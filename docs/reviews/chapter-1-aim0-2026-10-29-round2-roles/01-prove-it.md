GRANT 1 MISMATCH — missing none; holds Edit, Write, NotebookEdit (deferred), and also PowerShell, Agent, Artifact, Skill, ToolSearch, SubagentHandback and claude.ai/plugin MCP connectors, none of which the process file grants. I did not use any editing tool. My only writes were scratch scripts and printouts in my own `work-r2-1/` scratch folder.

# Role 1, "Prove It": claim and data verification of `docs/dissertation/chapter-1-aim0.md` (hash cdc8fbf6, confirmed)

## How I checked
- **Main record.** I ran `theory.py --from-record` using the main checkout's venv, because the worktree has no numpy.
- **Follow-up records.** I read `ch1_followups/{like_for_like,lab_values,order_power,correlogram_vs_joint}` (README/.txt), `held_out_summary.txt`, `order_limit.json` and `membership_limit.json`. I also read the per-condition joint-fit rows in `theory_check.json` and `ch1_followups/theory_check_heldout.json`, and the row data in `aim1_one_source.json`, `aim1_one_source_heldout.json` and `aim1_one_source_shared_seeds.json`.
- **Separation.** I read `separation/floor/derivation.md` and `separation/assessor_split/derivation.md`.
- **Code.** I checked `src/bugarach/assess.py`, `src/bugarach/detectors/count.py`, `tools/measure_coordination_rates.py`, `event_train.py`, `bench.py` and `bench_slow.py`.
- **Recomputed independently:**
  - the chance-cluster rates and budget thresholds;
  - k̂/k at σ = w/6 and σ = w;
  - Gaussian against uniform g₂/g₃, by Monte Carlo;
  - all sign-test p values;
  - (2/π)arctan r, the many-template amplitude, c(33,10), and (k−1)/(N−1);
  - the refusal counts;
  - per-cell resolution in Figure 1.11 on both records.
- **Literature spot checks:**
  - the Kreuz 2017 quote and its section;
  - Coppersmith's factor of 5 and the condition that pair weights sum to one;
  - Grün 1999's fission probability, Eq. 5;
  - Louis 2010 Fig. 6, "disentangle as their sizes converge";
  - Kruskal 1958 crediting Esscher;
  - Thomas 1949 working with quadrat counts only;
  - Kish 1995 p. 63, roh = (deft² − 1)/(n/a − 1), rendered from the scan.
- **Source of record for unit membership.** For this synthetic chapter, the design record is each run's seeding. The headline numbers come from the per-recording-seed rerun (`seeding` field present), not from the superseded `aim1_one_source_shared_seeds.json`. The realistic interval lists come from a dataset named `..._STEPS_AND_PINS_EXCLUDED`, so the lab's exclusions were applied upstream.

## Findings

| # | Location | Issue | Severity | Suggested fix | Verified against source |
|---|---|---|---|---|---|
| 1 | Fig. 1.11 and its caption; §1.8 ("between the joint fit's resolved point (0.2 s)…", "the resolved 0.2 s column", "the well-predicted 10-cell arm"); Fig. 1.1 title ("tracks the planted value from 0.2 s up") | Figure 1.11 is built from the **in-sample** record only. On the held-out record (`theory_check_heldout.json`), the 10-cell, σ = 0.2 s cell reads 0.98–1.36 (bg 0.05, E = 15 gives **1.36**), which fails the figure's own 0.8–1.25 criterion. The 5-cell, σ = 0.5 s cell, shown filled in-sample (0.87–1.13), reads 0.66–1.55 held-out. §1.3 says "where they differ, the held-out value is the honest one", so by the chapter's own rule two filled circles should be open. That includes the 10-cell point right beside the fast-type box that the §1.8 argument leans on. | major | Redraw Fig. 1.11 from the held-out record, or draw both records; on the held-out record only the 20-cell column is resolved from 0.2 s up. Recast §1.8 and the Fig. 1.1 title. | yes |
| 2 | §1.4.6 Table 1.2, rows "0.05 Hz, 0.5 s" and "0.05 Hz, 1.0 s" | The caption says "Off the curve" counts are given, but these two rows leave them out. The source (`ch1_followups/README.md`, Task 1) has **2 below** for 0.5 s and **5 above, 3 below** for 1.0 s. For 1.0 s that means 8 of 20 recordings are missing from the median and IQR (0.42 [0.27, 0.55]), and the source warns the IQR is "censored where off is large". The chapter's "It fails at 1 s" is also partly a range limit of the calibration at 0.01 Hz: the same widths through the Gaussian conversion read 0.97 [0.91, 1.08]. | major | Add the off-curve counts to every row. Say that the 0.01 Hz failure at 1 s is the calibration's top end, not the correlogram itself. | yes |
| 3 | §1.4.5, "the event rate was set to one over the mean interval, 0.0099 Hz, which makes these trains denser than the hard-core trains above" | The hard-core trains ran at 15 or 45 events per 2700 s, which is 0.0056 or **0.0167 Hz**. At 0.0099 Hz the renewal trains are denser than the 15-event arm but sparser than the 45-event arm, so the claim is false as written. Also, `lab_values.txt` gives the realized planted rate as 0.00944 Hz (25.5 events per recording), and the ratios are to that value, not to 0.0099. | minor | Say what is meant, presumably that intervals under 20 s occur (5th percentile 3.8 s). Give the realized rate the ratios are taken against. | yes |
| 4 | §1.4.5, "On a slow-type interval list … both forms predict it" | Not true everywhere. At 13 cells and the 4 s window, the tool measures rate 1.235; the hard-core form predicts 1.334 (off by 0.10) and the general form 1.273 (off by 0.04). At 7 cells, 4 s, the general form predicts 1.306 against 1.365 measured. | minor | Give the worst miss for each form, or say "both forms come within 0.10". | yes |
| 5 | §1.3, "The tool refused in 17 of 720 recording-windows, all 5-cell events at 0.05 Hz" | Correct for the first experiment. The held-out record, which the chapter also quotes, has **25 of 720**, including one 10-cell recording-window (bg 0.05, w = 1 s). That window falls inside the 10+-cell statistics reported in §1.4.4 and §1.4.6. | minor | Give both counts, and note the 10-cell refusal. | yes |
| 6 | §1.7, "The oracle reaches 0.07–0.2 s" | The sentence is about the four realistic combinations at 80 % power. There the oracle's Δ₈₀ is **0.12–0.22 s** (`floor/derivation.md` tables at b = 0.0096), and 0.18 s and 0.15 s at the two operating points (line 267). The 0.07 is a 20-cell Δ₅₀. | minor | Use 0.12–0.22 s, or state the k range and the power level. | yes |
| 7 | §1.4.6, Table 1.2 against the text "Planted 0.05 s … reads 0.041 s … 0.030 s" | Two summary statistics are used for the same quantity without saying so. Table 1.2 is the median of per-recording ratios (1.33 and 0.89 at σ = 0.05 s). The text's 0.041 and 0.030 s, and `theory.py`'s 0.075 and 0.039 s, are pooled condition medians; in-sample those would be ratios of 1.5 and 0.78, not 1.33 and 0.89. A reader comparing them will think one is wrong. | minor | Name the statistic in each place. | yes |
| 8 | §1.4.6, "Events of 5 cells read anywhere from 0.1 to 3.6 times planted" | This follows the held-out sentence, but 0.10–3.56 is the in-sample range. The held-out range is 0.10–3.71, and at 0.01 Hz it is 0.66–1.31. | minor | Label it in-sample, or give both. | yes |
| 9 | §1.6.2 text, "two need five or more", against the Fig. 1.8 title, "two templates need more than five" | These contradict each other. Table 1.3 has two templates at 5 events reaching only 0.67 and 0.77, both below 0.8. | minor | Use "more than five" in both places. | yes |
| 10 | §1.6.1, "still in 13 % at reuse 0.045 … where the variance ratio is 1.04" | 1.04 is the **predicted** ratio (1.044). The simulated ratio is 1.032. | minor | Say "predicted 1.04 (simulated 1.03)". | yes |
| 11 | §1.4.5, "The general form predicts the tool to within 0.01–0.04 at every window" | Recomputed from `lab_values.txt` (fast list), the misses run 0.000–0.040, so the sentence means "within 0.04". The "0.01–0.04" wording reads as a band. | minor | Write "within 0.04". | yes |
| 12 | §1.9.4 item 4, "lowered F by about 9 % … in a review agent's test (not kept)" | This is a number with no surviving source. The chapter discloses it, but a committee cannot check it. | minor | Rerun it and keep the script, or remove the number and keep the qualitative caveat. | no (unverifiable by construction) |
| 13 | §1.2.1 and References, "DeFazio et al. 2026 … *J Neuroendocrinol* 38:e70298" | The only place this citation appears in the repository is the chapter itself. I could not tie it to a source. The values attributed to the lab (0.0096 Hz, 0.105 s, 0.131 s, participation 0.203 and 0.375) do trace to `bench.py` and `bench_slow.py`. | minor | Point to where the values were measured (the bench docstrings, or the run folder), not only to the paper. | partly |

## Claim ledger: verified matches (quoted value, source, recomputed value)

- **§1.1**
  - 7.97 and 3.85 chance clusters per minute (`--from-record`: 7.9744, 3.8480).
  - Assessor jitter at 0.01 Hz, K = 4: 0.07, 0.23, 0.49, 0.72. At 0.05 Hz, K = 3/4: 0.64–0.73. At K = 6: 0.43–0.68. All match.
  - "Within about 1–2 %": median residual 0.007–0.021, matches.
- **§1.3**: 48 settings × 5 = 240, 33 cells, 2700 s, 20 s minimum separation; 200 chance recordings; 17 of 720 refusals, all 5-cell at 0.05 Hz. All match (`aim1_one_source.json`).
- **§1.4.1**: Gaussian against uniform maximum difference is 0.020 (g₂) and 0.035 (g₃) by Monte Carlo, so "0.02 and 0.04" matches.
- **§1.4.3**: k̂/k = 0.907 at w/6 and 0.883 at w/5, so "about w/6" is acceptable; 0.450 at σ = w matches. 1 s window 0.34–0.42 and 4 s window 0.68–0.85 match.
- **§1.4.4**
  - Residuals 0.007/0.016 (worst 0.037/0.106) in-sample and 0.0115/0.0209 (worst 0.056/0.132) held-out match; the Poisson-train residual of about 0.05 (0.046/0.049) matches.
  - 7 and 10 beyond 2 SE in-sample, 17 and 10 held-out; null rate 0.118, so about 5.7 expected. All match.
  - 24 of 32 below predicted gives p = 0.0070 (recomputed). Rate 0.032/0.024 and 0.055 (worst 0.38/0.62) match. Share 0.0175 rounds to 0.018 (`theory.py` prints 0.017), acceptable.
- **§1.4.5**
  - 18 of 32 gives p = 0.597, matches; 12 beyond 2 SE with P = 0.009 matches.
  - Rate 0.0324 → 0.0196 and held-out 0.0236 → 0.0141 match; signed +0.0298 → +0.0129 matches; 35 of 48 (p = 0.0021) and 18 of 48 (p = 0.111) match; 0.0553 → 0.0587 matches.
  - Realistic values: 1.158/0.902 predicted against 0.989/0.966 measured matches; slow 1.37/0.80 matches; Poisson, hard-core, renewal, empirical and Palm trains all exist in `event_train.py`.
- **§1.4.6**
  - In-sample ranges 0.91–1.13 / 0.88–1.12, participants 0.94–1.14 and rate 0.73–1.14 (union of both backgrounds) match. Held-out 0.86–1.22 / 0.86–1.36, 0.98–1.06 / 0.89–1.16 and 0.94–1.04 / 0.87–1.45 match. 0.041 s with 3 of 20 at the bound and 0.030 s with 7 of 20 match.
  - Table 1.2 matches `ch1_followups/README.md` cell for cell, apart from the omissions in finding 2.
  - Realistic joint fit: 1.06 [0.39, 1.53], 8 at the bound, 10 of 40; 0.88 [0.40, 1.48], 9 of 40; participants 0.97–1.05; rate 0.86–1.03; slow 17 and 19 of 40; hard-core form 1.62 and 1.43; bound 0.005 s. All match.
- **§1.5 and Fig. 1.5**
  - Predicted 0.2558/0.0191 and 7.973/3.860/0.2838 per minute, recomputed and matching.
  - Measured 0.262/0.020 and 7.97/3.85/0.279 match.
  - K = 5 at 0.01 Hz (0.066 per hour) and K = 8 at 0.05 Hz (0.53 per hour) match; 0.98 per hour at 0.0096 Hz, K = 4, matches; 0.2 expected clusters at K = 6 matches.
  - 0.76–0.80 and 0.29–0.33 match; the event floor of 6 and 12 matches the earlier record.
- **§1.2.2 code behavior**
  - Assessor: merge_bins = 2, which joins across one untriggered bin; gather window ±1.5 × 1 s; 1 s bins. Matches.
  - Count detector: 2 s bins, distinct cells, 3 s merge gap. Matches.
  - Coordination-rates tool: windows (1, 2, 4) s, two offsets, circular-shift surrogates. Matches.
  - Fig. 1.2: the 4 + 6 split is visible in the rendered PNG.
- **§1.6.1**
  - 43 of 60 = 72 % and 8 of 60 = 13 % (Clopper–Pearson about 6–25 %) match.
  - Random participation: 1 of 60 both reject, 3 of 60 either. Matches.
  - M = 1 rejects under the uniform null only, 60 of 60. Matches.
  - Common 1–2 % shortfall: ratios 0.981–0.990 across seven points. Matches.
- **§1.6.2**
  - 0.503 and 0.753 against the closed form's 0.500 and 0.758 match; 0.65 matches.
  - "Up to 10 % high at M = 2–16" (7–10 %) matches; c = 0.376 matches.
  - "0.03 high at n̄ = 0.4" matches, using c(33, 7) = 0.321.
  - 0.48 ± 0.06 and 0.14 ± 0.02 match; local-search constant 0.50 matches; 33 of 33 (goal page) matches; 0.28 = 9/32 matches.
  - Table 1.3: all 48 entries match the "exact 5 %" rows of `order_power.txt`. The 0.52–0.73 rerun against the recorded 0.43 matches.
- **§1.7**
  - Floors 0.44 and 0.59 s; range 0.26–0.76 s; 2.48–5.8σ. All match.
  - 28,800 pairs, 4 of 576 points at p < 0.01, 400 pairs per point, 2.5 w half-plateau, 3.8 s 5th percentile. All match.
- **§1.9.3**: eleven roles over four rounds matches the 2026-10-23 run record.
- **Literature attributions spot-checked** (see "How I checked"): all match their sources.

## What I would need before signing off
1. Redraw Fig. 1.11 from the held-out record, or from both records, and correct the "resolved 0.2 s" wording in §1.8 and the Fig. 1.1 title (finding 1).
2. Make Table 1.2's off-curve counts complete (finding 2).
3. Fix the factual slips in findings 3–11.
