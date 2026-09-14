# Entropy Extraction Pipeline — Peres + Toeplitz

> ⚠ **v2.0.0-beta2 — BETA non ancora pubblicata su GitHub.** Contiene funzionalità nuove
> non ancora sottoposte ad audit indipendente da terzi (sono state però verificate con una
> suite di test rigorosa e reale — vedi `CHANGELOG.md`). Vedi anche `SECURITY-NOTES.md` per
> i principi di design. Non usare per nulla che conti davvero finché non è stata verificata
> da un revisore indipendente.

Strumento didattico **standalone**, **offline**, **senza dipendenze esterne** per
sperimentare un pipeline completo di *entropy conditioning*: raccolta di bit grezzi →
stima di min-entropia (in stile NIST SP 800-90B) → estrazione del bias (Peres/von Neumann
Extractor) → hashing universale (Toeplitz, GF(2), con bound del Leftover Hash Lemma) →
output finale (doppio SHA-256, opzionalmente SHAKE256).
Nato da un'idea riflettendo sul caso COLDCARD di agosto 2026, sviluppare un metodo alternativo
con strumenti casalinghi e matematica, senza avere pretese di uso reale. Solo per usi didattici.

Un solo file HTML. Nessun server, nessuna build, nessuna dipendenza da CDN o pacchetti
npm. Apri `entropy_pipeline.html` in un browser moderno (Firefox, Chrome, ecc.) e funziona
— pensato in particolare per l'uso offline su una sessione live di Linux (es. Ubuntu MATE
Live + Firefox), dove non è necessaria una connessione a internet.

---

## ⚠️ Avvertenza — leggere prima dell'uso

**Questo strumento non è un generatore di chiavi crittografiche di livello produzione.**

È un dimostratore didattico/di verifica dei passaggi di un pipeline di estrazione entropia.
Gira interamente nel browser dell'utente: nessun controllo su swap/paging della memoria,
nessuna protezione da estensioni del browser o da un ambiente compromesso, e il margine di
sicurezza matematico (Leftover Hash Lemma) può essere abbassato con conferma esplicita
quando l'input di entropia grezza è limitato. È stato costruito con particolare attenzione
al rigore (vedi `AUDIT-NOTES.md` per il dettaglio completo e `CHANGELOG.md` per la
cronologia di tutti i bug trovati e corretti), ma resta uno strumento per **capire,
sperimentare e validare il processo** — non l'ultimo anello della catena per chiavi che
contano davvero.

## Indice

- [Perché esiste](#perché-esiste)
- [Funzionalità](#funzionalità)
- [Novità della v2.0.0-beta2](#novità-della-v200-beta2)
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

- **Input manuale, multi-sorgente**: da 1 a 4 sorgenti indipendenti di bit grezzi. Tre
formati accettati (binario, esadecimale — con parsing tollerante a prefissi "0x" e
separatori vari — e **NUOVO** lista di byte decimali/esadecimali separati da spazio o
virgola). Il tool non genera né simula mai entropia lato browser.
- **NUOVO — Assistente "dati numerici (sensore/CSV) → bit grezzi"**: incolla letture
numeriche (accelerometro, giroscopio, CSV) e lo strumento sceglie automaticamente scala,
LSB, modalità e interleave tramite grid-search su un punteggio di qualità, poi invia i
bit a una delle 4 sorgenti per la stima rigorosa standard.
- **NUOVO — Pulsante "Demo sbilanciata (test)"** per verificare in prima persona, con
CSPRNG reale, come reagisce il gate di esclusione H_min<0.3.
- **Modalità di combinazione esplicita**: Concatenazione (default, additiva), XOR o
Interleave (per sorgenti indipendenti — bloccate automaticamente se rilevata
correlazione). Vedi `SECURITY-NOTES.md`.
- **Stima di min-entropia in stile SP 800-90B**: Most Common Value (MCV) e Markov
(ordine-1) con limite di confidenza superiore di Clopper-Pearson al 99%, più t-Tuple e
Longest Repeated Substring (LRS) per rilevare strutture periodiche di ordine superiore.
La min-entropia finale è il minimo fra tutti gli stimatori applicabili.
- **Health test retrospettivi**: Repetition Count Test (RCT) e Adaptive Proportion Test
(APT), per intercettare run patologici o drift locale in una sorgente.
- **Controllo di correlazione multi-lag** (±8 posizioni) fra sorgenti, non solo bit
allineati alla stessa posizione.
- **Peres Extractor** (variante ricorsiva completa del von Neumann Extractor, Peres 1992)
con verifica di conservazione della massa ad ogni esecuzione.
- **Toeplitz Hashing su GF(2)** con seed generato automaticamente da timestamp CPU
(unicità/audit) + CSPRNG del browser (sicurezza), espanso via SHA-256 in counter-mode.
- **Tetto di emissione conservativo** (⌊input/2⌋), indipendente dal bound LHL.
- **NUOVO — Margine di sicurezza LHL selezionabile** (ε=2⁻ᵏ, k=16/20/40/64/80) invece
della sola scelta binaria standard/ridotto — richiede conferma esplicita sotto lo
standard (k=80), una sola volta per sessione.
- **Batteria di test statistici NIST SP 800-22 — 8 procedure** (Frequency, Runs, Longest
Run, **Serial completo** con estensione ciclica, **Approximate Entropy completa** con
estensione ciclica, **NUOVO Cumulative Sums** diretto e inverso, **NUOVO Binary Matrix
Rank** 32×32), applicate sia pre- che post-estrazione. Le 4 procedure aggiuntive/corrette
sono state sottoposte a verifica matematica indipendente completa (vedi CHANGELOG.md):
valori analitici noti, casi avversari, e tasso di falsi positivi su 300 sequenze CSPRNG
reali risultato statisticamente coerente con la teoria.
- **Pipeline di confronto diagnostica XOR-LFSR**: termine di paragone non protetto per
intercettare regressioni nella pipeline primaria. Vedi `SECURITY-NOTES.md`.
- **Hash di integrità dell'applicazione**: SHA-256 del codice core, mostrato al
caricamento, per verificare di star eseguendo il codice atteso.
- **Output finale**: doppio SHA-256 (schema Bitcoin-style) e, in opzione, SHAKE256 a
lunghezza di output variabile — implementazione JS pura di Keccak-f[1600], perché
`crypto.subtle` del browser non supporta nativamente SHAKE256.
- **Suite di autotest all'avvio**: conservazione di massa, coerenza Toeplitz contro
un'implementazione indipendente, vettori di test ufficiali SHA-256/SHAKE256,
auto-consistenza statistica, tetto di emissione. Se qualcosa fallisse qui, è una
regressione nel codice.

## Novità della v2.0.0-beta2

Vedi `CHANGELOG.md` per il dettaglio completo, inclusa la sezione dedicata alla verifica
matematica indipendente eseguita sui 4 test NIST nuovi/aggiornati. In sintesi: modalità di
combinazione multi-sorgente, tetto di emissione conservativo, pipeline di confronto
XOR-LFSR, hash di integrità, margine LHL selezionabile, demo sbilanciata, assistente
CSV/sensore, parsing di input più tollerante, batteria NIST estesa a 8 procedure
conformi. Il nucleo matematico/crittografico storico (Peres, Toeplitz, SHA-256/SHAKE256,
Clopper-Pearson) è **invariato** rispetto alla build 2026-09-11. Le note d'audit
dettagliate, prima incorporate nell'HTML, sono in `AUDIT-NOTES.md`; i principi di design
trasversali sono in `SECURITY-NOTES.md`.

## Come si usa

1. Scarica `entropy_pipeline.html` (unico file necessario).
2. Aprilo in un browser moderno — non serve alcuna installazione o connessione a internet.
3. Segui le fasi mostrate nella pagina, in ordine (l'assistente CSV/sensore è opzionale,
prima di Fase 1).

Istruzioni dettagliate passo-passo: [ISTRUZIONI.md](ISTRUZIONI.md).

## Struttura del repository

```
.
├── entropy_pipeline.html  # Lo strumento — build v2.0.0-beta2 (unico file necessario per l'uso)
├── ISTRUZIONI.md                # Guida all'uso passo-passo
├── CHANGELOG.md                 # Cronologia dettagliata di tutte le build e i bug corretti
├── AUDIT-NOTES.md               # Dettaglio completo delle note d'audit (spostato fuori dall'HTML)
├── SECURITY-NOTES.md            # Principi di design trasversali del progetto
├── CONTRIBUTING.md              # Linee guida per contribuire
├── LICENSE                      # Licenza MIT
└── README.md                    # Questo file
```

## Fondamenti tecnici

| Passaggio          | Tecnica                                                                             | Riferimento                            |
| ------------------ | ----------------------------------------------------------------------------------- | -------------------------------------- |
| Stima entropia     | MCV, Markov (ordine-1), t-Tuple, LRS — con limite di confidenza Clopper-Pearson 99% | NIST SP 800-90B                        |
| Health test        | Repetition Count Test, Adaptive Proportion Test                                     | NIST SP 800-90B §4.4                   |
| Estrazione bias    | Peres Extractor (costruzione ricorsiva completa)                                    | Peres, 1992                            |
| Hashing universale | Toeplitz matrix hashing su GF(2)                                                    | Toeplitz-hashing / universal hashing   |
| Bound di sicurezza | Leftover Hash Lemma (ε=2⁻ᵏ selezionabile) + tetto di emissione ⌊input/2⌋ indipendente | Impagliazzo–Levin–Luby, 1989           |
| Test statistici    | Frequency, Runs, Longest Run, Serial (completo), ApproxEntropy (completa), Cumulative Sums (×2), Binary Matrix Rank | NIST SP 800-22 (8 di 15 procedure) |
| Output finale      | SHA-256 (doppio), SHAKE256 (XOF)                                                    | FIPS 180-4, FIPS 202                   |
| Confronto          | Pipeline diagnostica XOR-LFSR (non protetta, solo per rilevare regressioni)          | —                                       |

## Audit e limiti noti

Il dettaglio completo, punto per punto, è in [AUDIT-NOTES.md](AUDIT-NOTES.md) — vale la
pena leggerlo prima di fidarsi ciecamente dello strumento. In sintesi: questo progetto è
nato da un processo di revisione conversazionale iterativo, in cui sono stati trovati e
corretti diversi bug reali nel nucleo matematico/crittografico. Ogni bug è stato riprodotto
con un caso di test costruito ad-hoc prima di essere corretto, e verificato senza
regressioni tramite la suite di autotest.

**Limiti architetturali che nessuna correzione di bug elimina:**

- Gira in un browser: nessun controllo su swap/paging della memoria, nessuna protezione
`mlock`, il garbage collector del motore JS gestisce i bit "segreti" senza alcun
controllo dell'utente.
- La stima di min-entropia dipende da un campione statico incollato manualmente — non
sostituisce un health test in tempo reale su hardware fisico.
- I test statistici su un output di poche centinaia di bit hanno potenza limitata: un
"PASS" è indicativo, non probante.
- La batteria NIST SP 800-22 copre 8 delle 15 procedure ufficiali (Serial e Approximate
Entropy ora nella forma completa con estensione ciclica; Cumulative Sums e Binary Matrix
Rank aggiunti in v2.0.0-beta2). Mancano ancora: DFT/Spettrale, Linear Complexity, Maurer's
Universal Statistical Test, Template Matching (×2), Random Excursions (×2) — dichiarato
come tale, non conformità certificata NIST STS.

## Autotest

Ad ogni caricamento della pagina, un pannello dedicato esegue automaticamente:

- conservazione di massa del Peres Extractor su input casuali;
- coerenza del Toeplitz hashing contro una seconda implementazione scritta con un percorso
di codice indipendente (diagonali esplicite, non la stessa formula confrontata con se
stessa);
- vettori di test ufficiali per SHA-256 e SHAKE256;
- auto-consistenza della funzione beta incompleta (Clopper-Pearson);
- coerenza fra i due metodi indipendenti di calcolo di erfc;
- verifica del tetto di emissione ⌊input/2⌋.

Se uno di questi autotest fallisse, significherebbe una regressione nel codice: non
fidarsi dei risultati della pipeline finché non è risolto. La verifica matematica dei
4 test NIST nuovi/aggiornati in questa build (blocco matematico, casi avversari, tasso di
falsi positivi su 300 prove CSPRNG reali) è documentata in `CHANGELOG.md` — non è
incorporata nel pannello di autotest della pagina per non appesantire il caricamento ad
ogni apertura, essendo stata eseguita una tantum in fase di sviluppo.

## Contribuire

Vedi [CONTRIBUTING.md](CONTRIBUTING.md). Segnalazioni di bug, correzioni matematiche e
miglioramenti alla suite di autotest sono particolarmente benvenuti — la storia di questo
progetto dimostra che ce n'è sempre bisogno.

## Licenza

Distribuito sotto licenza MIT — vedi [LICENSE](LICENSE).

## Per la raccolta delle sorgenti

APP consigliate per la raccolta dei campioni da processare: RØDE Reporter, sensor logger,
registratore Audio di Hardcoded Joy, RecForge II.

Uno o due telefoni cellulari, una macchina fotografica che abbia la possibilità di salvare
le foto in RAW, una o meglio due radio FM economiche a batterie, un dado in buone condizioni,
una moneta possibilmente in buone condizioni e bilanciata (da 2 euro esce certificata dalla
Zecca di Stato), 8 numeri della tombola, un file zip autocreato offline di qualche mega e
poi distrutto.

Con il microfono del telefono ed escludendo i filtri in ingresso, raw, mono (possibilmente
queste app lo fanno), già due o più minuti di audio in un bar frequentato o in una mensa
genera un audio con tanto materiale difficilmente prevedibile, buono da estrarre. O anche
il campionamento dal sensore del giroscopio o magnetometro o accelerometro in una strada con
buche e dossi, può esserci imprevedibilità nei bit estratti — l'assistente CSV/sensore di
questa build è pensato proprio per questo caso d'uso. L'importante è prendere sorgenti
grezze campionate che fra loro non abbiano correlazioni apparenti: il segnale audio di due
radio FM a batterie sintonizzate fuori frequenza, una foto completamente nera fatta in raw
tappando l'obiettivo, un giroscopio e il rumore in un bar o una mensa affollata hanno ben
poco in comune. Basta che una sola tra le sorgenti scelte abbia "qualità entropica".
