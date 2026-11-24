#!/usr/bin/env python3
"""Pemeriksa data/latihan-sulit.json (bank soal sulit buatan sendiri).

Jalankan dari akar repo:  python3 -I tools/latihan/periksa_sulit.py
Keluar dengan kode 1 bila ada GALAT. PERINGATAN tidak menggagalkan.

Yang dicek:
  g   kelompok 5 kata yang mudah tertukar (Arti kata, Pasangkan): kata ada di level itu, tanpa kembar, arti dan pinyin tidak sama
  is  isian kata: kata kunci ada di level itu, pengecoh ada di level itu atau di bawahnya, kata kunci muncul sekali di kalimat,
      pengecoh tidak muncul di kalimat, semua hanzi kalimat ada di kosakata sampai level itu
  pi  pinyin dan nada: pinyin benar sama dengan data situs, tiga pengecoh berbeda, ada penjelasan
  tu  buat kalimat: tiap kata wajib muncul di contoh jawaban dan di judul soal, contoh cukup panjang, hanzi sesuai level
  de  dengar dan pilih: kalimat soal adalah contoh milik satu kata di level itu dan punya rekaman, pengecoh hanya beda sedikit
Tanda pisah panjang (em dash) tidak boleh ada di berkas.
"""
import json
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
HANZI = re.compile(r"[一-鿿]")
EM = chr(0x2014)
KODE = {1: {1}, 2: {1, 2, 9}, 3: {1, 2, 3, 9}, 4: {1, 2, 3, 4, 9}, 5: {1, 2, 3, 4, 7, 9}, 6: {1, 2, 3, 4, 7, 8, 9}}
KODE_TEPAT = {1: 1, 2: 2, 3: 3, 4: 4, 5: 7, 6: 8}
JANGKAU = {"g": range(1, 7), "is": range(2, 7), "pi": range(1, 6), "tu": range(2, 7), "de": range(1, 5)}
NAMA_BERKAS = os.path.join(ROOT, "data", "latihan-sulit.json")

err, warn = [], []


def muat_situs():
    html = open(os.path.join(ROOT, "index.html"), encoding="utf-8").read()
    dec = json.JSONDecoder()
    i = html.index("const DATA=") + len("const DATA=")
    d, _ = dec.raw_decode(html[i:])
    j = html.index("const AU=") + len("const AU=")
    au, _ = dec.raw_decode(html[j:])
    return d["D"], au


D, AU = muat_situs()
AKSARA = {n: set("".join(r[0] for r in D if r[3] in k)) for n, k in KODE.items()}


def baris(w, n, rendah=False):
    ok = [r for r in D if r[0] == w and r[3] == KODE_TEPAT[n]]
    if ok or not rendah:
        return ok
    return [r for r in D if r[0] == w and r[3] in KODE[n] and r[3] != 9]


def hanzi_luar(teks, n, boleh=""):
    return sorted({c for c in HANZI.findall(teks) if c not in AKSARA[n] and c not in boleh})


def hitung(teks):
    return len(HANZI.findall(teks))


def jarak(a, b):
    """Jarak edit antar dua kalimat (per karakter)."""
    m, n = len(a), len(b)
    p = list(range(n + 1))
    for i in range(1, m + 1):
        q = [i] + [0] * n
        for j in range(1, n + 1):
            q[j] = min(p[j] + 1, q[j - 1] + 1, p[j - 1] + (a[i - 1] != b[j - 1]))
        p = q
    return p[n]


def cek_g(j):
    for ns, kel in j.items():
        n = int(ns)
        for gi, g in enumerate(kel):
            c = f"g{n}#{gi + 1}"
            if len(g) != 5 or len(set(g)) != 5:
                err.append(f"{c}: harus 5 kata berbeda ({g})")
                continue
            rows = []
            for w in g:
                r = baris(w, n)
                if not r:
                    err.append(f"{c}: '{w}' tidak ada di HSK {n}")
                else:
                    rows.append(r[0])
            if len(rows) == 5:
                if len({r[2] for r in rows}) != 5:
                    err.append(f"{c}: arti kembar di kelompok {g}")
                if len({r[1] for r in rows}) != 5:
                    err.append(f"{c}: pinyin kembar di kelompok {g}")


def cek_is(j):
    for ns, items in j.items():
        n = int(ns)
        seen = set()
        for i, h in enumerate(items):
            c = f"is{n}#{i + 1}"
            for f in ("k", "d", "z", "m"):
                if f not in h:
                    err.append(f"{c}: kolom '{f}' kosong")
            if any(f not in h for f in ("k", "d", "z", "m")):
                continue
            k, d, z, m = h["k"], h["d"], h["z"], h["m"]
            if z in seen:
                err.append(f"{c}: kalimat kembar")
            seen.add(z)
            if not baris(k, n):
                err.append(f"{c}: kata kunci '{k}' tidak ada di HSK {n}")
            if len(d) != 3 or len(set(d)) != 3 or k in d:
                err.append(f"{c}: butuh 3 pengecoh berbeda dan bukan kata kunci ({d})")
            for w in d:
                if not baris(w, n, True):
                    err.append(f"{c}: pengecoh '{w}' tidak ada di HSK 1 sampai {n}")
                if w in z:
                    err.append(f"{c}: pengecoh '{w}' muncul di kalimat")
            if z.count(k) != 1:
                err.append(f"{c}: '{k}' harus muncul tepat sekali di kalimat (sekarang {z.count(k)})")
            if not re.search(r"[。？！]$", z):
                err.append(f"{c}: kalimat tidak diakhiri tanda baca")
            luar = hanzi_luar(z, n)
            if luar:
                err.append(f"{c}: hanzi di atas HSK {n}: {''.join(luar)}")
            if hitung(z) < 6:
                warn.append(f"{c}: kalimat pendek ({hitung(z)} hanzi)")
            if len(m) < 30:
                err.append(f"{c}: penjelasan terlalu pendek")


def cek_pi(j):
    for ns, items in j.items():
        n = int(ns)
        for i, h in enumerate(items):
            c = f"pi{n}#{i + 1}"
            if len(h) != 3 or len(h[1]) != 3:
                err.append(f"{c}: bentuk harus [kata, [3 pengecoh], penjelasan]")
                continue
            w, wrong, m = h
            rows = baris(w, n)
            if not rows:
                err.append(f"{c}: '{w}' tidak ada di HSK {n}")
                continue
            if len(rows) > 1:
                warn.append(f"{c}: '{w}' punya {len(rows)} baris di level ini, soal memakai baris pertama")
            benar = rows[0][1]
            if benar in wrong:
                err.append(f"{c}: pengecoh sama dengan pinyin benar '{benar}'")
            if len(set(wrong)) != 3:
                err.append(f"{c}: pengecoh kembar {wrong}")
            if any(len(x.split()) != len(benar.split()) for x in wrong):
                warn.append(f"{c}: jumlah spasi pengecoh beda dengan '{benar}'")
            if len(m) < 30:
                err.append(f"{c}: penjelasan terlalu pendek")
            if not any(ch in m for ch in w) and benar not in m:
                warn.append(f"{c}: penjelasan tidak menyebut kata atau pinyinnya")


def cek_tu(j):
    for ns, items in j.items():
        n = int(ns)
        for i, h in enumerate(items):
            c = f"tu{n}#{i + 1}"
            for f in ("w", "py", "m", "sc", "need", "ex"):
                if f not in h:
                    err.append(f"{c}: kolom '{f}' kosong")
            if any(f not in h for f in ("w", "py", "m", "sc", "need", "ex")):
                continue
            ex = h["ex"]
            for t in h["need"]:
                if t not in ex:
                    err.append(f"{c}: contoh jawaban tidak memuat '{t}'")
                if t not in h["w"]:
                    err.append(f"{c}: judul soal tidak menampilkan '{t}'")
            if hitung(ex) < 8:
                err.append(f"{c}: contoh jawaban kurang dari 8 hanzi (aturan Periksa meminta 8)")
            if not re.search(r"[。？！]$", ex):
                err.append(f"{c}: contoh tidak diakhiri tanda baca")
            luar = hanzi_luar(ex, n)
            if luar:
                err.append(f"{c}: hanzi contoh di atas HSK {n}: {''.join(luar)}")
            if re.search(r"[A-Za-z]", ex):
                err.append(f"{c}: contoh memuat huruf Latin")


def cek_de(j):
    for ns, items in j.items():
        n = int(ns)
        for i, h in enumerate(items):
            c = f"de{n}#{i + 1}"
            s, d = h.get("s"), h.get("d")
            if not s or not d or len(d) != 3:
                err.append(f"{c}: butuh 's' dan 3 pengecoh 'd'")
                continue
            if not any(r[3] == KODE_TEPAT[n] and r[5] == s for r in D):
                err.append(f"{c}: kalimat bukan contoh milik kata HSK {n}: {s}")
            if s not in AU:
                err.append(f"{c}: kalimat tidak punya rekaman: {s}")
            if len(set(d)) != 3 or s in d:
                err.append(f"{c}: pengecoh kembar atau sama dengan soal")
            for x in d:
                luar = hanzi_luar(x, n, s)
                if luar:
                    err.append(f"{c}: pengecoh memuat hanzi di atas HSK {n}: {''.join(luar)}")
                dj = jarak(s, x)
                if dj > 4:
                    warn.append(f"{c}: pengecoh terlalu jauh dari soal (jarak {dj}): {x}")
                if abs(len(x) - len(s)) > 3:
                    err.append(f"{c}: panjang pengecoh beda jauh: {x}")
                if x[-1] != s[-1]:
                    warn.append(f"{c}: tanda baca akhir pengecoh beda: {x}")


def main():
    raw = open(NAMA_BERKAS, encoding="utf-8").read()
    if EM in raw:
        err.append("berkas memuat tanda pisah panjang (em dash)")
    j = json.loads(raw)
    for k in j:
        if k not in JANGKAU:
            err.append(f"kunci tak dikenal: {k}")
        for ns in j[k]:
            if int(ns) not in JANGKAU[k]:
                err.append(f"{k}: level {ns} tidak punya menu latihan, data tidak akan terpakai")
    cek_g(j.get("g", {}))
    cek_is(j.get("is", {}))
    cek_pi(j.get("pi", {}))
    cek_tu(j.get("tu", {}))
    cek_de(j.get("de", {}))
    tot = {k: sum(len(v) for v in j[k].values()) for k in j}
    print("Jumlah per jenis:", tot)
    for w in warn:
        print("PERINGATAN", w)
    for e in err:
        print("GALAT", e)
    print(f"GALAT {len(err)}, PERINGATAN {len(warn)}")
    return 1 if err else 0


if __name__ == "__main__":
    sys.exit(main())
