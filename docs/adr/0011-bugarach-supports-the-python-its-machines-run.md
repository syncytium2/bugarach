# ADR-0011: bugarach supports the Python its machines run, and no older one

## Status

Accepted, 2026-09-25, by Tony. Asked why CI tests three versions of Python, he answered *"i don't
recall promising back compatibility"*, gave the Mac's version, and approved the change.

## Context

**CI tested Python 3.11, 3.13 and 3.14 on every push, defending a promise nobody had made.**
`pyproject.toml` declared `requires-python = ">=3.11"`, and the README's install section said
"Requires Python ≥ 3.11". A stranger reads those two lines as a commitment. No ADR, handoff or
commit records anyone deciding it; it came with the project's setup.

**Both machines that produce results run 3.14:** the Windows GPU workstation (3.14, per
`docs/windows_workstation_setup.md`) and the Mac (3.14.5).

**What the two older legs cost and caught.** Each leg takes about 7 minutes, run in parallel. The
3.11 leg caught real breakage: f-strings using syntax that only 3.12 and later accept (PEP 701),
which is why `tests/test_syntax_floor.py` exists. That breakage matters only to someone running
3.11. The legs also exposed tests that depended on timing or scheduling, and a test that pinned
floating-point results across platforms (#824). Those were fragile tests, not version
incompatibilities, and they are fixed in the tests themselves.

## Decision

1. **The supported Python is 3.14 and later.** `requires-python = ">=3.14"`, and the README says so.
   Installing on an older Python now fails at `pip install` with a clear message, instead of
   appearing to work.
2. **CI tests 3.14 only.** The matrix is `["3.14"]`, and the site-staleness check runs on 3.14.
3. **When the machines move to a newer Python, the floor follows** in the same change, with this
   record's reasoning. A leg for a Python the machines do not run is added only if someone decides
   to support it.
4. **`tests/test_syntax_floor.py` stays.** It reads the floor from `pyproject.toml`, so it now
   checks that every file parses on 3.14. Its PEP 701 scan applies only to a floor below 3.12.

## Consequences

- **Branch protection must change with it.** `main` requires the checks by name. After this lands,
  Tony removes `test (3.11)` and `test (3.13)` from the required checks (Settings → Branches), or
  every PR waits for checks that never run. The change lands when no other PR is waiting to merge.
- **Syntax and standard-library features from 3.12–3.14 are now allowed** in the tree.
- **Anyone on an older Python** (a colleague installing the viewer) must install 3.14.
  `uv python install 3.14` is the quickest route, as in the workstation setup.
- **The historical notes stay as written.** CI comments, the CLAUDE.md CI section and past handoffs
  mention the 3.11 leg as the record of what it caught.
