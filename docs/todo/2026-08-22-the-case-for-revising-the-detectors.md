---
status: open
filed: 2026-08-22
---

# The case for revising the detectors, and the tasks that follow from it

Written 2026-08-22, at the end of the session that did the webapp work. **The
figures every claim below rests on are in
`<darkroom>/bugarach/2026-08-22-app-notes/`**, with a README walking each one.
This is the repo copy, so the argument is findable without the Dropbox mounted.

Tony's read at the time: *"at this point there is strong evidence to revise many
of the detectors … there's big changes coming and we will reassess where we are
when we get there."*

This is the evidence, assembled in one place, and the work it implies. It is
**not** a plan to execute — the reassessment comes first, and several items below
would be answered or cancelled by decisions that have not been made.

> **Not murderboarded.** This is an internal handoff, and the session that wrote
> it was nearly out of context — running the eleven-role review would have been
> the last thing it did badly rather than the first thing it did well. Every
> number is quoted from a named file or a measurement recorded in this folder, so
> it is checkable. **If any of it goes to an outside reader, murderboard that
> artifact first.**

---

## The short version

The operating points were chosen against a simulated field that differs from a
real one in a way that was measured, written down, and never wired in. Six
independent observations point the same direction, and three of them surfaced
this week from ordinary use rather than from anyone auditing the calibration.

Nothing here says a detector is *wrong*. It says the **settings** were fitted on
the wrong background, and that at least two of the six have sweep grids that do
not bracket their own best answer.

---

## The evidence, strongest first

### 1 · Every published operating point was fitted on a flat field, and real fields are not flat

`bench.MEASURED_RATE_SHAPE = 0.275` is a maximum-likelihood fit over **81
baseline windows / 2,643 ROIs**. `simulate.py` records what it buys, measured
rather than argued:

> measured over 81 baseline windows, **35% of real ROIs record no event at all**
> and the busiest reaches **486 mHz**, while the flat generator leaves **2%
> silent** and tops out near **138**. Its typical ROI is *busier* than a real one
> and its busiest is far quieter — **wrong in both directions at once**.

And `bench.py` says plainly what was done with it:

> ⚠ **Not wired into the bench.** `BENCH_RECORDING` still runs a flat field, so
> every operating point and every score in this package is still measured on the
> old background.

`fair_bakeoff.py` sets no shape either, so **`bakeoff.json` is flat too**. Every
number in the published comparison was measured on a field whose typical ROI is
too busy and whose busiest is too quiet.

**This is the load-bearing item.** The other five are consequences or corroboration.

### 2 · The calibration campaign was already marked provisional

`bench.py`, on where the settings came from:

> `optim_history/README.md` marks the whole campaign **PROVISIONAL**, and notes
> that the calibrated settings were adopted on 2026-08-05 *without* the real-data
> validation the deck named as the deciding step. These numbers are measurements;
> **the decision that rested on them was never checked.**

So the operating points were never claimed to be final. Revising them is
resuming a paused process, not overturning a settled one.

### 3 · Two detectors cannot choose a setting on most folds — their grids do not bracket the answer

From the scoreboard (`05-scoreboard-draft.png`), six detectors on one data set and
one fold split. The **folds** column:

| detector | folds answered | F1 (held out) |
|---|---|---|
| CoactDetect | 3 of 3 | 0.792 ± 0.012 |
| RateDetect | 3 of 3 | 0.707 ± 0.105 |
| SPIKE-synch | 3 of 3 | 0.591 ± 0.076 |
| **SCE** | **1 of 3** | 0.583, no spread |
| **LoCo** | **0 of 3** | — |
| **CICADA** | **0 of 3** | — |

`pickOperatingPoint` refuses a best value sitting at the end of the grid — the
sweep saying it stopped too early. Half the detectors hit that on most folds.
**That is a direct measurement that their sweep grids are wrong for this
data set**, and the grids are where the operating points came from.

Note the second-order finding: a detector that answers one fold also has **no
spread**, so its single F1 looks more confident than the ones measured three
times. The column exists because of that.

### 4 · CICADA at its shipped settings is not usable on a simulated data set

From the lane figure (`09-six-detector-lanes.png`), one 20-minute recording:

    rate 8 · SCE 5 · coact 5 · LoCo 6 · sync 9 · CICADA 264

Five detectors agree on a handful of events at roughly the same times. CICADA
calls **264**. That is its operating point being wrong for this background by a
wide margin, visible without any scoring at all.

### 5 · The difficulty axis moved underneath the settings

`bench.REGIMES` was re-derived from the approved export folder on 2026-08-20:
endpoints went **3.8 → 5.2 mHz** and **17.5 → 19.0 mHz**, the span narrowing from
4.6-fold to 3.7-fold. Both ends moved up. Every bench number in the tree was
computed against the old range.

The re-derivation measured that this *reorders nothing* and moves no detector
beyond seed noise — so it is not an emergency. But it does mean the axis the
operating points were chosen along is not the axis in the file now.

### 6 · The scoring tolerance is looser than the events it scores

The bench counts a hit at a **1.5 s** edge gap against a median realized event
**0.80 s** wide, and every detector plateaus by **~0.75 s**
(`docs/learned/tolerance_sweep.png`). The *ranking* survives the sweep; a bare F1
implying timing accuracy does not. Any revision should decide what overlap to
require rather than inherit one permissive constant —
`docs/todo/2026-08-17-scoring-cannot-see-localization.md`.

---

## What this session changed that bears on it

Two fixes landed that were affecting tuning while nobody could see them.

**The browser was tuning against a data set ~4.8× too quiet in the mean.**
`simulateFromMeasurement` handed `roi_rate_med` — a median — to a knob that means
the field's mean. On the fitted background those differ by a factor of 4.8
(`median/mean = median(Gamma(0.275,1))/0.275 = 0.2098`, exact). Fixed in PR #199:
the rate now carries `bg_rate_stat`, and `rate_as_mean` **refuses** a rate that
does not say which statistic it is. Nothing published was affected — Python runs
flat, where the two coincide — but every browser-side tuning run before that fix
was against the wrong background.

**And the two generators still disagree.** The browser defaults to the *fitted*
background; Python's bench runs *flat*. Same project, two ideas of what a
recording looks like. That is item 1 wearing different clothes, and it is why
item 1 is first.

---

## The tasks

Ordered by whether they are blocked on a decision.

### A · Decide before anything else: does the bench move to the fitted background?

This is the fork. `bench.py` states the cost in terms: switching **"re-derives
the whole bench and is not a default change"** — every operating point, every
number in `bakeoff.md`, every figure that quotes one.

- **If yes**, items B and C below are subsumed: the grids and the operating
  points get re-derived together against the field the detectors will actually
  meet, and it is one campaign rather than three patches.
- **If no**, the browser should probably default to *flat* so the two generators
  agree, and the fitted background becomes a diagnostic rather than the default —
  which is a smaller change but concedes item 1's measurement.

Everything else is cheaper after this is answered. `docs/todo/2026-08-14-generator-background-model-is-flat.md`.

### B · Re-derive the sweep grids so they bracket their answers

Independent of A, and measurable now: LoCo, CICADA and SCE hit the grid boundary
on most folds. Widen until `pickOperatingPoint` returns an interior row, then
re-run. Cheap, and it makes item 3's column stop firing.

### C · Re-fit the operating points

Downstream of A and B. The campaign is already marked provisional, so this is
resumption rather than reversal. `docs/todo/2026-08-12-reconcile-detector-defaults.md`
is the existing entry.

### D · Settle the scoring tolerance

`docs/todo/2026-08-17-scoring-cannot-see-localization.md`. Worth doing **before**
C, or C fits against a criterion nobody chose.

### E · Four webapp notes still open

Not blocked on any of the above; the record is
`docs/todo/2026-08-21-app-notes-from-use.md`.

- **12 · which detectors to tune.** Cheapest real win left, and it *merges* two
  functions: one selected is today's Tune, all six is today's scoreboard. The
  picker infrastructure landed with #209, so this is mostly wiring. Also directly
  useful for B and C — LoCo and CICADA are 97% of the sweep's wall clock
  (fit seconds: sync 0.06, coact 0.08, rate 0.10, SCE 0.17, **LoCo 2.69, CICADA
  7.06**), so being able to sweep a subset is what makes iterating on grids bearable.
- **8 · assess the whole folder.** A port, not a design — `bugarach assess
  <folder>` exists in Python with the three rules already encoded. **117 s for 84
  recordings** at the default thousand surrogates — measured 2026-08-23 on
  `2026-08-18_revised_2v_periods`, and 39 s on `2026-08-20_pensub_revised_2v`.
  The `~15 s` this line carried was wrong by 8x and was being quoted elsewhere as
  a budget. The CLI now prints per-recording progress with an estimate of what is
  left, which is the floor of what two minutes of silence needs; a browser-side
  version still needs its own.
- **4 · the region selector.** Needs Tony. The panel does two jobs with one menu.
- **3b · K as count or share of the field.** Needs Tony. Recommendation is to show
  both and keep the scan in counts.

### F · Three standing items, unchanged

- **The scoreboard's copy has not been reviewed**, so the panel is gated off the
  published page. One line to un-hide, after the review.
  `docs/todo/2026-08-20-the-scoreboard-copy-needs-review.md`.
- **Nothing publishes the site.** It was three features stale when this session
  started. A staleness check that only *reports* needs no credentials and is the
  cheap honest option.
  `docs/todo/2026-08-20-nothing-publishes-the-site-so-it-goes-stale.md`.
- **`port` means two things in the detector docstrings**, and it undersells five
  of six to an outside reader.
  `docs/todo/2026-08-21-port-means-two-things-in-the-detector-docstrings.md`.

---

## What must not happen in the revision

Three things this repo has already paid for, restated because a re-calibration is
exactly when they get done again.

**Do not raise `min_rois` until the false alarms go away.** FOUNDATIONS §9. A
nonzero coactivity excess on TTX slices is evidence about the preparation, not a
false-alarm floor to tune out. A session proposed exactly this on 2026-08-13,
reasoning from the textbook prior rather than from this project's data.

**Do not let a detector choose its own operating point on the data it is then
scored on.** The held-out fold split exists for this, and `pickOperatingPoint`
refusing a boundary answer is part of it — the refusals in item 3 are the
mechanism working, not a bug to route around by accepting the boundary value.

**Do not read the tie at the top as a win.** `bakeoff.md` has the tube at
0.668 ± 0.061 and CoactDetect at 0.651 ± 0.044, one training run per fold, so no
seed error bars exist to test the difference with. A revision that improves the
hand-written detectors makes that comparison *tighter*, not looser.
