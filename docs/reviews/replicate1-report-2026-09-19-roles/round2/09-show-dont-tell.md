GRANT 9 ok — Read, Grep, Glob, Bash

# Role 9: density and figure-first review ("Show, Don't Tell")

**Artifact reviewed:** `%USERPROFILE%\bugarach\bugarach-worktrees\replicate-report\docs\learned\tuned_vs_coact\replicate1\report.html`, the built page dated 09:02.
**Generator:** `%USERPROFILE%\bugarach\bugarach-worktrees\replicate-report\tools\make_replicate_report.py`
**Figure 1's key is built in:** `%USERPROFILE%\bugarach\bugarach-worktrees\replicate-report\src\bugarach\ui\diagnostic.py`, lines 690–761.

**How I measured.**
- I rendered the page fresh in light mode at a 1100 px viewport; the existing shots dated from 09:01, before this build. The page is 14,744 px tall, the body box is 1032 px wide, and the browser logged no console errors.
- I took each element's box from `getBoundingClientRect` in Playwright.
- I decoded Figure 1's PNG (3540×2025) and measured its ink row by row.
- Scratch outputs are under `...\scratchpad\mb2\role09\`: `raw_1100.json`, `shots\light_1100_*.png`, and `fig1_plot.png` / `fig1_legend.png`.
- The repo hook blocks writing scripts through a heredoc, and I hold no Write tool, so I ran the measurement inline with `python -c`. Nothing in any repository was edited.

**Thresholds I used.** These are conventions, not researched optima.
- **Any single text block over 60 words:** applied as written.
- **A results or methods section with no figure:** applied as written.
- **Two or more consecutive sections with no figure:** applied as written.
- **Figure share under about 50%:** measured as the rendered figure box's share of the section's rendered area.
- **The 40-words-per-unit cap:** reported but not flagged. It is a slide rule. Every section of this long page exceeds it, the smallest being section 6 at 116 + 37 words, so it tells us nothing here.

**Page totals.**
- About 4,330 words: 3,412 in the body, 645 in captions and 272 in tables.
- 32 text blocks exceed 60 words.
- Figures take 21% of the page area and tables 3.7%.
- Figures are given the full column width (840–1002 px of 1000). The text column stops at 74ch, about 640 px. That is the opposite of the margin incident and not a defect.

## Count table (one row per section)

| Section | Body words | Caption words | Table words | Largest text block (words) | Figure? | Figure share of the section, by area (by height) |
|---|---|---|---|---|---|---|
| Preamble (answer box) | 372 | 0 | 0 | 78, "Why this report exists" (subtitle 72, box bullet 73) | n | 0% |
| 1. The problem | 142 | 128 | 0 | 128, Figure 1 caption | y | 49.2% (50.7%). The recording itself is about 21%; see finding 1 |
| 2. Why a simulation | 326 | 0 | 0 | 115 (the others are 111 and 100) | **n** | 0% |
| 3. The contestants | 286 | 58 | 0 | 140, the four-nets paragraph | reserved slot only | 8.7% (86 px placeholder) |
| 4. Nested cross-validation (CV) | 309 | 79 | 0 | 126 (a boxed note is 100) | y | 34.0% |
| 5. Selections and budget | 353 | 73 | 0 | 148 (the others are 144 and 61) | y | 21.8% |
| 6. Why two draws | 116 | 37 | 0 | 116 | y | 31.3% |
| 7. Results of each draw | 178 | 61 | 97 | 97 | y, plus 2 tables | 22.7% (tables 14.3%) |
| 8. What the runs carry | 497 | 70 | 175 | 149 (the others are 136, 69 and 63) | y, plus 2 tables | **11.1%**, the lowest on the page (tables 13.0%) |
| 9. What the pair can claim | 385 | 139 | 0 | 133 (the others are 117 and 97) | y, 3 figures | 39.9% (51.7%) |
| 10. Limits | 321 | 0 | 0 | 122, the bench-defect bullet | n | 0% |
| 11. Where everything is | 127 | 0 | 0 | 47 | n | 0% (prose is right here) |

**Sections with no figure:**
- **Section 2** is a methods section with no figure.
- **Sections 2 and 3 in a row** have no real figure in this build; section 3 has only the reserved slot.
- **Sections 10 and 11** are consecutive and prose-only. That is acceptable: one is a list of limits and the other a list of locations.

## Findings

Each finding gives: location · issue · severity · suggested fix · whether I could verify it against a source.

**1. Section 1, Figure 1.** · Major · Verified: yes (decoded PNG, and `diagnostic.py` lines 713–755).

*Issue.* The figure box passes the 50% gate (49.2%), but the recording is not what fills it.
- **The key takes half the image.** The "How to read this" key is part of the image and takes 48.6% of its height (rows 1040–2025 of 2025). It holds about 270 words; two entries run to about 60 words each (Lane bar, Second call).
- **Three of its nine entries describe marks that are not in this figure:**
  - the ○ "Second call" mark;
  - the dotted "Threshold" line ("four of the six expose one");
  - the sentence "SCE bins at ten seconds". Only CoactDetect is drawn.
- **The plot band stops short.** Its ink ends at x = 2971 of 3540, leaving 16% of the width empty on the right.
- **Net result:** the lane and raster get about 21% of the section.

*Fix (a reflow, not a crop):*
1. Make those key entries conditional, the same way the red ▼ "missed" entry already is (`any_missed`, lines 702–711). Gate the ○ entry on a second call being present, the Threshold entry on a trace being drawn, and the SCE sentence on SCE being a lane.
2. Set the remaining one-line entries in a 2–3 column grid under the plot.
3. Give the freed height to the raster, so the 33 ROI rows can be read, and trim the empty right margin.
4. Move the explanations ("hairlines by honesty", "inference wearing the detector's authority") to the module docstring or the notes.

**2. Section 1, Figure 1 caption (128 words).** · Minor · Verified: yes.

*Issue.* The caption explains the marks a second time, on top of the key inside the image.

*Fix.* Cut the caption to what the figure shows and why it matters, for example: *"One quiet recording, seed 2000: CoactDetect matched 14 of the 15 planted events; all 6 of its unmatched calls fell on distractors."* Move "averages 0.75 there" to section 9, beside Figure 9; it is a pooled result, not a property of this recording.

**3. Section 2: a methods section with no figure, and all three paragraphs are 100 words or more.** · Major · Verified: yes.

- **Paragraph 2 (115 words) is a spec of the recording.** It lists 15 events in three sizes (10, 6 and 3 cells), at least 120 s apart; 6 distractors; a 300 s dense stretch; and two backgrounds. Replace it with a four-row spec table (component · count · cells recruited · timing). Also annotate Figure 1, which already *is* a bench recording:
  - lane triangle size encodes the recruitment level;
  - a bracket marks the ≥120 s spacing;
  - the dense block is labelled "300 s, nothing planted".
- **Paragraph 3 (100 words) defines F1 and the 0.83 practical ceiling.** Draw that ceiling as a reference line on Figure 6. Its axis currently stops at 0.8, below the ceiling and just above binned SCE's 0.771. Keep a one-line definition here; move the pooling and dense-stretch scoring detail to the notes.
- **Paragraph 1:** prose is right here, because it is the argument for simulating. Relocate the stream and defect asides to section 10, which already carries both.

**4. Sections 2 and 3: consecutive sections with no real figure.** · Minor (conditional) · Verified: yes.

*Issue.* The Figure 2 slot is deliberate. Even so, three of the first four units read as prose.

*Fix.* Finding 3 fixes section 2. Section 3 is fixed when the drawings land (finding 5). Until then, give the placeholder the height the drawings will need, not 86 px, so that measurements of this build reflect the real layout.

**5. Section 3.** · Minor (conditional on Figure 2 landing) · Verified: yes.

- **The four-nets paragraph (140 words) is Figure 2's content in prose.** When the drawings land:
  - give Figure 2 at least 50% of the section: four panels in a row, full width;
  - cut the paragraph to one label line per net under its panel;
  - keep the Deep Sets citation and "24 configurations = 23 random + the untuned default" in the caption.
- **Coded detectors.** Merge the six-bullet list and the provenance paragraph (56 words) into one six-row table: detector · what it counts · compared against · origin (citation).

**6. Section 4.** · Minor · Verified: yes.

- **Paragraph 2 (126 words) repeats Figure 3.** Figure 3 already draws the 24 configurations × 3 repeats × 3 fold pairs, the refit at 5 repeats on 10 recordings, and the coded search on all 72. Cut the paragraph to one sentence that points at Figure 3, and put "432 inner fits per net" and "50–55 refits" into Figure 3 as annotations.
- **The boxed note (100 words, the fold-sharing defect).** This is history, so prose is the right form, but it belongs elsewhere. Move it to section 6 (the rehearsal) or an appendix, and leave one line here: *"A fold-sharing defect found in the rehearsal was fixed and checked before both runs."*
- **The caption (79 words)** repeats the body. Drop its sentence starting "A net's inner selection fits on two…" and keep the colour key.
- **Result:** the figure's share rises from 34% to over half.

**7. Section 5: the largest prose blocks on the page, and the figure takes 21.8%.** · Major · Verified: yes.

- **Paragraph 2 (148 words)** tells the history of binned versus sliding detectors (30–36% of calls lost, goal 1's tuning, the shipped-settings table).
  - The history is provenance: move it to the notes or an appendix.
  - Move the reference settings (2 s window, 8 s merge, 1 s guard) into Figure 4's purple CoactDetect box, which already shows α and the context length.
- **Paragraph 1 (144 words):** keep the definition. Move the provenance of the factor 1.6 (the handoff on another branch) into a caption footnote.
- **Paragraph 3 (61 words), "What the budget does not police":** draw it.
  - Add the busy empty recording to Figure 4 as a greyed row ending in "reported, not gated".
  - Tag the dense-stretch ceiling "counts calls, not time".
  - The caveat then shows as a visible gap in the diagram, and the prose shrinks to one sentence. This moves the caveat into the figure; it does not delete it.

**8. Section 6.** · Minor · Verified: yes.

*Issue.* Figure 5 is eight coloured boxes that encode two seed ranges, which one clause of the preamble already states. The section's actual point — a +0.011 or +0.016 lead is too small to judge from one run — is not drawn anywhere.

*Fix.*
- Put the rehearsal's leads on Figure 8 as a third, grey mark labelled "rehearsal, retired simulator", beside the two draws.
- Fold the seed ranges into Figure 3's fold boxes or a caption line, which frees Figure 5.
- Move the paragraph's point about the declarations differing in two entries to section 11.

**9. Section 7, Figure 6: the payload is squeezed.** · Major · Verified: yes (SVG coordinates).

*Issue.* Each panel spans F1 from 0.2 to 0.8 across 244 px, which is about 407 px per unit of F1.
- The headline gap of 0.030 is therefore **12 px**.
- The between-draw moves of 0.005–0.010 are **2–4 px**, smaller than the 8 px dots.
- Most of each panel's width exists only for rate+context and SPIKE-synch under the budget, plus one collapsed fold.

*Fix.*
- Set the range to about 0.55–0.85 and draw off-axis entries at the edge, the convention Figures 8 and 10 already state.
- Add the 0.83 ceiling line (finding 3).
- Optionally make panel A narrower.

**10. Section 7, Tables 1 and 2.** · Minor · Verified: yes.

*Issue.*
- **Width and height:** the tables are stacked and have the same ten rows. They are 427 px and 284 px wide in a 1000 px column, which leaves 57% and 72% of the width empty, and together they take 754 px of height.
- **Paragraph detail:** the 97-word paragraph's "moved in 3 of 4 folds" is notes-level detail.

*Fix.*
- Merge the two into one 10 × 6 table (untuned, on F1 alone, and under the budget, each for both draws), about 650 px wide. That halves the height.
- Alternatively, since Figure 6 already marks every mean with a tick, move the exact values to an appendix.
- Move the "3 of 4 folds" detail to the notes.

**11. Section 8: the lowest figure share on the page (11.1%) in the tallest section (2210 px).** · Verified: yes, except 11c (no; I did not open the score files).

- **11a. "Training that failed" (149 words), major.** One sentence carries eight numbers: one-call inner fits of 292 and 306 of 864 for chorus_norm, 150 and 150 for chorus_gain_norm, 16 and 22 for line_length, 15 and 12 for tube. Draw them as a panel D of Figure 7 (or a new figure): the share of scored inner fits that collapsed to one call, per net, two bars in the draw colours. The sentence becomes *"It is not rare (Figure 7D)."*
- **11b. "Settings at the edge" (136 words) plus Table 4, major.** Every cell of Table 4 is "0 of 8" or "8 of 8", so it encodes one bit per detector in 220 px, and the prose already states that bit. The claim that matters is that SCE's 30 s merge may be rewarded by the bench's spacing, and the table cannot show it. Replace Table 4 with a grid-position chart:
  - one row per coded detector, its merge grid drawn as a track (up to 8 s for CoactDetect, up to 30 s for SCE);
  - a start marker and a chosen marker;
  - reference lines at the bench's 120 s minimum spacing and at goal 1's 6 s crowded spacing.
- **11c. Table 3, minor.** It mixes denominators (20 refit seeds against 4 folds) and says only *whether* a choice broke the budget. If the runs store the held-out rates (the table's wording implies they do), a strip plot of held-out rate ÷ ceiling with a line at 1.0 would show *how far* over. If they do not, the table is the right form.
- **11d. "No admissible setting" (69 words):** prose is right, since it is a single fact (449–527 calls per hour against ceilings of 15–18). Trim only.

**12. Section 9.**

- **12a. "Where the gap is" (133 words), major, verified yes.** The claim that the gap is in precision, not recall, is the second half of the answer box, and it has no picture; the recall figures appear only in prose.
  - Add a precision–recall plane under the budget: one dot per entry per draw, with iso-F1 curves.
  - Move the untested suspicion about duplicate calls at a 2 s merge to section 10, and keep one sentence here.
- **12b. "How far results move" (117 words), minor.** Draw the two medians (0.010 for the nets, 0.006 for the coded detectors) as marks on Figure 10 and keep only the interpretation in prose: a whole-draw shift, and a lower bound.
- **12c. Figure 10's layout, minor.** The "entry · selection" label column takes about 290 of 800 px, and the figure is 556 px tall. Group the rows by entry, with three dot columns (untuned, F1 alone, budget), to reach about 260 px.
- **12d. "The headline gap" (97 words), minor.** This is the argument, so prose is right. Put the fold standard deviations on Figure 8 as a mean ± SD mark per net per draw.

**13. Section 10: 321 words, no figure.** · Minor · Verified: yes, except 13c (no).

Prose is right for a list of limits, and every caveat stays. Three items:
- **13a. The bench-defect bullet (122 words)** contains a measurement: eight fitted constants inside their bootstrap intervals, except the recruitment share, just outside in both folders. Either show it as a small interval plot (eight rows, one interval each, with each workstation's value on the corrected export), or move the detail to the linked handoff and keep two sentences.
- **13b. The asymmetry between nets and coded detectors** is stated here for the fourth time; it also appears in the preamble's fourth bullet, at the end of section 4 and in section 9. State it once, as a two-column table (nets | coded) with rows for merge, training recordings, threshold selection and refits. Put the table in section 10 and point to it from the other three places.
- **13c. "Not broken down by event size"** names a figure the data already support. The page says the score files hold recall by event size (10, 6 and 3 cells). A per-entry chart of it is probably the cheapest figure to add, and it answers whether the nets lose on the smallest events.

**14. Preamble: 372 words, no figure; blocks of 78, 73, 72 and 61 words.** · Major · Verified: yes.

*Issue.* The answer box states numeric results with no picture. The box spans 1000 px, but its bullets wrap at about 740 px, so roughly 30% of the box is empty on the right.

*Fix.*
1. **Reflow.** Keep the bullets in a left column of about 60% and put a thumbnail of Figure 8 panel A (every net minus CoactDetect, under the budget, both draws, with the zero line) in the right column.
2. **Subtitle (72 words).** Move the workstation names and the date to a byline or to section 11.
3. **Bullet 4 (73 words).** Keep the claim and move its numbers (2 s, 10 recordings, 72) to the table in finding 13b.
4. **"Why this report exists" (78 words).** Keep it here and cut section 6 down to its figure (finding 8); the two currently tell the same rehearsal story.

**15. Section 11.** No finding. It is a list of locations, and prose is the right form.

## Surface examined
- All 11 sections and the preamble as rendered at 1100 px: word counts per block, and boxes for every figure and table.
- All ten figure slots, including the reserved Figure 2.
- Figure 1's decoded image and the source of its key.
- The generator's CSS (the 74ch text measure and the full-width figures).
- Not measured: narrow or mobile widths, and dark mode.
