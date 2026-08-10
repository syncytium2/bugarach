# bugarach

Python/web port of `explore_sce` — the interactive per-slice coordination viewer from
[interface2](https://gitlab.com/defazio/interface2) — so colleagues **without MATLAB**
can browse slices and tune detectors in a browser.

Detector ports build on open-source implementations. **See
[Licensing & citations](#licensing--citations)** for what to cite in any publication
that uses results from this tool.

> **The name.** Pic de Bugarach is the mountain in the French Pyrenees that doomsday
> believers converged on for the 2012 Mayan-calendar apocalypse, convinced it alone
> would be spared. The world did not end; the village had to restrict access to the
> summit. A coordination detector is a machine for deciding whether an alignment is
> real — this repo is named for the people who decided without one.
> (Team constellation, alongside `syzygy`, `murmuration`, `fireflies`.)

## What the MATLAB original does

`explore_sce.m` (interface2) shows six coordination detectors on one timeline for
a chosen slice — FAST and SLOW rasters with per-detector event lanes, a statistic-trace
signal row per detector, per-stream tunable parameters, and peak-gated vs
supra-threshold detection modes. Detectors run live off per-slice event-onset data.

## Port plan (in order)

1. **Store reader** — `bugarach.store.load_slice` reads the `event_store_onset*`
   `.mat` files directly (both MATLAB v7 via scipy and v7.3/HDF5 via h5py). ✅ working
2. **Detectors** — in port order: rate+context, CoactDetect, LoCo, binned SCE,
   CICADA, SPIKE-synchronization — each ported against interface2's
   `docs/specs/detector_output_spec.md` (the unified detector-output contract).
   SPIKE-synchronization comes from
   [PySpike](https://github.com/mariomulansky/PySpike) (same Kreuz-lab algorithms as
   cSPIKE). **Every port gets a parity test against MATLAB reference output before it
   is trusted.**
3. **Peak gating** — port of `if2_peak_gate` (prominence-qualified maxima of the
   statistic trace, shared min-distance D).
4. **UI** — web front end with linked rasters/signal rows and per-detector recompute.
   Framework decision open: Dash vs Panel/HoloViews.

## Licensing & citations

This project deliberately builds only on permissively licensed implementations — that
is what lets it run as a shared web app without asking anyone's permission. The one
restricted tool in the ecosystem, cSPIKE, is **not** used; its algorithms are taken
from PySpike instead. Do not port code from cSPIKE's MATLAB source.

| Upstream | License | Role here |
| --- | --- | --- |
| [PySpike](https://github.com/mariomulansky/PySpike) | BSD | SPIKE-synchronization (same Kreuz-lab algorithms as cSPIKE) |
| [CICADA](https://gitlab.com/cossartlab/cicada) | MIT | CICADA detection method (ported; carries upstream copyright notice) |
| cSPIKE (MATLAB) | research/education only — **not used** | replaced by PySpike |

**Cite in any publication that uses results from this tool:**

- **PySpike** — Mulansky M., Kreuz T., *PySpike — A Python library for analyzing
  spike train synchrony*, SoftwareX 5, 183–189 (2016).
- **CICADA** — cite per the [Cossart-lab repo](https://gitlab.com/cossartlab/cicada)'s
  guidance.
- Method papers for the remaining detectors will be added here as each port lands.

## Usage

```python
from bugarach import load_slice

s = load_slice("tests/fixtures/synth_fastcal_s1.mat")
s.fast.n_rois, s.fast.n_events   # per-stream ROI/event counts
s.fast.locs[0]                   # onset times (sec) for ROI 0, FAST stream
s.regions                        # annotated time windows (name, slot, start, end)
```

## Data

The viewer needs only the onset stores (`event_store_onset_revised_2v` is ~4 MB for
85 slices), **not** the 127 GB trace archive. Only **synthetic** slices are committed
here as test fixtures (`tests/fixtures/`); real stores stay out of the repo until the
data-sharing question is settled. The repo is private for the same reason.

## Dev

Requires Python ≥ 3.11.

```bash
python3 -m venv .venv && source .venv/bin/activate
pip install -e ".[dev]"
pytest
```

`pip install -e ".[dev,sync]"` additionally pulls PySpike, needed once the
SPIKE-synchronization detector lands.

The test suite runs on the committed synthetic fixture. To also smoke-test a real
slice, point `BUGARACH_DATA_ROOT` at an `event_store_onset_revised_2v` store
directory (it defaults to the lab Dropbox path); the test skips if the directory
is absent.
