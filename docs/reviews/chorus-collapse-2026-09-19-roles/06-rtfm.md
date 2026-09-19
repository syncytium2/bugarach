GRANT 6 ok — Read, Grep, Glob, Bash, WebSearch, WebFetch

# Role 6 (RTFM): chorus-collapse page and `diagnose_chorus_collapse.py`

## Summary
The heaviest problem is a measurement artefact. The head's convolutions pad with zeros, so a layer whose input is constant still "varies" near the ends of a recording or crop. The silent-layer rule takes the standard deviation (SD) over the whole window, so it counts that edge wiggle as a working unit. I re-measured every fit on the recording's interior, on CPU, with the page's own threshold. The page's exceptions all disappear:
- Every collapsed fit has a silent head layer: 153 of 153 chorus_norm, 75 of 75 chorus_gain_norm, and all 3 refits.
- No working fit has one.

The page's conclusion gets stronger, not weaker. But several of its numbers and one of its open questions are artefacts.

The second problem is what the training seed means. In this runner the seed also chooses which 10 of the 46 fitting recordings a fit trains on, and the page never says so. Its reading of the seed test, and its description of Figure 1, both miss this.

The replay's claim to reproduce training holds, by both code reading and the stored bit-for-bit checkpoint match. The replay loop matches the trainer's.

## Findings
Each row: location · issue · severity · suggested fix · verified against a source (yes/no).

1. **§3, the answer box, Figure 3, §5 last bullet, §6 fifth bullet; code `_head_probe` (`o[0].std(dim=1)`) and `census`.** The silent-layer rule and the output SD are computed over the whole recording, and zero padding creates variation at the edges.
   - On the collapsed fit in Figure 1, head layers 3 and 4 are silent (largest unit SD 2e-5 and 3e-6). Layers 5 to 8 still count as "varying", yet the output logit's SD away from the ends is 1.5e-8. In `trace.json`, every interior 1-second bin of the collapsed fit reads exactly 0.1835; all of the movement Figure 1 shows is in the first and last ~25 s.
   - Re-measured with 600 frames (60 s) dropped at each end:
     - the 24 "flat but no silent layer" chorus_gain_norm fits all have a silent layer (24 of 24);
     - the 11 such chorus_norm fits also do (11 of 11);
     - working fits still have none (0 of 279 and 0 of 357).
   - The output-SD gap moves from "at most 0.132 collapsed, at least 0.803 working" to "at most 0.0011, at least 0.82". The whole-recording figure depends on recording length, so the proposed end-of-training check should use the interior.
   - So the §6 limit ("what stops them is not established here") describes an artefact, and so do "142 of 153" and "51 of 75".
   - **Severity: blocking.**
   - **Fix:** measure SD on the interior, trimming at least the head's receptive field (±255 frames; 600 is safe). Recompute the counts, Figure 3, the §5 cutoff and the §6 limit. Say in §3 that padding makes edges vary.
   - **Verified:** yes. I re-ran the whole census on CPU; the output is in `<scratch>/mb2-cc/06/interior_census.json`.

2. **§4 and Figure 5; code `replay` hook (SD over batch × time).** The same artefact applies to training batches, where each 4,096-frame crop has two padded edges.
   - I ran the saved collapsed checkpoint in train mode on three 4,096-frame crops. The replay's rule gives 2 silent layers; the crop interiors give 6 of 8. That matches the page's "ends with 2 of its 8 silent", so the true figure is about 6.
   - Several claims rest on this metric and are unverified under the corrected one: "first has one at step 230", "135 of the 158 logged steps", and "the replay with a 50-step warm-up stays flat without a silent layer on any of its training batches". The last is the evidence for "does not begin the failure".
   - **Severity: major.**
   - **Fix:** measure interior-only in the replay hook and re-run the as-run and 50-step replays before stating when the head goes silent. Until then, drop or qualify the claim about what starts the failure.
   - **Verified:** end state yes (CPU, saved checkpoint). Onset no: the trajectories need a GPU replay, which I did not run because both GPUs are committed to goal 2 and a reviewer cannot claim the board.

3. **§1, "Both fits … differ only in their training seed, which sets the starting weights and the order of the training crops".** False on two counts.
   - The shown fits are seed 0 on folds [1, 3] (recs `3a17721a7a`) and seed 2 on folds [0, 3] (recs `ecf4b9b71a`). They differ in fold pair, so in training and threshold recordings too.
   - The seed also chooses which recordings are fitted: `_run_fit` takes `fit_pool[(seed*1000+i) % n_fit]`, with n_fit 46 and n_train 10.
   - **Severity: major.**
   - **Fix:** say they differ in seed *and* fold pair. In this configuration of the second draw, 17 of 18 fits collapsed and the only one that trained is this seed-2 fit, so the two could not be matched on fold pair.
   - **Verified:** yes (`collapse_table.json`, `tune_learned_vs_coact.py` line 811, `train.fold_maker`).

4. **§2, "The training seed does [matter] … some starting points escape and some do not"; code `_cluster_test`.** The seed test cannot separate starting weights from training data.
   - Within one draw and configuration, fits with the same seed on different fold pairs share on average 3.7 of their 10 fitted recordings (up to 6). Fits with different seeds share none (checked on config `2736f584`, second draw).
   - Across draws the same seed gives identical starting weights (manual_seed, then build on CPU) but different recordings. Evidence for a starting-point effect there is weak: my seed-level covariance test across draws gives p ≈ 0.036 for chorus_norm and 0.21 for chorus_gain_norm. The page's fit-level overlap is at chance (111 observed, 111.5 expected).
   - The page reads the within-draw p = 0.001 as a starting-point effect. Shared training recordings explain it at least as well.
   - The fold-pair test has the mirror problem: fits sharing a pair share no fitted recordings, only the validation ones.
   - **Severity: major.**
   - **Fix:** state what each level shares (seed: starting weights, crop random-number stream and about a third of the training recordings; pair: threshold recordings only). Drop "starting points" as the explanation, or test it across draws. Also reconcile "nothing about which ones do" (§1) with the seed claim.
   - **Verified:** yes. I reproduced the page's p values exactly: seed 0.001 and 0.2785, pair 0.9385 and 0.47.

5. **§4, "Sokar et al. (2023) define such 'dormant' units by a threshold on their activity, as this page does".** Not what the paper defines. Sokar Definition 3.1 thresholds a unit's mean absolute activation divided by its layer's average. That score cannot flag a uniformly quiet layer, and it ignores a unit stuck at a large constant. The page thresholds absolute SD over time.
   - **Severity: major** (the citation is offered as methodological support).
   - **Fix:** "Sokar et al. define dormant units by a threshold on normalized mean activation; this page thresholds variation instead." Or drop "as this page does".
   - **Verified:** yes (paper text, Definition 3.1).

6. **Table 2 note, "a constant output's loss is about 1.4 (2 ln 2 times the share of frames outside events)".** This holds only if batches carry the natural event share. The event-centred crops raise it: for the Figure 1 collapsed fit, 0.0065 against 0.0056. Under the actual sampler and pos_weight, the best constant logit is ≈ 0.14 and its loss 1.48, or 1.49 on the logged batches. The collapsed fit's logged loss averages 1.50 and its output sits at logit 0.18. So collapsed fits sit *at* the best constant, which is a sharper statement than "near 1.5".
   - **Severity: minor.**
   - **Fix:** "about 1.48 under the training sampler (the best constant); collapsed fits sit there".
   - **Verified:** yes (I simulated the sampler on the fit's own 10 recordings; PyTorch `BCEWithLogitsLoss` pos_weight semantics).

7. **§4, "If warm-up did nothing, each would train only as often as its configuration's fits do … predicts 1.4 of 7".** Replays are deterministic, so a warm-up that did nothing would reproduce the collapse: 0 of 7. The 1.4 is the expectation if the warm-up merely re-rolls the dice like a new draw.
   - **Severity: minor.**
   - **Fix:** "If the warm-up acted only as a perturbation that re-draws the outcome, …".
   - **Verified:** yes (code logic).

8. **§4, "one collapsed fit … from each of 7 other lr-0.03 configurations"; Figure 7 caption.** Table 2 has 8 rows. One is `2736f584` seed 1, a second fit of the reference fit's *own* configuration, and the twin of `9ad792aa` seed 1. The "6 of 7 distinct" and "8 distinct runs" arithmetic is right; this sentence is not.
   - **Severity: minor.**
   - **Fix:** "8 collapsed fits: one from each of 7 other configurations and a second fit of the reference configuration".
   - **Verified:** yes (replay files; every warm-up fit is confirmed collapsed as run in `collapse_table.json`).

9. **§3, "Every collapsed fit's threshold is the lowest value on the grid … below its whole output, so the whole recording is one call".** The causation is backwards. The collapsed output sits near sigmoid 0.545, so every grid threshold up to 0.5 gives the same single call. `pick_threshold` keeps the first maximum (`f1 > best_f1` on an ascending grid), so the floor is a tie-break signature, not the cause.
   - **Severity: minor.**
   - **Fix:** say that any threshold below the flat output gives one call and the tie-break lands on the floor.
   - **Verified:** yes (`train.py`, lines 372–385; `trace.json`).

10. **§3 and Figure 4, "d"; code `_selectivity`.** The "pooled SD" is the square root of the *unweighted* mean of the two groups' variances, not the n-weighted pooled SD, with events under 1% of frames. It takes the absolute value, and at the input it is a maximum over 12 or 24 channels, against one channel at the output. The dashed identity line therefore compares unlike quantities (the input maximum is only a lower bound on what the head could read).
    - **Severity: minor.**
    - **Fix:** name the variant (average-variance d), and note the max over channels and the absolute value in the caption.
    - **Verified:** yes (code).

11. **§1, "Inside each outer fold, every configuration is trained … on each of the 6 pairs of 4 inner folds and scored on the other two".** There are 4 folds in total. The 18 inner fits per configuration (3 seeds × 6 pairs) are shared across outer folds; refits train on 3 folds.
    - **Severity: minor.**
    - **Fix:** "the 4 folds give 6 pairs; each inner fit trains on a pair and is scored on the other two, and is shared by the outer folds it serves".
    - **Verified:** yes (`collapse_table.json`: pairs drawn from folds 0–3; outer `train_folds` have 3 folds).

12. **§4, the Gulcehre et al. (2022) citation.** Supported only in outline: the paper reports more dead ReLU units at larger learning rates. Their units are ReLU, and exact zeros do not occur with GELU.
    - **Severity: minor.**
    - **Fix:** add "(ReLU units)".
    - **Verified:** no (search summary only; the PDF exceeded the fetch limit).

## What I checked and found correct
- **PyTorch hooks.** Pre-hook `args[0][0]` is the head input, shape (12, T); the forward hooks sit on 8 distinct GELU modules (`approximate='none'`, which is exact GELU). The probe's logits are bit-identical to an unhooked forward pass.
- **GELU minimum.** −0.16997, which matches the page's "no lower than −0.17".
- **Adam.** Defaults are β 0.9 and 0.999, and lr 0.03 is 30 times Kingma & Ba's suggested 0.001.
- **Ma & Yarats.** The rule of thumb 2/(1−β2) = 2,000 steps is quoted correctly (checked in the paper).
- **The replay matches the trainer.**
  - The loop matches `train.train` lines 256–286.
  - The seeds, the `fold_maker` default n_val = 2, `conf["overrides"]`, and the seed → threshold-pinning → build order all match `_run_fit`.
  - Both as-run records store `max_abs_diff_vs_checkpoint` 0.0.
  - `--code` wins over the tool's own `src`: I checked that bugarach is not imported before `_use_code` runs.
- **Hardware.** All chorus_norm fits in both draws ran on one host, CUDA, RTX A4000. That supports both the bit-exact replay and "a shorter twin is its longer twin stopped early": step count only bounds the loop in `train.py`.
- **Expected overlap under independence.** Σ k1·k2/n per configuration is the correct hypergeometric mean; each (configuration, draw) has 18 fits with unique keys. Its interpretation is the problem (finding 4).
- **Permutation tests.** Shuffling within (draw, configuration), with p = (1+hits)/(N+1), is a valid construction, and the values reproduce exactly.

## Files
- Intermediates:
  - `<scratch>/mb2-cc/06/interior_census.json`: interior versus whole-recording census for all 1,215 chorus fits (both nets, second draw)
  - `<scratch>/mb2-cc/06/page.txt`: the page's text
  - `<scratch>/mb2-cc/06/sokar.txt` and `<scratch>/mb2-cc/06/ma.txt`: text of the two papers
- Artifact: `<worktrees>/chorus-collapse/docs/learned/chorus_collapse/index.html`
- Code: `<worktrees>/chorus-collapse/tools/diagnose_chorus_collapse.py`
- Trainer and runner: `<worktrees>/weekend-runs/src/bugarach/learn/train.py`, `<worktrees>/weekend-runs/tools/tune_learned_vs_coact.py`

Sources:
- [Sokar et al. 2023, arXiv:2302.12902](https://arxiv.org/pdf/2302.12902)
- [Ma & Yarats 2021, arXiv:1910.04209](https://arxiv.org/pdf/1910.04209)
- [Gulcehre et al. 2022, arXiv:2207.02099](https://arxiv.org/abs/2207.02099)
