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

| detector | calls | setting |
|---|---|---|
| **SPIKE-synch** | **6,300** | fast (its search pick was withheld) |
| LoCo | 3,196 | combined search pick |
| locust | 2,900 | combined search pick, anchor-flagged |
| rate+context | 2,897 | combined search pick |
| binned SCE | 2,673 | fast (nothing beat it) |
| chorus_gain_norm | 2,361 | trained on this bench, seed 2 |
| **CoactDetect** | **2,242** | combined search pick |

**SPIKE-synch makes 2.8× the calls CoactDetect does**, and it is one of the two detectors still at
its fast setting. That is not a finding about SPIKE-synch: it is the unsearched setting meeting a
stream with roughly twice the onsets. Its search pick — the largest measured gain of the six,
+0.131 F1 — was withheld because `min_n` came back at 0.25, a sub-integer value the search reaches
by halving an integer floor (`2026-09-23-full-search-combined-rest`). Until that defect is fixed,
this row is the cost of leaving it alone.

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
