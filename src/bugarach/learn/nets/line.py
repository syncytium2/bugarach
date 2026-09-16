"""line — one architecture, one file.

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

__all__ = ["build_line"]


@register("line", note="two sensors — how much of the field is lit (relative length) and how "
                       "tightly it is lit (orientation, as temporal concentration) — then "
                       "centre-surround that count in time. Tony's vertical line, 2026-09-15",
          n_scales=4, width=8, depth=6, max_center_frames=128, max_ratio=40.0,
          vote_gain=8.0, orientation=True)
def build_line(*, n_scales=4, width=8, depth=6, max_center_frames=128,
               max_ratio=40.0, vote_gain=8.0, orientation=True, eps=1e-3):
    """How many distinct ROIs are lit right now, judged against its own background.

    Tony, 2026-09-15, on the tube models trained against rigid shift: *"i wonder if
    we need an orientation detector rather than a center-surround. something that
    fires looking at the raster as a 1d 'line' at each time window. when most rois
    fire it looks like a vertical line. two rois aren't enough and noise/high
    background looks like fuzz"*.

    **This is that idea made order-free.** A literal oriented filter over the raster
    image cannot be used here: ``encode`` sorts rows busiest-first and its own
    docstring calls row order a coordinate rather than a label, so "vertical" is the
    only orientation with a meaning and a diagonal is an artifact of the sort. What
    survives the sort is the line's **length** — how many distinct ROIs are lit
    within one smear of time — and that is what this counts.

    Four stages, and each one exists because something already here gets it wrong:

    * **Thickness.** Each ROI is smoothed on its own by a Gaussian whose width is a
      free parameter, normalised to **peak one** rather than to area, so one onset
      reaches 1 whatever the fitted width. How tight "at once" must be is fitted.
    * **One ROI, one vote.** The smoothed row goes through a sigmoid, so a cell that
      fires eight times contributes at most one. ``tube`` has no such bound —
      ``max_pool1d`` on an already-binary raster *widens* onsets instead of capping
      them, and its own docstring records the cost: two bursting cells score 0.997
      where four distinct cells score 0.998. Measured again on 2026-09-15 across
      models and plants of equal ink: a 16-ROI line scored only 1.3x a 4-ROI burst
      under the supervised tube.
    * **Length.** The votes are averaged over ROIs, so the output is the **share of
      the field that is lit** — cell-count invariant, and bounded by construction at
      the number of ROIs that actually fired.
    * **Background.** That count is convolved with a difference of Gaussians,
      area-normalised so a flat field integrates to zero. A rising background raises
      the count everywhere and cancels; a line stands above its own surround. This
      is the half ``tiny`` lacks — it has the vote and the pooling and judges the
      sum without a local reference, which is why a busier field moves it.

    So ``line`` is ``tiny``'s distinctness with ``tube``'s rate invariance, and the
    two controls it sits between are already in this folder: ``trace`` pools first
    and keeps no distinctness, ``tube`` pools first and has the kernel.

    ⚠ **The vote is soft**, as the package docstring says: a sigmoid approximates
    "any onset within the smear" and the approximation is worst exactly where the
    smear is widest. Probe it behaviourally (``tools/probe_line_vs_fuzz.py``); do
    not assert it.

    **Two sensors, and the second one arrived on 2026-09-15.** Tony: *"so two sensors,
    orientation and length (relative to the number of rois)"*, then *"make line
    sensitive to both orientation (vertical line) and relative length"*.

    * **Relative length** is the count above: a **mean** over ROIs, so it is the share
      of the field that is lit and not a raw tally — the quantity that is 0.5 when half
      the ROIs fire, at any field size.
    * **Orientation** is the ratio of the count at a narrow smear to the count at the
      next wider one, one channel per adjacent pair. A vertical line has the same
      participants at every width, so its ratios sit near 1; a recruitment spread over
      seconds gathers members only as the smear widens, so its narrow count is a
      fraction of its broad one.

    ⚠ **Orientation here is NOT the orientation of the image.** This model is
    permutation-invariant over ROIs by construction and `encode` sorts rows by rate, so
    a tilted line and a random spread are the same object to it — the tilt is a fact
    about the row order, which is a coordinate. What survives the sort is **temporal
    concentration**, and that is what these channels measure. A figure can show a tilt;
    an order-free detector cannot, and one that claimed to would be reading the sort.

    Set ``orientation=False`` to build the length-only model this file shipped first —
    the ablation, so the second sensor's contribution stays attributable.
    """
    torch = _torch()
    nn = torch.nn
    import math

    class Line(nn.Module):
        def __init__(self):
            super().__init__()
            self.k = int(max_center_frames)
            # Smear widths in SAMPLES, a geometric ladder from one sample up, the
            # same starting point tube uses: one sample is the finest thing the
            # recording can resolve, and the fitted value is the model's own
            # estimate of how tight a coincidence has to be.
            self.log_smear = nn.Parameter(torch.tensor(
                [math.log(1.0 * (2 ** i)) for i in range(n_scales)]))
            self.vote_bias = nn.Parameter(torch.full((n_scales,), 0.5))
            self.vote_gain = nn.Parameter(torch.full((n_scales,), float(vote_gain)))
            # The temporal kernels that judge the count against its own background.
            self.log_center = nn.Parameter(torch.tensor(
                [math.log(2.0 * (2 ** i)) for i in range(n_scales)]))
            self.log_ratio = nn.Parameter(torch.full((n_scales,), math.log(8.0)))
            self.gain = nn.Parameter(torch.ones(n_scales))
            self.orientation = bool(orientation)
            # counts (relative length) + the difference-of-Gaussian responses, plus one
            # orientation channel per adjacent pair of smear widths.
            c_in = 2 * n_scales + (n_scales - 1 if self.orientation else 0)
            self.head = _dilated_stack(nn, c_in, 1, width, depth)

        def _smear(self, device):
            """Per-ROI Gaussians, PEAK-normalised: one onset reaches 1 at any width."""
            s = torch.exp(self.log_smear).clamp(0.5, self.k / 2).view(-1, 1)
            t = torch.arange(-self.k, self.k + 1, device=device,
                             dtype=torch.float32).view(1, -1)
            return torch.exp(-0.5 * (t / s) ** 2).unsqueeze(1)

        def _dog(self, device):
            """Difference of Gaussians on the count, area-normalised to zero sum."""
            c = torch.exp(self.log_center).clamp(0.5, self.k / 2).view(-1, 1)
            s = c * torch.exp(self.log_ratio).clamp(1.5, max_ratio).view(-1, 1)
            t = torch.arange(-self.k, self.k + 1, device=device,
                             dtype=torch.float32).view(1, -1)
            centre = torch.exp(-0.5 * (t / c) ** 2)
            surround = torch.exp(-0.5 * (t / s) ** 2)
            centre = centre / centre.sum(dim=1, keepdim=True)
            surround = surround / surround.sum(dim=1, keepdim=True)
            return ((centre - surround) * self.gain.view(-1, 1)).unsqueeze(1)

        def forward(self, x):                       # (B, n_roi, T)
            b, n, t = x.shape
            # --- thickness: each ROI smoothed on its own, one scale per channel ---
            smeared = torch.nn.functional.conv1d(
                x.reshape(b * n, 1, t), self._smear(x.device), padding=self.k)
            # --- one ROI, one vote: bounded BEFORE anything pools over ROIs -------
            vote = torch.sigmoid(
                self.vote_gain.view(1, -1, 1) * (smeared - self.vote_bias.view(1, -1, 1)))
            # --- length: the share of the field that is lit, per scale ------------
            count = vote.reshape(b, n, -1, t).mean(dim=1)      # (B, n_scales, T)
            # --- background: a flat count integrates to zero ----------------------
            resp = torch.stack([
                torch.nn.functional.conv1d(count[:, i:i + 1], self._dog(x.device)[i:i + 1],
                                           padding=self.k)[:, 0]
                for i in range(count.shape[1])], dim=1)
            channels = [count, resp]
            if self.orientation:
                # --- orientation: how much of the count survives a NARROWER smear ----
                # Same participants at every width -> near 1, a vertical line. Members
                # gathered only as the smear widens -> well below 1, a spread. The ROI
                # axis is already gone here, so this is temporal concentration and not
                # the image's tilt, which no order-free model can see.
                channels.append(count[:, :-1] / (count[:, 1:] + eps))
            return self.head(torch.cat(channels, dim=1)).squeeze(1)

    return Line()
