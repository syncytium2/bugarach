# Handoff: Chapter 2, from measured parameters to synthetic sets, and how detectors are tuned and compared on them

**Use this page when** you are the session starting Chapter 2 of the dissertation exercise, or
you want to know what Chapters 2 to 4 are meant to hold and what is already decided for them.

> Working material, not murderboarded. Written 2026-11-13 by the session that ran the route
> once on the new default (PRs #928 and #929). It is a brief for work that has **not started**,
> so it sits here and not at the repository root, where a handoff means work in flight.
> Every claim about the tree was checked on the day against branch `synth/per-group-benches`
> and, for Chapter 1, against branch `synth/dissertation-chapter-aim0`. **A linked file wins**
> where this page and it disagree.

Abbreviations: **ADR**, an architecture decision record (`docs/adr/`); **F1**, the harmonic
mean of recall and precision; **ROI**, region of interest (one imaged cell); **DI** and
**MALE**, the two groups of the default folder; **4x** and **3x**, the two event-detection
thresholds the producer ships (4 and 3 times the noise estimate).

## 1. The outline, as Tony gave it on 2026-11-13

| Chapter | What it holds | State |
|---|---|---|
| 1 | Model-free characterization tools, each predicted from planted parameters and then tested by simulation | Written 2026-10-29; `docs/dissertation/chapter-1-aim0.md` on branch `synth/dissertation-chapter-aim0`, PR #919, open, **not on `main`** |
| 2 | **This handoff.** How to build synthetic data from the parameters Chapter 1's tools measure, and how to tune, characterize and compare detectors on those data | Not started. A first, unprincipled pass through the mechanics exists (section 4) |
| 3 | Applying it to real data, **baseline only** | Not started |
| 4 | How to assess a treatment that may itself change the properties of coordination | Not started; partly ruled already (ADR-0013, ADR-0008 decision 4) |

Tony's words for 3 and 4 were tentative (*"i guess chapter 3 would be..."*, and Chapter 4 ended
in a question mark). Treat the outline as his current intent, not a ruling.

**The dissertation is an exercise, with no committee** (Tony, 2026-10-29). Write to that
standard, with sources read and claims checked, and state gaps as open work. Do not frame
anything as owed before a submission.

**How the chapters sit on the goal page's aims** (my reading, not Tony's ruling). The goal page
[`goals/synthetic-validation.md`](../goals/synthetic-validation.md) has Aims 0 to 3. Chapter 1
is Aim 0. Chapter 2 covers what that page calls Aim 1 (recover the parameters and find where
they stop being identifiable) as far as the generator needs it, and Aim 2 (a capability map per
detector). Chapter 3 is the real-data run that ADR-0021 puts after the synthetic validation.
Aim 3 (close the loop on a held-out synthetic recording from a different generator setting)
belongs at the end of Chapter 2 or the start of Chapter 3; that placement is open.

## 2. Tony's statement of the pipeline

Chapter 2 exists to make this principled. Tony, 2026-11-12:

> we characterize the properties of the data based on their temporal relationship without
> hypotheses about the nature of coordination. we use those characterizations to build
> synthetic data to optimize and train the detectors.

The route in his words: characterize the raw coordination, model-free; build synthetic sets
with known truth; optimise and train detectors; evaluate; iterate; then process the original
data.

## 3. What Chapter 1 gives Chapter 2

Read the chapter itself first; this is an index into it.

| Chapter 1 result | Where | What Chapter 2 does with it |
|---|---|---|
| The coordination-rates tool's participants, event rate and coordinated onset rate are predicted from the planted values, and its participant undercount at wide jitter is derived | sections 1.4.1 to 1.4.5 | These are the measured parameters a generator is built from. Their known biases must be inverted or carried, not ignored |
| A joint fit across the tool's windows recovers jitter from 0.2 s up, for events of 10 or more cells. It cannot read jitter per recording at realistic values (0.10 to 0.15 s, 7 cells) | section 1.4.6, 1.4.7, limitation 3 | The jitter that drives the benches comes from the correlogram tool instead, whose calibration on this generator is still owed (goal page, plan item 1) |
| Chance clusters at a threshold follow a closed form, and a fixed threshold does not transfer across backgrounds | section 1.5.1 | The basis for a per-recording floor (ADR-0008) and the reason a busy background removes low-participation events from scoring |
| Two events closer than a tool's bins are counted as one. The count detector's 3 s merge gap over 2 s bins joins events up to about 5 s apart; any method could separate them at 0.26 to 0.76 s | section 1.6 | The derived limit for the close-events axis (ADR-0022). It predicts what the searches found (section 4) |
| Membership and order tests, and how many events each needs | section 1.7 | What a generator with fixed assemblies or a latency template must plant for those structures to be testable at all |
| "One generator" as the first limitation: one source, Gaussian jitter, one participant count per source, random membership | section 1.8.4 | ADR-0021's premise is **two or more sources**. Chapter 2's generator has to get there |
| The shared-modulation prediction: shared slow rate change adds pair excess that grows with the window, while coordination levels off | section 1.8.5, "further out" | The theory behind the rate-matched negative (ADR-0019). Not done |

**Chapter 1 has nothing on scoring.** It does not mention decoys, negatives for detector
scoring, F1 or false-alarm limits, and its scope statement leaves out detector recall in a
continuous recording. Scoring lives only in the ADRs and run records. Pulling it into one
argued account is Chapter 2's job.

## 4. What exists already: one pass through the mechanics, 2026-11-12 and 13

A session ran the whole route once on the new default. It shows the machinery works and shows
where the design is missing. It is on branch `synth/per-group-benches`, draft PR #929, which
sits on draft PR #928 (the new default). **Nothing is merged and nothing is adopted.**

**The data.** The default is the table `tracked_cohorts` in `current_export.toml`: 12 recordings
of two tracked cohorts (DI 5 recordings from 3 mice, MALE 7 from 4), three streams shipped by
the producer (fast, slow, combined), threshold 4x. Its sibling `tracked_cohorts_3x` is the same
at 3x and is declared read-by-name.

**The tools built.**

| Tool | What it does |
|---|---|
| `tools/measure_bench_sets.py` | Measures a **bench set** per stream and per set of recordings (all, DI, MALE) with the route's stage 1 functions, and writes a record: `docs/learned/bench_sets/<stream>_<set>.json` |
| `bugarach.bench_sets` | Builds a bench module from a record, so a search takes a set by name (`--bench fast_di`). No decoys; the set's own measured gaps and event rate |
| `tools/search_all_settings.py --bench <set> --sliding` | The settings search, unchanged, run on a set |
| `tools/cross_score_sets.py` | Scores each set's proposed settings on every set of the same stream, on fresh seeds |
| `tools/greatlakes/` and [`greatlakes/RUN_2026-11-12_set_searches.md`](../greatlakes/RUN_2026-11-12_set_searches.md) | Job files and a run sheet for the university cluster. Untested; nothing has run there |

**The 4x result** ([record](../learned/runs/2026-11-12-set-searches/README.md)). Nine searches,
18 to 178 minutes each on 11 workers.

- On slow and combined, a setting tuned on any set scores within 0.008 mean F1 of the others.
- On fast, rate+context and SPIKE-synch have no setting that serves both groups' sets:
  rate+context tuned on all recordings scores 0.706 on the DI set against 0.980 for the
  DI-tuned setting.
- LoCo and the count detectors barely move across sets.
- The split by group describes synthetic sets. It tests nothing between the groups (ADR-0017).

**The 3x run** was started on 2026-11-13 at 7:45 AM EST and was three searches into nine when
this was written. Its bench records and stage 1 records exist only in a scratch checkout on the
workstation until that session commits them to #929. Check that PR before assuming either way.

**What the pass exposed.** These are the questions Chapter 2 answers.

1. **The sets no longer separate the detectors.** Most tuned detectors score 0.97 to 1.00. A
   bench at ceiling compares nothing.
2. **There are no negatives.** The only negatives scored are a recording with nothing planted at
   the quiet background, and the elevated-rate recording (ADR-0009). The rate-matched negative
   ADR-0019 calls for is not built.
3. **Settings run to the edges of their grids.** Every detector's search ended unbracketed on at
   least one setting. Merge gaps went to 0, windows from 2 s to 0.5 s, and SPIKE-synch's time
   step to 0.0008 s at its low cap.
4. **Parameter uncertainty is dropped.** Each set is built from point values. The records carry
   bootstrap intervals that the generator does not use. DI's busy background on fast (0.067 Hz
   against MALE's 0.013 Hz) is a quartile of five values, and it drives the only disagreement
   between the groups' sets.
5. **Some inputs are chosen, not measured.** The outer participation levels keep the September
   benches' ratios to the measured middle one. The three false-alarm limits, the starting
   settings, the grids and the recording length are inherited from the September benches.
6. **Tuning and testing share one generator.** Fresh seeds guard against fitting noise, not
   against fitting the simulator.
7. **The close-pair column is thin:** 8 to 29 pairs a cell in the cross-score table.
8. **A few evaluations dominate the run time.** In one search, 3 evaluations took 80 of 130
   minutes. Which setting does it was not identified; SPIKE-synch's small time step is the
   suspect.

## 5. What is already decided, and must not be re-decided

Read each ADR; this table is a pointer.

| Ruling | Source |
|---|---|
| A false alarm is a coincidence the event rates explain. A call where coordination is present is not a false alarm | ADR-0006 |
| The minimum participation is the larger of 3 ROIs and the window's own chance floor (at most 1 chance call per hour, 2 s window, per-ROI shifts within ±20 s). It is set by rule, not searched, in tuning and in scoring alike | ADR-0008 |
| Planted events under the floor are "don't care": out of recall and out of precision, and counted in every report. The elevated-rate test is a recording of its own. The false-call limits stand and are not loosened to pass a result | ADR-0009 |
| Tune against the data as they are; planted gaps come from gaps measured in real baseline windows without a detector | ADR-0010 |
| The bench simulates treatment periods, at rate-course levels that span the groups, never per group. Coordination in the treatment segment is centred on baseline and swept | ADR-0013, accepted as amended 2026-11-11 |
| Group and treatment comparisons are `fireflies`' by default; a by-group split here is descriptive | ADR-0017 |
| **The decoys are retired.** A negative is rate-matched and carries no coordination: it keeps each channel's own rate and the shared slow change in rate, and destroys the alignment between channels | ADR-0019 |
| One route from a folder to calls, per stream | ADR-0020, [`pipelines/stream-readiness.md`](../pipelines/stream-readiness.md) |
| bugarach is a general toolset whose input is unlabelled multichannel event times. It is validated on synthetic data first. **The output is what each detector can do, condition by condition; it is not a ranking.** The premise is two or more sources. Coded detectors only. The first capability map has four detectors: CoactDetect, LoCo, binned SCE and count (sliding) | ADR-0021 |
| Close events are a difficulty axis at set separations, below 2 s included; the event definition stays at the 2 s window for now | ADR-0022 |
| bugarach does not combine streams; the export's combined stream is final | ADR-0023 |
| The learned models are on hold | Tony, 2026-10-22 |
| No ranking of detectors in documents | Tony, 2026-10-20, cited in ADR-0019 decision 3 |

**A tension to resolve early, with Tony.** The pass in section 4 tuned every detector to the
highest mean F1 on a bench, which is the older goal
[`goals/coded-detector-optimization.md`](../goals/coded-detector-optimization.md). ADR-0021 and
the synthetic-validation goal ask for a capability map per detector over a grid of conditions,
with the same tuning budget in every condition, recall scored per source, false alarms on the
rate-matched negative, and one column scored on a generator setting the detectors were not
tuned on. Chapter 2 should say how the two relate: whether the per-stream bench is one cell of
the map, or a separate instrument.

## 6. The questions Chapter 2 should answer

Each should end as a proposed ruling Tony can accept or decline, tied to a source or a
measurement.

1. **From measurements to a generator.** Which of Chapter 1's readings become generator inputs,
   and how their known biases are inverted. Whether a set samples its parameters from their
   uncertainty, recording by recording, or fixes them at point values. How few recordings can
   support a set (the DI sets have five).
2. **What stays chosen.** Participation levels, recording length, the number of sources. For
   each, either measure it or state it as a swept axis with its range argued.
3. **The negatives.** Build the rate-matched negative as a tool that takes any recording of
   event times, simulated or real. Say what each construction preserves and destroys, from the
   surrogate-null literature (ADR-0006's references; Chapter 1 section 1.2.3 and its surrogate
   figure). Check Chapter 1's shared-modulation prediction on it.
4. **The objective.** F1 at a false-call limit, recall against participation at a fixed
   false-call rate, or something else. How a pair of close events counts. What the false-call
   limit is and where it is measured, now that the limits in hand were measured on benches with
   decoys.
5. **Difficulty.** How to make the sets hard enough to separate detectors without planting
   anything that is coordination and scoring it as false. Candidates already ruled in:
   participation near the floor, close events, elevated rate, two sources, shared slow
   modulation.
6. **Tuning.** Why settings leave their grids, and what cost the objective is missing when they
   do. The same budget for every detector. Selection and confirmation on different draws.
7. **Comparison.** Paired over what; how many draws; what difference is real. The fair
   comparison of 2026-09 measured a draw-to-draw spread of 0.010 F1 for nets and 0.003 for coded
   detectors on the September bench; it needs re-measuring on the new sets.
8. **Generalisation.** One column scored on a generator the detectors were not tuned on, as the
   goal page already plans, and what must hold on real recordings before a setting is trusted.
9. **One threshold or two.** Whether 3x and 4x are two data sets to be characterized and tuned
   separately, or one axis. The 3x run in section 4 is the first evidence.

## 7. Chapter 3: real data, baseline only

- **Input:** the default dataset, named in every result (`dataset.default()`, `dataset.stamp()`).
  The export folder is the input, and no filter is added here.
- **What it is:** Chapter 2's protocol applied end to end to the baseline windows: characterize,
  build sets, tune, detect, then re-measure the parameters from the calls and compare them with
  the characterization.
- **What it cannot claim:** real recordings have no truth. ADR-0021 decision 7 says the export
  supplies realistic values only. Agreement between detectors, the rate-matched negative run on
  the real recordings, and the re-measured parameters are the available checks.
- **Groups:** a split by group is descriptive only (ADR-0017). If the chapter would state a
  difference between DI and MALE as a finding, stop and ask Tony first.

## 8. Chapter 4: a treatment that may change coordination itself

- **The problem as already ruled.** A treatment can change event rate, and may change any
  property of coordinated events (ADR-0013 decision 3, with Tony's words of 2026-09-28). So a
  detector tuned on baseline may fail in the treatment window for reasons unrelated to
  coordination, and a change in calls may be a change in rate.
- **What exists.** ADR-0013: treatment recordings with a baseline segment, a 2-minute wash-in
  and a treatment segment, rate courses at fixed multiples of baseline, coordination swept
  around baseline. ADR-0008 decision 4: every treatment window is scored under two floors, its
  own and the baseline's, and both are reported. The route's owed list (item 3) says the
  treatment recordings are built with synthetic courses and that five open points are Tony's.
- **The boundary.** Working out how to assess a treatment, on synthetic data, is bugarach's.
  **A finding about what a treatment does to the lab's recordings is `fireflies`' by default
  (ADR-0017).** Before Chapter 4 applies its method to real treatment windows, say so to Tony,
  name the default, and wait for his yes.
- **A known contamination stops the work** (CLAUDE.md). Check the notes on any treatment folder
  in `current_export.toml` before reading it.

## 9. How to run the Chapter 2 session

1. **Start from `main`,** claim on the local board with `Goal: synthetic-validation`, and read
   `docs/FOUNDATIONS.md`, the goal page, the ADRs in section 5, Chapter 1 from its branch, and
   the two run records in section 4. PRs #919, #923, #924, #926, #928 and #929 are all open;
   decide with Tony which must land first.
2. **Literature:** the master library is `01-lit` at the top of the Dropbox, with bugarach's
   shelf under it. Search it first. For a paywalled paper, resolve the DOI and give it to Tony,
   one at a time; he pulls it through the university library.
3. **First deliverable: a design document of proposed rulings,** one per question in section 6.
   No new searches and no chapter text until Tony has ruled. A ruling that settles how work is
   done becomes an ADR in the same PR as the first work that reads it.
4. **First build after that: the rate-matched negative tool,** applied to the existing bench
   sets. It is owed under ADR-0019, it needs no ruling, and it is the first experiment of the
   chapter.
5. **Then the chapter,** in the form of Chapter 1: predict, then simulate to check. Run the
   murderboard before handing over the document (`/murderboard`), and freeze the artifact while
   reviewers run.
6. **Compute:** the lab workstation. A full search of nine sets took about 12 hours at 4x. The
   cluster route is written and untested.
7. **Do not** retrain or score the learned models, plant decoys, add a filter on the export,
   rank detectors in prose, or act in interface2.

## 10. Where things are

| What | Where |
|---|---|
| Chapter 1 and its figures | `docs/dissertation/` on branch `synth/dissertation-chapter-aim0` (PR #919) |
| The theory and its checks | [`learned/synthetic_validation/`](../learned/synthetic_validation/README.md) |
| The goal, its plan and its settled items | [`goals/synthetic-validation.md`](../goals/synthetic-validation.md) |
| The route from a folder to calls | [`pipelines/stream-readiness.md`](../pipelines/stream-readiness.md) |
| Bench sets, records and the builder | `docs/learned/bench_sets/`, `src/bugarach/bench_sets/`, `tools/measure_bench_sets.py` (PR #929) |
| The 4x searches and cross-scores | [`learned/runs/2026-11-12-set-searches/`](../learned/runs/2026-11-12-set-searches/README.md) (PR #929) |
| Stage 1 records on the default | `docs/learned/runs/2026-11-12-stage1-tracked-cohorts-three-streams/` (PR #929) |
| The decoy ruling and the todo for its replacement | ADR-0019; `docs/todo/2026-10-23-rate-matched-negatives-and-the-bench-without-decoys.md` |
| The cluster | [`greatlakes/README.md`](../greatlakes/README.md) |
