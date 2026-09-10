# Handoff — the full-cohort run is WITHDRAWN, the redesign is landed, eight questions are open

**Session ended 2026-09-09 evening.** Nothing is half-written; one thing is half-*run*, and
it must not resume until Tony has answered the questions in
[`docs/conditioned_run.md`](docs/conditioned_run.md).

> **Not murderboarded** — working material, same standing as `docs/pipeline.md`.

**No counts in this file.** Derive them: `git rev-parse --short origin/main` · `pytest -q` ·
`python3 tools/sapper.py --all` · `bash tools/murderboard_freshness.sh --refresh`.

Predecessor: [`docs/handoffs/2026-09-09-the-loop-closes.md`](docs/handoffs/2026-09-09-the-loop-closes.md).
**Its "Do not break this" section is NOT superseded** — Tony judges out of the detached
`../bugarach-worktrees/mahice` worktree, and it must not be reaped or recreated.

---

## Read this before touching anything in the darkroom

`<darkroom>/bugarach/2026-09-09-full-cohort-senktide-ttx/` holds a complete run whose
**report is withdrawn and whose numbers were produced on a generator fitted to the wrong
population.** Both `REPORT.md` and `RUN_RECORD.md` now open with the withdrawal and the
corrections; the artifacts are kept so the review has a subject and the corrections have a
before. **Do not quote any measurement out of that folder.** `for_fireflies/README.md` is a
draft marked do-not-send, and was not sent.

## What is in flight

**In flight as a pull request: [#466](https://github.com/syncytium2/bugarach/pull/466)
alone** — the field-step figure, inherited from an earlier session and still held because it
is a figure with a caption that was never murderboarded. **Everything this session opened has
landed.**

**What actually holds this root file open is not a PR.** It is a **withdrawn run** and an
**unanswered design**: the darkroom folder's measurements are void, its replacement is
landed and unanswered, and nobody should start the re-run until Tony has ruled on the eight
questions below. That state has no PR to retire it, which is why this file says so in
words — see [`docs/todo/2026-09-09-eight-questions-before-the-conditioned-run.md`](docs/todo/2026-09-09-eight-questions-before-the-conditioned-run.md).

## What landed

- **The 2026-09-03 artifact-excluded export declared** — it had sat on disk six days with no
  file in this repo naming it — plus a K floor under a percentage, a spec derivation that
  aggregates across recordings at each one's own resolved K, and group facets with
  per-detector pages on the before/after figure. Two latent defects fixed on the way: a
  hardcoded clip width that silently dropped the rightmost column of any wide page, and a
  positional tuple read across a module boundary.
- **The murderboard re-vendored to `81a0927`.** The freshness gate refused the review
  outright and was right to: upstream had added a cost section after a run on another model
  spent a two-day limit and produced no review at all. **Not adopted, deliberately:**
  upstream's `murderboard_model_gate.sh` and `TERMS.md`. Wiring that gate deserves its own
  decision rather than arriving as a side effect of a re-vendor.
- **[`docs/conditioned_run.md`](docs/conditioned_run.md)**, the redesign, plus the fix for
  the defect below.

## The defect that withdrew the run

A K given as a percentage puts each recording in the assessment **once**, at its own
resolved count. `assess_archive`'s ROI summary filtered to one K — a harmless de-duplication
under an absolute scan, a subset selector under a percentage — so it kept only the smallest
fields, and `derive_spec` read it for the simulated field size. **Three murderboard roles
found it independently**: from the spec, from the assessment contradicting its own rows, and
from the code.

Corrected, the simulated field size and participation both move materially, so every F1,
every operating point and every detection in that folder was produced on the wrong simulated
population. Both files now compute the field size from the rows themselves, and the
assessment header records the percentage and floor it was asked for — which it previously
recorded nowhere.

⚠ **The re-run was started and is incomplete, and its outputs live only in this session's
scratchpad.** Scratch is not durable: **treat the re-run as not started** and redo it from
the command sequence in the withdrawn `RUN_RECORD.md`, against the answers to the questions
below.

## Why a session must stop here rather than guess

`docs/conditioned_run.md` ends with **eight questions that have no safe default** — balance
by weighting or subsampling; the producer's windows or windows recomputed to Tony's 15–20 /
+2 min definition; the two recordings under the 15-minute floor; how finely to stratify when
a cell holds five recordings; one operating point or several; whether the slow stream gets an
assessment and a bench; whether K is one percentage across both streams; and whether MAHICE
comes before or after. Four further items are listed as defaults a session may take alone.

Tony, 2026-09-09: *"I don't think you can run this without my feedback."* He is right.

## Two decisions sitting with Tony

- **The TTX claim** — per-group with the zero-baseline denominators stated, or cut. Pooled
  across groups it is inadmissible under FOUNDATIONS §9, and the per-group breakdown
  reverses it: DI falls, MALE rises where the prior says unchanged, and ORX and OVX cannot
  produce a ratio at all.
- **Authorship.** The naive-reader role flagged *"A Claude Code session ran it on those
  instructions"* as the highest-variance sentence in a resume artifact — a cold evaluator
  cannot tell what Tony built from what was automated.

## Owed, and not yet filed — write these up before they are lost

- **The promiscuity gate is not in the bake-off's path.** `fair_bakeoff` picks each fold's
  knob by raw F1 argmax and never calls `pick_operating_point`, so `TooPromiscuous` and
  `EdgeOfRange` are inert; `settings_from_bakeoff` checks only fold agreement and grid edge.
  SPIKE-synch's selected knob sat over its own declared ceiling in five of six folds.
- **`check_quotes.py` misses a producer document.** Its marker wants a person-source phrase,
  so a verbatim quote introduced by *"its own README says"* passes. Goes in
  `docs/sapper_feedback/`, **not** into the check itself.
- **`tools/murderboard_prose.sh` is required by role 5's checklist and is absent from this
  tree** — a vendoring gap.
- **FOUNDATIONS §9's TTX magnitudes do not reproduce** from the root file the section names,
  and its own median/percentage pair cannot both describe one distribution.
- **The rate-matched treatment-window surrogate**, specified in `conditioned_run.md` and
  never run. It is the control that separates coordination from a marginal-rate response.
- One filed already:
  [`docs/todo/2026-09-09-an-edge-of-grid-threshold-refuses-on-one-branch-and-warns-on-the-other.md`](docs/todo/2026-09-09-an-edge-of-grid-threshold-refuses-on-one-branch-and-warns-on-the-other.md)
  — the murderboard sharpened it: the flag fires on three of six learned models, and the
  hand-written branch already carries the deciding rule in `pick_operating_point`'s plateau
  test.

## Traps this session hit

- **zsh does not word-split an unquoted parameter.** Building `--model a --model b` into a
  shell variable and passing it unquoted sends **one** argument; argparse reports every flag
  as unrecognised and the leading empty string is the tell.
- **A commit can land on a spent branch.** #513 merged while this worktree was still on its
  branch, so the next commit went somewhere already squashed. Check
  `git branch --show-current` against the last merged PR before committing.
- **A recording missing from a detections file is drawn at zero**, where it cannot be told
  from a detector that ran and found nothing. The figure now counts and names them.
- **The murderboard freshness gate is a hard stop, and it fires late.** It refused after the
  report was written. Run `bash tools/murderboard_freshness.sh --refresh` *before* drafting
  anything that will need review.
