"""Synthetic coordinated-event data with planted ground truth.

Builds a recording of per-ROI background activity with **coordinated events
planted into it at known times, with known participants**, so a detector — or a
model — can be scored against what was actually there rather than against
another detector's opinion. Ported from interface2's ``generate_synth_coord.m``.

Emits a real :class:`bugarach.store.Slice`, so every detector consumes it with no
adapter::

    slice_, gt = simulate_coordination(seed=1)
    det = loco_detect(stream_trains(slice_.streams["events"], ext), ext)
    score = score_against(gt, det.onset_sec)      # see bugarach.score

Single-stream by default. The canonical two-stream stores are a convention of
one lab's pipeline (FOUNDATIONS §3), and most outside labs have one stream;
``streams=("fast", "slow")`` duplicates the single stream, which is exactly what
the MATLAB original emits (its two streams are byte-identical).

Not bit-parity with MATLAB, deliberately
----------------------------------------
Every other port in this package matches its MATLAB original to 1e-9. This one
**cannot**, and chasing it would be wasted work. The original draws from
``poissrnd``, ``randn`` and ``randperm``; MATLAB's normal generator is a
ziggurat and numpy's legacy generator is the polar method, and the Poisson and
permutation algorithms differ too. Only ``rand`` is bit-compatible (verified —
FOUNDATIONS §2), which is why the *detectors* could be matched exactly: they use
only ``rand`` and ``randi``.

That is an acceptable loss here in a way it would not be for a detector. A
detector is a citable stand-in for the original and must agree with it on real
data; a generator only has to produce data with the right properties,
reproducibly. So what is guaranteed instead:

* **determinism** — same seed, same output, on every platform;
* **the same ground-truth contract** — planted times, participants,
  participation fraction, and jitter, plus distractors tracked separately;
* **MATLAB's rounding semantics where they change the answer** —
  ``matlab_round`` for grid quantization, because numpy rounds halves to even
  and MATLAB rounds them away from zero, which moves events between bins.

``np.random.RandomState`` is used throughout (``default_rng`` is banned in
``src/`` — sapper SAP002).
"""

from __future__ import annotations

import inspect
import math
from dataclasses import dataclass, field

import numpy as np

from bugarach.detectors._shared import matlab_round
from bugarach.io import slice_from_events
from bugarach.store import Slice


@dataclass(frozen=True)
class PlantedEvent:
    """One planted event and who took part in it."""

    time: float
    """Nominal event time (s). Participant onsets are jittered around it."""
    frac: float
    """Requested participating fraction of ROIs."""
    n_part: int
    """Actual participant count."""
    rois: tuple[int, ...]
    """Participating ROI indices, ascending."""
    jitter_sec: float
    """SD of participant onset jitter (s). 0 = perfectly synchronous."""
    kind: str = "coordinated"
    """``coordinated`` (a recall target) or ``distractor`` (see below)."""
    onsets: tuple[float, ...] = ()
    """The onset each participant actually got — jittered, clipped to the
    recording, and quantized to the imaging grid — column-aligned with ``rois``.

    **Additive: nothing that existed before this field reads it, and no emitted
    data changed when it arrived.** It is recorded because these are the times
    actually written into the trains, so they are what the event *is* rather than
    what it was asked to be. A footprint derived from ``time ± k·jitter_sec`` is a
    parametric restatement of the request — right on average and wrong on every
    individual event, since six Gaussian draws do not span exactly ±3 sigma and
    grid quantization moves the edges again. Read :attr:`observed_span` for the
    realized footprint; :attr:`span` is unchanged and still nominal.
    """

    @property
    def span(self) -> tuple[float, float]:
        """A conventional ±3-sigma window around the event, for scoring or masks.

        **Unchanged, deliberately.** This is what the generator *asked* for, and
        `docs/todo/2026-08-13-scoring-tolerance-vs-detector-resolution.md`
        describes it in those terms. Redefining it in place would have moved a
        published meaning with no test watching — see :attr:`observed_span` for
        what was actually planted.
        """
        w = 3.0 * self.jitter_sec
        return (self.time - w, self.time + w)

    @property
    def observed_span(self) -> tuple[float, float]:
        """First to last participant onset — the event's realized footprint.

        Falls back to :attr:`span` only for a :class:`PlantedEvent` built without
        onsets, which the generator never does but hand-built test fixtures do.

        ⚠ **A one-participant event has zero width here**, and that is reachable
        from ordinary settings: ``max(1, matlab_round(frac * n_roi))`` guarantees
        a participant, so a small population at a small fraction plants events
        whose realized footprint is a point. One onset genuinely has no spread,
        so it is not padded — but a consumer using this as a mask or a training
        target gets a degenerate interval, and should decide what to do about
        that rather than discover it. :attr:`span` is never degenerate, which is
        one of the few things it is better at.
        """
        if self.onsets:
            return (min(self.onsets), max(self.onsets))
        return self.span


@dataclass
class GroundTruth:
    """What was planted. ``events`` are recall targets; ``distractors`` are not.

    The distinction is the point. A distractor is a **correlated population
    burst** — genuine cross-ROI coincidence that is not a coordinated event.
    Together with a dense-but-random ``hot_window``, these are the negatives that
    decide whether a detector (or a model) has learned coordination or merely
    "lots of activity at once". Upstream tracked them to count false alarms; for
    a training set they are labelled negatives.
    """

    events: list[PlantedEvent] = field(default_factory=list)
    distractors: list[PlantedEvent] = field(default_factory=list)
    params: dict = field(default_factory=dict)

    @property
    def times(self) -> np.ndarray:
        return np.array([e.time for e in self.events], dtype=float)

    @property
    def frac(self) -> np.ndarray:
        return np.array([e.frac for e in self.events], dtype=float)

    @property
    def distractor_times(self) -> np.ndarray:
        return np.array([d.time for d in self.distractors], dtype=float)

    def participation_mask(self, n_roi: int) -> np.ndarray:
        """``(n_events, n_roi)`` boolean — who took part in each planted event.

        The per-(ROI, event) label. Rasterizing it onto a time grid is the
        caller's business; the sparse form is the source of truth because events
        are sparse and a dense mask over a long recording is mostly zeros.
        """
        m = np.zeros((len(self.events), n_roi), dtype=bool)
        for i, e in enumerate(self.events):
            m[i, list(e.rois)] = True
        return m


def median_over_mean(shape: float) -> float:
    """``median / mean`` of ``Gamma(shape, ·)`` — the scale cancels.

    The per-ROI background is ``Gamma(shape, bg_rate_hz / shape)``, whose mean is
    exactly ``bg_rate_hz``. Its median has no closed form, but it is proportional
    to the same scale, so the ratio depends on ``shape`` alone:
    ``median(Gamma(shape, 1)) / shape``.

    At the fitted :data:`~bugarach.bench.MEASURED_RATE_SHAPE` of 0.275 this is
    about **0.21** — the typical ROI fires at a fifth of the field's mean rate,
    which is what a field with a few busy cells and a third of them silent looks
    like.

    SciPy is not a hard dependency of this package, so the ratio is computed by
    bisection on the regularized lower incomplete gamma, which ``math.lgamma``
    and a short series give without it.
    """
    if shape <= 0:
        raise ValueError(f"shape must be positive, got {shape}")

    def _gammainc_lower(a: float, x: float) -> float:
        """P(a, x), by the series that converges for x < a+1 and the continued
        fraction elsewhere — Numerical Recipes 6.2, the standard pair."""
        if x <= 0:
            return 0.0
        if x < a + 1.0:
            term = 1.0 / a
            total = term
            n = a
            for _ in range(1000):
                n += 1.0
                term *= x / n
                total += term
                if abs(term) < abs(total) * 1e-15:
                    break
            return total * math.exp(-x + a * math.log(x) - math.lgamma(a))
        # continued fraction for Q(a, x), then P = 1 - Q
        tiny = 1e-300
        b = x + 1.0 - a
        c = 1.0 / tiny
        d = 1.0 / b
        h = d
        for i in range(1, 1000):
            an = -i * (i - a)
            b += 2.0
            d = an * d + b
            if abs(d) < tiny:
                d = tiny
            c = b + an / c
            if abs(c) < tiny:
                c = tiny
            d = 1.0 / d
            delta = d * c
            h *= delta
            if abs(delta - 1.0) < 1e-15:
                break
        q = math.exp(-x + a * math.log(x) - math.lgamma(a)) * h
        return 1.0 - q

    lo, hi = 0.0, max(1.0, shape) * 10.0
    while _gammainc_lower(shape, hi) < 0.5:
        hi *= 2.0
    for _ in range(200):
        mid = 0.5 * (lo + hi)
        if _gammainc_lower(shape, mid) < 0.5:
            lo = mid
        else:
            hi = mid
    return 0.5 * (lo + hi) / shape


def rate_as_mean(rate: float, stat: str, *, shape: float | None) -> float:
    """A per-ROI rate and WHICH STATISTIC OF THE FIELD IT IS, as the mean.

    ``bg_rate_hz`` is the mean, always — but a caller measuring a real recording
    usually has the median, because that is what ``assess`` puts in front of
    them, and the two are a factor of five apart on an uneven field. A number
    that means two things without saying which yields a plausible wrong answer
    rather than an error, which is the trap
    :doc:`the export contract <export_folder_spec>` names in as many words.

    ``shape`` is ``None`` for a flat field, where every ROI carries the same rate
    and the two statistics coincide, so nothing converts.
    """
    if stat not in ("mean", "median"):
        raise ValueError(
            f"bg_rate_stat must be 'mean' or 'median', got {stat!r} — the "
            "generator cannot guess which statistic a rate is, and guessing "
            "wrong is a factor of five on an uneven background")
    if stat == "mean" or shape is None:
        return float(rate)
    return float(rate) / median_over_mean(shape)


def _quantize(values, grid_sec: float) -> tuple[float, ...]:
    """Snap onsets to the imaging grid exactly as the trains are snapped.

    Must stay identical to the quantization applied to ``trains`` at the end of
    :func:`simulate_coordination` — including ``matlab_round``'s half-away-from-
    zero, which decides which bin a tie lands in. A recorded onset that differs
    from the one in the train by a grid step would make the label disagree with
    the data it labels, in the one place nothing would notice.
    """
    if grid_sec <= 0:
        return tuple(float(v) for v in values)
    return tuple(float(matlab_round(v / grid_sec) * grid_sec) for v in values)


def _place_uniform(rng, m, lo, hi, min_sep, exclude, max_tries=10000):
    """Uniform placement with a minimum-separation rejection loop (the MATLAB
    behaviour): draw a time, keep it if it clears every placed event and any
    excluded window."""
    times: list[float] = []
    for _ in range(max_tries):
        if len(times) >= m:
            break
        t = lo + rng.random_sample() * (hi - lo)
        if exclude is not None and exclude[0] - min_sep <= t <= exclude[1] + min_sep:
            continue
        if all(abs(t - u) >= min_sep for u in times):
            times.append(t)
    if len(times) < m:
        raise ValueError(
            f"placed only {len(times)}/{m} events — reduce the count or "
            f"min_sep_sec, or lengthen duration_sec")
    return np.sort(np.array(times, dtype=float))


def _place_renewal(rng, m, lo, hi, min_sep, exclude, interval_cv):
    """Renewal placement with a tunable interval CV — variable, not regular.

    Uniform-with-min-separation produces inter-event intervals that are fairly
    even, and *regularity is a cue*: a model can learn "an event is due" from the
    clock instead of from the activity, and score well on synthetic data for a
    reason that does not transfer. Real coordination is not metronomic.

    Intervals are ``min_sep + Gamma(shape, scale)``, so the floor is respected by
    construction and ``interval_cv`` sets the irregularity of the excess:

    * ``0``   — near-constant spacing (the regular case, available on purpose)
    * ``1``   — exponential excess: a Poisson process above the floor, maximally
      irregular
    * ``>1``  — bursty; long quiet stretches broken by closely-spaced events

    The realized mean interval is set by the span and count, so ``m`` events
    still fit the recording.
    """
    if m <= 0:
        return np.zeros(0, dtype=float)

    # An excluded window is removed from the timeline BEFORE placing, not
    # filtered out afterwards: placing m and then dropping the ones that landed
    # in the window returns fewer than m, silently thinning the schedule. Events
    # are laid out on the usable span and then shifted past the gap.
    gap_lo = gap_hi = None
    if exclude is not None:
        gap_lo = max(lo, exclude[0] - min_sep)
        gap_hi = min(hi, exclude[1] + min_sep)
        if gap_hi <= gap_lo:
            gap_lo = gap_hi = None

    gap_width = 0.0 if gap_lo is None else (gap_hi - gap_lo)
    hi = hi - gap_width                       # place on the compressed timeline
    span = hi - lo
    if span <= 0:
        raise ValueError(
            "the excluded window leaves no room for planted events — "
            "lengthen duration_sec or shrink hot_window")
    mean_interval = span / (m + 1)
    if mean_interval <= min_sep:
        raise ValueError(
            f"cannot fit {m} events {min_sep}s apart in {span:.1f}s — "
            f"reduce the count or min_sep_sec, or lengthen duration_sec")
    excess_mean = mean_interval - min_sep

    if interval_cv <= 0:
        gaps = np.full(m, min_sep + excess_mean)
    else:
        shape = 1.0 / (interval_cv ** 2)
        scale = excess_mean / shape
        gaps = min_sep + rng.gamma(shape, scale, size=m)

    times = lo + np.cumsum(gaps)
    # A draw can overrun the window; rescale the excess above the floor so the
    # last event still lands inside, preserving ordering and the min_sep floor.
    if times[-1] > hi:
        excess = times - lo - min_sep * np.arange(1, m + 1)
        room = hi - lo - min_sep * m
        if room <= 0:
            raise ValueError(
                f"cannot fit {m} events {min_sep}s apart in {span:.1f}s")
        excess = excess * (room / excess[-1]) if excess[-1] > 0 else excess
        times = lo + min_sep * np.arange(1, m + 1) + excess

    if gap_lo is not None:
        # Expand the timeline again: anything at or past the gap start slides
        # beyond it. Ordering and the min_sep floor are preserved, and the gap
        # is padded by min_sep on both sides so the events straddling it stay
        # separated too.
        times = np.where(times >= gap_lo, times + gap_width, times)
    return times


def simulate_coordination(
    spec=None,
    *,
    duration_sec: float = 600.0,
    n_roi: int = 30,
    bg_rate_hz: float = 0.05,
    bg_rate_stat: str = "mean",
    bg_rate_shape: float | None = None,
    bg_burst_shape: float | None = None,
    bg_burst_bin_sec: float = 60.0,
    participation=(1.0, 0.75, 0.50),
    n_per_level=(5, 5, 5),
    jitter_sec: float = 0.05,
    grid_sec: float = 0.1,
    min_sep_sec: float = 15.0,
    margin_sec: float = 5.0,
    spacing: str = "renewal",
    interval_cv: float = 1.0,
    hot_window=None,
    hot_rate_hz: float = 0.0,
    ramp_sec: float = 0.0,
    n_distractors: int = 0,
    distractor_frac: float = 0.5,
    distractor_jitter: float | None = None,
    distractor_window=None,
    streams=("events",),
    slice_id: str = "synthetic",
    regions=None,
    seed: int | None = None,
) -> tuple[Slice, GroundTruth]:
    """Build a synthetic recording with planted coordinated events.

    duration_sec, n_roi, bg_rate_hz: the background. ``bg_rate_hz`` is the
      **mean** per-ROI rate.
    bg_rate_stat: which statistic of the field ``bg_rate_hz`` is —
      ``"mean"`` (the default, and what this generator has always meant) or
      ``"median"``. A caller measuring a real recording usually holds the
      median, because that is what ``assess`` puts in front of them, and on an
      uneven field the two are a factor of five apart. Saying which is what
      stops a plausible wrong answer: ``rate_as_mean`` converts, and refuses
      anything it was not told. On a flat field (``bg_rate_shape=None``) the two
      statistics coincide and nothing converts, which is why handing over a
      median has been harmless here so far.
    bg_rate_shape: heterogeneity of the background across ROIs. ``None`` (the
      default) gives every ROI exactly ``bg_rate_hz`` — a flat field, and what
      this generator did for its whole life. A positive number draws each ROI's
      own rate from ``Gamma(shape, bg_rate_hz / shape)``, so the mean is still
      ``bg_rate_hz`` while the spread is ``1/sqrt(shape)``; small shape means a
      few busy ROIs and many near-silent ones.

      **Why it exists.** A real baseline field is not flat, and the gap is not
      subtle: measured over 81 baseline windows, 35% of real ROIs record no
      event at all and the busiest reaches 486 mHz, while the flat generator
      leaves 2% silent and tops out near 138. Its typical ROI is *busier* than
      a real one and its busiest is far quieter — wrong in both directions at
      once. See ``bugarach.bench.MEASURED_RATE_SHAPE`` for the fitted value and
      how it was obtained; note that the silent ROIs are not modelled, they
      fall out of a low rate drawn from the tail.

      Leaving it ``None`` keeps the RNG stream identical, so every existing
      seed reproduces exactly.
    bg_burst_shape / bg_burst_bin_sec: how unevenly an ROI's own events are
      spread **in time**. ``None`` (the default) is homogeneous Poisson — a
      constant rate for the whole recording. A positive number multiplies the
      rate in each bin by a ``Gamma(shape, 1/shape)`` draw, which has mean 1, so
      the expected total is untouched and only its distribution over time moves;
      counts per bin are then Negative Binomial, the model the clumping was
      fitted under.

      **Pass a sequence for more than one scale**, e.g.
      ``bg_burst_shape=(1.55, 1.39), bg_burst_bin_sec=(300.0, 60.0)``. One scale
      is not enough and the data says so: a single bin width draws independent
      bins, so its over-dispersion stops growing once you look at windows wider
      than the bin, while real ROIs keep getting more over-dispersed the wider
      you look — variance/mean 1.8 at 30 s, 2.6 at 60 s, 3.9 at 120 s, 5.7 at
      300 s. That is a busy stretch spanning several bins, and no single scale
      reproduces it at any shape.

      **Why this and not an interval distribution.** A baseline window gives the
      median ROI under one event and leaves 35% with none, so most ROIs have no
      interval to measure and requiring a few per ROI drops precisely the quiet
      ones (``docs/generator.md``). Binned counts survive that; ISIs do not.

      See ``bugarach.bench.MEASURED_BURST_SHAPE``. As with the rate shape this is
      **off by default and not used by the bench**, and leaving it ``None``
      leaves the RNG stream untouched.
    participation / n_per_level: participating fractions and how many events at
      each. ``(1.0, 0.75, 0.5)`` with ``(5, 5, 5)`` plants 5 all-ROI events,
      5 at 75%, 5 at 50%, interleaved in time.
    jitter_sec: SD of participant onset jitter. Small = tight coordination.
    grid_sec: quantize onsets to the imaging grid (0 disables). Uses MATLAB
      rounding — halves away from zero — because banker's rounding moves events
      between bins.
    spacing: ``"renewal"`` (default; variable intervals, see ``interval_cv``) or
      ``"uniform"`` (uniform placement with a min-separation rejection loop, the
      MATLAB behaviour).
    interval_cv: irregularity of the intervals under ``"renewal"``. 0 is
      near-constant, 1 is Poisson-like, >1 is bursty. **The default is 1, not 0,
      deliberately** — evenly spaced events let a model predict from the clock.
    hot_window / hot_rate_hz / ramp_sec: a dense-but-random block with **no**
      planted events, ramping in over ``ramp_sec`` (a sharp step produced a
      boundary false alarm upstream). Detectors that key on rate rather than
      coordination fire here; that is what it is for.
    n_distractors / distractor_frac / distractor_jitter / distractor_window:
      correlated population bursts — real coincidence that is not a coordinated
      event. Recorded in ``gt.distractors``, never in ``gt.events``.
    streams: stream names. One by default; pass ``("fast", "slow")`` to duplicate
      into the canonical two-stream shape.
    regions: **none by default, and that is a correction.** This used to emit
      ``[("baseline", 0.0, duration)]`` unconditionally, which looks harmless and
      is not: ``baseline`` is a label from the wet-lab protocol, and the region
      windowing rules read it as "the pre-solution period" and trim the analysis
      to its final ``baseline_window_max_sec`` (1200 s). SCE honours that trim,
      so on a 45-minute synthetic recording it analysed only 1500–2700 s and was
      scored against the 15 events planted across all of it — a recall ceiling of
      7/15, and measured recall of 0.40 that read as a weak detector rather than
      as a detector shown 44% of the data. Removing the annotation lifts it to
      0.73–0.87 while LoCo and CICADA, which do not restrict detection to the
      window, do not move at all.

      A synthetic recording with events planted uniformly throughout has no
      baseline and no treatment; claiming otherwise imposes an experimental
      protocol that is not in the data. Pass ``regions`` explicitly to simulate
      one on purpose — that is the only way it should ever happen.
    seed: ``None`` is nondeterministic; an int is reproducible everywhere.

    Returns ``(slice, ground_truth)``.
    """
    if spec is not None:
        # A spec supplies everything that describes the RECORDING; the caller
        # keeps everything that describes this CALL (seed, streams, slice_id,
        # regions) and the bench keeps its test constructs (probe, distractors).
        # Passing a spec and also naming one of its fields is refused rather
        # than merged: silently letting one win is how a figure ends up
        # labelled with settings it was not drawn at.
        from bugarach.spec import RecordingSpec

        if not isinstance(spec, RecordingSpec):
            raise TypeError(
                f"spec must be a RecordingSpec, got {type(spec).__name__}")
        owned = spec.as_kwargs()
        given = dict(
            duration_sec=duration_sec, n_roi=n_roi, bg_rate_hz=bg_rate_hz,
            bg_rate_shape=bg_rate_shape, bg_burst_shape=bg_burst_shape,
            bg_burst_bin_sec=bg_burst_bin_sec, participation=participation,
            n_per_level=n_per_level, jitter_sec=jitter_sec, grid_sec=grid_sec,
            min_sep_sec=min_sep_sec, margin_sec=margin_sec, spacing=spacing,
            interval_cv=interval_cv,
        )
        defaults = _SIGNATURE_DEFAULTS
        clashes = sorted(k for k, v in given.items()
                         if k in owned and v != defaults[k])
        if clashes:
            raise TypeError(
                f"simulate_coordination() got both a spec and {clashes} — "
                f"the spec owns those. Use spec.replace(...) to vary one.")
        # A spec's `bg_rate_hz` is a mean by construction — `bench.REGIMES`
        # states its endpoints as the interquartile spread of slice-MEAN per-ROI
        # rate — so a spec settles the question and a caller who also passed a
        # statistic is asserting something the spec already answers.
        if bg_rate_stat != _SIGNATURE_DEFAULTS["bg_rate_stat"]:
            raise TypeError(
                "simulate_coordination() got both a spec and bg_rate_stat — a "
                "spec's bg_rate_hz is a mean by construction, so there is "
                "nothing for the flag to say. Convert before building the spec.")
        bg_rate_stat = "mean"
        duration_sec = owned["duration_sec"]
        n_roi = owned["n_roi"]
        grid_sec = owned["grid_sec"]
        bg_rate_hz = owned["bg_rate_hz"]
        bg_rate_shape = owned["bg_rate_shape"]
        bg_burst_shape = owned["bg_burst_shape"]
        bg_burst_bin_sec = owned["bg_burst_bin_sec"]
        participation = owned["participation"]
        n_per_level = owned["n_per_level"]
        jitter_sec = owned["jitter_sec"]
        min_sep_sec = owned["min_sep_sec"]
        margin_sec = owned["margin_sec"]
        spacing = owned["spacing"]
        interval_cv = owned["interval_cv"]

    if len(participation) != len(n_per_level):
        raise ValueError(
            f"participation and n_per_level must be the same length "
            f"({len(participation)} vs {len(n_per_level)})")
    if spacing not in ("renewal", "uniform"):
        raise ValueError(f"spacing must be 'renewal' or 'uniform', got {spacing!r}")
    if not streams:
        raise ValueError("streams must name at least one stream")
    if duration_sec <= 2 * margin_sec:
        raise ValueError(
            f"margin_sec={margin_sec} leaves no room in duration_sec={duration_sec}")

    rng = np.random.RandomState(seed)
    T, nR = float(duration_sec), int(n_roi)
    trains: list[list[float]] = [[] for _ in range(nR)]

    # ---- background: per-ROI Poisson, homogeneous or Gamma-heterogeneous ------
    # Whatever statistic the caller holds, resolved to the mean this draw wants.
    # A flat field has one rate for every ROI, so its mean and its median are the
    # same number and nothing converts — which is exactly why a caller handing
    # over a median has been harmless here, and would stop being harmless the
    # moment `bg_rate_shape` is wired in.
    bg_rate_hz = rate_as_mean(bg_rate_hz, bg_rate_stat, shape=bg_rate_shape)
    # When bg_rate_shape is None every ROI gets bg_rate_hz and NO random numbers
    # are drawn here, so the stream — and every existing seed — is unchanged.
    if bg_rate_shape is None:
        bg_rates = np.full(nR, float(bg_rate_hz))
    else:
        if bg_rate_shape <= 0:
            raise ValueError(
                f"bg_rate_shape must be positive, got {bg_rate_shape}")
        # NOTE, because it bit a figure: this reshuffles everything downstream.
        # The draw consumes random numbers, and the per-ROI Poisson counts it
        # produces consume a different quantity again, so at a fixed seed the
        # planted events land at DIFFERENT times with the knob on than with it
        # off. Giving the rates their own stream does not fix that — the counts
        # still differ — and the only real fix, drawing the background after the
        # events, would renumber every existing seed and move every bench score
        # in this package. So the schedule redraws, exactly as it does for
        # `bg_rate_hz`, and anything comparing flat against varied must use each
        # run's OWN ground truth rather than assuming they share one.
        bg_rates = rng.gamma(bg_rate_shape, bg_rate_hz / bg_rate_shape, size=nR)

    if bg_burst_shape is None:
        # Homogeneous in time: one Poisson draw per ROI over the whole span.
        for r in range(nR):
            k = rng.poisson(bg_rates[r] * T)
            if k:
                trains[r].extend(rng.random_sample(k) * T)
    else:
        # Clumped in time. The ROI keeps its own mean rate; on each scale that
        # rate is multiplied by a Gamma(k, 1/k) draw, which has mean 1, so the
        # expected total is unchanged and only its distribution over time moves.
        # Counts on one scale are then Negative Binomial — exactly the model the
        # clumping was fitted under, rather than a burst generator invented to
        # look right.
        #
        # More than one scale is allowed, and is what real data needs. A single
        # scale draws independent bins, so its over-dispersion stops growing once
        # you look at windows wider than the bin; real ROIs keep getting more
        # over-dispersed the wider you look (variance/mean 1.8 at 30 s, 2.6 at
        # 60 s, 3.9 at 120 s, 5.7 at 300 s), which is a busy stretch spanning
        # several bins. Multiplying a slow modulation by a fast one reproduces
        # that; one bin width cannot, at any shape.
        shapes = (np.atleast_1d(np.asarray(bg_burst_shape, dtype=float))
                  .astype(float).tolist())
        bins = (np.atleast_1d(np.asarray(bg_burst_bin_sec, dtype=float))
                .astype(float).tolist())
        if len(bins) == 1 and len(shapes) > 1:
            raise ValueError(
                "bg_burst_shape names more than one scale, so bg_burst_bin_sec "
                f"must name the same number ({len(shapes)}), got 1")
        if len(shapes) != len(bins):
            raise ValueError(
                f"bg_burst_shape and bg_burst_bin_sec must be the same length "
                f"({len(shapes)} vs {len(bins)})")
        if any(s <= 0 for s in shapes):
            raise ValueError(
                f"bg_burst_shape must be positive, got {bg_burst_shape}")
        if any(b <= 0 for b in bins):
            raise ValueError(
                f"bg_burst_bin_sec must be positive, got {bg_burst_bin_sec}")

        # Finest scale last: it defines the bins events are actually placed in,
        # and the coarser scales multiply into it.
        order = np.argsort(bins)[::-1]
        shapes = [shapes[i] for i in order]
        bins = [bins[i] for i in order]
        fine = bins[-1]
        edges = np.arange(0.0, T, fine)
        for r in range(nR):
            # One multiplier series per scale, drawn per ROI: a busy stretch
            # belongs to a cell, not to the whole field.
            series = [rng.gamma(s, 1.0 / s, size=int(np.ceil(T / b)))
                      for s, b in zip(shapes, bins)]
            for j, lo_b in enumerate(edges):
                w = min(fine, T - lo_b)
                mult = 1.0
                for m, b in zip(series, bins):
                    mult *= m[min(int(lo_b // b), m.size - 1)]
                k = rng.poisson(bg_rates[r] * mult * w)
                if k:
                    trains[r].extend(lo_b + rng.random_sample(k) * w)

    # ---- optional dense-but-random block, no planted events -------------------
    if hot_window is not None and hot_rate_hz > 0:
        h0, h1 = float(hot_window[0]), float(hot_window[1])
        Lh = h1 - h0
        for r in range(nR):
            k = rng.poisson(hot_rate_hz * Lh)          # candidates at max rate
            if not k:
                continue
            ct = h0 + rng.random_sample(k) * Lh
            if ramp_sec > 0:                            # thin to the ramped rate
                rf = np.minimum(1.0, (ct - h0) / ramp_sec)
                ct = ct[rng.random_sample(k) < rf]
            trains[r].extend(ct)

    # ---- correlated-burst distractors (negatives, not targets) ----------------
    distractors: list[PlantedEvent] = []
    if n_distractors > 0:
        bw = distractor_window if distractor_window is not None else hot_window
        if bw is None:
            bw = (margin_sec, T - margin_sec)
        bj = jitter_sec if distractor_jitter is None else distractor_jitter
        bt = np.sort(bw[0] + rng.random_sample(n_distractors) * (bw[1] - bw[0]))
        for t in bt:
            np_ = max(1, matlab_round(distractor_frac * nR))
            rois = np.sort(rng.choice(nR, size=np_, replace=False))
            got = []
            for r in rois:
                onset = min(max(t + bj * rng.randn(), 0.0), T)
                trains[r].append(onset)
                got.append(onset)
            distractors.append(PlantedEvent(
                time=float(t), frac=float(distractor_frac), n_part=int(np_),
                rois=tuple(int(x) for x in rois), jitter_sec=float(bj),
                onsets=_quantize(got, grid_sec), kind="distractor"))

    # ---- planted events -------------------------------------------------------
    fracs = np.array([f for f, n in zip(participation, n_per_level)
                      for _ in range(int(n))], dtype=float)
    rng.shuffle(fracs)                                   # interleave levels in time
    m = fracs.size
    lo, hi = margin_sec, T - margin_sec
    excl = None if hot_window is None else (float(hot_window[0]), float(hot_window[1]))
    if m:
        if spacing == "uniform":
            times = _place_uniform(rng, m, lo, hi, min_sep_sec, excl)
        else:
            times = _place_renewal(rng, m, lo, hi, min_sep_sec, excl, interval_cv)
    else:
        times = np.zeros(0, dtype=float)

    events: list[PlantedEvent] = []
    for t, f in zip(times, fracs):
        np_ = max(1, matlab_round(f * nR))
        rois = np.sort(rng.choice(nR, size=np_, replace=False))
        got = []
        for r in rois:
            onset = min(max(t + jitter_sec * rng.randn(), 0.0), T)
            trains[r].append(onset)
            got.append(onset)
        events.append(PlantedEvent(
            time=float(t), frac=float(f), n_part=int(np_),
            rois=tuple(int(x) for x in rois), jitter_sec=float(jitter_sec),
            onsets=_quantize(got, grid_sec)))
    events.sort(key=lambda e: e.time)

    # ---- quantize + sort ------------------------------------------------------
    per_roi = []
    for v in trains:
        a = np.asarray(v, dtype=float)
        if grid_sec > 0 and a.size:
            # MATLAB round (half away from zero), not numpy's round-half-to-even:
            # a half-grid tie decides which bin an event lands in.
            a = np.array([matlab_round(x / grid_sec) for x in a],
                         dtype=float) * grid_sec
        per_roi.append(np.sort(a))

    # The generator knows its own imaging grid, so a simulated recording
    # carries the interval for free and nobody has to be prompted for one
    # (FOUNDATIONS §6). `grid_sec = 0` disables quantization — a continuous-time
    # simulation no camera could have produced — and that recording honestly
    # has no sampling interval, which is a state the loader already has a name
    # for rather than a reason to invent 0.1.
    slice_ = slice_from_events({name: per_roi for name in streams},
                               dt=grid_sec if grid_sec > 0 else None,
                               slice_id=slice_id, regions=regions)
    gt = GroundTruth(
        events=events,
        distractors=distractors,
        params=dict(
            duration_sec=T, n_roi=nR, bg_rate_hz=bg_rate_hz,
            bg_rate_shape=bg_rate_shape, bg_burst_shape=bg_burst_shape,
            bg_burst_bin_sec=bg_burst_bin_sec,
            participation=tuple(participation), n_per_level=tuple(n_per_level),
            jitter_sec=jitter_sec, grid_sec=grid_sec, min_sep_sec=min_sep_sec,
            margin_sec=margin_sec, spacing=spacing, interval_cv=interval_cv,
            hot_window=None if hot_window is None else tuple(hot_window),
            hot_rate_hz=hot_rate_hz, ramp_sec=ramp_sec,
            n_distractors=n_distractors, distractor_frac=distractor_frac,
            streams=tuple(streams), seed=seed,
        ),
    )
    return slice_, gt


# Derived from the signature rather than written out, so a default that changes
# cannot leave the spec/keyword clash check comparing against a stale value.
_SIGNATURE_DEFAULTS = {
    name: p.default
    for name, p in inspect.signature(simulate_coordination).parameters.items()
    if p.default is not inspect.Parameter.empty
}
