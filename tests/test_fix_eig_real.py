"""Regression test: the radius-of-gyration features stay real on NumPy >= 2.5.

From NumPy 2.5 np.linalg.eig always returns complex arrays, so radius_gyration, skewness and kurtosis became complex
(written to CSV as "(x+0j)"). Each copy now takes .real of eig's output: on NumPy <= 2.4 that is the same array, and
the eigenvector sign (which sets the sign of the skewness) is unchanged. np.linalg.eigh would flip that sign.
"""
import json
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
FX = json.loads((ROOT / "tests/fixtures/demo_cases.json").read_text())


def test_features_are_real_and_unchanged():
    f = load_functions(ROOT / "piezo1_analysis/workFlow_3/testing_misc/calcuateRGandFeatures.py",
                       ["RadiusGyrationAsymmetrySkewnessKurtosis"])["RadiusGyrationAsymmetrySkewnessKurtosis"]
    for case in FX["tracks"]:
        t = case["input"]
        with warnings.catch_warnings():
            warnings.simplefilter("ignore", RuntimeWarning)
            out = f(pd.DataFrame({"x": t["x"], "y": t["y"]}))
        for name, got in zip(["rg", "asymmetry", "skewness", "kurtosis"], out):
            assert not np.iscomplexobj(got), (t["name"], name)
            want = case[name]
            if want is None:
                assert np.isnan(got)
            else:
                assert got == pytest.approx(want, rel=1e-12, abs=1e-15), (t["name"], name)


def test_every_copy_takes_the_real_part():
    for e in catalogue()["scripts"].values():
        if "np.linalg.eig(radiusGyration_tensor)" in e["source"]:
            assert "eig_values.real, eig_vectors.real" in e["source"], e["path"]
