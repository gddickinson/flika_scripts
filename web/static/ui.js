// Small shared UI pieces: run badges, number formatting, an SVG line/scatter chart.
import { esc } from './core.js';

export const runBadge = r => `<span class="run ${esc(r.split(' ')[0])}" title="where it runs">${esc(r)}</span>`;
export const RUN_HELP = {
  FLIKA: 'needs FLIKA: run it from FLIKA\'s script editor or console', Python: 'plain Python (numpy / pandas / ...)',
  'Windows + Excel': 'drives Microsoft Excel through win32com (Windows only)', ImageJ: 'an ImageJ / Fiji macro',
  'desktop GUI': 'opens a Qt / OpenGL / Tk / VPython window',
};

export function fmt(v, d = 4) {
  if (v === null || v === undefined || Number.isNaN(v)) return 'NaN';
  if (typeof v !== 'number') return esc(v);
  if (v === 0) return '0';
  const a = Math.abs(v);
  return a >= 1e5 || a < 1e-3 ? v.toExponential(2) : String(+v.toFixed(d));
}

// series: [{ x: [...], y: [...], color, dots?, line? }]. Returns an SVG string.
export function chart(series, { w = 520, h = 220, xlabel = '', ylabel = '', title = '' } = {}) {
  const pts = series.flatMap(s => s.x.map((x, i) => [x, s.y[i]])).filter(([x, y]) => Number.isFinite(x) && Number.isFinite(y));
  if (!pts.length) return '<p class="mute small">nothing to plot</p>';
  let [x0, x1] = [Math.min(...pts.map(p => p[0])), Math.max(...pts.map(p => p[0]))];
  let [y0, y1] = [Math.min(...pts.map(p => p[1])), Math.max(...pts.map(p => p[1]))];
  if (x0 === x1) { x0 -= 1; x1 += 1; } if (y0 === y1) { y0 -= 1; y1 += 1; }
  const L = 52, R = 10, T = 12, B = 34, X = x => L + (x - x0) / (x1 - x0) * (w - L - R), Y = y => h - B - (y - y0) / (y1 - y0) * (h - T - B);
  let s = `<svg class="chart" viewBox="0 0 ${w} ${h}" role="img" aria-label="${esc(title || ylabel)}">`;
  s += `<line class="axis" x1="${L}" y1="${h - B}" x2="${w - R}" y2="${h - B}"/><line class="axis" x1="${L}" y1="${T}" x2="${L}" y2="${h - B}"/>`;
  s += `<text x="${L}" y="${h - B + 14}">${fmt(x0, 2)}</text><text x="${w - R}" y="${h - B + 14}" text-anchor="end">${fmt(x1, 2)}</text>`;
  s += `<text x="${L - 4}" y="${h - B}" text-anchor="end">${fmt(y0, 2)}</text><text x="${L - 4}" y="${T + 8}" text-anchor="end">${fmt(y1, 2)}</text>`;
  s += `<text x="${(L + w - R) / 2}" y="${h - 4}" text-anchor="middle">${esc(xlabel)}</text>`;
  s += `<text x="12" y="${(T + h - B) / 2}" text-anchor="middle" transform="rotate(-90 12 ${(T + h - B) / 2})">${esc(ylabel)}</text>`;
  for (const se of series) {
    const p = se.x.map((x, i) => [x, se.y[i]]).filter(([x, y]) => Number.isFinite(x) && Number.isFinite(y));
    if (se.line !== false && p.length > 1) s += `<polyline fill="none" stroke="${se.color}" stroke-width="1.6" points="${p.map(([x, y]) => `${X(x).toFixed(1)},${Y(y).toFixed(1)}`).join(' ')}"/>`;
    if (se.dots) s += p.map(([x, y]) => `<circle cx="${X(x).toFixed(1)}" cy="${Y(y).toFixed(1)}" r="${se.r || 2.4}" fill="${se.color}" opacity="${se.opacity || 0.9}"/>`).join('');
  }
  return s + '</svg>';
}

// Which scripts a demo ports, as links.
export function sourceList(demo, catalogue) {
  const ids = new Map(catalogue.scripts.map(s => [s.path, s.id]));
  return `<ul class="src-list">${demo.functions.map(f => `<li><a href="#/script/${esc(ids.get(f.path) || '')}">${esc(f.path)}</a>: <code>${f.names.map(esc).join('</code>, <code>')}</code></li>`).join('')}</ul>`;
}
