# Validazione degli stimatori di riferimento (collisione, compressione, LRS) contro l'output ufficiale di ea_non_iid.
# Uso:  python3 validazione_90b.py        (richiede numpy)
# Il flusso r603.json e' incluso; gli altri (cic100000.bin, AM_..._100000.bin, e i tre da 1.000.000 bit) si ricreano
# con estrai_lsb.py dai WAV originali e si mettono in flussi/: quelli assenti vengono saltati e il conteggio lo dice.
import json, os, sys
QUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, QUI)
from est90b_ref import collision, compression, lrs
FL = os.path.join(QUI, 'flussi')
ok = tot = saltati = 0
def carica(f):
    p = os.path.join(FL, f)
    if not os.path.exists(p): return None
    if f.endswith('.json'): return list(map(int, json.load(open(p))))
    return list(open(p, 'rb').read())
def conf(nome, mio, uff, tol):
    global ok, tot
    tot += 1; e = abs(mio - uff) <= tol; ok += e
    print(f"   {nome:16s} mio {mio:.16g}  uff {uff:.16g}  diff {mio-uff:+.2e}  {'OK' if e else 'NO'}")
VETT = [  # (file, collisione, compressione, LRS) con i valori stampati da ea_non_iid
 ("r603.json", dict(mean=2.514644351464435, sigma=0.50083436589185504, p=0.68547633415680098, H=0.544821), None,
               dict(u=6, v=16, p_hat=0.50162673951396098, p_u=0.55411794416325535, H=0.851735)),
 ("cic100000.bin", dict(mean=2.5065169440545416, sigma=0.4999637935141521, p=0.5, H=1.0),
               dict(mean=5.2208977821568299, sigma=1.0121602474939126, p=0.039460210841719356, H=0.777243),
               dict(u=13, v=29, p_hat=0.49998304217282302, p_u=0.50405580626586189, H=0.988345)),
 ("AM_rec20260921_105450_100000.bin", dict(mean=2.5010754839677856, sigma=0.50000509624949352, p=0.55179577364213839, H=0.857794),
               dict(mean=5.203084094767533, sigma=1.0267620947535732, p=0.051742748853928267, H=0.712083),
               dict(u=13, v=29, p_hat=0.50024353369671452, p_u=0.50431629730899539, H=0.987599)),
 ("AM_rec20260921_105450_1000000.bin", dict(H=0.900699), dict(H=0.819077), dict(H=0.994365)),
 ("radioFMAM_20260920_095010_1000000.bin", dict(H=0.932092), dict(H=0.867979), dict(H=0.994460)),
 ("cic1000000.bin", dict(H=0.916045), dict(H=0.845363), dict(H=0.996300)),
]
for f, uc, ucomp, ul in VETT:
    bits = carica(f)
    if bits is None:
        print(f"== {f}: flusso assente, saltato"); saltati += 1; continue
    print("==", f)
    c = collision(bits)
    for k, tolk in (("mean", 1e-12), ("sigma", 1e-12), ("p", 1e-12)):
        if k in uc: conf("collisione " + k, c[{'mean': 'mean', 'sigma': 'sigma', 'p': 'p'}[k]], uc[k], tolk)
    conf("collisione H", round(c['H'], 6), uc['H'], 5e-7)
    if ucomp:
        r = compression(bits)
        for k, tolk in (("mean", 1e-12), ("sigma", 1e-10), ("p", 1e-9)):
            if k in ucomp: conf("compress. " + k, r[k], ucomp[k], tolk)
        conf("compress. H", round(r['H'], 6), ucomp['H'], 5e-7)
    l = lrs(bits)
    for k, tolk in (("u", 0), ("v", 0), ("p_hat", 1e-12), ("p_u", 1e-12)):
        if k in ul: conf("LRS " + k, l[k], ul[k], tolk)
    conf("LRS H", round(l['H'], 6), ul['H'], 5e-7)
print(f"\nCONFRONTI RIUSCITI: {ok} su {tot} eseguiti ({saltati} flussi saltati perche' assenti)")
sys.exit(0 if ok == tot else 1)
