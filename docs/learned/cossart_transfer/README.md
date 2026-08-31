---
status: waiting-on-tony
filed: 2026-08-31
---

# The learned detectors are the best on another lab's field and the only ones that do not survive the trip

waiting: Choose a K for the Cossart assessment. Every number here is at an unreviewed K, and `derive_spec` refuses to pick one because it is a human's call.

> **Not murderboarded** — a finding for sessions in this tree. Every number is in the
> JSONs beside this file. **If any of it reaches an outside reader, murderboard that
> artifact first.**
>
> ⚠ **NOBODY HAS LOOKED AT THE SPEC.** Both specs were produced with
> `derive_spec.py --unreviewed` and say so in their own `notes`. `docs/RESET.md` §1 calls
> that state *"not a weaker result of the same kind — not a result"*. Treat everything
> below as a direction, not a number to quote.

Tony, overnight: *"compare the detectors performance on the dandiset from cossart with
and without retraining."*

## What was actually compared, because it is not their raster

Cossart's DANDI:000219 carries **no coordination ground truth**, so recall and precision
cannot be measured on it directly. The transfer path this project already built goes the
other way round: assess their folder, derive a **generator spec** from their statistics,
simulate recordings *with* planted truth from that spec, and score there. **You transfer
the statistics, not the data.**

So "on Cossart" below means *on simulated recordings whose field size, event rate,
participation and jitter were measured from their 59 recordings*. The one axis that
matters is stark:

| | ours | Cossart |
|---|---|---|
| ROIs per recording | **32** | **566** (median; IQR 408–687, max 1050) |
| participation, top level | 22.5% | 8.1% |
| participants per event | ~7 of 32 | ~28 of 566 |

Two conditions, 4 folds of 2 seeds each:

- **retrained** — fitted on the Cossart spec, scored on the Cossart spec.
- **as-is** — fitted on **our** spec, scored on the Cossart spec. Nothing about the scored
  recordings reaches the fit; that seam is what `--score-spec` exists for and it is tested.

## The result, and it holds at both K

F1, and the planted events actually found out of 120 across the four held-out folds.

| detector | home | k3 retrained | k3 as-is | k8 retrained | k8 as-is | as-is hits, k3 / k8 |
|---|---|---|---|---|---|---|
| **CoactDetect** | 0.651 | 0.697 | **0.702** | 0.751 | **0.748** | 89/120 · 100/120 |
| LoCo | 0.638 | 0.626 | 0.597 | 0.696 | 0.689 | 89/120 · 107/120 |
| binned SCE | 0.420 | 0.323 | 0.315 | 0.458 | 0.443 | 31/120 · 47/120 |
| locust | 0.541 | 0.365 | 0.299 | 0.393 | 0.385 | 52/120 · 75/120 |
| SPIKE-synch | 0.254 | 0.176 | 0.048 | 0.183 | 0.146 | 9/120 · 30/120 |
| rate+context | 0.571 | 0.428 | **0.171** | 0.424 | **0.170** | 120/120 · 120/120 |
| **tube_guard** | 0.673 | **0.828** | *0.096* | 0.801 | *0.096* | **0/120** · 6/120 |
| **tube** | 0.681 | **0.767** | *no F1* | **0.885** | *0.187* | **0/120** · 13/120 |
| tube_ratio | 0.503 | 0.647 | *no F1* | 0.716 | *no F1* | **0/120** · **0/120** |
| tube_ratio_guard | 0.471 | 0.625 | *no F1* | 0.686 | *no F1* | **0/120** · **0/120** |
| trace | 0.118 | 0.325 | 0.133 | 0.281 | 0.133 | 9/120 · 9/120 |
| tiny | 0.125 | 0.125 | 0.125 | 0.125 | 0.125 | 8/120 · 8/120 |

***no F1* is not missing data — it is total failure.** Those models fire (45 and 39
detections across the folds) and land on **none** of the 120 planted events, so recall and
precision are both zero, F1 is 0/0, and the raw file stores `nan`.

**Choosing K changes the level but not the shape.** Every score rises a little at k=8 —
larger events are easier — and the ordering, the winners, and every conclusion below are
the same at both. The one thing K does move is how completely the learned models fail:
0 hits at k=3, 6 and 13 at k=8, which is still failure.

### Two opposite ways to fail, and neither is "slightly worse"

Carried over unchanged, the detectors that break do not break the same way. From k=3:

| detector | recall | precision | detections | hits | what it is doing |
|---|---|---|---|---|---|
| rate+context | **1.00** | **0.09** | 1311 | 120 | finds every event and buries it — 1311 detections for 120 events |
| SPIKE-synch | 0.07 | 0.04 | 2880 | 9 | fires constantly and hits nothing |
| tube / tube_guard | **0.00** | 0.00 | 45 / 39 | 0 | nearly silent, and wrong where it does fire |
| CoactDetect | 0.74 | 0.67 | 151 | 89 | behaves |

rate+context has **perfect recall** on another lab's field and is still the worst
hand-written result, because its absolute threshold saturates when the field is seventeen
times larger. The learned models fail in the mirror image: they never fire on an event at
all. An F1 column alone would have shown both as "low" and hidden that one needs its
threshold rescaled while the other needs retraining from scratch.

### Three things it says

**1. The learned models gain the most from retraining and are the only ones that cannot
travel without it.** Refitted, they are the best detectors on this field by a clear margin
— `tube` **0.885** and `tube_guard` **0.801** at k=8, against 0.751 for the best
hand-written one — and carried over unchanged they find between **0 and 13 of 120** planted
events. Maximum benefit and maximum dependence are the same property: they learned a field
of 32.

**2. CoactDetect transfers for free.** 0.702 as-is against 0.697 retrained at k=3, and
0.748 against 0.751 at k=8 — indistinguishable both times, and better than its 0.651 at
home. Within this test it costs nothing to move it to a 566-ROI preparation. LoCo is a
close second and gets *better* at k=8 (0.689 as-is), and binned SCE holds too.

**3. rate+context does not travel, and it is not because it stops finding things.** It
loses 0.25 F1 in both K conditions while hitting **120 of 120** planted events. Its recall
is perfect and its precision is 0.09. An absolute threshold that is right for 32 ROIs is
tripped constantly by 566, so it finds every event and drowns each one in false alarms.
SPIKE-synch is worse in both directions at once. **What survives a seventeen-fold change
in field size is a statistic computed relative to the field's own population** — which is
what CoactDetect and LoCo compute and what these two do not.

That is the shape of the answer to *"does a detector tuned on our preparation work on
another lab's?"* — **for two of the six, yes, essentially free; for the learned models, only
if the lab can refit, and then better than anything else.** Which is exactly the case for
shipping the training loop rather than the weights.

## What would have to be true before any of this is quoted

- **A human has to choose K.** `assess.py` scans 3–24 and K decides what counts as one
  event; `derive_spec.py` requires `--k` explicitly and refuses to choose. The k=8 pair
  here is that check, and **the ordering survives it** — every score rises a little and
  nothing reorders — so the conclusions do not rest on the unmade choice, though the
  numbers do.
  **And no K in their scan reproduces our participation fraction**: our `k_chosen: 3` is
  3 of ~34 ROIs, about 9%. Three of 566 is 0.5%; even 24 is 4%. That gap is not a detail —
  it is the transfer problem stated in one line.
- **The background shape is ours, not theirs.** The Cossart export yielded **0 usable
  baseline windows**, so `bg_rate_shape=0.275` is inherited from this lab's recordings. The
  spec says so in its own notes. A background is not a detail for detectors that estimate
  one.
- **8 seeds.** Same thinness the home bench has, and
  [the 24-seed run](../bakeoff_24seed.md) showed 8 seeds reorders the leaders.
- **Simulated, not their raster.** Nothing here is a measurement of Cossart's recordings;
  it is a measurement on recordings built from statistics of theirs.

## Files

| file | what it is |
|---|---|
| `spec_k3.json`, `spec_k8.json` | generator specs derived from `assessment_cossart.json`, **unreviewed** |
| `k3_retrained.json`, `k8_retrained.json` | fitted and scored on the Cossart spec |
| `k3_as_is.json`, `k8_as_is.json` | fitted on ours, scored on the Cossart spec |

## Reproduce

```
python tools/derive_spec.py --assessment docs/learned/assessment_cossart.json \
    --out <dir> --k 3 --unreviewed
python tools/fair_bakeoff.py --spec <dir>/generator_spec.json --out <retrained> \
    --folds 4 --seeds-per-fold 2
python tools/fair_bakeoff.py --spec docs/learned/generator_spec.json \
    --score-spec <dir>/generator_spec.json --out <as-is> --folds 4 --seeds-per-fold 2
```

About 12 minutes for the pair on this machine — slower than the home bench because the
field is seventeen times larger.
