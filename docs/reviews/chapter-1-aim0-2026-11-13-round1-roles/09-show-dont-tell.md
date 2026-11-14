GRANT 9 MISMATCH — missing none; holds Edit, Write, PowerShell, Agent, Artifact, Skill, ToolSearch, mcp__claude_ai_Claude_Docs__batch, mcp__claude_ai_Claude_Docs__update (editing-capable), plus NotebookEdit among the deferred tools

(Run note: the grant is Read, Grep, Glob, Bash. I did not use any of the extra tools. The only file I wrote was a counting script, <scratch>\mb\role09\count.py, created through Bash. The artifact was not touched. The run record should say this review took a fallback path.)

# Role 9: Density and figure-first. Chapter 1 (chapter-1-aim0.md, blob 14d63527)

## What I checked
- I read the whole chapter (1,668 lines, about 21.5k words including references).
- I opened all 19 figure PNGs as images.
- I counted with a script: prose words per subsection, largest single text block, figures, caption lengths and tables. I measured each figure's rendered size from the PNG's pixel size and aspect.
- I read the house rules in CLAUDE.md: "Show the picture" and "Plot conventions".

## Thresholds used
This is a portrait document, not a deck, so I tuned the defaults:
- **Unit:** one subsection stands in for one slide.
- **Word limits:** "Over 40 words" and "a block over 60 words" would flag every unit in a dissertation. I report the counts, but only flag text blocks over about 250 words, and results or methods units with no figure.
- **Prose runs:** I flag two or more consecutive prose-only units in a results or methods stretch.
- **Figure share:** measured as height at full text width over a 6.5 × 9 in text block.
  - The chapter sets no width on any image. Native widths are 9.5–12.5 in, so pandoc scales every figure down to the full text width.
  - At full width, a landscape figure cannot reach 50% of the page. A share under 50% is therefore a flag only where the figure's own layout wastes area.

## Count table
"Prose" counts words outside captions and tables. "Max block" is the largest paragraph or list. "Fig share" is the share of the text block.

| line | unit | prose | max block | fig | fig share | caption words | tables |
|---|---|---|---|---|---|---|---|
| 10 | 1.1 The problem | 422 | 109 | y (1.1) | 67% | 146 | 0 |
| 58 | 1.1 How the chapter proceeds | 213 | 125 | n | – | – | 0 |
| 76 | 1.2 intro | 125 | 125 | n | – | – | 0 |
| 87 | 1.2.1 Fixed bins | 141 | 106 | n | – | – | 0 |
| 99 | 1.2.2 Sliding window | 110 | 110 | n | – | – | 0 |
| 109 | 1.2.3 CFAR | 443 | 161 | n | – | – | 0 |
| 144 | 1.2.4 What each detector finds | 492 | 347 (list) | y (1.2) | 87% | 271 | 1 |
| 212 | 1.3.1 Data and model | 513 | 194 | y (1.3) | 79% | 208 | 1 |
| 288 | 1.3.2 Correlogram | 593 | 131 | n (uses 1.3 C) | – | – | 0 |
| 334 | 1.3.3 Pairs and triples | 728 | 169 | y (1.4) | 87% | 323 | 0 |
| 413 | 1.3.4 Assessor and count detector | 343 | 179 | y (1.5) | 95% | 276 | 0 |
| 458 | 1.3.5 Which cells, what order | 86 | 86 | n | – | – | 0 |
| 467 | 1.3.6 Prior work | 957 | 193 | n | – | – | 0 |
| 544 | 1.4 What brute force found | 424 | 185 | y (1.6) | 44% | 122 | 0 |
| 590 | 1.4 The question and the answer in brief | 277 | 158 | n | – | – | 0 |
| 613 | 1.4 How the predictions are tested | 480 | 166 | n | – | – | 0 |
| 652 | 1.4 Contributions | 386 | 322 (list) | n | – | – | 0 |
| 685 | 1.5 intro | 118 | 118 | n | – | – | 0 |
| 696 | 1.5.1 Undercount | 99 | 78 | n | – | – | 0 |
| 708 | 1.5.2 Window sharing | 310 | 89 | y (1.7) | 37% | 183 | 0 |
| 751 | 1.5.3 Expected excess counts | 350 | 89 | n | – | – | 0 |
| 782 | 1.5.4 The test | 242 | 103 | y (1.8, 1.9) | 50%, 66% | 72, 251 | 0 |
| 830 | 1.5.5 General form | 501 | 154 | y (1.10) | 76% | 236 | 0 |
| 888 | 1.5.6 Joint fit vs correlogram | 447 | 180 | y (1.11) | 68% | 281 | 1 |
| 957 | 1.5.7 Realistic values | 416 | 148 | y (1.12) | 46% | 262 | 2 |
| 1027 | 1.6 intro | 71 | 71 | n | – | – | 0 |
| 1035 | 1.6.1 Chance clusters | 526 | 186 | y (1.13) | 45% | 209 | 0 |
| 1091 | 1.6.2 Jitter reading | 697 | 317 (list) | y (1.14) | 70% | 215 | 1 |
| 1168 | 1.7 Separation | 620 | 350 (list) | y (1.15, 1.16) | 58%, 60% | 203, 153 | 0 |
| 1237 | 1.8 intro | 60 | 60 | n | – | – | 0 |
| 1244 | 1.8.1 Membership | 456 | 151 | y (1.17) | 30% | 128 | 0 |
| 1291 | 1.8.2 Order | 1093 | 258 | y (1.18, 1.19) | 36%, 34% | 103, 193 | 2 |
| 1420–1533 | 1.9.1–1.9.5, 1.10 | 74–301 each | 240 max | n (6 units) | – | – | 1 (1.9) |

## Findings
Each row gives location · issue · severity · suggested fix · could I verify it against a source.

1. **Whole chapter (1.4 "answer in brief", 1.5.7, 1.10) · No picture of the measuring tools' successes and failures · major.**
   - **Issue:** The owner asked to see each method's successes and failures graphically. That is met for the three simple detectors (Figure 1.2) but not for the measuring tools. For the coordination-rates tool, joint fit, correlogram tool, assessor, order test and assembly test, the verdict of what reads and what fails is spread across:
     - Tables 1.4, 1.5 and 1.7;
     - Figure 1.12;
     - the prose of 1.4 and 1.10.
   - **Fix:** Add one scorecard (regime-map) figure, the measuring-tool counterpart of Figure 1.2.
     - Rows: each quantity and tool (participants by tool 1 s; participants by joint fit; rate; jitter by joint fit, correlogram and assessor; order; membership; separation).
     - Columns: events per 20-minute window (1, 2, 4, 8, 16), plus a busier-background column.
     - Cells: colored readable, marginal or not, with the n-of-40 count printed in each.
     - Place it at "The question, and the answer in brief" and point back to it from the Conclusion.
   - **Verifiable:** yes. Every number is already in Tables 1.4, 1.5 and 1.7.
2. **1.5.7, Table 1.5 · Typed-only key result · major.**
   - **Issue:** The chapter's main practical result, what one realistic window can read, appears only as a typed table.
   - **Fix:** Turn it into a line chart. Plot recordings in band (of 40) against E on a log₂ axis, one line per stream and cell count, with one panel for the joint fit and one for the tool's 1 s estimate. Add a reference line at about 32/40. Move Table 1.5 to an appendix (relocate, don't delete).
   - **Verifiable:** yes.
3. **1.2–1.2.3 (lines 76–143) · Four consecutive prose-only methods units, about 820 words, before Figure 1.2 · moderate.**
   - **Issue:** The CFAR geometry (cell under test, ±5 s guard, 30 s reference windows) and masking are described but never drawn. Figure 1.2 D shows only the resulting threshold.
   - **Fix:** Add a mechanism schematic panel on one time axis:
     - a fixed-bin grid with an event straddling a border;
     - the sliding window;
     - the CFAR reference and guard windows, with a neighboring event inside the reference window raising the threshold.
   - **Also:** The chance-floor formula's "6 cells at 0.0096 Hz, 12 at 0.05 Hz" could be a small curve of chance calls per hour against K with the one-per-hour line, in the style of Figure 1.13, or added to Figure 1.13 as count-detector curves.
   - **Verifiable:** partly (geometry stated in the text).
4. **1.5.3 "Two sources look like one" · Derived claim with no picture · moderate.**
   - **Issue:** The claim bears on the dissertation's premise, yet it is prose and algebra only.
   - **Fix:** Draw it as curves only, since it is derived. Show f₂ and f₃ (or k̂) against window width for a two-source mixture (for example k = 5 and 15) and for the single blended source. The curves overlie each other.
   - **Verifiable:** yes (formula in the text).
5. **1.6.2, Figure 1.14 vs Table 1.6 · Figure omits a row the text names as a test · moderate.**
   - **Issue:** Figure 1.14 omits the 0.01 Hz, K = 3 row. The text names that row as one of the two that "test the mixture as a mixture" (line 1148). Only Table 1.6 carries it.
   - **Fix:** Add it as a fifth panel. Then move Table 1.6 to an appendix.
   - **Verifiable:** yes.
6. **1.8.2, Figure 1.19 vs the rounding paragraph (lines 1385–1398) · The practically relevant power is prose-only · moderate.**
   - **Issue:** Figure 1.19 shows unrounded power only. The power under production frame rounding is in prose only (for example 0.06 → 0.66 at E = 2), and it is the power that applies to real data.
   - **Fix:** Add rounded power at realistic σ as paired markers (unrounded open, rounded filled) or as a panel C.
   - **Also:** Table 1.7 repeats Figure 1.19's values exactly. Move it to an appendix.
   - **Verifiable:** yes.
7. **Tables 1.3, 1.6 and 1.7 · Tables duplicate figures · minor.**
   - **Issue:** Table 1.7 = Figure 1.19, Table 1.6 ≈ Figure 1.14, and Table 1.3 overlaps Figure 1.11 A–B.
   - **Fix:** Relocate these tables to an appendix.
   - **Alternatively:** add the "pooled as shipped" and "Gaussian" columns of Table 1.3 to Figure 1.11 A–B as two more marker series.
   - **Verifiable:** yes.
8. **1.4 "question" → 1.5.1 (lines 590–707) · Five consecutive prose-only units, about 1,360 words · moderate.**
   - **Issue:** "How the predictions are tested" (480 words) describes the experimental design (the grid, the held-out rerun, and the realistic 45-minute, 20-minute and dense-train runs) in prose.
   - **Fix:** Add a study-design schematic: one box per simulation family with its parameters and recording counts, each arrowed to the section and figure that uses it.
   - **Fix:** The "answer in brief" becomes the scorecard of finding 1.
   - **Prose is right:** Contributions is a claims list.
   - **Verifiable:** yes.
9. **1.5.5, lines 857–867 · No figure for the general form on the first experiment · minor.**
   - **Issue:** The general form's effect on the first experiment is prose-only. Figure 1.10 covers only measured-interval trains.
   - **Fix:** Add the general form as a third series in Figure 1.9, or as a paired dot plot of median residual (hard-core against general) per background.
   - **Verifiable:** yes.
10. **Figure 1.8 · Wasted canvas hides the claim · minor-moderate.**
    - **Issue:** Every panel shares a 0.2–2.5 axis, while the participant data sit between 0.3 and 1.3. The "about 1 % overprediction" the section opens with cannot be seen.
    - **Fix:** Use per-panel ranges, or move Figure 1.8 to an appendix and give rate the residual-strip treatment Figure 1.9 gives participants.
    - **Verifiable:** yes.
11. **Captions carrying argument ("a caption is a caption") · minor.**
    - **Figure 1.9:** the sign test (24 of 32, p = 0.007; 17 of 48) appears three times: in the caption, in the figure's header text and in the prose. Keep it in the prose only.
    - **Figure 1.13:** "so K = 5 is the safe choice … one fixed threshold cannot serve both backgrounds" is a conclusion. Move it to the text.
    - **Figure 1.12:** the resolved-on-which-record narrative and "2 of 40 / 16 of 40" belong in the text.
    - **Figure 1.10:** the findings "all six … lie above" belong in the text.
    - **Figure 1.11:** the in-band counts repeat Table 1.4 and the figure's own labels. Drop them from the caption.
    - **Figure 1.2:** the draw-selection provenance ("first of 200 … 17 of 200") should move to a note or footnote, not be cut.
    - **Figure 1.4:** the caption (323 words) re-derives F's arithmetic that panel C already prints. Cut it to what the panels show.
    - **Verifiable:** yes.
12. **Figure geometry · minor.**
    - **Full width:** Every figure renders at full text width, so none is auto-shrunk below width.
    - **Under 50% by aspect:** Figures 1.6, 1.7, 1.12, 1.13, 1.17, 1.18 and 1.19 (30–46%) are landscape. That is acceptable at full width.
    - **Figure 1.12 · reflow wanted:** about a quarter of its width is callout text on the left. Move the callouts to the legend or caption and let the grid take that width.
    - **Figure 1.3 · reflow wanted:** a blank band of about 10% of its height sits above panels A–B, holding planted triangles detached from their panels. Draw the triangles inside A and B.
    - **Boundary with agent 10:** figures are drawn at 11–11.5 in wide (the script sets figsize (11, …)) and shrink to about 0.59× at 6.5 in, so text near 11 pt prints near 6.5 pt. That legibility check belongs to agent 10.
    - **Verifiable:** yes.
13. **1.7, Figure 1.15 · Missing reference line · minor.**
    - **Issue:** The count detector's 5 s half-plateau is stated in the text, but only the assessor's 2.5 s line is drawn.
    - **Fix:** Add the 5 s line.
    - **Verifiable:** yes.

## Where prose is right
- **1.3.2:** prose plus equations. Its figure is Figure 1.3 C.
- **1.3.6 and 1.9.2:** literature. Table 1.9 is the right form.
- **1.9.3–1.9.5:** discussion, limitations and next steps.
- **Conclusion:** prose, provided it points at the scorecard of finding 1.
- **Table 1.8:** qualitative comparison.
- **Figure 1.1:** meets "lead with the problem". It is the first visual, after about 190 words, and its caption describes rather than argues.
- **Figure 1.2:** shows the detectors' successes and failures directly.
