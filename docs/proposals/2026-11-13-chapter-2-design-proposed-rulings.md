# Chapter 2 design: proposed rulings on synthetic sets and on scoring detectors

**Use this page when** you are deciding how Chapter 2 of the dissertation exercise builds its
synthetic data and scores detectors on them, or you want to know which of those choices Tony has
ruled on.

> Working material, not murderboarded. Written 2026-11-13 by the Chapter 2 session, from the
> handoff of the same day
> (`docs/handoffs/2026-11-13-chapter-2-synthetic-sets-and-detector-scoring.md`, in pull request
> #929 and not on `main` when this was written). **Nothing here is decided.** Each
> section ends in a ruling asked of Tony; a ruling he accepts becomes a decision record in the
> pull request of the first work that reads it.

**What was read for this page:** `FOUNDATIONS.md`; the goal page
[`goals/synthetic-validation.md`](../goals/synthetic-validation.md); the decision records linked
below; the route page [`pipelines/stream-readiness.md`](../pipelines/stream-readiness.md); the
bench-set builder, measuring tool and nine records of pull request #929; and the handoff.
**Not read:** Chapter 1's text (pull request #919). Its results are taken from the goal page,
which states the same derivations, and from the handoff's index of the chapter. The papers cited
by the decision records were not opened for this page; they are cited through the record that
read them.

Abbreviations: **F1**, the harmonic mean of recall and precision; **ROI**, region of interest
(one imaged cell); **DI** and **MALE**, the two groups of the default folder; **4x** and **3x**,
the two event-detection thresholds the producer ships (4 and 3 times the noise estimate);
***J***, the largest shift, in seconds, that a surrogate applies to one cell's event train.

## The frame: a procedure, with the current folder as its worked example

Three facts set what Chapter 2 can deliver.

- **The data will change.** The default folder's own note says four more MALE recordings are
  expected and a later folder will supersede it. Tony, 2026-11-13: retracking is in progress and
  the old data will be replaced
  ([record](../adr/2026-11-13-43ba-the-september-bench-is-stale-and-is-not-re-measured.md)).
- **The one pass already run was built on the September bench.** Each bench set of pull request
  #929 is a September bench module executed again with its measured values replaced. It still
  inherits the false-call limits, the search grids, the outer participation ratios and the
  recording length, and that record now calls the September bench stale.
- **The output is a map, not a ranking**
  ([the synthetic-first record](../adr/0021-the-toolset-is-validated-on-synthetic-data-first-with-coded-detectors.md),
  decision 3; Tony, 2026-10-20, no ranking of detectors in documents).

So Chapter 2's product is **a procedure that takes any folder's measured record and returns
synthetic sets, tuned settings and a capability map**, with every chosen input named. The numbers
it prints for the tracked cohorts are an example and are re-derived when the folder changes.

## The rulings asked, in the order they depend on each other

| # | Question | Proposal in one line |
|---|---|---|
| 1 | Is the per-stream bench one cell of the capability map, or a separate instrument? | One generator and one scorer. The map is the instrument; the folder's own values are one named point on it |
| 2 | What is the objective? | Recall per source, at a setting that keeps false calls on the negative within a stated limit. F1 is reported beside it |
| 3 | What are the negatives? | On synthetic data, two: a twin with nothing planted, and the rate-matched shift. The gap between them is measured |
| 4 | How does a measurement become a generator input? | Resample mice, not recordings; draw each synthetic recording's parameters from that; no per-group sets |
| 5 | What stays chosen? | Each chosen input becomes a swept axis with an argued range, or a measured value |
| 6 | How are the sets made hard enough? | Each axis runs until the detectors fail; the map reports where |
| 7 | How is tuning made fair and bounded? | Equal budget; an unbracketed setting is not a proposal; selection and confirmation on different draws |
| 8 | What is a real difference? | Paired over the same recordings, with the number of draws set from the interval wanted |
| 9 | What shows a setting generalises? | One column on a generator that differs in two stated ways |
| 10 | Are 3x and 4x one dataset or two? | Deferred, with the test that decides it |

## 1. The instrument: one generator, one scorer, and the folder's point on the map

**The tension.** The pass of 2026-11-12 tuned every detector to the highest mean F1 on a bench
set. That is the older goal
([`goals/coded-detector-optimization.md`](../goals/coded-detector-optimization.md)). The
synthetic-first record asks for a capability map per detector over conditions, with the same
tuning budget in every condition, recall per source, false calls on the rate-matched negative,
and one column on a generator the detectors were not tuned on.

**Proposed.** They are two uses of one instrument, and the second serves the first.

1. **The capability map is the instrument.** A condition is one setting of the generator. For
   each condition and detector the map holds recall per source at a setting that meets the
   false-call limit (section 2).
2. **A folder's measured values are one named condition**, called the folder's point. Tuning for
   the real run (stage 5 of the route) is the map's tuning at that point, with nothing separate
   about it.
3. **One generator and one scorer serve both.** No bench module holds constants of its own.
   `bugarach.stream_profile` was written for this and the bench sets are a step toward it; the
   step still owed is a generator that does not execute the September modules.

**Set aside:** keeping the per-stream bench as a separate instrument. Two instruments drift. On
2026-11-11 the recovery scripts were found typing 33 cells and 0.0096 Hz where the benches held
32 cells and a measured background per stream (route page, stage 2).

**Cost.** The builder in pull request #929 is kept as working material and is not the
foundation. The generator gains sources (section 5) before the map is run.

**Ruling asked:** is the capability map the one instrument, with a folder's values as a point on
it?

## 2. The objective: recall at a stated false-call limit

**What is wrong with mean F1 here.** On the nine sets most tuned detectors score 0.97 to 1.00
(handoff, section 4). The sets plant no decoys, as ruled, and no rate-matched negative exists
yet. So precision is measured only against background onsets in a recording that has events, and
it is close to 1 for any setting. F1 then follows recall alone and every setting that finds the
events ties.

**Proposed.**

1. **The primary score is recall per source at each condition**, for the setting that maximises
   it **subject to** false calls per hour on the negative staying within the limit. A setting
   over the limit is not a candidate, whatever its recall.
2. **F1 is reported beside it**, for continuity with the September records, and is not what a
   search maximises.
3. **A pair of close events is scored one to one**, as
   [the tuning record](../adr/0010-tune-train-and-review-against-the-data-as-they-are.md)
   decision 3 rules: a call that joins two events is one hit and one miss. The share of pairs
   split at each separation is reported as its own column (`bugarach.close_events` computes it).
4. **Planted events under a recording's floor stay "don't care"**
   ([the elevated-rate record](../adr/0009-the-bench-keeps-its-elevated-rate-test-in-a-recording-of-its-own.md),
   decision 2).
5. **The limit is one number, stated in calls per hour on the negative of section 3**, the same
   for every detector, stream and condition. The three inherited limits were measured on benches
   with decoys.

**What I would measure before proposing the number.** The floor rule already uses one chance
call per hour
([the floor record](../adr/0008-the-event-floor-is-set-per-window-from-its-own-null.md)). A
detector that honours the floor should sit near that on the negative, but merging and each
detector's own context move it. The first experiment (section 3) gives every detector's
false-call rate on the negative at its shipped setting. The number is proposed from that table.

**Set aside:** the area under a recall against false-call curve. It hides the operating point,
and the real run needs one setting.

**Ruling asked:** is the objective recall per source under one false-call limit, with the limit
set after the negatives are measured? The elevated-rate record, decision 4, says changing a
limit takes its own ruling; this is that request.

## 3. The negatives: a twin for truth and a shift for what real data allow

**What is ruled.** A negative keeps each channel's own rate and the shared slow change in rate
and destroys the alignment between channels
([the decoy record](../adr/0019-the-decoys-are-retired-negatives-are-rate-matched.md),
decision 2). It is a tool that takes any recording of event times.

**The gap in that ruling on synthetic data.** A shifted copy of a recording with planted events
still holds every coordinated onset, scattered. The floor record says so and calls it
conservative. On synthetic data a better negative exists: the same background with nothing
planted. On real data only the shift exists.

**Proposed.**

1. **The tool** is `bugarach.negatives`: event times per channel and a duration in, matched
   negatives out, no labels and no export contract needed. Its default construction is the
   per-channel rigid shift at *J* = 20 s, which is the floor's own null
   (`event_floor.rigid_frames`).
2. **On synthetic data every recording has two negatives**: its **twin** (same background draw,
   nothing planted) and its **shift**. False calls are counted on both.
3. **Chapter 2 reports the difference between them**, per condition. That difference is the bias
   of the only negative real data have, and Chapter 3 needs it to read its own false-call rates.
4. **A second construction is offered for a sensitivity check and not for scoring**: dithering
   in operational time, which `bugarach.surrogates` already has. One scored negative keeps the
   limit of section 2 a single number.
5. **The tool's own test**: on a simulated recording with a planted shared slow change in rate,
   the pair excess at 60 s bins is kept and the pair excess at 1 s bins goes to that of
   independent cells.
   [The false-alarm record](../adr/0006-a-false-alarm-is-coincidence-the-event-rates-explain.md)
   measured this for the rigid shift on real recordings (the 1-minute reading went from 2.54 to
   2.48 on fast). The simulator has no shared slow change yet (goal page, *What the tree has*),
   so that generator change comes with the tool.

**This is the first build and needs no ruling to start**; the handoff says so and the decoy
record owes it. Its first result is the table section 2 waits for.

**Ruling asked:** on synthetic data, are false calls counted on both the twin and the shift,
with the shift as the scored one because it is the one real data have?

## 4. From measurements to a generator: resample mice, and no per-group sets

**What the nine records show.** Read from `docs/learned/bench_sets/` in pull request #929.
Background rates in Hz per cell, with each record's own 95 % bootstrap interval.

| Set | Recordings | Quiet background | Busy background |
|---|---|---|---|
| fast, all | 12 | 0.0052 (0.0032 to 0.0115) | 0.0167 (0.0087 to 0.0682) |
| fast, DI | 5 | 0.0035 (0.0024 to 0.0667) | 0.0667 (0.0035 to 0.0727) |
| fast, MALE | 7 | 0.0060 (0.0035 to 0.0100) | 0.0129 (0.0069 to 0.0137) |
| slow, all | 12 | 0.0083 (0.0052 to 0.0109) | 0.0149 (0.0106 to 0.0253) |
| slow, DI | 5 | 0.0079 (0.0037 to 0.0248) | 0.0248 (0.0079 to 0.0269) |
| slow, MALE | 7 | 0.0094 (0.0057 to 0.0110) | 0.0116 (0.0103 to 0.0132) |
| combined, all | 12 | 0.0150 (0.0093 to 0.0194) | 0.0307 (0.0189 to 0.0978) |
| combined, DI | 5 | 0.0104 (0.0061 to 0.0933) | 0.0933 (0.0104 to 0.1110) |
| combined, MALE | 7 | 0.0168 (0.0111 to 0.0194) | 0.0213 (0.0181 to 0.0255) |

- **On every DI set the quiet interval contains the busy value and the busy interval contains
  the quiet value.** With 5 recordings the two quartiles are not two measurements.
- **Those intervals are still too narrow.** The bootstrap resamples recordings. DI's 5
  recordings come from 3 mice, and recordings of one mouse are not independent.
- **The one place the pass found a group needing its own settings rests on this.** rate+context
  tuned on all recordings scored 0.706 on the fast DI set against 0.980 for the DI-tuned
  setting (handoff, section 4). The DI set's busy background is 0.0667 Hz against MALE's
  0.0129 Hz. That is a difference in background level, carried by a quartile of five values.

**Proposed.**

1. **No per-group sets.** Background level is an axis of the map (section 6), and its range
   spans what the recordings show. This is what
   [the treatment-period record](../adr/0013-the-bench-simulates-treatment-periods.md) already
   rules for treatment backgrounds: levels that span the groups, never a group. It also keeps
   the instrument clear of
   [the group-comparison default](../adr/0017-group-and-treatment-comparisons-default-to-fireflies.md).
2. **Uncertainty is carried by resampling mice.** One draw resamples the folder's mice with
   replacement and measures the whole parameter vector on that resample, so values that move
   together stay together. Each synthetic recording at the folder's point is built from one
   draw. Point values are kept only for a named reference recording.
3. **Known biases are inverted where a derivation exists and carried where it does not.** The
   coordination-rates tool's participant count is corrected by its window-sharing term (goal
   page, *Aim 0, the predictions*). Jitter comes from the correlogram tool, whose calibration on
   this generator is still owed (goal page, plan item 1); until it is done, jitter is a swept
   axis around the measured value.
4. **A record states what its folder cannot support.** If the interval of any generator input
   contains the neighbouring level of its own axis, the record says so in a caveat, and that
   input is swept and not fixed. The current caveat triggers below 4 recordings and did not
   trigger for DI's 5.

**Cost.** The measuring tool changes: mouse-level resampling, a caveat rule, and the count of
bootstrap draws that failed (they are dropped silently now). The nine records are re-measured.

**Ruling asked:** are per-group sets dropped in favour of a background axis, and is uncertainty
carried by resampling mice?

## 5. What stays chosen: every chosen input is named, and swept or measured

Each row is an input the pass of 2026-11-12 inherited from the September bench.

| Input | Now | Proposed |
|---|---|---|
| Outer participation levels | September's ratios to the measured middle level | Planted relative to each recording's floor: one cell under it, at it, one over it, then the measured value and above (the tuning record, decision 5, already plants the boundary this way for training) |
| Recording length | 45 minutes | The folder's own baseline window length, measured. The default folder's windows are 20 minutes (`win = "win20min"`) |
| Events per recording | Measured events per hour times the length | Unchanged, at the new length |
| Number of sources | One | An axis: one and two. The synthetic-first record's premise is two or more, and the generator plants one |
| Membership | A fresh random set of cells per event | An axis: random, and a fixed assembly (settled on the goal page, 2026-10-23) |
| False-call limits | Three limits measured on benches with decoys | One limit (section 2) |
| Starting settings and grids | September's | Grids set so that every search is bracketed (section 7) |
| Background grid | September's | The background axis of section 6 |

**Cost.** The generator gains a `source` on each planted event, several sources, an assembly
mode and a shared slow change in rate. The goal page lists all four as open work that needs no
ruling. A shorter recording holds fewer events, so more recordings are needed for the same
interval (section 8).

**Ruling asked:** is each inherited input replaced as in the table? The two that change the
most numbers are the recording length and planting participation relative to the floor.

## 6. Difficulty: every axis runs until the detectors fail

**The problem.** A set on which everything scores 0.97 to 1.00 compares nothing.

**Proposed.**

1. **The axes are the ones already ruled in**: participation relative to the floor; separation
   of neighbouring events at 0.5, 1, 2, 3 and 5 s
   ([the close-events record](../adr/0022-close-events-are-a-bench-axis-the-event-definition-stays-at-2-s.md));
   background level, with the elevated-rate recording as its top; jitter at 1, 2 and 4 times the
   measured value; one source or two; random or fixed membership; shared slow change in rate,
   off and on.
2. **Nothing is planted that is coordination and scored as false.** Every axis either makes true
   events harder to find or makes the background busier.
3. **The design is a star, not a full grid, for the first map**: each axis swept alone from the
   folder's point, plus named corners. The treatment-period record made the same choice (9
   conditions, not 27). The goal page's plan says factorial; the star is proposed as the first
   map because it can be run in days.
4. **Each axis is extended until the best detector's recall falls below one half.** The map then
   reports, per detector and axis, the level at which recall crosses one half and the level at
   which it crosses 0.9. Those crossings are the capability statement. A condition where every
   detector is above 0.97 is reported as not separating them.

**Ruling asked:** is the first map a star design around the folder's point, with each axis run
until recall falls below one half?

## 7. Tuning: equal budget, bracketed, and confirmed on other draws

**Why settings left their grids.** Merge gaps went to 0, windows from 2 s to 0.5 s, and
SPIKE-synch's time step to its lower cap of 0.0008 s (handoff, section 4). With close events
planted and no negative that prices an extra call, a shorter window and no merging only ever
gain recall. The objective of section 2 adds the missing cost.

**Proposed.**

1. **The same budget for every detector in every condition**: the same number of evaluations
   and the same selection recordings.
2. **A setting at the edge of its grid is not a proposal.** The grid is extended and the search
   repeated, or the setting is fixed by a stated rule, as the floor record fixes the minimum
   participation.
3. **Selection and confirmation use different draws**, and a proposal is the confirmed score.
   Confirmation on the same generator guards against fitting noise; section 9 guards against
   fitting the generator.
4. **Compute is part of the record.** In one search 3 evaluations took 80 of 130 minutes. Each
   evaluation's time is stored, and a setting whose evaluation takes more than ten times the
   search's median is reported with its cost beside its score.

**An open point this section cannot settle.** The close-events record keeps the event
definition at the 2 s window. The search of 2026-11-11 found that only a 0.5 s window splits
pairs 1 s apart. Whether a detector's window may be searched below the window that defines an
event is Tony's, and that record says it is decided after the revised export is re-measured.
Until then the proposal is to search the window and report both.

**Ruling asked:** are an equal budget, the bracketing rule and separate confirmation draws the
tuning protocol?

## 8. Comparison: paired, with the draws counted in advance

**What is ruled.** No ranking of detectors in documents.

**Proposed.**

1. **Every detector is scored on the same recordings**, and a difference between two detectors
   or two settings is a paired difference over those recordings, with a bootstrap interval over
   recordings.
2. **The number of recordings is set from the interval wanted.** For a recall near one half, a
   95 % interval of plus or minus 0.05 needs about 400 scored events in the cell; plus or minus
   0.07 needs about 200. The close-pair column of the first pass had 8 to 29 pairs a cell,
   which gives plus or minus 0.18 to 0.35.
3. **A difference is called real when its paired interval excludes zero and it exceeds the
   draw-to-draw spread** of the same detector on fresh draws. The spreads of 2026-09 (0.010 F1
   for the learned models, 0.003 for coded detectors) were measured on the September bench and
   are re-measured on the new sets before any difference is reported.
4. **The map is reported as crossings (section 6) with intervals**, detector by detector, and
   no table orders the detectors.

**Ruling asked:** is a real difference a paired interval that excludes zero and exceeds the
re-measured spread, with at least 200 scored events in a cell?

## 9. Generalisation: one column on a generator that differs in two stated ways

**What is ruled.** One column of the map is scored on a generator the detectors were not tuned
on, and the membership rule serves as that column (goal page, *Settled*).

**Proposed.**

1. **The held-out generator differs in membership and in the shape of the jitter.** Chapter 1's
   first stated limit is one generator with Gaussian jitter (handoff, section 3). Tuning uses
   random membership and Gaussian jitter; the held-out column uses a fixed assembly and a skewed
   onset spread of the same standard deviation.
2. **A setting is reported with its loss on that column**, and a setting that loses more than
   the spread of section 8 is marked as fitted to the generator.
3. **What must hold on real recordings before a setting is trusted is Chapter 3's**, and is
   listed here only so the two chapters agree: false calls on the shifted negative within the
   limit; the parameters re-measured from the calls inside the intervals of the first
   characterization; and the detectors' agreement with each other, reported and not scored.

**Ruling asked:** does the held-out column change membership and the jitter's shape together?

## 10. One threshold or two: deferred, with the test that decides it

The 3x searches were still running when this was written. The producer ships both thresholds,
and which events a stream holds is the producer's statement
([the streams record](../adr/0023-bugarach-does-not-combine-streams-the-export-is-final.md)).

**Proposed.** Each threshold's folder is characterized. If every generator input of the 3x
record lies inside the mouse-level interval of the 4x record, one set serves both. If not, the
threshold is a second folder's point on the same map, tuned on its own.

**Ruling asked:** none yet. The proposal is to decide by that test once the 3x records are
committed.

## The order of work if these are accepted

1. The rate-matched negative tool and its table of false calls at the shipped settings
   (needs no ruling; started first).
2. The measuring tool's changes of section 4, and the records re-measured.
3. The generator's sources, assembly mode and shared slow change in rate.
4. The first map, as a star around the folder's point.
5. The chapter, written as Chapter 1 was: predict, then simulate to check.

No search is run before sections 1, 2 and 7 are ruled on.
