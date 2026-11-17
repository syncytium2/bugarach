"""Review A pages: the 3x-only match, the set names, and the page names."""
from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
import pytest

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / "tools"))

import make_review_a_pages as ra  # noqa: E402


def test_only_in_keeps_onsets_with_no_partner_within_the_tolerance():
    a = np.array([1.0, 2.0, 3.0, 10.0])
    b = np.array([1.0, 2.04, 3.2])
    assert ra.only_in(a, b).tolist() == [3.0, 10.0]


def test_only_in_with_an_empty_side():
    a = np.array([1.0, 2.0])
    assert ra.only_in(a, np.array([])).tolist() == [1.0, 2.0]
    assert ra.only_in(np.array([]), a).size == 0
    assert ra.only_in(a, np.array([2.0])).tolist() == [1.0]


def test_set_names_follow_the_bench_set_records():
    assert ra.set_name("fast", "di", "4x") == "fast_di"
    assert ra.set_name("combined", "male", "3x") == "combined_male_3x"
    records = {p.stem for p in (REPO / "docs/learned/bench_sets").glob("*.json")}
    for s in ra.STREAMS:
        for g in ra.GROUPS:
            for t in ra.THRS:
                assert ra.set_name(s, g, t) in records


@pytest.mark.parametrize("stream", ra.STREAMS)
def test_page_names_pass_the_estate_scheme(stream):
    from naming import artifact_name

    name = ra.page_name(stream, "di", "20261117")
    assert name == f"raster_roi_{stream}_baseline_di_win20min_thr3x_20261117.html"
    assert artifact_name.check(artifact_name.load_codes(), name) is True
