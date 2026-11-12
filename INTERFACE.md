# INTERFACE: flika_scripts

## Scripts (the repository's content)
| Path | What |
| --- | --- |
| `*.py`, `*.txt` at the root | 2014-2021 FLIKA macros and helpers: calcium puffs, nearest neighbours, overlays, light-sheet display, file readers |
| `piezo1_analysis/workFlow/` | PIEZO1 single-particle tracking, workflow 1 (Step_1 ... Step_9, extension-less Python files) |
| `piezo1_analysis/workFlow_2/` | workflow 2 (Step_1 ... Step_17); `old/` superseded steps; `training_data/` SVM feature table |
| `piezo1_analysis/workFlow_3/` | workflow 3: `1_preprocessing/`, `2_analysis/` (Step_1 ... Step_12), `3_postprocessing/`, `testing_misc/` |
| `peakAnalysis/` | collaborator analyses (forLuca, forMike) |

Track-feature functions (`RadiusGyrationAsymmetrySkewnessKurtosis`, `FractalDimension`, `NetDisplacementEfficiency`,
`SummedSinesCosines`) are copied, identically, into many workflow scripts; each script page links the copies.

## Web catalogue (`web/`)
| File | Contents |
| --- | --- |
| `web/app.py` | FastAPI app: `/api/info`, `/api/catalogue`, `/api/script/{id}`, `/api/demos`, `/api/training`; `STATIC_ENDPOINTS` |
| `web/catalogue.py` | `catalogue()` finds scripts, folds duplicates, links identical functions and demos; `index_entry()`, `stats()` |
| `web/parse_script.py` | `parse_python()` / `parse_imagej()`: docstring purpose, comments, functions (+ `code_hash`), values, I/O calls, FLIKA steps, needs |
| `web/topics.py` | `TOPICS` (the only curated field), `topic_of(path)` |
| `web/demos.py` | `DEMOS` (which script functions each JS engine ports), `demo_hashes()`, `training()` |
| `web/script_loader.py` | `load_functions(path, names)`: run a script's imports + named defs only |
| `web/flika_names.py` | `FLIKA_PROCESS`: FLIKA process function names (from flika 0.3.0) |
| `web/static/` | front end: `main.js` (router), `home.js`, `browse.js`, `script.js`, `highlight.js`, `demos.js`, `demo_*.js`, `training.js`, `about.js`, `ui.js`, `static_api.js`, `core.js`/`style.css` (shared kit) |
| `web/static/*_engine.js` | JS ports: `track_engine.js`, `neighbours_engine.js`, `sites_engine.js`, `signal_engine.js` (+ `*.test.mjs` node tests, `fixture.test.mjs` helper) |

Connections: `app.py` → `catalogue.py` → `parse_script.py`, `topics.py`, `demos.py`; `demos.py` hashes the ported
functions with `parse_script.code_hash`; `scripts/make_demo_fixture.py` → `script_loader.py` → `tests/fixtures/demo_cases.json` ← node tests.

## Tooling
| File | What |
| --- | --- |
| `run_web.py` | local server on 127.0.0.1:8126 |
| `scripts/build_static.py` | export the static site (all `STATIC_ENDPOINTS` as JSON) |
| `scripts/screenshots.py` | Playwright smoke test / README screenshots |
| `scripts/make_demo_fixture.py` | Python outputs of the ported functions for the node tests |
| `tests/` | `test_web.py`, `test_catalogue.py`, `test_demos.py`, `test_fix_*.py` (regressions for script fixes) |
