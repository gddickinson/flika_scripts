// Neighbours demo: one frame of localisations (synthetic, or clicked in) analysed by neighbours_engine.js.
import { rng } from './core.js';
import { neighbours } from './neighbours_engine.js';
import { chart, fmt } from './ui.js';

const FW = 80, FH = 56, S = 7, W = FW * S, H = FH * S, RADII = [3, 5, 10, 20, 30];

function synth(seed, n) {
  const r = rng(seed), pts = [];
  const centres = Array.from({ length: 4 }, () => [5 + r() * (FW - 10), 5 + r() * (FH - 10)]);
  for (let i = 0; i < n; i++) {
    if (i % 2) { const [cx, cy] = centres[i % 4]; pts.push([cx + (r() - 0.5) * 8, cy + (r() - 0.5) * 8]); }
    else pts.push([r() * FW, r() * FH]);
  }
  return pts.map(([x, y]) => [Math.min(FW, Math.max(0, x)), Math.min(FH, Math.max(0, y))]);
}

export function render(host) {
  host.innerHTML = `<div class="demo-grid"><div>
      <div class="stage"><canvas id="cv" width="${W}" height="${H}" aria-label="localisations in one frame; click to add, click a point to select it"></canvas></div>
      <p class="small mute">An ${FW} x ${FH} pixel field. Synthetic points (half clustered, half uniform; not lab data). Click empty space to add a point, click a point to select it.</p>
      <label for="np">Points <b id="npv">60</b></label><input id="np" type="range" min="2" max="300" value="60">
      <label for="rad">Radius r <b id="rv">5</b> px</label><input id="rad" type="range" min="1" max="30" step="0.5" value="5">
      <label for="px">Pixel size <b id="pxv">108</b> nm</label><input id="px" type="range" min="50" max="200" value="108">
      <button type="button" id="new" class="alt">new points</button><button type="button" id="clr" class="alt">clear</button>
    </div><div><div class="vals" id="vals"></div><div id="tbl"></div></div></div><div id="hist"></div>`;
  const $ = s => host.querySelector(s), cv = $('#cv'), g = cv.getContext('2d');
  let seed = 3, pts = synth(seed, 60), sel = -1;

  function draw() {
    const r = +$('#rad').value, px = +$('#px').value;
    const res = neighbours({ frame: pts.map(() => 0), x: pts.map(p => p[0]), y: pts.map(p => p[1]) }, { pixelSize: px, radii: [...RADII, r] });
    const cnt = res.counts[r], maxC = Math.max(1, ...cnt);
    g.fillStyle = '#000'; g.fillRect(0, 0, W, H);
    if (sel >= 0 && pts[sel]) { g.strokeStyle = '#ffb02e'; g.beginPath(); g.arc(pts[sel][0] * S, pts[sel][1] * S, r * S, 0, 7); g.stroke(); }
    pts.forEach(([x, y], i) => {
      const t = cnt[i] / maxC;
      g.fillStyle = `rgb(${Math.round(46 + 209 * t)},${Math.round(230 - 150 * t)},${Math.round(255 - 39 * t)})`;
      g.beginPath(); g.arc(x * S, y * S, i === sel ? 5 : 3.2, 0, 7); g.fill();
    });
    const nn = res.nnDist_nm.filter(Number.isFinite);
    const mean = a => (a.length ? a.reduce((s, v) => s + v, 0) / a.length : NaN);
    $('#vals').innerHTML = [['localisations', pts.length], ['mean NN distance (nm)', mean(nn)],
      [`mean count within ${r} px`, mean(cnt)], ...(sel >= 0 ? [['selected: NN (nm)', res.nnDist_nm[sel]], [`selected: within ${r} px`, cnt[sel]]] : [])]
      .map(([k, v]) => `<div><b>${fmt(v, 1)}</b><span>${k}</span></div>`).join('');
    $('#tbl').innerHTML = `<h3>Columns Step_8 adds (means over points)</h3><table class="tbl"><tbody>${RADII.map(rr =>
      `<tr><td>nnCountInFrame_within_${rr}_pixels</td><td>${fmt(mean(res.counts[rr]), 2)}</td></tr>`).join('')}</tbody></table>`;
    const bins = 20, mx = Math.max(1, ...nn), h = new Array(bins).fill(0);
    nn.forEach(d => { h[Math.min(bins - 1, Math.floor(d / mx * bins))]++; });
    $('#hist').innerHTML = `<h3>Nearest-neighbour distances (nnDist_inFrame)</h3>${chart([{ x: h.map((_, i) => (i + 0.5) * mx / bins), y: h, color: '#2ee6ff', dots: true }], { w: 1040, h: 190, xlabel: 'nm', ylabel: 'points' })}`;
  }
  cv.addEventListener('click', e => {
    const b = cv.getBoundingClientRect(), x = (e.clientX - b.left) / b.width * FW, y = (e.clientY - b.top) / b.height * FH;
    const hit = pts.findIndex(([px, py]) => Math.hypot(px - x, py - y) < 1.2);
    if (hit >= 0) sel = hit; else { pts.push([x, y]); sel = pts.length - 1; }
    draw();
  });
  $('#np').addEventListener('input', () => { $('#npv').textContent = $('#np').value; pts = synth(seed, +$('#np').value); sel = -1; draw(); });
  $('#rad').addEventListener('input', () => { $('#rv').textContent = $('#rad').value; draw(); });
  $('#px').addEventListener('input', () => { $('#pxv').textContent = $('#px').value; draw(); });
  $('#new').addEventListener('click', () => { seed++; pts = synth(seed, +$('#np').value); sel = -1; draw(); });
  $('#clr').addEventListener('click', () => { pts = []; sel = -1; draw(); });
  draw();
}
