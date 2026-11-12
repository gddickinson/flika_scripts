// Demos index and the #/demo/<id> router: each demo lives in its own module and exports render(host, ctx).
import { api, app, esc, list, route } from './core.js';
import { sourceList } from './ui.js';

const MODULES = { 'track-features': './demo_track.js', neighbours: './demo_neighbours.js', 'puff-sites': './demo_sites.js',
  smoothing: './demo_smoothing.js' };

route('demos', async () => {
  const [demos, cat] = await Promise.all([api('/demos'), api('/catalogue')]);
  app().innerHTML = `<h1>Interactive demos</h1>
    <p class="lead">Small numpy computations from the scripts, ported line for line to JavaScript and run in your
      browser. Each port is tested against the Python function itself (loaded from the script file) on the same inputs.
      Inputs here are synthetic or typed in by you; they are not lab data.</p>
    ${list(demos, d => `<div class="panel"><h2 style="margin-top:0"><a href="#/demo/${d.id}">${esc(d.title)}</a></h2>
      <p>${esc(d.blurb)}</p><p class="small mute">Ports:</p>${sourceList(d, cat)}</div>`)}
    <div class="panel"><h2 style="margin-top:0"><a href="#/training">SVM training data</a></h2>
      <p>Not a port: the track-feature table committed with workflows 1 and 2, which the classification steps train on.</p></div>`;
});

route('demo', async ([id]) => {
  const [demos, cat] = await Promise.all([api('/demos'), api('/catalogue')]);
  const d = demos.find(x => x.id === id);
  if (!d || !MODULES[id]) { app().innerHTML = '<h1>No such demo</h1><p><a href="#/demos">All demos</a></p>'; return; }
  app().innerHTML = `<p class="kicker"><a href="#/demos">Demo</a></p><h1>${esc(d.title)}</h1><p class="lead">${esc(d.blurb)}</p>
    <div id="demo"></div><h2>Ported from</h2>${sourceList(d, cat)}
    <p class="small mute">Engine: <code>static/${esc(d.engine)}</code>, checked by its node test against
      <code>tests/fixtures/demo_cases.json</code> (written by <code>scripts/make_demo_fixture.py</code> from the script functions).</p>`;
  (await import(MODULES[id])).render(document.getElementById('demo'), { demo: d, catalogue: cat });
});
