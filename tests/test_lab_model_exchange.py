"""Weights cross between the command line and the browser, in both directions.

`/api/export_model` hands a fitted model out as a checkpoint the page can download;
`/api/import_model` takes one back and returns a handle `/api/detect` already
accepts. Together with `bugarach detect --model`, that is the round trip:

    CLI trains → saves JSON → browser imports → runs on the user's folder
    browser trains → exports JSON → CLI runs it with `detect --model`

**This does not reopen the question `Store.get` closed.** That refusal — models
*"live in this process and do not survive a restart, which is deliberate: a fitted
model cached on disk outlives the settings that produced it"* — is about a cache the
server keeps behind the user's back, and nothing here writes one. Handing the
weights to the person who fitted them, stamped with what fitted them, is the
opposite case.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "src"))

torch = pytest.importorskip("torch")

from bugarach import lab as lab_mod  # noqa: E402
from bugarach.learn import checkpoint  # noqa: E402
from bugarach.learn.nets import ARCHITECTURES, n_params  # noqa: E402
from bugarach.learn.train import Trained  # noqa: E402


class _Handler:
    """The two routes under test, without a socket.

    They are plain request/response — no chunked stream, no progress — so calling
    them directly tests the same code the server dispatches to, and a socket would
    only add a way for this to fail for reasons that are not the subject.
    """

    def __init__(self, lab):
        self.lab = lab

    _export_model = lab_mod.LabHandler._export_model
    _import_model = lab_mod.LabHandler._import_model


def _trained(name="tube", threshold=0.87):
    torch.manual_seed(0)
    model = ARCHITECTURES[name].make()
    return Trained(name=name, model=model, threshold=threshold,
                   n_params=n_params(model), dt=0.1, merge_gap_frames=20,
                   train_seconds=1.5, threads=1)


def _lab_with_a_model():
    lab = lab_mod.Lab(trainer=lab_mod.StubTrainer())
    tr = _trained()
    lab.put(lab_mod.Model(
        handle="", arch=tr.name, threshold=tr.threshold, dt=tr.dt,
        n_params=tr.n_params, trainer="test",
        predict=lambda *a, **k: None,
        report={"_trained": tr, "steps": 900}))
    return lab, tr


def test_a_fitted_model_exports_as_a_loadable_checkpoint(tmp_path):
    lab, tr = _lab_with_a_model()
    got = _Handler(lab)._export_model(
        {"model": "m1", "trained_on": "spec.json", "train_seed": 3})
    assert got["arch"] == "tube"
    doc = got["checkpoint"]
    assert doc["format"] == "bugarach.learned-model"
    assert doc["provenance"]["trained_on"] == "spec.json"
    assert doc["provenance"]["steps"] == 900
    # and it is a file the CLI's own loader takes
    p = tmp_path / "m.json"
    p.write_text(json.dumps(doc))
    back = checkpoint.load(p)
    assert back.name == "tube" and back.threshold == pytest.approx(tr.threshold)


def test_an_exported_model_imports_back_and_is_runnable():
    """The round trip inside one server, which is the cheap half of the claim."""
    lab, tr = _lab_with_a_model()
    h = _Handler(lab)
    doc = h._export_model({"model": "m1"})["checkpoint"]
    got = h._import_model({"checkpoint": doc})
    assert got["model"] != "m1", "an import is a new handle, not a mutation"
    imported = lab.get(got["model"])
    assert imported.arch == "tube"
    assert imported.threshold == pytest.approx(tr.threshold)
    assert imported.report["imported"] is True
    # the handle `/api/detect` wants is present and carries a runnable model
    assert imported.report["_trained"].name == "tube"


def test_a_cli_written_checkpoint_imports(tmp_path):
    """The direction that matters: weights fitted outside the browser, run inside."""
    p = checkpoint.save(_trained(), tmp_path / "from_cli.json",
                        trained_on="generator_spec.json", train_seed=0, steps=900)
    lab = lab_mod.Lab(trainer=lab_mod.StubTrainer())
    got = _Handler(lab)._import_model(
        {"checkpoint": json.loads(p.read_text())})
    assert lab.get(got["model"]).report["provenance"]["trained_on"] \
        == "generator_spec.json"


def test_a_bad_checkpoint_is_a_bad_request_not_a_crash(tmp_path):
    lab = lab_mod.Lab(trainer=lab_mod.StubTrainer())
    p = checkpoint.save(_trained(), tmp_path / "m.json", trained_on="x")
    doc = json.loads(p.read_text())
    doc["arch"] = "not_a_registered_net"
    with pytest.raises(lab_mod.BadRequest, match="not a model this server can run"):
        _Handler(lab)._import_model({"checkpoint": doc})


def test_a_string_body_is_refused_with_the_fix_named():
    lab = lab_mod.Lab(trainer=lab_mod.StubTrainer())
    with pytest.raises(lab_mod.BadRequest, match="JSON.parse"):
        _Handler(lab)._import_model({"checkpoint": "{\"format\": \"...\"}"})


def test_exporting_a_model_with_no_weights_says_so():
    """The stub trainer fits nothing; asking it for weights must not 500."""
    lab = lab_mod.Lab(trainer=lab_mod.StubTrainer())
    lab.put(lab_mod.Model(handle="", arch="tube", threshold=0.5, dt=0.1,
                          n_params=0, trainer="stub", predict=None, report={}))
    with pytest.raises(lab_mod.BadRequest, match="no weights to export"):
        _Handler(lab)._export_model({"model": "m1"})
