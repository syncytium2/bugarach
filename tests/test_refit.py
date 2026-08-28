"""The re-fit driver proposes and does not adopt, and a refusal is a row.

The behaviours worth pinning are not the numbers — those are the campaign's job
— but the three promises the tool makes about itself: it never writes an
operating point, a selection refusal comes back as a recorded outcome rather
than a traceback that ends the campaign at its first detector, and a decimated
grid says out loud that it is decimated.
"""
from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "src"))

from bugarach import bench  # noqa: E402


def _load():
    spec = importlib.util.spec_from_file_location("refit", ROOT / "tools" / "refit.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


refit = _load()


class _Fake:
    """A BenchResult-shaped stand-in — enough fields for a row and a table."""

    def __init__(self, knob_value, f1, hot=0.0, detector="coact",
                 regime="baseline_quiet"):
        self.knob_value = knob_value
        self.f1 = f1
        self.detector = detector
        self.regime = regime
        self.recall = f1
        self.precision = f1
        self.n_hit = 1
        self.n_planted = 2
        self.n_detected = 2
        self.n_fa = 1
        self.hot_fa = 0
        self.hot_fa_per_min = hot


def _curve(f1s, hot=0.0, detector="coact"):
    return [_Fake(float(i), f, hot, detector) for i, f in enumerate(f1s)]


def test_a_refusal_is_a_row_not_a_traceback(monkeypatch):
    """EdgeOfRange must not end the campaign — it is the finding about that grid.

    A driver that lets the first refusal propagate reports one detector and calls
    it a run.
    """
    monkeypatch.setattr(refit, "sweep",
                        lambda *a, **k: _curve([0.4, 0.6, 0.7, 0.8, 0.9]))
    row = refit.refit_one("coact", "baseline_quiet", (1,))
    assert row["verdict"] == "EdgeOfRange"
    assert row["chosen"] is None
    assert row["moves"] is None
    assert "still climbing" in row["reason"]
    assert len(row["curve"]) == 5, "the curve survives the refusal"


def test_the_probe_gate_reaches_the_driver(monkeypatch):
    """A winner that fires where nothing was planted comes back TooPromiscuous.

    This is the gate that has been in `pick_operating_point` since 2026-08-22 and
    is the reason the driver does not need a promiscuity term of its own.
    """
    ceiling = bench.MAX_PROBE_PER_MIN["rate"]
    monkeypatch.setattr(refit, "sweep",
                        lambda *a, **k: _curve([0.4, 0.9, 0.5],
                                               hot=ceiling + 10.0,
                                               detector="rate"))
    row = refit.refit_one("rate", "baseline_quiet", (1,))
    assert row["verdict"] == "TooPromiscuous"
    assert row["chosen"] is None


def test_a_chosen_point_reports_whether_it_moves(monkeypatch):
    monkeypatch.setattr(refit, "sweep", lambda *a, **k: _curve([0.4, 0.9, 0.5]))
    row = refit.refit_one("coact", "baseline_quiet", (1,))
    assert row["verdict"] == "chosen"
    assert row["chosen"]["knob_value"] == 1.0
    # shipped alpha is not 1.0, so this is a move
    assert row["moves"] is True
    assert row["shipped"] == bench.OPERATING_POINTS["coact"].params["alpha"]


def test_the_driver_never_adopts(monkeypatch):
    """The whole point: no path through this tool assigns an operating point."""
    before = {k: dict(v.params) for k, v in bench.OPERATING_POINTS.items()}
    monkeypatch.setattr(refit, "sweep", lambda *a, **k: _curve([0.4, 0.9, 0.5]))
    refit.refit_one("coact", "baseline_quiet", (1,))
    after = {k: dict(v.params) for k, v in bench.OPERATING_POINTS.items()}
    assert before == after

    src = (ROOT / "tools" / "refit.py").read_text(encoding="utf-8")
    assert "OPERATING_POINTS[" not in src.replace(
        "OPERATING_POINTS[name]", "").replace(
        "OPERATING_POINTS[det]", ""), (
        "the driver reads OPERATING_POINTS by name for the knob and the shipped "
        "value; anything else indexing it is a write waiting to happen")


def test_quick_says_it_is_quick():
    """A decimated grid manufactures EdgeOfRange, so the text must disclose it.

    Without this the smoke test's output is byte-shaped like a campaign's, which
    is how a decimation gets quoted as a finding.
    """
    rows = [{"detector": "coact", "regime": "baseline_quiet",
             "verdict": "EdgeOfRange", "shipped": 1e-4, "chosen": None,
             "moves": None, "reason": "still climbing"}]
    assert "--quick" in refit.summarise(rows, quick=True)
    assert "--quick" not in refit.summarise(rows, quick=False)


def test_unknown_detector_is_refused():
    with pytest.raises(KeyError):
        refit.refit_one("nosuchdetector", "baseline_quiet", (1,))
