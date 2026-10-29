GRANT 9 MISMATCH — missing none; holds Edit, Write, NotebookEdit (deferred), plus PowerShell, Agent, Artifact, Skill, ToolSearch and the write-capable Claude Docs batch/update tools

(A finding about the run, not the artifact. No editing tool was used. The only file written was a word-count script in my own scratch folder.)

# Role 9: Density and figure-first ("Show, Don't Tell"). Round 3 blind verify, Chapter 1 (Aim 0)

Artifact: `docs/dissertation/chapter-1-aim0.md`, hash-object a4fbb30ebe9e70313f10034927ccf32341948290 (confirmed). I read the whole chapter and opened all 14 embedded PNGs with Read. I did not open any earlier review or git history.

## Thresholds used, adapted from slides to a dissertation chapter

These are conventions, not optima.
- **Unit ("page")** = a numbered subsection.
- **Words:**
  - Flag a Results or Methods subsection with more than about 450 words of running prose (about one printed page) and no figure.
  - Flag any single paragraph or list item over **150 words**. The slide threshold of 60 words does not transfer to a thesis.
- **Results or methods subsection with no figure**: flagged. A table alone counts as "no figure".
- **Two or more consecutive prose-only subsections** within Results or Methods: flagged.
- **Figure share:** markdown renders every figure at column width, so share of the page is fixed. The analogue I measured is the share of each rendered PNG given to data panels, as opposed to legend, in-canvas prose, whitespace or panels that repeat another figure. Flag below about 50%, or where half the canvas repeats content found elsewhere.
- **Captions** over **150 words**: flagged, on the rule that a caption is a caption.
- **A table that repeats a figure** (same numbers): flagged.

## Count table

Prose words exclude captions, tables and display equations.

| § | prose words | largest block | figure | data-panel share of the figure(s), estimated from the render |
|---|---|---|---|---|
| 1.1 Problem | 212 | 99 | n | – |
| 1.1 Brute force | 307 | 128 | y (1.1) | ~75% |
| 1.1 Question/answer | 212 | 125 | n | – |
| 1.1 Contributions | 319 | 52 | n | – |
| 1.2.1 Data, model | 350 | **150** | n (Table 1.1) | – |
| 1.2.2 Tools | 363 | 112 | y (1.2, 1.3) | ~80%, ~85% |
| 1.2.3 Prior work | **755** | **172** | n | – |
| 1.3 Methods | **539** | 126 | y (1.4) | ~70% |
| 1.4.1 | 87 | 71 | n | – |
| 1.4.2 | 243 | 87 | y (1.5) | ~70% |
| 1.4.3 | 176 | 104 | n | – (equations) |
| 1.4.4 | 240 | 136 | y (1.6, 1.7) | ~80% (but D, H repeat Fig 1.9); ~85% |
| **1.4.5** | **452** | 123 | **n** | – |
| 1.4.6 | **706** | **170** | y (1.8) + Table 1.2 + unnumbered table | ~85% |
| 1.5.1 | 372 | 125 | y (1.9) | ~75% |
| **1.5.2** | **472** | 104 | **n** (Table 1.3 only) | – |
| 1.6 | **541** | 139 | y (1.10, 1.11) | ~60% (panel D ~22%, legend ~30%); ~85%, half of it a repeat |
| 1.7 intro | 65 | 65 | n | – |
| 1.7.1 | 363 | 90 | y (1.12) | ~70% |
| 1.7.2 | **986** | **193** | y (1.13, 1.14) + Tables 1.4, 1.5 | ~65%, ~65% |
| 1.8.1–1.8.5 | 198 / 75 / 122 / 253 / 166 | 122 | n (Table 1.6 in 1.8.2) | – |
| 1.9 | 85 | 85 | n | – |

Captions in words: 1.1: 123 · 1.2: **202** · 1.3: **281** · 1.4: **189** · 1.5: 133 · 1.6: 69 · 1.7: 146 · 1.8: **212** · 1.9: 133 · 1.10: **163** · 1.11: 126 · 1.12: 99 · 1.13: 89 · 1.14: 117.

Paragraphs over 150 words:
- line 137 (150)
- line 242 (172)
- line 272 (165)
- line 502 (161)
- line 521 (170)
- line 839 (193)

## Where prose is the right form (not flagged)

- 1.1 "The question, and the answer": it works as an abstract.
- 1.4.1 and 1.4.3: equations are the content there.
- 1.2.3 as a genre: a literature review is prose (see F14 for the one change I do ask).
- The Discussion (1.8.1, 1.8.3), the Limitations and Next-steps lists, and 1.9.
- The 1.5.1 threshold-budget paragraph: one argued choice.

## Findings

| # | location | issue | severity | suggested fix (replacement figure / reflow / relocation) | verified against a source |
|---|---|---|---|---|---|
| F1 | §1.4.5, whole subsection ("On the first experiment's own trains…" through "**This residual is unexplained.**") | A Results subsection of 452 words with no figure. It compares the hard-core and general forms at three train densities (first-experiment trains, denser realistic trains, realistic counts) and reports the chapter's one unexplained residual, all in about 30 inline numbers. The reader cannot see that the general form pulls points onto the identity line, or that the slow-stream misses all fall on one side. | **major** | **A figure for this already exists and the chapter does not use it:** `docs/learned/synthetic_validation/separation/real_intervals/synth_recovery_plot_coordination-rates-on-real-intervals_20261025.png`.<br>• Panels A–B: residual strips, hard-core vs general.<br>• Panels D–E: measured vs predicted, each measurement's hard-core prediction (open) joined to its general one (filled).<br>Adapt it:<br>• Relabel "page" as "hard-core form".<br>• Add the realistic-count points (7.3 and 16.5 events) to D–E, so the six slow-stream misses (1.3–2.6 SE) show as six points on one side of the identity line.<br>• Drop panel C/F or move them to an appendix.<br>The bullets then shrink to one sentence per panel. | yes (figure exists and was viewed; its values were not cross-checked against the chapter's numbers) |
| F2 | §1.5.2, Table 1.3 and the four bullets ("At 0.01 Hz and K = 4…" to "At σ = 1 s the event part runs high…") | The explanation of the second headline failure ("the reading is the median of a two-part mixture") is a mechanism, but it is shown only as 16 measured/predicted pairs in a table plus about 280 words of bullets that read the table aloud. A Results subsection with no figure. | **major** | **Replacement figure: assessor jitter reading against planted σ**, one panel per (b, K) (0.01/K4, 0.05/K3, K4, K6). In each panel:<br>• measured medians as points (the Fig 1.1 D/H data);<br>• the mixture prediction as a solid line;<br>• the chance-only level as a dashed horizontal line (0.38 s at 0.01 Hz; 0.73/0.68/0.60 s at 0.05 Hz);<br>• the event-only curve (SD of a Gaussian truncated at ±1.5 s, ceiling 0.743 s) dotted;<br>• the chance share c/(c+e) printed in the corner.<br>"Flat because the line sits on the chance level" and "tracks σ up to the truncation ceiling" then read at a glance. Move Table 1.3 to an appendix, or keep it compact under the figure. A cheaper alternative is to overlay the mixture lines on Fig 1.1 D and H. | no (judgment; Table 1.3 values not re-derived) |
| F3 | §1.2.1, "two measured lists of intervals between events, one per stream…"; used again in §1.3, §1.4.5, §1.4.6 and §1.6 ("5th percentile at 3.8 s and 1.7 % of intervals under 3 s… these shares are lower bounds") | The measured interval lists drive the realistic trains, the general-form result and the claim that the merging limit "rarely binds", yet they are never shown. Every reader has to take their shape on trust from scattered percentiles. | minor | **Replacement figure: empirical CDF of the two measured interval lists** (log time axis). Mark on it:<br>• the 2 s merge floor of the detector that made the lists (shaded "understated");<br>• the 20 s hard core;<br>• the 5th percentiles (3.8 s and 7.1 s);<br>• the tools' half-split separations (2.5 s assessor, 5 s count detector).<br>A single panel, placed in 1.2.1 or as Fig 1.11's companion, shows both why the hard core fails on dense trains and how much of the list lies below each tool's limit. | no |
| F4 | §1.7.2, "**No order.**" bullet (193 words, line 839); closing paragraph "The repository's wrapper scores only trains…" (127 words) | The longest block in the chapter is mostly a list of precedents: Kendall's W, Durbin, Skillings–Mack, Kreuz's rejected binomial null, Silva et al., Coppersmith et al., Shah & Wainwright. The same lineage already appears in Table 1.6 row "The exact no-order mean of F" and row "The score sort". | minor | **Relocate, don't delete.**<br>• Move the precedent sentences to §1.8.2. Expand Table 1.6's two rows, or add a short paragraph under it.<br>• Keep in §1.7.2 the result (exact mean; asymptote 0.376/√n̄; 33 of 33 matches), the caveat "only the mean is derived, not the spread", and the fitted 0.50.<br>Prose is right for this content; only its location is wrong. | yes (Table 1.6 rows read) |
| F5 | §1.7.2, Table 1.4 vs Figure 1.14 | The table and the figure carry the same 48 power values. That is one result shown twice in the chapter's longest subsection (986 words, two figures, two tables). | minor | Keep Figure 1.14 in the text and move Table 1.4 to an appendix, or keep the table and drop the figure. My preference is the figure: the 0.8 crossing is the message. | yes |
| F6 | §1.4.6: (a) the unnumbered table after Table 1.2; (b) "**Against the correlogram tool**…" (170 words); (c) "**The fit was given the true event train**…" (146 words) | (a) The jitter columns of the unnumbered table repeat Fig 1.8 C. Its participants and rate columns appear nowhere graphically, and the table has no number or caption. (b) Reads Table 1.2 aloud, cell by cell. (c) Hard-core-assumed and Poisson-assumed fits (Poisson on the slow stream reads 0.55–0.62 of planted) are given only as numbers. | minor | (a) Add two thin strip rows to Fig 1.8 C, participants and rate per recording with the in-band shading. Or number the table (Table 1.2b) with a one-line caption.<br>(b) Cut the paragraph to its verdict ("per recording, the joint fit is better at 0.05 Hz from 0.5 s; elsewhere the correlogram, pooled or Gaussian-converted, does as well") and let Table 1.2 carry the numbers.<br>(c) Add hard-core-assumed and Poisson-assumed medians to Fig 1.8 C as extra marker ticks per strip. | yes (figure and table compared) |
| F7 | Figure 1.6, panels D and H ("chance clusters per minute, discussed in *1.5.1*") | They repeat the measured-vs-predicted chance-cluster check that Figure 1.9 makes, and the caption itself defers them. That is a quarter of the canvas spent on another section's content. | minor | **Reflow:** drop D and H and redraw 1.6 as a 2×3 grid. A–C and E–G gain about a third more width, which helps the crowded F and G. | yes (both figures viewed) |
| F8 | Figure 1.11, panels E–H | Half the canvas repeats A–D with realized rather than planned separation. The caption calls it "the same result". | minor | **Reflow:** overlay the realized-separation points (already a distinct open marker) on A–D and drop E–H. That doubles A–D's height. Or move E–H to an appendix figure. | yes |
| F9 | Figure 1.10, lower row | The legend fills the right ~55% of the lower row, about 30% of the canvas, and panel D, the power curves at the realistic values, gets about 22%. | minor | **Reflow:** compress the legend into a two-row strip under A–C and give D the full lower width, or make D a fourth column beside A–C. | yes |
| F10 | Figure 1.14, the text block at bottom right ("r = δ/σ… Test: exact-size 5 %, randomized…") and the E = 1 callout | The canvas carries five lines of methods prose that already appear in the caption. The legend and text take about 20% of the height. | minor | Delete the in-figure methods block and put the legend in one row. The panels gain about 15% height. | yes |
| F11 | Captions of Figs 1.3 (281 words), 1.8 (212), 1.2 (202), 1.4 (189), 1.10 (163) | Captions that carry argument or methods. 1.3 re-walks panel C's arithmetic (net counts +3/+5/−3/−5, F = 0.67), which panel C itself prints. 1.4 defines "resolved", a method. 1.8 C restates the simulation design of §1.3. | minor | • Fig 1.3: "C: a worked example of the score sort and F (values in the panel)".<br>• Fig 1.4: move the definition of "resolved" to §1.3.<br>• Fig 1.8: replace the design restatement with "realistic values as in §1.3".<br>• Keep the provenance sentence in 1.2 ("This minute was picked…"). It is a caveat, and caveats stay. | yes |
| F12 | §1.1, numbered failures 1–3 and Figure 1.1 | The three failures are the chapter's hook, but the figure has no numbered callouts. Failure 3 is cited to background-only cluster rates, while Fig 1.1 F already shows it (assessor event rate about 8–16× planted at 0.05 Hz). | minor | Add callouts ①, ② and ③ on panels A/E, H and F, and cite "Figure 1.1 F" in item 3. Then Fig 1.1 shows the three failures, and the list only names them. | yes |
| F13 | §1.2.1, the generative-model paragraph (150 words, line 137) | A paragraph describing a mechanism, with no figure. Figure 1.2 (planted times, Gaussian jitter, Poisson background) illustrates exactly this model but sits in §1.2.2 and is not cited from §1.2.1. | minor | Cite Figure 1.2 A–B from the model paragraph, or move the figure up to §1.2.1. Placement order is role 11's call; the density point is that the model is drawn already and the text does not point to the drawing. | yes |
| F14 | §1.2.3 Prior work (755 words; paragraphs of 149, 172, 143 and 165 words), plus "Table 1.6 (*1.8.2*) sets each result against its nearest precedent" | Prose is the right form for a literature review, so this is not a figure flag. But the one structured artifact that makes the gap visible, Table 1.6, is placed 650 lines later, and §1.2.3 points forward to it. | minor | Move a slim Table 1.6 into §1.2.3, as the reader's map of the gap, with columns precedent · jitter law · carrier/train · statistic · what it estimates. Keep the "status" column, and the not-found results, in §1.8.2. | yes |
| F15 | §1.3, "**Rederivation.**" (about 120 words) | Process provenance (the rederivation sessions) inside Methods. | minor | Relocate it to "About this chapter". Keep one sentence in §1.3: "two independent rederivations agreed; see About this chapter". | no |

## Summary for the committee

The figures are strong. All 14 are real data or real schematics and all render legibly. The chapter is mostly figure-first.

Two results subsections still tell rather than show, and I would not sign off until each has a figure:
- **§1.4.5 (F1):** the general form vs the hard-core form, and the unexplained slow-stream residual. A ready-made figure sits unused in `separation/real_intervals/`.
- **§1.5.2 (F2):** the assessor's jitter reading as a two-part mixture.

The rest is reflow and relocation:
- Three figures give canvas to content repeated elsewhere or to legends (F7–F10).
- Table 1.4 repeats Figure 1.14 (F5).
- An unnumbered table partly repeats Fig 1.8 C (F6).
- The longest blocks are precedent lists that belong in §1.8.2 (F4). Move them; nothing should be cut.

Boundaries: I made no geometry or build checks (agent 10), did not judge argument order (agent 11, noted only in F13), and did not check any number against its record.
