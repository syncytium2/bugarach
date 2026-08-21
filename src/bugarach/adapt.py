"""Turn an assessment of a real recording into generator parameters.

The middle step of the per-lab loop: **measure your recordings → parameterize the
generator → train → detect.** :mod:`bugarach.assess` does the measuring and
:func:`bugarach.simulate.simulate_coordination` does the generating; this is the
translation between them, and it is where the assumptions live.

It is deliberately loud about what it does not know. Every value it cannot ground
in the measurement comes back as a **range to sweep**, not a point to trust —
`simulation_plan.md` §5's rule, which this project has already paid for twice:
*domain randomization widens a distribution, it does not centre one. Randomize
around measured values, never instead of measuring them.*

What maps to what
-----------------
======================  =========================  ===============================
assessment              generator                   note
======================  =========================  ===============================
``n_roi``               ``n_roi``                   direct
``roi_rate_mean``       ``bg_rate_hz``              ⚠ total rate, not background
``part_n_obs``          ``participation``           as a fraction of ``n_roi``
``jit_obs``             ``jitter_sec``              **only when ``jit_defined``**
``clusters_permin``     event count + ``min_sep``   floored by the null window
``win_dur``             ``duration_sec``            lengthened when spacing needs it
======================  =========================  ===============================

Two of those rows carry a trap.

**That row used to read ``roi_rate_med``, and that was a third trap** — a median
handed to a parameter ``simulate.py`` documents as the **mean**. It was invisible
because nothing here sets ``bg_rate_shape``, so the generated field is flat and
its two statistics are one number; wiring in
:data:`~bugarach.bench.MEASURED_RATE_SHAPE` would have made it wrong by about a
factor of five, silently. The statistic now travels with the number as
``bg_rate_stat`` and the generator refuses a rate that does not say which it is.
The mean is also the steadier estimator: at a realistic 33 ROIs the sample median
of a ``Gamma(0.275)`` field spans 0.56 to 5.56 mHz between its 5th and 95th
percentiles around a population value of 2.14.

**``roi_rate_mean`` is the total per-ROI rate, coordinated events included**, and
the generator's ``bg_rate_hz`` is background *only*. Handing one to the other
double-counts the coordination: the events get planted on top of a background
that already contains them. The over-count is small at measured rates — a
coordinated event contributes a few onsets per ROI against tens of background
ones — but it is a bias, it runs one way, and it is the same quantity the bench
inherited. Recorded here rather than silently corrected, because correcting it
needs a measurement nobody has made.

**Spacing is not free to follow the measurement.** If the measured event rate
implies events closer together than a detector's context window, then simulating
at that rate reproduces the **contaminated null** — real coordination inside the
window the threshold is estimated from — which is the trap that made the first
upstream benchmark unusable and cost two weeks of tuning against it. So
``min_sep_sec`` is floored at the context window and the recording is lengthened
to fit, rather than the events being packed closer. When that floor binds, it is
reported: the simulation is then **not** at the measured event rate, and any
claim about frequency has to say so.

How well the loop actually recovers what was planted
----------------------------------------------------
Measured 2026-08-16 by round trip — plant known coordination, assess it,
re-derive — over 8 seeds at the bench's own settings (33 ROI, 0.0096 Hz, 18%
participation, 0.36 s jitter, 15 events in 45 min). Median recovery:

=====  ==============  ==========  ============  ===================================
K      participants    jitter      frequency     what fails
=====  ==============  ==========  ============  ===================================
3      +1%             +10%        **+60%**      background pairs clear K=3
4      +18%            +9%         -7%           the compromise
6      +18%            +8%         **-77%**      most events never reach K=6
=====  ==============  ==========  ============  ===================================

Three things follow, and none of them is obvious from the algorithm.

**K=4 is the defensible default** — it is the only value where no measure is
badly wrong, and it is what this lab's own measurements used. It is still a
judgement call, and the assessment reports a scan rather than choosing.

**Participation is biased UP by K**, because the measure only sees clusters that
cleared K: a selection effect, not noise, and it grows with K until the event
count collapses. A generator parameterized at K=4 recruits about a fifth more
ROIs than the recording did.

**Jitter is biased up ~9% at every K.** The +/-Wm gather admits onsets that were
not participants, which inflates the SD. It is stable across K and seeds, so it
is a known offset rather than a reason to distrust the number — but a simulation
built from it is slightly looser than the recording it imitates, which makes
detection slightly harder rather than easier. That is the safe direction, and it
is not a licence to leave it uncorrected.
"""

from __future__ import annotations

from dataclasses import dataclass, field

import numpy as np

CONTEXT_WIN_SEC = 120.0
"""The widest context window the six detectors estimate a null over.

Event spacing below this puts real coordination inside the null — the
contaminated null. It is a property of the detectors, not of the preparation,
which is why it is a floor imposed on the simulation rather than a measurement.
"""


@dataclass
class GeneratorParams:
    """Generator settings derived from an assessment, plus what is not known.

    ``kwargs`` is what :func:`~bugarach.simulate.simulate_coordination` takes.
    ``sweep`` names parameters the measurement could not ground, each with the
    range to randomize over — **read it**; a caller that uses ``kwargs`` alone is
    simulating at a point estimate the assessment never supported.
    """

    kwargs: dict
    sweep: dict = field(default_factory=dict)
    notes: list[str] = field(default_factory=list)
    """Every assumption made, in words. Travels with the parameters so a model's
    provenance does not stop at "some numbers"."""

    @property
    def grounded(self) -> bool:
        """True when nothing had to be swept. Rare, and worth checking."""
        return not self.sweep

    def summary(self) -> str:
        out = [f"{k}={v!r}" for k, v in sorted(self.kwargs.items())]
        s = "generator: " + ", ".join(out)
        if self.sweep:
            s += "\nSWEEP (not grounded): " + ", ".join(
                f"{k} over {v}" for k, v in sorted(self.sweep.items()))
        if self.notes:
            s += "\n" + "\n".join(f"  - {n}" for n in self.notes)
        return s


# When tightness cannot be measured, this is the range to sweep instead of
# inventing a number. Spans an order of magnitude around the values seen across
# this lab's own baseline recordings, which is wide enough to cover a rig that
# differs and narrow enough to stay physical.
JITTER_SWEEP_SEC = (0.05, 1.5)

# Likewise for participation, expressed as a fraction of n_roi.
PARTICIPATION_SWEEP = (0.06, 0.45)


def generator_params(a, *, context_win_sec: float = CONTEXT_WIN_SEC,
                     n_levels: int = 3, events_per_level: int = 5,
                     duration_sec: float | None = None,
                     grid_sec: float = 0.1) -> GeneratorParams:
    """Generator kwargs from one :class:`~bugarach.assess.Assessment`.

    a: an assessment at ONE ``min_rois``. Which K is a judgement call the
      assessment deliberately does not make for you — it reports a scan — so pick
      it, having looked (see
      ``docs/todo/2026-08-16-assessment-needs-a-human-in-the-loop.md``).
    context_win_sec: the null window spacing must clear. Lower it only if every
      detector and model downstream estimates its null over less.
    duration_sec: recording length to generate. ``None`` derives the shortest
      length that fits the events at the required spacing, which is usually
      longer than the window that was measured.
    """
    if not a.meets_floor:
        raise ValueError(
            "assessment did not meet the window floor — its measures are NaN, "
            "and parameterizing a generator from them would invent a recording "
            "out of an exclusion")

    notes: list[str] = []
    sweep: dict = {}
    n_roi = int(a.n_roi)

    # --- background rate ------------------------------------------------------
    # THE MEAN, AND IT TRAVELS WITH A FLAG SAYING SO.
    #
    # This used to hand `roi_rate_med` — a median — to `bg_rate_hz`, which
    # `simulate.py` documents as the mean. It has been harmless only because
    # nothing here sets `bg_rate_shape`, so the field is flat and its mean and
    # median are the same number. The day `MEASURED_RATE_SHAPE` is wired in,
    # that line becomes wrong by about a factor of five with nothing to catch it.
    #
    # The mean is also the better estimator rather than merely the matching one:
    # at a realistic 33 ROIs the sample median of a Gamma(0.275) field spans
    # 0.56 to 5.56 mHz between its 5th and 95th percentiles around a population
    # value of 2.14, and comes back exactly zero about one run in a hundred.
    bg = float(a.roi_rate_mean)
    bg_stat = "mean"
    if not np.isfinite(bg):
        # An assessment from before `roi_rate_mean` existed. Convert rather than
        # mislabel, and say so.
        bg = float(a.roi_rate_med)
        bg_stat = "median"
        notes.append(
            "roi_rate_mean is absent, so bg_rate_hz comes from the median and "
            "is flagged as one; the generator converts it")
    notes.append(
        f"bg_rate_hz={bg:.4g} is the assessment's TOTAL per-ROI rate, which "
        "includes coordinated events; the generator treats it as background "
        "only, so the background is biased slightly high")

    # --- participation --------------------------------------------------------
    if np.isfinite(a.part_n_obs) and a.part_n_obs >= 1 and n_roi:
        centre = float(a.part_n_obs) / n_roi
        # Keep a spread around the measured centre rather than collapsing to it,
        # so recall still resolves a participant floor — the bench's own reason.
        levels = tuple(round(min(1.0, max(1.0 / n_roi, centre * m)), 4)
                       for m in (1.6, 1.0, 0.6))[:n_levels]
        notes.append(
            f"participation centred on the measured {a.part_n_obs:.3g} of "
            f"{n_roi} ROI ({centre:.1%}), spread 0.6-1.6x so a participant "
            "floor stays resolvable")
    else:
        levels = (0.30, 0.18, 0.10)[:n_levels]
        sweep["participation"] = PARTICIPATION_SWEEP
        notes.append("participation NOT measured (no clusters formed) — sweep it")

    # --- tightness ------------------------------------------------------------
    if a.jit_defined and np.isfinite(a.jit_obs):
        jitter = float(a.jit_obs)
        notes.append(
            f"jitter_sec={jitter:.3g} from the measured within-cluster onset SD "
            f"(null {a.jit_null:.3g}, excess {a.jit_excess:+.3g})")
    else:
        jitter = float(np.mean(JITTER_SWEEP_SEC))
        sweep["jitter_sec"] = JITTER_SWEEP_SEC
        notes.append(
            "jitter_sec NOT measured — jit_defined is False, so the observed or "
            "surrogate ensemble formed no cluster and there is no tightness "
            "comparison. Sweep it; do not read jit_obs as a measurement")

    # --- how many events, and how far apart -----------------------------------
    n_events = int(n_levels * events_per_level)
    rate_permin = float(a.clusters_permin) if np.isfinite(a.clusters_permin) else 0.0
    if rate_permin > 0:
        measured_interval = 60.0 / rate_permin
    else:
        measured_interval = float("inf")
        sweep["min_sep_sec"] = (context_win_sec, 4 * context_win_sec)
        notes.append("event frequency NOT measured (no clusters) — sweep spacing")

    min_sep = max(context_win_sec, measured_interval if np.isfinite(measured_interval)
                  else context_win_sec)
    if np.isfinite(measured_interval) and measured_interval < context_win_sec:
        notes.append(
            f"measured spacing {measured_interval:.0f}s is INSIDE the "
            f"{context_win_sec:.0f}s null window, so it was raised to the "
            "window: simulating at the measured rate would rebuild the "
            "contaminated null. This recording is NOT at the measured event "
            "frequency, and a frequency claim from it is invalid")

    # The generator needs a mean interval above the floor and refuses rather than
    # packing events closer, so the duration follows the spacing, never the
    # other way round.
    need = min_sep * (n_events + 1) * 1.15 + 2 * 5.0
    dur = float(duration_sec) if duration_sec else float(np.ceil(max(need, a.win_dur)))
    if duration_sec is None and dur > a.win_dur:
        notes.append(
            f"duration_sec={dur:.0f} exceeds the {a.win_dur:.0f}s window that was "
            "measured — the spacing floor needs the room")

    kwargs = dict(
        n_roi=n_roi, bg_rate_hz=bg, bg_rate_stat=bg_stat, participation=levels,
        n_per_level=tuple([events_per_level] * len(levels)),
        jitter_sec=jitter, min_sep_sec=min_sep, duration_sec=dur,
        grid_sec=grid_sec,
    )
    return GeneratorParams(kwargs=kwargs, sweep=sweep, notes=notes)
