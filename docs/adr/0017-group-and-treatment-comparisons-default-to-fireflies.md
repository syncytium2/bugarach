# ADR-0017: Group and treatment comparisons default to fireflies; an exception is flagged and confirmed

## Status

Accepted, 2026-10-14, by Tony. Drafted at his request: *"the default is fireflies for group
comparison, flag requests that differ"*, with the first exception named in the same message:
*"in this case it is silly for fireflies to handle this extremely specialized analysis"*. He asked
to confirm the division of labour before it was accepted, read the four points below, including
the instrument carve-out in point 2, and answered *"yes."*

## Context

**FOUNDATIONS §9 said it in one clause, and the clause was absolute.** *"Treatment effects
themselves are `fireflies`' and must not be re-derived here."* The working version of it was
settled on 2026-08-30, when the senktide and TTX recordings went to fireflies for before/after
plots: bugarach exports the calls with each recording's periods carried per call, and fireflies
plots. That split is right for most work. Fireflies is where group and treatment statistics are
done for the lab, and a second implementation here would be a second answer to the same
question.

**On 2026-10-14 the clause met a request it does not fit.** Coordinated events persist under TTX
and under APV+CNQX(+GZ), and Tony asked for a measure of how much of the activity is
coordinated: the fraction of calcium events that are coordinated, against the overall event
rate. The measure already exists here as `coordinated_share_of_rate` in
`tools/measure_coordination_rates.py`. It counts onsets across the population in a sliding
window, subtracts the same counts from a surrogate in which each cell's train is shifted
rigidly, and solves for how often shared moments happen (λ) and what share of the field joins
one (*k*/*N*). It has so far been run on baseline windows only. Whether its numbers can be
trusted depends on things that live only in this repository: the surrogate, the check on
whether a recording is usable, the choice between the fixed and binomial models, and
calibration against simulated recordings where the answer is planted. Fireflies receives calls,
not population counts with surrogates. Sending it this analysis would mean either duplicating
the method there or handing over numbers without the checks that make them valid.

**The clause was also already read narrowly.** §9 itself separates single-cell event frequency,
amplitude and width (global FOUNDATIONS §15.1) from cross-ROI coordination under treatment
(§15.1b), and reports the second as measured with this repository's detectors on paired
baseline/treatment windows. And bugarach already compares groups when the comparison is about
the instrument: the bench's constants are measured by group (`--by-group`, with leave-one-out,
in the 2026-09-22 and 2026-09-23 run records) because §9 makes a pooled constant inadmissible.

## Decision

1. **The default: a comparison across groups, or between baseline and a treatment, whose result
   is a claim about the preparation is fireflies' work.** bugarach supplies the per-recording,
   per-window measures and exports them. This is the 2026-08-30 split, kept as the rule.
2. **A comparison that sets or checks the instrument stays here.** That covers bench constants
   by group, which recording carries a group's number, and how detectors behave by group or
   under a treatment. Its result goes into the instrument and is not reported as a finding
   about the groups.
3. **When a request would have bugarach make a finding about the preparation itself, the
   session flags it before starting.** The flag names the default (fireflies), says why this
   request differs from it, and the work waits for Tony's yes in words. A confirmed exception
   is listed under FOUNDATIONS §9, with its date and scope, so the next session reads it there
   rather than re-asking.
4. **First exception, confirmed by Tony on 2026-10-14: the coordinated fraction under
   treatment.** bugarach measures, for each treatment window paired with its own baseline:
   - the share of events that are coordinated;
   - its two parts, the rate of shared moments and the share of the field per moment;
   - the per-cell event rate beside them.

   Each is reported per stream and per group, ordered as `bugarach.groups` orders them. This
   covers TTX, senktide and APV+CNQX(+GZ). The per-cell rate is shown because it is the
   fraction's denominator, and it is not reported as a finding about what a treatment does to
   event rate: that stays fireflies' (§15.1). If it disagrees with fireflies' rates, that is a
   conversation with them, not a correction made here.
5. **Unchanged:** coordination properties are calibrated from baseline only (§9); measuring a
   treatment window is pointing the instrument at it, not tuning it there. A pooled number
   across groups is still not admissible on its own, and every claim still names its stream.

## Consequences

- FOUNDATIONS §9's opening sentence points here and lists the confirmed exceptions, so the
  clause no longer reads as forbidding work Tony has approved.
- **Point 3 is not mechanized.** A request arrives in conversation, not as a line in the tree,
  so there is nothing for sapper to match. It rests on the CLAUDE.md line that points here and
  on the exception list in §9.
- The first run under point 4 is TTX against its own baseline, on the default dataset once
  Tony has confirmed it for the session. APV+CNQX(+GZ) is read from the two eval folders
  exported on 2026-10-12, by name. Both are separate PRs.
- Fireflies' export from bugarach is unchanged. Nothing here stops the coordinated fraction
  being exported to fireflies later if Tony wants it plotted with their figures.
