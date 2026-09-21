#!/usr/bin/env python3
"""Time one training step of registered architectures on the CPU and, where present, a GPU.

    python tools/bench_learned_step.py [--models tube line line_bound] [--rois 32 80] [--steps 5]

One step is Adam on a batch of three crops of 4,096 frames, sparse random onsets, loss the mean
output, so the timing is the model's forward and backward pass and nothing else. The CPU runs one
thread, as `bugarach.learn.train.pin_threads` does for every fit. The GPU is Apple's (MPS) or CUDA,
whichever torch reports. Exploratory: it measures step time on one stream, not a sweep's
throughput, and it says nothing if other work is running on the machine.
"""

from __future__ import annotations

import argparse
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))

CROP_FRAMES = 4096
BATCH = 3
ONSET_PROBABILITY = 0.002


def gpu_device(torch):
    if torch.cuda.is_available():
        return "cuda"
    if torch.backends.mps.is_available():
        return "mps"
    return None


def synchronize(torch, device):
    if device == "cuda":
        torch.cuda.synchronize()
    elif device == "mps":
        torch.mps.synchronize()


def seconds_per_step(name, device, n_roi, steps):
    import torch

    from bugarach.learn.nets import ARCHITECTURES

    torch.manual_seed(0)
    model = ARCHITECTURES[name].make().to(device)
    opt = torch.optim.Adam(model.parameters(), lr=1e-3)
    x = (torch.rand(BATCH, n_roi, CROP_FRAMES) < ONSET_PROBABILITY).float().to(device)

    def step():
        opt.zero_grad()
        model(x).mean().backward()
        opt.step()

    step()  # warm-up: kernel compilation and allocation are not the step
    synchronize(torch, device)
    t0 = time.perf_counter()
    for _ in range(steps):
        step()
    synchronize(torch, device)
    return (time.perf_counter() - t0) / steps


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--models", nargs="+", default=["tube", "line", "line_bound"])
    ap.add_argument("--rois", nargs="+", type=int, default=[32, 80])
    ap.add_argument("--steps", type=int, default=5)
    a = ap.parse_args(argv)
    import torch

    from bugarach.learn.train import pin_threads

    from bugarach.learn.nets import ARCHITECTURES

    pin_threads()
    gpu = gpu_device(torch)
    print(f"torch {torch.__version__}; GPU: {gpu or 'none'}")
    models = [m for m in a.models if m in ARCHITECTURES]
    for m in sorted(set(a.models) - set(models)):
        print(f"{m}: not registered on this checkout, skipped")
    for n_roi in a.rois:
        for name in models:
            cpu = seconds_per_step(name, "cpu", n_roi, a.steps)
            line = f"{name:12s} {n_roi:4d} ROIs   CPU, 1 thread {cpu * 1000:8.1f} ms/step"
            if gpu:
                g = seconds_per_step(name, gpu, n_roi, a.steps)
                line += f"   {gpu} {g * 1000:8.1f} ms/step   speedup {cpu / g:5.1f}x"
            print(line, flush=True)


if __name__ == "__main__":
    main()
