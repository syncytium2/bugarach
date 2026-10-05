GRANT 10 ok — Read, Grep, Glob, Bash

(SubagentHandback is only how this report gets delivered, not a review tool. I hold no Edit, Write or NotebookEdit. Because I have no Write tool, the measurement script ran inline with `python -c` and was never saved as a file. The repo's heredoc hook had blocked my first attempt.)

## Build currency and reproduction (checked before any row)
- **Artifact checked:** `<worktrees>/chorus-collapse/docs/learned/chorus_collapse/index.html`. Its `git hash-object` is `fe8db88a…`, which matches the brief, and it is identical to `HEAD:` at 56e5c49. The working tree has no diff in `tools/` or `docs/learned/chorus_collapse/`.
- **Timestamps:**
  - index.html: 16:18:42
  - `tools/diagnose_chorus_collapse.py`: 16:18:31
  - `collapse_table.json`, `census.json`, `trace.json`, `replays/`: 16:15:23
  - `tools/make_replicate_report.py`: 11:21
  - The build is newer than every input it embeds.
- **Test run:** `PYTHONPATH=src python -m pytest tests/test_diagnose_chorus_collapse.py` gave **3 passed**. That includes a byte-for-byte rebuild from the committed data, a check that figures are numbered in order and each is cited, and the no-personal-path check. **The build is current and reproduces.**

## Renders
- **Full-page slices:** `<scratch>/mb2-cc/10/r/{light,dark}_{1100,390}_NN.png`
  - At 1100 px: 9 slices each, page 11,374 px tall, scrollWidth 1100.
  - At 390 px: 12 slices each, page 16,587 px tall, **scrollWidth 390, so no page-level sideways scroll**.
  - Zero console errors in all four renders.
- **Per-element zoom crops at 2× (device scale factor 2):** `<scratch>/mb2-cc/10/z/elNN_{FIGURE|TABLE}_{scheme}_{width}.png`
- **Measured geometry:** `<scratch>/mb2-cc/10/z/geom_*.json`
- **Automated SVG text-box pass:** every `<text>` pair was tested for bounding-box overlap, and every label for clipping at the SVG edge.
  - It found zero clipped labels.
  - Its only hit was the two-line "N of M / fits" totals in Figure 2, overlapping by 2 px of line box. Visually they do not touch.

## Mechanical table
Rendered box = measured SVG or table box at a 1,100 px viewport (1,000 px content column), then its % of page width. At 390 every SVG has a min-width of 810–820 px inside an `overflow-x:auto` box 358 px wide, with a "Scroll sideways…" hint that appears only at that width.

| Item | Checked against | Rendered box (1100) | Overlap/clip | Axis name+units | Panels lettered | All marks identified | Color key in color, adjacent | Shared axes | Raster/lane rule | Time axis | Clamp marked | Dark tokens | 390 |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| Fig 1 (fig-problem) | el00_*_{light,dark}_{1100,390} | 895×422 px, 81% | FAIL minor: a working-trace spike near 41m crosses the "threshold, 2.9" label | ok (logit; "time in the recording") | **FAIL**: lane, working trace and collapsed trace unlettered; caption says "Lane:" and "Below:" | dashed = legend; ▼ = caption; blue/orange named by row labels; gray lane band unexplained (minor) | ok by row labels | differing y-ranges declared ("on its own vertical range") | PASS: ▼ points down, in a lane above the traces; no raster | PASS: 0/5m/…/40m | n/a: range covers min/max and threshold | PASS | scrolls in box, hint shown |
| Fig 2 (fig-rates) | el01_* | 990×254 px, 90% | PASS | ok (share, unitless; rows "learning rate x") | PASS A/B | dots and stacking explained in caption; alternate-row gray band unexplained (minor) | single color, no key needed | x 0–1 shared | n/a | n/a | n/a | PASS | text scales to about 9–10 px (minor) |
| Table 1 | el02_* | 775×283 px, 70% | PASS | headers carry units ("of 36 fits") | – | dash explained in note | – | – | – | – | – | PASS | table scrolls, hint shown |
| Fig 3 (fig-census) | el03_* | 928×380 px, 84% | PASS | ok ("SD of the output logit (log scale)") | PASS A/B | collapsed/working/hollow keyed | PASS: in-figure legend plus colored swatches in caption | y shared (panel B reuses A's ticks and gridlines) | n/a | n/a | PASS: floor tick "≤ 10⁻³", hollow marks, counts (59 + 26) verified against census.json; max SD 84 < 10² ceiling | PASS | ok |
| Fig 4 (fig-select) | el04_* | 920×370 px, 84% | PASS | ok ("event separation … (d)", d defined in caption) | PASS A/B | dashed identity line keyed | PASS | x=y shared, square 0–13.3 | n/a | n/a | none needed: max d_out 12.7 < 13.3 | PASS | ok |
| Fig 5 (fig-onset) | el05_* | 810×266 px, 74% | **FAIL minor**: blue working line hidden under the orange line, steps 0–~490 | ok ("silent head layers (of 8)", "training step") | single panel | legend | PASS | same x as Fig 6 | n/a | step axis, not time | n/a | PASS | ok |
| Fig 6 (fig-curves) | el06_* | 810×460 px, 74% | PASS | ok (loss is unitless) | single panel | 6-entry legend, solid vs dashed explained | PASS; see green note below | y 0–2 shared with Fig 7 | n/a | step axis | PASS in fact (max smoothed 1.70 < 2.0), but the caption sentence is hard-coded | c6 green #008300 has no dark step: dim on #1a1a19 | at 390 the right legend column (incl. the orange as-run line) is off-screen |
| Fig 7 (fig-warmup) | el07_* | 810×356 px, 74% | PASS | ok | single panel | trains / does not train / 0.5 line keyed | PASS | y shared with Fig 6 | n/a | step axis | caption computed; one line peaks at 1.996 and visually touches the 2.0 frame (minor) | PASS | ok |
| Table 2 | el08_* | 980×283 px, 89% | PASS | ok | – | – | – | – | – | – | – | PASS | identifying column is rightmost, off-screen at 390 |
| Table 3 | el09_* | 799×220 px, 73% | PASS | ok (column headers name the counts) | – | – | – | – | – | – | – | PASS | scrolls |
| §§ 1–7, answer box, refs | light/dark_1100_00–08, _390_00–11 | 1000 px column | no overlap; code paths wrap | – | – | – | – | – | – | – | – | PASS: all colors are CSS variables with a dark branch; the only literal `#fff` values are in classes this page does not use | no page-level scroll |

**Numbering:**
- Figures 1–7 and Tables 1–3 appear in order, and each is cited with its number and name.
- Two ordering deviations:
  - In §4, Figure 6 ("the replays") is cited one sentence before Figure 5, but Figure 5 is placed first.
  - The answer box forward-cites Figure 4 before Figure 2. That is a summary, so it is acceptable.

**Document properties (HTML):**
- `<title>` equals the h1 and names this page. There is no author meta.
- There is no build date or commit stamp on the page beyond the folder names in §7.

## Findings (location · issue · severity · suggested fix · verified)
1. **Fig 1 · unlettered panels described by position.** The figure has three regions: lane, working-fit trace and collapsed-fit trace. The caption uses "Lane:" and "Below:". · **major** (checklist rule) · Letter the regions A/B/C (or A = lane, B = working, C = collapsed) in the SVG, and refer to them by letter in the caption and in §1/§4. · verified: yes (render + `fig_problem` source)
2. **Fig 5 · working-fit line hidden.** The blue line is drawn first and lies under the orange collapsed line at y = 0 for steps 0–~490. A reader sees the working fit start at step ~500. · minor · Draw the working fit last, or offset or thicken it, or say in the caption that it lies under the orange line at 0 until step ~500. · verified: yes (2× crop; dict order in `page()` puts working first)
3. **Fig 1 · label overlap.** The working-fit trace (a spike near 41m) runs through the "threshold, 2.9" label. · minor · Give the label a surface-colored halo (paint-order stroke), or move it left of the last spike, or place it outside the plot at the right. · verified: yes (2× crop)
4. **Fig 6 · hard-coded clamp caption.** "The axis stops at 2.0; no smoothed line reaches it" is a literal string, while Fig 7's sentence is computed. It is true today (max smoothed loss 1.70, from replays/*.json), but it will not follow the data. · minor · Compute it the way Fig 7 does, or assert it. · verified: yes
5. **Fig 7 · line touches the frame.** One smoothed line peaks at 1.996, touching the 2.0 top edge, so it looks clamped even though the caption correctly says none passes it. · minor · Raise the axis top to 2.5, or add a small headroom pad. · verified: yes (data + render)
6. **Fig 6 dark mode · dim green.** `--c6` #008300 (50-step warm-up) has no dark-mode step and is dim on the dark surface. It is also a second green beside `--c3`; only the dash separates them. · minor · Add a lighter dark-mode step for c6, or pick a non-green slot. · verified: yes (dark_1100 crop; CSS comment admits "no separate dark step")
7. **Figs 1, 2 · unexplained gray bands.** The alternate-row gray bands are not identified. They are zebra striping for reading rows. · minor · Say so once ("shaded rows only aid reading"), or drop the band. · verified: yes
8. **Fig 2 at 390 · small text.** SVG text renders at about 9–10 px (viewBox 990 squeezed to 820 min-width). · minor · Raise the font size for this figure, or set min-width to its natural 990. · verified: yes (geometry json)
9. **Fig 6 / Table 2 at 390 · keys off-screen.** Fig 6's right legend column, which keys the orange as-run line, and Table 2's identifying "configuration" column are off-screen until the reader scrolls. · minor · Stack Fig 6's legend in one column; move the configuration column in Table 2 to the left. · verified: yes (390 crops)
10. **§4 · figure order.** Figure 6 is cited before Figure 5 in the same paragraph, but Figure 5 is placed first. · minor · Swap the two figures' placement, or reorder the two sentences. · verified: yes
11. **Captions of Figs 5 and 7 · bare figure references.** They use bare references ("the fits in Figure 1", "Figure 3's", "listed in Table 2"). House rule: a reference carries number and name. Separately, the `ref_` injection reads awkwardly in §4 ("The collapsed fit of Figure 1, a collapsed fit on a held-out recording and its working sibling…"). The prose itself is role 8's call. · minor · Add names to the caption references; restructure that §4 sentence. · verified: yes
12. **Fig 4 · large empty area in each panel.** The square 0–13.3 axes put all input-side data in the left ~28% of each panel. Whether the identity line justifies this is agent 9's call. · minor (geometry note) · Consider an x-range of about 0–4 with the diagonal clipped, or leave as designed. · verified: yes (census.json max d_in 3.68)
13. **Page · no build stamp.** There is no build date or commit stamp. · minor · Add a "built <date> from <commit>" footer line. Note: it would have to come from the data or an argument to keep the byte-equal rebuild test passing. · verified: yes

These checks passed:
- Figs 2/3/4 lettering, and shared axes where the same measurement repeats (Figs 2, 3, 4; Figs 6/7 y).
- Color keys render in color next to what they explain.
- Hollow floor marks and the "≤" floor tick in Fig 3, with counts matching census.json (59 + 26 inner fits).
- Down-pointing ▼ in a lane above the traces, and no raster on the page.
- Minutes-friendly time axis on Fig 1.
- Dark-mode tokens.
- No page-level scroll at 390.
- No console errors.
- Build is current and reproduces byte for byte.

No blocking findings.
