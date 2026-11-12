// Moving-average demo: signal_engine.js on a synthetic trace or pasted values.
import { rng } from './core.js';
import { movingAverage } from './signal_engine.js';
import { chart } from './ui.js';

function synth(seed, n = 300) {
  const r = rng(seed);
  return Array.from({ length: n }, (_, i) => 100 + 20 * Math.sin(i / 40) + i * 0.05 + (r() - 0.5) * 18);
}

export function render(host) {
  host.innerHTML = `<p class="small mute" id="cap"></p>
    <label for="w">Window <b id="wv">30</b> points</label><input id="w" type="range" min="1" max="150" value="30">
    <button type="button" id="new" class="alt">new trace</button>
    <div id="plot"></div>
    <details class="box"><summary>Paste values</summary><label for="txt">one number per line (or comma separated)</label>
      <textarea id="txt"></textarea><button type="button" id="use">smooth pasted values</button><p id="err" class="err small"></p></details>
    <p class="small mute">smoothing.py uses a window of len(trace)/10 on a background ROI trace, then subtracts the
      smoothed background from a track's intensity. The ends are padded with the first and last smoothed values.</p>`;
  const $ = s => host.querySelector(s);
  let seed = 2, y = synth(seed), mine = false;
  const draw = () => {
    const w = Math.min(+$('#w').value, y.length);
    const s = movingAverage(y, w), x = y.map((_, i) => i);
    $('#cap').textContent = `${mine ? 'Your values' : `Synthetic trace, seed ${seed} (not lab data)`}: ${y.length} points; window ${w}.`;
    $('#plot').innerHTML = `<div class="legend"><span style="--c:#7aa8ff">trace</span><span style="--c:#ffb02e">movingaverage()</span></div>${
      chart([{ x, y, color: '#7aa8ff', dots: true, line: false, r: 1.6, opacity: 0.6 }, { x, y: s, color: '#ffb02e' }], { w: 1040, h: 300, xlabel: 'frame', ylabel: 'intensity' })}`;
  };
  $('#w').addEventListener('input', () => { $('#wv').textContent = $('#w').value; draw(); });
  $('#new').addEventListener('click', () => { seed++; y = synth(seed); mine = false; draw(); });
  $('#use').addEventListener('click', () => {
    const v = $('#txt').value.split(/[\s,;]+/).filter(Boolean).map(Number);
    if (v.length < 2 || !v.every(Number.isFinite)) { $('#err').textContent = 'Need at least 2 numbers.'; return; }
    $('#err').textContent = ''; y = v; mine = true; draw();
  });
  draw();
}
