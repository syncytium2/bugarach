GRANT 6 MISMATCH — missing Grep, Glob; holds no forbidden tools (holds Read, Bash, WebSearch, WebFetch)

(The missing search tools were covered with `grep` through Bash. The hook blocks heredoc source files and I hold no Write tool, so every check ran as an inline `python -c` script in the scratch directory. Nothing in the repo or darkroom was touched, and no `rigid_shift` rows from the overnight run were opened.)

# Role 6 (RTFM) findings: rigid-shift pre-registration

**Artifact:** `docs/proposals/2026-09-14-preregistration-is-rigid-shift-usable.md`

**Grounded in:**
- **Elephant 1.2.1 source:** `dither_spike_train`, `dither_spikes` and `randomise_spikes`, downloaded from the v1.2.1 tag. I also installed Elephant 1.2.1 in a scratch virtual environment and ran the repo's own generators.
- **Lopez-Paz & Oquab 2017**, from the shelf (`lit/ml/lopezpaz_oquab_2017_c2st.pdf`).
- **Code:** `surrogate_discriminator.py`, `surrogates.py`, `surrogate_stats.py`, `assess.py`, `tools/measure_recording_identity.py`, `tools/probe_discriminator.py`, `tools/build_surrogate_screen.py`.
- **Data layout:** measured from `dataset.current("steps_excluded")` (windows only, no outcomes). Each stream has 84 recordings, 44 mice and 1,669 pairs, with 20 to 60 pairs per mouse. Generation windows run 1,020 to 1,200 s, **all exact multiples of 60 s**. Cossart has 59 recordings, 32 mice, 1,375 pairs, and a window that runs over the whole recording from frame 0.

## Blocking

**The count gate: its control is void at *J* = 1.6 s, and the statistic cannot see what rigid shift does**
- **Where:** Count preservation, "Pass" and "Control".
- **Issue, part one (the statistic).** The 60 s tiles cover each generation window exactly. So averaging the per-window count differences within a mouse telescopes: an ROI's summed difference is just minus the onsets it dropped. The statistic reads about −*J*/(2*T*). On synthetic trains with the data's layout, run through the repo's `rigid_shift`, the 98.3 % interval over mice was [−0.08 %, −0.03 %], [−0.14 %, −0.07 %] and [−0.29 %, −0.18 %] at the three *J*. Rigid shift passes by construction.
- **Issue, part two (the control).** `edge_thinning` at *J* loses about *J*/120 of each window's onsets. At 1.6 s its interval was [−1.49 %, −1.17 %], **inside ±2 %**. The control therefore passes, the gate is void, and under the outcome rule *J* = 1.6 s can never PASS. At 2.5 s the interval was [−2.44 %, −1.95 %], which only just straddles the band. The page never gives the control's *J*.
- **Fix (amendment):**
  - Score counts by window position (first and last tile versus interior), or use the per-window absolute deviation.
  - Fix the control's *J* where its expected loss clearly exceeds the band (5 s gives about 4 %).
  - Or tighten the tolerance. Declare the choice before the run.
- **Verified:** yes (synthetic, repo generators, Elephant 1.2.1).

**The do-nothing destruction control is an identity**
- **Where:** Destruction, "Controls: do-nothing must retain at least 0.9".
- **Issue.** `coact_excess` scores "before" and "after" with the same fixed assessor seed (20260722), and `do_nothing` returns its input. So after equals before exactly. I ran `destruction("do_nothing", …)`: every visible row read retained 1.0000 with spread 0.0. The control cannot fail. It is the same defect the 2026-09-11 review caught for circular shift.
- **Fix:** replace it with a graded control that can miss:
  - `freeze_half`, which already exists;
  - uniform dither at 1 frame;
  - or at minimum, score do-nothing with a different assessor seed.
- **Verified:** yes.

**The leak gate has no "undecided" outcome and is likely underpowered, so a STOP can be an artefact of the instrument**
- **Where:** Leak, "Pass at a *J*", and the outcome table.
- **Issue.** I simulated per-pair correctness on the real mouse layout, using `mouse_bootstrap`'s resampling at 98.3 %. The table shows how often a surrogate's upper bound falls below 0.55:

  | true accuracy | within-mouse correlation (ICC) | P(upper bound < 0.55) |
  |---|---|---|
  | 0.50 (no leak) | 0 | 0.95–0.97 |
  | 0.50 | 0.05 | 0.51–0.61 |
  | 0.50 | 0.11 | 0.28–0.37 |
  | 0.52 | 0.11 | 0.11–0.16 |

  An ICC of 0.11 is the only production value on record (fast homogeneous resample, 0.112). 0.52 sits inside the exploratory range the page quotes (0.495–0.524). Tied pairs, which score 0.5, raise these probabilities.

  The outcome table maps "could not exclude 0.55" to FAIL, then to STOPPED, "written up as a result about the data". `measure_recording_identity.verdict` already had a third state, UNDECIDED, and the page dropped it.
- **Fix (amendment):**
  - Add UNDECIDED: the upper bound is at or above 0.55 but the lower bound is not above it.
  - Add a feasibility check that never reads the candidate: two independent rigid-shift draws scored against each other, at the same pair count and tie structure. If that bound is at or above 0.55, the stream is UNDECIDABLE and is not reported as FAIL.
- **Verified:** yes (synthetic, real layout).

## Major

**The percentile behind "98.3 %" is undefined, and `mouse_bootstrap` cannot produce it**
- **Where:** "The displacements", last line, and Leak, "Intervals".
- **Issue.** `mouse_bootstrap` hard-codes the 2.5th and 97.5th percentiles (`measure_recording_identity.py:198`). The page says both "98.3 % interval" and "upper 98.3 % bound":
  - A one-sided test at 0.05/3 means the 98.33rd percentile.
  - A two-sided 98.3 % interval means the 99.17th.
  - The count gate, as a two-one-sided equivalence test at 0.05/3, would use a 96.7 % two-sided interval.

  The choice changes the result: at ICC 0.11 the pass probability is 0.28 against 0.37.
- **Fix:** state the exact percentiles for each gate, and add a level parameter to `mouse_bootstrap` in "What has to be built". Optionally use 10,000 resamples; the Monte Carlo spread of the bound is 0.002 at 2,000 and 0.0009 at 10,000.
- **Verified:** yes.

**A mouse bootstrap over fixed-fold correctness is anti-conservative**
- **Where:** Leak, "Intervals".
- **Issue.** The folds are fitted once and only the test-side correctness is resampled. That ignores variation from training and from fold assignment. In synthetic runs (47 features, the real layout, 150 datasets), the bootstrap standard error was 13 % too small with no mouse effect and 42 % too small with one. The upper bound fell below the procedure's own mean accuracy in 1–5 % of datasets, against 0.83 % nominal.
- **Fix:** refit inside the bootstrap. Resample mice, keep each duplicated mouse in one fold, and rerun `_cv_correct`; the model is numpy logistic, so this is cheap. Alternatively, widen the bound by the spread across fold seeds.
- **Verified:** yes (synthetic).

**The fold seed is a forking path**
- **Where:** Leak, "new mouse folds".
- **Issue.** The page runs the negative control on 20 seeds but never says which fold seed the candidate's bound uses. On identical synthetic data, accuracy across 20 fold seeds had a spread of 0.008–0.019. The upper bound ranged over **0.03–0.07** across seeds, which is large against the 0.55 margin.
- **Fix:** declare one fold seed, or average per-pair correctness over the 20 fold seeds before bootstrapping.
- **Verified:** yes (synthetic).

**What the bound covers is narrower than the question**
- **Where:** "The question" and the VIABLE outcome.
- **Issue.** The paper frames a classifier two-sample test as a test of P = Q. Failing to reject is a type-II question that depends on the classifier. Held-out accuracy understates how separable the samples are. In synthetic data where the best linear rule reaches 0.55, the cross-validated accuracy of this L2 logistic averaged only 0.514–0.527, and the bound fell below 0.55 in 21–33 % of datasets. A self-supervised model is a far stronger learner than a linear model on pooled features.
- **Fix:** amend the VIABLE wording to "not separable by the per-ROI-blind linear discriminator on 60 s windows". Optionally report a nonlinear learner on the same features beside it.
- **Verified:** yes (paper text and synthetic).

**Rigid shift's edge losses land in scored windows**
- **Where:** Leak and Count, and the generation window versus the analysis windows.
- **Issue.**
  - Elephant 1.2.1 draws one offset per call, uniform on (−shift, +shift), and with `edges=True` it **drops** onsets outside [t_start, t_stop). The repo seeds each ROI separately. After frame centring and flooring, the offset is round(*u*): 2*J*+1 values, with half weight at the two ends.
  - The tiles start at the generation window's start and, on the lab data, end at its end. So every recording's first and last scored windows carry a gap of length |*d*| at the outer edge.
  - Expected loss in the 5 s edge band is about (*J*/4)/5 s: 8 %, 12.5 % and 25 % at the three *J*. Synthetic runs gave −14 % and −28 % at 2.5 s and 5.0 s.
  - The discriminator's `edge_start` and `edge_end` features read exactly that band, in 2 of 20 pairs per recording. The two larger *J* are penalised for where generation stops, not for how the shift behaves.
  - Cossart: the first tile is always hit. The end edge usually falls in the discarded remainder (97 % of recordings).
- **Fix:** declare it. Either score only tiles at least *J* from a generation edge (18 of 20 pairs), or report the leak with and without edge tiles.
- **Verified:** yes.

**The positive control cannot fail at the margin**
- **Where:** Leak, "Positive control".
- **Issue.** Uniform dither scored 0.757–0.764 in production reruns (report residual on the fast-stream voiding). Its lower bound clears 0.55 trivially, and the leak it carries is in intervals, not edge bands. It shows power against a gross leak, not the ability to bound one near 0.55.
- **Fix:** use a calibrated near-margin control, such as partial-ROI uniform dither, or `edge_thinning` at around 0.6 accuracy. Its bound must fail the 0.55 pass.
- **Verified:** partly (numbers from the review record, not rerun).

**The "visible" rule and the retained-share rule are fragile at 1.0 s**
- **Where:** Destruction, "Pass at a *J*".
- **Issue.**
  - "Visible" means before > 0, with no floor. At 1.0 s, the 20 % participation arm at K = 8 turns visible with before = 0.37. At 0.5 s it was 0.00. The other K read 3.7–5.4. The value is stable across 12 assessor seeds (spread 0.002).
  - "Every visible K ≤ 0.25" is therefore gated by a ratio whose denominator is about 13 times smaller.
  - Retained is a ratio of means over 19 draws with no interval and no Bonferroni widening, although the page says "every bound below is Bonferroni-widened".
- **Fix:** add a visibility floor. Put an interval over draws on retained, use its upper bound, and widen it for three *J*. Alternatively, use `pair_share_planted_above`, which the code already computes.
- **Verified:** partly (the denominator was measured; the candidate's after-noise was not, by design).

**The saturation formula understates, and the void clause never fires**
- **Where:** Destruction, "Saturation".
- **Issue.** recruited × bin/(2*J*+1) is the expected count in one bin, but K responds to the largest bin. In a synthetic planted event (1-frame jitter, the adapter's rounding, 16 recruited, 1.0 s bin):

  | *J* | formula | mean largest bin | P(largest bin ≥ 4) |
  |---|---|---|---|
  | 16 frames (1.6 s) | 4.85 | 6.68 | 1.00 |
  | 25 frames (2.5 s) | 3.14 | 5.23 | 0.99 |
  | 50 frames (5.0 s) | 1.58 | 3.74 | 0.56 |

  The formula never exceeds the top of the K scan (8) at any declared *J*, so the void clause is inert. The residual of the event reaches K ≥ 3 with P ≈ 0.98 even at 5.0 s, so K = 3 at 50 % participation will probably decide "every K". That is knowable before any data are read.
- **Fix:** replace the formula with the largest-bin expectation and P(≥ K), and publish it for each *J* and K before the run.
- **Verified:** yes (synthetic).

## Minor

**The 20 negative-control seeds are effectively independent; the page's rates stand**
- **Where:** Leak, "Negative control".
- **Issue.** Given the data, the observed random orientation is exchangeable with the permutation draws. Per seed, P(flag) ≤ 9/200 = 0.045, and flags are independent across seeds. In synthetic runs (10 datasets × 20 seeds) there were 5 flags in 200 (2.5 %). Accuracy spread across seeds was 0.020–0.024, close to the binomial 0.017. The quoted 7.5 % and 1.6 % are correct at 0.05 and slightly conservative: P(≥ 4 of 20) is 1.1 % at 0.045.
  - The control is still exchangeable by construction. It checks only the permutation code path, and no pass decision uses permutation P values.
- **Fix:** add a control on the bootstrap bound, which is the instrument the decision actually uses. The draw-versus-draw check under the blocking power finding does this.
- **Verified:** yes. A 50-dataset tally was still running at write-up and is not reported.

**The bin cannot be expressed as a half-window**
- **Where:** "The bin as a parameter of `destruction`".
- **Issue.** `DESTRUCTION_HALF_WINDOW_FRAMES` gives bins of 2*H*+1 frames. 1.0 s at dt 0.1 s is 10 frames, which is unreachable (9 or 11). Float binning in `assess` at 1.0 s is exact: 10 frames per bin over 12,000 frames.
- **Fix:** take the bin in seconds or frames directly.
- **Verified:** yes.

**1.0 s as "the assessor's own definition" holds for fast only**
- **Where:** Destruction, "timescale".
- **Issue.** 1.0 s is the shipped default for every stream (`assess.py:512`). But the docstring calls it "the MATLAB default for the faster stream", the MATLAB slow parity case uses 2 s (`tools/matlab_ref/gen_ref_assess.m`), and LOCO's slow optimum is a 2 s bin.
- **Fix:** report 2 s beside for slow.
- **Verified:** yes.

**Bonferroni across *J* is the right direction; the Cossart *J* is ambiguous**
- **Where:** "Three displacements are a family of three" and the Cossart column.
- **Issue.** A false PASS is a union over *J*, so correcting across the three *J* is right and conservative, not anti-conservative. The gates within one *J*, and the requirement that both streams pass, are intersection-union tests and need no correction.
  - Destruction gets no multiplicity control at all (covered under the "visible" finding).
  - "Cossart leak at the passing *J*" is undefined when more than one *J* passes.
- **Fix:** name the rule, for example the smallest passing *J*.
- **Verified:** yes (reasoning).

**Homogeneous resample shares seeds between the twins**
- **Where:** Destruction, "Controls".
- **Issue.** The same key seeds both twins. ROIs with equal counts get identical surrogates: 14–18 of 31 at 20 % participation and 8–10 of 31 at 50 %. The rest share their first *n* draws. The control can still fail, but only just; retained was −0.016 to +0.024 at both bins.
- **Fix:** say so, or seed the twins independently.
- **Verified:** yes.

**Checked, no finding**
- The 1.5 × bin gather window affects only `_clusters`, never `coact_excess`, so changing the bin does not change "retained" through it.
- Excluding circular shift is correct: `surrogates.circular_shift` calls `assess.circular_shift_trains`, the function the assessor uses for its own surrogates.
- Rigid shift's offsets are independent per ROI and match the page's description.

---

**Addendum from the same role, sent after the report above (verbatim):**

The larger simulation of the real-against-real negative control has finished, and it backs the page's numbers. I ran 50 synthetic datasets, using the real layout of mice and recordings and the unchanged `negative_control_pairs` and `forced_choice`, each at 20 seeds:

| flags out of 20 seeds | 0 | 1 | 2 | 3 | 4 or more |
|---|---|---|---|---|---|
| datasets observed | 17 | 22 | 8 | 3 | 0 |
| expected if flags were independent, rate 0.045 | 19.9 | 18.8 | 8.4 | 2.4 | 0.5 |

- **Flag rate:** 0.047 per seed (47 flags in 1,000 seed runs).
- **Spread:** the variance is 0.86 times what independent flags would give, so the 20 seeds are not correlated in a way that matters.
- **Why:** each seed draws its own random orientation, fold assignment and permutations. Given the data, its observed accuracy is exchangeable with its own permutation draws, so P(flag) ≤ 9/200 = 0.045 per seed.

**Change to my negative-control finding (minor):** replace its "Verified" line with "yes: 50 datasets × 20 seeds, flag counts consistent with independent flags at 0.045". The page's 7.5 % for three or more flags and 1.6 % for four or more are correct at α = 0.05, and slightly conservative at the true 0.045 (four or more then happens 1.1 % of the time). The rest of that finding stands. This control is exchangeable by design, so it only checks the permutation code. It says nothing about the bootstrap bound, which is what the pass decision actually uses.

This does not change any blocking or major finding.
