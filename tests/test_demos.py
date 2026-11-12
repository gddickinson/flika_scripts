"""The demo fixture is still what the scripts compute, and the demo registry points at real functions.

The fixture (tests/fixtures/demo_cases.json) is what the node tests compare the JS engines against.
Regenerate with: python scripts/make_demo_fixture.py
"""
import json
import math
import sys
import warnings
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "scripts"))

pytest.importorskip("sklearn")
pytest.importorskip("tqdm")

from web.demos import DEMOS, demo_hashes, training  # noqa: E402
from web.script_loader import load_functions  # noqa: E402

FIXTURE = ROOT / "tests" / "fixtures" / "demo_cases.json"


def _close(a, b, path="$"):
    if isinstance(b, dict):
        assert set(a) == set(b), path
        for k in b:
            _close(a[k], b[k], f"{path}.{k}")
    elif isinstance(b, list):
        assert len(a) == len(b), path
        for i, (x, y) in enumerate(zip(a, b)):
            _close(x, y, f"{path}[{i}]")
    elif isinstance(b, float) and isinstance(a, (int, float)):
        assert math.isclose(a, b, rel_tol=1e-9, abs_tol=1e-12), f"{path}: {a} vs {b}"
    else:
        assert a == b, f"{path}: {a!r} vs {b!r}"


def test_fixture_is_current():
    import make_demo_fixture
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        fresh = json.loads(json.dumps(make_demo_fixture.build()))
    _close(fresh, json.loads(FIXTURE.read_text()))


def test_every_demo_function_loads():
    for d in DEMOS:
        for rel, names in d["functions"]:
            assert set(load_functions(ROOT / rel, names, {"nPuffs": 0})) == set(names)
    assert len(demo_hashes()) == sum(len(n) for d in DEMOS for _, n in d["functions"])


def test_persistence_of_uncorrelated_directions_is_about_one_half():
    """The docstring said 0 means random; 1 - mean|turn|/180 gives ~0.5 for uncorrelated directions."""
    import numpy as np
    f = load_functions(ROOT / "piezo1_analysis/workFlow_3/3_postprocessing/addDirectionOfTravel.py",
                       ["calculate_directional_persistence"])["calculate_directional_persistence"]
    angles = np.random.default_rng(0).uniform(0, 360, 20000)
    assert f(angles) == pytest.approx(0.5, abs=0.01)
    assert f(np.array([0.0, 180.0, 0.0, 180.0])) == 0.0


def test_training_table():
    t = training()
    assert t["identical"] and len(t["rows"]) == 2000 and "Elected_Label" in t["columns"]
    assert t["used_by"]
