"""Pelacak nada dasar (F0) sederhana dengan autokorelasi, untuk memeriksa kontur nada suku kata tunggal."""
import numpy as np
from scipy.signal import resample_poly


def track(y, sr, fmin=110.0, fmax=450.0):
    g = np.gcd(sr, 16000)
    y = resample_poly(y, 16000 // g, sr // g).astype(np.float64)
    sr = 16000
    win, hop = int(0.04 * sr), int(0.01 * sr)
    if len(y) < win:
        return np.array([]), np.array([])
    n = 1 + (len(y) - win) // hop
    w = np.hanning(win)
    lo, hi = int(sr / fmax), int(sr / fmin)
    e_all = np.array([np.sqrt((y[i * hop:i * hop + win] ** 2).mean()) for i in range(n)])
    e_ref = np.percentile(e_all, 90) + 1e-9
    f0 = np.zeros(n)
    for i in range(n):
        fr = y[i * hop:i * hop + win]
        fr = (fr - fr.mean()) * w
        if e_all[i] < 0.08 * e_ref:
            continue
        sp = np.fft.rfft(fr, 2048)
        r = np.fft.irfft(np.abs(sp) ** 2)[:hi + 2]
        wr = np.fft.irfft(np.abs(np.fft.rfft(w, 2048)) ** 2)[:hi + 2]
        r = r / (wr / wr[0] + 1e-9)
        if r[0] <= 0:
            continue
        r = r / r[0]
        k = lo + int(np.argmax(r[lo:hi + 1]))
        if r[k] > 0.5:
            # interpolasi parabola
            a, b, c = r[k - 1], r[k], r[k + 1]
            den = a - 2 * b + c
            off = 0.5 * (a - c) / den if abs(den) > 1e-9 else 0.0
            f0[i] = sr / (k + off)
    t = np.arange(n) * hop / sr
    return t, f0


def contour(y, sr):
    """-> (awal, tengah, akhir, min, rata2) dalam semiton terhadap 200 Hz, atau None bila bagian bersuara terlalu pendek."""
    t, f = track(y, sr)
    v = f[f > 0]
    if len(v) < 6:
        return None
    med = np.median(v)
    v = v[(v > med / 1.8) & (v < med * 1.8)]          # buang lompatan oktaf
    if len(v) < 6:
        return None
    st = 12 * np.log2(v / 200.0)
    k = max(2, len(st) // 4)
    return (float(st[:k].mean()), float(st[len(st) // 2 - k // 2:len(st) // 2 + (k + 1) // 2].mean()), float(st[-k:].mean()),
            float(st.min()), float(st.mean()), len(st))
