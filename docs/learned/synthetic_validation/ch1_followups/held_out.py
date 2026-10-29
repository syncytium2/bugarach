"""Task 2 (murderboard 2026-10-29, role 4): the Aim 1a grid again on FRESH seeds, and theory.check()
against it, hard-core form and general form (generator's empirical event train).

The theory's model choices were made looking at aim1_one_source.json. This reruns the same grid
(same jitters, participation, event counts, backgrounds, 5 recordings per condition, 33 cells,
45 min, same tools and settings) through aim1_one_source.py's own `cell` and `chance_cell`, with
only the seeds moved:

* recordings: `cell` seeds the generator 1000 + 100 * idx + seed and the surrogates
  7 + 100 * idx + seed, where idx enters nowhere else. Passing idx + 1000 gives generator seeds
  101000 + 100 * idx + seed (101000-105704) and surrogate seeds 100007-104711, disjoint from the
  original's 1000-5704 and 7-4711. The row's `cell` field is set back to idx.
* background-only arm: `chance_cell` seeds 900000 + 1000 * round(1000 b) + seed; seeds 100-199
  here, against 0-99 in the original.

theory.check() writes into its module's HERE, so HERE is pointed at this folder while it runs; the
original theory_check*.json files are not touched.

    PYTHONPATH=src python docs/learned/synthetic_validation/ch1_followups/held_out.py --workers 40
    ... held_out.py --checks-only      # rerun the two checks on the existing held-out record
    ... held_out.py --summary-only     # theory.summary() / general_summary() of both held-out
                                       # check records (held_out_summary.txt is this printout)
"""
from __future__ import annotations

import argparse
import itertools
import json
import shutil
import sys
import time
from concurrent.futures import ProcessPoolExecutor
from pathlib import Path

HERE = Path(__file__).resolve().parent
SV = HERE.parent
sys.path.insert(0, str(SV))
import aim1_one_source as a1  # noqa: E402

IDX_OFFSET = 1000
CHANCE_SEEDS = range(100, 200)
RECORD = HERE / "aim1_one_source_heldout.json"


def cell_fresh(args):
    idx, params = args
    row = a1.cell((idx + IDX_OFFSET, params))
    row["cell"] = idx
    return row


def run(workers: int) -> None:
    cells = list(itertools.product(a1.JITTERS, a1.PARTS, a1.N_EVENTS, a1.BG_RATES))
    grid = [(i, (*c, s)) for i, c in enumerate(cells) for s in a1.SEEDS]
    t0 = time.time()
    with ProcessPoolExecutor(workers) as ex:
        rows = list(ex.map(cell_fresh, grid))
        chance = list(ex.map(a1.chance_cell, list(itertools.product(a1.BG_RATES, CHANCE_SEEDS))))
    print(f"{len(rows)} recordings + {len(chance)} background-only in {time.time() - t0:.0f} s",
          file=sys.stderr)
    rec = dict(what="Aim 1a, HELD-OUT rerun on fresh seeds (ch1_followups/held_out.py)",
               seeding=f"per recording: 1000 + 100 * (condition index + {IDX_OFFSET}) + seed; "
                       f"surrogates 7 + 100 * (condition index + {IDX_OFFSET}) + seed; "
                       f"background-only seeds {CHANCE_SEEDS.start}-{CHANCE_SEEDS.stop - 1}",
               assessor_settings="as aim1_one_source.json",
               n_roi=a1.N_ROI, duration_sec=a1.DURATION, min_sep_sec=a1.MIN_SEP, ks=a1.KS,
               quick=False, rows=rows, chance_arm=chance)
    RECORD.write_text(json.dumps(rec, indent=1, default=float))
    print(RECORD, file=sys.stderr)


def checks() -> None:
    import theory
    theory.HERE = HERE
    for train, src, dst in ((None, "theory_check.json", "theory_check_heldout.json"),
                            ("empirical", "theory_check_empirical.json",
                             "theory_check_heldout_empirical.json")):
        t0 = time.time()
        theory.check(path=RECORD, train=train)
        shutil.move(HERE / src, HERE / dst)
        print(f"{dst} in {time.time() - t0:.0f} s", file=sys.stderr)


def summaries() -> None:
    import theory
    print("=== HELD-OUT, hard-core form: theory.summary(theory_check_heldout.json)")
    theory.summary(json.loads((HERE / "theory_check_heldout.json").read_text()))
    print("\n=== HELD-OUT, general form (empirical train): theory.summary + general_summary")
    g = json.loads((HERE / "theory_check_heldout_empirical.json").read_text())
    theory.summary(g)
    theory.general_summary(g)


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--workers", type=int, default=40)
    ap.add_argument("--checks-only", action="store_true")
    ap.add_argument("--summary-only", action="store_true")
    a = ap.parse_args()
    if not a.summary_only:
        if not a.checks_only:
            run(a.workers)
        checks()
    summaries()
