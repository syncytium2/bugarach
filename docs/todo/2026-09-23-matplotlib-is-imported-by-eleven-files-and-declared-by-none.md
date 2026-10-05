---
status: open
opened: 2026-09-23
area: packaging
---

# matplotlib is imported by eleven files and declared in no dependency group

`pyproject.toml` lists `numpy`, `scipy` and `h5py` as runtime dependencies, and optional groups
for `ui`, `docs`, `dl`, `surrogates` and `dev`. **matplotlib appears in none of them.** Eleven
files import it:

```
tools/make_line_sensors_figure.py          tools/make_tube_aggregate_figure.py
tools/make_rigid_shift_controls_figure.py  tools/make_tube_real_summary_figure.py
tools/make_rigid_shift_gates_figure.py     tools/make_tube_ssl_figure.py
tools/make_rigid_shift_look_figure.py      tools/make_twin_check_figure.py
tools/make_slow_comodulation_figure.py     tools/measure_recording_identity.py
tools/make_surrogate_schematic_figure.py
```

Every one of them fails at import on a clean environment built from `pyproject.toml`.

## How it stayed invisible

No test imports matplotlib, so the suite is green with it absent and **CI cannot see this**.
The failure only appears when a person tries to render a figure, which is exactly the moment
the repo is meant to be able to "stop on a dime, any machine" (FOUNDATIONS §8).

Found on 2026-09-23 while rendering the co-modulation figures on WSMIP064: the venv had no
matplotlib and no pip (it is `uv`-managed), so the fix was
`VIRTUAL_ENV=<venv> uv pip install matplotlib` — an undeclared, unpinned, machine-local
install. Nothing records that it happened, and the next clone hits the same wall.

## What to decide

1. **Which group.** `dev` is the minimum. A separate `figures` group is arguably more honest —
   figure rendering is not development — but it adds a group a newcomer has to know to install,
   and every figure tool is in `tools/`, which is already a developer surface. Recommend `dev`,
   plus `figures` only if someone wants the tools without the test stack.
2. **Whether to pin.** The other groups pin only where a defect made it necessary
   (`elephant==1.2.1`). A floor like `matplotlib>=3.8` matches `numpy`/`scipy` and is probably
   right; nothing here depends on a version-specific behaviour that has been found.
3. **Whether a test should catch the next one.** A test that imports every module under
   `tools/` would have caught this at the commit. It would also be slow and would pull the whole
   optional stack into the default suite, so it likely belongs behind a marker if it is written
   at all. Worth weighing against a sapper rule that flags an import of a module named in no
   dependency group — cheaper, and the kind of line-level check sapper is for.

## Not urgent, but not cosmetic

Every figure in `docs/learned/` was produced by one of these tools. A reviewer who clones this
repo to check a figure cannot regenerate it, and the error they get says `No module named
'matplotlib'` rather than anything about the project's packaging.
