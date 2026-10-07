#!/usr/bin/env python3
"""stack, count (sliding) and the best detectors on record, on one folder's baseline windows.

    python tools/measure_stack_on_folder.py --folder <name or path> --label <short name>

The real-recording half of ``tools/measure_stack.py``. Per recording and stream (fast, slow,
combined), on the folder's declared **baseline** window only:

* the window's ADR-0008 floor, from its own rigid-shift null;
* ``count_sliding`` at the bench's operating point for that stream, and ``stack`` with the same
  reference window, merge gap and floor;
* for comparison, CoactDetect and LoCo at their shipped operating points with the same floor,
  and ``chorus_norm`` at its picked checkpoint, shown the baseline window alone.

There is no planted truth, so nothing is scored. What is reported is how many calls each
detector makes, how ``stack``'s calls and ``count_sliding``'s overlap, and which window width
won each of ``stack``'s. The overlap is always said in words:

* **called by both**: a call of ``stack`` that ``count_sliding`` also made;
* **only stack**: a call of ``stack`` that ``count_sliding`` did not make;
* **only count (sliding)**: a call of ``count_sliding`` that ``stack`` did not make.

Figure 1 is the summary; Figures 2 onward are one raster page per recording and stream, drawn
with ``bugarach.ui.diagnostic``: nothing on the raster, one lane per detector above it.

**Output goes to the darkroom and nowhere else** (``<darkroom>/2026-10-07-stack/<label>/``).
Numbers and figures derived from real recordings are not committed (FOUNDATIONS §5), so this
tool takes no ``--also`` and refuses an output path inside the repository.

The folder is named on the command line and resolved by ``bugarach.dataset.require``, so a
folder ``current_export.toml`` declares passes the same archive, contamination and confirmation
gates it would by role. A folder that declares regions is read on its baseline window or not at
all; treatment windows are never read (FOUNDATIONS §9).

⚠ **Retired with the first form of stack, 2026-10-07**, for the reason in
``tools/measure_stack.py``. ``main`` refuses; the September pilot result was made at ``8646eb4``.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(Path(__file__).resolve().parent))

import make_stack_rasters as rasters  # noqa: E402
import measure_stack as ms  # noqa: E402

TAG = "stack-on-folder-2026-10-07"
MATCH_SEC = 2.5
"""Two calls are the same call when their spans come within this many seconds: the bench's
match tolerance."""
RNG_SEED = 20260706
"""The surrogate seed the bench and the folder run give CoactDetect and LoCo."""
PARTICIPANT_PAD_SEC = 1.0
"""A call's participants are the ROIs with an onset within this many seconds of its span:
``tools/detect_with_floors.py``'s rule (ADR-0010 part 6), so the viewer's hover reads the same
way for these calls as for every other run's."""
VIEWER_STREAMS = ("fast", "slow")
ONLY = "stack_only"
LANE_NAME = {**ms.NAME, "stack": "stack (every call)",
             ONLY: "only stack (count (sliding) did not call)"}
LANE_INK = {**ms.INK, ONLY: "#1f5fa8"}
OVERLAP = ("called by both", "only stack", "only count (sliding)")


def load(folder: Path, stream: str):
    """``[(slice, recording)]`` for ``stream``, each recording on its baseline window."""
    from dataclasses import replace

    from bugarach import surrogate_stats as ss
    from bugarach.combined import has_sources, stream_of
    from bugarach.io import load_folder

    slices = load_folder(folder)
    if stream == "combined":
        slices = [replace(s, streams={**s.streams, "combined": stream_of(s, "combined")})
                  if has_sources(s) else s for s in slices]
    recs, skipped = ss.recordings_from_slices(slices, stream)
    refused = [r.recording_id for r in recs if not r.window_source.startswith("baseline region")]
    if refused:
        raise SystemExit(f"refusing non-baseline windows in {stream}: {refused}")
    by_id = {s.slice_id: s for s in slices}
    return [(by_id[r.recording_id], r) for r in recs], skipped


def near(a_on, a_w, b_on, b_w) -> np.ndarray:
    """For each call of ``a``: does any call of ``b`` come within :data:`MATCH_SEC` of it?"""
    b_on, b_w = np.asarray(b_on, float), np.asarray(b_w, float)
    return np.array([bool(np.any((b_on <= o + w + MATCH_SEC) & (b_on + b_w >= o - MATCH_SEC)))
                     for o, w in zip(a_on, a_w)], dtype=bool)


def best_detectors(s, stream: str, trains, ext, t0: float, floor: int) -> tuple[dict, dict]:
    """CoactDetect, LoCo and chorus_norm on the baseline window: ``({name: (onsets, widths)},
    {name: why it did not run})``, onsets in seconds from the window's start."""
    from bugarach.detectors.coact import coact_detect
    from bugarach.detectors.loco import loco_detect

    mod = ms.bench_module(stream)
    out, failed = {}, {}
    try:
        p = {**mod.OPERATING_POINTS["coact"].params, "min_rois": floor, "rng_seed": RNG_SEED}
        d = coact_detect(trains, ext, **p)
        out["coact"] = (np.asarray(d.onset_sec, float), np.asarray(d.width_sec, float))
    except Exception as e:                                  # noqa: BLE001
        failed["coact"] = f"{type(e).__name__}: {e}"
    try:
        # LoCo takes the recording and windows it by region; keep its baseline-window calls.
        p = {**mod.OPERATING_POINTS["loco"].params, "min_rois": floor, "rng_seed": RNG_SEED}
        d = loco_detect(s, **p).streams[stream]
        on, w = np.asarray(d.onset_sec, float) - t0, np.asarray(d.width_sec, float)
        keep = (on >= ext[0]) & (on <= ext[1])
        out["loco"] = (on[keep], w[keep])
    except Exception as e:                                  # noqa: BLE001
        failed["loco"] = f"{type(e).__name__}: {e}"
    try:
        d = ms.chorus(stream).predict(s, stream=stream, extent=(t0, t0 + ext[1]))[0]
        out["chorus_norm"] = (np.asarray(d.onset_sec, float) - t0,
                              np.asarray(d.width_sec, float))
    except Exception as e:                                  # noqa: BLE001
        failed["chorus_norm"] = f"{type(e).__name__}: {e}"
    return out, failed


def measure(s, rec, stream: str, label: str) -> dict:
    from bugarach import event_floor as ef
    from bugarach.detectors.count import count_sliding_detect, stack_detect

    a0, a1 = rec.window
    L, dt = a1 - a0, float(rec.dt)
    frames = [np.asarray(t, np.int64) - a0 for t in rec.trains]
    floor = ef.window_floor(frames, L, dt, key=(TAG, label, stream, rec.recording_id))
    trains = [f.astype(float) * dt for f in frames]
    ext = (0.0, L * dt)
    op = ms.bench_module(stream).OPERATING_POINTS["count_sliding"].params
    a = count_sliding_detect(trains, ext, min_rois=floor.floor, **op)
    b = stack_detect(trains, ext, min_rois=floor.floor, frame_interval_sec=dt,
                     **ms.stack_params(op))
    b_in_a = near(b.onset_sec, b.width_sec, a.onset_sec, a.width_sec)
    a_in_b = near(a.onset_sec, a.width_sec, b.onset_sec, b.width_sec)
    best, failed = best_detectors(s, stream, trains, ext, a0 * dt, floor.floor)
    lanes = {**best,
             "count_sliding": (a.onset_sec, a.width_sec),
             "stack": (b.onset_sec, b.width_sec),
             ONLY: (b.onset_sec[~b_in_a], b.width_sec[~b_in_a])}
    hours = L * dt / 3600.0
    nh = b.null["hours"] or float("nan")
    # What the interactive viewer is given (write_viewer): LoCo, the best chorus variant and
    # stack, each call with its participants by detect_with_floors.py's one rule.
    t0 = a0 * dt
    try:
        d = ms.chorus(stream, ms.BEST_CHORUS).predict(s, stream=stream, extent=(t0, t0 + ext[1]))[0]
        best_chorus = (np.asarray(d.onset_sec, float) - t0, np.asarray(d.width_sec, float))
    except Exception as e:                                  # noqa: BLE001
        failed[ms.BEST_CHORUS] = f"{type(e).__name__}: {e}"
        best_chorus = None
    viewer = []
    for name, lane, extra in (("loco", lanes.get("loco"), None),
                              (ms.BEST_CHORUS, best_chorus, None),
                              ("stack", lanes["stack"], b.stability_sec)):
        if lane is None:
            continue
        for i, (o, w) in enumerate(zip(*lane)):
            lo, hi = o - PARTICIPANT_PAD_SEC, o + w + PARTICIPANT_PAD_SEC
            viewer.append(dict(
                detector=name, onset_sec=float(o) + t0, width_sec=float(w),
                n_roi=int(sum(bool(np.any((v >= lo) & (v <= hi))) for v in trains)),
                winning_width_sec=None if extra is None else float(extra[i])))
    return dict(
        _viewer=viewer,
        recording_id=rec.recording_id, mouse=rec.mouse, group=rec.group, stream=stream, dt=dt,
        window_sec=L * dt, window_start_sec=a0 * dt, n_roi=len(frames),
        n_onsets=int(sum(len(f) for f in frames)), floor=floor.floor,
        chance_floor=floor.chance_floor, floor_stable=bool(floor.stable),
        calls={n: int(len(v[0])) for n, v in lanes.items() if n != ONLY},
        calls_per_hour={n: len(v[0]) / hours for n, v in lanes.items() if n != ONLY},
        did_not_run=failed,
        rigid_shift_calls_per_hour={"count_sliding": (b.null["ref_calls"] or 0) / nh,
                                    "stack": (b.null["stack_calls"] or 0) / nh},
        overlap={"called by both": int(b_in_a.sum()), "only stack": int((~b_in_a).sum()),
                 "only count (sliding)": int((~a_in_b).sum())},
        alpha=b.alpha, thresholds={f"{w:g}": k for w, k in b.thresholds.items()},
        winning_width_sec={"called by both": b.stability_sec[b_in_a].tolist(),
                           "only stack": b.stability_sec[~b_in_a].tolist()},
        rois_in_only_stack_calls=b.nrois[~b_in_a].tolist(),
        _lanes=lanes, _slice=s)


def summary_figure(rows, out: Path) -> Path:
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    streams = [s for s in ms.STREAMS if any(r["stream"] == s for r in rows)]
    fig, axes = plt.subplots(2, len(streams), figsize=(6.2 * len(streams), 7.0), squeeze=False)
    for c, stream in enumerate(streams):
        rs = [r for r in rows if r["stream"] == stream]
        x = np.arange(len(rs))
        ax = axes[0, c]
        for j, name in enumerate(ms.DETECTORS):
            v = [r["calls_per_hour"].get(name, 0.0) for r in rs]
            ax.bar(x + (j - (len(ms.DETECTORS) - 1) / 2) * ms.BAR, v, ms.BAR,
                   color=ms.INK[name], label=ms.NAME[name])
        ax.set_xticks(x, [f"{r['recording_id']}\nfloor {r['floor']} ROIs" for r in rs],
                      fontsize=6, rotation=30)
        ax.set_ylabel(f"calls per hour · {stream} baseline", fontsize=8)
        if c == 0:
            ax.legend(frameon=False, fontsize=7)
        ax = axes[1, c]
        widths = [0.25, 0.5, 1.0, 2.0]
        xs = np.arange(len(widths))
        for j, (key, col) in enumerate((("called by both", ms.INK["stack"]),
                                        ("only stack", LANE_INK[ONLY]))):
            vals = sum((r["winning_width_sec"][key] for r in rs), [])
            ax.bar(xs + (j - 0.5) * 0.38, [int(np.isclose(vals, w).sum()) for w in widths], 0.38,
                   color=col, label=f"{key} ({len(vals)} calls)")
        ax.set_xticks(xs, [f"{w:g} s" for w in widths])
        ax.set_xlabel(f"window width that won the call · {stream}", fontsize=8)
        ax.set_ylabel("number of stack's calls", fontsize=8)
        ax.yaxis.get_major_locator().set_params(integer=True)
        ax.set_ylim(0, ax.get_ylim()[1] * 1.4)      # room for the legend above the bars
        ax.legend(frameon=False, fontsize=7,
                  title="stack's calls, by whether count (sliding) also made them",
                  title_fontsize=7)
    fig.tight_layout()
    p = out / "fig01_calls_and_winning_widths.png"
    fig.savefig(p, dpi=150)
    plt.close(fig)
    return p


def write_viewer(rows, out: Path) -> tuple[Path, Path]:
    """What the repository's interactive viewer needs to show these calls, as earlier runs left it
    (``tools/make_briefing.py``): ``detections.csv`` in the output contract
    (``bugarach.emit.COLUMNS``) and ``viewer.html``, a copy of the site's viewer
    (``docs/site/raster_viewer.html``). Nothing here draws anything; the viewer does.

    One lane per detector in the viewer: LoCo, the best chorus variant and stack. Fast and slow
    only, because the viewer builds its streams from the export folder's own and the combined
    stream is derived, never stored. Baseline windows only, as everything else this tool does.
    """
    import shutil

    from bugarach.emit import DetectedEvent, write_detections

    events = []
    for r in rows:
        if r["stream"] not in VIEWER_STREAMS:
            continue
        for c in r["_viewer"]:
            events.append(DetectedEvent(
                slice_id=r["recording_id"], stream=r["stream"], detector=c["detector"],
                mode="threshold" if c["detector"] != ms.BEST_CHORUS else None,
                onset_sec=c["onset_sec"], width_sec=c["width_sec"], strength=None,
                strength_unit=None, width_def=None, region_idx=1, region_label="baseline",
                n_roi=c["n_roi"],
                identity=dict(group_id=r["group"], window_kind="baseline", variant="own_floor",
                              own_floor=r["floor"], baseline_floor=r["floor"],
                              winning_width_sec=c["winning_width_sec"])))
    det = write_detections(events, out / "detections.csv")
    page = out / "viewer.html"
    shutil.copy2(ROOT / "docs" / "site" / "raster_viewer.html", page)
    return det, page


def main(argv=None):
    raise SystemExit(ms.RETIRED)
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--folder", required=True, help="an export folder, by name or path")
    ap.add_argument("--label", required=True,
                    help="short name for the output subfolder, e.g. sept-pilot-4x")
    ap.add_argument("--out", type=Path, default=None,
                    help=f"output folder (default: <darkroom>/{ms.FOLDER}/<label>)")
    ap.add_argument("--no-rasters", action="store_true", help="summary figure and numbers only")
    a = ap.parse_args(argv)

    from bugarach import dataset
    folder = Path(dataset.require(a.folder, want="export_folder", flag="--folder"))
    out = a.out
    if out is None:
        from bugarach.paths import darkroom
        out = darkroom(ms.FOLDER, a.label, create=True)
        if out is None:
            raise SystemExit("no darkroom found; pass --out")
    if ROOT in out.resolve().parents:
        raise SystemExit("output derived from real recordings does not go in the repository "
                         "(FOUNDATIONS §5)")
    out.mkdir(parents=True, exist_ok=True)

    rows, skipped = [], {}
    for stream in ms.STREAMS:
        pairs, sk = load(folder, stream)
        skipped[stream] = sk
        rows += [measure(s, r, stream, a.label) for s, r in pairs]
    made = [summary_figure(rows, out)]

    if not a.no_rasters:
        for n, r in enumerate(rows, start=2):
            t0 = r["window_start_sec"]
            ext = (t0, t0 + r["window_sec"])
            lanes = {k: (np.asarray(v[0], float) + t0, np.asarray(v[1], float))
                     for k, v in r["_lanes"].items()}
            counts = ", ".join(f"{LANE_NAME[k]} {len(v[0])} calls" for k, v in lanes.items())
            png = out / f"fig{n:02d}_raster_{r['stream']}_{r['recording_id']}.png"
            ok = rasters.page(
                lanes, r["_slice"].streams[r["stream"]], ext=ext, gt=None,
                raster_name="baseline", raster_height=240,
                heading=(f"Figure {n}. {r['recording_id']}, {r['stream']} stream, baseline "
                         f"window ({a.label}): what each detector called."),
                caption=(f"{r['n_roi']} ROIs; this window's floor is {r['floor']} ROIs. "
                         f"{counts}. The raster is the recording's baseline window, one row "
                         "per ROI (region of interest, a cell), one black mark per "
                         "calcium-event onset; nothing is drawn on it. Each lane above it "
                         "is one detector and each bar is one call. The bottom lane repeats "
                         "the calls only stack made, so they can be found by eye. There is "
                         "no planted truth here: a bar is a call, not a confirmed event."),
                png=png, not_run=tuple(r["did_not_run"]), names=LANE_NAME, colors=LANE_INK)
            if not ok:
                raise SystemExit(f"could not render {png.name} (playwright chromium missing?)")
            r["raster"] = dict(figure=n, file=png.name)
            made.append(png)

    made += list(write_viewer(rows, out))
    slim = [{k: v for k, v in r.items() if not k.startswith("_")} for r in rows]
    (out / "summary.json").write_text(json.dumps(
        dict(folder=folder.name, label=a.label, tag=TAG, match_sec=MATCH_SEC, skipped=skipped,
             chorus_norm_checkpoints={s: ms.chorus_path(s).name for s in ms.STREAMS},
             rows=slim), indent=1))

    for r in rows:
        print(f"{r['stream']:9s} {r['recording_id']} {r['n_roi']:3d} ROIs floor {r['floor']:2d}  "
              f"calls {r['calls']}  {r['overlap']}  did not run {list(r['did_not_run'])}")
    print(*made, sep="\n")


if __name__ == "__main__":
    main()
