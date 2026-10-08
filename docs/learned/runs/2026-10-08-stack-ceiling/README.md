# The stack ceiling: the idea, a page, and one bench run (2026-10-08)

![Figure 1](explainer_stack-ceiling-bench_20261008.png)

**Figure 1. The stack ceiling's call rule on the three benches, by threshold.** Columns are the
fast, slow and combined streams. Top row: F1 (the harmonic mean of recall and precision), averaged
over the quiet and busy backgrounds. Middle row: calls per hour on recordings with nothing
planted. Bottom row: calls per minute inside a stretch where every ROI's rate is raised. Black
curve: the stack ceiling at each threshold. Horizontal lines: CoactDetect (blue), LoCo (purple),
count (sliding) (grey) and stack (global) (orange) at their shipped operating points. Dotted red:
count (sliding)'s limit. Dashed grey: the threshold picked on the other half of the seeds.
Everything drawn is from the odd seeds.

**Simulated recordings only. A working record of one day, not murderboarded.** Nothing ships
from it and no operating point changes.

## The result

**On the bench the rule is count (sliding) with fewer calls in a raised-rate stretch, and
nothing more.** It does not beat LoCo anywhere.

| stream | detector | F1, quiet | F1, busy | calls per hour, nothing planted | calls per minute in the raised-rate stretch |
|---|---|---|---|---|---|
| fast | LoCo | 0.623 | 0.657 | 0.00 | 0.00 |
| fast | CoactDetect | 0.619 | 0.609 | 0.11 | 0.02 |
| fast | count (sliding) | 0.619 | 0.561 | 0.61 | 0.08 |
| fast | stack (global) | 0.619 | 0.511 | 0.11 | 0.08 |
| fast | stack ceiling, 10 s | 0.602 | 0.588 | 0.50 | 0.00 |
| slow | LoCo | 0.834 | 0.815 | 0.00 | 0.00 |
| slow | CoactDetect | 0.792 | 0.788 | 0.00 | 0.05 |
| slow | count (sliding) | 0.835 | 0.813 | 0.00 | 0.05 |
| slow | stack (global) | 0.834 | 0.814 | 0.00 | 0.03 |
| slow | stack ceiling, 2 s | 0.834 | 0.816 | 0.00 | 0.05 |
| combined | LoCo | 0.797 | 0.814 | 0.00 | 0.00 |
| combined | CoactDetect | 0.805 | 0.735 | 0.44 | 0.03 |
| combined | count (sliding) | 0.830 | 0.767 | 0.44 | 0.08 |
| combined | stack (global) | 0.829 | 0.741 | 0.00 | 0.07 |
| combined | stack ceiling, 2 s | 0.830 | 0.768 | 0.44 | 0.02 |

What Figure 1 and the table show:

- **On slow and combined the picked threshold is 2 s, the lowest tried.** At that threshold the
  rule calls nearly every moment that reaches the floor, which is count (sliding). Its F1 matches
  count (sliding)'s to the third decimal. Raising the threshold only loses recall.
- **On fast the picked threshold is 10 s.** Against count (sliding) it gains 0.027 F1 on the busy
  background and loses 0.017 on the quiet one. LoCo is ahead on both.
- **It does what it was built for in the raised-rate stretch.** From a threshold of 3 s up it
  makes no call there on fast and combined, where count (sliding) makes 0.08 per minute. Every
  detector here is already far inside the limit of 1 per minute, so the bench barely rewards it.
- **The threshold cannot buy precision, because the false calls are on decoys.** A decoy is
  planted coordination the bench labels as not an event (ADR-0006). On fast, precision stays
  between 0.40 and 0.55 at every threshold while recall falls from 0.97 to 0.12. A decoy is as
  costly to rebuild elsewhere as an event is. With calls on decoys left out, count (sliding)
  scores 0.983 on fast and the stack ceiling at 10 s scores 0.943 and 0.926.
- **The floor does most of the work.** It ran from 3 to 20 ROIs over these recordings. A tower
  that reaches the floor is, on these recordings, almost always planted.

## How it was run

`tools/measure_stack_ceiling.py --seeds 48`, 672 recordings, 183 s on one laptop. Numbers:
[`bench_summary.json`](bench_summary.json).

- **Fixed, not searched:** the 2 s window and 3 s merge gap are count (sliding)'s shipped
  operating point on each stream. The ROI minimum is each recording's ADR-0008 floor. The period
  is 120 s, LoCo's context.
- **The threshold** was run at 2, 3, 4, 5, 6, 8, 10, 12, 15, 20 and 25 s on every recording.
  The pick is the threshold with the highest F1 on the even seeds among those inside count
  (sliding)'s two limits. Every number above is from the odd seeds. On slow and combined that
  is, per background, 24 recordings with planted events and 12 with a raised-rate stretch, and
  12 recordings with nothing planted. Fast has twice as many of each (the bench doubles its
  seeds under the realistic spacing).
- **Seeds** are the fresh ones (6000 onward) that no search and no training run saw. Planted
  events use the realistic spacing (ADR-0010).
- **References** run at their shipped operating points and the same floor. The learned
  `chorus_norm` was left out, because it needs checkpoints from the darkroom.
- The measure takes a median of 0.08 to 0.16 s per 45-minute recording.

## The idea

Tony's question of 2026-10-08, asked to get away from the approaches `stack` shares with LoCo
and count (sliding): *"what is the tallest stack of width w we can create from circular shifting
events over period p?"* The answer is a count. Every ROI (region of interest, a cell) with an
onset anywhere in the period can be slid into the window, so the tallest stack is the number of
ROIs with an onset in the period: the **ceiling**. The **fill** is the height (ROIs in the
window, unshifted) divided by the ceiling. No probability, no calibration, no draws.

**The call rule.** A tower at a moment stands with no shift. The **cost to rebuild it
elsewhere** is the shift per ROI it takes to build a tower as tall at a typical other moment of
the same period (the median over them), in seconds. A moment is called when that cost reaches a
threshold and at least the floor of ROIs stand.

## The page

[`explainer_stack-ceiling_20261008.html`](explainer_stack-ceiling_20261008.html) animates one
period of a simulated recording as its ROIs shift toward the window, beside the tower they build
and the growth curve the animation traces. Below that, the whole recording with the calls in a
lane above it, and a slider for the threshold. Open it in a browser; the
[picture](explainer_stack-ceiling_20261008.png) is one frame of it.

    python tools/make_stack_ceiling_demo.py --also docs/learned/runs/2026-10-08-stack-ceiling

The page uses two 15-minute recordings on one seed, a minimum of 3 ROIs in place of the floor,
and its own matching in place of the bench's scorer. On them, a threshold of 10 s finds the four
planted events of 6 and 10 ROIs, misses both of 3 ROIs, and makes 1 call in the raised-rate
stretch where fill at 0.4 makes 22. Those two settings were picked by eye on four seeds of the
same recordings.

## Not done

- No real recording.
- The window, the merge gap and the period were not searched, and the threshold was searched on
  a grid of eleven values.
- ⚠ The cost saturates near a quarter of the period (30 s at 120 s) for a tower holding most of
  the period's ROIs, so it cannot rank large events against each other.
- Neither the page nor this record was put through the murderboard.

Code: `src/bugarach/detectors/stack_ceiling.py`, `tests/test_stack_ceiling.py`,
`tools/make_stack_ceiling_demo.py`, `tools/measure_stack_ceiling.py`.
