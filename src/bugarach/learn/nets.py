"""Architectures, and the registry that makes adding one cheap.

A new architecture is **one class plus one ``@register`` line**. It is then
trained on the same data, scored by the same scorer, and placed on the same
performance-vs-mass curve as everything already here, with nothing else edited.
That was the requirement: *if we decide a new architecture is needed, it can be
slotted in and trained and evaluated on the others we build now.*

torch is an optional extra (``pip install -e ".[dl]"``). Nothing in
:mod:`bugarach.learn.encode` imports it, so the measurement half of the package
works without it.

The one structural commitment
-----------------------------
**One ROI, one vote.** Coactivity is distinct active ROIs, never a spike count
(GLOSSARY), and every one of the six detectors enforces it. Reduce over ROIs
*before* smoothing over time and that is destroyed: one busy ROI firing
repeatedly becomes indistinguishable from several ROIs firing together — the
exact false coordination a ``min_rois`` floor exists to reject. Sorting rows by
rate makes it worse, because it puts every busiest ROI in the same place.

So the ROI axis survives the temporal filter, and each ROI's contribution is
**bounded before pooling**:

    (n_roi, T)  rows rate-sorted
        -> shared temporal filter, applied per ROI    (learns its own width)
        -> bounded activation                          <- one ROI, one vote
        -> pooled within rate quantiles                (distinctness preserved)
        -> temporal head -> per-frame logit

⚠ The bound is **soft**, not exact. An exact "any event in this window" needs a
fixed window, which is the assumption the whole design refuses to make — the
smear must be learned, not handed over. A sigmoid lets the model choose its own
window and pays for it with approximate distinctness. That trade is the thing to
probe behaviourally, not to assert.

Nothing here knows what a second is. Receptive fields are in samples.
"""

from __future__ import annotations

from dataclasses import dataclass, field

ARCHITECTURES: dict[str, "Arch"] = {}


@dataclass(frozen=True)
class Arch:
    """One registered architecture: how to build it, and what it costs."""

    name: str
    build: object
    """``build(n_rate_quantiles=..., **cfg) -> torch.nn.Module``."""
    cfg: dict = field(default_factory=dict)
    note: str = ""

    def make(self, **over):
        return self.build(**{**self.cfg, **over})


def register(name: str, note: str = "", **cfg):
    """Add an architecture to the sweep. One line per architecture, by design."""
    def deco(fn):
        ARCHITECTURES[name] = Arch(name=name, build=fn, cfg=cfg, note=note)
        return fn
    return deco


def n_params(model) -> int:
    """Trainable parameter count — the mass axis."""
    return int(sum(p.numel() for p in model.parameters() if p.requires_grad))


def _torch():
    try:
        import torch
        return torch
    except ImportError as exc:                                  # pragma: no cover
        raise ImportError(
            "bugarach.learn.nets needs torch — install the optional extra:\n"
            '    pip install -e ".[dl]"') from exc


def _dilated_stack(nn, c_in, c_out, width, depth):
    """Dilated causal-free conv stack. Dilation doubles per layer, so the
    receptive field grows exponentially in depth — which is how a small model
    reaches the ~1000 samples it needs to judge activity against its own local
    background without being told what that background is."""
    layers = []
    c = c_in
    for i in range(depth):
        d = 2 ** i
        layers += [nn.Conv1d(c, width, kernel_size=3, dilation=d, padding=d),
                   nn.GELU()]
        c = width
    layers += [nn.Conv1d(c, c_out, kernel_size=1)]
    return nn.Sequential(*layers)


def receptive_field(depth: int) -> int:
    """Samples visible to a stack of the given depth. Reported, not assumed —
    a model whose receptive field is shorter than the background it must judge
    against cannot be rate-invariant however it is trained."""
    return 1 + 2 * sum(2 ** i for i in range(depth))


@register("tiny", note="per-ROI filter, bounded vote, rate-quantile pooling",
          roi_width=4, roi_depth=4, head_width=8, head_depth=10,
          n_rate_quantiles=4)
def build_tiny(*, roi_width=4, roi_depth=4, head_width=8, head_depth=10,
               n_rate_quantiles=4):
    torch = _torch()
    nn = torch.nn

    class Tiny(nn.Module):
        """The smallest thing that can honour distinctness.

        ``n_rate_quantiles`` is the ROI-resolution knob, and it is the interesting
        half of the mass axis: 1 pools every ROI together and is exactly the
        coactivity trace the six detectors threshold; larger values keep bands of
        the rate distribution apart. If 1 scores as well as 32, rate-band
        structure does not matter and the cheap model is the right one — a real
        result either way.
        """

        def __init__(self):
            super().__init__()
            self.q = int(n_rate_quantiles)
            self.roi = _dilated_stack(nn, 1, roi_width, roi_width, roi_depth)
            self.head = _dilated_stack(nn, roi_width * self.q, 1,
                                       head_width, head_depth)

        def forward(self, x):                     # x: (B, n_roi, T)
            b, n, t = x.shape
            h = self.roi(x.reshape(b * n, 1, t))  # shared weights, per ROI
            h = torch.sigmoid(h)                  # <- one ROI, one vote (soft)
            h = h.reshape(b, n, -1, t)

            # Rows arrive rate-sorted, so a contiguous split of the ROI axis IS a
            # split by rate quantile. Uneven splits are fine and expected: a
            # recording's ROI count is not a multiple of anything.
            idx = [int(round(i * n / self.q)) for i in range(self.q + 1)]
            pooled = [h[:, idx[i]:max(idx[i] + 1, idx[i + 1])].sum(dim=1)
                      for i in range(self.q)]
            z = torch.cat(pooled, dim=1)          # (B, q*roi_width, T)
            return self.head(z).squeeze(1)        # (B, T) logits

    return Tiny()


@register("trace", note="pools ROIs first — the cheap baseline that gives up "
                        "distinctness, and the control for whether it matters",
          head_width=8, head_depth=11)
def build_trace(*, head_width=8, head_depth=11):
    """Collapse the ROI axis immediately, then filter in time.

    Deliberately the thing the design argues against: pooling before the temporal
    filter means a busy ROI bursting alone can masquerade as coordination. It is
    here as a **control** — if it matches ``tiny``, the distinctness machinery is
    not earning its compute on this data, and that is worth knowing.
    """
    torch = _torch()
    nn = torch.nn

    class Trace(nn.Module):
        def __init__(self):
            super().__init__()
            self.head = _dilated_stack(nn, 2, 1, head_width, head_depth)

        def forward(self, x):                     # (B, n_roi, T)
            n = x.shape[1]
            frac = x.sum(dim=1, keepdim=True) / max(n, 1)
            import math
            scale = torch.full_like(frac, math.log(max(n, 1)) / 5.0)
            return self.head(torch.cat([frac, scale], dim=1)).squeeze(1)

    return Trace()
