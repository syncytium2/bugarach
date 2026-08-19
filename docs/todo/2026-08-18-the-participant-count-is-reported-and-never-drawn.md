---
status: open
filed: 2026-08-18
---

# Five detectors report how many ROIs were in an event, and no figure shows it

Making the raster uniform removed a **wrong** answer to a real question. The old
figure inked the onsets falling inside a detected window, which looked like the
detector naming its participants and was in fact this figure's own rule applied
to the detector's window. That had to go.

What did not happen is the other half. **Five of the six return a participant
quantity** and the diagnostic now draws it nowhere:

| detector | field | what it is |
|---|---|---|
| CoactDetect | `nrois` | distinct ROIs in the bin |
| SPIKE-synch | `n_participating_rois` | ROIs in the synchrony event |
| LoCo | `mag_total` | coactivity summed over the event |
| binned SCE | `mag_total` | same |
| CICADA | `mag_total` | same |
| rate+context | — | reports no participation quantity at all |

Three of them (CICADA, binned SCE, LoCo) build the participating **set**
internally and return only its size. None returns the list, which is exactly why
per-onset shading was never theirs to draw — but the *count* is theirs, it is
already computed, and a reader of the diagnostic cannot see whether a call
gathered four ROIs or forty.

## What to build

Encode it on the lane bar, where the claim belongs: bar height, or alpha, or a
hover field — the published diagnostic is interactive, so hover costs nothing in
ink. Then say so in the legend. That turns this change from a subtraction into a
correction: the per-onset claim goes away and the per-event claim the detectors
actually make appears.

**The obstacle is plumbing, not design.** `ui.app._compute` hands each detector's
result on as `(t, y, (onsets, widths), extra)` — the participant field is dropped
at that boundary, so the lanes never see it. Widening that tuple touches the
viewer as well as the figure, which is why it was not folded into the raster
change.

## The same gap, seen from the generator figures

`generator_participation.png` is where a reader feels it. The sweep runs
participation from 0.45 down to 0.10 and the columns under each ▲ fade out, which
is the knob — qualitatively. What a reader cannot do any more is *count*: fifteen
ROIs against three. The old ink could not be counted either, and it was drawn
from the answer key, so nothing was lost that was ever trustworthy. But the
restoration is the same one: a thin coactivity lane under each raster — distinct
ROIs firing per bin, which is CoactDetect's own statistic and which
`trace_panel` already draws — would step from ~15 to ~3 at the planted times. It
is derived from the data, not from `gt`, so it does not smuggle the answer back
in.

## Why it is filed rather than fixed

Tony's instruction was to stop bolding raster events and carry detections in the
markers at the top. This is the adjacent improvement the murderboard's role 4
called for under *relocate, don't delete*, and it is a genuinely different piece
of work — a new encoding, a widened internal contract, and a legend entry.
