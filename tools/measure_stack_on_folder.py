#!/usr/bin/env python3
"""stack against count (sliding) on the baseline windows of one export folder.

    python tools/measure_stack_on_folder.py --folder <name or path> --label <short name>

The real-recording half of ``tools/measure_stack.py``. Per recording and stream (fast, slow,
combined), on the folder's declared **baseline** window only: the window's ADR-0008 floor,
``count_sliding`` at the bench's operating point for that stream, and ``stack`` with the same
reference window, merge gap and floor. There is no planted truth, so nothing is scored: what is
reported is how many calls each rule makes, how many it makes on rigid shifts of the same
window, which calls the two share, and which window width won each of ``stack``'s.

**Output goes to the darkroom and nowhere else** (``<darkroom>/2026-10-07-stack/<label>/``).
Numbers and figures derived from real recordings are not committed (FOUNDATIONS §5), so this
tool takes no ``--also``.

The folder is named on the command line and resolved by ``bugarach.dataset.require``, so a
folder ``current_export.toml`` declares passes the same archive, contamination and confirmation
gates it would by role. A folder that declares regions is read on its baseline window or not at
all; treatment windows are never read (FOUNDATIONS §9).
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

import measure_stack as ms  # noqa: E402

TAG = "stack-on-folder-2026-10-07"
MATCH_SEC = 2.5
"""Two calls are the same call when their spans come within this many seconds: the bench's
match tolerance."""


def load(folder: Path, stream: str):
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
    return recs, skipped


def shared(a_on, a_w, b_on, b_w) -> np.ndarray:
    """For each call of ``a``: does any call of ``b`` come within :data:`MATCH_SEC` of it?"""
    out = np.zeros(len(a_on), bool)
    for i, (o, w) in enumerate(zip(a_on, a_w)):
        out[i] = bool(np.any((np.asarray(b_on) <= o + w + MATCH_SEC)
                             & (np.asarray(b_on) + np.asarray(b_w) >= o - MATCH_SEC)))
    return out


def measure(rec, stream: str, label: str) -> dict:
    from bugarach import event_floor as ef
    from bugarach.detectors import sliding as sl
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
    b_in_a = shared(b.onset_sec, b.width_sec, a.onset_sec, a.width_sec)
    a_in_b = shared(a.onset_sec, a.width_sec, b.onset_sec, b.width_sec)
    starts, ends, S = sl.pieces(trains, float(op["win_sec"]), *ext)
    hours = L * dt / 3600.0
    nh = b.null["hours"] or float("nan")
    return dict(
        recording_id=rec.recording_id, mouse=rec.mouse, group=rec.group, stream=stream, dt=dt,
        window_sec=L * dt, window_start_sec=a0 * dt, n_roi=len(frames),
        n_onsets=int(sum(len(f) for f in frames)), floor=floor.floor,
        chance_floor=floor.chance_floor, floor_stable=bool(floor.stable),
        calls={"count_sliding": int(a.n_events), "stack": int(b.n_events)},
        calls_per_hour={"count_sliding": a.n_events / hours, "stack": b.n_events / hours},
        rigid_shift_calls_per_hour={"count_sliding": (b.null["ref_calls"] or 0) / nh,
                                    "stack": (b.null["stack_calls"] or 0) / nh},
        shared_calls=int(b_in_a.sum()), stack_only=int((~b_in_a).sum()),
        count_sliding_only=int((~a_in_b).sum()),
        alpha=b.alpha, thresholds={f"{w:g}": k for w, k in b.thresholds.items()},
        stability_sec=b.stability_sec.tolist(),
        stability_of_stack_only=b.stability_sec[~b_in_a].tolist(),
        nrois_of_stack_only=b.nrois[~b_in_a].tolist(),
        onsets={"count_sliding": a.onset_sec.tolist(), "stack": b.onset_sec.tolist()},
        stack_only_mask=(~b_in_a).tolist(),
        trace=dict(t=np.c_[starts, ends].ravel().tolist(), count=np.c_[S, S].ravel().tolist(),
                   win_sec=float(op["win_sec"])))


def figures(rows, out: Path, label: str) -> list[Path]:
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    from bugarach.time_axis import label as tlabel
    from bugarach.time_axis import ticks as tticks

    made = []
    streams = [s for s in ms.STREAMS if any(r["stream"] == s for r in rows)]
    # One page per stream: every recording's count, each rule's calls in lanes above it.
    for n, stream in enumerate(streams, start=1):
        rs = [r for r in rows if r["stream"] == stream]
        fig = plt.figure(figsize=(13, 2.5 * len(rs)))
        gs = fig.add_gridspec(2 * len(rs), 1, height_ratios=(0.75, 1.6) * len(rs), hspace=0.45)
        for k, r in enumerate(rs):
            lane = fig.add_subplot(gs[2 * k])
            trace = fig.add_subplot(gs[2 * k + 1], sharex=lane)
            on_a = np.asarray(r["onsets"]["count_sliding"])
            on_b = np.asarray(r["onsets"]["stack"])
            only = np.asarray(r["stack_only_mask"], bool)
            lane.plot(on_a, np.zeros(on_a.size), "v", color=ms.INK["count_sliding"], ms=5)
            lane.plot(on_b[~only], np.ones((~only).sum()), "v", color=ms.INK["stack"], ms=5)
            lane.plot(on_b[only], np.full(only.sum(), 2), "v", color="#1f5fa8", ms=5)
            lane.set_yticks([0, 1, 2], [f"count (sliding) · {on_a.size} calls",
                                        f"stack, shared · {(~only).sum()} calls",
                                        f"stack only · {only.sum()} calls"], fontsize=7)
            lane.set_ylim(-0.6, 2.6)
            lane.tick_params(labelbottom=False, length=0)
            for side in ("top", "right", "bottom"):
                lane.spines[side].set_visible(False)
            trace.plot(r["trace"]["t"], r["trace"]["count"], color="k", lw=0.5)
            trace.axhline(r["floor"], color="#888888", lw=0.6, ls=":")
            trace.set_ylabel(f"{r['recording_id']}\n{stream} · {r['n_roi']} ROI\n"
                             f"ROIs with an onset in {r['trace']['win_sec']:g} s", fontsize=7)
            tk = tticks(0.0, r["window_sec"])
            trace.set_xticks(tk, [tlabel(t) for t in tk] if k == len(rs) - 1 else [""] * len(tk))
            trace.set_xlim(0, r["window_sec"])
        made.append(out / f"fig{n}_{stream}_calls.png")
        fig.savefig(made[-1], dpi=150, bbox_inches="tight")
        plt.close(fig)

    # Calls per recording, each rule against its own rigid shifts; and the winning widths.
    fig, axes = plt.subplots(2, len(streams), figsize=(5.2 * len(streams), 6.4), squeeze=False)
    for c, stream in enumerate(streams):
        rs = [r for r in rows if r["stream"] == stream]
        x = np.arange(len(rs))
        ax = axes[0, c]
        for j, name in enumerate(ms.DETECTORS):
            ax.bar(x + (j - 0.5) * 0.38, [r["calls_per_hour"][name] for r in rs], 0.38,
                   color=ms.INK[name], label=ms.NAME[name])
            ax.plot(x + (j - 0.5) * 0.38, [r["rigid_shift_calls_per_hour"][name] for r in rs],
                    "_", color="k", ms=14, mew=1.5,
                    label="the same rule on rigid shifts" if j == 0 else None)
        ax.set_xticks(x, [f"{r['recording_id']}\nfloor {r['floor']} ROI" for r in rs],
                      fontsize=6, rotation=30)
        ax.set_ylabel(f"calls per hour · {stream} baseline", fontsize=8)
        if c == 0:
            ax.legend(frameon=False, fontsize=7)
        ax = axes[1, c]
        widths = sorted({w for r in rs for w in r["stability_sec"]} | {0.25, 0.5, 1.0, 2.0})
        xs = np.arange(len(widths))
        both = sum((list(np.asarray(r["stability_sec"])[~np.asarray(r["stack_only_mask"], bool)])
                    for r in rs), [])
        only = sum((r["stability_of_stack_only"] for r in rs), [])
        for j, (vals, col, lab) in enumerate(((both, ms.INK["stack"], "shared with count (sliding)"),
                                              (only, "#1f5fa8", "stack only"))):
            ax.bar(xs + (j - 0.5) * 0.38, [int(np.isclose(vals, w).sum()) for w in widths], 0.38,
                   color=col, label=f"{lab} ({len(vals)} calls)")
        ax.set_xticks(xs, [f"{w:g} s" for w in widths])
        ax.set_xlabel(f"winning window width · {stream}", fontsize=8)
        ax.set_ylabel("stack's calls (count)", fontsize=8)
        ax.legend(frameon=False, fontsize=7)
    fig.tight_layout()
    made.append(out / f"fig{len(streams) + 1}_rates_and_widths.png")
    fig.savefig(made[-1], dpi=150)
    plt.close(fig)
    return made


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--folder", required=True, help="an export folder, by name or path")
    ap.add_argument("--label", required=True,
                    help="short name for the output subfolder, e.g. sept-pilot-4x")
    ap.add_argument("--out", type=Path, default=None,
                    help=f"output folder (default: <darkroom>/{ms.FOLDER}/<label>)")
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
        recs, sk = load(folder, stream)
        skipped[stream] = sk
        rows += [measure(r, stream, a.label) for r in recs]
    made = figures(rows, out, a.label)
    slim = [{k: v for k, v in r.items() if k != "trace"} for r in rows]
    (out / "summary.json").write_text(json.dumps(
        dict(folder=folder.name, label=a.label, tag=TAG, match_sec=MATCH_SEC, skipped=skipped,
             rows=slim), indent=1))

    for r in rows:
        print(f"{r['stream']:9s} {r['recording_id']} {r['n_roi']:3d} ROI floor {r['floor']:2d}  "
              f"calls {r['calls']}  rigid/h "
              f"{ {k: round(v, 2) for k, v in r['rigid_shift_calls_per_hour'].items()} }  "
              f"shared {r['shared_calls']} stack-only {r['stack_only']} "
              f"count-only {r['count_sliding_only']}  needs {r['thresholds']}")
    print(*made, sep="\n")


if __name__ == "__main__":
    main()
