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

There are 20 rows, each 120 s of 32 ROIs, built with the bench's own simulator with no decoys
(ADR-0019). Ten conditions run on both background fields:

- **participation** 0.30, 0.20, 0.10 of ROIs, with tight timing (0.105 s, measured on fast), on a
  quiet and a busy background (`bench.REGIMES`);
- **wide timing**, 0.5 s, at 0.20, on both backgrounds;
- **nothing planted**, on both backgrounds.

Planted rows carry 3 events each. The two fields are the **fitted** field (the bench's measured
rate shape and slow bursts) and the **flat** field (the same mean rate, no shape). In the pilot,
"real or synthetic?" therefore asks whether people can see what the fitting changed.

**A known weakness:** every planted row's first event falls between 30 and 45 s, because of the
generator's minimum spacing and margin. Raters may learn that. Fix it before the real-row
version.

A mark counts as a hit within `bugarach.score.TOL_SEC` (2.5 s) of an event's median onset,
matched one to one, nearest first, the same tolerance the bench scores detectors with.

## Setting it up in Qualtrics (about 15 minutes)

1. `python tools/rater_sheet/make_pilot.py`. It prints the four files it wrote in
   `<darkroom>/bugarach/2026-10-23-rater-sheet-pilot/`.
2. **Try it locally first.** Open `explainer_rater-sheet-pilot-preview_20261023.html` in a browser.
   It is the same sheet.
3. In Qualtrics, create a survey. Add an intro text question; the preview's intro text can be
   reused.
4. Add a block with **one Text Entry question** (single line). In its question text, switch to
   the HTML view and add:
   `<span class="rater-row">${lm://Field/1}</span>` along with any instruction text you want.
5. In the question's left panel, **Question behavior → JavaScript**: delete the template and
   paste all of `explainer_rater-sheet-pilot-question_20261023.js`.
6. On the block, open **Loop & Merge**. Put the 20 ids from
   `explainer_rater-sheet-pilot-rows_20261023.txt` in Field 1, one per loop, and turn on
   **Randomize loop order**.
7. **Preview the survey.** Mark something on two rows, finish, then check
   **Data & Analysis**: each row's answer should read like
   `row=r07;judge=probably_real;marks=31.2,52.0`. If that column is empty, the page did not
   accept the script's write. Tell Claude what the editor shows, because the fix is in
   `qualtrics_glue.js`.
8. Export: **Data & Analysis → Export → CSV**, with "Use numeric values". Then:
   `python tools/rater_sheet/score_export.py <export.csv> <darkroom>/.../explainer_rater-sheet-pilot-key_20261023.json`

**The key never goes into the survey.** The script carries only event times, and a test checks
that.
