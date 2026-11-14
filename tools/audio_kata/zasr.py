"""Pengenal suara SenseVoice (ONNX) dengan fitur fbank gaya Kaldi dari numpy. Dipakai hanya untuk MEMERIKSA audio buatan."""
import os

import numpy as np
from scipy.signal import resample_poly


def _mel(f):
    return 1127.0 * np.log(1.0 + f / 700.0)


def _mel_banks(n_bins=80, n_fft=512, sr=16000, low=20.0, high=8000.0):
    n_f = n_fft // 2
    ml, mh = _mel(low), _mel(high)
    d = (mh - ml) / (n_bins + 1)
    fm = _mel(np.arange(n_f) * sr / n_fft)
    W = np.zeros((n_bins, n_f + 1), dtype=np.float32)
    for b in range(n_bins):
        l, c, r = ml + b * d, ml + (b + 1) * d, ml + (b + 2) * d
        up = (fm - l) / (c - l)
        dn = (r - fm) / (r - c)
        w = np.where((fm > l) & (fm <= c), up, np.where((fm > c) & (fm < r), dn, 0.0))
        W[b, :n_f] = w
    return W


_W = _mel_banks()
_WIN = (0.54 - 0.46 * np.cos(2 * np.pi * np.arange(400) / 399)).astype(np.float32)


def fbank(x16):
    x = x16.astype(np.float32) * 32768.0
    if len(x) < 400:
        x = np.pad(x, (0, 400 - len(x)))
    n = 1 + (len(x) - 400) // 160
    idx = np.arange(400)[None, :] + 160 * np.arange(n)[:, None]
    fr = x[idx]
    fr = fr - fr.mean(axis=1, keepdims=True)
    fr = np.concatenate([fr[:, :1] * (1 - 0.97), fr[:, 1:] - 0.97 * fr[:, :-1]], axis=1)
    fr = fr * _WIN
    sp = np.abs(np.fft.rfft(fr, 512, axis=1)) ** 2
    return np.log(np.maximum(sp @ _W.T, 1.1920929e-07)).astype(np.float32)


def lfr(f, m=7, n=6):
    T = f.shape[0]
    f = np.concatenate([np.repeat(f[:1], (m - 1) // 2, axis=0), f], axis=0)
    out = []
    t_out = int(np.ceil(T / n))
    for i in range(t_out):
        seg = f[i * n:i * n + m]
        if seg.shape[0] < m:
            seg = np.concatenate([seg, np.repeat(f[-1:], m - seg.shape[0], axis=0)], axis=0)
        out.append(seg.reshape(-1))
    return np.stack(out)


class ASR:
    def __init__(self, model_dir, threads=2):
        import onnxruntime as ort
        so = ort.SessionOptions()
        so.intra_op_num_threads = threads
        so.inter_op_num_threads = 1
        self.sess = ort.InferenceSession(os.path.join(model_dir, "model.int8.onnx"), so, providers=["CPUExecutionProvider"])
        m = self.sess.get_modelmeta().custom_metadata_map
        self.neg_mean = np.array([float(v) for v in m["neg_mean"].split(",")], dtype=np.float32)
        self.inv_std = np.array([float(v) for v in m["inv_stddev"].split(",")], dtype=np.float32)
        self.zh = int(m["lang_zh"])
        self.noitn = int(m["without_itn"])
        self.tok = {}
        with open(os.path.join(model_dir, "tokens.txt"), encoding="utf-8") as f:
            for line in f:
                a = line.rstrip("\n").rsplit(" ", 1)
                if len(a) == 2:
                    self.tok[int(a[1])] = a[0]

    def text(self, y, sr):
        if sr != 16000:
            g = np.gcd(sr, 16000)
            y = resample_poly(y, 16000 // g, sr // g)
        # sedikit hening di depan dan belakang supaya kata pendek terbaca utuh
        y = np.concatenate([np.zeros(3200, np.float32), y.astype(np.float32), np.zeros(4800, np.float32)])
        f = (lfr(fbank(y)) + self.neg_mean) * self.inv_std
        lg = self.sess.run(None, {"x": f[None].astype(np.float32), "x_length": np.array([f.shape[0]], dtype=np.int32),
                                  "language": np.array([self.zh], dtype=np.int32),
                                  "text_norm": np.array([self.noitn], dtype=np.int32)})[0][0]
        ids = lg.argmax(axis=1)
        out, prev = [], -1
        for i in ids:
            if i != prev and i != 0:
                out.append(int(i))
            prev = i
        s = "".join(self.tok.get(i, "") for i in out)
        import re
        s = re.sub(r"<\|[^|]*\|>", "", s).replace("▁", " ").strip()
        return s
