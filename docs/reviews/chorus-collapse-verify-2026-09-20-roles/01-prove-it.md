GRANT 1 ok — Read, Grep, Glob, Bash

# Role 1 — Claim & data verifier ("Prove It")

**Artifact:** `<worktrees>/chorus-verify/docs/learned/chorus_collapse/index.html`
**Blindness honoured:** I read nothing under `docs/reviews/`. I also deliberately did not open `<darkroom>/bugarach/2026-09-18-*/report/review-roles*/` or `<darkroom>/bugarach/reviews/`, which exist and hold prior murderboard passes on the two *upstream* reports.

## What I actually did

Not an eyeball pass. Concretely:

1. **Re-derived `collapse_table.json` from scratch out of the raw run archives** (`fits.tar.gz`/`fits.zip` + `scores.tar.gz`/`scores.zip` in `<darkroom>/bugarach/2026-09-18-fair-comparison-run/results/` and `.../2026-09-18-replicate-run-status/results/`), re-implementing the collapse criterion from the archives rather than calling the builder's function. **1938 rows, 0 differences.**
2. **Re-derived `selections.json`** from `results/selections/{gated,ungated}/outer*/` and `meta.json`. Exact match.
3. **Re-ran every permutation test** with an independent RNG (`np.random.default_rng`, not the page's `RandomState(2026)`) at 40,000–200,000 shuffles instead of 1,999.
4. **Rebuilt the nets myself** (torch 2.14.0, `weekend-runs` worktree at `7a95e8a`) and re-measured the untrained-control onset responses from first principles.
5. **Rebuilt the page**: `tools/diagnose_chorus_collapse.py page` → **byte-identical** to the published file; the darkroom copy `<darkroom>/bugarach/2026-09-19-chorus-collapse/index.html` is **byte-identical** to the repo copy (sha256 `0dfdc1e5…`).
6. Checked the sources the page did *not* name: `meta.json`'s run declaration (the real source of record for grid, folds, seeds and unit membership), `progress.json` stage totals, `fits/*.run.json` (`role`, `train_folds`, `fitted_recordings`, `own_index`), and the git history between the two draws' commits.

---

## Claim ledger

`✓` = recomputed and agrees. Every row below was recomputed, not re-read.

### Provenance / integrity

| Claim | Where | Recomputed | ? |
|---|---|---|---|
| Page is what the tool builds from the committed JSON | §8 / test | rebuild byte-identical | ✓ |
| Repo copy == darkroom copy | §8 | sha256 identical, 570,131 B | ✓ |
| `collapse_table.json` follows from the runs | §8 | 1938/1938 rows re-derived from raw archives, 0 diffs | ✓ |
| `selections.json` follows from the runs | §8 | exact | ✓ |
| Runs live at the two named darkroom `results/` folders | §8 | both exist, both readable | ✓ |
| Replay "re-runs … on the GPU" | §8 | all 14 replays: `NVIDIA RTX A4000`, `deterministic=True`, torch `2.14.0+cu126` (= second draw's `progress.json`) | ✓ |
| PR 596 "open as of 2026-09-19" | §8 | `gh pr view 596` → **OPEN** today | ✓ |
| `7fc052d` on branch `replicate-run` | §8 | commit exists, is an ancestor of `replicate-run` | ✓ |
| #596 "tested plain chorus at lr 0.01 and 0.001" | §8 | `why_chorus.txt` @7fc052d: exactly those two | ✓ |
| Both draws ran the same code | implied | `git diff e8764aa 7a95e8a -- src/bugarach` = **empty** | ✓ |
| Draws use different recordings | §2 | recs-hash sets per draw: 10 each, **0 overlap** | ✓ |

### Counts, Table 1, Figure 2

| Claim | Recomputed | ? |
|---|---|---|
| 146 and 153 of 432 chorus_norm inner fits collapsed | 146 / 153 of 432 | ✓ |
| 292 of 396 at lr 0.03; 7 of 468 below | 292/396; 7/468 | ✓ |
| Grid rates 0.003, 0.01, 0.03 | `meta.json` `learned_axes` | ✓ |
| 24 configs × 3 seeds × 6 fold pairs = 432 | 24 cfg files/net; `tune_seeds=[0,1,2]`; `folds=4`→C(4,2)=6 | ✓ |
| **All 24 Table 1 cells** (counts, denominators, percents, both nets) | all 24 reproduce exactly | ✓ |
| Dashes = grid has no such config | confirmed (4×4@0.003, 8×6@0.003, 8×6@0.03 absent) | ✓ |
| lr 0.03 configs collapse in 42%–92% | true range 41.7%–91.7% | ✓* (see F4) |
| 900 steps 65% (141/216); 1,800 82% (59/72); 3,600 85% (92/108) | 141/216=65.3%, 59/72=81.9%, 92/108=85.2% | ✓ |
| 3,600-step configs all 6 deep | 33622c24 4×6, e86433df 8×6, 5d2026d1 8×6 | ✓ |
| gain 4×6@0.03 78%, other shapes 8%, 4×6@0.01 25% | 84/108=77.8%; 26/324=8.0%; 36/144=25.0% | ✓ |
| Figure 2 row totals 1/216, 6/252, 292/396; 3/144, 37/288, 110/432 | all exact | ✓ |
| 5 pairs of configs differ only in step count | 5 (4 chorus_norm, 1 chorus_gain_norm) | ✓ |

### Cross-draw overlap and statistics

| Claim | Recomputed | ? |
|---|---|---|
| 111 fits collapsed in both draws | 111 | ✓ |
| ~52 expected at the overall rate | 146·153/432 = **51.708** | ✓ |
| 111.5 expected at per-config rates | **111.5000** | ✓ |
| gain: 38 observed, 39.6 expected | 38; **39.611** | ✓ |
| seed clusters, p = 0.002 (2nd draw) | independent 40k perms → **0.0025** | ✓ |
| seed clusters, p = 0.083 (1st draw) | **0.0820** | ✓ |
| carry-over correlation 0.24 | **0.23805** (deterministic, exact) | ✓ |
| carry-over p = 0.147 | 200k perms → **0.1525** | ✓ |
| fold pair p = 0.938 (chorus_norm) | **0.9342** | ✓ |
| fold pair p = 0.434 (chorus_gain_norm) | **0.4554** (Δ 0.021 ≈ 1.9 MC SE at n=1999) | ✓ |

### Selection, refits (Table 2)

| Claim | Recomputed | ? |
|---|---|---|
| chorus_norm gated 7/1/0; ungated 3/5/0 | exact, from raw `selections/` | ✓ |
| gain gated 7/1/0; ungated 0/2/6 | exact | ✓ |
| No lr-0.03 pick for chorus_norm under either rule | 0 and 0 | ✓ |
| 4 refits collapsed; 2 chorus_norm (2nd draw, lr 0.01), 2 gain (lr 0.03, one per draw) | exactly those four rows; chorus_norm's two are cfg `75d44745`, outer fold 1, seeds 1 and 2 (distinct fits) | ✓ |
| Both gain collapsed refits came from F1-alone picks | both map to `rule=['ungated']` only | ✓ |
| Replicate report's † wording quoted correctly | byte-for-byte match with that report's footnote | ✓ |
| Replicate report gives 111 / 38 overlap | its Table 2: 111 fits, 38 fits | ✓ |
| Table 2 per-rule "refits that collapsed" = 2 under the budget | **✗ — see Finding 1** | ✗ |

### Census (§4, Figures 3–4)

| Claim | Recomputed | ? |
|---|---|---|
| Census recording quiet bg, seed 9000, trained on by no fit | `census.json` `recording="quiet:9000"`; `recording_seeds` = 2000–2047 | ✓ |
| 153 of 153 / 75 of 75 collapsed have a silent layer | 153/153, 75/75 | ✓ |
| 0 of 279 / 0 of 357 working do | 0/279, 0/357 | ✓ |
| 3 of 3 second-draw collapsed refits | 3 collapsed refits in census, all silent | ✓ |
| Figure 3: 126 chorus_norm + 41 gain below the 10⁻¹¹ floor | 126 / 41; all 167 are collapsed fits | ✓ |
| Separation: ≤ 0.00023 collapsed | max = **0.00022623** | ✓ |
| Separation: ≥ 0.82 working | min = **0.81986** — below 0.82 | ✗ (F4) |
| Collapsed chorus_norm vote median 0.40 | **0.3984** | ✓ |
| Working median 0.52 | **0.5163** | ✓ |
| Plain chorus ≤ 0.0003; (0.0003, 0.0002, 0.0003) | 0.000262 / 0.000234 / 0.000281 — and I **rebuilt untrained plain chorus myself** and got 0.00026/0.00023/0.00028 | ✓ |
| Untrained "this configuration" 0.02 to 0.03 | I rebuilt 4×6: 0.0317/0.0221/0.0332 | ✓ but see F3, F4 |
| 4 of 153 / 19 of 75 as deaf as plain chorus | 4 / 19 (cut = max(plain) = 0.000281) | ✓ |
| Sign rule "counted 1 working fit as dead" | **5** working fits across both nets | ✗ (F2) |
| Every collapsed fit's threshold is the grid floor 0.0001 | **own_index = 0 for all 902 collapsed fit-folds, both draws** | ✓ |
| logit(0.0001) = −9.2 | −9.2102 | ✓ |
| 2 working chorus_norm fits also sit at the floor | 2 | ✓ |

### Architecture (§4) — checked against `replicate-run` @ `7a95e8a`, the code that ran

| Claim | Source | ? |
|---|---|---|
| Head: 8 conv layers, 8 channels, kernel 3, dilation 1→128, GELU each, then a linear output | `_dilated_stack(…, depth=8)`: 8× `Conv1d(k=3, dilation=2**i)` + `GELU`, then `Conv1d(k=1)` | ✓ |
| Encoder shared per ROI; standardised over time; sigmoid vote 0–1; pool = mean, spread, top-m mean | `chorus.py` forward pass, line for line | ✓ |
| gain variant = learnable steepness + midpoint on the vote | `vote_gain` (init from grid) and `vote_bias` (init 0.5), both `nn.Parameter` | ✓ |
| Head size never tuned | `learned_axes` has lr, steps, roi_width, roi_depth, top_m (+vote_gain); no head axis | ✓ |
| Adam at default 0.9 / 0.999 | `torch.optim.Adam(params, lr=lr)` — defaults | ✓ |
| lr 0.03 = 30× Adam's suggested 0.001 | arithmetic; Adam paper default α=0.001 | ✓ |
| GELU dips no lower than −0.17 | min = −0.16999 at x ≈ −0.7517 | ✓ |
| 400-frame trim clears the receptive field (encoder 63 + head 255 = 318) | `receptive_field(6)=127`→63; `receptive_field(8)=511`→255 | ✓ |
| Ma & Yarats 2/(1−0.999)=2,000, ten times the 200-step ramp | arithmetic | ✓ |
| Sokar et al. dormant = mean abs activation relative to layer's | matches the paper's definition | ✓ (from knowledge, no PDF here) |
| Gulcehre et al.: dead ReLUs grow with learning rate, offline RL | **not verifiable here** — no PDF; role 2's call | — |

### Figure 1 / §1

| Claim | Recomputed | ? |
|---|---|---|
| Recording quiet:2012, 15 planted events | `trace.json`: `quiet:2012`, 15 events | ✓ |
| **Every** recording has 15 planted events | `n_planted` over all collapsed-fit scores: **{15}** only | ✓ |
| Held out from both fits' training | `fitted_recordings` of seeds 0 and 2 — 2012 in neither | ✓ |
| 25 calls working, 1 call collapsed | 25; 1 = `[0, 26796]` = the whole recording | ✓ |
| Collapsed output flat except at the ends | interior (400-frame trim) is **exactly one value**, 0.0726 | ✓ |
| Config = lr 0.03, 4 wide × 6 deep, 1,800 steps | `configs/chorus_norm/2736f584e7c224e3.json` | ✓ |
| Seed sets starting weights, crop order, and which 10 recordings | `fitted_recordings`: 10 each, all different per seed; pool of 48 identical | ✓ |
| Working fit is 1 of 18 second-draw fits of this config | 17 of 18 collapsed; the one working is seed 2, recs `ecf4b9b71a` = `SHOWN["working"]` | ✓ |
| Panel axis ticks −20/14 and −9/0; thresholds 2.9 / −9.2 | re-derived from the drawing code and data | ✓ |
| Collapse ⇒ F1 0.125 | **21,648 recording-scores across both draws: every one is (n_detected 1, n_hit 1, n_planted 15) → F1 = 0.125 exactly** | ✓ |

### Replays, §5, Table 3

| Claim | Recomputed | ? |
|---|---|---|
| 14 replays of 10 fits | 14 files, 10 distinct `(cfg, seed, recs)` | ✓ |
| Both as-run replays reproduce their checkpoints to the last bit | `max_abs_diff_vs_checkpoint == 0.0` for both | ✓ |
| First-batch output SD 0.0003 to 0.0025 | min 0.00033, max 0.00246 | ✓ |
| Head starts silent in 5 to 8 of 8 layers, every replay | min 5, max 8 | ✓ |
| Working fit awake by step 50; loss < 1.0 by step 220 | wake = 50; smoothed loss first < 1.0 at **step 220** | ✓ |
| Collapsed fit never wakes; ≥3 silent at its most awake; ends with 3 | never; min 3; end 3 | ✓ |
| lr 0.003 / 0.01 / 0.03+200-warmup train; 50-warmup does not | finals 0.072 / 0.086 / 0.167 / **1.499** | ✓ |
| 200-warmup head awake by step 80 | 80 | ✓ |
| 50-warmup: awake by 40, silent again from 110, ends with 3 | 40 / 110 / 3 | ✓ |
| Settled early: 60 of 62 early, 2 later, 0 recovered (chorus_norm) | 60 / 2 / 0, longer-twin total 62 | ✓ |
| gain: 8 early, 0 later, 3 recovered | 8 / 0 / 3 | ✓ |
| **All 8 Table 3 rows** (encoder, top m, steps, config collapse count, final loss, outcome) | every cell reproduces | ✓ |
| "Two of the fits are one training run counted twice" | 9ad792aa s1 (900) vs 2736f584 s1 (1800): **log entries 0–89 identical**, only the last differs (step 899 vs 900) — proven, not assumed | ✓ |
| 6 of 7 distinct runs train | 7 distinct; e86433df fails (1.696) | ✓ |
| Failure woke by step 60, ended 8 of 8 silent | 60; 8 | ✓ |
| Re-rolled luck would train 1.4 of 7 | Σ(1−share) over the 7 = 52/36 = **1.444** | ✓ |
| Highest single logged loss 4.0, an early spike | **3.985**, at step 130 of 899 | ✓ |
| Collapsed fits sit near 1.5, about a constant output's score | observed 1.50/1.50/1.70; best constant scores (1−p)·2ln2 ≈ **1.386** | ✓ (approximate, as stated) |
| The 3 lr-0.03 configs left out: 2 collapse least, 1 is a shorter twin | left out = 9987efaa (41.7%, lowest), a04f8e10 (50.0%, 2nd lowest), aace23d7 (8×6 m8 900 = shorter twin of the tried 5d2026d1) | ✓ |

---

## Findings

### F1 — Table 2's "refits that collapsed" is wrong for the budgeted rule, and its footnote asserts a false mechanism — **MAJOR**

**Location:** §3, Table 2, row `chorus_norm | under the false-alarm budget | … | 2 refits`, plus the table note *"Both selections can pick the same configuration, so a collapsed refit can count under both."*

**Issue.** The page defines collapse as *"exactly one call on every recording it was scored on."* The builder computes it at the fit's **own** threshold (`own_index`) and then attributes the refit to **every rule that picked its configuration**. But the two rules do not apply the same threshold. `results/selections/gated/outer1/chorus_norm.json` carries `threshold_index: 30` (p = 0.9716) onto the refit; the ungated record carries no threshold, so the refit uses its own (index 0).

I read the raw scores for those two refits (`chorus_norm/75d4474550026cfa/seed{1,2}__recs-cb0fd11ae4__fold1.json`):

| refit | at own threshold (idx 0) | at the budgeted threshold (idx 30) |
|---|---|---|
| seed 1 | `n_detected = 1` → collapsed | **`n_detected = 0` — calls nothing** |
| seed 2 | `n_detected = 1` → collapsed | **`n_detected = 0` — calls nothing** |

So under the false-alarm budget **0 refits collapsed** by this page's own definition; they failed the other way. The replicate report — which this page cites four lines earlier, and whose † footnote it quotes verbatim including the words *"or called nothing on the held-out fold"* — says exactly this: *"Under the budget the threshold sits above everything those refits output, so they call nothing."* The page quotes the half of the footnote it does not use and never reconciles it.

The note is worse than the cell: it tells the reader the *same collapsed refit* counts under both rules, when the true reason the same rows appear twice is that the two rules picked the same configuration and then thresholded the trained model differently.

**Fix.** Either (a) split the column into "refits that made one call" and "refits that called nothing", scoring each rule at *its own* threshold; or (b) retitle it "refits of this net that failed on the held-out fold (at their own threshold)" and replace the note with one sentence saying the budgeted rule carries a threshold from the inner fits onto the refit, so the same trained model calls nothing under it. **Verifiable against a source: yes** (raw `scores.zip` + `selections/gated/outer1/chorus_norm.json`).

---

### F2 — "counted 1 working fit as dead" understates by 5×, and the sign rule fails in the other direction too — **MAJOR**

**Location:** §4, *"…a rule that asked only whether a unit ever went positive counted 1 working fit as dead."*

**Issue.** The paragraph opens *"Every second-draw fit of **both nets** was reloaded…"* and the very next sentence gives both nets' numbers. But `n_sign[('chorus_norm', False)]` in the builder (line 1249) is chorus_norm only. Recomputed over `census.json`:

| net | working fits the sign rule would call dead |
|---|---|
| chorus_norm | 1 (`75d44745` seed 2, lr 0.01, 4×6 m8, logit SD 3.02) |
| chorus_gain_norm | **4** (`8df600b3` seeds 1 & 2; `ce159f3f` seed 1 ×2 — one with logit SD **94.8**) |
| **total** | **5** |

And the reverse error is unreported: the sign rule would also have **missed 3 collapsed chorus_gain_norm fits** (`min_share_positive > 0`). So the rule fails in both directions, and both facts make the page's choice of a variation test look *better* than the page claims for it. The sentence is also hard-coded singular ("1 working fit"), so it would read ungrammatically the moment the number moved — a sign the phrasing was fixed to an assumed value.

**Fix.** *"…counted 5 working fits as dead (1 chorus_norm, 4 chorus_gain_norm) and would have missed 3 collapsed chorus_gain_norm fits."* **Verifiable: yes** (`census.json` `min_share_positive`).

---

### F3 — the untrained comparator in §4 is the single lowest of the four encoder shapes, and it contradicts the project's own older record of the same quantity — **MAJOR**

**Location:** §4, *"one onset moves a vote by a median of 0.40, against 0.52 in working fits and 0.02 to 0.03 in this configuration untrained. For them the votes still respond…"*; Figure 4's row *"chorus_norm, untrained (3)"*.

**Issue (a): the older artifact disagrees.** `docs/learned/field_size_candidates/README.md` **at commit `7fc052d` — the very commit §8 cites** — gives, in its "Repairing chorus" table, *"vote change for one onset at initialisation"* for **chorus_norm = 0.22 to 0.51**. The page prints 0.02–0.03 for untrained chorus_norm and never mentions the 10× disagreement.

**Issue (b): I found the cause, and it is worse than a stale number.** I rebuilt the nets and ran the probe myself. The difference is **entirely encoder depth**, and the probe is completely insensitive to the ROI count and onset frame (1 ROI @ f2048 and 32 ROIs @ f2000 give identical values to 4 dp):

| untrained chorus_norm | 3 torch seeds | median |
|---|---|---|
| 4×4 (the registered default, what #596 measured) | 0.5072, 0.2166, 0.4455 | **0.446** |
| 8×4 | 0.5056, 0.5130, 0.5107 | **0.511** |
| 4×6 (**Figure 1's configuration — what the page quotes**) | 0.0317, 0.0221, 0.0332 | **0.032** |
| 8×6 | 0.0716, 0.1633, 0.0531 | **0.072** |

(4×4 reproduces the README's "0.22 to 0.51" exactly; 4×6 reproduces the page's controls exactly. Both records are right about different configurations.)

Now put the page's pooled medians beside the shape-matched untrained value:

| shape | untrained median | **collapsed** fits' median | working fits' median |
|---|---|---|---|
| 4×4 | 0.446 | **0.507** (n=42) | 0.513 |
| 8×4 | 0.511 | **0.514** (n=19) | 0.516 |
| 4×6 | 0.032 | 0.110 (n=52) | 0.523 |
| 8×6 | 0.072 | 0.334 (n=40) | 0.527 |

The page's medians (0.40 collapsed, 0.52 working) pool all four shapes; the untrained reference it sets them against is the **lowest shape by 14×**. For 4×4 and 8×4 — 7 of the 11 lr-0.03 chorus_norm configurations — an **untrained** net already reads 0.45–0.51, i.e. **at or above the collapsed median and indistinguishable from the working median**. So "one onset moves a vote by a median of 0.40" does not show that training made the votes respond; for half the grid it is the no-training value.

**What survives.** The claim the number is actually *used* for — *"For most chorus_norm fits it is not the failure diagnosed earlier in plain chorus"*, i.e. 0.40 ≫ 0.0003 — is sound and I verified it. The headline diagnosis is untouched. What fails is the untrained comparator and the inference *"For them the votes still respond"* as evidence of anything training did.

**Fix.** Drop the untrained comparator or give it per shape; state that the untrained response ranges 0.03–0.51 across the grid's four encoder shapes; and keep the comparison that carries the argument (against plain chorus's 0.0003). Add one clause reconciling the field_size_candidates README's "0.22 to 0.51" as the 4×4 default. **Verifiable: yes** (I reran it; README @7fc052d; `census.json` + `collapse_table.json` for the by-shape split).

---

### F4 — three stated bounds are rounded *inward*, so each claims slightly more than the data support — **MINOR**

**Location:** §6, §4, §2.

| stated | true | direction |
|---|---|---|
| "at least **0.82** in every working one" | min = **0.81986** | over-claims (0.81986 < 0.82) |
| "**0.02 to 0.03** … untrained" | 0.0221 to **0.0332** | range narrower than the data |
| "collapses in **42% to 92%**" | 41.7% to 91.7% | both ends inward |

(The companion bound "at most 0.00023 in every collapsed fit" is fine: true max 0.00022623.) Trivial in size, but a *bound* should round outward; as printed, each is literally false.

**Fix.** "at least 0.81", "0.02 to 0.04" (or two significant figures: 0.022 to 0.033), "41% to 92%". **Verifiable: yes.**

---

### F5 — §4 describes the earlier diagnosis's test as something it wasn't — **MINOR**

**Location:** §4, *"in an otherwise empty window of 32 ROIs and 4,096 frames … the earlier diagnosis's test."*

`tools/probe_untrained_response.py` @`7fc052d` probes a **(1, 1, T) one-cell** raster with the onset at `t//2 = 2048`, at the net's registered defaults. The page's `_onset_response` uses 32 ROIs, onset at frame 2000, and (for the controls) Figure 1's overrides. I confirmed the ROI count and onset frame make **no numerical difference**, so nothing downstream moves — but the sentence attributes this page's setup to the earlier work. **Fix:** "the earlier diagnosis's test, re-run here on 32 ROIs". **Verifiable: yes.**

---

### F6 — Table 2's refit counts have no denominator, and the page never says a pick is refit five times — **MINOR**

"2 refits", "0 refits" with no base. The run declares `refit_seeds = [0,1,2,3,4]`, so each (fold, rule) pick is refit at **5** training seeds; chorus_norm has 95 refit rows across both draws, chorus_gain_norm 115 (these reconcile exactly with `progress.json`'s `outer:` stage totals 40/55 and 60/55). The replicate report says "2 of its 5 refits"; this page drops the denominator, so the reader cannot size the failure. **Fix:** give the base ("2 of 95 refits") and state the 5-seed refit in §1. **Verifiable: yes.**

---

### F7 — "the whole recording" is part of the collapse definition but is not what was measured — **MINOR**

§1 defines collapse as *"exactly one call on every recording it was scored on: **the whole recording**, which matches one of the 15 planted events, F1 0.125."* The recorded criterion is only `n_detected == 1`. I verified F1 = 0.125 on **all 21,648** collapsed recording-scores in both draws, and I verified the span directly for Figure 1's fit (`[0, 26796]`). For the rest, "the whole recording" is an inference from flat output + floor threshold — solid for the second draw (census: every collapsed fit's logit SD ≤ 0.00023, every threshold at the grid floor), but there is **no census for the first draw**. **Fix:** say the span was measured on one fit and follows from the flat output elsewhere, or drop "the whole recording" from the definition sentence. **Verifiable: yes.**

---

### F8 — Table 1, Figure 2 and the headline counts pool step-count twins, which are the same training trajectory — **MINOR**

§2 and §5 both tell the reader *"the shorter one's fits are the longer one's stopped early"*, and the page correctly excludes twins from the permutation tests and de-duplicates them for "6 of 7 distinct runs". I verified the premise directly (the 900-step replay's log is entry-for-entry identical to the 1800-step replay's for its whole length). But Table 1, Figure 2 and "432 inner fits" do **not** exclude them, and neither the table note nor Figure 2's caption repeats the caveat:

| | as counted | distinct trajectories |
|---|---|---|
| chorus_norm, 2nd draw | 153 of 432 (35.4%) | 124 of 360 (34.4%) |
| chorus_norm, lr 0.03, both draws | 292 of 396 | 233 of 324 |
| chorus_gain_norm, lr 0.01, both draws | 37 of 288 | 26 of 252 |

Every conclusion survives ("a third" holds at 31.9%–35.4%). It is a denominator-honesty point: 72 chorus_norm and 36 chorus_gain_norm fit-rows per draw are re-counts of trajectories already in the table. **Fix:** one clause in Table 1's note. **Verifiable: yes.**

---

### F9 — Figure 4's caption can be misread — **MINOR**

*"3 starting seeds each, the second in Figure 1's configuration."* "The second" means the second **row**; all three chorus_norm controls use Figure 1's overrides (`make(**shown)` in a loop over `range(3)`). Read as "the second seed" it is wrong. Also, §4 says the sign rule asked "whether a unit ever went positive" — the code thresholds at `> 1e-3`, not `> 0`. **Fix:** "the second row is in Figure 1's configuration"; "ever rose above 0.001". **Verifiable: yes.**

---

## On the checks my role is specifically told not to skip

- **Missing / blank values.** No `NA`, no blanks. Every labelled column in all three tables resolves. Table 1's em-dashes are real absences and I confirmed each against `meta.json`'s `learned_axes` product: those four (net, shape, lr) cells genuinely have no configuration. Label vocabulary (net names, lrs, shapes, step counts, top-m, vote gains) matches the run declaration exactly; 24 configurations per net, 864 inner fits per net, every stage total reconciling with `progress.json`.
- **Regeneration diff.** The page is a regeneration from committed JSON: it rebuilds byte-identically, and the JSON itself re-derives exactly from the raw archives. Against the older artifact it corrects (the replicate report), the only substantive difference is the *reading* of the 111 overlap, which is the page's stated purpose; the numbers agree (146/153/111, 75/75/38). The one place an older artifact disagrees and is not reconciled is F3.
- **Source of record for unit membership.** It exists and I located it: `results/meta.json` `declaration` (folds, `tune_seeds`, `refit_seeds`, `recording_seeds`, `configurations`) plus per-fit `*.run.json` (`role`, `train_folds`, `fitted_recordings`, `threshold_recordings`). The unit count reconciles against `progress.json` in every stage. **No withdrawn units**, no contamination note on these runs. On independence: the page does **not** treat correlated units as independent — it identifies the two ways units share a "subject" (same training seed across draws; step-count twins sharing a trajectory), tests the first rather than assuming it, and excludes the second from the tests. That is the right handling and it is documented. F8 is the one place the disclosure does not reach the tables.
- **Retractions.** No correction or retraction attaches to the sources this page builds on. The claim it inherits from PR 596 (plain chorus's votes do not respond, ≤ 0.0003) is live, and I reproduced it from scratch rather than trusting either record.

## Net assessment

The page's central diagnosis is, as far as I can recompute it, **sound and unusually well-evidenced**: every count, every p-value, every median, every replay number and every architectural statement reproduces, most of them from the raw run archives rather than from the JSON the page ships. Two independent re-derivations (the collapse table from the archives; the untrained controls from rebuilt nets) came out exact. Nothing I found threatens the conclusion that lr 0.03 collapses chorus_norm, that the head goes silent, or that a 200-step warm-up prevents it.

Three findings need action before this goes out in a public repo: **F1** (a table cell that is wrong under the page's own definition, with a footnote asserting a false mechanism), **F2** (a 5× understatement in a sentence justifying a methodological choice), and **F3** (a comparator chosen from the one encoder shape where it flatters the argument, contradicting the project's own earlier record of the same quantity without noticing).

## Files that matter

- Artifact: `<worktrees>/chorus-verify/docs/learned/chorus_collapse/index.html`
- Builder: `<worktrees>/chorus-verify/tools/diagnose_chorus_collapse.py` (F2 is line 1249, `n_sign[('chorus_norm', False)]`; F1 is `bad_by_rule`, lines 951–955, keyed on which rule *picked the configuration*, with collapse taken at `own_index`)
- Data: `…/docs/learned/chorus_collapse/{collapse_table,census,selections,trace}.json`, `…/replays/*.json`
- Older artifact that disagrees (F3): `docs/learned/field_size_candidates/README.md` at commit `7fc052d`, section "Repairing chorus"; probe `tools/probe_untrained_response.py` at the same commit
- Upstream report quoted: `<worktrees>/chorus-verify/docs/learned/tuned_vs_coact/replicate1/report.html`, section 8
- Raw ground truth: `<darkroom>/bugarach/2026-09-18-fair-comparison-run/results/` and `<darkroom>/bugarach/2026-09-18-replicate-run-status/results/` (resolved via `bugarach.paths.darkroom()`; never hardcoded)
- Nets/trainer as run: `<worktrees>/weekend-runs` @ `7a95e8a` (= the second draw's `progress.json` commit)

I wrote only into my scratchpad and modified nothing in the repo or the darkroom.
