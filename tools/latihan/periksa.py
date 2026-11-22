#!/usr/bin/env python3
"""Pemeriksa paket Latihan gaya HSK (data/latihan-1.json ... latihan-5.json).

Tujuan: jumlah butir, pembagian 听力/阅读/书写, dan jenis soal tiap nomor harus sama dengan kertas ujian HSK asli.
Sumber kebenaran struktur adalah konstanta UJ_LV di index.html,
jadi pemeriksa ini membacanya langsung dan membandingkannya dengan tabel BAGIAN di bawah.

Pemakaian:  python3 tools/latihan/periksa.py            (semua level yang ada)
            python3 tools/latihan/periksa.py 1 3        (level tertentu)
Keluar dengan kode 1 bila ada kesalahan. Peringatan tidak menggagalkan.

Pemeriksaan:
  1. Struktur: jumlah butir = UJ_LV[level].n, nomor berurutan, jenis tiap nomor sama dengan UJ_LV, bagian tidak melintasi batas 听力/阅读/书写.
  2. Bentuk tiap jenis: tf (T/X), abc (3 opsi), abcd (4 opsi), af (6 opsi bersama untuk 5 butir, kunci tidak kembar),
     ord (urutan ABC), tulis (kepingan kalimat), han (satu hanzi), xie (menulis bebas).
  3. Rekaman: semua butir 听力 punya skrip rekaman, butir 阅读 dan 书写 tidak.
  4. Kosakata: setiap hanzi harus ada di daftar kosakata level itu (HSK 2.0, kumulatif) atau daftar nama.
  5. Tanpa em dash, opsi tidak kembar, terjemahan ada untuk rekaman dan bacaan.
"""
import itertools
import json
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
HANZI = re.compile(r"[一-鿿]")
PUNCT = re.compile(r"[，。？！、；：“”‘’（）()\s,.?!;:\"'…·]")

# Nama orang yang boleh dipakai walau hanzinya di luar daftar kosakata (kertas ujian asli juga memakai nama seperti ini).
NAMES = set("李王张刘陈杨赵周吴黄林明华丽月方红芳伟强静雪燕玲卫玛约翰")

# Pembagian per level: (dari, sampai, jenis, ciri). Jenis: tf abc abcd af ord tulis han xie.
# Ciri (dipisah spasi): L = ada rekaman, g = ada deskripsi gambar, x = ada teks cetak, grup = opsi bersama A-F, pic = opsi berupa deskripsi gambar,
#       w = kepingan/kata, s = tiga kalimat, h = pinyin petunjuk, q = pertanyaan cetak, bc = bacaan bersama.
BAGIAN = {
    1: [(1, 5, "tf", "L g"), (6, 10, "abc", "L pic"), (11, 15, "af", "L grup pic"), (16, 20, "abc", "L"),
        (21, 25, "tf", "g x"), (26, 30, "af", "x grup pic"), (31, 35, "af", "x grup"), (36, 40, "af", "x grup")],
    2: [(1, 10, "tf", "L g"), (11, 15, "af", "L grup pic"), (16, 20, "af", "L grup pic"), (21, 30, "abc", "L"), (31, 35, "abc", "L"),
        (36, 40, "af", "x grup pic"), (41, 45, "af", "x grup pic"), (46, 50, "tf", "x"), (51, 55, "af", "x grup"), (56, 60, "af", "x grup")],
    3: [(1, 5, "af", "L grup pic"), (6, 10, "af", "L grup pic"), (11, 20, "tf", "L x"), (21, 30, "abc", "L"), (31, 40, "abc", "L"),
        (41, 45, "af", "x grup"), (46, 50, "af", "x grup"), (51, 55, "af", "x grup"), (56, 60, "af", "x grup"),
        (61, 70, "abc", "x q"), (71, 75, "tulis", "w"), (76, 80, "han", "x h")],
    4: [(1, 10, "tf", "L x"), (11, 25, "abcd", "L"), (26, 45, "abcd", "L"), (46, 50, "af", "x grup"), (51, 55, "af", "x grup"),
        (56, 65, "ord", "s"), (66, 85, "abcd", "q bc"), (86, 95, "tulis", "w"), (96, 100, "xie", "g w")],
    5: [(1, 20, "abcd", "L"), (21, 45, "abcd", "L"), (46, 60, "abcd", "bc"), (61, 70, "abcd", "q bc"), (71, 90, "abcd", "q bc"),
        (91, 98, "tulis", "w"), (99, 99, "xie", "w"), (100, 100, "xie", "g")],
}
# Jenis di UJ_LV yang cocok dengan jenis di sini.
COCOK = {"tf": "tf", "abc": "abc", "abcd": "abcd", "af": "af", "ord": "ord", "han": "han", "tulis": "tulis", "xie": "tulis"}
HURUF = {"abc": "ABC", "abcd": "ABCD", "af": "ABCDEF"}


def baca_uj_lv(html):
    m = re.search(r"const UJ_LV=\{(.*?)\n\};", html, re.S)
    if not m:
        sys.exit("UJ_LV tidak ditemukan di index.html")
    out = {}
    for mm in re.finditer(r"(\d):\{n:(\d+),maks:(\d+),lulus:(\d+),s:(\[\[.*?\]\]),j:(\[\[.*?\]\]),b:(\[[\d,]*\])\}", m.group(1)):
        out[int(mm.group(1))] = {
            "n": int(mm.group(2)),
            "s": json.loads(mm.group(5).replace("'", '"')),
            "j": json.loads(mm.group(6).replace("'", '"')),
            "b": json.loads(mm.group(7)),
        }
    if sorted(out) != [1, 2, 3, 4, 5]:
        sys.exit("UJ_LV tidak terbaca lengkap: " + str(sorted(out)))
    return out


def kosakata(html):
    i = html.index("const DATA=") + len("const DATA=")
    d, _ = json.JSONDecoder().raw_decode(html[i:])
    tingkat = {1: {1}, 2: {1, 2, 9}, 3: {1, 2, 3, 9}, 4: {1, 2, 3, 4, 9}, 5: {1, 2, 3, 4, 7, 9}}
    return {lv: set("".join(w[0] for w in d["D"] if w[3] in ok)) for lv, ok in tingkat.items()}


def jenis_uj(uj, n):
    for batas, t in uj["j"]:
        if n <= batas:
            return t
    return "tulis"


class Lap:
    def __init__(self):
        self.err, self.warn = [], []

    def e(self, kode, pesan):
        self.err.append(f"[{kode}] {pesan}")

    def w(self, kode, pesan):
        self.warn.append(f"[{kode}] {pesan}")


def teks_zh(it, ciri, pk, grup_of):
    """Semua string yang seharusnya hanzi (untuk cek kosakata). Mengembalikan daftar (label, teks)."""
    r = []
    for s in it.get("au", []):
        r.append(("au", re.sub(r"^(男|女|问)[：:]", "", s)))  # awalan pembicara bukan isi soal
    for k in ("x", "q", "ex", "h2"):
        if isinstance(it.get(k), str):
            r.append((k, it[k]))
    if "pic" not in ciri:
        for s in it.get("o", []):
            r.append(("o", s))
    for s in it.get("s", []):
        r.append(("s", s))
    for s in it.get("w", []):
        r.append(("w", s))
    k = it.get("k")
    if isinstance(k, list):
        r += [("k", s) for s in k]
    elif isinstance(k, str) and HANZI.search(k):
        r.append(("k", k))
    return r


def periksa_paket(lv, pk, uj, ada, lap):
    kode = f"HSK{lv} {pk.get('id', '?')}"
    N = uj["n"]
    soal = pk.get("soal")
    if not isinstance(soal, list) or len(soal) != N:
        lap.e(kode, f"jumlah butir {len(soal) if isinstance(soal, list) else 'tidak ada'}, seharusnya {N}")
        return
    grup = pk.get("grup") or []
    bc = pk.get("bc") or []
    for g in grup:
        if len(g.get("o", [])) != 6 or len(set(g["o"])) != 6:
            lap.e(kode, f"grup {g.get('d')}-{g.get('s')} harus punya 6 opsi berbeda")
    peta_g = {}
    for g in grup:
        for n in range(g["d"], g["s"] + 1):
            if n in peta_g:
                lap.e(kode, f"nomor {n} ada di dua grup")
            peta_g[n] = g
    peta_b = {}
    for b in bc:
        for n in range(b["d"], b["s"] + 1):
            peta_b[n] = b
        if not b.get("t") or not b.get("tr"):
            lap.e(kode, f"bacaan {b.get('d')}-{b.get('s')} butuh t (hanzi) dan tr (terjemahan)")
    # 1. struktur
    spek = BAGIAN[lv]
    nomor_spek = {}
    for a, z, t, c in spek:
        for n in range(a, z + 1):
            nomor_spek[n] = (a, z, t, c)
    if sorted(nomor_spek) != list(range(1, N + 1)):
        lap.e(kode, "tabel BAGIAN tidak menutup nomor 1 sampai " + str(N))
    batas = {s[1]: s[2] for s in uj["s"]}  # awal bagian -> akhir bagian
    for a, z, t, c in spek:
        for s_awal, s_akhir in batas.items():
            if a < s_awal <= z or a <= s_akhir < z:
                lap.e(kode, f"bagian {a}-{z} melintasi batas 听力/阅读/书写 ({s_awal}-{s_akhir})")
    for b in uj["b"]:
        if b not in {a for a, _, _, _ in spek}:
            lap.e(kode, f"awal 第X部分 nomor {b} (UJ_LV) bukan awal bagian di tabel BAGIAN")
    for n in range(1, N + 1):
        a, z, t, c = nomor_spek[n]
        if COCOK[t] != jenis_uj(uj, n):
            lap.e(kode, f"nomor {n}: jenis {t} tidak cocok dengan UJ_LV ({jenis_uj(uj, n)})")
    # 2. bentuk tiap butir
    dengar = set()
    for s in uj["s"]:
        if s[0] == "听力":
            dengar = set(range(s[1], s[2] + 1))
    kunci_grup = {}
    for n in range(1, N + 1):
        it = soal[n - 1]
        a, z, t, c = nomor_spek[n]
        ciri = set(c.split())
        lab = f"{kode} no.{n}"
        if not isinstance(it, dict) or it.get("n") != n:
            lap.e(lab, "butir tidak punya n yang sama dengan urutannya")
            continue
        # rekaman
        au = it.get("au")
        if n in dengar:
            if not au or not isinstance(au, list):
                lap.e(lab, "butir 听力 tanpa skrip rekaman (au)")
            else:
                for s in au:
                    if not isinstance(s, str) or not s.strip():
                        lap.e(lab, "baris au kosong")
                    elif re.match(r"^(男|女|问)[：:]", s) is None and re.match(r"^[^：:]{0,2}[：:]", s):
                        lap.e(lab, f"awalan pembicara tidak dikenal: {s[:6]}")
                if not it.get("tr"):
                    lap.e(lab, "butir 听力 butuh terjemahan (tr)")
        elif au:
            lap.e(lab, "butir di luar 听力 tidak boleh punya rekaman")
        k = it.get("k")
        o = it.get("o", [])
        if t == "tf":
            if k not in ("T", "X"):
                lap.e(lab, f"kunci tf harus T atau X, bukan {k!r}")
            if "g" in ciri and not it.get("g"):
                lap.e(lab, "butuh deskripsi gambar (g)")
            if "x" in ciri and not it.get("x"):
                lap.e(lab, "butuh teks cetak (x)")
        elif t in ("abc", "abcd"):
            m = len(HURUF[t])
            if len(o) != m or len(set(o)) != m or not all(isinstance(s, str) and s.strip() for s in o):
                lap.e(lab, f"harus punya {m} opsi berbeda dan tidak kosong")
            if k not in list(HURUF[t]):
                lap.e(lab, f"kunci {k!r} di luar {HURUF[t]}")
            if "q" in ciri and not (it.get("q") or (n in peta_b and re.search(r"[（(]%d[）)]" % n, peta_b[n]["t"]))):
                lap.e(lab, "butuh pertanyaan cetak (q) atau lubang (n) di bacaan")
            if ("bc" in ciri or lv == 5) and not (n in peta_b or it.get("x")):
                if lv >= 4 and n >= 46:
                    lap.e(lab, "butuh bacaan (bc) atau teks (x)")
            if lv == 3 and 61 <= n <= 70 and not it.get("x") and n not in peta_b:
                lap.e(lab, "butuh bacaan pendek (x)")
        elif t == "af":
            g = peta_g.get(n)
            if g is None:
                lap.e(lab, "tidak ada grup opsi A-F untuk nomor ini")
            else:
                if (g["d"], g["s"]) != (a, z):
                    lap.e(lab, f"grup {g['d']}-{g['s']} tidak sama dengan bagian {a}-{z}")
                if k not in list("ABCDEF"):
                    lap.e(lab, f"kunci {k!r} di luar A-F")
                else:
                    kunci_grup.setdefault((g["d"], g["s"]), []).append((n, k))
            if "x" in ciri and not it.get("x"):
                lap.e(lab, "butuh teks cetak (x)")
        elif t == "ord":
            sk = it.get("s")
            if not isinstance(sk, list) or len(sk) != 3 or len(set(sk)) != 3:
                lap.e(lab, "ord butuh 3 kalimat berbeda (s)")
            if not (isinstance(k, str) and sorted(k) == ["A", "B", "C"]):
                lap.e(lab, f"kunci ord harus urutan dari ABC, bukan {k!r}")
        elif t == "tulis":
            w = it.get("w")
            if not isinstance(w, list) or not (3 <= len(w) <= 7) or not all(isinstance(s, str) and s for s in w):
                lap.e(lab, "tulis butuh 3 sampai 7 kepingan (w)")
            elif isinstance(k, list) and k:
                polos = {PUNCT.sub("", s) for s in k}
                sesuai = False
                gabung = "".join(w)
                if gabung in polos:
                    lap.e(lab, "kepingan w sudah dalam urutan benar, harus diacak")
                for p in set(itertools.permutations(w)):
                    if "".join(p) in polos:
                        sesuai = True
                        break
                if not sesuai:
                    lap.e(lab, "kunci k tidak bisa disusun dari kepingan w")
                if len(polos) != len(k):
                    lap.w(lab, "ada kunci kembar di k")
            else:
                lap.e(lab, "tulis butuh kunci k berupa daftar kalimat")
        elif t == "han":
            x = it.get("x", "")
            if x.count("□") != 1:
                lap.e(lab, "han butuh tepat satu kotak □ di x")
            if not (isinstance(k, str) and len(k) == 1 and HANZI.match(k)):
                lap.e(lab, "kunci han harus satu hanzi")
            if not it.get("h"):
                lap.e(lab, "han butuh pinyin petunjuk (h)")
        elif t == "xie":
            ex = it.get("ex", "")
            n_ex = len(HANZI.findall(ex))
            if "w" in ciri:
                w = it.get("w")
                if not isinstance(w, list) or not w:
                    lap.e(lab, "xie butuh kata wajib (w)")
                elif lv == 5 and len(w) != 5:
                    lap.e(lab, "HSK 5 no.99 butuh tepat 5 kata")
                elif lv == 4 and len(w) != 1:
                    lap.e(lab, "HSK 4 no.96-100 butuh tepat 1 kata")
                elif any(x not in ex for x in w):
                    lap.e(lab, "contoh jawaban (ex) tidak memuat semua kata wajib")
            if "g" in ciri and not it.get("g"):
                lap.e(lab, "xie butuh deskripsi gambar (g)")
            if lv == 5 and n_ex < 80:
                lap.e(lab, f"contoh jawaban {n_ex} hanzi, harus sekitar 80 atau lebih")
            if lv == 4 and not (8 <= n_ex <= 40):
                lap.w(lab, f"contoh kalimat {n_ex} hanzi (biasanya 8 sampai 40)")
        # 3. teks umum
        for lbl, s in teks_zh(it, ciri, pk, peta_g):
            bad = {ch for ch in HANZI.findall(s) if ch not in ada and ch not in NAMES}
            if bad:
                lap.e(lab, f"hanzi di luar kosakata HSK {lv} ({lbl}): {''.join(sorted(bad))}  <- {s[:30]}")
    # grup: kunci tidak kembar
    for (d, s), ks in kunci_grup.items():
        huruf = [k for _, k in ks]
        if len(set(huruf)) != len(huruf):
            lap.e(kode, f"grup {d}-{s}: kunci kembar {huruf}")
    for g in grup:
        pic = any("pic" in c for a, z, t, c in spek if (a, z) == (g["d"], g["s"]))
        if not pic:
            bad = {ch for ch in HANZI.findall("".join(g["o"])) if ch not in ada and ch not in NAMES}
            if bad:
                lap.e(kode, f"hanzi di luar kosakata HSK {lv} pada grup {g['d']}-{g['s']}: {''.join(sorted(bad))}")
    for b in bc:
        bad = {ch for ch in HANZI.findall(b["t"]) if ch not in ada and ch not in NAMES}
        if bad:
            lap.e(kode, f"hanzi di luar kosakata HSK {lv} pada bacaan {b['d']}-{b['s']}: {''.join(sorted(bad))}")
    # 5. em dash dan sebaran kunci
    teks = json.dumps(pk, ensure_ascii=False)
    if "—" in teks:
        lap.e(kode, "ada em dash")
    for tipe, hur in (("abc", "ABC"), ("abcd", "ABCD")):
        ks = [soal[n - 1].get("k") for n in range(1, N + 1) if nomor_spek[n][2] == tipe]
        if ks:
            for h in hur:
                if ks.count(h) > 0.6 * len(ks) and len(ks) >= 10:
                    lap.w(kode, f"sebaran kunci {tipe}: {h} muncul {ks.count(h)} dari {len(ks)}")
    tf = [soal[n - 1].get("k") for n in range(1, N + 1) if nomor_spek[n][2] == "tf"]
    if len(tf) >= 10 and not (0.3 <= tf.count("T") / len(tf) <= 0.7):
        lap.w(kode, f"sebaran benar/salah: T={tf.count('T')} X={tf.count('X')}")


def ringkas(lv, pk, uj):
    soal = pk["soal"]
    baris = []
    for nama, a, z, _ in uj["s"]:
        baris.append(f"{nama} {a}-{z} ({z - a + 1})")
    return f"HSK{lv} {pk['id']} '{pk.get('judul', '')}': {len(soal)} butir = " + ", ".join(baris)


def main():
    html = open(os.path.join(ROOT, "index.html"), encoding="utf-8").read()
    uj_lv = baca_uj_lv(html)
    kv = kosakata(html)
    pilih = [int(a) for a in sys.argv[1:]] or [1, 2, 3, 4, 5]
    lap = Lap()
    jml = 0
    for lv in pilih:
        path = os.path.join(ROOT, "data", f"latihan-{lv}.json")
        if not os.path.exists(path):
            print(f"HSK{lv}: berkas belum ada, dilewati")
            continue
        try:
            d = json.load(open(path, encoding="utf-8"))
        except Exception as ex:  # noqa: BLE001
            lap.e(f"HSK{lv}", f"JSON rusak: {ex}")
            continue
        if d.get("v") != 1 or d.get("lv") != lv or not isinstance(d.get("paket"), list) or not d["paket"]:
            lap.e(f"HSK{lv}", "format berkas: butuh v=1, lv, dan paket (daftar tidak kosong)")
            continue
        ids = [p.get("id") for p in d["paket"]]
        if len(set(ids)) != len(ids):
            lap.e(f"HSK{lv}", "id paket kembar")
        for pk in d["paket"]:
            jml += 1
            periksa_paket(lv, pk, uj_lv[lv], kv[lv], lap)
            print(ringkas(lv, pk, uj_lv[lv]))
    for p in lap.warn:
        print("PERINGATAN", p)
    for p in lap.err:
        print("GALAT", p)
    print(f"\n{jml} paket diperiksa: {len(lap.err)} galat, {len(lap.warn)} peringatan")
    sys.exit(1 if lap.err else 0)


if __name__ == "__main__":
    main()
