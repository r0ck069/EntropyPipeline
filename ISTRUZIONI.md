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
come separatori). L'assistente **non genera entropia** e **non sceglie la configurazione**:
scala, numero di LSB, modalità (valore diretto o differenza) e interleave fra colonne li
imposti tu, poi premi "Estrai bit con questa configurazione", che estrae i bit meno
significativi realmente presenti nei dati incollati. Scegli la sorgente di destinazione e
premi "Invia bit alla sorgente scelta". I bit restano soggetti alla stessa stima di
min-entropia di Fase 1, che misura i numeri e non la loro origine fisica: una configurazione
che sembra buona non dimostra che la sorgente sia imprevedibile.

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
  soglia di esclusione 0,3 nel 7,9% delle prove a 256 bit (79 su 1000), nello 0,9% a 400 bit (9 su 1000) e in nessuna
  delle 1000 prove a 603 bit (misura della riverifica del 12/10, Chromium).
- Basta compilarne anche **una sola**: le altre restano semplicemente vuote e vengono
  ignorate. Funziona con 1, 2, 3 o 4 sorgenti indistintamente.
- **Requisito sulle sorgenti:** ogni sorgente va prodotta in proprio, distrutta dopo l'uso,
  deve essere di qualità e indipendente dalle altre, e deve superare i test di «Analizza»
  prima di far parte dei bit candidati per la seed. Il tool non controlla la provenienza.
- **Minimo e standard:** il minimo è di 256 bit per sorgente, senza eccezioni. Lo standard NIST SP 800-90B
  (§3.1.1, punto 1) richiede un dataset sequenziale di almeno 1.000.000 di campioni grezzi dalla
  stessa sorgente; se non è possibile, ammette la concatenazione di insiemi più piccoli della
  stessa sorgente, con almeno 1000 campioni ciascuno. Il progetto concatena sorgenti diverse:
  256 bit è una deviazione dichiarata, non una conformità (vedi README). Le stime di
  min-entropia ottenute con meno di 1.000.000 di campioni sono indicative e non costituiscono
  una validazione secondo NIST SP 800-90B.
- Premi "Analizza" su ogni finestra compilata: mostra la stima di min-entropia (il minimo
  fra più stimatori: MCV, Markov, t-Tuple, LRS, Collisione e, da 6012 bit in su, Compressione)
  e l'esito di due health test retrospettivi
  (RCT e APT) che intercettano pattern anomali (run troppo lunghi, bias locale).
- Una sorgente con H_min troppo basso viene automaticamente esclusa dal calcolo successivo.
  Una sorgente con allarme RCT o APT viene esclusa con il messaggio «da verificare»: su sorgenti
  lunghe l'RCT può dare falsi allarmi su dati buoni (vedi README, Audit e limiti noti). Non serve
  rimuoverla a mano.
- "Svuota" cancella una finestra e la relativa analisi.
- Durante una stima compare in cima alla pagina un contatore in secondi con l'etichetta dello stimatore in corso. Avanza solo se il browser risponde. Il calcolo prosegue anche quando il contatore si ferma per un momento; se resta fermo per molto più di qualche secondo, segnalalo.

**Consiglio pratico:** con una sola sorgente al minimo di 256 bit, capita occasionalmente (per
pura variabilità statistica dei dati, non per un difetto del tool) che venga esclusa dal calcolo
perché H_min scende sotto 0,3. Fornire più bit per singola sorgente aumenta il margine, rende
questo caso raro e avvicina il numero di campioni per sorgente a quello richiesto dallo standard: almeno 1000 per ciascun insieme concatenato, 1.000.000 per un dataset unico.

### Fase 2 — Concatenazione, conteggio degli uni, correlazione

Premi "Esegui FASE 2". Il tool concatena le sorgenti valide, verifica il conteggio degli uni con due
algoritmi distinti, e — se hai compilato più di una sorgente — controlla la correlazione
tra le coppie di sorgenti su più ritardi temporali (±8 posizioni), non solo bit-per-bit
allineati. Il flusso combinato viene poi rivalidato con gli stimatori: sotto 1.000.000 di bit con la battery completa (sei stimatori), sopra con il solo LRS. Se tutto è a posto, calcola l'entropia assoluta stimata (in bit), che sarà il budget usato in Fase 4: il minimo fra la stima per sorgente e quella misurata sul flusso combinato. Se la H_min combinata scende sotto 0,3, la Fase 2 si ferma.

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
mano. Un campo di override manuale resta disponibile per utenti avanzati: il seme inserito a mano viene rifiutato se è costante, periodico (periodo fino a 32) o con H_min sotto 0,3, e segnalato se sotto 0,8.

### Fase 5 — Test statistici NIST-style

Premi "Esegui FASE 5" per una batteria di 8 test (Frequency, Runs, Longest Run, Serial,
Approximate Entropy, Cumulative Sums diretto e inverso, Binary Matrix Rank) applicati sia ai
bit di ingresso (PRE) sia all'output di Fase 4 (POST). Frequency e Runs sono calcolati con
due metodi numerici indipendenti per un controllo incrociato. Se l'output è troppo corto
perché un test sia significativo, viene mostrato **N/A**, non un fallimento — non confondere
i due casi.

### Output finale

- **Doppio SHA-256**: premi il pulsante dedicato per ottenere `SHA-256(SHA-256(output))`,
  mostrato come sequenza binaria continua e come esadecimale. L'etichetta dichiara la forza di sicurezza: al più *m* bit (quelli della Fase 4), e avvisa quando *m* è sotto 256.
- **SHAKE256 (opzionale)**: imposta la lunghezza di output desiderata in bit e premi
  "Calcola SHAKE256" per un output a lunghezza variabile (funzione XOF), calcolato sullo
  stesso input del doppio SHA-256 (l'output di Fase 4), non incatenato dopo di esso.

### Autotest e log

- Il pannello "Autotest all'avvio" esegue automaticamente, ad ogni caricamento della
  pagina, una serie di controlli di non-regressione (conservazione di massa, coerenza
  Toeplitz, vettori di test SHA-256/SHAKE256, auto-consistenza statistica, stimatori
  LRS/Collisione/Compressione contro i valori ufficiali). Se qualcosa
  qui risultasse rosso/fallito, **non fidarti dei risultati della pipeline** finché non
  viene risolto — significherebbe una regressione nel codice. Con un autotest fallito le Fasi 1-5 e gli output finali restano bloccati, anche se i pulsanti vengono riabilitati a mano.
- Il log di sessione, in fondo alla pagina, resta solo in RAM: non viene scritto su disco
  e sparisce alla chiusura della scheda.

## Verificare di avere l'ultima versione

Sotto il titolo trovi una riga tipo `Build 2.0.0-beta7 (2026-10-12) — BETA NON AUDITATA.`.
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
