"""Build the script catalogue from the files in the repository.

`catalogue()` finds every script (Python, FLIKA command files and ImageJ macros), folds Finder duplicates
("name 2.py" byte-identical to "name.py") into the original, parses each file (parse_script.py), assigns a topic
(topics.py) and cross-links functions whose code is identical in several scripts and scripts that have an
interactive demo (demos.py). The result is cached; it only changes when the files do.
"""
import functools
import re
from pathlib import Path

from .demos import DEMOS, demo_hashes
from .parse_script import decode, parse_imagej, parse_python
from .topics import topic_list, topic_of

ROOT = Path(__file__).resolve().parent.parent
SKIP_DIRS = {".git", ".github", "web", "scripts", "tests", "site", "docs", "__pycache__", "node_modules", ".pytest_cache"}
SKIP_FILES = {"LICENSE", "run_web.py", "README.md", "INTERFACE.md", "SESSION_LOG.md", "CLAUDE.md"}
SCRIPT_EXT = {".py", ".txt", ".ijm", ""}
DUP = re.compile(r"^(?P<stem>.+) 2(?P<ext>\.[^.]*)?$")


def _files(root: Path) -> list[Path]:
    out = []
    for p in sorted(root.rglob("*")):
        rel = p.relative_to(root)
        if not p.is_file() or set(rel.parts[:-1]) & SKIP_DIRS or p.name in SKIP_FILES or p.name.startswith("."):
            continue
        if rel.parts[0] in SKIP_DIRS or p.suffix.lower() not in SCRIPT_EXT or p.name.startswith("requirements"):
            continue
        out.append(p)
    return out


def slug(rel: str) -> str:
    s = re.sub(r"\.(py|txt|ijm)$", "", rel)
    return re.sub(r"[^a-z0-9]+", "-", s.lower()).strip("-")


def kind_of(path: Path, text: str) -> str:
    if path.suffix == ".ijm":
        return "imagej"
    if path.suffix == ".txt":
        return "flika-macro"
    return "python"


def runs_in(kind: str, needs: list[str]) -> str:
    """Where the script runs, from what it imports and calls."""
    if kind == "imagej":
        return "ImageJ"
    if any(n.startswith("FLIKA") for n in needs):
        return "FLIKA"
    if any("Excel" in n for n in needs):
        return "Windows + Excel"
    if any(n.startswith(("a Qt", "OpenGL", "VPython", "Tk")) for n in needs):
        return "desktop GUI"
    return "Python"


def _summary(purpose: list[str]) -> str:
    if not purpose:
        return ""
    s = purpose[0]
    m = re.match(r"(.{20,220}?[.!?])(\s|$)", s)
    return m.group(1) if m else (s if len(s) <= 220 else s[:217] + "...")


def _entry(root: Path, p: Path) -> dict:
    rel = p.relative_to(root).as_posix()
    text, enc = decode(p.read_bytes())
    kind = kind_of(p, text)
    info = parse_imagej(text) if kind == "imagej" else parse_python(text)
    folder = rel.rsplit("/", 1)[0] if "/" in rel else ""
    return {"id": slug(rel), "path": rel, "name": p.name, "folder": folder, "topic": topic_of(rel), "kind": kind,
            "runs": runs_in(kind, info["needs"]), "lines": text.count("\n") + (0 if text.endswith("\n") else 1),
            "encoding": enc, "summary": _summary(info["purpose"]), **info, "source": text, "duplicates": [],
            "demos": []}


@functools.lru_cache(maxsize=4)
def catalogue(root: Path = ROOT) -> dict:
    """{'topics': [...], 'scripts': {id: entry}, 'order': [ids], 'duplicates': n} for the repo at `root`."""
    files = _files(root)
    by_rel = {f.relative_to(root).as_posix(): f for f in files}
    scripts, dup_of = {}, {}
    for rel, f in by_rel.items():
        m = DUP.match(f.name)
        if m:
            orig = f.with_name(m.group("stem") + (m.group("ext") or ""))
            if orig.exists() and orig.read_bytes() == f.read_bytes():
                dup_of[rel] = orig.relative_to(root).as_posix()
                continue
        e = _entry(root, f)
        while e["id"] in scripts:
            e["id"] += "-x"
        scripts[e["id"]] = e
    by_path = {e["path"]: e for e in scripts.values()}
    for rel, orig in dup_of.items():
        if orig in by_path:
            by_path[orig]["duplicates"].append(rel)
    _link_shared(scripts)
    _link_demos(scripts)
    topics = topic_list()
    order = sorted(scripts, key=lambda i: ([t["id"] for t in topics].index(scripts[i]["topic"]),
                                           scripts[i]["path"].lower()))
    return {"topics": topics, "scripts": scripts, "order": order, "duplicates": len(dup_of)}


def _link_shared(scripts: dict):
    """For each function, the other scripts that define a function with identical code."""
    where = {}
    for e in scripts.values():
        for fn in e["functions"]:
            where.setdefault(fn["hash"], set()).add(e["id"])
    for e in scripts.values():
        for fn in e["functions"]:
            fn["same_in"] = sorted(where[fn["hash"]] - {e["id"]})


def _link_demos(scripts: dict):
    hashes = demo_hashes()
    for e in scripts.values():
        for fn in e["functions"]:
            ids = sorted({d for h, d in hashes if h == fn["hash"]})
            if ids:
                fn["demo"] = ids
                for d in ids:
                    if d not in e["demos"]:
                        e["demos"].append(d)


def index_entry(e: dict) -> dict:
    """The fields the browse/search page needs (no source)."""
    text = " ".join(e["purpose"] + [c["text"] for c in e["comments"][:60]])
    return {k: e[k] for k in ("id", "path", "name", "folder", "topic", "kind", "runs", "lines", "summary", "needs",
                              "demos")} | {
        "created": e["meta"].get("created", ""), "author": e["meta"].get("author", ""),
        "functions": sorted({f["name"] for f in e["functions"]}), "params": [p["name"] for p in e["params"]][:40],
        "n_duplicates": len(e["duplicates"]), "text": text[:900]}


def stats(cat: dict) -> dict:
    s = cat["scripts"].values()
    runs = {}
    for e in s:
        runs[e["runs"]] = runs.get(e["runs"], 0) + 1
    shared = {f["hash"] for e in s for f in e["functions"] if f["same_in"]}
    return {"scripts": len(cat["scripts"]), "lines": sum(e["lines"] for e in s), "topics": len(cat["topics"]),
            "functions": sum(len(e["functions"]) for e in s), "duplicates": cat["duplicates"], "runs": runs,
            "shared_functions": len(shared), "demos": len(DEMOS),
            "with_description": sum(1 for e in s if e["purpose"])}
