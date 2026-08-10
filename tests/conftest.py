"""Shared helpers for MATLAB-reference parity tests."""

import numpy as np


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
