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
* no two labels **whose boxes overlap vertically** also overlap horizontally.

The second check compared only labels on the *same rounded baseline* when it was first
written, and the fix that prompted it — splitting the row onto three interleaved
baselines — walked straight through that hole: boxes 15 units tall on baselines 8 apart
overlap by 7 while sitting in different groups. A reviewer proved it by lengthening a
label until it collided and watching the suite stay green. Comparing boxes closes it,
with a looser vertical threshold so that two deliberately stacked lines of one wrapped
label are not reported as a collision.

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

#: Horizontal grazing allowed before it counts. Glyph boxes are a shade wider than the
#: ink, so a hairline of overlap is invisible.
SLACK = 1.0

#: Vertical overlap allowed, and it has to be looser than the horizontal one. Two
#: deliberately stacked lines of a wrapped label sit a line-height apart, and their
#: boxes graze by about a unit because the box is taller than the visible glyphs —
#: `landscape.svg` has two such pairs and they are correct. A genuine collision between
#: labels meant to be on separate rows is much deeper: the architecture row's baselines
#: are 8 units apart with 15-unit boxes, so a real clash there overlaps by 7.
#: 3 units separates the two cases with room on both sides.
Y_SLACK = 3.0

#: Every box and every path sample is mapped into the viewBox's own units before any
#: comparison. `getBBox()` and `getPointAtLength()` answer in the element's LOCAL space,
#: which ignores every ancestor transform — and every draughtsman figure wraps its
#: drawing in `<g class="ds-body" transform="translate(…)">` while its title and caption
#: sit outside it. Measured locally, a label in the body is compared with the title as if
#: the translate were not there: overlaps are reported across real gaps, and a label can
#: run off the bottom by the whole translate unseen. All four corners are mapped, not
#: just the origin, so a scale or rotation in some later figure still gives the extent.
SVG_SPACE = r"""
  const toSvg = svg.getScreenCTM().inverse();
  const at = (el, x, y) =>
    new DOMPoint(x, y).matrixTransform(toSvg.multiply(el.getScreenCTM()));
  const box = el => {
    const b = el.getBBox();
    const c = [[b.x, b.y], [b.x + b.width, b.y], [b.x, b.y + b.height],
               [b.x + b.width, b.y + b.height]].map(([x, y]) => at(el, x, y));
    const xs = c.map(p => p.x), ys = c.map(p => p.y);
    const x = Math.min(...xs), y = Math.min(...ys);
    return {x, y, w: Math.max(...xs) - x, h: Math.max(...ys) - y};
  };
"""

MEASURE = r"""
(svgText) => {
  const host = document.createElement('div');
  host.style.cssText = 'position:absolute;left:-9999px;width:1200px';
  host.innerHTML = svgText;
  document.body.appendChild(host);
  const svg = host.querySelector('svg');
  const vb = svg.viewBox.baseVal;
  // SVG_SPACE
  const out = [];
  svg.querySelectorAll('text').forEach(t => {
    out.push({text: (t.textContent || '').trim().slice(0, 60), ...box(t)});
  });
  return {vb: {x: vb.x, y: vb.y, w: vb.width, h: vb.height}, texts: out};
}
""".replace("// SVG_SPACE", SVG_SPACE)


MEASURE_PATHS = r"""
(svgText) => {
  const host = document.createElement('div');
  host.style.cssText = 'position:absolute;left:-9999px;width:1200px';
  host.innerHTML = svgText;
  document.body.appendChild(host);
  const svg = host.querySelector('svg');
  // SVG_SPACE
  const texts = [];
  svg.querySelectorAll('text').forEach(t => {
    texts.push({text: (t.textContent || '').trim().slice(0, 60), ...box(t)});
  });
  const paths = [];
  svg.querySelectorAll('path, line, polyline').forEach(el => {
    // Fills are shapes (arrowhead markers, glyphs); only stroked geometry routes.
    const cs = getComputedStyle(el);
    if (cs.stroke === 'none' && !el.hasAttribute('stroke-width')) return;
    let len = 0;
    try { len = el.getTotalLength(); } catch (e) { return; }
    if (!len) return;
    const n = Math.max(8, Math.min(120, Math.round(len / 6)));
    const samples = [];
    for (let i = 0; i <= n; i++) {
      const q = el.getPointAtLength((len * i) / n);
      const p = at(el, q.x, q.y);
      samples.push({x: p.x, y: p.y});
    }
    paths.push({d: el.getAttribute('d') || el.outerHTML.slice(0, 60), samples});
  });
  return {texts, paths};
}
""".replace("// SVG_SPACE", SVG_SPACE)


def _measure_paths(svg_path: Path):
    """Text boxes plus sampled points along every stroked path, in user units."""
    pw = pytest.importorskip("playwright.sync_api",
                             reason="playwright not installed")
    from playwright.sync_api import Error as PWError
    try:
        with pw.sync_playwright() as p:
            browser = p.chromium.launch()
            page = browser.new_page()
            page.set_content(
                "<style>text { font: 12px system-ui, sans-serif; }"
                "text.lbl { font-size: 12.5px; }</style>")
            got = page.evaluate(MEASURE_PATHS,
                                svg_path.read_text(encoding="utf-8"))
            browser.close()
            return got
    except PWError as exc:                                   # pragma: no cover
        pytest.skip(f"chromium unavailable: {exc}")


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
def test_labels_that_share_vertical_space_do_not_overlap(svg):
    """Two labels whose boxes overlap in both axes run together into one string.

    **Compares boxes, not baselines**, and the difference is the whole point. The first
    version of this test grouped by ``round(y)`` — "the same row" as a reader would say
    it — and the very fix it was written to protect defeated it: the annotation row was
    split onto three interleaved baselines at y=42/50/58, where a 15-unit-tall box on
    one baseline overlaps its neighbour on the next by seven units while sitting in a
    different comparison group.

    A later reviewer proved the hole rather than describing it: lengthening one label
    produced a real 8.8-unit collision with its neighbour and the suite stayed green.
    A guard with a hole is worse than no guard, because it is quoted as coverage.
    """
    got = _measure(svg)
    texts = sorted(got["texts"], key=lambda t: (t["x"], t["y"]))

    clashes = []
    for i, a in enumerate(texts):
        for b in texts[i + 1:]:
            dx = min(a["x"] + a["w"], b["x"] + b["w"]) - max(a["x"], b["x"])
            dy = min(a["y"] + a["h"], b["y"] + b["h"]) - max(a["y"], b["y"])
            if dx > SLACK and dy > Y_SLACK:
                clashes.append((a["text"], b["text"], round(dx, 1), round(dy, 1)))

    assert not clashes, (
        f"{svg.name}: {len(clashes)} overlapping label pair(s). They render as one "
        f"run-together string:\n" +
        "\n".join(f"  {a!r} overlaps {b!r} by {dx:.1f} x {dy:.1f} units"
                  for a, b, dx, dy in clashes))


@pytest.mark.parametrize("svg", SVGS, ids=lambda p: p.name)
def test_no_stroked_path_lands_on_a_label(svg):
    """An arrow that ends inside a label reads as attached to it.

    This is the third distinct way this estate's hand-drawn figures have broken, and
    the two `architecture.svg` comments record the first two: a bypass route drawn
    across the annotation row struck out two labels, and its return leg was later found
    running through `1,128 params`. `landscape.svg` had an arrowhead terminating inside
    `benchmarked by Mölter 2018`.

    Text-to-text overlap does not see any of it, so this samples each stroked path and
    asks whether any sample falls inside a text box. Endpoints matter most — an
    arrowhead is what a reader sees as "pointing at" something — so they are checked
    against a tighter margin than the middle of a run.
    """
    got = _measure_paths(svg)
    hits = []
    for path in got["paths"]:
        for i, pt in enumerate(path["samples"]):
            endpoint = i == 0 or i == len(path["samples"]) - 1
            pad = 0.0 if endpoint else -2.0
            for t in got["texts"]:
                if (t["x"] - pad <= pt["x"] <= t["x"] + t["w"] + pad
                        and t["y"] - pad <= pt["y"] <= t["y"] + t["h"] + pad):
                    hits.append((path["d"][:44], t["text"],
                                 round(pt["x"], 1), round(pt["y"], 1), endpoint))
                    break
            else:
                continue
            break

    assert not hits, (
        f"{svg.name}: {len(hits)} stroked path(s) land on a label. An arrow ending in "
        f"text reads as attached to it:\n" +
        "\n".join(f"  {'endpoint' if e else 'mid-run'} ({x}, {y}) inside {t!r}"
                  f"   path {d}…" for d, t, x, y, e in hits))


def test_the_guard_can_fail():
    """Prove the check fires, so a green run means something.

    All three checks above pass on a tree where the figures are fine, which is exactly
    when a broken check is invisible. This builds a deliberately damaged SVG — one
    label off the right edge, two overlapping on one baseline — and asserts the
    measurements catch both.

    **And the same damage hidden behind a transform**, because that is how every
    draughtsman figure is built. Each of the last three cases looks fine measured in
    its element's local units and is only wrong once its group's `translate` is
    applied — the blind spot the measurement had until `SVG_SPACE`.
    """
    import tempfile
    bad = ('<svg viewBox="0 0 200 100" xmlns="http://www.w3.org/2000/svg">'
           '<text x="10" y="50" class="lbl">a label long enough to overlap</text>'
           '<text x="60" y="50" class="lbl">its neighbour here</text>'
           # On a DIFFERENT baseline, 6 units down — the case the first version of
           # this guard could not see, because it only compared equal rounded y.
           '<text x="70" y="60" class="lbl">and one a baseline below</text>'
           '<text x="150" y="90" class="lbl">and this one runs off the edge</text>'
           # Locally at y=14, twenty units clear; translated, exactly on top of it.
           '<text x="10" y="34" class="lbl">a label up top</text>'
           '<g transform="translate(0 20)">'
           '<text x="10" y="14" class="lbl">lands on it once moved</text></g>'
           # Locally at y=30, well inside; translated, ten units past the bottom.
           '<g transform="translate(0 80)">'
           '<text x="10" y="30" class="lbl">pushed off the bottom</text></g>'
           # Locally left of every label; translated, it ends inside `a label up top`.
           '<g transform="translate(100 0)">'
           '<line x1="-70" y1="5" x2="-60" y2="30" stroke="#000" stroke-width="1"/>'
           '</g>'
           '</svg>')
    with tempfile.TemporaryDirectory() as tmp:
        p = Path(tmp) / "broken.svg"
        p.write_text(bad)
        got = _measure(p)
        drawn = _measure_paths(p)
    vb = got["vb"]
    texts = got["texts"]
    escaped = [t for t in texts if t["x"] + t["w"] > vb["x"] + vb["w"] + SLACK]
    sunk = [t["text"] for t in texts if t["y"] + t["h"] > vb["y"] + vb["h"] + SLACK]
    same_row = cross_row = 0
    clashes = set()
    for i, a in enumerate(texts):
        for b in texts[i + 1:]:
            dx = min(a["x"] + a["w"], b["x"] + b["w"]) - max(a["x"], b["x"])
            dy = min(a["y"] + a["h"], b["y"] + b["h"]) - max(a["y"], b["y"])
            if dx > SLACK and dy > Y_SLACK:
                clashes.add(frozenset((a["text"], b["text"])))
                if round(a["y"]) == round(b["y"]):
                    same_row += 1
                else:
                    cross_row += 1
    top = next(t for t in drawn["texts"] if t["text"] == "a label up top")
    end = next(pth for pth in drawn["paths"] if pth["d"].startswith("<line"))["samples"][-1]
    assert escaped, "the viewBox check did not catch a label off the edge"
    assert same_row, "the overlap check did not catch two labels on one baseline"
    assert cross_row, (
        "the overlap check did not catch two labels on ADJACENT baselines — this is "
        "the blind spot the first version of this guard shipped with")
    assert "pushed off the bottom" in sunk, (
        "the viewBox check did not see a label that its group's transform pushes off "
        "the bottom — measured in local units, as it once was")
    assert frozenset(("a label up top", "lands on it once moved")) in clashes, (
        "the overlap check did not see two labels that meet only once a transform is "
        "applied")
    assert (top["x"] <= end["x"] <= top["x"] + top["w"]
            and top["y"] <= end["y"] <= top["y"] + top["h"]), (
        "the path check did not see a line that reaches a label only through its "
        "group's transform")
