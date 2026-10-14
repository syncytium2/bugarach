GRANT 3 ok — Read, Grep, Glob

Role 3, Cross-Examiner (consistency). Artifact: c:\Users\defazio\bugarach\bugarach-worktrees\coordination-share-explainer\docs\learned\coordination_share_explainer\README.md and its six PNG figures. I edited nothing.

**What I checked.** I compared every number in the README against numbers.json. I opened all six figures and checked each against its caption and the prose. I cross-checked the tool's code and docstrings (`tools/measure_coordination_rates.py`: `shifted`, `solve`, `pooled_ratio`, `per_recording`, `truth`, `_sim`, `CAL_NO_PROBE`, `CAL_TOL`, `N_SURR`, `CAL_JITTER`). I also checked `src/bugarach/bench.py` (`REGIMES`, `BENCH_RECORDING`, `ELEVATED_RATE_RECORDING`, `realistic_counts`, spacing), `simulate.py` (the elevated stretch is added on top of each cell's rate), `fit_background_shape` floors, the real-intervals `summary.json`, `current_export.toml`, the 2026-10-05 contamination todo, ADR-0017, the explainer todo, `docs/GLOSSARY.md` and `docs/INDEX.md`.

**What reconciles cleanly:** every percentage and range in Figures 2 to 6 (rounding is correct throughout); the 90 and 720 ordered pairs and triples; 1.21 ÷ 0.20 + 2 ≈ 8.1; 20 shifted copies; the ±32 s slides; 28× quiet (0.0049 + 0.1334); 6 decoys of 6 cells; about 7 moments per 45 min (9.7 per hour); median gap 41 s; 66 recordings; four affected recordings, all DI, three not yet reviewed; the `shape_usable` floors 300 s / 20 onsets / 5 cells; ±25%; 43%; seed 13 / minutes 30–35 / quiet; seed 3 / busy; the planted shares under Figure 6 (20, 8, 5, 50, 7%); the 4 and 6 bars at 30m25s in Figure 1C; and the "bracket" claim checked against Figures 3A and 3C.

## Findings
Format: location · issue · severity · suggested fix · verified against a source (yes/no)

1. **README lines 48–50 against lines 72–73 and 260–262 (counting basis of "real input").** The page says "One input comes from real recordings: the bench's intervals between moments (Figure 3C)" and puts only that input under the contamination stop. But the Terms section itself says quiet and busy (0.0049 / 0.0169) are percentiles of real baseline recordings. The jitter (0.106 s) is called "measured", and the elevated-stretch level (0.1334, a measured 99th percentile) is real too. So are the 32 cells and the background rate and burst shapes (`BENCH_RECORDING`, `MEASURED_RATE_SHAPE`). `REGIMES`, cells and participation were re-measured on 2026-09-23 on the 66-recording default folder, which is now under the stop. Every figure, not just 3C, rests on real-derived constants. · **major** · Say "Several bench constants come from real recordings (background rates, cell count, jitter, stretch level, intervals)". State which were measured on the folder now under the stop, or narrow the claim another way that matches Terms. · yes (bench.py lines 890–900, 1023–1066, 1561–1574; RUN.md of the 2026-09-25 real-intervals run)

2. **README lines 62–63 against lines 116–117 and 325–326 (units of λ).** Terms defines "λ, moments per minute". Step 3 then says "Each cell's coordinated onsets per second are λk/N", and For developers says "at rate λ per second". That formula is only right if λ is per second. The glossary entry added in this same change also says "moments per second (λ)". Figure 4C labels its axis "moments per minute (λ)". · moderate · Pick one unit for the symbol λ: per second in formulas, with "moments per minute" as the reported quantity. Or write λ/60 in the formula. Make the GLOSSARY "fixed model / binomial model" entry match. · yes

3. **README lines 120–122 and 246–248 against Figure 6 / numbers.json (pooling and spread).** The page says "Pooling did not narrow the spread here … about as widely … and more widely with 6 moments", and that pooling "steadies the median … not a single recording's answer". In Figure 6 the pooled 10th–90th range is narrower than each recording's own in two of five groups. With 3 moments it is 0.69–1.02 pooled against 0.61–1.04 own. At busy it is 0.76–0.92 pooled against 0.74–0.95 own. Nothing in Figure 6 shows the median steadied either: the pooled medians are lower in 3 of 5 groups. The tool's own `per_recording` docstring gives the opposite purpose: "one recording's f3 is noisy". · moderate · Restate as "mixed: wider with 6 moments, narrower with 3 and at busy, about the same otherwise". Drop the "steadies the median" claim, or show it. · yes

4. **README lines 239–242 ("Fewer shared moments, much more spread"), measured on the basis the bullet uses ("as the tool reports it").** The spread is not monotone. The 6-moment range is 0.59–0.98 (width 0.39) and the 3-moment range is 0.69–1.02 (width 0.33). The bullet then switches to single-recording extremes for the 3-moment group (0.55–1.09). That mixes two counting bases (10th–90th percentile against min–max) in one comparison. · minor · Quote one basis for all three groups, or say outright that 3 moments is not wider than 6 on the 10th–90th percentile. · yes

5. **README lines 161–162.** "From size variation alone it reads 5% low (one size) to 18% low (three sizes)". The one-size set (Figure 3B) has no size variation, so its 5% has to come from the second reason the paragraph gives (window edges). The two reasons are attributed against each other. · minor · Say "with one size (window edges only) 5% low; with three sizes 18% low". · yes

6. **README lines 320–322, against the tool's module docstring, lines 60–62.** The README says "the module docstring's account agrees with the figure". The docstring says two things. Lines 27–31 say slower modulation survives into the surrogate, which agrees with Figure 5A. Lines 60–62 say "a joint rise in rate reads as coordination … and the surrogates cannot subtract it", which is `CAL_NO_PROBE`'s claim that the README says Figure 5A contradicts. · minor · Say "the docstring's surrogate paragraph agrees with the figure; its calibration paragraph repeats CAL_NO_PROBE". · yes

7. **README line 261 ("0.106 s (the correlogram's measured fast-stream jitter …)") against GLOSSARY "jitter" and `bench.BENCH_RECORDING`.** The glossary gives 0.105 s for fast, and the bench was re-measured to 0.105 s on 2026-09-23. 0.106 is the older 84-recording value, fixed in `CAL_JITTER` on purpose. · minor · Say "0.106 s, the value the tool's check fixes (the current measurement is 0.105 s)". · yes

8. **README lines 136–137.** The 43% failure quoted from `CAL_NO_PROBE` was measured with a 0.127 Hz stretch, at the old 120 s spacing. Elsewhere the page calls the bench's elevated-rate level 0.1334. A reader will assume the 43% belongs to the 0.1334 stretch. · minor · Add "(at the stretch's earlier level, 0.127 per second)". · yes

9. **README lines 126–129 (the default set-up) against Figures 3B, 3C, 5 and 6.** The page says every recording runs "at the quiet or the busy background, with 15 shared moments … 5 each of 10, 6 and 3 cells". Figure 5C uses 13× quiet, and Figure 6 uses ¼ quiet with 6 or 3 moments. Figure 3B uses one size, and Figure 3C has about 7 moments plus decoys. The next sentence also says "Figure 6 varies how many moments there are", but Figure 6 varies the background too. · minor · Mark it as the default ("unless a figure says otherwise"), and say "Figure 6 varies the number of moments and the background". · yes

10. **README line 219, "At a busy enough background (13 times quiet)" (reserved word).** The glossary reserves quiet and busy for the two bench backgrounds: "so that 'the quiet background' always means this". Busy is 3.4× quiet, and this page uses "busy" for 13×. · minor · Say "At a high enough background (13 times quiet)". · yes

11. **Figure 1 legend order against Figure 4 legend order (the same gap-type grouping).** Figure 1 lists close, medium, single. Figure 4 lists 120 s only (single), medium, close (very close). The colours agree (blue close, orange medium, green single/120 s), but the order is reversed between the two figures. · minor · Use one order in both (e.g. single / 120 s, medium, close, very close) in the figure code. · yes (images)

12. **README lines 174–175 against lines 243–244 and 266 (two numbers for the same quantity).** The page gives a median interval of 41 s and also "about 7 moments per 45 minutes", one every ~6 min. A reader dividing 2700 s by 41 s expects about 66. The glossary ("intervals") warns these two are not interchangeable and asks that the source of each be said. · minor · Add one clause, e.g. "real moments come in clusters: the median gap within a cluster is 41 s, but the rate over a whole baseline is 9.7 per hour". · yes (summary.json p50 41.25 s, 9.72 events per hour)

13. **README line 211, "The worst single recordings read up to 14%", and line 187 (binomial 3%–17% low): numbers in the prose that no figure shows.** Figure 5A draws the median and the 10th–90th band (top 11.8%), not the maximum. Figure 4 draws the fixed model only. Under the "a count named in prose is visible in the figure" rule, both numbers have no figure behind them. · minor · Either mark them "(not drawn)" or point to numbers.json. · yes

14. **README line 329: a dead cross-reference.** It links to `../../reviews/coordination_share_explainer_2026-10-14.md`, which does not exist in the worktree. Only the `…-roles/` folder exists. · minor (fine if the record is written before merge) · Make sure the run record lands at that exact path. · yes (Glob)

## Companion documents (fixes outside the artifact, found while checking terms)

15. **GLOSSARY "background" entry (line 422–424) against the "regime" entry (line 355–358) and the README.** "background" still says quiet 0.0052 / busy 0.019. "regime", `bench.REGIMES` and the README say 0.0049 / 0.0169. · minor · Update the glossary background entry. · yes

16. **ADR-0017 (Context) and the explainer todo, item 2, against the GLOSSARY "shifted copy" entry.** ADR-0017 and the todo both say each cell's train is "shifted rigidly". The glossary says a shifted copy is "Not a rigid shift". The README rightly avoids "rigid". The ADR is immutable, so this is a note, not a fix. · minor · None to the ADR; the todo could say "shifted copy". · yes

17. **Explainer todo header ("99% of a threefold rise") against README line 220 ("removes 98% of what it added").** numbers.json `rise_removed` is 0.981; 0.990 is the row total, clumping included. · minor · Change the todo to 98%. · yes

## Line 222 — not counted as a finding
README line 222, "removed almost entirely at 13 times quiet (99%)", is the "constant, 13× quiet" row's `removed` (0.994), not the rise row. It is consistent, so it is not counted above.

Key paths:
- c:\Users\defazio\bugarach\bugarach-worktrees\coordination-share-explainer\docs\learned\coordination_share_explainer\README.md
- c:\Users\defazio\bugarach\bugarach-worktrees\coordination-share-explainer\docs\learned\coordination_share_explainer\numbers.json
- c:\Users\defazio\bugarach\bugarach-worktrees\coordination-share-explainer\tools\measure_coordination_rates.py
- c:\Users\defazio\bugarach\bugarach-worktrees\coordination-share-explainer\src\bugarach\bench.py
- c:\Users\defazio\bugarach\bugarach-worktrees\coordination-share-explainer\docs\GLOSSARY.md
