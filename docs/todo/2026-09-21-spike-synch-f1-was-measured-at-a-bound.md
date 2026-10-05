---
status: open
filed: 2026-09-21
---

# SPIKE-synch's bake-off F1 was measured at a bound, not at an operating point

> Filed on 2026-09-21 because the finding existed only in a root handoff that was being retired,
> and its own words about itself were *"Nobody has acted on that."* Retiring the file would have
> retired the finding with it. Source:
> [`docs/handoffs/2026-09-08-the-loop-closes.md`](../handoffs/2026-09-08-the-loop-closes.md),
> *Three refusals that are findings*.

## What was found

`tools/settings_from_bakeoff.py` refuses to emit a calibration for three of the six coded
detectors on the pilot cohort, and each refusal says something about the detector rather than
about the tool. Two are disagreements between folds — **CoactDetect** and **binned SCE**, where a
mean over a knob grid is not a knob anyone ran. The third is different in kind:

**For SPIKE-synch, every fold's chosen setting landed on an *end* of its grid.**

`bench.pick_operating_point` already treats that state as a search that stopped while still
climbing, and it is deliberate about the distinction: a *plateau* reaching the edge is a fine
answer (LoCo saturates at F1 1.00 from `threshold_pctile` 99.99 upward, so no widening produces an
interior peak), but when **every** optimal point sits at an end, the grid did not bracket the
optimum. `bench.EdgeOfRange` exists for exactly this and its docstring is blunt about it: *"An
optimum at the edge is not an optimum — it is the search"*.

## Why it matters, and what it is not

**It is not a claim that SPIKE-synch is better or worse than its published number.** It is that
the number is a **bound**: the best F1 found inside a grid whose edge the search never got past.
The true optimum could be beyond it, and nothing in the bake-off says by how much. A comparison
that ranks SPIKE-synch against a detector whose optimum *was* bracketed is comparing two different
kinds of quantity.

That matters more now than when it was found, because the detector field is being ranked:
`tools/leaderboard.py` derives the standing of all ten players, and the margins it reports sit at
about one draw-to-draw noise unit.

## What would close it

Widen SPIKE-synch's grid and re-run its arm of the bake-off until some optimal point is interior —
or, if widening keeps hitting an end, record *that* as the finding, because a detector whose F1
climbs monotonically to the limit of a physically sensible range is telling you something about
the knob. Either way the published figure then says which it is.

⚠ **Two things to check before starting**, both of which may have moved the numbers underneath
this: [two of four bake-off folds train the same model](2026-09-17-two-bake-off-folds-train-the-same-model.md),
which touches every published bake-off figure; and the `tau` questions Kreuz answered in April
([todo](2026-08-24-kreuz-answered-the-spike-synch-questions-in-april.md)), which bear on what
SPIKE-synch's knob means in the first place.
