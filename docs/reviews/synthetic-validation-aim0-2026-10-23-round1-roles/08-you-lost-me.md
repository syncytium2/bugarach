GRANT 8 MISMATCH — missing none; holds Bash, PowerShell, Edit, Write, Agent, Artifact, Skill, Claude Docs batch/update and other tools beyond Read, Grep, Glob (general-purpose fallback spawn). I used only Read and Grep. I edited no files and wrote no scratch.

# Role 8: You Lost Me. Review of Aim 0 (docs/goals/synthetic-validation.md, lines 25–163 and 234–255, plus Figure 1)

## Per-slide verdict table

Here a "slide" is one section, table or figure. For each I list the terms and identifiers first used there, say which are defined there, and say whether a cold reader can follow it.

| # | Slide/panel | First used here | Defined here? | Cold reader follows? |
|---|---|---|---|---|
| S1 | §"Aim 0, first result", prose (l.25–53) | g_n, w, σ, R_n, E[·], (·)+, "closed form", factorial cumulants, "excess pair and triple cumulants", k, λ, N, "the coordination-rates tool", "the assessment", K, "chance clusters", "the tool's merging", "Poisson treatment", "0.1 s frame", "cell" meaning a grid condition, `theory.py`, `check()`, `theory_check.json` | Defined: g_n, w, R_n. Loosely defined: σ. **Not defined:** E[·] and (·)+, factorial cumulant, excess cumulant, k, λ, N, coordination-rates tool, assessment, K, "the tool's merging" | **BLOCKING** (10 or more undefined terms) |
| S2 | §"Aim 0, replicated blind", prose (l.55–62, 73–104) | "independent agents", blind A/B, `1000 + seed`, "five background draws", `aim1_one_source_shared_seeds.json`, Charlier polynomials, "signal-to-noise figure", "chance floor", ADR-0008, `window_floor`, "count detector", Fisher information, Cramér–Rao, scan statistics, "dimensionless groups", b (in N·b·w), f3, "rate", "the correlogram" | Defined: blind A/B (from context). **Not defined:** why "five", Charlier, chance floor and ADR-0008, `window_floor`, count detector, b, f3, which "rate", correlogram (first introduced at l.186) | **BLOCKING** |
| S3 | Table "All three reached…" (l.64–71) | "at-most-one-event term", k_hat, g_3/g_2, "window must exceed jitter" behaviour, q in "60 q (1 − q)^2", "as a rank question" | **Not defined:** at-most-one-event term, k_hat, q, the reason for the (1 − q)^2 factor, "rank question". The "window must exceed jitter" behaviour points forward to l.178 | **BLOCKING** |
| S4 | §"Aim 0, membership and order", prose (l.106–162) | assembly, M, E, "dispersion", s, σ (the event's jitter), τ = s/σ, SPIKE-order, synfire indicator F, "score sort", O(N²), N!, "adaptive windows", n̄, "fast ρ −0.75", "order-free control", "exchangeable limit", PySpike, venv, Aim 1b/1c, `synfire_scan.py` | Defined: M, E, s, τ, n̄, score sort, F (loosely). **Not defined:** dispersion (variance over mean?), "fast", ρ, order-free control, exchangeable limit. "Against" in "X against Y" never says which number is the prediction | **BLOCKING** (5 or more) |
| S5 | Table "Three properties…" (l.115–119) | "the chance floor", `bugarach.assembly`, `tools/synfire_scan.py`, "population-count tool" | Chance floor is not defined (nor in S2). Code paths stand where concepts should | no |
| S6 | Table "case / prediction / check" (l.137–141) | arctan/arcsin forms, "check (33 cells, 10 per event)" | Formulas are given. The order of "X against Y" (predicted or measured first?) is not | no. Fix the order and it is yes |
| S7 | Plan bullet "Aim 0: predict first" (l.234–255) | low-rank structure, random-matrix threshold, "score-sort indicator", "noise model", "closed-form floor", dimensionless axes, Cramér–Rao, "combined participation term", "at least K of k jittered onsets", binned SCE, CoactDetect, LoCo, "rolling context, merge gaps" | SCE, CoactDetect and LoCo are named in the Settled table but never explained. K and k are both used in one sentence with no definitions | **BLOCKING** |
| F1 | Figure 1, whole | "coordination rates" and "assess" in the legend, K, "(Aim 0)", participation "0.15/0.3/0.6", "event count (15/45)" | The caption defines the medians, the bars and the grey and coloured dashed lines. Participation and event count have no units. The legend says "assess" while the text says "the assessment" | yes, with the issues below |

Per-panel sentences: what a cold reader sees, with the caption covered.

**What it resembles:** a small-multiples parameter-recovery plot. Log-log axes, a ratio against a planted value, a reference line at 1. In that idiom the axes mean the same as they do here, so it is not a false friend. ✓

- **Top row (0.01 Hz).** (a) Participants: coloured lines hug 1, and the blue line (1 s window) sags to 0.4 at 1 s jitter. (b) Events per min: lines near 1–1.5, and the green line (K = 6) dives to 0.3 with a bar that runs off the axis. (c) Coordinated share: every line is flat at 1. (d) Jitter: the assessment lines fall from 3.5× to 0.7×, while the purple fit rises from 0.5× to 1×.
- **Bottom row (0.05 Hz).** Same layout. In (b), the yellow (K = 3) and pink (K = 4) lines sit flat at 16× and 8×. In (d), the assessment lines fall from 14× to 0.7× and the purple fit starts at 0.15×.
- I could write a sentence for every panel, so no panel is unreadable.

## Findings

Each finding gives location · issue · severity · suggested fix · whether I could check it against a source.

1. **S1, S2, S4: "cell" has two meanings, sometimes in one sentence.** l.37 "in every cell" means a grid condition. l.47 "the weakest cells (5 cells per event…)" uses both meanings at once. l.85 "within one cell" could mean one neuron or one grid cell. To a neuroscientist, "cell" means a neuron. · **major** (misleads a reader who is following closely) · Call grid conditions "conditions" or "grid points" throughout, and keep "cell" for neurons. · yes (the text)

2. **S1: core vocabulary used before it is defined.** "The coordination-rates tool" and "the assessment" are first explained at l.212–214, about 180 lines later, and only by code name. k, λ and N are never defined anywhere (from context they are participants per event, event rate and number of cells). · **blocking** · At the top of §Aim 0, add a short "symbols and tools" list: k participants per event (cells), σ onset jitter SD (s), w window width (s), λ event rate (events/min), N cells, b background rate (Hz per cell), K the assessor's threshold (cells); plus one line each on what the coordination-rates tool and the assessor measure. · yes

3. **S1, S5: "the assessment", and K as an absolute count, both go against GLOSSARY.md.** The glossary (l.205–207) says the machine half is "the assessor" and to never write "the assessment says". It defines K (l.196–204) as a percentage of the recording's region-of-interest (ROI) population, and says an absolute K is not comparable across recordings. The text writes "K = 3 or 4 at 0.05 Hz is swamped" as if K were the glossary's K. A reader who knows the glossary takes 3 to mean 3 %. · **major** · Write "the assessor" and "K = 3 cells (an absolute count, of 33 cells)". Note that this synthetic sweep uses absolute K. · yes (GLOSSARY.md l.196–207)

4. **Taken to mean: "replicated blind", "independent agents", "All three reached the same core answer independently", "Disagreements: none on substance" (S2).** A PI reads "replicated blind" as independent confirmation by other investigators. In fact these were two more instances of the same model family, given the same question and the same code pointers. Correlated blind spots are likely, and the first row of S3 says this session got the result only "on a second try". · **major** · State it as work done: "two more Claude sessions, given only the question and the code, derived…". Add that agreement among same-model agents is not external review. Keep "not reviewed" in the heading. · yes

5. **Taken to mean: "The coordination-rates tool is predicted exactly" (S1, l.34) and "matching `window_floor` exactly" (S2).** "Exactly" here means an exact closed form. The match to simulation is within 0.03, and worst 0.11 at 0.05 Hz. · **minor–major** · Write "has an exact closed form; it matches the simulation within …". · yes

6. **Taken to mean: "Membership is read perfectly here" (S4, l.126).** It means the check assumes perfect membership detection, not that a tool reads membership perfectly. · **major** · Write "This check assumes every member is detected and no background cell joins by chance". Give the shrink factor rather than "a factor blind pass B derived". · yes

7. **Taken to mean: "How does this compare with Kreuz…" is answered with "Against the brute force: `synfire_scan.py` anneals…" (S4).** The comparison is with this repository's own implementation, not with Kreuz's published method. The text does say PySpike was not compared, but only after the claim. · **minor** · Open the paragraph by naming the comparison as "against our `synfire_scan` implementation", before the ⚠ caveat. · yes

8. **Text and Figure 1 disagree on the fitted jitter (S1, l.40–43).** "Planted 0.2… come back as about 0.17… at both backgrounds" does not match what I read off the bottom-row purple line: about 0.72× at 0.2 s, roughly 0.14 s. "Planted 0.05 s reads about 0.02 s" matches the top row (≈0.5×), but the bottom row shows ≈0.15× (≈0.008 s). The cold reader who checks the figure is lost. · **major** (agent 2/4 own the numbers; flagged because the reader stalls here) · Give per-background values, or say "at 0.01 Hz". · yes (figure render)

9. **S3: q is undefined in "60 q (1 − q)^2 per minute".** The (1 − q)^2 factor (the merging rule) is unexplained, and so are k_hat, g_3/g_2 (defined in another section) and "the at-most-one-event term". · **blocking** (part of S3's blocking row) · Define q as the chance that one 1 s bin holds at least K onsets, say that (1 − q)^2 means both neighbouring bins are below K, write "estimated participants k̂" instead of k_hat, and point to the g_n definition. · yes

10. **S2: units are missing.** "At 33 cells it is 6 at 0.01 Hz and 12 at 0.05 Hz" has no unit (presumably cells). "within about 0.03" and "within a median 0.011 (worst 0.06)" (S1 l.37, l.51–52) could be cells or a ratio. "Rate 3–5 % above" does not say which rate. CLAUDE.md l.130 requires a unit on every number. · **major** · Add the units: "6 cells", "0.03 cells" or "0.03 of planted". · yes

11. **S2, S4: terms that are never defined.** "the chance floor" and "ADR-0008" (no link, no gloss), "exchangeable limit", "order-free control", "fast ρ −0.75" ("fast" and ρ), "f3", "b" in N·b·w, "count detector", "dispersion", "Charlier polynomials", "rank question", "low-rank / random-matrix threshold". · **blocking** (inside the S2/S4/S7 rows) · One clause each. For example: exchangeable limit means "cells interchangeable: no fixed membership, no order"; chance floor means "the smallest event size that beats chance (ADR-0008)"; ρ is Spearman correlation on the fast stream. · yes

12. **S4, S6: "X against Y" never says which number is the prediction** ("44.5 against 45.0", "0.503 against 0.500"). · **minor** · Use a "predicted / simulated" column pair, or write "predicted 45.0, simulated 44.5". · yes

13. **S7: K and k in one sentence.** "at least K of k jittered onsets" sets threshold K next to participants k, and neither is defined. · **major** for a non-statistician · Write "at least K (threshold) of the k participating cells' onsets", or rename one of the two symbols. · yes

14. **S1, S2, S4, S5: internal code identifiers in reader-facing text.** `check()`, `window_floor`, `theory_check.json`, `aim1_one_source_shared_seeds.json`, `bugarach.assembly`, `1000 + seed`, `derive_k`. File links can stay for future sessions, but the claims should not depend on them. · **minor** · Use the plain concept ("the chance-floor function", "the assembly recurrence test") and keep paths as links only. · yes (CLAUDE.md rule)

15. **S1: forward references.** It predicts and corrects "Aim 1a", "the reseeding below" and Figure 1 before the reader has met any of them (§Aim 1a is at l.164). · **minor** (ordering belongs to role 11) · Add one sentence at the start of S1: what Aim 1a simulated (one source, 240 recordings, 33 cells) and that Figure 1 is described at l.170. · yes

16. **S4: mechanisms named but not shown.** Score sort against annealing, and the "permuting which cell owns each onset" null, are given only in words. · **minor** · A small schematic (leader-to-follower raster plus a sorted matrix) would carry it. Reuse an existing synfire illustration if the project has one. · no (I did not search for one)

17. **F1: horizontal dodge and units.** Points are offset along log x (e.g. 0.9 against 1.05), which can read as different planted jitters. The column header "jitter, SD (s)" carries seconds while the y axis is a dimensionless ratio. The stacked y label "recovered ÷ planted / background 0.01 Hz per cell" can be parsed as "÷ planted background". · **minor** · Say in the caption that the offsets are for legibility, drop "(s)" from the header or write "jitter (ratio of SDs)", and split the row label from the axis quantity. · yes (render)

18. **F1: caption units and list style.** "participation (0.15/0.3/0.6)" and "event count (15/45)" have no units, and the slashes pack a list into the caption. · **minor** · Write "participation 0.15, 0.3 or 0.6 of cells; 15 or 45 events". · yes

19. **Tone.** Sentence case is consistent. ⚠ and bold are used sparingly. "signal-to-noise figure" (S2) clashes with "Figure 1" and should be "number". No ALL-CAPS. · **minor** · yes

## What I checked

Read in full: `08-you-lost-me.md`; synthetic-validation.md l.1–270; the GLOSSARY.md K and assessor entries (l.128–216); CLAUDE.md figure and writing rules (l.115–137). Viewed the Figure 1 render. I did not open theory.py, the blind scripts or ADR-0008, so I did not check whether the S2/S3 formulas are correct (that is roles 2/4).
