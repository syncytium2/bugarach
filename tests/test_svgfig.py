"""The hand-rolled SVG helpers behind the plain-language detector review."""
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "tools"))

import svgfig  # noqa: E402


def test_time_labels_are_minutes_friendly():
    """CLAUDE.md: 60-base ticks labeled 45s / 2m / 2m30s, never raw seconds."""
    labels = [lab for _, lab in svgfig.time_ticks(0, 600)]
    assert labels == ["0s", "2m", "4m", "6m", "8m", "10m"]
    assert [lab for _, lab in svgfig.time_ticks(1350, 1410, target=3)] == ["22m30s", "23m", "23m30s"]
    assert svgfig.fmt_time(-120, 60) == "−2m"


def test_clip_ids_are_unique_across_figures():
    """Panels freed and reallocated must not reuse a clip id: a repeated id clips a later
    panel to an earlier one's rectangle, and its marks silently vanish (it happened)."""
    ids = []
    for _ in range(3):
        f = svgfig.Figure(200, 200)
        for k in range(5):
            f.panel(0, k * 30, 200, 20, (0, 1), (0, 1)).raster([[0.5]])
        ids += re.findall(r"clipPath id='([^']+)'", f.svg())
    assert len(ids) == 15 and len(set(ids)) == 15


def test_raster_draws_ticks_and_nothing_else():
    """Nothing is ever drawn on a raster: the method emits one path of vertical ticks."""
    f = svgfig.Figure(200, 100)
    p = f.panel(0, 0, 200, 100, (0, 10), (0, 1), frame=False)
    before = len(f.parts)
    p.raster([[1.0, 2.0], [], [5.0]])
    added = "".join(f.parts[before:])
    assert added.count("<path") == 1
    assert re.findall(r"M[\d.]+ [\d.]+V[\d.]+", added) and "<text" not in added and "<rect" not in added.split("</clipPath>")[1]


def test_down_triangle_points_down():
    f = svgfig.Figure(100, 100)
    p = f.panel(0, 0, 100, 100, (0, 1), (0, 1), frame=False)
    p.down_triangle(0.5, 50, color="#000", size=10)
    pts = [tuple(map(float, xy.split(","))) for xy in re.search(r"points='([^']+)'", f.parts[-1]).group(1).split()]
    apex = max(pts, key=lambda q: q[1])
    assert apex[0] == 50.0 and sum(1 for q in pts if q[1] < apex[1]) == 2
