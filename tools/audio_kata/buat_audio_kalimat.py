#!/usr/bin/env python3
"""MP3 untuk kalimat contoh, memakai mesin yang sama dengan buat_audio_kata.py (MeloTTS + pemeriksa SenseVoice).

  python3 pinyin_kalimat.py --data hsk3-penuh.json --model <vits-melo-tts-zh_en> --keluar kalimat.json --tinjau tinjau.csv
  python3 buat_audio_kalimat.py --daftar kalimat.json --model <vits-melo-tts-zh_en> --asr <SenseVoice int8> \
      --keluar ../../audio/kalimat [--bagian 0 --dari 2] [--batas 50]

--daftar : keluaran pinyin_kalimat.py. Bila ada kolom "p2" (pinyin yang sudah dikoreksi manusia), itu yang dipakai.
Nama berkas = kah("s|" + hanzi kalimat) + ".mp3". Kuncinya HANYA hanzi kalimat, sehingga situs tidak perlu pinyin kalimat
(situs tidak menyimpannya). Kalimat yang sama untuk dua kata hanya dibuat sekali.
Hasil pemeriksaan tiap kalimat ditulis ke <keluar>/../kalimat-hasil-<bagian>.jsonl; proses dapat dilanjutkan.
Kalimat yang belum lolos pemeriksaan (s/t salah satunya False) dapat dicoba lagi dengan variasi suara tambahan; berkas lama
hanya diganti bila hasil baru lolos dua-duanya:
  python3 buat_audio_kalimat.py --daftar kalimat.json --model <...> --asr <...> --keluar ../../audio/kalimat --ulangi [--seed-tambahan 8]
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
import buat_audio_kata as bk
from buat_audio_kata import Pembuat


def kunci(h):
    return kah.kah("s|" + h)


def tulis_indeks(keluar):
    """index.json = daftar kode berkas yang ada (tanpa hanzi). Situs memakainya untuk tahu kalimat mana yang punya MP3.
    Jalankan sekali setelah semua --bagian selesai, lalu naikkan angka ?v= di index.html (h3Load) agar peramban memuat ulang."""
    ks = sorted(f[:-4] for f in os.listdir(keluar) if f.endswith(".mp3"))
    # kalimat yang belum lolos pemeriksa (menurut kalimat-hasil-*.jsonl di folder induk) tidak didaftarkan:
    # tombolnya jatuh ke suara peramban sampai ada yang mendengarkan dan memutuskan. Yang sudah didengar dan disetujui manusia:
    # tambahkan baris {"h": kalimat, "ok": true, "info": {...}, "disetujui": true} ke kalimat-hasil-*.jsonl (baris terakhir menang)
    tak_lolos = {kunci(h) for h, r in hasil_terakhir(keluar).items()
                 if r.get("ok") and not (r["info"].get("s") and r["info"].get("t")) and not r.get("disetujui")}
    if tak_lolos & set(ks):
        print("dikecualikan dari indeks (belum lolos):", len(tak_lolos & set(ks)))
        ks = [k for k in ks if k not in tak_lolos]
    with open(os.path.join(keluar, "index.json"), "w", encoding="utf-8") as f:
        json.dump(ks, f, separators=(",", ":"))
    print("indeks:", len(ks), "berkas")


def hasil_terakhir(keluar):
    """Hasil pemeriksaan tiap kalimat dari semua kalimat-hasil-*.jsonl (baris terakhir menang)."""
    induk = os.path.dirname(os.path.abspath(keluar))
    rs = {}
    for nama in sorted(os.listdir(induk)):
        if nama.startswith("kalimat-hasil-") and nama.endswith(".jsonl"):
            for l in open(os.path.join(induk, nama), encoding="utf-8"):
                try:
                    r = json.loads(l)
                    rs[r["h"]] = r
                except Exception:
                    pass
    return rs


def ulangi(a):
    """Coba lagi kalimat yang belum lolos dengan seed tambahan. Berkas MP3 diganti hanya bila hasil baru lolos."""
    items = {}
    for x in json.load(open(a.daftar, encoding="utf-8")):
        items.setdefault(x["h"], x.get("p2") or x["p"])
    rs = hasil_terakhir(a.keluar)
    gagal = [h for h, r in rs.items() if r.get("ok") and not (r["info"].get("s") and r["info"].get("t")) and h in items]
    print("belum lolos:", len(gagal))
    bk.SENT = [("X", k) for k in range(3, 3 + a.seed_tambahan)]
    P = Pembuat(a.model, a.asr)
    resf = os.path.join(os.path.dirname(os.path.abspath(a.keluar)), "kalimat-hasil-ulang.jsonl")
    pulih = 0
    with open(resf, "a", encoding="utf-8") as fo:
        for h in gagal:
            y, info = P.satu(h, items[h])
            lolos = bool(info.get("s") and info.get("t"))
            if lolos:
                zs.to_mp3(y, os.path.join(a.keluar, kunci(h) + ".mp3"))
                pulih += 1
            rec = dict(h=h, p=items[h], ok=True, dur=round(len(y) / zs.SR, 2), info=info, ulang=True, diganti=lolos)
            if not lolos:  # audio lama tetap dipakai; catat hasil lama supaya laporan tidak menyesatkan
                rec = dict(rs[h], ulang=True, diganti=False, percobaan_ulang=info)
            fo.write(json.dumps(rec, ensure_ascii=False) + "\n")
            fo.flush()
    print("diganti:", pulih, "| tetap belum lolos:", len(gagal) - pulih)


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--daftar")
    ap.add_argument("--model")
    ap.add_argument("--asr")
    ap.add_argument("--keluar", required=True)
    ap.add_argument("--bagian", type=int, default=0)
    ap.add_argument("--dari", type=int, default=1)
    ap.add_argument("--batas", type=int, default=None)
    ap.add_argument("--ulangi", action="store_true", help="coba lagi kalimat yang belum lolos dengan seed tambahan")
    ap.add_argument("--seed-tambahan", type=int, default=8)
    ap.add_argument("--indeks", action="store_true", help="hanya tulis <keluar>/index.json dari berkas yang ada, lalu selesai")
    a = ap.parse_args()
    if a.indeks:
        tulis_indeks(a.keluar)
        return
    if not (a.daftar and a.model and a.asr):
        ap.error("--daftar, --model, dan --asr wajib (kecuali --indeks)")
    if a.ulangi:
        ulangi(a)
        return
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
