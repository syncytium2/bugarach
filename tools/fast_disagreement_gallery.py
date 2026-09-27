#!/usr/bin/env python3
"""The fast stream's disagreements between count (sliding) and CoactDetect, to judge by eye.

    python tools/fast_disagreement_gallery.py [--parent <darkroom folder>] [--seed N]

Tony, 2026-09-27, through the orchestrator: he is leaning toward count (sliding) as the one
primary detector, and fast is where it and CoactDetect part most. This reads, under ``--parent``
(default ``<darkroom>/2026-09-27-simple-vs-coact-real``):

* ``run-count-and-coact-proposal/`` — CoactDetect proposed, from this morning's comparison;
* ``fast-sliding/run-sliding-w1/`` and ``fast-sliding/run-sliding-w2/`` — count (sliding) with a
  1 s and a 2 s window, k 0, merge 3 s, each a ``tools/detect_with_floors.py`` run.

and writes into ``fast-sliding/``: the shared share of each setting against CoactDetect proposed
on fast, beside this morning's binned figure; a tally of what the calls only one detector makes
look like; and a gallery page (``index.html``) of disagreement examples for the 1 s setting.

**Matching** is ``agreement_on_real.match_calls``: the scorer's rule, span to span, inclusive.

**The examples are picked by rule, not by hand.** Strata are group × treatment (baseline, TTX,
senktide), visited in a rotating order so each run of three picks covers the three treatments
and the groups turn over: round r takes (baseline, group r), (TTX, group r+1), (senktide, group
r+2), groups in the house order and counted modulo four. Within a stratum the pick is random with
a fixed seed. A call qualifies if it lies at least :data:`ZOOM_SEC` inside its window, so the
zoomed figure is never cut.

**What a lone call looks like**, for every lone call, not only the pictured ones:

* *participants over the floor*: the call's participating ROIs less its window's ADR-0008 floor;
* *onset spread*: across the participating ROIs, the range of each one's first onset within the
  call's participant span (``detect_with_floors.participants``: the call's span padded 1 s);
* *local rate*: the event rate within 30 s of the call, its own padded span left out, as a
  multiple of the window's mean rate.

The tally flags a call as a *tight burst just over the floor* (at most 2 ROIs over and a spread of
at most 1 s), a *wide spread* (at least 2 s), or *inside a busy stretch* (local rate at least 1.5
times the window's). The flags describe; they do not judge which calls are events.
"""
from __future__ import annotations

import argparse
import csv
import html
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

from agreement_on_real import _clock, _num, match_calls, nearest_gap  # noqa: E402
from bugarach.groups import in_group_order  # noqa: E402
from bugarach.score import TOL_SEC  # noqa: E402

PARENT_NAME = "2026-09-27-simple-vs-coact-real"
STREAM = "fast"
SETTINGS = (("w1", "count (sliding), 1 s window", "fast-sliding/run-sliding-w1"),
            ("w2", "count (sliding), 2 s window", "fast-sliding/run-sliding-w2"))
REF_RUN = "run-count-and-coact-proposal"
TREATMENTS = ("baseline", "TTX", "senktide")
ZOOM_SEC = 10.0
LOCAL_SEC = 30.0
PAD_SEC = 1.0
PER_SIDE = 10
SEED = 20260927
TIGHT_OVER, TIGHT_SPREAD, WIDE_SPREAD, BUSY_REL = 2, 1.0, 2.0, 1.5
LANE = {"count_sliding_w1": ("count (sliding) 1 s", "#CC79A7"),
        "count_sliding_w2": ("count (sliding) 2 s", "#E69F00"),
        "coact": ("CoactDetect proposed", "#00B3A4")}


def read_calls(run: Path, detector: str, rename: str | None = None) -> list[dict]:
    with (run / "calls.csv").open(encoding="utf-8", newline="") as fh:
        rows = [r for r in csv.DictReader(fh) if r["detector"] == detector
                and r["variant"] == "own_floor"]
    for r in rows:
        r["detector"] = rename or detector
        r["label"] = "baseline" if r["window_kind"] == "baseline" else r["label"]
    return rows


def by_window(calls: list[dict]) -> dict:
    out = defaultdict(list)
    for c in calls:
        out[(c["slice_id"], c["region_idx"], c["stream"])].append(c)
    return out


def compare(A: list[dict], B: list[dict], stream: str = STREAM) -> dict:
    """Shared, A-only and B-only calls on one stream, window by window."""
    a, b = by_window([c for c in A if c["stream"] == stream]), by_window(
        [c for c in B if c["stream"] == stream])
    shared, a_only, b_only = [], [], []
    for k in set(a) | set(b):
        X, Y = a.get(k, []), b.get(k, [])
        pairs = match_calls([_num(c["onset_sec"]) for c in X], [_num(c["width_sec"]) for c in X],
                            [_num(c["onset_sec"]) for c in Y], [_num(c["width_sec"]) for c in Y])
        ia, ib = {i for i, _ in pairs}, {j for _, j in pairs}
        shared += [X[i] for i, _ in pairs]
        a_only += [c for i, c in enumerate(X) if i not in ia]
        b_only += [c for j, c in enumerate(Y) if j not in ib]
    return dict(shared=shared, a_only=a_only, b_only=b_only)


def share_table(cmp: dict) -> list[dict]:
    rows = []
    for lab in ("all", *TREATMENTS):
        pick = (lambda c: True) if lab == "all" else (lambda c, lab=lab: c["label"] == lab)
        s, a, b = (sum(1 for c in cmp[k] if pick(c)) for k in ("shared", "a_only", "b_only"))
        n = s + a + b
        rows.append(dict(label=lab, shared=s, a_only=a, b_only=b, n=n,
                         share=s / n if n else None))
    return rows


def _measure_job(args):
    """Per recording: onset spread and local rate for each listed call."""
    i, folder, want = args
    from bugarach.detect_folder import _region_index, folder_analysis_windows
    from bugarach.detectors.rate import stream_trains
    from bugarach.io import load_folder

    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        s = load_folder(Path(folder))[i]
        if s.slice_id not in want:
            return s.slice_id, {}
        s, windows = folder_analysis_windows(s)
    out = {}
    for w in windows:
        lo, hi = float(w.win_start), float(w.win_end)
        idx = str(_region_index(w))
        keys = want[s.slice_id].get(idx)
        if hi <= lo or not keys or STREAM not in s.streams:
            continue
        tr = stream_trains(s.streams[STREAM], (lo, hi))
        n = max(len(tr), 1)
        allon = np.sort(np.concatenate([t for t in tr if len(t)] or [np.zeros(0)]))
        mean = allon.size / (n * (hi - lo))
        for on, wd in keys:
            p0, p1 = on - PAD_SEC, on + max(wd, 0.0) + PAD_SEC
            firsts = [float(t[(t >= p0) & (t <= p1)][0]) for t in tr
                      if np.any((t >= p0) & (t <= p1))]
            spread = max(firsts) - min(firsts) if firsts else None
            a, b = max(lo, on - LOCAL_SEC), min(hi, on + max(wd, 0.0) + LOCAL_SEC)
            span = (b - a) - max(0.0, min(b, p1) - max(a, p0))
            k = np.sum((allon >= a) & (allon <= b) & ~((allon >= p0) & (allon <= p1)))
            rel = (k / (n * span)) / mean if span > 0 and mean > 0 else None
            out[f"{idx}|{on:.4f}"] = dict(spread=spread, rel=rel)
    return s.slice_id, out


def measure(calls: list[dict], workers: int) -> None:
    """Adds ``spread``, ``rel`` and ``over`` to each call, in place."""
    from bugarach import dataset
    from bugarach.io import load_folder

    want = defaultdict(lambda: defaultdict(list))
    for c in calls:
        want[c["slice_id"]][c["region_idx"]].append((_num(c["onset_sec"]), _num(c["width_sec"])))
    folder = dataset.default()
    n = len(load_folder(folder))
    with mp.Pool(workers) as pool:
        got = dict(pool.map(_measure_job, [(i, str(folder), {k: dict(v) for k, v in want.items()})
                                           for i in range(n)]))
    for c in calls:
        m = (got.get(c["slice_id"]) or {}).get(f"{c['region_idx']}|{_num(c['onset_sec']):.4f}") or {}
        c["spread"], c["rel"] = m.get("spread"), m.get("rel")
        p, f = _num(c.get("participants")), _num(c.get("own_floor"))
        c["over"] = p - f if math.isfinite(p) and math.isfinite(f) else None


def flags(c: dict) -> list[str]:
    out = []
    if c.get("over") is not None and c.get("spread") is not None \
            and c["over"] <= TIGHT_OVER and c["spread"] <= TIGHT_SPREAD:
        out.append("tight")
    if c.get("spread") is not None and c["spread"] >= WIDE_SPREAD:
        out.append("wide")
    if c.get("rel") is not None and c["rel"] >= BUSY_REL:
        out.append("busy")
    return out


def tally(pool: list[dict]) -> dict:
    t = dict(n=len(pool), tight=0, wide=0, busy=0, none=0, measured=0)
    for c in pool:
        if c.get("spread") is None and c.get("rel") is None:
            continue
        t["measured"] += 1
        f = flags(c)
        for k in f:
            t[k] += 1
        t["none"] += not f
    return t


def pick(pool: list[dict], wins: dict, groups: list[str], seed: int, n: int = PER_SIDE) -> list[dict]:
    """The stated rule: rotating strata of group × treatment, a seeded random pick within each."""
    rng = np.random.default_rng(seed)
    strata = defaultdict(list)
    for c in pool:
        w = wins.get((c["slice_id"], c["region_idx"]))
        on, wd = _num(c["onset_sec"]), max(_num(c["width_sec"]), 0.0)
        if w is None or on - w[0] < ZOOM_SEC or w[1] - on - wd < ZOOM_SEC:
            continue
        if c["label"] in TREATMENTS:
            strata[(c["label"], c["group"])].append(c)
    for k in strata:
        strata[k].sort(key=lambda c: (c["slice_id"], _num(c["onset_sec"])))
        rng.shuffle(strata[k])
    order = [(TREATMENTS[t], groups[(r + t) % len(groups)])
             for r in range(len(groups)) for t in range(len(TREATMENTS))]
    out, used = [], defaultdict(int)
    while len(out) < n and any(used[k] < len(strata.get(k, [])) for k in order):
        for k in order:
            if len(out) >= n:
                break
            if used[k] < len(strata.get(k, [])):
                out.append(strata[k][used[k]])
                used[k] += 1
    return out


def render(examples: list[dict], lanes_src: dict, out: Path) -> None:
    from bugarach import dataset
    from bugarach.io import load_folder
    from make_briefing import render_example

    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        slices = {sl.slice_id: sl for sl in load_folder(dataset.default())
                  if sl.slice_id in {e["slice_id"] for e in examples}}
    for e in examples:
        sl = slices.get(e["slice_id"])
        on = _num(e["onset_sec"])
        ext = (on - ZOOM_SEC, on + max(_num(e["width_sec"]), 0.0) + ZOOM_SEC)
        lanes = {d: [c for c in rows if c["slice_id"] == e["slice_id"] and c["stream"] == STREAM
                     and _num(c["onset_sec"]) + max(_num(c["width_sec"]), 0) >= ext[0]
                     and _num(c["onset_sec"]) <= ext[1]]
                 for d, rows in lanes_src.items()}
        whose = "count (sliding) 1 s" if e["side"] == "simple_only" else "CoactDetect proposed"
        png = render_example(sl, STREAM, dict(onset_sec=on), lanes,
                             {d: LANE[d][0] for d in lanes}, {d: LANE[d][1] for d in lanes},
                             ext, out, f"example_{e['no']:02d}", f"this call ({whose}'s)") \
            if sl is not None and STREAM in sl.streams else None
        e["png"] = png.name if png else None


CSS = """
:root { --bg:#fbfaf7; --fg:#1b1b1b; --muted:#5b5b5b; --line:#dcd8cf; --accent:#0072B2; --card:#fff; }
@media (prefers-color-scheme: dark) { :root:not([data-theme="light"]) {
  --bg:#141414; --fg:#e8e6e1; --muted:#a8a49c; --line:#3a3833; --accent:#6cb4e4; --card:#1d1d1d; } }
:root[data-theme="dark"] { --bg:#141414; --fg:#e8e6e1; --muted:#a8a49c; --line:#3a3833;
  --accent:#6cb4e4; --card:#1d1d1d; }
html { font-size: 17px; }
body { background: var(--bg); color: var(--fg); margin: 0;
       font: 1rem/1.55 system-ui, -apple-system, "Segoe UI", sans-serif; }
.wrap { max-width: 1180px; margin: 0 auto; padding: 24px 16px 80px; }
a { color: var(--accent); }
.muted { color: var(--muted); }
.tablewrap { overflow-x: auto; }
table { border-collapse: collapse; margin: .4rem 0 1.2rem; }
th, td { border-bottom: 1px solid var(--line); padding: .3rem .6rem; text-align: left; }
td.n { text-align: right; font-variant-numeric: tabular-nums; white-space: nowrap; }
figure { margin: 1.4rem 0 2rem; }
figure img { width: 100%; max-width: 1160px; height: auto; background: #fff;
             border: 1px solid var(--line); display: block; }
figcaption { color: var(--muted); margin-top: .4rem; }
.box { border: 1px solid var(--line); background: var(--card); padding: .8rem 1rem;
       border-radius: 6px; margin: 1rem 0; }
"""


def _t(sec: float) -> str:
    from bugarach.time_axis import label
    return label(round(sec))


def _f(x, nd=2):
    return "—" if x is None else f"{x:.{nd}f}"


def _n(k, one, many=None):
    return f"{k} {one if k == 1 else (many or one + 's')}"


def page(model: dict) -> str:
    P = []
    P.append("<h1>Fast disagreement gallery</h1>")
    P.append(f"<p class='muted'>WSMIP065, built {html.escape(model['built'])}. <b>Working "
             "material, not murderboarded</b>; a detector-agreement look, not a treatment-effect "
             f"claim. Dataset <code>{html.escape(model['dataset']['name'])}</code> "
             f"({_n(model['dataset']['recordings'], 'recording')}). Fast stream, every detector at "
             "each window's own ADR-0008 floor.</p>")
    P.append("<div class='box'><b>Shared calls on fast.</b> " + model["headline"] + "</div>")
    head = ("<tr><th>treatment</th>" + "".join(f"<th>{html.escape(s['name'])}</th>"
                                               for s in model["shares"]) + "</tr>")
    body = []
    labels = [r["label"] for r in model["shares"][0]["rows"]]
    for i, lab in enumerate(labels):
        cells = []
        for s in model["shares"]:
            r = s["rows"][i]
            cells.append(f"<td class='n'>{_f(r['share'])} <span class='muted'>({r['shared']} of "
                         f"{_n(r['n'], 'call')})</span></td>")
        body.append(f"<tr><td>{lab}</td>{''.join(cells)}</tr>")
    P.append("<p><b>Table 1.</b> Shared share against CoactDetect proposed on fast: calls both "
             "make over all distinct calls, by treatment. Binned is this morning's figure.</p>"
             f"<div class='tablewrap'><table>{head}{''.join(body)}</table></div>")
    P.append("<p><b>Table 2.</b> What the lone calls look like, count (sliding) 1 s against "
             "CoactDetect proposed, every lone call on fast (the shared calls for reference). "
             f"<i>Tight burst just over the floor</i>: at most {TIGHT_OVER} ROIs over the floor "
             f"and an onset spread of at most {TIGHT_SPREAD:g} s. <i>Wide spread</i>: at least "
             f"{WIDE_SPREAD:g} s. <i>Busy stretch</i>: event rate within {LOCAL_SEC:g} s at least "
             f"{BUSY_REL:g} times the window's. A call can carry more than one flag. These "
             "describe the calls; they do not say which are events.</p>")
    rows = []
    for key, word in (("simple_only", "only count (sliding) 1 s"),
                      ("coact_only", "only CoactDetect proposed"), ("shared", "both")):
        t = model["tally"][key]
        m = t["measured"] or 1
        rows.append(f"<tr><td>{word}</td><td class='n'>{_n(t['n'], 'call')}</td>"
                    + "".join(f"<td class='n'>{t[k]} ({t[k] / m:.0%})</td>"
                              for k in ("tight", "wide", "busy", "none")) + "</tr>")
    P.append("<div class='tablewrap'><table><tr><th>calls</th><th>count</th><th>tight burst "
             "just over the floor</th><th>wide spread</th><th>busy stretch</th><th>none of "
             "these</th></tr>" + "".join(rows) + "</table></div>")
    n_ref = sum(1 for e in model["examples"] if e["side"] == "coact_only")
    n_simple = len(model["examples"]) - n_ref
    P.append(f"<h2>Examples</h2><p>{_n(len(model['examples']), 'example')}: "
             f"{_n(n_simple, 'call')} only count (sliding) 1 s makes (Figures 1–{n_simple}), then "
             f"{_n(n_ref, 'call')} only CoactDetect proposed makes. CoactDetect has only "
             f"{_n(model['tally']['coact_only']['n'], 'lone call')} on fast in the whole dataset, "
             f"so every one that qualifies is shown and the gallery is filled to "
             f"{2 * PER_SIDE} with the simple rule's. <b>How they were picked</b>: strata "
             "are group × treatment (baseline, TTX, senktide), visited in a rotating order so "
             "each run of three picks covers the three treatments and the groups turn over "
             f"(round r takes baseline with group r, TTX with group r+1, senktide with group "
             "r+2, groups in the order DI, OVX, MALE, ORX); within a stratum the pick is random "
             f"with seed {model['seed']}. A call qualifies if it lies at least {ZOOM_SEC:g} s "
             "inside its window. Each figure: a lane marking the call (▼, pointing down at the "
             "raster), then the lanes of count (sliding) 1 s, count (sliding) 2 s and "
             f"CoactDetect proposed, then the raster ±{ZOOM_SEC:g} s around the call, cells "
             "sorted by their event count in the window shown. Nothing is drawn on the raster. "
             "Each figure links to the viewer: open <code>viewer.html</code> beside this page "
             "first, choose the export folder, then <i>Open results (detections.csv)…</i> and "
             "pick the <code>detections.csv</code> here.</p>")
    for e in model["examples"]:
        who = "count (sliding) 1 s calls it; CoactDetect proposed does not" \
            if e["side"] == "simple_only" else "CoactDetect proposed calls it; count (sliding) 1 s does not"
        g = e.get("gap")
        gap = ("the other made no call in this window" if g is None else
               f"the other's nearest call is {g:.1f} s away" if g < 60 else
               f"the other's nearest call is {_t(g)} away")
        fl = ", ".join({"tight": "tight burst just over the floor", "wide": "wide spread",
                        "busy": "busy stretch"}[k] for k in flags(e)) or "none of the flags"
        link = f"viewer.html#slice={e['slice_id']}&stream={STREAM}"
        cap = (f"<b>Figure {e['no']}.</b> {who} ({gap}). {html.escape(e['group'])}, "
               f"{html.escape(e['label'])} window, the call at {_t(_num(e['onset_sec']))}: "
               f"{_n(int(_num(e['participants'])), 'participating ROI')} against a floor of "
               f"{_n(int(_num(e['own_floor'])), 'ROI')}; onset spread "
               f"{_f(e.get('spread'), 1)} s; local rate {_f(e.get('rel'))} times the window's. "
               f"Flags: {fl}. <a href='{link}' target='bugarach-viewer'>Open recording "
               f"{html.escape(e['slice_id'])} in the viewer</a> (it opens at the start; the call "
               f"is at {_t(_num(e['onset_sec']))}).")
        img = (f"<a href='{link}' target='bugarach-viewer'><img src='{e['png']}' alt='Figure "
               f"{e['no']}: {html.escape(who)}'></a>" if e.get("png") else
               "<p class='muted'>(figure did not render)</p>")
        P.append(f"<figure>{img}<figcaption>{cap}</figcaption></figure>")
    return ("<!doctype html>\n<html lang='en'>\n<head>\n<meta charset='utf-8'><title>Fast "
            "disagreement gallery</title>\n<meta name='viewport' content='width=device-width, "
            f"initial-scale=1'>\n<style>{CSS}</style>\n</head>\n<body><div class='wrap'>"
            + "\n".join(P) + "</div></body></html>\n")


def main(argv=None) -> int:
    from bugarach import dataset
    from bugarach.paths import darkroom, unresolved_message
    from detect_with_floors import write_detections

    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("--parent", type=Path, default=None)
    ap.add_argument("--seed", type=int, default=SEED)
    ap.add_argument("--workers", type=int, default=16)
    a = ap.parse_args(argv)
    if a.parent is None:
        root = darkroom()
        if root is None:
            print(unresolved_message(), file=sys.stderr)
            return 2
        a.parent = root / PARENT_NAME
    out = a.parent / "fast-sliding"
    ref = read_calls(a.parent / REF_RUN, "coact")
    runs = {k: read_calls(a.parent / rel, "count_sliding", f"count_sliding_{k}")
            for k, _, rel in SETTINGS}
    cmps = {k: compare(runs[k], ref) for k in runs}
    morning = json.loads((a.parent / "agreement.json").read_text(encoding="utf-8"))
    binned = {r["label"]: r for r in morning["tables"][STREAM]["count"]["all"]}
    shares = [dict(key="binned", name="count (binned), 1 s bins (this morning)", rows=[
        dict(label=lab, shared=sum(r["both"] for r in binned.values()) if lab == "all" else
             binned.get(lab, {}).get("both", 0),
             n=sum(r["both"] + r["a_only"] + r["b_only"] for r in binned.values()) if lab == "all"
             else sum(binned.get(lab, {}).get(k, 0) for k in ("both", "a_only", "b_only")))
        for lab in ("all", *TREATMENTS)])]
    for r in shares[0]["rows"]:
        r["share"] = r["shared"] / r["n"] if r["n"] else None
    shares += [dict(key=k, name=name, rows=share_table(cmps[k])) for k, name, _ in SETTINGS]
    c1 = cmps["w1"]
    for c in c1["a_only"]:
        c["side"] = "simple_only"
    for c in c1["b_only"]:
        c["side"] = "coact_only"
    measure(c1["a_only"] + c1["b_only"] + c1["shared"], a.workers)
    wins = {}
    with (a.parent / REF_RUN / "windows.csv").open(encoding="utf-8", newline="") as fh:
        for r in csv.DictReader(fh):
            wins[(r["slice_id"], r["region_idx"])] = (_num(r["win_start"]), _num(r["win_end"]))
    groups = in_group_order({c["group"] for c in ref if c.get("group")})
    # Up to PER_SIDE of CoactDetect's lone calls; the gallery is filled to 2 × PER_SIDE with the
    # simple rule's, because on fast CoactDetect has very few lone calls to show.
    ex_ref = pick(c1["b_only"], wins, groups, a.seed + 1)
    ex = pick(c1["a_only"], wins, groups, a.seed, n=2 * PER_SIDE - len(ex_ref)) + ex_ref
    ref_by, w1_by = by_window([c for c in ref if c["stream"] == STREAM]), by_window(
        [c for c in runs["w1"] if c["stream"] == STREAM])
    for no, e in enumerate(ex, 1):
        e["no"] = no
        others = (ref_by if e["side"] == "simple_only" else w1_by).get(
            (e["slice_id"], e["region_idx"], STREAM), [])
        e["gap"] = nearest_gap(_num(e["onset_sec"]), _num(e["width_sec"]),
                               [_num(x["onset_sec"]) for x in others],
                               [_num(x["width_sec"]) for x in others])
    render(ex, {"count_sliding_w1": runs["w1"], "count_sliding_w2": runs["w2"], "coact": ref}, out)
    # The calls the viewer draws: CoactDetect proposed and both sliding settings, every stream.
    merged = out / "merged"
    merged.mkdir(exist_ok=True)
    allc = ref + runs["w1"] + runs["w2"]
    cols = list(dict.fromkeys(k for c in allc for k in c if k not in ("side",)))
    with (merged / "calls.csv").open("w", encoding="utf-8", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=cols, extrasaction="ignore")
        w.writeheader()
        w.writerows(allc)
    res = json.loads((a.parent / REF_RUN / "results.json").read_text(encoding="utf-8"))
    for k, _, rel in SETTINGS:
        rk = json.loads((a.parent / rel / "results.json").read_text(encoding="utf-8"))
        for s, ch in (rk.get("chosen") or {}).items():
            d = (ch.get("detectors") or {}).get("count_sliding")
            if d:
                res["chosen"][s]["detectors"][f"count_sliding_{k}"] = d
    (merged / "results.json").write_text(json.dumps(res, indent=1, default=str), encoding="utf-8")
    det = write_detections(merged, out)
    tallies = {k: tally(c1[p]) for k, p in (("simple_only", "a_only"), ("coact_only", "b_only"),
                                            ("shared", "shared"))}
    s_all = {s["key"]: s["rows"][0]["share"] for s in shares}
    head = (f"Calls both make, as a share of all distinct calls on fast: count (binned) "
            f"{_f(s_all['binned'])} (this morning), count (sliding) with a 1 s window "
            f"{_f(s_all['w1'])}, with a 2 s window {_f(s_all['w2'])}. Table 1 splits them by "
            "treatment; Table 2 describes the lone calls; the figures below are for the 1 s "
            "window.")
    model = dict(built=_clock(datetime.now(timezone.utc)), dataset=dataset.stamp(), seed=a.seed,
                 shares=shares, tally=tallies, headline=head,
                 examples=[{k: v for k, v in e.items()} for e in ex])
    (out / "gallery.json").write_text(json.dumps(model, indent=1, default=str) + "\n",
                                      encoding="utf-8")
    (out / "index.html").write_text(page(model), encoding="utf-8")
    viewer = REPO / "docs" / "site" / "raster_viewer.html"
    if viewer.exists():
        shutil.copy2(viewer, out / "viewer.html")
    print(f"wrote {det}\nwrote {out / 'index.html'}")
    print(head)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
