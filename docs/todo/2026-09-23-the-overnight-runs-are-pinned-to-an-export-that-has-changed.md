---
status: open
filed: 2026-09-23
---

# Everything the overnight run measured is pinned to one export, and the data have changed

**Tony, 2026-09-23: *"data changed. we'll come back to this."*** This file is the label on that
work, written while it is still fresh, so whoever returns knows exactly what rests on what.

**The export everything below was measured on:**
`2026-09-17_revised_2v_long_STEPS_AND_PINS_EXCLUDED`, role `steps_and_pins_excluded`, 84
recordings, confirmed by Tony at the start of the 2026-09-22 session.

Nothing here is retracted and nothing needs deleting. Every run is reproducible and every number
is correct *about that folder*. What changed is the input, so what needs saying is which results
inherit it and in what order they would be redone.

## ⚠ The runs most affected are the ones least able to notice

`tools/check_scored_dataset.py` flags a result scored on something other than the default, but it
can only check a record that carries `dataset.stamp()`. Of the overnight runs:

| carries a `dataset` stamp — will be flagged automatically | carries none — **will pass silently** |
|---|---|
| `2026-09-22-jitter-correlogram` | `2026-09-23-full-search-fast` |
| `2026-09-22-jitter-by-group` | `2026-09-23-full-search-slow` |
| `2026-09-23-coordination-rates` | `2026-09-23-full-search-combined-{coact,rest,sync-rerun}` |
| `2026-09-23-coordination-rates-combined` | `2026-09-23-learned-{slow,fast,combined}` |
| `2026-09-23-jitter-correlogram-combined` | `2026-09-23-chorus-combined` |
| the three `bench_measured*.json` records | `2026-09-23-full-cohort-combined` |

The split is not an oversight in those runs. **The searches and the learned fits never read the
folder** — they read the *bench*, which is simulation. So they have no dataset to stamp, and the
checker is right that it cannot check them. The dependency is real but indirect:

> folder → `remeasure_bench` / `measure_slow_bench` → the bench constants (jitter, participation,
> backgrounds, probe) → every search, every learned fit, every bench F1 quoted anywhere

All three `bench_measured*.json` records name the folder and the date, so the chain **is**
traceable by hand. It is simply not mechanized, and a reader who only runs the checker would
conclude the searches are fine.

## What rests on it, in dependency order

1. **The bench constants themselves** — `bench`, `bench_slow`, `bench_combined`: jitter
   (0.106 / 0.135 / 0.148 s), participation, quiet/busy backgrounds, the 99th-percentile probes.
   These are the root; everything below inherits them.
2. **The every-knob searches** — fast, slow, and the three combined runs. Their picks are
   proposals against those constants. None was adopted: `bench.OPERATING_POINTS` and
   `bench_slow`'s were never edited, and `bench_combined`'s carries *"awaiting Tony's review"* in
   every `source` string.
3. **The learned models** — chorus on slow and on combined, five seeds each. Trained on the bench,
   so they inherit it twice over: the fits and the F1s both.
4. **The real-data passes** — the combined cohort detection (22,569 calls, then 18,866 after
   SPIKE-synch was retuned) and the slow learned detection (4,573 calls). These read the folder
   **directly**, so they are the ones a new export changes most concretely.

## If the work resumes, the order is forced

The chain above is also the order. Re-measuring the benches first is not a preference; every
number below step 1 is computed against those constants, so redoing anything downstream before
them wastes it.

1. `python -m bugarach.dataset confirm` for the new folder — Tony's, not a session's.
2. `tools/measure_jitter_correlogram.py`, then `remeasure_bench.py` and `measure_slow_bench.py`
   (both now read jitter from the correlogram record, and both refuse a record measured on a
   different folder — so a stale jitter cannot silently survive the move).
3. `tools/measure_coordination_rates.py` for the backgrounds and probes.
4. Only then the searches and the learned fits.

## Two findings that do **not** depend on the export

Worth separating, because they would otherwise be re-derived:

- **The `extend` cap is silent and reads a plateau as a climb.** `C_min` came back at exactly
  0.0025 — one eighth of its grid floor — on slow, combined *and* fast, and on combined it was
  shown by direct test that pinning it back to the grid costs nothing. That is a property of the
  search, not of the data. Counts were fixed in #755; the continuous case was not.
- **`search.json` is not strict JSON.** The slow run's binned-SCE pick carries a literal `NaN`
  for `merge_gap_sec`, a value not in its grid. Any reader stricter than Python's rejects the
  whole file. Also a property of the search.

## What would make this unnecessary next time

A result that cannot stamp a dataset could stamp the **bench record** it was computed against —
`bench_measured*.json` already carries the folder and the date. Then `check_scored_dataset.py`
would follow one hop and catch exactly the runs it currently cannot see. Filed as the useful
version of this note rather than as a complaint about it.
