"""Coordination detectors, ported one at a time from interface2.

Port order, **key** then the name a person sees (each lands only with a MATLAB
parity test):
  rate      rate+context (RateDetect)          -- landed (see rate.py)
  local     CoactDetect                        -- landed (see coact.py)
  loco      LoCo                               -- landed (see loco.py)
  sce       binned SCE                         -- landed (see sce.py)
  cicada    **locust**                         -- landed (see cicada.py; a
            modified partial port derived from the Cossart lab's CICADA, not
            CICADA itself)
  sync      SPIKE-synchronization              -- landed (see sync.py; native
            port bit-exact vs cSPIKE — PySpike's max_tau cap has been
            broken since 0.8.0, so it is a test-suite cross-check only,
            in the uncapped regime)

**Only the fifth row has a key that is not its name.** ``cicada`` is the
identifier — module, ``cicada_detect``, and the value in ``detections.csv``'s
``detector`` column, which is output contract — and **locust** is what every
screen, figure, report and README calls the same detector. Neither is CICADA in
capitals, which is the Cossart lab's upstream tool that locust is a modified port
of. ``cicada.py``'s docstring is where all three are written down; read it before
assuming which one a given sentence means.

The output contract mirrors interface2's docs/specs/detector_output_spec.md:
each detector returns its statistic trace plus detected events (onset, width),
in either supra-threshold or peak-gated (prominence + min-distance) mode.
The shared peak-gating kernel (if2_peak_gate + findpeaksTD half-prominence
extents) is ported in peaks.py.
"""

from bugarach.detectors.cicada import (
    CicadaDetection,
    CicadaStream,
    DurationIsNotOursToDerive,
    cicada_detect,
    rise_durations,
)
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
from bugarach.detectors.sync import (
    SyncDetection,
    adaptive_profile,
    binned_synchrony,
    sync_detect,
)
from bugarach.detectors.rate import (
    DetectorSignal,
    RateDetection,
    event_rate,
    event_rate_context,
    rate_detect,
    recording_extent,
    stream_trains,
)

__all__ = [
    "CicadaDetection",
    "CicadaStream",
    "CoactDetection",
    "DetectorSignal",
    "LocoDetection",
    "LocoStream",
    "PeakGateResult",
    "RateDetection",
    "RegionWindow",
    "SceDetection",
    "SceSignal",
    "SceStream",
    "SyncDetection",
    "adaptive_profile",
    "binned_synchrony",
    "cicada_detect",
    "DurationIsNotOursToDerive",
    "coact_detect",
    "event_rate",
    "loco_detect",
    "region_windows",
    "rise_durations",
    "sce_detect",
    "sync_detect",
    "event_rate_context",
    "peak_gate",
    "rate_detect",
    "recording_extent",
    "stream_trains",
]
