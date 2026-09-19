#!/usr/bin/env python3
"""Write the fair comparison's report: tuned nets against tuned coded detectors, for a reader new to it.

    python tools/build_fair_comparison_report.py                     # darkroom only
    python tools/build_fair_comparison_report.py --also docs/learned/tuned_vs_coact/fair_comparison_2026_09_18

Tony, 2026-09-19: *"I'd like a full report from each machine written so someone new can understand.
Include figures to explain conceptually what was done and why."* So the page explains the problem,
the simulation, the contestants and how the comparison was kept fair **before** it shows a result,
and every explanatory figure is drawn from the run's own files or from the bench itself, never from
numbers typed here.

Reads the run's committed summary (``--run``, default
``docs/learned/tuned_vs_coact/fair_comparison_2026_09_18/``): ``results.json`` and ``meta.json``
as the run wrote them, ``crowded_check.json`` (``tools/crowded_check_fair_comparison.py``) and
``fold_draws.json`` (the fitting draws behind Figure 4). Writes ``index.html`` to
``darkroom()/2026-09-18-fair-comparison-run/report/`` by default (sapper SAP006) and a copy to
``--also`` for review and git history.

The page kit (``Svg``, ``figure``, ``page``, ``table``) is ``tools/build_surrogate_report.py``'s,
imported rather than copied: inline SVG only, numbered figures, a light page.
"""

from __future__ import annotations

import argparse
import json
import math
import sys
import time
from pathlib import Path

import numpy as np

REPO = Path(__file__).resolve().parent.parent
sys.path[:0] = [str(REPO / "src"), str(REPO / "tools")]

from build_surrogate_report import Svg, esc, figure, num, page, table  # noqa: E402

from bugarach import bench, provenance  # noqa: E402

DEFAULT_RUN = REPO / "docs" / "learned" / "tuned_vs_coact" / "fair_comparison_2026_09_18"
DARKROOM_FOLDER = "2026-09-18-fair-comparison-run"

NETS = ("chorus_norm", "chorus_gain_norm", "line_length", "tube")
CODED = ("coact", "sce", "loco", "cicada", "sync", "rate")
NAME = {"coact": "CoactDetect", "loco": "LoCo", "rate": "rate+context", "sce": "binned SCE",
        "sync": "SPIKE-synch", "cicada": "locust", "chorus_norm": "chorus_norm",
        "chorus_gain_norm": "chorus_gain_norm", "line_length": "line_length", "tube": "tube"}
SEL = ("ungated", "gated")
SEL_NAME = {"ungated": "F1 alone", "gated": "F1 under the shared budget"}
NET_INK, CODED_INK, REF_INK = "#1b5fa8", "#111", "#b35900"
PLANT_INK, DISTRACT_INK = "#1b5fa8", "#b35900"


# ---- the run's numbers ---------------------------------------------------------------------------

class Run:
    """Everything the page quotes, read once from the committed files."""

    def __init__(self, folder: Path):
        self.folder = folder
        self.results = json.loads((folder / "results.json").read_text())
        self.meta = json.loads((folder / "meta.json").read_text())
        self.decl = self.meta["declaration"]
        self.crowded = json.loads((folder / "crowded_check.json").read_text())
        self.draws = json.loads((folder / "fold_draws.json").read_text())
        self.ran = json.loads((folder / "ran.json").read_text())
        self.folds = list(range(self.decl["folds"]))

    def net_f1(self, m, w):
        """Held-out F1 per outer fold: the mean over the refit seeds of the chosen configuration."""
        return [row[w]["f1_mean"] for row in self.results["learned"][m]]

    def net_seed_f1(self, m, w):
        return [[s["f1"] for s in row[w]["per_seed"]] for row in self.results["learned"][m]]

    def coded_f1(self, d, w):
        return [row[w]["f1"] for row in self.results["hand"][d]]

    def f1(self, name, w):
        return self.net_f1(name, w) if name in NETS else self.coded_f1(name, w)

    def over_budget(self, d, w):
        return [row[w].get("over_budget") for row in self.results["hand"][d]]

    def refused_all(self, d, w):
        """Folds where the budget refused every candidate the search scored."""
        out = []
        for h in self.folds:
            sel = json.loads((self.folder / "selections" / w / f"outer{h}" / f"{d}.json").read_text())
            out.append(bool(sel["n_refused"]) and sel["n_refused"] >= sel["n_scored"])
        return out

    def veto(self, d, w):
        """Goal 1's crowded veto, per outer fold: True passes."""
        got = {(c["outer_fold"], c["selection"]): c for c in self.crowded["choices"]
               if c["detector"] == d}
        return [got[(h, w)]["passes_veto"] for h in self.folds]

    def cmp(self, a, b, w):
        """The run's own paired comparison where it computed one (a net minus a coded detector);
        otherwise the same arithmetic as the tool's ``_paired``, over the same per-fold F1."""
        got = self.results["comparisons"][w].get(f"{a} - {b}")
        if got is not None:
            return got
        d = [x - y for x, y in zip(self.f1(a, w), self.f1(b, w))]
        sd = float(np.std(d, ddof=1))
        return dict(per_fold=d, mean=float(np.mean(d)), sd=sd,
                    t=float(np.mean(d) / (sd / math.sqrt(len(d)))) if sd > 0 else None,
                    df=len(d) - 1)

    def tuning(self, m, w):
        return self.results["comparisons"][w].get(f"{m} tuned - untuned")

    def collapsed(self):
        """Every distinct held-out refit that scored under 0.2 F1, once, with the selections that
        used it: (model, fold, seed, F1, failed-training signature, [selections])."""
        seen: dict = {}
        for m in NETS:
            for row in self.results["learned"][m]:
                for w in ("untuned",) + SEL:
                    for s in row[w]["per_seed"]:
                        if s["f1"] < 0.2:
                            k = (m, row["outer_fold"], row[w]["config_key"], s["seed"])
                            seen.setdefault(k, [m, row["outer_fold"], s["seed"], s["f1"],
                                                s.get("failed_training_signature"), []])[5].append(w)
        return [tuple(v) for v in seen.values()]

    def n_outer_refits(self) -> int:
        return sum(1 for x in self.ran if x["stage"].startswith("outer"))

    def wall_hours(self):
        a = time.mktime(time.strptime(self.meta["started"]["at"][:19], "%Y-%m-%dT%H:%M:%S"))
        progress = json.loads((self.folder / "progress.json").read_text())
        b = time.mktime(time.strptime(progress["at"][:19], "%Y-%m-%dT%H:%M:%S"))
        return (b - a) / 3600.0


def fold_label(h: int) -> str:
    return f"fold {h + 1}"


# ---- figures -------------------------------------------------------------------------------------

FIG1_SEED, FIG1_WINDOW = 1000, (940.0, 1560.0)


def problem_recording():
    """Figure 1's recording, and the facts its caption states, computed rather than typed."""
    sl, gt = bench.make_recording("baseline_busy", FIG1_SEED)
    trains = bench.stream_trains(sl.streams[bench.STREAM], bench.recording_extent(sl))
    t0, t1 = FIG1_WINDOW
    inside = [(t, f) for t, f in zip(gt.times, gt.frac) if t0 <= t <= t1]
    facts = dict(event_t=inside[0][0], event_frac=inside[0][1],
                 n_distractors=int(sum(t0 <= t <= t1 for t in gt.distractor_times)),
                 n_onsets=int(sum(len(t) for t in trains)))
    return sl, gt, trains, facts


def fig_problem() -> Svg:
    """Figure 1: one bench recording, its planted event, distractors and probe, cues in a lane above."""
    _, gt, trains, facts = problem_recording()
    t0, t1 = FIG1_WINDOW
    order = np.argsort([-len(t) for t in trains])          # busiest ROI on top, as encode sorts
    svg = Svg(900, 520, "Figure 1: a raster of 33 ROIs over ten minutes of one simulated bench "
                        "recording, with a lane above marking the planted coordinated event, two "
                        "distractors and the probe stretch")
    x0, x1 = 170, 870
    X = lambda t: x0 + (t - t0) / (t1 - t0) * (x1 - x0)    # noqa: E731
    lane_top, lane_bot = 40, 104
    ras_top, row_h = 124, 10.0
    # --- the lane: nothing is drawn on the raster itself ---
    svg.text(x0 - 12, lane_top + 16, "planted event", anchor="end", size=12)
    svg.text(x0 - 12, lane_top + 38, "distractor", anchor="end", size=12)
    svg.text(x0 - 12, lane_top + 60, "probe stretch", anchor="end", size=12)
    for t in gt.times:
        if t0 <= t <= t1:
            svg.tri(X(t), lane_top + 6, 6, fill=PLANT_INK)
            svg.text(X(t) + 9, lane_top + 16,
                     f"{facts['event_frac']:.0%} of ROIs, spread "
                     f"{bench.BENCH_RECORDING['jitter_sec']:g} s", size=11, fill=PLANT_INK)
    for t in gt.distractor_times:
        if t0 <= t <= t1:
            svg.tri(X(t), lane_top + 28, 6, fill=DISTRACT_INK)
    hot = bench.BENCH_RECORDING["hot_window"]
    ha, hb = X(max(hot[0], t0)), X(min(hot[1], t1))
    for k in range(int((hb - ha) / 7)):
        svg.line(ha + 7 * k, lane_top + 64, ha + 7 * k + 5, lane_top + 52, stroke="#666")
    svg.line(ha, lane_bot - 4, hb, lane_bot - 4, stroke="#666")
    # --- the raster: one ink, one tick per onset ---
    for row, i in enumerate(order):
        y = ras_top + row * row_h
        for t in trains[i]:
            if t0 <= t <= t1:
                svg.line(X(t), y, X(t), y + row_h - 2, w=1.3)
    ras_bot = ras_top + len(order) * row_h
    svg.text(x0 - 12, (ras_top + ras_bot) / 2, "33 ROIs,", anchor="end", size=12)
    svg.text(x0 - 12, (ras_top + ras_bot) / 2 + 15, "busiest on top", anchor="end", size=12)
    svg.time_axis(x0, x1, ras_bot + 8, t0, t1, "time in the recording")
    return svg


def _box(svg, x, y, w, h, label, sub=None, fill="#f2f2f2"):
    svg.rect(x, y, w, h, fill=fill, stroke="#333", sw=1.0)
    svg.text(x + w / 2, y + (h / 2 if sub is None else h / 2 - 4) + 4, label, anchor="middle",
             size=12, weight="bold")
    if sub:
        svg.text(x + w / 2, y + h / 2 + 13, sub, anchor="middle", size=11, fill="#333")


def _arrow(svg, x1, y, x2):
    svg.line(x1, y, x2 - 6, y, w=1.3)
    svg.add(f'<path d="M{x2 - 7:.1f} {y - 4:.1f} L{x2:.1f} {y:.1f} L{x2 - 7:.1f} {y + 4:.1f} Z" '
            f'fill="#111"/>')


def fig_nets() -> Svg:
    """Figure 2: what each of the four nets does to the raster, stage by stage."""
    svg = Svg(900, 470, "Figure 2: four block diagrams, one per learned model, showing where each "
                        "collapses the ROI axis and what it compares against")
    rows = [
        ("tube", [("average the ROIs", "one trace: share of the", "field active"),
                  ("centre minus surround", "at 4 widths, so a flat", "rise cancels"),
                  ("small network", "reads the responses and", "the raw level")]),
        ("line_length", [("each ROI on its own", "smoothed, then a vote", "capped at 1 per frame"),
                         ("share of ROIs lit", "at 4 smoothing widths", ""),
                         ("centre minus surround", "then a small network", "")]),
        ("chorus_norm", [("each ROI on its own", "a learned filter, each", "standardised over time"),
                         ("a vote per ROI", "bounded between 0 and 1", ""),
                         ("pool three ways", "mean, spread, loudest 4", "then a small network")]),
        ("chorus_gain_norm", [("each ROI on its own", "as chorus_norm", ""),
                              ("a vote per ROI", "with a learned gain", "and offset, as line's"),
                              ("pool three ways", "mean, spread, loudest 4", "then a small network")]),
    ]
    bw, gap, first = 168, 24, 246
    for r, (name, stages) in enumerate(rows):
        y = 30 + r * 108
        svg.text(20, y + 38, name, size=13, weight="bold")
        _box(svg, 132, y + 12, 92, 44, "raster", "33 ROIs x time", fill="#fff")
        prev = 224
        for k, (a, b, c) in enumerate(stages):
            bx = first + k * (bw + gap)
            _arrow(svg, prev, y + 34, bx)
            svg.rect(bx, y + 4, bw, 62, fill="#eef3fa" if k == 0 else "#f2f2f2", stroke="#333")
            svg.text(bx + bw / 2, y + 22, a, anchor="middle", size=12, weight="bold")
            svg.text(bx + bw / 2, y + 39, b, anchor="middle", size=11, fill="#333")
            if c:
                svg.text(bx + bw / 2, y + 54, c, anchor="middle", size=11, fill="#333")
            prev = bx + bw
        _arrow(svg, prev, y + 34, prev + 22)
        svg.text(prev + 26, y + 30, "event", size=11, fill="#333")
        svg.text(prev + 26, y + 44, "probability", size=11, fill="#333")
    svg.text(160, 462, "Shaded first box: where the ROI axis is still present. tube removes it "
                       "first; the other three keep each ROI separate until they vote.",
             size=12, fill="#333")
    return svg


def fig_nested(run: Run) -> Svg:
    """Figure 3: the outer folds, and the inner rotation inside one of them."""
    n = run.decl["folds"]
    spf = run.decl["seeds_per_fold"]
    svg = Svg(900, 400, "Figure 3: four outer folds of twelve recording seeds each; for each "
                        "held-out fold the other three train; inside, three inner fits rotate "
                        "which training fold scores")
    x0, cw, ch = 190, 96, 34
    svg.text(20, 26, "A  Outer loop: which fold is scored", size=13, weight="bold")
    for h in range(n):
        y = 44 + h * (ch + 8)
        svg.text(x0 - 12, y + 22, f"held-out {fold_label(h)}", anchor="end", size=12)
        for f in range(n):
            held = f == h
            svg.rect(x0 + f * (cw + 4), y, cw, ch, fill="#333" if held else "#dfe7f2", stroke="#333")
            svg.text(x0 + f * (cw + 4) + cw / 2, y + 22, "scored once" if held else "trains",
                     anchor="middle", size=12, fill="#fff" if held else "#111")
    for f in range(n):
        svg.text(x0 + f * (cw + 4) + cw / 2, 40 + n * (ch + 8) + 14,
                 f"{fold_label(f)}: {spf} seeds", anchor="middle", size=11, fill="#333")
    bx = 620
    svg.text(bx - 10, 26, "B  Inside held-out fold 1: choosing", size=13, weight="bold")
    for j, scored in enumerate((1, 2, 3)):
        y = 44 + j * (ch + 8)
        for f in range(1, n):
            is_scored = f == scored
            svg.rect(bx + (f - 1) * 86, y, 82, ch, fill="#8fb1d8" if is_scored else "#dfe7f2",
                     stroke="#333")
            svg.text(bx + (f - 1) * 86 + 41, y + 22, "scores" if is_scored else "trains",
                     anchor="middle", size=12)
    for f in range(1, n):
        svg.text(bx + (f - 1) * 86 + 41, 44 + 3 * (ch + 8) + 12, fold_label(f), anchor="middle",
                 size=11, fill="#333")
    svg.text(bx, 44 + 3 * (ch + 8) + 34, "3 inner fits x 3 training seeds per", size=12)
    svg.text(bx, 44 + 3 * (ch + 8) + 50, "candidate; fold 1 is never touched", size=12)
    svg.text(20, 262, "Every candidate — 24 configurations per net, or a coded detector's search", size=13)
    svg.text(20, 282, "— is judged in panel B on the training folds alone. Only the one chosen is then",
             size=13)
    svg.text(20, 302, "retrained on all three training folds and scored on the held-out fold, at 5 "
                      "training seeds.", size=13)
    svg.text(20, 330, "Each seed is simulated at both backgrounds, so a fold holds 24 recordings "
                      f"({spf} seeds x 2).", size=13, fill="#333")
    return svg


def fig_defect(run: Run) -> Svg:
    """Figure 4: which recordings each outer refit fitted at seed 0, before the fix and as run."""
    d = run.draws
    seeds = sorted(int(s) for s in d["fold_of"])
    fold_of = {int(k): v for k, v in d["fold_of"].items()}
    svg = Svg(900, 420, "Figure 4: for each held-out fold, the ten training recordings fitted at "
                        "training seed 0, under the order used before the fix and as this run drew "
                        "them")
    x0, x1 = 200, 880
    cell = (x1 - x0) / len(seeds)

    def strip(y, h, info, label):
        svg.text(x0 - 12, y + 12, label, anchor="end", size=12)
        fitted = {int(r.split(":")[1]) for r in info["fitted"]}
        thr = {int(r.split(":")[1]) for r in info["threshold"]}
        for k, s in enumerate(seeds):
            x = x0 + k * cell
            if fold_of[s] == h:
                svg.rect(x, y, cell - 1, 16, fill="#333")
            elif s in fitted:
                svg.rect(x, y, cell - 1, 16, fill=NET_INK)
            elif s in thr:
                svg.rect(x, y, cell - 1, 16, fill=REF_INK)
            else:
                svg.rect(x, y, cell - 1, 16, fill="#e6e6e6")

    for panel, (key, title) in enumerate((("before_fix", "A  Before the fix: contiguous order"),
                                          ("as_run", "B  As this run drew them: dealt across folds"))):
        top = 30 + panel * 176
        svg.text(20, top, title, size=13, weight="bold")
        for h in run.folds:
            strip(top + 14 + h * 26, h, d[key][str(h)], f"held-out {fold_label(h)}")
        distinct = len({tuple(v["fitted"]) for v in d[key].values()})
        svg.text(x0, top + 14 + 4 * 26 + 14,
                 f"{distinct} distinct fitting sets for 4 held-out folds", size=12,
                 weight="bold", fill="#b00" if distinct < 4 else "#060")
    for f in run.folds:
        xa = x0 + f * 12 * cell
        svg.text(xa + 6 * cell, 404, f"{fold_label(f)}: seeds {seeds[12 * f]}–{seeds[12 * f + 11]}",
                 anchor="middle", size=11, fill="#333")
    lx = 20
    for ink, lab in ((NET_INK, "fitted"), (REF_INK, "picks the threshold"), ("#333", "held out"),
                     ("#e6e6e6", "not used at this seed")):
        svg.rect(lx, 372, 12, 12, fill=ink, stroke="#999")
        svg.text(lx + 18, 382, lab, size=12)
        lx += 170
    return svg


def fig_budget(run: Run) -> Svg:
    """Figure 5: the two selections, drawn as a schematic."""
    svg = Svg(900, 380, "Figure 5: a schematic of the two selections: the best F1 anywhere, and the "
                        "best F1 among candidates that fire no more than 1.6 times the reference "
                        "CoactDetect")
    x0, x1, y0, y1 = 110, 560, 40, 300
    svg.line(x0, y1, x1, y1)
    svg.line(x0, y0, x0, y1)
    svg.text((x0 + x1) / 2, y1 + 34, "false alarms per hour (probe, and the quiet empty recording)",
             anchor="middle", size=12)
    svg.add(f'<text x="30" y="{(y0 + y1) / 2}" font-size="12" transform="rotate(-90 30 '
            f'{(y0 + y1) / 2})" text-anchor="middle">F1 on the training folds</text>')
    rs = np.random.RandomState(7)
    fa = rs.uniform(0.05, 0.95, 26)
    f1 = 0.45 + 0.35 * np.sqrt(fa) + rs.normal(0, 0.035, 26)
    ref_fa = 0.30
    budget = ref_fa * run.decl["budget_margin"]
    X = lambda v: x0 + v * (x1 - x0)                      # noqa: E731
    Y = lambda v: y1 - (v - 0.4) / 0.5 * (y1 - y0)        # noqa: E731
    svg.rect(X(budget), y0, x1 - X(budget), y1 - y0, fill="#f4f4f4")
    svg.line(X(budget), y0, X(budget), y1, stroke="#555", dash="5 4")
    svg.text(X(budget) + 8, y1 - 26, "outside the budget:", size=12, fill="#555")
    svg.text(X(budget) + 8, y1 - 10, f"over {run.decl['budget_margin']:g} x the reference's rate",
             size=12, fill="#555")
    for a, b in zip(fa, f1):
        svg.circle(X(a), Y(b), 4, fill="#777")
    ung = int(np.argmax(f1))
    inside = np.where(fa <= budget)[0]
    gat = inside[int(np.argmax(f1[inside]))]
    svg.circle(X(fa[ung]), Y(f1[ung]), 7, fill="none", stroke="#111")
    svg.text(X(fa[ung]) - 12, Y(f1[ung]) + 4, "chosen on F1 alone", anchor="end", size=12)
    svg.circle(X(fa[gat]), Y(f1[gat]), 7, fill="none", stroke=NET_INK)
    svg.text(X(fa[gat]) - 10, Y(f1[gat]) - 12, "chosen under the budget", anchor="end", size=12,
             fill=NET_INK)
    svg.add(f'<path d="M{X(ref_fa) - 6:.1f} {Y(0.66) - 6:.1f} h12 v12 h-12 Z" fill="{REF_INK}"/>')
    svg.text(X(ref_fa) + 10, Y(0.66) + 18, "reference CoactDetect", size=12, fill=REF_INK)
    svg.text(600, 60, "Schematic: the points are illustrative,", size=12, fill="#333")
    svg.text(600, 78, "not candidates from this run.", size=12, fill="#333")
    svg.text(600, 118, "The budget is measured per outer fold,", size=12)
    svg.text(600, 136, "on that fold's training recordings,", size=12)
    svg.text(600, 154, "from the reference's own firing rate:", size=12)
    svg.text(600, 172, "in the probe stretch at each background,", size=12)
    svg.text(600, 190, "and on the quiet recording with nothing", size=12)
    svg.text(600, 208, "planted. A candidate must stay within", size=12)
    svg.text(600, 226, f"{run.decl['budget_margin']:g} times both. Every model and", size=12)
    svg.text(600, 244, "detector faces the same budget.", size=12)
    return svg


def fig_draws(run: Run) -> Svg:
    """Figure 6: this run's recordings and the replicate's, sharing nothing but the design."""
    seeds = run.decl["recording_seeds"]
    svg = Svg(900, 300, "Figure 6: two strips of 48 recording seeds, 1000 to 1047 on WSMIP064 and "
                        "2000 to 2047 on WSMIP065, with the same configurations, grids and training "
                        "seeds applied to both")
    x0, x1 = 230, 880
    cell = (x1 - x0) / len(seeds)
    for r, (label, first, ink) in enumerate((("this run, WSMIP064", seeds[0], NET_INK),
                                             ("replicate 1, WSMIP065", seeds[0] + 1000, REF_INK))):
        y = 40 + r * 70
        svg.text(x0 - 12, y + 16, label, anchor="end", size=12, weight="bold")
        for k in range(len(seeds)):
            svg.rect(x0 + k * cell, y, cell - 1, 22, fill=ink if (k // 12) % 2 == 0 else "#9db8d8"
                     if ink == NET_INK else "#e0b48a")
        svg.text(x0, y + 40, f"recording seeds {first}–{first + len(seeds) - 1}, 4 folds of 12, "
                             "each seed at both backgrounds", size=12, fill="#333")
    svg.text(40, 200, "The same in both: the 24 configurations per net, the coded detectors' grids, "
                      "the training seeds,", size=13)
    svg.text(40, 220, "the budget rule, the simulator. Different: every recording. No recording "
                      "appears in both.", size=13)
    svg.text(40, 250, "So a margin that holds in both draws is a property of the models, not of "
                      "which 48 recordings", size=13)
    svg.text(40, 270, "were drawn. The two runs report separately; their folds are not pooled.",
             size=13)
    return svg


def fig_results(run: Run) -> Svg:
    """Figure 7: held-out F1 per outer fold for all ten contestants, both selections."""
    names = list(NETS) + list(CODED)
    svg = Svg(900, 520, "Figure 7: held-out F1 per outer fold, one row per contestant, two panels "
                        "for the two selections")
    lo, hi = 0.2, 0.85
    panels = ((170, 510, "ungated"), (560, 890, "gated"))
    top, row = 58, 38
    for x0, x1, w in panels:
        X = lambda v, a=x0, b=x1: a + (v - lo) / (hi - lo) * (b - a)   # noqa: E731
        svg.text((x0 + x1) / 2, 22, f"{SEL_NAME[w]} ({w})", anchor="middle", size=13, weight="bold")
        yb = top + len(names) * row
        svg.line(x0, yb, x1, yb)
        for v in (0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8):
            svg.line(X(v), top - 6, X(v), yb, stroke="#eee")
            svg.line(X(v), yb, X(v), yb + 4)
            svg.text(X(v), yb + 18, f"{v:.1f}", anchor="middle", size=11)
        svg.text((x0 + x1) / 2, yb + 38, "held-out F1", anchor="middle", size=12)
        for i, m in enumerate(names):
            y = top + i * row + row / 2
            vals = run.f1(m, w)
            ink = NET_INK if m in NETS else CODED_INK
            flags = [True] * len(vals)
            if m in CODED:
                veto = run.veto(m, w)
                refused = run.refused_all(m, w)
                flags = [v and not r for v, r in zip(veto, refused)]
            for v, ok in zip(vals, flags):
                svg.circle(X(v), y, 4.2, fill=ink if ok else "none", stroke=ink)
            mean = float(np.mean(vals))
            svg.line(X(mean), y - 10, X(mean), y + 10, stroke=ink, w=2.2)
    for i, m in enumerate(names):
        y = top + i * row + row / 2
        svg.text(160, y + 4, NAME[m], anchor="end", size=12,
                 fill=NET_INK if m in NETS else CODED_INK, weight="bold" if m == "coact" else "normal")
    svg.text(20, top + 2 * row - 26, "nets", size=11, fill=NET_INK)
    svg.text(20, top + len(NETS) * row + 12, "coded", size=11)
    svg.line(20, top + len(NETS) * row, 890, top + len(NETS) * row, stroke="#bbb", dash="3 3")
    svg.circle(180, 505, 4.2, fill=CODED_INK)
    svg.text(190, 509, "one outer fold", size=12)
    svg.line(300, 497, 300, 513, w=2.2)
    svg.text(308, 509, "mean of 4 folds", size=12)
    svg.circle(440, 505, 4.2, fill="none", stroke=CODED_INK)
    svg.text(450, 509, "not admissible: fails goal 1's crowded veto, or the budget refused every "
                       "candidate", size=12)
    return svg


def fig_margins(run: Run) -> Svg:
    """Figure 8: each net minus CoactDetect, per outer fold, both selections."""
    svg = Svg(900, 330, "Figure 8: the paired difference in held-out F1, each net minus CoactDetect, "
                        "per outer fold, for both selections")
    lo, hi = -0.30, 0.05
    x0, x1 = 290, 870
    X = lambda v: x0 + (v - lo) / (hi - lo) * (x1 - x0)   # noqa: E731
    top, row = 30, 30
    rows = [(m, w) for m in NETS for w in SEL]
    yb = top + len(rows) * row
    for v in (-0.3, -0.25, -0.2, -0.15, -0.1, -0.05, 0.0, 0.05):
        svg.line(X(v), top - 4, X(v), yb, stroke="#111" if v == 0 else "#eee",
                 dash="4 3" if v == 0 else None)
        svg.line(X(v), yb, X(v), yb + 4)
        svg.text(X(v), yb + 18, f"{v:+.2f}" if v else "0", anchor="middle", size=11)
    svg.text((x0 + x1) / 2, yb + 38, "net minus CoactDetect, held-out F1 (right of 0: the net is "
                                     "ahead)", anchor="middle", size=12)
    for i, (m, w) in enumerate(rows):
        y = top + i * row + row / 2
        c = run.cmp(m, "coact", w)
        svg.text(x0 - 10, y + 4, f"{m}, {SEL_NAME[w]}", anchor="end", size=12)
        for v in c["per_fold"]:
            assert v >= lo, f"{m} {w}: {v} is off the axis; widen lo"
            svg.circle(X(v), y, 4.2, fill=NET_INK)
        svg.line(X(c["mean"]), y - 10, X(c["mean"]), y + 10, stroke=NET_INK, w=2.2)
    return svg


# ---- tables --------------------------------------------------------------------------------------

CODED_WHAT = {
    "coact": "counts distinct ROIs firing together in a sliding window and asks how unlikely that "
             "count is against the same recording shifted in time",
    "loco": "counts ROIs active together and compares the count with a percentile of the counts "
            "around it",
    "rate": "compares the population's firing rate with its own slower average",
    "sce": "counts ROIs active in fixed time bins and thresholds against shuffled copies "
           "(synchronous calcium events, SCE)",
    "sync": "measures how closely ROIs' firing aligns, adapting its window to each ROI's rhythm",
    "cicada": "counts ROIs active within a few frames and thresholds against each ROI rolled in time",
}
NET_WHAT = {
    "tube": "averages the ROIs into one trace, then centre minus surround",
    "line_length": "lets each ROI vote once per moment, counts the share lit, then centre minus "
                   "surround",
    "chorus_norm": "filters each ROI separately, standardises it, votes, then pools three ways",
    "chorus_gain_norm": "as chorus_norm, with a learned gain and offset on each vote",
}


def contestants_table(run: Run) -> str:
    rows = []
    for m in NETS:
        axes = run.decl["learned_axes"][m]
        rows.append([f"<b>{esc(m)}</b>", "learned (net)", esc(NET_WHAT[m]),
                     f"{len(axes)} settings; 24 configurations drawn"])
    for d in CODED:
        axes = run.decl["hand_axes"][d]
        n_values = sum(len(v) for _, v in axes)
        rows.append([f"<b>{esc(NAME[d])}</b>", "coded", esc(CODED_WHAT[d]),
                     f"{len(axes)} settings, {n_values} grid values, searched one setting at a time"])
    return table(["contestant", "kind", "what it does", "what was tuned"], rows,
                 "Table 1: the ten contestants")


def headline_table(run: Run) -> str:
    rows = []
    for m in list(NETS) + list(CODED):
        cells = [f"<b>{esc(NAME[m])}</b>"]
        for w in SEL:
            vals = run.f1(m, w)
            cell = num(float(np.mean(vals)), 3)
            if m in CODED:
                bad = sum(1 for v, r in zip(run.veto(m, w), run.refused_all(m, w)) if not v or r)
                if bad:
                    cell += f" <span class=dim>({bad} of 4 folds not admissible)</span>"
            cells.append(cell)
            if m == "coact":
                cells.append("—")
            else:
                c = run.cmp(m, "coact", w)
                cells.append(f"{num(c['mean'], 3)} <span class=dim>(<i>t</i> = {num(c['t'], 1)})"
                             f"</span>")
        rows.append(cells)
    return table(["contestant", "mean F1, F1 alone", "minus CoactDetect",
                  "mean F1, under the budget", "minus CoactDetect"], rows,
                 "Table 2: held-out F1, means over four outer folds")


def coded_table(run: Run) -> str:
    rows = []
    ref = run.crowded["reference"]
    for d in CODED:
        for w in SEL:
            chosen = [row[w]["chosen_params"] for row in run.results["hand"][d]]
            gaps = sorted({str(c.get("merge_gap_sec", c.get("merge_gap_s", "—"))) for c in chosen})
            passes = sum(run.veto(d, w))
            crowd = [c["crowded_mean_f1"] for c in run.crowded["choices"]
                     if c["detector"] == d and c["selection"] == w]
            ob = sum(1 for v in run.over_budget(d, w) if v)
            refused = sum(run.refused_all(d, w))
            note = []
            if refused:
                note.append(f"budget refused every candidate in {refused} of 4 folds")
            if w == "gated" and ob:
                note.append(f"over the budget on the held-out fold in {ob} of 4 folds")
            rows.append([esc(NAME[d]), esc(SEL_NAME[w]), esc(", ".join(gaps)) + " s",
                         f"{num(min(crowd), 3)}–{num(max(crowd), 3)}",
                         num(ref[d]["crowded_mean_f1"], 3), f"{passes} of 4",
                         esc("; ".join(note)) or "—"])
    return table(["detector", "selection", "merge gap chosen", "crowded F1 of the choices",
                  "crowded F1 of the setting replaced", "folds passing the veto", "also"], rows,
                 "Table 3: the coded choices checked against goal 1's crowded veto")


# ---- the page ------------------------------------------------------------------------------------

def body(run: Run) -> str:
    d, r = run.decl, run.results
    n_fits = r["n_fits"]
    n_jobs = len(run.ran)
    wall = run.wall_hours()
    coact = {w: float(np.mean(run.coded_f1("coact", w))) for w in SEL}
    lead_u = max(NETS, key=lambda m: np.mean(run.net_f1(m, "ungated")))
    lead_g = max(NETS, key=lambda m: np.mean(run.net_f1(m, "gated")))
    cu, cg = run.cmp(lead_u, "coact", "ungated"), run.cmp(lead_g, "coact", "gated")
    sce = {w: float(np.mean(run.coded_f1("sce", w))) for w in SEL}
    sce_pass = {w: sum(run.veto("sce", w)) for w in SEL}
    tun = {m: run.tuning(m, "ungated")["mean"] for m in NETS}
    collapsed = run.collapsed()
    budget_margin = d["budget_margin"]
    spf, folds = d["seeds_per_fold"], d["folds"]
    n_rec = spf * folds * 2
    coact_over = sum(1 for v in run.over_budget("coact", "gated") if v)
    cicada_ref = sum(run.refused_all("cicada", "gated"))
    ref = d["reference"]["params"]
    base = d["coded_base"]["values"]
    facts = problem_recording()[3]
    first = {w: max(list(NETS) + list(CODED), key=lambda m: np.mean(run.f1(m, w))) for w in SEL}
    same_coact = run.coded_f1("coact", "ungated") == run.coded_f1("coact", "gated")

    parts = []
    parts.append(f"""
<h1>Do the learned detectors beat the hand-written ones once both are tuned fairly?</h1>
<p class=dim>Goal 2 of the current program, the fair comparison, run on the workstation WSMIP064
from 2026-09-18 at 16:14 to 2026-09-19 at 05:58. Simulated recordings only, the fast stream,
baseline conditions only (section 8). Written for a reader who has not followed this project.</p>
<p class=lede><b>The question.</b> This project detects <i>coordinated events</i> — moments when
several cells fire together — in calcium-imaging recordings. It has six hand-written ("coded")
detectors and a family of neural networks ("nets") trained to do the same job. An earlier
comparison had the nets ahead, but the nets had been run at one untuned setting and the coded
detectors tuned on a single knob each, so the margin could have been about who got tuned, not about
which approach is better. This run tunes both sides with the same care, chooses every setting
without looking at the recordings it is scored on, and asks again.</p>
<p class=lede><b>The answer, in words</b> (the numbers are in section 6): once both sides are
tuned, no net is ahead of CoactDetect, the coded detector the budget is anchored to. The one coded
detector that finishes ahead of CoactDetect does so with a setting that goal 1 of this program has
already ruled out, for a reason explained in section 7.</p>
<p>Abbreviations used throughout: <b>ROI</b>, region of interest (one imaged cell); <b>F1</b>, the
harmonic mean of recall (the share of planted events found) and precision (the share of calls that
were real), from 0 to 1; <b>CV</b>, cross-validation; <b>GPU</b>, graphics processor;
<b><i>t</i></b>, the paired <i>t</i> statistic across the four outer folds, on 3 degrees of freedom.</p>
""")

    parts.append(f"""
<h2 id="problem">1. The problem: finding coordinated events</h2>
<p>Each row of a raster is one ROI; each tick is a moment the cell fired. A coordinated event is
several ROIs firing within a fraction of a second of one another, more often than chance would put
them together. Two things make that hard. The cells fire at very different rates, so a busy cell
lands near others by accident all the time. And the whole field sometimes becomes busier for
minutes at a stretch, which raises chance coincidences everywhere without anything coordinated
happening. A detector has to find the few real events without firing on either.
<a href="#fig1">Figure 1, one simulated recording</a>, shows all three things a detector meets: a
planted event (marked in the lane above the raster), two <i>distractors</i> — bursts of correlated
firing that are not coordinated events and must not be called — and the <i>probe stretch</i>, five
minutes in which every ROI fires at {bench.BENCH_RECORDING['hot_rate_hz']:g} Hz, six times the
quiet background rate, with nothing planted in it.</p>
{figure(1, "One simulated bench recording and what is in it", fig_problem(),
        f"About ten minutes ({FIG1_WINDOW[0]:,.0f} s to {FIG1_WINDOW[1]:,.0f} s) of one recording "
        f"with the busy background, recording seed {FIG1_SEED}. <b>Raster</b> (bottom): "
        f"{bench.BENCH_RECORDING['n_roi']} ROIs, one tick per onset, busiest ROI on top. "
        f"<b>Lane</b> (top): a blue down-triangle marks the planted coordinated event at "
        f"{facts['event_t']:,.0f} s, which recruits {facts['event_frac']:.0%} of the ROIs with "
        f"{bench.BENCH_RECORDING['jitter_sec']:g} s of spread; orange down-triangles mark "
        f"{facts['n_distractors']} distractors; the hatched band marks the probe stretch, which "
        f"starts at {bench.BENCH_RECORDING['hot_window'][0]:,.0f} s and ramps up over its first "
        f"{bench.BENCH_RECORDING['ramp_sec']:g} s. Nothing is drawn on the raster itself. Finding "
        f"the event is the detector's problem: about "
        f"{round(facts['event_frac'] * bench.BENCH_RECORDING['n_roi'])} ticks aligned among "
        f"{facts['n_onsets']:,} onsets in the whole "
        f"{bench.BENCH_RECORDING['duration_sec'] / 60:.0f}-minute recording.")}
""")

    parts.append(f"""
<h2 id="bench">2. Why a simulation, and what it simulates</h2>
<p>A real recording has no answer key: nobody knows for certain which moments were coordinated, so
F1 cannot be computed on it. The project's <b>bench</b> is a simulator whose parameters are
measured from real baseline recordings, so its recordings look like real ones, but every planted
event is known. Each bench recording is {bench.BENCH_RECORDING['duration_sec'] / 60:.0f} minutes of
{bench.BENCH_RECORDING['n_roi']} ROIs holding 15 planted events, 5 at each of three participation
levels (30%, 18% and 10% of the ROIs), each event's onsets spread by
{bench.BENCH_RECORDING['jitter_sec']:g} s, with events at least
{bench.BENCH_RECORDING['min_sep_sec']:g} s apart. It also holds
{bench.BENCH_RECORDING['n_distractors']} distractors and the probe stretch.</p>
<p>Every recording seed is simulated at <b>two backgrounds</b>, the quiet and busy ends of the range
real baseline recordings span: {bench.REGIMES['baseline_quiet']['bg_rate_hz']:g} Hz and
{bench.REGIMES['baseline_busy']['bg_rate_hz']:g} Hz per ROI. A detector's score is its F1 pooled
within each background, then averaged over the two, so doing well at only one background is not
enough. A call counts as a hit if it lands within {2.5:g} s of a planted event; calls inside the
probe stretch are counted separately (as false alarms per hour) and kept out of precision, so the
probe measures "fires on busy but uncoordinated activity" without swamping every other number.</p>
<p>This run used {n_rec} recordings: {folds * spf} recording seeds
({d['recording_seeds'][0]}–{d['recording_seeds'][-1]}), each at both backgrounds, plus one
recording per seed with nothing planted at each background, used to count false alarms.</p>
""")

    parts.append(f"""
<h2 id="contestants">3. The contestants</h2>
<p>Ten detectors, four learned and six coded, listed in Table 1. The coded detectors are the
project's ports of established methods. The four nets are the ones that led the earlier untuned
comparison, plus <code>tube</code>, kept as a control: it tied CoactDetect untuned, so if tuning
lifted it far ahead too, the leaders' margins would be about tuning rather than design.
<a href="#fig2">Figure 2, the four nets side by side</a>, shows the difference that matters most:
where each one stops treating ROIs separately.</p>
{contestants_table(run)}
{figure(2, "What each of the four nets does", fig_nets(),
        "Each row reads left to right from the raster to a per-frame probability of an event. "
        "<code>tube</code> averages the ROIs first, so it cannot tell three cells firing once from "
        "one cell firing three times. The other three nets keep each ROI separate long enough for "
        "it to cast one bounded vote, then count or pool the votes. The final threshold on the "
        "probability is chosen on training recordings, like every other setting.")}
""")

    lr_steps = ", ".join(f"{a}: {', '.join(str(x) for x in v)}" for a, v in
                         d["learned_axes"]["chorus_norm"][:2])
    parts.append(f"""
<h2 id="fair">4. How the comparison was kept fair</h2>
<h3>4.1 Nested cross-validation: choose on some recordings, score on others</h3>
<p>If a setting is chosen by looking at the recordings it is then scored on, the score flatters
it. <b>Nested cross-validation</b> prevents that, and <a href="#fig3">Figure 3, the nested layout</a>,
shows it. The {folds * spf} recording seeds are split into {folds} <b>outer folds</b> of {spf}.
Each fold takes one turn being held out. With it set aside, every candidate setting is judged on
the other three folds alone, by rotating which of those three is scored while the other two train
(the <b>inner</b> loop). The winner is then retrained on all three training folds and scored once
on the held-out fold. The held-out fold is never seen while choosing.</p>
<p>Both sides went through exactly this. Each net had 24 configurations, drawn at random, before
the run started, from a grid over its learning rate, its number of training steps
({esc(lr_steps)}) and 3 or 4 settings of its own design, with the untuned setting always among
them. Each inner candidate was fitted at 3 training seeds, and each chosen configuration refitted at
5. Each coded detector's search walked every setting in goal 1's declared grids (Table 1), one
setting at a time, using the same inner loop.</p>
{figure(3, "The nested cross-validation layout", fig_nested(run),
        f"<b>A</b>: the four outer folds (folds 1 to 4; the run's files number them 0 to 3). "
        f"<b>B</b>: inside held-out fold 1, each candidate is fitted on two training folds and "
        f"scored on the third, three ways round, at 3 training seeds each. In all the run made "
        f"{n_fits:,} fits of nets across its {n_jobs:,} jobs.")}

<h3>4.2 A defect fixed before the run: two outer folds were training the same model</h3>
<p>A net does not train on every training recording: it fits a run of 10 consecutive recordings
from the list it is given, and the last two recordings on the list pick its threshold. Until
2026-09-18 that list was in fold order, so the run of 10 fell inside the first training fold, and
held-out folds that share their first training fold trained exactly the same model. Four outer
folds were then fewer than four independent fits, and a paired comparison over folds counts
independence it does not have. <a href="#fig4">Figure 4, the fitting draws before and after</a>,
shows it on this run's own split. The fix deals the recordings across the training folds in turn,
starting after the held-out one, so every fit reaches every training fold and the threshold
recordings rotate too. Before launching, the run replayed the exact draws for every training seed
and would have refused to start if any two outer folds shared a fitting set or threshold
recordings; its declaration records <code>fold_check.distinct = {str(d['fold_check']['distinct']).lower()}</code>.</p>
{figure(4, "Which recordings each outer refit fitted, at training seed 0", fig_defect(run),
        "Each strip is the 48 recording seeds, one cell per seed (each seed stands for its two "
        "backgrounds). <b>A</b>: the order used before the fix, applied to this run's split — "
        "held-out folds 2, 3 and 4 fit the same ten recordings, seeds 1000 to 1004, and fold 1's "
        "fitting set differs only because fold 1 is the one held out. <b>B</b>: what this run "
        "actually fitted, read from its fit records: four different sets, each reaching every "
        "training fold. Section 7 gives what the fix does not change.")}

<h3>4.3 The coded side runs in its better mode</h3>
<p>CoactDetect and LoCo each have two modes: <i>binned</i>, which counts coincidences in fixed time
bins, and <i>sliding</i>, which counts them in a window that moves smoothly. Goal 1 of this program
tuned both detectors in sliding mode, found better settings than the binned ones, and measured
sliding mode keeping its calls when a recording is shifted by a fraction of a second, where binned
mode can lose them. The project's shipped operating points are still binned — switching them
changes the browser viewer's defaults, and that switch has not been made — so a search that took
its unsearched settings from the shipped points would have tuned the coded side in the worse mode.
That would repeat the unfairness this comparison exists to remove. So this run lays goal 1's chosen
sliding values under every setting it scores for those two detectors, and uses them as the
reference below: CoactDetect at alpha {ref['alpha']:g}, a {ref['context_win_sec']:g} s context
window, a {ref['merge_gap_sec']:g} s merge gap and a {ref['guard_sec']:g} s guard; LoCo at the
{base['loco']['threshold_pctile']:g}th percentile with a {base['loco']['merge_gap_sec']:g} s merge
gap. The declaration records each coded detector's window mode.</p>

<h3>4.4 Two selections, and one false-alarm budget for everyone</h3>
<p>Choosing on F1 alone rewards a detector that calls more: extra calls can pick up extra planted
events faster than they cost precision. So every contestant was chosen twice from the same fits
(<a href="#fig5">Figure 5, the two selections</a>): once on F1 alone, and once on F1 among the
candidates within a <b>shared false-alarm budget</b>. The budget is anchored to the reference
CoactDetect: on each outer fold's training recordings, a candidate may fire at most
{budget_margin:g} times as often as the reference does, both in the probe stretch at each background
and on the quiet recordings with nothing planted. A net's threshold is chosen inside the budget
too. Neither selection is the headline over the other; they answer different questions.</p>
{figure(5, "Two selections from the same candidates", fig_budget(run),
        "A schematic, not data. Each grey point is a candidate: a configuration (and, for a net, "
        "a threshold) with its F1 and its firing rate on the training folds. The unshaded region "
        f"is within the budget, {budget_margin:g} times the reference CoactDetect's rate.")}

<h3>4.5 The size of the run</h3>
<p>{n_jobs:,} jobs: 1 reference measurement, {len(CODED) * folds} coded-detector searches
(6 detectors x 4 outer folds, on the processors), {sum(1 for x in run.ran if x['stage'].startswith('inner'))} inner fits and
{sum(1 for x in run.ran if x['stage'].startswith('outer'))} outer refits of nets (on one GPU). It
ran for {wall:.1f} hours of wall time with no errors, {r['cpu_hours_training']:.1f} hours of it
spent training nets.</p>
""")

    parts.append(f"""
<h2 id="replicate">5. A second, independent draw of recordings</h2>
<p>Four outer folds give only 3 degrees of freedom, and a margin of a hundredth of F1 can come and
go with which recordings happened to be drawn. So the workstation WSMIP065 ran the same comparison
on a disjoint set of recordings (<a href="#fig6">Figure 6, the two draws</a>): recording seeds
2000–2047 instead of 1000–1047, with everything else held fixed. A difference between the two
runs is then a difference between draws of data, and a margin that appears in both is not an
accident of one draw. The replicate finished at 07:48 on 2026-09-19 and is reported in its own
page by WSMIP065; this page does not quote its numbers.</p>
{figure(6, "The two draws of recordings", fig_draws(run),
        "Top: this run's 48 recording seeds, in its 4 outer folds of 12 (alternating shades). "
        "Bottom: the replicate's. The two share no recording.")}
""")

    lead_rows = "".join(
        f"<li><b>{esc(m)}</b>, tuned minus untuned: {num(tun[m], 3)} F1 on average "
        f"(<i>t</i> = {num(run.tuning(m, 'ungated')['t'], 1)}).</li>" for m in NETS)
    parts.append(f"""
<h2 id="results">6. What came out</h2>
<p><a href="#fig7">Figure 7, held-out F1 for all ten contestants</a>, shows every outer fold;
Table 2 gives the means and the paired comparisons with CoactDetect.</p>
{figure(7, "Held-out F1 per outer fold", fig_results(run),
        "One row per contestant; nets in blue above the dashed line, coded detectors in black "
        "below it. Each dot is one outer fold's held-out F1 (for a net, the mean over its 5 refit "
        "seeds); the bar is the mean of the 4 folds. A hollow dot is a coded choice that is not "
        "admissible: it fails goal 1's crowded veto (section 7), or the budget refused every "
        "candidate and the search returned its starting point.")}
{headline_table(run)}
<p>What the table says, in order of weight:</p>
<ul>
<li><b>No net is ahead of CoactDetect.</b> The best net on F1 alone, <code>{esc(lead_u)}</code>,
trails it by {num(-cu['mean'], 3)} F1 (<i>t</i> = {num(cu['t'], 1)}); under the budget,
<code>{esc(lead_g)}</code> trails by {num(-cg['mean'], 3)} (<i>t</i> = {num(cg['t'], 1)}).
CoactDetect's mean held-out F1 is {num(coact['ungated'], 3)} on F1 alone and
{num(coact['gated'], 3)} under the budget{' (its search chose the same settings both ways in every fold)' if same_coact else ''}.
Its choices pass goal 1's crowded veto in {sum(run.veto('coact', 'ungated')) + sum(run.veto('coact', 'gated'))} of 8 cases.
<a href="#fig8">Figure 8, each net minus CoactDetect</a>, shows the margins fold by fold.</li>
<li><b>Tuning barely moved the nets.</b>
<ul>{lead_rows}</ul>
The earlier comparison's lead for the nets came from comparing untuned nets against a coded side
tuned on one knob; with both sides tuned, it is gone.</li>
<li><b>Binned SCE finishes {'first' if first['ungated'] == 'sce' else 'high'} on paper, at
{num(sce['ungated'], 3)} on F1 alone and {num(sce['gated'], 3)} under the budget, and that result
does not stand.</b> Its search chose a 30 s merge gap in every fold, the top of its grid, and its choices
fail goal 1's crowded veto in {8 - sce_pass['ungated'] - sce_pass['gated']} of 8 cases (Table 3).
Section 7 explains why a long merge gap wins on this bench without being a better detector.</li>
<li><b>Under the budget, three coded detectors fall well behind</b>: SPIKE-synch, rate+context and
locust, whose gated results are either refused by the veto or not admissible at all (Table 3).</li>
</ul>
{figure(8, "Each net minus CoactDetect, per outer fold", fig_margins(run),
        "Each dot is one outer fold: the net's held-out F1 (mean over 5 refit seeds) minus "
        "CoactDetect's on the same fold. The bar is the mean. Left of the dashed zero line, "
        "CoactDetect is ahead; no dot is to the right of it. The two far-left dots, "
        "<code>chorus_gain_norm</code>'s fold 3 on F1 alone and <code>tube</code>'s fold 1 under "
        "the budget, are folds where one of the five refits scored below 0.2 F1 (section 7.3).")}
<p><b>How much the <i>t</i> values can carry.</b> They are plain paired <i>t</i> statistics over
four folds. The folds' training sets overlap (each training fold serves three held-out folds), which
makes the folds less independent than the statistic assumes, so these values overstate the
evidence; a correction for that (Nadeau and Bengio's) would shrink them, and none is applied here.
Read them as a ranking of consistency, not as tests. The replicate (section 5) is the real check.</p>
""")

    col_rows = "".join(
        f"<li><code>{esc(m)}</code>, {fold_label(h)}, refit seed {s}: F1 {num(f, 3)}, in the "
        f"{' and '.join('untuned setting' if w == 'untuned' else 'choice on ' + SEL_NAME[w] for w in ws)}"
        f"{' — the failed-training signature (the model predicts nearly everywhere)' if sig else ''}."
        f"</li>" for m, h, s, f, sig, ws in collapsed)
    parts.append(f"""
<h2 id="checks">7. Checks that qualify the result</h2>
<h3>7.1 The crowded-recording veto, applied after the fact</h3>
<p>On this bench, planted events are at least {bench.BENCH_RECORDING['min_sep_sec']:g} s apart.
A detector that <b>merges</b> calls closer together than some gap into one call therefore loses
nothing here by merging widely, and gains: merging removes near-duplicate calls, which raises
precision. On real recordings, coordinated events can come a few seconds apart, and a wide merge
fuses them. Goal 1 found exactly this (its first search ran merge gaps out to about a minute and
lost 0.25 to 0.32 F1 on crowded recordings), and added a veto: a setting may not score more than
{run.crowded['max_crowded_drop']:g} F1 below the setting it replaces on <b>crowded</b> recordings,
whose event spacing matches the crowded end of real recordings. This run's search did not apply
that veto, so it was applied afterwards to every coded choice, by
<code>tools/crowded_check_fair_comparison.py</code> on 12 crowded recordings at each background.
Table 3 gives the outcome. CoactDetect passes in every fold. Binned SCE's 30 s merge gap does
not, so its lead is the known artifact, not a better detector.</p>
{coded_table(run)}
<p class=warn>The nets were not checked on crowded recordings. Their merge gap is fixed rather than
tuned, so the artifact above cannot be chosen by their search, but whether they hold up on crowded
recordings is unmeasured.</p>

<h3>7.2 Choices that are not admissible, and choices that missed the budget on new data</h3>
<ul>
<li><b>locust under the budget:</b> in {cicada_ref} of 4 folds the budget refused every setting
its search tried, and the search returned its starting point, which is itself over the budget.
locust therefore has no admissible result under the budget in this run.</li>
<li><b>CoactDetect under the budget:</b> admissible on its training folds by construction, it
exceeded the budget on the held-out fold in {coact_over} of 4 folds. The budget is set from
training data and a new draw can land on either side of it.</li>
</ul>

<h3>7.3 Refits that failed to train</h3>
<p>Among the {run.n_outer_refits()} held-out refits of nets, {len(collapsed)} scored below 0.2
F1:</p>
<ul>{col_rows}</ul>
<p>Each one pulls its fold's mean down by about a fifth of its shortfall; they are included in
every mean above, not dropped.</p>
""")

    parts.append(f"""
<h2 id="limits">8. Limits</h2>
<ul class=resid>
<li><b>Baseline only, fast stream only</b> (Tony, 2026-09-17: <i>"for this training run use only
baseline"</i>). The bench is fitted to the baseline periods of the fast stream. Nothing here says
how any detector behaves in treatment periods or on the slow stream.</li>
<li><b>The bench's fitted constants carry a known, small contamination.</b> They were last measured
on the export folder <code>steps_excluded</code>, which still contains motion-correction
floor-pinning in a few ROIs — about 0.03% of events
(<code>HANDOFF-slow-comodulation-on-the-de-pinned-export.md</code>, decision 3). Re-measured on the
corrected folder on 2026-09-17 by both workstations, every constant moved by less than its own
bootstrap interval, and the two constants that describe coordination (onset spread and
participation) did not move. That makes the effect small; it does not make it absent, and moving
the bench to the corrected folder has not been decided.</li>
<li><b>Simulation only.</b> Every number is on simulated recordings. The bench is measured from real
ones, but a detector that wins here has not thereby been shown to win on real data.</li>
<li><b>Four outer folds</b>, so every paired comparison rests on 3 degrees of freedom, and the folds
share training data (section 6).</li>
<li><b>The coded searches move one setting at a time</b> and can end in a different place depending
on the path; under the budget a search can even score higher than without it, because the budget
changes which moves are available. The two selections are two searches, not one search filtered.</li>
<li><b>Chosen values at the edge of their grid</b> mean the search might have gone further. The
coded side's edges are recorded per fold in <code>results.json</code>; most coded detectors chose
the top of their merge-gap grid (Table 3).</li>
<li><b><code>min_rois</code>, the fewest ROIs a coded detector will call an event on, can learn the
bench's planted participation levels</b> (30%, 18% and 10% of 33 ROIs), so its tuned value is a
fact about this simulator.</li>
<li><b>One training run per seed, on one GPU.</b> GPU and processor arithmetic differ slightly; every
net in this run was trained on the same GPU.</li>
</ul>
""")

    parts.append(f"""
<h2 id="where">9. Where everything is</h2>
<ul>
<li><b>This report</b>: <code>&lt;darkroom&gt;/bugarach/{DARKROOM_FOLDER}/report/index.html</code>,
and in the repository beside the run's summaries.</li>
<li><b>The run's summaries, in the repository</b>:
<code>docs/learned/tuned_vs_coact/fair_comparison_2026_09_18/</code> — the declaration
(<code>meta.json</code>), <code>results.json</code>, the selections and configurations, the job
log, and this report's two derived files (<code>crowded_check.json</code>,
<code>fold_draws.json</code>). Personal paths in them are written as <code>%USERPROFILE%</code> and
<code>&lt;darkroom&gt;</code>.</li>
<li><b>Everything else, in the darkroom</b>: <code>&lt;darkroom&gt;/bugarach/{DARKROOM_FOLDER}/results/</code>
— the same summaries unedited, the chosen settings and fitted models (<code>chosen/</code>), every
fitted model (<code>fits.tar.gz</code>) and every score table (<code>scores.tar.gz</code>, 1.1 GB
unpacked), and the run's log. The workstation keeps its own copy in
<code>%USERPROFILE%\\runs\\fair-comparison-2026-09-18\\</code>.</li>
<li><b>The code that ran</b>: <code>tools/tune_learned_vs_coact.py</code> on branch
<code>tune-bench-comparison</code> at <code>{esc(run.meta['started']['git']['commit'][:7])}</code>
(the declaration records it, and that the tree was clean).</li>
</ul>
""")
    ver = provenance.code_version() or "unknown"
    parts.append(f'<h2 id="provenance">Provenance</h2><p class=dim>Built '
                 f"{time.strftime('%Y-%m-%d %H:%M %z')} by "
                 f"<code>tools/build_fair_comparison_report.py</code> at <code>{esc(ver)}</code> "
                 f"from <code>{esc(run.folder.relative_to(REPO).as_posix() if run.folder.is_relative_to(REPO) else run.folder.name)}</code>. "
                 f"Reviewed by the eleven roles of <code>docs/doc_review_process.md</code>.</p>")
    return "\n".join(parts)


# Long repository paths are single words to a browser and pushed a phone-width page sideways.
EXTRA_CSS = "<style>code{overflow-wrap:anywhere}</style>"


def build(run_dir: Path) -> str:
    run = Run(run_dir)
    return page("Tuned nets against tuned coded detectors", EXTRA_CSS + body(run))


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--run", type=Path, default=DEFAULT_RUN)
    ap.add_argument("--out", type=Path, default=None,
                    help="destination folder (default: the darkroom's "
                         f"{DARKROOM_FOLDER}/report/)")
    ap.add_argument("--also", type=Path, default=None,
                    help="write a second copy here, e.g. the run's folder in the repository")
    a = ap.parse_args(argv)
    html_text = build(a.run)
    out = a.out
    if out is None:
        from bugarach import paths
        root = paths.darkroom(create=True)
        if root is None:
            print(paths.unresolved_message(), file=sys.stderr)
            return 2
        out = root / DARKROOM_FOLDER / "report"
    for folder in [out] + ([a.also] if a.also else []):
        folder = Path(folder)
        folder.mkdir(parents=True, exist_ok=True)
        name = "index.html" if folder == Path(out) else "report.html"
        (folder / name).write_text(html_text, encoding="utf-8")
        print(folder / name)
    return 0


if __name__ == "__main__":
    sys.exit(main())
