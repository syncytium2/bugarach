---
status: open
filed: 2026-08-29
---

# Throughput is not the real-time question. Lookahead is, and nothing measures it

> **Not murderboarded** — a planning note for sessions in this tree. Every number is
> quoted from a named file or run. **If any of it reaches an outside reader,
> murderboard that artifact first.**

Tony, 2026-08-29: *"Real time performance. What if we simulate a real time data
stream?"* — then, on being shown the throughput figures: *"How machine dependent is
that. What if it's run on a phone?"*

Both questions land, and together they point away from the experiment they started
from.

## Throughput is already measured, and it is not a differentiator

`fair_bakeoff.py` records `detect_x_realtime` per fold. From the 2026-08-29 screen,
5 seeds × 4 folds, on `macOS-26.6.2-arm64` (the JSON records the machine — that field
is why this paragraph can be written at all):

| detector | × real time |
|---|---|
| rate | 1,505,586 |
| tube / tube_guard | ~340,000 |
| coact | 113,388 |
| **loco (slowest)** | **28,749** |

**The slowest detector is 28,749× faster than real time.** For that to fail on a
phone, the phone would have to be roughly 29,000× slower than an M-series Mac; phones
are 2–10× slower. The conclusion survives four orders of magnitude of hardware
variation, so simulating a stream to measure speed would produce a table in which
every row says "yes, trivially".

**But the honest gap Tony's second question exposes:** those are the **Python**
implementations. A phone runs the **browser** build, which is hand-written JS ports of
the six — a different implementation whose speed nobody has measured, and which must
not be assumed from the Python. And the tube has **no browser implementation at all**,
for inference or training, so on a phone today a visitor gets six hand-written
detectors and not the learned one.

## Lookahead is the real constraint, and it is machine-INDEPENDENT

Throughput is a property of the machine. **Lookahead is a property of the algorithm** —
12.8 s of required future is 12.8 s on a Mac, a phone, or a cluster. That is what makes
it worth measuring and worth publishing.

Read off the code rather than assumed:

- **tube** — `_kernels` builds `t = arange(-k, k+1)`, a **symmetric** kernel, convolved
  with `padding=self.k`, where `k = max_center_frames = 128`. At dt=0.1 s the response
  at time *t* depends on data up to **12.8 s after t**. The `max_pool1d` widening adds
  a little more. The tube cannot emit a call until that future has arrived.
- **binned SCE** — its threshold is a percentile over surrogates of the whole window,
  so it has no output at all until it has seen the window.
- **rate+context** — depends on whether its context window trails or is centred; not
  checked.
- **LoCo, CoactDetect** — local, and may be genuinely causal. Not checked.

## The experiment is a prefix test, not a streaming harness

Run each detector on the full recording, then on truncations, and ask whether the call
at time *t* changes when data after *t* is added. **The point at which calls stop
changing is the lookahead, measured rather than asserted.** No new simulator, no new
data, no streaming infrastructure — a loop over recordings that already exist.

Do that before building anything, because it is cheap and it may show that some
detectors are already causal, which changes what the rest of this is worth.

## Then the result worth putting in front of a reviewer

**The tube's lookahead is a design parameter.** Shrink `max_center_frames`, retrain,
and score: that is a **latency-versus-F1 curve** — what does online operation cost in
accuracy? At 5.6 s a fit it is an afternoon of compute.

It is also the one axis on which the tube might genuinely win. It currently ties
CoactDetect on F1 (0.662 vs 0.660) and loses badly on promiscuity (38.1 probe firings
against 2.25). If it degrades gracefully as its window shrinks while the
surrogate-thresholded detectors fall apart — SCE cannot produce anything without its
window — that is an advantage nobody in this project has looked for. Closed-loop
optogenetics is a real application and it is gated by lookahead, not by compute.

## A cheap honesty feature that falls out of this

The published page **already times itself** — `performance.now()` around the fit and
detect paths, and it reports elapsed seconds to the reader. A "how fast is this on
**your** device" line is instrumentation that exists, surfaced. It answers Tony's phone
question the right way round: the visitor measures their own machine instead of
trusting a number measured on ours.

## What NOT to do

- **Do not build a streaming harness to measure speed.** The margin is four orders of
  magnitude; the answer is known.
- **Do not quote a real-time factor without its machine.** The bake-off JSON records
  `platform` and `python` for exactly this reason. A bare "×N faster than real time" is
  a number with its provenance stripped off.
- **Do not infer the browser's speed from the Python's.** Different implementation,
  unmeasured, and the learned detector is not in it.
