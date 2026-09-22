GRANT 1 ok — Read, Grep, Glob, Bash

*(Line repeated at the top of the structured output, per the role contract. Scratch work in `<scratchpad>/mb2/role01/`; no repo file was modified.)*

---

# Claim ledger — every quantity recomputed from source

Legend: **=** match · **≠** mismatch · **?** unverifiable / not in the cited source. All recomputed with `<primary checkout>/.venv/bin/python` (and the Elephant venv where torch or the loader was needed), not eyeballed.

## Bake-off table (`line_bakeoff/bakeoff.json`) — Figure 1, the two sensors

| quoted | source field | recomputed | verdict |
|---|---|---|---|
| line F1 0.713 ± 0.078 | `learned.line.f1` | 0.71339, sd(n−1) 0.07810 | = |
| line fold range 0.64–0.81 | min/max | 0.63636 / 0.81081 | = |
| line recall 0.933 / precision 0.580 | means | 0.93333 / 0.58047 | = |
| line 1,305 parameters | `n_params` | 1305 — **independently rebuilt from `line.py`: 1305** | = |
| tube 0.686 ± 0.042, 0.65–0.74, 0.925, 0.547, 1,149 | — | 0.68645/0.04205, 0.65169–0.74359, 0.925, 0.54720, 1149 | = |
| tube_guard 0.680 ± 0.060, 0.63–0.75, 0.817, 0.583, 1,149 | — | 0.67992/0.05986, 0.62857–0.74667, 0.81667, 0.58303, 1149 | = |
| line_length 0.655 ± 0.035, 0.62–0.69, 0.750, 0.592, 1,233 | — | 0.65535/0.03548, 0.61972–0.69444, 0.750, 0.59167, 1233 (rebuilt: 1233) | = |
| CoactDetect 0.651 ± 0.044, 0.61–0.71, 0.767, 0.572 | `hand_written.coact` | 0.65069/0.04357, 0.60606–0.71053, 0.76667, 0.57209 | = |
| LoCo 0.645 ± 0.057, 0.57–0.70, 0.742, 0.575 | `hand_written.loco` | 0.64459/0.05683, 0.56667–0.69565, 0.74167, 0.57519 | = |
| tiny 0.125 ± 0.000, 0.067, 1.000, 2,393 | — | exact | = |
| trace 0.110 ± 0.018, 0.09–0.12, 0.075, 0.372, 2,065 | — | 0.10957/0.01785, 0.09302–**0.125**, 0.075, 0.37179, 2065 | = (max 0.125 shown as 0.12) |
| "72 parameters" for orientation | 1305 − 1233 | 72, and mechanistically exact: 3 extra input channels × width 8 × kernel 3 = 72 | = |
| "gain (0.058)" | 0.71339 − 0.65535 | 0.05804 | = |
| "four folds, one training seed per fold" | `train_seed: 0`; `seeds` are the 8 **generator** seeds, `seeds_per_fold: 2` = recordings/fold | confirmed in `tools/fair_bakeoff.py` (`train_seed` is the torch seed) | = |
| "best detector in the bake-off" | 14 detectors ran | line 0.713 is the max | = (but see F-2) |
| **table shows 8 rows** | 14 detectors in `bakeoff.json` | `tube_ratio` 0.503, `tube_ratio_guard` 0.471, `rate` 0.571, `cicada` 0.541, `sce` 0.451, `sync` 0.267 omitted, unflagged | ≠ (F-9) |

## Probe table (`probe/line_vs_fuzz.json`, K = 16)

| quoted | recomputed | verdict |
|---|---|---|
| line 18.50 / 1.83 / 1.99 / 1.32 | 18.5011, 1.8264, 1.9884, 1.3194 | = |
| line_length 17.56 / 1.82 / 1.75 / 1.14 | 17.5557, 1.8161, 1.7493, 1.1388 | = |
| tube 15.84 / 1.34 / 1.43 / 1.17 | 15.8402, 1.3398, 1.4327, 1.1685 | = |
| "untrained models scored 0.00 on every plant" | all four untrained models: 0.0000 at K = 4, 8, 16 (max 0.0001) | = |
| "four plants of equal ink" | line K, burst 4×(K//4) = K, fuzz K, wave K onsets | = |
| "so its own scale cancels" | subtraction cancels an **offset**, not a scale; the same file shows SSL `line` fits at 17.7 and 149.9 on identical plants | ≠ (F-4) |
| K = 4 and K = 8 wave ratios (not shown) | K = 4: line 1.0051 **vs** line_length 1.0094 — ordering reversed; K = 8: 1.0498 vs 1.0432 | ≠ (F-5) |

## Label-free threshold table (`training/results.jsonl`, arm `supervised`, n = 12 each)

Every cell matches on the **population** sd (the bake-off above uses the **sample** sd; neither is stated).

| model | ≤ 0.5 | ≤ 1 | ≤ 2 | oracle | verdict |
|---|---|---|---|---|---|
| line | 0.5727 ± 0.0899 | 0.6676 ± 0.0767 | 0.6986 ± 0.0673 | 0.6980 ± 0.0618 | = |
| line_length | 0.6008 ± 0.0734 | 0.6635 ± 0.0640 | 0.7026 ± 0.0610 | 0.6926 ± 0.0552 | = |
| tube | 0.4322 ± 0.0325 | 0.5187 ± 0.0754 | 0.6253 ± 0.0643 | 0.6648 ± 0.0549 | = |
| tube_guard | 0.4869 ± 0.1068 | 0.5420 ± 0.1055 | 0.6398 ± 0.0838 | 0.6518 ± 0.0579 | = |

## Rigid-shift-trained table (arm `ssl_real`)

| quoted row | recomputed (oracle · label-free ≤ 2, NaN F1 counted as 0) | verdict |
|---|---|---|
| line, real, *J* 20 s: 0.463 ± 0.171 · 0.305 ± 0.172 · 10 of 12 | 0.4631 ± 0.1706 · 0.3050 ± 0.1724 | = |
| line_length, real, *J* 10 s: 0.455 ± 0.181 · 0.286 ± 0.191 · 10 of 12 | 0.4549 ± 0.1806 · 0.2859 ± 0.1912 | = |
| tube, real, *J* 20 s: 0.488 ± 0.118 · 0.310 ± 0.200 · 9 of 12 | 0.4877 ± 0.1183 · 0.3100 ± 0.2002 | = |
| tube_guard, real, *J* 10 s: 0.487 ± 0.147 · 0.289 ± 0.159 · 9 of 12 | 0.4867 ± 0.1472 · 0.2887 ± 0.1594 | = |
| **which *J* each row uses** | every row is the **better of the two displacements** for that model (line 20 s > 10 s; line_length 10 > 20; tube 20 > 10; tube_guard 10 > 20). Unlabelled. | ≠ (F-3) |
| "fits that learned anything" | reproduces **only** under "final training loss < 0.6", a cut defined nowhere. At 0.5 → [10,10,8,8]; at ln 2 = 0.693 → [11,12,11,11] | ? (F-6) |
| "between 0.41 and 0.49 with an oracle threshold" | the eight `ssl_real` arms span **0.4047–0.4877**; the four shown span 0.455–0.488; pooled-by-model 0.434–0.464 | ≠ (F-10) |
| "against 0.65–0.70 supervised" | 0.6518, 0.6648, 0.6926, 0.6980 | = |
| "A quarter of the fits never left chance loss" | 47/192 = 24.5 % **at the 0.6 cut over all 192 SSL fits** (including the `ssl_sim` arm, never tabled). At chance loss proper (ln 2): 22/192 = 11.5 %, and 2/48 = 4.2 % for the four rows shown | ≠ (F-6) |
| "288 fits" | 288 rows in `results.jsonl`, but 48 are the `untrained` arm (`history: []`, no gradient step) and 48 are supervised. 4 architectures × 2 *J* × 3 seeds × 4 folds = **96**, and the `supervised`/`untrained` arms ran at *J* = 10 s only | ≠ (F-8) |
| untrained tube F1 0.507, oracle | 0.5069 | = |

## Real recordings (`real_compare/summary.json`, `events.json`)

| quoted | recomputed | verdict |
|---|---|---|
| 84 lab fast-stream baselines | 84 recordings in every detector's event map; controls meta `fast_recordings: 84, fast_skipped: []` | = |
| CoactDetect 2.70 · 7 · 1.00 | 2.7022 · 7.0 · 1.0 | = |
| LoCo 2.57 · 8 · 1.00 | 2.5704 · 8.0 · 1.0 | = |
| supervised line, label-free 4.95 · 5 · 0.88 | 4.9451 · 5.0 · 0.8764 | = |
| line vs rigid shift *J* 20 s: 5.73 · 4 · 0.63 | 5.7320 · 4.0 · 0.6272 | = |
| line vs rigid shift *J* 10 s: 5.70 · 2 · 0.48 | 5.7020 · 2.0 · 0.4841 | = |
| random times: median 1, 0.21–0.26 | medians all 1.0 ✓; shares 0.2070–**0.2705** (CoactDetect's chance is 0.27, above the stated top) | ≈ / minor ≠ (F-11) |
| **the ±2-frame participation column** | the tool's primary measure, present in the same file, never shown: SSL line *J* 20 s median **0** ROIs, share ≥ 3 ROIs **0.139**; *J* 10 s median 1, 0.216 | ≠ (F-1) |
| "catches 76–77 % … (chance 7–10 %)" | 0.7738 / 0.7576; chance 0.1010 / 0.0717 — **but these are seed 0 only** (`detector_events[det][:1]`); across the three seeds 0.7576–0.8315 | = value, ≠ basis (F-7) |
| "40–44 % of its own events … (chance 4–5 %)" | 0.4439 / 0.3990; chance 0.0547 / 0.0377 | = |
| "catch 47–72 % … place 19–30 %" | seed 0: 0.4685–0.7162 and 0.1912–0.3045; across seeds 0.4545–0.7716 | = value, ≠ basis (F-7) |
| "most frequent ROI pair … 0.29–0.33 against 0.33" | 0.2917 / 0.3333 vs 0.3333 — medians over only 28–33 of 84 recordings | = (denominator unstated) |
| "3–4 % of events sit within 5 s of a window edge" | **not computed anywhere in the pipeline.** My recomputation from `events.json` + the loaded windows: supervised line 3.9–4.0 %, SSL *J* 10 s 2.4–2.7 %, SSL *J* 20 s 4.5–4.6 % — and the uniform expectation is **0.84 %** | ≠ **and inverted** (F-1 below is separate; this is B-1) |

## Controls and the simulator (`../rigid_shift_look/controls/`, `docs/generator.md`)

| quoted | recomputed | verdict |
|---|---|---|
| shared offset "0.49–0.53 out to 40–45 s", both folders | fold-seed means span 0.4853 (lab slow, *J* 11.2 s) to 0.5279 (Cossart, *J* 20 s); max *J* 40.0 s lab fast / Cossart, 44.8 s lab slow | = |
| "removes planted coordination from about 10 s" | Cossart at *J* 10 s retains 0.01–0.11. **The lab folder has no rigid-shift destruction variant at any *J* in `controls/`**, and `destruction_table.json` stops at *J* = 5 s | ? (F-12) |
| "at that folder's measured participation" (Cossart) | `cossart_participation: 0.081`, destruction block participation 0.081 | = |
| "a graded control shows … partial removal" | `freeze_half` retains 0.41–0.49; `do_nothing` 1.00; `homogeneous_resample` 0.00 | = |
| simulator "0.31 s of jitter" | `spec.jitter_sec` = 0.310913 | = |
| "Real fast onset jitter is **0.36–1.04 s**" | `docs/generator.md` holds **0.36 s** (null 0.42 s, n = 47). **1.04 does not appear in `docs/generator.md` at all** | ? (B-2) |
| "the second number is flagged soft in `docs/generator.md`" | the source flags **0.36** — *"⚠ The least trustworthy number here"*, *"secondary, flagged-soft"* | ≠ **inverted** (B-2) |
| torch 2.14.0, branch `unsup/rigid-shift-controls` | 2.14.0 ✓; branch ✓ | = |

## Architecture claims against `line.py` (all verified by reading the forward pass)

| claim | verdict |
|---|---|
| "count how many ROIs are lit, then judge that count against its own background" | = (sigmoid vote → `mean(dim=1)` over ROIs → difference-of-Gaussians, area-normalised to zero sum) |
| "the same model with the orientation channels removed, registered as `line_length`" | = (`build_line(orientation=False)`) |
| "permutation-invariant over ROIs" | = for `line` (mean over ROIs) and `tube` (sum over ROIs) |
| "the encoder sorts rows by rate" | = (`encode`: *"Rows are sorted by firing frequency, busiest first"*) |
| "these channels measure temporal concentration" | = (`count[:, :-1] / (count[:, 1:] + eps)`, narrow smear over next-wider) |
| "worth keeping and worth replicating, not a measured superiority" | = — paired per-fold differences are +0.045, −0.009, +0.179, +0.017; mean +0.058, sd 0.081 |

---

# Findings

| # | location | issue | severity | suggested fix | verified against a source |
|---|---|---|---|---|---|
| **B-1** | "**Not artefacts**", ¶ "3–4 % of events sit within 5 s of a window edge, so it is not the window boundary" | **The negative control is inverted, and the number is not reproducible.** Nothing in `tube_ssl_real_compare.py` computes an edge statistic — `measure()` has no such field and `summary.json` has none — so the quantity has no artifact behind it. Recomputing it from `events.json` and the loaded windows gives 2.4–4.6 % for the three `line` rows (not 3–4 %), **and the uniform expectation for a 10 s edge band in a 1,200 s window is 0.84 %.** The observed shares are therefore a **2.9–5.4× enrichment at the edges**, which argues *for* an edge artefact, not against one. CoactDetect shows the same 4× enrichment; LoCo shows exactly 0.0 %, i.e. it suppresses edges — the comparator that would have made this visible is already in the table. | **blocking** | Either drop the sentence, or state the measure, add it to the tool, and report it against its chance baseline: *"edge events run 3–5× the uniform expectation, so an edge effect is not excluded."* | yes — recomputed; 0.0392 / 0.0242 / 0.0449 observed vs 0.0084 expected, n = 2,476 / 2,855 / 2,870 events |
| **B-2** | "What this does not settle", jitter bullet | **A quoted number is absent from the source it cites, and the source's caveat is attached to the wrong number.** `docs/generator.md` gives real fast onset jitter as **0.36 s** (surrogate null 0.42 s, n = 47 slices). **1.04 does not appear in `docs/generator.md`.** It appears only in a sibling todo, also unsourced. Worse, generator.md flags **0.36** — *"⚠ The least trustworthy number here … Its own source file marks it 'secondary, flagged-soft.' Treat it as an upper bound"* — while the report says *"the second number is flagged soft"*, i.e. 1.04. The report thus presents the number the source distrusts as the solid one and invents the other. | **blocking** | Quote what the source holds: *"real fast onset jitter is measured at 0.36 s against a 0.42 s circular-shift null, and `docs/generator.md` flags that 0.36 as an upper bound at the estimator's resolution."* Drop 1.04 or give it a source that contains it. | yes — `grep` of `docs/generator.md`; lines 93, 290–295, 415, 483–485 |
| **F-1** | "On real recordings" table, column *ROIs within ±1 s, median* | **The tool's primary participation measure is omitted and it reverses the table's story.** `measure()` computes participation at ±2 frames (0.2 s) *and* at ±1 s. The report shows only the ±1 s column. At ±2 frames, `line` trained against rigid shift at *J* 20 s has **median 0 ROIs** and share ≥ 3 ROIs **0.139** (vs the tabled 4 and 0.63); at *J* 10 s, median 1 and 0.216 (vs 2 and 0.48). Both numbers sit in the same `summary.json` the table is built from. A reader concludes the rigid-shift models call multi-ROI events; at the tighter window they largely do not. | major | Add the ±2-frame column beside the ±1 s one, or say in the caption that the loose window is what is shown and give the tight one in prose. | yes — `real_compare/summary.json`, keys `participation_median` / `participation_share_ge3` |
| **F-2** | "What holds", *"`line` … is now the best detector in the bake-off, and the second sensor is what put it there"* | **The headline asserts what the document's own ⚠ two paragraphs later retracts.** `line` beats `tube` by 0.027 F1; paired per-fold differences are +0.047, +0.008, +0.067, −0.015 (mean 0.027, sd 0.036, one fold negative). The ⚠ correctly says the line-vs-ablation gain is inside the fold spread — the same is true of the ranking itself, and the ranking is stated in bold without its caveat. | major | Soften to *"`line` takes the top mean F1 in the bake-off (0.713 against `tube`'s 0.686), by a margin one fold reverses"* and carry the ⚠ up to the summary. | yes — per-fold F1 from `bakeoff.json`, recomputed paired differences |
| **F-3** | Rigid-shift-trained table, *arm* column | **Every row is the better of the two displacements for its model, and the selection is not disclosed.** line takes *J* 20 s (0.463 vs 0.405 at 10 s), line_length takes 10 s (0.455 vs 0.448), tube takes 20 s (0.488 vs 0.432), tube_guard takes 10 s (0.487 vs 0.441). Four best-of-two picks reported as four results. The `ssl_sim` arm — 96 of the 192 trained fits, named in the setup sentence — never appears for `line` or `line_length` at all. | major | Show both displacements per model (eight rows), or state *"the better displacement per model is shown"* and give the other in a footnote. Say what became of the `ssl_sim` arm. | yes — all sixteen `ssl_real`/`ssl_sim` arm means recomputed from `results.jsonl` |
| **F-4** | Figure 1, the two sensors, Panel B text: *"Each model's score is its peak response with the plant minus the same field without it, so its own scale cancels"* | **Subtraction cancels an offset, not a scale.** `probe_line_vs_fuzz.py` returns raw logits and subtracts a baseline peak; a model whose logits run 10× larger yields a 10× larger difference. The same JSON proves it: SSL `line` fits score `line_16` at 17.7 and 149.9 depending on seed. The **ratio** columns are scale-free; the first column (18.50 / 17.56 / 15.84), and Panel B's bar heights, are not — and that column is where "`line` responds more than `tube`" is read. (The wording originates in the tool's own docstring, so the fix belongs in both.) | major | Say *"the ratios cancel each model's scale; the absolute column does not and should not be compared across architectures"*, and drop or normalise the absolute comparison. | yes — `tools/probe_line_vs_fuzz.py` lines 90–107; cross-model logit scales in `probe/line_vs_fuzz.json` |
| **F-5** | Figure 1 Panel B text: *"The orientation channels show up against the **wave**, 1.32 against 1.14"* | **The effect exists at one of the three K values measured, and reverses at the smallest.** At K = 4, line 1.0051 vs line_length **1.0094** (the ablation is higher); at K = 8, 1.0498 vs 1.0432. Only K = 16 gives 1.32 vs 1.14. The K = 4 and K = 8 columns are in the same file and are not shown. The difference also has no uncertainty attached while the document applies a ⚠ to a bake-off gain of the same size — the probe's own per-field sd is ±4.4 on a mean of 18.5 (n = 12 fields, one seed). | major | Show all three K values, and apply the report's own ⚠ standard: *"the separation appears only at K = 16 and is not resolved at n = 12 fields."* | yes — all three K values recomputed from `probe/line_vs_fuzz.json` |
| **F-6** | Rigid-shift-trained table, column *fits that learned anything*; and *"A quarter of the fits never left chance loss"* | **The criterion is defined nowhere and is mislabelled.** The column reproduces only under "final training loss < 0.6" — I brute-forced 36 candidate criteria and that is the unique match ([10,10,9,9]). Chance loss for this objective is softplus(0) = **ln 2 = 0.693**, not 0.6. Under the literal phrase, 2 of the 48 tabled fits (4.2 %) and 22 of all 192 SSL fits (11.5 %) never left chance — not a quarter. The "quarter" (24.5 %) holds only at the 0.6 cut *and* over all 192 fits including the `ssl_sim` arm the table does not show. The column is also very sensitive to the cut: 0.5 → [10,10,8,8], 0.65 → [11,10,11,9]. | major | Define the criterion in the table caption with its threshold, and either use ln 2 and quote 11.5 %, or keep 0.6 and call it *"final loss below 0.6, against a chance loss of 0.693"* — and name the population the quarter is drawn from. | yes — `results.jsonl` `history[-1][1]`; counts at every cut recomputed |
| **F-7** | "On real recordings", *"catches 76–77 %"*, *"catch 47–72 %"* | **The two agreement directions use different sample sizes and neither is stated.** `tube_ssl_real_compare.py` line 299 passes `detector_events[det][:1]` — so "CoactDetect → model" reads **only training seed 0**, while "model → CoactDetect" pools all three seeds. Across the three seeds supervised `line` catches 75.8–83.2 % (quoted 76–77 %) and the rigid-shift models 45.5–77.2 % (quoted 47–72 %). | major | Either report the three-seed mean and spread, or state *"catch rates are measured against the seed-0 fit"*. | yes — reimplemented `agreement()` over all three runs in `events.json` |
| **F-8** | Figure 2, learning from rigid shift alone, opening sentence: *"Four architectures, two displacements … three seeds and four folds each: **288 fits**"* | **The arithmetic the sentence offers gives 96, and 48 of the 288 rows are not fits.** `results.jsonl` holds 96 `ssl_sim` + 96 `ssl_real` + 48 `supervised` + 48 `untrained`. The `untrained` arm takes no gradient step (`history: []`, `train_seconds` ≈ 1 s), and the `supervised` and `untrained` arms ran at *J* = 10 s only, so "two displacements" covers 192 rows, not 288. | major | *"Four architectures × three seeds × four folds, at two displacements for the two label-free arms and once each for the supervised control and the untrained baseline: 192 fits plus 48 untrained baselines, 288 scored rows."* | yes — `results.jsonl` arm/J/seed/fold cross-tabulation |
| **F-9** | Figure 2 and its two tables | **The embedded figure does not contain the models the text under it discusses.** `make_tube_ssl_figure.py` hard-codes `MODELS = {"tube", "tube_guard"}`; the rendered `tube_ssl_fig.png` shows only those two. Both tables beneath it are about `line` and `line_length`. A reader looking at Figure 2 for the `line` result finds nothing. | major | Add `line` and `line_length` to `MODELS` and re-render, or retitle the figure to say it covers the tube family only. | yes — read `make_tube_ssl_figure.py` and the rendered PNG |
| **F-10** | *"Every architecture lands between 0.41 and 0.49 with an oracle threshold"* | Not reproducible under any grouping. The eight `ssl_real` arms span **0.4047–0.4877** (0.40, not 0.41, at the bottom — `line` at *J* 10 s); the four displayed rows span 0.455–0.488; pooled per model, 0.434–0.464; including `ssl_sim`, 0.338–0.488. | minor | Quote the range you mean and name its population — e.g. *"the eight real-data arms land between 0.40 and 0.49."* | yes — all sixteen arm means recomputed |
| **F-11** | Bake-off table (8 of 14 rows) and real-recordings table | **Completeness not declared.** Six detectors ran in the same bake-off and are absent without a note (`tube_ratio` 0.503, `tube_ratio_guard` 0.471, `rate` 0.571, `cicada` 0.541, `sce` 0.451, `sync` 0.267) — Panel A of Figure 1 shows all fourteen, so the table is a silent subset of its own figure. Likewise `summary.json` holds 18 detector rows and the real table shows 6. Also: "random times … 0.21–0.26" understates the top — CoactDetect's chance share is 0.2705. | minor | Add *"eight of fourteen detectors shown; the rest are in Figure 1, the bake-off"*, and correct the chance range to 0.21–0.27. | yes — `bakeoff.json`, `summary.json` |
| **F-12** | *"It removes planted coordination from about 10 s, including on the Cossart folder"* | The "about 10 s" figure is measured **only** on Cossart. The lab block in `controls/lab/results.json` carries no rigid-shift destruction variant at any displacement (only `homogeneous_resample`, `freeze_half`, `do_nothing`), and `../rigid_shift_look/destruction_table.json` stops at *J* = 5 s for the lab stream. The sentence reads as lab-plus-Cossart. | minor | *"Removal is measured out to 10 s on Cossart; on the lab folder the destruction scan stops at 5 s, where removal is already ≥ 0.96 at K ≥ 6."* | yes — both destruction artifacts enumerated |
| **F-13** | Probe table header, *"trained model"* | The probe's `supervised line` / `line_length` / `tube` are a **separate single-seed fit on all eight generator recordings** (`fold_split(...).seeds`, `seed=0`), not the bake-off's held-out fold models whose F1 appears in Panel A of the same figure. The two panels of Figure 1 are read side by side as the same models. | minor | Say *"probed models are supervised fits on the full generator corpus, seed 0 — not the bake-off's fold models."* | yes — `probe_line_vs_fuzz.py` lines 126–130 |
| **F-14** | "How to reproduce" and *"Checkpoints of one seed of each label-free fit are in `real_compare/checkpoints/`"* | **The probe cannot be reproduced from what ships.** `probe/line_vs_fuzz.json` scored **96** checkpoints (3 seeds × 4 folds × 4 models × 2 *J*); `real_compare/checkpoints/` holds **8** — seed 0, fold 0 only. The sentence says "one seed", which would be 32. Separately, the bake-off command as printed omits `--out`, which `fair_bakeoff.py` declares `required=True`, so it exits without running. | minor | *"Checkpoints of the seed-0, fold-0 fit of each (architecture, J) pair; the probe read all 96, which are not shipped."* Add `--out` to the command. | yes — checkpoint filenames vs the 96 model keys in `line_vs_fuzz.json`; `fair_bakeoff.py` line 348 |
| **F-15** | ± convention throughout | The bake-off table uses the **sample** sd (n−1) and the two training tables use the **population** sd; neither says which, and both are labelled "±". | minor | State the convention once, e.g. *"± is the sd over folds (n−1) in Figure 1 and over the 12 fits (population) in Figure 2"*, or use one. | yes — reproduced both by direct computation |

## The source the report did not consult

| # | issue | severity | verified |
|---|---|---|---|
| **F-16** | **A group-membership record exists in the file the analysis already loaded, and nothing in the report accounts for it.** `look_rigid_shift.load("fast")` returns records carrying `.group` alongside the `.mouse` field `tube_self_supervised.real_recordings()` already reads to build its folds: **ORX 25, MALE 22, OVX 20, DI 17** recordings. The controls run beside this report bootstraps by mouse and reports `by_group` accuracies; this report pools all 84 into single numbers with no per-group breakdown. Second, the 84 recordings come from **44 mice** (30 mice contribute 2 recordings, 5 contribute 3, 9 contribute 1), yet every rate, participation share, agreement share and chance level is computed over pooled **events** with no mouse-level clustering — units sharing a subject are counted as independent. The fold design is honest ("a model that never saw its mouse" is verified: `sd.mouse_folds`), but the *statistics* are not clustered. | major | yes — enumerated `.group` and per-mouse recording counts from the loader; `by_group` blocks in `controls/lab/results.json` |
| — | **Withdrawal / exclusion record: present and respected.** The analysis runs under `LOOK_ROLE=steps_excluded` and reads the export folder, which per the repo contract is the producer's own withdrawal decision; `controls/lab/meta.json` records `fast_skipped: []` and `fast_recordings: 84`, reconciling with the 84 recordings in `events.json`. No withdrawn unit appears to have been included. Reported as a pass, not a silence. | — | yes |
| — | **Retraction check.** The report itself notes the rigid-shift note "stays under its correction banner"; I found no claim in this report re-inheriting a withdrawn number from that banner. The one inherited quantity I could trace, the 0.36–1.04 s jitter range, fails for a different reason (B-2). | — | yes |

## What held up

Worth saying plainly, because it is most of the document: **every number in the bake-off table, the probe table, the supervised label-free table, the rigid-shift-trained table and the real-recordings table recomputes exactly from the artifacts beside the report.** Roughly 110 quantities, no arithmetic error found. The parameter counts survive an independent rebuild of the architecture from `line.py`. Every "X does Y" claim about the architecture — one ROI one vote, the mean over ROIs, the zero-integral difference-of-Gaussians, permutation invariance, the busiest-first sort, the orientation channel as a narrow-over-wide count ratio, the 72 parameters — is exactly what the code does. The report's own ⚠ about the untrained baselines is **correct and well-evidenced**: untrained models really do score 0.0000 on every plant at every K, and untrained `tube` really does score F1 0.5069 with an oracle threshold. The defects above are almost all in what was *selected*, what was *named*, and what was *inferred* — not in what was computed.

Files that matter: `<worktree>/docs/learned/tube_self_supervised/README.md`, `<worktree>/tools/tube_ssl_real_compare.py` (the `[:1]` on line 299 and the missing edge measure in `measure()`), `<worktree>/tools/make_tube_ssl_figure.py` (`MODELS` on line 29), `<worktree>/tools/probe_line_vs_fuzz.py` (the scale-cancellation claim in its docstring), `<worktree>/docs/generator.md`.
