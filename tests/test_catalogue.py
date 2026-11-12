"""The catalogue describes every script from its own text."""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from web.catalogue import catalogue, stats  # noqa: E402
from web.parse_script import comments, parse_python  # noqa: E402

CAT = catalogue()


def test_counts_and_duplicates():
    s = stats(CAT)
    assert s["scripts"] >= 150 and s["duplicates"] >= 40
    # every Finder copy "x 2.py" is folded into its original, never a page of its own
    assert not any(" 2." in e["path"] or e["path"].endswith(" 2") for e in CAT["scripts"].values())
    assert any(e["duplicates"] for e in CAT["scripts"].values())


def test_every_script_has_topic_and_parses():
    topics = {t["id"] for t in CAT["topics"]}
    for e in CAT["scripts"].values():
        assert e["topic"] in topics
        assert e["parses"], (e["path"], e.get("parse_error"))


def test_purpose_comes_from_the_docstring():
    e = next(e for e in CAT["scripts"].values() if e["name"] == "2014.09.19 Regroup by Radius.py")
    assert e["purpose"][0].startswith("This file can open a Flika excel file regroup all the puffs")
    assert e["meta"]["author"] == "Kyle Ellefsen"
    assert e["runs"] == "Windows + Excel" and "puff-sites" in e["demos"]


def test_flika_steps_and_files():
    e = CAT["scripts"]["nocodozole"]
    assert e["runs"] == "FLIKA"
    sub = next(s for s in e["flika_steps"] if s["name"] == "subtract")
    assert sub["args"] == ["650"] and sub["note"] == "subtract baseline"
    v = CAT["scripts"]["piezo1-analysis-workflow-3-2-analysis-step-6-addvelocity"]
    assert "_velocity.csv" in v["outputs"][0]["via"]


def test_identical_functions_are_cross_linked():
    e = CAT["scripts"]["piezo1-analysis-workflow-3-testing-misc-calcuatergandfeatures"]
    fd = next(f for f in e["functions"] if f["name"] == "FractalDimension")
    assert len(fd["same_in"]) >= 3 and "track-features" in fd["demo"]


def test_commented_out_code_is_not_prose():
    c = [x["text"] for x in comments("# load data into df\n#df = pd.read_csv(f)\n# ----\nx = 1  # pixels\n")]
    assert c == ["load data into df", "pixels"]


def test_ipython_magics_do_not_stop_parsing():
    info = parse_python("import numpy as np\n%gui qt\ndef f(a, b=2):\n    return a\n")
    assert info["parses"] and info["magics"][0]["text"] == "%gui qt" and info["functions"][0]["args"][1]["default"] == "2"
