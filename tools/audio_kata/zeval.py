"""Pemeriksaan otomatis: sintesis kata lalu kenali lagi dengan SenseVoice dan bandingkan bacaannya."""
import collections
import re

import zpinyin as zp


def build_readings(lex):
    rd = collections.defaultdict(set)      # hanzi -> {(inisial, final)}
    rt = collections.defaultdict(set)      # hanzi -> {(inisial, final, nada)}
    for w, (ph, tn) in lex.words.items():
        if len(ph) == 2 * len(w) and all("㐀" <= c <= "鿿" for c in w):
            for i, c in enumerate(w):
                rd[c].add((ph[2 * i], ph[2 * i + 1]))
                rt[c].add((ph[2 * i], ph[2 * i + 1], tn[2 * i]))
    return rd, rt


def expected(hanzi, pinyin):
    """Daftar (inisial, final, nada dasar) yang diharapkan; erhua dilewati."""
    out = []
    for k, v in zp.parse(pinyin, hanzi):
        if k != "syl":
            continue
        for s, t in v:
            if s == "r":
                continue
            a, b = zp.syl2ph(s)
            out.append((a, b, t))
    return out


def compare(exp, text, rd, rt):
    """-> (cocok_suku, cocok_nada). Teks hasil pengenal dibandingkan per karakter dengan bacaan yang mungkin."""
    ch = [c for c in re.findall(r"[㐀-鿿]", text) if c != "儿" or len(re.findall(r"[㐀-鿿]", text)) == len(exp)]
    if len(ch) != len(exp):
        ch2 = [c for c in re.findall(r"[㐀-鿿]", text) if c != "儿"]
        if len(ch2) != len(exp):
            return False, False
        ch = ch2
    ok_s = all((a, b) in rd.get(c, ()) for c, (a, b, t) in zip(ch, exp))
    ok_t = ok_s and all(t == 5 or (a, b, t) in rt.get(c, ()) for c, (a, b, t) in zip(ch, exp))
    return ok_s, ok_t
