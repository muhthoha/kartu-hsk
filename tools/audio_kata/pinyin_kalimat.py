#!/usr/bin/env python3
"""Pinyin untuk kalimat contoh kartu: kata utama memakai pinyin KARTU, bagian lain dibuat otomatis.

  python3 pinyin_kalimat.py --data hsk3-penuh.json --model <folder vits-melo-tts-zh_en> --keluar kalimat.json --tinjau tinjau.csv

--data   : {"D": [[hanzi, pinyin, arti, level, set, kalimat, kelas, urut], ...]} (bentuk data/hsk3.json dan hsk3-penuh.json)
--keluar : [{"n": urut, "k": kata utama, "h": kalimat, "p": pinyin kalimat, "f": [penanda ragu]}, ...]
--tinjau : CSV hanya berisi kalimat yang ditandai ragu, untuk dicek manusia.

Cara kerja:
1. Kata utama dicari di kalimat; bila ketemu, pinyin kartu dipakai apa adanya (bacaan yang pasti benar).
2. Sisanya dipecah dengan kamus MeloTTS (lexicon.txt) dan frekuensi jieba bawaan model, lalu dibaca per kata. Tanpa pustaka luar.
3. Sandhi 不 dan 一 diterapkan (gaya kartu: bú, yí, yì). Nada tiga berurutan dibiarkan nada dasar, seperti di kartu; sandhi nada tiga
   dikerjakan oleh pembuat audio (zpinyin/zsynth).
4. Hanzi berbacaan ganda yang dibaca lewat bacaan bawaan ditandai "ragu". Itu yang perlu didengar atau dicek manusia.
5. Hasil diperiksa sendiri: harus terbaca oleh parser pembuat audio dan jumlah suku katanya sama dengan jumlah hanzi.
"""
import argparse
import csv
import json
import math
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import zeval
import zpinyin as zp
import zsynth as zs

MARK = {"a": "āáǎà", "e": "ēéěè", "i": "īíǐì", "o": "ōóǒò", "u": "ūúǔù", "ü": "ǖǘǚǜ"}
PUNCT = "，。？！：；、…"
HAN = "㐀-鿿"
# hanzi berbacaan ganda yang umum di HSK 1-5. Hanya ini yang ditandai ragu bila dibaca lewat bacaan bawaan
# (bacaan langka seperti 给 jǐ, 说 shuì, 家 gū tidak ikut, supaya daftar tinjauan tidak penuh)
POLI_UMUM = set("得地行长重为发干便假空背数种少差乐当调倒觉角教量落间切曲散省提相应载转传只参处率朝薄划片系涨吐担称将冲度累露降")
# kata ulang yang suku keduanya bernada netral (māma, xièxie, kànkan); kata ulang lain (天天, 慢慢) tetap nada penuh
ULANG_NETRAL = set("妈妈 爸爸 哥哥 姐姐 弟弟 妹妹 奶奶 爷爷 姑姑 叔叔 舅舅 婆婆 公公 娃娃 宝宝 星星 太太 谢谢 看看 想想 听听 试试 说说 玩玩 走走 问问 尝尝 洗洗 坐坐 找找 读读 写写 画画 聊聊 逛逛 歇歇 瞧瞧 学学 练练 做做 吃吃 喝喝".split())
# kata dua hanzi yang suku keduanya bernada netral menurut kamus baku, tetapi dibaca nada penuh oleh kamus model
# (喜欢 xǐhuan, 东西 dōngxi). Daftar ini disusun tangan dan TIDAK lengkap; kata netral lain perlu ditambah bila ketemu.
NETRAL_2 = set("""学生 朋友 先生 东西 喜欢 时候 便宜 衣服 漂亮 舒服 地方 觉得 知道 认识 意思 告诉 干净 清楚 明白 休息 姑娘 麻烦
眼睛 头发 耳朵 嘴巴 脾气 热闹 客气 什么 怎么 关系 玻璃 葡萄 窗户 豆腐 家伙 师傅 事情 商量 打算 打听 照顾 帮助 部分 厉害
凉快 暖和 运气 糊涂 聪明 力气 买卖 本事 笑话 招呼 护士 故事 实在 点心 骆驼 钥匙 稀罕 月亮 脑袋 胳膊 蘑菇 萝卜 石头 木头
舌头 骨头 枕头 馒头 日子 老婆 打扮 收拾 对付 大夫 大方 太阳 椅子 哥们 爱人 行李 名字 位置 生意 精神 参谋""".split())
# 儿 yang berdiri sebagai suku kata penuh (ér), bukan erhua
BUKAN_ERHUA = set("女儿 婴儿 幼儿 孤儿 胎儿 儿童 儿子 儿女 男儿 孩儿".split())
BUKAN_ERHUA_DEPAN = set("女婴幼孤胎男")
# 得 partikel (de) bila diikuti kata keterangan/adjektiva seperti ini
SESUDAH_DE = set("很不好太真多非特清这那什挺极")
# 还 dibaca huán bila diikuti kata kerja pengembalian
SESUDAH_HUAN = set("钱书给款债回")
ANGKA = set("零〇一二三四五六七八九十百千万第")


def tone_mark(s, t):
    """Suku kata tanpa nada (ü ditulis v) + nada -> pinyin bertanda nada. Nada 5 atau 0: tanpa tanda."""
    s = s.replace("v", "ü")
    if t not in (1, 2, 3, 4):
        return s
    for ch in "ae":
        if ch in s:
            i = s.index(ch)
            return s[:i] + MARK[ch][t - 1] + s[i + 1:]
    if "ou" in s:
        i = s.index("o")
        return s[:i] + MARK["o"][t - 1] + s[i + 1:]
    last = max((i for i, ch in enumerate(s) if ch in "aeiouü"), default=None)
    if last is None:
        return s
    return s[:last] + MARK[s[last]][t - 1] + s[last + 1:]


def gabung_suku(sylls):
    """[(suku, nada)] -> teks satu kata, dengan apostrof bila suku kata tengah berawalan a/o/e (dá'àn)."""
    out = ""
    for k, (s, t) in enumerate(sylls):
        if k > 0 and s and s[0] in "aoe" and sylls[k - 1][0] != "r":
            out += "'"
        out += tone_mark(s, t)
    return out


def build_inverse():
    """(inisial, final) model -> suku kata pinyin tertulis (kebalikan zp.syl2ph)."""
    finals = set(zp._FINALS) | set(zp._Y) | set(zp._W) | {"ue", "un", "uan", "u"}
    cands = {}
    for ini in zp.INITIALS + [""]:
        for f in finals:
            s = ini + f
            if s in ("ng", "n", "m", "hm", "hng"):
                continue
            try:
                ph = zp.syl2ph(s)
            except KeyError:
                ph = None
            if ph:
                cands.setdefault(ph, []).append((ini, s))

    def rank(item):
        ini, s = item
        pen = 0
        if "v" in s and ini in ("j", "q", "x", "y"):
            pen += 2
        if s.endswith("ue") and ini in ("n", "l"):
            pen += 2          # nüe, lüe ditulis dengan v
        return (pen, len(s), s)

    return {ph: min(v, key=rank)[1] for ph, v in cands.items()}


class Otomatis:
    def __init__(self, model_dir):
        self.lex = zs.Lexicon(model_dir)
        self.inv = build_inverse()
        self.poli = POLI_UMUM
        self.w = {w for w, (ph, tn) in self.lex.words.items()
                  if len(w) > 1 and len(ph) == 2 * len(w) and re.fullmatch("[" + HAN + "]+", w)}

    def syl(self, a, b, t):
        s = self.inv.get((a, b))
        return None if s is None else (s, t)

    def char_syl(self, c):
        ph = self.lex.char_ph.get(c)
        if ph is None:
            return None
        return self.syl(ph[0], ph[1], self.lex.char_tone[c])

    def word_syls(self, w):
        """-> (daftar (suku, nada), daftar indeks hanzi yang dibaca lewat bacaan bawaan satu karakter).
        Kata yang ada di kamus dibaca utuh. Kata lain dipecah dengan pencocokan terpanjang ke kamus (银行卡 -> 银行 + 卡),
        sisanya hanzi per hanzi."""
        out, bawaan, i = [], [], 0
        while i < len(w):
            for L in range(min(len(w) - i, 6), 1, -1):
                sub = w[i:i + L]
                if sub in self.w:
                    ph, tn = self.lex.words[sub]
                    s2 = [self.syl(ph[2 * j], ph[2 * j + 1], tn[2 * j]) for j in range(L)]
                    if all(s2):
                        out += s2
                        i += L
                        break
            else:
                out.append(self.char_syl(w[i]))
                bawaan.append(i)
                i += 1
        return out, bawaan

    def pecah(self, t):
        """Pemecahan kata berprobabilitas terbesar (frekuensi jieba + bonus untuk kata di kamus model)."""
        n = len(t)
        best = [(-1e18, None)] * (n + 1)
        best[0] = (0.0, [])
        for i in range(n):
            if best[i][0] <= -1e17:
                continue
            for L in range(1, min(6, n - i) + 1):
                w = t[i:i + L]
                if L == 1:
                    if w not in self.lex.char_ph:
                        continue
                    f, bonus = self.lex.freq.get(w, 1), 0.0
                else:
                    in_lex = w in self.w
                    f = self.lex.freq.get(w)
                    if not in_lex and f is None:
                        continue
                    f, bonus = (f or 1), (4.0 if in_lex else 0.0)
                sc = best[i][0] + math.log(f / self.lex.total) + bonus
                if sc > best[i + L][0]:
                    best[i + L] = (sc, best[i][1] + [L])
        return best[n][1] if best[n][1] is not None else [1] * n

    def run_hanzi(self, t, flags, pre="", post=""):
        """Satu deret hanzi murni -> daftar unit dict(c=hanzi, s=[(suku, nada)], auto=True).
        pre/post: hingga dua karakter konteks di kiri/kanan deret ini dalam kalimat (untuk aturan 得, 地, 还, 着)."""
        full = pre + t + post
        off = len(pre)
        spans, i = [], 0
        for L in self.pecah(t):
            spans.append([i, t[i:i + L], False])
            i += L
        # erhua: 儿 yang berdiri sendiri menempel ke kata sebelumnya (wánr, bukan wán ér)
        gab = []
        for sp in spans:
            if sp[1] == "儿" and gab and gab[-1][1][-1] not in BUKAN_ERHUA_DEPAN:
                gab[-1][1] += "儿"
                gab[-1][2] = True
            else:
                gab.append(sp)
        units = []
        for i, w, er in gab:
            syls, bawaan = self.word_syls(w[:-1] if er else w)
            syls = list(syls)
            if er:
                syls.append(("r", 5))
            elif len(w) > 1 and w[-1] == "儿" and w not in BUKAN_ERHUA and syls[-1] and syls[-1][0] == "er":
                syls[-1] = ("r", 5)
            if not all(syls):
                bad = "".join(c for c, s in zip(w, syls) if not s)
                flags.append(f"GAGAL baca {bad}")
                syls = [s or ("?", 5) for s in syls]
            if len(w) >= 2 and w[:2] in ULANG_NETRAL:
                syls[1] = (syls[1][0], 5)
            for j in range(len(w) - 1):
                if w[j:j + 2] in NETRAL_2 and syls[j + 1] and syls[j + 1][0] != "r":
                    syls[j + 1] = (syls[j + 1][0], 5)
            for k in bawaan:
                c = w[k]
                pos = off + i + k
                sebelum = full[pos - 1] if pos > 0 else ""
                sesudah = full[pos + 1] if pos + 1 < len(full) else ""
                if c == "得" and sebelum and sesudah in SESUDAH_DE:
                    syls[k] = ("de", 5)
                elif c == "地" and len(w) == 1 and re.match("[" + HAN + "]", sebelum or "x") \
                        and re.match("[" + HAN + "]", sesudah or "x"):
                    syls[k] = ("de", 5)                      # 慢慢地走: partikel keterangan
                elif c == "还" and sesudah in SESUDAH_HUAN:
                    syls[k] = ("huan", 2)
                elif c == "着":
                    if (not sesudah) or sesudah in "了。，！？：；、…不":
                        flags.append("ragu 着 (zhe / zháo)")
                elif c in self.poli:
                    flags.append(f"ragu {c}")
            units.append(dict(c=w, s=syls, auto=True))
        return units


def sandhi(units):
    """Sandhi 不 dan 一 pada suku hasil otomatis, mengikuti nada suku berikutnya (tidak melewati tanda baca)."""
    flat = []
    for u in units:
        if u is None:
            flat.append(None)
            continue
        for k, (c, s) in enumerate(zip(u["c"], u["s"])):
            flat.append((u, k, c, s))
    for idx, it in enumerate(flat):
        if it is None or not it[0]["auto"]:
            continue
        u, k, c, (s, t) = it
        nxt = flat[idx + 1] if idx + 1 < len(flat) else None
        prv = flat[idx - 1] if idx > 0 else None
        nt = nxt[3][1] if nxt else None
        if c == "不" and t == 4 and nt == 4:
            u["s"][k] = (s, 2)
        elif c == "一" and t == 1 and nxt is not None:
            nc = nxt[2]
            pc = prv[2] if prv else ""
            if (pc and pc in ANGKA) or (nc and nc in ANGKA) or (nc and nc in "月日号"):
                continue
            if nt == 4:
                u["s"][k] = (s, 2)
            elif nt in (1, 2, 3):
                u["s"][k] = (s, 4)


def buat_kalimat(A, hanzi_kata, pinyin_kata, kalimat_asli):
    """-> (pinyin kalimat, [penanda])."""
    flags = []
    # label dialog "A：" / "B：" tidak dibaca (tidak ada pinyinnya); hanzi tetap utuh di tempat lain
    kalimat = re.sub(r"(?<![A-Za-z])[A-Z]：", "", kalimat_asli)
    if kalimat != kalimat_asli:
        flags.append("label dialog tidak dibaca")
    kn = kalimat.count(hanzi_kata)
    if kn == 0:
        flags.append("kata utama tidak utuh di kalimat")
    elif kn > 1 and len(hanzi_kata) == 1:
        flags.append(f"kata utama muncul {kn} kali (bacaan otomatis)")
    paksa = kn >= 1 and not (kn > 1 and len(hanzi_kata) == 1)
    bagian = re.split("(" + re.escape(hanzi_kata) + ")", kalimat) if paksa else [kalimat]

    units, off = [], 0
    for bag in bagian:
        if paksa and bag == hanzi_kata:
            try:
                ps = zp.syllables(pinyin_kata, hanzi_kata)
            except Exception:
                flags.append("pinyin kartu tidak terbaca")
                ps = [("?", 5)] * len(hanzi_kata)
            units.append(dict(c=hanzi_kata, s=ps[:len(hanzi_kata)] if len(ps) >= len(hanzi_kata) else ps,
                              auto=False, teks=pinyin_kata))
            off += len(bag)
            continue
        for m in re.finditer("[" + HAN + "]+|[" + PUNCT + "]|[“”\"‘’]|\\s+|[^" + HAN + PUNCT + "“”\"‘’\\s]+", bag):
            tok = m.group(0)
            a = off + m.start()
            if re.fullmatch("[" + HAN + "]+", tok):
                units += A.run_hanzi(tok, flags, kalimat[max(0, a - 2):a], kalimat[a + len(tok):a + len(tok) + 2])
            elif tok in PUNCT:
                units.append(None)
                units.append(dict(punct=tok))
            elif tok.strip() == "" or tok in "“”\"‘’":
                continue
            else:
                units.append(dict(c="", s=[], auto=False, teks=tok))
                flags.append(f"huruf/angka/tanda: {tok}")
        off += len(bag)
    sandhi([u for u in units if u is None or "punct" not in u])
    out = []
    for u in units:
        if u is None:
            continue
        if "punct" in u:
            if out:
                out[-1] += u["punct"]
            else:
                out.append(u["punct"])
            continue
        out.append(u["teks"] if u.get("teks") is not None else gabung_suku(u["s"]))
    teks = " ".join(out)
    # pemeriksaan sendiri: terbaca oleh parser pembuat audio dan jumlah suku kata sama dengan jumlah hanzi
    try:
        n_suku = len(zp.syllables(teks, kalimat_asli))
        n_hanzi = len(re.findall("[" + HAN + "]", kalimat_asli))
        if n_suku != n_hanzi:
            flags.append(f"jumlah suku kata {n_suku} beda dengan hanzi {n_hanzi}")
    except Exception as e:
        flags.append(f"pinyin tidak terbaca parser: {str(e)[:40]}")
    return teks, sorted(set(flags))


def uji_kamus(A):
    salah = tot = 0
    for w, (ph, tn) in A.lex.words.items():
        if w not in A.w:
            continue
        tot += 1
        py = gabung_suku([(A.inv.get((ph[2 * i], ph[2 * i + 1])) or "?", tn[2 * i]) for i in range(len(w))])
        try:
            syl = zp.syllables(py, w)
            ok = len(syl) >= len(w) and all(zp.syl2ph(s) == (ph[2 * i], ph[2 * i + 1]) and (t == tn[2 * i] or tn[2 * i] == 5)
                                            for i, (s, t) in enumerate(syl[:len(w)]))
        except Exception:
            ok = False
        salah += 0 if ok else 1
    print(f"uji bolak-balik: {tot - salah}/{tot} kata cocok ({salah} tidak)")


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--data", required=True)
    ap.add_argument("--model", required=True)
    ap.add_argument("--keluar", required=True)
    ap.add_argument("--tinjau")
    ap.add_argument("--uji-kamus", action="store_true", help="uji bolak-balik tabel pinyin lalu keluar")
    a = ap.parse_args()
    A = Otomatis(a.model)
    if a.uji_kamus:
        uji_kamus(A)
        return
    rows = json.load(open(a.data, encoding="utf-8"))["D"]
    hasil = []
    for r in rows:
        hz, py, kal = r[0], r[1], r[5]
        urut = r[7] if len(r) > 7 and isinstance(r[7], int) else None
        if not kal:
            continue
        p, f = buat_kalimat(A, hz, py, kal)
        hasil.append(dict(n=urut, k=hz, h=kal, p=p, f=f))
    json.dump(hasil, open(a.keluar, "w", encoding="utf-8"), ensure_ascii=False, indent=0)
    ragu = [x for x in hasil if x["f"]]
    print(f"{len(hasil)} kalimat, {len(ragu)} ditandai ragu ({100 * len(ragu) // max(1, len(hasil))}%)")
    if a.tinjau:
        with open(a.tinjau, "w", encoding="utf-8", newline="") as fo:
            w = csv.writer(fo)
            w.writerow(["no", "kata utama", "kalimat", "pinyin otomatis", "penanda", "keputusan", "koreksi pinyin"])
            for x in ragu:
                w.writerow([x["n"], x["k"], x["h"], x["p"], "; ".join(x["f"]), "", ""])


if __name__ == "__main__":
    main()
