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
touches the cap). **Re-verified 2026-08-17**: still nothing on the tracker
(open items are #88 interval edges, #85 numpy 2.x), and `master`'s
`cython_get_tau.pyx` still never mins against `max_tau`. Newest release on
GitHub is the 0.9.0 tag (PR #87, 2026-05-11).

## Process

Draft the issue text below; **Tony reviews before anything is posted**
(external communication). After filing, add the issue URL here and flip
status.

---

## Draft issue text (for review — not yet posted)

**Title:** `max_tau` is ignored whenever both spikes have neighbours (0.9.0
and master)

### Summary

In 0.9.0, `max_tau` no longer bounds the coincidence window. In `get_tau`
it is used *only* as the initial value of the four neighbour ISIs, and every
one of those is overwritten when the neighbour actually exists. The returned
tau is `min` of interpolated half-ISIs and is never compared against
`max_tau` again — so for any spike that is not at the edge of its train, the
cap has no effect at all.

Consequence: with sparse trains, a coincidence window of a microsecond still
reports the spike trains as ~⅓ synchronized.

### Reproducer

```python
import numpy as np, pyspike

rng = np.random.default_rng(0)
edges = (0.0, 600.0)
a, b = (pyspike.SpikeTrain(np.sort(rng.uniform(*edges, 60)), edges)
        for _ in range(2))          # mean ISI ~10 s

for max_tau in (None, 1.0, 0.25, 1e-6):
    print(max_tau, pyspike.spike_sync(a, b, max_tau=max_tau))
```

```
None 0.35
1.0 0.3333333333333333
0.25 0.3333333333333333
1e-06 0.3333333333333333
```

A 1 µs coincidence window on trains whose mean ISI is 10 s should give 0.
Instead it gives the uncapped answer, to three digits, and every finite
`max_tau` over six orders of magnitude returns the same number. (The small
gap from the `None` case is not the cap doing its job: it comes from the two
edge spikes, which are the only ones where the default survives.)

Minimal hand-checkable version — the pair at 77.3 s and 85.0 s, 7.7 s apart,
is marked coincident under a 0.25 s cap:

```python
import pyspike
a = pyspike.SpikeTrain([40.4, 77.3, 534.4], (0, 600))
b = pyspike.SpikeTrain([58.8,  85.0, 300.0], (0, 600))
prof = pyspike.spike_sync_profile(a, b, max_tau=0.25)
# y == 1 at t=77.3 and t=85.0
```

Note the contrast case that hides this in casual testing: give each train a
*single* spike and the neighbours are missing, so the defaults survive, the
cap applies, and the answer is correct.

Versions: PySpike 0.9.0 (pip, compiled Cython backend), NumPy 2.5.2,
Python 3.14.5, macOS. Same result from the pure-Python backend.

### Diagnosis

`pyspike/cython/cython_get_tau.pyx` (identical logic in
`cython/python_backend.py::get_tau`):

```cython
cdef double mF1 = max_tau        # only a default...
cdef double mP1 = max_tau
cdef double mF2 = max_tau
cdef double mP2 = max_tau

if i < len(spikes1)-1 and i > -1:
    mF1 = (spikes1[i+1]-spikes1[i])      # ...overwritten, uncapped
if j < len(spikes2)-1 and j > -1:
    mF2 = (spikes2[j+1]-spikes2[j])
if i > 0:
    mP1 = (spikes1[i]-spikes1[i-1])
if j > 0:
    mP2 = (spikes2[j]-spikes2[j-1])

mF1, mF2, mP1, mP2 = mF1/2., mF2/2., mP1/2., mP2/2.
...
return fmin(s1F, s2P)            # never min'd against max_tau
```

With the default `MRTS=0`, `Interpolate(a, b, 0)` returns `min(a, b)`, so
the whole function reduces to the minimum of the four half-ISIs — an
unbounded quantity.

Two things suggest the bound was meant to still be there:

1. The callers in `cython_profiles.pyx` still compute
   `true_max = fmin(t_end - t_start, 2*max_tau)` and pass it in — the factor
   2 exists precisely so that the halving step turns it back into `max_tau`.
   That arithmetic only makes sense if `true_max` is a bound.
2. It *was* there. In 0.6.0 the same helper ended with

   ```cython
   if max_tau > 0.0:
       m = fmin(m, max_tau)
   ```

   The cap was dropped in the MRTS rewrite, and the docstring that describes
   it was not: `spike_sync_profile` still documents `max_tau` as "Maximum
   coincidence window size. If 0 or `None`, the coincidence window has no
   upper bound."

Everything routed through these coincidence kernels is affected —
`spike_sync`, `spike_sync_profile` (bi and multi), `spike_sync_matrix`,
`filter_by_spike_sync`.

### Expected behaviour

The tau-capped adaptive window of Kreuz et al.: the coincidence window is
the minimum of the surrounding half-ISIs, bounded above by `max_tau`. cSPIKE
(the lab's MATLAB reference implementation) does bound it — see the
cross-check below.

### Suggested fix

Restore the bound after the ISI minimum, in both
`cython/cython_get_tau.pyx` and `cython/python_backend.py`:

```diff
     if i<0 or j<0 or spikes1[i] <= spikes2[j]:
         s1F = Interpolate(mP1, mF1, MRTS)
         s2P = Interpolate(mF2, mP2, MRTS)
-        return fmin(s1F, s2P)
+        return fmin(fmin(s1F, s2P), max_tau)
     else:
         s1P = Interpolate(mF1, mP1, MRTS)
         s2F = Interpolate(mP2, mF2, MRTS)
-        return fmin(s1P, s2F)
+        return fmin(fmin(s1P, s2F), max_tau)
```

Since the callers already pass `true_max = 2*max_tau`, the bound wants to be
`true_max/2` — i.e. either halve at the call site or halve here; the
edge-default path already assumes the latter. Happy to send this as a PR
with a regression test if you'd like it in that form.

### Where this was found, if it's useful

We ported the cSPIKE synchronization stack to Python and cross-check it
against both cSPIKE reference output and PySpike. The port agrees with
PySpike to 1e-9 in the *uncapped* regime and disagrees with it at every
finite cap, while matching cSPIKE at the same caps to 1e-9. On a 30-train,
2670-spike recording (median ISI 31 s), mean SPIKE-Sync:

| `max_tau` | PySpike 0.9.0 | cSPIKE-validated |
| --- | --- | --- |
| uncapped | 0.3235 | 0.3235 |
| 0.25 s | 0.3133 | 0.0696 |

Analysis and the cross-check test:
https://github.com/syncytium2/bugarach/blob/main/src/bugarach/detectors/sync.py
and `tests/test_sync_detect.py`.

---

## Notes for the reviewer (not part of the issue)

- The 0.25 s row of that table is the operating point our detectors run at;
  the cSPIKE column is the value `tests/test_sync_detect.py` asserts to 1e-9
  against MATLAB reference output, so both numbers are checkable from the
  repo.
- Deliberately left out: a third row at `max_tau=1e-6`, where PySpike gives
  0.3119 against our 0.0156. Our port is only validated against cSPIKE at
  0.25 s / 0.5 s / uncapped, so the 1 µs figure would be our extrapolation
  rather than a reference value — the synthetic repro above makes the same
  point without leaning on an unvalidated number.
- The repo link assumes bugarach stays public at that path.
