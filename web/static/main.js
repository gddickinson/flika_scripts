// Entry point: lazy page modules, the mode label, a faint intensity-trace background, then the router.
import { $, app, isStatic, lazy, route, start } from './core.js';

const PAGES = {
  'home.js': ['home'], 'browse.js': ['scripts'], 'script.js': ['script'], 'demos.js': ['demos', 'demo'],
  'training.js': ['training'], 'about.js': ['about'],
};
lazy(Object.fromEntries(Object.entries(PAGES).flatMap(([file, names]) => names.map(n => [n, () => import('./' + file)]))));
route('notfound', () => { app().innerHTML = '<h1>Not found</h1><p><a href="#/">Back to the start</a></p>'; });

$('#mode').textContent = isStatic()
  ? 'static site: catalogue read from the repository at build time; demos run in your browser'
  : 'local app: catalogue read from this checkout; demos run in your browser';

// Background: a few slowly scrolling noisy traces with occasional events. Off under prefers-reduced-motion.
function background(canvas) {
  if (!canvas || matchMedia('(prefers-reduced-motion: reduce)').matches) return;
  const g = canvas.getContext('2d'), cols = ['#ffb02e', '#2ee6ff', '#ff4fd8'];
  const fit = () => { canvas.width = innerWidth; canvas.height = innerHeight; };
  fit(); addEventListener('resize', fit);
  const traces = cols.map((c, k) => ({ c, y0: (k + 1) / 4, v: [] }));
  let last = 0;
  const tick = t => {
    requestAnimationFrame(tick);
    if (document.hidden || t - last < 50) return;
    last = t;
    g.clearRect(0, 0, canvas.width, canvas.height);
    for (const tr of traces) {
      const prev = tr.v.length ? tr.v[tr.v.length - 1] : 0;
      tr.v.push(prev * 0.85 + (Math.random() < 0.01 ? 40 : 0) + (Math.random() - 0.5) * 4);
      if (tr.v.length > canvas.width / 4) tr.v.shift();
      g.strokeStyle = tr.c; g.lineWidth = 1.2; g.beginPath();
      tr.v.forEach((v, i) => { const x = i * 4, y = tr.y0 * canvas.height - v; i ? g.lineTo(x, y) : g.moveTo(x, y); });
      g.stroke();
    }
  };
  requestAnimationFrame(tick);
}
background($('#bg'));
start();
