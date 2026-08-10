"""Coordination detectors, ported one at a time from interface2.

Port order (each lands only with a MATLAB parity test):
  rate      rate+context (RateDetect)
  local     CoactDetect
  loco      LoCo
  sce       binned SCE
  cicada    CICADA (native peak detection)
  sync      SPIKE-synchronization via PySpike (cSPIKE equivalent)

The output contract mirrors interface2's docs/specs/detector_output_spec.md:
each detector returns its statistic trace plus detected events (onset, width),
in either supra-threshold or peak-gated (prominence + min-distance) mode.
"""
