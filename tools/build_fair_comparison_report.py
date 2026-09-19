#!/usr/bin/env python3
"""Write the fair comparison's report: tuned nets against tuned coded detectors, for a reader new to it.

    python tools/build_fair_comparison_report.py                     # darkroom only
    python tools/build_fair_comparison_report.py --also docs/learned/tuned_vs_coact/fair_comparison_2026_09_18

Tony, 2026-09-19: *"I'd like a full report from each machine written so someone new can understand.
Include figures to explain conceptually what was done and why."* So the page explains the problem,
the simulation, the contestants and how the comparison was kept fair **before** it shows a result,
and every number and every data figure is computed here from the run's committed files or from the
bench itself. Prose stating a fact about these data comes from code too, and a sentence that is no
longer true stops the build (``claim``) rather than shipping: the first draft typed one such
sentence, and it was false.

Reads the run's committed summary (``--run``, default
``docs/learned/tuned_vs_coact/fair_comparison_2026_09_18/``): ``results.json`` and ``meta.json``
as the run wrote them; ``crowded_check.json`` (``tools/crowded_check_fair_comparison.py``);
``fold_draws.json``, ``merge_gap.json`` and ``breakdown.json`` (``tools/fair_comparison_evidence.py``);
and ``replicate_summary.json``, the replicate's numbers copied from WSMIP065's results (its source is
recorded inside). Writes ``index.html`` to ``darkroom()/2026-09-18-fair-comparison-run/report/`` by
default (sapper SAP006) and ``report.html`` to ``--also``.

The page kit (``Svg``, ``figure``, ``page``, ``table``) is ``tools/build_surrogate_report.py``'s,
imported rather than copied: inline SVG only, numbered figures, a light page. The provenance line is
this page's own, since it names this tool and this page's review record. The four nets' architecture
drawings are draughtsman's and are not drawn here (Tony, 2026-09-19: hand-drawn copies in two reports
"will likely be completely incomparable").
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
from fair_comparison_evidence import LOW_F1, _refit_health  # noqa: E402

from bugarach import bench, provenance, score  # noqa: E402
from bugarach.time_axis import label as mmss  # noqa: E402
from bugarach.ui.app import TITLES  # noqa: E402

DEFAULT_RUN = REPO / "docs" / "learned" / "tuned_vs_coact" / "fair_comparison_2026_09_18"
DARKROOM_FOLDER = "2026-09-18-fair-comparison-run"

NETS = ("chorus_norm", "chorus_gain_norm", "line_length", "tube")
CHORUS = ("chorus_norm", "chorus_gain_norm")
CODED = ("coact", "sce", "loco", "cicada", "sync", "rate")
# The viewer's display names, with locust named: the public site withholds it as "sixth", and this
# page is not the site (the README names it too).
NAME = {**TITLES, "cicada": "locust", **{m: m for m in NETS}}
SEL = ("ungated", "gated")
SEL_NAME = {"ungated": "F1 alone", "gated": "F1 under the budget"}
NET_INK, CODED_INK, GREY = "#1b5fa8", "#111", "#8a8a8a"
PLANT_INK, REPL_INK, THR_INK = "#1b5fa8", "#c2410c", "#7a4fa3"
PART_INK = {0.3: "#1b5fa8", 0.18: "#5b8fd0", 0.1: "#b3cbea"}
REPLICATE_PAGE = "&lt;darkroom&gt;/bugarach/2026-09-18-replicate-run-status/"
ARCH_REPO = "docs/learned/comparison/comparison.svg"
GOAL_PAGE = "docs/goals/learned-model-family.md"


def claim(ok: bool, what: str) -> None:
    """A sentence about these data is printed only while it is true."""
    if not ok:
        raise SystemExit(f"a sentence on the page is no longer true of the data: {what}")


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
        self.bd = rd("breakdown.json")
        self.health, self.rhealth = _refit_health(self.results), self.repl["refits"]
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

    def selection(self, d, w, h):
        return json.loads((self.folder / "selections" / w / f"outer{h}" / f"{d}.json").read_text())

    def refused_all(self, d, w):
        out = []
        for h in self.folds:
            sel = self.selection(d, w, h)
            out.append(bool(sel["n_refused"]) and sel["n_refused"] >= sel["n_scored"])
        return out

    def start_over_budget(self, d):
        """Folds in which a coded search's starting point was itself outside the budget: its first
        move had to leave it (the run records such a move as rescued from inadmissible), or it could
        not, because the budget refused every configuration, the start included."""
        refused = self.refused_all(d, "gated")
        return [bool((self.selection(d, "gated", h)["moves"][:1] or [{}])[0]
                     .get("rescued_from_inadmissible")) or refused[h] for h in self.folds]

    def first_move(self, d, h):
        m = (self.selection(d, "gated", h)["moves"][:1] or [None])[0]
        return m

    def veto(self, d, w, shipped=False):
        got = {(c["outer_fold"], c["selection"]): c for c in self.crowded["choices"]
               if c["detector"] == d}
        key = "passes_veto_vs_shipped" if shipped else "passes_veto"
        return [got[(h, w)][key] for h in self.folds]

    def admissible(self, d, w):
        """The glossary's word: chosen within the budget, and passing the crowded-recording check."""
        return [v and not r for v, r in zip(self.veto(d, w), self.refused_all(d, w))]

    def cmp(self, a, b, w):
        """The run's own paired comparison (tools/tune_learned_vs_coact.py ``_paired``) where it
        computed one, which it did for every net against CoactDetect; a coded detector against
        CoactDetect is computed here by the same arithmetic (``stats``)."""
        got = self.results["comparisons"][w].get(f"{a} - {b}")
        if got is not None:
            return got
        return self.stats([x - y for x, y in zip(self.f1(a, w), self.f1(b, w))])

    def stats(self, d):
        """Paired statistics for a comparison the run did not compute itself (a matched merge gap, a
        set-aside refit): the same arithmetic as the run's ``_paired``."""
        d = np.asarray(d, float)
        sd = float(np.std(d, ddof=1))
        t = float(np.mean(d) / (sd / math.sqrt(len(d)))) if sd > 0 else float("nan")
        return dict(per_fold=list(d), mean=float(np.mean(d)), t=t, tc=t * self.nb,
                    ahead=int(np.sum(d > 0)), n=len(d))

    def coact_fold(self, w, repl=False):
        return self.repl["hand"]["coact"][w] if repl else self.coded_f1("coact", w)

    def margin(self, m, w, repl=False, without_low=False):
        """Per fold: the net's mean over its refits, minus CoactDetect; optionally with the refits
        under LOW_F1 set aside."""
        h = (self.rhealth if repl else self.health)[m][w]
        key = "mean_without_low" if without_low else "mean"
        return [x[key] - c for x, c in zip(h, self.coact_fold(w, repl))]

    def matched(self, m, w, gap):
        """Per fold: the net re-decoded at ``gap`` minus CoactDetect re-scored at ``gap``."""
        net = [r["f1_mean_by_gap"][f"{gap:g}"] for r in self.gap["nets"][m] if r["selection"] == w]
        co = [r["f1_by_gap"][f"{gap:g}"] for r in self.gap["coded"]["coact"] if r["selection"] == w]
        return [a - b for a, b in zip(net, co)]

    def tuning(self, m, w):
        return self.results["comparisons"][w][f"{m} tuned - untuned"]

    def over_budget_nets(self, m):
        return [row["gated"]["seeds_over_budget"] for row in self.results["learned"][m]]

    def low_refits(self, repl=False):
        """Every distinct refit under LOW_F1: (model, fold, seed, F1 by selection, flags)."""
        seen: dict = {}
        health = self.rhealth if repl else self.health
        for m in NETS:
            for w in ("untuned",) + SEL:
                for h, x in enumerate(health[m][w]):
                    for s in x["low"]:
                        e = seen.setdefault((m, h, s), dict(model=m, fold=h, seed=s, where={}))
                        e["where"][w] = dict(f1=x["f1"][x["seeds"].index(s)],
                                             failed=s in x["failed_signature"],
                                             no_calls=s in x["no_calls"])
        return list(seen.values())

    def lowest_other_refit(self, repl=False):
        health = self.rhealth if repl else self.health
        return min(f for m in NETS for w in ("untuned",) + SEL for x in health[m][w]
                   for f in x["f1"] if f >= LOW_F1)

    def n_stage(self, prefix):
        return sum(1 for x in self.ran if x["stage"].startswith(prefix))

    def coded_gap_curve(self, d, w="ungated"):
        rows = [r for r in self.gap["coded"][d] if r["selection"] == w]
        gaps = [float(g) for g in self.gap["coded_gaps_sec"]]
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
        fold_means = max(abs(r["f1_mean_by_gap"]["2"] - r["run_f1_mean"])
                         for m in self.gap["nets"] for r in self.gap["nets"][m])
        return coded, nets, fold_means

    def recall_at(self, side, w, background, frac):
        rows = (self.bd["detectors"] if side in CODED else self.bd["nets"])[side]
        return [r["by_background"][background]["recall_by_participation"][frac]
                for r in rows if r["selection"] == w]

    def recall10(self, side, w, background):
        return self.recall_at(side, w, background, "0.1")

    def f1_background(self, side, w, background):
        rows = (self.bd["detectors"] if side in CODED else self.bd["nets"])[side]
        return [r["f1_by_background"][background] for r in rows if r["selection"] == w]

    def wall_hours(self):
        a = time.mktime(time.strptime(self.meta["started"]["at"][:19], "%Y-%m-%dT%H:%M:%S"))
        progress = json.loads((self.folder / "progress.json").read_text())
        b = time.mktime(time.strptime(progress["at"][:19], "%Y-%m-%dT%H:%M:%S"))
        return (b - a) / 3600.0


def fold_label(h: int) -> str:
    return f"fold {h + 1}"


def seed_label(s: int) -> str:
    return f"training seed {s + 1} of 5"


@lru_cache(maxsize=1)
def crowded_spacing():
    """Planted-event spacing on the crowded recordings the check scores (seeds 1-12, both
    backgrounds), measured rather than quoted."""
    from search_all_settings import N_TAIL
    gaps, n, dur = [], set(), set()
    for s in range(1, N_TAIL + 1):
        for r in ("baseline_quiet", "baseline_busy"):
            sl, gt = bench.make_tail_recording(r, s)
            t = np.sort(gt.times)
            n.add(len(t))
            lo, hi = bench.recording_extent(sl)
            dur.add(round((hi - lo) / 3600.0, 1))
            gaps += list(np.diff(t))
    g = np.array(gaps)
    return dict(n_events=sorted(n), hours=sorted(dur), min=float(g.min()),
                median=float(np.median(g)), n_recordings=2 * N_TAIL)


# ---- small drawing helpers -----------------------------------------------------------------------

def tri_down(svg: Svg, x, y, s=6, fill=PLANT_INK, stroke="none", sw=1.2):
    svg.add(f'<path d="M{x - s:.1f} {y:.1f} L{x + s:.1f} {y:.1f} L{x:.1f} {y + s * 1.6:.1f} Z" '
            f'fill="{fill}" stroke="{stroke}" stroke-width="{sw}"/>')


def diamond(svg: Svg, x, y, s=4.5, fill=REPL_INK, stroke=REPL_INK):
    svg.add(f'<path d="M{x:.1f} {y - s:.1f} L{x + s:.1f} {y:.1f} L{x:.1f} {y + s:.1f} '
            f'L{x - s:.1f} {y:.1f} Z" fill="{fill}" stroke="{stroke}" stroke-width="1.4"/>')


def hatch(svg: Svg, xa, xb, y_top, y_bot, step=7, ink="#666"):
    for k in range(int((xb - xa) / step)):
        svg.line(xa + step * k, y_bot, xa + step * k + 5, y_top, stroke=ink)


def x_axis(svg: Svg, X, x0, x1, yb, ticks, fmt, name, zero_rule=False, top=None):
    svg.line(x0, yb, x1, yb)
    for v in ticks:
        if top is not None:
            svg.line(X(v), top, X(v), yb, stroke="#111" if (zero_rule and v == 0) else "#eee",
                     dash="4 3" if (zero_rule and v == 0) else None)
        svg.line(X(v), yb, X(v), yb + 4)
        svg.text(X(v), yb + 18, fmt(v), anchor="middle", size=11)
    svg.text((x0 + x1) / 2, yb + 36, name, anchor="middle", size=12)


def fmt_diff(v):
    return "0" if abs(v) < 1e-12 else f"{v:+.2f}".replace("-", "−")


def signed(v, nd=3):
    return f"{v:+.{nd}f}".replace("-", "−")


def tnum(v):
    return num(v, 1).replace("-", "−")


def and_join(items):
    items = list(items)
    return items[0] if len(items) == 1 else ", ".join(items[:-1]) + " and " + items[-1]


# ---- figures -------------------------------------------------------------------------------------

FIG1_SEED, FIG1_WINDOW = 1000, (940.0, 1560.0)


def problem_recording():
    sl, gt = bench.make_recording("baseline_busy", FIG1_SEED)
    trains = bench.stream_trains(sl.streams[bench.STREAM], bench.recording_extent(sl))
    t0, t1 = FIG1_WINDOW
    inside = [e for e in gt.events if t0 <= e.time <= t1]
    facts = dict(event_t=inside[0].time, event_frac=inside[0].frac, n_part=inside[0].n_part,
                 distractors=[e.time for e in gt.distractors if t0 <= e.time <= t1],
                 n_onsets=int(sum(len(t) for t in trains)))
    return sl, gt, trains, facts


def fig_problem() -> Svg:
    """Figure 1. The raster rules are bugarach.ui.diagnostic's: rows ranked by activity INSIDE the
    drawn window (stable, busiest on top), nothing drawn on the raster, cues in a lane above with
    down-pointing markers, planted filled and distractors hollow."""
    _, gt, trains, facts = problem_recording()
    dur = bench.BENCH_RECORDING["duration_sec"]
    svg = Svg(900, 700, "Panel A, the whole 45-minute recording as a lane of planted "
                        "events, distractors and the probe; panel B, a raster of 33 ROIs over ten "
                        "minutes of it, with the same lane above")
    x0, x1 = 170, 870
    # --- A: the whole recording ---
    svg.text(20, 20, "A.  The whole recording", size=13, weight="bold")
    XA = lambda t: x0 + t / dur * (x1 - x0)                  # noqa: E731
    svg.rect(XA(FIG1_WINDOW[0]), 32, XA(FIG1_WINDOW[1]) - XA(FIG1_WINDOW[0]), 72, fill="#efefef")
    for y, lab in ((46, "planted events"), (70, "distractors"), (94, "probe")):
        svg.text(x0 - 12, y, lab, anchor="end", size=12)
    for e in gt.events:
        tri_down(svg, XA(e.time), 36, 5.5, fill=PART_INK[round(e.frac, 2)], stroke="#1b3f73", sw=0.8)
    for e in gt.distractors:
        tri_down(svg, XA(e.time), 60, 5.5, fill="none", stroke=GREY, sw=1.4)
    hot = bench.BENCH_RECORDING["hot_window"]
    hatch(svg, XA(hot[0]), XA(hot[1]), 84, 98)
    svg.time_axis(x0, x1, 110, 0, dur, "time in the recording")
    lx = x0
    for f in (0.3, 0.18, 0.1):
        tri_down(svg, lx, 166, 5.5, fill=PART_INK[f], stroke="#1b3f73", sw=0.8)
        svg.text(lx + 10, 176, f"planted, {f:.0%} of ROIs", size=11)
        lx += 150
    tri_down(svg, lx, 166, 5.5, fill="none", stroke=GREY, sw=1.4)
    svg.text(lx + 10, 176, "distractor", size=11)
    svg.rect(lx + 100, 166, 18, 12, fill="#efefef")
    svg.text(lx + 124, 176, "the stretch panel B shows", size=11)
    # --- B: ten minutes, cell by cell ---
    t0, t1 = FIG1_WINDOW
    svg.text(20, 214, "B.  About ten minutes of it, cell by cell", size=13, weight="bold")
    counts = [int(np.sum((t >= t0) & (t <= t1))) for t in trains]
    order = np.argsort(counts, kind="stable")[::-1]
    X = lambda t: x0 + (t - t0) / (t1 - t0) * (x1 - x0)      # noqa: E731
    lane_top, ras_top, row_h = 228, 310, 10.0
    svg.text(x0 - 12, lane_top + 14, "planted event", anchor="end", size=12)
    svg.text(x0 - 12, lane_top + 36, "distractor", anchor="end", size=12)
    svg.text(x0 - 12, lane_top + 58, "probe", anchor="end", size=12)
    tri_down(svg, X(facts["event_t"]), lane_top + 4, 6, fill=PART_INK[round(facts["event_frac"], 2)],
             stroke="#1b3f73", sw=0.8)
    for t in facts["distractors"]:
        tri_down(svg, X(t), lane_top + 26, 6, fill="none", stroke=GREY, sw=1.5)
    hatch(svg, X(max(hot[0], t0)), X(min(hot[1], t1)), lane_top + 50, lane_top + 62)
    for row, i in enumerate(order):
        y = ras_top + row * row_h
        for t in trains[i]:
            if t0 <= t <= t1:
                svg.line(X(t), y + 3, X(t), y + 7, w=1.3)
    ras_bot = ras_top + len(order) * row_h
    for k, s in enumerate((f"{len(order)} ROIs,", "most active", "in this window", "on top")):
        svg.text(x0 - 12, (ras_top + ras_bot) / 2 + 15 * k, s, anchor="end", size=12)
    svg.time_axis(x0, x1, ras_bot + 8, t0, t1, "time in the recording")
    return svg


def fig_scoring() -> Svg:
    """How a call is scored, drawn from score.TOL_SEC and the one-to-one matching."""
    tol = score.TOL_SEC
    svg = Svg(900, 330, "Four rows showing how a detector's call is scored: a hit, a false "
                        "alarm, one call spanning two events, and a call inside the probe")
    x0, x1, s0, s1 = 250, 590, 0.0, 40.0
    X = lambda t: x0 + (t - s0) / (s1 - s0) * (x1 - x0)      # noqa: E731
    rows = (
        ("a hit", [20.0], (18.5, 21.5), None,
         ["the call's span, widened by", f"{tol:g} s each side, reaches the event"]),
        ("a false alarm", [], (26.0, 29.0), None,
         ["no planted event within reach:", "it counts against precision"]),
        ("one call over two events", [12.0, 26.0], (11.0, 27.0), None,
         ["it is matched to one event only;", "the other event is missed"]),
        ("a call in the probe", [], (18.0, 21.0), (5.0, 35.0),
         ["counted apart, as false alarms per", "hour, and left out of precision"]),
    )
    for k, (lab, events, (ca, cb), probe, note) in enumerate(rows):
        y = 40 + k * 66
        svg.text(x0 - 14, y + 22, lab, anchor="end", size=12, weight="bold")
        if probe:
            hatch(svg, X(probe[0]), X(probe[1]), y - 2, y + 10)
        for t in events:
            tri_down(svg, X(t), y, 5.5)
        svg.rect(X(ca), y + 17, X(cb) - X(ca), 6, fill="#111")
        svg.line(X(ca - tol), y + 30, X(cb + tol), y + 30, stroke=GREY, w=1.4)
        svg.line(X(ca - tol), y + 26, X(ca - tol), y + 34, stroke=GREY, w=1.4)
        svg.line(X(cb + tol), y + 26, X(cb + tol), y + 34, stroke=GREY, w=1.4)
        for j, s in enumerate(note):
            svg.text(x1 + 24, y + 18 + 15 * j, s, size=12, fill="#333")
    ly = 312
    tri_down(svg, 40, ly - 9, 5.5)
    svg.text(52, ly, "planted event", size=11)
    svg.rect(150, ly - 7, 26, 6, fill="#111")
    svg.text(182, ly, "a detector's call (its time span)", size=11)
    svg.line(390, ly - 4, 430, ly - 4, stroke=GREY, w=1.4)
    svg.line(390, ly - 8, 390, ly, stroke=GREY, w=1.4)
    svg.line(430, ly - 8, 430, ly, stroke=GREY, w=1.4)
    svg.text(436, ly, f"the span widened by {tol:g} s", size=11)
    hatch(svg, 610, 650, ly - 10, ly)
    svg.text(656, ly, "the probe (section 1)", size=11)
    return svg


def fig_nested(run: Run) -> Svg:
    n, spf = run.decl["folds"], run.decl["seeds_per_fold"]
    svg = Svg(900, 250, "Four outer folds of twelve recording seeds; for held-out fold 1, "
                        "a net rotates which training fold scores, and a coded detector scores on all "
                        "three at once")
    x0, cw, ch = 170, 90, 34
    svg.text(20, 22, "A.  Outer loop: which fold is scored", size=13, weight="bold")
    for h in range(n):
        y = 40 + h * (ch + 8)
        svg.text(x0 - 12, y + 22, f"held-out {fold_label(h)}", anchor="end", size=12)
        for f in range(n):
            held = f == h
            svg.rect(x0 + f * (cw + 4), y, cw, ch, fill="#333" if held else "#dfe7f2", stroke="#333")
            svg.text(x0 + f * (cw + 4) + cw / 2, y + 22, "scored once" if held else "chooses",
                     anchor="middle", size=12, fill="#fff" if held else "#111")
    for f in range(n):
        svg.text(x0 + f * (cw + 4) + cw / 2, 40 + n * (ch + 8) + 12,
                 f"{fold_label(f)}: {spf} seeds", anchor="middle", size=11, fill="#333")
    bx, bw = 670, 70
    svg.text(560, 22, "B.  Inside held-out fold 1", size=13, weight="bold")
    for j, scored in enumerate((1, 2, 3)):
        y = 40 + j * (ch + 8)
        svg.text(bx - 10, y + 22, f"net, rotation {j + 1}", anchor="end", size=12)
        for f in range(1, n):
            is_scored = f == scored
            svg.rect(bx + (f - 1) * (bw + 4), y, bw, ch, fill="#8fb1d8" if is_scored else "#dfe7f2",
                     stroke="#333")
            svg.text(bx + (f - 1) * (bw + 4) + bw / 2, y + 22, "scores" if is_scored else "fits",
                     anchor="middle", size=12)
    y = 40 + 3 * (ch + 8)
    svg.text(bx - 10, y + 22, "coded detector", anchor="end", size=12)
    svg.rect(bx, y, 3 * bw + 8, ch, fill="#eeeeee", stroke="#333")
    svg.text(bx + (3 * bw + 8) / 2, y + 22, "scores every candidate", anchor="middle", size=12)
    for f in range(1, n):
        svg.text(bx + (f - 1) * (bw + 4) + bw / 2, y + ch + 16, fold_label(f), anchor="middle",
                 size=11, fill="#333")
    return svg


def fig_defect(run: Run) -> Svg:
    d = run.draws
    seeds = sorted(int(s) for s in d["fold_of"])
    fold_of = {int(k): v for k, v in d["fold_of"].items()}
    spf = run.decl["seeds_per_fold"]
    svg = Svg(900, 450, "For each held-out fold, the ten training recordings fitted at the "
                        "first training seed, before the fix and as this run drew them")
    x0, x1 = 200, 880
    cell = (x1 - x0) / len(seeds)

    def strip(y, h, info, label):
        svg.text(x0 - 12, y + 12, label, anchor="end", size=12)
        fitted = {int(r.split(":")[1]) for r in info["fitted"]}
        thr = {int(r.split(":")[1]) for r in info["threshold"]}
        for k, s in enumerate(seeds):
            fill = ("#333" if fold_of[s] == h else NET_INK if s in fitted
                    else THR_INK if s in thr else "#e6e6e6")
            svg.rect(x0 + k * cell, y, cell - 1, 16, fill=fill)

    for panel, (key, title) in enumerate((("before_fix", "A.  Before the fix: consecutive order"),
                                          ("as_run", "B.  As this run drew them: dealt across folds"))):
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
    for ink, lab in ((NET_INK, "fitted"), (THR_INK, "picks the threshold"), ("#333", "held out"),
                     ("#e6e6e6", "not used at this seed")):
        svg.rect(lx, 426, 12, 12, fill=ink, stroke="#999")
        svg.text(lx + 18, 436, lab, size=12)
        lx += 180
    return svg


MODE_TICKS = (9.55, 9.70, 9.90, 10.05, 10.20, 10.40)
MODE_SHIFT, MODE_NEED, MODE_WIN = 0.45, 5, 1.0


def fig_modes() -> Svg:
    """Binned against sliding counting, a schematic. The counts are computed from the tick
    positions drawn, not typed."""
    svg = Svg(900, 336, "Six ROIs firing within a second, counted in fixed one-second bins and in a "
                        "sliding one-second window, as recorded and shifted 0.45 s later")
    x0, x1, t0, t1 = 220, 700, 8.0, 12.0
    X = lambda t: x0 + (t - t0) / (t1 - t0) * (x1 - x0)      # noqa: E731
    for k, (title, shift) in enumerate((("A.  As recorded", 0.0),
                                        (f"B.  The same firings, {MODE_SHIFT:g} s later", MODE_SHIFT))):
        top = 22 + k * 132
        svg.text(20, top, title, size=13, weight="bold")
        ticks = [t + shift for t in MODE_TICKS]
        y = top + 14
        svg.text(x0 - 12, y + 16, "six ROIs firing", anchor="end", size=12)
        for j, t in enumerate(ticks):
            svg.line(X(t), y + 2 + j * 4, X(t), y + 12 + j * 4, w=1.6)
        # binned: fixed bins, one count each
        yb = y + 44
        svg.text(x0 - 12, yb + 13, "binned: fixed bins", anchor="end", size=12)
        counts = {}
        for b in range(int(t0), int(t1)):
            n = sum(1 for t in ticks if b <= t < b + 1)
            counts[b] = n
            svg.rect(X(b), yb, X(b + 1) - X(b) - 2, 18, fill="#f3f3f3", stroke="#999")
            svg.text((X(b) + X(b + 1)) / 2, yb + 13, str(n), anchor="middle", size=12)
        best_bin = max(counts.values())
        # sliding: the densest one-second window
        ys = yb + 30
        svg.text(x0 - 12, ys + 13, "sliding: moving window", anchor="end", size=12)
        best = max(((a, sum(1 for t in ticks if a <= t < a + MODE_WIN)) for a in ticks),
                   key=lambda p: p[1])
        svg.rect(X(best[0]), ys, X(best[0] + MODE_WIN) - X(best[0]), 18, fill="#e3ecf7", stroke=NET_INK)
        svg.text(X(best[0] + MODE_WIN / 2), ys + 13, str(best[1]), anchor="middle", size=12)
        ok_b, ok_s = best_bin >= MODE_NEED, best[1] >= MODE_NEED
        svg.text(x1 + 20, yb + 13, f"most in a bin: {best_bin} firings, "
                 + ("a call" if ok_b else "no call"), size=12, fill="#060" if ok_b else "#b00")
        svg.text(x1 + 20, ys + 13, f"most in a window: {best[1]} firings, "
                 + ("a call" if ok_s else "no call"), size=12, fill="#060" if ok_s else "#b00")
    svg.time_axis(x0, x1, 290, t0, t1, "time (a schematic)")
    return svg


def fig_budget(run: Run) -> Svg:
    svg = Svg(900, 330, "A schematic of the two selections: the best F1 anywhere, and the "
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
    svg.text(X(budget) + 10, y1 - 10, f"more than {run.decl['budget_margin']:g} times the "
                                      "reference's rate", size=12, fill="#555")
    far = [i for i in range(len(fa)) if abs(fa[i] - ref_fa) > 0.05 or abs(f1[i] - ref_f1) > 0.05]
    for i in far:
        svg.circle(X(fa[i]), Y(f1[i]), 4, fill="#777")
    ung = max(far, key=lambda i: f1[i])
    gat = max([i for i in far if fa[i] <= budget - 0.02], key=lambda i: f1[i])
    # Squares, not rings: a ring elsewhere on the page marks a fold holding a failed refit.
    svg.rect(X(fa[ung]) - 7, Y(f1[ung]) - 7, 14, 14, fill="none", stroke="#111", sw=1.4)
    svg.text(X(fa[ung]) - 12, Y(f1[ung]) + 4, "chosen on F1 alone", anchor="end", size=12)
    svg.rect(X(fa[gat]) - 7, Y(f1[gat]) - 7, 14, 14, fill="none", stroke=NET_INK, sw=1.4)
    svg.text(X(fa[gat]) - 12, Y(f1[gat]) - 10, "chosen under the budget", anchor="end", size=12,
             fill=NET_INK)
    svg.add(f'<path d="M{X(ref_fa) - 6:.1f} {Y(ref_f1) - 6:.1f} h12 v12 h-12 Z" fill="{CODED_INK}"/>')
    svg.text(X(ref_fa) - 10, Y(ref_f1) + 22, "reference CoactDetect", anchor="middle", size=12)
    return svg


def fig_results(run: Run) -> Svg:
    names = list(NETS) + list(CODED)
    svg = Svg(900, 560, "Held-out F1 per outer fold, one row per contestant, panel A for "
                        "choices on F1 alone and panel B under the budget")
    lo, hi = 0.2, 0.85
    panels = ((170, 510, "ungated", "A"), (560, 890, "gated", "B"))
    top, row = 58, 38
    for x0, x1, w, letter in panels:
        X = lambda v, a=x0, b=x1: a + (v - lo) / (hi - lo) * (b - a)   # noqa: E731
        svg.text((x0 + x1) / 2, 22, f"{letter}.  {SEL_NAME[w]}", anchor="middle", size=13,
                 weight="bold")
        yb = top + len(names) * row
        x_axis(svg, X, x0, x1, yb, (0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8), lambda v: f"{v:.1f}",
               "held-out F1", top=top - 6)
        for i, m in enumerate(names):
            y = top + i * row + row / 2
            vals = run.f1(m, w)
            ink = NET_INK if m in NETS else CODED_INK
            if m in CODED:
                veto, refused = run.veto(m, w), run.refused_all(m, w)
            else:
                veto, refused = [True] * 4, [False] * 4
            for k, v in enumerate(vals):
                assert lo <= v <= hi, f"{m} {w}: {v} is off the axis; widen it"
                if refused[k]:
                    s, yk = 3, y + (k - 1.5) * 8.0     # the × marks need more room than dots
                    svg.line(X(v) - s, yk - s, X(v) + s, yk + s, stroke=ink, w=1.6)
                    svg.line(X(v) - s, yk + s, X(v) + s, yk - s, stroke=ink, w=1.6)
                else:
                    yk = y + (k - 1.5) * 4.5          # each fold on its own line: no two can fuse
                    svg.circle(X(v), yk, 3.6, fill=ink if veto[k] else "#fff", stroke=ink)
                    if m in NETS and low_folds(run, m, w)[k]:
                        svg.circle(X(v), yk, 7.5, fill="none", stroke=ink)
            if not all(refused):                      # a row the budget refused has no result
                mean = float(np.mean(vals))
                svg.line(X(mean), y - 12, X(mean), y + 12, stroke=ink, w=2.2)
    for i, m in enumerate(names):
        y = top + i * row + row / 2
        svg.text(160, y + 4, NAME[m], anchor="end", size=12,
                 fill=NET_INK if m in NETS else CODED_INK, weight="bold" if m == "coact" else "normal")
    svg.line(20, top + len(NETS) * row, 890, top + len(NETS) * row, stroke="#bbb", dash="3 3")
    svg.text(20, top + len(NETS) * row - 6, "nets", size=11, fill=NET_INK)
    svg.text(20, top + len(NETS) * row + 14, "coded", size=11)
    ly = 540
    svg.circle(30, ly, 3.6, fill=CODED_INK)
    svg.text(40, ly + 4, "one outer fold", size=12)
    svg.line(150, ly - 8, 150, ly + 8, w=2.2, stroke=NET_INK)
    svg.line(156, ly - 8, 156, ly + 8, w=2.2)
    svg.text(164, ly + 4, "mean of 4 folds", size=12)
    svg.circle(290, ly, 3.6, fill="#fff", stroke=CODED_INK)
    svg.text(300, ly + 4, "fails the crowded-recording check (section 4.5)", size=12)
    svg.line(606, ly - 4, 614, ly + 4, stroke=CODED_INK, w=1.6)
    svg.line(606, ly + 4, 614, ly - 4, stroke=CODED_INK, w=1.6)
    svg.text(620, ly + 4, "the budget refused every configuration tried", size=12)
    return svg


def fig_margins(run: Run) -> Svg:
    """Net minus CoactDetect per fold, this run and the replicate, with refits under LOW_F1 set aside
    everywhere; a fold that held one is ringed. Drawing the with-failure value too, joined to the
    set-aside one, read as a confidence interval (round 3, role 8), so it is given in the text."""
    rows = [(m, w) for m in NETS for w in SEL]
    rh, top = 46, 36
    yb = top + len(rows) * rh
    svg = Svg(900, yb + 110, "Each net minus CoactDetect in held-out F1, per outer fold, in this run "
                             "and in the replicate, refits that failed to train set aside")
    vals = [v for m, w in rows for rep in (False, True) for v in run.margin(m, w, rep, True)]
    lo = math.floor(min(vals) / 0.05) * 0.05 - 0.01
    hi = max(0.05, math.ceil(max(vals) / 0.05) * 0.05)
    x0, x1 = 310, 880
    X = lambda v: x0 + (v - lo) / (hi - lo) * (x1 - x0)   # noqa: E731
    ticks = [round(v, 2) for v in np.arange(math.ceil(lo / 0.05) * 0.05, hi + 1e-9, 0.05)]
    x_axis(svg, X, x0, x1, yb, ticks, fmt_diff,
           "net minus CoactDetect, held-out F1 (right of 0: the net is ahead)", zero_rule=True,
           top=top - 6)
    for i, (m, w) in enumerate(rows):
        yc = top + i * rh + rh / 2
        svg.text(x0 - 10, yc + 4, f"{m}, {SEL_NAME[w]}", anchor="end", size=12)
        if i % 2 == 0 and i:
            svg.line(20, top + i * rh, x1, top + i * rh, stroke="#ddd")
        for rep, dy, ink in ((False, -9, NET_INK), (True, 9, REPL_INK)):
            full, kept = run.margin(m, w, rep), run.margin(m, w, rep, True)
            for k, (a, b) in enumerate(zip(full, kept)):
                y = yc + dy + (k - 1.5) * 2.6
                (svg.circle(X(b), y, 3.6, fill=ink) if not rep else diamond(svg, X(b), y, 4.2))
                if abs(a - b) > 1e-12:
                    svg.circle(X(b), y, 7.5, fill="none", stroke=ink)
            mean = float(np.mean(kept))
            svg.line(X(mean), yc + dy - 7, X(mean), yc + dy + 7, stroke=ink, w=2.4)
    ly = yb + 62
    svg.circle(30, ly, 3.6, fill=NET_INK)
    svg.text(40, ly + 4, "this run, one outer fold", size=12)
    diamond(svg, 212, ly, 4.2)
    svg.text(222, ly + 4, "the replicate, one outer fold", size=12)
    svg.line(410, ly - 7, 410, ly + 7, stroke=NET_INK, w=2.4)
    svg.line(416, ly - 7, 416, ly + 7, stroke=REPL_INK, w=2.4)
    svg.text(424, ly + 4, "mean of 4 folds", size=12)
    svg.circle(560, ly, 3.6, fill=NET_INK)
    svg.circle(560, ly, 7.5, fill="none", stroke=NET_INK)
    svg.text(574, ly + 4, f"a fold that held a refit below {LOW_F1:g} F1, set aside", size=12)
    return svg


def fig_merging() -> Svg:
    """Merging, as a schematic, with calls drawn as spans (as in the scoring figure)."""
    svg = Svg(900, 200, "A schematic of merging calls: two events far apart keep a merged call each; "
                        "three events a few seconds apart fuse into one call")
    base = 290
    for r, (label, sub, events, merged, note) in enumerate((
            ("far apart", "(this bench: at least 120 s)", [60, 330], [(50, 72), (320, 342)],
             "two merged calls, two events: both hit"),
            ("close", "(a few seconds apart)", [60, 100, 140], [(50, 152)],
             "one merged call, three events: one hit, two missed"))):
        y = 24 + r * 70
        svg.text(base - 20, y + 16, label, anchor="end", size=12, weight="bold")
        svg.text(base - 20, y + 31, sub, anchor="end", size=11)
        for t in events:
            tri_down(svg, base + t, y, 5)
            for off in (-8, -1, 6):
                svg.rect(base + t + off, y + 14, 5, 4, fill="#111")
        for a, b in merged:
            svg.rect(base + a, y + 24, b - a, 6, fill="#999")
        svg.text(base + max(b for _, b in merged) + 16, y + 30, note, size=11, fill="#333")
    ly = 180
    tri_down(svg, 40, ly - 9, 5)
    svg.text(52, ly, "planted event", size=11)
    svg.rect(150, ly - 6, 5, 4, fill="#111")
    svg.text(162, ly, "raw call (a short span)", size=11)
    svg.rect(310, ly - 7, 26, 6, fill="#999")
    svg.text(342, ly, "call after merging", size=11)
    return svg


def fig_gap_curves(run: Run) -> Svg:
    """Held-out F1 against the merge gap for both sides, from merge_gap.json (only the merge gap
    changed). The gaps tried double from 2 s, so the axis is logarithmic, with 0 s set apart."""
    svg = Svg(900, 380, "Held-out F1 against the merge gap, logarithmic axis with 0 s set apart, for "
                        "three coded detectors and the four nets, choices on F1 alone")
    top, bot, x0, x1 = 30, 290, 120, 620
    gaps = [float(g) for g in run.gap["coded_gaps_sec"]]
    lo_g, hi_g = min(g for g in gaps if g > 0), max(gaps)
    X = lambda g: (x0 if g == 0 else                                    # noqa: E731
                   x0 + 50 + math.log2(g / lo_g) / math.log2(hi_g / lo_g) * (x1 - x0 - 50))
    curves = []
    for d, (ink, dash, w) in {"coact": (CODED_INK, None, 2.4), "sce": (GREY, "7 4", 1.8),
                              "loco": (GREY, "2 3", 1.8)}.items():
        gs, vals, chosen = run.coded_gap_curve(d)
        curves.append((d, ink, dash, w, [(g, float(np.mean(vals[g]))) for g in gs],
                       sorted(set(chosen))))
    for m, (dash, w) in {"chorus_norm": (None, 2.4), "chorus_gain_norm": (None, 1.2),
                         "line_length": ("7 4", 1.4), "tube": ("2 3", 1.6)}.items():
        gs, vals = run.net_gap_curve(m)
        curves.append((m, NET_INK, dash, w, [(g, float(np.mean(vals[g]))) for g in gs], []))
    allv = [v for c in curves for _, v in c[4]]
    lo, hi = math.floor(min(allv) * 20) / 20, math.ceil(max(allv) * 20) / 20
    Y = lambda v: bot - (v - lo) / (hi - lo) * (bot - top)            # noqa: E731
    xb = (x0 + X(lo_g)) / 2                      # the break between 0 s and the doubling gaps
    svg.line(x0, bot, xb - 4, bot)
    svg.line(xb + 4, bot, x1, bot)
    svg.line(xb - 7, bot + 5, xb - 1, bot - 5)
    svg.line(xb + 1, bot + 5, xb + 7, bot - 5)
    svg.line(x0, top, x0, bot)
    for g in gaps:
        svg.line(X(g), bot, X(g), bot + 4)
        svg.text(X(g), bot + 18, f"{g:g} s", anchor="middle", size=11)
    svg.text((x0 + x1) / 2, bot + 36, "merge gap: calls closer than this become one (logarithmic; "
                                      "0 s set apart)", anchor="middle", size=12)
    for v in np.arange(lo, hi + 1e-9, 0.05):
        svg.line(x0 - 4, Y(v), x0, Y(v))
        svg.line(x0, Y(v), x1, Y(v), stroke="#eee")
        svg.text(x0 - 8, Y(v) + 4, f"{v:.2f}", anchor="end", size=11)
    svg.add(f'<text x="64" y="{(top + bot) / 2}" font-size="12" transform="rotate(-90 64 '
            f'{(top + bot) / 2})" text-anchor="middle">held-out F1</text>')
    svg.line(X(2.0), top, X(2.0), bot, stroke=NET_INK, w=0.8, dash="2 3")
    svg.text(X(2.0) + 4, top + 10, "every net ran at 2 s", size=11, fill=NET_INK)
    for name, ink, dash, w, pts, chosen in curves:
        for (ga, va), (gb, vb) in zip(pts, pts[1:]):
            if ga == 0:     # across the axis break: the curve's own style, faded (a dotted
                d = f' stroke-dasharray="{dash}"' if dash else ""      # bridge read as LoCo)
                svg.add(f'<line x1="{X(ga):.1f}" y1="{Y(va):.1f}" x2="{X(gb):.1f}" '
                        f'y2="{Y(vb):.1f}" stroke="{ink}" stroke-width="{w}" '
                        f'stroke-opacity="0.35"{d}/>')
            else:
                svg.line(X(ga), Y(va), X(gb), Y(vb), stroke=ink, w=w, dash=dash)
        for g, v in pts:
            if name in NETS:
                svg.circle(X(g), Y(v), 2.4, fill=ink)
        if name in ("coact", "sce"):              # the two detectors the text reads
            for g in chosen:
                svg.circle(X(g), Y(dict(pts)[g]), 6, fill="none", stroke=ink)
    # A key, not direct labels: the curves end at different gaps (16 s for the nets, 30 s for the
    # coded detectors), and leader lines from both ends crossed (round 3, role 10).
    lx, ly = x1 + 30, top + 8
    for name, ink, dash, w, _, _ in curves:
        svg.line(lx, ly, lx + 34, ly, stroke=ink, w=w, dash=dash)
        svg.text(lx + 42, ly + 4, NAME[name], size=12, fill=ink)
        ly += 20
    svg.circle(lx + 17, ly + 6, 6, fill="none", stroke="#111")
    svg.text(lx + 42, ly + 10, "the gap chosen", size=12)
    svg.text(lx + 42, ly + 26, "(CoactDetect, binned SCE)", size=11)
    return svg


MATCH_CASES = (("as run (2 s against 8 s)", None), ("both at 2 s", 2.0), ("both at 4 s", 4.0),
               ("both at 8 s", 8.0), ("both at 16 s", 16.0))


def low_folds(run: Run, m, w):
    """Folds of this run in which a net's choice holds a refit under LOW_F1."""
    return [bool(x["low"]) for x in run.health[m][w]]


def fold_key(svg: Svg, y, ink=NET_INK, ring=True, zero=True):
    """The key the per-fold dot figures share: one fold, the mean, the ring, the zero line."""
    svg.circle(30, y, 3.4, fill=ink)
    svg.text(40, y + 4, "one outer fold", size=12)
    svg.line(150, y - 8, 150, y + 8, stroke=ink, w=2.4)
    svg.text(158, y + 4, "mean of 4 folds", size=12)
    x = 290
    if ring:
        svg.circle(x, y, 3.4, fill=ink)
        svg.circle(x, y, 7.5, fill="none", stroke=ink)
        svg.text(x + 14, y + 4, f"a fold holding a refit below {LOW_F1:g} F1 (section 6), counted",
                 size=12)
        x += 400
    if zero:
        svg.line(x, y - 8, x, y + 8, dash="4 3")
        svg.text(x + 8, y + 4, "0: a tie", size=12)


def matched_case(run: Run, m, w, gap):
    if gap is None:
        return list(run.cmp(m, "coact", w)["per_fold"])
    return run.matched(m, w, gap)


def fig_matched(run: Run) -> Svg:
    """The two chorus nets minus CoactDetect with the merge gap matched, per fold, for both
    selections; every refit counted, and a fold holding a failed one ringed."""
    rows = [(m, lab, g) for m in CHORUS for lab, g in MATCH_CASES]
    top, rh = 50, 28
    yb = top + len(rows) * rh
    svg = Svg(900, yb + 100, "The two chorus nets minus CoactDetect per outer fold, with the merge gap "
                             "as run and matched at 2, 4, 8 and 16 s, for each selection")
    vals = [v for m, _, g in rows for w in SEL for v in matched_case(run, m, w, g)]
    lo = math.floor(min(vals) / 0.05) * 0.05
    hi = max(0.05, math.ceil(max(vals) / 0.05) * 0.05)
    ticks = [round(v, 2) for v in np.arange(lo, hi + 1e-9, 0.05)]
    for (x0, x1), w, letter in (((300, 560), "ungated", "A"), ((620, 870), "gated", "B")):
        X = lambda v, a=x0, b=x1: a + (v - lo) / (hi - lo) * (b - a)   # noqa: E731
        svg.text((x0 + x1) / 2, 24, f"{letter}.  {SEL_NAME[w]}", anchor="middle", size=13,
                 weight="bold")
        x_axis(svg, X, x0, x1, yb, ticks, fmt_diff, "net minus CoactDetect, held-out F1",
               zero_rule=True, top=top - 6)
        for i, (m, lab, g) in enumerate(rows):
            yc = top + i * rh + rh / 2
            d = matched_case(run, m, w, g)
            ringed = low_folds(run, m, w)
            for k, v in enumerate(d):
                svg.circle(X(v), yc + (k - 1.5) * 3.2, 3.4, fill=NET_INK)
                if ringed[k]:
                    svg.circle(X(v), yc + (k - 1.5) * 3.2, 7.5, fill="none", stroke=NET_INK)
            svg.line(X(float(np.mean(d))), yc - 10, X(float(np.mean(d))), yc + 10, stroke=NET_INK,
                     w=2.4)
    for i, (m, lab, g) in enumerate(rows):
        yc = top + i * rh + rh / 2
        svg.text(290, yc + 4, f"{m}, {lab}", anchor="end", size=12)
        if i and i % len(MATCH_CASES) == 0:
            svg.line(20, top + i * rh, 890, top + i * rh, stroke="#bbb", dash="3 3")
    fold_key(svg, yb + 72)
    return svg


def fig_breakdown(run: Run) -> Svg:
    """Recall of the planted events at each participation level, by background, per fold; the
    choices on F1 alone. Two levels sit at the ceiling for both sides, which is the point."""
    sides = CHORUS + ("coact",)
    rows = [(s, b) for b in ("quiet", "busy") for s in sides]
    top, rh = 50, 30
    yb = top + len(rows) * rh
    svg = Svg(900, yb + 100, "The share of planted events found at each participation level, per outer "
                            "fold, for CoactDetect and the two chorus nets at each background, choices "
                            "on F1 alone")
    for (x0, x1), frac, letter in (((270, 460), "0.3", "A"), ((490, 680), "0.18", "B"),
                                   ((710, 890), "0.1", "C")):
        X = lambda v, a=x0, b=x1: a + v * (b - a)            # noqa: E731
        svg.text((x0 + x1) / 2, 24, f"{letter}.  events joined by {float(frac):.0%}", anchor="middle",
                 size=13, weight="bold")
        x_axis(svg, X, x0, x1, yb, (0.0, 0.5, 1.0), lambda v: f"{v:.1f}", "recall", top=top - 6)
        for i, (s, b) in enumerate(rows):
            yc = top + i * rh + rh / 2
            ink = CODED_INK if s in CODED else NET_INK
            d = run.recall_at(s, "ungated", b, frac)
            ringed = low_folds(run, s, "ungated") if s in NETS else [False] * len(d)
            for k, v in enumerate(d):
                svg.circle(X(v), yc + (k - 1.5) * 3.2, 3.2, fill=ink)
                if ringed[k]:
                    svg.circle(X(v), yc + (k - 1.5) * 3.2, 7.5, fill="none", stroke=ink)
            svg.line(X(float(np.mean(d))), yc - 10, X(float(np.mean(d))), yc + 10, stroke=ink, w=2.4)
    for i, (s, b) in enumerate(rows):
        yc = top + i * rh + rh / 2
        svg.text(260, yc + 4, f"{NAME[s]}, {b} background", anchor="end", size=12,
                 fill=CODED_INK if s in CODED else NET_INK)
        if i == len(sides):
            svg.line(20, top + i * rh, 890, top + i * rh, stroke="#bbb", dash="3 3")
    fold_key(svg, yb + 72, ring=False, zero=False)
    svg.circle(330, yb + 72, 3.4, fill=CODED_INK)
    svg.text(340, yb + 76, "black: CoactDetect; blue: the chorus nets, pooled over 5 refits", size=12)
    return svg


def fig_crowded(run: Run) -> Svg:
    """Each coded choice on the crowded recordings, against the two references and the tolerance."""
    rows = [(d, w) for d in CODED for w in SEL]
    top, rh = 30, 28
    yb = top + len(rows) * rh
    svg = Svg(900, yb + 100, "Each coded detector's four fold choices scored on the crowded "
                             "recordings, against the setting each search started from and the "
                             "shipped setting, with the tolerance band")
    drop = run.crowded["max_crowded_drop"]
    ref, shipped = run.crowded["reference"], run.crowded["shipped_reference"]
    vals = [c["crowded_mean_f1"] for c in run.crowded["choices"]] + \
        [ref[d]["crowded_mean_f1"] - drop for d in CODED] + [shipped[d]["crowded_mean_f1"] for d in CODED]
    lo, hi = math.floor(min(vals) * 10) / 10, math.ceil(max(vals) * 10) / 10
    x0, x1 = 290, 870
    X = lambda v: x0 + (v - lo) / (hi - lo) * (x1 - x0)   # noqa: E731
    x_axis(svg, X, x0, x1, yb, [round(v, 1) for v in np.arange(lo, hi + 1e-9, 0.1)],
           lambda v: f"{v:.1f}", "mean F1 on the crowded recordings", top=top - 6)
    for i, (d, w) in enumerate(rows):
        yc = top + i * rh + rh / 2
        svg.text(x0 - 10, yc + 4, f"{NAME[d]}, {SEL_NAME[w]}", anchor="end", size=12)
        r0 = ref[d]["crowded_mean_f1"]
        svg.rect(X(r0 - drop), yc - 11, X(r0) - X(r0 - drop), 22, fill="#e8e8e8")
        svg.line(X(r0), yc - 11, X(r0), yc + 11, w=2.0)
        rs = shipped[d]["crowded_mean_f1"]
        svg.line(X(rs), yc - 11, X(rs), yc + 11, stroke=GREY, w=2.0, dash="3 2")
        got = sorted((c["outer_fold"], c["crowded_mean_f1"], c["passes_veto"])
                     for c in run.crowded["choices"] if c["detector"] == d and c["selection"] == w)
        refused = run.refused_all(d, w) if w == "gated" else [False] * len(got)
        for k, (h, v, ok) in enumerate(got):
            yk = yc + (k - 1.5) * (6.0 if refused[h] else 3.4)
            if refused[h]:                        # the budget refused it: no result to check
                svg.line(X(v) - 3, yk - 3, X(v) + 3, yk + 3, w=1.6)
                svg.line(X(v) - 3, yk + 3, X(v) + 3, yk - 3, w=1.6)
            else:
                svg.circle(X(v), yk, 3.4, fill=CODED_INK if ok else "#fff", stroke=CODED_INK)
        if i % 2 == 0 and i:
            svg.line(20, top + i * rh, x1, top + i * rh, stroke="#eee")
    ly = yb + 62
    svg.line(30, ly - 8, 30, ly + 8, w=2.0)
    svg.text(38, ly + 4, "the setting the search started from", size=12)
    svg.line(270, ly - 8, 270, ly + 8, stroke=GREY, w=2.0, dash="3 2")
    svg.text(278, ly + 4, "the shipped setting", size=12)
    svg.rect(410, ly - 8, 22, 16, fill="#e8e8e8")
    svg.text(438, ly + 4, f"within {drop:g} F1 below the starting setting", size=12)
    svg.circle(690, ly, 3.4, fill=CODED_INK)
    svg.circle(704, ly, 3.4, fill="#fff", stroke=CODED_INK)
    svg.text(714, ly + 4, "one fold's choice: passes, fails", size=12)
    svg.line(687, ly + 21, 693, ly + 27, w=1.6)
    svg.line(687, ly + 27, 693, ly + 21, w=1.6)
    svg.text(714, ly + 28, "all refused by the budget", size=12)
    return svg


def fig_tuning(run: Run) -> Svg:
    rows = [(m, w) for m in NETS for w in SEL]
    top, rh = 30, 30
    yb = top + len(rows) * rh
    svg = Svg(900, yb + 100, "Tuned minus untuned held-out F1 per outer fold, for each net and "
                             "selection")
    vals = [v for m, w in rows for v in run.tuning(m, w)["per_fold"]]
    lo = math.floor(min(vals) / 0.05) * 0.05
    hi = max(0.05, math.ceil(max(vals) / 0.05) * 0.05)
    x0, x1 = 310, 880
    X = lambda v: x0 + (v - lo) / (hi - lo) * (x1 - x0)   # noqa: E731
    x_axis(svg, X, x0, x1, yb, [round(v, 2) for v in np.arange(lo, hi + 1e-9, 0.05)], fmt_diff,
           "tuned minus untuned, held-out F1 (right of 0: tuning helped)", zero_rule=True, top=top - 6)
    for i, (m, w) in enumerate(rows):
        yc = top + i * rh + rh / 2
        svg.text(x0 - 10, yc + 4, f"{m}, {SEL_NAME[w]}", anchor="end", size=12)
        c = run.tuning(m, w)
        ringed = [a or b for a, b in zip(low_folds(run, m, w), low_folds(run, m, "untuned"))]
        for k, v in enumerate(c["per_fold"]):
            svg.circle(X(v), yc + (k - 1.5) * 3.2, 3.4, fill=NET_INK)
            if ringed[k]:
                svg.circle(X(v), yc + (k - 1.5) * 3.2, 7.5, fill="none", stroke=NET_INK)
        svg.line(X(c["mean"]), yc - 10, X(c["mean"]), yc + 10, stroke=NET_INK, w=2.4)
    fold_key(svg, yb + 72)
    return svg


# ---- tables --------------------------------------------------------------------------------------

def tcap(n: int, text: str) -> str:
    return f'<p class=tcap><b>Table {n}.</b> {text}</p>'


CODED_WHAT = {
    "coact": ("counts distinct ROIs firing together in a sliding window and asks how unlikely that "
              "count is against copies of the same stretch with each ROI's firings shifted in time "
              "(its local context, with a guard of a second or so next to the moment tested left "
              "out)",
              "designed here, independently. Excess-coincidence testing (Grün, Diesmann and "
              "Aertsen 2002, Neural Computation 14:43–80 and, for sliding windows, 14:81–119) "
              "against whole-train time shifts, whose nearest published forms are Pipa and "
              "colleagues 2008 (J Comput Neurosci 25:64–88) and the per-cell circular shift of Bocchio "
              "and colleagues 2020 (Nat Commun 11:4559) and Dard and colleagues 2022 (eLife "
              "11:e78116). The local context matches the cell-averaging structure credited under "
              "rate+context; the guard is later practice in that structure (Rohling 1983, IEEE "
              "Trans Aerosp Electron Syst 19:608–621)"),
    "loco": ("counts ROIs active together in a sliding window and compares the count with a high "
             "percentile of the same count on copies with each ROI's firings shifted in time",
             "designed here, independently; excess-coincidence testing, as CoactDetect"),
    "rate": ("compares the population's firing rate with its own slower average over the "
             "surrounding stretch",
             "designed here, independently, and later found to match the cell-averaging structure "
             "of radar detection (Finn and Johnson 1968, RCA Review 29:414–464): the average of the "
             "surrounding stretch serves as the local baseline"),
    "sce": ("counts ROIs active in fixed time bins (synchronous calcium events, SCE) and thresholds "
            "the count against copies with each ROI's firings shifted in time, wrapping around",
            "descends from Cossart, Aronov and Yuste 2003 (Nature 423:283–288), which resampled by "
            "interval reshuffling at P < 0.05 and credits the technique to Mao and colleagues 2001 "
            "(not obtained here). The circular-shift null is the Cossart lab's later practice "
            "(Bocchio and colleagues 2020; Dard and colleagues 2022); the settings tuned here are "
            "not the 2003 rule"),
    "sync": ("measures how closely ROIs' firing aligns, by default with a coincidence window set by "
             "the local gaps between each ROI's firings",
             "the local-gap window comes from event synchronization (Quian Quiroga, Kreuz and "
             "Grassberger 2002, Phys Rev E 66:041904), carried into SPIKE-synchronization (Kreuz, "
             "Mulansky and Bozanic 2015, J Neurophysiol 113:3432–3445). The detection step on top "
             "is written here; the measure's authors published a detection step of the same kind "
             "(Cecchini and colleagues 2021, PLoS Comput Biol 17:e1008963; Kreuz, personal "
             "communication, April 2026)"),
    "cicada": ("counts ROIs active within a few frames and thresholds against copies with each ROI's "
               "firings shifted in time",
               "a modified port, by way of this program's MATLAB code, of the SCE step of CICADA, "
               "the Cossart lab's calcium-imaging analysis toolbox (Denis and colleagues, software, "
               "doi:10.5281/zenodo.10041434; as used by Dard and colleagues 2022)"),
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
NET_ORIGIN = ("built here. The same network applied to each ROI separately, then a pool over the "
              "ROIs, then a final stage on the pool, is the Deep Sets shape (Zaheer and colleagues "
              "2017, NeurIPS 30; Qi and colleagues 2017, PointNet, CVPR); pooling several statistics "
              "at once is also prior art (Corso and colleagues 2020, NeurIPS 33)")
NET_PLAIN = {"chorus_norm": "vote-pooling net", "chorus_gain_norm": "vote-pooling net with gains",
             "line_length": "share-of-ROIs net", "tube": "pool-first net"}
SURROUND = ("; its comparison with the surrounding stretch is the local-context structure credited "
            "under rate+context")


def context_cut(run: Run, d) -> list:
    """Grid values the context rule removed from a coded detector's declared grid: the run's own rule,
    bench.context_fits_the_null, at the run's declared spacing."""
    sep = run.decl["hand_search"]["min_sep_sec"]
    axes = dict(run.decl["hand_axes"][d])
    return [v for k in ("context_win_sec", "context_win") for v in axes.get(k, [])
            if not bench.context_fits_the_null({k: v}, sep)]


def contestants_table(run: Run) -> str:
    rows = []
    for m in NETS:
        axes = run.decl["learned_axes"][m]
        origin = {"chorus_norm": NET_ORIGIN, "chorus_gain_norm": "as chorus_norm",
                  "line_length": "as chorus_norm" + SURROUND, "tube": "built here" + SURROUND}[m]
        rows.append([f"<b>{esc(m)}</b><br><span class=dim>{esc(NET_PLAIN[m])}</span>", "net",
                     esc(NET_WHAT[m]), esc(origin),
                     f"{len(axes)} training and architecture parameters; 24 configurations"
                     if m == "chorus_norm" else "as chorus_norm" if m != "chorus_gain_norm"
                     else f"{len(axes)} parameters; 24 configurations"])
    for d in CODED:
        axes = run.decl["hand_axes"][d]
        n_values = sum(len(v) for _, v in axes) - len(context_cut(run, d))
        what, origin = CODED_WHAT[d]
        rows.append([f"<b>{esc(NAME[d])}</b>", "coded", esc(what), esc(origin),
                     f"{len(axes)} parameters, {n_values} values searchable, one parameter at a "
                     "time"])
    return tcap(1, "The ten contestants. Every net ends in a probability per frame (a frame is 0.1 "
                   "s); decoding turns it into calls by keeping the frames above a threshold and "
                   "merging nearby runs of them (the merge gap, Figure 3). A net's 24 "
                   "configurations are its untuned one and 23 drawn at random (section 4.1). "
                   "\"Designed here\" means not found elsewhere yet: four literatures where the same "
                   "structure may exist (genomics peak calling, seismological event triggers, "
                   "adaptive image thresholding and changepoint detection) have not been "
                   "searched.") + table(
        ["contestant", "kind", "what it does", "where it comes from", "what was tuned"], rows,
        "Table 1: the ten contestants")


def headline_table(run: Run) -> str:
    rows = []
    for m in list(NETS) + list(CODED):
        cells = [f"<b>{esc(NAME[m])}</b>"]
        for w in SEL:
            if m in CODED and all(run.refused_all(m, w)):
                cells += ["the budget refused every configuration", "—"]
                continue
            vals = run.f1(m, w)
            cell = num(float(np.mean(vals)), 3)
            clean = True
            if m in CODED:
                bad = (sum(1 for ok in run.veto(m, w) if not ok) if w == "ungated"
                       else sum(1 for ok in run.admissible(m, w) if not ok))
                if bad:
                    clean = False
                    cell += (f" <span class=dim>({bad} of 4 fail the crowded check)</span>"
                             if w == "ungated" else
                             f" <span class=dim>({bad} of 4 not admissible)</span>")
            cells.append(cell)
            if m == "coact":
                cells.append("—")
            else:
                c = run.cmp(m, "coact", w)
                cells.append(signed(c["mean"]) + (
                    f" <span class=dim>(<i>t</i> {tnum(c['t'])}; corrected "
                    f"{tnum(c['t'] * run.nb)})</span>" if clean else ""))
        rows.append(cells)
    return tcap(2, "Held-out F1, mean of the four outer folds, every refit counted, and each "
                   "contestant minus CoactDetect (a difference in F1). The paired <i>t</i> and the "
                   "corrected <i>t</i> (section 4.1) are shown only where every fold's result counts. "
                   "A coded choice on F1 alone that fails the crowded-recording check, or one under "
                   "the budget that is not admissible (section 4.5), gets its difference and no "
                   "<i>t</i>.") + table(
        ["contestant", "mean F1, F1 alone", "minus CoactDetect", "mean F1, under the budget",
         "minus CoactDetect"], rows, "Table 2: held-out F1")


def coded_table(run: Run) -> str:
    rows = []
    ref, shipped = run.crowded["reference"], run.crowded["shipped_reference"]
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
            crowd_s = num(lo, 3) if abs(hi - lo) < 5e-4 else f"{num(lo, 3)} to {num(hi, 3)}"
            note = []
            if sum(run.refused_all(d, w)):
                note.append(f"the budget refused every configuration in {sum(run.refused_all(d, w))} of 4 "
                            "folds; the search returned its starting point")
            rows.append([esc(NAME[d]), esc(SEL_NAME[w]), esc(gap), crowd_s,
                         num(ref[d]["crowded_mean_f1"], 3), f"{sum(run.veto(d, w))} of 4",
                         num(shipped[d]["crowded_mean_f1"], 3),
                         f"{sum(run.veto(d, w, shipped=True))} of 4", esc("; ".join(note)) or "—"])
    return tcap(3, "Each coded detector's choices on the crowded recordings (section 4.5). "
                   "\"Crowded F1 of the choices\" is the lowest to highest over the 4 folds' choices. "
                   f"A choice passes if it scores no more than {run.crowded['max_crowded_drop']:g} F1 "
                   "below the configuration it replaces, judged here against two references: the "
                   "one its search started from, and the shipped one goal 1 compares against. The "
                   "crowded recordings are goal 1's first twelve, the ones its search used, so the "
                   "shipped values here match goal 1's reference exactly; goal 1's published crowded "
                   "values for its sliding CoactDetect and LoCo come from its held-out crowded "
                   "recordings instead, so they differ from the starting values here.") \
        + table(["detector", "selection", "merge gap chosen", "crowded F1 of the choices",
                 "crowded F1, starting configuration", "folds passing against the start",
                 "crowded F1, shipped configuration", "folds passing against the shipped", "also"], rows,
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
    bn = best["ungated"]
    cu = run.cmp(bn, "coact", "ungated")
    spf, folds = d["seeds_per_fold"], d["folds"]
    ref = d["reference"]["params"]
    base = d["coded_base"]["values"]
    quiet, busy = (bench.REGIMES[k]["bg_rate_hz"] for k in ("baseline_quiet", "baseline_busy"))
    hot = bench.BENCH_RECORDING["hot_rate_hz"]
    open_items = d.get("measured_outside_interval") or {}
    earlier = 0.103     # docs/goals/learned-model-family.md, the untuned home-spec table (cited)
    lr, steps = (dict(d["learned_axes"]["chorus_norm"])[k] for k in ("lr", "steps"))
    gate = run.meta["budgets"]["0"]["gate_empty_recording"]

    # --- the headline, every piece computed and checked ---
    under_budget = {}
    for m in NETS:
        under_budget[m] = dict(
            this=run.cmp(m, "coact", "gated")["mean"],
            repl=float(np.mean(run.margin(m, "gated", True))),
            repl_kept=float(np.mean(run.margin(m, "gated", True, True))),
            matched={g: float(np.mean(run.matched(m, "gated", g))) for _, g in MATCH_CASES if g})
    budget_behind = all(v < 0 for m in NETS for v in
                        [under_budget[m]["this"], under_budget[m]["repl"], under_budget[m]["repl_kept"],
                         *under_budget[m]["matched"].values()])
    claim(budget_behind, "under the budget, every net is behind CoactDetect on average in both draws "
                         "and at every matched gap")
    budget_best_matched = max(max(under_budget[m]["matched"].values()) for m in CHORUS)
    budget_folds_ahead = max(run.stats(run.matched(m, "gated", g))["ahead"] for m in CHORUS
                             for _, g in MATCH_CASES if g)
    m2, m8, m16 = (run.stats(run.matched(bn, "ungated", g)) for g in (2.0, 8.0, 16.0))
    repl_all = run.stats(run.margin(bn, "ungated", True))
    repl_kept = run.stats(run.margin(bn, "ungated", True, True))
    signs = {cu["mean"] > 0, m2["mean"] > 0, m8["mean"] > 0, repl_kept["mean"] > 0}
    claim(signs == {True, False}, "on F1 alone the best net's sign changes with the gap and the draw")
    claim(cu["mean"] < 0 and m2["mean"] > 0 and repl_kept["mean"] > 0,
          "behind as run, ahead matched at 2 s, ahead on the replicate with failed refits set aside")
    within = max(abs(cu["mean"]), abs(m2["mean"]), abs(m8["mean"]), abs(repl_kept["mean"]))
    repl_best = max(NETS, key=lambda m: np.mean(run.margin(m, "ungated", True, True)))
    claim(repl_best == bn, "the replicate's best net, failed refits set aside, is this run's best net")
    busy_net = run.recall10(bn, "ungated", "busy")
    busy_co = run.recall10("coact", "ungated", "busy")
    quiet_net = run.recall10(bn, "ungated", "quiet")
    quiet_co = run.recall10("coact", "ungated", "quiet")
    busy_ahead = sum(a > b for a, b in zip(busy_net, busy_co))
    quiet_co_ahead = sum(b > a for a, b in zip(quiet_net, quiet_co))
    claim(busy_ahead == 4 and quiet_co_ahead >= 3,
          "the best net finds more faint events on the busy background in every fold, CoactDetect "
          "more on the quiet one in most")

    P = []
    P.append(f"""
<h1>Do the learned detectors beat the hand-written ones once both are tuned fairly?</h1>
<p class=dim>Simulated recordings, baseline periods, the fast stream (terms below; limits in section
11).</p>
<p class=lede><b>The question.</b> This project detects <i>coordinated events</i>, moments when
several cells fire together, in calcium-imaging recordings. It has six hand-written ("coded")
detectors and a family of neural networks ("nets") trained to do the same job. An earlier comparison
put the best net {signed(earlier)} F1 (a 0-to-1 accuracy score, defined below) ahead of the coded
detector CoactDetect, but on a different, since-retired simulator, with every net at one untuned
setting while CoactDetect had one of its settings tuned. This run tunes both sides, on the current
simulator, choosing every setting without looking at the recordings it is scored on (section 6 names
the two places the page does look), and asks again.</p>
<p class=lede><b>The answer.</b> Held to the same limit on false alarms, a limit set at 1.6 times
CoactDetect's own rates, the hand-written CoactDetect is ahead of every net in every fold of two
independent sets of simulated recordings. Chosen for accuracy alone, the two are nearly tied. Counting every training of
every net, CoactDetect is ahead on average in both sets; but in this run the best net moves ahead when
both sides use the same merge gap, how close two calls must be before they are merged into one, a
setting only the coded side was allowed to tune; and in the second set it is ahead in most folds, its
average pulled
down by two trainings that failed. Margins this small are at the limit of what the scoring resolves.
The nets were also handicapped: each fits only 10 of the 72 training recordings, and in this run tuning moved them
by a few hundredths of F1 at most, not always up. The earlier lead is gone even for the untuned nets,
so it was not lost to tuning the nets; the simulator and CoactDetect's own tuning changed together,
and this run cannot separate them. The two sides also win in different places: chosen for accuracy
alone, the two chorus nets find more of the faintest events, those joined by only a tenth of the
cells, when the cells' background firing is high, and CoactDetect finds more of them when it is low.
Among the coded detectors, binned SCE beats CoactDetect under the limit in a few folds, by a few
hundredths of F1 (section 9). Sections 6 to 10 give the numbers.</p>
<p><b>Terms.</b> An <b>ROI</b> (region of interest) is one imaged cell. A cell's <b>firing</b> is one
entry in its list of event times; a <b>coordinated event</b> is several ROIs firing together. A
<b>call</b> is a detector's claim that a coordinated event happened, over a span of time. <b>F1</b>,
from 0 to 1, is the harmonic mean of <b>recall</b> (the share of planted events found) and
<b>precision</b> (the share of calls that were real). Recordings are split into four <b>outer
folds</b>; a configuration is chosen on three and scored on the fourth, the <b>held-out</b> fold (section
4.1). A <b>refit</b> is one training of a chosen net; each is refitted five times, and a few of those
trainings fail outright (section 6). The <b>merge gap</b> is how close two calls may be before they
are merged into one (section 2). The <b>budget</b> is the shared limit on false alarms (section 4.4).
A <b>draw</b> is one set of simulated recordings; this run's and a second workstation's are
independent (section 5). The <b>quiet</b> and <b>busy backgrounds</b> are the two steady rates at
which the simulated cells fire at random (section 2). Each recording comes with two event streams,
lists of per-cell event times extracted by the lab: the <b>fast stream</b>, from brief calcium
transients of about a second, and the slow stream, from much slower ones. <b>Baseline periods</b> are
the stretches recorded before any drug was applied. CoactDetect and LoCo are two of the coded
detectors (Table 1). <b>Goal 1</b> is an earlier study in this program that tuned the six coded
detectors alone and settled the values this run starts CoactDetect and LoCo from (section 4.3). The
<b>project lead</b> is the scientist who owns this project and made the design decisions cited
below.</p>
""")

    P.append(f"""
<h2 id="problem">1. The problem: finding coordinated events</h2>
<p>A coordinated event is several ROIs firing within a fraction of a second of one another, more often
than chance would put them together. Two things make that hard. The cells fire at very different
rates, so a busy cell lands near others by accident all the time. And the whole field sometimes
becomes busier for minutes at a stretch, which raises chance coincidences everywhere without anything
coordinated happening. A detector has to find the few real events without calling either.</p>
<p>A real recording has no answer key, so the example here is simulated (section 2):
<a href="#fig1">Figure 1, one simulated recording</a>. It holds planted coordinated events;
<i>distractors</i>, bursts built like planted events but labeled as negatives (section 2); and the
<i>probe</i>, five minutes in which every ROI fires more often, with nothing planted in it, standing
in for the stretches when the whole field becomes busier.</p>
{figure(1, "One simulated recording and what is in it", fig_problem(),
        f"Recording seed {FIG1_SEED} at the busy background, from the project's simulator (section "
        f"2). <b>A</b>: the whole {bench.BENCH_RECORDING['duration_sec'] / 60:.0f} minutes. Filled "
        f"down-triangles are the 15 planted events, shaded by how many of the ROIs join them; hollow "
        f"gray ones the {bench.BENCH_RECORDING['n_distractors']} distractors; the hatched band the "
        f"probe, from {mmss(bench.BENCH_RECORDING['hot_window'][0])}, ramping up over its first "
        f"{bench.BENCH_RECORDING['ramp_sec']:g} s. The gray band is the stretch panel B shows. "
        f"<b>B</b>: about ten minutes, {mmss(FIG1_WINDOW[0])} to {mmss(FIG1_WINDOW[1])}. The raster "
        f"has one row per ROI ({bench.BENCH_RECORDING['n_roi']} rows) and one tick per firing, rows "
        f"ranked by how often each ROI fires inside this window. The lane above marks the planted "
        f"event at {mmss(facts['event_t'])}, joined by {facts['n_part']} ROIs, and "
        f"{len(facts['distractors'])} distractors. Finding it means finding {facts['n_part']} aligned "
        f"ticks among the {facts['n_onsets']:,} firings in the whole recording.")}
""")

    tol = score.TOL_SEC
    P.append(f"""
<h2 id="bench">2. Why a simulation, and what it simulates</h2>
<p>Nobody knows for certain which moments of a real recording were coordinated, so F1 cannot be
computed on one. The project's <b>bench</b> is a simulator whose inputs are measured from real
baseline recordings, so its recordings look like real ones, but every planted event is known.</p>
<p>Each bench recording is {bench.BENCH_RECORDING['duration_sec'] / 60:.0f} minutes of
{bench.BENCH_RECORDING['n_roi']} ROIs. It holds 15 planted events, 5 at each of three participation
levels: 30%, 18% and 10% of the ROIs. Each event's onsets are drawn with a standard deviation of
{bench.BENCH_RECORDING['jitter_sec']:g} s, and events are at least
{bench.BENCH_RECORDING['min_sep_sec']:g} s apart. Every recording seed (the random seed that
generates one recording) is simulated at two backgrounds, the steady rates at which every cell also
fires at random: the <b>quiet background</b>, {quiet:g} firings per second per ROI, and the <b>busy
background</b>, {busy:g}. These are the 25th and 75th percentiles of the rates in real baseline
recordings, and they last the whole recording; they are not the probe, which adds {hot:g} firings per
second per ROI for five minutes (about {hot / quiet:.0f} times the quiet background's rate, and
{hot / busy:.0f} times the busy one's). A detector's score is its F1 pooled within each background,
then averaged over the two, so doing well at only one background is not enough.</p>
<p>Each recording also holds {bench.BENCH_RECORDING['n_distractors']} distractors. A distractor stands
for a real but uncoordinated burst: it is built exactly as a planted event joined by
{facts['event_frac']:.0%} of the ROIs is built, though placed at random times with no regard to the
planted events, and is labeled a negative, so a call on one counts
against the detector. No detector can tell the two apart by construction, so a detector that finds
nearly every {facts['event_frac']:.0%} event also calls nearly every distractor, and its precision
cannot rise far above {15 / (15 + bench.BENCH_RECORDING['n_distractors']):.2f} (15 planted events
against {bench.BENCH_RECORDING['n_distractors']} distractors). Whether real coincidence of that kind
should count against a detector is an open question in this project.</p>
<p><a href="#fig2">Figure 2, how a call is scored</a>, shows the rules. A call <b>hits</b> a planted
event if its span, widened by {tol:g} s on each side, reaches the event. Matching is one to one: each
call can hit at most one event and each event can be hit by at most one call, so a long call over two
events finds one of them. Calls inside the probe are counted apart, as false alarms per hour, and kept
out of precision. {tol:g} s is where the coded detectors' scores stop changing as the tolerance
widens; the nets' tolerance curve was never measured.</p>
<p><b>How fine a difference the scorer can resolve.</b> The scorer's own documentation says to read
the order in which it ranks detectors, never the decimal places of one score. On F1 alone, in this
run, the margins between the best net and CoactDetect in sections 6 and 7 are {abs(cu['mean']):.3f} to
{max(abs(m2['mean']), abs(m8['mean'])):.3f} F1: they say the two are close, and the sign of so small a
margin says little.</p>
{figure(2, "How a call is scored", fig_scoring(),
        f"A schematic. Each row is a few tens of seconds of one recording; the black bar is a call's "
        f"time span, the gray bracket that span widened by {tol:g} s on each side. The third row is "
        f"why merging calls can cost events (Figure 3).")}
<p>Every detector here produces calls, and calls closer together than a <b>merge gap</b> are merged
into one (<a href="#fig3">Figure 3, merging calls</a>). On this bench, planted events are at least
{bench.BENCH_RECORDING['min_sep_sec']:g} s apart, so for a detector whose calls come in short bursts
around each event, a wide merge folds the burst into one call: precision rises and the event is still
hit. Where events are a few seconds apart, the same merge fuses them, and with one-to-one matching a
fused call finds only one. Merging also chains: calls each within the gap of the next can fuse across
far more than the gap. How wide a merge gap each side was allowed is the subject of section 7.</p>
{figure(3, "Merging calls", fig_merging(),
        "A schematic, with calls drawn as short spans as in Figure 2. In the “far apart” row, two "
        "events each keep their own merged call, and both are hit. In the “close” row, three events "
        "a few seconds apart fuse into one merged call, which can hit only one of them.")}
<p>This run used {folds * spf * 2} recordings with planted events ({folds * spf} seeds,
{d['recording_seeds'][0]} to {d['recording_seeds'][-1]}, at both backgrounds), and
{folds * spf * 2} <b>empty recordings</b>, one per seed at each background with nothing planted, to
count false alarms. The recordings are sampled at 10 frames a second, a frame being 0.1 s.</p>
""")

    P.append(f"""
<h2 id="contestants">3. The contestants</h2>
<p>Ten detectors, four learned and six coded (Table 1). The nets are known by their names in the code;
Table 1 gives each a plain name too. Three of them led the earlier untuned comparison. The fourth,
<code>tube</code>, the pool-first net, was kept as a control because it tied CoactDetect there. On
this simulator it no longer ties: untuned, it scores
{num(float(np.mean([row['untuned']['f1_mean'] for row in r['learned']['tube']])), 3)} against the
tuned CoactDetect's {num(coact['ungated'], 3)}.</p>
<p>What separates the nets is where each stops treating ROIs separately. <code>tube</code> pools
them first. The other three keep each ROI separate long enough for it to cast a bounded vote, then
pool the votes: the two chorus nets, the vote-pooling nets, pool the votes three ways, and
<code>line_length</code> takes the share of ROIs voting. Drawings of the four, made with the
project's architecture tool, are listed in section 12.</p>
{contestants_table(run)}
""")

    ctx_cut = {dd: context_cut(run, dd) for dd in CODED}
    claim(any(ctx_cut.values()), "the context rule removed some grid values")
    ctx_txt = "; ".join(f"{NAME[dd]} lost {and_join([f'{v:g} s' for v in vs])}"
                        for dd, vs in ctx_cut.items() if vs)
    min_sep = run.decl["hand_search"]["min_sep_sec"]
    P.append(f"""
<h2 id="fair">4. How the comparison was kept fair</h2>
<h3>4.1 Nested cross-validation: choose on some recordings, score on others</h3>
<p>If a setting is chosen by looking at the recordings it is then scored on, the score flatters it.
<b>Nested cross-validation</b> prevents that; Varma and Simon (2006, BMC Bioinformatics 7:91) measured
how much choosing and scoring on the same recordings flatters a result. The {folds * spf} recording
seeds are split into {folds} outer folds of {spf}. Each fold takes one turn being held out. With it
set aside, every candidate configuration is judged on the other three folds alone, and the winner is
scored once on the held-out fold (<a href="#fig4">Figure 4, the nested layout</a>).</p>
<p>The two sides are judged on those three folds differently, because only the nets have anything to
fit. A coded detector has no parameters to learn, so each candidate is scored once on all three
training folds pooled. A net is fitted, so each candidate is fitted on two training folds and scored
on the third, three ways round (the <b>inner</b> loop), at 3 training seeds. A training seed sets a
net's random start and also which 10 of the training recordings it fits (section 4.2). An inner fit
depends only on its pair of training folds, so each is shared by the two outer folds that train on
that pair. The chosen net is then refitted at 5 training seeds and scored on the held-out fold.</p>
<p>Each net had 24 configurations: its untuned one and 23 drawn at random before the run started, from
a grid over its learning rate ({', '.join(f'{v:g}' for v in lr)}), its training steps
({', '.join(f'{v:,}' for v in steps)}), and 3 or 4 parameters of its own architecture. Each coded
detector's search changed one parameter at a time through goal 1's declared grids (Table 1). One rule
removed some grid values: a <b>context window</b> (the stretch a coded detector uses to estimate
chance) may not be wider than the {min_sep:g} s between planted events, because a wider one takes its
estimate of chance from a stretch holding other planted events ({ctx_txt}).</p>
{figure(4, "The nested cross-validation layout", fig_nested(run),
        "<b>A</b>: the four outer folds; each takes one turn being scored, while the other three are "
        "used to choose. Folds are numbered 1 to 4 here and 0 to 3 in the run's files. <b>B</b>: "
        "inside held-out fold 1. A net's candidate configuration is fitted on two training folds and "
        "scored on the third, three ways round; a coded detector's candidate is scored on folds 2 to "
        "4 at once. Either way, the chosen configuration is then scored once on fold 1.")}
<p><b>What four folds can and cannot show.</b> The <i>t</i> values below rank how consistent a
difference is across folds; they are not tests. Every comparison pairs the two sides fold by fold, so
it rests on 4 numbers and 3 degrees of freedom, and each training fold serves three held-out folds, so
the folds are less independent than a paired <i>t</i> assumes and the plain <i>t</i> overstates the
evidence. Table 2 therefore also gives each <i>t</i> multiplied by {run.nb:.3f} (√(3/7)), the
correction of Nadeau and Bengio (2003, Machine Learning 52:239–281, doi:10.1023/A:1024068626366) for a
test set one third the size of the training set. It was derived for repeated random splits; Bouckaert
and Frank (2004, PAKDD, LNCS 3056:3–12) carry it to repeated k-fold cross-validation, treating k-fold as
a special case of random subsampling; and Bengio and Grandvalet (2004, JMLR 5:1089–1105) show that no
unbiased estimator of k-fold's variance holds for every distribution. The correction also has no
stated form for a learner that fits only part of its training set, as the nets do, so it is not exact
for them either. For comparison, a two-sided 5% test at 3 degrees of freedom would need |<i>t</i>| of
at least 3.18.</p>
""")

    fd = run.draws
    fitted = {h: {int(x.split(":")[1]) for x in v["fitted"]} for h, v in fd["as_run"].items()}
    shared = [len(fitted[str(a)] & fitted[str(b)]) for a in run.folds for b in run.folds if a < b]
    n_fit_seeds = len(next(iter(fitted.values())))
    P.append(f"""
<h3>4.2 A defect fixed before the run: outer folds were training the same model</h3>
<p>A net does not train on every training recording. It fits a run of 10 consecutive recordings from
the list it is given, the training seed deciding where in the list the run starts, and, when chosen on
F1 alone, picks its threshold on the last two recordings of the list. Until this run the list was in
fold order, so at some training seeds the run of 10 fell inside the first training fold, and held-out
folds sharing that fold would have trained exactly the same model. Four outer folds would then have
been fewer than four independent fits (<a href="#fig5">Figure 5, the fitting draws before and
after</a>). The 10 is inherited from the earlier comparison, not chosen for this one.</p>
<p>The fix deals the recordings across the training folds in turn, starting after the held-out one,
so every fit reaches every training fold and the threshold recordings rotate too. Before launching,
the run replayed the exact draws for every training seed, and would have refused to start if any two
outer folds shared a fitting set or threshold recordings. "Not the same" is not "independent": at
the first training seed, two outer folds' fitting sets share {min(shared)} to {max(shared)} of their
{n_fit_seeds} recording seeds.</p>
{figure(5, "Which recordings each outer refit fitted, at the first training seed", fig_defect(run),
        "Each strip is the 48 recording seeds, one cell per seed; each seed stands for its two "
        "recordings, one at each background. <b>A</b>: the order used before the fix, applied to "
        "this run's split. Held-out folds 2, 3 and 4 fit the same ten recordings, seeds 1000 to "
        "1004; fold 1's set differs only because fold 1 is the one held out. <b>B</b>: what this run "
        "actually fitted, read from its fit records: four different sets, each reaching every "
        "training fold, still overlapping.")}
""")

    ok_b = max(sum(1 for t in MODE_TICKS if b <= t < b + 1) for b in range(8, 12)) >= MODE_NEED
    claim(not ok_b, "Figure 5's schematic: binned misses the recorded firings")
    P.append(f"""
<h3>4.3 The coded side runs in its better mode</h3>
<p>CoactDetect and LoCo can count firings in two ways. <i>Binned</i> mode counts them in fixed time
bins; <i>sliding</i> mode counts them in a window that moves smoothly (<a href="#fig6">Figure 6,
binned and sliding counting</a>). Goal 1 found sliding mode better on held-out recordings, and found
that it keeps its calls when a recording is shifted by a fraction of a second, where binned mode can
lose them. The project's current defaults are still binned, so every parameter these two searches did
not vary was held at goal 1's sliding values instead. (The detector named binned SCE is a different
detector, whose only counting is in bins.)</p>
{figure(6, "Binned and sliding counting of the same six firings", fig_modes(),
        f"A schematic: six ROIs fire within a second, and a call needs {MODE_NEED} of them in one "
        f"second. <b>A</b>: fixed one-second bins split them 3 and 3, so binned counting makes no "
        f"call; a sliding one-second window finds all 6. <b>B</b>: the same firings "
        f"{MODE_SHIFT:g} s later fall in one bin, and binned counting now calls. A result that turns "
        f"on where the bin edges fall is what goal 1 measured and left behind.")}
<p>The reference CoactDetect below therefore uses goal 1's values: alpha {ref['alpha']:.0e}, a
threshold on an approximate p-value that works as a tuning parameter rather than a calibrated
false-alarm rate; a context window of {ref['context_win_sec']:g} s; a merge gap of
{ref['merge_gap_sec']:g} s; and a guard of {ref['guard_sec']:g} s, the stretch next to the moment
tested that is left out of the estimate of chance. LoCo calls when its count passes the
{base['loco']['threshold_pctile']:g}th percentile of the same count on copies with each ROI's firings
shifted in time, and uses an {base['loco']['merge_gap_sec']:g} s merge gap. The other four coded
detectors start from their shipped operating points, the values the project ships them at.</p>
""".replace("1e-05", "10<sup>−5</sup>"))

    P.append(f"""
<h3>4.4 Two selections, and one false-alarm budget for everyone</h3>
<p>Choosing on F1 alone rewards a detector that calls more: extra calls can pick up extra planted
events faster than they cost precision. So every contestant was chosen twice
(<a href="#fig7">Figure 7, the two selections</a>): once on F1 alone, asking which configuration
finds the most events; and once on F1 among the configurations within a <b>shared false-alarm
budget</b>, asking which finds the most while firing no more than {d['budget_margin']:g} times as
often as the reference CoactDetect.</p>
<p>On each outer fold's training recordings, a candidate may fire at most {d['budget_margin']:g} times
as often as the reference does, on each of three gates: the probe at the quiet background, the probe
at the busy background, and the empty recordings at the quiet background. The empty recordings at the
busy background are reported but do not gate, by the project lead's decision before the run (goal 2's
decision 3); section 10 gives their rates. The limit is shared in name but shaped like CoactDetect: it
is the reference's own rate on each gate, scaled, so a detector whose false alarms fall differently
across the gates is held by its worst one. {d['budget_margin']:g} is a margin the project lead
declared before the run, not a measured value, and no sensitivity to it was run. The budget has a
floor of one false alarm in the time measured, and no fold's budget was low enough to reach it. It
counts calls after merging, so a detector with a wider merge gap calls less and passes it more easily
(section 7).</p>
<p>For a net, the two selections choose from the same fits. Under the budget its threshold is chosen
inside the budget too, on the inner fits, one threshold for all five refits; on F1 alone each refit
picks its own threshold on two recordings. For a coded detector the two selections are separate
searches: the budget changes which steps the search can take.</p>
{figure(7, "Two selections from the same candidates", fig_budget(run),
        "A schematic, not data. Each gray point is a candidate configuration, with its F1 and its "
        "false alarms per hour on the training recordings; for a net, a candidate is a configuration "
        "with one of its thresholds. The black square is the reference CoactDetect. The unshaded "
        f"region is within the budget, {d['budget_margin']:g} times the reference's rate, measured in "
        "the probe and on the empty recordings at the quiet background.")}
""")

    P.append(f"""
<h3>4.5 Which results count: the crowded-recording check</h3>
<p>Goal 1 found that a search free to widen the merge gap (Figure 3) gains F1 on this bench by
fusing calls, a gain that becomes a loss where events are close together. It added a rule, the
<b>crowded-recording check</b>: a coded configuration may not score more than
{run.crowded['max_crowded_drop']:g} F1 below the one it replaces on <b>crowded recordings</b>, where
"the one it replaces" is the configuration the search started from (section 9 also scores it against
the shipped one). The crowded recordings are {crowd['n_recordings']} simulated recordings of
{'/'.join(f'{h:g}' for h in crowd['hours'])} hours with {crowd['n_events'][0]} planted events each, at
least {crowd['min']:.0f} s apart (the minimum gap in the most crowded real recordings) and
{crowd['median']:.0f} s apart at the median: more crowded overall than any real recording, on purpose.
It penalizes a merge gap only where the gap fuses events there, which for a detector that merges calls
by their event times means a gap wider than about {crowd['min']:.0f} s, and for one that merges sliding
windows a narrower one, by about the window's width. {run.crowded['max_crowded_drop']:g} is a judgment
the project lead has not yet signed.</p>
<p>This run's search did not apply the check; it was applied to every coded choice after the run.
Goal 1 applies it inside the search, where a refused candidate sends the search elsewhere; applied
afterwards, it can strike a choice but cannot find one that passes. A coded result is
<b>admissible</b> when it was chosen within the budget and passes the check; a choice on F1 alone is
not budgeted, so for it the page says only whether it passes the check. The nets were not checked on
crowded recordings: their merge gap was fixed, so their search could not choose a wide one.</p>
<h3>4.6 What was not made equal</h3>
<p>These asymmetries remain, and each bears on the results below:</p>
<ul>
<li><b>The merge gap</b> was searched for the coded detectors and fixed at 2 s for the nets (section
7).</li>
<li><b>Training data</b>: a net fits 10 of the 72 training recordings and, on F1 alone, picks its
threshold on 2 of them; a coded configuration is scored on all 72 (section 4.2). This handicaps the
nets.</li>
<li><b>The crowded-recording check</b> was applied to the coded side only (section 4.5).</li>
<li><b>The budget</b> is CoactDetect's own rate, gate by gate (section 4.4).</li>
<li><b>What the nets were trained on</b>: every training recording contains the same probe and six
distractors, labeled as negatives, and distractors are built exactly as planted events joined by 18%
of the ROIs are. The nets were taught to refuse those patterns; the coded detectors were only scored on
them (section 11).</li>
</ul>
""")

    P.append(f"""
<h2 id="replicate">5. A second, independent draw of recordings</h2>
<p>Four outer folds give only 3 degrees of freedom, and a margin of a hundredth of F1 can come and go
with which recordings happened to be drawn. So a second workstation ran the same comparison on a
disjoint set of recordings: recording seeds {run.repl['recording_seeds'][0]} to
{run.repl['recording_seeds'][1]} instead of {d['recording_seeds'][0]} to
{d['recording_seeds'][-1]}, with the configurations, grids, training seeds, budget rule and simulator
held fixed. A difference between the two runs is then a difference between draws of recordings and
between machines, which this comparison cannot separate: the replicate trained on another GPU
(graphics processor) of the same model, and retraining on another machine can move a net's F1 by about
as much as the margins below (section 11). Its numbers appear beside this run's in section 6, read
from its results by the same rules; its own report is the authority on it (section 12).</p>
""")

    # --- section 6 ---
    lows, rlows = run.low_refits(), run.low_refits(True)
    n_refits = run.n_stage("outer")
    n_scored = sum(len(row[w]["per_seed"]) for m in NETS for row in r["learned"][m]
                   for w in ("untuned",) + SEL)
    this_behind = all(v < 0 for v in cu["per_fold"])
    claim(this_behind, "this run: the best net is behind CoactDetect in every fold, as chosen")
    claim(not any(x["low"] for x in run.health[bn]["ungated"]),
          "none of this run's best-net refits on F1 alone is below the cut")
    ra = [v for v in repl_all["per_fold"]]
    repl_low_folds = [h for h, x in enumerate(run.rhealth[bn]["ungated"]) if x["low"]]
    all_behind = {(rep, w): all(float(np.mean(run.margin(m, w, rep))) < 0 for m in NETS)
                  for rep in (False, True) for w in SEL}
    claim(all(all_behind.values()), "counting every refit, every net is behind CoactDetect on average "
                                    "in both draws and both selections")
    claim(len(repl_low_folds) == 1 and len(run.rhealth[bn]["ungated"][repl_low_folds[0]]["low"]) == 2
          and all(run.rhealth[bn]["ungated"][repl_low_folds[0]]["failed_signature"]),
          "the lede's two failed trainings in one replicate fold")
    claim(all(v < 0 for m in NETS for rep in (False, True) for v in run.margin(m, "gated", rep)),
          "under the budget every net is behind CoactDetect in every fold of both draws")
    rbest = max(NETS, key=lambda m: np.mean(run.repl["learned"][m]["ungated"]))
    rbest_all = run.stats(run.margin(rbest, "ungated", True))
    ahead_folds = [(m, w, h, v) for m in NETS for w in SEL
                   for h, v in enumerate(run.cmp(m, "coact", w)["per_fold"]) if v > 0]
    sce_run = float(np.mean(run.coded_f1("sce", "ungated")))
    P.append(f"""
<h2 id="results">6. What came out, at the configurations each search chose</h2>
<p><b>Counting every refit, CoactDetect is ahead of every net on average, in both draws of recordings
and in both selections.</b> What differs between the selections is how consistently: under the budget
every net is behind in every fold of both draws, while on F1 alone the best net's margin is small and
its sign changes with the merge gap and the draw.
<a href="#fig8">Figure 8, held-out F1 for all ten contestants</a>, shows every outer fold of this run,
and Table 2 gives the means and each contestant's difference from CoactDetect. The best net is picked
here from four by its held-out mean, which flatters the net side slightly.</p>
{figure(8, "Held-out F1 per outer fold", fig_results(run),
        "One row per contestant: nets in blue above the dashed line, coded detectors in black below "
        "it. For a net, a fold's value is the mean over its 5 refits, every refit counted; a ringed "
        f"dot is a fold holding a refit below {LOW_F1:g} F1 (section 6). A hollow circle is a coded "
        "choice that fails the crowded-recording check (section 4.5). An × is a fold where the budget "
        "refused every configuration the search tried, so there is no result under the budget; it is "
        "placed at the held-out F1 of the starting configuration, which was scored but is not a "
        "result.")}
{headline_table(run)}
<ul>
<li><b>On F1 alone, in this run,</b> the best net, <code>{esc(bn)}</code>, trails CoactDetect by
{num(-cu['mean'], 3)} F1 and is behind in every fold. The one coded detector that scores higher,
binned SCE at {num(sce_run, 3)}, does so by merging calls up to 30 s apart, and its choices fail the
crowded-recording check (section 9).</li>
<li><b>On F1 alone, in the replicate,</b> the best net counting every refit is
<code>{esc(rbest)}</code>, behind CoactDetect by {num(-rbest_all['mean'], 3)} and ahead in
{rbest_all['ahead']} of 4 folds. This run's best net, <code>{esc(bn)}</code>, is ahead in
{repl_all['ahead']} of 4 folds there ({', '.join(signed(v) for v in ra)}), but its mean,
{signed(repl_all['mean'])}, is pulled down by {fold_label(repl_low_folds[0])}, where
{len(run.rhealth[bn]['ungated'][repl_low_folds[0]]['low'])} of its 5 refits failed to train.</li>
<li><b>A refit that failed to train</b> is one training of a net that ended calling one long stretch
per recording, so it finds an event or two and nothing else. A few refits score below {LOW_F1:g} F1,
where every other scores at least {min(run.lowest_other_refit(), run.lowest_other_refit(True)):.2f}:
most failed to train, and the rest made no calls at all at the one threshold their selection chose
(section 10 lists them all; about 1% of refits, in both draws). Setting aside refits below
{LOW_F1:g} F1, a check made after seeing the held-out scores and not a rule fixed in advance,
<code>{esc(bn)}</code> in the replicate is ahead in {repl_kept['ahead']} of 4 folds by
{signed(repl_kept['mean'])}. None of this run's <code>{esc(bn)}</code> refits fell below it, so its
margin does not move. This check and the choice of the best net by its held-out mean are the two
places this page looks at held-out scores to decide what to show.</li>
<li><b>Under the budget,</b> every net is behind CoactDetect on average in both draws; the closest,
<code>{esc(best['gated'])}</code>, by {num(-run.cmp(best['gated'], 'coact', 'gated')['mean'], 3)} in
this run. CoactDetect scores {num(coact['ungated'], 3)} both ways{' (its two searches chose the same configuration in every fold)' if same_coact else ''},
and its choices pass the crowded-recording check in
{sum(run.veto('coact', 'ungated')) + sum(run.veto('coact', 'gated'))} of 8 cases (4 folds × 2
selections).</li>
</ul>
<p><a href="#fig9">Figure 9, each net minus CoactDetect</a>, shows both draws fold by fold.</p>
{figure(9, "Each net minus CoactDetect, per outer fold, in both draws", fig_margins(run),
        "For each net and selection, the upper line is this run and the lower the replicate (section "
        "5). Each mark is one outer fold: the net's held-out F1, mean over its refits, minus "
        f"CoactDetect's on the same fold, with refits below {LOW_F1:g} F1 set aside; a ringed mark is a "
        "fold that held one. The every-refit values are in the text above and in Table 2. "
        + ("Right of zero in this run: " + "; ".join(
            f"{m} on {SEL_NAME[w]}, {fold_label(h)}, by {v:.4f}" for m, w, h, v in ahead_folds) + "."
           if ahead_folds else "No fold of this run has a net ahead."))}
""")

    # --- section 7: the merge gap ---
    cg_gaps, cg_vals, cg_chosen = run.coded_gap_curve("coact")
    ng, nvals = run.net_gap_curve(bn)
    net_best_gap = max(ng, key=lambda g: np.mean(nvals[g]))
    repro_coded, repro_net, repro_fold = run.gap_repro()
    rising = {dd: all(np.mean(run.coded_gap_curve(dd)[1][a]) <= np.mean(run.coded_gap_curve(dd)[1][b])
                      for a, b in zip(cg_gaps, cg_gaps[1:])) for dd in ("coact", "sce", "loco")}
    claim(all(rising.values()), "every coded curve rises with the merge gap")
    falling_nets = [m for m in NETS if np.mean(run.net_gap_curve(m)[1][8.0])
                    < np.mean(run.net_gap_curve(m)[1][2.0])]
    rising_nets = [m for m in NETS if m not in falling_nets]
    gm = {m: {g: run.stats(run.matched(m, "gated", g)) for _, g in MATCH_CASES if g} for m in CHORUS}
    t_rng = {m: (min(s["t"] for s in gm[m].values()), max(s["t"] for s in gm[m].values()))
             for m in CHORUS}
    ahead_rng = {m: max(s["ahead"] for s in gm[m].values()) for m in CHORUS}
    claim(ahead_rng["chorus_gain_norm"] == 0 and 0.005 < m2["mean"] < 0.015
          and 0.005 < m8["mean"] < 0.015, "section 7's lead sentence")
    gated_nets_up = {m: np.mean(run.net_gap_curve(m, "gated")[1][16.0])
                     > np.mean(run.net_gap_curve(m, "gated")[1][2.0]) for m in NETS}
    sce_at_8 = float(np.mean(run.coded_gap_curve("sce")[1][8.0]))
    P.append(f"""
<h2 id="merge">7. The setting the two sides did not share: the merge gap</h2>
<p><b>On F1 alone, given the same merge gap, the best net moves ahead of CoactDetect in this run, by
about 0.01 F1; under the budget, CoactDetect stays ahead at every gap tried.</b> Neither margin is
large enough to call. The coded detectors' searches tuned their merge gaps (Figure 3); the nets' was
fixed at 2 s (20 frames), the default returned by their threshold picker (the training step that sets a net's threshold), and never searched. The budget
counts calls after merging (section 4.4), so the difference touches both selections.</p>
<p><a href="#fig10">Figure 10, the chorus nets against CoactDetect at matched gaps</a>, re-scores both
sides with only the merge gap changed. On F1 alone, <code>{esc(bn)}</code> is ahead by
{signed(m2['mean'])} with both at 2 s ({m2['ahead']} of 4 folds; <i>t</i> {tnum(m2['t'])}, corrected
{tnum(m2['tc'])}) and by {signed(m8['mean'])} with both at 8 s ({m8['ahead']} of 4; <i>t</i>
{tnum(m8['t'])}, corrected {tnum(m8['tc'])}). Under the budget, CoactDetect stays ahead of
<code>chorus_gain_norm</code> in every fold at every matched gap (<i>t</i> {tnum(t_rng['chorus_gain_norm'][0])}
to {tnum(t_rng['chorus_gain_norm'][1])}), and of <code>chorus_norm</code> by
{min(-s['mean'] for s in gm['chorus_norm'].values()):.3f} to
{max(-s['mean'] for s in gm['chorus_norm'].values()):.3f} F1, with
the net ahead in at most {ahead_rng['chorus_norm']} of 4 folds (<i>t</i> {tnum(t_rng['chorus_norm'][0])}
to {tnum(t_rng['chorus_norm'][1])}): as weak as the reversal on F1 alone. Each matched comparison
handicaps one side. At 2 s, CoactDetect's other parameters were tuned together with an 8 s gap. At a
wider gap, a net keeps a threshold chosen at 2 s; under the budget that handicap favors CoactDetect,
since a wider merge calls less and a lower threshold might then have fitted the budget.</p>
{figure(10, "The chorus nets minus CoactDetect with the merge gap matched", fig_matched(run),
        "Each dot is one outer fold, every refit counted; the bar is the mean of four; a ringed dot is "
        f"a fold holding a refit below {LOW_F1:g} F1 (section 6). \"As run\" is the net at its 2 s "
        "against CoactDetect at its chosen 8 s; the other rows re-score both at the gap named, "
        "nothing re-chosen. <b>A</b>: choices on F1 alone. <b>B</b>: choices under the budget, whose "
        "thresholds were chosen at 2 s. Left of the dashed zero line, CoactDetect is ahead.")}
<p><a href="#fig11">Figure 11, what the merge gap is worth</a>, shows each side's held-out F1 as the
gap changes, on F1 alone. A wider merge helps every coded detector shown: CoactDetect rises from
{num(float(np.mean(cg_vals[2.0])), 3)} at 2 s to {num(coact['ungated'], 3)} at its chosen 8 s and
{num(float(np.mean(cg_vals[30.0])), 3)} at 30 s. Among the nets it helps
{and_join([f'<code>{m}</code>' for m in rising_nets])}: <code>{esc(bn)}</code> goes from
{num(float(np.mean(nvals[2.0])), 3)} at 2 s to {num(float(np.mean(nvals[net_best_gap])), 3)} at
{net_best_gap:g} s. On F1 alone it costs {and_join([f'<code>{m}</code>' for m in falling_nets])},
whose worst refits call almost continuously at a threshold near the bottom of the grid, so merging
fuses their calls into long spans; under the budget a wider merge helps
{'all four nets' if all(gated_nets_up.values()) else and_join([m for m, v in gated_nets_up.items() if v])}.
Nothing was re-chosen at a new gap, so these curves indicate what tuning the gap could do; a search
that tuned it together with the other parameters could do better.</p>
{figure(11, "What the merge gap is worth on each side", fig_gap_curves(run),
        "Held-out F1, mean of the four outer folds, for choices on F1 alone, with only the merge gap "
        "changed: every choice of CoactDetect, binned SCE and LoCo re-scored at each gap, and every "
        "chosen net refit re-decoded from its saved model at 2 to 16 s, keeping its threshold. "
        "(rate+context also has a merge gap and was not re-scored.) Each side first reproduces the "
        f"run's own scores at its own gap: the coded detectors exactly, the nets within {repro_net:.4f} "
        f"F1 per refit and {repro_fold:.4f} per fold mean, since the run scored on a GPU and this "
        "re-scoring ran on a CPU (central processor). The faded segments cross the axis break "
        "between 0 s and 2 s. The coded curves rise all the way to 30 s, which is what the "
        "crowded-recording check (section 4.5) exists to stop.")}
<p>A rerun that tunes the nets' merge gap like any other parameter would remove the asymmetry; it
needs no retraining, only re-scoring. It has not been run.</p>
""")

    # --- section 8: where the two sides differ ---
    sat = min(v for s in ("coact",) + CHORUS for w in SEL for b in ("quiet", "busy")
              for row in (run.bd["detectors"] if s in CODED else run.bd["nets"])[s]
              if row["selection"] == w
              for f, v in row["by_background"][b]["recall_by_participation"].items() if f != "0.1")
    dist = [row["by_background"][b]["distractor_hit_rate"]
            for s in ("coact",) + CHORUS for row in (run.bd["detectors"] if s in CODED else run.bd["nets"])[s]
            if row["selection"] == "ungated" for b in ("quiet", "busy")]
    fq = float(np.mean(run.f1_background(bn, "ungated", "quiet"))
               - np.mean(run.f1_background("coact", "ungated", "quiet")))
    fb = float(np.mean(run.f1_background(bn, "ungated", "busy"))
               - np.mean(run.f1_background("coact", "ungated", "busy")))

    def precision(side, w, b):
        rows = (run.bd["detectors"] if side in CODED else run.bd["nets"])[side]
        c = [r["by_background"][b] for r in rows if r["selection"] == w]
        hits = sum(sum(x["hit"].values()) for x in c)
        return hits / sum(x["n_detected"] - x["hot_fa"] for x in c)

    for m, sels in ((bn, ("ungated",)), ("chorus_gain_norm", SEL)):
        for w in sels:
            claim(all(a > b for a, b in zip(run.recall10(m, w, "busy"), run.recall10("coact", w, "busy"))),
                  f"{m} finds more faint events at the busy background in every fold, {w}")
    P.append(f"""
<h2 id="differ">8. Where the two sides differ</h2>
<p>A pooled F1 can hide two sides winning in different places, and here it does
(<a href="#fig12">Figure 12, the planted events found, by participation and background</a>). Events
joined by 30% or 18% of the ROIs are found by both sides almost every time: recall
{math.floor(sat * 100) / 100:.2f} or more in every fold, background and selection, for CoactDetect and
both chorus nets. What separates them is the faintest events, joined by 10% of the ROIs. On F1 alone,
against the busy background, <code>{esc(bn)}</code> finds more of them than CoactDetect in
{busy_ahead} of 4 folds ({np.mean(busy_net):.2f} against {np.mean(busy_co):.2f} on average), and
<code>chorus_gain_norm</code> does too, in both selections; against the quiet background CoactDetect
finds more in {quiet_co_ahead} of 4 ({np.mean(quiet_co):.2f} against {np.mean(quiet_net):.2f}). By
background, <code>{esc(bn)}</code> minus CoactDetect in F1 is {signed(fq)} at the quiet background and
{signed(fb)} at the busy one: the net's extra faint events at the busy background are paid for in
precision, {precision(bn, 'ungated', 'busy'):.3f} against CoactDetect's
{precision('coact', 'ungated', 'busy'):.3f} there. Both sides also call {min(dist):.0%} to
{max(dist):.0%} of the distractors on F1 alone, a distractor counting as called when any call's
widened span reaches it. The breakdown covers the two chorus nets and this run only.</p>
{figure(12, "The planted events found, by participation and background", fig_breakdown(run),
        "The share of planted events each detector found on the held-out fold, per outer fold (dots) "
        "and on average (bars), for choices on F1 alone; for a net, pooled over its 5 refits, and "
        f"ringed where a refit fell below {LOW_F1:g} F1 (section 6). "
        "<b>A</b>: events joined by 30% of the ROIs; <b>B</b>: by 18%; <b>C</b>: by 10%. Read from "
        "the run's own score rows (<code>breakdown.json</code>).")}
""")

    # --- section 9: the coded detectors' choices ---
    sce_run = float(np.mean(run.coded_f1("sce", "ungated")))
    sce_pass = {w: sum(run.veto("sce", w)) for w in SEL}
    sce_pass_fold = [h for h in run.folds if run.veto("sce", "gated")[h]]
    no_admissible = [dd for dd in CODED if not any(run.admissible(dd, "gated"))]
    veto_fail_gated = [dd for dd in no_admissible if not all(run.refused_all(dd, "gated"))]
    refused_gated = [dd for dd in no_admissible if all(run.refused_all(dd, "gated"))]
    start_over = {dd: sum(run.start_over_budget(dd)) for dd in CODED}
    verdict_change = [(c["detector"], c["outer_fold"], c["selection"]) for c in run.crowded["choices"]
                      if c["passes_veto"] != c["passes_veto_vs_shipped"]]
    sync_fixed = sum(1 for row in r["hand"]["sync"]
                     if row["gated"]["chosen_params"].get("tau_mode") == "fixed")
    claim(sync_fixed > 0, "SPIKE-synch under the budget chose a fixed window in some fold")
    coact_over = sum(1 for x in r["hand"]["coact"] if x["gated"].get("over_budget"))
    other_over = [(dd, h) for dd in CODED if dd != "coact" for h in run.folds
                  if run.admissible(dd, "gated")[h] and r["hand"][dd][h]["gated"].get("over_budget")]
    claim(not other_over, "no other admissible coded choice exceeded the budget on held-out data")
    claim(set(veto_fail_gated) | set(refused_gated) == set(no_admissible), "section 9's split")
    coact_at_30 = float(np.mean(run.coded_gap_curve("coact")[1][30.0]))
    claim(coact_at_30 > sce_run, "at binned SCE's own 30 s gap CoactDetect scores higher")
    sce_win = [(h, run.coded_f1("sce", "gated")[h] - run.coded_f1("coact", "gated")[h])
               for h in run.folds if run.admissible("sce", "gated")[h]]
    sce_drop = [c for c in run.crowded["choices"] if c["detector"] == "sce"
                and c["selection"] == "gated" and c["passes_veto"]]
    repl_sce = [a - b for a, b in zip(run.repl["hand"]["sce"]["gated"], run.repl["hand"]["coact"]["gated"])]
    ra_sce = run.repl["admissibility"]["sce"]["gated"]
    repl_sce_adm = [(h, v) for h, v in enumerate(repl_sce)
                    if ra_sce["passes_crowded"][h] and not ra_sce["refused_all"][h]]
    claim(all(v > 0 for _, v in repl_sce_adm) and len(repl_sce_adm) >= 2,
          "in the replicate, binned SCE is admissible and ahead of CoactDetect in its admissible folds")
    moves = {dd: run.first_move(dd, 0) for dd in veto_fail_gated}
    move_txt = "; ".join(
        f"{NAME[dd]} moved <code>{esc(mv['setting'])}</code> from {mv['old']:g} to {mv['new']:g}, "
        f"training F1 {mv['old_f1']:.2f} to {mv['new_f1']:.2f}" for dd, mv in moves.items() if mv)
    P.append(f"""
<h2 id="coded">9. The coded detectors' choices</h2>
<ul>
<li><b>Binned SCE finishes first on paper, at {num(sce_run, 3)} on F1 alone, by merging calls up to
30 s apart, and it is no better than CoactDetect at a matched gap.</b> Its search chose a 30 s merge
gap, the top of its grid, in every fold; at that same gap CoactDetect scores {num(coact_at_30, 3)}
(Figure 11). Its choices fail the crowded-recording check in
{8 - sce_pass['ungated'] - sce_pass['gated']} of 8 cases. The one that passes is
{fold_label(sce_win[0][0]) if sce_win else 'none'} under the budget,
{sce_drop[0]['reference_crowded_mean_f1'] - sce_drop[0]['crowded_mean_f1']:.3f} F1 below its start on
the crowded recordings, inside the {run.crowded['max_crowded_drop']:g} allowance, and there it is ahead
of CoactDetect by {signed(sce_win[0][1])} F1, an admissible win in one fold. In the replicate the
pattern is stronger: under the budget, binned SCE's choices pass the replicate's own
crowded-recording check in {sum(ra_sce['passes_crowded'])} of 4 folds, the budget refused every
configuration in {sum(ra_sce['refused_all'])}, and in the {len(repl_sce_adm)} admissible folds it is
ahead of CoactDetect, by {and_join([signed(v) for _, v in repl_sce_adm])} F1. <b>So under the budget,
binned SCE is the one detector on this page that admissibly beats CoactDetect in some folds</b>:
{len(sce_win)} of 4 here and {len(repl_sce_adm)} of 4 in the replicate, by a few hundredths of F1 at
most.</li>
<li><b>Under the budget, {and_join([NAME[x] for x in no_admissible])} have no admissible result in
any fold.</b> The budget is anchored to CoactDetect, and every other coded detector's starting point
was over it in every fold ({and_join([NAME[x] for x in CODED if start_over[x] == 4])}). When a start
breaks the budget, the search takes the best value within the budget on the first parameter, in the
grid's order, that has one, whatever that costs: at {fold_label(0)}, {move_txt}. For
{and_join([NAME[x] for x in veto_fail_gated])}, what the searches reached that way loses events
everywhere, crowded recordings included, and fails the check in every fold. So these results depend on
the order of the parameters in the grid as well as on the detectors, and the check, applied after the
search, could not look for a configuration that passes both rules (section 4.5).
{' '.join(f'For {NAME[x]}, the budget refused every configuration its search tried, the start included, so it has no result under the budget at all.' for x in refused_gated)}</li>
<li><b>Which reference the check uses changes {('no' if not verdict_change else len(verdict_change))}
verdict{'' if len(verdict_change) == 1 else 's'}</b> (Table 3; <a href="#fig13">Figure 13, the coded
choices on the crowded recordings</a>).</li>
<li><b>SPIKE-synch, under the budget, dropped the local-gap coincidence window that defines
SPIKE-synchronization</b> and used a fixed window in {sync_fixed} of 4 folds.</li>
<li><b>CoactDetect exceeded the budget on the held-out fold in {coact_over} of 4 folds</b>: a choice
made within the budget on training recordings need not stay within it on new ones. No other admissible
coded choice exceeded it.</li>
</ul>
{figure(13, "The coded choices on the crowded recordings", fig_crowded(run),
        "One row per coded detector and selection. Each dot is one fold's choice, filled if it passes "
        "the check against the configuration its search started from (solid tick), hollow if it "
        f"fails; the gray band is the {run.crowded['max_crowded_drop']:g} F1 allowed below that tick. "
        "The dashed tick is the shipped configuration, goal 1's reference. An × is a fold where the "
        "budget refused every configuration, so the start was scored but is no result.")}
{coded_table(run)}
""")

    # --- section 10: tuning, failed refits, overruns ---
    tun = {w: {m: run.tuning(m, w) for m in NETS} for w in SEL}
    over = {m: run.over_budget_nets(m) for m in NETS}
    n_refits_gated = sum(len(row["gated"]["per_seed"]) for m in NETS for row in r["learned"][m])
    probe_gated = {m: [float(np.mean(list(s["probe_per_hour"].values())))
                       for row in r["learned"][m] for s in row["gated"]["per_seed"]] for m in CHORUS}
    probe_coact = [float(np.mean(list(row["gated"]["probe_per_hour"].values())))
                   for row in r["hand"]["coact"]]
    spread_chorus = max(max(s["probe_per_hour"][b] for s in row["gated"]["per_seed"])
                        - min(s["probe_per_hour"][b] for s in row["gated"]["per_seed"])
                        for m in CHORUS for row in r["learned"][m] for b in ("quiet", "busy"))
    quiet_gated = {m: [s["quiet_per_hour"]["null_quiet"] for row in r["learned"][m]
                       for s in row["gated"]["per_seed"]] for m in CHORUS}
    busy_gated = {m: [s["quiet_per_hour"]["null_busy"] for row in r["learned"][m]
                      for s in row["gated"]["per_seed"]] for m in CHORUS}
    quiet_coact = [row["gated"]["quiet_per_hour"]["null_quiet"] for row in r["hand"]["coact"]]
    busy_coact = [row["gated"]["quiet_per_hour"]["null_busy"] for row in r["hand"]["coact"]]
    busy_sce = [row["gated"]["quiet_per_hour"]["null_busy"] for row in r["hand"]["sce"]]
    quiet_budget = [run.meta["budgets"][str(h)]["quiet_per_hour"] for h in run.folds]
    grid = d["threshold_grid"]
    # The replicate's tuning, and the untuned nets against the tuned CoactDetect in both draws.
    rtun = {w: {m: float(np.mean([a - b for a, b in zip(run.repl["learned"][m][w],
                                                         run.repl["learned"][m]["untuned"])]))
                for m in NETS} for w in SEL}
    un_this = run.stats([a - b for a, b in zip(run.net_f1(bn, "untuned"), run.coded_f1("coact", "ungated"))])
    un_repl = run.stats([a - b for a, b in zip(run.repl["learned"][bn]["untuned"],
                                               run.repl["hand"]["coact"]["ungated"])])
    claim(abs(un_this["mean"]) < 0.02 and abs(un_repl["mean"]) < 0.02,
          "the untuned best net is within 0.02 of the tuned CoactDetect in both draws")

    def low_row(e, draw, repl):
        cells = []
        for w in ("untuned",) + SEL:
            x = e["where"].get(w)
            if x is None:
                cells.append("—")
                continue
            what = ("failed to train" if x["failed"] else
                    "no calls" + (f" at threshold {grid[r['learned'][e['model']][e['fold']]['gated']['per_seed'][e['seed']]['threshold_index']]:.4f}"
                                  if (w == "gated" and not repl) else "")
                    if x["no_calls"] else "")
            cells.append(f"{num(x['f1'], 3)}" + (f" <span class=dim>({esc(what)})</span>" if what else ""))
        return [draw, f"<code>{esc(e['model'])}</code>", fold_label(e["fold"]),
                f"{e['seed'] + 1} of 5"] + cells

    low_table = tcap(4, f"Every net refit that scored below {LOW_F1:g} F1 on its held-out fold, in "
                        "both draws, by the selection that scored it. \"Failed to train\": one long "
                        "call per recording, so an event or two found at perfect precision and "
                        "almost no recall. \"No calls\": nothing called at the one threshold the "
                        "selection chose on the inner fits; an F1 with no calls counts as 0.") + table(
        ["draw", "net", "fold", "training seed", "untuned", "F1 alone", "under the budget"],
        [low_row(e, "this run", False) for e in lows] + [low_row(e, "replicate", True) for e in rlows],
        "Table 4: refits below 0.2 F1")
    over_rows = "".join(
        f"<li><code>{esc(m)}</code>: {sum(over[m])} of {sum(len(row['gated']['per_seed']) for row in r['learned'][m])} "
        f"(per fold {', '.join(str(v) for v in over[m])}).</li>" for m in NETS)
    P.append(f"""
<h2 id="checks">10. Tuning, failed refits and false alarms</h2>
<p><b>Tuning moved the nets by little, and not always up</b> (<a href="#fig14">Figure 14, tuned
minus untuned</a>): in this run no net's mean moved by more than
{max(abs(tun[w][m]['mean']) for w in SEL for m in NETS):.2f} F1 either way. On F1 alone, tuned minus
untuned is {', '.join(f'<code>{m}</code> {signed(tun["ungated"][m]["mean"])}' for m in NETS)} in this
run, and {', '.join(f'<code>{m}</code> {signed(rtun["ungated"][m])}' for m in NETS)} in the
replicate, where <code>{esc(bn)}</code>'s figure includes the two refits that failed to train.
Under the budget the comparison is not like for like: the tuned configuration is held to the budget and
the untuned one is not, so the difference ({', '.join(f'<code>{m}</code> {signed(tun["gated"][m]["mean"])}' for m in NETS)})
mixes what tuning gained with what the budget cost.</p>
<p><b>The earlier {signed(earlier)} lead was not lost to the nets' tuning.</b> Untuned,
<code>{esc(bn)}</code> is already within 0.02 F1 of the tuned CoactDetect on this simulator:
{signed(un_this['mean'])} in this run and {signed(un_repl['mean'])} in the replicate. Two things
changed together between the earlier comparison and this one, the simulator and CoactDetect's own
tuning (goal 1's sliding values and this run's search), and this run cannot separate them.</p>
{figure(14, "Tuned minus untuned, per outer fold", fig_tuning(run),
        "Each dot is one outer fold: the net's held-out F1 at the chosen configuration minus at its "
        "untuned one in this run, both means over 5 refits, every refit counted; the bar is the mean of four; a "
        f"ringed dot is a fold where either side holds a refit below {LOW_F1:g} F1 (Table 4). Under "
        "the budget, the tuned configuration is held to the budget and the untuned one is not. Right "
        "of zero, tuning helped.")}
<p><b>Refits below {LOW_F1:g} F1.</b> Every refit was kept in every mean on this page except where
section 6 says otherwise. In this run {len(lows)} of {n_refits} distinct refits scored below
{LOW_F1:g} F1 (the {n_refits} are scored {n_scored} times, since each is scored at every selection that
chose it), and every other scored at least {num(run.lowest_other_refit(), 2)}; in the replicate,
{len(rlows)} did, all in chorus nets, and its lowest other refit scored
{num(run.lowest_other_refit(True), 2)}. Table 4 lists them. That is about
{(len(lows) + len(rlows)) / (2 * n_refits):.0%} of refits across the two draws. No rule fixed before
seeing the held-out scores picks out exactly these refits: the threshold picker's own warning, raised
when it chooses the bottom of its grid, also fires on healthy refits.</p>
{low_table}
<p><b>False alarms on held-out recordings.</b> The budget binds the nets mainly on the empty recordings
at the quiet background, where it allowed {min(quiet_budget):.1f} to {max(quiet_budget):.1f} false
alarms per hour: there the chorus nets' refits chosen under the budget fired
{min(min(v) for v in quiet_gated.values()):.1f} to {max(max(v) for v in quiet_gated.values()):.1f}, and
CoactDetect {min(quiet_coact):.1f} to {max(quiet_coact):.1f}. In the probe the same refits fired
{min(min(v) for v in probe_gated.values()):.0f} to {max(max(v) for v in probe_gated.values()):.0f}
per hour (mean of the two backgrounds; median
{float(np.median([x for v in probe_gated.values() for x in v])):.0f}), against CoactDetect's
{min(probe_coact):g} to {max(probe_coact):g}; across the five refits of one chorus-net choice the probe
rate at one background differs by up to {spread_chorus:.0f} false alarms per hour. The nets were
trained on recordings containing this same probe, labeled as a negative, so a low probe rate shows they
learned that pattern, not that they resist a busier field in general (section 11). On the empty
recordings at the busy background, which do not gate, the chorus nets fired
{min(min(v) for v in busy_gated.values()):.1f} to {max(max(v) for v in busy_gated.values()):.1f} per
hour, CoactDetect {min(busy_coact):.1f} to {max(busy_coact):.1f}, and binned SCE
{min(busy_sce):.1f} to {max(busy_sce):.1f}. Among the {n_refits_gated} refits of nets chosen under the
budget, these exceeded it on the held-out fold:</p>
<ul>{over_rows}</ul>
<p>A net over the budget calls more freely than the budget allows, which tends to favor its F1.</p>
""")

    part = open_items.get("participation", "")
    claim("0.18" in part and "0.1818" in part, "the open participation item is the 18% level")
    P.append(f"""
<h2 id="limits">11. Limits</h2>
<ul class=resid>
<li><b>Baseline periods only, fast stream only.</b> The project lead's decision of 2026-09-17 for this
run. The bench is fitted to the baseline periods of the fast stream, so nothing here says how any
detector behaves during drug treatment or on the slow stream.</li>
<li><b>The bench's fitted values were measured on data with a known, uncleared contamination.</b> The
bench was fitted to an export folder, the lab's exported per-cell event lists. In a few ROIs of that
folder, motion correction clamped the signal to its minimum value, and the lab's event extraction
recorded firings on the steps in and out of it: about 0.03% of firings. Re-measuring the bench on a
corrected folder moved every value by less than its own bootstrap interval (the spread of the value
over resampled recordings), a check with little power against an effect that small. Moving the bench
to the corrected folder has not been decided. This page lists the contamination as a limit because the
project lead asked for exactly that in the brief for this report (2026-09-19); listing it does not show
that the effect is negligible.</li>
<li><b>One of the bench's values sits on the edge of its own measured interval, and the decision on it
is open.</b> The bench declares its middle participation level as 0.18, which plants 6 of 33 ROIs,
18.18%. The real recordings measure 19.05%, with a 95% interval whose lower end is 18.18%: the planted
count sits on the interval's edge and the declared 0.18 just outside it. Changing it would move every
bench number, so it waits on the project lead.</li>
<li><b>Simulation only.</b> Every number is on simulated recordings. The bench is measured from real
ones, but a detector that wins here has not thereby been shown to win on real data.</li>
<li><b>The budget is CoactDetect's shape and a declared margin.</b> It is 1.6 times the reference
CoactDetect's own rate on each gate (section 4.4); the 1.6 was declared, not measured, and no
sensitivity to it was run, though every under-budget verdict rests on it.</li>
<li><b>What the nets were trained on.</b> Every training recording holds the same probe, at the same
place and rate, and six distractors built exactly as planted events joined by 18% of the ROIs are, and
the nets were trained to call neither. So the nets met the probe in training and the coded detectors
did not, and the nets were fitted to patterns identical to planted events but labeled the opposite
way. The effect of either on the results was not measured.</li>
<li><b>The merge gap was tuned for one side only</b> (section 7), and "matched" is nominal. There are
three merge rules: a net merges runs of frames above its threshold; CoactDetect and LoCo merge the
positions of a sliding window, so events up to about the gap plus the window's width apart can fuse;
binned SCE merges by the times of the firings. The same number of seconds drives different
operations.</li>
<li><b>The nets were not checked on crowded recordings.</b> Every net number was measured on events at
least {bench.BENCH_RECORDING['min_sep_sec']:g} s apart.</li>
<li><b>The two sides learn from different amounts of data.</b> A net fits 10 of the 72 training
recordings and, on F1 alone, picks its threshold on 2; a coded configuration, threshold included, is
scored on all 72. That handicaps the nets. On F1 alone the net's threshold is also picked on F1 pooled
over both backgrounds, while every selection and score on this page averages the two backgrounds'
F1.</li>
<li><b>The vote-pooling nets standardize each ROI over the whole input.</b> They trained on crops of
about 7 minutes and are scored on the whole 45-minute recording, probe included, so the statistics they
standardize by differ between training and scoring.</li>
<li><b>The hit tolerance was set for the coded detectors.</b> The {score.TOL_SEC:g} s at which scores
stop changing was measured for the coded detectors at their shipped configurations, not at the tuned
ones here and not for the nets.</li>
<li><b>Four outer folds</b>, so every paired comparison rests on 3 degrees of freedom, and the folds
share training data (section 4.1).</li>
<li><b>The coded searches move one parameter at a time</b> and can end in different places depending
on the path taken; a search under the budget can even end higher than the same search without it,
because the budget changes which steps it can take.</li>
<li><b>Chosen values at the top of their grid.</b> On F1 alone every coded detector with a merge gap
chose the top of its grid (Table 3). Goal 1 had tried CoactDetect's and LoCo's merge gap at 16 s and
its crowded check refused it, so 8 s is the most those two could take. SPIKE-synch's longest allowed
gap within an event and locust's minimum distance between calls, both merge-like, also sit at the top
of their grids on F1 alone.</li>
<li><b>Tuning the fewest ROIs a coded detector will call an event on (<code>min_rois</code>) can fit
it to the bench's planted participation levels</b>, so its tuned value is a fact about this
simulator.</li>
<li><b>One training run per seed, on one GPU per workstation.</b> Re-scoring on a CPU moved nets by up
to {repro_net:.4f} F1 per refit (section 7). Only one earlier check compared training on two machines,
and the second machine had uncommitted changes, so its difference of up to about 0.02 F1 per fold mixes
machine and code; that is the size of the margins above.</li>
</ul>
""")

    n_jobs = len(run.ran)
    P.append(f"""
<h2 id="where">12. Where everything is</h2>
<ul>
<li><b>This report</b>: <code>&lt;darkroom&gt;/bugarach/{DARKROOM_FOLDER}/report/index.html</code>,
where <code>&lt;darkroom&gt;</code> is the project's shared output folder, and
<code>report.html</code> beside the run's summaries in the repository. Its review record is
<code>docs/reviews/fair-comparison-2026-09-19.md</code>.</li>
<li><b>The replicate's own report</b>, from the second workstation (WSMIP065; this run is
WSMIP064): <code>{REPLICATE_PAGE}</code>.</li>
<li><b>The architecture drawings</b> of the four nets are drawn with draughtsman
(github.com/syncytium2/draughtsman, a sibling project whose code this repository carries a copy of),
one specification per model traced from the code, all at one scale:
<code>&lt;darkroom&gt;/bugarach/2026-09-19-comparison-architectures/index.html</code>, and in the
repository as <code>{ARCH_REPO}</code> on pull request #660, not yet merged when this page was
built.</li>
<li><b>On a narrow screen</b>, each figure scrolls sideways inside its own frame.</li>
<li><b>The run's summaries, in the repository</b>:
<code>docs/learned/tuned_vs_coact/fair_comparison_2026_09_18/</code>. It holds the declaration
(<code>meta.json</code>), <code>results.json</code>, the selections, configurations and job log, and
this report's derived files: <code>crowded_check.json</code>, <code>fold_draws.json</code>,
<code>merge_gap.json</code>, <code>breakdown.json</code> and <code>replicate_summary.json</code>.
Personal paths in them are written as <code>%USERPROFILE%</code> and
<code>&lt;darkroom&gt;</code>.</li>
<li><b>Everything else, in the darkroom</b>:
<code>&lt;darkroom&gt;/bugarach/{DARKROOM_FOLDER}/results/</code>. It holds the same summaries
unedited, the chosen settings and models (<code>chosen/</code>), every fitted model
(<code>fits.tar.gz</code>), every score table (<code>scores.tar.gz</code>, 1.1 GB unpacked) and the
run's log.</li>
<li><b>The code that ran</b>: <code>tools/tune_learned_vs_coact.py</code> on branch
<code>tune-bench-comparison</code> at <code>{esc(run.meta['started']['git']['commit'][:7])}</code>,
from a clean tree. The evidence tools are <code>tools/crowded_check_fair_comparison.py</code> and
<code>tools/fair_comparison_evidence.py</code>. To rebuild a net outside the trainer, go through the
registry, <code>ARCHITECTURES[name].make()</code>, as the trainer and <code>checkpoint.load</code> do:
calling <code>build_chorus_norm()</code> or <code>build_chorus_gain_norm()</code> directly builds plain
<code>chorus</code>, silently.</li>
<li><b>The records behind section 11</b>: the contamination is decision 3 of
<code>HANDOFF-slow-comodulation-on-the-de-pinned-export.md</code>; the re-measurement is commit
2120516 on branch <code>tune-bench-comparison</code>
(<code>HANDOFF-workstation-tuning.md</code>), not on <code>main</code>; the participation item is in
the run's declaration.</li>
<li><b>The size of the run</b>: {n_jobs:,} jobs, with no errors, over {wall:.1f} hours of wall time:
1 reference measurement; {run.n_stage('search')} coded-detector search jobs, 6 detectors × 4 outer
folds, each running both selections, on CPUs; {run.n_stage('inner'):,} inner fits of nets, each
shared by the two outer folds that train on its pair of folds;
and {run.n_stage('outer')} outer refits (the chosen and untuned configurations at 5 training seeds),
on one GPU. {r['cpu_hours_training']:.1f} hours of the run were spent training nets.</li>
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
    ver = provenance.code_version() or "unknown"
    meta = ('<meta name="description" content="The fair comparison of tuned learned detectors against '
            'tuned coded detectors on the project\'s simulator, written for a reader new to it.">\n'
            f'<meta name="generator" content="tools/build_fair_comparison_report.py {esc(ver)}">\n'
            '<meta name="author" content="the bugarach project">\n'
            f'<meta name="date" content="{time.strftime("%Y-%m-%d")}">\n')
    html = page("Tuned nets against tuned coded detectors",
                EXTRA_CSS + body(run) + provenance_line(run))
    html = html.replace('<meta name="viewport"', meta + '<meta name="viewport"', 1)
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
