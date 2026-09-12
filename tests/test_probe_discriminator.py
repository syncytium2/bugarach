"""`tools/probe_discriminator.py` on a synthetic export folder.

What this pins, and why each is here rather than discovered overnight:

* the tier is refused when the pairs available cannot reach the declared power — the
  arithmetic that was true on 2026-09-10 and computed on 2026-09-12, by which time a
  night had already reported "underpowered" on cell after cell;
* a refusal spends nothing: no control is run and no draw is generated;
* with the flag, both controls run and are reported separately, because a tier whose
  negative control flags cannot be read at all — which is what voided every fast-stream
  accuracy in the 2026-09-11 run.

Synthetic data only.
"""

from __future__ import annotations

import importlib.util
import json
import sys
from pathlib import Path

import pytest

pytest.importorskip("elephant")          # the positive control runs the real generator

TOOL = Path(__file__).resolve().parents[1] / "tools" / "probe_discriminator.py"

# The synthetic export folder is the screen tests' own builder rather than a second copy:
# two fixtures drifting apart is how a probe starts testing a folder the grid never sees.
sys.path.insert(0, str(Path(__file__).resolve().parent))
from test_build_surrogate_screen import _folder            # noqa: E402


@pytest.fixture(scope="module")
def pd_tool():
    spec = importlib.util.spec_from_file_location("_probe_disc", TOOL)
    m = importlib.util.module_from_spec(spec)
    sys.modules["_probe_disc"] = m
    spec.loader.exec_module(m)
    return m


@pytest.fixture(scope="module")
def folder(tmp_path_factory):
    return _folder(tmp_path_factory.mktemp("probe") / "export")


def _report(out: Path) -> dict:
    return json.loads((out / "discriminator_probe.json").read_text(encoding="utf-8"))


def test_it_refuses_when_the_pairs_cannot_reach_the_declared_power(pd_tool, folder,
                                                                   tmp_path):
    """654 pairs are needed at alpha 0.05 for a 55% effect at power 0.8. Twelve
    synthetic recordings of 900 s give 15 windows each — 180 pairs, power about 0.33 —
    so the run is refused before a single surrogate is drawn."""
    out = tmp_path / "refused"
    rc = pd_tool.main(["--dataset", str(folder), "--out", str(out),
                       "--streams", "events", "--J-frames", "2",
                       "--n-permutations", "39"])
    assert rc == 1                                   # unusable, and said so
    st = _report(out)["streams"]["events"]
    assert st["pairs_needed"] == 654
    assert st["n_pairs"] < st["pairs_needed"]
    assert st["power_at_n"] < st["declared_power"]
    assert "underpowered by arithmetic" in st["verdict"]
    assert st["positive_control"] is None            # nothing was spent
    assert st["negative_control"] is None


def test_with_the_flag_both_controls_run_and_are_reported_apart(pd_tool, folder,
                                                                tmp_path):
    """The flag is for probes, and a probe still has to say what it found: the positive
    and negative controls are separate results, and the verdict names which failed."""
    out = tmp_path / "ran"
    pd_tool.main(["--dataset", str(folder), "--out", str(out),
                  "--streams", "events", "--J-frames", "2",
                  "--n-permutations", "39", "--allow-underpowered"])
    st = _report(out)["streams"]["events"]
    assert st["positive_control"] is not None
    assert st["negative_control"] is not None
    assert 0.0 <= st["positive_control"]["accuracy"] <= 1.0
    # Real against real is exchangeable by construction (each pair's orientation is
    # drawn at random), so the machinery must not separate it from itself.
    assert st["negative_flagged"] is False
    # The tier is still underpowered here, and the verdict has to keep saying so rather
    # than let a passing control read as a clean bill.
    assert "underpowered" in st["verdict"]


def test_analysis_windows_are_a_duration_not_a_frame_count(pd_tool, folder):
    """Two recordings at different frame intervals get windows of the same seconds —
    the Cossart folder's frame interval varies 0.0926-0.1190 s across sessions, so a
    fixed frame count would cut windows of different lengths and the discriminator's
    features are counts."""
    from bugarach import surrogate_stats as ss
    from bugarach.io import load_folder

    recs, _ = ss.recordings_from_slices(load_folder(folder), "events")
    rec = recs[0]
    wins = pd_tool.analysis_windows(rec)
    assert wins, "a 900 s recording must hold whole 60 s windows"
    assert all(w[1] - w[0] == wins[0][1] - wins[0][0] for w in wins)
    assert (wins[0][1] - wins[0][0]) * rec.dt == pytest.approx(
        ss.ANALYSIS_WINDOW_SEC, abs=rec.dt)
    assert wins[-1][1] <= rec.window[1]               # no part-window at the end
