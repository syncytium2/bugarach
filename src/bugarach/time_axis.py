"""Minutes-friendly time axes for figures drawn without bokeh.

A pure-Python port of the axis ``_time_axis_hook`` (``src/bugarach/ui/app.py``)
gives the viewer, so a static SVG figure reads the same as the live one:

* **ticks** — bokeh's ``AdaptiveTicker(base=60, mantissas=[1, 2, 5, 10, 15, 30],
  min_interval=1)`` at its default six desired ticks: 1/2/5/10/15/30 × 60^k s;
* **labels** — the hook's formatter: ``45s``, ``2m``, ``2m30s``.

CLAUDE.md makes this axis the rule for every time axis in the repo. The report
figures of the surrogate screen are inline SVG with no bokeh behind them, which is
why the rule is ported rather than reused. ``tests/test_time_axis.py`` runs the
ORIGINAL — BokehJS's ticker and the hook's JavaScript formatter, in chromium —
against this port, so a port that drifts from the viewer goes red.

Faithful to the JavaScript, quirks included: ``Math.round`` rounds halves up (so a
tick at 150.5 s reads ``2m31s``), numbers print in JavaScript's shortest form
(``2s``, not ``2.0s``), and a remainder that rounds to 60 prints ``1m60s`` exactly
as the viewer would. On the ticks the ticker actually emits — whole seconds, since
``min_interval`` is 1 — none of those quirks can show.
"""

from __future__ import annotations

import math

__all__ = ["BASE", "MANTISSAS", "MIN_INTERVAL", "DESIRED_N_TICKS",
           "tick_interval", "ticks", "label"]

BASE = 60
MANTISSAS = (1, 2, 5, 10, 15, 30)
MIN_INTERVAL = 1.0
DESIRED_N_TICKS = 6     # bokeh's ContinuousTicker default; the hook does not set it


def tick_interval(lo: float, hi: float, desired_n_ticks: int = DESIRED_N_TICKS) -> float:
    """The spacing AdaptiveTicker picks for the span ``lo``..``hi``, in seconds."""
    span = hi - lo
    if not (math.isfinite(span) and span > 0):
        raise ValueError(f"need lo < hi, got {lo!r}..{hi!r}")
    ideal = span / desired_n_ticks
    # bokeh: base_factor is min_interval unless that is 0, and the exponent is taken
    # of ideal/base_factor in the ticker's own base.
    base_factor = MIN_INTERVAL if MIN_INTERVAL else 1.0
    exponent = math.floor(math.log(ideal / base_factor) / math.log(BASE))
    magnitude = BASE ** exponent * base_factor
    # The mantissas extended one step down and one step up, as bokeh does, so a span
    # that falls between decades can still land on its nearest tick count.
    candidates = (MANTISSAS[-1] / BASE,) + MANTISSAS + (MANTISSAS[0] * BASE,)
    errors = [abs(desired_n_ticks - span / (m * magnitude)) for m in candidates]
    best = candidates[errors.index(min(errors))]   # the FIRST minimum, as argmin
    return max(best * magnitude, MIN_INTERVAL)     # max_interval is unbounded


def ticks(lo: float, hi: float, desired_n_ticks: int = DESIRED_N_TICKS) -> list[float]:
    """Major tick positions inside ``lo``..``hi`` (inclusive), in seconds."""
    step = tick_interval(lo, hi, desired_n_ticks)
    first, last = math.floor(lo / step), math.ceil(hi / step)
    return [k * step for k in range(first, last + 1) if lo <= k * step <= hi]


def _js_number(x: float) -> str:
    """How JavaScript prints a number with ``+ ''``: integers bare, else shortest."""
    if float(x).is_integer():
        return str(int(x))
    return repr(float(x))


def _js_round(x: float) -> int:
    """``Math.round``: halves go toward +infinity (Python's round() goes to even)."""
    return math.floor(x + 0.5)


def label(seconds: float) -> str:
    """The viewer's tick label for a time in seconds: ``45s``, ``2m``, ``2m30s``."""
    sign = "-" if seconds < 0 else ""
    a = abs(seconds)
    if a < 60:
        return f"{sign}{_js_number(a)}s"
    m = math.floor(a / 60)
    r = _js_round(a - m * 60)
    return f"{sign}{m}m{r:02d}s" if r else f"{sign}{m}m"
