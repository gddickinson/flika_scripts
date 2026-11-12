// Minimal Python syntax highlighter (also used for FLIKA macros; ImageJ macros get strings/comments/numbers).
// Returns one HTML string per source line, so the caller can number lines and link to them.
import { esc } from './core.js';

const KW = new Set('False None True and as assert async await break class continue def del elif else except finally for from global if import in is lambda nonlocal not or pass raise return try while with yield var function'.split(' '));
const BI = new Set('print len range enumerate zip list dict set tuple int float str bool open min max sum abs round sorted map filter isinstance super np pd plt g self'.split(' '));
const RX = /("""[\s\S]*?(?:"""|$)|'''[\s\S]*?(?:'''|$)|[rRbBfFuU]{0,2}"(?:\\.|[^"\\\n])*"?|[rRbBfFuU]{0,2}'(?:\\.|[^'\\\n])*'?)|(#[^\n]*|\/\/[^\n]*)|(@[\w.]+)|(\b\d[\d_]*\.?\d*(?:[eE][+-]?\d+)?j?\b|\.\d+\b)|([A-Za-z_]\w*)/g;

export function highlight(src, kind = 'python') {
  const toks = [];
  let last = 0, m, prevDef = false;
  RX.lastIndex = 0;
  while ((m = RX.exec(src))) {
    if (m.index > last) toks.push(['', src.slice(last, m.index)]);
    let cls = '';
    if (m[1]) cls = 's'; else if (m[2]) cls = m[2].startsWith(kind === 'imagej' ? '//' : '#') ? 'c' : '';
    else if (m[3]) cls = 'd'; else if (m[4]) cls = 'n';
    else if (m[5]) cls = prevDef ? 'f' : KW.has(m[5]) ? 'k' : BI.has(m[5]) ? 'b' : '';
    if (m[5] || m[1] || m[2]) prevDef = m[5] === 'def' || m[5] === 'class';
    toks.push([cls, m[0]]);
    last = RX.lastIndex;
  }
  if (last < src.length) toks.push(['', src.slice(last)]);
  const lines = [''];
  for (const [cls, text] of toks) {
    text.split('\n').forEach((part, i) => {
      if (i) lines.push('');
      if (part) lines[lines.length - 1] += cls ? `<span class="tk-${cls}">${esc(part)}</span>` : esc(part);
    });
  }
  return lines;
}
