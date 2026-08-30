# The ranking rule

> **Provenance.** Every number in §1–§7 is one of two things, and each is marked.
> **Re-derived here** means this document's author recomputed it from
> `docs/learned/bakeoff.json` and the code, and the command is in §9.
> **Inherited ⚠** means it comes from
> [the ranking brief](handoffs/2026-08-30-ranking-the-detectors.md), was produced by
> the session that wrote that brief, and has **not** been recomputed here. Nothing
> below is unsourced, and nothing inherited is presented as though it were checked.

## 1. The problem: the winner changes when you change the seeds

Run the background-activity sweep on seeds 1–12 and CoactDetect wins every one of
the seven grid points. Run the same code, the same grid, on seeds 13–24 and **LoCo
takes the busy half.** ⚠ *inherited*

That is not a close result. It is the absence of a result, and it means **any
scheme obliged to emit a strict order will emit a different strict order next
week.**

The project already draws the reason:

![Panel A of the fair bake-off: mean F1 per detector as bars, with each held-out fold drawn as a dot on top. The four leftmost detectors have means spanning 0.638 to 0.681 and fold clouds that overlap almost completely.](learned/bakeoff.png)

*Panel A — every fold drawn on top of its mean. The four leading detectors span
0.043 in mean F1 and their fold clouds overlap almost entirely. Panel B is the cost
plane and is not what this document argues from. Note that the bars descend
left-to-right: the figure invites exactly the ordering this rule declines to make.
Re-derived — every bar matches the per-fold means in `bakeoff.json`.*

Read off that panel — all **re-derived**:

| comparison | mean F1 | the spread underneath it |
|---|---|---|
| center−surround (learned) vs CoactDetect | 0.681 vs 0.651 | folds span 0.629–0.744 and 0.606–0.711 — overlapping |
| CoactDetect vs LoCo | 0.651 vs 0.638 | inside each other's spread; CoactDetect takes 3 of 4 folds |

**So there is a rule, and its output is tiers.** Two detectors share a tier unless
one wins by more than a seed change can manufacture. *"CoactDetect and LoCo are
tier 1"* is a legitimate finding, and it is the one that survives.

Tony asked for it in those terms: *"lets figure out a solid foundation for ranking
the detectors, assuming that another data set might completely destroy what we
decide."*

## 2. The design: the rule and the result live apart

This document is the **rule** — what makes one detector better, decided once. The
**result** is what the rule returns when pointed at a particular set of scores, and
it is expected to change. Another lab's recordings can overturn every result here
without altering a line of this page, and that is the only form of robustness the
question admits.

Implemented in [`bugarach.rank`](../src/bugarach/rank.py). The decisions below are
that module's source of authority, not the other way round.

Every measure is sorted by what it **requires**, not by what it means:

| | measure | ranks | needs planted truth |
|---|---|---|---|
| **Score** | F1, paired by fold | **yes** | yes |
| **Gate** | promiscuity probe — firings/min into a block with nothing planted | no — disqualifies | **no** |
| **Gate** | detection throughput, as a multiple of realtime | no — disqualifies | no |
| **Gate** | distractor rate — *specified, disarmed, §6* | no | yes |
| **Tiebreak** | promiscuity probe, *within* a settled tier | ordering only | no |
| **Report** | recall by participation level, false alarms, raw timing | no | mixed |

A **gate encodes a requirement** and survives a change of data set. A **weight
encodes a preference**, and a preference about how much one failure matters against
another is a scientific claim this project has no measurement to support. So the
scored part is kept to one number and everything else either disqualifies or
informs.

The payoff is the last column. Point this rule at recordings with no coordination
ground truth and the probe and throughput gates still work — and you know which
half you lost rather than discovering it in the numbers.

**A fold** is one held-out block of recording seeds. Every detector is scored on the
same folds, which is what makes the comparisons below *paired*.

## 3. What ranks, and what only reports

*Decision D1.*

**F1 alone ranks.** Ranking on everything is a weighted sum wearing a disguise, and
the weights would be the claim.

The narrowness is load-bearing: one number is what lets the tie test in §5 be stated
precisely enough to check. A composite score would need its own noise floor
established before anyone could say what a tie was, and nothing here has measured
one.

## 4. The promiscuity probe gates, and breaks ties

*Decision D2. This also settles the standing question of how two scoring rules live
in the tree and pick opposite winners.*

The **promiscuity probe** is a stretch of recording with an elevated event rate and
**nothing planted in it**. A detector keying on rate rather than on coordination
lights it up.

**It does not enter F1.** Fold it in and the headline stops measuring the detector
and starts measuring how hard the probe was set — the project's own cautionary
number is a detector reading F1 0.09 one way against 0.68 the other, on 599
probe-block detections out of 601 false alarms. *Re-derived: quoted in
`bench.MAX_PROBE_PER_MIN`'s docstring.*

**It gates instead, at the ceilings the calibration already uses**, so a setting
refused when it is chosen is also refused when it is ranked.

**Why pass/fail alone is not enough: precision is blind to it.** On the bench the
brief measured, CoactDetect and center−surround have near-identical precision — 0.572
against 0.543 — and differ by **17×** in how often they fire into the empty block:
1.25 firings a minute against 20.5.
⚠ *inherited, and measured on `BENCH_RECORDING`, not on the bake-off —
the bake-off's own probe rates in §5 are smaller numbers from a different recording
spec and the two must not be read against each other.* Across twelve detectors the
correlation between precision and probe rate is only −0.32 ⚠, so this is a property
of the measure rather than a quirk of one pair.

The mechanism is not subtle: precision is a *ratio measured on data containing
events*, so a trigger-happy detector harvests true positives that dilute its false
ones. Remove the events and there is nothing left to dilute with.

**So inside a tier — where by construction nobody has won — the lower probe rate is
listed first.** It never moves the headline number and never crosses a tier
boundary.

**The objection, and the answer.** A tiebreak on "fires least into nothing" looks
like it rewards a detector for never firing, and one detector's 0.0 genuinely cannot
be distinguished from silence by this measurement ⚠. It is not a problem, because
the tiebreak runs only *inside* a tier and reaching a tier requires having earned the
F1 that put it there. Silence is filtered by the ranking before the tiebreak is
consulted. That ordering is asserted in the tests, because it is the whole of the
answer.

**What the probe actually measures — the name is wrong.** The block is not empty: it
carries 591 spikes across 33 ROIs in five minutes, each ROI drawn independently, and
independent draws still coincide. Within the planted jitter ⚠ *inherited throughout
this table*:

| ROIs coinciding | times per minute, by chance alone |
|---|---|
| 3 — the participation floor | **12.4** |
| 4 | 2.97 |
| 5 | 0.57 |
| 6 — the median planted event | **0.10** |
| 7 | 0.02 |
| 8 or more | **0.00** |

About four times rarer per additional ROI. **A detector firing on a three-ROI cluster
there is detecting something real.** What the probe measures is not "fires at
nothing" but *calls a chance coincidence coordination* — the same failure the
distractor axis is meant to measure deliberately, arrived at by accident. Reading
each detector's probe rate back across that curve implies the cluster size it is
consistent with, but that read-across is an **inference, not a measurement**: these
detectors threshold their own statistic, they do not count ROIs in a window.

## 5. What counts as a tie

*Decision D4.*

> **`A` beats `B` only if `A` wins a majority of the paired folds *and* leads by more
> than 0.02 in mean F1.** Anything else is a tie and they share a tier. Below twelve
> distinct seeds the rule refuses to answer at all.

Both conjuncts do independent work, and the shipped bake-off demonstrates each
catching what the other misses — all three rows **re-derived**:

| comparison | folds won | mean-F1 margin | verdict |
|---|---|---|---|
| center−surround over CoactDetect | **2 of 4** | +0.030 — clears | **tie**, blocked by the pairing |
| CoactDetect over LoCo | 3 of 4 — clears | **+0.013** | **tie**, blocked by the margin |
| locust over `tube_ratio` | 3 of 4 | +0.039 | a win |

Either half alone would have crowned a winner in one of the first two rows.

**The pairing** is information a marginal mean throws away. Every detector runs the
same folds and seeds, so "won three of four" is free — and writing it as
`0.651 ± 0.044` against `0.638 ± 0.053` discards it and makes the comparison look
like a coin flip.

**The margin** is the bench's noise floor, comfortably above the 0.0011 ⚠ that
separated two detectors at one end of the background grid — a gap that reversed when
the seed block changed.

**The margin is also what makes tiers exist**, which was not the reason for choosing
it and is the better reason for keeping it. Because beating requires a mean-F1 lead,
a cycle `A > B > C > A` would need `0 > 3 × 0.02`. The relation is therefore acyclic
and the tier decomposition always terminates. **Majority alone is not**: a rule
comparing only fold wins admits Condorcet cycles — three detectors each beating the
next, going round — which appear in about **3%** of random triples. *Re-derived:
6,118 cycles in 200,000 random triples; the property is also asserted by search in
the tests.* Such a rule must break the cycle arbitrarily and then calls the result a
ranking. That is why "margin only" and "majority only" were both rejected.

*The Condorcet paradox is Marquis de Condorcet's, 1785; the term is used here in its
standard sense and nothing about it is claimed as new.*

**The seed floor refuses rather than warns.** Twelve is the count this bench's own
author reached for after calling three noise-dominated ⚠ — and three is still live in
the background-curve tests, inherited by two other probes whose headline win counts
are three-seed comparisons with no spread reported ⚠. A rule that only warned would
be read by whoever happened to be watching stderr, after the ordering it qualified had
been published. This is the argument the project already made for refusing to load
data without a sampling interval (FOUNDATIONS §6), applied one layer up.

**The honest consequence: the rule refuses the shipped bake-off.** That run covers
eight seeds in four folds — below the floor. *Re-derived, and asserted as a test.* A
re-run at twenty-four seeds, twelve on each side of the block boundary, is what the
rule asks for next.

## 6. The distractor axis is specified, and switched off

*Decision D3 — the one place the decision could not be implemented as made.*

A **distractor** is a planted correlated burst: genuine cross-ROI coincidence that is
not a coordinated event. It is the most scientifically meaningful false positive this
bench measures — firing on a real burst is wrong in a far more interesting way than
firing on noise — and *"should a burst count?"* has been open since the scoring module
was written. The ruling was that it gets its own gated axis, out of F1.

**The gate is wired and disarmed, because the number does not mean what its name
says.** One detector makes **two detections in an entire fold**, matches a planted
event with both — precision 1.000 that fold — and is scored as hitting **twelve of
twelve** distractors. *Re-derived.* Two detections cannot land near twelve separate
times.

What is computed is *how many distractors are covered by the union of the detection
spans*. So it scales with span width rather than with firing; it has no opportunity
denominator; and, unlike the probe count computed twenty lines above it in the same
function, it is not restricted to unmatched detections — so a detection that correctly
found a real event is charged as a distractor hit as well.

Normalise it and every detector in the tree fires on distractors *more often* than on
real events. Read naively that says none of these methods can tell coordination from a
burst — a large claim, and not one this measure can support, because the wide spans
inflating it are the same spans the recall column is scored on.

So the axis reports and does not gate. Arming it means repairing the measure, which
changes published numbers and belongs to whoever owns that repair —
[the defect, with its evidence](todo/2026-08-30-distractor-hits-counts-coverage-not-firing.md).
The threshold sits in the code as `None` with that page named beside it.

## 7. Platform-dependent measures gate and never rank

*Decision D5.*

Detection and calibration times move with hardware and thread count, and the learned
models' shipped numbers were produced on one platform. **A detector is not better
science for having run on a faster machine.** One that cannot keep up with acquisition
is genuinely unusable, so normalised throughput gates at realtime and the raw seconds
are reported next to the platform that produced them.

## 8. What this does not do, and what is not yet tested

- **⚠ The central claim is untested.** *"The tiers hold even though the argmax
  flips"* is the design's whole promise and **nothing has run it**. It needs the
  bake-off at twenty-four seeds, tiered on each block, with the two tierings
  compared. Until then the rule is argued, not demonstrated.
- **It does not re-baseline the background-curve tests.** Those asserts encode a
  claim — that an F1 cannot be quoted without saying what background it was measured
  at — and were left red deliberately. Flipping them to today's numbers would publish
  the opposite scientific position silently.
- **It does not fix the calibration loop.** The bake-off picks each fold's knob by
  raw argmax with no probe gate, so rate+context ships a setting firing at 3.3, 3.5,
  3.8 and 3.3 a minute against its own 2.0 ceiling — **four folds of four**
  *(re-derived)*. The ranking refuses it on the way in, which is a symptom; the cure
  changes published numbers and is its own change.
- **It declares no probe ceilings for the learned models.** They have no entries in
  the ceiling table, so they are ungated on that axis — center−surround fires at 2.05
  a minute *(re-derived)*, over the 2.0 ceiling the most comparable hand-written
  detector is held to. Setting them is a measurement, not a default.
- **It does not rank on the participation breakdown.** Recall at three participation
  levels is a *vector*, and collapsing it to one number is another weighted sum in
  disguise. A detector that only finds large events is a different instrument from one
  that finds small ones, and tiers ought to be able to say so; how remains open.

## 9. Reproducing what is quoted here

```
# tiers, gates, and the refusal, from the shipped bake-off
python -c "from bugarach.rank import *; \
  print(rank(fold_scores_from_bakeoff('docs/learned/bakeoff.json'), min_seeds=8).table())"

# the paired per-fold F1 the tie rule reads
docs/learned/bakeoff.json -> hand_written[name]["per_fold"], learned[name]["per_fold"]

# Panel A above
python tools/make_bakeoff_figures.py --bakeoff docs/learned/bakeoff.json --out docs/learned

# the background axis, both seed blocks  (INHERITED — not run for this document)
evaluate_background_curve(name, "baseline_quiet", tuple(range(1, 13)))
evaluate_background_curve(name, "baseline_quiet", tuple(range(13, 25)))
```

Run pytest with `PYTHONPATH=$PWD/src` from a worktree, or it tests the primary
checkout's sources and fails toward green.
