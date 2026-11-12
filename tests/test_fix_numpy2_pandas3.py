"""Regression tests: the PIEZO1 track functions run on NumPy 2 and pandas 3.

np.cross() of 2-vectors is deprecated in NumPy 2.0-2.4 and an error from 2.5, and float() of a one-row pandas Series
was removed in pandas 3.0 (George's flika_new environment has pandas 3.0.1), so SummedSinesCosines and
addDiffusiontoDF stopped running. The replacements compute the same numbers.
"""
import sys
import warnings
from pathlib import Path

import numpy as np
import pandas as pd
import pytest

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from web.catalogue import catalogue  # noqa: E402
from web.script_loader import load_functions  # noqa: E402

pytest.importorskip("tqdm")
pytest.importorskip("sklearn")
WF3 = ROOT / "piezo1_analysis/workFlow_3"


def test_summed_sines_cosines_runs_and_matches_the_2d_cross_product():
    f = load_functions(WF3 / "testing_misc/calcuateRGandFeatures.py", ["SummedSinesCosines"])["SummedSinesCosines"]
    pts = np.array([[0.0, 0.0], [1.0, 0.0], [1.0, 1.0], [0.0, 1.0]])  # two left turns of 90 degrees
    with warnings.catch_warnings():
        warnings.simplefilter("error")
        sin_mean, sin_vals, cos_mean, _ = f(pts)
    np.testing.assert_allclose(sin_vals, [1.0, 1.0])
    assert cos_mean == pytest.approx(0.0)


def test_add_diffusion_runs_on_pandas_3():
    f = load_functions(WF3 / "2_analysis/Step_5_addDiffusion.py", ["addDiffusiontoDF"])["addDiffusiontoDF"]
    df = pd.DataFrame({"track_number": [1, 1, 1], "frame": [5, 6, 7], "x": [1.0, 4.0, 1.0], "y": [1.0, 5.0, 1.0],
                       "lag": [5.0, 5.0, np.nan]})
    out = f(df)
    np.testing.assert_allclose(out["distanceFromOrigin"], [0.0, 5.0, 0.0])
    np.testing.assert_allclose(out["lagNumber"], [0, 1, 2])


def test_no_script_keeps_the_removed_calls():
    for e in catalogue()["scripts"].values():
        assert "np.cross(ab, bc)" not in e["source"], e["path"]
        assert "== minFrame]['x'])" not in e["source"], e["path"]
