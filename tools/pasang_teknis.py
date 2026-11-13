#!/usr/bin/env python3
"""Memasang kosakata teknis bidang baru (Finance & Akuntansi, Pertambangan & Smelter, Bandara Lanjutan) ke index.html.

Berkas penuh (360 istilah) TIDAK disimpan di repo ini karena repo bersifat publik. Isi penuh dilayani server n8n
(tabel hsk_isi, paket fin / tam / ban) hanya untuk pemilik, akun langganan, dan akun trial bertanggal.
Yang masuk repo hanya cuplikan gratis (GRATIS istilah pertama tiap bidang) dan baris kosong penjaga tempat.

Cara kerja: tiap bidang mendapat kode level sendiri (10 Finance, 11 Tambang, 12 Bandara Lanjutan) dan ditaruh di AKHIR
array D di DATA index.html, urut tetap. Baris di luar cuplikan berupa penjaga tempat ["","","",level,bab,"",""]; situs
mengisinya di tempat (tanpa mengubah posisi) setelah isi penuh diterima dari server. Posisi baris di D adalah kunci
progres ("k<posisi>" di hsk_m dan jadwal ulang SRS), jadi urutan ini TIDAK boleh berubah, dan baris baru apa pun
harus ditambahkan sesudah baris terakhir.

Pakai:
  python3 tools/pasang_teknis.py --data /jalur/teknis-penuh.json --html index.html --server /jalur/hsk_isi_teknis.json

Bentuk berkas penuh : {"v":1,"bidang":{"fin":{"lv":10,"nama":"...","bab":["A · ...",...],"D":[[hanzi,pinyin,arti,level,bab,contoh,kelas],...]},"tam":{...},"ban":{...}}}
Berkas --server     : daftar baris tabel hsk_isi [{"paket":"fin","urut":1,"isi":"<JSON 30 istilah>"},...] (opsional)
Skrip ini aman dijalankan ulang: baris level 10 ke atas dibuang dulu, lalu dipasang lagi.
"""
import argparse
import json
import sys

GRATIS = 30      # istilah pertama tiap bidang yang terbuka untuk semua akun (sama dengan TEK_GRATIS di index.html)
PER_SET = 30     # istilah per baris tabel hsk_isi
LV_BARU = 10     # level >= 10 = bidang baru
ORDE = ["fin", "tam", "ban"]


def cek(b, kode):
    d = b["D"]
    if b["lv"] < LV_BARU:
        sys.exit(f"{kode}: level harus >= {LV_BARU}")
    if not d:
        sys.exit(f"{kode}: kosong")
    for i, r in enumerate(d):
        if not (isinstance(r, list) and len(r) == 7):
            sys.exit(f"{kode}[{i}]: harus 7 kolom")
        if not all(isinstance(r[j], str) and r[j] for j in (0, 1, 2, 5, 6)):
            sys.exit(f"{kode}[{i}]: kolom teks kosong")
        if r[3] != b["lv"] or not (1 <= r[4] <= len(b["bab"])):
            sys.exit(f"{kode}[{i}]: level atau bab tidak cocok")
    bab = [r[4] for r in d]
    if bab != sorted(bab):
        sys.exit(f"{kode}: bab harus berurutan")


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--data", required=True, help="berkas kosakata penuh (di luar repo)")
    ap.add_argument("--html", default="index.html")
    ap.add_argument("--server", help="tulis baris tabel hsk_isi ke berkas ini")
    a = ap.parse_args()

    penuh = json.load(open(a.data, encoding="utf-8"))
    bid = penuh["bidang"]
    for k in ORDE:
        cek(bid[k], k)

    teks = open(a.html, encoding="utf-8").read()
    baris = teks.split("\n")
    ix = next((i for i, l in enumerate(baris) if l.startswith("const DATA=")), None)
    if ix is None:
        sys.exit("baris const DATA= tidak ditemukan")
    L = baris[ix]
    j = L.index("{")
    obj, akhir = json.JSONDecoder().raw_decode(L[j:])
    ekor = L[j + akhir:]
    D, CH = obj["D"], obj["CH"]

    D[:] = [r for r in D if r[3] < LV_BARU]            # aman dijalankan ulang
    for k in list(CH):
        if int(k) >= LV_BARU:
            del CH[k]
    awal = len(D)
    server = []
    for k in ORDE:
        b = bid[k]
        for i, r in enumerate(b["D"]):
            D.append(list(r) if i < GRATIS else ["", "", "", r[3], r[4], "", ""])
        CH[str(b["lv"])] = list(b["bab"])
        for s in range(0, len(b["D"]), PER_SET):
            server.append({"paket": k, "urut": s // PER_SET + 1, "isi": json.dumps(b["D"][s:s + PER_SET], ensure_ascii=False, separators=(",", ":"))})
        print(f"{k}: level {b['lv']}, {len(b['D'])} istilah, posisi D {awal + sum(len(bid[x]['D']) for x in ORDE[:ORDE.index(k)])}..")

    baris[ix] = L[:j] + json.dumps(obj, ensure_ascii=False, separators=(",", ":")) + ekor
    open(a.html, "w", encoding="utf-8").write("\n".join(baris))
    print(f"D sekarang {len(D)} baris ({len(D) - awal} baru, {sum(1 for r in D[awal:] if r[0])} terbuka sebagai cuplikan)")
    if a.server:
        json.dump(server, open(a.server, "w", encoding="utf-8"), ensure_ascii=False, separators=(",", ":"))
        print(f"{len(server)} baris hsk_isi ditulis ke {a.server}")


if __name__ == "__main__":
    main()
