# ADR 2026-11-16-e860: Treat1 is APV plus CNQX, treat2 is GZ, and high K is a positive control

## Status

Accepted, 2026-11-16, by Tony: *"hik can be analyzed but this is a positive control that the
slice is alive, not something we plan to measure for comparison or mechanism"*. Answers open point
5 of [ADR-0013](0013-the-bench-simulates-treatment-periods.md) and makes its proposed default
permanent.

## Context

The tracked DI and MALE cohorts were recorded under three periods after baseline: APV with CNQX,
then GZ, then high K⁺ (HIK). The route to calls has steps that read treatment periods: measure a
treatment's properties, run the baseline-tuned detectors through it, review the result, and
revise the synthetic sets if a treatment breaks the detectors
([ADR-0013](0013-the-bench-simulates-treatment-periods.md)). Those steps need to know which periods
are treatments.

ADR-0013 left high K⁺ open (point 5) and proposed "out of scope for now, since it is a positive
control, not a treatment the analysis compares".

## Decision

1. **Treat1 is APV with CNQX; treat2 is GZ.** These are the treatment periods the route measures,
   detects through and builds treatment-shaped synthetic sets from.
2. **High K⁺ is a positive control** that the slice is alive. It may be analysed and shown. It is
   not measured for comparison or for mechanism, and no synthetic set is built from it.

## Consequences

- Detection runs over whole recordings, so detectors make calls in the high K⁺ period. Pages and
  reports label that period as the positive control and leave it out of any comparison between
  periods.
- Showing that a slice responded to high K⁺ is evidence for the reviewer. It never becomes a
  filter: whether an ROI or a recording is alive is decided at export
  ([FOUNDATIONS](../FOUNDATIONS.md), *a zero-event ROI is not a dead ROI*). A recording that looks
  unresponsive is a question to the producer.
- A finding that APV with CNQX or GZ changes coordination is a statement about the preparation,
  which is fireflies' by default
  ([ADR-0017](0017-group-and-treatment-comparisons-default-to-fireflies.md)). Measuring those
  periods so the detectors can be checked against them stays here.
- ADR-0013's open point 1 (is a treatment surge coordination?) still applies to treat1 and treat2.
