---
status: open
filed: 2026-09-17
---

# The bench draws event times continuously; real onsets sit on the imaging grid

Found while inventorying every parameter for goal 1 step 3, as the explanation for a parameter that
appeared to do nothing.

## What was measured

SPIKE-synch's `synchrony_statistic` ("max" or "mean") changed **nothing** on bench recordings — the
call lists were identical at every profile bin width tried (0.05, 0.1, 0.5 and 2.0 s). Reading
`binned_synchrony` says why: the statistic aggregates ROIs whose events carry the **same exact
timestamp**, and

- the generator draws event times from a continuous distribution, so two ROIs essentially never
  share one;
- real onsets are `t50rise` values quantized to the imaging frame interval — 0.1 s in this lab's
  recordings — so exact ties are **common**.

So the parameter is inert on simulated recordings by construction and live on real ones.

## Why it matters beyond that parameter

**Anything whose behaviour depends on ties or on where a value falls relative to a grid is being
tuned against a smoother world than it will meet.** The bench is where every operating point is
chosen (`bench.OPERATING_POINTS`), and this project has already paid once for a difference between
where a detector's arithmetic lands and where the data land: `docs/forks.md` §14, the calls that
moved with the bin grid.

Candidates for the same class of blindness, none of them checked yet:

- tie-breaking anywhere a detector sorts or groups event times;
- bin-edge behaviour, since a quantized onset can sit exactly on an edge where a continuous one
  almost never does;
- any detector whose count depends on distinct timestamps rather than distinct events.

## What it does NOT mean

It does not mean the bench's numbers are wrong. Every F1 measured on it is a real measurement of a
detector against planted truth. It means the bench cannot see one class of behaviour, and a
parameter that only bites on that class will look inert here and will not be tunable here.

## What to do about it

Unsettled, and worth a decision rather than a quick fix:

1. **Quantize the generator's event times to a frame interval** (the recordings' own `dt`), which
   makes the bench match the data and changes every seed's output — the same kind of move as the
   2026-08-28 background change, and it would supersede numbers measured before it.
2. **Leave it and say so**, recording that tie-dependent and edge-dependent settings are outside
   what this bench can choose, and tune them on real recordings instead, where there is no answer
   key.
3. **Quantize only for the affected detector's fixtures**, which keeps existing numbers but leaves
   two worlds in one bench.

Goal 1 step 3 takes the second course for now — `synchrony_statistic` is recorded as unsearchable on
this bench, with this file as the reason — because changing the generator mid-search would invalidate
the search that is running.
