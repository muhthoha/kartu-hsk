"""Hash kunci audio kata; harus identik dengan fungsi kaH() di index.html."""
M = 0xffffffff
def _imul(a, b):
    return ((a & M) * (b & M)) & M
def _b36(n):
    d = '0123456789abcdefghijklmnopqrstuvwxyz'
    if n == 0: return '0'
    o = ''
    while n: n, r = divmod(n, 36); o = d[r] + o
    return o
def kah(s):
    a, b = 0xdeadbeef, 0x41c6ce57
    u = s.encode('utf-16-le')
    for i in range(0, len(u), 2):
        c = u[i] | (u[i + 1] << 8)
        a = _imul(a ^ c, 2654435761); b = _imul(b ^ c, 1597334677)
    a = (_imul(a ^ (a >> 16), 2246822507) ^ _imul(b ^ (b >> 13), 3266489909)) & M
    b = (_imul(b ^ (b >> 16), 2246822507) ^ _imul(a ^ (a >> 13), 3266489909)) & M
    return _b36(4294967296 * (2097151 & b) + (a & M))
