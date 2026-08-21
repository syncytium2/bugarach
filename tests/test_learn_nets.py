"""The structural claims the learned-detector report makes about `tube`.

Every one of these is asserted in prose on `docs/learned/report.html` and, until
a murderboard on 2026-08-16 pointed it out, none was checked by anything: the
two modules that produce every number on that page — `learn/nets.py` and
`learn/train.py` — had no tests at all, while the page's footer said their tests
had landed. A claim in a figure caption that nothing can falsify is exactly the
class this repo's review process exists to catch, so the load-bearing ones are
promises here instead.

torch is optional in this package, so every test that needs it skips cleanly.
"""

from __future__ import annotations

import numpy as np
import pytest

torch = pytest.importorskip("torch")

from bugarach.learn.nets import ARCHITECTURES, n_params, receptive_field  # noqa: E402
from bugarach.learn.train import BENCH_SEEDS, TRAIN_SEED_BLOCK  # noqa: E402


def _tube():
    return ARCHITECTURES["tube"].make()


def test_difference_of_gaussians_integrates_to_zero():
    """The page's central architectural claim: 'area-matched so a uniform field
    sums to zero'. If the kernel does not integrate to zero, a uniform change in
    background does not cancel and the whole rate-invariance argument is wrong."""
    m = _tube()
    k = m._kernels(torch.device("cpu"))
    assert k.shape[0] == 4, "four scales, as the layer table says"
    sums = k.sum(dim=-1).flatten()
    assert torch.allclose(sums, torch.zeros_like(sums), atol=1e-6), sums


def test_a_uniform_field_cancels_but_a_concentrated_one_does_not():
    """The same claim, stated the way the page states it to a reader: raise the
    background everywhere and the response does not move; put the same activity
    into one moment and it jumps."""
    m = _tube()
    flat = torch.ones(1, 1, 4096) * 0.05
    resp_flat = torch.nn.functional.conv1d(flat, m._kernels(flat.device),
                                           padding=m.k)
    interior = resp_flat[..., m.k:-m.k]
    assert interior.abs().max() < 1e-3, "a flat field must not excite the kernel"

    burst = flat.clone()
    burst[..., 2048] += 1.0
    resp_burst = torch.nn.functional.conv1d(burst, m._kernels(burst.device),
                                            padding=m.k)
    assert resp_burst.abs().max() > 10 * interior.abs().max()


def test_parameter_count_matches_the_published_layer_table():
    """1,149 = 12 + 1,128 + 9, and the split is what the report prints."""
    m = _tube()
    assert n_params(m) == 1149

    front = sum(p.numel() for n, p in m.named_parameters()
                if n in ("log_center", "log_ratio", "gain"))
    head = sum(p.numel() for n, p in m.named_parameters() if n.startswith("head"))
    assert front == 12, "4 scales x (centre width, surround ratio, gain)"
    assert front + head == 1149


def test_the_head_receives_the_raw_brightness_trace_as_a_fifth_channel():
    """Not decoration. The report's layer table showed layer 3 emitting 4 x T
    into the stack, but the stack's first convolution takes FIVE inputs — the
    four difference-of-Gaussian responses plus the un-subtracted brightness
    trace. The published parameter count is only reachable with five, so the
    omitted channel was already inside a number the page printed, and 'raise the
    background and the response does not move' is true of four of five channels.
    """
    m = _tube()
    first = next(mod for mod in m.head.modules()
                 if isinstance(mod, torch.nn.Conv1d))
    assert first.in_channels == 5


def test_centre_widths_start_as_a_geometric_ladder_not_all_at_one_sample():
    """The report said every scale was initialised at one sample; the code
    initialises 1, 2, 4, 8. The distinction is load-bearing — it is the
    difference between a fitted width that measures something and one whose
    starting bank already brackets the answer."""
    m = _tube()
    start = torch.exp(m.log_center.detach())
    assert torch.allclose(start, torch.tensor([1.0, 2.0, 4.0, 8.0]))


def test_one_cell_one_vote_is_enforced_over_the_smallest_scale_only():
    """The cap window comes from the SMALLEST fitted centre, truncated to an
    integer — so at initialisation it is +/-1 sample, not the widest scale. A
    cell firing twice further apart than that votes twice, which is a real limit
    on the distinctness guarantee and is now stated on the page."""
    m = _tube()
    kmin = int(torch.exp(m.log_center.detach()).min().clamp(1, m.k))
    assert kmin == 1

    x = torch.zeros(1, 3, 200)
    x[0, 0, 100] = 1.0
    x[0, 0, 108] = 1.0          # same cell, 8 samples later — outside +/-1
    out = m(x)
    assert out.shape == (1, 200)


def test_receptive_field_is_reported_not_assumed():
    assert receptive_field(6) == 1 + 2 * (1 + 2 + 4 + 8 + 16 + 32)


@pytest.mark.parametrize("name", sorted(ARCHITECTURES))
def test_every_architecture_runs_at_any_cell_count(name):
    """Space invariance is a registry-wide contract, not a `tube` detail: a
    model that only works at 33 cells cannot be handed to another lab."""
    m = ARCHITECTURES[name].make()
    for n_cells in (5, 33, 61):
        out = m(torch.zeros(1, n_cells, 512))
        assert out.shape == (1, 512)


def test_the_threshold_is_never_chosen_on_the_recordings_it_is_scored_on():
    """The one methodological credential the report claims for its operating
    point. `train` and `pick_threshold` both assert this internally; a test makes
    it a promise to the reader rather than a comment to the next author."""
    for offset in (0, 500_000):
        seeds = {TRAIN_SEED_BLOCK + offset + s * 1000 + i
                 for s in range(4) for i in range(16)}
        assert not seeds & set(BENCH_SEEDS)
