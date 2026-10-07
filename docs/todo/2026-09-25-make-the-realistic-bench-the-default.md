---
status: done
filed: 2026-09-25
closed: 2026-10-07
---

> **Done 2026-10-07** (Tony: *"switch now"*), after the full-panel report had landed without it.
> `bench.DEFAULT_SPACING = "realistic"` is the one place it is decided; `spacing()`,
> `spacing_from_args()` and the two tools whose `--spacing` defaulted to `bench`
> (`probe_bench_floor.py`, `score_bench_candidates.py`) read it. The old bench is `--spacing
> bench`. Tests that pin it name it through the `pre_adr_0010_bench` fixtures in
> `tests/conftest.py`, not by re-baselining. ⚠ The realistic gaps were measured with events under
> 2 s apart merged first, so the closest real events, combined's among them, are not planted;
> re-measuring waits on the producer's new export.

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
