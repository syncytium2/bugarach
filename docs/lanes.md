# The lanes — what to work on, and why it is one at a time now

> ## Read this before the table: the queue is empty too
>
> **Updated 2026-08-23.** The three-item serial queue this page carried is **done**.
> Scoring is spliced into the page and the sweep runs through it. The download button
> is in, and the page writes `detections.csv` and `run.json`. CICADA landed, which
> made six of six. Three of the four lanes below had already landed; **model** is the
> only one still unstarted, and it needs Tony's go because it is compute rather than
> code.
>
> **What replaced the queue is not a fan-out either.** The webapp's remaining work is
> the in-browser trainer and the scoreboard's copy review, both in
> [`webapp_completion_plan.md`](webapp_completion_plan.md).
>
> **The defect this banner used to name is fixed** (2026-08-24, PR #262): the browser
> writes `detector_settings.csv`, `run.json` keys parameters by **detector and
> stream**, the stream is chosen at the door, and a tuned setting saves and loads as
> a file that names the data set it was fitted on. What is still open is one step
> further along — nothing hands that file to `bugarach detect`, so the per-lab loop
> ends before the command that would consume its answer.
>
> **And a new one, bigger than the old:** the browser and `bugarach detect` do not
> agree on how many detections one folder contains
> ([the routes disagree](todo/2026-08-24-two-routes-two-answers-on-one-folder.md)).
> Whoever next holds the page should read that before trusting either total.
>
> **Claim `docs/site/raster_viewer.html` by name** on `../bugarach-worktrees/SESSIONS.md`
> before editing it. That is the one rule on this page that has never gone stale, and
> it binds harder than when it was written: the file is 7,485 lines now, more than
> twice what it was, and several sessions a day want it.
>
> **Two traps the panel already paid for**, so the next one does not:
>
> - **The lab shim is APPENDED after the page's own script**, so `window.__lab` does not
>   exist at parse time. Anything gated on it waits for `DOMContentLoaded`. Wiring at parse
>   time leaves the panel hidden on exactly the page that should show it — and hidden is
>   also its correct *published* behavior, so **the bug looks like success**.
> - **Playwright's `inner_text()` returns empty for content inside a collapsed
>   `<details>`.** Now written down for good in
>   [`testing_a_sampling_port.md`](testing_a_sampling_port.md), because this page is a
>   queue that gets rewritten and that one is not.
>
> The rest of this page is kept because the *rules* in it still hold — the single-holder
> file, claiming your own block, the venv trap, and what each lane owed the others. Only
> the "start these in parallel" framing is spent.

The plan these come from is [`docs/webapp_completion_plan.md`](webapp_completion_plan.md);
the decision behind the training lane is [`ADR-0001`](adr/0001-the-lab-server.md).

## The one rule that makes parallel work possible here

**`docs/site/raster_viewer.html` is a single-holder resource.** Every UI phase edits that
one 7,485-line file, so only one session touches it at a time and claims it **by name**
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
| ~~**scoring**~~ | ~~`bugarach-worktrees/lane-scoring`~~ | [`todo/2026-08-19-lane-e-folds-and-scoring-in-the-browser.md`](todo/2026-08-19-lane-e-folds-and-scoring-in-the-browser.md) | ✅ **LANDED** — PR #160. `src/bugarach/score.py`, `bench.fold_split` (lifted out of `fair_bakeoff.py` so both languages divide the data set with the same call), and `docs/site/scoring.js`. **Spliced into the page** 2026-08-23; the sweep pools through it, and the byte-for-byte guard that armed itself when the splice markers appeared is now enforcing. |
| ~~**writer**~~ | ~~`bugarach-worktrees/lane-writer`~~ | [`todo/2026-08-19-lane-d1-the-detections-writer.md`](todo/2026-08-19-lane-d1-the-detections-writer.md) | ✅ **LANDED** — PR #158. `src/bugarach/emit.py`: the six detectors into one table, with the strength unit in the row. **Three callers now**: the browser's download, the Panel viewer's Save button, and `bugarach detect` over a whole folder. |
| **model** | branch fresh off `origin/main` | [`model_track.md`](model_track.md) queue, items 1 and 4 | close the seed gap; drop the raw brightness channel. **Not started, and still needs Tony's go — see below.** The only lane here that is not on the webapp queue, so it does **not** contend for `raster_viewer.html`. |

**All four worktrees are gone**, `lane-model` included — the merge gate now removes the
worktree whose PR it just landed, and the rest were swept. Branch fresh off
`origin/main` rather than looking for them, and write your own board block.

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

**Both prerequisites were discharged, and both paid off.** The writer landed before the
download button was written, which is why the browser's table and the library's are one
table with a test tying them together. The server landed before the in-browser trainer
starts, which turns that lane from *invent the numerics* into *match this*. Nothing is
now waiting on an ordering. If two PRs do touch the same file, the one that merges
second rebases — do not rebase somebody else's branch for them.

## Not in flight, deliberately

**The model lane**, above — real compute, and it wants asking first.

**CICADA landed**, so the hold Tony placed on it in 2026-08-19 is discharged and the
browser runs all six. The reason it was held is worth keeping, because it is a
property of the detector rather than of the schedule: CICADA's `onset_field` defaults
to the peak rather than the transient onset, the way its original does, and
`store.py`'s note on that has already misled two readers.
