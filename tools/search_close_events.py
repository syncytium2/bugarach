#!/usr/bin/env python3
"""Can any of the four map detectors be set to separate close events?

    python tools/search_close_events.py --out <folder>
    python tools/search_close_events.py --out <folder> --seeds 1 --heldout-seeds 1    # smoke

Tony, 2026-11-11, on the first run of ADR-0022's separation axis: *"nothing was optimized or
even built on events this close. lets build some test data sets and see if any of them can be
modified to separate close events"*.

**The test sets** are `bugarach.close_events.make`: each stream's own bench recording with half
the gaps between neighbouring planted events set to one separation. **The score** is per pair
(`bugarach.close_events.pair_score`): a pair is split when each of its two events is matched by
a call of its own, and an isolated event is double-called when two or more calls sit on it.

**What is varied** is each detector's own settings and nothing in its code: the window or bin,
the merge gap, and for count (sliding) its dip split. Everything else stays at the stream's
shipped operating point, and every participation minimum is the recording's own ADR-0008 floor.

**Two stages, on different seeds.**

1. *Select.* Every candidate on the close-event sets at 0.5, 1 and 2 s, and on recordings with
   nothing planted. A candidate is **admissible** when its false calls per hour with nothing
   planted are within the detector's budget on that stream, it double-calls at most
   `MAX_DOUBLE` of isolated events, and it recalls isolated events within `MAX_RECALL_LOSS` of
   the shipped setting. The pick is the admissible candidate with the highest split rate,
   pooled over the three separations.
2. *Report.* The shipped setting and the pick, on seeds the selection never saw, at every
   separation of the axis.

Nothing is installed. The picks are evidence about what the detectors can do, on one generator.
"""

from __future__ import annotations

import argparse
import itertools
import json
import multiprocessing as mp
import os
import sys
import time
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "src"))

SELECT_SEPARATIONS_SEC = (0.5, 1.0, 2.0)
REPORT_SEPARATIONS_SEC = (0.5, 1.0, 2.0, 3.0, 5.0, 10.0)
SELECT_SEED = 8000
"""First selection seed. The report uses the fresh bench seeds from 6000, which no search or
training run has seen, this one included."""
REPORT_SEED = 6000
MAX_DOUBLE = 0.05
"""The largest share of isolated events a candidate may double-call."""
MAX_RECALL_LOSS = 0.05
"""How far below the shipped setting's recall of isolated events a candidate may fall."""
NAME = {"coact": "CoactDetect", "loco": "LoCo", "sce": "binned SCE",
        "count_sliding": "count (sliding)"}
DETECTORS = tuple(NAME)


def _grid(**axes):
    keys = list(axes)
    return [dict(zip(keys, v)) for v in itertools.product(*(axes[k] for k in keys))]


def candidates(det: str) -> list[dict]:
    """The settings tried for one detector, as overrides of the shipped operating point.

    The first is always ``{}``, the shipped setting. Windows and merge gaps reach below the
    ranges ``bench.FULL_GRIDS`` searched, on purpose: those grids were built for a bench with no
    events closer than about 2 s.
    """
    if det == "count_sliding":
        g = _grid(win_sec=(0.3, 0.5, 1.0, 2.0), merge_gap_sec=(0.0, 0.2, 0.5, 1.0, 3.0),
                  split_dip=(None, 0.5))
    elif det == "coact":
        g = _grid(int_win_sec=(0.5, 1.0, 2.0), merge_gap_sec=(0.0, 0.5, 1.0, 2.0),
                  window_mode=("sliding",))
    elif det == "loco":
        g = _grid(bin_width_sec=(0.5, 1.0), merge_gap_sec=(0.5, 1.0, 2.0),
                  window_mode=("sliding",))
        g += _grid(bin_width_sec=(0.5, 1.0), merge_gap_sec=(0.5, 1.0), window_mode=("binned",))
    elif det == "sce":
        g = _grid(bin_width_sec=(0.5, 1.0, 2.0), threshold_pctile=(98.0, 99.5),
                  merge_gap_sec=(0.0,))
    else:
        raise ValueError(det)
    return [{}] + g


def label(det: str, over: dict) -> str:
    if not over:
        return "shipped"
    return ", ".join(f"{k}={v}" for k, v in over.items())


def _run(p, det, s, over):
    """One detector at one candidate. A setting the detector refuses is reported, not raised."""
    try:
        return p.module.run_detector(det, s, **over), None
    except Exception as exc:                                  # noqa: BLE001 (reported per row)
        return None, f"{type(exc).__name__}: {exc}"[:160]


def planted_task(args):
    stream, sep, regime, seed, which = args
    from bugarach import close_events as ce
    from bugarach import stream_profile as sp

    p = sp.profile(stream)
    s, gt = ce.make(stream, sep, regime, seed)
    out = dict(stream=stream, sep=sep, regime=regime, seed=seed, rows={})
    for det, overs in which.items():
        for i, over in overs:
            d, err = _run(p, det, s, over)
            out["rows"][f"{det}|{i}"] = (dict(error=err) if d is None else
                                         ce.pair_score(gt, d, sep, tol_sec=p.module.TOL_SEC))
    return out


def null_task(args):
    stream, seed, which = args
    from bugarach import close_events as ce
    from bugarach import stream_profile as sp

    p = sp.profile(stream)
    s, _ = p.simulate_null(seed)
    hours = float(p.module.NULL_RECORDING.get("duration_sec",
                                              p.recording()["duration_sec"])) / 3600.0
    out = dict(stream=stream, seed=seed, hours=hours, rows={})
    for det, overs in which.items():
        for i, over in overs:
            d, err = _run(p, det, s, over)
            out["rows"][f"{det}|{i}"] = (dict(error=err) if d is None else
                                         dict(n_calls=int(ce.call_spans(d)[0].size)))
    return out


def pool_counts(rows, key):
    from bugarach import close_events as ce

    got = [r["rows"][key] for r in rows if key in r["rows"]]
    errors = sorted({g["error"] for g in got if "error" in g})
    ok = [g for g in got if "error" not in g]
    counts = {f: int(sum(g[f] for g in ok)) for f in ce.FIELDS}
    return counts, errors


def select(stream, det, cands, planted, nulls, budget):
    from bugarach import close_events as ce

    table = []
    for i, over in cands:
        key = f"{det}|{i}"
        mine = [r for r in planted if r["stream"] == stream]
        counts, errors = pool_counts(mine, key)
        nz = [r for r in nulls if r["stream"] == stream and "n_calls" in r["rows"].get(key, {})]
        fph = (sum(r["rows"][key]["n_calls"] for r in nz) / sum(r["hours"] for r in nz)
               if nz else float("nan"))
        table.append(dict(index=i, settings=over, label=label(det, over), errors=errors,
                          counts=counts, false_calls_per_hour=fph, **ce.rates(counts)))
    shipped = table[0]
    for row in table:
        row["admissible"] = bool(
            not row["errors"] and np.isfinite(row["split_rate"])
            and row["false_calls_per_hour"] <= budget
            and row["isolated_double_rate"] <= MAX_DOUBLE
            and row["isolated_recall"] >= shipped["isolated_recall"] - MAX_RECALL_LOSS)
    ok = [r for r in table if r["admissible"]]
    pick = max(ok, key=lambda r: (r["split_rate"], r["isolated_recall"])) if ok else None
    return table, pick


def report_rows(stream, det, entries, planted):
    """Shipped and pick on the report seeds, per separation."""
    from bugarach import close_events as ce

    out = {}
    for name, i in entries.items():
        out[name] = {}
        for sep in REPORT_SEPARATIONS_SEC:
            mine = [r for r in planted if r["stream"] == stream and r["sep"] == sep]
            counts, errors = pool_counts(mine, f"{det}|{i}")
            out[name][f"{sep:g}"] = dict(counts=counts, errors=errors, **ce.rates(counts))
    return out


def text_table(R) -> str:
    lines = []
    for stream, by_det in R["by_stream"].items():
        lines.append(f"\n{stream} · split rate of close pairs by separation (s); "
                     "in brackets, the share of isolated events called twice")
        lines.append(f"  {'':<60}" + "".join(f"{g:>7g}" for g in REPORT_SEPARATIONS_SEC))
        for det, e in by_det.items():
            for name in ("shipped", "pick"):
                if name not in e["report"]:
                    continue
                rep = e["report"][name]
                dbl = np.nanmean([rep[f"{g:g}"]["isolated_double_rate"]
                                  for g in REPORT_SEPARATIONS_SEC])
                tag = "shipped" if name == "shipped" else e["pick"]["label"]
                lines.append(f"  {(NAME[det] + ': ' + tag)[:58]:<60}" + "".join(
                    f"{rep[f'{g:g}']['split_rate']:>7.2f}" for g in REPORT_SEPARATIONS_SEC)
                    + f"   [{dbl:.2f}]")
            if e["pick"] is None:
                lines.append(f"  {NAME[det] + ': no admissible candidate':<60}")
    return "\n".join(lines)


INK = {"coact": "#1f77b4", "loco": "#d62728", "sce": "#7f7f7f", "count_sliding": "#1a7f37"}


def figure_name() -> str:
    """The figure's file name, from the estate's naming tool (never typed by hand)."""
    import subprocess
    from datetime import date

    r = subprocess.run(
        [sys.executable, str(ROOT / "tools" / "naming" / "artifact_name.py"), "build",
         "--type", "recovery", "--ext", "png", "--source", "synth", "--form", "plot",
         "--topic", "close-pairs-split-shipped-against-searched",
         "--date", date.today().strftime("%Y%m%d")],
        capture_output=True, text=True, check=True)
    return r.stdout.strip().splitlines()[-1]


def figure(R, out: Path) -> Path:
    """Split rate against separation: the shipped setting dashed, the searched one solid."""
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    streams = list(R["by_stream"])
    fig, axes = plt.subplots(1, len(streams), figsize=(12.0, 4.3), sharey=True)
    for ax, stream in zip(axes, streams):
        for det in DETECTORS:
            rep = R["by_stream"][stream][det]["report"]
            for name, ls in (("shipped", "--"), ("pick", "-")):
                if name not in rep:
                    continue
                ax.plot(REPORT_SEPARATIONS_SEC,
                        [rep[name][f"{g:g}"]["split_rate"] for g in REPORT_SEPARATIONS_SEC],
                        color=INK[det], lw=1.5, ls=ls, marker="o", ms=3.5,
                        label=f"{NAME[det]}, {'shipped' if name == 'shipped' else 'searched'}")
        ax.set_xscale("log")
        ax.set_xticks(REPORT_SEPARATIONS_SEC, [f"{g:g}" for g in REPORT_SEPARATIONS_SEC],
                      fontsize=8)
        ax.minorticks_off()
        ax.set_ylim(-0.02, 1.02)
        n = R["by_stream"][stream]["count_sliding"]["report"]["shipped"]["1"]["counts"]["n_pairs"]
        ax.set_ylabel(f"{stream} · share of close pairs split ({n} pairs at 1 s)", fontsize=8)
        ax.set_xlabel("separation of the two planted events (s)", fontsize=8)
        ax.tick_params(axis="y", labelsize=8, labelleft=True)
        for side in ("top", "right"):
            ax.spines[side].set_visible(False)
    handles, labels = axes[0].get_legend_handles_labels()
    fig.legend(handles, labels, loc="lower center", ncol=4, fontsize=7.5, frameon=False)
    fig.tight_layout(rect=(0, 0.12, 1, 1))
    path = out / figure_name()
    fig.savefig(path, dpi=170)
    plt.close(fig)
    return path


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--out", type=Path, required=True, help="folder for the summary JSON")
    ap.add_argument("--seeds", type=int, default=12,
                    help="selection recordings per stream, separation and background")
    ap.add_argument("--heldout-seeds", type=int, default=24,
                    help="report recordings per stream, separation and background")
    ap.add_argument("--jobs", type=int, default=max(1, (os.cpu_count() or 2) - 2))
    ap.add_argument("--figure", type=Path, default=None,
                    help="also draw the figure into this folder (the claimed darkroom folder)")
    ap.add_argument("--from-summary", action="store_true",
                    help="draw from the summary already in --out; simulate nothing")
    a = ap.parse_args(argv)
    a.out.mkdir(parents=True, exist_ok=True)
    if a.from_summary:
        if a.figure is None:
            raise SystemExit("--from-summary draws a figure; pass --figure <folder>")
        R = json.loads((a.out / "close_events_search.json").read_text(encoding="utf-8"))
        a.figure.mkdir(parents=True, exist_ok=True)
        print(figure(R, a.figure))
        return

    from bugarach import bench
    from bugarach import stream_profile as sp

    bench.use_spacing("realistic")
    profiles = sp.profiles()
    cands = {det: list(enumerate(candidates(det))) for det in DETECTORS}

    t0 = time.time()
    # The fast stream plants about half as many events per recording, so it gets twice the
    # seeds, as every bench run under realistic spacing does (bench.seed_factor; ADR-0010).
    def seeds(first, n, stream):
        return range(first, first + n * bench.seed_factor(stream))

    planted = [(s, sep, regime, sd, cands) for s, p in profiles.items()
               for sep in SELECT_SEPARATIONS_SEC for regime in p.regimes
               for sd in seeds(SELECT_SEED, a.seeds, s)]
    nulls = [(s, sd, cands) for s in profiles for sd in seeds(SELECT_SEED, a.seeds, s)]
    with mp.get_context("spawn").Pool(a.jobs) as pool:
        sel_rows = pool.map(planted_task, planted, chunksize=1)
        null_rows = pool.map(null_task, nulls, chunksize=1)
    t_select = time.time() - t0

    R = dict(by_stream={})
    report_which = {s: {} for s in profiles}
    for stream, p in profiles.items():
        R["by_stream"][stream] = {}
        for det in DETECTORS:
            budget = float(p.budgets["false_positives_per_hour"][det])
            table, pick = select(stream, det, cands[det], sel_rows, null_rows, budget)
            R["by_stream"][stream][det] = dict(
                budget_false_calls_per_hour=budget, shipped=dict(p.operating_points[det].params),
                selection=table, pick=pick)
            idx = [0] + ([pick["index"]] if pick and pick["index"] != 0 else [])
            report_which[stream][det] = [cands[det][i] for i in idx]

    rep_tasks = [(s, sep, regime, sd, report_which[s]) for s, p in profiles.items()
                 for sep in REPORT_SEPARATIONS_SEC for regime in p.regimes
                 for sd in seeds(REPORT_SEED, a.heldout_seeds, s)]
    t1 = time.time()
    with mp.get_context("spawn").Pool(a.jobs) as pool:
        rep_rows = pool.map(planted_task, rep_tasks, chunksize=1)
    for stream in profiles:
        for det in DETECTORS:
            e = R["by_stream"][stream][det]
            entries = {"shipped": 0}
            if e["pick"] is not None and e["pick"]["index"] != 0:
                entries["pick"] = e["pick"]["index"]
            e["report"] = report_rows(stream, det, entries, rep_rows)

    R["_"] = dict(
        what="settings of the four map detectors that split close pairs (ADR-0022)",
        select=dict(separations_sec=list(SELECT_SEPARATIONS_SEC), first_seed=SELECT_SEED,
                    seeds=a.seeds, fast_seeds_doubled=True, recordings=len(sel_rows), null_recordings=len(null_rows),
                    seconds=round(t_select, 1)),
        report=dict(separations_sec=list(REPORT_SEPARATIONS_SEC), first_seed=REPORT_SEED,
                    seeds=a.heldout_seeds, recordings=len(rep_rows),
                    seconds=round(time.time() - t1, 1)),
        rule=dict(max_isolated_double_rate=MAX_DOUBLE, max_isolated_recall_loss=MAX_RECALL_LOSS,
                  false_calls="within the detector's own budget on that stream"),
        decoys_per_recording=0, spacing="realistic", close_share=0.5,
        profiles={s: p.summary() for s, p in profiles.items()})
    path = a.out / "close_events_search.json"
    path.write_text(json.dumps(R, indent=1, default=float), encoding="utf-8")
    print(path)
    if a.figure is not None:
        a.figure.mkdir(parents=True, exist_ok=True)
        print(figure(R, a.figure))
    print(text_table(R))
    print(f"\nselect: {len(sel_rows)} + {len(null_rows)} recordings in {t_select:.0f} s; "
          f"report: {len(rep_rows)} recordings in {time.time() - t1:.0f} s")


if __name__ == "__main__":
    main()
