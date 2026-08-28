"""The declared stream default, and the app control that overrides it.

Two rules, and the distinction between them is the point:

- **Headless analysis** has no person, so it needs a declared answer —
  `dataset.preferred_stream`. Before this existed, `assess_folder` silently took
  `names[0]` while `detect_folder` ran every stream, which is a question with no
  answer in the tree getting a different answer from each caller.
- **The viewer has a person**, so the person picks. The default only decides
  which entry the control opens on.

Synthetic fixtures only (FOUNDATIONS §5).
"""

from __future__ import annotations

import numpy as np
import pytest

from bugarach.dataset import DEFAULT_STREAM, preferred_stream
from bugarach.io import slice_from_events


def _slice(streams, slice_id="s1"):
    return slice_from_events(
        {name: [np.array([1.0, 5.0, 9.0])] for name in streams},
        dt=0.1, slice_id=slice_id)


def test_one_stream_is_used_whatever_it_is_called():
    """FOUNDATIONS §3: most outside labs have one stream. No convention of ours
    may touch that case — including a convention named 'fast'."""
    assert preferred_stream(["events"]) == "events"
    assert preferred_stream(["dF_F"]) == "dF_F"


def test_fast_wins_when_more_than_one_stream_is_present():
    assert preferred_stream(["slow", "fast"]) == DEFAULT_STREAM
    assert preferred_stream(["fast", "slow"]) == DEFAULT_STREAM


def test_order_no_longer_decides_between_two_real_streams():
    """The defect this closes: dict order chose between two utterly different
    measurements. Both orderings must now give the same answer."""
    assert preferred_stream(["slow", "fast"]) == preferred_stream(["fast", "slow"])


def test_without_the_default_it_falls_back_to_first_as_the_tree_always_did():
    assert preferred_stream(["alpha", "beta"]) == "alpha"


def test_no_streams_raises_rather_than_returning_a_name_that_indexes_nothing():
    with pytest.raises(ValueError, match="no streams"):
        preferred_stream([])


def test_it_is_not_importable_from_the_store_reader():
    """It lives in `dataset`, beside `current()`, on purpose. In `store` it made
    every caller import the module the folder-is-the-input hook watches — a
    helper about convention tripping a gate about provenance."""
    import bugarach.store as store
    assert not hasattr(store, "preferred_stream")
    assert not hasattr(store, "DEFAULT_STREAM")


def test_the_viewer_offers_the_choice_and_opens_on_the_default():
    """The app must ASK, not decide. Requested 2026-08-22 in
    `docs/todo/2026-08-22-a-back-route-for-a-reliable-pipeline.md` — "a person
    chooses K, looks at the comparison, and picks a stream" — and never built."""
    pn = pytest.importorskip("panel")
    from bugarach.ui.app import build_viewer

    s = _slice(["slow", "fast"])
    view = build_viewer({s.slice_id: s}, title="t")
    sels = [w for w in view.sidebar[0] if isinstance(w, pn.widgets.Select)]
    stream_sel = next((w for w in sels if w.name == "stream"), None)

    assert stream_sel is not None, "the viewer must offer a stream control"
    assert set(stream_sel.options) == {"fast", "slow"}
    assert stream_sel.value == DEFAULT_STREAM, "opens on the default"
    assert not stream_sel.disabled, "two streams is a real choice"


def test_a_single_stream_recording_gets_no_live_dropdown():
    """One stream is not a choice, and a live control implies it is."""
    pn = pytest.importorskip("panel")
    from bugarach.ui.app import build_viewer

    s = _slice(["events"])
    view = build_viewer({s.slice_id: s}, title="t")
    sels = [w for w in view.sidebar[0] if isinstance(w, pn.widgets.Select)]
    stream_sel = next((w for w in sels if w.name == "stream"), None)

    assert stream_sel is not None
    assert stream_sel.value == "events"
    assert stream_sel.disabled
