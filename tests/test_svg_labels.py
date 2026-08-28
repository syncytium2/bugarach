"""Hand-written SVG labels stay inside the viewBox and clear their neighbours.

**Why this exists.** `docs/learned/architecture.svg` and `pipeline.svg` are hand-drawn:
no generator lays them out, so nothing catches a label that outgrows the space it was
written into. That row of annotations has now broken twice.

The first time, a routed arrow was drawn across it and struck out two labels — recorded
in the file's own comment. The second time, on 2026-08-28, two labels were *lengthened*
to qualify claims the page had corrected (`one cell, one vote — exact` gained
`in amplitude`; `the six's own contract` became `same output the six emit`). Both grew
past the 150-unit box pitch. They overlapped their neighbours by 21 and 13 units, and
one ran 4 units past the viewBox and rendered as `same output the six emi`.

Nobody noticed for a commit, because the SVG still parsed, the page still built, every
test still passed, and the damage is only visible if you look at the picture. The
project's rule is that a visual finding gets rendered rather than described; this is
the same rule applied to a visual *defect*.

**What it measures, and what it cannot.** Chromium's `getBBox()` on the real rendered
text, in SVG user units, driven through Playwright — so it sees the actual font, not an
estimate. It checks two things a reader would notice immediately and a diff would not:

* every `<text>` sits inside its viewBox;
* no two labels **on the same baseline** overlap horizontally.

It does not check that a label is *correct*, near the thing it describes, or legible at
a given screen width. Those are review questions. This is the mechanical half.

Skips rather than fails when chromium is absent, matching the rest of the browser tests
here; CI installs it and `tests/test_browser_available.py` fails loudly if that stops
being true.
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent
SVGS = sorted((ROOT / "docs" / "learned").glob("*.svg"))

#: Labels are allowed to touch by this much before it counts as a collision. Antialiased
#: glyph boxes are a shade wider than the ink, so a hairline of overlap is invisible.
SLACK = 1.0

MEASURE = r"""
(svgText) => {
  const host = document.createElement('div');
  host.style.cssText = 'position:absolute;left:-9999px;width:1200px';
  host.innerHTML = svgText;
  document.body.appendChild(host);
  const svg = host.querySelector('svg');
  const vb = svg.viewBox.baseVal;
  const out = [];
  svg.querySelectorAll('text').forEach(t => {
    const b = t.getBBox();
    out.push({
      text: (t.textContent || '').trim().slice(0, 60),
      x: b.x, y: b.y, w: b.width, h: b.height,
    });
  });
  return {vb: {x: vb.x, y: vb.y, w: vb.width, h: vb.height}, texts: out};
}
"""


def _measure(svg_path: Path):
    pw = pytest.importorskip("playwright.sync_api",
                             reason="playwright not installed")
    from playwright.sync_api import Error as PWError
    try:
        with pw.sync_playwright() as p:
            browser = p.chromium.launch()
            page = browser.new_page()
            # A stylesheet, because the labels inherit their size from the report's
            # sheet and measuring them at a browser default would measure a different
            # figure from the one that ships.
            page.set_content(
                "<style>"
                "text { font: 12px system-ui, sans-serif; }"
                "text.lbl { font-size: 12.5px; }"
                "</style>")
            got = page.evaluate(MEASURE, svg_path.read_text(encoding="utf-8"))
            browser.close()
            return got
    except PWError as exc:                                   # pragma: no cover
        pytest.skip(f"chromium unavailable: {exc}")


@pytest.mark.parametrize("svg", SVGS, ids=lambda p: p.name)
def test_no_label_escapes_its_viewbox(svg):
    """A label wider than its canvas is clipped, and clipping reads as a typo.

    `same output the six emit` rendered as `same output the six emi` for one commit —
    a sentence that looks written rather than broken, which is the worst kind of
    breakage to ship.
    """
    got = _measure(svg)
    vb = got["vb"]
    escaped = [
        (t["text"], round(t["x"], 1), round(t["x"] + t["w"], 1))
        for t in got["texts"]
        if t["x"] < vb["x"] - SLACK
        or t["x"] + t["w"] > vb["x"] + vb["w"] + SLACK
        or t["y"] < vb["y"] - SLACK
        or t["y"] + t["h"] > vb["y"] + vb["h"] + SLACK
    ]
    assert not escaped, (
        f"{svg.name}: {len(escaped)} label(s) outside the viewBox "
        f"(0-{vb['w']:.0f} x 0-{vb['h']:.0f}). Shorten the text, split it across two "
        f"baselines, or widen the viewBox:\n" +
        "\n".join(f"  {x:7.1f}-{x2:7.1f}  {t!r}" for t, x, x2 in escaped))


@pytest.mark.parametrize("svg", SVGS, ids=lambda p: p.name)
def test_labels_on_one_baseline_do_not_overlap(svg):
    """Two labels sharing a baseline and a span run together into one string.

    Grouped by rounded `y` because that is what "the same row" means to a reader; a
    label deliberately moved to its own baseline is not compared against the row it
    left, which is the fix this test is meant to make discoverable rather than forbid.
    """
    got = _measure(svg)
    rows: dict[int, list] = {}
    for t in got["texts"]:
        rows.setdefault(round(t["y"]), []).append(t)

    clashes = []
    for y, items in sorted(rows.items()):
        items.sort(key=lambda t: t["x"])
        for a, b in zip(items, items[1:]):
            gap = b["x"] - (a["x"] + a["w"])
            if gap < -SLACK:
                clashes.append((y, a["text"], b["text"], round(gap, 1)))

    assert not clashes, (
        f"{svg.name}: {len(clashes)} overlapping label pair(s) on a shared baseline. "
        f"They render as one run-together string:\n" +
        "\n".join(f"  y={y}: {a!r} overlaps {b!r} by {-g:.1f} units"
                  for y, a, b, g in clashes))


def test_the_guard_can_fail():
    """Prove the check fires, so a green run means something.

    Both assertions above pass on a tree where the figures are fine, which is exactly
    when a broken check is invisible. This builds a deliberately damaged SVG — one
    label off the right edge, two overlapping on one baseline — and asserts the
    measurements catch both.
    """
    import tempfile
    bad = ('<svg viewBox="0 0 200 100" xmlns="http://www.w3.org/2000/svg">'
           '<text x="10" y="50" class="lbl">a label long enough to overlap</text>'
           '<text x="60" y="50" class="lbl">its neighbour here</text>'
           '<text x="150" y="80" class="lbl">and this one runs off the edge</text>'
           '</svg>')
    with tempfile.TemporaryDirectory() as tmp:
        p = Path(tmp) / "broken.svg"
        p.write_text(bad)
        got = _measure(p)
        vb = got["vb"]
        escaped = [t for t in got["texts"]
                   if t["x"] + t["w"] > vb["x"] + vb["w"] + SLACK]
        rows: dict[int, list] = {}
        for t in got["texts"]:
            rows.setdefault(round(t["y"]), []).append(t)
        overlaps = 0
        for items in rows.values():
            items.sort(key=lambda t: t["x"])
            for a, b in zip(items, items[1:]):
                if b["x"] - (a["x"] + a["w"]) < -SLACK:
                    overlaps += 1
    assert escaped, "the viewBox check did not catch a label off the edge"
    assert overlaps, "the overlap check did not catch two labels on one baseline"
