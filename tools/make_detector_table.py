#!/usr/bin/env python3
"""Every detector's numbers for one cohort, in one place — and in two halves.

    python tools/make_detector_table.py --run RUN_DIR --folder EXPORT_FOLDER \
        [--baseline baseline --treatment 'APV+CNQX+GZ'] [--out DIR] [--also DIR]

Tony, 2026-09-08: *"provide a table on the performance of all the detectors on these
data in one place"*. This assembles it from the run's own files rather than having
anyone type it — `docs/learned/bakeoff.md`'s hand-typed table going stale is a defect
this repo already carries a row for in `docs/INDEX.md`.

THE ONE THING THIS FILE EXISTS TO STOP is a reader taking the average of two columns
that are not about the same thing. **Performance and behaviour are separated, and
they cannot be read across:**

* **Scored** — F1, recall, precision, distractors, probe. Ground truth exists, so
  these are performance. They are measured on **simulated** recordings drawn from
  this cohort's own `generator_spec.json`, four folds, and NOT on the recordings.
* **Observed** — calls, rate per minute, participation. These are the real
  recordings, where **no ground truth exists**: nobody has run a MAHICE review on
  this folder, so `RESET.md` §1 applies and not one number here is a hit or a miss.
  A high call count is not a good score and a low one is not a bad one.

And **neither family's two halves are the same instrument**, for different reasons:

* **For the six**, the bake-off CALIBRATED a knob per fold and `bugarach detect` then
  ran on the folder at the SHIPPED operating point, because tuned settings do not
  reach the command line. The `knob` column prints both, and the distance is large:
  five of six shipped values lie outside everything the folds chose.
* **For the learned six**, the Scored row is the mean of FOUR fits, one per held-out
  fold; the Observed row is a FIFTH, separate fit — `run_learned_on_folder.py` trains
  once over the whole simulated corpus and predicts in the same process, because
  nothing persists a model. Same architecture and same recipe; not the same weights
  and not the same threshold.

  ⚠ That paragraph read *"the same fit produced both halves ... so their two rows do
  describe one instrument"* until 2026-09-08, and it is false: **one process is not
  one fit.** It reached the rendered page and a merged PR's description, and was
  caught only when Tony asked for the chain to be confirmed a link at a time.
  `tube_ratio_guard` is the proof — it ran the folder at threshold 0.990819, a value
  none of the four bake-off folds produced.

The scored half is **4-fold cross-validation holding out 2 recordings of 8, NOT
leave-one-out**, at **one training seed per fold** — so the spread it reports is a
property of the data split rather than of the optimiser.

Flags earn a row a warning rather than a footnote nobody reads: a threshold that
stopped on the end of its grid, and a model whose calls do not require more than one
cell (`tools/probe_participation.py`, and the finding in
`docs/todo/2026-09-08-the-ratio-tube-cannot-count-cells.md`).

Output is `detector_table.csv` — one row per detector, every column above — beside a
rendered page. Destination defaults to the darkroom (FOUNDATIONS §5).
"""
from __future__ import annotations

import argparse
import csv
import json
import os
import sys
import tempfile
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))

from bugarach import paths  # noqa: E402
from bugarach.bench import MAX_PROBE_PER_MIN, OPERATING_POINTS  # noqa: E402
from bugarach.detect_folder import DETECTORS  # noqa: E402
from bugarach.ui.app import TITLES  # noqa: E402

#: The public build withholds locust as "sixth" (`ui.app.TITLES`); the darkroom is
#: not the public build, so the one key is overridden here and nowhere else.
NAMES = {**TITLES, "cicada": "locust"}
LEARNED_NAMES = {
    "tube": "tube (centre-surround)", "tube_guard": "tube_guard",
    "tube_ratio": "tube_ratio", "tube_ratio_guard": "tube_ratio_guard",
    # `tiny` is ONE filter shared across every ROI with a bounded per-ROI vote;
    # `trace` is the baseline that gives ROI distinctness up. Naming them the other
    # way round said the opposite of both halves and has been wrong here before.
    "trace": "pooled trace", "tiny": "shared per-ROI filter"}

#: Where the run keeps each thing. Named once so a changed layout is one edit.
SPEC = "02_spec/generator_spec.json"
BAKEOFF = "03_bakeoff/bakeoff.json"
DETECT = "04_detect/detections.csv"
LEARNED_DETECT = "07_learned/detections.csv"
LEARNED_SETTINGS = "07_learned/learned_settings.csv"


def scored(bake: dict):
    """The half with ground truth: per-detector fold statistics from the bake-off."""
    spf = int(bake["seeds_per_fold"])
    n_dis = int(bake["spec"]["n_distractors"]) * spf
    hw = bake["spec"]["hot_window"]
    probe_min = (float(hw[1]) - float(hw[0])) / 60.0 * spf
    out = {}
    for family, keys in (("hand-written", [k for k in DETECTORS if k in bake["hand_written"]]),
                         ("learned", list(bake["learned"]))):
        src = bake["hand_written"] if family == "hand-written" else bake["learned"]
        for key in keys:
            r = src[key]
            pf = r["per_fold"]
            out[key] = dict(
                family=family,
                f1=r["f1"]["mean"], f1_lo=r["f1"]["min"], f1_hi=r["f1"]["max"],
                recall=r["recall"]["mean"], precision=r["precision"]["mean"],
                distractors=sum(f["distractor_hits"] for f in pf) / len(pf),
                n_distractors=n_dis,
                probe_per_min=sum(f["hot_fa"] for f in pf) / len(pf) / probe_min,
                probe_gate=MAX_PROBE_PER_MIN.get(key),
                n_params=r["n_params"],
                n_planted=int(pf[0]["n_planted"]),
                knobs=[f.get("knob_value") for f in pf],
                thresholds=[f.get("threshold") for f in pf])
    return out, n_dis, probe_min


def knob_column(key: str, row: dict) -> str:
    """`calibrated -> shipped` for a hand-written detector; the fitted threshold otherwise.

    The two numbers are the point: the bake-off calibrated one instrument and the
    folder was scored with another. Where the folds disagreed, the range is printed
    rather than a mean — a mean over four knob values is not a knob anyone ran. The
    words "calibrated" and "shipped" live in the column header instead of on every
    row; repeated twelve times they pushed the flags column off the rendered page.
    """
    if key in OPERATING_POINTS:
        op = OPERATING_POINTS[key]
        vals = [v for v in row["knobs"] if v is not None]
        shipped = op.params.get(op.knob)
        if not vals:
            return f"{op.knob}<br>&mdash; &rarr; {shipped:g}"
        lo, hi = min(vals), max(vals)
        got = f"{lo:g}" if lo == hi else f"{lo:g}&ndash;{hi:g}"
        return f"{op.knob}<br>{got} &rarr; {shipped:g}"
    thr = [t for t in row["thresholds"] if t is not None]
    return (f"threshold<br>{min(thr):.4g}&ndash;{max(thr):.4g}"
            if thr else "threshold<br>&mdash;")


def observed(run: Path, folder: Path, *, baseline: str, treatment: str, pad: float):
    """The half without ground truth: what each detector did on the real recordings."""
    from make_before_after_figure import rates
    from probe_participation import tally

    files = [run / DETECT, run / LEARNED_DETECT]
    files = [f for f in files if f.exists()]
    if not files:
        raise SystemExit(f"no detections under {run} — looked for {DETECT} and {LEARNED_DETECT}")

    rows, detectors, streams, missing = rates(folder, *files,
                                              baseline=baseline, treatment=treatment)
    per = {}
    for f in files:
        per.update(tally(f, folder, pad=pad))

    out = {}
    for det in detectors:
        mine = [r for r in rows if r[0] == det]
        # Median OVER RECORDINGS of each recording's own rate, both streams pooled;
        # a mean would be carried by the two busiest recordings in a cohort of six.
        # Indices 4 and 5, not 3 and 4: `rates()` grew a `group` field at index 3
        # on 2026-09-09 for the group-faceted figure. Unpacking by position across
        # a module boundary is what made that a silent multiply-a-string rather
        # than a wrong number — which is the good outcome, and the reason to name
        # the fields here rather than count them.
        b = [r[4] * 60.0 for r in mine]
        t = [r[5] * 60.0 for r in mine]
        d = per.get(det, {})
        chance = d.get("chance", float("nan"))
        pct_lone = (100.0 * d["lone"] / d["n"]) if d.get("n") else float("nan")
        out[det] = dict(
            # EVERY call the detector made on the folder, including the high K+ period
            # and any call the folder places in no declared period — which is what a
            # reader means by "how many calls". The two rate columns beside it are the
            # named periods only, so the three do not add up and must not be made to.
            calls=d.get("n", 0),
            calls_in_the_two_periods=sum(r[6] + r[7] for r in mine),
            baseline_per_min=float(np.median(b)) if b else float("nan"),
            treatment_per_min=float(np.median(t)) if t else float("nan"),
            lone=d.get("lone", 0),
            pct_lone=pct_lone,
            pct_chance=100.0 * chance,
            # The comparable quantity. A raw lone percentage is set by the width the
            # detector declares, not by what it gates on; dividing by the rate for
            # windows of that width thrown at random removes exactly that.
            lone_vs_chance=(pct_lone / (100.0 * chance)
                            if np.isfinite(chance) and chance else float("nan")))
    return out, streams, missing


#: A row is flagged on participation only when its lone rate reaches this share of
#: its OWN chance rate — i.e. when it is APPROACHING dart-throwing.
#:
#: Two drafts got this wrong in the same direction and both looked reasonable.
#: Flagging on the raw percentage put a warning on locust, whose 12% is against a
#: chance of 98% — a fixed 0.3 s declared width, not a defect. Flagging at 0.05x
#: chance still caught locust at 0.13x and the two ratio tubes at 0.06-0.07x, all of
#: which are 8-16x BETTER than chance. On this cohort the ratios fall in two clear
#: groups — 0.00-0.13 for everything that gates on coordination, 0.64-0.75 for the
#: three that barely do — and the flag belongs between them, not inside the first.
#: A difference within the good group is a comparison, and it belongs in the column
#: where a reader can weigh it, not in red where it reads as an accusation.
LONE_VS_CHANCE_FLAG = 0.30


def flags(key: str, sc: dict, ob: dict, settings: dict) -> str:
    """One short warning per row, or nothing. Not a footnote — a column."""
    out = []
    s = settings.get(key)
    if s and s.get("threshold_at_grid_edge") == "yes":
        out.append("threshold on the edge of its grid — a bound, not an operating point")
    r = ob.get("lone_vs_chance", float("nan"))
    if np.isfinite(r) and r >= LONE_VS_CHANCE_FLAG:
        out.append(f"lone calls at {r:.2f}x its own chance rate — its calls are "
                   f"approaching random placement")
    gate = sc.get("probe_gate")
    if gate is not None and sc.get("probe_per_min", 0) > gate:
        out.append(f"probe {sc['probe_per_min']:.1f}/min over its gate of {gate:g}")
    return "; ".join(out)


def build_rows(run: Path, folder: Path, *, baseline: str, treatment: str, pad: float):
    bake = json.loads((run / BAKEOFF).read_text())
    sc, n_dis, probe_min = scored(bake)
    ob, streams, missing = observed(run, folder, baseline=baseline,
                                    treatment=treatment, pad=pad)
    settings = {}
    if (run / LEARNED_SETTINGS).exists():
        for r in csv.DictReader((run / LEARNED_SETTINGS).open()):
            settings.setdefault(r["detector"], r)

    order = [k for k in DETECTORS if k in sc] + [k for k in sc if k not in DETECTORS]
    rows = []
    for key in order:
        s = sc[key]
        o = ob.get(key, {})
        rows.append(dict(
            detector=NAMES.get(key, LEARNED_NAMES.get(key, key)), key=key,
            family=s["family"],
            f1=s["f1"], f1_lo=s["f1_lo"], f1_hi=s["f1_hi"],
            recall=s["recall"], precision=s["precision"],
            distractors=s["distractors"], n_distractors=s["n_distractors"],
            probe_per_min=s["probe_per_min"], probe_gate=s["probe_gate"],
            n_params=s["n_params"], knob=knob_column(key, s),
            calls=o.get("calls", 0),
            calls_in_the_two_periods=o.get("calls_in_the_two_periods", 0),
            baseline_per_min=o.get("baseline_per_min", float("nan")),
            treatment_per_min=o.get("treatment_per_min", float("nan")),
            pct_lone=o.get("pct_lone", float("nan")),
            pct_chance=o.get("pct_chance", float("nan")),
            lone_vs_chance=o.get("lone_vs_chance", float("nan")),
            flags=flags(key, s, o, settings)))
    return rows, bake, streams, missing, n_dis, probe_min


def _num(v, fmt="{:.3f}"):
    return "" if v is None or (isinstance(v, float) and not np.isfinite(v)) else fmt.format(v)


#: The screenshot viewport is 1120 CSS px (`make_generator_figures._render_png`), and
#: a table wider than that is silently CUT rather than scrolled — the first draft of
#: this page lost its flags column and half its header that way, and the HTML looked
#: fine because a browser window is wider than the renderer's.
PAGE_PX = 1080


def _table_html(rows, cols, *, note="", wrap_last=True):
    th = "".join(f"<th style='text-align:{'left' if i < 2 else 'right'};padding:3px 6px;"
                 f"border-bottom:1px solid #bbb;vertical-align:bottom'>{h}</th>"
                 for i, (h, _) in enumerate(cols))
    body = []
    prev = None
    for r in rows:
        rule = ("border-top:2px solid #888" if prev is not None and r["family"] != prev else "")
        prev = r["family"]
        last = len(cols) - 1
        tds = "".join(
            f"<td style='text-align:{'left' if i < 2 else 'right'};padding:3px 6px;{rule};"
            f"white-space:{'normal' if wrap_last and i == last else 'nowrap'}"
            f"{';max-width:230px' if wrap_last and i == last else ''}'>{fn(r)}</td>"
            for i, (_, fn) in enumerate(cols))
        body.append(f"<tr>{tds}</tr>")
    return (f"<div style='font:11.5px system-ui,sans-serif;color:#111;"
            f"max-width:{PAGE_PX}px'>{note}"
            f"<table style='border-collapse:collapse;margin:6px 0 18px;"
            f"table-layout:auto'>"
            f"<tr>{th}</tr>{''.join(body)}</table></div>")


def page_html(rows, bake, *, run: Path, folder: Path, baseline: str, treatment: str,
              n_dis: int, probe_min: float, pad: float, missing) -> str:
    folds, spf = bake.get("folds"), bake.get("seeds_per_fold")
    n_planted = int(bake["learned"][next(iter(bake["learned"]))]["per_fold"][0]["n_planted"])

    scored_cols = [
        ("detector", lambda r: f"<b>{r['detector']}</b>"),
        ("family", lambda r: r["family"]),
        ("F1", lambda r: f"{_num(r['f1'])} <span style='color:#888'>"
                         f"[{_num(r['f1_lo'],'{:.2f}')}-{_num(r['f1_hi'],'{:.2f}')}]</span>"),
        ("recall", lambda r: _num(r["recall"])),
        ("precision", lambda r: _num(r["precision"])),
        (f"distractors<br>covered of {n_dis}", lambda r: _num(r["distractors"], "{:.1f}")),
        ("probe<br>firings/min", lambda r: _num(r["probe_per_min"], "{:.2f}")
         + ("" if r["probe_gate"] is None else
            f" <span style='color:#888'>/{r['probe_gate']:g}</span>")),
        ("params", lambda r: f"{r['n_params']:,}" if r["n_params"] else "0"),
        ("what was fitted<br><span style='font-weight:400;color:#888'>"
         "calibrated &rarr; shipped</span>",
         lambda r: f"<span style='color:#555'>{r['knob']}</span>"),
    ]
    observed_cols = [
        ("detector", lambda r: f"<b>{r['detector']}</b>"),
        ("family", lambda r: r["family"]),
        ("calls<br><span style='font-weight:400;color:#888'>every period</span>",
         lambda r: f"{r['calls']:,}"),
        (f"{baseline}<br>calls/min", lambda r: _num(r["baseline_per_min"], "{:.2f}")),
        (f"{treatment}<br>calls/min", lambda r: _num(r["treatment_per_min"], "{:.2f}")),
        ("calls on<br>&le;1 ROI", lambda r: _num(r["pct_lone"], "{:.1f}%")),
        ("same, thrown<br>at random", lambda r: f"<span style='color:#888'>"
                                                f"{_num(r['pct_chance'], '{:.0f}%')}</span>"),
        ("ratio to<br>chance", lambda r: _num(r["lone_vs_chance"], "{:.2f}")),
        ("flags", lambda r: f"<span style='color:#8b1a1a'>{r['flags']}</span>"),
    ]

    scored_note = (
        f"<b style='font-size:15px'>Scored — against planted truth, on SIMULATED recordings</b><br>"
        f"{folds} folds x {spf} seeds from this cohort's own <code>generator_spec.json</code>; "
        f"{n_planted} planted events and {n_dis} correlated-burst distractors per held-out fold, "
        f"plus {probe_min:g} min of promiscuity probe with nothing coordinated planted. "
        f"F1 is the mean with the fold range beside it — <b>at {folds} folds this is an interval, "
        f"not a ranking</b>.<br>"
        f"<b>{folds}-fold cross-validation, holding out {spf} recordings each time — NOT "
        f"leave-one-out</b>, and <b>one training seed per fold</b>. So the spread is a property "
        f"of the data split, not of the optimiser: a variant moving F1 by less than the fold "
        f"range has shown nothing.<br>"
        f"<span style='color:#8b1a1a'>The probe is a HOT window only.</span> A detector that "
        f"divides by its surround cannot fire where the denominator is large, so a probe of 0 "
        f"is arithmetic rather than evidence; there is no quiet-field negative anywhere in this "
        f"corpus. <code>docs/todo/2026-09-08-the-ratio-tube-cannot-count-cells.md</code>")
    observed_note = (
        f"<b style='font-size:15px'>Observed — on the REAL recordings, where there is no ground "
        f"truth</b><br>"
        f"<b>Nobody has run a MAHICE review on this folder.</b> The events the whole chain above "
        f"was built on are the <b>assessor's clusters at the K it was given</b>, which no person "
        f"judged — <code>derive_spec.py</code> refused until told <code>--unreviewed</code> and "
        f"wrote why into the spec. So not one number below is a hit or a miss "
        f"(<code>RESET.md</code> §1). A high call count is not a good score. Rates are the "
        f"median over recordings of each recording's own calls per minute of the window the "
        f"producer declared, both streams pooled. &le;1 ROI counts calls with at most one ROI "
        f"having an onset within &plusmn;{pad:g} s of the call's own span; a bursting cell counts "
        f"once.<br>"
        f"<b>Read the ratio, not the percentage.</b> A detector's lone fraction is set by the "
        f"width IT declares — locust emits a fixed 0.3 s span, binned SCE the tightness of its "
        f"participants — so each call is matched against windows of its own width placed at "
        f"random times in its own recording. That is the <i>thrown at random</i> column, and it "
        f"runs 90-97% for short calls. <b>12% against a chance of 97% is a detector working.</b>")

    head = (
        f"<div style='font:12px system-ui,sans-serif;color:#111;max-width:{PAGE_PX}px'>"
        f"<b style='font-size:16px'>twelve detectors on {folder.name}</b><br>"
        f"<b style='color:#8b1a1a'>The two tables cannot be read across. NEITHER family's two "
        f"halves are the same instrument</b>, and the reasons differ.<br>"
        f"<b>The six</b> — the bake-off calibrated a knob per fold; <code>bugarach detect</code> "
        f"then ran the folder at the <b>shipped</b> operating point, because tuned settings do "
        f"not reach the command line. <b>Five of six shipped values lie outside everything the "
        f"folds chose</b>; only CoactDetect's overlaps. The <i>what was fitted</i> column prints "
        f"both.<br>"
        f"<b>The learned six</b> — the Scored row is the mean of <b>four fits</b>, one per "
        f"held-out fold. The Observed row is a <b>fifth, separate fit</b>: nothing persists a "
        f"model, so <code>run_learned_on_folder.py</code> trains once over the whole simulated "
        f"corpus and predicts in the same process. Same architecture, same recipe; not the same "
        f"weights and not the same threshold.<br>"
        f"{'<span style=color:#8b1a1a>Recordings lacking one of the two periods and therefore not in the Observed rates: ' + ', '.join(missing) + '</span><br>' if missing else ''}"
        f"<span style='color:#777;font-size:11px'>{run.name} &middot; {BAKEOFF} &middot; "
        f"{DETECT} &middot; {LEARNED_DETECT} &middot; one training seed</span></div>")

    return (head
            + _table_html(rows, scored_cols, note=f"<div style='margin:14px 0 0'>{scored_note}</div>")
            + _table_html(rows, observed_cols, note=f"<div style='margin:2px 0 0'>{observed_note}</div>"))


CSV_COLS = ["detector", "key", "family", "f1", "f1_lo", "f1_hi", "recall", "precision",
            "distractors", "n_distractors", "probe_per_min", "probe_gate", "n_params",
            "knob", "calls", "calls_in_the_two_periods", "baseline_per_min",
            "treatment_per_min", "pct_lone", "pct_chance", "lone_vs_chance", "flags"]


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--run", required=True, type=Path,
                    help="the run directory holding 03_bakeoff/, 04_detect/, 07_learned/")
    ap.add_argument("--folder", required=True, type=Path,
                    help="the export folder those detections were made on")
    ap.add_argument("--baseline", default="baseline")
    ap.add_argument("--treatment", default="APV+CNQX+GZ")
    ap.add_argument("--pad", type=float, default=0.25,
                    help="seconds of timing tolerance when counting a call's ROIs")
    ap.add_argument("--out", type=Path, default=None, help="destination (default: the darkroom)")
    ap.add_argument("--also", type=Path, default=None, help="write a second copy here")
    a = ap.parse_args(argv)

    rows, bake, _streams, missing, n_dis, probe_min = build_rows(
        a.run, a.folder, baseline=a.baseline, treatment=a.treatment, pad=a.pad)

    if a.out is None:
        root = paths.darkroom(create=True)
        if root is None:
            print(paths.unresolved_message(), file=sys.stderr)
            return 2
        a.out = root / "detector_table"
    a.out.mkdir(parents=True, exist_ok=True)

    with (a.out / "detector_table.csv").open("w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=CSV_COLS, lineterminator="\n", extrasaction="ignore")
        w.writeheader()
        w.writerows(rows)
    print(f"wrote {a.out / 'detector_table.csv'}")

    import panel as pn
    from make_generator_figures import _write

    _write(pn.pane.HTML(page_html(rows, bake, run=a.run, folder=a.folder,
                                  baseline=a.baseline, treatment=a.treatment,
                                  n_dis=n_dis, probe_min=probe_min, pad=a.pad,
                                  missing=missing), width=PAGE_PX + 30),
           a.out, "detector_table", png=True)

    if a.also:
        a.also.mkdir(parents=True, exist_ok=True)
        for f in sorted(a.out.glob("detector_table.*")):
            with tempfile.TemporaryDirectory() as td:
                tmp = Path(td) / f.name
                tmp.write_bytes(f.read_bytes())
                os.replace(tmp, a.also / f.name)
        print(f"also {a.also}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
