---
status: waiting-on-tony
filed: 2026-09-22
---

# The corrected jitter flattens SPIKE-synch across the background axis

**Found** by the WSMIP065 overnight session on 2026-09-22, immediately after adopting the
measured jitter. **It stops the every-knob re-searches** (overnight handoff, WSMIP065 step 5),
which is why it is filed rather than worked around.

## What happened

Tony ruled the measured jitter in: fast **0.36 s → 0.106 s**. Both re-measures ran clean and
every bench constant landed inside its interval. Then `tests/test_background_curve.py` went red:

```
sync reported a bare F1: F1 0.657, flat across 2.6–40 mHz/ROI (spread 0.026)
assert 0.026 > 0.05          # BACKGROUND_TOLERABLE_SPREAD
```

**Figure 1, the background curve on the re-measured bench** —
`<darkroom>/bugarach/2026-09-22-jitter-background-curve/background_curve.png`, 12 seeds per
grid point, base recording `baseline_quiet`. Abbreviations: **F1**, the harmonic mean of
recall and precision; **ROI**, region of interest (one imaged cell); **mHz/ROI**,
millihertz per ROI, the background event rate each cell fires at.

| detector | F1 at quiet | F1 at busy | spread across grid |
|---|---|---|---|
| rate+context | 0.668 | 0.648 | 0.178 |
| CoactDetect | 0.781 | 0.661 | 0.165 |
| LoCo | 0.808 | 0.678 | 0.156 |
| binned SCE | 0.578 | 0.498 | 0.087 |
| locust | 0.647 | 0.637 | 0.081 |
| **SPIKE-synch** | **0.657** | **0.637** | **0.026** |

In Figure 1's panel A, SPIKE-synch is the line that does not descend.

## Why it is a finding and not a broken test

The threshold it crosses is not arbitrary. `BACKGROUND_TOLERABLE_SPREAD` is 0.05 because the
published bake-off asks readers to believe a **0.017 F1** gap between its top two rows; a
detector whose score moves less than about three times that across the difficulty axis is one
whose bare F1 is quotable. The MILESTONES row *"Background is an axis, not a point — **nothing
is flat across it** — every detector moves across the axis and a bare F1 is refused for all
six"* is `measured`, `current`, and pinned to `c7786f2`. **It is no longer true of this bench.**

The mechanism is unsurprising once stated. SPIKE-synch is the one detector that keys on
coincidence *timing* rather than on counts or rate. Tightening planted jitter by about 3.4×
sharpens exactly the feature it reads, so it now resolves events at every background level
instead of degrading as the field fills up. That is the bench getting easier for one detector
in particular, not that detector getting better.

## Why it stops the searches

Step 5 searches every knob of all six detectors on this bench and proposes operating points.
For SPIKE-synch the axis has stopped discriminating, so a setting chosen on it would be chosen
against a flat objective — and the slow thread already adopted SPIKE-synch at `max_gap` 4 s on
evidence from the **old** jitter. Spending the hours before that is settled produces numbers
that need redoing.

## What is actually being asked

Three readings, and they are not equivalent:

1. **The measurement is right and the bench should be re-derived around it.** The jitter was
   wrong for a year; the difficulty axis was built on top of the wrong value, so the axis is
   what needs revisiting — its grid, or `BACKGROUND_TOLERABLE_SPREAD` itself.
2. **The measurement is right and the milestone is wrong.** "Nothing is flat across it" was a
   property of a bench that planted events three times too loose. The honest correction is to
   the row, not to the bench.
3. ~~**The correlogram measures something the bench should not plant directly.**~~ The worry was
   that planting 0.106 s on a 0.1 s grid is planting near the floor of what the grid can
   express, so the flattening would be quantisation rather than a real change. **Checked, and
   it is not the explanation.** The correlogram's own calibration — the simulator run at a grid
   of planted jitters, in the record — is monotone and close to linear right through the region
   in question, at about 1.7× planted:

   | planted (s) | 0.05 | 0.10 | 0.15 | 0.20 | 0.30 | 0.36 |
   |---|---|---|---|---|---|---|
   | measured half-width (s) | 0.096 | 0.175 | 0.246 | 0.323 | 0.511 | 0.626 |

   The bench distinguishes 0.05 s from 0.10 s from 0.15 s cleanly, so 0.106 s is well inside
   what the 0.1 s grid expresses and is not sitting on a floor. **The flattening is a real
   property of the corrected bench.**

So reading 3 is closed. **Readings 1 and 2 are Tony's**, and they differ in what gets edited:
the bench's difficulty axis, or the milestone that describes it.

## Also blocked by the same change

`tools/build_fair_comparison_report.py` asserts the live bench's `jitter_sec` equals what a run
declared, and **refuses to rebuild the 2026-09-18 fair comparison** — three test errors. The
guard is correct: goal 2's weekend result, its merge-gap addendum and the leaderboard were all
measured at 0.36 s. Nothing is wrong with those numbers; they belong to the old bench and cannot
be re-rendered against this one. Whether that run is re-run (about 28 GPU-hours), frozen against
its own declaration, or rebuilt with a superseded-bench banner is a decision, not a fix.

## Where the pieces are

- The figure: `<darkroom>/bugarach/2026-09-22-jitter-background-curve/` (claimed, `docs/SESSIONS.md`)
- The constants and both records: [#738](https://github.com/syncytium2/bugarach/pull/738), draft
- The measurement: `docs/learned/runs/2026-09-22-jitter-correlogram/`
- The test that fails: `tests/test_background_curve.py`, `test_every_detector_refuses_a_bare_f1`
  and `test_the_spreads_dwarf_the_differences_the_bakeoff_asks_about`
- The milestone it contradicts: `docs/MILESTONES.md`, section B, `c7786f2`
