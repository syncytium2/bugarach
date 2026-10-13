"""The group raster pages navigate the way Igor Pro does (ADR-0015).

Three layers, cheapest first: the tools each panel is built with, read off the bokeh
model; the script appended to the saved page; and the gestures themselves, driven in a
headless browser on a page built from a synthetic folder.
"""
from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
import pytest

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "tools"))

import make_group_raster_summary as mod  # noqa: E402
from bugarach.ui import navigate  # noqa: E402

N_ROI = {"s1": 24, "s2": 17}


def _folder(tmp_path: Path) -> Path:
    """Two recordings long and busy enough that a box has something to close on."""
    d = tmp_path / "flagged"
    d.mkdir()
    rng = np.random.RandomState(3)
    (d / "slices.csv").write_text(
        "slice_id,frame_interval_sec,date,mouse_id,group_id,n_roi_recorded\n"
        + "".join(f"{s},0.1,2024010{i},{i},MALE,{n}\n"
                  for i, (s, n) in enumerate(N_ROI.items(), 1)))
    (d / "regions.csv").write_text(
        "slice_id,region_idx,label,start_sec,end_sec,analysis_start_sec,analysis_end_sec\n"
        + "".join(f"{s},1,baseline,0,1200,0,1200\n{s},2,TTX,1200,3000,1200,3000\n"
                  for s in N_ROI))
    for s, n in N_ROI.items():
        rows = ["roi,time_sec,stream,width_sec,width_def,peak_sec,amp"]
        for roi in range(1, n + 1):
            for t in np.sort(rng.uniform(0, 3000, rng.randint(5, 60))):
                rows.append(f"{roi},{t:.6f},fast,1.0,halfprom_width_findpeaks_w,"
                            f"{t + 0.5:.6f},1.0")
        (d / f"{s}.csv").write_text("\n".join(rows) + "\n")
    (d / mod.MANIFEST).write_text(
        "slice_id\troi\tstream\ttime_sec\tonset_sec\tfield_step_id\tregion\t"
        "in_analysis_window\n")
    return d


def _figures(tmp_path):
    """Every panel of the page as the bokeh figure the browser is sent, in page order."""
    import holoviews as hv

    pages, manifest, _ = mod.measure(_folder(tmp_path), ("TTX",))
    spec = pages[("MALE", "TTX", "fast")]
    blocks, _ = mod.build_page(spec["members"], ext=spec["ext"], manifest=manifest,
                               width=600, stream="fast")
    return [hv.renderer("bokeh").get_plot(p).state for _, panels in blocks for p in panels]


def test_a_plain_drag_is_the_box_and_the_box_zooms_time_only(tmp_path):
    """Tony, 2026-10-13: Igor's assignment, the box has the plain drag. And the same day,
    on the first real pages: "disable the pitch and make zoom only x-axis" (ADR-0016)."""
    from bokeh.models import BoxZoomTool

    figs = _figures(tmp_path)
    assert len(figs) == 4                    # period lane and raster, twice
    for fig in figs:
        boxes = [t for t in fig.toolbar.tools if isinstance(t, BoxZoomTool)]
        assert len(boxes) == 1
        assert fig.toolbar.active_drag is boxes[0]
        assert navigate.NAV_TAG in fig.tags
        assert boxes[0].dimensions == "width"


def test_the_wheel_zooms_only_with_ctrl_held_and_only_in_time(tmp_path):
    """The bare wheel scrolls the page. A page of stacked rasters that zooms when the
    reader tried to scroll past it is the failure "scroll wins" was written against."""
    from bokeh.models import PanTool, WheelZoomTool

    for fig in _figures(tmp_path):
        wheel = [t for t in fig.toolbar.tools if isinstance(t, WheelZoomTool)]
        assert len(wheel) == 1
        assert wheel[0].modifiers == {"ctrl": True}
        assert wheel[0].dimensions == "width"
        assert fig.toolbar.active_scroll is wheel[0]
        # Shift hands the drag to this one, so it has to be there and slide time only
        pans = [t for t in fig.toolbar.tools if isinstance(t, PanTool)]
        assert pans and all(t.dimensions == "width" for t in pans)


def test_the_script_goes_inside_the_body_and_a_page_without_one_is_refused():
    out = navigate.add_navigation("<body><p>x</p></body>")
    assert out.index("bugarachNavBar") < out.index("</body>")
    assert out.count("window.bugarachNav =") == 1
    assert "__" not in out.split("<script>")[1].split("</script>")[0]
    with pytest.raises(ValueError):
        navigate.add_navigation("<p>no body</p>")


# --- the gestures, in a browser -------------------------------------------------------

@pytest.fixture(scope="module")
def page(tmp_path_factory):
    pw = pytest.importorskip("playwright.sync_api", reason="playwright is not installed")
    tmp = tmp_path_factory.mktemp("nav")
    out = tmp / "pages"
    assert mod.main(["--folder", str(_folder(tmp)), "--out", str(out),
                     "--treatments", "TTX", "--streams", "fast", "--signal", "roi",
                     "--win", "win20min", "--source", "none"]) == 0
    html = next(out.glob("*.html"))
    with pw.sync_playwright() as p:
        try:
            browser = p.chromium.launch()
        except Exception as e:                              # noqa: BLE001
            pytest.skip(f"no chromium available: {type(e).__name__}")
        try:
            pg = browser.new_page(viewport={"width": 1700, "height": 500})
            pg.goto(html.as_uri())
            pg.wait_for_function("window.bugarachNav !== undefined", timeout=30_000)
            yield pg
        finally:
            browser.close()


def _view(page):
    return page.evaluate("({...bugarachNav.view(), y: bugarachNav.rows(),"
                         " heights: bugarachNav.heights(),"
                         " depth: bugarachNav.depth(), scrollY: window.scrollY})")


def _flat(rows):
    return [v for row in rows for v in row]


def _settled(page, before):
    """Wait for the view to differ from ``before`` and for the script to have recorded it."""
    page.wait_for_function(
        "b => { const v = bugarachNav.view();"
        " return JSON.stringify(v.x) !== JSON.stringify(b.x)"
        " && bugarachNav.depth() !== b.depth; }", arg=before, timeout=10_000)
    return _view(page)


def _raster(page):
    """Screen box of the first recording's raster: the second plot canvas on the page."""
    boxes = page.evaluate("""() => {
        const out = [];
        const walk = root => { for (const el of root.querySelectorAll('*')) {
            if (el.shadowRoot) walk(el.shadowRoot);
            if (el.classList && el.classList.contains('bk-Canvas')) {
                const r = el.getBoundingClientRect();
                out.push([r.x, r.y + window.scrollY, r.width, r.height]); } } };
        walk(document); return out; }""")
    return boxes[1]


def _drag(page, x0, y0, x1, y1, *, shift=False):
    if shift:
        page.keyboard.down("Shift")
    page.mouse.move(x0, y0)
    page.mouse.down()
    page.mouse.move((x0 + x1) / 2, (y0 + y1) / 2, steps=4)
    page.mouse.move(x1, y1, steps=4)
    page.mouse.up()
    if shift:
        page.keyboard.up("Shift")


def test_the_gestures_in_a_browser(page):
    """One walk through the page, in the order a reader would make it. One test because
    each step starts from the view the last one left."""
    page.evaluate("window.scrollTo(0, 0)")
    x, y, w, h = _raster(page)
    home = _view(page)
    assert home["x"] == [-1200, 1800] and home["depth"] == 1

    # A box dragged across: time closes on it.
    _drag(page, x + 0.4 * w, y + 20, x + 0.6 * w, y + 23)
    across = _settled(page, home)
    assert home["x"][0] < across["x"][0] < across["x"][1] < home["x"][1]
    assert across["x"][1] - across["x"][0] == pytest.approx(0.2 * 3000, rel=0.1)
    # approx: bokeh writes a range back through its screen mapping
    assert _flat(across["y"]) == pytest.approx(_flat(home["y"]))
    assert across["heights"] == home["heights"]

    # A box dragged corner to corner still zooms time only: every row stays on screen
    # and no panel changes height (ADR-0016).
    _drag(page, x + 0.3 * w, y + 0.2 * h, x + 0.7 * w, y + 0.7 * h)
    down = _settled(page, across)
    assert down["x"][1] - down["x"][0] == pytest.approx(0.4 * (across["x"][1] - across["x"][0]),
                                                        rel=0.1)
    assert _flat(down["y"]) == pytest.approx(_flat(home["y"]))
    assert down["heights"] == home["heights"]

    # Shift-drag slides: the same span of time, moved.
    x, y, w, h = _raster(page)
    _drag(page, x + 0.5 * w, y + 10, x + 0.3 * w, y + 10, shift=True)
    slid = _settled(page, down)
    assert slid["x"][0] > down["x"][0]
    assert slid["x"][1] - slid["x"][0] == pytest.approx(down["x"][1] - down["x"][0])

    # The bare wheel leaves the view alone; with Ctrl it zooms time.
    page.mouse.move(x + 0.5 * w, y + 10)
    page.mouse.wheel(0, -240)
    page.wait_for_timeout(400)
    assert _view(page)["x"] == slid["x"]
    page.evaluate("window.scrollTo(0, 0)")
    page.keyboard.down("Control")
    page.mouse.wheel(0, -240)
    page.keyboard.up("Control")
    wheeled = _settled(page, _view(page) | {"x": slid["x"], "depth": slid["depth"]})
    assert wheeled["x"][1] - wheeled["x"][0] < slid["x"][1] - slid["x"][0]

    # Ctrl+Z steps back one view at a time.
    page.keyboard.press("Control+z")
    back = _view(page)
    assert back["x"] == slid["x"] and back["depth"] == wheeled["depth"] - 1

    # Double-click shows everything.
    page.mouse.dblclick(x + 0.5 * w, y + 10)
    page.wait_for_function("bugarachNav.view().x[0] === -1200", timeout=10_000)
    again = _view(page)
    assert again["x"] == home["x"]
    assert _flat(again["y"]) == pytest.approx(_flat(home["y"]))
    assert again["heights"] == home["heights"]
