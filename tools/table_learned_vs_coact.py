#!/usr/bin/env python3
"""Every learned model against CoactDetect, on the same home folds, as one table.

    python tools/table_learned_vs_coact.py --runs <bakeoff*.json> ... [--out DIR] [--also DIR]

Reads home runs of ``tools/fair_bakeoff.py`` (never a ``--score-spec`` run: the input is
refused) that share folds and recordings. Runs may hold one learned model or several,
at any ``--train-seed``; the hand-written rows are deterministic and are taken from the
first run that scored them.

WHY AGAINST COACTDETECT. ``docs/pipelines/learned-model-evaluation.md`` puts the licence
for any learned model in this comparison, not in a comparison with its own ablation:
"does the learned family earn its place at all" is the question that decides whether
any of it ships.

For each learned model and each training seed: mean F1 over folds, and the paired
per-fold difference from CoactDetect with *t* on (folds - 1) degrees of freedom. Then
the same on the seed-averaged F1 per fold, which is the column to read when both seeds
exist. A fold with planted events and no hits counts as F1 0 (the rule in
``tools/compare_field_size_candidates.py``). Beside them, from the first training seed:
busy-window false alarms per hour of busy window, quiet-field false alarms per hour at
the quietest null twin when the run recorded them, parameter count and training
seconds per fold.

Writes ``learned_vs_coact.md`` and ``learned_vs_coact.json``; default destination the
darkroom (SAP006), ``--also`` for the repo copy.
"""

from __future__ import annotations

import argparse
import json
import math
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
from compare_field_size_candidates import _f1  # noqa: E402

ORDER = ["tube", "tube_no_bypass", "tube_guard", "tube_ratio", "tube_ratio_guard", "gauge",
         "line", "line_length", "chorus_line", "chorus", "chorus_gain", "chorus_norm",
         "chorus_gain_norm", "trace", "tiny"]
"""Grouped by family, never by score: at four folds these are intervals, not a ranking."""

REFERENCE = "coact"


def _folds(row: dict) -> list[float]:
    return [_f1(f) for f in sorted(row["per_fold"], key=lambda f: f["fold"])]


def _paired(a: list[float], b: list[float]) -> dict:
    d = np.array(a) - np.array(b)
    n = len(d)
    sd = float(d.std(ddof=1)) if n > 1 else float("nan")
    t = float(d.mean() / (sd / math.sqrt(n))) if n > 1 and sd > 0 else float("nan")
    return {"mean": float(d.mean()), "sd": sd, "t": t, "df": n - 1,
            "per_fold": [float(x) for x in d]}


def build(runs: list[dict]) -> dict:
    first = runs[0]
    for r in runs:
        if r.get("transfer"):
            raise SystemExit("a --score-spec run was given; this table is home runs only")
        for key in ("folds", "seeds_per_fold", "seeds"):
            if r[key] != first[key]:
                raise SystemExit(f"runs differ in {key}; they are not the same folds")
    hand = next((r["hand_written"] for r in runs if r["hand_written"]), None)
    if not hand or REFERENCE not in hand:
        raise SystemExit("no run scored CoactDetect on these folds")
    ref = _folds(hand[REFERENCE])

    spec = first["spec"]
    hot = spec.get("hot_window")
    busy_hours = ((hot[1] - hot[0]) * first["seeds_per_fold"] / 3600.0) if hot else None

    by_model: dict[str, dict[int, dict]] = {}
    for r in runs:
        for name, row in r["learned"].items():
            by_model.setdefault(name, {}).setdefault(int(r["train_seed"]), row)

    rows = []
    for name in [m for m in ORDER if m in by_model] + sorted(set(by_model) - set(ORDER)):
        seeds = by_model[name]
        entry = {"model": name, "seeds": sorted(seeds), "by_seed": {}}
        for s in sorted(seeds):
            f = _folds(seeds[s])
            entry["by_seed"][s] = {"f1_mean": float(np.mean(f)), "f1_per_fold": f,
                                   "vs_coact": _paired(f, ref)}
        if len(seeds) > 1:
            avg = list(np.mean([_folds(seeds[s]) for s in sorted(seeds)], axis=0))
            entry["seed_average"] = {"f1_mean": float(np.mean(avg)),
                                     "vs_coact": _paired(avg, ref)}
        base = seeds[min(seeds)]
        folds0 = base["per_fold"]
        entry["probe_per_hour"] = (float(np.mean([f["hot_fa"] for f in folds0])) / busy_hours
                                   if busy_hours else None)
        null = folds0[0].get("null_fa_per_hour") or {}
        if null:
            quietest = min(null, key=float)
            entry["quiet_field"] = {"factor": float(quietest),
                                    "per_hour": float(np.mean(
                                        [f["null_fa_per_hour"][quietest] for f in folds0]))}
        entry["n_params"] = base.get("n_params")
        entry["train_sec_per_fold"] = float(np.mean([f["train_sec"] for f in folds0]))
        rows.append(entry)

    hf = hand[REFERENCE]["per_fold"]
    reference = {"model": REFERENCE, "f1_mean": float(np.mean(ref)), "f1_per_fold": ref,
                 "probe_per_hour": (float(np.mean([f["hot_fa"] for f in hf])) / busy_hours
                                    if busy_hours else None)}
    if hf[0].get("null_fa_per_hour"):
        q = min(hf[0]["null_fa_per_hour"], key=float)
        reference["quiet_field"] = {"factor": float(q), "per_hour": float(np.mean(
            [f["null_fa_per_hour"][q] for f in hf]))}
    return {"produced_by": "tools/table_learned_vs_coact.py", "folds": first["folds"],
            "seeds_per_fold": first["seeds_per_fold"], "n_roi": spec.get("n_roi"),
            "busy_window_hours_per_fold": busy_hours, "reference": reference, "rows": rows}


def _fmt_diff(p: dict) -> str:
    t = "—" if not np.isfinite(p["t"]) else f"{p['t']:+.1f}"
    return f"{p['mean']:+.3f} (*t* {t})"


def markdown(tab: dict) -> str:
    seeds = sorted({s for r in tab["rows"] for s in r["by_seed"]})
    head = ["model"] + [f"F1, seed {s}" for s in seeds] + \
           [f"− CoactDetect, seed {s}" for s in seeds] + \
           ["− CoactDetect, seed average", "probe, per hour", "quiet field, per hour",
            "parameters", "training s per fold"]
    lines = ["| " + " | ".join(head) + " |", "|" + "---|" * len(head)]
    for r in tab["rows"]:
        cells = [r["model"]]
        cells += [f"{r['by_seed'][s]['f1_mean']:.3f}" if s in r["by_seed"] else "not run"
                  for s in seeds]
        cells += [_fmt_diff(r["by_seed"][s]["vs_coact"]) if s in r["by_seed"] else "not run"
                  for s in seeds]
        cells.append(_fmt_diff(r["seed_average"]["vs_coact"]) if "seed_average" in r
                     else "one seed")
        cells.append(f"{r['probe_per_hour']:.1f}" if r["probe_per_hour"] is not None else "—")
        cells.append(f"{r['quiet_field']['per_hour']:.1f}" if "quiet_field" in r else "—")
        cells.append(f"{r['n_params']:,}" if r["n_params"] is not None else "—")
        cells.append(f"{r['train_sec_per_fold']:.0f}")
        lines.append("| " + " | ".join(cells) + " |")
    ref = tab["reference"]
    cells = ["CoactDetect"] + [f"{ref['f1_mean']:.3f}"] * len(seeds) + ["—"] * len(seeds) + \
            ["—", f"{ref['probe_per_hour']:.1f}" if ref["probe_per_hour"] is not None else "—",
             f"{ref['quiet_field']['per_hour']:.1f}" if "quiet_field" in ref else "—",
             "0", "—"]
    lines.append("| " + " | ".join(cells) + " |")
    return "\n".join(lines) + "\n"


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--runs", type=Path, nargs="+", required=True)
    ap.add_argument("--out", default=None, help="default: the darkroom")
    ap.add_argument("--also", default=None, help="a second copy, usually the repo")
    a = ap.parse_args(argv)
    tab = build([json.loads(p.read_text()) for p in a.runs])
    md = markdown(tab)
    out = a.out
    if out is None:
        from bugarach.paths import darkroom
        out = str(darkroom() / "field-size-candidates")
    for d in [out] + ([a.also] if a.also else []):
        Path(d).mkdir(parents=True, exist_ok=True)
        (Path(d) / "learned_vs_coact.json").write_text(json.dumps(tab, indent=1) + "\n")
        (Path(d) / "learned_vs_coact.md").write_text(md)
    print(md)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
