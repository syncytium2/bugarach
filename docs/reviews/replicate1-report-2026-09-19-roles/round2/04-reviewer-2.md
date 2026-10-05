GRANT 4 ok — Read, Grep, Glob, Bash

# Role 4 (Reviewer 2): adversarial review of `replicate1/report.html`

**Artifact reviewed:** `%USERPROFILE%\bugarach\bugarach-worktrees\replicate-report\docs\learned\tuned_vs_coact\replicate1\report.html` (built 09:02:55). I read the text of the HTML and the pictures in `...\scratchpad\shots\light_1100_00..10.png`. I checked claims against the generator, the two runs' archives, `score.py`, `performance.py`, `tune_learned_vs_coact.py`, `search_all_settings.py` and the handoff on branch `tune-bench-comparison`. My intermediates are under `...\scratchpad\mb2\role04\`, including the enlarged Figure 1 lane `fig1_lane.png`. I edited nothing.

**A finding about the run, not the artifact:** the rendered slices (09:01:38) are older than the built HTML (09:02:55). The section 9 paragraph under Figure 8 reads differently in the picture ("That is the pattern a short, fixed merge would produce…") than in the HTML ("…so this is a suspicion, not a finding"). My picture findings are against the older render and my text findings are against the build. Re-render before role 10 checks anything.

## Findings

Format: location · issue · severity · suggested fix · could I verify it against a source.

**1. Figure 9 and the "Where the gap is" paragraph in section 9 · BLOCKING**
- **Issue:** the three-way false-alarm split is not a split of false alarms.
  - `distractor_hits` counts **distractors covered by any call's span, matched calls included**. See `score.py` lines 267–271 ("Distractors that a detection landed on") and the project's own warning in `performance.py` `MAX_DISTRACTOR_RATE` (todo `2026-08-30-distractor-hits-counts-coverage-not-firing.md`).
  - "Anywhere else" is then `n_fa − hot_fa − distractor_hits` (`make_replicate_report.py` line 686). It goes **negative**: LoCo shows −0.70 and −0.67 per recording in the figure's own tooltips. The bar clips it to zero width, so LoCo's drawn total (about 5.7) overstates its real false alarms (about 5.0).
  - For wide-merge detectors the bias is systematic. I re-scored CoactDetect at the reference settings on the second draw's fold-0 held-out recordings (24 recordings): about 4.38 per recording are unmatched calls on a distractor and about 1.13 fall anywhere else. The report's formula gives −0.21 anywhere else on the same recordings.
  - The "on a distractor" bar sits near its ceiling for every detector (5.0–5.8 of 6 distractors per recording). So "about as often on distractors" is a comparison that could not have come out differently.
  - Consequence: "far more often anywhere else" (2.10 against 0.24) is unsupported. It inflates the nets' excess exactly where the merge asymmetry lives.
- **Fix:** re-score from `fa_times`. The scorer already computes `dup_times` and `n_duplicate`; the coded side is cheap to re-run, and the nets need their held-out outputs re-decoded. Until then, reduce Figure 9 to "in the dense stretch" against "outside it", and drop the distractor sentence.
- **Verified:** yes.

**2. Answer box, bullet 3 ("Chosen on F1 alone, the best learned model also trailed in both, −0.007 and −0.029") · BLOCKING**
- **Issue:** the second-draw number is a † mean. The best net there (chorus_gain_norm, 0.719†) and chorus_norm (0.690†) are both pulled down by collapsed refits.
  - In the folds where training worked, chorus_norm leads CoactDetect: +0.003, +0.003 and +0.007 (Figure 8B).
  - In the first draw, chorus_gain_norm ties at +0.000 in folds 0 and 1; its −0.153 comes from the flagged fold.
  - "The best learned model" is a different net in each draw, and it was picked on held-out means.
  - So "trailed" on F1 alone measures training failure, not skill.
- **Fix:** say that on F1 alone the chorus nets matched CoactDetect within about 0.01 wherever they trained, and that the means trail because of the failed refits in section 8. Name the net for each draw and mark the †.
- **Verified:** yes, from the report's own per-fold values.

**3. Generator assertions at `make_replicate_report.py` lines 836–843 · MAJOR**
- **Issue:** these are passing checks that assert the defect in finding 1. `assert all(other_g[k][0] > other_g[k][1] …)` ("the net's extra false alarms lie outside…") and `assert abs(dn - dc) <= 0.2 * dc` ("about as often on distractors") both run on the invalid quantity. The second one is close to saturation, so it cannot fail. They are green and they vouch for the sentence.
- **Fix:** replace these assertions; do not add new ones beside them. Rebase them on re-scored `fa_times`, and state in the record that they were flipped.
- **Verified:** yes.

**4. Figure 1 caption ("6 of its 6 unmatched calls fell on distractors") · MAJOR**
- **Issue:** the picture contradicts the caption. The enlarged lane shows red ✕ marks at about 18 minutes and about 37 minutes, far from any hollow triangle.
  - Re-scoring seed 2000 (quiet) gives 4 of 6. The false alarms at 1090.5 s and 2213.6 s touch no distractor.
  - The two distractors at 284.9 s and 542.3 s were covered by calls matched to planted events: the thick bars under the 8 s merge.
  - The caption prints `distractor_hits`, which is the same bug as finding 1.
- **Fix:** compute unmatched calls on a distractor directly, or reword to "all 6 distractors lie under a call".
- **Verified:** yes.

**5. Section 9, "Two draws … agreeing to within 0.005, are the stronger evidence", and answer box bullet 2 · MAJOR**
- **Issue:** this overweights one difference.
  - **The agreement is expected anyway.** The second draw's fold SD is 0.018, so the standard error of the between-draw difference is about 0.009, and agreeing within 0.005 is what chance alone would produce.
  - **0.005 is the smallest gap move on offer.** CoactDetect moved 0.000, so every gap move equals the net's own move: median 0.010, maximum 0.027. The untuned chorus_norm gap moved 0.018 and changed sign.
  - **The pooled 0.005 hides moves in opposite directions.** Split by background (my approximation, refits pooled), the budgeted gap moved about +0.018 at busy and about −0.008 at quiet.
  - **No test is reported.** The handoff specified a paired t on 3 degrees of freedom. It gives t ≈ 12.4 for the first draw (p ≈ 0.001) and t ≈ 2.8 for the second (p ≈ 0.07, not significant alone).
- **Fix:** report the paired t per draw. Say the claim rests on all 8 folds being negative plus the first draw's test. Recast 0.005 as "smaller than the typical between-draw move of 0.010".
- **Verified:** yes; the per-background figures are approximate.

**6. Section 9, "The nets moved more, and mostly in the same direction, which is a shift of the whole draw rather than independent noise" · MAJOR**
- **Issue:** Figure 10 refutes it. All four untuned nets moved up (+0.006 to +0.027), while the coded detectors moved mostly down (rate+context, binned SCE, locust, SPIKE-synch) and CoactDetect moved 0.000. A whole-draw shift would move both sides together. What the figure shows is a shift specific to the nets, so the net-minus-coded gaps, which are the headline quantity, drifted toward the nets by about 0.01–0.03 in the second draw.
- **Fix:** restate it that way and draw the consequence for the gaps.
- **Verified:** yes.

**7. "It is not in recall" (answer box bullet 4 and section 9) · MAJOR**
- **Issue:** the result is pooled across the design variable, background. From the score archives (refits pooled, approximate), chorus_gain_norm under the budget against CoactDetect:

| background | draw | chorus_gain_norm recall | CoactDetect recall |
|---|---|---|---|
| quiet | first | 0.929 | 0.938 |
| quiet | second | 0.873 | 0.932 |
| busy | first | 0.861 | 0.775 |
| busy | second | 0.820 | 0.750 |

  Precision is lower for the net at both backgrounds. "Not in recall" holds only after pooling.
- **Fix:** add a per-background table (F1, recall, precision) for the headline pair. Also add the recruitment-level breakdown that section 10 admits exists in the score files.
- **Verified:** yes (approximate).

**8. "One shared false-alarm budget" (answer box and section 5) · MAJOR**
- **Issue:** "shared" overstates neutrality.
  - CoactDetect's reference point is admissible by construction (1.0× against a 1.6× ceiling).
  - The ceilings count calls. Goal 1 found that "merging makes a detector call less, so the artifact looks cleaner on every false-alarm measure", and the nets' merge is fixed at 2 s (`merge_gap_frames = 20` in `train.py`).
  - The nets' budgeted threshold is carried onto refits calibrated differently. That costs F1 in both directions, but Table 3 counts only overshoot.
  - The handoff says the coded side got the larger tuning budget deliberately, so that a net win would be credible. Under that design, a net loss is the expected direction of bias and is weakly informative.
  - CoactDetect's starting point also comes from goal 1's search on 96 more recordings of the same bench (seeds 1–96; I checked they are disjoint from these seeds, so there is no leakage). The nets never had that prior tuning.
- **Fix:** say the budget is anchored to CoactDetect. Say the design was one-sided on purpose and that a trailing net is its expected bias.
- **Verified:** yes.

**9. Unjustified constants · MAJOR**
- **The 1.6 margin** is derived as binned CoactDetect's empty-recording limit over its measured rate (7.0/4.4). The report then applies it to both dense-stretch ceilings and to the sliding variant with no reason given, and no sensitivity is shown: does the headline survive at 1.3 or 2.0?
- **The nets' 2 s merge** is the report's own leading explanation of the gap and is never justified.
- **Also unexplained:** the 0.002 minimum gain in the coordinate search, 10 training plus 2 threshold recordings per fit, 3 against 5 training repeats, and the 2.5 s tolerance (justified in the `score.py` docstring but not in the report).
- **Fix:** give one sentence of reason for each, and a margin sensitivity check or an explicit "untested".
- **Verified:** yes, for the 1.6 derivation.

**10. The answer box leaves out training failure · MAJOR**
- **Issue:** a third of chorus_norm's scored inner fits collapsed to one call per recording (292 and 306 of 864), and so did 150 of 864 for chorus_gain_norm. The tuned net entries therefore measure the search with an unstable trainer, which is not the same as the architectures. The box names the merge and data asymmetries but not this one. Separately, "the net's output sat near a constant whatever the input" is inferred from F1 = 0.125 and never shown.
- **Fix:** add it to bullet 4. Show one collapsed output trace, or soften to "consistent with".
- **Verified:** partly.

**11. "One run cannot see this movement; two can" and "the same learned model moved by a median of 0.010" · minor**
- **Issue:** a single run's folds hold disjoint recordings, so fold-to-fold spread does see movement driven by the recordings, only confounded by shared training. Two draws give one difference per entry. The median is taken over 8 non-independent net-by-selection entries, not over one model.
- **Fix:** reword both.
- **Verified:** yes.

**12. "Practical ceiling F1 0.83" (section 2) · minor**
- **Issue:** the derivation assumes each distractor draws its own call. A long merge whose span covers a planted event and a distractor next to it avoids that false alarm. Figure 1 shows exactly this at about 4 and 9 minutes. This bears on binned SCE's 30 s merge lead.
- **Fix:** qualify the ceiling.
- **Verified:** partly (picture plus re-score).

**13. Section 10, "It does not make the results wrong" · minor**
- **Issue:** the evidence the report gives ("participation just outside its interval in both folders") reads as if a constant moved. The source says the constants are identical or near-identical between the two folders. Participation's mismatch is a pre-existing rounding (stored 0.18 = 6/33 against measured 0.1905), the same in both.
- **Fix:** give that evidence, or the sentence is only a reassurance.
- **Verified:** yes.

**14. "Why this report exists" and section 6 · minor**
- **Issue:** the report implies the two draws test whether the rehearsal's lead (+0.011 and +0.016) was real. The reversal is confounded with four simultaneous changes: simulator, coded tuning, budget and the fold defect.
- **Fix:** say the draws cannot attribute the reversal.
- **Verified:** yes.

**15. "Tuning … raised line_length by +0.032 and +0.029, more than any unflagged net moved" · minor**
- **Issue:** 0.029 against a maximum of 0.027 is a 0.002 margin.
- **Fix:** drop "more than".
- **Verified:** yes.

**16. Undefined quantities · minor**
- **Issue:** the report never says how a net's per-fold F1 is formed from its 5 refits (mean of refit F1s, or pooled), or what "pooled" means (summed hits and calls?).
- **Fix:** define both once.
- **Verified:** no.

**17. Captions for Figures 6, 8 and 10 · minor**
- **Issue:** each names the plotted quantity but not the claim it supports.
- **Fix:** state the inferential purpose in each caption.
- **Verified:** not applicable.

## Checked and clean
- **Fold independence.** I checked it independently of `fold_check`, which replays the same `fold_maker` path and so is a same-route check. In the fit records of both draws (1,943 and 1,938 fits), 0 fits trained or picked a threshold on a held-out-fold recording, and no two outer folds share a fitting set at any refit seed.
- **Seed overlap.** Goal 1's seeds (1–96) are disjoint from 1000–1047 and 2000–2047.
- **Arithmetic.** The fold SDs (0.005 and 0.018), the medians (0.010 and 0.006), 432/864 inner fits, F1 = 0.125, and the fit counts all recompute.
- **Held-out budget check (Table 3).** It could fail, and it did fire.
- **Headline sign.** chorus_gain_norm under the budget is below CoactDetect in all 8 folds, with no flagged fold.
