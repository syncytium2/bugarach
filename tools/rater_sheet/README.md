# The rater sheet

People mark coordinated events on rows of raster, and say whether each row looks like a real
recording or a synthetic one. It answers Tony's question of 2026-10-22: *can synthetic data be
used to train and tune detectors, or do we fall back on events people mark?* A by-product is
psychophysics: how well people see coordination as participation, timing spread and background
change.

**The pilot is synthetic only.** Real rows wait on Tony's baseline-only release by name
(FOUNDATIONS §5). The survey runs in U-M Qualtrics, which Tony chose on 2026-10-23 for its
logins and control.

| file | what it is |
|---|---|
| `make_pilot.py` | builds the rows, the key, the paste-ready Qualtrics script and the preview into the darkroom |
| `rater_raster.js` | the raster: draws a row, takes marks, asks real or synthetic. Plain ES5, no dependencies |
| `qualtrics_glue.js` | connects the raster to a Qualtrics question |
| `preview.template.html` | the same sheet run locally, with a CSV laid out like a Qualtrics export |
| `score_export.py` | scores an export against the key: recall, precision, per-condition recall, d′ |

## The pilot's rows

**Every row is 15 minutes**, one x-axis length for everything the sheet will ever show (Tony,
2026-10-23). That length fits inside every one of Cossart's 59 DANDI:000219 recordings (shortest
1153.5 s) and inside this lab's 20-minute analysis windows, so real rows from both corpora can join
later without changing the axis. At 15 minutes a coordinated event is a hairline until you zoom, as
on the lab's own rasters, so the controls are buttons above the raster, not hidden gestures.

There are 10 rows of 32 ROIs, built with the bench's own simulator with no decoys (ADR-0019). Each of
5 conditions runs on both background fields:

- **tight timing** (0.105 s, measured on fast) and **wide timing** (0.5 s), each on a quiet and a
  busy background (`bench.REGIMES`). Each of these rows plants six events, two each at 30%, 20% and
  10% of ROIs, so every row tests every participation level;
- **nothing planted**, on the busy background.

The two fields are the **fitted** field (the bench's measured rate shape and slow bursts) and the
**flat** field (the same mean rate, no shape). In the pilot, "how real does this row look?" therefore
asks whether people can see what the fitting changed.

**The judgement is a slider** (Tony, 2026-10-23): real on the left, no idea in the middle, synthetic
on the right, stored from +1 to −1. Next stays locked until it has been touched, so a middle answer is
a choice, not an omission. The scorer reports the AUC (0.5 is chance) and the d′ that follows from it.

**A 30-second walk-through opens the survey.** It runs on a row of its own, never scored, and shows
every control: zoom, slide, mark, remove a mark, whole row, and the slider.

**Cossart's event rate is far higher than ours.** At their chosen K = 12, the median recording has
about 6 clusters a minute, around 90 in 15 minutes, against this lab's roughly 10 to 25
coordinated events an hour. A Cossart row would be a much bigger marking job. Lanes shrink to fit
(566 ROIs draw at 1 pixel each).

A mark counts as a hit within `bugarach.score.TOL_SEC` (2.5 s) of an event's median onset,
matched one to one, nearest first, the same tolerance the bench scores detectors with.

## The separation rows (added 2026-10-25)

Tony, 2026-10-25: *"What is the limit of human detection of separation"*: how close in time two
coordinated events can be before people mark them as one. Four more rows, **r11 to r14**, follow the
pilot's ten, which are byte-identical to before (a test checks their fingerprint).

- **Each row** is 15 minutes of 32 ROIs on the fitted background. It plants **six pairs**, one at
  each separation of 0.5, 1, 2, 3, 5 and 8 s (onset to onset), and **three single events** as
  controls, in random order, each in its own 90 s slot, so neighbouring items are about a minute
  apart at least and never interact.
- **Participation is fixed at 20%** (6 cells), so separation is the only thing varying within a row.
  The two events of a pair **recruit different cells**: one cell with two onsets 0.5 s apart is
  something no recording shows.
- **The four rows** are tight (0.105 s) and wide (0.5 s) timing, each on the quiet and the busy
  background.
- **The instruction** now on every row, in the walk-through and on the intro page: *if two events sit
  close together, mark both.*
- **Zoom is logged.** Every mark carries the width of the view it was placed in (`spans=` in the
  stored line). At full width a pixel is about 0.9 s, and a click within 7 pixels of a mark removes
  it, so a pair closer than about 6 s can only be marked as two after zooming. Whether people zoom is
  part of the result.

**How it is scored** (`score_export.py`, printed under each rater and pooled):

- A **pair** is looked at from 2.5 s before its first event to 2.5 s after its second, each event at
  the median onset of its cells. Each mark in that stretch goes to the nearer event. The pair is
  **resolved** when both events got a mark, and **detected** when either did.
- A **single** is **split** when it got two marks or more in its ±2.5 s. The split rate is the false
  alarm: "two where there was one".
- **P(resolved) against separation** is reported overall and per condition, with the narrowest view
  people used. A logistic curve in log separation is fitted, floored at the split rate. **D50** is the
  separation at which resolving runs halfway from that floor to certainty, and **D75** is three
  quarters of the way. When every pair or no pair is resolved, the fit says the limit lies outside the
  tested range.
- **The realized separation can be smaller than the planned one.** At wide timing and 0.5 s, the two
  groups' median onsets can coincide (r13 does). Then the pair holds no second cluster to find, and
  nobody can resolve it. That is the data's own limit: two Gaussian onset clouds stop being bimodal
  below twice their spread, 0.2 s at tight timing and 1 s at wide. Each outcome carries
  `realized_delta_sec` so the curve can be read against either.

**What the answer is compared with** (from the handoff): the data's own limit above; the assessor's
floor of about 3 s; and real event intervals, whose 5th percentile is 3.8 s on fast and 7.1 s on
slow. If people resolve pairs the assessor merges, people's marks are the better reference for close
events. The detectors' limit is derived in a sister handoff
(`docs/todo/2026-10-25-handoff-minimum-separation-theory.md`); the human curve belongs on the same
plot.

## Setting it up in Qualtrics (about 15 minutes)

1. `python tools/rater_sheet/make_pilot.py`. It prints the four files it wrote in
   `<darkroom>/bugarach/2026-10-23-rater-sheet-pilot/`.
2. **Try it locally first.** Open `explainer_rater-sheet-pilot-preview_20261023.html` in a browser.
   It is the same sheet.
3. In Qualtrics, create a survey. First block: one **Text/Graphic** question with the instructions
   (the preview's intro text can be reused). Its **Question behavior → JavaScript**: paste all of
   `explainer_rater-sheet-pilot-intro_20261023.js`. That is the walk-through; Next unlocks when it
   ends.
4. Add a second block with **one Text Entry question** (single line). In its question text, switch to
   the HTML view and add:
   `<span class="rater-row">${lm://Field/1}</span>` along with any instruction text you want.
5. In the question's left panel, **Question behavior → JavaScript**: delete the template and
   paste all of `explainer_rater-sheet-pilot-question_20261023.js`.
6. On the block, open **Loop & Merge**. Put the 14 ids (the pilot's ten and the four separation rows) from
   `explainer_rater-sheet-pilot-rows_20261023.txt` in Field 1, one per loop, and turn on
   **Randomize loop order**.
7. **Preview the survey.** Mark something on two rows, finish, then check
   **Data & Analysis**: each row's answer should read like
   `row=r07;real=0.45;marks=331.2,452.0`. If that column is empty, the page did not
   accept the script's write. Tell Claude what the editor shows, because the fix is in
   `qualtrics_glue.js`.
8. Export: **Data & Analysis → Export → CSV**, with "Use numeric values". Then:
   `python tools/rater_sheet/score_export.py <export.csv> <darkroom>/.../explainer_rater-sheet-pilot-key_20261023.json`

**The key never goes into the survey.** The script carries only event times, and a test checks
that.
