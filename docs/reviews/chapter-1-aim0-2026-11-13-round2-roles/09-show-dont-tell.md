GRANT 9 MISMATCH — missing none; holds Edit, Write, PowerShell, Agent, Artifact, Skill, ToolSearch, Claude Docs batch/update (NotebookEdit also reachable through deferred tool search)

**Run note (about the run, not the artifact):** the harness gave this reviewer editing and publishing tools that the role does not grant. I used none of them on the repository, and every file I wrote is under `<scratch>/mb2/role09/`. The run record's `roles:` line should therefore say this role ran on a fallback path, not as the named agent. To measure the rendered page I called `powershell.exe` from Bash to drive Word read-only on a scratch .docx.

# Murderboard role 9: Show, Don't Tell. Chapter 1 (blob 0acfccbb, verified with `git hash-object`)

## What I measured, and how
- **Render:** built a .docx from the chapter with the project's own recipe (pandoc 3.9, `-f gfm -t docx --resource-path=.`, run from the chapter folder) into `<scratch>`. Word then reported page geometry, the page each figure and table lands on, each figure's rendered size, and the word count on every page. The result is **59 pages** on Letter paper with 1 in margins, so the text block is 468 × 648 pt.
- **Figures:** I opened all 19 PNGs.
- **Thresholds.** The role's slide defaults (40 words per slide, 60-word text blocks) are meaningless for a dissertation page: every page fails them, and the median page holds about 400 words. I used these project-tunable conventions instead:
  - flag a results or methods subsection with no figure of its own;
  - flag 3 or more consecutive figure-free pages inside methods or results;
  - flag a prose block over 200 words, and a caption over 150 words;
  - flag a figure under 50% of the page area, which I also report as a share of the text block;
  - flag a figure that does not fill the text column.

## Count table: one row per rendered page
Page share (shown as "share") is figure area ÷ page area; the second number is figure area ÷ text block. T = a typed table is on the page.

| page | words | figure | share (page / text block) |
|---|---|---|---|
| 1 | 283 | n | – |
| 2 | 177 | **1.1** | 38% / 61% |
| 3–5 | 526, 535, 441 | n | – |
| 6 | 65 | **1.2** | 47% / 75% |
| 7 | 503 | n (T1.1) | – |
| 8–9 | 627, 515 | n | – |
| 10 | 82 | **1.3** | 48% / 76% |
| 11 | 292 | n | – |
| 12 | 109 | **1.4** | 46% / 74% |
| 13–15 | 555, 543, 575 | n | – |
| 16 | 143 | **1.5** | 44% / 70% |
| 17–18 | 596, 399 | n | – |
| 19 | 237 | **1.6** (T1.2) | 22% / 35% |
| 20–25 | 590, 491, 508, 514, 505, 415 | n | – |
| 26 | 364 | **1.7** | 19% / 30% |
| 27 | 252 | **1.8** | 25% / 40% |
| 28 | 235 | **1.9** | 33% / 53% |
| 29 | 350 | n | – |
| 30 | 190 | **1.10** | 38% / 61% |
| 31–32 | 560, 393 | n | – |
| 33 | 267 | **1.11** | 34% / 55% |
| 34 | 343 | n (T1.3) | – |
| 35 | 396 | **1.12** | 23% / 37% |
| 36 | 520 | n (T1.4, T1.5) | – |
| 37 | 281 | **1.13** | 23% / 36% |
| 38–39 | 631, 337 | n (T1.6) | – |
| 40 | 218 | **1.14** | 35% / 57% |
| 41 | 603 | n | – |
| 42 | 327 | **1.15** | 29% / 47% |
| 43 | 392 | n | – |
| 44 | 223 | **1.16** | 30% / 48% |
| 45 | 414 | **1.17** | 15% / 24% |
| 46 | 432 | n | – |
| 47 | 402 | **1.18** | 18% / 29% |
| 48 | 387 | **1.19** | 17% / 28% |
| 49–50 | 496, 427 | n (T1.7, T1.8) | – |
| 51 | **0** | n | – |
| 52–59 | 448, 471, 486, 244, 316, 370, 345, 129 | n (T1.9) | – |

**Summary**
- **Under 50% of the page:** every figure (19 of 19), ranging from 15% to 48%.
- **Under 50% of the text block:** 9 of 19.
- **Width:** every figure renders 420 pt (5.83 in) wide in a 468 pt (6.5 in) column, left-aligned. The figure is narrower than the text above it.
- **Figure-free runs:**
  - 6 consecutive pages, 20–25 (1.4 "The question" through 1.5.2);
  - 3-page runs at pages 3–5, 7–9 and 13–15;
  - 11 pages at 49–59, which are discussion, end matter and references.
- **Long blocks:** 24 prose blocks exceed 150 words and 4 exceed 200 (lines 428, 572, 1127, 1449). 14 captions exceed 150 words; the largest is Figure 1.5 at 329.

## Owner's two requests: verdicts
1. **"Lead with a figure of the problem": met in content, missed in placement.**
   - Figure 1.1 is the right picture. Its three rasters (background alone, events alone, what the analyst receives) state the problem without words.
   - But it renders on page 2. Page 1 is 283 words of text with no figure, because the figure is 6.15 in tall (aspect 0.95) and cannot fit beneath the preamble and two paragraphs.
2. **"Show each method's successes and failures graphically": met for the detectors in one draw and for most measuring tools; missed for the statistics and for the take-home.**
   - The detectors' 200-draw success rates (Table 1.1) are a typed table.
   - The realistic-value readability results (Tables 1.4 and 1.5), which are the practical answer for Chapter 3, have no figure.
   - The chapter's answer appears three times (1.4 "answer in brief", 1.9.1, 1.10) and is prose-only every time.

## Findings
Columns: location · issue · severity · suggested fix · verifiable against a source?

1. **1.10 Conclusion (line 1607) and 1.4 "The question, and the answer in brief" (line 572, 196 words); the take-home is prose-only.**
   - **Issue:** a 197-word paragraph lists how many events per 20-minute segment each property needs: participants from 2 events (13 cells) or about 8 (7 cells); rate from 4 or 16; jitter never; order from 3 events with a strong template. This is the chapter's result for Chapter 3, and it is a chart typed as sentences. Neither the conclusion nor the 1.4 answer-in-brief has a figure.
   - **Severity:** **major.**
   - **Fix:** add a **readability chart**.
     - x-axis: events per 20-min segment, log scale, 1–16.
     - One row per property × cell count: participants (joint fit and the tool's 1 s estimate), rate, jitter, order.
     - Each row is a bar from the event count at which the property becomes readable (≥ 36 of 40 recordings in band, or power ≥ 0.8), with "never" marked at the right edge.
     - Overlay the lab's histogram of events per segment (fast and slow streams; median 1–2, 28 and 25 of 66 segments with none) as a strip along the x-axis.
     - Place it in 1.4 as the "answer in brief", with a 2-line caption, and point at it again from 1.10.
     - It also absorbs Table 1.5, which can move to an appendix.
   - **Verifiable:** yes. Tables 1.4, 1.5 and 1.7 and the 1.3.1 segment counts hold every number.

2. **Every figure; rendered width and page share (render measurement).**
   - **Issue:** all 19 figures render at 420 pt in a 468 pt column, left-aligned, with 120 pt (1.7 in, 20% of page width) of empty space on the right. This is pandoc's default image width, not a design choice. No figure reaches half the page.
   - Panel text shrinks badly, because the figures are drawn 1,430–1,800 px wide (150 dpi, 130 dpi for some):
     - text drawn at 10 pt renders at about 4.5–5.8 pt in 15 of the 19 figures;
     - it renders at about 8 pt only in Figures 1.1, 1.2 and 1.4.
   - **Severity:** **major.**
   - **Fix (reflow, not crop):**
     - give every figure the full 6.5 in column, with an explicit width in the build or a reference .docx;
     - put the 6- to 8-panel figures on their own landscape page, each with a 2-line caption footer and the rest of the caption moved to the body text: 1.3, 1.6, 1.9, 1.15, 1.16;
     - redraw the wide, short figures (1.7, 1.17, 1.18, 1.19, at 15–19% of the page) at their final width, so their type is not halved.
   - Boundary: agent 10 owns font size as a defect. This row owns the layout policy that causes it.
   - **Verifiable:** yes, by Word's InlineShape sizes on the recipe build.

3. **Figure 1.1 placement (lines 25–38).**
   - **Issue:** the problem figure lands on page 2. Page 1 is all text.
   - **Severity:** **major**, because the owner asked for it explicitly.
   - **Fix:**
     - redraw Figure 1.1 at about 6.5 × 3.8 in, with three shorter raster lanes (33 rows fit in about 1.1 in each);
     - place it directly after the first paragraph of "The problem";
     - move the second paragraph's definitions (recording, frame, onset, channel) below it, so page 1 ends on the picture.
   - **Verifiable:** yes, by render.

4. **Table 1.1 (lines 180–193); the detectors' success and failure rates are typed.**
   - **Issue:** an 8-column table, cramped at 6.5 in, carries the 200-draw shares found for 3 detectors × 5 situations plus false-alarm rates. Figure 1.2 shows a single draw only.
   - **Severity:** **major**, because it is the owner's second request.
   - **Fix:** add a **dot matrix** as Figure 1.2 E, or a new figure.
     - Rows are detectors and columns are situations 1–5.
     - Dot fill is the share found on a green-to-red scale, and the number is printed in the dot.
     - A hollow ring shows the "by chance" share for situation 4.
     - A right-hand column of short bars gives false alarms per hour in each background on a log axis, with the one-per-hour allowance drawn.
     - Move Table 1.1 to an appendix.
   - **Verifiable:** yes, from Table 1.1.

5. **1.2.4 numbered list (lines 197–227, about 537 words) after Figure 1.2.**
   - **Issue:** five paragraphs explain mechanisms the reader must map back onto the figure by event number.
   - **Severity:** minor.
   - **Fix:** label each mechanism in Figure 1.2 A under its event number ("bin border", "masking", "merge gap", "clutter / chance floor", "below floor"). The list can then keep only the numbers and the cause. Keep the CFAR caveats in the text, relocated rather than deleted.
   - **Verifiable:** yes.

6. **1.7 punchline (lines 1268–1285); the comparison of separation limits with real intervals is prose.**
   - **Issue:** "between about 0.5 and 2.5 s the tools merge pairs that onset times could separate … rarely binds at realistic intervals (5th percentile 3.8 s; 98 %; 7 % and 1 % merged)." Figures 1.15 and 1.16 show the limits but not the interval distribution they are compared against.
   - **Severity:** major.
   - **Fix:** add a **histogram (or empirical CDF) of the measured inter-event intervals**, fast and slow, on a log time axis.
     - Shade the band of the likelihood-ratio tests (0.26–0.76 s).
     - Draw vertical lines at the assessor's 2.5 s and the count detector's 5 s.
     - Mark the 2 s merge censoring of the lists themselves.
     - Use it as Figure 1.16's first panel, and move 1.16 E–H (the same result against realized separation) to an appendix.
   - **Verifiable:** yes. The interval lists are in the run record.

7. **Pages 20–25; six consecutive figure-free pages** (1.4 "The question", "How the predictions are tested", "Prior work", "Contributions", the 1.5 intro).
   - **Severity:** major for "How the predictions are tested"; prose is right for "Prior work".
   - **Fix:**
     - "How the predictions are tested" (lines 595–631, 483 words) describes four simulation campaigns in prose: the first experiment, the held-out rerun, the realistic 45-minute runs and the 20-minute fixed-count runs, plus the denser check. Replace it with a **design schematic**: one row per campaign showing the grid axes, recordings and seeds, and which sections and figures use it.
     - "Prior work" is correctly prose. It is a literature argument with no quantity to plot.
     - Its content is stated three times ("What is missing", "Contributions" and Table 1.9, pages 23–24 and 52). Keep Table 1.9, keep the contributions as a 7-line list, and move the status tags into Table 1.9 only.
   - **Verifiable:** partly. The design facts are in the text.

8. **1.8.2 frame-rounding paragraph (line 1449, 245 words).**
   - **Issue:** before-and-after power numbers are typed: "0.06 to 0.66 at E = 2, 0.18 to 0.73 at E = 3, 0.69 to 0.92 at E = 5".
   - **Severity:** minor.
   - **Fix:** add rounded-onset power to Figure 1.19 as a third panel, or as paired arrows from unrounded to rounded power at each E. The modelling caveat stays in the text.
   - **Verifiable:** yes.

9. **Tables duplicated by figures: Table 1.6 duplicates Figure 1.14; Table 1.7 duplicates Figure 1.19; Table 1.3 mostly duplicates Figure 1.11 A–B.**
   - **Issue:** the reader gets the same result twice, and the tables push figures apart. For example, Table 1.6 sits on page 39 between the 1.6.1 figure and Figure 1.14.
   - **Severity:** minor.
   - **Fix:** relocate the three tables to an appendix and keep the figures. The extra columns of Table 1.3 (pooled-as-shipped, Gaussian conversion) can go to the appendix with it; the counts off the calibration curve are already printed in Figure 1.11.
   - **Verifiable:** yes.

10. **Table 1.4 (line 1046); the 45-minute joint-fit results.**
    - **Issue:** the jitter column is already shown as strips in Figure 1.11 C, but the participant and rate columns are typed only.
    - **Severity:** minor.
    - **Fix:** add participants and rate as two more strip groups next to Figure 1.11 C, same layout and same 0.8–1.25 band. Then move Table 1.4 to an appendix.
    - **Verifiable:** yes.

11. **Captions carry the argument.**
    - **Issue:** captions run 74–329 words (median about 200), and several repeat or interpret the body:
      - Figure 1.9's caption restates "24 of 32 conditions (p = 0.007)" and "17 of 48", which the body (line 851) and the figure's own header text also state, so the result appears three times;
      - Figure 1.14 ends with an interpretation sentence;
      - Figure 1.5 (329 words) explains the mechanisms of 1.8.1 and 1.8.2.
    - **Severity:** minor.
    - **Fix:**
      - cut each caption to what is shown plus why it matters, at most about 80–100 words;
      - move the statistics and interpretation to the body, or to a notes appendix;
      - split Figure 1.5 B–C off to sit with 1.8, which also shortens its caption by about 150 words.
    - **Verifiable:** yes.

12. **Results subsections with no figure of their own: 1.3.2 (720 words, pages 13–14), 1.3.4, 1.5.3 (340 words).**
    - **Issue:** 1.3.2 and 1.3.4 point at Figure 1.4, a page or more away, which is acceptable. 1.5.3 derives the at-most-one-event (hard-core) term and the surrogate term in prose and equations.
    - **Severity:** minor.
    - **Fix:**
      - 1.5.3: add a small mechanism schematic. One event per window under the 20 s hard core, against two events sharing a window under a Poisson train, with the pairs each adds; or point to the 4–8 s downturn in Figure 1.4 D.
      - 1.3.2: prose and equations are right for the derivation itself.
    - **Verifiable:** n/a, a judgment.

13. **Discussion and end matter (pages 49–59) are figure-free.**
    - **Assessment:** prose is right for limitations, next steps and references. Table 1.9 is a precedent table and correctly a table. 1.9.1 should point at the readability chart from finding 1 rather than re-list results.
    - **Severity:** none / minor.
    - **Verifiable:** n/a.

14. **Figures 1.9, 1.10, 1.11, 1.15 and 1.16 carry text headers above the panels** (statistics lines, set descriptions).
    - **Issue:** this conflicts with the CLAUDE.md rule "no titles above plots". It is noted here only because it is the in-figure form of caption sprawl.
    - **Severity:** minor. The mechanical check belongs to agent 10.
    - **Fix:** move the statistics into the body text or the caption, and put set identity into y-axis or legend labels.
    - **Verifiable:** yes.

**Boundary note for agent 10:** rendered page 51 is blank (0 words), between Table 1.8 on page 50 and 1.9.3 on page 52. This looks like a build or geometry artifact of the pandoc → Word render, so I report it but do not judge it.

**Checked and passed:**
- Figures 1.2, 1.6, 1.8, 1.12, 1.13 and 1.14 each show a method's success and failure regions directly. The flat jitter reading, the chance floor crossing the one-per-hour line, and the resolved / unresolved grid all read without the text.
- Figure 1.1's content is the right lead picture.
- Prose is the right medium for the CFAR history, the generative-model definition and the prior-work argument.
