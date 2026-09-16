"""quorum — one architecture, one file.

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

__all__ = ["build_quorum"]


@register("quorum", note="UNTRAINED, UNSCORED. C -- scores each cell against its own rate, "
                         "then reads an order statistic over cells whose depth "
                         "grows as a FITTED power of the field size",
          occupancy_frames=601, head_width=8, head_depth=8, init_exponent=0.5,
          init_coefficient=0.5, temperature=1.0, eps=1e-6)
def build_quorum(*, occupancy_frames=601, head_width=8, head_depth=8,
                 init_exponent=0.5, init_coefficient=0.5, temperature=1.0,
                 eps=1e-6):
    """How deep into the population does the co-firing reach?

    **Why neither rule on offer is right.** Under an independent-cell null at one
    chance frame per hour, the smallest co-active count that is not chance grows
    **sub-linearly** with the field: 3 cells at 32, 6 at 566, 7 at 1,050 on this
    lab's median rate. A **fixed count** set at 32 cells fires 334x over budget at
    566. A **fixed fraction** set there demands 54 cells, whose chance probability is
    6e-89 of the budget, and at 9 cells the same fraction rounds to one cell and
    fires 242x over. The honest rule lies strictly between them
    (``tools/probe_field_size.py``; the numbers are in
    ``docs/learned/field_size.json``).

    So the depth of the pool is a **power of the field size with a fitted
    exponent**::

        m = coefficient * n_roi ** exponent

    ``exponent = 0`` is a fixed count and ``exponent = 1`` is a fixed fraction, so
    the two rules are the endpoints of the one free parameter rather than a choice
    made in advance. ⚠ **Report the fitted exponent with its bounds every time.**
    ``tube``'s own rule applies: a fitted value that runs to the end of its range is
    the model saying the range was wrong — and here, a value at 0 or 1 says one of
    the two rules was right after all, which is a result worth having either way.

    **Why the cells are scored against themselves first.** Per-cell rate
    heterogeneity is the one nuisance nothing in the estate touches; rate-sorted rows
    are the only acknowledgement anywhere, and ``tube`` discards that order at its
    mean. Here each onset is weighted by the surprise of its own cell —
    ``-log`` of that cell's occupancy over a long trailing window — so a busy cell's
    onset is worth less than a quiet cell's. The decision variable is then a rank
    over the population, and a rank's null does not care how the rates are
    distributed.

    **Why the cell axis and not the time axis.** This is ordered-statistic
    constant-false-alarm-rate detection, and it was on the list once already: V3 of
    the tube screen, the censored surround, deliberately left out because an order
    statistic over a sliding TIME window is not a convolution and spends the one
    property ``tube`` owns — 0.014 s to scan a fold. Over the **cell** axis the cost
    is a different shape: a sort of ``n_roi`` values per frame, which is one kernel.
    That distinction is the reason this is worth running where V3 was not.

    ⚠ **The pool is SOFT, and it has to be.** A hard ``topk`` needs an integer depth,
    and deriving that integer from a trained parameter is exactly the hazard
    ``tube``'s max-pool fell into — a Python value baked out of a tensor, which
    freezes an initialisation into the graph and into every figure drawn from it.
    Here the sorted scores are weighted by ``sigmoid((m - rank) / temperature)``, so
    ``m`` stays a tensor, the gradient reaches the exponent, and nothing is baked.
    ``temperature`` is how sharply the quorum ends; it is a configuration value
    rather than a fitted one, so the screen compares models that share it.
    """
    torch = _torch()
    nn = torch.nn

    class Quorum(nn.Module):
        def __init__(self):
            super().__init__()
            self.w = int(occupancy_frames) | 1          # odd, so padding is symmetric
            self.temp = float(temperature)
            self.log_coefficient = nn.Parameter(
                torch.tensor(float(init_coefficient)).log())
            self.raw_exponent = nn.Parameter(torch.tensor(float(init_exponent)))
            # two channels: the quorum's own surprise, and the whole field's
            self.head = _dilated_stack(nn, 2, 1, head_width, head_depth)

        def exponent(self):
            """Clamped to the two rules it interpolates. Read this after a fit."""
            return self.raw_exponent.clamp(0.0, 1.0)

        def forward(self, x):                       # (B, n_roi, T)
            b, n, t = x.shape
            # --- each cell against its own rate --------------------------------
            occ = torch.nn.functional.avg_pool1d(
                x.reshape(b * n, 1, t), kernel_size=self.w, stride=1,
                padding=self.w // 2, count_include_pad=False).reshape(b, n, t)
            surprise = x * -(occ.clamp_min(eps).log())

            # --- an order statistic over CELLS ---------------------------------
            srt, _ = surprise.sort(dim=1, descending=True)
            rank = torch.arange(1, n + 1, device=x.device,
                                dtype=srt.dtype).view(1, n, 1)
            m = torch.exp(self.log_coefficient) * float(n) ** self.exponent()
            w = torch.sigmoid((m - rank) / self.temp)
            quorum = (srt * w).sum(dim=1, keepdim=True) / w.sum().clamp_min(eps)

            field = surprise.mean(dim=1, keepdim=True)
            return self.head(torch.cat([quorum, field], dim=1)).squeeze(1)

    return Quorum()
