# The conditioned run — the standard pipeline when the cohort has structure

> **Working material, not murderboarded.** Same standing as [`pipeline.md`](pipeline.md)
> and [`run_records.md`](run_records.md): for sessions in this tree and for Tony. If any of
> it reaches an outside reader, murderboard that artifact first.

[`pipeline.md`](pipeline.md) is the loop: open a folder → MAHICE → derive the spec →
simulate and validate → tune → test on a fresh batch → detect → output. **That page is
still the authority on what each step owns.** This one describes what changes when the
cohort is not one undifferentiated population — when it has **two streams, four
experimental groups and two treatments**, and the detectors have to hold across all of
them.

**Why it exists.** The 2026-09-09 run took the loop at face value: it pooled every
baseline into one median per generator quantity, simulated 72 recordings that all shared
those parameters, and calibrated one operating point at the centre of a distribution it
never sampled. The murderboard on its report found the consequence in three independent
places, and Tony's own reading found the rest: *"the detectors need to fare well under all
these conditions."* A calibration fitted at the centre has not been asked to.

**The conditioning axes, and they multiply.**

| axis | values | binds |
|---|---|---|
| stream | fast, slow | different measurements; **never pooled** (GLOSSARY) |
| group | DI, MALE, ORX, OVX | effects run in **opposite directions** by group (FOUNDATIONS §9) |
| treatment arm | TTX, senktide | the contrast the run exists to support |
| field size | 9–61 ROIs | a coactivity null scales with the number of cells |

---

## What the cohort actually offers

Counted from the producer's `STEPS_EXCLUDED` split, 2026-09-09. **Baselines available to
the assessor**, which is the only region the generator may be fitted from (FOUNDATIONS §9):

| | senktide | TTX | total |
|---|---|---|---|
| DI | 6 | 11 | 17 |
| MALE | **5** | 9 | 14 |
| ORX | 10 | 9 | 19 |
| OVX | 8 | 9 | 17 |
| **total** | 29 | 38 | **67** |

The limiting cell is MALE/senktide at 5, so a strictly balanced design is **5 × 8 = 40
recordings** and discards 27. The parent export holds 84 baselines; the other 17 belong to
recordings whose first treatment is neither arm.

---

## Analysis regions

Tony's definition, 2026-09-09:

- **baseline** — 20 minutes maximum, 15 minutes minimum, measured **backward from the end
  of the baseline period**.
- **treatment** — 15 to 20 minutes, starting **2 minutes after the baseline period ends**,
  the delay being solution exchange.

**What the shipped folder actually carries.** The producer's `analysis_start_sec` /
`analysis_end_sec` (the `long_window_20` regime) mostly comply, and two windows do not:

| | n | median | range |
|---|---|---|---|
| senktide baseline | 29 | 20.0 min | 19.0–20.0 |
| senktide treatment | 29 | 20.0 min | **14.9**–20.0 |
| TTX baseline | 38 | 20.0 min | 17.0–20.0 |
| TTX treatment | 38 | 20.0 min | **13.0**–20.0 |

`20250912_227` (ORX, senktide) at 14.9 min and `20241211_127` (MALE, TTX) at 13.0 min sit
below the 15-minute floor. **That is a conversation with the producer, not a filter here** —
CLAUDE.md's rule that the export folder is the input, and that which recordings are
analysable is the producer's call, has already cost this project one real error.

⚠ **Unequal windows are not cosmetic.** The degenerate control models emit exactly one span
per analysis window, so their before/after ratio *is* the window-length ratio. On the
2026-09-09 run that ratio moved on 12 of 38 TTX recordings, one by 54%, and it was how the
review caught a false sentence in the report. Any run whose windows are unequal must say so
and must not attribute the control's movement to tissue.

⚠ **The three-delta window interface is browser-only.** `pipeline.md` records this as the
first place the two modes diverge: the browser can define windows from the three deltas,
the Python library cannot. So a run that needs windows recomputed to the definition above,
rather than taken from the producer, **cannot be driven from the command line today**.

---

## The stages, and what changes at each

### Assess — balanced across cells, and per stream

The assessor measures coordination without a detector, on **baseline regions only**. Two
changes from the pooled default:

1. **Equal influence per cell.** Compute each generator quantity per (group × arm) cell,
   then combine the eight cell values with equal weight. **Prefer weighting to
   subsampling** — subsampling to 40 throws away 27 recordings and makes the spec depend on
   a draw. The rows already carry `group_id` and `mouse_id` through the loader's `meta`, so
   no new join is needed.
2. **Both streams.** Every row of the 2026-09-09 assessment reads `stream: fast`, so the
   generator, every operating point and all 72 simulated recordings were fast-derived and
   then applied to slow — which carries the larger treatment effect. A conditioned run
   assesses both streams or states that it did not.

⚠ **Recordings are not independent.** 29 senktide recordings come from 18 mice, 38 TTX from
23; eleven mice contribute two slices and two contribute three. Any median or count over
recordings inherits that nesting, and nothing in the toolchain accounts for it today.

### Derive the spec — a distribution, not a point

The generator is set from **rate, cluster, participation and jitter** (`pipeline.md`). The
conditioned form keeps those four and changes how they are carried:

- **`n_roi` varies per simulated recording**, drawn from the observed field-size
  distribution rather than fixed at one median. This is the single largest lever. A
  coactivity detector's null scales with the number of cells, so an operating point chosen
  at 32 ROIs is not the one that holds at 10 or 61 — and because **K is a percentage**, it
  resolves to a different absolute count at each field size, which is exactly the property
  the run is meant to respect.
- **One parameter block per cell**, so the simulated corpus spans the real between-group
  spread instead of averaging it away.
- **K as a percentage with a floor**, recorded per recording along with whether the floor
  bound. On this cohort at 10% floored at 3 the floor binds on 26 of 84, so two rules govern
  one population and a number pooled over them came from both.

⚠ **A K given as a percentage puts each recording in the assessment exactly once, at its own
resolved count.** Anything that aggregates by filtering to one K therefore selects a
subpopulation — and it selects the small fields. That defect shipped on 2026-09-09 and made
the generator describe the smallest 55 of 84 recordings; it is fixed in `assess_archive.py`
and `derive_spec.py`, and it is the failure mode to check first in any new aggregation.

### Simulate — sample the conditions

Build the simulated data set by drawing equally from the eight cells, each recording taking
its cell's parameters and its own `n_roi`. Same total recordings, so essentially the same
runtime as the pooled form.

### Tune and test — score per cell, not only pooled

- Calibrate on a fold, score on a held-out fold, as now.
- **Report F1 per cell as well as pooled.** This is the simulation-side analogue of the
  group facets: the pooled number cannot say *which* condition a detector fails in.
- **The promiscuity gate is not currently in this path.** `fair_bakeoff` picks each fold's
  knob by raw F1 argmax and never calls `bench.pick_operating_point`, so `TooPromiscuous`
  and `EdgeOfRange` are both inert; `settings_from_bakeoff` adds only fold-agreement and
  grid-edge checks. On 2026-09-09 SPIKE-synch's selected knob sat over its own declared
  ceiling in five of six folds and was refused for an unrelated reason. **A conditioned run
  either wires the gate in or says plainly that it is not wired in** — the 2026-09-09 report
  claimed the gate as a safeguard and that claim was false.
- **Operating-point stability is necessary, not sufficient.** The two deliberately-poor
  control models select the same threshold in every fold, because a detector that emits one
  span per window regardless of input is maximally stable. Any use of stability as a
  criterion must say so.

### Robustness to treatment, without training on it

FOUNDATIONS §9 forbids taking **the properties of coordination** from senktide or TTX. It
does not forbid knowing how far the **marginal rate** moves under them, and the distinction
is what makes robustness reachable without violating the rule:

- **Admissible:** measure the per-ROI event-rate shift in treatment windows and widen the
  simulated background axis to span it, so an operating point is chosen to hold *across* the
  range rather than at baseline's centre. The bench already carries a background grid.
- **Not admissible:** fitting participation, jitter, cluster rate or span from a treatment
  window.

⚠ **The control this project does not yet run.** Rate-matched surrogates of the *treatment*
windows — per-ROI rates preserved, cross-ROI structure destroyed — through the same
detectors. The ratio must go to 1. That is a null, not training, and it is the only thing
that separates *coordination changed* from *an instrument calibrated on baseline statistics
responding to a marginal-rate change*. It matters most for `rate+context`, which uses an
absolute threshold fitted in the baseline regime and shows one of the largest fast-stream
effects.

### Detect and output

Detect at the calibration, with the trained models, on each arm's folder. Then:

- **One page per detector per treatment, groups in facets, streams as rows.** Y shared
  across the group facets of one stream and nowhere else.
- **Say what the pages do not draw.** On 2026-09-09 the figures covered periods 1 and 2 only,
  while 17% of senktide and 28% of TTX calls fell in later declared periods, and nothing
  said so.
- **No pooled across-group treatment number.** FOUNDATIONS §9: a pooled figure hides sign
  changes and is not admissible on its own. On this cohort the pooled TTX slow ratio is
  carried by the MALE facet, reverses in DI, and is undefined in ORX and OVX where the
  median baseline is exactly zero.
- **Name the statistic.** A ratio of medians and a median of per-recording ratios are
  different numbers and disagree here about which detectors rise. State which, and state how
  many recordings per cell have a zero baseline.

---

## What a session must ask before running this autonomously

**These are blocking.** Each changes what gets built, and no default is safe.

1. **Balance by weighting or by subsampling?** Weighting keeps all 67 and gives every cell
   equal influence; subsampling gives a strictly balanced 40 and discards 27. *Recommended:
   weight.*
2. **Which analysis windows?** Take the producer's shipped `long_window_20` as-is, or
   recompute to the 15–20 / +2 min definition above. Recomputing needs the three-delta
   interface in Python, which does not exist — so this may be a build, or a request to
   interface2 for a re-export.
3. **The two recordings under the 15-minute floor** — keep, exclude, or ask the producer?
   The standing rule says the producer decides what is analysable, which points at asking.
4. **Stratification granularity.** Eight cells (group × arm, n = 5–11) fits parameters on
   very few recordings each. Four cells (group), two (arm), or eight? This is a judgement
   about how much structure the data can support, and it is Tony's about his own data.
5. **One operating point or several?** If detectors genuinely behave differently across
   field size, group or stream, does the run ship a single setting chosen to hold across the
   range, or conditional settings? This changes what a calibration *is* and what the
   settings file has to carry.
6. **Assess and bench the slow stream?** It roughly doubles the assessment and the bake-off.
   Slow carries the larger treatment effect and currently has neither.
7. **Is K the same percentage for both streams?** K is set by a person during MAHICE and the
   assessor has run one stream to date.
8. **MAHICE — before or after?** It has never been run on an approved folder. Until it is,
   `RESET.md` §1 applies to everything downstream: a coordination number nobody looked at is
   not a result. Every artifact this pipeline produces inherits that.

**These I will default and flag**, unless told otherwise:

- `n_roi` drawn per recording from the empirical distribution, not a fitted parametric one.
- Fold and seed counts held at the previous run's 6 × 12 unless a corrected pairwise winner
  is wanted, which needs **eight folds at twelve seeds — 96 recordings, not a finer cut of
  72**.
- The treatment-surrogate null specified but not run until the design is agreed.
- No ranking published; the spread and the per-cell table reported instead.

---

## Related

[`pipeline.md`](pipeline.md) — the loop and what each step owns ·
[`performance_table.md`](performance_table.md) — why no ranking, and the accepted route if
one is ever wanted · [`FOUNDATIONS.md`](FOUNDATIONS.md) §9 — what the preparation constrains ·
[`RESET.md`](RESET.md) §1 — why an unreviewed K is not a result ·
[`export_folder_spec.md`](export_folder_spec.md) — what a folder may contain ·
[`handoffs/2026-09-09-the-full-cohort-through-the-loop.md`](handoffs/2026-09-09-the-full-cohort-through-the-loop.md)
— the run that motivated this page.
