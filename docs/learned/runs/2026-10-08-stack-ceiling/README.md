# The stack ceiling: a first look on simulated recordings (2026-10-08)

**What this is.** Tony's question of 2026-10-08, asked to get away from the approaches `stack`
shares with LoCo and count (sliding): *"what is the tallest stack of width w we can create from
circular shifting events over period p?"* The answer is a count. Every ROI (region of interest,
a cell) with an onset anywhere in the period can be slid into the window, so the tallest stack
is the number of ROIs with an onset in the period: the **ceiling**. The **fill** is the height
(ROIs in the window, unshifted) divided by the ceiling. No probability, no calibration, no draws.

**The page.** [`explainer_stack-ceiling_20261008.html`](explainer_stack-ceiling_20261008.html)
animates one period of a simulated recording as its ROIs shift toward the window, beside the
tower they build and the growth curve the animation traces. Open it in a browser; the
[picture](explainer_stack-ceiling_20261008.png) is one frame of it.

    python tools/make_stack_ceiling_demo.py --also docs/learned/runs/2026-10-08-stack-ceiling

**Strength: one look, two simulated recordings, one seed. Nothing here is a result.** The
recordings are the bench's (32 ROIs, 15 minutes, busy baseline background, 0.1 s frame grid):
one with six planted events, one with a raised-rate stretch and nothing planted. Window 2 s,
period 2 minutes.

| moment | height | ceiling | fill | shift at which the tower reaches half the ceiling |
|---|---|---|---|---|
| planted event, 10 ROIs | 12 ROIs | 17 ROIs | 0.71 | 0.0 s |
| planted event, 6 ROIs | 6 ROIs | 15 ROIs | 0.40 | 12.3 s |
| planted event, 3 ROIs | 3 ROIs | 16 ROIs | 0.19 | 8.6 s |
| background, where fill is highest | 5 ROIs | 15 ROIs | 0.33 | 13.9 s |
| raised-rate stretch, where fill is highest | 19 ROIs | 32 ROIs | 0.59 | 0.0 s |

What the table shows, and no more than that:

- The 10-ROI event stands well clear of the background on fill.
- The 3-ROI event does not: the busiest background moment has a higher fill (0.33 against 0.19).
- The raised-rate stretch reaches a fill of 0.59 with nothing planted, above the 6-ROI event.
  The ceiling saturates at the ROI count while the height keeps rising with rate.

**Not done.** No rule turns fill into a call. Nothing was run on a bench, on more than one seed,
or on a real recording. The page was not put through the murderboard.

Code: `src/bugarach/detectors/stack_ceiling.py`, `tests/test_stack_ceiling.py`,
`tools/make_stack_ceiling_demo.py` (which checks the page's numbers against the module before it
writes the page).
