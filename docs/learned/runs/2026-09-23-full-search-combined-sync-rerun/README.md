# SPIKE-synch re-searched on COMBINED, and the extensions turn out to be cosmetic


> ⚠ **Measured on `2026-09-17_revised_2v_long_STEPS_AND_PINS_EXCLUDED`, and the data have
> since changed** (Tony, 2026-09-23: *"data changed. we'll come back to this."*). Nothing
> here is retracted — every number is correct about that folder — but it is not the current
> input. What inherits it, and in what order it would be redone:
> [`docs/todo/2026-09-23-the-overnight-runs-are-pinned-to-an-export-that-has-changed.md`](../../../todo/2026-09-23-the-overnight-runs-are-pinned-to-an-export-that-has-changed.md).

**Run 2026-09-23 on WSMIP065**, 15.1 minutes, on the search with the integer-floor fix (#755).
`tools/search_all_settings.py --bench combined --sliding --only sync`.

The first combined search (#754) returned SPIKE-synch's pick with the largest gain of the six and
in a form that could not be installed. This run, plus one attribution test, resolves it: **the
pick is installed, with every value on its own declared grid, at the full gain.**

Abbreviations: **F1**, the harmonic mean of recall and precision.

## What the fix changed, and what it did not

| | first search (#754) | rerun, fixed `extend` |
|---|---|---|
| `min_n` | **0.25** | **2** |
| gain | +0.131 [+0.120, +0.142] | +0.131 [+0.119, +0.141] |

`min_n` is a clean count now, at the new `COUNT_FLOOR` of two cells. **The gain is unchanged**,
which is the informative part: the sub-integer floor was never load-bearing. It was an artifact
riding beside the real effect, not the source of it. The fix was still right — but it was
guarding against something cosmetic rather than something that mattered.

## What the fix did not reach

`C_min` and `dt` both came back at **exactly one eighth of their declared grid floors**
(0.02 → 0.0025 and 0.05 → 0.00625). That is three halvings, which is `MAX_EXTENSIONS` exhausted:
the edge rule was still "improving" when the cap stopped it, so neither was bracketed. The
integer fix does not apply — both are genuinely continuous.

And `C_min` came back at **0.0025 again, the same value the slow search produced**. That thread
diagnosed it: *every value 0–0.03 gives identical calls, the profile steps by about 1/31, so the
search was extending along a flat stretch and the edge rule cannot tell a plateau from a climb.*

## The attribution test

Rather than assume that diagnosis transfers, it was tested on this bench, on the search's own
held-out seeds (49–96), both backgrounds.

| variant | mean F1 | vs shipped |
|---|---|---|
| shipped (fast settings) | 0.666 | — |
| pick as searched | 0.797 | +0.131 |
| pick, `dt` → 0.05 (grid floor) | 0.797 | +0.131 |
| pick, `C_min` → 0.02 (grid floor) | 0.797 | +0.131 |
| **pick, both → grid floors** | **0.797** | **+0.131** |
| pick, both → shipped values | 0.720 | +0.054 |
| shipped + `max_gap` 8 only | 0.671 | +0.005 |

**Pinning both extended values back to their grids costs nothing.** The plateau diagnosis
transfers exactly. So the installed point uses `C_min` 0.02 and `dt` 0.05 — on-grid, bracketed —
and keeps the whole +0.131.

Two things the table settles that the search could not:

- **The gain is not `max_gap`.** 8 s on the shipped point is worth +0.005. A reasonable guess,
  given the slow thread's experience, and wrong.
- **It is `dt` and `C_min` at their grid floors**, worth +0.077 of the +0.131. SPIKE-synch wants
  a finer detection resolution and a lower coincidence floor on this stream. The search found
  that correctly and then kept walking past where the improvement stopped.

## Installed

```
C_threshold 0.08 · C_min 0.02 · tau_max 0.25 · max_gap 8.0 · min_n 2 · dt 0.05 · isi_adaptive
```

Probe 0.20 calls/min against a budget of 16; null 0.11/hour. In `bench_combined.OPERATING_POINTS`
with a source string saying it awaits Tony's review. `bench.OPERATING_POINTS` and `bench_slow`
untouched.

**On the cohort this takes SPIKE-synch from 6,300 calls to 2,597** — it had been making 2.8× what
CoactDetect did, purely because it was the one detector left at a setting chosen for another
bench. It now sits between CoactDetect (2,242) and binned SCE (2,673).

## What would be worth doing next

The `extend` cap is a **silent** one: three halvings and it stops, reporting the edge value as if
it were chosen. For a count that is now fixed. For a continuous setting the same shape remains —
a search that runs to the cap should say so in the record, and a plateau should be distinguishable
from a climb by checking whether the objective actually moved rather than by where the walk
stopped. Both `C_min` findings, on slow and here, were plateaus that read as climbs.
