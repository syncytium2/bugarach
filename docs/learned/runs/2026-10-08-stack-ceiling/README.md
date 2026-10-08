# The stack ceiling: the idea, a page, and two bench runs (2026-10-08)

![Figure 1](explainer_stack-ceiling-search_20261008.png)

**Figure 1. F1 on the three benches after searching every setting of the stack ceiling.** F1 is
the harmonic mean of recall and precision. Each pair of bars is one detector on the quiet (dark)
and busy (light) background. The reference detectors run at their shipped operating points. All
bars are from the odd seeds, which picked nothing.

**Simulated recordings only. A working record of one day, not murderboarded.** Nothing ships
from it and no operating point changes.

## The result, after the search

**Searched, the rule matches or beats the shipped LoCo on fast and combined. Almost none of that is the
stack ceiling's own idea: it is the sliding count in a 0.5 s window.**

The first run (next section) searched the threshold alone. Tony's question on it,
*"stack_ceiling was not optimized?"*, was fair: every detector beside it ran at a fully searched
operating point. `tools/search_stack_ceiling.py` then searched the window, the period, the merge
gap and the threshold as one grid of 2,520 settings per stream, picked on the even seeds inside
count (sliding)'s three limits, and reported on the odd seeds.

| stream | detector | F1, quiet | F1, busy | calls per hour, nothing planted | calls per minute in the raised-rate stretch |
|---|---|---|---|---|---|
| fast | LoCo | 0.623 | 0.657 | 0.00 | 0.00 |
| fast | count (sliding), shipped | 0.619 | 0.561 | 0.61 | 0.08 |
| fast | best with the rebuild cost off: window 0.5 s, gap 1.5 s | 0.625 | 0.670 | 0.00 | 0.00 |
| fast | stack ceiling, searched: window 0.5 s, period 480 s, gap 1.5 s, threshold 10 s | 0.625 | 0.686 | 0.00 | 0.00 |
| slow | LoCo | 0.834 | 0.815 | 0.00 | 0.00 |
| slow | count (sliding), shipped | 0.835 | 0.813 | 0.00 | 0.05 |
| slow | stack ceiling, searched: window 1 s, gap 0.5 s, threshold 0 s (cost off) | 0.828 | 0.812 | 0.00 | 0.00 |
| combined | LoCo | 0.797 | 0.814 | 0.00 | 0.00 |
| combined | count (sliding), shipped | 0.830 | 0.767 | 0.44 | 0.08 |
| combined | best with the rebuild cost off: window 0.5 s, gap 3 s | 0.824 | 0.830 | 0.00 | 0.00 |
| combined | stack ceiling, searched: window 0.5 s, period 480 s, gap 3 s, threshold 8 s | 0.824 | 0.831 | 0.00 | 0.00 |

Gain in F1 (mean of the two backgrounds) of the searched rule, on the odd seeds, with a 95%
bootstrap interval over recordings:

| stream | over LoCo | over count (sliding), shipped | over the best setting with the cost off |
|---|---|---|---|
| fast | +0.016 (−0.004 to +0.037) | +0.066 (+0.046 to +0.092) | +0.008 (+0.001 to +0.017) |
| slow | −0.004 (−0.009 to 0.000) | −0.004 (−0.008 to +0.001) | 0.000, the same setting |
| combined | +0.021 (+0.007 to +0.035) | +0.029 (+0.001 to +0.061) | +0.001 (−0.008 to +0.009) |

- ⚠ **The reference detectors here are the shipped points, and on fast those are not the best on
  record.** Fast LoCo and CoactDetect ship in their binned form at points set on 2026-09-16.
  Their sliding forms were searched on this realistic bench on 2026-09-26 and reached a held-out
  mean F1 of 0.661 each (from 0.626 and 0.583 shipped); nothing was adopted
  (`<darkroom>/bugarach/2026-09-26-full-panel/064/README.md`). The searched stack ceiling's mean
  here is 0.655, on different seeds. So on fast it is about level with the tuned sliding forms,
  not ahead of them. Slow LoCo and CoactDetect ship sliding and searched (2026-09-21, before
  ADR-0008's floor and the realistic spacing); combined ships a sliding search pick (2026-09-23).
- ⚠ **The 0.5 s window is a rediscovery.** count (sliding) was searched on this bench on
  2026-09-26 (`<darkroom>/bugarach/2026-09-26-full-panel/064/count/README.md`): on fast the best
  setting was a 0.5 s window with 2 ROIs above the floor, +0.020 F1 over CoactDetect's proposal
  and refused for its precision difference between backgrounds (0.146 against a limit of 0.10).
  Slow did not move and combined chose 1 s. None was adopted, so count (sliding) ships untuned.
  This search did not vary the ROIs above the floor.
- **The rebuild cost adds 0.008 F1 on fast, nothing on slow and 0.001 on combined.** A threshold
  of 0 switches the cost off and leaves the sliding count at that window against the floor. On
  slow the search picked exactly that.
- **The gain over shipped count (sliding) comes from the window.** With the cost off, a 0.5 s
  window scores 0.670 on the fast busy background against 0.561 at the shipped 2 s, and makes no
  call on recordings with nothing planted (0.61 per hour at 2 s).
- ⚠ **That is a finding about count (sliding), and it needs its own check.** The floor is counted
  in a 2 s window (ADR-0008) and is here applied to a 0.5 s one, which asks for more than the
  floor was set to mean. `bench.FLOOR_AT_WINDOW_ENV` exists to study that and was off. The
  repository's own search of count (sliding) is the place to confirm it.
- ⚠ **The period is unbracketed on fast and combined:** the pick is 480 s, the longest tried. It
  only matters through the cost, which adds little.
- The merge gap and window are bracketed. The grid edges of the first search (period 240 s, gap
  0.5 s) were extended once.

Numbers: [`search_summary.json`](search_summary.json). 672 recordings, 394 s on one laptop.

## The first run: the threshold alone

![Figure 2](explainer_stack-ceiling-bench_20261008.png)

**Figure 2. The stack ceiling's call rule on the three benches, by threshold, at borrowed
settings.** The window (2 s), merge gap (3 s) and period (120 s) are held. Columns are the
fast, slow and combined streams. Top row: F1 (the harmonic mean of recall and precision), averaged
over the quiet and busy backgrounds. Middle row: calls per hour on recordings with nothing
planted. Bottom row: calls per minute inside a stretch where every ROI's rate is raised. Black
curve: the stack ceiling at each threshold. Horizontal lines: CoactDetect (blue), LoCo (purple),
count (sliding) (grey) and stack (global) (orange) at their shipped operating points. Dotted red:
count (sliding)'s limit. Dashed grey: the threshold picked on the other half of the seeds.
Everything drawn is from the odd seeds.

**At the borrowed settings the rule is count (sliding) with fewer calls in a raised-rate
stretch.** This run is what the search above corrects: only the threshold was free.

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

What Figure 2, the threshold sweep, and the table show:

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
- The search is a grid, picked once: no second seed split, and the period's best value is past
  the longest tried.
- The 0.5 s window has not been tried on count (sliding) through the repository's own search,
  nor with the floor counted in the rule's own window.
- ⚠ The cost saturates near a quarter of the period (30 s at 120 s) for a tower holding most of
  the period's ROIs, so it cannot rank large events against each other.
- Neither the page nor this record was put through the murderboard.

Code: `src/bugarach/detectors/stack_ceiling.py`, `tests/test_stack_ceiling.py`,
`tools/make_stack_ceiling_demo.py`, `tools/measure_stack_ceiling.py`,
`tools/search_stack_ceiling.py`.
