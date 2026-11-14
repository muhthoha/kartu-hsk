"""Menambah keluaran durasi ke model ONNX VITS tanpa pustaka onnx (sunting protobuf di tingkat kawat)."""


def _varint(b, i):
    r, s = 0, 0
    while True:
        c = b[i]
        i += 1
        r |= (c & 0x7F) << s
        if not c & 0x80:
            return r, i
        s += 7


def _enc(n):
    out = bytearray()
    while True:
        c = n & 0x7F
        n >>= 7
        if n:
            out.append(c | 0x80)
        else:
            out.append(c)
            return bytes(out)


def fields(b, start, end):
    """Iterasi (nomor_field, tipe_kawat, awal_isi, akhir_isi, awal_field)."""
    i = start
    while i < end:
        f0 = i
        tag, i = _varint(b, i)
        fn, wt = tag >> 3, tag & 7
        if wt == 0:
            _, j = _varint(b, i)
            yield fn, wt, i, j, f0
            i = j
        elif wt == 2:
            ln, i = _varint(b, i)
            yield fn, wt, i, i + ln, f0
            i += ln
        elif wt == 1:
            yield fn, wt, i, i + 8, f0
            i += 8
        elif wt == 5:
            yield fn, wt, i, i + 4, f0
            i += 4
        else:
            raise ValueError("tipe kawat %d" % wt)


def nodes(b):
    g = [(s, e) for fn, wt, s, e, f0 in fields(b, 0, len(b)) if fn == 7][0]
    out = []
    for fn, wt, s, e, f0 in fields(b, g[0], g[1]):
        if fn != 1:
            continue
        n = {"in": [], "out": [], "name": "", "op": ""}
        for f2, w2, s2, e2, _ in fields(b, s, e):
            if f2 == 1:
                n["in"].append(b[s2:e2].decode())
            elif f2 == 2:
                n["out"].append(b[s2:e2].decode())
            elif f2 == 3:
                n["name"] = b[s2:e2].decode()
            elif f2 == 4:
                n["op"] = b[s2:e2].decode()
        out.append(n)
    return out


def add_outputs(b, names):
    """Kembalikan byte model baru dengan tensor `names` sebagai keluaran tambahan graf."""
    for fn, wt, s, e, f0 in fields(b, 0, len(b)):
        if fn == 7:
            extra = b""
            for nm in names:
                vi = b"\x0a" + _enc(len(nm.encode())) + nm.encode()          # ValueInfoProto.name
                extra += b"\x62" + _enc(len(vi)) + vi                        # GraphProto.output (field 12)
            g = b[s:e] + extra
            return b[:f0] + b"\x3a" + _enc(len(g)) + g + b[e:]
    raise ValueError("graf tidak ditemukan")
