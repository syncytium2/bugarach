#!/usr/bin/env python3
"""Write the fair comparison's report: tuned nets against tuned coded detectors, for a reader new to it.

    python tools/build_fair_comparison_report.py                     # darkroom only
    python tools/build_fair_comparison_report.py --also docs/learned/tuned_vs_coact/fair_comparison_2026_09_18

Tony, 2026-09-19: *"I'd like a full report from each machine written so someone new can understand.
Include figures to explain conceptually what was done and why."* So the page explains the problem,
the simulation, the contestants and how the comparison was kept fair **before** it shows a result,
and every number and every data figure is computed here from the run's committed files or from the
bench itself. Prose stating a fact about these data comes from code too: a sentence such as "no fold
is ahead" is a comparison in code, never a typed claim (the first draft typed one, and it was false).

Reads the run's committed summary (``--run``, default
``docs/learned/tuned_vs_coact/fair_comparison_2026_09_18/``): ``results.json`` and ``meta.json``
as the run wrote them; ``crowded_check.json`` (``tools/crowded_check_fair_comparison.py``);
``fold_draws.json`` and ``merge_gap.json`` (``tools/fair_comparison_evidence.py``); and
``replicate_summary.json``, the replicate's numbers copied from WSMIP065's results (its source is
recorded inside). Writes ``index.html`` to ``darkroom()/2026-09-18-fair-comparison-run/report/`` by
default (sapper SAP006) and ``report.html`` to ``--also``.

The page kit (``Svg``, ``figure``, ``page``, ``table``, ``provenance_block``) is
``tools/build_surrogate_report.py``'s, imported rather than copied: inline SVG only, numbered
figures, a light page. The four nets' architecture drawings are draughtsman's and are not drawn here
(Tony, 2026-09-19: hand-drawn copies in two reports "will likely be completely incomparable").
"""

from __future__ import annotations

import argparse
import json
import math
import sys
import time
from functools import lru_cache
from pathlib import Path

import numpy as np

REPO = Path(__file__).resolve().parent.parent
sys.path[:0] = [str(REPO / "src"), str(REPO / "tools")]

from build_surrogate_report import Svg, esc, figure, num, page, table  # noqa: E402

from bugarach import bench, provenance, score  # noqa: E402

DEFAULT_RUN = REPO / "docs" / "learned" / "tuned_vs_coact" / "fair_comparison_2026_09_18"
DARKROOM_FOLDER = "2026-09-18-fair-comparison-run"

NETS = ("chorus_norm", "chorus_gain_norm", "line_length", "tube")
CODED = ("coact", "sce", "loco", "cicada", "sync", "rate")
# The display names are the viewer's (bugarach.ui.app.TITLES), with locust named: the public
# site withholds it as "sixth", and this page is not the site (the README names it too).
NAME = {"coact": "CoactDetect", "loco": "LoCo", "rate": "rate+context", "sce": "binned SCE",
        "sync": "SPIKE-synch", "cicada": "locust", "chorus_norm": "chorus_norm",
        "chorus_gain_norm": "chorus_gain_norm", "line_length": "line_length", "tube": "tube"}
SEL = ("ungated", "gated")
SEL_NAME = {"ungated": "F1 alone", "gated": "F1 under the budget"}
NET_INK, CODED_INK, GREY = "#1b5fa8", "#111", "#8a8a8a"
PLANT_INK, REPL_INK = "#1b5fa8", "#c2410c"
REPLICATE_PAGE = "<darkroom>/bugarach/2026-09-18-replicate-run-status/ (WSMIP065's report)"
ARCH_PAGE = "<darkroom>/bugarach/2026-09-19-comparison-architectures/index.html"
ARCH_REPO = "docs/learned/comparison/comparison.svg (pull request #660, not yet on main)"
N_B_FACTOR_NOTE = "Nadeau and Bengio 2003"


def _nb_factor(j: int, test_over_train: float) -> float:
    """Nadeau and Bengio's corrected resampled t: the variance's 1/J becomes 1/J + n2/n1."""
    return math.sqrt((1.0 / j) / (1.0 / j + test_over_train))


# ---- the run's numbers ---------------------------------------------------------------------------

class Run:
    """Everything the page quotes, read once from the committed files."""

    def __init__(self, folder: Path):
        self.folder = folder
        rd = lambda n: json.loads((folder / n).read_text())   # noqa: E731
        self.results, self.meta = rd("results.json"), rd("meta.json")
        self.decl = self.meta["declaration"]
        self.crowded, self.draws = rd("crowded_check.json"), rd("fold_draws.json")
        self.gap, self.repl, self.ran = rd("merge_gap.json"), rd("replicate_summary.json"), rd("ran.json")
        self.folds = list(range(self.decl["folds"]))
        self.nb = _nb_factor(self.decl["folds"], 1.0 / (self.decl["folds"] - 1))
        bench_decl = self.decl["bench_recording"]
        for k in ("duration_sec", "n_roi", "jitter_sec", "min_sep_sec", "hot_rate_hz"):
            assert bench_decl[k] == bench.BENCH_RECORDING[k], \
                f"the live bench's {k} differs from what the run declared; rebuild from the run"

    def net_f1(self, m, w):
        return [row[w]["f1_mean"] for row in self.results["learned"][m]]

    def coded_f1(self, d, w):
        return [row[w]["f1"] for row in self.results["hand"][d]]

    def f1(self, name, w):
        return self.net_f1(name, w) if name in NETS else self.coded_f1(name, w)

    def refused_all(self, d, w):
        out = []
        for h in self.folds:
            sel = json.loads((self.folder / "selections" / w / f"outer{h}" / f"{d}.json").read_text())
            out.append(bool(sel["n_refused"]) and sel["n_refused"] >= sel["n_scored"])
        return out

    def veto(self, d, w):
        got = {(c["outer_fold"], c["selection"]): c for c in self.crowded["choices"]
               if c["detector"] == d}
        return [got[(h, w)]["passes_veto"] for h in self.folds]

    def admissible(self, d, w):
        return [v and not r for v, r in zip(self.veto(d, w), self.refused_all(d, w))]

    def cmp(self, a, b, w):
        """The run's own paired comparison where it computed one; otherwise the same arithmetic as
        its ``_paired`` (tools/tune_learned_vs_coact.py on branch tune-bench-comparison)."""
        got = self.results["comparisons"][w].get(f"{a} - {b}")
        if got is not None:
            return got
        d = [x - y for x, y in zip(self.f1(a, w), self.f1(b, w))]
        sd = float(np.std(d, ddof=1))
        return dict(per_fold=d, mean=float(np.mean(d)), sd=sd,
                    t=float(np.mean(d) / (sd / math.sqrt(len(d)))) if sd > 0 else None, df=len(d) - 1)

    def tuning(self, m, w):
        return self.results["comparisons"][w][f"{m} tuned - untuned"]

    def over_budget_nets(self, m):
        return [row["gated"]["seeds_over_budget"] for row in self.results["learned"][m]]

    def low_refits(self):
        """Every distinct held-out refit under 0.2 F1: (model, fold, seed, F1, made no calls,
        failed-training signature, [selections])."""
        seen: dict = {}
        for m in NETS:
            for row in self.results["learned"][m]:
                for w in ("untuned",) + SEL:
                    for s in row[w]["per_seed"]:
                        if s["f1"] < 0.2:
                            k = (m, row["outer_fold"], row[w]["config_key"], s["seed"])
                            seen.setdefault(k, [m, row["outer_fold"], s["seed"], s["f1"],
                                                bool(s.get("f1_was_nan")),
                                                bool(s.get("failed_training_signature")), []])[6].append(w)
        return [tuple(v) for v in seen.values()]

    def lowest_other_refit(self):
        vals = [s["f1"] for m in NETS for row in self.results["learned"][m]
                for w in ("untuned",) + SEL for s in row[w]["per_seed"] if s["f1"] >= 0.2]
        return min(vals)

    def n_stage(self, prefix):
        return sum(1 for x in self.ran if x["stage"].startswith(prefix))

    def coded_gap_curve(self, d, w="ungated"):
        rows = [r for r in self.gap["coded"][d] if r["selection"] == w]
        gaps = sorted({float(g) for r in rows for g in r["f1_by_gap"]})
        return gaps, {g: [r["f1_by_gap"][f"{g:g}"] for r in rows] for g in gaps}, \
            [float(r["chosen_gap"]) for r in rows]

    def net_gap_curve(self, m, w="ungated"):
        rows = [r for r in self.gap["nets"][m] if r["selection"] == w]
        gaps = [float(g) for g in self.gap["net_gaps_sec"]]
        return gaps, {g: [r["f1_mean_by_gap"][f"{g:g}"] for r in rows] for g in gaps}

    def gap_repro(self):
        coded = max(r["reproduces_run"] for d in self.gap["coded"] for r in self.gap["coded"][d])
        nets = max(e["reproduces_run"] for m in self.gap["nets"] for r in self.gap["nets"][m]
                   for e in r["per_seed"])
        return coded, nets

    def wall_hours(self):
        a = time.mktime(time.strptime(self.meta["started"]["at"][:19], "%Y-%m-%dT%H:%M:%S"))
        progress = json.loads((self.folder / "progress.json").read_text())
        b = time.mktime(time.strptime(progress["at"][:19], "%Y-%m-%dT%H:%M:%S"))
        return (b - a) / 3600.0


def fold_label(h: int) -> str:
    return f"fold {h + 1}"


def mmss(t: float) -> str:
    """Minutes-friendly time, as the viewer's axis labels it: 16m33s."""
    m, s = divmod(int(round(t)), 60)
    return f"{m}m{s:02d}s" if s else f"{m}m"


@lru_cache(maxsize=1)
def crowded_spacing():
    """Planted-event spacing on the crowded recordings the veto scores (seeds 1-12, both
    backgrounds), measured rather than quoted."""
    from search_all_settings import N_TAIL
    gaps, n = [], set()
    for s in range(1, N_TAIL + 1):
        for r in ("baseline_quiet", "baseline_busy"):
            _, gt = bench.make_tail_recording(r, s)
            t = np.sort(gt.times)
            n.add(len(t))
            gaps += list(np.diff(t))
    g = np.array(gaps)
    return dict(n_events=sorted(n), min=float(g.min()), p10=float(np.percentile(g, 10)),
                median=float(np.median(g)), n_recordings=2 * N_TAIL)


# ---- figures -------------------------------------------------------------------------------------

FIG1_SEED, FIG1_WINDOW = 1000, (940.0, 1560.0)


def problem_recording():
    sl, gt = bench.make_recording("baseline_busy", FIG1_SEED)
    trains = bench.stream_trains(sl.streams[bench.STREAM], bench.recording_extent(sl))
    t0, t1 = FIG1_WINDOW
    inside = [(t, f) for t, f in zip(gt.times, gt.frac) if t0 <= t <= t1]
    facts = dict(event_t=inside[0][0], event_frac=inside[0][1],
                 n_part=int(round(inside[0][1] * bench.BENCH_RECORDING["n_roi"])),
                 distractors=[t for t in gt.distractor_times if t0 <= t <= t1],
                 n_onsets=int(sum(len(t) for t in trains)))
    return sl, gt, trains, facts


def fig_problem() -> Svg:
    """Figure 1. The raster rules are bugarach.ui.diagnostic's: rows ranked by activity INSIDE the
    drawn window (stable), ticks under half the row pitch, nothing drawn on the raster, cues in a lane
    above with down-pointing markers, planted filled and distractors hollow."""
    _, gt, trains, facts = problem_recording()
    t0, t1 = FIG1_WINDOW
    counts = [int(np.sum((t >= t0) & (t <= t1))) for t in trains]
    order = np.argsort([-c for c in counts], kind="stable")
    svg = Svg(900, 500, "Figure 1: a raster of 33 ROIs over ten minutes of one simulated recording, "
                        "with a lane above marking the planted event, two distractors and the probe")
    x0, x1 = 170, 870
    X = lambda t: x0 + (t - t0) / (t1 - t0) * (x1 - x0)    # noqa: E731
    lane_top, ras_top, row_h = 36, 118, 10.0
    svg.text(x0 - 12, lane_top + 14, "planted event", anchor="end", size=12)
    svg.text(x0 - 12, lane_top + 36, "distractor", anchor="end", size=12)
    svg.text(x0 - 12, lane_top + 58, "probe", anchor="end", size=12)
    svg.tri(X(facts["event_t"]), lane_top + 4, 6, fill=PLANT_INK)
    for t in facts["distractors"]:
        s = 6
        svg.add(f'<path d="M{X(t) - s:.1f} {lane_top + 26:.1f} L{X(t) + s:.1f} {lane_top + 26:.1f} '
                f'L{X(t):.1f} {lane_top + 26 + s * 1.6:.1f} Z" fill="none" stroke="{GREY}" '
                f'stroke-width="1.5"/>')
    hot = bench.BENCH_RECORDING["hot_window"]
    ha, hb = X(max(hot[0], t0)), X(min(hot[1], t1))
    for k in range(int((hb - ha) / 7)):
        svg.line(ha + 7 * k, lane_top + 62, ha + 7 * k + 5, lane_top + 50, stroke="#666")
    for row, i in enumerate(order):
        y = ras_top + row * row_h
        for t in trains[i]:
            if t0 <= t <= t1:
                svg.line(X(t), y + 3, X(t), y + 7, w=1.3)
    ras_bot = ras_top + len(order) * row_h
    svg.text(x0 - 12, (ras_top + ras_bot) / 2, f"{len(order)} ROIs,", anchor="end", size=12)
    svg.text(x0 - 12, (ras_top + ras_bot) / 2 + 15, "most active", anchor="end", size=12)
    svg.text(x0 - 12, (ras_top + ras_bot) / 2 + 30, "in this window", anchor="end", size=12)
    svg.text(x0 - 12, (ras_top + ras_bot) / 2 + 45, "on top", anchor="end", size=12)
    svg.time_axis(x0, x1, ras_bot + 8, t0, t1, "time in the recording")
    return svg


def fig_nested(run: Run) -> Svg:
    n, spf = run.decl["folds"], run.decl["seeds_per_fold"]
    svg = Svg(900, 300, "Figure 2: four outer folds of twelve recording seeds; for each held-out "
                        "fold the other three are used to choose; for a net, three inner fits "
                        "rotate which training fold scores")
    x0, cw, ch = 190, 96, 34
    svg.text(20, 26, "A  Outer loop: which fold is scored", size=13, weight="bold")
    for h in range(n):
        y = 44 + h * (ch + 8)
        svg.text(x0 - 12, y + 22, f"held-out {fold_label(h)}", anchor="end", size=12)
        for f in range(n):
            held = f == h
            svg.rect(x0 + f * (cw + 4), y, cw, ch, fill="#333" if held else "#dfe7f2", stroke="#333")
            svg.text(x0 + f * (cw + 4) + cw / 2, y + 22, "scored once" if held else "chooses",
                     anchor="middle", size=12, fill="#fff" if held else "#111")
    for f in range(n):
        svg.text(x0 + f * (cw + 4) + cw / 2, 40 + n * (ch + 8) + 14,
                 f"{fold_label(f)}: {spf} seeds", anchor="middle", size=11, fill="#333")
    bx = 620
    svg.text(bx - 10, 26, "B  A net, inside held-out fold 1", size=13, weight="bold")
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
    return svg


def fig_defect(run: Run) -> Svg:
    d = run.draws
    seeds = sorted(int(s) for s in d["fold_of"])
    fold_of = {int(k): v for k, v in d["fold_of"].items()}
    spf = run.decl["seeds_per_fold"]
    svg = Svg(900, 450, "Figure 3: for each held-out fold, the ten training recordings fitted at "
                        "training seed 0, before the fix and as this run drew them")
    x0, x1 = 200, 880
    cell = (x1 - x0) / len(seeds)

    def strip(y, h, info, label):
        svg.text(x0 - 12, y + 12, label, anchor="end", size=12)
        fitted = {int(r.split(":")[1]) for r in info["fitted"]}
        thr = {int(r.split(":")[1]) for r in info["threshold"]}
        for k, s in enumerate(seeds):
            fill = ("#333" if fold_of[s] == h else NET_INK if s in fitted
                    else REPL_INK if s in thr else "#e6e6e6")
            svg.rect(x0 + k * cell, y, cell - 1, 16, fill=fill)

    for panel, (key, title) in enumerate((("before_fix", "A  Before the fix: consecutive order"),
                                          ("as_run", "B  As this run drew them: dealt across folds"))):
        top = 30 + panel * 190
        svg.text(20, top, title, size=13, weight="bold")
        for h in run.folds:
            strip(top + 14 + h * 26, h, d[key][str(h)], f"held-out {fold_label(h)}")
        for f in run.folds:
            xa = x0 + f * spf * cell
            svg.text(xa + spf * cell / 2, top + 14 + 4 * 26 + 12,
                     f"{fold_label(f)}: seeds {seeds[spf * f]}–{seeds[spf * f + spf - 1]}",
                     anchor="middle", size=11, fill="#333")
        distinct = len({tuple(v["fitted"]) for v in d[key].values()})
        svg.text(x0, top + 14 + 4 * 26 + 32, f"{distinct} distinct fitting sets for 4 held-out folds",
                 size=12, weight="bold", fill="#b00" if distinct < 4 else "#060")
    lx = 20
    for ink, lab in ((NET_INK, "fitted"), (REPL_INK, "picks the threshold"), ("#333", "held out"),
                     ("#e6e6e6", "not used at this seed")):
        svg.rect(lx, 426, 12, 12, fill=ink, stroke="#999")
        svg.text(lx + 18, 436, lab, size=12)
        lx += 180
    return svg


def fig_budget(run: Run) -> Svg:
    svg = Svg(900, 330, "Figure 4: a schematic of the two selections: the best F1 anywhere, and the "
                        "best F1 among candidates firing no more than 1.6 times the reference")
    x0, x1, y0, y1 = 110, 870, 30, 270
    svg.line(x0, y1, x1, y1)
    svg.line(x0, y0, x0, y1)
    svg.text((x0 + x1) / 2, y1 + 30, "false alarms per hour on the training recordings",
             anchor="middle", size=12)
    svg.add(f'<text x="34" y="{(y0 + y1) / 2}" font-size="12" transform="rotate(-90 34 '
            f'{(y0 + y1) / 2})" text-anchor="middle">F1 on the training recordings</text>')
    rs = np.random.RandomState(7)
    fa = rs.uniform(0.05, 0.95, 26)
    f1 = 0.45 + 0.35 * np.sqrt(fa) + rs.normal(0, 0.035, 26)
    ref_fa, ref_f1 = 0.22, 0.60
    budget = ref_fa * run.decl["budget_margin"]
    X = lambda v: x0 + v * (x1 - x0)                      # noqa: E731
    Y = lambda v: y1 - (v - 0.4) / 0.5 * (y1 - y0)        # noqa: E731
    svg.rect(X(budget), y0, x1 - X(budget), y1 - y0, fill="#f4f4f4")
    svg.line(X(budget), y0, X(budget), y1, stroke="#555", dash="5 4")
    svg.text(X(budget) + 10, y1 - 26, "outside the budget:", size=12, fill="#555")
    svg.text(X(budget) + 10, y1 - 10, f"more than {run.decl['budget_margin']:g} x the reference's "
                                      "rate", size=12, fill="#555")
    far = [i for i in range(len(fa)) if abs(fa[i] - ref_fa) > 0.05 or abs(f1[i] - ref_f1) > 0.05]
    for i in far:
        svg.circle(X(fa[i]), Y(f1[i]), 4, fill="#777")
    ung = max(far, key=lambda i: f1[i])
    gat = max([i for i in far if fa[i] <= budget - 0.02], key=lambda i: f1[i])
    svg.circle(X(fa[ung]), Y(f1[ung]), 7, fill="none", stroke="#111")
    svg.text(X(fa[ung]) - 12, Y(f1[ung]) + 4, "chosen on F1 alone", anchor="end", size=12)
    svg.circle(X(fa[gat]), Y(f1[gat]), 7, fill="none", stroke=NET_INK)
    svg.text(X(fa[gat]) - 12, Y(f1[gat]) - 10, "chosen under the budget", anchor="end", size=12,
             fill=NET_INK)
    svg.add(f'<path d="M{X(ref_fa) - 6:.1f} {Y(ref_f1) - 6:.1f} h12 v12 h-12 Z" fill="{CODED_INK}"/>')
    svg.text(X(ref_fa) - 10, Y(ref_f1) + 22, "reference CoactDetect", anchor="middle", size=12)
    return svg


def fig_merge(run: Run) -> Svg:
    """Figure 5. A: why merging pays on the bench and costs on crowded recordings. B: held-out F1
    against the merge gap for both sides, from merge_gap.json (only the merge gap changed)."""
    svg = Svg(900, 560, "Figure 5: panel A, how merging calls behaves when events are far apart and "
                        "when they are close; panel B, held-out F1 against the merge gap for the "
                        "coded detectors and the nets")
    # --- A: schematic ---
    svg.text(20, 22, "A  Merging calls: harmless when events are far apart, fatal when close",
             size=13, weight="bold")
    for r, (label, events, calls) in enumerate((
            ("far apart (this bench:", [60, 330], [52, 58, 61, 66, 322, 331, 336]),
            ("close (crowded:", [60, 100, 140], [55, 62, 96, 103, 136, 144]))):
        y = 48 + r * 64
        svg.text(250, y + 10, label, anchor="end", size=12)
        svg.text(250, y + 25, ["at least 120 s)", "a few seconds)"][r], anchor="end", size=12)
        base = 280
        svg.text(base - 8, y + 4, "", size=11)
        for t in events:
            svg.tri(base + t, y - 4, 5, fill=PLANT_INK)
        for t in calls:
            svg.line(base + t, y + 12, base + t, y + 22, w=1.6)
        a, b = min(calls), max(calls) if r else 66
        if r == 0:
            svg.rect(base + 50, y + 26, 18, 6, fill="#999")
            svg.rect(base + 320, y + 26, 18, 6, fill="#999")
            svg.text(base + 360, y + 32, "two merged calls, two events: precision up, recall kept",
                     size=11, fill="#333")
        else:
            svg.rect(base + 53, y + 26, 93, 6, fill="#999")
            svg.text(base + 160, y + 32, "one merged call, three events: two events lost",
                     size=11, fill="#333")
    svg.tri(40, 172, 5, fill=PLANT_INK)
    svg.text(52, 181, "planted event", size=11)
    svg.line(160, 170, 160, 180, w=1.6)
    svg.text(168, 181, "raw call", size=11)
    svg.rect(240, 173, 18, 6, fill="#999")
    svg.text(264, 181, "call after merging", size=11)
    # --- B: data ---
    top, bot, x0, x1 = 230, 500, 120, 700
    svg.text(20, top - 16, "B  Held-out F1 with only the merge gap changed (mean of 4 outer folds, "
                           "choices on F1 alone)", size=13, weight="bold")
    gaps = [0.0, 2.0, 4.0, 8.0, 16.0, 30.0]
    X = lambda g: x0 + gaps.index(g) / (len(gaps) - 1) * (x1 - x0)   # noqa: E731
    lo, hi = 0.45, 0.85
    Y = lambda v: bot - (v - lo) / (hi - lo) * (bot - top)            # noqa: E731
    svg.line(x0, bot, x1, bot)
    svg.line(x0, top, x0, bot)
    for g in gaps:
        svg.line(X(g), bot, X(g), bot + 4)
        svg.text(X(g), bot + 18, f"{g:g} s", anchor="middle", size=11)
    svg.text((x0 + x1) / 2, bot + 38, "merge gap: calls closer than this are merged into one",
             anchor="middle", size=12)
    for v in (0.5, 0.6, 0.7, 0.8):
        svg.line(x0 - 4, Y(v), x0, Y(v))
        svg.line(x0, Y(v), x1, Y(v), stroke="#eee")
        svg.text(x0 - 8, Y(v) + 4, f"{v:.1f}", anchor="end", size=11)
    svg.add(f'<text x="70" y="{(top + bot) / 2}" font-size="12" transform="rotate(-90 70 '
            f'{(top + bot) / 2})" text-anchor="middle">held-out F1</text>')
    styles = {"coact": (CODED_INK, None, 2.2), "sce": (GREY, "6 4", 1.8), "loco": (GREY, "2 3", 1.8)}
    labels = []
    for d, (ink, dash, w) in styles.items():
        gs, vals, chosen = run.coded_gap_curve(d)
        pts = [(X(g), Y(float(np.mean(vals[g])))) for g in gs if g in gaps]
        for (xa, ya), (xb, yb) in zip(pts, pts[1:]):
            svg.line(xa, ya, xb, yb, stroke=ink, w=w, dash=dash)
        for g in sorted(set(chosen)):
            if g in gaps:
                svg.circle(X(g), Y(float(np.mean(vals[g]))), 6, fill="none", stroke=ink)
        labels.append((pts[-1][1], NAME[d], ink))
    for m in NETS:
        gs, vals = run.net_gap_curve(m)
        pts = [(X(g), Y(float(np.mean(vals[g])))) for g in gs if g in gaps]
        for (xa, ya), (xb, yb) in zip(pts, pts[1:]):
            svg.line(xa, ya, xb, yb, stroke=NET_INK, w=2.0 if m == "chorus_norm" else 1.0)
        for x, y in pts:
            svg.circle(x, y, 2.6, fill=NET_INK)
        svg.circle(pts[0][0], pts[0][1], 6, fill="none", stroke=NET_INK)
        labels.append((pts[-1][1], m, NET_INK))
    labels.sort()
    last = -99
    for y, lab, ink in labels:
        y = max(y, last + 14)
        svg.text(x1 + 10, y + 4, lab, size=11, fill=ink)
        last = y
    svg.circle(x1 + 30, bot + 40, 6, fill="none", stroke="#111")
    svg.text(x1 + 42, bot + 44, "the gap the run used", size=11)
    return svg


def fig_draws(run: Run) -> Svg:
    seeds = run.decl["recording_seeds"]
    spf = run.decl["seeds_per_fold"]
    svg = Svg(900, 150, "Figure 6: two strips of 48 recording seeds, 1000 to 1047 on WSMIP064 and "
                        "2000 to 2047 on WSMIP065")
    x0, x1 = 230, 880
    cell = (x1 - x0) / len(seeds)
    for r, (label, first) in enumerate((("A  this run (WSMIP064)", seeds[0]),
                                        ("B  replicate (WSMIP065)", seeds[0] + 1000))):
        y = 26 + r * 62
        svg.text(x0 - 12, y + 16, label, anchor="end", size=12, weight="bold")
        for k in range(len(seeds)):
            shade = "#555" if (k // spf) % 2 == 0 else "#bbb"
            svg.rect(x0 + k * cell, y, cell - 1, 22, fill="none", stroke=shade)
        for f in run.folds:
            svg.text(x0 + (f + 0.5) * spf * cell, y + 38,
                     f"{fold_label(f)}: {first + spf * f}–{first + spf * f + spf - 1}",
                     anchor="middle", size=11, fill="#333")
    return svg


def fig_results(run: Run) -> Svg:
    names = list(NETS) + list(CODED)
    svg = Svg(900, 540, "Figure 7: held-out F1 per outer fold, one row per contestant, panel A for "
                        "choices on F1 alone and panel B under the budget")
    lo, hi = 0.2, 0.85
    panels = ((170, 510, "ungated", "A"), (560, 890, "gated", "B"))
    top, row = 58, 38
    for x0, x1, w, letter in panels:
        X = lambda v, a=x0, b=x1: a + (v - lo) / (hi - lo) * (b - a)   # noqa: E731
        svg.text((x0 + x1) / 2, 22, f"{letter}  {SEL_NAME[w]}", anchor="middle", size=13,
                 weight="bold")
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
            if m in CODED:
                veto, refused = run.veto(m, w), run.refused_all(m, w)
            else:
                veto, refused = [True] * 4, [False] * 4
            for k, v in enumerate(vals):
                yk = y + (k - 1.5) * 4.5          # each fold on its own line: no two can fuse
                if refused[k]:
                    s = 4
                    svg.line(X(v) - s, yk - s, X(v) + s, yk + s, stroke=ink, w=1.6)
                    svg.line(X(v) - s, yk + s, X(v) + s, yk - s, stroke=ink, w=1.6)
                else:
                    svg.circle(X(v), yk, 3.6, fill=ink if veto[k] else "#fff", stroke=ink)
            mean = float(np.mean(vals))
            svg.line(X(mean), y - 12, X(mean), y + 12, stroke=ink, w=2.2)
    for i, m in enumerate(names):
        y = top + i * row + row / 2
        svg.text(160, y + 4, NAME[m], anchor="end", size=12,
                 fill=NET_INK if m in NETS else CODED_INK, weight="bold" if m == "coact" else "normal")
    svg.line(20, top + len(NETS) * row, 890, top + len(NETS) * row, stroke="#bbb", dash="3 3")
    svg.text(20, top + len(NETS) * row - 6, "nets", size=11, fill=NET_INK)
    svg.text(20, top + len(NETS) * row + 14, "coded", size=11)
    ly = 522
    svg.circle(40, ly, 3.6, fill=CODED_INK)
    svg.text(50, ly + 4, "one outer fold", size=12)
    svg.line(160, ly - 8, 160, ly + 8, w=2.2)
    svg.text(168, ly + 4, "mean of 4 folds", size=12)
    svg.circle(290, ly, 3.6, fill="#fff", stroke=CODED_INK)
    svg.text(300, ly + 4, "fails the crowded-recording check (section 4.5)", size=12)
    svg.line(596, ly - 4, 604, ly + 4, stroke=CODED_INK, w=1.6)
    svg.line(596, ly + 4, 604, ly - 4, stroke=CODED_INK, w=1.6)
    svg.text(610, ly + 4, "no admissible setting: the budget refused all", size=12)
    return svg


def fig_margins(run: Run) -> Svg:
    svg = Svg(900, 360, "Figure 8: each net minus CoactDetect in held-out F1, per outer fold of this "
                        "run, with the mean of this run and of the replicate")
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
            assert lo <= v <= hi, f"{m} {w}: {v} is off the axis; widen it"
            svg.circle(X(v), y, 4.0, fill=NET_INK)
        svg.line(X(c["mean"]), y - 10, X(c["mean"]), y + 10, stroke=NET_INK, w=2.2)
        rm = run.repl["comparisons"][w][f"{m} - coact"]["mean"]
        s = 5
        svg.add(f'<path d="M{X(rm):.1f} {y - s:.1f} L{X(rm) + s:.1f} {y:.1f} L{X(rm):.1f} '
                f'{y + s:.1f} L{X(rm) - s:.1f} {y:.1f} Z" fill="none" stroke="{REPL_INK}" '
                f'stroke-width="1.8"/>')
    ly = yb + 58
    svg.circle(300, ly, 4.0, fill=NET_INK)
    svg.text(310, ly + 4, "one outer fold, this run", size=12)
    svg.line(470, ly - 8, 470, ly + 8, stroke=NET_INK, w=2.2)
    svg.text(478, ly + 4, "mean, this run", size=12)
    svg.add(f'<path d="M590 {ly - 5} L595 {ly} L590 {ly + 5} L585 {ly} Z" fill="none" '
            f'stroke="{REPL_INK}" stroke-width="1.8"/>')
    svg.text(602, ly + 4, "mean, the replicate", size=12)
    svg.line(730, ly - 8, 730, ly + 8, stroke="#111", dash="4 3")
    svg.text(738, ly + 4, "0: a tie", size=12)
    return svg


# ---- tables --------------------------------------------------------------------------------------

def tcap(n: int, text: str) -> str:
    return f'<p class=tcap><b>Table {n}.</b> {text}</p>'


CODED_WHAT = {
    "coact": ("counts distinct ROIs firing together in a sliding window and asks how unlikely that "
              "count is against the same recording shifted in time",
              "designed here; excess-coincidence testing (Grün and colleagues 2002)"),
    "loco": ("counts ROIs active together in a sliding window and compares the count with a "
             "percentile of the same count on the recording shifted in time",
             "designed here; excess-coincidence testing"),
    "rate": ("compares the population's firing rate with its own slower average",
             "designed here; the structure of Finn and Johnson 1968"),
    "sce": ("counts ROIs active in fixed time bins and thresholds the count against circularly "
            "shifted copies (synchronous calcium events, SCE)",
            "the rule of Cossart, Aronov and Yuste 2003"),
    "sync": ("measures how closely ROIs' firing aligns, with a coincidence window set by the local "
             "gaps between each ROI's events", "built on Kreuz, Mulansky and Bozanic 2015"),
    "cicada": ("counts ROIs active within a few frames and thresholds against each ROI rolled in "
               "time", "a modified port of CICADA (Denis and colleagues 2020)"),
}
NET_WHAT = {
    "chorus_norm": "filters each ROI separately, standardizes it over time, lets it cast a vote "
                   "bounded between 0 and 1, then pools the votes three ways (mean, spread, loudest "
                   "few)",
    "chorus_gain_norm": "as chorus_norm, with a fitted gain and offset on each vote",
    "line_length": "smooths each ROI separately, lets it cast a vote bounded in height, takes the "
                   "share of ROIs lit, then compares that share with its own surroundings in time",
    "tube": "pools all the ROIs into one trace first, then compares it with its own surroundings in "
            "time; a few cells firing repeatedly can look to it like many cells firing once",
}


def contestants_table(run: Run) -> str:
    rows = []
    for m in NETS:
        axes = run.decl["learned_axes"][m]
        rows.append([f"<b>{esc(m)}</b>", "net", esc(NET_WHAT[m]), "this project",
                     f"{len(axes)} settings; 24 configurations drawn at random"])
    for d in CODED:
        axes = run.decl["hand_axes"][d]
        n_values = sum(len(v) for _, v in axes)
        what, origin = CODED_WHAT[d]
        rows.append([f"<b>{esc(NAME[d])}</b>", "coded", esc(what), esc(origin),
                     f"{len(axes)} settings, {n_values} grid values, searched one setting at a time"])
    return tcap(1, "The ten contestants.") + table(
        ["contestant", "kind", "what it does", "where it comes from", "what was tuned"], rows,
        "Table 1: the ten contestants")


def headline_table(run: Run) -> str:
    rows = []
    for m in list(NETS) + list(CODED):
        cells = [f"<b>{esc(NAME[m])}</b>"]
        for w in SEL:
            if m in CODED and all(run.refused_all(m, w)):
                cells += ["no admissible setting", "—"]
                continue
            vals = run.f1(m, w)
            cell = num(float(np.mean(vals)), 3)
            if m in CODED:
                bad = sum(1 for ok in run.admissible(m, w) if not ok)
                if bad:
                    cell += f" <span class=dim>({bad} of 4 not admissible)</span>"
            cells.append(cell)
            if m == "coact":
                cells.append("—")
            else:
                c = run.cmp(m, "coact", w)
                cells.append(f"{num(c['mean'], 3)} <span class=dim>(<i>t</i> {num(c['t'], 1)}; "
                             f"corrected {num(c['t'] * run.nb, 1)})</span>")
        rows.append(cells)
    return tcap(2, "Held-out F1, mean of the four outer folds, and each contestant minus CoactDetect "
                   "(a difference in F1, with its paired <i>t</i> and the corrected <i>t</i>, section "
                   "6).") + table(
        ["contestant", "mean F1, F1 alone", "minus CoactDetect", "mean F1, under the budget",
         "minus CoactDetect"], rows, "Table 2: held-out F1")


def coded_table(run: Run) -> str:
    rows = []
    ref = run.crowded["reference"]
    grids = {d: dict(run.decl["hand_axes"][d]) for d in CODED}
    for d in CODED:
        for w in SEL:
            chosen = [row[w]["chosen_params"] for row in run.results["hand"][d]]
            key = next((k for k in ("merge_gap_sec", "merge_gap_s") if k in grids[d]), None)
            if key is None:
                gap = "no merge setting"
            else:
                vals = sorted({float(c[key]) for c in chosen})
                top = max(grids[d][key])
                gap = ", ".join(f"{v:g} s" for v in vals) + (" (top of its grid)" if top in vals else "")
            crowd = [c["crowded_mean_f1"] for c in run.crowded["choices"]
                     if c["detector"] == d and c["selection"] == w]
            lo, hi = min(crowd), max(crowd)
            crowd_s = num(lo, 3) if abs(hi - lo) < 5e-4 else f"{num(lo, 3)}–{num(hi, 3)}"
            note = []
            if sum(run.refused_all(d, w)):
                note.append(f"the budget refused every setting in {sum(run.refused_all(d, w))} of 4 "
                            "folds; the search returned its starting point")
            rows.append([esc(NAME[d]), esc(SEL_NAME[w]), esc(gap), crowd_s,
                         num(ref[d]["crowded_mean_f1"], 3), f"{sum(run.veto(d, w))} of 4",
                         esc("; ".join(note)) or "—"])
    return tcap(3, "Each coded detector's choices, checked on the crowded recordings (section 4.5).") \
        + table(["detector", "selection", "merge gap chosen", "crowded F1 of the choices",
                 "crowded F1 of the setting it replaces", "folds passing", "also"], rows,
                "Table 3: the coded choices on crowded recordings")


# ---- the page ------------------------------------------------------------------------------------

def body(run: Run) -> str:
    d, r = run.decl, run.results
    wall = run.wall_hours()
    facts = problem_recording()[3]
    crowd = crowded_spacing()
    coact = {w: float(np.mean(run.coded_f1("coact", w))) for w in SEL}
    same_coact = all(a["ungated"]["chosen_params"] == a["gated"]["chosen_params"]
                     for a in r["hand"]["coact"])
    best = {w: max(NETS, key=lambda m: np.mean(run.net_f1(m, w))) for w in SEL}
    cu, cg = run.cmp(best["ungated"], "coact", "ungated"), run.cmp(best["gated"], "coact", "gated")
    # The merge-gap evidence, both directions, choices on F1 alone.
    cg_gaps, cg_vals, cg_chosen = run.coded_gap_curve("coact")
    coact_at_2 = cg_vals[2.0]
    bn = best["ungated"]
    bn_run = run.net_f1(bn, "ungated")
    ahead_at_2 = sum(1 for a, b in zip(bn_run, coact_at_2) if a > b)
    diff_at_2 = float(np.mean(bn_run) - np.mean(coact_at_2))
    ng, nvals = run.net_gap_curve(bn)
    # Matched at the coded side's own 8 s: the net re-decoded at 8 s against CoactDetect as run.
    bn_at_8, coact_at_8 = nvals[8.0], cg_vals[8.0]
    ahead_at_8 = sum(1 for a, b in zip(bn_at_8, coact_at_8) if a > b)
    diff_at_8 = float(np.mean(bn_at_8) - np.mean(coact_at_8))
    net_best_gap = max(ng, key=lambda g: np.mean(nvals[g]))
    net_at_best = float(np.mean(nvals[net_best_gap]))
    coact_at_30 = float(np.mean(cg_vals[30.0]))
    repro_coded, repro_net = run.gap_repro()
    sce_gaps, sce_vals, _ = run.coded_gap_curve("sce")
    sce_at_8 = float(np.mean(sce_vals[8.0]))
    sce_run = float(np.mean(run.coded_f1("sce", "ungated")))
    sce_pass = {w: sum(run.veto("sce", w)) for w in SEL}
    sce_pass_fold = [h for h in run.folds if run.veto("sce", "gated")[h]]
    tun = {m: run.tuning(m, "ungated") for m in NETS}
    lows = run.low_refits()
    over = {m: run.over_budget_nets(m) for m in NETS}
    n_refits_gated = sum(len(row["gated"]["per_seed"]) for m in NETS for row in r["learned"][m])
    ref = d["reference"]["params"]
    base = d["coded_base"]["values"]
    spf, folds = d["seeds_per_fold"], d["folds"]
    ahead_folds = [(m, w, h, v) for m in NETS for w in SEL
                   for h, v in enumerate(run.cmp(m, "coact", w)["per_fold"]) if v > 0]
    quiet, busy = (bench.REGIMES[k]["bg_rate_hz"] for k in ("baseline_quiet", "baseline_busy"))
    hot = bench.BENCH_RECORDING["hot_rate_hz"]
    open_items = d.get("measured_outside_interval") or {}
    repl_agree = all(run.repl["comparisons"][w][f"{m} - coact"]["mean"] < 0 for m in NETS for w in SEL)
    earlier = 0.103     # docs/goals/learned-model-family.md, the untuned home-spec table (cited below)
    within = max(abs(cu["mean"]), abs(diff_at_2), abs(diff_at_8))
    no_admissible = [dd for dd in CODED if not any(run.admissible(dd, "gated"))]
    veto_fail_gated = [dd for dd in no_admissible if not all(run.refused_all(dd, "gated"))]
    refused_gated = [dd for dd in no_admissible if all(run.refused_all(dd, "gated"))]
    sce_below = sce_at_8 < coact["ungated"]
    rising = {dd: all(np.mean(run.coded_gap_curve(dd)[1][a]) <= np.mean(run.coded_gap_curve(dd)[1][b])
                      for a, b in zip(run.coded_gap_curve(dd)[0], run.coded_gap_curve(dd)[0][1:]))
              for dd in ("coact", "sce", "loco")}

    def repro_txt(x):
        return "exactly" if x == 0 else f"within {x:.1g} F1"

    P = []
    P.append(f"""
<h1>Do the learned detectors beat the hand-written ones once both are tuned fairly?</h1>
<p class=dim>Simulated recordings, baseline periods, the fast stream (section 7).</p>
<p class=lede><b>The question.</b> This project detects <i>coordinated events</i>, moments when
several cells fire together, in calcium-imaging recordings. It has six hand-written ("coded")
detectors and a family of neural networks ("nets") trained to do the same job. An earlier
comparison put the best net {earlier:+.3f} F1 ahead of the coded detector CoactDetect, but on a
different simulator (since retired), with the nets untuned and CoactDetect tuned on one setting. This
run tunes both sides, on the current simulator, choosing every setting without looking at the
recordings it is scored on, and asks again.</p>
<p class=lede><b>The answer.</b> Once both sides are tuned, the best net and CoactDetect finish
within {within:.3f} F1 of each other, and which one is ahead turns on a setting the run treated
unequally: how close two calls must be before they are merged into one. The coded detectors' search
tuned it; the nets' was fixed at 2 seconds. At the settings the run chose, 2 seconds for the nets
and 8 for CoactDetect, CoactDetect is ahead of the best net, {esc(bn)}, by {num(-cu['mean'], 3)} F1.
With the gap matched, {esc(bn)} is ahead: by {diff_at_2:+.3f} with both at 2 seconds ({ahead_at_2}
of 4 folds) and by {diff_at_8:+.3f} with both at 8 ({ahead_at_8} of 4 folds). So this run does not
settle which side is better. A second, independent draw of recordings on another workstation
{'agrees that no net is ahead at the settings as chosen' if repl_agree else 'does not agree on every margin'};
it was not re-scored at matched gaps (section 5). One coded detector, binned SCE, finishes ahead of all of them, and only by merging calls
up to 30 seconds apart. On real recordings, where coordinated events can come a few seconds apart,
that would fuse separate events (section 4.5).</p>
<p>Terms used throughout: <b>ROI</b>, region of interest, one imaged cell; <b>F1</b>, the harmonic
mean of recall (the share of planted events found) and precision (the share of calls that were
real), from 0 to 1; <b>GPU</b>, graphics processor; <b><i>t</i></b>, the paired <i>t</i> statistic
across the four outer folds, on 3 degrees of freedom, read as described in section 6. <b>Goal 1</b> is
an earlier study in this program that tuned the six coded detectors alone, every setting they
accept, and settled the values this run starts them from (section 4.3). <b>The project lead</b> is
the scientist who owns this project and made the design decisions cited below.</p>
""")

    P.append(f"""
<h2 id="problem">1. The problem: finding coordinated events</h2>
<p>Each row of a raster is one ROI; each tick is a moment the cell fired. A coordinated event is
several ROIs firing within a fraction of a second of one another, more often than chance would put
them together. Two things make that hard. The cells fire at very different rates, so a busy cell
lands near others by accident all the time. And the whole field sometimes becomes busier for
minutes at a stretch, which raises chance coincidences everywhere without anything coordinated
happening. A detector has to find the few real events without firing on either.
<a href="#fig1">Figure 1, one simulated recording</a>, shows what a detector meets: a planted
event, marked in the lane above the raster; two <i>distractors</i>; and the <i>probe</i>, five
minutes in which every ROI fires an extra {hot:g} times a second, about
{hot / quiet:.0f} times the quiet background rate and {hot / busy:.0f} times the busy one, with
nothing planted in it. A distractor is built exactly as an {facts['event_frac']:.0%} planted event
is built, and is labeled a negative: a call on one counts against the detector. Whether real
coincidence of that kind should count against a detector is an open question in this project; here
it counts the same way for every contestant.</p>
{figure(1, "One simulated recording and what is in it", fig_problem(),
        f"About ten minutes ({mmss(FIG1_WINDOW[0])} to {mmss(FIG1_WINDOW[1])}) of one simulated "
        f"recording with the busy background, recording seed {FIG1_SEED}, from the project's "
        f"simulator (section 2). <b>Raster</b>: {bench.BENCH_RECORDING['n_roi']} ROIs, one tick per "
        f"event, ranked by how often each fires inside this window. <b>Lane</b> above it: the filled "
        f"blue down-triangle marks the planted coordinated event at {mmss(facts['event_t'])}, "
        f"{facts['n_part']} ROIs spread over {bench.BENCH_RECORDING['jitter_sec']:g} s (the "
        f"standard deviation of their onsets); the hollow gray down-triangles mark "
        f"{len(facts['distractors'])} distractors; the hatched band marks the probe, from "
        f"{mmss(bench.BENCH_RECORDING['hot_window'][0])}, ramping up over its first "
        f"{bench.BENCH_RECORDING['ramp_sec']:g} s. Nothing is drawn on the raster. Finding the event "
        f"means finding {facts['n_part']} aligned ticks among the "
        f"{facts['n_onsets']:,} events in the whole "
        f"{bench.BENCH_RECORDING['duration_sec'] / 60:.0f}-minute recording.")}
""")

    P.append(f"""
<h2 id="bench">2. Why a simulation, and what it simulates</h2>
<p>A real recording has no answer key: nobody knows for certain which moments were coordinated, so
F1 cannot be computed on it. The project's <b>bench</b> is a simulator whose settings are measured
from real baseline recordings, so its recordings look like real ones, but every planted event is
known.</p>
<p>Each bench recording is {bench.BENCH_RECORDING['duration_sec'] / 60:.0f} minutes of
{bench.BENCH_RECORDING['n_roi']} ROIs. It holds 15 planted events, 5 at each of three participation
levels: 30%, 18% and 10% of the ROIs. Each event's onsets are spread by
{bench.BENCH_RECORDING['jitter_sec']:g} s, and events are at least
{bench.BENCH_RECORDING['min_sep_sec']:g} s apart. It also holds
{bench.BENCH_RECORDING['n_distractors']} distractors and the probe.</p>
<p>Every recording seed (the random seed that generates one recording) is simulated at <b>two
backgrounds</b>: {quiet:g} and {busy:g} events per second per ROI. These are the 25th and 75th
percentiles of the rates in real baseline recordings. A detector's score is its F1 pooled within
each background, then averaged over the two, so doing well at only one background is not enough.</p>
<p>A call is a <b>hit</b> if its time span, widened by {score.TOL_SEC:g} s, contains a planted
event. {score.TOL_SEC:g} s is where the scores stop changing as the tolerance widens. One
consequence matters later: a call that spans a long stretch hits any event inside it. Calls inside
the probe are counted separately, as false alarms per hour, and kept out of precision.</p>
<p>This run used {folds * spf * 2} recordings with planted events ({folds * spf} seeds,
{d['recording_seeds'][0]}–{d['recording_seeds'][-1]}, at both backgrounds), plus
{folds * spf * 2} with nothing planted (one per seed at each background), used to count false
alarms.</p>
""")

    P.append(f"""
<h2 id="contestants">3. The contestants</h2>
<p>Ten detectors, four learned and six coded (Table 1). The nets are known by their names in the
code. Three of them led the earlier untuned comparison. The fourth, <code>tube</code>, was kept as a
control because it tied CoactDetect there. On this simulator it no longer ties: untuned, it scores
{num(float(np.mean([row['untuned']['f1_mean'] for row in r['learned']['tube']])), 3)} against
CoactDetect's {num(coact['ungated'], 3)}.</p>
<p>The difference between the nets that matters most is where each stops treating ROIs separately.
<code>tube</code> pools them first. The other three keep each ROI separate long enough for it to cast
a bounded vote, then pool the votes. Each net ends in a probability per frame, and its threshold on
that probability is chosen on training recordings.</p>
{contestants_table(run)}
<p class=warn><b>The architecture drawings are not on this page yet.</b> The four nets are drawn by
draughtsman, the project's architecture-diagram tool, one specification per model traced from the
code, all at one scale, and shared with the replicate's report so both pages show the same
drawings. They are at <code>{ARCH_PAGE}</code> and, once it lands, <code>{ARCH_REPO}</code>.</p>
<p class=dim>Full citations for the coded detectors' origins are in the repository's README, section
"Licensing &amp; citations", and in <code>docs/detector_history.md</code>.</p>
""")

    lr, steps = (dict(d["learned_axes"]["chorus_norm"])[k] for k in ("lr", "steps"))
    P.append(f"""
<h2 id="fair">4. How the comparison was kept fair</h2>
<h3>4.1 Nested cross-validation: choose on some recordings, score on others</h3>
<p>If a setting is chosen by looking at the recordings it is then scored on, the score flatters it.
<b>Nested cross-validation</b> prevents that (<a href="#fig2">Figure 2, the nested layout</a>). The
{folds * spf} recording seeds are split into {folds} <b>outer folds</b> of {spf}. Each fold takes one
turn being held out. With it set aside, every candidate setting is judged on the other three folds
alone. The winner is then scored once on the held-out fold, which is never seen while choosing.</p>
<p>The two sides are judged on those three folds differently, because only the nets have anything to
fit. A coded detector has no parameters to learn, so each candidate setting is scored once on all
three training folds pooled. A net is fitted, so each candidate is fitted on two training folds and
scored on the third, three ways round (the <b>inner</b> loop, panel B), at 3 training seeds (the
random start of a net's training, unrelated to recording seeds). The chosen net is then refitted at 5
training seeds and scored on the held-out fold.</p>
<p>Each net had 24 configurations, drawn at random before the run started, from a grid over its
learning rate ({', '.join(f'{v:g}' for v in lr)}), its training steps
({', '.join(f'{v:,}' for v in steps)}), and 3 or 4 settings of its own architecture. The untuned
setting was always among them. Each coded detector's search moved one setting at a time through goal
1's declared grids (Table 1). Settings that break the context-window rule in section 4.5 were
skipped.</p>
{figure(2, "The nested cross-validation layout", fig_nested(run),
        "<b>A</b>: the four outer folds; each takes one turn being scored, while the other three are "
        "used to choose. Folds are numbered 1 to 4 here and 0 to 3 in the run's files. <b>B</b>: "
        "for a net, inside held-out fold 1, each candidate configuration is fitted on two training "
        "folds and scored on the third, three ways round. A coded detector skips this rotation: "
        "each candidate setting is scored once on folds 2 to 4 pooled.")}

<h3>4.2 A defect fixed before the run: outer folds were training the same model</h3>
<p>A net does not train on every training recording. It fits a run of 10 consecutive recordings
from the list it is given, and the last two recordings on the list pick its threshold. Until this
run the list was in fold order. At some training seeds the run of 10 then fell inside the first
training fold, so held-out folds that share that fold trained exactly the same model.
<a href="#fig3">Figure 3, the fitting draws before and after</a>, shows it at training seed 0 on this
run's own split: three of the four held-out folds would have fitted the same ten recordings. Four
outer folds were then fewer than four independent fits, and a comparison across folds counts
independence it does not have.</p>
<p>The fix deals the recordings across the training folds in turn, starting after the held-out one,
so every fit reaches every training fold and the threshold recordings rotate too. Before launching,
the run replayed the exact draws for every training seed. It would have refused to start if any two
outer folds shared a fitting set or threshold recordings.</p>
{figure(3, "Which recordings each outer refit fitted, at training seed 0", fig_defect(run),
        "Each strip is the 48 recording seeds, one cell per seed; each seed stands for its two "
        "recordings, one at each background. <b>A</b>: the order used before the fix, applied to "
        "this run's split. Held-out folds 2, 3 and 4 fit the same ten recordings, seeds 1000 to "
        "1004. Fold 1's set differs only because fold 1 is the one held out. <b>B</b>: what this "
        "run actually fitted, read from its fit records: four different sets, each reaching every "
        "training fold. The folds still share training data, since each fold trains three others; "
        "section 6 says what that does to the statistics.")}

<h3>4.3 The coded side runs in its better mode</h3>
<p>For CoactDetect and LoCo, every setting the search did not vary was held at goal 1's values, not
at the project's current default settings. The difference is the counting mode. <i>Binned</i> mode
counts coincidences in fixed time bins. <i>Sliding</i> mode counts them in a window that moves
smoothly. Goal 1 found sliding mode better on held-out recordings. It also found that sliding mode
keeps its calls when a recording is shifted by a fraction of a second, where binned mode can lose
them. The project's defaults are still binned, so a search built on them would have tuned the coded
side in its weaker mode.</p>
<p>The reference CoactDetect below therefore uses goal 1's settings:</p>
<ul>
<li>alpha (the significance level for calling an event) {ref['alpha']:g};</li>
<li>a context window (the stretch used to estimate chance) of {ref['context_win_sec']:g} s;</li>
<li>a merge gap of {ref['merge_gap_sec']:g} s;</li>
<li>a guard of {ref['guard_sec']:g} s (the stretch around an event left out of that estimate).</li>
</ul>
<p>LoCo uses the {base['loco']['threshold_pctile']:g}th percentile and an
{base['loco']['merge_gap_sec']:g} s merge gap.</p>

<h3>4.4 Two selections, and one false-alarm budget for everyone</h3>
<p>Choosing on F1 alone rewards a detector that calls more: extra calls can pick up extra planted
events faster than they cost precision. So every contestant was chosen twice. Once on F1 alone,
asking which setting finds the most events. Once on F1 among the settings within a <b>shared
false-alarm budget</b>, asking which finds the most while firing no more than CoactDetect does
(<a href="#fig4">Figure 4, the two selections</a>).</p>
<p>The budget is anchored to the reference CoactDetect. On each outer fold's training recordings, a
candidate may fire at most {d['budget_margin']:g} times as often as the reference does, both in the
probe at each background and on the quiet recordings with nothing planted. {d['budget_margin']:g} is
a margin the project lead declared before the run, not a measured value. The budget never drops
below one false alarm in the time measured, a floor that bound in no fold.</p>
<p>For a net, the two selections choose from the same fits, and its threshold is chosen inside the
budget too. For a coded detector they are two separate searches: the budget changes which steps the
search can take.</p>
{figure(4, "Two selections from the same candidates", fig_budget(run),
        "A schematic, not data. Each gray point is a candidate setting, with its F1 and its firing "
        "rate on the training recordings; for a net, a candidate is a configuration with one of its "
        "thresholds. The black square is the reference CoactDetect. The unshaded region is within "
        f"the budget, {d['budget_margin']:g} times the reference's rate, measured in the probe and "
        "on the quiet recordings with nothing planted.")}

<h3>4.5 One setting the two sides did not share: the merge gap</h3>
<p>Every detector here produces calls, and calls closer together than a <b>merge gap</b> are merged
into one. On this bench, events are at least {bench.BENCH_RECORDING['min_sep_sec']:g} s apart. A wide
merge gap therefore loses nothing: it folds the near-duplicate calls around one event into one call,
which raises precision, and the merged call still hits its event (section 2's hit rule). On real
recordings, coordinated events can come a few seconds apart, and a wide merge fuses them
(<a href="#fig5">Figure 5, merging and its effect on F1</a>, panel A).</p>
<p>The coded detectors' searches tuned their merge gaps. The nets' was fixed at 2 s, the default
their threshold picker returns, and never searched. Panel B shows what the gap is worth on each side.
Only the merge gap was changed: every coded choice was rescored, and every chosen net refit was
re-decoded from its saved model, keeping its threshold. Both sides first reproduce the run's own
scores at their own gaps: the coded detectors {repro_txt(repro_coded)}, the nets
{repro_txt(repro_net)}. On this bench, a wider merge helps
{'every coded detector shown' if all(rising.values()) else ', '.join(NAME[k] for k, v in rising.items() if v)}. CoactDetect
rises from {num(float(np.mean(coact_at_2)), 3)} at 2 s to {num(coact['ungated'], 3)} at its chosen
8 s and {num(coact_at_30, 3)} at 30 s. {esc(bn)} scores {num(float(np.mean(bn_run)), 3)} at its 2 s
and {num(net_at_best, 3)} at its best gap tried, {net_best_gap:g} s. Nothing was re-chosen, so these
curves bound what tuning the gap could do rather than measure it.</p>
<p>Goal 1 met the same effect and added a rule before this run: the <b>crowded-recording check</b>.
A setting may not score more than {run.crowded['max_crowded_drop']:g} F1 below the setting it
replaces on <b>crowded recordings</b>. These are {crowd['n_recordings']} bench recordings with
{crowd['n_events'][0]} events each, spaced as the crowded end of real recordings is: at least
{crowd['min']:.0f} s apart, median {crowd['median']:.0f} s. {run.crowded['max_crowded_drop']:g} is a
judgment the project lead has not yet signed. The run's own search did not apply the check (its
declaration does not mention it). It was applied afterwards, when the other workstation pointed at
the merge gaps, by <code>tools/crowded_check_fair_comparison.py</code>. That tool uses goal 1's own
scoring on {crowd['n_recordings'] // 2} crowded recordings per background.</p>
<p>The setting a choice replaces is the one its search started from: goal 1's values for CoactDetect
and LoCo, and the project's defaults for the others. Goal 1 compares against the project's shipped
defaults instead. Scored against those, no verdict changes. The nets were not checked on crowded
recordings; their merge gap is fixed, so their search could not choose a wide one.</p>
{figure(5, "Merging calls, and what the merge gap is worth on each side", fig_merge(run),
        "<b>A</b>: a schematic. <b>B</b>: held-out F1, mean of the four outer folds, for choices on "
        "F1 alone, with only the merge gap changed. Black: CoactDetect; gray dashed: binned SCE; "
        "gray dotted: LoCo; blue: the nets, re-decoded at each gap, with the best net drawn "
        "thicker. A ring marks the gap each detector was actually run at. "
        + ("The coded curves rise all the way to 30 s, because on this bench merging costs nothing "
           "(panel A); that rise is what the crowded-recording check exists to stop."
           if all(rising.values()) else
           "Where a coded curve rises with the gap, merging is costing it nothing on this bench "
           "(panel A); that rise is what the crowded-recording check exists to stop."))}
""")

    P.append(f"""
<h2 id="replicate">5. A second, independent draw of recordings</h2>
<p>Four outer folds give only 3 degrees of freedom, and a margin of a hundredth of F1 can come and go
with which recordings happened to be drawn. So the workstation WSMIP065 ran the same comparison on
a disjoint set of recordings (<a href="#fig6">Figure 6, the two draws</a>): recording seeds
{run.repl['recording_seeds'][0]}–{run.repl['recording_seeds'][1]} instead of
{d['recording_seeds'][0]}–{d['recording_seeds'][-1]}. The configurations, grids, training seeds, budget
rule and simulator were held fixed. A difference between the two runs is then a difference between
draws of data. This page shows the replicate's headline numbers beside this run's in Figure 8, copied
from its results; its own report is the authority on it: <code>{esc(REPLICATE_PAGE)}</code>.</p>
{figure(6, "The two draws of recordings", fig_draws(run),
        "<b>A</b>: this run's 48 recording seeds, in its 4 outer folds of 12. <b>B</b>: the "
        "replicate's. The two share no recording.")}
""")

    tun_rows = "".join(
        f"<li><code>{esc(m)}</code>: per fold "
        f"{', '.join(f'{v:+.3f}' for v in tun[m]['per_fold'])} (mean {tun[m]['mean']:+.3f}).</li>"
        for m in NETS)
    low_rows = "".join(
        f"<li><code>{esc(m)}</code>, {fold_label(h)}, training seed {s + 1} of 5: F1 {num(f, 3)}, "
        f"in the {' and '.join('untuned setting' if w == 'untuned' else 'choice on ' + SEL_NAME[w] for w in ws)}. "
        + ("It made no calls at all at a threshold picked on two recordings, and a F1 with no calls "
           "counts as 0." if nan else "")
        + (" Its record carries the failed-training signature: it calls one long stretch per "
           "recording, so its few hits come at perfect precision and almost no recall." if sig else "")
        + "</li>" for m, h, s, f, nan, sig, ws in lows)
    over_rows = "".join(
        f"<li><code>{esc(m)}</code>: {sum(over[m])} of {sum(len(row['gated']['per_seed']) for row in r['learned'][m])} "
        f"(per fold {', '.join(str(v) for v in over[m])}).</li>" for m in NETS)
    ahead_txt = ("No fold has a net ahead of CoactDetect." if not ahead_folds else
                 "Where a dot sits right of zero, the net is ahead in that fold: " + "; ".join(
                     f"{m} on {SEL_NAME[w]}, {fold_label(h)}, by {v:.4f}" for m, w, h, v in ahead_folds)
                 + ".")
    P.append(f"""
<h2 id="results">6. What came out</h2>
<p><b>How to read the <i>t</i> values first.</b> They are paired <i>t</i> statistics over four folds.
Each training fold serves three held-out folds, so the folds are less independent than the
statistic assumes, and the plain values overstate the evidence. Table 2 therefore also gives each
<i>t</i> multiplied by {run.nb:.2f}, the correction of {N_B_FACTOR_NOTE} (Machine Learning
52:239–281) for a test set one third the size of its training set.</p>
<p>That correction was derived for repeated random splits, not for k-fold cross-validation. Bouckaert
and Frank (2004) carry it over to k-fold as a heuristic, and Bengio and Grandvalet (2004) show that no
exact correction exists for k-fold. Read the corrected values as a ranking of consistency, not as
tests. At 3 degrees of freedom, a two-sided 5% test would need about 3.2. The second draw of
recordings (section 5) is the stronger check.</p>
<p><a href="#fig7">Figure 7, held-out F1 for all ten contestants</a>, shows every outer fold.
Table 2 gives the means and each contestant's difference from CoactDetect.</p>
{figure(7, "Held-out F1 per outer fold", fig_results(run),
        "One row per contestant: nets in blue above the dashed line, coded detectors in black below "
        "it. Each fold is drawn on its own line within the row, so four folds are always four marks. "
        "For a net, a fold's value is the mean over its 5 refits. The bar is the mean of the 4 folds. "
        "A hollow circle is a coded choice that fails the crowded-recording check (section 4.5). An "
        "× is a fold where the budget refused every setting the search tried; the search then "
        "returned its starting point, which is not an admissible result.")}
{headline_table(run)}
<p>What the table says, in order of weight:</p>
<ul>
<li><b>At the settings the run chose, no net is ahead of CoactDetect on average.</b> The best net on
F1 alone, <code>{esc(best['ungated'])}</code>, trails it by {num(-cu['mean'], 3)} F1. Under the
budget, <code>{esc(best['gated'])}</code> trails by {num(-cg['mean'], 3)}. CoactDetect scores
{num(coact['ungated'], 3)} on F1 alone and {num(coact['gated'], 3)} under the budget{' (its searches chose the same settings both ways in every fold)' if same_coact else ''}.
Its choices pass the crowded-recording check in
{sum(run.veto('coact', 'ungated')) + sum(run.veto('coact', 'gated'))} of 8 cases (4 folds × 2
selections). <a href="#fig8">Figure 8, each net minus CoactDetect</a>, shows the margins fold by fold,
with the replicate's means.</li>
<li><b>With the merge gap matched, the order reverses.</b> Both at 2 s, <code>{esc(bn)}</code> is
ahead of CoactDetect in {ahead_at_2} of 4 folds, by {diff_at_2:+.3f} on average. Both at 8 s
(<code>{esc(bn)}</code> re-decoded, CoactDetect as run), it is ahead in {ahead_at_8} of 4 folds, by
{diff_at_8:+.3f} (section 4.5). Nothing was re-chosen at the new gap, so these are bounds, not tuned
results, and the nets were not checked on crowded recordings at 8 s. Which side is ahead is not
settled by this run; a rerun that tunes the nets' merge gap like any other setting would settle it,
and needs no retraining.</li>
<li><b>Tuning moved some nets and not others.</b> Tuned minus untuned, on F1 alone:
<ul>{tun_rows}</ul>
<code>line_length</code> gained in three folds. <code>chorus_gain_norm</code>'s mean includes one
refit that failed to train (below). <code>chorus_norm</code> and <code>tube</code> barely moved.
The earlier lead does not reappear on this simulator, but this run cannot say which of three changes
removed it: the new simulator, CoactDetect's sliding values from goal 1, or the tuning.</li>
<li><b>Binned SCE finishes first on paper, at {num(sce_run, 3)} on F1 alone, and that is its merge
gap, not a better detector.</b> Its search chose a 30 s merge gap, the top of its grid, in every
fold. Held to 8 s, the same choices score {num(sce_at_8, 3)} (Figure 5, panel B),
{'below' if sce_below else 'still above'} CoactDetect's {num(coact['ungated'], 3)}. Its choices fail the crowded-recording check in {8 - sce_pass['ungated'] - sce_pass['gated']} of 8
cases (Table 3). One passes: {fold_label(sce_pass_fold[0]) if sce_pass_fold else 'none'} under the
budget, where the check sits close to its limit.</li>
<li><b>Under the budget, {len(no_admissible)} coded detectors have no admissible result in any
fold.</b> {', '.join(NAME[x] for x in veto_fail_gated)} fail the crowded-recording check in every
fold: the budget forced them into stricter settings that lose events everywhere, crowded recordings
included, which is a different failure from binned SCE's wide merge.
{' '.join(f'For {NAME[x]}, the budget refused every setting its search tried, so it has no result under the budget at all.' for x in refused_gated)}
(Table 3.)</li>
</ul>
{figure(8, "Each net minus CoactDetect, per outer fold", fig_margins(run),
        "Each blue dot is one outer fold of this run: the net's held-out F1 (mean over 5 refits) "
        "minus CoactDetect's on the same fold. The blue bar is this run's mean. The orange diamond "
        "is the same mean in the replicate (section 5), on recordings this run never used. Left of "
        f"the dashed zero line, CoactDetect is ahead. {ahead_txt} The two far-left dots are folds "
        "where one of five refits scored below 0.2 F1 (listed below).")}
{coded_table(run)}
<h3>Refits below 0.2 F1</h3>
<p>Of the {run.n_stage('outer')} held-out refits of nets, {len(lows)} scored below 0.2 F1; every
other refit scored at least {num(run.lowest_other_refit(), 2)}, so the cut falls in an empty
stretch of the distribution. Both are included in every mean above:</p>
<ul>{low_rows}</ul>
<h3>Choices that exceeded the budget on new data</h3>
<p>A choice made within the budget on the training folds can exceed it on the held-out fold. Among
the coded choices under the budget, CoactDetect exceeded it in
{sum(1 for x in r['hand']['coact'] if x['gated'].get('over_budget'))} of 4 folds. Among the
{n_refits_gated} held-out refits of nets chosen under the budget, these exceeded it:</p>
<ul>{over_rows}</ul>
<p>Exceeding the budget can only help a net's F1 under the budget, so this does not favor the coded
side.</p>
""")

    part = open_items.get("participation", "")
    P.append(f"""
<h2 id="limits">7. Limits</h2>
<ul class=resid>
<li><b>Baseline periods only, fast stream only.</b> The project lead's decision of 2026-09-17 for this
run. The recordings in this project have two event streams (fast and slow), and periods before
(baseline) and during drug treatment. The bench is fitted to the baseline periods of the fast stream,
so nothing here says how any detector behaves in treatment periods or on the slow stream.</li>
<li><b>The bench's fitted values were measured on data with a known, uncleared contamination.</b>
They were last measured on the export folder <code>steps_excluded</code>. In a few ROIs of that folder,
motion correction clamped the signal to its minimum value, and the detectors call events on the
steps in and out of it: about 0.03% of events (<code>HANDOFF-slow-comodulation-on-the-de-pinned-export.md</code>,
decision 3). Both workstations re-measured the bench on the corrected folder on 2026-09-17, and every
value moved by less than its own bootstrap interval. That record is commit 2120516 on branch
<code>tune-bench-comparison</code> (<code>HANDOFF-workstation-tuning.md</code>), not yet on
<code>main</code>. Moving the bench to the corrected folder has not been decided. This page states the
contamination as a limit because the project lead's brief for this report asked for exactly that; it
is not evidence that the effect is negligible.</li>
<li><b>One of the bench's values sits outside its own measured interval, and the decision on it is
open.</b> The run's declaration records it: <i>{esc(part)}</i></li>
<li><b>Simulation only.</b> Every number is on simulated recordings. The bench is measured from real
ones, but a detector that wins here has not thereby been shown to win on real data.</li>
<li><b>The merge gap was tuned for one side only</b> (section 4.5). A rerun with the nets' merge gap
chosen like any other setting needs no retraining, only re-scoring. It has not been run.</li>
<li><b>The nets were not checked on crowded recordings.</b> The headline was measured on well-spaced
events only.</li>
<li><b>The two sides learn from different amounts of data.</b> A net fits 10 of the 72 training
recordings and picks its threshold on 2. A coded setting, threshold included, is scored on all
72.</li>
<li><b>Four outer folds</b>, so every paired comparison rests on 3 degrees of freedom, and the folds
share training data (section 6).</li>
<li><b>The coded searches move one setting at a time</b> and can end in different places depending
on the path. Under the budget, a search can even score higher than without it.</li>
<li><b>Chosen values at the top of their grid</b> mean a search might have gone further. For the merge
gap, that is every coded detector with one (Table 3).</li>
<li><b>The fewest ROIs a coded detector will call an event on (<code>min_rois</code>) can learn the
bench's planted participation levels</b>, so its tuned value is a fact about this simulator.</li>
<li><b>One training run per seed, on one GPU.</b> A rerun on another GPU or on processors may not
reproduce these F1 values exactly; how far they would move is unmeasured.</li>
</ul>
""")

    n_jobs = len(run.ran)
    P.append(f"""
<h2 id="where">8. Where everything is</h2>
<ul>
<li><b>This report</b>: <code>&lt;darkroom&gt;/bugarach/{DARKROOM_FOLDER}/report/index.html</code>,
and <code>report.html</code> beside the run's summaries in the repository.</li>
<li><b>The run's summaries, in the repository</b>:
<code>docs/learned/tuned_vs_coact/fair_comparison_2026_09_18/</code>. It holds the declaration
(<code>meta.json</code>), <code>results.json</code>, the selections, configurations and job log, and
this report's derived files: <code>crowded_check.json</code>, <code>fold_draws.json</code>,
<code>merge_gap.json</code> and <code>replicate_summary.json</code>. Personal paths in them are
written as <code>%USERPROFILE%</code> and <code>&lt;darkroom&gt;</code>.</li>
<li><b>Everything else, in the darkroom</b>:
<code>&lt;darkroom&gt;/bugarach/{DARKROOM_FOLDER}/results/</code>. It holds the same summaries
unedited, the chosen settings and models (<code>chosen/</code>), every fitted model
(<code>fits.tar.gz</code>), every score table (<code>scores.tar.gz</code>, 1.1 GB unpacked) and the
run's log.</li>
<li><b>The code that ran</b>: <code>tools/tune_learned_vs_coact.py</code> on branch
<code>tune-bench-comparison</code> at <code>{esc(run.meta['started']['git']['commit'][:7])}</code>,
from a clean tree. The evidence tools are <code>tools/crowded_check_fair_comparison.py</code> and
<code>tools/fair_comparison_evidence.py</code>. To rebuild a net outside the trainer, go through the
registry, <code>ARCHITECTURES[name].make()</code>, as the trainer and <code>checkpoint.load</code>
do: calling <code>build_chorus_norm()</code> or <code>build_chorus_gain_norm()</code> directly builds
plain <code>chorus</code>, silently, because the registered settings arrive only through the
registry.</li>
<li><b>The size of the run</b>: {n_jobs:,} jobs, with no errors, over {wall:.1f} hours of wall
time:
<ul>
<li>1 reference measurement;</li>
<li>{run.n_stage('search')} coded-detector search jobs, 6 detectors × 4 outer folds, each running both
selections, on the processors;</li>
<li>{run.n_stage('inner'):,} inner fits of nets, one per configuration, training seed and pair of
training folds, a pair shared by the two outer folds that use it;</li>
<li>{run.n_stage('outer')} outer refits, on one GPU.</li>
</ul>
{r['cpu_hours_training']:.1f} hours of the run were spent training nets.</li>
</ul>
""")
    return "\n".join(P)


EXTRA_CSS = ("<style>code{overflow-wrap:anywhere}.tcap{margin:18px 0 4px;font-size:15px}"
             "</style>")


def provenance_line(run: Run) -> str:
    ver = provenance.code_version() or "unknown"
    dirty = provenance.git_dirty()
    note = ("" if dirty is False else
            " <b>The tree had uncommitted changes when this was built</b>, so the version above "
            "names a tree that exists nowhere else." if dirty else
            " Whether the tree was clean could not be checked.")
    return (f'<h2 id="provenance">Provenance</h2><p class=dim>Built '
            f"{time.strftime('%Y-%m-%d %H:%M %z')} by <code>tools/build_fair_comparison_report.py"
            f"</code> at <code>{esc(ver)}</code>.{note} The review record for this page is "
            f"<code>docs/reviews/fair-comparison-2026-09-19.md</code>.</p>")


def build(run_dir: Path) -> str:
    run = Run(run_dir)
    html = page("Tuned nets against tuned coded detectors",
                EXTRA_CSS + body(run) + provenance_line(run))
    return html.replace("<!doctype html>", '<!doctype html><html lang="en">', 1)


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--run", type=Path, default=DEFAULT_RUN)
    ap.add_argument("--out", type=Path, default=None,
                    help=f"destination folder (default: the darkroom's {DARKROOM_FOLDER}/report/)")
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
