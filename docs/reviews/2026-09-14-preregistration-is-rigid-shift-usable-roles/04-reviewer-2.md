GRANT 4 MISMATCH — missing Grep, Glob; holds no forbidden tools (Read, Bash only)

This is a finding about the run, not the page: I searched with `grep` through Bash. The run record should say this role came in through a fallback path.

**Contamination:** I read no rows from the overnight run's darkroom folder. I computed no destruction or leak result for rigid shift at any of the declared displacements. Every walk-through below is either a control on synthetic data or plain arithmetic.

# Role 4 (Reviewer 2): pre-registration for "is rigid shift usable?"

**Artifact:** `docs/proposals/2026-09-14-preregistration-is-rigid-shift-usable.md`

**Summary:** 3 blocking, 9 major, 4 minor.

## Blocking

**B1. Count preservation gate: it can't fail for rigid shift, and its control goes void at the smallest displacement.**
- **Location:** *Count preservation*, and the per-stream PASS rule.
- **Issue, part 1 (the control).** The page never says what displacement (*J*) `edge_thinning` runs at. The screen's `params_for` gives edge controls the cell's own *J*.
  - `edge_thinning` dithers uniformly inside each 60 s window and drops what leaves it. The expected loss is *J*/120 of the count.
  - On a stand-in train with an 18.5 min baseline and 60 s windows, that came to −1.17 % at 1.4 s, −1.30 % at 1.6 s, −2.14 % at 2.5 s, −2.27 % at 2.8 s and −4.15 % at 5.0 s.
  - At 1.6 s (fast) and 1.4 s (slow) the control therefore sits inside ±2 %. It passes the gate, so the gate is void. Under the PASS rule ("every control valid"), the smallest *J* on both streams can then never pass.
  - At 2.5 s and 2.8 s the control only just clears −2 %, so whether it counts as "failing" depends on how wide the interval is.
- **Issue, part 2 (the statistic).** Rigid shift loses onsets only at the edges of the whole generation window.
  - The discriminator's windows (`probe_discriminator.analysis_windows`) are laid end to end from the start of the generation window, with no margin. So the whole loss lands in the first window, and in the last one if the leftover margin is under *J*.
  - Averaged over all windows, the stand-in gave −0.03 % to −0.12 %. The first window alone lost −0.6 % to −1.9 %, and its 5 s edge band loses up to about a quarter of its onsets at *J* = 5 s.
  - The page's statistic averages every window within a mouse. It is scored over the set where the harm isn't: an average over all items can't show a harm confined to a few of them.
  - The control only shows power against a uniform loss 20–40× larger than the pooled rigid-shift loss.
  - This is exactly the tube foot gun the gate cites: `tube` would see an onset deficit that is local in time.
- **Suggested fix.**
  - Declare `edge_thinning`'s *J*, fixed and large enough to fail at every candidate *J*.
  - Score count preservation **per window position** (first window, last window, interior), or only on windows at least *J* from the generation edge, and say which.
  - Or remove the defect at the source: generate over a window padded by the largest *J* and score the inner windows. Then the gate is answered by construction and its control can be tested honestly.
- **Verified:** yes. I read `surrogates._edge_dither`, `rigid_shift` and `probe_discriminator.analysis_windows`, and ran a numpy stand-in.

**B2. The outcome table is incomplete, and FAIL/STOPPED can be built from void cells.**
- **Location:** *The outcome, per stream and overall*.
- **Issue.**
  - A stream is VOID only if controls fail at **every** *J*, and FAIL "otherwise". So one broken *J* plus one failed *J* reads FAIL, even if the broken *J* was the only one that could have passed. B1 makes exactly that likely at the smallest *J*.
  - Saturation marks a *J* void "not failed", but the stream rule never says how a saturation-void *J* counts.
  - The table has no row for PASS/VOID, FAIL/VOID, VOID/VOID, or PASS/PASS with a void Cossart leak test.
  - "Cossart leak at the passing *J*" is undefined when fast and slow pass at different grid positions, or at more than one.
  - "Fixed and rerun rather than read" doesn't say what may change before the rerun. After data have been seen, that is the post-hoc loop this page exists to end.
  - Since STOPPED stops the goal, a STOP assembled from void cells ends the goal on an instrument defect.
- **Suggested fix (dated amendment).**
  - A stream whose only non-failing *J* are void is VOID, not FAIL.
  - Add the VOID rows, and say which outcome each combination gives.
  - Tie Cossart's *J* to the grid position (smallest, middle, largest).
  - For a rerun after VOID, list the permitted changes in advance: the broken instrument only, with no thresholds or displacements changed.
- **Verified:** yes, from the page text.

**B3. Neither destruction control can fail on data this size, and the saturation void rule watches the wrong K.**
- **Location:** *Destruction*, the Controls and Saturation bullets.
- **Issue, do-nothing.** It returns its input. `destruction` scores both sides with `coact_excess`'s fixed seed (20260722). So "retained" is exactly 1.0 by construction, and "at least 0.9" can't fail.
- **Issue, homogeneous resample.** I ran it through the real `destruction_twins` and `assess_coactivity` at a 1.0 s bin: 31 ROIs, 11,100 frames, rates across the baseline IQR, 19 draws, 3 twin seeds, both participation levels.
  - It read retained 0.00 at every K.
  - A sparse random background never reaches K after the selection correction, so this control reads zero whether or not the measure grades removal correctly.
  - It only has power against dense saturation (the Cossart case), which this gate doesn't score.
- **Issue, no graded control.** Nothing checks that "retained" behaves sensibly near the 0.25 threshold. The graded `freeze_half` control is already in the screen (`build_grid` adds it), and the page drops it.
- **Issue, the saturation rule.**
  - It voids a *J* only when the expected number of co-active ROIs left in the bin exceeds the top of the K scan (8).
  - The pass rule needs ≤ 0.25 at **every** visible K, so the binding K is 3.
  - The report's own formula (recruited × bin / (2*J*+1)) gives about 15.5 ROIs recruited at participation 0.5 on fast. With a 10-frame bin, about 4.7 stay in the bin at 1.6 s and 3.0 at 2.5 s. Both are at or above K = 3 but below 8, so neither is void.
  - Those cells are FAIL, and that is predictable from arithmetic before any run. The page should say so up front rather than find it afterwards.
- **Suggested fix.**
  - Replace do-nothing with `freeze_half` (or a known partial removal) whose expected retention per K is derived in advance, and require it to read within a stated band.
  - Keep homogeneous resample, but label it as a guard against saturation only.
  - Compute and publish now, from the formula alone, the expected in-bin survivors at every (stream, participation, *J*) against K = 3. Define "void" against the binding K, not the top of the scan.
- **Verified:** yes. I read `do_nothing`, `destruction` and `coact_excess`, and ran the homogeneous-resample walk-through.

## Major

**M1. A leak PASS doesn't license "a usable negative class".**
- **Location:** *The question*; *Leak*; the "VIABLE: the goal moves to the model tier" row.
- **Issue.** Rigid shift keeps each ROI's intervals, and more than 90 % of each 60 s window's content at *J* ≤ 5.6 s. Its per-ROI features change only through edge crossings.
  - The one per-ROI leak it plausibly has (the edge deficit) is confined to about 5–10 % of pairs. Even if the classifier caught those pairs perfectly, accuracy would rise by roughly 0.025–0.05.
  - The positive control (uniform dither) shows power against a different kind of leak: broken interval floors, AUC 0.647 on one count.
  - A plausible leak is invisible to the gate entirely. Surrogate seeds come from `(recording_id, stream, cell_id, draw)` plus the ROI, so **the same ROI's fast and slow trains get independent offsets**. Any model that sees both streams can win on within-ROI fast/slow alignment, with no coordination at all. The per-stream classifier can't see this.
  - So a PASS means "not detectable by this test", nothing more.
- **Suggested fix.**
  - Restate VIABLE as "no per-ROI, per-stream leak detectable".
  - Require the model tier to take one stream, or apply one offset per ROI to both streams.
  - List the aggregate (cells-mean) channel and the window-position channel as untested.
- **Verified:** yes (`draw_surrogates` key, `_roi_seed`, `surrogate_discriminator`).

**M2. The pair count and the chance of passing are undeclared, and the no-leak control has already come close to failing the pass rule.**
- **Location:** Leak "Pass at a *J*".
- **Issue.** Passing needs the upper bound below 0.55, and whether that is reachable depends on how many pairs there are. The page gives no count, and the tree's figures disagree: `probe_discriminator` says 543 pairs, `recording_identity` says 1,669 windows.
  - I simulated a surrogate with no leak at all through `sd._cv_correct` and a mouse bootstrap (44 mice):
    - About 1,680 pairs: passes about 98 %.
    - About 590 pairs: passes about 47–57 %.
  - On real fast data, the exchangeable real-vs-real comparison read 0.523 [0.491, 0.556] (`recording_identity.md`). Its 95 % upper bound already exceeds 0.55, on half the pairs.
  - The negative control can only flag machinery bugs: orientation is randomised, so the P-value is exact by construction. So nothing shows the gate **can pass** on these data.
- **Suggested fix.**
  - Declare how windows are built and how many pairs each stream gives.
  - State the probability that a leak-free surrogate passes.
  - Add a can-pass control: real-vs-real judged by the candidate's own pass rule.
- **Verified:** yes (simulation plus the cited table).

**M3. "Confirmatory" needs a disclosure of what was already known at the declared cells.**
- **Location:** *Why rigid shift*; *What this run cannot claim*; the displacement table.
- **Issue.**
  - The grid is anchored on a value picked from these same windows: "the largest leak-free value". So the page's author knew that 2.5 s (and the grid beyond it) were not leak-free in the exploratory run.
  - Exploratory destruction results at 2.5 s and 5.0 s exist on disk, and the page doesn't say whether anyone read them.
  - "Fresh randomness" refreshes surrogate draws and folds, not the real-window features.
  - B3's arithmetic plus this selection makes a fast FAIL the expected result before the run.
- **Suggested fix.** Add a disclosure like `recording_identity`'s: which exploratory outcomes at these cells were seen, by whom, before signing. Report the result as a re-run under a fixed rule of cells whose exploratory outcomes were known.
- **Verified:** partly. Page text only; I deliberately didn't open the outcomes.

**M4. Verdicts pool across groups (FOUNDATIONS §9).**
- **Location:** Data; every gate.
- **Issue.**
  - §9: "a pooled across-group number … is not admissible on its own."
  - Only the zero-event share is reported per group.
  - `recording_identity` found DI baselines the least stationary (0.73–0.76 vs 0.54–0.65 in slow).
  - The destruction twins draw rates pooled across all groups (`prepare_stream`).
  - A group-concentrated leak or count loss can pass pooled.
- **Suggested fix.** Per-group gating is underpowered at 9–13 mice per group. Instead, report per-group accuracy, count change and zero-event share next to every pooled verdict, and declare now which per-group reading turns VIABLE into NARROWED.
- **Verified:** yes.

**M5. Destruction runs on one synthetic recording, so it licenses nothing "on these data".**
- **Location:** *Destruction*; "If no … on these data"; STOPPED "a result about the data".
- **Issue.**
  - It uses one twin per participation level: median ROI count and length, counts drawn from pooled rates, a stationary floor-renewal background, and planted events in exact synchrony with 1-frame jitter.
  - "Visible" means `before > 0` from that single twin.
  - "Retained" is a point ratio over an undeclared number of draws. The page says "every bound below is Bonferroni-widened", but no bound exists for destruction.
- **Suggested fix.**
  - Word the claim as "removes planted zero-lag synchrony in a synthetic twin sized like the stream".
  - Declare the draw count and the number of twin seeds, and require several twin seeds with an interval.
  - Remove "on these data" from the destruction arm.
- **Verified:** yes (`destruction_twins`, `prepare_stream`, `destruction`).

**M6. STOPPED overreaches.**
- **Location:** "So a STOP on rigid shift stops the goal"; the STOPPED row.
- **Issue.**
  - Joint-ISI is "unmeasured, not failed" (its own todo), under Tony's 2026-09-10 ruling that no candidate is pruned. Stopping the goal on rigid shift alone is a pruning decision, and the page doesn't record it as amending that ruling.
  - A FAIL caused by the unwrapped edge is an implementation artifact that padding would fix (B1), not a property of the preparation.
- **Suggested fix.**
  - Have STOPPED record which gate failed and whether the cause is fixable (edge or instrument) or intrinsic (no *J* both leak-free and destructive).
  - Only the intrinsic cause stops the goal.
  - State explicitly that joint-ISI is dropped by Tony's decision.
- **Verified:** yes.

**M7. Nothing bounds *J* from above for cross-ROI structure that isn't coordination.**
- **Location:** The question; the displacements.
- **Issue.**
  - Destruction rewards larger *J*, and the per-ROI leak test is blind across ROIs.
  - At 5.0 s or 5.6 s, rigid shift removes all cross-ROI structure shorter than about *J*.
  - A model trained against it learns 1–5 s co-modulation as "real", which contradicts the page's own 1.0 s definition. The displacement-floor todo asks for a ceiling as well.
- **Suggested fix.** Caveat any VIABLE at the largest *J* as "coordination at timescales up to *J*", or declare a ceiling criterion.
- **Verified:** yes (argument plus the todo).

**M8. The count gate measures the wrong thing for the tube foot gun, and the aggregate test is missing.**
- **Location:** The VIABLE/NARROWED commitments.
- **Issue.**
  - The tube todo's closing condition is an aggregate-channel (cells-mean) leak test passed before the model tier. This run doesn't include one.
  - "Normalise the count across ROIs away" doesn't remove a deficit that is local in time at the generation start.
- **Suggested fix.** Keep the aggregate-channel test as a precondition of the model tier, or pad the generation window (B1).
- **Verified:** yes.

**M9. The negative-control rule (4 of 20 seeds) is valid but can't fail except through a code defect.**
- **Location:** Leak, negative control.
- **Issue.**
  - Pairing is fixed by window order, and only the orientation flips and folds change with the seed.
  - The observed orientation is one draw from the permutation null, so the P-value is exact given the data. The 7.5 % and 1.6 % figures are therefore right.
  - But the control can only catch machinery defects, not anything about the data. That is fine if labelled, and misleading if read as evidence the gate works (see M2).
- **Suggested fix.** Label it a machinery check.
- **Verified:** yes (`negative_control_pairs`, `forced_choice`).

## Minor

**m1. Undefined quantities.**
- Whether the "upper 98.3 % bound" is one-sided or two-sided. `mouse_bootstrap` hard-codes 95 % two-sided, so "unchanged" can't hold.
- Surrogate draws per recording for the leak and count gates.
- Where windows sit relative to the generation edges.
- The number of destruction draws and twin seeds.
- What "mean real count" is taken over.

Fix: declare each. Verified: yes.

**m2. Unjustified constants.** Retained 0.25, ±2 % counts, do-nothing 0.9, homogeneous 0.1, and the 60 s window (the code's own docstring says "⚠ Inherited … not justified"). They were accepted, but the page never says why. Fix: one line of rationale each. Verified: yes.

**m3. The uniform-dither positive control may void slow at 1.4 s.** The slow interval floor is about 2.8–3.2 s, so dithering by ±1.4 s rarely breaks it. Fix: note the risk, or say what happens then. Verified: no, argument only.

**m4. The 0.64 slow within-recording result does not transfer to rigid shift, so I did not escalate it.** That chimera swaps in a **random ROI** from a different window. Rigid shift keeps more than 90 % of each ROI's own window. The nonstationarity risk for rigid shift is small. Fix: none needed; noted so the next reader doesn't escalate it either. Verified: yes.

## What I checked
- The artifact in full.
- `surrogate_discriminator.py`; the destruction functions and constants in `surrogate_stats.py`; `rigid_shift`, `uniform_dither`, `edge_thinning`, `do_nothing` and `homogeneous_resample` in `surrogates.py`.
- `assess_coactivity`; `build_surrogate_screen.prepare_stream` and `params_for`; `probe_discriminator.py`; `mouse_bootstrap` in `measure_recording_identity.py`.
- FOUNDATIONS §9; `recording_identity.md`; the saturation and circularity passages of the 2026-09-11 review.
- These todos: rigid-shift edge, tube foot gun, count preservation, displacement floor, exit criterion, joint-ISI.
- Three walk-throughs:
  - A leak-free classifier through the pass rule.
  - `edge_thinning` and rigid shift (numpy stand-in) through the count statistic.
  - Homogeneous resample through the real destruction path at a 1.0 s bin.
