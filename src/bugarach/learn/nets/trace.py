"""trace — one architecture, one file.

ONE FILE IS ONE ARCHITECTURE. Drop a module in this folder with a ``@register``
line and it appears everywhere the registry is read — the bake-off, the lab
server's ``/api/capabilities``, the browser's model picker — with nothing else
edited. Delete the file and it is gone. That is what "added and removed at will"
has to mean to be worth saying (ADR-0005).

``nets/__init__.py`` imports every module in this folder at import time, so
registration is automatic; there is no list of architectures anywhere to fall
behind. Shared machinery — ``register``, ``_torch``, ``_dilated_stack``,
``receptive_field`` — lives there and is imported from there.
"""

from bugarach.learn.nets import _dilated_stack, _torch, receptive_field, register

__all__ = ["build_trace"]

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
