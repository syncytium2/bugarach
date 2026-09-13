---
status: open
filed: 2026-09-12
---

# Evidence before more effort on the ROI swap

Tony, 2026-09-12: *"we need some evidence in our system that this is a valuable approach … a plan to
justify further effort in this direction."*

**The idea.** Build a null by replacing ROIs in a recording with real trains from other recordings.
Coordination is destroyed, and every train stays exactly real, so the null cannot manufacture an
interval real data never produces — the failure that killed the dither family.

**Where it stands.** The detector-training design built on it was reviewed three times and marked
**not recommended as designed** ([proposal](../proposals/2026-09-12-the-roi-swap-null.md),
[record](../reviews/2026-09-12-the-roi-swap-null_2026-09-12.md)). The idea itself was not refuted.
Three things were:
- the grid of chimeras that design needed cannot be built on this cohort;
- its two cheap gates could not fail;
- it never compared the swap against the within-recording nulls, which keep slice identity.

This plan produces evidence on the idea's value **before** anyone redesigns the detector.

> **Status: working material, not murderboarded.** It is a todo, like the eight from #540. Run
> `/murderboard` on it before the simulated-ground-truth stage, which is the first to need new code
> and compute. The proposal it follows failed review partly because its gates could not fail, so
> **every gate below names how it can fail and the control that proves it can.**

---

## The reorientation this plan rests on

**Use the swap first as a significance null, not as training negatives.** The round-3 reviewer found
the chimera grid unbuildable mainly because donors had to stay inside the target's **training fold**:
their simulation left 3.7 of 84 targets buildable at a full chimera with fold confinement, and none
for the within-group arm. A significance test has no training folds, so that constraint does not
apply. It is also where the literature precedent is strongest: recombining units never recorded
together is the shift predictor, a significance tool.

So the value claim this plan tests is:

> **Among nulls that destroy cross-ROI coordination, the ROI swap is the only one whose per-ROI trains
> are exactly real. That is worth its cost — slice identity — if, on this data, it gives better
> significance calls than the circular shift the coactivity assessor already uses.**

If that fails, the swap adds nothing the project does not already have, and the direction stops here
with a negative result worth recording. If it holds, the swap has proven value for **significance
testing** whether or not it ever becomes training negatives, and the detector question can be
reopened on evidence.

---

## What exists, what must be built

| need | exists? | where |
|---|---|---|
| Synthetic recordings with planted coordination, participation levels and jitter | yes | `simulate.simulate_coordination` on main |
| A population-wide rate increase with no coordination | yes | its `hot_window` / `hot_rate_hz` / `ramp_sec` |
| Correlated bursts that are not coordinated events | yes | its `n_distractors` |
| Across-ROI rate heterogeneity; within-ROI burstiness over time | yes | `bg_rate_shape`; `bg_burst_shape` (drawn **per ROI**, not shared) |
| Slow drift shared by every ROI across a whole recording; bleaching; field steps | **no** | new simulator code if wanted |
| A coactivity significance test | yes | `assess.assess_coactivity` on main |
| That test with a swap null | **no** | its null is hard-coded to circular shift; needs a donor-pool option |
| Pooled per-window features and a mouse-grouped paired classifier | yes, **unmerged** | `surrogate_discriminator.py` on `origin/surrogate-screen-overnight` (draft PR #530): `window_features`, `pool_symmetric`, `forced_choice`, `mouse_folds` |
| A same-recording-versus-different-recording classifier | **no** | a small adaptation of `forced_choice` |
| Cohort metadata: group, mouse, date, frame interval | yes | the approved export's `slices.csv` |

Using the screen branch's code **read-only** does not reopen the screen. Tony stopped that thread on
2026-09-12, and nothing here touches its family-size decision or its verdict rule.

---

## The literature deep dive — runs alongside everything

[Its own todo](2026-09-12-literature-deep-dive-on-recombination-nulls.md). Two outcomes would change
this plan before any code is written:

- **A documented false-positive mode for recombination nulls under preparation-level covariation.**
  Brody 1999, *"Correlations without synchrony"*, is the leading candidate and is unread. If it holds,
  the simulated stage must add a slice-level covariation arm strong enough to reproduce it.
- **Session identity reported as highly decodable in multi-session population models.** That moves the
  slice-identity stage's expectation toward STOP.

> **Both outcomes came in, 2026-09-12** — [reading log](../learned/recombination_nulls_reading_log.md),
> section *What this changes in the plan*. The stages below are **not yet edited** to match. Whoever next
> declares a stage's margins reads that section first. It proposes:
> - **Slice identity:** expect STOP at the global level; add a single-train lineup test of native versus
>   donor ROIs.
> - **Simulated ground truth:** split the slice-level covariation arm into three — shared gain within a
>   recording, donor mismatch with unshared gains, and protocol-locked structure. Declare the hot window's
>   timing random per recording, or its positive control cannot bite for the swap. Add a shared-drift arm
>   before simulation can license real data.
> - **The decision:** the condition for reopening training negatives is **not met**. Cross-recording
>   negatives taught recording identity in every study that measured it.

---

## Buildability for a significance test — arithmetic, hours

**Question.** Can a chimera be built for most recordings, with each swapped ROI taken from a different
donor recording, when donors need not respect training folds?

**Compute**, from `slices.csv` and the baseline windows of the approved export: for every target
recording, every matching level (another recording from the same mouse, the same group, global) and
every swap rule, the largest buildable swap fraction `k/N`. The swap rules are one ROI per donor
recording, or up to *m* ROIs per donor recording. Donors must have a baseline window at least as long as
the target's, and the same frame interval.

**Check the counter first:** re-impose fold confinement and reproduce the round-3 reviewer's 3.7 of 84.
If it does not reproduce, fix the counter before reading anything else. That simulation has never been
reproduced by this project.

**Gate.**
- **GO** if, at `k/N = 1` with one ROI per donor recording, at least **80% of the 84 targets** are
  buildable at the global level. Record, for the tighter levels, the largest `k/N` buildable for 80% of
  targets.
- **STOP** if the global level fails that bar. Then the swap cannot be built even without folds, on this
  cohort, under the rule that keeps donor ROIs mutually non-simultaneous.
- **The gate can fire, and we already know one arm will:** in the approved export, **68 of 84
  recordings have more ROIs than their group has other recordings** — ROIs per recording run 9 to 61
  (median 31.5), and groups hold 17 to 25 recordings (checked against `slices.csv` on 2026-09-12). So
  the within-group level **must** fail the full-chimera bar under one ROI per donor recording. If the
  counter says otherwise, the counter is wrong.
- Allowing *m* ROIs per donor recording makes more chimeras buildable, but those ROIs were recorded
  together. **Record that as a cost, not a fix.**

---

## Is slice identity detectable at all — real data, no chimera builder

**Question.** The swap's largest objection is that a model can tell ROIs from one slice apart from ROIs
pooled from several. **Measure that directly on real recordings, before building anything.**

**Compute.** For pairs of real baseline windows, classify *same recording* against *different
recording*, using the pooled per-window features the surrogate discriminator already computes:
- **same recording:** windows at least 5 minutes apart, so adjacency and short-range drift cannot decide
  it;
- **different recording:** at each matching level — same mouse, same group but a different mouse, and
  global.

Mouse-grouped folds and a permutation null throughout, adapted from `forced_choice`. Report accuracy per
matching level with a confidence interval **over mice**. Zero-event ROIs stay in (FOUNDATIONS §9):
empty-baseline composition is exactly the kind of slice signature this measures.

**Gate** — margin proposed here, to be declared before running:
- **GO** if at least one matching level that passed buildability has accuracy whose upper 95% bound
  over mice is below **0.60**.
- **STOP** if every buildable level is above that. On pooled features, slice identity is then visible
  at every matching the cohort allows, and the swap cannot be a coordination-only null.
- **The gate can fire, and its instrument is checked, in both directions.** The global level is
  expected to be clearly detectable: a reviewer reported silent-ROI shares varying severalfold between
  groups, which is unverified here and must be recomputed. **If even the global level reads chance,
  treat it as instrument failure** — the features or the classifier cannot see anything — not as GO.
- ⚠ **Necessary, not sufficient.** `tube` or any learned model may see more than pooled features. A GO
  here licenses the significance-test use; it does not clear training negatives.

---

## Simulated ground truth — does the swap null make better calls than circular shift?

**The central value test**, and the first stage that needs new code: a donor-pool null option for the
coactivity assessor, plus a loop that builds a synthetic cohort. **Murderboard this todo before starting
it.**

**Build a synthetic cohort** of recordings with `simulate_coordination`. Draw each recording's
slice-level parameters from **baseline** statistics of the approved export (FOUNDATIONS §9: calibrate
from baseline only). Take the per-ROI rate distribution with zero-event ROIs included; it is
zero-inflated, and [the FOUNDATIONS rate range does not reproduce](2026-09-10-the-foundations-rate-range-does-not-reproduce.md),
so do not use the published interquartile range. Then run five arms:

| arm | what is planted | correct call |
|---|---|---|
| **null** | heterogeneous, bursty backgrounds; no coordination | not significant |
| **shared rate increase** | a `hot_window` ramped in; no coordination | not significant — *the confound Amarasingham et al. 2012 show shuffle-type nulls flag* |
| **correlated bursts** | `n_distractors`; no coordinated events | not significant |
| **slice-level covariation** | recordings differing in rate scale and burstiness, so pooled donors are mismatched | not significant — *the swap-specific risk* |
| **planted coordination** | events at participation 1.0, 0.75 and 0.5 | significant |

**Run each recording through the assessor under three nulls:** circular shift (today's), the ROI swap
drawing donors from other synthetic recordings in the same arm, and a within-recording null
(`rigid_shift`) as a reference.

**Size it before running.** At a false-positive rate of 0.05, a 95% interval half-width of about 0.03
needs about **200 recordings per arm**, from 1.96 x sqrt(0.05 x 0.95 / 200) = 0.030. Declare the number of
recordings per arm, the number of surrogates, and **each arm's confound strength** before the first run.
Strength is the knob most easily tuned after the fact.

**Gate** — margins proposed here, to be declared before running:
- **GO** only if **all** of these hold:
  - the swap null's false-positive rate on the null arm is at most 0.05 + 0.03;
  - its false-positive rate on each confound arm is no worse than circular shift's by more than 0.03;
  - its power on planted coordination is no worse than circular shift's by more than 0.05;
  - **and it beats circular shift by more than the margin on at least one arm.**
- **STOP — "not better than what we have"** if it beats circular shift nowhere. That is a clean negative
  result, and **the most likely way this direction ends**. Write it up.
- **STOP — "worse"** if it loses on any arm by more than the margin.
- **The gate can fire:** the shared-rate-increase arm is a *known* failure for shuffle-type nulls. **If
  neither null flags it, the confound was planted too weakly to test anything** — re-declare its strength
  and re-run before reading any other arm. Do not read results from an arm whose positive control did not
  bite.

⚠ **What the simulation cannot test:** slow drift shared by every ROI over a whole recording,
photobleaching, whole-field steps and motion pinning. The simulator has none of them. The slice-identity
stage above is the real-data complement; a field-step arm would need new simulator code.

---

## Real-data concordance — where do the two nulls disagree, and why?

**Question.** On the approved baseline recordings, does the swap null change any significance call, and
do its disagreements look like the arm where simulation showed it better — or like slice identity?

**Compute.** Assess every approved baseline recording under circular shift and under the swap at the
matching level that passed. Report per stream and **per group, never pooled across groups** (FOUNDATIONS
§9).

**Gate:**
- **STOP — "no practical difference"** if the two nulls agree on at least 95% of recordings in both
  streams. The swap is then sound but changes nothing in practice.
- **GO** if disagreements are substantial **and** track the property simulation identified — for
  example, recordings with strong within-recording nonstationarity, where circular shift's wrap splices
  unlike segments together.
- **Flag, and treat as evidence against,** if disagreements track **group, silent-ROI share or imaging
  date**. That is the identity confound showing up in real calls. Group is nested in imaging date on this
  cohort — 42 dates, none with more than one group, checked against `slices.csv` on 2026-09-12 — so a
  group-tracking disagreement cannot be told apart from a day effect.
- **The gate can fire in both directions**, and there is no ground truth here, so a GO means "worth
  investigating", not "correct".

---

## The decision this plan earns

**Further effort on the swap as training negatives** — reopening the detector — **is justified only if**
buildability, slice identity, simulated ground truth and real-data concordance all return GO, **and** the
literature deep dive has not surfaced a documented failure that applies. Even then, the next artifact is
not a detector. It is the comparison the review asked for: the swap against the within-recording nulls
(`rigid_shift`, `circular_shift`, `trial_shift`) on leak and destruction, on one cohort, with paired
gates. `rigid_shift` already reads 0.495–0.524 per-ROI on fast, checked against the run files on
2026-09-12, and any case for the swap has to beat that.

**A partial result is still value, and is named in advance.** If simulation shows the swap null makes
better significance calls but slice identity is visible on pooled features, the swap is **worth adopting
for coactivity significance testing** and **not** worth pursuing as training negatives. The outcome is
worth stating before anyone hopes for the other one.

**A STOP at any stage is a result.** Record it in this todo, update the ROI-swap row in `docs/INDEX.md`,
and close the direction with the reason. The label-free detector thread still has no exit criterion
([todo](2026-09-12-the-label-free-detector-thread-has-no-exit-criterion.md)); a clean negative here is
part of one.

## Cost

Buildability and the literature need no compute. Slice identity is a classifier over existing pooled
features: CPU, minutes to an hour. Simulated ground truth is the only real cost — five arms of about 200
recordings, times three nulls, times the surrogate count — CPU-bound and suitable for the Windows
workstation session Tony named on 2026-09-12. Concordance is 84 recordings times two nulls. **No GPU
anywhere in this plan.** A run that writes to the darkroom claims its own folder on `docs/SESSIONS.md`
first.

## Related

- [Empty baselines are a group feature](2026-09-12-an-empty-baseline-is-a-group-feature-and-39-percent-of-every-surrogate-is-the-data.md)
  — silent-ROI composition is both a slice signature and something a swap changes.
- [126 fast candidates voided on one seed](2026-09-12-126-fast-candidates-were-voided-on-one-seed-of-twenty.md)
  — `rigid_shift`'s fast rows are among them.
- [Which surrogates enter the screen](2026-09-10-which-surrogates-enter-the-screen.md) — the no-pruning
  ruling. This plan prunes nothing from the screen.

**Not in scope:** the group-identity side quest, parked because group is nested in imaging date; the
stopped screen's family-size decision; PR #531.
