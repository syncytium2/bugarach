---
status: open
filed: 2026-09-08
---

# binned SCE's calls on this cohort are close to random placement, and two measures say so

> **Not murderboarded** — working material for sessions in this tree. **If any of it
> reaches an outside reader, murderboard that artifact first.** No number derived from a
> real recording is in this file; they are in the darkroom.

Found while assembling `tools/make_detector_table.py` for the pilot APV+CNQX+GZ cohort,
not looked for. Two independent measures land on the same detector.

**Against planted truth**, on simulated recordings from this cohort's own spec, `sce` is
last of the six by a distance: F1 **0.400** where the next-worst is SPIKE-synch at 0.599
and the best three sit at 0.76–0.79. It covers **7 of 12** distractors where four of the
six cover 11 or 12, and it fires **5.9 times per minute** into the promiscuity probe
against a gate of 9.

**On the real recordings**, where there is no ground truth, **57 % of its calls have at
most one ROI with an onset within ±0.25 s of the call's own span**. That number alone
would mean little — a detector's lone fraction is set by the width it declares — so each
call was matched against windows of its own width thrown at random times in its own
recording. That chance rate is **90 %**, so SCE sits at **0.64× chance**. Every other
hand-written detector is at 0.00–0.13, and the two learned baselines that are known to be
degenerate sit at 0.73–0.75. **SCE is in their band, not in the working one.**

Its offsets say the same thing from a third angle: the median gap from an SCE call's span
to the nearest event of any ROI is 0.3 s, **44 % of its calls have no event within 1 s and
19 % none within 5 s**. No other detector in either family has a nonzero median gap.

## What this is not

- **Not the binning artefact on its own.** SCE bins at 10 s and reports the tightness of
  its participants as the width, so a call can miss events sitting elsewhere in its own
  bin. Widening the tolerance to ±6 s — over half a bin either side — takes the lone
  fraction from 57 % to 14 %, so most of it is convention. **The residual is not.**
- **Not a claim about the SCE algorithm.** This is the *binned* port at the *shipped*
  operating point (`threshold_pctile` 99), on one cohort of six recordings, and the
  bake-off calibrated it to 75–80 on every fold — a distance of twenty percentile points
  from what shipped. Whether a calibrated SCE behaves this way is unmeasured, and the
  bake-off half above says it might not.
- **Not evidence about the preparation.** FOUNDATIONS §9: nobody has reviewed this folder,
  so a detector's calls here are not comparable to a truth that does not exist.

## What would settle it

Run `bugarach detect` on this folder with SCE at its calibrated percentile rather than its
shipped one, and re-run `tools/make_detector_table.py`. If the ratio to chance falls into
the other detectors' band, this is an operating-point problem and belongs with
[the settings that do not reach `detect`](../handoffs/2026-09-07-the-pilot-cohort-through-the-whole-loop.md).
If it does not, the port needs looking at.

Reproduce both halves:

```
python tools/make_detector_table.py --run <run> --folder <run>/data/<export folder>
```
