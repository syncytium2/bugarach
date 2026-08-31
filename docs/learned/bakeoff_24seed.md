---
status: waiting-on-tony
filed: 2026-08-30
---

# The bake-off at 24 seeds: the top four converge, and a second detector fails its gate

waiting: Promote this run over the shipped 8-seed one, or leave it beside it? Promotion re-quotes ~10 docs, the site and several figures.

> **Not murderboarded** — a finding for sessions in this tree. Every number is in
> `bakeoff_24seed.json` beside this file. **If any of it reaches an outside reader,
> murderboard that artifact first.**

The shipped bake-off runs **8 seeds in 4 folds**, and every F1 in
[the performance table](../performance_table.md) rests on it. Eight is thin. This is the
same run at **24 seeds** — 4 folds of 6 — approved by Tony as an overnight job. It took
**9 minutes 36 seconds**, which is worth recording because "it is expensive" was the
standing reason not to do it.

**Nothing is promoted.** `docs/learned/bakeoff.json` is untouched and the table still
quotes it. Promotion is decision-shaped rather than mechanical, and §4 says why.

## First: the run is bit-for-bit reproducible

Before trusting any of this, the **8-seed** configuration was re-run from scratch and
compared against the shipped file. All twelve detectors, including the six PyTorch fits,
reproduce to **delta 0.0000** on mean F1. So the differences below are caused by the seed
count and by nothing else — not by a drifting toolchain, not by nondeterministic training.

## The result: more data makes the leaders *harder* to tell apart

| detector | F1 @8 | range @8 | F1 @24 | range @24 | Δ |
|---|---|---|---|---|---|
| tube | 0.681 | 0.629–0.744 | **0.656** | 0.623–0.691 | −0.025 |
| LoCo | 0.638 | 0.567–0.696 | **0.650** | 0.630–0.667 | +0.013 |
| tube_guard | 0.673 | 0.600–0.747 | **0.645** | 0.612–0.664 | −0.027 |
| CoactDetect | 0.651 | 0.606–0.711 | **0.645** | 0.621–0.670 | −0.005 |
| rate+context | 0.571 | 0.463–0.647 | 0.594 | 0.580–0.607 | +0.022 |
| locust | 0.541 | 0.472–0.627 | 0.555 | 0.539–0.571 | +0.013 |
| tube_ratio | 0.503 | 0.422–0.562 | 0.525 | 0.469–0.563 | +0.022 |
| binned SCE | 0.420 | 0.308–0.487 | 0.417 | 0.392–0.465 | −0.003 |
| tube_ratio_guard | 0.471 | 0.424–0.545 | **0.389** | 0.228–0.462 | **−0.081** |
| SPIKE-synch | 0.254 | 0.205–0.341 | 0.266 | 0.222–0.319 | +0.013 |
| tiny | 0.125 | 0.125–0.125 | 0.125 | 0.125–0.125 | +0.000 |
| trace | 0.118 | 0.095–0.125 | 0.125 | 0.125–0.125 | +0.007 |

**The spread across the top four collapses from 0.043 to 0.011.** At 8 seeds they looked
like a descending list; at 24 they are four numbers within about one percentage point of
each other, and every fold range narrowed — rate+context's from 0.184 wide to 0.027.

**And the order inside that group rearranged.** LoCo goes from fourth to second while tube
falls from first; CoactDetect and tube_guard tie exactly at 0.645. Nothing about the
8-seed ordering of the leaders survived tripling the data, which is the clearest statement
yet that there was no ordering to find. **This is the decision to publish no ranking,
vindicated by the run that could have overturned it.**

⚠ **tube_ratio_guard moved −0.081 and its range is 0.228–0.462** — by far the widest here
and wider than it was at 8 seeds, while everything else narrowed. That is the opposite of
what more data should do and it wants explaining before that architecture is relied on.

## What changed for the gates

**locust now FAILS.** It fires **30.62** times a minute into the block with nothing
planted, against its declared ceiling of **25**. At 8 seeds it read 21.48 and passed. So
two detectors are now over ceiling rather than one:

| detector | probe/min @8 | probe/min @24 | ceiling | verdict |
|---|---|---|---|---|
| rate+context | 3.47 | **3.60** | 2 | FAIL, both runs |
| locust | 21.48 | **30.62** | 25 | passed at 8, **FAILS at 24** |
| tube_guard | 0.48 | 1.48 | — | none declared |
| tube | 2.05 | 2.09 | — | none declared |

Both failures have one cause, already filed: `fair_bakeoff.py:139` picks each fold's knob
by raw argmax with **no probe gate**, so the calibration is free to choose a promiscuous
setting and nothing objects. More seeds gave it more chances to.

## Why the learned models still have no ceilings — and must not get one from this run

The obvious move is to read the learned models' probe rates off this table and write them
into `MAX_PROBE_PER_MIN`. **Do not.**

That table's ceilings are *"measured baselines, not aspirations"* — each one measured at
the detector's **shipped operating point**. The learned models have no shipped operating
point: they are fitted per run, and in this run their knobs were chosen by the same
gate-free argmax that put two hand-written detectors over ceiling. So their probe rates
here are **an upper bound produced by an ungated search**, not a baseline. Writing a
ceiling from them would enshrine the defect the ceiling exists to catch, and would set the
bar at whatever the search happened to reach.

The order has to be: fix the calibration loop to gate, then re-fit, then measure, then
declare. Filed rather than fudged.

## The decision, and it is Tony's

**Promote this run, or leave it here beside the 8-seed one?**

Promotion is not a file copy. `bakeoff.json` is read by **20 files** under `src/`, `tests/`
and `tools/` — including `provenance.py`, `lab.py`, the site builder and four test modules
— and its numbers are quoted in about **ten documents** plus the public site and several
figures. Landing it means re-quoting all of them in one pass, at which point every one of
those documents is unreviewed prose.

Three ways:

1. **Promote fully** — replace, regenerate every figure, re-quote every document, and
   murderboard the ones that face a reader. The honest headline numbers, at the cost of a
   large coordinated edit.
2. **Leave it beside** — the shipped table stays at 8 seeds and says so, with this file as
   the record that 24 seeds converges the leaders further. Cheapest, and the table already
   names its seed count on every render.
3. **Promote the artifact, not the prose** — swap the JSON and the figures, and mark every
   quoting document as stale in one commit rather than rewriting them. Fast, but leaves ten
   documents knowingly wrong, which this project has a bad history with.

I did not choose. Option 2 is the state as committed.

## Reproduce

```
PYTHONPATH=$PWD/src python tools/fair_bakeoff.py \
  --spec docs/learned/generator_spec.json --out <scratch> --folds 4 --seeds-per-fold 6
```

9m36s on this machine, one core. The 8-seed configuration is `--seeds-per-fold 2`.

## See also

- [the performance table](../performance_table.md) — quotes the 8-seed run and says so.
- [the bake-off calibrates without the gate](../todo/2026-08-28-the-bakeoff-calibrates-without-the-gate.md)
  — the argmax defect both gate failures trace to.
- [`distractor_hits` counts coverage](../todo/2026-08-30-distractor-hits-counts-coverage-not-firing.md)
  — why the `distr` column in both runs means less than it appears to.
