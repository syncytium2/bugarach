# ADR 2026-11-17-b16b: The route to calls has three human reviews and a treatment loop that tests before it retunes

## Status

Accepted as amended, 2026-11-17, by Tony: *"we will run 3x and 4x in parallel. the rest is fine"*.
The one amendment is written into decision 3, marked where it falls. Drafted at Tony's request; the
sequence of steps is his, given on 2026-11-16:

> *"characterize the three streams (corellograms, etc). build synthetic data. human review of
> synthetic data and real data side by side. optimize and train select/all detectors on synthetic
> data. human review on synthetic data. detect on real data. assess treat1 (and treat2 if
> available), real data properties. run baseline opt/train detectors on treat1/treat2. human
> review. revise synthetic datasets if necessary to address treatment effects"*

Two rulings from the same afternoon are already recorded:

- treat1 is APV with CNQX, treat2 is GZ, and high K⁺ is a positive control
  ([ADR 2026-11-16-e860](2026-11-16-e860-treat1-is-apv-plus-cnqx-treat2-is-gz-and-high-k-is-a-positiv.md));
- the learned models are off hold, so "train" in step 4 includes them
  ([ADR 2026-11-16-4feb](2026-11-16-4feb-the-learned-models-are-off-hold-on-the-reviewed-tracked-coho.md)).

Five points were the session's, drafted as proposals and accepted with the rest: keeping the
machine check in front of the first review, the rule for step 10, where the loop goes back to and
when it stops, freezing the settings before any comparison, and a closing check after detection.
A sixth, picking one threshold at the first review, was replaced at acceptance (decision 3).

It revises the route of [ADR-0020](0020-one-route-from-a-folder-to-calls-per-stream.md)
(decision 1) and does not supersede it: ADR-0020's other three decisions stand.

## Context

ADR-0020 set one route per stream: characterize the baseline, simulate from it, check that the
measuring tools recover what was planted, tune, evaluate, detect. Its commands are
[`pipelines/stream-readiness.md`](../pipelines/stream-readiness.md). Every gate on that route is a
test or a person's word on adopting a setting. **No gate is a person looking at the data.**

The route also stops at baseline. FOUNDATIONS §9 keeps coordination properties baseline-only, and
ADR-0013 builds treatment-shaped benches from treatment rates, but no step runs the tuned
detectors through a real treatment period and looks at what they do.

Tony's sequence adds both: three reviews by eye, and a second half that takes the baseline-tuned
detectors into treat1 and treat2 and revises the synthetic sets if a treatment breaks them.

The first walk of that sequence is the tracked DI and MALE cohorts, at two thresholds (4× and 3×
sigma_est). On them steps 1 and 2 are done at both thresholds (2026-11-12 and 2026-11-13), the
coded detectors are searched at both, and nothing is adopted.

## Decision

The route, per stream (fast, slow, combined):

1. **Characterize the baseline**: correlograms, event rates, participation, jitter, intervals.
2. **Build synthetic sets** from what step 1 measured.
   - **The machine check stays between 2 and 3**: the measuring tools are run blind
     on the synthetic sets and must recover what was planted (route stage 3). A review by eye
     tests whether the sets look like the data; this tests whether the numbers they were built
     from can be trusted, which the eye cannot.
3. **Human review: synthetic beside real.** One page per stream draws simulated recordings and
   real ones the same way, with the same correlograms.
   - **Both thresholds run in parallel (amended at acceptance).** Where a folder exists at two
     thresholds (the tracked cohorts at 4× and 3× sigma_est), each is carried through the whole
     route as its own walk, and the review shows both on the same real recordings. Proposed was
     to pick one here; Tony chose to run both.
4. **Optimize and train detectors on synthetic data**: coded detectors searched, learned models
   trained (ADR 2026-11-16-4feb), on the selected detectors or all of them.
5. **Human review on synthetic data.** What is reviewed is a capability map per detector: what
   it finds and what it misses across separation, participation and background, with false calls
   on rate-matched negatives (ADR-0019). Until those negatives exist, the map shows false calls
   against background only, and says so. Adopting a setting stays Tony's word.
6. **Detect on real data**, whole recordings, with the adopted settings.
   - **A closing check follows**: the step 1 quantities are re-measured from the
     calls on real baseline and compared with step 1 (Aim 3 of
     [`goals/synthetic-validation.md`](../goals/synthetic-validation.md)). If they disagree, the
     loop has not closed, whatever the reviews said.
7. **Assess treat1 and treat2**: their event rates, rate courses and the properties the
   detectors depend on, measured so the detectors can be checked against them. High K⁺ is not
   measured (ADR 2026-11-16-e860).
8. **Run the baseline-tuned detectors through treat1 and treat2**, unchanged.
9. **Human review** of those calls. The high K⁺ period is shown, labelled as the positive control,
   and left out of every comparison.
10. **Revise the synthetic sets if a treatment breaks the detectors.**
    - **Treatment-shaped sets test before they tune.** The sets are rebuilt with
      treatment backgrounds (ADR-0013: treatment rates as background, baseline's coordination
      planted through them, swept). The baseline-tuned settings are scored on them first. Only
      settings that fail there are retuned, and the retune is scored on baseline sets as well.
      Tuning on sets shaped by a treatment's effect, and then measuring that effect with the
      tuned detectors, would make the measurement depend on what it measures.
    - **The loop goes back to step 2**, then 3, 4, 5, with step 1's baseline record
      held fixed. It stops when the settings pass on the treatment-shaped sets and on baseline.
    - **The settings are frozen before anything compares treatment with
      baseline**, and that comparison is fireflies' by default
      ([ADR-0017](0017-group-and-treatment-comparisons-default-to-fireflies.md)).

## Consequences

- **The route page gains three review gates and a second half.**
  [`pipelines/stream-readiness.md`](../pipelines/stream-readiness.md) carries them, with what
  exists for each and what is owed.
- **Two review pages are owed before steps 3 and 5 can run.** Step 3 needs a page that draws a
  simulated recording and a real one the same way; for the tracked cohorts it also draws each real
  recording at 4× and 3×. Step 5 needs the capability map, which is ADR-0020's owed evaluation
  stage.
- **Steps 7 to 9 are bugarach's only as instrument checks.** Their outputs say whether the
  detectors cope with a treatment period, not what the treatment does. A finding about the drug
  is a statement about the preparation and waits for Tony's yes (ADR-0017).
- **FOUNDATIONS §9 is unchanged.** Step 7 measures backgrounds and rate courses, which ADR-0013
  allows; coordination properties still come from baseline only.
- **Nothing is adopted by this record.** Every setting still goes in on Tony's word.
