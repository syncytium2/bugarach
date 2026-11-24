# ADR 2026-11-24-1063: The benches cover the range the recordings show: a twin for every recording and a sweep along every feature

Status: Proposed, 2026-11-24

Drafted at Tony's request, after he read the per-recording figures behind Review A. Tony,
2026-11-24: *"these plots along with the other review material suggest that the bench[e]s need
to cover a wide range [of] features. females show the widest range in background, while males
show the widest range in excess pairs"*, and then *"we'll need a fairly detailed ADR to capture
this … otherwise there may be systematic failures, given the group patterns"*. Five points below
are the session's proposals and are marked as open; the rest follows from his two sentences.

The evidence is in
[`docs/learned/runs/2026-11-24-bench-coverage/`](../learned/runs/2026-11-24-bench-coverage/README.md):
a per-recording table (`coverage.csv`), the script that writes it, and its Figure 1. Every number
below comes from there or from a record it links, on the tracked cohorts
(`export_roi_apv+cnqx-then-gz-then-hik_di+male_thr4x_rigid_blanked_20261112_v2` and its 3x
sibling; 12 recordings: DI 5, MALE 7), baseline analysis windows only, at 4x unless it says 3x.

## Context

### What a bench set is today

The route builds one synthetic bench per stream (fast, slow, combined) and per set of recordings
(all, DI, MALE) at each threshold (`tools/measure_bench_sets.py`, `bugarach.bench_sets`; Tony,
2026-11-12). Each set is **one typical recording at two backgrounds**:

- one ROI (region of interest) count: the median over the set's recordings;
- one participation: the median participating-ROI count over the median ROI count, both from the
  per-recording measurement `tools/remeasure_bench.py` reads (`_values`);
- one coordinated-event rate and one gap distribution, pooled over the set's recordings
  (stage 1 intervals record);
- one jitter, from the pooled correlogram (stage 1 jitter record);
- two backgrounds, "quiet" and "busy": the 25th and 75th percentiles of the recordings'
  backgrounds. A recording's background is its mean onset rate per ROI minus its coordinated
  share (`tools/remeasure_bench.py`).

Searches tune each detector on a set's recordings and score it on fresh ones drawn the same way.
A setting is therefore chosen for the middle of the set, and nothing in the route reports how it
does on a recording far from the middle.

### What the recordings show

Within each group, every feature spreads widely, and the two groups spread on different features
(full table in the evidence folder):

| feature (4x) | DI, 5 recordings | MALE, 7 recordings |
|---|---|---|
| ROIs | 24 to 73 | 18 to 59 |
| background, combined (onsets per minute per ROI) | 0.36 to 6.7 (18-fold) | 0.65 to 1.5 (2.3-fold) |
| background, fast | 0.14 to 4.4 (30-fold) | 0.21 to 0.82 (4-fold) |
| coordinated events per hour, slow | 21 to 135 | 6 to 96 |
| participation, combined (median of event peaks) | 0.28 to 0.83 | 0.24 to 0.87 |
| short-lag excess, slow (pairs at lag 0 to 0.3 s over chance, minus 1) | 5.8 to 23.5 | 0.9 to 36.2 |

These describe what a synthetic set has to reproduce. They compare nothing between groups
(ADR-0017): the point is only that a set built around one group's middle sits in a different
place, on different features, from a set built around the other's.

### What goes wrong when a bench covers the middle

Four observations, each already on record:

1. **The middle is not where the recordings are.** A set's two backgrounds bracket the middle half
   of its recordings and nothing else. For MALE combined they are 1.01 and 1.28 per minute while
   the recordings span 0.65 to 1.5; for DI combined they are 0.62 and 5.6, close to the extremes,
   but paired with median coordination, which no DI recording at 5.6 per minute has.
2. **At matched background, the simulations look less coordinated than the recordings.** The MALE
   combined quiet simulation at 1.01 per minute has a short-lag excess of 6.8; the four MALE
   recordings between 0.96 and 1.15 per minute have 10.9 to 17.6. The DI combined busy simulation
   at 5.6 per minute has 0.7; the DI recordings at 5.56 and 6.65 per minute have 1.5 and 1.8. The
   cause is not traced.
3. **Participation is measured two ways and they disagree.** The bench's measurement gives 0.17
   to 0.53 across the six sets; the median of each coordinated event's peak ROI count
   gives 0.26 to 0.67, higher in every set (MALE combined: 0.31 against 0.64). Peak counts favour
   large events, because an event is counted only once it reaches the floor, so neither is
   obviously right. It is the first candidate for point 2.
4. **Where a bench sits changes the setting a search picks.** In the 4x set searches
   ([record](../learned/runs/2026-11-12-set-searches/README.md)), rate+context tuned on all
   recordings scores 0.706 mean F1 (the harmonic mean of precision and recall) on the DI fast set,
   where the DI-tuned setting scores 0.980; the DI-tuned setting scores 0.801 on the MALE fast set.
   At 3x the combined sets disagree as well
   ([record](../learned/runs/2026-11-13-set-searches-3x/README.md)).

Review A did not show this on its own. Its correlogram pools pair counts, so the recordings with
the most pairs dominate each curve: one 73-ROI DI recording supplies 54 % of the real short-lag
pairs in combined DI, and the busy simulations supply 71 % of the simulated ones. The pooled
curves disagreed for that reason more than for any other. A per-recording view was needed to see
where the recordings sit.

### The failure this is meant to prevent

A detector tuned at the middle can fail in a region of the feature space that real recordings
occupy: a high background, a near-silent recording, a large field with weak participation. When
the groups occupy different regions, **that failure lands on one group more than the other**. The
calls then differ between groups for a reason that belongs to the instrument, and any comparison
built on them (fireflies', by default) reads it as biology. Nothing in the route today would
report it: searches and reviews summarize over the middle.

[ADR-0013](0013-the-bench-simulates-treatment-periods.md) already ruled the principle for
treatment recordings: *"A bench recording has a rate level, never a group. This keeps group
structure out of the instrument."* This record applies it to baseline, and adds the half ADR-0013
did not need: covering the range is not enough if the range is summarized away when a setting is
chosen.

## Decision

1. **A bench covers the range its folder's recordings show, on every feature it plants.** For each
   stream and threshold, the span is taken over **all** baseline recordings of the folder, every
   group together. The features are the generator's inputs:
   - ROI count;
   - background, its spread across ROIs (`bg_rate_shape`) and its unevenness over time
     (`bg_burst_shape`);
   - coordinated-event rate and the gaps between events;
   - participation;
   - jitter;
   - event width;
   - close-event separation, already an axis
     ([ADR-0022](0022-close-events-are-a-bench-axis-the-event-definition-stays-at-2-s.md)).

   The short-lag excess is **not** an input. It results from the others, and it is how the realism
   check reads them (decision 6).

2. **Two constructions, and both are built.**
   - **A twin for every recording.** One simulated recording per real baseline recording, built
     from that recording's own measured value of every feature, with several seeds each. A value
     that cannot be measured on one recording (too few coordinated events for a jitter or a gap
     distribution, for instance) takes the folder's pooled value, and the twin's record says which
     ones did. Twins reproduce the spread the data have, including recordings like 20261020_439,
     whose excess is near 0 in every stream; a detector must stay silent there.
   - **A sweep along every feature.** Each feature is set at levels spanning the folder's range,
     with every other feature at the folder's median. Background and participation are also
     crossed on a grid, because that is where the present bench fails: high background with
     median coordination is harder than any real recording, and nothing places it.

     **Open point 1: the extent and spacing.** Proposed: from the minimum to the maximum over the
     recordings, plus one level beyond each end, at 5 levels; on a log scale for a feature that
     spans more than tenfold (background does). A span set by 12 recordings is narrower than a
     span set by 66, and the levels beyond each end are what keep the next folder's extremes
     from being untested.

   Twins test realism and carry the data's joint structure (a recording's background and
   coordination come together). Sweeps test capability, one feature at a time and in the one
   crossing that matters, including combinations no recording happens to have.

3. **One measurement per feature, and it must recover what is planted before it sets anything.**
   The value a twin or a sweep takes for a feature comes from one instrument, the same for every
   recording, stream and threshold. That instrument passes the route's stage 3 check at the values
   it will set (planted against recovered, within 10 % at the median) before a bench is built from
   it. Where two instruments disagree, as the two participation measurements do (Context, point
   3), stage 3 decides between them: the one that recovers a planted participation is used, and
   the other is recorded as not used and why.

4. **Nothing in a bench recording names a group.** A twin carries its recording's identifier,
   for tracing, and its measured values. It does not carry a group, and no generator input or
   search reads one. Groups appear only in the coverage report (decision 5), which describes and
   does not compare (ADR-0017).

   **Open point 2: per-group settings.** Proposed: one setting per detector, stream and threshold,
   tuned over the whole range. A setting tuned on one group's recordings would be group structure
   in the instrument, which ADR-0013 rules out for treatment. The per-group sets of 2026-11-12 stay
   on record as a diagnostic (their cross-scores are Context, point 4) and are not a route to
   adoption.

5. **Coverage is a gate, run at stage 1.** Before a bench is built, every real recording's
   features are placed against the bench's span, per stream and threshold. A recording outside it
   widens the span (decision 2) before any search runs. The report lists every recording, its
   group, and where it sits on each feature. For the revised senktide/TTX export (66 recordings)
   this is the first thing that runs, and it is where the folder shows whether it is "weird"
   (Tony, 2026-11-24: the route is to be settled before it arrives, *"subject to revision if the
   full data set is weird"*).

6. **Review A shows twins beside their own recordings, and per recording.** Each recording is
   drawn with its twin, and the comparison statistics (the short-lag excess, each ROI's onset rate,
   the correlogram) are shown per recording and placed on background, as Figure 1 of the evidence
   folder does. A pooled curve may appear only beside the per-recording view and only with equal
   weight per recording; on its own it compares weightings, not recordings.

7. **Tuning, adoption and Review B read the whole range.**
   - A search scores a setting on the twins and on every sweep level, with each twin weighted
     equally, so that no recording counts more for having more ROIs or more events.
   - What is reported is never one pooled number. Every score is given per twin and per sweep
     level, and Review B's capability map (ADR 2026-11-17-b16b, decision 5) is the sweep scores,
     drawn along each feature.
   - **Open point 3: the adoption rule.** Proposed: a setting is adoptable only if no twin and no
     sweep level inside the observed range falls more than a stated margin below the setting's
     mean, and where one does, the report names the recording or the level and the adoption
     waits on Tony's word. The margin is his.

8. **Negatives and learned models follow the same construction.** Rate-matched negatives
   ([ADR-0019](0019-the-decoys-are-retired-negatives-are-rate-matched.md)) are made from each twin,
   so false calls are reported per twin, at that recording's own background. The learned models
   train on twins and sweeps, with seeds kept disjoint between training and scoring.

9. **Combined twins are built the way the export builds the stream.**
   **Open point 4.** The exported combined stream is exactly the fast onsets plus the slow onsets
   (ADR-0023: bugarach does not combine streams; the export is final), and 8 to 20 % of combined
   onsets have another onset in the same ROI within 0.5 s, one from each stream. Proposed: a
   combined twin is the fast twin plus the slow twin of the same recording, with their coordinated
   events placed together as the recording's are, rather than a stream simulated on its own. The
   pairs move the pooled excess little (4.2 to 3.9 in DI, 12.3 to 12.1 in MALE), so this is for
   fidelity, not to explain decision 2's gap. Whether such a pair is one calcium event or two is
   the producer's statement (route, *Owed* item 9).

10. **The scale of a twin set is the folder's.** **Open point 5.** Twelve recordings give 12
    twins per stream and threshold; 66 give 66. Proposed: twins for every recording, and if a
    search's cost makes that impractical, a subset chosen to cover each feature's range (its
    extremes kept), with every recording still placed by the coverage report.

**What this does not change.** Baseline only, for every coordination property (FOUNDATIONS §9;
ADR-0013 for treatment). The 2 s event definition (ADR-0022). The streams as exported (ADR-0023).
The route's order and its three reviews (ADR 2026-11-17-b16b). Adoption is Tony's.

## Consequences

- **The bench changes form.** A bench set becomes a list of twin specifications plus a sweep
  grid, built from a per-recording record, instead of one set of constants with two backgrounds.
  `tools/measure_bench_sets.py` and `bugarach.bench_sets` change; the stage 1 tools already
  measure per recording and need not.
- **The generator mostly has what it needs.** ROI count, background, its spread across ROIs and
  over time, participation, jitter, event rate and gaps are inputs today. A per-recording fit of
  the background's spread across ROIs may be unstable on a small recording; where it is, the twin
  keeps the pooled shape scaled to its own mean, and says so (decision 2).
- **Searches cost more.** How much is not measured. A 4x set search took 18 to 178 minutes on 11
  workers, and cross-scoring the nine sets 35 minutes at 12 recordings per background; twins with
  several seeds each, plus sweep levels, multiply the recordings scored. The first run measures it, and open point 5 is the
  release valve for 66 recordings.
- **The per-group sets and their searches become a diagnostic** (open point 2). Their records
  stay as they were, as records of their date.
- **Review A is rebuilt** with twins and per-recording statistics (decision 6), and Review B waits
  for the sweeps.
- **Stage 3 gains a question it must answer first**: which participation measurement recovers
  what is planted (decision 3). Until it does, a twin's participation is marked as chosen, not
  measured, on the route's existing rule for stage 3 failures.
- **A systematic failure becomes visible rather than averaged away.** This does not promise that
  one setting works everywhere. It promises that where it does not, the report names the
  recording or the region, before any comparison between groups or treatments is built on the
  calls.
- **The September bench stays stale** ([ADR 2026-11-13-43ba](2026-11-13-43ba-the-september-bench-is-stale-and-is-not-re-measured.md)).
  Nothing here re-measures it.
