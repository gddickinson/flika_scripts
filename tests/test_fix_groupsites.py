"""Regression test: groupSites ("2014.09.19 Regroup by Radius.py") puts every puff in exactly one site.

Before the fix, when a puff's neighbourhood (puffs within `radius`) touched two existing sites, the whole
neighbourhood was added to the first of them, so puffs already in the second site were in two sites. The returned
list then had more rows than puffs (the script writes only the first nPuffs rows, so some puffs were written twice
and others not at all), and the shared puff dicts kept the values of whichever site came last.

Rule now: a puff already in a site stays there; each unassigned puff in the neighbourhood joins the touched site
whose centre (mean x, y of its members so far) is nearest to it, ties going to the earlier site.
"""
import sys
from pathlib import Path

import numpy as np
import pytest

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from web.script_loader import load_functions  # noqa: E402

SCRIPTS = [ROOT / "2014.09.19 Regroup by Radius.py"]


def group(path, puffs, radius):
    f = load_functions(path, ["groupSites"], {"nPuffs": len(puffs)})["groupSites"]
    return f([dict(p, id=i) for i, p in enumerate(puffs)], radius)


def line_puffs():
    """Four puffs 3 px apart on a line, listed as the 1st, 4th, 2nd and 3rd along it."""
    return [{"x": 20.0 + 3 * x, "y": 20.0, "t_peak": 100.0 * i, "Amplitude": 1 + i / 4} for i, x in enumerate([0, 3, 1, 2])]


def random_puffs(seed):
    rng = np.random.default_rng(seed)
    return [{"x": float(x), "y": float(y), "t_peak": float(t), "Amplitude": float(a)}
            for x, y, t, a in zip(rng.uniform(0, 20, 40), rng.uniform(0, 20, 40), rng.integers(0, 500, 40),
                                  rng.uniform(0.2, 2, 40))]


@pytest.mark.parametrize("path", SCRIPTS, ids=["original"])
def test_line_example_has_two_disjoint_sites(path):
    out = group(path, line_puffs(), 3)
    assert len(out) == 4
    sites = {}
    for p in out:
        sites.setdefault(p["Group #"], set()).add(p["x"])
    assert sorted(map(sorted, sites.values())) == [[20.0, 23.0], [26.0, 29.0]]
    assert all(p["No. Events"] == 2 for p in out)


@pytest.mark.parametrize("path", SCRIPTS, ids=["original"])
@pytest.mark.parametrize("seed", range(6))
@pytest.mark.parametrize("radius", [np.sqrt(2), 3.0, 5.0])
def test_every_puff_in_exactly_one_site(path, seed, radius):
    puffs = random_puffs(seed)
    out = group(path, puffs, radius)
    assert sorted(p["id"] for p in out) == list(range(len(puffs)))
    by_group = {}
    for p in out:
        by_group.setdefault(p["Group #"], []).append(p)
    for members in by_group.values():
        assert all(p["No. Events"] == len(members) for p in members)
        gx = np.mean([p["x"] for p in members])
        assert all(np.isclose(p["Group x"], gx) for p in members)

