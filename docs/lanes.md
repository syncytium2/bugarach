# The lanes — what to work on, and why it is one at a time now

> ## Read this before the table: the parallel phase is over
>
> **Updated 2026-08-20.** The four lanes below ran and **three of them landed**:
>
> | lane | landed |
> |---|---|
> | **server** | `src/bugarach/lab.py` + `bugarach lab` (PRs #159, #161, #162), and the training panel that reaches it (#168) |
> | **scoring** | `src/bugarach/score.py`, `bench.fold_split`, `docs/site/scoring.js` (#160) |
> | **writer** | `src/bugarach/emit.py` (#158) |
> | **model** | not started — still needs Tony's go, see below |
>
> **What is left is a queue, not a fan-out.** Every remaining webapp task edits
> `docs/site/raster_viewer.html`, so they go one session at a time, in this order:
>
> 1. **splice [`docs/site/scoring.js`](site/scoring.js)** into the page — `foldSplit` and
>    `poolScores` exist and nothing calls them yet. Plain script, not a module, because
>    the build refuses a page containing `import(`; the splice is a paste.
> 2. **the download button** — `detections.csv` out of the browser. **Read
>    `emit.DETECTOR_FIELDS`, not the detector dataclasses**: the six disagree about their
>    own field names and about what "strength" means, and copying one detector's spelling
>    is how a second dialect starts. `tests/test_emit.py` is the round-trip bar — a real
>    zero stays zero, NaN is absence, `NA` spelled literally, newline-only endings.
> 3. **CICADA**, the sixth detector — **held at Tony's instruction, 2026-08-19.** Not
>    blocked, not started, and not to be picked up without asking.
>
> **Claim `docs/site/raster_viewer.html` by name** on `../bugarach-worktrees/SESSIONS.md`
> before editing it. The rule below has not changed; what changed is that it now binds
> everything left rather than nothing.
>
> **Two traps the panel already paid for**, so the next one does not:
>
> - **The lab shim is APPENDED after the page's own script**, so `window.__lab` does not
>   exist at parse time. Anything gated on it waits for `DOMContentLoaded`. Wiring at parse
>   time leaves the panel hidden on exactly the page that should show it — and hidden is
>   also its correct *published* behaviour, so **the bug looks like success**.
> - **Playwright's `inner_text()` returns empty for content inside a collapsed
>   `<details>`.** Use `text_content()`, or open the accordion first.
>
> The rest of this page is kept because the *rules* in it still hold — the single-holder
> file, claiming your own block, the venv trap, and what each lane owed the others. Only
> the "start these in parallel" framing is spent.

The plan these come from is [`docs/webapp_completion_plan.md`](webapp_completion_plan.md);
the decision behind the training lane is [`ADR-0001`](adr/0001-the-lab-server.md).

## The one rule that makes parallel work possible here

**`docs/site/raster_viewer.html` is a single-holder resource.** Every UI phase edits that
one ~3,000-line file, so only one session touches it at a time and claims it **by name**
on `../bugarach-worktrees/SESSIONS.md`. Every lane below is chosen to avoid it — that is
why they can run at once. If your work starts wanting that file, stop and claim it first.

## Claim your own block

`.githooks/pre-commit` refuses a commit from a worktree with no block on the machine-local
board, and **that message is the intended path** — write your own block when it fires. Do
**not** write one for another session: the gate matches by worktree name, so a block
somebody else wrote releases the gate without that session ever having read the board.

## The lanes

| lane | worktree + branch | read this first | what it is |
|---|---|---|---|
| ~~**server**~~ | ~~`bugarach-worktrees/lane-server`~~ | [`todo/2026-08-19-lane-h1-the-lab-server.md`](todo/2026-08-19-lane-h1-the-lab-server.md) | ✅ **LANDED** 2026-08-20 — `main` @ `9ed4140`, PR #159. `bugarach lab`, the shim and the publish gate are in, and the server reproduces `bakeoff.json` per fold. **Do not start this lane.** Its todo now carries the request/response shapes, which is what **H2 was blocked on**. |
| ~~**scoring**~~ | ~~`bugarach-worktrees/lane-scoring`~~ | [`todo/2026-08-19-lane-e-folds-and-scoring-in-the-browser.md`](todo/2026-08-19-lane-e-folds-and-scoring-in-the-browser.md) | ✅ **LANDED** — PR #160. `src/bugarach/score.py`, `bench.fold_split` (lifted out of `fair_bakeoff.py` so both languages divide the corpus with the same call), and `docs/site/scoring.js`. **Not yet spliced into the page** — that is queue item 1 above. |
| ~~**writer**~~ | ~~`bugarach-worktrees/lane-writer`~~ | [`todo/2026-08-19-lane-d1-the-detections-writer.md`](todo/2026-08-19-lane-d1-the-detections-writer.md) | ✅ **LANDED** — PR #158. `src/bugarach/emit.py`: the six detectors into one table, with the strength unit in the row. **No download button yet** — queue item 2. |
| **model** | `bugarach-worktrees/lane-model` | [`model_track.md`](model_track.md) queue, items 1 and 4 | close the seed gap; drop the raw brightness channel. **Not started, and still needs Tony's go — see below.** The only lane here that is not on the webapp queue, so it does **not** contend for `raster_viewer.html`. |

`lane-model` is created off `origin/main` and otherwise untouched; the board block is
yours to write. **The other three worktrees have been removed** — their work is on `main`,
so branch fresh rather than looking for them.

**Before you run anything in a worktree**: the venv is an editable install rooted in the
*primary* checkout, so a test run from here can execute a different branch's code and pass
clean. Set `PYTHONPATH=src` and confirm it took —
`python -c "import bugarach; print(bugarach.__file__)"` must print a path inside **your**
worktree. This has already turned a reported green suite into a result about the wrong
branch.

## ⚠ The model lane is not pre-approved

[`docs/model_track.md`](model_track.md) opens with *"Nothing here is approved to run"*, and
[`docs/overnight_spec.md`](overnight_spec.md) governs what may run unattended. Multi-seed
training is real compute. **Ask before starting it**; the other three lanes need no such
permission because they are code, not experiments.

## What each lane owes the others

- **writer** settles the `detections.csv` shape **once**, in the library, so the browser
  half cannot ship a second dialect of the same table. It is the only lane whose output
  another lane copies rather than calls.
- **scoring** is consumed by Phase 2 and Phase 4 both. Keep it pure functions with no UI —
  the moment F1 is computed in a UI layer, two halves of a comparison end up on different
  metrics, which has already happened here once.
- **server** defines what a correct trained model looks like, which is what turns the
  in-browser trainer (lane C, later) from *invent the numerics* into *match this*.
  **It has landed, so lane C is now unblocked** — the thing to match is
  `bugarach.lab` calling `learn.train`, and the number to match is the per-fold
  agreement with `bakeoff.json` that its test asserts.
- **model** decides whether *"the tube outperforms"* is a claim this project owns. Today it
  **ties** CoactDetect — 0.668 ± 0.061 against 0.651 ± 0.044 — with no seed error bars
  anywhere.

## Landing order, when several are ready at once

**Both prerequisites are discharged.** Writer landed before the download button is
written; server landed before lane C starts. What remains contends for one file rather
than for an ordering, so the sequencing question has become the queue at the top of this
page. If two PRs do touch the same file, the one that merges second rebases — do not
rebase somebody else's branch for them.

## Not in flight, deliberately

**CICADA** — the sixth detector, and the last one missing from the browser. Held at Tony's
instruction, 2026-08-19. It queues on `raster_viewer.html` behind nothing; it is simply not
started.
