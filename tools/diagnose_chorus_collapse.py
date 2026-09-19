#!/usr/bin/env python3
"""Why a third of chorus_norm's fits make one call per recording: the diagnosis, from the runs' own fits.

    python tools/diagnose_chorus_collapse.py table   --code <checkout>          # collapse vs configuration
    python tools/diagnose_chorus_collapse.py census  --code <checkout>          # what a collapsed fit is
    python tools/diagnose_chorus_collapse.py replay  --code <checkout> CFG SEED RECS [--lr X] [--warmup N]
    python tools/diagnose_chorus_collapse.py page    [--also docs/learned/chorus_collapse/index.html]

The replicate report (docs/learned/tuned_vs_coact/replicate1/) found that in both draws of goal 2's
comparison about a third of chorus_norm's inner fits made exactly one call per recording, F1 0.125,
and that most of those are the same fit in both draws. This tool answers why, reading nothing but the
two runs' result folders in the darkroom:

- ``table`` joins every fit's collapse status (the report's Table 2 rule: exactly one call on every
  recording of every fold it was scored on, at its own threshold) to its role and configuration.
- ``census`` reloads every second-draw chorus fit and runs it on one bench recording, recording for
  each whether its head (the stack that maps the pooled per-cell statistics to the output) has a
  layer whose units are all switched off, and how much its output varies.
- ``replay`` re-runs one inner fit exactly as ``bugarach.learn.train.train`` ran it — same seed,
  same recordings in the same order, same crops, on the GPU with deterministic kernels — logging the
  loss and each head layer's live units every 10 steps, and checks the result against the saved
  checkpoint tensor by tensor. ``--lr`` and ``--warmup`` turn it into a counterfactual: the same fit
  with only that changed. Nothing the runs wrote is modified.
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
PROBE_RECORDING = ("baseline_quiet", 2000)      # one bench recording; the census input for every fit
DEAD = 1e-3                                     # a GELU output above this counts as switched on


def _results(draw: str) -> Path:
    from bugarach.paths import darkroom
    return Path(darkroom(DRAW_DIRS[draw], "results"))


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

def _probe_input():
    import numpy as np
    import torch

    from bugarach.bench import make_recording
    from bugarach.learn.encode import encode
    slice_, _ = make_recording(*PROBE_RECORDING)
    return torch.from_numpy(np.asarray(encode(slice_, dt=0.1).raster, dtype=np.float32)).unsqueeze(0)


def _load_fit(zf, tmp: Path, net: str, cfg: str, seed: int, recs: str):
    from bugarach.learn import checkpoint
    name = f"fits/{net}/{cfg}/seed{seed}__recs-{recs}.json"
    p = tmp / name.replace("/", "__")
    if not p.exists():
        p.write_bytes(zf.read(name))
    return checkpoint.load(p)


def census(rows: list[dict], work: Path) -> list[dict]:
    """Every second-draw chorus fit, inner fits and refits, on one bench recording of that draw: the
    smallest share of live units in any head layer, and the spread of the output logit over it."""
    import zipfile

    import torch
    x = _probe_input()
    zf = zipfile.ZipFile(_results("second") / "fits.zip")
    tmp = work / "checkpoints"
    tmp.mkdir(parents=True, exist_ok=True)
    out = []
    for r in rows:
        if r["draw"] != "second":
            continue
        m = _load_fit(zf, tmp, r["net"], r["cfg"], r["seed"], r["recs"]).model.cpu().eval()
        alive = []
        hooks = [g.register_forward_hook(lambda mod, i, o: alive.append(
            float((o[0] > DEAD).any(dim=1).float().mean()))) for g in m.head
            if isinstance(g, torch.nn.GELU)]
        with torch.no_grad():
            logit = m(x)[0]
        for h in hooks:
            h.remove()
        entry = dict(net=r["net"], cfg=r["cfg"], seed=r["seed"], recs=r["recs"], role=r["role"],
                     lr=r["lr"],
                     collapsed=r["collapsed"], min_head_alive=min(alive),
                     logit_sd=float(logit.std()))
        if r["net"] == "chorus_gain_norm":
            # how far training moved the vote gain, as a fraction of where it started
            entry["vote_gain_moved"] = float((m.vote_gain.detach() / r["vote_gain"] - 1).abs().max())
        out.append(entry)
        (tmp / f"fits__{r['net']}__{r['cfg']}__seed{r['seed']}__recs-{r['recs']}.json").unlink()
    return out


# ---- replay ------------------------------------------------------------------------------------

def replay(cfg_key: str, seed: int, recs_hash: str, *, lr: float | None, warmup: int,
           work: Path, net: str = "chorus_norm") -> dict:
    """One inner fit re-run exactly as `train.train` ran it (see the module docstring)."""
    import zipfile

    import numpy as np
    import torch

    from bugarach.bench import make_recording
    from bugarach.learn import train as T
    from bugarach.learn.nets import ARCHITECTURES

    res = _results("second")
    zf = zipfile.ZipFile(res / "fits.zip")
    stem = f"fits/{net}/{cfg_key}/seed{seed}__recs-{recs_hash}"
    run = json.loads(zf.read(stem + ".run.json"))
    conf = json.loads((res / "configs" / net / f"{cfg_key}.json").read_text())
    tr = conf["training"]
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
    alive = {}
    hooks = [g.register_forward_hook(lambda mod, i, o, k=k: alive.__setitem__(
        k, float((o > DEAD).any(dim=2).any(dim=0).float().mean()))) for k, g in enumerate(gelus)]
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
        if warmup:
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
                            head_alive=[alive[k] for k in range(len(gelus))]))
    for h in hooks:
        h.remove()
    doc = dict(net=net, cfg=cfg_key, seed=seed, recs=recs_hash, lr=base_lr, warmup=warmup,
               as_run=(lr is None and not warmup), config_lr=float(tr["lr"]), steps=steps, log=log)
    if doc["as_run"]:
        # the replay must BE the run's fit: every tensor against the saved checkpoint
        tmp = work / "checkpoints"
        tmp.mkdir(parents=True, exist_ok=True)
        saved = _load_fit(zf, tmp, net, cfg_key, seed, recs_hash).model.state_dict()
        mine = model.state_dict()
        doc["max_abs_diff_vs_checkpoint"] = max(
            float((mine[k].cpu() - saved[k].cpu()).abs().max()) for k in mine)
    return doc


# ---- page --------------------------------------------------------------------------------------

LRS = (0.003, 0.01, 0.03)                      # the learning rates the tuning grid declared


def fig_rates(rows: list[dict]) -> str:
    """Share of each configuration's inner fits that collapsed, both draws pooled, by learning rate."""
    left, top, rh, pw, gap = 120, 34, 30, 360, 60
    w = left + 2 * pw + gap + 30
    h = top + rh * 3 + 70
    svg = R.Svg(w, h, "collapse share by configuration and learning rate")
    for j, net in enumerate(CHORUS):
        x0 = left + j * (pw + gap)
        sx = R.x_axis(svg, x0, x0 + pw, top + rh * 3 + 4, 0, 1, (0, 0.25, 0.5, 0.75, 1.0),
                      "share of the configuration's 36 inner fits that collapsed", fmt="{:.2f}")
        svg.text(x0, top - 14, f"{'A' if j == 0 else 'B'} · {net}", size=12, weight="bold")
        for i, lr in enumerate(LRS):
            y = top + i * rh + rh / 2
            if j == 0:
                svg.text(left - 12, y + 4, f"lr {lr:g}", anchor="end", size=12)
            if i % 2:
                svg.rect(x0, y - rh / 2 + 2, pw, rh - 4, fill="var(--band)")
            per = defaultdict(lambda: [0, 0])
            for r in rows:
                if r["net"] == net and r["lr"] == lr:
                    per[r["cfg"]][0] += r["collapsed"]
                    per[r["cfg"]][1] += 1
            for k, (c, n) in sorted(per.items()):
                svg.circle(sx(c / n), y, 5, fill="var(--c1)", stroke="none", opacity=0.75,
                           title=f"{net}, configuration {k[:8]}, lr {lr:g}: {c} of {n} fits collapsed")
    return svg.render()


def fig_census(cen: list[dict]) -> str:
    """Each second-draw fit: the smallest live share of any head layer against its output's spread."""
    left, top, ph, pw, gap = 70, 30, 260, 380, 60
    w = left + 2 * pw + gap + 30
    h = top + ph + 90
    svg = R.Svg(w, h, "dead head layers and flat outputs")
    lo, hi = -3, 2                                   # log10 of the logit's spread
    for j, net in enumerate(CHORUS):
        x0 = left + j * (pw + gap)
        sx = R.x_axis(svg, x0, x0 + pw, top + ph + 4, 0, 1, (0, 0.25, 0.5, 0.75, 1.0),
                      "smallest share of live units in any head layer", fmt="{:.2f}")
        sy = lambda v: top + ph - (v - lo) / (hi - lo) * ph
        for t in range(lo, hi + 1):
            svg.line(x0, sy(t), x0 + pw, sy(t), stroke="var(--rule)")
            if j == 0:
                svg.text(x0 - 8, sy(t) + 4, f"10{'⁻' if t < 0 else ''}{'⁰¹²³'[abs(t)]}", size=12,
                         anchor="end", fill="var(--ink-2)")
        svg.text(x0, top - 12, f"{'A' if j == 0 else 'B'} · {net}", size=12, weight="bold")
        rnd = random.Random(1)
        for e in cen:
            if e["net"] != net:
                continue
            xj = e["min_head_alive"] + rnd.uniform(-0.02, 0.02)
            v = math.log10(max(e["logit_sd"], 10 ** lo))
            svg.circle(sx(min(1, max(0, xj))), sy(v), 3, stroke="none", opacity=0.55,
                       fill="var(--c2)" if e["collapsed"] else "var(--c1)",
                       title=f"{net} {e['cfg'][:8]} seed {e['seed']}: "
                             f"{'collapsed' if e['collapsed'] else 'working'}, smallest live share "
                             f"{e['min_head_alive']:.2f}, output spread {e['logit_sd']:.4f}")
    svg.add(f'<text x="0" y="0" font-size="12" text-anchor="middle" fill="var(--ink-2)" '
            f'transform="translate(16,{top + ph / 2:.1f}) rotate(-90)">spread of the output logit '
            f'(log scale)</text>')
    ly = h - 14
    for k, (col, words) in enumerate((("var(--c2)", "collapsed"), ("var(--c1)", "working"))):
        svg.circle(left + 8 + k * 140, ly - 4, 5, fill=col, stroke="none")
        svg.text(left + 18 + k * 140, ly, words, size=12)
    return svg.render()


def fig_curves(reps: dict[str, dict]) -> str:
    """Loss over training for one collapsed fit as run, the working fit of the same configuration,
    and the collapsed fit replayed with only its learning rate or warm-up changed."""
    left, top, ph, pw = 70, 24, 300, 720
    w, h = left + pw + 20, top + ph + 70 + 22 * math.ceil(len(reps) / 2)
    svg = R.Svg(w, h, "training loss, replayed")
    steps = max(e["step"] for d in reps.values() for e in d["log"])
    sx = R.x_axis(svg, left, left + pw, top + ph + 4, 0, steps,
                  [s for s in range(0, steps + 1, 300)], "training step", fmt="{:.0f}")
    lo, hi = 0.0, 2.0
    sy = lambda v: top + ph - (min(hi, max(lo, v)) - lo) / (hi - lo) * ph
    for t in (0.0, 0.5, 1.0, 1.5, 2.0):
        svg.line(left, sy(t), left + pw, sy(t), stroke="var(--rule)")
        svg.text(left - 8, sy(t) + 4, f"{t:.1f}", size=12, anchor="end", fill="var(--ink-2)")
    svg.add(f'<text x="0" y="0" font-size="12" text-anchor="middle" fill="var(--ink-2)" '
            f'transform="translate(18,{top + ph / 2:.1f}) rotate(-90)">training loss (mean of 5 '
            f'logged steps)</text>')
    # A warm-up replay is dashed (identity is never color alone), and the collapsed fit as run is
    # drawn last: the 50-step warm-up retraces it almost exactly and would otherwise hide it.
    dashed = lambda label: "warm-up" in label
    order = sorted(enumerate(reps.items()), key=lambda kv: "as run" in kv[1][0])
    for k, (label, d) in order:
        col = f"var(--c{k + 1})"
        dash = ' stroke-dasharray="7 4"' if dashed(label) else ""
        pts = []
        L = d["log"]
        for i in range(len(L)):
            win = L[max(0, i - 4):i + 1]
            pts.append((sx(L[i]["step"]), sy(st.mean(e["loss"] for e in win))))
        svg.add(f'<polyline fill="none" stroke="{col}" stroke-width="2"{dash} points="'
                + " ".join(f"{a:.1f},{b:.1f}" for a, b in pts) + f'"><{R.SVG_TITLE}>{R.esc(label)}'
                f'</{R.SVG_TITLE}></polyline>')
        # the key, below the axis: two columns, a line swatch beside each name
        kx, ky = left + (k % 2) * (pw / 2), top + ph + 62 + 22 * (k // 2)
        svg.line(kx, ky - 4, kx + 22, ky - 4, stroke=col, width=3,
                 dash="7 4" if dashed(label) else None)
        svg.text(kx + 30, ky, label, size=12)
    return svg.render()


def fig_dead(pair: dict[str, tuple[dict, str]]) -> str:
    """How many of the head's 8 layers are dead on the training batch, over the replayed training."""
    left, top, ph, pw = 70, 24, 150, 720
    w, h = left + pw + 20, top + ph + 70 + 22
    svg = R.Svg(w, h, "dead head layers during training")
    steps = max(e["step"] for d, _ in pair.values() for e in d["log"])
    sx = R.x_axis(svg, left, left + pw, top + ph + 4, 0, steps,
                  [s for s in range(0, steps + 1, 300)], "training step", fmt="{:.0f}")
    n = max(len(e["head_alive"]) for d, _ in pair.values() for e in d["log"])
    sy = lambda v: top + ph - v / n * ph
    for t in range(0, n + 1, 2):
        svg.line(left, sy(t), left + pw, sy(t), stroke="var(--rule)")
        svg.text(left - 8, sy(t) + 4, str(t), size=12, anchor="end", fill="var(--ink-2)")
    svg.add(f'<text x="0" y="0" font-size="12" text-anchor="middle" fill="var(--ink-2)" '
            f'transform="translate(18,{top + ph / 2:.1f}) rotate(-90)">dead head layers</text>')
    for k, (label, (d, col)) in enumerate(pair.items()):
        pts = " ".join(f"{sx(e['step']):.1f},{sy(sum(a == 0 for a in e['head_alive'])):.1f}"
                       for e in d["log"])
        svg.add(f'<polyline fill="none" stroke="{col}" stroke-width="2" points="{pts}">'
                f'<{R.SVG_TITLE}>{R.esc(label)}</{R.SVG_TITLE}></polyline>')
        kx, ky = left + k * (pw / 2), top + ph + 62
        svg.line(kx, ky - 4, kx + 22, ky - 4, stroke=col, width=3)
        svg.text(kx + 30, ky, label, size=12)
    return svg.render()


# Slots 1-6 of the reference categorical palette, in its validated order: adjacent pairs pass the
# color-vision checks in both modes (Figure 3's lines), and the first three pass all pairs (the dot
# plots, which use no more than three).
CSS_EXTRA = """
:root{--c1:#2a78d6;--c2:#eb6834;--c3:#1baf7a;--c4:#eda100;--c5:#e87ba4;--c6:#008300}
@media (prefers-color-scheme: dark){:root:not([data-theme="light"]){--c1:#3987e5;--c2:#d95926;
--c3:#199e70;--c4:#c98500;--c5:#d55181;--c6:#008300}}
:root[data-theme="dark"]{--c1:#3987e5;--c2:#d95926;--c3:#199e70;--c4:#c98500;--c5:#d55181;--c6:#008300}
"""


def page(work: Path) -> str:
    table = json.loads((work / "collapse_table.json").read_text())
    rows = [r for r in table if r["role"] == "inner"]
    refits = [r for r in table if r["role"] != "inner"]
    census_all = json.loads((work / "census.json").read_text())
    cen = [e for e in census_all if e["role"] == "inner"]
    reps = {p.stem: json.loads(p.read_text()) for p in sorted((work / "replays").glob("*.json"))}

    def rate(net, pred, rs=rows):
        rs = [r for r in rs if r["net"] == net and pred(r)]
        return sum(r["collapsed"] for r in rs), len(rs)

    pct = lambda cn: f"{cn[0] / cn[1]:.0%}"
    # nothing but the learning rate: training seed and fold pair, over all of chorus_norm's inner fits
    by_seed = {s: rate("chorus_norm", lambda r, s=s: r["seed"] == s) for s in (0, 1, 2)}
    pairs = sorted({tuple(r["pair"]) for r in rows})
    by_pair = [rate("chorus_norm", lambda r, p=p: tuple(r["pair"]) == p) for p in pairs]
    # within lr 0.03: the per-cell encoder's width and depth
    hi = lambda **kw: rate("chorus_norm", lambda r: r["lr"] == 0.03
                           and all(r[k] == v for k, v in kw.items()))
    widths = sorted({r["width"] for r in rows})
    depths = sorted({r["depth"] for r in rows})
    by_w = {v: hi(width=v) for v in widths}
    by_d = {v: hi(depth=v) for v in depths}
    # what tuning chose: the refits, their learning rates, and which of them collapsed
    ref_lr = {(n, lr): rate(n, lambda r, lr=lr: r["lr"] == lr, refits) for n in CHORUS
              for lr in LRS}
    ref_bad = [r for r in refits if r["collapsed"]]
    cen_ref_bad = [e for e in census_all if e["role"] != "inner" and any(
        (e["net"], e["cfg"], e["seed"], e["recs"]) == (r["net"], r["cfg"], r["seed"], r["recs"])
        for r in ref_bad)]
    low_bad = [e for e in cen if e["collapsed"] and e["lr"] < 0.03]

    per_draw = {(n, d): rate(n, lambda r, d=d: r["draw"] == d) for n in CHORUS for d in DRAW_DIRS}
    by_lr = {(n, lr): rate(n, lambda r, lr=lr: r["lr"] == lr) for n in CHORUS for lr in LRS}
    # the same fit (configuration, training seed, pair of folds) in both draws
    keyset = lambda d, n: {(r["cfg"], r["seed"], tuple(r["pair"])) for r in rows
                           if r["draw"] == d and r["net"] == n and r["collapsed"]}
    both = {n: len(keyset("first", n) & keyset("second", n)) for n in CHORUS}
    per_cfg = defaultdict(lambda: [0, 0])
    for r in rows:
        per_cfg[(r["net"], r["cfg"], r["lr"])][0] += r["collapsed"]
        per_cfg[(r["net"], r["cfg"], r["lr"])][1] += 1
    cn_hi = [c / n for (net, _, lr), (c, n) in per_cfg.items() if net == "chorus_norm" and lr == 0.03]
    cn_lo = sum(c for (net, _, lr), (c, n) in per_cfg.items() if net == "chorus_norm" and lr < 0.03)
    cn_lo_n = sum(n for (net, _, lr), (c, n) in per_cfg.items() if net == "chorus_norm" and lr < 0.03)
    # the census claims
    cz = {(net, col): [e for e in cen if e["net"] == net and e["collapsed"] == col]
          for net in CHORUS for col in (True, False)}
    dead = {k: sum(e["min_head_alive"] == 0 for e in v) for k, v in cz.items()}
    # the exceptions, named rather than rounded away
    odd_work = [e for e in cz[("chorus_norm", False)] if e["min_head_alive"] == 0]
    odd_coll = [e for e in cz[("chorus_norm", True)] if e["min_head_alive"] > 0]
    assert dead[("chorus_norm", True)] >= 0.95 * len(cz[("chorus_norm", True)]) and len(odd_work) <= 3
    cgn_rest = [e for e in cz[("chorus_gain_norm", True)] if e["min_head_alive"] > 0]
    cgn_work = cz[("chorus_gain_norm", False)]
    sd_coll_max = max(e["logit_sd"] for e in census_all if e["collapsed"])
    sd_work_min = min(e["logit_sd"] for e in census_all if not e["collapsed"])
    assert sd_coll_max < sd_work_min, "the output's spread separates collapsed from working fits"
    odd_text = ""
    if odd_work:
        sds = ", ".join(f"{e['logit_sd']:.1f}" for e in odd_work)
        odd_text += (f"The working fit{'s' if len(odd_work) > 1 else ''} with a dead layer still "
                     f"var{'y' if len(odd_work) > 1 else 'ies'} (output spread {sds}), carried by "
                     f"that residue. ")
    if odd_coll:
        lrs = ", ".join(f"lr {e['lr']:g}" for e in odd_coll)
        flat = ", ".join(f"{e['logit_sd']:.3f}" for e in odd_coll)
        odd_text += (f"The collapsed fit{'s' if len(odd_coll) > 1 else ''} without one ({lrs}) "
                     f"{'have' if len(odd_coll) > 1 else 'has'} the same flat output (spread {flat}).")
    med_sd = {k: st.median(e["logit_sd"] for e in v) for k, v in cz.items()}
    # the replays
    as_run = [d for d in reps.values() if d["as_run"]]
    assert all(d["max_abs_diff_vs_checkpoint"] == 0.0 for d in as_run), \
        "every as-run replay reproduces its checkpoint exactly"
    final = lambda d: st.mean(e["loss"] for e in d["log"][-5:])
    trains = lambda d: final(d) < 0.5
    ref = next(d for d in as_run if not trains(d))          # the collapsed fit replayed
    ref_id = (ref["cfg"], ref["seed"], ref["recs"])
    cf = {(d["lr"], d["warmup"]): d for d in reps.values()
          if (d["cfg"], d["seed"], d["recs"]) == ref_id and not d["as_run"]}
    wu = [d for d in reps.values() if d["warmup"] == 200 and d["lr"] == 0.03
          and (d["cfg"], d["seed"], d["recs"]) != ref_id]
    wu_ok = sum(trains(d) for d in wu)
    wu_cfgs = {d["cfg"] for d in wu}
    wu_fail = [d for d in wu if not trains(d)]
    first_dead = next(e["step"] for e in ref["log"] if 0.0 in e["head_alive"])
    work_fit = next(d for d in as_run if trains(d))
    assert work_fit["cfg"] == ref["cfg"], "the working replay is the same configuration"
    assert trains(cf[(0.01, 0)]) and trains(cf[(0.003, 0)]) and trains(cf[(0.03, 200)]) \
        and not trains(cf[(0.03, 50)]), "the counterfactuals come out as the page says"
    assert min(cn_hi) >= 0.4 and cn_lo / cn_lo_n < 0.02
    assert ref_lr[("chorus_norm", 0.03)][1] == 0, "tuning never chose a lr-0.03 chorus_norm config"
    assert len(cen_ref_bad) == sum(r["draw"] == "second" for r in ref_bad)

    # colors follow Figure 2: working slot 1, collapsed slot 2
    curves = {"same configuration, the working fit": work_fit,
              "collapsed fit, as run (lr 0.03)": ref,
              "collapsed fit at lr 0.01": cf[(0.01, 0)],
              "collapsed fit at lr 0.003": cf[(0.003, 0)],
              "collapsed fit, lr 0.03, warm-up 200": cf[(0.03, 200)],
              "collapsed fit, lr 0.03, warm-up 50": cf[(0.03, 50)]}
    sw = lambda v: f'<span class="sw" style="background:var(--{v})"></span>'

    t1 = "".join(f"<tr><td>{net}</td>" + "".join(
        f"<td>{by_lr[(net, lr)][0]} of {by_lr[(net, lr)][1]} fits</td>" for lr in LRS)
        + "".join(f"<td>{per_draw[(net, d)][0]} of {per_draw[(net, d)][1]} fits</td>"
                  for d in DRAW_DIRS) + f"<td>{both[net]} fits</td></tr>" for net in CHORUS)
    t2 = "".join(
        f"<tr><td style='text-align:left'>{d['cfg'][:8]}, training seed {d['seed']}</td>"
        f"<td>{final(d):.2f}</td><td>{'trains' if trains(d) else 'still collapses'}</td></tr>"
        for d in sorted(wu, key=lambda d: d["cfg"]))
    F = {"rates": 1, "census": 2, "curves": 3, "dead": 4}
    ref_ = lambda k, words: f'<a href="#fig-{k}">Figure {F[k]}, {words}</a>'
    fig = lambda k, body, cap: (f'<figure id="fig-{k}"><div class="scrollhint">Scroll sideways to '
                                f'see the whole figure.</div>{body}<figcaption><b>Figure {F[k]}.</b> '
                                f'{cap}</figcaption></figure>')
    body = f"""
<h1>Why a third of chorus_norm's fits do not train</h1>
<p class="sub">A diagnosis from the fits of goal 2's two draws, reloaded and replayed; nothing in the
runs was retrained. Simulated recordings only.</p>

<div class="box"><b>The answer.</b>
<ul>
<li><b>It is the learning rate at the start of training.</b> chorus_norm collapses in
{by_lr[('chorus_norm', 0.03)][0]} of its {by_lr[('chorus_norm', 0.03)][1]} inner fits at a learning
rate of 0.03 and in {cn_lo} of {cn_lo_n} below it.</li>
<li><b>What breaks is the head</b>, the eight-layer stack that turns the pooled per-cell statistics
into the output: {dead[('chorus_norm', True)]} of {len(cz[('chorus_norm', True)])} collapsed chorus_norm
fits have a head layer whose units never switch on, so almost no signal passes and the output barely
moves; {len(odd_work)} of the {len(cz[('chorus_norm', False)])} working fits {'has' if len(odd_work) == 1 else 'have'} one.</li>
<li><b>It happens in the first steps.</b> Replayed exactly, a collapsed fit's head starts losing
whole layers by step {first_dead} and its loss never leaves its starting level. The same fit, with the
same initial weights and the same data, trains at a learning rate of 0.01 or 0.003, or at 0.03 with a
200-step warm-up; a 50-step warm-up is not enough.</li>
<li><b>This is not the failure PR #596 fixed.</b> That was plain chorus's per-cell encoder starting
deaf at every learning rate; chorus_norm's standardization repaired it. This is a second mechanism, in
the head, and almost entirely at the top of the tuning grid.</li>
</ul></div>

<h2>1. The finding it explains</h2>
<p>In goal 2's comparison each net is tuned by inner fits: each of 24 configurations is trained at 3
training seeds on each pair of 4 folds, 432 inner fits per net per draw. The replicate report
(<code>docs/learned/tuned_vs_coact/replicate1/</code>) found that
{per_draw[('chorus_norm', 'first')][0]} and {per_draw[('chorus_norm', 'second')][0]} of chorus_norm's
432 inner fits in the two draws made exactly one call on every recording they were scored on — the
whole recording as one call, which matches one of 15 planted events, F1 0.125 — and that
{both['chorus_norm']} of them are the same fit (configuration, training seed and pair of folds) in both
draws. The draws share their configurations and training seeds and differ only in their recordings, so
the collapse follows the fit's configuration and starting weights more than its data. It matters because chorus_norm's scores
mix a working model with one that never trained.</p>

<h2>2. Which configurations collapse</h2>
<p>{ref_('rates', 'collapse by configuration')} shows each configuration's collapse share. For
chorus_norm the learning rate separates them almost completely: every configuration at 0.03 collapses
in {min(cn_hi):.0%} to {max(cn_hi):.0%} of its fits, and below 0.03 the collapse is rare. Within 0.03
the per-cell encoder's shape shifts the share: by width,
{'; '.join(f"{v} units {pct(by_w[v])} ({by_w[v][0]} of {by_w[v][1]} fits)" for v in widths)}; by depth,
{'; '.join(f"{v} layers {pct(by_d[v])} ({by_d[v][0]} of {by_d[v][1]} fits)" for v in depths)}.
Nothing else in the fit's identity matters: across all of chorus_norm's inner fits the share is
{', '.join(pct(by_seed[s]) for s in (0, 1, 2))} at training seeds 0, 1 and 2, and between
{min(c[0] / c[1] for c in by_pair):.0%} and {max(c[0] / c[1] for c in by_pair):.0%} across the {len(pairs)} pairs of
training folds. chorus_gain_norm shows the same pattern, milder.</p>
""" + fig("rates", fig_rates(rows),
          "<b>The top of the learning-rate grid is where chorus_norm collapses.</b> Each dot is one "
          "configuration: the share of its 36 inner fits (3 training seeds × 6 pairs of folds × 2 "
          "draws) that made one call per recording, one row per learning rate. Panel A chorus_norm, "
          "panel B chorus_gain_norm.") + f"""
<p><b>Table 1. Collapsed inner fits, by learning rate and by draw.</b></p>
<div class="tablewrap"><table><thead><tr><th>net</th><th>lr 0.003</th><th>lr 0.01</th><th>lr 0.03</th>
<th>first draw</th><th>second draw</th><th>the same fit in both</th></tr></thead><tbody>{t1}</tbody>
</table></div>

<h2>3. What a collapsed fit is</h2>
<p>chorus_norm passes each cell through a shared encoder, standardizes the encoder's output over time,
turns it into a vote, pools the votes into three statistics, and feeds those to a head of 8 layers of 8
units, each followed by a GELU (a smooth activation that passes positive input and squeezes negative
input to small values near zero). Call a head layer <i>dead</i> when none of its 8 units ever outputs
more than 0.001 over a whole recording. Every second-draw chorus inner fit was reloaded and run on one
bench recording of that draw ({ref_('census', 'what the head does')}). In chorus_norm,
{dead[('chorus_norm', True)]} of the {len(cz[('chorus_norm', True)])} collapsed fits have a dead head
layer, against {len(odd_work)} of the {len(cz[('chorus_norm', False)])} working fits. A dead layer passes
only the small negative residue of its GELUs, so the output hardly moves: the median spread (standard
deviation over the recording's frames) of the output logit is {med_sd[('chorus_norm', True)]:.4f} in
collapsed fits against {med_sd[('chorus_norm', False)]:.2f} in working ones, and the fit's threshold
falls to the bottom of its grid, which makes the whole recording one call.
{odd_text}</p>
<p>In chorus_gain_norm, {dead[('chorus_gain_norm', True)]} of {len(cz[('chorus_gain_norm', True)])}
collapsed fits have a dead head layer, against {dead[('chorus_gain_norm', False)]} of {len(cgn_work)}
working fits. The other {len(cgn_rest)} collapsed fits have the same flat output without a dead layer,
and they are not concentrated at lr 0.03
({', '.join(f"{sum(e['lr'] == lr for e in cgn_rest)} at lr {lr:g}" for lr in LRS)}).
Their vote gains, the one parameter chorus_gain_norm adds, end a median
{st.median(e['vote_gain_moved'] for e in cgn_rest):.0%} from where they started, against
{st.median(e['vote_gain_moved'] for e in cgn_work):.0%} in working fits. That is a second route to the
same failure, and this page does not establish what it is.</p>
""" + fig("census", fig_census(cen),
          "<b>A collapsed chorus_norm fit has a dead head layer; a working one almost never does.</b> One dot "
          "per second-draw inner fit, run on one bench recording of that draw (quiet background, seed "
          f"2000): the smallest share of live units in any of its head layers, against the spread of "
          f"its output logit over the recording. {sw('c2')}collapsed, {sw('c1')}working.") + f"""

<h2>4. When it happens, and what prevents it</h2>
<p>A collapsed fit (configuration {ref['cfg'][:8]}, lr 0.03, training seed {ref['seed']}) and the one
working fit of the same configuration were replayed exactly as the run trained them; each replay
reproduced its saved checkpoint to the last bit. Both start with an output that barely varies (spread
{ref['log'][0]['logit_sd']:.4f} and {work_fit['log'][0]['logit_sd']:.4f} on the first batch). The
working fit escapes and its loss falls; the collapsed fit's loss never leaves its starting level
({ref_('curves', 'the replays')}), and its head has a dead layer by step {first_dead} and
{sum(a == 0 for a in ref['log'][-1]['head_alive'])} of its 8 at the end, against
{sum(a == 0 for a in work_fit['log'][-1]['head_alive'])} in the working fit
({ref_('dead', 'the head dying')}). The
collapsed fit was then replayed with one thing changed. With the same initial weights and the same data
it trains at lr 0.01 or 0.003, and at lr 0.03 with the learning rate ramped up over the first 200 steps;
a 50-step ramp is not enough. A 200-step warm-up at lr 0.03 was then applied to {len(wu)} more collapsed
fits from {len(wu_cfgs)} lr-0.03 configurations{' (one of them the configuration of Figure 3)' if ref['cfg'] in wu_cfgs else ''}:
{wu_ok} of them train (Table 2). {'The one that does not, ' + wu_fail[0]['cfg'][:8] + ', is from a configuration that collapsed in ' + str(per_cfg[('chorus_norm', wu_fail[0]['cfg'], 0.03)][0]) + ' of its ' + str(per_cfg[('chorus_norm', wu_fail[0]['cfg'], 0.03)][1]) + ' fits; a longer warm-up was not tried.' if len(wu_fail) == 1 else ''}</p>
""" + fig("curves", fig_curves(curves),
          "<b>The same fit collapses or trains depending only on its early learning rate.</b> "
          "Training loss, the mean of 5 logged steps (logged every 10), for one collapsed chorus_norm "
          "fit replayed as run and with one change each, and the working fit of the same "
          "configuration; warm-up replays dashed. The 50-step warm-up retraces the fit as run almost "
          "exactly. Loss is clipped at 2.0.") + fig(
          "dead", fig_dead({"the working fit": (work_fit, "var(--c1)"),
                            "the collapsed fit, as run": (ref, "var(--c2)")}),
          "<b>The collapsed fit's head dies layer by layer; the working fit's does not.</b> The two "
          "as-run replays of Figure 3: how many of the head's 8 layers have no unit above 0.001 "
          "anywhere in the training batch, logged every 10 steps.") + f"""
<p><b>Table 2. A 200-step warm-up at lr 0.03, applied to other collapsed fits.</b></p>
<div class="tablewrap"><table><thead><tr><th style='text-align:left'>fit</th><th>final loss</th>
<th>outcome</th></tr></thead><tbody>{t2}</tbody></table></div>
<p class="tnote">Final loss is the mean of the last 5 logged steps; a fit "trains" when it is below
0.5 (collapsed fits sit near 1.5).</p>

<h2>5. What it means, and the choice it leaves</h2>
<ul>
<li><b>Tuning already stepped around it, at a cost.</b> A configuration whose fits collapse scores
badly in the inner selection, so tuning never chose a lr-0.03 configuration for chorus_norm: its
{sum(ref_lr[('chorus_norm', lr)][1] for lr in LRS)} refits across both draws (the chosen
configurations, trained afresh and scored on held-out recordings) are
{', '.join(f"{ref_lr[('chorus_norm', lr)][1]} at lr {lr:g}" for lr in LRS)}. The
collapse therefore did not put dead models into chorus_norm's held-out scores wholesale; it removed
{len(cn_hi)} of its {len([k for k in per_cfg if k[0] == 'chorus_norm'])} configurations from
contention, so chorus_norm was in effect tuned over a smaller grid than the one declared.</li>
<li><b>The refits that did collapse are the same failure.</b> {len(ref_bad)} refits collapsed across
both draws ({'; '.join(f"{r['net']}, {r['draw']} draw, lr {r['lr']:g}" for r in ref_bad)}); each
puts a † beside its net in the replicate report. The second draw's {len(cen_ref_bad)} were in the census, and
{sum(e['min_head_alive'] == 0 for e in cen_ref_bad)} of them have a dead head layer.</li>
<li><b>A repair is a design decision for goal 2, not this page's.</b> Three follow from the evidence:
drop lr 0.03 from the chorus grids, which accepts the smaller grid tuning already used in effect; add a
learning-rate warm-up (200 steps rescued {wu_ok} of {len(wu)} fits tried); or change the head (8 layers
of 8 units, never tuned), which was not tested here. Any of them changes chorus_norm's numbers in goal
2 and would need both draws re-run to compare.</li>
<li><b>A collapse is detectable when it happens.</b> On the census recording, the output's spread
separates the two groups without overlap in both nets and in the refits: at most {sd_coll_max:.2f} in
every collapsed fit, at least {sd_work_min:.2f} in every working one. A check at the end of training
could refuse such a fit instead of scoring it.</li>
</ul>

<h2>6. Limits</h2>
<ul>
<li>Simulation only; the census and the replays use the second draw's fits; the collapse table uses
both draws.</li>
<li>The census runs each fit on one recording, which some fits trained on and others did not. A unit
counted dead there could switch on elsewhere. The separation by output spread held on this one
recording; it was not tested on others.</li>
<li>Replays are exact for fits as run (checked against the checkpoints); a counterfactual replay is the
same code with one change, and was scored by its training loss, not re-scored on held-out
recordings.</li>
<li>Warm-up was tried on {len(wu) + 1} collapsed fits, not on the whole grid or on chorus_gain_norm.</li>
</ul>

<h2>7. Where everything is</h2>
<ul>
<li>This page and its tables (<code>collapse_table.json</code>, <code>census.json</code>,
<code>replays/</code>): <code>docs/learned/chorus_collapse/</code> in the repository, where a test
rebuilds the page from them, and <code>&lt;darkroom&gt;/bugarach/{FOLDER}/</code>.</li>
<li>The tool: <code>tools/diagnose_chorus_collapse.py</code>; it needs a checkout that registers the
chorus nets (branch <code>replicate-run</code>), passed as <code>--code</code>.</li>
<li>The runs it reads: the two draws' <code>results/</code> folders in the darkroom
(<code>{R.THEIRS_FOLDER}</code> and <code>{R.MINE_FOLDER}</code>).</li>
<li>The earlier diagnosis of plain chorus: PR #596 and
<code>docs/learned/field_size_candidates/why_chorus.txt</code> (branch <code>replicate-run</code>).</li>
</ul>
"""
    return ("<!doctype html><html lang='en'><head>"
            "<meta name='viewport' content='width=device-width,initial-scale=1'>"
            "<meta charset='utf-8'><title>Why chorus_norm collapses</title><style>" + R.CSS
            + CSS_EXTRA + "</style></head><body>" + body + "</body></html>")


def main(argv=None) -> int:
    p = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    sub = p.add_subparsers(dest="cmd", required=True)
    for name in ("table", "census", "replay", "page"):
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
        cen = census(rows, work)
        (work / "census.json").write_text(json.dumps(cen))
        print(f"{len(cen)} fits probed")
    elif a.cmd == "replay":
        d = replay(a.cfg, a.seed, a.recs, lr=a.lr, warmup=a.warmup, work=work)
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
