"""Shared helpers for MATLAB-reference parity tests."""

import re
from pathlib import Path

import numpy as np

_VIEWER = Path(__file__).resolve().parents[1] / "docs/site/raster_viewer.html"


def locust_suppressed_in_the_browser() -> bool:
    """Does the shipped page hold locust out of this build?

    Read from the artifact rather than from a constant in this suite, so a skip
    can only ever agree with what a user actually gets.

    ⚠ **THIS READ THE WRONG FIELD FOR A WHILE, AND WENT SILENTLY BLIND.** It
    looked for a truthy ``unavailable`` on the registry entry. That was the
    mechanism on 2026-08-29 morning; by the evening the page had moved to a
    ``WITHHELD`` set, because ``unavailable`` draws the row and states a reason
    and Tony asked for the detector to be absent instead — *"withold cicada
    locust entirely … there's no reason for cicada/locust to be present in the
    current webpage."* The helper then reported **not suppressed** while the page
    suppressed it, so every skip it guards would have quietly run against a
    detector with no controls at all: a check that cannot ring, which is the
    failure class this suite files incidents about.

    It reads **both** now. A detector is out of this build if it is in
    ``WITHHELD`` (absent: no option, no tick, no explanation) or carries
    ``unavailable`` (present, disabled, and saying why) — two different answers to
    "not in this build", and a test that exercises the detector wants to skip
    under either.

    The port, its MATLAB parity to 1e-9 and ``bugarach detect`` are untouched;
    what went away is the viewer offering it. Tests are keyed to this rather than
    deleted, so **they come back by themselves the day it does** — the behaviour
    they cover is not knowledge worth re-earning later.
    """
    src = _VIEWER.read_text(encoding="utf-8")

    held = re.search(r"const WITHHELD = new Set\(\[(.*?)\]\)", src, re.S)
    if held and '"cicada"' in held.group(1):
        return True

    entry = re.search(r"\n  cicada: \{(.*?)\n  \},", src, re.S)
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
