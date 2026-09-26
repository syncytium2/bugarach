---
status: open
filed: 2026-09-25
---

# Make the realistic bench the default, in the PR that brings the full-panel report to main

**What:** ADR-0010's ruling 2 says the realistic bench replaces the old one. Tonight's full-panel
run uses it by name, but every run that does not name a bench still gets the old ≥120 s one: #823
and the night's bench PR were built off by default, so merging them changed nothing.

**Do, in the PR that brings the 2026-09-26 full-panel morning report to `main`** (Tony, 2026-09-25):
- The realistic bench becomes the default for every search, training and scoring tool.
- The old bench stays available **by name**, so past results can be reproduced.
- Tests that pin the old bench's recordings name it explicitly, rather than being re-baselined.
- The goal page and `docs/INDEX.md` say which bench is the default and since when.

**Not before the report:** switching the default mid-night would change what a half-finished run
reads.
