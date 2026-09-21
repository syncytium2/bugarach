---
status: open
filed: 2026-09-04
waiting: Whether the screen's control cell keeps `build_tube` or moves to `_build_tube_variant`.
---

# The control is a different code path, and it computes an identical result

> **Not murderboarded** — a planning note for sessions in this tree, same standing as
> [`four tubes`](2026-08-23-four-variants-of-the-tube.md), which it extends. If any of it
> reaches an outside reader, murderboard that artifact first.

## Why this file exists

Someone drew the four cells of the mechanism screen as architecture figures, which meant
counting the operations in each. The counts disagreed with the architecture: the guard
appeared to cost seven operations against the shipped tube and four against its own row.
Both counts are correct. They differ because **the no-guard subtract cell is not built by
the same function as the other three**, and the gap has nothing to do with either axis of
the screen.

This is not a threat to anything measured. It is a trap for anything *described*.

## What the guard actually costs

Traced with `torch.jit.trace` on torch 2.13.0, counting `aten::` operations in the
inlined graph, each model built from its own registered config:

| pair | total | operations added |
|---|---|---|
| `tube_ratio` → `tube_ratio_guard` | 63 → 67 | `abs`, `gt`, `mul`, `to` |
| `tube` → `tube_guard` | 55 → **62** | the same four, **plus `clamp_min` twice and a second `unsqueeze`** |

The first row is the guard, isolated against a cell that shares its builder: **four
operations**, which is the mask, the comparison, the cast and the multiply. The second row
is the guard plus three operations that are not the guard.

## Where the extra three come from

`build_tube` constructs its kernel in `_kernels`; the three variants construct theirs in
`_build_tube_variant`'s `_centre_surround`. The second one floors both normalisation sums
with `clamp_min(eps)`, returns the two kernels separately so each gets its own
`unsqueeze`, and leaves the `gain` multiply to `forward` instead of folding it into the
kernel.

**None of those change the number the model computes**, and that is measured rather than
argued. Loading the shipped tube's parameters into the subtract-mode variant with the
guard turned off — every parameter name shared, nothing missing, nothing unexpected — and
running both over the same random binary raster:

```
max |shipped − twin| = 0.0
```

Bit-identical. Convolution is linear, so scaling the kernel and scaling the response are
the same operation; and a sum of Gaussians never reaches `eps`, so the floors never bite.
**The re-expression is not a re-expression. It is the same function.**

## What this puts at risk, and what it does not

**Safe:** every performance number the screen produces. The four cells compute what they
are supposed to compute, and the control computes exactly what the shipped model computes.
Nothing about the comparison is invalidated.

**Wrong the moment it is written down:** any sentence or figure that reports the guard's
cost by differencing the shipped tube against `tube_guard`. That reads seven and the
answer is four. A caption saying *"the guard adds seven operations"* would be a false
statement derived from two true counts, which is the shape this repo keeps catching.

## The decision this makes available

[`four tubes`](2026-08-23-four-variants-of-the-tube.md) settles on `tube` itself as the
control, and `_build_tube_variant` defends that in terms: *"the control has to be the
shipped model, not a re-expression of it."* That reason was sound when it was written and
the measurement above answers it — **the variant builder at `mode="subtract",
guard_frames=0` is the shipped model**, to the last bit, not a re-expression of it.

So the screen can build all four cells from one function and lose nothing it was
protecting. The alternative is to keep the shipped model as the control and require every
artifact that counts operations to difference within a row rather than across the screen.
Either is defensible; what is not defensible is leaving it undecided while figures of the
four cells are being drawn.

## Reproduce

Both tables, self-contained — no draughtsman, no committed graph:

```python
import torch
from collections import Counter
from bugarach.learn.nets import ARCHITECTURES

def kinds(name):
    a = ARCHITECTURES[name]
    m = a.build(**a.cfg).eval()
    g = torch.jit.trace(m, torch.zeros(1, 30, 600)).inlined_graph
    return Counter(n.kind() for n in g.nodes() if n.kind().startswith("aten::"))

for a, b in (("tube_ratio", "tube_ratio_guard"), ("tube", "tube_guard")):
    x, y = kinds(a), kinds(b)
    print(a, "->", b, sum(x.values()), "->", sum(y.values()),
          {k: (x[k], y[k]) for k in sorted(set(x) | set(y)) if x[k] != y[k]})

guard = ARCHITECTURES["tube_guard"]
twin = guard.build(**{**guard.cfg, "guard_frames": 0}).eval()
shipped = ARCHITECTURES["tube"].build(**ARCHITECTURES["tube"].cfg).eval()
print(twin.load_state_dict(shipped.state_dict(), strict=False))    # both lists empty

torch.manual_seed(0)
x = (torch.rand(4, 30, 600) < 0.02).float()
with torch.no_grad():
    print("max |shipped - twin| =", (shipped(x) - twin(x)).abs().max().item())
```

**A registered builder cannot be called bare.** `build_tube_guard()` raises — `mode` and
`guard_frames` live in the `@register` config, not in the signature's defaults, so
anything that instantiates an architecture by importing its builder has to go through
`ARCHITECTURES[name].cfg`. That is what the snippet does, and it is worth knowing before
pointing an external tracer at one of these.
