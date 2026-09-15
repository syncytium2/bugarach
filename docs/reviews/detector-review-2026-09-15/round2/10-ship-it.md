> **Public copy.** Lines that concern real treatment recordings are removed (12 here), per FOUNDATIONS §5, and machine paths are shortened to `<scratchpad>`, `<worktree>`, `<darkroom>` or `<home>` (sapper SAP004). Everything else is verbatim.

GRANT 10 ok — Read, Grep, Glob, Bash

# Role 10, Ship It: build and craft gate, round 2 blind pass

**Artifact checked:** `detector_review.html`, sha256 `935452c9…7c25ab7`. I confirmed the hash on disk before rendering.

**How I rendered it:** Playwright chromium, at a 1280×900 desktop viewport and a 400×860 phone viewport, full page. I also took element screenshots of every figure and table, and looked at each figure PNG at native size (2360 px wide). The one exception to "measured" is the build-currency column, which comes from file timestamps and says so.

**Screenshots:** all evidence is in `<scratchpad>\mb_scratch\role10_r2\`. File names below are relative to that folder: `desktop_p01…p12.png` and `phone_p01…p16.png` are page slices, `*_figNN.png` are figures, `*_tableN.png` are tables, and `zoom_*.png` are close-ups.

**Run note:** the project's no-heredoc hook blocked writing a script file, and I have no Write tool. So I piped the scripts to Python on stdin. No project file was written or edited.

## Page-level checks (both widths)

| check | desktop 1280 | phone 400 | evidence |
|---|---|---|---|
| Sideways page scroll (scrollWidth vs viewport) | 1280 = 1280, none | 400 = 400, none | render.py output; nothing outside `.scroll` is wider than the viewport |
| All 16 images load | 16/16 loaded, each 2360 px wide | 16/16 | naturalWidth > 0 for all |
| Embedded base64 matches the fig PNG beside it | 16/16 identical sha256 | n/a | hash comparison |
| Broken in-page anchors | 0 of 12 | 0 of 12 | every `#id` resolves |
| Figure links (`figNN.png`) | relative; the generator copies the PNGs next to the page (`make_detector_review.py` about line 1590) | same | the links work only while the PNGs stay beside the page |
| Console errors / failed requests | none | none | |
| Leftover `{{tokens}}`, `nan`/`None`/`undefined` | none | none | regex scan with base64 removed |
| Mojibake | none; non-ASCII is only – — − ¹ ▼ ▽ ○ ⚠ ö ü ć, all intended | none | |
| British spellings | none found (analyse, colour, centre, grey, modelling, labelled and similar) | none | |
| HTML validity | doctype, `lang="en"`, charset, viewport and `<title>` present; alt text on 16/16 images; unquoted attributes are valid HTML5 | same | |
| Gap between figure and caption | 8 px on all 16; captions never touch | 8 px on all 16 | |
| Tables | Tables 1–3 all fit (1180 of 1180) | Tables 1 and 3 wrap to fit; Table 2 is 1022 px in a 368 px scroller and scrolls sideways | `phone_table1.png`, `phone_table2.png` |
| Text under 13 px | only `<sup>` (12.5 px) | only `<sup>` | |
| Build is current | **fails, see B1** | same | file timestamps |

## Rendered box of each figure

The width is the same for every figure: 1182 CSS px on desktop (92% of the viewport) and 370 px on phone (92.5%). On desktop the image is shrunk to 50% of native size; on phone to 15.7%.

| fig | desktop box (w×h px) | phone box | build current? | defects (IDs below) |
|---|---|---|---|---|
| 1 | 1182×858 | 370×269 | **no**: staged 11:45, generator last edited 12:02 | M4, n6 |
| 2 | 1182×1483 | 370×464 | **no**: staged 11:47 | n1 |
| 3 | 1182×501 | 370×158 | yes (12:03) | M1, M4 |
| 4 | 1182×501 | 370×158 | yes | M4, n5 |
| 5 | 1182×501 | 370×158 | yes | M4 |
| 6 | 1182×501 | 370×158 | yes | M1, M4 |
| 7 | 1182×501 | 370×158 | yes | M1, M4, n2 |
| 8 | 1182×661 | 370×208 | yes | M4 |
| 9 | 1182×1189 | 370×372 | yes (12:03) | M4, n2, n3, n4 |
| 10 | 1182×1105 | 370×346 | **no**: staged 11:46 | n7 |
| 11 | 1182×919 | 370×288 | **no**: staged 11:46 | n8 |
| 12 | 1182×745 | 370×234 | **no**: staged 11:46 | M2, M3, n8 |
| 13 | 1182×1552 | 370×485 | **no**: staged 11:44 | M5 |
| 14 | 1182×1552 | 370×485 | **no**: staged 11:44 | M5 |
| 15 | 1182×1552 | 370×485 | **no**: staged 11:44 | M5, n9 |
| 16 | 1182×1552 | 370×485 | **no**: staged 11:45 | M5, n9 |

Every figure, at both widths, has the same phone-readability defect (M6).

## Blocking

**B1. Nine of the 16 embedded figures, and part of the page's numbers, may predate the last generator change.**
- **Where:** Figures 1, 2 and 10–16.
- **Evidence:**
  - `tools/make_detector_review.py` was last modified at 12:02:22.
  - [line removed from the public copy: it concerns real treatment recordings (FOUNDATIONS §5); the verbatim report is in the darkroom delivery folder]
  - Only figures 3–9 and `numbers.json` were restaged after the edit (12:02–12:03).
  - The generator is an untracked file, so there is no diff showing what the edit between 11:47 and 12:02 touched.
  - Under the build-current rule, those figure rows describe images that may not match what today's generator would produce.
- **Fix:** Either restage every stage and rebuild, or record from the session which functions the edits after 11:47 changed and show they touch only the stages for figures 3–9.
- **Could I verify against a source?** No. There is no history for an untracked file.

## Major

**M1. The bottom-row y-axis label is cut off at its top end in three figures, and the cut words carry the unit.**
- **Where:** Figure 3 reads "events per second, all ROI…". Figure 6 reads "ROIs active in each 10 s bi…". Figure 7 reads "ROIs switched on, per 0.1 s fra…". The cut is the same in panels A and B. Figures 4, 5 and 8 fit.
- **Evidence:** `zoom_fig03_ylabel.png`, the native `fig06_sce.png` and `fig07_cicada.png`, and `desktop_p03.png`.
- **Fix:** Shorten the labels (for example "events/s, all ROIs", "ROIs per 10 s bin", "ROIs on per frame"), or make the bottom row taller.
- **Verified:** yes.

**M2. In Figure 12C the busy-background points lose their size class.**
- **Where:** Figure 12C.
- **Evidence:**
  - The key says the shade gives the size class (black = 30%, dark gray = 18%, light gray = 10%) and that filled means quiet, hollow means busy.
  - Every hollow marker is white with the same dark outline, so the three busy classes look identical.
  - Only a horizontal offset, which the key never mentions, separates them.
  - See `zoom_fig12_C.png`.
- **Fix:** Put the class shade on the hollow marker's outline, or add a note to the key such as "left to right: 30%, 18%, 10%".
- **Verified:** yes.

**M3. The Figure 12 heading for B and C says "quiet background", but panel C also plots busy results.**
- **Where:** The strip heading "B, C · quiet background: …" in Figure 12.
- **Evidence:** Panel C's own key says "hollow: busy", and hollow markers are drawn. See `review/fig12_performance.png`.
- **Fix:** Give B and C separate headings, or write "B · quiet background; C · quiet (filled) and busy (hollow)".
- **Verified:** yes.

**M4. Several color keys exist only as plain words in the caption.**
- **Where:**
  - Figures 3–8 and 9B/C: the bottom-row lines (blue or other color = measure, gray = average, black dotted = bar) are named only in gray-free caption text below the figure. The key above the figure covers glyphs only.
  - [line removed from the public copy: it concerns real treatment recordings (FOUNDATIONS §5); the verbatim report is in the darkroom delivery folder]
- **Evidence:**
  - [line removed from the public copy: it concerns real treatment recordings (FOUNDATIONS §5); the verbatim report is in the darkroom delivery folder]
  - The checklist rule says a key that names colors in plain text is functionally absent.
  - See `desktop_fig01.png` and `desktop_p03.png`.
- [line removed from the public copy: it concerns real treatment recordings (FOUNDATIONS §5); the verbatim report is in the darkroom delivery folder]
- **Verified:** yes.

*[line removed from the public copy: it concerns real treatment recordings (FOUNDATIONS §5); the verbatim report is in the darkroom delivery folder]
- [line removed from the public copy: it concerns real treatment recordings (FOUNDATIONS §5); the verbatim report is in the darkroom delivery folder]
- **Evidence:** The lanes read "tube (learned)", "tube_guard", "tube_ratio" and "tube_ratio_guard". The text, Tables 2 and 3, and Figures 9 and 12 use "tube", "tube-guard", "tube-ratio" and "tube-ratio-guard". The underscore forms are code identifiers.
- **Fix:** Pass display names to `build_page`, using the `NAMES` mapping from Figure 9.
- **Verified:** yes.

**M6. On a phone, no figure is readable in place.**
- **Where:** All 16 figures at 400 px width.
- **Evidence:**
  - Figures are shown at 15.7% of native size, which puts tick and lane labels at about 2–3 CSS px. See `phone_fig03.png`.
  - The only way to read them is to tap through to the PNG. The page says so once, in the last line of the page.
  - [line removed from the public copy: it concerns real treatment recordings (FOUNDATIONS §5); the verbatim report is in the darkroom delivery folder]
- **Fix:** State "tap or click a figure to enlarge" near the top of the page or in each caption. Consider a narrow-screen `<picture>`/`srcset` crop, or allow pinch-zoom on the image.
- **Verified:** yes.

## Minor

**Figure-level**

- **n1. Figure 2B has two legends that name the same lines differently.** The strip legend says "recorded / circular shift / shuffle"; the legend inside the plot says "real / shift / shuffle". The two sub-panels (fast and slow stream) are both lettered "B" and differ only in their x-labels. Evidence: `review/fig02_surrogates.png`. Fix: drop the in-plot legends, and letter the sub-panels B1/B2 in the caption.
- **n2. False-alarm × markers are half cut off at the panel edge.** This happens at the right edge of Figure 7B and on the trace/tiny lanes at the left edge of Figure 9C. Evidence: `zoom_fig07_B_rightedge.png`, `zoom_fig09_C_leftedge.png`. Fix: pad the lane's x-range, or turn off clipping for the lane glyphs.
- **n3. The Figure 9A legend swatch is dark red only.** The center filters are drawn in four different colors, one per model (dark red, red, orange, yellow). Fix: "colored: center filters (one line per scale)".
- **n4. The surround dips in Figure 9A nearly touch the lower frame.** The tube-ratio-guard dips stop about 3 native px above the frame, and the caption points readers at exactly these dips, so they read as clipped. I measured the pixels: they are not clipped, the 5% padding is just too small. Evidence: `zoom_fig09_A4.png`. Fix: raise the padding to about 15%.
- **n5. In Figure 4B the black bar dashes from neighboring tested bins overlap into a jagged stack.** Fix: make the dashes narrower (bin width × 0.8).
- **n6. The "▮ a call" key in Figures 3–9 is a gray swatch, but calls are drawn in each detector's color.** Fix: say "a call (detector color)".
- **n7. Glyphs collide in the Figure 10 A1/A2 lanes.** Some decoy ▽ markers sit directly on planted ▼ markers or on each other (A1 near 2 min and near 4 min). Fix: stagger the decoy row further, or shrink the glyphs.
- **n8. The same concepts get different glyphs, and one axis names a detector instead of a quantity.**
  - The shipped setting is a filled ◆ in Figure 11C but a hollow ◇ in Figure 12.
  - Figure 11C's y-labels name the detector ("C · rate+context (0–1)") rather than the quantity ("score (0–1)").
  - Figure 11C's x-axis titles sit at different heights because the rotated tick labels differ in length.
  - Fix: use one diamond style across both figures, use "score (0–1)" as the y-label, and fix the x-label offset.

*[line removed from the public copy: it concerns real treatment recordings (FOUNDATIONS §5); the verbatim report is in the darkroom delivery folder]

- [line removed from the public copy: it concerns real treatment recordings (FOUNDATIONS §5); the verbatim report is in the darkroom delivery folder]
- [line removed from the public copy: it concerns real treatment recordings (FOUNDATIONS §5); the verbatim report is in the darkroom delivery folder]

**Page-level**

- [line removed from the public copy: it concerns real treatment recordings (FOUNDATIONS §5); the verbatim report is in the darkroom delivery folder]
- **n12. On a phone, Table 2's scroll cue is invisible and the row labels scroll away.** The `.scroll` shadow is painted behind an opaque white table, so it never shows, and the detector column scrolls out of view. Evidence: `phone_table2.png`. Fix: make the first column sticky (`position:sticky;left:0;background:#fff`) and put the shadow on a pseudo-element.
- **n13. Table 2 uses three different placeholders.** "n/a", "—" and "not meaningful¹" all appear. Fix: use one convention and explain it in the caption.
- **n14. The build footer says "from commit f240215 plus uncommitted changes of the project's own tools".** For a page going into a public portfolio repo, the build can't be reproduced from any commit. Fix: commit the generator and template, rebuild, and stamp a clean sha.

## What passed and needs no action

- **Rasters:** every raster is black and white, with nothing drawn on it. Busy-block shading and all markers sit only in lanes (Figures 2C, 3–10).
- **Markers:** every directional lane marker points down.
- **Histograms:** none has vertical annotation lines. The n = 6 line in Figure 2B is on a survival curve and is in the key.
- **Shared y-limits:** Figure 2B both panels 1e-6–1; Figure 9A −0.4–0.6; Figure 11C 0–1; Figure 12A 0–1; the A/B pairs in Figures 3–8 match each other.
- **Axes:** all have names; units are in the label or the ticks.
- **Panel references:** panels are lettered and never referred to as left or right.
- **Legends:** none sits over data. I checked the insets in Figures 2B and 10C/D.
- [line removed from the public copy: it concerns real treatment recordings (FOUNDATIONS §5); the verbatim report is in the darkroom delivery folder]
