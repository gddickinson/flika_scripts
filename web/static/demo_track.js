// Track features demo: a synthetic track (or your own, typed or clicked) analysed by track_engine.js.
import { esc, rng } from './core.js';
import { analyseTrack, parseTrack, simulateTrack } from './track_engine.js';
import { chart, fmt } from './ui.js';

const W = 560, H = 420;

export function render(host) {
  host.innerHTML = `<div class="demo-grid">
    <div>
      <div class="stage"><canvas id="cv" width="${W}" height="${H}" aria-label="track plot: click to add points in draw mode"></canvas></div>
      <p class="small mute" id="cap"></p>
      <div class="seg" role="group" aria-label="track source">${['free', 'confined', 'directed', 'draw'].map(k =>
        `<button type="button" data-k="${k}">${k}</button>`).join('')}</div>
      <button type="button" id="new" class="alt">new random track</button>
      <label for="n">Points <b id="nv">60</b></label><input id="n" type="range" min="4" max="300" value="60">
      <details class="box"><summary>Paste a track</summary>
        <label for="txt">frame,x,y (or x,y) per line, in pixels</label><textarea id="txt"></textarea>
        <button type="button" id="use">analyse pasted track</button><p id="err" class="err small"></p></details>
    </div>
    <div><div class="vals" id="vals"></div><p class="small mute" id="fdnote"></p></div>
  </div>
  <div class="two"><div id="c1"></div><div id="c2"></div></div><div id="c3"></div>
  <p class="small mute">Persistence is 1 - (mean absolute turn between steps)/180: 1 for a straight line, 0 when every
    step reverses, and about 0.5 for directions with no correlation. Skewness and kurtosis are of the step projections
    onto the track's dominant axis (dashed line). Velocity is step length / frames to the next point.</p>`;
  const cv = host.querySelector('#cv'), g = cv.getContext('2d');
  let kind = 'free', seed = 1, track = null, drawn = [];
  const $ = s => host.querySelector(s);

  const make = () => {
    if (kind === 'draw') track = drawn.length ? { frame: drawn.map((_, i) => i), x: drawn.map(p => p[0]), y: drawn.map(p => p[1]) } : null;
    else track = simulateTrack(rng(seed), { n: +$('#n').value, kind });
    $('#cap').textContent = kind === 'draw' ? 'Click on the plot to add points in order (pixel units).'
      : `Synthetic ${kind} random walk, seed ${seed} (not lab data). Green = first point, red = last; circle = radius of gyration.`;
    draw();
  };

  function draw() {
    g.fillStyle = '#000'; g.fillRect(0, 0, W, H);
    if (!track || track.x.length < 3) { $('#vals').innerHTML = '<p class="mute">Need at least 3 points.</p>'; ['#c1', '#c2', '#c3'].forEach(s => { $(s).innerHTML = ''; }); return; }
    const r = analyseTrack(track);
    const xs = track.x, ys = track.y, pad = 30;
    const span = Math.max(Math.max(...xs) - Math.min(...xs), Math.max(...ys) - Math.min(...ys), 10);
    const sc = kind === 'draw' ? 1 : Math.min((W - 2 * pad) / span, (H - 2 * pad) / span);
    const ox = kind === 'draw' ? 0 : W / 2 - sc * (Math.min(...xs) + Math.max(...xs)) / 2, oy = kind === 'draw' ? 0 : H / 2 - sc * (Math.min(...ys) + Math.max(...ys)) / 2;
    const P = (x, y) => [ox + sc * x, oy + sc * y];
    const [cx, cy] = P(...r.center);
    g.strokeStyle = 'rgba(46,230,255,.35)'; g.beginPath(); g.arc(cx, cy, r.rg * sc, 0, 2 * Math.PI); g.stroke();
    g.setLineDash([6, 5]); g.strokeStyle = '#ff4fd8'; g.beginPath();
    g.moveTo(cx - r.dominant[0] * 2 * r.rg * sc, cy - r.dominant[1] * 2 * r.rg * sc); g.lineTo(cx + r.dominant[0] * 2 * r.rg * sc, cy + r.dominant[1] * 2 * r.rg * sc); g.stroke(); g.setLineDash([]);
    g.strokeStyle = '#ffb02e'; g.lineWidth = 1.6; g.beginPath();
    xs.forEach((x, i) => { const [a, b] = P(x, ys[i]); i ? g.lineTo(a, b) : g.moveTo(a, b); }); g.stroke(); g.lineWidth = 1;
    xs.forEach((x, i) => { const [a, b] = P(x, ys[i]); g.fillStyle = i === 0 ? '#3dff8f' : i === xs.length - 1 ? '#ff5c7a' : '#ffd9a0'; g.beginPath(); g.arc(a, b, i === 0 || i === xs.length - 1 ? 4.5 : 2, 0, 7); g.fill(); });
    const v = [['radius of gyration', r.rg], ['asymmetry', r.asymmetry], ['skewness', r.skewness], ['kurtosis', r.kurtosis],
      ['fractal dimension', r.fracDimension], ['net displacement', r.netDispl], ['efficiency', r.efficiency],
      ['straightness (mean cos)', r.cos_mean], ['mean sin', r.sin_mean], ['directional persistence', r.persistence],
      ['mean step (meanLag)', r.meanLag], ['track length', r.track_length], ['Rg / meanLag', r.rg_scaled],
      ['mean distance from centre', r.meanLocDistanceFromCenter], ['mean velocity', r.meanVelocity]];
    $('#vals').innerHTML = v.map(([k, x]) => `<div><b>${fmt(x)}</b><span>${esc(k)}</span></div>`).join('');
    $('#fdnote').textContent = r.fdError ? 'Fractal dimension: ' + r.fdError + ' (the script raises ValueError here).' : '';
    const steps = r.directions.map((_, i) => i);
    $('#c1').innerHTML = `<h3>Distance from origin</h3>${chart([{ x: r.lagNumber, y: r.distanceFromOrigin, color: '#2ee6ff', dots: true }], { xlabel: 'frames since start', ylabel: 'px' })}`;
    $('#c2').innerHTML = `<h3>Step direction</h3>${chart([{ x: steps, y: r.directions, color: '#ffb02e', dots: true, line: false }], { xlabel: 'step', ylabel: 'degrees (y up)' })}`;
    $('#c3').innerHTML = `<h3>Velocity</h3>${chart([{ x: track.frame, y: r.velocity, color: '#ff4fd8', dots: true }], { w: 1040, h: 200, xlabel: 'frame', ylabel: 'px / frame' })}`;
  }

  const setKind = k => { kind = k; host.querySelectorAll('[data-k]').forEach(b => b.classList.toggle('on', b.dataset.k === k)); make(); };
  host.querySelectorAll('[data-k]').forEach(b => b.addEventListener('click', () => { if (b.dataset.k === 'draw') drawn = []; setKind(b.dataset.k); }));
  $('#new').addEventListener('click', () => { seed++; if (kind === 'draw' || kind === 'pasted') kind = 'free'; setKind(kind); });
  $('#n').addEventListener('input', () => { $('#nv').textContent = $('#n').value; if (kind !== 'draw') make(); });
  cv.addEventListener('click', e => {
    if (kind !== 'draw') return;
    const b = cv.getBoundingClientRect();
    drawn.push([+((e.clientX - b.left) * W / b.width).toFixed(1), +((e.clientY - b.top) * H / b.height).toFixed(1)]);
    make();
  });
  $('#use').addEventListener('click', () => {
    try { track = parseTrack($('#txt').value); $('#err').textContent = ''; kind = 'pasted'; host.querySelectorAll('[data-k]').forEach(b => b.classList.remove('on')); $('#cap').textContent = 'Your pasted track.'; draw(); }
    catch (err) { $('#err').textContent = err.message; }
  });
  setKind('free');
}
