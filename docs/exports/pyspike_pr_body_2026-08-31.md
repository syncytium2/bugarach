### Summary

Since 0.8.0, `max_tau` has had no effect on any pair of spikes that each have a neighbour on both sides in their own train — call such a pair *interior*, and it is most pairs in most recordings. On two six-spike trains where cSPIKE returns 3/6 at its `max_dist = 0.25`, PySpike at `max_tau = 0.25` returns 5/6 — and returns that same 5/6 at 0.35, and again at 1 µs.

In `get_tau`, `max_tau` seeds each of the four neighbouring ISI slots, and each slot is overwritten as soon as that neighbour exists. All four are overwritten exactly when the pair is interior to both trains, and the cap is then never compared against the window at all.

The docstring — all fourteen copies of it — still promises otherwise:

> `:param max_tau:` Maximum coincidence window size. If 0 or `None`, the
> coincidence window has no upper bound.

This PR restores the clamp that 0.7.0 applied, and adds the regression test that would have caught its loss.

### Thomas Kreuz reproduced this and asked for the PR

I wrote to Thomas Kreuz before filing anything, since the same parameter is `max_dist` in cSPIKE and whether a hard cap is still wanted is a question about the measure rather than about this library. He replied by email on 2026-08-31, copying you. He had reproduced it independently, on two trains of his own:

```matlab
spikes{1} = [0 1   3   5   7   9  ];
spikes{2} = [0 1.1 3.2 5.3 7.4 9.5];
```

The six pairs are separated by 0, 0.1, 0.2, 0.3, 0.4 and 0.5 s. In cSPIKE, `max_dist = 0.25` gives 3/6 — the first three pairs match — and `max_dist = 0.35` gives 4/6. **PySpike returns 5/6 for both.** Every pair except the last is admitted regardless of the cap.

His diagnosis, in his words: *"it indeed seems that we just forgot to track tau_max within the new get_tau function in v0.8.0."* And on the fix: *"So this should clearly be fixed and I am happy with your suggested correction. Please go ahead with sending the PR to Mario."*

What he saw was the one-sentence description of the fix in my note: bound the returned window by half the value `get_tau` is handed, because that value is already twice the user's cap (the `true_max` of the section below). The diff, the test and the caveats are new to him too, so his agreement covers the direction and not the details.

I then applied the patch and re-ran his example: PySpike returns **0.500000** and **0.666667**, matching the cSPIKE figures he quoted.

### Smallest reproduction

Kreuz's example is the clearest statement of the *effect*. This one is the smallest case that exposes the *cause*, because the arithmetic under it is short enough to write out in full.

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
t=  77.3  coincident=1     <- 7.7 s apart, under a 0.25 s cap
t=  85.0  coincident=1     <-
t= 300.0  coincident=0
t= 534.4  coincident=0
t= 600.0  coincident=0
```

Two spikes 7.7 s apart are coincident under a 0.25 s cap. All of the arithmetic comes from the four ISIs bracketing that pair:

```
                  mP1 = 36.9              mF1 = 457.1
             |<---------------->|  |<------------------------->|
train a  ----*------------------*--|---------------------------*----
            40.4              77.3 |                         534.4
                                   | gap = 7.7 s
train b  ---------*----------------|--*--------------*-------------
                 58.8              | 85.0          300.0
             |<--------------->|   |<-------------->|
                  mP2 = 26.2            mF2 = 215.0

window returned = min(36.9, 457.1, 26.2, 215.0) / 2 = 13.1 s
max_tau         = 0.25 s   <- seeds all four slots, all four overwritten, never reached

7.7 < 13.1  =>  coincident
```

### The cap is inert across six orders of magnitude

```python
import numpy as np, pyspike

rng = np.random.default_rng(0)
edges = (0.0, 600.0)                       # seconds
a, b = (pyspike.SpikeTrain(np.sort(rng.uniform(*edges, 60)), edges)
        for _ in range(2))                 # mean ISI ~10 s

print(" max_tau   SPIKE-Sync   directionality")
for max_tau in (None, 1.0, 0.25, 1e-6):
    print(f"{str(max_tau):>8}   {pyspike.spike_sync(a, b, max_tau=max_tau):10.4f}"
          f"   {pyspike.spike_directionality(a, b, max_tau=max_tau):13.6f}")
```

```
 max_tau   SPIKE-Sync   directionality
    None       0.3500        -0.016667
     1.0       0.3333         0.000000
    0.25       0.3333         0.000000
   1e-06       0.3333         0.000000
```

The `None` row differs, but not because the cap works on the body of the trains: it comes from the spikes at the trains' ends, the only ones where a missing neighbour lets the default survive — here just one such pair moves. Sweeping `max_tau` densely finds exactly one transition, at the 1.268 s gap between the final pair of spikes; below it every positive value returns 0.3333, above it the uncapped 0.3500. (`max_tau=0`, like `None`, means no cap.)

**`MRTS > 0` opens a second route past the cap, this time at the edges.** `MRTS` — the minimum relevant time scale of Satuvuori et al. 2017, which stops short-ISI stretches producing spuriously narrow windows — is passed to the same `get_tau`. `Interpolate(a, b, t)` is bounded above by `b`, so a seeded slot arriving in that position still bounds the result; but a slot arriving as the *first* argument does not, and the interpolation can walk straight past it. So under `MRTS > 0` the cap survives at some edge spikes and leaks at others. A case you can run — it is `test_max_tau_bounds_an_mrts_raised_window` in the new test file:

```python
a = pyspike.SpikeTrain([0.0, 0.1, 2.1, 2.2, 4.2, 4.3], 6.0)
b = pyspike.SpikeTrain([0.4, 0.5, 2.5, 2.6, 4.6, 4.7], 6.0)
# nearest cross-train pair is 0.3 apart, so a 0.2 cap should admit nothing
pyspike.spike_sync(a, b, max_tau=0.2, MRTS=2.0)   # 0.166667 shipped, 0.0 patched
```

### Scope

`get_tau` is called from 14 sites in `cython_profiles.pyx` (4), `cython_directionality.pyx` (8) and `cython_distances.pyx` (2), and from 8 more in the pure-Python backend. Every one of the 22 passes `true_max`. So the affected surface is wider than SPIKE-Sync:

- `spike_sync` and its `_bi` / `_multi` / `_profile` / `_matrix` forms, plus `filter_by_spike_sync`
- the three `spike_directionality` entry points
- the six `spike_train_order` entry points
- `optimal_spike_train_sorting`, which reaches them through `spike_directionality_matrix` rather than calling `get_tau` itself

For scale: on a 2670-event recording of ours at a 0.25 s cap, the shipped code reports **4.5× the synchrony the capped definition allows** — 0.3133 against 0.0696. The numbers behind that are at the end, under *what the inert cap costs downstream*.

### Cause

`pyspike/cython/cython_get_tau.pyx`, and the same logic in `pyspike/cython/python_backend.py`. The parameter named `max_tau` here receives `true_max` — the recording span, or twice the user's cap when that doubled value is smaller. This is why the patch bounds by `max_tau/2.` rather than `max_tau`. Annotations marked `<-`:

```cython
cdef double mF1 = max_tau        # <- only a default
cdef double mP1 = max_tau
cdef double mF2 = max_tau
cdef double mP2 = max_tau

if i < len(spikes1)-1 and i > -1:
    mF1 = (spikes1[i+1]-spikes1[i])      # <- overwritten, uncapped
if j < len(spikes2)-1 and j > -1:
    mF2 = (spikes2[j+1]-spikes2[j])
if i > 0:
    mP1 = (spikes1[i]-spikes1[i-1])
if j > 0:
    mP2 = (spikes2[j]-spikes2[j-1])

mF1, mF2, mP1, mP2 = mF1/2., mF2/2., mP1/2., mP2/2.
...                              # <- MRTS /= 4. elided

if i<0 or j<0 or spikes1[i] <= spikes2[j]:
    s1F = Interpolate(mP1, mF1, MRTS)
    s2P = Interpolate(mF2, mP2, MRTS)
    return fmin(s1F, s2P)        # <- max_tau never enters
```

One slot per neighbour, and each is claimed by that neighbour if it exists:

| slot | seeded with | overwritten when | value in the 7.7 s example above |
| --- | --- | --- | --- |
| `mP1` | `max_tau` | train a has an earlier spike | 36.9 |
| `mF1` | `max_tau` | train a has a later spike | 457.1 |
| `mP2` | `max_tau` | train b has an earlier spike | 26.2 |
| `mF2` | `max_tau` | train b has a later spike | 215.0 |

At the default `MRTS=0`, `Interpolate(a, b, 0)` returns `min(a, b)`, so the function reduces to the minimum of the four half-ISIs — a quantity `max_tau` never touches. **MRTS does not substitute for a cap**: `Interpolate` is bounded above by its second argument, the half-ISI facing the other spike, so raising MRTS can only move the window up toward that bound, never down.

The clamp existed until 0.8.0. 0.7.0 carried `get_tau` separately in each of the three `.pyx` files and again in `python_backend.py`, and those copies ended with the clamp; 0.8.0 consolidated the Cython side into one shared implementation that does not carry it, and the pure-Python copy lost it too — so this was not a single edit to a single consolidated function. In 0.7.0 the seed and the cap were separate parameters, and `max_tau` there was the user's raw value rather than today's `true_max`:

```cython
    m *= 0.5
    if max_tau > 0.0:
        m = fmin(m, max_tau)
    return m
```

| version | `get_tau` | the cap |
| --- | --- | --- |
| ≤ 0.7.0 | three per-file copies | `if max_tau > 0.0: m = fmin(m, max_tau)` |
| 0.8.0 (PyPI 2023-07-14) | consolidated into one | absent from the consolidated copy |
| 0.9.0 | same | still absent |

Kreuz's reading, above, is that this was lost in the consolidation rather than removed deliberately. Either way the docstring and the code disagree today, and this PR moves the code.

### Is a cap still wanted?

Yes, and not only on Kreuz's say-so. He confirms the parameter is one his group still uses — their approach is *"to give the user options and not impose one specific variant over any other"*, so the parameter-free measure stays the default and `max_tau` is an option that has to work. He puts its absence from his review ([Biol Cybern 120:21](https://doi.org/10.1007/s00422-026-01045-5), 2026) down to space rather than to a withdrawal, and points at Kreuz et al. 2017 and the two recent latency-correction papers as where it is actually used. All three are in the table below.

<details>

<summary><b>Where the cap comes from</b> — five papers, cSPIKE, and PySpike ≤ 0.7.0</summary>

The measure itself is deliberately parameter-free, which makes it worth showing that the cap is not an invention of the implementations:

| a global cap? | source | what it says |
| --- | --- | --- |
| **yes — as an option** | Quian Quiroga, Kreuz & Grassberger 2002, Eq. 4 ([Phys Rev E 66:041904](https://doi.org/10.1103/PhysRevE.66.041904)) | *"…one could also make other choices, e.g. by taking τij smaller than in Eq.(4) or by using τ′ij=min{τ,τij}."* Then: *"In the following we shall suppress the dependence on τ, understanding that all formulas apply for both variants."* |
| no | Kreuz, Mulansky & Bozanic 2015, Eq. 19 ([J Neurophysiol 113:3432](https://doi.org/10.1152/jn.00848.2014)) | the parameter-free default: min of the four surrounding half-ISIs |
| no | Satuvuori et al. 2017, Eqs. 17–18 ([J Neurosci Methods 287:25](https://doi.org/10.1016/j.jneumeth.2017.05.028)) | MRTS, which puts a floor under the window rather than a ceiling over it |
| **yes — `τmax`** | Kreuz, Satuvuori, Pofahl & Mulansky 2017 ([New J Phys 19:043028](https://doi.org/10.1088/1367-2630/aa68c3)) | *"For some applications it might be appropriate to additionally introduce a maximum coincidence window τmax as a parameter."* Used in §3.3 with τmax = 9 months |
| **yes — `τmax`** | Kreuz et al. 2022 ([J Neurosci Methods 381:109703](https://doi.org/10.1016/j.jneumeth.2022.109703)) | *"…combining the time-scale independent coincident detection with a time-scale dependent upper limit."* |
| **yes — `τmax`** | Mariani et al. 2025 ([J Neurosci Methods 416:110378](https://doi.org/10.1016/j.jneumeth.2025.110378), [arXiv:2410.15018](https://arxiv.org/abs/2410.15018)) | Fig. 11 applies *"a maximum time interval of 2.5ms between matched spikes"* to the gerbil data, alongside a Spike Train Order threshold, and reports that it *"reduces the number of mismatched spikes […] considerably"* |
| yes — `max_dist` | cSPIKE | cSPIKE v1.5 `Spiketrains.cpp:453` requires `\|Δt\| < TAUij` **and** `\|Δt\| < max_dist` |
| yes — `max_tau` | PySpike ≤ 0.7.0 | `if max_tau > 0.0: m = fmin(m, max_tau)` |
| **no** | PySpike ≥ 0.8.0 | seeds four ISI slots, all overwritten for an interior pair |

`min{τ, τij}` is in the paper that introduced the adaptive window, as an explicitly optional variant, and it is named and used in the SPIKE-order work fifteen years later. Neither the paper that defines SPIKE-Sync nor the one that introduces MRTS carries it — neither is about bounding the window. For `max_dist > 0`, cSPIKE's two conditions are exactly `|Δt| < min(TAUij, max_dist)`, which is what the patch computes. That reading is from the C++ in a checkout we run — `if (|Δt| < TAUij)` guarding `if (((max_dist < 0) || (|Δt| < max_dist)) && ...)`, where `max_dist < 0` is the disabled sentinel — and it is corroborated by our port matching cSPIKE's own per-spike profile to 1e-9 at finite caps on 30 dense trains, as described under *Environment*.

</details>

### The fix

`get_tau` receives `true_max`, so the bound the patch applies is half of that value. In `pyspike/cython/cython_get_tau.pyx`:

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

and the same two returns in `pyspike/cython/python_backend.py`, which uses the builtin `min` rather than `fmin`:

```diff
@@ -361,11 +361,11 @@ def get_tau(spikes1, spikes2, i, j, max_tau, MRTS):
     if i<0 or j<0 or spikes1[i] <= spikes2[j]:
         s1F = Interpolate(mP1, mF1, MRTS)
         s2P = Interpolate(mF2, mP2, MRTS)
-        return min(s1F, s2P)
+        return min(min(s1F, s2P), max_tau/2.)
     else:
         s1P = Interpolate(mF1, mP1, MRTS)
         s2F = Interpolate(mP2, mF2, MRTS)
-        return min(s1P, s2F)
+        return min(min(s1P, s2F), max_tau/2.)
```

No `max_tau > 0` guard is needed. The two cases:

| user passes | callers set `true_max` to | new bound | vs 0.7.0 at `MRTS=0` |
| --- | --- | --- | --- |
| `None`, `0`, negative | `t_end - t_start` | half the recording span | same function |
| `τ > 0` | `min(span, 2τ)` | `min(span/2, τ)` | same function |

Bounding at half the span is what 0.7.0 did by seeding `m` with `interval` before halving, so at `MRTS = 0` the patched function and 0.7.0's are the same function: both land on `min(interval/2, ISI/2 over existing neighbours)`, further clamped at the user's cap when one was asked for. `(2·max_tau)/2 == max_tau` is exact in IEEE-754 for every double below the overflow threshold, so the boundary sits on the user's value to the ULP.

Patched, the sweep above becomes:

```
 max_tau   as shipped   with the patch
    None       0.3500          0.3500
     1.0       0.3333          0.1833
    0.25       0.3333          0.0500
   1e-06       0.3333          0.0000
```

The score becomes monotone in `max_tau` for SPIKE-Sync, where it follows from per-pair monotonicity in the window. It does **not** hold for `spike_directionality`, which is signed and resamples which pairs contribute: on these same trains the patched values run −0.016667 uncapped, −0.050000 at 1.0, +0.016667 at 0.25 and 0.000000 at 1 µs.

### Does `max_tau` override an MRTS-raised window?

I believe this is forced rather than chosen, but it is your library and your call. **Kreuz, Satuvuori, Pofahl & Mulansky 2017** (New J Phys 19:043028) introduces τmax in §2.1 alongside the adaptive window, not instead of it, and applies it to the El Niño data of §3.3; Appendix B puts it plainly — *"We still use the adaptive coincidence detection from Eq. 1 but define a maximum coincidence window τmax"*, there set to 9 months. Its purpose is a hard physical constraint, a propagation speed, the kind that should not be defeated by a resolution floor. **Satuvuori et al. 2017** (J Neurosci Methods 287:25), which introduced MRTS, already pairs it with its own ISI ceiling: *"each side is limited to half the ISI even if the threshold is larger."*

And because `min` is associative and commutative, applying the cap per side inside the MRTS expression or once outside it gives the same function — so the placement in this patch is not one choice among several. Flagging it because it is a real behaviour change under `MRTS > 0`, not because I think it is open.

### The regression test

`test/test_max_tau.py` is new here, and it exists because nothing in the suite passes `max_tau` for a pair of spikes that are each interior to their own train. The existing `max_tau` assertion (`test/test_distance.py:184`) scores a three-spike train against `SpikeTrain([2.1], 4.0)`; the one-spike partner leaves two slots seeded, so the cap stays live and the assertion passes either way. It is untouched and still green. (`test_MRTS.py:20` also binds a `max_tau` local, but never passes it to anything.)

The new file uses Kreuz's two trains, whose six pair separations are 0, 0.1, 0.2, 0.3, 0.4 and 0.5 s. Each cap therefore admits exactly one more pair, and every expected value is a sixth countable by hand off the two spike lists — no fixture, no reference file:

| pair separation (s) | 0 | 0.1 | 0.2 | 0.3 | 0.4 | 0.5 |
| --- | --- | --- | --- | --- | --- | --- |
| `max_tau` (s) | 0.05 | 0.15 | 0.25 | 0.35 | 0.45 | 0.55 |
| as shipped | 5/6 | 5/6 | 5/6 | 5/6 | 5/6 | 6/6 |
| with the patch | 1/6 | 2/6 | 3/6 | 4/6 | 5/6 | 6/6 |

The last two columns agree; only the strictly-increasing check separates them. The first column is set by the pair at separation 0, which the equal-times branch admits without calling `get_tau` at all — so that cell is insensitive to the cap rather than a test of it.

Six tests: the staircase above; `spike_sync_profile` under a 0.25 s cap; the same bound reaching `spike_directionality`; the staircase's strict increase rather than mere non-decrease (the weaker form passes on the current code, since the shipped row does rise once, at the edge pair); that `max_tau` of `0` and `None` remain no-ops; and one `MRTS > 0` case, since that is where the cap leaks worst.

Five of the six fail on 0.9.0 as shipped and pass with the patch, compiled and pure-Python alike. The sixth is the `0`/`None` no-op, which passes either way — it is there to keep it passing. With them the suite is **56 tests over 13 collecting files**, against 50 over 12 today. I ran it from the source root against a build of the patched tree, and separately against an installed unpatched 0.9.0 from a directory outside the tree.

### What changes for existing users

Nothing, when `max_tau` is `0` or `None` and `Reconcile` is left at its default — verified over the full suite and ~12,600 probes comparing shipped against patched output on both backends. (`Reconcile` is the flag that sorts, de-duplicates and trims each train to the common interval before analysis; it defaults to on.) Four things do change, and all four follow from the cap working:

- **A boundary now exists.** `|Δt| == max_tau` is no longer a coincidence, which matches cSPIKE's strict `|Δt| < max_dist` and 0.7.0's behaviour.
- **`Reconcile=False`.** A half-ISI can exceed the recording span, and 0.9.0 returns it where this bounds it at half the span — a restoration of 0.7.0 rather than a new hazard, but it moves numbers: fuzzing 3,000 pairs with spikes drawn well outside the interval, 23 `spike_sync` values differed, always downward, sometimes to zero (0.5714 → 0.2857, 0.2857 → 0.0000); the signed measures move both ways, as they do under any tightening of the window. `test_reconcile.py` passes either way.
- **A working cap filters more aggressively, and empty trains are a rough landing.** `filter_by_spike_sync` with a tight `max_tau` returns empty trains on inputs where it previously returned a few spikes. Empty trains are already reachable on 0.9.0 — a tight cap plus a high threshold does it today, without this patch — so the hazard is pre-existing, but the patch makes it much easier to hit. `spike_directionality` raises `ZeroDivisionError` on an empty train and `spike_sync` returns 1.0. Happy to open that separately; it is not in scope here.
- **`optimal_spike_train_sorting` can return a different permutation.** On five jittered synfire trains it returns `[0,1,2,3,4]` with synfire indicator 50.0 as shipped at `max_tau = 0.25`, and `[1,2,4,0,3]` with 5.0 patched. At `max_tau = 0.01` the directionality matrix underneath it is **all zero**, so the ordering handed back is arbitrary rather than meaningful — worth knowing, since this output is a permutation people publish. Both are the cap doing its job on a matrix that no longer has evidence in it, but neither is a number quietly shifting.

<details>

<summary><b>What the inert cap costs downstream</b> — a 2670-event recording at a 0.25 s cap</summary>

We hit this porting the cSPIKE SPIKE-synchronization stack to Python and cross-checking against both cSPIKE reference output and PySpike. Here is the cost on a synthetic 30-train recording — simulated calcium event times, 2670 events at 2362 distinct times after dropping within-train duplicates, median ISI 31 s — from [our committed test fixture](https://github.com/syncytium2/bugarach/blob/6eafdb69cd3c3ed4694dcdddcf5978aa84af6636/tests/fixtures/synth_fastcal_s1.mat). Both columns are `pyspike.spike_sync`, so this is PySpike against itself:

| `max_tau` | as shipped | with the patch |
| --- | --- | --- |
| uncapped | 0.3235 | 0.3235 |
| 0.25 s | 0.3133 | 0.0696 |
| 1 µs | 0.3119 | 0.0156 |

At a 0.25 s cap the shipped code reports 4.5× the synchrony the capped definition allows. The 1 µs row does not reach zero because this recording has many exactly simultaneous cross-train events, and the equal-times fast path admits those without consulting the window.

Our port computes the same three-term minimum this patch restores, so its agreement with the patched column is arithmetic rather than a second measurement — it reproduces that column bit-for-bit, which is what you would expect of a transcription. **The independent anchor is one layer down, and it is cSPIKE itself.** The port's per-spike profile is tested against cSPIKE's own MATLAB output at `rtol = atol = 1e-9` — the full 2670-point profile, at a 0.25 s cap, a 0.5 s cap and uncapped, on both streams. So the semantics this patch restores are the semantics we already hold cSPIKE to, at finite caps, on 10,680 per-spike values. Meanwhile our cross-check *against PySpike* had to be run uncapped, precisely because the capped regime disagreed — which is how we found this in the first place. [`sync.py`](https://github.com/syncytium2/bugarach/blob/6eafdb69cd3c3ed4694dcdddcf5978aa84af6636/src/bugarach/detectors/sync.py) is the port; [`test_sync_detect.py`](https://github.com/syncytium2/bugarach/blob/6eafdb69cd3c3ed4694dcdddcf5978aa84af6636/tests/test_sync_detect.py) is the parity test.

</details>

### Environment

PySpike 0.9.0 (pip, compiled Cython backend), NumPy 2.5.2, Python 3.14.5, macOS; built and run on that platform only. The pure-Python backend agrees on every number quoted here, as shipped and patched both, and the two `Interpolate` implementations agree on 200k random triples, so none of this is a build artifact.

**On cSPIKE.** cSPIKE runs on our MATLAB side, not in the Python package — that is the division of labour here, and the Python port is a consumer of what MATLAB emits. Under MATLAB R2025b, cSPIKE's own `SpikyRun` and `computeAdaptiveProfile` generate the reference the port is tested against: [`gen_ref_sync.m`](https://github.com/syncytium2/bugarach/blob/6eafdb69cd3c3ed4694dcdddcf5978aa84af6636/tools/matlab_ref/gen_ref_sync.m) is the generator and [`ref_sync_synth.json`](https://github.com/syncytium2/bugarach/blob/6eafdb69cd3c3ed4694dcdddcf5978aa84af6636/tests/fixtures/ref_sync_synth.json) the committed output. It is the **raw per-spike profile — 2670 points per condition** — at a 0.25 s cap, a 0.5 s cap and uncapped, on both of our event streams, and [`test_sync_detect.py`](https://github.com/syncytium2/bugarach/blob/6eafdb69cd3c3ed4694dcdddcf5978aa84af6636/tests/test_sync_detect.py) holds the port to it at `rtol = atol = 1e-9` in all four. The `max_dist` semantics in the table are read from the C++ in that same checkout. The two figures in the Kreuz section are his, quoted from his mail rather than re-run here.

### What is in this PR

- `pyspike/cython/cython_get_tau.pyx` — bound both returns by `max_tau/2.`
- `pyspike/cython/python_backend.py` — the same two returns, with the builtin `min`.
- `test/test_max_tau.py` — the six tests above.

Together the first two cover every caller on both backends; `directionality_python_backend.py` imports `get_tau` from `python_backend`. No public signature changes and no new parameters. The three behaviour changes are listed above.
