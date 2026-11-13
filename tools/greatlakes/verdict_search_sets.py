#!/usr/bin/env python3
"""Open each set's search output and say whether it is a result.

    python tools/greatlakes/verdict_search_sets.py --out <run folder> --sets fast_di fast_male

Writes ``<run folder>/run_record/VERDICT_set_searches.txt``. Per set, one of:

* ``PASS``: ``search.json`` is there, finished, on that set's bench, and every detector has a
  shipped row and at least one candidate with a finite held-out score;
* ``FAIL``: the search ended and its output is not that;
* ``FAILED-TO-RUN``: there is no finished ``search.json``.

The first line is the run's verdict: ``PASS`` only when every set passed. A job that exits 0
has said nothing about its output (docs/greatlakes/README.md, rule 1), so this reads the file.
Exits 0 whatever it finds; the verdict is the file.
"""
from __future__ import annotations

import argparse
import datetime
import json
import math
from pathlib import Path

PASS, FAIL, NOT_RUN = "PASS", "FAIL", "FAILED-TO-RUN"


def verdict(folder: Path, name: str) -> tuple[str, str]:
    path = folder / name / "search.json"
    if not path.exists():
        return NOT_RUN, "no search.json"
    try:
        s = json.loads(path.read_text(encoding="utf-8"))
    except ValueError as exc:
        return NOT_RUN, f"search.json does not parse ({exc})"
    if not s.get("finished"):
        return NOT_RUN, f"search.json has no finish time (stage: {s.get('stage')})"
    bench = str(s.get("bench", ""))
    if not bench.endswith("." + name):
        return FAIL, f"searched {bench!r}, not this set"
    held = s.get("held_out") or {}
    if not held:
        return FAIL, "no held-out scores"
    bad = []
    for det, rows in held.items():
        f1 = [r.get("mean_f1") for r in rows.values()]
        if "shipped" not in rows or not any(
                isinstance(v, (int, float)) and math.isfinite(v) for v in f1):
            bad.append(det)
    if bad:
        return FAIL, f"no finite held-out score for: {', '.join(sorted(bad))}"
    best = {det: max(r["mean_f1"] for r in rows.values()
                     if isinstance(r.get("mean_f1"), (int, float)) and math.isfinite(r["mean_f1"]))
            for det, rows in held.items()}
    return PASS, (f"{len(held)} detectors, {s.get('evaluations')} evaluations, "
                  f"{s.get('elapsed_min')} min, best held-out mean F1 "
                  f"{min(best.values()):.3f} to {max(best.values()):.3f}")


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--out", type=Path, required=True)
    ap.add_argument("--sets", nargs="+", required=True)
    a = ap.parse_args(argv)
    rows = [(name, *verdict(a.out, name)) for name in a.sets]
    overall = (PASS if all(v == PASS for _, v, _ in rows)
               else NOT_RUN if all(v == NOT_RUN for _, v, _ in rows) else FAIL)
    lines = [f"VERDICT: {overall}",
             f"{sum(v == PASS for _, v, _ in rows)} of {len(rows)} sets passed; "
             f"written {datetime.datetime.now().isoformat(timespec='seconds')}"]
    lines += [f"{name:16s} {v:14s} {why}" for name, v, why in rows]
    text = "\n".join(lines) + "\n"
    (a.out / "run_record").mkdir(parents=True, exist_ok=True)
    (a.out / "run_record" / "VERDICT_set_searches.txt").write_text(text, encoding="utf-8")
    print(text, end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
