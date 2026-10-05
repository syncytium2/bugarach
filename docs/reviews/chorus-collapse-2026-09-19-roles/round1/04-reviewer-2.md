GRANT 4 ok — Read, Grep, Glob, Bash

Role 4 (Reviewer 2): adversarial findings on `<worktrees>/chorus-collapse/docs/learned/chorus_collapse/index.html`

I read the built page, the builder `tools/diagnose_chorus_collapse.py`, `chorus.py` and `train.py` on replicate-run, and `why_chorus.txt`. I recomputed from `collapse_table.json`, `census.json` and `replays/`, and read the second draw's `scores.zip`, `fits.zip` and `selections/`. The only model work was CPU forward passes on 34 checkpoints run on quiet:2000. I ran no GPU training. Nothing was edited. Intermediates are in `<scratch>/mb-cc/04/`.

**The main result holds.** Lowering the learning rate early rescues most collapsed lr-0.03 chorus_norm fits. Several claims around it do not hold as written, and one figure contradicts its own caption.

Each row: location · issue · severity · suggested fix · verified against a source.

## Blocking

**B1.** Figure 4 and the answer box, third bullet ("It happens in the first steps… losing whole layers by step 30"); section 4 ("against 0 in the working fit")
- **Issue:** the picture contradicts the caption. In Figure 4's own line for the working fit, one head layer is dead at step 10, earlier than the collapsed fit's step 30. It is dead again at steps 70, 80, 90, 120 and 130, then recovers. The caption says "the working fit's does not" die.
  - The two warm-up rescues 2736f584 s1 and 9ad792aa s1 also lose a layer at steps 110–120 and recover.
  - So the start of a dead layer does not tell the two fits apart. What differs is that it persists and more layers die (2 by step 120, 4 at the end).
- **Severity:** blocking.
- **Fix:** retitle Figure 4 and reword the bullet: dead layers come and go early in both fits, and the collapsed fit's never recover. Drop "by step 30" as the marker, or report it next to the working fit's step 10.
- **Verified:** yes. I read the polyline points in the built SVG and the replay logs.

## Major

**M1.** Answer box, "never leaves its starting level"; section 1, "a working model with one that never trained"; the page title "do not train"
- **Issue:** the page's own data contradict "never trained" and "the first steps" as general claims. Some grid configurations are identical except for step count, so their fits are the same run, cut off earlier or later:
  - 9ad792aa (900 steps) and 2736f584 (1,800 steps) are one run for their first 900 steps. All 90 logged losses to step 900 are identical in the two warm-up replays.
  - aace23d7 (900 steps) and 5d2026d1 (3,600 steps) are also a pair.
  - Across these pairs, 59 of 61 collapses are already present at 900 steps.
  - 2 had not happened by then. Second draw, seed 1, recs fe543e94c1: at 900 steps it works (output spread 2.36, smallest live share 0.125). At 1,800 steps it is collapsed (dead layer, spread 0.045). That fit trained and then died late.
- **Severity:** major.
- **Fix:** use the nested pairs as evidence: collapse is present by step 900 in 59 of 61. Name the 2 late collapses. Soften "never trained" and "the first steps".
- **Verified:** yes (`collapse_table.json` and `census.json`, joined on seed and recs).

**M2.** Section 1: "the collapse follows the fit's configuration and starting weights more than its data"
- **Issue:** the overlap between draws is exactly what chance predicts. If each draw collapsed independently at its configuration's own rate, the expected chorus_norm overlap is 111.5 fits. The observed overlap is 111; a permutation test gives a 95% range of 107–116. For chorus_gain_norm it is 38 observed against 39.6 expected. The overlap shows that configuration matters and says nothing about starting weights.
- **Severity:** major.
- **Fix:** replace this with the chance comparison and drop "starting weights" from the inference.
- **Verified:** yes (my permutation test on `collapse_table.json`).

**M3.** Section 2: "Nothing else in the fit's identity matters… 34%, 32%, 38% at training seeds 0, 1 and 2"
- **Issue:** this null claim cannot fail as tested, and the effect it rules out is there.
  - A seed sets different starting weights in each configuration. Per-seed shares pooled over all configurations therefore cannot see a seed effect inside a configuration. Suppose seed 1 collapses 6 of 6 in configuration A and 0 of 6 in B: the pooled share does not move.
  - Tested inside each configuration (seed labels shuffled within configuration, nested twins removed), chorus_norm clusters by seed: p = 0.002 in the second draw, 0.086 in the first, 0.0015 pooled. Examples: 5d2026d1 seed 1 collapses 1 of 6 in the second draw while seeds 0 and 2 collapse 6 of 6.
  - Fold pair is null by the same test (p = 0.78 and 0.97), so that half of the claim stands.
  - Step count and top_m were never examined.
  - M2 and M3 together: section 1 credits starting weights on evidence that cannot show them, and section 2 denies them with a test that cannot see them.
- **Severity:** major.
- **Fix:** state the seed test inside each configuration. Keep "fold pair makes no difference". Remove "nothing else matters".
- **Verified:** yes.

**M4.** Section 2, "chorus_gain_norm shows the same pattern, milder"; answer box, "It is the learning rate"
- **Issue:** the encoder's shape drives collapse at least as much as the learning rate, and in chorus_gain_norm more.
  - chorus_gain_norm at lr 0.03: 84 of 108 fits collapse with encoder width 4 and depth 6. All other shapes: 26 of 324.
  - chorus_gain_norm at lr 0.01 with width 4, depth 6: 36 of 144.
  - chorus_norm at lr 0.03: 97 of 108 for width 4, depth 6, against 33 of 72 for width 8, depth 4. 4 of the 7 collapses below lr 0.03 are width 4, depth 6.
  - All 15 of chorus_gain_norm's "second route" fits are width 4, depth 6.
  - The grid is unbalanced: chorus_gain_norm has no width-8, depth-6 configuration at lr 0.03.
- **Severity:** major.
- **Fix:** break the counts down by learning rate × encoder shape, as a table or by colouring Figure 1. Limit "It is the learning rate" to chorus_norm. Replace "same pattern, milder".
- **Verified:** yes.

**M5.** Section 3, the "second route" for chorus_gain_norm (overclaimed)
- **Issue:** the evidence does not establish a second route.
  - 9 of the 15 fits have exactly one live unit in their weakest layer, 0.125, which is one unit short of the "dead" line.
  - The vote-gain comparison (3% against 13%) is confounded by learning rate. Working fits at lr 0.03 move a median 28%, at lr 0.01 6.3%. At lr 0.01, dead-layer collapsed fits move 2.7% and no-dead-layer ones 3.6%. Vote-gain movement does not tell the two kinds of collapse apart.
  - At least 2 of the 15 are undertrained, not failing. c5fcce77 seed 1 fcbb and seed 2 fe54 have the same starting weights and data as a6d1c9b2 but 900 steps instead of 3,600, and the 3,600-step versions work.
- **Severity:** major.
- **Fix:** restate: "15 collapsed fits have no fully dead layer; 9 run a layer on one unit; all are width 4, depth 6; at least 2 recover with more steps." Compare vote gains at matched learning rate. Drop "second route".
- **Verified:** yes (census joined to the nested twins).

**M6.** Answer box, "What breaks is the head… so almost no signal passes"; section 3's mechanism
- **Issue:** a dead layer marks a collapse but has not been shown to cause it.
  - It is not necessary: 16 of 228 collapsed fits have none.
  - It is not sufficient: 4 of 636 working fits have one, the working replay has them briefly (B1), and one working fit has an output spread of 3.1 despite a dead layer.
  - 60 of 279 working chorus_norm fits run some layer on one live unit, so the head sheds units in general.
  - On the other hand, the head is where the signal is lost, and my check supports that. In 10 sampled collapsed fits, the head's input separates event frames from the rest about as well as in working fits: largest standardized difference (d) across channels 0.99–3.24 collapsed, 0.45–2.87 working. The collapsed fits' output does not: d ≤ 0.10 in 8 of the 10.
- **Severity:** major.
- **Fix:** keep "the head" and add the head-input against output comparison. Say "coincides with a dead head layer" instead of implying a dead layer is the cause.
- **Verified:** yes (CPU forward passes on checkpoints).

**M7.** Answer box, "This is not the failure PR #596 fixed"
- **Issue:** the page runs no test that could show this, though the claim is probably true.
  - Run the test: suppose a collapsed fit's encoder were deaf, as in #596. Its output would be flat, and its head layers could die downstream of a constant input. Neither page metric (smallest live share, output spread) would move. The only evidence offered is that collapse depends on the learning rate.
  - A check of the head input's *spread* also cannot fail in chorus_norm, because standardization gives every channel unit variance by construction.
  - The test that can fail is whether the head input responds to events. It passes: see M6. #596's own measure (difference at events against elsewhere, 1e-5) is the model to follow.
- **Severity:** major.
- **Fix:** add the event-selectivity measurement and cite it as the evidence.
- **Verified:** yes.

**M8.** Section 5: "its 95 refits across both draws (the chosen configurations…) are 35 at lr 0.003, 60 at lr 0.01"
- **Issue:** 40 of the 95 are refits of the untuned default configuration (9c65e498, flagged `is_untuned`, lr 0.01). Tuning did not choose them. Tuning's own picks are 55 unique refits: 35 at lr 0.003 and 20 at lr 0.01. "0 at lr 0.03" still holds: all 32 selection files show no lr-0.03 pick.
- **Severity:** major.
- **Fix:** separate the untuned refits and give tuning's picks as 55.
- **Verified:** yes (`is_untuned` in the table, and `selections/`).

**M9.** Section 4 and Table 2: "8 more collapsed fits from 8 lr-0.03 configurations: 7 of them train"
- **Issue:** the sample is smaller than it looks and its selection is not stated.
  - 2736f584 s1 ecf4 and 9ad792aa s1 ecf4 are the same run: the two configurations differ only in step count (their logged losses are identical through step 900). So Table 2 has 7 distinct runs, 6 of which train.
  - How the fits were chosen is not stated. The 3 lr-0.03 configurations left out (9987efaa, a04f8e10, aace23d7) are the ones that collapse least.
  - The comparison that would make this a test is missing. If warm-up were just any perturbation, each fit's expected chance of surviving is its configuration's working share. That sums to about 1.6 of 8 (about 1.4 of the 7 distinct runs), against 7 (6) observed. This is strong support, and the page does not use it.
- **Severity:** major.
- **Fix:** report 6 of 7 distinct runs, state the selection rule, and add the chance expectation.
- **Verified:** yes.

## Minor

**m1.** Section 4: "e86433df, is from a configuration that collapsed in 31 of its 36 fits"
- **Issue:** this reads as an explanation, and Table 2 contradicts it: 2736f584 and 33622c24 (33 of 36 each) were rescued.
- **Severity:** minor.
- **Fix:** drop the implied explanation.
- **Verified:** yes.

**m2.** Section 3, the "dead" threshold of 0.001
- **Issue:** the threshold is defined but not justified.
  - GELU(x) > 0.001 means a pre-activation above about 0.002, so "dead" is effectively "never positive".
  - In my probe, collapsed fits' dead layers peak between −98 and −0.17, or at about 0 downstream of an already-constant layer. The count is therefore robust to the threshold.
  - The real knife-edge is 0 against 1 live unit.
- **Severity:** minor.
- **Fix:** state the "never positive" reading and the robustness.
- **Verified:** yes, on a sample.

**m3.** Table 2 note: "trains" means training loss < 0.5; section 5 says "rescued"
- **Issue:** the cutoff is not justified, and it is not the criterion that defines a collapse.
  - About 1.5 is roughly the weighted loss of a constant output (≈2·ln2·(1−p) ≈ 1.4). Say so; that is the justification for 0.5.
  - The final training-batch output spread agrees with the loss cutoff: rescued fits 2.3–9.4, e86433df 0.0.
  - "Rescued" claims more than a training loss can show.
- **Severity:** minor.
- **Fix:** add the justification and the spread agreement. Say "trains", not "rescued".
- **Verified:** yes (replay logs).

**m4.** Section 5: "tuning never chose… because those configurations score badly"
- **Issue:** this is asserted, not shown, though true on my check. With collapsed fits included, second-draw inner F1 puts all 11 lr-0.03 configurations at ranks 14–24 (0.16–0.42). Their working fits alone score 0.67–0.75; 33622c24's 2 working fits (0.750) would tie the top. My F1 pools hits over recordings and approximates the tool's `inner_f1`.
- **Severity:** minor.
- **Fix:** show the ranking.
- **Verified:** yes (`scores.zip`).

**m5.** Section 5 bullet heading "Tuning already stepped around it"
- **Issue:** this is true for chorus_norm only. For chorus_gain_norm, tuning chose lr-0.03 configurations in 6 of 16 selections, and that is where 2 of the collapsed refits came from.
- **Severity:** minor.
- **Fix:** scope the heading to chorus_norm.
- **Verified:** yes.

**m6.** Figure 3 title: "depending only on its early learning rate"
- **Issue:** the lr 0.01 and lr 0.003 curves change the learning rate for the whole run. Only the warm-up curves isolate the early rate.
- **Severity:** minor.
- **Fix:** reword the title.
- **Verified:** yes.

**m7.** Subtitle: "nothing in the runs was retrained"
- **Issue:** the 14 replays are retraining. The subtitle contradicts section 4.
- **Severity:** minor.
- **Fix:** say the runs' outputs were not modified, and that 14 fits were replayed.
- **Verified:** yes.

**m8.** Section 5, the output-spread detector
- **Issue:** the check can fail (the builder asserts the separation), but the proposed refusal gives no cutoff. The 0.13 / 0.80 gap was set on the same second-draw data and one recording.
- **Severity:** minor.
- **Fix:** name the cutoff and test it on a second recording or the first draw.
- **Verified:** yes.

**m9.** Section 2, the width and depth shares within lr 0.03
- **Issue:** these are described, not tested. There are 5–6 configurations per level, and width and depth are confounded with each other, with top_m and with step count. The nested twins also count double in Figure 1.
- **Severity:** minor.
- **Fix:** say "described, not tested" and mark the twins.
- **Verified:** yes.

**m10.** Figure 2
- **Issue:** the output spread is clamped to a floor of 10⁻³ without saying so, and several collapsed fits have a spread of 0.0. This overlaps role 10's lane, so it is filed here once.
- **Severity:** minor.
- **Fix:** note the floor.
- **Verified:** yes (builder source).

## Claims that held when checked
- Table 1 counts; 152 of 153 and 1 of 279.
- Collapsed fits' threshold sits at the bottom of the 41-point grid (306 of 306 scored files).
- Both as-run replays match their checkpoints exactly. That check compares against the saved checkpoint, so it can fail.
- The counterfactuals change only the learning rate or warm-up: same starting weights and same batch sequence, because the batch sampler has its own seed.
- quiet:2000 was a training recording for some fits and not others, as the page says.

## Files
- Artifact: `<worktrees>/chorus-collapse/docs/learned/chorus_collapse/index.html`
- Builder: `<worktrees>/chorus-collapse/tools/diagnose_chorus_collapse.py`
- Data: `<worktrees>/chorus-collapse/docs/learned/chorus_collapse/collapse_table.json`, `census.json`, `replays/`
- Raw runs: `<darkroom>/bugarach/2026-09-18-replicate-run-status/results/` (`fits.zip`, `scores.zip`, `selections/`)
