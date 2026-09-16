#!/usr/bin/env python3
"""Does an untrained model hear its input? The gate `chorus` failed, as a check.

    PYTHONPATH=src python tools/probe_untrained_response.py [--arch NAME ...] [--seeds 3]

`chorus` scored F1 0.125 in every fold because its per-cell encoder started deaf: one
onset moved a vote by at most 0.0003, and the encoder's gradient was about 270,000
times smaller than the head's (docs/learned/field_size_candidates/why_chorus.txt).
Nothing in the pipeline asked, so the answer arrived as a failed overnight-sized run.
This asks first, in seconds, on synthetic input with no labels:

* **vote change for one onset** -- for models with a per-cell vote (``roi`` or
  ``line``'s smear and sigmoid): the largest change one onset in one otherwise silent
  cell makes to that cell's vote, on a 0-to-1 scale.
* **gradient share** -- one backward pass of a binary cross-entropy loss against a
  label at a planted co-active frame; the gradient norm reaching everything before the
  head, divided by the head's. A share near zero means the head is the only part
  that learns.
* **output change at a co-active frame** -- how far the model's output moves when 8 of
  32 cells fire in one frame, against the same field without them.

Prints one line per model and seed. Writes nothing.
"""

from __future__ import annotations

import argparse

import torch

from bugarach.learn.nets import ARCHITECTURES


def _vote(model, x):
    """Per-cell votes (n, C, T) for a (1, n, T) raster, or None if the model has none."""
    b, n, t = x.shape
    if hasattr(model, "roi"):
        # chorus and its variants: rebuild the vote path from the model's own pieces
        # by running forward with the pool replaced is not possible without editing
        # it, so reproduce the three optional steps in order.
        xr = x.reshape(b * n, 1, t)
        if hasattr(model, "log_input_gain"):
            xr = xr * torch.exp(model.log_input_gain)
        h = model.roi(xr)
        if getattr(model, "norm", False):
            h = (h - h.mean(dim=2, keepdim=True)) / (h.std(dim=2, keepdim=True,
                                                           unbiased=False) + 1e-6)
        if hasattr(model, "vote_gain") and hasattr(model, "vote_bias"):
            return torch.sigmoid(model.vote_gain.view(1, -1, 1)
                                 * (h - model.vote_bias.view(1, -1, 1)))
        return torch.sigmoid(h)
    if hasattr(model, "_smear"):
        sm = torch.nn.functional.conv1d(x.reshape(b * n, 1, t), model._smear(x.device),
                                        padding=model.k)
        return torch.sigmoid(model.vote_gain.view(1, -1, 1)
                             * (sm - model.vote_bias.view(1, -1, 1)))
    return None


def probe(name: str, seed: int, n: int = 32, t: int = 4096) -> dict:
    torch.manual_seed(seed)
    model = ARCHITECTURES[name].make().eval()
    out: dict = {}

    silent = torch.zeros(1, 1, t)
    one = silent.clone()
    one[0, 0, t // 2] = 1
    with torch.no_grad():
        v0, v1 = _vote(model, silent), _vote(model, one)
    if v0 is not None:
        out["vote_change_one_onset"] = float((v1 - v0).abs().max())

    g = torch.Generator().manual_seed(seed)
    field = (torch.rand(1, n, t, generator=g) < 0.001).float()
    planted = field.clone()
    planted[0, :8, t // 2] = 1
    with torch.no_grad():
        out["output_change_8_of_32"] = float((model(planted) - model(field))[0, t // 2])

    model.train()
    y = torch.zeros(1, t)
    y[0, t // 2 - 2:t // 2 + 3] = 1
    loss = torch.nn.functional.binary_cross_entropy_with_logits(model(planted), y)
    loss.backward()
    head = sum(float(p.grad.norm() ** 2) for k, p in model.named_parameters()
               if k.startswith("head.") and p.grad is not None) ** 0.5
    rest = sum(float(p.grad.norm() ** 2) for k, p in model.named_parameters()
               if not k.startswith("head.") and p.grad is not None) ** 0.5
    out["gradient_share_before_head"] = rest / head if head else float("nan")
    return out


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--arch", nargs="+", default=sorted(ARCHITECTURES))
    ap.add_argument("--seeds", type=int, default=3)
    a = ap.parse_args(argv)
    for name in a.arch:
        for seed in range(a.seeds):
            r = probe(name, seed)
            print(f"{name:18s} seed {seed}  " + "  ".join(
                f"{k} {v:.3g}" for k, v in r.items()))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
