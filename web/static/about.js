// About: what the repo is, how to run the scripts and this site, and how the catalogue is made.
import { api, app, route } from './core.js';

route('about', async () => {
  const s = (await api('/info')).stats;
  app().innerHTML = `<h1>About</h1>
  <p class="lead">flika_scripts is George Dickinson's collection of "scripts to run from inside flika" (the repository
    README). This site catalogues them; it does not change or run them.</p>
  <h2>Running the scripts</h2>
  <p>Most scripts are meant to be opened in <a href="https://flika-org.github.io/" target="_blank" rel="noopener">FLIKA</a>'s
    script editor or console, where names such as <code>open_file</code>, <code>subtract</code>, <code>g.win</code> and
    <code>Window</code> are defined. Edit the file paths and values at the top of a script first: they point to the
    author's own folders. The PIEZO1 workflow scripts are numbered in the order they are run. Some 2014 scripts drive
    Microsoft Excel through <code>win32com</code> (Windows only); two files are ImageJ macros for ThunderSTORM.</p>
  <h2>How this catalogue is made</h2>
  <ul>
    <li>Every script is parsed with Python's <code>ast</code>: the purpose comes only from its docstring and header comments;
      settable values are top-level literal assignments; inputs and outputs are calls such as <code>read_csv</code> or
      <code>to_csv</code>; FLIKA steps are calls to FLIKA process functions.</li>
    <li>The ${s.duplicates} Finder copies named "name 2.py" are byte-identical to their originals and are listed on the
      original's page.</li>
    <li>${s.shared_functions} functions appear with identical code in more than one script; each copy links to the others.</li>
    <li>Topics are the only hand-made grouping, by folder and file name.</li>
    <li>The demos are JavaScript ports, tested in node against the Python functions loaded from the script files.</li>
  </ul>
  <h2>Run this site locally</h2>
  <pre>pip install -r requirements-web.txt
python run_web.py            # http://127.0.0.1:8126</pre>
  <p>The static copy on GitHub Pages is built by <code>scripts/build_static.py</code>.</p>
  <h2>Credits</h2>
  <p>Scripts by George Dickinson; the 2014 puff scripts by Kyle Ellefsen (their docstrings); <code>pyWinSpec.py</code> by
    Anton Loukianov (BSD, per its header). Track-feature functions are marked "Vivek's code" in the source.
    Repository licence: MIT.</p>`;
});
