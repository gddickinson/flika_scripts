"""Interactive demos: which script functions each one ports to JavaScript, and the training-data table.

Each demo names the canonical script and functions its JS engine reproduces; any other script that contains a
function with identical code (same AST) links to the same demo. tests/fixtures/demo_cases.json holds the Python
outputs the node tests compare against (scripts/make_demo_fixture.py).
"""
import ast
import csv
import functools
import hashlib
from pathlib import Path

from .parse_script import code_hash, decode

ROOT = Path(__file__).resolve().parent.parent
WF3 = "piezo1_analysis/workFlow_3/"

DEMOS = [
    {"id": "track-features", "title": "Track features",
     "blurb": "Radius of gyration, asymmetry, skewness, kurtosis, fractal dimension, net displacement, efficiency, "
              "straightness, step directions and directional persistence, localisation spread, and distance from "
              "origin / velocity for one track.",
     "engine": "track_engine.js",
     "functions": [(WF3 + "testing_misc/calcuateRGandFeatures.py",
                    ["RadiusGyrationAsymmetrySkewnessKurtosis", "FractalDimension", "NetDisplacementEfficiency",
                     "SummedSinesCosines", "addLagDisplacementToDF"]),
                   (WF3 + "3_postprocessing/addDirectionOfTravel.py",
                    ["calculate_direction", "calculate_directional_persistence"]),
                   (WF3 + "2_analysis/Step_11_addLocalizationError.py", ["addLocalizationError"]),
                   (WF3 + "2_analysis/Step_5_addDiffusion.py", ["addDiffusiontoDF"]),
                   (WF3 + "2_analysis/Step_6_addVelocity.py", ["addVelocitytoDF"])]},
    {"id": "neighbours", "title": "Neighbours in a frame",
     "blurb": "Nearest-neighbour distance of every localisation in a frame, and how many others lie within a radius.",
     "engine": "neighbours_engine.js",
     "functions": [(WF3 + "2_analysis/Step_3_nearestNeighbour.py", ["getNearestNeighbors", "getNN"]),
                   (WF3 + "2_analysis/Step_8_addNNcounts.py", ["countNNwithRadius", "getNNinFrame"])]},
    {"id": "puff-sites", "title": "Regroup puffs into sites",
     "blurb": "Group puff events into sites by a distance radius, with each site's mean position, event count, "
              "maximum amplitude and amplitudes normalised by the site mean and by a line fitted to amplitude vs time.",
     "engine": "sites_engine.js",
     "functions": [("2014.09.19 Regroup by Radius.py", ["groupSites"])]},
    {"id": "smoothing", "title": "Moving-average smoothing",
     "blurb": "The edge-padded moving average used to smooth a background trace before subtracting it.",
     "engine": "signal_engine.js",
     "functions": [(WF3 + "testing_misc/smoothing.py", ["movingaverage"])]},
]
TRAINING = ["piezo1_analysis/workFlow_2/training_data/tdTomato_37Degree_CytoD_training_feats.csv",
            "piezo1_analysis/workFlow/training_data/tdTomato_37Degree_CytoD_training_feats.csv"]


@functools.lru_cache(maxsize=1)
def demo_hashes() -> list[tuple[str, str]]:
    """(code hash, demo id) for every function a demo ports."""
    out = []
    for d in DEMOS:
        for rel, names in d["functions"]:
            tree = ast.parse(decode((ROOT / rel).read_bytes())[0])
            for node in tree.body:
                if isinstance(node, ast.FunctionDef) and node.name in names:
                    out.append((code_hash(node), d["id"]))
    return out


def demo_list() -> list[dict]:
    return [{k: d[k] for k in ("id", "title", "blurb", "engine")}
            | {"functions": [{"path": p, "names": n} for p, n in d["functions"]]} for d in DEMOS]


def _num(v: str):
    try:
        return float(v)
    except ValueError:
        return v


def training() -> dict:
    """The SVM training table committed in the repo (both copies are byte-identical; reports the sha1)."""
    raw = [(ROOT / p).read_bytes() for p in TRAINING]
    rows = list(csv.reader(raw[0].decode().splitlines()))
    header, body = rows[0], [[_num(v) for v in r] for r in rows[1:] if r]
    labels = sorted({r[header.index("Elected_Label")] for r in body})
    return {"paths": TRAINING, "identical": len({hashlib.sha1(r).hexdigest() for r in raw}) == 1,
            "sha1": hashlib.sha1(raw[0]).hexdigest(), "columns": header, "rows": body, "labels": labels,
            "used_by": used_by()}


def used_by() -> list[dict]:
    """Scripts whose source names the training file."""
    from .catalogue import catalogue
    name = Path(TRAINING[0]).name
    return [{"id": e["id"], "path": e["path"]} for e in catalogue()["scripts"].values() if name in e["source"]]
