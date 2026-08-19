#!/usr/bin/env python3
"""Which recordings has the lab marked excluded? Ask the record, don't infer it.

    python tools/lab_excluded.py --store <onset store> --out docs/learned/lab_excluded_slices.txt

**Why this exists.** Every measurement in the assembly line of work was computed over the
recordings present in the onset store, and the store is not a statement about which
recordings the lab considers analysable. That statement lives in a separate workbook —
`indiegroups_db4.xlsx`, sheet `indiegroups`, column **`exclude`** — which no part of this
analysis had ever opened. Two recordings marked `exclude=1` were inside every reported
number until a review went looking for the source of record.

**Selection is the producer's call, not the analysis layer's.** That rule is already this
project's, from the dead-ROI argument (Tony to fireflies, 2026-08-10): the analysis does not
get to invent an inclusion threshold, and by the same token it does not get to overrule one.
So the default is to respect the mark.

**The exclusion is matched by DATE, and that is deliberately blunt.** The workbook keys on
(date, mouse) and carries no slice id; a store recording is `<date>_<n>`. Any recording
sharing a date with an excluded row is therefore returned. Where a date carries several
slices this may exclude more than the lab meant, which is the conservative direction and is
reported so a reader can see the cost.

Reads the workbook and the store; writes a list with its provenance in the header.
"""
from __future__ import annotations

import argparse
import re
from pathlib import Path

SHEET = "indiegroups"


def excluded_dates(xlsx: Path) -> list[tuple[str, str, str]]:
    """(date, mouse_id, reason) for every row the lab marked excluded."""
    import openpyxl
    wb = openpyxl.load_workbook(xlsx, read_only=True, data_only=True)
    ws = wb[SHEET]
    it = ws.iter_rows(values_only=True)
    hdr = list(next(it))
    idx = {c: i for i, c in enumerate(hdr) if c}
    for need in ("date", "mouse_id", "exclude"):
        if need not in idx:
            raise SystemExit(f"{xlsx}: sheet {SHEET} has no `{need}` column")
    out, seen = [], set()
    for r in it:
        if not r or r[idx["mouse_id"]] is None:
            continue
        if r[idx["exclude"]] in (None, "", 0, "0"):
            continue
        d = str(r[idx["date"]]).strip()
        m = str(r[idx["mouse_id"]]).strip()
        reason = str(r[idx.get("notes", -1)] if "notes" in idx else "") or ""
        if (d, m) in seen:
            continue
        seen.add((d, m))
        out.append((d, m, reason.strip()))
    return sorted(out)


def match_store(store: Path, dates: set[str]) -> list[str]:
    ids = sorted(p.stem for p in Path(store).glob("*.mat"))
    hit = []
    for s in ids:
        m = re.match(r"(\d{8})", s)
        if m and m.group(1) in dates:
            hit.append(s)
    return hit


def main(argv=None) -> int:
    p = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--xlsx", type=Path, default=None,
                   help="default: $BUGARACH_DATA_ROOT/indiegroups_db4.xlsx")
    p.add_argument("--store", type=Path, required=True)
    p.add_argument("--out", type=Path, default=None)
    a = p.parse_args(argv)

    xlsx = a.xlsx
    if xlsx is None:
        import os
        root = os.environ.get("BUGARACH_DATA_ROOT")
        if not root:
            raise SystemExit("no --xlsx and BUGARACH_DATA_ROOT is unset")
        xlsx = Path(root) / "indiegroups_db4.xlsx"

    rows = excluded_dates(xlsx)
    dates = {d for d, _, _ in rows}
    hits = match_store(a.store, dates)

    print(f"lab record: {xlsx}")
    print(f"  {len(rows)} excluded (date, mouse) rows over {len(dates)} dates")
    for d, m, why in rows:
        print(f"    {d}  mouse {m:>4}  {why}")
    print(f"store: {a.store}")
    print(f"  {len(hits)} recording(s) on an excluded date:")
    for h in hits:
        print(f"    {h}")

    if a.out:
        a.out.parent.mkdir(parents=True, exist_ok=True)
        lines = [
            "# Recordings the lab has marked excluded.",
            f"# Source of record: {xlsx.name}, sheet `{SHEET}`, column `exclude`.",
            "# Matched by DATE — the workbook keys on (date, mouse) and carries no slice id,",
            "# so a date with several slices excludes all of them. Conservative on purpose.",
            "# Regenerate: python tools/lab_excluded.py --store <onset store> --out <this file>",
            "#",
        ]
        lines += [f"# reason: {d} mouse {m} — {why}" for d, m, why in rows]
        lines += [""] + hits + [""]
        a.out.write_text("\n".join(lines))
        print(f"\nwrote {a.out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
