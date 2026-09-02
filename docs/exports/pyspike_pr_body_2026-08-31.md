### The bug

Since 0.8.0, `max_tau` has no effect on any pair of spikes that each have a neighbour on both sides in their own train.

```python
a = pyspike.SpikeTrain([0.0, 1.0, 3.0, 5.0, 7.0, 9.0], 10.0)
b = pyspike.SpikeTrain([0.0, 1.1, 3.2, 5.3, 7.4, 9.5], 10.0)
```

The six pairs are 0, 0.1, 0.2, 0.3, 0.4, 0.5 s apart. A 0.25 s cap should admit three of them, a 0.35 s cap four. **PySpike returns 5/6 for both**, and for every positive cap down to 1 µs. The docstring, in all fourteen copies, says `max_tau` bounds the window.

### Cause

`get_tau` seeds the four neighbouring-ISI slots with `max_tau` and overwrites each one as soon as that neighbour exists. All four are overwritten exactly when the pair is interior to both trains, and the cap is then never compared against the window:

```cython
cdef double mF1 = max_tau        # <- only a default
...
if i < len(spikes1)-1 and i > -1:
    mF1 = (spikes1[i+1]-spikes1[i])      # <- overwritten, uncapped
...
return fmin(s1F, s2P)            # <- max_tau never enters
```

0.7.0 ended `get_tau` with `if max_tau > 0.0: m = fmin(m, max_tau)`, in each of the three `.pyx` copies and in `python_backend.py`. 0.8.0 consolidated the Cython side into one shared implementation without it, and the pure-Python copy lost it too.

This is not only SPIKE-Sync: `get_tau` has 14 call sites across the three `.pyx` files and 8 more in the pure-Python backend, so `spike_directionality`, `spike_train_order`, `filter_by_spike_sync` and `optimal_spike_train_sorting` are all affected.

### The fix

`get_tau` receives `true_max` — the span, or twice the user's cap when smaller — so the bound is half of it.

```diff
@@ -43,8 +43,8 @@ cdef double get_tau(double[:] spikes1, double[:] spikes2,
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

Same two returns in `python_backend.py` with the builtin `min`. Between them that is every caller on both backends — `directionality_python_backend.py` imports `get_tau` from `python_backend`.

No `max_tau > 0` guard needed: at `0`/`None` the callers set `true_max` to the span, so the bound is half the span, which is what 0.7.0 did by seeding `m` with `interval` before halving. At `MRTS = 0` the patched function and 0.7.0's are identical.

### What changes

Nothing at `max_tau` of `0`/`None` with default `Reconcile` — checked over the suite and ~12,600 shipped-vs-patched probes on both backends. Four things do change, all of them the cap working:

- `|Δt| == max_tau` is no longer a coincidence, matching cSPIKE's strict `<` and 0.7.0.
- `Reconcile=False`: a half-ISI can exceed the span, and 0.9.0 returns it where this bounds it at half the span. Fuzzing 3,000 pairs, 23 `spike_sync` values moved, always down. `test_reconcile.py` passes either way.
- `filter_by_spike_sync` with a tight cap returns empty trains more readily. Empty trains already break `spike_directionality` on 0.9.0 (`ZeroDivisionError`) — pre-existing, happy to file separately.
- `optimal_spike_train_sorting` can return a different permutation; at a very tight cap the directionality matrix is all zero, so the ordering is arbitrary.

Under `MRTS > 0` the cap now also overrides an MRTS-raised window. That looks right — Kreuz et al. 2017 introduces τmax alongside the adaptive window, and Satuvuori's Eqs. 17–18 already cap MRTS at half the ISI — but it is a behaviour change, so I am flagging it.

### Tests

`test/test_max_tau.py` is new, because nothing in the suite passes `max_tau` for a pair interior to both trains. The one existing assertion (`test_distance.py:184`) uses a one-spike partner, which leaves two slots seeded and passes either way; it is untouched and still green.

| pair separation (s) | 0 | 0.1 | 0.2 | 0.3 | 0.4 | 0.5 |
| --- | --- | --- | --- | --- | --- | --- |
| `max_tau` (s) | 0.05 | 0.15 | 0.25 | 0.35 | 0.45 | 0.55 |
| as shipped | 5/6 | 5/6 | 5/6 | 5/6 | 5/6 | 6/6 |
| with the patch | 1/6 | 2/6 | 3/6 | 4/6 | 5/6 | 6/6 |

Six tests: that staircase, the profile at 0.25 s, the bound reaching `spike_directionality`, strict increase, `0`/`None` still a no-op, and one `MRTS > 0` case. Five fail as shipped and pass patched on both backends; the sixth is the no-op invariant.

**56 tests over 13 collecting files, against 50 over 12 today.**

Verified on PySpike 0.9.0, NumPy 2.5.2, Python 3.14.5, macOS only.
