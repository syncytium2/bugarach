GRANT 6 ok — Read, Grep, Glob, Bash, WebSearch, WebFetch

(I also hold SubagentHandback, which is the report channel and not an editing tool. I hold no Edit, Write or NotebookEdit.)

## Role 6 (RTFM): findings on `chorus_collapse/index.html` and `tools/diagnose_chorus_collapse.py`

**Summary.** The replay is faithful to `train()`, and the warm-up counterfactual is clean. Both hooks and `logit_sd` compute what they claim: a CPU re-run reproduced every census number exactly, for all 864 fits.

What does not hold up is the definition of "dead". The page counts a head layer as dead when no unit outputs more than 0.001. That is a sign test. GELU has a negative lobe that still passes a gradient, so the test does not show whether signal or gradient gets through the layer. The main finding survives a stricter definition, and actually separates better under it. But four things rest on the sign test and are wrong or overstated:
- the page's counts;
- the "passes only the residue, so the output hardly moves" mechanism;
- the "dies layer by layer" framing;
- Figure 4's caption, which its own data contradict.

**How I grounded it**
- **PyTorch 2.14.0+cu126**, from the docstrings installed in the venv the runs used. The web docs only returned redirect pages.
  - Adam: m̂ₜ = mₜ/(1−β₁ᵗ) and v̂ₜ = vₜ/(1−β₂ᵗ), and the step is θ −= γ·m̂/(√v̂+ε). Bias correction depends on t only, never on γ.
  - `register_forward_hook`: the hook signature is `hook(module, args, output)`. Returning None leaves the output unchanged; a return value replaces it.
  - `nn.GELU`: GELU(x) = x·Φ(x), `approximate='none'`, output shape = input shape.
- **Hendrycks & Gimpel, arXiv 1606.08415 v5** (ar5iv HTML; the PDF would not extract). They describe GELU as "non-convex, non-monotonic", and say that unlike ReLU it "can be both negative and positive".
- **GELU values, computed:** minimum −0.170 at x = −0.752. GELU′ is −0.083 at x = −1 and x = −2, −0.012 at −3, −5e-4 at −4, and 7e-6 at −5.
- **Lit-cache:** `fetch_paper.py` is not vendored in this repo, so I fetched the paper by hand. Nothing needs to go on the want-list.

**CPU checks only; no GPU was used.** I reloaded all 864 second-draw inner fits (chorus_norm and chorus_gain_norm) from `fits.zip` and ran each on the census recording (quiet background, seed 2000), recording every head GELU's input and output. The census's `min_head_alive` and `logit_sd` were reproduced for 864 of 864 fits. The per-fit results are in `<scratch>/mb-cc/06/altdef.json`.

## Findings

Each row gives location · issue · severity · suggested fix · verified against a source.

**1. Page §3 ("Call a head layer dead…", "152 of 153", "1 of the 279"), the census rule `DEAD = 1e-3` (tool line 53), and the chorus_gain_norm counts "60 of 75" / "3 of 357"**
- **Issue:** "No unit outputs more than 0.001" tests the sign of the output. It does not test whether a signal or gradient passes. I reloaded the collapsed replay fit (2736f584, seed 0, recs 3a17721a7a), where the page counts layers 2, 3, 5 and 7 as dead:
  - Layer 2 really is saturated: every input is ≤ −3.14, and the largest per-unit spread over time is 2.3e-5.
  - Layers 3 and 5 sit in the steepest part of GELU's negative lobe. Their inputs run from −1.18 to −0.35 and from −1.95 to −0.09, where |GELU′| reaches 0.23 and 0.43. Their outputs are flat because their input is flat, not because they are switched off.
  - The one "working fit with a dead layer" (75d44745, seed 2, recs fcbbb6d968) has inputs to that layer between −11 and −0.4, and its output still varies over time (per-unit SD 0.05). The rule counts it as dead even though signal passes through it.
- **Recount under two stricter definitions, all 432 fits per net:**

  | Definition of a dead layer | chorus_norm: collapsed / working | chorus_gain_norm: collapsed / working |
  |---|---|---|
  | The page's rule | 152 of 153 / 1 of 279 | 60 of 75 / 3 of 357 |
  | Saturated: every unit's input below −3 over the whole recording | 120 of 153 / 0 of 279 | 42 of 75 / 0 of 357 |
  | Flat: every unit's output varies with SD below 1e-3 | 142 of 153 / 0 of 279 | 51 of 75 / 0 of 357 |

  The conclusion survives and separates more cleanly. The page's exact counts, its "exception" fit, and the sentence "A dead layer passes only the small negative residue of its GELUs, so the output hardly moves" are products of the sign rule.
- **Severity:** major.
- **Fix:** define a dead layer by transmission, either the flat rule (every unit's SD over time below ε) or the saturated rule (every input below about −3, where |GELU′| < 0.012), and recount. Alternatively keep the sign rule but name it for what it measures ("no unit ever outputs a positive value") and drop the causal "so". In either case the page should say that flat downstream layers are a consequence of one saturated layer.
- **Verified against a source:** yes (the PyTorch GELU definition, Hendrycks & Gimpel, and the CPU reload).

**2. Figure 4's caption ("the working fit's does not"); the answer box ("starts losing whole layers by step 30"); §4 ("a dead layer by step 30")**
- **Issue:** The working fit's own as-run replay has a dead layer (by the page's rule) at step 10, which is earlier than the collapsed fit's first one at step 30, and again at steps 70–90 and 120–130: 6 of 181 logged steps. Two warm-up fits that went on to train also had dead layers at step 110. Early dead layers therefore come back and do not tell the two fits apart. The figure's own data contradict its caption. This is what GELU's non-zero negative-lobe gradient allows, and it undercuts "units never switch on".
- **Severity:** major.
- **Fix:** make the caption something like "the collapsed fit's head keeps its dead layers and adds more; the working fit's recover within about 130 steps", and give the working fit's first transient dead layer in the text. Better still, re-log with the transmission definition from finding 1.
- **Verified against a source:** yes (the replay JSONs).

**3. Does `replay()` reproduce `train()`?**
- **Issue:** I found no divergence. Checked item by item:
  - Seeding order is the same: `deterministic_cuda` → `manual_seed` → `pin_threads` → model built on the CPU → `.to(cuda)` → Adam.
  - The data list is the same: `fold_maker(planted, run.json["recordings"])` with the default n_val=2. `run.json["recordings"]` is the tune tool's `job["train_recordings"]`, and the tune tool's `_run_fit` also calls `fold_maker` with the default.
  - Seeds `TRAIN_SEED_BLOCK + seed*1000 + i` match; dt = 0.1 and stream = None match `train`'s defaults, which the tune tool does not override.
  - The regime map matches the tune tool's `BENCH_REGIMES`.
  - `pos_weight` is the same float ((1 − pos) against (1.0 − pos)), built on the CPU as float32 and then moved.
  - Crop sampling and every `rng` call match, and the per-step order matches.
  - The hooks return None and draw no random numbers.
  - The checkpoint stores float32 values as JSON floats, which round-trip exactly, so "max diff 0.0" is a real check.
  - Both draws ran on an RTX A4000 with torch 2.14.0+cu126 and driver 582.78.

  The weakness is robustness. `replay` hard-codes cuda, dt, stream and n_val rather than asserting them against the checkpoint's `training` record, and it does not record its own GPU or torch version. Counterfactual replays have no bit-for-bit check, so they rely on that provenance.
- **Severity:** minor.
- **Fix:** assert that `training.device == "cuda"`, that `dt_sec`, `stream` and `threads` match, and that the GPU name matches. Write the replay's torch version, GPU and `are_deterministic_algorithms_enabled()` into the replay JSON.
- **Verified against a source:** yes (the code on both branches and the runs' `meta.json`).

**4. Page §6 Limits ("Replays are exact for fits as run (checked against the checkpoints)")**
- **Issue:** Only two fits were replayed as run and checked. The 8 fits in Table 2 were replayed only with the warm-up, never as run, so no checkpoint check covers them. The sentence reads as though all replays were verified.
- **Severity:** minor.
- **Fix:** "The two as-run replays reproduced their checkpoints exactly; the other eight fits were replayed only with the warm-up."
- **Verified against a source:** yes.

**5. Warm-up counterfactual (tool lines 237–239); Figure 3's heading ("depending only on its early learning rate")**
- **Issue:** The warm-up changes only the size of each step. Adam's bias correction depends on t alone, and setting `param_groups["lr"]` on each step is exactly what an LR scheduler does. The initial weights and the crop stream are also unchanged: all five replays of 2736f584 seed 0 start with loss 1.49 and output spread 0.0008 at step 0. So the counterfactual is clean. The lr 0.01 and 0.003 replays, however, change the rate for the whole run, not just the early part. Only the two warm-up curves support "early".
- **Severity:** minor.
- **Fix:** "…depending on its learning rate; the warm-up curves show it is the early steps that matter."
- **Verified against a source:** yes (the Adam docstring and the replay JSONs).

**6. Hooks: census line 150 and replay line 216**
- **Issue:** No fault. The head GELU output has shape (B, 8, T). The census's `o[0].any(dim=1)` and the replay's `o.any(dim=2).any(dim=0)` both reduce to one value per channel, i.e. the share of the 8 units. `m.head` holds exactly 8 GELUs: `head_depth` = 8 and `head_width` = 8 are defaults that no configuration overrides. One caveat for the reader: chorus_norm standardizes over whatever window it sees. Figure 4 measures on 3 training crops of 4,096 frames each, while Figure 2 measures on one 26,720-frame recording, so their counts are not on the same input.
- **Severity:** minor (only the caveat).
- **Fix:** add one clause saying the two figures measure on different windows.
- **Verified against a source:** yes (`chorus.py`, `_dilated_stack`, the configs, and the exact reproduction).

**7. `logit_sd` (tool lines 153 and 159, and 247)**
- **Issue:** Correct. The model returns (B, T) after `squeeze(1)`. `[0]` then gives (T,), and `.std()` is the unbiased SD over the recording's frames. The replay's value is taken over all 3 × 4,096 values of the batch, which matches "on the first batch".
- **Severity:** none.
- **Fix:** none.
- **Verified against a source:** yes.

**8. Collapse rule (tool line 99 against `make_replicate_report.py` line 266)**
- **Issue:** For inner fits the two rules are identical: one call on every row, at `own_index`, on every fold scored. Keying by `recs` rather than by fold pair is one-to-one for inner fits. For refits, though, the tool uses the `own_index` rule, while the report's † comes from a different rule: `failed_training_signature` (F1 within 0.01 of 0.125, with the threshold at the grid floor, at the selection's threshold index) or `f1_was_nan`. I checked the 4 collapsed refits:
  - All 4 carry `failed_training_signature` under ungated selection, at threshold index 0.
  - The two chorus_norm refits are `f1_was_nan` under gated selection, at threshold index 30.

  So "each puts a †" is true, but it is true under a different rule.
- **Severity:** minor.
- **Fix:** say that the † is the report's F1-and-threshold flag and that it agrees for these four refits.
- **Verified against a source:** yes (`results.json` for both draws).

**9. Page §3 ("the fit's threshold falls to the bottom of its grid")**
- **Issue:** Verified. All 153 of 153 collapsed chorus_norm fits and all 75 of 75 collapsed chorus_gain_norm fits have threshold 1e-4, the grid floor. Two working chorus_norm fits also sit there.
- **Severity:** none.
- **Fix:** none.
- **Verified against a source:** yes (the checkpoints).

**10. Page §2 ("by depth… 6 layers 85%", "Nothing else in the fit's identity matters") and the answer box ("It happens in the first steps")**
- **Issue:** At lr 0.03, the collapse rate rises with training length. The three 3,600-step configurations are all depth 6, so the depth effect the page reports is confounded with training length, and training length is not reported. A higher collapse rate after longer training also suggests some fits die, or fail to recover, after the first steps. The one replay does not test that.

  | Steps (lr 0.03) | Collapsed inner fits |
  |---|---|
  | 900 | 141 of 216 (65%) |
  | 1,800 | 59 of 72 (82%) |
  | 3,600 | 92 of 108 (85%) |

- **Severity:** minor.
- **Fix:** report the rate by training length and note the confound with depth. Soften "It happens in the first steps" to "In the replayed fit, it starts in the first steps".
- **Verified against a source:** yes (`collapse_table.json`).

**11. Page §3's GELU gloss ("squeezes negative input to small values near zero")**
- **Issue:** GELU is non-monotonic. It reaches −0.17 at x ≈ −0.75 and has a non-zero gradient throughout the lobe (Hendrycks & Gimpel). The gloss hides the very property behind findings 1 and 2.
- **Severity:** minor.
- **Fix:** "…passes positive input and maps negative input to a small negative dip (at least −0.17), which still carries a gradient".
- **Verified against a source:** yes.

**12. Page §3's vote-gain figures ("end a median 3%… against 13%") and tool line 162**
- **Issue:** `vote_gain_moved` is the largest relative change across the fit's `roi_width` gains, not a change in "the vote gain". The median is then taken across fits.
- **Severity:** minor.
- **Fix:** "the largest of each fit's vote gains moved a median 3%…".
- **Verified against a source:** yes (the code).

## Checked and clean
- Both draws ran on the same GPU model, torch version and driver, which supports "the draws … differ only in their recordings".
- The `--code` path handling works: `make_replicate_report` puts the tool repo's own `src` on the path, but `_use_code` inserts `--code` ahead of it before bugarach is imported. If that order ever breaks, the ARCHITECTURES check refuses to run rather than quietly building plain chorus.
- The replay's "same initial weights, same data" claim holds.

## Files
- Artifact: `<worktrees>/chorus-collapse/docs/learned/chorus_collapse/index.html`
- Tool: `<worktrees>/chorus-collapse/tools/diagnose_chorus_collapse.py`
- Trainer and nets: `<worktrees>/weekend-runs/src/bugarach/learn/train.py`, `nets/chorus.py`, `nets/__init__.py`, `checkpoint.py`
- Tune caller: `<worktrees>/weekend-runs/tools/tune_learned_vs_coact.py` (`_run_fit`, lines 798–870)
- Recount data: `<scratch>/mb-cc/06/altdef.json`, one row per fit with the page's rule, the saturated rule, the flat rule and the threshold.
