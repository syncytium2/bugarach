# The estimator travels on slow and not on fast, and the probe change is a definition, not a measurement

Run 2026-09-22 on WSMIP064, the overnight brief's WSMIP064 step 2.
**Working material, not murderboarded** — same standing as the other run records here.

**Dataset:** `2026-09-17_revised_2v_long_STEPS_AND_PINS_EXCLUDED`, 84 recordings,
**confirmed by Tony in this session** in his own words before anything read it.
**Tool:** `tools/measure_coordination_rates.py` ([#737](https://github.com/syncytium2/bugarach/pull/737)).
**Figure:** `tools/make_coordination_rates_figure.py` → `coordination_rates.png` / `.html`.
**Record:** `coordination_rates.json` — every stream, every window, per recording.
Baseline analysis windows only (FOUNDATIONS §9), `t50rise` onsets, 20 surrogate draws
per recording, 2,582 five-minute stretches.

**This adopts nothing.** No bench constant moves here. The adoption PR the brief asks for
is deliberately **not opened yet** — see *Why the adoption PR is not here* below.

## What was measured

Factorial cumulants of the population count in a sliding window: cells firing
independently at constant rates contribute exactly zero to both the pair and triple
terms, whatever their rates, so only shared firing adds. Pairs and triples fix the
**coordinated share** — the part of a cell's own rate belonging to moments shared with
other cells — without anyone deciding which onsets form an event. Slow shared drift also
adds to both terms, so each recording is compared with per-cell circular-shift surrogates
and the surrogate's cumulants subtracted.

Two models bracket how many cells join a moment, because pairs and triples fix the
spread and not the mean: **fixed** (every moment the same size) and **binomial** (each
cell joins independently).

## The calibration is not uniform, and that governs everything else (Figure 1, Panel A)

The same estimator runs on each bench's simulated recordings, where the planted
participants are known. The tool's `passed` flag is decided on the **coordinated share**
alone, against a ±0.25 median relative error tolerance.

| stream | model | 1 s | 2 s | 4 s |
|---|---|---|---|---|
| fast | fixed | **+0.060** | +0.457 ✗ | +0.998 ✗ |
| fast | binomial | **+0.248** | +0.731 ✗ | +1.231 ✗ |
| slow | fixed | **−0.137** | −0.063 | +0.107 |
| slow | binomial | **−0.097** | −0.019 | +0.165 |

**Slow clears the tolerance at every window. Fast clears only the 1 s window**, and
misses by +0.46 at its 2 s neighbour and +1.00 at 4 s. Fast's binomial case at 1 s clears
by 0.002 — it passes, with no margin worth the word.

So the two streams are not equally supported. The fast numbers hold at exactly the window
they were measured at and nowhere either side of it; the slow numbers travel. The
direction makes mechanical sense — a wider window dilutes brief fast coincidences with
independent firing, while slow events are long enough that a wider window catches more of
them — but the consequence for adoption is the point.

⚠ **Two error terms the `passed` flag does not look at.** On `slow fixed@1.0` the
participants are over-estimated by +11.8% and the moment rate under-estimated by −22.8%,
while the share they multiply to reads −13.7%. Errors in opposite directions flatter their
product, and the gated quantity is the product. Anything read off *participants* or
*moments per minute* separately carries the larger error, not the gated one.

## What adoption would move (Figure 1, Panel B)

Per-cell rates in Hz, at the 1 s window, fixed model. **Background** is the raw rate minus
the coordinated share — like for like with what `tools/remeasure_bench.py` measures.

| stream | level | bench today | measured background | change |
|---|---|---|---|---|
| fast | quiet | 0.0052 | 0.00337 | −35% |
| fast | busy | 0.0190 | 0.01641 | −14% |
| fast | probe | 0.0600 | 0.12708 | **+112%** |
| slow | quiet | 0.0030 | 0.00208 | −31% |
| slow | busy | 0.0113 | 0.00816 | −28% |
| slow | probe | 0.0320 | 0.02906 | −9% |

**The two streams' probes move for opposite reasons**, and the first draft of this record
got it wrong by asserting one reason for both. Going from the raw rate to the background
one costs:

| stream | quiet | busy | probe |
|---|---|---|---|
| fast | −7.2% | −11.8% | **−0.6%** |
| slow | −11.5% | −25.4% | **−35.9%** |
| combined | −7.9% | −16.8% | −0.3% |

**Fast's busiest stretches are not its coordinated ones.** Its probe correction is
essentially nil, so fast's +112% is purely a change of *definition* — a measured 99th
percentile of 300-second stretches in place of a chosen multiple of the median.

**Slow's busiest stretches are its coordinated ones**, so more than a third of its probe
is the correction, and its small net −9% is two large opposite moves cancelling: the raw
99th percentile is 0.0453 Hz, well above the bench's 0.032, and the correction pulls it
back under. ⚠ **That 36% is the number to check before anything rests on it**, because
slow is also the stream whose ungated calibration terms are weakest — its moment rate
reads −22.8%.

Worth knowing before ruling: the bench's **current** `hot_rate_hz` sits at the **96.2nd**
percentile on fast and the **96.1st** on slow — strikingly consistent, and not a wild
value. Going to the 99th is a deliberate move up the same distribution.

**For quiet and busy the calibration weakness barely matters**, which is the reassuring
part: the corrections there are 7% to 25% of the rate, and an error of even half the
share moves them by a few percent. Quiet and busy are the safe rows in the table above.

## Report only, per the brief's table

Not adoptable tonight, and not because they look wrong:

| stream | model | participants per moment | participation | shared moments per min |
|---|---|---|---|---|
| fast | fixed | 10.6 cells | 0.335 | 0.031 |
| fast | binomial | 7.4 cells | 0.233 | 0.079 |
| slow | fixed | 25.7 cells | 0.816 | 0.0034 |
| slow | binomial | 18.4 cells | 0.583 | 0.0077 |
| combined | fixed | 25.8 cells | 0.819 | 0.015 |
| combined | binomial | 18.7 cells | 0.594 | 0.029 |

These are **not** the bench's participation and must not be read as correcting it. The
bench plants a fixed participant count at three levels with a 120-second spacing floor;
this is a per-cell join probability over *all* shared moments, including ones joined by
one or two cells. Adopting it means restructuring how events are planted, which is a
decision and not a substitution — the brief says so, and it is right.

Two observations worth carrying anyway. **Slow's measured participation (0.58–0.82) sits
far above the slow bench's 0.38**, which ruling-queue item 3 calls the value the whole
slow bench turns on — so that ruling has a number pointing at it now, even though this one
cannot replace it. And **combined is slow, not a mixture**: 25.8 participants against
slow's 25.7 and fast's 10.6, because the merge is dominated by the stream with the larger
moments. Combined is **uncalibrated** — there is no combined bench — and its merge rule
(a slow onset within one frame of a fast onset counts once) is a stated assumption, not
goal 4's answer.

## Why the adoption PR is not here

The brief's step 2 says to open it **rebased on WSMIP065's constants PR**. That PR is
[#738](https://github.com/syncytium2/bugarach/pull/738) and it is **still a draft** —
`main` still carries `jitter_sec` 0.36 s fast and 0.30 s slow and `participation` 0.18.
Opening an adoption PR now would either conflict with it in `bench.py` or silently
reorder two changes that were meant to land in sequence, and this session's board block
says the constants are WSMIP065's tonight.

So the measurement is landed and the adoption waits on #738. When it lands, the quiet and
busy rows above are the straightforward part; **the fast probe is the one that deserves a
sentence from Tony**, because +112% is not a correction, it is a different definition of
what "busy" means for a probe.
