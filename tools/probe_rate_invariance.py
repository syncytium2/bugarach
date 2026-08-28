#!/usr/bin/env python3
"""Push a rate change through the WHOLE trained model, not through its kernel.

    python tools/probe_rate_invariance.py --out docs/learned/rate_invariance.json

**Why this exists.** ``build_tube``'s difference-of-Gaussians kernel is area-matched, so
a flat field integrates to zero and a uniform rate change cancels *in the kernel*. That
property is real, it is arithmetic, and it is what the architecture figure's
`flat field cancels` label refers to.

It is not a property of the model. ``Tube.forward`` ends

    self.head(torch.cat([bright, resp], dim=1))

so the raw pooled brightness trace — the absolute local activity level — reaches the head
on its own channel, beside the zero-integral responses. Whatever the kernel cancels, that
channel carries straight through.

An earlier version of the learned-detector page claimed rate invariance "by construction"
and offered, as its test, a figure panel that convolves a step with a **numpy
reimplementation of the kernel**. That panel cannot fail: it tests the arithmetic, not the
network. The 2026-08-27 murderboard called it blocking.

So this measures the thing the claim is about. Train the model exactly as the bench trains
it, then run it over recordings that contain **no planted events at all**, at multiplies of
the background rate, and count frames over the model's own operating point. A rate-invariant
detector returns roughly the same count at every multiple.

It also runs the ablation that separates the two mechanisms: re-scoring with the brightness
channel zeroed leaves only the variance term, so the gap between the two curves is what the
bypass is worth.

Everything is one seeded training run — the same limitation as every other learned number
in this repository. The effect it reports is an order of magnitude, not a measurement.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

MULTIPLES = (1, 2, 4, 8)
"""Background multiples. 1 is the bake-off's own fitted background."""


def _bench():
    from bugarach import bench
    return bench


def _null_recording(spec: dict, seed: int, multiple: float):
    """A recording at `multiple` x background with NOTHING planted in it.

    The planted-event machinery is switched off rather than filtered afterwards:
    `n_per_level` empty means the generator plants nothing, and the distractors and
    the probe block go with it. What is left is background and only background, which
    is the only condition under which "did the rate change move the detector" has a
    clean answer.
    """
    s = dict(spec)
    s["bg_rate_hz"] = spec["bg_rate_hz"] * multiple
    # Zero counts, not an empty list: the generator requires `n_per_level` and
    # `participation` to be the same length, so plant zero events at each level
    # rather than removing the levels.
    s["n_per_level"] = [0] * len(spec["participation"])
    s["n_distractors"] = 0
    s["hot_rate_hz"] = s["bg_rate_hz"]          # no hot block: same rate throughout
    return _fair_bakeoff()._make_recording(s, seed)


def _fair_bakeoff():
    import importlib.util
    p = Path(__file__).with_name("fair_bakeoff.py")
    spec = importlib.util.spec_from_file_location("_fb", p)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def _frames_over(model, threshold, slice_, dt, *, kill_bright=False):
    """Count frames whose score clears the operating point.

    `kill_bright` zeroes the bypass channel between the concatenation and the head, so
    the head sees the centre-surround responses and a constant. That isolates the two
    mechanisms: what remains is the variance term the kernel cannot cancel.
    """
    import torch
    from bugarach.learn.encode import encode

    enc = encode(slice_, dt=dt)
    x = torch.from_numpy(enc.raster).float().unsqueeze(0)

    with torch.no_grad():
        if not kill_bright:
            logits = model(x)
        else:
            b, n, t = x.shape
            kmin = int(torch.exp(model.log_center.detach()).min().clamp(1, model.k))
            pooled = torch.nn.functional.max_pool1d(
                x.reshape(b * n, 1, t), kernel_size=2 * kmin + 1,
                stride=1, padding=kmin).reshape(b, n, t)
            bright = pooled.sum(dim=1, keepdim=True) / max(n, 1)
            resp = torch.nn.functional.conv1d(
                bright, model._kernels(x.device), padding=model.k)
            logits = model.head(torch.cat([torch.zeros_like(bright), resp],
                                          dim=1)).squeeze(1)
        score = torch.sigmoid(logits).squeeze(0).numpy()
    return int((score >= threshold).sum()), int(score.size)


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--bakeoff", default="docs/learned/bakeoff.json")
    ap.add_argument("--out", default="docs/learned/rate_invariance.json")
    ap.add_argument("--steps", type=int, default=900)
    ap.add_argument("--seed", type=int, default=7)
    a = ap.parse_args(argv)

    from bugarach.learn.train import train

    spec = json.loads(Path(a.bakeoff).read_text())["spec"]
    fb = _fair_bakeoff()
    dt = spec["grid_sec"]

    # Train on the bake-off's own training recordings, same settings the bench uses.
    train_seeds = [1000 + i for i in range(6)]
    cache: dict[int, tuple] = {}

    def rec(seed):
        if seed not in cache:
            cache[seed] = fb._make_recording(spec, seed)
        return cache[seed]

    mk = lambda seed, _t=tuple(train_seeds): rec(_t[seed % len(_t)])   # noqa: E731
    print(f"training tube: {a.steps} steps, seed {a.seed}")
    tr = train("tube", mk, dt=dt, n_train=6, steps=a.steps, crop=4096,
               batch=3, lr=1e-2, seed=a.seed)
    thr = float(tr.threshold)
    print(f"  operating point {thr:.6f}, {tr.n_params} params")

    out = {"threshold": thr, "n_params": int(tr.n_params), "steps": a.steps,
           "seed": a.seed, "bg_rate_hz": spec["bg_rate_hz"],
           "note": "recordings contain no planted events, no distractors, no hot block",
           "by_multiple": {}}

    for m in MULTIPLES:
        sl, _gt = _null_recording(spec, 90210, m)
        full, n_frames = _frames_over(tr.model, thr, sl, dt)
        nobright, _ = _frames_over(tr.model, thr, sl, dt, kill_bright=True)
        out["by_multiple"][str(m)] = {
            "background_hz": spec["bg_rate_hz"] * m,
            "frames_over_threshold": full,
            "frames_over_threshold_no_bypass": nobright,
            "n_frames": n_frames,
        }
        print(f"  x{m}: {full:6d} frames over threshold  "
              f"({nobright:6d} with the bypass zeroed)  of {n_frames}")

    Path(a.out).write_text(json.dumps(out, indent=1, sort_keys=True) + "\n")
    print(f"wrote {a.out}")
    return 0


if __name__ == "__main__":                                      # pragma: no cover
    raise SystemExit(main())
