# Cover memo: the coordination-pipeline methods section

**For Tony, 2026-09-22.** This goes with `coordination_pipeline_methods.docx`. It holds what the
review found that is not manuscript text:
- code defects that stop results;
- design choices a referee will attack;
- decisions that are yours;
- why the section order is not your list's.

The murderboard run record is `docs/reviews/coordination_pipeline_methods_2026-09-22.md`.

## 1. Stop before reporting results: four code defects

Each of these makes a number the methods describe differ from the number the code produces. The
methods state the intended rule. Until each is fixed and the affected outputs are regenerated,
results for the detectors named should not be reported.

| # | defect | affects | fix |
|---|---|---|---|
| 1 | **LoCo and locust rates count the wrong calls.** Both run on the whole recording and tag each call with its raw *period*. `make_before_after_figure` counts every call in the period, then divides by the *analysis window's* duration. So calls from the first 2 min of treatment, and from baseline before its last 20 min, are counted against time that excludes them. The detectors already compute `in_stats_window`, but `emit` drops it. | before/after rates for LoCo and locust | carry the in-window flag into `detections.csv`, or drop out-of-window calls in `detect_folder._run_nested`; regenerate |
| 2 | **binned SCE's width and amplitude are measured over the wrong interval.** `measure_calls` uses onset to onset + width, which for binned SCE is the bin start plus the *spread of its events*, not the bin. In the fast stream, 157 of 1,665 binned SCE calls find no events, and 347 have a core of fewer than 3 cells, although every call has at least 3. `score.py` already fixed this for scoring with `extent_sec`, which `emit` does not export. | binned SCE width and amplitude | export `extent_sec`, measure over it, re-measure |
| 3 | **locust's threshold spans drug periods.** `threshold_scope="global"` pools baseline and treatment into one null. A treatment that raises the rate, such as senktide, both sets the bar and clears it more easily. In the cohort run, locust's fast-stream calls went from 998 in baseline to 2,763 under senktide, while CoactDetect's went from 428 to 317. | locust before/after rates | run `threshold_scope="regional"` (it exists), or drop locust from treatment contrasts |
| 4 | **Table 4's CoactDetect and LoCo settings are not the stored defaults.** `bench.OPERATING_POINTS` still holds the binned points, marked "not yet switched to sliding". The recorded-data run used a settings file, now committed as `docs/methods/recorded_data_detector_settings.csv`. Anyone running `bugarach detect` without that file gets different settings. | reproducibility of every CoactDetect and LoCo result | land the sliding switch in `OPERATING_POINTS`, or cite the settings file in every run record |

## 2. Design choices a referee will attack (the methods now disclose each)

- **Distractors are identical to planted 18% events and are scored as false alarms.** Detecting
  6-cell events gains 5 true positives and costs up to 6 false alarms, so the objective barely
  rewards seeing the most realistic event size, and F1 is capped at 0.83. Every search, limit and
  ranking inherits this. Give distractors a property a detector could reject (for example wider
  jitter), or report F1 without them.
- **No benchmark puts planted events on a treatment-rate background.** Detectors are tuned at
  baseline rates and applied across treatments that change the rate, so a change in call rate
  cannot be separated from a change in detector sensitivity.
- **Everything was tuned at 33 cells; the recordings have 9–61.** rate+context's threshold, the
  minimum-cells floors and SPIKE-synch's coincidence threshold are absolute in cells.
- **No statistics plan.** The section does not say how group and treatment effects are tested,
  how recordings from one mouse are handled (67 recordings from 36 mice), which detector is
  primary, or how multiplicity is controlled.
- **The close-events limit was reported, not applied, in the comparison.** It would have failed 19
  of 48 coded choices, and 16 of 48 in the replicate. The adopted CoactDetect and LoCo settings lose
  0.040 and 0.042 close-events F1 against their own sliding starting points, against a limit of
  0.02; they pass only because the reference is the binned default.
- **The learned detector run on recorded data used a 2 s merge gap; the re-selection chose 8 s.**
  Either justify 2 s or re-run at 8 s.
- **The width rule depends on the background rate.** At senktide rates the 0.5 s gap chains chance
  events: the widest "coordinated event" spans 64.8 s and 1,046 events. The rule has never been
  checked against planted events.
- **The benchmark constants were set from earlier data and re-checked by the same cluster method.**
  That method cannot see events under 4 cells, and its jitter includes chance onsets.
- **The Nadeau–Bengio factor √(3/7) was applied to every contrast**, including learned refits
  where the training-to-test ratio is below 1.
- **Judgement constants:** the 2.5 s matching tolerance (1.5 s until 2026-08-28), the admissibility
  margins, the 1.6× false-alarm factor, and the 1 s span and 0.5 s gap of the width rule.

## 3. Decisions that are yours

- **Participation 0.18 → 0.19** (your todo for after today's meeting). At 33 cells both give 6
  cells, so the planted events do not change. Whether anything else changes depends on what moves
  with it (the 30% and 10% levels, the random-number stream). Figure 1's tool now reads the levels
  from `BENCH_RECORDING`, so it follows.
- **The 12-minute first-treatment floor** is now recorded in `docs/conditioned_run.md`. The older
  15-minute rule would drop two windows (13.0 and 14.9 min).
- **"Amplitude" = cells ÷ width.** That is your definition. Four reviewers across two rounds asked
  for a name that cannot be read as fluorescence amplitude (for example "recruitment rate"). The
  text keeps your word and says it is unrelated to fluorescence amplitude.
- **Chaining in the width measure:** the count-each-cell-once revision is still unmerged.
- **Proposed and not adopted:**
  - locust: percentile 99.99, synchronous frames 2, minimum distance 128 frames (unbracketed);
  - SPIKE-synch: minimum events 2;
  - rate+context: merge gap 8 s.
  The methods say they were not adopted; reasons are on record only for locust.
- **The personal communication.** Kreuz is cited, not quoted, for the April 2026 exchange. Many
  journals want the person's written permission to be cited that way.

## 4. Questions for the producer and for correspondents

- **Pinning.** One analysed TTX-first recording, 20260629_314, came back clean from the per-ROI
  census, but a whole-frame scan ranks it as a candidate and the pixel-level test has not been run.
  Two recordings with sub-cut pinning were kept. Is that final?
- **Versions.** Which MATLAB release produced the `findpeaks` widths? Which PySpike and cSPIKE
  versions did the parity checks use?
- **CICADA.** Nobody has asked its authors how they want the software cited, or which version
  interface2 ported.
- **Sources.** Cossart et al. (2003) and Mao et al. (2001) are not on the shelf. The description of
  their method is second-hand, from the Methods paragraph the repo carries.

## 5. Why the section order differs from your list

Your list runs: data, synthetic data, optimization, training, benchmark, scoring parameters, knobs,
real data, width and amplitude. The section follows dependency instead:
1. data;
2. synthetic recordings (the benchmark and its derivation);
3. coded detectors (the knobs, all in Table 4);
4. scoring;
5. optimization;
6. learned detectors (training);
7. comparison;
8. recorded data;
9. width and amplitude;
10. limitations.

Optimization cannot be stated before its objective, its limits and the parameters it moves, so
your order would put each use before its definition. Every item on your list is answered. "The
benchmark" is read as the synthetic benchmark recording and its derivation. The coded-versus-learned
comparison is added as its own section, because it is how the learned detector used on recorded
data was chosen.

## 6. Stale notes found in passing (not fixed here)

- `docs/GLOSSARY.md`:
  - its "guard" entry says no operating point sets a guard;
  - its "merge gap" entry says binned SCE merges;
  - its "analysis window" means something narrower than the producer's window used here.
- `bench.NOT_SEARCHED["sync"]` and `docs/todo/2026-09-17-the-bench-does-not-put-events-on-the-frame-grid.md`
  both say the generator draws continuous times. It has rounded to the 0.1 s grid since 2026-08-13.
- `tools/search_all_settings.py`'s docstring says minimum cells and merge gaps are not searched.
  The search log shows both were.
