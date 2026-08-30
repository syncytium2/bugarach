---
status: open
filed: 2026-08-30
---

# `distractor_hits` counts span coverage, not firing on a burst — and it cannot be ranked on until it doesn't

waiting: nothing. This is a measurement defect with a reproducible demonstration; the
repair is a decision about `score.py`, which is held elsewhere (see **Who owns the fix**).

> **Not murderboarded** — a finding for sessions in this tree. Every number below is read
> from the shipped `docs/learned/bakeoff.json` (`a510e694`) with no new run.
> **If any of it reaches an outside reader, murderboard that artifact first.**

Tony ruled on 2026-08-30 that `distractor_hits` gets **its own gated axis, kept out of
F1** — decision D3 of [the ranking brief](../handoffs/2026-08-30-ranking-the-detectors.md).
Building that gate meant first reading what the number is. It is not what its name says,
and the ruling cannot be implemented against it as it stands.

## The demonstration, in one row

`tiny` makes **2 detections in a whole fold**, and both of them match a planted event —
its precision that fold is **1.000**. It is scored as hitting **12 of the 12** distractors
in that fold.

| detector | detections | hits | precision | distractor hits |
|---|---|---|---|---|
| `tiny` | **2** | 2 | 1.000 | **12 / 12** |
| `trace` | 12 | 2 | 0.167 | 11 / 12 |
| `coact` | 48 | 27 | 0.587 | 12 / 12 |
| `sync` | 19 | 4 | 0.444 | 6 / 12 |

Two detections cannot land within tolerance of twelve separate times. The fold holds two
recordings of six distractors each, planted in `distractor_window` `[120, 1100]`, and the
match tolerance is seconds. One detection per recording is covering the **whole window**.

## What the code actually computes

[`score.py:244`](../../src/bugarach/score.py):

```python
distractor_hits = 0
if gt.distractors and nD:
    dt = np.array([d.time for d in gt.distractors], dtype=float)
    distractor_hits = int(np.sum(
        [np.any(_gap(t, lo, hi) <= tol_sec) for t in dt]))
```

`lo, hi` are **every** detection, and `_gap` returns `0.0` for any time falling *inside* a
span. So the quantity is **"how many distractors are covered by the union of the detection
spans"**. Three consequences, and each is enough on its own to sink a gate:

1. **It scales with span width, not with firing.** A detector emitting one span a thousand
   seconds wide covers every distractor in the window and is charged twelve hits for one
   detection. A detector emitting a hundred tight spans that each genuinely sit on a burst
   is charged at most a hundred, and probably fewer.
2. **It is a count, not a rate.** Twelve is the ceiling, and most detectors sit at 11–12,
   so the axis has almost no dynamic range at the top where the ranking needs it.
3. **It is not disjoint from correct detection.** `hot_fa` is computed from `fa_times` /
   `fa_ends` — the **unmatched** detections — twenty lines above. `distractor_hits` is
   computed from `lo` / `hi`, all of them. A detection that correctly matched a coordinated
   event is *also* charged as a distractor hit whenever a distractor lies within tolerance
   of its span. The two measures in the same function disagree about whether a correct
   detection can be a false one.

The module docstring is right that a detection on a distractor "lands in `fa_times` and
costs precision like any other". That part works. It is the *separately reported* number
that does not.

## Why this defeats the ruling rather than merely annoying it

Normalise by opportunity and every detector in the tree hits distractors **more often than
it hits real events**:

| detector | recall | distractor rate | recall − distractor rate |
|---|---|---|---|
| `tube` | 0.917 | 0.958 | −0.042 |
| `coact` | 0.767 | 0.938 | −0.171 |
| `loco` | 0.733 | 0.938 | −0.204 |
| `rate` | 0.700 | 1.000 | −0.300 |
| `trace` | 0.067 | 0.979 | −0.912 |
| `tiny` | 0.067 | 1.000 | −0.933 |

Read naively that says no detector in this project can tell a coordinated event from a
correlated burst — which would be a large finding about the instrument. It is not
supported, because the same wide spans that inflate the right-hand column are what the
left-hand column is scored on with a tolerance. **The measure cannot currently distinguish
"fires on bursts" from "fires in wide spans", and those have opposite meanings for a
ranking.**

So D3's axis is **specified and not yet armed**: `bugarach.rank` carries the gate with its
threshold set to `None`, and says why in the one place a reader will look.

## What the repair probably is

Not decided here — it changes published numbers, which is the reason it is not being done
in passing:

- **Restrict to unmatched detections**, mirroring `hot_fa`, so a correct detection is not
  charged twice. This is the inconsistency inside one function and looks like the clear
  half of the fix.
- **Report a rate, not a count** — hits per distractor planted — so the axis is comparable
  across folds and across a data set with a different `n_distractors`.
- **Decide what a wide span means.** Either charge coverage per unit time, or count each
  detection at most once, or refuse spans beyond some width at scoring time. This is the
  genuinely open half, and it is the same question `tol_sec` already raises for recall.

## Who owns the fix

Not this branch. `src/bugarach/score.py` is declared off-limits by
`tube-variants-overnight`, which is live and running fits on top of it, and changing the
number re-quotes anything already published from `bakeoff.json`. `ranking-rule` reads the
value and refuses to gate on it; whoever repairs it should re-arm the threshold in
`bugarach.rank.MAX_DISTRACTOR_RATE` and say in the commit what moved.

## See also

- [the ranking brief](../handoffs/2026-08-30-ranking-the-detectors.md) — D3, and the
  `score.py:44` note that "should a burst count?" has been live since the file was written.
- [the promiscuity probe cannot fail](2026-08-16-promiscuity-probe-cannot-fail.md) — the
  same shape one axis over: a measure that is reported but cannot change any outcome.
- [the bake-off calibrates without the gate](2026-08-28-the-bakeoff-calibrates-without-the-gate.md)
  — the third instance, and the reason `rank` gates rather than trusts.
