---
status: open
filed: 2026-08-11
---

# File the PySpike max_tau bug upstream

Report to PySpike (`mariomulansky/PySpike`) that its `max_tau` coincidence-window
cap has no effect: in the MRTS-era `get_tau`, the cap enters only as the default
for missing edge-neighbor ISIs — whenever all four surrounding ISIs exist,
`max_tau` is ignored, so spikes seconds apart count as coincident under a 0.25 s
cap.

**Verified unreported as of 2026-08-11** (searched their tracker: no issue
touches the cap). **Re-verified 2026-08-17**: still nothing on the tracker (open
items are #88 interval edges, #85 numpy 2.x), and `master`'s
`cython_get_tau.pyx` still never takes a minimum against `max_tau`. 0.9.0 is the
newest version on PyPI and exists upstream as the `v0.9.0` tag (PR #87,
2026-05-11); GitHub's Releases page still tops out at 0.8.0.

**The regression is older than the draft first said.** 0.7.0 still ends `get_tau`
with `if max_tau > 0.0: m = fmin(m, max_tau)`; 0.8.0 — the MRTS release, October
2023 — does not. So the cap has been inert for nearly three years, not since
0.9.0.

## Process

Draft the issue text below; **Tony reviews before anything is posted**
(external communication). After filing, add the issue URL here and flip status.

**Before posting**: land this branch, then repoint all **three** repo links
(fixture, `sync.py`, `test_sync_detect.py`) from `main` to the landed commit SHA.
The pinned regression test they reference does not exist on `main` yet.

---

## Draft issue text (for review — not yet posted)

**Title:** `max_tau` has no effect except at spike-train edges (regression since 0.8.0)

### Summary

`spike_sync` returns the same number for `max_tau` of 1.0, 0.25 and 1e-6 on
trains whose mean ISI is 10 s. On those data a 1 µs coincidence window should
report no coincidences at all; it reports SPIKE-Sync 0.33. On a real 30-train
recording at a 0.25 s cap, the effect is a 4.5× overstatement of synchrony.

The cause is in `get_tau`: `max_tau` is used only as the initial value for each
of the four neighboring ISIs, and each is overwritten as soon as that neighbor
exists. The returned window is the minimum of the interpolated half-ISIs, and
`max_tau` is never compared against it. Only spikes at the start or end of a
train — where a neighbor is genuinely missing — still see the cap.

### Smallest reproduction

```python
import pyspike

# The middle pair is 7.7 s apart. The outer spikes exist only to give that
# pair a neighbor on each side -- that is what triggers the bug.
a = pyspike.SpikeTrain([40.4, 77.3, 534.4], (0, 600))   # seconds
b = pyspike.SpikeTrain([58.8, 85.0, 300.0], (0, 600))   # seconds

x, y = pyspike.spike_sync_profile(a, b, max_tau=0.25).get_plottable_data()
for t, c in zip(x, y):
    print(f"t={t:6.1f}  coincident={c:.0f}")
```

```
t=   0.0  coincident=0
t=  40.4  coincident=0
t=  58.8  coincident=0
t=  77.3  coincident=1
t=  85.0  coincident=1
t= 300.0  coincident=0
t= 534.4  coincident=0
t= 600.0  coincident=0
```

Two spikes 7.7 s apart are coincident under a 0.25 s cap. The arithmetic, all of
it from the ISIs surrounding that pair (spacing not to scale):

```
train a:    40.4 ─────── 77.3 ────────────────── 534.4
train b:         58.8 ─────── 85.0 ── 300.0

pair under test:  a@77.3 vs b@85.0                       gap = 7.7 s
surrounding ISIs: 36.9 (a), 457.1 (a), 26.2 (b), 215.0 (b)
window returned = min(36.9, 457.1, 26.2, 215.0) / 2    = 13.1 s
max_tau                                                = 0.25 s  <- never consulted

7.7 s < 13.1 s  =>  coincident
```

With the cap applied the window would be 0.25 s, and the pair would not be
coincident.

### The cap is inert across six orders of magnitude

```python
import numpy as np, pyspike

rng = np.random.default_rng(0)
edges = (0.0, 600.0)                       # seconds
a, b = (pyspike.SpikeTrain(np.sort(rng.uniform(*edges, 60)), edges)
        for _ in range(2))                 # mean ISI ~10 s

print(" max_tau   SPIKE-Sync")
for max_tau in (None, 1.0, 0.25, 1e-6):
    print(f"{str(max_tau):>8}   {pyspike.spike_sync(a, b, max_tau=max_tau):.4f}")
```

```
 max_tau   SPIKE-Sync
    None   0.3500
     1.0   0.3333
    0.25   0.3333
   1e-06   0.3333
```

Every finite `max_tau` returns exactly the same value. The `None` row differs,
but that difference is not the cap working: it comes from the spikes at the start
and end of each train, the only ones where a missing neighbor lets the default
survive. So a finite cap is not quite the uncapped answer — it is the uncapped
answer everywhere except the train edges.

This is also why casual testing misses the bug — with a single spike per train
there are no neighbors, so the defaults survive, the cap applies, and the answer
is correct.

### Scope

`get_tau` is called from 14 sites across `cython_profiles.pyx`,
`cython_directionality.pyx` and `cython_distances.pyx`, so the affected public
API is wider than SPIKE-Sync alone:

- `spike_sync`, `spike_sync_multi`, `spike_sync_profile` (bivariate and
  multivariate), `spike_sync_matrix`, `filter_by_spike_sync`
- `spike_directionality`, `spike_directionality_matrix`,
  `spike_directionality_values`
- `spike_train_order`, `spike_train_order_bi`, `spike_train_order_multi`, and
  the three corresponding `..._profile` functions
- `optimal_spike_train_sorting`

On the same two trains as above, `spike_directionality` returns `-0.016667`
uncapped and `0.0` for `max_tau` of 1.0, 0.25 and 1e-6 alike. On three such
trains, `optimal_spike_train_sorting` returns a different permutation uncapped
than it does for any finite cap.

### Diagnosis

`pyspike/cython/cython_get_tau.pyx` (same logic in
`pyspike/cython/python_backend.py`), with my annotations marked `<--`:

```cython
cdef double mF1 = max_tau        # <-- only a default
cdef double mP1 = max_tau
cdef double mF2 = max_tau
cdef double mP2 = max_tau

if i < len(spikes1)-1 and i > -1:
    mF1 = (spikes1[i+1]-spikes1[i])      # <-- overwritten, uncapped
if j < len(spikes2)-1 and j > -1:
    mF2 = (spikes2[j+1]-spikes2[j])
if i > 0:
    mP1 = (spikes1[i]-spikes1[i-1])
if j > 0:
    mP2 = (spikes2[j]-spikes2[j-1])

mF1, mF2, mP1, mP2 = mF1/2., mF2/2., mP1/2., mP2/2.
...
return fmin(s1F, s2P)            # <-- max_tau never enters
```

With the default `MRTS=0` (minimum relevant time scale), `Interpolate(a, b, 0)`
returns `min(a, b)`, so the function reduces to the minimum of the four
half-ISIs — a quantity `max_tau` never touches.

**MRTS does not substitute for the cap.** `Interpolate` can only raise its result
toward the larger half-ISI as MRTS grows, never lower it, so no MRTS value bounds
the window from above and there is no way to express a hard cap with it.

Two things say the bound was meant to survive the MRTS rewrite. The callers still
compute a doubled `max_tau` and pass it in:

```cython
cdef double true_max = t_end - t_start
if max_tau > 0:
    true_max = fmin(true_max, 2*max_tau)
```

That factor of 2 only makes sense as a bound the halving step turns back into
`max_tau`. And the rewrite dropped the cap while keeping the docstring that
promises it:

> `max_tau` — Maximum coincidence window size. If 0 or `None`, the coincidence
> window has no upper bound.

The change landed in 0.8.0. 0.7.0's `get_tau` still ends with:

```cython
if max_tau > 0.0:
    m = fmin(m, max_tau)
```

### Expected behavior

```
window = min(ISI before a, ISI after a, ISI before b, ISI after b) / 2   # 0.9.0
window = min(the above, max_tau)                                        # expected
```

To be clear about provenance, since the published measure is deliberately
parameter-free: Eq. 19 of Kreuz, Mulansky & Bozanic (*SPIKY*, J Neurophysiol
113:3432, 2015) defines the coincidence window as the minimum of the four
surrounding half-ISIs with no upper bound, and Satuvuori et al. (J Neurosci
Methods 287:25, 2017) add MRTS as a *lower* bound. The cap is not in either
paper.

It is in all three implementations. cSPIKE, the reference implementation from
Kreuz's group, takes the same parameter under the name `max_dist` — a documented
argument of `SPIKEsynchro` and `AdaptiveSPIKEsynchro`, defaulting to 10^12 — and
applies it in `AdaptiveCoincidence` as a second condition on top of the adaptive
window:

```cpp
if( std::abs(spiketime-closestSpike) < TAUij )
{
    if (((max_dist < 0) || (std::abs(spiketime-closestSpike) < max_dist)) && ...
```

Requiring `|Δt| < TAUij` and `|Δt| < max_dist` is exactly requiring
`|Δt| < min(TAUij, max_dist)`, so cSPIKE's semantics and the patch below agree.
PySpike's own docstring promises the same bound, and PySpike implemented it
through 0.7.0. Only 0.8.0 onward disagrees.

### Suggested fix

`get_tau`'s parameter named `max_tau` actually receives `true_max`, which the
callers set to twice the user's value (or the recording duration, whichever is
smaller) — so the bound to apply is half of it. In
`pyspike/cython/cython_get_tau.pyx`:

```diff
     if i<0 or j<0 or spikes1[i] <= spikes2[j]:
         s1F = Interpolate(mP1, mF1, MRTS)
         s2P = Interpolate(mF2, mP2, MRTS)
-        return fmin(s1F, s2P)
+        return fmin(fmin(s1F, s2P), max_tau/2.)
     else:
         s1P = Interpolate(mF1, mP1, MRTS)
         s2F = Interpolate(mP2, mF2, MRTS)
-        return fmin(s1P, s2F)
+        return fmin(fmin(s1P, s2F), max_tau/2.)
```

and the same in `pyspike/cython/python_backend.py`, which uses the builtin rather
than `fmin`:

```diff
-        return min(s1F, s2P)
+        return min(min(s1F, s2P), max_tau/2.)
...
-        return min(s1P, s2F)
+        return min(min(s1P, s2F), max_tau/2.)
```

Those two files cover every caller in both backends —
`directionality_python_backend.py` imports `get_tau` from `python_backend`.

No `max_tau > 0` guard is needed: when the user passes 0 or `None` the callers
set `true_max = t_end - t_start`, and no half-ISI can exceed half the recording
duration, so the new minimum is never the binding term. Running the sweep above
against a patched pure-Python backend:

```
 max_tau   as shipped   with the patch
    None       0.3500          0.3500
     1.0       0.3333          0.1833
    0.25       0.3333          0.0500
   1e-06       0.3333          0.0000
```

The uncapped case is untouched, finite caps become monotone in `max_tau`, and a
1 µs window reaches 0 — the smallest cross-train gap in these data is 0.027 s.
At `MRTS=0` this restores 0.7.0's semantics exactly.

One design question I did not want to decide for you: with `MRTS > 0` this lets
`max_tau` override the MRTS-raised window. That seems right for a hard cap, but
it is your call.

### How we found it

We maintain a Python port of the cSPIKE synchronization stack — cSPIKE being the
MATLAB implementation from Kreuz's group — and cross-check it against both cSPIKE
reference output and PySpike. Uncapped, our port and PySpike agree exactly. At
every cap we tested they diverge, and there our port matches cSPIKE to 1e-9.

On a 30-train, 2670-event synthetic recording with a median ISI of 31 s
([the fixture is public](https://github.com/syncytium2/bugarach/blob/main/tests/fixtures/synth_fastcal_s1.mat)),
comparing `pyspike.spike_sync(trains, max_tau=...)` against the mean of our
port's per-spike coincidence values — on this recording the two agree bit-for-bit
uncapped, which is what makes the capped rows comparable:

| `max_tau` | PySpike 0.9.0 | our port (matches cSPIKE to 1e-9) |
| --- | --- | --- |
| uncapped | 0.3235 | 0.3235 |
| 0.25 s | 0.3133 | 0.0696 |

At the cap, PySpike reports 4.5× more synchrony than the capped definition
allows.

The analysis and the cross-check test:
[`sync.py`](https://github.com/syncytium2/bugarach/blob/main/src/bugarach/detectors/sync.py)
and
[`test_sync_detect.py`](https://github.com/syncytium2/bugarach/blob/main/tests/test_sync_detect.py).

### Environment

PySpike 0.9.0 (pip, compiled Cython backend), NumPy 2.5.2, Python 3.14.5, macOS.
The pure-Python backend gives the same results; I checked that the two
`Interpolate` implementations agree on 200k random triples, so this is not a
build artifact.

Happy to send the fix as a PR with a regression test if that is useful.

---

## Notes for the reviewer (not part of the issue)

- **The patch changed twice during review.** The first draft proposed
  `fmin(tau, max_tau)`, which caps at *twice* the intended window — inside
  `get_tau` the parameter named `max_tau` is the already-doubled `true_max`. The
  blind re-review then caught that the corrected diff, applied where the draft
  said to apply it, raises `NameError` in `python_backend.py`, which imports only
  numpy and uses the builtin `min`. Both backends now get their own diff, and the
  patched sweep in the issue is the tested result.
- **The regression is from 0.8.0, not 0.9.0.** The first draft said 0.9.0 because
  that is the version we run. 0.7.0 has the cap and 0.8.0 does not, so the report
  now names the release that dropped it and the maintainer has a bisect boundary.
- **The citation was re-attributed twice, and the first correction overshot.**
  The original draft cited Kreuz et al. 2015 for the capped formula; that paper
  says the opposite — SPIKE-synchronization is "parameter- and scale-free" and its
  Eq. 19 has no upper bound — and the recipient co-authored it. The first fix
  swung to "`max_tau` is PySpike's own addition", which is also false and which
  this report's own cSPIKE-parity section contradicted. cSPIKE has the same
  parameter as `max_dist` (`cSPIKE_mac/SpikeTrainSet.m:187` and its documented
  API; applied in `cSPIKEmex/Spiketrains.cpp:453` as a second condition on top of
  the adaptive window). The final version says what is actually true and is the
  strongest of the three: absent from the papers, present in all three
  implementations, dropped only in 0.8.0.
- **Scope was understated.** `get_tau` has 14 call sites across three `.pyx`
  files, not the four SPIKE-Sync entry points originally listed; the
  directionality and spike-train-order APIs take `max_tau` too and are equally
  affected.
- **The 0.25 s row is the operating point our detectors run at.** Our port's
  per-spike profile at that cap is what `tests/test_sync_detect.py` asserts to
  1e-9 against cSPIKE MATLAB reference output, so both columns are checkable from
  the repo.
- **Deliberately left out**: a third row at `max_tau=1e-6`, where PySpike gives
  0.3119 against our 0.0156. Our port is validated against cSPIKE only at
  0.25 s / 0.5 s / uncapped, so the 1 µs figure would be our extrapolation rather
  than a reference value. The synthetic reproducer makes the same point without
  it.
- **A rendered figure was considered and left out.** The finding is a scalar
  comparison, the ASCII derivation carries all of it, and unlike an image it can
  be quoted in a reply and read in a terminal — where triage happens. The one
  picture-shaped claim (SPIKE-Sync vs `max_tau`, PySpike flat while the capped
  definition falls) has only two validated points, which is a table, not a curve.
  Recorded so a later session does not reopen it.
- **After filing**, the issue URL belongs in `docs/FOUNDATIONS.md` (the PySpike
  bullet at line 49), `README.md` (twice — lines 41 and 76), `tools/sapper.py`'s
  SAP003 message, and `src/bugarach/detectors/__init__.py`. All of them assert
  the bug today with no upstream reference — **and all five call it "PySpike
  0.9.0's" bug, which this report now shows is wrong: it broke in 0.8.0.** Fix the
  version in the same pass as the URL.
- The repo links assume bugarach stays public at that path.
