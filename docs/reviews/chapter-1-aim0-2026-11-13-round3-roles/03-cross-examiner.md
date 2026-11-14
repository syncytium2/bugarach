GRANT 3 MISMATCH — missing none; holds Edit, Write, Bash, PowerShell, Agent, Artifact, Skill, ToolSearch, Claude Docs batch/update (editing-capable tools no reviewer may have)

This is a finding about the run, not the artifact. The harness gave this role more than its Read, Grep, Glob grant. The run record's `roles:` line should say the review took a fallback path. I used only Read, Grep and Glob and edited nothing.

**Role 3, Cross-Examiner.** Artifact: `<repo>/docs/dissertation/chapter-1-aim0.md`. I checked the whole text (lines 1–1794) against `ch1_intro_figures.log`, `docs/GLOSSARY.md`, `tools/measure_coordination_rates.py` and the rendered PNGs of Figures 1.1–1.6, 1.8, 1.9 and 1.11–1.13.

## Findings
Each row gives: location · issue · severity · suggested fix · could I verify it against a source.

1. **§1.9.4 limitation 3 (line 1609)** · Says the realistic trains "were not placed through the simulator's own measured-interval option (*1.4*)". §1.4 never says this; the phrase occurs only at line 1609, so the cross-reference points nowhere. · medium · Add the sentence to §1.4's "Realistic values" paragraph, or drop the "(*1.4*)". · yes (grep)

2. **Figures 1.9 and 1.12 vs the text and glossary: "held-out record" against "held-out rerun"** · Fig 1.9's panel annotations and legend say "held-out record" and "both records". Fig 1.12's legend says "resolved on both records". The text, the captions and the glossary's reserved term are "held-out rerun" and "runs". The reader meets two names for one run. · medium · Relabel the figures "held-out rerun" and "both runs". · yes (images)

3. **Surrogate offset rule: 1.3.3 (line 457–459), Fig 1.5 caption (line 473–474), 1.5.3 (line 867), Fig 1.5 axis label** · There are three problems:
   - The span is given as "(N − 1) × 2w" in 1.3.3 but "about N·2w" in the Fig 1.5 caption and "about N × 2w" in 1.5.3.
   - "Distinct multiples of two windows" does not match the figure's own offsets of −6, −2, +2 and +6 s for 2w = 4 s. None of those is a multiple of 4.
   - The code (`shifted()`) uses `permutation(N)·spacing + randint(0, spacing)`, minus the mean. That is a spacing of 2w with a random common phase, not multiples of 2w.

   · low · Write "offsets spaced 2w apart (a random permutation, with a common random phase), centered", and use one span formula, (N − 1)·2w, throughout. · yes (code, image)

4. **Raster row order differs across figures** · Figs 1.1, 1.2 and 1.4 put cell 1 at the bottom (33 at top). Fig 1.3 puts cell 1 at the top. The caption admits this ("In this figure cell 1 is at the top"), but it is still an ordering disagreement between figures the reader compares. · low · Redraw Fig 1.3 with cell 1 at the bottom and drop the caption sentence. · yes (images)

5. **§1.2.4 item 3 (line 219–220)** · "Section *1.7* derives the limit: about (m + ½) bin widths, roughly 5 s for these settings". This is attached to all three detectors, but §1.7 derives it only for the assessor and the count detector (fixed bins). The sliding window and CFAR are not covered. Also, m is used here before §1.7 defines it. · low · Say "for the fixed-bin detector" and define m in place, or soften to "a similar limit". · yes

6. **§1.2.4 item 5 vs the log** · The text says CFAR's threshold near event 5 is "6 cells in 119 draws and 7 or more in 67". That is 186 draws. The log (line 8) shows the other 14 at 4 cells (1) and 5 cells (13), and the text leaves them out. Those draws are below the 6-cell floor, which is relevant to why CFAR finds event 5 at all. · low · Add "and 4–5 in 14". · yes (log)

7. **§1.8.2 rounding paragraph (line 1499) vs Table 1.7** · The unrounded "from" values for 7 cells, r = 2.5 (0.06 at E = 2, 0.18 at E = 3, 0.69 at E = 5) differ from Table 1.7's 0.08, 0.20 and 0.68. Line 1455 just said the table "stands for any σ". These come from a different run of 1,000 recordings and agree within Monte Carlo noise, but the text does not say so, so the reader sees two values for one quantity. · low · Note that the unrounded baseline was re-simulated at 1,000 recordings. · partly (internal only)

8. **Fig 1.6 caption (line 575–576)** · "markers are dodged horizontally for visibility" is stated only for panels D and H. In A–C and E–G the coordination-rates points are also visibly offset from their planted σ (the 1 s point sits near 0.75). · low · Say that markers are dodged in every panel. · yes (image)

9. **"Chance floor" scope: §1.9.5 item 2 (line 1638–1639)** · It says "the chance floor of *1.2.3* and *1.6.1*". The term is defined (§1.2.3, and in the glossary) by the up-crossing rule for a 2 s sliding window. §1.6.1 never uses the term; it computes a different quantity, the cluster-start rate in 1 s bins, called "the smallest threshold under [the budget]". · low · Write "the chance floor of *1.2.3* and the safe threshold of *1.6.1*". · yes

10. **Reserved word "fresh seeds" (lines 645, 911, 1065)** · The glossary reserves "fresh seeds" for the bench seeds nothing chose on (6000–6023 and others, line 498). The chapter uses it for the held-out rerun's seeds. The glossary's own Chapter 1 entry (line 713) repeats that use, so the glossary contradicts itself. · low · Use "new seeds" in the chapter, or add a disambiguating clause to the glossary. · yes

11. **"Quieter background" (lines 587, 1246)** · The glossary keeps "quiet" and "busy" for the bench's 0.0052 and 0.019 Hz backgrounds. Its Chapter 1 entry says the chapter "calls the 0.0096 and 0.05 Hz backgrounds by their rates, not 'quiet' and 'busy'". The chapter still says "the quieter background" twice; "busier" appears throughout but is less likely to be confused. · low · Write "at 0.01 Hz". · yes

12. **Stale glossary entry (GLOSSARY line 697–699)** · It says the coordinated onset rate per cell "is labeled 'coordinated share' in the Chapter 1 figures". Figs 1.6 and 1.8 actually label it "coordinated onset rate (per cell) recovered/measured ÷ planted". This is a defect in the companion doc, not the chapter. · low · Update the glossary entry. · yes (images)

13. **Symbol reuse** · Several letters carry more than one meaning:
   - **a:** 1 − e^(−bw) in §1.2.3, w/s in §1.5.2, and Kish's n/a in §1.8.1.
   - **r:** δ/σ, and the order of the falling factorial (k)_r in §1.5.3.
   - **C:** the correlogram C(τ), and the M-template constant.
   - **p:** p = λw, p-values, and p_m.

   Table 1.2 lists only one meaning for each. · low · Rename the local uses (for example α for 1 − e^(−bw), and c_M for the template constant). · yes

14. **§1.4 "a median of 1–2 % of planted" (line 609, also §1.5 opening)** · The quoted medians are 0.007 and 0.016 for the first experiment, and 0.012 and 0.021 for the held-out rerun, so the range is 0.7–2.1 %. · low · Write "about 1–2 %", or give the range. · yes

## Checked and consistent
- **Table 1.1 against the log:** every share, every false-alarm count and rate, and the 0.1 and 0.5 per hour figures.
- **CFAR claims against the log:** the 196/200 count, 98 %, 9–14 and 10–12 cells, the 1.5/h interval of 0.5–3.5, four of five false alarms within 13 s, the 0.021 Hz median estimate, the merge-gap 0.5 s result, and the drawn seed's outcomes against the Fig 1.2 marks (3/5/3 of 6, and the false-alarm times).
- **Event times in Fig 1.2:** 46, 81/85, 151 and 212 s, and the busier stretch at 2–3 min.
- **Recomputed by hand from the formulas:** the chance floors of 6 and 12 cells (2 s window), 4 cells (0.2 s window) and 5 cells (fixed bins); the 8 × 10⁻¹⁰ tail; and ν_c of 0.256 and 0.019.
- **Mixture and sign-test arithmetic:** the chance shares of 0.89–0.96, 0.79–0.92 and 0.02–0.05; the 0.25 share at the budget; sign-test p of 0.007 and 0.60.
- **Correlogram and window-sharing numbers:** HWHMs, peak levels and g₂ values for both sets against the log, plus my own recomputation of g₂.
- **Fig 1.5 C:** the score-sort example computed out (+3, +5, −3, −5 and F = 0.67). The margins of Fig 1.5 B.
- **Order and membership arithmetic:** c = 0.376, C = 0.65, the one-template values, no-order F against its asymptote, and Table 1.7 against the power claims. Membership: 9 % ≈ 0.62 × 0.14 + 0.38 × 0.02, and the ratio 1.044.
- **Joint fit and residuals:** Fig 1.11 counts against Table 1.3 and Table 1.4. Fig 1.12 ranges against the text of §1.5.6 and §1.5.7. Fig 1.9 counts (7/10/17/10, 24 of 32) against the text. Fig 1.13 labels against §1.6.1.
- **Table 1.6:** every tolerance quoted in §1.6.2 and the Fig 1.6 items.
- **Rates and counts:** pooled rates and per-recording counts (9.7/22.0 per hour, 7.3/16.5 per recording, 25.5/53.6, 2.25×); the grid totals (48 conditions, 240 and 160 recordings, 720 combinations); and the cross-references to sections and tables.
