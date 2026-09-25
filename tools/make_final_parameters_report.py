#!/usr/bin/env python3
"""The morning report of the final-parameters night (2026-09-25): the adoption table and Figures 1–2.

    python tools/make_final_parameters_report.py --night <darkroom night folder> \
        [--out <folder>] [--also docs/learned/runs/2026-09-25-final-parameters]

**What it reads**, all under ``--night`` (``<darkroom>/bugarach/2026-09-25-final-parameters``), the
run records of phases 2 and 3 exactly as the two worker sessions wrote them:

* ``064/phase3/candidates.json`` (fast) and ``065/phase3/candidates.json`` (slow, combined): each
  coded detector's shipped point and proposal, fresh-seed scores, bracketing;
* ``064/phase3-chorus-slow-combined/candidates.json``: the slow and combined chorus fits;
* each detector's ``search.json`` (``064/phase2/by-detector/search-fast-<det>``,
  ``065/phase2/search-<bench>/<det>``): the held-out gain and the held-out budgets;
* ``064/phase3-3x3/selection_budgets.json``: every budget on the selection seeds, by the search's
  own gate; ``064/phase3-3x3/cross_stream.json``: the 3 × 3.

**What it decides: nothing.** "Adoptable" is the runbook's strict rule: the held-out gain interval
is above zero, every budget passes on selection, held-out and fresh seeds, and the proposal is
bracketed with a hard limit counted as an open end. The looser reading, where a limit counts as a
bracket, is a separate column, because which rule applies is Tony's.

**What it writes:** ``adoption.json``, ``figure1_fresh_f1.png``, ``figure2_cross_stream.png``, and
``adoption_table.md`` (the table the README includes). It defaults to the darkroom, and ``--also``
copies to the repo.
"""
from __future__ import annotations

import argparse
import json
import math
import shutil
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / "src"))

STREAMS = ("fast", "slow", "combined")
CODED = ("coact", "loco", "sce", "rate", "sync", "cicada")
CHORUS = ("chorus_norm", "chorus_gain_norm")
NAME = {"coact": "CoactDetect", "loco": "LoCo", "sce": "binned SCE", "rate": "rate+context",
        "sync": "SPIKE-synch", "cicada": "locust", "chorus_norm": "chorus_norm",
        "chorus_gain_norm": "chorus_gain_norm"}
REG = ("baseline_quiet", "baseline_busy")


def _load(p: Path) -> dict:
    return json.loads(p.read_text(encoding="utf-8"))


def search_path(night: Path, stream: str, det: str) -> Path:
    if stream == "fast":
        return night / "064" / "phase2" / "by-detector" / f"search-fast-{det}" / "search.json"
    return night / "065" / "phase2" / f"search-{stream}" / det / "search.json"


def fresh_budgets(bench, det: str, row: dict, limit_det: str) -> dict:
    """Every budget on the fresh seeds, from one candidates.json results row."""
    q, b = row["baseline_quiet"], row["baseline_busy"]
    probe = max(q["probe_calls_per_min"], b["probe_calls_per_min"])
    elev = q.get("elevated_calls_per_hour_outside")
    swing = abs(q["precision"] - b["precision"])
    fp = bench.MAX_FALSE_POSITIVES_PER_HOUR[limit_det]
    return dict(
        probe=dict(value=probe, limit=bench.MAX_PROBE_PER_MIN[limit_det],
                   ok=probe <= bench.MAX_PROBE_PER_MIN[limit_det]),
        null=dict(value=row["null_calls_per_hour"], limit=fp, ok=row["null_calls_per_hour"] <= fp),
        elevated_out_quiet=dict(value=elev, limit=fp, ok=elev is not None and elev <= fp),
        precision_swing=dict(value=swing, limit=bench.MAX_PRECISION_DROP[limit_det],
                             ok=swing <= bench.MAX_PRECISION_DROP[limit_det]))


def held_out_budgets(bench, det: str, ho: dict) -> dict:
    """The budgets the search's held-out rows carry. Precision per background is not recorded
    there, so the precision swing is marked as not recorded rather than passed."""
    probe = max(ho["probe_quiet_per_hour"], ho["probe_busy_per_hour"]) / 60.0
    fp = bench.MAX_FALSE_POSITIVES_PER_HOUR[det]
    elev = ho.get("elevated_out_quiet_per_hour")
    crowd = ho.get("crowded_gain_vs_shipped", 0.0)
    return dict(
        probe=dict(value=probe, limit=bench.MAX_PROBE_PER_MIN[det],
                   ok=probe <= bench.MAX_PROBE_PER_MIN[det]),
        null=dict(value=ho["null_per_hour"], limit=fp, ok=ho["null_per_hour"] <= fp),
        elevated_out_quiet=dict(value=elev, limit=fp, ok=elev is not None and elev <= fp),
        crowded=dict(value=crowd, limit=-bench.MAX_CROWDED_DROP,
                     ok=crowd >= -bench.MAX_CROWDED_DROP),
        precision_swing=dict(value=None, limit=bench.MAX_PRECISION_DROP[det], ok=None,
                             note="not recorded in the search's held-out rows"))


def selection_budgets(sel: list[dict], stream: str, det: str, version: str) -> dict | None:
    r = next((x for x in sel if x["stream"] == stream and x["detector"] == det
              and x["version"] == version), None)
    if r is None:
        return None
    lim = r["limits"]
    val = dict(probe=max(r["probe_quiet_per_min"], r["probe_busy_per_min"]),
               null=r["null_per_hour"], elevated_out_quiet=r["elevated_out_quiet_per_hour"],
               precision_swing=r["precision_swing"],
               crowded=(None if r["crowded_mean_f1"] is None
                        else r["crowded_mean_f1"] - r["crowded_reference"]))
    lims = dict(probe=lim["probe_per_min"], null=lim["per_hour"], elevated_out_quiet=lim["per_hour"],
                precision_swing=lim["precision_drop"], crowded=-lim["crowded_drop"])
    return {k: dict(value=val[k], limit=lims[k], ok=bool(r["checks"][k])) for k in r["checks"]}


def under_floor(row: dict) -> dict:
    out = {}
    for reg in REG:
        uf = row[reg].get("under_floor") or {}
        out[reg] = dict(floors=uf.get("floors"), by_participation=uf.get("by_participation"))
    return out


def all_ok(budgets: dict | None) -> bool | None:
    if budgets is None:
        return None
    vals = [b["ok"] for b in budgets.values() if b["ok"] is not None]
    return all(vals)


def failed(budgets: dict | None) -> list[str]:
    return [] if budgets is None else [k for k, b in budgets.items() if b["ok"] is False]


def build(night: Path) -> dict:
    import importlib

    mods = {"fast": "bugarach.bench", "slow": "bugarach.bench_slow",
            "combined": "bugarach.bench_combined"}
    cand = {"fast": _load(night / "064" / "phase3" / "candidates.json")}
    cand["slow"] = cand["combined"] = _load(night / "065" / "phase3" / "candidates.json")
    chorus_rec = {"fast": cand["fast"],
                  "slow": _load(night / "064" / "phase3-chorus-slow-combined" / "candidates.json")}
    chorus_rec["combined"] = chorus_rec["slow"]
    sel = _load(night / "064" / "phase3-3x3" / "selection_budgets.json")["rows"]
    rows = []
    for stream in STREAMS:
        bench = importlib.import_module(mods[stream])
        C = cand[stream]
        for det in CODED:
            M = C["benches"][stream]["detectors"][det]
            search = _load(search_path(night, stream, det))
            ship_fresh = C["results"][stream][f"{det}:shipped"]
            row = dict(stream=stream, detector=det, kind="coded",
                       shipped=dict(params=M["shipped"],
                                    fresh=dict(f1=ship_fresh["mean_f1"],
                                               f1_without_decoys=ship_fresh["mean_f1_without_decoys"]),
                                    budgets=dict(selection=selection_budgets(sel, stream, det, "shipped"),
                                                 held_out=held_out_budgets(
                                                     bench, det, search["held_out"][det]["shipped"]),
                                                 fresh=fresh_budgets(bench, det, ship_fresh, det))),
                       floor=C.get("floor"), under_floor=under_floor(ship_fresh))
            p = M["proposal"]
            if p["name"] != "shipped":
                fr = C["results"][stream][f"{det}:proposal"]
                ho = search["held_out"][det][p["name"]]
                br = p["bracketing"]
                strict = br.get("bracketed") is True
                loose = strict or bool(br.get("only_at_limits"))
                budgets = dict(selection=selection_budgets(sel, stream, det, "proposal"),
                               held_out=held_out_budgets(bench, det, ho),
                               fresh=fresh_budgets(bench, det, fr, det))
                gain = ho["gain_vs_shipped"]
                every = all(all_ok(budgets[k]) is not False for k in budgets)
                row["proposal"] = dict(
                    name=p["name"], params=p["params"],
                    changed={k: [M["shipped"].get(k, search["shipped"][det].get(k)), v]
                             for k, v in p["params"].items()
                             if v != search["shipped"][det].get(k)
                             and not (isinstance(v, float) and math.isnan(v))},
                    held_out_gain=gain, fresh=dict(f1=fr["mean_f1"],
                                                   f1_without_decoys=fr["mean_f1_without_decoys"]),
                    budgets=budgets, every_budget=every,
                    bracketed_strict=strict, bracketed_if_limit_counts=loose,
                    open_axes={k: v["reason"] for k, v in br.get("unbracketed_axes", {}).items()},
                    adoptable_strict=bool(strict and every and gain.get("lo") is not None
                                          and gain["lo"] > 0),
                    adoptable_if_limit_counts=bool(loose and every and gain.get("lo") is not None
                                                   and gain["lo"] > 0),
                    under_floor=under_floor(fr))
            rows.append(row)
        R = chorus_rec[stream]
        for m in CHORUS:
            pick = R["benches"][stream]["chorus"][m]["picked"]
            fr = R["results"][stream][f"chorus:{pick}"]
            rows.append(dict(stream=stream, detector=m, kind="chorus", picked=pick,
                             fresh=dict(f1=fr["mean_f1"], f1_without_decoys=fr["mean_f1_without_decoys"]),
                             budgets=dict(fresh=fresh_budgets(bench, "coact", fr, "coact")),
                             budgets_note="against CoactDetect's budgets, the training rule's anchor",
                             collapsed=fr.get("collapsed"), under_floor=under_floor(fr)))
    xs = _load(night / "064" / "phase3-3x3" / "cross_stream.json")
    return dict(floor="ADR-0008 per-window floor, bench per ADR-0009", rows=rows,
                cross_stream=dict(chosen=xs["chosen"], rows=xs["rows"],
                                  diagonal_all_reproduce=xs["diagonal_check"]["all_reproduce"]))


# ------------------------------------------------------------------ figures

def figure1(rep: dict, dest: Path) -> Path:
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    fig, axes = plt.subplots(1, 3, figsize=(13, 4.6), sharey=True)
    for ax, stream in zip(axes, STREAMS):
        rs = [r for r in rep["rows"] if r["stream"] == stream]
        labels, ship, prop, colors = [], [], [], []
        for r in rs:
            labels.append(NAME[r["detector"]])
            if r["kind"] == "chorus":
                ship.append(float("nan"))
                prop.append(r["fresh"]["f1"])
                colors.append("#6b6a64")
            else:
                ship.append(r["shipped"]["fresh"]["f1"])
                p = r.get("proposal")
                prop.append(p["fresh"]["f1"] if p else float("nan"))
                colors.append("#1f6fb4" if p and p["adoptable_strict"] else
                              "#c9822a" if p else "#6b6a64")
        y = list(range(len(labels)))[::-1]
        ax.scatter(ship, y, marker="o", facecolors="none", edgecolors="#1b1b1a", s=46,
                   label="shipped point", zorder=3)
        ax.scatter(prop, y, marker="D", c=colors, s=40, zorder=4)
        for yi, a, b in zip(y, ship, prop):
            if math.isfinite(a) and math.isfinite(b):
                ax.plot([a, b], [yi, yi], color="#b9b8b2", lw=1, zorder=2)
        ax.set_yticks(y, labels)
        ax.set_xlim(0.6, 0.9)
        ax.set_xlabel(f"{stream} · mean F1, fresh seeds")
        ax.grid(axis="x", color="#e4e3de")
        for s_ in ("top", "right"):
            ax.spines[s_].set_visible(False)
    from matplotlib.lines import Line2D
    handles = [Line2D([], [], marker="o", ls="", mfc="none", mec="#1b1b1a", label="shipped point"),
               Line2D([], [], marker="D", ls="", color="#1f6fb4", label="proposal, adoptable (strict rule)"),
               Line2D([], [], marker="D", ls="", color="#c9822a", label="proposal, not adoptable"),
               Line2D([], [], marker="D", ls="", color="#6b6a64", label="chorus fit the training rule picked")]
    fig.legend(handles=handles, loc="lower center", ncol=4, frameon=False)
    fig.tight_layout(rect=(0, 0.08, 1, 1))
    out = dest / "figure1_fresh_f1.png"
    fig.savefig(out, dpi=160)
    plt.close(fig)
    return out


def figure2(rep: dict, dest: Path) -> Path:
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    import numpy as np

    xs = rep["cross_stream"]
    dets = (*CODED, *CHORUS)
    fig, axes = plt.subplots(2, 4, figsize=(14, 7.2))
    for ax, det in zip(axes.ravel(), dets):
        m = np.full((3, 3), np.nan)
        for i, tuned in enumerate(STREAMS):
            variant = xs["chosen"][det][tuned]
            for j, scored in enumerate(STREAMS):
                r = next((x for x in xs["rows"] if x["det"] == det and x["tuned"] == tuned
                          and x["scored"] == scored and x["variant"] == variant), None)
                if r and "mean_f1" in r:
                    m[i, j] = r["mean_f1"]
        ax.imshow(m, vmin=0.4, vmax=0.9, cmap="Blues")
        for i in range(3):
            for j in range(3):
                if np.isfinite(m[i, j]):
                    ax.text(j, i, f"{m[i, j]:.2f}", ha="center", va="center", fontsize=10,
                            color="white" if m[i, j] > 0.7 else "#1b1b1a",
                            fontweight="bold" if i == j else "normal")
        ax.set_xticks(range(3), STREAMS)
        ax.set_yticks(range(3), STREAMS)
        ax.set_xlabel("scored on (bench)")
        ax.set_ylabel(f"{NAME[det]} · tuned on")
    fig.tight_layout()
    out = dest / "figure2_cross_stream.png"
    fig.savefig(out, dpi=160)
    plt.close(fig)
    return out


# ------------------------------------------------------------------ table

def _v(x):
    """A setting's value as a person reads it: NaN merge gaps mean "do not merge"."""
    if isinstance(x, float):
        if math.isnan(x):
            return "none (no merge)"
        return f"{x:.2g}" if 0 < abs(x) < 1e-3 else f"{x:.10g}"
    return str(x)


def _gain(g):
    if not g or g.get("mid") is None:
        return "—"
    return f"{g['mid']:+.3f} [{g['lo']:+.3f}, {g['hi']:+.3f}]"


def _bud(b):
    if b is None:
        return "not measured"
    ok = all_ok(b)
    miss = [k for k, v in b.items() if v["ok"] is None]
    s = "pass" if ok else "**fail: " + ", ".join(failed(b)) + "**"
    return s + (" (swing not recorded)" if miss else "")


def _uf(u):
    q = u["baseline_quiet"]
    if not q["by_participation"]:
        return "—"
    fl = q["floors"]
    parts = ", ".join(f"{float(k) * 100:.0f}%: {v['under_floor']} under"
                      for k, v in sorted(q["by_participation"].items(), key=lambda kv: float(kv[0])))
    return f"floors {fl['min']}–{fl['max']} ROIs; {parts}"


def table(rep: dict) -> str:
    head = ("| stream | detector | shipped → proposal (settings that change) | held-out gain [95%] | "
            "fresh F1 as scored / without decoys | budgets: selection · held-out · fresh | "
            "bracketed (strict) | bracketed if a limit counts | adoptable (strict) | "
            "planted events under the floor (quiet, fresh seeds) |\n"
            "|---|---|---|---|---|---|---|---|---|---|\n")
    lines = []
    for r in rep["rows"]:
        if r["kind"] == "chorus":
            b = r["budgets"]["fresh"]
            lines.append(
                f"| {r['stream']} | {NAME[r['detector']]} | picked {r['picked'].split('_')[-1].replace('.json', '')} "
                f"| — | {r['fresh']['f1']:.3f} / {r['fresh']['f1_without_decoys']:.3f} | "
                f"— · — · {_bud(b)} (CoactDetect's budgets) | — | — | — | {_uf(r['under_floor'])} |")
            continue
        p = r.get("proposal")
        sb = r["shipped"]["budgets"]
        if not p:
            lines.append(
                f"| {r['stream']} | {NAME[r['detector']]} | shipped; no proposal | — | "
                f"{r['shipped']['fresh']['f1']:.3f} / {r['shipped']['fresh']['f1_without_decoys']:.3f} | "
                f"{_bud(sb['selection'])} · {_bud(sb['held_out'])} · {_bud(sb['fresh'])} | — | — | — | "
                f"{_uf(r['under_floor'])} |")
            continue
        ch = "; ".join(f"`{k}` {_v(a)} → {_v(b)}" for k, (a, b) in p["changed"].items())
        ob = ", ".join(f"{k} ({v})" for k, v in p["open_axes"].items()) or "all interior"
        lines.append(
            f"| {r['stream']} | {NAME[r['detector']]} | {p['name']}: {ch} | {_gain(p['held_out_gain'])} | "
            f"{r['shipped']['fresh']['f1']:.3f} → **{p['fresh']['f1']:.3f}** / "
            f"{p['fresh']['f1_without_decoys']:.3f} | {_bud(p['budgets']['selection'])} · "
            f"{_bud(p['budgets']['held_out'])} · {_bud(p['budgets']['fresh'])} | "
            f"{'yes' if p['bracketed_strict'] else 'no: ' + ob} | "
            f"{'yes' if p['bracketed_if_limit_counts'] else 'no'} | "
            f"{'**yes**' if p['adoptable_strict'] else 'no'} | {_uf(p['under_floor'])} |")
    return head + "\n".join(lines) + "\n"


def main(argv=None) -> int:
    from bugarach.paths import darkroom, unresolved_message

    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("--night", type=Path, required=True,
                    help="the night's darkroom folder, bugarach/2026-09-25-final-parameters")
    ap.add_argument("--out", type=Path, default=None,
                    help="default: <darkroom>/2026-09-25-final-parameters/report")
    ap.add_argument("--also", type=Path, default=None, help="a second copy, e.g. the repo folder")
    a = ap.parse_args(argv)
    if a.out is None:
        root = darkroom(create=True)
        if root is None:
            print(unresolved_message(), file=sys.stderr)
            return 2
        a.out = root / "2026-09-25-final-parameters" / "report"
    a.out.mkdir(parents=True, exist_ok=True)
    rep = build(a.night)
    (a.out / "adoption.json").write_text(json.dumps(rep, indent=1, default=float) + "\n",
                                         encoding="utf-8")
    (a.out / "adoption_table.md").write_text(table(rep), encoding="utf-8")
    written = [a.out / "adoption.json", a.out / "adoption_table.md", figure1(rep, a.out),
               figure2(rep, a.out)]
    if a.also:
        a.also.mkdir(parents=True, exist_ok=True)
        for p in written:
            shutil.copy2(p, a.also / p.name)
    # The README carries the table between two markers, written here so the page and
    # adoption_table.md cannot disagree. Then the page itself goes to the darkroom beside the rest.
    for folder in [x for x in (a.also, a.out) if x]:
        readme = folder / "README.md"
        if readme.exists():
            text = readme.read_text(encoding="utf-8")
            start, end = "<!-- adoption-table:start", "<!-- adoption-table:end -->"
            i, j = text.find(start), text.find(end)
            if i >= 0 and j > i:
                head = text[:text.index("\n", i) + 1]
                readme.write_text(head + table(rep) + text[j:], encoding="utf-8")
                print(f"wrote the table into {readme}")
    if a.also and (a.also / "README.md").exists():
        shutil.copy2(a.also / "README.md", a.out / "README.md")
    for p in written:
        print(f"wrote {p}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
