# Estrae i primi N bit meno significativi di un WAV a 16 bit e li scrive come un byte (0 o 1) per bit,
# cioe' lo stesso formato che si passa a ea_non_iid.  Uso: python3 estrai_lsb.py file.wav uscita.bin [N]
import sys, wave, array
w = wave.open(sys.argv[1]); a = array.array('h'); a.frombytes(w.readframes(w.getnframes()))
n = int(sys.argv[3]) if len(sys.argv) > 3 else 1000000
open(sys.argv[2], 'wb').write(bytes(x & 1 for x in a[:n]))
