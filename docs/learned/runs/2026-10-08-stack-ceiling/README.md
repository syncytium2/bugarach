# The stack ceiling: a first look on simulated recordings (2026-10-08)

**What this is.** Tony's question of 2026-10-08, asked to get away from the approaches `stack`
shares with LoCo and count (sliding): *"what is the tallest stack of width w we can create from
circular shifting events over period p?"* The answer is a count. Every ROI (region of interest,
a cell) with an onset anywhere in the period can be slid into the window, so the tallest stack
is the number of ROIs with an onset in the period: the **ceiling**. The **fill** is the height
(ROIs in the window, unshifted) divided by the ceiling. No probability, no calibration, no draws.

**The call rule tried here.** A tower at a moment stands with no shift. The **cost to rebuild
it elsewhere** is the shift per ROI it takes to build a tower as tall at a typical other moment
of the same period (the median over them), in seconds. A moment is called when that cost
reaches a setting and at least 3 ROIs stand; called moments under 0.5 s apart are one call.

**The page.** [`explainer_stack-ceiling_20261008.html`](explainer_stack-ceiling_20261008.html)
animates one period of a simulated recording as its ROIs shift toward the window, beside the
tower they build and the growth curve the animation traces. Below that, the whole recording
with the calls in a lane above it, and a slider for the setting. Open it in a browser; the
[picture](explainer_stack-ceiling_20261008.png) is one frame of it.

    python tools/make_stack_ceiling_demo.py --also docs/learned/runs/2026-10-08-stack-ceiling

**Strength: one look, two simulated recordings, one seed. Nothing here is a result.** The
recordings are the bench's (32 ROIs, 15 minutes, busy baseline background, 0.1 s frame grid):
one with six planted events, one with a raised-rate stretch and nothing planted. Window 2 s,
period 2 minutes.

| moment | height | ceiling | fill | cost to rebuild elsewhere |
|---|---|---|---|---|
| planted event, 10 ROIs | 12 ROIs | 17 ROIs | 0.71 | 30.0 s |
| planted event, 6 ROIs | 6 ROIs | 15 ROIs | 0.40 | 17.1 s |
| planted event, 3 ROIs | 3 ROIs | 16 ROIs | 0.19 | 2.4 s |
| background, where fill is highest | 5 ROIs | 15 ROIs | 0.33 | 9.5 s |
| raised-rate stretch, where fill is highest | 19 ROIs | 32 ROIs | 0.59 | 1.9 s |

The calls, at the settings the page opens with. The verdict is the page's own: a planted event
is found when a call lies within 2.5 s of it. It is not the bench's scorer.

| rule | recording | calls | planted events found | false calls |
|---|---|---|---|---|
| rebuild cost at least 10 s | six planted events | 4 calls | 4 of 6 | 0 |
| rebuild cost at least 10 s | raised-rate stretch | 1 call | none planted | 1 |
| fill at least 0.4 | six planted events | 4 calls | 4 of 6 | 0 |
| fill at least 0.4 | raised-rate stretch | 22 calls | none planted | 22 |

What that shows, and no more than that:

- Both rules find the four events of 6 and 10 ROIs and miss both 3-ROI events. A 3-ROI tower is
  as cheap to rebuild as the background's own.
- In the raised-rate stretch, fill makes 22 calls and the rebuild cost makes 1. A tall tower
  there is cheap to rebuild a few seconds away, which is what the cost was meant to see.
- ⚠ The two settings were picked by eye on seeds 7 to 10 of these same recordings, so the
  table is a fit, not a test.
- ⚠ The cost saturates near a quarter of the period (30 s here) for a tower holding most of
  the period's ROIs.

**Not done.** No bench run, no bench scorer, no real recording, no search of the setting, the
window or the period. The page was not put through the murderboard.

Code: `src/bugarach/detectors/stack_ceiling.py`, `tests/test_stack_ceiling.py`,
`tools/make_stack_ceiling_demo.py` (which checks the page's numbers and calls against the module
before it writes the page).
