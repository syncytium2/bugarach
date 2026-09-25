GRANT 9 ok — Read, Grep, Glob, Bash

# Role 9 — Show, Don't Tell: final-parameters README

**Artifact:** `<worktree>\docs\learned\runs\2026-09-25-final-parameters\README.md` + figure1–4 PNGs in the same folder. No file was edited.

**Thresholds used** (conventions, not optima): any single text block > 60 words; a section with ≥ ~150 prose words and no figure; two or more consecutive figure-less sections; a figure whose content box is < 50% of its canvas. The deck rule of 40 words per slide does not transfer to a scrolling report, so it is not applied; each section is treated as one page.

**Method:** word counts by script (prose vs table text separated); figure share = ink bounding box (pixels < 245 grey) as a share of the rendered PNG. GitHub scales every image to the column width, so column share is ~100% for all four; the internal share is what matters.

## Count table

| Section (page) | Prose words | Table words | Largest text block | Figure? | Figure share of its canvas |
|---|---|---|---|---|---|
| Title + "Nothing here is adopted" + floor paragraph | 114 | 0 | 73 (floor paragraph, lines 9–13) | n | – |
| In one paragraph | 172 | 0 | 60 (lines 17–20 + list lead-in) | n | – |
| The adoption table | 317 | 975 (24 rows × 10 cols) | 104 (the "Budgets" bullet, lines 40–51) | n | – |
| Figure 1 (fresh F1, shipped vs proposal) | 78 | 0 | 35 | y | 91% (2080×736) |
| Figure 2 (3 × 3 cross-stream) | 114 | 0 | 26 | y | 84% (2240×1152) |
| Figure 3 (elevated-rate recording) | 64 (+ caption burned into the PNG) | 0 | 24 | y | 96% (2250×1230) |
| Figure 4 (bench floors) | 55 (+ caption burned into the PNG) | 0 | 22 | y | 95% (2100×840) |
| What waits on Tony | ~500 (622 by script, incl. two indented tables ~120) | ~120 | 98 (item 6 / item 1 with its gains table) | n (item 6 cites Figure 4) | – |
| Real data | 34 | 0 | 31 | n | – (prose is right here) |
| What ran | 55 | 100 | 19 | n | – (a table is right here) |

**Totals:** ~1,550 prose words, ~1,195 table words, 4 figures. **All four figures are in section 4**; a reader passes ~600 prose words and a 975-word table before the first picture. No figure is under 50% of its canvas, and none has wide empty margins, so there is no reflow finding on that count.

## Findings (location · issue · severity · suggested fix naming the replacement figure · verified)

1. **Page order — sections 1–3 before the figures.** Three consecutive figure-less sections (title block, "In one paragraph", the adoption table; ~1,400 words together) come before any picture, so the picture that answers "what can I adopt?" is below all of them. Figure 1 already encodes adoptable vs not (blue vs orange diamonds) but sits below the table. **Major.** Fix: move the figures up so the page opens with a picture: title → new Figure 1 (#2) → current Figure 1 → adoption table. Renumber. **Verified: yes** (line numbers 1–99, word counts by script).

2. **"In one paragraph" (lines 15–30) + "What waits on Tony" items 1, 3 and the smaller slow-SCE item.** The 14 proposals and the reason each is held back are sorted in prose: a 5 / 4 / 1 bullet list, then re-stated with numbers in item 1, item 3, a gains table and the "Smaller items" list. That is category × value-with-interval, which is a figure's job, and the reader has to join three places to see the decision. **Major.** Fix: replace it with a **forest plot of held-out gain [95%] for all 14 proposals** — one row per detector, one panel per stream (or rows grouped by stream), a zero line, and marker colour for status: adoptable (strict) / held back only by a hard limit (locust ×3, slow rate+context, slow SPIKE-synch) / held back by the cap or a grid edge (CoactDetect ×2, LoCo ×2) / held back by the close-events loss (slow binned SCE; fast CoactDetect marked with both). This shows decision 1 (the five "limit" rows) at a glance and lets the paragraph shrink to two sentences pointing at it. Keep the item-1 gains table only in notes or an appendix. **Verified: yes** (all gains and intervals present in the table, lines 63–86).

3. **The adoption table (lines 61–86), 10 columns, 975 words.** Too wide to read, and it scrolls sideways on GitHub.
   - The "planted events under the floor" column is **the same string in all 8 rows of each stream**: 3 unique values over 24 rows, already shown by Figure 4 (right). About 250 of the 975 words are repeats.
   - The three budget checks (selection · held-out · fresh) are pass/fail on a grid.
   - The two bracketing columns are yes/no with the reason in parentheses.

   **Major.** Fix: split it, don't shrink it. (a) Drop the floor column and put a one-line note per stream under Figure 4. (b) Replace the budget and bracketing columns with a **status tile matrix** (rows = detector × stream; columns = selection, held-out, fresh, bracketed (strict), bracketed (limit counts); green pass / red fail, with the failed budget named in the tile — crowded, precision_swing, probe — and grey "not recorded" for the held-out precision swing). (c) Keep a narrow table of stream, detector, the settings that change, held-out gain and fresh F1; parameter values are for looking up, not for seeing, so a table is right there. **Verified: yes** (repeat check by reading rows 63–86; the per-stream strings are identical).

4. **Adoption-table definitions (lines 34–58): 317 words, including a 104-word bullet.** The definitions of gain, fresh F1, budgets, bracketing and chorus all sit before the table. They are correct and must stay, but they block it. **Minor.** Fix: relocate, don't cut. Move them to a "Definitions" section after "What ran" (or a `<details>` block under the table), keeping one sentence above the table (seed sets, and "adoptable = strict rule"). With the tile matrix from #3, only its legend is needed. **Verified: yes.**

5. **Header floor paragraph (lines 9–13): a 73-word block.** The method definition sits on the page's first screen, where the reader needs the decision. **Minor.** Fix: keep its first sentence ("Floor: ADR-0008 per-window, bench per ADR-0009") and move the null-draw details (1,000 draws, *J*, window, the don't-care rule) to the Definitions section. There is no replacement figure; prose is right here, only in the wrong place. **Verified: yes.**

6. **"What waits on Tony" item 2 (lines 150–162).** It lists four shipped points out of budget but does not point at Figure 3, which visibly shows slow locust above its probe bar. **Minor.** Fix: add "(Figure 3, the elevated-rate recording, slow panel)" to the slow-locust row. For the three precision-swing rows a **measured-vs-limit dot plot** would work (one row per shipped point, the measured swing on selection and fresh seeds, a limit tick). With four rows the current table is also acceptable; state that choice. **Verified: yes.**

7. **"What waits on Tony" items 4–5 (lines 171–178): grid-rule prose.** The guard cap (guard ≤ context/4) and the fast-LoCo context extension are geometry described in words. **Minor.** Fix: a small **grid schematic**: context window (s) on x, guard (s) on y, the searched cells marked, the guard = context/4 line drawn, the 8 s guard cells at 20 s and 30 s context shown as removed, and the fast-LoCo proposal at 20 s marked with its round-1 point at 5 s. One picture answers both items. **Verified: no** (grid values taken from the prose only; the runbook grids were not opened).

8. **Figure 2 caption (lines 101–111), 114 words.** The caption carries provenance — "38 of 38 to the digit", "114 cells ran as-is", where the intervals live in `adoption.json`. A caption states what the figure shows and why it matters. **Minor.** Fix: keep the first three bullets; move the reproduction check and the `adoption.json` pointer to "What ran"; add the one sentence the figure exists for (e.g. whether a version tuned on one stream carries to the others), stated as the takeaway. **Verified: yes.**

9. **Figures 3–4: two captions each.** Each PNG carries a burned-in "Figure N." caption, and the Markdown supplies a second, different one: double text for one figure. **Minor.** Boundary: agent 10 owns rendering and build; this is only the caption policy. Fix: keep one caption, the Markdown one (it is searchable), and render the PNGs without the burned-in line. **Verified: yes** (read both PNGs).

10. **"Real data" and "What ran".** No finding. Prose and a table are right here: these are pointers and provenance, with nothing to draw. **None. Verified: yes.**

11. **Figure canvas share, all four figures.** No finding. Content fills 84–96% of each canvas; the lowest is Figure 2 at 84%, from the inter-panel gaps of its 2 × 4 heatmap grid. GitHub renders each at full column width. No reflow is needed. **None. Verified: yes** (bounding boxes measured with PIL).

**Summary for adjudication:** the words are fine; the order is the problem. The highest-value change is a new opening figure, the held-out gain forest plot coloured by why each proposal is held back (#2), placed above the table. Next, split the adoption table (#3): drop the floor column, which repeats Figure 4, and move the budget and bracketing columns into a pass/fail tile matrix. Everything else relocates to a Definitions section rather than being cut.
