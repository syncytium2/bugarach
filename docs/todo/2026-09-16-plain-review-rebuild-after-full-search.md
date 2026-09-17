---
status: done
filed: 2026-09-16
closed: 2026-09-17
---

# Rebuild the plain-language review on tonight's settings, and give Figure 2 a representative recording

**Done 2026-09-17, on the settings already on `main`, not on the overnight search's.** Tony, that morning:
*"all overnight runs failed. it is imperative we complete the word doc with our current 'best' params"*.
The current best are the 2026-09-16 retune (#597: rate+context 4.5 Hz, LoCo 99.5, binned SCE 98; CoactDetect,
locust and SPIKE-synch confirmed), with locust's measured durations (#594) and binned SCE scored over its bin
(#593). The sliding CoactDetect and LoCo (`sliding-loco-coact`) are **not** in the document: their settings
are not chosen and the branch is not on `main`; Section "How we grade a program" says they are being tested.

## What changed

- **Scores are the stored settings', on recordings none was chosen on.** `make_detector_review.py --stages
  stored` scores each program at `OPERATING_POINTS` on bench recordings 1000–1023; the retune chose on 1–48.
  Figure "scores" reads `stored_*` (all 24 recordings, spread over four groups of six). The old per-round
  picks (`perf_*`, `opt_quiet_*`) and the "why not keep the rounds' settings" paragraphs are gone, and so is
  binned SCE's second dot.
- **First-review measurements rebuilt without the learned checkpoints**:
  `make_detector_review.py --out <plain>/_review_best --carry-learned <first review>/measurements --stages
  stored shipped blockrecall real`. Learned-model results do not read the programs' settings, so they are
  carried over; `load_models` returns only checkpoints that exist. The plain builder reads
  `measurements/` or `_work/` (`_measured`). The `real` stage's own figure rendering fails on a missing
  `make_group_raster_summary.RASTER_PX` after its calls are cached — not needed here, not fixed.
- **Bug fixed: the page and the docx embedded the first review's four real-recording PNGs** (old settings,
  learned-model lanes) although the plain builder draws its own. Both now use the builder's figures, and the
  "four extra tube rows" paragraph became one sentence saying learned models are left out.
- **Figure 2 by a stated rule** (`PROBLEM_MIN`, `PROBLEM_STRIPES`): brief events, 3 min before to 10 min after
  the drug; among recordings with at least 2 clear stripes there, the median disagreement (lower middle).
  Picks TTX DI (2 eligible: TTX DI spread 2.5, TTX MALE 4.6; the old pick, senktide ORX, has spread 50 and no
  stripe). The figure now marks clear stripes, and the caption says which programs call each, how the
  recording was chosen and the settings' date.
- **Close-up B** (busy, no stripe) is chosen across all brief-event recordings, since Figure 2's recording
  held stripes in its busiest 90 s. **Real tallies:** binned SCE's calls cover their bin (its inside-window
  stripe share went 61% → 89%); "called by 3 or fewer" counts the six programs, not ten rows.
- **locust** text: measured durations, not a fixed second.
- Darkroom `real_prose.json` rewritten against the rebuilt numbers and figures.

## Still open

- `HANDOFF-detector-optimization.md` predates #597 and is stale in §1–§3; the retune answered most of it.
- Murderboard the rebuilt document, then send the docx.
- The four real-recording figures have 1.5 px vertical overlaps between stacked lane labels (render_check);
  legible in the PNGs.
