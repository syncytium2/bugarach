"""Gaps between planted events drawn from intervals measured in the real data.

ADR-0010 (Proposed, 2026-09-25) part 2: the bench plants events at intervals measured in the
recordings, not at the fixed minimum of 120 s every bench recording has used. This module is the
**preparation** for that and nothing more. It reads the measured intervals and hands the generator
something to draw from; :func:`bugarach.simulate.simulate_coordination` does the drawing when a
caller passes ``gap_source=`` and a ``gap_mix`` below 1. **Nothing turns it on.** With neither
option set every recording is byte-identical to what it was
(``tests/test_real_intervals_off_by_default.py`` pins that on all three benches).

The file it reads
-----------------
The measurement is WSMIP065's (``<darkroom>/bugarach/2026-09-25-real-intervals/``): for each
recording and stream, the gaps between neighbouring peaks of the co-active ROI count at or above
that window's floor, baseline windows only, measured without a detector (ADR-0010 part 2). No
schema had been written when this loader was, so this one is **a request to match**: one JSON
object per stream,

.. code-block:: json

    {
      "stream": "fast",
      "pooled": {"gaps_sec": [4.1, 12.0, 33.5]},
      "by_group": {
        "DI":   {"gaps_sec": [...]},
        "OVX":  {"gaps_sec": [...]},
        "MALE": {"gaps_sec": [...]},
        "ORX":  {"gaps_sec": [...]}
      }
    }

- ``gaps_sec`` is every measured gap, in seconds, one value per gap, not a histogram. ``gaps`` is
  accepted as an alias.
- ``by_group`` is optional, and its keys match :data:`bugarach.groups.GROUP_ORDER` whatever their
  case (exports have spelled MALE both ways).
- Any other key (provenance, counts, the dataset stamp) is ignored here and kept in the file.
- A file may also hold a JSON list of such objects, one per stream.

:func:`load_gaps` takes an explicit ``path`` (a file, or a folder of them) or, with none, the
folder above under :func:`bugarach.paths.darkroom`; in a folder it takes the file whose
``"stream"`` is the one asked for.

Which pool
----------
``pool="pooled"`` (the default) draws from all four groups together; ``pool="DI"`` and so on
draws from one group. ADR-0010's open point 1 (pool unless the groups differ materially) is
Tony's, and this module decides nothing about it: it offers both.
"""
from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path

import numpy as np

from bugarach.groups import GROUP_ORDER

INTERVALS_DIR = "2026-09-25-real-intervals"
"""The darkroom folder WSMIP065's measurement is written to."""

POOLED = "pooled"
"""The pool name for all groups together."""

GAP_KEYS = ("gaps_sec", "gaps")
"""Where a pool's gaps are read from, in order of preference."""

STREAMS = ("fast", "slow", "combined")
"""The three streams the benches score; ``bench``, ``bench_slow`` and ``bench_combined``."""


@dataclass(frozen=True)
class GapDistribution:
    """Measured gaps for one stream and one pool, ready to draw from.

    Drawing is a bootstrap: each drawn gap is one of :attr:`gaps_sec`, chosen uniformly with
    replacement from the recording's own random generator. So the planted gaps follow the measured
    distribution exactly, short gaps and long ones in their measured proportion, without a fitted
    shape standing between the two.
    """

    stream: str
    pool: str
    gaps_sec: tuple[float, ...]
    source: str = ""
    """The file's name (never its full path, which carries a person's name on some machines)."""

    def __post_init__(self):
        g = np.asarray(self.gaps_sec, dtype=float).ravel()
        if g.size == 0:
            raise ValueError(f"no gaps for stream {self.stream!r}, pool {self.pool!r}")
        if not np.all(np.isfinite(g)) or np.any(g <= 0):
            raise ValueError(
                f"gaps for stream {self.stream!r}, pool {self.pool!r} must be finite and "
                "positive seconds")
        object.__setattr__(self, "gaps_sec", tuple(float(x) for x in g))

    def draw(self, rng, n: int) -> np.ndarray:
        """``n`` gaps, resampled with replacement using ``rng`` (a ``numpy.random.RandomState``)."""
        g = np.asarray(self.gaps_sec, dtype=float)
        return g[rng.randint(0, g.size, size=int(n))]

    def summary(self) -> dict:
        """What a recording's ``gt.params`` records about where its gaps came from."""
        g = np.asarray(self.gaps_sec, dtype=float)
        return dict(stream=self.stream, pool=self.pool, source=self.source, n_gaps=int(g.size),
                    median_sec=float(np.median(g)), min_sec=float(g.min()),
                    max_sec=float(g.max()))


def as_gap_distribution(source) -> GapDistribution:
    """``source`` as a :class:`GapDistribution`: one already, or a bare sequence of seconds."""
    if isinstance(source, GapDistribution):
        return source
    return GapDistribution(stream="given", pool="given", gaps_sec=tuple(np.ravel(source)))


def _gaps_of(entry, what: str) -> list:
    if not isinstance(entry, dict):
        raise ValueError(f"{what} must be an object holding 'gaps_sec', got {type(entry).__name__}")
    for k in GAP_KEYS:
        if k in entry:
            return entry[k]
    raise ValueError(f"{what} has none of {list(GAP_KEYS)}")


def parse_gaps(doc: dict, *, pool: str = POOLED, source: str = "") -> GapDistribution:
    """One stream's JSON object (schema in the module docstring), read into a distribution."""
    if not isinstance(doc, dict) or "stream" not in doc:
        raise ValueError("a real-intervals document is an object with a 'stream' key")
    stream = str(doc["stream"])
    if pool == POOLED:
        if POOLED not in doc:
            raise ValueError(f"{source or 'document'}: stream {stream!r} has no 'pooled' entry")
        return GapDistribution(stream, POOLED, tuple(_gaps_of(doc[POOLED], "'pooled'")), source)
    want = str(pool).upper()
    if want not in GROUP_ORDER:
        raise ValueError(f"pool must be {POOLED!r} or one of {list(GROUP_ORDER)}, got {pool!r}")
    groups = {str(k).upper(): v for k, v in (doc.get("by_group") or {}).items()}
    if want not in groups:
        have = [g for g in GROUP_ORDER if g in groups]
        raise ValueError(f"{source or 'document'}: stream {stream!r} has no group {want!r} "
                         f"(has {have})")
    return GapDistribution(stream, want, tuple(_gaps_of(groups[want], f"group {want!r}")), source)


def _docs_in(path: Path) -> list:
    doc = json.loads(path.read_text(encoding="utf-8"))
    return doc if isinstance(doc, list) else [doc]


def default_dir() -> Path:
    """The measurement's darkroom folder; refuses, rather than guesses, when there is no darkroom."""
    from bugarach import paths

    d = paths.darkroom(INTERVALS_DIR)
    if d is None:
        raise FileNotFoundError(paths.unresolved_message("path="))
    return d


def load_gaps(stream: str, *, pool: str = POOLED, path=None) -> GapDistribution:
    """The measured gaps for ``stream`` (``"fast"``, ``"slow"`` or ``"combined"``) and ``pool``.

    ``path`` is a JSON file or a folder of them; ``None`` is :func:`default_dir`. In a folder the
    file whose ``"stream"`` is ``stream`` is used, and two such files are refused rather than one
    picked.
    """
    p = default_dir() if path is None else Path(path)
    files = sorted(p.glob("*.json")) if p.is_dir() else [p]
    if not files or not files[0].exists():
        raise FileNotFoundError(f"no real-intervals JSON at {p}")
    found = [(f, d) for f in files for d in _docs_in(f)
             if isinstance(d, dict) and str(d.get("stream")) == stream]
    if not found:
        raise FileNotFoundError(f"no real-intervals document for stream {stream!r} in {p}")
    if len(found) > 1:
        raise ValueError(f"{len(found)} documents for stream {stream!r} in {p}: "
                         f"{sorted({f.name for f, _ in found})}")
    f, doc = found[0]
    return parse_gaps(doc, pool=pool, source=f.name)


def bench_overrides(stream: str, *, mix: float, pool: str = POOLED, path=None) -> dict:
    """Generator settings that turn empirical gaps on, for a bench maker's ``**overrides``.

    ``bench.make_recording("baseline_busy", 1, **bench_overrides("fast", mix=0.0))``. ``mix`` is
    the share of gaps kept at the old spacing (1.0 is today's recording exactly); see
    :func:`bugarach.simulate.simulate_coordination`.
    """
    return dict(gap_source=load_gaps(stream, pool=pool, path=path), gap_mix=float(mix))
