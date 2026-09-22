---
status: open
filed: 2026-09-22
priority: high — it is a precondition for ruling the jitter constant (queue item 2)
---

# The jitter was not a lone bad constant: participation came out of the same call

Tony, 2026-09-22, before adopting the measured jitter: what other parameters of the data do the
simulations absorb, and were they measured carefully? This is that audit, read off the tree.

## The finding in one line

`tools/remeasure_bench.py` derives **`n_roi`, `jitter_sec` and `participation` from a single
call to `assess_coactivity` at K = 4** (its own docstring says so), and inside that call
`assess.py:586` takes the jitter and the participation out of **the same `_clusters(...)`
invocation at the same `bin_width`**, default 1.0 s. The jitter from that instrument has now
been shown to track bin ÷ √12. **Participation is the other output of the same clustering and
has never been checked against the bin.**

## What the bench absorbs, by how well it is measured

### Fitted properly, and validated against something they were not fitted on

| constant | value | why it is credible |
|---|---|---|
| `rate_shape` | 0.275 | maximum-likelihood Gamma over **81 baseline windows, 2,643 ROIs**, each window keeping its own mean. The test of it is a prediction it was not fitted to: real windows leave **35%** of ROIs with no event at a median 1.7 mHz; drawing at this shape leaves **38%** at 1.7. A flat field leaves 2% at 10.0 |
| `regime_quiet_hz` / `regime_busy_hz` | 0.0052 / 0.0190 Hz | 25th and 75th percentiles of per-recording mean ROI rate over baseline windows. No clustering, no bin, no threshold — a rate is a count over a duration |
| `n_roi` | 33 | a count of ROIs in the window. It comes back from the same call as the two below but is not derived from the clustering |

Each of these carries its own ⚠ in its own docstring, and those are worth keeping in view:
`rate_shape`'s tail **overshoots** (the fit reaches ~847 mHz where the data reach 486), and
`burst_shape` (1.547, 1.388) is fitted **per scale independently and then multiplied** — no
joint fit, because the joint likelihood has no closed form — which is why its coarse end is
short: variance/mean at 300 s is **4.44 simulated against 5.69 real**. Busy stretches of several
minutes are shorter in simulation than in tissue.

### Out of the clustering instrument, at one bin, with no sensitivity check

| constant | value | exposure |
|---|---|---|
| `jitter_sec` | 0.36 fast, 0.30 slow | **already shown wrong** — tracks bin ÷ √12; measured without bins it is 0.106 and 0.135 s |
| `participation` | 0.18 fast (moving to 0.19), **0.38 slow** | `part_n_obs`, the median distinct-ROI count per cluster, from the same `_clusters` call at the same 1.0 s bin. **It was swept and it held** — see the correction below |

### Correction, same day: participation WAS swept, and it held

**The first version of this file said nobody had run the sweep. That was wrong**, and the
answer was in the tool's own docstring. `tools/measure_slow_bench.py`'s `BINS` carries the
result of the 2026-09-21 measurement that caught the jitter: over 0.5 s to 5 s the jitter
tracks bin ÷ √12 on both streams (fast 0.17 → 2.03 s, slow 0.21 → 1.39 s), while
**participation does not move — fast 0.19 at every bin, slow 0.37–0.38 from 0.5 s to 3 s.**
Figure: `<darkroom>/bugarach/2026-09-21-slow-bench-jitter-vs-bin.png`.

So the recommendation below is already satisfied for the sweep itself, and the shape of the
worry changes rather than disappearing. What remains:

- **The quoted stability stops at 3 s.** The bins run to 5 s and the flat range is reported as
  0.5–3 s. At `wm_factor` 1.5 a 5 s bin gathers participants within ±7.5 s of a cluster centre,
  and at a background of 0.0052–0.019 Hz per ROI over 33 ROIs that window admits several
  background ROIs by chance. Whether participation holds at the top of the range is not stated.
- **Participation still has no null.** Flat against the bin is not the same as corrected for
  chance gathering, and there is no `part_n_null` to subtract.
- **The flatness is empirical, not structural.** Participants are gathered within ±1.5 × bin of
  the cluster centre, so the quantity *is* coupled to the bin by construction; it happens not to
  move over the range tested. That is worth knowing but it is a different kind of assurance from
  the rate shape's, which predicts a number it was not fitted to.

Two things sharpen this.

**The instrument already computes a control for the jitter and the bench does not use it.**
`assess_coactivity` returns `jit_obs`, `jit_null` and `jit_excess` — the surrogate version is
right there in the same result. Neither `bench.py` nor `remeasure_bench.py` mentions
`jit_null` or `jit_excess` anywhere: the bench absorbed the uncorrected observation.

**Participation has no control at all.** The same result carries `n_clusters_obs` and
`n_clusters_null`, and `jit_obs` and `jit_null` — but `part_n_obs` is reported observed-only.
There is no `part_n_null` to compare against, so unlike the jitter there is not even a
surrogate to check it with. One would have to be added.

**And participation is the value with the most riding on it.** The WSMIP064 session's own
finding: *slow participation, 0.38, is the value the whole slow bench turns on* — at fast's
participation the slow bench reproduces fast's detector ordering. It is also the constant
already queued to move, 0.18 → 0.19, after the 2026-09-22 meeting.

### Design choices, correctly reasoned, but not measurements

`min_sep_sec` 120 s (set by the detectors' context window, to keep real coordination out of the
null they threshold against), `duration_sec` 2700 s (falls out of that spacing), the
participation spread 0.30 / 0.18 / 0.10, `n_per_level` (5, 5, 5), and `hot_rate_hz` 0.06 (six
times measured baseline, chosen to be busier than any real condition without leaving the
physical world). These are stated as decisions in `BENCH_RECORDING`'s docstring and should not
be confused with the measured set — they are not wrong, they are chosen.

The distractors (6 at `distractor_frac` 0.18) are a known weak point the methods review already
raised: they are built exactly like the 18% events and are not kept away from them.

### Absorbed from the producer rather than measured here

Event widths, via `simulate.MEASURED_WIDTH_QUANTILES`, come from the producer's `width_sec`
under its `width_def` — and on the slow stream that is a deliberate truncation. FOUNDATIONS §7:
the duration is the column.

### Known-unmeasured, and already flagged by the tree

**The simulators' long-lag level is far above the real one** — excess ≈ 0.75 at 5–10 s on the
fast bench against about 0.1 in real data (Figure 1 of the jitter record). The 064 handoff lists
it as open and not yet looked at. Whatever produces it — the elevated-rate stretch, the burst
shapes, or both — the bench's background carries several times the shared slow structure real
tissue does, which is the axis a co-modulation claim lives on.

## What to do before item 2 is ruled

1. **Sweep participation across bins, the way the jitter was swept.** The machinery exists:
   `tools/measure_slow_bench.py` already carries `BINS = (0.5, 1.0, 2.0, 3.0, 5.0)`, which is
   how the jitter's bin-dependence was caught. `tools/remeasure_bench.py` is still single-bin at
   1.0 s. If participation moves with the bin, it is the same defect and adopting a jitter while
   leaving it alone fixes half a bench.
2. **Decide what participation should mean**, if it does move: the count at a bin, or a
   bin-independent quantity measured the way the correlogram measures jitter — from cross-ROI
   structure rather than from bin membership.
3. **Then rule the jitter**, and move both constants in the same overnight pass as the 0.19
   change, since all three move the same bench.

The 064 handoff already proposes making the re-measure run at two bins and refuse a value that
moves with the bin. This todo says that guard must cover **participation**, not only the jitter,
and that the instrument's own null is available for one of them and missing for the other.
