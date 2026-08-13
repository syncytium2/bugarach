---
status: open
filed: 2026-08-13
---

# LoCo and CICADA can't run on a single-stream slice with their own defaults

Found while porting the simulator, which now emits single-stream slices by
decision (2026-08-13).

```python
s, gt = simulate_coordination(seed=3)     # one stream, named "events"
loco_detect(s)      # ValueError: bin_width_sec must be scalar, a 1-element
                    # sequence in stream order, or a dict keyed by ['events']
cicada_detect(s)    # ValueError: sce_percentile must be ...
sce_detect(s)       # fine
```

## Cause

`per_stream_param` accepts a scalar, a sequence of length `len(streams)`, or a
name-keyed dict. The defaults are `(FAST, SLOW)` pairs, which is none of those
when there is one stream:

| file | parameters |
|---|---|
| `detectors/loco.py` | `bin_width_sec=(1.0, 2.0)`, `context_win_sec=(120.0, 60.0)`, `thr_step_sec=(15.0, 30.0)`, `merge_gap_sec=(2.0, 4.0)` |
| `detectors/cicada.py` | `active_duration_sec=(1.0, 2.0)`, `sce_percentile=(99.99, 99.9999)` |

The broadcasting logic is right; the *defaults* assume the canonical two-stream
store.

## Why it matters more than it looks

FOUNDATIONS §3 says streams are generic, that most outside labs have **one**, and
that the viewer treats single-stream as the default presentation. The whole point
of that section is that a foreign single-stream recording should just work. Two
of the six detectors refuse it out of the box, and the error names an internal
helper rather than saying "these defaults are for two-stream stores" — so a new
user's first read is that their data is malformed.

It is invisible in the current tests because they all run against the committed
two-stream fixture, and `tests/test_ui.py` passes explicit params.

## Fix — do NOT just make the defaults scalar

Flattening `(1.0, 2.0)` to `1.0` would silently change SLOW's behaviour on every
canonical store and break the parity claim. Two options that do not:

1. **Sentinel defaults.** Default each to `None` and resolve inside the detector:
   the pair for two streams, its first element for one. Explicit, keeps
   two-stream behaviour byte-identical, costs six small edits plus a helper.
2. **Relax `per_stream_param` for the single-stream case**: when there is exactly
   one stream and a longer sequence arrives, take the first element. One edit,
   but implicit — a caller who passed `(fast, slow)` meaning SLOW gets FAST
   without being told.

Option 1 is preferable: same result, nothing implicit.

Whichever, add a test that **every** detector runs on a single-stream slice with
pure defaults. The absence of that test is the actual bug — the defect is old,
and only surfaced when something finally generated single-stream data.

## Not urgent for the bench

`tools/`-side callers can pass explicit scalars, which is what
`tests/test_simulate.py` does. This blocks the "it just works for other labs"
claim, not the port.
