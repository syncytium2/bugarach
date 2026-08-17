"""bugarach command line: launch the viewer on stores or event CSVs."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path


def _is_export_folder(p: Path) -> bool:
    """A folder written to ``docs/export_folder_spec.md``, rather than a pile
    of files that happen to be CSVs. Decided by the reserved names, because
    that is exactly what separates the two — without this check `slices.csv`
    and `regions.csv` load as if they were recordings, and a folder of 85
    recordings opens as 87 with two of them nonsense."""
    from bugarach.io import RESERVED

    return p.is_dir() and any((p / n).is_file() for n in RESERVED)


def _collect(paths: list[str]) -> list[Path]:
    files = []
    for p in paths:
        p = Path(p)
        if p.is_dir():
            files.extend(sorted(p.glob("*.mat")))
            files.extend(sorted(p.glob("*.csv")))
        elif p.exists():
            files.append(p)
        else:
            sys.exit(f"bugarach: no such file or directory: {p}")
    if not files:
        sys.exit("bugarach: no .mat/.csv slices found")
    return files


def main(argv: list[str] | None = None) -> None:
    ap = argparse.ArgumentParser(
        prog="bugarach",
        description="Browse event slices and tune coordination detectors "
                    "in a browser (no MATLAB required).")
    sub = ap.add_subparsers(dest="cmd", required=True)
    view = sub.add_parser("view", help="launch the viewer")
    view.add_argument("paths", nargs="+",
                      help="store .mat files, event CSVs, or directories")
    view.add_argument("--port", type=int, default=5006)
    view.add_argument("--no-show", action="store_true",
                      help="don't open a browser tab")
    view.add_argument("--raster-only", action="store_true",
                      help="show the recordings and nothing else — no "
                           "detectors, no parameters. The first look at a "
                           "folder somebody just sent you.")
    chk = sub.add_parser(
        "check", help="does an export folder conform to the import contract?")
    chk.add_argument("folder", help="the export folder to check")
    args = ap.parse_args(argv)

    if args.cmd == "check":
        # deliberately importable without panel: a producer checking a folder
        # should not need the viewer's dependencies installed
        from bugarach.conform import check_folder, format_report

        rep = check_folder(args.folder)
        print(format_report(rep))
        raise SystemExit(0 if rep.ok else 1)

    import panel as pn

    from bugarach.io import load_folder
    from bugarach.ui.app import build_viewer, load_any

    slices = {}

    def add(sid, s):
        name, k = sid, 2
        while name in slices:            # disambiguate duplicate slice ids
            name = f"{sid} ({k})"
            k += 1
        slices[name] = s

    plain = []
    for p in args.paths:
        # an export folder is read as one thing, by the contract's own reader,
        # rather than swept for files — see _is_export_folder
        if _is_export_folder(Path(p)):
            for s in load_folder(p):
                add(s.slice_id, s)
        else:
            plain.append(p)
    for f in _collect(plain) if plain else []:
        add(*load_any(f))

    if not slices:
        sys.exit("bugarach: nothing to view")
    app = build_viewer(slices, raster_only=args.raster_only)
    pn.serve(app, port=args.port, show=not args.no_show)


if __name__ == "__main__":
    main()
