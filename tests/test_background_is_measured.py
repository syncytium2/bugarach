"""The background shape is a measurement of a corpus, not a constant.

`bench.MEASURED_RATE_SHAPE` (0.275) is the maximum-likelihood fit over **this
lab's** 81 baseline windows. That number is right about this lab and says nothing
about anyone else's field, so handing it to another folder is the same category of
error as handing them a flat one: a constant standing in for a measurement.

Tony, 2026-08-22: *"Chosing flat clearly fails to match our data. Whether or not
another users data has this property is another question. This should be a toggle
not a decision."*

These tests pin the toggle, and the point is that **it toggles itself**: the same
code returns a small shape for a heterogeneous field and a large one for a flat
field, because in both cases it is reading the recordings rather than a constant.
"""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

import numpy as np
import pytest

from bugarach.io import load_folder

TOOLS = Path(__file__).resolve().parents[1] / "tools"


@pytest.fixture(scope="module")
def fitter():
    spec = importlib.util.spec_from_file_location(
        "_fbs", TOOLS / "fit_background_shape.py")
    m = importlib.util.module_from_spec(spec)
    sys.modules["_fbs"] = m
    spec.loader.exec_module(m)
    return m


def _folder(root: Path, rates_hz, *, dur=1800.0, n_rec=12, seed=0) -> Path:
    """An export folder whose per-ROI rates are drawn by the caller.

    Poisson events at a per-ROI rate, one `baseline` region covering the whole
    recording, written the way a producer would.
    """
    rng = np.random.RandomState(seed)
    root.mkdir(parents=True, exist_ok=True)
    reg = ["slice_id,region_idx,label,start_sec,end_sec"]
    for i in range(n_rec):
        rates = rates_hz(rng)
        rows = ["roi,time_sec"]
        for r, lam in enumerate(rates):
            k = rng.poisson(lam * dur)
            t = np.sort(rng.uniform(0, dur, k))
            if not k:
                rows.append(f"{r + 1},NA")
            for x in t:
                rows.append(f"{r + 1},{x:.2f}")
        (root / f"rec_{i + 1}.csv").write_text("\n".join(rows) + "\n",
                                               encoding="utf-8")
        reg.append(f"rec_{i + 1},1,baseline,0,{dur:.1f}")
    (root / "slices.csv").write_text(
        "slice_id,frame_interval_sec\n"
        + "".join(f"rec_{i + 1},0.1\n" for i in range(n_rec)), encoding="utf-8")
    (root / "regions.csv").write_text("\n".join(reg) + "\n", encoding="utf-8")
    return root


def test_a_heterogeneous_field_fits_a_small_shape(tmp_path, fitter):
    """Drawn from Gamma(0.3): a third of ROIs near-silent, a long tail. The fit
    should recover something in that neighbourhood rather than a constant."""
    folder = _folder(tmp_path / "het",
                     lambda rng: rng.gamma(0.3, 0.02 / 0.3, 40), seed=1)
    shape, n_win, n_roi = fitter.fit_shape_from_slices(load_folder(folder))
    assert n_win == 12 and n_roi == 480
    assert shape is not None
    assert 0.15 < shape < 0.7, (
        f"fitted {shape:.3f} from a field drawn at 0.3 — the estimator should "
        "land near the truth, not near this lab's 0.275 by coincidence")


def test_a_flat_field_fits_a_large_shape(tmp_path, fitter):
    """**The half that makes it a toggle rather than a decision.** A lab whose
    field really is uniform gets that answer from the same code — shape grows
    without bound as heterogeneity vanishes, so nothing has to be chosen."""
    folder = _folder(tmp_path / "flat",
                     lambda rng: np.full(40, 0.02), seed=2)
    shape, _, _ = fitter.fit_shape_from_slices(load_folder(folder))
    assert shape is not None
    assert shape > 5.0, (
        f"fitted {shape:.3f} on a genuinely flat field — a flat field is "
        "shape -> infinity, and reporting a small one would impose this lab's "
        "heterogeneity on a corpus that does not have it")


def test_the_two_fields_are_told_apart_by_a_wide_margin(tmp_path, fitter):
    """Not a threshold to tune: the two answers should be an order of magnitude
    apart, so the measurement is decisive rather than marginal."""
    het = fitter.fit_shape_from_slices(load_folder(
        _folder(tmp_path / "a", lambda rng: rng.gamma(0.3, 0.02 / 0.3, 40),
                seed=3)))[0]
    flat = fitter.fit_shape_from_slices(load_folder(
        _folder(tmp_path / "b", lambda rng: np.full(40, 0.02), seed=4)))[0]
    assert flat > 10 * het, f"flat {flat:.2f} vs heterogeneous {het:.2f}"


def test_too_little_baseline_refuses_rather_than_inheriting(tmp_path, fitter):
    """The failure that matters. With too few windows to fit, the honest answer
    is None and a reason — silently falling back to another corpus's constant is
    the error this whole path exists to prevent."""
    folder = _folder(tmp_path / "thin",
                     lambda rng: rng.gamma(0.3, 0.02 / 0.3, 40), n_rec=3, seed=5)
    shape, n_win, _ = fitter.fit_shape_from_slices(load_folder(folder))
    assert shape is None and n_win == 3


def test_this_labs_constant_is_labelled_as_this_labs(fitter):
    """It is a measurement of one corpus and the source has to say so, or the
    next reader takes it for a property of calcium imaging."""
    src = (TOOLS.parent / "src" / "bugarach" / "bench.py").read_text()
    i = src.index("MEASURED_RATE_SHAPE = ")
    block = src[i:i + 1400]
    assert "81 baseline windows" in block, (
        "the constant must carry the corpus it was fitted on, or the next "
        "reader takes it for a property of calcium imaging")
    assert fitter._this_labs_reference() == pytest.approx(0.275)
