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
touches the cap — closed #14 mentions `max_tau`, but as a units question). **Re-verified 2026-08-17**: still nothing on the tracker (#88,
interval edges, is the only open *issue*; #85 and #47 are open pull requests), and
`master`'s `cython_get_tau.pyx` still has no final clamp — `max_tau` survives only
as a seed that any interior spike overwrites. 0.9.0 is the newest version on PyPI
and exists upstream as the `v0.9.0` tag (PR #87, 2026-05-11); GitHub's Releases
page still tops out at 0.8.0.

**The regression is older than the draft first said.** 0.7.0 carried three
separate Cython copies of `get_tau`, each ending with
`if max_tau > 0.0: m = fmin(m, max_tau)`. 0.8.0 — the MRTS release, on PyPI
2023-07-14 — consolidated them into one shared `cython_get_tau.pyx` and dropped
the clamp from all three at once. So the cap has been inert for over three years
counting from that release, not since 0.9.0. Don't date it from the GitHub
*Releases* entry, which reads 2023-10-13 — three months late, because the tag was
only pushed after issue #71 asked for it. The tag itself is lightweight, so it
carries the July commit date and gives the right answer.

## Process

Draft the issue text below; **Tony reviews before anything is posted**
(external communication). After filing, add the issue URL here and flip status.

**Before posting**: land this branch, then repoint all **three** repo links
(fixture, `sync.py`, `test_sync_detect.py`) from `main` to the landed commit SHA.
`test_sync_detect.py` resolves on `main` today, but the version there does not yet
carry `test_pyspike_max_tau_is_still_inert` — the test that makes the link worth
following.

**When pasting**: the `**Title:**` line is the issue title, not body. Unwrap every
wrapped run of prose first — paragraphs, the Scope bullets, and the docstring
blockquote — because this file is hard-wrapped near 80 columns and GitHub treats
each newline in an issue body as a line break, so wrapped text ships as a stack of
short ragged lines. Leave the fenced blocks and the tables exactly as they are.

---

## Draft issue text (for review — not yet posted)

**Title:** `max_tau` has no effect except at spike-train edges (regression since 0.8.0)

### Summary

`spike_sync` returns the same number for `max_tau` of 1.0, 0.25 and 1e-6 on
trains whose mean ISI is about 10 s. On those data a 1 µs coincidence window
should report no coincidences at all; it reports SPIKE-Sync 0.33. On a 30-train
synthetic recording at a 0.25 s cap, the reported synchrony is 4.5× what the
capped definition allows.

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

The `None` row differs, but that difference is not the cap working on the body of
the trains: it comes from the spikes at the start and end of each train, the only
ones where a missing neighbor lets the default survive. In these trains that is
the last pair, 1.2680583 s apart — and it is the one route by which a cap still
moves the number here. Sweeping `max_tau` densely finds exactly one transition,
at that gap: every positive value below it returns 0.3333 and every value above
it returns the uncapped 0.3500. (`max_tau=0`, like `None`, means no cap.)

The pair under test has to be interior in *both* trains before all four defaults
are overwritten, so a train with fewer than three spikes never has an interior
spike and the cap still applies there. That is worth knowing for the test suite:
the only `max_tau` assertion in the suite (`test/test_distance.py:184` — the other
grep hit, `test_MRTS.py:20`, is an unused local) scores a three-spike train against
`SpikeTrain([2.1], 4.0)`, and the one-spike partner is enough to keep the cap
working. The fix proposed below leaves that assertion green — I ran it.

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
- `optimal_spike_train_sorting` (via `spike_directionality_matrix`; its annealing
  uses libc `rand()`, not seedable from Python, so compare the indicator it
  returns rather than the permutation)

`spike_directionality` on the same two trains as the sweep above shows the same
flat response:

```
 max_tau   spike_directionality
    None   -0.016667
     1.0    0.000000
    0.25    0.000000
   1e-06    0.000000
```

### Diagnosis

`pyspike/cython/cython_get_tau.pyx` (same logic in
`pyspike/cython/python_backend.py`). Note that the parameter named `max_tau`
here receives `true_max` — twice the user's cap, or the recording span, whichever
is smaller — which matters for the patch below. Annotations marked `<-`:

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
...
return fmin(s1F, s2P)            # <- max_tau never enters
```

With the default `MRTS=0` (minimum relevant time scale), `Interpolate(a, b, 0)`
returns `min(a, b)`, so the function reduces to the minimum of the four
half-ISIs — a quantity `max_tau` never touches.

**MRTS does not substitute for the cap.** `Interpolate` is bounded above by its
second argument — the half-ISI on the side facing the other spike — and raising
MRTS can only move its result up toward that bound, never down. So no MRTS value
bounds the window from above, and there is no way to express a hard cap with it.

The behavior changed in 0.8.0 (PyPI, 2023-07-14 UTC), which replaced three per-file
copies of `get_tau` with one shared implementation. In 0.7.0 the seed and the cap
were separate parameters and the cap was applied at the end — `max_tau` there is
the user's raw value, not today's `true_max`:

```cython
cdef inline double get_tau(double[:] spikes1, double[:] spikes2,
                           int i, int j, double interval, double max_tau):
    cdef double m = interval
    ...
    m *= 0.5
    if max_tau > 0.0:
        m = fmin(m, max_tau)
    return m
```

Meanwhile the documented contract never changed:

> `max_tau` — Maximum coincidence window size. If 0 or `None`, the coincidence
> window has no upper bound.

I can't tell from the outside whether the clamp was dropped deliberately or lost
in the consolidation. Either way the docstring and the code now disagree, and one
of them should move.

### Expected behavior

```
# 0.8.0 on, at MRTS=0, for spikes interior to their own trains
window = min(ISI before a, ISI after a, ISI before b, ISI after b) / 2
# expected
window = min(the above, the user's max_tau)
```

Where the parameter comes from, since the measure itself is deliberately
parameter-free:

| source | a global cap? | what it specifies |
| --- | --- | --- |
| Quian Quiroga, Kreuz & Grassberger 2002, Eq. 4 ([Phys Rev E 66:041904](https://doi.org/10.1103/PhysRevE.66.041904)) | **sanctioned** | defines the adaptive window, then: *"…one could also make other choices, e.g. by taking τij smaller than in Eq.(4) or by using τ′ij=min{τ,τij}."* |
| Kreuz, Mulansky & Bozanic 2015, Eq. 19 ([J Neurophysiol 113:3432](https://doi.org/10.1152/jn.00848.2014)) | no | window = min of the four surrounding half-ISIs (not the Eq. 19 `get_tau`'s docstring points at — that one is Satuvuori's) |
| Satuvuori et al. 2017, Eqs. 17–18 ([J Neurosci Methods 287:25](https://doi.org/10.1016/j.jneumeth.2017.05.028)) | no | raises each side toward a quarter of the MRTS, then clips at half the adjacent ISI |
| **Kreuz, Satuvuori, Pofahl & Mulansky 2017** ([New J Phys 19:043028](https://doi.org/10.1088/1367-2630/aa68c3)) | **yes — `τmax`** | *"For some applications it might be appropriate to additionally introduce a maximum coincidence window τmax as a parameter."* Applied to the El Niño data in §3.3, with the 9-month value given in appendix B |
| cSPIKE | yes — `max_dist` | `\|Δt\| < TAUij` **and** `\|Δt\| < max_dist`, plus an edge guard |
| PySpike ≤ 0.7.0 | yes — `max_tau` | `if max_tau > 0.0: m = fmin(m, max_tau)` |
| PySpike ≥ 0.8.0 | **no** | seeds four ISI slots, all overwritten for an interior spike |

So the cap is not an invention of the implementations. `min{τ, τij}` is written
into the paper that introduced the adaptive window in the first place, as an
explicitly optional variant, and it is named and used in the SPIKE-order work
fifteen years later. Neither measure paper carries it because neither is about
bounding the window: Kreuz 2015 describes the parameter-free default, and
Satuvuori's MRTS is a floor, which is the opposite thing.

cSPIKE applies it in `AdaptiveCoincidence` as a second condition on top of the
adaptive window, where `TAUij` is that window and the elided conjunct is an
edge-correction guard (indentation normalized):

```cpp
if( std::abs(spiketime-closestSpike) < TAUij )
{
    if (((max_dist < 0) || (std::abs(spiketime-closestSpike) < max_dist)) && ...
```

`max_dist` reaches nine public methods; there is no separate non-adaptive path,
since `SPIKEsynchro` just calls `AdaptiveSPIKEsynchro` with `threshold = 0`. For
`max_dist > 0`, requiring both conditions is exactly requiring
`|Δt| < min(TAUij, max_dist)` — which is what the patch below computes. Two
mismatches worth knowing if you adopt the semantics wholesale (this is cSPIKE
v1.5, 30.6.2023):

- The `max_dist < 0` escape exists only in `AdaptiveCoincidence`. The spike-order
  routines test `|Δt| < max_dist` with no escape, so there any value at or below
  zero drives every result silently to zero.
- In `AdaptiveCoincidence` itself, `max_dist = 0` admits exactly the simultaneous
  spikes — not through the strict `<`, which admits nothing at zero, but through a
  fast path that returns 1 for ties (subject to the same edge guard) before either
  condition is evaluated. cSPIKE's own no-cap conventions are `10^12` and negative
  values, never zero; PySpike's `max_tau = 0` means "no cap". So porting the
  parameter across unchanged inverts its meaning at that value.

The patch below leaves exact ties alone either way: the bound it introduces is
`true_max/2`, strictly positive for any positive cap, so `|Δt| = 0 < tau` still
holds.

### Suggested fix

As noted above, `get_tau`'s `max_tau` parameter receives `true_max`, so the bound
to apply is half of it. In
`pyspike/cython/cython_get_tau.pyx`:

```diff
--- a/pyspike/cython/cython_get_tau.pyx
+++ b/pyspike/cython/cython_get_tau.pyx
@@ -43,8 +43,8 @@
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

and the same two returns in `pyspike/cython/python_backend.py`, which uses the
builtin rather than `fmin` (both lines are unique in that file; this one is not a
`git apply`-able hunk):

```diff
-        return min(s1F, s2P)
+        return min(min(s1F, s2P), max_tau/2.)
...
-        return min(s1P, s2F)
+        return min(min(s1P, s2F), max_tau/2.)
```

Those two files cover every caller in both backends —
`directionality_python_backend.py` imports `get_tau` from `python_backend`.

No extra `max_tau > 0` guard is needed. When the user passes 0 or `None` the
callers set `true_max = t_end - t_start`, so the new term bounds the window at half
the recording span — which is exactly what 0.7.0 did, since it seeded `m` with
`interval` before halving. At the default `MRTS = 0` the two are the same function. 0.7.0 computes
`min(interval, existing ISIs) / 2` and then, for a positive cap, clamps at
`max_tau`; the patched 0.9.0 computes `min(existing ISIs / 2)` and clamps at
`true_max/2`, which is `min(interval/2, max_tau)` for a positive cap and
`interval/2` otherwise. Either way both land on
`min(interval/2, ISI/2 over existing neighbors)`, further clamped at `max_tau`
when one was asked for. I also checked it numerically, including with spikes
outside `[t_start, t_end]`.

That last part is worth stating explicitly, because it is the one case where the
patch changes a currently-uncapped answer: with `Reconcile=False` a half-ISI can
exceed the recording span, and today's code returns it while the patch bounds it at
half the span. That is a behavior change against 0.9.0 and a restoration of 0.7.0,
not a new hazard — but it is yours to sign off on.

Running the sweep above against a patched pure-Python backend:

```
 max_tau   as shipped   with the patch
    None       0.3500          0.3500
     1.0       0.3333          0.1833
    0.25       0.3333          0.0500
   1e-06       0.3333          0.0000
```

Finite caps become monotone in `max_tau`, a 1 µs window reaches 0 — the smallest
cross-train gap in these data is 0.027 s — and the `None` row is unchanged.

One design question I did not want to decide for you: with `MRTS > 0` this lets
`max_tau` override the MRTS-raised window. That seems right for a hard cap, but
it is your call.

### How we found it

We hit this porting the cSPIKE synchronization stack to Python and cross-checking
the result against both cSPIKE reference output and PySpike. Our port and PySpike
agree uncapped, and still agree at any cap too loose to bind; they diverge at every
cap tight enough to matter.

Here is what it costs on a synthetic 30-train recording — simulated calcium event
times, 2670 events at 2362 distinct times after dropping within-train duplicates,
median ISI 31 s — the project's committed test fixture, from
[a public fixture](https://github.com/syncytium2/bugarach/blob/main/tests/fixtures/synth_fastcal_s1.mat).
Both columns are `pyspike.spike_sync`, so this is PySpike against itself; the
patched column comes from the pure-Python backend with the diff above applied:

| `max_tau` | as shipped | with the patch |
| --- | --- | --- |
| uncapped | 0.3235 | 0.3235 |
| 0.25 s | 0.3133 | 0.0696 |
| 1 µs | 0.3119 | 0.0156 |

At a 0.25 s cap the shipped code reports 4.5× the synchrony the capped definition
allows. Our own port, which matches cSPIKE reference output to 1e-9 at that cap,
reproduces the patched column to the digit — corroboration rather than the
measurement, since it implements the same semantics the patch restores.

The port and the test that pins this bug:
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

- **The intent argument was cut, because it was false.** The draft claimed the
  callers "still" compute a doubled `max_tau`, offering that factor of 2 as
  evidence the bound was meant to survive. 0.7.0 has no `true_max` and no
  doubling — the seed and the cap were separate parameters — so the doubling was
  created by the same rewrite that dropped the clamp, and it is fully explained by
  `max_tau` now seeding an ISI slot that gets halved. It discriminates nothing. The
  report now rests on the docstring alone and asks which way the maintainer wants
  it resolved, which is both true and harder to argue with.
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
  this report's own "Expected behavior" section contradicted. cSPIKE has the same
  parameter as `max_dist` (`cSPIKE_mac/SpikeTrainSet.m:187`, and in eight of the
  nine signatures in the class help, and described in none of them; applied in
  `cSPIKEmex/Spiketrains.cpp:453` as a second condition on top of the adaptive
  window). The final version says what is actually true and is the
  strongest of the three: the cap is published, in a third paper
  (New J Phys 19:043028) that Mulansky himself co-authored, as an explicitly
  optional extension — which is why it is missing from the two measure papers and
  why 0.8.0 dropping it is a regression rather than a redesign. Verified verbatim
  from the PDF.
- **Scope was understated.** `get_tau` has 14 call sites across three `.pyx`
  files, not the four SPIKE-Sync entry points originally listed; the
  directionality and spike-train-order APIs take `max_tau` too and are equally
  affected.
- **The 0.25 s row is the operating point our detectors run at.** Our port's
  per-spike profile at that cap is what `tests/test_sync_detect.py` asserts to
  1e-9 against cSPIKE MATLAB reference output, so both columns are checkable from
  the repo.
- **The results table became PySpike-against-PySpike**, which removed two problems
  at once. It no longer asks the maintainer to trust an unpublished port for the
  headline number, and it no longer needs the definitional hedge about comparing
  our mean-of-per-spike-values against PySpike's summed-coincidence-over-summed-
  multiplicity. The 1 µs row, previously withheld because our port is
  cSPIKE-validated only at 0.25 s / 0.5 s / uncapped, ships now that both columns
  come from the same code path. The port's numbers reproduce the patched column to
  the digit, so it corroborates instead of carrying.
- **A rendered figure was considered and left out.** The finding is a scalar
  comparison, the ASCII derivation carries all of it, and unlike an image it can
  be quoted in a reply and read in a terminal — where triage happens. The one
  picture-shaped claims are both better as the tables they already are: the
  cSPIKE comparison has only two validated points, and the as-shipped-vs-patched
  sweep is four rows whose whole content is "one column moves and the other does
  not". Recorded, with both reasons, so a later session does not reopen it.
- **After filing**, the issue URL belongs in `docs/FOUNDATIONS.md` (the PySpike
  bullet at line 49), `README.md` (twice — lines 41 and 76), `tools/sapper.py`'s
  SAP003 message, `src/bugarach/detectors/__init__.py`, the NOTE comment in
  `tests/test_sync_detect.py`, `docs/sapper_feedback/2026-08-12-sap-id-namespace-collides-with-interface2.md`,
  and — the one an outside reader meets —
  `docs/todo/2026-08-11-methodology-narrative-doc.md`. All **eight** assert the bug
  today with no upstream reference, **and all eight call it "PySpike 0.9.0's" bug,
  which this report now shows is wrong: it broke in 0.8.0.** Fix the version in the
  same pass as the URL. `test_pyspike_max_tau_is_still_inert` is a ninth mention
  but already names 0.8.0 correctly; it now points back here instead of keeping
  its own copy of this list, which had already drifted to three entries.
- **Unverified here** ⚠: whether upstream's own test suite stays green under the
  patch. The one `max_tau` assertion does — I ran it, patched and unpatched, and
  the issue says so. The other 11 test files were not executed against a patched
  build — 13 test files ship in the 0.9.0 sdist and one assertion in one of them
  has been exercised, so this is a small concrete job
  before offering the PR, and `test_reconcile.py` is the one to watch given the
  `Reconcile=False` behavior change the issue now discloses. Note also that every
  "with the patch" number was produced by the pure-Python backend; nothing has been
  run through a patched *compiled* extension.
- SPIKY, the MATLAB GUI, is not in this tree at all, so it cannot be checked from
  here — the issue claims the cap only for cSPIKE and PySpike, both read directly.
- The repo links assume bugarach stays public at that path.
