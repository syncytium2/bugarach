"""bugarach command line: launch the viewer on stores or event CSVs."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path


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

    from bugarach.ui.app import build_viewer, load_any

    slices = {}
    for f in _collect(args.paths):
        sid, s = load_any(f)
        name = sid
        k = 2
        while name in slices:            # disambiguate duplicate slice ids
            name = f"{sid} ({k})"
            k += 1
        slices[name] = s
    app = build_viewer(slices)
    pn.serve(app, port=args.port, show=not args.no_show)


if __name__ == "__main__":
    main()
