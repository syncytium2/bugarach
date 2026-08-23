# Forks — what was chosen, what the alternative was, and how to go back

Tony, 2026-08-22: *"document each fork so if we need to go back or toggle we don't
start from scratch."*

Every entry is a place the project could have gone two ways. Each records **what
is live now**, **what the alternative is**, **the evidence that decided it**, and
— the part that matters when someone wants to reverse course — **exactly how to
flip it and what that costs.**

This is not an ADR index. ADRs record decisions that are meant to stand
([`adr/`](adr/), Nygard template, immutable once accepted). This records
**switches**, most of which are live parameters with a default, and it exists so
that reversing one is a lookup rather than an excavation.

**Reading order:** `#1` and `#2` govern everything below them.

---

## 1 · Mechanism changes land as flags defaulting to the original

**Live:** every mechanism change added during the revision is a keyword argument
whose default reproduces the MATLAB original exactly.

**Alternative:** change the detectors outright and re-baseline the parity fixtures.

**Why:** FOUNDATIONS §2 — *every detector matches its MATLAB original to 1e-9 in
every mode, and that is what makes the ports citable in place of the originals.*
A guard interval changes the numbers; so does a multiplicative bar. Done
carelessly the revision destroys the property the project's central claim rests
on. Done as flags, the port stays a port and the revised configuration is a named
alternative the bench can score against it.

**To flip:** change a default in the detector signature and regenerate
`tests/fixtures/ref_*.json` — which needs MATLAB **and** an interface2 checkout
(`tools/matlab_ref/README.md`; path order matters). **Cost: high and
cross-machine.** Do not do it to save a keyword argument.

**Watch for:** a flag whose default is *not* the original silently becoming the
shipped behaviour. `tests/test_rate_detect.py::test_the_guard_is_inert_at_its_default`
is the guard on that for `rate`; the other detectors need the same when they get
flags.

---

## 2 · The background shape is measured per corpus, not chosen

**Live:** `assess` fits the per-ROI heterogeneity from the folder it was handed
and emits it; `derive_spec` prefers that over any constant.

**Alternatives, both rejected:** a flat field (what `BENCH_RECORDING` still runs),
or this lab's fitted `MEASURED_RATE_SHAPE = 0.275` applied everywhere.

**Why:** flat is settled against by measurement — real windows leave ~35% of ROIs
silent against a flat field's 2%. And 0.275 is a fit over *this lab's* 81 baseline
windows, so handing it to another folder substitutes a constant for a measurement
exactly as flat does. Tony: *"This should be a toggle not a decision."*

**To flip:**
- **flat, deliberately** — pass `bg_rate_shape=None` to the generator. A flat
  field is `shape → ∞`, and a genuinely uniform corpus already fits that way
  (the estimator saturates and the assessment reports *flat*), so this is only
  for a diagnostic, never a default.
- **inherit this lab's shape** — it is still in `bench.MEASURED_RATE_SHAPE`,
  labelled as this lab's reference. `derive_spec` falls back to it, loudly and
  with the reason, when a corpus has too little baseline to fit its own.
- **Cost: low.** One parameter; nothing is baked in.

**Still open (Phase 2, not a decision):** `BENCH_RECORDING` runs flat, so the
bench and `derive_spec` disagree about what a recording looks like.

---

## 3 · rate+context: additive bar (live) vs multiplicative

**Live:** `threshold_mode="additive"` — fire where `rate − context ≥ 5 Hz`, the
MATLAB original.

**Alternative:** `threshold_mode="multiplicative"`, `rate ≥ α·context`, which is
how cell-averaging CFAR sets a threshold.

**Evidence, measured** (`tools/probe_rate_mechanism.py`, `baseline_quiet`, 3
seeds): additive F1 **0.636** with **2.0** probe firings; multiplicative
**0.667** with **0.0**; multiplicative + a 5 s guard **0.686**. The promiscuity
signature an additive offset was predicted to cause goes to zero.

**Why not switched already:** the campaign that would re-fit `α` has not run, and
`threshold_alpha=2.0` is a placeholder, not a calibrated value. Switching the
default before Phase 4 would ship an uncalibrated operating point.

**To flip:** `rate_detect(..., threshold_mode="multiplicative", threshold_alpha=α)`.
**Cost: low to try, and the α grid must be wide** — the optimum sat at 15–20 on
this bench and an initial grid topping out at 8 put it at the edge.

---

## 4 · Guard interval: off everywhere (live)

**Live:** `guard_sec=0.0` on all three of `rate`, `loco` and `coact` — landed on
the two surrogate detectors 2026-08-23 and measured in §4a below.

**Alternative:** a guard band excluded from the reference window — standard in
every CFAR detector since at least 1983.

**Evidence, and it is a negative worth keeping:** on `rate` the guard does
**nothing**, and the arithmetic says why. At a planted event the 1 s rate is
9.00 Hz against a 60 s context of 0.283 Hz — 3.1% of the peak. A 10 s guard halves
the context, exactly as designed, and so moves the threshold crossing by 0.143 Hz
**against a 2–5 Hz bar**. Swept across event spacings from 120 s down to 14 s,
F1 moves −0.006 to +0.000 (`tools/probe_guard_vs_spacing.py`).

**Two things that follow, and would otherwise be re-derived:**
- The guard is **coupled to #3** — it only helps once the bar is multiplicative
  (+0.019 there), because then a contaminated context *multiplies* into the
  threshold instead of adding 0.14 Hz to a constant.
- The place to test it is **`loco`/`coact`**, whose bar is a percentile of a null
  pool built from events *inside* the window, so contamination scales the
  threshold directly. That is also the shape of the regime-shift incident, whose
  victim was SCE's surrogate null rather than `rate`.

**To flip:** `guard_sec=<seconds>`, now on all three.

### 4a · Measured on `loco` and `coact`, 2026-08-23 — the prediction held

`tools/probe_guard_on_surrogates.py`, 4 seeds, shipped operating points. On
`baseline_quiet`, where contamination is **impossible by construction**, both move
−0.021 to +0.021 with no direction — the null result the geometry demands. On
`CROWDED_RECORDING` (#10) at `baseline_quiet`, where it is likely:

| detector | guard 0 | 5 s | 10 s | 20 s |
|---|---|---|---|---|
| CoactDetect | 0.786 | **0.820** | 0.815 | 0.786 |
| LoCo | 0.716 | 0.717 | 0.710 | 0.717 |

**CoactDetect gains +0.034, entirely through recall** (0.652 → 0.702) — the
predicted mechanism in the predicted place: crowding masks events, and removing an
event from its own null recovers some. The gain lands where it matters most:
at **0.18 participation — the measured real value, about six of thirty-three
ROIs** — recall goes **0.82 → 0.89**. Confirmed on the statistic rather than only
through the score: the mean null across candidate bins falls when the guard is on.

**LoCo shows no clear effect, and the reason is structural rather than
disappointing.** Its halves are *already one-sided* — the anchor is a boundary of
each half, not its centre — so an event at the anchor sits at the edge of the
reference and contributes far less than one at the centre of a centred window.
**LoCo was partly guarded by its own geometry all along**, which is also why its
guard needed no compaction while CoactDetect's did.

⚠ **Do not compare F1 across the two recordings.** The crowded one plants eight
times as many events, so a detector firing at a similar rate hits far more often
and its precision rises — CoactDetect reads a *higher* F1 crowded (0.786) than on
the bench (0.719) while recalling a fifth less. Only recall compares:
**0.833 → 0.652** for CoactDetect, **0.700 → 0.558** for LoCo.

### 4b · The first version of §4a was measured off the difficulty axis — what that cost, and what is left

**Corrected in place; §4a's table above is the re-measurement.** Kept because the
error is instructive and because anything quoting the old numbers needs to find
this.

`BENCH_RECORDING` carries no `bg_rate_hz` — the rate always arrives from
`REGIMES[regime]`, which `make_recording` merges in. **`make_crowded_recording`
merged no regime**, so `bg_rate_hz` fell through to `simulate_coordination`'s own
default of **0.05 Hz**: the pre-2026-08-13 invented value that
`BENCH_RECORDING`'s correction table names *"5× too busy"*, roughly 10× the quiet
endpoint. The recording built to isolate crowding was running off the axis.

`CROWDED_RECORDING`'s docstring shuts the probe and the distractors off
*"because a dense-but-random block would confound it with rate-keying"* — the
author saw the confound coming and closed the doors they knew about. It came in
through a keyword default. Every knob set deliberately was asserted in
`tests/test_bench.py`; the one that came from a default was not. It is now:
`test_the_crowded_recording_stays_on_the_difficulty_axis` checks the **realised**
rate against the chosen regime, so a background arriving from anywhere else fails
regardless of how it got in.

The recording is steeply sensitive to the thing that was wrong, which is why this
mattered — CoactDetect recall on the same 120 crowded events:

| background | bg Hz/ROI | recall | 0.30 | 0.18 | 0.10 |
|---|---|---|---|---|---|
| bench, 15 events, quiet | 0.0052 | 0.833 | 1.00 | 1.00 | 0.50 |
| crowded, `baseline_quiet` | 0.0052 | **0.652** | 0.98 | 0.82 | 0.15 |
| crowded, `baseline_busy` | 0.0190 | 0.460 | 0.94 | 0.42 | 0.02 |
| crowded, off-axis (pre-fix) | 0.0505 | 0.254 | 0.64 | 0.11 | 0.01 |

So the collapse §4a reported as *"most of their recall"* was **two thirds
background, one third crowding**: crowding costs CoactDetect 0.181 and LoCo 0.142;
the off-axis background cost another 0.398 and 0.289 on top.

**Two of the three candidates §4a named are dead, and should not be re-opened.**
An oracle emitting the exact planted times scores **F1 1.000** on the crowded
recording, and across every condition **zero** emitted spans cover two planted
events — so neither the greedy one-to-one matching in `score_detections` nor
episode merging contributes anything. Spans are 2.0 s (coact) and 0.70 s (loco)
against a 19.4 s median gap. Precision *rises* to 0.98–1.00 while the detection
count falls below the planted count: **the detectors are not firing wrongly, they
are silent**, which is a bar that went up.

**What is left is the real open item, and a guard is probably the wrong
instrument for it.** With the background held right, crowding still costs
0.14–0.18 of recall, concentrated in realistically-sized events, and the guard
recovers about a quarter of CoactDetect's loss and none of LoCo's. A guard excises
a span *adjacent to the anchor*; at a 19.4 s median gap the interference is spread
across the whole ±30 s reference. That is the **multiple-target** case, and
[`detector_history.md`](detector_history.md) §5.4 and §6.4 prescribe **censoring
inside the estimator** for it — which §5.5 wants tried on LoCo anyway, for the 17×
cost. Same experiment, two payoffs.

Reproduce both: `tools/probe_crowded_background.py`.

**Implementation note worth not re-deriving:** the two guards are *not* the same
change. LoCo's halves stay contiguous when a guard shrinks them, so it is two
bounds. CoactDetect's window is centred, so a guard holes it — and because the
null is a circular shift *within* the window, shifting on the original width would
wrap events across the excised span and re-import exactly what the guard removed.
Its retained span is therefore **compacted** onto one line before shifting, using
the fact that a uniform circular shift is translation-invariant so the test window
is a width rather than a position. `guard_sec` with
`null_context_mode="symmetric"` is refused rather than given a third variant.

---

## 5 · Scoring tolerance: a curve (live) vs a constant

**Live:** `bench.evaluate_curve` scores across `TOLERANCE_GRID` and
`describe_curve` reports "F1 x, flat from y s" — or refuses to give a bare number
for a detector still climbing. The old single-tolerance `evaluate(tol_sec=1.5)`
still exists and is unchanged.

**Alternative:** pick one constant. The inherited 1.5 s, or the ~0.75 s plateau,
or the 0.80 s median event width.

**Why the curve:** it is what DOSED does, and it dissolves the choice instead of
forcing it. Five of six detectors are flat well below 1.5 s, so the inherited
constant was granting slack nobody used.

⚠ **A correction, recorded because the earlier claim is still in a shipped
figure.** `docs/learned/two_decisions.png` panel C says *"ranking unchanged from
0.4 s to 2.0 s"*. That is true of the archived `tolerance_sweep.json` and **not**
true at the shipped operating points, where `sce` and `sync` swap between 0.4 s
and 0.5 s. The robust claim, true in both: **the top of the table never moves, and
every reordering involves the one detector whose score depends on the
tolerance.** Pinned by
`tests/test_tolerance_curve.py::test_only_the_tolerance_dependent_detector_reorders`.

**To flip:** call `evaluate(..., tol_sec=x)` and quote one number — but
`describe_curve` exists so nothing has to.

---

## 6 · `DegenerateSweep` refuses a total tie only

**Live:** `pick_operating_point` raises when **every** grid point ties.

**Alternative:** refuse "flat within noise" — a near-degenerate curve.

**Why the strict rule:** partial ties are real and informative (the bench's own
`sweep("sync", "baseline_busy")` moves 0.58 → 0.48 with its bottom three tied), so
refusing them needs a noise model this project does not have and would reject
curves that carry information. A total tie cannot be a measurement of anything, so
it is the case refusable without one.

**Known cost, recorded rather than implied:** the gate is narrower than the
disease. `sync`'s shipped grid is `[0.400, 0.400, 0.400, 0.400, 0.476, 0.316]` —
four of six identical — and the gate stays silent on it. Pinned by
`tests/test_bench.py::test_syncs_grid_is_mostly_degenerate_and_the_gate_does_not_catch_it`,
which is **expected to fail when the grid is fixed**; update the measurement then
rather than deleting it.

**To flip:** widen to a fractional-spread test, which needs the noise model above.

---

## 7 · Quote verification is a report, not a gate

**Live:** `tools/verify_quotes.py` prints hits and misses. Not wired into CI.

**Alternative:** fail a build on an untraceable quotation.

**Why:** it still traces only 11 of 30 on `detector_history.md` because OCR breaks
words across lines without hyphens, while hand-checking confirmed all sixteen
paper quotations were genuine. A gate whose alarms are mostly false is one people
learn to ignore.

**To flip:** fuzzy matching over exact substring, then wire it in —
`todo/2026-08-22-quote-verification-is-not-a-gate-yet.md`. **The hazard it
documents is worth more than the tool**: extracting a two-column PDF without
`-layout` splices the columns and can *manufacture* a quotation that appears
nowhere on the page.

---

## 8 · Detectors kept, not retired

**Live:** all six ship.

**Alternative considered and rejected:** retire the weak ones.

- **binned SCE** (F1 0.422) — kept as a **reference row**, because its value is
  comparability with the field's own rule, not accuracy. Tuning it to compete
  destroys the only thing it is for.
- **CICADA** — kept, and its citability is the asset. It is already modified
  (rise-interval active duration); the recommendation is to carry **both** modes
  and name which produced any output.
- **SPIKE-synch** — kept. Its 0.254 is the score of a **degenerate sweep**
  (#6), not of the detector, and must not be quoted as accuracy until
  `(C_threshold, C_min)` are swept together.
- **LoCo's `maxlt`** — **do not replace with an order statistic.** Gandhi &
  Kassam score greatest-of as better than any other mean-level scheme at clutter
  transitions, which is the nonhomogeneity this preparation actually has; Hansen
  & Sawyers price the split at 0.1–0.3 dB. The fix for its multiple-target blind
  spot is censoring *inside* it.

**To flip any of these:** the argument is in
[`detector_history.md`](detector_history.md) §6, with the primaries on the shelf
at `<darkroom>/bugarach/lit/radar/`.

---

## 9 · The probe gates the calibration, not the score

**Live:** `pick_operating_point` raises `TooPromiscuous` when the F1-optimum
exceeds that detector's `MAX_PROBE_PER_MIN` ceiling.

**Alternatives:** fold the probe into F1 — **rejected, and it stays rejected**,
because the headline then measures how hard the probe was set, and CICADA reads
F1 0.09 that way against a true 0.68. Or leave it a diagnostic column nobody
reads, which is what it was.

**Why this shape:** the budgets already existed, but only in `tests/test_bench.py`.
So the probe could fail a **shipped setting** and not the **sweep that chooses
one** — and operating points come from sweeps. Moving the budgets into `bench.py`
and gating selection on them closes that without touching F1.

**It fires on a real case immediately:** `rate`'s best-F1 setting on
`baseline_quiet` (0.79 at `excess_threshold_hz=3`) fires 3.6/min into a block
containing nothing, against a ceiling of 2.0. The *shipped* value is 5.0 and is
within budget — so nothing broken shipped, and a re-calibration would have chosen
the promiscuous point. Recorded by
`tests/test_bench.py::test_rates_own_f1_optimum_is_over_its_probe_budget`, which
is expected to change when #3 lands.

**To flip:** `max_probe_per_min=None` restores F1-only selection; a number
overrides the ceiling. **Deliberately does not re-rank** — a promiscuous winner is
a refusal, not an invitation to take second place silently.

---

## 10 · Crowding is a separate recording, not a change to the bench

**Live:** `CROWDED_RECORDING` / `make_crowded_recording(regime, seed)` — 120
events at a 14 s floor, median gap 19.4 s, 97 of 119 gaps putting two events
inside one ±30 s reference window, on a background chosen from `REGIMES` exactly
as `make_recording`'s is.

**Alternative:** lower `BENCH_RECORDING["min_sep_sec"]`.

**Why not that:** it would re-derive every operating point and invalidate every
published number, for a reason unrelated to why they were derived. Adding a
condition is cheaper than moving the goalposts.

**What it fixes:** the bench plants events **≥120 s apart** against a ±30 s
reference window, so reference-window contamination — the failure guard cells
exist for, and the shape of the regime-shift incident — was **impossible by
construction** on the recording the six are scored on. That is why the incident
was found by hand rather than by the suite.

**Two things worth not re-deriving:** `min_sep_sec` is a *floor under a renewal
process*, not a target — at the bench's own event count it changes almost nothing
(median gap ~70 s, 5 of 35 gaps inside a window). **The count is what crowds.**
And 14 s is the spacing of the historical dense benchmark whose settings
collapsed.

**To flip:** opt-in already, and deliberately **not** in `REGIMES` so nothing can
be calibrated on it — a corpus where every event has a neighbour is as
unrepresentative as one where none does.

⚠ **It is a second axis crossing the difficulty axis, not a replacement for it**,
and treating it as a self-contained condition is what went wrong in §4b: the
`regime` argument is required precisely because the recording's answer moves more
with the background than with the crowding it exists to measure.

---

## What is still genuinely open

Not forks — nobody has taken a side.

- **`BENCH_RECORDING` runs flat** while `derive_spec` measures (#2).
- **Why crowding costs 0.14–0.18 of recall** once the background is held right
  (#4b). Two of the three candidates are dead — the scorer and episode merging
  both contribute exactly nothing — and a guard recovers only about a quarter of
  CoactDetect's loss and none of LoCo's. The remedy the primaries prescribe for a
  *multiple-target* environment is **censoring inside the estimator**
  ([`detector_history.md`](detector_history.md) §5.4, §6.4), which §5.5 wants
  tried on LoCo anyway for the 17× cost. Nobody has run it.
- **The detectors are steeply background-sensitive and nothing measures that
  directly.** On the same 120 crowded events, CoactDetect recalls 0.652 at
  `baseline_quiet` and 0.460 at `baseline_busy` — a 3.7-fold rate change costing
  0.19 of recall, and 0.40 at the 0.18 participation level. Operating points are
  chosen at one point on that axis and quoted as though they held across it.
  Adjacent to #2 and to the re-fit, but not the same question.
