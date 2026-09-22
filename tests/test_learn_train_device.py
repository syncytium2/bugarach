"""`train(device=...)`: the CPU default does not move, and a GPU fit repeats itself.

The option exists because on WSMIP064 an RTX A4000 fits an untuned `chorus_norm` in 6.4 s
against 244 s on one CPU process (`docs/windows_workstation_setup.md`). Two guarantees
make it safe to add to training code every published number came from:

* **Not asking for a device changes nothing.** Every existing caller passes no ``device``;
  their weights, threshold and training record must be what they were.
* **A GPU fit is repeatable.** A tuning run resumes after a crash by rerunning the fits that
  had not finished, so a rerun must be the fit it replaces. cuDNN and cuBLAS do not promise
  that by default; `train.deterministic_cuda` does, and this checks it on the weights.

The GPU tests skip where torch sees no CUDA device, which includes CI.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np
import pytest

torch = pytest.importorskip("torch")

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / "tools"))

from fair_bakeoff import _make_recording  # noqa: E402

from bugarach.learn import checkpoint  # noqa: E402
from bugarach.learn.train import fold_maker, train  # noqa: E402

SPEC = json.loads((REPO / "docs/learned/generator_spec.json").read_text())["generator"]
_CACHE: dict = {}

needs_cuda = pytest.mark.skipif(not torch.cuda.is_available(), reason="no CUDA device")


def _rec(seed):
    if seed not in _CACHE:
        _CACHE[seed] = _make_recording(SPEC, seed)
    return _CACHE[seed]


def _fit(**kw):
    mk, n_fit, _ = fold_maker(_rec, [1000, 1001, 1002])
    return train("tube", mk, n_train=n_fit, steps=25, crop=1024, batch=2, lr=1e-2, seed=0, **kw)


def _weights(tr):
    return {k: v.detach().cpu().numpy() for k, v in tr.model.state_dict().items()}


def _same(a, b):
    return a.keys() == b.keys() and all(np.array_equal(a[k], b[k]) for k in a)


def test_no_device_trains_on_the_cpu_exactly_as_before():
    default, explicit = _fit(), _fit(device="cpu")
    assert _same(_weights(default), _weights(explicit))
    assert default.threshold == explicit.threshold
    assert "device" not in default.training, \
        "a CPU fit's record must stay byte-identical to one from before the option"
    assert explicit.training["device"] == "cpu"


@needs_cuda
def test_a_gpu_fit_repeated_with_the_same_seed_gives_the_same_weights():
    a, b = _fit(device="cuda"), _fit(device="cuda")
    assert _same(_weights(a), _weights(b)), "a rerun GPU fit is not the fit it replaces"
    assert a.threshold == b.threshold
    assert a.training["device"].startswith("cuda")
    assert a.training["deterministic_algorithms"] is True
    assert a.training["gpu"] and a.training["cuda_version"]


@needs_cuda
def test_a_gpu_fit_scores_and_saves_like_a_cpu_one(tmp_path):
    tr = _fit(device="cuda")
    assert next(tr.model.parameters()).device.type == "cuda"
    sl, _ = _rec(1002)
    dets, enc = tr.predict(sl)                    # input goes to the model's device and back
    assert len(dets.score) == enc.n_frame and np.all(np.isfinite(dets.score))
    path = tmp_path / "fit.json"
    checkpoint.save(tr, path, train_seed=0, steps=25)
    reloaded = checkpoint.load(path)              # rebuilt on the CPU from the saved floats
    got = {k: v.numpy() for k, v in reloaded.model.state_dict().items()}
    assert _same(got, _weights(tr))
    cpu_key = checkpoint.config_key("tube", tr.cfg, _fit().training)
    assert json.loads(path.read_text())["config_key"] == cpu_key, \
        "the device must not change which configuration a fit belongs to"
