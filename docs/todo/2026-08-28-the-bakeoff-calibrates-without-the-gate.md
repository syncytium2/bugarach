---
status: open
filed: 2026-08-28
---

# The bake-off picks each fold's knob by raw argmax, and rate's pick is over its own ceiling on every fold

> ## ⛔ Do not act on the fix section. Tony, 2026-08-28, hours after this was written:
>
> > *"all the bake-offs are stale. the next bakeoff will be in app. that is the only
> > pipeline that matters now."*
>
> **So `tools/fair_bakeoff.py` is not to be repaired and `docs/learned/bakeoff.json` is not
> to be regenerated on this file's account.** Both are on a path being retired. Read the fix
> section as the record of what *would* have been done, not as an instruction — it was
> written before the ruling and is left standing rather than deleted, because the measurement
> is still the evidence for what follows.
>
> **What survives the ruling, and is the reason this file is still worth reading:**
>
> 1. **The in-app bake-off already selects without the gate — checked, not predicted.** This
>    started as a warning about a bake-off nobody had written yet. The browser's sweep is
>    stage 6a and it exists today, so the warning was checkable, and the answer is below
>    under *"The app has two of the three refusals"*. It is the one finding here that is
>    about the pipeline that matters.
> 2. **`bench.py:703` is a live defect on code the app path may well use** — see the second
>    section below. It is not stale; it has never been right.
> 3. **The numbers below are the case for (1)**, and they are the only measurement anyone has
>    of what the gate does to a *fold-based* selection rather than a single sweep.

> **Not murderboarded** — a code reading and one `json.load` over a store already in the
> tree. Every number below is reproducible by the snippet at the end.

> **Found because of #379.** That PR measured the promiscuity gate on the rate mechanism
> probe and showed it refuses **31 of 56** additive candidates and moves additive's own
> operating point. The obvious next question is *which other callers choose a knob without
> it* — and the bake-off, which produces the numbers on the public page, is one.

## What the code does

`tools/fair_bakeoff.py:139-140`, inside the per-fold calibration loop:

```python
if np.isfinite(p.f1) and p.f1 > best_f1:
    best_f1, best_v = p.f1, v
```

Raw argmax over the grid. It does not call `bench.pick_operating_point`, so it gets **none
of that function's three refusals**: no promiscuity gate, no `EdgeOfRange`, no
`DegenerateSweep`. The knob that wins on F1 is taken, whatever it does in a block where
nothing was planted.

That rule was decided against in this repo on **2026-08-22**, in `MAX_PROBE_PER_MIN`'s own
docstring — *"the fix for 'the alarm cannot ring' is to give the probe a gate at selection
time"* — and `pick_operating_point` applies it by default. The bake-off predates neither;
it simply never routed through it.

## What it costs, measured on the shipped store

Held-out folds in `docs/learned/bakeoff.json`, against the shipped ceilings in
`MAX_PROBE_PER_MIN`:

| detector | ceiling /min | per-fold /min | over ceiling |
|---|---|---|---|
| **rate** | 2.0 | 3.3, 3.5, 3.8, 3.3 | **4 of 4** |
| **cicada** | 25.0 | 12.0, 36.6, 17.1, 20.2 | **1 of 4** |
| sce | 9.0 | 6.0, 5.8, 5.9, 6.0 | 0 of 4 |
| sync | 1.0 | 1.0, 0.9, 1.0, 0.6 | 0 of 4 |
| loco | 1.0 | 0.5, 0.1, 0.2, 0.2 | 0 of 4 |
| coact | 1.0 | 0.2, 0.0, 0.2, 0.1 | 0 of 4 |

**rate's published bake-off F1 is earned at a setting this project would refuse to ship**,
on every fold. `pick_operating_point` exists precisely to say *"that setting wins on F1 by
keying on rate, so it is not an operating point"*, and nothing said it here.

**The ceilings transfer, and that was checked rather than assumed.** The probe block is
constructed identically in `BENCH_RECORDING` and in the bake-off spec — same `hot_window`
(1200–1500 s), same `hot_rate_hz` (0.06), same `ramp_sec`, same `distractor_window`, same
`n_per_level`. The two differ in `duration_sec` (2700 vs 3525) and in background rate
(the two `REGIMES` endpoints vs a single 0.0097), and that background sits **inside** the
baseline interquartile range FOUNDATIONS §9 fixes the axis to. So this is the same
instrument reading in both places.

## Two honest limits on the claim

- **These are held-out rates; the gate acts at selection, on training folds.** So the table
  shows the *chosen* setting is promiscuous where it was scored, not that the gate would
  have refused it at the moment of choice. Those are different measurements and only a
  re-run answers the second. The gap is not large — a knob that fires 3.3–3.8/min on
  held-out folds did not arrive there from a quiet training fold — but it is a gap.
- **This does not retract the bake-off's comparison.** Whether it reorders anything is
  unmeasured. It is not common-mode: the gate has per-detector ceilings, four of the six
  are comfortably inside theirs, and #379 showed it bites one mechanism hard and another
  not at all. So it *could* reorder, and saying it does would be a story.

## The app has two of the three refusals, and the missing one is the gate

**This is the part that matters**, given the ruling above. Stage 6a — *"optimize the six
detectors"* — is **already in the browser**, and `webapp_completion_plan.md` records it as
done: *"all six; the sweep splits folds and pools through the same scorer as the Python,
checked against it in CI."*

`docs/site/raster_viewer.html:4234`, `pickOperatingPoint`, is a careful port of the Python
function. It refuses a degenerate sweep and it refuses an optimum at the edge of the grid,
each with the Python twin named in a comment. **It does not refuse a promiscuous winner.**
The function ends after the edge check; there is no gate and no ceiling table.

And the page **already computes the number the gate needs**:

```js
out.hotFaPerMin = (hotWindow) => { …                 // raster_viewer.html:4117
```

`grep -n 'hotFaPerMin' docs/site/raster_viewer.html` returns **one line — its own
definition.** Nothing calls it. The browser scorer correctly keeps the probe out of F1
(`out.nScored = out.nDetected - out.hotFa`, line 4086, with the reasoning quoted from
`pool_scores`), so it has the *first* half of the 2026-08-22 decision and not the second:
the probe stays out of the score, and nothing gates on it at selection.

So the app can choose exactly the settings the Python refuses — which, measured on the rate
mechanism in #379, is **31 of 56 candidates** at that detector's ceiling.

**One thing the browser gets right that Python does not.** `hotFaPerMin` takes the window as
an argument instead of reaching for a module-level constant, which is precisely the defect in
the next section. When that Python bug is fixed, the browser is the reference.

### And the gate cannot be ported, because the probe is not there to gate on

Tony said *"do it"* to porting the gate. **It would be inert**, and that is worse than
absent: a third branch in `pickOperatingPoint` would sit in the page looking like Python's
protection while measuring nothing. The probe is not **planted** in the app on either route —
which is not the same as the app being unable to run one, a distinction this section first
got wrong and step 1 below now states properly:

| | |
|---|---|
| the in-browser generator | `simulateRecording` (raster_viewer.html:5335–5442) contains no `hot` block and no distractors — `grep` over that range returns nothing |
| the lab-server route | `LAB_SPEC_DEFAULTS` (:9786) carries `hot_rate_hz: 0.06` but **no `hot_window`**, and `simulate.py:653` reads `if hot_window is not None and hot_rate_hz > 0` — so Python plants none either |
| the scorer | `scoreDetections` (:4154–4217) returns `nPlanted, nDetected, nHit, nMiss, nFa, nDup, byFrac, recall, precision, f1` — **no `hotFa`** |
| the pool | `out.hotFa += sc.hotFa \|\| 0` (:4070) therefore always adds `undefined \|\| 0`, so `out.nScored = out.nDetected - out.hotFa` (:4086) **is the identity function** |

**And the page says so itself — this is a documented stub, not a disguise.** The comment
above that line, at :4082:

> *"The browser's generator plants no probe, so today this equals `nDetected` and the
> distinction costs nothing; it stops being free the day one is added, which is exactly when
> a page computing its own precision would quietly disagree with the Python."*

So nobody was misled and nothing is pretending. The exclusion rule was written **ahead of**
the probe on purpose, with its own inertness stated and the failure mode named. What is
missing is the probe, and the person who wrote this line predicted precisely the situation
this file is now in. Read it as a gap in the plan's sequencing, not as a defect in the code
— and note that the same care is the reason step 4 below is cheap when its turn comes.

**The real chain is four steps and the gate is last:**

1. **Plant the probe.** ⚠ **Corrected 2026-08-28 — this is not one job, and the wording above
   read as though the app *could not* run a probe. It can.** Tony asked directly; the answer
   splits by route and the two costs are nothing alike:
   - **The lab-server route already has the capability, and needs one key.** `lab.py:499` is
     `simulate_coordination(seed=seed, **spec)` with `spec` arriving straight from the page's
     `labSpec()`, and that function fully supports the probe. The page already sends
     `hot_rate_hz: 0.06`. Adding `hot_window` to `LAB_SPEC_DEFAULTS` plants it.
   - **The published in-browser generator needs the block written.** `simulateRecording` is a
     hand-written JS port and the hot block was not among the parts ported — a Poisson draw
     over a window, not a large job, but it is code rather than a setting.
   - **They must agree**, or the page and the server disagree about what a precision number
     means, which is exactly the failure the `:4082` comment names.
2. **Score it** — `scoreDetections` counts detections falling inside that window and returns
   `hotFa`, the way `score.py:242` does.
3. **`nScored` stops being the identity**, which is the moment the app's exclusion rule
   begins to mean what its comment says.
4. **Then the gate**, with the six ceilings and a third branch.

**Step 3 is the one to think about before starting.** It is *approximately* F1-neutral by
design — the probe adds detections and then excludes them from the precision denominator, so
a correct implementation should leave the headline near where it is. That is a prediction,
not a measurement, and it is exactly the kind of prediction this repo has been wrong about
before. It should be measured on the existing data set before and after, and the answer
stated, rather than asserted from the algebra.

What is **not** neutral either way: the user's simulated recording gains a dense block it
does not have today, which changes the raster they look at and the data they tune on.

## A second defect on the same code path, latent today

`bench.py:703`, in `hot_fa_per_min`:

```python
span = BENCH_RECORDING["hot_window"]
```

The rate is computed against **the bench recording's** window, whatever recording actually
produced the result. It is correct today only because the bake-off spec happens to carry
the same window — which is luck, and the arithmetic above depends on it. Any spec with a
different probe block silently yields a wrong per-minute rate, and the gate that consumes
it silently uses a wrong ceiling comparison. The value is in `gt.params["hot_window"]`,
which is where `score.py:239` correctly reads it from.

## The fix, and why this is filed rather than done

Two lines in the calibration loop — build the fold's curve and let
`pick_operating_point` choose it, catching the three refusals as outcomes rather than
letting the first one end the run (`tools/refit.py` does exactly this and is the worked
example). **But regenerating `bakeoff.json` moves numbers on a page written for outside
readers**, and by the murderboard rule a document deliverable is not a session's to redraft
unasked. Same call `2bc3160` made when it wrote *"not touched: the prose that quotes these
numbers"*, and the same one #373 made.

**Sequencing.** `the-numbers-moved` holds `bakeoff.md` / `bakeoff.html` / `report.html`;
this is the *calibration rule*, not the transcription, and the two should not be merged into
one job. And it belongs after — not before — the scoping question in
[two scorers, two winners](2026-08-25-two-scorers-two-winners-and-nothing-decides.md), since
#379 narrowed that to *"is the gate enough?"* and this is evidence about what the gate does
when it is finally switched on somewhere it currently is not.

## Reproduce

```bash
python3 -c "
import json, sys; sys.path.insert(0, 'src')
from bugarach.bench import MAX_PROBE_PER_MIN
b = json.load(open('docs/learned/bakeoff.json'))
hw = b['spec']['hot_window']
mins = (hw[1] - hw[0]) / 60.0 * b['seeds_per_fold']
for det, v in b['hand_written'].items():
    r = [f['hot_fa'] / mins for f in v['per_fold']]
    c = MAX_PROBE_PER_MIN[det]
    print(det, c, [round(x, 1) for x in r], sum(x > c for x in r), 'over')
"
```
