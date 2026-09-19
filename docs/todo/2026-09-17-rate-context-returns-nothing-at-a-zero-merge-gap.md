---
status: open
filed: 2026-09-17
---

# rate+context returns NO calls at a merge gap of zero, where it should return the most

Found while inventorying every parameter for goal 1 step 3 — the first time anything had varied
`merge_gap_s`, which has sat at its function default since the port.

## What was measured

`bench.run_detector("rate", …)` at the shipped operating point on one quiet bench recording,
varying only `merge_gap_s`:

| `merge_gap_s` | calls |
|---|---|
| 0.0 | **0** |
| 0.001 | **0** |
| 0.1 | 51 |
| 0.5 | 21 |
| 1.0 | 21 |
| 3.0 (shipped) | 20 |

Merging fewer calls together should yield **more** calls, not none. The series behaves from 0.1 s
upward; at and near zero the detector returns an empty list.

## Why it matters beyond the number

- **A setting nobody varies can be broken for a long time without anyone noticing.** This one has
  never been searched; it was found by a probe asking only whether each parameter can move the
  answer at all.
- **It is a shipped detector**, and zero is the value a reader would reach for to mean *do not
  merge*. Someone comparing detectors "without merging" would get an empty result and might read it
  as *this detector finds nothing*.
- Goal 1 step 3 searches this axis. Until this is understood, a grid that includes 0.0 s would hand
  the search a value that scores F1 zero for a reason that is probably arithmetic rather than
  detection. **The step 3 grid therefore starts at 0.1 s**, and this file is why.

## What has NOT been done

Nobody has read the merging code to find the cause; this is a measurement, not a diagnosis. The
likely shapes are a `<=` where a `<` belongs, a zero-width interval collapsing, or a division that
produces an empty index set — but that is a guess and should be checked rather than assumed.

Two things to establish when someone picks this up:

1. Whether the same shape exists in the other detectors' merge gaps (CoactDetect's `merge_gap_sec`
   showed **no effect** at 0.0 and 1.0 on the same probe, which is a different behaviour and may be
   a different code path).
2. Whether the MATLAB original does the same thing at zero, since the port's parity fixtures run at
   the shipped value only.
