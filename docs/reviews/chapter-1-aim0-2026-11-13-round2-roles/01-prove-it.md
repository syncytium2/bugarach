GRANT 1 MISMATCH — missing none; holds Edit, Write, PowerShell, Agent, Artifact, Skill, ToolSearch, mcp__claude_ai_Claude_Docs__batch, mcp__claude_ai_Claude_Docs__update (write-capable), with NotebookEdit and other write-capable MCP tools reachable through ToolSearch

The mismatch is a fact about how this run was set up, not about the chapter. No editing tool was used. Every file I wrote is under <scratch>/mb2/role01/ (cfar_check.py, its .out, and pdftotext extracts of the cited papers). The run record's `roles:` line has to say that role 1 took a fallback path.

**Artifact.** docs/dissertation/chapter-1-aim0.md, blob 0acfccbb (I re-hashed it and it matches). I opened Figures 1.2 and 1.3 as images. I did not read anything under docs/reviews/.

## Findings (location · issue · severity · suggested fix · verified against a source?)

1. **§1.3.1, §1.4 "Realistic values", §1.6.1, §1.8.2 "Power", §1.10 · Every "realistic" count pools four experimental groups and treats recordings as independent, but the chapter never says so.**
   - The record of unit membership exists: <repo>/docs/learned/runs/2026-09-25-real-intervals/windows.csv has a `group` column, and tools/measure_coordination_rates.py resamples by mouse ("66 recordings come from fewer mice"). DeFazio et al. 2026 allows up to 3 slices per mouse.
   - Recomputed by group, fast stream, events per segment (median / mean / segments with none):
     - DI: 5 / 6.8 / 1 of 17
     - MALE: 3 / 4.9 / 2 of 13
     - OVX: 0 / 1.1 / 12 of 17
     - ORX: 0 / 0.7 / 13 of 19
   - Slow stream: DI median 10, MALE 5, OVX 0, ORX 0.
   - So "a median segment of one or two events" is a pooled number. It mixes groups whose segments mostly hold no events with groups whose median is 5–10. The chapter uses it to set the event range for the order-power analysis ("1–5 events", §1.8.2), the readability verdicts in §1.5.7 and §1.10, and the "lab's 10–22 per hour" against the design's 90 per hour in §1.2.4. By group the per-hour rate runs 2.1–48.5.
   - The words "group", "mouse" and "DI/OVX/MALE/ORX" do not appear in the chapter. Recording counts (66, 28 of 66, 25 of 66) are presented as independent units.
   - Severity: **high** for the framing; the derivations are untouched.
   - Fix: state that the realistic counts pool four groups and are not independent by mouse. Give the per-group medians, or justify pooling.
   - Verified: yes.

2. **§1.7, first sentence · "Situation 3 of Figure 1.2 showed two events 3 s apart".** The design places them at 81 s and 85 s (ch1_intro_figures.py, DET), and §1.2 and Figure 1.2 say 4 s. Severity: medium. Fix: change to 4 s. Verified: yes.

3. **§1.8.1 "Detection" · Headline rate contradicts the chapter's own larger run.**
   - The chapter says 13 % at reuse 0.045 (8 of 60, from membership_limit.json).
   - The 1,000-recording follow-up (membership_repeat.txt) gives a both-null rejection of **0.094 [0.077, 0.114]** at 200 surrogates and 0.092 at 1,000. That interval excludes 13 %.
   - The paragraph's own decomposition gives the same thing: 0.62 × 0.14 + 0.38 × 0.018 ≈ 0.094.
   - Severity: medium. Fix: quote about 9 % (n = 1000), or report both. Verified: yes.

4. **§1.4 "How the predictions are tested" · "on that path the participant residuals change by at most 0.004" is false.**
   - In pooled_path.txt, the median |residual| for participants moves from per-recording to shipped by:
     - first run at 0.05 Hz: 0.0161→0.0210 (hard-core) and 0.0146→0.0227 (general)
     - held-out at 0.05 Hz: 0.0209→0.0170
   - The largest change is 0.008. "The rate bias is smaller" also does not hold everywhere: held-out hard-core signed rate bias grows 0.0165→0.0176 at 0.01 Hz and 0.0247→0.0322 at 0.05 Hz.
   - Severity: low–medium. Fix: say "by at most 0.008", and qualify the rate claim. Verified: yes.

5. **§1.5.7, closing paragraph · Effect of assuming a 20 s hard core: "slow-stream jitter by at most 0.03" holds only at the pooled rates.**
   - In 20-minute segments (window_counts.txt, true vs page form), slow jitter changes by up to 0.10:
     - slow 7 cells: 0.87→0.77 at E=8, 1.04→0.95 at E=1, 0.87→0.78 at E=2
     - slow 13 cells: 0.93→0.87 at E=8
   - Fast 7 cells at E=1 also changes rate by 0.04 (1.67→1.71).
   - The sentence explicitly covers "up to eight events per window".
   - Severity: low–medium (jitter is unreadable there anyway). Fix: restrict the claim to the pooled rates, or give the segment figures. Verified: yes.

6. **§1.2.4, item 4 · "four of the five false alarms fall within 13 s of its ends" is not printed by any listed script.** The chapter claims every number is printed by a listed script; the log has no such line. I recomputed it over seeds 1000–1199 with the script's own functions: CFAR false alarms fall at 125.6, 130.9, 131.2, 143.2 and 167.3 s, so 4 of 5 is correct. Severity: low (provenance). Fix: add a print line to ch1_intro_figures.py. Verified: yes, by recomputation only.

7. **§1.2.4, item 4 · "CFAR raises its threshold to 10–12 cells in that stretch" describes only the draw shown.** The log's `[10, 11, 12]` is for seed 1015. Over 200 draws the busier-stretch threshold runs from a minimum of 9–11 to a maximum of 11–14. Severity: low. Fix: say "10–12 in the draw shown (9–14 over the 200)". Verified: yes, by recomputation.

8. **§1.6.2, third bullet · "0.01 Hz with K = 3 (chance share about 0.4)".** assessor_jitter.txt gives a pooled predicted share of 0.32 and measured 0.26–0.29; per condition it runs 0.15–0.48. Severity: low. Fix: "about 0.3 (0.2–0.4 by condition)". Verified: yes.

9. **§1.5.7, Table 1.5 text · "The tool's participant estimate sits at 0.90–0.95 of planted throughout".** At E = 1–2 the 1 s estimate reads 0.88 (fast, 7 cells, E=1), 0.97–0.98 (slow, 7 cells, E=1–2) and 0.92–0.95 (13 cells). Severity: low. Fix: "0.88–0.98, near 0.92 from four events". Verified: yes.

10. **"Reproducing" list · ch1_intro_figures.py is labeled "Figures 1.1–1.3".** It produces Figures 1.1, 1.2 and 1.4. Figure 1.3 (data-and-what-each-tool-sees) comes from ch1_new_figures.py, `fig_data`. The task brief repeats the same attribution. Severity: low. Fix: relabel as "Figures 1.1, 1.2, 1.4". Verified: yes.

11. **§1.3.1 · The realistic parameter values have no cited source in the chapter.** I traced them myself:
    - σ 0.105 and 0.131 s: GLOSSARY, from runs/2026-09-23-jitter-by-group-66, i.e. the correlogram tool with its simulated calibration, pooled over 66 recordings.
    - b 0.0096 Hz: generator.md.
    - 7 and 13 of 33 cells: only the goal page ("about 7 of 33").
    - The jitter values come from the correlogram tool, which the chapter says "was not tested at those values" (§1.4).
    - The lab's recordings hold 14–61 cells (median 32); the chapter uses 33 throughout. The newer stream_profile uses 32, as the goal page notes.
    - Severity: low–medium. Fix: cite the run records, and note that σ itself is a correlogram-tool reading. Verified: partly; I found no source for 7 and 13.

12. **§1.3.3 · The ±5 s shifts losing 35 % of planted pairs, and "64 s at the 1 s window".**
    - The 35 % figure exists only as a docstring in tools/measure_coordination_rates.py, `shifted`. No run record holds it. Unverifiable.
    - "About N × 2w (64 s)": N × 2w is 66 s; the 64 s is the (N−1) × 2w span.
    - Severity: low. Fix: cite or drop the 35 %; write "(N − 1) × 2w". Verified: no for the 35 %; yes for the arithmetic.

13. **§1.6.1, "Real backgrounds are not flat" · "the generator's fitted per-cell burstiness" is weaker than the real recordings.** chance_bursty.txt shows the simulated variance/mean at 30/60/120/300 s is 1.50/2.02/2.29/3.53, against the real 1.81/2.60/3.87/5.68. The "does not change" result was measured on a less over-dispersed background than the lab's. Severity: low. Fix: state the gap. Verified: yes.

## Claim ledger: values that matched

Format: quoted value · source · recomputed or read value.

**§1.1–1.3, from the log and my recomputation**
- Figure 1.1: 190 background and 40 event onsets, 4 × 10 cells, 120 s, b 0.05 Hz, σ 0.2 s · log and script · match.
- Table 1.1, every cell (shares 1.00/0.34/0.00/1.00/0.41 and the others; 1.82, 3.58, 0.03 per min; 364, 717, 5 in 200 min; 1, 5, 0 in 10 h) · log · match.
- Situation 2: CFAR at 7 or 8 cells in 196 of 200 · log (74 + 122) · match.
- Situation 4: chance hits 0.21 and 0.34 · log · match. 0.03 per min = 1.5 per hour (5 / 200 min) · match.
- Situation 5: 66 %, 41 %, 49 %; threshold 6 in 119 draws and ≥ 7 in 67 (63 + 4) · log · match.
- Merge gap 0.5 s gives 1.00 for all three detectors · log · match.
- 7 of 200 draws typical; seed 1015 · log · match.
- CFAR median background estimate 0.0208 Hz, about twice the true rate · log · match.
- 90 per hour (6 events in 4 min) · match.
- Chance floor 6 at 0.0096 Hz, 12 at 0.05 Hz, 4 at a 0.2 s window · log, plus my recompute (0.33, 0.49 and 0.038 per hour at the floor) · match.
- Repository's simulated floor 6 and 12 · blind_a/REPORT.md and split_output.txt · match.
- Event 2 sits on a bin border (45.95 s rounds across 46 s); events 1, 3a, 3b, 4 and 5 sit mid-bin · script · match.
- Correlogram:
  - level 0.887 / 0.884 predicted against 0.891 / 0.881 measured · match
  - peak 18.4 vs 18.3 and 4.6 vs 4.6 · match
  - HWHM 0.174 vs 0.177 (SE 0.003) and 0.835 vs 0.821 (SE 0.021); 0.167 s · match
  - 2√ln2 = 1.665 · match
  - "within about one SE" · 1.0 and 0.67 SE · match
- g₂ sharp 0.49 / 0.89 (measured 0.48 / 0.87); jittered 0.11 / 0.49 (measured 0.10 / 0.47) · log · match.
- Shares within about 0.02 of the full prediction · largest gap 0.021 (jittered, 8 s) · match.
- g₂ = ½ at 2.08 σ · my recompute 2.079 · match.
- Bin-count chance share 7.79e-10 ("8 × 10⁻¹⁰"); 397/450, 119/450, 450/450, 442/450 · log · match.
- DeFazio et al. 2026: 10 Hz imaging (0.1 s frame) and fast/slow events · paper · match.
- Per-segment counts: fast mean 3.21, median 1, range 0–23, 28 of 66 with none; slow 7.29, median 2, range 0–49, 25 with none; 9.7 and 22.0 per hour; segments 17–20 min · windows.csv, summary.json · match.

**§1.4–1.5**
- σ = 1 s participants: 0.34–0.42 (1 s window) and 0.68–0.85 (4 s window) · aim1_one_source.json, recomputed 0.343–0.422 and 0.678–0.852 · match.
- 7.97 and 3.85 per min · theory_check.json · match.
- Participant residuals 0.007 / 0.016 (worst 0.037 / 0.106); held-out 0.012 / 0.021 (worst 0.056 / 0.132) · summaries · match.
- 24 of 32 conditions, p = 0.007 · my binomial recompute 0.0070 · match.
- 7 and 10, then 17 and 10, beyond 2 SE; null 0.118 × 48 = 5.7; normal 2.2 · match.
- p 0.0005–0.002 · dependence_null (MVN 0.0005, bootstrap 0.0022) · match.
- Rate residuals 0.032 (held-out 0.024); 0.055 (worst 0.38; held-out worst 0.62); share 0.018 (held-out 0.011) · match.
- Refusals 17 and 25 · match.
- General form:
  - 18 of 32, p 0.60 · match
  - 12 beyond 2 SE, p 0.03–0.07 · match
  - 0.032→0.020, 0.024→0.014, +0.030→+0.013→+0.005 · match
  - 35 of 48, p 0.01–0.04; held-out 18 of 48 · match
  - 0.055→0.059 · match
- Dense trains:
  - fast stream: hard-core predicts 1.16 / 0.90, tool measures 0.99 / 0.97; general form within 0.040 · match
  - slow stream: tool 1.37 / 0.80, general form 1.31 / 0.82; Figure 1.10 miss 0.17 · match
- Pooled-rate trains: 7.28 events (range 2–19) and 16.46 (2–35) · match. Slow-stream misses 0.010–0.079 and 0.005–0.023 · match. 1.160 vs 1.081 and 0.909 vs 0.932 · match.
  - "Up to 3.3 SE": the rounded SEs in the table give about 3.0. Close; unrounded SEs were not available.
- Joint fit, both runs: 0.91–1.13, 0.88–1.12, 0.94–1.14, 0.73–1.14; held-out 0.86–1.22, 0.86–1.36, 0.98–1.06, 0.89–1.16, 0.94–1.04, 0.87–1.45 · match.
- 0.041 s with 3 at the bound, 0.030 s with 7; 5-cell 0.1–3.7 and 3.6 · match.
- Table 1.3, all eight rows · correlogram_table.txt · match.
- Table 1.4 and the Figure 1.11 C band counts (4/2, 8/8, 17/18, 16/16) · realistic_counts.txt · match.
- Table 1.5, all joint-fit cells and the tool's cells I checked · window_counts.txt · match.
- Poisson-train assumption gives 0.55–0.62, 0.91–0.93, 1.08–1.11; hard-core assumption gives 1.62 / 1.43 and 1.32–1.45 · match.
- k̂/k: 0.45 at σ = w, and below 0.9 from σ/w = 0.177 ("about w/6") · my recompute with theory.g · match.

**§1.6**
- 0.256 / 0.019 predicted vs 0.262 / 0.020 measured; 7.97 / 3.86 / 0.284 vs 7.97 / 3.85 / 0.279 · theory_check.json · match.
- 0.98 per hour at K = 4 and 0.0096 Hz; first K under budget is 5 at 0.01 Hz and 8 at 0.05 Hz · my recompute · match.
- K = 4 crossing at b = 0.00964 · chance_bursty.txt · match. 0.2 clusters expected at K = 6, 0.01 Hz · match.
- 0.99 and 0.79 per hour · chance_bursty.txt · match.
- Table 1.6, all 20 cells; shares 0.89–0.96, 0.79–0.92, 0.02–0.05 · my recompute · match.
- 85–93 %; within 0.006 s and 0.015 s; ceiling 0.743 · match.
- −0.02 / −0.04 / −0.03 / +0.036 s; 0.28–0.29 vs 0.34; 0.58–0.62 vs 0.74 · match.
- Null readings 0.727 / 0.671 / 0.595 (within 0.01 s); excess moves 0.02–0.04 s · assessor_null.txt · match.

**§1.7**
- 0.44 and 0.59 s; range 0.26–0.76 s (2.5–5.8 σ); labelled-onset test 0.12–0.22 s · bound_output.txt · match.
- 28,800 pairs; 4 of 576 points at p < 0.01 · split_output.txt and derivation · match.
- Interval shares: 5th percentile 3.79 s; 1.7 % under 3 s; 7.5 % under 5 s (fast) and 0.9 % (slow) · gaps.csv · match.

**§1.8**
- Membership: 72 % (43 of 60); 62 %; 14 % / 26 % / 2 %; 1 of 60 and 3 of 60; 1–2 % shortfall; ratio 1.044 · match.
- Order:
  - F = 0.48 ± 0.06 and 0.14 ± 0.02 · match
  - score sort 0.503 / 0.753 · match
  - c = 0.376; C = 0.65 · my recompute · match
  - template asymptote up to 10 % high · 1.07–1.10 · match
  - Table 1.7, all cells · order_power.txt, exact rows · match
  - 0.06→0.66, 0.18→0.73, 0.69→0.92; −0.178; tie-corrected mean within 0.004; 5.2 %; tied pairs 21–26 % and 8–10 % · match
  - F_Kreuz = 9/32 ≈ 0.28 · match

**Attributions opened in <01-lit> (text extracted)**
- Finn & Johnson 1968: threshold from the surrounding resolution cells, excluding the cell under test; target-pair resolution · match.
- Rohling 1983: two guard cells; masking in Fig. 3; clutter edges · match.
- DeFazio 2026: 10 Hz imaging; fast and slow events; up to 3 slices per mouse · match.
- Kish 1995: the PDF has no text layer (12 words extracted), so pp. 63–64 and "synthetic but useful" are **unverifiable**.

**Not checked, for scope:** the remaining prior-work attributions (Grün, Louis, Müller, Wu, Staude, Kreuz, Tomlinson, Silva, Shah & Wainwright, Thomas 1949, Kruskal); every row of Table 1.9; and the claim in "Revision" that no number from the earlier version changed (no earlier version consulted).

unreached: 1 (Kish 1995 text — the PDF has no extractable text)
