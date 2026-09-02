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

Destination is the darkroom, resolved by ``bugarach.paths`` — from
``$BUGARACH_DARKROOM``, or from Dropbox's own record of where it mounted itself.
It is never hardcoded: that path carries a person's name and this repo is
public. When neither route answers the script says so and writes nothing, rather
than guessing — the darkroom is mounted on every machine, so a wrong path
scatters files into another project's folder instead of failing locally.

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

#: What the raster's y-axis calls itself. **"simulated", not "events"**, because
#: every recording this tool draws comes from `simulate_coordination` — there is
#: no path through it that renders a real slice. Tony, 2026-09-02: *"label the
#: raster as simulated. use yaxis title."*
#:
#: The y-axis is the right place by this repo's own plot conventions — identity
#: and counts live in the y-label, never as text laid over the marks — and it is
#: the durable place: a caption saying "simulated recording" can be trimmed, and
#: the figure travels into reports and slides without it. A reader who meets this
#: raster anywhere at all should not have to be told it is not data.
RASTER_NAME = "simulated"

# The six, at the operating points the bench declares, with their provenance —
# so this figure and the scores in bugarach.bench describe the same detectors.
# An earlier version used "deliberately plain values chosen to make the picture
# legible", which quietly meant the diagnostic and the bench could disagree
# about what a detector does; coact at the MATLAB signature default scores F1
# 0.72 against 1.00 at its calibrated point, and a picture drawn at the wrong
# one is a picture of a different detector.
#
# (loco and cicada used to fail here outright — their defaults were (FAST, SLOW)
# pairs that could not broadcast to a single-stream slice. Fixed 2026-08-13;
# the "did not run" path below stays, because a detector that cannot run is a
# finding worth printing rather than a crash worth losing the figure to.)
def _detector_params(without=()):
    """The calibrated operating points, minus any detector a build withholds.

    `without` exists because a figure is part of a BUILD, not a fixed fact about
    the project. Tony, 2026-08-29: *"we must be able to remove or add detectors
    and models at will."* The published site passes it; a troubleshooting run
    passes nothing and still draws all six, which is what this tool is for.

    **A lane is the one place a withheld detector comes back without anyone
    editing a page.** Every served HTML file can be scrubbed clean while
    `hero.png`, rendered from `bugarach.ui`, still carries the name in its y-axis
    label — where no grep of the served bytes will ever find it. That happened on
    2026-08-29, which is why this is an argument and not a note asking somebody
    to remember.
    """
    from bugarach.bench import OPERATING_POINTS
    drop = set(without or ())
    return {name: dict(op.params) for name, op in OPERATING_POINTS.items()
            if name not in drop}


class NoDetectorRan(RuntimeError):
    """Every detector failed, so there is no figure to write — only an empty one.

    **The `except` below is right and this is not a retreat from it.** A detector
    that cannot run on a particular slice is a finding: record it in the sidecar,
    draw the other five, and let whoever is troubleshooting see both. That is what
    this tool is for.

    *Every* detector failing at once is a different animal. It has never once
    meant six independent findings; both times it happened it was this file
    calling `_compute` the old way after its signature changed — `dt` becoming
    required, then `StreamResult` growing a fifth field — and each time the six
    identical tracebacks went into the sidecar, the figure was drawn with six
    blank lanes, and the process exited 0.

    An empty figure is worse than no figure, and worse than the text fallback the
    site can use, because both of those announce themselves. This one looked like
    a figure: a raster, six labelled lanes, a valid 196 KB PNG that a person would
    put on a front page. The threshold is therefore *all*, not *any* — the site
    build applies the stricter `any` at publish time, where the page promises six.
    """


def _dt_for(slice_) -> float:
    """The recording's sampling interval, from the one accessor that has it.

    `Slice.dt` became a real typed field in PR #250 and `require_dt` is the single
    place a number can come from, with the refusal message already written
    (FOUNDATIONS §6). This used to read `gt.params["grid_sec"]` — the generator's
    imaging grid, which is the same number by construction — and one path is
    better than two that agree.
    """
    return float(slice_.require_dt("the diagnostic figure"))


def _recording_maker(args):
    """``seed -> (slice, gt)`` at THIS figure's settings, for the trainer.

    The model has to be trained on the regime the figure draws — a tube fitted to
    the bench's 120 s spacing and shown over a 15 s one is a picture of a transfer
    failure captioned as a detector. So the closure restates the same generator
    arguments `build` used, and takes the seed from the caller.

    It never sees the figure's own seed. :func:`bugarach.learn.train.train` draws
    from ``TRAIN_SEED_BLOCK`` and picks its threshold from a second block above
    that; the figure is drawn on the seed in ``args``, which is in neither.
    Evaluating on a recording the model trained on is the most flattering possible
    mistake and the seed blocks are what stop it.
    """
    from bugarach.bench import make_recording as bench_recording
    from bugarach.simulate import simulate_coordination

    if args.bench:
        return lambda seed: bench_recording(args.bench, seed)

    def make(seed):
        return simulate_coordination(
            seed=seed,
            duration_sec=args.duration,
            n_roi=args.n_roi,
            n_per_level=(args.per_level,) * 3,
            interval_cv=args.interval_cv,
            hot_window=(args.duration * 0.4, args.duration * 0.6) if args.hot else None,
            hot_rate_hz=args.hot_rate if args.hot else 0.0,
            ramp_sec=args.duration * 0.02 if args.hot else 0.0,
            n_distractors=args.distractors,
        )
    return make


def _tube_lane(arch, slice_, *, dt, recording, steps):
    """Train one architecture and return its lane, its trace and the fit.

    Returns ``((onsets, widths), (t, y, (onsets, widths), extra), Trained)`` —
    the same shapes ``_compute`` produces for the six, so the lane and the trace
    join the figure through the identical path and nothing downstream needs to
    know one of the rows came from a network.

    The learning rate is read from :data:`bugarach.lab.TubeTrainer.LR`, which is
    itself quoted from ``tools/fair_bakeoff.py``. A rate chosen here would make
    this figure a different experiment from the published one.
    """
    import numpy as np

    from bugarach.lab import TubeTrainer
    from bugarach.learn.train import train

    trained = train(arch, recording, dt=dt, steps=steps,
                    lr=TubeTrainer.LR.get(arch, 1e-3))
    det, _enc = trained.predict(slice_)
    onsets = np.asarray(det.onset_sec, dtype=float)
    widths = np.asarray(det.width_sec, dtype=float)

    # The trace is the model's own per-frame score — the quantity its threshold
    # is applied to, so a reader can see WHY each bar is where it is. Taken from
    # `to_seconds`, which carries `score` and `times` alongside the detections it
    # produced them from. Re-running the forward pass here to get the same curve
    # would be a second computation that could disagree with the first.
    t = np.asarray(det.times, dtype=float)
    y = np.asarray(det.score, dtype=float)

    extra = {"threshold": float(trained.threshold)}
    return (onsets, widths), (t, y, (onsets, widths), extra), trained


def build(args):
    import holoviews as hv
    import panel as pn

    hv.extension("bokeh")

    from bugarach.detectors.rate import recording_extent
    from bugarach.simulate import simulate_coordination
    from bugarach.ui.app import TITLES, _compute
    from bugarach.ui.diagnostic import (coordination_diagnostic, legend_html,
                                        score_table)

    if args.bench:
        # The bench's own recording, so the figure and the scores in
        # bugarach.bench describe the same run rather than merely the same
        # detectors. The two differ in ways that matter — the bench spaces
        # events 120 s apart to keep the null clean, this tool's default is 15 s
        # — and a picture drawn on a different recording is not evidence about
        # the bench.
        from bugarach.bench import BENCH_RECORDING, make_recording
        slice_, gt = make_recording(args.bench, args.seed)
        args.duration = BENCH_RECORDING["duration_sec"]
        args.n_roi = BENCH_RECORDING["n_roi"]
    else:
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

    dt = _dt_for(slice_)

    lanes, traces, failed = {}, {}, {}
    for det, params in _detector_params(getattr(args, "without", ())).items():
        try:
            # Read the fields by name. This used to unpack the tuple positionally
            # and broke silently the day `StreamResult` grew a fifth field for
            # the emit writer — the figure has never needed that field and still
            # does not, and it should not have to be edited when a sixth arrives.
            r = _compute(det, slice_, ext, params, dt=dt)["events"]
            lanes[det] = r.events
            traces[det] = (r.t, r.y, r.events, r.extra)
        except Exception as exc:                      # noqa: BLE001
            # A detector that cannot run on this slice is a finding, not a crash
            # — record it in the sidecar instead of losing the whole figure.
            failed[det] = f"{type(exc).__name__}: {exc}"

    if getattr(args, "tube", None):
        arch = args.tube
        try:
            lanes[arch], traces[arch], trained = _tube_lane(
                arch, slice_, dt=dt, recording=_recording_maker(args),
                steps=args.tube_steps)
            header_tube = (
                f"{TITLES.get(arch, arch)}: {trained.n_params:,} parameters, "
                f"trained in {trained.train_seconds:.1f}s on seeds from the "
                f"training block, threshold {trained.threshold:.3f} picked on "
                f"held-out recordings")
        except Exception as exc:                      # noqa: BLE001
            # Unlike the six, this one can fail for a reason about the MACHINE
            # rather than the data — torch is the optional `dl` extra. Both end
            # up here, and the message has to let a reader tell them apart,
            # because "the learned lane is missing" reads as a result.
            failed[arch] = f"{type(exc).__name__}: {exc}"
            header_tube = None
    else:
        header_tube = None

    if failed and not lanes:
        raise NoDetectorRan(
            "not one of the "
            f"{len(failed)} detectors ran, so there is no figure to draw — only "
            "a raster with blank lanes, which looks like a result and is not "
            "one. This is the call site being wrong, not six findings; the two "
            "times it has happened, _compute's signature had changed under it. "
            "What each raised:\n  "
            + "\n  ".join(f"{k}: {v}" for k, v in failed.items()))

    fig = coordination_diagnostic(slice_.streams["events"], ext=ext, lanes=lanes,
                                  gt=gt, traces=traces, height=args.height,
                                  name=RASTER_NAME,
                                  mark_px=getattr(args, "mark_px", None))
    legend = legend_html(lanes, gt)

    # The hero is the same figure with the analysis traces dropped — lanes over
    # raster and nothing below. Tony, 2026-09-02: *"condense the top of the
    # raster so that the net, the detections, and the raster are all easily
    # viewed without scrolling."* The traces were three panels of ~112px each on
    # a page whose first screen also has to hold the model diagram, and they
    # answer a different question ("what does each detector compute?") which the
    # diagnostic page exists to answer at length.
    #
    # Built as a SECOND figure rather than by re-running the fit: same lanes,
    # same raster, same ground truth, no extra seconds.
    # `getattr`, not `args.hero`: `build()` is called directly by tests with a
    # hand-made namespace, and a function that reads an attribute only argparse
    # guarantees turns "this tool grew an option" into "three unrelated tests
    # fail with AttributeError". The caller that wants a hero passes one.
    hero_fig = (coordination_diagnostic(slice_.streams["events"], ext=ext,
                                        lanes=lanes, gt=gt, traces=None,
                                        height=args.height, name=RASTER_NAME,
                                        mark_px=getattr(args, "mark_px", None))
                if getattr(args, "hero", None) else None)

    header = [
        f"bugarach coordination diagnostic — seed {args.seed}",
        f"{args.n_roi} ROI · {args.duration:g}s · {len(gt.events)} planted events"
        + (f" · bench {args.bench} regime" if args.bench
           else f" · interval CV {args.interval_cv:g}"),
    ]
    # read the probe and distractors off the ground truth, not off the CLI args:
    # with --bench the recording came from bugarach.bench and the args no longer
    # describe it. A caption that describes a different recording is worse than
    # no caption.
    hot = gt.params.get("hot_window")
    if hot:
        header.append(
            f"dense-but-random block {hot[0]:g}–{hot[1]:g}s at "
            f"+{gt.params.get('hot_rate_hz', args.hot_rate):g} Hz/ROI — contains "
            f"NO planted events, so detections inside it are false alarms by "
            f"construction")
    if gt.distractors:
        header.append(f"{len(gt.distractors)} correlated-burst distractors — real "
                      f"coincidence that is not a coordinated event")
    if header_tube:
        header.append(header_tube)
    header += ["", score_table(gt, lanes)]
    if failed:
        header += ["", "did not run:"]
        header += [f"  {k}: {v}" for k, v in failed.items()]
    header += ["", "Detectors run at the operating points declared in "
                   "bugarach.bench, so this figure and the bench scores describe "
                   "the same detectors. Still a troubleshooting view, not a "
                   "ranking — one seed is not a measurement."]
    report = "\n".join(header)

    return fig, hero_fig, legend, header, report, pn


def main(argv=None):
    p = argparse.ArgumentParser(description=__doc__,
                                formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--without", nargs="*", default=(), metavar="DETECTOR",
                   help="detectors this build withholds — no lane, no trace, no "
                        "score row. Default: none, so a troubleshooting run "
                        "draws all six. The published site passes the same set "
                        "the viewer's WITHHELD holds, because a figure carries "
                        "a detector's name in pixels where no grep of the "
                        "served HTML will find it.")
    p.add_argument("--tube", nargs="?", const="tube", default=None,
                   metavar="ARCH",
                   help="also draw a LEARNED lane, trained on this figure's own "
                        "regime from the training seed block. Names an entry in "
                        "bugarach.learn.nets.ARCHITECTURES; bare --tube means "
                        "`tube`. Off by default: it needs torch (the optional "
                        "`dl` extra) and costs a fit, so a troubleshooting run "
                        "should not pay for it unless it asked.")
    p.add_argument("--tube-steps", type=int, default=900, metavar="N",
                   help="training steps for --tube (default 900, the value "
                        "tools/fair_bakeoff.py uses).")
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
    p.add_argument("--height", type=int, default=200,
                   help="raster height in px. Short on purpose: a coordinated "
                        "event is a vertical alignment, and vision reads one "
                        "better over less distance — raster_panel's docstring "
                        "has the argument and the limit")
    p.add_argument("--mark-px", type=float, default=None,
                   help="height of one onset mark in px (default: raster_panel's "
                        "own). Moves with --height: a mark as tall as its own row "
                        "makes every column look solid whether or not anything "
                        "coordinated")
    from bugarach.bench import REGIMES as _R
    p.add_argument("--bench", choices=tuple(_R), default=None,
                   help="render the bugarach.bench recording for this regime "
                        "instead of one built from the options above")
    p.add_argument("--tag", default=None, help="filename suffix (default: seed)")
    p.add_argument("--out", default=None,
                   help="destination directory; default $BUGARACH_DARKROOM")
    p.add_argument("--no-png", dest="png", action="store_false", default=True,
                   help="skip the flat render (needs playwright chromium)")
    p.add_argument("--scale", type=int, default=3,
                   help="device pixel ratio for the PNG — how far it can be "
                        "zoomed before it goes soft (default 3, ~1.4 MB)")
    p.add_argument("--hero", default=None, metavar="PNG",
                   help="also render the plot ALONE to this path — no title, no "
                        "legend, no score table. For pages that lead with the "
                        "picture and carry the explanation in their own words.")
    args = p.parse_args(argv)

    from bugarach.paths import darkroom, unresolved_message

    if args.out:
        dest = Path(args.out).expanduser()
        dest.mkdir(parents=True, exist_ok=True)
    else:
        dest = darkroom(create=True)
        if dest is None:
            print(unresolved_message(), file=sys.stderr)
            return 2

    # The refusal has to reach the EXIT CODE, because that is the only thing
    # `build_site.py` reads from this process. A refusal that printed to stderr
    # and still returned 0 would be the original bug wearing a different hat.
    # Nothing has been written at this point — `build` returns before `main`
    # opens a file — so an empty figure cannot be left behind either.
    try:
        fig, hero_fig, legend, header, report, pn = build(args)
    except NoDetectorRan as exc:
        print(f"make_diagnostic: {exc}", file=sys.stderr)
        return 1
    tag = args.tag or f"seed{args.seed}"
    html, txt = dest / f"coord_diagnostic_{tag}.html", dest / f"coord_diagnostic_{tag}.txt"

    # write-then-replace: the darkroom is inside Dropbox, and writing in place is
    # what produced its orphaned-file problem.
    with tempfile.TemporaryDirectory() as td:
        tmp_html = Path(td) / "fig.html"
        # header + figure + legend: a figure whose markers need explaining and
        # does not carry the explanation is not finished — but the explanation
        # goes UNDER it.
        #
        # THE FIGURE COMES SECOND, NOT THIRD (Tony, 2026-08-30, of this page:
        # *"raster should dominate rather than a crapton of dense text and
        # symbols"*). The legend sat between the title and the figure, so a
        # reader met eleven SVG keys and their glosses before the thing they
        # annotate, with nothing yet to attach them to. A key is consulted when
        # something is puzzling, which is after looking.
        #
        # `<details>`, not deletion. These keys are the only place the ✕ and the
        # ◯ are explained, and this file's own module docstring records shipping
        # this figure once with "an unexplained marker" in it. Closed is not
        # hidden: it is one click, sitting beside the picture that raised the
        # question instead of ahead of it.
        title = header[0]
        subtitle = "  \n".join(header[1:4])
        page = pn.Column(
            pn.pane.Markdown("### " + title + "\n\n" + subtitle),
            pn.pane.HoloViews(fig),
            pn.pane.HTML("<details><summary style='cursor:pointer;font:13px "
                         "system-ui,sans-serif;padding:6px 0;color:#555'>"
                         "What the marks mean</summary>" + legend + "</details>"),
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
        if _render_png(html, shot, scale=getattr(args, "scale", 3)):
            written.append(shot)
        else:
            print("(no PNG: pip install playwright && python -m playwright "
                  "install chromium, or pass --no-png)", file=sys.stderr)

    if args.hero:
        # The plot without the prose above it — no title, no score table. It
        # still carries its KEY, and that is a correction rather than a
        # relaxation of the rule above.
        #
        # ⚠ THIS USED TO SHIP WITH NO LEGEND AT ALL, on the reasoning that "a
        # page that leads with this must supply the reading instructions itself"
        # and that a lead graphic which is 300px of rendered text is a picture of
        # a paragraph. The first half was wrong in practice. The front page did
        # supply them, in its caption, and Tony still could not read the figure —
        # 2026-09-02: *"open triangles never defined. needs a complete legend in
        # figure."* He was right and the caption did not in fact define the open
        # triangle, which marks a distractor. A key in the caption is a key the
        # reader has to leave the picture to use, and one in a caption that gets
        # trimmed for space is a key that quietly stops existing.
        #
        # `legend_html` already had the entry. Only the hero rendered without it.
        # The second half of the old reasoning survives: this is a compact key of
        # symbol-then-meaning rows, not the flat render's header block.
        hero = Path(args.hero).expanduser()
        hero.parent.mkdir(parents=True, exist_ok=True)
        with tempfile.TemporaryDirectory() as td:
            tmp_html = Path(td) / "hero.html"
            pn.Column(
                pn.pane.HoloViews(hero_fig if hero_fig is not None else fig),
                pn.pane.HTML(legend, sizing_mode="stretch_width"),
            ).save(str(tmp_html))
            if _render_png(tmp_html, hero):
                written.append(hero)
            else:
                print("(no hero PNG: pip install playwright && python -m "
                      "playwright install chromium)", file=sys.stderr)

    print(report)
    print("\nwrote " + "\n      ".join(str(w) for w in written))
    return 0


def _render_png(html_path: Path, png_path: Path, *, wait_ms: int = 3500,
                scale: int = 3) -> bool:
    """Flatten the page to a PNG. Returns False rather than raising when the
    browser is unavailable — a missing screenshot must not cost you the figure.

    ``scale`` is the device pixel ratio the page is rendered at, and it is what
    decides whether the figure survives being zoomed into. This view is read by
    zooming — a 45-minute recording at 1180 CSS px puts a 0.36 s jitter well
    under one pixel, and the reason to open it at all is usually to look closely
    at one event. At 2 the raster ticks and the lane markers go soft before you
    get there (Tony, 2026-08-15), so 3 is the default and the cost is file size:
    roughly 0.7 MB at 2, 1.4 MB at 3.
    """
    try:
        from playwright.sync_api import sync_playwright
    except ImportError:
        return False
    try:
        with tempfile.TemporaryDirectory() as td:
            tmp = Path(td) / "shot.png"
            with sync_playwright() as pw:
                browser = pw.chromium.launch()
                page = browser.new_page(viewport={"width": 1180, "height": 1400},
                                   device_scale_factor=scale)
                page.goto(html_path.resolve().as_uri())
                page.wait_for_timeout(wait_ms)      # bokeh draws after load
                # CROP TO THE FIGURE, not to the viewport. `full_page` returns
                # whichever is taller, so a figure shorter than the 1400 px
                # viewport comes back with the difference as white — and the
                # raster is deliberately short now, which put a quarter-page of
                # blank under the hero's bottom trace.
                #
                # The measurement is taken with the viewport SHRUNK first, and
                # both tricks that suggest themselves fail: Panel's wrappers
                # stretch to the viewport, so measuring a container just hands
                # the viewport height back, and Bokeh 3 draws into a shadow root,
                # so `querySelectorAll('canvas')` comes back EMPTY. Against a
                # short viewport nothing has room to stretch and `scrollHeight`
                # is the content. Nothing here is responsive — every plot carries
                # a fixed width and height — so the resize does not reflow the
                # figure. An implausible reading leaves the untrimmed shot, which
                # is still a correct figure.
                page.set_viewport_size({"width": 1180, "height": 320})
                page.wait_for_timeout(400)
                h = page.evaluate("document.documentElement.scrollHeight")
                w = page.evaluate("document.documentElement.scrollWidth")
                clip = None
                if all(isinstance(v, (int, float)) for v in (h, w)) \
                        and 200 <= h <= 20000 and 200 <= w <= 8000:
                    clip = {"x": 0, "y": 0, "width": float(w), "height": float(h)}
                page.screenshot(path=str(tmp), full_page=True, clip=clip)
                browser.close()
            os.replace(tmp, png_path)
        return True
    except Exception as exc:                        # noqa: BLE001
        print(f"(PNG render failed: {type(exc).__name__}: {exc})", file=sys.stderr)
        return False


if __name__ == "__main__":
    raise SystemExit(main())
