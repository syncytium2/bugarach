#!/usr/bin/env python3
"""The operating-point campaign, which this repo could describe but not run.

`RESET.md` §7 step 5 is *"then the re-fit"*, and until now nothing here walked
one. The pieces were all present and unassembled: :func:`bugarach.bench.sweep`
builds one detector's curve over one regime, and
:func:`bugarach.bench.pick_operating_point` chooses a point on one curve and
already refuses three ways — a grid that never bracketed the optimum
(``EdgeOfRange``), a knob that did nothing (``DegenerateSweep``), and a winner
that got there by firing where nothing was planted (``TooPromiscuous``). What was
missing is the loop over every detector × regime, and somewhere to put the answer.

**This proposes; it does not adopt.** Nothing here writes
:data:`~bugarach.bench.OPERATING_POINTS`. The output is a candidate record — for
each detector and regime, the point the campaign would choose, what the shipped
setting is, and whether the two differ — for a person to read and decide on. An
operating point is what every published number in this project is computed at, so
moving one silently would invalidate the lot; ``docs/learned/`` regeneration is a
separate pass and RESET §7 puts it in the same step deliberately.

**What this campaign cannot see, stated because a silent limit reads as coverage.**

- **Only the knob each detector declares.** ``OPERATING_POINTS[name].knob`` is one
  parameter; every other parameter is held at its shipped value. So this is a
  one-dimensional re-fit, and a mechanism whose parameter is not the declared knob
  cannot be found by it — the guard is the live example, since ``guard_sec`` is not
  on coact's axis (root ``HANDOFF.md``, *"a decision, not a task"*).
- **Only the two baseline regimes.** ``REGIMES`` is ``baseline_quiet`` and
  ``baseline_busy``, both derived from untreated recordings, which is what
  FOUNDATIONS §9 requires. Both plant events ≥120 s apart against a ±30 s
  reference window, so **measured crowding is 0.00 on both** and any mechanism
  that acts on mutual masking cannot fire in this campaign at all. A flat result
  here is not evidence that such a mechanism does nothing.
- **The bench recording, not a folder.** ``bench.py``'s hardcoded recording reads
  no external file. This is the first of the three things RESET §10 says must be
  named apart.

Usage::

    python tools/refit.py                      # all six, both regimes
    python tools/refit.py --detectors rate sce --seeds 1 2 3 4 5
    python tools/refit.py --quick              # every other grid point, 1 seed

Writes ``refit_candidates.json`` to the darkroom by default (the place a person
opens), ``--also`` for a copy in the repo (what review and git history need).
"""
from __future__ import annotations

import argparse
import json
import os
import platform
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "src"))

from bugarach.bench import (  # noqa: E402
    DETECTORS,
    MAX_PROBE_PER_MIN,
    OPERATING_POINTS,
    REGIMES,
    DegenerateSweep,
    EdgeOfRange,
    TooPromiscuous,
    pick_operating_point,
    sweep,
)
from bugarach.paths import darkroom, unresolved_message  # noqa: E402


def _machine() -> dict:
    """What produced these numbers, recorded rather than assumed.

    ``tube_ablation.json`` carries no such block and its own todo calls that the
    defect: a store whose thread count is unrecorded cannot say whether a later
    run disagreeing with it disagrees about the detector or about the machine.
    Threads are **recorded, not pinned** — the six here are numpy and their F1
    does not depend on the count, but their timings do, and claiming a pin this
    does not perform would be worse than either.
    """
    return {
        "platform": platform.platform(),
        "python": platform.python_version(),
        "threads": {v: os.environ.get(v) for v in
                    ("OMP_NUM_THREADS", "MKL_NUM_THREADS",
                     "OPENBLAS_NUM_THREADS")},
    }


def _point(r) -> dict:
    """One row of a curve, with the probe's own number beside the headline."""
    return {
        "knob_value": r.knob_value,
        "f1": r.f1, "recall": r.recall, "precision": r.precision,
        "n_hit": r.n_hit, "n_planted": r.n_planted,
        "n_detected": r.n_detected, "n_fa": r.n_fa,
        "hot_fa": r.hot_fa, "hot_fa_per_min": r.hot_fa_per_min,
    }


def refit_one(name: str, regime: str, seeds: tuple[int, ...],
              values=None) -> dict:
    """Sweep one detector on one regime and record what selection did with it.

    A refusal is an **outcome, not a crash**: the three exceptions are the
    campaign's actual findings about a grid, and a driver that stops at the first
    one reports the first detector instead of the six. Each is caught, named, and
    the curve kept, so the row says which refusal and at which value.
    """
    op = OPERATING_POINTS[name]
    t0 = time.perf_counter()
    curve = sweep(name, regime, seeds, values=values)
    elapsed = time.perf_counter() - t0

    row: dict = {
        "detector": name, "regime": regime, "seeds": list(seeds),
        "knob": op.knob,
        "grid": [p.knob_value for p in curve],
        "shipped": op.params.get(op.knob),
        "probe_ceiling": MAX_PROBE_PER_MIN.get(name),
        "curve": [_point(p) for p in curve],
        "sweep_sec": round(elapsed, 2),
    }

    best_f1 = max((p for p in curve if p.f1 == p.f1), key=lambda p: p.f1,
                  default=None)
    row["argmax_f1"] = None if best_f1 is None else _point(best_f1)

    try:
        chosen = pick_operating_point(curve)
    except (EdgeOfRange, DegenerateSweep, TooPromiscuous) as exc:
        row["verdict"] = type(exc).__name__
        row["reason"] = str(exc)
        row["chosen"] = None
        row["moves"] = None
        return row

    row["verdict"] = "chosen"
    row["reason"] = None
    row["chosen"] = _point(chosen)
    shipped = row["shipped"]
    row["moves"] = (shipped is None or chosen.knob_value != shipped)
    return row


def summarise(rows: list[dict], *, quick: bool = False) -> str:
    """The table a person reads, and it leads with what would change.

    ``quick`` is carried into the text rather than only into the JSON, because a
    decimated grid **manufactures refusals**: ``--quick`` takes every other value,
    so an optimum that a full grid brackets can land at the end of the halved one
    and come back ``EdgeOfRange``. A smoke test whose output is indistinguishable
    from a campaign is how a decimation gets quoted as a finding.
    """
    w = max(len(r["detector"]) for r in rows) if rows else 8
    out = [f"{'detector':<{w}}  {'regime':<15}  {'verdict':<16} "
           f"{'shipped':>10} {'chosen':>10} {'F1':>6} {'probe/min':>10}"]
    for r in rows:
        ch = r["chosen"]
        chosen = "—" if ch is None else f"{ch['knob_value']:g}"
        f1 = "—" if ch is None else f"{ch['f1']:.3f}"
        probe = "—" if ch is None else f"{ch['hot_fa_per_min']:.1f}"
        shipped = "—" if r["shipped"] is None else f"{r['shipped']:g}"
        flag = " *" if r.get("moves") else ""
        out.append(f"{r['detector']:<{w}}  {r['regime']:<15}  "
                   f"{r['verdict']:<16} {shipped:>10} {chosen:>10} {f1:>6} "
                   f"{probe:>10}{flag}")

    moved = [r for r in rows if r.get("moves")]
    refused = [r for r in rows if r["chosen"] is None]
    out.append("")
    out.append(f"{len(moved)} of {len(rows)} would move (*), "
               f"{len(refused)} refused by selection.")
    for r in refused:
        out.append(f"  {r['detector']}/{r['regime']}: {r['verdict']} — "
                   f"{r['reason'].splitlines()[0]}")
    out.append("")
    if quick:
        out.append("!! --quick: every other grid value, one seed. A halved grid "
                   "can put an optimum at its end, so an EdgeOfRange here may "
                   "be the decimation rather than the detector. Smoke test; not "
                   "a campaign, and not quotable as one.")
        out.append("")
    out.append("Nothing here is adopted. OPERATING_POINTS is unchanged; this is "
               "a candidate record for a person to decide on.")
    return "\n".join(out)


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    p.add_argument("--detectors", nargs="+", default=list(DETECTORS),
                   help="default: all six")
    p.add_argument("--regimes", nargs="+", default=list(REGIMES),
                   help="default: both baseline regimes")
    p.add_argument("--seeds", nargs="+", type=int, default=[1, 2, 3])
    p.add_argument("--quick", action="store_true",
                   help="every other grid point, one seed — a smoke test, not a "
                        "campaign; the record says so in its own header")
    # default=None, never required: a deliverable's destination falls back to the
    # darkroom (sapper SAP006's lesson, and the report that never reached Tony).
    p.add_argument("--out", type=Path, default=None,
                   help="directory for the record (default: the darkroom)")
    p.add_argument("--also", type=Path, default=None,
                   help="extra copy, e.g. docs/learned — review and git history "
                        "need the repo copy; a person opens the darkroom one")
    args = p.parse_args()

    unknown = [d for d in args.detectors if d not in OPERATING_POINTS]
    if unknown:
        p.error(f"unknown detector(s) {unknown} — have {sorted(OPERATING_POINTS)}")
    bad_regimes = [r for r in args.regimes if r not in REGIMES]
    if bad_regimes:
        p.error(f"unknown regime(s) {bad_regimes} — have {sorted(REGIMES)}")

    seeds = tuple(args.seeds[:1] if args.quick else args.seeds)
    rows = []
    for det in args.detectors:
        op = OPERATING_POINTS[det]
        values = op.grid[::2] if args.quick else None
        for regime in args.regimes:
            print(f"  {det}/{regime} …", flush=True)
            rows.append(refit_one(det, regime, seeds, values=values))

    record = {
        "what": "operating-point candidates — RESET §7 step 5, proposed not adopted",
        "quick": bool(args.quick),
        "machine": _machine(),
        "rows": rows,
    }
    text = summarise(rows, quick=args.quick)
    print()
    print(text)

    out = args.out or darkroom(create=True)
    if out is None:
        print(unresolved_message("--out DIR"), file=sys.stderr)
        return 2
    dests = [Path(out)] + ([Path(args.also)] if args.also else [])
    for d in dests:
        d.mkdir(parents=True, exist_ok=True)
        (d / "refit_candidates.json").write_text(
            json.dumps(record, indent=1), encoding="utf-8")
        (d / "refit_candidates.txt").write_text(text + "\n", encoding="utf-8")
        print(f"wrote {d / 'refit_candidates.json'}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
