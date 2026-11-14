#!/usr/bin/env python3
"""Membuat MP3 untuk setiap kata (hanzi + pinyin) dengan model MeloTTS zh_en (lisensi MIT) lewat onnxruntime.

  python3 buat_audio_kata.py --daftar kata.json --model <folder vits-melo-tts-zh_en> --asr <folder SenseVoice int8> \
      --keluar ../../audio/kata [--bagian 0 --dari 2] [--batas 50]

--daftar : JSON berisi [[hanzi, pinyin], ...]  (kata dengan dua bacaan ditulis "cháng / zhǎng"; kata yang sama tidak diulang)
Nama berkas = kah(hanzi + "|" + pinyin) + ".mp3" (lihat kah.py; harus sama dengan kaH() di index.html), jadi situs tidak
perlu daftar kata di berkas publik. Hasil pemeriksaan tiap kata ditulis ke <keluar>/../kata-hasil-<bagian>.jsonl (di luar repo
bila ingin dirahasiakan) dan dapat dilanjutkan bila proses terhenti.

Cara kerja: bacaan ditentukan dari PINYIN situs (bukan ditebak dari hanzi), kata diucapkan dalam konteks ("kata, kata.")
lalu salinan yang tepat dipotong memakai durasi per token dari model; hasil dikenali ulang dengan SenseVoice dan dibandingkan
dengan pinyin; kandidat lain (mode/seed berbeda) dicoba bila tidak cocok. Nada 1 dan 4 pada kata satu suku juga diperiksa lewat F0.
"""
import argparse, json, os, re, sys, time
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import numpy as np
import kah, zasr, zeval, zf0, zsynth as zs

CANDS = [("x,X,x.", 0), ("X!x.", 0), ("X,x.", 0), ("x,X.", 0), ("x,X,x.", 1), ("X!x.", 1), ("X,x.", 1)]
SENT = [("X", 0), ("X", 1), ("X", 2)]


def tone_ok(y, exp):
    if len(exp) != 1 or exp[0][2] not in (1, 4):
        return True
    c = zf0.contour(y, zs.SR)
    if c is None:
        return True
    a, e = c[0], c[2]
    return abs(e - a) < 3.0 if exp[0][2] == 1 else (a - e) > 1.5


def readings(h, p):
    if " / " in p:
        ps = p.split(" / ")
        hs = h.split(" / ") if " / " in h else [h] * len(ps)
        if len(hs) == len(ps):
            return list(zip(hs, ps))
    return [(h, p)]


class Pembuat:
    def __init__(self, model, asr):
        self.S = zs.Synth(model, threads=1)
        self.A = zasr.ASR(asr, threads=1)
        self.rd, self.rt = zeval.build_readings(self.S.lex)

    def satu(self, h, p):
        sent = len(h) > 8 or bool(re.search(r'[，。？！、：；“”"\-A-Za-z0-9]', h))
        p = re.sub(r"(?<![A-Za-z])([A-Z])(?![A-Za-z])", lambda m: m.group(1).lower(), p)
        try:
            exp = zeval.expected(h, p)
        except Exception:
            exp = None
        best = None
        for mode, seed in (SENT if sent else CANDS):
            y, _, _ = self.S.word(h, p, mode=mode, seed=seed)
            y = zs.trim(y)
            if len(y) < zs.SR * 0.12:
                continue
            txt = self.A.text(y, zs.SR)
            if exp is None:
                best = (3, y, dict(mode=mode, seed=seed, asr=txt, s=None, t=None))
                break
            s_ok, _ = zeval.compare(exp, txt, self.rd, self.rt)
            tk = tone_ok(y, exp)
            sc = 2 * int(s_ok) + int(tk)
            if best is None or sc > best[0]:
                best = (sc, y, dict(mode=mode, seed=seed, asr=txt, s=bool(s_ok), t=bool(tk)))
            if sc == 3:
                break
        if best is None:
            raise RuntimeError("semua kandidat terlalu pendek")
        return best[1], best[2]

    def kata(self, h, p):
        ys, infos = [], []
        for hh, pp in readings(h, p):
            y, inf = self.satu(hh, pp)
            ys.append(y); infos.append(inf)
        if len(ys) == 1:
            return ys[0], infos
        gap = np.zeros(int(0.45 * zs.SR), np.float32)
        out = []
        for k, y in enumerate(ys):
            out.append(y)
            if k < len(ys) - 1:
                out.append(gap)
        return np.concatenate(out), infos


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--daftar", required=True); ap.add_argument("--model", required=True); ap.add_argument("--asr", required=True)
    ap.add_argument("--keluar", required=True); ap.add_argument("--bagian", type=int, default=0); ap.add_argument("--dari", type=int, default=1)
    ap.add_argument("--batas", type=int, default=None)
    a = ap.parse_args()
    items = sorted({(h, p) for h, p in json.load(open(a.daftar, encoding="utf-8"))})
    os.makedirs(a.keluar, exist_ok=True)
    resf = os.path.join(os.path.dirname(os.path.abspath(a.keluar)), f"kata-hasil-{a.bagian}.jsonl")
    done = set()
    if os.path.exists(resf):
        for l in open(resf, encoding="utf-8"):
            try:
                done.add(json.loads(l)["k"])
            except Exception:
                pass
    P = Pembuat(a.model, a.asr)
    n = 0
    with open(resf, "a", encoding="utf-8") as fo:
        for i, (h, p) in enumerate(items):
            key = h + "|" + p
            if i % a.dari != a.bagian or key in done or os.path.exists(os.path.join(a.keluar, kah.kah(key) + ".mp3")):
                continue
            if a.batas is not None and n >= a.batas:
                break
            t0 = time.time()
            try:
                y, infos = P.kata(h, p)
                zs.to_mp3(y, os.path.join(a.keluar, kah.kah(key) + ".mp3"))
                rec = dict(k=key, ok=True, dur=round(len(y) / zs.SR, 2), info=infos)
            except Exception as e:
                rec = dict(k=key, ok=False, err=f"{type(e).__name__}: {e}"[:200])
            rec["sec"] = round(time.time() - t0, 2)
            fo.write(json.dumps(rec, ensure_ascii=False) + "\n"); fo.flush(); n += 1
    print("selesai", a.bagian, n)


if __name__ == "__main__":
    main()
