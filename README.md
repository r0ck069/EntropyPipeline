# Entropy Extraction Pipeline — Peres + Toeplitz

Strumento didattico **standalone**, **offline**, **senza dipendenze esterne** per
sperimentare un pipeline completo di *entropy conditioning*: raccolta di bit grezzi →
stima di min-entropia (in stile NIST SP 800-90B) → estrazione del bias (Peres/von Neumann
Extractor) → hashing universale (Toeplitz, GF(2), con bound del Leftover Hash Lemma) →
output finale (doppio SHA-256, opzionalmente SHAKE256).
Nato da un idea riflettendo su caso COLDCARD di agosto 2026, sviluppare un metodo alternativo 
con strumenti casalinghi e matematica ,senza avere pretese di uso reale. Solo per usi didattici.

Un solo file HTML. Nessun server, nessuna build, nessuna dipendenza da CDN o pacchetti
npm. Apri `entropy_pipeline.html` in un browser moderno (Firefox, Chrome, ecc.) e funziona
— pensato in particolare per l'uso offline su una sessione live di Linux (es. Ubuntu MATE
Live + Firefox ), dove non è necessaria una connessione a internet.

![status](https://img.shields.io/badge/status-didattico-orange)
![license](https://img.shields.io/badge/license-MIT-blue)
![dependencies](https://img.shields.io/badge/dipendenze-zero-brightgreen)

---

## ⚠️ Avvertenza — leggere prima dell'uso

**Questo strumento non è un generatore di chiavi crittografiche di livello produzione.**

È un dimostratore didattico/di verifica dei passaggi di un pipeline di estrazione entropia.
Gira interamente nel browser dell'utente: nessun controllo su swap/paging della memoria,
nessuna protezione da estensioni del browser o da un ambiente compromesso, e il margine di
sicurezza matematico (Leftover Hash Lemma) può essere abbassato con conferma esplicita
quando l'input di entropia grezza è limitato. È stato costruito con particolare attenzione
al rigore (vedi sezione [Audit e limiti noti](#audit-e-limiti-noti) più sotto e il
[CHANGELOG](CHANGELOG.md) per la cronologia completa dei bug trovati e corretti), ma resta
uno strumento per **capire, sperimentare e validare il processo** — non l'ultimo anello
della catena per chiavi che contano davvero.

## Indice

- [Perché esiste](#perché-esiste)
- [Funzionalità](#funzionalità)
- [Come si usa](#come-si-usa)
- [Struttura del repository](#struttura-del-repository)
- [Fondamenti tecnici](#fondamenti-tecnici)
- [Audit e limiti noti](#audit-e-limiti-noti)
- [Autotest](#autotest)
- [Contribuire](#contribuire)
- [Licenza](#licenza)

## Perché esiste

Molti strumenti di "entropy combining" per uso hobbistico o didattico trattano la
generazione di numeri casuali come una scatola nera. Questo progetto fa l'opposto: rende
esplicito e ispezionabile ogni singolo passaggio matematico — dalla stima di quanta vera
entropia contengono i dati grezzi, fino all'output finale — così chi lo usa può vedere
*perché* un certo output è considerato affidabile (o non lo è), invece di limitarsi a
premere un pulsante "genera".

## Funzionalità

- **Input manuale, multi-sorgente**: da 1 a 4 sorgenti indipendenti di bit grezzi (hex o
  binario), fornite dall'utente da strumenti esterni (TRNG hardware, `/dev/hwrng`, ecc.).
  Il tool non genera né simula mai entropia lato browser.
- **Stima di min-entropia in stile SP 800-90B**: Most Common Value (MCV) e Markov
  (ordine-1) con limite di confidenza superiore di Clopper-Pearson al 99%, più t-Tuple e
  Longest Repeated Substring (LRS) per rilevare strutture periodiche di ordine superiore.
  La min-entropia finale è il minimo fra tutti gli stimatori applicabili.
- **Health test retrospettivi**: Repetition Count Test (RCT) e Adaptive Proportion Test
  (APT), per intercettare run patologici o drift locale in una sorgente.
- **Controllo di correlazione multi-lag** (±8 posizioni) fra sorgenti, non solo bit
  allineati alla stessa posizione.
- **Peres Extractor** (variante ricorsiva del von Neumann Extractor) con verifica di
  conservazione della massa ad ogni esecuzione.
- **Toeplitz Hashing su GF(2)** con seed generato automaticamente da timestamp CPU
  (unicità/audit) + CSPRNG del browser (sicurezza), espanso via SHA-256 in counter-mode.
- **Vincolo di sicurezza a due livelli** (Leftover Hash Lemma): margine standard (160 bit,
  distanza statistica ≤2⁻⁸⁰) o ridotto (32 bit, ≤2⁻¹⁶, con conferma esplicita) quando
  l'input non basta per il livello standard.
- **Batteria di test statistici NIST-style** (Frequency, Runs, Longest Run, Serial,
  Approximate Entropy), ciascuno calcolato con due metodi numerici indipendenti per il
  controllo incrociato, applicati sia pre- che post-estrazione.
- **Output finale**: doppio SHA-256 (schema Bitcoin-style) e, in opzione, SHAKE256 a
  lunghezza di output variabile — implementazione JS pura di Keccak-f[1600], perché
  `crypto.subtle` del browser non supporta nativamente SHAKE256.
- **Suite di autotest all'avvio**: conservazione di massa, coerenza Toeplitz contro
  un'implementazione indipendente, vettori di test ufficiali SHA-256/SHAKE256,
  auto-consistenza statistica. Se qualcosa fallisse qui, è una regressione nel codice.

## Come si usa

1. Scarica `entropy_pipeline.html` (unico file necessario).
2. Aprilo in un browser moderno — non serve alcuna installazione o connessione a internet.
3. Segui le 5 fasi mostrate nella pagina, in ordine.

Istruzioni dettagliate passo-passo: [ISTRUZIONI.md](ISTRUZIONI.md).

## Struttura del repository

```
.
├── entropy_pipeline.html   # Lo strumento (unico file necessario per l'uso)
├── ISTRUZIONI.md           # Guida all'uso passo-passo
├── CHANGELOG.md            # Cronologia dettagliata di tutte le build e i bug corretti
├── CONTRIBUTING.md         # Linee guida per contribuire
├── LICENSE                 # Licenza MIT
└── README.md               # Questo file
```

## Fondamenti tecnici

| Passaggio | Tecnica | Riferimento |
|---|---|---|
| Stima entropia | MCV, Markov (ordine-1), t-Tuple, LRS — con limite di confidenza Clopper-Pearson 99% | NIST SP 800-90B |
| Health test | Repetition Count Test, Adaptive Proportion Test | NIST SP 800-90B §4.4 |
| Estrazione bias | Peres Extractor (variante ricorsiva del von Neumann Extractor) | Peres, 1992 |
| Hashing universale | Toeplitz matrix hashing su GF(2) | Toeplitz-hashing / universal hashing |
| Bound di sicurezza | Leftover Hash Lemma | Impagliazzo–Levin–Luby, 1989 |
| Test statistici | Frequency, Runs, Longest Run, Serial, Approximate Entropy | NIST SP 800-22 (versioni semplificate) |
| Output finale | SHA-256 (doppio), SHAKE256 (XOF) | FIPS 180-4, FIPS 202 |

## Audit e limiti noti

Questo progetto è nato da un processo di revisione conversazionale iterativo, in cui sono
stati trovati e corretti diversi bug reali nel nucleo matematico/crittografico — inclusi un
errore di contabilità nel Peres Extractor, un bound del Leftover Hash Lemma con unità di
misura sbagliate, una matrice di Hankel scambiata per una matrice di Toeplitz, un
cross-check statistico rotto, un gate di sicurezza diventato una tautologia e, nell'audit
più recente, un riferimento numerico errato nel rapporto di estrazione del Peres Extractor
(25% invece del corretto 1/3), un off-by-one nell'Adaptive Proportion Test e un limite di
ricerca artificiale nello stimatore Longest Repeated Substring. Ogni bug è stato riprodotto
con un caso di test costruito ad-hoc prima di essere corretto, e verificato senza
regressioni tramite la suite di autotest. La cronologia completa, onesta e dettagliata è nel
[CHANGELOG.md](CHANGELOG.md) — vale la pena leggerla prima di fidarsi ciecamente dello
strumento.

**Limiti architetturali che nessuna correzione di bug elimina:**
- Gira in un browser: nessun controllo su swap/paging della memoria, nessuna protezione
  `mlock`, il garbage collector del motore JS gestisce i bit "segreti" senza alcun
  controllo dell'utente.
- La stima di min-entropia dipende da un campione statico incollato manualmente — non
  sostituisce un health test in tempo reale su hardware fisico.
- I test statistici su un output di poche centinaia di bit hanno potenza limitata: un
  "PASS" è indicativo, non probante.
- Il test Serial (SP 800-22) implementato è in realtà un singolo chi-quadro sulle coppie di
  bit, non il vero test ufficiale a due statistiche; né Serial né ApproxEntropy usano
  l'estensione ciclica del campione richiesta dalla specifica — semplificazioni dichiarate,
  non conformità certificata.

## Autotest

Ad ogni caricamento della pagina, un pannello dedicato esegue automaticamente:
- conservazione di massa del Peres Extractor su input casuali;
- coerenza del Toeplitz hashing contro una seconda implementazione scritta con un percorso
  di codice indipendente (diagonali esplicite, non la stessa formula confrontata con se
  stessa);
- vettori di test ufficiali per SHA-256 e SHAKE256;
- auto-consistenza della funzione beta incompleta (Clopper-Pearson);
- coerenza fra i due metodi indipendenti di calcolo di erfc.

Se uno di questi autotest fallisse, significherebbe una regressione nel codice: non
fidarsi dei risultati della pipeline finché non è risolto.

## Contribuire

Vedi [CONTRIBUTING.md](CONTRIBUTING.md). Segnalazioni di bug, correzioni matematiche e
miglioramenti alla suite di autotest sono particolarmente benvenuti — la storia di questo
progetto dimostra che ce n'è sempre bisogno.

## Licenza

Distribuito sotto licenza MIT — vedi [LICENSE](LICENSE).

app consigliate per la raccolta dei campioni, rode reporter, sensor logger.
