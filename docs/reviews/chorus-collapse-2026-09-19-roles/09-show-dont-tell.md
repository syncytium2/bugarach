GRANT 9 ok — Read, Grep, Glob, Bash

I received those four tools plus the SubagentHandback tool, and no editing tool. I edited no files. Renders are in `<scratch>/mb2-cc/09/`: `light_1100_00.png` to `light_1100_08.png` are 1,100 px slices, and `fig1.png` is Figure 1 captured alone.

# Role 9, Show Don't Tell: `<worktrees>/chorus-collapse/docs/learned/chorus_collapse/index.html`

## Verdict
Every data figure shows individual fits or configurations, not only aggregates, and each gets 81–99% of the content column's width. The page's problem is text volume. About 2,900 words of prose and 572 words of caption sit around 7 figures. The first figure appears 1,292 px down the page, after 471 words. §5 is the decision section, and it has no figure. Three of the fixes are **reflows of figures the page already has**: move Figure 1 up, encode shape in Figure 2, and merge Figures 5 and 6. The fourth turns Table 3 into a new chart.

## How I measured
- **Tool:** Playwright chromium, reading `getBoundingClientRect` on the rendered page. I measured at viewport widths of 1,100, 1,440 and 1,920 px, where the layout is the same, and at 800 px.
- **Layout:** the body is capped at 1,000 px. Prose paragraphs are capped at 638 px. Captions are 649 px wide.
- **Figure size:** I measured each inline SVG's rendered box. I did not use the width requested in the source.

## Thresholds used
These are conventions, adapted for a scrolling report rather than slides:
- **Text blocks:** flag any block over 60 words. Report sections are not slides, so I did not apply the 40-words-per-slide rule. Instead I count prose words per figure.
- **Figure width:** a figure should take at least 50% of the content column's width. Separately, I flag more than 20% empty margin on *both* sides.
- **Figure area:** I report each figure's share of its section's area. Anything under 50% is noted.
- **Results and decision sections:** a results or decision section with no figure is flagged.
- **First figure:** it should start inside the first 900 px screen.

## Density table (1,100 px viewport, 1,000 px content column)

| section | prose words | caption words | table words | largest text block | figure | figure width (% of column) | figure share of section area |
|---|---|---|---|---|---|---|---|
| Title and lede (subtitle, intro, "The answer." box) | 480 | 0 | 0 | 107 words (answer-box bullet about the replays) | **n** | — | 0% |
| 1. The problem | 279 | 112 | 0 | 134 words ("How the fits are organized") | y (Figure 1) | 90% | 30% |
| 2. Which configurations collapse | 300 | 67 | 153 (Table 1) | 117 words (fold-pair and seed tests) | y (Figure 2) | 99% | **18%** |
| 3. Where the signal stops | 443 | 167 | 0 | 134 words (census definition) | y (Figures 3 and 4) | 93%, 92% | 33% |
| 4. When it happens, and what prevents it | 600 | 226 | 140 (Table 2) | **169 words** (replay narrative, the largest block on the page) | y (Figures 5, 6, 7) | 81% each | 28% |
| 5. What it means, and the choice it leaves | 400 | 0 | 45 (Table 3) | 89 words (repair options) | **n** | — | 0% |
| 6. Limits | 155 | 0 | 0 | 41 words | n | — | 0% |
| 7. Where everything is (with References) | 243 | 0 | 0 | 35 words | n | — | 0% |

- **Totals:** about 2,900 prose words, 572 caption words and 338 table words. The page has 7 figures and 3 tables and is 11,374 px tall.
- **Blocks over 60 words:** 24.
  - Lede intro: 85.
  - Answer-box bullets: 63 and 107.
  - §1: 76 and 134.
  - §2: 106 and 117.
  - §3: 122, 134, 108 and 79.
  - §4: 169, 71, 122, 72 and 106.
  - §5 bullets: 69, 85, 89 and 85.
  - All seven captions: 67 to 112.
- **First figure:** the Figure 1 SVG starts at y = 1,292 px. That is 1.4 screens down at a 900 px viewport. At 1,400 px only its lane row shows above the fold.

## Findings

| # | location | issue | severity | suggested fix (replacement figure or reflow) | verified |
|---|---|---|---|---|---|
| 1 | Lede and "The answer." box | 471 words and no figure before the first picture, which starts 1,292 px down. The box is 1,000 px wide but its bullets end 744 px from the page's left edge, 694 px from the box's left edge. That leaves **290 px (29%) of the box empty on the right**. Two bullets are over 60 words (107 and 63). | major | **Reflow.** Move Figure 1 up to sit directly after the intro paragraph, above the box. Its three-row lane strip is the whole finding at a glance: planted events, the working fit's calls, and the collapsed fit's single call across the recording. Then split the box into two columns: bullets in about 600 px on the left, and in the empty ~330 px on the right, a small copy of Figure 2 panel A (chorus_norm, collapse share by learning rate). Cut the 107-word replay bullet to its claim. Its numbers already appear in §4. Keep "a known failure with a standard remedy". | yes |
| 2 | §2, Table 1 and Figure 2 | Figure 2's configurations are identified only on hover ("Hover a dot for its configuration"). So the encoder-shape claim lives only in an 8×3 table (153 words) and a 41-word paragraph about chorus_gain_norm. The figure covers just 18% of the section's area, the lowest on the page. | major | **Encode encoder shape in Figure 2:** colour or marker per shape (4×4, 4×6, 8×4, 8×6). The claims that 4×6 collapses most and that chorus_gain_norm's 4×6 collapses at 78% can then be read off the dots. Table 1 moves to an appendix or behind a disclosure, and the chorus_gain_norm paragraph shrinks to one sentence. | yes |
| 3 | §2, sentence on training length | Three collapse rates are given in prose: 900 steps 65% (141 of 216), 1,800 steps 82% (59 of 72), 3,600 steps 85% (92 of 108). | minor | Add Figure 2 panel C, a dot plot of collapse share at lr 0.03 against step count, marked by depth. Alternatively move the sentence to notes: the page says itself the rates are "described, not tested". | yes |
| 4 | §4, first paragraph (169 words) plus Figures 5 and 6 | This paragraph narrates a timeline across two figures that share an x axis (training step, 0 to about 1,800) but are drawn separately. The text cites Figure 6 before Figure 5. Figure 5 spends 266 px of height on lines that are almost all zero. The working fit's blue line sits on the axis and is nearly invisible. | major | **Merge Figures 5 and 6 into one figure with a linked x axis.** The loss curves go in the main panel. The silent-layer count goes in a lane above them, following the house lane-above convention. Mark step 220 (working fit's loss falls below 1.0) and step 230 (first silent layer). The paragraph then shrinks to its claim: the head goes silent after the loss has stalled. The step and SD numbers move into the caption or notes. | yes |
| 5 | §5, Table 3 and the bullet "For chorus_norm, tuning stepped around it" | The decision section has no figure. Its central finding is that tuning chose none of chorus_norm's 11 configurations at lr 0.03. It sits as a zero in row 3 of a 6-row table. | major | **Replace Table 3 with grouped bars.** Group by net, with one pair of bars per learning rate: configurations in the grid, and refits of configurations tuning chose. Colour collapsed refits orange. The empty chorus_norm lr 0.03 pair is the finding and shows at a glance. The untuned-default note stays as the caption footer. | yes |
| 6 | §5, bullet "A collapse can be caught when it happens" (85 words) | The separating gap in output SD (at most 0.132 for collapsed fits, at least 0.803 for working ones) is stated in prose. Figure 3 already plots this quantity on its y axis. | minor | Shade the empty band from 0.132 to 0.803 on Figure 3's y axis, labelled "no fit falls here", and point the bullet at it. The bullet also covers the refits, which Figure 3 does not show (it shows second-draw inner fits only). Add the refits as distinct markers or say so in the caption. | yes |
| 7 | §5, bullet "The refits that collapsed" (85 words) | Four refits are listed inline as (net, draw, lr) tuples, followed by a cross-check against the replicate report. | minor | Add the four refits to Table 3 (or to the finding 5 chart) as orange marks. Move the cross-check with the replicate report's own flag to notes. That is provenance: relocate it, do not delete it. | yes |
| 8 | §5, bullet "A repair is a decision for goal 2" (89 words) | Three options are compared in running prose. | minor | Use a 3-row options table: option · what it changes · tried here? · needs both draws rerun. Prose also works. It is a decision list, not data, so this is optional. | yes |
| 9 | §3, paragraph before Figure 4 (108 words) | Four medians are stated in prose (1.84 and 2.60 at the head's input; 0.13 and 4.29 at the output). The same data are plotted in Figure 4. | minor | Draw each group's median as a crosshair in both panels of Figure 4. The paragraph keeps its claim: the encoder still hears the events, and the head does not pass them on. | yes |
| 10 | §3, paragraph "Round 1 of this page's review counted a layer as dead..." (79 words) | Review history is on the face of the report. | minor | **Relocate, do not delete.** Keep one sentence defining "silent" against a sign test. Move the story of the round-1 review to a methods note or appendix. | yes |
| 11 | §4, "Settled early, mostly" (72 words) | Transition counts in prose: 60 of 62 collapses already there at the shorter length, 2 later, 0 recovered. chorus_gain_norm: 8, 0, 3. | minor | A 2×2 transition table or small slope chart per net (collapsed or working at the shorter step count against the longer one). | yes |
| 12 | All seven captions (67 to 112 words) | Captions carry more than what the figure shows and why it matters. Figure 1's caption (112 words) spells out the fits' identity: net, lr, encoder and training seeds. The captions of Figures 3 and 4 repeat the colour key that is already drawn under each plot ("■ collapsed, ■ working"). | minor | Move the fit identity in Figure 1 into the trace panels' y-axis labels, following the house compact-labelling rule, for example "working fit · seed 2 · logit". Drop "both are replayed in §4". Cut the duplicated colour key from Figures 3 and 4. | yes |
| 13 | Whole page, figure share by area | In every results section (§1 to §4), figures fill only 18–33% of the section's area. Figure widths pass: 81–99% of the column, with no two-sided margins. The low area share comes from prose volume, not figure sizing. | major (aggregate) | Fixed by findings 1, 2, 4 and 5 together, which are reflows and a table-to-chart swap, not cuts. No caveat is removed: each one moves to notes, an appendix or the caption footer. | yes |
| 14 | Figures 5, 6 and 7 | Fixed at 810 px (81% of the column) while Figures 1 to 4 span 895–990 px. The 19% gap is all on the right, so it does not trip the both-sides rule. | minor | If finding 4's merge is applied, let the merged figure fill the column. Any geometry or build cause belongs to agent 10. | yes |

## Where prose is right
I found no problem with these sections or paragraphs:
- **§6 Limits:** scope statements, nothing to draw.
- **§7 Where everything is:** file locations, nothing to draw.
- **§4 "A known failure, with a standard remedy" (106 words):** literature and provenance. It is rigor, and it stays.
- **§1 "Which fits collapse is not repeatable" (69 words):** one comparison of two numbers (111 observed against 111.5 expected). A null-distribution plot would add ink but no information.
- **§4 paragraph before Figure 7 (122 words):** its "6 of 7 against 1.4 expected" argument is fully backed by Table 2, one row per fit, and those are the data themselves. Optionally, add end-of-line labels in Figure 7 naming each fit's configuration.

## Do the figures show the data themselves?
Mostly yes:
- Figure 1 shows the raw output trace over one recording.
- Figure 2 shows every configuration.
- Figures 3 and 4 show every second-draw inner fit.
- Figures 5 to 7 show per-step training curves.
- Table 2 lists each fit.

Some claims are shown only as totals, never fit by fit:
- **Tables 1 and 3:** addressed by findings 2 and 5.
- **The four collapsed refits:** addressed by finding 7.
- **The first draw's fits:** Figures 3 and 4 show the second draw only, by design. Figure 2 pools both draws, so the draw-to-draw difference (146 against 153) appears only as numbers in the text.

## Boundary notes
- At an 800 px viewport the SVGs render at about 820 px, wider than the 800 px column, so the figures fall back to horizontal scroll. That is a geometry question for agent 10, not a layout-policy finding here.
- Figure 6 being cited before Figure 5 is an order-of-argument point for agent 11. I raise it only as support for the merge in finding 4.
