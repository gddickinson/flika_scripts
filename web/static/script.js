// One script: purpose (docstring / header comments only), what it needs, its FLIKA steps, settable values, files,
// functions, comments, duplicates and the highlighted source.
import { $, api, app, esc, route } from './core.js';
import { highlight } from './highlight.js';
import { RUN_HELP, runBadge } from './ui.js';

const lineLink = (id, n) => `<a href="#/script/${id}?line=${n}">${n}</a>`;
const val = v => (Array.isArray(v) ? `[${v.map(x => esc(JSON.stringify(x))).join(', ')}]` : esc(typeof v === 'string' ? JSON.stringify(v) : String(v)));

function table(rows, head, fn) {
  if (!rows.length) return '';
  return `<div class="scroll"><table class="tbl"><thead><tr>${head.map(h => `<th>${h}</th>`).join('')}</tr></thead><tbody>${rows.map(fn).join('')}</tbody></table></div>`;
}

function files(e) {
  const row = kind => r => `<tr><td class="ln">${lineLink(e.id, r.line)}</td><td>${kind}</td><td>${esc(r.call)}${r.via ? `<br><span class="mute">${esc(r.via)}</span>` : ''}</td></tr>`;
  const rows = [...e.inputs.map(r => row('reads')(r)), ...e.outputs.map(r => row('writes')(r)),
    ...e.displays.map(r => `<tr><td class="ln">${lineLink(e.id, r.line)}</td><td>shows</td><td>${esc(r.what)}: ${esc(r.call)}</td></tr>`)];
  return rows.length ? `<h2>Inputs and outputs</h2><p class="small mute">Calls in the code that read or write files or open windows.</p>
    <div class="scroll"><table class="tbl"><thead><tr><th>line</th><th></th><th>call</th></tr></thead><tbody>${rows.join('')}</tbody></table></div>` : '';
}

function functions(e) {
  if (!e.functions.length) return '';
  return `<h2>Functions <small class="mute">${e.functions.length}</small></h2>${e.functions.map(f => `<div class="fn">
    <code class="sig">${f.cls ? esc(f.cls) + '.' : ''}<b>${esc(f.name)}</b>(${f.args.map(a => esc(a.name) + (a.default !== null ? '=' + esc(a.default) : '')).join(', ')})</code>
    <span class="small mute"> · lines ${lineLink(e.id, f.line)}-${f.end}</span>
    ${f.demo ? f.demo.map(d => ` <a class="tag a" href="#/demo/${d}">try it: ${esc(d)}</a>`).join('') : ''}
    ${f.doc ? `<p class="small">${esc(f.doc)}</p>` : ''}
    ${f.same_in.length ? `<p class="small mute">Identical code also in: ${f.same_in.map(s => `<a href="#/script/${s.id}">${esc(s.path)}</a>`).join(', ')}</p>` : ''}
  </div>`).join('')}`;
}

function source(e, on) {
  const lines = highlight(e.source, e.kind === 'imagej' ? 'imagej' : 'python');
  return `<h2>Source <small class="mute">${e.lines} lines${e.encoding !== 'utf-8' ? ', ' + esc(e.encoding) : ''}</small></h2>
    <div class="src" tabindex="0" aria-label="source code"><table><tbody>${lines.map((l, i) =>
      `<tr id="L${i + 1}"${i + 1 === on ? ' class="on"' : ''}><td class="n">${i + 1}</td><td>${l || ' '}</td></tr>`).join('')}</tbody></table></div>`;
}

route('script', async ([id], query) => {
  const e = await api('/script/' + encodeURIComponent(id));
  const gh = `https://github.com/gddickinson/flika_scripts/blob/master/${e.path.split('/').map(encodeURIComponent).join('/')}`;
  const prose = e.comments.filter(c => !e.purpose.some(p => p.includes(c.text)));
  app().innerHTML = `
    <p class="kicker"><a href="#/scripts?topic=${e.topic}">${esc(e.topic_title)}</a></p>
    <h1>${esc(e.name)}</h1>
    <p class="path">${esc(e.path)} · <a href="${gh}" target="_blank" rel="noopener">view on GitHub</a></p>
    <p>${runBadge(e.runs)} <span class="small mute">${esc(RUN_HELP[e.runs] || '')}</span></p>
    <h2>Purpose</h2>
    ${e.purpose.length ? e.purpose.map(p => `<p>${esc(p)}</p>`).join('') + '<p class="small mute">From the script\'s docstring and header comments.</p>'
      : '<p class="mute">No description in the source: no module docstring or header comment. See the functions, comments and code below.</p>'}
    <dl class="kv">
      ${e.meta.created ? `<dt>Created</dt><dd>${esc(e.meta.created)}</dd>` : ''}
      ${e.meta.author ? `<dt>Author</dt><dd>${esc(e.meta.author)}</dd>` : ''}
      <dt>Needs</dt><dd>${e.needs.length ? e.needs.map(esc).join('; ') : 'only standard scientific Python'}</dd>
      ${e.imports.length ? `<dt>Imports</dt><dd class="mono small">${e.imports.map(esc).join(', ')}</dd>` : ''}
      ${e.duplicates.length ? `<dt>Copies</dt><dd>${e.duplicates.map(d => `<code>${esc(d)}</code>`).join(', ')} (byte-identical Finder copies)</dd>` : ''}
    </dl>
    ${e.magics.length ? `<p class="callout small">Uses IPython magics (${e.magics.map(m => `<code>${esc(m.text)}</code>`).join(', ')}): run it in IPython, Spyder or the FLIKA console.</p>` : ''}
    ${e.demos.length ? `<p class="callout a">Interactive demo of functions in this script: ${e.demos.map(d => `<a href="#/demo/${d}">${esc(d)}</a>`).join(', ')}.</p>` : ''}
    ${e.runs !== 'Python' ? `<p class="small mute">This script is documented, not run: it needs ${esc(e.runs)}.</p>` : ''}
    ${e.flika_steps.length ? `<h2>FLIKA steps</h2><p class="small mute">Calls to FLIKA process functions, in order, with the comment on the same line.</p>
      ${table(e.flika_steps, ['line', 'step', 'arguments', 'comment'], s => `<tr><td class="ln">${lineLink(e.id, s.line)}</td><td>${esc(s.name)}</td><td>${s.args.map(esc).join(', ')}</td><td>${esc(s.note || '')}</td></tr>`)}` : ''}
    ${e.imagej_steps && e.imagej_steps.length ? `<h2>ImageJ commands</h2>${table(e.imagej_steps, ['line', 'run(...)'], s => `<tr><td class="ln">${lineLink(e.id, s.line)}</td><td>${esc(s.args[0])}</td></tr>`)}` : ''}
    ${e.params.length ? `<h2>Settable values</h2><p class="small mute">Top-level assignments of literal values (edit these before running).</p>
      ${table(e.params, ['line', 'name', 'value', 'comment'], p => `<tr><td class="ln">${lineLink(e.id, p.line)}</td><td>${esc(p.name)}</td><td>${val(p.value)}${p.also ? `<br><span class="mute">later: ${p.also.map(a => `${val(a.value)} (line ${a.line})`).join(', ')}</span>` : ''}</td><td>${esc(p.note)}</td></tr>`)}` : ''}
    ${files(e)}
    ${functions(e)}
    ${prose.length ? `<details class="box"><summary>Comments in the code (${prose.length})</summary>
      ${table(prose.slice(0, 200), ['line', 'comment'], c => `<tr><td class="ln">${lineLink(e.id, c.line)}</td><td>${esc(c.text)}</td></tr>`)}</details>` : ''}
    ${source(e, +query.line || 0)}
    <div class="pager">${e.prev ? `<a href="#/script/${e.prev}">&larr; previous</a>` : '<span></span>'}<a href="#/scripts?topic=${e.topic}">all in this topic</a>${e.next ? `<a href="#/script/${e.next}">next &rarr;</a>` : '<span></span>'}</div>`;
  if (query.line) setTimeout(() => { const r = $('#L' + query.line); if (r) { r.scrollIntoView({ block: 'center' }); r.closest('.src').scrollLeft = 0; } }, 30);
});
