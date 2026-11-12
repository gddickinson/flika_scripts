// SVM training data: the feature table committed in the repo, as a scatter of any two features by class.
import { $, api, app, esc, route } from './core.js';
import { chart, fmt } from './ui.js';

const COLS = ['#ffb02e', '#2ee6ff', '#ff4fd8', '#3dff8f', '#ffd23f'];

route('training', async (_, query) => {
  const t = await api('/training');
  const num = t.columns.filter((c, i) => typeof t.rows[0][i] === 'number' && c !== 'TrackID');
  const xs = query.x && num.includes(query.x) ? query.x : 'radiusGyration', ys = query.y && num.includes(query.y) ? query.y : 'NetDispl';
  const opts = sel => num.map(c => `<option${c === sel ? ' selected' : ''}>${esc(c)}</option>`).join('');
  const li = t.columns.indexOf('Elected_Label');
  app().innerHTML = `<h1>SVM training data</h1>
    <p class="lead">The track-feature table committed in the repository: ${t.rows.length} tracks, ${t.columns.length} columns,
      labelled ${t.labels.map(l => `"${esc(l)}"`).join(', ')} in <code>Elected_Label</code>.</p>
    <p class="small mute">Files: ${t.paths.map(p => `<code>${esc(p)}</code>`).join(' and ')} (${t.identical ? 'byte-identical copies' : 'different files'}, sha1 ${esc(t.sha1.slice(0, 12))}).
      Named in: ${t.used_by.map(u => `<a href="#/script/${u.id}">${esc(u.path)}</a>`).join(', ')}.
      Units are those of the original analysis; the files do not state them.</p>
    <div class="row"><div><label for="fx">x axis</label><select id="fx">${opts(xs)}</select></div>
      <div><label for="fy">y axis</label><select id="fy">${opts(ys)}</select></div>
      <div><label class="chk"><input id="lx" type="checkbox"${query.log ? ' checked' : ''}> log10 of both axes</label></div></div>
    <div id="plot"></div><h2>Per-class medians</h2><div class="scroll" id="tbl"></div>`;
  const draw = () => {
    const fx = $('#fx').value, fy = $('#fy').value, lg = $('#lx').checked, ix = t.columns.indexOf(fx), iy = t.columns.indexOf(fy);
    const f = v => (lg ? (v > 0 ? Math.log10(v) : NaN) : v);
    history.replaceState(null, '', `#/training?x=${encodeURIComponent(fx)}&y=${encodeURIComponent(fy)}${lg ? '&log=1' : ''}`);
    const series = t.labels.map((l, k) => { const rows = t.rows.filter(r => r[li] === l);
      return { x: rows.map(r => f(r[ix])), y: rows.map(r => f(r[iy])), color: COLS[k % COLS.length], dots: true, line: false, r: 1.8, opacity: 0.55 }; });
    $('#plot').innerHTML = `<div class="legend">${t.labels.map((l, k) => `<span style="--c:${COLS[k % COLS.length]}">${esc(l)} (${series[k].x.length})</span>`).join('')}</div>
      ${chart(series, { w: 1040, h: 440, xlabel: (lg ? 'log10 ' : '') + fx, ylabel: (lg ? 'log10 ' : '') + fy })}`;
    const med = a => { const s = a.filter(Number.isFinite).sort((p, q) => p - q); return s.length ? s[Math.floor((s.length - 1) / 2)] : NaN; };
    $('#tbl').innerHTML = `<table class="tbl"><thead><tr><th>feature</th>${t.labels.map(l => `<th>${esc(l)}</th>`).join('')}</tr></thead><tbody>${
      num.map(c => `<tr><td>${esc(c)}</td>${t.labels.map(l => `<td>${fmt(med(t.rows.filter(r => r[li] === l).map(r => r[t.columns.indexOf(c)])), 3)}</td>`).join('')}</tr>`).join('')}</tbody></table>
      <p class="small mute">Median here is the lower median (the middle value, or the lower of the two middle values).</p>`;
  };
  ['#fx', '#fy', '#lx'].forEach(s => $(s).addEventListener('input', draw));
  draw();
});
