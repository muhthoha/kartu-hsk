#!/usr/bin/env python3
"""Buat audio MP3 untuk kosakata HSK 3.0 dengan suara Microsoft Edge (edge-tts).

Sumber kata: berkas kosakata PENUH (3.600 kata) yang disimpan di luar repo (repo ini publik, jadi hanya pratinjau
data/hsk3.json yang ada di sini). Tunjukkan lokasinya dengan --data.

Hasilnya masuk ke folder audio3/:
    audio3/w<id>.mp3   suara kata      (id = nomor urut kata di berkas penuh + 1)
    audio3/s<id>.mp3   suara kalimat contoh
    audio3/index.json  daftar id yang sudah ada: {"w":[...], "s":[...]}

Situs memakai MP3 ini otomatis bila data/hsk3.json bertanda "a3": 1 (pakai --tandai) dan audio3/index.json ada.
Kata yang tidak punya MP3 tetap memakai suara browser. Kata yang hanzi-nya punya lebih dari satu bacaan di daftar
(还 hái/huán, 好 hǎo/hào, dst.) sengaja TIDAK dibuatkan audio kata, karena suara mesin memilih bacaan sendiri;
kalimatnya tetap dibuat.

Catatan: berkas di audio3/ ikut terbit di situs dan bisa diunduh siapa saja yang tahu alamatnya (suara saja, tanpa arti).

Cara pakai (di komputer Anda, di folder repo kartu-hsk, perlu internet):
    pip install edge-tts
    python3 tools/buat_audio_hsk3.py --data /jalur/hsk3-penuh.json --level 1   # coba Level 1 dulu (300 kata + 300 kalimat)
    python3 tools/buat_audio_hsk3.py --data /jalur/hsk3-penuh.json             # semua level (7.200 berkas, kira-kira 100 MB)
    python3 tools/buat_audio_hsk3.py --tandai              # pasang "a3": 1 di data/hsk3.json (pratinjau) setelah audio siap
Skrip bisa dihentikan dan dijalankan lagi kapan saja: berkas yang sudah ada dilewati.
Opsi lain: --only w (hanya kata) atau --only s (hanya kalimat), --voice zh-CN-YunxiNeural, --rate=-15%, --paralel 4.
"""
import argparse
import asyncio
import json
import os
import sys
from collections import defaultdict


def muat(path):
    with open(path, encoding="utf-8") as f:
        j = json.load(f)
    if j.get("v") != 1 or not isinstance(j.get("D"), list) or len(j["D"]) < 1000:
        sys.exit("Berkas kosakata penuh tidak dikenali (butuh {\"v\":1,\"D\":[...3.600 baris...]}). data/hsk3.json di repo hanya pratinjau.")
    return j


def daftar_tugas(rows, level, only):
    bacaan = defaultdict(set)
    for r in rows:
        bacaan[r[0]].add(r[1])
    tugas = []
    for i, r in enumerate(rows):
        if level and r[3] != level:
            continue
        id_ = i + 1
        if only in (None, "w") and len(bacaan[r[0]]) == 1:
            tugas.append(("w", id_, r[0]))
        if only in (None, "s") and r[5]:
            tugas.append(("s", id_, r[5]))
    return tugas


async def buat(edge_tts, teks, tujuan, voice, rate, percobaan=4):
    sementara = tujuan + ".tmp"
    for n in range(percobaan):
        try:
            await edge_tts.Communicate(teks, voice, rate=rate).save(sementara)
            if os.path.getsize(sementara) < 300:
                raise RuntimeError("berkas terlalu kecil")
            os.replace(sementara, tujuan)
            return True
        except Exception as e:  # jaringan putus, dibatasi layanan, dst.
            if os.path.exists(sementara):
                os.remove(sementara)
            if n == percobaan - 1:
                print(f"  gagal {os.path.basename(tujuan)}: {e}", file=sys.stderr)
                return False
            await asyncio.sleep(2 * (n + 1))


def tulis_index(folder):
    w, s = [], []
    for nama in os.listdir(folder):
        if nama.endswith(".mp3") and nama[1:-4].isdigit() and os.path.getsize(os.path.join(folder, nama)) >= 300:
            (w if nama[0] == "w" else s if nama[0] == "s" else []).append(int(nama[1:-4]))
    w.sort()
    s.sort()
    with open(os.path.join(folder, "index.json"), "w", encoding="utf-8") as f:
        json.dump({"w": w, "s": s}, f, separators=(",", ":"))
    return len(w), len(s)


async def main_async(a, rows, folder):
    try:
        import edge_tts
    except ImportError:
        sys.exit("Pasang dulu: pip install edge-tts")
    tugas = daftar_tugas(rows, a.level, a.only)
    sisa = [(k, i, t) for (k, i, t) in tugas if not os.path.exists(os.path.join(folder, f"{k}{i}.mp3"))]
    print(f"Total {len(tugas)} berkas, sudah ada {len(tugas) - len(sisa)}, akan dibuat {len(sisa)}.")
    if a.dry_run or not sisa:
        return
    os.makedirs(folder, exist_ok=True)
    sem = asyncio.Semaphore(a.paralel)
    selesai = gagal = 0

    async def satu(k, i, t):
        nonlocal selesai, gagal
        async with sem:
            ok = await buat(edge_tts, t, os.path.join(folder, f"{k}{i}.mp3"), a.voice, a.rate)
        if ok:
            selesai += 1
        else:
            gagal += 1
        if (selesai + gagal) % 50 == 0:
            print(f"  {selesai + gagal}/{len(sisa)} (gagal {gagal})")

    await asyncio.gather(*(satu(*x) for x in sisa))
    print(f"Selesai: {selesai} dibuat, {gagal} gagal. Jalankan lagi bila ada yang gagal.")


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--data", default=None, help="lokasi berkas kosakata PENUH (di luar repo); wajib kecuali untuk --tandai")
    ap.add_argument("--keluar", default=None, help="folder keluaran (bawaan: audio3/ di repo)")
    ap.add_argument("--level", type=int, choices=[1, 2, 3, 4, 5], help="hanya level ini")
    ap.add_argument("--only", choices=["w", "s"], help="w = hanya kata, s = hanya kalimat")
    ap.add_argument("--voice", default="zh-CN-XiaoxiaoNeural")
    ap.add_argument("--rate", default="-10%", help="kecepatan bicara, mis. -10%% atau +0%%")
    ap.add_argument("--paralel", type=int, default=5)
    ap.add_argument("--dry-run", action="store_true", help="hanya hitung, tidak membuat berkas")
    ap.add_argument("--tandai", action="store_true", help='pasang "a3": 1 di data/hsk3.json (pratinjau) lalu keluar (setelah audio siap)')
    a = ap.parse_args()
    repo = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    pratinjau = os.path.join(repo, "data", "hsk3.json")
    folder = a.keluar or os.path.join(repo, "audio3")
    if a.tandai:
        with open(pratinjau, encoding="utf-8") as f:
            j = json.load(f)
        if not os.path.exists(os.path.join(folder, "index.json")):
            n = tulis_index(folder) if os.path.isdir(folder) else (0, 0)
            print(f"index.json dibuat: {n[0]} kata, {n[1]} kalimat")
        j["a3"] = 1
        with open(pratinjau, "w", encoding="utf-8") as f:
            json.dump(j, f, ensure_ascii=False, separators=(",", ":"))
        print('data/hsk3.json sekarang bertanda "a3": 1. Naikkan angka "?v=2" pada data/hsk3.json di index.html bila perlu menyegarkan cache.')
        return
    if not a.data:
        sys.exit("Sebutkan berkas kosakata penuh dengan --data /jalur/hsk3-penuh.json (berkas ini tidak ada di repo).")
    j = muat(a.data)
    asyncio.run(main_async(a, j["D"], folder))
    if not a.dry_run and os.path.isdir(folder):
        n = tulis_index(folder)
        print(f"audio3/index.json diperbarui: {n[0]} kata, {n[1]} kalimat")


if __name__ == "__main__":
    main()
