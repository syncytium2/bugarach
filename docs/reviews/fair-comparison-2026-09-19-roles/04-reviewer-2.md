<!-- Verbatim role report, except that this machine's absolute paths are written as %USERPROFILE% and <darkroom> (the repository is public). The unedited original is in <darkroom>/bugarach/2026-09-18-fair-comparison-run/report/review-roles/. -->

GRANT 4 ok — Read, Grep, Glob, Bash (I also hold SubagentHandback, the report channel. I hold no editing tools.)

# Role 4 (Reviewer 2): findings on the fair-comparison report

**Artifact:** `%USERPROFILE%\bugarach\bugarach-worktrees\fair-comparison-report\docs\learned\tuned_vs_coact\fair_comparison_2026_09_18\report.html`. Its blob hash matches 76c3270. The worktree HEAD is 805fee9.

**What I did:**
- Read the whole page and every render (figures 1–8, tables 1–3).
- Checked the page against `results.json`, `meta.json`, `crowded_check.json`, `tools/crowded_check_fair_comparison.py`, `tools/search_all_settings.py`, `src/bugarach/bench.py`, `src/bugarach/score.py` and the tuning tool's `train` and `decode` code.
- Ran three small ablations through the run's own scoring path (`search_all_settings._job`, `bench.pool_scores`).
  - They first reproduced the run's numbers exactly: CoactDetect fold 0 at 0.7562, fold 3 at 0.7352; SCE fold 0 at 0.7886, fold 3 (budget selection) at 0.7648; SCE's crowded scores 0.6557 and 0.7027.
  - Scratch output is in `...\scratchpad\mb\role-4\bench_ablate.txt`. No repo file was touched.

Fold numbers below use the run's 0–3 numbering unless I write "page fold". The page numbers folds 1–4.

## Findings

Each finding gives: location · issue · severity · suggested fix · verified against a source.

**1. Section 6 headline ("No net is ahead of CoactDetect"), the answer at the top, and section 7.1 ("The nets were not checked… merge gap is fixed")**
- **Issue:** The headline rests on a post-processing difference the page never states. The nets merge calls with a fixed 2 s gap (`pick_threshold`/`decode` default of 20 frames at 0.1 s). CoactDetect uses 8 s, which is the top of its grid.
- I re-scored CoactDetect's chosen settings with only the merge gap changed to 2 s:
  - Held-out F1 falls from 0.748 to 0.7315 (per fold 0.7384, 0.7226, 0.7475, 0.7175).
  - At that matched gap, chorus_norm (0.7543, 0.7315, 0.7606, 0.7180) leads CoactDetect in **4 of 4 folds**, by +0.0005 to +0.016, mean +0.010.
- The 8 s gap is worth about 0.017 F1 to CoactDetect. That is more than twice chorus_norm's 0.007 deficit.
- The page presents the fixed gap as something that protects the nets from suspicion. In fact it is an advantage the coded side had and the nets did not. Goal 1's own page (row 86) also flags that an 8 s gap fuses crowded events planted 6 s apart.
- **Severity:** blocking.
- **Fix:** State both merge gaps. Then do one of the following:
  - tune the nets' merge gap (decode-only, no retraining needed); or
  - score both sides at a common gap; or
  - at minimum, report this ablation.

  Soften the headline to something like: "chorus_norm and CoactDetect are within about 0.01 F1, and which one leads depends on the merge gap."

  Caveat on my ablation: CoactDetect was not re-tuned at 2 s, and the nets were not tried at 8 s.
- **Verified:** yes (ablation reproduces the run's own numbers first).

**2. Section 6 ("…its choices fail goal 1's crowded veto in 7 of 8 cases"), section 7.1 ("Binned SCE's 30 s merge gap does not [pass]"), and the answer at the top ("a setting that goal 1… has already ruled out")**
- **Issue:** The veto did **not** refuse every 30 s choice.
  - In fold 3 of the budget selection, SCE's 30 s choice passes (crowded 0.7027 against a floor of 0.694).
  - Its held-out F1 is 0.765 against CoactDetect's 0.735 on the same fold. That is an admissible SCE result 0.030 ahead of CoactDetect.
  - Figure 7 shows it: the one solid SCE dot in the budget panel sits right of every CoactDetect dot.
- The prose never mentions this case. It also says goal 1 "ruled out" the setting, when goal 1's rule passes it in that fold.
- The conclusion is right, but for a reason the page does not show. I ablated the merge gap on the bench's held-out recordings:
  - SCE fold 0 falls from 0.789 to 0.682 at 16 s and to 0.603 at 8 s.
  - SCE fold 3 (budget selection) falls from 0.765 to 0.685 at 8 s.
  - On crowded recordings the same choices at 8 s score 0.776 and 0.840, which passes easily.
- So the lead really is the merge gap, and the veto is a leaky proxy for it.
- **Severity:** blocking. The second headline claim is supported by evidence that is contradicted in one fold, and the decisive evidence is absent.
- **Fix:**
  - Replace or supplement the veto argument with the merge-gap ablation: SCE's own choice at 8 s or 16 s, scored on the held-out bench recordings, against CoactDetect.
  - Name the fold that passes, and say the veto missed it.
  - Drop "already ruled out".
- **Verified:** yes.

**3. Section 7.1, table 3, and the "not admissible" label in figure 7 and table 2**
- **Issue:** The veto's threshold is presented as settled. `bench.MAX_CROWDED_DROP`'s own docstring says: "0.02 is a judgement, not a measurement… Tony has not signed it."
- The crowded check pools only 12 recordings per background and reports no uncertainty. The verdicts that matter sit at drops of 0.012 (pass) and 0.031 (fail).
- The page also does not say the veto was added on 2026-09-17 22:23 (d181a96). That is before this run launched, yet the run's declaration never mentions it.
  - This fact helps the page: the rule was not invented after seeing the result.
  - It should still say the check was run only after the result was known, when the other workstation (WSMIP065) pointed at the top-of-grid merge gaps.
- **Severity:** major.
- **Fix:** State that 0.02 is an unsigned judgement. Give a paired bootstrap interval on each crowded difference, or at least the per-background values. Give the timeline: the veto predates the run, the run omitted it, and the check was triggered by seeing the result.
- **Verified:** yes.

**4. The "not admissible" marker in figure 7 and table 2 for LoCo, rate+context and SPIKE-synch under the budget**
- **Issue:** One hollow marker carries three different meanings. None of these choices is a merge-gap artifact:
  - LoCo under the budget keeps the 8 s gap its reference already has. Only its threshold moved (99.9 to 99.99).
  - rate+context under the budget cut its gap to 3 s.
  - SPIKE-synch has no merge gap.
  - locust is hollow because the budget refused every candidate, yet it *passes* the veto.
- These choices fail the veto simply because the budget forced stricter settings that lose recall everywhere. The veto was designed to catch the opposite: a setting that wins on the bench and loses on crowded recordings.
- The reader sees "fails goal 1's crowded veto" and infers the SCE-style artifact.
- **Severity:** major.
- **Fix:** Use distinct markers, or add a caption sentence saying these failures are general losses, not the merge artifact. Mark locust as "no admissible setting", not as a veto failure.
- **Verified:** yes.

**5. The veto reference rule (section 7.1; `crowded_check_fair_comparison.py`)**
- **Issue:** The page calls this "goal 1's crowded veto", but the reference differs from goal 1's.
  - Goal 1's search deliberately references the *shipped* `OPERATING_POINTS` for every detector. `search_all_settings.py` says so at about line 876: "A veto is only as honest as its reference."
  - This check uses goal 1's sliding base for CoactDetect and LoCo.
- I checked against goal 1's shipped crowded scores (CoactDetect 0.808, LoCo 0.816). CoactDetect still passes, and LoCo under the budget (0.771) still fails. So no verdict flips, but the page should say so.
- Separately, a relative veto sets a detector-specific bar. SPIKE-synch's reference is 0.462, so its choices on F1 alone pass by +0.33, which is trivially easy. SCE's reference is 0.714, while CoactDetect's is 0.826.
- The stronger, reference-free argument is absolute, and the page does not make it: SCE's choices score 0.656–0.684 on crowded recordings, against CoactDetect's 0.820–0.837.
- **Severity:** minor.
- **Fix:** Name the departure from goal 1's rule and say the verdicts are unchanged under it. Add the absolute crowded comparison.
- **Verified:** yes (goal 1 numbers taken from `docs/goals/coded-detector-optimization.md` row 78).

**6. Section 6, "Tuning barely moved the nets"**
- **Issue:** Two of the four nets contradict it. The test had power; it moved, and the prose reports it as if it had not.
  - line_length, tuned minus untuned, per fold: +0.047, +0.041, −0.016, +0.056. It rose in 3 of 4 folds.
  - chorus_gain_norm, per fold: +0.042, +0.066, −0.128, −0.005. The mean of −0.006 is one failed refit (F1 0.125) cancelling two real gains.
- Scale is also inconsistent: +0.032 is called "barely", while SCE's +0.023 is "first place".
- The page never says which selection the numbers use. They are from F1 alone. Under the budget, chorus_norm is −0.020 (t = −2.0) and tube −0.035. That comparison is suspect in itself, because the untuned threshold was chosen on F1 alone.
- In 2 of the 16 net-fold choices on F1 alone the untuned configuration won outright, so those folds contribute exact zeros.
- **Severity:** major.
- **Fix:**
  - Report per-fold values, and chorus_gain_norm with and without the failed refit.
  - Say "tuning lifted line_length by about 0.03–0.05 in three folds, and left chorus_norm and tube where they were".
  - Name the selection.
  - Scope the claim to "this 24-draw random search".
- **Verified:** yes (`results.json` comparisons).

**7. Section 6 ("The earlier comparison's lead… came from comparing untuned nets against a coded side tuned on one knob; with both sides tuned, it is gone") and the question at the top**
- **Issue:** This causal attribution is confounded, and the run cannot test it.
- The earlier comparison ran on the retired **home spec** simulator; this run uses the bench (`meta.declaration.simulation = "bench"`). There, CoactDetect scored 0.645. Here it scores 0.748, in sliding mode from goal 1, not binned.
- Three things changed at once: the simulator, CoactDetect's window mode, and tuning.
- The page's own data argue against tuning as the cause: the nets barely moved, and on this bench the *untuned* chorus_norm (mean 0.736) is already behind CoactDetect.
- The run has no arm with the coded side tuned on one knob.
- **Severity:** major.
- **Fix:** Say the earlier lead does not reappear on the bench. Say this run cannot separate the simulator change, goal 1's sliding base and tuning as the cause. Mention the home spec in "The question".
- **Verified:** yes (`docs/goals/learned-model-family.md` lines 61–65 and 138).

**8. Figure 8 caption ("no dot is to the right of it")**
- **Issue:** False. chorus_gain_norm on F1 alone is +0.00006 in fold 0 and +0.0004 in fold 1. The sentence is hard-coded in `build_fair_comparison_report.py` around line 792 rather than computed.
- chorus_gain_norm therefore *ties* CoactDetect in 2 of 4 folds. That is a more informative fact than its mean of −0.045.
- **Severity:** minor. It is a factual error in a caption.
- **Fix:** Compute the statement from the data, or say "no dot is more than 0.001 right of it; chorus_gain_norm ties CoactDetect in two folds".
- **Verified:** yes.

**9. Section 2, the hit definition ("A call counts as a hit if it lands within 2.5 s of a planted event")**
- **Issue:** This does not match the scorer. `score_detections` matches **spans**: "A detection whose span contains the planted event matches at any tolerance."
- That rule is the mechanism behind the merge artifact the page dismisses SCE for. A merged 30 s span is a hit wherever the event falls inside it.
- It is also why the failed chorus_gain_norm refit scores precision 1.0 at recall 0.067. That is one recording-long call per recording, and each one counts as a hit.
- The 2.5 s tolerance is never justified on the page. `score.TOL_SEC` explains it as the plateau of the tolerance curve.
- **Severity:** major.
- **Fix:** Define a hit as "the call's span, widened by 2.5 s, contains a planted event". Add one line on why 2.5 s was chosen, and one on why wide spans are rewarded.
- **Verified:** yes.

**10. Section 4 ("tunes both sides with the same care") and section 8 (Limits)**
- **Issue:** The training data are asymmetric, and this is not listed as a limit.
  - Each net fit sees 10 of the 72 training recordings, and its threshold is picked on **2** recordings (`N_TRAIN = 10`; figure 4B shows about 5 seeds fitted per fold).
  - Every coded setting, threshold included, is chosen on all 72.
- A 2-recording threshold is a likely contributor to:
  - the tube refit that made no calls at all;
  - net choices under the budget exceeding the budget on held-out data.
- **Severity:** major.
- **Fix:** Add it to the Limits section. Do not say "the same care" without that qualifier.
- **Verified:** yes (tuning tool constants; figure 4).

**11. Section 7.2 and table 3's "also" column (budget exceedance reported for coded detectors only)**
- **Issue:** Budget exceedance on held-out data is reported for CoactDetect (1 of 4) and locust (4 of 4), but not for the nets.
- By my approximate count against `meta.budgets`, 25 of 80 net refits under the budget exceed their fold's budget on the held-out fold. tube is the worst: 5 of 5 in fold 2.
- If anything this flatters the nets, so the headline is not threatened. But the reporting is one-sided.
- The page also does not say the budget operates on counts of about 10 calls per hour, where Poisson noise is roughly ±3. Nor does it say that 1.6 is a "declared margin" with no stated justification (goal 2 page, decision 4).
- **Severity:** minor.
- **Fix:** Report net exceedance too. Justify 1.6, or label it a declared judgement, and give the underlying counts.
- **Verified:** partly (my own count; the net null rates are approximate).

**12. Table 2 (locust and SPIKE-synch under the budget) and the section 6 bullet "Under the budget, three coded detectors fall well behind…"**
- **Issue:** locust under the budget is not a result. The search fell back to its starting point, which was 510 probe calls per hour in the quiet background against a budget of about 16. Yet it gets a mean of 0.549 and **t = −37.5**, and the bullet says it "falls behind".
- The same bullet omits LoCo under the budget (−0.059, not admissible in 4 of 4).
- The phrase "either refused by the veto or not admissible at all" is circular: being refused by the veto *is* being not admissible.
- **Severity:** minor.
- **Fix:** Show "no admissible setting" in place of locust's mean and t. Include LoCo in the bullet. Reword.
- **Verified:** yes.

**13. The "How much the t values can carry" paragraph, and t values quoted in the headline and table 2**
- **Issue:** The caveat is good, but the page still leads with t = −13.0 and prints t = −67.5.
- The Nadeau–Bengio correction is one line of arithmetic. For k = 4 folds with a test-to-train ratio of 1/3, it scales every t by about 0.65.
- The page says the replicate "is the real check" but deliberately does not quote it, even though the replicate had finished 28 minutes before this page was built. A headline stated flatly should then be conditional.
- **Severity:** minor.
- **Fix:** Apply the correction, or drop t from the headline sentences. Make the headline conditional on the replicate, or cite the replicate's page.
- **Verified:** yes (build and replicate times are on the page).

**14. Section 6, "Its choices pass goal 1's crowded veto in 8 of 8 cases", and SCE's "7 of 8"**
- **Issue:** These counts treat duplicates as independent checks.
  - CoactDetect's two selections are identical, and folds 0 and 2 chose the same settings. That is **3 distinct settings**.
  - SCE has 3 distinct settings, of which 2 fail.
- **Severity:** minor.
- **Fix:** Count distinct settings, or say "4 folds × 2 selections, 3 distinct settings".
- **Verified:** yes.

**15. Section 7.3 heading ("Refits that failed to train") and the tube case**
- **Issue:** The tube refit (page fold 1, seed 4) has `failed_training_signature: false`, recall 0, precision undefined, and threshold index 35. It made **no calls**, which is consistent with a threshold picked too high on 2 recordings rather than a failed fit.
- chorus_gain_norm's "predicts nearly everywhere" is correct, but the reader cannot check it. Its record (recall 0.067, precision 1.0, 24 hits in 24 recordings) is exactly one call per recording.
- The 0.2 cut is not justified. It does sit in a gap: every other refit is at least 0.51.
- **Severity:** minor.
- **Fix:** Retitle the section "Refits below 0.2 F1". Give each refit's signature. Say the 0.2 cut falls in an empty gap of the distribution.
- **Verified:** yes.

**16. Section 3 ("tube… kept as a control: it tied CoactDetect untuned")**
- **Issue:** The tie was measured on the home spec. On this bench, untuned tube scores 0.629 against CoactDetect's 0.748, so the control's premise does not hold here.
- **Severity:** minor.
- **Fix:** Say the tie was on the retired simulator, and that tube no longer ties on the bench.
- **Verified:** yes.

**17. Constants not justified on the page**
- **Issue:**
  - The 1.6 margin, the 0.02 drop and the 2.5 s tolerance are covered in findings 3, 9 and 11.
  - Also unexplained: 10 fitting recordings and 2 threshold recordings; 24 configurations; 3 and 5 training seeds; 12 crowded recordings per background; the probe at 0.06 Hz.
- **Severity:** minor.
- **Fix:** Give one clause each of rationale, or point to the owning docstring.
- **Verified:** yes.

## What I checked that held up
- Table 2 and table 3 numbers match `results.json` and `crowded_check.json`.
- The fold-defect story and figure 4 are consistent with the run.
- CoactDetect's two selections really are identical.
- My ablations reproduce the run's held-out and crowded scores exactly, so the harness is the run's own.
- SCE's lead really is carried by the merge gap. This is verified by ablation, just not by the evidence the page cites.

## Files
- Artifact: `%USERPROFILE%\bugarach\bugarach-worktrees\fair-comparison-report\docs\learned\tuned_vs_coact\fair_comparison_2026_09_18\report.html`
- Builder (the hard-coded caption is at about line 792; claim text at lines 643 and 777–821): `%USERPROFILE%\bugarach\bugarach-worktrees\fair-comparison-report\tools\build_fair_comparison_report.py`
- Veto constant and its docstring: `%USERPROFILE%\bugarach\bugarach-worktrees\fair-comparison-report\src\bugarach\bench.py` (`MAX_CROWDED_DROP`, about line 1575)
- Span-matching rule: `%USERPROFILE%\bugarach\bugarach-worktrees\fair-comparison-report\src\bugarach\score.py` (`score_detections`)
- Nets' fixed merge gap: `%USERPROFILE%\bugarach\bugarach-worktrees\tune-bench-comparison\src\bugarach\learn\train.py` (`pick_threshold`, `merge_gap_frames=20`)
- Ablation output: `%USERPROFILE%\AppData\Local\Temp\claude\c--Users-<user>-bugarach-bugarach\0c979457-501e-4b3d-9c4b-21e394823cf5\scratchpad\mb\role-4\bench_ablate.txt`
