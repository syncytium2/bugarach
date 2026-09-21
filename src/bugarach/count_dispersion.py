"""How unevenly one ROI's events spread in time — binned counts and their Fano factor.

Moved out of ``tools/fit_background_shape.py`` (2026-09-11) so the surrogate
screen's rate-profile statistic and the background fitter compute the same
quantity from one definition rather than two. The tool imports these names back,
so its behaviour and its module attributes are unchanged.

The Fano factor is a **diagnostic, never a target**: the fitter maximises a
likelihood and prints this beside it; the surrogate screen compares it between a
recording and its surrogates. Nothing optimises against it.
"""

from __future__ import annotations

import numpy as np

MIN_EVENTS_PER_ROI = 10
"""Below this a within-ROI temporal fit has nothing to say."""


def burst_rows(windows_t, bin_sec, *, min_events: int | None = None):
    """Per-ROI binned-count vectors, for ROIs carrying enough events.

    ``windows_t`` is a sequence of ``(trains, dur)``: per-ROI event times re-zeroed
    to the window, and the window's duration, in the same unit as ``bin_sec``.
    ``min_events`` defaults to :data:`MIN_EVENTS_PER_ROI`, read at call time so a
    caller that patches the constant still gets its own threshold.
    """
    need = MIN_EVENTS_PER_ROI if min_events is None else int(min_events)
    rows = []
    for trains, dur in windows_t:
        edges = np.arange(0.0, dur + bin_sec, bin_sec)
        for v in trains:
            if v.size >= need:
                rows.append(np.histogram(v, bins=edges)[0].astype(float))
    return rows


def fano(rows) -> float:
    """Mean variance/mean of per-bin counts — the diagnostic, never a target."""
    vals = [c.var() / c.mean() for c in rows if c.mean() > 0]
    return float(np.mean(vals)) if vals else float("nan")
