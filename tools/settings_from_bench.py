#!/usr/bin/env python3
"""A bench module's operating points, as a settings file ``bugarach detect --settings`` runs at.

    python tools/settings_from_bench.py --bench combined --out <dir>/combined_settings.csv
    python tools/settings_from_bench.py --bench slow --stream slow --out <dir>/slow_settings.csv

**Why.** A stream's parameter set lives in its bench module's ``OPERATING_POINTS``
(``bench_slow``, ``bench_combined``) and reaches real recordings only as ``stream=<name>`` rows of
a settings file (``docs/handoffs/2026-09-21-slow-bench.md``); only the fast set ships through
``bench.OPERATING_POINTS``. The slow file was written by hand. This writes it from the module, so
the parameters that ran on real data are the ones the search chose and nothing was retyped.

Each detector also gets a ``fitted_on`` row naming the module, which ``detect_folder.load_settings``
carries into ``run.json`` as provenance rather than passing to the detector.

The file lands where ``--out`` says: it is an input to a run, claimed with that run's folder.
"""
from __future__ import annotations

import argparse
import importlib
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
if str(REPO / "src") not in sys.path:
    sys.path.insert(0, str(REPO / "src"))

BENCHES = {"fast": "bugarach.bench", "slow": "bugarach.bench_slow",
           "combined": "bugarach.bench_combined"}


def settings_of(module_name: str, stream: str) -> dict[tuple[str, str], dict]:
    """``{(detector, stream): params}`` from a bench module, with its provenance row."""
    b = importlib.import_module(module_name)
    out = {}
    for det, op in b.OPERATING_POINTS.items():
        params = dict(op.params)
        params["fitted_on"] = f"{module_name}.OPERATING_POINTS"
        out[(det, stream)] = params
    return out


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--bench", choices=sorted(BENCHES), required=True)
    ap.add_argument("--stream", default=None,
                    help="the stream column's value (default: the bench's own name)")
    ap.add_argument("--out", type=Path, required=True)
    a = ap.parse_args(argv)

    from bugarach.detect_folder import load_settings
    from bugarach.emit import write_detector_settings

    stream = a.stream or a.bench
    a.out.parent.mkdir(parents=True, exist_ok=True)
    write_detector_settings(settings_of(BENCHES[a.bench], stream), a.out)
    params, _ = load_settings(a.out)          # refuses anything detect would refuse, now
    print(f"wrote {a.out}: {len(params)} detector(s) at {BENCHES[a.bench]}, stream={stream}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
