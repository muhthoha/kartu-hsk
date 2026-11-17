#!/usr/bin/env python3
"""Ambil kunci jawaban dari halaman "卷答案" PDF kertas ujian HSK (2.0) resmi.

Pemakaian:
    python3 kunci_ujian.py H41001.pdf [H41002.pdf ...]

Hanya huruf/tanda kunci yang diambil (satu karakter per nomor). Teks soal,
naskah 听力, dan kalimat contoh 书写 tidak disalin.
Format satu karakter per nomor:
    T / X  = benar (√) / salah (×)
    A..F   = pilihan
    1..6   = urutan kalimat HSK 4 no. 56-65 (ABC ACB BAC BCA CAB CBA)
    hanzi  = HSK 3 no. 76-80 (satu karakter)
    -      = dinilai sendiri (书写)
Butuh `pdftotext` (poppler-utils).
"""
import re
import subprocess
import sys

ORD = ["ABC", "ACB", "BAC", "BCA", "CAB", "CBA"]
# (awal, akhir, jenis)
SPEC = {
    1: [(1, 5, "tf"), (6, 10, "abc"), (11, 15, "af"), (16, 20, "abc"),
        (21, 25, "tf"), (26, 40, "af")],
    2: [(1, 10, "tf"), (11, 20, "af"), (21, 35, "abc"),
        (36, 45, "af"), (46, 50, "tf"), (51, 60, "af")],
    3: [(1, 10, "af"), (11, 20, "tf"), (21, 40, "abc"),
        (41, 60, "af"), (61, 70, "abc"), (71, 75, "self"), (76, 80, "han")],
    4: [(1, 10, "tf"), (11, 45, "abcd"), (46, 55, "af"), (56, 65, "ord"),
        (66, 85, "abcd"), (86, 100, "self")],
    5: [(1, 90, "abcd"), (91, 100, "self")],
}
OK = {"tf": "TX", "abc": "ABC", "abcd": "ABCD", "af": "ABCDEF", "ord": "123456"}


def jenis(level, n):
    for a, b, j in SPEC[level]:
        if a <= n <= b:
            return j
    raise ValueError(n)


def total(level):
    return SPEC[level][-1][1]


def dari_teks(teks, level):
    """Kembalikan (kunci, masalah). teks = isi PDF dari pdftotext -layout."""
    pos = [m.start() for m in re.finditer(r"卷\s*答\s*案", teks)]
    if not pos:
        return None, ["tidak ada halaman 卷答案"]
    t = teks[pos[-1]:]
    t = t.replace("．", ".").replace("。", ".")
    t = t.replace("√", "T").replace("✓", "T").replace("✔", "T")
    t = t.replace("×", "X").replace("✕", "X").replace("✗", "X")
    n_tot = total(level)
    kunci = {}
    for m in re.finditer(r"(?<![\d])(\d{1,3})\s*\.\s*([A-Za-z一-鿿]+)", t):
        n = int(m.group(1))
        if not 1 <= n <= n_tot or n in kunci:
            continue
        v = m.group(2)
        j = jenis(level, n)
        if j == "self":
            kunci[n] = "-"
        elif j == "han":
            kunci[n] = v[0] if "一" <= v[0] <= "鿿" else "?"
        elif j == "ord":
            v = v.upper()
            kunci[n] = str(ORD.index(v) + 1) if v in ORD else "?"
        else:
            v = v.upper()
            kunci[n] = v[0] if len(v) == 1 and v in OK[j] else "?"
    masalah = []
    out = []
    for n in range(1, n_tot + 1):
        j = jenis(level, n)
        c = kunci.get(n)
        if j == "self":
            c = "-"
        if c is None:
            masalah.append("no. %d tidak ditemukan" % n)
            c = "?"
        elif c == "?":
            masalah.append("no. %d tidak terbaca" % n)
        out.append(c)
    return "".join(out), masalah


def dari_pdf(path, level=None):
    teks = subprocess.run(["pdftotext", "-layout", path, "-"], capture_output=True,
                          text=True, errors="replace").stdout
    if level is None:
        m = re.search(r"H([1-5])\d{4}", teks) or re.search(r"H([1-5])\d{4}", path)
        if not m:
            return None, ["level tidak dikenali"], None
        level = int(m.group(1))
    k, mas = dari_teks(teks, level)
    return k, mas, level


if __name__ == "__main__":
    for p in sys.argv[1:]:
        k, mas, lv = dari_pdf(p)
        kode = re.search(r"H\d{5}[A-D]?", p.upper().replace(" ", ""))
        print("%s\t%s\t%s\t%s" % (kode.group(0) if kode else p, lv, k, "; ".join(mas) or "ok"))
