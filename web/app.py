"""FastAPI web app for the FLIKA scripts catalogue: serves the front end in static/ and the JSON API under /api.

Run with `python run_web.py` (http://127.0.0.1:8126, local only). `scripts/build_static.py` exports every path in
STATIC_ENDPOINTS to JSON for the GitHub Pages site, so keep that list in step with the GET routes below.
Everything the API returns is read from the repository's own files (catalogue.py); nothing runs the scripts.
"""
from pathlib import Path

from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from .catalogue import catalogue, index_entry, stats
from .demos import demo_list, training

STATIC = Path(__file__).resolve().parent / "static"
TITLE = "FLIKA Scripts"

app = FastAPI(title=TITLE)
app.mount("/static", StaticFiles(directory=STATIC), name="static")


@app.get("/", include_in_schema=False)
def index():
    return FileResponse(STATIC / "index.html")


@app.get("/api/info")
def info():
    """Counts for the home page: scripts, lines, topics, where they run, demos."""
    cat = catalogue()
    counts = {}
    for e in cat["scripts"].values():
        counts[e["topic"]] = counts.get(e["topic"], 0) + 1
    return {"title": TITLE, "repo": "flika_scripts", "stats": stats(cat),
            "topics": [t | {"count": counts.get(t["id"], 0)} for t in cat["topics"]], "demos": demo_list()}


@app.get("/api/catalogue")
def catalogue_index():
    """Every script's searchable summary, in topic order."""
    cat = catalogue()
    return {"topics": cat["topics"], "scripts": [index_entry(cat["scripts"][i]) for i in cat["order"]]}


@app.get("/api/script/{sid}")
def script(sid: str):
    """One script: description, functions, values, files, FLIKA steps and full source."""
    cat = catalogue()
    if sid not in cat["scripts"]:
        raise HTTPException(404, f"no script {sid!r}")
    e = dict(cat["scripts"][sid])
    names = {i: cat["scripts"][i]["path"] for i in cat["scripts"]}
    e["functions"] = [f | {"same_in": [{"id": i, "path": names[i]} for i in f["same_in"]]} for f in e["functions"]]
    pos = cat["order"].index(sid)
    e["prev"] = cat["order"][pos - 1] if pos else None
    e["next"] = cat["order"][pos + 1] if pos + 1 < len(cat["order"]) else None
    e["topic_title"] = next(t["title"] for t in cat["topics"] if t["id"] == e["topic"])
    return e


@app.get("/api/demos")
def demos():
    return demo_list()


@app.get("/api/training")
def training_data():
    """The SVM training-feature table committed in the repo."""
    return training()


# GET paths (without the /api prefix) written to the static site as api/<path>.json.
STATIC_ENDPOINTS = ["/info", "/catalogue", "/demos", "/training"] + [f"/script/{i}" for i in catalogue()["order"]]
