"""
Stimatori SP 800-90B (binari, 1 bit per campione) - implementazione di riferimento in Python.
Collisione (6.3.2), Compressione (6.3.4) e LRS (6.3.7), scritti da zero sulla descrizione della norma e
validati contro l'output ufficiale di ea_non_iid (vedi validazione_90b.py).
"""
import math
import numpy as np

Z99 = 2.5758293035489        # coefficiente della norma per il 99%

# ---------------------------------------------------------------- Collisione (6.3.2)
def collision(bits):
    s = bits; L = len(s)
    ts = []; i = 0
    while i < L - 1:
        if s[i] == s[i+1]:
            t = 2
        elif i + 2 < L:
            t = 3
        else:
            break
        ts.append(t); i += t
    v = len(ts)
    mean = sum(ts) / v
    sigma = math.sqrt(sum((t - mean)**2 for t in ts) / (v - 1))
    mean_lo = mean - Z99 * sigma / math.sqrt(v)
    # per bit: E = 2 + 2pq  ->  pq = (mean_lo - 2)/2
    pq = (mean_lo - 2.0) / 2.0
    if pq >= 0.25:
        p = 0.5
    elif pq <= 0:
        p = 1.0
    else:
        p = (1.0 + math.sqrt(1.0 - 4.0*pq)) / 2.0
    return {"v": v, "mean": mean, "sigma": sigma, "p": p, "H": -math.log2(p)}

# ---------------------------------------------------------------- Compressione (6.3.4)
def compression(bits, b=6, d=1000):
    L = len(bits)
    nblk = L // b
    if nblk <= d + 1:                       # servono almeno due blocchi di test (divisione per v-1)
        return None
    arr = np.asarray(bits[:nblk*b], dtype=np.int64).reshape(nblk, b)
    blk = (arr * (1 << np.arange(b-1, -1, -1))).sum(axis=1)
    last = {}
    for i in range(d):                      # inizializzazione: posizione dell'ultima occorrenza (1-based)
        last[int(blk[i])] = i + 1
    A = np.empty(nblk - d, dtype=np.float64)
    for i in range(d, nblk):
        k = int(blk[i]); pos = i + 1
        A[i-d] = pos - last[k] if k in last else pos
        last[k] = pos
    x = np.log2(A); N = len(x)
    mean = x.mean()
    c = 0.5907                                  # costante della norma per b = 6 (non la formula in N)
    sigma = c * math.sqrt((x**2).sum()/(N-1) - mean**2)
    mean_lo = mean - Z99 * sigma / math.sqrt(N)
    # E_p come da norma; q = (1-p)/(2^b - 1)
    t = np.arange(d+1, nblk+1, dtype=np.float64)
    logs = np.log2(np.arange(1, nblk+1, dtype=np.float64))
    def G(z):
        # sum_{u=1}^{t-1} log2(u) z^2 (1-z)^{u-1} + log2(t) z (1-z)^{t-1}
        w = (1.0 - z) ** np.arange(0, nblk, dtype=np.float64)       # (1-z)^{u-1}, u=1..nblk
        cs = np.concatenate(([0.0], np.cumsum(logs * w)))            # cs[k] = sum_{u=1}^{k}
        ti = t.astype(np.int64)
        inner = z*z * cs[ti-1]
        last_term = logs[ti-1] * z * w[ti-1]
        return (inner + last_term).sum() / N
    def E(p):
        q = (1.0 - p) / (2**b - 1)
        return G(p) + (2**b - 1) * G(q)
    lo, hi = 2.0**(-b), 1.0
    if E(lo) < mean_lo:                      # nessuna soluzione: distribuzione uniforme
        p = lo
    else:
        for _ in range(200):
            mid = (lo + hi) / 2
            if E(mid) > mean_lo: lo = mid
            else: hi = mid
        p = (lo + hi) / 2
    return {"nblk": nblk, "N": N, "mean": mean, "sigma": sigma, "p": p, "H": -math.log2(p)/b}


# ---------------------------------------------------------------- LRS (6.3.7)
from collections import Counter

def lrs(bits):
    """u = lunghezza minima per cui la tupla piu' frequente compare meno di 35 volte;
    v = lunghezza massima per cui qualche tupla compare almeno 2 volte;
    per W in u..v: P_W = somma C(c,2) / C(L-W+1,2), poi radice W-esima; si prende il massimo."""
    s = bytes(bits); L = len(s)
    def counts(W):
        return Counter(s[i:i+W] for i in range(L - W + 1))
    u = 1
    while max(counts(u).values()) >= 35:
        u += 1
    v = u
    while max(counts(v + 1).values()) >= 2:
        v += 1
    P = {}
    for W in range(u, v + 1):
        c = counts(W); tot = L - W + 1
        coll = sum(math.comb(x, 2) for x in c.values() if x >= 2)
        P[W] = (coll / math.comb(tot, 2)) ** (1.0 / W)
    p_hat = max(P.values())
    p_u = min(1.0, p_hat + Z99 * math.sqrt(p_hat * (1 - p_hat) / (L - 1)))
    return {"u": u, "v": v, "p_hat": p_hat, "p_u": p_u, "H": -math.log2(p_u)}
