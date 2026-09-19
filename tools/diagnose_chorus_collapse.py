#!/usr/bin/env python3
"""Why a third of chorus_norm's fits make one call per recording: the diagnosis, from the runs' own fits.

    python tools/diagnose_chorus_collapse.py table   --code <checkout>          # collapse vs configuration
    python tools/diagnose_chorus_collapse.py census  --code <checkout>          # what a collapsed fit is
    python tools/diagnose_chorus_collapse.py trace   --code <checkout>          # the problem, drawn
    python tools/diagnose_chorus_collapse.py replay  --code <checkout> CFG SEED RECS [--lr X] [--warmup N]
    python tools/diagnose_chorus_collapse.py page    [--also docs/learned/chorus_collapse/index.html]

The replicate report (docs/learned/tuned_vs_coact/replicate1/) found that in both draws of goal 2's
comparison about a third of chorus_norm's inner fits made exactly one call per recording, F1 0.125.
This tool answers why, reading nothing but the two runs' result folders in the darkroom:

- ``table`` joins every fit's collapse status (the report's Table 2 rule: exactly one call on every
  recording of every fold it was scored on, at its own threshold) to its role and configuration.
- ``census`` reloads every second-draw chorus fit and runs it on one bench recording, recording for
  each how many units of each head layer (the stack that maps the pooled per-ROI statistics to the
  output) pass anything that varies, how much the output varies, and how well the head's input and
  the output separate event frames from the rest.
- ``trace`` runs one collapsed fit and one working fit (``SHOWN``) on a recording held out from both
  and keeps their output over time, their calls and the planted events.
- ``replay`` re-runs one second-draw chorus_norm inner fit exactly as ``bugarach.learn.train.train``
  ran it — same seed, same recordings in the same order, same crops, on the GPU with deterministic
  kernels — logging the loss and each head layer's varying units every 10 steps, and checks the
  result against the saved checkpoint tensor by tensor. ``--lr`` and ``--warmup`` turn it into a
  counterfactual: the same fit with only that changed. Nothing the runs wrote is modified.
- ``page`` draws the figures and writes the readout: the darkroom by default, ``--also`` for the repo.

``--code`` names a checkout whose ``src`` registers chorus_norm and chorus_gain_norm (on
2026-09-19 that is branch ``replicate-run``, the code the second draw ran; they are not on ``main``).
The tool refuses when they are not registered rather than building something else under the name:
a bare ``build_chorus_norm()`` silently builds plain chorus.
"""

from __future__ import annotations

import argparse
import json
import math
import random
import re
import statistics as st
import sys
from collections import defaultdict
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / "tools"))
import make_replicate_report as R  # noqa: E402  (SVG kit, page CSS, archive reader, darkroom names)

FOLDER = "2026-09-19-chorus-collapse"
CHORUS = ("chorus_norm", "chorus_gain_norm")
DRAW_DIRS = {"first": R.THEIRS_FOLDER, "second": R.MINE_FOLDER}
REGIMES = {"quiet": "baseline_quiet", "busy": "baseline_busy"}
PROBE_RECORDING = "quiet:2000"      # the census recording: one bench recording, the same for every fit
# A head unit is silent on a recording when its output's standard deviation over the frames is below
# this: it passes (almost) nothing that changes. Round 1 of the review counted a unit dead when its
# output never rose above 0.001; that is a sign test, and GELU's negative lobe carries signal (and
# gradient) without ever going positive, so it counted layers that still transmit.
SILENT = 1e-3
# The fits the replays follow: one collapsed and the one working second-draw fit of the same
# configuration (lr 0.03, encoder 4 units wide and 6 layers deep, 1,800 steps).
SHOWN = {"collapsed": ("2736f584e7c224e3", 0, "3a17721a7a"),
         "working": ("2736f584e7c224e3", 2, "ecf4b9b71a")}


def _results(draw: str) -> Path:
    from bugarach.paths import darkroom, unresolved_message
    p = darkroom(DRAW_DIRS[draw], "results")
    if p is None:
        raise SystemExit(unresolved_message("--work"))
    return Path(p)


def _use_code(code: Path | None) -> None:
    """Put the checkout that registers the chorus nets first on the path, and refuse otherwise."""
    if code is not None:
        sys.path.insert(0, str(Path(code).resolve() / "src"))
    from bugarach.learn.nets import ARCHITECTURES
    missing = [n for n in CHORUS if n not in ARCHITECTURES]
    if missing:
        raise SystemExit(f"{', '.join(missing)} not registered in this code; pass --code with a "
                         "checkout of branch replicate-run (the code the runs trained with)")


# ---- table -------------------------------------------------------------------------------------

def collapse_table() -> list[dict]:
    """Every fit of the two chorus nets, both draws, with its role (an inner fit, or a refit of the
    configuration tuning chose), its configuration, and whether it collapsed: exactly one call on
    every recording of every fold it was scored on, at its own threshold."""
    rows = []
    for draw in DRAW_DIRS:
        folder = _results(draw)
        fits = {}
        for name, raw in R.Archive(folder, "fits").items(lambda n: n.endswith(".run.json")):
            parts = name.split("/")
            if parts[1] not in CHORUS:
                continue
            m = re.match(r"seed(\d+)__recs-([0-9a-f]+)\.run\.json$", parts[-1])
            fits[(parts[1], parts[2], int(m.group(1)), m.group(2))] = json.loads(raw)
        one = defaultdict(lambda: [0, 0])
        for name, raw in R.Archive(folder, "scores").items(
                lambda n: n.count("/") == 3 and n.split("/")[1] in CHORUS):
            parts = name.split("/")
            m = re.match(r"seed(\d+)__recs-([0-9a-f]+)__fold(\d+)\.json$", parts[3])
            key = (parts[1], parts[2], int(m.group(1)), m.group(2))
            if key not in fits:
                continue
            d = json.loads(raw)
            c = one[key]
            c[1] += 1
            c[0] += all(r[d["own_index"]]["n_detected"] == 1 for r in d["rows"].values())
        for key, (k, s) in one.items():
            net, cfg, seed, recs = key
            conf = json.loads((folder / "configs" / net / f"{cfg}.json").read_text())
            c, tr = conf["cfg"], conf["training"]
            rows.append(dict(draw=draw, net=net, cfg=cfg, seed=seed, recs=recs, role=fits[key]["role"],
                             pair=sorted(fits[key]["train_folds"]), collapsed=k == s,
                             lr=tr["lr"], steps=tr["steps"], width=c["roi_width"],
                             depth=c["roi_depth"], top_m=c["top_m"], vote_gain=c.get("vote_gain"),
                             untuned=conf["is_untuned"]))
    return rows




# ---- census ------------------------------------------------------------------------------------

def _fit_bytes(net: str, cfg: str, seed: int, recs: str, suffix: str = ".json") -> bytes:
    """One member of the second draw's fit archive, read through the report's archive reader."""
    want = f"fits/{net}/{cfg}/seed{seed}__recs-{recs}{suffix}"
    for name, raw in R.Archive(_results("second"), "fits").items(lambda n: n == want):
        return raw
    raise SystemExit(f"{want} is not in the second draw's fit archive")


def _load_fit(net: str, cfg: str, seed: int, recs: str):
    """A saved fit, through the project's own loader (which reads a path, hence the temp file)."""
    import tempfile

    from bugarach.learn import checkpoint
    with tempfile.TemporaryDirectory() as d:
        p = Path(d) / "fit.json"
        p.write_bytes(_fit_bytes(net, cfg, seed, recs))
        return checkpoint.load(p)


def _bench(rec_id: str):
    """A bench recording by its run id ("quiet:2000"), encoded with its per-frame event labels,
    exactly as the trainer builds one."""
    from bugarach.bench import make_recording
    from bugarach.learn import train as T
    reg, s = rec_id.split(":")
    enc, y, gt = T._recording(lambda seed: make_recording(REGIMES[reg], seed), int(s), 0.1, None)
    return enc, y, gt


def _selectivity(z, y) -> float:
    """How well a signal separates event frames from the rest: the largest standardized difference
    of means (event minus other, over the pooled standard deviation) across its channels."""
    import numpy as np
    z = np.atleast_2d(z)
    on, off = z[:, y > 0], z[:, y == 0]
    sd = np.sqrt((on.var(axis=1) + off.var(axis=1)) / 2) + 1e-12
    return float(np.max(np.abs(on.mean(axis=1) - off.mean(axis=1)) / sd))


def _head_probe(model, raster, y) -> dict:
    """Run one fit on one recording and look inside its head: for each of the head's GELU layers,
    the share of units whose output varies over the recording (standard deviation over its frames
    at least ``SILENT``) and the share that is ever positive (the rule round 1 of the review used,
    kept for comparison); how well the head's input and the output separate event frames."""
    import numpy as np
    import torch
    varying, positive, head_in = [], [], []

    def take_input(mod, args):         # hooks return None, so they observe and change nothing
        head_in.append(args[0][0])

    def take_layer(mod, args, o):
        varying.append(float((o[0].std(dim=1) >= SILENT).float().mean()))
        positive.append(float((o[0] > 1e-3).any(dim=1).float().mean()))

    hooks = [model.head.register_forward_pre_hook(take_input)]
    hooks += [g.register_forward_hook(take_layer) for g in model.head
              if isinstance(g, torch.nn.GELU)]
    with torch.no_grad():
        logit = model(torch.from_numpy(np.asarray(raster, dtype=np.float32)).unsqueeze(0))[0]
    for h in hooks:
        h.remove()
    return dict(varying=varying, positive=positive, logit=logit.numpy(),
                d_in=_selectivity(head_in[0].numpy(), y), d_out=_selectivity(logit.numpy(), y))


def census(rows: list[dict]) -> list[dict]:
    """Every second-draw chorus fit, inner fits and refits, on one bench recording of that draw."""
    enc, y, _ = _bench(PROBE_RECORDING)
    out = []
    for r in rows:
        if r["draw"] != "second":
            continue
        fit = _load_fit(r["net"], r["cfg"], r["seed"], r["recs"])
        m = fit.model.cpu().eval()
        p = _head_probe(m, enc.raster, y)
        entry = dict(net=r["net"], cfg=r["cfg"], seed=r["seed"], recs=r["recs"], role=r["role"],
                     lr=r["lr"], collapsed=r["collapsed"],
                     min_share_varying=min(p["varying"]), min_share_positive=min(p["positive"]),
                     logit_sd=float(p["logit"].std()), d_in=p["d_in"], d_out=p["d_out"],
                     threshold=float(fit.threshold))
        if r["net"] == "chorus_gain_norm":
            # the largest change across the fit's vote gains, as a fraction of where they started
            entry["vote_gain_moved"] = float((m.vote_gain.detach() / r["vote_gain"] - 1).abs().max())
        out.append(entry)
    return out


# ---- trace: the problem itself -----------------------------------------------------------------

def trace() -> dict:
    """The collapsed fit and the working fit that the replays follow (``SHOWN``), run on one
    recording held out from both: their output over time, their calls, and the planted events."""
    import numpy as np

    from bugarach.learn.encode import decode
    runs = {k: json.loads(_fit_bytes("chorus_norm", *SHOWN[k], suffix=".run.json")) for k in SHOWN}
    trained_on = set().union(*(set(r["recordings"]) for r in runs.values()))
    # the recordings both fits were scored on, less everything either trained or picked a threshold on
    scored = None
    for k, (cfg, seed, recs) in SHOWN.items():
        names = set()
        for _, raw in R.Archive(_results("second"), "scores").items(
                lambda n: n.startswith(f"scores/chorus_norm/{cfg}/seed{seed}__recs-{recs}__fold")):
            names |= set(json.loads(raw)["rows"])
        scored = names if scored is None else scored & names
    rec_id = sorted(x for x in scored - trained_on if x.startswith("quiet:"))[0]
    enc, y, gt = _bench(rec_id)
    bin_ = 10
    doc = dict(recording=rec_id, dt=float(enc.dt), n_frames=int(enc.n_frame), bin_frames=bin_,
               events=[[float(a) - float(enc.t0), float(b) - float(enc.t0)]
                       for a, b in (e.observed_span for e in gt.events)], fits={})
    for k, (cfg, seed, recs) in SHOWN.items():
        fit = _load_fit("chorus_norm", cfg, seed, recs)
        logit = _head_probe(fit.model.cpu().eval(), enc.raster, y)["logit"].astype(float)
        det = decode(1 / (1 + np.exp(-logit)), threshold=fit.threshold,
                     merge_gap_frames=fit.merge_gap_frames)
        nb = len(logit) // bin_
        blocks = logit[:nb * bin_].reshape(nb, bin_)
        doc["fits"][k] = dict(cfg=cfg, seed=seed, recs=recs, threshold=float(fit.threshold),
                              threshold_logit=float(np.log(fit.threshold / (1 - fit.threshold))),
                              lo=[round(float(v), 4) for v in blocks.min(axis=1)],
                              hi=[round(float(v), 4) for v in blocks.max(axis=1)],
                              calls=[[int(a), int(w)]
                                     for a, w in zip(det.onset_frame, det.width_frame)])
    return doc


# ---- replay ------------------------------------------------------------------------------------

def replay(cfg_key: str, seed: int, recs_hash: str, *, lr: float | None, warmup: int,
           net: str = "chorus_norm") -> dict:
    """One inner fit re-run exactly as `train.train` ran it (see the module docstring)."""
    import numpy as np
    import torch

    from bugarach.bench import make_recording
    from bugarach.learn import train as T
    from bugarach.learn.nets import ARCHITECTURES

    res = _results("second")
    run = json.loads(_fit_bytes(net, cfg_key, seed, recs_hash, suffix=".run.json"))
    saved = _load_fit(net, cfg_key, seed, recs_hash)
    conf = json.loads((res / "configs" / net / f"{cfg_key}.json").read_text())
    tr = conf["training"]
    # the settings this loop hard-codes must be the ones the fit was made with
    t = saved.training
    assert t["device"] == "cuda" and t["dt_sec"] == 0.1 and t["stream"] is None, t
    assert t["gpu"] == torch.cuda.get_device_name(0), (t["gpu"], torch.cuda.get_device_name(0))
    cache = {}

    def planted(rid):
        if rid not in cache:
            reg, s = rid.split(":")
            cache[rid] = make_recording(REGIMES[reg], int(s))
        return cache[rid]

    mk, _, _ = T.fold_maker(planted, run["recordings"])
    dev = torch.device("cuda")
    T.deterministic_cuda()
    torch.manual_seed(seed)
    T.pin_threads()
    model = ARCHITECTURES[net].make(**conf["overrides"]).to(dev)
    base_lr = float(tr["lr"]) if lr is None else float(lr)
    opt = torch.optim.Adam(model.parameters(), lr=base_lr)
    seeds = [T.TRAIN_SEED_BLOCK + seed * 1000 + i for i in range(int(tr["n_train"]))]
    data = [T._recording(mk, s, 0.1, None)[:2] for s in seeds]
    pos = float(np.mean([y.mean() for _, y in data]))
    lossf = torch.nn.BCEWithLogitsLoss(
        pos_weight=torch.tensor([(1 - pos) / max(pos, 1e-6)], dtype=torch.float32).to(dev))
    pos_idx = [np.flatnonzero(y > 0) for _, y in data]
    rng = np.random.RandomState(seed)
    crop, batch, steps = int(tr["crop_frames"]), int(tr["batch"]), int(tr["steps"])

    gelus = [g for g in model.head if isinstance(g, torch.nn.GELU)]
    varying = {}
    # a unit varies when its output's standard deviation over the batch's frames reaches SILENT
    hooks = [g.register_forward_hook(lambda mod, i, o, k=k: varying.__setitem__(
        k, float((o.transpose(0, 1).reshape(o.shape[1], -1).std(dim=1) >= SILENT).float().mean())))
        for k, g in enumerate(gelus)]
    log = []
    model.train()
    for step in range(steps):          # the loop below is train.train's, line for line
        xs, ys = [], []
        for _ in range(batch):
            di = rng.randint(len(data))
            enc, y = data[di]
            if enc.n_frame <= crop:
                xx, yy = enc.raster, y
            else:
                pi = pos_idx[di]
                if pi.size and rng.rand() < 0.5:
                    c = int(pi[rng.randint(pi.size)])
                    a = int(np.clip(c - crop // 2, 0, enc.n_frame - crop))
                else:
                    a = rng.randint(0, enc.n_frame - crop)
                xx, yy = enc.raster[:, a:a + crop], y[a:a + crop]
            xs.append(torch.from_numpy(np.ascontiguousarray(xx)))
            ys.append(torch.from_numpy(np.ascontiguousarray(yy)))
        xb, yb = torch.stack(xs).to(dev), torch.stack(ys).to(dev)
        if warmup:                     # linear warm-up: the only line train() does not have
            for g in opt.param_groups:
                g["lr"] = base_lr * min(1.0, (step + 1) / warmup)
        opt.zero_grad()
        out = model(xb)
        loss = lossf(out, yb)
        loss.backward()
        opt.step()
        if step % 10 == 0 or step == steps - 1:
            log.append(dict(step=step, loss=float(loss.detach()),
                            logit_sd=float(out.detach().std()),
                            head_varying=[varying[k] for k in range(len(gelus))]))
    for h in hooks:
        h.remove()
    doc = dict(net=net, cfg=cfg_key, seed=seed, recs=recs_hash, lr=base_lr, warmup=warmup,
               as_run=(lr is None and not warmup), config_lr=float(tr["lr"]), steps=steps,
               torch=torch.__version__, gpu=torch.cuda.get_device_name(0),
               deterministic=bool(torch.are_deterministic_algorithms_enabled()), log=log)
    if doc["as_run"]:
        # the replay must BE the run's fit: every tensor against the saved checkpoint
        ref = saved.model.state_dict()
        mine = model.state_dict()
        doc["max_abs_diff_vs_checkpoint"] = max(
            float((mine[k].cpu() - ref[k].cpu()).abs().max()) for k in mine)
    return doc



# ---- page --------------------------------------------------------------------------------------

LRS = (0.003, 0.01, 0.03)                    # the learning rates the tuning grid declared
SHAPES = ((4, 4), (4, 6), (8, 4), (8, 6))    # the per-ROI encoder's (width, depth) pairs in the grid
N_PERM = 1999                                # shuffles for the clustering tests
DIAGNOSIS_596 = "7fc052d"                    # the commit on replicate-run carrying PR #596's diagnosis


def _minutes(sec: float) -> str:
    """A time label in the house's 60-base style: 0, 45s, 5m, 2m30s."""
    s = int(round(sec))
    if s == 0:
        return "0"
    m, r = divmod(s, 60)
    return (f"{m}m" if m else "") + (f"{r}s" if r else "")


def _identity(r: dict) -> tuple:
    """What a configuration is, apart from how long it trains."""
    return (r["net"], r["lr"], r["width"], r["depth"], r["top_m"], r["vote_gain"])


def _twin_groups(rows: list[dict]) -> list[list[str]]:
    """Configurations identical but for step count, shortest first. Training is deterministic and
    the step count only decides where it stops, so a shorter twin's fit is its longer twin's fit
    cut off early: the same trajectory, not a second sample."""
    by, steps = defaultdict(set), {}
    for r in rows:
        by[_identity(r)].add(r["cfg"])
        steps[r["cfg"]] = r["steps"]
    return [sorted(g, key=lambda c: steps[c]) for g in by.values() if len(g) > 1]


def _cluster_test(rows: list[dict], net: str, level, rnd: random.Random) -> float:
    """Does collapse cluster by ``level`` (training seed, or fold pair) inside a configuration?
    Statistic: over every (draw, configuration), the spread across levels of the collapsed count;
    null: the collapse labels shuffled within each (draw, configuration). Shorter twins are left out,
    since they repeat their longer twin. Pooling over configurations cannot see such an effect, which
    is why the test is made inside them. Returns the permutation p value."""
    shorter = {c for g in _twin_groups(rows) for c in g[:-1]}
    groups = defaultdict(list)
    for r in rows:
        if r["net"] == net and r["cfg"] not in shorter:
            groups[(r["draw"], r["cfg"])].append((level(r), r["collapsed"]))

    def stat(labelled):
        tot = 0.0
        for items in labelled:
            counts = defaultdict(int)
            for lv, c in items:
                counts[lv] += c
            vals = list(counts.values())
            mu = sum(vals) / len(vals)
            tot += sum((v - mu) ** 2 for v in vals)
        return tot

    obs = stat(groups.values())
    hits = 0
    for _ in range(N_PERM):
        shuffled = []
        for items in groups.values():
            labels = [c for _, c in items]
            rnd.shuffle(labels)
            shuffled.append([(lv, c) for (lv, _), c in zip(items, labels)])
        hits += stat(shuffled) >= obs
    return (1 + hits) / (N_PERM + 1)


def _ypanel_label(svg, x, y, text):
    svg.add(f'<text x="0" y="0" font-size="12" text-anchor="middle" fill="var(--ink-2)" '
            f'transform="translate({x},{y:.1f}) rotate(-90)">{R.esc(text)}</text>')


def _polyline(svg, pts, col, *, width=2, dash=None, title=None):
    d = f' stroke-dasharray="{dash}"' if dash else ""
    t = f"<{R.SVG_TITLE}>{R.esc(title)}</{R.SVG_TITLE}>" if title else ""
    svg.add(f'<polyline fill="none" stroke="{col}" stroke-width="{width}"{d} points="'
            + " ".join(f"{a:.1f},{b:.1f}" for a, b in pts) + f'">{t}</polyline>')


def fig_problem(tr: dict) -> str:
    """The problem itself: a collapsed fit and a working fit of the same configuration on one
    recording held out from both. Calls and planted events in the lane above; each fit's output
    below, on its own y range with its own threshold."""
    left, top, pw = 175, 10, 700
    lane_h, ph, gap = 22, 120, 26
    w = left + pw + 20
    h = top + 3 * lane_h + 10 + 2 * ph + gap + 70
    svg = R.Svg(w, h, "the output of a collapsed fit and a working one")
    total = tr["n_frames"] * tr["dt"]
    sx = lambda sec: left + sec / total * pw
    cols = {"working": "var(--c1)", "collapsed": "var(--c2)"}
    # lane: planted events (down-pointing, at the raster-free traces below), then each fit's calls
    rows = [("planted events", None), ("working fit's calls", "working"),
            ("collapsed fit's calls", "collapsed")]
    for i, (label, k) in enumerate(rows):
        y = top + i * lane_h + lane_h / 2
        svg.text(left - 10, y + 4, label, size=12, anchor="end", fill="var(--ink-2)")
        if i % 2:
            svg.rect(left, y - lane_h / 2 + 1, pw, lane_h - 2, fill="var(--band)")
        if k is None:
            for a, b in tr["events"]:
                xm = sx((a + b) / 2)
                svg.add(f'<path d="M{xm - 5:.1f},{y - 5:.1f} L{xm + 5:.1f},{y - 5:.1f} '
                        f'L{xm:.1f},{y + 5:.1f} z" fill="var(--ink)"><{R.SVG_TITLE}>planted event '
                        f'at {_minutes(a)}</{R.SVG_TITLE}></path>')
        else:
            for a, wd in tr["fits"][k]["calls"]:
                x0, x1 = sx(a * tr["dt"]), sx((a + wd) * tr["dt"])
                svg.rect(x0, y - 5, max(2.0, x1 - x0), 10, fill=cols[k],
                         title=f"{label[:-8]} call from {_minutes(a * tr['dt'])}, "
                               f"{wd * tr['dt']:.1f} s long")
    # the two outputs
    y0 = top + 3 * lane_h + 10
    for j, k in enumerate(("working", "collapsed")):
        f = tr["fits"][k]
        pt = y0 + j * (ph + gap)
        lo, hi = min(min(f["lo"]), f["threshold_logit"]), max(max(f["hi"]), f["threshold_logit"])
        pad = 0.08 * (hi - lo)
        lo, hi = lo - pad, hi + pad
        sy = lambda v: pt + ph - (v - lo) / (hi - lo) * ph
        svg.rect(left, pt, pw, ph, stroke="var(--rule)")
        for t in (math.ceil(lo), math.floor(hi)):
            svg.text(left - 6, sy(t) + 4, f"{t}".replace("-", "−"), size=12, anchor="end",
                     fill="var(--ink-2)")
        bw = f.get("bin", tr["bin_frames"]) * tr["dt"]
        up = [(sx(i * bw), sy(v)) for i, v in enumerate(f["hi"])]
        dn = [(sx(i * bw), sy(v)) for i, v in enumerate(f["lo"])][::-1]
        svg.add(f'<polygon fill="{cols[k]}" fill-opacity="0.85" stroke="{cols[k]}" '
                f'stroke-width="0.6" points="' + " ".join(f"{a:.1f},{b:.1f}" for a, b in up + dn)
                + f'"><{R.SVG_TITLE}>{k} fit: output logit, lowest to highest in each '
                f'{bw:.0f}-second bin</{R.SVG_TITLE}></polygon>')
        svg.line(left, sy(f["threshold_logit"]), left + pw, sy(f["threshold_logit"]),
                 stroke="var(--ink)", width=1.2, dash="5 4")
        _ypanel_label(svg, left - 44, pt + ph / 2, f"{k} fit · logit")
        svg.text(left + pw - 4, sy(f["threshold_logit"]) - 5,
                 f"threshold, {f['threshold_logit']:.1f}".replace("-", "−"), size=12,
                 anchor="end", fill="var(--ink-2)")
    base = y0 + 2 * ph + gap
    ticks = [t for t in range(0, int(total) + 1, 300)]
    svg.line(left, base + 4, left + pw, base + 4, stroke="var(--ink-3)")
    for t in ticks:
        svg.line(sx(t), base + 4, sx(t), base + 8, stroke="var(--ink-3)")
        svg.text(sx(t), base + 21, _minutes(t), size=12, anchor="middle", fill="var(--ink-2)")
    svg.text(left + pw / 2, base + 38, "time in the recording", size=12, anchor="middle",
             fill="var(--ink-2)")
    ky = h - 8
    svg.line(left, ky - 4, left + 24, ky - 4, stroke="var(--ink)", width=1.2, dash="5 4")
    svg.text(left + 30, ky, "the fit's own threshold, as a logit", size=12)
    return svg.render()


def fig_rates(rows: list[dict]) -> str:
    """Share of each configuration's inner fits that collapsed, both draws pooled, by learning rate.
    Configurations with the same share stack vertically, so every configuration is one visible dot."""
    left, top, rh, pw, gap = 130, 34, 50, 320, 110
    w = left + 2 * (pw + gap)
    h = top + rh * 3 + 70
    svg = R.Svg(w, h, "collapse share by configuration and learning rate")
    for j, net in enumerate(CHORUS):
        x0 = left + j * (pw + gap)
        sx = R.x_axis(svg, x0, x0 + pw, top + rh * 3 + 4, 0, 1, (0, 0.25, 0.5, 0.75, 1.0),
                      "share of the configuration's 36 inner fits that collapsed", fmt="{:.2f}")
        svg.text(x0, top - 14, f"{'A' if j == 0 else 'B'} · {net}", size=12, weight="bold")
        for i, lr in enumerate(LRS):
            y = top + i * rh + rh / 2
            rs = [r for r in rows if r["net"] == net and r["lr"] == lr]
            if j == 0:
                svg.text(left - 12, y + 4, f"learning rate {lr:g}", anchor="end", size=12)
            # the row's total, beside the panel: collapsed fits over all its configurations
            svg.text(x0 + pw + 8, y, f"{sum(r['collapsed'] for r in rs)} of {len(rs)}", size=11,
                     fill="var(--ink-2)")
            svg.text(x0 + pw + 8, y + 13, "fits", size=11, fill="var(--ink-2)")
            if i % 2:
                svg.rect(x0, y - rh / 2 + 2, pw, rh - 4, fill="var(--band)")
            per = defaultdict(lambda: [0, 0])
            shape = {}
            for r in rs:
                per[r["cfg"]][0] += r["collapsed"]
                per[r["cfg"]][1] += 1
                shape[r["cfg"]] = (r["width"], r["depth"], r["top_m"], r["steps"])
            stacks = defaultdict(list)
            for k, (c, n) in sorted(per.items()):
                stacks[c].append((k, n))
            for c, ks in stacks.items():
                for q, (k, n) in enumerate(ks):
                    yy = y + (q - (len(ks) - 1) / 2) * 9
                    wd, dp, tm, stp = shape[k]
                    svg.circle(sx(c / n), yy, 4.5, fill="var(--c1)", stroke="var(--surface)",
                               width=1, title=f"{net}, encoder {wd} wide × {dp} deep, top {tm}, "
                                              f"{stp:,} steps, lr {lr:g} ({k[:8]}): {c} of {n} "
                                              f"fits collapsed")
    return svg.render()


def fig_census(cen: list[dict]) -> str:
    """Each second-draw inner fit: the smallest share of varying units in any head layer, against
    the spread of its output. Spreads below the axis floor are drawn hollow on the floor."""
    left, top, ph, pw, gap = 78, 30, 260, 380, 60
    w = left + 2 * pw + gap + 30
    h = top + ph + 90
    svg = R.Svg(w, h, "silent head layers and flat outputs")
    lo, hi = -3, 2                                   # log10 of the logit's standard deviation
    sup = str.maketrans("-0123456789", "⁻⁰¹²³⁴⁵⁶⁷⁸⁹")
    for j, net in enumerate(CHORUS):
        x0 = left + j * (pw + gap)
        sx = R.x_axis(svg, x0, x0 + pw, top + ph + 4, 0, 1, (0, 0.25, 0.5, 0.75, 1.0),
                      "smallest share of varying units in any head layer", fmt="{:.2f}")
        sy = lambda v: top + ph - (v - lo) / (hi - lo) * ph
        for t in range(lo, hi + 1):
            svg.line(x0, sy(t), x0 + pw, sy(t), stroke="var(--rule)")
            if j == 0:
                svg.text(x0 - 8, sy(t) + 4, ("≤ " if t == lo else "") + "10" + str(t).translate(sup),
                         size=12, anchor="end", fill="var(--ink-2)")
        svg.text(x0, top - 12, f"{'A' if j == 0 else 'B'} · {net}", size=12, weight="bold")
        rnd = random.Random(1)
        for e in cen:
            if e["net"] != net:
                continue
            xj = min(1, max(0, e["min_share_varying"] + rnd.uniform(-0.02, 0.02)))
            floored = e["logit_sd"] < 10 ** lo
            v = lo if floored else math.log10(e["logit_sd"])
            svg.circle(sx(xj), sy(v), 3, stroke="none", opacity=0.55, hollow=floored,
                       fill="var(--c2)" if e["collapsed"] else "var(--c1)",
                       title=f"{net} {e['cfg'][:8]} seed {e['seed']} recs {e['recs']}: "
                             f"{'collapsed' if e['collapsed'] else 'working'}, smallest varying "
                             f"share {e['min_share_varying']:.3f}, output SD {e['logit_sd']:.4g}")
    _ypanel_label(svg, 18, top + ph / 2, "SD of the output logit (log scale)")
    ly = h - 14
    keys = (("var(--c2)", "collapsed", False), ("var(--c1)", "working", False),
            ("var(--ink-2)", "hollow: SD below 10⁻³, drawn on the floor", True))
    xk = left
    for col, words, hollow in keys:
        svg.circle(xk + 6, ly - 4, 5, fill=col, stroke="none", hollow=hollow)
        svg.text(xk + 16, ly, words, size=12)
        xk += 30 + 7.2 * len(words)
    return svg.render()


def fig_selectivity(cen: list[dict]) -> str:
    """How well the head's input and the output separate event frames from the rest."""
    left, top, ph, pw, gap = 70, 30, 250, 380, 60
    w = left + 2 * pw + gap + 30
    h = top + ph + 90
    svg = R.Svg(w, h, "the head's input still sees events; a collapsed fit's output does not")
    hi_x = max(e["d_in"] for e in cen) * 1.05
    hi_y = max(e["d_out"] for e in cen) * 1.05
    top_ = max(hi_x, hi_y)
    ticks = [t for t in range(0, int(top_) + 1) if t % max(1, int(top_ // 5) or 1) == 0]
    for j, net in enumerate(CHORUS):
        x0 = left + j * (pw + gap)
        sx = R.x_axis(svg, x0, x0 + pw, top + ph + 4, 0, top_, ticks,
                      "event separation at the head's input (d)", fmt="{:.0f}")
        sy = lambda v: top + ph - v / top_ * ph
        for t in ticks:
            svg.line(x0, sy(t), x0 + pw, sy(t), stroke="var(--rule)")
            if j == 0:
                svg.text(x0 - 8, sy(t) + 4, f"{t}", size=12, anchor="end", fill="var(--ink-2)")
        svg.line(sx(0), sy(0), sx(top_), sy(top_), stroke="var(--ink-3)", dash="5 4")
        svg.text(x0, top - 12, f"{'A' if j == 0 else 'B'} · {net}", size=12, weight="bold")
        for e in cen:
            if e["net"] != net:
                continue
            svg.circle(sx(e["d_in"]), sy(e["d_out"]), 3, stroke="none", opacity=0.55,
                       fill="var(--c2)" if e["collapsed"] else "var(--c1)",
                       title=f"{net} {e['cfg'][:8]} seed {e['seed']} recs {e['recs']}: "
                             f"input d {e['d_in']:.2f}, output d {e['d_out']:.2f}")
    _ypanel_label(svg, 18, top + ph / 2, "event separation at the output (d)")
    ly = h - 14
    svg.circle(left + 6, ly - 4, 5, fill="var(--c2)", stroke="none")
    svg.text(left + 16, ly, "collapsed", size=12)
    svg.circle(left + 106, ly - 4, 5, fill="var(--c1)", stroke="none")
    svg.text(left + 116, ly, "working", size=12)
    svg.line(left + 196, ly - 4, left + 222, ly - 4, stroke="var(--ink-3)", dash="5 4")
    svg.text(left + 228, ly, "output separates events as well as the head's input", size=12)
    return svg.render()


def _step_axis(svg, left, pw, y, steps):
    return R.x_axis(svg, left, left + pw, y, 0, steps, list(range(0, steps + 1, 300)),
                    "training step", fmt="{:.0f}")


def fig_onset(pair: dict[str, tuple[dict, str]]) -> str:
    """How many of the head's 8 layers are silent on each training batch, over the replayed training."""
    left, top, ph, pw = 70, 24, 150, 720
    w, h = left + pw + 20, top + ph + 70 + 22
    svg = R.Svg(w, h, "silent head layers during training")
    steps = max(e["step"] for d, _ in pair.values() for e in d["log"])
    sx = _step_axis(svg, left, pw, top + ph + 4, steps)
    n = max(len(e["head_varying"]) for d, _ in pair.values() for e in d["log"])
    sy = lambda v: top + ph - v / n * ph
    for t in range(0, n + 1, 2):
        svg.line(left, sy(t), left + pw, sy(t), stroke="var(--rule)")
        svg.text(left - 8, sy(t) + 4, str(t), size=12, anchor="end", fill="var(--ink-2)")
    _ypanel_label(svg, 18, top + ph / 2, "silent head layers (of 8)")
    for k, (label, (d, col)) in enumerate(pair.items()):
        pts = [(sx(e["step"]), sy(sum(a == 0 for a in e["head_varying"]))) for e in d["log"]]
        _polyline(svg, pts, col, title=label)
        kx, ky = left + k * (pw / 2), top + ph + 62
        svg.line(kx, ky - 4, kx + 22, ky - 4, stroke=col, width=3)
        svg.text(kx + 30, ky, label, size=12)
    return svg.render()


def fig_curves(reps: dict[str, tuple[dict, str, bool]]) -> str:
    """Training loss for the collapsed fit as run, its working sibling, and the collapsed fit
    replayed with one change each."""
    left, top, ph, pw = 70, 24, 300, 720
    w, h = left + pw + 20, top + ph + 70 + 22 * math.ceil(len(reps) / 2)
    svg = R.Svg(w, h, "training loss, replayed")
    steps = max(e["step"] for d, _, _ in reps.values() for e in d["log"])
    sx = _step_axis(svg, left, pw, top + ph + 4, steps)
    lo, hi = 0.0, 2.0
    sy = lambda v: top + ph - (min(hi, max(lo, v)) - lo) / (hi - lo) * ph
    for t in (0.0, 0.5, 1.0, 1.5, 2.0):
        svg.line(left, sy(t), left + pw, sy(t), stroke="var(--rule)")
        svg.text(left - 8, sy(t) + 4, f"{t:.1f}", size=12, anchor="end", fill="var(--ink-2)")
    _ypanel_label(svg, 18, top + ph / 2, "training loss (mean of 5 logged steps)")
    # the as-run collapsed fit is drawn last: the 50-step warm-up retraces its loss and would hide it
    order = sorted(enumerate(reps.items()), key=lambda kv: "as run" in kv[1][0])
    for k, (label, (d, col, dashed)) in order:
        L = d["log"]
        pts = [(sx(L[i]["step"]), sy(st.mean(e["loss"] for e in L[max(0, i - 4):i + 1])))
               for i in range(len(L))]
        _polyline(svg, pts, col, dash="7 4" if dashed else None, title=label)
        kx, ky = left + (k % 2) * (pw / 2), top + ph + 62 + 22 * (k // 2)
        svg.line(kx, ky - 4, kx + 22, ky - 4, stroke=col, width=3, dash="7 4" if dashed else None)
        svg.text(kx + 30, ky, label, size=12)
    return svg.render()


def fig_warmup(wu: list[dict], trains) -> str:
    """The 200-step warm-up at lr 0.03 on other collapsed fits: every logged loss, one line per fit."""
    left, top, ph, pw = 70, 24, 240, 720
    w, h = left + pw + 20, top + ph + 92
    svg = R.Svg(w, h, "a 200-step warm-up on other collapsed fits")
    steps = max(e["step"] for d in wu for e in d["log"])
    sx = R.x_axis(svg, left, left + pw, top + ph + 4, 0, steps,
                  list(range(0, steps + 1, 600)), "training step", fmt="{:.0f}")
    lo, hi = 0.0, 2.0
    sy = lambda v: top + ph - (min(hi, max(lo, v)) - lo) / (hi - lo) * ph
    for t in (0.0, 0.5, 1.0, 1.5, 2.0):
        svg.line(left, sy(t), left + pw, sy(t), stroke="var(--rule)")
        svg.text(left - 8, sy(t) + 4, f"{t:.1f}", size=12, anchor="end", fill="var(--ink-2)")
    svg.line(left, sy(0.5), left + pw, sy(0.5), stroke="var(--ink)", width=1.2, dash="5 4")
    _ypanel_label(svg, 18, top + ph / 2, "training loss (mean of 5 logged steps)")
    for d in wu:
        L = d["log"]
        pts = [(sx(L[i]["step"]), sy(st.mean(e["loss"] for e in L[max(0, i - 4):i + 1])))
               for i in range(len(L))]
        _polyline(svg, pts, "var(--c1)" if trains(d) else "var(--c2)", width=1.6,
                  title=f"{d['cfg'][:8]} seed {d['seed']}")
    ky = h - 26
    for k, (col, words) in enumerate((("var(--c1)", "trains"), ("var(--c2)", "does not train"))):
        svg.line(left + k * 160, ky - 4, left + k * 160 + 22, ky - 4, stroke=col, width=3)
        svg.text(left + k * 160 + 30, ky, words, size=12)
    svg.line(left + 320, ky - 4, left + 344, ky - 4, stroke="var(--ink)", width=1.2, dash="5 4")
    svg.text(left + 350, ky, "loss 0.5, the line between them", size=12)
    return svg.render()


# Slots 1-6 of the reference categorical palette, in its validated order: adjacent pairs pass the
# color-vision checks in both modes (Figure 6's lines), and the first three pass all pairs (the dot
# plots use two). The reference is the dataviz guidance's own palette; slot 6 (green) has no
# separate dark step there.
CSS_EXTRA = """
:root{--c1:#2a78d6;--c2:#eb6834;--c3:#1baf7a;--c4:#eda100;--c5:#e87ba4;--c6:#008300}
@media (prefers-color-scheme: dark){:root:not([data-theme="light"]){--c1:#3987e5;--c2:#d95926;
--c3:#199e70;--c4:#c98500;--c5:#d55181;--c6:#008300}}
:root[data-theme="dark"]{--c1:#3987e5;--c2:#d95926;--c3:#199e70;--c4:#c98500;--c5:#d55181;--c6:#008300}
td,th{white-space:nowrap}
code{overflow-wrap:anywhere}
.refs li{font-size:14px}
"""


def page(work: Path) -> str:
    table = json.loads((work / "collapse_table.json").read_text())
    rows = [r for r in table if r["role"] == "inner"]
    refits = [r for r in table if r["role"] != "inner"]
    census_all = json.loads((work / "census.json").read_text())
    cen = [e for e in census_all if e["role"] == "inner"]
    tr = json.loads((work / "trace.json").read_text())
    reps = {p.stem: json.loads(p.read_text()) for p in sorted((work / "replays").glob("*.json"))}
    rnd = random.Random(2026)
    cfg_row = {r["cfg"]: r for r in rows}

    def rate(net, pred, rs=rows):
        rs = [r for r in rs if r["net"] == net and pred(r)]
        return sum(r["collapsed"] for r in rs), len(rs)

    pct = lambda cn: f"{cn[0] / cn[1]:.0%}"
    of = lambda cn, unit="fits": f"{cn[0]} of {cn[1]} {unit}"

    # ---- the problem, and how it repeats across the draws
    per_draw = {(n, d): rate(n, lambda r, d=d: r["draw"] == d) for n in CHORUS for d in DRAW_DIRS}
    by_lr = {(n, lr): rate(n, lambda r, lr=lr: r["lr"] == lr) for n in CHORUS for lr in LRS}
    fitkey = lambda r: (r["cfg"], r["seed"], tuple(r["pair"]))
    colset = lambda d, n: {fitkey(r) for r in rows if r["draw"] == d and r["net"] == n
                           and r["collapsed"]}
    both = {n: len(colset("first", n) & colset("second", n)) for n in CHORUS}
    per_cfg_draw = defaultdict(lambda: [0, 0])
    for r in rows:
        per_cfg_draw[(r["net"], r["cfg"], r["draw"])][0] += r["collapsed"]
        per_cfg_draw[(r["net"], r["cfg"], r["draw"])][1] += 1
    expected = {n: sum(per_cfg_draw[(n, c, "first")][0] * per_cfg_draw[(n, c, "second")][0]
                       / per_cfg_draw[(n, c, "first")][1]
                       for c in {r["cfg"] for r in rows if r["net"] == n}) for n in CHORUS}
    n_cfg = {n: len({r["cfg"] for r in rows if r["net"] == n}) for n in CHORUS}
    per_fit_cfg = {n: len([r for r in rows if r["net"] == n and r["draw"] == "second"]) // n_cfg[n]
                   for n in CHORUS}

    # ---- which configurations
    per_cfg = defaultdict(lambda: [0, 0])
    for r in rows:
        per_cfg[(r["net"], r["cfg"])][0] += r["collapsed"]
        per_cfg[(r["net"], r["cfg"])][1] += 1
    share = lambda net, c: per_cfg[(net, c)][0] / per_cfg[(net, c)][1]
    hi_cfgs = sorted(c for (n, c) in per_cfg if n == "chorus_norm" and cfg_row[c]["lr"] == 0.03)
    cn_hi = [share("chorus_norm", c) for c in hi_cfgs]
    cn_lo = rate("chorus_norm", lambda r: r["lr"] < 0.03)
    shape_lr = {(n, lr, s): rate(n, lambda r, lr=lr, s=s: r["lr"] == lr
                                 and (r["width"], r["depth"]) == s)
                for n in CHORUS for lr in LRS for s in SHAPES}
    steps_hi = {s: rate("chorus_norm", lambda r, s=s: r["lr"] == 0.03 and r["steps"] == s)
                for s in sorted({r["steps"] for r in rows if r["net"] == "chorus_norm"
                                 and r["lr"] == 0.03})}
    deep_steps = {r["steps"] for r in rows if r["net"] == "chorus_norm" and r["lr"] == 0.03
                  and r["depth"] == 6}
    longest = max(steps_hi)
    assert {r["depth"] for r in rows if r["net"] == "chorus_norm" and r["lr"] == 0.03
            and r["steps"] == longest} == {6}, "the longest runs are all deep: the confound stated"
    p_seed = {n: _cluster_test(rows, n, lambda r: r["seed"], rnd) for n in CHORUS}
    p_pair = {n: _cluster_test(rows, n, lambda r: tuple(r["pair"]), rnd) for n in CHORUS}
    twins = _twin_groups(rows)
    assert all(len(g) == 2 for g in twins), "the twins come in pairs"
    # nested twins: a longer twin's collapse, and whether its shorter twin had already collapsed
    status = {(r["draw"], r["cfg"], r["seed"], r["recs"]): r["collapsed"] for r in rows}
    early, late, recovered = defaultdict(int), defaultdict(int), defaultdict(int)
    for g in twins:
        net = cfg_row[g[0]]["net"]
        for (dr, c, s, rc), col in status.items():
            if c != g[-1]:
                continue
            short = status[(dr, g[0], s, rc)]
            if col:
                (early if short else late)[net] += 1
            elif short:
                recovered[net] += 1
    twin_steps = {n: sorted({tuple(cfg_row[c]["steps"] for c in g) for g in twins
                            if cfg_row[g[0]]["net"] == n}) for n in CHORUS}

    # ---- the census
    silent = lambda e: e["min_share_varying"] == 0
    cz = {(n, col): [e for e in cen if e["net"] == n and e["collapsed"] == col]
          for n in CHORUS for col in (True, False)}
    n_silent = {k: sum(silent(e) for e in v) for k, v in cz.items()}
    n_sign = {k: sum(e["min_share_positive"] == 0 for e in v) for k, v in cz.items()}
    med = lambda v, f: st.median(e[f] for e in v)
    sd_coll_max = max(e["logit_sd"] for e in census_all if e["collapsed"])
    sd_work_min = min(e["logit_sd"] for e in census_all if not e["collapsed"])
    assert sd_coll_max < sd_work_min, "the output's spread separates collapsed from working fits"
    floored = {n: sum(e["logit_sd"] < 1e-3 for e in cen if e["net"] == n) for n in CHORUS}
    at_floor = [e for e in census_all if e["collapsed"]]
    grid_floor = min(e["threshold"] for e in census_all)
    assert all(e["threshold"] == grid_floor for e in at_floor), "every collapsed fit at the floor"
    work_floor = sum(e["threshold"] == grid_floor for e in census_all if not e["collapsed"])
    cgn_rest = [e for e in cz[("chorus_gain_norm", True)] if not silent(e)]
    rest_lr = {lr: sum(e["lr"] == lr for e in cgn_rest) for lr in LRS}
    rest_shape = defaultdict(int)
    for e in cgn_rest:
        rest_shape[(cfg_row[e["cfg"]]["width"], cfg_row[e["cfg"]]["depth"])] += 1
    ref_census_bad = [e for e in census_all if e["role"] != "inner" and e["collapsed"]]

    # ---- the replays
    final = lambda d: st.mean(e["loss"] for e in d["log"][-5:])
    trains = lambda d: final(d) < 0.5
    nsil = lambda e: sum(v == 0 for v in e["head_varying"])
    as_run = [d for d in reps.values() if d["as_run"]]
    assert len(as_run) == 2 and all(d["max_abs_diff_vs_checkpoint"] == 0.0 for d in as_run), \
        "both as-run replays reproduce their checkpoints exactly"
    ref = next(d for d in as_run if (d["cfg"], d["seed"], d["recs"]) == SHOWN["collapsed"])
    work_fit = next(d for d in as_run if (d["cfg"], d["seed"], d["recs"]) == SHOWN["working"])
    assert not trains(ref) and trains(work_fit)
    ref_id = SHOWN["collapsed"]
    cf = {(d["lr"], d["warmup"]): d for d in reps.values()
          if (d["cfg"], d["seed"], d["recs"]) == ref_id and not d["as_run"]}
    assert trains(cf[(0.01, 0)]) and trains(cf[(0.003, 0)]) and trains(cf[(0.03, 200)]) \
        and not trains(cf[(0.03, 50)]), "the counterfactuals come out as the page says"
    first_silent = {k: next((e["step"] for e in d["log"] if nsil(e)), None)
                    for k, d in (("collapsed", ref), ("working", work_fit))}
    assert first_silent["working"] is None, "the working fit's head is never silent on a batch"
    end_silent = nsil(ref["log"][-1])
    after = [e for e in ref["log"] if e["step"] >= first_silent["collapsed"]]
    silent_after = sum(nsil(e) > 0 for e in after)
    smooth = lambda d: [st.mean(e["loss"] for e in d["log"][max(0, i - 4):i + 1])
                        for i in range(len(d["log"]))]
    escape = next(e["step"] for e, s in zip(work_fit["log"], smooth(work_fit)) if s < 1.0)
    wu50_silent = sum(nsil(e) > 0 for e in cf[(0.03, 50)]["log"])
    wu = sorted((d for d in reps.values() if d["warmup"] == 200 and d["lr"] == 0.03
                 and (d["cfg"], d["seed"], d["recs"]) != ref_id), key=lambda d: d["cfg"])
    traj = lambda d: (_identity(cfg_row[d["cfg"]]), d["seed"], d["recs"])
    distinct = {}
    for d in sorted(wu, key=lambda d: -cfg_row[d["cfg"]]["steps"]):
        distinct.setdefault(traj(d), d)
    dist = list(distinct.values())
    dup = [d for d in wu if d not in dist]
    wu_ok = sum(trains(d) for d in dist)
    wu_fail = [d for d in dist if not trains(d)]
    chance = sum(1 - share("chorus_norm", d["cfg"]) for d in dist)
    tried_cfgs = {d["cfg"] for d in wu} | {ref["cfg"]}
    omitted = sorted((c for c in hi_cfgs if c not in tried_cfgs),
                     key=lambda c: share("chorus_norm", c))
    # a left-out configuration is either the shorter twin of one tried, or collapses least of all
    twin_left = {c: next(o for g in twins if c in g for o in g if o in tried_cfgs)
                 for c in omitted if any(c in g and set(g) & tried_cfgs for g in twins)}
    low_left = [c for c in omitted if c not in twin_left]
    assert max(share("chorus_norm", c) for c in low_left) < min(
        share("chorus_norm", c) for c in tried_cfgs), "the others left out collapse least"
    assert cn_lo[0] / cn_lo[1] < 0.02 and min(cn_hi) >= 0.4

    # ---- what tuning chose
    untuned_cfg = {n: next(r["cfg"] for r in table if r["net"] == n and r["untuned"]) for n in CHORUS}
    chosen = {(n, lr): [r for r in refits if r["net"] == n and r["lr"] == lr
                        and r["cfg"] != untuned_cfg[n]] for n in CHORUS for lr in LRS}
    n_untuned = {n: sum(r["cfg"] == untuned_cfg[n] for r in refits if r["net"] == n) for n in CHORUS}
    assert not chosen[("chorus_norm", 0.03)], "tuning never chose an lr-0.03 chorus_norm configuration"
    ref_bad = [r for r in refits if r["collapsed"]]
    declared = {(n, lr): len({r["cfg"] for r in rows if r["net"] == n and r["lr"] == lr})
                for n in CHORUS for lr in LRS}

    # ---- drawing
    curves = {"the working fit, as run": (work_fit, "var(--c1)", False),
              "the collapsed fit, as run (lr 0.03)": (ref, "var(--c2)", False),
              "the collapsed fit, replayed at lr 0.003": (cf[(0.003, 0)], "var(--c3)", False),
              "the collapsed fit, replayed at lr 0.01": (cf[(0.01, 0)], "var(--c4)", False),
              "lr 0.03, 200-step warm-up": (cf[(0.03, 200)], "var(--c5)", True),
              "lr 0.03, 50-step warm-up": (cf[(0.03, 50)], "var(--c6)", True)}
    sw = lambda v: f'<span class="sw" style="background:var(--{v})"></span>'
    F = {"problem": 1, "rates": 2, "census": 3, "select": 4, "onset": 5, "curves": 6, "warmup": 7}
    T_ = {"shape": 1, "warmup": 2, "refits": 3}
    ref_ = lambda k, words: f'<a href="#fig-{k}">Figure {F[k]}, {words}</a>'
    tref = lambda k, words: f'<a href="#tab-{k}">Table {T_[k]}, {words}</a>'
    fig = lambda k, body, cap: (f'<figure id="fig-{k}"><div class="scrollhint">Scroll sideways to '
                                f'see the whole figure.</div>{body}<figcaption><b>Figure {F[k]}.</b> '
                                f'{cap}</figcaption></figure>')

    def tab(k, title, head, body_rows, note=""):
        return (f'<p id="tab-{k}"><b>Table {T_[k]}. {title}</b></p><div class="scrollhint">Scroll '
                f'sideways to see the whole table.</div><div class="tablewrap"><table><thead><tr>'
                + "".join(f"<th>{h_}</th>" for h_ in head) + "</tr></thead><tbody>"
                + "".join("<tr>" + "".join(f"<td>{c}</td>" for c in row) + "</tr>"
                          for row in body_rows) + "</tbody></table></div>"
                + (f'<p class="tnote">{note}</p>' if note else ""))

    def shape_cell(n, lr, s):
        c, k = shape_lr[(n, lr, s)]
        return "—" if k == 0 else f"{c} of {k} fits ({c / k:.0%})"

    t_shape = tab("shape", "Collapsed inner fits by learning rate and the encoder's shape, both "
                  "draws pooled.", ["net", "encoder (units wide × layers deep)"]
                  + [f"lr {lr:g}" for lr in LRS],
                  [[n, f"{s[0]} × {s[1]}"] + [shape_cell(n, lr, s) for lr in LRS]
                   for n in CHORUS for s in SHAPES],
                  "A dash: the grid has no configuration of that shape at that learning rate.")
    twin_of = {d["cfg"]: t["cfg"] for d in dup for t in dist if traj(t) == traj(d)}
    t_wu = tab("warmup", "The 200-step warm-up at lr 0.03, fit by fit.",
               ["encoder", "top m", "steps", "configuration's collapse share", "final loss",
                "outcome", "configuration"],
               [[f"{cfg_row[d['cfg']]['width']} × {cfg_row[d['cfg']]['depth']}",
                 cfg_row[d["cfg"]]["top_m"], f"{d['steps']:,}",
                 f"{per_cfg[('chorus_norm', d['cfg'])][0]} of 36 fits", f"{final(d):.2f}",
                 ("trains" if trains(d) else "does not train")
                 + (f" (the same run as {twin_of[d['cfg']][:8]}'s, stopped earlier)"
                    if d["cfg"] in twin_of else ""),
                 f"{d['cfg'][:8]}, training seed {d['seed']}"] for d in wu],
               "Final loss: the mean of the last 5 logged steps. A fit trains when that is below "
               "0.5; a constant output's loss is about 1.4 (2 ln 2 times the share of frames "
               "outside events), and the collapsed fits sit near 1.5.")
    t_ref = tab("refits", "What tuning chose: refits by learning rate.",
                ["net", "learning rate", "configurations in the grid",
                 "refits of configurations tuning chose", "of them collapsed"],
                [[n, f"{lr:g}", declared[(n, lr)], len(chosen[(n, lr)]),
                  sum(r["collapsed"] for r in chosen[(n, lr)])] for n in CHORUS for lr in LRS],
                f"Both draws. Each net also refits its untuned default configuration in every fold "
                f"whatever tuning chooses ({n_untuned['chorus_norm']} refits for chorus_norm, "
                f"{n_untuned['chorus_gain_norm']} for chorus_gain_norm, all at lr 0.01, none "
                f"collapsed); those are left out here.")
    shared = all(expected[n] > 0 for n in CHORUS)
    assert shared
    fmt_p = lambda p: f"p = {p:.3f}" if p >= 0.001 else "p < 0.001"
    body = f"""
<h1>Why a third of chorus_norm's fits do not train</h1>
<p class="sub">A diagnosis from the saved fits of the two runs of the project's fair comparison of
coded detectors against learned nets (goal 2). The runs' results were not changed; {len(reps)}
training runs were replayed from the runs' own starting points to watch the failure happen.
Simulated recordings only.</p>

<p>chorus_norm and chorus_gain_norm are two of the small neural networks the project trains to find
coordinated events, moments when many cells in a recording become active together. Each reads a
recording as one row per cell (a region of interest, ROI) in 0.1-second frames and outputs a score
for every frame, as a logit (log-odds). A threshold chosen during training turns the scores into
calls, and calls are scored by F1 (the harmonic mean of precision and recall) against the events
planted in the simulation.</p>

<div class="box"><b>The answer.</b>
<ul>
<li><b>The problem.</b> In both runs of goal 2, {per_draw[('chorus_norm', 'first')][0]} and
{per_draw[('chorus_norm', 'second')][0]} of chorus_norm's 432 inner fits <i>collapsed</i>: each
called every recording it was scored on as a single event, which matches one of the 15 planted
events, F1 0.125 ({ref_('problem', 'a collapsed fit on a held-out recording')}).</li>
<li><b>For chorus_norm the cause is the learning rate (lr).</b> {of(by_lr[('chorus_norm', 0.03)])}
collapse at lr 0.03; {of(cn_lo)} below it. The encoder's shape shifts the share. chorus_gain_norm
is different: its encoder's shape matters as much as the learning rate.</li>
<li><b>The signal stops in the head</b>, the eight layers that turn the pooled per-ROI statistics
into the output. In the second run, {n_silent[('chorus_norm', True)]} of the
{len(cz[('chorus_norm', True)])} collapsed chorus_norm inner fits have a head layer whose units'
outputs do not vary, against {n_silent[('chorus_norm', False)]} of the
{len(cz[('chorus_norm', False)])} working ones, while the head's input still separates events from
the rest ({ref_('select', 'where the signal stops')}).</li>
<li><b>A collapsed fit never leaves its flat start, and a slower start prevents it.</b> Replayed
exactly, a collapsed fit and a working fit of the same configuration both start with a flat output.
The working one leaves it within {escape} steps; the collapsed one never does, and its head goes
silent later. The same collapsed fit trains at lr 0.003 or 0.01, or at 0.03 with the learning rate
ramped up linearly over the first 200 steps, which also trains {wu_ok} of {len(dist)} other
collapsed runs. This is a known failure of training at too large a step size, and a warm-up is its
standard remedy (§4).</li>
<li><b>It is not the failure found earlier in plain chorus</b> (PR #596), where the encoder barely
responded to events. Here the encoder's output still does.</li>
<li><b>What it did to goal 2.</b> Tuning chose no lr-0.03 configuration for chorus_norm, so the
collapse took {len(hi_cfgs)} of its {n_cfg['chorus_norm']} configurations out of contention rather
than putting dead models into its held-out scores; {len([r for r in ref_bad if r['net'] == 'chorus_norm'])}
of its refits collapsed anyway. How to repair it is a decision for goal 2 (§5).</li>
</ul></div>

<h2>1. The problem</h2>
<p>{ref_('problem', 'a collapsed fit on a held-out recording')} shows what a collapse is. Both fits
come from the same configuration and differ only in their training seed, which sets the starting
weights and the order of the training crops. The working fit's output rises at events and its
threshold turns the rises into calls. The collapsed fit's output barely moves, and it sits far above
the fit's threshold, so the whole recording is one call.</p>
""" + fig("problem", fig_problem(tr),
          f"<b>A collapsed fit calls the whole recording one event; a working fit of the same "
          f"configuration calls events.</b> One simulated recording with a quiet background "
          f"({tr['recording'].split(':')[1]} is its simulation seed), held out from the training of "
          f"both fits; {len(tr['events'])} planted events. Lane: the planted events (▼) and each fit's "
          f"calls ({len(tr['fits']['working']['calls'])} for the working fit, "
          f"{len(tr['fits']['collapsed']['calls'])} for the collapsed one). Below: each fit's output "
          f"logit, lowest to highest in every {tr['bin_frames'] * tr['dt']:.0f}-second bin, on its "
          f"own vertical range; dashed, the fit's threshold as a logit. The fits are chorus_norm, lr "
          f"0.03, encoder 4 units wide and 6 layers deep, training seeds 2 (working) and 0 "
          f"(collapsed); both are replayed in §4.") + f"""
<p><b>How the fits are organized.</b> A <i>configuration</i> is one setting of the net's size and
training: the encoder's width and depth, how many of the most active ROIs one pooled statistic
averages (top m), the learning rate and the number of training steps. Goal 2 tunes each net over
{n_cfg['chorus_norm']} configurations by nested cross-validation. Inside each outer fold, every
configuration is trained at 3 training seeds on each of the 6 pairs of 4 inner folds and scored on
the other two: these are the <i>inner fits</i>, {per_fit_cfg['chorus_norm'] * n_cfg['chorus_norm']}
per net per run. The configuration tuning picks is then trained afresh and scored on recordings held
out from all of that: a <i>refit</i>. Goal 2 was run twice, on different simulated recordings;
<a href="../tuned_vs_coact/replicate1/report.html">the replicate report</a> calls the two runs
<i>draws</i>, and so does this page.</p>
<p><b>Which fits collapse is not repeatable; how many is.</b> {both['chorus_norm']} of chorus_norm's
collapsed fits are the same fit (configuration, training seed and pair of folds) in both draws. If
each draw collapsed its fits independently at its configurations' own rates, the expected overlap
would be {expected['chorus_norm']:.1f}. So the overlap says the configuration decides how often a
fit collapses, and nothing about which ones do (chorus_gain_norm: {both['chorus_gain_norm']}
observed, {expected['chorus_gain_norm']:.1f} expected).</p>

<h2>2. Which configurations collapse</h2>
<p>For chorus_norm the learning rate separates the configurations almost completely
({ref_('rates', 'collapse by configuration')}): every configuration at lr 0.03 collapses in
{min(cn_hi):.0%} to {max(cn_hi):.0%} of its fits, and below 0.03 the collapse is rare. Within lr
0.03 the encoder's shape shifts the share ({tref('shape', 'collapse by shape')}): the narrow, deep
encoder (4 × 6) collapses most. Training length is tangled with depth: at lr 0.03,
{'; '.join(f"{s:,} steps {pct(v)} ({of(v)})" for s, v in steps_hi.items())}, and the
{longest:,}-step configurations are all 6 layers deep. These shape and length shares are described,
not tested.</p>
<p>chorus_gain_norm does not follow the learning rate the same way. At lr 0.03 its 4 × 6
configurations collapse in {pct(shape_lr[('chorus_gain_norm', 0.03, (4, 6))])} of fits and the other
shapes in {pct((sum(shape_lr[('chorus_gain_norm', 0.03, s)][0] for s in SHAPES if s != (4, 6)), sum(shape_lr[('chorus_gain_norm', 0.03, s)][1] for s in SHAPES if s != (4, 6))))};
at lr 0.01 its 4 × 6 configurations still collapse in
{pct(shape_lr[('chorus_gain_norm', 0.01, (4, 6))])}.</p>
<p>Inside a configuration, the fold pair makes no difference to whether a fit collapses
({fmt_p(p_pair['chorus_norm'])} for chorus_norm, {fmt_p(p_pair['chorus_gain_norm'])} for
chorus_gain_norm; collapse labels shuffled within each configuration and draw). The training seed
does, for chorus_norm ({fmt_p(p_seed['chorus_norm'])}; chorus_gain_norm
{fmt_p(p_seed['chorus_gain_norm'])}): at a risky configuration some starting points escape and some
do not. Pooled over configurations the seeds look alike ({', '.join(pct(rate('chorus_norm', lambda r, s=s: r['seed'] == s)) for s in (0, 1, 2))}
of chorus_norm's fits at seeds 0, 1 and 2), which is why the test is made inside them.
{len(twins)} pairs of configurations in the grid (both nets) differ only in step count; the shorter one's fits
are the longer one's stopped early, so they are left out of these tests.</p>
""" + fig("rates", fig_rates(rows),
          "<b>For chorus_norm, the top learning rate is where fits collapse.</b> Each dot is one "
          "configuration: the share of its 36 inner fits (3 training seeds × 6 pairs of folds × 2 "
          "draws) that collapsed. Rows: learning rate, with the collapsed count over all its "
          "configurations; configurations with the same share are stacked. Panel A chorus_norm, "
          "panel B chorus_gain_norm. Hover a dot for its configuration.") + t_shape + f"""

<h2>3. Where the signal stops</h2>
<p>chorus_norm passes each ROI's activity through a shared encoder, standardizes the encoder's
output over time, turns it into a vote per ROI, pools the votes into three statistics (their mean,
their spread across ROIs, and the mean of the top m) and feeds those to a head: 8 layers of 8 units,
each followed by a GELU, an activation that passes positive input and maps negative input to a small
dip (no lower than −0.17) that still carries a gradient (Hendrycks &amp; Gimpel 2016). The head's
size was never tuned. The nets are trained with Adam (Kingma &amp; Ba 2015) at its default β1 0.9
and β2 0.999; lr 0.03 is 30 times the step size that paper suggests as a default.</p>
<p>Every second-draw fit of both nets was reloaded and run on one simulated recording (quiet
background, simulation seed {PROBE_RECORDING.split(':')[1]}); call this the <i>census</i>. Call a
head layer <i>silent</i> when none of its 8 units' outputs varies over the recording (standard
deviation under {SILENT:g}): it passes nothing that changes. In chorus_norm,
{n_silent[('chorus_norm', True)]} of the {len(cz[('chorus_norm', True)])} collapsed inner fits have a
silent head layer, against {n_silent[('chorus_norm', False)]} of the
{len(cz[('chorus_norm', False)])} working ones ({ref_('census', 'silent layers and flat outputs')});
in chorus_gain_norm, {n_silent[('chorus_gain_norm', True)]} of {len(cz[('chorus_gain_norm', True)])}
against {n_silent[('chorus_gain_norm', False)]} of {len(cz[('chorus_gain_norm', False)])}. The output
of a collapsed fit barely moves: its standard deviation over the recording has a median of
{med(cz[('chorus_norm', True)], 'logit_sd'):.4f} logits against
{med(cz[('chorus_norm', False)], 'logit_sd'):.2f} in working fits. Every collapsed fit's threshold is the
lowest value on the threshold grid ({grid_floor:g}), below its whole output, so the whole recording
is one call.</p>
""" + fig("census", fig_census(cen),
          f"<b>Every collapsed fit has a flat output and most have a silent head layer; no "
          f"working fit has either.</b> One dot per second-draw inner fit on the census recording: the smallest "
          f"share of units whose output varies, over the head's 8 layers (it takes only the values "
          f"0, 1/8, …, 1; dots are spread ±0.02 sideways so they can be seen), against the standard "
          f"deviation of its output logit over the recording. {floored['chorus_norm']} chorus_norm "
          f"and {floored['chorus_gain_norm']} chorus_gain_norm fits have an output SD below 10⁻³ "
          f"and are drawn hollow on that floor. {sw('c2')}collapsed, {sw('c1')}working.") + f"""
<p>This is the test that separates this failure from the earlier one. PR #596 found plain chorus's
encoder barely responding to events. If that were happening here, the head's input would not
separate event frames from the rest either. It does: measured as the largest standardized difference
between event frames and the rest (d) over the head's input channels, collapsed chorus_norm fits have
a median of {med(cz[('chorus_norm', True)], 'd_in'):.2f} and working ones
{med(cz[('chorus_norm', False)], 'd_in'):.2f}. At the output the collapsed fits' separation falls to a
median of {med(cz[('chorus_norm', True)], 'd_out'):.2f}, against
{med(cz[('chorus_norm', False)], 'd_out'):.2f} in working fits
({ref_('select', 'where the signal stops')}). The encoder still hears the events; the head does not
pass them on.</p>
""" + fig("select", fig_selectivity(cen),
          "<b>The head's input still separates events in collapsed fits; their output does not.</b> "
          "One dot per second-draw inner fit on the census recording. Across: how well the head's "
          "input separates event frames from the rest, the largest standardized difference of means "
          "(d) over its input channels. Up: the same for the output logit. On the dashed line the "
          f"output separates events as well as the head's input does. {sw('c2')}collapsed, "
          f"{sw('c1')}working.") + f"""
<p>Round 1 of this page's review counted a layer as dead when none of its units' outputs ever rose
above 0.001. That is a sign test, and GELU's negative dip carries signal without going positive: it
counted {n_sign[('chorus_norm', True)]} of the collapsed and {n_sign[('chorus_norm', False)]} of the
working chorus_norm fits, including one working fit whose output varies normally. The silent-layer
rule counts what reaches the output. {len(cgn_rest)} collapsed chorus_gain_norm fits have no silent
layer; §6 says what is known about them.</p>

<h2>4. When it happens, and what prevents it</h2>
<p>The collapsed fit of {ref_('problem', 'a collapsed fit on a held-out recording')} and its working
sibling were replayed exactly as the run trained them, and each replay reproduced its saved
checkpoint to the last bit. Both start with an output that barely varies (standard deviation
{ref['log'][0]['logit_sd']:.4f} and {work_fit['log'][0]['logit_sd']:.4f} logits on the first batch).
The working fit's loss falls below 1.0 by step {escape}; the collapsed fit's never leaves its
starting level ({ref_('curves', 'the replays')}). Measured on the training batches, the working
fit's head never has a silent layer. The collapsed fit's first has one at step
{first_silent['collapsed']}, well after its loss has stalled; from then on it has one at
{silent_after} of the {len(after)} logged steps, and ends with {end_silent} of its 8 silent
({ref_('onset', 'silent layers during training')}). So the silent head marks a fit that never left
its flat start, and does not begin the failure: the replay with a 50-step warm-up stays flat without
a silent layer on {"any" if wu50_silent == 0 else "most"} of its training batches.</p>
""" + fig("onset", fig_onset({"the working fit, as run": (work_fit, "var(--c1)"),
                             "the collapsed fit, as run": (ref, "var(--c2)")}),
          "<b>The collapsed fit's head goes silent after its loss has stalled; the working fit's "
          "never does.</b> The two as-run replays of "
          "the fits in Figure 1: how many of the head's 8 layers have no unit whose output varies "
          f"over the training batch (standard deviation under {SILENT:g}), logged every 10 steps. "
          "The batch is 3 training crops of 4,096 frames, not the census recording, so these counts "
          "are not on the same input as Figure 3's.") + f"""
<p>The collapsed fit was then replayed with one thing changed and the same starting weights and
training crops. It trains at lr 0.003 and at lr 0.01, which change the learning rate for the whole
run; and at lr 0.03 when the learning rate is ramped up linearly over the first 200 steps, which
changes only the start. A 50-step ramp is not enough: its loss retraces the fit as run.</p>
""" + fig("curves", fig_curves(curves),
          "<b>The same fit trains at a lower learning rate, or at the top one with a slower "
          "start.</b> Training loss (binary cross-entropy weighted toward event frames), the mean of 5 "
          "logged steps, logged every 10. Solid: the two fits as run and the collapsed fit replayed "
          "at a lower learning rate; dashed: the collapsed fit replayed at lr 0.03 with a linear "
          "warm-up. The axis stops at 2.0; no smoothed line reaches it.") + f"""
<p>The 200-step warm-up was then tried on one collapsed fit, chosen by hand, from each of
{len(tried_cfgs) - 1} other lr-0.03 configurations ({ref_('warmup', 'warm-up on other fits')},
{tref('warmup', 'fit by fit')}). Two of those configurations differ only in step count, so their
fits are one training run counted twice; counted once, {wu_ok} of {len(dist)} distinct runs train.
If warm-up did nothing, each would train only as often as its configuration's fits do, which
predicts {chance:.1f} of {len(dist)}. The one that does not train
({wu_fail[0]['cfg'][:8] if wu_fail else '—'}) was not tried with a longer ramp. Of the
{len(omitted)} lr-0.03 configurations left out, {len(low_left)} collapse least of all
({', '.join(f"{per_cfg[('chorus_norm', c)][0]} of 36 fits" for c in low_left)}) and
{len(twin_left)} {'is the shorter twin' if len(twin_left) == 1 else 'are shorter twins'} of one
that was tried.</p>
""" + fig("warmup", fig_warmup(wu, trains),
          "<b>A 200-step linear warm-up at lr 0.03 lets most collapsed fits train.</b> Training loss, "
          "the mean of 5 logged steps, for one collapsed fit from each of the other lr-0.03 "
          "configurations tried, replayed with the warm-up. Dashed: loss 0.5, the line this page uses "
          "between training and not. The fits are listed in Table 2; two of the lines are one run. "
          + ("The axis stops at 2.0 and one early spike is cut there." if max(
              max(smooth(d)) for d in wu) > 2.0 else "The axis stops at 2.0; no line passes it."))
    body += t_wu + f"""
<p><b>Settled early, mostly.</b> The configurations that differ only in step count show when a
collapse is decided: of the collapses in the longer twin, {early['chorus_norm']} of
{early['chorus_norm'] + late['chorus_norm']} in chorus_norm were already there when the shorter twin
stopped ({', '.join(f"{a:,} against {b:,} steps" for a, b in twin_steps['chorus_norm'])}), and
{late['chorus_norm']} came later. {recovered['chorus_norm']} fits collapsed at the shorter length and
worked at the longer (chorus_gain_norm: {early['chorus_gain_norm']} early, {late['chorus_gain_norm']}
late, {recovered['chorus_gain_norm']} recovered).</p>
<p><b>A known failure, with a standard remedy.</b> Units that stop responding under too large a step
size are a long-standing observation in training deep nets; Gulcehre et al. (2022) measure more of
them at larger learning rates, and Sokar et al. (2023) define such "dormant" units by a threshold on
their activity, as this page does. A learning-rate warm-up is the usual remedy (He et al. 2016;
Goyal et al. 2017). Why it helps Adam is argued (Liu et al. 2020; Ma &amp; Yarats 2021); Ma &amp;
Yarats's rule of thumb, 2/(1 − β2), is 2,000 steps at Adam's default, ten times the ramp tried
here.</p>

<h2>5. What it means, and the choice it leaves</h2>
<ul>
<li><b>For chorus_norm, tuning stepped around it.</b> A configuration whose fits collapse scores
badly in the inner selection, and tuning chose none at lr 0.03 ({tref('refits', 'what tuning chose')}).
The collapse therefore did not put dead models into chorus_norm's held-out scores wholesale; it took
{len(hi_cfgs)} of its {n_cfg['chorus_norm']} configurations out of contention, so chorus_norm was in
effect tuned over a smaller grid than the one
<a href="../tuned_vs_coact/fair_comparison_2026_09_18/report.html">the fair-comparison report</a>
declares.</li>
<li><b>For chorus_gain_norm it did not.</b> Tuning chose lr-0.03 configurations for it
({len(chosen[('chorus_gain_norm', 0.03)])} refits), and both of its collapsed refits are among them.</li>
<li><b>The refits that collapsed.</b> {len(ref_bad)} refits collapsed across both draws:
{'; '.join(f"{r['net']}, {r['draw']} draw, lr {r['lr']:g}" for r in ref_bad)}. They are behind the †
on chorus_norm (second draw) and chorus_gain_norm (both draws) in the replicate report, whose †
is its own flag (F1 near 0.125 with the threshold at the grid floor, or F1 undefined) and agrees for
these four. The census holds the second draw's {len(ref_census_bad)}; all
{sum(silent(e) for e in ref_census_bad)} have a silent head layer.</li>
<li><b>A repair is a decision for goal 2, not this page's.</b> Three are open. Drop lr 0.03 from
chorus_norm's grid, which accepts the grid tuning already used in effect (for chorus_gain_norm it
would change what tuning chose). Add a linear learning-rate warm-up to training, which changes every
net, since they share one trainer; 200 steps was tried here. Or change the head, 8 layers of 8 units
and never tuned, which was not tried. Each changes chorus_norm's numbers in goal 2 and needs both
draws run again to compare.</li>
<li><b>A collapse can be caught when it happens.</b> On the census recording the output's standard
deviation separates the two groups without overlap, in both nets and in the refits: at most
{sd_coll_max:.3f} logits in every collapsed fit, at least {sd_work_min:.3f} in every working one. A
check at the end of training could refuse a fit whose held-out output does not vary, instead of
scoring it. The gap was found on one recording and one draw; a cutoff inside it has not been tested
on others.</li>
</ul>
""" + t_ref + f"""

<h2>6. Limits</h2>
<ul>
<li>Simulated recordings only. The census and the replays use the second draw's fits; the collapse
counts use both draws.</li>
<li>The census runs each fit on one recording, which some fits trained on and others did not. The
separations above held on that recording and were not tested on others.</li>
<li>The two as-run replays reproduced their checkpoints exactly. The counterfactual replays are the
same code with one change and have no checkpoint to match; they are judged by training loss, not by
calls on held-out recordings.</li>
<li>The warm-up was tried on {len(dist) + 1} distinct collapsed runs of chorus_norm, chosen by hand,
and on no chorus_gain_norm fit.</li>
<li>{len(cgn_rest)} collapsed chorus_gain_norm fits have a flat output without a silent head layer
({', '.join(f"{v} at lr {lr:g}" for lr, v in rest_lr.items())}; encoder
{', '.join(f"{w_} × {d_}: {v}" for (w_, d_), v in sorted(rest_shape.items()))}). What stops them is
not established here.</li>
<li>The seed effect inside a configuration is measured, not explained.</li>
</ul>

<h2>7. Where everything is</h2>
<ul>
<li>This page and its data (<code>collapse_table.json</code>, <code>census.json</code>,
<code>trace.json</code>, <code>replays/</code>): <code>docs/learned/chorus_collapse/</code> in the
repository, where a test rebuilds the page from them, and
<code>&lt;darkroom&gt;/bugarach/{FOLDER}/</code>.</li>
<li>The tool: <code>tools/diagnose_chorus_collapse.py</code>. It needs a checkout that registers the
chorus nets (branch <code>replicate-run</code>), passed as <code>--code</code>; its
<code>replay</code> re-runs a second-draw chorus_norm inner fit on the GPU.</li>
<li>The reports it builds on: the replicate report,
<code>docs/learned/tuned_vs_coact/replicate1/</code>, and the fair-comparison report, which declares
the tuning grid, <code>docs/learned/tuned_vs_coact/fair_comparison_2026_09_18/</code>.</li>
<li>The runs it reads: <code>&lt;darkroom&gt;/bugarach/{R.THEIRS_FOLDER}/results/</code> (first draw)
and <code>&lt;darkroom&gt;/bugarach/{R.MINE_FOLDER}/results/</code> (second draw).</li>
<li>The earlier diagnosis of plain chorus: PR #596 (open, not merged), with
<code>docs/learned/field_size_candidates/why_chorus.txt</code> and that folder's README, section
"Repairing chorus", at commit {DIAGNOSIS_596} on branch <code>replicate-run</code>. It tested plain
chorus at lr 0.01 and 0.001.</li>
</ul>
<p><b>References</b></p>
<ul class="refs">
<li>Goyal P. et al. (2017). Accurate, large minibatch SGD: training ImageNet in 1 hour.
arXiv:1706.02677.</li>
<li>Gulcehre C. et al. (2022). An empirical study of implicit regularization in deep offline RL.
arXiv:2207.02099.</li>
<li>He K., Zhang X., Ren S., Sun J. (2016). Deep residual learning for image recognition. CVPR;
arXiv:1512.03385.</li>
<li>Hendrycks D., Gimpel K. (2016). Gaussian error linear units (GELUs). arXiv:1606.08415.</li>
<li>Kingma D. P., Ba J. (2015). Adam: a method for stochastic optimization. ICLR;
arXiv:1412.6980.</li>
<li>Liu L. et al. (2020). On the variance of the adaptive learning rate and beyond. ICLR;
arXiv:1908.03265.</li>
<li>Ma J., Yarats D. (2021). On the adequacy of untuned warmup for adaptive optimization. AAAI;
arXiv:1910.04209.</li>
<li>Sokar G., Agarwal R., Castro P. S., Evci U. (2023). The dormant neuron phenomenon in deep
reinforcement learning. ICML; arXiv:2302.12902.</li>
</ul>
"""
    title = "Why a third of chorus_norm's fits do not train"
    return ("<!doctype html><html lang='en'><head>"
            "<meta name='viewport' content='width=device-width,initial-scale=1'>"
            f"<meta charset='utf-8'><title>{R.esc(title)}</title><style>" + R.CSS
            + CSS_EXTRA + "</style></head><body>" + body + "</body></html>")


def main(argv=None) -> int:
    p = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    sub = p.add_subparsers(dest="cmd", required=True)
    for name in ("table", "census", "trace", "replay", "page"):
        s = sub.add_parser(name)
        s.add_argument("--work", type=Path, default=None,
                       help=f"working folder (default <darkroom>/bugarach/{FOLDER})")
        s.add_argument("--code", type=Path, default=None,
                       help="a checkout whose src registers the chorus nets (branch replicate-run)")
        if name == "replay":
            s.add_argument("cfg")
            s.add_argument("seed", type=int)
            s.add_argument("recs")
            s.add_argument("--lr", type=float, default=None)
            s.add_argument("--warmup", type=int, default=0)
        if name == "page":
            s.add_argument("--out", type=Path, default=None,
                           help=f"default <darkroom>/bugarach/{FOLDER}/index.html")
            s.add_argument("--also", type=Path, default=None, help="a second copy, e.g. the repo's")
    a = p.parse_args(argv)
    if a.cmd != "page":
        _use_code(a.code)          # before anything imports bugarach, so --code's package wins
    from bugarach.paths import darkroom, unresolved_message
    work = a.work or darkroom(FOLDER)
    if work is None:
        print(unresolved_message("--work"), file=sys.stderr)
        return 2
    work = Path(work)
    work.mkdir(parents=True, exist_ok=True)
    if a.cmd == "page":
        html = page(work)
        for dest in [a.out or work / "index.html"] + ([a.also] if a.also else []):
            Path(dest).parent.mkdir(parents=True, exist_ok=True)
            Path(dest).write_text(html, encoding="utf-8")
            print(f"wrote {dest}")
        return 0
    if a.cmd == "table":
        rows = collapse_table()
        (work / "collapse_table.json").write_text(json.dumps(rows))
        print(f"{len(rows)} fits, {sum(r['collapsed'] for r in rows)} collapsed")
    elif a.cmd == "census":
        rows = json.loads((work / "collapse_table.json").read_text())
        cen = census(rows)
        (work / "census.json").write_text(json.dumps(cen))
        print(f"{len(cen)} fits probed")
    elif a.cmd == "trace":
        d = trace()
        (work / "trace.json").write_text(json.dumps(d))
        print(f"traced the shown fits on {d['recording']}")
    elif a.cmd == "replay":
        d = replay(a.cfg, a.seed, a.recs, lr=a.lr, warmup=a.warmup)
        (work / "replays").mkdir(exist_ok=True)
        tag = "as-run" if d["as_run"] else f"lr{d['lr']:g}-warmup{d['warmup']}"
        (work / "replays" / f"{a.cfg}_s{a.seed}_{a.recs}_{tag}.json").write_text(json.dumps(d))
        last = st.mean(e["loss"] for e in d["log"][-5:])
        print(f"{a.cfg} seed {a.seed}: {tag}, final loss {last:.3f}"
              + (f", max |replay - checkpoint| {d['max_abs_diff_vs_checkpoint']}"
                 if d["as_run"] else ""))
    return 0


if __name__ == "__main__":
    sys.exit(main())
