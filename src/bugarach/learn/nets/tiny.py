"""tiny — one architecture, one file.

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

__all__ = ["build_tiny"]

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
