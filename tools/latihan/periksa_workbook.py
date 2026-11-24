#!/usr/bin/env python3
"""Pemeriksa Workbook (data/soal-hsk1.json ... soal-hsk5.json).

Memeriksa bentuk tiap jenis soal, kunci jawaban, aksara per level, dan butir sulit (ciri "h": 1).
Pemeriksa ini melengkapi periksa.py (yang khusus data/latihan-*.json). Daftar aksara per level diambil dengan cara yang sama.

Pemakaian:  python3 tools/latihan/periksa_workbook.py            (semua level)
            python3 tools/latihan/periksa_workbook.py 2 4        (level tertentu)
Keluar dengan kode 1 bila ada galat. Butir bertanda "h": 1 diperiksa ketat (aksara di luar level = galat).
Butir lama hanya diberi peringatan untuk aksara di luar level, supaya data yang sudah tayang tidak tiba-tiba gagal.

Yang diperiksa:
  ting  s sama panjang dengan d, 2-4 opsi unik, kunci dalam jangkauan
  pan   kunci 0 atau 1
  xc    jumlah （n） di teks sama dengan jumlah pertanyaan; opsi unik; kunci dalam jangkauan
  pj px du dl  opsi unik, kunci dalam jangkauan, px memakai urutan ABC tetap (fix)
  jz    gabungan kepingan w tanpa tanda baca sama dengan kalimat z; urutan alternatif a juga sama hurufnya
  xh    tepat satu ＿ dan jawaban satu hanzi
  zj    kata w ada di contoh m
  semua tanpa tanda hubung panjang; hanzi di teks Mandarin harus ada di daftar level (butir sulit) atau nama diri
"""
import importlib.util
import json
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
spec = importlib.util.spec_from_file_location("periksa", os.path.join(ROOT, "tools", "latihan", "periksa.py"))
P = importlib.util.module_from_spec(spec)
spec.loader.exec_module(P)

HANZI = re.compile(r"[一-鿿]")
PUNCT = re.compile(r"[，。？！、；：“”‘’（）()\s,.?!;:\"'…·　]")
BLANK = re.compile(r"（\d+）")
EM = "\u2014"
WAJIB = {
    1: ["ting", "pan", "xc", "pj", "du"],
    2: ["ting", "pan", "xc", "pj", "du"],
    3: ["ting", "pan", "xc", "pj", "du", "jz", "xh"],
    4: ["ting", "pan", "xc", "px", "du", "jz", "zj"],
    5: ["ting", "du", "dl", "jz"],
}


# 男 dan 女 dipakai di pertanyaan "男的 / 女的" di semua level (juga di kertas ujian asli), jadi tidak dihitung sebagai aksara di luar level.
EXTRA = set("男女")


def hanzi_asing(teks, ok):
    return sorted({c for c in HANZI.findall(teks) if c not in ok and c not in P.NAMES and c not in EXTRA})


def periksa_level(n, ok_set, html):
    err, warn = [], []
    path = os.path.join(ROOT, "data", f"soal-hsk{n}.json")
    d = json.load(open(path, encoding="utf-8"))
    ok = ok_set[n]
    ringkas = {}

    def lapor(item, kunci, i, pesan, teks_mandarin=None):
        sulit = bool(item.get("h")) if isinstance(item, dict) else False
        tag = f"HSK{n} {kunci}[{i}]" + (" (sulit)" if sulit else "")
        err.append(f"{tag}: {pesan}") if sulit else warn.append(f"{tag}: {pesan}")

    def cek_aksara(item, kunci, i, *teks):
        asing = hanzi_asing("".join(t for t in teks if isinstance(t, str)), ok)
        if asing:
            sulit = bool(item.get("h"))
            (err if sulit else warn).append(f"HSK{n} {kunci}[{i}]{' (sulit)' if sulit else ''}: aksara di luar level {''.join(asing)}")

    def cek_opsi(item, kunci, i, o, a, min_o=2, maks_o=6):
        if not isinstance(o, list) or not (min_o <= len(o) <= maks_o):
            lapor(item, kunci, i, f"jumlah opsi {len(o) if isinstance(o, list) else '?'}")
            return
        if len(set(o)) != len(o):
            lapor(item, kunci, i, "opsi kembar")
        if not isinstance(a, int) or not (0 <= a < len(o)):
            lapor(item, kunci, i, f"kunci {a} di luar jangkauan")

    for kunci in WAJIB[n] + [k for k in ("dl",) if k not in WAJIB[n] and k in d]:
        arr = d.get(kunci)
        if not isinstance(arr, list) or not arr:
            err.append(f"HSK{n}: jenis {kunci} kosong atau tidak ada")
            continue
        sulit_n = 0
        for i, x in enumerate(arr):
            if x.get("h"):
                sulit_n += 1
            blob = json.dumps(x, ensure_ascii=False)
            if EM in blob:
                lapor(x, kunci, i, "ada tanda hubung panjang")
            if kunci == "ting":
                if not x.get("s") or len(x["s"]) != len(x["d"]):
                    lapor(x, kunci, i, "s tidak sama panjang dengan d")
                cek_opsi(x, kunci, i, x.get("o"), x.get("a"), 2, 4)
                cek_aksara(x, kunci, i, *x["d"], x["q"], *x["o"])
                if not x.get("tr") or not x.get("ex"):
                    lapor(x, kunci, i, "tr atau ex kosong")
            elif kunci == "pan":
                if x.get("a") not in (0, 1):
                    lapor(x, kunci, i, "kunci harus 0 atau 1")
                cek_aksara(x, kunci, i, *x["d"], x["q"])
                if not x.get("tr") or not x.get("ex"):
                    lapor(x, kunci, i, "tr atau ex kosong")
            elif kunci in ("xc", "pj", "px", "du", "dl"):
                qs = x.get("q") or []
                if kunci == "xc":
                    nb = len(BLANK.findall(x["t"]))
                    if nb != len(qs) or nb == 0:
                        lapor(x, kunci, i, f"lubang di teks {nb}, pertanyaan {len(qs)}")
                if kunci == "dl" and len(qs) < 2:
                    lapor(x, kunci, i, "bacaan panjang butuh 2 pertanyaan atau lebih")
                cek_aksara(x, kunci, i, x["t"], *[q["q"] for q in qs], *[o for q in qs for o in q["o"]])
                for j, q in enumerate(qs):
                    cek_opsi(x, f"{kunci}.q", f"{i}.{j}", q.get("o"), q.get("a"), 2, 4)
                    if not q.get("ex"):
                        lapor(x, kunci, i, f"q[{j}] tanpa ex")
                    if kunci == "px" and not q.get("fix"):
                        lapor(x, kunci, i, "px wajib fix:true")
                if not x.get("tr"):
                    lapor(x, kunci, i, "tr kosong")
            elif kunci == "jz":
                w, z = x.get("w") or [], x.get("z", "")
                if PUNCT.sub("", "".join(w)) != PUNCT.sub("", z):
                    lapor(x, kunci, i, "gabungan w tidak sama dengan z")
                if len(w) < 3:
                    lapor(x, kunci, i, "kepingan kurang dari 3")
                for alt in x.get("a") or []:
                    if isinstance(alt, str) and PUNCT.sub("", alt) != PUNCT.sub("", z) and sorted(PUNCT.sub("", alt)) != sorted(PUNCT.sub("", z)):
                        lapor(x, kunci, i, f"urutan alternatif {alt} beda huruf dari z")
                cek_aksara(x, kunci, i, z, *w)
                if not x.get("g") or not x.get("tr"):
                    lapor(x, kunci, i, "g atau tr kosong")
            elif kunci == "xh":
                if x["z"].count("＿") != 1:
                    lapor(x, kunci, i, "harus tepat satu ＿")
                if len(x.get("a", "")) != 1 or not HANZI.match(x.get("a", "")):
                    lapor(x, kunci, i, "jawaban harus satu hanzi")
                if not x.get("p"):
                    lapor(x, kunci, i, "pinyin petunjuk kosong")
                cek_aksara(x, kunci, i, x["z"], x["a"])
                if not x.get("tr") or not x.get("ex"):
                    lapor(x, kunci, i, "tr atau ex kosong")
            elif kunci == "zj":
                if x["w"] not in x["m"]:
                    lapor(x, kunci, i, "kata tidak ada di contoh m")
                cek_aksara(x, kunci, i, x["w"], x["m"])
                if not x.get("p") or not x.get("g") or not x.get("tr"):
                    lapor(x, kunci, i, "p, g, atau tr kosong")
        ringkas[kunci] = (len(arr), sulit_n)
    return err, warn, ringkas


def main():
    html = open(os.path.join(ROOT, "index.html"), encoding="utf-8").read()
    ok_set = P.kosakata(html)
    levels = [int(a) for a in sys.argv[1:]] or [1, 2, 3, 4, 5]
    semua_err = 0
    for n in levels:
        err, warn, ringkas = periksa_level(n, ok_set, html)
        total = sum(a for a, _ in ringkas.values())
        sulit = sum(b for _, b in ringkas.values())
        print(f"HSK {n}: {total} butir, {sulit} sulit | " + ", ".join(f"{k} {a}/{b}" for k, (a, b) in ringkas.items()))
        for e in err:
            print("  GALAT", e)
        for w in warn[:8]:
            print("  peringatan", w)
        if len(warn) > 8:
            print(f"  ... {len(warn) - 8} peringatan lain")
        semua_err += len(err)
    print("GALAT:", semua_err)
    sys.exit(1 if semua_err else 0)


if __name__ == "__main__":
    main()
