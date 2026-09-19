---
status: open
filed: 2026-09-19
---

# The chorus grids put a third of their fits where they cannot train: pick a repair

**What was found** ([`docs/learned/chorus_collapse/index.html`](../learned/chorus_collapse/index.html),
built by `tools/diagnose_chorus_collapse.py`):

- At a learning rate of 0.03, chorus_norm's head dies in the first training steps. The head is 8
  layers of 8 GELU units, and it was never tuned.
- A dead head layer makes the output a constant, so the whole recording becomes one call (F1 0.125).
- That accounts for 292 of chorus_norm's 396 inner fits at lr 0.03, against 7 of 468 fits below it.
- It is not the "starts deaf" failure that PR #596 fixed in plain chorus.
- Tuning never chose a lr-0.03 configuration. The effect on goal 2 is therefore a smaller effective
  grid, not dead models in the held-out scores. 4 refits did collapse and carry the replicate
  report's †.

**The decision, which is Tony's.** Every option changes chorus_norm's numbers in goal 2, and each
would need both draws re-run before the draws can be compared:

1. **Drop lr 0.03 from the chorus grids.** This makes the declared grid the one tuning already used.
2. **Add a learning-rate warm-up to `train()`.** 200 steps rescued 7 of 8 collapsed fits in replay,
   and 50 steps did not. Because `train()` is shared, this changes every net.
3. **Change the head** (wider or shallower). This was not tested.

**Also open, whatever is chosen:**

- **A collapse can be detected when it happens.** On the census recording, the output's spread
  separates collapsed fits from working ones with no overlap: at most 0.13 against at least 0.80. A
  check at the end of training could refuse such a fit instead of scoring it.
- **chorus_gain_norm has a second route to the same flat output.** 15 of its 75 collapsed fits have no
  dead layer, and these are spread across all three learning rates. That route is not diagnosed.
