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

**This adopts nothing.** No bench constant moves here. The adoption PR the brief asks for
is deliberately **not opened yet** — see *Why the adoption PR is not here*.

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

## The calibration is not uniform, and that bounds the rest (Figure 1, Panel A)

`passed` is decided on the coordinated-share error alone, against ±0.25.

| stream | model | 1 s | 2 s | 4 s |
|---|---|---|---|---|
| fast | fixed | **+0.060** | +0.457 ✗ | +0.998 ✗ |
| fast | binomial | **+0.248** | +0.731 ✗ | +1.231 ✗ |
| slow | fixed | **−0.137** | −0.063 | +0.107 |
| slow | binomial | **−0.097** | −0.019 | +0.165 |

**Slow clears every window. Fast clears only the 1 s window**, missing by +0.46 at 2 s and
+1.00 at 4 s; its binomial case at 1 s clears by 0.002. The fast numbers hold at exactly the
window they were measured at, with no margin either side. The direction is mechanical — a
wider window dilutes brief fast coincidences with independent firing, while slow events are
long enough that a wider window catches more of them.

⚠ **Two error terms `passed` does not look at.** On `slow fixed@1.0` the participants read
+11.8% and the moment rate −22.8%, while the share they multiply to reads −13.7%. Errors in
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
  −22.8% — and its probe carries a −35.9% coordination correction, the largest anywhere in
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

## Why the adoption PR is not here

The brief's step 2 says to open it **rebased on WSMIP065's constants PR**. That PR is
[#738](https://github.com/syncytium2/bugarach/pull/738) and it is **still a draft** — `main`
still carries `jitter_sec` 0.36 s fast and 0.30 s slow and `participation` 0.18. Opening an
adoption PR now would either conflict with it in `bench.py` or silently reorder two changes
meant to land in sequence, and this session's board block says the constants are WSMIP065's
tonight.

When #738 lands, quiet and busy are the straightforward rows — a 13% to 22% subtraction, on
rates that otherwise reproduce the bench. **The fast probe is the one that deserves a
sentence from Tony**, because +112% is not a correction, it is a different definition of
what "busy" means for a probe.
