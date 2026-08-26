---
status: open
filed: 2026-08-25
---

# CFAR and its variants belong on a knob axis, not in the detector list

> **Not murderboarded** — a planning note for sessions in this tree, same standing as
> [`the four variants`](2026-08-23-four-variants-of-the-tube.md). Every claim is quoted
> from a named file or a line of source. **If any of it reaches an outside reader,
> murderboard that artifact first.**

**Tony asked** (2026-08-25) whether CFAR and its variants should be added to the detector
list, and then ruled on the answer below: *"these are all valuable additions that need to
be prioritized after the full pipeline is viable."* So this is a **deferred yes to the
work and a no to the shape** — the additions are wanted, they are not new entries in
`DETECTORS`, and none of them starts before the revision plan's phases run end to end.

## The answer to the question as asked

`DETECTORS = ("rate", "coact", "loco", "sce", "cicada", "sync")`
([`detect_folder.py`](../../src/bugarach/detect_folder.py)) lists things that take
multi-ROI event trains and return coordinated events with onsets, widths and participant
counts. CA, GO, SO, OS and trimmed-mean are **rules for setting a bar over a 1-D signal**.
Registering `ca_cfar` there requires first choosing which statistic it thresholds — rate,
coactivity, the SCE signal — and at that moment it has become a variant of an existing
detector. There is no seventh detector in the CFAR family; there are five ways to
threshold the three we already have.

Three reasons the registry is the wrong home, each with its source:

**1 · The variants are already in the tree under other names.**
[`the CFAR bench`](../reviews/cfar_demo_2026-08-24.md) settled this: LoCo in `maxlt` is
greatest-of selection over an order-statistic reference — GO and OS at once, arrived at
here independently, with its own docstring giving greatest-of's reason. `rate+context`
under `threshold_mode="multiplicative"` **is** a cell-averaging CFAR, and *"the only thing
between it and being one by default is a calibration."* CoactDetect is cell-averaging in
shape with the self-masking built in. Binned SCE and locust are pre-CFAR fixed bars;
SPIKE-synch has no bar at all.

**And the knobs exist.** `loco_detect` carries `null_context_mode` — `"maxlt"` is
greatest-of, `"symmetric"` is cell-averaging — and `guard_sec`; `rate_detect` carries
`threshold_mode` / `threshold_alpha`; all three rolling detectors carry `guard_sec`
(`loco.py:333`, `rate.py:178`, `coact.py:79`). The CFAR design space is already
parameterised. What is missing is not code, it is a reason to prefer one point in it.

**2 · Five new detectors are five new tuned constants, and the scoring rule is in
dispute.** [`two scorers, two winners`](2026-08-25-two-scorers-two-winners-and-nothing-decides.md)
found `BenchResult.precision` and `probe_rate_mechanism` disagree about what counts as a
false positive — multiplicative wins 1 of 7 background points with the probe excluded and
5 of 7 with it included, same runs, same seeds, same grids. Adding detectors before that
is settled means selecting five operating points against a score two tools compute
differently, and whichever campaign ran first would look authoritative.

**3 · The bench they would be scored on is the one already flagged for revision.**
`BENCH_RECORDING` still runs a flat field, and
[`revise the bench`](2026-08-23-revise-the-bench-recording-before-the-refit.md) names the
larger problem: it plants no assemblies. Five more detectors measured there inherit both.

## What to add instead, in the order the tree's own findings support

### A · A design false-alarm probability — do this one regardless

[`the CFAR bench`](../reviews/cfar_demo_2026-08-24.md) calls it *"the highest-value import
from radar, above any architecture"*, and `detector_history.md` §5.3 is titled *"Nobody
here has stated a design false-alarm probability."* It is the scoring rule under which a
hand-written detector and the tube can be compared honestly: fix P<sub>fa</sub>, measure
achieved P<sub>fa</sub> on the deployment distribution, compare recall at matched false
alarms. It also dissolves reason 2 above, because a stated design rate is a claim the
promiscuity probe can falsify — which is what
[`the probe cannot fail`](2026-08-16-promiscuity-probe-cannot-fail.md) has been asking for
since 2026-08-16.

Read the [loco/coact murderboard](../reviews/loco_coact_as_cfar_2026-08-25.md) before
writing the word "promise" anywhere near it. CoactDetect's `alpha` looks like a design
point and is a swept knob (`bench.py`, `grid=(1e-2 … 1e-7)`), and on bins where the
surrogate standard deviation is zero `coact.py` sets `pval = 0.0` and the bin fires
regardless of it. The gap between design and achieved is the diagnostic; today neither
number exists.

### B · Censoring inside `maxlt` — the one the plan already endorses

Order-statistic or trimmed-mean over the reference, dropping the largest samples wherever
they sit. This is the remedy the primaries prescribe for a multiple-target environment,
and nobody here has run it on anything.
[`censoring is the instrument the guard was not`](2026-08-23-censoring-is-the-instrument-the-guard-was-not.md)
owns it and carries the control that can tell.

**Read that file before starting**: the guard interval was written up as a success and
then retracted, and the reason was the measurement rule rather than the mechanism. Report
**crowded-band gain minus control-band gain, never F1** — a gain flat across
nearest-neighbour gap is a threshold shift wearing a mechanism's clothes.

### C · Variability-index selection on LoCo — wanted, and contested

Test the two half-contexts for homogeneity and choose symmetric or maxlt **per anchor**
instead of shipping `maxlt` unconditionally.
[`the CFAR bench`](../reviews/cfar_demo_2026-08-24.md) names it *"the cheapest real
upgrade, and it involves no learning at all"*, and `detector_history.md` §5.4 establishes
that the estimator and the combination rule are separable, so it is a third value of
`null_context_mode` rather than a module. The measured cost of the unconditional choice:
greatest-of holds 1.12× design through a clutter edge where cell-averaging reads 2.03× —
and comes **last** with two targets in one window, 45.7% detection against SO's 73.2%.
*Best at an edge and worst against a neighbour, for the same reason.*

**It sits below B because the revision plan argues against it, and that argument is
good.** Item 12 of [`the revision plan`](2026-08-22-the-revision-plan-mechanism-before-calibration.md)
— *"Do not change LoCo's combination rule"* — reasons that bugarach's dominant
nonhomogeneity is the drug-onset rate transition, which is an edge, which is exactly where
greatest-of wins; Hansen & Sawyers price the split at *"0.1 to 0.3 dB"*, so it is nearly
free; and *"the fix for its multiple-target blind spot is censoring inside it, not
replacing it."*

**VI selection is not the replacement item 12 rules out** — it keeps maxlt wherever the
window looks like an edge — but item 12's premise still binds it: if the edge case is
dominant, a conditional switch buys little and adds a classifier that can be wrong. So C
is a **measurement before it is a change**, and the thing it must show is a gain
concentrated where the two half-contexts disagree. If B lands first and works, C may have
nothing left to buy.

### D · The tube's V2 and V3 — the same two ideas one layer down

Already scoped in [`the four variants`](2026-08-23-four-variants-of-the-tube.md); listed
here only so nobody builds the CFAR axis twice. `build_tube` **subtracts where CFAR
divides**, which cancels the mean of a rate change and not its variance — and it fires
15.75 times in a probe block containing nothing, against LoCo's 2.50.

## The one item that would be a genuinely new detector

The [loco/coact murderboard](../reviews/loco_coact_as_cfar_2026-08-25.md) found the
departure that matters more than any CA-vs-GO-vs-SO choice: **LoCo's reference does not
slide with the cell under test.** It quantizes to anchors every 15 s and assigns each bin
its nearest one, so a bin can be judged by a window centred up to 7.5 s away on FAST and
15 s on SLOW. *"CFAR's defining property is that the reference slides with the cell under
test."* A sliding, guarded, multiplicative-bar coordination detector is not a knob on LoCo
— it is a new thing, and it is the only entry in this file that would ever earn a row in
`DETECTORS`. Scope it as such, and cost the compute before agreeing to it: the anchor grid
is presumably what makes LoCo affordable.

## The gate Tony set, in the tree's own terms

*After the full pipeline is viable.* In the plan that is on `main` today — the phases of
[`the revision plan`](2026-08-22-the-revision-plan-mechanism-before-calibration.md) — A
belongs with **Phase 2** (*"the promiscuity probe must be able to fail before C"*), and B,
C and D are **Phase 1** mechanism work whose payoff is only visible after the **Phase 4**
re-fit. None of it is worth starting while the bench is flat and the scorer is forked,
because everything measured now gets measured again afterwards.

**A step exists in front of all of them that is not yet on `main`.** `docs/RESET.md` is in
flight on branch `the-reset` and inserts a step 0 before the plan's Phase 0: *the assessor
becomes a pair* that records the decision and the view beside the data set it produced,
because *"nothing downstream is reproducible until this exists."* If that document lands,
the gate in this file means after **its** §7 sequence, not the revision plan's alone. A
session picking this up should check which of the two is canonical before quoting a phase
number.

Two exceptions worth arguing for when the time comes, not now:

- **A is a scoring rule, not a mechanism change.** If the null test is being built anyway,
  stating a design P<sub>fa</sub> alongside it is nearly free, and it makes every later
  comparison in this file honest.
- **B and C ship no default.** Both can run as a sweep that changes nothing, which is what
  [`the four variants`](2026-08-23-four-variants-of-the-tube.md) means by *"seeds before
  conclusions"* — one training run per fold against a fold spread of 0.061 demonstrates
  nothing, and the same discipline applies to a hand-written knob.

## Two things not to re-derive

- **The parity constraint on mechanism changes has been retired, and the file saying so is
  not on `main` yet.** [`the revision plan`](2026-08-22-the-revision-plan-mechanism-before-calibration.md)
  still reads *"every mechanism change lands as an additive option, defaulting to the
  current behaviour"*, and that is what makes this question askable at all — but Tony
  accepted ADR-0003 on 2026-08-25 (*"we should no longer be concerned about matching their
  output"*), in flight on branch `parity-was-the-inheritance`. Either way it lifted a
  constraint on **changing** the six and supplied no reason to **add** five more.
- **The radar attributions in the CFAR bench are explicitly unretrieved.** Variability
  index (*Smith & Varshney*), clutter maps (*Nitzberg*), the multichannel work (*Kelly*,
  *Reed–Mallett–Brennan*) are named there as starting points for a literature pass and
  marked unverified. None may reach a document without the primary in hand — and
  [`the methods are not ours`](2026-08-24-the-methods-are-not-ours-and-the-app-says-otherwise.md)
  is the ruling on how to phrase it: cite the origins, say plainly that we arrived
  independently, stop there.
