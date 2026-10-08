---
status: waiting-on-tony
filed: 2026-10-08
---

# Characterize the revised `stack`, then search it per stream

**Where this stands.** `stack` (Tony's "stacking blocks", 2026-10-07) has been built, revised
and never optimized. Every figure and raster page made so far shows its **first form**, now
`stack_global`. The revised `stack` (`src/bugarach/detectors/stack.py`, #869, #872, #875) has
not been run on a bench or on real recordings by anyone. Tony, 2026-10-07: *"definitely need to
characterize the revised version of stack."*

Written at the end of session `bugarach-shallow-gravel` (Mac), 2026-10-07. Nothing is running
and nothing is unpushed.

## What is known

**The first form (`stack_global`), on the reference bench.** Run record:
[`docs/learned/runs/2026-10-07-stack/README.md`](../learned/runs/2026-10-07-stack/README.md).
- LoCo has the highest F1 on fast, slow and combined; `stack_global` does not beat it. It was
  untuned against tuned or trained detectors, so the ranking says little about what stack can do.
- Against count (sliding), its one-width case, it finds the same scored events. What it adds is
  calls on tight groups with fewer ROIs than the floor: under-floor planted events (left out of
  the score) and decoys (counted against it).
- It is no better than count (sliding) at ignoring shared rate change.

**The first form on the September 2026 pilot** (six APV+CNQX-then-gabazine recordings, baseline
windows, interface2's 4x and 3x eval folders). Numbers and pages are in the darkroom only,
`bugarach/2026-10-07-stack/README.md`. On real baselines it makes more calls than count
(sliding), most of the extra ones won by the narrowest window. ⚠ That folder is an eval folder,
not cleared for analysis, and was never scanned for field steps.

**The revised `stack`'s parameters, none searched:**

| parameter | value | source |
|---|---|---|
| widths | 0.3, 0.5, 1, 2 s | Tony: 3, 5, 10, 20 frames at 0.1 s |
| reference width | 2 s | count (sliding)'s window, ADR-0008's floor window |
| ROI minimum, reference width | the window's ADR-0008 floor | ADR-0008 |
| ROI minimum, narrower widths | 3 | Tony, 2026-10-07: a pair is never an event (#875) |
| null context | 120 s, `maxlt` | copied from LoCo |
| guard | 0 s | LoCo's option, off |
| calling probability | calibrated per recording to count (sliding)'s call rate at the floor, 200 rigid shifts within ±20 s | Tony |
| merge gap | 0.5 s fast, 2.5 s slow, 2.5 s combined | Tony: `call_measure`'s gaps |

**It is not registered in any bench.** `bench.py`, `bench_slow.py` and `bench_combined.py` hold
eight detectors each and no `stack`. Only LoCo, CoactDetect and SPIKE-synch ship three distinct
parameter sets; rate+context and locust ship two (fast equals slow); binned SCE and both count
rules ship one. Tony wants **three distinct optimized sets** for stack.

**It is cheap.** Timed on this laptop, one thread, 45-minute bench recordings: about 2 s (fast),
3 s (slow), 10 s (combined; 29 s worst, busy background). A rough budget for a per-axis search
of about eight settings on all three streams is 40 + 30 + 100 CPU-hours, about four hours on a
workstation at 40 workers. The three-hour crowded recordings were not timed.

## Waiting on Tony

1. **Pilot pages: detector's own width or the unified width?** They currently draw the unified
   width (`call_measure`), labelled, at his word. He then wondered about reverting. My
   recommendation is to revert the pages to each detector's own width and keep the unified width
   as a carried column, because:
2. **The unified width rule chains onsets on slow and combined.** On the pilot, the stretch
   holding 80% of an event's ROIs has a median of 0.4 to 0.6 s on every stream, while the
   unified width has a median of 1.7 s (slow) and 3.3 s (combined), and on combined it tracks
   how busy the recording is (r = 0.54). Options, smallest first: a 0.5 s gap on every stream;
   keep the gap rule and report the shortest stretch holding a stated share of the ROIs; a
   per-onset gap on combined. The gap and aperture are his settings of 2026-09-21. Note that
   stack's merge gaps are copied from the same numbers.
3. **Should the bench hold events closer than 2 s?** The realistic bench plants gaps drawn from
   measured baseline gaps, and that measurement merged events under 2.0 s apart, so no shorter
   gap exists in it. Combined is otherwise reflected well (3.0% of planted gaps under 5 s
   against 3.4% measured). Fast plants about half the measured share of short gaps (3.5% under
   5 s against 7.5%), cause not found. The gaps came from the 66-recording default folder, now
   stopped (#858).
4. **When to search.** A handoff landed on 2026-10-07 saying the floor needs a rethink
   (`de09354e`). Stack calibrates against the floor. Nobody in this session read it.

## What a session can do without a ruling

1. **Run the revised `stack` through the existing comparison.** `tools/measure_stack.py` and
   `tools/measure_stack_on_folder.py` call `stack_global`. Add the revised `stack` beside it
   (it needs `stream=` and the floor), rerun the five-detector bench figure and the pilot pages,
   and say what changed. This is the characterization Tony asked for.
2. **Draft the search grid for his review**, one axis per parameter in the table above, before
   registering anything. Registering a detector in the benches touched 24 files for count
   (sliding): operating points, grids, budgets per stream, the registry tests.
3. **Find why the fast bench under-plants short gaps.**

## Loose ends from the session

- **Test workers segfault inside torch on this Mac under `-n auto`.** Fourteen workers each run
  torch at its default thread count; `OMP_NUM_THREADS=1` stops it. `learn.train` pins threads
  for training only, so a test that runs a model directly is unpinned. A session-wide pin in
  `tests/conftest.py` would fix it. Not done; CI's 4-core runners were not checked.
- `pytest-xdist`, a declared dev dependency, was missing from the Mac's venv and was installed.
- `tests/test_session_briefing.py::test_it_is_fast_enough_to_be_unconditional` fails under a
  loaded parallel run (3.7 to 4.5 s against 3.0 s) and passes alone.
- **Lane bars are drawn at the call's true width since #870.** Figures committed before that
  keep bars padded to as much as 2.5 s.
- The interactive webapp draws imported detections only in its single-recording view. Putting
  the lanes in its overview and turbo views was proposed and not decided.
- The pilot's chorus lane is `chorus_norm_part` on the group pages and in the viewer file, and
  `chorus_norm` on the per-recording pages.

## Where things are

- Detectors: `src/bugarach/detectors/stack.py`, `stack_global.py`; tests `tests/test_stack.py`,
  `tests/test_stack_global.py`.
- Tools: `tools/measure_stack.py` (benches and swell worlds), `tools/make_stack_rasters.py`
  (simulated raster pages), `tools/measure_stack_on_folder.py` (real baselines; darkroom only;
  writes the detections files the group page and the viewer read).
- Group pages for the pilot: `tools/make_group_raster_summary.py --unscanned --all-groups
  --detections <detections_all_streams.csv>`; output in
  `<darkroom>/bugarach/2026-10-07-stack/sept-pilot-{4x,3x}/group-pages/`.
- PRs from this session, all merged: #865, #866, #868, #870, #875.
