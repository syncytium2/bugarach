# ADR-0010: Tune, train and review against the data as they are

## Status

**Proposed**, 2026-09-25. Drafted by the orchestrator at Tony's request (*"agree, draft one ADR
covering all of it"*), after the morning review of the final-parameters night. It becomes
Accepted when Tony rules on the open points at the end of this record.

**One record, six parts, on purpose.** This directory's convention is one decision per file. Tony
asked for one record because the parts are one decision: stop measuring detectors on a bench and
through a review tool that the real data contradict. The parts depend on each other. The bench
change (part 2) is what gives the merge penalty (part 3) and the participation training (part 5)
something to act on. The review-tool rule (part 6) decides what the first review of the result
shows.

**Revised the same day, before acceptance.** The first draft focused tuning on CoactDetect and the
chorus models. Tony then pointed out that nothing had been trained on realistic intervals, so every
ranking behind that focus came from the bench this record replaces. He asked instead to optimise the
full panel one last time on the new bench (*"cover our asses and optimize the full panel of
detectors one last time on the new real interval simulated data"*). Part 1 now says that.

It **amends** [ADR-0009](0009-the-bench-keeps-its-elevated-rate-test-in-a-recording-of-its-own.md)
without superseding it. ADR-0009's five decisions stand. What changes is a premise it took from the
bench as built: planted events at least 120 s apart.
[ADR-0008](0008-the-event-floor-is-set-per-window-from-its-own-null.md)'s floor is unchanged.

## Context

**The final-parameters night (2026-09-25) found no coded detector that beats CoactDetect.** Fresh-seed
F1 ([report](../learned/runs/2026-09-25-final-parameters/README.md)) on slow was 0.848 for
CoactDetect, against 0.846 for LoCo, 0.845 for SPIKE-synch and 0.845 for locust. On fast and
combined, LoCo was level with CoactDetect or slightly ahead. The intervals are roughly ±0.015 to
±0.03. Every other coded detector either sits within those intervals of CoactDetect or below it.
CoactDetect's shipped setting passes every budget on all three streams; four other shipped settings
do not. The chorus models were level with CoactDetect on fast and combined and 0.02 below on slow.
Tony, the same morning: *"I feel we have enough evidence to focus on coact detect and the learned
models."*

**Every ranking so far comes from a bench with events at least 120 s apart.** Among the learned
models, chorus has led each comparison: chorus_norm at 0.745–0.763 held-out F1 per fold in the fair
comparison's replicate draw (2026-09-18), against line_length at 0.661–0.725 and tube at
0.637–0.657, with CoactDetect at 0.744–0.752
([`replicate_summary.json`](../learned/tuned_vs_coact/fair_comparison_2026_09_18/replicate_summary.json)).
But chorus's lead over CoactDetect shrank each time the bench got fairer: +0.103 F1 untuned on the
retired home spec, nearly tied in the fair comparison, tied or behind on 2026-09-25. None of these
models, and none of the coded detectors, has been trained or tuned with events seconds apart, which
is where the families differ most: separating neighbours, and counting cells against a floor. Tony:
*"nothing has been trained on the realistic intervals."*

**The bench plants events at least 120 s apart; real events are often seconds apart.** In
`bench.BENCH_RECORDING` the minimum spacing is 120 s, and the scored recordings' neighbouring events
are 122 to 265 s apart (5th–95th percentile). On the 66 recordings of the default export, a
diagnosis on 2026-09-25 (`<darkroom>/bugarach/2026-09-25-floor-plus-one-review/diagnosis/`) found:

| Stream | CoactDetect calls that merge 2 or more distinct stripes | Gap between the merged stripes, median (5th–95th percentile) |
|---|---|---|
| fast | 14 of 356 calls | 4 s (3–5 s) |
| slow | 133 of 1,337 calls | 6 s (3–9 s) |
| combined | 162 of 1,340 calls | 5 s (3–9 s) |

On the combined stream, gaps between separate CoactDetect calls have a median of 34 s, and 115 of
1,192 are under 14 s. The close-events recording (`CROWDED_RECORDING`, minimum 14 s) plants no two
neighbours under 10 s apart. So the recordings every search optimises on cannot produce a merge, and
the one recording that can is a pass/fail check against the shipped setting, which already merges.
The scorer matches calls to events one to one (`score.score_detections`), so a merge would already
cost a miss, but only if two events are ever close enough to merge.

Two of these diagnosis numbers are measured through CoactDetect. Gaps between merged stripes are
capped by the call's width, 28 s at most. Gaps between calls are counted after merging. A
detector-free measurement is still needed (part 2).

**The same detector merges on one recording and separates on another.** Tony, on the review page
DI · senktide · combined: on 20250925_231 (20 ROIs) CoactDetect joins two distinct stripes into one
call, while on 20250926_237 (39 ROIs) it calls neighbouring stripes one by one. A bench that never
places events close together cannot tune that behaviour.

**Chorus cannot represent the floor.** `learn/nets/chorus.py` computes a vote per cell per time step,
then pools the votes into their mean, their spread and the mean of the top 4. All three are
fractions of the field, chosen so the model reads the same at any field size. The floor is an
absolute number of co-active ROIs. No fraction-only model can learn "at least 7 cells". Tony:
*"for chorus, reporting participation is not as important as learning participation."*

**The review tool filtered chorus's calls with a rule of its own.** `tools/detect_with_floors.py`
keeps a chorus, rate+context or locust call only when enough ROIs have an onset in
[onset, onset + max(width, 2 s)]. That window looks only forward, and chorus places its onset mid-stripe.
On 20250925_231, combined stream, it deleted 6 chorus_norm calls whose centred counts, 10 to 15 ROIs,
cleared floors of 10 and 12. Across the 66 recordings, it deleted 26 to 111 calls per stream and
chorus model that a centred count keeps. On the bench, by contrast, chorus's calls are never
filtered (`tools/score_bench_candidates.py`: the floor decides which planted events count). So the
chorus on Tony's review pages was not the chorus that earned its bench F1.

## Decision

1. **The full panel is optimised one last time on the realistic bench, and the focus is chosen from
   the result.**
   - **Coded:** all six detectors (CoactDetect, LoCo, binned SCE, rate+context, SPIKE-synch and
     locust) are searched on the fast, slow and combined benches.
   - **Learned:** chorus_norm, chorus_gain_norm, line (with its orientation channel) and tube are
     trained on all three benches, each with the participation changes its architecture allows
     (part 5).
   - **Final** means what the 2026-09-25 runbook defined: tuned under the definitions it is scored
     under, bracketed, confirmed on fresh seeds within every budget, and adopted by Tony.
   - **The focus is decided after the run**, by a rule fixed before it: a detector more than one
     noise unit behind the leader on at least two streams is dropped from further tuning. One noise
     unit is 0.01 F1, the draw-to-draw spread measured in the fair comparison. Dropped detectors stay
     scored, at their final settings, as comparators.
   - The four proposals the 2026-09-25 report found adoptable are not adopted. They were tuned on
     the bench this record replaces.
   - A shipped setting that fails a budget on the new bench is marked as out of budget wherever a
     user can pick it.

2. **The bench plants events at intervals measured in the real data.**
   - **Measured without a detector.** For each recording and stream: count ROIs with an onset
     inside the 2 s co-activity window, mark peaks at or above that window's floor, and take the gaps
     between neighbouring peaks. A detector's calls are not used, because merging hides the short
     gaps.
   - **Baseline windows only** (FOUNDATIONS §9), **per stream**: fast, slow and combined each get
     their own distribution.
   - **Planted gaps are drawn from that distribution**, replacing the fixed minimum of 120 s, in
     every recording with planted events: the scored recordings, the tail recording, and chorus's
     training recordings. Recording length is unchanged.
   - Chorus training and the CoactDetect search use the same generator, on disjoint seeds.

3. **A merge is penalised by scoring, and counted.**
   - Every planted event stays separately labelled, and matching stays one to one. With realistic
     gaps, a call that swallows two events costs a miss.
   - Every score reports a merge count: calls whose span contains two or more scored events.
   - The merge count has no budget of its own until the first run under this record has measured
     it.

4. **Rules the old spacing needed are retired.**
   - The constraint that no context may be longer than the planted spacing
     (`bench.context_fits_the_null`) is removed. A neighbouring event inside CoactDetect's context is
     realistic, and it is part of what the bench measures.
   - The close-events recording and its allowance (`CROWDED_RECORDING`, `MAX_CROWDED_DROP`) are
     retired, because the scored recordings now contain close events themselves. This is the ruling
     ADR-0009 decision 4 requires for changing a budget.
   - ADR-0009 decision 5's cap of 120 s on contexts stands. It is Tony's preference, not only a
     consequence of the spacing.

5. **Every learned model trained under this record learns participation.** Each model in the
   registry combines its cells into a fraction of the field (the chorus and line families by a vote
   per cell; tube and trace by averaging cells away early), so none can represent the floor's
   absolute count. Each model gets what its architecture allows:
   - **A count it can see** (every family). A pooled count, the sum of its bounded per-cell votes or
     its equivalent, and the recording's floor as an input. The sum is bounded by the number of ROIs,
     because each vote lies between 0 and 1. That keeps it clear of the unbounded sum that failed in
     `tiny`.
   - **Membership is trained** (the chorus and line families, which have per-cell votes). A per-cell
     term in the loss uses the bench's planted membership: a cell's vote is pushed high at an event
     that recruited it, and low otherwise. Tube and trace average cells away before any such stage,
     so they train without it.
   - **The boundary is planted.** Each recording plants events at its floor − 1, at its floor and at
     floor + 1, besides the higher levels. For training, events under the floor are labelled as no
     event. For scoring, ADR-0009 decision 2 is unchanged: they are "don't care".
   - **What counts as learned**, on the bench:
     - calls on under-floor events fall toward zero;
     - recall on events just above the floor holds;
     - the vote-derived count tracks the planted participants.
   - **The bar for the learned models:** beat CoactDetect's fresh-seed F1, with a paired interval
     above zero, on at least two streams, within every budget.

6. **The review tool shows what detectors call, and never changes it.**
   - **Each detector runs as it is defined and scored.** The floor belongs to the detector
     (ADR-0008). CoactDetect, LoCo, binned SCE and SPIKE-synch take it as their own minimum. A
     detector without a participation setting runs unfloored until it has one.
   - **The floor is shown, never applied.** Every call is drawn. Each call's participant count and
     its window's floor appear in the lane's label or hover text, never on the raster. One counting
     rule serves every detector, and it is stated on the page: ROIs with an onset in
     [onset − 1 s, onset + width + 1 s].
   - **Analysis and review read the same unaltered calls.** A floor-based count (verdict flips,
     calls lost at floor + 1) is computed beside the calls and labelled with its rule, and never
     replaces them.

## Consequences

- **Every tuned number gets a new baseline.** The 2026-09-25 report's adoption table becomes the
  record of a bench that no longer exists. Its shipped-point comparisons stay valid as history.
- **Floors must be re-measured** with `tools/probe_bench_floor.py`. Denser events raise a
  recording's chance floor.
- **Recall is measured on a harder task.** Some events will sit inside another event's context or
  within a call's width of a neighbour. That is intended.
- **Some published counts must be recomputed.** The 498 verdict flips of the 2026-09-25 real-data
  run and the floor + 1 shares for chorus, rate+context and locust were computed with the
  forward-only filter. CoactDetect's numbers stand, because its floor is its own.
- **Chorus lanes on review pages get busier.** They show every call the bench scores.
- **Floor + 1 stays evidence, not a rule.** It is re-examined on the corrected review, and adopting
  it would take its own record.
- **Work, in order:**
  1. Measure the intervals.
  2. Build the generator, the participation changes and the review-tool change.
  3. Re-measure the floors.
  4. One night: search the six coded detectors, train the four learned models, and score all of
     them on fresh seeds.
  5. Review all of them on the same rasters.
  6. Choose the focus by the rule in part 1.

  A full coded search took about 35 minutes per machine on 2026-09-25, running one process per
  detector, and a learned fit takes seconds on the GPU. So the panel fits in one night.

## Open for Tony before acceptance

1. **Pooling groups.** Pool DI, OVX, MALE and ORX baseline intervals into one distribution per
   stream, unless they differ materially. What counts as material is to be decided once the
   intervals are measured.
2. **Replace or mix.** Draw every planted gap from the real distribution (as written), or keep a
   share of isolated 120 s events as a reference.
3. **The review tool's counting window.** ±1 s around the call's span (as written), or another
   width.
4. **The learned models' bar** (part 5), as stated or otherwise.

**Carried over from the 2026-09-25 report**, because a full-panel search meets each of them again.
Unsettled, they would leave the run ending on the same list:

5. **A value at a hard limit** (a guard, `C_min` or merge gap of 0): does it count as bracketed?
   Five proposals were held back on this alone on 2026-09-25.
6. **CoactDetect's `alpha`**, which ran to the extension cap (1e-9) on fast and combined: take it
   out of the search, fix its value, or raise the cap.
7. **Contexts shorter than 20 s**, which fast LoCo's search reached by extension (5 s): allow them,
   or make 20 s the floor of the grid.
8. **The guard cap** (a guard at most a quarter of its context), which now reaches LoCo too:
   confirm it.

## References

- The final-parameters report: `docs/learned/runs/2026-09-25-final-parameters/README.md`.
- The floor + 1 review: `docs/learned/runs/2026-09-25-floor-plus-one-review/README.md`. Its
  diagnosis of the review tool and of merges: `<darkroom>/bugarach/2026-09-25-floor-plus-one-review/diagnosis/FINDINGS.md`.
- ADR-0006 for chance, ADR-0008 for the floor, ADR-0009 for the bench it amends.
