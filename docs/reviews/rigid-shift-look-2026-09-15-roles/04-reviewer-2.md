GRANT 4 MISMATCH — missing Grep, Glob; holds no forbidden tools (Read, Bash only)

That mismatch is about how this review ran, not about the note: the run record should say this role took a fallback path. I searched with `grep` through Bash instead. I edited nothing, and nothing was written to the scratch folder: a hook blocks writing source files through a heredoc, so I passed the check scripts to Python on stdin.

**What I checked:** the README; all six figures, opened as images; `results.json` and `meta.json` for the three runs; the three `destruction_table.json` files; `tools/look_rigid_shift.py`; `tools/make_rigid_shift_look_figure.py`; `rigid_shift`, `edge_thinning` and `_prepare` in `surrogates.py`; the features and folds in `surrogate_discriminator.py`; `destruction_twins` in `surrogate_stats.py`; the leak, count, destruction and group rules in the pre-registration; FOUNDATIONS §9; and `docs/learned/recording_identity.md`. I also ran two small tests of my own, described in the first and seventh findings.

## Findings

**1. The leak classifier can see coordination under rigid shift, so the "leak" reading is confounded — BLOCKING**
- **Where:** "What was measured" (the leak bullet), "The answer, short" (slow paragraph), Figure 3's slow bullet, Figure 5's leak bullet, and the Cossart "Reading".
- **Issue:** The note calls the classifier one "that cannot see coordination". It can. With the edge-band features dropped it still keeps the count features pooled over ROIs (`sd_count`, `max_count`, `frac_active`). Once *J* is a sizeable share of the 60 s window, those features see shared bursts carried across window edges. I tested this with the runner's own code: `destruction_twins`, `sg.generate("rigid_shift")`, `feature_mask`, `pair_features`, `cv_correct`, on planted twins against their own rigid shift, with unplanted twins as the reference.
  - **Lab-sized twin** (31 ROIs, 20 min, events in half the ROIs):
    - planted 0.62 against unplanted 0.49 at 10 s
    - planted 0.80 against unplanted 0.45 at 44.8 s
    - the top feature is `sd_count`
  - **Cossart-sized twin** (566 ROIs, events in 20 % of ROIs), planted against unplanted:
    - 0.57 against 0.51 at 5 s
    - 0.59 against 0.49 at 10 s
    - 0.66 against 0.53 at 40 s
  - The Cossart-sized numbers look much like the real Cossart curve (0.52, 0.58, 0.59, 0.60).
  - So accuracy climbing with *J* on the slow stream and on Cossart may be the classifier noticing that coordination was removed, not a leak.
  - That undercuts the proposed ceilings: "about 11 s" on slow, "near 5 s" on Cossart, and "larger shifts leak".
- **Fix:**
  - Stop calling the leak test coordination-blind for *J* that is not small against the window.
  - Add a common-offset shift as a control: every ROI moved by the same offset. It keeps coordination and moves drift. If it rises the same way, the cause is drift; if not, the classifier is seeing removed coordination.
  - Report the planted-against-unplanted twin check beside the leak test.
  - Until then, treat the slow and Cossart ceilings as unexplained, not as leaks.
- **Verified:** yes, by the rerun above. Caveats: 30 twins on the lab-sized run (20 on the Cossart-sized one), and the planted events are strong.

**2. The Cossart destruction result cannot fail at the displacements it clears — BLOCKING**
- **Where:** Figure 6's "What it shows", the "Reading", and "The K scaling makes removal easy".
- **Issue:** The note's own arithmetic settles it. An event in 283 ROIs spread over ±*J* puts about 283/(2*J*) ROIs in a 1 s bin, which is below K = 55 for any *J* ≥ 2.6 s. So every cell at 5 s or more had to read 0, and it did (`destruction_table.json`, all 0.000).
  - "With K scaled, the controls read 0 and 1, so here it can" does not follow. Controls at the two ends do not show the measure can register partial survival.
  - The pre-registration asked for exactly that: a graded control (`freeze_half` on homogeneous resample, reading 0.10–0.90) and a saturation table.
  - The pre-registration also said "Cossart is not scored for destruction". The note reverses that without saying so.
- **Fix:**
  - Take "it removes large events" out of the Cossart reading.
  - State that at *J* ≥ 5 s this measure cannot register survival at the K scanned.
  - Say that the pre-registration's exclusion is being overridden, and why.
  - Before any Cossart removal claim, run the graded control, or a K below 283/(2*J*).
- **Verified:** yes (arithmetic, the table, and pre-registration lines 125–131).

**3. The count test cannot see how rigid shift actually loses onsets — MAJOR**
- **Where:** "Onset counts are unchanged" in "The answer, short", and the Figure 1 and Figure 3 count panels.
- **Issue:**
  - Rigid shift drops onsets pushed past the ends of the recording (`rigid_shift`: "no wrap, onsets pushed out dropped").
  - The count test only looks at interior windows, with the first and last dropped. With *J* < 60 s it cannot see that loss.
  - Its control, `edge_thinning`, thins at every 60 s window edge. That is a mechanism rigid shift does not have, so the control proves nothing about rigid shift.
  - On a 20-minute synthetic recording, rigid shift dropped 0.50 % of onsets at 10 s and 2.07 % at 44.8 s. The larger figure is outside the ±2 % band.
  - The pre-registration names this exact problem (the tube foot gun).
- **Fix:** Report the whole-recording dropped share for each *J*. It is already returned in `per_roi["dropped"]`. Replace "unchanged" with "unchanged inside interior windows", plus the whole-recording loss.
- **Verified:** yes (code, and the synthetic rerun).

**4. The destruction headline follows from K ≥ 3 and one-frame events — MAJOR**
- **Where:** "removes 84–99 %" in "The answer, short", and Figure 4.
- **Issue:**
  - At 10 s, an event in half of 31 ROIs spreads to about 0.8 ROIs per 1 s bin. Below K = 3, near-total removal is geometry, not a finding.
  - Participation 0.2 and 0.5, the K scan 3–8, and the 1 s bin are never justified in the note.
  - Whether real lab events look like "15 of 31 ROIs within one frame" is never argued.
  - Two cases are not measured: small K (pairwise) and looser events. The "best case" caveat is not tested, although the jitter parameter exists.
- **Fix:**
  - Put the dependence into the headline ("for tight synthetic events in 6 or 15 ROIs, K ≥ 3").
  - Justify the participation levels and the K scan from the lab's own baseline events.
  - Run jitter at 1 s, since the note cites that as the real value.
- **Verified:** yes (arithmetic, `twin_shape`, `destruction_twins`).

**5. Some plotted points have nothing to remove — MAJOR**
- **Where:** Figures 2 and 4, participation 0.2 at K = 8 (every row); participation 0.2 at K = 6.
- **Issue:**
  - At participation 0.2 a planted event holds 6 ROIs, so it can never reach K = 8.
  - The median "before" excess there is 0 (0.15 / 0.08 / 0.42 on average, against about 5 at K ≤ 6).
  - Those points and their wide bars (slow 2 s bin, 1.4 s: 0.13, 0.07–0.20) are noise ratios.
  - The note flags the same case on Cossart (K = 146) but not in the lab figures.
  - K = 6 at participation 0.2 needs all 6 ROIs in one bin, so removal is nearly automatic there too.
- **Fix:** Drop or grey out cells where participants < K. Apply the pre-registration's "visible" rule (excess before ≥ 1.0), and say so in the Figure 2 caption.
- **Verified:** yes (per-twin "before" values).

**6. The slow window "near 11 s" crosses 0.55, and the note does not say so — MAJOR**
- **Where:** "The answer, short" ("Up to about 11 s the shift hides (0.52)"), and the slow-stream decision question at the end of the note.
- **Issue:**
  - At 11.2 s the upper bound is 0.551 over mice and 0.552 over slices, which crosses the signed 0.55.
  - The note flags the same situation for Cossart at 5 s but not here, and it asks Tony to accept this window.
  - "At 22 s and beyond it starts to give itself away (0.55–0.56)": the 22.4 s point is 0.549.
- **Fix:** Give the bounds at 11.2 s and say the upper bound crosses 0.55. Correct the 22.4 s value.
- **Verified:** yes (`look_large/results.json`).

**7. The group story is not tested and is partly contradicted — MAJOR**
- **Where:** "almost entirely in the DI group (0.62–0.68)", "probably seeing slow drift moved in time", and Figure 3's by-group line.
- **Issue:**
  - **The numbers disagree with "almost entirely".** At 44.8 s MALE reads 0.593. At 22.4 s MALE reads 0.543 and OVX 0.541.
  - **No uncertainty.** Group accuracies are point estimates from one cross-validation pass, with no interval (306 DI pairs from a handful of mice).
  - **No test.** No group difference is tested.
  - **DI is the easiest group for this classifier in every case.** Under dither, DI reads 0.82–0.90 against ORX 0.69–0.71, so a DI excess is not evidence of DI nonstationarity in particular.
  - **The "least stationary" support is not independent.** It comes from `recording_identity.md`'s within-recording swap. That swap also moves trains in time one ROI at a time, so it shares the confound in the first finding.
- **Fix:**
  - Give per-group bootstrap intervals, and a group-by-displacement test or a statement that it is "described, not tested".
  - Replace "almost entirely" with the four numbers.
  - Label the drift reading as an untested guess, as the Cossart section already does.
  - Name the rival explanations: DI's overall sensitivity, and removed slow coordination.
- **Verified:** yes (`by_group` in `results.json`, and `recording_identity.md` lines 157–163).

**8. Results are pooled across the study's design groups — MAJOR**
- **Where:** all six figures, and the Count and Destruction bullets.
- **Issue:**
  - The pre-registration's own group rule required per-group leak accuracy, count difference and zero-event share "beside every pooled verdict".
  - The figures pool DI, MALE, ORX and OVX. Count is never broken down, and fast-stream groups are never shown.
  - The twins use rates pooled across groups, although the groups differ in rate makeup (`recording_identity.md`).
- **Fix:** Add group-split leak and count panels. At least give per-group fast numbers (the largest is OVX 0.537 at 5 s), and say the twins are pooled.
- **Verified:** yes.

**9. The conclusions reach past baseline-only data — MAJOR**
- **Where:** "The answer, short", and the decision section at the end.
- **Issue:**
  - All the lab data come from baseline windows, but "looks usable" is stated without that limit.
  - FOUNDATIONS §9: senktide raises the GCaMP background over time, which is a strong nonstationarity.
  - If the slow leak really is drift, as the note guesses, a detector trained against rigid-shift negatives may fire on treatment drift.
- **Fix:** Put "baseline windows only" into the short answer. Add a caveat that behaviour on treatment windows, where drift is larger, is untested.
- **Verified:** yes (FOUNDATIONS §9, `meta.json` window sources).

**10. Uniform dither does not show the leak test can catch a rigid-shift leak — MAJOR**
- **Where:** "Uniform dither … is drawn beside it as what a leak looks like", and the Figure 1 legend.
- **Issue:**
  - Dither scrambles within-ROI intervals, a large per-ROI change (0.63–0.99).
  - Rigid shift keeps intervals exactly, except at window edges. Its possible leaks are drift and edge effects, and dither exercises neither.
  - So dither shows the classifier works, not that it would catch this surrogate's failure.
  - For fast, "hides" rests on a test with no demonstrated power against the relevant alternative.
- **Fix:** Add a positive control that has the rigid-shift failure: a planted slow per-ROI drift, the common-offset shift from the first finding, or the edge features put back as a known-leaking reference.
- **Verified:** yes (code).

**11. The 60 s window is never justified, and it shapes the leak curve — MINOR**
- **Where:** "What was measured".
- **Issue:**
  - *J* goes up to 44.8 s against a 60 s window.
  - How strongly the pooled count features react to a shift grows with *J* divided by the window (see the first finding).
  - The window is neither justified nor varied.
- **Fix:** Justify 60 s, or show the leak at a second window length (for example 120 s) for the largest *J*.
- **Verified:** partly (the mechanism was verified; no second window was run).

**12. The 1.67–98.33 % range is unexplained, and its basis no longer fits — MINOR**
- **Where:** Figure 1 and the Figure 1 legend.
- **Issue:**
  - The range is inherited from the pre-registration (0.05/3 per tail, for three displacements) but never explained in the note.
  - It is reused unchanged for 4 and 5 displacements, so the adjustment it implies is no longer the one applied.
- **Fix:** Explain it in one line, or relabel it as a descriptive range.
- **Verified:** yes (pre-registration lines 260–262, `summarize`).

**13. The destruction bars and "excess" are ambiguous — MINOR**
- **Where:** "Bars are 95 % over the 20 twin pairs" (Figure 2), and the definition of "excess".
- **Issue:**
  - The bars are a bootstrap 95 % interval of the ratio of mean "after" to mean "before", resampling twins. They are not the spread across twins, which stays hidden.
  - The unit of "excess" is never given (about 15 at participation 0.5 with 20 events).
- **Fix:** Say "bootstrap 95 % interval of the mean ratio, resampling twins", and show the per-twin spread. Give the unit of excess.
- **Verified:** yes (`_retained`).

**14. Figure titles name the quantity, not what it means — MINOR**
- **Where:** the Figure 1–6 captions (for example "Leak and onset count at the planned displacements").
- **Issue:** The titles say what is plotted, not why it matters.
- **Fix:** Lead with the inference, for example "Rigid shift is not separable from real at any planned displacement; dither is".
- **Verified:** yes.

**15. The "about 1 s" jitter figure has no traceable source — MINOR**
- **Where:** "an interface2 commit measured real fast onset jitter at about 1 s".
- **Issue:** This role could not trace the source: no sha or file is given.
- **Fix:** Cite the commit or file.
- **Verified:** no.

## Most urgent
The first two findings decide the note's recommendations. The leak classifier sees planted coordination once *J* is a sizeable share of the window, so the slow and Cossart "leak" ceilings may be the instrument detecting removal. The Cossart destruction cells at 5 s and above could only have read zero.

## Files
- <worktree>/docs/learned/rigid_shift_look/README.md
- <worktree>/tools/look_rigid_shift.py
- <worktree>/tools/make_rigid_shift_look_figure.py
- <worktree>/src/bugarach/surrogate_discriminator.py
- <worktree>/src/bugarach/surrogates.py
- <worktree>/docs/proposals/2026-09-14-preregistration-is-rigid-shift-usable.md
- <worktree>/docs/learned/recording_identity.md
