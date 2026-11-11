# Pipeline: stream readiness — from an export folder to calls, once per stream

**Use it when** a new or revised export folder becomes the default and each stream (fast, slow,
combined) needs detector calls on it that rest on settings chosen for that folder.
**It produces** per stream: a measured record of the baseline, a simulated bench built from it, a
check that the measuring tools recover what was planted at those values, searched detector
settings, and `detections.csv` on the folder.
**Cost:** stages 1 and 3 are minutes to an hour on 12 workers; stage 5 is one overnight per
stream on WSMIP065.

> **Working material, not murderboarded.** For sessions in this tree.
>
> ⚠ **This is not [`../pipeline.md`](../pipeline.md).** That page is the product loop Tony
> dictated on 2026-09-04 and it names the steps. This page is the commands that walk those steps
> for one stream, as they ran in September, joined to the synthetic-validation checks
> ([ADR-0020](../adr/0020-one-route-from-a-folder-to-calls-per-stream.md)).

**Where this came from.** The stages were run for all three streams between 2026-09-21 and
2026-09-25, as three sets of commands recorded in three places (`bench_combined.py`'s docstring,
[`handoffs/2026-09-21-slow-bench.md`](../handoffs/2026-09-21-slow-bench.md) and
[`handoffs/2026-09-25-overnight-final-parameters.md`](../handoffs/2026-09-25-overnight-final-parameters.md)).
Stage 3 is new: it is Aim 1 of [`goals/synthetic-validation.md`](../goals/synthetic-validation.md).
Every command below was checked against the tool's `--help` on 2026-11-11.

**The rulings it rests on:** baseline only (FOUNDATIONS §9); the folder is the input and a known
contamination stops the work (CLAUDE.md); a false alarm is coincidence the rates explain
(ADR-0006); the floor is per window (ADR-0008); the elevated-rate test has its own recording
(ADR-0009); events are planted at measured gaps (ADR-0010); treatment recordings at rate levels (ADR-0013); no decoys (ADR-0019); coded
detectors, synthetic first (ADR-0021); close events as an axis of set separations (ADR-0022).

## The route, as commands

`<run>` is one dated folder under `docs/learned/runs/`. `<stream>` is `fast`, `slow` or
`combined`.

### Stage 0 — the folder

    bugarach check <folder>
    python -m bugarach.dataset

**Gate: `dataset.default()` does not refuse.** The default folder has been stopped since
2026-10-05 ([todo](../todo/2026-10-05-the-pinning-census-undercounts-on-the-default-folder.md)).
Nothing below stage 2 reads data, so stages 2 to 5 can be rehearsed while it is stopped; stage 1
and stage 7 cannot run. The stop is what a week of analyses over four contaminated recordings
earned (2026-09-10 to 2026-09-17).

### Stage 1 — characterize the baseline, per stream

    python tools/measure_jitter_correlogram.py --streams fast slow combined --out <run>/jitter
    python tools/measure_coordination_rates.py --out <run>/rates
    python tools/measure_real_intervals.py --out <run>/intervals
    python tools/remeasure_bench.py --jitter-record <jitter> --rates-record <rates>            # fast
    python tools/measure_slow_bench.py --stream slow --jitter-record <jitter> --rates-record <rates>
    python tools/measure_slow_bench.py --stream combined --jitter-record <jitter> --rates-record <rates>

Then transcribe each record into its module (`bench.py`, `bench_slow.py`, `bench_combined.py`).

**Gate: `pytest tests/test_bench_is_measured_on_the_declared_folder.py tests/test_bench_slow.py
tests/test_combined.py`.** A constant that disagrees with its record is refused. The
transcription is by hand, and that is the route's weakest joint (*Owed*, item 5).

### Stage 2 — the stream profile

    python -m bugarach.stream_profile

Prints, for each stream, the cells, participants, jitter and backgrounds the next stages will
use, the record they came from and how many decoys the bench still plants.

**Gate: `pytest tests/test_stream_profile.py`.** The profile holds no number of its own, so a
stream cannot have two answers. Earned on 2026-11-11: the recovery scripts typed 33 cells and
0.0096 Hz where the benches hold 32 cells and a measured background per stream.

### Stage 3 — do the measuring tools recover what was planted, at this stream's values?

    python docs/learned/synthetic_validation/aim1_lab_regime.py

One planted source at each of the profile's participation levels and both backgrounds; the
coordination-rates tool and the joint fit are run blind.

**Gate: per stream and level, participants and event rate within 10 % of planted at the
median, and the jitter's interquartile range containing 1.** Where a level fails, the
characterization of that stream at that level is not trusted, and the bench value it would set
is marked as chosen, not measured. On 2026-11-11 (September's values, 20 simulated recordings
per row) the two larger levels of every stream pass on participants and rate; jitter passes at
6.7 cells and above and fails at 3 to 4 cells, where it reads about twice the planted value
([goal page](../goals/synthetic-validation.md), *Aim 1a at the lab's values*).

### Stage 4 — budgets

    python tools/measure_slow_budgets.py --bench slow
    python tools/measure_slow_budgets.py --bench combined

The fast stream's three limits are constants in `bench.py`.

### Stage 5 — tune

    python tools/search_all_settings.py --bench <stream> --sliding --out <run>/search-<stream>

Realistic spacing is the default (ADR-0010); `--spacing bench` reproduces older results.

**Gate: adoption is Tony's.** The search proposes; a setting is installed only on his word. The
2026-09-25 night produced nine rulings that are still open
([report](../learned/runs/2026-09-25-final-parameters/README.md)).

### Stage 6 — the settings file

    python tools/settings_from_bench.py --bench <stream> --out <run>/detector_settings_<stream>.csv

### Stage 7 — detect on the original folder

    bugarach detect <folder> --stream <stream> --settings <run>/detector_settings_<stream>.csv

Every analysis names the dataset it read, on stderr and in its record (ADR-0018).

## Owed, in the order the route needs it

None of these needs a ruling unless it says so.

1. **The bench without decoys, and the rate-matched negative tool** (ADR-0019;
   [todo](../todo/2026-10-23-rate-matched-negatives-and-the-bench-without-decoys.md)). Every
   bench still plants 6 decoys per recording. `StreamProfile.recording(decoys=False)` gives the
   recording without them; the scores have not been re-derived.
2. **The separation axis on all three streams**
   ([ADR-0022](../adr/0022-close-events-are-a-bench-axis-the-event-definition-stays-at-2-s.md)):
   neighbouring events planted 0.5 to 5 s apart, every detector scored at each separation.
   **First run 2026-11-11** (`tools/measure_separation_axis.py`;
   [record](../learned/runs/2026-11-11-separation-axis/README.md)): at the shipped settings no
   detector on any stream separates events 2 s apart or closer. **Searched the same day**
   (`tools/search_close_events.py`;
   [record](../learned/runs/2026-11-11-close-events-search/README.md)): count (sliding) in a
   0.5 s window with no merge gap splits 0.88 to 0.97 of pairs 1 s apart on every stream, at
   the 2 s floor's count and with no false call on recordings with nothing planted. No
   setting that keeps the 2 s window splits close pairs. Owed: whether a 0.5 s window holds a
   real event (first check on the revised export), the picks' scores on the whole bench and
   its other budgets, and a stricter per-event tolerance. Nothing is adopted.
3. **Treatment recordings**
   ([ADR-0013](../adr/0013-the-bench-simulates-treatment-periods.md)): a rate course as a
   generator input, courses at set multiples of the baseline rate, a null twin for each, and
   scores by segment. Built now with synthetic courses; the measured ones wait on the export.
   Five of its open points are still Tony's.
4. **Stage 3 for the rest of Aim 1**: the assessor and the correlogram on the same recordings, a
   fixed assembly, and two sources ([goal page](../goals/synthetic-validation.md), *The plan*).
5. **A profile built from the measured record**, so stage 1 ends in a file and not in an edit
   to three modules; then the scoring path takes the profile and the three modules become one
   ([todo](../todo/2026-09-21-one-stream-aware-bench.md)).
6. **A `--folder` route for the measuring tools and a writer for a simulated folder**, so the
   whole route can be rehearsed on a synthetic stand-in before the export arrives.
7. **An evaluation stage between 6 and 7**: the capability map per detector (Aim 2), scored per
   source on rate-matched negatives.
8. **Re-measuring the parameters from the calls** after stage 7 (Aim 3).
9. **The producer's own statement of what assigns an event to fast or slow**
   ([`goals/combined-stream-coordination.md`](../goals/combined-stream-coordination.md)); the
   route runs on Tony's working rule of 2026-10-07 until then.
