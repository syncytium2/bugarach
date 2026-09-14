# Pre-registration — is rigid shift a usable surrogate on these data?

> **SIGNED by Tony, 2026-09-14 — every value accepted as proposed.** Everything above the sign-off
> line is frozen: only typos change, and the run reads its result against this page as written.
> A change found necessary before any result exists goes in as a **dated amendment** below the
> sign-off, never as an edit above it.
>
> **Goal:** [`goals/unsupervised-learning.md`](../goals/unsupervised-learning.md).
> **Why this page exists.** Tony stopped the surrogate screen on 2026-09-12 because it felt like
> going in circles. The cause was structural: the screen was designed to measure everything and
> design its verdict rule *afterwards*, so every rule anyone wrote was post-hoc, and every review
> correctly said so. This page does it the other way round: rule first, then one small run, then
> read the result once.

## The question

**Does rigid shift — each ROI's whole train moved by one random offset in ±*J*, nothing wrapped
— give a surrogate that a coordination-blind classifier cannot tell from the real recording,
while it removes planted coordination at the timescale this project calls coordinated?**

If yes, a self-supervised objective has a usable negative class, and the goal moves to the model.
If no, the goal stops with a written result: the leading within-recording surrogate either leaks
or leaves coordination in place on these data.

## Why rigid shift, and why only rigid shift

**Chosen from the 2026-09-11 overnight run, which is exploratory and is labelled so here.** It is
the only candidate the per-ROI leak test could not detect at a displacement comparable to real
event structure: to 1.6 s fast, 1.4 s slow, four frames on Cossart
([the join](../todo/2026-09-12-join-the-leak-results-to-the-destruction-results.md)). Its fast
accuracies there were 0.495–0.524, though every fast row was voided by the seed-0 defect
([todo](../todo/2026-09-12-126-fast-candidates-were-voided-on-one-seed-of-twenty.md)). The other
survivors moved onsets by one frame, which cannot destroy seconds-scale coordination. Uniform
dither is known to leak. Joint-ISI was never measured.

**So a STOP on rigid shift stops the goal**, not just this candidate: nothing else reached this
stage in the exploratory run. Reopening would need a new candidate with its own exploratory
evidence.

## What this run cannot claim

⚠ **The data are the same data.** Both folders were used in the exploratory run, and there are no
unused baseline recordings. What protects this run is a **fixed rule and fresh randomness** —
new surrogate seeds, new mouse folds — not new recordings. A VIABLE result is therefore "held up
under a rule declared in advance", not "replicated on independent data". It must be reported
that way.

---

## Data

- **Lab folder:** `dataset.current("steps_excluded")` — 84 recordings, 44 mice, four groups,
  frame interval 0.1 s. **Baseline windows only** (FOUNDATIONS §9). Fast and slow are analysed
  **separately** and get separate verdicts.
- **Cossart folder:** `dataset.current("cossart")` — **leak test only** (see *Destruction*).
- **Zero-event ROIs stay in** (FOUNDATIONS §9). The share of ROIs that rigid shift cannot change
  is **reported per group**, not removed
  ([why](../todo/2026-09-12-an-empty-baseline-is-a-group-feature-and-39-percent-of-every-surrogate-is-the-data.md)).
- **The four motion-pinned recordings stay in.** Which recordings are analysable is the
  producer's call ([todo](../todo/2026-09-10-four-recordings-carry-an-unflagged-contaminant.md));
  the report names them.

## The displacements — accepted

Three per stream, declared now; no other *J* may be credited.

| stream | *J* | why |
|---|---|---|
| fast | 1.6 s, 2.5 s, 5.0 s | the largest leak-free value in the exploratory run, the next step on its grid, and double that |
| slow | 1.4 s, 2.8 s, 5.6 s | the same logic on the slow grid |
| Cossart | 4, 8, 16 frames | the same logic in frames |

Three displacements are a family of three: every bound below is Bonferroni-widened to a
**98.3 %** interval.

---

## The gates

Each gate states how it can fail, and each has a control that shows it can.

### Leak — a coordination-blind classifier must not tell real from surrogate

**Instrument:** `surrogate_discriminator.forced_choice`, unchanged. Each ROI is reduced alone to
count, interval quantiles, shortest interval and edge-band counts; ROIs are pooled only by
symmetric statistics, so the classifier cannot see coordination. 60 s windows, mouse-grouped
folds, 199 within-pair permutations. Intervals: bootstrap over **mice**, 2,000 resamples (the
recording-identity run's `mouse_bootstrap`).

- **Pass at a *J*:** the upper 98.3 % bound on accuracy is **below 0.55** (accepted) — the screen's
  own smallest effect worth detecting. Not detecting a leak is not enough; the bound has to
  exclude one.
- **Positive control, uniform dither at the same *J*:** lower bound **above 0.55**. If it fails,
  that *J* is **void** for that stream: the test could not have seen a leak.
- **Negative control, real against real, 20 seeds:** void the stream if **4 or more of 20** seeds
  flag at α = 0.05 (accepted). Three or more happens 7.5 % of the time by chance, four or more 1.6 %.
  **No single seed can void anything** — that was the defect.

### Count preservation — the surrogate must not change how many onsets there are

Rigid shift drops onsets pushed past the generation window's edge, and any model that averages
over ROIs sees a count change as a free win
([tube foot gun](../todo/2026-09-12-tube-cannot-tell-a-count-leak-from-coordination.md)).

- **Statistic:** per ROI and per analysis window, surrogate onset count minus real, paired,
  averaged within mouse.
- **Pass:** the 98.3 % interval over mice lies inside **±2 % of the mean real count** (accepted).
- **Control:** the screen's `edge_thinning` control, which deletes onsets near the window edges,
  must *fail* this gate. If it passes, the statistic is too coarse to read and the gate is void.

### Destruction — the surrogate must remove planted coordination

**Instrument:** `surrogate_stats.destruction`, unchanged except the bin. Synthetic twins with the
stream's own per-ROI counts and floor, with and without planted events, each pushed through rigid
shift with the same key and scored by the assessor's selection-corrected coactivity excess.
**Retained** = excess the planted twin keeps after the surrogate, as a share of what it had
before. Participation 0.2 and 0.5, the assessor's K scan.

- **The timescale of "coordinated" — accepted: 1.0 s.** The screen scored destruction in a ±2-frame
  (0.5 s) bin. The assessor that proposes events uses **1.0 s**. A shift can clear a 0.5 s bin and
  still leave 1 s coincidences in place. **Scored at 1.0 s**, the assessor's own
  definition, and report 0.5 s beside it.
- **Pass at a *J*:** retained share **at most 0.25** (accepted), at every K where the planted
  events are visible before the surrogate, at both participation levels.
- **Controls:** do-nothing must retain **at least 0.9** (the measure sees coordination that
  survives); homogeneous resample must retain **at most 0.1** (it sees removal). **Not circular
  shift** — it is the assessor's own null, so it reads zero whether or not the measure works.
- **Saturation:** at each *J*, report the expected number of co-active ROIs still inside the bin.
  A *J* where it exceeds the top of the K scan cannot show removal and is **void**, not failed.
- **Cossart is not scored for destruction.** At 566 median ROIs the measure registered no removal
  at any setting in the exploratory run, so a pass or fail there would mean nothing.

---

## The outcome, per stream and overall

**Per stream:** **PASS** if at least one declared *J* passes leak, count and destruction with
every control valid. **VOID** if the controls fail at every *J*: the instrument is broken, which
is fixed and rerun rather than read. **FAIL** otherwise.

| fast | slow | Cossart leak at the passing *J* | outcome |
|---|---|---|---|
| PASS | PASS | passes | **VIABLE** — the goal moves to the model tier |
| PASS | PASS | fails | **NARROWED** — every claim names the lab folder |
| PASS on one stream, FAIL on the other | | | **NARROWED** — every claim names the stream |
| FAIL | FAIL | — | **STOPPED** — written up as a result about the data |

**What each outcome commits to next.**
- **VIABLE / NARROWED:** the model must keep the ROI axis before its first pooling, or normalise
  the count across ROIs away, because `tube` in its current form cannot tell a count leak from
  coordination. The quiet → busy transfer penalty is stated beside any treated-window number.
- **STOPPED:** the fallbacks are the simulator-trained models, with their measured transfer
  penalty, and the six hand-written detectors. The write-up says which gate failed, at which *J*,
  on which stream.

## Not in this run

- **The band statistics and their family size.** This run replaces that route to a verdict; the
  overnight run stays on file as exploratory.
- **Other candidates, the ROI swap and MAHICE** — none gates this question.
- **Any model training.**

## What has to be built, and its cost

- **A runner, `tools/confirm_rigid_shift.py`**, calling the three instruments above with fresh
  seeds. The discriminator has no command-line entry point today.
- **The bin as a parameter of `destruction`**, defaulting to today's value so the overnight
  numbers still reproduce.
- **The seed-distribution voiding rule** and **the count-preservation statistic**, each with a
  test that fails if the rule is reverted.
- **Cost:** rigid shift is one of the cheapest generators. Two streams × three *J*, plus Cossart
  leak and the controls, is expected to take hours on the Mac. A `--limit` smoke run prices it
  before the real run starts, and the run claims its darkroom folder first.

## Review, once

`/murderboard` runs on **this page** before signing, and on the **result** only if it goes to an
outside reader. Plans in between are working material.

---

## Sign-off

| | |
|---|---|
| Accepted as written, or amended as noted | **Accepted as written.** Asked to set or accept each proposed value — the 1.0 s timescale, the displacements, the 0.55 leak margin, 25 % retained, ±2 % counts, 4 of 20 seeds — and to name any that was wrong, Tony answered *"agreed. signed"* |
| Signed | Tony |
| Date | 2026-09-14 |

*Nothing above this line changes after signing, except typos.*

## Amendments

⚠ **The page asked for its murderboard before signing; it was signed first.** The review runs
once, now, before any code is built or any data are read. A blocking finding is brought to Tony
and, if he accepts it, recorded here with its date. Nothing above the line is edited.

**2026-09-14 — the review ran; eleven amendments are proposed and none is adopted yet.** All 11
roles found that the rule as signed cannot be read if it runs: three controls cannot fail, the
outcome table has no VOID or UNDECIDED rows, the 98.3 % bound is undefined, and "fresh
randomness" is not delivered by the instruments as they stand. No amendment changes a signed
threshold. ⚠ One reviewer quoted exploratory outcomes at declared displacements, so anything
adopted from here is post-exposure and says so. **Do not run until Tony has ruled on each.**
[Run record](../reviews/2026-09-14-preregistration-is-rigid-shift-usable_2026-09-14.md).

---

### Adopted amendments — 2026-09-14

**Adopted by Tony, all eleven.** He was shown the eleven, each described as leaving every signed
threshold unchanged, with the recommendation to accept all of them and then run one blind review
pass before building, and answered *"agreed"*. **Where an amendment and the text above disagree,
the amendment wins.** ⚠ **These were written after one reviewer quoted exploratory outcomes at
declared displacements** (the run record's contamination section). They were written to make gates
able to fail and the rule executable, not in response to those outcomes. A reader should still
weigh them as post-exposure.

**Terms used below.** A *window* is one of the 60 s analysis windows. An *interior window* is one
that is neither the first nor the last window of its recording. A *cell* is one stream at one
declared *J*. *Bootstrap* means 2,000 resamples of mice with replacement.

#### The outcome, completed

- **Each cell** gets one of four results.
  - **PASS:** every gate passes and every control is valid.
  - **FAIL:** a gate fails with its controls valid, and that failure is decided. For the leak
    gate, decided means the lower bound is above 0.55.
  - **UNDECIDED:** no gate fails decidedly, but at least one could not pass. For the leak gate,
    that means the upper bound is at or above 0.55 and the lower bound is at or below 0.55. A
    cell whose can-pass check fails (see *The leak gate*) is also UNDECIDED.
  - **VOID:** a control needed by some gate is invalid.
- **Each stream:** PASS if any cell passes. Otherwise FAIL only if **every** cell is FAIL.
  Otherwise VOID if every non-FAIL cell is VOID. Otherwise UNDECIDED. **A void or undecided cell
  can never make a stream FAIL.**
- **Cossart** is tied to the lab folder by grid position: smallest, middle, largest. Its leak
  result is read at the position of the smallest passing cell among the lab streams.

| fast | slow | Cossart leak at that position | outcome |
|---|---|---|---|
| PASS | PASS | PASS | **VIABLE** |
| PASS | PASS | FAIL, UNDECIDED or VOID | **NARROWED** — claims name the lab folder |
| PASS | FAIL | any | **NARROWED** — claims name the fast stream |
| FAIL | PASS | any | **NARROWED** — claims name the slow stream |
| FAIL | FAIL | — | **STOPPED**, scoped as below |
| any other combination | | | **UNRESOLVED** — nothing is read about the candidate |

- **After UNRESOLVED:**
  - **A VOID stream may be rerun**, changing only the instrument whose control failed. No
    threshold, displacement, window, bin or seed rule may change.
  - **An UNDECIDED stream is not rerun.** There are no more recordings to add. It is written up
    as "not decidable on these data", and it does not stop the goal.

#### The leak gate

- **Which windows count:** the gate is scored on **interior windows only**, which removes the
  generation-edge loss. The same statistic on all windows is reported beside it and does not
  gate. The runner reports the pair count per stream from the window layout before any
  surrogate is scored.
- **The bounds are one-sided.** All three use the mouse bootstrap:
  - **PASS** if the 98.33rd percentile is below 0.55.
  - **Decided FAIL** if the 1.67th percentile is above 0.55.
  - **Positive control valid** if uniform dither's 1.67th percentile is above 0.55.
- **The bootstrap refits.** Each resample re-runs the mouse-grouped cross-validation on the
  resampled mice. A mouse drawn twice stays inside one fold. Each resample also draws a fresh
  fold seed, so variation between fold assignments sits inside the interval rather than being
  chosen once.
- **Can-pass check:** before the candidate is scored, two independent rigid-shift draws at the
  same *J* go through the identical pipeline, one playing "real". If their 98.33rd percentile is
  at or above 0.55, the gate cannot pass on these data and the cell is UNDECIDED.
- **Negative control:** unchanged, 4 or more of 20 seeds. It is labelled a check of the
  permutation machinery. Nothing decides on its P values.

#### The count gate

- **What is counted:** occupied frames per ROI per interior window, so two onsets in one frame
  count once. That is the input `tube` sees. The statistic is surrogate minus real, averaged
  within mouse.
- **Pass:** the two-sided 96.67 % bootstrap interval (1.67th to 98.33rd percentile) lies inside
  ±2 % of the mean real occupied-frame count per ROI per interior window. That is equivalence by
  two one-sided tests at 0.05/3 each.
- **Edge windows** (first and last) are reported separately, and a count difference there does
  not gate. If a later step trains on whole recordings, that edge difference is a precondition
  to address there.
- **Control:** `edge_thinning` at a **fixed 5 s**, expected loss about 4 %, must fall outside
  ±2 %. If it does not, the count gate is VOID.

#### The destruction gate

- **The bin is given in seconds:** 1.0 s, which is 10 frames.
- **Slow is scored at 1.0 s and at 2.0 s**, the MATLAB assessor's slow default, and must pass
  at both.
- **Retained** is computed as the code does it: planted minus unplanted excess after the
  surrogate, divided by the same difference before, averaged over draws.
- **Replication:** 5 independent twins per stream and participation level, 40 surrogate draws per
  twin, and 200 assessor surrogates per score.
- **Pass:** the 98.33rd percentile of retained is at most 0.25, under a bootstrap that resamples
  twins and then draws within each twin. This applies at every gated K.
- **Gated K:** a K is gated only if both of these hold.
  - **Visible:** the excess before the surrogate is at least 1.0.
  - **Not saturated:** the saturation table does not put P(largest bin ≥ K) at or above 0.95 for
    the planted event after the shift.
  - If no K is gated, the cell is VOID for destruction.
- **The saturation table** is computed by the runner's first step from a synthetic event model
  alone: participants, 1-frame planted jitter, the shift, and the bin. It is committed before
  any score is produced.
- **Controls:**
  - **`freeze_half` applied to homogeneous resample** is the graded control. At K = 4 it must
    read retained between 0.10 and 0.90, and at least 0.10 away from homogeneous resample's own
    value. Otherwise the cell is VOID.
  - **Homogeneous resample** must retain at most 0.10. It is labelled a guard against saturation.
  - **Do-nothing** is scored with a different assessor seed on its "after" side and must retain
    at least 0.9. It is labelled a check of the machinery.

#### Randomness

**Every random key is salted with the run tag `confirm-2026-09-14`:** surrogate cell ids, twin
seeds, the assessor seed, fold seeds, and negative-control seeds (1000 to 1019). A test asserts
that no key equals one that `tools/build_surrogate_screen.py`'s 2026-09-11 scheme would produce.

#### What was known before signing

- **Exploratory results already existed** at every declared cell except fast 5.0 s.
- **The smallest *J* in each stream was chosen by this leak criterion**, from fast rows the
  seed-0 defect had voided.
- **In the slow stream, 0.7 s leaked**; 1.4 s was the only slow displacement that did not.
- **After signing, a reviewer quoted exploratory outcomes** at declared displacements.

**So a VIABLE or NARROWED result is reported as "held up under a rule fixed after an exploratory
look at the same recordings".** It is never reported as a confirmation or a replication.

#### What a PASS may claim

- **Leak:** a PASS means "not separable by this per-ROI, coordination-blind linear discriminator
  on 60 s interior windows, per stream". It does not mean "no leak".
- **Offsets:** fast and slow receive independent offsets. A model at the next tier that sees both
  streams must use one offset per ROI across both, or take one stream only.
- **The largest *J*:** a pass there is reported as removing "coordination up to *J*".
- **Destruction:** a PASS is a statement about synthetic twins sized like the stream.

#### What STOPPED means

- **STOPPED stops the goal only when the failure is intrinsic**: no cell in either stream passes
  both the leak and the destruction gate with its controls valid. A FAIL traced to a fixable
  instrument or to window edges is written up as that, and it does not stop the goal.
- **Joint-ISI:** "was never measured" above is wrong. Joint-ISI was measured where tractable (the
  lab folder, fast 2.5 s, slow 5.6 s and 11.2 s) and leaked at every cell it reached.
- **Before any model that pools across ROIs**, whatever this run's outcome, the aggregate-channel
  leak test from the `tube` todo is still required.

#### Groups

- **Reported per group:** leak accuracy, count difference and zero-event share, for each of the
  four groups, beside every pooled verdict (FOUNDATIONS §9).
- **Declared now:** if a stream passes pooled while any group's leak point estimate is at or
  above 0.55, the outcome is NARROWED for that stream and the claim names the group.
