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
               max_ratio=40.0, vote_gain=8.0, orientation=True, bound_vote=False,
               eps=1e-3, extra_pools=False, top_m=4, participation=False):
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
    * **One ROI, one vote — in height only.** The smoothed row goes through a
      sigmoid, so at any one frame a cell that fires eight times contributes at most
      one. ⚠ **That bounds the vote's height, not its time integral**, and this
      docstring used to say it bounded both. Onsets are summed *before* the sigmoid,
      so a burst holds its vote near one for longer than a single onset does, and the
      difference-of-Gaussians stage below is area-normalised — it reads the integral.
      A murderboard reviewer measured a four-onset burst delivering 1.7–2.7x the
      integrated vote of one onset on a fitted model (2026-09-16), and
      ``tests/test_line_vote.py`` pins the direction on an untrained one. So ``line``
      widens a bursting cell too. ``tube`` widens every onset and bounds nothing:
      its ``max_pool1d`` runs on an already-binary raster, and its own docstring
      records two bursting cells scoring 0.997 where four distinct cells score 0.998.
      ``bound_vote=True`` builds the variant that bounds the integral (registered as
      ``line_bound``), so whether the bound matters is measured rather than argued.
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
      fraction of its broad one. ⚠ **On an empty field the ratio is neither 1 nor
      0.** Every ROI's vote has a floor, ``sigmoid(-vote_gain * vote_bias)``, so the
      count never reaches zero and each channel reads a ratio of two floors — 0.635,
      1.30 and 0.494 on one fitted model — which is what neither a line nor an empty
      field should read. ``eps`` is far below the floor and never engages.
      ``bound_vote=True`` subtracts the floor first, so an empty field reads 0.

    ⚠ **Orientation here is NOT the orientation of the image.** This model is
    permutation-invariant over ROIs by construction and `encode` sorts rows by rate, so
    a tilted line and a random spread are the same object to it — the tilt is a fact
    about the row order, which is a coordinate. What survives the sort is **temporal
    concentration**, and that is what these channels measure. A figure can show a tilt;
    an order-free detector cannot, and one that claimed to would be reading the sort.

    Set ``orientation=False`` to build the length-only model this file shipped first —
    the ablation, so the second sensor's contribution stays attributable.

    ``extra_pools=True`` adds ``chorus``'s two other pooled statistics beside the mean:
    the spread of the votes over ROIs and the mean of the loudest ``top_m``, per smear
    width, straight to the head. That is ``chorus_line`` — ``chorus``'s pooling on
    ``line``'s per-cell stage, which trains — and it differs from ``line`` by exactly
    those channels.

    **``bound_vote=True``** (Tony, 2026-09-16, choosing to measure the bound rather
    than only describe it) changes two things and nothing else:

    * the floor is subtracted and the vote rescaled, ``(vote - floor) / (1 - floor)``,
      so an ROI with no onset nearby votes 0;
    * each ROI's vote is scaled down wherever its local mass exceeds what one onset
      produces. The mass is the vote smoothed by the *same* area-normalised Gaussian
      the difference-of-Gaussians centre uses at that scale, so the bound is on the
      quantity the next stage reads. A lone onset is never scaled. ⚠ The bound is
      still soft: the factor is read frame by frame, so a burst's flanks keep more
      than its peak. How much is measured in ``tests/test_line_vote.py``, not
      asserted here.

    ``participation`` (off by default; ADR-0010 part 5, ``line_part``) adds one vote per ROI
    -- a 1x1 convolution over that ROI's ``n_scales`` votes, then a sigmoid -- whose **sum
    over ROIs** is a count in [0, n_roi], and hands the head that count and the recording's
    floor (``bugarach.learn.participation.count_features``). The model then needs
    ``forward(x, floor=...)``; ``return_votes=True`` also returns the per-ROI votes for the
    membership loss. Off, nothing is built and nothing moves.
    """
    torch = _torch()
    nn = torch.nn
    import math

    from bugarach.learn import participation as part

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
            self.bound_vote = bool(bound_vote)
            # counts (relative length) + the difference-of-Gaussian responses, plus one
            # orientation channel per adjacent pair of smear widths.
            self.extra_pools = bool(extra_pools)
            self.m = int(top_m)
            c_in = (2 * n_scales + (n_scales - 1 if self.orientation else 0)
                    + (2 * n_scales if self.extra_pools else 0))
            self.reads_floor = bool(participation)
            self.head = _dilated_stack(nn, c_in + (3 if participation else 0), 1, width, depth)
            if participation:
                self.vote_head = part.vote_head(nn, n_scales)

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

        def _centre(self, device):
            """The difference-of-Gaussians CENTRE alone, area-normalised: what the
            next stage averages a vote over, per scale."""
            c = torch.exp(self.log_center).clamp(0.5, self.k / 2).view(-1, 1)
            t = torch.arange(-self.k, self.k + 1, device=device,
                             dtype=torch.float32).view(1, -1)
            centre = torch.exp(-0.5 * (t / c) ** 2)
            return (centre / centre.sum(dim=1, keepdim=True)).unsqueeze(1)

        def _vote(self, smeared):
            vote = torch.sigmoid(
                self.vote_gain.view(1, -1, 1) * (smeared - self.vote_bias.view(1, -1, 1)))
            if self.bound_vote:
                floor = torch.sigmoid(-self.vote_gain * self.vote_bias).view(1, -1, 1)
                vote = ((vote - floor) / (1.0 - floor)).clamp_min(0.0)
            return vote

        def _one_onset_mass(self, device):
            """Peak local mass of a lone onset, per scale — the most one vote may carry."""
            one = torch.zeros(1, 1, 2 * self.k + 1, device=device)
            one[0, 0, self.k] = 1.0
            vote = self._vote(torch.nn.functional.conv1d(
                one, self._smear(device), padding=self.k))
            mass = torch.nn.functional.conv1d(
                vote, self._centre(device), padding=self.k, groups=vote.shape[1])
            return mass.amax(dim=2).squeeze(0)

        def forward(self, x, floor=None, return_votes=False):     # (B, n_roi, T)
            b, n, t = x.shape
            # --- thickness: each ROI smoothed on its own, one scale per channel ---
            smeared = torch.nn.functional.conv1d(
                x.reshape(b * n, 1, t), self._smear(x.device), padding=self.k)
            # --- one ROI, one vote: bounded in HEIGHT before anything pools -------
            vote = self._vote(smeared)
            if self.bound_vote:
                # --- ...and in time: no ROI's local mass above one onset's ---------
                mass = torch.nn.functional.conv1d(
                    vote, self._centre(x.device), padding=self.k, groups=vote.shape[1])
                scale = (self._one_onset_mass(x.device).view(1, -1, 1)
                         / mass.clamp_min(1e-6)).clamp(max=1.0)
                vote = vote * scale
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
            if self.extra_pools:
                # chorus's other two symmetric statistics over the ROI axis. Sort and
                # slice rather than topk(min(m, n)), for the reason chorus gives.
                votes = vote.reshape(b, n, -1, t)
                channels.append(votes.std(dim=1, unbiased=False))
                srt, _ = votes.sort(dim=1, descending=True)
                channels.append(srt[:, :self.m].mean(dim=1))
            if not self.reads_floor:
                return self.head(torch.cat(channels, dim=1)).squeeze(1)
            # --- ADR-0010 part 5: one bounded vote per ROI, summed into a count ---
            votes = torch.sigmoid(self.vote_head(vote)).reshape(b, n, t)
            fl = part.floor_tensor(floor, b, x.device)
            channels.append(part.count_features(votes.sum(dim=1), fl))
            out = self.head(torch.cat(channels, dim=1)).squeeze(1)
            return (out, votes) if return_votes else out

    return Line()
