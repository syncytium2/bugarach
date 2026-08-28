"""`rise_durations()` on FOLDER input, which nothing had ever tested.

`test_cicada_detect.py` covers the function on `SLICE.fast` — a **store** fixture,
where `locs` really is the peak time and `locs - t50rise` really is the rise
interval. On an **export folder** the field named `locs` holds `t50rise` (the
coordination data put the onset into the legacy `findpeaks` field name), so the
same subtraction returns zero for every event.

That asymmetry is documented in `bugarach.store.Stream` and was invisible to the
suite because no test loaded a folder and asked what a duration came out as.

Synthetic fixture only — no real recording is committed (FOUNDATIONS §5).

See `docs/todo/2026-08-28-locs-is-a-field-name-and-rise-durations-is-zero.md`.
"""

from __future__ import annotations

import numpy as np
import pytest

from bugarach.detectors.cicada import rise_durations
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
    """The premise. If this ever fails, the rest of this file is meaningless."""
    st = load_folder(folder_with_peaks)[0].streams["fast"]
    assert st.has_peak, "the producer sent peak_sec; it must be loaded"
    assert np.allclose(np.concatenate(st.locs), np.concatenate(st.t50rise)), \
        "on a FOLDER, locs holds t50rise — the legacy field name, the new value"
    assert not np.allclose(np.concatenate(st.peak), np.concatenate(st.locs)), \
        "the peak is a different time and it is available"


@pytest.mark.xfail(strict=True, reason=(
    "KNOWN DEFECT, latent not live: rise_durations() computes locs - t50rise, "
    "which is the rise interval on a STORE and identically zero on a FOLDER. "
    "The real interval (peak - locs, median 0.30 s on dataset.current()) is "
    "loaded and unread. Not on the deployed path — OPERATING_POINTS['cicada'] "
    "uses fixed active_duration_sec=1.0 — so this documents the trap rather "
    "than a wrong published number. Remove this marker when it is fixed; "
    "strict=True makes the suite fail if it starts passing silently. "
    "docs/todo/2026-08-28-locs-is-a-field-name-and-rise-durations-is-zero.md"))
def test_rise_durations_should_not_be_zero_when_the_producer_sent_a_peak(
        folder_with_peaks):
    st = load_folder(folder_with_peaks)[0].streams["fast"]
    durations = np.concatenate([d for d in rise_durations(st) if d.size])
    assert durations.size, "fixture should produce events"
    assert (durations > 0).all(), (
        "every event has a real rise interval in this fixture "
        "(0.3, 0.4, 0.2 s) and rise_durations() returns zeros")


def test_the_zero_is_what_happens_today_and_it_is_silent(folder_with_peaks):
    """Pins the CURRENT behaviour so the failure mode is legible in the suite.

    Not an endorsement — the point is that it returns a plausible array of the
    right shape and dtype rather than raising, which is why nothing noticed.
    """
    st = load_folder(folder_with_peaks)[0].streams["fast"]
    durations = np.concatenate([d for d in rise_durations(st) if d.size])
    assert durations.size == 3
    assert (durations == 0).all()
    assert np.isfinite(durations).all(), "silently zero, never NaN, never raised"
