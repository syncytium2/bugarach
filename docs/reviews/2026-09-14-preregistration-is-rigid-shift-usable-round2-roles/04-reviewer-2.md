GRANT 4 MISMATCH — missing Grep, Glob; holds no forbidden tools (Read and Bash only; no Edit, Write or NotebookEdit)

**Run note:** the grant gap didn't limit the review. I searched with `grep` through Bash instead. This was a blind pass: I opened no earlier review of this page and read no rigid_shift results from the overnight run. Every number below comes from built-in synthetic data, mostly using the repo's own `surrogate_discriminator`, `surrogate_stats.destruction` and `destruction_twins`. Where Elephant was needed I used numpy stand-ins for rigid shift, uniform dither and homogeneous resample, run in-process with `python -c`. No files were written, and the scratch folder `<review-session-scratchpad>/r2role04/` is empty.

Artifact: `docs/proposals/2026-09-14-preregistration-is-rigid-shift-usable.md` (blob 2c9813d, confirmed).

## Findings

Each row: **location · issue · severity · suggested fix · verified**

**1. Leak gate, and "What a PASS may claim" (the "coordination-blind" wording)**
- **Issue:** The classifier is not blind to coordination under rigid shift. The edge-band features count onsets within 5 s of each 60 s window edge, and they are pooled by median and sd over ROIs. A shift of about 5 s moves the members of one event in and out of that band independently. The median over ROIs then changes, so the classifier is seeing coordination being removed.
- **Synthetic test:** 40 recordings, 34 ROIs, background 3 onsets/min, one event per minute with 50 % participation, interior windows only.
  - Rigid shift at 5.0 s read accuracy 0.578, 0.602 and 0.617 over three repeats.
  - The same data with the edge-band columns removed read 0.502, 0.512 and 0.506.
  - With no planted coordination it read 0.46–0.50.
  - The can-pass check (two shifts against each other) read 0.461, because neither side has coordination left, so it cannot catch this.
- **Consequence:** a decided leak FAIL at the largest J can mean the surrogate did its job. That wrong FAIL can feed NARROWED or STOPPED.
- **Severity:** blocking.
- **Fix:** On interior windows the edge bands have nothing left to detect: the only edge loss is at the recording edges, which are excluded. So either leave the edge-band columns out of the gating statistic and report them beside it, or add a control: run the same leak pipeline on planted and unplanted twins under rigid shift at each J. If the planted twins read higher, the cell's leak FAIL is not decided.
- **Verified:** yes (synthetic).

**2. "The outcome, completed" (FAIL definition)**
- **Issue:** "Decided" is defined only for the leak gate. The count and destruction gates have a pass rule but no decided-FAIL rule, so a non-pass there cannot be sorted into FAIL or UNDECIDED. Stream FAIL needs every cell FAIL, and STOPPED needs FAIL on both streams. The runner would have to invent the rule after seeing data.
- **Why it matters:** destruction is the realistic way to stop. In my stand-in run (34 ROIs, 1 s bin), rigid shift at 5.0 s kept a share of 0.32–0.33 at K = 3–4 with 50 % participation, and at 1.6 s it kept 0.4–0.75.
- **Severity:** blocking.
- **Fix:** Declare the rule now. Count: decided FAIL if the 96.67 % interval lies wholly outside ±2 %. Destruction: decided FAIL if the 1.67th percentile of retained share is above 0.25 at any gated K.
- **Verified:** yes (text, plus stand-in run).

**3. "Can-pass check"**
- **Issue:** One random draw can overrule the candidate in both directions. It turns a candidate PASS (bound already below 0.55) into UNDECIDED. It also turns a decided FAIL (lower bound above 0.55) into UNDECIDED, which removes a way to stop. It never adds information to a cell that is UNDECIDED anyway.
- **How close it sits to the line:** the recording-identity real-vs-real fast result, 0.523 [0.491, 0.556], would put a one-sided 98.33 % bound at about 0.55 even with roughly 1,500 interior pairs. So a perfect surrogate plausibly fails this check about one time in ten.
- **Other gaps:** it compares two shifts, so the displacement between the two sides is about twice that of real against one shift, and it cannot see the channel in the first finding.
- **Severity:** high.
- **Fix:** Make it a diagnostic label that applies only to cells that are otherwise UNDECIDED. Or use the median over several draw pairs, and never let it override a PASS or a decided FAIL.
- **Verified:** partly (the logic is certain; the one-in-ten figure is arithmetic from `docs/learned/recording_identity.md` interval widths).

**4. Outcome table**
- **Issue:** PASS on one stream with UNDECIDED or VOID on the other falls into "any other combination", which is UNRESOLVED with nothing read. PASS with FAIL, a worse result, reads NARROWED. The ordering is backwards.
- **A permanent dead end:** "An UNDECIDED stream is not rerun" and "does not stop the goal", so PASS with UNDECIDED can never resolve.
- **Severity:** high.
- **Fix:** PASS on one stream with any non-PASS on the other gives NARROWED, naming the passing stream. Then say what the goal does after UNRESOLVED caused by UNDECIDED.
- **Verified:** yes (text).

**5. "What STOPPED means"**
- **Issue:** "A FAIL traced to a fixable instrument … does not stop the goal" is a judgment made after the results, with no criterion. Any FAIL can be argued to be fixable; the first finding is itself such an argument. This is the same post-hoc rule-writing the page exists to prevent.
- **A second gap:** a cell that passes leak and destruction but decidedly fails count counts as not intrinsic, so it can't stop the goal either.
- **Severity:** high.
- **Fix:** List now, closed, what counts as an instrument defect (a control invalid, the saturation table void). Everything else that meets the FAIL rule is intrinsic.
- **Verified:** yes (text).

**6. Leak gate and count gate on interior windows only, versus "VIABLE — the goal moves to the model tier"**
- **Issue:** On interior windows, rigid shift changes per-ROI features and occupied-frame counts only when onsets cross window boundaries, and those crossings are symmetric. Both gates are close to guaranteed passes by construction; no-coordination synthetic data read 0.46–0.52. The one leak rigid shift is known to have, the holes at the recording edges, lives in the first and last windows, which no longer gate. The harm lives in the set that isn't scored.
- **Severity:** high.
- **Fix:** Make VIABLE and NARROWED commit the model tier to interior windows only, or to rerunning both gates on whatever windows it trains on. The count-gate text says this only for counts.
- **Verified:** yes (synthetic plus code reading).

**7. "Groups"**
- **Issue:** Narrowing is triggered by a point estimate alone, with no test.
  - A group of 17–25 recordings gives about 290–425 interior pairs, a standard error of about 0.024–0.029, and roughly a 2–5 % chance per group of reading ≥ 0.55 by chance. Across four groups that is about 10–15 % per stream and cell.
  - The rule never says which J's estimate counts when several cells pass.
  - It doesn't say how "NARROWED for that stream" combines with the table, for example fast narrowed by a group while slow FAILs.
- **Severity:** medium.
- **Fix:** Narrow only if the group's lower bound is above 0.55. Report a group whose interval straddles 0.55 as undecided for that group. Name the cell, and add the combination rule.
- **Verified:** partly (arithmetic, not simulated).

**8. "The largest J: a pass there is reported as removing 'coordination up to J'"**
- **Issue:** Overreach. The gate scores 1.0 s bins (and 2.0 s bins on slow), not "up to J". Two ROIs shifted independently by ±J end up with a relative offset spread over ±2J, so structure at timescales near J is only partly removed. In the stand-in run, 5.0 s still kept a share of 0.33 at a 1 s bin for large events.
- **Severity:** medium.
- **Fix:** Say "removes coincidence in the 1.0 s bin (2.0 s on slow) in synthetic twins at the gated K", and give J separately.
- **Verified:** yes (stand-in run).

**9. "Gated K", the saturation rule**
- **Issue:** The rule excludes exactly the K at which the shifted event almost surely still forms a cluster of K or more, meaning the surrogate did not remove it.
  - On slow at the 2.0 s bin with J = 1.4 s, 34 ROIs and 50 % participation, the chance the largest bin reaches K is 1.00 at every K: nothing is gated.
  - At 20 % participation, K = 6 is still gated, so the cell reads as passable while the large events went untested.
  - "No K gated → VOID", combined with "rerun changing only the instrument whose control failed", names no instrument to change.
- **Severity:** medium.
- **Fix:** Report retained share at the excluded K beside the result. Scope any PASS to the gated K and participation levels. A participation level with no gated K should read "not tested", not VOID.
- **Verified:** yes (simulation of the chance the largest bin reaches K).

**10. Leak positive control ("uniform dither at the same J")**
- **Issue:** How strong this control is depends on J and on the data, not on the candidate. In a sparse synthetic set (3 onsets/min) uniform dither at 1.6 s read 0.572, so the lower bound would fall below 0.55 and the cell would be VOID. It only shows the classifier can see changes in interval distributions, which is not a kind of leak rigid shift can have. The VOID-rerun rule again has no instrument to change.
- **Severity:** medium.
- **Fix:** Use one fixed positive control at a strength already shown to be detected (the recording-identity run's 30 % thinning), the same for every cell. Keep uniform dither at J as a reported number.
- **Verified:** partly (synthetic, not real data).

**11. Cossart "tied by grid position"**
- **Issue:** Cossart's frame interval is 0.093–0.119 s (59 recordings, 32 subjects, from `docs/learned/assessment_cossart.json`). So 4 frames is 0.37–0.48 s, a quarter to a third of the lab's 1.6 s, and it varies by recording. VIABLE's Cossart check is made at a much smaller physical displacement than the claim it supports. Cossart's pair count and whether it gets its own can-pass check are also unstated.
- **Severity:** medium.
- **Fix:** Report Cossart J in seconds per recording. Word VIABLE as "Cossart does not leak at about 0.4 s", not as support for the lab's J.
- **Verified:** yes.

**12. Destruction "Visible: the excess before the surrogate is at least 1.0"**
- **Issue:** An undefined quantity with an unjustified constant. It doesn't say whether "excess" is the planted twin's own excess or planted minus unplanted (the code divides by the latter), and it gives no unit (co-active ROI·events per minute). At 20 % participation, K = 8 was "visible" (2.9–5.0) only through background coincidences, since 7 participants is fewer than 8. The rule still requires a pass at every gated K, so a noisy ratio can decide the cell.
- **Severity:** medium–low.
- **Fix:** Name the quantity and its unit, justify 1.0, and consider gating only K ≤ the number of participants.
- **Verified:** yes (stand-in run).

**13. Leak gate, "interior window" definition**
- **Issue:** I walked through the edge holes. Rigid shift empties the first J after the recording start (positive shifts) and the last J before its end (negative shifts). With whole 60 s windows and the trailing part-window dropped (as `probe_discriminator.analysis_windows` does), both holes stay inside the first and last whole windows for any J up to 5.6 s, so the leak is removed. But `surrogates._tiles`, used by `edge_thinning`, keeps the partial last tile. If "last window" is read as that partial tile, the end hole reaches an interior window whenever the leftover part is shorter than J: about 9 % of recordings at 5.6 s.
- **Severity:** low.
- **Fix:** Define interior windows as whole windows only, trailing part dropped, then excluding the first and last.
- **Verified:** yes (code).

**14. `freeze_half` on homogeneous resample (the graded destruction control)**
- **Issue:** In the stand-in run (34 ROIs, 1 s bin) it read 0.27–0.57 at K = 4, against 0.00–0.03 for homogeneous resample, so it is valid when the measure works. It would catch a measure that ignores how many ROIs are in an event (that reads about 1.0 at 50 % participation). It cannot catch a bin that is too narrow for the shift, because homogeneous resample moves onsets across the whole window whatever the bin, and that was the defect that motivated this change.
  - The page doesn't say which participation level is read at K = 4.
  - It doesn't say whether the 0.10–0.90 range applies to a point estimate or a bound.
  - The frozen-ROI key `("freeze-half", p, k)` in `surrogate_stats.destruction` isn't salted with the run tag, and the "no key equals the 2026-09-11 scheme" test as described would not catch it.
- **Severity:** low.
- **Fix:** Name the participation level and the statistic, salt the key, and label the control "graded", not a bin check.
- **Verified:** yes (stand-in run plus code).

**15. `edge_thinning` count control at a fixed 5 s**
- **Result:** No defect. The derivation J/(2W) predicts a 4.17 % loss. Simulated occupied frames on interior windows lost 4.19 % (1 onset/min), 4.48 % (3/min), 5.64 % (bursty) and 5.66 % (20 onsets/min), so the control lands outside ±2 % and is valid.
- **Remaining wording gap:** "must fall outside" doesn't say point estimate or whole interval.
- **Severity:** low.
- **Fix:** Say "its 96.67 % interval lies wholly beyond −2 %".
- **Verified:** yes (simulation).

**16. Destruction bootstrap over 5 twins**
- **Issue:** A percentile bootstrap over 5 units understates spread by about 10 % (the √(4/5) factor) and has only 126 distinct resamples. All twins also share one ROI count, one length and one rate pool.
- **Severity:** low.
- **Fix:** State this beside the result, or use more twins.
- **Verified:** partly (arithmetic).

**17. Negative control wording**
- **Issue:** "Nothing decides on its P values" contradicts "void the stream if 4 or more of 20 seeds flag at α = 0.05". The binomial figures (7.5 % for three or more, 1.6 % for four or more) are correct. Orientation is re-drawn per seed, so the flags are close to independent.
- **Severity:** low.
- **Fix:** Reword to "decides only machinery validity".
- **Verified:** yes.

## What I checked and found sound
- The mapping from Bonferroni to one-sided percentiles.
- That the two one-sided tests at 0.05/3 match a 96.67 % interval.
- That the destruction gate can fail at small J; the stand-in run shows it would.
- That do-nothing and homogeneous resample are valid machinery and saturation guards.
- That STOPPED is reachable in principle, through destruction, once decided FAIL is defined for that gate.
