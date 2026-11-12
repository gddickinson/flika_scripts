// Puff-site regrouping demo: synthetic puff events grouped by sites_engine.js (port of groupSites, 2014).
import { rng } from './core.js';
import { groupSites } from './sites_engine.js';
import { fmt } from './ui.js';

const FW = 60, FH = 40, S = 9, W = FW * S, H = FH * S;
const COLS = ['#ffb02e', '#2ee6ff', '#ff4fd8', '#3dff8f', '#ffd23f', '#7aa8ff', '#ff5c7a', '#c792ea'];

function synth(seed) {
  const r = rng(seed), out = [];
  for (let s = 0; s < 9; s++) {
    const cx = 4 + r() * (FW - 8), cy = 4 + r() * (FH - 8), n = 1 + Math.floor(r() * 6), base = 0.5 + r();
    for (let k = 0; k < n; k++) out.push({ x: +(cx + (r() - 0.5) * 2.4).toFixed(2), y: +(cy + (r() - 0.5) * 2.4).toFixed(2),
      t_peak: Math.floor(r() * 1000), Amplitude: +(base * (0.6 + 0.8 * r())).toFixed(3) });
  }
  return out;
}
// Four puffs on a line: neighbourhoods 0-2 and 1-3 start two sites, then puff 2 touches both.
const QUIRK = [0, 3, 1, 2].map((x, i) => ({ x: 20 + x * 3, y: 20, t_peak: 100 * i, Amplitude: 1 + i / 4 }));

export function render(host) {
  host.innerHTML = `<div class="demo-grid"><div>
      <div class="stage"><canvas id="cv" width="${W}" height="${H}" aria-label="puff positions coloured by site"></canvas></div>
      <p class="small mute" id="cap"></p>
      <label for="rad">Radius <b id="rv">3</b> px</label><input id="rad" type="range" min="0.5" max="12" step="0.1" value="3">
      <button type="button" id="new" class="alt">new puffs</button><button type="button" id="quirk" class="alt">show the merge quirk</button>
    </div><div><div class="vals" id="vals"></div><p id="warn" class="callout small hide"></p></div></div>
    <h3>Sites</h3><div class="scroll" id="tbl"></div>
    <p class="small mute">"Amplitude Normalized by Fitted Line" divides each amplitude by a straight line fitted to the
      site's amplitude vs t_peak (np.linalg.lstsq), as the script does.</p>`;
  const $ = s => host.querySelector(s), g = $('#cv').getContext('2d');
  let seed = 5, puffs = synth(seed), scale = 1;
  $('#cap').textContent = `Synthetic puffs, seed ${seed} (not lab data).`;

  function draw() {
    const r = +$('#rad').value, res = groupSites(puffs, r);
    g.fillStyle = '#000'; g.fillRect(0, 0, W, H);
    res.puffs.forEach((p, i) => {
      const c = COLS[(p['Group #'] - 1) % COLS.length];
      g.strokeStyle = c; g.globalAlpha = 0.18; g.beginPath(); g.arc(p.x * S * scale, p.y * S * scale, r * S * scale, 0, 7); g.stroke(); g.globalAlpha = 1;
      g.fillStyle = c; g.beginPath(); g.arc(p.x * S * scale, p.y * S * scale, 2 + 3 * p.Amplitude, 0, 7); g.fill();
      if (res.inTwoSites.includes(i)) { g.strokeStyle = '#fff'; g.lineWidth = 2; g.beginPath(); g.arc(p.x * S * scale, p.y * S * scale, 9, 0, 7); g.stroke(); g.lineWidth = 1; }
    });
    $('#vals').innerHTML = [['puffs', puffs.length], ['sites', res.sites.length], ['puffs in two sites', res.inTwoSites.length]]
      .map(([k, v]) => `<div><b>${v}</b><span>${k}</span></div>`).join('');
    const w = $('#warn');
    w.classList.toggle('hide', !res.inTwoSites.length);
    w.innerHTML = res.inTwoSites.length ? `Puff ${res.inTwoSites.map(i => i + 1).join(', ')} ended up in two sites (ringed):
      a neighbourhood touched two existing sites and was added to the first only. The script keeps the values of the
      later site for these puffs, and writes only the first ${puffs.length} of its ${res.sites.reduce((s, x) => s + x.length, 0)} output rows.` : '';
    $('#tbl').innerHTML = `<table class="tbl"><thead><tr><th>Group #</th><th>puffs</th><th>Group x</th><th>Group y</th><th>No. Events</th><th>Max Amp</th><th>Amp / site mean</th><th>Amp / fitted line</th></tr></thead><tbody>${
      res.sites.map((s, si) => { const p = res.puffs[s[0]]; return `<tr><td style="color:${COLS[si % COLS.length]}">${si + 1}</td><td>${s.map(k => k + 1).join(', ')}</td><td>${fmt(p['Group x'], 2)}</td><td>${fmt(p['Group y'], 2)}</td><td>${s.length}</td><td>${fmt(p['Max Amp'], 3)}</td><td>${s.map(k => fmt(puffs[k].Amplitude / (s.reduce((a, j) => a + puffs[j].Amplitude, 0) / s.length), 2)).join(', ')}</td><td>${s.map(k => fmt(res.puffs[k]['Amplitude Normalized by Fitted Line'], 2)).join(', ')}</td></tr>`; }).join('')}</tbody></table>`;
  }
  $('#rad').addEventListener('input', () => { $('#rv').textContent = $('#rad').value; draw(); });
  $('#new').addEventListener('click', () => { seed++; puffs = synth(seed); $('#cap').textContent = `Synthetic puffs, seed ${seed} (not lab data).`; draw(); });
  $('#quirk').addEventListener('click', () => { puffs = QUIRK.map(p => ({ ...p })); $('#rad').value = 3; $('#rv').textContent = '3';
    $('#cap').textContent = 'Four puffs 3 px apart on a line, listed as the 1st, 4th, 2nd and 3rd along it; radius 3 px.'; draw(); });
  draw();
}
