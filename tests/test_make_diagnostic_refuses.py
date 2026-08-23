"""The site's own figure cannot be published empty.

`tools/make_diagnostic.py` draws the front page's lead image and the Detector
diagnostic page. On 2026-08-23 it produced both with **no detector lanes at all**
for a day, and exited 0 the whole time.

`ui.app._compute` gained a required keyword-only `dt` and this tool's call site
did not, so every detector raised `TypeError`. The tool's own `except` — written
for the good reason that *one* detector failing on an awkward slice is a finding
worth printing rather than a crash worth losing the figure to — swallowed all six
identically. `build_site.py` judges the step by its return code, got 0, and
published an empty raster under a caption describing lanes nobody could see.

Then the same call site broke a second way in the same day: `StreamResult` gained
a fifth field and `t, y, events, extra = ...` started raising "too many values to
unpack" — again for all six, again silently.

So the property under test is not "the figure renders". It is **that the tool
refuses rather than shipping something that is not the figure**, and that its
sampling interval comes off the recording instead of a constant.
"""

from __future__ import annotations

import importlib.util
from pathlib import Path

import pytest

hv = pytest.importorskip("holoviews")

ROOT = Path(__file__).resolve().parents[1]


def _tool():
    """Load the CLI by path — `tools/` is not a package and is not on sys.path."""
    spec = importlib.util.spec_from_file_location(
        "make_diagnostic", ROOT / "tools" / "make_diagnostic.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


md = _tool()


def _args(**over):
    """The CLI's own defaults, shrunk to something quick."""
    ns = md.main.__wrapped__ if hasattr(md.main, "__wrapped__") else None
    import argparse
    a = argparse.Namespace(
        seed=3, duration=600.0, n_roi=12, per_level=2, interval_cv=1.0,
        hot=False, hot_rate=0.25, distractors=0, height=300, bench=None,
        tag="t", out=None, png=False, scale=1, hero=None)
    for k, v in over.items():
        setattr(a, k, v)
    return a


def test_every_detector_running_is_the_normal_case():
    """The regression itself: all six reach the figure, by name not by position."""
    fig, legend, header, report, pn = md.build(_args())
    for name in ("LoCo", "CICADA", "binned SCE", "CoactDetect", "rate+context",
                 "SPIKE-synch"):
        assert name in report, f"{name} is missing from the figure's own table"
    assert "did not run" not in report, report


def test_the_interval_comes_off_the_recording_not_a_constant():
    """FOUNDATIONS §6. The tool must not carry a fourth hardcoded 0.1.

    Asserted by watching what `_compute` is handed, because a constant that
    happens to equal the recording's interval passes any test of the output.
    """
    seen = {}
    real = md._compute

    def spy(det, s, ext, params, *, dt):
        seen[det] = (dt, s.dt)
        return real(det, s, ext, params, dt=dt)

    md._compute = spy
    try:
        md.build(_args())
    finally:
        md._compute = real
    assert seen, "no detector was run at all"
    for det, (passed, recorded) in seen.items():
        assert passed == recorded, (
            f"{det} was run at dt={passed} while the recording states "
            f"{recorded} — the figure is drawn on a grid the data does not have")


def test_all_six_failing_is_a_refusal_not_a_figure():
    """One detector failing is a finding. Six is the tool being broken.

    This is the test that would have caught the day-long outage: it fails if the
    tool writes anything when nothing ran.
    """
    real = md._compute

    def broken(det, s, ext, params, *, dt):
        raise TypeError("_compute() missing 1 required keyword-only argument: 'dt'")

    md._compute = broken
    try:
        with pytest.raises(md.NoFigure) as exc:
            md.build(_args())
    finally:
        md._compute = real
    assert "NO detector ran" in str(exc.value)
    assert "dt" in str(exc.value), "the refusal must name why each detector failed"


def test_the_refusal_reaches_the_exit_code(tmp_path, capsys):
    """`build_site.py` judges this step by its return code and nothing else.

    A refusal that printed to stderr and still returned 0 is exactly the shape of
    the original bug, so the exit code is the property, not the message.
    """
    real = md._compute

    def broken(det, s, ext, params, *, dt):
        raise TypeError("boom")

    md._compute = broken
    try:
        rc = md.main(["--out", str(tmp_path), "--duration", "600", "--n-roi", "12",
                      "--per-level", "2", "--no-hot", "--distractors", "0",
                      "--no-png", "--tag", "t"])
    finally:
        md._compute = real
    assert rc == 1, "a figure that could not be drawn must not exit 0"
    assert not list(tmp_path.glob("*.html")), (
        "the tool wrote a page it had just refused to draw")
    assert "refusing" in capsys.readouterr().err.lower()


def test_one_detector_failing_still_draws_the_others():
    """The behaviour the refusal must not have swallowed.

    The `except` this test protects is correct and load-bearing: loco and cicada
    once failed outright on a single-stream slice, and losing the whole figure to
    that would have been worse than losing one lane.
    """
    real = md._compute

    def one_bad(det, s, ext, params, *, dt):
        if det == "sce":
            raise ValueError("cannot run here")
        return real(det, s, ext, params, dt=dt)

    md._compute = one_bad
    try:
        fig, legend, header, report, pn = md.build(_args())
    finally:
        md._compute = real
    assert "did not run" in report and "sce" in report
    assert "LoCo" in report, "the other five must still be drawn"
