#!/usr/bin/env python3
"""Is the co-participation departure optical crosstalk between neighbouring ROIs?

    python tools/assembly_pensub_compare.py \\
        --main   <out>/run_revised_2v_fast/assessment_real.json \\
        --pensub <out>/run_pensub_revised_2v_fast/assessment_real.json \\
        --k 3

**The alternative the nulls cannot remove.** Both nulls reshuffle a membership
table that has already been built. If two ROIs overlap optically, one cell's
calcium transient lands in both, and the pair co-participates in the table for a
reason that has nothing to do with the tissue. No reshuffle of that table can
undo it, because the artifact is in the table. The only way to answer it is to
rebuild the table from a store where the overlap was subtracted, and re-measure.

**Paired, on the recordings testable in both stores.** The marginal tallies are
not comparable: penumbra subtraction removes events, removing events removes
coactive clusters, and a recording that drops below the floor returns
``undefined`` rather than a negative. Comparing 49-of-85 against 28-of-85 would
read a *loss of power* as a *loss of signal* — the single most likely way to get
this question wrong. So the comparison here is over the intersection, one
recording contributing one pair.

Reads two ``assess_archive.py --assemblies`` assessments. Writes no store.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

FIRED = ("structure-beyond-rate", "uniform-only", "margin-only")


def rows_at(path: Path, k: int, stream: str | None) -> dict:
    """Assembly rows keyed by slice, at one coactivity floor K.

    **No exclusion argument.** Which recordings are analysable is the producer's
    call, expressed by what the export folder contains — see the note in
    ``bugarach.assembly``.
    """
    d = json.loads(Path(path).read_text())
    rows = d["rows"] if isinstance(d, dict) and "rows" in d else d
    out = {}
    for r in rows:
        if int(r.get("K", -1)) != int(k):
            continue
        if stream and r.get("stream") != stream:
            continue
        out[str(r.get("slice_id", ""))] = r
    return out


def _fired(r) -> bool:
    return r.get("asm_verdict") in FIRED


def compare(main: dict, pensub: dict) -> dict:
    """The paired cross-tab, plus an exact test on the discordant pairs."""
    shared = sorted(set(main) & set(pensub))
    both = [s for s in shared
            if main[s].get("asm_defined") and pensub[s].get("asm_defined")]

    tab = {}
    for s in both:
        key = (main[s]["asm_verdict"], pensub[s]["asm_verdict"])
        tab[key] = tab.get(key, 0) + 1

    # McNemar on fired/not-fired. The discordant cells are the whole test: pairs
    # that agree carry no information about a change.
    b = sum(1 for s in both if _fired(main[s]) and not _fired(pensub[s]))
    c = sum(1 for s in both if not _fired(main[s]) and _fired(pensub[s]))
    p = _binom_two_sided(b, b + c)

    # Recordings that were testable in main and STOPPED being testable. This is
    # the power the store costs, and it is reported separately from the verdict
    # so the two can never be confused.
    lost = [s for s in shared
            if main[s].get("asm_defined") and not pensub[s].get("asm_defined")]
    gained = [s for s in shared
              if not main[s].get("asm_defined") and pensub[s].get("asm_defined")]

    return {
        "n_shared": len(shared),
        "n_testable_main": sum(1 for s in shared if main[s].get("asm_defined")),
        "n_testable_pensub": sum(1 for s in shared if pensub[s].get("asm_defined")),
        "n_testable_both": len(both),
        "n_lost_testability": len(lost),
        "n_gained_testability": len(gained),
        "fired_main": sum(1 for s in both if _fired(main[s])),
        "fired_pensub": sum(1 for s in both if _fired(pensub[s])),
        "discordant_main_only": b,
        "discordant_pensub_only": c,
        "mcnemar_p": p,
        "crosstab": {f"{a} -> {bb}": n for (a, bb), n in sorted(tab.items())},
        "slices_lost_testability": lost,
    }


def _binom_two_sided(k: int, n: int, p: float = 0.5) -> float:
    """Exact two-sided binomial p. No SciPy — this repo does not depend on it."""
    if n == 0:
        return float("nan")
    from math import comb
    probs = [comb(n, i) * p ** i * (1 - p) ** (n - i) for i in range(n + 1)]
    obs = probs[k]
    return float(min(1.0, sum(q for q in probs if q <= obs * (1 + 1e-12))))


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--main", type=Path, required=True)
    ap.add_argument("--pensub", type=Path, required=True)
    ap.add_argument("--k", type=int, default=3)
    ap.add_argument("--stream", default=None)
    ap.add_argument("--json-out", type=Path, default=None)
    a = ap.parse_args(argv)

    m = rows_at(a.main, a.k, a.stream)
    p = rows_at(a.pensub, a.k, a.stream)
    res = compare(m, p)
    res["k"] = a.k
    res["stream"] = a.stream

    print(f"K={a.k}" + (f"  stream={a.stream}" if a.stream else ""))
    print(f"  shared recordings            {res['n_shared']}")
    print(f"  testable  main               {res['n_testable_main']}")
    print(f"  testable  penumbra-subtracted{res['n_testable_pensub']:>4}")
    print(f"  testable  BOTH (the pairs)   {res['n_testable_both']}")
    print(f"  lost testability             {res['n_lost_testability']}"
          f"   <- power the store costs, NOT a negative")
    print()
    print(f"  fired, main                  {res['fired_main']}/{res['n_testable_both']}")
    print(f"  fired, penumbra-subtracted   {res['fired_pensub']}/{res['n_testable_both']}")
    print(f"  discordant  main only {res['discordant_main_only']}"
          f"   pensub only {res['discordant_pensub_only']}"
          f"   McNemar p={res['mcnemar_p']:.3g}")
    print("\n  verdict transitions:")
    for k_, n in res["crosstab"].items():
        print(f"    {n:>3}  {k_}")
    if a.json_out:
        a.json_out.parent.mkdir(parents=True, exist_ok=True)
        a.json_out.write_text(json.dumps(res, indent=1))
        print(f"\nwrote {a.json_out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
