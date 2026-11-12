// Home: what the repo is, real counts, topics and demos.
import { api, app, esc, list, route } from './core.js';
import { RUN_HELP, runBadge } from './ui.js';

route('home', async () => {
  const info = await api('/info'), s = info.stats;
  app().innerHTML = `
  <section class="hero">
    <p class="kicker">gddickinson / flika_scripts</p>
    <h1 class="glow">FLIKA Scripts</h1>
    <p class="lead">A catalogue of the analysis scripts kept in this repository, run inside
      <a href="https://flika-org.github.io/" target="_blank" rel="noopener">FLIKA</a> or next to it: calcium-puff
      macros from 2014-2015 and the PIEZO1 single-particle-tracking workflows. Every page is read from the script itself
      (its docstring, comments, functions and settable values) with the highlighted source. Where the core
      computation is small numpy, a demo runs a JavaScript port of it in your browser.</p>
    <a class="btn" href="#/scripts">Browse and search</a><a class="btn alt" href="#/demos">Interactive demos</a>
  </section>
  <div class="tiles">
    <div class="tile"><b>${s.scripts}</b><span>scripts</span></div>
    <div class="tile"><b>${s.lines.toLocaleString()}</b><span>lines of code</span></div>
    <div class="tile"><b>${s.functions}</b><span>functions</span></div>
    <div class="tile"><b>${s.shared_functions}</b><span>functions copied between scripts</span></div>
    <div class="tile"><b>${s.duplicates}</b><span>Finder copies ("name 2.py") folded in</span></div>
    <div class="tile"><b>${s.demos}</b><span>interactive demos</span></div>
  </div>
  <h2>Where they run</h2>
  <p>${Object.entries(s.runs).sort((a, b) => b[1] - a[1]).map(([r, n]) => `${runBadge(r)} ${n} <span class="mute small">${esc(RUN_HELP[r] || '')}</span>`).join('<br>')}</p>
  <p class="small mute">Scripts that need FLIKA, Excel, ImageJ or a desktop window are documented here, not run.
    ${s.with_description} of ${s.scripts} carry a description in a docstring or header comment; the others are shown
    with their code, comments and file names only.</p>
  <h2>Topics</h2>
  <div class="grid wide">${list(info.topics, t => `<a class="card" href="#/scripts?topic=${t.id}"><b>${esc(t.title)}</b>
    <small>${t.count} script${t.count === 1 ? '' : 's'}</small><span>${esc(t.blurb)}</span></a>`)}</div>
  <h2>Interactive demos</h2>
  <div class="grid">${list(info.demos, d => `<a class="card" href="#/demo/${d.id}"><b>${esc(d.title)}</b><span>${esc(d.blurb)}</span></a>`)}
    <a class="card" href="#/training"><b>SVM training data</b><span>The 2000-track feature table committed with workflows 1 and 2, plotted by class.</span></a></div>`;
});
