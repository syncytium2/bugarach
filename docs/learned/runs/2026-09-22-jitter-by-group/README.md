# The correlogram's peak width by group: the fast stream says no, the slow stream says maybe

Written 2026-09-22. Working material, not murderboarded. Tony: *"run the correlogram on fast and
slow, by group_id. are the widths different between the groups?"*

**Tool:** `tools/measure_jitter_correlogram.py --by-group` (tests:
`tests/test_measure_jitter_correlogram.py`). **Data:** the default export
`2026-09-17_revised_2v_long_STEPS_AND_PINS_EXCLUDED`, confirmed at the start of the session; 84
baseline analysis windows from 44 mice, `t50rise` onsets, per stream. Baseline only
(FOUNDATIONS §9). **Record:** `jitter_correlogram.json`. **Figure 1:** `jitter_by_group.png`, also
in the darkroom at `bugarach/correlogram/jitter_by_group.png`.

The measure is unchanged — the cross-ROI onset correlogram of the
[2026-09-22 jitter run](../2026-09-22-jitter-correlogram/README.md), whose pooled numbers this run
reproduces to the digit (fast half-width 0.183 s, slow 0.230 s). What is new is the split, and
three decisions inside it.

## The answer

**Fast: no.** The four groups' half-widths span 0.148 s (ORX) to 0.192 s (DI), a spread of
**0.045 s** — which is *smaller* than the median spread of 0.060 s that shuffled group labels
produce, and well inside the shuffled 95th percentile of 0.108 s. **p(any difference) = 0.71** over
2,000 label permutations. All six pairwise intervals contain zero. The groups are, if anything,
more alike than chance labelling would make them.

**Slow: maybe, and it is not established.** The spread is **0.077 s** against a shuffled 95th
percentile of 0.078 s — **p = 0.054**. MALE is the widest at 0.261 s [0.246, 0.314] and ORX the
narrowest at 0.183 s [0.163, 0.654]. One pairwise interval excludes zero, DI − MALE at
**−0.046 s [−0.086, −0.016]**, which is one comparison of six with nothing correcting for that.

| stream | group | recordings | mice | ROIs | onsets | half-width (s) | 95% interval | σ (s) |
|---|---|---:|---:|---:|---:|---:|---|---:|
| fast | DI | 17 | 10 | 512 | 14,118 | 0.192 | 0.173–0.225 | 0.112 |
| fast | MALE | 22 | 12 | 724 | 11,364 | 0.183 | 0.148–0.252 | 0.106 |
| fast | ORX | 25 | 12 | 763 | 6,408 | 0.148 | 0.078–0.311 | 0.083 |
| fast | OVX | 20 | 10 | 631 | 12,501 | 0.148 | 0.079–0.316 | 0.083 |
| fast | **pooled** | 84 | 44 | 2,630 | 44,391 | **0.183** | 0.159–0.205 | **0.106** |
| slow | DI | 17 | 10 | 512 | 9,762 | 0.214 | 0.206–0.242 | 0.126 |
| slow | MALE | 22 | 12 | 724 | 8,465 | 0.261 | 0.246–0.314 | 0.154 |
| slow | ORX | 25 | 12 | 763 | 3,440 | 0.183 | 0.163–0.654 | 0.107 |
| slow | OVX | 20 | 10 | 631 | 4,485 | 0.235 | 0.098–0.301 | 0.138 |
| slow | **pooled** | 84 | 44 | 2,630 | 26,152 | **0.230** | 0.214–0.252 | **0.135** |

σ is the timing spread of the cells joining a shared moment, read off the simulator calibration.
Every group on both streams stays well under its bench's planted jitter (fast bench 0.36 s, slow
bench 0.30 s), so the pooled finding — *both streams are about three times tighter than their
benches* — is a statement about all four groups and not an average over a split field.

## The dots in Figure 1 b and e, and why the group's number is not their average

Each row carries one small dot per recording, an open circle at their mean, and the filled dot for
the group's own width. The group's width is **not** an average over those dots: it is read off the
group's **pooled** onset-pair counts, one correlogram built from every pair the group contributes,
so a recording weighs by the pairs it brings. The three marks can be read against each other, and
where they disagree the reason is in the last column.

| stream | group | pooled (the filled dot) | mean over recordings | median over recordings | recordings with a measurable peak |
|---|---|---:|---:|---:|---:|
| fast | DI | 0.192 | 0.190 | 0.180 | 17 of 17 |
| fast | MALE | 0.183 | 0.197 | 0.179 | 21 of 22 |
| fast | ORX | 0.148 | 0.133 | 0.079 | 18 of 25 |
| fast | OVX | 0.148 | 0.141 | 0.105 | 14 of 20 |
| slow | DI | 0.214 | 0.248 | 0.235 | 17 of 17 |
| slow | MALE | 0.261 | 0.270 | 0.242 | 20 of 22 |
| slow | ORX | 0.183 | 0.232 | 0.175 | 16 of 25 |
| slow | OVX | 0.235 | 0.176 | 0.083 | 9 of 20 |

**This is why the measure pools rather than averages.** A recording with too few onset pairs has no
measurable peak at all, and that is not rare in the quiet groups: 7 of 25 fast ORX recordings, and
**11 of 20 slow OVX recordings**. A mean or a median over recordings is then taken over whichever
recordings happened to be measurable — slow OVX reads 0.235 s pooled, 0.176 s as a mean and 0.083 s
as a median, and the three differ because they are answers to three different questions. Pooling
asks the question once, of every pair.

The bootstrap agrees with the pooled dot rather than with the recording average: the median of the
400 mouse-clustered draws sits within 0.002 s of the filled dot everywhere except fast ORX
(0.138 s against 0.148 s), so the estimate is essentially unbiased under its own resampling.

## Three decisions the split needed, and why

**The resampling unit is the mouse.** 84 recordings come from 44 mice, so two recordings from one
mouse are not two independent draws; each group's interval resamples its own **mice** with
replacement, and a drawn mouse brings all of its recordings. The pooled block keeps its original
recording-level bootstrap, which is why its numbers still reproduce exactly.

**The answer is one test, not four intervals.** Four intervals invite reading the largest gap as
the finding. The test is a permutation: mouse→group labels are shuffled with each group's number of
mice held fixed, and the spread (widest minus narrowest) recomputed 2,000 times. Group sizes differ
— 25, 22, 20 and 17 recordings — and the smaller group gives the noisier width, which shuffling at
fixed size prices in.

**A width is not a σ, per group.** The calibration curve converts width to σ at the *bench's*
participation and rate. Groups differ in both, so the per-group comparison above is of the measured
half-width; the σ column is recorded beside it and inherits that caveat.

## What would sink the slow result, and it is not a further test

⚠ **The permutation test is anti-conservative exactly where this result lives.** Labels are shuffled
at fixed *mouse* count, not at fixed *onset* count, and the groups' onset counts are not comparable:
ORX contributes 3,440 slow onsets from 25 recordings against DI's 9,762 from 17. A shuffled group of
12 mice therefore usually carries more onsets than the real ORX does, so its width is estimated more
precisely than ORX's is, the null spread comes out too tight, and p comes out too small. **A p of
0.054 under a null biased toward significance is not a result**; ORX's own interval,
0.163–0.654 s, says the same thing in plainer terms.

⚠ **ORX's sparsity is a group feature, not a defect to correct.** It has the most recordings and
the fewest onsets in both streams. FOUNDATIONS §9 already says an empty baseline is a group feature,
and nothing here drops a quiet recording or an ROI with no events.

⚠ **Both streams' quiet groups run off the calibration curve on a minority of draws** — 90 of 400
fast ORX draws and 71 of 400 fast OVX draws land outside the planted-jitter grid, so those σ
intervals are narrower than the width intervals warrant. The widths themselves are unaffected.

**What would settle the slow stream** is not another statistic on these onsets: it is more slow
onsets per group, or a pre-registered single contrast (DI vs MALE) instead of the four-way spread.
Both are Tony's calls, and neither is started.
