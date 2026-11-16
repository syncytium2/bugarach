# ADR 2026-11-16-4feb: The learned models are off hold, on the reviewed tracked cohorts

## Status

Accepted, 2026-11-16, by Tony: *"RELEASE THE HOLD"*. Amends decision 5 of
[ADR-0021](0021-the-toolset-is-validated-on-synthetic-data-first-with-coded-detectors.md), which
said a release would come as a new record. Its other decisions stand.

## Context

The learned models were put on hold on 2026-10-22 ([ADR-0021](0021-the-toolset-is-validated-on-synthetic-data-first-with-coded-detectors.md),
decision 5). Tony gave the reasons on 2026-11-16, in order:

- **Artifacts in the recordings**, the field-step problems first among them. A model learns from
  whatever the recordings hold, so a step in the field becomes something it learns to call.
- **Then the retracking.** Every ROI in the senktide and TTX recordings is being tracked again,
  and the data they replace are never read again
  ([ADR 2026-11-13-43ba](2026-11-13-43ba-the-september-bench-is-stale-and-is-not-re-measured.md)).
  Training on those data would be training on data already condemned.

Neither reason applies to the tracked DI and MALE cohorts treated with APV and CNQX, then GZ: Tony
states they **have been reviewed for all of these artifacts**. They are the two `tracked_cohorts`
folders of 2026-11-12, at 4x and 3x sigma_est, and the default folder is the 4x one.

## Decision

1. **The learned models are off hold.** Training, bake-offs and write-ups on the
   [learned-model goal](../goals/learned-model-family.md) may resume.
2. **The real recordings they read are the reviewed tracked cohorts** (DI and MALE, APV and CNQX
   then GZ, at either threshold). Synthetic sets built from those cohorts' measurements are
   included, as they are for the coded detectors.
3. **The senktide and TTX recordings stay out until their retracked export arrives** and has
   had the same review. That is a statement about those data, not a hold on the models.
4. **The route is the coded detectors' route.** A learned model is tuned and trained on the
   synthetic sets and goes through the same reviews; the general toolset, the synthetic-first
   order and the no-decoys ruling still bind
   ([ADR-0021](0021-the-toolset-is-validated-on-synthetic-data-first-with-coded-detectors.md)
   decisions 1 to 4, [ADR-0019](0019-the-decoys-are-retired-negatives-are-rate-matched.md)).

## Consequences

- The goal pages that say "on hold" are updated in the same change:
  [`goals/learned-model-family.md`](../goals/learned-model-family.md),
  [`goals/README.md`](../goals/README.md),
  [`goals/synthetic-validation.md`](../goals/synthetic-validation.md) and
  [`goals/detector-review-document.md`](../goals/detector-review-document.md).
- Chorus may return to the detector document's main text; whether it does is that document's
  decision, not this record's.
- The learned models' labels were built with a decoy case that
  [ADR-0019](0019-the-decoys-are-retired-negatives-are-rate-matched.md) retired. Training resumes
  on labels without decoys; the old labels are not reused as they are.
- Learned results from before 2026-10-22 were trained and scored on the September benches, which
  are stale. They are history, not a starting score to compare against.
- Nothing is adopted by this record. Which model or setting goes forward is still Tony's.
