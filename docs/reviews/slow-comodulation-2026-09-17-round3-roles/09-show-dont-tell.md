GRANT 9 MISMATCH — missing Grep, Glob; holds no forbidden tools (held: Read, Bash)

The missing tools didn't limit the review: I used `grep` and `ls` through Bash instead. No reviewer should hold an editing tool, and I hold none. Nothing was written to the repo, and my scratch directory `<scratchpad>/review3/r9/` is empty.

# Density & figure-first review: `<worktree>/docs/learned/slow_comodulation/README.md`

**Verdict:** the figures themselves are good and fill the column. The page still reads prose-first: **818 words (about 1,300 rendered px) come before the first picture**. Figures take up about **37 %** of the page's height. And **the headline claim, that the minute-scale excess sits in some recordings and some groups, appears in no figure at all.**

## Thresholds used
These are adapted from the slide defaults to a GitHub page, and the project can tune them:
- A text block over 60 words is flagged.
- A results or methods section with no figure is flagged.
- Figure share is measured as rendered figure height over total section height, and flagged under 50 %.
- Blank horizontal bands of 40 px or more (source pixels) inside a figure count as wasted canvas.
- Figure text is flagged when its em size falls below 12 px; GitHub body text is 16 px.
- Text height is an estimate: 16 px font, 24 px line height, about 16 words per line at 880 px, plus 16 px between blocks.

## Count table (per section)

| section | visible words | largest block (words) | figure | fig px / text px (est.) | fig share |
|---|---|---|---|---|---|
| title + "Why this page exists" | 138 | 138 | n | 0 / 232 | 0 % |
| The short answer | 315 | 83 (roadmap), 80 (fast-stream bullet) | **n (results)** | 0 / 640 | 0 % |
| Two ways ROIs are active together | 580 | 173 (Figure 1 caption), 148, 141 | y | 968 / 1048 | **48 %** |
| Two measurements | 335 | 136, 128 | **n (methods)** | 0 / 576 | 0 % |
| What the surrogates remove | 515 | 143 (Figure 3 caption), 87 | y (2) | 1672 / 1032 | 62 % |
| What the recordings hold | 660 (+508 collapsed) | 155 (lab fast bullet), 139 (Figure 4 caption), 114, 101 | y (2) | 1274 / 1168 | 52 % |
| By group | 423 | 137, 87 | y | 810 / 832 | **49 %** |
| What this changes for the label-free thread | 300 | 116 | **n (argued results)** | 0 / 624 | 0 % |
| The decision this sets up | 201 | 174 | n | 0 / 344 | 0 % |
| What this does not settle | 250 | 43 | n (caveats; prose is right) | 0 / 584 | 0 % |
| Published lineage | 424 | 126 | n (reference; prose is right) | 0 / 752 | 0 % |
| Reproduce | 214 | 151 | n (reference; prose is right) | 0 / 368 | 0 % |
| **whole page** | **4,355 (+508)** | 38 blocks over 40 words | 6 figures | 4,724 / ~8,200 | **~37 %** |

## Figure geometry at an 880 px column (measured with PIL)

| figure | source px | rendered | blank bands | left/right ink margin | smallest text (11 pt at 150 dpi) |
|---|---|---|---|---|---|
| Figure 1, the two kinds | 1800×1980 | 880×968 | 124 px (13 %) | 26/7 px | 11.2 px em, cap height about 8 px |
| Figure 2, the surrogates drawn | 1800×1260 | 880×616 | 33 px (5 %) | 1/17 px | 11.2 px em |
| Figure 3, what the surrogates remove | 1875×2250 | 880×1056 | **244 px (23 %)**; 96 px empty below the legend | 24/11 px | 10.8 px em |
| Figure 4, how much the count varies | 1875×840 | 880×394 | 40 px (10 %) | 32/8 px | 11.7 px (12 pt ticks) |
| Figure 5, the recordings' correlograms | 1875×1875 | 880×880 | 108 px (12 %); 66 px empty at the bottom | 4/**0** px | 11.7 px |
| Figure 6, by group | 1875×1725 | 880×810 | 77 px (9 %) | 16/2 px | 10.8 px em (the y-labels) |

No figure was auto-shrunk: every one fills the column, with side margins of 32 px or less, so no margin flag applies.

## Findings
Each finding gives the location, the issue, its severity, the suggested fix, and whether I verified it.

1. **The short answer and the page opening: 818 words before Figure 1, and the results summary has no figure.**
   - **Issue:** The lead asked for "a figure or a doc" and the project rule is to show the picture first. Instead there is a 138-word standfirst, five result bullets and an 83-word roadmap, all prose.
   - **Severity:** major.
   - **Fix:** Add a **headline figure** directly under the standfirst. It should be a per-recording strip plot of the 1-minute count-variance ratio for lab fast, lab slow and Dard et al., with two columns per dataset (as recorded; episodes removed, then block control). Colour the dots by group, draw the pooled estimate with its 95 % whisker over each strip, and put a dashed line at 1.
     - That one figure carries the three dataset bullets and the "median recording 1.3 / 0.96 detrended" claim.
     - Cut the bullets to one assertion each, pointing at it.
     - The roadmap sentence listing the page order is navigation that GitHub's heading outline already gives. Keep only the one-line decision question and its link.
     - Move the standfirst's provenance (the report on `main` and the unmerged revision branch) to a footer line or a `<details>` block. Keep all of it.
   - **Verified:** yes (word count and layout measured).

2. **What the recordings hold, and the collapsed per-recording table: the claim that the excess is "concentrated in some recordings" is shown only as numbers.**
   - **Issue:** Figures 4 and 5 are pooled. The per-recording median, quartiles, share above 1 and the leave-five-out check exist only in a 155-word bullet and a collapsed table.
   - **Severity:** major.
   - **Fix:** The headline strip plot from the first finding shows this. After it, cut the lab fast (155 words), lab slow (114) and Dard et al. (101) bullets to one assertion and one number each. The interval values are already in the `<details>` table, so leave them there. The effective-mice bullet repeats the same point in What this does not settle; keep that copy only.
   - **Verified:** yes (compared figure contents against the text).

3. **By group, the 137-word paragraph: a 4-group × 2-statistic comparison is typed out as prose.**
   - **Issue:** Pooled ratios 3.71/2.83/1.96/3.30 and medians 2.94/1.81/1.20/1.32 are written in a sentence. Figure 6 shows correlograms, not these ratios.
   - **Severity:** minor.
   - **Fix:** Either split the headline strip plot by group, or add a small **grouped dot chart** (x: group; pooled ratio as a filled dot, per-recording median as a hollow dot; fast and slow side by side). Keep the ⚠ note that group is confounded with imaging day in the text, next to the chart.
   - **Verified:** yes.

4. **Figure 1, the two kinds, rows A–F: the top two rows don't show the distinction the figure exists to show.**
   - **Issue:** At 10 s bins, with about 3 onsets per bin, the planted-event, 20 s and 5-minute share-lit traces (A–C) all look like Poisson noise. A 1-minute raster (D–F) can't show a 5-minute modulation at all, and F looks like E. Only the correlograms (G and H) carry the message. About 60 % of the figure's 968 px goes to panels that don't tell the worlds apart.
   - **Severity:** major.
   - **Fix:**
     - Redraw A–C at **1-minute bins**, the bin width the page's headline ratio uses. Show the planted shared multiplier in a lane above each trace, not over it.
     - Keep one raster (D, the planted event) and drop E and F. That frees room for G and H.
     - The log-lag and linear-lag correlograms (G and H) show the same curves twice. They could become one row of two columns.
   - **Verified:** yes (read the rendered image).

5. **Captions of Figure 1 (173 words), Figure 3 (143), Figure 4 (139) and Figure 5 (94) carry methods and definitions, not "what it shows and why".**
   - **Severity:** minor.
   - **Fix:** Relocate these, don't delete them:
     - **Figure 1:** move the generator parameters (0.0097 onsets per ROI per second; 15 events of 3–7 ROIs; how depth was chosen) into a `<details>` block called "Synthetic worlds".
     - **Figure 3:** move the definitions of "arm" and "episodes removed, then block control" into the prose before the figure. Move the 20 s window trim to the same `<details>` block.
     - **Figure 4:** move the dataset sizes (84 recordings from 44 mice; 59 from 32; 17–25 min; 566 ROIs median) to "The data" paragraph. The axis labels already carry the counts.
     - **Figure 5:** move CoactDetect's operating point (2 s bins, 60 s context, α = 10⁻⁴, 3 s merge) to "The data" paragraph or a `<details>` block.
     - **Figure 6:** move the provenance of how the group labels are read into the paragraph below it.
   - **Verified:** yes.

6. **Two measurements: a prose-only methods section (336 words; blocks of 128, 136 and 71 words).**
   - **Severity:** minor.
   - **Fix:** Prose is right for the definitions, but they should be shown as display math, which GitHub renders from `$$…$$`: excess(ℓ) = observed/expected − 1; ratio = Var(population count)/Var_circular ≈ 1 + (N − 1)·r̄. Add a two-panel **schematic** next to them:
     - left: a toy population count at bin width *w*, recorded next to its circular shift, labelled with both variances;
     - right: a correlogram with the "event peak" and "shoulder out to *T*" marked, and the area out to lag *w* shaded to show that count variance sums the correlogram.

     Move the ⚠ caveat that both measures are relative to the window average into What this does not settle, and leave a one-line pointer here.
   - **Verified:** yes.

7. **Two ways ROIs are active together, the 148-word paragraph defining the surrogates: Figure 2, which draws them, sits a whole section later.**
   - **Severity:** minor.
   - **Fix:** Reflow by moving Figure 2 up next to this paragraph so it carries the definitions, and cut the paragraph to one line per surrogate. That also lifts this section above 50 % figure share (currently 48 %).
   - **Verified:** yes.

8. **By group, the slow-stream dip aside, extractor dead-time bullet (87 words): a histogram typed as numbers.**
   - **Issue:** "15 at 2.8–3.4 s, 95…, 333…, 771…, about 1,050 beyond" is a histogram written out.
   - **Severity:** minor.
   - **Fix:** Draw a small **within-ROI inter-onset interval histogram** for the slow stream, 0–10 s, counts per second of interval. Mark the 2.7–5.4 s dip range in a lane above it and draw the Dard et al. histogram beside it. The numbers can go into the `<details>` block. Separately, the aside is about the slow stream, not groups, and is referenced from the lab slow bullet. Where it belongs is a sequence judgment, which I pass on without ruling on it.
   - **Verified:** yes.

9. **What this changes for the label-free thread, 116-word bullet: rigid-shift survival fractions in prose.**
   - **Issue:** "a tenth of the 1-minute excess… half of the 10 s… nearly all of the 1 s" has no figure.
   - **Severity:** minor.
   - **Fix:** Add a **dot chart**: x is bin width (1 s, 10 s, 1 min); y is the share of excess that rigid shift at *J* = 20 s removes, (as recorded − rigid shift)/(as recorded − 1); one colour per dataset. The inputs are already in the table; lab fast gives about 90 %, 52 % and 10 %. The cross-branch model-score check (95.8–100 % against 52–62 %) can stay in prose because it comes from another branch's run.
   - **Verified:** yes (the fractions were computed from the collapsed table).

10. **The decision this sets up, 174-word paragraph: a list of candidate sources written as running prose.**
    - **Severity:** minor.
    - **Fix:** Use a **table**: candidate source (network state; focus or slice position; bleaching; drifting baseline threshold; motion-correction artefact; pup movement) · what would distinguish it · whose question it is (lab, producer, Dard et al. authors). Keep the ⚠ note that no one has asked yet under the table.
    - **Verified:** yes.

11. **Figure 3 and Figure 5: canvas lost to blank bands.**
    - **Issue:** In Figure 3, 23 % of its height is blank, including 96 px under the legend and 64 px between rows. In Figure 5, 66 px under the legend are empty.
    - **Severity:** minor.
    - **Fix:** For Figure 3, move the two-column legend to the right of the count-ratio panel (F), which has room, and trim the bottom margin. For Figure 5, trim the bottom margin.
    - **Verified:** yes (PIL row scan).

12. **Figure 6, panel A (fast stream as recorded): the y-range runs −0.8 to 0.8, but the data sit between about −0.2 and 0.8.**
    - **Issue:** About 40 % of the panel is empty. It matches panel B's range, but the house rule is that y is not linked across rows.
    - **Severity:** minor.
    - **Fix:** Set panel A to about −0.25 to 0.8.
    - **Verified:** yes.

13. **Smallest text in all six figures is 10.8–11.2 px em (cap height about 8 px), against 16 px body text.**
    - **Issue:** The worst case is Figure 6's rotated two-line y-labels at 11 pt.
    - **Severity:** minor.
    - **Fix:** Raise the 11 pt labels to 13 pt at the current figure widths, or narrow the figures (figsize 12.5 in) so each is scaled down less to fit 880 px.
    - **Verified:** yes (from the font sizes and dpi in `<worktree>/tools/make_slow_comodulation_figure.py` and the measured scale).

14. **Where prose is right, and why (no fix needed):**
    - What this does not settle is a list of caveats.
    - Published lineage is citations.
    - Reproduce holds commands and a test list.
    - The paragraph pointing at the darkroom-only real-recording figure has to describe it in words, because FOUNDATIONS §5 keeps that figure off the public page.
    - **Verified:** yes.

## Passed to Ship It (agent 10)
These are mechanical defects I saw; I have not filed them as density findings:
- **Figure 1:** the rotated y-labels on the B and C share-lit traces overlap the neighbouring panels' "20m" tick labels.
- **Figure 5:** the right edge is clipped: the "5m" tick and "(log sca…" on the Dard et al. zoom panel (F) are cut off, with 0 px margin.
- **Figure 6:** dashed per-mouse curves leave the view with no "curve above the view" mark: MALE in panel D and ORX in panel C at the top, OVX in panel C at the bottom.

Files examined:
- `<worktree>/docs/learned/slow_comodulation/README.md`
- the six `fig*.png` files beside it
- `<worktree>/tools/make_slow_comodulation_figure.py`
