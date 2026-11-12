"""Write tests/fixtures/demo_cases.json: inputs and the scripts' own outputs for the JS demo engines.

Each function is loaded verbatim from its script (web/script_loader.py) and run on small seeded test inputs. The
node tests (web/static/*.test.mjs) run the JS ports on the same inputs and compare; tests/test_demos.py checks the
fixture still matches what the Python code computes now.

Run: python scripts/make_demo_fixture.py
"""
import json
import math
import sys
import warnings
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from web.demos import DEMOS  # noqa: E402
from web.script_loader import load_functions  # noqa: E402

OUT = ROOT / "tests" / "fixtures" / "demo_cases.json"


def fns(demo_id: str) -> dict:
    out = {}
    for rel, names in next(d for d in DEMOS if d["id"] == demo_id)["functions"]:
        out.update(load_functions(ROOT / rel, names, {"nPuffs": 0}))
    return out


def clean(v):
    """JSON-safe: NaN/inf -> None, numpy -> python."""
    if isinstance(v, dict):
        return {k: clean(x) for k, x in v.items()}
    if isinstance(v, (list, tuple, np.ndarray, pd.Series)):
        return [clean(x) for x in list(v)]
    if isinstance(v, (np.integer,)):
        return int(v)
    if isinstance(v, (complex, np.complexfloating)):  # NumPy >= 2.5: eig() always returns complex
        assert v.imag == 0, v
        v = v.real
    if isinstance(v, (float, np.floating)):
        return None if not math.isfinite(float(v)) else float(v)
    return v


def tracks() -> list[dict]:
    """Test tracks: free, confined and directed random walks, a gap in frames, a repeated position, a 3-point
    track and an exactly straight one (collinear: FractalDimension raises)."""
    rng = np.random.default_rng(42)
    out = []
    for name, n, drift, conf in (("free", 40, 0.0, 0.0), ("confined", 60, 0.0, 0.6), ("directed", 30, 0.8, 0.0),
                                 ("short", 3, 0.3, 0.0)):
        p = np.zeros((n, 2))
        for i in range(1, n):
            p[i] = p[i - 1] + rng.normal(0, 1, 2) + [drift, drift / 2] - conf * p[i - 1]
        p += [20, 30]
        out.append({"name": name, "frame": list(range(n)), "x": p[:, 0].tolist(), "y": p[:, 1].tolist()})
    g = {"name": "gap+repeat", "frame": [0, 1, 2, 5, 6, 7, 9], "x": [1.0, 2.0, 2.0, 4.5, 3.0, 3.5, 6.0],
         "y": [1.0, 1.5, 1.5, 0.0, 2.0, 2.5, 1.0]}
    out.append(g)
    out.append({"name": "straight", "frame": list(range(6)), "x": [0.0, 1, 2, 3, 4, 5], "y": [0.0, 2, 4, 6, 8, 10]})
    return out


def track_case(t: dict, f: dict) -> dict:
    df = pd.DataFrame({"track_number": 1, "frame": t["frame"], "x": t["x"], "y": t["y"]})
    pts = np.array(df[["x", "y"]])
    rg, asym, skew, kurt = f["RadiusGyrationAsymmetrySkewnessKurtosis"](df)
    try:
        fd = f["FractalDimension"](pts)
    except ValueError as e:
        fd = str(e)
    net, eff = f["NetDisplacementEfficiency"](pts)
    with np.errstate(invalid="ignore", divide="ignore"):
        sin_m, sin_v, cos_m, cos_v = f["SummedSinesCosines"](pts)
    angles = [f["calculate_direction"](pts[i, 0], pts[i, 1], pts[i + 1, 0], pts[i + 1, 1]) for i in range(len(pts) - 1)]
    pers = f["calculate_directional_persistence"](np.array(angles))
    loc = f["addLocalizationError"](df.copy())
    lagdf = f["addLagDisplacementToDF"](df.assign(radius_gyration=rg, n_segments=len(df)))
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        diff = f["addDiffusiontoDF"](lagdf.copy())
        vel = f["addVelocitytoDF"](diff.copy())
    return {"input": t, "rg": rg, "asymmetry": asym, "skewness": skew, "kurtosis": kurt, "fracDimension": fd,
            "netDispl": net, "efficiency": eff, "sin_mean": sin_m, "sin_vals": sin_v, "cos_mean": cos_m,
            "cos_vals": cos_v, "directions": angles, "persistence": pers,
            "distanceFromMean": loc["distanceFromMean"], "meanLocDistanceFromCenter": loc["meanLocDistanceFromCenter"][0],
            "lag": lagdf["lag"], "meanLag": lagdf["meanLag"].iloc[0], "track_length": lagdf["track_length"].iloc[0],
            "rg_scaled": lagdf["radius_gyration_scaled"].iloc[0],
            "rg_scaled_nSegments": lagdf["radius_gyration_scaled_nSegments"].iloc[0],
            "rg_scaled_trackLength": lagdf["radius_gyration_scaled_trackLength"].iloc[0],
            "distanceFromOrigin": diff["distanceFromOrigin"], "lagNumber": diff["lagNumber"],
            "d_squared": diff["d_squared"], "velocity": vel["velocity"], "dt": vel["dt"],
            "dydt": vel["dy-dt: distance"], "direction_origin": vel["direction_Relative_To_Origin"],
            "meanVelocity": vel["meanVelocity"].iloc[0]}


def neighbour_cases(f: dict) -> list[dict]:
    rng = np.random.default_rng(7)
    out = []
    for n_frames, n, spread in ((1, 25, 40.0), (3, 12, 15.0)):
        rows = [(fr, *rng.uniform(0, spread, 2)) for fr in range(n_frames) for _ in range(n)]
        rows.append((n_frames, 5.0, 5.0))  # a frame with a single localisation: NN distance is NaN
        rows.append((0, rows[0][1], rows[0][2]))  # an exact duplicate position
        df = pd.DataFrame(rows, columns=["frame", "x", "y"])
        df["x [nm]"], df["y [nm]"] = df["x"] * 108, df["y"] * 108
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            nn = f["getNN"](df.copy())
            cnt = f["getNNinFrame"](df.copy())
        out.append({"input": {"frame": df["frame"].tolist(), "x": df["x"].tolist(), "y": df["y"].tolist()},
                    "nnDist_nm": nn["nnDist_inFrame"],
                    "counts": {str(r): cnt[f"nnCountInFrame_within_{r}_pixels"] for r in [3, 5, 10, 20, 30]}})
    return out


def site_cases(path: Path) -> list[dict]:
    rng = np.random.default_rng(3)
    centres = [(10, 10), (12, 11), (30, 8), (20, 25), (40, 40)]
    puffs = []
    for k, (cx, cy) in enumerate(centres):
        for _ in range(int(rng.integers(1, 6))):
            puffs.append({"x": float(cx + rng.normal(0, 0.8)), "y": float(cy + rng.normal(0, 0.8)),
                          "t_peak": float(rng.integers(0, 500)), "Amplitude": float(rng.uniform(0.2, 2.0))})
    out = []
    for radius in (float(np.sqrt(2)), 3.0, 6.0):
        f = load_functions(path, ["groupSites"], {"nPuffs": len(puffs)})["groupSites"]
        res = f([dict(p) for p in puffs], radius)
        keys = ["x", "y", "t_peak", "Amplitude", "Group #", "Group x", "Group y", "No. Events", "Max Amp",
                "Amplitude Normalized by Site Mean", "Amplitude Normalized by Fitted Line"]
        out.append({"radius": radius, "result": [{k: p[k] for k in keys} for p in res]})
    return {"puffs": puffs, "runs": out}


def smoothing_cases(f) -> list[dict]:
    rng = np.random.default_rng(11)
    y = (np.sin(np.linspace(0, 6, 57)) + rng.normal(0, 0.3, 57)).tolist()
    return {"y": y, "runs": [{"window": w, "result": f(np.array(y), window_size=w)} for w in (1, 2, 5, 10, 20)]}


def build() -> dict:
    tf, nf = fns("track-features"), fns("neighbours")
    sites_path = ROOT / next(d for d in DEMOS if d["id"] == "puff-sites")["functions"][0][0]
    return clean({"tracks": [track_case(t, tf) for t in tracks()], "neighbours": neighbour_cases(nf),
                  "sites": site_cases(sites_path), "smoothing": smoothing_cases(fns("smoothing")["movingaverage"])})


def main():
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(build(), indent=1))
    print(f"wrote {OUT.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
