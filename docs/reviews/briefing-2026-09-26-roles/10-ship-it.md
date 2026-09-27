> Archived verbatim except machine-local paths (shown as `<darkroom>`, `<worktree>`, `<scratchpad>`, `<repo>`, SAP004) and redactions: call times and axis positions on real recordings (rows 7, 9 and 11) are
> replaced by `[t]`, because nothing derived from real data goes into this public repo (FOUNDATIONS §5). Each
> finding's substance survives.

GRANT 10 ok — Read, Grep, Glob, Bash (I also hold SubagentHandback, which is not an editing tool. I hold no Edit, Write or NotebookEdit.)

# Role 10, Ship It: build and craft gate for the full-panel briefing page (round 1)

The build is current and every link target exists. The page still has five blocking defects:
- **Four of the nine example captions give the wrong call time.** Figures 2, 3 and 9 are one minute late, and Figure 6 reads "20m60s". The formatter is at `tools/make_briefing.py:769`.
- **The time in the example links does nothing.** Every example link carries `&t=`, but the copied viewer only reads `slice` and `stream`.
- **The example PNGs are drawn at 11 pt but shown smaller.** They appear at 13.4 px on desktop and about 4.5 px on a phone. About 16% of each PNG is blank on the right.
- **At 390 px the whole page scrolls sideways.** The page is 526 px wide because an unbreakable `<code>` path in the section 3 box overflows.
- **Two figures have visible defects.** Figure 9's y-axis label is clipped, and Figure 10's call sits on the axis edge of a window that only extends one way.

## How I checked
- **Renders:** made with Playwright chromium from the repo `.venv`, full page, at viewport widths 1200 and 390, light and dark. All files are under `<scratchpad>\mb\`:
  - `full_1200_light.png`, `full_1200_dark.png`, `full_390_light.png`, `full_390_dark.png`
  - zoom bands `crop_1200_{light,dark}_{top,fig1a,fig1b,t2,ex1,ex2,ex3,ras,terms}.png` and `crop_390_{0..3}.png`
  - left-edge zooms of the source PNGs, `zoom_example_*_left.png`
- **Measurements:** computed in the DOM — font size of every text node (SVG text scaled by its displayed width over its viewBox width), each image's natural and displayed size, and `scrollWidth` per wrapper.
- **PNG text size:** from the generator. Text is 11 pt (14.67 px) at a page width of 1180 CSS px, saved at scale 2, so the PNGs are 2360 px wide.
- **Script note:** a repo hook blocks heredocs that contain `write_text`, so I piped the render script to `python -` and printed the metrics to stdout rather than writing a file. Nothing outside the scratchpad was changed.

## Build currency: PASS
- `index.html` and `briefing.json` were built at 20:30:13 EDT.
- The generator's last commit (86cfffe2) is timed 20:30:42, which is 29 s after the build. But the file's mtime is 20:29:01, before the build, and the worktree is clean. So the committed content is the content that ran.
- Nothing under `064/` or `065/` that the page embeds is newer than the build.
- `detections.csv` (18:19) is newer than its source `065/review/detect/calls.csv` (02:08).
- The PNGs and SVG were written between 20:29:15 and 20:30:13, in the same run.
- `viewer.html` is byte-identical to the worktree's `docs/site/raster_viewer.html`.

## Results table

| # | Section / figure | Checked against | Measured box (1200 / 390) | Result | Finding · severity · fix |
|---|---|---|---|---|---|
| 0 | Page shell: charset, viewport, nav | DOM, `full_1200_light.png` | — | PASS | `<meta charset='utf-8'>` is present. The four nav anchors resolve to existing ids. The `<title>` says "Full-panel briefing" but the h1 says "Full-panel night briefing" (low; make them match). |
| 1 | Header byline and "How to read it" box | `crop_1200_light_top.png` | full column | PASS | Times are EDT (built 20:29 EDT; benches scored 1:33 AM and 8:03 PM EDT). Seed counts carry units. |
| 2 | Table 1 (at a glance) | `crop_1200_light_top.png`, 390 wrap 358/596 | 1080 wide; scrolls inside its wrapper at 390 | PASS with a nit | Cells read "1 rows" in two places (low; make the unit singular for 1). |
| 3 | Figure 1 (leaderboard, inline SVG), geometry and type | `crop_1200_dark_fig1a.png`, `crop_1200_light_fig1b.png`, `crop_390_1.png` | 1000×2122 px = 92.6% of the 1080 column, 83% of the 1200 viewport. At 390: 1000 px in a 358 px wrapper, so 36% is visible. | PASS on type, FAIL on phone use | SVG text is 15.0 px at both widths, above the 14.67 px floor. At 390 the first screen of every row shows only the row labels: all the data sit off-screen to the right inside the scroll wrapper (medium). Fix: at narrow widths either scale the SVG (`width:100%`) and accept smaller text, or put the labels above each row. |
| 3a | Figure 1: axis, legend, colours | same crops | — | PARTIAL | The x-axis has name and units ("ΔF1 against CoactDetect at its shipped setting (95% interval)"; ΔF1 has no unit). Blue and red contrast. Filled means new bench and open means old; both are in the legend. Three problems: (i) **The legend and the only tick row are at the bottom of a 2122 px figure,** about 2000 px below the top rows (medium; repeat the ticks and legend at the top of each stream block). (ii) Red open (old bench over budget) and the interval bar have no legend swatch; only the caption covers them (low). (iii) No clipping or overlap found; every bar stays inside x 330–970. |
| 3b | Figure 1 in dark mode | `crop_1200_dark_fig1a.png`, computed styles | — | PASS | Text fill is rgb(232,230,225) on rgb(20,20,20). Open marks take the page background. Gridlines are rgb(58,56,51). All readable. |
| 4 | Tables 2–4 (per stream) | `crop_1200_light_t2.png`, 390 wraps 901 px | 1080; scroll inside wrapper at 390 | PASS on render, FAIL on units | Budget lines carry units ("calls/h", "calls/min"). The ruling-5 marks give bare parameter values: "(20.0)", "(0.0)", "(120.0)", "(8.0)", "dt at its cap (0.00078125)", "threshold_pctile at its cap (99.9921875)" (medium, house rule that every number carries a unit). Fix: add "s" or "%" and round to the grid's precision. |
| 5 | Figures 2–10: type at displayed size | DOM image metrics, generator line 353 | natural 2360 px, displayed 1082 px (1200) / 360 px (390) | **FAIL** | Text is drawn at 14.67 px on an 1180 px canvas and shown in a 1080 px column: 14.67 × 1080/1180 = **13.4 px (10.1 pt) on desktop**. At 390 it is 14.67 × 360/1180 = **4.5 px**, and the image is not in a scroll wrapper (high). Fix: see row 6. Cropping the canvas to the plot width alone brings desktop text to about 15.8 px. |
| 6 | Figures 2–10: geometry | pixel scan of each PNG, `crop_1200_*_ex*.png` | Ink ends at column 1981 of 2360 in every PNG, leaving **15.5–16.0% of each image blank on the right**. Images are 1082 px wide in a 1080 px column (`width:100%` plus a 1 px border each side, so 2 px overflow). | FAIL | The capture canvas is 1180 px for 1000 px panels, so the figure gives up about 170 px of the column to white space (medium). Fix: match the capture viewport to the panel width, or trim the PNG. Add `box-sizing:border-box` to `figure img` (low). |
| 7 | Figures 2–10: caption times | captions against each render's x-axis, and generator line 769 | — | **FAIL** | `f"{t / 60:.0f}m{t % 60:02.0f}s"` rounds the minutes instead of flooring them. Results (high — the caption contradicts the figure beside it): Figures 2, 3 and 9 each say a minute later than the call the render is centred on. Figure 6 says "20m60s". Figure 10 says "0m00s" for a call at [t]. Figures 4, 5, 7 and 8 are correct. Fix: `m, s = divmod(round(t), 60)`, then reuse the house minutes formatter. |
| 8 | Figure 9: y-axis label | `zoom_example_combined_leader_only_left.png` | — | FAIL | The label is clipped to "combined · 30 RO"; the final "I" is cut off (medium). Fix: raise the panel height or `min_border_left` for short rasters. |
| 9 | Figure 10: subject call at the window edge | `zoom_example_combined_ref_only_left.png`, `crop_1200_light_ex3.png` | — | FAIL | The call at t = [t] makes `max(0, t − half)` clamp the window to 0–2m. The subject CoactDetect mark sits on the y-axis spine and tick, so they overlap. The caption still says "120 s either side", but the render shows only the 120 s after (medium). Fix: pad the axis range left of 0, or skip calls within `half` of the recording start, and word the caption from the actual window. |
| 10 | Figures 2–10: marking the subject call | all example crops | — | PARTIAL | Nothing in any figure marks which call the caption means. It is only implied by the window centre. In busy windows (Figures 5, 8, 9 and 10 have 5–8 calls per lane) the reader cannot find it (medium). Fix: one ▼ in a lane above the lanes at the subject onset, legended. It must not go on the raster. |
| 11 | Figures 2–10: raster, lanes, axes, colours | example crops | — | PARTIAL | Nothing is drawn on the raster; the lanes sit above it (pass). Ticks are minutes-style (e.g. [t], 2m, 0s) (pass). The y label names the stream and ROI count (pass). The x-axis label is a bare "t" with no name or unit (medium; e.g. "time (min:s)"). Lane colours are identified by lane row labels (pass). One grey is reused for different detectors: chorus_gain_norm_part in Figures 2–4 and 8–10, line in Figures 5–7, and chorus_norm_part too, so Figures 8–10 have two grey lanes (low; one colour per detector across all figures). |
| 12 | Figures 2–10 in dark mode | `crop_1200_dark_ex1.png` | — | PASS | The PNGs sit on a white card with a border, and the captions are readable. |
| 13 | Section 3 box (opening a recording) | `crop_1200_light_ras.png`, 390 metrics | — | **FAIL at 390** | At 390 the page's `scrollWidth` is **526 px, beyond the 390 px viewport, outside any scroll wrapper**. The one element overflowing is the `<code>` holding the absolute `detections.csv` path, which cannot break (high on the house rule). Fix: `overflow-wrap:anywhere` on `.box code`, or show the file name only. The same text prints an absolute Windows path with a person's name in it: fine in the darkroom, but it is Windows-only and would be wrong on the Mac (low). |
| 14 | Table 5 (group × first-treatment pages) | `crop_1200_light_ras.png`, file checks | 1080; fits at 390 (358/358) | PASS | All 24 relative links `../065/review/pages/<GROUP>_<treatment>_<stream>.html` exist; that folder holds 48 files. Groups appear in the order DI, OVX, MALE, ORX. |
| 15 | Table 6 (66 recordings with viewer links) | DOM, regex over hrefs, `detections.csv` | 1080; 358/387 at 390, inside a wrapper | PARTIAL | All 198 links match `viewer.html#slice=…&stream=(fast\|slow\|combined)`. `viewer.html` is present. The 66 linked recordings exactly match the 66 in `detections.csv`. Groups are in order DI, OVX, MALE, ORX. The viewer's `readDeepLink()` reads only `slice` and `stream`: the `&t=` on every figure link in Figures 2–10 is silently ignored, so those links open the recording but not the call (high; either add `t` to the viewer — a site change — or drop `t` and say the link opens the recording). |
| 16 | Terms table | `crop_1200_light_terms.png` | full column; not wrapped, but no overflow at 390 | PASS | EDT is defined. |
| 17 | Figure numbering | DOM | — | PASS | Figures 1–10 are numbered in their captions, and so are Tables 1–6. Each image's alt text is "Figure N", which describes nothing (low; alt text belongs to another role). |
| 18 | Type floor, HTML text | DOM font census (all four renders) | — | PASS | The smallest HTML text is `code` at 16.15 px and the smallest SVG text is 15.0 px. Only the PNG text (row 5) is below 14.67 px. |
| 19 | Document properties | `<head>` | — | PASS (HTML) | The page is stamped "Built 2026-09-26 20:29 EDT". It has no author meta tag, which the HTML house style does not require. |

## Could I verify each finding against a source?
Yes for all of them:
- Rows 7 and 15 were checked against generator line 769 and the viewer's `readDeepLink` source.
- Rows 5 and 6 were checked against generator lines 353–365 and pixel scans of the PNGs.
- Row 13 was checked against DOM `scrollWidth`.
- Rows 8–10 were checked against zoomed crops of the source PNGs.

Following the public-repo constraint, this report names no recording by id; it points only to figure and table numbers.
