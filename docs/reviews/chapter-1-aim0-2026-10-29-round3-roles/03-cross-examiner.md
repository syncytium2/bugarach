GRANT 3 MISMATCH — missing none; holds Edit, Write, Bash, PowerShell, Agent, Artifact, Skill, ToolSearch, mcp__claude_ai_Claude_Docs__batch, mcp__claude_ai_Claude_Docs__update (NotebookEdit also reachable through ToolSearch)

This is a finding about the run, not about the chapter: the harness gave this reviewer editing and shell tools that role 3 may not hold. I used only Read, Grep and Glob. I edited nothing and wrote no scratch files. Because I kept to that grant, I did **not** run `theory.py --from-record`. Every number below was checked by hand against the printed `.txt`/`.json` records and the rendered PNGs.

# Role 3 — Cross-Examiner: Chapter 1 (Aim 0), blind verify round 3

**Artifact:** `docs/dissertation/chapter-1-aim0.md`. I read all of it (1,135 lines). I opened 12 of the 14 figures; Figures 1.6 and 1.11 were not opened.

**Canonical counting basis I pinned:**
- events per **45-min simulated recording**, for the simulations;
- events per **20-min real baseline window**, for the lab data (`docs/learned/runs/2026-09-25-real-intervals/windows.csv`).

## Findings

| # | location | issue | severity | suggested fix | verified against a source |
|---|---|---|---|---|---|
| 1 | §1.2.1 "1–8 coordinated events per recording window (medians 1, 2 and 3…)"; §1.5.1 "against the 7–16 coordinated events a realistic recording holds"; §1.7.2 "a realistic recording window holds 1–8"; §1.8.1 "at 7–16 events"; §1.8.3 "more events than a realistic recording window often holds" | **One population is counted on two bases, and the stated range does not match its own source.** (a) "Recording window" is never defined. In the source it is a **20-min baseline window**: 66 windows, 21.8 h, `hours` = 0.333 in `windows.csv`. The simulations are **45-min recordings**, about 2.3 windows, holding 7.3 and 16.5 events on average. The chapter switches between "a realistic recording" (7–16) and "a realistic recording window" (1–8) without saying they differ in length. (b) "1–8" is not the range. `windows.csv` has many windows with 0 events (fast: 212 events − 174 gaps = 38 windows with any event, of 66). It also has windows holding up to 23 (fast), 49 (slow) and 52 (combined) events. The mean per window is 3.2 fast and 7.3 slow, so "1–8" cannot be a range for slow. The goal page itself says "about 1–8". (c) The 1–5-event power design in §1.7.2, and the conclusions in §1.8.1 and §1.8.3, rest on this number. (d) GLOSSARY "intervals/frequency" asks writers to quote the median interval (41.3 s fast, 25.1 s slow) and say where a frequency came from. §1.2.1 quotes 9.7 and 22.0 per hour without that, next to an interval list whose 1/mean gap is about 3.7× higher. | major | Define "recording window" once (20-min baseline window) and state the 45-min ↔ 20-min relation. Replace "1–8" with the actual distribution (share with 0 events, median, upper percentiles). Say that the 1–5-event power grid covers the typical window, not the busy tail. Write "7.3–16.5" rather than "7–16". | yes |
| 2 | §1.2.2 "Four population-count tools are analyzed. Each sees only how many onsets or cells fall in a window or bin, never which cells they are", then "The correlogram tool estimates jitter without bins, from … the cross-cell onset correlogram" | **Internal contradiction, plus a reserved-term mismatch.** The correlogram tool uses no bins and works on cross-cell pairs, so it needs cell identity (same cell or different). GLOSSARY "population-count tool" names exactly **three**: the coordination-rates tool, the assessor and the count detector. | major | Say "three population-count tools plus the correlogram tool", or widen the glossary entry in the same change. | yes |
| 3 | §1.3 "An earlier run at about 3.7 and 3.2 times those rates (25.5 and 53.6 events per recording)" | The arithmetic does not hold within the sentence: 25.5 / 7.3 = **3.5**. "3.7" is the unthinned 1/mean-gap rate over the tabulated rate (35.8 / 9.7 per hour, from `ch1_followups/README.md`). The 25.5 is the planted count (0.00944 Hz), which is 3.5×. For slow, 53.6 / 16.5 = 3.25. | minor | Write "about 3.5 and 3.3 times (25.5 and 53.6 events)". | yes |
| 4 | §1.4.5 slow-stream paragraph: "Each miss is small (rate 0.010–0.079, participants 0.005–0.024; 1.3–2.6 standard errors), and the largest is … 1.160 measured against 1.081 predicted, participants 0.909 against 0.932" | **Two prediction bases in one paragraph.** The ranges and SE counts are taken against the *nearer* of the two forms: 0.024 and 2.6 SE come from the hard-core form. The "largest" example is quoted against the general form (1.081, 0.932). Against the general form, two rate misses reach about **3 SE**: 13 cells at 2 s, (1.052 − 1.034) / 0.006; and 13 cells at 4 s, (1.107 − 1.077) / 0.010 (`realistic_counts.txt`). | minor | State that misses are measured against the nearer form, or quote everything against the general form (participants 0.005–0.023, up to about 3 SE). | yes |
| 5 | §1.4.4 "not the 2.4 a normal error would give" | 48 × P(\|z\| > 2) = 48 × 0.0455 = **2.2**. The 2.4 is 48 × 0.05, the 1.96-SE rate. The heavy-tail figure, about 6 (0.1183 × 48 = 5.7, `like_for_like.txt`), is correct. | minor | Write "the 2.2". | yes |
| 6 | §1.2.3 "What is missing … the assessor's chance-cluster rate" versus Contribution 4 and Table 1.6 "Known in form" | The chance-cluster rate is called both "missing" and "known in form". | minor | In "What is missing", narrow it to "the assessor's run-start factor and jitter reading". | yes |
| 7 | §1.6 "That within-cell minimum interval, g"; §1.4 g_n; §1.5.2 "c" and "e"; §1.7.1 "e events" (E = Me); §1.7.2 c(N, k); Table 1.5 "N the trains scored"; §1.2.3 "Ripley's K-function"; §1.4.3 p = λw beside p-values and p_m | **Symbols reused for different concepts:**<br>• g: window sharing, and also the within-cell minimum interval<br>• e: events per minute, events per assembly, and Euler's e in e^(−b)<br>• c: chance-cluster rate, and the no-order constant<br>• N: cells, and trains scored<br>• K: threshold, and the K-function<br>Table 1.1 also omits q, c, e, p, π_K and Δ. | minor | Rename the minimum interval (the glossary uses τ "dead time" or *f*). Rename the §1.7.1 e (for example e_a). Write c_chance or a similar label. Write N_scored in Table 1.5. Add the local symbols to Table 1.1. | yes |
| 8 | §1.2.1 "The lists came from a detector with 2 s bins"; §1.6 "the lists were themselves made with 2 s bins" | The source README is titled "measured **without a detector**". It counts ROIs in a 2 s window **sliding at every 0.1 s frame position**, against each window's ADR-0008 floor, and merges events under 2 s apart. The lists do not come from fixed 2 s bins. The lower-bound conclusion still stands. | minor | "came from a 2 s sliding co-activity count, which merged events closer than 2 s". | yes |
| 9 | §1.5.1 "event floor, the smallest count that chance reaches less than once per hour in a 2 s sliding window" | GLOSSARY "event floor" (ADR-0008) defines it as "at most once per hour", the larger of 3 ROIs and that count, under the window's own rigid-shift null (J = 20 s). The chapter says "less than" and omits the 3-ROI minimum and the null. | minor | Match the glossary wording, or cite ADR-0008. | yes |
| 10 | §1.6 "The test that knows each onset's event reaches 0.07–0.2 s" | Basis mismatch. The surrounding sentence is at 80 % power for the four realistic combinations. 0.07 is the **50 %** value at **k = 20** (`separation/floor/derivation.md`). At 80 % for σ 0.105–0.131 s and 7–13 cells, the oracle reaches about 0.12–0.22 s. | minor | Give "0.12–0.22 s" on the same basis. | yes |
| 11 | §1.7.2 "Frame rounding… power rises from 0.91 to 0.99" versus Table 1.4, 13 cells, 3 events, r = 2.5, one template: 0.89 | The same unrounded condition gives two powers: 0.909 from 2,000 recordings at σ 0.105 s, and 0.89 from 300 recordings at σ 0.2 s. Unrounded F depends only on r, so these are one quantity, and the reader is not told why they differ (Monte Carlo noise). | minor | Add "(2,000 recordings; Table 1.4's 0.89 is the same condition from 300)". | yes |
| 12 | §1.4.6 "Events of 5 cells read anywhere from 0.1 to 3.6 times planted" | This follows a sentence about the held-out record, but the held-out maximum is **3.71**: Figure 1.4 shows 0.10–3.71, and `like_for_like.txt` gives 3.71 hard-core. 3.6 is the first experiment's value. | minor | "0.1–3.6 (first experiment; held-out 0.1–3.7)". | yes |
| 13 | §1.5.2 chance-cluster share | Three bases sit side by side without labels: (a) predicted per condition, 0.89–0.96 and 0.79–0.92; (b) "85–93 % of clusters are chance clusters", which is the pooled *measured* share; (c) "predicted 0.34" at K = 6, the pooled mean of the two event counts. | minor | Label each as predicted or measured, and per condition or pooled. | yes |
| 14 | Figure 1.5 caption "for 5, 10 and 20 cells per event. Points are medians…" | The figure draws points only for 10 and 20 cells; its own legend says "10- and 20-cell events". | minor | Add "points: 10 and 20 cells". | yes |
| 15 | Figure 1.1, panels C and G, y-axis "coordinated share of onsets" | §1.2.2 and the GLOSSARY say this is a rate, λk/N, labeled "coordinated share" only as a ratio to planted, and "as a bare quantity it is a rate, not a share". The axis calls it a share of onsets. | minor | Relabel as "coordinated onset rate per cell, recovered ÷ planted". | yes |
| 16 | Figure 1.4 caption "Beside each box is the share of 40 recordings…(Figure 1.8 C)" | Figure 1.8 C shows two forms; the box counts (2 and 16 of 40) are the general form, while the hard-core form gives 4 and 16. The figure legend also has a "held-out record only (right half)" category the caption does not mention. | minor | Add "(general form)" and list the fourth marker state. | yes |
| 17 | Table 1.2 caption "20 per row"; Figure 1.8 "20 recordings per point" | The row for 0.01 Hz and 1.0 s is a median over **5** recordings (15 fell above the curve), and the row for 0.05 Hz and 0.05 s over 5. The censoring is disclosed, but the n is not. | minor | Give n per cell, or "20 minus those off the curve". | yes |
| 18 | §1.4.6 "jitter on the slow stream is unchanged" (when a 20 s hard core is assumed) | The medians move 1.00 → 0.97 and 0.97 → 0.95 (`realistic_counts.txt`). | minor | "changes by at most 0.03". | yes |
| 19 | §1.2.2 surrogates "shifted in time by its own random offset" | `tools/measure_coordination_rates.py` `shifted()` shifts each train **circularly**, with every two cells' offsets **at least two windows apart**. Figure 1.3 says circular; the text says neither. | minor | Add "circularly, with offsets at least two windows apart". | yes |
| 20 | §1.8.4 item 6 "eleven more checked this chapter in three" | The run context describes this pass as the third *blind verify* round. If a review round came first, as in the Aim 0 record (1 review + 3 blind = "four rounds"), the count is four. | minor | Count rounds the same way as for the Aim 0 record. | no (blindness rules forbid opening the chapter's review records) |

## Checked and found consistent

**Experiment counts**
- 4×3×2×2 = 48 conditions; 240 recordings; 720 recording-windows; 160 of 240 for 10+ cells.
- 16 conditions and 48 condition-windows per background; 15 or 45 events in 45 min equals 0.0056 and 0.0167 Hz (λ).

**Chance clusters (§1.5.1–1.5.2)**
- Chance-cluster rates recomputed from the binomial formula: 0.256 and 0.019 per minute at 0.01 Hz; 0.98 per hour at K = 4 and 0.0096 Hz. K = 5 is the first K under budget at 0.01 Hz.
- c/(c + e) ranges; the truncated-Gaussian ceiling, 0.743 s.

**Assessor jitter**
- All 16 cells of Table 1.3 match `assessor_jitter.txt`, as do the §1.1 failure-2 values (0.07–0.72 s).
- §1.5.2 per-K differences (within 0.015, within 0.006, 0.03 low, 0.036 high); 0.58–0.62 against 0.74.

**Participant residuals and sign tests (§1.4.4–1.4.5)**
- 0.007/0.016 (worst 0.037, 0.11) and held-out 0.012/0.021 (worst 0.056, 0.13).
- 7/10/17/10 beyond 2 SE; 24 of 32 (p = 0.007); 18 of 32 (p = 0.60); 12 (p = 0.009).
- Rate residuals 0.032→0.020 and 0.024→0.014; +0.030→+0.013; 35 of 48 and 18 of 48; 0.055→0.059.
- All of these match `like_for_like.txt` and the Figure 1.7 headers.

**Joint fit**
- Ranges on both records; 0.041 and 0.030 s with 3 and 7 at the bound.
- The realistic-values table, every cell, matches `realistic_counts.txt` and Figure 1.8 C (both forms' counts).
- Poisson-train figures; dense-run numbers (1.16/0.90 against 0.99/0.97; 1.37/0.80 against 1.31/0.82; 1.62/1.43).

**Correlogram comparison**
- Table 1.2's below/above counts and medians match Figure 1.8 A–B.
- Figure 1.4's ranges match the §1.4.6 text, and the half-filled 10-cell, 0.2 s marker matches "only the 20-cell row … on both records".

**Order (§1.7.2)**
- Figure 1.3 C worked example recomputed: net scores +3, +5, −3, −5; order 2, 1, 3, 4; 12 co-participations; F = 0.67.
- Figure 1.3 B row and column sums for all three matrices; Figure 1.3 A, 4 onsets against 1.
- c(33, 10) = 0.376; the M-template value 0.65; no-order F of 0.48 and 0.14 against the asymptote; the k = 7 bias of 0.03.
- Table 1.4, all 48 entries, matches the exact-test column in `ch1_followups/README.md` and Figure 1.14.
- Rounding numbers: 5.2 % (SE 0.08 %), 19.6 %, 1.3 %, 26 % / 10 %, 0.91→0.99.

**Membership (§1.7.1)**
- Reuse 0.045, about one sharing pair, ratio 1.04, 8 of 60 (CI about 6–25 %), 72 %, "1–15"; Figure 1.12.

**Separation (§1.6)**
- 0.44 and 0.59 s; 0.26–0.76 s equals 2.5–5.8 σ; 3.8 and 7.1 s; 1.7 %; 28,800 = 72 × 400 pairs; 576 = 2 × 4 × 72 points.

**Chance-cluster figure**
- Figure 1.9 labels (8 cells at 0.53 per hour; 5 cells at 0.07; 4 cells at 0.98) match the text.

**Raster figure**
- Figure 1.2's 4/6 split and the per-frame histogram sums (10 and 10).

**Files and references**
- All 14 figure files and all 18 reproduction scripts exist.
- Every in-text citation has a reference entry, and every reference is cited.
- ⚠ marks agree between text and reference list.
- Category order (0.01 before 0.05 Hz; fast before slow; 7 before 13 cells; first experiment before held-out) is consistent across figures and tables.
