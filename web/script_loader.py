"""Load named functions from a script file without running the script.

The scripts in this repo run their analysis at module level (often inside FLIKA), so they cannot be imported. This
executes only the file's import statements (skipping any that fail, e.g. flika or win32com) and the requested
top-level `def` blocks, verbatim, so tests and fixtures use the script's own code.
"""
import ast
from pathlib import Path

from .parse_script import decode


def load_functions(path: Path, names: list[str], extra: dict | None = None) -> dict:
    """{name: function} for the named top-level functions in `path`; `extra` adds globals (e.g. nPuffs)."""
    text, _ = decode(Path(path).read_bytes())
    tree = ast.parse(text)
    ns = {"__name__": "flika_script", "__file__": str(path), **(extra or {})}
    for node in tree.body:
        if isinstance(node, (ast.Import, ast.ImportFrom)):
            try:
                exec(compile(ast.Module(body=[node], type_ignores=[]), str(path), "exec"), ns)
            except Exception:  # noqa: BLE001 - a missing optional import (flika, win32com, cv2) is expected
                pass
    found = [n for n in tree.body if isinstance(n, ast.FunctionDef) and n.name in names]
    missing = set(names) - {n.name for n in found}
    if missing:
        raise KeyError(f"{path}: no top-level function {sorted(missing)}")
    exec(compile(ast.Module(body=found, type_ignores=[]), str(path), "exec"), ns)
    return {n: ns[n] for n in names}
