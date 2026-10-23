"""Build the rater sheet's pilot: synthetic rows, their answer key, the Qualtrics question
script and a local preview.

**Synthetic only.** Real rows wait on Tony's baseline-only release by name
(FOUNDATIONS §5). Nothing here reads a store.

The pilot asks two questions of each row (Tony, 2026-10-22/23):

1. *Where are the coordinated events?* The person clicks them. Each planted row carries six events,
   two each at 30%, 20% and 10% of ROIs, so recall can be read per participation level.
2. *Real or synthetic?* With no real rows yet, half the rows come from the **fitted** field
   (the bench's measured background) and half from the **flat** field (the same mean rate,
   no rate shape and no slow bursts). A rater who sees "real" more often in fitted rows than in
   flat ones can see the difference the fitting made; that is the format test for the real
   question later.

No decoys (ADR-0019). Every row is **15 minutes** of 32 ROIs, the bench's ROI count. The length is one
constant for every row, real or synthetic, ours or Cossart's (Tony, 2026-10-23: *"ideally we take the
x-axis length as constant"*). 15 min fits inside every one of Cossart's 59 DANDI:000219 recordings
(shortest 1153.5 s, ``docs/learned/assessment_cossart.json``) and inside this lab's 20-minute windows.

Outputs go to ``<darkroom>/bugarach/2026-10-23-rater-sheet-pilot/``:

- ``explainer_rater-sheet-pilot-intro_20261023.js``: paste into the opening question (the walk-through);
- ``explainer_rater-sheet-pilot-question_20261023.js``: paste into the row question;
- ``explainer_rater-sheet-pilot-preview_20261023.html``: the same sheet, run locally;
- ``explainer_rater-sheet-pilot-key_20261023.json``: the answer key, which never goes into the survey;
- ``explainer_rater-sheet-pilot-rows_20261023.txt``: the row ids for Loop & Merge.

Names use the estate scheme's explainer layout (armory ``tools/naming``), checked with
``artifact_name.py check``. The pilot is about a method, not a dataset.

    python tools/rater_sheet/make_pilot.py [--out DIR]
"""
from __future__ import annotations

import argparse
import json
import random
from pathlib import Path

import numpy as np

from bugarach import bench
from bugarach.simulate import simulate_coordination

HERE = Path(__file__).resolve().parent
FOLDER = "2026-10-23-rater-sheet-pilot"
STEM = "explainer_rater-sheet-pilot-{}_20261023"   # tools/naming/artifact_name.py build --type explainer

DURATION_SEC = 900.0                 # one x-axis length for every row (see above)
LEVELS = (0.30, 0.20, 0.10)
EVENTS_PER_LEVEL = 2
EVENTS_PER_ROW = EVENTS_PER_LEVEL * len(LEVELS)
MIN_SEP_SEC = 60.0
MARGIN_SEC = 30.0
SEED0 = 20261023

QUIET_HZ = bench.REGIMES["baseline_quiet"]["bg_rate_hz"]
BUSY_HZ = bench.REGIMES["baseline_busy"]["bg_rate_hz"]
TIGHT_JITTER_SEC = bench.BENCH_RECORDING["jitter_sec"]   # 0.105 s, measured on fast
WIDE_JITTER_SEC = 0.5

# One condition per row, run on both fields: timing spread and background. Planted rows mix all
# three participation levels, so each row tests every level.
CONDITIONS = [
    dict(planted=True, jitter_sec=TIGHT_JITTER_SEC, bg="quiet"),
    dict(planted=True, jitter_sec=TIGHT_JITTER_SEC, bg="busy"),
    dict(planted=True, jitter_sec=WIDE_JITTER_SEC, bg="quiet"),
    dict(planted=True, jitter_sec=WIDE_JITTER_SEC, bg="busy"),
    dict(planted=False, jitter_sec=None, bg="busy"),      # nothing planted
]
FIELDS = ("fitted", "flat")


def _recording(field: str) -> dict:
    """The bench recording's background, without its test constructs (ADR-0009, ADR-0019)."""
    d = dict(bench.BENCH_RECORDING)
    for k in ("n_distractors", "distractor_frac", "distractor_window",
              "hot_window", "hot_rate_hz", "ramp_sec", "participation", "n_per_level",
              "jitter_sec", "min_sep_sec", "duration_sec"):
        d.pop(k, None)
    if field == "flat":
        d.update(bg_rate_shape=None, bg_burst_shape=None, bg_burst_bin_sec=60.0)
    return d


def make_row(cond: dict, field: str, seed: int):
    kw = _recording(field)
    planted = cond["planted"]
    s, gt = simulate_coordination(
        duration_sec=DURATION_SEC,
        bg_rate_hz=QUIET_HZ if cond["bg"] == "quiet" else BUSY_HZ,
        participation=LEVELS if planted else (),
        n_per_level=(EVENTS_PER_LEVEL,) * len(LEVELS) if planted else (),
        jitter_sec=cond["jitter_sec"] if planted else TIGHT_JITTER_SEC,
        min_sep_sec=MIN_SEP_SEC, margin_sec=MARGIN_SEC, seed=seed, **kw)
    stream = s.streams["events"]
    trains = [[round(float(t), 1) for t in np.sort(np.asarray(tr, float))] for tr in stream.t50rise]
    events = [dict(time=round(float(np.median(e.onsets)), 2), first=round(min(e.onsets), 2),
                   last=round(max(e.onsets), 2), participation=float(e.frac), n_part=int(e.n_part),
                   rois=[int(r) for r in e.rois]) for e in sorted(gt.events, key=lambda e: e.time)]
    return trains, events


def build(seed0: int = SEED0):
    """Rows for the survey and the key that scores them, in a shuffled order with neutral ids."""
    cells = [(c, f) for f in FIELDS for c in CONDITIONS]
    order = list(range(len(cells)))
    random.Random(seed0).shuffle(order)
    rows, key = {}, {}
    for n, i in enumerate(order, start=1):
        cond, field = cells[i]
        rid = f"r{n:02d}"
        seed = seed0 + i
        trains, events = make_row(cond, field, seed)
        rows[rid] = dict(id=rid, n_roi=len(trains), duration_sec=DURATION_SEC, trains=trains)
        key[rid] = dict(field=field, planted=cond["planted"],
                        jitter_sec=cond["jitter_sec"], background=cond["bg"],
                        bg_rate_hz=QUIET_HZ if cond["bg"] == "quiet" else BUSY_HZ,
                        seed=seed, n_events_total=sum(len(t) for t in trains), events=events)
    return rows, key


def demo_row(seed: int = SEED0 - 1) -> dict:
    """The walk-through's own row: easy, fitted, quiet, never scored. The pointer goes to its first
    event, on the lane of a cell that takes part in it."""
    cond = dict(planted=True, jitter_sec=TIGHT_JITTER_SEC, bg="quiet")
    kw = _recording("fitted")
    s, gt = simulate_coordination(duration_sec=DURATION_SEC, bg_rate_hz=QUIET_HZ, participation=(0.5,),
                                  n_per_level=(4,), jitter_sec=cond["jitter_sec"], min_sep_sec=MIN_SEP_SEC,
                                  margin_sec=MARGIN_SEC, seed=seed, **kw)
    trains = [[round(float(t), 1) for t in np.sort(np.asarray(tr, float))] for tr in s.streams["events"].t50rise]
    first = min(gt.events, key=lambda e: e.time)
    return dict(row=dict(id="demo", n_roi=len(trains), duration_sec=DURATION_SEC, trains=trains),
                event_time=round(float(np.median(first.onsets)), 1),
                lane=int(first.rois[len(first.rois) // 2]))


def question_js(rows: dict) -> str:
    core = (HERE / "rater_raster.js").read_text(encoding="utf-8")
    glue = (HERE / "qualtrics_glue.js").read_text(encoding="utf-8")
    data = "var RATER_ROWS = " + json.dumps(rows, separators=(",", ":")) + ";\n"
    return ("/* Rater sheet pilot, synthetic rows only. Built by tools/rater_sheet/make_pilot.py;"
            " do not edit here. */\n" + data + core + "\n" + glue)


def intro_js(demo: dict) -> str:
    core = (HERE / "rater_raster.js").read_text(encoding="utf-8")
    glue = (HERE / "qualtrics_intro_glue.js").read_text(encoding="utf-8")
    data = "var RATER_DEMO = " + json.dumps(demo, separators=(",", ":")) + ";\n"
    return ("/* Rater sheet pilot: the opening walk-through. Built by tools/rater_sheet/make_pilot.py;"
            " do not edit here. */\n" + data + core + "\n" + glue)


def preview_html(rows: dict, demo: dict) -> str:
    template = (HERE / "preview.template.html").read_text(encoding="utf-8")
    core = (HERE / "rater_raster.js").read_text(encoding="utf-8")
    data = ("var RATER_ROWS = " + json.dumps(rows, separators=(",", ":")) + ";\n"
            "var RATER_DEMO = " + json.dumps(demo, separators=(",", ":")) + ";")
    return template.replace("/*RATER_ROWS*/", data).replace("/*RATER_CORE*/", core)


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--out", type=Path, help="folder to write into (default: the darkroom)")
    args = ap.parse_args(argv)
    if args.out is None:
        from bugarach.paths import darkroom
        args.out = Path(darkroom()) / FOLDER
    args.out.mkdir(parents=True, exist_ok=True)
    rows, key = build()
    demo = demo_row()
    (args.out / (STEM.format("question") + ".js")).write_text(question_js(rows), encoding="utf-8")
    (args.out / (STEM.format("intro") + ".js")).write_text(intro_js(demo), encoding="utf-8")
    (args.out / (STEM.format("preview") + ".html")).write_text(preview_html(rows, demo), encoding="utf-8")
    (args.out / (STEM.format("key") + ".json")).write_text(json.dumps(
        dict(built_by="tools/rater_sheet/make_pilot.py", seed0=SEED0, duration_sec=DURATION_SEC,
             tol_note="scored with bugarach.score.TOL_SEC", rows=key), indent=1), encoding="utf-8")
    (args.out / (STEM.format("rows") + ".txt")).write_text("\n".join(rows) + "\n", encoding="utf-8")
    for p in sorted(args.out.iterdir()):
        print(p)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
