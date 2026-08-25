#!/usr/bin/env python3
"""How much does a sampled detector disagree with ITSELF on a different draw?

    python tools/sampling_floor.py <export folder> [--detectors coact,sce]

**The control `compare_routes.py` needs.** That tool found `rate` agreeing
1613/1613 between the browser and `bugarach detect` — exact, as a detector drawing
no random numbers must — while `coact` agreed on 1224 of 1376 and `sce` on 1681 of
1692. Calling the difference *"sampling error"* without measuring sampling error
is an assertion, not a finding.

So: run the same route twice, changing only the surrogate seed, and see how far a
detector lands from itself. That is the floor. A browser-vs-CLI disagreement at or
below it is sampling; one above it is a real divergence in the port and worth
chasing.

Same folder, same stream, same settings, same matching tolerance as the route
comparison, so the two numbers are directly comparable.
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

from compare_routes import MATCH_SEC, key_rows, pair_up


def run_at_seed(folder: Path, out: Path, detectors, stream: str,
                seed: int) -> Path:
    """One folder run with the surrogate seed overridden."""
    from bugarach import detect_folder as df

    out.mkdir(parents=True, exist_ok=True)
    original = df.detector_params

    def seeded(name: str, *, frame_interval_sec: float) -> dict:
        p = dict(original(name, frame_interval_sec=frame_interval_sec))
        # only the samplers carry one; the rest are untouched
        if "rng_seed" in p or name in ("coact", "sce", "loco", "cicada"):
            p["rng_seed"] = seed
        return p

    df.detector_params = seeded
    try:
        df.detect_folder(folder, out_dir=out, detectors=tuple(detectors),
                         stream=stream)
    finally:
        df.detector_params = original
    return out / "detections.csv"


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("folder", type=Path)
    p.add_argument("--detectors", default="coact,sce")
    p.add_argument("--stream", default="fast")
    p.add_argument("--seeds", default="20260706,20260707")
    p.add_argument("--out", default=None)
    a = p.parse_args()
    detectors = tuple(x.strip() for x in a.detectors.split(",") if x.strip())
    s1, s2 = (int(x) for x in a.seeds.split(","))

    from bugarach.paths import darkroom, unresolved_message
    dest = Path(a.out) if a.out else darkroom()
    if dest is None:
        print(unresolved_message(), file=sys.stderr)
        return 1
    root = dest / "two_routes" / "sampling_floor"

    print(f"same route, seed {s1}…")
    one = run_at_seed(a.folder, root / f"seed{s1}", detectors, a.stream, s1)
    print(f"same route, seed {s2}…")
    two = run_at_seed(a.folder, root / f"seed{s2}", detectors, a.stream, s2)

    A, B = key_rows(one), key_rows(two)
    print(f"\n{'detector':<10} {'seed A':>7} {'seed B':>7} {'agreed':>7} "
          f"{'A only':>7} {'B only':>7}  {'agreement':>9}")
    for det in sorted(detectors):
        ka = {k: v for k, v in A.items() if k[1] == det}
        kb = {k: v for k, v in B.items() if k[1] == det}
        na = nb = ag = ao = bo = 0
        for k in set(ka) | set(kb):
            x, y = ka.get(k, []), kb.get(k, [])
            na += len(x)
            nb += len(y)
            m, xo, yo = pair_up(x, y, MATCH_SEC)
            ag += m
            ao += len(xo)
            bo += len(yo)
        frac = ag / max(na, 1)
        print(f"{det:<10} {na:>7} {nb:>7} {ag:>7} {ao:>7} {bo:>7}  {frac:>8.1%}")
    print(f"\nmatching tolerance {MATCH_SEC:g} s — the same rule "
          "compare_routes.py uses, so the two are directly comparable.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
