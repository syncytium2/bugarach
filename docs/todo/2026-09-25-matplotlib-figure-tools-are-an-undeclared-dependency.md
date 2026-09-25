---
status: open
opened: 2026-09-25
area: packaging; figure tools
waits_on: nobody
---

# The matplotlib figure tools rely on a dependency nothing declares

Several `tools/make_*_figure.py` tools import matplotlib. So do the two figures added for the
final-parameters night's morning report, `make_elevated_rate_figure.py` (Figure 3) and
`make_bench_floor_figure.py` (Figure 4). No extra in `pyproject.toml` lists matplotlib, and CI does
not install it.

The tools work on a machine that happens to have matplotlib installed. On WSMIP065 on 2026-09-25,
the repo's `.venv` did not have it: the figures were rendered with matplotlib installed into a
scratch folder (`pip install --target <scratch> --no-deps matplotlib ...`) and put on
`PYTHONPATH`, so the shared venv was left untouched.

Their tests skip where matplotlib is absent (`pytest.importorskip`), so in CI they currently skip.

**To do:** add matplotlib to an extra, for example `figures`, and to `dev`. Install that extra in
CI so the figure tests run. The bokeh route that `tools/make_diagnostic.py` uses is declared under
`ui`, so it is not affected.
