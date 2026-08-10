"""Coordination detectors, ported one at a time from interface2.

Port order (each lands only with a MATLAB parity test):
  rate      rate+context (RateDetect)          -- landed (see rate.py)
  local     CoactDetect                        -- landed (see coact.py)
  loco      LoCo                               -- landed (see loco.py)
  sce       binned SCE                         -- landed (see sce.py)
  cicada    CICADA (native peak detection)
  sync      SPIKE-synchronization via PySpike (cSPIKE equivalent)

The output contract mirrors interface2's docs/specs/detector_output_spec.md:
each detector returns its statistic trace plus detected events (onset, width),
in either supra-threshold or peak-gated (prominence + min-distance) mode.
The shared peak-gating kernel (if2_peak_gate + findpeaksTD half-prominence
extents) is ported in peaks.py.
"""

from bugarach.detectors.coact import CoactDetection, coact_detect
from bugarach.detectors.loco import (
    LocoDetection,
    LocoStream,
    RegionWindow,
    loco_detect,
    region_windows,
)
from bugarach.detectors.peaks import PeakGateResult, peak_gate
from bugarach.detectors.sce import SceDetection, SceSignal, SceStream, sce_detect
from bugarach.detectors.rate import (
    DetectorSignal,
    GridDtNotSetWarning,
    RateDetection,
    event_rate,
    event_rate_context,
    rate_detect,
    recording_extent,
    stream_trains,
)

__all__ = [
    "CoactDetection",
    "DetectorSignal",
    "GridDtNotSetWarning",
    "LocoDetection",
    "LocoStream",
    "PeakGateResult",
    "RateDetection",
    "RegionWindow",
    "SceDetection",
    "SceSignal",
    "SceStream",
    "coact_detect",
    "event_rate",
    "loco_detect",
    "region_windows",
    "sce_detect",
    "event_rate_context",
    "peak_gate",
    "rate_detect",
    "recording_extent",
    "stream_trains",
]
