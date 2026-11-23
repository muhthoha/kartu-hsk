#!/usr/bin/env python3
"""MP3 untuk kalimat contoh, memakai mesin yang sama dengan buat_audio_kata.py (MeloTTS + pemeriksa SenseVoice).

  python3 pinyin_kalimat.py --data hsk3-penuh.json --model <vits-melo-tts-zh_en> --keluar kalimat.json --tinjau tinjau.csv
  python3 buat_audio_kalimat.py --daftar kalimat.json --model <vits-melo-tts-zh_en> --asr <SenseVoice int8> \
      --keluar ../../audio/kalimat [--bagian 0 --dari 2] [--batas 50]

--daftar : keluaran pinyin_kalimat.py. Bila ada kolom "p2" (pinyin yang sudah dikoreksi manusia), itu yang dipakai.
Nama berkas = kah("s|" + hanzi kalimat) + ".mp3". Kuncinya HANYA hanzi kalimat, sehingga situs tidak perlu pinyin kalimat
(situs tidak menyimpannya). Kalimat yang sama untuk dua kata hanya dibuat sekali.
Hasil pemeriksaan tiap kalimat ditulis ke <keluar>/../kalimat-hasil-<bagian>.jsonl; proses dapat dilanjutkan.
Setelah semua bagian selesai:  python3 buat_audio_kalimat.py --keluar ../../audio/kalimat --indeks
"""
import argparse
import json
import os
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import kah
import zsynth as zs
from buat_audio_kata import Pembuat


def kunci(h):
    return kah.kah("s|" + h)


def tulis_indeks(keluar):
    """index.json = daftar kode berkas yang ada (tanpa hanzi). Situs memakainya untuk tahu kalimat mana yang punya MP3.
    Jalankan sekali setelah semua --bagian selesai, lalu naikkan angka ?v= di index.html (h3Load) agar peramban memuat ulang."""
    ks = sorted(f[:-4] for f in os.listdir(keluar) if f.endswith(".mp3"))
    with open(os.path.join(keluar, "index.json"), "w", encoding="utf-8") as f:
        json.dump(ks, f, separators=(",", ":"))
    print("indeks:", len(ks), "berkas")


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--daftar")
    ap.add_argument("--model")
    ap.add_argument("--asr")
    ap.add_argument("--keluar", required=True)
    ap.add_argument("--bagian", type=int, default=0)
    ap.add_argument("--dari", type=int, default=1)
    ap.add_argument("--batas", type=int, default=None)
    ap.add_argument("--indeks", action="store_true", help="hanya tulis <keluar>/index.json dari berkas yang ada, lalu selesai")
    a = ap.parse_args()
    if a.indeks:
        tulis_indeks(a.keluar)
        return
    if not (a.daftar and a.model and a.asr):
        ap.error("--daftar, --model, dan --asr wajib (kecuali --indeks)")
    items, seen = [], set()
    for x in json.load(open(a.daftar, encoding="utf-8")):
        if x["h"] in seen:
            continue
        seen.add(x["h"])
        items.append((x["h"], x.get("p2") or x["p"]))
    os.makedirs(a.keluar, exist_ok=True)
    resf = os.path.join(os.path.dirname(os.path.abspath(a.keluar)), f"kalimat-hasil-{a.bagian}.jsonl")
    done = set()
    if os.path.exists(resf):
        for l in open(resf, encoding="utf-8"):
            try:
                done.add(json.loads(l)["h"])
            except Exception:
                pass
    P = Pembuat(a.model, a.asr)
    n = 0
    with open(resf, "a", encoding="utf-8") as fo:
        for i, (h, p) in enumerate(items):
            tujuan = os.path.join(a.keluar, kunci(h) + ".mp3")
            if i % a.dari != a.bagian or h in done or os.path.exists(tujuan):
                continue
            if a.batas is not None and n >= a.batas:
                break
            t0 = time.time()
            try:
                y, info = P.satu(h, p)
                zs.to_mp3(y, tujuan)
                rec = dict(h=h, p=p, ok=True, dur=round(len(y) / zs.SR, 2), info=info)
            except Exception as e:
                rec = dict(h=h, p=p, ok=False, err=f"{type(e).__name__}: {e}"[:200])
            rec["sec"] = round(time.time() - t0, 2)
            fo.write(json.dumps(rec, ensure_ascii=False) + "\n")
            fo.flush()
            n += 1
    print("selesai", a.bagian, n)


if __name__ == "__main__":
    main()
