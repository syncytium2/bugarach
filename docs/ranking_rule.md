# The ranking rule

**The rule and the result live apart.** This document is the rule: what makes one
detector better than another, decided once. The result — which detector is
actually better — is regenerated whenever the data set changes, and is expected to
change. Another lab's recordings can overturn every result here without altering a
line of this page, and that is the only form of robustness the question admits.

Tony asked for it in those terms: *"lets figure out a solid foundation for ranking
the detectors, assuming that another data set might completely destroy what we
decide."*

Implemented in [`bugarach.rank`](../src/bugarach/rank.py); the decisions below are
its docstrings' source of authority, not the other way round.

---

## 1. Why there is a rule at all

A ranking rule is worth writing only if the obvious thing fails. It does.

**F1 does not separate the detectors it is being used to separate.** Three
measurements say so, and the third is decisive:

| comparison | mean F1 | what the spread does |
|---|---|---|
| learned `tube` vs `coact` | 0.681 vs 0.651 | fold ranges 0.63–0.74 and 0.61–0.71, overlapping |
| `coact` vs `loco` | 0.651 vs 0.638 | inside each other's spread; `coact` takes 3 of 4 folds |
| the background axis, seeds 1–12 | `coact` wins all seven grid points | by **0.0011** at the busy end |
| the background axis, seeds 13–24 | **`loco` takes the busy half** | **the winner changes with the seed block** |

Same code, same grid, twelve different seeds, different winner. Any scheme obliged
to produce a strict order will produce a different strict order next week. So this
one is not obliged to.

**The output is tiers.** Two detectors share a tier unless one of them wins by
more than a seed change can manufacture. *"`coact` and `loco` are tier 1"* is a
legitimate finding, and it is the finding that survives.

## 2. The shape: gates, scores, reports

Every measure is sorted by what it **requires**, not by what it means:

| | measure | ranks | needs planted truth |
|---|---|---|---|
| **Score** | F1, paired by fold | **yes** | yes |
| **Gate** | promiscuity probe, firings/min into a block with nothing in it | no — disqualifies | **no** |
| **Gate** | detection throughput, as a multiple of realtime | no — disqualifies | no |
| **Gate** | distractor rate — *specified, disarmed, see §6* | no | yes |
| **Tiebreak** | promiscuity probe, *within* a settled tier | ordering only | no |
| **Report** | recall by participation level, false alarms, raw timing, near-misses | no | mixed |

A **gate encodes a requirement** and survives a change of data set. A **weight
encodes a preference**, and a preference about how much one failure matters
against another is a scientific claim that this project has no measurement to
support. So the scored part is kept as small as it can be — one number — and
everything else either disqualifies or informs.

The practical payoff is the second column of that table. Point this rule at a
recording set with no coordination ground truth and the probe and the timing gate
still work, and you know exactly which half you lost rather than discovering it in
the numbers.

## 3. Which measures rank, and which only report

*Decision D1.*

**F1 alone ranks.** Ranking on everything is a weighted sum wearing a disguise,
and the weights would be the claim. One number ranks; the rest gate or report.

That is a deliberately narrow score, and the narrowness is load-bearing: it is
what lets the tie rule in §5 be stated precisely enough to be checked. A composite
score would need its own noise floor established before anyone could say what a
tie was, and nothing here has measured one.

## 4. The promiscuity probe gates, and breaks ties

*Decision D2. This also settles the standing question of how two live scoring
rules in the tree could pick opposite winners.*

The probe is a stretch of recording with an elevated event rate and **nothing
planted in it**. A detector that keys on rate rather than on coordination lights
it up.

**It does not enter F1.** Fold it in and the headline stops measuring the detector
and starts measuring how hard the probe was set — the project's own cautionary
number is a detector reading F1 0.09 one way against 0.68 the other, on 599
hot-window detections out of 601 false alarms.

**It gates instead, at the ceilings the calibration already uses**, so a setting
that would be refused when it was chosen is also refused when it is ranked.

**Why it cannot simply be left as pass/fail.** Precision is blind to it. Two
detectors with near-identical precision — 0.572 against 0.543 — differ by **17×**
in how often they fire into the empty block, 1.25 firings a minute against 20.5.
Precision is a *ratio measured on data containing events*, so a trigger-happy
detector harvests true positives that dilute its false ones. Remove the events and
there is nothing left to dilute with. Across twelve detectors the correlation
between precision and probe rate is only −0.32, so this is a property of the
measure, not a quirk of one pair.

So inside a tier — where by construction nobody has won — **the lower probe rate
is listed first.** It never moves the headline number and it never crosses a tier
boundary.

**The objection, and the answer.** A tiebreak on "fires least into nothing" looks
like it rewards a detector for never firing at all, and one detector's 0.0 genuinely
cannot be distinguished from silence by this measurement. It is not a problem,
because the tiebreak only runs *inside* a tier and reaching a tier requires having
earned the F1 that put it there. Silence is filtered by the ranking before the
tiebreak is consulted. The ordering of those two steps is asserted in the tests,
because it is the whole of the answer.

**What the probe is actually measuring** — and the name is wrong. The block is not
empty: it holds 591 spikes across 33 ROIs in five minutes, each ROI drawn
independently, and independent draws still coincide. Within the planted jitter:

| ROIs coinciding | times per minute, by chance alone |
|---|---|
| 3 — the participation floor | **12.4** |
| 4 | 2.97 |
| 5 | 0.57 |
| 6 — the median planted event | **0.10** |
| 7 | 0.02 |
| 8 or more | **0.00** |

About four times rarer per additional ROI. **A detector firing on a three-ROI
cluster in that block is detecting something real.** What the probe measures is
not "fires at nothing" but *calls a chance coincidence coordination* — which is
the same failure the distractor axis is meant to measure deliberately, arrived at
by accident. Read across the curve, each detector's probe rate implies the cluster
size it is consistent with. That read-across is an **inference**, not a
measurement: these detectors threshold their own statistic, they do not count ROIs
in a window.

## 5. What counts as a tie

*Decision D4.*

> **`A` beats `B` only if `A` wins a majority of the paired folds *and* leads by
> more than 0.02 in mean F1.** Anything else is a tie, and they share a tier.
> Below twelve distinct seeds the rule refuses to produce an answer at all.

Both conjuncts do independent work, and the shipped bake-off demonstrates each
catching what the other misses:

| comparison | folds won | mean-F1 margin | verdict |
|---|---|---|---|
| `tube` over `coact` | **2 of 4** | +0.030 — clears | **tie**, blocked by the pairing |
| `coact` over `loco` | 3 of 4 — clears | **+0.013** | **tie**, blocked by the margin |
| `cicada` over `tube_ratio` | 3 of 4 | +0.039 | a win |

Either half alone would have crowned a winner in one of the first two rows.

**The pairing** is information a marginal mean throws away. Every detector runs the
same folds and the same seeds, so "won three of four" is available for free — and
writing it as `0.651 ± 0.044` against `0.638 ± 0.053` discards it and makes the
comparison look like a coin flip.

**The margin** is the bench's noise floor. It is comfortably above the 0.0011 that
separated two detectors at one end of the background grid — a gap that reversed
when the seed block changed.

**The margin is also what makes tiers exist at all**, which was not the reason for
choosing it and is the better reason for keeping it. Because beating requires a
mean-F1 lead, a cycle `A > B > C > A` would need `0 > 3 × 0.02`. The relation is
therefore acyclic and the tier decomposition always terminates. **Majority alone
would not be**: a rule that compared only fold wins admits Condorcet cycles — three
detectors each beating the next, going round — which turn up in about **3% of
random triples**. Such a rule has to break the cycle arbitrarily and then calls the
result a ranking. That is why "margin only" and "majority only" were both rejected,
and it is checked by search as well as by argument.

**The seed floor refuses rather than warns.** Twelve is the count this bench's own
author reached for after calling three noise-dominated — and three is still live in
the background-curve tests one file over, inherited by two other probes whose
headline win counts are three-seed comparisons with no spread reported. A rule that
only warned would be read by whoever happened to be watching stderr, after the
ordering it qualified had been published. This is the argument the project already
made for refusing to load data without a sampling interval, applied one layer up.

**A consequence, and it is the honest one: the rule refuses the shipped bake-off.**
That run covers eight seeds in four folds. It is below the floor, and a re-run at
twenty-four — twelve on each side of the seed-block boundary — is what the rule
asks for next.

## 6. The distractor axis is specified, and switched off

*Decision D3, and the one place where the decision could not be implemented as
made.*

A **distractor** is a planted correlated burst: genuine cross-ROI coincidence that
is not a coordinated event. It is the most scientifically meaningful false positive
this bench measures — firing on a real burst is wrong in a far more interesting way
than firing on noise — and *"should a burst count?"* has been an open question since
the scoring module was written. The ruling was that it gets its own gated axis and
stays out of F1.

**The gate is wired and disarmed, because the number does not currently mean what
its name says.** One detector makes **two detections in an entire fold**, matches a
planted event with both — its precision that fold is 1.000 — and is scored as
hitting **twelve of twelve** distractors. Two detections cannot land near twelve
separate times.

The quantity being computed is *how many distractors are covered by the union of
the detection spans*. So it scales with span width rather than with firing; it has
no opportunity denominator; and, unlike the probe count computed twenty lines above
it in the same function, it is not restricted to unmatched detections, so a
detection that correctly found a real event is charged as a distractor hit as well.

Normalise it and every detector in the tree fires on distractors *more often* than
on real events. Read naively that says none of these methods can tell coordination
from a burst — a large claim, and not one this measure can support, because the
wide spans inflating it are the same spans the recall column is scored on.

So the axis reports and does not gate. Arming it means repairing the measure, which
changes published numbers and belongs to whoever owns that repair —
[the defect is written up with its evidence](todo/2026-08-30-distractor-hits-counts-coverage-not-firing.md).
The threshold sits in the code as `None` with that page named beside it.

## 7. Platform-dependent measures gate and never rank

*Decision D5.*

Detection and calibration times move with hardware and thread count, and the
learned models' shipped numbers were produced on one platform. **A detector is not
better science for having run on a faster machine.** But one that cannot keep up
with acquisition is genuinely unusable, so the normalised throughput gates at
realtime and the raw seconds are reported next to the platform that produced them.

## 8. What this does not do

- **It does not re-baseline the background-curve tests.** Those asserts encode a
  claim — that an F1 cannot be quoted without saying what background it was
  measured at — and were left red deliberately. Flipping them to today's numbers
  would publish the opposite scientific position silently.
- **It does not fix the calibration loop.** The bake-off picks each fold's knob by
  raw argmax with no probe gate, so one detector ships a setting firing over its
  own ceiling on four of four folds. The ranking refuses that detector on the way
  in, which is a symptom; the cure changes published numbers and is its own change.
- **It does not declare ceilings for the learned models.** They have no entries in
  the probe table, so they are ungated on that axis — one of them fires at 2.05 a
  minute, which is over the ceiling the most comparable hand-written detector is
  held to. Setting them is a measurement, not a default, and is left open.
- **It does not rank on the participation breakdown.** Recall at three
  participation levels is a *vector*, and collapsing it to one number is another
  weighted sum in disguise. A detector that only finds large events is a different
  instrument from one that finds small ones, and tiers ought to be able to say so;
  how remains open.

## 9. Reproducing what is quoted here

```
# the tiering, the gates, and the refusal, from the shipped bake-off
python -c "from bugarach.rank import *; print(rank(fold_scores_from_bakeoff('docs/learned/bakeoff.json'), min_seeds=8).table())"

# the background axis, both seed blocks
evaluate_background_curve(name, "baseline_quiet", tuple(range(1, 13)))
evaluate_background_curve(name, "baseline_quiet", tuple(range(13, 25)))

# the paired per-fold F1 the tie rule reads
docs/learned/bakeoff.json -> hand_written[name]["per_fold"]
```

Run pytest with `PYTHONPATH=$PWD/src` from a worktree, or it tests the primary
checkout's sources and fails toward green.
