GRANT 1 ok — Read, Grep, Glob, Bash

# Role 1, Prove It: round 2 on `<worktrees>/chorus-collapse/docs/learned/chorus_collapse/index.html`

I checked the page, the todo and the INDEX row against the raw runs, using my own tar/zip reader and my own code, not the builder's `R.Archive` or `page()`.

**How I checked it:**
- **Collapse table.** I rebuilt all 1,938 chorus fits (both draws) from the fits and scores archives. The keys and the collapsed, role, pair, lr, steps, width, depth, top_m and untuned fields match `collapse_table.json` exactly, with 0 differences.
- **Census.** I ran all 974 second-draw fits on quiet:2000 with my own hooks.
- **Replays through the project's own trainer.** I re-ran four fits on the GPU through `bugarach.learn.train.train` itself, not the builder's copy of its loop:
  - Both as-run fits reproduce their checkpoints with max |diff| 0.0, and the same thresholds (0.95 and 0.0001).
  - The collapsed fit at lr 0.01, and at lr 0.03 with a 200-step warm-up (added by wrapping Adam's step, since I may not edit the trainer), give loss histories identical to the committed replay logs at all 37 steps they share (|diff| 0.0).

**Results:**
- Nearly every number recomputes.
- **One figure's data are numerically wrong (F3).** Figure 4 and the 0.13 median come from float32 rounding.
- **Five claims are wrong in what they assert (F1, F2, F4, F5, F6).**

## Claim ledger

| # | Quoted value | Cited source | Recomputed | Verdict |
|---|---|---|---|---|
| 1 | 146 and 153 of 432 chorus_norm inner fits collapsed | raw scores | 146/432, 153/432 | match |
| 2 | a collapsed fit makes one call, matching 1 of 15 events, F1 0.125 | score rows at own_index | all 21,648 collapsed recording-rows are (15 planted, 1 hit, 1 detected) | match |
| 3 | 292 of 396 at lr 0.03; 7 of 468 below | raw | 292/396; 7/468 | match |
| 4 | Table 1, every cell, both nets | raw | identical in all 24 cells | match |
| 5 | Figure 2: row totals 1/216, 6/252, 292/396, 3/144, 37/288, 110/432, and every per-configuration count and shape in the hovers | raw + configs | identical | match (but see F10) |
| 6 | lr-0.03 configurations collapse in 42% to 92% of fits | raw | 0.417 to 0.917 | match |
| 7 | at lr 0.03: 900 steps 141/216, 1,800 steps 59/72, 3,600 steps 92/108; all 3,600-step configurations are 6 deep | raw | same; depth {6} | match |
| 8 | chorus_gain_norm at lr 0.03: 4×6 78%, other shapes 8%; at lr 0.01, 4×6 25% | raw | 84/108; 26/324; 36/144 | match |
| 9 | same fit collapsed in both draws: 111, expected 111.5; chorus_gain_norm 38 and 39.6 | raw | 111 / 111.50; 38 / 39.61 | match |
| 10 | fold-pair p 0.939 / 0.470; seed p 0.001 / 0.279 | raw, my own permutation test (4,999 shuffles, different RNG) | 0.935 / 0.459; 0.0016 / 0.262 | match |
| 11 | seeds 0, 1, 2 pooled: 34%, 32%, 38% | raw | 97, 93 and 109 of 288 | match |
| 12 | 5 twin pairs; early 60 of 62, late 2, recovered 0; chorus_gain_norm 8, 0, 3; step pairs 900/1,800, 900/3,600, 1,800/3,600 | raw | identical. Each twin pair ran on one host (0 of 90 mismatched per draw) | match |
| 13 | 432 inner fits = 24 configurations × 3 seeds × 6 pairs | runs | 24 configurations × 18 fits per draw | count matches, description wrong (F7) |
| 14 | Figure 1 fits "differ only in their training seed" | run.json | seed 0 is fold pair [1,3]; seed 2 is fold pair [0,3] | **mismatch (F1)** |
| 15 | Figure 1: quiet:2024, held out from both fits, 15 events, 23 calls vs 1 whole-recording call (2,693.8 s); thresholds 2.9 and −9.2 as logits | my own run of both fits | 23 calls vs 1 call spanning 26,938 frames; collapsed output 0.174 to 0.195 logits; quiet:2024 is in neither fit's training recordings | match |
| 16 | census: 142 of 153 vs 0 of 279 (chorus_norm); 51 of 75 vs 0 of 357 (chorus_gain_norm) | my census | identical | match |
| 17 | round-1 sign rule: 152 collapsed and 1 working; the working one varies normally | my census | 152, 1 (75d44745, output SD 3.12) | match |
| 18 | median output SD 0.0055 vs 5.20 | my census | 0.00547 / 5.198 | match |
| 19 | median d at the head's input: 1.84 vs 2.60 | my census | 1.843 / 2.600 | match |
| 20 | median d at the output: collapsed **0.13**, working 4.29 | my census (float64) | **0.111** / 4.291 | **mismatch (F3)** |
| 21 | 59 and 26 fits with output SD below 10⁻³ | my census | 59, 26 | match |
| 22 | every collapsed fit's threshold is the grid floor 0.0001, below its whole output | scores + census | all 453 collapsed fits in both draws at own_index 0 (grid[0] = 0.0001). On quiet:2000 the minimum logit clears the threshold by at least 7.4 logits in 231 of 231 | match |
| 23 | output SD separates the groups: at most 0.132, at least 0.803 | my census, including refits | 0.1322 / 0.8034 | match |
| 24 | 24 collapsed chorus_gain_norm fits have no silent layer: 2 / 11 / 11 by lr; 4×6: 23, 8×4: 1 | my census | identical; largest SD 0.106 | match |
| 25 | the second draw's collapsed refits: 3 in the census, all 3 silent | my census | 7cea38e2 s1, 75d44745 s1 and s2; silent layers 2, 1, 2 | match |
| 26 | both as-run replays reproduce their checkpoints bit for bit (page and INDEX row) | my run through `train.train` | 0.0 and 0.0, with identical thresholds | match |
| 27 | first-batch output SD 0.0008 and 0.0011; loss below 1.0 by step 220; first silent layer at step 230; 135 of 158; ends with 2 silent | replay logs | 0.00080 / 0.00105; 220; 230; 135/158; 2 | match |
| 28 | the working fit never has a silent layer; the 50-step warm-up never has one | replay logs | 0 of 181 logged steps in each | match on logged batches only (F12) |
| 29 | the collapsed fit trains at lr 0.003, 0.01 and 0.03 with a 200-step warm-up; not with a 50-step one | replay logs; the lr-0.01 and 200-step runs re-run through `train()` | 0.199, 0.143, 0.162; 1.506. My `train()` runs give identical losses | match |
| 30 | Table 2 final losses 0.07 / 0.11 / 0.18 / 0.09 / 0.14 / 0.11 / 1.70 / 0.09; 6 of 7 distinct runs train; every target collapsed as run | replays + table | 0.073 / 0.112 / 0.179 / 0.087 / 0.144 / 0.113 / 1.696 / 0.094. All 8 targets are collapsed. 9ad792aa s1 equals 2736f584 s1 at 90 of 90 shared steps | match |
| 31 | chance baseline 1.4 of 7 | raw shares | 1.444 | arithmetic matches, the null is mislabelled (F9) |
| 32 | 3 lr-0.03 configurations left out: 2 lowest (15/36, 18/36) and 1 shorter twin (aace23d7) | raw | same | match |
| 33 | Figure 6: no smoothed line reaches 2.0. Figure 7: no line passes 2.0 | replays | highest smoothed values 1.700 and 1.996 | match |
| 34 | a constant output's loss is about 1.4; collapsed fits sit near 1.5 | my own crop sampling on the fit's data | 1.48 on the batches actually trained on | **mismatch (F8)** |
| 35 | tuning chose no lr-0.03 configuration for chorus_norm; 11 of 24 configurations out of contention | selections (16 per net) + inner F1 | 0 of 16 chorus_norm selections at lr 0.03. All 11 lr-0.03 configurations rank below all 13 others in both draws (inner F1 0.16 to 0.50 vs 0.67 to 0.75); working lr-0.03 fits average 0.691 | match (proxy) |
| 36 | Table 3: 6/7/11 and 4/8/12 configurations; refits 35/20/0 and 35/10/30; collapsed 0/2/0 and 0/0/2; 40 untuned refits per net | raw + selections | same under the builder's definition | counts match, 5 refits per net dropped (F6) |
| 37 | tuning chose lr 0.03 for chorus_gain_norm (30 refits) | selections | 6 of 8 **ungated** selections, 0 of 8 **gated** | **incomplete (F4)** |
| 38 | the 4 collapsed refits: chorus_gain_norm first draw lr 0.03, second draw lr 0.03; chorus_norm second draw lr 0.01 ×2; the † agrees | results.json `failed_training_signature` / `f1_was_nan` | exactly those 4, plus the chorus_norm pair called nothing under the budget | match |
| 39 | the † flag means F1 near 0.125 with the threshold at the grid floor, or F1 undefined | `tune_learned_vs_coact.py:1581` | abs(F1 − 0.125) < 0.01 and threshold ≤ 1e-4; or `f1_was_nan` | match |
| 40 | head: 8 layers of 8 GELU units, never tuned; Adam at its defaults; lr 0.03 is 30× Kingma & Ba's default | configs (all 96), `train.py:228`, `_dilated_stack` | head 8×8 in every configuration; `Adam(params, lr=lr)`; α = 0.001 | match (F13 nit) |
| 41 | GELU's dip goes no lower than −0.17; 2/(1 − β2) = 2,000 = 10 × 200 | arithmetic | −0.170; 2,000 | match |
| 42 | PR #596 open; it tested plain chorus at lr 0.01 and 0.001; the README section "Repairing chorus" at 7fc052d | gh; `git show 7fc052d:` | OPEN; only those two learning rates in why_chorus.txt; section at README line 195 | match |
| 43 | the fair-comparison report declares 24 configurations per net; a test rebuilds the page | report; tests/ | "its untuned one and 23 drawn at random"; `test_page_rebuilds_from_committed_data` | match |
| 44 | the census recording was trained on by some fits and not others | run.json | 161 of 974 fits trained on quiet:2000; 0 picked a threshold on it | match |
| 45 | Gulcehre 2022, He 2016, Goyal 2017, Liu 2020 (what each says) | — | not fetched | unverifiable here (role 2) |
| 46 | Sokar 2023 defines dormant units "as this page does" | the paper's definition, from knowledge (not fetched) | Sokar thresholds normalized mean \|activation\|; this page thresholds the SD over time | mismatch (F11) |
| 47 | Todo and INDEX: 292/396, 7/468, 6 of 7, 11 of 24, 0.132/0.803, 24 of 75, 50-step warm-up insufficient, bit-exact | as above | same | match (wording issues: F4, F13) |

**Missing values:**
- `collapse_table.json`: `vote_gain` is null only for chorus_norm, which has no vote gain. Correct.
- My census: no NaN in SD or d_in. d_out is undefined (0/0) for 46 fits whose output is exactly constant; F3 covers them.

**Record of design:** these are simulated recordings. The configs, meta.json, run.json and selections are the record, I consulted all four, and nothing is withdrawn.

## Findings

Each finding is given as: location · issue · severity · fix · verified against a source.

**F1** · §1 prose before Figure 1: "Both fits … differ only in their training seed, which sets the starting weights and the order of the training crops." · **major**
- **Issue:** the two fits also differ in fold pair. The collapsed fit (seed 0) trained on folds [1,3]; the working fit (seed 2) on [0,3]. They trained on entirely different recordings.
- **Issue:** the seed also picks which 10 of the pair's 22 fitting recordings are used (`fold_maker`: `fit[(seed·1000 + i) % 22]`). In 576 of 576 (draw, configuration, pair) groups, the 3 seeds have 3 different sets of fitted recordings.
- **Fix:** "same configuration, different training seed and fold pair". List what the seed sets: starting weights, crop order, and which recordings of the pair it fits.
- **Verified against a source:** yes (run.json `train_folds` and `fitted_recordings`; `train.py` 117–147 and 230).

**F2** · §2: "The training seed does [matter] … at a risky configuration some starting points escape and some do not." Also §6, "the seed effect … is measured, not explained" · **major**
- **Issue:** the seed carries three things, not one: starting weights, crop order and the subset of training recordings (F1). The page names only the starting weights.
- **Issue:** its own §1 overlap argues against starting points. A given configuration and seed builds the same starting weights and draws the same crop sequence in both draws (`manual_seed(seed)`, `RandomState(seed)`); only the recordings differ, because the draws use seeds 1000–1047 and 2000–2047.
- **Evidence:** if starting points decided escape, the same (configuration, seed) would collapse together across draws. They do not:
  - The overlap is 111 against 111.5 expected.
  - My test of whether per-seed collapse counts within a configuration covary across draws gives p = 0.155 for chorus_norm and 0.229 for chorus_gain_norm (one-sided, 9,999 permutations).
- **Conclusion:** the seed effect inside a draw is at least as consistent with the seed's choice of training recordings.
- **Fix:** say the seed effect is not attributed. It could be the starting weights or the recording subset, and the draw comparison does not support starting weights alone.
- **Verified against a source:** yes. Caveat: that the first draw built identical starting weights assumes it ran the same trainer as the second. Both are torch 2.14.0+cu126, and the model is built on the CPU after `manual_seed`.

**F3** · §3 "median of 0.13" (output d, collapsed chorus_norm fits) and Figure 4 · **major**
- **Issue:** `_selectivity` works in float32 with `+1e-12` outside the square root. On outputs that are exactly constant, it returns rounding noise:
  - 32 collapsed chorus_norm and 14 collapsed chorus_gain_norm census fits have exactly constant logits (SD 0.0 in float64), so their d is undefined.
  - The builder gives them values up to 2.0.
- **Scale in Figure 4:** 23 chorus_norm and 11 chorus_gain_norm collapsed dots sit at output d ≥ 0.5 (16 and 6 at ≥ 1). Recomputed in float64, none reaches 0.5. The largest disagreement with `census.json` is 2.0; for fits with SD ≥ 1 it is 1e-6.
- **Consequence:** the true median is 0.11. The artifact dots put collapsed fits at d ≈ 1.4–2.0 at the output, which is near the working fits' input median, and so visually undercut the caption.
- **Fix:** compute d in float64, and either draw constant-output fits as a separate "undefined" mark or put them at 0. Regenerate `census.json` and Figure 4.
- **Verified against a source:** yes (my census; the logits are exactly constant).

**F4** · §5 "For chorus_gain_norm it did not. Tuning chose lr-0.03 configurations for it (30 refits)"; also the todo's "tuning did choose lr-0.03 configurations for it" and option 1 · **major**
- **Issue:** chorus_gain_norm chose lr 0.03 only in the F1-alone (ungated) selection: 6 of its 8 ungated selections and 0 of its 8 gated ones. Both collapsed chorus_gain_norm refits are ungated.
- **Consequence:** under the budget, the column the replicate report headlines, chorus_gain_norm's held-out scores contain no collapsed refit, and the replicate report puts no † on chorus_gain_norm's budget column. The page never names the two selections.
- **Fix:** "On F1 alone, tuning chose lr 0.03 for chorus_gain_norm in 6 of 8 folds (30 refits), including both collapsed refits. Under the budget it never did." Qualify the todo the same way.
- **Verified against a source:** yes (selections/{gated,ungated}/outer*/chorus_gain_norm.json; results.json; replicate report Table 1).

**F5** · Companion doc, the replicate report (`docs/learned/tuned_vs_coact/replicate1/report.html` §8, and its builder's assert at `make_replicate_report.py:1190`): "The two draws share their configurations and training seeds, so the same fits largely fail in both (111 of chorus_norm's are the same fit)" · **major**
- **Issue:** this page measures 111 against 111.5 expected by chance and concludes the opposite. The replicate report is linked here as "the reports it builds on", and still carries the withdrawn claim. Its builder asserts `coll_both > 0.5 × min`, which enforces the refuted inference.
- **Fix:** correct the replicate report's sentence and assert in the same PR, or have this page state that it corrects that report.
- **Verified against a source:** yes.

**F6** · Table 3, column "refits of configurations tuning chose" · **minor**
- **Issue:** the builder drops every refit whose configuration equals the untuned default. Tuning itself chose the untuned default twice:
  - chorus_norm, first draw, ungated outer 0 (9c65e498);
  - chorus_gain_norm, second draw, gated outer 0 (eefc4415).
- **Consequence:** both lr-0.01 cells undercount tuning's choices by 5 refits: chorus_norm should read 25, not 20, and chorus_gain_norm 15, not 10. The note's "whatever tuning chooses" hides the overlap.
- **Fix:** count those refits under tuning as well, or say in the note that 5 per net are both.
- **Verified against a source:** yes (selections; refit keys).

**F7** · §1 "How the fits are organized": "Inside each outer fold, every configuration is trained at 3 training seeds on each of the 6 pairs of 4 inner folds and scored on the other two" · **minor**
- **Issue:** there are 4 folds in all. For outer fold h, selection uses the 3 pairs of its 3 training folds, each scored on the one remaining fold (`tune_learned_vs_coact.py` `_inner`). Inner fits are shared between outer folds ("the one inner fit two outer folds share is still trained once"). The 432 is 24 × 3 × 6 over the whole draw, not per outer fold.
- **Fix:** "Across the 4 folds, each configuration is trained at 3 seeds on each of the 6 pairs of folds and scored on the other two; each outer fold's selection uses the 3 pairs that exclude it."
- **Verified against a source:** yes.

**F8** · Table 2 note: "a constant output's loss is about 1.4 (2 ln 2 times the share of frames outside events), and the collapsed fits sit near 1.5" · **minor**
- **Issue:** the formula assumes the batch's event share equals the training recordings' share (0.56%). The loss plotted is taken on crops half of which are centred on events, where the event share is 0.65%. With pos_weight 177, a constant output then scores 1.48 (1.47 at the best constant).
- **Consequence:** the collapsed fits' ~1.5 is the constant-output level, not above it.
- **Fix:** "a constant output's loss on these batches is about 1.5, where the collapsed fits sit."
- **Verified against a source:** yes (I replayed the crop sampler on the collapsed and working fits' own data).

**F9** · §4 "If warm-up did nothing, each would train only as often as its configuration's fits do, which predicts 1.4 of 7" · **minor**
- **Issue:** the replays are deterministic (bit-identical). If warm-up did nothing, 0 of 7 would train. The 1.4 is the null that "the warm-up re-draws the fit's luck without helping", which is a different claim.
- **Fix:** relabel the null. The conclusion is stronger against 0.
- **Verified against a source:** yes.

**F10** · the definition of a configuration (§1), and Figure 2 panel B hovers · **minor**
- **Issue:** chorus_gain_norm has a further axis, the vote gain's starting value (8 or 16). 95a649dd and c5fcce77 read identically in the hover ("encoder 4 wide × 6 deep, top 8, 900 steps, lr 0.01"); they differ only in vote_gain, 16 against 8.
- **Fix:** add the vote gain to the definition and to panel B's hover.
- **Verified against a source:** yes (configs).

**F11** · §4 "Sokar et al. (2023) define such 'dormant' units by a threshold on their activity, as this page does" · **minor**
- **Issue:** Sokar's τ-dormant score is a unit's mean |activation| normalized by its layer's mean. This page thresholds the SD over time, which is a variation test and not an activity test. A unit with constant nonzero output is silent here but not dormant there.
- **Fix:** "a related threshold on activity; this page thresholds variation instead."
- **Verified against a source:** partly. The paper's definition is from knowledge, not fetched; role 2 should confirm it.

**F12** · §4 "Measured on the training batches, the working fit's head never has a silent layer" and "without a silent layer on any of its training batches" · **minor**
- **Issue:** only every 10th batch was measured (181 of 1,800 logged steps).
- **Fix:** "on any logged batch (every 10th step)".
- **Verified against a source:** yes.

**F13** · Box and §3 "the eight layers that turn the pooled per-ROI statistics into the output" · **minor (nit)**
- **Issue:** `_dilated_stack` ends in a 9th layer, a linear 1×1 output convolution, which the silent-layer test does not cover.
- **Fix:** "8 GELU layers of 8 units, then a linear output layer".
- **Verified against a source:** yes (`nets/__init__.py` 84–97).

**F14** · Todo "Why the output stays flat" · **minor**
- **Issue:** "Every fit starts with a nearly flat output" generalizes from 9 replayed fits (first-batch SD 0.0003 to 0.0025).
- **Issue:** "its head … later goes silent" is stated for every collapsed fit, but 11 of 153 collapsed chorus_norm census fits have no silent layer.
- **Fix:** "every replayed fit (9)"; "most collapsed fits' heads (142 of 153) …".
- **Verified against a source:** yes.

**Checked with no finding:**
- **INDEX row:** its bit-exact claim holds; I confirmed it through the project's own trainer.
- **Glossary "Tuning the learned nets":** the definitions match the code (the SD < 0.001 rule applies per unit, over frames).

## Files
All intermediates are under `<scratch>/mb2-cc/01/`:
- `raw.pkl`: the archives, as read by my own reader
- `mine.pkl`: my collapse table
- `census_mine.pkl`: my census, float64
- `reps.pkl`: the committed replay logs
- `gpu_hist.pkl` and `gpu_replay.log`: my `train.train` GPU runs
- `page.txt` and `replicate.txt`: text extracted from the two pages

Sources:
- Artifact: `<worktrees>/chorus-collapse/docs/learned/chorus_collapse/index.html`
- Builder: `<worktrees>/chorus-collapse/tools/diagnose_chorus_collapse.py`: `_selectivity` at lines 159–166 is F3; Table 3's filter at lines 881–884 is F6.
- Trainer: `<worktrees>/weekend-runs/src/bugarach/learn/train.py`
- Tuning tool: `<worktrees>/weekend-runs/tools/tune_learned_vs_coact.py`
- Raw runs: `<darkroom>/bugarach/2026-09-18-fair-comparison-run/results/` and `<darkroom>/bugarach/2026-09-18-replicate-run-status/results/`
