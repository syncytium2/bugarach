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

BENCH_SEEDS = (1, 2, 3)


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
                   train_seconds=train_seconds, history=hist)


def pick_threshold(model, make_recording, *, dt, seed, n_val: int = 4,
                   stream=None, merge_gap_frames: int = 20):
    """Choose the one operating point, on held-out **training-distribution** data.

    Never on the bench. A threshold tuned against the recordings a model is then
    scored on is the benchmark leaking into the model, which is a subtler version
    of the mistake this project already paid for twice.
    """
    import torch

    seeds = [TRAIN_SEED_BLOCK + 500_000 + seed * 1000 + i for i in range(n_val)]
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
    grid = np.concatenate([np.arange(0.05, 0.95, 0.05),
                           1.0 - np.geomspace(0.05, 1e-4, 12)])
    best, best_f1 = 0.5, -1.0
    for thr in grid:
        tot_hit = tot_det = tot_pl = 0
        for p, enc, gt in scored:
            det = decode(p, threshold=float(thr),
                         merge_gap_frames=merge_gap_frames)
            sc = score_stream(gt, det.to_seconds(enc))
            tot_hit += sc.n_hit
            tot_det += sc.n_detected
            tot_pl += sc.n_planted
        if tot_det == 0 or tot_pl == 0:
            continue
        r, pr = tot_hit / tot_pl, tot_hit / tot_det
        f1 = 0.0 if (r + pr) == 0 else 2 * r * pr / (r + pr)
        if f1 > best_f1:
            best_f1, best = f1, float(thr)
    if best >= grid[-1] - 1e-12 or best <= grid[0] + 1e-12:
        import warnings
        warnings.warn(
            f"threshold {best:.4g} sits at the edge of the searched grid "
            f"[{grid[0]:.4g}, {grid[-1]:.4g}] — the search was still climbing "
            "when it stopped, so this is not an operating point. Widen it.",
            RuntimeWarning, stacklevel=2)
    return best, merge_gap_frames
