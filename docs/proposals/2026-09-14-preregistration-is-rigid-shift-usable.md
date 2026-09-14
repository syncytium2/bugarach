# Pre-registration — is rigid shift a usable surrogate on these data?

> **DRAFT, not signed.** Every number marked **⚠ OPEN** is a proposal for Tony to accept or
> change. When he signs at the bottom, everything above the line freezes: after that, only typos
> change, and the run reads its result against this page as written.
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

## The displacements — ⚠ OPEN

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

- **Pass at a *J*:** the upper 98.3 % bound on accuracy is **below 0.55** ⚠ OPEN — the screen's
  own smallest effect worth detecting. Not detecting a leak is not enough; the bound has to
  exclude one.
- **Positive control, uniform dither at the same *J*:** lower bound **above 0.55**. If it fails,
  that *J* is **void** for that stream: the test could not have seen a leak.
- **Negative control, real against real, 20 seeds:** void the stream if **4 or more of 20** seeds
  flag at α = 0.05 ⚠ OPEN. Three or more happens 7.5 % of the time by chance, four or more 1.6 %.
  **No single seed can void anything** — that was the defect.

### Count preservation — the surrogate must not change how many onsets there are

Rigid shift drops onsets pushed past the generation window's edge, and any model that averages
over ROIs sees a count change as a free win
([tube foot gun](../todo/2026-09-12-tube-cannot-tell-a-count-leak-from-coordination.md)).

- **Statistic:** per ROI and per analysis window, surrogate onset count minus real, paired,
  averaged within mouse.
- **Pass:** the 98.3 % interval over mice lies inside **±2 % of the mean real count** ⚠ OPEN.
- **Control:** the screen's `edge_thinning` control, which deletes onsets near the window edges,
  must *fail* this gate. If it passes, the statistic is too coarse to read and the gate is void.

### Destruction — the surrogate must remove planted coordination

**Instrument:** `surrogate_stats.destruction`, unchanged except the bin. Synthetic twins with the
stream's own per-ROI counts and floor, with and without planted events, each pushed through rigid
shift with the same key and scored by the assessor's selection-corrected coactivity excess.
**Retained** = excess the planted twin keeps after the surrogate, as a share of what it had
before. Participation 0.2 and 0.5, the assessor's K scan.

- ⚠ **OPEN — the timescale of "coordinated".** The screen scored destruction in a ±2-frame
  (0.5 s) bin. The assessor that proposes events uses **1.0 s**. A shift can clear a 0.5 s bin and
  still leave 1 s coincidences in place. **Proposed: score at 1.0 s**, the assessor's own
  definition, and report 0.5 s beside it.
- **Pass at a *J*:** retained share **at most 0.25** ⚠ OPEN, at every K where the planted
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
| Accepted as written, or amended as noted | |
| Signed | |
| Date | |

*Nothing above this line changes after signing, except typos.*
