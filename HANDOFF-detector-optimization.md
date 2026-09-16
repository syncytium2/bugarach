# HANDOFF — where detector optimization actually stands

**Written 2026-09-16, at Tony's instruction**, pausing work on the plain-language review:

> let's pause the doc development. write a handoff summarizing the status of optimization of the
> "program" detectors. i can't release these data in the current state. it looks unfinished and no polish
> can hide that.

> **Corrected 2026-09-16, the same day.** The first version judged every setting on F1 alone and never
> mentioned the **promiscuity gate** — the ceiling on how often a detector may fire where nothing was
> planted, which `bench.pick_operating_point` has applied by default since 2026-08-22. Re-run through
> that picker, the same sweeps say something different: binned SCE's "0.13 F1 given up" is mostly the
> credit a detector gets for calling more bins, rate+context's quiet-background cost halves, LoCo's
> "tuned" value turns out stale, and the four selection rounds §2 called honest took picks the gate
> refuses. §1, §2, §3 and §6 are rewritten in place; Table 1 is new.

**He is right, and this file is the evidence rather than the reassurance.** The judgement below is that
the *method* is sound and the *coverage* is not: the calibration machinery exists, is tested, and refuses
bad answers — and neither the six deployed settings nor the rounds that assessed them went through it.
That is a fixable gap with a known shape, and most of the measuring is already done.

Everything here is derived from `bugarach.bench.OPERATING_POINTS`, `bench.MAX_PROBE_PER_MIN`, and the
2026-09-15 review build's `measurements/` (`sweeps.json`, `shipped.json`, `numbers.json`). No number below
is remembered; Table 1 was produced by feeding each stored sweep to `bench.pick_operating_point`.

---

## 1. The one-paragraph version

Each of the six detectors runs at a single stored setting. **Three of those six carry values their
functions were written with, and the three labeled "tuned" were chosen before the bench's background
took its current shape** — so none of the six stored values was chosen by the bench as it now stands.
Exactly one parameter per detector was ever swept; 13 other parameters declared in each detector's
operating point have never been varied. Put through the project's own picker, which refuses a setting
that fires too often where nothing was planted, **three of the twelve sweeps are refused for firing too
often, one is refused because its optimum sits on the edge of the grid, and one of the accepted answers
is not usable**: binned SCE fires about once every ten seconds in a block with nothing planted at
*every* threshold searched, so no threshold choice fixes it.

The largest consequences are not settings at all. **locust runs at a fixed one-second duration instead of
the measured ones, and binned SCE's calls are timed in a way that costs it credit** — both invalidate the
curves any retune would read. Among the settings themselves the gated gaps are small: LoCo about 0.02 F1
on both backgrounds, rate+context about 0.04 on quiet ones, SPIKE-synch about 0.03 on quiet ones.

---

## 2. What is solid, and should not be relitigated

Worth stating first, because "unfinished" is not "unfounded":

- **The bench is measured, not invented.** `n_roi`, background rate, jitter and participation were all
  fitted off real recordings on 2026-08-13, replacing guesses that made coordination 3–6× easier than it
  is. Before that fix every detector scored F1 ≈ 0.9–1.0 and the bench could not separate them.
- **The difficulty axis is measured.** `REGIMES` quiet/busy endpoints are the p25/p75 of per-ROI rate
  across real baseline windows, re-derived 2026-08-20 from the approved export folder.
- **The refusal machinery exists and is tested.** `pick_operating_point` refuses three kinds of bad
  answer rather than reporting them — an optimum on the edge of the grid (`EdgeOfRange`), a sweep where
  every value scores the same (`DegenerateSweep`), and a winner that fires too often where nothing was
  planted (`TooPromiscuous`) — and `tests/test_bench.py` covers it.
- **Two detectors are, on their swept parameter, genuinely at their optimum.** CoactDetect and locust
  are accepted by the gated picker at their stored value on the busy background, and on the quiet one
  at a neighboring value worth 0.002 F1 more (Table 1).

**What is not solid, and the first version said it was:** the four selection rounds. They pick a setting
on held-out recordings and score on recordings never seen, which is the right *shape* of procedure — but
they come from `tools/fair_bakeoff.py`'s per-fold selection, which takes the raw F1 maximum over the grid
and never calls `pick_operating_point`, so it gets **none of the three refusals**. That was found and
filed on 2026-08-28
([`docs/todo/2026-08-28-the-bakeoff-calibrates-without-the-gate.md`](docs/todo/2026-08-28-the-bakeoff-calibrates-without-the-gate.md)),
and Tony ruled the same day that the scripted bake-offs are stale and the next one runs in the app. The
review build still reads them (`tools/make_detector_review.py`, the `per_fold` picks). §3.4 shows what
that costs.

**The gap is coverage.** The machine that would refuse a bad operating point exists; neither the deployed
table nor the rounds that assessed it passed through it.

---

## 3. Where each detector actually stands

The **promiscuity probe** is a five-minute block of the bench recording (1200–1500 s) where background
firing is raised and no coordinated event is planted. Every call a detector makes there is a false alarm,
counted as *firings per minute in the empty block*. `MAX_PROBE_PER_MIN` sets a ceiling per detector from
its own measured firing at the stored setting: CoactDetect, LoCo and SPIKE-synch 1, rate+context 2, binned
SCE 9, locust 25 firings per minute.

**Table 1. Each stored sweep, put through `pick_operating_point`.** Every cell is *setting → F1 (firings
per minute in the empty block)*. F1 is dimensionless. Settings are in each detector's own units:
rate+context's `excess_threshold_hz` in hertz; CoactDetect's `alpha` a dimensionless probability; SPIKE-synch's
`C_threshold` a dimensionless coincidence value between 0 and 1; LoCo, binned SCE and locust thresholds are
percentiles. "Stored" is what runs on every real recording. Each detector–background pair is one sweep
over the same 24 simulated recordings.

| detector · background | stored | best on F1 alone | ceiling (firings/min) | the picker says | best under the ceiling |
| --- | --- | --- | --- | --- | --- |
| rate+context · quiet | 5.0 Hz → 0.633 (0.6) | 2.0 Hz → 0.710 (5.3) | 2 | **refused: fires too often** | 4.0 Hz → 0.669 (1.8) |
| rate+context · busy | 5.0 Hz → 0.627 (1.1) | 5.0 Hz → 0.627 (1.1) | 2 | accepts 5.0 Hz | 5.0 Hz → 0.627 (1.1) |
| CoactDetect · quiet | 1e-4 → 0.741 (0.06) | 1e-3 → 0.743 (0.19) | 1 | accepts 1e-3 | 1e-3 → 0.743 (0.19) |
| CoactDetect · busy | 1e-4 → 0.667 (0.06) | 1e-4 → 0.667 (0.06) | 1 | accepts 1e-4 | 1e-4 → 0.667 (0.06) |
| LoCo · quiet | 99.9 → 0.719 (0.06) | 99.5 → 0.738 (0.20) | 1 | accepts 99.5 | 99.5 → 0.738 (0.20) |
| LoCo · busy | 99.9 → 0.645 (0.03) | 99.5 → 0.661 (0.14) | 1 | accepts 99.5 | 99.5 → 0.661 (0.14) |
| binned SCE · quiet | 99.0 → 0.370 (5.8) | 75 → 0.452 (5.9) | 9 | **refused: optimum on the grid's edge** | 75 → 0.452 (5.9) |
| binned SCE · busy | 99.0 → 0.449 (5.6) | 85 → 0.625 (5.9) | 9 | accepts 85, but see §3.3 | 85 → 0.625 (5.9) |
| locust · quiet | 99.999 → 0.574 (8.1) | 99.9999 → 0.576 (4.4) | 25 | accepts 99.9999 | 99.9999 → 0.576 (4.4) |
| locust · busy | 99.999 → 0.557 (4.5) | 99.999 → 0.557 (4.5) | 25 | accepts 99.999 | 99.999 → 0.557 (4.5) |
| SPIKE-synch · quiet | 0.1 → 0.486 (0.3) † | 0.04 → 0.529 (1.05) | 1 | **refused: fires too often** | 0.08 → 0.515 (0.6) |
| SPIKE-synch · busy | 0.1 → 0.470 (0.6) † | 0.005–0.02 → 0.507 (1.6) | 1 | **refused: fires too often** | 0.12 → 0.471 (0.5) |

† 0.1 is not on SPIKE-synch's sweep grid; these two cells come from the review's separate run at the
stored setting (`shipped.json`), which matches the sweep exactly wherever the two overlap.

Five defects are visible in that table.

### 3.1 Three of six were never calibrated, and the three that were are older than the bench

rate+context, binned SCE and SPIKE-synch carry the values their functions were written with. This is the
sentence that reads worst to an outside reviewer, and it is true.

It also **is not** merely cosmetic: `bench.py` refuses to run a detector at its signature default
precisely because the difference can be large — CoactDetect at its own default `alpha=0.01` scores F1
0.72 where the calibrated point scores 1.00 on the sparse regime.

**"Tuned" needs its date.** The `source` strings for LoCo and CoactDetect in `OPERATING_POINTS` were written
on 2026-08-13; locust's percentile was retuned on 2026-08-20. The bench background stopped being flat — the
burst and rate shape fitted off real recordings — on 2026-08-28. So all three "tuned" values were chosen
against an earlier bench than the one Table 1 measures. CoactDetect's source is also not a picker run at
all: it is a point read off the `explore_sce` viewer.

**LoCo is the one where that matters**, and the first version of this file did not count it: the gated
picker accepts 99.5 on *both* backgrounds, at 0.019 F1 more on quiet and 0.015 more on busy, firing 0.2
times per minute against a ceiling of 1. Its stored 99.9 is stale, not a choice.

### 3.2 The optimum moves with background — less than it looked

**rate+context is the example.** Scored on F1 alone, its quiet optimum is 2.0 Hz and the stored 5.0 Hz
costs 0.08 F1. But 2.0 Hz fires 5.3 times per minute in the empty block against a ceiling of 2, so the
picker refuses it. The best quiet setting under the ceiling is **4.0 Hz, F1 0.669 against the stored
0.633 — a real cost of about 0.04, not 0.08.** The lab's untreated recordings vary 3.7-fold in rate among
themselves, so both ends of that axis are real recordings, not hypotheticals.

A single value is defensible, and it has to be chosen in writing. **4.0 Hz has the best mean F1 across
the two backgrounds (0.637 against 5.0 Hz's 0.630), but on the busy background it fires 2.3 times per
minute, over the ceiling of 2.** 5.0 Hz is the best value that passes the gate on both. So the choice is
between 5.0 Hz — gate-clean everywhere, 0.04 F1 lower on quiet backgrounds — and 4.0 Hz with a deliberate,
recorded decision about the busy-background ceiling. Right now it is neither: 5.0 Hz is what the function
was written with.

**SPIKE-synch** has the same shape. Its gated optima are 0.08 on quiet backgrounds and 0.12 on busy ones;
the stored 0.1 sits between them and scores within 0.03 F1 of the quiet one and level with the busy one.

### 3.3 One search was too narrow, one missed its own value, and one answer cannot be used

- **binned SCE, quiet** — optimum at `threshold_pctile=75`, the **floor** of its grid. The picker refuses
  it as an edge optimum.
- **SPIKE-synch's grid does not contain its deployed value.** Stored is 0.1; the grid is 0.005, 0.01,
  0.02, 0.04, 0.08, 0.12. The review measured 0.1 separately (Table 1, †), which is how we know it is
  competitive, but the sweep itself cannot place it. **The fix is to put 0.1 on the grid, not to widen
  the grid downward:** F1 and firing rate are *identical* at 0.005, 0.01 and 0.02 on both backgrounds.
  The floor is a flat plateau, not a climb — the synchrony profile is quantized in steps of one ROI's
  share of the field, so every threshold below one step is the same threshold (`DegenerateSweep`'s
  docstring) — and values below 0.005 would measure nothing.
- **binned SCE, busy, is accepted at 85 and should not be installed.** binned SCE fires 5.4–5.9 times per
  minute in the empty block **at every threshold on the grid, 75 through 99.9, on both backgrounds** —
  roughly one call for every 10-second bin. Its ceiling of 9 was set from its own measured firing, so the
  gate cannot bite. Between 75 and 90 on the quiet background its F1 barely moves (0.44–0.45). What a
  looser threshold buys is more bins called: recall rises from 0.27 at the stored 99.0 to 0.49 at 75 while
  precision falls from 0.60 to 0.42. **The "0.13 mean F1 given up" in the first version of this file is
  mostly that credit.** Installing 75 or 85 would ship a detector that marks nearly every bin. Its problem
  is structural — the 10-second bin width, how its calls are timed (§5.1), and its near-random placement
  on this bench
  ([`docs/todo/2026-09-08-binned-sce-is-close-to-random-placement-here.md`](docs/todo/2026-09-08-binned-sce-is-close-to-random-placement-here.md)).

`OperatingPoint`'s own docstring: *"if the F1-optimum lands on an end of it, the search was too narrow
and `pick_operating_point` says so rather than reporting the boundary as an answer."* binned SCE's quiet
sweep violates that rule. SPIKE-synch's missing value and binned SCE's unusable busy answer are different
defects — the first is a grid that omits the deployed setting, the second a gate whose ceiling was set
where the detector already fires.

**Also to reconcile:** `src/bugarach/detectors/sync.py`, in the comment above `PROFILE_BIN_SEC`, says
`C_threshold`, `C_min`, `max_gap` and `min_n` were each *measured* at 10 Hz imaging. That contradicts the
"code default" label SPIKE-synch carries here and in
[`docs/todo/2026-09-16-three-detectors-run-at-code-defaults.md`](docs/todo/2026-09-16-three-detectors-run-at-code-defaults.md).
One of the two is wrong, and nobody has checked which.

### 3.4 The selection rounds took picks the gate refuses

The four rounds' picks on the quiet background (`numbers.json`, `opt_quiet_*.picks`), with how many of
the four fire over that detector's ceiling in its full sweep (`picks_over_limit`). CoactDetect's picks are
shown as the review displays them, **as 1/`alpha`**: "10,000" is `alpha=1e-4`, the stored value.

| detector | the four rounds picked | picks over the firing ceiling |
| --- | --- | --- |
| rate+context | 2, 2, 2, 2 (Hz) | **4 of 4** |
| SPIKE-synch | 0.04, 0.04, 0.04, 0.04 | **4 of 4** (and 4 of 4 on busy, at 0.005) |
| LoCo | 99, 99, 99.5, 99 | 0 of 4 |
| binned SCE | 75, 75, 75, 85 | 0 of 4 |
| CoactDetect (1/`alpha`) | 10,000 · 1,000 · 1,000 · 10,000 | 0 of 4 |
| locust | 99.9 · 99.9 · 99.9999 · 99.9999 | **2 of 4** |

Two things follow. **Every round's rate+context and SPIKE-synch number was earned at a setting the
project would refuse to ship**, so the review's per-round scores for those two are not scores of any
deployable detector. And **half of locust's thousandfold spread is gate-refused picks**: the two 99.9
picks fire 32 times per minute against a ceiling of 25. The spread that remains, 99.999 against 99.9999,
is a flat curve (0.574 against 0.576 F1).

The ungated rounds also took edge picks the picker would refuse: three of LoCo's four quiet picks are
99, the floor of its grid, and three of binned SCE's are 75, the floor of its.

The first version of this section read the disagreement as "24 recordings cannot resolve a flat curve".
Some of it is that. Much of it is picks that should never have been candidates. **Fold agreement is not
the right stability measure anyway** — see §6, step 3.

---

## 4. What has never been optimized at all

Every detector had **exactly one** parameter swept. Counting only the parameters **declared** in each
detector's `OperatingPoint` — excluding `n_surrogates` (a precision/compute knob, not a detection
threshold) and rate's `grid_dt` (fixed to the generator's grid) — **13 declared detection parameters have
never been varied**:

| detector | swept | declared, never swept |
| --- | --- | --- |
| LoCo | `threshold_pctile` | `bin_width_sec`, `context_win_sec`, `thr_step_sec`, `merge_gap_sec` |
| SPIKE-synch | `C_threshold` | `tau_max`, `max_gap`, `C_min` |
| CoactDetect | `alpha` | `int_win_sec`, `context_win_sec` |
| rate+context | `excess_threshold_hz` | `context_win`, `rate_win` |
| binned SCE | `threshold_pctile` | `bin_width_sec` |
| locust | `sce_percentile` | `active_duration_sec` |

The functions take more than their operating points declare. `loco_detect` alone also has `min_rois`,
`guard_sec`, `null_context_mode` and `onset_field`; SPIKE-synch's `min_n` runs at its signature default; the
others have the same kind of tail. Those run at their signature defaults and are not in the 13.

Two of these are known to matter rather than suspected:

- **binned SCE's `bin_width_sec=10.0`** is the cause of its scoring penalty (§5.1) and, from §3.3, the
  likeliest reason it fires about once per bin at any threshold. Threshold and bin width are not
  independent and have never been searched together.
- **locust's `active_duration_sec=1.0`** is not a tuning question but a **correctness** one — see §5.2.

---

## 5. The two defects that are not about settings

### 5.1 binned SCE's calls are timed in a way that loses it credit

Scored as the standard run scores it, binned SCE reaches F1 0.37 on the quiet background. Scored over the
whole 10-second bin each call came from, it reaches 0.45. **The difference is in how a call's time is
reported, not in what the detector found.** Every binned SCE curve in Table 1 is scored the first way, so
the sweep a retune would read is itself distorted — and it is the detector the review currently treats
most harshly.

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
[`docs/todo/2026-09-16-locust-ran-at-a-fixed-one-second.md`](docs/todo/2026-09-16-locust-ran-at-a-fixed-one-second.md).
**This one blocks release on its own**: it is not a suboptimal setting, it is a detector not doing what
its description says.

---

## 6. What finishing this actually costs

In order. The order is forced: the first step changes the curves every later step reads.

**1. Correctness first — locust's durations (§5.2) and binned SCE's call timing (§5.1).** Both invalidate
the sweeps a retune would use: locust's percentile was fitted against the fixed second, and binned SCE's
curve is scored over the wrong stretch. Tony said on 2026-09-16 to start on this immediately; it is in
progress in a separate session.

**2. Retune only through `pick_operating_point`, never raw argmax.** Each new value's `source` string names
the run that chose it.
- locust: re-sweep `sce_percentile` after the durations fix.
- binned SCE: threshold × bin width, jointly, after the timing fix. **Do not widen its threshold grid
  first** — at a 10-second bin it fires about once per bin at every threshold (§3.3), so more threshold
  values would measure the same thing.
- LoCo: 99.9 → 99.5, which the picker already accepts on both backgrounds.
- rate+context: 4.0 Hz or 5.0 Hz, with the reason written down — 4.0 Hz is the quiet-background gated
  optimum but fires over its ceiling on busy backgrounds (§3.2).
- SPIKE-synch: add 0.1 to the grid, then pick; and reconcile `sync.py`'s "measured" comment with the
  "code default" label (§3.3).

**3. Replace fold agreement with a real-recording stability measurement.** For each detector, run the real
recordings at every setting the gated picker accepts as near-optimal and measure how much the calls change
(`real_detections.json` in the review's measurements folder holds the calls at the stored settings, which is
the starting point). If the calls barely move across those settings, the choice of value does not matter
for release, and saying so is a stronger claim than any single optimum. If they move, that is the finding
the review has to carry.

**4. A decision, not a task: the background policy.** Once the gate is on, the question of whether a
single stored value per detector is the right shape narrows mainly to binned SCE. rate+context and
SPIKE-synch each have a value that is gate-clean on both backgrounds and close to both optima (§3.2);
LoCo, CoactDetect and locust barely move. The alternative for binned SCE — a setting that adapts to the
recording's own background rate, as several of these detectors already do internally for their threshold
— should wait until step 2 has told us what its bin width does.

**Still true, and not first:** two-parameter sweeps where parameters are known to interact beyond binned
SCE, and the declared-but-never-swept parameters of §4.

---

## 7. What must not happen

- **Do not move `OPERATING_POINTS` casually.** It moves the viewer, `detections.csv`, every real-recording
  call, both review documents, and the MILESTONES rows pinned to those numbers. It is a release event,
  not an edit.
- **Do not select a setting by raw F1 maximum.** `pick_operating_point` exists because the maximum can be a
  setting that fires on nothing, sits on the edge of the grid, or was never measured at all. The first
  version of this file made exactly that mistake reading the sweeps by eye.
- **Do not tune against the simulator and call it done.** Every value above is fitted to planted events
  from a generator whose faults the review lists. Better F1 on the bench is not the same as better calls
  on a slice, and the gap is unmeasured because real recordings have no answer key — which is why §6
  step 3 measures stability on them instead.
- **Do not raise the session-briefing budget** to clear the red CI on PR #587. The overage is caused by
  the number of open waiting-on-Tony todos; ruling on them is the fix.

---

## 8. State of the tree

- Branch `detector-review-doc`, pushed. PR #587 open, CI red for the briefing-budget reason above, plus a
  pre-existing `tests/test_sapper.py::test_tracked_tree_is_clear` failure (31 WARN "data is plural" hits
  in `.claude/hooks/` and `docs/GLOSSARY.md`, none from this work).
- **The plain-language review is paused mid-review, not abandoned.** 35 numbered notes with diagnosis and
  fix in [`docs/reviews/detector_review_plain_notes.md`](docs/reviews/detector_review_plain_notes.md);
  companion handoff for that work in
  [`HANDOFF-detector-review.md`](HANDOFF-detector-review.md). The built pages are in the darkroom at
  `2026-09-15-detector-review-plain/`. **Its sweep figure circles the ungated round picks of §3.4**
  (`tools/make_detector_review.py` reads them from the bake-off's `per_fold` records) and needs redrawing
  once §6 has run.
- Open todos bearing on this file: locust's fixed second; three detectors at code defaults; binned SCE's
  scoring; the bake-off calibrating without the gate; `sapper --all`'s Windows crash.

**When this is spent**: delete it if the calibration lands, or move it to
[`docs/handoffs/`](docs/handoffs/README.md) if §4 and §6 are still live. Do not leave it at the root
saying work is in flight once it is not.
