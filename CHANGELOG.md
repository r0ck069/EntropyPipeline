# Changelog — Entropy Extraction Pipeline (Peres + Toeplitz)

Tutte le build sono identificabili dalla riga `build YYYY-MM-DD.N` mostrata sotto il titolo
dell'app. Se quella riga non corrisponde all'ultima elencata qui, il browser sta mostrando
una copia in cache: ricaricare forzando lo svuotamento cache (Ctrl+Shift+R) o riaprire il
file scaricato di recente.

---

## v2.0.0-beta2 (2026-09-13) — BETA, non ancora pubblicata su GitHub

**Stato: da verificare e auditare prima del rilascio pubblico.** SHA-256 del file
`entropy_pipeline.html` di questa build:
`93e61abddabaaf452d642ba35bf72f6dae8aadf900a9c001f593a566fb4fa04a`.

### Fase 5 estesa: da 5 a 8 procedure NIST SP 800-22 (adottate da terzi, riverificate)

Dopo la revisione di alcuni analizzatori NIST SP 800-22 di terze parti (stesso autore,
lavoro precedente), tre procedure sono state adottate — dopo verifica matematica
indipendente completa, non per semplice copia:

- **Serial Test completo** (sostituisce `serialTestM2`): la versione precedente era
dichiaratamente un singolo chi-quadro senza estensione ciclica del campione, non
conforme alla specifica. La nuova versione calcola le due statistiche ufficiali
∇ψ²m e ∇²ψ²m, CON l'estensione ciclica richiesta (gli ultimi m−1 bit avvolgono
sull'inizio della sequenza).
- **Approximate Entropy completa** (sostituisce `approxEntropyM2`): stessa correzione,
estensione ciclica ora applicata come richiesto dalla specifica.
- **Cumulative Sums (Cusum) Test**, eseguito sia in direzione diretta sia inversa
(2 righe distinte, come richiede la specifica — non sono "2 metodi" dello stesso
calcolo, sono 2 esecuzioni della stessa procedura in direzioni opposte).
- **Binary Matrix Rank Test** (matrici 32×32, rango su GF(2) per eliminazione
gaussiana, confrontato con le probabilità teoriche note 0.2888/0.5776/0.1336).

**Non incluse in questa build, con motivazione esplicita**: Discrete Fourier
Transform/Spettrale, Linear Complexity (Berlekamp–Massey), Maurer's Universal
Statistical Test, Template Matching (overlapping e non), Random Excursions e
variante. Il codice sorgente di riferimento per queste procedure è stato letto e
le formule sono risultate corrette nella verifica a campione (Maurer's Universal
e Cumulative Sums controllati riga per riga contro le costanti NIST pubblicate),
ma non sono state sottoposte alla stessa suite di verifica rigorosa (blocco
matematico + casi avversari + tasso di falsi positivi su centinaia di prove
CSPRNG reali) applicata alle quattro adottate — per onestà, non vengono incluse
finché non lo saranno. In più, la maggior parte richiede campioni molto più
grandi di quelli tipici di un input incollato a mano in Fase 1 (Maurer richiede
≥387.840 bit, Random Excursions richiede molti cicli di ritorno a zero nel
random walk, Linear Complexity richiede ≥100.000 bit per piena affidabilità):
mostrerebbero quasi sempre N/A nell'uso tipico di questo strumento.

### Verifica matematica indipendente eseguita su QUESTA build (non simulata)

Prima di considerare questi 4 test integrati, sono stati eseguiti — con dati
reali, non inventati — tre livelli di verifica:

1. **Blocco matematico di base**: la nuova funzione gamma incompleta regolarizzata
(`gammq`/`igamc`, necessaria per i p-value chi-quadro) riusa la stessa
approssimazione di Lanczos già presente e testata (`logGammaLocal`), invece di
introdurne una seconda ridondante. Verificata contro valori analitici esatti
noti (Γ(0.5)=√π, Γ(6)=5!=120), contro valori critici chi-quadro tabulati
standard (P(χ²₁>3.841)≈0.05, P(χ²₁>6.635)≈0.01, P(χ²₂>9.210)≈0.01), e contro
l'identità nota gammq(0.5,x²)=erfc(x) confrontata con ENTRAMBI i metodi erfc
indipendenti già presenti nel file — tutti i controlli hanno una corrispondenza
a 4+ cifre significative.
2. **Casi avversari con esito noto a priori**: sequenze tutte-zero, tutte-uno e
alternanza 0101... sottoposte a Serial/ApproxEntropy/Cusum/Rank — tutte
correttamente FALLITE (p≈0), come deve essere per sequenze palesemente non
casuali.
3. **Tasso di falsi positivi empirico su 300 sequenze CSPRNG reali indipendenti**
(50.000 bit ciascuna, `crypto.getRandomValues`): per ciascuno degli 8 test di
Fase 5 (compresi i 4 già esistenti, riverificati per completezza), il numero
di fallimenti osservati su 300 prove è risultato entro 3 deviazioni standard
dal tasso atteso teorico (~1% per test a singolo p-value, ~2% per test che
richiedono entrambi i p-value ≥0.01). Questo è il controllo più severo
possibile per un test statistico: verifica che il tasso di falso allarme
REALE coincida con quello dichiarato, non solo che la funzione "non vada in
crash". Nessuna anomalia rilevata.
4. **Pipeline completa Fase 1→5 con sorgente CSPRNG reale**: eseguita end-to-end,
tutte le 8 righe di Fase 5 popolate con p-value plausibili sia PRE sia
POST-estrazione; il gate "N/A per bit insufficienti" del Rank Test verificato
scattare correttamente sull'output POST a 256 bit (sotto i 1024 richiesti per
una singola matrice 32×32).

Suite di autotest interna (7 controlli, incluso il fix SHAKE256 sotto) rieseguita
per intero dopo l'integrazione: tutti superati, nessuna regressione.

### Correzione di un bug reale della v2.0.0-beta1

**Il vettore di test ufficiale SHAKE256("") nell'autotest interno era troncato di un
carattere** (mancava la "f" finale: `…646ed5762` invece di `…646ed5762f`), facendo
sempre FALLIRE quell'autotest specifico anche se la funzione `shake256()` vera e
propria era — ed è rimasta — corretta (verificata contro l'implementazione nativa
`shake256` di Node.js: risultato identico byte per byte). Il bug era stato introdotto
durante la ricostruzione della coda del file (v2.0.0-beta1, oltre le 1000 righe che
GitHub tronca in visualizzazione) ed era già stato notato e corretto nel mio script di
verifica esterno di allora — ma non nel file consegnato. Trovato e corretto solo ora,
grazie a un secondo giro di test end-to-end sull'intera suite di autotest reale (non
solo sulle singole funzioni). Nessun impatto sulla sicurezza: era un falso allarme
dell'autotest, non un difetto della funzione crittografica.

### Aggiunte

5. **Margine di sicurezza LHL selezionabile (ε=2⁻ᵏ)**: menu a tendina con k=16/20/40/64/80
(era una scelta binaria fissa standard/ridotto). k=80 resta lo standard crittografico
di riferimento; qualunque k<80 richiede una conferma esplicita, una sola volta per
sessione, indipendentemente da quale valore intermedio sia stato scelto.
6. **Pulsante "Demo sbilanciata (test)"** per ciascuna delle 4 finestre di Fase 1: genera
con CSPRNG reale (`crypto.getRandomValues`, mai `Math.random()`) una sequenza
deliberatamente sbilanciata (p(1)≈0.8), per mostrare come il gate H_min<0.3 reagisce a
una sorgente scadente. Chiaramente etichettata come test, mai usata come sorgente reale
senza scelta esplicita dell'utente.
7. **Assistente opzionale "dati numerici (sensore/CSV) → bit grezzi"** (nuova card prima
di Fase 1): incolla letture numeriche (accelerometro, giroscopio, CSV di sensori) e
sceglie automaticamente scala, numero di LSB, modalità (diretto/differenza) e
interleave fra colonne tramite grid-search su un punteggio (bilanciamento 0/1 + Shannon
+ bassa autocorrelazione + lunghezza). Non genera né simula entropia: estrae solo bit
realmente presenti nei numeri forniti. I bit prodotti restano comunque soggetti alla
stessa stima rigorosa di min-entropia di ogni sorgente, una volta inviati a Fase 1.
8. **Parsing di input più tollerante in Fase 1**: oltre a binario ed esadecimale (ora con
prefissi "0x"/separatori vari tollerati), accettato anche un terzo formato — lista di
byte decimali o esadecimali separati da spazio/virgola (es. "72, 101, 108" o "0x48
0x65"). Corretto anche un bug latente della versione originale: `hexToBytes` non
validava i caratteri esadecimali (un carattere non valido produceva silenziosamente
`NaN` invece di un errore esplicito) — ora rifiuta esplicitamente.
9. **Principio di design "tag di dominio prima della concatenazione multi-sorgente"**
documentato in `SECURITY-NOTES.md` (non un cambiamento di codice: vedi la nota lì per
il perché non si applica direttamente alle modalità di combinazione bit-a-bit già
esistenti, e dove il principio equivalente è già implicitamente rispettato).

### Verifica eseguita con dati reali (non simulati), prima di questo commit

Tutte le funzionalità nuove sono state testate con un harness Node.js dedicato usando
`crypto.getRandomValues` **reale** (CSPRNG del sistema operativo, non un PRNG giocattolo)
e chiamando le funzioni effettive del file, non copie riscritte:

- **Feature 6**: demo sbilanciata generata con CSPRNG reale → proporzione di 1 osservata
89,4%→79,4% a seconda del run (atteso ≈80%), H_min misurato dal vero stimatore del tool
≈0.24, correttamente sotto la soglia di esclusione 0.3.
- **Feature 5**: su un pool reale piccolo (300 bit CSPRNG, ~87 bit di entropia assoluta
stimata), il margine standard (2⁻⁸⁰) fallisce correttamente con messaggio esplicito;
scegliendo 2⁻²⁰ si ottiene una vera finestra di conferma (`confirm()` invocato con il
messaggio corretto) e, se accettata, l'estrazione procede; se rifiutata, **nessun bit
viene prodotto** (`state.finalOut.length===0` verificato) — testato in un processo
isolato per evitare che la conferma già data in un test precedente falsasse il risultato.
- **Feature 7**: dati "sensore" con rumore realmente generato da CSPRNG sulle ultime
cifre decimali → l'assistente ha scelto autonomamente 8 LSB/valore, scala 1e6, modalità
differenza, interleave attivo (su 48 configurazioni provate), estraendo 71.992 bit
reali; inviati a una sorgente di Fase 1 tramite i veri pulsanti dell'interfaccia,
H_min misurato dal vero `analyzeSource()`: 0.46.
- **Feature 8**: casi concreti verificati (parsing tollerante con "0x"/trattini/underscore,
lista di byte con virgole e con prefisso "0x", rifiuto di caratteri non validi).
- **Suite di autotest interna**: tutti i controlli passano dopo la correzione del bug
SHAKE256 sopra descritto.

### Un risultato reale e onesto sulla min-entropia combinata di EntropyPipeline

Testando `combinedHmin()` — la funzione reale del tool, invariata rispetto alla v1 — su
bit genuinamente casuali (`crypto.getRandomValues`, fino a 2.000.000 di bit, con
generazione a blocchi per rispettare il limite di 65.536 byte per chiamata dell'API Web
Crypto): **il valore combinato riportato da EntropyPipeline resta strutturalmente
intorno a 0.40-0.45 bit/bit, anche con entropia CSPRNG perfetta e campioni molto
grandi** — non si osserva convergenza verso 1.0 aumentando n. La causa è nota e già
documentata (vedi AUDIT-NOTES.md, punto 6): lo stimatore LRS entra nel MINIMO che
determina `combinedHmin`, e LRS resta strutturalmente conservativo indipendentemente
dalla qualità della sorgente — esattamente il comportamento già descritto nel
CHANGELOG di `entropy-extractor` come motivo per cui **quel** repository esclude
deliberatamente LRS/t-Tuple dal minimo, usandoli solo come gate strutturale separato.
Misurato per confronto, sugli stessi bit reali: gli stimatori MCV e Markov *presi
singolarmente* superano regolarmente 0.95 con n≥32.000 bit (fino a MCV=0.9955 e
Markov=0.9921 su 2.000.000 di bit) — è il minimo con LRS/t-Tuple a tenere basso il
valore combinato. **Questo non è un difetto introdotto in questa beta**: è un
comportamento preesistente del nucleo matematico originale di EntropyPipeline,
invariato dalla v1. Segnalato qui per trasparenza, con dati reali alla mano, come
possibile obiettivo di una futura revisione (allineare `combinedHmin` alla scelta già
fatta da `entropy-extractor`, escludendo LRS/t-Tuple dal minimo e usandoli solo come
gate). Per confronto, `entropy-extractor`/`entropy-extractor-raw-2photo` (che già
escludono LRS/t-Tuple dal minimo) hanno raggiunto realmente H_min combinato >0.95 su
2.000.000 di bit CSPRNG reali (misurato: 0.958991) — la prova che superare 0.95 è
effettivamente raggiungibile con dati reali, quando la formula lo consente.

---

## v2.0.0-beta1 (2026-09-12) — BETA, non ancora pubblicata su GitHub

**Stato: da verificare e auditare prima del rilascio pubblico.** Questa build introduce
funzionalità nuove non ancora sottoposte allo stesso livello di audit indipendente delle
build precedenti (vedi `AUDIT-NOTES.md`, sezione finale, e `SECURITY-NOTES.md`).

### Aggiunte

1. **Modalità di combinazione multi-sorgente esplicita** (Fase 2): Concatenazione
   (default, min-entropia ≈ somma), XOR e Interleave (min-entropia stimata in modo
   conservativo come il massimo fra le sorgenti, mai la somma). XOR e Interleave sono
   bloccate automaticamente se il controllo di correlazione multi-lag (±8) già esistente
   rileva MI>0.05 fra una coppia di sorgenti attive — vedi `SECURITY-NOTES.md`, principio 3.
2. **Tetto di emissione conservativo indipendente dal bound LHL** (Fase 4): l'output non
   può mai superare ⌊bit_di_ingresso_a_questa_fase / 2⌋, verificato con un calcolo separato
   dal bound del Leftover Hash Lemma — rete di sicurezza a basso costo contro un'eventuale
   futura regressione nel calcolo del bound principale. Vedi `SECURITY-NOTES.md`, principio 2.
3. **Pipeline di confronto diagnostica XOR-LFSR**: elabora l'intera sorgente combinata
   (Fase 2) con un algoritmo indipendente (LFSR a 16 bit, seed fisso e pubblico), senza
   purificazione Peres/Toeplitz. Uso esclusivamente diagnostico — segnala un possibile
   regressione se la pipeline primaria risultasse "peggiore" di questa versione non protetta.
   Non sostituisce né integra mai l'output finale. Vedi `SECURITY-NOTES.md`, principio 4.
4. **Hash di integrità dell'applicazione**: SHA-256 del blocco `<script id="core-script">`,
   calcolato e mostrato al caricamento della pagina. Controllo diagnostico (non una firma
   digitale dell'intero file) per verificare, specialmente offline, di star eseguendo il
   codice atteso. L'hash SHA-256 dell'intero file `entropy_pipeline.html` di questa
   build (calcolato con `sha256sum`, da ricalcolare se il file viene modificato):
   `b6c4608f048adf83ea8e12c352c24814b4294f108583ebda5ba6c9ba2132ed01`.
   Nota: questo è l'hash dell'intero file, mentre il pannello "Integrità
   dell'applicazione" nella pagina mostra invece l'hash del solo blocco
   `<script id="core-script">` (i due valori sono diversi per costruzione — vedi la nota
   nel pannello stesso).

### Riorganizzazione della documentazione (nessun cambiamento funzionale)

Il pannello "Note dell'audit applicate a questa implementazione" (14 punti) e la riga di
build inline, prima incorporati direttamente nell'HTML, sono stati spostati in
`AUDIT-NOTES.md`. I principi di design trasversali (incluso il principio "mai inventare
bit", già rispettato dalle build precedenti ma non scritto esplicitamente da nessuna
parte) sono stati messi per iscritto in `SECURITY-NOTES.md`, nuovo file. L'HTML dello
strumento riporta ora solo l'essenziale operativo e i limiti indispensabili all'uso
corretto, con rimando esplicito a questi due file per il dettaglio completo.

### Nota di trasparenza su questa build

Le funzioni matematiche/crittografiche (Peres Extractor, Toeplitz hashing, SHAKE256,
stimatori di min-entropia, health test, test NIST-style) sono **invariate** rispetto alla
build 2026-09-11 — nessuna modifica al nucleo già auditato. Le funzioni nuove
(`combineSourceArrays`, `lfsrCompareExtract`, tetto di emissione, hash di integrità) sono
state verificate con una suite di test funzionali indipendente (conservazione di massa del
Peres Extractor, coerenza Toeplitz contro implementazione di riferimento, vettori ufficiali
SHA-256/SHAKE256, forma chiusa di Clopper-Pearson, coerenza fra i due metodi erfc, casi di
prova per le nuove funzioni) prima di questo commit — non sono tuttavia ancora state
sottoposte a un audit indipendente da terzi, a differenza del nucleo storico. **Non
pubblicare su GitHub prima di un audit.**

---

## build 2026-09-11 — Bug di scalabilità reale corretto: t-Tuple/LRS potevano bloccare la pagina

**Scoperto testando il porting di questi stessi stimatori (t-Tuple, LRS) in due strumenti
correlati** (che li importano da qui): né `tTupleHmin` né `longestRepeatedSubstringLen` limitavano la lunghezza massima di pattern esaminata. Su una sequenza fortemente periodica —
non un input "rotto", ma un pattern realistico da artefatto di sensore/codifica — il costo di `modeCount(L)` resta sopra la soglia (35 occorrenze) per `L` crescente fino a quasi n/8,
facendo salire il costo totale a diversi miliardi di operazioni.

- **Riprodotto**: un pattern periodico di soli 2000 bit incollato in una qualunque finestra
bloccava la pagina per oltre 20 secondi senza mai restituire una stima (verificato in un
ambiente headless senza il limite di tempo che un browser reale applicherebbe comunque
all'utente in attesa).
- **Esposizione reale, non solo teorica**: questo tool non impone un limite superiore alla
lunghezza dei bit incollati (`MIN_PASTE_BITS` è solo un minimo). Chiunque incolli una
sorgente con una struttura periodica di qualche migliaio di bit o più — es. un file audio
con un ronzio di rete non completamente filtrato, un dump con un header ripetuto per errore
— poteva bloccare la pagina.
- **Corretto** con due limiti espliciti: `TTUPLE_MAX_T=64` (lunghezza massima esaminata da
t-Tuple) e `LRS_MAX_SEARCH_LEN=256` (limite superiore della ricerca binaria di LRS).
Verificato che il limite non altera il comportamento su sorgenti realmente casuali (la più
lunga sottostringa ripetuta scala ~O(log2 n), tipicamente poche decine di bit anche su
campioni di decine di migliaia di bit — ben sotto i limiti) e che su sequenze
periodiche/strutturate la rilevazione di bassa entropia resta corretta anche limitando la
ricerca (la ripetizione resta comunque visibile entro il limite).
- Aggiunto un autotest dedicato di regressione (guardia di performance, soglia 2 secondi) per
impedire che questo bug si ripresenti inosservato.
- Nessuna modifica di comportamento per sorgenti equo/moderatamente sbilanciate: verificato
con la suite di autotest completa (nessuna regressione) più una verifica end-to-end in
Node.js dedicata a questo fix.

---

## build 2026-09-10.2 — Upgrade: Peres Extractor completo (Peres 1992)

**Scoperta durante lo sviluppo di un progetto correlato** (un secondo strumento indipendente
di estrazione entropia, poi confrontato con questo): l'implementazione del Peres Extractor
qui presente riciclava da sempre solo il flusso Z (il valore comune delle coppie uguali,
00→0, 11→1) verso il livello successivo di ricorsione — una variante che si può descrivere
come "von Neumann iterato". Il paper originale di Peres (1992) descrive invece un algoritmo
che ricicla ricorsivamente **anche** il flusso indicatore C (1 se la coppia è diseguale, 0 se
uguale), che contiene a sua volta entropia residua estraibile.

- **Prima**: efficienza di estrazione asintoticamente fissa a **1/3 (33.3%)** su input equo,
indipendentemente dalla lunghezza del campione (verificato analiticamente via serie
geometrica 1/4+1/16+1/64+...=1/3, e confermato empiricamente in build precedenti).
- **Ora**: efficienza di estrazione **~95-97%** su input equo per campioni grandi (n≥30000),
convergente all'entropia di Shannon H(p) della sorgente al crescere di n — non più un
tetto fisso indipendente dai dati. Verificato empiricamente su una scala di lunghezze
(n=128 → 76.2%, n=512 → 83.6%, n=2048 → 89.2%, n=8192 → 92.6%, n=32768 → 95.1%,
n=131072 → 96.8%) e su una scala di bias (p=0.5 → 94.5% [H=1.0], p=0.7 → 83.7% [H=0.881],
p=0.9 → 43.8% [H=0.469]), mostrando una correlazione coerente con l'entropia di Shannon
attesa in ciascun caso.
- **Invariante di conservazione della massa** riverificato da zero con la nuova logica
ricorsiva a due flussi (non solo uno): su migliaia di casi generati casualmente più tutti
gli edge case di lunghezza 0-5 bit, nessuna eccezione. Aggiunto anche un nuovo autotest
dedicato (eseguito automaticamente ad ogni caricamento pagina) che verifica l'efficienza
su un campione equo di riferimento (n=30000, soglia di allarme fissata al 70% — ampio
margine sotto il ~95-97% osservato) proprio per intercettare un'eventuale regressione
futura alla versione semplificata.
- **Conseguenza collaterale corretta**: poiché il rapporto di estrazione non è più una
costante universale (dipende ora sia dalla lunghezza sia dal bias della sorgente), il
controllo di Fase 3 che confrontava il rapporto osservato con un valore fisso atteso
(~33.3%, esso stesso frutto di una correzione in build 2026-09-10.1) non aveva più senso
ed è stato rimosso. Sostituito con un controllo che segnala solo il caso patologico di un
rapporto estremamente basso (<10%) su un campione già ampio — indicativo di una
sorgente quasi costante, non di una normale variazione statistica.
- Verificata l'intera pipeline end-to-end (Fase 1→4→doppio SHA-256) con il nuovo algoritmo:
nessuna rottura nei componenti a valle (stima di entropia, bound LHL, Toeplitz hashing).
Zero regressioni: tutti gli 8 autotest (incluso quello nuovo) superati.

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
produzione**. Vedi `ISTRUZIONI.md` per le limitazioni d'uso, `AUDIT-NOTES.md` per il
dettaglio completo delle note d'audit, e `SECURITY-NOTES.md` per i principi di design
trasversali del progetto.
