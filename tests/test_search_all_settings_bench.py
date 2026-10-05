"""``tools/search_all_settings.py --bench slow`` searches the slow bench, in every stage.

The search reads its bench in five places, four of them inside worker processes. A run that
chose on slow recordings and held out on fast ones would look like any other run, so these
check the seam rather than trust it (``docs/handoffs/2026-09-21-slow-bench.md``, *Nothing a slow run writes
may land on a fast result*).
"""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

from bugarach import bench, bench_slow

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / "tools"))

import search_all_settings as sas  # noqa: E402


@pytest.fixture
def restore(monkeypatch):
    monkeypatch.delenv(sas.BENCH_ENV, raising=False)
    yield
    sas.use_bench("fast")
    monkeypatch.delenv(sas.BENCH_ENV, raising=False)


def test_the_default_is_the_fast_bench(restore):
    assert sas._load_bench() is bench


def test_use_bench_slow_rebinds_the_module_and_what_workers_will_read(restore):
    import os

    b = sas.use_bench("slow")
    assert b is bench_slow and sas._bench is bench_slow
    assert os.environ[sas.BENCH_ENV] == "bugarach.bench_slow"
    # What a worker process does on import, and in _job / held_out / make_admissible:
    assert sas._load_bench() is bench_slow
    assert sas.SPACE["coact"]["int_win_sec"] == list(bench_slow.FULL_GRIDS["coact"]["int_win_sec"])
    assert sas.shipped_value("coact", "alpha") == bench_slow.OPERATING_POINTS["coact"].params["alpha"]


def test_use_bench_fast_undoes_it(restore):
    sas.use_bench("slow")
    assert sas.use_bench("fast") is bench
    assert sas.SPACE["coact"]["int_win_sec"] == list(bench.FULL_GRIDS["coact"]["int_win_sec"])


def test_a_stray_bench_name_is_refused(restore, monkeypatch):
    monkeypatch.setenv(sas.BENCH_ENV, "bugarach.somewhere_else")
    with pytest.raises(ValueError, match="not one of"):
        sas._load_bench()


def test_the_slow_grids_walk_the_fast_axes_and_every_fast_value():
    assert set(bench_slow.FULL_GRIDS) == set(bench.FULL_GRIDS)
    for d, axes in bench.FULL_GRIDS.items():
        assert set(bench_slow.FULL_GRIDS[d]) == set(axes), d
        for k, v in axes.items():
            assert set(v) <= set(bench_slow.FULL_GRIDS[d][k]), (d, k)


def test_the_slow_grids_add_nothing_the_null_rule_would_refuse():
    for d, axes in bench_slow.SLOW_EXTRA.items():
        assert not any(k.startswith("context") for k in axes), d
