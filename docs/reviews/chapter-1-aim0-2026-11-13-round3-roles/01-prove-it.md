GRANT 1 MISMATCH — missing none; holds Edit, Write, NotebookEdit (deferred), plus PowerShell, Agent, Artifact, Skill, ToolSearch and Claude_Docs MCP write tools

**Run finding:** the fallback path gave this reviewer editing tools that no reviewer may have. None was used. The only files written were scratch scripts under <scratch>/mb3/role01/. The run record's `roles:` line should therefore say "fallback path", not "named agents".

## Role 1, Prove It: Chapter 1 (blob faa8e320, verified by `git hash-object`)

**Method.** I recomputed claims from the log, the scripts, the record files and the PDFs rather than reading them by eye:
- I read `ch1_intro_figures.py` and its `.log`.
- I recomputed the chance floors, ν_c, q, g₂ and its half point, HWHM, d, the b at which K=4 crosses the budget, k̂/k and Figure 1.5C's F by hand or in Python.
- I re-derived the per-segment statistics from `runs/2026-09-25-real-intervals/windows.csv`, and the chance-arm Poisson intervals and the 1 s / 4 s participant ranges from `aim1_one_source.json`.
- I checked these follow-up outputs line by line: window_counts, realistic_counts (and its JSON standard errors), lab_values, correlogram_table, assessor_jitter, assessor_null, chance_bursty, like_for_like, dependence_null, pooled_path, membership_repeat, order_power.
- I diffed the decimal values against the pre-revision text (fd1ace2d). No decimal was dropped or changed, so "No number from the earlier version changed" holds.
- I read Finn & Johnson 1968, Rohling 1983, Perkel 1967, Thomas 1949 and Neyman & Scott 1952 for the new attributions.

### Findings (location · issue · severity · fix · verified against source?)

1. **§1.2.3, "Finn (1967) set it instead from an estimate of the background made in the reference cells…"; reference list entry "Finn HM (1967)" with no ⚠.**
   - **Issue:** Finn 1967 is not in <01-lit>. `radar/README.md` says only the journal's contents page was checked, never the paper. The chapter header promises that every unmarked source "was read against the claim it supports".
   - The only primary in hand, Finn & Johnson 1968 (p. 415, footnotes 1–3), credits the clutter-proportional threshold to three Finn papers: RCA Review 1967, Allerton 1967 and **Proc. Nat. Electronics Conf. 1966**. So the priority implied by "Finn (1967)" is not secure either.
   - **Severity:** medium (an attribution to an unopened source).
   - **Fix:** mark it ⚠, and attribute the approach as "Finn (1966; 1967 ⚠), as cited by Finn & Johnson 1968". Or attribute it to Finn & Johnson 1968 alone, whose Fig. 2 and p. 417 do describe it (cells surrounding the test cell, cell under test excluded, a step on from thermal-noise regulation).
   - **Verified:** yes (F&J PDF and the radar README).

2. **§1.3.1, first bullet, 0.0096 Hz "estimated from the fast stream … (the simulator's generator notes)".**
   - **Issue:** `docs/generator.md` (around lines 405–414) gives 0.0096 Hz as a **per-ROI rate over 84 slices** from the constellation summary (fast stream, `min_rois=4`). That is the earlier recording set, not the 66 baseline segments.
   - It also appears to be the rate of all onsets, not of background onsets only.
   - The next paragraph ("These values pool the four experimental groups … the 66 segments") implies every realistic value comes from the 66 segments.
   - The citation is accurate, but the provenance is mixed and unstated. Whether the 84-slice set included recordings the lab later withdrew cannot be checked from the repository.
   - **Severity:** low–medium.
   - **Fix:** say "measured on the lab's earlier 84-recording set (all fast-stream onsets per cell)", or re-measure on the 66.
   - **Verified:** yes (generator.md).

3. **§1.3.1, "several segments come from the same mouse, so the 66 segments are not independent".**
   - **Issue:** I could not verify this from any source in the repository.
   - `windows.csv` carries `group` (DI 17, OVX 17, MALE 13, ORX 19) and `slice_id`, with 66 distinct slices. Recording dates repeat up to 3 times, which is suggestive only.
   - The export contract's `subject_id` column (`export_folder_spec.md`, line 663) was not consulted.
   - The chapter makes no inference from these units, so the claim is harmless. But no source of record for subject membership was opened.
   - **Severity:** low.
   - **Fix:** cite the subject record, or soften to "may share a mouse".
   - **Verified:** no.

4. **§1.2.3, "both are integers, so this is agreement at two points, not a test of the formula's shape".**
   - **Issue:** this understates the record. `blind_a/REPORT.md` §4 compares the analytic and Monte Carlo floors at six backgrounds: they agree at five, and at 0.1 Hz the analytic floor is 17 against Monte Carlo 16. That supports the chapter's own "errs toward a higher floor".
   - **Severity:** low (the claim is conservative).
   - **Fix:** cite the six-point comparison.
   - **Verified:** yes.

5. **§1.2.4, situation 5, "its threshold there is 6 cells in 119 draws and 7 or more in 67".**
   - **Issue:** this accounts for 186 of 200 draws. The log has 4 cells in 1 draw and 5 cells in 13. A lower threshold in those 14 draws bears directly on CFAR's 49 %.
   - **Severity:** low.
   - **Fix:** add "and 4–5 in 14".
   - **Verified:** yes (log).

6. **§1.6.2, "0.01 Hz with K = 3 (chance share about 0.3, 0.2–0.4 by condition)".**
   - **Issue:** per condition, the predicted share is 0.20 or 0.43 and the measured share runs 0.15–0.48 (`assessor_jitter.txt`). The pooled values are 0.32 predicted and 0.26–0.29 measured.
   - **Severity:** low.
   - **Fix:** "0.2–0.45".
   - **Verified:** yes.

7. **§1.5.7, "Assuming a Poisson train … reads jitter at 0.55–0.62".**
   - **Issue:** this matches the `poisson` rows. The `poisson_fixed` rows give 0.58 and 0.63.
   - **Severity:** low.
   - **Fix:** none needed if "Poisson" means the variant without a fixed count; otherwise "0.55–0.63".
   - **Verified:** yes.

8. **§1.5.7, "at best 12–13 of 40 in the band, at 16 slow events".**
   - **Issue:** true for the fit given the true train. With the hard-core assumption, slow-stream 7 cells at E=16 reaches 14.
   - **Severity:** low/informational.
   - **Verified:** yes.

9. **§1.3.4, "Counting every active cell (background included) in the 1 s bins within 1.5 s of each event…".**
   - **Issue:** the code (`events_reaching`) takes the **maximum over single 1 s bins** that overlap ±1.5 s. The log says "in some 1 s bin". The prose can be read as a count pooled across those bins.
   - **Severity:** low (ambiguity).
   - **Fix:** "in at least one 1 s bin within 1.5 s of the event".
   - **Verified:** yes.

10. **§1.4 Prior work, "Cossart, Aronov & Yuste 2003, with a threshold from reshuffled surrogates".**
    - **Issue:** the PDF in <01-lit> is a scan whose text does not extract, so this is unchecked.
    - **Severity:** low.
    - **Verified:** no.

11. **"About this chapter", "checked … in four rounds and this chapter in three".**
    - **Issue:** not verifiable, because the brief forbids reading `docs/reviews/`.
    - **Verified:** no.

### Claim ledger: verified matches (recomputed)

**§1.1 and Figure 1.1:**
- 190 background and 40 event onsets.
- 33 cells, 0.05 Hz (5.2 × 0.0096), 4 events × 10 cells, σ 0.2 s.

**§1.2.3 and §1.6.1 (chance floor and chance clusters):**
- 2 s floor: 6 cells at 0.0096 Hz, 6 at 0.01 Hz, 12 at 0.05 Hz.
- 0.2 s window floor: 4 cells.
- Fixed 2 s bins: 0.68 per hour at 5 cells.
- ν_c = 0.256 and 0.019 at 0.01 Hz; 7.97, 3.86 and 0.284 at 0.05 Hz.
- Measured 0.262, 0.020, 7.97, 3.85 and 0.279, all inside exact Poisson 95 % intervals.
- 0.23 expected clusters at K=6, 0.01 Hz.
- 0.98 per hour at K=4, 0.0096 Hz; the crossing is at b = 0.00964 Hz.
- 5 and 8 cells; 0.33 per segment and a quarter of all clusters.
- Bursty background 0.99 per hour, unequal rates 0.79 per hour.
- Event floor 6 and 12, max(3, ·), rigid shift: matches ADR-0008 and `blind_a`.

**Table 1.1 and situations 1–5 (every cell matches the log):**
- 196 of 200 draws at 7–8 cells near event 2; 0.98 with events 1 and 3 removed.
- Chance hits 0.21, 0.34 and 0.01.
- Busier-stretch threshold 9–14 cells, 10–12 in the draw shown.
- False alarms 5 in 200 min = 1.5 per hour, interval 0.5–3.5; 4 of 5 within 13 s of an edge.
- CFAR's background estimate 0.0208 Hz, about twice the true rate.
- Merge gap 0.5 s gives 1.00 for all three detectors.
- 7 of 200 draws typical; seed 1015 shown.
- About 90 events per hour.
- The event list, the border at 45.95 s, the 60 s busier stretch against a 70 s reference span, and the merge gap of 3 s (`count.py` default) all match.

**§1.3 and Figure 1.4:**
- Peak 18.4 predicted / 18.3 measured; 4.6 / 4.6.
- HWHM 0.174 / 0.167 / 0.177 s (standard error 0.003); 0.835 / 0.821 s (standard error 0.021); both within about 1 standard error.
- Level 0.886 / 0.891 and 0.883 / 0.881; 0.859 at 2–3 s.
- The d formula equals the code's.
- 2√(ln 2) = 1.665.
- g₂ = 0.486, 0.887, 0.112, 0.486; measured 0.48, 0.87, 0.10, 0.47; within 0.02 of the full prediction.
- g₂ = ½ at 2.08 σ.
- 7.8e-10 share; 450/450, 442/450, 397 (88 %), 119 (26 %).
- Tool constants: lag to 10 s, shoulder at 5–10 s.
- The distinct-offset surrogate and its "35 %" both appear in the tool's docstring; 64 s span.

**§1.3.1 (realistic values):**
- 3.21 / 7.29 events per segment, medians 1 / 2, ranges 0–23 / 0–49, 28 and 25 segments with none.
- 9.72 and 22.05 events per hour; 17–20 min segments; 14–61 cells, median 32.
- Jitter 0.105 and 0.131 s, from the `bench.py` and `bench_slow.py` re-measures on the 66 recordings.

**§1.4:**
- 0.34–0.42 and 0.68–0.85.
- Assessor readings 0.07 / 0.23 / 0.49 / 0.72 s, 0.64–0.73 s and 0.43–0.68 s.
- 17 and 25 refusals.
- Ranges 2–19 and 2–35; factor 2.25.

**§1.5:**
- Sign test 24/32, p = 0.007.
- Residuals 0.007, 0.016 (worst 0.037, 0.11); held-out 0.012, 0.021 (worst 0.056, 0.13).
- Beyond 2 standard errors: 7 / 10 and 17 / 10; 5.7 against 2.2 expected; p = 0.0005–0.002.
- 18/32 (p = 0.60); 12 at 0.01 Hz (p = 0.03–0.07).
- Rate residual 0.032 → 0.020 and 0.024 → 0.014; bias +0.030 → +0.013 → +0.005; 35/48 (p = 0.01–0.04); 18/48; 0.055 → 0.059.
- Worst rate residuals 0.38 and 0.62; coordinated onset rate 0.018 and 0.011; pooled gap ±0.008.
- Denser trains: 1.16 / 0.90 against 0.99 / 0.97; general form within 0.04; 1.37 / 0.80 against 1.31 / 0.82; 3 of 6.
- Pooled rates: within 0.025 and 0.01; fast within 1.5 standard errors; slow up to 3.26 standard errors; rate 0.010–0.079 and participants 0.005–0.023; 1.160 / 1.081 and 0.909 / 0.932.
- Joint-fit ranges on both runs, 0.041 s and 0.030 s, 0.1–3.7 times planted.
- Tables 1.3, 1.4 and 1.5: every cell matches.
- Figure 1.11C in-band counts and Figure 1.12's 2/40 and 16/40.
- k̂/k = 0.45 at σ = w; the 0.9 crossing at σ/w = 0.177.
- Hard-core assumption changes ≤ 0.03 and ≤ 0.10; 1.62 / 1.43; 1.32–1.45.

**§1.6.2:**
- Table 1.6: every cell matches.
- Shares 0.89–0.96, 0.79–0.92 and 0.02–0.05; chance-cluster SDs 0.73 / 0.68 / 0.60 / 0.38 s.
- Mixture misses: within 0.015 s and 0.006 s; 0.02 s / 0.04 s low; 0.03 s low / 0.036 s high; shares 0.28–0.29 against 0.34; 0.58–0.62 against 0.74; ceiling 0.743 s.
- Null readings 0.727 / 0.671 / 0.595 s; excess moves 0.02–0.04 s.

**§1.8:**
- Ratio 1.044; C = 0.649; c = 0.376; Kreuz's factor 0.281.
- Figure 1.5C: +3, +5, −3, −5; F = 8/12.
- Membership: 9 % [8–11 %], 62 %, 14 %, 26 %, 2 %.
- Table 1.7: every cell matches the exact-5 % rows.

**Literature:**
- Rohling 1983: masking in Fig. 3, guard cells "usually" ignored, clutter-edge behaviour, the greatest-of comparison, OS-CFAR.
- Perkel 1967: "cross-correlation histogram".
- Thomas 1949: plant counts in quadrats.
- Neyman & Scott 1952: the cluster construction.

unreached: 31 — claims I did not verify:
- §1.7: 0.44, 0.59, 0.26–0.76 s, 2.5–5.8 σ, 0.12–0.22 s, 28,800 pairs / 576 points / 4 at p<0.01, 1.7 %, 98 %, 7 % / 1 %, and 3.2 s τ_min.
- §1.8.1: 72 % at reuse 0.3, and 13 % (8 of 60).
- §1.8.2: 33/33 with |z| ≤ 2.2; 0.503 and 0.753; "10 % high"; "0.03 high"; tie rates 21–26 % and 8–10 %; 0.06 → 0.66, 0.18 → 0.73 and 0.69 → 0.92; misses of 0.18 and 0.004; 5.2 %.
- §1.6.1: recall 0.76–0.80 and 0.29–0.33.
- §1.5.2: uniform-jitter gap 0.02 / 0.04.
- §1.5.3: 4–15 times and +0.4 to +1 %.
- §1.5.4: "about 0.05" without the at-most-one-event term.
- Figure 1.3: caption onset counts.
- Prior-work attributions not opened in this pass: Grün 1999 eq. 5, Pazienti, Louis–Borgelt–Grün Fig. 6, Müller, Wu & Müller, CuBIC eq. 3, Kish pp. 63–64, Kruskal sec. 4, Kreuz 2017 secs. 2.5 / 3.1, Tomlinson, Silva, Shah & Wainwright, Coppersmith, Diggle & Gratton, Waagepetersen, Williams, Wang, Malvache, Peyrache / Lopes-dos-Santos, Schrader, Cecchini, Mariani, and Kreuz 2022 / 2026.
