---
status: open
filed: 2026-08-31
---

# The gate fix: plant the probe in the browser's generator — and the Python bake-off is NOT the target

> **Not murderboarded** — written for a session in this tree, near compaction. Every number
> is reproducible from the paths given.
> **If any of it reaches an outside reader, murderboard that artifact first.**

**This is the next piece of work.** Tony, 2026-08-31: *"prepare the handoff to do the gate
fix. we're going to hold on the 24 seed run. the input data may need revision."*

## Read this first: the obvious target is the wrong one

The visible defect is in [`tools/fair_bakeoff.py:222-231`](../../tools/fair_bakeoff.py),
which picks each fold's knob by raw argmax with no probe gate. **Do not fix it.**

> Tony, 2026-08-28: *"all the bake-offs are stale. the next bakeoff will be in app. that is
> the only pipeline that matters now."*

That ruling retires the Python path, and
[the 2026-08-28 handoff](2026-08-28-the-gate-is-in-the-app-and-inert.md) §3 says so in
terms: *"Do not act on that todo's fix section. It prescribes repairing
`tools/fair_bakeoff.py` and regenerating `docs/learned/bakeoff.json`. Tony's ruling above
retires that path."* `tools/refit.py` (#378) is on the same stale side — **do not build on
it**, though it remains the worked example of catching the three refusals as *outcomes*
rather than letting the first one end the run.

**I nearly wrote this handoff prescribing exactly that repair.** The first draft laid out
how to swap the argmax for `bench.pick_operating_point`, including a policy for the raise,
and it was wrong from its premise. I caught it only by reading the tail of
`docs/handoffs/README.md` on the way past. That is the third instance in one session of a
decision existing in prose and nearly being re-derived against —
[filed](../todo/2026-08-31-a-decision-in-prose-will-be-re-derived.md).

## The actual job, in one sentence

**Plant the promiscuity probe in the browser's generator**, so the gate that already exists
in the app can fire.

Everything downstream is built and tested. `pickOperatingPoint` in
`docs/site/raster_viewer.html:3817` had **two** of the Python's three refusals; #387 added
the third — the promiscuity gate — plus the `hotFa` count it needs, and `scoring.js:186`
carries `hotFaPerMin(hotWindow)`. **All of it is inert**, because no recording the page
generates has a hot block, and a test pins that a missing probe reads *unknown* rather than
*zero*. So the alarm is wired to a sensor that is not installed.

## The trap, and it is why #387 stopped short

Planting must **exclude** the hot window, and the exclusion works by compressing the
timeline. [`src/bugarach/simulate.py:318-326`](../../src/bugarach/simulate.py):

```python
gap_lo = gap_hi = None
if exclude is not None:
    gap_lo = max(lo, exclude[0] - min_sep)
    gap_hi = min(hi, exclude[1] + min_sep)
    if gap_hi <= gap_lo:
        gap_lo = gap_hi = None
gap_width = 0.0 if gap_lo is None else (gap_hi - gap_lo)
hi = hi - gap_width                       # place on the compressed timeline
```

Events are drawn on the compressed span and the gap is added back at `:363`. **A port that
plants on the raw span puts planted events inside the block that is supposed to contain
none** — and then the probe counts them as promiscuity, which inverts the measurement it
exists to make. The failure is silent: the recording looks right and every count is
plausible.

Also carried from the same handoff: `bench.py:703` computes the per-minute probe rate
against `BENCH_RECORDING["hot_window"]` rather than the window of the recording the result
came from — correct today only because the bake-off spec happens to use the same window,
which is luck. **The browser is the reference**: its `hotFaPerMin(hotWindow)` takes the
window as an argument, and `score.py:239` reads it from `gt.params`, which is where it
lives.

## Why this is worth doing now — new evidence since that handoff

The 24-seed run (2026-08-30, `docs/learned/bakeoff_24seed.md`) shows the ungated
calibration getting **worse with more data**, which is the opposite of what anyone would
assume:

| detector | probe firings/min | ceiling | |
|---|---|---|---|
| rate+context | 3.47 at 8 seeds → **3.60** at 24 | 2.0 | over in both |
| locust (`cicada`) | 21.48 at 8 → **30.62** at 24 | 25.0 | **passed at 8, fails at 24** |

More seeds gave the search more chances to find a promiscuous setting. The shipped 8-seed
numbers therefore *hide* a ceiling breach that more data exposes. That is an argument about
the **shape** of an ungated search, and it carries to the app's campaign unchanged — the
app inherits the defect the moment its sweep runs on recordings that can actually trip the
gate.

## The policy question, which the app will hit and one sweep never did

`pickOperatingPoint` **raises** rather than taking second place — deliberately: *"silently
accepting a worse point is how a calibration stops being reproducible."* Right for one
sweep. A campaign is many detectors × many folds, and an unhandled raise means one
detector's bad fold destroys every other detector's result.

Three policies. **This must not be decided silently:**

1. **Abort the campaign.** Loudest; also makes the campaign unrunnable while any detector
   is over ceiling, which today two are.
2. **Record that fold as gate-failed, carry no operating point, continue.** ← *my
   recommendation.* It matches the shape the project already chose: the performance table
   keeps a failing detector in the table with its verdict beside it, because the table's
   job is to report. `knob_value` is already `float | None`, so "no operating point" needs
   no new type.
3. **Widen the grid and retry.** Right for a *boundary* refusal, **wrong for a promiscuity
   refusal** — there the ceiling is the point and widening just searches harder for a way
   past it. Any implementation must branch on which exception was raised.

`tools/refit.py` is the worked example of (2) in Python, and is the only reason to open it.

## What is on hold, and why it touches this

**The 24-seed bake-off is held** — Tony, 2026-08-31: *"we're going to hold on the 24 seed
run. the input data may need revision."* Do not promote it as part of this work. It came
out of the ungated calibration, and if the input data is revised it is superseded twice.

**The Cossart transfer numbers are at the wrong K** (k=3 and k=8; the decided value is
**K=12**) and its README now says so at the top. A re-run was started and is not reflected
anywhere; re-derive the spec before trusting it, because a data revision moves that too.

## Do not do these

- **Do not repair `tools/fair_bakeoff.py`** or regenerate `docs/learned/bakeoff.json`.
  Retired by ruling. The todo that prescribes it carries the ruling at its top; its fix
  section is left standing only as a record of what would have been done.
- **Do not set `MAX_PROBE_PER_MIN` for the learned models from any bake-off run.** Those
  ceilings are measured at *shipped* operating points; the learned models have none, and
  every run to date chose their knobs with the ungated argmax. Order is: gate → re-fit →
  measure → declare.
- **Do not lower a ceiling** so the current winner passes. They are measured baselines, not
  aspirations.
- **Do not touch `tests/test_background_curve.py`.** Its asserts encode a claim and were
  left red on purpose.

## How to know it worked

1. A recording generated in the browser carries a hot block, and no planted event falls
   inside it — assert that directly, because the failure is silent.
2. `hotFaPerMin` returns a number rather than `unknown` for such a recording.
3. A sweep whose F1-optimum is promiscuous does **not** adopt it, and the campaign survives
   — with the chosen policy visible in the output rather than only in a commit message.
4. The gate is **on the live site**, not just in the tree. The 2026-08-28 handoff records
   it was one serving-relevant commit behind at the time; check `tools/site_staleness.py`
   before claiming it ships.

## See also

- [the gate is in the app, and it cannot fire yet](2026-08-28-the-gate-is-in-the-app-and-inert.md)
  — **the authority for this work.** Read it before starting; this file only adds what has
  happened since.
- [the bake-off calibrates without the gate](../todo/2026-08-28-the-bakeoff-calibrates-without-the-gate.md)
  — the measurement that is the evidence, with its fix section retired.
- [the promiscuity probe cannot fail](../todo/2026-08-16-promiscuity-probe-cannot-fail.md)
  — the same shape one layer up.
