---
status: open
filed: 2026-09-21
priority: high — right after the 2026-09-22 meeting
---

# One stream-aware bench, in place of `bench.py` beside `bench_slow.py`

## The ruling

Tony, 2026-09-21: *"we don't have time to rebuild bench.py to handle more than one stream.
this has to be a high priority todo after tomorrows meeting."* So the slow-stream bench is
being built as a separate `src/bugarach/bench_slow.py` (`docs/handoffs/2026-09-21-slow-bench.md`, step 2, on
WSMIP064), and this todo is the rebuild that makes that module unnecessary.

## Why the separate module is a stopgap

`bench.py` holds one fast value for every structural constant — 24 module-level constants —
and the functions that produce every score read them as globals: `evaluate`, `sweep` and
`evaluate_curve` go through `make_recording` to `BENCH_RECORDING`; `false_positives_per_hour`
goes through `make_null_recording` to `NULL_RECORDING`; `pick_operating_point` reads
`MAX_PROBE_PER_MIN`. A second stream therefore cannot reuse those functions, and
`bench_slow.py` has to carry its own copies of about nine of them. Two copies of the scoring
path drift: a fix to one is a bug left in the other, and nothing but a test notices.

## What done looks like

- A **stream profile** — one object holding every constant that differs by stream (recording
  spec, backgrounds, no-coordination and close-events recordings, elevated-rate limits,
  false-alarm budgets, search grids, measured values, width distribution) — and one per
  stream, fast and slow, each measured on the default folder's baselines.
- Every function in the scoring path takes the profile as an argument instead of reading a
  global. The fast profile's values are **byte-identical** to today's constants: this is a
  refactor, and a moved fast number is a regression.
- `bench_slow.py` is deleted; its slow values become the slow profile.
- `tools/measure_slow_bench.py` is deleted with it. It exists for the same reason the module
  does — Tony declined a `--bench` flag on `tools/remeasure_bench.py` on 2026-09-21, because
  threading a stream through the shared measurement tool is the expansion there was no time
  for, and that tool is claimed on WSMIP065 besides. One tool measures a profile afterwards,
  and it writes that profile's own record rather than the one path it writes today
  (`tools/remeasure_bench.py:224`).
- Every tool's `--bench fast|slow` (added for the slow work) selects a profile rather than a
  module.
- The guard `tests/test_bench_slow.py` becomes a test that no scoring function reads a
  stream constant from module scope.

## Coordination

`bench.py` is claimed by two WSMIP065 sessions as of 2026-09-21 (`opt-min-baseline`,
`opt-assess-revised-export`), and the participation 0.18 → 0.19 change
(`docs/todo/2026-09-21-bench-participation-to-0-19-after-the-meeting.md`) edits it too.
Sequence the three: land or release those claims, make the participation change, then this
refactor — or do the participation change inside the fast profile as its first commit.
