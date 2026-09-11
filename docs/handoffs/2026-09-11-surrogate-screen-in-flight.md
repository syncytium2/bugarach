# Handoff — the surrogate screen is running; here is how to finish it if this session cannot

> **In flight, 2026-09-11.** Not murderboarded — working material for sessions in this tree.
> Delete this file (and its pointer in the root `HANDOFF.md`) once the run's report has been
> murderboarded and PR #530 lands.

## What is running

The measurement run of [the surrogate-screen plan](../proposals/2026-09-10-surrogate-evaluation-overnight.md),
on Tony's go: every candidate measured on the `steps_excluded` and `cossart` folders, **no shortlist**.
It is a Claude Code Workflow — run ID `wf_67d9ec7c-4e6` — **bound to the session that launched it**:
its completion notice goes there, and it can be resumed only from there. Hard stop **15:00 EDT**.

## What is done

- **The plan** landed as #529, carrying the darkroom claim on `docs/SESSIONS.md`.
- **The build** is committed on branch `surrogate-screen-overnight`: commit `47e278e`, **draft PR #530**. Its
  full suite gave 3,018 passed, 33 skipped, 1 xfailed. The pattern-jitter clean room gave 473 passed:
  the differential fuzz agrees exactly and all 16 mutants are caught.
- **The run folder** `<darkroom>/bugarach/2026-09-11-surrogate-screen/` holds `reproduction/` (finished) and
  `_cost_probe/`, plus partial `steps_excluded/`, `cossart/` and `discriminator/`.
- The first run agent died at about 08:00 on a network drop. The workflow was **resumed at about
  08:15**, with the run step told to keep finished cells and redo only those with stale `.progress`
  markers.

## If the launching session dies before the run finishes

A new session cannot resume the Workflow. Finish by hand, in the worktree `surrogate-screen-overnight`,
with its venv `../bugarach-worktrees/surrogate-screen-overnight-venv`:

1. A cell is finished if its result `.json` has no `.progress` sibling. Redo the rest with
   `tools/build_surrogate_screen.py`, per the plan's grid. JointISI at *J* = 1 frame on sparse ROIs
   costs about 14 s per draw, so cap it and record what you drop as intractable.
2. Write the reports per the plan's section "The report": no shortlist, inline SVG, and the render
   gate run from stamped copies in the run folder's `tools/`.

## Owed after the run, whoever finishes it

- **CI must install the `surrogates` extra** (`.github/workflows/ci.yml`: `.[ui,dl,surrogates]`).
  Without it, all 98 surrogate tests skip in CI.
- **Add a sixth defect to [the Elephant todo](../todo/2026-09-11-elephant-surrogate-defects-are-not-filed-upstream.md)**:
  in ISI-dither mode without the square root, JointISI writes its smoothed histogram into an integer
  array, so sparse regions round to zero and fall back to uniform dither. The adapter works around it.
- **A known departure from the plan**: the interval-jitter bin is rounded to whole frames, so at
  *J* = 1 frame interval jitter moves nothing. The movement statistic shows it.
- **Murderboard the report**, then land #530. Release the darkroom claim once that is done.
- **The verdict-rule design session** takes its agenda from
  [the review record](../reviews/2026-09-10-surrogate-evaluation-overnight_2026-09-10.md).
