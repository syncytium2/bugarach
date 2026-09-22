"""What `line`'s vote bounds, and what `line_bound`'s adds — measured, not asserted.

`line`'s docstring used to say one ROI casts at most one vote. The sigmoid bounds the
vote's height; the difference-of-Gaussians centre that reads it averages over time, so a
burst still reaches it as more than one onset. `line_bound` bounds the local mass the
centre reads. These tests pin both behaviours on untrained models with the smear widths
set by hand: the ladder the models start from, and the widths one fitted `tube` reached
(2.3–5.3 frames), which is the regime the report's reviewer measured in.
"""

import pytest

torch = pytest.importorskip("torch")

from bugarach.learn.nets import ARCHITECTURES, n_params  # noqa: E402

WIDTHS = ([1.0, 2.0, 4.0, 8.0], [2.3, 3.0, 4.3, 5.3])
BURST = [500, 502, 504, 506]
"""Four onsets two frames apart — the burst `tools/probe_line_vs_fuzz.py` plants."""


def _model(name, widths):
    torch.manual_seed(0)
    m = ARCHITECTURES[name].make().eval()
    with torch.no_grad():
        m.log_smear.copy_(torch.log(torch.tensor(widths)))
    return m


def _peak_centre_mass(m, frames):
    """Per scale, the largest value the difference-of-Gaussians centre reads from one ROI,
    with the empty-field floor removed so a silent frame reads 0 for both models."""
    x = torch.zeros(1, 1, 1024)
    x[0, 0, frames] = 1.0
    with torch.no_grad():
        sm = torch.nn.functional.conv1d(x, m._smear(x.device), padding=m.k)
        vote = m._vote(sm)
        if m.bound_vote:
            mass = torch.nn.functional.conv1d(vote, m._centre(x.device), padding=m.k,
                                              groups=vote.shape[1])
            vote = vote * (m._one_onset_mass(x.device).view(1, -1, 1)
                           / mass.clamp_min(1e-6)).clamp(max=1.0)
        else:
            vote = vote - torch.sigmoid(-m.vote_gain * m.vote_bias).view(1, -1, 1)
        return torch.nn.functional.conv1d(vote, m._centre(x.device), padding=m.k,
                                          groups=vote.shape[1]).amax(dim=2).squeeze(0)


@pytest.mark.parametrize("widths", WIDTHS)
def test_line_caps_the_vote_height_but_a_burst_still_reads_as_more_than_one_onset(widths):
    m = _model("line", widths)
    ratio = _peak_centre_mass(m, BURST) / _peak_centre_mass(m, [500])
    # Measured 2026-09-16: 2.14/1.92/1.71/1.62 on the ladder, 1.28/1.54/1.66/1.77 fitted.
    assert float(ratio.max()) > 1.5, ratio


@pytest.mark.parametrize("widths", WIDTHS)
def test_line_bound_holds_a_burst_near_one_onset(widths):
    m = _model("line_bound", widths)
    ratio = _peak_centre_mass(m, BURST) / _peak_centre_mass(m, [500])
    # Measured 2026-09-16: 1.11/1.15/1.13/1.12 and 1.04/1.13/1.14/1.08. Soft, as documented.
    assert float(ratio.max()) < 1.2, ratio
    assert float(ratio.min()) >= 1.0 - 1e-6, ratio


def test_a_lone_onset_is_never_scaled_by_the_bound():
    m = _model("line_bound", WIDTHS[1])
    one = _peak_centre_mass(m, [500])
    assert torch.allclose(one, m._one_onset_mass(torch.device("cpu")), rtol=1e-5)


def test_on_an_empty_field_line_counts_its_floor_and_line_bound_counts_nothing():
    x = torch.zeros(1, 32, 1024)
    for name, expect_zero in (("line", False), ("line_bound", True)):
        m = _model(name, WIDTHS[0])
        with torch.no_grad():
            sm = torch.nn.functional.conv1d(x.reshape(32, 1, 1024), m._smear(x.device),
                                            padding=m.k)
            count = m._vote(sm).reshape(1, 32, -1, 1024).mean(dim=1)[0, :, 512]
        assert bool((count == 0).all()) is expect_zero, (name, count)


def test_the_bound_adds_no_parameters_so_the_comparison_is_the_mechanism_alone():
    assert n_params(ARCHITECTURES["line"].make()) == n_params(ARCHITECTURES["line_bound"].make())
