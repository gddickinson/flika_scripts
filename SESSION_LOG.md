# Session log

## 2026-11-11/12: web catalogue (branch web-interface)
- Added `web/` (FastAPI + static ES-module front end, port 8126), static export for GitHub Pages (workflow on
  `master`), tests. 161 scripts catalogued (45 byte-identical "name 2" Finder copies folded in), 15 topics.
  Purpose text comes only from docstrings/header comments (19 of 161 scripts have one).
- Demos with JS ports checked in node against the Python functions loaded from the scripts: track features
  (calcuateRGandFeatures + addDirectionOfTravel + Step_5/6/11), neighbours (Step_3, Step_8), puff sites (2014 Regroup
  by Radius), moving average (smoothing.py). The eigenvector sign of np.linalg.eig is reproduced (LAPACK dlanv2), so
  skewness signs match. Training-data page plots the committed SVM feature table.
- Fixes in the scripts (separate commits, regression tests `tests/test_fix_*.py`):
  - velocity `dt` used `np.insert(frame[1:], -1, 0)`, which put the 0 before the last element: the second-to-last row
    of every file lost its velocity. Now `np.append(frame[1:], 0)` (Step_6, Step_10 twice, joinTracks).
  - `Step_13_classifyTracks_forRemains-3`: an indented `import seaborn` made the file an IndentationError.
  - NumPy 2 / pandas 3: `np.cross` of 2-vectors (error in NumPy 2.5) replaced by the explicit 2D cross product in 10
    copies of SummedSinesCosines; `float(df[...]['x'])` (removed in pandas 3.0, which flika_new has) now `.iloc[0]`.
  - addDirectionOfTravel docstring said persistence 0 means random; uncorrelated directions give ~0.5.
  - NumPy >= 2.5: np.linalg.eig returns complex, so Rg/skewness/kurtosis became complex. The 9 copies now take
    `.real` of eig's output (identical on 2.4.2, checked in flika_new). eigh was not used: it flips the dominant
    eigenvector and so the sign of every skewness value (checked on the demo fixture).
- (Resolved below) Needs George: groupSites (2014 Regroup by Radius) can put a puff in two sites when a neighbourhood touches two
  existing sites (demo shows it).

## 2026-11-12: follow-up (George approved fixing groupSites)
- groupSites (2014 Regroup by Radius, both byte-identical copies): a puff whose neighbourhood touched two existing
  sites was added to the first of them while staying in the second, so it was in two sites, the output had more rows
  than puffs and the script wrote some puffs twice and dropped others. Now each puff is in exactly one site: puffs
  already in a site stay; each unassigned puff in the neighbourhood joins the touched site whose centre (mean x, y
  before this neighbourhood) is nearest, ties to the earlier site. Sites are not merged (single linkage would chain
  neighbouring sites into one). It also uses len(puff_info) instead of the global nPuffs. No parameter: the rule is
  not experiment-specific. Results change only for inputs that hit the old overlap. Regression test
  tests/test_fix_groupsites.py (30 of 39 failed before). JS port, fixture (adds the four-puffs-on-a-line case), node
  test and the demo page updated; the "puff in two sites" warning is gone.
- eig follow-up was already done in 47f67c4 (.real; eigh/eigvalsh rejected because skewness needs the eigenvector
  and eigh flips its sign); re-checked on NumPy 2.5.4 (shared venv) and 2.4 (flika_new).
- Frame interval: no open item for this repo. Velocities in the scripts are px/frame (lag / frame difference) and
  the web demo labels them so; no frame-interval setting was added, so saved columns keep their units.
