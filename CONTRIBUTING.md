# Come contribuire

Grazie per l'interesse! Questo progetto è nato con l'obiettivo dichiarato di essere onesto
sui propri limiti — la cronologia in [CHANGELOG.md](CHANGELOG.md) documenta apertamente
ogni bug trovato, incluso nel codice di verifica stesso. I contributi che continuano in
questo spirito sono particolarmente benvenuti.

## Tipi di contributo utili

- **Correzioni matematiche/crittografiche**: se trovi un errore nella stima di
  min-entropia, nel bound del Leftover Hash Lemma, nell'implementazione di Peres/Toeplitz/
  SHAKE256, o in qualunque altro punto del nucleo statistico/crittografico.
- **Nuovi vettori di test** per la suite di autotest (`runSelfTests()` in
  `entropy_pipeline.html`), specialmente su casi limite non ancora coperti.
- **Miglioramenti alla batteria di stima entropia** (es. implementazioni corrette e
  validate di Collision Estimate o Compression/Universal di Maurer, se qualcuno risolve i
  problemi di validità statistica su campioni piccoli discussi nel codice).
- **Traduzioni** dell'interfaccia e della documentazione.
- **Segnalazioni di bug**, anche solo comportamentali (es. un messaggio fuorviante, una
  soglia mal calibrata).

## Prima di proporre una modifica

1. **Verifica, non fidarti.** Se cambi una formula matematica o statistica, aggiungi un
   test alla suite di autotest (`runSelfTests()`) che la verifichi contro un valore noto o
   un'implementazione indipendente — non un controllo tautologico che confronta una
   formula con se stessa.
2. **Testa i casi limite**: lunghezza 0, 1, 2 bit; sorgenti tutte uguali; sequenze
   periodiche; numero di sorgenti da 1 a 4; lunghezze non multiple di 8/32/ecc.
3. **Documenta il perché**, non solo il cosa. I commenti nel codice esistente spiegano
   deliberatamente la logica di ogni scelta (es. perché Collision Estimate non è
   implementato, perché il margine LHL ha due livelli) — mantieni questo stile.
4. Se non sei sicuro che un cambiamento sia corretto, aprilo comunque come issue per
   discuterne prima di una pull request.

## Segnalare un problema

Apri una issue con:
- Cosa hai fatto (fasi eseguite, dati di input se non sensibili).
- Cosa ti aspettavi e cosa è successo invece.
- Se possibile, uno screenshot o l'output del pannello "Autotest all'avvio".

## Codice di condotta

Rispetto e chiarezza. Le critiche tecniche dirette sono benvenute (è così che questo
progetto è migliorato finora) — mantienile sul codice, non sulle persone.
