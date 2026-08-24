#!/usr/bin/env python3
"""How many distinct ROIs does each detector say were in the events it reports?

    python tools/survey_participant_counts.py                    # the bench
    python tools/survey_participant_counts.py --folder <path>    # a real export

**Ask each detector for the number it already publishes.** Every one but
`rate_detect` carries a distinct-ROI count in its own contract, and those counts
mean the same thing across the six even though almost nothing else about their
event fields does.

**Do not replace this with a common span rule.** One was tried on 2026-08-24 —
*distinct ROIs with an onset inside `[onset, onset+width]`*, applied to all six —
and it reported `rate_detect` finding **0 ROIs in 94% of its events** and locust in
**83%**. Both were artifacts:

- `rate_detect` has no `ends` field, so the span collapsed to zero width;
- locust's `magnitude` counts cells **active** across its sliding window (painted
  active for the rise interval), not onsets inside its ~0.3 s reported width;
- binned SCE's `onset_sec` is the **bin edge**, not the first participating event —
  one event reads onset 1060.30, width 1.30, nearest event 4.6 s away, own
  magnitude 10.

Six detectors do not share onset semantics. A uniform rule over them produces a
confident wrong answer, which is the failure this file exists to prevent repeating.

**What it found.** SPIKE-synch is the only one of the six that reports events below
its own floor, because it is the only floor that **sums across bins** — SCE, LoCo
and CoactDetect apply `min_rois` per bin to a genuine distinct-ROI count, so every
bin in an episode independently cleared it. locust has no floor at all; on the
approved export folder that costs 45 events in 11,940, every one of them two cells.
Written up in
`docs/todo/2026-08-24-kreuz-answered-the-spike-synch-questions-in-april.md`.
"""
from __future__ import annotations

import argparse
from pathlib import Path

import numpy as np

FLOOR = 3
SEEDS = tuple(range(1, 13))

#: Each detector's own declared distinct-ROI count, per its dataclass contract.
#: `None` means the detector has no participant concept — a pooled population rate
#: does not have participants, and that is a design fact rather than an omission.
FIELD = {
    "rate": None,                       # pooled population rate
    "coact": "nrois",                   # peak/episode-max distinct-ROI coactivity
    "loco": "magnitude",                # distinct ROIs in the firing bin
    "sce": "magnitude",                 # distinct ROIs / bin
    "cicada": "magnitude",              # distinct cells in the sync window (locust)
    "sync": "n_participating_rois",     # distinct ROIs in the detected span
}

#: Shown to people, not used as a key — see ADR-0002.
DISPLAY = {"rate": "rate+context", "coact": "CoactDetect", "loco": "LoCo",
           "sce": "binned SCE", "cicada": "locust", "sync": "SPIKE-synch"}


def _counts(det, field):
    if field is None:
        onset = getattr(det, "onset_sec", None)
        onset = det.locs if onset is None else onset
        return np.full(np.asarray(onset).size, np.nan)
    return np.asarray(getattr(det, field), dtype=float)


def survey_bench(regime: str) -> dict[str, np.ndarray]:
    from bugarach.bench import make_recording, run_detector
    out: dict[str, list] = {n: [] for n in FIELD}
    for seed in SEEDS:
        sl, _ = make_recording(regime, seed)
        for n, f in FIELD.items():
            out[n].append(_counts(run_detector(n, sl), f))
    return {n: (np.concatenate(v) if v else np.empty(0)) for n, v in out.items()}


def survey_folder(folder: Path) -> dict[str, np.ndarray]:
    """The three slice-taking detectors over a real export folder, per stream.

    `rate`, `coact` and `sync` take one stream's trains rather than a slice and are
    left to the bench: this exists to answer the locust question, which is about
    real sparsity and cannot be reproduced in simulation — on the bench, on a null
    recording, and on a null with the fitted background shape, nothing reports an
    event below three.
    """
    from bugarach.bench import OPERATING_POINTS
    from bugarach.detectors.cicada import cicada_detect
    from bugarach.detectors.loco import loco_detect
    from bugarach.detectors.sce import sce_detect
    from bugarach.io import load_folder

    fns = {"cicada": cicada_detect, "sce": sce_detect, "loco": loco_detect}
    out: dict[str, list] = {}
    n_rec = 0
    for sl in load_folder(folder):
        n_rec += 1
        for name, fn in fns.items():
            try:
                det = fn(sl, **OPERATING_POINTS[name].params)
            except Exception as exc:                               # noqa: BLE001
                print(f"  ({DISPLAY[name]} declined one recording: "
                      f"{type(exc).__name__})")
                continue
            for stream_name, st in det.streams.items():
                mag = np.asarray(getattr(st, "magnitude", []), dtype=float)
                if mag.size:
                    out.setdefault(f"{name}/{stream_name}", []).append(mag)
    print(f"recordings read: {n_rec}")
    return {k: np.concatenate(v) for k, v in out.items()}


def report(title: str, res: dict[str, np.ndarray]) -> None:
    print(f"\n=== {title} — each detector's OWN participant count ===")
    print(f"{'detector':<18}{'events':>9}{'median':>8}{'<3':>7}{'%':>7}"
          f"{'==1':>6}{'==2':>6}")
    print("-" * 61)
    for key, v in res.items():
        base, _, stream = key.partition("/")
        label = DISPLAY.get(base, base) + (f" {stream}" if stream else "")
        if not v.size or np.isnan(v).all():
            print(f"{label:<18}{v.size:>9}{'—':>8}{'—':>7}{'—':>7}{'—':>6}{'—':>6}")
            continue
        u = int((v < FLOOR).sum())
        print(f"{label:<18}{v.size:>9}{np.median(v):>8.0f}{u:>7}"
              f"{100 * u / v.size:>7.1f}{int((v == 1).sum()):>6}"
              f"{int((v == 2).sum()):>6}")


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--folder", type=Path, default=None,
                   help="an export folder; omit to survey the bench recording")
    a = p.parse_args()

    if a.folder:
        report(a.folder.name, survey_folder(a.folder))
    else:
        for regime in ("baseline_quiet", "baseline_busy"):
            report(regime, survey_bench(regime))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
