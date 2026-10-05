# The correlogram's peak width by group: neither stream has a difference, and the slow one was a single recording

> **Revised 2026-09-23.** The first version of this page called the slow stream a *maybe* at
> p = 0.054. Drawing the correlograms **raw** (Figure 2, asked for by Tony) showed a bump near
> 7.5 s lag in ORX that the shoulder-subtracted panels had hidden; it is one recording,
> `20250806_174`, and removing it moves ORX from 0.183 s to 0.229 s and the four-way p from
> **0.054 to 0.48** (Figure 3). The slow suggestion was that recording's leverage, not a group
> effect. The leave-one-out is now computed by the measure itself, so it travels with every rerun
> rather than waiting for somebody to ask the right question.
>
> Two numbers also moved under this page while it sat: `main` merged
> [the bench adopting this measurement](https://github.com/syncytium2/bugarach/commit/8137da71),
> so both benches now plant the jitter measured here (fast 0.106 s, slow 0.135 s) and the
> calibration curve was rebuilt on the new regimes. The half-widths are unchanged — they are read
> off the data — and σ moved by about 2%.

Written 2026-09-22. Working material, not murderboarded. Tony: *"run the correlogram on fast and
slow, by group_id. are the widths different between the groups?"*

**Tool:** `tools/measure_jitter_correlogram.py --by-group` (tests:
`tests/test_measure_jitter_correlogram.py`). **Data:** the default export
`2026-09-17_revised_2v_long_STEPS_AND_PINS_EXCLUDED`, confirmed at the start of the session; 84
baseline analysis windows from 44 mice, `t50rise` onsets, per stream. Baseline only
(FOUNDATIONS §9). **Record:** `jitter_correlogram.json`. **Figures**, here and in the darkroom at
`bugarach/correlogram/`: **Figure 1** `jitter_by_group.png` (the widths and the test), **Figure 2**
`raw_correlograms.png` (the curves as measured, nothing subtracted or normalised), **Figure 3**
`one_recording_leverage.png` (what one recording does to a group).

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

**Slow: no, once one recording is out.** As recorded the spread is **0.077 s** against a shuffled
95th percentile of 0.078 s, **p = 0.054** — MALE widest at 0.261 s, ORX narrowest at 0.183 s. But
ORX's number is one recording's: removing `20250806_174` moves that group to **0.229 s**, drops the
spread to **0.046 s**, which is the shuffled median exactly, and takes **p to 0.48** (Figure 3).
Nothing else in the four groups moves by more than 0.016 s. A difference that one recording carries
is not a group difference.

| stream | group | recordings | mice | ROIs | onsets | half-width (s) | 95% interval | σ (s) | without its biggest mover |
|---|---|---:|---:|---:|---:|---:|---|---:|---:|
| fast | DI | 17 | 10 | 512 | 14,118 | 0.192 | 0.173–0.225 | 0.108 | 0.180 |
| fast | MALE | 22 | 12 | 724 | 11,364 | 0.183 | 0.148–0.252 | 0.103 | 0.167 |
| fast | ORX | 25 | 12 | 763 | 6,408 | 0.148 | 0.078–0.311 | 0.082 | 0.095 |
| fast | OVX | 20 | 10 | 631 | 12,501 | 0.148 | 0.079–0.316 | 0.082 | 0.231 |
| fast | **pooled** | 84 | 44 | 2,630 | 44,391 | **0.183** | 0.159–0.205 | **0.103** | — |
| slow | DI | 17 | 10 | 512 | 9,762 | 0.214 | 0.206–0.242 | 0.122 | 0.220 |
| slow | MALE | 22 | 12 | 724 | 8,465 | 0.261 | 0.246–0.314 | 0.150 | 0.253 |
| slow | ORX | 25 | 12 | 763 | 3,440 | 0.183 | 0.163–0.654 | 0.104 | **0.229** |
| slow | OVX | 20 | 10 | 631 | 4,485 | 0.235 | 0.098–0.301 | 0.135 | 0.220 |
| slow | **pooled** | 84 | 44 | 2,630 | 26,152 | **0.230** | 0.214–0.252 | **0.132** | — |

σ is the timing spread of the cells joining a shared moment, read off the simulator calibration.
**Do not read σ against the bench any more**: as of `8137da71` both benches plant the jitter this
measure produced (fast 0.106 s, slow 0.135 s), so the comparison is now circular. The earlier
version of that sentence — *three times tighter than their benches*, against 0.36 s and 0.30 s —
was true of the benches as they stood on 2026-09-22 morning and is not a finding to repeat.

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

## What the raw curves show, and what sank the slow result

Figure 1's peak panels subtract each group's mean excess over 5–10 s lag and divide by the zero-lag
height, which is what makes the shapes comparable — and what hides two things. **Figure 2 is the
same correlograms with neither step applied.** Three things are visible only there:

- **The peaks differ enormously in HEIGHT, and height is not width.** Zero-lag excess coincidence
  runs 1.0 (OVX) to 4.5 (DI) on fast and 17.0 (ORX) to 32.4 (DI) on slow — a group's onsets can be
  four times as over-represented at zero lag as another's while the peak is no wider.
- **The slow stream dips BELOW chance at 2–5 s lag**, to about −0.6 pooled, recovering by 6 s.
  Fewer cross-ROI onset pairs than the ROIs' own rates predict. Some of that is arithmetic rather
  than biology: because chance is set by whole-window counts, excess summed over all lags is zero by
  construction (`measure_slow_comodulation.py`, the single-window case of Brody 1999 eq. 3.6), so a
  peak is paid back somewhere.
- **ORX's slow shoulder is not a shoulder.** It carries a bump to +2.0 near 7.5 s lag, and
  `20250806_174` alone supplies 45% of the observed pairs in that band at an excess of +7.6. That
  is what led to the leave-one-out below.

**The shoulder subtraction is not what drives any of this**, which was worth checking rather than
assuming: with nothing subtracted at all the group widths move by at most 0.012 s and the slow
p goes 0.054 → 0.059; with one common level for every group, 0.060.

⚠ **What does drive the slow result is one recording, `20250806_174`** — Figure 3. ORX 0.183 s →
0.229 s without it, four-way spread 0.077 s → 0.046 s, p 0.054 → 0.48. The same recording is ORX's
biggest mover on fast (0.148 s → 0.095 s). A group's width is read off pooled pair counts, so a
recording weighs by the pairs it brings and a dense or unusually coincident one can carry a group.
**That is not a defect to filter** — the export folder is the input, and which recordings are
analysable is the producer's call — but it is the first question to ask of any group difference
here, and the measure now answers it in every run (`leave_one_out`, `without_most_influential`).

## Two things that were already weak about it

⚠ **The permutation test is anti-conservative exactly where this result lived.** Labels are shuffled
at fixed *mouse* count, not at fixed *onset* count, and the groups' onset counts are not comparable:
ORX contributes 3,440 slow onsets from 25 recordings against DI's 9,762 from 17. A shuffled group of
12 mice therefore usually carries more onsets than the real ORX does, so its width is estimated more
precisely than ORX's is, the null spread comes out too tight, and p comes out too small. **A p of
0.054 under a null biased toward significance is not a result**; ORX's own interval,
0.163–0.654 s, says the same thing in plainer terms.

⚠ **ORX's sparsity is a group feature, not a defect to correct.** It has the most recordings and
the fewest onsets in both streams. FOUNDATIONS §9 already says an empty baseline is a group feature,
and nothing here drops a quiet recording or an ROI with no events.

⚠ **The fast stream's quiet groups run off the calibration curve on a minority of draws** — 78 of
400 fast ORX draws and 69 of 400 fast OVX draws land outside the planted-jitter grid, so those σ
intervals are narrower than the width intervals warrant. The widths themselves are unaffected.

## What is left, and what it would take

The measurement stands: **no between-group difference in correlogram width on either stream**, and
the pooled numbers (fast 0.183 s half-width, σ 0.103 s; slow 0.230 s, σ 0.132 s) are what the
benches now plant.

What would make a group difference findable here is more onset pairs per group, not another
statistic on these ones. ORX carries 3,440 slow onsets, a third of DI's, and its width rests on so
few pairs that one recording moves it by 0.046 s. A pre-registered single contrast — DI versus MALE
on slow, the only pair whose intervals separated — would spend the power on one question instead of
six, but on this corpus it would still be asking 20 recordings to outvote one. Both are Tony's
calls, and neither is started.
