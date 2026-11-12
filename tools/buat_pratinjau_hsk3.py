#!/usr/bin/env python3
"""Membuat data/hsk3.json (pratinjau HSK 3.0) dari berkas kosakata penuh.

Berkas penuh (3.600 kata) TIDAK disimpan di repo ini karena repo bersifat publik; isi penuh
dilayani server n8n (tabel hsk_isi, paket h3) hanya untuk pelanggan. Yang masuk repo hanya
pratinjau: Set 1 (50 kata pertama) tiap level, jumlah kata per level, dan daftar hanzi
yang punya lebih dari satu bacaan (supaya aturan audio kata tetap benar di pratinjau).

Pakai:
  python3 tools/buat_pratinjau_hsk3.py --data /jalur/hsk3-penuh.json --keluar data/hsk3.json

Bentuk berkas penuh : {"v":1,"D":[[hanzi,pinyin,arti,level,set,contoh,kelas], ...]}  (3.600 baris, urutan tetap)
Bentuk pratinjau    : {"v":2,"n":3600,"lv":{"1":300,...},"dup":[...],"D":[[...7 kolom..., nomor_urut], ...]}
Nomor urut (0..3599) adalah kunci progres (hsk_m3) dan nama berkas audio, jadi urutan berkas penuh tidak boleh berubah.
"""
import argparse
import json
import os
import sys

SET_GRATIS = 1      # set yang dibuka untuk semua akun
PER_SET = 50


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--data", required=True, help="berkas kosakata penuh (di luar repo)")
    ap.add_argument("--keluar", default="data/hsk3.json", help="berkas pratinjau yang ditulis")
    a = ap.parse_args()

    with open(a.data, encoding="utf-8") as f:
        penuh = json.load(f)
    rows = penuh["D"]
    if not isinstance(rows, list) or not rows:
        sys.exit("berkas penuh kosong atau bentuknya salah")

    lama = {}
    if os.path.exists(a.keluar):
        try:
            with open(a.keluar, encoding="utf-8") as f:
                lama = json.load(f)
        except Exception:
            lama = {}

    lv, baca, pratinjau = {}, {}, []
    for i, r in enumerate(rows):
        if len(r) < 7 or not (1 <= r[3] <= 5) or not isinstance(r[4], int):
            sys.exit(f"baris {i} tidak sesuai: {r!r}")
        lv[str(r[3])] = lv.get(str(r[3]), 0) + 1
        baca.setdefault(r[0], set()).add(r[1])
        if r[4] == SET_GRATIS:
            pratinjau.append(list(r[:7]) + [i])
    for k, n in lv.items():
        ada = sum(1 for r in pratinjau if str(r[3]) == k)
        if ada != min(PER_SET, n):
            sys.exit(f"level {k}: pratinjau berisi {ada} kata, seharusnya {min(PER_SET, n)}")

    out = {"v": 2, "n": len(rows), "lv": dict(sorted(lv.items())),
           "dup": sorted(h for h, s in baca.items() if len(s) > 1), "D": pratinjau}
    if lama.get("a3"):
        out["a3"] = 1          # penanda MP3 (tools/buat_audio_hsk3.py --tandai) dipertahankan
    with open(a.keluar, "w", encoding="utf-8") as f:
        json.dump(out, f, ensure_ascii=False, separators=(",", ":"))
    print(f"pratinjau: {len(pratinjau)} dari {len(rows)} kata -> {a.keluar} ({os.path.getsize(a.keluar)} byte)")


if __name__ == "__main__":
    main()
