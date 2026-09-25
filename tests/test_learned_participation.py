"""Participation for the learned models — ADR-0010 (Proposed) part 5, preparation only.

What these pin:

* **Nothing registered before it moves.** Every pre-existing architecture builds with the
  parameter names and shapes it had on ``main`` (pinned in
  ``tests/fixtures/learn_participation_pins.json``, computed before the change), the checkpoints
  in the repository load and score as they did, a default fit is the fit it was, and the bench's
  scoring and training recordings are byte-for-byte the recordings they were.
* **The count is bounded** by the number of ROIs, and the comparison with the floor flips at the
  floor.
* **Membership targets and floor labels** say what the ADR says, on a hand-built recording.
* **Boundary planting** adds events at floor − 1, floor and floor + 1 and leaves scoring alone.
* **A smoke fit per new variant**: a tiny CPU fit that trains (loss falls, output not a
  constant) and reads its floor input (change only the floor and the output moves).
"""
from __future__ import annotations

import hashlib
import json
import warnings
from pathlib import Path

import numpy as np
import pytest

torch = pytest.importorskip("torch")

from bugarach import bench  # noqa: E402
from bugarach.learn import checkpoint  # noqa: E402
from bugarach.learn import participation as part  # noqa: E402
from bugarach.learn.encode import encode, frame_targets  # noqa: E402
from bugarach.learn.nets import ARCHITECTURES, n_params  # noqa: E402
from bugarach.learn.train import Trained, fold_maker, train  # noqa: E402
from bugarach.simulate import GroundTruth, PlantedEvent, simulate_coordination  # noqa: E402

REPO = Path(__file__).resolve().parents[1]
PINS = json.loads((REPO / "tests/fixtures/learn_participation_pins.json").read_text())
NEW = ("chorus_norm_part", "chorus_gain_norm_part", "line_part", "tube_part")
WITH_MEMBERSHIP = ("chorus_norm_part", "chorus_gain_norm_part", "line_part")


# --------------------------------------------------------------------------------------------
# nothing registered before moves
# --------------------------------------------------------------------------------------------

@pytest.mark.parametrize("name", sorted(PINS["shapes"]))
def test_every_pre_existing_architecture_builds_as_it_did_on_main(name):
    torch.manual_seed(0)
    got = {k: list(v.shape) for k, v in ARCHITECTURES[name].make().state_dict().items()}
    assert got == PINS["shapes"][name], f"{name}'s parameters moved"
    assert ARCHITECTURES[name].training == {}, f"{name} gained training defaults"
    assert "participation" not in ARCHITECTURES[name].cfg


def test_the_new_variants_are_new_names_not_edits():
    assert not set(NEW) & set(PINS["shapes"])
    for name in NEW:
        assert name in ARCHITECTURES
        assert ARCHITECTURES[name].cfg.get("participation") is True


@pytest.mark.parametrize("arch", sorted(PINS["checkpoints"]))
def test_the_repositorys_checkpoints_load_and_score_as_they_did(arch):
    pin = PINS["checkpoints"][arch]
    tr = checkpoint.load(REPO / pin["path"])
    rng = np.random.RandomState(7)
    x = torch.from_numpy((rng.rand(1, 20, 600) < 0.02).astype(np.float32))
    x[0, :9, 300] = 1.0
    with torch.no_grad():
        z = tr.model(x).squeeze(0).numpy().astype(np.float64)
    assert np.allclose(z[:3], pin["first"], rtol=1e-4, atol=1e-4)
    assert np.isclose(z[300], pin["at300"], rtol=1e-4, atol=1e-4)
    assert np.isclose(z.sum(), pin["sum"], rtol=1e-4)


def _recording_hash(s, gt, stream="events"):
    h = hashlib.sha256()
    st = s.streams[stream]
    for v in st.locs:
        h.update(np.asarray(v, np.float64).tobytes())
        h.update(b"|")
    for v in st.t50rise:
        h.update(np.asarray(v, np.float64).tobytes())
        h.update(b"|")
    for e in list(gt.events) + list(gt.distractors):
        h.update(repr((e.time, e.frac, e.n_part, e.rois, e.onsets)).encode())
    h.update(repr(gt.params.get("event_floor")).encode())
    enc = encode(s, dt=0.1, stream=stream)
    h.update(enc.raster.tobytes())
    h.update(frame_targets(gt, enc).tobytes())
    return h.hexdigest()[:24]


@pytest.mark.parametrize("key", ["bench:baseline_quiet:1", "bench:baseline_quiet:1000"])
def test_scoring_and_training_recordings_are_the_ones_main_built(key):
    """Seed 1 is a scored recording and seed 1000 a training one; both hashes were taken on
    ``main`` before this change, over the trains, the planted events, the floor, the raster and
    the frame labels."""
    _, regime, seed = key.split(":")
    s, gt = bench.make_recording(regime, int(seed))
    assert _recording_hash(s, gt) == PINS["recordings"][key]


def _fit_pin_recordings():
    import sys
    sys.path.insert(0, str(REPO / "tools"))
    from fair_bakeoff import _make_recording

    spec = json.loads((REPO / "docs/learned/generator_spec.json").read_text())["generator"]
    cache = {}

    def rec(s):
        if s not in cache:
            cache[s] = _make_recording(spec, s)
        return cache[s]
    return rec


@pytest.mark.parametrize("name", ["tube", "chorus_norm", "line"])
def test_a_default_fit_is_the_fit_main_made(name):
    """Ten steps of an existing architecture: its weights, threshold, loss history and training
    record keys match what ``main`` produced (pinned before the change)."""
    pin = PINS["fits"][name]
    mk, n_fit, _ = fold_maker(_fit_pin_recordings(), [1000, 1001, 1002])
    with warnings.catch_warnings():
        warnings.simplefilter("ignore", RuntimeWarning)
        tr = train(name, mk, n_train=n_fit, steps=10, crop=1024, batch=2, lr=1e-2, seed=0)
    w = sum(float(np.abs(v.detach().numpy().astype(np.float64)).sum())
            for v in tr.model.state_dict().values())
    assert np.isclose(w, pin["abs_sum"], rtol=1e-4)
    assert tr.threshold == pin["threshold"]
    assert np.allclose([l for _, l in tr.history], pin["loss"], rtol=1e-4)
    assert sorted(tr.training) == pin["training_keys"]


def test_membership_is_refused_for_a_model_without_votes():
    mk, _, _ = fold_maker(_fit_pin_recordings(), [1000, 1001, 1002])
    with pytest.raises(ValueError, match="no per-cell vote"):
        train("tube", mk, n_train=1, steps=1, crop=256, batch=1, membership_weight=1.0)


# --------------------------------------------------------------------------------------------
# the count, the floor, the targets
# --------------------------------------------------------------------------------------------

@pytest.mark.parametrize("name", NEW)
def test_the_count_is_bounded_by_the_number_of_rois(name):
    """Every ROI active in every frame: the count cannot pass the ROI count, however trained."""
    torch.manual_seed(0)
    m = ARCHITECTURES[name].make().eval()
    x = torch.ones(1, 12, 300)
    with torch.no_grad():
        if name in WITH_MEMBERSHIP:
            m.vote_head.bias.fill_(50.0)                  # every vote saturated at 1
            _, votes = m(x, floor=5, return_votes=True)
            count = votes.sum(dim=1)
        else:
            count = part.window_count(x, m.count_frames)
    assert float(count.max()) <= 12 + 1e-4
    assert float(count.min()) >= 0.0


def test_the_comparison_flips_between_floor_minus_one_and_floor():
    f = part.count_features(torch.tensor([[4.0, 5.0, 6.0]]), torch.tensor([5.0]))
    assert f.shape == (1, 3, 3)
    assert f[0, 2, 0] < 0 < f[0, 2, 1] < f[0, 2, 2]
    assert torch.allclose(f[0, 1], torch.log1p(torch.tensor(5.0)).expand(3))


@pytest.mark.parametrize("name", NEW)
def test_a_model_that_reads_the_floor_refuses_to_run_without_one(name):
    m = ARCHITECTURES[name].make()
    with pytest.raises(ValueError, match="floor"):
        m(torch.zeros(1, 5, 64))


def _hand_built():
    """Ten ROIs at 0.1 s; two events and one distractor, onsets placed by hand."""
    from bugarach.io import slice_from_events

    ev = [PlantedEvent(time=10.0, frac=0.3, n_part=3, rois=(1, 4, 7), jitter_sec=0.1,
                       onsets=(10.0, 10.1, 10.2)),
          PlantedEvent(time=30.0, frac=0.6, n_part=6, rois=(0, 1, 2, 3, 5, 9), jitter_sec=0.1,
                       onsets=(30.0, 30.0, 30.1, 30.1, 30.2, 30.3))]
    dis = [PlantedEvent(time=50.0, frac=0.2, n_part=2, rois=(6, 8), jitter_sec=0.1,
                        onsets=(50.0, 50.1), kind="distractor")]
    trains = [[] for _ in range(10)]
    for e in ev + dis:
        for r, t in zip(e.rois, e.onsets):
            trains[r].append(t)
    trains[0] += [1.0, 59.0]                              # recording ends at 60 s
    per = [np.sort(np.asarray(t, float)) for t in trains]
    s = slice_from_events({"events": per}, dt=0.1, slice_id="hand")
    return s, GroundTruth(events=ev, distractors=dis, params={"event_floor": 5})


def test_floor_labels_drop_the_sub_floor_event_for_training_only():
    s, gt = _hand_built()
    enc = encode(s, dt=0.1)
    all_ = frame_targets(gt, enc)
    y = part.training_targets(gt, enc, 5)
    t = lambda sec: int(round((sec - enc.t0) / enc.dt))  # noqa: E731
    assert all_[t(10.1)] == 1 and y[t(10.1)] == 0, "the 3-ROI event is under a floor of 5"
    assert all_[t(30.1)] == 1 and y[t(30.1)] == 1
    assert np.array_equal(part.training_targets(gt, enc, None), all_)
    # scoring is untouched: the scorer still reads the floor and calls the event don't-care
    from bugarach.score import score_stream

    class _Det:
        onset_sec = np.array([10.0])
        width_sec = np.array([0.3])
        score = np.zeros(1)
        threshold = 0.5
        times = np.zeros(1)
    sc = score_stream(gt, _Det())
    assert sc.n_planted == 1, "the sub-floor event is don't-care in scoring (ADR-0009 d. 2)"


def test_membership_targets_follow_the_planted_members_in_encoded_row_order():
    s, gt = _hand_built()
    enc = encode(s, dt=0.1)
    target, mask = part.membership_targets(gt, enc)
    row = {int(r): i for i, r in enumerate(enc.order)}
    t = lambda sec: int(round((sec - enc.t0) / enc.dt))  # noqa: E731
    for r in range(10):
        assert target[row[r], t(10.1)] == (1.0 if r in (1, 4, 7) else 0.0)
        assert target[row[r], t(30.1)] == (1.0 if r in (0, 1, 2, 3, 5, 9) else 0.0)
    assert target[:, t(20.0)].sum() == 0
    assert mask[row[6], t(50.0)] == 0 and mask[row[8], t(50.0)] == 0, "distractors are masked"
    assert mask[row[0], t(50.0)] == 1
    assert target[:, t(50.0)].sum() == 0


# --------------------------------------------------------------------------------------------
# boundary planting and the smoke fits
# --------------------------------------------------------------------------------------------

SMALL = dict(duration_sec=900.0, n_roi=20, bg_rate_hz=0.01, participation=(0.5, 0.3),
             n_per_level=(8, 8), jitter_sec=0.105, min_sep_sec=25.0, n_distractors=2,
             distractor_frac=0.2)
_CACHE: dict = {}


def _small(regime, seed, **over):
    """A small bench-shaped recording with its ADR-0008 floor, cheap enough for a smoke test.
    ``regime`` is ignored: the signature is a bench module's ``make_recording``."""
    return bench.with_floor(simulate_coordination(seed=seed, **{**SMALL, **over}))


def _boundary(seed):
    if seed not in _CACHE:
        _CACHE[seed] = part.boundary_recording(_small, "small", seed)
    return _CACHE[seed]


def test_boundary_planting_adds_events_either_side_of_the_floor():
    s, gt = _boundary(2000)
    bp = gt.params["boundary_planting"]
    f0 = bp["planned_floor"]
    assert bp["counts"] == [c for c in (f0 - 1, f0, f0 + 1) if c >= 1]
    got = sorted(e.n_part for e in gt.events)
    for c in bp["counts"]:
        assert c in got
    assert len(gt.events) == 16 + len(bp["counts"])
    assert gt.params["event_floor"] >= 3
    base_s, base_gt = _small("small", 2000)
    assert len(base_gt.events) == 16, "the generator's own recording is unchanged"


def _smoke_maker():
    return fold_maker(_boundary, [2000, 2001, 2002, 2003, 2004])


def _frame_loss(model, recs):
    tot = 0.0
    for enc, y, f in recs:
        pos = max(float(y.mean()), 1e-6)
        lossf = torch.nn.BCEWithLogitsLoss(pos_weight=torch.tensor([(1 - pos) / pos]))
        with torch.no_grad():
            z = model(torch.from_numpy(enc.raster).unsqueeze(0), floor=[f])
        tot += float(lossf(z, torch.from_numpy(y).unsqueeze(0)))
    return tot / len(recs)


@pytest.mark.parametrize("name", NEW)
def test_smoke_fit_trains_and_reads_its_floor(name, tmp_path):
    """One tiny CPU fit per new variant, with boundary planting, floor labels and (chorus, line)
    the membership term. It trains: the frame loss on its own recordings falls and the output is
    not a constant. It reads the floor: changing only the floor input moves the output."""
    mk, n_fit, _ = _smoke_maker()
    with warnings.catch_warnings():
        warnings.simplefilter("ignore", RuntimeWarning)
        # 120 steps at 3e-3: at 60 steps and 1e-2 chorus_norm_part, seed 0, is still on the
        # plateau chorus_norm is known to start on (docs/learned/chorus_collapse/), and leaves it
        # by step 100 here.
        tr = train(name, mk, n_train=n_fit, steps=120, crop=2048, batch=2, lr=3e-3, seed=0)
    p = tr.training["participation"]
    assert p["reads_floor"] and p["floor_labels"]
    assert p["membership_weight"] == (1.0 if name in WITH_MEMBERSHIP else 0.0)

    recs = []
    for s in (2000, 2001, 2002):
        sl, gt = _boundary(s)
        enc = encode(sl, dt=0.1)
        f = gt.params["event_floor"]
        recs.append((enc, part.training_targets(gt, enc, f), f))
    torch.manual_seed(0)
    before = _frame_loss(ARCHITECTURES[name].make().eval(), recs)
    after = _frame_loss(tr.model, recs)
    assert after < before, f"{name}: frame loss {before:.3f} -> {after:.3f}, did not train"

    enc, y, f = recs[0]
    x = torch.from_numpy(enc.raster).unsqueeze(0)
    with torch.no_grad():
        z = tr.model(x, floor=[f]).squeeze(0).numpy()
        z_up = tr.model(x, floor=[f + 4]).squeeze(0).numpy()
    assert z.std() > 1e-3 and np.ptp(z) > 0.05, f"{name} collapsed to a constant"
    assert z[y > 0].mean() > z[y == 0].mean(), f"{name} does not separate events"
    assert np.abs(z - z_up).max() > 1e-3, f"{name} ignores its floor input"

    if name in WITH_MEMBERSHIP:
        target, mask = part.membership_targets(_boundary(2000)[1], enc)
        with torch.no_grad():
            _, votes = tr.model(x, floor=[f], return_votes=True)
        v = votes.squeeze(0).numpy()
        keep = mask > 0
        assert v[(target > 0) & keep].mean() > v[(target == 0) & keep].mean(), (
            f"{name}'s votes are no higher on members than elsewhere")

    # the fitted model travels: checkpoint round trip, and predict computes a window's floor
    path = checkpoint.save(tr, tmp_path / f"{name}.json",
                           trained_on="smoke", train_seed=0, steps=120)
    back = checkpoint.load(path)
    assert back.n_params == tr.n_params == n_params(ARCHITECTURES[name].make())
    with torch.no_grad():
        assert np.allclose(back.model(x, floor=[f]).squeeze(0).numpy(), z, atol=1e-5)
    det, _ = back.predict(_boundary(2000)[0])
    assert isinstance(back, Trained) and det.score.size == enc.n_frame
