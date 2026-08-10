# bugarach

Python/web port of `explore_sce` — the interactive per-slice coordination viewer from
[interface2](https://gitlab.com/defazio/interface2) — so colleagues **without MATLAB**
can browse slices and tune detectors in a browser.

> **The name.** Pic de Bugarach is the mountain in the French Pyrenees that doomsday
> believers converged on for the 2012 Mayan-calendar apocalypse, convinced it alone
> would be spared. The world did not end; the village had to restrict access to the
> summit. A coordination detector is a machine for deciding whether an alignment is
> real — this repo is named for the people who decided without one.
> (Team constellation, alongside `syzygy`, `murmuration`, `fireflies`.)

## What the MATLAB original does

`explore_sce.m` (interface2) shows five/six coordination detectors on one timeline for
a chosen slice — FAST and SLOW rasters with per-detector event lanes, a statistic-trace
signal row per detector, per-stream tunable parameters, and peak-gated vs
supra-threshold detection modes. Detectors run live off per-slice event-onset data.

## Port plan (in order)

1. **Store reader** — `bugarach.store.load_slice` reads the `event_store_onset*`
   `.mat` files directly (both MATLAB v7 via scipy and v7.3/HDF5 via h5py). ✅ working
2. **Detectors** — rate+context, binned SCE, CICADA, SPIKE-synch, CoactDetect, LoCo,
   ported against interface2's `docs/specs/detector_output_spec.md` (the unified
   detector-output contract). SPIKE-synchronization comes from
   [PySpike](https://github.com/mariomulansky/PySpike) (same Kreuz-lab algorithms as
   cSPIKE). **Every port gets a parity test against MATLAB reference output before it
   is trusted.**
3. **Peak gating** — port of `if2_peak_gate` (prominence-qualified maxima of the
   statistic trace, shared min-distance D).
4. **UI** — web front end with linked rasters/signal rows and per-detector recompute.
   Framework decision open: Dash vs Panel/HoloViews.

## Data

The viewer needs only the onset stores (`event_store_onset_revised_2v` is ~4 MB for
85 slices), **not** the 127 GB trace archive. Only **synthetic** slices are committed
here as test fixtures (`tests/fixtures/`); real stores stay out of the repo until the
data-sharing question is settled. The repo is private for the same reason.

## Dev

```bash
pip install -e ".[dev]"
pytest
```

The test suite runs on the committed synthetic fixture; if the interface2 Dropbox data
root is present on the machine, it also smoke-tests a real slice.
