GRANT 8 MISMATCH — missing none; holds Edit, Write, NotebookEdit, Bash, PowerShell, Agent, Artifact, Skill, ToolSearch, MCP doc, Dropbox, Gmail tools (forbidden). I was spawned through the inline fallback as a general-purpose agent. I used only Read and Grep, and I edited, created and deleted nothing. This mismatch is a finding about the run: the run record's `roles:` line should say the review took a fallback path.

# Role 08, "You Lost Me": naive-reader review of Aim 0

**What I examined:** `_scratch/r2_extract.md` in full (page lines 16–241 and plan item 286–311), the GLOSSARY "Two measures of one spread" note (lines 473–476) and the synthetic-validation vocabulary block (656–673). I opened all four figure PNGs before reading any caption. I grepped `membership_limit.py` and `aim0_figures.py` to check one band label. I did not open any blinded path.

## Per-slide verdict table

Each section, figure and table counts as one slide. A slide with three or more undefined terms is a blocking row.

| # | Slide / panel | Terms and identifiers first used here | Defined on the slide? | Cold reader follows? |
|---|---|---|---|---|
| S1 | "Where it stands" | Aim 1a, one source, random membership, assessor, coordination-rates tool, fixed threshold, seed per recording, background draws, three windows, murderboarded / 11 roles, at-most-one-event term, refusal rule, August synfire result, "exact" | None. The symbols block comes *after* this section. | **BLOCKING** (≥3 undefined: assessor, coordination-rates tool, at-most-one-event term, refusal rule, synfire) |
| S2 | "Symbols and tools used below" | N, k, σ, w, λ, b, K, E, M, condition, coordination-rates tool, assessor, time-shifted copies, "coordinated share of onsets" | Mostly yes. "Coordinated share of onsets" is not defined: share of *what*? | yes, with one gap |
| S3 | Figure 1 (render) | recovered ÷ planted, joint fit across windows, IQR bars, down-triangle | Caption defines most. Joint fit points forward to Aim 0. | yes, but the panel H reading trap is in F3 |
| S4 | Aim 1a bullets | MAHICE, `derive_k`, chance coincidences, ±1.5 s gather | MAHICE is not defined. `derive_k` is a code identifier. | yes (2 undefined) |
| S5 | "Aim 0, the predictions" + "What it rests on" | Neyman–Scott (defined), factorial cumulants, population count, CuBIC, fission probability, window sharing g_n, frame rounding, at-most-one-event term | Not defined: factorial cumulants, population count, CuBIC, frame rounding. The mechanism is never drawn. | **BLOCKING** (4 undefined; core mechanism has no illustration) |
| S6 | Figure 2 (render) | "exact prediction", Poisson event train, at-most-one-event term, binomial tail, chance clusters | Partly. "Exact" is misleading (F2). | yes for A–C and E–G; D/H follow too, but switch quantity silently |
| S7 | Aim 0 prediction bullets | seed-to-seed noise, hard-core bias, surrogate's own correlations, "murderboard role 6", `solve()`, recording-windows, search bound, frame scale | Not defined: hard-core bias, `solve()` (code identifier), "role 6" as a source | **BLOCKING** (3 undefined) |
| S8 | "Checked by two more sessions" + table | blind A/B, excess cumulants, leading terms, "no 1/N factor", k̂, g_3/g_2, Charlier polynomials, delta method, null variances, up-crossing form, window-budget closed form, count detector, chance joiners, event floor | Almost none defined. In the table, a cold reader cannot tell whether "no 1/N factor" means agreement or an error. | **BLOCKING** (≥8 undefined) |
| S9 | Membership + Figure 3 | exchangeable limit, population-count tool, co-participation counts, design effect (Kish), reuse E/M, `stat_dispersion`, readout dilution | Mostly yes. "Population-count tool" is not defined. `stat_dispersion` sits in the caption. | yes, but the band is mislabelled (F4) |
| S10 | Order + Figure 4 | latency template, τ (two meanings), F, Borda/Copeland, O(N²), Kendall τ, Greiner's relation, F_M, F_0, n̄, score sort, local search | F_M and F_0 appear only in the legend. τ collides (F5). | no: blocking-level confusion on the F = Kendall τ sentence |
| S11 | Kreuz comparison bullets | SPIKE-order, Synfire Indicator, ISI-adaptive windows, simulated annealing, finite-size effect, fast/slow ρ, 5-approximates | Not defined: ISI-adaptive, fast/slow (streams), ρ (Spearman?), "5-approximates" | **BLOCKING** (4 undefined) |
| S12 | "What it changes for the generator" | PP-Seq, spread s | `s` collides with the unit "s" | yes |
| S13 | Tried and dropped | none new | n/a | yes (one stale pointer, F12) |
| S14 | Plan item, Aim 0 | PySpike, count detector, co-activation matrix, low-rank, Marchenko–Pastur, PCA, Cramér–Rao, composite likelihood, identifiability boundary, slow-comodulation, dimensionless axes, CoactDetect, LoCo, clustered intervals, burstiness | Almost none | **BLOCKING** (≥10 undefined; the audience includes cold future sessions) |
| S15 | GLOSSARY additions | σ vs correlogram half-width, source, stream, condition, membership, latency template, exchangeable limit, g_n | Yes | yes (one mismatch, F11) |

## Caption-covered "what does this resemble?" checks

For each figure: what it resembles, what the axes mean in that idiom, and whether they mean the same here.

- **Figure 1** resembles a small-multiples recovery or dose-response grid: a log ratio against a log parameter. The axes mean the same in that idiom, so it is not a false friend.
  - **What a cold reader sees:** flat lines hugging 1 in A–C and E–G, two orange/pink lines floating at ×16 and ×8 in F, and steep falling lines in D/H.
  - **Problem:** the falling lines in D/H are a constant absolute value drawn as a ratio (F3).
- **Figure 2** resembles a calibration scatter with an identity line; the axes mean the same, so it is not a false friend.
  - **What a cold reader sees:** coloured dots on the diagonal and grey dots in a vertical column at x ≈ 1.
  - **Problem:** nothing tells the reader that a grey dot and a coloured dot at the same height are the *same measurement* paired with two predictions.
  - D/H switch to log absolute rates in a grid whose first six panels are linear ratios.
- **Figure 3A** resembles a dose-response curve over a shaded null band; **3B** resembles a power curve. Both are conventional, so not false friends.
  - **Problem:** the band is not what its label says (F4).
- **Figure 4A** resembles a psychometric sigmoid; **4B and 4C** resemble log-log scaling plots. All are conventional; no false friend.
  - **What a cold reader sees:** dots on curves, with two parallel lines in C.
  - The phantom-structure check is clean in all four figures.

## Findings

| # | Location | Issue | Severity | Suggested fix | Verified against source? |
|---|---|---|---|---|---|
| F1 | S1, "Where it stands" bullet 2: "Two more sessions, given only the question and the code" | Readers will take this as independent replication. S8 says they also got the Aim 1a record and shared the prompt, repository, model and seeds, and calls it "a consistency check, not independent review". "Only the question and the code" is false and invites the wrong inference. S8's bold "One answer, reached three ways" does the same before its own caveat. | major | Write: "Two more sessions, given the question, the code and the Aim 1a record, reached the same core derivation (a consistency check, not independent review)." Move the caveat into the bold lead of S8. | yes (extract lines 10–11 vs 115–119) |
| F2 | Figure 2 legend: "exact prediction, 5/10/20 cells per event" | The page's own run record says "exact" was stretched past participants. The legend still labels all panels "exact", including event rate and share, which the text says are "predicted less well", and 5-cell events, which are "not predicted". | major | Write "with at-most-one-event term" (or "full prediction") in place of "exact prediction". | yes (extract lines 15, 93–97; render) |
| F3 | Fig 1 D/H vs text "reads about 0.66 s whatever was planted… tops out near 0.7 s" | The text quotes absolute seconds, but the panels plot recovered ÷ planted. A constant 0.66 s therefore draws as a steep line falling from ×14 to ×0.7. A cold reader sees "the assessor hugely overestimates small jitter", not "the assessor returns a constant". | major | Plot D/H as recovered seconds against planted seconds with an identity line, or add a labelled slope −1 guide marked "constant 0.66 s". | yes (render; 0.66/0.05 ≈ 13 matches H) |
| F4 | Fig 3A band "random participation, 95 % range", caption "the 95 % range of a single random recording"; 3B "5 % by chance" | The band runs from 1 (the mean) to the 95th percentile (`axhspan(1, random_p95)`). It is not a 95 % range. Read as a central 95 % range, only 2.5 % would fall above it by chance, which contradicts the "5 % by chance" line. | major | Label it "below the random 95th percentile", draw it from the axis floor, and make the caption match. | yes (`aim0_figures.py:132,140`; `membership_limit.py:21,46`) |
| F5 | S10: "F = (2/π) arctan τ (A), which is the population Kendall τ between template and observed latencies" | τ means two things in one sentence: template spread ÷ jitter, and Kendall's τ. It also reads as a time constant to a neuroscientist. A cold reader cannot tell which τ F equals. | major | Rename the ratio (for example ρ_s or "spread ratio r") and write "F equals Kendall's rank correlation between …". | yes (extract line 182–183) |
| F6 | S5, "What it rests on" (BLOCKING S5) | The core mechanism is only name-dropped: factorial cumulants of the population count, CuBIC, frame rounding. Nothing shows *why* the window must exceed the jitter. | major | Add a schematic: one event's onsets spread by σ, cut by windows of width w = 1, 2, 4 s, with g_n as the share caught together. State in one plain sentence what the tool counts. | n/a (judgment) |
| F7 | S1, S7, S8, S14 (blocking rows) | Each introduces three or more undefined terms (listed in the table). For a non-statistician PI: Charlier polynomials, delta method, up-crossing form, hard-core bias, Cramér–Rao, Marchenko–Pastur, CoactDetect, LoCo, PySpike. | blocking, by slide | S1: move the symbols block above "Where it stands", or link it. S7/S8: gloss each method in parentheses or cut it to "by a variance formula". S14: one-line gloss per item, or links to the GLOSSARY. | n/a |
| F8 | S7 "(about 1 % of the pair count, murderboard role 6)"; S11 "(0.28 at 10 of 33 cells…; murderboard role 6)" | A reviewer agent's computation is cited as if it were a source. A cold session will treat "role 6" as established and cannot trace it. | minor | State it as work done, with a script or number pointer, for example "a reviewer's check, not yet in `theory.py`", or move it into the code. | partly (cannot open the blinded review) |
| F9 | S9: "detected every time while each assembly is used at least once" | Readers take "used at least once" as "every assembly appears", but the meaning is reuse E/M ≥ 1. With E = M = 45, many assemblies are never used. | minor | Write "detected every time once reuse E/M reaches 1". | yes (Fig 3B render) |
| F10 | "blind" (S4 "measured blind by two tools"; S8 "blind passes") | The same word carries two meanings: the tools do not see planted values, and the agents do not see prior results. | minor | Use "without the planted values" for the tools and keep "blind" for the agents. | yes |
| F11 | Page vs GLOSSARY: the page says "cells" throughout; the GLOSSARY says "Never 'cell', which is an ROI" and uses "ROIs" | The page never says that cell = ROI. A cold reader of both may think they are different units. | minor | Add "(cells = ROIs)" to the symbols block. | yes |
| F12 | S13: "errors correlated across each row of Figure 1" | Figure 1 is now the reseeded version, so the reader looks for correlated rows and finds none. | minor | Write "…of the first run's Figure 1 (record kept in `aim1_one_source_shared_seeds.json`)". | yes |
| F13 | Code identifiers in audience text: `derive_k`, `solve()`, `bugarach.assembly.stat_dispersion` (Fig 3 caption), MAHICE | These are internal identifiers, plus an undefined acronym. | minor | Use the plain concept ("setting K from each recording's own null", "the tool's own estimator") and keep paths in a "code" line. | yes |
| F14 | Fig 4B legend `√(F_M² + F_0²)`; S12 "latency template (spread s)" | F_M and F_0 are defined only by the legend. `s` collides with the unit seconds. | minor | Define F_M (signal) and F_0 (no-order bias) in the caption; rename the spread symbol. | yes |
| F15 | S11: "fast ρ −0.75, slow ρ −0.40"; "5-approximates" | Fast/slow streams and the ρ statistic are not named on the page, and "5-approximates" is algorithms jargon. | minor | Write "Spearman ρ in the fast and slow streams" and "gets within 5× of the best order's disagreements". | no |
| F16 | S2 symbols paragraph | Fourteen definitions are run together with "·" separators: a list smuggled into prose. | minor (tone) | Format it as a list or table. | yes |
| F17 | Fig 1 A/C/E/G | A 3-decade log axis squeezes the ±25–30 % effects the text quotes into a few pixels. A cold reader sees "all flat at 1". | minor | Use a narrower y range for the ratio panels (for example 0.3–3), or a linear ratio axis. | yes (render) |
| F18 | S4 "Aim 0's joint fit (violet) does measure it" | This reads as unconditional. S7 says jitter is not resolved at 0.05 s or for 5-cell events, and violet in H at 0.05 s reads 0.53 with a bar down to 0.1. | minor | Write "…does, from 0.2 s up and for events of 10 or more cells". | yes (render; extract lines 103–104) |

No ALL-CAPS or scattered capitals in the prose; sentence case holds throughout. None of the four figures is a false friend, and none shows phantom structure.
