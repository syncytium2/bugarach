GRANT 9 MISMATCH — missing none; holds Edit, Write, PowerShell, Agent, Artifact, Skill, ToolSearch, mcp__claude_ai_Claude_Docs__batch/update/guide (editing and publishing tools no reviewer may hold). I used none of them and changed no file. The only file I wrote is one counting script at <scratch>/mb3/role09/count.py. This mismatch is a finding about the run: the run record must say the review took a fallback path.

# Role 9: Show, don't tell — Chapter 1 (<repo>/docs/dissertation/chapter-1-aim0.md, blob faa8e320)

## Thresholds I used
The artifact is a dissertation chapter, not a deck, so the slide thresholds do not carry over directly. These are my adaptations, and they are conventions, not optima:
- **Unit:** one numbered (sub)section.
- **Flags:**
  - two or more consecutive sections with no figure in a methods or results stretch;
  - any single block of text over 300 words;
  - a methods or results section whose key numbers exist only as prose or a typed table;
  - a figure that does not fill the text width, or one whose panels or legend waste the canvas.
- **Figure share:** there is no render of this blob. The Dropbox .docx is the pre-revision version (16 images, an old figure order), so I could not measure from a render.
  - I estimated share from each PNG's native size at 150 dpi (130 dpi for three), capped at a 6.5 in text width, as a share of a letter page.
  - Every PNG is natively wider than 6.5 in, so every figure fills the text width and none has side margins.
  - Measuring from the source rather than a render is a gap in this check.
- **Run-level note for agent 10:** the Dropbox deliverable `explainer_dissertation-chapter-1-analytical-baseline_20261113.docx` and the `chapter-1-aim0.md` beside it predate this revision.

## Count table (words exclude equations, tables and image lines; captions included)

| line | section | words | largest block | figure | est. page share |
|---|---|---|---|---|---|
| 10 | 1.1 The problem | 731 | 158 | 1.1 | 48% |
| 69 | How the chapter proceeds | 208 | 144 | n | – |
| 87 | 1.2 intro | 125 | 125 | n | – |
| 98 | 1.2.1 Fixed bins | 142 | 108 | n (cites 1.2 C) | – |
| 111 | 1.2.2 Sliding window | 117 | 117 | n (cites 1.2 D) | – |
| 121 | 1.2.3 CFAR | 678 | 232 | n | – |
| 168 | 1.2.4 What each finds | 1220 | 613 (numbered list) | 1.2 + Table 1.1 | 59% |
| 258 | 1.3.1 Data, model | 1155 | 290 (caption) | 1.3, 1.4 | 59%, 57% |
| 345 | 1.3.2 Correlogram | 775 | 149 | n (uses 1.4 C) | – |
| 404 | 1.3.3 Windows | 1170 | 336 (caption) | 1.5 | 54% |
| 488 | 1.3.4 Assessor / count detector | 423 | 191 | n (uses 1.3, 1.4 E) | – |
| 523 | 1.4 What brute force found | 681 | 185 | 1.6 + Table 1.2 | 27% |
| 597 | The question, answer in brief | 347 | 203 | **n** | – |
| 626 | How predictions are tested | 477 | 181 | **n** | – |
| 665 | Prior work | 1051 | 193 | **n** | – |
| 747 | Contributions | 399 | 336 (list) | **n** | – |
| 781 | 1.5 intro | 122 | 122 | **n** | – |
| 792 | 1.5.1 Undercount | 99 | 78 | **n** | – |
| 804 | 1.5.2 Window sharing | 493 | 183 | 1.7 (at end) | 23% |
| 847 | 1.5.3 Expected counts | 350 | 89 | n | – |
| 878 | 1.5.4 Test | 565 | 251 | 1.8, 1.9 | 31%, 41% |
| 926 | 1.5.5 General form | 743 | 235 | 1.10 | 47% |
| 984 | 1.5.6 Joint fit | 862 | 287 | 1.11 + Table 1.3 | 43% |
| 1055 | 1.5.7 Realistic values | 781 | 262 | 1.12 + Tables 1.4, 1.5 | 29% |
| 1127 | 1.6 intro | 71 | 71 | n | – |
| 1135 | 1.6.1 Chance clusters | 816 | 221 | 1.13 | 28% |
| 1195 | 1.6.2 Jitter reading | 959 | 321 | 1.14 + Table 1.6 | 44% |
| 1272 | 1.7 Separation | 1029 | 361 | 1.15, 1.16 | 36%, 38% |
| 1343 | 1.8 intro | 60 | 60 | n | – |
| 1350 | 1.8.1 Membership | 617 | 155 | 1.17 | 19% |
| 1399 | 1.8.2 Order | 1410 | 258 | 1.18, 1.19 + Tables 1.7, 1.8 | 22%, 22% |
| 1527–1665 | 1.9.1–1.10 | 1318 | 319 | n (Table 1.9) | – |

- The body runs about 22,800 words with 19 figures and 9 tables.
- **Longest stretch with no figure:** from Figure 1.6 (line 567) to Figure 1.7 (line 833), about 2,800 words over seven consecutive subsections.

## Findings
Columns: location · issue · severity · suggested fix · could I verify it against a source (yes/no).

1. **Lines 597–832 (1.4 "The question" through 1.5.2)** · About 2,800 words and seven consecutive subsections with no figure. They include a methods subsection ("How the predictions are tested", 477 words) that defines four named simulation runs a reader must keep straight for the rest of the chapter · **major**
   - (a) Add a **run map**: the planted (σ, k) plane, with markers showing which run covers each point, for the first-experiment and held-out grid, the realistic points (45 min and 20 min) and the denser-train check, each labeled with its event count. Figure 1.12 already draws this plane, so either extend it and move it into 1.4, or cite it here.
   - (b) Move Figure 1.7 to the head of 1.5.1. 1.5.1 states k̂ = 2 + (k − 2)g₃/g₂, and Figure 1.7 B draws exactly that.
   - (c) Prose is right for "Prior work" and "Contributions", which are attribution. Consider moving Table 1.9 up beside them.
   · yes

2. **1.5.7 Table 1.5, the 1.4 "answer in brief" (lines 619–623) and 1.10 Conclusion (lines 1656–1660)** · The chapter's practical headline has no figure anywhere: how many events in one 20-minute segment it takes to read participants, rate, jitter and order. It exists as a typed 4×10 table plus prose, told three times · **major**
   - Replace with an **"events needed" figure**:
     - x axis: events per segment (1, 2, 4, 8, 16, log scale);
     - y axis: share of 40 recordings within 0.8–1.25, with a line per stream × cell count;
     - one panel each for participants (joint fit, and the tool's 1 s estimate) and rate;
     - one order-power panel (the Figure 1.19 data) on the same x axis;
     - a shaded band for the median segment (1–2 events), and a 0.8 line.
   - The data are in Table 1.5, `window_counts.py` and Table 1.7.
   - Put the figure in 1.5.7, then point to it from 1.4 and 1.10. Move Table 1.5 to an appendix.
   · yes

3. **1.2.1–1.2.3 (lines 98–166) and Figure 1.2's placement** · About 940 words of detector mechanism cite "Figure 1.2 C" and "Figure 1.2 D" before the figure appears at line 170. CFAR (678 words) explains reference cells, guard cells and the cell under test in prose only, and these are radar terms an outside reader has never seen · **major**
   - Move Figure 1.2 to just after the 1.2 intro (line 96).
   - Add a **CFAR schematic**: a time axis, the instant t, the ±5 s guard, the 5–35 s reference stretches on each side, and the threshold set from b̂.
   - Draw the chance-floor formula at line 131 as chance calls per hour against K for the 2 s sliding window at 0.0096 and 0.05 Hz, with the 1-per-hour line. Best done as added series in Figure 1.13, which would also show why 1.2.3 gives 6/12 cells and 1.6.1 gives 5/8 (the 1 s bins versus the 2 s sliding window, stated in prose at lines 1170–1171).
   · yes

4. **1.6.2, Table 1.6 against Figure 1.14** · The row that the text (line 1252) calls "the rows that test the mixture as a mixture", 0.01 Hz at K = 3, is only in the table. The figure draws 0.01 Hz K = 4 and 0.05 Hz K = 3, 4 and 6. Panels B and C tell the same flat-line story twice · **major**
   - Add a 0.01 Hz, K = 3 panel.
   - Merge B and C, or lay out 2×3.
   - Move Table 1.6 to an appendix.
   · yes

5. **1.8.2 frame-rounding paragraph (lines 1492–1505, about 300 words)** · Rounding raises realistic power sharply, for example 0.06 to 0.66 at E = 2 for 7 cells, r = 2.5, σ = 0.105 s. That is the realistic-value order result, and it is prose only. Figure 1.19 and Table 1.7 show unrounded power · **major**
   - Add rounded-onset power at realistic σ to Figure 1.19 as a second line style, or as a paired dot plot (unrounded → rounded) per point.
   · yes

6. **Table 1.7 against Figure 1.19** · Exact duplicate · minor · Move Table 1.7 to an appendix · yes

7. **Table 1.3 against Figure 1.11 A, B** · The text (lines 1010–1015) argues from the "pooled as shipped" and "Gaussian conversion" columns, which the figure does not draw · minor · Add both as marker series in Figure 1.11 A, B, and move the table to an appendix · yes

8. **Table 1.4 against Figure 1.11 C** · The jitter column duplicates the figure's in-band annotations. The participants and rate columns are drawn nowhere · minor · Add participant and rate strips to Figure 1.11 C, or fold them into the figure from finding 2. Move the table to an appendix · yes

9. **Table 1.1 (8 columns of long header text)** · A typed table of shares and rates · minor
   - Make it a **dot plot**: share of draws found, for events 1–5 × the 3 detectors, with a hollow "by chance" marker for event 4.
   - Draw false-alarm rates in a small log-scale panel next to it, as Figure 1.2 E or its own figure.
   - Move the table to an appendix.
   · yes

10. **Figure 1.6 (est. 27% of a page)** · The figure that motivates the chapter is a 2×4 grid squeezed into 6.5 in: each panel is about 1.2 in wide, its tick labels are roughly 5 pt when printed, and the top legend takes about 10% of the canvas. Panels C and G (coordinated onset rate) sit flat at 1 and are not cited for any failure · major
    - **Reflow, not crop:** transpose to 4 rows × 2 columns, with background as the columns, at full width (about 6.5 × 8 in).
    - Or drop C and G and use 3 × 2.
    - Move the legend into a single strip.
    · yes

11. **Figure 1.16** · Panels E–H repeat A–D with separation measured from the onsets ("show the same result"), so half the canvas goes on a robustness check · minor · Overlay the realized-separation points as open markers in A–D, or move E–H to an appendix, and give A–D a full-width 2×2 · yes

12. **Figure 1.15** · The legend fills the right half of the bottom row (about 25% of the canvas), and panel D gets half the width · minor · Move the legend into a strip under A–C and give D the full width · yes

13. **Figure 1.18** · Three legend blocks below the panels take about 30% of the figure's height · minor · Label lines directly in each panel and remove the legend blocks · yes

14. **Figure 1.8** · The 0.2–2.5 axes push the participant points (A, D) into a corner. The claims (about 1% overprediction; about 0.05 without the at-most-one-event term) cannot be seen at this scale, and Figure 1.9 carries the participant result instead · minor
    - Set a per-panel range for participants (about 0.3–1.1).
    - Or drop A and D and add the Poisson-train residual as gray points in Figure 1.9.
    · yes

15. **Captions that carry the argument** · minor each. Relocate, don't delete: move the results and reasoning to the body or to notes, and keep each caption to what the figure shows and why it matters.
    - Figure 1.9 (251 words): "24 of 32, p = 0.007" and "17 of 48" appear in the caption, again in body lines 888–901, and a third time in a 3-line stats header above each panel. That header is a title above the plot, which is agent 10's house-rule boundary. The header also says "held-out record" where the text says "held-out rerun".
    - Figure 1.10 (235 words): ends with findings that repeat lines 973–982.
    - Figure 1.11 (287 words): lists the in-band counts that are printed in the figure and again in Table 1.4, four times in all.
    - Figure 1.12 (262 words): restates ranges and the 2/40 and 16/40 that are printed in the figure.
    - Figure 1.5 (336 words): re-derives panel C's worked example, which the panel already prints in full.
    - Figure 1.13 (209 words): carries the threshold argument (K = 5 is safe; one threshold cannot serve both backgrounds) that repeats lines 1167–1173.
    · yes

16. **Where prose is right, and why** · no finding
    - "How the chapter proceeds": a short roadmap.
    - Prior work and Table 1.9: attribution and lineage.
    - Contributions, 1.9.4 Limitations, 1.9.5 Next steps: lists of claims and caveats, which belong in words.
    - 1.3.2–1.3.4 derivations: already drawn in Figure 1.4 C–E.
    - The 1.2.4 numbered list (613 words): each item points at a panel of Figure 1.2. It could be shorter if finding 9 moves the numbers into a figure.

## What I checked
- The whole artifact (lines 1–1793).
- All 19 PNGs, opened as images, plus their pixel size and dpi.
- House rules "Show the picture" and "Plot conventions".
- The Dropbox .docx's image sizes, which is how I found it is stale.
- I did not read anything under docs/reviews/.
