---
status: open
filed: 2026-08-27
---

# The sweep turns one knob per detector, and the page already tells you when that is the wrong knob

> Found while giving the Tune panel a range control. Tony, on being shown that a
> sweep varies exactly one setting: *"each tool has only one parameter for
> simplicity?"* — the answer is yes, deliberately, and this is what it costs.

The range boxes fix the refusal that says **"widen the range"**. They do nothing
for the other one, which the page has been printing since the SPIKE-synch
degeneracy was found:

> Every setting on this sweep scores the same F1, so the knob being swept is not
> what decides the answer here. Widening the range will not help — **sweep the
> parameter that is binding, or sweep them together.**

Neither of those moves exists. `DETECTORS[k].knob` is a single key, `sweepPoint`
sets that one key on top of whatever the Detect panel holds, and the reader who
has just been told to sweep a different parameter can only go and type numbers
into Detect by hand, one at a time, with no scoring in between. That is the same
shape of dead end the missing range control was, one step further in.

## What each detector holds still, and what it would mean to move it

| detector | swept | held at whatever Detect has |
|---|---|---|
| RateDetect | excess threshold (Hz) | rate window, context window |
| SCE | threshold percentile | bin width, surrogates |
| CoactDetect | alpha | bin, context, surrogates |
| LoCo | threshold percentile | bin, context, surrogates |
| locust | SCE percentile | surrogates, synchronous frames, min distance, active duration |
| SPIKE-synch | C threshold | (its own) |

The held settings are not incidental. **The bin width is the one to look at
first**: `docs/learned/tolerance_sweep.png` already shows binned SCE still
climbing at 3 s because 10 s bins put a floor under its timing, and a threshold
percentile swept on top of a bin that wide is a knob turning inside a decision
that was already made.

## Why this is not simply "add a second knob"

Three things get harder at once, and the panel's existing promises are what make
them hard:

1. **In-sample cost.** One knob over 6 settings is 6 fits; two knobs over 6 is
   36, and locust costs ~7 s a fit. The tick list exists because two detectors
   are 97% of a six-detector sweep's wall clock; a product grid multiplies the
   thing that was already the problem.
2. **`pickOperatingPoint` is one-dimensional.** "The optimum is at the end of the
   grid" and "a plateau with neighbours on both sides bracketed it" are both
   statements about a line. On a surface, "edge" means a border, and the refusal
   that keeps a boundary value from being published has to be re-derived — this
   is the check that exists because a boundary value once WAS published upstream.
   Its Python twin `bench.pick_operating_point` would need the same treatment.
3. **The held-out claim.** Each fold currently chooses one knob on the folds it
   may see. Choosing a pair the same way is fine; reporting it is where it gets
   delicate, because a two-parameter fit on the same number of recordings is a
   weaker claim at the same F1 and the panel currently has no way to say so.

## Smaller moves that are worth considering first

- **Let the knob be chosen, not just its range.** A select per detector — "sweep
  which setting?" — over the keys in its `params` map, one at a time. That
  answers "sweep the parameter that is binding" exactly, costs nothing extra per
  run, and needs no change to `pickOperatingPoint`. It is probably the whole fix.
- **Say which parameter to try next when a sweep goes degenerate.** The message
  currently sends the reader to "the Detect section"; it could name the setting
  most likely to be binding for that detector.
- Leave the product grid alone until somebody has actually wanted it.

## Where to look

- The registry rows and their `knob`/`params`, and `sweepPoint`, in
  `docs/site/raster_viewer.html`.
- `pickOperatingPoint` in the same file, and `bench.pick_operating_point` /
  `bench.DegenerateSweep` in `src/bugarach/bench.py`.
- The range control this was found beside — `sweepGrid`, `makeGrid`,
  `extendPlan`, and `tests/test_webapp_sweep_range.py`.
