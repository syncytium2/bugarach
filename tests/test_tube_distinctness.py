"""The tube's distinctness bound, asserted behaviourally because it does not hold.

`build_tube`'s docstring claimed each cell was capped at one vote and that the cap
was *"exact rather than soft"*, in explicit contrast to `tiny`, whose own docstring
admits its bound is soft. The contrast was the wrong way round, and it survived
because nothing measured it — the claim was about `max_pool1d`, read as a cap by
everyone who read the source, including the page that inherited it.

So the corrected docstring says *"probe it behaviourally; do not assert it"*, and
this is that probe. It exists to fail in **both** directions:

* if somebody restores the claim without changing the model, the docstring and this
  file disagree and the file wins;
* if somebody fixes the model — the honest fix is a per-cell cap before the sum
  rather than a max-pool over an already-binary raster — this test goes red and
  says so, which is the signal to correct the docstring in the same commit.

Numbers are deliberately not asserted. One training run per seed is the standing
limitation of everything learned here, and the *magnitude* of this effect moves an
order of magnitude between runs. What is stable, and what is asserted, is the
ordering: a couple of bursting cells reach the response of a genuine crowd.
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]

pytest.importorskip("torch", reason="the tube is the optional `dl` extra")

N_ROI = 32
T = 4000
AT = 2000            # where the synthetic input is placed, well clear of edges


@pytest.fixture(scope="module")
def trained():
    """One tube, fitted the way the bake-off fits one, on its own spec."""
    import torch

    from bugarach.learn.train import fold_maker, train
    from bugarach.simulate import simulate_coordination

    torch.set_num_threads(1)
    spec = dict(json.loads((ROOT / "docs/learned/bakeoff.json").read_text())["spec"])
    cache: dict[int, tuple] = {}

    def rec(seed):
        if seed not in cache:
            cache[seed] = simulate_coordination(seed=seed, **spec)
        return cache[seed]

    mk, n_fit, _ = fold_maker(rec, [2000, 2001, 2002, 2003, 2004, 2005])
    return train("tube", mk, n_train=min(10, n_fit), steps=900, crop=4096,
                 batch=3, lr=1e-2, seed=0)


def _peak(trained, spec: dict[int, list[int]]) -> float:
    """Highest probability the model reports anywhere on a synthetic raster."""
    import torch

    x = torch.zeros(1, N_ROI, T)
    for roi, onsets in spec.items():
        for f in onsets:
            # one-or-zero per (cell, frame), exactly as `encode` builds it
            x[0, roi, f] = 1.0
    with torch.no_grad():
        return float(torch.sigmoid(trained.model(x)).max())


def _kmin(trained) -> int:
    import torch

    m = trained.model
    return int(torch.exp(m.log_center.detach()).min().clamp(1, m.k))


def test_the_pool_widens_an_onset_rather_than_capping_a_cell(trained):
    """The structural half, and it needs no training run to be true.

    `raster` is already binary, so a max-pool over it returns a binary signal and
    bounds nothing. It spreads each onset over the pooling window instead, which
    *increases* what a repeatedly firing cell contributes to the centre integral.
    """
    import torch

    k = _kmin(trained)
    x = torch.zeros(1, N_ROI, T)
    for i in range(8):
        x[0, 0, AT + k * i] = 1.0
    pooled = torch.nn.functional.max_pool1d(
        x.reshape(N_ROI, 1, T), kernel_size=2 * k + 1, stride=1,
        padding=k).reshape(1, N_ROI, T)

    assert set(pooled.unique().tolist()) <= {0.0, 1.0}, "a cap would not be binary"
    assert pooled.sum() > x.sum(), (
        "the pool is described as capping a cell's contribution; it widened it "
        f"from {int(x.sum())} frames to {int(pooled.sum())}")


def test_two_bursting_cells_reach_a_four_cell_crowd(trained):
    """The behavioural half: the false coordination the design exists to reject.

    If this ever goes red because the left side dropped, distinctness has been
    fixed — update `build_tube`'s docstring in the same commit.
    """
    k = _kmin(trained)
    burst = [AT + k * i for i in range(8)]

    two_bursting = _peak(trained, {0: burst, 1: list(burst)})
    four_distinct = _peak(trained, {r: [AT] for r in range(4)})

    assert two_bursting >= 0.9 * four_distinct, (
        f"two bursting cells scored {two_bursting:.4f} against a four-cell "
        f"crowd's {four_distinct:.4f} — distinctness may now hold, which would "
        f"be good news and makes `build_tube`'s docstring wrong again")
    assert two_bursting >= trained.threshold, (
        f"two bursting cells scored {two_bursting:.4f}, below the model's own "
        f"operating point {trained.threshold:.5f}")


def test_one_bursting_cell_alone_does_not_fire(trained):
    """The bound is not absent, it is too weak — worth keeping the distinction.

    A single cell bursting is still rejected. What fails is the *step* from one
    cell to two, which the docstring claimed could not happen at all.
    """
    k = _kmin(trained)
    one = _peak(trained, {0: [AT + k * i for i in range(8)]})
    assert one < trained.threshold, (
        f"a single bursting cell scored {one:.4f} at threshold "
        f"{trained.threshold:.5f} — even the weak bound is gone")


def test_the_docstring_does_not_claim_an_exact_cap(trained):
    """Prose and behaviour in one file, so they cannot drift apart quietly."""
    from bugarach.learn.nets import build_tube

    doc = build_tube.__doc__ or ""
    assert "exact rather than soft" not in doc, (
        "the docstring claims an exact cap that the two tests above disprove")
    assert "NOT delivered" in doc, (
        "the docstring should say plainly that distinctness is not delivered")
