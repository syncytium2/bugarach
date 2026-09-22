"""The slow stream's measurement is its own record, of the slow stream, on the default folder.

The sibling of ``test_bench_is_measured_on_the_declared_folder.py`` that
``docs/handoffs/2026-09-21-slow-bench.md`` asks for. Tony, 2026-09-21: nothing a slow run writes may land on
a fast result. So these tests read only the committed record and the pointer — no data on
the machine — and turn red when:

* the slow tool's record path is the fast bench's, so a slow run would overwrite it;
* the record is of any stream but ``slow``;
* the default folder moved and the slow stream was not re-measured on it;
* the width table cannot be handed to the simulator (wrong length, not monotone).
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

from bugarach import bench, dataset
from bugarach.simulate import MEASURED_WIDTH_QUANTILE_LEVELS

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / "tools"))

import measure_slow_bench as msb  # noqa: E402


def _record() -> dict:
    return json.loads((REPO / msb.RECORD).read_text(encoding="utf-8"))


def test_the_slow_record_is_not_the_fast_record():
    assert Path(msb.RECORD) != Path(bench.MEASURED_RECORD)
    assert msb.STREAM == "slow"


def test_the_record_is_of_the_slow_stream():
    assert _record()["stream"] == "slow"


def test_the_record_was_measured_on_the_folder_the_pointer_declares_today():
    rec = _record()
    assert rec["dataset"]["role"] == dataset.default_role()
    assert rec["dataset"]["name"] == dataset.current_name(), (
        "the default folder moved since the slow stream was measured: rerun "
        "tools/measure_slow_bench.py")


def test_the_width_table_fits_the_simulators_levels():
    wq = _record()["width_quantiles"]
    assert len(wq) == len(MEASURED_WIDTH_QUANTILE_LEVELS)
    assert all(a <= b for a, b in zip(wq, wq[1:]))
    assert wq[0] > 0


def test_every_bin_the_record_claims_was_measured():
    rec = _record()
    for b in rec["bins_sec"]:
        assert f"jitter_sec@{b:g}s" in rec["values"]
        assert f"participation@{b:g}s" in rec["values"]
