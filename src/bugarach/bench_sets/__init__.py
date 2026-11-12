"""A bench built from a measured record: one per stream and per set of recordings.

``importlib.import_module("bugarach.bench_sets.fast_di")`` returns a bench module with the same
names as :mod:`bugarach.bench` (``make_recording``, ``REGIMES``, ``OPERATING_POINTS``, ...), so
every tool that takes a bench by module name takes a set the same way. The values come from
``docs/learned/bench_sets/fast_di.json``, written by ``tools/measure_bench_sets.py``.

**Why (Tony, 2026-11-12).** One synthetic set holding both groups of the default folder, and
one per group; each tuned on its own and scored on the others. The three bench modules hold one
hand-transcribed set of constants per stream, so a second set had nowhere to live. A set is the
stream's own bench with the record's values in place of the module's: this is item 4 of the
stream-readiness route's *Owed* list, a bench that ends stage 1 as a file.

**How a set is made.** The stream's bench module is executed again under the set's name, so
the set has its own copies of the constants and of the functions that read them, and the
stream's module is not touched: a September score cannot move. Then the record is applied
(:func:`_apply`):

* cells, the middle participation level, jitter, the two backgrounds, the rate and burst
  shapes, the event widths and the elevated-rate level are the record's;
* the outer participation levels keep the stream bench's ratios to the middle one, as the
  stream benches do (they are chosen, so that recall resolves a participant floor);
* planted gaps and the number of planted events are the set's own measured gaps and events per
  hour, under any spacing but ``"bench"``;
* **no decoys** (ADR-0019). The stream modules still plant theirs.

**What a set inherits and does not re-measure**, each named in :data:`INHERITED` on the module:
the detectors' shipped settings and grids, the three false-alarm limits (measured on the
stream's September bench by ``tools/measure_slow_budgets.py``), the recording's length, and the
background grid of the background curve.

Workers reach a set by name. This package installs an import finder for its own submodules, so
a process spawned on Windows that imports ``bugarach.bench_sets.fast_di`` builds the same module
from the same record.
"""
from __future__ import annotations

import importlib.abc
import importlib.util
import json
import sys
from pathlib import Path

PREFIX = __name__ + "."
RECORDS_DIR = Path(__file__).resolve().parents[3] / "docs" / "learned" / "bench_sets"
"""Where the records live, in the repository, so a clone on any machine builds the same sets."""

STREAM_MODULES = {"fast": "bugarach.bench", "slow": "bugarach.bench_slow",
                  "combined": "bugarach.bench_combined"}
INHERITED = ("OPERATING_POINTS", "FULL_GRIDS", "MAX_PROBE_PER_MIN",
             "MAX_FALSE_POSITIVES_PER_HOUR", "MAX_PRECISION_DROP", "BACKGROUND_GRID",
             "duration_sec")
MAX_PARTICIPATION = 0.95
RECORDING_DICTS = ("BENCH_RECORDING", "CROWDED_RECORDING", "TAIL_RECORDING")


def names() -> list[str]:
    """Every set with a record, sorted."""
    return sorted(p.stem for p in RECORDS_DIR.glob("*.json"))


def record_path(name: str) -> Path:
    return RECORDS_DIR / f"{name}.json"


def record(name: str) -> dict:
    path = record_path(name)
    if not path.exists():
        raise ModuleNotFoundError(
            f"no bench set {name!r}: there is no {path.name} in docs/learned/bench_sets "
            f"(have {', '.join(names()) or 'none'}). tools/measure_bench_sets.py writes them.")
    return json.loads(path.read_text(encoding="utf-8"))


def module_name(name: str) -> str:
    """The importable name of a set, for a tool that passes benches by module name."""
    return PREFIX + name


def load(name: str):
    """The bench module of one set."""
    return importlib.import_module(module_name(name))


def stream_of(name: str) -> str:
    """The stream a set belongs to (``fast_di`` is a fast bench)."""
    return str(record(name)["stream"])


def _counts(total: int, n_levels: int) -> tuple[int, ...]:
    """``total`` events over the participation levels, as ``bench.realistic_counts`` splits
    them: evenly, the middle (measured) level first, then the highest."""
    base, rem = divmod(int(total), n_levels)
    counts = [base] * n_levels
    order = (n_levels // 2, 0, n_levels - 1) if n_levels >= 3 else tuple(range(n_levels))
    for i in order[:rem]:
        counts[i] += 1
    return tuple(counts)


class _FastWithSetSpacing:
    """``bugarach.bench`` as a slow or combined set sees it: every name is the real module's,
    except ``spacing_overrides``, which plants the set's own gaps."""

    def __init__(self, real, spacing_overrides):
        self._real = real
        self.spacing_overrides = spacing_overrides

    def __getattr__(self, attr):
        return getattr(self._real, attr)


def _apply(mod, rec: dict) -> None:
    """Put the record's values into a freshly executed copy of the stream's bench module."""
    from bugarach import bench as fast
    from bugarach import real_intervals as ri

    stream, v = rec["stream"], rec["values"]
    mid_old = float(mod.BENCH_RECORDING["participation"][1])
    mid_new = float(v["participation"]["measured"])
    participation = tuple(min(MAX_PARTICIPATION, float(p) * mid_new / mid_old)
                          for p in mod.BENCH_RECORDING["participation"])
    burst = float(v["burst_shape_300s"]["measured"])
    if isinstance(mod.MEASURED_BURST_SHAPE, tuple):          # fast: (300 s, 60 s)
        burst = (burst, float(v["burst_shape_60s"]["measured"]))
    mod.MEASURED_RATE_SHAPE = float(v["rate_shape"]["measured"])
    mod.MEASURED_BURST_SHAPE = burst
    widths = tuple(float(w) for w in rec["width_quantiles"])
    if hasattr(mod, "MEASURED_WIDTH_QUANTILES"):
        mod.MEASURED_WIDTH_QUANTILES = widths

    changes = dict(
        n_roi=int(round(float(v["n_roi"]["measured"]))),
        participation=participation,
        jitter_sec=float(v["jitter_sec"]["measured"]),
        distractor_frac=float(mod.BENCH_RECORDING["distractor_frac"]) * mid_new / mid_old,
        bg_rate_shape=mod.MEASURED_RATE_SHAPE,
        bg_burst_shape=mod.MEASURED_BURST_SHAPE,
        n_distractors=0,                                     # ADR-0019
    )
    if not hasattr(mod, "MEASURED_WIDTH_QUANTILES"):
        # The fast bench takes the simulator's default widths; a fast set states its own.
        changes["width_quantiles"] = widths
    for key in RECORDING_DICTS:
        getattr(mod, key).update(changes)
    mod.REGIMES["baseline_quiet"]["bg_rate_hz"] = float(v["regime_quiet_hz"]["measured"])
    mod.REGIMES["baseline_busy"]["bg_rate_hz"] = float(v["regime_busy_hz"]["measured"])
    mod.NULL_RECORDING["bg_rate_hz"] = mod.REGIMES["baseline_quiet"]["bg_rate_hz"]
    mod.ELEVATED_RATE_RECORDING["hot_rate_hz"] = float(rec["elevated_rate_hz"])

    gaps = ri.GapDistribution(stream, str(rec["group"]), tuple(rec["gaps_sec"]),
                              f"{rec['set']}.json")
    per_hour = float(rec["events"]["events_per_hour"])

    def spacing_overrides(_stream: str, recording: dict) -> dict:
        """The set's own gaps and event count; nothing under the ``"bench"`` spacing."""
        if fast.spacing() == "bench":
            return {}
        total = int(round(per_hour * recording["duration_sec"] / 3600.0))
        return dict(gap_source=gaps, gap_mix=0.0,
                    n_per_level=_counts(total, len(recording["n_per_level"])))

    if stream == "fast":
        mod.spacing_overrides = spacing_overrides
    else:
        mod._fast = _FastWithSetSpacing(fast, spacing_overrides)

    mod.SET = str(rec["set"])
    mod.SET_GROUP = str(rec["group"])
    mod.SET_RECORDINGS = tuple(rec["recordings"])
    mod.MEASURED_STREAM = stream
    mod.MEASURED_RECORD = f"docs/learned/bench_sets/{rec['set']}.json"
    mod.MEASURED_DATASET = dict(rec["dataset"])
    mod.INHERITED = INHERITED
    mod.PROVISIONAL = False


class _Finder(importlib.abc.MetaPathFinder, importlib.abc.Loader):
    def find_spec(self, fullname, path=None, target=None):
        if not fullname.startswith(PREFIX) or "." in fullname[len(PREFIX):]:
            return None
        return importlib.util.spec_from_loader(fullname, self)

    def create_module(self, spec):
        return None

    def exec_module(self, module):
        name = module.__name__[len(PREFIX):]
        rec = record(name)
        base = STREAM_MODULES.get(rec["stream"])
        if base is None:
            raise ImportError(f"bench set {name!r} names stream {rec['stream']!r}; the benches "
                              f"are {', '.join(STREAM_MODULES)}")
        origin = importlib.util.find_spec(base).origin
        module.__file__ = origin
        module.__package__ = "bugarach"            # the stream modules use relative imports
        code = compile(Path(origin).read_text(encoding="utf-8"), origin, "exec")
        exec(code, module.__dict__)                # noqa: S102  our own module's source
        _apply(module, rec)


if not any(isinstance(f, _Finder) for f in sys.meta_path):
    sys.meta_path.append(_Finder())
