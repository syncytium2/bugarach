---
status: done
filed: 2026-08-24
closed: 2026-08-25
---

# The null leaked; the excess is selection-corrected now

> ## ✅ Decided and implemented 2026-08-25
>
> Tony was shown both outcomes measured
> ([the decision figure](../learned/assess_fork_decision.png)) and **took the
> correction**. Landed in PR #303 as `excess_mode="corrected"`, the default, in both
> the Python and the browser — [forks §13](../forks.md).
>
> | nothing planted, K=3 | was | is |
> |---|---|---|
> | quiet, 5.2 mHz/ROI | 0.28 | **0.01** |
> | busy, 19.0 mHz/ROI | 6.14 | **0.39** |
> | crowded, 50 mHz/ROI | 30.09 | **0.04** |
>
> The residual does not track the background — that is how it is told from the bias
> it replaced — and it is signed, so it is noise rather than a clamp.
>
> **No parity exemption was needed.** `coact_excess_raw` still carries the
> uncorrected quantity on every call and `tests/test_assess.py` still holds it to the
> MATLAB fixtures at 1e-9 via `excess_mode="raw"`. The inheritance stayed *verified*
> rather than waived — a cleaner pattern than
> [ADR-0003](../adr/0003-parity-was-the-inheritance-not-the-contract.md) anticipated
> needing, and the one to reach for on the next fork.
>
> `tests/test_assess_null.py`'s strict xfail — *plant nothing, expect zero* — passes
> now, and the tests that pinned the leak are retired with it.
>
> **Still owed, not started:** RESET §5's one-pass regeneration of everything derived
> from the old number — `docs/learned/`, `generator_spec.json`, the bake-off. It
> should not start until
> [the scoring question](2026-08-25-two-scorers-two-winners-and-nothing-decides.md)
> is settled, or it needs doing twice.

> **Not murderboarded** — a finding for sessions in this tree, same standing as
> the revision plan it feeds. Every number is reproducible from
> `tests/test_assess_null.py` and `tools/make_null_leak_figure.py`. **If any of it
> reaches an outside reader, murderboard that artifact first.**

`docs/RESET.md` §7 puts the null test first in the order of work, ahead of the
background axis and ahead of the fresh assessment the K decision waits on. §1
gives the reason: *"plant nothing, and the excess must read zero. A rate-matched
null that leaks is a defect in the arithmetic whatever convention sits on top,
and every generator spec derived afterwards inherits it."*

**It leaks.**

![Panel A: excess against background rate on recordings with nothing planted, K=3, 4 and 6, all rising steeply away from the zero line rather than sitting on it. Panel B: at each of three backgrounds, the excess computed on the recording beside the excess computed on a draw from the null itself — the two bars are nearly the same height at the busy and crowded backgrounds](../learned/assess_null_leak.png)

## What is new here, and what is not

**None of this is a discovery about statistics** (Tony, 2026-08-24: *"I'd be
surprised if this isn't a known issue in neuroscience and outside fields. That's
why we have these fancy detectors. The assessor is a simple tool for a
challenging problem."*). Comparing a selected extremum against an ensemble
*mean* is a textbook selection bias, and the textbook remedy — compare against
the ensemble *distribution* instead — is exactly what the surrogate literature on
synchrony testing does. The assessor is a deliberately simple instrument, chosen
because it is not one of the six detectors and therefore cannot make the
benchmark a restatement of whichever detector measured it. Simple was the point.

**What is new is the size of it, here, at this project's own background rates**,
and the fact that nothing downstream knows. The excess is used as an absolute
per-minute magnitude — to choose K, to size the generator, and (if the treatment
contrast is ever built) to compare two windows. Those uses need the number to
mean something on its own, and at 19.0 mHz/ROI 96% of it does not. That is worth
a measurement rather than an assumption, which is what this file is.

## What it looks like

![Three rasters, one per row, each with a lane above it holding the assessor's calls. Top: quiet background, nothing planted, a single call. Middle: busy background, nothing planted, fifteen calls in the six minutes shown, all spurious. Bottom: busy background with twelve real events planted — green calls sit on the blue triangles marking planted events, and red spurious calls outnumber them](../learned/assess_calls.png)

Same 40 ROIs, same window, same generator; only the background rate and whether
anything was planted differ. **The assessor is not blind** — in the bottom panel
it found all 12 planted events. It also made **77 calls that were not on one**,
in the same recording, at the same K. The instrument detects real coordination
and cannot tell you which of its calls that was, which is the argument for the
person in MAHDCE rather than against the tool.

## What was measured

Independent Poisson ROIs — every train drawn on its own, no shared process, no
injected event, so every co-active moment is a coincidence and the rate-matched
null is exactly the right model of what produced it. 40 ROIs, 30-minute window,
1 s bins, 200 surrogates, three seeds per rate.

| background | K=3 | K=4 | K=6 |
|---|---|---|---|
| quiet, 5.2 mHz/ROI | 0.28 | 0.00 | 0.00 |
| **busy, 19.0 mHz/ROI** | **6.50** | 1.54 | 0.00 |
| crowded, 50 mHz/ROI | 30.09 | 18.70 | 2.93 |

Excess co-active ROI·events per minute, on data with no coordination in it. The
two named rows are the endpoints of this project's own difficulty axis
(`bench.REGIMES`, corrected 2026-08-20), so this is not an exotic regime — it is
the interquartile spread of untreated slices.

## What it is actually measuring

Read off `assess.py` rather than inferred:

```python
bk = np.flatnonzero(obs >= K)          # bins chosen BY THE OBSERVED counts
obs_mass  = obs[bk].sum() / win_min
null_mass = null_mean[bk].sum() / win_min
coact_excess = obs_mass - null_mass
```

Bins are selected where the **observed** count reaches K, then the observed is
compared against the null's **mean** in those same bins. Selecting on the
observed value guarantees the observed is high there; the null mean is the
ensemble average and is not. The difference is positive by construction whenever
any bin reaches K, coordination or no. It is the winner's curse.

**The decisive measurement** is panel B, and it is the one worth quoting. Hand
the estimator a circular shift of the same trains — by construction a draw *from*
the null it compares against, so an unbiased estimator reads zero on it:

| background | the recording | a draw from the null | ratio |
|---|---|---|---|
| quiet, 5.2 mHz | 0.28 | 0.09 | 34% |
| busy, 19.0 mHz | 6.14 | 5.91 | **96%** |
| crowded, 50 mHz | 30.09 | 28.88 | **96%** |

At the background the real recordings sit at, **96% of the excess survives when
the data is replaced by pure null.** Whatever the statistic is measuring, it is
almost entirely the selection rule.

It is a bias and not an estimation error: 50 surrogates and 800 surrogates give
the same answer to within 20%, because more surrogates estimate the null mean
better and do not touch which bins were chosen.

## Why this matters beyond the assessor

Three consequences, in the order they bite.

1. **K is chosen off a leaking number.** RESET §7 item 3 has a person choosing K
   on the approved folder, and §1 makes that choice constitutive. The excess as a
   function of K is exactly what an analyst reads to make it — and at the busy
   background it reads 6.50 at K=3 and 0.00 at K=6 on *nothing*. The apparent
   "coordination falls off above K=4" shape is partly the bias dying out.
2. **Every generator spec inherits it.** `derive_spec` sizes event frequency and
   recruitment from the assessment. A baseline that reads coordination it does not
   have parameterises a simulation with events it should not have, and the six
   detectors are then tuned against that.
3. **The leak grows with the background rate, and the treatment contrast is a
   comparison across backgrounds.** RESET §6 already says a change in detections
   across a treatment window mixes coordination with the instrument's sensitivity.
   This is worse and more specific: the excess is quoted as an absolute per-minute
   magnitude, and a window at a different rate carries a different bias. Under TTX,
   coordination splits by stream (FAST 0.46, SLOW 2.50) — a result running in
   opposite directions in two streams is exactly the shape a rate-tracking bias
   could manufacture *or* hide. RESET §6 called the assessor "the one
   rate-controlled instrument in the stack" and flagged that whether two windows at
   different rates yield comparable excesses is "established nowhere". It is
   established now, and the answer is no.

## What was NOT done, and why

**The arithmetic is untouched.** `assess_coactivity` is held to 1e-9 against
`measure_coordination_timescale.m` and parity is the product (FOUNDATIONS §2), so
the same bias is in the MATLAB and in every number the constellation campaign
produced. Correcting it here would break the one property the port exists to
have, and would silently put this repo and the producer's numbers on different
definitions. That is Tony's call, and if it is taken it lands as a named fork
(`docs/forks.md`) defaulting to current behaviour, like every other mechanism
change.

**The tests pin the leak rather than forbid it** (`tests/test_assess_null.py`),
so the suite stays green and the measurement is available to act on. The property
RESET asks for is written down as a **strict xfail**: the day the arithmetic is
fixed, that test passes, the strictness turns it into a failure, and whoever did
it is told to retire the pinning tests with it. Nobody has to remember.

## What would fix it, when somebody decides to

- **Select on the null too. ✅ COSTED 2026-08-24.** Compute the same statistic on
  every surrogate, each selecting on *itself*, and report the observed excess
  minus the *median surrogate excess*. The standard remedy for a selection-biased
  statistic; it reuses the ensemble already being computed, so it needs no extra
  sampling and adds no parameter. **Measured, with the consequences drawn:**

  ![Panel A, excess against K at the busy background: the current estimator falls 75 percent from K=3 to K=6 on planted data and its nothing-planted curve has the same shape, while the corrected estimator is flat across K=3 to 6 and sits on zero when nothing is planted. Panel B, the same twelve planted events at two backgrounds: the current estimator reports them 2.8 times larger at the busy background, the corrected one within 17 percent](../learned/assess_fork_decision.png)

  | at the busy background, K = 3 | current | corrected |
  |---|---|---|
  | nothing planted — the answer is zero | **6.15** | **0.41** |
  | 12 events planted | 8.95 | 2.27 |
  | same 12 events, busy ÷ quiet (1.0 = comparable) | **2.80×** | **0.83×** |
  | fall from K=3 to K=6, 12 events planted | **−75%** | **−19%** |

  Two consequences beyond the null reading zero. **The K curve reverses its
  reading:** under the current estimator the excess falls 75% from K=3 to K=6, and
  an analyst reading that concludes the coordination lives at low K — but the
  nothing-planted curve has the same shape, so most of the fall is the bias dying
  out. Corrected, the signal is flat across K=3–6 and the choice of K stops
  changing the answer. **And the excess becomes comparable across backgrounds:**
  the same twelve events read 2.8× larger at the busy background under the current
  estimator and within 17% under the corrected one — which is exactly what
  consequence 3 above, and RESET §6, said was established nowhere.

  Costed by `tools/make_fork_decision_figure.py`, which computes the corrected
  estimator **in the tool rather than in `assess.py`**, so the consequence could be
  shown without a session pre-empting the decision.

Still uncosted, listed so the options stay on the table rather than being
rediscovered:

- **Report the excess as a percentile of the surrogate excess distribution**
  rather than as an absolute magnitude, which also fixes the cross-window
  comparability problem in consequence 3.
- **Do not select at all**: sum `obs - null_mean` over every bin. Unbiased and
  answers a different question, since it stops being about co-active moments.

Any of them changes what the number means, so it is a fork with a name, and the
generator spec and everything derived from it would need regenerating in one pass
— which RESET §5 already requires for other reasons.

## Decisions this needs from Tony

1. **Fork the assessor's excess, or keep parity and caveat the number?**
2. **Does the K decision (RESET §7 item 3) wait for that?** It is currently the
   thing everything downstream is blocked on, and it is read off this statistic.
3. **Does the producer team need telling?** The same arithmetic is in
   `measure_coordination_timescale.m`, and `darkroom/constellation/` holds numbers
   computed with it.
