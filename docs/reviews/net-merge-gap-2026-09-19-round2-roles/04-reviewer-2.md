GRANT 4 ok — Read, Grep, Glob, Bash

**Role 4, adversarial reviewer ("Reviewer 2"), round 2, BLIND.** Surface examined: the built page `...\fair_comparison_2026_09_18\net_merge_gap.html` (all 8 sections, Table 1, all four figure SVGs read as markup), the four rendered PNGs plus the two full-page shots in `...\scratchpad\v2shots\`, `net_merge_gap.json`, `replicate_net_merge_gap.json`, `crowded_check.json`, `meta.json`, the parent `report.html`, `docs/learned/tuned_vs_coact/replicate1/report.html` §9, `tools/tune_net_merge_gap.py`, `tools/build_net_merge_gap_page.py`, `docs/goals/learned-model-family.md`, `src/bugarach/bench.py`, `current_export.toml`. I did **not** open `docs/reviews/net_merge_gap_2026-09-19-roles/` or any prior review.

---

## BLOCKING

**B1 · §2 lede + §2 body ("the gain and the cost are the same size") · The crowded-recording cost is charged to the nets against *their own* baseline, while the head-to-head on that same corpus — which is in a file in the same folder and points the other way — is never computed.**
The page's central offset is: nets gain ~0.012 F1 on the bench, lose "a median 0.012 F1" on the crowded recordings, therefore a wash. But `outer_crowded_f1` is the tuned net against the *as-run net*, not against CoactDetect. `crowded_check.json` declares the identical corpus (`bench.make_tail_recording`, seeds 1–12, both backgrounds — byte-identical declaration to `net_merge_gap.json`'s `crowded_recordings`) and carries CoactDetect's per-fold crowded F1. Differencing them on this run's draw:

| selection | net | net − CoactDetect, crowded mean F1 |
|---|---|---|
| F1 alone | chorus_norm | **+0.056** (4/4 folds ahead) |
| F1 alone | chorus_gain_norm | +0.016 |
| under budget | chorus_norm | **+0.021** (4/4) |
| under budget | chorus_gain_norm | **+0.028** (4/4) |
| under budget | line_length | +0.001 |
| under budget | tube | −0.142 |

On the corpus the page itself calls "the only thing that charges for fusing two real events," the tuned chorus nets beat CoactDetect by 2–6 noise units — larger than CoactDetect's 0.015–0.018 bench lead under the budget. A reader finishes this page concluding "the nets' gap gain is cancelled by a crowded-recording cost, and CoactDetect wins"; the page's own sources do not support the second half and arguably invert it for the chorus nets.
*Fix:* add the head-to-head (net minus CoactDetect, crowded mean F1, per fold, all four nets, both draws) as a figure or table column, and either withdraw "the gain and the cost are the same size" or restate it as a within-net statement that says explicitly it is **not** a comparison against CoactDetect. Note also that the pooled median 0.012 hides a 0.20 F1 spread across nets (tube −0.14, chorus_norm +0.06) — the cost must be broken down by net, not pooled.
*Verified against a source:* **yes** (computed from `crowded_check.json` `choices[detector=coact].crowded_mean_f1` and `net_merge_gap.json` `…config_kept.outer_crowded_f1`; both corpora declared identical). Caveat for the adjudicator: I did not re-run the scorer, and the net value is a mean over five refits against CoactDetect's single value — confirm comparability before quoting my numbers.

**B2 · §7 Limits, bullet 2 · "Against no merging at all it does gain on the crowded recordings, which is the comparison worth making and is not the one the run recorded." The page asserts the outcome of a measurement it says in the same sentence was never made.**
There is no zero-gap CoactDetect entry anywhere in `crowded_check.json` (`any merge_gap_sec == 0.0` → False; coact's only crowded numbers are at 8 s against a reference that also carries 8 s), none in `net_merge_gap.json`'s `coact` block, and the sentence is hardcoded prose in `build_net_merge_gap_page.py` (line ~751), not computed. "It does gain" is an unsupported claim sitting inside the very bullet that admits CoactDetect "passed a test it could not fail."
*Fix:* delete "it does gain," or run it and report the number. If it is not run, the bullet should read "…and no one has measured it."
*Verified:* **yes.**

**B3 · Lede · "Tuning each net's merge gap on its training folds gains 0.008 to 0.014 F1 against CoactDetect" is false for two of the four nets.**
The range is computed over the chorus nets only (`lede()`'s `gained` dict; the guard `claim(...)` is worded "helps every **chorus** net"). Actual tuned-minus-as-run, all four nets, both draws, both selections: chorus_norm 0.0089–0.0142, chorus_gain_norm 0.0080–0.0136, line_length **0.0072**–0.0140, tube **0.0026–0.0049**. The goals page says "the chorus nets'"; the page says "each net."
*Fix:* say "each chorus net," and give tube's 0.003–0.005 somewhere in the body — a net whose gain is a fifth of the headline is information about the mechanism, not an omission.
*Verified:* **yes.**

**B4 · §4, last sentence of para 1 · "the nets that end ahead were already ahead before the gap moved" is contradicted by the numbers two sentences earlier in the same paragraph.**
`chorus_norm` in this run's draw goes −0.007 → **+0.004**: it ends ahead and was behind. On the stricter reading (° = inside the noise band, therefore not "ahead"), the two that end genuinely ahead — replicate chorus_norm +0.015 and chorus_gain_norm +0.013 — were at +0.005° and +0.003°, i.e. inside the band, also not "ahead." The sentence is false under both readings. It is hardcoded in `alone_text()` (line ~549) while the numbers beside it are computed, so no guard catches it.
*Fix:* replace with the computed statement — e.g. "in three of the four cases the net was already at or above zero; in this run's draw `chorus_norm` crosses zero, from −0.007 to +0.004, a move the size of the noise scale" — and put it behind a `claim()` like the other assertions in that module.
*Verified:* **yes.**

---

## MAJOR

**M1 · Table 1 · The ⚠ (chosen gap fails the crowded check on the outer refits) is applied to the "gap tuned" column only, and omitted from the set-aside and re-chosen columns that use the same chosen gap.**
`results_table()` passes `flag=` to one `stat_cell` call only. So `chorus_gain_norm` F1-alone this draw reads "−0.037 ⚠" but "−0.007°" with no flag, and replicate budget `chorus_gain_norm` reads "−0.015 ⚠" then "−0.015" clean. The flag disappears from precisely the columns where the nets look best, and the table note gives a reader no way to know.
*Fix:* pass the flag to every column derived from that chosen gap.
*Verified:* **yes** (builder source and rendered table cells).

**M2 · §3, §4, Figures 3 and 4 · The set-aside is one-sided by construction and reverses a ruling the parent report already made.**
CoactDetect has one deterministic value per fold (`coact/f1` is a 4-element list, no seeds); only the nets have refits. So "set aside on both sides" means the net's own as-run baseline, never CoactDetect — the adjustment can only ever remove net failures and can only ever move the margin in the nets' favour. Every set-aside column in Table 1 is ≥ its paired counted-every-refit column, in all 16 rows. Worse, replicate-1's report §9 already ruled on this: "with their failed folds counted — **a user of these models gets the failures too** — the mean at 8 s is below CoactDetect." The addendum re-opens that as a neutral "two choices a reader must see separately."
*Fix:* state plainly that the set-aside has no counterpart on the coded side and therefore cannot be neutral; carry forward the parent's position as the default and present the set-aside as the sensitivity, not as a co-equal accounting.
*Verified:* **yes.**

**M3 · §4 · Two of the six refits set aside are *not* training failures, and the page says so and lumps them anyway.**
"6 made no calls at all at the threshold their selection chose, **which the report counts as a different failure**. The set-aside covers both." A refit that makes no calls at the threshold the selection picked is a failure *of the procedure under test*, not of training; setting it aside deletes a cost of the method being evaluated. `low_kinds()`'s own docstring says "they are not the same failure and the page must not merge them" — and the reported column merges them.
*Fix:* report the set-aside split by failure kind, or restrict it to `failed_training_signature` and show the other separately.
*Verified:* **yes** (`build_net_merge_gap_page.py` `low_kinds` docstring + per-seed `failed_training_signature` flags).

**M4 · §4 counts · "8 … and 6 …" are row counts, not refit counts, and inflate the scope of the set-aside by 2×.**
Scanning per-seed entries under 0.2 F1 across both variants gives exactly 14 entries — but they are 7 distinct (net, selection, fold, seed) rows, each counted once under `as_run` and once under `config_kept`; and several of those 7 are the *same trained refit* appearing under both selections (replicate `chorus_norm` fold 3 seeds 1 and 2 appear as 0.125 ungated and 0.000 gated). The number of distinct collapsed models is about **5**.
*Fix:* say how many distinct refits, out of how many (of 320 refit-rows / of 160 trained refits), and stop double-counting the variants.
*Verified:* **yes.**

**M5 · §4 and §3 · The page's most net-favourable results rest on two refits in one fold out of twenty, and the budget case is not flagged the way the F1-alone case is.**
§4 discloses the carriers for F1 alone (replicate `chorus_norm`, fold 2, +0.253 F1). The same two collapsed refits drive the budget row from −0.092 to −0.018 — a 0.074 F1 move, seven noise units, from removing 2 of 20 refits — and §3 reports only the consequence ("sits inside the noise band") without the carrier. Figure 3 panel B shows it: the "as run" chorus_norm row has three dots on-axis and a gutter reading "◀ −0.305, mean −0.092."
*Fix:* give the budget case the same carrier sentence, with the same explicitness, and say what fraction of refits the whole reversal rests on.
*Verified:* **yes.**

**M6 · §2 body and Figure 1 caption · "a wider merge there only deletes duplicate calls" and "held-out F1 keeps climbing to the top of the grid" are both refuted by the page's own data, and by the plotted curve.**
Across all 64 fold-rows the *argmax* is at 30 s (so the boundary claim survives), but held-out F1 is **non-monotone in 18 of 64** — and the dip is visible in Figure 1 itself: panel A's orange `chorus_gain_norm` mean runs 0.7026 (2 s) → 0.6992 (3 s) → 0.6978 (5 s) before rising. `line_length` this draw fold 3 runs 0.6945 (2 s) → 0.7329 (3 s) → 0.6970 (5 s): a 0.038 F1 swing, ~4 noise units, on a bench where a wider merge is supposed to be free. If merging could only delete duplicate calls, F1 would be monotone non-decreasing. It is not, so something else is happening (most likely the merged call's timestamp crossing the 2.5 s match tolerance — half-acknowledged three sections later in Limits, and flatly contradicted in the body). This matters because "the bench cannot see the harm" is the entire justification for needing the crowded check at all.
*Fix:* replace "keeps climbing" / "rises to" with "is largest at the widest gap in all 64 fold-rows, though not monotonically — it dips in 18 of them"; withdraw "can only delete duplicate calls" or show the mechanism. Figure 1's caption carries the same sentence and needs the same fix.
*Verified:* **yes** (per-fold `heldout_f1_by_gap`, 64 rows; and the figure image).

**M7 · Throughout, and §7 bullet 6 · The ±0.010 F1 "between-draw scale" is used as an uncertainty band; its own source says it is an understatement and reports a maximum of 0.027.**
Replicate-1 §9: "the nets moved a median of 0.010 F1 in absolute value (**at most 0.027**) and the coded detectors 0.003 (at most 0.011) … It was measured with the 24 configurations and the training seeds held fixed … and **probably understates how far a full rerun can move a result**." The page reports neither the 0.027, nor the source's own understatement caveat, nor that the coded side's scale is 0.003 — while using a symmetric ±0.010 shaded band in Figures 3 and 4 and a ° mark in Table 1 keyed to it. A median absolute move is a central tendency, not a standard error, and the quantity being banded is a *difference* whose noise should combine both sides. The page's own limits then concede refit-to-refit SE alone exceeds 0.010 in more than half the chorus-net folds — i.e. the band is known to be too narrow and is used anyway.
*Fix:* define the scale on-page (what it is a median of, over what), give the maximum (0.027) and the coded-side figure (0.003), and either widen the band or relabel it "median between-draw move, not a confidence interval."
*Verified:* **yes.**

**M8 · §5, move-rule bullet · "moves only for a gain of at least 0.002 inner F1 — a fifth of the noise scale, so it binds rarely" is offered as reassurance and is the opposite.**
A threshold a fifth of the noise means the search moves on noise. 59 of 64 choices moved; **31 of those 59 moves had an inner gain below one noise unit (0.010), and 9 below 0.005**; median inner gain 0.0097. The page never reports this distribution. The same rule also makes the nets' search an incumbent-anchored hill-climb from 2 s, whereas the tool's own docstring records that the coded searches ran the grid and "chose the top of goal 1's grid in every fold" — so "tuned by the same rules" is not exact.
*Fix:* report the inner-gain distribution; stop presenting "binds rarely" as a safeguard; state the anchored-vs-grid asymmetry in §5 or Limits.
*Verified:* **yes.**

**M9 · §2 and §7 · The 0.02 crowded allowance is decided at margins far below its own measurement noise, and the "2 of 64 fail" count is spuriously precise.**
The page says the crowded cost "moves by a median 0.002 F1 and as much as 0.045 … against a limit of 0.02." Against that: six of 64 choices sit within 0.0012 of the limit (0.01997, 0.01994, 0.01885, 0.01884, 0.01872, 0.01884), and the single most consequential refusal on the page — replicate `chorus_gain_norm` fold 4, the only F1-alone chorus fold that stayed at 2 s — was refused at a drop of **0.020881**, i.e. by 0.00088 F1. So one of the gaps in Table 1 was set by 4% of one noise unit on a quantity with 0.045 F1 of instability. "2 of 64 lose more than the 0.02" is reported as a count when the same measurement re-run could plausibly give 2 to 8.
*Fix:* report the count with its sensitivity (how many are within ±0.005 of the limit), and name the 0.00088 refusal as the concrete instance — it is the strongest evidence on the page that the allowance is unsigned for a reason.
*Verified:* **yes.**

**M10 · §2, §7 and Table 1 · The crowded cost decides everything on this page and is the one quantity never plotted — and the reported summary hides that 8 of 64 costs are negative.**
Costs run −0.020 to +0.063, median +0.012, with **8 of 64 negative** (the tuned gap is *better* on the crowded recordings). The page gives a median, a max, and a per-row worst; there is no distribution. Per the "distribution, not the bare maximum" rule, and given this is the quantity the allowance is enforced against, it needs a figure.
*Fix:* add a panel of the 64 crowded costs, by net, with the 0.02 limit drawn.
*Verified:* **yes.**

**M11 · §5, last paragraph · The bit-for-bit reproduction check has almost no power over anything the page's conclusion depends on.**
It verifies the re-decode **at 2 s only** — the one gap that was already run — using the same code, same decoder, same GPU, same machine. Every number that supports the conclusion is at 3–30 s and is unverified by it. The page presents the same-GPU bit-for-bit match as *stronger* than the parent's CPU re-scoring, which matched only to 0.0015 F1; in fact the CPU comparison was the more independent of the two, and the same-machine match is close to guaranteed. A decoder error at wider gaps would sail through.
*Fix:* say what the check does and does not cover ("at 2 s only; the gaps the result rests on are not independently checked"), and if a cheap independent check at one wider gap exists (a CPU re-decode at 8 s, a hand-derived vector), run it.
*Verified:* **yes** (`reproduction` block records only `own_threshold_at_2s`, `rows_at_2s`, `empty_recordings_at_2s`; 1938 + 1943 = 3,881 fits, which matches the page).

**M12 · §3, "Two things the comparison does not hold level" · The two asymmetries are stated without saying which way either cuts, and the as-run baseline for the budget violation is withheld.**
"44 of the 160 nets' budget-chosen refits are over budget on the fold they were scored on" — the as-run figure is 41 of 160, so tuning slightly *increased* violations, and the page does not say so. Nor does it say the direction: I find over-budget refits average 0.680 F1 against 0.689 for within-budget ones, so being over budget is not obviously buying the nets F1 — which means the reader cannot tell whether "CoactDetect wins under the budget" is conservative or flattered. Separately, "under the shared false-alarm budget" is a misnomer: the budget is enforced at *selection* on the inner fits, and 27% of the scored refits exceed it at held-out time, while CoactDetect's budget never bound at all (its gated F1 equals its ungated F1 in all 8 folds — confirmed identical to 16 decimal places).
*Fix:* give the as-run 41, state the direction of each asymmetry, and qualify "under the shared budget" as "selected under the budget, not scored under it."
*Verified:* **yes.**

**M13 · Table 1, "gap and configuration re-chosen" column · The column is missing non-randomly, in the direction that matters, and the page explains the mechanism without naming the bias.**
6 of 16 rows read "no mean: N of 4 folds refitted." The missing ones are exactly the rows where re-choosing preferred a configuration the run never refitted — i.e. where the nets would have moved furthest. Where it *is* scored, it is nearly identical to "gap tuned" (5 of 10 identical to three decimals), so the column is close to vacuous where present and informative-missing where absent. Meanwhile "tuned by the same rules" is only true in the config-kept variant, while the coded detectors' searches chose configuration and gap jointly.
*Fix:* say that the missingness is informative and adverse to the fairness claim, and soften §1/lede: the gap was tuned by the same rules **at fixed configuration**; the joint search the coded side got cannot be scored without retraining.
*Verified:* **yes.**

**M14 · §7 Limits bullet 1 · "a known, uncleared contamination" is stale and overstates the open question.**
`current_export.toml` carries `[steps_and_pins_excluded]` — the producer's 2026-09-17 export with the moco floor-pinned windows removed, 83 events listed in `moco_pinned_excluded.tsv`, windows human-confirmed. The goals page records that the bench values were re-measured on that de-pinned export on 2026-09-17 by both workstations, every value inside its own bootstrap interval (commit `2120516`). The producer question was asked and answered; what is open is a repo decision (moving `MEASURED_ROLE`). "Uncleared" tells a reader the producer question is still hanging. (It also compresses away the parent report's own caveat that the re-measurement "had little power against an effect that small," and never says whether a contamination in the bench's *fitted values* could plausibly move a *difference between detectors* at all — my read is that it cannot, and saying so would be worth more than the flag.)
*Fix:* "fitted on an export whose contamination the producer has since corrected in a shipped folder; re-measuring moved every bench value inside its bootstrap interval; moving the bench to that folder is undecided."
*Verified:* **yes** (`current_export.toml`, `docs/goals/learned-model-family.md`, parent `report.html` §11).

---

## MINOR

**m1 · §2 body vs Figure 1's own in-panel note.** §2 argues "held-out F1 keeps climbing … so what the nets chose is a boundary, not an optimum," using the held-out curve to reach a conclusion about what the *inner* search wanted — while Figure 1's own grey note says "Read as a diagnostic, not a selection rule." The boundary case is actually carried by the refusal counts (64/64), not by Figure 1. *Fix:* argue it from the refusals and cite Figure 1 as corroboration only. *Verified:* yes.

**m2 · §7 "Every chosen gap is a boundary" cites Figure 1 for an all-nets, per-fold claim that Figure 1 cannot show.** Figure 1 plots two of four nets, as fold-averaged means; the claim is "in every fold of both draws" for all four. The claim happens to be true (argmax at 30 s in all 64 fold-rows) but the figure is not its evidence. Also, 5 of 64 choices never moved off 2 s — those are stopped by the move rule at the incumbent, which is a different kind of "boundary" than the check's. *Fix:* cite the JSON, not the figure, and distinguish the 5 unmoved choices. *Verified:* yes.

**m3 · §5, grid bullet.** The grid is coarser than the coded union (missing 0.5, 4, 10, 20 s) and the page says so without saying which way it cuts. Given that 15 s and 30 s were refused in nearly every choice, a 10 s value might well have passed and given the nets more — i.e. the coarseness plausibly *understates* the nets' gain. *Fix:* one clause on direction. *Verified:* partly (the missing values are real; the direction is my inference).

**m4 · §2, "at least 120 s apart."** Correct as a floor (`bench.BENCH_RECORDING.min_sep_sec = 120.0`, documented as a floor under a renewal process), but it is a magic number used to carry the load of "the bench cannot see the harm," and the reader is told the value without being told it is a floor rather than a spacing. *Fix:* "a floor of 120 s, under a renewal process." *Verified:* yes.

**m5 · Figure 4, `chorus_gain_norm` "gap tuned", panel A.** The mean bar sits at ≈ −0.037, left of all three visible dots (≈ −0.020, +0.005, +0.018); the fourth fold is in the gutter at −0.157. A reader who does not read the gutter sees a bar that cannot be the mean of what is drawn. The caption explains the gutter convention but not that the bar can fall outside every plotted point. *Fix:* one clause in the caption, or a tick on the gutter arrow. *Verified:* yes (image + SVG coordinates).

**m6 · Provenance.** "The tree had uncommitted changes when this was built" (`0.1.0+gf7a12e5.dirty`), and §8 says the nets and the tuning tool are on branch `tune-bench-comparison`, not on `main`, while `tests/test_tune_net_merge_gap.py` is described as checking "against the committed output." A reader cannot reproduce this page from any committed state. Not my primary lane, but it bears on every claim above being re-checkable. *Fix:* rebuild from a clean tree before delivery. *Verified:* yes.

---

## What a reader would still conclude that the data do not support

1. **"Even given the same tuning freedom, the nets lose."** The nets did *not* get the same freedom: their search was anchored at the incumbent and clipped by a check the coded searches never ran inside their own searches (`tune_net_merge_gap.py` docstring: "the coded side of the fair comparison did not"), and the joint gap-plus-configuration variant — the coded side's actual rule — is unscored in 6 of 16 rows, non-randomly.
2. **"The gap gain is real but cancelled by a crowded-recording cost."** The cost is measured against the wrong reference (B1); the head-to-head on that corpus favours the chorus nets.
3. **"±0.010 is the noise, so a 0.014 gain is about one noise unit."** The source of that number caps the observed move at 0.027 and calls itself an understatement (M7).
4. **"The replicate corroborates."** The two draws are disjoint in recordings (seeds 1000–1047 vs 2000–2047) but differ in training machine as well, and the replicate carries a measured +0.015 F1 systematic shift in the nets' favour — the size of the lead it is being read as confirming. §4 says this in one sentence; the lede and §3 say "in both draws" seven times.
5. **"The crowded check is a safeguard the nets passed."** It refused every choice at margins as fine as 0.0009 F1 on a quantity that moves 0.045, its allowance is unsigned, and on the coded side it was structurally incapable of refusing anything.
