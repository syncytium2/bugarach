GRANT 8 MISMATCH — missing none; holds Edit, Write, NotebookEdit (deferred), Bash, PowerShell, Agent, Artifact, Skill and others beyond Read, Grep, Glob

This is a finding about the run, not the artifact. I used only Read, Grep and Glob, edited nothing and read nothing under docs/reviews/. The run record's `roles:` line should say role 8 ran on a fallback path.

**Role 8, "You Lost Me": naive-reader review of `<repo>/docs/dissertation/chapter-1-aim0.md`.** I opened all 19 figures as images before reading their captions.

## A. Per-section and per-figure verdicts

"Undefined" means the term is used before it is defined, or is never defined, for a scientist outside this subfield. A row with three or more undefined terms is blocking under the rule.

| unit | terms first used here | defined here? | can a cold reader follow? |
|---|---|---|---|
| Header note | ⚠ | yes | yes |
| 1.1 The problem, Fig 1.1 | recording, frame, calcium event, onset, channel, raster, background, coordinated event, participation, jitter, latency template, source | all defined. Not defined: "the lab" (Fig 1.1 caption, "the lab's typical rate"). "the repository" is used two paragraphs before "'the repository' below means…" | yes |
| 1.1 How the chapter proceeds | cross-cell correlogram, pair and triple counts | forward pointers | yes |
| 1.2.1–1.2.2 | bin, threshold K, merge gap, count detector, sliding window | yes | yes |
| 1.2.3 | Poisson, binomial, chance floor, CFAR, reference/guard cells, cell under test, masking, clutter edge | yes. Not defined: "up-crossing"; "train" ("each cell's whole train shifted"), which is later also used for the *event* train | yes, with effort (see B4) |
| 1.2.4, Fig 1.2, Table 1.1 | false alarm, found, "by chance" | yes. Not defined: **m** in "(m + ½) bin widths" (situation 3), which is defined only in 1.7 | yes |
| 1.3.1 | stream, baseline segment, region of interest, Neyman–Scott, Thomas, hard-core | yes. Not defined: "arcuate kisspeptin neurons", "the goal page's working values", "the simulator's generator notes"; ⚠ attached to a value ("of 33 ⚠") | **BLOCKING: 1.3.1, three undefined (two of them internal repository sources)** |
| Fig 1.3 | coordination-rates tool, assessor, "±1.5 s gather" (in the figure only) | one-line forward definitions for the tools; the gather is not defined until 1.3.4 | yes, with effort |
| Fig 1.4 | HWHM, g₂ ("window sharing g₂ alone"), "run off its settings" | HWHM yes; g₂ forward; "run off its settings" no | yes |
| 1.3.2–1.3.4, Fig 1.5 | factorial cumulant, surrogate, null, assessor, cluster, jitter/null/excess reading | yes, and Fig 1.5 illustrates the surrogate, the nulls and the score sort graphically | yes |
| 1.4, Table 1.2, Fig 1.6 | condition, seed, first experiment, held-out rerun, joint fit (forward) | yes | yes |
| 1.4 How the predictions are tested | residual, refused, renewal train, pair correlation, stationary | yes | yes, with effort |
| 1.4 Prior work, "Order" paragraph | SPIKE-order, latency correction, direct shift, extrapolation direct shift | none of these | **BLOCKING: "Order" paragraph of Prior work, four undefined** |
| 1.4 Prior work, other paragraphs | fission probability, dithering, compound Poisson/carrier, minimum contrast, Ripley's function, Marčenko–Pastur, synfire chain | all glossed except Ripley's function | yes |
| Contributions | design effect, arcsine relation, Borda score | yes | yes |
| 1.5.1–1.5.3, Fig 1.7 | g_n, falling factorial, at-most-one-event term, hard-core form | yes | yes, with effort (see B5) |
| 1.5.4, Figs 1.8–1.9 | sign test, condition-window | yes | yes, apart from the "record" drift (B3) |
| 1.5.5, Fig 1.10 | general form, "empirical trains"; panel titles "one event per mean interval", "tabulated event counts" | none of the three | **no**: panel titles do not match any run name in the text (B2) |
| 1.5.6–1.5.7, Figs 1.11–1.12, Tables 1.3–1.5 | identifiable, calibration curve, bound, censored, "in band" | yes. Fig 1.11 C also says "tabulated event counts" | yes |
| 1.6.1, Fig 1.13 | cluster-start factor, Poisson-binomial, event floor, "budget" | yes. "budget" = 1.2.3's "allowance", unflagged | yes |
| 1.6.2, Fig 1.14, Table 1.6 | mixture, chance share | yes | yes |
| 1.7, Fig 1.15 | likelihood-ratio test, power, EM, τ_min, plateau; legend "test size", "(model as stated)" | text yes; legend terms no | yes, with effort |
| Fig 1.16 | "planned separation" (the chapter says "planted" everywhere else), "event floor (the count chance first exceeds)" | partly | **misleads** (B1) |
| 1.8.1, Fig 1.17 | assembly, reuse, Bonferroni, margin-preserving/uniform null | yes | yes |
| 1.8.2, Figs 1.18–1.19, Tables 1.7–1.8 | score sort, F, local search, randomized test, "lattice convolution"; "test size" in Fig 1.19 | mostly. "lattice convolution" no | yes |
| 1.9, Table 1.9 row "exact no-order mean of F" | Durbin's incomplete-block test, Skillings–Mack form, W ("√W") | none of the three | **BLOCKING: Table 1.9, that row** |
| 1.10, About this chapter | — | — | yes (but see B6) |

**False-friend check** (what each image resembles, with the caption covered). Figs 1.1, 1.2 B, 1.3 A–C, 1.4 A–B and 1.5 A are genuine rasters: time across, one cell per row. Fig 1.5 B draws the membership matrix as gridded tiles, so it cannot be mistaken for a raster. Fig 1.4 C is a standard correlogram.

The only near miss is Fig 1.9. Its x axis is categorical, but the evenly spaced numeric tick labels (0.0125 … 0.1, 0.125, 0.2 …) read as a numeric, log-like axis. The caption says "categorical"; the axis label does not. Minor.

**Can a stranger say what each panel shows?** For every panel I could write the sentence "what a cold reader sees". Two panels show structure the caption does not explain:
- **Fig 1.16:** the predicted count-detector curves oscillate with a period of about 2 s beyond 5 s separation. A reader will ask whether this is real.
- **Fig 1.6 E:** the assessor reports roughly half the planted participants at K = 3 and 4 (0.05 Hz). Neither the caption nor the three numbered failures mention it; only 1.9.1 says it is not predicted.

## B. Findings

Format: location · issue · severity · suggested fix · could I verify it against a source?

1. **Fig 1.16 caption** · The caption says "Events of 7 cells rarely reach 8 or 12, so the 0.05 Hz panels for 7 cells stay near 0." Panel B (σ = 0.105 s, 0.05 Hz) shows the assessor with 7 cells (blue) plateauing at about 0.37. Only the count detector with 7 cells, and panel D, stay near 0. A reader who trusts the caption misreads panel B. · major (misleads) · Restrict the sentence to the count detector and to the σ = 0.5 s panel, or state the panel B plateau. · yes (the rendered figure)

2. **Fig 1.10 panel titles and Fig 1.11 C title** · The panels say "one event per mean interval" and "tabulated event counts". The text calls the same runs the "denser-train check" (about 3.5× the pooled rates) and "at the pooled rates". A cold reader cannot map the panels to the runs named in the text. · major · Use the text's names ("denser trains: 25.5 / 53.6 events"; "at the pooled rates: 7.3 / 16.5 events") in the figure titles and the caption. · yes

3. **"record(s)" vs "run(s)"** (Figs 1.9 and 1.12 legends "first experiment / held-out record", "resolved on both records"; text 1.5.4 "16 conditions × 2 records") · The text names "the held-out rerun" and "two runs", and also uses "run record" for a documentation file. Three meanings of "record" are in play. · minor · Use "run" everywhere for the two simulation runs. · yes

4. **1.2.3, chance-floor paragraph** · Two sentences lose a non-specialist:
   - "counts every up-crossing and so errs toward a higher floor": up-crossing is undefined, and the reason it errs high is not given.
   - "both are integers, so this is agreement at two points, not a test of the formula's shape": a hedge written for a reviewer that a cold reader cannot parse.

   "train" is also used here before it is defined, and later for the event train. · minor · Define "train (a cell's list of onsets)" once; say "counts each rise to K separately, even when calls would be merged"; move the integer caveat to a footnote. · yes

5. **Fig 1.7** · Panel A's x axis is w/σ and panel B's, side by side, is σ/w. The curves run in opposite directions for the same physics. The legend's "full prediction" is called "the hard-core form" in the caption ("Yellow dashes"; the mark is orange-gold). The vertical "2√3 σ" line in A is not in the caption. · minor · Put both panels on the same ratio, or say in the caption that B is inverted. Use one name for the dashes. · yes

6. **What a sentence will be taken to mean: 1.10 Conclusion, "A realistic 20-minute baseline segment supports, for one source: participants … jitter, not at all …"** · A reader who reads only the conclusion, or who forgets 1.3.1's rule that "realistic" values "only choose where to simulate", reads this as a statement about the lab's real segments. It is a simulation result at the lab's parameter values. · major · "A simulated 20-minute segment at the lab's parameter values supports …". · yes (1.3.1, "no statement in this chapter is about the recordings themselves")

7. **Taken to mean: 1.1, "Chapter 1, this one, builds and checks the tools that measure coordination"** · This credits the chapter with building the coordination-rates tool, the assessor and the correlogram tool. These are pre-existing repository tools; the chapter derives what they return and adds the joint fit. · minor · "derives and checks what the repository's measuring tools return, and adds one (the joint fit)". · partly (the text itself calls them "the repository's tools"; I did not check code history)

8. **⚠ used outside its declared meaning** (1.3.1 "of 33 ⚠"; 1.9.4 item 2 "from error in the theory ⚠") · ⚠ is defined as marking references not opened. Attached to a value or a claim, the reader cannot tell what it flags. · minor · Use a separate mark or words ("unverified"). · yes

9. **Internal sources in audience text** (1.3.1: "the goal page's working values", "the simulator's generator notes"; 1.5.6 onward: "shipped", "as shipped", "how it ships", 12 uses) · These are repository vocabulary. "Shipped" means "the tool's released default" to a software reader and nothing to a biologist. · minor (but part of the 1.3.1 blocking row) · Cite the run record or drop the source note; define "as shipped (the tool's default settings)" once. · yes

10. **"Order" paragraph of Prior work (blocking)** · SPIKE-order, latency correction, direct shift and extrapolation direct shift are named without any gloss. · blocking per the three-term rule · Gloss in one clause ("latency correction: shifting each train to align events") or cut the method lineage to one sentence. · yes

11. **Table 1.9, row "exact no-order mean" (blocking)** · Durbin's incomplete-block test, the Skillings–Mack form and W are named bare. · blocking per the three-term rule, though this table mainly serves methods reviewers · Add "(Kendall's coefficient of concordance)" after W and one clause for the incomplete-block test, or move the lineage to a footnote. · yes

12. **"the lab"** (first use: Fig 1.1 caption) · The lab is not identified until 1.3.1. "arcuate kisspeptin neurons" is never glossed for an outsider. · minor · At first use: "the DeFazio lab's recordings (1.3.1)"; one clause on what the neurons are. · yes

13. **Fig 1.4 C y-axis, "onset pairs ÷ independent cells"** · Read literally, this is a count divided by a number of cells. · minor · "onset pairs ÷ pairs expected if independent". · yes

14. **Fig 1.15 legend** · "(model as stated)" and "test size" are undefined. The caption says "false-alarm rate". · minor · "minimum interval one frame"; "false-alarm rate above 7.5 %". · yes

15. **Fig 1.16 x label "planned separation"** · Every other place in the chapter says "planted". The footnote line "the event floor (the count chance first exceeds)" contradicts 1.6.1's definition ("smallest count chance reaches at most once per hour"). · minor · Write "planted separation", and quote 1.6.1's definition. · yes

16. **Unexplained structure** · The oscillating prediction lines in Fig 1.16 and the assessor's participant undercount in Fig 1.6 E (described under section A) are neither explained nor pointed to in their captions. · minor · One sentence each: why the bin phase makes the curve wiggle; "assessor participants are not analysed (1.9.1)". · yes (rendered figures)

17. **1.2.4, situation 3** · "about (m + ½) bin widths" uses m about 20 sections before 1.7 defines it. · minor · "(m + ½) bin widths, where m is the merge gap in bins". · yes

18. **Tone** · Sentence case is consistent and there is no ALL-CAPS. Bold is heavy but used as run-in heads. No list items are smuggled into titles. · none · — · yes

**What I checked:** the whole chapter, section by section; all 19 figures opened as images before their captions; all 9 tables; the "About this chapter" note; and a LICENSE check (`<repo>/LICENSE` exists, so the "open-source" claim stands).
