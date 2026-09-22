# Cover memo: the coordination-pipeline methods section

**For Tony, 2026-09-22.** This goes with `coordination_pipeline_methods.docx`. It holds what the
review found that is not manuscript text: code defects that stop results, design choices a
referee will attack, decisions that are yours, and why the section order is not your list's.
The murderboard run record is in `docs/reviews/coordination_pipeline_methods_2026-09-22.md`.

## 1. Stop before reporting results: three code defects

Each of these makes a number the methods describe differ from the number the code produces. The
methods state the intended rule. Until each is fixed and the affected outputs are regenerated,
results for the named detectors should not be reported.

| # | defect | affects | fix |
|---|---|---|---|
| 1 | **LoCo and locust rates count the wrong calls.** They run on the whole recording and tag each call with its raw *period*. `make_before_after_figure` then counts every call in the period and divides by the *analysis window's* duration. The count includes calls from the first 2 min of treatment and from baseline before its last 20 min, while the duration excludes that time. The detectors already compute an `in_stats_window` flag, but `emit` drops it. | before/after rates for LoCo and locust | carry the in-window flag into `detections.csv` (or have `detect_folder._run_nested` drop out-of-window calls), and regenerate the before/after figures |
| 2 | **binned SCE's width and amplitude are measured over the wrong interval.** `measure_calls` rebuilds each call as onset to onset + width. For binned SCE that is the bin start plus the *spread of its events*, not the bin. `score.py` fixed the same defect for scoring with `extent_sec`, but `emit` does not export that field. | binned SCE width and amplitude | export `extent_sec` in `detections.csv`, build the aperture from it, and re-measure |
| 3 | **locust's threshold spans drug periods.** `threshold_scope="global"` computes one threshold per recording, baseline and treatment pooled, so a treatment that raises the event rate raises baseline's bar as well. The methods disclose it; for a before/after comparison it is a confound, not a detail. | locust before/after rates | run locust with a per-period (regional) threshold, or report it only with this caveat |

## 2. Design choices a referee will attack (the methods now disclose each)

- **Distractors are indistinguishable from planted 18% events.** They have the same 6 cells and the
  same 0.36 s jitter, yet are scored as false alarms, which caps F1 at 0.83. The generator's own
  docstring calls them "genuine coincidence that is not a coordinated event", but nothing a
  detector can observe separates the two. Either give them a property a detector could reject
  (wider jitter, for example) or accept the ceiling and say why.
- **The close-events limit was reported, not applied, in the comparison.** It would have refused 19
  of 48 coded choices, and 16 of 48 in the replicate. LoCo, rate+context and SPIKE-synch failed it
  in every fold under the false-alarm rule. Against their own sliding starting points, the adopted
  CoactDetect and LoCo settings lose 0.041 and 0.042 close-events F1, over the 0.02 limit.
  Whether the limit's reference is the binned or the sliding default is a ruling that is still
  open.
- **The benchmark constants were set from earlier data** (a closed archive and older exports), then
  only re-checked on the current export. Cell count, jitter and participation come from a cluster
  rule that cannot see events under 4 cells.
- **No-coordination recordings share seeds, and hence backgrounds, with the selection recordings**
  in the settings search.
- **The Nadeau–Bengio factor √(3/7) was applied to learned-versus-coded contrasts**, where the
  training-set ratio does not hold (a refit fits 10 recordings). The methods now call separability
  a descriptive bar.
- **Constants set by judgement:** the 2.5 s matching tolerance (1.5 s until 2026-08-28), the
  admissibility margins, the 1.6× false-alarm multiplier, and the 1 s aperture and 0.5 s gap of the
  width measure.

## 3. Decisions that are yours

- **Participation 0.18 → 0.19** (your todo for after today's meeting). At 33 cells both give 6
  cells, so the planted events do not change. Whether the move changes anything else depends on
  what else moves with it (the 30% and 10% levels, the RNG stream).
- **The 12-minute first-treatment floor** is now recorded in `docs/conditioned_run.md`. The older
  15-minute rule would drop two windows (13.0 and 14.9 min).
- **"Amplitude" = cells ÷ width.** That is your definition. Two reviewers asked for a name that
  cannot be read as fluorescence amplitude (for example "recruitment rate"). The text keeps your
  word and says it is unrelated to fluorescence amplitude.
- **Chaining in the width measure:** the widest calls span 64.8 s (rate+context), and the
  count-each-cell-once revision is still unmerged.
- **Proposed and not adopted:** locust's minimum distance of 128 frames (unbracketed), SPIKE-synch
  minimum events 3 → 2, and rate+context merge gap 3 → 8 s.
- **Sliding mode:** `docs/goals/coded-detector-optimization.md` still says the sliding switch "is NOT
  on yet", while the recorded-data run used sliding. Either the goal page is stale or the switch
  needs recording as landed.

## 4. Questions for the producer and for correspondents

- One analysed TTX-first recording has never been screened for floor pinning, and two recordings
  with sub-cut pinning were kept. Is that final?
- Which MATLAB release produced the `findpeaks` widths? The manuscript needs it for the software
  citation.
- CICADA: nobody has asked its authors how they want the software cited, or which version was
  ported.

## 5. Why the section order differs from your list

Your list runs: data, synthetic data, optimization, training, benchmark, scoring parameters, knobs,
real data, width and amplitude. The section follows dependency instead: data → synthetic
recordings (which is where the benchmark and its derivation live) → coded detectors (the knobs) →
scoring → optimization → learned detectors (training) → comparison → recorded data → width and
amplitude. Optimization cannot be stated before its objective, its limits and the parameters it
moves, so taking your order literally would put each use before its definition. Every item on
your list is answered; "the benchmark" is read as the synthetic benchmark recording and its
derivation, with the coded-versus-learned comparison as its own section.
