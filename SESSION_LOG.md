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
- Needs George: groupSites (2014 Regroup by Radius) can put a puff in two sites when a neighbourhood touches two
  existing sites (demo shows it); NumPy >= 2.5 makes np.linalg.eig return complex, so Rg/skewness columns would be
  complex there (flika_new has 2.4.2, unaffected).
