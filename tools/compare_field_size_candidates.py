#!/usr/bin/env python3
"""Read a home bake-off and its transfer twin, and put the field-size candidates beside their controls.

    python tools/compare_field_size_candidates.py --home <bakeoff.json> \
        --transfer <bakeoff_..._to_....json> [--out DIR] [--also DIR]

Both files come from ``tools/fair_bakeoff.py`` run with the same ``--folds``,
``--seeds-per-fold`` and ``--train-seed``: the first on the home spec, the second with
``--score-spec`` pointed at another corpus. Training is deterministic, so a fold's fit
is the same model in both files and the two can be paired fold by fold.

WHAT IT REPORTS, AND WHY EACH PAIR. Every comparison is one named change, so a
difference has one reading:

* ``gauge`` against ``tube_no_bypass`` -- standardising against the recording's own
  shifted null, and nothing else.
* ``tube_no_bypass`` against ``tube`` -- removing the raw-brightness bypass, which
  ``gauge`` also does. Without this pair a ``gauge`` score confounds the two.
* ``chorus`` against ``line`` -- the spread and loudest-few channels ``chorus`` adds.
* each learned model against ``coact`` (CoactDetect) -- the comparison that decides
  whether a learned model earns its place at all (docs/pipelines/learned-model-evaluation.md).

For each pair and each corpus: the per-fold F1 differences, their mean and a paired
*t* on (folds - 1) degrees of freedom. For each model: the per-fold transfer change
(the other corpus minus home), and false alarms per hour on the quiet-field null twins
when the run recorded them. Four folds make *t* a coarse instrument; the per-fold
values are in the JSON so nobody has to take the mean on trust.

Writes ``field_size_candidates.json`` and ``field_size_candidates.png``. The
destination defaults to the darkroom (SAP006); ``--also`` puts a second copy in the repo.
"""

from __future__ import annotations

import argparse
import json
import math
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402

PAIRS = [("gauge", "tube_no_bypass", "standardise against own null"),
         ("tube_no_bypass", "tube", "remove the bypass"),
         ("chorus", "line", "add spread and loudest-few channels"),
         ("gauge", "coact", "gauge against CoactDetect"),
         ("chorus", "coact", "chorus against CoactDetect"),
         ("tube", "coact", "tube against CoactDetect"),
         ("line", "coact", "line against CoactDetect")]

ORDER = ["tube", "tube_no_bypass", "gauge", "line", "chorus", "coact", "loco"]
"""Grouped by family and control, never sorted by score: at four folds these are
intervals, not an ordering."""

LABEL = {"tube": "tube", "tube_no_bypass": "tube\nno bypass", "gauge": "gauge",
         "line": "line", "chorus": "chorus", "coact": "CoactDetect", "loco": "LoCo"}

HOME, AWAY = "#2a78d6", "#eb6834"
"""Categorical slots one and two of the default palette; validated light-mode, worst
adjacent CVD separation 24.7. Fill also differs (filled home, open away), so identity
never rests on colour alone."""


def _rows(bake: dict) -> dict:
    return {**bake["hand_written"], **bake["learned"]}


def _f1(fold: dict) -> float:
    """A fold's F1, with no hits on planted events counted as 0 rather than dropped.

    ``bench`` returns NaN when recall and precision are both zero or precision is
    undefined, which is right for a single score and wrong for a comparison: dropping
    those folds averages a model over only the folds where it found something, which
    flatters exactly the models that fail to transfer. A fold with planted events and
    no hits scored 0 on them.
    """
    f1 = fold["f1"]
    if f1 is not None and np.isfinite(f1):
        return float(f1)
    if fold.get("n_planted", 0) > 0 and fold.get("n_hit", 0) == 0:
        return 0.0
    return float("nan")


def _per_fold(row: dict) -> list[float]:
    return [_f1(f) for f in sorted(row["per_fold"], key=lambda f: f["fold"])]


def _zeroed(row: dict) -> list[int]:
    """Folds whose NaN F1 was read as 0, so the conversion is on the record."""
    return [f["fold"] for f in row["per_fold"]
            if not (f["f1"] is not None and np.isfinite(f["f1"])) and _f1(f) == 0.0]


def _paired(a: list[float], b: list[float]) -> dict:
    d = np.array(a) - np.array(b)
    d = d[np.isfinite(d)]
    n = len(d)
    out = {"per_fold": [float(x) for x in d], "n": n,
           "mean": float(d.mean()) if n else None}
    if n > 1:
        sd = float(d.std(ddof=1))
        out["sd"] = sd
        out["t"] = float(d.mean() / (sd / math.sqrt(n))) if sd > 0 else None
        out["df"] = n - 1
    return out


def summarise(home: dict, away: dict) -> dict:
    for key in ("folds", "seeds_per_fold", "train_seed"):
        if home[key] != away[key]:
            raise SystemExit(f"the two runs differ in {key}: {home[key]} against "
                             f"{away[key]}, so their folds cannot be paired")
    if not away.get("transfer"):
        raise SystemExit("--transfer is not a transfer run (no --score-spec)")
    h, w = _rows(home), _rows(away)
    models = [m for m in ORDER if m in h and m in w]

    pairs = []
    for a, b, what in PAIRS:
        if a in h and b in h and a in w and b in w:
            pairs.append({"a": a, "b": b, "change": what,
                          "home": _paired(_per_fold(h[a]), _per_fold(h[b])),
                          "transfer": _paired(_per_fold(w[a]), _per_fold(w[b]))})

    per_model = {}
    for m in models:
        entry = {"f1_home": _per_fold(h[m]), "f1_transfer": _per_fold(w[m]),
                 "folds_with_no_hits_read_as_zero": {"home": _zeroed(h[m]),
                                                     "transfer": _zeroed(w[m])},
                 "transfer_change": _paired(_per_fold(w[m]), _per_fold(h[m]))}
        for label, row in (("home", h[m]), ("transfer", w[m])):
            folds = sorted(row["per_fold"], key=lambda f: f["fold"])
            if folds and "null_fa_per_hour" in folds[0] and folds[0]["null_fa_per_hour"]:
                entry[f"null_fa_per_hour_{label}"] = {
                    k: [float(f["null_fa_per_hour"][k]) for f in folds]
                    for k in folds[0]["null_fa_per_hour"]}
        per_model[m] = entry

    return {"produced_by": "tools/compare_field_size_candidates.py",
            "home_spec_n_roi": home["spec"].get("n_roi"),
            "transfer_spec_n_roi": away["score_spec"].get("n_roi"),
            "folds": home["folds"], "seeds_per_fold": home["seeds_per_fold"],
            "train_seed": home["train_seed"],
            "quick": bool(home.get("provenance", {}).get("quick")),
            "models": models, "pairs": pairs, "per_model": per_model}


def draw(summary: dict, path: Path) -> None:
    models = summary["models"]
    pm = summary["per_model"]
    has_null = any("null_fa_per_hour_home" in pm[m] for m in models)
    fig = plt.figure(figsize=(13.5, 8.6 if has_null else 4.8))
    grid = fig.add_gridspec(2 if has_null else 1, len(models),
                            height_ratios=[1.25, 1] if has_null else [1],
                            hspace=0.42, wspace=0.22)
    ax = fig.add_subplot(grid[0, :])
    x = np.arange(len(models))
    for i, m in enumerate(models):
        hf, af = pm[m]["f1_home"], pm[m]["f1_transfer"]
        for fh, fa in zip(hf, af):
            ax.plot([i - 0.15, i + 0.15], [fh, fa], color="#b9b8b0", lw=1, zorder=1)
        ax.scatter([i - 0.15] * len(hf), hf, s=36, color=HOME, zorder=2,
                   edgecolor="#fcfcfb", linewidth=1.5)
        ax.scatter([i + 0.15] * len(af), af, s=36, facecolor="#fcfcfb",
                   edgecolor=AWAY, linewidth=1.8, zorder=2)
    ax.set_xticks(x, [LABEL.get(m, m) for m in models])
    ax.set_ylim(-0.03, 1.0)
    ax.set_ylabel(f"F1 per fold ({summary['folds']} folds)")
    ax.scatter([], [], s=36, color=HOME,
               label=f"home spec, {summary['home_spec_n_roi']} ROIs")
    ax.scatter([], [], s=36, facecolor="#fcfcfb", edgecolor=AWAY, linewidth=1.8,
               label=f"carried to Cossart spec, {summary['transfer_spec_n_roi']} ROIs")
    ax.legend(frameon=False, loc="upper left", fontsize=9)

    styled = [ax]
    if has_null:
        # One small panel per model, background rate on x from busy to quiet, so a
        # model whose false alarms CLIMB as the field empties reads as a rising line.
        factors = sorted(pm[models[0]]["null_fa_per_hour_home"], key=float, reverse=True)
        fx = np.arange(len(factors))
        floor = 0.1
        top = max([floor] + [v for m in models for label in ("home", "transfer")
                             for vals in (pm[m].get(f"null_fa_per_hour_{label}") or {}).values()
                             for v in vals]) * 1.6
        first = None
        for i, m in enumerate(models):
            bx = fig.add_subplot(grid[1, i], sharey=first)
            first = first or bx
            for label, colour, filled, dx in (("home", HOME, True, -0.08),
                                              ("transfer", AWAY, False, 0.08)):
                table = pm[m].get(f"null_fa_per_hour_{label}")
                if not table:
                    continue
                folds = np.array([[max(v, floor) for v in table[f]] for f in factors])
                means = np.array([max(float(np.mean(table[f])), floor) for f in factors])
                bx.plot(fx + dx, means, color=colour, lw=2, zorder=2)
                for j in range(len(factors)):
                    bx.scatter([fx[j] + dx] * folds.shape[1], folds[j], s=18,
                               color=colour if filled else "#fcfcfb",
                               edgecolor=colour, linewidth=1.2, zorder=3)
            bx.set_yscale("log")
            bx.set_ylim(floor * 0.7, top)
            bx.set_xlim(-0.35, len(factors) - 0.65)
            bx.set_xticks(fx, [f"{float(f):g}×" for f in factors], fontsize=8)
            bx.set_xlabel(LABEL.get(m, m).replace("\n", " "), fontsize=9)
            if i == 0:
                bx.set_ylabel("false alarms per hour\nnothing planted (0 drawn at 0.1)")
            else:
                bx.tick_params(labelleft=False)
            styled.append(bx)
        fig.text(0.5, 0.015, "background rate, as a multiple of the spec's own, "
                 "busy to quiet", ha="center", fontsize=9)
    for a in styled:
        a.spines[["top", "right"]].set_visible(False)
        a.grid(axis="y", color="#e6e5df", lw=0.8)
        a.set_axisbelow(True)
    fig.savefig(path, dpi=150, bbox_inches="tight")
    plt.close(fig)


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--home", type=Path, required=True)
    ap.add_argument("--transfer", type=Path, required=True)
    ap.add_argument("--out", default=None, help="default: the darkroom")
    ap.add_argument("--also", default=None, help="a second copy, usually the repo")
    a = ap.parse_args(argv)

    summary = summarise(json.loads(a.home.read_text()),
                        json.loads(a.transfer.read_text()))
    out = a.out
    if out is None:
        from bugarach.paths import darkroom
        out = str(darkroom() / "field-size-candidates")
    for d in [out] + ([a.also] if a.also else []):
        Path(d).mkdir(parents=True, exist_ok=True)
        (Path(d) / "field_size_candidates.json").write_text(
            json.dumps(summary, indent=1, sort_keys=True) + "\n")
        draw(summary, Path(d) / "field_size_candidates.png")
        print(Path(d) / "field_size_candidates.png")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
