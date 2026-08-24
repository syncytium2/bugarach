---
status: open
filed: 2026-08-23
---

# Four tubes, and what each one would have to show to be believed

> **Not murderboarded** — a planning note for sessions in this tree, same standing as
> [`the revision plan`](2026-08-22-the-revision-plan-mechanism-before-calibration.md)
> it extends. Every number is quoted from a named file. **If any of it reaches an
> outside reader, murderboard that artifact first.**

**Why this file exists.** The radar reading produced a fix for the learned model, and
then the evidence for that fix moved twice while several sessions were reading it. The
guard interval landed on the two surrogate detectors under the message *"the prediction
held"*; two commits later it landed again as *"the guard is not doing what we thought"*.
Both are on `main`, in that order, and a session that reads the first and stops has the
opposite of the current finding. So the four candidates are written down once, with what
is actually known about each, and the two rules that decide which of them is believed.

**Nothing here has been run on the tube.** `tools/` holds probes for the rate mechanism,
the guard against event spacing, the guard on the surrogate detectors and the crowded
background; for the learned model it holds `ablate_tube.py`, which removes components of
the architecture that exists and does not test a changed one. The controlled test the plan
asks for — the tube against a rate step — is Phase 2 work and is unstarted.

## The defect, read off the model rather than inferred

`build_tube` puts both Gaussians on the same axis, `arange(-k, k+1)`, with no offset and
no hole, area-normalises each, and returns their **difference** (condensed from
`src/bugarach/learn/nets.py`, which also clamps both widths):

```python
centre   = exp(-0.5 * (t / c) ** 2);  centre   /= centre.sum()
surround = exp(-0.5 * (t / s) ** 2);  surround /= surround.sum()
return ((centre - surround) * gain)
```

Two consequences, and both are classical results in a network's clothing. The surround is
**maximal exactly at the sample under test**, so the event contributes to the reference
that judges it — no guard, self-masking by construction. And it **subtracts where CFAR
divides**: the area-normalisation makes a flat field integrate to zero, which cancels the
**mean** of a rate change and not its **variance**, so a fixed threshold on a zero-mean
but rate-scaled signal has a false-alarm rate that climbs with background.

The symptom was in `bakeoff.json` before anyone went looking. Firings in the probe block,
which contains nothing planted:

| | mean | sd | range |
|---|---|---|---|
| **tube** | **15.75** | 9.88 | 5–26 |
| LoCo | 2.50 | 1.73 | 1–5 |
| CoactDetect | 1.25 | 0.96 | 0–2 |

Two cautions the argument needs and does not carry. That spread is **63% of the mean over
four folds** — it is a signal, not a number. And the supporting observation that `tiny`
and `trace` fire 0.0 is worth nothing: they score F1 0.125 and 0.131, so they are
near-silent, and a silent detector's clean probe is not evidence of discrimination. The
comparison that survives is against the two rate-**local** hand-written detectors, and it
is still 6× to 13×.

## The four

| | what changes in `_kernels` | evidence today | what it costs |
|---|---|---|---|
| **V0 · shipped** | nothing — centre − surround, unguarded | F1 **0.668 ± 0.061**, 1,149 params, 5.6 s to fit, 0.014 s to scan a fold | the baseline everything else is read against |
| **V1 · guarded surround** | zero the surround inside ±g, renormalise | **untested here; failed on all three detectors it was tried on, for two reasons neither of which transfers** | one parameter, one line |
| **V2 · ratio of Gaussians** | centre ÷ surround instead of centre − surround | **the only mechanism change measured to work anywhere in this repo** | rewrites the docstring's central claim; a clamp that can silently do the work |
| **V3 · censored surround** | order statistic over the surround support, largest samples dropped | the remedy the primaries prescribe for this environment; **nobody has run it on anything** | the property the tube actually wins on |

### V1 · a surround with a hole

The guard-cell analogue: the reference stops abutting the thing it judges.

**It failed everywhere it has been measured, and the two failures have different
mechanisms.** On `rate` it is a question of scale — at a planted event the 1 s rate is
9.00 Hz against a 60 s context of 0.283 Hz, so a 10 s guard halves the context and moves
the threshold crossing by 0.143 Hz against a 2–5 Hz bar; swept from 120 s spacing down to
14 s, F1 moves −0.006 to +0.000. On `loco` and `coact` it is an artifact — the recall gain
is **flat across nearest-neighbour gap** (CoactDetect +0.045 where a neighbour sits 15–30 s
away, **+0.046** where nothing sits within 60 s), it raises recall on the sparse bench
where nothing *can* be masked, and precision pays for it. What it does is shrink the null
pool, and a fixed 99.9th percentile of a smaller sample underestimates the tail.

**Neither reason transfers to the tube, which is why V1 is unsupported rather than
refuted.** The tube has no null pool and no percentile — its threshold is chosen once on
held-out data — so the `loco`/`coact` artifact cannot arise the same way. And whether the
`rate` scale argument applies is an empirical question nobody has asked: it turns on how
large the surround's contribution is at an event relative to the centre's, which is one
forward pass to find out.

### V2 · divide instead of subtract

`θ = α·μ̂` rather than `θ = μ̂ + k`, which is how cell-averaging CFAR holds a false-alarm
rate constant as the background moves.

**This is the one with positive evidence.** On `rate`, `tools/probe_rate_mechanism.py`
over 3 seeds: additive F1 **0.636** with **2.0** probe firings, multiplicative **0.667**
with **0.0**. The promiscuity signature an additive offset was predicted to cause went to
zero — and promiscuity in an empty block is precisely the tube's symptom, six to thirteen
times over.

**What it costs beyond the three lines.** The docstring's load-bearing sentence — *"the
surround subtracts the local level, so a uniform rate change cancels and only excess
survives"*, offered as making rate invariance *"structural rather than learned"* — is a
claim about the area-normalised **difference**, and a ratio would make it true for a
different reason. Rewrite it; do not leave a correct-sounding justification standing over
changed arithmetic.

**The hazard to watch is the denominator.** A surround that approaches zero needs an ε or
a clamp, and a clamp is exactly the kind of knob that can absorb the question it was added
to answer — `model_track.md` already records the existing surround clamp as *"a wart, not
a cause"*. Implementing it as a **difference of logs** avoids the divide and keeps the
operation a convolution, which also keeps the JS trainer's operation list closed.

Note the α grid must be wide. On `rate` the optimum sat at **15–20** and a first grid
topping out at 8 put it on the boundary.

### V3 · censor the surround

Replace the Gaussian-weighted mean over the surround support with a trimmed or
order-statistic estimate: drop the largest reference samples **wherever they sit**, rather
than a span at a fixed position. This is what the primaries prescribe for a
*multiple-target* environment, and this repo's own review reaches for it twice — as the
fix for greatest-of's blind spot, and as the thing that would answer whether the surrogate
pool is an expensive way to compute an order statistic.

**It is the variant that spends what the tube wins on.** The learned model's honest claim
is not accuracy, it is cost — 1,149 parameters, 0.014 s to scan a held-out fold. An order
statistic over a sliding window is not a convolution, so V3 trades the model's cheapest
property for its most-prescribed fix. Differentiability is not the obstacle: `forward`
already routes gradients through `max_pool1d` by argmax, so sorting-based routing has
precedent in the same file.

**The masking it targets is real and measured.** With an internal control, a neighbour
inside the reference window costs CoactDetect **0.144** of recall and LoCo **0.104**.
Nothing currently fixes it.

## Two rules, and they decide more than the variants do

**Read the signature, not the score.** `bench.nearest_neighbour_gaps` splits recall by each
event's own nearest-neighbour gap **within one recording**, holding count, duration,
background and false-alarm opportunity fixed by construction. A change that relieves
masking shows a gain **concentrated in the crowded band and near zero in the control
band**. A gain that is flat across the gap is a threshold shift wearing a mechanism's
clothes — which is what the guard turned out to be, after it had been written up as a
success. Report crowded-band gain **minus** control-band gain. That number, not F1,
decides V1 and V3.

**Seeds before conclusions.** Every learned number in this repo is **one training run per
fold**, and the fold spread is **0.061**. A variant that moves F1 by less than that has
demonstrated nothing, and three of these four are plausible enough to produce a flattering
run by chance. Multi-seed is already item 1 of the model track; for this work it is a
**prerequisite**, not a follow-up.

Two smaller things worth stating so they are not re-derived:

- **The four are not a race.** On `rate` the guard paid only once the bar was
  multiplicative (0.667 → 0.686), because a contaminated reference then *multiplies* into
  the threshold instead of adding a fixed offset. V1 and V2 compose; the honest design is
  a 2×2, with V3 on its own axis.
- **No parity constraint applies.** The tube has no MATLAB original, so fork #1's
  flag-defaulting-to-current is about reproducing published numbers here, not about the
  1e-9 property. This is the cheapest mechanism change in the repository, and it is the
  one carrying the largest measured symptom.

## The order I would run them

1. **V2**, because it is the only one with positive evidence, the change is small, and the
   prediction is specific and falsifiable: probe firings collapse toward zero **without
   recall falling**. If recall falls with them, the ratio is buying its clean probe by
   refusing to fire, which is what `tiny` and `trace` already do at F1 0.13.
2. **The 2×2 with V1**, since the `rate` result says the guard's value is conditional on
   the bar and evaluating the two independently would repeat a mistake already made once.
3. **V3 last**, and only against a stated speed budget, because it is the variant that can
   cost the tube the claim it actually owns.

## The caveat every number here inherits

All of it would be measured against a `BENCH_RECORDING` that still runs a **flat**
background, and a generator spec derived from the `.mat` store rather than the approved
folder. A mechanism probe survives that — it compares the tube to itself on one recording
— but it cannot settle whether the tube leads CoactDetect, and it must not be reported as
though it could. The bench question is
[`revise the bench recording before the re-fit`](2026-08-23-revise-the-bench-recording-before-the-refit.md).
