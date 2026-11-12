"""Web catalogue for flika_scripts (FastAPI app + static front end; see INTERFACE.md).

app.py            routes under /api and STATIC_ENDPOINTS for the static export
catalogue.py      finds scripts, folds Finder duplicates, links shared functions and demos
parse_script.py   reads one script: docstrings, comments, functions, values, files, FLIKA steps
topics.py         the curated topic groups
demos.py          the interactive demos (which functions each JS engine ports) and the training table
script_loader.py  loads named functions from a script file without running it (tests, fixtures)
flika_names.py    FLIKA process function names
static/           the front end (ES modules, no build step)
"""
