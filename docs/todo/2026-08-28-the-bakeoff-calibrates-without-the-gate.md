---
status: open
filed: 2026-08-28
---

# The bake-off picks each fold's knob by raw argmax, and rate's pick is over its own ceiling on every fold

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
