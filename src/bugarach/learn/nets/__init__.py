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


# ---------------------------------------------------------------------------
# EVERY MODULE IN THIS FOLDER IS IMPORTED, so `@register` fires and the registry
# is whatever the folder contains. There is deliberately no list of architecture
# names here: a list is a second place to edit, and the one thing this layout is
# for is that adding a file is the whole of adding an architecture.
#
# Import errors are NOT swallowed. An architecture that fails to import is a
# broken architecture, and a registry that quietly skips it would report a
# smaller model set as if that were the truth — the same "a finding and a bug
# must not look alike" rule the run.json roster is built on.
#
# The import is at the bottom because the submodules import `register`,
# `_torch`, `_dilated_stack` and `receptive_field` from this module: they must
# exist before anything is loaded.
import pkgutil as _pkgutil
from importlib import import_module as _import_module

for _m in sorted(m.name for m in _pkgutil.iter_modules(__path__)):
    _mod = _import_module(f"{__name__}.{_m}")
    # Re-export the builder so `from bugarach.learn.nets import build_tube`
    # keeps working — several call sites and one test import them directly.
    for _n in getattr(_mod, "__all__", ()):
        globals()[_n] = getattr(_mod, _n)
del _pkgutil, _import_module, _m, _mod, _n
