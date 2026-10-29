GRANT 8 MISMATCH — missing none; holds Bash, PowerShell, Edit, Write, Agent, Artifact, Skill, ToolSearch, mcp__claude_ai_Claude_Docs__batch/update (editing and publishing tools forbidden to reviewers)

**Run note:** I used only Read and Grep. I made no edits and wrote no files. Because I held editing tools, this review took a fallback path. The run record's `roles:` line should say so.

# Role 8: You Lost Me (naive-reader accessibility). Chapter 1, Aim 0

**Artifact reviewed:** `<worktree>/docs/dissertation/chapter-1-aim0.md`, with all six figures opened. The reader I played is a neuroscientist on the committee who knows calcium imaging and basic statistics but not this subfield or this repository.

**Verdict:** I would not sign off. The derivations may be right, but a neuroscientist from outside the subfield is lost in §1.1 (Introduction) before any result is stated:
- "fast stream" and "slow stream" are never defined.
- Every contribution is stated in symbols that §1.2 defines only later.
- No figure ever shows what the data look like.
- Two figures send false signals:
  - Fig 1.4C's legend says "fitted" where the text says "nothing fitted".
  - Fig 1.6's y-axis label reads as a multiplication.
- Two lines are easy to follow but lead the reader to a false belief: "spike count" (§1.6.2), and the review and source-reading claims in the preface.

## A. Per-section verdicts (required output)

| § | Terms and identifiers first used here | Defined here? | Can a cold reader follow? |
|---|---|---|---|
| Preface | goal page, `learned/synthetic_validation/`, Claude, Tony, "two-source test" | no | yes, but misled (B2) |
| **1.1** | **KNDy**, action-potential independent, **fast stream / slow stream**, coordination detectors, "the coordination-rates tool", "cluster-finding tool", **g_n(w, σ)**, **k̂**, **g₃/g₂**, at-most-one-event term, **pair correlation** of an event train, joint fit, **Kish's design effect**, **order indicator**, **Kruskal's τ**, **c/√n̄**, **n̄**, **Durbin's rank-sum covariance**, ranking sort, assemblies, latency template, **baseline window**, cumulant route, bin width | Only "assemblies" (in parentheses) and "Aim 0". The tools and symbols are defined later in §1.2. | **BLOCKING.** It has at least 12 undefined terms, and the reader cannot tell what the 33-cell parameters describe (two streams of what?). |
| 1.2.1 | Neyman–Scott, Thomas process, Poisson background, frame, fixed vs Poisson count, 20 s spacing, Table 1.1 symbols | mostly yes; "participation" is used as k/N without being stated | yes |
| 1.2.2 | surrogates (time-shifted copies), coordinated share, **CuBIC**, **multiple-interaction model**, **factorial cumulants**, population-count tools, assembly test, code paths (`bugarach.assess`, …) | surrogates and share yes; CuBIC, the multiple-interaction model and factorial cumulants no | **BLOCKING** (three undefined terms; also code identifiers in prose) |
| 1.2.3 | fission probability, dithering, complexity distribution, "second maximum", **minimum contrast**, **K-function**, simulated-but-not-written-down inference, PP-Seq, **PCA / Marchenko–Pastur null**, SPIKE-order, Synfire Indicator, simulated annealing, Aim 1 | partial | **BLOCKING** (minimum contrast, Marchenko–Pastur, SPIKE-order and "Aim 1" are undefined). This is tolerable for a literature review only if the reader is told it can be skipped. |
| 1.3.1 | g_n, R_n (range), Φ, φ, "tabulated once", uniform phase | yes | yes |
| 1.3.2 | **factorial moments**, falling factorial, shift surrogate, f₂ and f₃, **`solve()`** | the falling factorial yes; factorial moments no | partly (`solve()` is a code identifier) |
| 1.3.3 | k̂ | yes | yes, the best paragraph in the chapter |
| 1.3.4 | **hard-core**, **pair correlation**, **renewal / empirical / Palm trains**, `event_train.py` | no. "Hard-core" is never tied to "events ≥ 20 s apart". | **BLOCKING** |
| 1.3.5 | scaled least squares, identifiable, `fit_joint(..., train=EventTrain.palm(gaps, λ))` | mostly | partly (a code call in prose) |
| 1.4 | q, chance call, budget | yes | yes |
| 1.5.1–1.5.2 | **Aim 1a**, `aim1_one_source.py`, residual, `check()`, `--from-record` | residual yes; Aim 1a no | partly |
| 1.5.3 + Fig 1.1 | recovered ÷ planted, interquartile range | yes | yes |
| 1.5.4 + Fig 1.2 | standard error of a median, sign test, **the repository's "event floor"**, "the shipped tool", **χ² (of what?)**, renewal trains | event floor and χ² no | partly |
| 1.6.1 + Fig 1.3 | pair co-participation, **deft², roh**, intraclass correlation, **margin-preserving null**, uniform null, reuse E/M | deft² and roh yes; the two nulls no | partly |
| 1.6.2 + Fig 1.4 + Table 1.2 | latency template, δ, r, score sort, **Borda count**, **O(N²)**, F, local search, **Kendall's W**, **Durbin incomplete-block test**, **Skillings–Mack**, **ISI-adaptive windows**, **Copeland**, "spike count", calibrated null | score sort and F yes; the rest named but not explained | **BLOCKING** (at least five undefined terms) |
| 1.7 + Figs 1.5, 1.6 | likelihood-ratio test on "onset times and cell identity", 80 % power / 5 % false alarm, **merge rule**, **plateau f²**, realized separation, **ADR-0008 floor** (Fig 1.5), **within-cell floor g**, **oracle t test** (Fig 1.6), Δ | none of the bold terms are defined | **BLOCKING** |
| 1.8 | rederivation, "Tried and dropped", goal page | partly | yes, and honest (but see B2) |
| 1.9 | as in §1.1 | by now mostly | yes |
| 1.10 | **CoactDetect, LoCo**, rolling detectors, **Nbw**, event floor, **correlogram tool**, **August recordings**, **Synfire scan**, random-matrix threshold | no | **BLOCKING** (at least five undefined) |
| 1.11 | none new | — | yes |

## B. Findings

| # | Location | Issue | Severity | Suggested fix | Verified against source |
|---|---|---|---|---|---|
| 1 | §1.1, "0.105 s on the fast stream and 0.131 s on the slow one"; also §§1.3.4, 1.5.4, 1.6.2, 1.7, 1.10 | "Fast stream" and "slow stream" are relative words with no referent, and the chapter never defines them. A cold reader cannot tell what the 33-cell parameters, the gap percentiles or the 7- vs 13-cell figures describe. It also seems to contradict "A recording of 33 cells", which reads as one recording. | blocking | At first use, say in one sentence what the two streams are (which events, separated how, and from what recordings). Name the dataset (how many recordings and mice, and where the numbers were measured). | yes (grep: the terms are never defined in the chapter) |
| 2 | Preface, "Every cited source was obtained … and read against the claim it supports"; §1.8 heading "Adversarial review"; §1.10.5 | A committee member reads "read against the claim", and the heading "Adversarial review", as work done by a person. §1.8 says plainly that the readers and reviewers were Claude agents and that no human reviewed the derivations, but the preface sentence and the heading arrive first and give the chapter standing it does not have. | major | Write it as work done, naming who did it: "each source was read by Claude against the claim it supports; Tony obtained the PDFs." Rename §1.8's subheading to "Review by Claude agents". | yes (chapter text) |
| 3 | §1.6.2, "Synfire Indicator fell as spike count rose"; §1.6.2 "normalizes by all spikes", "non-coincident spikes" | §1.1 says these events are action-potential independent. A neuroscientist reading "spike count" about the lab's recordings concludes the events are spikes, which is false. | major | Say "event count", or "onset count (Kreuz's 'spikes')". | yes (§1.1 lines 22–23 against line 401) |
| 4 | §1.1, "In the arcuate KNDy neurons … the events are action-potential independent" | The acronym is undefined. The claim is surprising to a neuroscientist and has no citation or explanation, so the reader is left asking what the events are. | major | Expand KNDy (kisspeptin/neurokinin B/dynorphin). Add one clause on what the calcium events are, and a citation. | no (I did not check the source for the claim) |
| 5 | §1.1, Contributions 1–7 | Every contribution is stated in notation (g_n, k̂ = 2 + (k − 2)g₃/g₂, c = √(4(k + 1)/(3πN)), deft, Kruskal τ) that §1.2 defines later. The reader cannot judge any contribution when it is claimed. | blocking (part of the §1.1 row) | Restate each contribution in words: "how often a window catches all of an event's onsets when onset times scatter normally". Move the formulas to §1.3–1.6, or define the symbols before the list. | yes |
| 6 | Whole chapter; no figure shows data | There is no schematic of the generative model or of a simulated recording: no raster of cells against time with coordinated events, background onsets and jitter marked. The chapter names mechanisms instead of drawing them: window sharing (g_n), the shift surrogate, the assessor's cluster-start rule, the score sort, and the two-event separation test. A neuroscientist meets six result figures and never sees an input. | major | Add a Figure 1.0: a true raster (time on x, one row per cell) of a short simulated stretch, with an event's participants, background onsets, σ, and windows of 1, 2 and 4 s drawn on it. Add an inset showing a window catching all n onsets of an event or cutting them. Reuse a repository illustration if one exists. | yes (all six figures viewed) |
| 7 | Fig 1.4C legend, "fitted 0.38 / √n̄" | The text says the score-sort constant is "0.376 … with nothing fitted" and exact. The legend calls it "fitted", so the reader concludes the main analytical result is an empirical fit. | major | Relabel: "exact c/√n̄, c = 0.376 (score sort)". Keep "fitted 0.50" for the local search. | yes (legend against §1.6.2 lines 428–434) |
| 8 | Fig 1.6 y-axis, "resolvable Δ (s) · σ = 0.105 s" | The middle dot reads as multiplication ("Δ times σ"). Δ is never defined in the text. | major | Use "separation resolvable, Δ (s)" as the axis label and put "σ = 0.105 s" in a panel title, as Fig 1.5 does. Define Δ in §1.7. | yes (image) |
| 9 | Fig 1.6, panels a–c, orange and green curves dropping to about 0.035 s | Several curves plunge to a constant at the bottom of the axis. A cold reader sees "resolvable at 0.035 s", which looks like a result and is presumably a plotting floor. The caption also does not say what the four curve families mean ("within-cell floor g = 0.1 s (model as stated)", "measured within-cell floor", "membership known (oracle t test)"). "g" also collides with g_n from §1.3. I could not write the "what a cold reader sees" sentence for these panels. | blocking | Mark below-floor points explicitly ("resolved at every Δ tested" with an arrow). Explain each curve family in the caption or in §1.7. Rename "within-cell floor g" (to the minimum gap between a cell's own onsets, for example). | yes (image; caption lines 499–501) |
| 10 | Fig 1.6, "assessor floor 3 s" line vs §1.7 "about 2.5 s for the assessor" | The figure and the text give different values for the same quantity. The reader cannot tell which is right, or whether they are different quantities. | major | Use one number, or say in the caption that 3 s is the full-plateau point and 2.5 s the half-plateau point. | yes |
| 11 | §1.7, "(merge rule + ½) × bin width"; "the plateau, f²"; "between about 0.6 and 2.5 s" | "Merge rule" is undefined (is it a number of bins?). The 0.6 s figure does not match the 0.26–0.76 s floor stated two bullets earlier. | major | Define the merge rule as a number of bins for each tool. Say where 0.6 comes from. | yes |
| 12 | Fig 1.5 | The prediction curves have a sawtooth ripple, and the caption does not explain it. Panels E–H nearly duplicate A–D, and the caption does not say why the reader should care about "realized separation". The legend uses the internal "ADR-0008 floor" and British "centre". | minor | Add one caption line: "ripple: dependence on the pair's phase relative to the bin grid". Say what E–H add, or drop them. Replace "ADR-0008 floor" with "the event floor (the count chance first exceeds)". Use "center". | yes (image) |
| 13 | Fig 1.3 caption, "M from 1 to 10 000" | The x-axis is reuse E/M, not M, so the reader looks for an M axis that is not there. The caption gives the reference lines as "both … and either … (dashed and dotted)", but the legend has either as dashed and both as dotted. The y-axis says "pair-count variance" where the text says "pair co-participation variance". | minor | Rewrite the caption on the E/M axis (M = 1 is E/M = 45). Match the dash order. Use one term. | yes (image against caption) |
| 14 | §1.6.1 and Fig 1.3B, "margin-preserving and uniform" nulls | The assembly test's two nulls are named but never explained, so the result in panel B is opaque. | major | Give one sentence each: what is shuffled and what is held fixed. | yes |
| 15 | §§1.3.2, 1.3.5, 1.5.2, 1.2.2, 1.3.4 | Internal code identifiers appear in reader-facing text: `solve()`, `fit_joint(..., train=EventTrain.palm(gaps, λ))`, `check()`, `event_train.py`, `bugarach.assess`, `bugarach.detectors.count`, `theory.py --from-record`. | major | Use plain concepts ("the tool's own estimator", "the fit, given the stream's measured gaps"). Move the paths to the Reproducing section or footnotes. | yes |
| 16 | §§1.3.4, 1.5.4, 1.10, Limitations 1 | "Hard-core" is never defined (the reader has to infer it means "the generator's 20 s minimum spacing"). "Palm", "renewal" and "pair correlation" are also undefined, and they are what the real-data result rests on. | major | Define "hard-core" at §1.2.1 ("events at least 20 s apart, called a hard-core train"). Give one plain line for renewal and Palm. | yes |
| 17 | §1.5.1, "Aim 1a"; §1.2.3, "Aim 1's brute-force grid"; title "Aim 0" | The aim numbering is internal. The reader cannot map Aim 0, Aim 1 and Aim 1a onto Chapters 1–4. | minor | Say once that "Aim 1a" is this chapter's first simulation experiment. Otherwise use "the first experiment". | yes |
| 18 | §1.10, "CoactDetect and LoCo", "correlogram tool", "August recordings", "Synfire scan", "Nbw", "event floor" | These are undefined names in the discussion and next steps. | major | Give each a few words of explanation, or cut it. | yes |
| 19 | §1.1, §1.6.2, §1.10, "baseline window(s)" | This is the foundation of the chapter's most sobering conclusion (one template at best), and it is never defined: baseline relative to what treatment or state, and how long. | major | Define it at first use (duration and what makes it baseline). | yes |
| 20 | Table 1.2 cells, "1 template 0.43; 2, 0.13" | Lists are packed into table cells with semicolons. The grid of numbers is hard to read and to compare. | minor | Use a real grid: rows for events × cells per event, columns for M = 1, 2, 4, 8, 16, and power in the cells (blank where not run). | yes |
| 21 | §1.10, "Its jitter (0.105–0.150 s)" vs §1.1 "0.105 … 0.131 s" | The range differs between sections. A cold reader notices it and loses trust. (The accuracy roles own the correct value; I flag it only as confusing.) | minor | Use one range, or explain the difference. | no |
| 22 | Fig 1.1, A–C and E–G | Markers are offset horizontally so they do not overlap. On log axes a cold reader may read the offsets as different planted jitters. | minor | Say "points offset horizontally for visibility" in the caption. | yes (image) |
| 23 | Fig 1.2 legend, "95 % interval about the marker size"; grey points "same measurements, Poisson-train prediction" | The phrasing is hard to parse. A reader cannot tell at once that grey points show what the prediction without the at-most-one-event term would give. | minor | Write "grey: prediction without the at-most-one-event term (Poisson events)" and "95 % intervals smaller than the markers". | yes |
| 24 | §1.2.3 | This is a dense literature paragraph of undefined methods. A non-specialist cannot tell which items matter later. | minor | Open with a sentence saying which three precedents the chapter builds on, or point to §1.9. | yes |

## C. "What does this resemble?" (false-friend check) and what a cold reader sees in each figure

- **Fig 1.1:** log-log recovery-ratio plots in a grid, a familiar idiom whose axes mean the expected thing. A reader sees flat lines near 1 that sag for the 1 s window, and two assessor lines stuck flat in H.
- **Fig 1.2:** predicted-against-measured scatter on an identity line, a familiar idiom used correctly. A reader sees points hugging the diagonal; D and H show three violet dots on the diagonal.
- **Fig 1.3:** A is a dose–response-like curve and B is a detection-rate curve, both read correctly. B's collapse to 0 at the far right is surprising but annotated.
- **Fig 1.4:** a sigmoid plus straight log-log decay lines, read correctly. The defect is the "fitted" label (B7).
- **Fig 1.5:** psychometric-style P(two) against separation, read correctly. The ripple goes unexplained (B12).
- **Fig 1.6:** a–c resemble "threshold against group size" plots, but the floor plunges look like results (B9) and the label reads as a product (B8). Panel d (power curves) is clear.
- **No raster-like false friend** appears. The problem runs the other way: no raster appears at all (B6).

## D. Tone
- Headings are in sentence case, and there is no ALL-CAPS emphasis.
- Bold is used heavily for emphasis in prose (§§1.6.1, 1.6.2, 1.7), but it is defensible.
- Lists are formatted as lists, except in Table 1.2 (B20).

## E. Before I would sign off
1. Define the fast and slow streams and the baseline window (B1, B19).
2. Rewrite the contributions in words (B5).
3. Add a raster and mechanism figure (B6).
4. Fix the Fig 1.4C legend and Fig 1.6 (B7–B10).
5. Remove the misleading preface wording and "spike count" (B2, B3).
6. Remove code identifiers from prose (B15).
7. Give a definition for every term in the blocking rows: §§1.1, 1.2.2, 1.2.3, 1.3.4, 1.6.2, 1.7 and 1.10.

---
*Archivist's note (main thread, 2026-10-29): for this public repository (sapper SAP004), the review worktree's absolute path became `<worktree>/`. Nothing else in the report was changed by this pass.*
