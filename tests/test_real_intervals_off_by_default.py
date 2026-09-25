"""ADR-0010 (Proposed) part 2 is off by default: every bench recording is byte-identical to before.

The empirical-gap placement (``simulate_coordination(gap_source=..., gap_mix=...)``) was added on
2026-09-25 as preparation only. With neither option set, every recording every bench module makes
must be exactly what it was, including the order in which the random generator is consumed, or
every published score would move for a change nobody switched on.

The hashes below were computed on ``origin/main`` at 538ae74, before the generator changed, and
pinned here. Each covers every ROI's onsets and widths on every stream, every planted event
(time, participation, members, onsets), every decoy, and the ground truth's ``params``. The floor
is switched off (``BUGARACH_BENCH_FLOOR=off``) only to keep the test fast: it is computed from the
recording afterwards and draws nothing from the recording's generator.

To re-pin after a deliberate change to the bench, run this file's ``_print_hashes()`` and say in
the commit why the recordings moved.
"""
from __future__ import annotations

import hashlib

import numpy as np
import pytest

from bugarach import bench, bench_combined, bench_slow
from bugarach.simulate import simulate_coordination

MODULES = {"fast": bench, "slow": bench_slow, "combined": bench_combined}
SEEDS = (1, 7)


def _h(h, a) -> None:
    # Rounded to 1e-9 s so a last-place difference between platforms' maths libraries cannot
    # redden CI; a moved event or a changed draw moves far more than that.
    h.update(np.round(np.asarray(a, dtype=np.float64), 9).tobytes())
    h.update(b"|")


def recording_hash(pair) -> str:
    s, gt = pair
    h = hashlib.sha256()
    for name in sorted(s.streams):
        st = s.streams[name]
        h.update(name.encode())
        for field in (st.locs, st.width):
            for v in field:
                _h(h, v)
    for group in (gt.events, gt.distractors):
        h.update(b"#")
        for e in group:
            _h(h, [e.time, e.frac, e.n_part, e.jitter_sec])
            _h(h, e.rois)
            _h(h, e.onsets)
            h.update(e.kind.encode())
    params = {k: v for k, v in gt.params.items() if not k.startswith("event_floor")}
    h.update(repr(sorted(params.items())).encode())
    return h.hexdigest()[:24]


def _makers():
    """Every maker on every bench, at both regime endpoints where it takes one."""
    out = {}
    for bench_name, m in MODULES.items():
        for regime in ("baseline_quiet", "baseline_busy"):
            for kind in ("make_recording", "make_tail_recording", "make_crowded_recording",
                         "make_elevated_rate_recording"):
                out[f"{bench_name}:{kind}:{regime}"] = (
                    lambda seed, m=m, kind=kind, regime=regime: getattr(m, kind)(regime, seed))
        out[f"{bench_name}:make_null_recording"] = (
            lambda seed, m=m: m.make_null_recording(seed))
    # The route chorus's training recordings take (`tools/fair_bakeoff.py:_make_recording`): the
    # generator called directly with a recording dict, no floor.
    out["simulate:BENCH_RECORDING"] = lambda seed: simulate_coordination(
        seed=seed, **bench.BENCH_RECORDING)
    out["simulate:uniform"] = lambda seed: simulate_coordination(
        seed=seed, spacing="uniform", duration_sec=900.0)
    out["simulate:defaults"] = lambda seed: simulate_coordination(seed=seed)
    return out


PINNED = {
    "fast:make_recording:baseline_quiet@1": "918772e20da1a168d1ab1771",
    "fast:make_recording:baseline_quiet@7": "1094e53a5f551d13de274839",
    "fast:make_tail_recording:baseline_quiet@1": "c9712bec56e1d43e211ea6b7",
    "fast:make_tail_recording:baseline_quiet@7": "524f6fb7f086e9942560155c",
    "fast:make_crowded_recording:baseline_quiet@1": "edfa8a58ab5c689e18ba4e2f",
    "fast:make_crowded_recording:baseline_quiet@7": "05dd3f7fea8e8fb9ff4b3f0d",
    "fast:make_elevated_rate_recording:baseline_quiet@1": "b227780c344b9fb587b17806",
    "fast:make_elevated_rate_recording:baseline_quiet@7": "42dd750c1ae4cd3b8cecff48",
    "fast:make_recording:baseline_busy@1": "cd5494ab12d8df08f81c1952",
    "fast:make_recording:baseline_busy@7": "4cfeaba5a1740c3525cfd138",
    "fast:make_tail_recording:baseline_busy@1": "6edcc240faaeb7eb7275d105",
    "fast:make_tail_recording:baseline_busy@7": "3a49847f75fb3e43733b217e",
    "fast:make_crowded_recording:baseline_busy@1": "16b765ed8296869f90a96a8b",
    "fast:make_crowded_recording:baseline_busy@7": "5392b29e42c10a88e4de84bb",
    "fast:make_elevated_rate_recording:baseline_busy@1": "a669e8fa79c49cd4f5cbf284",
    "fast:make_elevated_rate_recording:baseline_busy@7": "72d99d7b7c7e2ab546056d5d",
    "fast:make_null_recording@1": "1f72787a04384e0ce44abc8c",
    "fast:make_null_recording@7": "67ab96dae5d9b51da3bf4b49",
    "slow:make_recording:baseline_quiet@1": "74e61565b42d2e31fdf77385",
    "slow:make_recording:baseline_quiet@7": "80167d42fb74c01fcbb8e46b",
    "slow:make_tail_recording:baseline_quiet@1": "e40e4cbc26c023832ec42b6c",
    "slow:make_tail_recording:baseline_quiet@7": "42c33791ffc1c7ac37543df5",
    "slow:make_crowded_recording:baseline_quiet@1": "4154a588e2c650243683bff2",
    "slow:make_crowded_recording:baseline_quiet@7": "e01bee9495340ddba77bc8c4",
    "slow:make_elevated_rate_recording:baseline_quiet@1": "e658f83ab1f8d61fe241b103",
    "slow:make_elevated_rate_recording:baseline_quiet@7": "b7ae7b159f8b5771d1c7c5f4",
    "slow:make_recording:baseline_busy@1": "f50f985bfec7d4902a0133b3",
    "slow:make_recording:baseline_busy@7": "3ce7366e280e6d4fcec2e437",
    "slow:make_tail_recording:baseline_busy@1": "55f8532fe6a62cb95642ecfb",
    "slow:make_tail_recording:baseline_busy@7": "6b916a5dc2f0f3392fb30902",
    "slow:make_crowded_recording:baseline_busy@1": "a266bcf956697be1d74e0992",
    "slow:make_crowded_recording:baseline_busy@7": "db8e8048a11e9e07ee75e41d",
    "slow:make_elevated_rate_recording:baseline_busy@1": "09e3e1756143e7ac39d54667",
    "slow:make_elevated_rate_recording:baseline_busy@7": "7097d1e8671794a851f0c751",
    "slow:make_null_recording@1": "9ad82b18d1bad98033dae702",
    "slow:make_null_recording@7": "e0c5b4c3faf3f128d733bb00",
    "combined:make_recording:baseline_quiet@1": "21df7640c3e3d300d3c92a02",
    "combined:make_recording:baseline_quiet@7": "fda24fe3850c13632b824b09",
    "combined:make_tail_recording:baseline_quiet@1": "e0c8e8d73f755385a747dc76",
    "combined:make_tail_recording:baseline_quiet@7": "b8f10133d490ebabeab31f74",
    "combined:make_crowded_recording:baseline_quiet@1": "aecf42ddecbf116f9a9019f7",
    "combined:make_crowded_recording:baseline_quiet@7": "7f248f043bb3226cfede8f71",
    "combined:make_elevated_rate_recording:baseline_quiet@1": "6490efb82adc37c03422b23e",
    "combined:make_elevated_rate_recording:baseline_quiet@7": "40992b2ac94be0f6a79b961e",
    "combined:make_recording:baseline_busy@1": "cf7b7dd1b88a96eb033f7714",
    "combined:make_recording:baseline_busy@7": "6061f290221444f1e0e93f52",
    "combined:make_tail_recording:baseline_busy@1": "66bba4feb52607a17efab4c9",
    "combined:make_tail_recording:baseline_busy@7": "9a71ea6ca98c870847eac16e",
    "combined:make_crowded_recording:baseline_busy@1": "3ea117750502372ee2d6dd84",
    "combined:make_crowded_recording:baseline_busy@7": "b29422f7a7ed2d58c3c4c6fc",
    "combined:make_elevated_rate_recording:baseline_busy@1": "7a79e82b8b8f79c4c349ff32",
    "combined:make_elevated_rate_recording:baseline_busy@7": "4eb456ef5df62947a2fc332b",
    "combined:make_null_recording@1": "d36323e4f4ed416dcd2ceb0e",
    "combined:make_null_recording@7": "59376dc4c763dcfb8e829ee7",
    "simulate:BENCH_RECORDING@1": "02a6953fa586a309d4b1ad3e",
    "simulate:BENCH_RECORDING@7": "1d0e562f9f32e7edab42053a",
    "simulate:uniform@1": "f556aa170a39967b6207118c",
    "simulate:uniform@7": "980e932aac03c8cd82e9e9a5",
    "simulate:defaults@1": "4d32dd3cb238c7c55b6d59bf",
    "simulate:defaults@7": "05d61f4f286fce5762723c15",
}


def _print_hashes() -> None:
    import os

    os.environ[bench.FLOOR_SWITCH_ENV] = "off"
    for key, make in _makers().items():
        for seed in SEEDS:
            print(f'    "{key}@{seed}": "{recording_hash(make(seed))}",')


@pytest.fixture(autouse=True)
def _no_floor(monkeypatch):
    monkeypatch.setenv(bench.FLOOR_SWITCH_ENV, "off")


@pytest.mark.parametrize("key", sorted(_makers()))
def test_every_bench_recording_is_unchanged_with_the_new_options_unset(key):
    make = _makers()[key]
    for seed in SEEDS:
        assert recording_hash(make(seed)) == PINNED[f"{key}@{seed}"], (
            f"{key} seed {seed} moved: with gap_source unset and gap_mix at 1.0, the recording "
            "must be byte-identical to origin/main 538ae74")


if __name__ == "__main__":
    _print_hashes()
