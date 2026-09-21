"""gauge — one architecture, one file.

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

__all__ = ["build_gauge"]


@register("gauge", note="SIMULATION ONLY; false alarms climb on quiet fields "
                        "(docs/learned/field_size_candidates). B -- the same centre-surround as `tube`, "
                        "standardised against a null built by shifting the "
                        "recording's own cells; no bypass",
          n_scales=4, width=8, depth=6, max_center_frames=128, max_ratio=40.0,
          n_null=8, eps=1e-6)
def build_gauge(*, n_scales=4, width=8, depth=6, max_center_frames=128,
                max_ratio=40.0, n_null=8, eps=1e-6):
    """Measure the window against a null made from the window.

    **The evidence this is built on.** CoactDetect scores 0.790 refitted on the
    Cossart lab's 566-cell field and **0.789 carried over unchanged** from a fit on
    this lab's 32-cell one, on 107 of 120 planted events. That gap of 0.001 is not a
    property of its statistic — its statistic is a coactivity count, the same
    quantity ``tube`` reads. It is a property of its **bar**, which is a percentile
    of a null built by circularly shifting that recording's own cells. The
    hand-written detectors that travel are the ones whose bar is computed from the
    recording being judged; the two that do not travel carry an absolute threshold,
    and rate+context finds 120 of 120 planted events on that field while scoring
    0.168, because a bar that is right for 32 cells is tripped constantly by 566.

    So the single change here is to stop treating calibration as something done to a
    model after it is fitted, and make it a layer inside the model.

    **What the layer does.** The feature stage — identical to ``tube``'s, so the
    comparison is exact — runs on the window and on ``n_null`` surrogate copies in
    which every cell's row is rolled by its own offset. What leaves the layer is the
    observation in units of its own null::

        z = (observed - null mean) / (null spread + eps)

    Everything downstream reads a **pivotal** quantity: its null distribution does
    not move with the field size, the background rate or the sampling interval. That
    is the term the tube screen identified and did not act on — area-normalised
    subtraction "cancels the MEAN of a rate change and not its VARIANCE". The guard
    moved where the reference is measured; the ratio changed how the comparison is
    formed; neither divided by the null's spread.

    **THE BYPASS IS GONE, deliberately.** ``tube`` sends the pooled brightness to the
    head on its own channel, so the absolute activity level the kernel exists to
    cancel reaches the head anyway. Keeping it here would defeat the whole layer.
    Dropping it is also a filed experiment in its own right — item 4 of the
    2026-08-16 learned-detector handoff — so **a score from this model confounds two
    changes** until ``tube`` is re-run without its bypass. Say so with any number.

    **The shift is deterministic, not drawn.** Row *i* of null draw *k* is rolled by
    ``floor(T * frac((i + 1) * phase[k]))`` samples, where ``phase[k]`` is the
    fractional part of the square root of the *k*-th prime, held in a fixed buffer.
    Three reasons for no RNG: a forward pass with no RNG in it is reproducible, which
    every number in this project needs; ``torch.jit.trace`` bakes a sampled value into
    the graph and would make the architecture figure a drawing of one draw; and a
    per-row shift destroys alignment ACROSS cells while leaving each cell's own
    intervals exactly as they were, apart from the one wrap point.

    ⚠ **The first build used integer strides, ``(i + 1) * stride[k]`` with strides
    7, 13, 23 and up, and they were too small.** Adjacent rows moved only 7 frames
    apart in the first draw, inside the 9-frame widening, so that draw left 6.25 % of
    cell pairs still aligned at 32 cells on a 4,096-frame crop, 15 times the chance
    share. Irrational phases scatter every pair across the whole crop in every draw.

    ⚠ **Relabelling the cells still moves the output slightly**, because the shift a
    cell receives is set by its row. Exact invariance is out of reach for a finite,
    deterministic shift null: making the shift a function of the cell's own onsets
    would give two cells that fire only in the same event the same shift, which keeps
    the coordination inside the null. ``encode`` fixes the row order before this model
    sees it, so in use the order is canonical rather than arbitrary.

    ⚠ **This inherits the surrogate problem, whole.** A per-cell circular shift is the
    construction this project has spent weeks finding leaks in, and the rigid-shift
    work has already shown a shift can leak through shared modulation and through what
    happens at a window edge. **The null here must clear the same leak screen as any
    training surrogate before this layer is trusted.** One thing does differ: this is a
    calibration reference inside a supervised model rather than a training negative, so
    a leak biases the bar rather than manufacturing a learning signal out of nothing.
    That is a smaller failure, not an absent one.

    ⚠ **Cost is the open question**: ``n_null`` + 1 passes through the feature stage.
    ``tube`` scans a held-out fold in 0.014 s. Measure this before believing anything
    about it.
    """
    torch = _torch()
    nn = torch.nn
    import math

    class Gauge(nn.Module):
        def __init__(self):
            super().__init__()
            self.k = int(max_center_frames)
            self.n_null = int(n_null)
            init = [math.log(1.0 * (2 ** i)) for i in range(n_scales)]
            self.log_center = nn.Parameter(torch.tensor(init))
            self.log_ratio = nn.Parameter(torch.full((n_scales,), math.log(8.0)))
            self.gain = nn.Parameter(torch.ones(n_scales))
            # One irrational phase per draw, so the relative shift between two rows
            # differs from draw to draw and no pair stays close in all of them. A
            # buffer, not a parameter: the null is a fixed reference class, and a
            # fitted null would be a model that can move its own bar.
            primes = [2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37][:self.n_null]
            self.register_buffer("phase",
                                 torch.tensor([math.sqrt(q) % 1.0 for q in primes],
                                              dtype=torch.float32))
            self.head = _dilated_stack(nn, n_scales, 1, width, depth)

        def _kernels(self, device):
            """``tube``'s bank, unchanged, so the only difference is the layer below."""
            t = torch.arange(-self.k, self.k + 1, device=device,
                             dtype=torch.float32).view(1, -1)
            c = torch.exp(self.log_center).clamp(0.5, self.k / 2).view(-1, 1)
            s = c * torch.exp(self.log_ratio).clamp(1.5, max_ratio).view(-1, 1)
            centre = torch.exp(-0.5 * (t / c) ** 2)
            surround = torch.exp(-0.5 * (t / s) ** 2)
            centre = centre / centre.sum(dim=1, keepdim=True)
            surround = surround / surround.sum(dim=1, keepdim=True)
            return ((centre - surround) * self.gain.view(-1, 1)).unsqueeze(1)

        def _feature(self, x, kern):
            """``tube``'s first three stages: widen, mean over cells, the bank."""
            b, n, t = x.shape
            kmin = int(torch.exp(self.log_center.detach()).min().clamp(1, self.k))
            pooled = torch.nn.functional.max_pool1d(
                x.reshape(b * n, 1, t), kernel_size=2 * kmin + 1,
                stride=1, padding=kmin).reshape(b, n, t)
            bright = pooled.sum(dim=1, keepdim=True) / max(n, 1)
            return torch.nn.functional.conv1d(bright, kern, padding=self.k)

        def _shifted(self, x):
            """Every cell rolled by its own amount, for each null draw at once.

            One gather rather than a Python loop, so the traced graph carries one
            stage with a lane count instead of ``n_null`` unrolled copies.
            """
            b, n, t = x.shape
            # float64 on the CPU: at 1,050 rows a float32 product loses about three
            # frames of shift across a long recording.
            rows = torch.arange(1, n + 1, dtype=torch.float64).view(1, n, 1)
            phase = self.phase.detach().to("cpu", torch.float64).view(-1, 1, 1)
            shift = torch.floor(t * torch.remainder(rows * phase, 1.0))
            shift = shift.to(device=x.device, dtype=torch.long)  # (n_null, n, 1)
            frames = torch.arange(t, device=x.device).view(1, 1, t)
            idx = (frames - shift) % t                          # (n_null, n, T)
            idx = idx.unsqueeze(0).expand(b, -1, -1, -1)
            xs = x.unsqueeze(1).expand(b, self.n_null, n, t)
            return xs.gather(3, idx).reshape(b * self.n_null, n, t)

        def forward(self, x):                       # (B, n_roi, T)
            b, n, t = x.shape
            kern = self._kernels(x.device)
            obs = self._feature(x, kern)                        # (B, n_scales, T)
            null = self._feature(self._shifted(x), kern)
            null = null.reshape(b, self.n_null, -1, t)
            mu = null.mean(dim=1)
            sd = null.std(dim=1, unbiased=False)
            z = (obs - mu) / (sd + eps)
            # No bypass. Nothing un-normalised reaches the head, which is the point.
            return self.head(z).squeeze(1)

    return Gauge()
