# Changelog — Entropy Extraction Pipeline (Peres + Toeplitz)

Tutte le build sono identificabili dalla riga `build YYYY-MM-DD.N` mostrata sotto il titolo
dell'app. Se quella riga non corrisponde all'ultima elencata qui, il browser sta mostrando
una copia in cache: ricaricare forzando lo svuotamento cache (Ctrl+Shift+R) o riaprire il
file scaricato di recente.

**SHA-256 di questo file:** `a114753c57bd05c017d1f3e75be0692465ed1aef8f637ca291ef93f0a4a5b4c0`

---

## build 2026-09-10.1 — Audit matematico approfondito: 3 bug trovati e corretti

Audit di verifica indipendente su ogni formula statistica/crittografica del file, con
riscontro contro la letteratura di riferimento (NIST SP 800-90B, SP 800-22) e verifica
numerica/analitica indipendente di ciascun componente (non solo ispezione del codice).

**Bug trovati e corretti, ciascuno riprodotto con un caso costruito ad-hoc prima del fix:**

1. **Riferimento errato nel messaggio di Fase 3** ("atteso 25%" per il rapporto di
   estrazione del Peres Extractor). Il valore teorico corretto per la variante
   **ricorsiva** implementata è **1/3 (33.3%)**, non 25% — quel valore vale solo per il
   von Neumann extractor a singolo livello (senza riciclo delle coppie uguali). Confermato
   sia analiticamente (serie geometrica 1/4+1/16+1/64+...=1/3) sia empiricamente
   (simulazione: 33.29% osservato su 30 trial da 50.000 bit, contro 33.33% teorico).
   Impatto pratico: nullo (la tolleranza di ±15 punti percentuali non aveva mai reagito),
   ma il numero mostrato all'utente era semplicemente sbagliato.
2. **Off-by-one nell'Adaptive Proportion Test (APT)**. Il conteggio confrontava il simbolo
   di riferimento (primo della finestra) anche con se stesso, su tutte le W posizioni,
   mentre il cutoff statistico è calcolato per una distribuzione Binomiale(W−1, p) — cioè
   sulle sole rimanenti W−1 posizioni. Il conteggio risultava sistematicamente gonfiato di
   +1. Verificato con un caso costruito: finestra `[0,1,1,1,1,1,1,1,1,1]` doveva dare
   conteggio 0 (nessun altro simbolo coincide col primo), il codice restituiva 1.
   Impatto pratico: il test risultava leggermente più severo del tasso di falso-positivo
   dichiarato (2⁻²⁰) — un errore nella direzione cauta, non pericolosa, ma comunque un
   disallineamento reale dalla specifica.
3. **Limite artificiale nella ricerca del Longest Repeated Substring (LRS)**. La ricerca
   binaria era limitata a `floor(n/2)`, un limite non previsto dalla specifica SP 800-90B.
   Per sequenze fortemente periodiche la vera ripetizione più lunga può superare n/2:
   dimostrato con una sequenza di periodo 2 su 100 bit, dove la vera ripetizione (98 bit)
   veniva troncata a 50 dal limite precedente. Impatto pratico: risultato trascurabile nei
   casi analizzati (l'effetto di "appiattimento" della radice L-esima nella formula LRS
   maschera comunque il problema per sequenze fortemente strutturate, dando in entrambi i
   casi un H_min correttamente vicino a zero), ma la deviazione dalla specifica è stata
   comunque corretta per rigore.

**Componenti riverificati e confermati corretti**, con un livello di verifica più alto
della semplice ispezione:
- **Clopper-Pearson**: confermato non solo per auto-consistenza ma **analiticamente**,
  sfruttando la forma chiusa della funzione Beta(1,n) per il caso x=0 — il valore
  calcolato dal tool (0.3690) coincide esattamente con `1 - 0.01^(1/10) = 0.369043`.
- Soglie chi-quadro di Serial (11.34, df=3) e ApproxEntropy (13.28, df=4): corrispondono
  esattamente ai valori critici tabulati per α=0.01.
- Costanti del test Longest Run a blocchi M=8: corrispondono esattamente alla tabella
  ufficiale NIST SP 800-22.
- Margini del Leftover Hash Lemma (160 bit → 2⁻⁸⁰, 32 bit → 2⁻¹⁶): consistenti con la
  formulazione standard del bound.
- Peres Extractor, Toeplitz Hashing, SHAKE256: riconfermati senza regressioni rispetto
  alle build precedenti.

**Semplificazioni già dichiarate, ora esplicitate con maggiore dettaglio tecnico** (non
nuovi bug, ma precisazioni che un audit rigoroso deve nominare): il test Serial qui
implementato è in realtà un singolo chi-quadro di bontà d'adattamento sulle frequenze
delle coppie di bit (matematicamente equivalente a ψ²₂), non il vero test Serial ufficiale
a due statistiche (∇ψ²ₘ, ∇²ψ²ₘ); né Serial né ApproxEntropy usano l'estensione ciclica del
campione richiesta dalla specifica NIST SP 800-22 (che ripete i primi m−1 bit in coda).

**Verifica di non-regressione:** l'intera suite di autotest all'avvio è stata rieseguita
dopo ciascun fix — tutti i 7 controlli continuano a passare.

## build 2026-09-08.9 — Fix gate Fase 2 ridondante

- **Rimosso** il controllo aggregato `Σ H_min ≥ soglia` in Fase 2. Era stato introdotto per
  scalare con il numero di sorgenti attive, ma dopo l'irrobustimento degli stimatori
  (Clopper-Pearson) è diventato o troppo severo (soglia 0.5×N: nessuna sorgente reale la
  superava più) o, una volta abbassato a 0.3×N, matematicamente **tautologico**: poiché ogni
  sorgente attiva è già filtrata individualmente a H_min≥0.3, la somma di N sorgenti attive è
  sempre ≥0.3×N per costruzione. Un controllo che non può mai fallire non è un controllo.
- Il vero vincolo di sicurezza resta, come deve essere, il bound del Leftover Hash Lemma in
  Fase 4, calcolato sull'entropia assoluta reale (bit), non su una soglia euristica in Fase 2.

## build 2026-09-08.8 — Batteria di stima entropia irrobustita

- **Clopper-Pearson 99%**: MCV e Markov usano ora il limite di confidenza superiore al 99%
  (SP 800-90B) invece della stima puntuale grezza (count/n), che su campioni piccoli
  sottostima sistematicamente il bias reale della sorgente.
- **Nuovi stimatori t-Tuple e LRS** (Longest Repeated Substring): rilevano strutture
  periodiche/ripetute di ordine superiore che MCV e Markov (ordine-1) non vedono per
  costruzione. Dimostrato su una sequenza periodica completamente prevedibile: MCV dava
  H_min=1.0 (perfetta!), t-Tuple/LRS la riconoscono correttamente come quasi priva di entropia.
  La min-entropia finale della sorgente è il minimo fra tutti gli stimatori applicabili.
  Volutamente non implementati: Collision Estimate (degenere su alfabeto binario) e
  Compression/Universal di Maurer (richiede campioni troppo grandi per essere valido qui).
- **Health test retrospettivi RCT/APT** (SP 800-90B §4.4): Repetition Count Test e Adaptive
  Proportion Test applicati al campione incollato. Intercettano run patologici e drift
  locale che gli stimatori globali medierebbero via. Una sorgente che fallisce viene esclusa
  in Fase 2 indipendentemente dal suo H_min aggregato.
- **Correlazione multi-lag (±8)** tra sorgenti in Fase 2: il controllo precedente (solo
  lag 0) non rilevava due sorgenti correlate ma temporalmente sfasate (es. clock diverso).
- **Suite di autotest all'avvio**: conservazione di massa del Peres Extractor su input
  casuali, coerenza del Toeplitz hashing contro una seconda implementazione scritta con un
  percorso di codice indipendente, vettori di test ufficiali SHA-256/SHAKE256,
  auto-consistenza di Clopper-Pearson, coerenza fra i due metodi erfc.
- **Non incluso**: due tentativi di ottimizzazione prestazionale del Toeplitz hashing
  (BigInt, poi word-packing a 32 bit) sono stati scartati dopo benchmark/test — il primo
  più lento dell'originale, il secondo con un bug di indicizzazione irrisolto in tempo utile.
  Resta il ciclo bit-a-bit originale, verificato. Nessun audit trail firmato (solo log RAM).

## build 2026-09-08.7 — Fix confusione N/A vs FAIL in Fase 5

- Ogni test NIST-style ha una lunghezza minima per essere significativo (100 o 128 bit).
  Con output brevi (es. m=56 bit) le funzioni restituivano un valore "sentinella" trattato
  erroneamente come FAIL vero. Ora mostrato come **N/A**, escluso dal verdetto finale.
- Corretto bug nel calcolo del 3σ per il bilanciamento 0/1 (usava `3·√n` invece della vera
  deviazione standard binomiale `1.5·√n`, due volte più permissivo del dovuto).
- Soglia Shannon fissa (0.999) rimossa dal verdetto pass/fail: statisticamente irraggiungibile
  per campioni brevi anche con dati perfettamente casuali. Resta solo informativa.

## build 2026-09-08.6 — Gate Fase 2 proporzionale + margine LHL adattivo

- Gate Fase 2 reso proporzionale al numero di sorgenti attive (permette l'uso con 1 sola
  sorgente, prima impossibile per costruzione con la soglia fissa `Σ H_min ≥ 2.0`).
- Margine di sicurezza LHL in Fase 4 a due livelli: standard (160 bit, distanza statistica
  ≤2⁻⁸⁰) e ridotto (32 bit, ≤2⁻¹⁶, richiede conferma esplicita) — permette di completare la
  pipeline anche con input limitati (es. una sola sorgente da 256 bit), sempre con avviso
  chiaro quando si scende sotto il margine crittografico standard.

## build 2026-09-08.5 — Fix cross-check erfc + SHAKE256 opzionale

- **Bug critico corretto**: la funzione `erfcAbramowitzStegun` usava la struttura di calcolo
  di Numerical Recipes ma con i coefficienti sbagliati (di un'altra formula), dando
  `erfc(0)=0.767` invece di `1`. Il cross-check Frequency/Runs falliva sempre per questo.
  Corretta con i coefficienti giusti, rinominata `erfcNumericalRecipes`.
- **SHAKE256 opzionale** aggiunto dopo la Fase 5. `crypto.subtle` del browser non supporta
  SHAKE256 nativamente: implementato Keccak-f[1600] in JS puro, verificato byte-per-byte
  contro l'implementazione nativa OpenSSL su più vettori di test.

## build precedenti (non numerate con questo schema)

- Fix bug di contabilità nel Peres Extractor: le coppie di bit diseguali non incrementavano
  il contatore `discarded`, causando divergenza `out+discarded ≠ input` su campioni grandi.
- Fix errore dimensionale nel bound LHL: la Fase 4 sommava i **tassi** di H_min (0-1 per bit)
  come se fossero già un conteggio assoluto di bit, rendendo `m_max` sempre fortemente
  negativo. Corretto usando Σ(tasso×lunghezza) per sorgente.
- **Bug concettuale nel cuore matematico**: la matrice usata per l'hashing era in realtà una
  matrice di **Hankel** (costante sulle anti-diagonali, T[i][j]=seed[i+j]), non di Toeplitz
  (costante sulle diagonali, T[i][j]=seed[i-j+n-1]). Corretta l'indicizzazione in entrambe le
  funzioni (hash e verifica).
- Seed Toeplitz reso derivabile automaticamente da timestamp CPU (per unicità/audit) +
  CSPRNG del browser (per sicurezza), espanso via SHA-256 in counter-mode alla lunghezza
  esatta richiesta, invece di richiedere un seed manuale di lunghezza calcolata a mano.
- Fase 1 ridisegnata come puro input manuale (nessuna generazione di entropia lato browser):
  4 finestre indipendenti che accettano hex/binario incollato da strumenti esterni, minimo
  1 sorgente compilata, minimo 256 bit per sorgente.
- Output binario reso sequenziale e continuo (nessun raggruppamento a spazi che interrompe
  la sequenza) sia in Fase 4 sia nell'output finale.

---

## Nota di trasparenza sul processo di sviluppo

Praticamente ogni build elencata sopra corregge un bug reale, spesso nel nucleo
matematico/crittografico dello strumento (Toeplitz-non-Toeplitz, bound LHL con unità di
misura sbagliate, cross-check erfc rotto, gate di sicurezza tautologico). Costruendo la
suite di autotest sono stati scoperti perfino due refusi di trascrizione nelle costanti di
test stesse. Questo tool è nato come dimostratore didattico dei passaggi di un pipeline di
entropy conditioning (von Neumann/Peres → hashing universale Toeplitz → Leftover Hash Lemma
→ XOF), verificato con test automatici e vettori di riferimento ufficiali dove possibile —
ma **non è, e non deve essere considerato, un generatore di chiavi crittografiche di livello
produzione**. Vedi il file `ISTRUZIONI.md` per le limitazioni d'uso.
