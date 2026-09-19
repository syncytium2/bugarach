---
status: open
filed: 2026-09-19
---

# chorus_norm's lr-0.03 configurations do not train: pick a repair

The diagnosis is in [`docs/learned/chorus_collapse/index.html`](../learned/chorus_collapse/index.html),
built by `tools/diagnose_chorus_collapse.py`.

## What was found

- **Where collapse happens.** Across both draws, 292 of chorus_norm's 396 inner (tuning) fits at a
  learning rate of 0.03 collapse, against 7 of 468 at lower rates. A collapsed fit makes a single
  call covering the whole recording, which scores F1 0.125.
- **Why the output stays flat.** At its starting weights, the head of every replayed fit is silent:
  its layers pass almost nothing that varies. In the working fit, training wakes the head within
  about 50 steps. In the collapsed fit replayed as run, it never does.
  - In the second draw, every collapsed inner fit ends with a silent head layer (153 of 153
    chorus_norm, 75 of 75 chorus_gain_norm), measured away from the ends of the recording. No
    working fit does.
  - For most collapsed chorus_norm fits the votes still respond to an event, so this is not the
    deaf-encoder failure that PR #596 diagnosed in plain chorus. 4 of 153 are as deaf as plain
    chorus.
  - In chorus_gain_norm the votes respond less often: 19 of its 75 collapsed fits are as deaf as
    plain chorus.
- **What prevents it.** Replayed exactly, the same fit trains at a learning rate of 0.003 or 0.01,
  or at 0.03 with a 200-step linear warm-up.
  - The same warm-up was tried on 7 other hand-picked collapsed runs. Training loss fell below 0.5
    in 6 of them.
  - That was judged by training loss, not by calls on held-out recordings.
- **Effect on goal 2.** Tuning picked no lr-0.03 configuration for chorus_norm under either
  selection. Whether collapse alone decided that was not tested.
  - 2 of chorus_norm's refits collapsed anyway, both at lr 0.01.
  - For chorus_gain_norm, the selection on F1 alone picked lr 0.03 in 6 of 8 folds, and both of its
    collapsed refits came from those picks. The selection under the false-alarm budget never picked
    lr 0.03.

## The decision, which is Tony's

Each option changes chorus_norm's numbers in goal 2, and both draws would need to run again before
the results can be compared.

1. **Drop lr 0.03 from chorus_norm's grid.** This matches what tuning picked anyway. Doing the same
   for chorus_gain_norm would change what its selection on F1 alone picked.
2. **Add a linear learning-rate warm-up to `train()`.** The trainer is shared, so this changes every
   net. 200 steps is a tenth of Ma & Yarats's rule of thumb for Adam. A 50-step warm-up, tried on
   one fit, was not enough: the head woke and then fell silent again.
3. **Change the head** (it was never tuned). This was not tried.

## Also open, whatever is chosen

- **Catch a collapse in training.** On the census recording, measured away from its ends, the
  output's standard deviation separates collapsed fits from working ones without overlap. A check
  at the end of training could flag such a fit.
  - A flagged fit must still count against the net, as a failure or as a retraining charged to it.
    Dropping it would select on the outcome.
  - The gap was found on one recording from one draw.
- **The replicate report misreads an overlap.** It reads the 111 chorus_norm fits that collapsed in
  both draws as the same fits failing twice. The configurations' collapse rates alone predict that
  many (111.5). The chorus-collapse page corrects this. The report itself
  (`docs/learned/tuned_vs_coact/replicate1/`) should be rebuilt with the corrected sentence, and its
  builder's assert on that overlap, at `tools/make_replicate_report.py` around line 1190, should be
  dropped.
