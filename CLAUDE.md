# bugarach — durable session rules

**Session start:** read [`docs/FOUNDATIONS.md`](docs/FOUNDATIONS.md) (canonical
truth — it wins over conversation) and use [`docs/GLOSSARY.md`](docs/GLOSSARY.md)'s
vocabulary (stream axis vs detector axis; "modality" is banned).

## Todos

Open work items live in `docs/todo/` (one file per item, frontmatter
status). Check it when Tony asks "what's next" or has spare cycles.

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
  batched for later. This is the rule that matters most; nothing below may be
  used as a reason to sit on unpushed work.
- **Work on a branch; land on `main` through a green PR.** Never commit to
  `main` directly. Branch, push the branch immediately (`git push -u origin
  <slug>`), open a PR, merge when CI passes — `gh pr merge --merge --auto`.
  Use `--merge`, **not** `--squash`: commit messages here are the story a
  reviewer reads (Portfolio posture, below), and squashing flattens them.
- **One PR per theme, not per commit.** A PR is a unit of review, not a unit of
  work. Several related commits — a vendored tool plus its wiring plus its
  docs — belong in one. Six PRs for one afternoon of related doc edits is
  fragmentation, not rigour.
- **Merge with `bash tools/merge_when_green.sh <pr>`, not `gh pr merge --auto`.**
  `--auto` only waits for *required* checks; with no branch protection nothing is
  required, so it merges instantly and the PR gates nothing. The script does the
  waiting and verifying itself, and **fails closed when no checks are found** —
  an absent gate is indistinguishable from a passed one, so absence is treated as
  failure. It self-tests, and `tests/test_merge_gate.py` runs that in CI.
  It is weaker than branch protection (it only governs merges that go through
  it), so `docs/todo/2026-08-12-enable-branch-protection-on-main.md` stays open —
  but nothing is waiting on that todo to be safe today.
  *This was live for a whole session:* every PR merged ~90 seconds before its
  own CI finished. They all happened to pass, so it looked fine. The tell is
  `gh pr view N --json autoMergeRequest` returning `null` — if auto-merge were
  armed it would name a merge method. **Check that, don't read past it.**
  It is the skipped-gate trap from [`docs/simulation_plan.md`](docs/simulation_plan.md),
  committed in the same session that documented it: a gate written as a
  sentence, shipped without the mechanism.
  *Why this replaced "commit straight to main" (reconciled 2026-08-12):* CI
  triggers on `push: [main]` and `pull_request`, so a direct push to `main`
  runs CI **after** `main` already has the commit. "`main` stays green (CI is
  the gate)" was therefore unachievable by the flow that sentence sat next to —
  CI could only report the breakage, not prevent it. A PR makes the same
  sentence true. It also makes one-session-one-branch real, so two sessions
  cannot collide on `main` (`docs/session_protocol.md`).
  The push-promptly rule is unaffected: the branch is pushed on creation, so
  work is durable on `origin` long before the PR merges.
- **Stopping mid-task**: push a WIP branch (`wip/<slug>`) AND write
  `HANDOFF.md` at the repo root — what's in flight, exact next step, how to
  verify — then push that too. Delete `HANDOFF.md` when the task completes.
  No handoff file on `main` == nothing is in flight.
- **Machine-local inventory** (everything else lives in the repo): the
  `.venv` (rebuild: `python3 -m venv .venv && pip install -e ".[dev]"`),
  `BUGARACH_DATA_ROOT` (real stores; optional — everything but the
  real-slice smoke tests runs without it), MATLAB + interface2 checkout,
  Playwright chromium (screenshots only).
- **What the interface2 checkout actually holds** (this line used to say
  "ONLY needed to regenerate parity references" — that was wrong, and a
  session acting on it concluded bugarach had no simulator and proposed
  building one from scratch): besides the MATLAB originals, it carries the
  **coordinated-event simulation, scoring and calibration suite** that
  produced the detector operating points — `generate_synth_coord.m`,
  `generate_coord_benchmark.m`, `score_coord_detection.m`,
  `optimize_detectors.m`, `calibrate6.m`. Running/validating the ports still
  needs neither MATLAB nor the checkout. See
  [`docs/todo/2026-08-12-port-coordination-benchmark.md`](docs/todo/2026-08-12-port-coordination-benchmark.md).
- **Figure/report output goes to the Dropbox darkroom**, not the repo and not
  local disk. bugarach owns `<darkroom>/bugarach/` — resolve it with
  `bugarach.paths.darkroom()`, which reads `$BUGARACH_DARKROOM` and returns
  `None` (skip the export) when unset. Never hardcode it: the path carries a
  person's name and this repo is public (sapper SAP004).
  `<darkroom>/constellation/` is the **MATLAB producer** team's folder —
  detector sweeps and calibrated operating points live there; don't write into
  it. The darkroom is mounted on **every** machine, so it is a cross-machine
  shared resource: claim it on the board before writing.
- **Cross-OS**: code uses pathlib and env vars — keep it that way (sapper
  SAP004 blocks personal absolute paths). MATLAB launch for reference
  regeneration is version-pinned R2025b, full path, never bare `matlab`:
  - Mac: `/Applications/MATLAB_R2025b.app/bin/matlab -batch "..."`
  - WSL: `/mnt/c/Program Files/MATLAB/R2025b/bin/matlab.exe -batch "..."`
    (launch path only — script bodies use Windows `C:\...` paths, per
    interface2's SAP003 lesson).

## Multi-session coordination — assume you are not alone

Several stateless sessions may run against this repo at once, on this machine
and others; a session learns what another did **only** from durable artifacts.
Read [`docs/session_protocol.md`](docs/session_protocol.md) and claim shared
external outputs on [`docs/SESSIONS.md`](docs/SESSIONS.md) before writing them.
The `SessionStart` hook (`.claude/hooks/session-start.sh`) prints the briefing
automatically — if it ever stops firing, that is a bug worth fixing, not an
inconvenience to route around.

**Vendored copies** (`docs/session_protocol.md` and the hook, from interface2;
`tools/murderboard_freshness.sh`, from syncytium2/murderboard) carry a
provenance stamp on line 1. To refresh: re-copy and bump the stamp — never edit
a vendored file in place. Check staleness with
`bash tools/check_vendor_freshness.sh` (set `BUGARACH_INTERFACE2` to a local
interface2 clone first; the wrapper refuses to guess, and
[`docs/todo/2026-08-12-report-freshness-gate-clone-bug.md`](docs/todo/2026-08-12-report-freshness-gate-clone-bug.md)
explains why).

## Document deliverables — run the murderboard first (anti-slop)

When asked for a **document** deliverable — the methodology narrative, methods or
manuscript text, an explainer, a figure or its caption, a report, or a human-facing
handoff — do **not** hand over a first draft. **Invoke `/murderboard <artifact>`**
(vendored skill in `.claude/skills/murderboard/`); it gates freshness, derives the
role roster, resolves the **built** artifact rather than its generator, and emits a
checkable run record. Without the skill, follow
[`docs/doc_review_process.md`](docs/doc_review_process.md) by hand: draft, run the
review team (**every role runs** — scale *how* you run them to stakes, never
*which* ones), apply the fixes, **re-review the repaired artifact — blind pass
first**, and deliver the corrected document **plus a summary and a role ledger**
with any residual `⚠` flags. Then `bash tools/murderboard_roster.sh check <report>`
so a dropped role cannot pass as a clean one (it derives the roster from the process
doc, so a new role propagates for free — 11 roles as of b2b2ba2).

**Deliberate deviation:** murderboard's `fetch_paper.py` is **not** vendored here.
It hardcodes a personal/institutional library path, which SAP004 blocks and which
must not sit in a public repo — see
[`docs/todo/2026-08-12-vendored-lit-tool-carries-personal-paths.md`](docs/todo/2026-08-12-vendored-lit-tool-carries-personal-paths.md).
If a review needs a paper, fetch it by hand. Do not re-vendor that file without
reading it first.

**Why this repo in particular:** FOUNDATIONS §8 makes bugarach a portfolio artifact,
and the open [methodology narrative](docs/todo/2026-08-11-methodology-narrative-doc.md)
is explicitly written for outside readers — bios, grant facilities sections, hiring
reviewers. That todo already warns "verify all counts/claims against the tree at
writing time"; the murderboard is the mechanized version of that warning. A parity
claim that overstates, or a test count quoted from memory, costs more here than a bug.

## Writing for a human reader

Tony's correction, 2026-08-12: *"the numbers and dates don't mean much to a
human."* Applies to docs, commit messages, PR bodies, and replies.

- **Name things; don't index them.** If a doc defines a list of traps, stages, or
  findings, refer to them by a short descriptive name, never `T3` or `stage 4`. A
  sentence like "stage 4 is T3 again" asks the reader to hold two numbered
  taxonomies in their head and cross-reference them — it carries no meaning on
  its own. "We'd be skipping the check again because there was something more
  interesting to build" does.
- **Commit shas and dates are lookup keys, not content.** `b94062e` and
  `2026-07-23` tell a reader nothing. Say what changed and how long it sat.
  Include the sha only when someone would actually go look it up, and then in
  parentheses after the meaning.
- **Prefer the consequence to the label.** "LoCo goes from 81 events to 28 on a
  real recording" beats "the adoption had a large effect".
- Same instinct as the plot conventions above: identity in the label, no titles
  restating what the axes already say.

## Portfolio posture

The repo is a resume artifact as much as a tool (FOUNDATIONS §8): commit
messages tell the story a reviewer will read; README screenshot and CI badge
stay current; process docs (clean-room, sapper, parity methodology) are
presentation surface. Before landing work, ask: does this read well to a
stranger deciding whether to hire its author?

## Git conduct

- Commit and push verified work without asking (Tony juggles projects and
  wants finished work landed) — including opening the PR and setting it to
  auto-merge on green. "Without asking" survives the branch-and-PR flow above;
  what changed is the route to `main`, not whether you need permission.
- **Never rewrite git history** (filter-repo, rebase of pushed commits,
  force-push) without restating what will be destroyed and getting explicit
  confirmation in words. A bare menu-choice reply is not consent (near-miss
  2026-08-11). Merging a PR is not a rewrite; squash-merging your own
  feature branch is fine.

## Housekeeping

Prefer durable notes in this repo (this file, `docs/`) over agent memory —
Tony's explicit preference (2026-08-11): memory doesn't last and gets crowded.
