"""The folder case that exposed `rise_durations()`, and the refusal that closed it.

This file used to carry a strict-xfail marker and a test pinning a silent wrong
answer. Both are gone, because the function they described is gone.

**What it was.** `rise_durations()` computed the rise interval as
`locs - t50rise`. On a **store** that is right: `locs` there is the peak. On an
**export folder** — the only input, since the store is closed — the field named
`locs` holds the `t50rise`, because the coordination data put the onset into the
legacy `findpeaks` field name. So the subtraction returned identically zero for
every event: 2,215 of them on `dataset.current()`, finite, correctly shaped,
never raising. That asymmetry is documented in `bugarach.store.Stream` and was
invisible to the suite because no test had ever loaded a folder and asked what a
duration came out as.

**Why the fix is not "use the peak instead".** That was the obvious repair and it
is the wrong one. Tony, 2026-08-29: *"matlab decides duration. bugarach python
and webapp is not responsible for what the duration is derived from."* The rise
interval is a truncation the MATLAB team applies **on export**, because this
preparation's slow events are not described in the literature and destroy CICADA
at full duration; it travels in `width_sec` under its own `width_def`.
Recomputing it here — correctly or otherwise — duplicates a decision that has
already been made and silently overrides whatever the producer actually sent.
The zero was the symptom that got someone's attention. The derivation was the
defect. See ADR-0002's 2026-08-28 addendum and FOUNDATIONS §7.

So the tests below check two things: that the folder asymmetry which made the
old answer wrong is still real (it is a property of the contract, not a bug that
was fixed), and that the function refuses rather than answering.

Synthetic fixture only — no real recording is committed (FOUNDATIONS §5).

Closes `docs/todo/2026-08-28-locs-is-a-field-name-and-rise-durations-is-zero.md`.
"""

from __future__ import annotations

import numpy as np
import pytest

from bugarach.detectors.cicada import DurationIsNotOursToDerive, rise_durations
from bugarach.io import load_folder


@pytest.fixture
def folder_with_peaks(tmp_path):
    """A minimal export folder whose producer sent `peak_sec`, like ours does."""
    rows = [
        # roi, time_sec (t50rise), width_sec, width_def, peak_sec
        ("1", 10.0, 0.9, "halfprom_width_findpeaks_w", 10.3),
        ("1", 20.0, 0.9, "halfprom_width_findpeaks_w", 20.4),
        ("2", 15.0, 0.9, "halfprom_width_findpeaks_w", 15.2),
    ]
    csv = tmp_path / "synthetic_a.csv"
    csv.write_text(
        "roi,time_sec,stream,width_sec,width_def,peak_sec\n"
        + "".join(f"{r},{t},fast,{w},{d},{p}\n" for r, t, w, d, p in rows))
    (tmp_path / "slices.csv").write_text(
        "slice_id,frame_interval_sec\nsynthetic_a,0.1\n")
    return tmp_path


def test_a_folder_puts_the_onset_in_locs_and_the_peak_somewhere_else(
        folder_with_peaks):
    """The premise, and it is contract rather than accident.

    Kept after the refusal landed: this is the asymmetry that made a subtraction
    look reasonable in one place and evaluate to zero in the other, and anything
    that reads `locs` on a folder still has to know it.
    """
    st = load_folder(folder_with_peaks)[0].streams["fast"]
    assert st.has_peak, "the producer sent peak_sec; it must be loaded"
    assert np.allclose(np.concatenate(st.locs), np.concatenate(st.t50rise)), \
        "on a FOLDER, locs holds t50rise — the legacy field name, the new value"
    assert not np.allclose(np.concatenate(st.peak), np.concatenate(st.locs)), \
        "the peak is a different time and it is available"


def test_the_producer_sent_a_duration_and_it_is_the_one_to_use(
        folder_with_peaks):
    """What replaces the derivation: read `width_sec`, and its `width_def`.

    Every event in this fixture has a real duration that arrived from the
    producer, named by the rule that made it. There was never anything to
    compute.
    """
    st = load_folder(folder_with_peaks)[0].streams["fast"]
    assert st.has_width, "width_sec + width_def is how a duration travels"
    assert st.width_def == "halfprom_width_findpeaks_w"
    widths = np.concatenate([w for w in st.width if len(w)])
    assert widths.size == 3
    assert (widths > 0).all(), "the producer's durations are real and positive"


def test_rise_durations_refuses_on_a_folder(folder_with_peaks):
    """The failure is now loud, at the line that asked for it.

    The old behaviour returned three zeros and no signal of any kind. What made
    that dangerous was not the wrong value but the confident shape: an array of
    the right length and dtype is indistinguishable from an answer.
    """
    st = load_folder(folder_with_peaks)[0].streams["fast"]
    with pytest.raises(DurationIsNotOursToDerive) as e:
        rise_durations(st)
    assert "width_sec" in str(e.value)
