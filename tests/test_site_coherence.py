"""The built site links only to things the build actually produces.

**A dead link on the front door is the expensive defect here.** FOUNDATIONS §8
makes this repo a portfolio artifact as much as a tool, and the one page a
stranger is guaranteed to see is `index.html` — so a nav entry pointing at
nothing costs more than a wrong number somewhere in `src/`.

It had already happened twice over, in two different ways, and neither showed up
in a test or on stderr:

* Two of the four pages had **no nav bar at all**. `diagnostic.html` and
  `landscape.html` are produced by other tools, which is why, and a visitor who
  followed the index to either one was stranded there with no way back except the
  browser's back button. Nothing was broken enough to notice: every link on the
  index resolved, so a check that only looked at the index would have passed.
* The **hero figure and the diagnostic page were built with no detections in
  them.** PR #243 made `_compute` require the sampling interval and
  `tools/make_diagnostic.py` was never updated, so all six detectors raised into
  the per-detector `except` that exists for a detector meeting an awkward slice.
  Both processes exited 0, stderr was clean, and the published page would have
  argued for six detectors above a picture of none.

So the properties below are checked against `build_site.PUBLISHED` and
`build_site.PAGES` rather than against lists this file keeps of its own. A test
carrying its own copy of "the site has four pages" agrees with the build until
somebody adds a fifth, and then it is the test that is wrong.

Everything here is static: no build, no browser, no network. The tests that need
a built `site/` say so and skip without one, the same way `test_site_dates.py`
does — but the front page's own links are checked from the template, so CI
catches a dead nav entry whether or not it built the site first.
"""

from __future__ import annotations

import importlib.util
import re
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
SITE = ROOT / "site"


def _build_site():
    """Load the tool by path — `tools/` is not a package and is not on the path
    in CI, which is how `test_site_dates.py` first went red."""
    spec = importlib.util.spec_from_file_location(
        "build_site", ROOT / "tools" / "build_site.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


bs = _build_site()

#: Schemes that leave the site, plus the in-page anchor. Not this file's problem:
#: whether `https://github.com/...` resolves is a question for the internet, and a
#: test that asks it fails on an aeroplane.
EXTERNAL = re.compile(r"^(https?:|mailto:|data:|blob:|javascript:|#|//)", re.I)

REF = re.compile(r'(?:href|src)\s*=\s*"([^"]+)"', re.I)


def local_refs(html: str) -> set[str]:
    """Every same-site path a page points at, anchors and query strings dropped."""
    out = set()
    for raw in REF.findall(html):
        v = raw.strip()
        if not v or EXTERNAL.match(v):
            continue
        out.add(v.split("#")[0].split("?")[0].lstrip("/"))
    return {v for v in out if v}


def built_pages():
    have = [(name, SITE / name) for name, _ in bs.PAGES]
    missing = [n for n, p in have if not p.is_file()]
    if missing:
        pytest.skip("no built site/ here — run tools/build_site.py")
    return have


# --------------------------------------------------------------------------
# How finished each page says it is.
# --------------------------------------------------------------------------

def test_every_page_says_how_finished_it_is():
    """A public page that says nothing reads as finished, and this site is not.

    Tony, 2026-08-27, on realizing the thing is public while he is still working
    on it. The failure this closes is the quiet one: a fifth page is added to
    `PAGES`, nobody classifies it, and it ships looking done — which is a claim,
    made by omission, on the front door of a portfolio artifact (FOUNDATIONS §8).
    """
    unlabelled = [name for name, _ in bs.PAGES if name not in bs.STATUS]
    assert not unlabelled, (
        f"{unlabelled} are published with no entry in build_site.STATUS, so they "
        f"ship with no banner and read as finished work")
    unknown = {k: v for k, v in bs.STATUS.items() if v not in bs.BANNERS}
    assert not unknown, f"STATUS names a banner that does not exist: {unknown}"


def test_the_banner_travels_with_the_nav_so_no_page_can_lose_it():
    """Both routes onto a page go through `nav_html`, so both carry the label.

    The index writes its own template; the other three are post-processed by
    `add_nav`. Checking the BUILT pages is the point — it is the only way to catch
    a page that took the nav down one path and the banner down neither.
    """
    for name, path in built_pages():
        body = path.read_text(encoding="utf-8")
        kind = bs.STATUS[name]
        badge, _ = bs.BANNERS[kind]
        assert f'class="status {kind}"' in body, (
            f"{name} carries a nav but no {kind} banner")
        # the badge, minus any entity, actually reaches the reader
        assert badge.split(";")[-1].strip() in body, f"{name} banner has no label"


def test_the_viewers_hand_written_banner_matches_the_one_the_build_injects():
    """The viewer is the one page the build may not touch, so its label is a copy.

    `viewer.html` is published byte-for-byte from `docs/site/raster_viewer.html`
    and `tests/test_lab_server.py` pins that, because the page promises the reader
    it reaches nothing and a build that could rewrite it could break the promise.
    That means its nav, its stamp and now its status bar are hand-written — and a
    hand-written copy of a constant is a drift waiting to happen. This is the
    thing that notices.
    """
    src = (ROOT / "docs" / "site" / "raster_viewer.html").read_text(encoding="utf-8")
    assert bs.status_html("viewer.html").strip() in src, (
        "the viewer's hand-written status bar no longer matches "
        "build_site.BANNERS['wip'] — one of the two was edited alone")


def test_running_the_build_twice_does_not_stack_two_banners():
    """`add_nav` is a no-op on a page that already has a bar; prove the banner
    inherits that rather than being appended on every rebuild."""
    for name, path in built_pages():
        if name == "index.html":
            continue                    # written whole from the template each time
        body = path.read_text(encoding="utf-8")
        once = bs.add_nav(body, name)
        assert once == body, f"{name} gained a second banner on rebuild"
        assert body.count('class="status ') == 1, f"{name} has stacked banners"


# --------------------------------------------------------------------------
# The front page, checked from the template — no build required.
# --------------------------------------------------------------------------

def test_the_index_template_links_only_to_files_the_build_writes():
    """The one page every visitor sees, checked in CI whether or not it was built.

    `INDEX` is a format string, so it is rendered with placeholder content first;
    the three figures carry `hero.png`, `reality.png` and `model.png`, which are
    exactly the references most likely to be wrong.
    """
    page = bs.render_index("abc1234", bs.LEAD_FIGURE.format(w=1, h=1),
                           bs.LEAD_REAL.format(w=1, h=1),
                           bs.lead_model(bs.MODEL_SVG.read_text(encoding="utf-8")))
    unresolved = sorted(local_refs(page) - set(bs.PUBLISHED))
    assert not unresolved, (
        f"the front page points at {unresolved}, which the build does not "
        f"produce. Either the build should write it or the page should not "
        f"link to it — a dead link on index.html is the first thing a stranger "
        f"finds (FOUNDATIONS §8).")


def test_the_fallback_front_page_also_links_only_to_real_files():
    """`--allow-degraded` swaps the lead figure for a link card, and that card is
    a link like any other. A path that only appears in the fallback is a path
    nothing normally renders, which is exactly where a dead one survives."""
    page = bs.render_index("abc1234", bs.LEAD_FALLBACK,
                           bs.LEAD_REAL.format(w=1, h=1),
                           bs.lead_model(bs.MODEL_SVG.read_text(encoding="utf-8")))
    assert not sorted(local_refs(page) - set(bs.PUBLISHED))


def test_the_nav_names_every_page_and_invents_none():
    nav = local_refs(bs.nav_html("index.html"))
    assert nav == {name for name, _ in bs.PAGES}
    assert nav <= set(bs.PUBLISHED), (
        "the nav offers a page the build does not publish")


def test_exactly_one_nav_entry_is_marked_as_the_current_page():
    marker = 'aria-current="page"'
    for name, _ in bs.PAGES:
        html = bs.nav_html(name)
        assert html.count(marker) == 1, (
            f"the nav for {name} marks {html.count(marker)} pages as current")
        assert f'href="{name}" {marker}' in html


def test_the_nav_is_added_once_however_many_times_it_is_applied():
    """A rebuild over an existing `site/` must not stack two bars on one page."""
    for shape in ('<!doctype html>\n<meta charset="utf-8">\n<head></head>'
                  '<body>hi</body>',
                  '<!doctype html>\n<meta charset="utf-8">\n<style>p{}</style>\n<p>hi',
                  'bare text with no markup at all'):
        once = bs.add_nav(shape, "index.html")
        assert once.count('nav class="site"') == 1, shape[:40]
        assert bs.add_nav(once, "index.html") == once, shape[:40]


def test_a_page_shaped_like_landscape_gets_its_nav_before_the_content():
    """`landscape.html` has an unclosed `<head>` and no `<body>`, so the anchor is
    the end of its first style block. A `<nav>` there auto-closes the head, which
    is what the parser is specified to do — but only if it lands before the
    document's own content rather than after it."""
    # Written as one literal opening with the doctype: SAP005 reads how a string
    # literal OPENS and matches per line, so a continuation line beginning
    # `<title` reads as a page built with no charset in front of it.
    page = ('<!doctype html>\n<html lang="en">\n<head>\n'
            '<meta charset="utf-8">\n<title>x</title>\n'
            '<style>body{color:red}</style>\n<h1>the content</h1>')
    out = bs.add_nav(page, "landscape.html")
    assert out.index('nav class="site"') < out.index("<h1>")
    assert out.index("</style>") < out.index('nav class="site"')


# --------------------------------------------------------------------------
# The built payload, when there is one.
# --------------------------------------------------------------------------

def test_the_build_writes_exactly_what_it_declares():
    if not (SITE / "index.html").is_file():
        pytest.skip("no built site/ here — run tools/build_site.py")
    got = {str(f.relative_to(SITE)) for f in SITE.rglob("*") if f.is_file()}
    assert got == set(bs.PUBLISHED), (
        f"missing {sorted(set(bs.PUBLISHED) - got)}, "
        f"stray {sorted(got - set(bs.PUBLISHED))}")


def test_every_link_on_every_built_page_resolves_to_a_file_that_exists():
    """The whole point, stated once: nothing published points at nothing."""
    dead = []
    for name, path in built_pages():
        for ref in sorted(local_refs(path.read_text(encoding="utf-8"))):
            if not (SITE / ref).is_file():
                dead.append(f"{name} -> {ref}")
    assert not dead, "dead links in the built site: " + ", ".join(dead)


def test_a_visitor_can_get_from_any_page_to_every_other_page():
    """Reachability in both directions, which is the property that was broken.

    Every link on the index resolved while two of the four pages had no nav at
    all, so this asks the question the other way round: standing on each page in
    turn, can you get to all the others?
    """
    stranded = []
    for name, path in built_pages():
        refs = local_refs(path.read_text(encoding="utf-8"))
        for other, _ in bs.PAGES:
            if other != name and other not in refs:
                stranded.append(f"{name} offers no way to {other}")
    assert not stranded, "; ".join(stranded)


def test_every_page_with_a_nav_bar_also_carries_the_style_for_it():
    """Markup and styling went missing separately, and only one was checked.

    The fix for the two navless pages factored the rules into `NAV_CSS` and
    injected them alongside the markup — but `add_nav` returns early on a page
    that already has a bar, and the index has its bar written into its own
    template. So the index kept the markup, lost the rules, and the site's front
    door shipped as a row of default-blue underlined links.

    Every structural check passed while it did: the bar was present, every link
    resolved, every page was reachable from every other. It took opening a
    screenshot. This asserts the pair instead — a page carrying one and not the
    other is that bug, in either direction.
    """
    unstyled = []
    for name, path in built_pages():
        body = path.read_text(encoding="utf-8")
        has_markup = 'nav class="site"' in body
        has_css = "nav.site" in body
        if has_markup != has_css:
            unstyled.append(
                f"{name}: nav markup {'present' if has_markup else 'absent'}, "
                f"its CSS {'present' if has_css else 'absent'}")
    if unstyled:
        # Say WHICH failure this is before accusing anybody of anything. `site/`
        # is gitignored, so a checkout that built it once and then pulled holds a
        # payload describing an older tree, and the honest answer there is
        # "rebuild" rather than a report of a defect that was fixed commits ago.
        #
        # This test exists because a guard was right about the property and wrong
        # about the evidence — and it then shipped with the same fault, naming on
        # a stale payload the exact defect it was written to detect. Two other
        # tests in this suite already had the answer.
        stale = bs.stale_build_note(SITE)
        assert not stale, stale
    assert not unstyled, "; ".join(unstyled)


def test_no_published_page_is_titled_after_the_tool_that_made_it():
    """`diagnostic.html` came out of Panel titled `Panel`, and that is the text in
    the browser tab, the bookmark and the link preview."""
    bad = []
    for name, path in built_pages():
        # `(?si)` inline rather than as flags, so the pattern literal does not
        # OPEN with `<title` — which is what SAP005 reads, and it cannot tell a
        # regex from a page.
        m = re.search(r"(?si)<title>(.*?)</title>", path.read_text(encoding="utf-8"))
        title = (m.group(1).strip() if m else "")
        if not title or title.lower() in {"panel", "bokeh", "holoviews",
                                          "untitled", "document"}:
            bad.append(f"{name}: {title!r}")
    assert not bad, ("published with a generator's default title: "
                     + ", ".join(bad))


# --------------------------------------------------------------------------
# The build refuses to publish a page that is missing part of itself.
# --------------------------------------------------------------------------

def test_the_sidecar_parser_finds_the_detectors_that_did_not_run():
    """The real sidecar from the day all six broke, trimmed to its shape."""
    sidecar = (
        "bugarach coordination diagnostic — seed 3\n"
        "30 ROI · 1800s · 15 planted events\n\n"
        "detector      recall  prec    F1\n"
        "----------------------------------\n\n"
        "did not run:\n"
        "  loco: TypeError: _compute() missing 1 required keyword-only argument: 'dt'\n"
        "  sync: TypeError: _compute() missing 1 required keyword-only argument: 'dt'\n"
        "\nDetectors run at the operating points declared in bugarach.bench.\n")
    assert bs.detectors_that_did_not_run(sidecar) == ["loco", "sync"]


def test_the_built_site_shipped_with_every_detector_scored():
    """The regression itself, asserted against the payload rather than the parser.

    `build_site.py` refuses this at build time, which is where it belongs. This is
    the second lock: a `site/` produced by an older build, or by
    `--allow-degraded`, or by hand, does not get to sit in the tree looking
    finished. The sidecar is published — it is one of the eight files in
    `PUBLISHED` — so this costs a file read.
    """
    sidecar = SITE / "diagnostic.txt"
    if not sidecar.is_file():
        pytest.skip("no built site/ here — run tools/build_site.py")
    silent = bs.detectors_that_did_not_run(sidecar.read_text(encoding="utf-8"))
    assert not silent, (
        f"the published diagnostic scored none of {silent} — the hero figure on "
        f"index.html is missing that many lanes, and the paragraph above it "
        f"promises six detectors. Rebuild; if it will not build, that is the bug.")


def test_a_sidecar_where_everything_ran_reports_nothing():
    ok = ("detector      recall  prec    F1\n"
          "LoCo           1.00   1.00   1.00\n\n"
          "Detectors run at the operating points declared in bugarach.bench.\n")
    assert bs.detectors_that_did_not_run(ok) == []
    assert bs.detectors_that_did_not_run("") == []
