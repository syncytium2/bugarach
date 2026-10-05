GRANT 9 ok — Read, Grep, Glob, Bash

I hold no editing tool. The only other tool I have is SubagentHandback. I did not edit any file.

# Role 9: density and figure-first. Blind review, round 3

**Artifact:** `<worktree>/docs/learned/runs/2026-09-25-final-parameters/README.md`, 6,523 words, plus figure1_fresh_f1.png, figure2_cross_stream.png, figure3_elevated_rate.png and figure4_bench_floors.png. I opened all four figures. I did not open the earlier-round review folder.

**Thresholds I used.** These are conventions, not researched optima.
- This is a Markdown page, not a slide deck. My unit is one decision section, not one slide.
- The 40-words-per-slide rule does not fit a decision memo, so I did not apply it.
- I did apply these: any single text block over 60 words; a results section with no figure; two or more prose-only results sections in a row; a figure placed away from the decision that cites it.
- **Canvas share:** GitHub-style Markdown renders every image at the full column width, so each figure fills the column. I could not measure a rendered page because the page has no fixed canvas. So I judged share inside each figure: how much is plot, and how much is legend, embedded caption and white space.

## Count table (one row per section)

| section | words | largest single block | figure? | notes |
|---|---|---|---|---|
| Header + decisions at a glance | ~390 | 74 | n | at-a-glance table is good |
| D1 adopt four | 975 | 306 (under-floor table plus bullets) | y (Fig 1, at the end) | figure comes after about 800 words |
| D2 cross-stream | 217 | 88 (caption) | y (Fig 2) | |
| D3 budget failures | 538 | 127 | y (Fig 3, covers 1 of 4 failures) | 3 of 4 failures have no figure |
| D4 bench under floor | 299 | 153 | y (Fig 4) | prose table repeats Fig 4 and Table 3 |
| D5 hard limit | 234 | 112 | **n** | |
| D6 close-events | 75 | 71 | **n** | prose is right here |
| D7 alpha to cap | 190 | 182 | **n** | |
| D8 LoCo / context | 172 | 154 | **n** | |
| D9 guard cap | 187 | 183 | **n** | prose is right here |
| Full tables | 2,187 | 912 (Table 1) | n | appendix |
| Real data | 241 | 193 | **n** | a group result with no figure |
| Definitions | 468 | 468 | n | appendix, fine |
| What ran | 331 | 138 | n | provenance, fine |

**Consecutive sections with no figure:** Decisions 5, 6, 7, 8 and 9 (five decisions in a row), then Real data.

## Findings

Every finding below could be checked against the files: yes.

**1. D1, lines 39–122 · major.** Figure 1 comes last, after about 800 words of prose. Worse, it shows the wrong statistic for this decision.
- The text calls the paired fresh-seed gain "the independent check".
- Figure 1 shows unpaired shipped and proposal intervals. For combined binned SCE and combined SPIKE-synch those intervals visibly overlap, so the figure tells Tony "no clear gain" while the text says the gain is above zero.
- **Fix:** add a forest-plot panel of proposal minus shipped, with the paired 95% interval and a zero line: 4 rows, plus the 5 limit-held proposals in gray for Decision 5. Place it directly under the four-row table at line 49.
- Move the caveat bullets (lines 60–106) below the figure, or into notes under it. Relocate them; do not delete them.

**2. D1, "what the gain is made of", lines 66–69 · major.** The claim that the gain is mostly fewer decoy calls is argued in prose only. The evidence sits in Table 1's "without decoy calls" column, about 300 lines further down.
- **Fix:** give Figure 1 a second marker per point for F1 without decoy calls, as a hollow twin on the same row. The claim "near 1 for all" then becomes visible: the gain collapses once decoys are removed.

**3. D1, the under-floor calls table, lines 75–80, nested in a 306-word bullet · major.**
- **Fix:** turn this 4×3 "shipped → proposal of N" table into a slope chart. Use one small panel per level (lowest quiet, lowest busy, middle busy), draw shipped and proposal as two x positions with one line per proposal, and put the y-axis in calls on under-floor events per 120 events (or per 85 and 55 for the middle level).
- The drops (rate+context 34 → 2, fast SCE 22 → 5) are this decision's hidden cost, and a slope shows that at a glance.

**4. D3, lines 151–202 · major.** Figure 3 carries only the locust failure (1 of the 4 failures). The three precision-swing failures are argued in prose with numbers: 84 against 23 decoy calls, and precision 0.992 against 0.764.
- **Fix:** add a figure of precision on quiet against busy for each detector × stream, as a dumbbell. Show it twice, "as scored" and "without decoys", with the 0.10 and 0.15 swing limit as a band.
- That shows directly that fast SPIKE-synch's swing disappears without decoys, while fast rate+context's swing stays.
- Locust's old-layout figure (1.83) against the new one (5.00) per minute could be one added marker on Figure 3's slow locust column, against the 4.0 bar.

**5. D1 and D3, placement of Figure 3 · minor.** Decision 1 cites Figure 3 for combined rate+context going over the limit on busy (1.28 and 1.38 calls per hour) and cites Figure 4 for the floor of 16–20 ROIs. Both are forward references to figures two sections later.
- **Fix:** repeat or crop the relevant panel into Decision 1: Figure 3's bottom-right panel, combined, outside the stretch.
- Otherwise add an "evidence" column to the at-a-glance table (D1 → Fig 1 and Fig 3 bottom right, D2 → Fig 2, and so on), so Tony can jump to it.

**6. D2, Figure 2 · major.**
- The decision-relevant cell is not marked: fast-tuned binned SCE on the combined bench, 0.79 against the diagonal's 0.76.
- The prose claim "14 of 48 beat the diagonal, 13 overlap, 1 does not" cannot be seen, because the heatmap carries no intervals and no markers.
- **Fix:** outline every off-diagonal cell that beats its column's diagonal. Use a heavy border or a star for the one whose interval does not overlap (rate+context, combined-tuned on slow). Use a distinct highlight for the binned SCE cell that bears on Decision 1.
- The three bullets at lines 130–135 then become a two-line caption.

**7. D4, lines 208–223 · major.** The same quantity appears three times in three versions: the prose table on fresh seeds, Table 3 on fresh seeds, and Figure 4's right panel on seeds 1–8, which has different counts.
- The primary measurement (fresh, 120 per level) has no figure. The figure shows the secondary subset.
- **Fix:** plot the fresh-seed shares as the bars in Figure 4's right panel, with the seeds 1–8 shares as overlaid ticks. Then delete the prose table at lines 208–212 and point at the figure.
- If Figure 4 cannot be re-rendered (it came from the other workstation), put a fresh-seed version of the right panel beside it.

**8. D5, lines 237–258 · major.** The question is whether an optimum pressed against a wall (0, or 1 frame) counts as bracketed. That is a question about the shape of a curve, and the section has only a table and prose.
- The claim "C_min 0 to 0.03 gave identical calls" describes a plateau in words.
- **Fix:** plot F1 against the setting value along the searched grid for the five limit-held settings: `n_synchronous_frames` × 3 streams, `guard_sec` on slow rate+context, `C_min` on slow SPIKE-synch. Draw the hard limit as a vertical wall.
- A plateau and a still-climbing curve at the wall are different answers, and only the picture tells them apart.

**9. D7, lines 274–293, prose-only, largest block 182 words · major.** "Stop the grid at a stated z-cutoff" is a curve question.
- **Fix:** plot selection-seed F1 against `alpha` per extension step for fast and combined. Use a log x-axis with a second axis in z-cutoff (3.7σ to 5.9σ), and mark the extension cap.
- That shows whether the gain is flattening. The "read alpha as a z-cutoff" argument can then be one caption line.

**10. D8, lines 295–310 · minor.** The claim "LoCo's own threshold decides almost nothing under the floor" is an F1-flat-against-`threshold_pctile` profile.
- **Fix:** one small line plot per stream, reusing the profile form from findings 8 and 9.
- The context-below-20 s question can stay in prose.

**11. D6 and D9 · no figure needed.**
- Decision 6 is one number (0.0207 lost) against a 0.02 allowance. Prose is right there, and it is only 75 words.
- Decision 9 is a procedural rule plus a bug fix. Prose is right there too. Its 183-word bullet block (lines 318–326) could move to notes under a one-line assertion: "the cap was not applied to LoCo; no proposal changes".

**12. Real data, lines 448–474, prose-only · major.**
- The group contrast (median floor difference under senktide on fast: DI +1 ROI, OVX +17, MALE +1, ORX +20) is a visual finding given as a four-item list, which the house rule says to render.
- **Fix:** a strip plot, one dot per recording, with the per-window floor minus the baseline floor (in ROIs) on the y-axis and groups in the order DI, OVX, MALE, ORX. Draw the median as a bar and label the axis with its unit.
- If `065/report-inputs/real_data.md` already has such a figure, link or embed it.
- The counts 2,696 and 498 can go in the caption.

**13. Full tables, Table 2, lines 388–432 · minor.**
- "(precision swing not recorded)" is repeated in about 36 held-out cells.
- **Fix:** state it once in the column header ("held-out, precision swing not recorded"). Better, render Table 2 as a colored pass/fail grid (rows are detector × version, columns are seed set, a cell is red on a fail).
- It is an appendix, so this is minor.

**14. Captions of Figures 1–3 · minor.**
- **Figure 1's caption (84 words)** repeats the legend already drawn in the figure. Cut it to what the figure shows and why: "Blue diamonds are the four adoptable proposals; each sits right of its shipped circle."
- **Figure 3's caption (114 words)** carries method details: the 99th-percentile rates (0.1334, 0.0321 and 0.1529 Hz) and the seed range. Move them to Definitions or notes.
- **Figures 3 and 4 have two captions each:** one embedded in the image and one in the Markdown, with different wording. Keep one. The embedded ones cannot be re-rendered here, so trim the Markdown caption to what the embedded one does not say.

**15. Figure 3, share of the image · minor.**
- The legend block and the embedded caption take about 15% of the image height.
- Each detector has its own color while the x-axis already names it. That doubles the encoding and makes the legend wider than it needs to be.
- **Fix (for WSMIP065's next render):** one ink per shipped or proposal marker, with the detector named only on the axis. The plots then gain about 10% of the height.
- This role judges it as a layout policy. Any geometry or build bug belongs to agent 10.

**16. Layout overall · major.** Five decision sections in a row (Decisions 5–9) and the Real data section carry no figure. The figures are used for Decisions 1–4 only.
- **Fix:** findings 8, 9, 10 and 12 give Decisions 5, 7 and 8 and Real data a figure each. Decisions 6 and 9 correctly stay as prose.
- The "Search rules for next time" framing does not excuse Decision 7: it asks Tony to set a number.

**Relocation rule.** None of the fixes above deletes a caveat. Everything cut from the face of a section moves to notes under its figure or to the appendix, where every word is kept.

## What I checked
- Every section's word count and largest block.
- All four figures, opened as images.
- Where each figure sits against the decision that cites it.
- Every table, for whether it should be a figure.
- Every caption, for whether it goes past what the figure shows and why.
