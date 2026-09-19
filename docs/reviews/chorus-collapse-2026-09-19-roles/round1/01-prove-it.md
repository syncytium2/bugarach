GRANT 1 ok — Read, Grep, Glob, Bash

# Role 1, Prove It: round 1 on `<worktrees>/chorus-collapse/docs/learned/chorus_collapse/index.html`

Every number on the page recomputes, and I found no mismatched value. I rebuilt the collapse table from the raw archives with my own zip/tar reader, not the builder's `R.Archive`. My table has the same 1,938 keys as `collapse_table.json`, and none of its fields differ (collapsed, role, pair, lr, width, depth). I also re-ran the as-run replay 2736f584 seed 0 on the GPU into scratch. It gives max |replay − checkpoint| 0.0, and its log is identical to the committed one.

The problems are in the inferences drawn from the numbers. Five are major.

## Claim ledger

`match (proxy)` means I recomputed an approximation, not the exact quantity. Every other `match` is a recomputation of the quoted value.

| # | Quoted on page | Cited source | Recomputed | Verdict |
|---|---|---|---|---|
| 1 | chorus_norm collapses in 292 of 396 inner fits at lr 0.03, 7 of 468 below | raw archives | 292/396; 7/468 | match |
| 2 | Table 1, chorus_norm: 1/216, 6/252, 292/396; draws 146/432 and 153/432; same fit in both 111 | raw archives | identical | match |
| 3 | Table 1, chorus_gain_norm: 3/144, 37/288, 110/432; draws 75/432 and 75/432; same fit in both 38 | raw archives | identical | match |
| 4 | 24 configurations × 3 seeds × 6 fold pairs = 432 per net per draw; 36 per configuration in Figure 1 | configs, run.json | 24 configurations (one is the untuned default, 9c65e498); 18 per configuration per draw; 6 pairs; 2 scored folds per fit | match |
| 5 | Replicate report: 146, 153 and 111 | report Table 2 | same | match |
| 6 | One call = 1 of 15 planted events, F1 0.125 | score rows | every collapsed recording in both draws is (15 planted, 1 hit) | match |
| 7 | lr 0.03 configurations collapse in 42% to 92% of fits | raw | 0.417 to 0.917 | match |
| 8 | Width 4: 80% (172/216); width 8: 67% (120/180); depth 4: 60% (108/180); depth 6: 85% (184/216) | raw | 172/216 = 0.796, 120/180, 108/180, 184/216 | match |
| 9 | By seed 34%, 32%, 38%; by fold pair 30% to 38% | raw | 97/288, 93/288, 109/288; pairs 0.299 to 0.375 | match |
| 10 | Refits: 95 = 35 at lr 0.003, 60 at lr 0.01, 0 at lr 0.03 | raw run.json roles | 40 + 55 = 95; lr counts 35/60/0 | counts match, description wrong (F4) |
| 11 | "Tuning never chose a lr-0.03 configuration for chorus_norm" | results.json | 16 selections (untuned, ungated and gated × 4 folds × 2 draws, untuned excluded): 10 at 0.003, 6 at 0.01, 0 at 0.03 | match |
| 12 | 4 collapsed refits: chorus_gain_norm first draw 0.03; chorus_gain_norm second draw 0.03; chorus_norm second draw 0.01 × 2 | raw | 67689e66 s3; 7cea38e2 s1; 75d44745 s1 and s2 | match |
| 13 | Those refits put a † beside their net in the replicate report | report Table 1 | † on chorus_gain_norm (F1-alone, both draws) and chorus_norm (second draw, both columns) | match (loose, N11) |
| 14 | Removed 11 of 24 configurations from contention | raw scores | Mean inner F1 per configuration: all 11 lr-0.03 configurations (0.16 to 0.42) rank below all 13 others (0.67 to 0.75) | match (proxy) |
| 15 | Census: 152 of 153 collapsed fits have a dead layer; 1 of 279 working fits does | census.json; checked against my table | same; census has 0 collapsed-flag mismatches and covers 974 of 974 fits | match |
| 16 | Median output spread 0.0055 collapsed vs 5.20 working; odd working fit 3.1; odd collapsed fit lr 0.003, 0.047 | census.json | 0.00547 / 5.198; 3.121; lr 0.003, 0.0472 | match |
| 17 | chorus_gain_norm: 60 of 75 dead vs 3 of 357; the other 15 split 2/8/5 by lr; vote gain moved 3% vs 13% | census.json | same; 0.034 vs 0.131 | match |
| 18 | Refits: the second draw's 3 are in the census, all 3 with a dead layer | census.json | 3, all with min_head_alive 0 | match |
| 19 | Spread separates the groups: at most 0.13 collapsed, at least 0.80 working | census.json | max 0.1322, min 0.8034 | mismatch in rounding (F6) |
| 20 | The threshold falls to the bottom of its grid | second-draw run.json, meta grid | 231 of 231 collapsed fits at own_index 0 (grid of 41, lowest first) | match (first draw not checked) |
| 21 | Replays reproduce the checkpoints to the last bit | replays; my GPU re-run | 0.0 for both; my re-run is bit-identical | match |
| 22 | Spread 0.0008 and 0.0011 on the first batch | replays | 0.00080, 0.00105 | match |
| 23 | Dead layer by step 30; 4 of 8 at the end vs 0 in the working fit | replays | 30; 4; 0 | match, but framing is refuted (F2) |
| 24 | Rescued at lr 0.01, lr 0.003 and 0.03 with 200 warm-up steps; not with 50 | replays | final loss 0.143, 0.199, 0.162; 1.506 | match |
| 25 | Table 2 final losses 0.07 / 0.11 / 0.18 / 0.09 / 0.14 / 0.11 / 1.70 / 0.09; 7 of 8 train | replays | 0.073 / 0.112 / 0.179 / 0.087 / 0.144 / 0.113 / 1.696 / 0.094 | match, but the fits are not independent (F5) |
| 26 | e86433df collapsed in 31 of its 36 fits | raw | 31/36 | match |
| 27 | Collapsed fits sit near 1.5; the as-run loss never leaves its start | replays | first 5 logged 1.458, last 5 1.517 | match |
| 28 | Warm-up tried on 9 collapsed fits | replays | 8 + 1 | match |
| 29 | Architecture: shared per-cell encoder; standardized over time; sigmoid vote; 3 pooled statistics; head of 8 layers × 8 GELU units, never tuned | chorus.py, `_dilated_stack`, all configs | Code matches: norm over dim 2 (time); mean, spread and top-m mean; 8 × (Conv1d + GELU) then a 1×1 output conv; every config head 8 × 8 | match |
| 30 | Dead = no unit above 0.001 over the recording (census) or the training batch (replays) | builder hooks | GELU output is (B, 8, T); the hooks reduce over time (and batch) per unit, so values move in 1/8 steps | match |
| 31 | Draws share configurations and seeds and differ only in recordings | configs of both draws | the 24 + 24 config JSONs are identical | match |
| 32 | "the one parameter chorus_gain_norm adds" | chorus.py | it adds `vote_gain` **and** `vote_bias`; the metric is the largest change across channels | mismatch (F7) |
| 33 | "the failure PR #596 fixed … at every learning rate" | why_chorus.txt, gh | PR #596 is OPEN; why_chorus.txt tests lr 0.01 and 0.001 only | mismatch (F8) |
| 34 | The page is rebuilt by a test; darkroom copy exists | tests, darkroom | `tests/test_diagnose_chorus_collapse.py` exists; darkroom index.html, census.json and collapse_table.json are byte-identical to the repo copies | match |
| 35 | Missing values | tables | table: `vote_gain` null only for chorus_norm (correct, it has none); census: no nulls or NaN; `vote_gain_moved` present on all chorus_gain_norm rows | match |

## Findings

The last field on each row says whether I checked the finding against a source.

**F1 · §1, "the collapse follows the fit's configuration and starting weights more than its data" · major**
- **Issue:** the page's own 111 refutes the "starting weights" half. If collapse depended only on the configuration, with each draw's per-configuration rate held fixed, the expected overlap is Σ c₁c₂/18 = **111.5** (112.2 given configuration + seed). Observed: 111. The same holds for chorus_gain_norm: 38 observed, 39.6 expected. Within a configuration, which fit collapses shows no agreement between draws beyond chance.
- **Fix:** say that the collapse follows the configuration. Within a configuration, which fits collapse is no more alike across draws than chance, so the 111 is what the per-configuration rates predict. Drop "starting weights".
- **Verified against a source:** yes.

**F2 · §4, Figure 4 caption ("the working fit's does not"), and the box line "starts losing whole layers by step 30" · major**
- **Issue:** the working as-run replay (2736f584 s2) has a dead head layer at **step 10**, earlier than the collapsed fit's step 30, and again at steps 70–90 and 120–130. The warm-up-rescued fits 2736f584 s1 and 9ad792aa s1 also lose a layer at step 110 and still train. The collapsed fit's count also swings between 0 and 3 until about step 1,660. Early loss of a layer does not separate the two fits; recovery does, and the page's own replay data show it.
- **Fix:** retitle Figure 4. Rewrite the claim: both fits lose a head layer in the first steps; the working fit recovers by step 140; the collapsed fit never does and ends with 4 dead.
- **Verified against a source:** yes.

**F3 · §2 "chorus_gain_norm shows the same pattern, milder"; §5 "drop lr 0.03 from the chorus grids, which accepts the smaller grid tuning already used in effect" · major**
- **Issue:** for chorus_gain_norm the learning rate does not separate the configurations.
  - At lr 0.03 its per-configuration shares run from 0% to 86%; two lr-0.03 configurations never collapse.
  - Below 0.03 they reach 33%.
  - Within lr 0.03, depth separates them: depth 6 is 84/108 (78%), depth 4 is 26/324 (8%).
  - Tuning **did** choose lr 0.03 for chorus_gain_norm: 6 of 16 selections (results.json), which is 30 of its 115 refits. Both of its collapsed refits come from those lr-0.03 choices.
- **Fix:** limit the lr-separation and "smaller grid in effect" claims to chorus_norm. State that chorus_gain_norm's tuning used lr 0.03, so dropping lr 0.03 would change chorus_gain_norm's selections.
- **Verified against a source:** yes.

**F4 · §5 "its 95 refits … (the chosen configurations, trained afresh …) are 35 at lr 0.003, 60 at lr 0.01" · major**
- **Issue:** 40 of the 95 are the refits of the **untuned default** configuration, 9c65e498 at lr 0.01, 20 per draw. The `untuned` entry refits it in every fold, so tuning did not choose them. Only first-draw fold 0 also selected it (ungated).
  - Tuning's own choices: 10 selections at lr 0.003 and 6 at lr 0.01.
  - By refit: 35 at 0.003 and 25 at 0.01. That is 60 distinct fits, of which 5 are shared with the untuned default.
- **Fix:** separate the untuned default's refits from the chosen configurations', or count selections instead of refits.
- **Verified against a source:** yes (results.json).

**F5 · §4 and Table 2: "8 more collapsed fits from 8 lr-0.03 configurations: 7 of them train"; also the §5 and todo line "rescued 7 of 8" · major**
- **Issue:** 2736f584 s1 and 9ad792aa s1 have the same architecture (width 4, depth 6, top_m 4), lr, seed and recordings. They differ only in step count (1,800 vs 900), and 90 of 9ad792aa's 91 logged losses are bit-identical to 2736f584 s1's. They are one training trajectory counted twice, so the independent evidence is 6 of 7.
- **Related:** 2 of the 11 lr-0.03 chorus_norm configurations duplicate another's architecture (2736f584/9ad792aa and 5d2026d1/aace23d7). Across same-architecture groups that differ only in step count, the collapse status agrees in 142 of 144. Figure 1's lr-0.03 row therefore has 9 independent architectures, not 11.
- **Fix:** report 6 of 7 independent trajectories, or replace 9ad792aa with a distinct fit. Note in Figure 1 that step count does not affect the early collapse.
- **Verified against a source:** yes.

**F6 · §5 "at most 0.13 in every collapsed fit" · minor**
- **Issue:** the maximum is 0.1322, so an upper bound rounded down is false by 0.002.
- **Fix:** write "below 0.14", or print three digits.
- **Verified against a source:** yes.

**F7 · §3 "Their vote gains, the one parameter chorus_gain_norm adds" · minor**
- **Issue:** chorus_gain_norm adds `vote_gain` and `vote_bias`, each with `roi_width` channels. `vote_gain_moved` is the largest relative change across channels.
- **Fix:** "the learnable vote gain (one of the two parameters it adds); its largest change across channels ends a median 3%…".
- **Verified against a source:** yes (chorus.py lines 93–95; builder line 162).

**F8 · Box and §3 "the failure PR #596 fixed … at every learning rate" · minor**
- **Issue:** PR #596 is still OPEN (gh). why_chorus.txt tested lr 0.01 and 0.001 only; "at any learning rate" comes from its commit title, not from its measurements.
- **Fix:** "diagnosed in PR #596 (open; the repair is on branch replicate-run)"; "at the two learning rates tried".
- **Verified against a source:** yes.

**F9 · Figure 3 caption "The 50-step warm-up retraces the fit as run almost exactly" · minor**
- **Issue:** the loss curves agree (smoothed mean |Δ| 0.016, max 0.27), but the heads differ: 2 vs 4 dead layers at the end, first dead layer at step 80 vs 30.
- **Fix:** "its loss retraces…".
- **Verified against a source:** yes.

**F10 · Figure 3 caption "depending only on its early learning rate" · minor**
- **Issue:** the lr 0.01 and 0.003 arms change the learning rate for all 1,800 steps. Only the warm-up arms isolate "early".
- **Fix:** "on its learning rate, and at lr 0.03 on its first 200 steps".
- **Verified against a source:** yes.

**F11 · §5 "each puts a † beside its net" · minor (nit)**
- **Issue:** the two chorus_norm refits share one flagged fold, and its † also covers "called nothing" under the budget.
- **Fix:** "they are behind the † on chorus_norm (second draw) and chorus_gain_norm (both draws)".
- **Verified against a source:** yes.

**F12 · Companion todo `docs/todo/2026-09-19-chorus-grids-put-a-third-of-their-fits-where-they-cannot-train.md` · major (companion doc, not the page)**
- **Issue:** four claims in it are false:
  - "A dead head layer makes the output a constant": the page shows a working fit with a dead layer and output spread 3.1.
  - "Tuning never chose a lr-0.03 configuration" is unqualified: false for chorus_gain_norm (see F3).
  - "Drop lr 0.03 … makes the declared grid the one tuning already used": false for chorus_gain_norm.
  - The title "The chorus grids put a third of their fits": chorus_gain_norm is 150/864, which is 17%.
- **Fix:** qualify each to chorus_norm, and correct the causal line.
- **Verified against a source:** yes.

## Surfaces checked with no finding

- **Source of record for group membership:** these are simulated recordings. The design record is the configs, meta.json's declaration and results.json. I consulted all three, and there is nothing withdrawn to reconcile.
- **Companion docs:** the INDEX row is consistent with the page. The replicate report's counts are consistent too. It also says "the same fits largely fail in both (111…)", and F1 applies to that sentence.
- **Code the page describes:** `train.py` has no warm-up, scheduler or gradient clipping, so "add a warm-up" is a real change. The local chorus.py is on branch replicate-run, not main, as the page says.

## Files

- Intermediates, all under `<scratch>/mb-cc/01/`:
  - `mine.pkl`: my independent table.
  - `recompute.txt`
  - `report.txt`: text extracted from the replicate report.
  - `work/replays/…as-run.json`: my GPU re-run.
- Artifact: `<worktrees>/chorus-collapse/docs/learned/chorus_collapse/index.html`
- Builder: `<worktrees>/chorus-collapse/tools/diagnose_chorus_collapse.py`
- Code: `<worktrees>/weekend-runs/src/bugarach/learn/nets/chorus.py`
- Raw runs: `<darkroom>/bugarach/2026-09-18-fair-comparison-run/results/` and `<darkroom>/bugarach/2026-09-18-replicate-run-status/results/`.
