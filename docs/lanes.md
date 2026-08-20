# The lanes — what to work on, in a worktree that is already waiting for you

**If you were started with a lane name, this is your first page.** Find your row, read the
todo it points at, claim the machine-local board, and go.

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
| **server** | `bugarach-worktrees/lane-server` | [`todo/2026-08-19-lane-h1-the-lab-server.md`](todo/2026-08-19-lane-h1-the-lab-server.md) | `bugarach lab` on loopback, the `window.__lab` shim, the publish gate. **The long pole.** |
| **scoring** | `bugarach-worktrees/lane-scoring` | [`todo/2026-08-19-lane-e-folds-and-scoring-in-the-browser.md`](todo/2026-08-19-lane-e-folds-and-scoring-in-the-browser.md) | fold split + `bench.pool_scores` in JS, so held-out scoring exists at all |
| **writer** | `bugarach-worktrees/lane-writer` | [`todo/2026-08-19-lane-d1-the-detections-writer.md`](todo/2026-08-19-lane-d1-the-detections-writer.md) | `detections.csv` + `run.json` in the library. **Nothing in this tree writes a data file yet.** |
| **model** | `bugarach-worktrees/lane-model` | [`model_track.md`](model_track.md) queue, items 1 and 4 | close the seed gap; drop the raw brightness channel. **Needs Tony's go — see below.** |

Each worktree is already created off `origin/main`. Nothing else about them is set up,
deliberately: the board block is yours to write.

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
- **model** decides whether *"the tube outperforms"* is a claim this project owns. Today it
  **ties** CoactDetect — 0.668 ± 0.061 against 0.651 ± 0.044 — with no seed error bars
  anywhere.

## Landing order, when several are ready at once

No lane blocks another, so land whichever is green. The only sequencing that matters is
that **writer** should land before the browser download button is written, and **server**
before lane C starts. If two PRs touch the same file, the one that merges second rebases —
do not rebase somebody else's branch for them.

## Not in flight, deliberately

**CICADA** — the sixth detector, and the last one missing from the browser. Held at Tony's
instruction, 2026-08-19. It queues on `raster_viewer.html` behind nothing; it is simply not
started.
