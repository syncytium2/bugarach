GRANT 8 MISMATCH — missing none; holds Edit, Write, Bash, PowerShell, Agent, Artifact, Skill, ToolSearch, mcp__claude_ai_Claude_Docs__batch, mcp__claude_ai_Claude_Docs__update, mcp__claude_ai_Claude_Docs__guide (plus SubagentHandback, the return channel)

Run note: this is a finding about the run, not the artifact. I hold every tool my grant allows, plus editing and execution tools that no reviewer may have. That means this role took a fallback path, and the run record's `roles:` line should say so. I used only Read, Grep and Glob. I edited, wrote and deleted nothing.

# Murderboard role 8, "You Lost Me": Chapter 1 (chapter-1-aim0.md, blob 14d63527)

**Surface checked.** I read the whole chapter (1,669 lines) as a scientist outside this subfield. I opened all 19 figures as images, each before its caption, including the six linked from `docs/learned/...`. I also read writing_conventions.md and grepped for "toy", "fire", code identifiers and unit words.

## Summary

The owner's requested structure is mostly in place:
- The problem is drawn first. Figure 1.1 is a true raster and a good one.
- The three simple detectors follow (fixed bins, sliding window, CFAR), shown on one recording with Table 1.1.
- The measuring tools then get their mathematics in 1.3.
- No "toy" and no "fire" appear.

The chapter loses the naive reader in four places:
1. **"window" carries four meanings.** In two places the collision makes a sentence read as something false.
2. **CFAR's radar "cells" sit next to biological cells.** The reader is never told that a radar cell here is a stretch of time.
3. **1.3.1 and Table 1.2 open with symbols and "the first experiment" before either has been introduced.**
4. **1.3.6 Prior work sits before the chapter states its question.** It is dense with undefined jargon and points forward to results the reader has not seen.

Smaller items:
- Internal code identifiers (`jit_obs`, `jit_null`, `jit_excess`, a .json path) appear in audience-facing text.
- "record" and "recording" are easily confused.
- A handful of figure-level traps, listed below.

## Findings

Format: location · issue · severity · suggested fix · verifiable against a source (yes/no)

1. **"window" has four meanings: the counting window w (1–4 s), the sliding 2 s window, CFAR's 30 s reference windows, and the 20-minute "recording window" of real baseline.** · Major (misleads).
   - Line 623, "17 of 720 recording-windows", means recording × tool window (240 × 3). But "recording windows" was defined at line 225 as 17–20 minute stretches of baseline. A reader takes 720 as a count of 20-minute windows.
   - Conclusion, lines 1538–1543: "What a realistic 20-minute window can support … A window shorter than about six times the jitter undercounts participants." These sit two sentences apart and mean different things.
   - Same problem in 1.5.7 ("one 20-minute window" next to "1 s window").
   - Fix: give the 20-minute stretch its own word ("segment" or "baseline epoch") everywhere, and call the 1/2/4 s units "counting windows". Replace "recording-windows" with "recording × window combinations".
   - Verifiable: yes (lines 225, 623, 1538–1543).

2. **1.2.3 and 1.3.6: radar "cells" next to imaged cells.** "reference cells around the cell under test", "Guard cells", and in 1.3.6 "with the cell under test and its neighbors left out". The reader has just spent two sections on cells as neurons, and nothing says a radar cell is a range bin, i.e. here a stretch of time. "Applied here…" uses seconds without making the mapping. · Major (a reader follows it and gets it wrong).
   - Fix: one clause at first use, e.g. "(in radar a 'cell' is a slot of range; here it is a stretch of time, not a neuron)". Prefer "reference stretches" or "guard stretches" in the "applied here" sentence and in 1.3.6.
   - Verifiable: yes (lines 129–137, 473).

3. **1.3.1 and Table 1.2 front-load undefined material.** · Blocking row (see the verdict table).
   - The table's third column is headed "values in the first experiment", but that experiment is introduced only in 1.4.
   - It lists about 12 symbols defined only in 1.5–1.8: f₂, f₃, g_n, q, ν_c, ν_e, π_K, τ_min, M, δ, r, F, n̄.
   - The same subsection uses "Poisson" undefined (line 239), plus "sampling quadrats" and the Thomas (1949) historical aside, all before any tool is shown.
   - Fix:
     - Move Table 1.2 to the start of 1.4, or make it an end-of-chapter glossary.
     - In 1.3.1, keep only N, k, σ, b, E, λ, T, with a one-line pointer.
     - Define Poisson at first use (best in 1.2.3, where "background onsets at random at rate b" already describes it: "…at random at a constant rate b, a **Poisson** process").
     - Move the Thomas/quadrat aside to 1.3.6.
   - Verifiable: yes.

4. **1.3.6 Prior work is placed before 1.4 states the question.** · Blocking row.
   - It uses terms nowhere defined: fission probability, dithering, "second maximum" of the observed-minus-independent distribution, fluorescence fluctuation spectroscopy, brightness and occupation number, compound Poisson, minimum contrast, Ripley's pair-count function, pairwise-interaction inhibition process, Marčenko–Pastur, SPIKE-order, simulated annealing, latency correction, interictal spike propagation, replay.
   - It also points forward to results the reader has not met: "the joint fit's construction (1.5.6)", "this tool's correction for event trains that cannot share a window", "the assessor's cluster-start factor".
   - The "What is missing" paragraph therefore claims novelty for objects the reader cannot yet name.
   - Fix: move 1.3.6 into the Discussion beside Table 1.9 (1.9.2), or after 1.4's contributions. Give each named method a clause saying what it does in plain words, or cut it to the citation.
   - Verifiable: yes.

5. **Internal code identifiers in audience-facing text.**
   - `jit_obs`, `jit_null`, `jit_excess` appear at lines 433–434, at 1159–1165 and in the Table 1.9 row.
   - The file path `separation/real_intervals/intervals_results.json` sits inside the Figure 1.10 caption.
   - "the follow-up scripts", "the simulator's own measured-interval option" and "fixed-count placement" (lines 647–650) describe implementation, not concepts.
   - Severity: moderate (explicit checklist rule).
   - Fix: write "the observed jitter reading", "the same reading on shifted copies", "their difference". Move the path to the Reproducing section.
   - Verifiable: yes.

6. **"record" against "recording".** "held-out record", "two records", "changes sign between records", "the underlying record", "run record" (a README) all sit beside "recording" (an imaging session). A cold reader reads "on both records" as "on both recordings". · Moderate.
   - Fix: call the rerun "the held-out rerun" or "the held-out replicate experiment", and the pair "both runs". Keep "record" only for documents.
   - Verifiable: yes (lines 627–633, 794, 1.5.6, Figures 1.9 and 1.12).

7. **"assessor" is used before it is defined, and its name invites a wrong inference.**
   - First use: line 193, "derives this failure for the repository's assessor". The definition comes only at 1.3.4 (line 428).
   - To an outsider, "assessor" reads as something that grades detectors. It is actually a cluster-based measuring tool.
   - Severity: moderate.
   - Fix: define it at first use ("the repository's **assessor**, a tool that measures participation and jitter from clusters of co-active cells (1.3.4)"), or rename it in prose ("the cluster assessor").
   - Verifiable: yes.

8. **Surrogate-offset paragraph (1.3.3, lines 384–389): "independent random shifts were tried and lost planted pairs"** has no mechanism a cold reader can supply, so it reads as a non sequitur. "Per recording it reports participants from f₃/f₂ pooled across all the recordings it is given" is self-contradictory on a first read. · Moderate.
   - Fix: one sentence on why independent shifts lose planted pairs. Rewrite the second sentence as "it estimates participants once from all recordings pooled, and reports that value for each".
   - Verifiable: no (the mechanism is not stated in the chapter).

9. **1.8.2, the "One template" bullet** puts Kendall rank correlation, the bivariate normal, the "quadrant-probability relation", Cramér, Kruskal and Greiner into three lines. It is 4+ undefined terms, all attribution. Table 1.9's last rows (Durbin's incomplete-block test in Skillings & Mack's form, "Kendall-τ analogue of √W") have the same problem. · Moderate (blocking row by the three-term rule).
   - Fix: state the result plainly ("F equals Kendall's rank correlation between the template and the observed latencies, a standard result for normal data") and move the lineage to Table 1.9 or a footnote.
   - Verifiable: yes.

10. **Statistical and engineering terms used undefined.** · Minor each; 1.5.6 and 1.6.1 reach three or more in one subsection.
    - "identifiable" and "Fisher-information calculation" (1.5.6)
    - "censored" (Figure 1.11 caption)
    - "Poisson-binomial", "rigid-shift null", "over-dispersed", "burstiness" (1.6.1)
    - "test size" (Figures 1.15 and 1.19)
    - "inverse-covariance weighting", "parametric bootstrap", "random-matrix threshold", "likelihood bounds" (1.9.5)
    - "seed" (1.4)
    - "null" as a noun: first in the Figure 1.4 caption, never defined. It needs one line: "a **null**: data built to have no coordination, against which a statistic is compared."
    - Fix: a clause each at first use.
    - Verifiable: yes.

11. **Foundational terms missing for an outsider.**
    - "calcium events" (line 12) is never defined. It needs one clause: a transient rise in a cell's calcium-reporting fluorescence.
    - "baseline" is undefined at line 51 ("at baseline only"), and it collides with the title's "an analytical baseline". Give the recording sense a definition (untreated, pre-treatment period) and change the title word, e.g. to "reference".
    - "the lab" (line 122 onward) has no named referent. Say whose recordings once ("the DeFazio et al. (2026) recordings of arcuate kisspeptin neurons").
    - "Hz" first appears at line 122 for a per-cell onset rate, while Figure 1.1 says "onsets per second per cell". Tie the two at first Hz.
    - Severity: minor.
    - Verifiable: yes.

12. **"Aim 0" (lines 72, 594) is an orphan label.** It implies Aims 1–n, but the dissertation outline in 1.1 is by chapter and names no aims. A reader goes looking for Aim 1. · Minor.
    - Fix: drop the label and keep "predict first, simulate to check", or say in one clause why it is numbered 0.
    - Verifiable: yes.

13. **Figure 1.6's title, "What the first experiment found", includes the joint fit (violet).** That estimator was built afterward from the theory in 1.5.6. In panels D and H the violet line tracks identity, so the figure that introduces the jitter failure also shows it solved, and a cold reader takes the joint fit as part of the first experiment. The caption does mention it. · Minor-moderate.
    - Fix: drop the joint fit from this figure (it is in Figure 1.11), or retitle it "…and the joint fit derived later".
    - Verifiable: yes.

14. **Figure 1.16.**
    - The x-axis "realized separation, median onset B − A" names the two events A and B, which collides with the panel letters A–H. The text never calls the events A and B.
    - The axes say "planned separation", while the text says "planted".
    - "unimodal" in the legend is undefined.
    - The footnote "the event floor (the count chance first exceeds)" is garbled.
    - The y-axis says "clusters" for the count detector, which "calls events".
    - Severity: moderate.
    - Fix: "second event's median onset minus the first's"; use "planted"; "2σ: below this the two onset clouds merge into one hump"; rewrite the footnote.
    - Verifiable: yes (render).

15. **Figure 1.7.**
    - Panel A's x-axis is w/σ and panel B's is σ/w. The same figure flips the ratio, so the reader must invert in their head to connect A to B.
    - The legend says "full prediction", while the caption calls the same marks "the hard-core form".
    - The vertical line "window = full width of uniform jitter (2√3 σ)" is not explained in the caption.
    - Severity: minor.
    - Fix: put both panels on σ/w; use one name.
    - Verifiable: yes.

16. **Figure 1.9.**
    - The x-axis is categorical, but its labels (0.0125, 0.025, 0.05, 0.1, 0.125, 0.2…) are evenly spaced and look like a continuous log axis. That is a mild false friend; the caption warns, but the idiom is read first.
    - The legend shows "10 cells" and "45 events" with the same filled-circle marker.
    - Severity: minor.
    - Fix: draw the group labels as boxed categories (or as "σ/w = 0.05") and separate the shape and fill keys in the legend.
    - Verifiable: yes.

17. **Figure 1.10.** The panel C/D subtitle "tabulated event counts" does not match the caption's "thinned to the pooled rates". "one event per mean interval" (A/B) is opaque. The legend uses the same gray circle for "fast stream" and for the size key. · Minor.
    - Fix: "at the pooled rates", and "one event per mean measured interval (25.5 and 53.6 per recording)".
    - Verifiable: yes.

18. **Figure 1.14** prints "c/(c + e)", while the text uses ν_c/(ν_c + ν_e); c and e are undefined in the figure. **Figure 1.15** says "gap" for what the text calls interval, and "test size" for what the caption calls false-alarm rate. · Minor.
    - Fix: one notation, one word.
    - Verifiable: yes.

19. **Figure 1.5's raster puts cell 1 at the top. Figures 1.1–1.3 put cell 1 at the bottom.** · Minor. This is a cross-figure consistency item and belongs to agent 3; it is noted here because a cold reader comparing rasters notices it.
    - Fix: one orientation throughout.
    - Verifiable: yes.

20. **Table units (boundary with agent 10's mechanical row).** Table 1.1's per-event columns are shares of 200 draws, Table 1.7 is power, and Tables 1.4 and 1.5 are ratios or counts of 40. None of these is marked in its header. · Minor.
    - Fix: "(share of draws)", "(power, 0–1)", "(fitted ÷ planted)".
    - Verifiable: yes.

## What sentences invite readers to infer (taken-to-mean check)

These read correctly; no false credit was found:
- Line 3 ("written by Claude with Tony DeFazio as an exercise; no human has reviewed the derivations").
- "Eleven AI agents… That panel is not a committee and not peer review."
- "two further Claude sessions… a consistency check, not independent review".
- "realistic" is defined (values measured from the lab's recordings), and the caveat that the interval lists understate close pairs is stated.
- "held-out" is defined as a rerun on fresh seeds after model choices, which matches its ML sense honestly.

The misleading lines are the collisions in findings 1, 2, 6, 7 and 11 ("baseline").

## Per-section verdict

Format: section · terms first used here · defined here? · cold reader follows?

| section | terms first used here | defined here? | cold reader follows? |
|---|---|---|---|
| Title and note | analytical baseline, multichannel, ⚠ | ⚠ defined; "baseline" collides | yes |
| 1.1 The problem | calcium event, onset, frame, recording, raster, background, coordinated event, source, participation, jitter, membership rule, latency template, baseline, repository | all but calcium event and baseline | yes |
| 1.1 How the chapter proceeds | correlogram (preview), Aim 0 | preview pointers; Aim 0 orphan | yes |
| 1.2.1–1.2.2 | detector, call, planted, bin, threshold K, merge gap, count detector, sliding window | all | yes |
| 1.2.3 CFAR | binomial, Hz, chance floor, reference cells, cell under test, guard cells, masking, the lab | Hz unit and "the lab" not defined; radar "cell" not mapped | no: misleads (finding 2) |
| 1.2.4, Figure 1.2, Table 1.1 | false call, assessor | assessor not defined | yes, apart from "assessor" |
| 1.3.1 data and model | channel, ROI, stream, recording window, Neyman–Scott, Thomas process, quadrats, Poisson, hard-core, plus ~12 later symbols, "first experiment" | Poisson, quadrats, first experiment and most symbols not defined | **BLOCKING (1.3.1)** |
| 1.3.2 correlogram | lag, cross-cell correlogram, chance C₀, φ, HWHM, calibration curve, "shoulder" | all but "shoulder" | yes |
| 1.3.3 window counting | factorial moments and cumulants, f₂, f₃, k̂, g₂, surrogate, circular shift | yes, but the surrogate-offset rationale is missing | partly (finding 8) |
| 1.3.4 assessor / count detector | cluster, gather, code identifiers | yes; identifiers leak | yes, apart from identifiers |
| 1.3.5 | assembly, assembly test, order indicator | pointers | yes |
| 1.3.6 Prior work | ~15 named methods (finding 4) | mostly not defined | **BLOCKING (1.3.6)** |
| 1.4 what brute force found | condition, seed, joint fit (forward reference) | seed not defined | yes |
| 1.4 question / testing | residual, refused, recording-windows, record(s), renewal train, pair correlation, stationary | yes, but the collisions mislead | no: misleads (findings 1, 6) |
| 1.4 contributions | design effect, arcsine relation, Borda score | arcsine not defined | yes |
| 1.5.1–1.5.2 | g_n, range, Φ | yes | yes |
| 1.5.3 | falling factorial, at-most-one-event term, hard-core form, CuBIC eq. 3 | yes; (1 − 1/N) terms not explained | yes |
| 1.5.4 | sign test, 2 SE, dependence-aware null | mostly | yes |
| 1.5.5 | general form, empirical train, bootstrap SE | yes; Figure 1.10 terms do not match | yes |
| 1.5.6 | identifiable, Fisher information, censored (Figure 1.11) | not defined | **BLOCKING by count (1.5.6)**; trivial to fix |
| 1.5.7 | in band (±25 %), general form given the true train | yes | yes |
| 1.6.1 | q, cluster-start factor, ν_c, Poisson-binomial, event floor, rigid-shift null, over-dispersed, recall | Poisson-binomial, rigid-shift null, over-dispersed not defined | **BLOCKING by count (1.6.1)**; trivial to fix |
| 1.6.2 | mixture, chance share | yes; identifiers leak | yes |
| 1.7 | likelihood-ratio test, power, false alarm, EM, τ_min, plateau π_K² | yes | yes |
| 1.8.1 | reuse, margin-preserving and uniform nulls, Bonferroni, eigenvalue, roh | mostly | yes |
| 1.8.2 | score sort, F, local search, Kendall τ, bivariate normal, quadrant-probability, lattice convolution, randomized test | attribution terms not defined | **BLOCKING (1.8.2, "One template" bullet)** |
| 1.9 Discussion and Table 1.9 | Durbin, Skillings–Mack, √W, minimum contrast, Ripley; 1.9.5 inverse-covariance weighting, parametric bootstrap | not defined | no (Table 1.9 and 1.9.5) |
| 1.10 Conclusion | none new | n/a | no: misleads ("window" collision) |
| About / Reproducing | AI review panel, scripts | appropriate there | yes |

## Per-figure verdict

For each figure: what a cold reader sees, the idiom it resembles, and whether it is readable.

- **1.1:** Three stacked rasters (background only, events only, both), with four triangles over the events. A true raster, read correctly. Readable; a model figure.
- **1.2:** Triangle verdict lanes over a raster, then bin-count bars and a sliding-count trace with a dashed fixed line and a violet stepped CFAR line. The idioms (raster, histogram) are used correctly. Readable. The lane label "background 0.0096 Hz" is the only unit-mismatch point.
- **1.3:** Two short rasters around one event each; a correlogram (a tall narrow blue peak and a wide red one); a sigmoid-then-dip curve of pair share against log window width; a log-scale tail plot against K. Readable once the caption is read. Panels C–E use tools defined only in the following subsections (forward references are given).
- **1.4:** (A) Four-cell rasters before and after per-cell shifts. (B) Three 6×4 membership grids drawn as bordered tiles, so they are not a raster false friend, which is good. (C) A worked lead table. I checked C's arithmetic: nets +3, +5, −3, −5; order 2, 1, 3, 4; 10 agree and 2 disagree; F = 0.67, all correct. B's row and column sums are also correct. Readable; a good illustration of each mechanism.
- **1.5:** A raster (cell 1 at top, see finding 19), enlarged events with per-frame histograms and window strips, then per-window count bars for three tools. Readable. Dense, but every element is labeled.
- **1.6:** Eight small log-ratio panels, plus jitter panels against identity. Readable. Misleading inclusion of the joint fit (finding 13).
- **1.7:** Two sigmoids in A, and falling bias curves with points in B. Readable. Axis inversion between panels (finding 15).
- **1.8:** Predicted-against-measured scatters with an identity line. Readable.
- **1.9:** Residual dot-and-whisker strips around zero. Readable. Categorical axis looks continuous (finding 16).
- **1.10:** Measured-against-predicted scatters, with open and filled pairs joined by lines. Readable with effort; terms do not match (finding 17).
- **1.11:** Medians with IQR bars against a shaded band (A, B), and per-recording strip plots (C). Readable.
- **1.12:** A grid of filled, half-filled and open circles over (σ, k), with two shaded boxes for realistic values. Readable; clear.
- **1.13:** Chance-cluster rate falling with K on a log scale, against a dashed budget line. Readable.
- **1.14:** Four panels where the purple mixture line sits on the event-only curve (A) or the chance-only line (B, C). Readable. Notation c/(c + e) (finding 18).
- **1.15:** Resolvable separation against k on a log scale, and power curves in D. Readable for a statistics-literate reader. "test size", "gap" (finding 18).
- **1.16:** Step-up curves of the probability of a split against separation. Readable, but "B − A" collides with the panel letters (finding 14).
- **1.17:** A variance ratio rising on log–log axes, and a rejection share against reuse. Readable.
- **1.18:** Three log-axis panels of F against r, M and n̄, with closed-form lines through points. Readable for a math reader.
- **1.19:** Power against events per recording, solid for one template and dashed for two. Readable.

False-friend check: every raster-looking panel (Figures 1.1, 1.2B, 1.3A–B, 1.4A, 1.5A–C) really is a time-by-cell raster. The membership matrix in Figure 1.4B is drawn as gridded tiles, not a raster. The only mild false friend is Figure 1.9's categorical axis.

**Tone.** Sentence case throughout, no ALL-CAPS, and lists are formatted as lists. Bold is heavy in 1.4 and 1.5 but is used to name items, not to claim a best value.

**Verdict for the owner's brief.** The opening three-part arc works for a naive reader. The chapter stops being readable at the start of 1.3.1 (the symbols table and "first experiment") and 1.3.6 (prior work before the question). It misleads in two places: the "window" collision, which reaches into the Conclusion, and CFAR's radar "cells". Fixing findings 1–4 and 7 would carry the cold reader from 1.1 through 1.5. The rest are one-clause glosses.
