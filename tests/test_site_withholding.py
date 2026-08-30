"""A withheld detector must be withheld in the FIGURES too, not just the pages.

Tony, 2026-08-29: *"withold cicada locust entirely. we must be able to remove or
add detectors and models at will. there's no reason for cicada/locust to be
present in the current webpage."*

**The requirement is the mechanism, not the case.** The viewer's `WITHHELD` set is
the one declaration of what this build ships; everything that offers a detector
reads it, and `build_site.py` parses it so the Python-rendered figures agree.

⚠ **THE FAILURE THIS EXISTS FOR IS INVISIBLE TO EVERY OTHER CHECK.** The site's
lane labels are rendered into `hero.png` and `diagnostic.png` by
`bugarach.ui.app.TITLES`. A detector's name reaches a reader through a y-axis
label exactly as well as through a paragraph — and **no grep of the served HTML
can see a picture**. On 2026-08-29 every served page was scrubbed clean while both
figures still carried the name, and the only reason it was caught was somebody
opening the PNG.

So the property is not "the string is absent from the HTML". The `cicada` key
stays: it is `detections.csv`'s `detector` value and output contract. The property
is that **nothing this build renders offers or names a withheld detector.**
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
VIEWER = ROOT / "docs/site/raster_viewer.html"
sys.path.insert(0, str(ROOT / "tools"))


def _viewer_withheld() -> list[str]:
    m = re.search(r"const WITHHELD = new Set\(\[(.*?)\]\)",
                  VIEWER.read_text(encoding="utf-8"), re.S)
    assert m, "the viewer has no WITHHELD set — the mechanism is gone"
    return sorted(re.findall(r'"([^"]+)"', m.group(1)))


def test_the_build_reads_the_viewers_list_rather_than_keeping_its_own():
    """One declaration, two consumers. Two copies would drift in exactly one
    direction — page clean, figure not — which is the direction nobody checks."""
    import build_site

    assert sorted(build_site.WITHHELD_FROM_THE_BUILD) == _viewer_withheld(), (
        "build_site and the viewer disagree about what this build withholds; "
        "the figures and the pages are about to describe different builds")


def test_the_build_refuses_rather_than_guessing_if_the_set_disappears(tmp_path,
                                                                     monkeypatch):
    """If the parse stops matching, the figures would be built with every
    detector in them and nothing would say so. It raises instead."""
    import build_site

    fake = tmp_path / "docs" / "site"
    fake.mkdir(parents=True)
    # Deliberately not a document — the point is only that the parse finds no
    # WITHHELD set. Writing a stub page here would trip SAP005, which requires a
    # charset on any HTML built in this repo, and it would be right to: a fixture
    # that looks like a page is one somebody later copies as if it were one.
    (fake / "raster_viewer.html").write_text("no such set here")
    monkeypatch.setattr(build_site, "ROOT", tmp_path)
    with pytest.raises(SystemExit) as e:
        build_site._withheld_from_the_viewer()
    assert "WITHHELD" in str(e.value)


def test_a_withheld_detector_has_no_operating_point_in_the_figure():
    """`make_diagnostic` is the tool that draws the lanes. Asked to withhold one,
    it must not hand that detector's params to the figure at all — a lane is
    drawn from what this returns."""
    import make_diagnostic

    every = make_diagnostic._detector_params()
    assert every, "no operating points at all; this test would pass vacuously"
    for k in _viewer_withheld():
        assert k in every, (
            f"{k} is withheld but has no operating point — this test can no "
            f"longer tell withholding from absence")

    fewer = make_diagnostic._detector_params(_viewer_withheld())
    for k in _viewer_withheld():
        assert k not in fewer, f"{k} still reaches the figure"
    assert set(fewer) == set(every) - set(_viewer_withheld()), (
        "withholding removed something it was not asked to remove")


def test_the_default_still_draws_everything():
    """A troubleshooting run is not a release. `--without` defaults to nothing,
    so the tool a person reaches for when a detector misbehaves still shows it."""
    import make_diagnostic

    assert set(make_diagnostic._detector_params()) == \
        set(make_diagnostic._detector_params(())), (
            "the default dropped a detector; withholding belongs to the BUILD, "
            "not to the tool")


@pytest.mark.parametrize("figure", ["hero.png", "diagnostic.png"])
def test_the_built_figures_exist_to_be_checked(figure):
    """Not a content assertion — a reminder that the artifact is a picture.

    Skips when the site has not been built, because a clean clone has no
    `site/`. What it pins is that these two files are the ones a reviewer has to
    OPEN; `tests/test_site_viewer.py` can only read text.
    """
    p = ROOT / "site" / figure
    if not p.is_file():
        pytest.skip("site/ not built here — `python tools/build_site.py` first")
    assert p.stat().st_size > 10_000, (
        f"{figure} is suspiciously small; it may have failed to render")
