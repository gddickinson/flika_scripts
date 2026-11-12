// Browse and search: every script grouped by topic, filtered by text, topic, where it runs, and demos.
import { $, api, app, esc, route } from './core.js';
import { runBadge } from './ui.js';

const hay = s => [s.path, s.summary, s.text, s.functions.join(' '), s.params.join(' '), s.needs.join(' '), s.author, s.created].join(' ').toLowerCase();
const mark = (text, q) => {
  const t = esc(text);
  if (!q) return t;
  const words = q.split(/\s+/).filter(w => w.length > 1).map(w => esc(w).replace(/[.*+?^${}()|[\]\\]/g, '\\$&'));
  return words.length ? t.replace(new RegExp(`(${words.join('|')})`, 'gi'), '<mark>$1</mark>') : t;
};
// Short excerpt around the first match in the searchable text.
function snippet(s, q) {
  const w = q.split(/\s+/).find(x => x.length > 1);
  if (!w) return '';
  const fn = s.functions.find(f => f.toLowerCase().includes(w));
  if (fn) return `function <code>${mark(fn, q)}</code>`;
  const i = s.text.toLowerCase().indexOf(w);
  return i < 0 ? '' : `"${mark((i > 40 ? '...' : '') + s.text.slice(Math.max(0, i - 40), i + 90) + '...', q)}"`;
}

route('scripts', async (_, query) => {
  const cat = await api('/catalogue');
  const runs = [...new Set(cat.scripts.map(s => s.runs))].sort();
  app().innerHTML = `<h1>Browse the scripts</h1>
    <p class="lead">${cat.scripts.length} scripts in ${cat.topics.length} topics. Search covers file names, descriptions,
      comments, function and variable names.</p>
    <div class="panel filters">
      <div><label for="q">Search</label><input id="q" type="search" placeholder="e.g. radius of gyration, butterworth, KDTree" value="${esc(query.q || '')}"></div>
      <div><label for="topic">Topic</label><select id="topic"><option value="">All topics</option>
        ${cat.topics.map(t => `<option value="${t.id}"${t.id === query.topic ? ' selected' : ''}>${esc(t.title)}</option>`).join('')}</select></div>
      <div><label for="runs">Runs in</label><select id="runs"><option value="">Anywhere</option>
        ${runs.map(r => `<option${r === query.runs ? ' selected' : ''}>${esc(r)}</option>`).join('')}</select>
        <label class="chk"><input id="demo" type="checkbox"${query.demo ? ' checked' : ''}> has a demo</label></div>
    </div>
    <p id="count" class="mute small" aria-live="polite"></p><div id="results"></div>`;
  const idx = cat.scripts.map(s => [s, hay(s)]);
  const draw = () => {
    const q = $('#q').value.trim().toLowerCase(), topic = $('#topic').value, run = $('#runs').value, demo = $('#demo').checked;
    const words = q.split(/\s+/).filter(Boolean);
    const hits = idx.filter(([s, h]) => (!topic || s.topic === topic) && (!run || s.runs === run) && (!demo || s.demos.length)
      && words.every(w => h.includes(w))).map(([s]) => s);
    const params = new URLSearchParams(Object.entries({ q, topic, runs: run, demo: demo ? '1' : '' }).filter(([, v]) => v));
    history.replaceState(null, '', '#/scripts' + (params.toString() ? '?' + params : ''));
    $('#count').textContent = `${hits.length} of ${cat.scripts.length} scripts`;
    $('#results').innerHTML = cat.topics.map(t => {
      const items = hits.filter(s => s.topic === t.id);
      if (!items.length) return '';
      return `<h2 class="topic-h">${esc(t.title)} <small>${items.length}</small></h2>
        ${topic || q ? '' : `<p class="small mute">${esc(t.blurb)}</p>`}
        <ul class="slist">${items.map(s => `<li><a class="nm" href="#/script/${s.id}">${mark(s.name, q)}</a> ${runBadge(s.runs)}
          ${s.demos.length ? '<span class="tag a">demo</span>' : ''}
          <span class="sum">${s.summary ? mark(s.summary, q) : '<span class="mute">no description in the source</span>'}</span>
          <span class="meta">${s.folder ? esc(s.folder) + ' · ' : ''}${s.lines} lines${s.functions.length ? ` · ${s.functions.length} functions` : ''}${s.created ? ' · ' + esc(s.created) : ''}</span>
          ${q ? `<span class="meta">${snippet(s, q)}</span>` : ''}</li>`).join('')}</ul>`;
    }).join('') || '<p>No scripts match.</p>';
  };
  for (const id of ['#q', '#topic', '#runs', '#demo']) $(id).addEventListener('input', draw);
  draw();
});
