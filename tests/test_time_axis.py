"""`bugarach.time_axis` against the ORIGINAL it ports, not against a transcription.

The viewer's time axis is bokeh's AdaptiveTicker plus a JavaScript formatter, both
set in ``_time_axis_hook`` (``src/bugarach/ui/app.py``). The port exists so static
SVG figures read like the viewer, so the only test worth having runs the originals:
BokehJS's ticker from the installed bokeh, and the formatter's code read out of
``app.py`` itself — so editing the hook without the port turns this red.

Needs chromium (playwright) and bokeh (the ``ui`` extra); skips without them unless
``BUGARACH_REQUIRE_BROWSER=1``, as the repo's other browser tests do.
"""

from __future__ import annotations

import os
import re
from pathlib import Path

import numpy as np
import pytest

from bugarach import time_axis as ta

APP = Path(__file__).resolve().parents[1] / "src" / "bugarach" / "ui" / "app.py"


# ---- the port on its own ---------------------------------------------------

@pytest.mark.parametrize("s, want", [
    (0, "0s"), (45, "45s"), (59, "59s"), (60, "1m"), (120, "2m"), (150, "2m30s"),
    (125, "2m05s"), (3600, "60m"), (-90, "-1m30s"), (2.0, "2s"), (0.5, "0.5s"),
])
def test_labels_read_like_the_viewer(s, want):
    assert ta.label(s) == want


def test_the_ticker_lands_on_sixty_base_steps():
    assert ta.ticks(0, 900) == [0, 120, 240, 360, 480, 600, 720, 840]
    assert ta.tick_interval(0, 30) == 5
    # Two hours: 900 s and 1800 s steps are equally far from six ticks (8 and 4), and
    # bokeh takes the FIRST minimum — 15 min, not the 20 min a person would guess.
    assert ta.tick_interval(0, 7200) == 900


def test_an_empty_span_is_refused():
    with pytest.raises(ValueError):
        ta.ticks(5, 5)


# ---- the port against the originals, in chromium -------------------------

def _hook_formatter_code() -> str:
    src = APP.read_text(encoding="utf-8")
    m = re.search(r'CustomJSTickFormatter\(code="""(.*?)"""\)', src, re.S)
    assert m, "the hook's formatter moved; this test must follow it"
    return m.group(1)


@pytest.fixture(scope="module")
def page():
    required = os.environ.get("BUGARACH_REQUIRE_BROWSER") == "1"
    try:
        import bokeh
        from playwright.sync_api import sync_playwright
    except ImportError as e:
        if required:
            pytest.fail(f"BUGARACH_REQUIRE_BROWSER=1 but {e}")
        pytest.skip(f"needs playwright and bokeh ({e})")
    js = Path(bokeh.__file__).parent / "server" / "static" / "js" / "bokeh.min.js"
    with sync_playwright() as p:
        try:
            browser = p.chromium.launch()
        except Exception as e:                              # noqa: BLE001
            if required:
                raise
            pytest.skip(f"chromium will not launch ({e})")
        pg = browser.new_page()
        pg.set_content('<meta charset="utf-8"><body></body>')
        pg.add_script_tag(path=str(js))
        yield pg
        browser.close()


def _spans():
    fixed = [(0, 5), (0, 30), (0, 59), (0, 60), (0, 90), (0, 300), (0, 900),
             (0, 1799), (0, 3600), (0, 7200), (12.3, 987.6), (-100, 100),
             (0, 86400), (3, 4), (0, 1200.5), (600, 660)]
    rng = np.random.RandomState(20260911)
    lo = rng.uniform(-500, 5000, 200)
    width = 10 ** rng.uniform(0, 4.7, 200)
    return fixed + [(float(a), float(a + w)) for a, w in zip(lo, width)]


def test_ticks_match_bokehjs(page):
    spans = _spans()
    theirs = page.evaluate("""(spans) => {
        const T = Bokeh.Models.get('AdaptiveTicker');
        const t = new T({base: 60, mantissas: [1, 2, 5, 10, 15, 30], min_interval: 1});
        return spans.map(([lo, hi]) => t.get_ticks(lo, hi, null, null).major);
    }""", spans)
    for (lo, hi), want in zip(spans, theirs):
        got = ta.ticks(lo, hi)
        assert np.allclose(got, want), f"{lo}..{hi}: port {got} vs bokehjs {want}"


def test_labels_match_the_hooks_own_formatter(page):
    values = [float(v) for v in range(-200, 4000, 7)] + \
             [0.5, 2.25, 59.6, 119.5, 150.5, -150.5, 3599.4, 3599.6]
    theirs = page.evaluate("""([code, values]) => {
        const f = new Function('tick', code);
        return values.map((v) => f(v));
    }""", [_hook_formatter_code(), values])
    for v, want in zip(values, theirs):
        assert ta.label(v) == want, f"{v}: port {ta.label(v)!r} vs hook {want!r}"
