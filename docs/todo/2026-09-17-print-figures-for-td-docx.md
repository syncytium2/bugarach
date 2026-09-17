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
| 21-24 | real_{ttx,senk}_{brief,long} | done: names once in a key, counts per row (fig21-24_real_*) | yes, caption on the same page |
| 25 | fig_eye | done at 646 pt, placed at the full 6.5 in (the builder had narrowed it to 426 pt) | yes; fills its page, caption starts on the next (as before) |
| 4-9, 16, 17, 20 | count_rule, count_edge, count_slices, count_published, chance_steps, shift_shuffle, simulator, grading, count_bar | done (fig04-09, 16, 17, 20) | yes |

**All 25 in the -td docx, 2026-09-17.** Word PDF: 40 pages, every figure at 6.5 in, every caption on its figure's
page except Figure 25 (fills its page; its long caption starts on the next, as before). PDF beside the docx:
`detector_review_plain-td.pdf`. Backups: `detector_review_plain-td.before-print-figures.docx` (Tony's copy before
any swap) and `.before-program-figures.docx`.

Left for Tony: nothing in the figures depends on him; he has not seen the print versions of 4-25.
