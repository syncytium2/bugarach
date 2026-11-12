"""Close-event test sets, and a score that asks the question per pair.

ADR-0022 (Tony, 2026-11-11): close events are a bench axis of set separations, below 2 s
included, because a person separates events closer than that. Tony, the same day, on the first
run of that axis: *"nothing was optimized or even built on events this close. lets build some
test data sets and see if any of them can be modified to separate close events"*.

**The test set.** One recording is a stream's own bench recording (`bugarach.stream_profile`)
with a share of the gaps between neighbouring planted events set to one separation and the rest
left at the realistic spacing. It is planted by the generator's supported route,
``simulate_coordination(gap_source=, gap_mix=)``, as ``tools/measure_close_events.py`` and
``tools/measure_separation_axis.py`` do; nothing is planted by hand here. A set is named by
``(stream, separation, background, seed)`` and is rebuilt from those four, so it needs no file.

**What recall could not say.** Planted this way, events come as isolated events, pairs and
longer chains, and a detector that joins every pair still recalls about half of them. So the
planted events are sorted by their neighbours (:func:`structure`) and two things are counted
(:func:`pair_score`):

* **a pair is split** when both of its events are matched, each by a call of its own;
* **an isolated event is double-called** when two or more calls fall within tolerance of it.

The second is the control for the first. A setting that breaks every call into fragments splits
every pair and double-calls every isolated event, and has separated nothing.

**Matching is the bench's** (:func:`bugarach.score.score_stream`: one call per event, closest
first, within the bench's tolerance of the call's span), so a pair counts as split under the
rule every other score in this repository uses. With a tolerance wider than the separation, a
stray call beside a joined pair can pass for a split; the double-call rate on isolated events
measures how often such a call exists.
"""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np

from bugarach import real_intervals as ri
from bugarach import score as _score
from bugarach import stream_profile as sp

CLOSE_SHARE = 0.5
"""The share of gaps set to the separation; the simulator's ``gap_mix`` is one minus this."""
ISOLATION_SEC = 20.0
"""How far every other planted event must be for an event or a pair to count as on its own.
Eight times the bench's scoring tolerance, so no call on a neighbour can reach it."""


def make(stream: str, separation_sec: float, regime: str, seed: int, *,
         close_share: float = CLOSE_SHARE):
    """One test recording and its truth: ``(slice, ground truth)``. No decoys (ADR-0019)."""
    return sp.profile(stream).simulate(
        regime, seed, gap_source=ri.as_gap_distribution([float(separation_sec)]),
        gap_mix=1.0 - float(close_share), n_distractors=0)


@dataclass(frozen=True)
class Structure:
    """Planted events sorted by their neighbours. Indices are into ``gt.events``."""

    pairs: tuple[tuple[int, int], ...]
    """Two events one separation apart, with every other event at least the isolation away."""
    isolated: tuple[int, ...]
    """Events with every other event at least the isolation away."""
    other: tuple[int, ...]
    """Everything else: chains of three or more, and events near but not at the separation."""


def structure(gt, separation_sec: float, *, isolation_sec: float = ISOLATION_SEC,
              atol: float = 1e-6) -> Structure:
    """Sort a ground truth's planted events into pairs, isolated events and the rest."""
    t = np.asarray([e.time for e in gt.events], dtype=float)
    order = np.argsort(t, kind="stable")
    ts = t[order]
    n = ts.size
    before = np.concatenate(([np.inf], np.diff(ts)))      # gap to the previous event
    after = np.concatenate((np.diff(ts), [np.inf]))       # gap to the next one
    pairs, isolated, taken = [], [], np.zeros(n, dtype=bool)
    for i in range(n - 1):
        if (abs(after[i] - separation_sec) <= atol and before[i] >= isolation_sec
                and after[i + 1] >= isolation_sec):
            pairs.append((int(order[i]), int(order[i + 1])))
            taken[i] = taken[i + 1] = True
    for i in range(n):
        if not taken[i] and before[i] >= isolation_sec and after[i] >= isolation_sec:
            isolated.append(int(order[i]))
            taken[i] = True
    other = tuple(int(order[i]) for i in range(n) if not taken[i])
    return Structure(pairs=tuple(pairs), isolated=tuple(isolated), other=other)


def call_spans(det):
    """A detector result's calls as ``(start, end)`` arrays, by the scorer's own reading."""
    for onset_field, width_field in _score._ONSET_FIELDS:
        if hasattr(det, onset_field):
            widths = getattr(det, _score.EXTENT_FIELD, None)
            if widths is None:
                widths = getattr(det, width_field, None)
            return _score._spans(getattr(det, onset_field), widths)
    raise TypeError(f"{type(det).__name__} carries no detection times")


FIELDS = ("n_pairs", "n_split", "n_pair_events_hit", "n_isolated", "n_isolated_hit",
          "n_isolated_double", "n_calls", "n_false_alarms")


def pair_score(gt, det, separation_sec: float, *, tol_sec: float = _score.TOL_SEC,
               isolation_sec: float = ISOLATION_SEC) -> dict[str, int]:
    """Count split pairs and double-called isolated events for one detector on one recording.

    An event under the recording's floor is "don't care" (ADR-0009 decision 2), so a pair is
    counted only when both of its events are at or above the floor, and an isolated event only
    when it is.
    """
    c = _score.score_stream(gt, det, tol_sec=tol_sec)
    st = structure(gt, separation_sec, isolation_sec=isolation_sec)
    care = np.ones(len(gt.events), dtype=bool) if c.care is None else np.asarray(c.care, bool)
    hits = np.asarray(c.hits, dtype=bool)
    lo, hi = call_spans(det)
    times = np.asarray([e.time for e in gt.events], dtype=float)

    pairs = [(i, j) for i, j in st.pairs if care[i] and care[j]]
    isolated = [i for i in st.isolated if care[i]]
    double = 0
    for i in isolated:
        near = _score._gap(times[i], lo, hi) <= tol_sec if lo.size else np.zeros(0, bool)
        double += int(np.sum(near) >= 2)
    return dict(
        n_pairs=len(pairs),
        n_split=int(sum(hits[i] and hits[j] for i, j in pairs)),
        n_pair_events_hit=int(sum(int(hits[i]) + int(hits[j]) for i, j in pairs)),
        n_isolated=len(isolated),
        n_isolated_hit=int(sum(hits[i] for i in isolated)),
        n_isolated_double=int(double),
        n_calls=int(lo.size),
        n_false_alarms=int(len(c.fa_times) - len(c.dup_times)))


def rates(counts: dict[str, int]) -> dict[str, float]:
    """Pooled counts as rates. A rate with nothing under it is NaN, not zero."""
    def div(a, b):
        return float(a) / float(b) if b else float("nan")

    return dict(
        split_rate=div(counts["n_split"], counts["n_pairs"]),
        pair_event_recall=div(counts["n_pair_events_hit"], 2 * counts["n_pairs"]),
        isolated_recall=div(counts["n_isolated_hit"], counts["n_isolated"]),
        isolated_double_rate=div(counts["n_isolated_double"], counts["n_isolated"]))
