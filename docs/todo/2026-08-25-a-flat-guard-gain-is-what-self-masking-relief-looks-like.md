---
status: open
filed: 2026-08-25
---

# A flat guard gain across the neighbour gap is what self-masking relief looks like

**This is a question about `forks.md` §4a's conclusion, raised by a review of something else.
It is not an edit, and §4a should not be changed on the strength of it without a measurement.**
§4a has already been corrected twice and its current form is the careful one; this is the
objection that survived a murderboard, recorded so it can be settled rather than rediscovered.

## The conclusion at issue

§4a concludes the guard interval is **not doing guard-cell work** — that it is "a threshold
knob that happens to be spelled in seconds". The evidence is that its recall gain is **flat
across the neighbour gap**: CoactDetect at a 5 s guard gains +0.045 where a neighbour sits
within 15–30 s, and +0.046 where the nearest is beyond 60 s. Where there is nothing to unmask,
it helps just as much.

## The objection

**Guard cells relieve two maskings, and §5.1 of `detector_history.md` names both:**

- **self-masking** — the event's own energy sits in the reference that judges it;
- **mutual masking** — a *neighbouring* event sits in the reference too.

A gap-stratified test measures the second. **Self-masking relief is gap-independent by
construction** — every event self-masks, whether or not it has a neighbour. So a gain that is
flat across the gap is the signature of guard-cell work with **no mutual-masking component**,
which is not the same thing as no guard-cell work at all.

The same objection reaches §4a's second leg. The sparse bench is described as the place "where
the effect can only be an artifact" because a second planted event can never enter the context
— but §5.1 says in terms that *"the test bin's own events sit in the null pool that judges
them"*. Self-masking is present on the sparse bench. A guard raising recall there is what the
mechanism predicts, not evidence against it.

## Two more things in §4a's own table that bear on it

- **It is non-monotonic, and the middle cell is never discussed.** CoactDetect reads 0.711 at a
  15–30 s gap, **0.882** at 30–60 s, and 0.855 with no neighbour at all. A neighbour at 30–60 s
  leaves recall *better* than no neighbour does. Under a pure crowding story that cannot happen,
  so either the strata differ in something besides the gap, or the effect is inside the noise —
  and if it is inside the noise, the ±0.001 flatness claim goes with it.
- **The seed count moved the sign once already.** §4a's first version, on 4 seeds, reported
  "−0.021 to +0.021 with no direction". At 8 seeds it is a consistent positive. A measurement
  whose sign depends on 4 versus 8 seeds needs its spread published beside it before three
  decimals are quoted from it.

## The better structural argument, which nobody has used

If the conclusion survives, there is a sharper reason for it than pool shrinkage — and unlike
pool shrinkage it applies to LoCo specifically and is checkable from the source:

**LoCo's guard excises around the *anchor*, not around the bin under test.** Thresholds are
computed at anchors every `thr_step_sec` (15 s FAST, 30 s SLOW) and each bin takes its nearest
anchor's value. At the 5 s guard §4a measured, the excised band is ±2.5 s of the anchor, so most
bins in a 15 s step keep their own events in the reference entirely. LoCo's guard cannot relieve
self-masking for the bins it does not cover — which would also explain the thing §4a finds
strangest, that LoCo's gain is *worse* than flat (+0.014 crowded against +0.025 isolated).

## And the mechanism §4a states does not fit one of its two detectors

§4a explains the gain as *"a fixed 99.9th percentile of a smaller sample underestimates the
tail"*. That is LoCo's estimator. **CoactDetect has no percentile**: its bar is a Gaussian tail
on the mean and sd of `n_surrogates` counts, and `n_surrogates` is unchanged by a guard — only
the span the events are drawn from changes. Whatever moves CoactDetect's +0.045, it is not a
shrinking sample. §4a applies one mechanism to two estimators.

## What would settle it

A guard sweep scored on **isolated events only**, against a no-guard control, with the seed
spread published. If the gain persists on events that have no neighbour and cannot be mutually
masked, the remaining candidates are self-masking relief and a lowered bar — and those separate
cleanly by looking at the threshold itself rather than at recall: a lowered bar moves the
threshold on *every* anchor, including anchors with no event anywhere near them. §4a already
did a version of this ("over 891 candidate bins the mean null falls 3.689 → 3.645") for a
different claim; the same instrument answers this one.

Run record: [`loco_coact_as_cfar_2026-08-25`](../reviews/loco_coact_as_cfar_2026-08-25.md) §E2.
