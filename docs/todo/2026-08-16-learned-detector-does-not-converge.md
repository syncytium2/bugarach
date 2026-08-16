---
status: open
filed: 2026-08-16
---

# The learned detector does not converge yet — what is ruled out, and what is not

Step 3 of the plan Tony approved (port the assessor → parameterize the generator →
train a tiny model → sweep mass). Steps 1 and 2 landed in PR #52. **This step does
not work**, and the point of this file is that the next session should not
re-derive the four things already ruled out.

## Where it stands, measured

Bench, `baseline_busy`, seeds 1–3, against planted truth:

| model | params | train | F1 | recall | precision | detections |
|---|---|---|---|---|---|---|
| `tiny` | 2 393 | 238 s | 0.12 | 0.07 | 1.00 | 3 |
| `trace` | 2 065 | 8 s | 0.15 | 0.09 | 0.50 | 8 |

The six, on the same recordings: **CoactDetect 0.66**, LoCo 0.64, RateDetect 0.63,
CICADA 0.54, spike-sync 0.54, SCE 0.42. So a learned detector is currently far
worse than every hand-written one, and nothing about this should be reported
otherwise.

## Ruled out — do not spend time here again

1. **Not a structural bug.** On a single crop containing an event the model
   reaches p = 0.75 at event frames and loss falls 1.40 → 0.68 in 150 steps. It
   can fit; it does not converge on the full task.
2. **Not the ROI-order encoding.** The canonicalisation bug that was there —
   ties broken by original index — is fixed and tested: permuting ROIs now encodes
   bit-identically.
3. **Not (only) signal starvation.** Positives are **0.5%** of frames (135 of
   26 922). Event-balanced crop sampling is implemented — half the crops drawn
   around an event, half uniform — and it changed the failure's shape but not its
   outcome.
4. **Not the two architectures being secretly identical.** An earlier run had
   `tiny` and `trace` producing byte-identical losses, which was degenerate. They
   now differ (3 vs 8 detections, thresholds 0.05 vs 0.35).

## The symptom, precisely

Loss oscillates between roughly 0.8 and 1.9 across 900 steps with no downward
trend, while a single crop trains fine. That pattern is batch-to-batch variance
dominating the gradient, not an inability to represent the target.

## Ranked suspects, cheapest first

1. **`pos_weight` is ~200.** At 0.5% positives, BCE's positive term is scaled by
   two orders of magnitude, so a batch's loss is decided by how many event frames
   its three crops happened to contain. Try capping it near 20, or focal loss.
   This is the single most likely cause and the cheapest test.
2. **Batch of 3 is too small** for a target this sparse. Larger batches, or
   gradient accumulation, directly attack the variance above.
3. **The label is very thin.** `observed_span` gives a *median 0.80 s* footprint —
   about **8 frames** — against a 208-sample receptive field. ⚠ **Widen only the
   training target, never `frame_targets`' contract.** Tony was explicit that the
   definition of an event comes from the plants; a tolerance band used for the
   loss is a different object from the label, and if one is added it must be said
   out loud and kept out of scoring.
4. **It may simply need more steps than a laptop budget allows.** If so that is a
   **finding about the target**, not a knob — "lightweight, easily trained on user
   data simulations" would be in tension with this task at this event rate, and
   that is worth knowing early.

## One diagnostic worth running first

Train on the **old invented generator settings** (`bg_rate_hz=0.05`,
`jitter_sec=0.05`, participation 50–100%), where every detector scored F1 0.9–1.0.
If the model learns there and not on the measured settings, the pipeline is sound
and the measured regime is simply hard — which is a result. If it fails there
too, the problem is in the training loop and none of the suspects above matter yet.

## Constraints that are settled — do not relitigate

- **Frames, not seconds, inside the model.** dt is the loader's problem
  (FOUNDATIONS §6, PR #48).
- **The smear is learned, not assumed.** No fixed scale bank; the ~4-sample width
  is a test point.
- **Event definition comes from the plants** — `observed_span` (PR #46).
- **Rows sorted by firing frequency**, canonical and tested.
- **One ROI, one vote** — bounded activation before pooling. The bound is *soft*
  and that trade has not been probed behaviourally.
- **Modular** — a new architecture is one class plus one `@register` line.

## Step 4 is blocked on this, deliberately

The mass sweep (`n_rate_quantiles` from 1 to 32, with `trace` as the
distinctness-free control) measures nothing while every model scores ~0.12. Do not
run it until step 3 beats a trivial baseline.
