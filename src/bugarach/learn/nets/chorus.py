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
def build_chorus(*, roi_width=4, roi_depth=4, head_width=8, head_depth=8, top_m=4,
                 input_gain=None, norm=False, vote_gain=None, eps=1e-6, participation=False):
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

    ⚠ **As built above, the per-cell encoder starts deaf and never trains**
    (``docs/learned/field_size_candidates/why_chorus.txt``): one onset moves a vote by
    at most 0.0003 at initialisation, and the encoder's gradient is about 270,000
    times smaller than the head's. Three options, each off by default so ``chorus``
    itself is unchanged and stays the failed control:

    * ``input_gain`` -- a learnable gain on the raster before the encoder, started at
      this value, so an onset dominates the convolutions' biases instead of vanishing
      under them (``chorus_gain``).
    * ``norm`` -- each cell's encoder output standardised over time, channel by
      channel, before the vote; a cell with no onsets in the window comes out 0
      (``chorus_norm``). The statistics are taken over whatever window the model is
      given, so a 4,096-frame training crop and a whole recording at inference are
      standardised over different spans.
    * ``vote_gain`` -- ``line``'s vote on the standardised output,
      ``sigmoid(gain * (z - bias))`` with a learnable gain started at this value and a
      learnable bias started at 0.5 (``chorus_gain_norm``, with ``norm``).

    ``participation`` (off by default; ADR-0010 part 5, the ``*_part`` variants) adds a
    per-cell vote -- a 1x1 convolution over the cell's ``roi_width`` bounded channels, then a
    sigmoid -- whose **sum over cells** is a count in [0, n_roi], and hands the head that
    count and the recording's floor (``bugarach.learn.participation.count_features``). The
    model then needs ``forward(x, floor=...)``; ``return_votes=True`` also returns the votes,
    which the membership loss trains. Off, nothing is built and nothing moves.
    """
    torch = _torch()
    nn = torch.nn

    import math

    from bugarach.learn import participation as part

    class Chorus(nn.Module):
        def __init__(self):
            super().__init__()
            self.m = int(top_m)
            self.norm = bool(norm)
            self.roi = _dilated_stack(nn, 1, roi_width, roi_width, roi_depth)
            if input_gain is not None:
                self.log_input_gain = nn.Parameter(
                    torch.tensor(math.log(float(input_gain))))
            if vote_gain is not None:
                self.vote_gain = nn.Parameter(torch.full((roi_width,), float(vote_gain)))
                self.vote_bias = nn.Parameter(torch.full((roi_width,), 0.5))
            # three pooled statistics, each `roi_width` channels wide
            self.reads_floor = bool(participation)
            self.head = _dilated_stack(nn, 3 * roi_width + (3 if participation else 0), 1,
                                       head_width, head_depth)
            if participation:
                self.vote_head = part.vote_head(nn, roi_width)

        def forward(self, x, floor=None, return_votes=False):     # (B, n_roi, T)
            b, n, t = x.shape
            xr = x.reshape(b * n, 1, t)
            if input_gain is not None:
                xr = xr * torch.exp(self.log_input_gain)
            h = self.roi(xr)
            if self.norm:
                h = (h - h.mean(dim=2, keepdim=True)) / (
                    h.std(dim=2, keepdim=True, unbiased=False) + eps)
            if vote_gain is not None:
                h = torch.sigmoid(self.vote_gain.view(1, -1, 1)
                                  * (h - self.vote_bias.view(1, -1, 1)))
            else:
                h = torch.sigmoid(h)                # <- one cell, one vote (soft)
            votes = None
            if self.reads_floor:
                # ADR-0010 part 5: one bounded vote per cell, so their sum is a count.
                votes = torch.sigmoid(self.vote_head(h)).reshape(b, n, t)
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
            if not self.reads_floor:
                return self.head(z).squeeze(1)
            fl = part.floor_tensor(floor, b, x.device)
            z = torch.cat([z, part.count_features(votes.sum(dim=1), fl)], dim=1)
            out = self.head(z).squeeze(1)
            return (out, votes) if return_votes else out

    return Chorus()
