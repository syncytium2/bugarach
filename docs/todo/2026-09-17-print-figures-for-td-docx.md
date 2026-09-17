---
status: open
filed: 2026-09-17
---

# Redraw the plain review's figures for print and swap them into Tony's edited docx

**Tony, 2026-09-17:** the figures print at ~5 pt in Word; redraw each "with proper font sizes", then add them
to his hand-edited copy `<darkroom>/bugarach/2026-09-15-detector-review-plain/detector_review_plain-td.docx`.
Never rebuild over it (`make_plain_detector_review.py --stages docx` writes the OTHER file,
`detector_review_plain.docx`). He has no time to edit further: swap figures in, keep his text.

## How

- `tools/make_print_figures.py --plain <that folder> --figs <name>` draws on a 468-unit canvas (1 unit = 1 pt
  at 6.5 in), text >= 8 pt, into `<folder>/print_figures/`. Each figure is a function registered in `FIGURES`
  (page name -> (stem, function)); port the page version from `make_plain_detector_review.py`, render, LOOK
  at the PNG, fix clipping/overlaps, commit.
- `tools/swap_print_figures_into_docx.py` (run with system `python`): finds each old figure in the docx by
  its exact PNG bytes, replaces it, rescales height to the new aspect, keeps a backup
  (`detector_review_plain-td.before-print-figures.docx`). Extend its `PAIRS` (page PNG -> print PNG) and rerun;
  it is idempotent for figures already swapped only if their OLD png still matches, so swap each figure once
  (remove done pairs, or it exits "found n of m").
- Check with Word COM -> PDF (`SaveAs2(pdf, 17)`) and look at the pages.

## Status

| figure | page name | print | in -td docx |
|---|---|---|---|
| 1 | fig_orient | done (fig01_orient) | yes |
| 2 | fig_problem | done, a tick per minute (fig02_problem) | yes |
| 3 | fig_chance | done, asterisk on B's tallest bin (fig03_chance) | yes |
| 10-15 | fig_alg_{rate,coact,loco,sce,cicada,sync} (`fig_algorithm`) | done: steps full width, settings beside the chance picture, A/B below (fig10-15_alg_*) | yes; each caption on its figure's page (Word PDF, 37 pages) |
| 18 | fig_scores | done (fig18_scores), numbers from `_review_best/_work/numbers.json` | yes |
| 19 | fig_busy | done, two-line panel titles (fig19_busy) | yes |
| then | 4 count_rule, 5 count_edge, 6 count_slices, 7 count_published, 8 chance_steps, 9 shift_shuffle, 16 simulator, 17 grading, 18 scores, 19 busy, 20 count_bar, 21-24 real_* (`fig_real_overview`), 25 fig_eye (reuse `_closeup` in the print tool) | | |

Priority after 10-15: 18-19, 21-25, then the rest.
