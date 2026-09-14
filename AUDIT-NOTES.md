# Note di audit — dettaglio applicato all'implementazione

> Questo file raccoglie il pannello "Note dell'audit applicate a questa
> implementazione" che nelle build precedenti (fino alla v1.x, build
> 2026-09-11) era incorporato direttamente nell'HTML dello strumento. A
> partire dalla v2.0.0-beta1 l'HTML riporta solo l'essenziale e i limiti
> indispensabili all'uso; il dettaglio completo vive qui.

1. **Bound LHL ancorato alle sorgenti, non all'output.** A differenza di una
   versione ancora precedente (che ri-misurava H_min su peres_out, in modo
   circolare), `m_max` è calcolato da Σ (tasso H_min × lunghezza) misurato
   sulle sorgenti in Fase 2, propagato attraverso il rapporto di estrazione
   di Fase 3. È una stima euristica, non una prova formale — trattare
   `m_max` come limite prudente, non come garanzia assoluta.

1bis. **Margine di sicurezza a due livelli.** Il margine LHL standard (160
   bit → distanza statistica ≤2⁻⁸⁰, adatto a materiale crittografico)
   richiede centinaia/migliaia di bit grezzi di buona qualità. Con input
   limitati (es. una sola sorgente da 256 bit) è spesso irraggiungibile per
   costruzione matematica, non per un difetto del tool. In tal caso l'app
   propone — solo previa conferma esplicita — un margine ridotto (32 bit →
   distanza statistica ≤2⁻¹⁶), che permette di completare comunque la
   pipeline a scopo dimostrativo/di test. L'interfaccia segnala sempre quale
   dei due margini è stato usato.

2. **Nessuna generazione di entropia lato browser.** Le 4 finestre sono puri
   campi di input: l'utente incolla bit grezzi (hex o binario) ottenuti con
   strumenti esterni (TRNG hardware, /dev/hwrng, ADC, ecc.). Il tool non
   genera, non simula e non completa mai autonomamente una sorgente.

3. **Test ridenominati "NIST-style (semplificati)".** Le implementazioni
   (Monobit, Runs, Longest-Run a blocchi M=8, Serial m=2, ApproxEntropy m=2)
   sono versioni pure-JS della famiglia NIST SP 800-22, ma con
   parametrizzazioni ridotte — non sono conformità certificata NIST.

4. **Potenza statistica dichiarata.** Con m tipico di poche centinaia di bit
   i p-value dei test finali sono indicativi, non probanti.

5. **Test troppo corti = N/A, non FAIL.** Ogni test NIST-style richiede una
   lunghezza minima (100 o 128 bit) per essere statisticamente
   significativo. Se l'output è più corto, il test è mostrato come N/A e
   non concorre al verdetto finale.

6. **Stima di min-entropia irrobustita (Clopper-Pearson + t-Tuple + LRS).**
   Gli stimatori MCV e Markov usavano prima la stima puntuale grezza
   (count/n), che su un campione piccolo sottostima sistematicamente il
   bias reale. Ora usano il limite di confidenza superiore di
   Clopper-Pearson al 99% (SP 800-90B). Aggiunti anche t-Tuple e Longest
   Repeated Substring (LRS), capaci di rilevare strutture periodiche di
   ordine superiore che MCV e Markov (ordine-1) non vedono per costruzione
   — dimostrato: su una sequenza periodica prevedibile, MCV riportava
   H_min=1.0 mentre t-Tuple/LRS la riconoscono correttamente come quasi
   priva di entropia. La min-entropia finale è il minimo fra tutti gli
   stimatori applicabili. Volutamente NON implementati: Collision Estimate
   (degenere su alfabeto binario) e Compression/Universal di Maurer
   (richiede campioni enormemente più grandi).

7. **Health test retrospettivi (RCT/APT).** Repetition Count Test e
   Adaptive Proportion Test (SP 800-90B §4.4), applicati retrospettivamente
   al campione incollato. Intercettano pattern patologici (run anomali,
   drift locale) che gli stimatori globali mediano via. Una sorgente che
   fallisce RCT o APT viene esclusa in Fase 2 indipendentemente dal suo
   H_min aggregato.

8. **Correlazione multi-lag tra sorgenti.** Il controllo precedente
   confrontava solo bit alla stessa posizione (lag 0): due sorgenti con un
   semplice sfasamento temporale apparivano indipendenti anche quando una
   era una copia shiftata dell'altra. Ora si cerca la mutua informazione
   più alta su un intervallo di lag (±8).

9. **Suite di autotest all'avvio.** Conservazione di massa del Peres
   Extractor su input casuali, coerenza del Toeplitz hashing contro una
   seconda implementazione scritta con un percorso di codice indipendente,
   vettori di test ufficiali SHA-256/SHAKE256, auto-consistenza di
   Clopper-Pearson, coerenza fra i due metodi erfc. Costruendo questa suite
   sono stati scoperti e corretti due refusi di trascrizione nelle costanti
   di test stesse — a riprova che anche il codice di verifica va
   verificato.

10. **Non incluso, onestamente.** Due tentativi di ottimizzazione
    prestazionale del Toeplitz hashing (BigInt, poi word-packing a 32 bit)
    sono stati scartati dopo benchmark/test: il primo più lento
    dell'originale, il secondo con un bug di indicizzazione irrisolto in
    tempo utile. Il ciclo bit-a-bit originale resta in uso, verificato.
    Non è presente un audit trail firmato crittograficamente (solo log
    testuale in RAM).

11. **Audit approfondito — tre bug matematici trovati e corretti.** (a)
    Riferimento errato "atteso 25%" per il rapporto di estrazione del
    Peres extractor — il valore corretto per la variante ricorsiva è 1/3
    (33.3%). (b) Off-by-one nell'Adaptive Proportion Test: il conteggio
    includeva il simbolo di riferimento confrontato con se stesso,
    gonfiando il conteggio di +1 rispetto alle W-1 prove assunte dal
    cutoff. (c) Limite artificiale (floor(n/2)) nella ricerca del Longest
    Repeated Substring, non previsto dalla specifica SP 800-90B.

12. **Semplificazioni dichiarate rese esplicite.** Il test Serial (SP
    800-22) qui implementato è in realtà un singolo chi-quadro sulle
    frequenze delle coppie di bit, non il vero test Serial ufficiale a due
    statistiche. Né Serial né ApproxEntropy usano l'estensione ciclica del
    campione richiesta dalla specifica.

13. **Peres Extractor aggiornato alla versione completa (Peres 1992).** La
    versione precedente riciclava solo il flusso Z, efficienza fissa al
    33.3%. La versione attuale ricicla ricorsivamente anche il flusso
    indicatore C — costruzione completa del paper originale — efficienza
    ~95-97% su input equo per campioni grandi, convergente all'entropia di
    Shannon della sorgente.

14. **Bug di scalabilità reale in t-Tuple/LRS, trovato e corretto.**
    Nessuno dei due stimatori limitava la lunghezza massima di pattern
    esaminata. Su una sequenza fortemente periodica il costo poteva salire
    a diversi miliardi di operazioni, bloccando la pagina per oltre 20
    secondi. Corretto con `TTUPLE_MAX_T=64` e `LRS_MAX_SEARCH_LEN=256`,
    verificati non alterare il comportamento su sorgenti realmente casuali.

## Limiti architetturali che nessuna correzione di bug elimina

- Gira in un browser: nessun controllo su swap/paging della memoria,
  nessuna protezione `mlock`.
- La stima di min-entropia dipende da un campione statico incollato
  manualmente — non sostituisce un health test in tempo reale su hardware
  fisico.
- I test statistici su un output di poche centinaia di bit hanno potenza
  limitata: un "PASS" è indicativo, non probante.
- Il test Serial implementato è un singolo chi-quadro, non il vero test
  ufficiale a due statistiche.

## Nota sulle nuove funzionalità della v2.0.0-beta2

Le funzionalità aggiunte dalla v2.0.0-beta1 in poi (modalità di combinazione
Concat/XOR/Interleave, pipeline di confronto XOR-LFSR, tetto di emissione
⌊input/2⌋, hash di integrità dell'applicazione, margine LHL selezionabile,
demo sbilanciata, assistente CSV/sensore, parsing tollerante) sono
documentate nel `CHANGELOG.md` e nei principi di design in
`SECURITY-NOTES.md`. Le 4 procedure NIST SP 800-22 nuove/aggiornate in
v2.0.0-beta2 (Serial completo, ApproxEntropy completa, Cumulative Sums,
Binary Matrix Rank) sono state sottoposte a una verifica matematica
indipendente specifica — valori analitici noti, casi avversari, tasso di
falsi positivi su 300 sequenze CSPRNG reali — descritta per esteso in
`CHANGELOG.md`. Il resto delle funzionalità nuove **non è ancora auditato**
allo stesso livello di rigore dei punti 1-14 sopra — va verificato prima di
un rilascio pubblico.
