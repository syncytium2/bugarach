---
status: open
filed: 2026-08-12
---

# Reconcile viewer defaults against the calibrated operating points

`PARAM_SPECS` in `src/bugarach/ui/app.py` ships one default per parameter,
applied to every stream. Upstream has **per-stream calibrated optima** in
`if2_detector_defaults.m` (interface2 `origin/detector-defaults-optimized`),
derived by `optimize_detectors.m` from the coordination benchmark and adopted
2026-08-05. Nothing in bugarach records whether its defaults came from there.

They partly did. Compared field-by-field, 2026-08-12 (calibrated **FAST** optima
vs bugarach defaults):

| detector | aligned | diverging (calibrated FAST → bugarach) |
|---|---|---|
| **loco** | bin 1 s, ctx 120 s, pctile 99.9, min_rois 3, thr_step 15 s, merge_gap 2 s | n_surrogates 200 → 100 |
| **sync** | tau_max 0.25, max_gap 0.5, C_thr 0.1, C_min 0.1, min_n 3 | — |
| **coact** | ctx 60 s, min_rois 3, n_surr 100 | int_win 2 → 1 s; alpha 1e-4 → 1e-3 |
| **sce** | min_rois 3 | bin 2 → 10 s; pctile 99.9 → 99.0; n_surr 1000 → 200 |
| **cicada** | min_dist 4 frames, active_dur 1 s | sync_frames 1 → 2; pctile 99.99 → 99.9; n_surr 100 → 50 |
| **rate** | rate_win 1 s, merge_gap 3 s | excess_thr 10 → 5 Hz; ctx 30 → 60 s |

So LoCo and spike-sync are effectively the calibrated FAST optima; SCE and
CICADA are not, and SCE's bin width differs by 5×.

## Do NOT bulk-adopt these — the caveats are load-bearing

Carried verbatim from `if2_detector_defaults.m`, which is itself careful:

1. **Upstream marks them PROVISIONAL.** `rederive_optima_fast.m` says "params
   from a measurement pending Tony's review" — the benchmark is parameterized
   by the measured coordination timescale, and that measurement was not
   reviewed when these were derived.
2. **Half of them are weak optima.** F1 at these settings (FAST | SLOW):
   loco 0.859 | 0.466 · sce 0.827 | 0.532 · coact 0.829 | 0.757 ·
   sync 0.816 | 0.735 · cicada 0.679 | 0.550 · **rate 0.444 | 0.371**.
   Anything below ~0.6 means the sweep found no good operating point and the
   "optimum" reflects a flat/noisy F1 surface — that is all of SLOW except
   coact/sync, and rate on **both** streams.
3. **Grid-edge hits:** rate `excess_thr=10` and sce `pctile=99.9` sit at the
   edge of their swept range; the true optimum may lie outside it.
4. **Not swept:** `n_surrogates` and `min_rois` were held fixed (loco used 80
   purely for sweep speed). They are not optima — which makes the loco
   `n_surrogates` divergence above a non-finding.
5. **Measured with region trimming DISABLED** (`NOTRIM`,
   `clamp_context_to_region=false`) — i.e. under non-production windowing.
6. Upstream has an **unreconciled design split**: `detector-defaults-optimized`
   moves the code defaults, `explore-sce-optimized-defaults` leaves them alone
   and applies the optima via a per-store CSV. Do not double-apply.

## The actual work

- Decide whether bugarach's viewer defaults should track the calibrated optima
  at all, or stay at neutral round numbers with the optima documented. A viewer
  for *other labs* (FOUNDATIONS §1) arguably wants defaults that are not tuned
  to this lab's KNDy regime — that is a real argument for the status quo.
- Whichever way: **record the provenance in the repo**, so the next session
  does not have to re-derive it from a MATLAB branch. Right now the numbers
  have no story attached.
- bugarach has no per-stream default mechanism at all. Per-stream parameters
  already broadcast (FOUNDATIONS §3); the viewer just does not use it.
- Blocked on nothing, but far more meaningful after
  [`2026-08-12-port-coordination-benchmark.md`](2026-08-12-port-coordination-benchmark.md)
  lands — with the benchmark ported, these numbers become re-derivable here
  instead of quoted from a branch.

## Measured here, 2026-08-13 — the numbers are now re-derivable

`src/bugarach/bench.py` landed, so the sweep no longer has to be quoted from a
MATLAB branch. Swept on the sparse regime, one seed, F1 at each grid point:

| detector | knob | declared point | F1 there | best on this bench | F1 |
|---|---|---|---|---|---|
| loco | `threshold_pctile` | 99.9 | 0.94 | 99.99 (plateau to 1e-4) | 1.00 |
| cicada | `sce_percentile` | 99.99 | 0.97 | 99.9 | 0.97 |
| sce | `threshold_pctile` | 99.0 | 0.85 | 95.0 | 0.97 |
| coact | `alpha` | 1e-4 | 0.97 | 1e-6 | 1.00 |
| rate | `excess_threshold_hz` | 5.0 | 0.88 | **10.0** | 1.00 |
| sync | `C_threshold` | 0.1 | 0.62 | 0.2 | 1.00 |

(SCE and coact rows re-measured after the region fix below; the earlier figures
for them were taken while SCE could see only 44% of the recording.)

**Caveat 3 above partly resolves.** Upstream's `rate excess_thr=10` was
untrustworthy because it sat at the edge of the swept range. A wider grid here
finds the same value as a genuine interior peak — F1 falls to 0.80 at 20 — so
that particular grid-edge worry was unfounded. An independent bench reproducing
an upstream optimum is the useful kind of agreement.

**Four of the six declared points are not optimal on this generator, and they
have deliberately not been changed.** Re-tuning to a synthetic benchmark whose
realism nothing has yet measured is the trap this project already paid for
(`docs/simulation_plan.md` §5, *stranded validation* and *the benchmark, not the
detectors, was the problem*). The numbers say the sweep works, not that the
defaults are wrong. What would license a change is the real-data validation
that §6 names as the honest blocker — not a better F1 against data we generated
ourselves.

## ~~SCE is a separate problem from its defaults~~ — resolved, and the first diagnosis was wrong

**Superseded 2026-08-13.** The original text here blamed SCE's ceiling on
`threshold_pctile` being a percentile over *bins*, so that detection count was
capped by recording length. That was a guess from the numbers, and it was wrong.

The actual cause was visible the moment the analysis traces were drawn under the
raster: **SCE's trace simply stopped, covering 1505–2695 s of a 2700 s
recording.** The generator was stamping every recording with a region named
`baseline` spanning the whole duration, and the region windowing rules read
`baseline` as the pre-solution period and trim it to the final
`baseline_window_max_sec` (1200 s). SCE honours that trim; LoCo and CICADA do
not restrict detection to the window, so they were unaffected and the asymmetry
looked like a detector difference.

SCE was therefore scored against 15 planted events while being shown 7 of them —
a recall ceiling of 0.47, measured at 0.40. It was not a weak detector. It was a
detector shown 44% of the data.

With the annotation removed (`simulate_coordination` no longer invents regions):

| | before | after |
|---|---|---|
| SCE recall | 0.40 | 0.73–0.87 |
| SCE F1, sparse | 0.56 | **0.89** |
| SCE precision | 0.92 | **1.00**, in both regimes — the most precise of the six |
| LoCo, CICADA | — | unmoved |

Two lessons worth keeping. The scope-mismatch trap in
`docs/simulation_plan.md` §5 is listed as *tuned whole-recording, deployed
per-region*; this is the same trap reached from the other direction, and nothing
in the bench would have caught it, because a detector quietly analysing less
data still returns plausible numbers. And the diagnosis only became obvious when
the picture was drawn — the numbers alone supported a confident, wrong story for
a full day.
