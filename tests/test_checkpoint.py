"""A trained model survives its process, or it is refused for a named reason.

The round trip is the easy half. What these mostly pin is the refusals, because a
checkpoint's characteristic failure is that the FILE outlives an edit to the code
that made it — and a model which half-loads and then scores is worse than one that
will not open.

* identical predictions after a reload, on the same recording, to float equality —
  anything looser would not notice a tensor loaded into the wrong slot;
* the config travels, so moving a registry default does not silently rebuild a
  different network under old weights;
* a shape that no longer matches is refused with **both** shapes named;
* a changed encoding contract is refused, because the weights are a function of the
  raster the model was shown;
* `peek` reads provenance **without torch**, so a report tool need not build a net;
* the file is JSON and contains no pickle, which is what makes it loadable from the
  browser and safe to accept from a stranger.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np
import pytest

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "src"))

torch = pytest.importorskip("torch")

from bugarach.learn import checkpoint  # noqa: E402
from bugarach.learn.nets import ARCHITECTURES, n_params  # noqa: E402
from bugarach.learn.train import Trained  # noqa: E402

ARCH = "tube"


def _trained(seed=0):
    """A model with real weights, untrained — the checkpoint does not care which,
    and training one per test would make these minutes instead of milliseconds."""
    torch.manual_seed(seed)
    model = ARCHITECTURES[ARCH].make()
    return Trained(name=ARCH, model=model, threshold=0.9838,
                   n_params=n_params(model), dt=0.1, merge_gap_frames=20,
                   train_seconds=6.6, threads=1)


def _raster(n_roi=24, n_frame=600, seed=3):
    rng = np.random.RandomState(seed)
    x = np.zeros((n_roi, n_frame), dtype=np.float32)
    x[rng.rand(n_roi, n_frame) < 0.01] = 1.0
    x[:5, n_frame // 2] = 1.0
    return torch.from_numpy(x).unsqueeze(0)


def _score(tr, x):
    with torch.no_grad():
        return tr.model(x).squeeze(0).numpy()


def test_a_reloaded_model_predicts_identically(tmp_path):
    tr = _trained()
    x = _raster()
    before = _score(tr, x)
    checkpoint.save(tr, tmp_path / "m.json", trained_on="spec.json", train_seed=0)
    back = checkpoint.load(tmp_path / "m.json")
    np.testing.assert_array_equal(before, _score(back, x))
    assert (back.threshold, back.dt, back.merge_gap_frames) == (0.9838, 0.1, 20)
    assert back.n_params == tr.n_params


def test_the_operating_point_and_provenance_travel(tmp_path):
    tr = _trained()
    checkpoint.save(tr, tmp_path / "m.json", trained_on="generator_spec.json",
                    train_seed=7, steps=900, n_fit=6, n_threshold_val=2)
    meta = checkpoint.peek(tmp_path / "m.json")
    assert meta["provenance"]["trained_on"] == "generator_spec.json"
    assert meta["provenance"]["train_seed"] == 7
    assert meta["provenance"]["steps"] == 900
    assert meta["provenance"]["threads"] == 1, "reduction order is a condition of the number"
    assert meta["operating_point"]["threshold"] == 0.9838


def test_the_config_travels_so_a_moved_default_cannot_rebuild_another_model(tmp_path):
    """The file records what it WAS, not what the name means now."""
    tr = _trained()
    checkpoint.save(tr, tmp_path / "m.json", trained_on="x")
    doc = json.loads((tmp_path / "m.json").read_text())
    assert doc["cfg"] == dict(ARCHITECTURES[ARCH].cfg)
    assert doc["cfg"], "an empty cfg would make this guarantee vacuous"


def test_a_changed_shape_is_refused_with_both_shapes_named(tmp_path):
    tr = _trained()
    p = tmp_path / "m.json"
    checkpoint.save(tr, p, trained_on="x")
    doc = json.loads(p.read_text())
    key = next(k for k, v in doc["state_dict"].items() if len(v["shape"]) == 1)
    doc["state_dict"][key]["shape"] = [len(doc["state_dict"][key]["data"]) + 1]
    doc["state_dict"][key]["data"].append(0.0)
    p.write_text(json.dumps(doc))
    with pytest.raises(ValueError, match="wants"):
        checkpoint.load(p)


def test_a_missing_tensor_is_refused_rather_than_half_loaded(tmp_path):
    tr = _trained()
    p = tmp_path / "m.json"
    checkpoint.save(tr, p, trained_on="x")
    doc = json.loads(p.read_text())
    doc["state_dict"].pop(next(iter(doc["state_dict"])))
    p.write_text(json.dumps(doc))
    with pytest.raises(ValueError, match="missing"):
        checkpoint.load(p)


def test_a_changed_encoding_contract_is_refused(tmp_path):
    """Weights are a function of the raster the model was shown."""
    tr = _trained()
    p = tmp_path / "m.json"
    checkpoint.save(tr, p, trained_on="x")
    doc = json.loads(p.read_text())
    doc["encoding"]["row_order"] = "original ROI index"
    p.write_text(json.dumps(doc))
    with pytest.raises(ValueError, match="different encoding contract"):
        checkpoint.load(p)


def test_an_unregistered_architecture_says_how_to_register_it(tmp_path):
    tr = _trained()
    p = tmp_path / "m.json"
    checkpoint.save(tr, p, trained_on="x")
    doc = json.loads(p.read_text())
    doc["arch"] = "not_a_net"
    p.write_text(json.dumps(doc))
    with pytest.raises(ValueError, match="not registered"):
        checkpoint.load(p)


def test_the_file_is_json_and_holds_no_pickle(tmp_path):
    """The point of the format: a model can be read by the browser, and opening a
    stranger's model cannot execute their code."""
    tr = _trained()
    p = tmp_path / "m.json"
    checkpoint.save(tr, p, trained_on="x")
    raw = p.read_bytes()
    assert raw.lstrip()[:1] == b"{"
    # pickle protocol markers that a torch.save payload would carry
    assert b"\x80\x02" not in raw and b"PK\x03\x04" not in raw
    doc = json.loads(raw)                       # parses with the stdlib alone
    assert doc["format"] == "bugarach.learned-model"
    flat = doc["state_dict"][next(iter(doc["state_dict"]))]["data"]
    assert all(isinstance(v, float) for v in flat)


def test_peek_needs_no_torch(tmp_path, monkeypatch):
    """A listing of models must not have to instantiate them."""
    tr = _trained()
    p = tmp_path / "m.json"
    checkpoint.save(tr, p, trained_on="x", note="hello")
    monkeypatch.setitem(sys.modules, "torch", None)   # any use would raise
    meta = checkpoint.peek(p)
    assert meta["arch"] == ARCH and meta["provenance"]["note"] == "hello"
    assert "state_dict" not in meta


def test_a_file_that_is_not_a_model_says_so(tmp_path):
    p = tmp_path / "nope.json"
    p.write_text(json.dumps({"format": "something-else"}))
    with pytest.raises(ValueError, match="not a bugarach model"):
        checkpoint.peek(p)
    with pytest.raises(ValueError, match="not a bugarach model"):
        checkpoint.load(p)
