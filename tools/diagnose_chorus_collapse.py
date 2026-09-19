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
PROBE_RECORDING = "quiet:9000"      # the census recording: simulated fresh, outside every draw's seeds
# A head unit is silent on a recording when its output's standard deviation over the frames is below
# this: it passes (almost) nothing that changes. Round 1 of the review counted a unit dead when its
# output never rose above 0.001; that is a sign test, and GELU's negative lobe carries signal (and
# gradient) without ever going positive, so it counted layers that still transmit.
SILENT = 1e-3
# Every variation measure skips this many frames at each end of a recording or training crop. The
# convolutions pad with zeros, so even a layer whose input is constant wiggles near the ends; the
# net's receptive field is at most 318 frames each way (encoder 63, head 255), so 400 clears it.
EDGE = 400
# The fits the replays follow: the one working second-draw fit of its configuration (lr 0.03,
# encoder 4 units wide and 6 layers deep, 1,800 steps) and a collapsed one trained on the same pair
# of folds, so the two differ only in training seed (which sets the starting weights, the order of
# the training crops and which recordings of those folds the fit trains on).
SHOWN = {"collapsed": ("2736f584e7c224e3", 0, "ecf4b9b71a"),
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


def selections() -> dict:
    """What tuning chose: for each draw, selection rule (``gated``, under the false-alarm budget;
    ``ungated``, on F1 alone) and outer fold, the chorus configuration picked; and the floor of the
    threshold grid each draw declared."""
    out = {}
    for draw in DRAW_DIRS:
        folder = _results(draw)
        picks = []
        for rule in ("gated", "ungated"):
            for net in CHORUS:
                for p in sorted((folder / "selections" / rule).glob(f"outer*/{net}.json")):
                    d = json.loads(p.read_text())
                    picks.append(dict(rule=rule, outer=d["outer_fold"], net=net, cfg=d["config_key"]))
        decl = R.load_run(folder)["decl"]
        out[draw] = dict(picks=picks, threshold_grid_floor=min(decl["threshold_grid"]))
    return out


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


def _votes(model, x):
    """Each ROI's vote, (n_roi, roi_width, T), computed as the chorus forward pass computes it
    (encoder, standardization over time, sigmoid with the fit's own gain and bias). The model does
    not expose its votes, so they are recomputed here; ``_onset_response`` checks the copy against
    the head's actual input, so a drift from the net's own forward pass fails loudly."""
    import torch
    b, n, t = x.shape
    h = model.roi(x.reshape(b * n, 1, t))
    if model.norm:
        h = (h - h.mean(dim=2, keepdim=True)) / (h.std(dim=2, keepdim=True, unbiased=False) + 1e-6)
    if hasattr(model, "vote_gain"):
        h = torch.sigmoid(model.vote_gain.view(1, -1, 1) * (h - model.vote_bias.view(1, -1, 1)))
    else:
        h = torch.sigmoid(h)
    return h.reshape(b, n, -1, t)[0]


def _onset_response(model) -> float:
    """PR #596's test of whether the encoder hears an event: in an otherwise empty window of 32 ROIs
    and 4,096 frames, how far does one onset (ROI 0, frame 2,000) move any vote, on the vote's 0-to-1
    scale. #596 measured at most 0.0003 for plain chorus at initialization, and 0.22 to 0.51 for
    chorus_norm; a fit whose encoder had gone deaf would read like the former."""
    import torch
    x0 = torch.zeros(1, 32, 4096)
    x1 = x0.clone()
    x1[0, 0, 2000] = 1.0
    seen = []
    hook = model.head.register_forward_pre_hook(lambda mod, a: seen.append(a[0][0]))
    with torch.no_grad():
        v0, v1 = _votes(model, x0), _votes(model, x1)
        model(x1)
    hook.remove()
    w = v1.shape[1]
    assert torch.allclose(v1.mean(dim=0), seen[0][:w], atol=1e-5), "vote copy drifted from the net"
    return float((v1 - v0).abs().max())


def _head_probe(model, raster) -> dict:
    """Run one fit on one recording and look inside its head: for each of the head's 8 GELU layers,
    the share of units whose output varies over the recording (standard deviation over its frames
    at least ``SILENT``) and the share that is ever above 0.001 (the sign rule round 1 of the review
    used, kept for comparison); and the output logit."""
    import numpy as np
    import torch
    varying, positive = [], []

    def take_layer(mod, args, o):     # returns None, so it observes and changes nothing
        inner = o[0][:, EDGE:-EDGE]
        varying.append(float((inner.std(dim=1) >= SILENT).float().mean()))
        positive.append(float((inner > 1e-3).any(dim=1).float().mean()))

    hooks = [g.register_forward_hook(take_layer) for g in model.head
             if isinstance(g, torch.nn.GELU)]
    with torch.no_grad():
        logit = model(torch.from_numpy(np.asarray(raster, dtype=np.float32)).unsqueeze(0))[0]
    for h in hooks:
        h.remove()
    return dict(varying=varying, positive=positive, logit=logit.numpy())


def census(rows: list[dict]) -> dict:
    """Every second-draw chorus fit, inner fits and refits, on one simulated recording that no fit
    trained on; each fit's response to one onset (#596's test); and that test on untrained nets, so
    the page can show it is able to fail."""
    import torch

    from bugarach.learn.nets import ARCHITECTURES
    enc, _, _ = _bench(PROBE_RECORDING)
    out = []
    for r in rows:
        if r["draw"] != "second":
            continue
        fit = _load_fit(r["net"], r["cfg"], r["seed"], r["recs"])
        assert fit.dt == 0.1, fit.dt
        m = fit.model.cpu().eval()
        p = _head_probe(m, enc.raster)
        entry = dict(net=r["net"], cfg=r["cfg"], seed=r["seed"], recs=r["recs"], role=r["role"],
                     lr=r["lr"], collapsed=r["collapsed"],
                     min_share_varying=min(p["varying"]), min_share_positive=min(p["positive"]),
                     logit_sd=float(p["logit"][EDGE:-EDGE].astype("float64").std()),
                     onset_response=_onset_response(m),
                     threshold=float(fit.threshold))
        if r["net"] == "chorus_gain_norm":
            # the largest change across the fit's vote gains, as a fraction of where they started
            entry["vote_gain_moved"] = float((m.vote_gain.detach() / r["vote_gain"] - 1).abs().max())
        out.append(entry)
    shown = json.loads((_results("second") / "configs" / "chorus_norm"
                        / f"{SHOWN['collapsed'][0]}.json").read_text())["overrides"]
    controls = []
    for net, over in (("chorus", {}), ("chorus_norm", shown)):
        for s in range(3):
            torch.manual_seed(s)
            m = ARCHITECTURES[net].make(**over).eval()
            controls.append(dict(net=net, seed=s, onset_response=_onset_response(m)))
    return dict(fits=out, controls=controls, recording=PROBE_RECORDING)


# ---- trace: the problem itself -----------------------------------------------------------------

def trace() -> dict:
    """The collapsed fit and the working fit that the replays follow (``SHOWN``), run on one
    recording held out from both: their output over time, their calls, and the planted events."""
    import numpy as np

    from bugarach.learn.encode import decode
    runs = {k: json.loads(_fit_bytes("chorus_norm", *SHOWN[k], suffix=".run.json")) for k in SHOWN}
    trained_on = set().union(*(set(r["recordings"]) for r in runs.values()))
    # the recordings both fits were scored on, less everything either trained or picked a threshold on
    scored, archived = None, {}
    for k, (cfg, seed, recs) in SHOWN.items():
        names = set()
        for _, raw in R.Archive(_results("second"), "scores").items(
                lambda n: n.startswith(f"scores/chorus_norm/{cfg}/seed{seed}__recs-{recs}__fold")):
            d = json.loads(raw)
            names |= set(d["rows"])
            for rid, row in d["rows"].items():         # the calls the run itself counted
                archived[(k, rid)] = row[d["own_index"]]["n_detected"]
        scored = names if scored is None else scored & names
    rec_id = sorted(x for x in scored - trained_on if x.startswith("quiet:"))[0]
    enc, y, gt = _bench(rec_id)
    bin_ = 10
    doc = dict(recording=rec_id, dt=float(enc.dt), n_frames=int(enc.n_frame), bin_frames=bin_,
               events=[[float(a) - float(enc.t0), float(b) - float(enc.t0)]
                       for a, b in (e.observed_span for e in gt.events)], fits={})
    for k, (cfg, seed, recs) in SHOWN.items():
        fit = _load_fit("chorus_norm", cfg, seed, recs)
        assert fit.dt == 0.1, fit.dt
        logit = _head_probe(fit.model.cpu().eval(), enc.raster)["logit"].astype(float)
        det = decode(1 / (1 + np.exp(-logit)), threshold=fit.threshold,
                     merge_gap_frames=fit.merge_gap_frames)
        # this re-scoring (CPU) must make the calls the run made (GPU) on this recording
        assert len(det.onset_frame) == archived[(k, rec_id)], (k, len(det.onset_frame))
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
        k, float((o[..., EDGE:-EDGE].transpose(0, 1).reshape(o.shape[1], -1).std(dim=1)
                    >= SILENT).float().mean())))
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
N_PERM = 1999                                # shuffles for the permutation tests
DIAGNOSIS_596 = "7fc052d"                    # the commit on replicate-run carrying PR #596's diagnosis
RULE_WORDS = {"gated": "under the false-alarm budget", "ungated": "on F1 alone"}
# one marker per encoder shape in Figure 2: shape is carried by the mark, not by a color
MARKS = {(4, 4): "circle", (4, 6): "square", (8, 4): "triangle", (8, 6): "diamond"}


def _identity(r: dict) -> tuple:
    """What a configuration is, apart from how long it trains."""
    return (r["net"], r["lr"], r["width"], r["depth"], r["top_m"], r["vote_gain"])


def _twin_groups(rows: list[dict]) -> list[list[str]]:
    """Configurations identical but for step count, shortest first. Training is deterministic, the
    learning rate constant and the step count only decides where it stops, so a shorter twin's fit
    is its longer twin's fit cut off early: the same trajectory, not a second sample."""
    by, steps = defaultdict(set), {}
    for r in rows:
        by[_identity(r)].add(r["cfg"])
        steps[r["cfg"]] = r["steps"]
    return [sorted(g, key=lambda c: steps[c]) for g in by.values() if len(g) > 1]


def _cluster_test(rows, net, level, rnd, draws=("first", "second")) -> float:
    """Does collapse cluster by ``level`` (training seed, or fold pair) inside a configuration?
    Statistic: over every (draw, configuration), the spread across levels of the collapsed count;
    null: the collapse labels shuffled within each (draw, configuration). Shorter twins are left
    out, since they repeat their longer twin. Returns the permutation p value."""
    shorter = {c for g in _twin_groups(rows) for c in g[:-1]}
    groups = defaultdict(list)
    for r in rows:
        if r["net"] == net and r["cfg"] not in shorter and r["draw"] in draws:
            groups[(r["draw"], r["cfg"])].append((level(r), r["collapsed"]))

    def stat(labelled):
        # n times the spread, in integers: it ranks shuffles exactly as the spread does, and float
        # sums round differently across Python versions (3.12's sum() compensates, 3.11's does
        # not), which moved the p value in the last digit and broke the byte-for-byte rebuild
        tot = 0
        for items in labelled:
            counts = defaultdict(int)
            for lv, c in items:
                counts[lv] += c
            vals = list(counts.values())
            tot += len(vals) * sum(v * v for v in vals) - sum(vals) ** 2
        return tot

    obs = stat(groups.values())
    hits = 0
    for _ in range(N_PERM):
        shuffled = []
        for items in groups.values():
            labels = [c for _, c in items]
            labels = [labels[i] for i in rnd.permutation(len(labels))]
            shuffled.append([(lv, c) for (lv, _), c in zip(items, labels)])
        hits += stat(shuffled) >= obs
    return (1 + hits) / (N_PERM + 1)


def _seed_carryover(rows, net, rnd) -> tuple[float, float]:
    """Does a (configuration, seed) that collapses more than its configuration's other seeds in one
    draw do so in the other? Same seed means the same starting weights and crop order in both draws;
    the recordings differ. Returns the correlation across draws of each seed's collapsed count minus
    its configuration's mean, and a one-sided permutation p (seeds shuffled within configuration)."""
    shorter = {c for g in _twin_groups(rows) for c in g[:-1]}
    k = defaultdict(int)
    for r in rows:
        if r["net"] == net and r["cfg"] not in shorter:
            k[(r["draw"], r["cfg"], r["seed"])] += r["collapsed"]
    cfgs = sorted({c for (_, c, _) in k})

    def dev(draw, cfg, order):
        # three times the deviation from the configuration's mean: integers, so every sum below is
        # exact on every Python version, and the correlation is unchanged by the scale
        v = [k[(draw, cfg, s)] for s in order]
        return [3 * x - sum(v) for x in v]

    def corr(order_of):
        a, b = [], []
        for c in cfgs:
            a += dev("first", c, (0, 1, 2))
            b += dev("second", c, order_of(c))
        sa = math.sqrt(sum(x * x for x in a)) or 1.0
        sb = math.sqrt(sum(x * x for x in b)) or 1.0
        return sum(x * y for x, y in zip(a, b)) / (sa * sb)

    obs = corr(lambda c: (0, 1, 2))
    hits = 0
    for _ in range(N_PERM):
        perms = {c: [int(i) for i in rnd.permutation(3)] for c in cfgs}
        hits += corr(lambda c: tuple(perms[c])) >= obs
    return obs, (1 + hits) / (N_PERM + 1)


def _ypanel_label(svg, x, y, text):
    svg.add(f'<text x="0" y="0" font-size="12" text-anchor="middle" fill="var(--ink-2)" '
            f'transform="translate({x},{y:.1f}) rotate(-90)">{R.esc(text)}</text>')


def _polyline(svg, pts, col, *, width=2, dash=None, title=None):
    d = f' stroke-dasharray="{dash}"' if dash else ""
    t = f"<{R.SVG_TITLE}>{R.esc(title)}</{R.SVG_TITLE}>" if title else ""
    svg.add(f'<polyline fill="none" stroke="{col}" stroke-width="{width}"{d} points="'
            + " ".join(f"{a:.1f},{b:.1f}" for a, b in pts) + f'">{t}</polyline>')


def _mark(svg, x, y, shape, r, fill, title):
    t = f"<{R.SVG_TITLE}>{R.esc(title)}</{R.SVG_TITLE}>"
    if shape == "circle":
        svg.add(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="{r}" fill="{fill}">{t}</circle>')
    elif shape == "square":
        svg.add(f'<rect x="{x - r:.1f}" y="{y - r:.1f}" width="{2 * r}" height="{2 * r}" '
                f'fill="{fill}">{t}</rect>')
    elif shape == "triangle":
        svg.add(f'<path d="M{x:.1f},{y - r - 1:.1f} L{x + r + 1:.1f},{y + r:.1f} '
                f'L{x - r - 1:.1f},{y + r:.1f} z" fill="{fill}">{t}</path>')
    else:
        svg.add(f'<path d="M{x:.1f},{y - r - 1:.1f} L{x + r + 1:.1f},{y:.1f} L{x:.1f},'
                f'{y + r + 1:.1f} L{x - r - 1:.1f},{y:.1f} z" fill="{fill}">{t}</path>')


def fig_problem(tr: dict) -> str:
    """The problem itself: a collapsed fit and a working fit of the same configuration and fold pair
    on one recording held out from both. Panel A, the lane: planted events and each fit's calls.
    Panels B and C: each fit's output, on its own y range with its own threshold."""
    from bugarach.time_axis import label, ticks
    left, top, pw = 190, 12, 680
    lane_h, ph, gap = 22, 120, 30
    w = left + pw + 110
    h = top + 3 * lane_h + 14 + 2 * ph + gap + 72
    svg = R.Svg(w, h, "the output of a collapsed fit and a working one")
    total = tr["n_frames"] * tr["dt"]
    sx = lambda sec: left + sec / total * pw
    cols = {"working": "var(--c1)", "collapsed": "var(--c2)"}
    svg.text(left - 180, top + 10, "A", size=12, weight="bold")
    rows = [("planted events", None), ("working fit's calls", "working"),
            ("collapsed fit's calls", "collapsed")]
    for i, (words, k) in enumerate(rows):
        y = top + i * lane_h + lane_h / 2
        svg.text(left - 10, y + 4, words, size=12, anchor="end", fill="var(--ink-2)")
        if k is None:
            for a, b in tr["events"]:
                xm = sx((a + b) / 2)
                svg.add(f'<path d="M{xm - 5:.1f},{y - 5:.1f} L{xm + 5:.1f},{y - 5:.1f} '
                        f'L{xm:.1f},{y + 5:.1f} z" fill="var(--ink)"><{R.SVG_TITLE}>planted event '
                        f'at {label(round(a))}</{R.SVG_TITLE}></path>')
        else:
            for a, wd in tr["fits"][k]["calls"]:
                x0, x1 = sx(a * tr["dt"]), sx((a + wd) * tr["dt"])
                svg.rect(x0, y - 5, max(2.0, x1 - x0), 10, fill=cols[k],
                         title=f"{k} fit's call from {label(round(a * tr['dt']))}, "
                               f"{label(round(wd * tr['dt']))} long")
    y0 = top + 3 * lane_h + 14
    for j, k in enumerate(("working", "collapsed")):
        f = tr["fits"][k]
        pt = y0 + j * (ph + gap)
        lo, hi = min(min(f["lo"]), f["threshold_logit"]), max(max(f["hi"]), f["threshold_logit"])
        pad = 0.08 * (hi - lo)
        lo, hi = lo - pad, hi + pad
        sy = lambda v: pt + ph - (v - lo) / (hi - lo) * ph
        svg.text(left - 180, pt + 10, "BC"[j], size=12, weight="bold")
        svg.rect(left, pt, pw, ph, stroke="var(--rule)")
        for t in (math.ceil(lo), math.floor(hi)):
            svg.text(left - 6, sy(t) + 4, f"{t}".replace("-", "−"), size=12, anchor="end",
                     fill="var(--ink-2)")
        bw = tr["bin_frames"] * tr["dt"]
        up = [(sx(i * bw), sy(v)) for i, v in enumerate(f["hi"])]
        dn = [(sx(i * bw), sy(v)) for i, v in enumerate(f["lo"])][::-1]
        svg.add(f'<polygon fill="{cols[k]}" fill-opacity="0.85" stroke="{cols[k]}" '
                f'stroke-width="0.6" points="' + " ".join(f"{a:.1f},{b:.1f}" for a, b in up + dn)
                + f'"><{R.SVG_TITLE}>{k} fit: output logit, lowest to highest in each '
                f'{bw:.0f}-second bin</{R.SVG_TITLE}></polygon>')
        svg.line(left, sy(f["threshold_logit"]), left + pw, sy(f["threshold_logit"]),
                 stroke="var(--ink)", width=1.2, dash="5 4")
        # the threshold's value sits outside the plot, where no trace can cross it
        svg.text(left + pw + 6, sy(f["threshold_logit"]) + 4,
                 f"{f['threshold_logit']:.1f}".replace("-", "−"), size=12, fill="var(--ink-2)")
        _ypanel_label(svg, left - 44, pt + ph / 2, f"{k} fit · logit")
    base = y0 + 2 * ph + gap
    svg.line(left, base + 4, left + pw, base + 4, stroke="var(--ink-3)")
    for t in ticks(0, total):
        svg.line(sx(t), base + 4, sx(t), base + 8, stroke="var(--ink-3)")
        svg.text(sx(t), base + 21, label(t), size=12, anchor="middle", fill="var(--ink-2)")
    svg.text(left + pw / 2, base + 38, "time in the recording", size=12, anchor="middle",
             fill="var(--ink-2)")
    ky = h - 8
    svg.line(left, ky - 4, left + 24, ky - 4, stroke="var(--ink)", width=1.2, dash="5 4")
    svg.text(left + 30, ky, "the fit's own threshold, as a logit (its value at the right)", size=12)
    return svg.render()


def fig_rates(rows: list[dict]) -> str:
    """Share of each configuration's inner fits that collapsed, both draws pooled, by learning rate;
    the mark's shape is the encoder's shape; equal shares stack vertically."""
    left, top, rh, pw, gap = 130, 34, 56, 320, 110
    w = left + 2 * (pw + gap)
    h = top + rh * 3 + 96
    svg = R.Svg(w, h, "collapse share by configuration, learning rate and encoder shape")
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
            svg.text(x0 + pw + 8, y, f"{sum(r['collapsed'] for r in rs)} of {len(rs)}", size=12,
                     fill="var(--ink-2)")
            svg.text(x0 + pw + 8, y + 14, "fits", size=12, fill="var(--ink-2)")
            per = defaultdict(lambda: [0, 0])
            about = {}
            for r in rs:
                per[r["cfg"]][0] += r["collapsed"]
                per[r["cfg"]][1] += 1
                about[r["cfg"]] = r
            stacks = defaultdict(list)
            for k, (c, n) in sorted(per.items()):
                stacks[c].append((k, n))
            for c, ks in stacks.items():
                for q, (k, n) in enumerate(ks):
                    yy = y + (q - (len(ks) - 1) / 2) * 10
                    a = about[k]
                    gain = f", vote gain {a['vote_gain']:g}" if a["vote_gain"] is not None else ""
                    _mark(svg, sx(c / n), yy, MARKS[(a["width"], a["depth"])], 4, "var(--ink-2)",
                          f"{net}, encoder {a['width']} wide × {a['depth']} deep, top {a['top_m']}"
                          f"{gain}, {a['steps']:,} steps, lr {lr:g} ({k[:8]}): {c} of {n} fits "
                          f"collapsed")
    ky = h - 10
    for q, (s, shape) in enumerate(MARKS.items()):
        kx = left + q * 150
        _mark(svg, kx + 6, ky - 4, shape, 4, "var(--ink-2)", f"encoder {s[0]} × {s[1]}")
        svg.text(kx + 16, ky, f"encoder {s[0]} wide × {s[1]} deep", size=12)
    return svg.render()


def fig_census(cen: list[dict], lo: int) -> str:
    """Each second-draw inner fit: the smallest share of varying units in any head layer, against the
    standard deviation of its output, both measured away from the recording's ends."""
    left, top, ph, pw, gap = 78, 30, 260, 380, 60
    w = left + 2 * pw + gap + 30
    h = top + ph + 90
    svg = R.Svg(w, h, "silent head layers and flat outputs")
    hi = 2
    sup = str.maketrans("-0123456789", "⁻⁰¹²³⁴⁵⁶⁷⁸⁹")
    for j, net in enumerate(CHORUS):
        x0 = left + j * (pw + gap)
        sx = R.x_axis(svg, x0, x0 + pw, top + ph + 4, 0, 1, (0, 0.25, 0.5, 0.75, 1.0),
                      "smallest share of varying units in any head layer (0: a silent layer)",
                      fmt="{:.2f}")
        sy = lambda v: top + ph - (v - lo) / (hi - lo) * ph
        for t in range(lo, hi + 1, 2):
            svg.line(x0, sy(t), x0 + pw, sy(t), stroke="var(--rule)")
            if j == 0:
                svg.text(x0 - 8, sy(t) + 4, ("≤ " if t == lo else "") + "10" + str(t).translate(sup),
                         size=12, anchor="end", fill="var(--ink-2)")
        svg.text(x0, top - 12, f"{'A' if j == 0 else 'B'} · {net}", size=12, weight="bold")
        rnd = random.Random(1)
        for e in sorted(cen, key=lambda e: not e["collapsed"]):
            if e["net"] != net:
                continue
            xj = min(1, max(0, e["min_share_varying"] + rnd.uniform(-0.02, 0.02)))
            floored = e["logit_sd"] < 10 ** lo
            v = lo if floored else math.log10(e["logit_sd"])
            svg.circle(sx(xj), sy(v), 3, stroke="none", opacity=0.55, hollow=floored,
                       fill="var(--c2)" if e["collapsed"] else "var(--c1)",
                       title=f"{net} {e['cfg'][:8]}, seed {e['seed']}: "
                             f"{'collapsed' if e['collapsed'] else 'working'}, smallest varying "
                             f"share {e['min_share_varying']:.3f}, output SD {e['logit_sd']:.3g}")
    _ypanel_label(svg, 18, top + ph / 2, "SD of the output logit (logits, log scale)")
    ly = h - 14
    keys = (("var(--c1)", "working", False), ("var(--c2)", "collapsed", False),
            ("var(--ink-2)", f"hollow: SD below 10{str(lo).translate(sup)}, drawn on the floor", True))
    xk = left
    for col, words, hollow in keys:
        svg.circle(xk + 6, ly - 4, 5, fill=col, stroke="none", hollow=hollow)
        svg.text(xk + 16, ly, words, size=12)
        xk += 30 + 7.2 * len(words)
    return svg.render()


def fig_onset(groups: list[tuple[str, list[float], str]], floor: float) -> str:
    """PR #596's test on every group: how far one onset moves a vote, one mark per net or fit."""
    left, top, rh, pw = 250, 16, 34, 560
    w, h = left + pw + 30, top + rh * len(groups) + 64
    svg = R.Svg(w, h, "how far one onset moves a vote")
    lo, hi = math.log10(floor), 0.0
    sx = lambda v: left + (math.log10(max(v, floor)) - lo) / (hi - lo) * pw
    ticks = [10.0 ** e for e in range(int(lo), 1)]
    sup = str.maketrans("-0123456789", "⁻⁰¹²³⁴⁵⁶⁷⁸⁹")
    base = top + rh * len(groups) + 4
    svg.line(left, base, left + pw, base, stroke="var(--ink-3)")
    for t in ticks:
        svg.line(sx(t), top, sx(t), base, stroke="var(--rule)")
        svg.text(sx(t), base + 17, ("≤ " if t == floor else "") + "10"
                 + str(int(round(math.log10(t)))).translate(sup), size=12, anchor="middle",
                 fill="var(--ink-2)")
    svg.text(left + pw / 2, base + 36, "largest change in any vote for one onset (0 to 1 scale, "
             "log)", size=12, anchor="middle", fill="var(--ink-2)")
    rnd = random.Random(3)
    for i, (words, vals, col) in enumerate(groups):
        y = top + i * rh + rh / 2
        if i % 2:
            svg.rect(left, y - rh / 2, pw, rh, fill="var(--band)")
        svg.text(left - 10, y + 4, f"{words} ({len(vals)})", size=12, anchor="end")
        for v in vals:
            svg.circle(sx(v), y + rnd.uniform(-8, 8), 3, fill=col, stroke="none", opacity=0.6,
                       hollow=v < floor, title=f"{words}: {v:.2g}")
    return svg.render()


def _step_axis(svg, left, pw, y, steps):
    return R.x_axis(svg, left, left + pw, y, 0, steps, list(range(0, steps + 1, 300)),
                    "training step", fmt="{:.0f}")


def fig_onset_in_training(pair: dict[str, tuple[dict, str]]) -> str:
    """Panel A, silent head layers on each logged training batch; panel B, the training loss; one
    x axis for both."""
    left, top, pa, pb, gap, pw = 70, 20, 110, 220, 22, 740
    w = left + pw + 20
    h = top + pa + gap + pb + 90
    svg = R.Svg(w, h, "the collapsed fit's loss stalls, then its head goes silent")
    steps = max(e["step"] for d, _ in pair.values() for e in d["log"])
    sxs = lambda s: left + s / steps * pw
    n = max(len(e["head_varying"]) for d, _ in pair.values() for e in d["log"])
    sya = lambda v: top + pa - v / n * pa
    svg.text(left, top - 6, "A", size=12, weight="bold")
    for t in range(0, n + 1, 4):
        svg.line(left, sya(t), left + pw, sya(t), stroke="var(--rule)")
        svg.text(left - 8, sya(t) + 4, str(t), size=12, anchor="end", fill="var(--ink-2)")
    _ypanel_label(svg, 18, top + pa / 2, "silent layers (of 8)")
    tb = top + pa + gap
    syb = lambda v: tb + pb - min(2.0, max(0.0, v)) / 2.0 * pb
    svg.text(left, tb - 6, "B", size=12, weight="bold")
    for t in (0.0, 0.5, 1.0, 1.5, 2.0):
        svg.line(left, syb(t), left + pw, syb(t), stroke="var(--rule)")
        svg.text(left - 8, syb(t) + 4, f"{t:.1f}", size=12, anchor="end", fill="var(--ink-2)")
    _ypanel_label(svg, 18, tb + pb / 2, "training loss")
    _step_axis(svg, left, pw, tb + pb + 4, steps)
    # the working fit is drawn last so its line at 0 is not hidden under the collapsed fit's
    for k, (words, (d, col)) in sorted(enumerate(pair.items()), key=lambda kv: "working" in kv[1][0]):
        L = d["log"]
        _polyline(svg, [(sxs(e["step"]), sya(sum(v == 0 for v in e["head_varying"]))) for e in L],
                  col, title=words)
        _polyline(svg, [(sxs(L[i]["step"]), syb(st.mean(e["loss"] for e in L[max(0, i - 4):i + 1])))
                        for i in range(len(L))], col, title=words)
    ky = h - 12
    for k, (words, (d, col)) in enumerate(pair.items()):
        svg.line(left + k * 260, ky - 4, left + k * 260 + 22, ky - 4, stroke=col, width=3)
        svg.text(left + k * 260 + 30, ky, words, size=12)
    return svg.render()


def fig_curves(reps: dict[str, tuple[dict, str, bool]], smooth) -> str:
    """Training loss for the collapsed fit as run and replayed with one change each."""
    left, top, ph, pw = 70, 24, 300, 740
    w, h = left + pw + 20, top + ph + 70 + 22 * len(reps)
    svg = R.Svg(w, h, "training loss, replayed with one change")
    steps = max(e["step"] for d, _, _ in reps.values() for e in d["log"])
    sx = _step_axis(svg, left, pw, top + ph + 4, steps)
    top_y = 2.5
    sy = lambda v: top + ph - min(top_y, max(0.0, v)) / top_y * ph
    for t in (0.0, 0.5, 1.0, 1.5, 2.0, 2.5):
        svg.line(left, sy(t), left + pw, sy(t), stroke="var(--rule)")
        svg.text(left - 8, sy(t) + 4, f"{t:.1f}", size=12, anchor="end", fill="var(--ink-2)")
    _ypanel_label(svg, 18, top + ph / 2, "training loss (mean of 5 logged steps)")
    order = sorted(enumerate(reps.items()), key=lambda kv: "as run" in kv[1][0])
    for k, (words, (d, col, dashed)) in order:
        L = d["log"]
        _polyline(svg, [(sx(e["step"]), sy(s)) for e, s in zip(L, smooth(d))], col,
                  dash="7 4" if dashed else None, title=words)
    for k, (words, (d, col, dashed)) in enumerate(reps.items()):
        ky = top + ph + 62 + 22 * k
        svg.line(left, ky - 4, left + 22, ky - 4, stroke=col, width=3, dash="7 4" if dashed else None)
        svg.text(left + 30, ky, words, size=12)
    return svg.render()


def fig_warmup(wu: list[dict], trains, smooth) -> str:
    """The 200-step warm-up at lr 0.03 on other collapsed fits: every logged loss, one line per fit."""
    left, top, ph, pw = 70, 24, 240, 740
    w, h = left + pw + 20, top + ph + 92
    svg = R.Svg(w, h, "a 200-step warm-up on other collapsed fits")
    steps = max(e["step"] for d in wu for e in d["log"])
    sx = R.x_axis(svg, left, left + pw, top + ph + 4, 0, steps,
                  list(range(0, steps + 1, 600)), "training step", fmt="{:.0f}")
    top_y = 2.5
    sy = lambda v: top + ph - min(top_y, max(0.0, v)) / top_y * ph
    for t in (0.0, 0.5, 1.0, 1.5, 2.0, 2.5):
        svg.line(left, sy(t), left + pw, sy(t), stroke="var(--rule)")
        svg.text(left - 8, sy(t) + 4, f"{t:.1f}", size=12, anchor="end", fill="var(--ink-2)")
    svg.line(left, sy(0.5), left + pw, sy(0.5), stroke="var(--ink)", width=1.2, dash="5 4")
    _ypanel_label(svg, 18, top + ph / 2, "training loss (mean of 5 logged steps)")
    for d in wu:
        _polyline(svg, [(sx(e["step"]), sy(s)) for e, s in zip(d["log"], smooth(d))],
                  "var(--c1)" if trains(d) else "var(--c2)", width=1.6,
                  title=f"{d['cfg'][:8]} seed {d['seed']}")
    ky = h - 26
    for k, (col, words) in enumerate((("var(--c1)", "trains"), ("var(--c2)", "does not train"))):
        svg.line(left + k * 160, ky - 4, left + k * 160 + 22, ky - 4, stroke=col, width=3)
        svg.text(left + k * 160 + 30, ky, words, size=12)
    svg.line(left + 320, ky - 4, left + 344, ky - 4, stroke="var(--ink)", width=1.2, dash="5 4")
    svg.text(left + 350, ky, "loss 0.5, the line between them", size=12)
    return svg.render()


# Slots 1-5 of the reference categorical palette, in its validated order: adjacent pairs pass the
# color-vision checks in both modes, and slots 1-2 (working, collapsed) pass all pairs. The fifth
# replay line (a 50-step warm-up) is dashed ink rather than slot 6, which has no dark-mode step.
CSS_EXTRA = """
:root{--c1:#2a78d6;--c2:#eb6834;--c3:#1baf7a;--c4:#eda100;--c5:#e87ba4}
@media (prefers-color-scheme: dark){:root:not([data-theme="light"]){--c1:#3987e5;--c2:#d95926;
--c3:#199e70;--c4:#c98500;--c5:#d55181}}
:root[data-theme="dark"]{--c1:#3987e5;--c2:#d95926;--c3:#199e70;--c4:#c98500;--c5:#d55181}
td,th{white-space:nowrap}
code{overflow-wrap:anywhere}
.refs li{font-size:14px}
.terms{font-size:15px}
"""


def page(work: Path) -> str:
    table = json.loads((work / "collapse_table.json").read_text())
    rows = [r for r in table if r["role"] == "inner"]
    refits = [r for r in table if r["role"] != "inner"]
    census_doc = json.loads((work / "census.json").read_text())
    census_all, controls = census_doc["fits"], census_doc["controls"]
    cen = [e for e in census_all if e["role"] == "inner"]
    sel = json.loads((work / "selections.json").read_text())
    tr = json.loads((work / "trace.json").read_text())
    reps = {p.stem: json.loads(p.read_text()) for p in sorted((work / "replays").glob("*.json"))}
    import numpy as np
    # numpy's legacy RandomState, not the stdlib: random.shuffle and random.sample draw differently
    # on Python 3.11 and 3.12+, and the page must rebuild byte for byte on every version CI runs
    rnd = np.random.RandomState(2026)
    cfg_row = {r["cfg"]: r for r in rows}

    def rate(net, pred, rs=rows):
        rs = [r for r in rs if r["net"] == net and pred(r)]
        return sum(r["collapsed"] for r in rs), len(rs)

    pct = lambda cn: f"{cn[0] / cn[1]:.0%}"
    of = lambda cn, unit="fits": f"{cn[0]} of {cn[1]} {unit}"
    fmt_p = lambda p: f"p = {p:.3f}" if p >= 0.001 else "p < 0.001"

    # ---- counts, draw by draw and together
    per_draw = {(n, d): rate(n, lambda r, d=d: r["draw"] == d) for n in CHORUS for d in DRAW_DIRS}
    by_lr = {(n, lr): rate(n, lambda r, lr=lr: r["lr"] == lr) for n in CHORUS for lr in LRS}
    n_cfg = {n: len({r["cfg"] for r in rows if r["net"] == n}) for n in CHORUS}
    per_draw_n = {n: per_draw[(n, "second")][1] for n in CHORUS}
    assert per_draw_n["chorus_norm"] == n_cfg["chorus_norm"] * 18

    # ---- the overlap between draws, against two expectations
    fitkey = lambda r: (r["cfg"], r["seed"], tuple(r["pair"]))
    colset = lambda d, n: {fitkey(r) for r in rows if r["draw"] == d and r["net"] == n
                           and r["collapsed"]}
    both = {n: len(colset("first", n) & colset("second", n)) for n in CHORUS}
    per_cfg_draw = defaultdict(lambda: [0, 0])
    for r in rows:
        per_cfg_draw[(r["net"], r["cfg"], r["draw"])][0] += r["collapsed"]
        per_cfg_draw[(r["net"], r["cfg"], r["draw"])][1] += 1
    exp_cfg = {n: math.fsum(per_cfg_draw[(n, c, "first")][0] * per_cfg_draw[(n, c, "second")][0]
                      / per_cfg_draw[(n, c, "first")][1]
                      for c in {r["cfg"] for r in rows if r["net"] == n}) for n in CHORUS}
    exp_flat = {n: per_draw[(n, "first")][0] * per_draw[(n, "second")][0] / per_draw_n[n]
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
    assert cn_lo[0] / cn_lo[1] < 0.02 and min(cn_hi) >= 0.4
    shape_lr = {(n, lr, s): rate(n, lambda r, lr=lr, s=s: r["lr"] == lr
                                 and (r["width"], r["depth"]) == s)
                for n in CHORUS for lr in LRS for s in SHAPES}
    steps_hi = {s: rate("chorus_norm", lambda r, s=s: r["lr"] == 0.03 and r["steps"] == s)
                for s in sorted({r["steps"] for r in rows if r["net"] == "chorus_norm"
                                 and r["lr"] == 0.03})}
    longest = max(steps_hi)
    assert {r["depth"] for r in rows if r["net"] == "chorus_norm" and r["lr"] == 0.03
            and r["steps"] == longest} == {6}, "the longest runs are all deep: the confound stated"
    gain_other = (sum(shape_lr[("chorus_gain_norm", 0.03, s)][0] for s in SHAPES if s != (4, 6)),
                  sum(shape_lr[("chorus_gain_norm", 0.03, s)][1] for s in SHAPES if s != (4, 6)))
    p_seed_draw = {d: _cluster_test(rows, "chorus_norm", lambda r: r["seed"], rnd, (d,))
                   for d in DRAW_DIRS}
    p_pair = {n: _cluster_test(rows, n, lambda r: tuple(r["pair"]), rnd) for n in CHORUS}
    carry_r, carry_p = _seed_carryover(rows, "chorus_norm", rnd)
    twins = _twin_groups(rows)
    assert all(len(g) == 2 for g in twins), "the twins come in pairs"
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

    # ---- what tuning chose
    picks = [dict(p, draw=d, lr=cfg_row[p["cfg"]]["lr"]) for d, v in sel.items() for p in v["picks"]]
    grid_floor = {d: v["threshold_grid_floor"] for d, v in sel.items()}
    assert len(set(grid_floor.values())) == 1
    grid_floor = next(iter(grid_floor.values()))
    chose = {(n, rule, lr): sum(p["net"] == n and p["rule"] == rule and p["lr"] == lr for p in picks)
             for n in CHORUS for rule in RULE_WORDS for lr in LRS}
    n_picks = {(n, rule): sum(chose[(n, rule, lr)] for lr in LRS) for n in CHORUS for rule in RULE_WORDS}
    assert all(chose[("chorus_norm", rule, 0.03)] == 0 for rule in RULE_WORDS)
    assert chose[("chorus_gain_norm", "gated", 0.03)] == 0
    missing = lambda r: ({0, 1, 2, 3} - set(r["pair"])).pop()
    ref_bad = [r for r in refits if r["collapsed"]]
    bad_rules = {(r["draw"], r["net"], r["cfg"], missing(r)): sorted(
        p["rule"] for p in picks if (p["draw"], p["net"], p["cfg"], p["outer"])
        == (r["draw"], r["net"], r["cfg"], missing(r))) for r in ref_bad}
    bad_by_rule = {(n, rule): sum(1 for r in ref_bad if r["net"] == n and rule in
                                  bad_rules[(r["draw"], r["net"], r["cfg"], missing(r))])
                   for n in CHORUS for rule in RULE_WORDS}

    # ---- inside the collapsed fits
    silent = lambda e: e["min_share_varying"] == 0
    cz = {(n, col): [e for e in cen if e["net"] == n and e["collapsed"] == col]
          for n in CHORUS for col in (True, False)}
    n_silent = {k: sum(silent(e) for e in v) for k, v in cz.items()}
    n_sign = {k: sum(e["min_share_positive"] == 0 for e in v) for k, v in cz.items()}
    assert all(n_silent[(n, True)] == len(cz[(n, True)]) and n_silent[(n, False)] == 0
               for n in CHORUS), "every collapsed fit has a silent layer and no working fit does"
    med = lambda v, f: st.median(e[f] for e in v)
    sd_coll_max = max(e["logit_sd"] for e in census_all if e["collapsed"])
    sd_work_min = min(e["logit_sd"] for e in census_all if not e["collapsed"])
    assert sd_coll_max < sd_work_min, "the output's spread separates collapsed from working fits"
    sd_floor = math.floor(math.log10(min(e["logit_sd"] for e in census_all if e["logit_sd"] > 0)))
    sd_floor = max(sd_floor, -12)
    floored = {n: sum(e["logit_sd"] < 10 ** sd_floor for e in cen if e["net"] == n) for n in CHORUS}
    assert all(e["threshold"] == grid_floor for e in census_all if e["collapsed"]), \
        "every collapsed fit's threshold is the declared grid's floor"
    work_floor = sum(e["threshold"] == grid_floor for e in cen
                     if e["net"] == "chorus_norm" and not e["collapsed"])
    ref_census_bad = [e for e in census_all if e["role"] != "inner" and e["collapsed"]]
    plain = [c["onset_response"] for c in controls if c["net"] == "chorus"]
    untrained = [c["onset_response"] for c in controls if c["net"] == "chorus_norm"]
    deaf = max(plain)                     # #596's deaf net: no vote moves more than this
    onset = {k: [e["onset_response"] for e in v] for k, v in cz.items()}
    as_deaf = {k: sum(v <= deaf for v in vals) for k, vals in onset.items()}
    assert max(plain) < 0.001 and min(onset[("chorus_norm", False)]) > 0.1

    # ---- the replays
    smooth = lambda d: [st.mean(e["loss"] for e in d["log"][max(0, i - 4):i + 1])
                        for i in range(len(d["log"]))]
    final = lambda d: st.mean(e["loss"] for e in d["log"][-5:])
    trains = lambda d: final(d) < 0.5
    nsil = lambda e: sum(v == 0 for v in e["head_varying"])
    fid = lambda d: (d["cfg"], d["seed"], d["recs"])
    as_run = [d for d in reps.values() if d["as_run"]]
    assert len(as_run) == 2 and all(d["max_abs_diff_vs_checkpoint"] == 0.0 for d in as_run), \
        "both as-run replays reproduce their checkpoints exactly"
    ref = next(d for d in as_run if fid(d) == SHOWN["collapsed"])
    work_fit = next(d for d in as_run if fid(d) == SHOWN["working"])
    assert not trains(ref) and trains(work_fit)
    cf = {(d["lr"], d["warmup"]): d for d in reps.values()
          if fid(d) == SHOWN["collapsed"] and not d["as_run"]}
    assert trains(cf[(0.01, 0)]) and trains(cf[(0.003, 0)]) and trains(cf[(0.03, 200)]) \
        and not trains(cf[(0.03, 50)]), "the counterfactuals come out as the page says"
    first_sd = [d["log"][0]["logit_sd"] for d in reps.values()]
    escape = next(e["step"] for e, s in zip(work_fit["log"], smooth(work_fit)) if s < 1.0)
    # the head at the first logged batch (the starting weights), and when training wakes it
    start_silent = [nsil(d["log"][0]) for d in reps.values()]
    wakes = lambda d: next((e["step"] for e in d["log"] if nsil(e) == 0), None)
    assert min(start_silent) >= 5, "every replayed fit's head starts mostly silent"
    work_wake = wakes(work_fit)
    assert work_wake is not None and wakes(ref) is None, "the working head wakes; the collapsed never"
    ref_least = min(nsil(e) for e in ref["log"])
    end_silent = nsil(ref["log"][-1])
    d50 = cf[(0.03, 50)]
    wu50_wake = wakes(d50)
    wu50_back = next(e["step"] for e in d50["log"] if e["step"] > wu50_wake and nsil(e))
    wu50_end = nsil(d50["log"][-1])
    wu200_wake = wakes(cf[(0.03, 200)])
    wu = sorted((d for d in reps.values() if d["warmup"] == 200 and d["lr"] == 0.03
                 and fid(d) != SHOWN["collapsed"]), key=lambda d: d["cfg"])
    traj = lambda d: (_identity(cfg_row[d["cfg"]]), d["seed"], d["recs"])
    distinct = {}
    for d in sorted(wu, key=lambda d: -cfg_row[d["cfg"]]["steps"]):
        distinct.setdefault(traj(d), d)
    dist = list(distinct.values())
    dup = [d for d in wu if d not in dist]
    wu_ok = sum(trains(d) for d in dist)
    wu_fail = [d for d in dist if not trains(d)]
    fail_note = "".join(
        f" The one that did not train woke its head by step {wakes(d)} and fell silent again, "
        f"ending with {nsil(d['log'][-1])} of 8 layers silent." if wakes(d) is not None else
        " The one that did not train never woke its head." for d in wu_fail[:1])
    reroll = math.fsum(1 - share("chorus_norm", d["cfg"]) for d in dist)
    wu_cfgs = {d["cfg"] for d in wu}
    own_cfg = [d for d in wu if d["cfg"] == SHOWN["collapsed"][0]]
    tried_cfgs = wu_cfgs | {SHOWN["collapsed"][0]}
    omitted = sorted((c for c in hi_cfgs if c not in tried_cfgs), key=lambda c: share("chorus_norm", c))
    twin_left = [c for c in omitted if any(c in g and set(g) & tried_cfgs for g in twins)]
    low_left = [c for c in omitted if c not in twin_left]
    assert max(share("chorus_norm", c) for c in low_left) < min(
        share("chorus_norm", c) for c in tried_cfgs), "the others left out collapse least"
    fits_replayed = len({fid(d) for d in reps.values()})
    this_cfg = [r for r in rows if r["cfg"] == SHOWN["working"][0] and r["draw"] == "second"]
    this_cfg_working = sum(not r["collapsed"] for r in this_cfg)
    spike = max(max(e["loss"] for e in d["log"]) for d in wu)

    # ---- drawing
    sw = lambda v: f'<span class="sw" style="background:var(--{v})"></span>'
    F = {"problem": 1, "rates": 2, "census": 3, "onset": 4, "training": 5, "curves": 6, "warmup": 7}
    T_ = {"shape": 1, "chose": 2, "warmup": 3}
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
                  "draws.", ["net", "encoder (units wide × layers deep)"] + [f"lr {lr:g}" for lr in LRS],
                  [[n, f"{s[0]} × {s[1]}"] + [shape_cell(n, lr, s) for lr in LRS]
                   for n in CHORUS for s in SHAPES],
                  "A dash: the grid has no configuration of that shape at that learning rate. Shape "
                  "and training length are described here, not tested.")
    t_chose = tab("chose", "What tuning chose: the learning rate of the configuration picked, over "
                  "both draws' 4 outer folds.", ["net", "selection", "lr 0.003", "lr 0.01", "lr 0.03",
                                                  "refits that collapsed"],
                  [[n, RULE_WORDS[rule]] + [f"{chose[(n, rule, lr)]} of {n_picks[(n, rule)]} folds"
                                            for lr in LRS] + [f"{bad_by_rule[(n, rule)]} refits"]
                   for n in CHORUS for rule in RULE_WORDS],
                  "Each fold's pick is refit and scored on the held-out fold. Both selections can pick "
                  "the same configuration, so a collapsed refit can count under both.")
    t_wu = tab("warmup", "The 200-step linear warm-up at lr 0.03, fit by fit.",
               ["fit", "encoder", "top m", "steps", "collapsed fits in its configuration (both "
                "draws)", "final loss", "outcome"],
               [[f"{d['cfg'][:8]}, seed {d['seed']}" + (" (Figure 1's configuration)"
                                                        if d["cfg"] == SHOWN["collapsed"][0] else ""),
                 f"{cfg_row[d['cfg']]['width']} × {cfg_row[d['cfg']]['depth']}",
                 cfg_row[d["cfg"]]["top_m"], f"{d['steps']:,}",
                 f"{per_cfg[('chorus_norm', d['cfg'])][0]} of 36", f"{final(d):.2f}",
                 ("trains" if trains(d) else "does not train")
                 + (" (the same run as a longer twin's, stopped earlier)" if d in dup else "")]
                for d in wu],
               "Final loss: the mean of the last 5 logged steps, on training batches. A fit trains "
               "when that is below 0.5; the collapsed fits sit near 1.5, about what a constant output "
               "scores on these batches.")

    body = f"""
<h1>Why a third of chorus_norm's tuning fits do not train</h1>
<p class="sub">A diagnosis from the saved fits of both draws of the project's fair comparison between
coded detectors and learned nets (goal 2). The draws' results were not changed; {len(reps)} replays
of {fits_replayed} fits retrain them from their own starting points to watch the failure happen.
Simulated recordings only.</p>

<p>chorus_norm and chorus_gain_norm are two of the small neural networks the project trains to find
coordinated events, moments when many cells in a recording become active together. Each reads a
recording as one row per cell (a region of interest, ROI) in 0.1-second frames and outputs a score
for every frame, as a logit (log-odds). A threshold, picked during training from a fixed list of
probabilities, turns the scores into calls, and calls are scored by F1 (the harmonic mean of
precision and recall) against the events planted in the simulation. chorus_gain_norm is chorus_norm
with a learnable steepness and midpoint on each vote.</p>
""" + fig("problem", fig_problem(tr),
          f"<b>A collapsed fit calls the whole recording one event; its working sibling calls "
          f"events.</b> One simulated recording with a quiet background (simulation seed "
          f"{tr['recording'].split(':')[1]}), held out from the training of both fits, with "
          f"{len(tr['events'])} planted events. Panel A: the planted events (▼) and each fit's calls "
          f"({len(tr['fits']['working']['calls'])} for the working fit, "
          f"{len(tr['fits']['collapsed']['calls'])} for the collapsed one). Panels B and C: each fit's "
          f"output logit, lowest to highest in every {tr['bin_frames'] * tr['dt']:.0f}-second bin, "
          f"on its own vertical range, with its threshold dashed. Its only movement is at the "
          f"recording's ends, where the convolutions' zero padding reaches the output. Shaded rows "
          f"in panel A only aid reading.") + f"""
<p class="terms"><b>How the comparison is organized.</b> A <i>draw</i> is one complete run of the
comparison on its own simulated recordings; there are two. A draw's recordings are split into 4
folds. An <i>inner fit</i> trains one configuration at one training seed on 2 of the folds and is
scored on the other 2: 24 configurations × 3 seeds × 6 pairs of folds = {per_draw_n['chorus_norm']}
inner fits per net per draw. For each fold held out in turn, tuning picks a configuration from the
inner fits that did not use it, trains it afresh on the other 3 folds and scores it on the held-out
one: a <i>refit</i>. A <i>configuration</i> is one setting of the encoder's width and depth, how many
of the most active ROIs one pooled statistic averages (top m), the learning rate (lr), the number of
training steps and, for chorus_gain_norm, the vote gain's starting value. A fit <i>collapsed</i> when
it made exactly one call on every recording it was scored on: the whole recording, which matches one
of the 15 planted events, F1 0.125.</p>

<div class="box"><b>The answer.</b>
<ul>
<li><b>The problem.</b> In each draw, {per_draw[('chorus_norm', 'first')][0]} and
{per_draw[('chorus_norm', 'second')][0]} of chorus_norm's {per_draw_n['chorus_norm']} inner fits
collapsed ({ref_('problem', 'a collapsed fit on a held-out recording')}).</li>
<li><b>For chorus_norm it goes with the learning rate.</b> Across both draws,
{of(by_lr[('chorus_norm', 0.03)])} collapse at lr 0.03 and {of(cn_lo)} below it (the grid's rates
are 0.003, 0.01 and 0.03). chorus_gain_norm follows its encoder's shape at least as much, described
here, not tested.</li>
<li><b>The signal stops in the head</b>, the eight layers that turn the pooled per-ROI votes into the
output. Measured away from the recording's ends, every collapsed inner fit in the second draw has a
head layer whose units' outputs do not vary ({n_silent[('chorus_norm', True)]} of
{len(cz[('chorus_norm', True)])} chorus_norm, {n_silent[('chorus_gain_norm', True)]} of
{len(cz[('chorus_gain_norm', True)])} chorus_gain_norm) and no working fit does
({ref_('census', 'silent layers and flat outputs')}).</li>
<li><b>For most chorus_norm fits it is not the failure diagnosed earlier in plain chorus</b> (pull
request 596), whose votes did not respond to events. By that diagnosis's own test, one onset moves a
collapsed chorus_norm fit's vote by a median of {med(cz[('chorus_norm', True)], 'onset_response'):.2f}
against at most {deaf:.4f} for plain chorus; {as_deaf[('chorus_norm', True)]} of
{len(cz[('chorus_norm', True)])} are as deaf as plain chorus. In chorus_gain_norm,
{as_deaf[('chorus_gain_norm', True)]} of {len(cz[('chorus_gain_norm', True)])} are
({ref_('onset', 'the earlier diagnosis’s test')}).</li>
<li><b>Every head starts mostly silent; a collapsed fit's is never woken, and a slower start wakes it.</b>
In every replayed fit the head starts mostly silent ({min(start_silent)} to {max(start_silent)} of its 8 layers). The working fit's wakes by step {work_wake} and its loss
falls; the replayed collapsed fit's never fully wakes and its loss never leaves its start. The same
fit trains at lr 0.003 or 0.01, or at 0.03 with the learning rate ramped up linearly over the first
200 steps; that ramp also brought training loss below 0.5 in {wu_ok} of {len(dist)} other hand-picked
collapsed runs.</li>
<li><b>What it did to the comparison.</b> Tuning picked no lr-0.03 configuration for chorus_norm under
either selection rule. For chorus_gain_norm, the selection on F1 alone picked lr 0.03 in
{chose[('chorus_gain_norm', 'ungated', 0.03)]} of {n_picks[('chorus_gain_norm', 'ungated')]} folds,
and both of its collapsed refits came from those picks; the selection under the false-alarm budget
never did. Repairing it is a decision for goal 2 (§6).</li>
</ul></div>

<h2>1. What a collapse is</h2>
<p>The two fits of {ref_('problem', 'a collapsed fit on a held-out recording')} share the
configuration (lr 0.03, encoder 4 units wide and 6 layers deep, 1,800 steps) and the pair of folds
they trained on; they differ only in training seed, which sets the starting weights, the order of
the training crops and which 10 of the pair's recordings the fit trains on. The working one is the
only one of this configuration's {len(this_cfg)} second-draw inner fits that trained
({this_cfg_working} of {len(this_cfg)}). Its output rises at events and its threshold turns the rises
into calls. The collapsed fit's output is flat: any threshold below it gives the same single call,
and the threshold search keeps the first best value on its ascending list, the lowest,
{grid_floor:g} (a logit of {tr['fits']['collapsed']['threshold_logit']:.1f}). Every collapsed fit's
threshold sits there, as do {work_floor} working chorus_norm fits'.</p>

<h2>2. Which configurations collapse</h2>
<p>For chorus_norm the learning rate separates the configurations almost completely: every
configuration at lr 0.03 collapses in {min(cn_hi):.0%} to {max(cn_hi):.0%} of its fits, and below 0.03
collapse is rare ({ref_('rates', 'collapse by configuration')}).</p>
""" + fig("rates", fig_rates(rows),
          "<b>For chorus_norm, the top learning rate is where fits collapse.</b> Each mark is one "
          "configuration: the share of its 36 inner fits (3 training seeds × 6 pairs of folds × 2 "
          "draws) that collapsed. Rows: learning rate, with the collapsed count over the row beside "
          "it; the mark's shape is the encoder's shape; configurations with the same share are "
          "stacked. Panel A chorus_norm, panel B chorus_gain_norm. Hover a mark for its "
          "configuration.") + f"""
<p>Within lr 0.03 the encoder's shape shifts the share: the narrow, deep encoder (4 × 6) collapses
most ({tref('shape', 'collapse by shape')}). Training length is tangled with depth: at lr 0.03,
{'; '.join(f"{s:,} steps {pct(v)} ({of(v)})" for s, v in steps_hi.items())}, and the
{longest:,}-step configurations are all 6 layers deep. chorus_gain_norm follows shape more than the
learning rate: at lr 0.03 its 4 × 6 configurations collapse in
{pct(shape_lr[('chorus_gain_norm', 0.03, (4, 6))])} of fits and its other shapes in
{pct(gain_other)}, and at lr 0.01 its 4 × 6 configurations still collapse in
{pct(shape_lr[('chorus_gain_norm', 0.01, (4, 6))])}.</p>
""" + t_shape + f"""
<p><b>The configuration sets how often; within it, the draw decides which.</b> {both['chorus_norm']}
of chorus_norm's collapsed inner fits are the same fit (configuration, training seed and pair of
folds) in both draws. If every fit collapsed at chorus_norm's overall rate, about
{exp_flat['chorus_norm']:.0f} fits would overlap; at each configuration's own rate,
{exp_cfg['chorus_norm']:.1f} fits. The configuration accounts for the overlap and nothing is left for
the particular fit (chorus_gain_norm: {both['chorus_gain_norm']} fits observed,
{exp_cfg['chorus_gain_norm']:.1f} expected). Inside a draw the training seed does cluster with
collapse ({fmt_p(p_seed_draw['second'])} in the second draw, {fmt_p(p_seed_draw['first'])} in the
first; collapse labels shuffled within each configuration). Across draws the same seed builds the same
starting weights and crop order but trains on different recordings, and a seed that collapses more
than its configuration's others in one draw does not do so in the other (correlation {carry_r:.2f},
{fmt_p(carry_p)}). So the seed's effect cannot be put down to its starting weights; the recordings it
picks are at least as likely. No fold-pair effect was detected ({fmt_p(p_pair['chorus_norm'])} for
chorus_norm, {fmt_p(p_pair['chorus_gain_norm'])} for chorus_gain_norm). {len(twins)} pairs of
configurations differ only in step count; the shorter one's fits are the longer one's stopped early,
so they are left out of these tests.</p>

<h2>3. What it cost the comparison</h2>
<p>A configuration whose fits collapse scores badly in selection, and tuning picked no lr-0.03
configuration for chorus_norm under either rule ({tref('chose', 'what tuning chose')}). Whether the
collapse alone decided that was not tested: those configurations' working fits may have lost the
selection anyway. For chorus_gain_norm the selection on F1 alone did pick lr 0.03, in
{chose[('chorus_gain_norm', 'ungated', 0.03)]} of {n_picks[('chorus_gain_norm', 'ungated')]} folds, and
both of its collapsed refits came from those picks; the selection under the false-alarm budget never
picked lr 0.03. {len(ref_bad)} refits collapsed across both draws, {len([r for r in ref_bad if r['net'] == 'chorus_norm'])}
of chorus_norm's (second draw, lr 0.01) and {len([r for r in ref_bad if r['net'] == 'chorus_gain_norm'])}
of chorus_gain_norm's (lr 0.03, one per draw). They are the refits behind the † on those nets in the
<a href="../tuned_vs_coact/replicate1/report.html">replicate report</a>, which footnotes it as a refit
that "made one call per recording or called nothing on the held-out fold".</p>
<p>That report reads the {both['chorus_norm']} fits collapsed in both draws as the same fits failing
twice. The comparison in §2 shows that is what the configurations' rates alone predict: this page
corrects that reading.</p>
""" + t_chose + f"""

<h2>4. What a collapsed fit looks like inside</h2>
<p>chorus_norm passes each ROI's activity through a shared encoder, standardizes the encoder's
output over time, turns it into a vote per ROI (a number from 0 to 1 per frame), pools the votes into
three statistics (their mean, their spread across ROIs and the mean of the top m) and feeds those to a
head: 8 convolution layers of 8 channels each (kernel 3, dilation doubling from 1 to 128), each
followed by a Gaussian error linear unit (GELU; Hendrycks &amp; Gimpel 2016), then a linear output
layer. A GELU passes positive input and maps negative input to a small dip, no lower than −0.17, that
still carries a gradient. The head's size was never tuned. The nets are trained with Adam (Kingma
&amp; Ba 2015) at its default moment-decay rates (0.9 and 0.999); lr 0.03 is 30 times that paper's
suggested step size of 0.001.</p>
<p>Every second-draw fit of both nets was reloaded and run on one fresh simulated recording (quiet
background, simulation seed {census_doc['recording'].split(':')[1]}) that no fit trained on; call this
the <i>census</i>. Call a head layer <i>silent</i> when none of its 8 units' outputs varies (standard
deviation under {SILENT:g}), measured with {EDGE} frames trimmed from each end, where zero padding
makes even a constant layer wiggle. This is a test of variation, not of sign: a GELU's negative dip
carries signal without going positive, and a rule that asked only whether a unit ever went positive
counted {n_sign[('chorus_norm', False)]} working fit as dead. Every collapsed inner fit has a silent
layer ({n_silent[('chorus_norm', True)]} of {len(cz[('chorus_norm', True)])} chorus_norm,
{n_silent[('chorus_gain_norm', True)]} of {len(cz[('chorus_gain_norm', True)])} chorus_gain_norm) and
no working one does ({n_silent[('chorus_norm', False)]} of {len(cz[('chorus_norm', False)])} and
{n_silent[('chorus_gain_norm', False)]} of {len(cz[('chorus_gain_norm', False)])}); the second draw's
{len(ref_census_bad)} collapsed refits all have one ({sum(silent(e) for e in ref_census_bad)} of
{len(ref_census_bad)}). A silent layer passes nothing that changes, so the output is flat.</p>
""" + fig("census", fig_census(cen, sd_floor),
          f"<b>Every collapsed fit has a silent head layer and a flat output; no working fit has "
          f"either.</b> One dot per second-draw inner fit on the census recording, both measures "
          f"taken with {EDGE} frames trimmed from each end: the smallest share of units whose output "
          f"varies, over the head's 8 layers (it takes only the values 0, 1/8, …, 1; dots are "
          f"spread ±0.02 sideways so they can be seen), against the standard deviation (SD) of the "
          f"output logit. {floored['chorus_norm']} chorus_norm and {floored['chorus_gain_norm']} "
          f"chorus_gain_norm fits have an output SD below the floor and are drawn hollow on it. "
          f"{sw('c1')}working, {sw('c2')}collapsed.") + f"""
<p>The earlier diagnosis of plain chorus (pull request 596) asked whether the votes respond at all:
in an otherwise empty window of 32 ROIs and 4,096 frames, how far does one onset move any vote? Its
answer for plain chorus was at most 0.0003, and the test gives the same here for untrained plain
chorus ({', '.join(f'{v:.4f}' for v in plain)}), so it can fail. Most collapsed chorus_norm fits pass
it: one onset moves a vote by a median of {med(cz[('chorus_norm', True)], 'onset_response'):.2f},
against {med(cz[('chorus_norm', False)], 'onset_response'):.2f} in working fits and
{min(untrained):.2f} to {max(untrained):.2f} in this configuration untrained. For them the votes still
respond and the head does not pass the response on. {as_deaf[('chorus_norm', True)]} of the
{len(cz[('chorus_norm', True)])} collapsed chorus_norm fits and
{as_deaf[('chorus_gain_norm', True)]} of the {len(cz[('chorus_gain_norm', True)])} collapsed
chorus_gain_norm fits are as deaf as plain chorus; for those the votes stopped responding too
({ref_('onset', 'the earlier diagnosis’s test')}).</p>
""" + fig("onset", fig_onset(
            [("plain chorus, untrained", plain, "var(--ink-2)"),
             ("chorus_norm, untrained", untrained, "var(--ink-2)"),
             ("chorus_norm, working", onset[("chorus_norm", False)], "var(--c1)"),
             ("chorus_norm, collapsed", onset[("chorus_norm", True)], "var(--c2)"),
             ("chorus_gain_norm, working", onset[("chorus_gain_norm", False)], "var(--c1)"),
             ("chorus_gain_norm, collapsed", onset[("chorus_gain_norm", True)], "var(--c2)")], 1e-5),
          "<b>Most collapsed chorus_norm fits' votes still respond to an event; plain chorus's "
          "never did.</b> For each net or fit, the largest change in any ROI's vote when one onset is "
          "added to an otherwise empty window of 32 ROIs and 4,096 frames, the earlier diagnosis's "
          "test. Rows: untrained plain chorus and untrained chorus_norm (3 starting seeds each, the "
          "second in Figure 1's configuration), then every second-draw inner fit; the count is in "
          "brackets. Changes below 10⁻⁵ are drawn hollow on the floor. "
          f"{sw('c1')}working, {sw('c2')}collapsed; gray, untrained.") + f"""

<h2>5. When it happens, and what prevents it</h2>
<p>Both fits of {ref_('problem', 'a collapsed fit on a held-out recording')} were replayed exactly as
the draw trained them, and each replay reproduced its saved checkpoint to the last bit. Every one of
the {len(reps)} replays starts with a flat output (standard deviation {min(first_sd):.4f} to
{max(first_sd):.4f} logits on the first batch), and in every one the head starts mostly silent: at the
starting weights, {min(start_silent)} to {max(start_silent)} of its 8 layers pass nothing that varies
over the training batch (measured every tenth batch, crops' ends trimmed). Training has to wake the
head. The working fit's is awake, with no silent layer, by step {work_wake}, and its loss falls below
1.0 by step {escape}. The collapsed fit's never is: even at its most awake {ref_least} of its layers are silent; it
ends with {end_silent}, and its loss never leaves its starting level
({ref_('training', 'the loss and the silent head')}).</p>
""" + fig("training", fig_onset_in_training({"the working fit, as run": (work_fit, "var(--c1)"),
                                             "the collapsed fit, as run": (ref, "var(--c2)")}),
          "<b>Both heads start mostly silent; the working fit's wakes and the collapsed fit's never "
          "does.</b> The "
          "two as-run replays of the fits in Figure 1. Panel A: how many of the head's 8 layers have "
          f"no unit whose output varies over the training batch (standard deviation under "
          f"{SILENT:g}, {EDGE} frames trimmed from each crop's ends), logged every 10 steps. Panel B: "
          "training loss (binary cross-entropy weighted toward event frames), the mean of 5 logged "
          "steps. The batch is 3 training crops of 4,096 frames, not the census recording.") + f"""
<p><b>Settled early, mostly.</b> The configurations that differ only in step count show when a
collapse is decided. Of the collapsed fits of the longer twins, {early['chorus_norm']} of
{early['chorus_norm'] + late['chorus_norm']} in chorus_norm were already collapsed where the shorter
twin stopped, and {late['chorus_norm']} came later; {recovered['chorus_norm']} recovered with more
steps. In chorus_gain_norm, {early['chorus_gain_norm']} early, {late['chorus_gain_norm']} later and
{recovered['chorus_gain_norm']} recovered.</p>
<p>The collapsed fit was then replayed with one thing changed and the same starting weights and
training crops ({ref_('curves', 'one change at a time')}). It trains at lr 0.003 and at lr 0.01, which
change the learning rate for the whole run, and at lr 0.03 when the learning rate is ramped up
linearly over the first 200 steps, which changes only the start; with that ramp its head is awake by
step {wu200_wake}. A 50-step ramp is not enough, and it shows that a head can wake and die again: it
is awake by step {wu50_wake}, has a silent layer again from step {wu50_back} and ends with
{wu50_end} silent, while its loss retraces the fit as run.</p>
""" + fig("curves", fig_curves({
            "the collapsed fit, as run (lr 0.03)": (ref, "var(--c2)", False),
            "replayed at lr 0.003": (cf[(0.003, 0)], "var(--c3)", False),
            "replayed at lr 0.01": (cf[(0.01, 0)], "var(--c4)", False),
            "replayed at lr 0.03, 200-step warm-up": (cf[(0.03, 200)], "var(--c5)", True),
            "replayed at lr 0.03, 50-step warm-up": (cf[(0.03, 50)], "var(--ink-2)", True)}, smooth),
          "<b>The same fit trains at a lower learning rate, or at the top one with a slower "
          "start.</b> Training loss, the mean of 5 logged steps, logged every 10. Dashed: a linear "
          "warm-up at lr 0.03.") + f"""
<p>The 200-step warm-up was then tried on {len(wu)} more collapsed fits, one from each of
{len(wu_cfgs)} lr-0.03 configurations, {len(own_cfg)} of them Figure 1's own configuration at another
seed ({ref_('warmup', 'warm-up on other fits')}; {tref('warmup', 'fit by fit')}). They were picked by
hand, not at random: of the {len(omitted)} lr-0.03 configurations left out, {len(low_left)} collapse
least of all and {len(twin_left)} {'is the shorter twin' if len(twin_left) == 1 else 'are shorter twins'}
of one that was tried. Two of the fits are one training run counted twice; counted once, training loss
fell below 0.5 in {wu_ok} of {len(dist)} distinct runs.{fail_note} A replay with nothing changed reproduces the
collapse, so doing nothing trains none of them; a change that merely re-drew each fit's luck would
train each as often as its configuration's fits train, {reroll:.1f} of {len(dist)}. These runs were
judged by training loss, not by calls on held-out recordings.</p>
""" + fig("warmup", fig_warmup(wu, trains, smooth),
          "<b>A 200-step linear warm-up at lr 0.03 lets most of the collapsed fits tried train.</b> "
          "Training loss, the mean of 5 logged steps, for each collapsed fit in Table 3, replayed with "
          "the warm-up. Dashed: loss 0.5, the line this page uses between training and not. "
          f"The highest single logged loss, {spike:.1f}, is in an early spike the smoothing shortens.")
    body += t_wu + f"""
<p><b>Related work.</b> Dead ReLU units, which output zero for every input, have been measured to grow
with the learning rate (Gulcehre et al. 2022, in offline reinforcement learning), and Sokar et al.
(2023) call a unit dormant when its mean absolute activation, relative to its layer's, falls below a
threshold. This page thresholds variation instead, and here every head starts mostly silent, working or not:
what fails is training's waking it, so these are related observations, not this mechanism. A
learning-rate
warm-up is the standard remedy for unstable early training at a large step size (He et al. 2016;
Goyal et al. 2017); why it helps Adam is disputed (Liu et al. 2020; Ma &amp; Yarats 2021), and Ma &amp;
Yarats's rule of thumb, 2/(1 − 0.999) = 2,000 steps, is ten times the ramp tried here. That it
prevents this collapse is this page's result.</p>

<h2>6. The choice it leaves</h2>
<ul>
<li><b>A repair is a decision for goal 2, not this page's.</b> Three are open. Drop lr 0.03 from
chorus_norm's grid, which matches what tuning picked anyway (for chorus_gain_norm it would change what
the selection on F1 alone picked). Add a linear learning-rate warm-up to training, which changes every
net, since they share one trainer; 200 steps was tried here. Or change the head, which was never tuned
and was not tried. Each changes chorus_norm's numbers in goal 2 and needs both draws run again to
compare.</li>
<li><b>A fourth, which catches rather than prevents.</b> Measured away from the ends, the output's
standard deviation on the census recording separates the groups without overlap, in both nets and in
the refits: at most {sd_coll_max:.2g} logits in every collapsed fit, at least {sd_work_min:.2f} in
every working one. A check at the end of training could flag a fit whose held-out output does not
vary. In a fair comparison a flagged fit must still count, as a failure or as a retraining charged to
the net; dropping it would select on the outcome. The gap was found on one recording and one draw.</li>
</ul>

<h2>7. Limits</h2>
<ul>
<li>Simulated recordings only. The census and the replays use the second draw's fits; the collapse
counts use both draws.</li>
<li>The census runs each fit on one fresh recording; its separations were not tested on others.</li>
<li>The two as-run replays reproduced their checkpoints exactly. The counterfactual replays are the
same code with one change and have no checkpoint to match; they are judged by training loss, not by
calls on held-out recordings.</li>
<li>The warm-up was tried on {len(dist) + 1} distinct collapsed runs of chorus_norm, chosen by hand,
and on no chorus_gain_norm fit. That a collapsed fit's head is never woken rests on the one collapsed
fit replayed as run and on the step-count twins. "Silent" uses an absolute threshold (standard
deviation 0.001), and at the starting weights a layer's outputs are small, so some of the starting
silence may be scale rather than a layer that passes nothing.</li>
<li>The seed's effect inside a draw is measured, not explained. Why some collapsed fits' votes also
stop responding, most of all in chorus_gain_norm, is not established here.</li>
</ul>

<h2>8. Where everything is</h2>
<ul>
<li>This page and its data (<code>collapse_table.json</code>, <code>selections.json</code>,
<code>census.json</code>, <code>trace.json</code>, <code>replays/</code>):
<code>docs/learned/chorus_collapse/</code> in the repository, where a test rebuilds the page from them,
and <code>&lt;darkroom&gt;/bugarach/{FOLDER}/</code>.</li>
<li>The tool: <code>tools/diagnose_chorus_collapse.py</code>. It needs a checkout that registers the
chorus nets (branch <code>replicate-run</code>), passed as <code>--code</code>; its
<code>replay</code> re-runs a second-draw chorus_norm inner fit on the GPU.</li>
<li>The reports it builds on: the replicate report, <code>docs/learned/tuned_vs_coact/replicate1/</code>,
and the fair-comparison report, which declares the tuning grid,
<a href="../tuned_vs_coact/fair_comparison_2026_09_18/report.html"><code>docs/learned/tuned_vs_coact/fair_comparison_2026_09_18/</code></a>.</li>
<li>The runs it reads: <code>&lt;darkroom&gt;/bugarach/{R.THEIRS_FOLDER}/results/</code> (first draw)
and <code>&lt;darkroom&gt;/bugarach/{R.MINE_FOLDER}/results/</code> (second draw).</li>
<li>The earlier diagnosis of plain chorus: pull request 596 (open as of 2026-09-19), with
<code>docs/learned/field_size_candidates/why_chorus.txt</code> and that folder's README, section
"Repairing chorus", at commit {DIAGNOSIS_596} on branch <code>replicate-run</code>. It tested plain
chorus at lr 0.01 and 0.001.</li>
</ul>
<p><b>References</b></p>
<ul class="refs">
<li>Goyal P. et al. (2017). Accurate, large minibatch SGD: training ImageNet in 1 hour.
arXiv:1706.02677.</li>
<li>Gulcehre C. et al. (2022). An empirical study of implicit regularization in deep offline RL.
TMLR; arXiv:2207.02099.</li>
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
    title = "Why a third of chorus_norm's tuning fits do not train"
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
        (work / "selections.json").write_text(json.dumps(selections()))
        print(f"{len(rows)} fits, {sum(r['collapsed'] for r in rows)} collapsed")
    elif a.cmd == "census":
        rows = json.loads((work / "collapse_table.json").read_text())
        cen = census(rows)
        (work / "census.json").write_text(json.dumps(cen))
        print(f"{len(cen['fits'])} fits probed")
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
