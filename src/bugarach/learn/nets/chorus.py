"""chorus — one architecture, one file.

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

__all__ = ["build_chorus"]


@register("chorus", note="DOES NOT TRAIN: its per-cell encoder starts deaf (docs/learned/field_size_candidates/why_chorus.txt). A -- keeps the cell axis until after the "
                         "temporal filter, then pools it into several symmetric "
                         "statistics instead of one sum",
          roi_width=4, roi_depth=4, head_width=8, head_depth=8, top_m=4)
def build_chorus(*, roi_width=4, roi_depth=4, head_width=8, head_depth=8, top_m=4):
    """Filter every cell, bound its vote, and pool the field into its SHAPE.

    ``tube`` averages the cell axis away in its second stage and everything after
    that reads one trace whose value is the fraction of the field that is active.
    A fraction runs at any cell count and is calibrated at none: the same number
    means three cells out of thirty and fifty-seven out of five hundred and sixty-six.

    This is the standard answer to that, and it is not a new idea — a shared
    per-element encoder, a symmetric pool, a decoder on the pool is the Deep Sets
    shape (Zaheer and colleagues, 2017; Qi and colleagues, PointNet, 2017), and
    ``tube``'s mean over cells is its degenerate member: one element feature, one
    pooling function, and the pooling applied before any element encoder exists.

    **Three symmetric statistics, not one.** The pool returns the mean of the
    bounded per-cell votes, their spread, and the mean of the loudest ``top_m``.
    All three have the same expectation at nine cells and at a thousand; what
    changes with the field is their sampling error, not their level. A sum does not
    have that property, which is the defect of ``tiny``'s rate-band pooling.

    ⚠ **THIS IS THE FAMILY ``tiny`` ALREADY FAILED IN, and that is the first thing
    to know about it.** ``tiny`` is a per-cell filter, a bounded vote and a pool by
    rate band, and it scored F1 0.125 in every published run with its threshold on
    the edge of its grid in four folds of four. Three things differ here and none of
    them has been measured: ``tiny`` pools with an unbounded **sum** within each
    band, which puts a count leak straight back; it was fitted at a tenth of
    ``tube``'s learning rate, so the architecture comparison was never controlled;
    and it normalises nothing at the pool. **Re-run ``tiny`` under control before
    reading anything into this model's score** — that is one run and it decides
    whether the class is alive.

    ⚠ ``top_m`` is a **fixed count** here on purpose. Letting the pool depth grow
    with the field is a different mechanism and it is ``quorum``'s; crossing the two
    before either is measured would repeat the mistake the tube screen names in its
    own text.
    """
    torch = _torch()
    nn = torch.nn

    class Chorus(nn.Module):
        def __init__(self):
            super().__init__()
            self.m = int(top_m)
            self.roi = _dilated_stack(nn, 1, roi_width, roi_width, roi_depth)
            # three pooled statistics, each `roi_width` channels wide
            self.head = _dilated_stack(nn, 3 * roi_width, 1, head_width, head_depth)

        def forward(self, x):                       # (B, n_roi, T)
            b, n, t = x.shape
            h = self.roi(x.reshape(b * n, 1, t))
            h = torch.sigmoid(h)                    # <- one cell, one vote (soft)
            h = h.reshape(b, n, -1, t)

            # The pool. Every one of these is symmetric in the cell axis, so the
            # model never sees which cell is which, and every one has the same
            # expectation whatever the field size.
            mean = h.mean(dim=1)
            # unbiased=False, because a one-cell field is legal input and the
            # unbiased estimator is not defined there — a NaN in the forward pass
            # would be a crash blamed on the data rather than on this line.
            spread = h.std(dim=1, unbiased=False)
            # Sort and slice rather than `topk(min(self.m, n))`. `min` against a
            # traced shape converts a tensor to a Python value, which is the hazard
            # draughtsman refuses to let a figure quote and the one `tube`'s max-pool
            # fell into; a slice past the end simply returns what is there, so a
            # field smaller than `top_m` needs no special case either.
            srt, _ = h.sort(dim=1, descending=True)
            top = srt[:, :self.m].mean(dim=1)

            z = torch.cat([mean, spread, top], dim=1)   # (B, 3*roi_width, T)
            return self.head(z).squeeze(1)

    return Chorus()
