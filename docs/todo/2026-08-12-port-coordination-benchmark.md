---
status: open
filed: 2026-08-12
---

# Port interface2's coordination benchmark + scoring suite

The simulation, scoring and calibration tooling for coordinated-event detection
**already exists** in interface2. It was never ported to bugarach, and nothing
in this repo pointed at it — a session surveying bugarach alone concluded no
simulator existed and proposed building one from scratch. It is a **port**, not
a greenfield build.

## What exists upstream (read-only survey, 2026-08-12)

| File | Lines | Role |
|---|---|---|
| `generate_synth_coord.m` | 193 | Planted events at 3 participation levels (100/75/50% of ROIs), Poisson background, onset jitter. Plus a **`hot_window` promiscuity probe** (dense-but-random block with a wash-in ramp and NO planted events — a rate-fooled detector fires there) and **correlated-burst distractors** tracked in `gt.distractors` as non-recall targets. |
| `generate_coord_benchmark.m` | 158 | One recording holding a full **participation × tightness grid** across a sparse→dense background ramp, plus distractors. |
| `score_coord_detection.m` | 90 | Greedy nearest match within ±tol; recall **broken down by participation level**, false alarms, and FAs inside the hot window. |
| `score_coord_grid.m` | — | Grid-cell scoring. |
| `optimize_detectors.m` | 156 | Sweeps each detector's params over the benchmark, multi-seed, picks the **F1-optimal** operating point; emits an optimal-settings `.mat` and a recall/precision figure. |
| `calibrate6.m` | 115 | Six-detector F1 calibration, threshold **and** peak modes, per-detector P grid with D∈{2,4}, at two regimes (sparse `bg=0.05`, dense `bg=0.15`). |
| `run_coord_benchmark.m`, `run_all_detectors.m` | — | Drivers. |

On `origin/main` except where noted; the *sweeps themselves*
(`rederive_optima_fast/_slow/_sparse.m`, a widened `optimize_detectors`,
`write_calibrated_settings.m`) are on `origin/explore-sce-optimized-defaults`
and `origin/sparse-benchmark-optim`. `optimize_detectors` on
`detector-defaults-optimized` **cannot reproduce the published numbers** — its
grids are too narrow.

## Why this is the cleanest port target in the repo

`generate_synth_coord` emits the event-store contract directly
(`.fast/.slow/.regions/.slice_id`, `.locs` + `.t50rise` cells) — exactly what
`store.py` reads and `io.py:slice_from_events` builds. No adapter on either
side. And unlike a from-scratch simulator it has a **parity oracle**: with
`RandomState(seed) ≡ rng(seed)` already verified (FOUNDATIONS §2), the port can
be held to the same 1e-9 bar as the six detectors.

## Why it is worth doing even if nothing downstream needs it

1. It replaces `tests/fixtures/synth_fastcal_s1.mat` — a committed binary with
   **no generator in the repo**, unreproducible on any machine. (Probed: 30
   ROIs, 4520 s, 2675 events/stream, 32 bins with ≥5/30 ROIs coactive, so it
   *does* carry planted structure — but `fast` and `slow` are byte-identical
   and `t50rise == locs`, and no ground-truth labels are recorded anywhere.
   "fastcal" appears nowhere in interface2; its provenance is unresolved.)
2. It enables an ROC / sensitivity bench across all six ports against known
   truth — a portfolio-grade result on its own (FOUNDATIONS §8).
3. It is the prerequisite for any learned detector (see the DL note below).

## Constraints for the port

- `default_rng` is banned in `src/` (sapper SAP002) — a simulator that lands in
  the package inherits `RandomState`. That is also what parity requires.
- Ground truth must travel with the data: `(t_start, t_end, participating
  ROIs, participation frac, tightness)`. Detector outputs are **not** labels —
  training or scoring against them yields a detector emulator.

## Note on deep learning

There are **no** DL plans anywhere in bugarach (repo-wide search: zero hits),
and the current framing cuts against one — "parity is the product" means every
detector here is defined by matching a MATLAB oracle, and a learned detector
has none. interface2 does contain DL (`seq2seqLSTMexample.m`, `seq2seq_ca2ap.m`,
Cascade) but for **calcium→spike inference upstream of events**, not for
coordination detection. If a learned detector is ever wanted, this port is step
one, and the label-definition question has to be settled first: the six
detectors disagree on what an event *is* (`episode` vs peak mode; `width_kind`
of `tightness` / `episode_span` / `half_prominence`).
