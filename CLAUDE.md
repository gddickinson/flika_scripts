# flika_scripts

Scripts run inside FLIKA (or beside it), plus a web catalogue of them in `web/`.

@INTERFACE.md

- The scripts run at module level and cannot be imported; load a function with `web/script_loader.load_functions`.
- Web tests: `python -m pytest -q tests` (needs requirements-web.txt). Local app: `python run_web.py` (port 8126).
- After changing a demo function or its JS port: `python scripts/make_demo_fixture.py`, then the node tests.
