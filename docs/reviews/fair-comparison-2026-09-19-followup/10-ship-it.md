<!-- Verbatim role report, except that this machine's absolute paths are written as %USERPROFILE% and <darkroom> (the repository is public). The unedited original is in <darkroom>/bugarach/2026-09-18-fair-comparison-run/report/review-followup/. -->

GRANT 10 ok — Read, Grep, Glob, Bash

**Role 10 (Ship It), round 4. I checked the built artifact, not the generator, and did my own pass before opening round 3's report.**

**Summary:** the build is current, nothing overlaps or runs off the page at either width, and every element the generator draws is present. There are no high-severity findings. Four are medium:
- the SVG accessible labels carry stale figure numbers;
- Figure 11 draws a dotted segment in LoCo's line style on another curve;
- Figure 8 places a "no result" × at a value on the F1 axis without saying what that value is;
- the ringed dot still means two different things across figures.

## Build currency: PASS
- **Same file in both places:** the repo `report.html` and the darkroom `index.html` both hash to `805b113`.
- **Build is newer than everything it uses:** `report.html` was written at 10:40:56. The generator was last modified at 10:37:44, and the newest run input (`replicate_summary.json`) at 10:01:14.
- **Worktree HEAD `127b337`** only rebuilds the report: `git diff 1a0a260 127b337` touches `report.html` and nothing else.
- **Rebuild matches:** I rebuilt from the worktree into `scratchpad\mb\r4-role-10\build\index.html`. Apart from the build time and the version stamp (`+g127b337` against `+g1a0a260`), it is byte-identical to the shipped file. The stamp difference is expected, since `127b337` is the rebuild commit. The provenance line reports no dirty tree.

## Render table
- **Where the renders came from:** Playwright chromium at 1100 px and 400 px viewports, with 2.5× zoom crops where noted. Every file named below is in `%USERPROFILE%\AppData\Local\Temp\claude\c--Users-<user>-bugarach-bugarach\0c979457-501e-4b3d-9c4b-21e394823cf5\scratchpad\mb\r4-role-10\`, and the measurements are in `measure.json`.
- **Column and figure widths:** the column is 980 px wide at 1100 (89% of the viewport). Every figure is an intrinsic 900 px wide. That is 91.8% of the column at 1100. At 400 only 368 of the 900 px show (41%), and the figure scrolls inside its container.
- **Nothing escapes the page:** the page's `scrollWidth` equals the viewport at both widths.
- **Text checks (DOM, all 14 SVGs):** no two text boxes overlap, no text box extends past its SVG edge, and no text renders below 11 px.

| Item | Checked against | Rendered box (px, W×H at 1100) | Overlap / off-edge | Axes: name + unit | Marks identified | Result |
|---|---|---|---|---|---|---|
| Fig 1 | w1100_fig01, zoom_fig1, w400_fig01 | 900×700 | 0/0 | 0s–40m and 16m–26m, minutes-friendly; ROI rows named "33 ROIs" | legend in A; lanes named in B; black-and-white raster; cues are down-triangles in lanes above it; 15 planted and 6 distractors counted, matching the caption | pass |
| Fig 2 | w1100_fig02, zoom_fig2 | 900×330 | 0/0 | schematic, "2.5 s" | legend covers all 4 marks, but the bracket's key swatch has no end caps | minor (N7) |
| Fig 3 | w1100_fig03 | 900×200 | 0/0 | schematic | legend covers all 3 marks | minor (N6) |
| Fig 4 | w1100_fig04 | 900×250 | 0/0 | "fold N: 12 seeds" | cells self-labeled | pass (N1: aria-label says "Figure 3") |
| Fig 5 | w1100_fig05 | 900×450 | 0/0 | seed ranges | legend covers all 4 fills; red/green verdict text is unkeyed | minor (N9; aria-label says "Figure 4") |
| Fig 6 | w1100_fig06 | 900×336 | 0/0 | 8s–12s | notes name "firings"; the bin counts inside the boxes have no unit | minor (R-F7) |
| Fig 7 | w1100_fig07 | 900×330 | 0/0 | both named, "per hour" | on-figure labels | N4 (aria-label says "Figure 6") |
| Fig 8 | w1100_fig08, zoom_fig8, w400_fig08 | 900×560 | 0/0 | "held-out F1"; both panels 0.2–0.85, shared | legend covers dot, bar, hollow, × | N3, N4 (aria-label says "Figure 7") |
| Fig 9 | w1100_fig09, zoom_fig9 | 900×514 | 0/0 | named, "(right of 0: the net is ahead)" | legend covers all 4 marks | pass |
| Fig 10 | w1100_fig10 | 900×430 | 0/0 | named; panels share −0.20 to +0.05 | legend, including "0: a tie" | pass |
| Fig 11 | w1100_fig11, zoom_fig11 | 900×380 | 0/0 | "held-out F1"; merge gap in s, log scale with a break | key for 7 curves plus ring | N2, N8 |
| Fig 12 | w1100_fig12 | 900×330 | 0/0 | "recall"; 3 panels share 0 to 1.0 | legend | pass (see N4) |
| Fig 13 | w1100_fig13, zoom_fig13 | 900×466 | 0/0 | "mean F1 on the crowded recordings" | legend covers ticks, band and dots, but not the × | N5 |
| Fig 14 | w1100_fig14 | 900×370 | 0/0 | named, "(right of 0: tuning helped)" | legend | pass |
| Table 1 | w1100_tab1, w400_tab1 | 980×1422; at 400, 599 in a 368 container, scrolls | none | n/a | n/a | pass |
| Table 2 | w1100_tab2 | 980×533; at 400, 477 in 368 | none | F1 unitless, *t* | n/a | pass; values match the Fig 8 marks |
| Table 3 | w1100_tab3, w400_tab3 | 980×898; at 400, 700 in 368 | none | "8 s" etc. | n/a | pass; start and shipped values match the Fig 13 ticks |
| Table 4 | w1100_tab4 | 803×189; at 400, 411 in 368 | none | n/a | n/a | pass |
| Page at 400 | full_400.png, DOM | width 400, height 40,241 | nothing outside the viewport except inside scroll containers | — | — | pass; the scrolling is disclosed ("On a narrow screen…", section 12) |
| Metadata | `<head>` | — | — | — | — | title, description, generator, date 2026-09-19 and `lang` present; no author (R-F10) |

**Other checks, all clean:**
- **Numbering and references:** all 14 figures are numbered, and each is referenced 3 or more times as number plus name. All 4 tables are numbered.
- **Shared limits:** multi-panel figures share their x-limits (8, 10, 12).
- **Histograms:** there are none.
- **Colour contrast:** blue against black, and blue against orange, contrast clearly.
- **Spacing:** the small multiples have real gaps between panels.

## Findings (location · issue · severity · fix · verified)

**N1. SVG `aria-label`s on Figures 4, 5, 7 and 8 carry stale numbers (medium, verified yes).**
- **Issue:** they say "Figure 3", "Figure 4", "Figure 6" and "Figure 7", left over from before the renumbering. A screen reader announces "Figure 4, scrollable" and then "Figure 3: …". The numbers are hardcoded in the generator at lines 435, 477, 561 and 599 (lines 338 and 394 are right only by luck).
- **Also:** some labels carry a "Figure N:" prefix and others do not (Figures 3, 6, 9–14 have none).
- **Fix:** take the number out of every `Svg(...)` description, since the region's label already names it, or derive the number from the figure counter.

**N2. Figure 11: the 0-to-2 s segments of every coded curve use a dotted `1 4` dash (medium, verified yes).**
- **Issue:** binned SCE's gray segment from 0.49 to 0.53 is visually LoCo's gray dotted style, and CoactDetect's is black dotted. The key does not explain this bridge style (generator line 773).
- **Fix:** draw the bridge in each curve's own dash with lower opacity, or add a key entry "dotted: across the axis break".

**N3. Figure 8B, locust: the × marks sit at x ≈ 0.55 on the F1 axis (medium, verified yes).**
- **Issue:** that position is the starting configuration's held-out F1 (generator lines 616–624). The caption says only "no result under the budget", so the position reads as an F1 of 0.55. Figure 13's caption explains the same placement ("the start was scored but is no result"); Figure 8's does not.
- **Fix:** add that sentence to the Figure 8 caption, or move the × marks into a margin column off the value axis.

**N4. The ringed dot still means two things, and Figure 8 does not ring the same fold (medium, verified yes).**
- **Two meanings:** in Figure 7 the ringed dot means "chosen" (on F1 alone, or under the budget). In Figures 9, 10 and 14 it means "a fold holding a refit below 0.2 F1".
- **Fold not ringed in Figure 8:** chorus_gain_norm, F1 alone, is the fold ringed at −0.15 in Figure 10A and at −0.03 in Figure 9. In Figure 8A it is a plain filled dot at 0.605, because the net branch sets `veto=[True]*4` and has no ring logic (generator line 618).
- **Figure 12 (not verified):** the low chorus_gain_norm recall fold is probably the same refit, also unringed.
- **Fix:** give Figure 7's "chosen" a different glyph, such as a star or a larger square outline. Ring the low-refit folds in Figure 8, and in Figure 12 if confirmed.

**N5. Figure 13: the × is keyed only in the caption (low, verified yes).**
- **Issue:** the on-figure legend has no × entry, although Figure 8's legend has one.
- **Fix:** add the same × legend item.

**N6. Figure 3 caption uses spatial words (low, verified yes).**
- **Issue:** it says "Above: … Below: …" for the two rows, which already carry names ("far apart", "close").
- **Fix:** refer to them as the "far apart" row and the "close" row.

**N7. Figure 2: the key swatch for "the span widened by 2.5 s" is a plain line (low, verified yes).**
- **Issue:** the figure draws that span as a bracket with end caps (zoom_fig2).
- **Fix:** draw end caps on the key swatch.

**N8. Figure 11: LoCo's chosen gap is not ringed (low, verified yes).**
- **Issue:** Table 3 gives LoCo's chosen gap as 8 s. The key restricts the ring to "(CoactDetect, binned SCE)" on purpose (generator line 780, "the two detectors the text reads"), so this is disclosed.
- **Also:** tick labels read "2 s" with a space, while Figures 1 and 6 use "8s" and "10m" without one, as the house `45s`/`2m` form does.
- **Fix:** adjudicate the ring. Either unify the tick-label spacing or accept it.

**N9. Figures 5 and 6: unkeyed red/green verdict text (low, verified yes).**
- **Issue:** red "2 distinct fitting sets" against green "4 distinct…", and red "no call" against green "a call". The words carry the meaning, so nothing is lost, but it is a red/green pair.
- **Fix:** optional; use a single ink, or a colour-blind-safe pair.

## Round 3's findings, checked after my pass
Round 3 numbered 12 figures, so its figure numbers are shifted from today's.

| Round 3 | Status |
|---|---|
| F1: glyph used two ways | **Partly resolved.** Hollow now means "fails crowded check" consistently (Figs 8, 13), and failed-refit folds are ringed consistently in Figs 9, 10 and 14. Still open: Fig 8 does not ring the fold, and Fig 7's "chosen" ring collides (N4). |
| F2: crossing leader lines in the merge-gap figure | **Resolved.** Figure 11 now uses a key. |
| F3: phone width | **Resolved as disclosure.** The note sits in section 12, not section 11 as round 3 suggested. The figures still open on labels only at 400 px, an accepted cost. |
| F4: ring radii | **Resolved.** One radius; the ring takes each curve's ink, which the key does not state. Trivial. |
| F5: no on-figure key (Figs 10–12 then) | **Resolved.** Figures 10, 12 and 14 now carry legends. |
| F6: locust × tangle and mean bar | **Resolved.** The × marks are spread by fold and there is no mean bar. Their x-position is new finding N3. |
| F7: Figure 5 (now 6) counts without a unit | **Partly resolved.** The notes now say "firings"; the bin counts inside the boxes have no unit. Low. |
| F8: panel headings are titles | **Partly resolved.** The long Figure 9B heading is gone. Short tags remain ("A. The whole recording", "A. As recorded", "B. The same firings, 0.45 s later"). Adjudicate. |
| F9: Figure 5 axis label past the SVG edge | **Resolved.** The clip scan reports 0. |
| F10: no author in the metadata | **Unresolved.** There is still no `<meta name="author">`. Low. |
| F11: caption and axis name the quantity differently | **Resolved.** The Figure 7 caption now matches the axis ("false alarms per hour on the training recordings"). |

## Files
- **Artifact:** `%USERPROFILE%\bugarach\bugarach-worktrees\fair-comparison-report\docs\learned\tuned_vs_coact\fair_comparison_2026_09_18\report.html` (darkroom `index.html` has the same hash, `805b113`).
- **Generator:** `%USERPROFILE%\bugarach\bugarach-worktrees\fair-comparison-report\tools\build_fair_comparison_report.py`
- **Scratch evidence**, in `%USERPROFILE%\AppData\Local\Temp\claude\c--Users-<user>-bugarach-bugarach\0c979457-501e-4b3d-9c4b-21e394823cf5\scratchpad\mb\r4-role-10\`:
  - element renders `w1100_fig01–14.png`, `w400_fig01–14.png`, `w1100_tab1–4.png`, `w400_tab1–4.png`
  - full pages `full_1100.png`, `full_400.png`
  - zoom crops `zoom_fig1/2/8/9/11/13.png`
  - geometry `measure.json`
  - the rebuild `build\index.html`

I edited nothing.