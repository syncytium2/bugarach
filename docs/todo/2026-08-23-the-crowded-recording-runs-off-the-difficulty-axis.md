---
status: open
filed: 2026-08-23
---

# The crowded recording runs off the difficulty axis, and two thirds of its finding is that

`CROWDED_RECORDING` was added so the bench could exhibit reference-window
contamination, which `BENCH_RECORDING` makes impossible by construction. It
changes two things at once, and only one of them was intended.

**`BENCH_RECORDING` carries no `bg_rate_hz`.** The background rate always arrives
from `REGIMES[regime]`, which `make_recording` merges in at call time:

```python
def make_recording(regime, seed, **overrides):
    return simulate_coordination(seed=seed,
                                 **{**BENCH_RECORDING, **REGIMES[regime], **overrides})
```

`make_crowded_recording` has no `regime` argument and merges no regime:

```python
def make_crowded_recording(seed, **overrides):
    return simulate_coordination(seed=seed, **{**CROWDED_RECORDING, **overrides})
```

So `bg_rate_hz` falls through to `simulate_coordination`'s own default of
**0.05 Hz** — which is the pre-2026-08-13 *invented* value that
`BENCH_RECORDING`'s docstring names in its own correction table as **"5× too
busy"**. `REGIMES` spans 0.0052 to 0.0190 Hz, the interquartile range of per-ROI
rate across baseline windows. The crowded recording sits at roughly **10× the
quiet endpoint and 2.6× the busy one** — off the measured axis in a direction the
project already discarded once.

Realised per-ROI rate, planted events included: **0.0590 Hz** against the bench's
**0.0129**.

## What it cost

`docs/forks.md` §4a read the consequence as a property of crowding, flagged it as
the larger finding in its own table, and made it the standing open item:

> Both detectors lose most of their recall on the crowded recording — 0.70–0.83
> down to 0.25–0.29 — and a guard recovers a slice, not the bulk.

Separated (`tools/probe_crowded_background.py`, 4 seeds, shipped operating
points), the split is roughly two to one the other way:

| CoactDetect | bg Hz/ROI | recall | 0.30 | 0.18 | 0.10 |
|---|---|---|---|---|---|
| bench, quiet | 0.0129 | 0.833 | 1.00 | 1.00 | 0.50 |
| crowded, at quiet | 0.0137 | 0.652 | 0.98 | 0.82 | 0.15 |
| crowded, as shipped | 0.0590 | 0.254 | 0.64 | 0.11 | 0.01 |

Crowding costs **0.181** of coact's recall and **0.142** of LoCo's; the unintended
background costs **0.398** and **0.289**.

The docstring is explicit that the probe and the distractors are off *"because a
dense-but-random block would confound it with rate-keying"* — the author saw the
confound coming and closed the doors they knew about. It arrived through a
keyword default instead.

The other two candidates §4a named are both cleared by the same run, which is
worth keeping so nobody re-opens them: an oracle emitting the exact planted times
scores **F1 1.000** on the crowded recording, and across every condition **zero**
emitted spans cover two planted events, so neither the scorer's one-to-one
matching nor episode merging contributes anything. Detection spans are 2.0 s
(coact) and 0.70 s (loco) against a 19.4 s median gap.

## What to do

1. **Give the crowded recording a regime**, the way `make_recording` has one —
   `make_crowded_recording(regime, seed, **overrides)`, same signature, same
   merge order. A default of `"baseline_quiet"` keeps the call sites short and
   puts the recording back on the axis. This is the fix; the rest follows from it.
2. **Assert the background in `tests/test_bench.py`.** The existing crowding
   tests pin the spacing, the absent hot window and the zero distractors — every
   knob the author set deliberately — and none of them pins the one that came
   from a default. A test that the realised rate sits inside `REGIMES`' span
   would have caught this and would catch the next one.
3. **Re-measure §4a's guard table on the axis.** The direction survives and gets
   *stronger*: at the quiet endpoint a 10 s guard takes coact 0.652 → **0.696**
   against §4a's +0.047, and the gain lands at **0.18 participation — the
   measured real value** — where recall goes 0.82 → **0.89**. LoCo stays flat
   either way, as §4a's geometry argument predicts. The aggregate F1 hid both
   halves of that.
4. **Then re-ask the open question.** Crowding still costs 0.14–0.18 of recall
   with the background held right, concentrated in the realistically-sized
   events, and a 10 s guard recovers about a quarter of it on coact and none on
   LoCo. That residual is the real version of the standing item — and per
   `detector_history.md` §5.4 and §6.4 the instrument for a *multiple-target*
   environment is **censoring inside the estimator**, not a wider guard. A guard
   excises a span adjacent to the anchor; at a 19.4 s median gap the interference
   is spread across the whole ±30 s reference, which is the case censoring is for
   and guards are not.

## Why this is not a one-line fix landed quietly

Changing the recording changes every number in `docs/forks.md` §4a, which is a
recorded measurement other work is reasoning from. Fix, re-measure and correct
the section in one pass — §4b records the separation in the meantime so nothing
is read at face value while it waits.
