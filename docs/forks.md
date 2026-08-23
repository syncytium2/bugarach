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

### 4a · Measured on `loco` and `coact`, 2026-08-23 — the prediction did **not** hold

Two earlier versions of this section said it did. Both compared **between**
recordings, and neither could tell masking relief from a bar that moved. With an
internal control, it is the bar.

`tools/probe_guard_on_surrogates.py`, 8 seeds, shipped operating points,
`baseline_quiet`. `CROWDED_RECORDING` (#10) runs three hours so that **38%** of its
events have a neighbour inside their own ±30 s reference window and **31%** have
nothing within 60 s. Recall is per-event, so splitting it by each event's own
nearest-neighbour gap holds count, duration, background and false-alarm
opportunity fixed by construction — one recording, two populations.

**Crowding costs recall, and this is the first clean measurement of it:**

| detector | 15–30 s gap | 30–60 s | 60 s+ (control) | cost of a neighbour |
|---|---|---|---|---|
| CoactDetect | 0.711 | 0.882 | 0.855 | **−0.144** |
| LoCo | 0.602 | 0.659 | 0.706 | **−0.104** |

**The guard does not fix it.** Its recall gain is *flat across the gap* — where
there is no neighbour to unmask, it helps just as much:

| CoactDetect, guard 5 s | 15–30 s | 30–60 s | 60 s+ (control) |
|---|---|---|---|
| Δ recall | +0.045 | +0.049 | **+0.046** |

LoCo's is worse than flat: +0.014 crowded against **+0.025** isolated, and at a
20 s guard +0.025 against **+0.064**. The guard helps the events it cannot
possibly be unmasking *more* than the ones it can.

**What it is actually doing is lowering the bar**, and precision pays for it:
CoactDetect 0.889 → 0.867, LoCo 0.992 → 0.985. Excising a span shrinks the null
pool, and a fixed 99.9th percentile of a smaller sample underestimates the tail —
so every anchor gets an easier threshold, crowded or not.

**A second, independent confirmation, in the place where the effect can only be an
artifact.** On the sparse bench, where a second planted event can never enter the
context, 8 seeds show the guard raising recall monotonically anyway — CoactDetect
0.833 → 0.875, LoCo 0.683 → 0.733. §4a's first version called this *"−0.021 to
+0.021 with no direction, the null result the geometry demands"*, on 4 seeds. It
is not null. It is the same bar-lowering, measured where nothing can be masked.

**What survives.** LoCo's geometry argument still stands and now explains more than
it did: its halves are *already one-sided* — the anchor is a boundary of each half,
not its centre — so it was partly guarded all along, which is why its guard needed
no compaction while CoactDetect's did. And the guard is not useless: it is a
threshold knob that happens to be spelled in seconds. It is just not the
guard-cell mechanism, and calling it one would put a wrong reason in front of a
real number.

**What to do instead** is §4b's last paragraph: censoring inside the estimator,
which removes the largest reference cells wherever they sit rather than a span
next to the anchor.

⚠ **Do not compare F1 or recall between the two recordings.** The crowded one
plants eight times as many events, so precision rises on density alone and
CoactDetect reads a *higher* F1 crowded than on the bench. Matching the count by
lengthening the sparse side does not rescue the comparison either — false-alarm
opportunity scales with duration, and the bench's own 15 events over 6 h hold
recall at 0.85 while precision falls 0.633 → 0.250. **Crowding is events per unit
time, so no two recordings can differ in it and match on both count and
duration.** The within-recording split is not a nicety; it is the only version of
this measurement that is not confounded.

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
mattered. CoactDetect recall on the same 120 events, `tools/probe_crowded_background.py`:

| background | bg Hz/ROI | recall | 0.30 | 0.18 | 0.10 |
|---|---|---|---|---|---|
| crowded, `baseline_quiet` | 0.0052 | **0.817** | 1.00 | 0.94 | 0.51 |
| crowded, `baseline_busy` | 0.0189 | 0.560 | 0.98 | 0.62 | 0.08 |
| crowded, off-axis (pre-fix, 45 min) | 0.0505 | 0.254 | 0.64 | 0.11 | 0.01 |

A 3.7-fold background change — the interquartile spread of untreated slices, not
an extreme — costs 0.26 of recall and 0.32 at the measured real participation.
That is a bigger effect than crowding, and it is the axis every operating point is
chosen on one point of.

**Two of the three candidates §4a named are dead, and should not be re-opened.**
An oracle emitting the exact planted times scores **F1 1.000** on the crowded
recording, and across every condition **zero** emitted spans cover two planted
events — so neither the greedy one-to-one matching in `score_detections` nor
episode merging contributes anything. Spans are 2.0 s (coact) and 0.70 s (loco),
far under any gap that matters. Where the detectors do lose recall they lose it by
**going silent** — precision *rises* while the detection count falls — which is a
bar that went up.

**The third candidate is real, and a guard is the wrong instrument for it.**
§4a measures the cost of a neighbour at 0.144 (CoactDetect) and 0.104 (LoCo) with
an internal control, and shows the guard's gain is flat across the gap: it lowers
the bar everywhere rather than unmasking anything. A guard excises a span
*adjacent to the anchor*, but interference is spread across the whole ±30 s
reference. That is the **multiple-target** case, and
[`detector_history.md`](detector_history.md) §5.4 and §6.4 prescribe **censoring
inside the estimator** for it — trimming the largest reference cells wherever they
sit — which §5.5 wants tried on LoCo anyway, for the 17× cost. Same experiment,
two payoffs, and now a control that can tell whether it worked.

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
be calibrated on it — a corpus assembled to hold crowded and isolated events in
useful proportions is not a corpus anything resembles.

⚠ **It is a second axis crossing the difficulty axis, not a replacement for it**,
and treating it as a self-contained condition is what went wrong in §4b: the
`regime` argument is required precisely because the recording's answer moves more
with the background than with the crowding it exists to measure.

**It runs three hours, and the length is the design.** Tony, 2026-08-23:
*"shouldn't the two tests have the same number of events so F1 can be compared.
who cares how long the recording has to be?"* The first version planted the same
120 events in 45 minutes, which crowded **every** one of them — so it had no
uncontaminated group and the only comparison available was against a different
recording. That comparison cannot be rescued: matching the count means changing
the duration, and false-alarm opportunity scales with duration, so precision
moves for a reason unrelated to crowding. **Crowding is events per unit time —
no two recordings can differ in it and match on both count and duration.** Three
hours puts both populations in *one* recording (38% crowded, 31% isolated), and
`nearest_neighbour_gaps` splits recall between them with everything else fixed by
construction. That contrast is what showed the guard was not doing what §4a
thought (§4a), and it is the instrument for whatever replaces it.

---

## What is still genuinely open

Not forks — nobody has taken a side.

- **`BENCH_RECORDING` runs flat** while `derive_spec` measures (#2).
- **Nothing yet fixes the cost of a neighbour**, which §4a now measures cleanly at
  **0.144** (CoactDetect) and **0.104** (LoCo). Three candidates were named; the
  scorer and episode merging contribute exactly nothing, and the guard turns out
  to lower the bar everywhere rather than unmask anything. The remedy the
  primaries prescribe for a *multiple-target* environment is **censoring inside
  the estimator** ([`detector_history.md`](detector_history.md) §5.4, §6.4), which
  §5.5 wants tried on LoCo anyway for the 17× cost. Nobody has run it — and the
  within-recording split now makes it checkable, because censoring that works
  shows a gain **concentrated in the crowded band**, which is exactly what the
  guard failed to show.
- **The detectors are steeply background-sensitive and nothing measures that
  directly.** On the same 120 events, CoactDetect recalls 0.817 at
  `baseline_quiet` and 0.560 at `baseline_busy` — a 3.7-fold rate change, the
  interquartile spread of untreated slices rather than anything extreme, costing
  **0.26** of recall and **0.32** at the measured real participation. That is a
  larger effect than crowding, and operating points are chosen at one point on
  that axis and quoted as though they held across it. Adjacent to #2 and to the
  re-fit, but not the same question.
- **`guard_sec` is now a threshold knob spelled in seconds**, and nothing says so
  where a caller would look. It is inert at its default and the parity tests pin
  that, so nothing is broken — but a reader of the signature would reasonably
  expect a guard-cell mechanism. Either document it as what it measurably is, or
  find the reason the shrunken null pool biases the percentile and fix that
  instead, which would make the guard mean what it says.
