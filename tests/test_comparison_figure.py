"""The fair comparison's four architectures: traced as registered, placed at one scale.

Two things here were each green while wrong before they were tested.

* ``build_chorus_norm()`` called bare builds plain ``chorus``: the registered
  ``norm=True`` never reaches it. draughtsman's tracer calls its target with no
  arguments, so the first trace of ``chorus_norm`` was of the failed control, and
  coverage passed because the graph was complete — of the wrong model.
* Four figures each stretched to one slot are four scales. The page composes them
  at their own extents and has to keep doing so.

The staleness of each figure against its model is not here: the four are ``DRAWABLE``
entries, so ``test_architecture_diagram_is_current.py`` already regenerates them.
"""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO / "tools"))

mcf = pytest.importorskip("make_comparison_figure")


def test_the_registry_target_builds_the_registered_model_and_the_bare_builder_does_not():
    torch = pytest.importorskip("torch")  # noqa: F841
    from bugarach.learn import registered
    from bugarach.learn.nets import ARCHITECTURES, n_params
    from bugarach.learn.nets.chorus_gain_norm import build_chorus_gain_norm

    want = n_params(ARCHITECTURES["chorus_gain_norm"].make())
    assert n_params(registered.chorus_gain_norm()) == want
    # The trap itself, pinned so a fix to the builders is noticed and this
    # module's reason for existing can be revisited rather than kept by habit.
    assert n_params(build_chorus_gain_norm()) != want


def test_an_unregistered_name_is_an_attribute_error():
    pytest.importorskip("torch")
    from bugarach.learn import registered
    with pytest.raises(AttributeError):
        registered.no_such_architecture  # noqa: B018


def test_every_compared_architecture_is_drawable_through_the_registry():
    from make_architecture_diagram import COMPARED, DRAWABLE
    for arch in COMPARED:
        assert f"comparison/{arch}.svg" in DRAWABLE[arch]["figures"], arch
        if arch != "tube":
            assert DRAWABLE[arch]["target"] == f"bugarach.learn.registered:{arch}"


def test_the_page_places_every_panel_at_its_own_extent(tmp_path):
    """One scale: each nested panel is exactly as wide and tall as its viewBox."""
    panels = [mcf.Panel(a) for a in mcf.COMPARED]
    mcf.one_scale(panels)
    svg = mcf.compose(panels)
    nested = re.findall(r'<svg x="[\d.]+" y="[\d.]+" width="([\d.]+)" height="([\d.]+)"'
                        r'[^>]*viewBox="0 0 ([\d.]+) ([\d.]+)"', svg)
    assert len(nested) == len(panels)
    for w, h, vw, vh in nested:
        assert float(w) == pytest.approx(float(vw), abs=0.01)
        assert float(h) == pytest.approx(float(vh), abs=0.01)
    ids = re.findall(r'\sid="([^"]+)"', svg)
    assert len(ids) == len(set(ids)), "a panel's arrows would use another panel's marker"


def test_the_page_fits_the_slot_every_spec_was_checked_against():
    panels = [mcf.Panel(a) for a in mcf.COMPARED]
    width = float(re.search(r'viewBox="0 0 ([\d.]+)', mcf.compose(panels)).group(1))
    slot = float(panels[0].output["width"].removesuffix("px"))
    assert width <= slot


def test_a_panel_drawn_for_another_slot_is_refused(monkeypatch):
    panels = [mcf.Panel(a) for a in mcf.COMPARED]
    monkeypatch.setitem(panels[-1].output, "width", "6in")
    with pytest.raises(SystemExit, match="one output.width"):
        mcf.one_scale(panels)


def test_every_comparison_spec_breaks_its_rows_by_name():
    """The row breaks carry the comparison; a spec that wraps by width instead
    would let the packer move the cut and nothing would say so."""
    for arch in mcf.COMPARED:
        spec = json.loads((mcf.COMPARISON / f"{arch}.spec.json").read_text())
        assert spec["layout"].get("breaks"), arch
        assert "wrap" not in spec["layout"], arch
