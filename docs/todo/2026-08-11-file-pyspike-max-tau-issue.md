---
status: open
filed: 2026-08-11
---

# File the PySpike max_tau bug upstream

Report to https://github.com/mariomulansky/PySpike that 0.9.0's `max_tau`
coincidence-window cap is broken: in the MRTS-era `get_tau`, the cap enters
only as the DEFAULT for missing edge-neighbor ISIs — whenever all four
surrounding ISIs exist, `max_tau` is silently ignored, so spikes seconds
apart count as coincident under a 0.25 s cap.

**Verified unreported as of 2026-08-11** (searched their tracker: no issue
touches the cap).

## Minimal repro (include verbatim)

```python
import pyspike
a = pyspike.SpikeTrain([40.4, 77.3, 534.4], (0, 600))
b = pyspike.SpikeTrain([58.8, 85.0, 300.0], (0, 600))
prof = pyspike.spike_sync_profile(a, b, max_tau=0.25)
# spikes 7.7 s apart marked coincident: y == 1 at t=77.3 and t=85.0
```

Note the contrast case that hides the bug: a single-spike train (missing
neighbors -> the cap applies as the default) behaves correctly, which is
why casual tests pass.

## Body should include

- Diagnosis: `get_tau`'s neighbor defaults are `max_tau`, but existing ISIs
  are never min'd against it (pre-0.9 behavior capped explicitly); with
  MRTS=0 the Interpolate path reduces to min of half-ISIs, uncapped.
- Expected behavior per cSPIKE (the Kreuz-lab reference implementation,
  which caps correctly) and per PySpike's own docs.
- Suggested fix: restore `tau = min(tau, max_tau)` after the ISI min.
- Link bugarach's `src/bugarach/detectors/sync.py` docstring + the repo's
  cross-check test for the full analysis.

## Process

Draft the issue text in this file first; **Tony reviews before anything is
posted** (external communication). After filing, add the issue URL here and
flip status.
