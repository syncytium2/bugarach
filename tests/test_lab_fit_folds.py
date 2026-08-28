"""`/api/fit_folds` — the route that lets a learned row join the six's table.

The scoreboard scores the six on the corpus the page has open, split by the
page's own `tunePlan`. `/api/train` generates its own corpus and splits it with
`bench.fold_split`. Two corpora and two splits, so the page says in terms that
the learned detector cannot be in that table — and it is right to refuse rather
than fake it.

This route inverts the direction: the page sends the corpus **and** the fold
assignment, the server fits and predicts, and the page scores everything through
the one scorer it already ran the six through. So what these tests check is not
"does it train" — `test_lab_server.py` covers that — but the properties that make
the resulting table a comparison:

- the scored recordings are unreachable from the fit,
- a fold that overlaps is refused rather than reported,
- the server returns **detections and never a score**, because a second scorer is
  how the two halves of a comparison end up on different metrics.

Driven through a real socket with the stub trainer, so the transport, the refusals
and the framing are checked on a machine with no torch.
"""

from __future__ import annotations

import json
import threading
import urllib.request

import pytest

from bugarach import lab as lab_mod


def _rec(slice_id: str, *, n_roi: int = 6, n_event: int = 3, t0: float = 5.0):
    """A recording in the page's shape: per-ROI onsets, plus planted events.

    The events carry `onsets` — the participant times actually written into the
    trains — because that is what `frame_targets` labels across. See
    `truth_from_request`.
    """
    rois, events = [[] for _ in range(n_roi)], []
    for k in range(n_event):
        t = t0 + 40.0 * k
        onsets = [t + 0.1 * j for j in range(3)]
        for j, r in enumerate(range(3)):
            rois[r].append(onsets[j])
        events.append(dict(time=t, onsets=onsets, rois=[0, 1, 2],
                           frac=0.5, jitter_sec=0.1))
    for r in range(n_roi):                       # a little background everywhere
        rois[r].extend([2.0 + 17.0 * i + r for i in range(4)])
        rois[r].sort()
    return dict(slice_id=slice_id, rois=rois, frame_interval_sec=0.1,
                truth=dict(events=events))


def _post(port, body, path="/api/fit_folds"):
    req = urllib.request.Request(
        f"http://127.0.0.1:{port}{path}", data=json.dumps(body).encode(),
        headers={"content-type": "application/json"})
    out = {"progress": [], "result": None, "error": None}
    for raw in urllib.request.urlopen(req):
        msg = json.loads(raw)
        if msg["event"] == "progress":
            out["progress"].append(msg)
        elif msg["event"] == "result":
            out["result"] = msg
        else:
            out["error"] = msg["message"]
    return out


@pytest.fixture()
def server():
    httpd = lab_mod.make_server(port=0, trainer=lab_mod.StubTrainer(), quiet=True)
    t = threading.Thread(target=httpd.serve_forever, daemon=True)
    t.start()
    yield httpd.server_address[1]
    httpd.shutdown()
    httpd.server_close()


CORPUS = [_rec("a"), _rec("b"), _rec("c"), _rec("d")]
FOLDS = [dict(train=[0, 1, 2], test=[3]), dict(train=[1, 2, 3], test=[0])]


def test_it_returns_detections_for_every_scored_recording(server):
    got = _post(server, dict(recordings=CORPUS, archs=["tube"], folds=FOLDS))
    assert got["error"] is None, got["error"]
    per_fold = got["result"]["per_arch"]["tube"]
    assert len(per_fold) == 2
    for f, spec in zip(per_fold, FOLDS):
        assert [d["index"] for d in f["detections"]] == spec["test"]
        assert f["test_idx"] == spec["test"] and f["train_idx"] == spec["train"]


def test_it_returns_no_score(server):
    """The page pools these through the scorer the six went through.

    A score computed here would be a second scorer, which is precisely how this
    project once put the two halves of one comparison on different metrics —
    `bench.pool_scores`' docstring records it.
    """
    got = _post(server, dict(recordings=CORPUS, archs=["tube"], folds=FOLDS))
    blob = json.dumps(got["result"])
    for scoreish in ("f1", "recall", "precision", "n_hit"):
        assert f'"{scoreish}"' not in blob, f"the route computed {scoreish}"


def test_a_fold_that_scores_what_it_trained_on_is_refused(server):
    got = _post(server, dict(recordings=CORPUS, archs=["tube"],
                             folds=[dict(train=[0, 1, 2], test=[2])]))
    assert got["result"] is None
    assert "BOTH" in got["error"] and "in-sample" in got["error"]


def test_a_threshold_is_refused_here_too(server):
    """Same rule as `/api/detect`: refused, not ignored."""
    got = _post(server, dict(recordings=CORPUS, archs=["tube"], threshold=0.5,
                             folds=FOLDS))
    assert got["result"] is None and "threshold" in got["error"]


def test_an_unknown_architecture_names_what_there_is(server):
    got = _post(server, dict(recordings=CORPUS, archs=["nope"], folds=FOLDS))
    assert got["result"] is None
    assert "nope" in got["error"] and "tube" in got["error"]


def test_a_fold_too_small_to_hold_out_a_validation_recording_is_refused(server):
    """One training recording cannot both fit the model and choose its threshold."""
    got = _post(server, dict(recordings=CORPUS, archs=["tube"],
                             folds=[dict(train=[0], test=[1])]))
    assert got["result"] is None and "at least two" in got["error"]


def test_truth_without_onsets_is_refused_rather_than_padded(server):
    """The nominal time cannot be widened into a footprint here.

    `frame_targets` labels across the realized span, and padding `time ± 3·jitter`
    would teach a model a window the generator never planted — invisibly, in the
    one place nothing would check it.
    """
    bad = json.loads(json.dumps(CORPUS))
    for e in bad[0]["truth"]["events"]:
        e.pop("onsets")
    got = _post(server, dict(recordings=bad, archs=["tube"], folds=FOLDS))
    assert got["result"] is None and "onsets" in got["error"]


def test_the_registry_is_what_the_picker_is_offered(server):
    """A hardcoded `<option>` list would be the second edit a new model needs."""
    cap = json.load(urllib.request.urlopen(
        f"http://127.0.0.1:{server}/api/capabilities"))
    names = [a["name"] for a in cap["architectures"]]
    from bugarach.learn.nets import ARCHITECTURES
    assert names == sorted(ARCHITECTURES)
    for a in cap["architectures"]:
        assert a["note"], f"{a['name']} has no note for the picker to show"


def test_progress_arrives_per_fold_and_per_architecture(server):
    got = _post(server, dict(recordings=CORPUS, archs=["tube", "trace"],
                             folds=FOLDS))
    assert got["error"] is None
    fits = [p for p in got["progress"] if p.get("stage") == "fit"]
    assert len(fits) == 4                       # 2 architectures x 2 folds
    assert {p["arch"] for p in fits} == {"tube", "trace"}
    assert [p["done"] for p in fits] == [0, 1, 2, 3]


@pytest.mark.skipif(not lab_mod.TubeTrainer().available,
                    reason="torch not installed — install `.[dl]`")
def test_the_real_trainer_fits_the_pages_corpus_and_pins_its_threads():
    """One small end-to-end fit, so the seam is checked against real numerics."""
    httpd = lab_mod.make_server(port=0, quiet=True)
    threading.Thread(target=httpd.serve_forever, daemon=True).start()
    try:
        got = _post(httpd.server_address[1],
                    dict(recordings=CORPUS, archs=["tube"], steps=5,
                         folds=[dict(train=[0, 1, 2], test=[3])]))
    finally:
        httpd.shutdown()
        httpd.server_close()
    assert got["error"] is None, got["error"]
    fold = got["result"]["per_arch"]["tube"][0]
    from bugarach.learn.train import THREADS
    assert fold["threads"] == THREADS
    assert fold["n_params"] == 1149
    assert 0.0 < fold["threshold"] < 1.0
