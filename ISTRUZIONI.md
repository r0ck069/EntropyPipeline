# Entropy Extraction Pipeline (Peres + Toeplitz) — Istruzioni per l'uso

Strumento HTML standalone per sperimentare un pipeline completo di entropy conditioning:
raccolta di bit grezzi → stima di min-entropia (stile SP 800-90B) → estrazione del bias
(Peres Extractor) → hashing universale (Toeplitz, GF(2)) → output finale (doppio SHA-256,
opzionalmente SHAKE256).

## Requisiti

- Un browser moderno con supporto a `crypto.subtle` e `BigInt` (Firefox recente va bene;
  testato pensando a Firefox su Ubuntu MATE Live).
- **Nessuna connessione internet richiesta.** Tutto il file è autocontenuto: nessuna
  dipendenza esterna, nessun CDN, nessuna chiamata di rete.
- Nessuna installazione: basta aprire il file `entropy_pipeline.html` con doppio click o
  trascinandolo in una finestra del browser.

## Avvertenza importante, da leggere prima di usarlo

**Questo strumento non è un generatore di chiavi crittografiche di livello produzione.**
È un dimostratore didattico/di verifica dei passaggi di un pipeline di estrazione entropia,
costruito e verificato con test automatici (vedi il pannello "Autotest all'avvio" e il file
CHANGELOG.md), ma opera dentro un browser: nessun controllo su swap/paging della memoria,
nessuna protezione da estensioni del browser o da un ambiente compromesso, e il margine di
sicurezza matematico può essere abbassato con conferma esplicita quando l'input è limitato.
Usalo per capire, sperimentare, validare il processo — non come ultimo anello della catena
per chiavi che contano davvero.

## Come si usa, passo per passo

### Fase 1 — Inserimento bit grezzi

Per la raccolta dei dati grezzi da varie sorgenti vedere il file README.md
Successivamente andranno processati per avere i bit da incollare nelle finestre successive
(tool in sviluppo, stay tuned).
Al momento si possono provare sequenze di bit prese da qualche bit generator online o da 
qualche AI o generati in proprio.

Ci sono 4 finestre (S1-S4), ciascuna indipendente. In ognuna incolla bit grezzi ottenuti
con uno strumento **esterno** al tool (un TRNG hardware, `/dev/hwrng`, un generatore di
rumore, ecc.) — il tool stesso non genera né simula entropia in nessuna finestra.

- Formato accettato: **esadecimale** oppure **binario puro** (solo caratteri `0` e `1`).
- Lunghezza minima per finestra: **256 bit**.
- Basta compilarne anche **una sola**: le altre restano semplicemente vuote e vengono
  ignorate. Funziona con 1, 2, 3 o 4 sorgenti indistintamente.
- Premi "Analizza" su ogni finestra compilata: mostra la stima di min-entropia (il minimo
  fra più stimatori: MCV, Markov, t-Tuple, LRS) e l'esito di due health test retrospettivi
  (RCT e APT) che intercettano pattern anomali (run troppo lunghi, bias locale).
- Una sorgente con H_min troppo basso, o che fallisce RCT/APT, viene automaticamente
  esclusa dal calcolo successivo — non serve rimuoverla a mano.
- "Svuota" cancella una finestra e la relativa analisi.

**Consiglio pratico:** con una sola sorgente al minimo esatto di 256 bit, capita
occasionalmente (per pura variabilità statistica dei dati, non per un difetto del tool) che
venga respinta. Con 2+ sorgenti, o con più di 256 bit per sorgente, il margine aumenta e
questo diventa raro.

### Fase 2 — Concatenazione, checksum, correlazione

Premi "Esegui FASE 2". Il tool concatena le sorgenti valide, verifica l'integrità con due
checksum indipendenti, e — se hai compilato più di una sorgente — controlla la correlazione
tra le coppie di sorgenti su più ritardi temporali (±8 posizioni), non solo bit-per-bit
allineati. Se tutto è a posto, calcola anche l'entropia assoluta stimata (in bit), che sarà
il budget usato in Fase 4.

### Fase 3 — Peres Extractor

Premi "Esegui FASE 3". Applica l'estrattore di von Neumann/Peres (versione ricorsiva) per
rimuovere il bias dai bit concatenati. Mostra input, output, bit scartati e la verifica di
conservazione della massa (out + scartati = input): se questa verifica fallisse, sarebbe un
segnale di bug interno, non un problema dei tuoi dati.

### Fase 4 — Toeplitz Hashing

Imposta `m` (i bit di output desiderati) oppure lascia il campo vuoto per farlo proporre
in automatico. Il tool calcola il vincolo di sicurezza (Leftover Hash Lemma):

- Se l'entropia raccolta è sufficiente, usa il margine **standard** (160 bit, distanza
  statistica dall'uniforme ≤2⁻⁸⁰ — livello adatto a materiale crittografico).
- Se non è raggiungibile (tipico con input limitati, es. una sola sorgente da 256 bit), il
  tool propone un margine **ridotto** (32 bit, ≤2⁻¹⁶) — solo dopo una tua conferma esplicita,
  perché adatto solo a scopi dimostrativi/di test, non a chiavi reali.

Il seed della matrice di Toeplitz viene generato automaticamente combinando il timestamp
CPU (per rendere ogni esecuzione tracciabile/unica) con `crypto.getRandomValues` (per la
sicurezza), espanso alla lunghezza esatta necessaria — non serve calcolarlo o incollarlo a
mano. Un campo di override manuale resta disponibile per utenti avanzati.

### Fase 5 — Test statistici NIST-style

Premi "Esegui FASE 5" per una batteria di test (Frequency, Runs, Longest Run, Serial,
Approximate Entropy) applicati sia ai bit di ingresso (PRE) sia all'output di Fase 4 (POST),
ciascuno calcolato con due metodi numerici indipendenti per un controllo incrociato. Se
l'output è troppo corto perché un test sia significativo, viene mostrato **N/A**, non un
fallimento — non confondere i due casi.

### Output finale

- **Doppio SHA-256**: premi il pulsante dedicato per ottenere `SHA-256(SHA-256(output))`,
  mostrato come sequenza binaria continua e come esadecimale.
- **SHAKE256 (opzionale)**: imposta la lunghezza di output desiderata in bit e premi
  "Calcola SHAKE256" per un output a lunghezza variabile (funzione XOF), calcolato sullo
  stesso input del doppio SHA-256 (l'output di Fase 4), non incatenato dopo di esso.

### Autotest e log

- Il pannello "Autotest all'avvio" esegue automaticamente, ad ogni caricamento della
  pagina, una serie di controlli di non-regressione (conservazione di massa, coerenza
  Toeplitz, vettori di test SHA-256/SHAKE256, auto-consistenza statistica). Se qualcosa
  qui risultasse rosso/fallito, **non fidarti dei risultati della pipeline** finché non
  viene risolto — significherebbe una regressione nel codice.
- Il log di sessione, in fondo alla pagina, resta solo in RAM: non viene scritto su disco
  e sparisce alla chiusura della scheda.

## Verificare di avere l'ultima versione

Sotto il titolo trovi una riga tipo `build 2026-09-08.9 — ...`. Confrontala con il file
CHANGELOG.md incluso in questo pacchetto. Se non coincide, il browser sta probabilmente
mostrando una copia in cache: ricarica forzando lo svuotamento cache (in Firefox:
Ctrl+Shift+R) o riapri il file scaricato di recente.

## Contenuto di questo pacchetto

- `entropy_pipeline.html` — lo strumento vero e proprio, apribile direttamente nel browser.
- `CHANGELOG.md` — cronologia dettagliata di tutte le correzioni e migliorie.
- `ISTRUZIONI.md` — questo file.
