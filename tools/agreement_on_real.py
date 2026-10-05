#!/usr/bin/env python3
"""How often the simple count rule and CoactDetect agree on real recordings, with no bench.

    python tools/agreement_on_real.py [--out <darkroom folder>] [--no-figures]

Tony, 2026-09-27, through the orchestrator: does the simple rule tie CoactDetect only because the
bench was built in its image? The realistic bench's spacing was measured as runs of the co-active
count at the floor, and its planted events are tight bursts, the shape a count sees best. This
reads two ``tools/detect_with_floors.py`` runs over the default dataset and compares calls
directly, window by window:

* ``run-count-and-coact-proposal/`` — count (binned), count (sliding) and CoactDetect at the
  settings in 064's count scoring (``064/count/fresh-realistic/candidates.json``);
* ``run-coact-shipped/`` — CoactDetect at its shipped setting, renamed ``coact_shipped`` here. The
  two CoactDetect settings against each other are the yardstick: how much two settings of one
  detector disagree.

**Agreement** is the scorer's matching rule (``score.score_detections``: greedy, closest pair
first, one to one, within ``score.TOL_SEC``, ties broken by distance between centres), applied
span to span: the gap between two calls is 0 when their spans overlap and the distance between
the nearer edges otherwise, and the tolerance is inclusive.

**The disagreements** are then described by what a local null should care about: each call's
participants against its window's ADR-0008 floor, its width, the event rate around it relative to
its window's, and whether the window's rate trends (last third against first third).

**What it writes** into ``--out``: ``merged/calls.csv`` and ``results.json`` (both runs, one
file), ``detections.csv`` (the viewer opens it), ``agreement.json`` (every number),
``README.md``, ``figure_*.png`` and ``viewer.html``. Nothing here is a treatment-effect claim; the
windows are grouped by treatment only to see where the detectors part.
"""
from __future__ import annotations

import argparse
import csv
import json
import math
import multiprocessing as mp
import shutil
import sys
import warnings
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path

import numpy as np

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / "tools"))
sys.path.insert(0, str(REPO / "src"))

from bugarach.groups import group_key, in_group_order  # noqa: E402
from bugarach.score import TOL_SEC, _spans  # noqa: E402

FOLDER_NAME = "2026-09-27-simple-vs-coact-real"
RUNS = (("run-count-and-coact-proposal", {}), ("run-coact-shipped", {"coact": "coact_shipped"}))
STREAMS = ("fast", "slow", "combined")
VIEWER_STREAMS = ("fast", "slow")               # the viewer derives no combined stream
LABEL_ORDER = ("baseline", "TTX", "senktide", "high K+", "wash")
#: The count form that stood in for "the simple rule" on each stream: the best within budget on
#: 064's realistic-bench search (064/count/README.md). Both forms are tabulated regardless.
SIMPLE = {"fast": "count", "slow": "count_sliding", "combined": "count_sliding"}
PAIRS = (("count", "coact"), ("count_sliding", "coact"), ("coact_shipped", "coact"))
NAME = {"count": "count (binned)", "count_sliding": "count (sliding)", "coact": "CoactDetect proposed",
        "coact_shipped": "CoactDetect shipped"}
EPS_SEC = 1e-6                                  # an inclusive tolerance, safe from rounding
LOCAL_SEC = 30.0                                # half-width of the stretch a call's local rate is read over
PAD_SEC = 1.0                                   # the call's own span, padded, left out of that stretch


def _n(k, one="call", many=None) -> str:
    """``1 call``, ``2 calls``: every count carries its unit, in the right number."""
    return f"{k} {one if k == 1 else (many or one + 's')}"


def _f(x, nd=2):
    return "—" if x is None or (isinstance(x, float) and not math.isfinite(x)) else f"{x:.{nd}f}"


# --------------------------------------------------------------------------------------------
# reading the runs
# --------------------------------------------------------------------------------------------

def read_run(run: Path, rename: dict) -> tuple[list[dict], list[dict], dict]:
    """(calls, windows, results) of one detect_with_floors run, detectors renamed."""
    def ren(rows):
        for r in rows:
            r["detector"] = rename.get(r["detector"], r["detector"])
        return rows
    with (run / "calls.csv").open(encoding="utf-8", newline="") as fh:
        calls = ren(list(csv.DictReader(fh)))
    with (run / "windows.csv").open(encoding="utf-8", newline="") as fh:
        wins = ren(list(csv.DictReader(fh)))
    res = json.loads((run / "results.json").read_text(encoding="utf-8"))
    for s, ch in (res.get("chosen") or {}).items():
        ch["detectors"] = {rename.get(d, d): v for d, v in (ch.get("detectors") or {}).items()}
    return calls, wins, res


def merge_runs(out: Path) -> tuple[list[dict], list[dict], dict]:
    calls, wins, results = [], [], None
    for name, rename in RUNS:
        c, w, r = read_run(out / name, rename)
        calls += c
        wins += w
        if results is None:
            results = r
        else:
            for s, ch in (r.get("chosen") or {}).items():
                results["chosen"].setdefault(s, {"detectors": {}, "chorus": {}})
                results["chosen"][s]["detectors"].update(ch["detectors"])
            results.setdefault("merged_from", []).append(name)
    results["merged_from"] = [n for n, _ in RUNS]
    return calls, wins, results


def write_merged(out: Path, calls: list[dict], results: dict) -> Path:
    """One calls.csv and results.json for both runs, then detections.csv beside the README."""
    from detect_with_floors import write_detections

    m = out / "merged"
    m.mkdir(exist_ok=True)
    cols = list(dict.fromkeys(k for c in calls for k in c))
    with (m / "calls.csv").open("w", encoding="utf-8", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=cols)
        w.writeheader()
        w.writerows(calls)
    (m / "results.json").write_text(json.dumps(results, indent=1, default=str), encoding="utf-8")
    return write_detections(m, out)


# --------------------------------------------------------------------------------------------
# agreement
# --------------------------------------------------------------------------------------------

def match_calls(a_on, a_w, b_on, b_w, tol: float = TOL_SEC) -> list[tuple[int, int]]:
    """One-to-one matches between two detectors' calls, as index pairs into the inputs: the
    scorer's rule (greedy, closest pair first, ties by distance between centres), span to span,
    with an inclusive tolerance."""
    a_on, b_on = np.asarray(a_on, float), np.asarray(b_on, float)
    if not a_on.size or not b_on.size:
        return []
    ao = np.argsort(a_on, kind="stable")
    bo = np.argsort(b_on, kind="stable")
    alo, ahi = _spans(a_on, a_w)
    blo, bhi = _spans(b_on, b_w)
    gap = np.maximum(0.0, np.maximum(blo[None, :] - ahi[:, None], alo[:, None] - bhi[None, :]))
    centre = np.abs(0.5 * (alo + ahi)[:, None] - 0.5 * (blo + bhi)[None, :])
    order = np.lexsort((centre.ravel(), gap.ravel()))
    ua, ub, pairs = set(), set(), []
    for flat in order:
        if gap.flat[flat] > tol + EPS_SEC:
            break
        i, j = divmod(int(flat), b_on.size)
        if i not in ua and j not in ub:
            ua.add(i)
            ub.add(j)
            pairs.append((int(ao[i]), int(bo[j])))
    return pairs


def nearest_gap(on, w, others_on, others_w) -> float | None:
    if not len(others_on):
        return None
    lo, hi = on, on + max(0.0, w)
    olo, ohi = _spans(others_on, others_w)
    return float(np.min(np.maximum(0.0, np.maximum(olo - hi, lo - ohi))))


def _num(x):
    try:
        v = float(x)
    except (TypeError, ValueError):
        return math.nan
    return v


def windows_of(wins: list[dict]) -> dict:
    """``(slice, region, stream) -> window facts`` from the floored rows of either run."""
    out = {}
    for r in wins:
        if r["variant"] != "own_floor":
            continue
        k = (r["slice_id"], r["region_idx"], r["stream"])
        out.setdefault(k, dict(slice_id=r["slice_id"], group=r["group"], region_idx=r["region_idx"],
                               label="baseline" if r["window_kind"] == "baseline" else r["label"],
                               stream=r["stream"], hours=_num(r["hours"]), n_roi=_num(r["n_roi"]),
                               own_floor=_num(r["own_floor"]), baseline_floor=_num(r["baseline_floor"]),
                               win_start=_num(r["win_start"]), win_end=_num(r["win_end"])))
    return out


def agreement(calls: list[dict], wins: dict, variant: str = "own_floor") -> list[dict]:
    """Per window and pair: calls both make, calls only one makes, and which calls those are."""
    by = defaultdict(lambda: defaultdict(list))
    for c in calls:
        if c["variant"] == variant:
            by[(c["slice_id"], c["region_idx"], c["stream"])][c["detector"]].append(c)
    rows = []
    for k, w in wins.items():
        per = by.get(k, {})
        for a, b in PAIRS:
            A, B = per.get(a, []), per.get(b, [])
            pairs = match_calls([_num(c["onset_sec"]) for c in A], [_num(c["width_sec"]) for c in A],
                                [_num(c["onset_sec"]) for c in B], [_num(c["width_sec"]) for c in B])
            ia, ib = {i for i, _ in pairs}, {j for _, j in pairs}
            rows.append(dict(w, a=a, b=b, variant=variant, both=len(pairs),
                             a_only=[c for i, c in enumerate(A) if i not in ia],
                             b_only=[c for j, c in enumerate(B) if j not in ib],
                             shared=[A[i] for i, _ in pairs], a_calls=A, b_calls=B))
    return rows


def tally(rows: list[dict], a: str, stream: str, *, by_group: bool) -> list[dict]:
    """Agreement per treatment (and group), for one pair and stream."""
    cells = defaultdict(lambda: dict(windows=0, hours=0.0, both=0, a_only=0, b_only=0))
    for r in rows:
        if r["a"] != a or r["stream"] != stream:
            continue
        key = (r["label"], r["group"] if by_group else "all")
        c = cells[key]
        c["windows"] += 1
        c["hours"] += r["hours"] if math.isfinite(r["hours"]) else 0.0
        c["both"] += r["both"]
        c["a_only"] += len(r["a_only"])
        c["b_only"] += len(r["b_only"])
    labels = [x for x in LABEL_ORDER if any(k[0] == x for k in cells)] + sorted(
        {k[0] for k in cells} - set(LABEL_ORDER))
    out = []
    for lab in labels:
        groups = ["all"] if not by_group else in_group_order({k[1] for k in cells if k[0] == lab})
        for g in groups:
            c = cells.get((lab, g))
            if not c:
                continue
            n = c["both"] + c["a_only"] + c["b_only"]
            out.append(dict(label=lab, group=g, **c,
                            agree_share=c["both"] / n if n else None,
                            a_only_share=c["a_only"] / n if n else None,
                            b_only_share=c["b_only"] / n if n else None))
    return out


# --------------------------------------------------------------------------------------------
# describing the disagreements
# --------------------------------------------------------------------------------------------

def _context_job(args):
    """Per recording: every window's rate trend, and each listed call's local rate."""
    i, folder, want = args
    from bugarach.combined import COMBINED, has_sources, stream_of
    from bugarach.detect_folder import _region_index, folder_analysis_windows
    from bugarach.detectors.rate import stream_trains
    from bugarach.io import load_folder

    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        s = load_folder(Path(folder))[i]
        s, windows = folder_analysis_windows(s)
    if s.slice_id not in want:
        return s.slice_id, {}, {}
    if has_sources(s) and COMBINED not in s.streams:
        s.streams[COMBINED] = stream_of(s, COMBINED)
    trend, local = {}, {}
    for w in windows:
        lo, hi = float(w.win_start), float(w.win_end)
        if hi <= lo:
            continue
        idx = str(_region_index(w))
        for sname in STREAMS:
            if sname not in s.streams:
                continue
            tr = stream_trains(s.streams[sname], (lo, hi))
            n = max(len(tr), 1)
            allon = np.sort(np.concatenate([t for t in tr if len(t)] or [np.zeros(0)]))
            third = (hi - lo) / 3.0
            r1 = np.sum(allon < lo + third) / (n * third)
            r3 = np.sum(allon >= hi - third) / (n * third)
            mean = allon.size / (n * (hi - lo))
            trend[f"{idx}|{sname}"] = dict(first=r1, last=r3, mean=mean,
                                           ratio=r3 / r1 if r1 > 0 else None)
            for key in want[s.slice_id].get((idx, sname), []):
                on, wd = key
                a, b = max(lo, on - LOCAL_SEC), min(hi, on + max(wd, 0.0) + LOCAL_SEC)
                ex0, ex1 = on - PAD_SEC, on + max(wd, 0.0) + PAD_SEC
                span = (b - a) - max(0.0, min(b, ex1) - max(a, ex0))
                k = np.sum((allon >= a) & (allon <= b) & ~((allon >= ex0) & (allon <= ex1)))
                rate = k / (n * span) if span > 0 else None
                local[f"{idx}|{sname}|{on:.4f}"] = dict(
                    rate=rate, rel=rate / mean if rate is not None and mean > 0 else None,
                    where=(on - lo) / (hi - lo))
    return s.slice_id, trend, local


def context(rows: list[dict], workers: int) -> tuple[dict, dict]:
    from bugarach import dataset
    from bugarach.io import load_folder

    want = defaultdict(lambda: defaultdict(list))
    for r in rows:
        if r["a"] != SIMPLE.get(r["stream"]):
            continue
        for c in r["a_only"] + r["b_only"] + r["shared"]:
            want[r["slice_id"]][(r["region_idx"], r["stream"])].append(
                (_num(c["onset_sec"]), _num(c["width_sec"])))
    folder = dataset.default()
    n = len(load_folder(folder))
    with mp.Pool(workers) as pool:
        got = pool.map(_context_job, [(i, str(folder), {k: dict(v) for k, v in want.items()})
                                      for i in range(n)])
    return ({sid: t for sid, t, _ in got}, {sid: l_ for sid, _, l_ in got})


def describe(rows: list[dict], trend: dict, local: dict) -> dict:
    """Per stream and treatment, for the stream's simple rule against CoactDetect proposed: the
    calls both make, and each side's calls alone, by participants over the floor, width, local
    rate against the window's, and the window's trend."""
    out = defaultdict(lambda: defaultdict(lambda: defaultdict(list)))
    for r in rows:
        if r["a"] != SIMPLE.get(r["stream"]):
            continue
        t = (trend.get(r["slice_id"]) or {}).get(f"{r['region_idx']}|{r['stream']}") or {}
        for kind, pool in (("both", r["shared"]), ("simple_only", r["a_only"]),
                           ("coact_only", r["b_only"])):
            for c in pool:
                on = _num(c["onset_sec"])
                lc = (local.get(r["slice_id"]) or {}).get(
                    f"{r['region_idx']}|{r['stream']}|{on:.4f}") or {}
                p, fl = _num(c.get("participants")), r["own_floor"]
                rec = dict(over_floor=p - fl if math.isfinite(p) and math.isfinite(fl) else None,
                           width=_num(c["width_sec"]), rel=lc.get("rel"),
                           trend=t.get("ratio"))
                for lab in (r["label"], "all"):
                    for key, v in rec.items():
                        if v is not None and math.isfinite(v):
                            out[r["stream"]][lab][f"{kind}|{key}"].append(v)
    summ = {}
    for s, per in out.items():
        summ[s] = {}
        for lab, d in per.items():
            summ[s][lab] = {k: dict(n=len(v), median=float(np.median(v)),
                                    q25=float(np.percentile(v, 25)), q75=float(np.percentile(v, 75)))
                            for k, v in d.items()}
    return summ


def trend_split(rows: list[dict], trend: dict) -> dict:
    """Disagreement share by the window's rate trend, per stream: rising (last third ≥ 1.5× the
    first), flat, falling (≤ 1/1.5)."""
    out = {}
    for s in STREAMS:
        cells = defaultdict(lambda: dict(windows=0, both=0, a_only=0, b_only=0))
        for r in rows:
            if r["stream"] != s or r["a"] != SIMPLE[s]:
                continue
            t = ((trend.get(r["slice_id"]) or {}).get(f"{r['region_idx']}|{s}") or {}).get("ratio")
            if t is None:
                continue
            key = "rising" if t >= 1.5 else "falling" if t <= 1 / 1.5 else "flat"
            c = cells[key]
            c["windows"] += 1
            c["both"] += r["both"]
            c["a_only"] += len(r["a_only"])
            c["b_only"] += len(r["b_only"])
        out[s] = {k: dict(v, disagree_share=(v["a_only"] + v["b_only"]) /
                          max(v["both"] + v["a_only"] + v["b_only"], 1)) for k, v in cells.items()}
    return out


# --------------------------------------------------------------------------------------------
# examples and the README
# --------------------------------------------------------------------------------------------

def clearest(rows: list[dict], per_side: int = 5) -> list[dict]:
    """The clearest disagreements on the streams the viewer opens: a call one detector makes with
    no call of the other within 4 tolerances, most participants over the floor first, one per
    recording and side."""
    out = []
    for side, pool_key, other_key in (("simple_only", "a_only", "b_calls"),
                                      ("coact_only", "b_only", "a_calls")):
        cand = []
        for r in rows:
            if r["stream"] not in VIEWER_STREAMS or r["a"] != SIMPLE[r["stream"]]:
                continue
            O = r[other_key]
            for c in r[pool_key]:
                on, wd = _num(c["onset_sec"]), _num(c["width_sec"])
                g = nearest_gap(on, wd, [_num(x["onset_sec"]) for x in O],
                                [_num(x["width_sec"]) for x in O])
                if g is not None and g <= 4 * TOL_SEC:
                    continue
                if not (on - r["win_start"] >= 10 and r["win_end"] - on - max(wd, 0) >= 10):
                    continue
                over = _num(c.get("participants")) - r["own_floor"]
                cand.append((over if math.isfinite(over) else -1e9, r, c, g))
        cand.sort(key=lambda x: -x[0])
        seen = set()
        for over, r, c, g in cand:
            if r["slice_id"] in seen:
                continue
            seen.add(r["slice_id"])
            out.append(dict(side=side, slice_id=r["slice_id"], stream=r["stream"],
                            group=r["group"], label=r["label"], region_idx=r["region_idx"],
                            onset=_num(c["onset_sec"]), width=_num(c["width_sec"]),
                            participants=_num(c.get("participants")), floor=r["own_floor"],
                            gap=g, win=(r["win_start"], r["win_end"])))
            if sum(1 for x in out if x["side"] == side) >= per_side:
                break
    return out


def render_figures(ex: list[dict], calls: list[dict], out: Path, n_each: int = 2) -> list[dict]:
    """The first ``n_each`` examples per side as rasters with lanes above (``make_briefing``'s
    figure: a ▼ lane marking the call, then the detectors' lanes, then the raster)."""
    from bugarach import dataset
    from bugarach.io import load_folder
    from make_briefing import render_example
    from make_group_raster_summary import lane_color

    picked = [e for side in ("simple_only", "coact_only")
              for e in [x for x in ex if x["side"] == side][:n_each]]
    if not picked:
        return []
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        slices = {sl.slice_id: sl for sl in load_folder(dataset.default())
                  if sl.slice_id in {e["slice_id"] for e in picked}}
    figs = []
    for no, e in enumerate(picked, 1):
        sl = slices.get(e["slice_id"])
        if sl is None or e["stream"] not in sl.streams:
            continue
        simple = SIMPLE[e["stream"]]
        ext = (max(e["win"][0], e["onset"] - 60.0), min(e["win"][1], e["onset"] + 60.0))
        lanes = {}
        for d in (simple, "coact", "coact_shipped"):
            lanes[d] = [c for c in calls if c["slice_id"] == e["slice_id"] and c["stream"] == e["stream"]
                        and c["detector"] == d and c["variant"] == "own_floor"
                        and _num(c["onset_sec"]) + max(_num(c["width_sec"]), 0) >= ext[0]
                        and _num(c["onset_sec"]) <= ext[1]]
        whose = NAME[simple] if e["side"] == "simple_only" else NAME["coact"]
        # The count forms take Okabe-Ito reddish purple: their review-page teal sits too close to
        # CoactDetect's to tell the lanes apart. CoactDetect shipped is gray.
        colors = {simple: "#CC79A7", "coact": lane_color("coact"), "coact_shipped": "#666666"}
        png = render_example(sl, e["stream"], dict(onset_sec=e["onset"]), lanes,
                             {d: NAME[d] for d in lanes}, colors,
                             ext, out, f"figure_{no}", f"this call ({whose}'s)")
        figs.append(dict(e, no=no, png=png.name if png else None, ext=ext))
    return figs


def _clock(t: datetime) -> str:
    from zoneinfo import ZoneInfo
    t = t.astimezone(ZoneInfo("America/New_York"))
    return f"{t:%Y-%m-%d} {int(t.strftime('%I'))}:{t:%M %p %Z}"


def _t(sec: float) -> str:
    from bugarach.time_axis import label
    return label(round(sec))


def readme(model: dict) -> str:
    L = []
    L.append("# The simple count rule against CoactDetect, on real recordings\n")
    L.append(f"WSMIP065, built {model['built']}. **Working material, not murderboarded.** A "
             "detector-agreement result, not a treatment-effect claim (those belong to fireflies). "
             f"Dataset: `{model['dataset']['name']}` ({model['dataset']['recordings']} recordings). "
             "Every number is in `agreement.json`; the calls are in `detections.csv`, which the "
             "viewer opens.\n")
    h = model["headline"]
    L.append("## The answer\n")
    L.append(h + "\n")
    L.append("## What was run\n")
    L.append("`tools/detect_with_floors.py` on every baseline and treatment window of the default "
             "dataset, fast, slow and combined, every detector at each window's own ADR-0008 floor "
             "(treatment windows also at the baseline's floor, reported in `agreement.json`):\n")
    for s in STREAMS:
        ch = model["settings"].get(s, {})
        L.append(f"- **{s}**: " + "; ".join(f"{NAME.get(d, d)} ({ch[d]['which']}: "
                                              + ", ".join(f"{k} {v}" for k, v in ch[d]['params'].items()
                                                          if k not in ('rng_seed',)) + ")"
                                              for d in ("count", "count_sliding", "coact", "coact_shipped")
                                              if d in ch))
    L.append("\nFast count (sliding)'s proposal is the setting 064 found out of budget on the bench "
             "(precision swing 0.146 against 0.10); it is run because the brief asked for the "
             "proposed settings, and the headline uses each stream's best in-budget form instead: "
             + ", ".join(f"{s} {NAME[SIMPLE[s]]}" for s in STREAMS) + ".\n")
    L.append(f"**Agreement** is the scorer's matching rule (`score.score_detections`: greedy, "
             f"closest pair first, one to one, within {TOL_SEC:g} s, ties broken by distance "
             "between centres), applied span to span: two calls are {TOL_SEC:g} s apart or closer "
             "when their spans overlap or their nearer edges are that close. **Agreement share** "
             "is calls both make over all distinct calls (both + only one + only the other).\n"
             .replace("{TOL_SEC:g}", f"{TOL_SEC:g}"))
    n = 1
    L.append("## Agreement by stream and treatment\n")
    L.append("The simple rule (each stream's best in-budget count form) against CoactDetect "
             "proposed, and, as a yardstick, CoactDetect shipped against CoactDetect proposed. "
             "Counts are calls; windows at their own floor.\n")
    for s in STREAMS:
        L.append(f"**Table {n}. {s} stream.** Calls both make, calls only the simple rule makes, "
                 "calls only CoactDetect proposed makes, and the agreement share; the last column "
                 "is the yardstick's agreement share.\n")
        L.append("| treatment | windows | hours | both | only simple | only CoactDetect | "
                 "agreement | yardstick agreement |")
        L.append("|---|---|---|---|---|---|---|---|")
        yard = {r["label"]: r for r in model["tables"][s]["coact_shipped"]["all"]}
        for r in model["tables"][s][SIMPLE[s]]["all"]:
            y = yard.get(r["label"], {})
            L.append(f"| {r['label']} | {_n(r['windows'], 'window')} | {r['hours']:.1f} h | "
                     f"{_n(r['both'])} | {_n(r['a_only'])} | {_n(r['b_only'])} | "
                     f"{_f(r['agree_share'])} | {_f(y.get('agree_share'))} |")
        L.append("")
        n += 1
    L.append(f"**Table {n}. By group**, the simple rule against CoactDetect proposed, agreement "
             "share (calls both make over all distinct calls), groups in the house order.\n")
    groups = in_group_order({r["group"] for s in STREAMS for r in model["tables"][s][SIMPLE[s]]["group"]})
    L.append("| stream | treatment | " + " | ".join(groups) + " |")
    L.append("|---|---|" + "---|" * len(groups))
    for s in STREAMS:
        cells = defaultdict(dict)
        for r in model["tables"][s][SIMPLE[s]]["group"]:
            cells[r["label"]][r["group"]] = r
        for lab in [x for x in LABEL_ORDER if x in cells] + sorted(set(cells) - set(LABEL_ORDER)):
            L.append(f"| {s} | {lab} | " + " | ".join(
                (f"{_f(cells[lab][g]['agree_share'])} ({_n(cells[lab][g]['both'] + cells[lab][g]['a_only'] + cells[lab][g]['b_only'])})"
                 if g in cells[lab] else "—") for g in groups) + " |")
    L.append("")
    n += 1
    L.append("## What the disagreements look like\n")
    L.append(f"**Table {n}.** Medians (25th–75th percentile) for the calls both make and each "
             "side's calls alone, by stream and treatment: participants over the window's own "
             f"floor (ROIs), width (s), and the event rate within {LOCAL_SEC:g} s of the call "
             "(its own span left out) as a multiple of the window's mean rate. A local null "
             "should matter where calls alone sit in stretches busier than their window.\n")
    L.append("| stream | treatment | kind | calls | over floor (ROIs) | width (s) | local rate ÷ window rate |")
    L.append("|---|---|---|---|---|---|---|")
    kinds = (("both", "both"), ("simple_only", "only simple"), ("coact_only", "only CoactDetect"))
    for s in STREAMS:
        per = model["describe"].get(s, {})
        for lab in [x for x in ("all", *LABEL_ORDER) if x in per]:
            for k, word in kinds:
                d = per[lab]
                of, wd, rl = (d.get(f"{k}|{m}") for m in ("over_floor", "width", "rel"))
                if not of:
                    continue
                L.append(f"| {s} | {lab} | {word} | {_n(of['n'])} | {_f(of['median'], 0)} "
                         f"({_f(of['q25'], 0)}–{_f(of['q75'], 0)}) | {_f(wd['median'])} "
                         f"({_f(wd['q25'])}–{_f(wd['q75'])}) | "
                         + (f"{_f(rl['median'])} ({_f(rl['q25'])}–{_f(rl['q75'])})" if rl else "—")
                         + " |")
    L.append("")
    n += 1
    L.append(f"**Table {n}.** Disagreement share (calls only one makes over all distinct calls) "
             "by the window's rate trend: *rising* when the last third's event rate is at least "
             "1.5 times the first third's, *falling* at 1/1.5 or less, *flat* between.\n")
    L.append("| stream | trend | windows | both | only simple | only CoactDetect | disagreement |")
    L.append("|---|---|---|---|---|---|---|")
    for s in STREAMS:
        for k in ("falling", "flat", "rising"):
            v = model["trend_split"].get(s, {}).get(k)
            if v:
                L.append(f"| {s} | {k} | {_n(v['windows'], 'window')} | {_n(v['both'])} | "
                         f"{_n(v['a_only'])} | {_n(v['b_only'])} | {_f(v['disagree_share'])} |")
    L.append("")
    n += 1
    L.append("## Examples\n")
    L.append("Each figure: a lane marking the call (▼, pointing down at the raster), then the "
             "simple rule's, CoactDetect proposed's and CoactDetect shipped's calls in lanes, then "
             "the recording's raster over two minutes around the call (cut at the window's edge), "
             "cells sorted by their event count in the window shown. Nothing is drawn on the "
             "raster. The examples are the calls with the most participants over their floor "
             "among those with no call of the other detector within "
             f"{4 * TOL_SEC:g} s, one per recording, on the streams the viewer opens.\n")
    fig = 1
    for f in model["figures"]:
        who = NAME[SIMPLE[f["stream"]]] if f["side"] == "simple_only" else NAME["coact"]
        other = NAME["coact"] if f["side"] == "simple_only" else NAME[SIMPLE[f["stream"]]]
        gap = ("no call on this window" if f["gap"] is None else
               f"its nearest call {_t(f['gap']) if f['gap'] >= 60 else f'{f['gap']:.1f} s'} away")
        L.append(f"**Figure {fig}.** {who} calls it; {other} does not ({gap}). {f['group']}, "
                 f"{f['label']} window, {f['stream']} stream, the call at {_t(f['onset'])} with "
                 f"{int(f['participants'])} participating ROIs against a floor of "
                 f"{int(f['floor'])} ROIs. [Open in the viewer](viewer.html#slice={f['slice_id']}"
                 f"&stream={f['stream']}).\n")
        if f.get("png"):
            L.append(f"![Figure {fig}]({f['png']})\n")
        fig += 1
    L.append("## Viewer links to the clearest disagreements\n")
    L.append("Open `viewer.html` beside this file, choose the export folder named above, then "
             "*Open results (detections.csv)…* and pick `detections.csv` here. Each link opens the "
             "recording at its start; the time is given beside it. The viewer names lanes by short "
             "id (`coact`, `count`, `count_sliding`, `coact_shipped`); `own_floor` is the run at "
             "the window's own floor.\n")
    for e in model["examples"]:
        who = "simple only" if e["side"] == "simple_only" else "CoactDetect only"
        L.append(f"- [{e['group']}, {e['label']}, {e['stream']}, {_t(e['onset'])}]"
                 f"(viewer.html#slice={e['slice_id']}&stream={e['stream']}) — {who}, "
                 f"{int(e['participants'])} ROIs against a floor of {int(e['floor'])} ROIs")
    L.append("\n## Limits\n")
    L.append("- There is no ground truth on real recordings: a call only one detector makes is a "
             "disagreement, not a miss.\n- The count settings were tuned on the realistic bench, "
             "the object of the question; CoactDetect's proposal too. The shipped CoactDetect is "
             "the one setting here that predates that bench.\n- Windows are grouped by treatment "
             "only to see where the detectors part; nothing here compares treatments.\n"
             "- Recordings share animals; the counts are pooled calls, with no inference drawn "
             "from them.")
    return "\n".join(L) + "\n"


def headline(tables: dict, describe_: dict, split: dict) -> str:
    parts = []
    for s in STREAMS:
        rows = {r["label"]: r for r in tables[s][SIMPLE[s]]["all"]}
        yard = {r["label"]: r for r in tables[s]["coact_shipped"]["all"]}
        tot = [r for r in tables[s][SIMPLE[s]]["all"]]
        both = sum(r["both"] for r in tot)
        a = sum(r["a_only"] for r in tot)
        b = sum(r["b_only"] for r in tot)
        n = both + a + b
        seg = [f"**{s}**: {NAME[SIMPLE[s]]} and CoactDetect proposed share {both} of {n} distinct "
               f"calls ({both / n:.0%}); {a} are the simple rule's alone and {b} CoactDetect's"
               if n else f"**{s}**: no calls"]
        per = ", ".join(f"{lab} {_f(rows[lab]['agree_share'])} (yardstick {_f(yard.get(lab, {}).get('agree_share'))})"
                        for lab in ("baseline", "TTX", "senktide") if lab in rows)
        if per:
            seg.append(f"agreement share by treatment: {per}")
        parts.append("; ".join(seg) + ".")
    def med(s, lab, key):
        v = ((describe_.get(s) or {}).get(lab) or {}).get(key)
        return v["median"] if v else None

    floor_txt = "; ".join(
        f"{s} {_f(med(s, 'all', 'simple_only|over_floor'), 0)} against "
        f"{_f(med(s, 'all', 'both|over_floor'), 0)}" for s in STREAMS
        if med(s, "all", "simple_only|over_floor") is not None)
    busy = []
    for s in STREAMS:
        for k, word in (("simple_only", "the simple rule's"), ("coact_only", "CoactDetect's")):
            m = med(s, "senktide", f"{k}|rel")
            if m is not None and (describe_[s]["senktide"][f"{k}|rel"]["n"] >= 3):
                busy.append(f"{s} {word} {_f(m)}")
    shared = "; ".join(f"{s} {_f(med(s, 'senktide', 'both|rel'))}" for s in STREAMS
                       if med(s, "senktide", "both|rel") is not None)
    tr = "; ".join(f"{s} " + ", ".join(f"{k} {_f(split[s][k]['disagree_share'])}"
                                       for k in ("falling", "flat", "rising") if k in split[s])
                   for s in STREAMS if split.get(s))
    return ("On real recordings, with no bench: " + " ".join(parts) + " The yardstick is "
            "CoactDetect shipped against CoactDetect proposed: how much two settings of one "
            "detector disagree.\n\n**Where they part.** Most disagreements are calls the simple "
            "rule makes alone, and they sit close to the floor: median participants over the "
            f"window's floor, the simple rule's calls alone against calls both make, {floor_txt} "
            "ROIs (Table 5). In senktide windows, calls one detector makes alone sit in stretches "
            f"busier than their window (event rate within {LOCAL_SEC:g} s ÷ the window's: "
            f"{'; '.join(busy)}), where calls both make sit at about their window's rate "
            f"({shared}). That is the case a local null exists for. But a window whose rate "
            "rises across it does not disagree more than a flat or falling one (disagreement "
            f"share by trend: {tr}; Table 6), and senktide's fast windows have few calls "
            "(Table 1).")


def main(argv=None) -> int:
    from bugarach import dataset
    from bugarach.paths import darkroom, unresolved_message

    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("--out", type=Path, default=None,
                    help=f"the folder holding both runs (default <darkroom>/{FOLDER_NAME})")
    ap.add_argument("--workers", type=int, default=16)
    ap.add_argument("--no-figures", action="store_true")
    a = ap.parse_args(argv)
    if a.out is None:
        root = darkroom()
        if root is None:
            print(unresolved_message(), file=sys.stderr)
            return 2
        a.out = root / FOLDER_NAME
    calls, wins_rows, results = merge_runs(a.out)
    det_path = write_merged(a.out, calls, results)
    wins = windows_of(wins_rows)
    rows = agreement(calls, wins, "own_floor")
    rows_base = agreement(calls, {k: v for k, v in wins.items() if v["label"] != "baseline"},
                          "baseline_floor")
    tables = {s: {x: dict(all=tally(rows, x, s, by_group=False),
                          group=tally(rows, x, s, by_group=True),
                          treatment_at_baseline_floor=tally(rows_base, x, s, by_group=False))
                  for x, _ in PAIRS} for s in STREAMS}
    trend, local = context(rows, a.workers)
    desc = describe(rows, trend, local)
    split = trend_split(rows, trend)
    ex = clearest(rows)
    figs = [] if a.no_figures else render_figures(ex, calls, a.out)
    model = dict(built=_clock(datetime.now(timezone.utc)), dataset=dataset.stamp(),
                 tol_sec=TOL_SEC, simple=SIMPLE, tables=tables, describe=desc, trend_split=split,
                 examples=ex, figures=figs,
                 settings={s: (results.get("chosen") or {}).get(s, {}).get("detectors", {})
                           for s in STREAMS},
                 headline=headline(tables, desc, split))
    (a.out / "agreement.json").write_text(json.dumps(model, indent=1, default=str) + "\n",
                                          encoding="utf-8")
    (a.out / "README.md").write_text(readme(model), encoding="utf-8")
    viewer = REPO / "docs" / "site" / "raster_viewer.html"
    if viewer.exists():
        shutil.copy2(viewer, a.out / "viewer.html")
    print(f"wrote {det_path}\nwrote {a.out / 'agreement.json'}\nwrote {a.out / 'README.md'}")
    for f in figs:
        print(f"wrote {a.out / f['png']}" if f.get("png") else f"figure {f['no']} did not render")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
