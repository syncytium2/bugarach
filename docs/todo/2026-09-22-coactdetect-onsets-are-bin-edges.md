---
status: open
filed: 2026-09-22
priority: high — it touches the detector that wins goal 2's comparison
---

# CoactDetect's event times are bin edges, so they cannot line up with chorus or with the data

Tony, 2026-09-22: CoactDetect's event times do not line up with chorus or with the data. **A
mechanism that would produce exactly that is in the code, and this file is the candidate, not
the verdict.** It is filed to be confirmed on a real recording, which this session could not do.

## The candidate mechanism

`src/bugarach/detectors/coact.py:278` builds a call's onset as the **left edge of the bin it
started in**:

```python
onset = np.array([edges[s] for s in starts_b])
width = np.array([edges[e + 1] - edges[s] for s, e in zip(starts_b, ends_b)])
```

So both the onset and the width are quantised to `int_win_sec`, which the shipped operating
point sets to **2.0 s** (`bench.OPERATING_POINTS["coact"]`). Every CoactDetect onset in the
binned mode lands on a 2-second grid anchored at the window start, not on any event.

Three consequences, and they match the complaint one for one:

- **Against the data.** A call's reported onset can precede the first member event by up to one
  bin. It is a grid edge, not an event time.
- **Against chorus.** The nets decode per frame — `decode()` in `learn/encode.py`, 0.1 s
  resolution with a 20-frame merge gap — so their onsets sit near real events. Multiples of 2 s
  and frame-resolution onsets cannot agree except by coincidence.
- **It reaches everything downstream.** `emit.py` writes the detector's own `onset_sec` into
  `detections.csv`, which is what the rasters, the before/after figures and fireflies all read.
  `call_measure` is **not** joined in `src/`: it is a sidecar produced by `tools/measure_calls.py`
  into `calls_measured.csv`, so the primary artifact carries the bin-quantised time.

## Why this is not simply a bug

The bin edge is what a binned detector honestly knows — the statistic is a per-bin count of
distinct ROIs, and no finer time is available from it. PR #698 already gave every detector one
yardstick for a call's width and amplitude, derived from the **member events**
(`src/bugarach/call_measure.py`), precisely because a detector's own extent is not comparable
across detectors. What this todo says is narrower: **the same argument applies to the onset, and
the onset never got the same treatment.**

## What to confirm, on a real recording

1. **Measure the offset.** For each CoactDetect call on one recording, the gap between its
   `onset_sec` and the first member event onset inside it (`call_measure`'s core first onset).
   If the mechanism above is right, that gap is in [0, 2.0) s and its distribution is roughly
   uniform, not centred on zero.
2. **Compare with chorus on the same recording**, same way. A net's onsets should sit within a
   frame or two of member events; if CoactDetect's sit a bin away, the two series will look
   shifted rather than disagreeing about which events are coordinated.
3. **Check the sliding mode.** The every-knob search chose *sliding* for CoactDetect and LoCo,
   where there is no grid — but **the shipped points are still binned**, which is already the
   fifth code defect in the methods cover memo. If sliding removes the offset, that is one more
   argument for switching, and it should be stated in the switch's rationale.

## What it would change if confirmed

- **Goal 2's comparison is not automatically wrong.** Scoring matches a call to ground truth
  within a tolerance (`bench.TOL_SEC` and the tolerance grid), and a tolerance wider than a bin
  absorbs the offset — which is why this could be true all along and not show up in F1. **That
  is the first thing to check before anything is re-run**: if the tolerance absorbs it, the
  comparison stands and only the *displayed* times are wrong.
- **Anything that reads a time rather than a match is affected**: the rasters, the before/after
  figures, the merge-gap page, and fireflies' pages — which is where a person would notice it,
  and did.
- **The fix, if one is wanted, has a shape already in the tree**: give the emitted onset the
  same treatment #698 gave width and amplitude — take it from the member events, keep the
  detector's own value in a column beside it. That is also what the fireflies contract proposal
  asks for in its own terms, which makes the two changes one change.

## Where it came from

Tony noticed it by eye, which is the third time this month that a figure has caught something a
test did not.
