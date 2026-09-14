# Principi di sicurezza e di design

Questo file raccoglie i principi che guidano le scelte di design dei tool
della famiglia EntropyPipeline / entropy-extractor / entropy-extractor-raw-2photo,
al di là del changelog build-per-build. Non è un documento legale, è una
lista di regole tecniche pensate per non essere infrante silenziosamente in
una branch futura.

## Principio 1 — Mai inventare bit

Nessuna funzione di espansione dell'output (hash non crittografico, PRNG,
KDF) deve mai produrre più bit "sicuri" di quanti ne siano stati realmente
estratti e validati prima del conditioning. Se l'output richiesto supera i
bit disponibili, la scelta corretta è **troncare o segnalare
l'insufficienza** — mai completare con bit sintetici presentati come
equivalenti in sicurezza.

Questo errore è già stato commesso una volta in un ramo sperimentale (uso
di MurmurHash, un hash non crittografico, per espandere l'output oltre i
bit realmente estratti). La correzione, quando fu applicata, introdusse
esattamente questa regola: *"la forza di sicurezza dichiarata non supera
mai la lunghezza dei bit estratti prima del conditioning."* Vale la pena
tenerlo scritto qui perché è più facile che ricapiti se non resta
documentato in un posto visibile e cercabile.

Corollario pratico: quando esiste una modalità "rigorosa" (nessuna
espansione sintetica) e una modalità opzionale con espansione HKDF, la
modalità rigorosa deve restare quella di default, e l'espansione HKDF deve
sempre essere etichettata chiaramente come "sintetica" nell'output, mai
mescolata silenziosamente ai bit reali.

## Principio 2 — Tetto di emissione indipendente dal bound principale

Oltre al bound matematico principale (Leftover Hash Lemma), ogni pipeline
applica un secondo controllo, più semplice e indipendente dalla stessa
formula: **mai più di ⌊bit_di_ingresso / 2⌋ bit in output**, verificato con
un calcolo separato da quello del bound LHL.

Il motivo non è sostituire il bound LHL — è dargli una rete di sicurezza a
basso costo. Il CHANGELOG di questo stesso progetto documenta più bug reali
proprio nel calcolo del bound LHL (unità di misura sbagliate, gate
diventato tautologico, bound ancorato in modo circolare all'output invece
che alle sorgenti). Un secondo controllo, aritmeticamente banale e separato
dalla logica del primo, non elimina quella classe di bug ma ne limita il
danno se si ripresentasse.

## Principio 3 — Le modalità di combinazione multi-sorgente non sono intercambiabili in sicurezza

- **Concatenazione**: preserva l'additività della min-entropia (≈ somma
  delle sorgenti). È la scelta di default e la più permissiva su quanti
  bit produce.
- **XOR** e **Interleave**: la proprietà "min-entropia ≈ max delle
  sorgenti" vale *solo* sotto indipendenza statistica delle sorgenti
  combinate. Per questo motivo:
  - sono **bloccate automaticamente** se il controllo di correlazione
    multi-lag (±8) già in uso per l'health-check delle sorgenti rileva
    MI > 0.05 fra una coppia qualsiasi;
  - l'entropia assoluta propagata al bound LHL in Fase 4 viene stimata in
    modo **conservativo**, usando il massimo fra le sorgenti attive e mai
    la somma, per non sovrastimare la sicurezza quando queste due modalità
    sono in uso.

## Principio 4 — Le pipeline diagnostiche/di confronto non sono mai la sorgente dell'output finale

La pipeline di confronto XOR-LFSR (introdotta in v2.0.0-beta1) esiste solo
per intercettare regressioni nella pipeline primaria (Peres + Toeplitz):
se la pipeline "senza rete di protezione" risultasse migliore di quella
purificata, è un segnale d'allarme su quest'ultima — non un'indicazione
che la sorgente grezza sia sicura di per sé, e il suo output non deve mai
essere usato come output finale dello strumento.

## Principio 5 — Trasparenza sui limiti, sempre visibile

Ogni stima statistica (min-entropia, test NIST-style) deve dichiarare
esplicitamente cosa NON è: non è una certificazione, non sostituisce la
batteria completa SP 800-90B/SP 800-22, e un "PASS" su un campione di
poche centinaia di bit è indicativo, non probante. Questo principio è
applicato nell'interfaccia (badge, banner brevi) e documentato per esteso
in `AUDIT-NOTES.md`.

## Principio 6 — Separazione di dominio quando più sorgenti alimentano una funzione di hash

Quando più input distinti vengono concatenati prima di essere passati a una
funzione di hash o KDF, il confine fra un input e l'altro va reso
inequivocabile (es. un tag/etichetta di dominio prima di ciascun pezzo, o la
lunghezza codificata esplicitamente), per evitare ambiguità del tipo
"A"+"BC" indistinguibile da "AB"+"C".

Questo principio **non si applica direttamente** alle modalità di
combinazione multi-sorgente di Fase 2 (Concat/XOR/Interleave, Principio 3):
quei bit alimentano Peres+Toeplitz, non una funzione di hash — l'estrattore
tratta l'intero pool come una sequenza indifferenziata per costruzione
matematica, quindi non c'è un "confine" da proteggere nello stesso senso.
Il principio è però già rispettato implicitamente dove conta davvero: la
derivazione del seed Toeplitz (`deriveSeedFromCpuTimestamp`) usa un
contatore esplicito a lunghezza fissa in ciascun blocco SHA-256
counter-mode, eliminando l'ambiguità sui confini fra i blocchi. Se in
futuro il progetto aggiungesse una modalità di combinazione basata su hash
(invece che sulla concatenazione di bit grezzi), questo principio andrebbe
applicato esplicitamente a quel punto — annotato qui apposta perché non
venga dimenticato quando servirà.

## Stato di audit di questi principi

I principi 1 e 5 derivano da bug/lezioni già verificati nella storia del
progetto (vedi `CHANGELOG.md` e `AUDIT-NOTES.md`). I principi 2, 3, 4 e 6
sono **nuovi con la v2.0.0-beta2** (il 6 è documentale: non introduce
codice, chiarisce solo perché il pattern non si applica qui e dove è già
implicitamente rispettato) e non sono ancora stati sottoposti allo stesso
livello di verifica indipendente degli altri — vanno controllati
esplicitamente in fase di audit prima di un rilascio pubblico.
