---
status: open
filed: 2026-09-07
---

# Four of the six detectors change their calls when the recording is shifted by a fraction of a bin

Tony, 2026-09-07, after turbo's marks flickered with the bin width and the window was
made to slide (#489): *"I suspect several of the detectors suffer this defect. Shifting
the data by a time step will change calls."*

Measured the same day, not argued. `tools/probe_shift_invariance.py` runs each detector
at its shipped operating point on a real baseline recording, then on the same recording
with every onset moved by d for d = 0.1 … 0.9 s, undoes the shift on the calls, and asks
what fraction of the unshifted calls are still there. A detector with no grid returns the
same calls; one that bins returns different ones, and how different says how much of what
it reports is the grid rather than the data.

## The measurement

Three TTX baselines from `2026-09-03_revised_2v_long_STEPS_EXCLUDED_TTX`
(`20240930_65`, `20240930_69`, `20241002_72`), all six detectors, nine shifts each. "Kept"
is the fraction of unshifted calls with a shifted-back call within one bin (1 s) of them
— the event-level question, since a binned detector reports its call at the bin's left
edge and a 0.05 s match would fail on the timestamp even when the same event was called.

| detector | calls at d = 0 | kept, mean over shifts | kept, worst shift | extra calls, worst shift | reads as |
|---|---|---|---|---|---|
| rate+context | 71 | 1.000 | 1.000 | 0 | shift-invariant |
| locust | 378 | 0.998 | 0.983 | 4 | nearly invariant |
| SPIKE-synch | 274 | 0.972 | 0.875 | 5 | small grid effect |
| binned SCE | 73 | 0.976 | 0.900 | 3 | small grid effect at its 10 s bin |
| LoCo | 84 | 0.64 | 0.67 on a recording with 36 calls | 14 | **grid-dependent** |
| CoactDetect | 89 | 0.70 | 0.47 on a recording with 51 calls | 32 | **grid-dependent, and it gets worse the further the shift** |

Per recording, per shift, for the two that matter (kept fraction at d = 0.1 … 0.9 s):

```
loco    20240930_65  n=47   0.91 0.81 0.79 0.81 0.83 0.79 0.81 0.87 0.94
loco    20240930_69  n=36   0.81 0.81 0.67 0.78 0.72 0.69 0.69 0.81 0.83
coact   20240930_65  n=51   0.90 0.90 0.80 0.73 0.67 0.63 0.63 0.55 0.47
coact   20240930_69  n=36   0.81 0.81 0.69 0.64 0.58 0.61 0.53 0.50 0.50
```

LoCo's curve is symmetric about 0.5 s, which is a 1 s grid doing what a grid does: the
worst case is a half-bin shift and a full-bin shift is a return to the start. CoactDetect's
curve is not symmetric — it falls monotonically to 0.47 at 0.9 s — so its calls are not only
moving with the bin edges. CoactDetect thresholds against a circular-shift surrogate null
drawn from a fixed seed; moving the data under fixed surrogate offsets changes the null as
well as the count, and both contribute. Which is which was not separated here.

The grids, from `bench.OPERATING_POINTS`: LoCo bins at 1 s; CoactDetect integrates in a 2 s
window on a 1 s step; SCE bins at 10 s; SPIKE-synch bins its profile at a detection `dt`;
rate+context runs on the generator's 0.1 s grid with a 1 s rate window and is invariant
because its windows are much wider than its step; locust gathers onsets by
`active_duration_sec` rather than a fixed grid.

## Why it matters

A call that appears or disappears when the recording is translated by 0.3 s is a call
about the bin edges, not about the cells. On the bench this is noise that the seed axis
averages over — every planted event lands at a random phase relative to the grid — so F1
does not see it, exactly as it did not see turbo's flicker. On a real recording it means
the reported event list is one of several the same data could have produced, and two
detectors disagreeing about a moment may be disagreeing about their grids.

It is also the difference between the two halves of the tolerance story. The scoring
tolerance was widened to 2.5 s (2026-08-28) because coarse detectors report a bin's left
edge; that repaired the *scoring* of a grid-dependent call and left the call itself alone.

## What to do, in order

1. **Make the probe part of the bench's report.** Run it over the bench's own regimes at
   twelve seeds and publish a "kept at the worst shift" column beside F1, the way the
   tolerance and background curves sit beside it. A detector's score should carry its
   grid dependence the way it now carries its tolerance.
2. **LoCo and CoactDetect: count in a moving window.** `turboMarks` in the viewer
   (#489) is the reference: per-ROI merged start-intervals and one sweep, O(n log n),
   no step. For CoactDetect the surrogates go through the same sweep so the null stays
   rate-matched under the same rule — measured on 38 TTX baselines at 1000 surrogates,
   that costs the assessor 3 % (47.1 s → 48.4 s), because nine tenths of its time is the
   participant gather, not the count. **The binned rule is the MATLAB port's**, so this is
   a recorded fork with a parity fixture behind it (`docs/forks.md`), not a knob.
3. **SCE and SPIKE-synch**: a 3–10 % effect, real, and second in line. SCE's 10 s bin is
   the reason its calls are 10 s wide; a moving window there changes what an SCE *is*.
4. **Do not touch rate+context or locust** for this; they pass.

Not done here because it changes what four detectors report and every number quoted
about them, and that is a campaign, not a fix. The probe is the first step and it is
in the tree.
