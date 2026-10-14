"""Figure 7: calling events against counting them, on the page's simulated recordings.

The measure never says which onsets formed a moment. A detector does: CoactDetect counts the
distinct cells with an onset in each 2 s bin and calls a bin whose count beats a circular-shift
null measured locally, in 60 s around it. That is the window-by-window version of what the
measure adds up over a whole recording. This script runs both on the same recordings:

- **CoactDetect** at the bench's shipped operating point (``bench.OPERATING_POINTS["coact"]``,
  binned), with its participation minimum set to each recording's own ADR-0008 floor
  (``event_floor.window_floor``), as the bench sets it.
- **The measure**, exactly as the page's other figures run it (``explain_coordination_share``).

From the calls, the share of events coordinated is the onsets inside a called span over all
onsets. A planted moment counts as called when a call's span comes within the bench's match
tolerance (``score.TOL_SEC``) of it; one call can cover both moments of a close pair.

Simulated recordings only; no real recording is read.

Run: python docs/learned/coordination_share_explainer/compare_with_calls.py [--also]
  Writes the figure and ``calls.json`` to the page's darkroom folder; ``--also`` copies both
  beside this script.
"""
from __future__ import annotations

import argparse
import json
import shutil
import sys
from concurrent.futures import ProcessPoolExecutor
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

import explain_coordination_share as e  # noqa: E402  (puts src/ and tools/ on the path)

import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402

import measure_coordination_rates as mcr  # noqa: E402
from bugarach import bench, event_floor  # noqa: E402
from bugarach.detectors.coact import coact_detect  # noqa: E402
from bugarach.score import TOL_SEC  # noqa: E402

COACT = bench.OPERATING_POINTS["coact"].params
FIG1_SEED, FIG1_START = 13, 1800.0          # Figure 1's five minutes (numbers.json, figure 1)
CALLED, MISSED = e.GREEN, "#d63a2f"
TICK = {"planted\nquiet": "planted\nquiet", "planted\nbusy": "planted\nbusy",
        "nothing\nplanted": "nothing\nplanted",
        "nothing planted,\n1-min busy stretch": "nothing\nplanted,\n1-min\nstretch",
        "nothing planted,\n5-min busy stretch": "nothing\nplanted,\n5-min\nstretch"}
SETS = {
    # label: (recording keywords, background)
    "planted\nquiet": (dict(), e.QUIET),
    "planted\nbusy": (dict(), e.BUSY),
    "nothing\nplanted": (dict(n_total=0), e.QUIET),
    "nothing planted,\n1-min busy stretch": (dict(n_total=0, hot_window=(1200.0, 1260.0),
                                                  hot_rate_hz=e.HOT["hot_rate_hz"], ramp_sec=0.0), e.QUIET),
    "nothing planted,\n5-min busy stretch": (dict(n_total=0, hot_window=(1200.0, 1500.0),
                                                  hot_rate_hz=e.HOT["hot_rate_hz"], ramp_sec=0.0), e.QUIET),
}


def run_one(job):
    """One recording: CoactDetect's calls and the measure's cumulants."""
    label, seed = job
    kw, bg = SETS[label]
    rec = e.recording(seed, bg_hz=bg, **kw)
    floor = _floor(rec, label, seed)
    secs = [t * e.DT for t in rec["trains"]]
    lo, hi, share = _calls(secs, floor, seed)
    near = [np.flatnonzero((lo - TOL_SEC <= t) & (hi + TOL_SEC >= t)) for t in rec["times"]]
    used = set(np.concatenate(near).tolist()) if near else set()
    out = dict(floor=int(floor), spans=list(zip(lo.tolist(), hi.tolist())), call_share=share,
               called=[bool(n.size) for n in near], ks=rec["ks"].tolist(),
               false_calls=int(lo.size - len(used)))
    if "hot_window" in kw:
        # The floor is the recording's own, so a busy stretch raises it. Also call at the floor the
        # same recording has without its stretch, to see what the floor alone is doing.
        calm = _floor(e.recording(seed, bg_hz=bg, n_total=0), "nothing\nplanted", seed)
        lo2, _, share2 = _calls(secs, calm, seed)
        out.update(floor_without_stretch=int(calm), calls_at_that_floor=int(lo2.size),
                   call_share_at_that_floor=share2)
    out.update(m=mcr.measure(rec["trains"], rec["L"], np.random.RandomState(seed)),
               truth=rec["truth"])
    return out


def _floor(rec, label, seed):
    return event_floor.window_floor([np.unique(t) for t in rec["trains"]], rec["L"], e.DT,
                                    key=("coordination-share-explainer", label, seed)).floor


def _calls(secs, floor, seed):
    """CoactDetect's call spans and the share of onsets inside them."""
    det = coact_detect(secs, (0.0, e.T), **COACT, min_rois=floor, rng_seed=seed)
    lo, hi = det.onset_sec, det.onset_sec + det.width_sec
    onsets = np.concatenate(secs)
    inside = np.zeros(onsets.size, bool)
    for a, b in zip(lo, hi):
        inside |= (onsets >= a) & (onsets < b)
    return lo, hi, float(inside.mean()) if onsets.size else 0.0


def figure7(out, date, res):
    planted = res["planted\nquiet"] + res["planted\nbusy"]
    pairs = [(r["m"], r["truth"]) for r in planted]
    measure = {"planted\nquiet": e.recovered(pairs)[:len(e.SEEDS)],
               "planted\nbusy": e.recovered(pairs)[len(e.SEEDS):]}
    run = [(r["m"], r["truth"]) for r in res["planted\nquiet"]]
    for label in list(SETS)[2:]:
        measure[label] = e.in_run([(r["m"], r["truth"]) for r in res[label]], run)

    rec = e.recording(FIG1_SEED)
    one = res["planted\nquiet"][e.SEEDS.index(FIG1_SEED)]
    t0, t1 = FIG1_START, FIG1_START + 300.0

    fig = plt.figure(figsize=(12, 12))
    gs = fig.add_gridspec(3, 2, height_ratios=[0.9, 5, 5.2], width_ratios=[1.5, 1],
                          hspace=0.32, wspace=0.25)
    lane = fig.add_subplot(gs[0, :])
    for t, hit in zip(rec["times"], one["called"]):
        if t0 <= t <= t1:
            lane.scatter([t], [1.0], marker="v", s=40, color=CALLED if hit else MISSED, zorder=3)
    shown = [(a, b) for a, b in one["spans"] if b >= t0 and a <= t1]
    for a, b in shown:
        lane.fill_between([a, b], -0.25, 0.25, color=e.INK, lw=0)
    lane.scatter([], [], marker="v", s=40, color=CALLED, label="planted moment, called")
    lane.scatter([], [], marker="v", s=40, color=MISSED, label="planted moment, missed")
    lane.fill_between([], [], color=e.INK, label="CoactDetect call (its span)")
    lane.set_xlim(t0, t1)
    lane.set_ylim(-0.5, 1.4)
    lane.set_yticks([1.0, 0.0], ["planted", f"CoactDetect · {len(shown)} calls"])
    lane.tick_params(axis="y", length=0)
    lane.tick_params(axis="x", bottom=False, labelbottom=False)
    for s in lane.spines.values():
        s.set_visible(False)
    lane.legend(loc="lower left", bbox_to_anchor=(0, 1.0), ncol=3, frameon=False)
    e.letter(lane, "A", x=-0.13, y=0.6)

    ax = fig.add_subplot(gs[1, :], sharex=lane)
    for r, tr in enumerate(rec["trains"]):
        on = tr * e.DT
        on = on[(on >= t0) & (on <= t1)]
        ax.vlines(on, r + 0.6, r + 1.4, color=e.INK, lw=1.2)
    ax.set_ylim(e.N + 0.7, 0.3)
    ax.set_yticks([1, 8, 16, 24, 32])
    ax.set_ylabel(f"cell · {e.N} cells")
    e.time_axis(ax, t0, t1)
    ax.set_xlabel("time in the recording (Figure 1's five minutes)")

    bx = fig.add_subplot(gs[2, 0])
    stats = {}
    labels = list(SETS)
    for i, label in enumerate(labels):
        truth = np.array([r["truth"]["share"] for r in res[label]]) * 100
        meas = np.asarray(measure[label]) * 100
        calls = np.array([r["call_share"] for r in res[label]]) * 100
        rng = np.random.RandomState(i)
        marks = [(-0.27, truth, e.MUTED, "_", e.MUTED), (-0.09, meas, e.BLUE, "o", e.BLUE),
                 (0.09, calls, e.ORANGE, "o", "none")]
        calm = None
        if "call_share_at_that_floor" in res[label][0]:
            calm = np.array([r["call_share_at_that_floor"] for r in res[label]]) * 100
            marks.append((0.27, calm, e.ORANGE, "^", "none"))
        for dx, v, colour, mk, face in marks:
            ok = np.isfinite(v)
            bx.scatter(i + dx + rng.uniform(-0.06, 0.06, ok.sum()), v[ok], s=16, marker=mk,
                       color=colour, facecolors=face, lw=1.2, alpha=0.8)
            if ok.any():
                bx.plot([i + dx - 0.1, i + dx + 0.1], [np.median(v[ok])] * 2, color=e.INK, lw=2)
        stats[label.replace("\n", " ")] = dict(
            planted_median_pct=float(np.median(truth)), measure_median_pct=e.q(meas, 50),
            measure_answers=int(np.isfinite(meas).sum()), calls_median_pct=float(np.median(calls)),
            calls_per_recording_median=float(np.median([len(r["spans"]) for r in res[label]])),
            false_calls_per_recording_median=float(np.median([r["false_calls"] for r in res[label]])),
            floor_cells_median=float(np.median([r["floor"] for r in res[label]])))
        if calm is not None:
            stats[label.replace("\n", " ")].update(
                floor_without_stretch_median=float(np.median(
                    [r["floor_without_stretch"] for r in res[label]])),
                calls_at_that_floor_median=float(np.median(
                    [r["calls_at_that_floor"] for r in res[label]])),
                call_share_at_that_floor_median_pct=float(np.median(calm)))
    bx.axhline(0, color=e.GRID, lw=1, zorder=0)
    bx.set_xticks(range(len(labels)), [TICK[lab] for lab in labels], fontsize=9.5)
    bx.set_ylabel("share of onsets coordinated (%)")
    bx.scatter([], [], marker="_", s=60, color=e.MUTED, label="planted (the right answer)")
    bx.scatter([], [], marker="o", s=20, color=e.BLUE, label="the measure (no calls)")
    bx.scatter([], [], marker="o", s=20, facecolors="none", color=e.ORANGE,
               label="from CoactDetect's calls")
    bx.scatter([], [], marker="^", s=20, facecolors="none", color=e.ORANGE,
               label="calls at the floor without the stretch")
    bx.plot([], [], color=e.INK, lw=2, label="median")
    bx.legend(loc="upper right", frameon=False, fontsize=9)
    e.letter(bx, "B", x=-0.2)

    cx = fig.add_subplot(gs[2, 1])
    called = {}
    for j, (label, colour) in enumerate((("planted\nquiet", e.INK), ("planted\nbusy", e.MUTED))):
        fr = []
        for k in e.SIZES:
            hits = [h for r in res[label] for h, kk in zip(r["called"], r["ks"]) if kk == k]
            fr.append(100 * np.mean(hits))
        called[label.replace("\n", " ")] = dict(zip([f"{k} cells" for k in e.SIZES], fr))
        x = np.arange(len(e.SIZES)) + (j - 0.5) * 0.36
        cx.bar(x, fr, width=0.34, color=colour, label=label.replace("planted\n", "") + " background")
    floors = {lab.replace("\n", " "): sorted({r["floor"] for r in res[lab]})
              for lab in ("planted\nquiet", "planted\nbusy")}
    cx.set_xticks(range(len(e.SIZES)), [f"{k} cells" for k in e.SIZES])
    cx.set_xlabel("cells joining the moment")
    cx.set_ylabel("planted moments called (%)")
    cx.set_ylim(0, 105)
    cx.legend(loc="upper right", frameon=False, fontsize=9)
    e.letter(cx, "C", x=-0.2)

    name = e.save(fig, out, "coordinated-share-fig7-calling-events", date,
                  "Figure 7. Calling events against counting them")
    return name, dict(window_sec=[t0, t1], seed=FIG1_SEED, calls_in_view=len(shown),
                      shares=stats, called_by_size_pct=called, floors_cells=floors,
                      coact=COACT, match_tolerance_sec=TOL_SEC)


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--out", type=Path, default=None,
                    help="default: <darkroom>/bugarach/2026-10-14-coordination-share-explainer")
    ap.add_argument("--also", action="store_true", help="also write the repo copy beside this script")
    ap.add_argument("--date", default=e.PAGE_DATE)
    ap.add_argument("--jobs", type=int, default=8)
    a = ap.parse_args()
    if a.out is None:
        from bugarach.paths import darkroom
        a.out = darkroom() / "2026-10-14-coordination-share-explainer"
    a.out.mkdir(parents=True, exist_ok=True)
    jobs = [(label, s) for label in SETS for s in e.SEEDS]
    with ProcessPoolExecutor(a.jobs) as pool:
        flat = list(pool.map(run_one, jobs))
    res = {label: [r for (lab, _), r in zip(jobs, flat) if lab == label] for label in SETS}
    name, stats = figure7(a.out, a.date, res)
    record = dict(note="simulated recordings only; no real recording read", file=name, numbers=stats)
    (a.out / "calls.json").write_text(json.dumps(record, indent=1, default=float) + "\n")
    if a.also:
        for f in (name, "calls.json"):
            shutil.copy2(a.out / f, HERE / f)
    print(json.dumps(record, indent=1, default=float))


if __name__ == "__main__":
    main()
