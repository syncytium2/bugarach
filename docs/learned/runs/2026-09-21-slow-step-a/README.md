# Step A of the slow bench: is slow participation real, and does the jitter choice matter?

Written 2026-09-21 on WSMIP064 for `HANDOFF-slow-bench.md`. Working material, not murderboarded.
Both checks read the default dataset (`2026-09-17_revised_2v_long_STEPS_AND_PINS_EXCLUDED`),
baseline analysis windows only.

## Participation: confirmed, and slow's events are about twice fast's at every floor

`participation_k.py` → `participation_k.json`. Median participants per cluster over median ROI
count (the bench's definition), from `assess_coactivity` at a 1 s bin, 95% bootstrap interval
over recordings:

| floor K (ROIs) | fast | slow | slow ÷ fast |
|---|---|---|---|
| 3 | 0.127 [0.119, 0.179] | 0.222 [0.156, 0.323] | 1.75 |
| 4 | 0.190 [0.182, 0.230] | 0.381 [0.281, 0.450] | 2.00 |
| 5 | 0.222 [0.212, 0.267] | 0.421 [0.375, 0.509] | 1.90 |
| 6 | 0.254 [0.235, 0.305] | 0.476 [0.430, 0.571] | 1.87 |

The value depends on K on both streams, because a floor of K counts only clusters of at least
K; the ratio does not. K = 4 is the convention both benches use (the MATLAB summary's headline
K). **Independent check**: the MATLAB summary the fast bench was first built from,
`<darkroom>/constellation/coordination_timescale_summary.csv`, flavour `all-baseline`, gives
median participants 6 (fast) and **12.5 (slow)** at K = 4 — 12.5 of 33 ROIs is 0.38.

## Jitter: the fast analogy was wrong, and the choice matters for two detectors

The fast bench's `jitter_sec` 0.36 is **that MATLAB summary's value** (`jit_obs_med`, fast,
K = 4), not a bugarach measurement. The same summary gives **0.46 s for slow** at K = 4. The
slow bench was set to 0.30 s on the argument that it is "what the same instrument gives at the
fast bench's bin" — true of bugarach's instrument at 1 s, but the fast bench does not take its
jitter from that instrument, so the analogy does not hold. 0.46 is what bugarach's instrument
reads at a 2 s bin (`tools/measure_slow_bench.py`, `BINS`), which suggests the MATLAB summary
bins the slow stream wider.

`jitter_sens.py`: each detector at `bench_slow.OPERATING_POINTS` (before SPIKE-synch's slow
setting merged, so SPIKE-synch here is at the FAST settings), seeds 1–48, mean F1 over both
backgrounds:

| detector | jitter 0.30 s | 0.46 s | change |
|---|---|---|---|
| LoCo | 0.853 | 0.840 | −0.013 |
| locust | 0.607 | 0.510 | **−0.098** |
| binned SCE | 0.785 | 0.783 | −0.003 |
| CoactDetect | 0.861 | 0.861 | +0.000 |
| rate+context | 0.848 | 0.837 | −0.010 |
| SPIKE-synch (fast settings) | 0.735 | 0.652 | **−0.082** |

**So step C is held**: a 14-GPU-hour comparison on a jitter value that rests on a wrong
analogy is the kind of known problem that stops work. The decision is Tony's — keep 0.30, or
take 0.46 as the fast bench took its value — and it moves the slow bench, so the slow search
and the adopted settings would be re-checked on it.
