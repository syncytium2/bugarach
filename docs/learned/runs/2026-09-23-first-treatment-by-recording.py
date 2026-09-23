"""Every recording's group, first treatment and full region order, from the export's own tables.

Replaces asking a calls table which recordings are in a set: a calls table has a row only where
a detector called, so a treatment window that worked contributes nothing and the recording
silently leaves the list. See the 2026-09-23 note on silent regions.

Read-only. Nothing is filtered and no label is rewritten.
"""
import collections
import csv
import pathlib
import sys

FOLDER = pathlib.Path(sys.argv[1])
OUT = pathlib.Path(sys.argv[2]) if len(sys.argv) > 2 else None
GROUPS = ("DI", "OVX", "MALE", "ORX")                    # house rule, PR #775
TREATMENTS = ("senktide", "TTX", "SB222200", "(baseline only)")

slices = {}
with (FOLDER / "slices.csv").open(encoding="utf-8-sig", newline="") as fh:
    for row in csv.DictReader(fh):
        slices[row["slice_id"]] = row

regions = collections.defaultdict(list)
with (FOLDER / "regions.csv").open(encoding="utf-8-sig", newline="") as fh:
    for row in csv.DictReader(fh):
        regions[row["slice_id"]].append((int(row["region_idx"]), row["label"]))

rows = []
for sid in sorted(slices):
    ordered = [lab for _, lab in sorted(regions.get(sid, []))]
    rest = [lab for lab in ordered if lab.strip().lower() != "baseline"]
    rows.append({"slice_id": sid,
                 "group": slices[sid]["group_id"],
                 "mouse": slices[sid]["mouse_id"],
                 "first_treatment": rest[0] if rest else "(baseline only)",
                 "regions_in_order": " / ".join(ordered),
                 "n_roi": slices[sid]["n_roi_recorded"]})

cell = collections.defaultdict(list)
for r in rows:
    cell[(r["group"], r["first_treatment"])].append(r["slice_id"])

names = [g for g in GROUPS if any(g == r["group"] for r in rows)]
labels = [t for t in TREATMENTS] + sorted({r["first_treatment"] for r in rows}
                                          - set(TREATMENTS))
for t in labels:
    for g in names:
        ids = cell[(g, t)]
        if ids:
            print(f"{g:5s} {t:16s} n={len(ids):2d}  " + ", ".join(ids))
    if any(cell[(g, t)] for g in names):
        print()

if OUT:
    OUT.parent.mkdir(parents=True, exist_ok=True)
    with OUT.open("w", encoding="utf-8", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=["slice_id", "group", "mouse", "first_treatment",
                                           "regions_in_order", "n_roi"])
        w.writeheader()
        w.writerows(rows)
    print(f"wrote {OUT} — {len(rows)} recordings")
