# bugarach — durable session rules

**Session start:** read [`docs/FOUNDATIONS.md`](docs/FOUNDATIONS.md) (canonical
truth — it wins over conversation) and use [`docs/GLOSSARY.md`](docs/GLOSSARY.md)'s
vocabulary (stream axis vs detector axis; "modality" is banned).

## Sapper (mechanized rules)

`tools/sapper.py` converts incidents into checks that fire by themselves —
`--selftest` proves every rule can fire, `--all` scans the tree, `--staged`
gates commits (enable: `git config core.hooksPath .githooks`). pytest/CI run
both via `tests/test_sapper.py`. Prefer adding a sapper rule over adding
prose; file new-rule requests and disputes in `docs/sapper_feedback/`.

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

## Plot conventions (viewer, exports, figures)

- **Minutes-friendly time axes, always**: 60-base ticks (1/2/5/10/15/30 x
  60^k s) labeled `45s` / `2m` / `2m30s`, never raw seconds. Implemented as
  `_time_axis_hook` in `src/bugarach/ui/app.py` — reuse it.
- **Compact labeling**: no titles above plots; identity + counts live in
  y-axis labels ("fast · 30 ROI", "rate (27)"); one x-axis per linked group
  (bottom row only, with extra height so plot areas match).
- **Unlinked y, linked x**: signal rows carry a unique value dimension per
  detector so y-ranges never link across rows; x links through the shared
  `t` dimension.
- **Scroll wins**: wheel-zoom stays in the toolbar but inactive — the mouse
  wheel scrolls the page; drag pans.

## Repo management — stop-on-a-dime, any machine, any OS

The state on `origin` must always be enough to resume elsewhere (FOUNDATIONS
§8). Operational rules:

- **Push important steps promptly.** A completed, verified step (port lands,
  bug fixed, doc revised) is committed and pushed in the same breath — never
  batched for later. `main` stays green (CI is the gate).
- **Stopping mid-task**: push a WIP branch (`wip/<slug>`) AND write
  `HANDOFF.md` at the repo root — what's in flight, exact next step, how to
  verify — then push that too. Delete `HANDOFF.md` when the task completes.
  No handoff file on `main` == nothing is in flight.
- **Machine-local inventory** (everything else lives in the repo): the
  `.venv` (rebuild: `python3 -m venv .venv && pip install -e ".[dev]"`),
  `BUGARACH_DATA_ROOT` (real stores; optional — everything but the
  real-slice smoke tests runs without it), MATLAB + interface2 checkout
  (ONLY needed to regenerate parity references; running/validating the
  ports needs neither), Playwright chromium (screenshots only).
- **Cross-OS**: code uses pathlib and env vars — keep it that way (sapper
  SAP004 blocks personal absolute paths). MATLAB launch for reference
  regeneration is version-pinned R2025b, full path, never bare `matlab`:
  - Mac: `/Applications/MATLAB_R2025b.app/bin/matlab -batch "..."`
  - WSL: `/mnt/c/Program Files/MATLAB/R2025b/bin/matlab.exe -batch "..."`
    (launch path only — script bodies use Windows `C:\...` paths, per
    interface2's SAP003 lesson).

## Portfolio posture

The repo is a resume artifact as much as a tool (FOUNDATIONS §8): commit
messages tell the story a reviewer will read; README screenshot and CI badge
stay current; process docs (clean-room, sapper, parity methodology) are
presentation surface. Before landing work, ask: does this read well to a
stranger deciding whether to hire its author?

## Git conduct

- Commit and push verified work without asking (Tony juggles projects and
  wants finished work landed) — with ONE exception: **never rewrite git
  history** (filter-repo, rebase of pushed commits, force-push) without
  restating what will be destroyed and getting explicit confirmation in
  words. A bare menu-choice reply is not consent (near-miss 2026-08-11).

## Housekeeping

Prefer durable notes in this repo (this file, `docs/`) over agent memory —
Tony's explicit preference (2026-08-11): memory doesn't last and gets crowded.
