"""The 2026-09-22 run on 84 recordings against this one on 66, group by group.

    python docs/learned/runs/2026-09-23-jitter-by-group-66/compare_84_vs_66.py

Prints the markdown table the README carries. The two folders' recording files are
byte-identical (sha256) on the 66 recordings they share — the producer checked it and
`current_export.toml`'s `senktide_ttx` note records it — so nothing here differs because of
event derivation. What differs is the recording set: the 66 keeps only the senktide- and
TTX-first recordings, which takes MALE from 22 to 13, ORX from 25 to 19, OVX from 20 to 17 and
leaves DI at 17.

Two quantities per group, because Figure 1's normalised panels show neither on its own:

* the **half-width at half height** (s), the width statistic; and
* the **zero-lag peak height**, the excess coincidence at lag 0 — observed ÷ expected onset
  pairs − 1, dimensionless, where 0 means no more pairs than the ROIs' own rates predict.

Groups are listed in ``bugarach.groups.GROUP_ORDER`` (DI, OVX, MALE, ORX).
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[3]
sys.path.insert(0, str(REPO / "src"))

from bugarach.groups import GROUP_ORDER  # noqa: E402

OLD = REPO / "docs/learned/runs/2026-09-22-jitter-by-group/jitter_correlogram.json"


def row(rec, stream, group):
    """(recordings, half-width s, zero-lag excess) for one group, or None if absent."""
    st = rec["streams"][stream]
    g = st["groups"].get(group)
    if not g:
        return None
    return g["recordings"], g["hwhm"]["real_sec"], g["real_excess"][0]


def pooled_row(rec, stream):
    st = rec["streams"][stream]
    return st["recordings"], st["hwhm"]["real_sec"], st["real_excess"][0]


def table(old, new) -> str:
    out = ["| stream | group | recordings | half-width (s) | zero-lag peak (excess coincidence) |",
           "|---|---|---:|---:|---:|"]
    for stream in ("fast", "slow"):
        for group in (*GROUP_ORDER, None):
            a = pooled_row(old, stream) if group is None else row(old, stream, group)
            b = pooled_row(new, stream) if group is None else row(new, stream, group)
            if a is None and b is None:
                continue
            name = "**pooled**" if group is None else group
            cells = [f"{a[0]} → {b[0]}" if a and b else "—",
                     f"{a[1]:.3f} → {b[1]:.3f}" if a and b else "—",
                     f"{a[2]:.1f} → {b[2]:.1f}" if a and b else "—"]
            out.append(f"| {stream} | {name} | " + " | ".join(cells) + " |")
    return "\n".join(out)


def verdicts(old, new) -> str:
    lines = []
    for stream in ("fast", "slow"):
        for label, rec in (("84", old), ("66", new)):
            c = rec["streams"][stream]["contrasts"]["hwhm"]
            w = c["without_most_influential"]
            lines.append(f"* **{stream}, {label} recordings** — spread {c['spread_sec']:.3f} s, "
                         f"p = {c['permutation']['p_any_difference']:.3f}; without "
                         f"{w['slice_id']}, spread {w['spread_sec']:.3f} s, "
                         f"p = {w['p_any_difference']:.3f}.")
        loo = new["streams"][stream]["groups"].get("ORX", {}).get("hwhm", {}).get("leave_one_out")
        if loo:
            lines.append(f"* **{stream}, ORX's biggest mover on the 66** — {loo['slice_id']}: "
                         f"{loo['delta_sec']:+.3f} s without it.")
    return "\n".join(lines)


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--old", type=Path, default=OLD, help="the 84-recording record")
    ap.add_argument("--new", type=Path, default=HERE / "jitter_correlogram.json")
    a = ap.parse_args(argv)
    old = json.loads(a.old.read_text(encoding="utf-8"))
    new = json.loads(a.new.read_text(encoding="utf-8"))
    print(f"84: {old['dataset']['name']}\n66: {new['dataset']['name']}\n")
    print(table(old, new))
    print()
    print(verdicts(old, new))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
