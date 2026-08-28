---
status: open
filed: 2026-08-28
---

# `forward` and `_kernels` clamp the same fitted centre width to different ranges

> **Not murderboarded** — a code observation, reproducible in four lines. Split out
> of [the docstring correction](2026-08-27-the-model-does-not-do-what-its-docstring-says.md),
> which named it as a third thing worth a line either way and was right that it is
> a separate decision from the two prose errors.

`build_tube` derives two things from the same parameter, `log_center`, and bounds
them differently:

| where | expression | range |
|---|---|---|
| `forward` | `int(exp(log_center.detach()).min().clamp(1, k))` | `[1, 128]` |
| `_kernels` | `exp(log_center).clamp(0.5, k / 2)` | `[0.5, 64]` |

One is a pooling radius in whole frames, the other a Gaussian sigma, so the two
are not obliged to be identical — but nothing in the file says that, and nothing
says which range is the intended one.

## Why it has not bitten

Measured on a trained model (bake-off spec, 900 steps): fitted centre widths come
out around **3.9, 4.0, 5.0, 7.0 samples**. Both clamps are inert over that range,
so the two expressions agree today and the difference is latent rather than live.

It would become live at either end:

- a width fitted **below 1** — `_kernels` uses 0.5, `forward` uses 1;
- a width fitted **above 64** — `_kernels` caps the sigma at 64 while `forward`
  pools over `2*128+1 = 257` frames, so the pooling window would be four times the
  widest centre the kernel is allowed.

The second is not hypothetical in spirit: `ablate_tube.py` was written precisely
because a fitted surround ratio sat at 38 against a ceiling of 40, and this repo's
own rule is that a value at the end of its range means the range was wrong.

## What to decide

Either the two ranges are deliberately different — in which case say so in one
line, next to whichever is the derived one — or they are one quantity and should
share a bound. **Do not "align" them silently**: `forward`'s clamp feeds
`max_pool1d`'s kernel size, so changing it changes what the model computes and
moves every published number, which is the same trap
[the docstring correction](2026-08-27-the-model-does-not-do-what-its-docstring-says.md)
kept separate from its own prose fix.

Cheapest useful step is a guard rather than a decision: assert after fitting that
no centre width has reached either bound, so the question only has to be answered
on the day it stops being latent.
