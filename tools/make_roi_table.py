#!/usr/bin/env python3
"""How many ROIs each recording has, by group and by first treatment.

    python tools/make_roi_table.py
    python tools/make_roi_table.py --also docs/learned/roi_table
    python tools/make_roi_table.py --treatments senktide TTX --groups DI OVX

One row per recording, two column blocks — senktide and TTX — and one block of
rows per experimental group. Tony, 2026-09-22, asked for exactly this table for
the recordings behind the group raster pages, and asked on 2026-09-23 that it be
reproducible: **the export folder changes under a table typed once**, and a
number nobody can re-derive is a number nobody can check.

THE INCLUSION RULE IS NOT RE-IMPLEMENTED HERE. Which recordings belong to a
treatment is `make_group_raster_summary.measure` — a recording is on a page when
the period right after its baseline is that treatment, and a later period never
adds one. That rule has already been got wrong once (matching any period put 35
recordings on the senktide pages against the producer's 29), so this tool imports
it rather than re-deriving it, and the table therefore lists exactly the
recordings the raster pages draw. Same reason the ROI count is read from the
producer's ``slices.csv`` ``n_roi_recorded`` column: the folder is the input, and
which ROIs are alive is the producer's call, already applied.

THE TABLE SAYS WHAT IT WAS BUILT FROM. Every output carries ``dataset.stamp()``
— the role, the folder name and its recording count — because this table's whole
purpose is to be rebuilt when the folder moves, and two copies that do not say
which folder they came from cannot be told apart.

Writes ``roi_table.md`` and ``roi_table.csv``. Destination is the darkroom,
resolved by ``bugarach.paths``; ``--also`` writes a second copy into the repo.
The path is never hardcoded: it carries a person's name and this repo is public.
"""

from __future__ import annotations

import argparse
import csv
import json
import statistics
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from bugarach import dataset, paths  # noqa: E402
from bugarach.groups import in_group_order  # noqa: E402

import make_group_raster_summary as rasters  # noqa: E402

DEFAULT_TREATMENTS = ("senktide", "TTX")


def read_roi_counts(folder: Path) -> dict[str, int]:
    """``slice_id -> n_roi_recorded``, the producer's own count."""
    with (folder / "slices.csv").open(newline="", encoding="utf-8-sig") as fh:
        return {row["slice_id"]: int(row["n_roi_recorded"])
                for row in csv.DictReader(fh)}


def measure(folder: Path, treatments: tuple[str, ...],
            groups: tuple[str, ...] | None = None):
    """``{(group, treatment): [(slice_id, n_roi), ...]}``, slice id order.

    Built from the raster pages' own membership, taken at one stream: a
    recording is on both its streams' pages and the ROI count is the producer's
    per-recording value, so counting streams would list every recording twice.
    """
    built, _manifest, skipped = rasters.measure(folder, treatments,
                                                steps_excluded=True,
                                                groups=groups)
    n_roi = read_roi_counts(folder)
    one_stream = sorted({s for (_g, _t, s) in built})[:1]
    out: dict[tuple[str, str], list[tuple[str, int]]] = {}
    for (group, treatment, stream), page in built.items():
        if stream not in one_stream:
            continue
        rows = sorted((sl.slice_id, n_roi[sl.slice_id]) for sl, _anchor in page["members"])
        out[(group, treatment)] = rows
    return out, skipped


def ordered_groups(table) -> list[str]:
    """DI, OVX, MALE, ORX, then any other label — `bugarach.groups`, one order in the tree."""
    return in_group_order(g for (g, _t) in table)


def as_rows(table, treatments: tuple[str, ...]) -> list[dict]:
    """One flat record per recording — the CSV, and what the markdown is built from."""
    rows = []
    for group in ordered_groups(table):
        for treatment in treatments:
            for slice_id, n_roi in table.get((group, treatment), []):
                rows.append({"group": group, "treatment": treatment,
                             "slice_id": slice_id, "n_roi_recorded": n_roi})
    return rows


def _slices(n: int) -> str:
    """Every number carries its unit, and one recording is a slice, not slices."""
    return f"{n} slice" if n == 1 else f"{n} slices"


def markdown(table, treatments: tuple[str, ...], stamp: dict) -> str:
    """The two-block table, groups down the page, with a summary line per group."""
    head = "| Group | " + " | ".join(f"{t} slice | ROIs" for t in treatments) + " |"
    rule = "|---" * (1 + 2 * len(treatments)) + "|"
    out = [head, rule]
    for group in ordered_groups(table):
        blocks = [table.get((group, t), []) for t in treatments]
        for i in range(max((len(b) for b in blocks), default=0)):
            cells = []
            for block in blocks:
                cells += ([str(block[i][0]), str(block[i][1])] if i < len(block)
                          else ["", ""])
            label = f"**{group}**" if i == 0 else ""
            out.append(f"| {label} | " + " | ".join(cells) + " |")
        summary = []
        for block in blocks:
            if block:
                counts = [n for _s, n in block]
                summary += [f"*{_slices(len(block))}*",
                            f"*median {statistics.median(counts):g} ROIs*"]
            else:
                summary += ["*none*", ""]
        out.append(f"| *{group} summary* | " + " | ".join(summary) + " |")
    totals = []
    for treatment in treatments:
        counts = [n for group in ordered_groups(table)
                  for _s, n in table.get((group, treatment), [])]
        totals += ([f"**{_slices(len(counts))}**", f"**{min(counts)}-{max(counts)} ROIs**"]
                   if counts else ["**none**", ""])
    out.append("| **All groups** | " + " | ".join(totals) + " |")
    out.append("")
    out.append(f"ROI counts are `n_roi_recorded` in the export folder's `slices.csv`. "
               f"A recording is listed under a treatment when the period right after its "
               f"baseline is that treatment, which is the rule the group raster pages use "
               f"(`tools/make_group_raster_summary.py`).")
    out.append("")
    out.append(f"Dataset: `{stamp['name']}` (role `{stamp['role']}`, "
               f"{stamp['recordings']} recordings). Rebuild with "
               f"`python tools/make_roi_table.py`.")
    return "\n".join(out) + "\n"


def write(dest: Path, table, treatments, stamp, skipped) -> None:
    dest.mkdir(parents=True, exist_ok=True)
    (dest / "roi_table.md").write_text(markdown(table, treatments, stamp),
                                       encoding="utf-8")
    with (dest / "roi_table.csv").open("w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=["group", "treatment", "slice_id",
                                           "n_roi_recorded"])
        w.writeheader()
        w.writerows(as_rows(table, treatments))
    (dest / "roi_table.json").write_text(
        json.dumps({"dataset": stamp,
                    "treatments": list(treatments),
                    "rows": as_rows(table, treatments),
                    "not_listed": skipped}, indent=2) + "\n",
        encoding="utf-8")
    print(f"  wrote {dest / 'roi_table.md'}")
    print(f"  wrote {dest / 'roi_table.csv'}")
    print(f"  wrote {dest / 'roi_table.json'}")


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--folder", default=None,
                    help="an export folder (default: the confirmed default dataset)")
    ap.add_argument("--treatments", nargs="+", default=list(DEFAULT_TREATMENTS),
                    help=f"one column block each (default: "
                         f"{' '.join(DEFAULT_TREATMENTS)})")
    ap.add_argument("--groups", nargs="+", default=None, metavar="GROUP",
                    help="only these groups (default: every group in the folder)")
    ap.add_argument("--out", default=None,
                    help="destination directory (default: the darkroom)")
    ap.add_argument("--also", default=None, help="write a second copy here")
    a = ap.parse_args(argv)

    folder = rasters.resolve_folder(a.folder, steps_excluded=True)
    treatments = tuple(a.treatments)
    table, skipped = measure(folder, treatments,
                             tuple(a.groups) if a.groups else None)
    stamp = dataset.stamp()

    if a.out:
        dest = Path(a.out).expanduser()
    else:
        root = paths.darkroom(create=True)
        if root is None:
            print(paths.unresolved_message(), file=sys.stderr)
            return 2
        dest = root / "roi_table"
    write(dest, table, treatments, stamp, skipped)
    if a.also:
        write(Path(a.also).expanduser(), table, treatments, stamp, skipped)

    listed = sum(len(v) for v in table.values())
    print(f"\n{listed} recording(s) listed; {len(skipped)} not listed "
          f"(first treatment is none of {', '.join(treatments)})")
    print(f"dataset: {stamp['name']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
