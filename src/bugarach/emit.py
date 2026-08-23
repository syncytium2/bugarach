"""What bugarach emits back: one row per detected coordinated event.

**The six detectors do not return the same shape**, and until now nothing in this
tree had to reconcile them. Three return flat parallel arrays over one stream's
events (``rate``, ``coact``, ``sync``); three return a slice-level container whose
``streams`` maps a name to that stream's events (``loco``, ``sce``, ``cicada``).
They also disagree on spelling — ``locs`` against ``onset_sec``, ``widths`` against
``width_sec``, ``amps`` against ``strength`` — and on what "how strong" even means.

So this module holds **one** table of that mapping, in :data:`FIELDS`, and every
writer goes through it. The alternative is what was already starting to happen:
``bench.false_positives_per_hour`` carries its own two-way ``onset_sec``-or-``locs``
fallback, which covers onsets and nothing else. A second such guess, in the code
that writes the file a statistician opens, is how a column quietly comes to mean
two things.

The output contract is ``docs/export_folder_spec.md`` ("What bugarach emits back").
Rules that are decisions rather than preferences, each recorded there or in
FOUNDATIONS §9:

* **No column changes meaning between rows.** Where "how strong" differs by
  detector, the unit travels beside it in ``strength_unit`` — never in a lookup
  table a reader might not have, because a reader without the table gets a
  plausible wrong answer instead of an error.
* **No privileged region and no protocol vocabulary.** ``region_idx`` and
  ``region_label`` are the producer's own index and name, carried unchanged. There
  is no reserved ``baseline`` and no "treatment slot"; a consumer wanting a
  before-and-after picks the two rows it wants, because it knows which they are and
  we do not.
* **Never a viability claim.** No "dead", "silent" or "inactive" column, ever. A
  zero-event ROI is not a dead ROI, and that verdict belongs to the exporter, which
  sees every treatment of an ROI at once — a record this repo does not have.
* **Seconds, on the recording's own clock.** Frames are the model's unit; the
  conversion happens once, before a value reaches here.
"""

from __future__ import annotations

import csv
import json
from dataclasses import dataclass, field, fields
from pathlib import Path

import numpy as np

__all__ = [
    "DETECTOR_FIELDS",
    "DetectedEvent",
    "DetectionField",
    "NA",
    "detector_settings_rows",
    "events_from",
    "read_detections",
    "write_detections",
    "write_detector_settings",
    "write_run",
]

#: How a missing value is spelled, literally, in every file this module writes.
#: Chosen over the empty string so that "no value" and "a value that happens to be
#: empty" cannot be confused by a reader, and so a real zero stays a zero.
NA = "NA"


@dataclass(frozen=True)
class DetectionField:
    """Where one detector keeps each quantity, and what its strength means.

    ``strength_unit`` is the load-bearing one. It is written into every row this
    detector produces, because the six do not measure strength in the same thing
    and a bare number would need a decoder.
    """

    onset: str
    width: str
    strength: str
    strength_unit: str
    n_roi: str | None
    nested: bool = False


#: The whole mapping, in one place. A seventh detector is one entry here.
#:
#: ``n_roi`` is ``None`` for ``rate`` alone, and that is a fact about RateDetect
#: rather than an omission: it measures how fast the population is firing and
#: reports **no participation quantity at all**. Five of the six do — see
#: ``docs/todo/2026-08-18-the-participant-count-is-reported-and-never-drawn.md``,
#: which is also where ``mag_total`` (recruited anywhere in the episode) is settled
#: as the participant count for the three that build the set internally, in
#: preference to ``magnitude`` (the peak bin alone).
DETECTOR_FIELDS: dict[str, DetectionField] = {
    "rate": DetectionField(
        onset="locs", width="widths", strength="amps",
        strength_unit="intra_event_event_rate_hz", n_roi=None),
    "coact": DetectionField(
        onset="onset_sec", width="width_sec", strength="strength",
        strength_unit="coactivity_z", n_roi="nrois"),
    "sync": DetectionField(
        onset="locs", width="widths", strength="amps",
        strength_unit="spike_synchronization_c", n_roi="n_participating_rois"),
    "loco": DetectionField(
        onset="onset_sec", width="width_sec", strength="strength",
        strength_unit="local_coincidence_coactivity", n_roi="mag_total",
        nested=True),
    "sce": DetectionField(
        onset="onset_sec", width="width_sec", strength="magnitude",
        strength_unit="binned_coactivity_roi_count", n_roi="mag_total",
        nested=True),
    "cicada": DetectionField(
        onset="onset_sec", width="width_sec", strength="magnitude",
        strength_unit="synchronous_cell_count", n_roi="mag_total",
        nested=True),
}

#: Column order of ``detections.csv``, before the carried identity columns.
COLUMNS = ("slice_id", "stream", "detector", "mode", "region_idx", "region_label",
           "onset_sec", "width_sec", "width_def", "n_roi", "strength",
           "strength_unit")


@dataclass
class DetectedEvent:
    """One detected coordinated event — one row of ``detections.csv``.

    ``identity`` carries every column from the producer's ``slices.csv`` through
    untouched. bugarach reads exactly one field of that file (the frame interval)
    and passes the rest along without interpreting it.
    """

    slice_id: str
    stream: str
    detector: str
    mode: str
    onset_sec: float
    width_sec: float
    strength: float
    strength_unit: str
    width_def: str | None = None
    region_idx: int | None = None
    region_label: str | None = None
    n_roi: int | None = None
    identity: dict[str, str] = field(default_factory=dict)

    def row(self) -> dict[str, str]:
        """This event as strings, ready to write. ``None`` becomes :data:`NA`."""
        out = {c: _fmt(getattr(self, c)) for c in COLUMNS}
        # Identity is carried, so it must not be able to overwrite a computed
        # column: a producer whose slices.csv happens to have a `detector` column
        # would otherwise silently replace which detector fired.
        for k, v in self.identity.items():
            if k not in out:
                out[k] = _fmt(v)
        return out


def _fmt(v) -> str:
    """One value as the file spells it.

    A real zero survives as ``0``; only genuine absence becomes ``NA``. NaN counts
    as absence — it is how the detectors spell "not applicable in this mode" — and
    conflating the two is the round-trip bug this is written to avoid.
    """
    if v is None:
        return NA
    if isinstance(v, (float, np.floating)):
        return NA if np.isnan(v) else repr(float(v))
    if isinstance(v, (int, np.integer)):
        return str(int(v))
    s = str(v)
    return NA if s == "" else s


def _settings(result) -> dict:
    """The settings dict, whatever this detector calls it."""
    for name in ("opts", "settings", "params"):
        got = getattr(result, name, None)
        if isinstance(got, dict):
            return got
    return {}


def _mode(result) -> str:
    """``threshold`` or ``peak``, as a value rather than folded into a name.

    Two detectors record it directly in their settings. The rest say it through
    ``width_kind``, because the width they return *is* a different quantity in the
    two modes — which is the more reliable witness of the two, since it comes from
    the branch that ran rather than from the argument that asked.
    """
    kind = getattr(result, "width_kind", None)
    if kind == "half_prominence":
        return "peak"
    mode = _settings(result).get("detection_mode")
    if mode in ("threshold", "peak"):
        return mode
    return "threshold"


def events_from(result, *, detector: str, slice_id: str, stream: str,
                region_idx=None, region_label=None,
                identity: dict[str, str] | None = None) -> list[DetectedEvent]:
    """Normalize one detector's result into rows.

    ``result`` is what the detector returned — either its flat per-stream result,
    or one stream out of a slice-level container's ``streams`` mapping. Pass the
    stream itself for the nested three; this function does not reach into the
    container, because which stream is being written is the caller's decision.

    ``region_idx`` / ``region_label`` are the caller's for the three detectors run
    per-window. The nested three carry a per-event ``region`` of their own, and
    where they do it wins — it is the region the detector actually scored in.
    """
    if detector not in DETECTOR_FIELDS:
        raise ValueError(
            f"unknown detector {detector!r} — have {sorted(DETECTOR_FIELDS)}. "
            f"A new detector needs an entry in DETECTOR_FIELDS, which is also "
            f"where its strength unit gets declared.")
    spec = DETECTOR_FIELDS[detector]
    onset = np.asarray(getattr(result, spec.onset), dtype=float)
    width = np.asarray(getattr(result, spec.width), dtype=float)
    strength = np.asarray(getattr(result, spec.strength), dtype=float)
    n_roi = (None if spec.n_roi is None
             else np.asarray(getattr(result, spec.n_roi)))
    per_event_region = getattr(result, "region", None)
    mode = _mode(result)
    width_def = getattr(result, "width_kind", None)

    n = len(onset)
    if not (len(width) == len(strength) == n):
        raise ValueError(
            f"{detector}: onset/width/strength lengths disagree "
            f"({n}/{len(width)}/{len(strength)}) — these are parallel arrays over "
            f"the same events and a mismatch means the wrong field was read.")

    out = []
    for i in range(n):
        label = region_label
        if per_event_region is not None and i < len(per_event_region):
            label = per_event_region[i]
        out.append(DetectedEvent(
            slice_id=slice_id, stream=stream, detector=detector, mode=mode,
            onset_sec=float(onset[i]), width_sec=float(width[i]),
            strength=float(strength[i]), strength_unit=spec.strength_unit,
            width_def=width_def, region_idx=region_idx, region_label=label,
            n_roi=None if n_roi is None else int(n_roi[i]),
            identity=dict(identity or {})))
    return out


def _columns(events: list[DetectedEvent]) -> list[str]:
    """Header: the fixed columns, then carried identity in first-seen order."""
    cols = list(COLUMNS)
    for e in events:
        for k in e.identity:
            if k not in cols:
                cols.append(k)
    return cols


def write_detections(events, path) -> Path:
    """Write ``detections.csv``. Returns the path written.

    **A slice with no detections writes no rows and is still a real file.** An
    empty result and an absent one must not look alike: the first is a finding, the
    second is a bug. Which slices were looked at belongs in the run sidecar's
    roster, where a reader can tell them apart.
    """
    events = list(events)
    path = Path(path)
    cols = _columns(events)
    with path.open("w", encoding="utf-8", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=cols, lineterminator="\n")
        w.writeheader()
        for e in events:
            w.writerow(e.row())
    return path


def read_detections(path) -> list[dict]:
    """Read one back, undoing :data:`NA` so a round trip compares equal.

    Numeric columns come back as floats or ints and everything else as strings —
    the identity columns included, because they were carried through as text and
    guessing a type for them here would be interpreting what we promised to pass
    along.
    """
    floats = {"onset_sec", "width_sec", "strength"}
    ints = {"region_idx", "n_roi"}
    out = []
    with Path(path).open(encoding="utf-8", newline="") as fh:
        for row in csv.DictReader(fh):
            rec = {}
            for k, v in row.items():
                if v == NA:
                    rec[k] = None
                elif k in floats:
                    rec[k] = float(v)
                elif k in ints:
                    rec[k] = int(v)
                else:
                    rec[k] = v
            out.append(rec)
    return out


def detector_settings_rows(settings: dict[tuple[str, str], dict]) -> list[dict]:
    """``detector, stream, parameter, value`` — one row per parameter.

    Keyed by ``(detector, stream)`` because a detector may run with different
    settings on the fast and slow streams, and a table that could not say so would
    make one of the two unreproducible.
    """
    rows = []
    for (detector, stream), params in settings.items():
        for name in sorted(params):
            rows.append({"detector": detector, "stream": stream,
                         "parameter": name, "value": _fmt(params[name])})
    return rows


def write_detector_settings(settings, path) -> Path:
    """Write ``detector_settings.csv``, so a result reproduces from the folder."""
    path = Path(path)
    with path.open("w", encoding="utf-8", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=("detector", "stream", "parameter",
                                           "value"), lineterminator="\n")
        w.writeheader()
        w.writerows(detector_settings_rows(settings))
    return path


def write_run(path, *, slices, frame_interval_sec, code_version=None,
              generator_spec=None, chosen_k=None, simulated_data_seeds=None,
              thresholds=None, extra=None) -> Path:
    """Write ``run.json`` — the provenance a table of times cannot carry itself.

    ``slices`` is the **roster**: every slice that was analysed, whether or not it
    produced a row. That is the half of the "no detections is not no slice"
    distinction that ``detections.csv`` structurally cannot hold.

    Everything else is optional because a run may not have had it — a straight
    detection pass over a real folder has no generator spec, no chosen K and no
    seeds, and writing ``null`` for those says so honestly rather than
    implying the question was never asked.
    """
    doc = {
        "slices": list(slices),
        "frame_interval_sec": {k: (None if v is None else float(v))
                               for k, v in dict(frame_interval_sec).items()},
        "code_version": code_version,
        "generator_spec": generator_spec,
        "chosen_k": chosen_k,
        "simulated_data_seeds":
            None if simulated_data_seeds is None else list(simulated_data_seeds),
        "thresholds": thresholds,
    }
    if extra:
        doc.update(extra)
    path = Path(path)
    path.write_text(json.dumps(doc, indent=2, sort_keys=True) + "\n",
                    encoding="utf-8")
    return path
