# HANDOFF — where detector optimization actually stands

**Written 2026-09-16, at Tony's instruction**, pausing work on the plain-language review:

> let's pause the doc development. write a handoff summarizing the status of optimization of the
> "program" detectors. i can't release these data in the current state. it looks unfinished and no polish
> can hide that.

**He is right, and this file is the evidence rather than the reassurance.** The judgement below is that
the *method* is sound and the *coverage* is not: the calibration machinery exists, is tested, and refuses
bad answers — and the six deployed settings did not all come through it. That is a fixable gap with a
known shape, and most of the measuring is already done.

Everything here is derived from `bugarach.bench.OPERATING_POINTS` and the 2026-09-15 review build's
`measurements/` (`sweeps.json`, `shipped.json`, `numbers.json`). No number below is remembered.

---

## 1. The one-paragraph version

Each of the six detectors runs at a single stored setting. **Three of those six were calibrated; three
are the values the functions were written with.** For each detector, **exactly one** parameter was ever
swept — 13 other detection parameters have never been varied at all. Two of the six sweeps put their
optimum on the edge of the grid they searched, which the project's own code calls a search too narrow to
report. One detector's grid does not contain its own deployed value. And the optimum moves with how busy
the recording is, while one value is deployed for all of them.

The largest single consequence: **binned SCE gives up about 0.13 mean F1 to its stored setting**, before
counting a separate scoring defect worth roughly as much again.

---

## 2. What is solid, and should not be relitigated

Worth stating first, because "unfinished" is not "unfounded":

- **The bench is measured, not invented.** `n_roi`, background rate, jitter and participation were all
  fitted off real recordings on 2026-08-13, replacing guesses that made coordination 3–6× easier than it
  is. Before that fix every detector scored F1 ≈ 0.9–1.0 and the bench could not separate them.
- **The difficulty axis is measured.** `REGIMES` quiet/busy endpoints are the p25/p75 of per-ROI rate
  across real baseline windows, re-derived 2026-08-20 from the approved export folder.
- **The selection method is honest.** The rounds pick a setting on held-out recordings and score on
  recordings never seen. That is the right procedure and it is implemented correctly.
- **The refusal machinery exists and is tested.** `pick_operating_point` raises rather than reporting a
  boundary optimum as an answer, and `tests/test_bench.py` covers it.
- **Two detectors are, on their swept parameter, genuinely at their optimum.** CoactDetect and locust
  gain nothing from re-selection on either background.

**The gap is coverage.** The machine that would refuse a bad operating point exists; the deployed table
was hand-declared and did not all pass through it.

---

## 3. Where each detector actually stands

`stored` is what runs on every real recording. F1 at the stored value against F1 at each background's own
best value, from `sweeps.json`:

| detector | stored | origin | quiet: best (F1) vs stored | busy: best (F1) vs stored |
| --- | --- | --- | --- | --- |
| CoactDetect | `alpha=1e-4` | **tuned** | 0.001 (0.74) vs **0.74** | 1e-4 (0.67) vs **0.67** |
| locust | `sce_percentile=99.999` | **tuned** | 99.9999 (0.58) vs **0.57** | 99.999 (0.56) vs **0.56** |
| LoCo | `threshold_pctile=99.9` | **tuned** | 99.5 (0.74) vs 0.72 | 99.5 (0.66) vs 0.65 |
| rate+context | `excess_threshold_hz=5.0` | code default | **2.0 (0.71) vs 0.63** | 5.0 (0.63) vs **0.63** |
| binned SCE | `threshold_pctile=99.0` | code default | **75.0 (0.45) vs 0.37** | **85.0 (0.63) vs 0.45** |
| SPIKE-synch | `C_threshold=0.1` | code default | 0.04 (0.53) vs — | 0.005 (0.51) vs — |

Four defects are visible in that table.

### 3.1 Three of six were never calibrated

CoactDetect, LoCo and locust carry values chosen by measurement. rate+context, binned SCE and SPIKE-synch
carry the values their functions were written with. This is the sentence that reads worst to an outside
reviewer, and it is true.

It also **is not** merely cosmetic: `bench.py` refuses to run a detector at its signature default
precisely because the difference can be large — CoactDetect at its own default `alpha=0.01` scores F1
0.72 where the calibrated point scores 1.00 on the sparse regime.

### 3.2 The optimum moves with background, and one value is deployed

**rate+context is the clean example.** Its stored 5.0 is the *busy* optimum; on quiet backgrounds the
best value is 2.0 and the stored one costs **0.08 F1**. The lab's untreated recordings vary 3.7-fold in
rate among themselves, so both ends of that axis are real recordings, not hypotheticals.

A single compromise value recovers almost nothing (best single value 4.0, +0.01 mean). **The honest
options are a per-recording adaptive setting or an explicit, documented decision to optimise for one end
of the axis.** Right now it is neither — it is the busy optimum by accident, because 5.0 is what the
function was written with.

### 3.3 Two searches were too narrow, and one missed its own value

- **binned SCE, quiet** — optimum at `threshold_pctile=75.0`, the **floor** of its grid, F1 still
  climbing. The true optimum is below the range searched.
- **SPIKE-synch, busy** — optimum at `C_threshold=0.005`, the **floor** of its grid.
- **SPIKE-synch's grid does not contain its deployed value.** Stored is 0.1; the grid is
  (0.005 … 0.12) and 0.1 is not among them. Its sweep cannot say what the deployed setting is worth
  relative to the alternatives.

`OperatingPoint`'s own docstring: *"if the F1-optimum lands on an end of it, the search was too narrow
and `pick_operating_point` says so rather than reporting the boundary as an answer."* The rule is
written down and these three points violate it.

### 3.4 Selection is unstable where the curve is flat

The four rounds disagreed with each other for **four of the six** detectors (`opt_quiet_*.picks`):

| detector | the four rounds picked |
| --- | --- |
| rate+context | 2, 2, 2, 2 |
| SPIKE-synch | 0.04, 0.04, 0.04, 0.04 |
| LoCo | 99, 99, 99.5, 99 |
| binned SCE | 75, 75, 75, 85 |
| CoactDetect | 10,000 · 1,000 · 1,000 · 10,000 |
| locust | 99.9 · 99.9 · **99.9999** · 99.9999 |

locust's spread is a thousandfold on the same 24 recordings. This is not a bug — it says the F1 curve is
flat near the top and 24 recordings cannot resolve it. **But it means "the tuned setting" has no single
referent, and any recalibration has to report a stability claim alongside the value it picks.**

---

## 4. What has never been optimized at all

Every detector had **exactly one** parameter swept. Excluding `n_surrogates` (a precision/compute knob,
not a detection threshold) and rate's `grid_dt` (fixed to the generator's grid), **13 detection
parameters have never been varied**:

| detector | swept | never swept |
| --- | --- | --- |
| LoCo | `threshold_pctile` | `bin_width_sec`, `context_win_sec`, `thr_step_sec`, `merge_gap_sec` |
| SPIKE-synch | `C_threshold` | `tau_max`, `max_gap`, `C_min` |
| CoactDetect | `alpha` | `int_win_sec`, `context_win_sec` |
| rate+context | `excess_threshold_hz` | `context_win`, `rate_win` |
| binned SCE | `threshold_pctile` | `bin_width_sec` |
| locust | `sce_percentile` | `active_duration_sec` |

Two of these are known to matter rather than suspected:

- **binned SCE's `bin_width_sec=10.0`** is the cause of its scoring penalty (§5.1) and is also plausibly
  the reason its threshold wants to run so loose. Threshold and bin width are not independent and have
  never been searched together.
- **locust's `active_duration_sec=1.0`** is not a tuning question but a **correctness** one — see §5.2.

---

## 5. The two defects that are not about settings

### 5.1 binned SCE's calls are timed in a way that loses it credit

Scored as the standard run scores it, binned SCE reaches F1 0.37 on the quiet background. Scored over the
whole 10-second bin each call came from, it reaches 0.45. **The difference is in how a call's time is
reported, not in what the detector found.** Combined with the threshold defect, binned SCE's headline
number understates it substantially — and it is the detector the review currently treats most harshly.

Filed at
[`docs/todo/2026-09-15-binned-sce-calls-are-scored-over-the-wrong-stretch.md`](docs/todo/2026-09-15-binned-sce-calls-are-scored-over-the-wrong-stretch.md),
and see also
[`2026-09-08-binned-sce-is-close-to-random-placement-here.md`](docs/todo/2026-09-08-binned-sce-is-close-to-random-placement-here.md).

### 5.2 locust runs at a fixed one second

locust is duration-based, and everything published assumes it used measured durations. **It did not** —
`active_duration_sec=1.0` is a constant, and the calibrated `sce_percentile` was tuned against that
constant, so the two are coupled. Tony, reading the review: *"i hope we are actually using FWHM and
t_peak - t50rise"*.

Filed at
[`docs/todo/2026-09-16-locust-ran-at-a-fixed-one-second.md`](docs/todo/2026-09-16-locust-ran-at-a-fixed-one-second.md),
status waiting-on-tony. **This one blocks release on its own**: it is not a suboptimal setting, it is a
detector not doing what its description says.

---

## 6. What finishing this actually costs

Sorted by cost, and the first tier is nearly free because the measurements already exist.

**Tier 1 — no new computation. The sweeps are already on disk.**
1. Decide and install values for the swept parameter of rate+context, binned SCE and SPIKE-synch.
   `sweeps.json` already holds the full curve on both backgrounds.
2. State the background policy explicitly: one value tuned for which end of the axis, and why.

**Tier 2 — small, targeted runs.**
3. Widen binned SCE's grid below 75 and SPIKE-synch's below 0.005 until each optimum is interior; put
   SPIKE-synch's deployed value on its own grid.
4. Re-run selection and report a stability claim per detector, since four of six disagreed across rounds.

**Tier 3 — the real work.**
5. Two-parameter sweeps where the parameters are known to interact: binned SCE (threshold × bin width)
   first, since it is the worst-placed detector and the interaction is understood.
6. Fix locust's durations (§5.2), then **re-tune its percentile**, because the current one was fitted
   against the fixed second.
7. Fix binned SCE's call timing (§5.1), then re-score everything that quotes it.

**Tier 4 — a decision, not a task.**
8. Whether a single stored value per detector is the right shape at all, given §3.2. The alternative is a
   setting that adapts to the recording's own background rate — which several of these detectors already
   do internally for their threshold, just not for this parameter.

---

## 7. What must not happen

- **Do not move `OPERATING_POINTS` casually.** It moves the viewer, `detections.csv`, every real-recording
  call, both review documents, and the MILESTONES rows pinned to those numbers. It is a release event,
  not an edit.
- **Do not tune against the simulator and call it done.** Every value above is fitted to planted events
  from a generator whose faults the review lists. Better F1 on the bench is not the same as better calls
  on a slice, and the gap is unmeasured because real recordings have no answer key.
- **Do not raise the session-briefing budget** to clear the red CI on PR #587. The overage is caused by
  the number of open waiting-on-Tony todos; ruling on them is the fix.

---

## 8. State of the tree

- Branch `detector-review-doc`, pushed through `df33cd4`. PR #587 open, CI red for the briefing-budget
  reason above, plus a pre-existing `tests/test_sapper.py::test_tracked_tree_is_clear` failure (31 WARN
  "data is plural" hits in `.claude/hooks/` and `docs/GLOSSARY.md`, none from this work).
- **The plain-language review is paused mid-review, not abandoned.** 35 numbered notes with diagnosis and
  fix in [`docs/reviews/detector_review_plain_notes.md`](docs/reviews/detector_review_plain_notes.md);
  companion handoff for that work in
  [`HANDOFF-detector-review.md`](HANDOFF-detector-review.md). The built pages are in the darkroom at
  `2026-09-15-detector-review-plain/`.
- Open todos bearing on this file: locust's fixed second; three detectors at code defaults; binned SCE's
  scoring; `sapper --all`'s Windows crash.

**When this is spent**: delete it if the calibration lands, or move it to
[`docs/handoffs/`](docs/handoffs/README.md) if §4 and §6 are still live. Do not leave it at the root
saying work is in flight once it is not.
