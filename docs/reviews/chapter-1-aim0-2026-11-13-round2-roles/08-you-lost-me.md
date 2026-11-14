GRANT 8 MISMATCH — missing none; holds Edit, Write, Bash, PowerShell, Agent, Artifact, Skill, ToolSearch, Claude Docs batch/update (NotebookEdit can be loaded through ToolSearch)

This is a finding about the run, not the artifact. The harness gave this reviewer editing and shell tools that the role does not allow. I used only Read, Grep and Glob, edited nothing, and read nothing under docs/reviews/. The run record's `roles:` line should say this role ran on a fallback grant.

# Murderboard role 8 ("You Lost Me"): Chapter 1, blob 0acfccbb

**Surface examined:** I read all 1,745 lines of `<repo>/docs/dissertation/chapter-1-aim0.md`, section by section, as a scientist from outside this subfield. I opened all 19 figure PNGs as images and looked at each one before reading its caption. I also read `docs/writing_conventions.md` and the role file. The words "toy" and "fire" do not appear in the chapter. The figures that most needed to be readable are, overall:
- Figures 1.1 and 1.2: a real raster, a clear legend for found, missed and false alarm.
- Figure 1.3 B/C: the onsets of one event cut by a window border into 4 + 6.
- Figure 1.5: the membership matrix drawn as gridded tiles, and a worked example of the order indicator.

The opening the owner asked for, problem first and then the simple detectors, works for a cold reader up to about 1.3.4. From 1.4 on it degrades into run-history, internal plumbing and words that change meaning partway through.

## A. Highest-priority findings (each one loses or misleads the target reader)

| # | location | issue | severity | suggested fix | verifiable vs source? |
|---|---|---|---|---|---|
| A1 | 1.5.7 text (lines ~1061–1068), Table 1.5 caption ("by events per window E"), and 1.5.7's last paragraph ("eight events per window", "16 events per window") | **"Window" changes meaning.** Everywhere else, *window* is the counting window w (1, 2 or 4 s). In 1.5.7 it silently means the 20-minute baseline segment: "At a median window (one fast or two slow events)", "Jitter is not readable per window", "E = 1…16 events per window". A reader who follows the chapter faithfully reads "16 events per window" as 16 events inside a 1–4 s window, which is impossible after "events at least 20 s apart". | blocking (the reader is misled) | Replace every such use with "segment" (the term 1.3.1 defines). | yes (Grep "per window") |
| A2 | 1.7, first line: "Situation 3 of Figure 1.2 showed two events **3 s** apart" | Figure 1.2's caption, Table 1.1 and item 3 of 1.2.4 all say **4 s**. A reader going back to the figure finds a different number and stops trusting the cross-references. | high | Change "3 s" to "4 s". | yes |
| A3 | 1.4 "What brute force found" (lines 504–512); later "held-out rerun" (607); "An earlier run at about 3.5 and 3.3 times…" (627) | **Too many runs, with clashing names.** "The first experiment" is actually the *rerun* of a first run that had a shared-seed flaw. "Rerun" is then used again for the held-out rerun, and a third "earlier run" appears in 1.4. The figures add "record": "held-out record" and "both records" in Figure 1.9; "resolved on both records" in Figure 1.12. In the text, "16 conditions × 2 records" at line 852 means *runs*. Yet "run record" also means a provenance file. A cold reader cannot tell how many independent simulations exist. | high | Name the runs once in a small list: discarded first run (shared seeds; no numbers used) · **first experiment** · **held-out rerun** · **denser-train check**. Use only those names, and replace "record(s)" with "run(s)" in Figures 1.9 and 1.12 and at line 852/919. | yes |
| A4 | Line 576 (1.4 "answer in brief") | "On the held-out rerun the residuals exceed sampling noise" is used about 30 lines before the held-out rerun is defined (line 607). | medium | Move the definition up, or gloss it here ("a second run of the same grid on fresh random draws"). | yes |
| A5 | Chapter title, "Predict first, simulate to check", and the 1.4 slogan | **What a true sentence will be taken to mean.** A reader takes the title as the order in which the work was done: predictions written down, then simulation. The chapter's own account is the reverse. A brute-force grid found failures, the derivations came afterwards, and some model choices were tuned while looking at that grid, which is why the held-out rerun exists. The title credits the work with a pre-registration it did not have. | high | Make the title say what was done, e.g. "Deriving what the tools return, checked by simulation". Or keep the slogan as the *proposed method* and add one sentence in 1.4 saying that in this chapter the derivation followed the first simulation and was then tested on a held-out rerun. | yes (1.4 text) |
| A6 | 1.1, line 41–42: "Chapter 2 builds simulated data from the participation, jitter and event rate **measured here**" | The reader takes this to mean that Chapter 1 measured those properties in real recordings. Line 253 says "no statement in this chapter is about the recordings themselves." | medium | Say "…from the participation, jitter and event rate that the tools characterized here measure". | yes |
| A7 | 1.3.1 "realistic values" (lines 248–266) | A reader takes "realistic" as trustworthy ground truth. The chapter does not say **which tool produced each realistic number**, for example whether the 0.105/0.131 s jitter came from the correlogram tool or the assessor. Two things make that matter: 1.6.2 shows the assessor's jitter reading is biased, and 1.3.1 says the interval lists came from a detector that merges close events. The citation (DeFazio et al. 2026) sits next to the list, so the reader may also infer that the published paper reported these values. | medium | Add the source tool to each bullet. State whether the published paper or the repository's run record is the source of each number. Add one line on whether this chapter's findings bear on any of them. | no (provenance not checked) |
| A8 | 1.3.3, lines 395–397 | "Cumulants are the combinations that add across independent processes, so the background's contribution drops out." This does not follow: adding does not make a term vanish. The missing step is that **a Poisson count has zero factorial cumulants of order 2 and above**, so independent Poisson background contributes zero. Without it, the reader cannot see why f₂ measures only coordination. | high (this is the step the chapter's mathematics rests on) | Insert: "For a Poisson count every factorial cumulant beyond the mean is zero; because cumulants add across independent sources, the background contributes nothing to f₂ or f₃." | yes |
| A9 | 1.5.6, first paragraph | **The joint fit is named but never defined.** "Fitting those six numbers against the exact forms above" never says what is minimized (least squares? on what scale?) or which "exact form" (hard-core or general). Only later, from figure legends, does the reader learn there are two variants. | high | Add one sentence: "minimize the sum of squared differences between the six measured counts and the hard-core (or general) form, each count divided by its mean absolute value, over (σ, k, λ)". | yes |
| A10 | 1.4 "How the predictions are tested", lines 627–631 | Internal plumbing in audience-facing text: "placed by the follow-up scripts rather than through the simulator's own measured-interval option…the simulator's fixed-count placement is not". The reader learns of a simulator option, a placement mode and follow-up scripts. None of them is defined, and none changes the result. | medium (blocking count: 3 undefined) | Cut, or move to *Reproducing*. Keep only: "these trains were built so that their statistics are constant over the recording, which the general form requires." | yes |
| A11 | Figure 1.10 caption (line 910) | A repository file path, `separation/real_intervals/intervals_results.json`, appears in the caption. That breaks the rule against internal identifiers in audience text. | low | Remove it; *Reproducing* covers it. | yes |
| A12 | 1.8.1 "assembly" | "Assembly" is a loaded neuroscience term: a Hebbian, synaptically bound group. A neuroscientist reader will import that meaning. Here it only means a fixed set of cells that join the same events. The word is never defined in plain terms. | medium | At first use: "an **assembly** here is simply a fixed set of k cells that join the same events; nothing about connections between them is implied." | yes |

## B. Per-section verdicts

Columns: section · terms first used there · which are defined there · can a cold reader follow it (yes / no / **blocking** = 3 or more undefined).

| section | terms first used | defined here? | follow? |
|---|---|---|---|
| 1.1 problem + Fig 1.1 | recording, frame, calcium event, onset, channel, raster, background, coordinated event, SD, participation, participants, jitter, latency template, baseline | all | **yes**. The figure is a proper raster and reads cold. See A6. |
| 1.1 "How the chapter proceeds" | cross-cell correlogram, pair/triple counts | named, defined later (flagged as later) | yes |
| 1.2.1–1.2.2 | detector, call, planted, bin, threshold K, merge gap, count detector, sliding window | all | **yes** |
| 1.2.3 CFAR | Poisson, Hz, binomial, chance floor, reference / guard cells, cell under test, masking, clutter edge | all except "up-crossing" (inferable) | yes. The radar sense of "cell" is defined, which is good. |
| 1.2.4 + Fig 1.2 + Table 1.1 | false alarm, "by chance" share | all | **yes**. This is the clearest part of the chapter. |
| 1.3.1 | stream, realistic, baseline segment, Neyman–Scott, Thomas process, hard-core | all | yes (see A7) |
| Fig 1.3 | coordination-rates tool, assessor, count detector | forward refs | yes. Note: cell 1 is at the **top** here, but at the **bottom** in Figs 1.1, 1.2 and 1.4. The caption admits it; better to flip the figure for consistency. |
| 1.3.2 + Fig 1.4 C | lag, C₀, φ(τ; s), HWHM, d, bootstrap standard error | all but **bootstrap SE** (first defined at Fig 1.10, line 908) | yes. Define bootstrap SE at line 365. The Fig 1.4 C y-label "onset pairs ÷ independent cells" is garbled; use "÷ expected if cells independent". |
| 1.3.3 | f₂, f₃, factorial moments/cumulants, k̂, coordinated onset rate, g₂, surrogates, null | mostly | no until A8 is fixed |
| Fig 1.5 | surrogate shift; margin-preserving / uniform null; score sort; F | all, by illustration | **yes**. This is a model figure for the "illustrate, don't name-drop" rule. |
| 1.3.4 | distinct active cells, assessor, cluster, gather, jitter / null / excess reading | all | yes |
| 1.4 brute force + Fig 1.6 + Table 1.2 | conditions, seed, refused | yes | no (A3). In Fig 1.6 E the assessor's participants sit at about 0.5 at every jitter, and neither the caption nor the text explains it. Add a line, or point to 1.9.1 ("not predicted"). |
| 1.4 "question / answer in brief" | Aim 0, held-out rerun, joint fit | Aim 0 yes; held-out rerun no (A4) | partly |
| 1.4 "How tested" | residual, "signed", "shipped report…on that path", renewal train, pair correlation, stationary, follow-up scripts, measured-interval option, fixed-count placement | first five yes; last three no | **blocking** (A10) |
| 1.4 Prior work | scan statistics, cell-averaging / greatest-of / ordered-statistic CFAR, fission probability, dithering, compound Poisson / carrier, minimum contrast, Ripley's pair-count function, Marčenko–Pastur, synfire chain, SPIKE-order, interictal spike propagation, replay | about half | **blocking** for a non-subfield reader: dithering, minimum contrast, interictal, replay and greatest-of are undefined. Give each a short clause, or cut the ones that do no work. |
| 1.4 Contributions | closed form g_n, event-train term, surrogate term, **cluster-start factor**, Kish design effect, **arcsine relation**, Borda score, "one-template value" | Kish and Borda glossed inline; cluster-start factor (defined only in 1.6.1), arcsine relation and one-template value are not | **blocking**. Either move Contributions after the results (1.9), or gloss each term in one clause. |
| 1.5.1–1.5.2 + Fig 1.7 | range R_n, Φ, φ, a = w/s | yes | yes. φ is overloaded: φ(τ; s) in 1.3.2, the standard density φ(a) here. The Fig 1.7 B legend says "full prediction" where the caption says "hard-core form"; use one name. |
| 1.5.3 | falling factorial, at-most-one-event term, hard-core form | yes | mostly. "The surrogate's own pair count 4–15 times the independent value" is unclear: independent value of what? Two sources: yes. |
| 1.5.4 + Figs 1.8, 1.9 | sign test, condition-window, "beyond 2 SE", dependence-aware p | sign test yes; condition-window inferable | yes, but dense. Fig 1.9's evenly spaced categorical σ/w ticks look like a log axis; the caption warns, which is acceptable. |
| 1.5.5 + Fig 1.10 | general form, empirical train | yes | yes. The Fig 1.10 and 1.11 C panel titles say "tabulated event counts" where the text says "pooled rates"; use one term. A11. |
| 1.5.6 + Fig 1.11 + Table 1.3 | joint fit, identifiable, Fisher information, calibration curve, censored | yes, except what the fit minimizes (A9) | no until A9 is fixed |
| 1.5.7 + Fig 1.12 + Tables 1.4, 1.5 | "in band", "at bound", "window" = segment | the first two yes; the window collision misleads | **blocking** (A1) |
| 1.6.1 + Fig 1.13 | q, cluster-start factor, ν_c, Poisson-binomial, event floor, rigid-shift null, over-dispersed, recall, π_K | yes | **yes** |
| 1.6.2 + Fig 1.14 + Table 1.6 | chance share, mixture, semi-analytic | yes | yes. Fig 1.14 writes c/(c + e) where the text uses ν_c/(ν_c + ν_e); align them. Table 1.6 has its unit (s) only in the caption, which is agent 10's check. |
| 1.7 + Figs 1.15, 1.16 | likelihood-ratio test, power, EM, τ_min, **plateau**, **merge rule m**, **half-split point**, **test size**, "**model as stated**", "membership-known test", "planned separation" | the first four yes; the rest no | **blocking**. Define the plateau: "the chance both events of a far-apart pair are each detected, π_K²". Replace "half-split point" with "the separation at which half of the plateau is reached". In Fig 1.15's legend, use "false-alarm rate" instead of "test size" and drop "(model as stated)". In Fig 1.16, change "planned" to "planted". The Fig 1.16 footer's "the count chance first exceeds" contradicts the text's definition of the event floor. |
| 1.8.1 + Fig 1.17 | assembly (A12), reuse, co-participation, co-activation, leading eigenvalue, Bonferroni, perfect readout, deft², roh | most | yes after A12. Kish's notation (deft², roh, n/a) can be cut to "the form of Kish's design effect". |
| 1.8.2 + Figs 1.18, 1.19 + Tables 1.7, 1.8 | Synfire Indicator, score sort, F, local search, Kendall's τ, n̄, randomized test, **test size**, simulated annealing | all but test size and annealing | yes. Fig 1.19 says "exact-size 5 % test" and "test size": gloss once as "the false-positive rate, 5 %". |
| 1.9.1–1.9.5 | (back-references) | n/a | yes. Table 1.9's column header "status" actually holds precedents; rename it "nearest precedent". In its last-but-two row, "Durbin's incomplete-block test in Skillings & Mack's form" and "Kendall-τ analogue of √W" are opaque to this reader. |
| 1.10 | none new | n/a | **yes** |
| About this chapter | "Revision of 2026-11-13", "earlier version" | | Readable. "No number from the earlier version changed" means nothing to a reader who never saw that version; keep it only in the run record. |

## C. Figures read cold: what a cold reader sees

- **1.1:** three rasters (background, events alone, combined) with four blue triangles. Readable. No false friend: this is a true raster.
- **1.2:** event numbers above detector lanes of green, red and orange triangles; a raster; 2 s bin bars against a dashed line; a sliding-count trace with a violet stepped CFAR threshold. Readable.
- **1.3:** a raster with two events, and zoomed panels showing a 1 s border splitting 4 + 6. Readable, except that the cell order is flipped (cell 1 at top) relative to every other raster.
- **1.4:** two sharp-vs-jittered raster snippets, a tall narrow peak against a short wide one, S-curves against window width, and tail curves against K. Readable. C's y-label is garbled.
- **1.5:** a surrogate shift drawn on 4 cells, tile matrices with orange swaps, and a lead table. Readable. The best figure in the chapter.
- **1.6:** an 8-panel grid of recovered÷planted against jitter. Readable with effort. Flat yellow and pink lines in F and H stand out; the participant panel E is unexplained.
- **1.7:** two S-curves (g₂, g₃) and falling k̂/k curves with points. Readable. Legend and caption name the yellow marks differently.
- **1.8:** measured-vs-predicted scatters on the identity line. Readable.
- **1.9:** residual dot-and-whisker strips, two colors. Readable, but the header text is long and says "record".
- **1.10:** dumbbells (open to filled) on identity lines. The legend reuses a filled gray circle for both "general-form prediction" and "fast stream", which confuses. The title says "tabulated".
- **1.11:** medians with interquartile-range bars, and strip plots with a cluster of points sitting on the bound. Readable.
- **1.12:** a grid of resolved / unresolved circles with two shaded boxes. Readable. Legend says "records".
- **1.13:** chance-cluster rate falling with K, with a budget line. Readable.
- **1.14:** four panels, a mixture line between the chance level and the event curve. Readable. Notation differs from the text.
- **1.15:** resolvable separation against k for four test types, plus power curves. Hard to read: "test size", "model as stated", "half its split plateau" and "membership-known" are all undefined.
- **1.16:** step curves of P(reported as two) against separation. Readable, but "planned" should be "planted", and the 7-cell plateau below 1 is unexplained in the caption.
- **1.17:** a variance ratio rising with reuse, and detection share. Readable.
- **1.18:** three log-log panels, closed forms with points. Readable for this audience.
- **1.19:** power curves against E. Readable. "Test size" is undefined.

No false-friend idioms were found. The membership matrix (Fig 1.5 B) is drawn as bordered tiles, not marks scattered over continuous axes. No panel shows phantom structure.

## D. Tone

- Sentence case is consistent throughout.
- No all-caps emphasis.
- Lists are formatted as lists.
- One run-on sentence in 1.2.4 item 4: "four of the five false alarms fall within 13 s of its ends. Section *1.6.1*…" runs past the normal line wrap. Line-editor territory, noted only.

## E. Summary

The chapter has six **blocking rows**:
- 1.4 "How tested"
- 1.4 Prior work
- 1.4 Contributions
- 1.5.7
- 1.7 with Figs 1.15 and 1.16
- Table 1.9

It has three **misleads**, places where a reader follows the sentence and lands somewhere false:
- the title (A5)
- "measured here" (A6)
- "window" meaning segment (A1)

Fix A1, A2, A3, A8 and A9 first. These are what stop a cold reader from following the argument after 1.3.
