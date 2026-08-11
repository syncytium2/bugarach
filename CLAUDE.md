# bugarach — durable session rules

## Clean-room specs (`docs/clean_room/`)

Specs in `docs/clean_room/*_spec.md` are implemented from the spec document
ALONE — no MATLAB/Octave/SciPy source, no existing implementations of the same
algorithm. The integrator returns divergences as new vectors or a revision
header **inside the spec file**, never as reference code, so when the user
points at a spec path again, re-read the file top-to-bottom first: a revision
header means the rules changed.

Validation is adversarial and differential — an independently-spawned agent
clean-rooms its own implementation, hand-derives hostile vectors, and fuzzes
both implementations against each other. The full process is in
[`docs/clean_room/WORKFLOW.md`](docs/clean_room/WORKFLOW.md); follow it for
new specs and revisions. Per-spec harnesses (adversary impl, vectors,
derivation notes, fuzzer) live in `docs/clean_room/harness/<name>/` and are
wired into the normal suite via `tests/test_<name>.py` — keep it that way so
validation reruns with plain `pytest`.

Status: `find_peaks_halfprom` implemented against spec rev 2, accepted
2026-08-11 and integrated into `src/bugarach/detectors/peaks.py` (the tests
target that integrated copy, not a standalone file).

## Housekeeping

Prefer durable notes in this repo (this file, `docs/`) over agent memory —
Tony's explicit preference (2026-08-11): memory doesn't last and gets crowded.
