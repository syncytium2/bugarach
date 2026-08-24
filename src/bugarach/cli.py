"""bugarach command line: launch the viewer, and run a folder through the ports.

Four things a lab does with an export folder, one word each: ``check`` that it
conforms, ``assess`` how coordinated it is with no detector involved, ``detect``
the coordinated events and write them down, ``view`` the recordings in a browser.

``detect`` is the newest and closes a hole. :mod:`bugarach.emit` — the writer for
the whole output contract — had no caller anywhere outside the tests, so the only
route to a ``detections.csv`` ran through a browser page and a person clicking in
it. Nothing could be scripted, scheduled, or run over 84 recordings unattended.
"""

from __future__ import annotations

import argparse
import sys
import time
from pathlib import Path

CONTRACT = ("see the export contract: docs/export_folder_spec.md in the "
            "bugarach repo, or export_folder_spec.html beside the one-page "
            "producer guide wherever that was sent to you")


def _folder_or_exit(path: str) -> Path:
    """A readable export folder, or a message a producer can act on.

    ``bugarach check`` has always reported a bad path cleanly; ``assess`` handed
    the same path back as a ``NotADirectoryError`` traceback out of the loader.
    A stack trace says the tool did not expect this, when what happened is
    entirely expected and has a one-line answer.
    """
    p = Path(path)
    if not p.exists():
        sys.exit(f"bugarach: no such folder: {p}\n  An export folder holds one "
                 f"CSV per recording, plus optionally slices.csv and "
                 f"regions.csv — {CONTRACT}")
    if not p.is_dir():
        sys.exit(f"bugarach: {p} is a file, not a folder. bugarach reads an "
                 f"export folder — one CSV per recording — {CONTRACT}")
    return p


def _load_or_exit(fn, *args, **kw):
    """Run something that reads a folder, reporting a bad folder as a message.

    The loader's own refusals are precise and worth showing — *no recordings in
    here*, *region_idx is not an integer*, *analysis_start_sec without an end*.
    What they should not arrive as is a traceback.
    """
    try:
        return fn(*args, **kw)
    except (OSError, ValueError) as exc:
        sys.exit(f"bugarach: {exc}\n  {CONTRACT}")


def _progress(label: str):
    """A per-recording progress line on stderr, with what is left to go.

    The folder commands went **blind for two minutes**: 117 s over an
    84-recording folder with not one byte printed until the whole report landed
    at the end, so a new user could not tell working from hung. It goes to
    stderr, so redirecting the report to a file still yields a clean report; it
    rewrites one line on a terminal and prints plainly when piped.
    """
    start = time.monotonic()

    def cb(done: int, total: int, slice_id: str | None) -> None:
        el = time.monotonic() - start
        if slice_id is None:
            msg, end = f"{label}: {total}/{total} in {el:.0f}s", "\n"
        else:
            eta = f", ~{(el / done) * (total - done):.0f}s left" if done else ""
            msg, end = f"{label}: {done}/{total} · {slice_id} ({el:.0f}s{eta})", ""
        if sys.stderr.isatty():
            print(f"\r\033[K{msg}", end=end, file=sys.stderr, flush=True)
        else:
            print(msg, file=sys.stderr, flush=True)

    return cb


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

    asr = sub.add_parser(
        "assess", help="how coordinated are these recordings? (no detector)")
    asr.add_argument("folder", help="the export folder to assess")
    asr.add_argument("--stream", default=None,
                     help="which stream; default is the first in each recording")
    asr.add_argument("--surrogates", type=int, default=1000,
                     help="circular-shift surrogates per recording (default 1000, "
                          "the value the reference numbers were produced at)")
    asr.add_argument("--bin-width", type=float, default=None,
                     help="coactivity bin in seconds; default 1.0. It interacts "
                          "with what counts as one event — say which you used")
    asr.add_argument("--limit", type=int, default=None,
                     help="assess only the first N recordings")

    from bugarach.detect_folder import DETECTORS

    det = sub.add_parser(
        "detect", help="run the detectors over a folder and write detections.csv")
    det.add_argument("folder", help="the export folder to detect on")
    # NOT required, and that is a rule rather than a convenience: a tool whose
    # output is meant for a person defaults its destination to the darkroom,
    # because the one deliverable that required --out was the one that never
    # reached anybody (sapper SAP006).
    det.add_argument("--out", default=None, type=Path,
                     help="where the three output files go; defaults to the "
                          "darkroom, under detect/<folder name>")
    det.add_argument("--stream", default=None,
                     help="report only this stream; default is every stream. "
                          "The three region-aware ports still RUN every stream "
                          "either way — they share one RNG stream in "
                          "declaration order, so dropping one would move the "
                          "numbers of the rest")
    det.add_argument("--detectors", default=None,
                     help=f"comma-separated subset of {','.join(DETECTORS)}; "
                          f"default is all six")
    det.add_argument("--frame-interval", type=float, default=None,
                     help="the acquisition interval in seconds, for a folder "
                          "whose slices.csv does not carry it. There is no "
                          "default: a default here is a guess about somebody "
                          "else's microscope (FOUNDATIONS §6)")
    det.add_argument("--limit", type=int, default=None,
                     help="detect on only the first N recordings")

    # Imported at module scope below rather than lazily: the help text quotes
    # the default port, so a reader of `bugarach lab --help` sees the number
    # this server actually binds instead of one written twice.
    from bugarach import lab as lab_mod

    lab = sub.add_parser(
        "lab", help="serve the viewer locally, with training enabled")
    lab.add_argument("--port", type=int, default=lab_mod.DEFAULT_PORT,
                     help=f"loopback port (default {lab_mod.DEFAULT_PORT}); "
                          f"0 picks a free one")
    lab.add_argument("--no-show", action="store_true",
                     help="don't open a browser tab")
    lab.add_argument("--stub", action="store_true",
                     help="serve the endpoints against a trainer that fits "
                          "nothing and calls an event a minute — for driving "
                          "the page against the seam without paying for a fit")
    args = ap.parse_args(argv)

    if args.cmd == "lab":
        # The published page is untouched by this. The server appends the
        # `window.__lab` shim to the copy it hands out; the copy on disk — the
        # one `build_site.py` publishes — never grows a transport.
        # docs/adr/0001-the-lab-server.md.
        raise SystemExit(lab_mod.serve(
            port=args.port,
            trainer=lab_mod.StubTrainer() if args.stub else None,
            open_browser=not args.no_show))

    if args.cmd == "detect":
        # importable without panel, like `check` and `assess`: a lab running its
        # own folder through the ports should not need the viewer installed
        from bugarach.detect_folder import (
            NoRecordingDetectedOn,
            detect_folder,
            format_run,
        )
        from bugarach.paths import darkroom

        folder = _folder_or_exit(args.folder)
        names = (DETECTORS if args.detectors is None
                 else tuple(x.strip() for x in args.detectors.split(",") if x.strip()))
        bad = [d for d in names if d not in DETECTORS]
        if bad:
            sys.exit(f"bugarach: unknown detector(s) {', '.join(bad)} — have "
                     f"{', '.join(DETECTORS)}")

        out = args.out
        if out is None:
            dark = darkroom()
            if dark is None:
                sys.exit(
                    "bugarach: no --out, and the darkroom could not be "
                    "resolved. Set BUGARACH_DARKROOM, or pass --out. "
                    "`python -m bugarach.paths` says what it looked at")
            out = dark / "detect" / folder.name

        try:
            run = _load_or_exit(
                detect_folder, folder, out_dir=out, detectors=names,
                stream=args.stream, frame_interval_sec=args.frame_interval,
                limit=args.limit, progress=_progress("detecting"))
        except NoRecordingDetectedOn as exc:
            # The refusal has to reach the EXIT CODE, because that is the only
            # thing a pipeline reads from this process — the same reasoning
            # `tools/make_diagnostic.py` was given in PR #255, and the same
            # threshold, so the two tools cannot teach a user opposite rules.
            # The roster still prints: the refusal says the folder failed, and
            # the roster says what each recording raised.
            if exc.run is not None:
                print(format_run(exc.run))
                # stdout is block-buffered when redirected and stderr is not, so
                # without this the refusal lands above the report it explains.
                sys.stdout.flush()
            sys.exit(f"bugarach: {exc}")
        print(format_run(run))
        # Exit 0 once at least one recording was scored, whatever the detectors
        # then found. Zero detections across scored recordings is a finding
        # about the tissue, and a folder where SOME recordings were skipped is a
        # finding about those recordings — both are named in the report and in
        # run.json, and turning either into a failure invites somebody to make
        # it pass. Scoring nothing at all is not a finding: it is this command
        # not having run, and it exits above.
        raise SystemExit(0)

    if args.cmd == "assess":
        # importable without panel, for the same reason `check` is: a lab
        # measuring its own folder should not need the viewer installed
        from bugarach.assess_folder import assess_folder, format_assessment

        fa = _load_or_exit(
            assess_folder, _folder_or_exit(args.folder), stream=args.stream,
            n_surrogates=args.surrogates, bin_width_sec=args.bin_width,
            limit=args.limit, progress=_progress("assessing"))
        print(format_assessment(fa))
        # Exit 0 whether or not anything was assessable. This is a MEASUREMENT,
        # not a gate: "no recording carried a baseline region" is an answer about
        # the folder, and turning it into a non-zero exit would put it in a build
        # where somebody would make it pass.
        raise SystemExit(0)

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
    # Loopback, and both spellings of it.
    #
    # This served on every interface until 2026-08-23 — `pn.serve` with no
    # address binds 0.0.0.0 and ::, so a laptop on a conference network was
    # handing out its real recordings to anyone who knew the port. `bugarach
    # lab` has bound 127.0.0.1 from the start and says why; the asymmetry was
    # exactly the wrong way round, since lab serves simulated data and this
    # serves the recordings.
    #
    # Binding loopback is not enough on its own: Bokeh checks the websocket
    # Origin against the address it was given, so a user who typed the IP got a
    # blank page and the reason only in the server log ("Refusing websocket
    # connection from Origin ... 403 GET /ws"). Both spellings are allowed so
    # neither is a dead end. Port 0 picks a port at runtime and cannot be named
    # in an origin ahead of time, so it keeps Bokeh's own default.
    origins = ([f"localhost:{args.port}", f"127.0.0.1:{args.port}"]
               if args.port else None)
    pn.serve(app, port=args.port, address="127.0.0.1",
             websocket_origin=origins, show=not args.no_show)


if __name__ == "__main__":
    main()
