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

### Assistente opzionale — dati numerici → bit grezzi (prima di Fase 1)

Incolla letture numeriche (accelerometro, giroscopio, CSV di sensori; spazi, virgole o tab
come separatori). L'assistente **non genera entropia**: prova più combinazioni di scala,
numero di LSB, modalità (valore diretto o differenza) e interleave fra colonne, tiene quella
con il punteggio migliore (bilanciamento 0/1, Shannon, bassa autocorrelazione, lunghezza) ed
estrae i bit meno significativi realmente presenti nei dati incollati. Scegli la sorgente di
destinazione e premi "Invia bit alla sorgente scelta": i bit restano soggetti alla stessa
stima di min-entropia di Fase 1.

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
- Lunghezza minima per finestra: **256 bit**. Consigliato: almeno **600 bit**. Su bit
  casuali ideali (CSPRNG del browser, 1000 prove per lunghezza) la stima scende sotto la
  soglia di esclusione 0,3 circa il 9% delle volte a 256 bit, meno dell'1% a 400 bit e in nessuna
  delle 1000 prove a 603 bit.
- Basta compilarne anche **una sola**: le altre restano semplicemente vuote e vengono
  ignorate. Funziona con 1, 2, 3 o 4 sorgenti indistintamente.
- Premi "Analizza" su ogni finestra compilata: mostra la stima di min-entropia (il minimo
  fra più stimatori: MCV, Markov, t-Tuple, LRS, Collisione e, da 6012 bit in su, Compressione)
  e l'esito di due health test retrospettivi
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

Imposta `m` (i bit di output desiderati; se lasci il campo vuoto viene usato 256). Il tool
calcola il vincolo di sicurezza (Leftover Hash Lemma) e applica anche un tetto: `m` non
supera mai la metà dei bit in uscita dalla Fase 3.

- Scegli il margine ε dal menu: 2⁻⁸⁰ (standard, predefinito, livello adatto a materiale
  crittografico), 2⁻⁶⁴, 2⁻⁴⁰, 2⁻²⁰ o 2⁻¹⁶. Per ε = 2⁻ᵏ il margine è di 2×k bit (160 bit
  per lo standard).
- Se l'entropia disponibile non basta per `m` con il margine scelto, il tool si ferma e
  indica quanti bit servirebbero: riduci `m` oppure scegli un ε meno stretto.
- Sotto lo standard (2⁻⁸⁰) il tool chiede una conferma esplicita, una sola volta per
  sessione: adatto solo a scopi dimostrativi/di test, non a chiavi reali.

Il seed della matrice di Toeplitz viene generato automaticamente combinando il timestamp
CPU (per rendere ogni esecuzione tracciabile/unica) con `crypto.getRandomValues` (per la
sicurezza), espanso alla lunghezza esatta necessaria — non serve calcolarlo o incollarlo a
mano. Un campo di override manuale resta disponibile per utenti avanzati.

### Fase 5 — Test statistici NIST-style

Premi "Esegui FASE 5" per una batteria di 8 test (Frequency, Runs, Longest Run, Serial,
Approximate Entropy, Cumulative Sums diretto e inverso, Binary Matrix Rank) applicati sia ai
bit di ingresso (PRE) sia all'output di Fase 4 (POST). Frequency e Runs sono calcolati con
due metodi numerici indipendenti per un controllo incrociato. Se l'output è troppo corto
perché un test sia significativo, viene mostrato **N/A**, non un fallimento — non confondere
i due casi.

### Output finale

- **Doppio SHA-256**: premi il pulsante dedicato per ottenere `SHA-256(SHA-256(output))`,
  mostrato come sequenza binaria continua e come esadecimale.
- **SHAKE256 (opzionale)**: imposta la lunghezza di output desiderata in bit e premi
  "Calcola SHAKE256" per un output a lunghezza variabile (funzione XOF), calcolato sullo
  stesso input del doppio SHA-256 (l'output di Fase 4), non incatenato dopo di esso.

### Autotest e log

- Il pannello "Autotest all'avvio" esegue automaticamente, ad ogni caricamento della
  pagina, una serie di controlli di non-regressione (conservazione di massa, coerenza
  Toeplitz, vettori di test SHA-256/SHAKE256, auto-consistenza statistica, stimatori
  LRS/Collisione/Compressione contro i valori ufficiali). Se qualcosa
  qui risultasse rosso/fallito, **non fidarti dei risultati della pipeline** finché non
  viene risolto — significherebbe una regressione nel codice.
- Il log di sessione, in fondo alla pagina, resta solo in RAM: non viene scritto su disco
  e sparisce alla chiusura della scheda.

## Verificare di avere l'ultima versione

Sotto il titolo trovi una riga tipo `Build 2.0.0-beta6 (2026-10-02) — BETA NON AUDITATA.`.
Confrontala con la voce in cima al file CHANGELOG.md incluso in questo pacchetto. Se non
coincide, il browser sta probabilmente mostrando una copia in cache: ricarica forzando lo
svuotamento cache (in Firefox: Ctrl+Shift+R) o riapri il file scaricato di recente.
Puoi anche calcolare `sha256sum entropy_pipeline.html` e confrontare il risultato con
l'hash nell'intestazione di quella voce.

## Contenuto di questo pacchetto

- `entropy_pipeline.html` — lo strumento vero e proprio, apribile direttamente nel browser.
- `CHANGELOG.md` — cronologia dettagliata di tutte le correzioni e migliorie.
- `ISTRUZIONI.md` — questo file.
- `README.md` — panoramica, funzionalità, limiti noti e fondamenti tecnici.
- `AUDIT-NOTES.md` — dettaglio completo delle note d'audit.
- `SECURITY-NOTES.md` — principi di design trasversali del progetto.
- `CONTRIBUTING.md` — linee guida per contribuire.
- `verifica-stimatori/` — controlli (Python e Node) degli stimatori contro l'output ufficiale di `ea_non_iid`; non servono per usare lo strumento.
- `LICENSE` — licenza MIT.
