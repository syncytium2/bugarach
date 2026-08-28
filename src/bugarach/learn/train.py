"""Train a learned detector on generated recordings, and score it like the six.

The training set is **generated, not stored**. The generator is deterministic and
fast, so recordings are made on demand from seeds — no dataset contract, no
on-disk format, and no stale artifact to outlive the settings that made it
(``simulation_plan.md`` §5's last trap, avoided by not creating the artifact).

Seed discipline
---------------
Training seeds are drawn from a block **disjoint from the bench's** (1, 2, 3).
Evaluating on a recording the model trained on would be the most flattering
possible mistake and is easy to make by accident, so the block is explicit and
asserted rather than assumed.
"""

from __future__ import annotations

from dataclasses import dataclass, field

import numpy as np

from bugarach.learn.encode import decode, encode, frame_targets
from bugarach.learn.nets import ARCHITECTURES, n_params
from bugarach.score import score_stream

TRAIN_SEED_BLOCK = 10_000
"""Training seeds start here. The bench scores on 1, 2, 3."""

VAL_SEED_BLOCK = TRAIN_SEED_BLOCK + 500_000
"""Threshold-validation seeds start here, and the gap is the whole guarantee.

:func:`train` draws from :data:`TRAIN_SEED_BLOCK` and :func:`pick_threshold` from
here, so the two never ask for the same seed. **That only separates recordings if
the ``make_recording`` a caller supplies honours the boundary**, and until
2026-08-28 no caller did: a maker of the shape ``lambda seed: recs[seed % len]``
maps both blocks onto one set, while the assertions below still pass because they
compare seeds rather than recordings. :func:`fold_maker` is the fix, and it exists
so the boundary has one implementation instead of one per call site.
"""

THREADS = 1
"""Intra-op threads, pinned — the number is part of the result.

``torch.manual_seed`` fixes the draws and nothing else. Left alone, torch reads
the thread count off the hardware and the CPU reduction order goes with it: the
published bake-off reproduced only on a 10-thread machine, and at 1, 2 or 4
threads the same seeds gave a mean F1 0.0178 higher with one fold moving 45 -> 62
detections. The 1-, 2- and 4-thread runs were byte-identical to each other, so
this is a reduction-order code path switching rather than chaos — which is why
pinning fixes it rather than merely hiding it. **1 is the only value available on
every machine**, so it is the one that makes a number regenerable from the
repository alone.
"""

BENCH_SEEDS = (1, 2, 3)


def pin_threads(n: int = THREADS) -> int:
    """Pin torch's intra-op threads. Idempotent; returns what is now set."""
    import torch

    if torch.get_num_threads() != n:
        torch.set_num_threads(n)
    return torch.get_num_threads()


def fold_maker(rec, seeds, *, n_val: int = 2):
    """A ``make_recording`` that keeps fitting and threshold-picking apart.

    ``rec`` is ``seed -> (slice, ground_truth)``; ``seeds`` are the recordings of
    the **training folds only**, so the held-out fold is unreachable from here by
    construction rather than by discipline — it is simply not in the list.

    Those recordings are split again: the last ``n_val`` answer
    :func:`pick_threshold`'s block and the rest answer :func:`train`'s. Callers
    used to hand both blocks the same recordings through a ``seed % len`` maker,
    which defeated a separation :func:`pick_threshold` asserts and its docstring
    calls *"explicit and asserted rather than assumed."* The scored fold was never
    reachable either way, so no published F1 was inflated by this — what was wrong
    is that the fairness guarantee the code stated was not the one it delivered.

    Returns ``(mk, n_fit, n_val)`` so a caller can size its own requests rather
    than asking for more recordings than exist and receiving them back modulo.
    """
    seeds = tuple(seeds)
    if len(seeds) < 2:
        raise ValueError(
            f"{len(seeds)} training recording(s) cannot be split into a fitting "
            "set and a threshold-validation set — the operating point would be "
            "picked on the recordings the model had just fitted")
    n_val = max(1, min(int(n_val), len(seeds) - 1))
    fit, val = seeds[:-n_val], seeds[-n_val:]

    def mk(seed):
        if seed >= VAL_SEED_BLOCK:
            return rec(val[(seed - VAL_SEED_BLOCK) % len(val)])
        return rec(fit[(seed - TRAIN_SEED_BLOCK) % len(fit)])

    return mk, len(fit), len(val)


@dataclass
class Trained:
    """A trained model, its operating point, and what it cost."""

    name: str
    model: object
    threshold: float
    n_params: int
    dt: float
    merge_gap_frames: int
    train_seconds: float = 0.0
    history: list = field(default_factory=list)
    threads: int = 0
    """Intra-op threads this was fitted at — a condition of the number, not trivia."""

    def predict(self, slice_, *, stream=None):
        """Detections in the six ports' contract, ready for ``score_stream``."""
        import torch

        enc = encode(slice_, dt=self.dt, stream=stream)
        with torch.no_grad():
            x = torch.from_numpy(enc.raster).unsqueeze(0)
            p = torch.sigmoid(self.model(x)).squeeze(0).numpy()
        det = decode(p, threshold=self.threshold,
                     merge_gap_frames=self.merge_gap_frames)
        return det.to_seconds(enc), enc


def _recording(make, seed, dt, stream=None):
    s, gt = make(seed)
    enc = encode(s, dt=dt, stream=stream)
    return enc, frame_targets(gt, enc), gt


def train(name: str, make_recording, *, dt: float = 0.1, n_train: int = 12,
          steps: int = 300, crop: int = 4096, batch: int = 4,
          lr: float = 3e-3, seed: int = 0, stream=None, **arch_over) -> Trained:
    """Fit one architecture. Returns it with a threshold already chosen.

    make_recording: ``seed -> (slice, ground_truth)``. Called with seeds from the
      training block only.
    crop: training window in **frames**. Long enough to contain the local
      background a model must judge against, short enough to batch.
    """
    import time

    import torch

    torch.manual_seed(seed)
    threads = pin_threads()
    arch = ARCHITECTURES[name]
    model = arch.make(**arch_over)
    opt = torch.optim.Adam(model.parameters(), lr=lr)

    seeds = [TRAIN_SEED_BLOCK + seed * 1000 + i for i in range(n_train)]
    assert not set(seeds) & set(BENCH_SEEDS), "training seed collides with the bench"
    data = [_recording(make_recording, s, dt, stream)[:2] for s in seeds]

    # Events occupy ~1% of frames. Without a positive weight the model learns to
    # answer "no" and scores 99% accuracy while detecting nothing.
    pos = float(np.mean([y.mean() for _, y in data]))
    pos_weight = torch.tensor([(1.0 - pos) / max(pos, 1e-6)], dtype=torch.float32)
    lossf = torch.nn.BCEWithLogitsLoss(pos_weight=pos_weight)

    # Where the events are, per recording. With ~0.5% positive frames a uniformly
    # drawn crop spends nearly all its gradient on background, and 400 steps of
    # that is why the first version of this trained to a constant. Half the crops
    # are drawn to contain an event; the other half stay uniform so the model
    # still sees ordinary background, and the THRESHOLD is picked later on
    # naturally-sampled recordings so this sampling never reaches the operating
    # point (`simulation_plan.md` §5: event frequency is a knob on the label
    # distribution, not a cosmetic detail).
    pos_idx = [np.flatnonzero(y > 0) for _, y in data]

    rng = np.random.RandomState(seed)
    t0 = time.time()
    hist = []
    model.train()
    for step in range(steps):
        xs, ys = [], []
        for _ in range(batch):
            di = rng.randint(len(data))
            enc, y = data[di]
            if enc.n_frame <= crop:
                x, yy = enc.raster, y
            else:
                pi = pos_idx[di]
                if pi.size and rng.rand() < 0.5:
                    c = int(pi[rng.randint(pi.size)])
                    a = int(np.clip(c - crop // 2, 0, enc.n_frame - crop))
                else:
                    a = rng.randint(0, enc.n_frame - crop)
                x = enc.raster[:, a:a + crop]
                yy = y[a:a + crop]
            xs.append(torch.from_numpy(np.ascontiguousarray(x)))
            ys.append(torch.from_numpy(np.ascontiguousarray(yy)))
        # Recordings can differ in ROI count; a batch must not silently assume
        # they do not. Same n_roi within a batch is guaranteed by one generator,
        # but the model itself is ROI-count agnostic and that is the point.
        x = torch.stack(xs)
        y = torch.stack(ys)
        opt.zero_grad()
        loss = lossf(model(x), y)
        loss.backward()
        opt.step()
        if step % 50 == 0 or step == steps - 1:
            hist.append((step, float(loss.item())))
    train_seconds = time.time() - t0

    model.eval()
    thr, gap = pick_threshold(model, make_recording, dt=dt, seed=seed,
                              stream=stream)
    return Trained(name=name, model=model, threshold=thr,
                   n_params=n_params(model), dt=dt, merge_gap_frames=gap,
                   train_seconds=train_seconds, history=hist, threads=threads)


def pick_threshold(model, make_recording, *, dt, seed, n_val: int = 4,
                   stream=None, merge_gap_frames: int = 20):
    """Choose the one operating point, on held-out **training-distribution** data.

    Never on the bench. A threshold tuned against the recordings a model is then
    scored on is the benchmark leaking into the model, which is a subtler version
    of the mistake this project already paid for twice.
    """
    import torch

    seeds = [VAL_SEED_BLOCK + seed * 1000 + i for i in range(n_val)]
    assert not set(seeds) & set(BENCH_SEEDS)

    scored = []
    for s in seeds:
        sl, gt = make_recording(s)
        enc = encode(sl, dt=dt, stream=stream)
        with torch.no_grad():
            p = torch.sigmoid(model(torch.from_numpy(enc.raster).unsqueeze(0)))
        scored.append((p.squeeze(0).numpy(), enc, gt))

    # The grid must BRACKET the optimum. `tube` first picked 0.95 — the top of a
    # 0.05-0.95 sweep — and this repo already refuses a boundary answer for the
    # six (`bench.EdgeOfRange`): an optimum at the edge means the search stopped
    # while still climbing, and reporting it as an operating point is how a
    # boundary value once got published upstream as one.
    # ...and it must bracket it at BOTH ends, which took a second incident to
    # learn. The grid had a dense tail towards 1 and a hard floor at 0.05, which
    # was enough for as long as the threshold was picked on the recordings the
    # model had just fitted: probabilities run high on training data and the
    # optimum sat comfortably inside. The moment `fold_maker` started handing
    # this function recordings the fit had never seen (2026-08-28), the optimum
    # went straight through the floor and the warning below fired on the first
    # architecture of the first fold. A grid open at one end is only half a
    # search, and which half it is depends on data the search does not control.
    grid = np.unique(np.concatenate([np.geomspace(1e-4, 0.05, 12),
                                     np.arange(0.05, 0.95, 0.05),
                                     1.0 - np.geomspace(0.05, 1e-4, 12)]))
    # Pooled by `bench.pool_scores`, like everything else scored against this
    # benchmark. Selecting the operating point under one rule and reporting it
    # under another is the same defect as scoring two detectors differently, and
    # it is worse here because it is invisible: the number that ships is honest
    # and the choice behind it was not. Picking by hand cost 0.08 of F1 — the
    # hand-rolled rule counted probe firings against every candidate threshold,
    # so it chose a stricter point than the reported metric wanted.
    from bugarach.bench import pool_scores

    best, best_f1 = 0.5, -1.0
    for thr in grid:
        scs = []
        for p, enc, gt in scored:
            det = decode(p, threshold=float(thr),
                         merge_gap_frames=merge_gap_frames)
            scs.append(score_stream(gt, det.to_seconds(enc)))
        pooled = pool_scores(scs, detector="learned", regime="val", seeds=seeds)
        if pooled.n_scored <= 0 or pooled.n_planted == 0:
            continue
        f1 = pooled.f1
        if np.isfinite(f1) and f1 > best_f1:
            best_f1, best = f1, float(thr)
    if best >= grid[-1] - 1e-12 or best <= grid[0] + 1e-12:
        import warnings
        warnings.warn(
            f"threshold {best:.4g} sits at the edge of the searched grid "
            f"[{grid[0]:.4g}, {grid[-1]:.4g}] — the search was still climbing "
            "when it stopped, so this is not an operating point. Widen it.",
            RuntimeWarning, stacklevel=2)
    return best, merge_gap_frames
