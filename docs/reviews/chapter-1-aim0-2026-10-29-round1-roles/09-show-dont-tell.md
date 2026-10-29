GRANT 9 MISMATCH — missing none; holds forbidden tools: Edit, Write, PowerShell, Agent, Artifact, Skill, ToolSearch, mcp__claude_ai_Claude_Docs__batch / __update (both write-capable), plus deferred NotebookEdit, SendMessage, Gmail and Dropbox write tools, which ToolSearch can load. The session handed me the full harness toolset, not the role's grant of Read, Grep, Glob, Bash. Record it as a run-level finding: this role ran on a fallback path. I used only Read, Bash and the SubagentHandback call, and wrote only to my scratch folder (`.../scratchpad/mb/work-9/count.py`). I did not edit anything in the repository or in 01-lit.

# Role 9: Density & figure-first ("Show, Don't Tell"). Committee review of Chapter 1 (Aim 0)

Artifact: `<worktree>/docs/dissertation/chapter-1-aim0.md`, hash a3d06b04… (checked). 700 lines, 7,743 words, 6 figures. I viewed all six figures with Read. I also viewed one figure that exists in the sources but is **not** in the chapter: `separation/real_intervals/synth_recovery_plot_coordination-rates-on-real-intervals_20261025.png`.

## Thresholds, adapted for a dissertation chapter (conventions, not optima)
The deck thresholds (40 words a slide, 60-word blocks) make no sense for a chapter, where continuous prose is the normal form. The unit here is each numbered section, treated as a page. I flagged:
- a **results, methods or derivation section with no figure**, when its central claim has a shape (a curve, a boundary, a comparison);
- **three or more consecutive prose-only sections** (two if they are results);
- any **single paragraph over 150 words**, about 12 rendered lines, roughly one screen;
- in a figure-bearing section, a **figure share under ~30%** of the section's rendered height (lower than the deck rule's 50%, because chapter text is expected).

How I estimated figure share: the markdown renders each image at column width, so its rendered height is column width ÷ aspect ratio, taken from the PNG header. Text height is (words ÷ 12) × line height, assuming a 700 px column, about 12 words a line and 22 px a line. These are estimates from the render model, not measured pixels. No rendered HTML or PDF exists to measure.

## Count table (one row per section)

| § | words | largest block | figure | fig share (est.) |
|---|---|---|---|---|
| front note (blockquote) | 116 | 116 | n | – |
| 1.1 Introduction | 479 | 156 | n | – |
| Contributions | 365 | 97 | n | – |
| 1.2.1 Data & generative model | 345 (incl. Table 1.1) | 162 | n | – |
| 1.2.2 The tools | 221 | 100 | n | – |
| 1.2.3 Prior work | 423 | **217** | n | – |
| 1.3.1 Window sharing | 231 | **162** | n | – |
| 1.3.2 Expected excess counts | 152 | 69 | n | – |
| 1.3.3 Window must exceed jitter | 76 | 41 | n | – |
| 1.3.4 Any stationary event train | 92 | 92 | n | – |
| 1.3.5 Joint fit | 147 | 147 | n | – |
| 1.4 Assessor's threshold | 112 | 47 | n | – |
| 1.5.1 Simulation testbed | 145 | 90 | n | – |
| 1.5.2 Protocol | 45 | 45 | n | – |
| 1.5.3 What brute force found | 245 | 82 | y (Fig 1.1) | ~49% |
| 1.5.4 What theory predicts | 533 | 131 | y (Fig 1.2) | **~29%** |
| 1.6 intro | 44 | 44 | n | – |
| 1.6.1 Membership | 342 | 80 | y (Fig 1.3) | ~32% |
| 1.6.2 Order | **836** (incl. Table 1.2) | **207** | y (Fig 1.4) | **~14%** |
| 1.7 Minimum separation | 393 | 85 | y (Figs 1.5, 1.6) | ~48% |
| 1.8 Checking the derivations | 253 | 141 | n | – |
| 1.9 Old and new | 274 (table) | 47 | n | – |
| 1.10 Discussion (5 subsections) | 863 | 136 | n | – |
| 1.11 Conclusion | 179 | **179** | n | – |

Headline: **the first figure appears 3,099 words into the chapter (line 292 of 700).** Every section from 1.1 to 1.5.2 is prose-only: 13 consecutive sections, covering the generative model, the tools and all of the theory. The chapter's central contributions, g_n, k̂, the joint fit and the chance-cluster rate, are stated only as equations and sentences. The figures that exist are confined to the results sections.

## Findings
Columns: location · issue · severity · suggested fix (the replacement figure) · verified against a source.

1. **1.1–1.5.2 as a block** ("The input is one list of onset times…" through "prints every number quoted in this section") · 13 consecutive prose-only sections and about 3,100 words before Figure 1.1. A committee member reaches the results without ever having seen the data, the model or a single prediction curve. · **blocking** · Add the four figures in items 2–5 below. Together they give the theory half of the chapter a visual spine. · yes (counted)

2. **1.2.1 + 1.2.2** ("cluster centers placed at random… jitter of standard deviation σ"; "finds clusters of at least K active cells in 1 s bins…") · The generative model and three tools are described only in words. This is a methods section with no figure. · **major** · Make a new **Figure 1.1, a schematic raster**: 33 cells × about 60 s of simulated recording, with background onsets in grey and two coordinated events in color. On it, annotate σ (Gaussian scatter about the event time), k, b and the 20 s minimum spacing. Underneath, add three aligned strips: the coordination-rates tool's w = 1/2/4 s windows with one shifted surrogate; the assessor's 1 s bins, threshold K and ±1.5 s gather; and the count detector's 2 s bins. Keep Table 1.1. Renumber the later figures. · yes

3. **1.3.1 + 1.3.3** ("g₂(w, σ) = (2Φ(a) − 1) − …"; "**k̂ = 2 + (k − 2) g₃/g₂.** As σ approaches w, g₃ falls faster than g₂") · Contribution 1, the chapter's lead result, has no picture. The 162-word paragraph comparing it with uniform jitter ("Gaussian jitter has no such edge, so g_n stays smooth in w") makes an argument about the *shape* of a curve that the reader is asked to imagine. · **major** · Two-panel figure. (A) g₂ and g₃ against w/σ for Gaussian jitter (smooth curves), overlaid with the uniform-jitter piecewise-linear counterparts (Grün 1999 / Louis 2010), so that "no edge" is visible. (B) k̂/k against σ/w for k = 5, 10, 20. This is the "window must exceed jitter" rule as a curve, and the Fig 1.1 A measured medians can be overlaid on it. The uniform-jitter attribution sentence can then shrink to a caption clause. · yes (equations in text; theory.py has g_n)

4. **1.3.4 and 1.5.4 "On real gaps"** ("the hard-core form fails at the 4 s window: it predicts rate 1.17… χ² about 15, against 74–133") and the 1.5.4 sign-test sentences ("measured below predicted in 12 of 16 conditions, p = 0.08… removed it (p = 0.19)"; "median residual falls from 0.030 to 0.013") · These claims are given as numbers in prose, yet **a finished figure for them already exists in the sources and was left out**: `separation/real_intervals/synth_recovery_plot_coordination-rates-on-real-intervals_20261025.png`. Its panel C shows the rate residual as terms are added (0.030 → 0.013). D and E show hard-core against general predictions on real gaps, with lines joining each measurement's two predictions. F shows the joint fit's σ/k/λ ratios on real gaps, hard-core against general. · **major** · Embed that figure, or its panels C–F, as the figure for 1.3.4 / "On real gaps". Replace the χ² and residual strings with panel references, and move the sign-test p-values to a figure note or appendix (relocate, do not delete). Note that its legend refers to "page's hard-core form" (repo jargon), which needs relabeling to "hard-core form" for the chapter. · yes (file viewed)

5. **1.4** ("**60 q (1 − q)² per minute.** Setting this against a budget of one chance call per hour gives the smallest threshold") and its payoff in 1.5.4 ("the smallest threshold safe against one chance call per hour is 5 cells at 0.01 Hz and 8 at 0.05 Hz") · The safe threshold is read off a curve that is never drawn. Fig 1.2 D/H shows only the 2–3 measured points. · **major** · Line plot of predicted chance clusters per minute against K (3–10), one line per background (0.01, 0.05 Hz; optionally the lab's 0.0096). Add a horizontal line at 1/60 per minute (one an hour) and mark the measured points with Poisson 95% intervals. The crossings at K = 5 and K = 8 become visible. This can replace Fig 1.2 D/H and free those panels. · yes

6. **1.6.2, Table 1.2** ("| 5 | 1 template 0.43; 2, 0.13 | 1 template 1.00; 2, 0.73; 4, 0.34 |") · This is the chapter's most consequential applied result ("an order indicator can find one template at best"), and it sits in a typed table whose cells are ragged lists, unreadable at a glance. This is exactly the "typed table → figure" case. · **major** · Grouped line plot: power against number of templates M (log₂ axis), one panel each for 7 and 13 cells per event, and one line per events-per-recording (5, 10, 25). Add a horizontal line at power 0.8 and a shaded note giving the lab's 1–8 events per baseline window. Move the exact values to an appendix table. · yes (values in text; order_limit.json holds them)

7. **1.6.2 figure share ~14%, 836 words, a 207-word block** ("**Against the Synfire Indicator.** Kreuz's indicator differs from F in four ways…") · The section is a wall of text around one short, wide figure. The 207-word paragraph mixes a four-way comparison, the lab-observation caveat and a Borda/Copeland literature aside. · **major** · Turn the "four ways" comparison into a 4-row table: coincidence finding · sort · normalization (F_Kreuz = F(k−1)/(N−1)) · null, with Synfire and F as the two columns. Relocate the Coppersmith / Shah & Wainwright sentences to 1.9 (its row "The score sort" already exists) or to a footnote. With item 6 in place, the section carries two figures and its share rises above 30%. · yes

8. **1.5.4, figure share ~29%, 533 words, 5 paragraphs over 60 words** ("Of 48 condition-windows per background, 7 and 10 sit beyond 2 standard errors; if the prediction were exact, simulation says about 6 would…") · Fig 1.2 is followed by five dense numeric paragraphs. Much of their content is either already in Fig 1.2 / Fig 1.1, or belongs in a figure note. · **minor** · Keep the assertion and one number per estimate in the body, and point to panels ("Fig 1.2 A, E"). Relocate the outlier count, the heavy-tail remark and the sign tests to a figure note or appendix. Item 4 absorbs the "On real gaps" and rate paragraphs. The "safe threshold also loses spread-out events… 0.76–0.80… 0.29–0.33" sentence either gets a panel (detected ÷ planted against σ at K = 6) or moves to 1.5.3 beside Fig 1.1. · yes

9. **1.7** ("**So between about 0.6 and 2.5 s the tools merge pairs the data could separate.**") · The section's conclusion compares two floors, but no single figure puts them on one axis. Fig 1.5 shows the tools' floors, and Fig 1.6 shows the data's floor on a log y axis with an "assessor floor 3 s" reference line. · **minor** (major if 1.7 is meant to be a headline result) · Add a one-row "separation ruler": a log axis from 0.1 to 10 s with marked bands for the frame (0.1 s), the data's floor (0.26–0.76 s), the 2σ unimodality limit, the assessor's half-split point (about 2.5 s), the count detector's (about 5 s), and the fast/slow 5th-percentile real gaps (3.8 s, 7.1 s). The same ruler can serve the Discussion. Separately, Fig 1.5 rows E–H repeat A–D on a realized-separation axis. Move E–H to an appendix so A–D get the full width, and Fig 1.5's legend can then shrink. · yes

10. **Figure 1.6 vs 1.7 text** (figure reference line "assessor floor 3 s"; text "about 2.5 s for the assessor") · The figure and the text give different numbers for the same quantity: probably the full plateau against the half-plateau. A reader comparing them will see a contradiction. · **minor** (owned by another role; noted for adjudication) · Relabel the line in Fig 1.6 to the half-plateau 2.5 s, or state in the caption that 3 s is the plateau onset. · yes (separation/README.md gives half-plateau 2.5 s)

11. **Figure 1.4 C legend vs 1.6.2 text** (legend "fitted 0.38/√n̄"; text "c/√n̄ … 0.376… with nothing fitted") · The figure calls the score-sort line fitted, while the text says the constant is exact and nothing is fitted. · **minor** (consistency; flagged for the figure/rigor roles) · Relabel to "exact 0.376/√n̄". Keep "fitted 0.50/√n̄" for the local search. · yes (figure viewed)

12. **1.10 "What it says about the lab's recordings"** (128-word paragraph: "Its jitter (0.105–0.150 s) lies between the joint fit's resolved point (0.2 s) and its unresolved one (0.05 s). Its fast-stream events (about 7 cells) lie between the 5-cell arm… and the 10-cell arm") · This is a two-dimensional "where does the lab sit" argument, given in prose. · **major** · Regime map: σ on the x axis (log) against cells per event on the y axis. Mark the tested grid points as resolved or unresolved by the joint fit, and the k̂-bias boundary from item 3. Overlay the lab's fast and slow streams as boxes (σ 0.105–0.15 s; k 7 and 13). It shows the chapter's applied conclusion, "the lab sits at the edge of what has been tested", at a glance, and it motivates Next step 1. · yes

13. **1.1 Introduction / Contributions** (156-word "The answer, developed below…" paragraph; 7-item list) · Prose is right for the argument here, but the chapter has no graphical abstract of its method ("predict first, simulate to check"). · **minor** · Optional opening figure: a flow from planted parameters → closed form → predicted tool output → simulated tool output → residual, with the seven contributions placed on the tools they predict. Otherwise prose is right here: the paragraph is a summary, and a summary is prose. · yes

14. **1.2.3 Prior work** (217-word Louis, Borgelt & Grün paragraph) · Over the block limit. Its three-way comparison ("the jitter is uniform rather than Gaussian, the reading is a slope-change rule rather than a fit, and the event rate is not estimated") is repeated in 1.3.5 and again in the 1.9 table. · **minor** · Prose is the right form for a literature review. Make 1.9's table the single home for the comparison, and cut the repeats in 1.2.3 and 1.3.5 to one sentence each that points to it. No figure needed. · yes

15. **Front note blockquote** (116 words: "An exercise, not a submission…") · Provenance and caveats sit on the face of the chapter, ahead of the title's content. · **minor** · Relocate them to a preface or acknowledgments note. Keep every word, but take them off the first page. · yes

16. **Captions, Figs 1.1 and 1.5** · The Fig 1.1 title is descriptive ("Recovery against planted jitter…") and does not say what the figure shows or why it matters. The Fig 1.5 caption re-lists every condition that the legend already carries. · **minor** · For Fig 1.1, use an assertion title, for example "At 0.05 Hz the assessor reads a constant jitter; the joint fit tracks planted jitter." For Fig 1.5, cut the caption to what it shows (split chance rises at bin-set separations, regardless of σ and b) and leave the conditions to the legend. · yes

17. **1.3.2, 1.3.5, 1.5.1, 1.8, 1.9, Limitations, Next steps, 1.11** · Checked. Prose or tables are the right form here. 1.3.2 is equations. The 1.5.1 grid is stated compactly; a 4×3×2×2 design table is optional, and the shared-seed rerun paragraph could move to a methods note. 1.8 is a verification narrative; a 3-row "check · what it covers · its limit" table is optional. 1.9 is already a table. The Conclusion's single 179-word paragraph is acceptable for a conclusion. · – · no change required · yes

## Sign-off condition (this role)
Before I would sign, the chapter needs a figure on the theory side: items 2, 3 and 5. It needs the omitted real-intervals figure embedded (item 4). It needs Table 1.2 redrawn as a power plot (item 6), and the lab-regime argument in 1.10 drawn as a map (item 12). Caveats, p-values and outlier counts should be **relocated** to figure notes or appendices, not cut.

Residual: figure shares are estimated from PNG aspect ratios under a 700 px column assumption. If a PDF render exists, agent 10 should measure it.

---
*Archivist's note (main thread, 2026-10-29): for this public repository (sapper SAP004), the review worktree's absolute path became `<worktree>/`; a slash-joined list of tool names containing "Dropbox" was written with "and". Nothing else in the report was changed by this pass.*
