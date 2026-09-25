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
    # A missing close-events score fails, as `make_admissible` fails it; it never passes by default.
    crowd = ho.get("crowded_gain_vs_shipped")
    return dict(
        probe=dict(value=probe, limit=bench.MAX_PROBE_PER_MIN[det],
                   ok=probe <= bench.MAX_PROBE_PER_MIN[det]),
        null=dict(value=ho["null_per_hour"], limit=fp, ok=ho["null_per_hour"] <= fp),
        elevated_out_quiet=dict(value=elev, limit=fp, ok=elev is not None and elev <= fp),
        crowded=dict(value=crowd, limit=-bench.MAX_CROWDED_DROP,
                     ok=crowd is not None and crowd >= -bench.MAX_CROWDED_DROP),
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


def all_ok(budgets: dict | None) -> bool:
    """Every recorded check passed. A budget set that is missing entirely is a failure: nobody
    checked it, and this report exists because an unchecked candidate once won."""
    if budgets is None:
        return False
    vals = [b["ok"] for b in budgets.values() if b["ok"] is not None]
    return all(vals)


def failed(budgets: dict | None) -> list[str]:
    return [] if budgets is None else [k for k, b in budgets.items() if b["ok"] is False]


def changed_settings(shipped: dict, searched: dict, proposal: dict) -> dict:
    """``{setting: [shipped value, proposed value]}`` against the point ``bench*.py`` SHIPS.

    The search starts from ``searched`` — the shipped point with LoCo and CoactDetect forced into
    their sliding form (``--sliding``) — so comparing against it hides a binned → sliding change
    on a bench whose operating point is binned. A setting the shipped params leave to the
    detector's default is filled from ``searched``; a missing ``window_mode`` means binned."""
    out = {}
    for k in sorted(proposal):
        v = proposal[k]
        base = shipped.get(k, "binned" if k == "window_mode" else searched.get(k))
        nan = lambda x: isinstance(x, float) and math.isnan(x)  # noqa: E731
        if nan(v) and nan(base):
            continue
        if v != base:
            out[k] = [base, v]
    return out


def diag_ci(xs: dict, det: str, stream: str, variant: str) -> list | None:
    """The 95% bootstrap interval over fresh seeds of a version scored on its own bench."""
    r = next((x for x in xs["rows"] if x["det"] == det and x["tuned"] == stream
              and x["scored"] == stream and x["variant"] == variant), None)
    return r.get("mean_f1_ci") if r else None


def participants_per_level() -> dict:
    """``{stream: {participation fraction: participants}}``, read off one planted recording of
    each bench, so the table can say "10% (3 ROIs)" rather than leave the conversion to the
    reader."""
    import importlib

    mods = {"fast": "bugarach.bench", "slow": "bugarach.bench_slow",
            "combined": "bugarach.bench_combined"}
    out = {}
    for stream, mod in mods.items():
        b = importlib.import_module(mod)
        _, gt = b.make_recording("baseline_quiet", 1)
        out[stream] = {f"{e.frac:g}": int(e.n_part) for e in gt.events}
    return out


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
    xs = _load(night / "064" / "phase3-3x3" / "cross_stream.json")
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
                                               f1_without_decoys=ship_fresh["mean_f1_without_decoys"],
                                               ci=diag_ci(xs, det, stream, "shipped")),
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
                every = all(all_ok(budgets[k]) for k in budgets)
                row["proposal"] = dict(
                    name=p["name"], params=p["params"],
                    changed=changed_settings(M["shipped"], search["shipped"][det], p["params"]),
                    held_out_anchor=("sliding at the shipped values"
                                     if search["shipped"][det].get("window_mode", "binned")
                                     != M["shipped"].get("window_mode", "binned")
                                     else "the shipped point"),
                    held_out_gain=gain, fresh=dict(f1=fr["mean_f1"],
                                                   f1_without_decoys=fr["mean_f1_without_decoys"],
                                                   ci=diag_ci(xs, det, stream, "proposal")),
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
            seed = pick.split("_")[-1].replace(".json", "")
            rows.append(dict(stream=stream, detector=m, kind="chorus", picked=pick,
                             fresh=dict(f1=fr["mean_f1"], f1_without_decoys=fr["mean_f1_without_decoys"],
                                        ci=diag_ci(xs, m, stream, seed)),
                             budgets=dict(fresh=fresh_budgets(bench, "coact", fr, "coact")),
                             budgets_note="against CoactDetect's budgets, the training rule's anchor",
                             collapsed=fr.get("collapsed"), under_floor=under_floor(fr)))
    return dict(floor="ADR-0008 per-window floor, bench per ADR-0009", rows=rows,
                participants=participants_per_level(),
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
        labels, ship, prop, colors, sci, pci = [], [], [], [], [], []
        nan2 = [float("nan"), float("nan")]
        for r in rs:
            labels.append(NAME[r["detector"]])
            if r["kind"] == "chorus":
                ship.append(float("nan"))
                sci.append(nan2)
                prop.append(r["fresh"]["f1"])
                pci.append(r["fresh"].get("ci") or nan2)
                colors.append("#6b6a64")
            else:
                ship.append(r["shipped"]["fresh"]["f1"])
                sci.append(r["shipped"]["fresh"].get("ci") or nan2)
                p = r.get("proposal")
                prop.append(p["fresh"]["f1"] if p else float("nan"))
                pci.append((p["fresh"].get("ci") if p else None) or nan2)
                colors.append("#1f6fb4" if p and p["adoptable_strict"] else
                              "#c9822a" if p else "#6b6a64")
        y = list(range(len(labels)))[::-1]
        # Each point's 95% interval over fresh seeds, the shipped point's a little above its row
        # and the proposal's a little below, so neither hides the other.
        for yi, (a0, a1), (b0, b1) in zip(y, sci, pci):
            ax.plot([a0, a1], [yi + 0.12] * 2, color="#1b1b1a", lw=1, zorder=2)
            ax.plot([b0, b1], [yi - 0.12] * 2, color="#8a8983", lw=1, zorder=2)
        for yi, a, b in zip(y, ship, prop):
            if math.isfinite(a) and math.isfinite(b):
                ax.plot([a, b], [yi, yi], color="#d8d7d2", lw=1, zorder=1)
        ax.scatter(prop, [yi - 0.12 for yi in y], marker="D", c=colors, s=40, zorder=4)
        # The shipped circle is drawn last: where the two sit at the same F1 it stays visible.
        ax.scatter(ship, [yi + 0.12 for yi in y], marker="o", facecolors="white",
                   edgecolors="#1b1b1a", s=46, zorder=5)
        ax.set_yticks(y, labels)
        ax.set_xlim(0.6, 0.9)
        ax.set_xlabel(f"{stream} · mean F1, fresh seeds")
        ax.grid(axis="x", color="#e4e3de")
        for s_ in ("top", "right"):
            ax.spines[s_].set_visible(False)
    from matplotlib.lines import Line2D
    handles = [Line2D([], [], marker="o", ls="", mfc="white", mec="#1b1b1a", label="shipped point"),
               Line2D([], [], color="#1b1b1a", lw=1, label="95% interval, shipped"),
               Line2D([], [], color="#8a8983", lw=1, label="95% interval, proposal or chorus"),
               Line2D([], [], color="#d8d7d2", lw=1, label="joins a shipped point to its proposal"),
               Line2D([], [], marker="D", ls="", color="#1f6fb4", label="proposal, adoptable (strict rule)"),
               Line2D([], [], marker="D", ls="", color="#c9822a", label="proposal, not adoptable"),
               Line2D([], [], marker="D", ls="", color="#6b6a64", label="chorus fit the training rule picked")]
    fig.legend(handles=handles, loc="lower center", ncol=4, frameon=False, fontsize=10)
    fig.tight_layout(rect=(0, 0.14, 1, 1))
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
    fig, axes = plt.subplots(2, 4, figsize=(14, 6.6))
    im = None
    for ax, det in zip(axes.ravel(), dets):
        m = np.full((3, 3), np.nan)
        for i, tuned in enumerate(STREAMS):
            variant = xs["chosen"][det][tuned]
            for j, scored in enumerate(STREAMS):
                r = next((x for x in xs["rows"] if x["det"] == det and x["tuned"] == tuned
                          and x["scored"] == scored and x["variant"] == variant), None)
                if r and "mean_f1" in r:
                    m[i, j] = r["mean_f1"]
        im = ax.imshow(m, vmin=0.6, vmax=0.9, cmap="Blues")
        for i in range(3):
            for j in range(3):
                if np.isfinite(m[i, j]):
                    ax.text(j, i, f"{m[i, j]:.2f}", ha="center", va="center", fontsize=12,
                            color="white" if m[i, j] > 0.78 else "#1b1b1a",
                            fontweight="bold" if i == j else "normal")
        ax.set_xticks(range(3), STREAMS)
        ax.set_yticks(range(3), STREAMS)
        ax.set_xlabel("scored on (bench)")
        ax.set_ylabel(f"{NAME[det]} · tuned on")
    fig.tight_layout(rect=(0, 0, 0.93, 1), h_pad=0.6)
    cax = fig.add_axes((0.945, 0.15, 0.012, 0.7))
    fig.colorbar(im, cax=cax, label="mean F1 on fresh seeds (0.6–0.9)")
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


BUDGET_NAME = {"probe": "elevated-rate test, inside the stretch",
               "elevated_out_quiet": "elevated-rate test, outside the stretch",
               "null": "no-coordination recording",
               "precision_swing": "precision swing",
               "crowded": "close-events test"}
"""The glossary's names for the five budgets (``docs/GLOSSARY.md``: *elevated-rate test* and
*close-events test* replaced "probe" and "crowded" on 2026-09-21)."""


def _bud(b):
    """A budget cell. A check that was never measured is named, never folded into "pass"."""
    if b is None:
        return "**not checked**"
    fails = [BUDGET_NAME.get(k, k) for k, v in b.items() if v["ok"] is False]
    unrec = [BUDGET_NAME.get(k, k) for k, v in b.items() if v["ok"] is None]
    s = "pass" if not fails else "**fail: " + ", ".join(fails) + "**"
    return s + (f" ({', '.join(unrec)} not recorded)" if unrec else "")


UNIT = {"bin_width_sec": "s", "merge_gap_sec": "s", "merge_gap_s": "s", "context_win_sec": "s",
        "context_win": "s", "int_win_sec": "s", "rate_win": "s", "guard_sec": "s", "dt": "s",
        "tau_max": "s", "max_gap": "s", "peak_min_distance_sec": "s",
        "excess_threshold_hz": "Hz", "threshold_pctile": "percentile",
        "sce_percentile": "percentile", "sce_min_distance_frames": "frames",
        "n_synchronous_frames": "frames"}
"""The unit each setting is in, so a table cell never carries a bare number (CLAUDE.md)."""


def _vu(k, x):
    u = UNIT.get(k)
    s = _v(x)
    return f"{s} {u}" if u and isinstance(x, (int, float)) and not (
        isinstance(x, float) and math.isnan(x)) else s


def _f1(f: dict) -> str:
    ci = f.get("ci")
    return f"{f['f1']:.3f}" + (f" [{ci[0]:.3f}, {ci[1]:.3f}]" if ci else "")


def _open(p: dict) -> str:
    return ", ".join(f"`{k}` ({v})" for k, v in p["open_axes"].items())


def table(rep: dict) -> str:
    """The decision table: one row per detector × stream."""
    head = ("| stream | detector | settings that change, shipped → proposal | "
            "held-out gain in F1 [95% interval] | fresh F1, shipped → proposal [95% interval] | "
            "fresh F1 without decoy calls, shipped → proposal | bracketed (strict) | "
            "bracketed if a limit counts | adoptable (strict) |\n"
            "|---|---|---|---|---|---|---|---|---|\n")
    lines = []
    for r in rep["rows"]:
        name = NAME[r["detector"]]
        if r["kind"] == "chorus":
            seed = r["picked"].split("_")[-1].replace(".json", "").replace("seed", "training seed ")
            lines.append(f"| {r['stream']} | {name} | the fit the training rule picked ({seed}) | — | "
                         f"{_f1(r['fresh'])} | {r['fresh']['f1_without_decoys']:.3f} | — | — | — |")
            continue
        s, p = r["shipped"], r.get("proposal")
        if not p:
            lines.append(f"| {r['stream']} | {name} | none (no proposal) | — | {_f1(s['fresh'])} | "
                         f"{s['fresh']['f1_without_decoys']:.3f} | — | — | — |")
            continue
        ch = "; ".join(f"`{k}` {_vu(k, a)} → {_vu(k, b)}" for k, (a, b) in p["changed"].items())
        anchor =("" if p["held_out_anchor"] == "the shipped point"
                  else f" (against {p['held_out_anchor']})")
        lines.append(
            f"| {r['stream']} | {name} | {ch} | {_gain(p['held_out_gain'])}{anchor} | "
            f"{_f1(s['fresh'])} → {_f1(p['fresh'])} | "
            f"{s['fresh']['f1_without_decoys']:.3f} → {p['fresh']['f1_without_decoys']:.3f} | "
            f"{'yes' if p['bracketed_strict'] else 'no: ' + _open(p)} | "
            f"{'yes' if p['bracketed_if_limit_counts'] else 'no'} | "
            f"{'**yes**' if p['adoptable_strict'] else 'no'} |")
    return head + "\n".join(lines) + "\n"


def budget_table(rep: dict) -> str:
    """Every budget, for the shipped point and the proposal, on each seed set."""
    head = ("| stream | detector | version | selection seeds 1–48 | held-out seeds 49–96 | "
            "fresh seeds 6000–6023 |\n|---|---|---|---|---|---|\n")
    lines = []
    for r in rep["rows"]:
        name = NAME[r["detector"]]
        if r["kind"] == "chorus":
            lines.append(f"| {r['stream']} | {name} | picked fit | not run | not run | "
                         f"{_bud(r['budgets']['fresh'])} (CoactDetect's limits) |")
            continue
        sliding = (r.get("proposal") or {}).get("held_out_anchor", "the shipped point") \
            != "the shipped point" or r["stream"] == "fast" and r["detector"] in ("coact", "loco")
        for label, v in (("shipped", r["shipped"]), ("proposal", r.get("proposal"))):
            if v is None:
                continue
            b = v["budgets"]
            # Under --sliding, fast CoactDetect and LoCo were searched from the shipped values in
            # their sliding form, while fast ships them binned: the selection and held-out shipped
            # rows, and the held-out close-events reference, are that sliding point's.
            note = (" (the sliding starting point)" if label == "shipped" else
                    " (close-events against the sliding starting point)") if sliding else ""
            lines.append(f"| {r['stream']} | {name} | {label} | {_bud(b['selection'])} | "
                         f"{_bud(b['held_out'])}{note} | {_bud(b['fresh'])} |")
    return head + "\n".join(lines) + "\n"


def floor_table(rep: dict) -> str:
    """Planted events under the floor on the fresh seeds, per stream and background — a property
    of the bench, not of a detector, so one row per stream rather than one per detector."""
    head = ("| stream | background | floors (co-active ROIs) | planted events under the floor, "
            "by participation level (of 120 per level: 24 recordings × 5 events) |\n"
            "|---|---|---|---|\n")
    lines = []
    for stream in STREAMS:
        r = next(x for x in rep["rows"] if x["stream"] == stream and x["kind"] == "coded")
        parts = rep["participants"][stream]
        for reg, lab in (("baseline_quiet", "quiet"), ("baseline_busy", "busy")):
            u = r["under_floor"][reg]
            fl = u["floors"]
            by = sorted(u["by_participation"].items(), key=lambda kv: float(kv[0]))
            cells = ", ".join(f"{float(k) * 100:.0f}% ({parts.get(k, '?')} ROIs): "
                              f"{v['under_floor']}" for k, v in by)
            lines.append(f"| {stream} | {lab} | {fl['min']}–{fl['max']} | {cells} |")
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
    tables = {"adoption-table": table(rep), "budget-table": budget_table(rep),
              "floor-table": floor_table(rep)}
    (a.out / "adoption_table.md").write_text("\n".join(tables.values()), encoding="utf-8")
    written = [a.out / "adoption.json", a.out / "adoption_table.md", figure1(rep, a.out),
               figure2(rep, a.out)]
    if a.also:
        a.also.mkdir(parents=True, exist_ok=True)
        for p in written:
            shutil.copy2(p, a.also / p.name)
    # The README carries each table between two markers, written here so the page and
    # adoption_table.md cannot disagree. Then the page itself goes to the darkroom beside the rest.
    for folder in [x for x in (a.also, a.out) if x]:
        readme = folder / "README.md"
        if readme.exists():
            text = readme.read_text(encoding="utf-8")
            for name, body in tables.items():
                start, end = f"<!-- {name}:start", f"<!-- {name}:end -->"
                i, j = text.find(start), text.find(end)
                if i >= 0 and j > i:
                    text = text[:text.index("\n", i) + 1] + body + text[j:]
            readme.write_text(text, encoding="utf-8")
            print(f"wrote the tables into {readme}")
    if a.also and (a.also / "README.md").exists():
        shutil.copy2(a.also / "README.md", a.out / "README.md")
    for p in written:
        print(f"wrote {p}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
