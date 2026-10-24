GRANT 1 MISMATCH — missing none; holds Edit, Write, NotebookEdit (deferred), PowerShell, Agent, Artifact, Skill, ToolSearch, plus MCP write tools (Gmail, Dropbox, Claude Docs). These are forbidden editing tools; I did not use any of them. I ran in a general-purpose harness through the inline fallback, so the run record's `roles:` line must say this role took a fallback path.

**Role 01, Prove It: claim ledger and findings.** Aim 0 page lines 16–241 and 286–311, plus the new GLOSSARY entries. Blindness rule kept: I opened no `docs/reviews/synthetic-validation-aim0*`, `_scratch/role-*`, `_scratch/aim0_*` or prose_report file. No tracked file was touched. Scratch is only `_scratch/r2-role-01/`.

## Reproduction (done first)
- I reran `theory.check()` into scratch by redirecting `HERE`. The result is identical to the committed `theory_check.json`: every field within 1e-9.
- I ran `membership_limit.py` and `order_limit.py` from scratch copies. Both JSONs are byte-identical to the committed ones.
- Every number below was recomputed from these records, with `theory.summary()` and my own `_scratch/r2-role-01/fig1.py`.

## Claim ledger (quoted · source · recomputed · verdict)
**Aim 1a / Figure 1**
- 240 recordings, 33 cells, 45 min · `aim1_one_source.json` · 240 rows (240 unique condition×seed pairs), n_roi 33, 2700 s · match
- k = 5/10/20 from participation 0.15/0.3/0.6 · record `true.k` · 5.0 / 9.9 / 19.8 round to 5/10/20 · match
- First run seeded 1000 + replicate; generator draws background first · git `d93b5c0d` (`seed=1000 + seed`); `simulate.py` line 775 onward · match
- Each recording has its own seed now · `1000+100·idx+seed`, all unique · match
- Share "within about 25 % of planted **in every condition** at the 2 and 4 s windows" · theory_check per-condition medians · 2 s: 0.53–1.53, with 6/48 conditions outside 25 %. 4 s: 0.09–3.58, with 6/48 outside, including one at 0.01 Hz (k 5, σ 0.2, 15 events, 4 s: 0.71). It holds only at the figure-point level (pooled medians 0.86–1.10) · **mismatch**
- Share at 1 s, 1 s jitter: 0.74 (C, G) · C 0.74, G 0.79 · match for C; G is 0.79
- Participants: 1 s window reads 0.4 at 1 s jitter (A, E) · 0.40 / 0.39 · match
- 4 s window within about 30 % · 0.72–0.89 · match
- Assessor K = 4/6 within about 30 % at 0.01 Hz · 0.90–1.10 · match
- K = 3/4 at 0.05 Hz: 16× and 8× planted rate (F) · 15.5–15.8× / 7.8–8.1× · match
- "K = 6 misses most 5-cell events (B, 0.3 at 1 s jitter)" · 0.30 is the pooled figure point over k = 5, 10 and 20. The 5-cell-only ratios are 0.20, 0.07, 0.06 and 0.00 · **mismatch of attribution**: the claim is true, the number is not its evidence
- Assessor jitter "about 0.66 s whatever was planted at 0.05 Hz (H)" · absolute medians K3 0.72–0.73, K4 0.66–0.69, K6 0.49–0.67 · partial: true of K = 4 only
- "tops out near 0.7 s" · max 0.734 · match
- ±1.5 s gather; a 1 s Gaussian cut at ±1.5 s has SD 0.74 s · `assess.py` `wm = 1.5 × bin`, bin 1.0; truncated-normal SD 0.743 · match

**Aim 0 predictions** (`theory_check.json` / `summary()`)
- Participants residual median 0.009 (worst 0.056) at 0.01 Hz · 0.009 / 0.056 · match
- Participants residual, ≥10 cells at 0.05 Hz: median 0.015 (worst 0.11) · 0.015 / 0.107 · match
- Poisson-only residual "about 0.05" · 0.045–0.048 · match
- Rate, ≥10 cells: median 0.03–0.06, worst 0.18–0.38 · 0.031 / 0.055, 0.182 / 0.384 · match
- Share: median 0.02, worst 0.07–0.28 · 0.018 / 0.024, 0.071 / 0.283 · match
- "Not predicted: 5-cell at 0.05 Hz, worst off by 5.6" · 5.608 (k = 5, σ 1, w 2) · match
- Refused in 17 of 720 recording-windows, all at 0.05 Hz · 17, all at 0.05 Hz and all at k = 5 · match
- Joint fit at 0.2/0.5/1.0 s reads 0.22/0.49/1.01 (0.01 Hz) and 0.20/0.52/1.01 (0.05 Hz) · 0.217/0.494/1.010 and 0.195/0.519/1.011 · match
- Joint fit: "participants and rate within 4 %" · true of the medians of condition medians (k 0.98–1.04, rate 0.97–1.04). Per condition (k ≥ 10) the range is k 0.94–1.14 and rate 0.73–1.14 · **overstated**: it is a median of medians
- Planted 0.05 s reads 0.07 and 0.03 s, with 3 and 7 of 20 fits at the bound · 0.069 / 0.026, 3 / 7 · match
- "5-cell events (jitter off by up to 2×)" · k = 5 summary values: 0.05 → 0.005 (10× low, at the bound), 0.2 → 0.53 (2.65×) and 0.12 (0.6×), 1.0 → 1.85. Per-condition medians reach 2.88 s at planted 1.0 and 0.005 at planted 0.05 · **mismatch**
- Chance clusters predicted 0.26/0.02/0 and 7.97/3.86/0.28; measured 0.27/0.04/0 and 7.94/3.96/0.22; 10 recordings each · 0.256/0.019/5e-5 and 7.973/3.860/0.284; 0.267/0.044/0 and 7.944/3.956/0.222; n = 10 · match
- Chance formula 60 q (1 − q)² · `theory.py` and both blind reports · match
- "Participants predicted to within seed-to-seed noise" · residual ÷ approximate SE of the median: \|z\| > 2 in 8 % of cases at 0.01 Hz, but in 23 % at 0.05 Hz (k ≥ 10) · holds at 0.01 Hz, weak at 0.05 Hz
- Tried and dropped: Poisson left a 5 % residual, up to 20 % at 4 s · max 0.189 / 0.193 · match

**Blind-pass table and attributions** (`blind_a/REPORT.md`, `blind_b/REPORT.md`, `blind_b/*.txt`)
- Blind A: no 1/N factor; Blind B: no 1/N² in the triple term · the reports' formulas · match
- B's ratio of two windows reads 0.2 s 5–15 % high · `jitter_from_window_ratio.txt` 1.05–1.15 · match
- A by Charlier polynomials, B by the delta method; B's hard-core bias · reports · match
- Up-crossing floor exact or within one cell (both) · A: 5/6 exact, 1 off by one; B: 25 exact, 5 off by ±1 · match
- Floor is 6 cells at 0.01 Hz and 12 at 0.05 Hz · both reports · match
- Count-detector recall within about 0.03 in 20 of 24 conditions (B) · 19 within ≤0.030, 20 if 0.031 counts · match (the "20" is a count B's report never stated; it was derived from the txt)
- "Chance joiners lift a 5-cell event past 6 about a third of the time at 0.01 Hz (B)" · `theory_count_detector.txt` recall 0.33–0.34, but only at σ = 0.2 (0.08 at σ = 1.0) · partial: an unstated σ condition
- B's triple count 3–19 % below prediction at 0.05 Hz, 40 seeds · sim_cumulant_check: 0.970, 0.807, 0.952, 0.947; `nseed = 40` · match. The 19 % point is about 2 SE.
- A's rate 3–5 % above · report · match
- "This session's exact term was committed before either blind report arrived" · exact term in `d495ab0e` at 15:40; blind reports in `bc0a1f80` at 15:54 · consistent with commit order; arrival time not recorded · partly verifiable

**Membership and order** (`membership_limit.json`, `order_limit.json`)
- 400 simulations per point; 1 + (E − 1)/M · reps 400; measured within about 2 % of predicted · match
- Detected every time while reuse ≥ 1 · 1.0 for M ≤ 45 · match
- 63 % at 0.3 uses per assembly · 0.63 · match
- "8 % at 0.04" · reuse 0.045, detected 0.085 · rounding only; low
- Figure 3: "grey band, the 95 % range of a single random recording" · `aim0_figures.py` `axhspan(1, random_p95)`. The band runs from the random mean to the one-sided 95th percentile, so it is not a 95 % range · **mismatch (label)**
- F = (2/π) arctan τ · τ = 1 gives 0.500 against 0.503 measured · match
- Signal term falls as 1/√M; bias adds in quadrature · `pred_many` ∝ 1/√M; hypot · match (by construction)
- No-order constant 0.38 (score sort) and 0.50 (search) · 0.36–0.38 / 0.49–0.51 · match
- "0.22 to 0.61 across 15–100 cells" · c_score 0.216–0.508; c_search 0.314–0.602. The quoted range takes its low end from one method and its high end from the other, and 0.602 rounds to 0.60 · **mismatch**
- Kreuz normalisation factor 0.28 at 10 of 33 cells · only "murderboard role 6", repeated in the `order_limit.py` docstring; no script or record computes it · unverifiable
- Panel A uses 200 events; panel B uses τ 2.5 and 2000 events · `order_limit.py` · match
- August ρ −0.75 fast / −0.40 slow · `todo/2026-08-19…` line 71 · match
- August null "permutes which ROI owns each spike" · same todo, line 34; `synfire_scan._relabel` · match
- `derive_k` / MAHICE · `annotate.py:466` · match
- assembly Marchenko–Pastur note; `assembly_report` "flags essentially every simulated recording" · `assembly.py:43`; `assembly_report.md:342` · match
- Window-budget closed form · `measure_chance_floor.py` · match
- Kreuz 2022 JNM 381:109703 is the latency-correction paper · `detector_history.md:169` · match
- Mariani 2025: 9.7 s against 861.8 s · nowhere in the repo · unverifiable
- External citations (Staude 2010, Ehm 2007, Grün 1999, Kreuz 2017, Coppersmith 2010, Shah & Wainwright 2018, Williams 2020, Kruskal 1958, Kish 1965, BBP 2005) · bibliographic details match what I know; I opened none (no web tool in grant) · unverifiable from a source

**Glossary**
- √(2 ln 2)·σ√2 ≈ 1.67 σ, as half width at half height · arithmetic 1.665; the correlogram tool's primary width is `hwhm` · match
- **New note plus page "Symbols": "the glossary's correlogram half-width is a different measure of the same spread"** · the glossary jitter entry it annotates quotes "half-width … 0.105 s fast, 0.131 s slow". `learned/runs/2026-09-23-jitter-by-group-66/README.md` lines 51 and 56 show 0.105 and 0.131 are the **calibrated σ** column; the half-widths there are 0.186 and 0.228 · **mismatch, inherited and now amplified**

## Findings
1. **GLOSSARY.md ~469–476, and page "Symbols" σ line.**
   - Issue: the glossary's 0.105 / 0.131 s are calibrated σ (an SD, the same quantity as `jitter_sec`), not half-widths (0.186 / 0.228). The new note tells readers they are a different measure, roughly 1.67 σ. A reader who converts would get σ ≈ 0.063 s, wrong by 1.67×. The benches plant 0.106 / 0.135 s as `jitter_sec`, which confirms the values are σ.
   - Severity: high.
   - Fix: relabel the glossary values as calibrated σ (half-width 0.186 / 0.228 s, 66-recording run), and reword the note and the page line to say so.
   - Verified against source: yes.
2. **Page, Aim 0 joint-fit bullet: "5-cell events (jitter off by up to 2×)".**
   - Issue: the recomputed error reaches 10× low (0.005 s at the bound, against 0.05) and 2.65× high (0.53 against 0.2). Condition medians reach 2.88 s against 1.0.
   - Severity: medium.
   - Fix: say "off by up to 10×, or not identified".
   - Verified: yes.
3. **Page, Aim 1a share bullet: "within about 25 % … in every condition at the 2 and 4 s windows".**
   - Issue: false by the page's own definition of a condition (one k, σ, event count and background). 6 of 48 conditions fall outside at each window, from 0.09 to 3.58, all at k = 5 and 0.05 Hz, plus one at 0.01 Hz (0.71). It is true only of Figure 1's pooled points.
   - Severity: medium.
   - Fix: say "in every Figure 1 point", or exclude 5-cell events at 0.05 Hz.
   - Verified: yes.
4. **Page, joint-fit bullet: "participants and rate within 4 %".**
   - Issue: this is a median of condition medians. Individual conditions with k ≥ 10 reach a k ratio of 1.14 and a rate ratio of 0.73.
   - Severity: medium.
   - Fix: say "median within 4 %; conditions within 14 % (participants) and 27 % (rate)".
   - Verified: yes.
5. **Page, order: "0.22 to 0.61 across 15–100 cells".**
   - Issue: the range mixes the score-sort minimum (0.216) with the search maximum (0.602, which rounds to 0.60).
   - Severity: low–medium.
   - Fix: "0.22–0.51 under the score sort, 0.31–0.60 under the search".
   - Verified: yes.
6. **Figure 3 caption and legend in `aim0_figures.py` line 132: "95 % range".**
   - Issue: the band runs from 1 (the random mean) to the one-sided 95th percentile.
   - Severity: low–medium.
   - Fix: "from the random mean to its 95th percentile".
   - Verified: yes.
7. **Page, Aim 1a: "K = 6 misses most 5-cell events (B, 0.3 at 1 s jitter)".**
   - Issue: 0.3 is the point pooled over k = 5, 10 and 20. 5-cell recall at K = 6 is 0.00–0.20.
   - Severity: low.
   - Fix: quote the 5-cell values, or say that 0.3 is pooled.
   - Verified: yes.
8. **Page, Aim 1a: assessor jitter "about 0.66 s whatever was planted at 0.05 Hz".**
   - Issue: true for K = 4 only. K = 3 reads 0.72–0.73 and K = 6 reads 0.49–0.67.
   - Severity: low.
   - Fix: "0.5–0.73 s depending on K".
   - Verified: yes.
9. **Page, blind section: "chance joiners lift a 5-cell event past 6 about a third of the time at 0.01 Hz (B)".**
   - Issue: the source value (recall 0.33–0.34) is at σ = 0.2 only; at σ = 1.0 it is 0.08. It is also a count-detector result, not the assessor's.
   - Severity: low.
   - Fix: add "at 0.2 s jitter".
   - Verified: yes.
10. **Page, participants bullet: "predicted to within seed-to-seed noise".**
    - Issue: holds at 0.01 Hz (8 % of cases beyond 2 SE). At 0.05 Hz (k ≥ 10), 23 % are beyond 2 SE.
    - Severity: low.
    - Fix: qualify the 0.05 Hz half.
    - Verified: yes (approximate SE).
11. **Page "Where it stands": "a fit across its three windows recovers jitter … for events of 10 or more cells".**
    - Issue: it omits that 0.05 s jitter is not resolved, which the body does state.
    - Severity: low.
    - Fix: add "at jitter ≥ 0.2 s".
    - Verified: yes.
12. **Page and `order_limit.py` docstring: the Kreuz normalisation factor "0.28 at 10 of 33 cells".**
    - Issue: its only source is a review role's report. No script or record in the repo computes it.
    - Severity: low–medium.
    - Fix: add a computation to `order_limit.py`, or mark it unverified.
    - Verified: no.
13. **Page, order: Mariani et al. 2025, "9.7 s against 861.8 s".**
    - Issue: not in any repo source, and not opened.
    - Severity: low.
    - Fix: cite the figure or table, or mark it "⚠ not opened".
    - Verified: no.
14. **Run record (not the artifact).**
    - Issue: GRANT MISMATCH. This reviewer held editing tools through the inline fallback.
    - Severity: process.
    - Fix: the run record's `roles:` line must say "fallback path".
    - Verified: yes.

## Also checked, clean
- **Regeneration diff, new record against `aim1_one_source_shared_seeds.json`:** same 240 rows and 48 conditions. The new record adds the `cum` field and a 20-recording chance arm. Coordination-rates NaNs fell from 35 to 17. Assessor K = 6 has `part` / `jit` NaN in 12 of 240 recordings (14 before), excluded by `aim1_figure.py`. 45 recordings are `jit_defined = False`, which concerns the surrogate side only; their observed jitter is valid, and excluding them barely changes the medians.
- **Unit-membership record:** the deliverable is synthetic only. Its one real-data number (August ρ) is quoted from its todo, and the glossary's jitter values come from the 66-recording run. No new real-data membership claim needs a design record.
