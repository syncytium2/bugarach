"""The bench's measured values were last checked on the folder the pointer declares today.

Tony, 2026-09-17, on finding that the bench's background had been fitted on a closed
`.mat` archive rather than on `steps_excluded`: *"not sure how to keep an eye on
that."* Provenance written as prose had not kept an eye on it. These tests do, with no
data on the machine: they read `bench.MEASURED_RECORD` (written by
`tools/remeasure_bench.py` when it last measured the folder) and compare it with
`current_export.toml` and with the constants in `bench.py`.

What turns them red:

* the pointer names a different folder for `bench.MEASURED_ROLE` than the one last
  measured (a new export arrived, and the bench was not re-measured on it);
* a measured constant in `bench.py` was edited without re-measuring;
* a constant sits outside its bootstrap interval and nobody has recorded why.
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from bugarach import bench, dataset

REPO = Path(__file__).resolve().parents[1]


def _record() -> dict:
    return json.loads((REPO / bench.MEASURED_RECORD).read_text(encoding="utf-8"))


def problems(record: dict, declared_folder: str, constants: dict, acknowledged: dict) -> list[str]:
    """Every way the record, the pointer and the bench disagree. Empty means agreement."""
    out = []
    if record["role"] != bench.MEASURED_ROLE:
        out.append(f"record measured role {record['role']!r}, bench declares {bench.MEASURED_ROLE!r}")
    if record["folder"] != declared_folder:
        out.append(f"record measured folder {record['folder']!r}, but current_export.toml now "
                   f"declares {declared_folder!r} for {record['role']!r}: re-run "
                   f"tools/remeasure_bench.py")
    if record["stream"] != bench.MEASURED_STREAM:
        out.append(f"record measured stream {record['stream']!r}, bench declares "
                   f"{bench.MEASURED_STREAM!r}")
    if set(record["values"]) != set(constants):
        out.append(f"record measured {sorted(record['values'])}, bench.measured_constants() "
                   f"lists {sorted(constants)}: re-run tools/remeasure_bench.py")
    for k, v in constants.items():
        row = record["values"].get(k)
        if row is None:
            continue
        if row["bench"] != pytest.approx(v, rel=1e-12, abs=1e-12):
            out.append(f"{k}: bench.py holds {v}, but the record checked {row['bench']}: "
                       f"a constant changed without re-measuring")
        if not row["inside"] and k not in acknowledged:
            out.append(f"{k}: bench {row['bench']} is outside the folder's 95% interval "
                       f"[{row['lo']:.4f}, {row['hi']:.4f}] and no reason is recorded in "
                       f"bench.MEASURED_OUTSIDE_INTERVAL")
    for k in acknowledged:
        row = record["values"].get(k)
        if row is not None and row["inside"]:
            out.append(f"{k}: listed in bench.MEASURED_OUTSIDE_INTERVAL but now inside its "
                       f"interval: remove the entry")
    return out


def test_the_bench_agrees_with_its_last_measurement_and_the_pointer():
    found = problems(_record(), dataset.current_name(bench.MEASURED_ROLE),
                     bench.measured_constants(), bench.MEASURED_OUTSIDE_INTERVAL)
    assert not found, "\n".join(found)


def test_the_program_reads_steps_excluded_fast():
    """The current program's decisions 1 and 4 (docs/goals/README.md)."""
    assert bench.MEASURED_ROLE == "steps_excluded"
    assert bench.MEASURED_STREAM == "fast"


def test_the_check_fires_on_each_kind_of_disagreement():
    """A check that cannot fail is not a check: plant each disagreement once."""
    rec = _record()
    folder = rec["folder"]
    consts = {k: row["bench"] for k, row in rec["values"].items()}
    ack = {k: "" for k, row in rec["values"].items() if not row["inside"]}
    assert problems(rec, folder, consts, ack) == []

    assert any("re-run" in p for p in problems(rec, folder + "_NEWER", consts, ack))

    edited = dict(consts)
    k0 = next(iter(edited))
    edited[k0] = edited[k0] * 1.5
    assert any("changed without re-measuring" in p for p in problems(rec, folder, edited, ack))

    outside = json.loads(json.dumps(rec))
    k1 = next(k for k in outside["values"] if k not in ack)
    outside["values"][k1]["inside"] = False
    assert any("no reason is recorded" in p for p in problems(outside, folder, consts, ack))

    stale = json.loads(json.dumps(rec))
    stale["values"][k1]["inside"] = True
    assert any("remove the entry" in p for p in problems(stale, folder, consts, {**ack, k1: ""}))
