"""Regression test: Step_13_classifyTracks_forRemains-3 must at least parse."""
import ast
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


def test_step13_classify_tracks_parses():
    """Step_13_classifyTracks_forRemains-3 had `import seaborn as sns` indented by 12 spaces: IndentationError."""
    path = ROOT / "piezo1_analysis/workFlow_2/Step_13_classifyTracks_forRemains-3"
    ast.parse(path.read_text())
