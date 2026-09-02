"""The front page's model figure is a committed file, so something has to prove it still matches the model.

``tools/make_architecture_diagram.py`` exists because the SVG it replaced
hardcoded ``1,128 params`` in its own markup, and its docstring says why in
terms: *"A number in a figure that a human maintains by hand is a number that
goes stale silently."*

**That argument does not stop at the number.** The generator reads everything off
``build_tube()``, but its output is written to ``docs/learned/architecture.svg``
and committed, and ``build_site.py`` inlines that file rather than running the
generator. So the defect moved up one level: it is no longer a number a human
maintains by hand, it is a *file* a human regenerates by hand — and the next
change to ``src/bugarach/learn/nets/tube.py`` leaves the published front page
asserting the old model, with nothing red anywhere to say so.

These tests close that. They are the mechanized form of the rule the generator
already states about itself, and they cost milliseconds: the model is 1,149
parameters and instantiating it is the same act the generator performs.

Both skip rather than fail without torch, because a clone that cannot build the
model cannot check the figure either, and a skip says that honestly where a
failure would blame the figure.

⚠ **IN A WORKTREE THIS CHECK IS WEAKER THAN IT LOOKS, AND NOT BECAUSE OF
ANYTHING HERE.** A worktree imports the *primary checkout's* ``src`` — see
``docs/todo/2026-08-15-worktrees-import-the-primary-checkouts-src.md``, still
open — so a session editing ``nets/tube.py`` in a worktree gets a figure
regenerated from the primary's model and these tests go green on a comparison
they did not really make. CI is a fresh clone with one ``src``, so the gate is
sound where it matters; this is written down because a staleness test that can
be quietly satisfied by the wrong source is the exact shape of failure the rest
of this file exists to prevent, and the next person to see it pass in a worktree
should know what it did and did not prove.
"""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO / "tools"))

COMMITTED = REPO / "docs" / "learned" / "architecture.svg"

make_architecture_diagram = pytest.importorskip("make_architecture_diagram")


def _regenerated(tmp_path: Path) -> str:
    pytest.importorskip(
        "torch",
        reason="the diagram is generated FROM the built module; with no torch "
               "there is nothing to compare the committed file against")
    rc = make_architecture_diagram.main(["--out", str(tmp_path)])
    assert rc == 0, "the generator refused to build the model it draws"
    return (tmp_path / "architecture.svg").read_text(encoding="utf-8")


def test_the_committed_svg_is_what_the_generator_produces_now(tmp_path):
    """The whole file, byte for byte — not a spot-check on the total.

    Comparing only the parameter count would pass a figure whose dilation
    schedule, channel width or kernel size had moved, and those are exactly the
    quantities the generator was written to stop anyone from typing.
    """
    assert COMMITTED.read_text(encoding="utf-8") == _regenerated(tmp_path), (
        f"{COMMITTED.relative_to(REPO)} is not what "
        f"tools/make_architecture_diagram.py produces from the model as it "
        f"stands. The model moved and the figure did not — the front page is "
        f"drawing the old one. Regenerate:\n\n"
        f"    python tools/make_architecture_diagram.py\n\n"
        f"and commit the result with whatever changed the model.")


def test_the_generator_is_deterministic(tmp_path):
    """Two runs agree, so a failure above means the model moved and nothing else.

    Without this, the check above has a second reading — dict ordering, a float
    that formats differently, an id that counts up — and a session facing a red
    suite would have to rule that out before believing it.

    ⚠ **WHAT THIS DOES NOT COVER, AND THE SENTENCE THAT USED TO SAY IT DID.**
    This docstring previously went on: *"The generator draws an architecture, so
    it must not depend on initialised weights … a figure that redrew itself per
    seed would be describing a run."* The first clause is the right ambition and
    the second does not deliver it. `build_tube` initialises `log_center`
    **deterministically** at 1/2/4/8 samples, so a fitted quantity baked into the
    figure is baked identically on every run and both comparisons agree. The
    figure could state an initialisation as though it were an architectural
    constant and this test would be green — which is exactly the defect
    `docs/todo/2026-09-01-a-traced-figure-cannot-tell-a-constant-from-an-
    initialisation.md` was filed about, in this very figure, at the same time
    this test was written.

    **Determinism and architecture are different claims**, and only the first one
    is checked here. Found by `draughtsman` while vendoring against this gate,
    2026-09-01; recorded rather than quietly reworded, because a check whose
    docstring overstates its reach is worse than no check. What actually closes
    the gap lives upstream in draughtsman's `check` stage: torch warns when it
    bakes a Python-arithmetic constant into a trace, and a spec may not quote such
    a constant until it declares why that one is architectural.
    """
    first = _regenerated(tmp_path)
    second = _regenerated(tmp_path / "again")
    assert first == second, (
        "the diagram is not reproducible from one run to the next, so it is "
        "reading something that is not the architecture — most likely a "
        "randomly initialised weight, which belongs in "
        "tools/make_architecture_figures.py and not here")
