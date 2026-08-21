"""What a recording looks like, as one value instead of twenty-five arguments.

``simulate_coordination`` grew to 25 keyword parameters, four of them the
background model, three of those four inside two days as the model learned that
real fields are uneven across ROIs and clumpy in time. That churn is the project
working; the cost is that it arrives through every caller's call site. These
objects move it behind one value:

    spec = RecordingSpec.from_kwargs(**settings)   # or from a fitting stage
    sim, gt = simulate_coordination(spec, seed=1)

Adding a background axis then changes no call site for anyone who *received* a
spec and passed it on — which is every stage of the workflow app. A caller that
**constructs** a :class:`BackgroundModel` by naming fields is as coupled as it
ever was; what changes is that the coupling is countable, a grep for one class
name rather than for four keyword names that will be six.

Design proposal and its open questions: ``docs/parameter_spec_proposal.md``.

What is deliberately NOT here
-----------------------------
The **promiscuity probe** and the **distractors**. They are not properties of a
real recording and cannot be fitted from one — they are test constructs, planted
to catch a detector that keys on rate or on coincidence. They belong to the
bench, which is a different object with a different job:

    the generator makes data; the bench is a standard — a pinned recipe, pinned
    detector settings and a scoring rule — and it CALLS the generator.

Keeping them out is what holds that boundary in code rather than in prose.
Also absent: ``seed``, ``streams``, ``slice_id`` and ``regions``, which describe
a particular *call* rather than the recording being described.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass, field, replace

__all__ = ["BackgroundModel", "CoordinationModel", "RecordingSpec"]


def _as_tuple(v) -> tuple:
    if v is None:
        return ()
    if isinstance(v, (tuple, list)):
        return tuple(float(x) for x in v)
    return (float(v),)


@dataclass(frozen=True)
class BackgroundModel:
    """How background events are distributed. Every field is fittable from data.

    ``rate_hz`` is the **mean** per-ROI rate, and that word is load-bearing: the
    original calibration took the mean of a heavily right-skewed distribution and
    gave it to every ROI, which is how the generator ended up simultaneously
    busier than a typical real ROI and missing every busy one. The mean is only
    the right summary when ``rate_shape`` is set.
    """

    rate_hz: float
    rate_shape: float | None = None
    """Gamma shape of the per-ROI rate. ``None`` gives every ROI ``rate_hz`` —
    a flat field. Smaller means a few busy ROIs and many near-silent ones."""
    burst_shape: tuple[float, ...] = ()
    """Gamma shape of the per-bin rate multiplier, one per time scale. Empty is
    a constant rate in time."""
    burst_bin_sec: tuple[float, ...] = ()
    """The scales ``burst_shape`` was fitted at, coarsest first. One scale cannot
    reproduce real data: independent bins stop being over-dispersed once the
    window exceeds the bin, and real ROIs keep getting more over-dispersed the
    wider you look."""

    def __post_init__(self):
        object.__setattr__(self, "burst_shape", _as_tuple(self.burst_shape))
        object.__setattr__(self, "burst_bin_sec", _as_tuple(self.burst_bin_sec))
        if len(self.burst_shape) != len(self.burst_bin_sec):
            raise ValueError(
                f"burst_shape and burst_bin_sec must name the same number of "
                f"scales ({len(self.burst_shape)} vs {len(self.burst_bin_sec)})")

    @property
    def is_flat(self) -> bool:
        """True when this is the homogeneous background the generator shipped
        with — no ROI-to-ROI spread and no clumping in time."""
        return self.rate_shape is None and not self.burst_shape

    def as_kwargs(self) -> dict:
        """The keyword form ``simulate_coordination`` has always taken."""
        return dict(
            bg_rate_hz=self.rate_hz,
            bg_rate_shape=self.rate_shape,
            bg_burst_shape=(list(self.burst_shape) if self.burst_shape else None),
            bg_burst_bin_sec=(list(self.burst_bin_sec) if self.burst_bin_sec
                              else 60.0),
        )

    @classmethod
    def from_kwargs(cls, **kw) -> "BackgroundModel":
        """Read a keyword call back into a model. Inverse of :meth:`as_kwargs`."""
        shape = kw.get("bg_burst_shape")
        bins = kw.get("bg_burst_bin_sec", 60.0)
        return cls(
            rate_hz=kw["bg_rate_hz"],
            rate_shape=kw.get("bg_rate_shape"),
            burst_shape=() if shape is None else _as_tuple(shape),
            burst_bin_sec=() if shape is None else _as_tuple(bins),
        )


@dataclass(frozen=True)
class CoordinationModel:
    """The planted events: how many, how many ROIs each, how tight, how spaced.

    ⚠ Fittable *in principle* and not uniformly in practice. ``jitter_sec`` is
    the standing example — 0.36 s was measured against a statistic whose own
    circular-shift surrogate null is 0.42 s, and it does not round-trip, so a
    per-dataset fit of it would produce a number with no information in it and a
    provenance that reads like a measurement.
    """

    participation: tuple[float, ...]
    n_per_level: tuple[int, ...]
    jitter_sec: float
    min_sep_sec: float
    interval_cv: float = 1.0
    spacing: str = "renewal"
    margin_sec: float = 5.0

    def __post_init__(self):
        if len(self.participation) != len(self.n_per_level):
            raise ValueError(
                f"participation and n_per_level must be the same length "
                f"({len(self.participation)} vs {len(self.n_per_level)})")

    def as_kwargs(self) -> dict:
        return dict(
            participation=tuple(self.participation),
            n_per_level=tuple(self.n_per_level),
            jitter_sec=self.jitter_sec,
            min_sep_sec=self.min_sep_sec,
            interval_cv=self.interval_cv,
            spacing=self.spacing,
            margin_sec=self.margin_sec,
        )

    @classmethod
    def from_kwargs(cls, **kw) -> "CoordinationModel":
        return cls(
            participation=tuple(kw["participation"]),
            n_per_level=tuple(kw["n_per_level"]),
            jitter_sec=kw["jitter_sec"],
            min_sep_sec=kw["min_sep_sec"],
            interval_cv=kw.get("interval_cv", 1.0),
            spacing=kw.get("spacing", "renewal"),
            margin_sec=kw.get("margin_sec", 5.0),
        )


@dataclass(frozen=True)
class RecordingSpec:
    """One recording, described. This is what a dataset gets fitted to.

    ``grid_sec`` has **no default on purpose.** It is the acquisition sampling
    interval, the onset stores do not carry it, and it cannot be recovered from
    onsets — so a default here would be a guess about someone's microscope
    baked into a value object that then travels. It must come from the user.
    Note also that it is not the same knob as a detector's ``grid_dt`` even
    though both name the same physical quantity: this one quantizes planted
    onsets at construction, deciding which bin an event lands in before any
    detector sees it.
    """

    n_roi: int
    duration_sec: float
    grid_sec: float
    background: BackgroundModel
    coordination: CoordinationModel

    def as_kwargs(self) -> dict:
        """Everything ``simulate_coordination`` needs except the call's own
        arguments — ``seed``, ``streams``, ``slice_id``, ``regions`` — and the
        bench's test constructs, which are not properties of a recording."""
        return dict(
            n_roi=self.n_roi,
            duration_sec=self.duration_sec,
            grid_sec=self.grid_sec,
            **self.background.as_kwargs(),
            **self.coordination.as_kwargs(),
        )

    @classmethod
    def from_kwargs(cls, **kw) -> "RecordingSpec":
        """Read a full keyword call back into a spec.

        Round-trips with :meth:`as_kwargs` for every field either one names. Any
        probe or distractor arguments in ``kw`` are ignored — deliberately, since
        they are the bench's and not the recording's.
        """
        return cls(
            n_roi=kw["n_roi"],
            duration_sec=kw["duration_sec"],
            grid_sec=kw.get("grid_sec", 0.1),
            background=BackgroundModel.from_kwargs(**kw),
            coordination=CoordinationModel.from_kwargs(**kw),
        )

    def replace(self, **changes) -> "RecordingSpec":
        """A copy with top-level fields replaced — these objects are frozen."""
        return replace(self, **changes)

    def summary(self) -> dict:
        """A flat, JSON-friendly record of what this describes.

        For stamping on an artifact. Every figure, score and trained model in
        this project was produced against *some* recording, and until now none of
        them said which — every F1 in the repo was measured on a background flat
        in both axes and no artifact records that.
        """
        return {"n_roi": self.n_roi, "duration_sec": self.duration_sec,
                "grid_sec": self.grid_sec,
                "background": asdict(self.background),
                "coordination": asdict(self.coordination)}
