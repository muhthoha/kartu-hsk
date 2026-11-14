"""Pinyin bertanda nada -> suku kata -> fonem MeloTTS (inisial + final) + nada, termasuk sandhi nada ketiga.

Dipakai oleh buat_audio_kata.py. Tidak butuh pustaka luar.
"""
import re
import unicodedata

# huruf bertanda nada -> (huruf dasar, nada)
_TM = {}
for _base, _marks in {"a": "āáǎà", "e": "ēéěè", "i": "īíǐì", "o": "ōóǒò", "u": "ūúǔù", "v": "ǖǘǚǜ"}.items():
    for _i, _ch in enumerate(_marks):
        _TM[_ch] = (_base, _i + 1)
_TM["ü"] = ("v", 0)
_TM["ń"] = ("n", 2)
_TM["ň"] = ("n", 3)
_TM["ǹ"] = ("n", 4)
_TM["ḿ"] = ("m", 2)

INITIALS = ["zh", "ch", "sh", "b", "p", "m", "f", "d", "t", "n", "l", "g", "k", "h", "j", "q", "x", "r", "z", "c", "s", "y", "w"]

_Y = {"i": "i", "a": "a", "an": "En", "ang": "ang", "ao": "ao", "e": "E", "in": "in", "ing": "ing", "o": "o",
      "ong": "ong", "ou": "ou", "u": "v", "uan": "van", "ue": "ve", "un": "vn", "ve": "ve"}
_W = {"u": "u", "a": "a", "ai": "ai", "an": "an", "ang": "ang", "ei": "ei", "en": "en", "eng": "eng", "o": "o"}
_ZERO = {"a": "AA", "ai": "AA", "an": "AA", "ang": "AA", "ao": "AA", "e": "EE", "ei": "EE", "en": "EE", "eng": "EE",
         "er": "EE", "o": "OO", "ou": "OO"}
_FINALS = {"a", "o", "e", "ai", "ei", "ao", "ou", "an", "en", "ang", "eng", "ong", "i", "ia", "ie", "iao", "iu", "ian",
           "in", "iang", "ing", "iong", "u", "ua", "uo", "uai", "ui", "uan", "un", "uang", "v", "ve", "van", "vn", "er"}


def syl2ph(s):
    """Suku kata tanpa nada (ü ditulis v) -> (inisial, final) menurut tabel MeloTTS, atau None bila bukan suku kata."""
    if s in _ZERO:
        return (_ZERO[s], s)
    if s in ("ng", "n", "m", "hm", "hng"):      # kata seru 嗯/呣: model tidak punya; dekati dengan "en"
        return ("EE", "en")
    ini = ""
    for i in INITIALS:
        if s.startswith(i):
            ini = i
            break
    if not ini:
        return None
    f = s[len(ini):]
    if not f:
        return None
    if ini == "y":
        return ("y", _Y[f]) if f in _Y else None
    if ini == "w":
        return ("w", _W[f]) if f in _W else None
    if ini in ("zh", "ch", "sh", "r") and f == "i":
        return (ini, "ir")
    if ini in ("z", "c", "s") and f == "i":
        return (ini, "i0")
    if ini in ("j", "q", "x"):
        f = {"u": "v", "uan": "van", "ue": "ve", "un": "vn"}.get(f, f)
        if f in ("a", "o", "e", "ai", "ei", "ao", "ou", "an", "en", "ang", "eng", "ong", "ua", "uo", "uai", "ui", "uang", "er"):
            return None
    if f == "ue":
        f = "ve"
    if f not in _FINALS or f == "er":
        return None
    return (ini, f)


def _norm(p):
    return unicodedata.normalize("NFC", p).lower().replace("’", "'").replace("ɡ", "g")


def _letters(tok):
    """'zhǎng' -> ([huruf dasar...], [nada per huruf atau 0])."""
    base, tone = [], []
    for ch in tok:
        if ch in _TM:
            b, t = _TM[ch]
            base.append(b)
            tone.append(t)
        else:
            base.append(ch)
            tone.append(0)
    return base, tone


def _split(tok, longgar=False):
    """Pecah satu potong huruf (tanpa spasi/apostrof) menjadi suku kata [(suku, nada)].

    Aturan ejaan pinyin: suku kata yang diawali a/o/e di tengah kata selalu didahului apostrof, jadi di dalam satu potong
    hanya suku pertama yang boleh berawalan a/o/e. 'r' di akhir sesudah suku kata lengkap = erhua.
    Mengembalikan semua pemecahan yang sah (biasanya satu); pemanggil memilih yang cocok dengan jumlah hanzi.
    """
    base, tone = _letters(tok)
    n = len(base)
    res = []

    def rec(i, acc):
        if i == n:
            res.append(list(acc))
            return
        if base[i] == "r" and acc and (i == n - 1 or base[i + 1] not in "aeiouv") and acc[-1][0] != "er":
            acc.append(("r", 5))           # erhua
            rec(i + 1, acc)
            acc.pop()
        for L in range(min(6, n - i), 0, -1):
            s = "".join(base[i:i + L])
            if i > 0 and s[0] in "aoe" and not longgar:
                continue
            ts = [t for t in tone[i:i + L] if t]
            if len(ts) > 1:
                continue
            if syl2ph(s) is None:
                continue
            acc.append((s, ts[0] if ts else 5))
            rec(i + L, acc)
            acc.pop()

    rec(0, [])
    return res


class PinyinError(ValueError):
    pass


def parse(pinyin, hanzi=None):
    """Pinyin situs -> daftar potongan: ('syl', [(suku, nada), ...]) per kata (dipisah spasi) atau ('pause', tanda).

    Tanda '/' (dua bacaan) dan tanda baca menjadi jeda. Erhua ditulis sebagai suku ("r", 5).
    Bila pemecahan suku kata ambigu dan hanzi diketahui, dipilih yang jumlah sukunya sama dengan jumlah hanzi.
    """
    import itertools
    p = _norm(pinyin)
    p = p.replace("/", " , ")
    p = re.sub(r"[\"“”‘·]", " ", p)
    p = p.replace("-", " ")
    toks = []          # ('pause', x) atau ('alts', [[alternatif pemecahan] per bagian apostrof])
    for tok in re.findall(r"[a-z" + "".join(_TM) + r"']+|[,.?!;:，。？！；：、…]|\S", p):
        if tok in ",;:，；：、":
            toks.append(("pause", ","))
        elif tok in ".。…":
            toks.append(("pause", "."))
        elif tok in "?？":
            toks.append(("pause", "?"))
        elif tok in "!！":
            toks.append(("pause", "!"))
        elif re.match(r"[a-z" + "".join(_TM) + r"']+$", tok):
            parts = []
            for part in tok.split("'"):
                if not part:
                    continue
                c = _split(part)
                if not c:
                    raise PinyinError(f"tidak bisa dipecah: {part!r} dalam {pinyin!r}")
                c.sort(key=len)          # utamakan suku paling sedikit (pencocokan terpanjang)
                parts.append(c)
            if parts:
                toks.append(("alts", parts))
        else:
            raise PinyinError(f"karakter tak dikenal {tok!r} dalam {pinyin!r}")
    slots = [alts for k, v in toks if k == "alts" for alts in v]
    pick = [alts[0] for alts in slots]
    n_h = len(re.findall(r"[\u3400-\u9fff]", hanzi)) if hanzi is not None and "/" not in pinyin else None
    if n_h and sum(len(x) for x in pick) != n_h:
        ok = False
        for combo in itertools.islice(itertools.product(*slots), 5000):
            if sum(len(part) for part in combo) == n_h:
                pick, ok = list(combo), True
                break
        if not ok:
            # ejaan tanpa apostrof (mis. "fǎnér"): izinkan suku berawalan a/o/e di tengah kata
            slots2 = []
            for k, v in toks:
                if k == "alts":
                    for part in v:
                        raw = part[0]
                        slots2.append(part)
            parts_raw = [x for tok in re.findall(r"[a-z" + "".join(_TM) + r"']+", p) for x in tok.split("'") if x]
            slots2 = [sorted(_split(x, longgar=True), key=len) for x in parts_raw]
            if len(slots2) == len(slots):
                for combo in itertools.islice(itertools.product(*slots2), 5000):
                    if sum(len(part) for part in combo) == n_h:
                        pick = list(combo)
                        break
    it = iter(pick)
    out = []
    for k, v in toks:
        if k == "pause":
            out.append((k, v))
        else:
            out.append(("syl", [s for _ in v for s in next(it)]))
    return out


def syllables(pinyin, hanzi=None):
    return [s for k, v in parse(pinyin, hanzi) if k == "syl" for s in v]


def key(pinyin):
    """Kunci berkas audio: pinyin dinormalkan (huruf kecil, NFC, tanpa spasi berlebih). Harus sama dengan kunci di index.html."""
    p = unicodedata.normalize("NFC", pinyin).lower()
    p = re.sub(r"\s+", " ", p).strip()
    return p
