---
status: open
filed: 2026-09-10
---

# The encoder clips out-of-range onsets onto frame 0 and frame n−1 instead of dropping them

> A latent defect today. A **support violation** the moment any surrogate displaces an onset.

## The line

`src/bugarach/learn/encode.py`, in `encode()`:

```python
idx = np.clip(((v - t0) / dt).astype(np.int64), 0, n_frame - 1)
```

Any onset falling outside `[t0, t1]` is **pinned to the nearest boundary frame** rather than
discarded. On real data nothing is out of range — the extent is derived from the trains themselves —
so today this never fires.

## Why it becomes a defect

The moment a surrogate displaces onsets in time — dither, jitter, shift — events near either edge
move out of range, and clipping **piles them onto exactly frame 0 and frame n−1**. Real recordings
essentially never place onsets on the boundary frame; a displaced one does, with probability rising
in the displacement width. That is an **infinite likelihood ratio at a known location**, carrying
zero cross-cell information — a discriminator can win on it alone.

Murderboard role 4, 2026-09-10, put it at **40 % of windows carrying a pile-up at J = 2 s and 74 %
at J = 5 s**. Reproduce before quoting; those are analytic estimates, not measurements on the folder.

## The fix is a choice, and it must be stated

- **Drop** out-of-range onsets — leaves a density deficit in the outer band, also detectable but far
  weaker than a pile-up.
- **Dither the whole recording before cutting windows**, and score only the interior, discarding a
  margin at each end so no scored frame is within the displacement width of a place events can leave
  from. This is the better answer and costs only a margin.

Clipping is the worst of the three and is what the code does now.

## Closes when

`encode()` either drops or refuses out-of-range onsets rather than clipping, the boundary policy is
named in its docstring, and a test asserts that no surrogate can manufacture a boundary-frame
pile-up. Related: [`build the surrogate screen`](2026-09-10-build-the-surrogate-screen.md), whose
counting tier measures exactly this.
