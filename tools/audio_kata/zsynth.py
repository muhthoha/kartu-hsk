"""Sintesis kata Mandarin dari pinyin dengan model MeloTTS (MIT) lewat onnxruntime.

Bacaan ditentukan oleh pinyin (bukan ditebak dari hanzi), jadi kata berbacaan ganda (还 hái/huán) selalu benar.
"""
import os
import re
import subprocess

import numpy as np

import zpinyin as zp

SR = 44100


class Lexicon:
    def __init__(self, model_dir):
        self.tok = {}
        with open(os.path.join(model_dir, "tokens.txt"), encoding="utf-8") as f:
            for line in f:
                a = line.rstrip("\n").split(" ")
                if len(a) == 2:
                    self.tok[a[0]] = int(a[1])
        self.words = {}
        with open(os.path.join(model_dir, "lexicon.txt"), encoding="utf-8") as f:
            for line in f:
                a = line.split()
                if len(a) < 3 or (len(a) - 1) % 2:
                    continue
                n = (len(a) - 1) // 2
                self.words[a[0]] = (a[1:1 + n], [int(x) for x in a[1 + n:]])
        # nada bawaan tiap hanzi (dari entri satu karakter) dan pasangan fonem yang sah
        self.char_tone = {}
        self.char_ph = {}
        self.pairs = set()
        for w, (ph, tn) in self.words.items():
            if len(w) == 1 and "㐀" <= w <= "鿿" and len(ph) == 2:
                self.char_tone[w] = tn[0]
                self.char_ph[w] = (ph[0], ph[1])
                self.pairs.add((ph[0], ph[1]))

        # frekuensi kata jieba, untuk menebak susunan dalam kata (展览|馆, 小|老虎) saat menerapkan sandhi
        self.freq = {}
        jp = os.path.join(model_dir, "dict", "jieba.dict.utf8")
        if os.path.exists(jp):
            with open(jp, encoding="utf-8") as f:
                for line in f:
                    a = line.split(" ")
                    if len(a) >= 2 and a[1].isdigit():
                        self.freq[a[0]] = int(a[1])
        self.total = float(sum(self.freq.values()) or 1)


def _subwords(hanzi, lex):
    """Pecah kata >= 3 hanzi menjadi sub-kata (peluang terbesar menurut frekuensi jieba, tiap bagian < seluruh kata).

    Mengembalikan daftar panjang sub-kata. Bila hasilnya hanya karakter lepas, kata dianggap satu kesatuan."""
    import math
    n = len(hanzi)
    if n < 3:
        return [n]
    best = [(-1e18, [])] * (n + 1)
    best[0] = (0.0, [])
    for i in range(n):
        if best[i][0] <= -1e17:
            continue
        for L in range(1, min(4, n - i, n - 1) + 1):
            w = hanzi[i:i + L]
            f = lex.freq.get(w)
            if f is None:
                if L > 1:
                    continue
                f = 1
            sc = best[i][0] + math.log(f / lex.total)
            if sc > best[i + L][0]:
                best[i + L] = (sc, best[i][1] + [L])
    out = best[n][1]
    if not out or all(L == 1 for L in out):
        return [n]
    return out


def surface_tones(chunks, hanzi, lex, pos=""):
    """Terapkan sandhi nada ketiga pada daftar potongan dari zpinyin.parse. Mengembalikan daftar item:
    ('syl', suku, nada_permukaan) / ('r',) / ('pause', tanda)."""
    han = re.findall(r"[㐀-鿿]", hanzi or "")
    n_syl = sum(len(v) for k, v in chunks if k == "syl")
    aligned = len(han) == n_syl and not any(k == "pause" for k, v in chunks)
    items = []          # [kind, syl, tone, hanzi, unit_id]
    unit = 0
    hi = 0
    for k, v in chunks:
        if k == "pause":
            items.append(["pause", v, 0, "", -1])
            unit += 1
            continue
        hz = "".join(han[hi:hi + len(v)]) if aligned else ""
        sub = _subwords(hz, lex) if hz and len(v) >= 3 else [len(v)]
        j = 0
        for L in sub:
            for s, t in v[j:j + L]:
                items.append(["syl", s, t, han[hi] if aligned else "", unit])
                hi += 1
            j += L
            unit += 1
    # nada dasar untuk sandhi: suku netral yang hanzi-nya bernada 3 dianggap 3 hanya pada pola yang memang memicu sandhi
    syl_ix = [i for i, it in enumerate(items) if it[0] == "syl" and it[1] != "r"]
    base = {i: items[i][2] for i in syl_ix}
    for a, b in zip(syl_ix, syl_ix[1:]):
        if items[a][2] == 3 and items[b][2] == 5 and items[b][3] and lex.char_tone.get(items[b][3]) == 3:
            ha, hb = items[a][3], items[b][3]
            if hb == "子":
                continue
            if ha == hb and "v" not in pos.split(","):
                continue                       # 姐姐, 奶奶: tidak berubah; 想想, 走走 (verba): berubah
            base[b] = 3
    surf = dict(base)
    # kanan ke kiri: nada 3 sebelum nada 3 (permukaan) menjadi 2, kecuali ada jeda di antaranya
    for a, b in reversed(list(zip(syl_ix, syl_ix[1:]))):
        if any(items[x][0] == "pause" for x in range(a + 1, b)):
            continue
        if base[a] == 3 and base[b] == 3:
            same_unit = items[a][4] == items[b][4]
            if same_unit or surf[b] == 3:
                surf[a] = 2
    out = []
    for i, it in enumerate(items):
        if it[0] == "pause":
            out.append(("pause", it[1]))
        elif it[1] == "r":
            out.append(("r",))
        else:
            out.append(("syl", it[1], surf[i] if items[i][2] != 5 else 5))
    return out


def to_ids(items, lex, erhua_tone=2):
    """-> (x, tones, fonem, nada, spans). spans[i] = (awal, akhir) indeks fonem milik items[i] dalam daftar fonem."""
    ph, tn, spans = ["_"], [0], []
    for it in items:
        a0 = len(ph)
        if it[0] == "pause":
            ph.append(it[1])
            tn.append(0)
        elif it[0] == "r":
            ph += ["EE", "er"]
            tn += [erhua_tone, erhua_tone]
        elif it[0] == "raw":
            ph += it[1]
            tn += it[2]
        else:
            a, b = zp.syl2ph(it[1])
            ph += [a, b]
            tn += [it[2], it[2]]
        spans.append((a0, len(ph)))
    ph.append("_")
    tn.append(0)
    ids = [lex.tok[p] for p in ph]
    x, t = [0], [0]
    for i, tt in zip(ids, tn):
        x += [i, 0]
        t += [tt, 0]
    return np.array([x], dtype=np.int64), np.array([t], dtype=np.int64), ph, tn, spans


def g2p(hanzi, pinyin, lex, pos=""):
    """(hanzi, pinyin situs) -> item fonem siap sintesis. Huruf Latin tunggal/kata Inggris diambil dari leksikon."""
    p = zp._norm(pinyin)
    # token Latin yang bukan pinyin (mis. "X" pada X光机)
    try:
        chunks = zp.parse(pinyin, hanzi)
    except zp.PinyinError:
        toks = p.split()
        items = []
        for tk in toks:
            try:
                c = zp.parse(tk)
                items += surface_tones(c, None, lex, pos)
            except zp.PinyinError:
                w = re.sub(r"[^a-z]", "", tk)
                if w and w in lex.words:
                    items.append(("raw", list(lex.words[w][0]), list(lex.words[w][1])))
                else:
                    raise
        return items
    return surface_tones(chunks, hanzi, lex, pos)


HOP = 512


class Synth:
    """MeloTTS ONNX dengan keluaran durasi per token, supaya satu kata bisa dipotong tepat dari dalam konteks."""

    def __init__(self, model_dir, threads=2):
        import onnxruntime as ort
        import zonnx
        so = ort.SessionOptions()
        so.intra_op_num_threads = threads
        so.inter_op_num_threads = 1
        self.lex = Lexicon(model_dir)
        src = os.path.join(model_dir, "model.onnx")
        dur = os.path.join(os.path.dirname(os.path.abspath(model_dir)), "model_dur.onnx")
        if not os.path.exists(dur):
            with open(src, "rb") as f:
                b = f.read()
            with open(dur, "wb") as f:
                f.write(zonnx.add_outputs(b, ["/Ceil_output_0"]))
        self.sess = ort.InferenceSession(dur, so, providers=["CPUExecutionProvider"])

    def run(self, x, tones, noise=0.6, length=1.0, noise_w=0.8, sid=1):
        y, d = self.sess.run(None, {
            "x": x, "x_lengths": np.array([x.shape[1]], dtype=np.int64), "tones": tones,
            "sid": np.array([sid], dtype=np.int64),
            "noise_scale": np.array([noise], dtype=np.float32),
            "length_scale": np.array([length], dtype=np.float32),
            "noise_scale_w": np.array([noise_w], dtype=np.float32)})
        return y.reshape(-1).astype(np.float32), d.reshape(-1).astype(np.int64)

    def word(self, hanzi, pinyin, pos="", seed=0, mode="x,X.", noise=0.4, noise_w=0.6, length=1.2):
        """Sintesis satu kata. mode menentukan konteks dan salinan mana yang diambil (huruf besar):
        "X" = kata sendirian, "x,X." = diucapkan dua kali lalu diambil yang kedua, "X,x." yang pertama, "x,X,x." yang tengah."""
        items = g2p(hanzi, pinyin, self.lex, pos)
        seq, take, n = [], None, len(items)
        for ch in mode:
            if ch in "xX":
                if ch == "X":
                    take = len(seq)
                seq += items
            else:
                seq.append(("pause", ch))
        x, t, ph, tn, spans = to_ids(seq, self.lex)
        np.random.seed(seed)
        y, d = self.run(x, t, noise=noise, noise_w=noise_w, length=length)
        if mode == "X":
            return y, ph, tn
        a, b = spans[take][0], spans[take + n - 1][1]
        cum = np.concatenate([[0], np.cumsum(d)])
        s0, s1 = int(cum[2 * a]) * HOP, int(cum[min(2 * b + 1, len(d))]) * HOP
        return y[s0:s1], ph[a:b], tn[a:b]


def trim(y, sr=SR, thr_db=-42.0, pad_start=0.03, pad_end=0.09):
    """Buang hening di awal/akhir, sisakan sedikit ruang, beri fade halus, samakan kenyaringan."""
    if len(y) == 0:
        return y
    win = int(sr * 0.01)
    n = len(y) // win
    if n < 3:
        return y
    e = np.sqrt((y[:n * win].reshape(n, win) ** 2).mean(axis=1) + 1e-12)
    ref = np.percentile(e, 95)
    thr = ref * (10 ** (thr_db / 20))
    on = np.where(e > max(thr, 1e-4))[0]
    if len(on) == 0:
        return y
    a = max(0, on[0] * win - int(pad_start * sr))
    b = min(len(y), (on[-1] + 1) * win + int(pad_end * sr))
    y = y[a:b].copy()
    f_in, f_out = min(int(0.008 * sr), len(y) // 4), min(int(0.04 * sr), len(y) // 4)
    if f_in > 0:
        y[:f_in] *= np.linspace(0, 1, f_in)
    if f_out > 0:
        y[-f_out:] *= np.linspace(1, 0, f_out)
    # kenyaringan: RMS bagian bersuara ke -20 dBFS, puncak dibatasi -1 dBFS
    v = y[np.abs(y) > 0.02 * np.abs(y).max()]
    rms = np.sqrt((v ** 2).mean()) if len(v) else 0
    if rms > 0:
        y = y * (10 ** (-20 / 20) / rms)
    pk = np.abs(y).max()
    lim = 10 ** (-1 / 20)
    if pk > lim:
        y = y * (lim / pk)
    return y


def write_wav(path, y, sr=SR):
    import wave
    with wave.open(path, "wb") as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(sr)
        w.writeframes((np.clip(y, -1, 1) * 32767).astype("<i2").tobytes())


def to_mp3(y, path, sr=SR, out_sr=22050, bitrate="40k"):
    pcm = (np.clip(y, -1, 1) * 32767).astype("<i2").tobytes()
    r = subprocess.run(["ffmpeg", "-hide_banner", "-loglevel", "error", "-y", "-f", "s16le", "-ar", str(sr), "-ac", "1", "-i", "-",
                        "-ar", str(out_sr), "-ac", "1", "-c:a", "libmp3lame", "-b:a", bitrate, "-map_metadata", "-1",
                        "-write_xing", "0", "-id3v2_version", "0", path], input=pcm, capture_output=True)
    if r.returncode:
        raise RuntimeError(r.stderr.decode()[:300])
