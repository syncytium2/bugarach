GRANT 9 ok — Read, Grep, Glob, Bash (SubagentHandback also present, the reporting channel, not an editing tool; no Edit, Write or NotebookEdit)

**Role 9 — Show, Don't Tell: the four figures are in the wrong places, not the wrong size.**

- All four PNGs render full column width on GitHub, with no empty side margins (they are 2,080–2,250 px wide and GitHub scales them down).
- **Seven of the eight decisions, plus "Smaller items", have no figure.** Three of the four figures that would carry them (2, 3, 4) sit in "The full tables", below the decisions that cite them.
- Where text and figures compete, text wins: Figure 1 takes ~24% of its section's height, and the Full-tables figures ~26%, surrounded by ~1,600 words of on-page prose and caveats.

Artifact: `docs/learned/runs/2026-09-25-final-parameters/README.md` + `figure1_fresh_f1.png`…`figure4_bench_floors.png`. No file edited.

**Thresholds** (project conventions, tunable; not researched optima): >40 words per section; any single block >60 words; a results or methods section with no figure; two or more consecutive figure-less sections; a figure under ~50% of its section's rendered height.

**Method:** each Markdown section is a page. Words were counted by regex, splitting prose from table cells. The largest block is a paragraph, or a top-level bullet with its nested bullets. Figure share = the figure's rendered height ÷ the section's estimated rendered height, with each figure at 950 px × its own h/w, and text at a 950 px GitHub column, ~120 characters per 24 px line and 40 px per table row. These are estimates from the source plus the real PNG sizes; GitHub's render was not screenshotted.

## Count table

| section | prose words | table words | largest block | figure? | figure share of section height |
|---|---|---|---|---|---|
| Title + opening paragraph | 93 | 0 | 93 (one paragraph) | n | 0% |
| Decision 1: adopt these four? | 429 | 90 | 147 (the "held-out seeds also chose" bullet group) | y (Fig 1) | ~24% |
| The rulings… (intro) | 30 | 0 | 30 | n | 0% |
| Decision 2: hard limit | 79 | 64 | 24 | n | 0% |
| Decision 3: out of budget | 176 | 52 | 88 | n | 0% |
| Decision 4: CoactDetect alpha | 167 | 0 | 73 | n | 0% |
| Decision 5: context < 20 s | 134 | 0 | 46 | n | 0% |
| Decision 6: guard cap | 110 | 0 | 62 | n | 0% |
| Decision 7: bench under the floor | 139 | 71 | 42 | n | 0% |
| Decision 8: per-stream tuning | 72 | 44 | 29 | n | 0% |
| Smaller items | 102 | 0 | 76 | n | 0% |
| The full tables (Tables 1–3, Figs 2–4) | 576 | 954 | 109 ("How to read them" caveats) | y (Figs 2, 3, 4) | ~26% |
| Real data | 134 | 0 | 52 | n | 0% |
| Definitions | 345 | 0 | 84 | n | 0% |
| What ran | 99 | 119 | 36 | n | 0% |

**Figure geometry (PIL, measured on the PNGs):**

| figure | px | inked box (% of image) | blank rows (% of height) | shrink in a 950 px column |
|---|---|---|---|---|
| Fig 1 | 2080×736 | 91% | 14% | 0.46× |
| Fig 2 | 2240×1216 | 79% | 21% | 0.42× |
| Fig 3 | 2250×1230 | 96% | 17% | 0.42× |
| Fig 4 | 2100×840 | 95% | 10% | 0.45× |

**Consecutive figure-less sections:** nine in a row (the rulings intro, Decisions 2–8, Smaller items), and three in a row (Real data, Definitions, What ran).

## Findings (location · issue · severity · suggested fix · verified)

1. **Decisions 2–8 and Smaller items.** Nine consecutive figure-less sections (~1,000 prose words and four typed tables) are where Tony makes seven of his eight calls, while the figures that evidence them (2, 3, 4) sit ~200 lines later in "The full tables". · **blocking** · Move each figure up to the decision it evidences: Figure 2 into Decision 8; Figure 4 into Decision 7; Figure 3 into Decision 3 (slow locust's elevated-rate failure), with Decision 1 linking to it for the 1.28/h on busy. "The full tables" keeps only Tables 1–3. · verified yes (figure placement L345, 357, 366; citations L47, 185, 194).

2. **Decision 1, L28–50.** About 250 words of caveats sit before the figure, so the figure takes ~24% of the section. The fresh-seed overlap comparison in the third sub-bullet is prose for something Figure 1 already shows. · major · Put Figure 1 directly under the adoption table; cut the overlap sentence to "Figure 1: only fast binned SCE's intervals separate"; move the rest of "Read these three things" (selection bias, budget gaps, the combined warning) into a GitHub `<details>` block right after the figure. That block is this page's notes pane, and every word is kept. · verified yes (word count; Figure 1 viewed).

3. **Decision 2, table L74–80.** The five limit-bound proposals are a typed table. Figure 1 already plots all five as orange diamonds, but draws them the same as proposals held back for other reasons (cap, edge, budget fail). · major · Give Figure 1 a third marker class, "adoptable if a limit counts" (e.g. a half-filled blue diamond); Decision 2 then reads off Figure 1 and the table can go to Table 1. · verified yes (Figure 1 legend viewed).

4. **Decision 3, L90–117.** The key claim is before vs after: a precision swing near 0.01 pre-floor against 0.18–0.26 under the floor. It is carried by a 4-row table and an 88-word bullet group, with no figure. · major · A slope chart per failing detector (precision swing, pre-floor bench → under the floor, limit as a horizontal bar), paired with Figure 4's right panel (85/120 middle level under the floor on fast busy). The darkroom path to the diagnosis moves to notes. · verified partly (text read; pre-floor swing values not checked against a source).

5. **Decision 4, L119–139.** 167 words and no figure. "Runs to the extension cap, gaining F1 at each step" is a trajectory, which prose carries badly. · major · A line plot of selection-seed F1 vs log10 alpha, one line each for fast and combined, with the cap (1.4e-9) as a vertical rule and the shipped values as circles. Move the close-events re-run (0.044 vs 0.0165) to the `<details>` notes: it is provenance, not what Tony is deciding. · verified yes (text read).

6. **Decision 7, L167–190.** The in-section table duplicates Table 3, and Figure 4 shows the same quantity. The "each planted recording's floor sits about one ROI above the no-coordination floor" claim is explicitly "read off the figure", yet the figure is 180 lines away. · major · Put Figure 4 here instead of the table (Table 3 stays in the full tables), with one sentence pointing at the right panel's 100% bars. · verified yes.

7. **Decision 8, L192–207.** The table pulls 3 cells out of Figure 2's 72, with the figure far away, and in Figure 2 itself nothing marks the cells where an off-diagonal version beats the diagonal down a column. · major · Move Figure 2 here and give those winning off-diagonal cells a heavy outline. Figure 2's colorbar runs 0.4–0.9 while the data run 0.67–0.87, so the colours barely separate: rescale to the data range, or plot each detector's column as a diverging "minus the diagonal" map. The table can then drop to one line. · verified yes (Figure 2 viewed; colorbar range read off the image).

8. **Real data, L368–384.** A results section with no figure: 3,072 cells, 2,696 floors that differ, 498 flipped calls, median floor shifts of +17 and +20 ROIs. CLAUDE.md "Show the picture" applies directly. · major · A strip plot of own floor minus baseline floor per treatment window, one panel per stream, groups ordered DI, OVX, MALE, ORX, beside a stacked bar of call flips per detector. Keep "Descriptive only" on the page. Provenance (PR #814 unmerged; v3 supersedes v2) moves to notes or What ran. · verified no (numbers and per-group data not checked).

9. **Opening paragraph, L3–13.** A single 93-word block, over the 60-word threshold. · minor · Keep the first two sentences as the lead and replace the rest with an "8 decisions at a glance" table (decision · one-line ask · figure number); the runbook and ADR links move to What ran. Prose is otherwise right for a lead. · verified yes.

10. **The full tables, "How to read them" L222–243.** 576 prose words (largest block 109) of caveats and methods notes placed before Tables 1–3. · minor · Relocate, don't delete: wrap "How to read them" in `<details>`, merge the three methods caveats into Definitions, and replace Table 2 (37 rows, almost all "pass") with a pass/fail grid (detector×version rows, 3 seed-set columns, fails filled) — or lead with its 9 fail rows and say the rest pass. · verified yes.

11. **Figures 3–4 (PNG) vs their Markdown captions.** Both PNGs carry an in-image "Figure 3."/"Figure 4." caption at the bottom, plus a second 4-bullet Markdown caption each; Figure 1's first caption bullet repeats its legend. · minor · One caption per figure, stating what it shows and why it matters: drop the in-image caption line, or cut the Markdown caption to one sentence; move seed ranges and the supplier name to notes. · verified yes (images viewed).

12. **All four figures — the shrink factor.** Each is authored at 14–15 in (2,080–2,250 px) and shown at ~0.42–0.46× in a 950 px column; Figure 3's 6 panels × 8 detectors and Figure 2's 8 panels lose their small type. Figure 2 also has 21% blank rows, mostly the gap between its two panel rows. · minor (the layout-policy half; legibility measurement is agent 10's) · Reflow, don't crop: split Figure 3 into two figures (inside the stretch; outside the stretch) or re-author it at the column's aspect ratio; tighten the gap between Figure 2's panel rows. · verified yes (PIL measurement; on-screen fonts not checked).

13. **Decisions 5, 6, Smaller items, Definitions, What ran.** Figure-less, but prose or a table is right here: Decisions 5 and 6 are grid-scope and code-bug rulings with no quantity to plot (a small grid-axis schematic — tried values 5/10/20…120 s with the "cap" extensions marked — is optional for Decision 5); Smaller items is a point estimate against an allowance, with no interval computed; Definitions is a glossary; What ran is provenance. · minor · Only fix: Decision 5's paragraph explaining threshold_pctile's "cap" repeats Table 1's reading notes, so move it to Definitions; Decision 6's "Fixed in the same PR" note goes to What ran. · verified yes.

No figure shows empty side margins: every PNG is wider than the column, so GitHub renders it full width and there is no margin finding.
