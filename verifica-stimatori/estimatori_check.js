// Controlla in Node (senza browser) le tre funzioni portate nella pagina (LRS, Collisione, Compressione)
// contro l'output ufficiale di ea_non_iid.  Uso:  node estimatori_check.js
// Estrae dall'HTML il blocco da "const Z99_90B" a "function combinedHmin": lo stesso codice che gira nella pagina.
const fs = require('fs'), path = require('path');
const html = fs.readFileSync(path.join(__dirname, '..', 'entropy_pipeline.html'), 'utf8');
const a = html.indexOf('const Z99_90B'), b = html.indexOf('function combinedHmin');
if (a < 0 || b < 0) { console.log('ERRORE: blocco degli stimatori non trovato'); process.exit(2); }
const F = new Function(html.slice(a, b) + '; return {lrsHmin, collisionHmin, compressionHmin};')();
let ok = 0, tot = 0, saltati = 0;
function conf(nome, mio, uff) { tot++; const e = Math.abs(mio - uff) <= 5e-7; if (e) ok++; console.log(`   ${nome.padEnd(14)} mio ${mio.toFixed(6)}  uff ${uff.toFixed(6)}  ${e ? 'OK' : 'NO'}`); }
function carica(f) {
  const p = path.join(__dirname, 'flussi', f);
  if (!fs.existsSync(p)) return null;
  if (f.endsWith('.json')) return Array.from(JSON.parse(fs.readFileSync(p, 'utf8')), c => +c);
  return Array.from(fs.readFileSync(p));
}
const VETT = [
  ['r603.json', { col: 0.544821, lrs: 0.851735 }],
  ['cic100000.bin', { col: 1.000000, comp: 0.777243, lrs: 0.988345 }],
  ['AM_rec20260921_105450_100000.bin', { col: 0.857794, comp: 0.712083, lrs: 0.987599 }],
  ['AM_rec20260921_105450_1000000.bin', { col: 0.900699, comp: 0.819077, lrs: 0.994365 }],
  ['radioFMAM_20260920_095010_1000000.bin', { col: 0.932092, comp: 0.867979, lrs: 0.994460 }],
  ['cic1000000.bin', { col: 0.916045, comp: 0.845363, lrs: 0.996300 }],
];
for (const [f, r] of VETT) {
  const bits = carica(f);
  if (!bits) { console.log('==', f, ': flusso assente, saltato'); saltati++; continue; }
  console.log('==', f);
  conf('collisione', F.collisionHmin(bits), r.col);
  if (r.comp !== undefined) conf('compressione', F.compressionHmin(bits), r.comp);
  conf('LRS', F.lrsHmin(bits), r.lrs);
}
console.log(`\nCONFRONTI RIUSCITI: ${ok} su ${tot} eseguiti (${saltati} flussi saltati perche' assenti)`);
process.exit(ok === tot ? 0 : 1);
