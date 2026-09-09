"""A saved model runs on a real folder from the command line.

The point of the checkpoint is not the file, it is this: `bugarach detect --model`
is a separate process from whatever fitted the weights, which is exactly what could
not happen before. `docs/pipeline.md`'s blocker list said so — *"cannot detect on
the user's folder, and cannot accept a model the user brings"*.

What these pin:

* a learned call lands in `detections.csv` in the SAME contract as the six, so
  every reader takes it without knowing the difference;
* it is scored inside each analysis window, the way the six are, and not once over
  the whole recording — otherwise the model gets context across a drug transition
  that no hand-written detector was given, and the difference lands in a
  comparison without appearing in it;
* `run.json` names the models, because a learned row is deliberately
  indistinguishable from a hand-written one in the detections file;
* a model whose name collides with one of the six is refused — that column is one
  namespace across both families.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "src"))

torch = pytest.importorskip("torch")

from bugarach.detect_folder import detect_folder  # noqa: E402
from bugarach.learn import checkpoint  # noqa: E402
from bugarach.learn.nets import ARCHITECTURES, n_params  # noqa: E402
from bugarach.learn.train import Trained  # noqa: E402

SLICES = "slice_id,frame_interval_sec,group_id\ns1,0.1,MALE\n"
REGIONS = ("slice_id,region_idx,label,start_sec,end_sec,"
           "analysis_start_sec,analysis_end_sec\n"
           "s1,1,baseline,0,300,0,300\n"
           "s1,2,drug,300,600,300,600\n")


def _folder(tmp_path: Path) -> Path:
    folder = tmp_path / "folder"
    folder.mkdir()
    (folder / "slices.csv").write_text(SLICES)
    (folder / "regions.csv").write_text(REGIONS)
    rows = ["roi,time_sec,stream"]
    for t in (50, 120, 200, 350, 420, 500):
        for roi in range(1, 10):
            rows.append(f"{roi},{t + roi * 0.02:.2f},fast")
    (folder / "s1.csv").write_text("\n".join(rows) + "\n")
    return folder


def _checkpoint(tmp_path: Path, *, name="tube", threshold=0.0) -> Path:
    """A real architecture with real weights at a threshold low enough to fire.

    Untrained on purpose: this file is about the checkpoint reaching detection,
    and training one would make the test minutes long and its assertions about
    that seed.
    """
    torch.manual_seed(0)
    model = ARCHITECTURES[name].make()
    tr = Trained(name=name, model=model, threshold=threshold,
                 n_params=n_params(model), dt=0.1, merge_gap_frames=20,
                 train_seconds=0.0, threads=1)
    return checkpoint.save(tr, tmp_path / f"{name}.json", trained_on="a_spec.json",
                           train_seed=0, steps=1)


def test_a_saved_model_detects_on_a_folder_in_the_six_ports_contract(tmp_path):
    folder = _folder(tmp_path)
    ckpt = _checkpoint(tmp_path)
    run = detect_folder(folder, out_dir=tmp_path / "out", detectors=("coact",),
                        models=(ckpt,))
    import csv

    rows = list(csv.DictReader(Path(run.paths["detections"]).open()))
    learned = [r for r in rows if r["detector"] == "tube"]
    assert learned, "the model made no call at threshold 0 — the wiring is not reached"
    one = learned[0]
    # the same columns as a hand-written call, filled the same way
    assert one["mode"] == "learned"
    assert one["strength_unit"] == "score threshold"
    assert one["slice_id"] == "s1" and one["stream"] == "fast"
    assert set(rows[0]) == set(one), "a learned row must not have its own columns"


def test_it_is_scored_inside_each_window_not_once_over_the_recording(tmp_path):
    """The six are run per analysis window; a model that saw the whole recording
    would be judged against a background no other detector was given."""
    folder = _folder(tmp_path)
    ckpt = _checkpoint(tmp_path)
    run = detect_folder(folder, out_dir=tmp_path / "out", detectors=(),
                        models=(ckpt,))
    import csv

    rows = list(csv.DictReader(Path(run.paths["detections"]).open()))
    labels = {r["region_label"] for r in rows}
    assert labels == {"baseline", "drug"}, labels
    # every call carries the region it was made in, as the six do
    assert all(r["region_idx"] in ("1", "2") for r in rows)


def test_run_json_names_the_models_that_ran(tmp_path):
    folder = _folder(tmp_path)
    ckpt = _checkpoint(tmp_path)
    run = detect_folder(folder, out_dir=tmp_path / "out", detectors=("coact",),
                        models=(ckpt,))
    got = json.loads(Path(run.paths["run"]).read_text())
    assert got["models"] and got["models"][0]["arch"] == "tube"
    assert got["models"][0]["file"] == str(ckpt)
    # and with none, null keeps meaning "the six alone"
    bare = json.loads(Path(detect_folder(
        folder, out_dir=tmp_path / "bare", detectors=("coact",)
    ).paths["run"]).read_text())
    assert bare["models"] is None


def test_a_model_named_like_a_detector_is_refused(tmp_path):
    """`detections.csv`'s detector column is one namespace across both families."""
    folder = _folder(tmp_path)
    ckpt = _checkpoint(tmp_path)
    doc = json.loads(ckpt.read_text())
    doc["arch"] = "tube"
    ckpt.write_text(json.dumps(doc))
    # rename the registry entry's key by faking a collision through the loader
    import bugarach.detect_folder as df

    original = df.DETECTORS
    try:
        df.DETECTORS = original + ("tube",)
        with pytest.raises(ValueError, match="collide"):
            detect_folder(folder, out_dir=tmp_path / "out", detectors=("coact",),
                          models=(ckpt,))
    finally:
        df.DETECTORS = original


def test_a_broken_checkpoint_fails_before_the_folder_is_walked(tmp_path):
    folder = _folder(tmp_path)
    ckpt = _checkpoint(tmp_path)
    doc = json.loads(ckpt.read_text())
    doc["arch"] = "not_a_registered_net"
    ckpt.write_text(json.dumps(doc))
    out = tmp_path / "out"
    with pytest.raises(ValueError, match="not registered"):
        detect_folder(folder, out_dir=out, detectors=("coact",), models=(ckpt,))
    assert not (out / "detections.csv").exists()
