"""The diagnostic refuses rather than shipping something that is not the figure.

The property under test is **not** "the figure renders". It is that a run which
cannot produce the figure says so in the one channel its caller reads, and leaves
nothing behind that could be mistaken for a result.

Twice in one day `tools/make_diagnostic.py` drew a raster with six blank detector
lanes and exited 0. Both times the cause was the same shape — `_compute`'s
signature changed and this caller was not updated with it, first when `dt` became
required (PR #243) and then when `StreamResult` grew a fifth field — and both
times all six detectors raised into the per-detector `except` that exists so one
awkward slice cannot lose the whole figure. The sidecar listed six identical
tracebacks. Nothing was red. `tools/build_site.py` put the result on the front
page, where it read as six detectors finding nothing.

**An empty figure is worse than no figure**, and worse than the link card the
site falls back to, because both of those announce themselves. This one looked
like a figure: a valid 196 KB PNG with labelled lanes.

So the threshold here is *all six*, not *any*. A single detector failing stays a
finding recorded in the sidecar — that `except` is correct and load-bearing, and
`test_one_detector_failing_still_draws_the_other_five` is what stops a later
session from tightening this into uselessness. The site build applies the
stricter `any` at publish time, in `tools/build_site.py`, where the page's own
text promises six.
"""

from __future__ import annotations

import importlib.util
import sys
import types
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]


def _make_diagnostic():
    """Load the tool by path — `tools/` is not a package and is not importable as
    one in CI, which is how `test_site_dates.py` first went red."""
    spec = importlib.util.spec_from_file_location(
        "make_diagnostic", ROOT / "tools" / "make_diagnostic.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


md = _make_diagnostic()


def args(**over):
    """The tool's defaults, small and fast. Duration is the one that costs."""
    base = dict(seed=3, duration=300.0, n_roi=12, per_level=2, interval_cv=1.0,
                hot=True, hot_rate=0.25, distractors=2, height=300, bench=None)
    base.update(over)
    return types.SimpleNamespace(**base)


@pytest.fixture
def spy(monkeypatch):
    """Stand in for `_compute` and record how it was called.

    `build` imports `_compute` from `bugarach.ui.app` *inside* the function, so
    the patch has to land on the module it is imported from rather than on a name
    in this one.
    """
    from bugarach.ui import app

    calls = []
    real = app._compute          # bind BEFORE patching, or `fake` calls itself

    def fake(det, s, ext, params, *, dt):
        calls.append({"det": det, "dt": dt, "slice": s})
        return real(det, s, ext, params, dt=dt)

    monkeypatch.setattr(app, "_compute", fake)
    return calls


# ---------------------------------------------------------------------------
# the regression itself
# ---------------------------------------------------------------------------

def test_all_six_detectors_reach_the_score_table():
    """The defect, stated as the thing that was false while it was live."""
    _, _, _, _, report, _ = md.build(args())
    assert "did not run" not in report, (
        "a detector failed to run in the default figure:\n" + report)
    # 'sixth', not the detector's name: it is withheld from the public build
    # while its attribution is settled, and the figure labels it neutrally. The
    # DETECTOR still runs and still reaches this table — that is what this asserts.
    for name in ("LoCo", "sixth", "binned SCE", "CoactDetect", "rate+context",
                 "SPIKE-synch"):
        assert name in report, f"{name} is missing from the score table:\n{report}"


def test_every_detector_is_handed_the_recordings_own_interval(spy):
    """Spied, not inferred from the output.

    A hardcoded constant that happens to equal this recording's 0.1 s passes any
    test that only reads the figure — which is precisely the fabricated-interval
    failure FOUNDATIONS §6 exists to stop, and it would sail through a check on
    the numbers. So the assertion is on the argument.
    """
    md.build(args())
    assert spy, "_compute was never called"
    for call in spy:
        want = call["slice"].require_dt("the diagnostic figure")
        assert call["dt"] == want, (
            f"{call['det']} was handed dt={call['dt']}, but the recording "
            f"states {want}")


def test_the_interval_comes_from_the_recording_not_from_a_constant(spy):
    """Change the recording's interval and the argument must move with it.

    Pinning the value to 0.1 would pass the test above forever. This one fails
    for any implementation that is not actually reading the slice.
    """
    import dataclasses

    from bugarach.simulate import simulate_coordination

    s, _ = simulate_coordination(seed=3, duration_sec=300, n_roi=6,
                                 n_per_level=(1, 1, 1))
    assert s.dt is not None, "the generator stopped declaring its grid"
    assert md._dt_for(s) == s.dt
    assert md._dt_for(dataclasses.replace(s, dt=0.05)) == 0.05


# ---------------------------------------------------------------------------
# the refusal
# ---------------------------------------------------------------------------

def test_all_six_failing_raises_instead_of_returning_a_figure(monkeypatch):
    from bugarach.ui import app

    def broken(det, s, ext, params, *, dt):
        raise TypeError("_compute() missing 1 required keyword-only argument: 'dt'")

    monkeypatch.setattr(app, "_compute", broken)
    with pytest.raises(md.NoDetectorRan) as e:
        md.build(args())
    # the message has to carry what each one raised, or the next person debugging
    # this is back to reading a blank figure
    assert "missing 1 required keyword-only argument" in str(e.value)


def test_the_refusal_reaches_the_exit_code_and_writes_no_file(monkeypatch, tmp_path):
    """`build_site.py` reads this process's return code and nothing else.

    A refusal that printed to stderr and still returned 0 is the original bug
    wearing a different hat — that is the whole reason this test names the exit
    code rather than the message.
    """
    from bugarach.ui import app

    monkeypatch.setattr(app, "_compute",
                        lambda *a, **k: (_ for _ in ()).throw(ValueError("nope")))
    rc = md.main(["--out", str(tmp_path), "--duration", "600", "--n-roi", "12",
                  "--per-level", "2", "--tag", "t", "--no-png"])
    assert rc != 0, "the tool reported success after drawing nothing"
    assert list(tmp_path.iterdir()) == [], (
        f"a refused run still wrote {[p.name for p in tmp_path.iterdir()]} — an "
        f"empty figure left on disk is what somebody publishes next")


def test_one_detector_failing_still_draws_the_other_five(monkeypatch):
    """The `except` is correct and load-bearing. This is what protects it.

    A detector that cannot run on a particular slice is a finding, and losing the
    whole figure over it would be a worse tool. Anyone tightening the refusal
    above from *all* to *any* has to delete this test first, and read why.
    """
    from bugarach.ui import app

    real = app._compute

    def one_bad(det, s, ext, params, *, dt):
        if det == "sync":
            raise RuntimeError("this detector cannot run on this slice")
        return real(det, s, ext, params, dt=dt)

    monkeypatch.setattr(app, "_compute", one_bad)
    _, _, _, _, report, _ = md.build(args())
    assert "did not run" in report and "sync" in report, (
        "the failure was not recorded in the sidecar:\n" + report)
    assert "LoCo" in report and "sixth" in report, (
        "the surviving detectors were not drawn:\n" + report)


def test_the_refusal_says_it_is_the_call_site_and_not_six_findings():
    """The message is the whole value of the guard.

    Six identical tracebacks in a sidecar read as six detector problems, and both
    times that is not what it was. Whoever meets this next should be pointed at
    `_compute`'s signature, not at the detectors.
    """
    doc = md.NoDetectorRan.__doc__ or ""
    assert "signature" in doc or "_compute" in doc
