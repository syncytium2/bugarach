"""The separation axis (ADR-0022) plants close events on every stream and scores the map's four.

A smoke test of ``tools/measure_separation_axis.py``: one recording, checked for the properties
the run record's claims rest on.
"""
from __future__ import annotations

import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))

import measure_separation_axis as msa  # noqa: E402

from bugarach import bench  # noqa: E402
from bugarach import stream_profile as sp  # noqa: E402


@pytest.fixture(autouse=True)
def realistic_spacing(monkeypatch):
    monkeypatch.setenv(bench.SPACING_ENV, "realistic")


def test_the_axis_goes_below_two_seconds():
    assert min(msa.SEPARATIONS_SEC) < 2.0, "ADR-0022 decision 2: the axis goes below 2 s"


def test_the_detectors_are_the_first_maps_four_and_every_stream_has_them():
    assert set(msa.DETECTORS) == {"coact", "loco", "sce", "count_sliding"}      # ADR-0021
    for stream in sp.STREAMS:
        assert set(msa.DETECTORS) <= set(sp.profile(stream).detectors)


@pytest.mark.parametrize("stream", sp.STREAMS)
def test_a_recording_holds_close_events_at_the_separation_and_no_decoys(stream):
    row = msa.task((stream, 1.0, "baseline_quiet", msa.FRESH_SEED))
    assert row["n_close_gaps"] >= 1, "no gap was set to the separation"
    assert set(row["det"]) == set(msa.DETECTORS)
    for counts in row["det"].values():
        assert len(counts) == len(msa.FIELDS)
    from bugarach import real_intervals as ri
    _, gt = sp.profile(stream).simulate(
        "baseline_quiet", msa.FRESH_SEED, gap_source=ri.as_gap_distribution([1.0]),
        gap_mix=1.0 - msa.CLOSE_SHARE, n_distractors=0)
    assert not list(gt.distractors), "ADR-0019: the axis plants no decoys"


def test_the_figures_name_comes_from_the_naming_tool():
    name = msa.figure_name()
    assert name.startswith("synth_recovery_plot_separation-axis-recall_") and name.endswith(".png")
