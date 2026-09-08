#!/usr/bin/env python3
"""How many cells does a learned model need before it calls a coordinated event?

    python tools/probe_participation.py --spec RUN/02_spec/generator_spec.json \
        [--detections RUN/07_learned/detections.csv --folder EXPORT_FOLDER] \
        [--out DIR] [--also DIR]

WHY THIS EXISTS. Tony, 2026-09-08, on the pilot run's learned detections: *"the
learned detectors fire on a single event in a single roi"*. A detector whose whole
definition is *"the moments when many ROIs fire together"* calling a lone onset is
not a tuning question, so the claim was worth measuring rather than arguing.

It measures two things, and they are independent evidence of the same thing:

* **The ladder** (always). Train the models on a spec exactly the way
  `run_learned_on_folder.py` does — same seeds, same steps, same learning rates, so
  the fitted thresholds come out equal to that run's `learned_settings.csv` — then
  score hand-built rasters in which ``k`` cells fire in the same frame against a
  background of a stated rate. A coordination detector's score must rise with ``k``.
  Whether it does is the whole probe.
* **The tally** (with ``--detections`` and ``--folder``). For each call in a real
  detections file, count the ROIs with an onset within ``--pad`` of the call's own
  span. A call matching one ROI or none is what Tony was looking at.

THE BAKE-OFF CANNOT SEE THIS, which is why it is a separate probe rather than a
column. The generator's rate-robustness negative is the HOT window — a stretch of
raised background with nothing coordinated planted — and `hot_fa` counts firings
into it. A model that divides by its surround passes that by construction: a large
denominator cannot produce a large ratio. The failure it trades into is the other
end of the same fraction, a SMALL denominator, and the simulated corpus has no
quiet-field negative to catch it. `hot_fa` of 0 is therefore not evidence of
robustness on its own, and reading it as such is what this probe exists to stop.

WHAT IT DOES NOT SETTLE. One training seed — the standing limitation of everything
learned in this project, and it bites hardest on a comparison between architectures.
The ladder is synthetic: a single-frame coincidence with no jitter is an easier
event than anything real, so the ladder measures ORDERING (does the score rise with
k?), never an operating point.
"""
from __future__ import annotations

import argparse
import csv
import json
import os
import sys
import tempfile
import warnings
from collections import defaultdict
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))

from bugarach import paths  # noqa: E402

#: The tube 2x2 plus the two baselines, in the bake-off's order. `trace` and `tiny`
#: are included because a probe that only looked at the models under suspicion could
#: not show that the other four are fine.
LEARNED = ("tube", "tube_guard", "tube_ratio", "tube_ratio_guard", "trace", "tiny")

#: `run_learned_on_folder.py`'s rates, repeated rather than imported so that tool
#: can change its own defaults without silently re-fitting this probe's models.
LR = {"tube": 1e-2, "tube_guard": 1e-2, "tube_ratio": 1e-2,
      "tube_ratio_guard": 1e-2, "trace": 1e-3, "tiny": 1e-3}

INK = ["#1b4f72", "#b9770e", "#7d3c98"]


def train_like_the_run(spec, models, *, folds, seeds_per_fold, seed, steps):
    """Fit each architecture the way ``run_learned_on_folder.py`` fits it.

    Same corpus, same split, same hyperparameters, so the threshold this returns is
    the threshold that run wrote down. That equality is the probe's licence to talk
    about the run's calls: a model fitted some other way would be a different model
    and its ladder would say nothing about the detections on disk.
    """
    from bugarach.bench import fold_split
    from bugarach.learn.train import fold_maker, pin_threads, train
    from bugarach.simulate import simulate_coordination

    pin_threads()
    seeds = list(fold_split(n_folds=folds, seeds_per_fold=seeds_per_fold).seeds)
    cache: dict[int, tuple] = {}

    def rec(s):
        if s not in cache:
            cache[s] = simulate_coordination(seed=s, **spec)
        return cache[s]

    mk, n_fit, _ = fold_maker(rec, seeds)
    out = []
    for name in models:
        tr = train(name, mk, n_train=min(10, n_fit), steps=steps, crop=4096,
                   batch=3, lr=LR.get(name, 1e-2), seed=seed)
        print(f"  {name:18} threshold {tr.threshold:.4f}  {tr.n_params} params", flush=True)
        out.append((name, tr))
    return out


def ladder(fitted, *, n_roi, duration_sec, dt, backgrounds, k_max, seed=0):
    """Peak score around a k-cell coincidence, for each k and each background rate.

    The coincidence is planted in ONE frame with no jitter, which is the cleanest
    coordinated event the encoding can carry. If a model does not separate k=1 from
    k=5 here it will not separate them anywhere.
    """
    import torch

    n_frame = int(round(duration_sec / dt))
    rng = np.random.RandomState(seed)
    at = n_frame // 2
    rows = []
    for name, tr in fitted:
        for bg in backgrounds:
            base = np.zeros((n_roi, n_frame), dtype=np.float32)
            if bg > 0:
                base[rng.rand(n_roi, n_frame) < bg * dt] = 1.0
            base[:, at] = 0.0          # the planted moment is ours alone to fill
            for k in range(0, k_max + 1):
                r = base.copy()
                r[:k, at] = 1.0
                with torch.no_grad():
                    s = tr.model(torch.from_numpy(r).unsqueeze(0)).squeeze(0).numpy()
                s = np.asarray(s, dtype=np.float64)
                if s.min() < 0.0 or s.max() > 1.0:      # a model may emit logits
                    s = 1.0 / (1.0 + np.exp(-np.clip(s, -60, 60)))
                half = max(1, int(round(1.0 / dt)))
                rows.append(dict(detector=name, bg_hz=bg, k=k,
                                 score=float(s[max(0, at - half):at + half].max()),
                                 threshold=float(tr.threshold)))
    return rows


def tally(detections: Path, folder: Path, *, pad: float):
    """Per detector: how many real calls land on <=1 ROI, and how quiet it was there.

    ``pad`` widens the call's own span on both sides before counting, because a
    score crosses its threshold a little before or after the onsets that raised it.
    It is a tolerance on the model's timing, not on its participation.
    """
    from bugarach.detectors.rate import recording_extent, stream_trains
    from bugarach.io import load_folder

    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        slices = {s.slice_id: s for s in load_folder(folder)}
    cache: dict[tuple, tuple] = {}

    def trains(sid, stream):
        key = (sid, stream)
        if key not in cache:
            s = slices[sid]
            tr = [np.asarray(v) for v in
                  stream_trains(s.streams[stream], recording_extent(s), "t50rise")]
            flat = np.sort(np.concatenate(tr)) if any(v.size for v in tr) else np.array([])
            cache[key] = (tr, flat)
        return cache[key]

    per = defaultdict(lambda: dict(n=0, lone=0, ctx_lone=[], ctx_multi=[]))
    for r in csv.DictReader(detections.open()):
        sid, stream, det = r["slice_id"], r["stream"], r["detector"]
        if sid not in slices or stream not in slices[sid].streams:
            continue
        a = float(r["onset_sec"])
        b = a + float(r["width_sec"])
        tr, flat = trains(sid, stream)
        n_roi = sum(1 for v in tr if np.any((v >= a - pad) & (v <= b + pad)))
        ctx = int(((flat >= a - 30.0) & (flat <= b + 30.0)).sum())
        d = per[det]
        d["n"] += 1
        if n_roi <= 1:
            d["lone"] += 1
            d["ctx_lone"].append(ctx)
        else:
            d["ctx_multi"].append(ctx)
    return per


def build_ladder(rows, *, width=250, height=200):
    import holoviews as hv
    hv.extension("bokeh")

    dets = list(dict.fromkeys(r["detector"] for r in rows))
    bgs = sorted({r["bg_hz"] for r in rows})
    panels = []
    for i, det in enumerate(dets):
        mine = [r for r in rows if r["detector"] == det]
        thr = mine[0]["threshold"]
        els = [hv.HLine(thr).opts(color="#c0392b", line_dash="dashed", line_width=1)]
        for j, bg in enumerate(bgs):
            pts = sorted(((r["k"], r["score"]) for r in mine if r["bg_hz"] == bg))
            els.append(hv.Curve(pts).opts(color=INK[j % len(INK)], line_width=2))
            els.append(hv.Scatter(pts).opts(color=INK[j % len(INK)], size=5))
        bottom = i >= len(dets) - 3
        panels.append(hv.Overlay(els).opts(
            width=width, height=height + (24 if bottom else 0), toolbar=None,
            show_legend=False, ylim=(-0.03, 1.06), ylabel=f"{det} · score",
            xlabel="cells firing in one frame" if bottom else "",
            xaxis="bottom" if bottom else None, show_grid=False))
    return hv.Layout(panels).cols(3).opts(shared_axes=False, toolbar=None)


def build_tally(per, *, width=760, row_h=26):
    import holoviews as hv
    hv.extension("bokeh")

    rows = [(k, v) for k, v in per.items() if v["n"]]
    rows.sort(key=lambda kv: kv[1]["lone"] / kv[1]["n"])
    labels, els = [], []
    for y, (det, d) in enumerate(rows):
        frac = 100.0 * d["lone"] / d["n"]
        labels.append((y, f"{det} · {d['n']} calls"))
        els.append(hv.Curve([(0, y), (frac, y)]).opts(color="#8b1a1a", line_width=7))
        els.append(hv.Text(frac + 0.6, y, f"{d['lone']}", halign="left",
                           fontsize=8).opts(color="#8b1a1a"))
    top = max((100.0 * d["lone"] / d["n"] for _, d in rows), default=1.0)
    return hv.Overlay(els).opts(
        width=width, height=row_h * max(len(rows), 1) + 60, toolbar=None,
        show_legend=False, ylabel="", yticks=labels, ylim=(-0.7, len(rows) - 0.3),
        xlim=(0, max(top * 1.25, 1.0)),
        xlabel="% of that detector's calls landing on one ROI or none", show_grid=False)


def _chip(colour, text):
    return (f"<span style='display:inline-block;width:11px;height:11px;background:{colour};"
            f"vertical-align:-1px;margin-right:5px'></span><span style='color:{colour}'>{text}</span>")


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--spec", required=True, type=Path,
                    help="generator_spec.json the models are trained on")
    ap.add_argument("--models", nargs="+", default=list(LEARNED))
    ap.add_argument("--detections", type=Path, default=None,
                    help="a detections.csv to tally; needs --folder")
    ap.add_argument("--folder", type=Path, default=None,
                    help="the export folder those detections were made on")
    ap.add_argument("--pad", type=float, default=0.25,
                    help="seconds of timing tolerance around a call's span (default 0.25)")
    ap.add_argument("--n-roi", type=int, default=24,
                    help="field size for the ladder (default 24, the pilot's median)")
    ap.add_argument("--duration-sec", type=float, default=300.0)
    ap.add_argument("--k-max", type=int, default=8)
    ap.add_argument("--seed", type=int, default=0, help="torch seed; one training run each")
    ap.add_argument("--folds", type=int, default=4)
    ap.add_argument("--seeds-per-fold", type=int, default=2)
    ap.add_argument("--steps", type=int, default=900)
    ap.add_argument("--out", type=Path, default=None, help="destination (default: the darkroom)")
    ap.add_argument("--also", type=Path, default=None, help="write a second copy here")
    a = ap.parse_args(argv)

    if (a.detections is None) != (a.folder is None):
        ap.error("--detections and --folder go together: a call's participation "
                 "cannot be counted without the recording it was made on")

    gen = json.loads(a.spec.read_text())
    gen = gen.get("generator", gen)
    dt = float(gen.get("grid_sec", 0.1))
    bg = float(gen.get("bg_rate_hz", 0.0042))
    backgrounds = [0.0, bg / 2.0, bg]

    if a.out is None:
        root = paths.darkroom(create=True)
        if root is None:
            print(paths.unresolved_message(), file=sys.stderr)
            return 2
        a.out = root / "participation_probe"
    a.out.mkdir(parents=True, exist_ok=True)

    print(f"fitting {len(a.models)} architecture(s) on {a.spec.name}")
    fitted = train_like_the_run(gen, a.models, folds=a.folds,
                                seeds_per_fold=a.seeds_per_fold, seed=a.seed,
                                steps=a.steps)
    rows = ladder(fitted, n_roi=a.n_roi, duration_sec=a.duration_sec, dt=dt,
                  backgrounds=backgrounds, k_max=a.k_max, seed=a.seed)
    with (a.out / "participation_ladder.csv").open("w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=list(rows[0]), lineterminator="\n")
        w.writeheader()
        w.writerows(rows)

    per = tally(a.detections, a.folder, pad=a.pad) if a.detections else {}
    if per:
        with (a.out / "participation_tally.csv").open("w", newline="") as fh:
            w = csv.writer(fh, lineterminator="\n")
            w.writerow(["detector", "n_calls", "n_lone", "pct_lone",
                        "median_events_within_30s_lone", "median_events_within_30s_multi"])
            for det, d in sorted(per.items()):
                w.writerow([det, d["n"], d["lone"], f"{100.0*d['lone']/d['n']:.1f}",
                            f"{np.median(d['ctx_lone']):.0f}" if d["ctx_lone"] else "",
                            f"{np.median(d['ctx_multi']):.0f}" if d["ctx_multi"] else ""])

    import panel as pn
    from make_generator_figures import _write

    bgtxt = " · ".join(f"{v:g} Hz" for v in backgrounds)
    head = (
        f"<div style='font:13px system-ui,sans-serif;color:#111;max-width:1060px'>"
        f"<b style='font-size:16px'>how many cells does a learned model need?</b> &nbsp;—&nbsp; "
        f"{a.n_roi} ROI, {a.duration_sec:g} s, {dt:g} s grid; k cells fire in ONE frame, no "
        f"jitter — the cleanest coordinated event the encoding can carry.<br>"
        f"Per-ROI background, one curve each: {bgtxt}. "
        f"Models fitted on <code>{a.spec.name}</code> exactly as "
        f"<code>run_learned_on_folder.py</code> fits them, so each threshold equals that "
        f"run's.<br><b>Read the ORDERING, not the level.</b> A coordination detector's score "
        f"must rise with k. Where it does not, the model is answering some other question.<br>"
        f"<div style='margin:5px 0 0'>{_chip(INK[0], f'{backgrounds[0]:g} Hz (silent)')} &nbsp; "
        f"{_chip(INK[1], f'{backgrounds[1]:.4g} Hz')} &nbsp; "
        f"{_chip(INK[2], f'{backgrounds[2]:.4g} Hz (the spec)')} &nbsp; "
        f"<span style='color:#c0392b'>- - -</span> that model's own fitted threshold</div>"
        f"<div style='margin:4px 0 0;color:#777;font-size:11px'>{a.spec.name} · one training "
        f"seed ({a.seed}), {a.steps} steps</div></div>")
    _write(pn.Column(pn.pane.HTML(head), pn.pane.HoloViews(build_ladder(rows))),
           a.out, "participation_ladder", png=True)

    if per:
        head2 = (
            f"<div style='font:13px system-ui,sans-serif;color:#111;max-width:1060px'>"
            f"<b style='font-size:16px'>real calls that match one ROI or none</b> &nbsp;—&nbsp; "
            f"every call in <code>{a.detections.name}</code>, against the recordings in "
            f"<code>{a.folder.name}</code>. A call counts as lone when at most one ROI has an "
            f"onset within &plusmn;{a.pad:g} s of the call's own span.<br>"
            f"The number at the end of a bar is the count. Per-detector medians of how busy "
            f"the surrounding &plusmn;30 s was, lone against not, are in "
            f"<code>participation_tally.csv</code>.<br>"
            f"<div style='margin:4px 0 0;color:#777;font-size:11px'>{a.detections.parent.name}/"
            f"{a.detections.name}</div></div>")
        _write(pn.Column(pn.pane.HTML(head2), pn.pane.HoloViews(build_tally(per))),
               a.out, "participation_tally", png=True)

    if a.also:
        a.also.mkdir(parents=True, exist_ok=True)
        for f in sorted(a.out.glob("participation_*")):
            with tempfile.TemporaryDirectory() as td:
                tmp = Path(td) / f.name
                tmp.write_bytes(f.read_bytes())
                os.replace(tmp, a.also / f.name)
        print(f"also {a.also}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
