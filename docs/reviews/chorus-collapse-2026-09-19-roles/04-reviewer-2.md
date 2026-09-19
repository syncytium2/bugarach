GRANT 4 ok — Read, Grep, Glob, Bash

(I also hold SubagentHandback, which only delivers this report and cannot edit anything. I hold no editing tools. I rendered the figures to `<scratch>/mb2-cc/04/fig1..7.png` with Playwright and wrote nothing else.)

**Artifact:** `<worktrees>/chorus-collapse/docs/learned/chorus_collapse/index.html`, built by `<worktrees>/chorus-collapse/tools/diagnose_chorus_collapse.py`. I checked the claims against `collapse_table.json`, `census.json`, `trace.json`, `replays/`, the raw runs in `<darkroom>/bugarach/2026-09-18-{fair-comparison-run,replicate-run-status}/results/`, and the trainer in `<worktrees>/weekend-runs/src/bugarach/learn/train.py`.

## Findings
Each row: location · issue · severity · suggested fix · verified against a source (yes/no).

**B1 · Answer box, "It is not the failure found earlier in plain chorus"; §3, "This is the test that separates this failure from the earlier one"; Figure 4**
- **Issue:** the test cannot fail. I built the nets untrained (torch seeds 0–2) and ran them on the census recording, quiet:2000, through the builder's own `_head_probe`.
  - Plain `chorus`, the net PR #596 called deaf, gives head-input d of 1.39–2.53.
  - Untrained chorus_norm gives 1.28–2.90.
  - The collapsed fits' median is 1.84.
  - So an encoder known to be deaf passes this test. The reason is that d is a standardized difference, so it does not depend on scale. PR #596's failure was about size: one onset moved a vote by at most 0.0003 (`why_chorus.txt` at 7fc052d). d cannot see a failure of that kind.
  - The failure also runs the other way. 32 of 279 working chorus_norm fits have head-input d < 1 but output d of about 5 (median 5.1). A low d at the input therefore does not mean the head has nothing to work with.
  - Untrained output d is 0.01–0.14, the same as the collapsed median of 0.13. On both axes a collapsed fit looks like an untrained net.
- **Severity:** blocking.
- **Fix:** restate this as "not detectable by this test". Replace it with a test that could fail: PR #596's own quantities (the ratio of encoder to head gradient norm, and the change in a vote per onset in absolute units), measured at initialization and at the end of training, for collapsed fits, working fits and plain chorus. Drop "the encoder still hears the events" until that test is run.
- **Verified:** yes (CPU run).

**M1 · §1, Figure 1: "Both fits … differ only in their training seed, which sets the starting weights and the order of the training crops"**
- **Issue:** this is false.
  - The two fits use different fold pairs. The collapsed fit is seed 0 on recs 3a17721a7a (folds [1,3]); the working fit is seed 2 on recs ecf4b9b71a (folds [0,3]).
  - The seed also chooses which 10 of the 46 training recordings a fit uses (`fold_maker` indexes `seed*1000+i`). The two fits trained on disjoint sets: quiet/busy 2012–2014 and 2036–2037 against 2041–2043 and 2006–2007.
  - A pair that differs only in seed exists: seed 0 on ecf4b9b71a also collapsed.
  - The working exemplar is also the only working fit out of 18 in this configuration in the second draw.
- **Severity:** major.
- **Fix:** use the matched pair, seed 0 against seed 2 on ecf4b9b71a, or state every difference. Say what the seed controls: weights, crop order and the choice of training recordings. Say that the exemplar is 1 working fit of 18.
- **Verified:** yes.

**M2 · §2, "The training seed does … some starting points escape and some do not"; §1, "nothing about which ones do"**
- **Issue:** the explanation is not supported, and the two sections contradict each other without saying so.
  - The seed effect comes from one draw: p = 0.0015 in the second draw and 0.09 in the first (the builder's own `_cluster_test`, run per draw).
  - The same configuration and seed has identical starting weights in both draws: `torch.manual_seed(seed)` runs before the net is built, and both draws used torch 2.14.0+cu126 on the same GPU. Its collapse tendency still does not carry over. The per-seed collapse counts, taken relative to each configuration's mean, correlate r = 0.08 across draws (permutation p = 0.15).
  - So starting points do not explain the seed effect. The training recordings, which the seed also picks, are the obvious confound.
  - The §1 overlap test takes the configurations' rates as input, so it cannot show that "the configuration decides how often".
- **Severity:** major.
- **Fix:** report the seed test per draw and the cross-draw result. Replace "starting points" with "the seed (weights, crop order and training recordings)". For "configuration decides how often", compare against an expectation that ignores configuration (about 52 overlapping fits if every fit shared chorus_norm's overall rate, against 111 observed).
- **Verified:** yes.

**M3 · Answer box, "a slower start prevents it … also trains 6 of 7 other collapsed runs"; §4; Table 2**
- **Issue:** the evidence is weaker than the claim.
  - "Prevents collapse" is judged by training loss on training batches. Collapse is defined by calls on held-out folds, and no counterfactual was scored that way.
  - The fits were "chosen by hand" with no stated criterion. Five of the eight share recs ecf4b9b71a with the working fit.
  - "If warm-up did nothing … predicts 1.4" states the null wrongly. A replay with nothing changed reproduces the checkpoint exactly, so doing nothing predicts 0. The 1.4 is a null in which any perturbation re-rolls the outcome.
  - "Each of 7 other lr-0.03 configurations" is wrong. Table 2 has 8 configurations, and one of them, 2736f584 at seed 1, is Figure 1's own configuration.
- **Severity:** major.
- **Fix:** write "in 7 of 8 hand-picked collapsed runs, training loss fell below 0.5". State the rule used to pick the fits, or pick them at random. Name the null correctly. Score the counterfactual models with `pick_threshold` and held-out calls before saying "prevents". Fix the count.
- **Verified:** yes.

**M4 · Answer box, "A collapsed fit never leaves its flat start"**
- **Issue:** a universal claim rests on one as-run replay.
  - Every one of the 14 replays starts flat: first-batch output SD 0.0003–0.0025 logits.
  - The time to leave varies from about 80 to 420 steps; the lr-0.01 replay leaves only near step 420 (Figure 6).
  - End-state data cannot tell "never left" from "left and came back". The two-length comparison shows the outcome is fixed by step 900, not that the fit never moved.
- **Severity:** major.
- **Fix:** replay the other 7 collapsed fits as run (the same GPU cost as their warm-up replays) and report the time each leaves, or narrow the claim to "the replayed collapsed fit".
- **Verified:** yes.

**M5 · §4, "A known failure, with a standard remedy"; answer box, "This is a known failure …"**
- **Issue:** the cited literature describes a different failure.
  - Dormant or dead units (Sokar 2023; Gulcehre 2022) are the thing this page's own replay shows arriving after the failure: the first silent layer appears at step 230, and the 50-step warm-up replay stays flat with no silent layer at all.
  - Sokar defines dormancy by normalized mean |activation|, not by the SD over time, so "as this page does" is wrong.
  - What the page actually shows is an output that is flat from initialization, through an 8-layer GELU dilated-convolution head, and never escapes. That is not the cited phenomenon.
- **Severity:** major.
- **Fix:** soften to "consistent with"; drop "as this page does". Cite warm-up as a remedy that was tried here, not as the standard cure for this mechanism. I did not check the Gulcehre claim against the paper.
- **Verified:** partly (Sokar's definition from knowledge; Gulcehre not checked).

**M6 · Answer box and §5: "the collapse took 11 of its 24 configurations out of contention … in effect tuned over a smaller grid"**
- **Issue:** this is an untested counterfactual, and the data lean against it.
  - I computed a rough pooled inner F1 per configuration, 2·hits/(planted+detected) at each fit's own threshold, both draws.
  - Counting only fits that worked, which favours them, 9 of the 11 lr-0.03 configurations (0.663–0.731) still score below every lower-lr configuration (0.704–0.740).
  - Most lr-0.03 configurations would probably have lost the selection anyway.
- **Severity:** major.
- **Fix:** rerun the selection with collapsed fits removed and see whether any lr-0.03 configuration wins. Otherwise write "tuning chose none; whether collapse alone decided that was not tested".
- **Verified:** partly (my F1 approximates the selection rule).

**M7 · §3 "The encoder still hears … the head does not pass them on"; Figure 4, image against caption**
- **Issue:** the picture does not show what the caption says.
  - The caption says "the head's input still separates events in collapsed fits". In panel B that is false for many fits: collapsed chorus_gain_norm median d_in is 1.01, and 19 of 75 are below 0.5.
  - In panel A, working fits sit far above the diagonal. The head builds separation over time (dilated convolutions with a receptive field of about 511 frames) from inputs whose best single channel separates weakly. The input d is a maximum over 12–24 channels, frame by frame, so it does not bound what the head can use.
  - The visible orange row at output d ≈ 1.4–2.0 is an artifact: 16 chorus_norm and 6 chorus_gain_norm collapsed fits with output SD ≈ 0, where d comes out as √2 or 2 from float32 round-off.
- **Severity:** major.
- **Fix:** fix the caption for panel B. Mask d wherever the output SD is below 1e-6. Stop presenting input d as "what the head was given". Describe the head as 8 dilated temporal convolutions (kernel 3, dilation 1–128) plus a 1×1 output layer, not "8 layers of 8 units".
- **Verified:** yes.

**M8 · §5, "A check at the end of training could refuse a fit … instead of scoring it"**
- **Issue:** in a fair comparison, refusing failed fits selects on the outcome and flatters the nets unless a refused fit counts as a failure or its retraining cost is charged. The separation is also close to definitional: a flat output is how one call per recording arises.
- **Severity:** major.
- **Fix:** say how a refused fit would be counted in goal 2, and that the check must not silently drop failures.
- **Verified:** yes (from the page's logic).

**m1 · Title and answer box, "a third of chorus_norm's fits"**
- **Issue:** these are inner (tuning) fits. The delivered refits collapse at about 2%: 2 of 95.
- **Severity:** minor.
- **Fix:** write "a third of its tuning fits".
- **Verified:** yes.

**m2 · §3, the silent threshold (SD < 0.001) and "flat output"**
- **Issue:** the 0.001 cutoff is stated but not justified, and nothing shows how sensitive the counts are to it. It is an absolute value applied to layers of different scale. "Flat" is never defined; implicitly it means SD ≤ 0.132.
- **Severity:** minor.
- **Fix:** justify the cutoff and give the counts at 1e-4 and 1e-2; define "flat" numerically.
- **Verified:** yes.

**m3 · §3, "Every collapsed fit's threshold is the lowest value on the threshold grid … below its whole output"**
- **Issue:** the converse is withheld. The builder computes `work_floor` (2 of 279 working chorus_norm fits also sit at the floor) and never prints it. "Below its whole output" is not checked by the build; a single call can still contain dips shorter than the 20-frame merge gap.
- **Severity:** minor.
- **Fix:** report the 2 of 279, and check or drop "below its whole output".
- **Verified:** yes.

**m4 · §2, "the fold pair makes no difference (p = 0.939)"**
- **Issue:** a null result is stated as absence. The test has little power: 3 fits per pair per configuration per draw, and only the lr-0.03 configurations have any variance to detect.
- **Severity:** minor.
- **Fix:** write "no fold-pair effect detected".
- **Verified:** yes.

**m5 · Answer box, chorus_gain_norm "shape matters as much as the learning rate"**
- **Issue:** an untested comparison sits in the summary.
- **Severity:** minor.
- **Fix:** label it "described, not tested".
- **Verified:** yes.

**m6 · Table 3, "refits of configurations tuning chose"**
- **Issue:** the counts are not defined.
  - They pool two selection rules, gated and ungated, which the page never mentions, and they deduplicate refits the two rules share.
  - Refits of configurations tuning did choose are filed as the "untuned default": first-draw chorus_norm ungated outer 0 chose 9c65e498, and second-draw chorus_gain_norm gated outer 0 chose eefc4415. So the lr-0.01 counts are too low.
- **Severity:** minor.
- **Fix:** define the count and split it by selection rule.
- **Verified:** yes.

**m7 · §1, "Inside each outer fold, every configuration is trained … on each of the 6 pairs of 4 inner folds"**
- **Issue:** the design is misdescribed. There are 4 folds in total. The 432 inner fits are shared across outer folds, and each outer fold's selection uses the 3 pairs that exclude it.
- **Severity:** minor.
- **Fix:** describe the design as run.
- **Verified:** yes.

**m8 · §1, the definition of a configuration**
- **Issue:** it omits vote_gain, which is a grid axis for chorus_gain_norm (two configurations differ only in vote gain).
- **Severity:** minor.
- **Fix:** add it.
- **Verified:** yes.

**m9 · §3 and §6, the census recording quiet:2000**
- **Issue:** some fits trained on it (for example seed 0 on folds [0,3]).
- **Severity:** minor.
- **Fix:** rerun the census on a recording outside seeds 2000–2047. It is a cheap CPU run and removes the caveat.
- **Verified:** yes.

**m10 · §4, "the working fit's head never has a silent layer"**
- **Issue:** silent layers also appear briefly in fits that do train. The warm-up replays of 2736f584 and 9ad792aa at seed 1 show one on 10 logged steps each; the lr-0.003 replay on 2.
- **Severity:** minor.
- **Fix:** say that a brief silent layer also occurs in fits that train.
- **Verified:** yes.

**m11 · Figure 7 caption, "no line passes it [2.0]"**
- **Issue:** 4a12a8bb's smoothed loss reaches 2.00 and its raw loss spikes to 3.99. The 5-step smoothing hides the spike.
- **Severity:** minor.
- **Fix:** mention the spike.
- **Verified:** yes.

## Checked and holding up
- **Figures 1, 2, 5 and 6 support their captions.** In Figure 1 the collapsed output stays between 0.174 and 0.195 logits, with no rise at events, against a threshold of −9.21.
- **The table and census numbers check:** 146 and 153 collapses; 292 of 396 at lr 0.03 and 7 of 468 below it; 142 of 153 against 0 of 279; SD medians 0.0055 and 5.20; the gap 0.132 / 0.803. Every recording has 15 planted events, so F1 = 0.125.
- **The replays:** both as-run replays reproduce their checkpoints exactly (maximum difference 0.0); the working fit's loss falls below 1.0 at step 220; the first silent layer appears at step 230.
- **Constant learning rate:** there is no LR schedule in `train()`, so a shorter twin really is its longer twin stopped early.
- **The head is untuned:** head width and depth are not grid axes.
