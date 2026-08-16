"""The troubleshooting view builds, and carries the parts that make it useful.

These are structural checks, not pixel comparisons — the point is that the lanes,
the ground-truth markers and the isolated/member split are actually present, and
that the thing survives the awkward inputs a real run produces (no detections, a
detector that fires everywhere, zero-width events).
"""

import numpy as np
import pytest

hv = pytest.importorskip("holoviews")

from bugarach.detectors.rate import recording_extent  # noqa: E402
from bugarach.simulate import simulate_coordination  # noqa: E402
from bugarach.ui.diagnostic import (  # noqa: E402
    _is_member, _spans, coordination_diagnostic, lane_panel, legend_html,
    raster_panel, score_table,
)


@pytest.fixture(scope="module")
def sim():
    s, gt = simulate_coordination(seed=3, duration_sec=900, n_per_level=(3, 3, 3),
                                  hot_window=(400.0, 600.0), hot_rate_hz=0.25)
    return s, gt, recording_extent(s)


def test_spans_clip_to_the_extent():
    sp = _spans([10.0, 95.0], [5.0, 20.0], (0.0, 100.0))
    assert sp[0] == (10.0, 15.0)
    assert sp[1][1] == 100.0, "must not draw past the recording"


def test_zero_width_events_still_draw():
    """A zero-width detection that vanished would read as 'found nothing here'."""
    sp = _spans([50.0], [0.0], (0.0, 100.0))
    assert len(sp) == 1 and sp[0][1] > sp[0][0]


def test_non_finite_width_still_draws():
    sp = _spans([50.0], [np.nan], (0.0, 100.0))
    assert len(sp) == 1 and sp[0][1] > sp[0][0]


def test_membership():
    t = np.array([1.0, 5.0, 50.0])
    m = _is_member(t, [(0.0, 6.0)])
    assert list(m) == [True, True, False]


def test_membership_with_no_windows_is_all_isolated():
    assert not _is_member(np.array([1.0, 2.0]), []).any()


def test_builds_with_lanes_and_ground_truth(sim):
    s, gt, ext = sim
    lanes = {"coact": (gt.times, np.full(gt.times.size, 1.0))}
    fig = coordination_diagnostic(s.streams["events"], ext=ext, lanes=lanes, gt=gt)
    assert isinstance(fig, hv.Layout)
    assert len(fig) == 2, "lanes panel over raster panel"


def test_builds_without_any_detections(sim):
    """The first thing you look at is often a detector that found nothing."""
    s, gt, ext = sim
    fig = coordination_diagnostic(s.streams["events"], ext=ext,
                                  lanes={"coact": (np.zeros(0), np.zeros(0))}, gt=gt)
    assert isinstance(fig, hv.Layout)


def test_builds_with_no_lanes_and_no_truth(sim):
    s, _, ext = sim
    assert isinstance(coordination_diagnostic(s.streams["events"], ext=ext), hv.Layout)


def test_panels_do_not_share_a_y_dimension(sim):
    """The y dimension NAME is what links y-ranges across panels. When both used
    "y", the lane panel inherited the raster's 0-30 ROI range and collapsed into
    a sliver at the bottom — visible only by rendering it. Pin the names."""
    s, gt, ext = sim
    lanes = {"coact": (gt.times, None)}
    top = lane_panel(lanes, ext=ext, gt=gt)
    bottom = raster_panel(s.streams["events"], ext=ext, gt=gt)

    def ydims(overlay):
        return {d.name for el in overlay for d in el.vdims}

    assert not (ydims(top) & ydims(bottom)), (
        "lane and raster panels must not share a y dimension name, or their "
        "y-ranges link and the lanes collapse")


def test_only_one_x_axis_is_drawn(sim):
    """CLAUDE.md: one x-axis per linked group, bottom row only."""
    s, gt, ext = sim
    top = lane_panel({"coact": (gt.times, None)}, ext=ext, gt=gt)
    assert top.opts.get("plot").kwargs.get("xaxis") is None


def test_legend_explains_every_marker(sim):
    """A figure whose markers need explaining, that does not carry the
    explanation, is not finished — this is what shipped the first time."""
    _, gt, _ = sim
    html = legend_html({"coact": (gt.times, None)}, gt)
    for phrase in ("false alarm", "planted", "no planted events", "onset"):
        assert phrase in html


def test_hot_window_is_drawn_when_present(sim):
    """The probe band has to be visible, or a reader cannot tell that a cluster
    of false alarms sits inside a block with no planted events."""
    s, gt, ext = sim

    def n_bands(layout):
        return sum(isinstance(el, hv.VSpan) for panel in layout for el in panel)

    with_gt = coordination_diagnostic(s.streams["events"], ext=ext,
                                      lanes={"coact": (gt.times, None)}, gt=gt)
    without = coordination_diagnostic(s.streams["events"], ext=ext,
                                      lanes={"coact": (gt.times, None)})
    assert n_bands(with_gt) == 2, "the probe band belongs on both panels"
    assert n_bands(without) == 0


def test_score_table_covers_every_lane(sim):
    _, gt, _ = sim
    lanes = {"coact": (gt.times, None), "sce": (np.zeros(0), None)}
    txt = score_table(gt, lanes)
    assert "recall" in txt
    assert len(txt.splitlines()) == 4, "header, rule, and one row per detector"


def test_score_table_reports_a_perfect_and_an_empty_detector(sim):
    _, gt, _ = sim
    txt = score_table(gt, {"coact": (gt.times, None), "sce": (np.zeros(0), None)})
    assert " 1.00" in txt, "a detector handed the truth should score 1.00"
    assert "nan" in txt.lower() or " 0.00" in txt, "an empty detector must show as such"


def test_every_zoom_is_constrained_to_the_time_axis(sim):
    """Zooming y is meaningless here and desynchronises rows meant to be read
    against each other — the y axis is an ROI index or a detector name.

    Pinned against the render, not the source, because the source was already
    right and the render was not: every panel declares ``xwheel_zoom``/``xpan``
    and HoloViews still put its own toolbar back when they were merged into a
    layout. The shipped figure carried eight unconstrained ``BoxZoomTool``s with
    no ``dimensions`` set at all.
    """
    from bokeh.models import BoxZoomTool, WheelZoomTool

    s, gt, ext = sim
    fig = coordination_diagnostic(s.streams["events"], ext=ext, gt=gt)
    doc = hv.renderer("bokeh").get_plot(fig).state

    from bokeh.models import PanTool

    movers = (list(doc.select({"type": BoxZoomTool}))
              + list(doc.select({"type": WheelZoomTool}))
              + list(doc.select({"type": PanTool})))
    assert movers, "no zoom or pan tools found — the check would pass vacuously"
    offenders = [type(z).__name__ for z in movers if z.dimensions != "width"]
    assert not offenders, f"not constrained to x: {sorted(set(offenders))}"


def test_the_wheel_actually_zooms(sim):
    """Constraining the wheel is not the same as connecting it.

    bokeh leaves ``active_scroll`` on "auto" and nothing claims the wheel, so the
    first version of this fix produced x-constrained tools that did nothing when
    you scrolled — zooming meant finding the box-zoom button first. The tool has
    to be x-only AND be the active scroll tool.
    """
    from bokeh.models import WheelZoomTool
    from bokeh.plotting import figure as _figure

    s, gt, ext = sim
    fig = coordination_diagnostic(s.streams["events"], ext=ext, gt=gt)
    doc = hv.renderer("bokeh").get_plot(fig).state

    panels = list(doc.select({"type": _figure}))
    assert panels, "no panels found — the check would pass vacuously"
    for p in panels:
        scroll = p.toolbar.active_scroll
        assert isinstance(scroll, WheelZoomTool), (
            f"active_scroll is {scroll!r} — the wheel does nothing")
        assert scroll.dimensions == "width"
