GRANT 1 MISMATCH — missing none; holds Edit, Write, NotebookEdit (forbidden), plus PowerShell, Agent, Artifact, Skill, ToolSearch and Claude Docs, Gmail, Dropbox MCP tools, none of which are in my grant

**Run finding:** I was spawned through the inline general-purpose fallback, so the run record's `roles:` line must say the review took a fallback path. I used only Read, Grep, Glob and Bash. I edited no tracked file. My scratch is under `_scratch/r4-role-01/` only. I did not open anything under `docs/reviews/`; I only checked by path that the run record exists.

## Recomputation done
- `theory.py` full `check()` was rerun from a scratch copy (`_scratch/r4-role-01/x/`). Its `theory_check.json` is identical to the shipped one: 0 differing values.
- `membership_limit.py` and `order_limit.py` were rerun in scratch. Both JSONs are byte-identical to the shipped ones.
- `theory.py --from-record` output is saved at `_scratch/r4-role-01/fromrecord.txt`.

## Findings (location · issue · severity · suggested fix · verifiable against a source?)

1. **Order section, "The lab's events per recording are not settled here… 10–25 in a 59 min recording, but its median intervals of 25–41 s imply more"** (extract l.300–303)
   - **Issue:** the glossary's 9.7/22.0/25.3 events per hour come from `docs/learned/runs/2026-09-25-real-intervals/`. That run covers 66 baseline windows totalling 21.8 h per stream, and `windows.csv` shows each window is 17–20 min, not 59 min. The 59-minute figure exists only in an older 85-slice todo (`2026-08-18-do-real-slices-have-recurring-assemblies.md`).
   - **Recomputed from `windows.csv`:** events per baseline window have median 1 / 2 / 3 (fast / slow / combined), with IQR 0–4, 0–8 and 0–11. Totals are 212/66 = 3.2, 481/66 = 7.3 and 552/66 = 8.4.
   - **"Median intervals imply more" is not a valid inference.** Those are within-window gaps of clustered events (95th percentile 368 s). The per-hour count is a direct measurement.
   - `synfire_scan.py` and `bugarach.assembly` both run on baseline windows only. So the scale the order indicator meets is around 1–8 events, below the page's smallest simulated case (10 events). This makes the no-order bias larger than the page implies.
   - **Severity:** high. **Fix:** quote events per baseline window from `windows.csv`, drop the 59 min figure and the "imply more" clause, and reframe the "at the lab's scale" text and plan item 3 around it. **Verifiable:** yes.

2. **Where it stands (l.9–10) and Settled row (l.355): "participants are predicted to within about 0.01 [at every jitter]"**
   - **Issue:** about 0.01 is the median residual (0.007 / 0.016), not a bound.
   - **Recomputed per jitter:** medians run 0.006–0.012 at 0.01 Hz and 0.011–0.020 at 0.05 Hz. Worst values are 0.037 and 0.106. At 0.05 Hz, 20 of 48 condition-windows are off by more than 0.02.
   - **Severity:** medium. **Fix:** say "median residual about 0.01 (0.02 at 0.05 Hz; worst 0.11)". **Verifiable:** yes.

3. **Blind section: "count-detector recall within about 0.03 of simulated recall in 20 of B's 24 conditions"**
   - **Issue:** from `blind_b/theory_count_detector.txt`, 19 of 24 are within ≤ 0.030; the 20th is 0.031. B's own report says "most cells" and also reports underprediction of up to 0.12 at 0.05 Hz and high K, which the page omits.
   - **Severity:** low. **Fix:** "19 of 24 within 0.03; up to 0.12 low at 0.05 Hz and high K". **Verifiable:** yes.

4. **"This session's at-most-one-event term was committed before either blind report arrived"**
   - **Issue:** commit d495ab0e (2026-10-23 15:40) does contain the term ("at most one event per window"). But when the blind reports arrived is recorded nowhere; they were committed later, in ccb31a16 at 23:35.
   - Both blind reports also derived the term: A writes "no two events share a window" and B writes "The m-terms are new".
   - **Severity:** low. **Fix:** cite the commit hash and time, and say that A and B derived the term too. **Verifiable:** partly (the commit yes, the arrival time no).

5. **GLOSSARY jitter entry: "σ = … 0.150 s combined", cited to `2026-09-23-jitter-by-group-66/`**
   - **Issue:** that folder holds only fast (0.1048) and slow (0.1306). The combined value 0.1503 is in `2026-09-23-jitter-correlogram-combined-senktide-ttx/jitter_correlogram.json`. The values themselves match.
   - **Severity:** low. **Fix:** add the second citation. **Verifiable:** yes.

6. **Order section, August numbers (ρ −0.75 / −0.40; 23/80, 44/82, 3/40; medians 0.036 / 0.099 / 0.101)**
   - **Issue:** all of these match the todo. But they come from the 84-recording folder, while every other lab parameter on the page comes from the 66-recording `senktide_ttx` default export. That export holds 66 recordings from 36 mice, so recordings are not independent units.
   - The record of group and mouse membership exists (the by-group-66 README, `bugarach.groups`), but the page does not account for it when it reads 23/80 against 3/40.
   - **Severity:** low–medium. **Fix:** name the folder and the 84 vs 66 scope difference, and note that recordings share mice. **Verifiable:** yes.

7. **Plan item 5: "PCA against it flags every simulated recording"**
   - **Issue:** `assembly_report.md` says "essentially every".
   - **Severity:** low. **Fix:** "essentially every". **Verifiable:** yes.

8. **Aim 1a bullet: "By the assessor's own rule, chance falls to one cluster per hour or fewer only from K = 5 … and K = 8"**
   - **Issue:** these are closed-form predictions from 60 q(1 − q)², not measurements. They sit in a list headed "per-condition medians … unless marked pooled".
   - The one-per-hour budget is ADR-0008's, not the assessor's; `assess.py` has no hourly rule. The values themselves match theory.py's output (0.07 and 0.53 per hour).
   - **Severity:** low. **Fix:** "predicted, by the assessor's clustering rule against ADR-0008's one-per-hour budget". **Verifiable:** yes.

9. **Plan item 3: "PySpike with the unmerged PR #89"**
   - **Issue:** FOUNDATIONS §2 says the fix was made upstream "until that lands in a release". Nothing in the repo supports "unmerged".
   - **Severity:** low. **Fix:** "not yet in a release". **Verifiable:** no (upstream state).

10. **Kreuz table, null row, and the GLOSSARY "exchangeable limit" entry: the August null "permutes which cell owns each onset across the whole recording"**
    - **Issue:** `synfire_scan._relabel` permutes within the analysis window only, which is the baseline window.
    - **Severity:** low. **Fix:** "across the baseline window". **Verifiable:** yes.

11. **Claims that cannot be checked from any kept source.** Each is labelled "not kept" on the page, so this is the record:
    - the surrogate/event-train term "about 1 % of pairs, about 3 % in rate";
    - the PySpike 0.9.0 test (36 %, 23 %, 44 %);
    - frame ties lowering F "about 9 %";
    - the frame-rounding bias "8 % / 35 %";
    - "0.2 s read as 0.17 s" from the dropped one-parameter fit;
    - the C `rand()` claim about PySpike's annealer;
    - F_Kreuz = F(k − 1)/(N − 1), which I can only check arithmetically: 9/32 = 0.28;
    - every literature citation, including the Mariani 9.7 s vs 861.8 s figures and Kreuz's quoted sentence;
    - Tony's quotes and Settled-table decisions (none are recorded in the repo).

    "2 SD up to about 3 templates … about 80" is not in any record. I recomputed it from `order_limit.json` as √(F_M² + F₀²) − F₀ ≥ 2 SD with F_M = 0.649/√M, which gives M ≤ 3.0 and M ≤ 81, so it matches under that assumption. **Fix:** have `order_limit.py` print it. **Severity:** low.

## Claim ledger (quoted · source · recomputed · verdict)

All of these **match**.

**Grid**
- 240 recordings = 48 conditions × 5.
- 160 recordings with 10+ cells.
- k = 5 / 10 / 20, exact in the record (80 each).
- N = 33, 45 min, K = 3 / 4 / 6, w = 1 / 2 / 4 s.
- Events at least 20 s apart (`MIN_SEP`).
- 100 background-only recordings per background.
- 17 of 720 refused, all 5-cell at 0.05 Hz.

**Chance clusters and the event floor**
- Chance clusters, measured: 7.97 / 3.85 (pooled 7.974 / 3.848).
- Planted events: 0.33 / 1 per minute.
- Predicted: 0.256 / 0.019 / 7.97 / 3.86 / 0.284. Measured: 0.262 / 0.020 / 7.97 / 3.85 / 0.279, all inside their CIs.
- K = 6 at 0.01 Hz: 5.12e-5 per minute, 0.23 expected clusters.
- ADR-0008 floor 6 / 12 cells, matching A's and B's floor files.
- Rule "starts a cluster only when the two preceding bins are below K" matches `merge_bins = 2`. Gather ±1.5 s matches `wm_factor`.

**Aim 1a measurements**
- K = 6 recall: 0.76–0.80 at 0.5 s jitter and 0.29–0.33 at 1 s.
- Assessor jitter at 0.01 Hz, K = 4: 0.07 / 0.23 / 0.49 / 0.72 s. At 0.05 Hz: 0.64–0.73 s (K = 3 or 4) and 0.43–0.68 s (K = 6).
- Truncated Gaussian SD 0.74 s (0.7426).
- Participants at 1 s jitter: 0.34–0.42 (1 s window) and 0.68–0.85 (4 s window); 4 s window at every jitter 0.68–1.04.
- Rate at the 1 s window: 1.6–2.4 times planted.
- Share: 0.78–1.11 and 0.67–1.11.
- 5-cell events: up to 6.3 / 6.4 times planted; 0–0.27 at K = 6.

**Aim 0 residuals and joint fit**
- Participant residuals: 0.007 / 0.037 and 0.016 / 0.106; Poisson version about 0.05 (0.046 / 0.049).
- Beyond 2 SE: 7 and 10 of 48, against 5.7 expected; null rate 0.118.
- Below predicted in 34 and 31 of 48; sign test p = 0.006 and 0.059; median 0.006 and 0.005.
- Rate residuals: 0.03 / 0.18 and 0.06 / 0.38. Share residuals: 0.02 / 0.07 and 0.02 / 0.28.
- Measured above predicted: 43 / 41 and 30 / 29 of 48.
- Joint fit jitter: 0.22 / 0.50 / 1.01 s (0.495 rounded) and 0.20 / 0.52 / 1.01 s.
- Ranges per condition: jitter 0.88–1.13 of planted, participants 0.94–1.14, rate 0.73–1.14.
- At 0.05 s planted: reads 0.075 and 0.039 s, with 1 and 4 of 20 fits at the bound.
- 5-cell jitter: 0.1–3.6 times planted.
- Lab jitter σ = 0.105–0.150 s; half-width ≈ 1.67σ (1.665).

**Blind passes**
- Shared-background flaw found by both.
- B's 2 % median jitter error.
- B's window ratio reads 0.2 s at 1.05–1.15 of planted.
- B's triple count 5–7 % low over 60 seeds; 3–19 % in the saved 40-seed run.
- A's rate 3–5 % high.
- A drops the 1/N terms; B drops the 1/N² term in the triple count.

**Membership**
- 1 + (E − 1)/M within 1.0–1.9 % below.
- Both nulls reject in 60/60 at reuse 1–15, 43/60 (72 %) at 0.3, 8/60 (13 %) at 0.045, and 1/60 under random participation.
- At M = 1 only the uniform null rejects (60 recordings).
- Package default 1000 surrogates.

**Order**
- One template: 0.503 / 0.753 against 0.500 / 0.758; 1.9 % below at r = 5; 0.176 against 0.156.
- M templates: constant 0.649; up to 9.8 % high at M = 2–16.
- No order: c = 0.38 / 0.50 over n̄ 2.1–68; across fields 0.22–0.51 and 0.31–0.60.
- Few events: 0.48 ± 0.06 (n̄ 0.40), 0.14 ± 0.02 (n̄ 5.57), 0.34 ± 0.04, 0.09 ± 0.01.

**Other**
- Kreuz normalization factor 9/32 = 0.28.
- August todo numbers all match.
- Poisson "up to 0.20 at 4 s" recomputes to 0.194.
- `pairs` and `hwhm` take in-memory arrays.
- Every page link resolves.

**Sources not consulted.** For the synthetic work, the record of units is the JSONs, and they reconcile. For the real-data claims, the unit record (66 recordings / 36 mice, `windows.csv`) exists but the order section did not use it (findings 1 and 6).
