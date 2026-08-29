"""Shared helpers for MATLAB-reference parity tests."""

import re
from pathlib import Path

import numpy as np

_VIEWER = Path(__file__).resolve().parents[1] / "docs/site/raster_viewer.html"


def locust_suppressed_in_the_browser() -> bool:
    """Does the shipped page hold locust out of this build?

    Read from the artifact rather than from a constant in this suite, so a skip
    can only ever agree with what a user actually gets. The page's own mechanism
    is a truthy ``unavailable`` on the registry entry — the same flag
    ``offReason()`` reads to disable the option, clear the tick, label it "off in
    this build" and keep the detector out of every run.

    locust was suppressed for this release on 2026-08-29 (Tony). The port, its
    MATLAB parity to 1e-9 and ``bugarach detect`` are untouched; what went away
    is the viewer offering a detector whose number would come from a fixed
    duration nobody chose. Tests that exercise it are keyed to this rather than
    deleted, so **they come back by themselves the day the flag does** — the
    behaviour they cover is not knowledge worth re-earning later.
    """
    entry = re.search(r"\n  cicada: \{(.*?)\n  \},",
                      _VIEWER.read_text(encoding="utf-8"), re.S)
    return bool(entry and "unavailable:" in entry.group(1))


def as1d(v):
    """MATLAB jsonencode collapses 1-element arrays to scalars, empties to [],
    and NaN/Inf to null — normalize back to a 1-D float array."""
    if v is None:
        return np.empty(0)
    if not isinstance(v, list):
        v = [v]
    return np.array([np.nan if x is None else x for x in v], dtype=float)


def as2d(v):
    """Normalize a jsonencode'd Kx2 matrix ([] / flat pair / nested lists)."""
    if v is None or v == []:
        return np.empty((0, 2))
    a = np.array(v, dtype=float)
    return a.reshape(1, 2) if a.ndim == 1 else a


def assert_close_naninf(ours, ref, rtol=1e-9, atol=1e-9, err_msg=""):
    """allclose where the reference is finite; where jsonencode nulled a
    NaN/Inf, require ours to be non-finite too."""
    ours = np.asarray(ours, dtype=float)
    assert ours.shape == ref.shape, f"{err_msg}: shape {ours.shape} vs {ref.shape}"
    finite = np.isfinite(ref)
    np.testing.assert_allclose(ours[finite], ref[finite], rtol=rtol, atol=atol,
                               err_msg=err_msg)
    assert not np.isfinite(ours[~finite]).any(), f"{err_msg}: finite vs null"
