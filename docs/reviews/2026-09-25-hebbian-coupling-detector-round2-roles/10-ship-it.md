GRANT 10 ok — Read, Grep, Glob, Bash (I also hold SubagentHandback, which is only the hand-off channel. I hold no editing tools.)

# Role 10, Build & craft gate ("Ship It"): hebbian-coupling-detector proposal

The figure is built from current inputs, but it doesn't pass the craft checks. The link to the review record is dead. All three scripts you named ran clean.

The worst figure problems: about 22% of the image is blank space at the bottom, and at page width its text shrinks to 8–9 px against 16 px body text. Blue, orange and red also mean different things in panel B than in panel C.

## Renders I checked against
All in `<scratchpad>`:
- **R1:** the committed PNG, `docs/proposals/2026-09-25-hebbian-coupling-detector/hebbian_kernel.png`, 2520×1256 px, viewed whole.
- **R2:** the markdown rendered with cmarkgfm and GitHub-like CSS (880 px content column). The HTML is `page.html`; screenshots are `page_00.png`…`page_07.png`, all 8 pages viewed.
- **R3:** the committed SVG at 4× zoom: `zoomC.png` (tail of panel C), `zoomB.png` (key of panel B), `zoomBot.png` (under panel C). I also took every `<text>` bounding box from the SVG to check overlaps.
- **R4:** the SVG regenerated from the tool (`regen/hebbian_kernel.svg`), and the PNG re-rendered with your chromium command (`regen/rerender.png`).

## Per-item table

| item | render | result | detail |
|---|---|---|---|
| Build is current: SVG | R4 | PASS | Regenerated SVG is byte-identical to the committed one. |
| Build is current: PNG | R4 | PASS | Re-rendered PNG is byte-identical to the committed one. Tool 15:41:43, SVG 15:41:47, PNG 15:41:47, all in commit 5f6a271; working tree clean. |
| Markdown pages 1–8 | R2 | PASS | Nothing overflows the column. The Stages table fits without scrolling. Code spans wrap cleanly. Headings render. |
| Anchor `#what-is-asked` | R2 | PASS | The GitHub slug of "What is asked" is `what-is-asked`. |
| Relative links (8) | file check | **FAIL 1** | Line 6 links to `../reviews/2026-09-25-hebbian-coupling-detector_2026-09-25.md`, which does not exist. Only its `-roles/` and `-round2-roles/` folders do; I listed names only, not contents. The other 7 links resolve. The DOI link was not fetched. |
| Figure 1 box on the page | R2 | **FAIL (geometry)** | Placed at 880×439 CSS px, 100% of the column width. The PNG is 1260×628 CSS px but the SVG content ends at y≈490. Rows 490–628 (**22%** of the height, about 96 px on the page) are blank above the caption. Cause: the command used `--window-size=1260,628`, while the SVG is 540 tall; the tool's own Playwright path uses 540. The SVG itself also leaves about 50 px blank under its last text. |
| Figure text size on the page | R2 | **FAIL** | Scale is 880/1260 = 0.70. Tick labels (12 px) show at about 8.4 px, annotations and keys (11 px) at about 7.7 px, axis labels (13 px) at about 9.1 px. Body text is 16 px. Page 2 of R2 shows it plainly. Whether the layout should give the figure more room is agent 9's call; the measured sizes are reported here. |
| Overlap, panel A | R1, R3 | PASS | No text-box collisions. The rotated y-label clears the tick labels. The gray note under A (x 15–465) ends before B's y-label. |
| Overlap, panel B | R1, R3 | PASS (tight) | "same-frame artifact: 1" (y 60–72) and the fast-stream key entry (y 74–86) are 2 px apart vertically but offset horizontally, so they don't touch. |
| Overlap, panel C | R3 (`zoomC.png`) | **FAIL** | The red ▲ at s = 0.0220 sits on the q(s) curve where it crosses zero and against the right clamp line at 0.0216. Triangle, curve and dashed line collide. Suggest moving the triangles into a strip below the plot area, or clipping the curve at the clamp. |
| Clipping / off-canvas | R1, R3 | PASS | All text lies inside 0–1260 × 0–540. Rightmost is the 0.024 tick at x 1239. |
| Every element in the source is present | R1 vs `build()` | PASS | A: dashed cosine, 11 stems, hollow end dots, gray note. B: lines at 0 and 1 with their labels, two 5-point series, two key entries. C: two clamp lines with labels, zero line, curve, 3 triangles, 4 key lines. All are rendered. |
| Axis labels with name and units | R1 | PASS with a low note | A: lag (frames of 0.1 s) and update weight Co (unitless). B: span m (frames of 0.1 s) and expected Co (unitless). C: "coupling s (paper's units)" and "step size q(s) (paper's units)". "Paper's units" is a unit label only by reference; the text defines s₀ in those units. Low. |
| Shared y-limits for the same measurement | R1 | ADVISORY | A (−1.15 to 1.15) and B (−0.1 to 1.05) are both Co, but A is the kernel value and B its expected value per update. The difference is defensible but not marked. Low. |
| Panels lettered | R1, R2 | PASS | A, B and C are drawn. Text and caption say 1A/1B/1C. No left/right/top/bottom wording (grep: the only hits, lines 142 and 243, are unrelated). |
| Every line and mark identified | R1 | **FAIL (minor)** | A's dashed curve is named only in the caption ("the continuous cosine"), not on the figure. The filled dots at lags ±5 (outside the span, weight 0) are not explained anywhere. The hollow dots, B's lines and C's clamp lines are labeled on the figure. |
| One glyph / one color per concept | R1 | **FAIL** | Blue and orange are the fast and slow streams in B, but q₀ = 0.004 and q₀/12 in C. Red is the same-frame artifact in B and the paper's q₀ in C. The dashed style means three things (A cosine, B artifact line, C clamps), each labeled. Suggest a separate palette for C's step sizes. |
| Category colors contrast | R1 | PASS | Blue #1b6ca8 and orange #c2571a are clearly distinct; the red is distinct from the orange at full zoom. |
| Color key: in its colors, next to the figure, at body size | R1, R2 | PARTIAL | B's key and C's ▲ key are set in their own colors, next to their panels. On the page they show at about 7.7 px, not body size (see text-size row). |
| Direction of the ▲ markers | R1 | ADVISORY | C's up-pointing triangles sit just below the q = 0 line inside the plot area. The house rule on direction (CLAUDE.md, down-pointing marks over data) is about lanes above a raster or trace, so this is a judgment call. Noted only. |
| Typesetting consistency | R1 vs R2 | ADVISORY | The figure writes plain "q0", "q0 / 12" and "s0"; the text writes q₀, 0.01/12 and s₀. Figure ticks use hyphen-minus ("-0.5"); the text uses "−1". Low. |
| No vertical lines on a histogram | R1 | N/A | No histogram. A's stems are a stem plot of kernel values, not bars on a distribution. |
| Colorbar / overlay colors | R1 | N/A | No colormap. |
| Spacing between panels | R1 | PASS | The gaps between panels are about 70 px and hold the y-labels; the side margins are not wider than those gaps. |
| Document properties | R1, SVG | PASS / low note | The PNG carries only IHDR, IDAT and IEND chunks, so nothing is inherited from a template. The SVG has no `<title>`, so there is no title property. Low. |
| `pytest tests/test_index_resolves.py` | run | PASS | 483 passed in 0.32 s. That test covers INDEX only; it did not catch the dead review-record link. |
| `sapper.py --all` | run | PASS for scope | Exit 0. No hits on the proposal, on `tools/make_hebbian_kernel_figure.py`, on `docs/INDEX.md:117` (the Hebbian row), or on `docs/goals/unsupervised-learning.md` lines 49–54 (the bullet). The tree has 1534 WARN lines elsewhere. Some of those name `docs/reviews/2026-09-25-hebbian-*-roles/` files; I saw only the sapper lines, never opened those files. |
| `check_quotes.py --all` | run | PASS | "check_quotes: clear", exit 0. |

## Findings
Each row gives location · issue · severity · suggested fix · could I verify it against a source.

1. Proposal line 6 · the link to the review record points at a file that does not exist · **blocking for delivery** (it may be written at the end of the run, but as committed it is dead) · write the record at that path, or change the link · yes, by listing files.
2. The PNG canvas, set by the render command · 22% blank band at the bottom, because the window was 628 tall for a 540-tall SVG · major · re-render with `--window-size=1260,540`, or tighten the SVG to about 500 · yes, byte-identical re-render plus text boxes.
3. Figure 1 at page width · text at 7.7–9.1 px against 16 px body · major · enlarge the fonts in the SVG (about 16–18 px ticks) or give the figure a taller, narrower layout (layout is agent 9's call) · yes, measured on R2.
4. Panel C, s ≈ 0.022 · red ▲ collides with the q(s) curve and the clamp line · major · move the markers into a strip below the plot area, or stop the curve at the clamps · yes (`zoomC.png`).
5. Panels B and C · blue, orange and red each mean one thing in B and another in C · major · give C's three step sizes their own palette · yes.
6. Panel A · dashed cosine not identified on the figure; the ±5 dots at 0 are unexplained · minor · add an on-figure label ("continuous cos(πk/m)"), and drop the out-of-span dots or explain them · yes.
7. Panels A and B · both plot Co on different y-ranges, with the difference unmarked · low · note in the caption that B is an expectation on its own scale · yes.
8. Panel C axes · "paper's units" · low · keep it, or add "(s₀ = 0.012)" · yes.
9. Figure labels · q0 vs q₀, "q0 / 12" vs "0.01/12", hyphen-minus vs − · low · make them match the text · yes.
10. SVG · no `<title>` · low · add `<title>Figure 1 …</title>` · yes.

No step was skipped.
