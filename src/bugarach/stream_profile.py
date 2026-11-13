"""One object per stream holding what was measured, what is simulated and what is tuned.

**Why this exists (ADR-0020, Tony, 2026-11-11: "integrate the paths first").** Two bodies of work
described the same loop and shared no code path:

* the three benches (:mod:`bugarach.bench`, :mod:`bugarach.bench_slow`,
  :mod:`bugarach.bench_combined`), each a module of constants measured on one stream, read by the
  search, budget, training and figure tools through a ``{"fast": "bugarach.bench", ...}`` table
  that a dozen tools each carry a copy of;
* the synthetic-validation scripts (``docs/learned/synthetic_validation/``), which type their own
  cells, rates and jitters and call :func:`bugarach.simulate.simulate_coordination` directly, so
  "the lab's regime" there is a number copied from a page.

A :class:`StreamProfile` is the seam between them. It **reads** a bench module and owns no number
of its own, so the fast, slow and combined values stay exactly where they are and nothing a
published score depends on can move. ``tests/test_stream_profile.py`` holds that: every field is
compared with the module constant it came from.

This is the first step of ``docs/todo/2026-09-21-one-stream-aware-bench.md``, not the whole of
it. That rebuild inverts the dependency (the scoring functions take a profile, and the three
modules become three profile records). Until it lands the modules stay the owners, and this
module is the one place a tool or a script asks "which bench is this stream's".

**Symbols.** :meth:`StreamProfile.source` returns the planted source in the synthetic-validation
goal page's notation (N, k, sigma, b, E), so a grid can be centred on a stream without retyping
its values.
"""

from __future__ import annotations

import importlib
from dataclasses import dataclass
from types import ModuleType

STREAMS = ("fast", "slow", "combined")
"""The lab's three streams, in the order every page lists them (fast first: goals README,
decision 4). FOUNDATIONS §3 keeps streams generic; these three are this lab's benches."""

MODULES = {"fast": "bugarach.bench", "slow": "bugarach.bench_slow",
           "combined": "bugarach.bench_combined"}
"""Which module owns each stream's constants. The table a dozen tools each carry a copy of."""


def bench_module(stream: str) -> ModuleType:
    """The bench module that owns ``stream``'s constants. Refuses a stream it does not know."""
    if stream not in MODULES:
        raise ValueError(f"no bench for stream {stream!r}; the benches are {', '.join(STREAMS)}")
    return importlib.import_module(MODULES[stream])


@dataclass(frozen=True)
class Source:
    """One planted source of coordinated events, in the goal page's symbols."""

    stream: str
    regime: str
    n_cells: int                      # N
    participants: tuple[float, ...]   # k per planted level, cells (participation x N)
    jitter_sec: float                 # sigma
    bg_rate_hz: float                 # b, per cell
    n_events: int                     # E, coordinated events per recording
    duration_sec: float

    @property
    def events_per_sec(self) -> float:
        """lambda, the coordinated event rate."""
        return self.n_events / self.duration_sec


@dataclass(frozen=True)
class StreamProfile:
    """A read-only view of one stream's bench. Every value is the module's own."""

    stream: str
    module: ModuleType

    # --- what was measured -------------------------------------------------------------------
    @property
    def measured(self) -> dict[str, float]:
        """Every value the bench claims was measured off real recordings."""
        return dict(self.module.measured_constants())

    @property
    def measured_record(self) -> str:
        """The repo-relative JSON the measuring tool wrote, with intervals."""
        return self.module.MEASURED_RECORD

    @property
    def measured_role(self) -> str:
        """The ``current_export.toml`` role the measurement read."""
        return self.module.MEASURED_ROLE

    @property
    def provisional(self) -> bool:
        """True while any constant is a stand-in and not a measurement on this stream."""
        return bool(getattr(self.module, "PROVISIONAL", False))

    # --- what is simulated -------------------------------------------------------------------
    @property
    def regimes(self) -> dict[str, dict]:
        """The background axis: quiet and busy, from baseline recordings only (FOUNDATIONS §9)."""
        return {k: dict(v) for k, v in self.module.REGIMES.items()}

    def recording(self, *, decoys: bool = True) -> dict:
        """The planted recording's generator arguments, a copy.

        ``decoys=False`` gives the recording ADR-0019 rules for: planted coordination labelled
        negative is retired, so ``n_distractors`` is 0. The module still carries its decoys
        (``docs/todo/2026-10-23-rate-matched-negatives-and-the-bench-without-decoys.md``), which
        is why this is an argument and not the default: the default must reproduce the module.
        """
        spec = dict(self.module.BENCH_RECORDING)
        if not decoys:
            spec["n_distractors"] = 0
        return spec

    @property
    def decoys(self) -> int:
        """Decoys the module still plants per recording. ADR-0019 retired them; 0 when done."""
        return int(self.module.BENCH_RECORDING.get("n_distractors", 0))

    def source(self, regime: str = "baseline_quiet") -> Source:
        """The planted source at one background, in the goal page's symbols."""
        if regime not in self.module.REGIMES:
            raise ValueError(f"no regime {regime!r} on the {self.stream} bench; "
                             f"it has {', '.join(self.module.REGIMES)}")
        spec = self.module.BENCH_RECORDING
        n = int(spec["n_roi"])
        return Source(
            stream=self.stream, regime=regime, n_cells=n,
            participants=tuple(float(p) * n for p in spec["participation"]),
            jitter_sec=float(spec["jitter_sec"]),
            bg_rate_hz=float(self.module.REGIMES[regime]["bg_rate_hz"]),
            n_events=int(sum(spec["n_per_level"])),
            duration_sec=float(spec["duration_sec"]))

    def simulate(self, regime: str, seed: int, **overrides):
        """A planted recording and its truth, built by the module's own maker."""
        return self.module.make_recording(regime, seed, **overrides)

    def simulate_null(self, seed: int, **overrides):
        """A recording with nothing planted, built by the module's own maker."""
        return self.module.make_null_recording(seed, **overrides)

    # --- what is tuned -----------------------------------------------------------------------
    @property
    def detectors(self) -> tuple[str, ...]:
        return tuple(self.module.DETECTORS)

    @property
    def operating_points(self) -> dict:
        """Detector name to its stored :class:`~bugarach.bench.OperatingPoint`."""
        return dict(self.module.OPERATING_POINTS)

    @property
    def budgets(self) -> dict[str, dict[str, float]]:
        """The three false-alarm budgets, each detector name to its limit."""
        m = self.module
        return {"probe_per_min": dict(m.MAX_PROBE_PER_MIN),
                "false_positives_per_hour": dict(m.MAX_FALSE_POSITIVES_PER_HOUR),
                "precision_drop": dict(m.MAX_PRECISION_DROP)}

    def summary(self) -> dict:
        """What a run record needs to say which profile it was made on."""
        src = self.source()
        return {"stream": self.stream, "module": self.module.__name__,
                "measured_record": self.measured_record, "measured_role": self.measured_role,
                "provisional": self.provisional, "decoys_per_recording": self.decoys,
                "n_cells": src.n_cells, "participants": list(src.participants),
                "jitter_sec": src.jitter_sec,
                "bg_rate_hz": {r: v["bg_rate_hz"] for r, v in self.regimes.items()},
                "detectors": list(self.detectors)}


def profile(stream: str) -> StreamProfile:
    """The profile of one stream."""
    return StreamProfile(stream=stream, module=bench_module(stream))


def profiles() -> dict[str, StreamProfile]:
    """All three, in :data:`STREAMS` order."""
    return {s: profile(s) for s in STREAMS}


def _main() -> int:
    import json

    print(json.dumps({s: p.summary() for s, p in profiles().items()}, indent=1))
    return 0


if __name__ == "__main__":
    raise SystemExit(_main())
