# bugarach — durable session rules

**Session start:** read [`docs/FOUNDATIONS.md`](docs/FOUNDATIONS.md) (canonical
truth — it wins over conversation) and use [`docs/GLOSSARY.md`](docs/GLOSSARY.md)'s
vocabulary (stream axis vs detector axis; "modality" is banned).

**This is not optional and skipping it has cost real work.** A session on
2026-08-13 went the whole way without reading it, and proposed calibrating the
detectors so that TTX slices stop showing coordination — the dominant-paradigm
assumption that TTX silences the field, which this project's own data refutes
and which §9 forbids in terms. The error was not a wrong number; it was
reasoning from textbook priors where the lab has a finding. When this repo's
FOUNDATIONS is silent on a question about the *preparation* (not the code), the
authority is `syncytium2/foundations` FOUNDATIONS §15 — check it before building
anything on an assumption about what a condition does.

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

## Show the picture — don't describe it

**If a finding is visual, render it before writing about it.** Rasters,
detector traces, distributions, sweeps, before/after comparisons: produce the
figure, show it, and let the prose point at what to look at. Flagging something
for Tony's attention and then explaining it in paragraphs is the failure mode
he has called out (2026-08-13) — the text arrives, the evidence doesn't.

This repo can already draw. `tools/make_diagnostic.py` renders detector lanes,
the ROI raster and per-detector analysis traces to PNG through Playwright
chromium; `bugarach.ui.diagnostic` is the figure itself. Reuse them rather than
describing what a figure would have shown.

Applies to the mid-task update as much as the final answer: "SCE tops out at
F1 0.57 and here is the trace showing why" beats three paragraphs of mechanism.

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
- **Nothing is ever drawn on the raster** (Tony, 2026-08-26 — *"please, lets never
  draw on the raster. i know i've changed my mind on this"*). The raster is **black
  and white**: one ink, one mark per event, nothing competing with it. Every
  detection, planted event, treatment window, anchor or other cue goes in a **lane
  above** it — symbols, or hashes where the cue needs rows — x-linked through the
  shared `t` dimension. **A directional marker in that lane points *down*, at the
  raster it describes** (Tony, 2026-08-26): the lane sits above its own raster, so
  an up triangle walks the reader's eye to the panel above, which belongs to the
  previous recording. Identity and counts go in the panel's y-axis label or a
  text header outside the plot, **never as text laid over the marks**.
  `bugarach.ui.diagnostic.raster_panel` already refuses detection spans in its own
  docstring and `lane_panel` is what stacks above it; the way to break the rule is
  to overlay from *outside* the module, which is exactly how
  `make_benchmark_figures.py` broke it on the day the rule was written. **Sapper
  SAP009 fires on it**, and it works by naming — hold a raster in a variable
  called `raster` so the check can see it.
  Two consequences of that down-pointing rule, learned the same day. **Shape is
  spoken for**: it already means "look below", so it cannot also encode what a
  mark *is* — recovered and missed are both ▼, green and red, and the verdict is
  the colour. And it holds **above a trace** as well as above a raster, for the
  same reason: a mark riding over data is an annotation on that data.
  Not mechanized, and the reason is filed rather than skipped —
  [`docs/sapper_feedback/2026-08-26-down-triangles-cannot-be-a-line-match.md`](docs/sapper_feedback/2026-08-26-down-triangles-cannot-be-a-line-match.md).

## Repo management — stop-on-a-dime, any machine, any OS

The state on `origin` must always be enough to resume elsewhere (FOUNDATIONS
§8). Operational rules:

- **Push important steps promptly.** A completed, verified step is committed and
  pushed in the same breath — never batched. Nothing below is a reason to sit on
  unpushed work.
- **Branch; land on `main` via a green PR** — full rules, and which of them fire
  by themselves, in [`docs/git_workflow.md`](docs/git_workflow.md). The two that
  are mechanized need no memory: `.githooks/pre-commit` refuses a commit on
  `main`, and `tools/merge_when_green.sh <pr>` refuses to merge a PR whose checks
  have not passed (including when there are none). Enable the hook once per
  clone: `git config core.hooksPath .githooks`.
- **Stopping mid-task**: push a `wip/<slug>` branch AND a root `HANDOFF.md`, then
  push that too. **No handoff file on `main` == nothing in flight**, so the root is
  a signal and it has to stay honest. When the work lands, the file leaves the
  root — **delete it if it is spent, move it to
  [`docs/handoffs/`](docs/handoffs/README.md) if anything in it is still worth
  reading.** That third option was missing until 2026-08-24, and its absence cost
  four days of a false positive: `HANDOFF-difficulty-axis-and-synfire.md` sat at
  the root saying *"nothing is half-done"* in its own second paragraph, because
  the only alternative on offer was deleting content that three open items still
  depend on.
- **The export folder is the input. The store is closed.** (Tony, 2026-08-20.)
  Analysis reads an **export folder** — `docs/export_folder_spec.md` — and nothing
  else: no `.mat` store, no lab workbook, no roster, no companion database. **Do not
  add an exclusion or dead-ROI filter to anything here.** Which recordings are
  analysable and which ROIs are alive are the producer's calls, already applied; a
  withdrawn recording is simply absent from the folder.
  The rule was there from revision 1 and got read as a convenience. Going around it
  cost a real error: an analysis read the store, noticed it held recordings the lab
  had withdrawn, re-derived the exclusions from the lab's workbook — which keys them
  on (date, mouse, `slice_order`) — matched on date because bugarach has no
  `slice_order`, and **dropped a recording the lab had not withdrawn**, while the
  producer's own export had it right. Contract revision 6 records it.
  If a folder looks like it contains something it should not, that is a
  **conversation with the producer**, not a filter in the consumer.
- **Machine-local inventory** (everything else lives in the repo): the
  `.venv` (rebuild: `python3 -m venv .venv && pip install -e ".[dev]"`),
  the export folders under `<data>/exports/bugarach/`, MATLAB + interface2
  checkout, Playwright chromium (screenshots only). `BUGARACH_DATA_ROOT` still
  resolves the older `.mat` stores and a few legacy tools still read them
  (`bench.py`, `fit_background_shape.py`, the parity fixtures) — that is
  migration debt, not licence.
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
  `bugarach.paths.darkroom()` — it takes `$BUGARACH_DARKROOM` when set and
  otherwise finds the mount itself, and the briefing prints what it resolved.
  Rule and the incident behind it: FOUNDATIONS §5. Never hardcode the path: it
  carries a person's name and this repo is public (sapper SAP004).
  **A report counts as output, and "in the repo" is not delivered.** The assembly
  report reached `docs/learned/` and stopped there, because its builder took
  `--out` as required while every figure tool defaults to the darkroom — so the
  one artifact written for a person to read was the only one that could not find
  its way to them, and Tony had to ask where it was (2026-08-18). A tool that
  renders something to be read defaults its destination to `darkroom()` and takes
  `--also` for the repo copy; sapper SAP006 blocks the required form in page and
  report builders. Keep both copies: the repo one is what review and git history
  need, the darkroom one is what a person opens.
  Two paths, one directory: `~/Dropbox-<org>` is a **symlink** to
  `~/Library/CloudStorage/Dropbox-<org>`. Seeing a tool print one while looking in
  the other does not mean the file went somewhere else — check with `ls -ld`
  before concluding anything is missing.
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
The `SessionStart` hook prints the briefing automatically — if it ever stops
firing, that is a bug worth fixing, not an inconvenience to route around. It is
wired to `tools/session_start_trimmed.sh`, which runs the vendored
`.claude/hooks/session-start.sh` unchanged and replaces its whole-board dump with
`tools/board_digest.sh` — the **ACTIVE blocks only**. The vendored hook `cat`s the
board, which on 2026-08-20 made the briefing 60,235 bytes; the harness refused an
injection that size, spilled it to a file and delivered a 2KB preview, so the board
(line 32) reached nobody and took the worktree list and the unpushed-work alarm
with it. Both hooks print a size canary — `briefing delivered: N lines, NB` — as
their **first** line, because a spill keeps the opening ~2KB and drops the rest, so
a canary anywhere else reports only when nothing is wrong.

**Don't take the budgets on trust, and don't watch the number by hand.** They were
guessed from two remembered incidents, and the guess was three kilobytes loose.
`tools/hook_spill_census.sh` reads the record instead: every payload the harness has
ever refused is still on disk, because refusing it is what wrote it there. On this
machine that record says the threshold sits in **(8,768B, 10,186B]** across 55
refusals. Run it before changing either budget — and note that a budget can be wrong
in *both* directions: too high and the channel goes silent, too low and FOUNDATIONS
§9 degrades to its claims on every run while the hook reports success.

**There are two boards and they answer different questions.** `docs/SESSIONS.md`
is in git and covers what another *machine* can see — the darkroom, the public
site, a remote store. The machine-local `../bugarach-worktrees/SESSIONS.md`
covers what this *machine* shares: which session holds the primary checkout, a
MATLAB process, the venv, a port. **Claiming on the local board is a
precondition for working, not a courtesy**, and it is mechanized both ways: the
briefing creates the board if it is missing, and `tools/guard_local_board.sh`
refuses a commit from a worktree that has no block on it (override, one-shot:
`ALLOW_UNCLAIMED_BOARD=1`). Prose did not hold — a session on 2026-08-18 read
"(no board yet — create it)" at startup, worked all day across two worktrees and
wrote to the shared darkroom without ever creating it, while four other sessions
ran on the same machine. This is a bugarach-local addition; the vendored
protocol does not require it, which is why the gate lives here and not upstream.

**Claim as the first act of the session, not at your first commit, and give the
block a `Touches:` line.** The gate fires at the commit, which is hours after the
work exists: on 2026-08-20 three sessions each did good work twice — two tool
conversions, a spec revision, a CI change — and every one of them had claimed
correctly, just afterwards. No two shared a branch name and all three overlapped in
**paths**, which is what `Touches:` is for and why the digest puts it in front of
you at startup. Whether the machine should insist at the first *file write* rather
than the first commit is an open decision in
[`docs/todo/2026-08-20-claim-before-starting-not-before-committing.md`](docs/todo/2026-08-20-claim-before-starting-not-before-committing.md).

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
doc, so a new role propagates for free — 11 roles as of f43a07b).

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

Name things; don't index them. Shas and dates are lookup keys, not content.
Prefer the consequence to the label. Full version, with the examples that
prompted it: [`docs/writing_conventions.md`](docs/writing_conventions.md).

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
