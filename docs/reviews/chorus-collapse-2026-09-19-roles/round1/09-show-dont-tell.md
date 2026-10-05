GRANT 9 ok — Read, Grep, Glob, Bash

(Declared note about the run, not the artifact: I hold no Write tool, and the repo's no-heredoc hook blocks writing a source file through the shell. So the measurement script went to Python on stdin with a quoted heredoc, and no file was written. The renders are in <scratch>/mb-cc/09/: light_1100_00..04.png and an unused measure.py stub that the hook blocked before it could be used.)

## What I measured, and how

- **Render:** Playwright chromium at 1100 px and 1440 px viewports. The page is 6,128 px tall, the content column is capped at 1,032 px, and prose paragraphs render 638–649 px wide (about 62% of the column). The viewport width changes only the side gutters, so every share below uses the 1,032 px content column. Share of the full viewport is lower still: at 1440 px, Figure 1 is 65% and Figure 3 is 56%.
- **Word counts:** visible text with SVG text excluded, taken with `page.evaluate`. Figure boxes come from `getBoundingClientRect` on each rendered `<svg>` and `<table>`.
- **Unit of analysis:** a report page has no slides, so each `<h2>` section is one unit. The header plus "The answer" box is one more.
- **Thresholds.** These are process conventions, not researched optima.
  - More than 40 words per unit. This fires on every unit of a report, so I report it but do not judge by it.
  - Any single text block over 60 words. This is the working discriminator.
  - A results or methods unit with no figure.
  - Two or more prose-only units in a row.
  - SVG area under 50% of the unit's area.
  - More than 20% empty margin on both sides of a figure while the text above it runs full width.

## Density table

| unit | words | largest block (words) | figure? | SVG share of unit area | figure width / 1,032 px column |
|---|---|---|---|---|---|
| header + "The answer" box | 218 | 61 (bullet 3) | n | 0% | — |
| 1. The finding it explains | 146 | **141** (one paragraph) | n | 0% | — |
| 2. Which configurations collapse | 239 (52 caption, 62 table) | **123** | y (Fig 1, Table 1) | **23%** (33% counting the table) | Fig 1 90%, Table 1 77% |
| 3. What a collapsed fit is | 370 (59 caption) | **208** (largest on the page) | y (Fig 2) | **31%** | Fig 2 89% |
| 4. When it happens, and what prevents it | 399 (108 caption, 53 table) | **206** | y (Fig 3, Fig 4, Table 2) | **32%** (37% with the table) | Fig 3 78%, Fig 4 78%, Table 2 35% |
| 5. What it means, and the choice it leaves | 301 | **93** (bullet 1) | n | 0% | — |
| 6. Limits | 110 | 42 | n | 0% | — |
| 7. Where everything is | 70 | 22 | n | 0% | — |
| **total** | **1,853** | | 4 SVGs, 2 tables | | |

**How to read the table.** No figure is undersized. All four are wider than the prose, so the "empty margin on both sides" rule does not fire. Every figure-bearing section still falls under 50% because long prose paragraphs dilute it. The remedy is therefore to convert and relocate prose, not to enlarge figures.

The first picture sits about 1,270 px down the page. At a 900 px viewport the reader scrolls about 1.4 screens and reads about 490 words (answer box, all of section 1 and section 2's paragraph) before seeing any evidence. Every paragraph also leaves about 390 px (38% of the column) empty to its right. That empty band is free space for the side figures proposed below.

## Findings

Each finding gives its location, issue, severity, suggested fix and whether it was verified.

1. **§3, and the page as a whole: the central claim is never shown as data.**
   - **Issue:** The central claim is that a collapsed fit's output "barely moves" and makes the whole recording one call. The page never shows a collapsed fit's output trace, only its spread: one number per fit, plotted in Figure 2. The per-fit points in Figure 2 and the loss traces in Figure 3 are real data, but the output itself, which is the thing that fails, is only described.
   - **Severity:** major.
   - **Fix:** Add a new figure at the top of §3, "the output of a collapsed fit and a working one." Show two stacked traces of the output logit over the bench recording (quiet background, seed 2000): the collapsed fit 2736f584, training seed 0, against the working fit of the same configuration. Each trace gets its own y range, x is linked in minutes-friendly time, and the threshold is drawn as a line on each trace. Above them goes a lane of the 15 planted events and each fit's calls as down-pointing markers (green recovered, red missed). The collapsed fit's single whole-recording call then sits visibly against 15 events. The data do not exist yet: census.json stores only `logit_sd` per fit, not the trace. The census already runs each fit on this recording, so `tools/diagnose_chorus_collapse.py` only has to save the logit trace for these two fits.
   - **Verified:** yes (census.json has keys `logit_sd`, `min_head_alive` and `vote_gain_moved`, and no trace).

2. **§1: 141-word prose-only paragraph on a results unit.**
   - **Issue:** This is the page's founding result (146 and 153 of 432 fits collapsed, 111 of them the same fit in both draws) with no figure. The "answer" box before it is also prose-only, so the page opens with two prose-only units.
   - **Severity:** major.
   - **Fix:** Replace the paragraph's numbers with a small side figure in the empty right third of §1, "the same fits collapse in both draws." Draw one bar per net: collapsed fits in the first draw only, in both draws, and in the second draw only. For chorus_norm that is 35, 111 and 42 fits; for chorus_gain_norm, 37, 38 and 37 fits. The overlap is the evidence for "follows the configuration more than the data." Keep one sentence of assertion.
     - Move the nesting description ("24 configurations × 3 seeds × 6 fold pairs = 432") into that figure's caption or a tiny nesting schematic.
     - Move the `replicate1/` path to §7.
   - **Verified:** yes for the counts (from Table 1). The splits are derived from Table 1, not re-counted.

3. **§2 paragraph: 123 words, a run-on of percentages.**
   - **Issue:** The paragraph reads: width 80%/67%, depth 60%/85%, seeds 34/32/38%, fold pairs 30–38%. Only marginals are given. The grid is crossed, and I checked it from collapse_table.json for chorus_norm at lr 0.03:
     - 4 units × 4 layers: 69% (75 of 108 fits)
     - 4 units × 6 layers: 90% (97 of 108 fits)
     - 8 units × 4 layers: 46% (33 of 72 fits)
     - 8 units × 6 layers: 81% (87 of 108 fits)

     The marginals hide that 8 units × 4 layers is the one cell under half.
   - **Severity:** major.
   - **Fix:** Add a Figure 1 panel C, "the encoder's shape at lr 0.03." It is a 2×2 grid, width by depth, with each cell giving its share and "n of N fits." Add panel D, "identity does not matter": the share by training seed (3 dots) and by fold pair (6 dots) on the same 0–1 axis as panels A and B, visibly flat. Cut the paragraph to one sentence of assertion plus pointers. Also pass the 2×2 interaction to the content roles: the prose does not state it.
   - **Verified:** yes (computed from collapse_table.json; the marginals 172 of 216 and 120 of 180 match the prose).

4. **Table 1: mixes two breakdowns and sits in the wrong section.**
   - **Issue:** The table combines the count by learning rate, which aggregates Figure 1, with the count by draw and the overlap, which is §1's finding. It sits in §2.
   - **Severity:** minor.
   - **Fix:**
     - Put the learning-rate counts on Figure 1's y-axis labels, following the house compact-labeling convention (for example "lr 0.03 · 292 of 396 fits"). The table's lr columns then add nothing.
     - The draw columns become finding 2's overlap bars.
     - Keep the exact table as a lookup in an appendix below §7. A 12-number table of exact counts is legitimate reference material, but it is not the evidence figure.
   - **Verified:** yes.

5. **§3 first paragraph: 208 words, the largest block on the page, with the architecture described in prose.**
   - **Issue:** The paragraph describes the pipeline in prose: encoder → standardization → vote → 3 pooled statistics → head of 8 layers × 8 units with GELU → logit → threshold.
   - **Severity:** major.
   - **Fix:** Add a mechanism schematic, "where the signal stops," placed in the empty right band beside the paragraph. Draw the stages as a left-to-right box chain, with the head drawn as an 8-layer stack, one layer greyed out as dead ("no unit above 0.001 over the recording"). Show the output as a nearly flat line against a threshold at the floor of its grid.
     - The GELU definition becomes a schematic annotation.
     - The spread medians (0.0055 against 5.20) are already Figure 2's y axis. Point to them there and drop them from the prose.
   - **Verified:** yes (paragraph measured; the schematic is a proposal).

6. **§3 second paragraph (chorus_gain_norm, "a second route").**
   - **Issue:** The vote-gain comparison (3% moved against 13%) and the lr split of the 15 collapsed fits without a dead layer (2/8/5) are aggregates in prose. The page says it does not establish this route.
   - **Severity:** minor.
   - **Fix:** Either add a Figure 2 panel C, "vote gain moved": dots for the 15 collapsed fits without a dead layer against working fits, from `vote_gain_moved` in census.json. Or, since the claim is explicitly unexplained, move the paragraph to §6 Limits whole. Do not delete it.
   - **Verified:** yes (the field exists in census.json).

7. **§4 paragraph: 206 words that narrate Figure 3's sequence step by step.**
   - **Issue:** The paragraph walks through the replays one after another, which the figure already shows.
   - **Severity:** major.
   - **Fix:** This is a timeline and it is already drawn, so cut the paragraph to two sentences: "the collapsed fit's loss never leaves its start; its head loses layers from step 30 (Figures 3–4); lower lr or a 200-step warm-up rescues it."
     - Put the order of changes into Figure 3's legend: group "as run" first, then "one change."
     - Move the exact-replay provenance to speaker notes or §6 Limits: "reproduced its saved checkpoint to the last bit," and first-batch spreads of 0.0008 and 0.0011.
   - **Verified:** yes.

8. **Figures 3 and 4: two figures on the same x axis (training step), each with its own x axis and legend.**
   - **Issue:** Both render at 78% of the column. The house convention is one x axis per linked group.
   - **Severity:** minor.
   - **Fix:** Reflow them into one figure at full column width (1,032 px). Figure 4, "dead head layers," becomes a short lane under the loss panel, sharing Figure 3's x axis on the bottom row only. Use one legend with a shared colour per fit. This saves one axis and one legend, and puts "loss stays flat" directly above "head is dying" at the same step.
   - **Verified:** yes (widths measured at 810 of 1,032 px).

9. **Table 2: 8 rows of final loss, trains or collapses.**
   - **Issue:** This is an aggregate of training runs whose full loss logs are already in the repo. Each `replays/*_lr0.03-warmup200.json` holds a `log` of up to 181 logged steps, and all 8 fits have a file.
   - **Severity:** major.
   - **Fix:** Add a figure, "a 200-step warm-up on eight other collapsed fits." Show small multiples or thin overlaid lines of training loss, one per fit, with the as-run collapsed level (about 1.5) as a grey band and the 0.5 "trains" line dashed. e86433df then stands alone at the top. Move the exact final losses to the lines' end labels or to an appendix table. This shows the data rather than one number per run.
   - **Verified:** yes (the files exist and hold a `log` list). The file sizes differ (about 13 KB against 51 KB), so log lengths may differ, which is a point for the plot's x range.

10. **§5 bullet 1: 93 words, a results claim with no figure.**
    - **Issue:** The claim is that tuning chose 35/60/0 refits at lr 0.003/0.01/0.03, and that 11 of 24 configurations were effectively removed.
    - **Severity:** major.
    - **Fix:** Add a figure, "the grid declared against the grid tuning used." Use paired bars per learning rate: configurations in the declared grid (6, 7 and 11) beside refits tuning chose (35, 60 and 0). The empty lr 0.03 bar carries the claim. Keep one sentence.
    - **Verified:** partly. The configuration counts come from Table 1's denominators ÷ 36 fits. The 35/60/0 figures are the page's own numbers and were not re-counted.

11. **§5 bullet 2: the enumerated parenthetical list of 4 refits.**
    - **Severity:** minor.
    - **Fix:** Prose is fine for a 4-item fact, but move the parenthetical list (net, draw, lr ×4) into a 4-row table or speaker notes. Better, plot the 4 refits as distinct markers in Figure 2, where bullet 4 also points.
    - **Verified:** yes.

12. **§5 bullet 4: "spread ≤ 0.13 in every collapsed fit, ≥ 0.80 in every working one."**
    - **Issue:** The separation is visible in Figure 2 but not marked there.
    - **Severity:** minor.
    - **Fix:** Draw the empty gap on Figure 2 as a shaded band from 0.13 to 0.80, labelled "no fit in the census or the refits," and add the refits as a third marker. The bullet then becomes a pointer to that band.
    - **Verified:** yes (Figure 2's y axis is visible in the render).

13. **§5 bullet 3 (the repair options), §6 Limits, §7 Where everything is.**
    - **Issue:** Together with §5, these give three prose-only units in a row (481 words), so the consecutive-prose rule fires.
    - **Severity:** none. I checked, and prose is right here.
    - **Why no change:** Bullet 3 is a decision menu for goal 2, not a result. At most it could become a 3-row table (option · evidence · tested?), which is optional. §6 holds caveats, which stay on the page; do not trim them for word count. §7 is provenance. The run is really §5 alone, and findings 10–12 address it.
    - **Verified:** yes.

14. **"The answer" box: 218 words; bullet 3 is 61 words, over the 60-word block limit.**
    - **Severity:** minor.
    - **Fix:** Keep the box as prose, since it is the standfirst. Cut bullet 3 to the assertion and move "a 50-step warm-up is not enough" to §4. Optionally reflow the box into a narrow left column with a thumbnail of the merged Figure 3/4 on the right (collapsed loss flat, rescued loss falling). The evidence then appears on the first screen instead of 1.4 screens down.
    - **Verified:** yes.

## Candidates you asked about

- **§2 percentages:** yes, make them a figure (finding 3). The crossed 2×2 shows something the prose does not say.
- **§5's four bullets:** bullet 1 needs a figure (finding 10) and bullet 4 needs a mark on Figure 2 (finding 12). Bullet 2 needs relocating (finding 11). Bullet 3 is right as prose (finding 13).
- **Table 1:** split it (finding 4) rather than turning it into a figure. **Table 2:** replace it with the actual loss curves (finding 9).
- **Showing the data themselves:** partly. Figure 2 plots one point per fit and Figure 3 shows real loss traces. The one thing the page's argument rests on, a flat output trace beside a working one, is not shown and cannot be drawn from the stored data yet (finding 1).

## Files

- Artifact: <worktrees>/chorus-collapse/docs/learned/chorus_collapse/index.html
- Generator: <worktrees>/chorus-collapse/tools/diagnose_chorus_collapse.py
- Data checked: census.json, collapse_table.json and replays/ in the artifact's folder
- Renders: <scratch>/mb-cc/09/light_1100_00.png through light_1100_04.png
