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


@register("tube", note="center-surround on the brightness trace — Tony's tube, "
                       "2026-08-16: a DC-free kernel, with a raw-brightness "
                       "bypass the kernel does not reach",
          n_scales=4, width=8, depth=6, max_center_frames=128, max_ratio=40.0)
def build_tube(*, n_scales=4, width=8, depth=6, max_center_frames=128,
               max_ratio=40.0):
    """Look down a tube as the recording slides past.

    The tube is dark; onsets are specks. When several cells fire together a bright
    spot crosses the centre. Jitter dims it. A busier background raises the whole
    field, but a real spot still stands above its own surround.

    That last sentence is the architecture. **The KERNEL makes rate invariance
    structural**: it is a difference of Gaussians, area-normalised so a flat field
    integrates to zero, so a uniform rate change cancels rather than merely
    shrinking. It is what every one of the six detectors computes by hand —
    observed minus context — and what `tiny` spends a 2 000-sample receptive field
    *hoping* to discover.

    ⚠ **That is a property of the kernel and not of this model**, and the
    difference is one line of ``forward``::

        self.head(torch.cat([bright, resp], dim=1))

    ``bright`` is the pooled brightness itself — an absolute local activity level —
    and it reaches the head on its own channel, beside the zero-integral responses.
    Whatever the kernel cancels, that channel carries through, so the model is free
    to learn the rate dependence the kernel was built to remove. Whether it should
    keep that channel is an open experiment rather than a defect to paper over:
    item 4 of `docs/todo/2026-08-16-learned-detectors-handoff.md` is *"drop the raw
    brightness channel and re-run"*, and doing so moves every published number.
    **No magnitude is quoted here, deliberately** — three probes on three training
    runs put the effect an order of magnitude apart, and one was not monotonic in
    the background rate at all. One training run per seed is the standing
    limitation of everything learned in this project, and it bites hardest here.

    Two properties fall out rather than being enforced, and a third does not:

    * **space invariance** — cells are summed, so the model never sees which cell
      is which and runs at any cell count. Tony's phrase for it.
    * **tightness is a learned kernel width** — the centre widths are free
      parameters, so how tight an event must be is fitted, not supplied.
    * ⚠ **distinctness is NOT delivered, and this docstring used to claim it was.**
      It said each cell was capped at one vote and that the cap was *"exact rather
      than soft"*, in explicit contrast to `tiny`. The contrast was the wrong way
      round. ``encode.Encoded.raster`` is already one-or-zero per (cell, frame) —
      *"several onsets in one frame stay 1"* — so the ``max_pool1d`` below runs on
      a binary signal and returns a binary signal. **It caps nothing.** What it
      does is *widen* each onset to ``2*kmin+1`` frames, which increases what a
      repeatedly firing cell contributes to the centre integral. Measured on a
      trained model at its own operating point: one cell bursting eight times
      scores 0.28 and stays silent, but **two** such cells score 0.997 and fire —
      level with four genuinely distinct cells at 0.998. Two bursting cells
      imitating a crowd is the exact false coordination this design exists to
      reject. Probe it behaviourally; do not assert it.

    ⚠ The centre widths are initialised across a geometric spread and then
    trained. The spread is a starting point, not the answer: if a fitted width
    runs to the end of its range the model is telling you the range was wrong.

    ``max_ratio`` caps how much wider the surround may be than the centre, and it
    is a **parameter rather than a constant** because a fit on the training data put one
    of the four ratios at 38 against a ceiling of 40 — which by the rule above is
    the search reporting that the range was wrong, not an answer. Raising it is
    how that gets tested; the default is the value everything published so far
    was fitted under, so nothing moves unless it is passed.
    """
    torch = _torch()
    nn = torch.nn
    import math

    class Tube(nn.Module):
        def __init__(self):
            super().__init__()
            self.k = int(max_center_frames)
            # **Start at one sample and let it zoom out.** Tony, 2026-08-16:
            # "the scaling can start with dt, 1 point. if the events are long
            # relative to dt the center surround zooms out." One sample is the
            # finest thing the recording can resolve, so it is the only
            # non-arbitrary place to begin — and because the width is a free
            # parameter, the FITTED value is the model's own estimate of how wide
            # an event is, in samples. Multiply by dt and it is directly
            # comparable to what the assessor measured. Stored as a log so it
            # stays positive under gradient descent.
            init = [math.log(1.0 * (2 ** i)) for i in range(n_scales)]
            self.log_center = nn.Parameter(torch.tensor(init))
            self.log_ratio = nn.Parameter(torch.full((n_scales,), math.log(8.0)))
            self.gain = nn.Parameter(torch.ones(n_scales))
            self.head = _dilated_stack(nn, n_scales + 1, 1, width, depth)

        def _kernels(self, device):
            """Difference of Gaussians, centre minus surround, area-normalised so
            a flat field integrates to zero — which is what makes a uniform rate
            change cancel instead of merely shrink."""
            t = torch.arange(-self.k, self.k + 1, device=device,
                             dtype=torch.float32).view(1, -1)
            c = torch.exp(self.log_center).clamp(0.5, self.k / 2).view(-1, 1)
            s = c * torch.exp(self.log_ratio).clamp(1.5, max_ratio).view(-1, 1)
            centre = torch.exp(-0.5 * (t / c) ** 2)
            surround = torch.exp(-0.5 * (t / s) ** 2)
            centre = centre / centre.sum(dim=1, keepdim=True)
            surround = surround / surround.sum(dim=1, keepdim=True)
            return ((centre - surround) * self.gain.view(-1, 1)).unsqueeze(1)

        def forward(self, x):                       # (B, n_roi, T)
            b, n, t = x.shape
            # --- widen each cell's onsets, which is NOT one cell one vote -----
            # This was written as "smooth each cell, then clamp -- exact, not a
            # soft cap". It is neither exact nor a cap. `x` is already binary, so
            # a max-pool over it returns a binary signal and bounds nothing; what
            # it does is WIDEN each onset to 2*kmin+1 frames, which increases a
            # bursting cell's contribution to the centre integral. Two cells
            # bursting reach the response of four distinct cells at the shipped
            # operating point. See the class docstring; do not restore the claim
            # without a probe that fails when it stops being true.
            #
            # ⚠ kmin is clamped to [1, k] HERE and each centre width is clamped to
            # [0.5, k/2] in `_kernels` -- two different bounds on the same fitted
            # quantity. They agree over the widths seen so far (~4-7 samples) and
            # would diverge at either extreme. Nothing says which is intended.
            kmin = int(torch.exp(self.log_center.detach()).min().clamp(1, self.k))
            pooled = torch.nn.functional.max_pool1d(
                x.reshape(b * n, 1, t), kernel_size=2 * kmin + 1,
                stride=1, padding=kmin).reshape(b, n, t)
            bright = pooled.sum(dim=1, keepdim=True) / max(n, 1)   # space invariant

            # --- centre-surround in time --------------------------------------
            resp = torch.nn.functional.conv1d(
                bright, self._kernels(x.device), padding=self.k)
            # ⚠ THE BYPASS. `bright` is an absolute activity level and it goes to
            # the head alongside the zero-integral responses, so the kernel's DC
            # invariance is not the model's. Removing this channel is a filed
            # experiment, not a tidy-up: it moves every published number.
            return self.head(torch.cat([bright, resp], dim=1)).squeeze(1)

    return Tube()


# ---------------------------------------------------------------------------------
# THE 2x2 MECHANISM SCREEN — the variants scoped in
# docs/todo/2026-08-23-four-variants-of-the-tube.md, built so they can be measured
# rather than argued about.
#
# WHAT THEY ARE AIMED AT. In the probe block, which contains nothing planted, the
# shipped tube fires 15.75 times on average against LoCo's 2.50 and CoactDetect's
# 1.25 -- six to thirteen times the two rate-LOCAL hand-written detectors. Two
# classical results in a network's clothing explain it, and each variant addresses
# one:
#
#   * the surround is maximal EXACTLY at the sample under test, so an event
#     contributes to the reference that judges it -> the GUARD (V1)
#   * area-normalised subtraction cancels the MEAN of a rate change and not its
#     VARIANCE, where CFAR divides -> the RATIO (V2)
#
# THEY ARE NOT A RACE, and the todo is explicit about why: on `rate` the guard paid
# only once the bar was multiplicative (0.667 -> 0.686), because a contaminated
# reference then multiplies into the threshold instead of adding a fixed offset.
# Evaluating them independently would repeat a mistake already made once. Hence a
# 2x2 over {subtract, ratio} x {no guard, guard}, with `tube` itself as the control
# cell -- re-measured in the same run rather than quoted from a previous one.
#
# V3 (censored surround) IS DELIBERATELY ABSENT. An order statistic over a sliding
# window is not a convolution, so it spends the one property the tube actually owns
# (0.014 s to scan a held-out fold). The todo says run it last, against a stated
# speed budget. It is not a variant to slip into an unattended run.
# ---------------------------------------------------------------------------------

def _build_tube_variant(*, mode: str, guard_frames: int, n_scales=4, width=8,
                        depth=6, max_center_frames=128, max_ratio=40.0,
                        eps: float = 1e-6):
    """The shipped tube with one or both mechanism changes applied.

    ``mode="subtract"`` reproduces :func:`build_tube`'s arithmetic; ``mode="ratio"``
    replaces centre-minus-surround with a **difference of logs**.

    WHY LOGS RATHER THAN A DIVIDE. The todo prescribes it, for three reasons that all
    matter here: there is no denominator to clamp, so the variant cannot quietly
    absorb the question it was added to answer -- ``model_track.md`` already records
    the existing surround clamp as "a wart, not a cause"; the operation stays a
    convolution followed by a pointwise map, which keeps the JS trainer's operation
    list closed; and the fitted ``gain`` already plays the role of CFAR's alpha, so no
    grid is needed. On `rate` the alpha optimum sat at 15-20 and a first grid topping
    out at 8 put it on the boundary -- a learned gain has no boundary to sit on.

    THE COST OF THE RATIO, STATED HERE RATHER THAN LEFT STANDING. ``build_tube``'s
    docstring says the kernel makes rate invariance *structural* because a difference
    of Gaussians area-normalises to zero. That sentence is about the **difference**.
    Under ``mode="ratio"`` the invariance holds for a different reason -- a common
    multiplicative factor cancels in a log difference -- and a correct-sounding
    justification over changed arithmetic is exactly what the todo warns against.

    THE GUARD. ``guard_frames`` zeroes the surround within +/-g of the sample under
    test and renormalises **after** masking, so the reference still integrates to one
    and only its support changes. Renormalising before would leave the guarded kernel
    with less than unit mass and confound a mechanism change with a gain change.

    The guard is a **fixed configuration value, not a fitted parameter**. It is an
    axis of the screen; letting it train would mean the 2x2 compared four models that
    had each chosen their own guard, which is a different experiment.
    """
    if mode not in ("subtract", "ratio"):
        raise ValueError(f"mode must be 'subtract' or 'ratio', not {mode!r}")

    torch = _torch()
    nn = torch.nn
    import math

    class TubeVariant(nn.Module):
        def __init__(self):
            super().__init__()
            self.k = int(max_center_frames)
            self.g = int(guard_frames)
            self.mode = mode
            init = [math.log(1.0 * (2 ** i)) for i in range(n_scales)]
            self.log_center = nn.Parameter(torch.tensor(init))
            self.log_ratio = nn.Parameter(torch.full((n_scales,), math.log(8.0)))
            self.gain = nn.Parameter(torch.ones(n_scales))
            self.head = _dilated_stack(nn, n_scales + 1, 1, width, depth)

        def _centre_surround(self, device):
            """The two kernels, each area-normalised, guard applied to the surround.

            Returned apart rather than differenced, because the ratio mode convolves
            them separately and both modes should read one construction.
            """
            t = torch.arange(-self.k, self.k + 1, device=device,
                             dtype=torch.float32).view(1, -1)
            c = torch.exp(self.log_center).clamp(0.5, self.k / 2).view(-1, 1)
            s = c * torch.exp(self.log_ratio).clamp(1.5, max_ratio).view(-1, 1)
            centre = torch.exp(-0.5 * (t / c) ** 2)
            surround = torch.exp(-0.5 * (t / s) ** 2)
            if self.g > 0:
                surround = surround * (t.abs() > self.g).to(surround.dtype)
            centre = centre / centre.sum(dim=1, keepdim=True).clamp_min(eps)
            surround = surround / surround.sum(dim=1, keepdim=True).clamp_min(eps)
            return centre.unsqueeze(1), surround.unsqueeze(1)

        def forward(self, x):                       # (B, n_roi, T)
            b, n, t = x.shape
            kmin = int(torch.exp(self.log_center.detach()).min().clamp(1, self.k))
            pooled = torch.nn.functional.max_pool1d(
                x.reshape(b * n, 1, t), kernel_size=2 * kmin + 1,
                stride=1, padding=kmin).reshape(b, n, t)
            bright = pooled.sum(dim=1, keepdim=True) / max(n, 1)

            ck, sk = self._centre_surround(x.device)
            gain = self.gain.view(1, -1, 1)
            if self.mode == "subtract":
                resp = torch.nn.functional.conv1d(
                    bright, (ck - sk), padding=self.k) * gain
            else:
                # Two convolutions, then a pointwise log difference. `bright` is a
                # non-negative rate and both kernels are non-negative and normalised,
                # so both responses are >= 0 and eps is the only guard needed.
                cr = torch.nn.functional.conv1d(bright, ck, padding=self.k)
                sr = torch.nn.functional.conv1d(bright, sk, padding=self.k)
                resp = (torch.log(cr.clamp_min(eps))
                        - torch.log(sr.clamp_min(eps))) * gain
            return self.head(torch.cat([bright, resp], dim=1)).squeeze(1)

    return TubeVariant()


# The 2x2's other three cells. `tube` itself is the fourth and is registered above,
# unchanged -- the control has to be the shipped model, not a re-expression of it.
@register("tube_guard", note="V1 -- centre minus GUARDED surround: the reference stops "
                             "abutting the sample it judges",
          mode="subtract", guard_frames=8, n_scales=4, width=8, depth=6,
          max_center_frames=128, max_ratio=40.0)
def build_tube_guard(**cfg):
    return _build_tube_variant(**cfg)


@register("tube_ratio", note="V2 -- log(centre) minus log(surround): divides where the "
                             "shipped tube subtracts; the one mechanism change with "
                             "positive evidence anywhere in this repo",
          mode="ratio", guard_frames=0, n_scales=4, width=8, depth=6,
          max_center_frames=128, max_ratio=40.0)
def build_tube_ratio(**cfg):
    return _build_tube_variant(**cfg)


@register("tube_ratio_guard", note="V1+V2 -- the interaction cell; on `rate` the guard "
                                   "paid only once the bar was multiplicative",
          mode="ratio", guard_frames=8, n_scales=4, width=8, depth=6,
          max_center_frames=128, max_ratio=40.0)
def build_tube_ratio_guard(**cfg):
    return _build_tube_variant(**cfg)
