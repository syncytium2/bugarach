# The COMBINED stream over the full cohort

**Run 2026-09-22 evening on WSMIP065**, on the default folder Tony confirmed for the session
(`2026-09-17_revised_2v_long_STEPS_AND_PINS_EXCLUDED`, 84 recordings). Outputs are in
`<darkroom>/bugarach/2026-09-23-full-cohort-combined/` — `combined_settings.csv`, `detect/`,
`models/`, `rasters/`. Bulk stays there; this is the repo's record.

> ⚠ **Nothing here rests on adopted settings.** `bench_combined.OPERATING_POINTS` holds search
> picks whose `source` says they await Tony's review, and two detectors are at the fast settings
> they started from. Read the call counts as *what these settings do*, not as a result about the
> tissue. `bench.OPERATING_POINTS` and `bench_slow` were not touched.

Abbreviations: **ROI**, region of interest (one imaged cell); **F1**, the harmonic mean of recall
and precision.

## What ran

| stage | tool | output |
|---|---|---|
| settings | `settings_from_bench.py --bench combined` | `combined_settings.csv`, 6 detectors, `stream=combined` |
| detection | `bugarach detect --stream combined --model models/best.json` | `detect/detections.csv`, **22,569 calls** |
| calls | `measure_calls.py` | `detect/calls_measured.csv` |
| rasters | `make_group_raster_summary.py --steps-excluded --streams combined` | `rasters/`, **10 pages** (5 groups × PNG + HTML) |

## Calls per detector, whole cohort

**Updated 2026-09-23** after SPIKE-synch's pick was installed
(`2026-09-23-full-search-combined-sync-rerun`). The merged detections are
`detect/detections_tuned.csv`, which the rasters are drawn from; `detect/detections.csv` is the
first pass and is kept.

| detector | calls | setting |
|---|---|---|
| LoCo | 3,196 | combined search pick |
| locust | 2,900 | combined search pick, anchor-flagged |
| rate+context | 2,897 | combined search pick |
| binned SCE | 2,673 | fast (nothing beat it) |
| **SPIKE-synch** | **2,597** | combined search pick, installed 2026-09-23 |
| chorus_gain_norm | 2,361 | trained on this bench, seed 2 |
| **CoactDetect** | **2,242** | combined search pick |

**SPIKE-synch fell from 6,300 calls to 2,597** when its pick was installed. In the first pass it
was making **2.8× what CoactDetect did**, and that was never a fact about SPIKE-synch: it was the
one detector left at a setting chosen for a different bench, meeting a stream with roughly twice
the onsets. Tuned, it sits between binned SCE and CoactDetect, where the bench scores say it
belongs.

The route from withheld to installed is worth reading, because the first pick was refused for a
reason that turned out not to be the operative one — the sub-integer `min_n` was cosmetic, and
the gain came from `dt` and `C_min` at their grid floors. The rerun README has it.

**CoactDetect makes the fewest calls of the six coded detectors.** Its pick moved `min_rois` 3 → 4
and added an 8 s guard, both of which suppress calls, and its bench null rate fell 12.9 → 3.5 per
hour.

**CoactDetect makes the fewest calls of the six coded detectors.** Its pick moved `min_rois` 3 → 4
and added an 8 s guard, both of which suppress calls, and its bench null rate fell 12.9 → 3.5 per
hour.

## The rasters

Five groups — `DI_TTX`, `DI_senktide`, `MALE_TTX`, `MALE_senktide`, `ORX_TTX` — each a PNG and an
HTML. One row per recording, `t = 0` at the end of that recording's baseline, detector lanes above
each raster and nothing drawn on the raster itself.

**Two inks on the raster, deliberately**: fast onsets black, slow onsets vermillion. That departs
from the one-ink rule, at Tony's instruction for this stream — the whole question the combined
stream asks is which onsets came from where, and a single ink would erase it.

⚠ **One thing to look at on `DI_senktide`**: in `20250926_235` the top ROI row is a near-continuous
vermillion line across the whole recording — one cell firing in the slow stream at a rate nothing
else approaches. It has not been chased and is not excluded; it is the kind of thing a combined
raster surfaces that a per-stream one can bury, and it is the producer's call whether that cell is
real.

## What this does not establish

No detector is right about a real slice here. The corpus has no ground truth, the settings are
unreviewed picks, and two detectors are at settings chosen for a different bench. What the pass
establishes is that the combined route runs end to end — bench, model, settings, detection,
rasters — on the folder the session confirmed.
