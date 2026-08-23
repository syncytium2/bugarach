---
status: open
filed: 2026-08-20
---

# The scoreboard's numbers are built; its sentences have not been reviewed

Phase 4 of [`the completion plan`](../webapp_completion_plan.md) landed as a
panel that scores every detector on one data set and one fold split. **The panel
is gated on `window.__lab` and hidden on the published page**, on purpose: the
wording below has not been through
[`the document review process`](../doc_review_process.md), and this repo does not
ship copy an outside reader sees until it has.

Un-hiding it is one line — the gate in `wireLab`. Do that after the review, not
before.

## The copy, in full

It lives in one object, `SCORE_COPY` in `docs/site/raster_viewer.html`, so a
reviewer reads it in one place rather than hunting it through the render code.

| key | sentence |
|---|---|
| `draft` | *Draft — the wording on this panel has not been reviewed, which is why it does not appear on the published page.* |
| `simulatedOnly` | *Every number here is measured on simulated recordings. None of it says a detector is right about a real slice, because no real slice has an answer key to be right against.* |
| `tolerance` | *F1 counts a hit within the match tolerance above. Against events this wide that makes the ORDER of these rows meaningful and a single number's decimal places not — read the ranking, not the gap.* |
| `noTube` | *The learned detector is not in this table. It trains through the server rather than in the page, and a row scored on a different data set than the rest would be the one comparison this table exists to avoid.* |
| `heldOut` | *Each detector's setting is chosen on the folds it may see and scored on the fold it may not. The spread is across folds.* |

Plus one sentence generated per run, when a detector could not have a setting
chosen on every fold: *"… could not have a setting chosen on every fold: the best
value on those folds sat at the end of the grid, which the sweep reports rather
than returns. Those rows rest on less evidence than the others and their spread
is not comparable."*

## What the review has to check, beyond the usual

- **No claim about a real slice.** Everything measured is simulated, and the
  panel says so — but it sits one accordion away from a Detect step that runs on
  the reader's own recordings, and the two must not blur.
- **The banned phrase.** *"competes with state-of-the-art"* must not appear, in
  any spelling: the comparison holds no published learned method and none of the
  assembly-detection family. `test_no_banned_phrase_anywhere_in_the_page` guards
  the literal strings; a reviewer has to guard the paraphrase.
- **The tube's absence must not read as the tube losing.** `bakeoff.md` has it in
  a **tie at the top** — 0.668 ± 0.061 against CoactDetect's 0.651 ± 0.044, with
  one training run per fold and so no seed error bars to test the difference
  with. An empty row is easier to misread than a stated one.
- **`knobs` is a count of settings, not a complexity measure**, and it is the
  column that makes the tube's 1,149 parameters a comparison rather than a
  boast. Check it cannot be read as "fewer is better".

## What is already mechanised

`tests/test_webapp_scoreboard.py` pins the gate (the panel is hidden on the
published page and present in the file rather than added by a build), the banned
phrases, that every detector is offered the same folds, and that a detector which
answered fewer of them says so on screen.

That last one was a bug this panel's own test caught on its first run: folds where
`pickOperatingPoint` refused a boundary answer were being skipped and averaged
over silently, so each detector had its own denominator — the one thing the panel
exists to prevent — and a row resting on one fold of three showed a confident F1
with no spread.
