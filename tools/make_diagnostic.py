#!/usr/bin/env python3
"""Build the coordination diagnostic and write it to the darkroom.

    python tools/make_diagnostic.py                    # defaults
    python tools/make_diagnostic.py --seed 7 --duration 3000
    python tools/make_diagnostic.py --out ./somewhere  # override the destination

Produces, named by the run so successive runs sit side by side rather than
overwriting each other:

    coord_diagnostic_<tag>.html   the interactive view — zoom into a false alarm
    coord_diagnostic_<tag>.png    a flat render of the same page
    coord_diagnostic_<tag>.txt    the scoreboard, in text so it can go in a
                                  commit message or a log where a figure cannot

The PNG is not a convenience. The first version of this figure shipped with its
lane labels written on top of the data, an unexplained marker, and detections
too faint to see — because it was published without anyone rendering it. Both
the darkroom README ("render every slide and look at it before shipping") and
the murderboard's build-and-craft gate already said not to do that. Producing
the flat render in the same command is that rule mechanized: the picture a
reader will see is now an artifact of the build, previewable in Dropbox without
opening anything.

Destination is ``$BUGARACH_DARKROOM`` (see ``bugarach.paths``). It is never
hardcoded: that path carries a person's name and this repo is public. With the
variable unset the script says so and writes nothing, rather than guessing —
the darkroom is mounted on every machine, so a wrong guess scatters files into
another project's folder instead of failing locally.

Files are written to a temporary name and moved into place. The darkroom README
records 188 MB of hash-named orphans created by writing into Dropbox in place;
an atomic replace means the folder only ever sees a finished file.
"""

from __future__ import annotations

import argparse
import os
import sys
import tempfile
from pathlib import Path

import numpy as np

# The six, with the parameters this diagnostic runs them at. These are NOT the
# calibrated operating points — they are deliberately plain values chosen to
# make the picture legible. Anything comparative belongs in the bench, which
# scores against the calibrated settings; see docs/simulation_plan.md.
DETECTORS = {
    "coact": dict(int_win_sec=1.0, context_win_sec=60.0, min_rois=3,
                  n_surrogates=100, alpha=1e-4),
    "sce": dict(bin_width_sec=2.0, threshold_pctile=99.9, min_rois=3,
                n_surrogates=100),
    "sync": dict(tau_max=0.25, max_gap=0.5, C_threshold=0.1, C_min=0.1, min_n=3),
    "rate": dict(grid_dt=0.1, excess_threshold_hz=5.0, merge_gap_s=3.0,
                 rate_win=1.0, context_win=60.0),
    # loco and cicada are listed on purpose even though they currently FAIL on a
    # single-stream slice: their defaults are (FAST, SLOW) pairs that cannot
    # broadcast to one stream. Dropping them from this list would hide that in
    # the very artifact meant to expose detector behaviour — the report names
    # them under "did not run" instead. See
    # docs/todo/2026-08-13-single-stream-defaults-fail.md.
    "loco": {},
    "cicada": {},
}


def build(args):
    import holoviews as hv
    import panel as pn

    hv.extension("bokeh")

    from bugarach.detectors.rate import recording_extent
    from bugarach.simulate import simulate_coordination
    from bugarach.ui.app import _compute
    from bugarach.ui.diagnostic import (coordination_diagnostic, legend_html,
                                        score_table)

    slice_, gt = simulate_coordination(
        seed=args.seed,
        duration_sec=args.duration,
        n_roi=args.n_roi,
        n_per_level=(args.per_level,) * 3,
        interval_cv=args.interval_cv,
        hot_window=(args.duration * 0.4, args.duration * 0.6) if args.hot else None,
        hot_rate_hz=args.hot_rate if args.hot else 0.0,
        ramp_sec=args.duration * 0.02 if args.hot else 0.0,
        n_distractors=args.distractors,
    )
    ext = recording_extent(slice_)

    lanes, failed = {}, {}
    for det, params in DETECTORS.items():
        try:
            lanes[det] = _compute(det, slice_, ext, params)["events"][2]
        except Exception as exc:                      # noqa: BLE001
            # A detector that cannot run on this slice is a finding, not a crash
            # — record it in the sidecar instead of losing the whole figure.
            # loco and cicada currently land here on single-stream data; see
            # docs/todo/2026-08-13-single-stream-defaults-fail.md.
            failed[det] = f"{type(exc).__name__}: {exc}"

    fig = coordination_diagnostic(slice_.streams["events"], ext=ext, lanes=lanes,
                                  gt=gt, height=args.height)
    legend = legend_html(lanes, gt)

    header = [
        f"bugarach coordination diagnostic — seed {args.seed}",
        f"{args.n_roi} ROI · {args.duration:g}s · {len(gt.events)} planted events "
        f"· interval CV {args.interval_cv:g}",
    ]
    if args.hot:
        header.append(
            f"dense-but-random block {args.duration * 0.4:g}–{args.duration * 0.6:g}s "
            f"at +{args.hot_rate:g} Hz/ROI — contains NO planted events, so "
            f"detections inside it are false alarms by construction")
    if args.distractors:
        header.append(f"{args.distractors} correlated-burst distractors — real "
                      f"coincidence that is not a coordinated event")
    header += ["", score_table(gt, lanes)]
    if failed:
        header += ["", "did not run:"]
        header += [f"  {k}: {v}" for k, v in failed.items()]
    header += ["", "Parameters here are plain, not the calibrated operating "
                   "points — this is a troubleshooting view, not a ranking."]
    report = "\n".join(header)

    return fig, legend, header, report, pn


def main(argv=None):
    p = argparse.ArgumentParser(description=__doc__,
                                formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--seed", type=int, default=3)
    p.add_argument("--duration", type=float, default=1800.0)
    p.add_argument("--n-roi", type=int, default=30)
    p.add_argument("--per-level", type=int, default=5,
                   help="planted events at each of 100%%/75%%/50%% participation")
    p.add_argument("--interval-cv", type=float, default=1.0,
                   help="0 regular, 1 Poisson-like, >1 bursty")
    p.add_argument("--hot", action="store_true", default=True,
                   help="include the dense-but-random probe block (default on)")
    p.add_argument("--no-hot", dest="hot", action="store_false")
    p.add_argument("--hot-rate", type=float, default=0.25)
    p.add_argument("--distractors", type=int, default=3)
    p.add_argument("--height", type=int, default=560)
    p.add_argument("--tag", default=None, help="filename suffix (default: seed)")
    p.add_argument("--out", default=None,
                   help="destination directory; default $BUGARACH_DARKROOM")
    p.add_argument("--no-png", dest="png", action="store_false", default=True,
                   help="skip the flat render (needs playwright chromium)")
    args = p.parse_args(argv)

    from bugarach.paths import ENV_VAR, darkroom

    if args.out:
        dest = Path(args.out).expanduser()
        dest.mkdir(parents=True, exist_ok=True)
    else:
        dest = darkroom(create=True)
        if dest is None:
            print(f"{ENV_VAR} is not set, so there is nowhere agreed to write.\n"
                  f"Set it to this repo's darkroom folder, or pass --out DIR.\n"
                  f"Not guessing: the darkroom is visible from every machine, so "
                  f"a wrong guess lands files in another project's folder.",
                  file=sys.stderr)
            return 2

    fig, legend, header, report, pn = build(args)
    tag = args.tag or f"seed{args.seed}"
    html, txt = dest / f"coord_diagnostic_{tag}.html", dest / f"coord_diagnostic_{tag}.txt"

    # write-then-replace: the darkroom is inside Dropbox, and writing in place is
    # what produced its orphaned-file problem.
    with tempfile.TemporaryDirectory() as td:
        tmp_html = Path(td) / "fig.html"
        # header + legend + figure: a figure whose markers need explaining
        # and does not carry the explanation is not finished.
        title = header[0]
        subtitle = "  \n".join(header[1:4])
        page = pn.Column(
            pn.pane.Markdown("### " + title + "\n\n" + subtitle),
            pn.pane.HTML(legend),
            pn.pane.HoloViews(fig),
            pn.pane.HTML("<pre style='font:12px ui-monospace,monospace'>"
                         + report + "</pre>"),
        )
        page.save(str(tmp_html))
        os.replace(tmp_html, html)
        tmp_txt = Path(td) / "report.txt"
        tmp_txt.write_text(report + "\n", encoding="utf-8")
        os.replace(tmp_txt, txt)

    written = [html, txt]
    if getattr(args, "png", True):
        shot = dest / f"coord_diagnostic_{tag}.png"
        if _render_png(html, shot):
            written.append(shot)
        else:
            print("(no PNG: pip install playwright && python -m playwright "
                  "install chromium, or pass --no-png)", file=sys.stderr)

    print(report)
    print("\nwrote " + "\n      ".join(str(w) for w in written))
    return 0


def _render_png(html_path: Path, png_path: Path, *, wait_ms: int = 3500) -> bool:
    """Flatten the page to a PNG. Returns False rather than raising when the
    browser is unavailable — a missing screenshot must not cost you the figure."""
    try:
        from playwright.sync_api import sync_playwright
    except ImportError:
        return False
    try:
        with tempfile.TemporaryDirectory() as td:
            tmp = Path(td) / "shot.png"
            with sync_playwright() as pw:
                browser = pw.chromium.launch()
                page = browser.new_page(viewport={"width": 1180, "height": 1400})
                page.goto(html_path.resolve().as_uri())
                page.wait_for_timeout(wait_ms)      # bokeh draws after load
                page.screenshot(path=str(tmp), full_page=True)
                browser.close()
            os.replace(tmp, png_path)
        return True
    except Exception as exc:                        # noqa: BLE001
        print(f"(PNG render failed: {type(exc).__name__}: {exc})", file=sys.stderr)
        return False


if __name__ == "__main__":
    raise SystemExit(main())
