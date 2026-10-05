# The rates reproduce the bench; what adoption would change is the coordination subtraction alone

Run 2026-09-22 on WSMIP064, the overnight brief's WSMIP064 step 2.
**Working material, not murderboarded** — same standing as the other run records here.

**Dataset:** `2026-09-17_revised_2v_long_STEPS_AND_PINS_EXCLUDED`, 84 recordings,
**confirmed by Tony in this session** in his own words before anything read it.
**Tool:** `tools/measure_coordination_rates.py` ([#737](https://github.com/syncytium2/bugarach/pull/737)),
with the recording-set correction below.
**Figure:** `tools/make_coordination_rates_figure.py` → `coordination_rates.png` / `.html`.
**Record:** `coordination_rates.json` — every stream, every window, per recording.
20 surrogate draws per recording, 2,582 five-minute stretches.

**Adopted 2026-09-22**, in the same change that lands this record: Tony ruled **background,
end to end** (~21:45 EDT), so `bench.REGIMES` quiet/busy, `bench_slow.REGIMES`, and both
`hot_rate_hz` probes take the background values below. Each constant's docstring carries its
own provenance and points back here.

## Baseline only, and the count that shows it

Every measurement is on each recording's **baseline analysis window**
(`assess_folder.generation_window`, with `bench.MIN_BASELINE_SEC` as a floor). A recording
with no declared baseline region returns `window=None` — the whole-recording fallback — and
this tool **drops it rather than measuring it** (`_real`: `if w is None … return None`).
So no whole-recording window enters any number here, and no treatment window does either
(FOUNDATIONS §9). All **84** recordings of the default export cleared that test and
contributed.

## The correction that changed the answer

The first run of this step measured quiet and busy over **all 84** recordings and compared
them against `bench.REGIMES`. That is not like for like. `tools/remeasure_bench.py` — which
is where `bench.REGIMES` came from — takes its 25th/75th percentiles over
`[r for r in recs if r["shape_usable"]]`, the recordings clearing
`fit_background_shape`'s floors (≥ 300 s, ≥ 20 events, ≥ 5 ROIs).

The floors cut short, sparse and few-ROI windows, which are the **quiet tail** — so the
mismatch shows up almost entirely in quiet and barely in busy. That is exactly the shape
the first run reported, and it read as a measurement:

| | fast quiet | fast busy | slow quiet | slow busy |
|---|---|---|---|---|
| all 84 recordings, vs bench | **−30.2%** | −2.1% | **−21.5%** | −3.2% |
| the bench's own set, vs bench | **−3.0%** | +0.2% | **+0.6%** | +0.3% |

**On the bench's own recording set the raw rates reproduce `bench.REGIMES` to within 3%.**
80 of 84 recordings clear the floors on fast, 75 on slow, 81 on combined. The tool now
reports quiet and busy on that set and keeps the all-recordings pair beside it as
`*_all_recordings`; `tests/test_measure_coordination_rates.py` pins both, and imports the
floors rather than copying them so they cannot drift.

The coordination numbers are untouched by this — the coordinated share reproduces
bit-identically across the two runs, because the filter only ever moved which recordings
enter a percentile.

## What adoption would actually move (Figure 1, Panel B)

Per-cell rates in Hz, 1 s window, fixed model. **Background** is the raw rate minus the
coordinated share.

| stream | level | bench today | raw (bench's set) | background | raw → background |
|---|---|---|---|---|---|
| fast | quiet | 0.0052 | 0.00505 | 0.00422 | −16.5% |
| fast | busy | 0.0190 | 0.01904 | 0.01645 | −13.6% |
| fast | probe | 0.0600 | 0.12781 | 0.12708 | −0.6% |
| slow | quiet | 0.0030 | 0.00302 | 0.00245 | −19.0% |
| slow | busy | 0.0113 | 0.01133 | 0.00886 | −21.8% |
| slow | probe | 0.0320 | 0.04531 | 0.02906 | −35.9% |

**Because the raw column reproduces the bench, the whole of the proposed quiet/busy change
is the coordination subtraction: 13% to 22% on both streams.** That is a cleaner claim than
the first run's, and a smaller one.

**The probes split, and for opposite reasons.** Fast's coordination correction at the probe
is −0.6% against −16.5% at quiet, so its busiest stretches are not its coordinated ones and
its **+112%** is purely a change of *definition* — a measured 99th percentile of 300-second
stretches in place of a chosen multiple of the median. Slow's is −35.9%: its busiest
stretches *are* its coordinated ones, and its small net −9% against the bench is two large
opposite moves cancelling (raw 0.0453 is well above the bench's 0.032; the correction pulls
it under). ⚠ **That 36% is the number to check before anything rests on it**, slow being the
stream whose ungated calibration terms are weakest.

Worth having before ruling: the bench's **current** `hot_rate_hz` sits at the **96.2nd**
percentile on fast and the **96.1st** on slow — consistent, and not a wild value. Going to
the 99th is a deliberate step up the same distribution.

## The calibration passes everywhere — once the probe stretch is out of it (Figure 1, Panel A)

`passed` is decided on the coordinated-share error alone, against ±0.25. **All twelve cells
clear it**, both streams, both models, all three windows:

| stream | model | 1 s | 2 s | 4 s |
|---|---|---|---|---|
| fast | fixed | **−0.166** | −0.140 | −0.115 |
| fast | binomial | **−0.047** | −0.022 | +0.005 |
| slow | fixed | **−0.171** | −0.132 | −0.114 |
| slow | binomial | **−0.134** | −0.095 | −0.078 |

**An earlier version of this record said fast cleared only the 1 s window, missing by +0.46
at 2 s and +1.00 at 4 s. That was the probe stretch, not the estimator**, and it is worth
setting out because the finding underneath is about what this statistic can and cannot see.

When the probe moved to the measured 99th percentile, the fast calibration went from passing
to failing by 1.7× the tolerance. Isolating it on the fast bench, fixed model, 1 s window:

| configuration | share error | |
|---|---|---|
| old backgrounds + old 0.06 Hz probe | +0.060 | pass |
| new backgrounds + old 0.06 Hz probe | +0.025 | pass |
| new backgrounds + new 0.1271 Hz probe | **+0.433** | **fail** (moment rate +0.386) |
| new backgrounds + no probe stretch | −0.166 | pass |

**The backgrounds were never implicated; the probe alone moves it.** The mechanism is a limit
of the measuring tool. In the probe window every cell lifts to 0.1271 Hz across the same
300 s, and a joint rise in rate is indistinguishable from many shared moments to a statistic
built on factorial cumulants of the population count. The surrogates cannot remove it either:
per-cell circular shifts move each train independently, so they break the joint rise up
rather than preserving it as the null.

So the probe stretch made the calibration measure the estimator's response to a correlated
rate change, which is not the question it exists to ask. It is now excluded
(`measure_coordination_rates.CAL_NO_PROBE`), and the backgrounds it validates were measured
and calibrated before the probe ever moved.

⚠ **What that admits, and it belongs beside the adopted numbers.** The same effect runs on
real recordings: a baseline window containing a stretch where the whole field is busier will
have part of that rise counted as coordination and subtracted, so the background rates may be
**slightly over-subtracted**. The measured probe bounds it — the coordinated share at the
fast probe is 0.6% of the rate, so on fast the effect is small. **On slow the share at the
probe is 35.9%**, which is not obviously small, and is the first thing to re-check if the
slow bench behaves oddly.

⚠ **Two error terms `passed` does not look at.** On `slow fixed@1.0` the participants read
+14.2% and the moment rate −27.4%, while the share they multiply to reads −17.1%. Errors in
opposite directions flatter their product, and the product is the gated quantity. Anything
read off *participants* or *moments per minute* separately carries the larger error.

## Report only, per the brief's table

| stream | model | participants per moment | participation | shared moments per min |
|---|---|---|---|---|
| fast | fixed | 10.6 cells | 0.335 | 0.031 |
| fast | binomial | 7.4 cells | 0.233 | 0.079 |
| slow | fixed | 25.7 cells | 0.816 | 0.0034 |
| slow | binomial | 18.4 cells | 0.583 | 0.0077 |
| combined | fixed | 25.8 cells | 0.819 | 0.015 |
| combined | binomial | 18.7 cells | 0.594 | 0.029 |

These are **not** the bench's participation and must not be read as correcting it. The bench
plants a fixed participant count at three levels with a 120-second spacing floor; this is a
per-cell join probability over *all* shared moments, including ones joined by one or two
cells. Adopting it means restructuring how events are planted — a decision, not a
substitution.

Two observations worth carrying. **Slow's measured participation (0.58–0.82) sits far above
the slow bench's 0.38**, which ruling-queue item 3 calls the value the whole slow bench turns
on — so that ruling has a number pointing at it, even though this one cannot replace it. And
**combined is slow, not a mixture**: 25.8 participants against slow's 25.7 and fast's 10.6,
because the merge is dominated by the stream with the larger moments. Combined is
**uncalibrated** — there is no combined bench — and its merge rule (a slow onset within one
frame of a fast onset counts once) is a stated assumption, not goal 4's answer.

## Slow is the stream where least is settled, and three runs now say so

Worth reading beside this one, because two of the three landed the same night and none
pointed at the others:

- **This run.** Slow's ungated calibration terms are the weakest — its moment rate reads
  −27.4% — and its probe carries a −35.9% coordination correction, the largest anywhere in
  the table.
- **[The correlogram by group](../2026-09-22-jitter-by-group/README.md)** (#744). Fast shows
  no group difference in onset jitter (p = 0.71); **slow is borderline at p = 0.054**, with
  one of six pairwise intervals excluding zero and nothing correcting for the six.
- **[The slow pilot](../2026-09-21-slow-pilot/README.md)** and ruling-queue item 3, which
  calls slow's participation of 0.38 the value that whole bench turns on — against the
  0.58–0.82 measured here for a related but different quantity.

None of these is fatal on its own and none adjudicates anything. Together they say the slow
stream's constants are the ones to be slowest about, which is a reason to sequence rather
than a reason to stop.

## What was adopted, and what the guard now checks

Landed with this record, on top of [#738](https://github.com/syncytium2/bugarach/pull/738):

| constant | was | now |
|---|---|---|
| `bench.REGIMES` quiet / busy | 0.0052 / 0.0190 | **0.0042 / 0.0165** |
| `bench.BENCH_RECORDING["hot_rate_hz"]` | 0.06 | **0.1271** |
| `bench_slow.REGIMES` quiet / busy | 0.0030 / 0.0113 | **0.0024 / 0.0089** |
| `bench_slow.BENCH_RECORDING["hot_rate_hz"]` | 0.032 | **0.0291** |

**The measured-record guard had to learn the new quantity, or it would have been
permanently wrong.** `tests/test_bench_is_measured_on_the_declared_folder.py` compares the
bench against `tools/remeasure_bench.py`'s measurement, and that tool measures the *total*
rate — so a bench holding background rates would have failed the check for as long as it
stood. `remeasure_bench` now reads **each recording's** coordinated share from this run's
record and subtracts it before taking the regime percentiles, exactly as it already reads
`jitter_sec` from the correlogram record, and refuses a record measured on another folder
for the same reason. `tools/measure_slow_bench.py` reuses that code and inherits it.

Per recording rather than pooled, deliberately: a pooled share would shift every bootstrap
draw by the same constant, and an interval that cannot move with the resampling is an
interval that cannot fail. On the re-measure both regimes land inside their intervals —
fast quiet 0.0042 in [0.0026, 0.0059], fast busy 0.0165 in [0.0141, 0.0223].

**What is still not adopted:** the operating points. The re-searches propose settings on the
new bench; adopting any of them stays Tony's, as it was for the slow reference. Event
frequency and participation remain report-only for the reason the brief gives.

## ⚠ Two published findings reversed, and they are for Tony

Moving `REGIMES` down re-anchors the **difficulty axis**, and `BACKGROUND_GRID` moved with
it (the two endpoints must be on the grid, and a test enforces that). Re-measuring the
background curve at twelve seeds on the new axis reverses two claims
`tests/test_background_curve.py` had pinned. They are **restated as measured, not
re-baselined**: no tolerance was loosened, nothing was skipped, and each restated test now
asserts the mechanism so it cannot pass for an unrelated reason.

**1. No detector is a steady leader across the whole axis any more.** Three now win
somewhere on the grid — CoactDetect at the quiet end, LoCo through the middle, SPIKE-synch
at the busy end. The leader *does* still hold between the two named `REGIMES` endpoints,
which is where this project reports, so the claim that survives is the narrower one.

**2. The fitted-versus-flat contrast is gone.** That file is named for it: the fitted field
was the stable one and the flat field the one that reordered. On the background axis both
show the **same** flat set (`{sync}`), the **same** three winners and the **same** largest
rank change. What still separates them is magnitude — mean own-range **0.126** fitted
against **0.171** flat — so the fitted axis is about a quarter shorter and has not gone
dead. That is the 2026-08-28 handoff's reading (a), and only it is still asserted.

**Both follow from one fact already ruled a result rather than a defect** (#738,
ruling 6): SPIKE-synch went flat when the measured jitter was adopted, and **a flat
detector on a declining axis eventually overtakes the ones that decline**. Nothing
collapses down the table — the mover is the detector that does not move. It goes fourth at
2.1 mHz to **first at 25 mHz**, 0.665 against LoCo's 0.657 and CoactDetect's 0.633.

| | fitted | flat |
|---|---|---|
| flat set | `{sync}` | `{sync}` |
| winners along the axis | coact, loco, sync | coact, loco, sync |
| largest rank change | 4 (sync, rising) | 4 (sync, rising) |
| steady leaders | none | none |
| mean own-range | **0.126** | **0.171** |

**What this does not settle.** Whether a bench whose busy end is won by a detector that
cannot see the axis is the bench the searches should run on. It is a coherent result and it
may be the right one — a flat detector *should* win where the others have degraded — but it
changes what "best detector" means at the busy end, and WSMIP065's fast and slow searches
run on exactly this axis.
