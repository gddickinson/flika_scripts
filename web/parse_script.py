"""Read one script file and describe it from its own text: docstrings, comments, functions, settable values, files read
and written, imports and what it needs to run. Nothing here is written by hand about a script; every field is taken
from the source (the catalogue's topic is the only curated field, see topics.py).
"""
import ast
import hashlib
import io
import re
import tokenize

from .flika_names import FLIKA_PROCESS

# Calls whose first argument (or receiver) names a file the script reads / writes.
READ_CALLS = {"read_csv", "read_excel", "read_table", "read_json", "read_hdf", "load", "loadtxt", "genfromtxt", "imread",
              "TiffFile", "open_workbook", "open_file", "open_points", "SpeFile", "File", "Open", "glob", "iglob",
              "listdir", "load_points", "loadPointData", "loadImgData"}
WRITE_CALLS = {"to_csv", "to_excel", "to_json", "to_hdf", "save", "savez", "savetxt", "imsave", "imwrite", "save_file",
               "savefig", "dump", "Save", "save_points", "save_rois", "write", "writeMacro", "copy", "move", "rename"}
DISPLAY_CALLS = {"Window": "opens a FLIKA window", "show": "shows a plot", "imshow": "shows an image",
                 "GLViewWidget": "opens a 3D OpenGL view", "plot": "draws a plot"}
NEEDS = [  # (test on the import / name set, label)
    (lambda m, n: "flika" in m or n,
     "FLIKA (run from the FLIKA script editor or console)"),
    (lambda m, n: "win32com" in m, "Windows with Microsoft Excel (win32com)"),
    (lambda m, n: "xlrd" in m, "xlrd (old .xls workbooks)"),
    (lambda m, n: {"qtpy", "PyQt5", "PyQt4", "pyqtgraph"} & m, "a Qt desktop session (pyqtgraph / Qt)"),
    (lambda m, n: {"OpenGL"} & m or "pyqtgraph.opengl" in m, "OpenGL"),
    (lambda m, n: "visual" in m, "VPython (visual)"),
    (lambda m, n: "cv2" in m, "OpenCV (cv2)"),
    (lambda m, n: "nibabel" in m, "nibabel"),
    (lambda m, n: "trackpy" in m, "trackpy"),
    (lambda m, n: "sklearn" in m, "scikit-learn"),
    (lambda m, n: "tkinter" in m, "Tk (tkinter)"),
]
DOC_META = re.compile(r"^\s*(created on|@author|@email|author:)", re.I)


def decode(raw: bytes) -> tuple[str, str]:
    """Source text and the encoding it was read with (utf-8, else cp1252 for old Windows files)."""
    for enc in ("utf-8", "cp1252", "latin-1"):
        try:
            return raw.decode(enc).replace("\r\n", "\n").replace("\r", "\n"), enc
        except UnicodeDecodeError:
            continue
    raise ValueError("undecodable")


def _clean_doc(doc: str) -> tuple[list[str], dict]:
    """Split a docstring into prose paragraphs and 'Created on' / '@author' metadata."""
    meta, keep = {}, []
    for line in doc.splitlines():
        s = line.strip()
        m = re.match(r"created on\s*:?\s*(.+)", s, re.I)
        if m:
            meta["created"] = m.group(1).strip()
            continue
        m = re.match(r"@?author\s*:?\s*(.+)", s, re.I)
        if m:
            meta["author"] = m.group(1).strip()
            continue
        keep.append(line.rstrip())
    paras, cur = [], []
    for line in keep:
        if line.strip():
            cur.append(line.strip())
        elif cur:
            paras.append(" ".join(cur))
            cur = []
    if cur:
        paras.append(" ".join(cur))
    return paras, meta


def _is_code(text: str) -> bool:
    """True when a comment's text is commented-out code rather than prose."""
    t = text.strip()
    if not t or re.fullmatch(r"[#=*\-_~ ]+", t):
        return True  # rulers
    if t.startswith(("%", "!")):
        return True
    try:
        tree = ast.parse(t)
    except SyntaxError:
        return False
    body = tree.body
    if len(body) == 1 and isinstance(body[0], ast.Expr) and isinstance(body[0].value, (ast.Name, ast.Constant)):
        return False  # a bare word or number is prose ("plot", "2")
    return True


def comments(text: str) -> list[dict]:
    """Prose comments (line, text), with commented-out code and ruler lines dropped."""
    out = []
    try:
        toks = list(tokenize.generate_tokens(io.StringIO(text).readline))
        items = [(t.start[0], t.string) for t in toks if t.type == tokenize.COMMENT]
    except (tokenize.TokenError, IndentationError, SyntaxError):
        items = [(i + 1, l.strip()) for i, l in enumerate(text.splitlines()) if l.strip().startswith(("#", "//"))]
    for line, raw in items:
        s = raw.lstrip("#/").strip().strip("#").strip()
        if raw.startswith("#!") or re.match(r"-\*-\s*coding", s) or _is_code(s):
            continue
        out.append({"line": line, "text": s})
    return out


def _literal(node):
    try:
        v = ast.literal_eval(node)
    except (ValueError, TypeError, SyntaxError, MemoryError, RecursionError):
        return None, False
    if isinstance(v, (str, int, float, bool)) or v is None:
        return v, True
    if isinstance(v, (list, tuple)) and len(v) <= 20 and all(isinstance(x, (str, int, float, bool)) for x in v):
        return list(v), True
    return None, False


def _short(node, n=110) -> str:
    try:
        s = ast.unparse(node)
    except Exception:  # pragma: no cover - unparse handles every node the parser makes
        return "?"
    s = " ".join(s.split())
    return s if len(s) <= n else s[: n - 3] + "..."


def _call_name(call: ast.Call) -> str:
    f = call.func
    if isinstance(f, ast.Name):
        return f.id
    if isinstance(f, ast.Attribute):
        return f.attr
    return ""


def _receiver(call: ast.Call) -> str:
    f = call.func
    return _short(f.value, 40) if isinstance(f, ast.Attribute) else ""


def _top_assignments(body, lines, out, seen):
    """Module-level (and `if __name__ == '__main__'`) assignments of literal values: the script's settable values."""
    for node in body:
        if isinstance(node, ast.If) and "__main__" in _short(node.test):
            _top_assignments(node.body, lines, out, seen)
            continue
        if not isinstance(node, (ast.Assign, ast.AnnAssign)):
            continue
        targets = node.targets if isinstance(node, ast.Assign) else [node.target]
        if node.value is None or len(targets) != 1 or not isinstance(targets[0], ast.Name):
            continue
        value, ok = _literal(node.value)
        if not ok:
            continue
        name = targets[0].id
        src = lines[node.lineno - 1] if node.lineno <= len(lines) else ""
        note = src.split("#", 1)[1].strip() if "#" in src and not isinstance(value, str) else ""
        item = {"name": name, "value": value, "line": node.lineno, "note": note}
        if name in seen:  # reassigned: keep every value, later ones are what runs
            out[seen[name]].setdefault("also", []).append({"value": value, "line": node.lineno})
            continue
        seen[name] = len(out)
        out.append(item)


def _args(fn: ast.FunctionDef) -> list[dict]:
    a = fn.args
    pos = a.posonlyargs + a.args
    defaults = [None] * (len(pos) - len(a.defaults)) + list(a.defaults)
    out = [{"name": p.arg, "default": None if d is None else _short(d, 60)} for p, d in zip(pos, defaults)]
    if a.vararg:
        out.append({"name": "*" + a.vararg.arg, "default": None})
    for p, d in zip(a.kwonlyargs, a.kw_defaults):
        out.append({"name": p.arg, "default": None if d is None else _short(d, 60)})
    if a.kwarg:
        out.append({"name": "**" + a.kwarg.arg, "default": None})
    return [x for x in out if x["name"] != "self"]


def functions(tree) -> list[dict]:
    """Top-level functions and class methods with their arguments, docstring and a hash of their code."""
    out = []

    def add(fn, cls=None):
        doc = ast.get_docstring(fn) or ""
        out.append({"name": fn.name, "cls": cls, "line": fn.lineno, "end": getattr(fn, "end_lineno", fn.lineno),
                    "args": _args(fn), "doc": " ".join(doc.split()), "hash": code_hash(fn)})

    for node in tree.body:
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            add(node)
        elif isinstance(node, ast.ClassDef):
            for sub in node.body:
                if isinstance(sub, (ast.FunctionDef, ast.AsyncFunctionDef)):
                    add(sub, node.name)
    return out


def code_hash(fn) -> str:
    """Identity of a function's code ignoring comments, docstring, formatting and a leading `self` (ast.dump)."""
    body = fn.body[1:] if ast.get_docstring(fn) is not None else fn.body
    args = ast.dump(ast.arguments(posonlyargs=fn.args.posonlyargs, args=[a for a in fn.args.args if a.arg != "self"],
                                  vararg=fn.args.vararg, kwonlyargs=fn.args.kwonlyargs, kw_defaults=fn.args.kw_defaults,
                                  kwarg=fn.args.kwarg, defaults=fn.args.defaults))
    return hashlib.sha1((args + "".join(ast.dump(b) for b in body)).encode()).hexdigest()[:12]


def io_calls(tree) -> tuple[list, list, list, list]:
    """(inputs, outputs, displays, flika_steps): calls that read files, write files, show windows, run FLIKA processes."""
    ins, outs, shows, steps, by_line_call = [], [], [], [], {}
    for node in ast.walk(tree):
        if not isinstance(node, ast.Call):
            continue
        name, recv = _call_name(node), _receiver(node)
        entry = {"line": node.lineno, "call": _short(node)}
        by_line_call[(node.lineno, entry["call"])] = node
        if name in FLIKA_PROCESS and isinstance(node.func, ast.Name):
            steps.append({"line": node.lineno, "name": name, "args": [_short(a, 50) for a in node.args]
                          + [f"{k.arg}={_short(k.value, 40)}" for k in node.keywords]})
        if name == "open" and isinstance(node.func, ast.Name):
            mode = node.args[1] if len(node.args) > 1 else next((k.value for k in node.keywords if k.arg == "mode"), None)
            m = mode.value if isinstance(mode, ast.Constant) else "r"
            (outs if isinstance(m, str) and any(c in m for c in "wa") else ins).append(entry)
        elif name in READ_CALLS:
            ins.append(entry)
        elif name in WRITE_CALLS and recv != "sys.stdout":
            outs.append(entry)
        elif name in DISPLAY_CALLS and (name != "plot" or recv in ("plt", "ax", "pg")):
            shows.append({**entry, "what": DISPLAY_CALLS[name]})
    assigns = sorted((n.lineno, n.targets[0].id, n.value) for n in ast.walk(tree) if isinstance(n, ast.Assign)
                     and len(n.targets) == 1 and isinstance(n.targets[0], ast.Name))
    for e in ins + outs:  # say what a file-name variable was set to, e.g. saveName = ... + '_velocity.csv'
        call = by_line_call.get((e["line"], e["call"]))
        arg = call.args[0] if call is not None and call.args else None
        if isinstance(arg, ast.Name):
            prior = [(ln, v) for ln, nm, v in assigns if nm == arg.id and ln <= e["line"]]
            if prior:
                e["via"] = f"{arg.id} = {_short(prior[-1][1], 120)}"
    key = lambda e: e["line"]  # noqa: E731
    return sorted(ins, key=key), sorted(outs, key=key), sorted(shows, key=key)[:12], sorted(steps, key=key)


def imports(tree) -> list[str]:
    mods = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            mods += [a.name for a in node.names]
        elif isinstance(node, ast.ImportFrom) and node.module and node.level == 0:
            mods.append(node.module)
    seen, out = set(), []
    for m in mods:
        if m not in seen and m != "__future__":
            seen.add(m)
            out.append(m)
    return out


def needs(mods: list[str], used: set) -> list[str]:
    roots = {m.split(".")[0] for m in mods} | set(mods)
    return [label for test, label in NEEDS if test(roots, used)]


MAGIC = re.compile(r"^\s*[%!]")


def parse_python(text: str) -> dict:
    """Describe a Python (or FLIKA-macro) script. A file that does not parse still gets its comments."""
    lines = text.split("\n")
    magics = [{"line": i + 1, "text": l.strip()} for i, l in enumerate(lines) if MAGIC.match(l)]
    # IPython magics (%gui qt) are fine in the FLIKA / Spyder console; blank them so the rest can be parsed.
    code = "\n".join("" if MAGIC.match(l) else l for l in lines)
    info = {"purpose": [], "meta": {}, "functions": [], "params": [], "inputs": [], "outputs": [], "displays": [],
            "flika_steps": [], "imports": [], "needs": [], "parses": True, "magics": magics}
    info["comments"] = comments(code)
    try:
        tree = ast.parse(code)
    except SyntaxError as e:
        info["parses"] = False
        info["parse_error"] = f"line {e.lineno}: {e.msg}"
        info["purpose"] = leading_comments(info["comments"], _first_code_line(lines))
        return info
    for node in tree.body[:6]:  # module docstring, and a second one some files carry
        if _is_doc_node(node):
            paras, meta = _clean_doc(node.value.value)
            info["purpose"] += paras
            info["meta"].update(meta)
    first = next((n.lineno for n in tree.body if not _is_doc_node(n)), len(lines) + 1)
    info["purpose"] += leading_comments(info["comments"], first)
    info["functions"] = functions(tree)
    _top_assignments(tree.body, lines, info["params"], {})
    info["inputs"], info["outputs"], info["displays"], info["flika_steps"] = io_calls(tree)
    for st in info["flika_steps"]:
        src = lines[st["line"] - 1]
        if "#" in src:
            st["note"] = src.split("#", 1)[1].strip()
    info["imports"] = imports(tree)
    info["needs"] = needs(info["imports"], flika_names_used(tree))
    return info


def _first_code_line(lines: list[str]) -> int:
    """First line that is neither blank, a comment nor part of a leading docstring (for files that do not parse)."""
    in_doc = None
    for i, l in enumerate(lines):
        s = l.strip()
        if in_doc:
            if in_doc in s:
                in_doc = None
            continue
        if not s or s.startswith("#"):
            continue
        q = s[:3]
        if q in ('"""', "'''"):
            if s.count(q) == 1:
                in_doc = q
            continue
        return i + 1
    return len(lines) + 1


def flika_names_used(tree) -> set:
    """FLIKA globals the script relies on: `g.*`, `start_flika`, and FLIKA process names called without being
    defined, assigned or imported under another meaning in the file."""
    defined = set()
    for n in ast.walk(tree):
        if isinstance(n, (ast.FunctionDef, ast.ClassDef)):
            defined.add(n.name)
        elif isinstance(n, ast.Name) and isinstance(n.ctx, ast.Store):
            defined.add(n.id)
        elif isinstance(n, ast.ImportFrom) and n.module and not n.module.startswith("flika"):
            defined |= {a.asname or a.name for a in n.names}
    called = {n.func.id for n in ast.walk(tree) if isinstance(n, ast.Call) and isinstance(n.func, ast.Name)}
    g_used = any(isinstance(n, ast.Attribute) and isinstance(n.value, ast.Name) and n.value.id == "g"
                 and n.attr in ("m", "win", "currentWindow", "windows", "settings") for n in ast.walk(tree))
    return ((called - defined) & (FLIKA_PROCESS | {"Window", "start_flika"})) | ({"g"} if g_used else set())


def _is_doc_node(n) -> bool:
    return isinstance(n, ast.Expr) and isinstance(n.value, ast.Constant) and isinstance(n.value.value, str)


def leading_comments(cmts: list[dict], first_code: int) -> list[str]:
    """Prose comments above the first line of code (the file header), joined into paragraphs at gaps."""
    paras, cur, last = [], [], None
    for c in cmts:
        if c["line"] >= first_code:
            break
        if last is not None and c["line"] > last + 1 and cur:
            paras.append(" ".join(cur))
            cur = []
        cur.append(c["text"])
        last = c["line"]
    if cur:
        paras.append(" ".join(cur))
    return paras


def parse_imagej(text: str) -> dict:
    """ImageJ macro (.ijm): comments, top-level assignments and run(...) commands."""
    cm = [{"line": i + 1, "text": l.strip()[2:].strip()} for i, l in enumerate(text.split("\n"))
          if l.strip().startswith("//") and l.strip()[2:].strip()]
    params = []
    for i, l in enumerate(text.split("\n")):
        m = re.match(r"\s*(\w+)\s*=\s*(.{0,200})", l)
        if m and not l.strip().startswith("//"):
            v = m.group(2).rstrip(";")
            params.append({"name": m.group(1), "value": v if len(v) < 160 else v[:157] + "...", "line": i + 1, "note": ""})
    steps = [{"line": i + 1, "name": "run", "args": [m.group(1)[:80]]}
             for i, l in enumerate(text.split("\n")) for m in [re.search(r'run\("([^"]+)"', l)] if m]
    return {"purpose": leading_comments(cm, 10**9)[:3], "meta": {}, "functions": [], "params": params[:30],
            "inputs": [], "outputs": [], "displays": [], "flika_steps": [], "imagej_steps": steps[:40], "imports": [],
            "magics": [], "needs": ["ImageJ / Fiji with the ThunderSTORM plugin" if "ThunderSTORM" in text or "Camera setup" in text
                      else "ImageJ / Fiji"], "comments": cm, "parses": True}
