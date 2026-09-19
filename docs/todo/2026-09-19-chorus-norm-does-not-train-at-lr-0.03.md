---
status: open
filed: 2026-09-19
---

# chorus_norm's lr-0.03 configurations do not train: pick a repair

The diagnosis is in [`docs/learned/chorus_collapse/index.html`](../learned/chorus_collapse/index.html),
built by `tools/diagnose_chorus_collapse.py`.

## What was found

- **Where it happens.** At a learning rate of 0.03, most of chorus_norm's inner fits collapse:
  292 of 396, against 7 of 468 below that rate. A collapsed fit calls every recording as a single
  event, which scores F1 0.125.
- **Why the output stays flat.** Every fit starts with a nearly flat output. A collapsed fit never
  leaves that start, and its head (8 layers of 8 GELU units, never tuned) later goes silent: one
  of its layers passes nothing that varies. The head's input still separates events from everything
  else, so the signal is lost in the head. This is not the "starts deaf" encoder failure that PR
  #596 diagnosed in plain chorus.
- **What prevents it.** Replayed exactly, the same fit trains at lr 0.003 or 0.01, or at 0.03
  with a 200-step linear warm-up. The same warm-up, tried on 7 other collapsed runs, trained 6.
- **Effect on goal 2.** Tuning chose no lr-0.03 configuration for chorus_norm, so the collapse
  took 11 of its 24 configurations out of contention rather than putting dead models into its
  held-out scores.
- **chorus_gain_norm is different.** Its encoder shape matters as much as the learning rate, and
  tuning did choose lr-0.03 configurations for it.

## The decision, which is Tony's

Each option changes chorus_norm's numbers in goal 2, and both draws would need to run again before
the results can be compared.

1. **Drop lr 0.03 from chorus_norm's grid.** This makes the declared grid the one tuning already
   used in effect. It says nothing about chorus_gain_norm, whose tuning did pick lr 0.03.
2. **Add a linear learning-rate warm-up to `train()`.** The trainer is shared, so this changes
   every net. 200 steps is a tenth of Ma & Yarats's rule of thumb for Adam. A 50-step warm-up,
   tried on one fit, was not enough.
3. **Change the head**, by making it wider or shallower. This was not tried.

## Also open, whatever is chosen

- **Catch a collapse in training.** On the census recording, the output's standard deviation
  separates collapsed fits from working ones without overlap: at most 0.132 logits against at
  least 0.803. A check at the end of training could refuse such a fit. The gap was found on one
  recording and has not been tested on others.
- **24 collapsed chorus_gain_norm fits are unexplained.** In the second draw, 24 of its 75
  collapsed inner fits have a flat output without a silent layer. Nothing here explains them.
