"""Clean-room implementation of rate+context, written from rate_steps_for_cleanroom.md ONLY."""
import math

import numpy as np

_EPS = np.finfo(float).eps


def _grid(t_lo, t_hi, dt):
    """Step 2: MATLAB-style t_lo:dt:t_hi as described on the page."""
    n = int(math.floor((t_hi - t_lo) / dt * (1.0 + 4.0 * _EPS))) + 1
    if n <= 0:
        return np.zeros(0)
    forward_end = t_lo + (n - 1) * dt
    tol = 4.0 * np.spacing(max(abs(t_lo), abs(t_hi)))
    end = t_hi if abs(forward_end - t_hi) <= tol else forward_end
    g = np.empty(n)
    m = n // 2  # first half: k = 0..m-1 forward; the rest backward from `end`
    for k in range(n):
        if k < m:
            g[k] = t_lo + k * dt
        else:
            g[k] = end - (n - 1 - k) * dt
    return g


def _slot_counts(events, grid, dt):
    """Step 3: slots [g_k - dt/2, g_k + dt/2), last slot closed on both ends.
    Adjacent slots share one edge (edge k = g_k - dt/2, final edge = g_last + dt/2)."""
    n = grid.size
    edges = np.empty(n + 1)
    edges[:n] = grid - dt / 2.0
    edges[n] = grid[-1] + dt / 2.0
    idx = np.searchsorted(edges, events, side="right") - 1
    idx[events == edges[n]] = n - 1  # last slot includes its end
    ok = (idx >= 0) & (idx < n)
    return np.bincount(idx[ok], minlength=n).astype(float)


def _window_rate(counts, grid, t_lo, t_hi, dt, w):
    """Step 4: sum 2h+1 slots (truncated at grid ends), divide by in-recording window length."""
    n = counts.size
    h = int(math.floor(w / (2.0 * dt) + 0.5))
    csum = np.concatenate(([0.0], np.cumsum(counts)))
    k = np.arange(n)
    lo = np.maximum(0, k - h)
    hi = np.minimum(n - 1, k + h)
    total = csum[hi + 1] - csum[lo]
    divisor = np.minimum(t_hi, grid + w / 2.0) - np.maximum(t_lo, grid - w / 2.0)
    with np.errstate(divide="ignore", invalid="ignore"):
        return total / divisor


def _context_window(context_win, t_lo, t_hi):
    """Step 5: 90% rule."""
    ninety = 0.9 * (t_hi - t_lo)
    return ninety if context_win >= ninety else context_win


def _groups(grid, over, merge_gap):
    """Steps 7-8: returns list of (start_time, end_time) with single-moment groups dropped."""
    idx = np.flatnonzero(over)
    groups = []
    if idx.size == 0:
        return groups
    first = prev = idx[0]
    for j in idx[1:]:
        if grid[j] - grid[prev] > merge_gap:
            groups.append((first, prev))
            first = j
        prev = j
    groups.append((first, prev))
    return [(grid[a], grid[b]) for a, b in groups if a != b]


def rate_context_calls(trains, t_lo, t_hi, *, grid_dt=0.1, rate_win=1.0, context_win=60.0,
                       excess_threshold=4.5, merge_gap=3.0, pad=0.5):
    """trains: list of 1-D sequences of event times in seconds, one per neuron, NOT yet clipped to [t_lo, t_hi].
    t_lo, t_hi: the recording's start and end in seconds (already worked out; you do not derive them).
    Returns (onsets, widths): two 1-D numpy float arrays of equal length, one entry per call, in time order."""
    empty = (np.zeros(0), np.zeros(0))
    # Step 1 (with clipping from "What goes in")
    if len(trains) < 2:
        return empty
    clipped = []
    for tr in trains:
        a = np.asarray(tr, dtype=float).ravel()
        clipped.append(a[(a >= t_lo) & (a <= t_hi)])
    events = np.concatenate(clipped) if clipped else np.zeros(0)
    if events.size == 0:
        return empty
    # Step 2
    grid = _grid(t_lo, t_hi, grid_dt)
    if grid.size == 0:
        return empty
    # Step 3
    counts = _slot_counts(events, grid, grid_dt)
    # Steps 4-5
    count_rate = _window_rate(counts, grid, t_lo, t_hi, grid_dt, rate_win)
    cw = _context_window(context_win, t_lo, t_hi)
    context_rate = _window_rate(counts, grid, t_lo, t_hi, grid_dt, cw)
    # Step 6
    with np.errstate(invalid="ignore"):
        excess = count_rate - context_rate
        over = excess >= excess_threshold
    # Steps 7-8
    groups = _groups(grid, over, merge_gap)
    # Step 9
    onsets = np.array([s - pad for s, _ in groups], dtype=float)
    widths = np.array([(e + pad) - (s - pad) for s, e in groups], dtype=float)
    return onsets, widths


if __name__ == "__main__":
    ap = lambda a, b: abs(a - b) < 1e-9  # noqa: E731

    # Step 1: fewer than 2 neurons / no events in range
    o, w = rate_context_calls([[50.02] * 20], 0.0, 100.0)
    assert o.size == 0 and w.size == 0
    o, w = rate_context_calls([[-5.0, 101.0], [200.0]], 0.0, 100.0)
    assert o.size == 0

    # Step 2: grid
    g = _grid(0.0, 1.0, 0.1)
    assert g.size == 11 and g[-1] == 1.0 and g[0] == 0.0
    # 0.3/0.1 = 2.9999999999999996; the 4-eps factor lifts it to 3 -> 4 moments, last snaps to 0.3
    assert (0.3 / 0.1) < 3.0
    g = _grid(0.0, 0.3, 0.1)
    assert g.size == 4 and g[-1] == 0.3, g
    g = _grid(0.0, 1.02, 0.1)
    assert g.size == 11 and ap(g[-1], 1.0)

    # Step 3: slots
    g = _grid(0.0, 1.0, 0.1)
    c = _slot_counts(np.array([0.0, 0.05, 0.049, 1.0, 1.05]), g, 0.1)
    # 0.0 and 0.049 -> slot 0; 0.05 is edge of slot 1 (0.1-0.05 == 0.05) -> slot 1;
    # 1.0 -> slot 10; 1.05 is the closed end of the last slot -> slot 10
    assert c[0] == 2 and c[1] == 1 and c[10] == 2 and c.sum() == 5, c
    g = _grid(0.0, 1.08, 0.1)  # last moment 1.0, last slot ends 1.05
    c = _slot_counts(np.array([1.02, 1.07]), g, 0.1)
    assert c.sum() == 1 and c[-1] == 1

    # Step 4: h values and divisor
    g = _grid(0.0, 100.0, 0.1)
    counts = np.zeros(g.size); counts[500] = 20  # 50.0
    r = _window_rate(counts, g, 0.0, 100.0, 0.1, 1.0)
    assert ap(r[500], 20.0) and ap(r[495], 20.0) and r[494] == 0 and r[506] == 0
    counts0 = np.zeros(g.size); counts0[0] = 3
    r = _window_rate(counts0, g, 0.0, 100.0, 0.1, 1.0)
    assert ap(r[0], 6.0)  # 3 events / (0.5 - 0) s

    # Step 5: 90% rule
    assert _context_window(60.0, 0.0, 100.0) == 60.0
    assert ap(_context_window(60.0, 0.0, 10.0), 9.0)

    # Steps 6-8 on a hand-made excess
    gg = np.array([0.0, 1.0, 3.0, 4.0, 7.5, 10.0, 11.0])
    over = np.array([4.5, 4.5, 1.0, 5.0, 9.0, 9.0, 0.0]) >= 4.5
    # over at 0,1,4 (3 s after 1 -> same group), 7.5 (3.5 s -> new group), 10 (2.5 -> same)
    assert _groups(gg, over, 3.0) == [(0.0, 4.0), (7.5, 10.0)]
    over = np.array([True, False, False, False, True, False, False])  # two singletons
    assert _groups(gg, over, 3.0) == []

    # End to end: one burst of 20 events at 50.02 on 2 neurons, 100 s recording
    tr = [[50.02] * 10, [50.02] * 10 + [-1.0, 150.0]]
    o, w = rate_context_calls(tr, 0.0, 100.0)
    assert o.size == 1 and ap(o[0], 49.0) and ap(w[0], 2.0), (o, w)

    # two bursts 3.5 s apart -> moments over bar 49.5..50.5 and 53.0..54.0 -> merged
    tr = [[50.02] * 10 + [53.52] * 10, [50.02] * 10 + [53.52] * 10]
    o, w = rate_context_calls(tr, 0.0, 100.0)
    assert o.size == 1 and ap(o[0], 49.0) and ap(w[0], 5.5), (o, w)  # 49.0 .. 54.5
    # bursts 4.1 s apart -> gap between 50.5 and 53.6 is 3.1 s -> two calls
    tr = [[50.02] * 10 + [54.12] * 10, [50.02] * 10 + [54.12] * 10]
    o, w = rate_context_calls(tr, 0.0, 100.0)
    assert o.size == 2 and ap(o[1], 53.1) and ap(w[1], 2.0), (o, w)

    # Single-moment group dropped: rate_win 0.05 -> h = 0, one slot
    o, w = rate_context_calls([[50.02], [50.02]], 0.0, 100.0, rate_win=0.05)
    assert o.size == 0
    # Two adjacent moments -> call width 1.1
    o, w = rate_context_calls([[50.02], [50.12]], 0.0, 100.0, rate_win=0.05)
    assert o.size == 1 and ap(o[0], 49.5) and ap(w[0], 1.1), (o, w)

    # 90% rule changes the outcome: 10 s recording, burst of 20 at 5.02
    tr = [[5.02] * 10, [5.02] * 10]
    o, _ = rate_context_calls(tr, 0.0, 10.0, excess_threshold=17.9)  # context 9 s -> excess <= 17.89
    assert o.size == 0, o
    o, w = rate_context_calls(tr, 0.0, 10.0, excess_threshold=17.7)
    assert o.size == 1 and ap(o[0], 4.0) and ap(w[0], 2.0), (o, w)

    print("all hand checks passed")
