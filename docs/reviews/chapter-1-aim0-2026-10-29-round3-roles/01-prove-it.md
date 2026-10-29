GRANT 1 MISMATCH — missing none; holds Edit, Write, PowerShell, Agent, Artifact, Skill, ToolSearch, MCP Claude Docs batch/update/guide (plus NotebookEdit, ArtifactData and other deferred tools). The forbidden editing tools were present, but I did not use them. I wrote nothing to the repository or to 01-lit; my only intermediates are under my scratch folder (`mb/work-r3-1/`).

# Role 1, "Prove It": claim ledger for `docs/dissertation/chapter-1-aim0.md` (hash a4fbb30e…)

**Sign-off position:** I would not sign yet. Almost every number is quoted faithfully from its printout, and I recomputed many of them. But the chapter's "realistic recording" does not match the record of the real recordings. The lab's baseline windows (`docs/learned/runs/2026-09-25-real-intervals/windows.csv`) last 20 minutes. The chapter's "realistic counts" come from 45-minute simulated recordings. That makes its realistic-value conclusions describe about 2.25 times the events a real window holds. The chapter also states two contradictory event-count ranges for a realistic recording (1–8 and 7–16). One quoted standard-error range also understates a residual that the chapter itself calls unexplained.

## How I checked
- I ran `theory.py --from-record` with the repository's `.venv`. Plain `python` lacks numpy, so the context file's command fails as written.
- I read every `ch1_followups/*.txt` printout in full: held-out, like-for-like, correlogram ×2, realistic counts, lab values, assessor jitter, order power, order rounding.
- I also read `membership_limit.json`, `order_limit.json`, `kendall_w/derivation.md`, `separation/floor/derivation.md` and `separation/assessor_split/derivation.md`.
- I opened the record of the real recordings the chapter never cites: `runs/2026-09-25-real-intervals/windows.csv` and its README.
- I recomputed the following myself rather than reading them off a printout:
  - g_n and k̂/k, using theory.py's functions plus a uniform-jitter Monte Carlo.
  - The chance-cluster budget at 0.0096 Hz.
  - Two sign-test p values.
  - The z-scores for the slow-stream misses, from `realistic_counts.json`.
  - Per-k joint-fit resolution on both records.
  - The truncated-Gaussian ceiling.
  - Kish's design-effect form, from the rendered scan (p. 63).
  - Quotes and section numbers in Kreuz 2017 and Kruskal 1958.

## Findings

| # | location | issue | severity | suggested fix | verified against source |
|---|---|---|---|---|---|
| 1 | §1.5.1 "against the 7–16 coordinated events a realistic recording holds"; §1.8.1 "Participants can be read from one recording at 7–16 events"; §1.4.6 "At realistic values and realistic event counts"; §1.3 "40 recordings of 45 minutes … held 7.3 events on average … 16.5" | **The "realistic recording" is not the lab's recording unit.** `windows.csv` (66 baseline windows per stream) has windows of median 0.333 h (0.283–0.333 h), i.e. 20 minutes. Mean events per window are 3.21 (fast) and 7.29 (slow). The simulations put the tabulated hourly rates (9.7 and 22.0 per hour) into 45-minute recordings, which gives 7.3 and 16.5 events, about 2.25 times a real window. So the realistic-count verdicts describe roughly twice the events a real window offers: the joint fit reads participants in 35–40 of 40 recordings, and rate with 13 cells. §1.5.1 and §1.8.1 also contradict §1.2.1 and §1.7.2, which say a real window holds 1–8 events. | major | Either rerun `realistic_counts.py` at T = 1200 s (3.2 and 7.3 events), or say plainly that the realistic recordings are 45 min long, which is 2.25 times a lab baseline window. Reconcile "7–16" with "1–8" in one place. | yes |
| 2 | §1.2.1 "1–8 coordinated events per recording window (medians 1, 2 and 3…)"; §1.7.2 "a realistic recording window holds 1–8" | The medians are correct (1, 2, 3), but 1–8 is not the range. Fast: 42 % of windows hold **0** events, the 75th and 90th percentiles are 4 and 9, and the maximum is 23. Slow: 38 % hold 0, the 90th percentile is 27.5, and the maximum is 49. 11 % (fast) and 24 % (slow) of windows hold more than 8. The figure comes from the goal page's "about 1–8", and the chapter drops the "about". It is the stated basis for testing order power only at 1–5 events. | major | Quote the distribution (median, IQR, share with zero events) from `windows.csv` and cite that file. | yes |
| 3 | §1.4.5 "Each miss is small (… 1.3–2.6 standard errors)" | Recomputed from `realistic_counts.json` (pooled value against `pooled_se`): the slow-stream misses reach \|z\| = 2.84 against the hard-core form (participants, 13 cells, 4 s window). Against the general form they span 1.27–3.26: rate is 3.26 SE at 13 cells, 2 s window and 2.79 SE at 13 cells, 4 s window, and participants reach 2.82. The quoted range understates the evidence against the theory on the slow stream. | major | State "1.3–2.8 SE (hard-core form), up to 3.3 (general form)", or name the form the range refers to. | yes |
| 4 | §1.4.4 "not the 2.4 a normal error would give" | 48 × P(\|Z\| > 2) = 48 × 0.0455 = 2.2. The 2.4 is 48 × 0.05, the 1.96 rule, which conflicts with the "beyond 2 standard errors" criterion used throughout. No source prints 2.4. | minor | Change to 2.2. | yes (recomputed) |
| 5 | §1.3 "An earlier run at about 3.7 and 3.2 times those rates (25.5 and 53.6 events per recording)" | 25.5 ÷ 7.3 = 3.5, not 3.7. The 3.7 is 35.8/h ÷ 9.7/h, the train's natural rate 1/mean gap, but the planted count was 25.5 (0.00944 Hz, 34.0/h). The slow figure of 3.2 matches either way (53.6 ÷ 16.5 = 3.26; 70.1 ÷ 22.0 = 3.19). | minor | Change to "about 3.5 and 3.3 times". | yes |
| 6 | §1.3 "on these records that gap is about 0.1 % of k" | No printout or README states this. I found no record of the plug-in versus median-of-estimator gap. | minor | Cite the script or printout that measured it, or drop the number. | no (unverifiable) |
| 7 | §1.3 "The tool refused … in 17 of 720 … the medians exclude those." | The number is correct (from-record: 17 of 720, all 5-cell events at 0.05 Hz). But the goal page adds that "the prediction cannot [exclude them], so those medians carry a selection bias", and the chapter drops that caveat. The held-out record refused in **25** of 720, which the chapter does not report. | minor | Restore the selection-bias sentence and give the held-out count of 25. | yes |
| 8 | Table 1.2 joint-fit column vs theory.py's printout | Table 1.2 uses the median over 20 recordings (0.01 Hz, 0.05 s → 1.33; 0.05 Hz, 0.05 s → 0.89). The from-record print and the §1.4.6 text use the median of 4 condition medians (0.075 s → 1.50; 0.039 s → 0.78). Both follow their own scripts, but a reader cross-checking the table against `theory.py --from-record` finds disagreement with no stated reason. | minor | Add one clause to the Table 1.2 caption saying it pools recordings, unlike the condition medians quoted in the text. | yes |
| 9 | §1.4.6 "Events of 5 cells read anywhere from 0.1 to 3.6 times planted" | That is the first experiment (0.10–3.56). The held-out record, which §1.3 says is "the one to trust", reads 0.10–3.71. | minor | Change to "0.1 to 3.7 (held-out)", or label the record. | yes |
| 10 | §1.4.5 "the general form predicts the tool to within 0.01–0.04 at every window" | Recomputed from `lab_values.txt`: the general-form differences run 0.000–0.040. A lower bound of 0.01 is wrong. | minor | Change to "within 0.04". | yes |
| 11 | §1.4.6 "jitter on the slow stream is unchanged" (20 s hard core assumed) | Medians go 1.00 → 0.97 (7 cells) and 0.97 → 0.95 (13 cells), and in-band counts go 18 → 17 and 16 → 16. Close, but not unchanged. | minor | Change to "changes by at most 0.03". | yes |
| 12 | Fig. 1.4 caption "On both records only the 20-cell row is resolved from 0.2 s up" | True as worded. But the 10-cell row is resolved from 0.5 s on both records and at 0.2 s on the first. The 5-cell, 0.5 s point is resolved on the first record only. The sentence reads as if 10-cell events are never resolved. | minor | Add "and the 10-cell row from 0.5 s". | yes |

## Claims verified to match (recomputed or matched exactly to their source)
- **§1.1**
  - The 1 s window reads 0.34–0.42 of planted participants, the 4 s window 0.68–0.85.
  - Assessor jitter at 0.01 Hz, K = 4 reads 0.07/0.23/0.49/0.72 s. At 0.05 Hz it reads 0.64–0.73 s, and 0.43–0.68 s at K = 6.
  - Chance clusters: 7.97 and 3.85 per minute measured.
  - Intro: median 1–2 %, worst 13 % (held-out 0.13).
- **§1.4.2** (recomputed)
  - Gaussian and uniform g₂/g₃ differ by at most 0.020/0.035.
  - k̂/k for 10-cell events falls below 0.9 at σ ≈ w/5.5 ("about w/6") and is 0.450 at σ = w.
- **§1.4.4**
  - Residuals 0.007/0.016 (worst 0.037/0.11), Poisson version about 0.05.
  - Held-out 0.012/0.021 (worst 0.056/0.13).
  - Beyond 2 SE: 7/10 first experiment, 17/10 held-out; about 6 expected (0.118 × 48 = 5.7).
  - 24 of 32 measured below predicted, p = 0.007 (recomputed two-sided).
  - Rate 0.032/0.024 and 0.055 (worst 0.38; held-out worst 0.62).
  - Coordinated onset rate 0.018/0.011 (0.0175 in `like_for_like.txt`).
- **§1.4.5**
  - 18 of 32, p = 0.60 (recomputed); 12 beyond 2 SE, p = 0.009.
  - Rate 0.032 → 0.020, held-out 0.024 → 0.014, bias +0.030 → +0.013.
  - 35 of 48 (p = 0.002), 18 of 48 (p = 0.11), 0.055 → 0.059.
  - Dense trains: 1.16/0.90 against 0.99/0.97; 1.37/0.80 against 1.31/0.82.
  - Realistic counts: the two forms agree within 0.025 everywhere and 0.01 at 1 and 2 s.
  - Fast stream within 1.5 SE: maximum 1.51.
  - Slow stream misses in 6 of 6 cases (rate 0.010–0.079, participants 0.005–0.024); largest is 1.160 vs 1.081 and 0.909 vs 0.932.
- **§1.4.6**
  - Joint-fit ranges on both records match exactly (0.91–1.13 … 0.87–1.45).
  - Planted 0.05 s reads 0.041 s (3 of 20 at the bound) and 0.030 s (7 of 20).
  - Table 1.2: all 32 cells match `correlogram_table.txt`.
  - Realistic-values table: all 16 cells match `realistic_counts.txt` ("true" form).
  - Unknown-train paragraph (0.23/0.80; Poisson 0.55–0.62, 11/9, 0.91–0.93, 1.08–1.11; dense 1.62/1.43) matches.
- **§1.5.1**
  - Predicted and measured rates for all six arms match.
  - Budget: K = 5 (0.07/h), K = 8 (0.53/h), and K = 4 at 0.0096 Hz giving 0.983/h (recomputed).
  - Event floor 6/12; recall 0.76–0.80 and 0.29–0.33.
- **§1.5.2**
  - Shares 0.89–0.96, 0.79–0.92, 0.02–0.05.
  - Chance-cluster SDs 0.73/0.68/0.60/0.38 s.
  - Table 1.3: all 16 cells match.
  - "Within 0.015 s", "within 0.006 s", 85–93 %, 0.28–0.29 vs 0.34, 0.58–0.62 vs 0.74.
  - Ceiling 0.743 s (recomputed truncated-Gaussian SD).
- **§1.6**
  - Separations 0.44/0.59 s, range 0.26–0.76 s (2.48–5.80 σ, recomputed).
  - g of 0.4 and 3.2 s.
  - 28,800 pairs and 4 of 576 points.
  - Gaps: 1.7 % under 3 s, about 98 % resolved, 7 %/1 % merged, 5th percentiles 3.8 and 7.1 s.
- **§1.7.1**
  - Reuse 0.045 gives about one shared pair (990/1000).
  - Rejections 1 of 60 / 3 of 60, 43 of 60 = 72 %, 8 of 60 = 13 % (Clopper–Pearson interval about 6–25 %).
  - Variance ratio 1.044 predicted (1.032 measured); 1–2 % common shortfall.
  - Kish's roh = (deft² − 1)/(n/a − 1) is on p. 63 of the scan.
- **§1.7.2**
  - 0.503/0.753; 0.65 (recomputed); up to 9.8 % high at M ≤ 16.
  - c = 0.376 (recomputed); +0.031 at n̄ = 0.4; 33 comparisons.
  - 0.48 ± 0.06 and 0.14 ± 0.02.
  - Table 1.4: all 48 entries match the "exact 5 %" rows.
  - Rounding: 5.2 % (SE 0.08 %), 19.6 % ties, 1.3 %, 0.91 → 0.99, 26 %/10 %.
  - F_Kreuz factor 9/32 = 0.28.
- **§1.2.1**
  - 0.0096 Hz comes from the fast stream (`generator.md`).
  - σ of 0.105/0.131 s (GLOSSARY).
  - Middle participation levels 0.203/0.375 (`bench.py`, `bench_slow.py`).
  - 9.7 and 22.0 events per hour (real-intervals README).
- **Literature spot checks**
  - The Kreuz 2017 quote is verbatim and in §3.1; the binomial-null discussion is near §2.5.
  - Kruskal 1958 §4 derives τ = (2/π) arcsin ρ from the quadrant relation via Cramér.
  - Louis 2010 Fig. 6 matches its use ("disentangle as their sizes converge").
  - Grün 1999 Eq. 5 is the fission probability.
  - The Silva 2015 and Tomlinson 2019 uses match the 01-lit README.
- **About this chapter:** "four rounds" for the record's review matches `docs/reviews/synthetic-validation-aim0_2026-10-23.md`.

## Sources the chapter did not consult
The record of the real recordings (`runs/2026-09-25-real-intervals/windows.csv`, its README and `gaps.csv`) is where every "realistic" quantity originates. The chapter cites only the goal page's summary of it. Opening the record produced findings 1 and 2. Exclusions were applied upstream: the dataset stamp reads "…STEPS_AND_PINS_EXCLUDED", and only baseline windows are used. Per-group differences (DI/OVX/MALE/ORX) are pooled into the hourly rates. That is acceptable because the chapter uses those values only to choose where to simulate.

## Not checked or residual
- The CuBIC eq. 3 citation.
- The claim that Thomas 1949 gives no scatter law.
- The oracle range of 0.07–0.2 s: the table spans 0.07–0.18 s including 20-cell events, and only 0.12–0.18 s at the four realistic combinations.
- The figures' internal labels (role 10's surface).
