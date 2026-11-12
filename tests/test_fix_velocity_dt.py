"""Regression test: velocity dt in Step_6_addVelocity.py (and its copies in Step_10 and joinTracks.py).

The scripts run their analysis at module level, so the functions under test are loaded with web/script_loader.py,
which executes only the file's imports and the named `def` blocks, verbatim.
"""
import ast
import sys
from pathlib import Path

import numpy as np
import pandas as pd
import pytest

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from web.catalogue import catalogue  # noqa: E402
from web.parse_script import decode  # noqa: E402
from web.script_loader import load_functions  # noqa: E402

pytest.importorskip("tqdm")
STEP6 = ROOT / "piezo1_analysis/workFlow_3/2_analysis/Step_6_addVelocity.py"


def _two_tracks():
    """Two tracks laid out as addDiffusiontoDF leaves them (lag = distance to the next point, NaN on the last)."""
    rows = []
    for tn, frames, xs in ((1, [0, 1, 2, 4], [0.0, 1.0, 2.0, 4.0]), (2, [3, 4, 6, 7], [5.0, 6.0, 8.0, 9.0])):
        for i, (f, x) in enumerate(zip(frames, xs)):
            lag = xs[i + 1] - x if i + 1 < len(xs) else np.nan
            rows.append({"track_number": tn, "frame": f, "x": x, "y": 0.0, "lag": lag, "zeroed_X": x - xs[0],
                         "zeroed_Y": 0.0, "lagNumber": f - frames[0], "distanceFromOrigin": x - xs[0]})
    return pd.DataFrame(rows)


def test_velocity_dt_is_time_to_next_point_on_every_row():
    """dt was np.insert(frame[1:], -1, 0) - frame: the 0 went in BEFORE the last element, so the second-to-last row
    of every file got dt = -frame (masked to NaN) and lost its velocity, and meanVelocity of the last track was
    taken over one row fewer. dt must be frame[i+1] - frame[i] wherever that is positive."""
    fn = load_functions(STEP6, ["addVelocitytoDF"])["addVelocitytoDF"]
    out = fn(_two_tracks())
    dt = out["dt"].to_numpy(dtype=float)
    # track 1 rows 0-2: 1, 1, 2; last of track 1 -> next track's first frame 3 - 4 < 0 -> NaN;
    # track 2 rows: 2, 1 (the second-to-last row of the file), last row NaN.
    np.testing.assert_allclose(dt, [1, 1, 2, np.nan, 1, 2, 1, np.nan])
    assert out["velocity"].iloc[6] == pytest.approx(1.0)
    assert out.loc[out.track_number == 2, "meanVelocity"].iloc[0] == pytest.approx((1 + 1 + 1) / 3)


def test_no_script_keeps_the_misplaced_insert():
    """The same dt line was copied into Step_10 (twice) and testing_misc/joinTracks.py."""
    bad = [e["path"] for e in catalogue()["scripts"].values() if "[1:],-1,0)" in e["source"].replace(" ", "")]
    assert bad == []
