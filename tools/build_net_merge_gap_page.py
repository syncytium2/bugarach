#!/usr/bin/env python3
"""Write the page on the nets' merge gap, tuned like any other setting: the fair comparison's addendum.

    python tools/build_net_merge_gap_page.py                     # darkroom only
    python tools/build_net_merge_gap_page.py --also docs/learned/tuned_vs_coact/fair_comparison_2026_09_18

Reads ``net_merge_gap.json`` and ``replicate_net_merge_gap.json`` (``tools/tune_net_merge_gap.py``)
from ``--run`` (default ``docs/learned/tuned_vs_coact/fair_comparison_2026_09_18/``). Writes
``merge-gap.html`` beside the fair comparison's report in
``darkroom()/2026-09-18-fair-comparison-run/report/`` (sapper SAP006) and ``net_merge_gap.html`` to
``--also``, each linking to the report copy that sits beside it.

The page kit is ``tools/build_surrogate_report.py``'s and the axis helpers are the report's, imported
rather than copied. Every sentence stating a fact about these data is computed, and a directional one
sits behind ``claim``, which stops the build when it stops being true.

**What the murderboard of 2026-09-19 changed** (``docs/reviews/net_merge_gap_2026-09-19.md``), because
each of these is a way the first draft read better than the data warranted: the set-aside treatment is
applied to the as-run baseline as well as the tuned one, so the gap's own contribution is visible; the
held-out F1 of every gap is drawn, which shows that every chosen gap is a boundary the crowded check
imposed rather than an optimum; the crowded cost of the settings that were *accepted* is reported
beside the refusals; and the noise scale is named for what its source measures — two draws on two
machines, with a systematic shift in the second draw's favour.
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

from build_fair_comparison_report import (DARKROOM_FOLDER, GREY, NET_INK, REPL_INK,  # noqa: E402
                                          SEL_NAME, and_join, claim, fmt_diff, fold_label, signed,
                                          tnum, x_axis)
from build_surrogate_report import Svg, esc, figure, page, table  # noqa: E402
from fair_comparison_evidence import LOW_F1  # noqa: E402
from tune_net_merge_gap import _paired  # noqa: E402

from bugarach import provenance  # noqa: E402

DEFAULT_RUN = REPO / "docs" / "learned" / "tuned_vs_coact" / "fair_comparison_2026_09_18"
DRAWS = (("this", "net_merge_gap.json", "this run's draw"),
         ("replicate", "replicate_net_merge_gap.json", "the replicate's draw"))
NETS = ("chorus_norm", "chorus_gain_norm", "line_length", "tube")
CHORUS = ("chorus_norm", "chorus_gain_norm")
SEL = ("ungated", "gated")
#: The rows of the two margin figures: a choice, and whether refits under LOW_F1 are set aside. The
#: baseline carries the set-aside too, or the tuned row's lead would be the exclusion rule's.
ROWS = (("as_run", False, "as run, 2 s"), ("as_run", True, "as run, low refits set aside"),
        ("config_kept", False, "gap tuned"), ("config_kept", True, "tuned, low refits set aside"))
NOISE_INK = "#ececec"
NOTE_INK = "#595959"      # 7:1 on white; the 10 px grey of the first draft was 3.45:1
SMALL = 11                # the page's own legibility floor
#: The report's Figure 8 measures this between two draws that differ in recordings AND machine.
NOISE_SOURCE = ("the median absolute move of a net's held-out F1 between the two draws, measured in "
                "the replicate's own report; the draws differ in their recordings and in the machine "
                "that trained them, which no measurement here separates")


def load(run: Path) -> dict:
    """Whichever draws are committed, in DRAWS order. One draw is a page; the page then says so."""
    got = {k: json.loads((run / f).read_text(encoding="utf-8")) for k, f, _ in DRAWS
           if (run / f).exists()}
    if "this" not in got:
        raise SystemExit(f"{run / DRAWS[0][1]} is not there: nothing to write about")
    return got


def draws(docs):
    return [(k, f, name) for k, f, name in DRAWS if k in docs]


def first(docs):
    return docs[draws(docs)[0][0]]


def both(docs):
    return "both draws" if len(docs) > 1 else "this draw"


def name_of(k):
    return dict((kk, n) for kk, _, n in DRAWS)[k]


def rows_of(doc, m, w):
    return doc["nets"][m][w]


# ---- the numbers ---------------------------------------------------------------------------------

def kept_refits(entry):
    """The refits at or above the report's LOW_F1 set-aside. Below it sits an empty band: across
    every refit of both draws the low scores are 0.0 and 0.125 and the lowest other is 0.39."""
    h = entry.get("heldout") if isinstance(entry, dict) else None
    return None if h is None else [x for x in h["per_seed"] if x["f1"] >= LOW_F1]


def low_refits(doc, m, w, variant):
    out = []
    for r in rows_of(doc, m, w):
        h = r[variant].get("heldout")
        out.append(0 if h is None else sum(1 for x in h["per_seed"] if x["f1"] < LOW_F1))
    return out


def low_kinds(docs):
    """How the refits under LOW_F1 divide: a collapsed training, or no calls at the chosen threshold.
    The run records both; they are not the same failure and the page must not merge them."""
    collapsed = nocall = 0
    for k in docs:
        for m in NETS:
            for w in SEL:
                for r in rows_of(docs[k], m, w):
                    for v in ("as_run", "config_kept"):
                        h = r[v].get("heldout")
                        if h is None:
                            continue
                        for x in h["per_seed"]:
                            if x["f1"] >= LOW_F1:
                                continue
                            if x.get("failed_training_signature"):
                                collapsed += 1
                            else:
                                nocall += 1
    return collapsed, nocall


def margins(doc, m, w, variant, without_low=False):
    """Net minus CoactDetect per fold, held-out F1; None where the choice has no refits, or where
    every refit of that fold is under LOW_F1."""
    coact = doc["coact"]["f1"][w]
    out = []
    for r in rows_of(doc, m, w):
        e = r[variant]
        keep = kept_refits(e)
        if keep is None:
            out.append(None)
        elif without_low:
            out.append(None if not keep
                       else float(np.mean([x["f1"] for x in keep])) - coact[r["outer_fold"]])
        else:
            out.append(e["heldout"]["f1_mean"] - coact[r["outer_fold"]])
    return out


def stats(doc, m, w, variant, without_low=False):
    d = margins(doc, m, w, variant, without_low)
    if any(v is None for v in d):
        return None
    if not without_low:
        got = doc["comparisons"][w].get(f"{m} {variant} - coact")
        if got is not None:
            return got
    return _paired(d, [0.0] * len(d))


def gaps(doc, m, w, variant="config_kept"):
    return [r[variant]["gap_sec"] for r in rows_of(doc, m, w)]


def crowded_cost(doc, m, w):
    """What the chosen setting itself loses on the crowded recordings, measured on the outer refits
    against the as-run choice. Positive means the tuned gap is worse there."""
    out = []
    for r in rows_of(doc, m, w):
        c = r["config_kept"]
        if c.get("outer_crowded_f1") is None:
            out.append(None)
        else:
            out.append(c["outer_crowded_f1_as_run"] - c["outer_crowded_f1"])
    return out


def all_costs(docs):
    return [v for k in docs for m in NETS for w in SEL for v in crowded_cost(docs[k], m, w)
            if v is not None]


def fmt_gaps(gs):
    return ", ".join(f"{g:g}" for g in gs) + " s"


def pct(x):
    return f"{x:.0%}"


# ---- figures ------------------------------------------------------------------------------------

def key_row(svg, x, y, draw, text, width=None):
    draw(x, y)
    svg.text(x + 14, y + 4, text, size=12)
    return x + (width or 0)


def fig_margins(docs, w) -> Svg:
    """Per fold, net minus CoactDetect, for the two chorus nets: as run and with the gap tuned, each
    counting every refit and then with the refits under LOW_F1 set aside."""
    rows = [(m, v, low, lab) for m in CHORUS for v, low, lab in ROWS]
    top, rh, gutter = 54, 30, 108
    yb = top + len(rows) * rh
    svg = Svg(900, yb + 150, f"The two chorus nets minus CoactDetect per outer fold, {SEL_NAME[w]}, "
                             "as run and with the merge gap tuned, each counting every refit and "
                             "then with the refits under 0.2 F1 set aside, for each draw")
    vals = [v for d in docs.values() for m, var, low, _ in rows
            for v in margins(d, m, w, var, low) if v is not None]
    # The axis holds the folds whose refits all trained; a collapsed fold is written in the gutter to
    # its left, so one fold a quarter of an F1 out cannot flatten every margin this page is about.
    inliers = []
    for d in docs.values():
        for m, var, low, _ in rows:
            nlow = low_refits(d, m, w, var)
            for j, v in enumerate(margins(d, m, w, var, low)):
                if v is not None and (low or not nlow[j]):
                    inliers.append(v)
    inliers = inliers or vals
    step = 0.02 if max(inliers) - min(inliers) <= 0.1 else 0.04
    lo = min(-step, math.floor(min(inliers) / step) * step)
    hi = max(step, math.ceil(max(inliers) / step) * step)
    ticks = [round(v, 2) for v in np.arange(lo, hi + 1e-9, step)]
    noise = first(docs)["noise_f1"]
    # A and B carry the same axis, so they get the same width: a band 21% wider on the left is a
    # comparison the eye gets wrong before it reads either label.
    panels = ([((372, 552), draws(docs)[0], "A")] if len(docs) == 1 else
              [((372, 552), draws(docs)[0], "A"), ((700, 880), draws(docs)[1], "B")])
    for (x0, x1), (k, _, name), letter in panels:
        X = lambda v, a=x0, b=x1: a + (v - lo) / (hi - lo) * (b - a)   # noqa: E731
        svg.text((x0 + x1) / 2, 24, f"{letter}.  {name[0].upper() + name[1:]}", anchor="middle",
                 size=13, weight="bold")
        svg.rect(X(-noise), top - 6, X(noise) - X(-noise), yb - top + 6, fill=NOISE_INK)
        x_axis(svg, X, x0, x1, yb, ticks, fmt_diff, "net minus CoactDetect, held-out F1",
               zero_rule=True, top=top - 6)
        for i, (m, var, low, _) in enumerate(rows):
            yc = top + i * rh + rh / 2
            d = margins(docs[k], m, w, var, low)
            nlow = low_refits(docs[k], m, w, var)
            ink = GREY if var == "as_run" else NET_INK
            off = []
            for j, v in enumerate(d):
                if v is None:
                    continue
                y = yc + (j - 1.5) * 3.4
                if v < lo:
                    off.append(v)
                    continue
                svg.circle(X(v), y, 3.4, fill=ink)
                if nlow[j] and not low:
                    svg.circle(X(v), y, 7.5, fill="none", stroke=ink)
            got = [v for v in d if v is not None]
            mean = float(np.mean(got)) if len(got) == len(d) else None
            if mean is not None and mean >= lo:
                svg.line(X(mean), yc - 11, X(mean), yc + 11, stroke=ink, w=2.4)
            # Two short lines in the gutter, never one long one: the row label sits just left of it.
            notes = []
            if off:
                notes.append("◀ " + ", ".join(f"{v:.3f}" for v in off).replace("-", "−"))
                if mean is not None and mean < lo:
                    notes.append(f"mean {mean:.3f}".replace("-", "−"))
            elif mean is None:
                notes.append(f"{len(got)} of {len(d)} folds")
                notes.append("refitted, so no mean")
            for n_, txt in enumerate(notes):
                # In the row's own colour: grey means as-run everywhere else in this figure, so a
                # grey value on a blue row read as a fold of the wrong series.
                svg.text(x0 - 6, yc + (1 if len(notes) == 1 else -3 + n_ * 13), txt, anchor="end",
                         size=SMALL, fill=ink if off else NOTE_INK)
    # The net names head their group; the rows carry only what distinguishes them, which keeps the
    # longest label inside the label column instead of off the left edge.
    for i, (m, var, low, lab) in enumerate(rows):
        yc = top + i * rh + rh / 2
        svg.text(372 - gutter - 6, yc + 4, lab, anchor="end", size=12)
        if i % len(ROWS) == 0:
            svg.text(20, yc - 6, m, size=12, weight="bold")
            if i:
                svg.line(20, top + i * rh, 890, top + i * rh, stroke="#bbb", dash="3 3")
    y = yb + 74
    svg.circle(30, y, 3.4, fill=GREY)
    svg.text(40, y + 4, "one outer fold, as run", size=12)
    svg.circle(210, y, 3.4, fill=NET_INK)
    svg.text(220, y + 4, "one outer fold, re-selected", size=12)
    svg.line(410, y - 8, 410, y + 8, stroke=NET_INK, w=2.4)
    svg.line(404, y - 8, 404, y + 8, stroke=GREY, w=2.4)
    svg.text(420, y + 4, "mean of 4 folds, in the row's colour", size=12)
    svg.rect(660, y - 8, 22, 16, fill=NOISE_INK)
    svg.text(690, y + 4, f"±{noise:.3f} F1, the between-draw scale", size=12)
    y += 22
    svg.circle(30, y, 3.4, fill=NET_INK)
    svg.circle(30, y, 7.5, fill="none", stroke=NET_INK)
    svg.text(44, y + 4, f"a fold holding a refit under {LOW_F1:g} F1, counted in that row's mean; "
                        "in these panels every such fold lies left of the axis and is written "
                        "there instead", size=12)
    svg.text(30, y + 20, "◀ a fold, and where needed a mean, beyond the axis, in the row's colour",
             size=12, fill=NOTE_INK)
    svg.line(560, y + 12, 560, y + 26, dash="4 3")
    svg.text(570, y + 24, "zero: the net and CoactDetect tie; right of it the net is ahead", size=12)
    y += 22
    svg.text(30, y + 22, "Rows are grouped by net; the dashed rule separates them.", size=12,
             fill=NOTE_INK)
    return svg


def fig_curve(docs, w) -> Svg:
    """Held-out F1 against merge gap, averaged over folds, with the chosen gap marked: the shape the
    single chosen point cannot show, and the reason every choice is a boundary."""
    grid = first(docs)["gaps_sec"]
    top, h_ = 56, 250
    yb = top + h_
    svg = Svg(900, yb + 132, "Held-out F1 against the merge gap for the two chorus nets, averaged "
                             f"over the four outer folds, {SEL_NAME[w]}, with the chosen gap marked, "
                             "for each draw")
    curves = {}
    for k in docs:
        for m in CHORUS:
            per = [r["config_kept"].get("heldout_f1_by_gap") for r in rows_of(docs[k], m, w)]
            if any(c is None for c in per):
                continue
            curves[(k, m)] = [float(np.mean([c[f"{g:g}"] for c in per])) for g in grid]
    vals = [v for c in curves.values() for v in c]
    lo, hi = math.floor(min(vals) * 50) / 50, math.ceil(max(vals) * 50) / 50
    panels = ([((360, 860), draws(docs)[0], "A")] if len(docs) == 1 else
              [((360, 590), draws(docs)[0], "A"), ((650, 880), draws(docs)[1], "B")])
    inks = {CHORUS[0]: NET_INK, CHORUS[1]: REPL_INK}
    for (x0, x1), (k, _, name), letter in panels:
        X = lambda i, a=x0, b=x1: a + i * (b - a) / (len(grid) - 1)     # noqa: E731
        Y = lambda v: yb - (v - lo) / (hi - lo) * h_                    # noqa: E731
        svg.text((x0 + x1) / 2, 24, f"{letter}.  {name[0].upper() + name[1:]}", anchor="middle",
                 size=13, weight="bold")
        svg.line(x0, yb, x1, yb)
        for i, g in enumerate(grid):
            svg.line(X(i), yb, X(i), yb + 4)
            svg.text(X(i), yb + 18, f"{g:g}", anchor="middle", size=SMALL)
        svg.text((x0 + x1) / 2, yb + 38, "merge gap (s), the eight grid values, evenly spaced",
                 anchor="middle", size=12)
        for v in np.arange(lo, hi + 1e-9, 0.02):
            svg.line(x0, Y(v), x1, Y(v), stroke="#eee")
            svg.text(x0 - 6, Y(v) + 4, f"{v:.2f}", anchor="end", size=SMALL)
        for m in CHORUS:
            c = curves.get((k, m))
            if c is None:
                continue
            for i in range(len(grid) - 1):
                svg.line(X(i), Y(c[i]), X(i + 1), Y(c[i + 1]), stroke=inks[m], w=1.8)
            for g in sorted(set(gaps(docs[k], m, w))):
                i = grid.index(g)
                svg.circle(X(i), Y(c[i]), 4.2, fill=inks[m])
    svg.text(30, top + 4, "held-out F1,", size=12)
    svg.text(30, top + 20, "mean over folds", size=12)
    y = yb + 66
    for i, m in enumerate(CHORUS):
        svg.line(30, y + i * 20, 56, y + i * 20, stroke=inks[m], w=1.8)
        svg.circle(43, y + i * 20, 4.2, fill=inks[m])
        svg.text(64, y + i * 20 + 4, f"{m}", size=12)
    svg.text(230, y + 4, "a dot marks a gap some fold chose", size=12)
    svg.text(230, y + 24, "Read as a diagnostic, not a selection rule: these are held-out scores, "
                          "and choosing on them would use the fold held out.", size=12, fill=NOTE_INK)
    return svg


def fig_gaps(docs) -> Svg:
    """Which gap each fold chose, and how many folds had a wider setting refused at each gap."""
    grid = first(docs)["gaps_sec"]
    rows = [(m, w) for m in NETS for w in SEL]
    top, rh = 70, 32
    yb = top + len(rows) * rh
    svg = Svg(900, yb + 126, "For every net and selection, the merge gap each outer fold chose and "
                             "the number of folds in which a setting at each gap was refused by the "
                             "crowded-recording check, for each draw")
    panels = ([((330, 570), draws(docs)[0], "A")] if len(docs) == 1 else
              [((330, 570), draws(docs)[0], "A"), ((640, 880), draws(docs)[1], "B")])
    coact_gap = sorted({g for d in docs.values() for w in SEL for g in d["coact"]["merge_gap_sec"][w]})
    claim(coact_gap == [8.0], "CoactDetect chose 8 s in every fold, selection and draw")
    for (x0, x1), (k, _, name), letter in panels:
        step = (x1 - x0) / len(grid)
        X = lambda i, a=x0, s=step: a + (i + 0.5) * s                   # noqa: E731
        svg.text((x0 + x1) / 2, 24, f"{letter}.  {name[0].upper() + name[1:]}", anchor="middle",
                 size=13, weight="bold")
        ci = grid.index(8.0)
        svg.rect(X(ci) - step / 2, top - 8, step, yb - top + 8, fill=NOISE_INK)
        svg.text(X(ci), top - 14, "CoactDetect: 8 s", anchor="middle", size=SMALL)
        svg.text(X(grid.index(2.0)), top - 30, "as run: 2 s", anchor="middle", size=SMALL)
        svg.line(x0, yb, x1, yb)
        for i, g in enumerate(grid):
            svg.line(X(i), yb, X(i), yb + 4)
            svg.text(X(i), yb + 18, f"{g:g}", anchor="middle", size=SMALL)
        svg.text((x0 + x1) / 2, yb + 38, "merge gap (s), the eight grid values, evenly spaced",
                 anchor="middle", size=12)
        for r, (m, w) in enumerate(rows):
            yc = top + r * rh + rh / 2
            chosen = gaps(docs[k], m, w)
            refused: dict = {}
            for row in rows_of(docs[k], m, w):
                for g in {x["gap_sec"] for x in row["config_kept"]["refused_by_crowded"]}:
                    refused[g] = refused.get(g, 0) + 1
            # Chosen on the row's line, refused on a lane below it: the two counts are different
            # facts about the same gap and ran together when they shared a baseline.
            for i, g in enumerate(grid):
                n = chosen.count(g)
                if n:
                    svg.circle(X(i), yc - 4, 3.6, fill=NET_INK)
                    if n > 1:
                        svg.text(X(i) + 6, yc - 1, str(n), size=SMALL, fill=NET_INK)
                if refused.get(g):
                    svg.text(X(i), yc + 12, f"×{refused[g]}", anchor="middle", size=SMALL,
                             fill=REPL_INK)
    for r, (m, w) in enumerate(rows):
        yc = top + r * rh + rh / 2
        svg.text(320, yc + 4, f"{m}, {SEL_NAME[w]}", anchor="end", size=12)
        if r and r % len(SEL) == 0:
            svg.line(20, top + r * rh, 890, top + r * rh, stroke="#bbb", dash="3 3")
    y = yb + 66
    svg.circle(30, y, 3.6, fill=NET_INK)
    svg.text(42, y + 4, "a gap chosen, with the number of folds that chose it where more than one",
             size=12)
    svg.text(30, y + 26, "×n", size=SMALL, fill=REPL_INK)
    svg.text(52, y + 30, "a setting at that gap beat the chosen one on the inner fits in n folds and "
                         f"was refused: it lost more than {first(docs)['max_crowded_drop']:g} mean F1",
             size=12)
    svg.text(52, y + 48, "on the crowded recordings. Under the budget a setting is a gap and a "
                         "threshold together, so a refusal can sit at the chosen gap.", size=12)
    return svg


def fig_crowded(docs, coact_crowded) -> Svg:
    """Two things the prose can only summarise: what each chosen gap costs its own net on the crowded
    recordings, against the check's limit; and where the tuned net stands against CoactDetect there."""
    drop = first(docs)["max_crowded_drop"]
    rows = [(m, w) for m in NETS for w in SEL]
    top, rh = 56, 30
    yb = top + len(rows) * rh
    svg = Svg(900, yb + 118, "For every net and selection, what the chosen merge gap costs on the "
                             "crowded recordings against the same net at 2 s, and the same net's "
                             "crowded F1 against CoactDetect, one mark per outer fold per draw")
    cost, head = {}, {}
    for k in docs:
        for m, w in rows:
            for r in rows_of(docs[k], m, w):
                c = r["config_kept"]
                if c.get("outer_crowded_f1") is None:
                    continue
                cost.setdefault((m, w), []).append(c["outer_crowded_f1_as_run"] - c["outer_crowded_f1"])
                ref = coact_crowded.get((r["outer_fold"], w))
                if ref is not None:
                    head.setdefault((m, w), []).append(c["outer_crowded_f1"] - ref)
    for (x0, x1), vals, title, zero, lim in (
            ((330, 560), cost, "A.  Cost to the net's own 2 s", 0.0, drop),
            ((650, 880), head, "B.  The same net minus CoactDetect", 0.0, None)):
        flat = [v for vs in vals.values() for v in vs]
        lo = math.floor(min(flat + [0.0]) / 0.05) * 0.05
        hi = math.ceil(max(flat + [lim or 0.0]) / 0.05) * 0.05
        X = lambda v, a=x0, b=x1, l=lo, h=hi: a + (v - l) / (h - l) * (b - a)   # noqa: E731
        svg.text((x0 + x1) / 2, 24, title, anchor="middle", size=13, weight="bold")
        x_axis(svg, X, x0, x1, yb, [round(v, 2) for v in np.arange(lo, hi + 1e-9, 0.05)], fmt_diff,
               "crowded-recording F1 lost" if lim else "crowded-recording F1, net minus CoactDetect",
               zero_rule=True, top=top - 6)
        if lim:
            svg.line(X(lim), top - 6, X(lim), yb, stroke=REPL_INK, w=1.4, dash="4 3")
            svg.text(X(lim) + 4, top + 6, f"the {lim:g} limit", size=SMALL, fill=REPL_INK)
        for i, key in enumerate(rows):
            yc = top + i * rh + rh / 2
            for j, v in enumerate(vals.get(key, [])):
                svg.circle(X(v), yc + (j % 4 - 1.5) * 3.4, 3.2,
                           fill=REPL_INK if (lim and v > lim) else NET_INK)
    for i, (m, w) in enumerate(rows):
        yc = top + i * rh + rh / 2
        svg.text(320, yc + 4, f"{m}, {SEL_NAME[w]}", anchor="end", size=12)
        if i and i % len(SEL) == 0:
            svg.line(20, top + i * rh, 890, top + i * rh, stroke="#bbb", dash="3 3")
    y = yb + 70
    svg.circle(30, y, 3.2, fill=NET_INK)
    svg.text(42, y + 4, "one outer fold of one draw, eight per row", size=12)
    svg.circle(330, y, 3.2, fill=REPL_INK)
    svg.text(342, y + 4, f"a fold whose cost exceeds the {drop:g} limit (panel A)", size=12)
    svg.text(30, y + 22, "Panel A: right of zero the tuned gap is worse than the net's own 2 s. "
                         "Panel B: right of zero the net beats CoactDetect on these recordings. "
                         "Rows are grouped by net.", size=12, fill=NOTE_INK)
    return svg


# ---- tables -------------------------------------------------------------------------------------

def stat_cell(c, per_fold=None, noise=None, flag=""):
    if c is None:
        got = sum(v is not None for v in per_fold or [])
        return (f"no mean: {got} of {len(per_fold)} folds refitted" if per_fold else "not measured")
    # A dagger, not a degree sign: on a page whose rule is that every number carries its unit, "°"
    # after a number reads as a unit before it reads as a footnote.
    mark = "†" if (noise is not None and abs(c["mean"]) < noise) else ""
    return (f"{signed(c['mean'])}{mark}{flag} ({c['folds_ahead']} of {c['folds']}; <i>t</i> "
            f"{tnum(c['t'])}, corrected {tnum(c['t_corrected'])})")


def results_table(docs) -> str:
    noise = first(docs)["noise_f1"]
    drop = first(docs)["max_crowded_drop"]
    rows = []
    for k, _, name in draws(docs):
        d = docs[k]
        for w in SEL:
            for m in NETS:
                cost = [v for v in crowded_cost(d, m, w) if v is not None]
                over = max(cost) if cost else None
                fail_mark = " ⚠" if over is not None and over > drop else ""
                rows.append([
                    name, SEL_NAME[w], m, fmt_gaps(gaps(d, m, w)),
                    stat_cell(stats(d, m, w, "as_run"), noise=noise),
                    stat_cell(stats(d, m, w, "as_run", True), margins(d, m, w, "as_run", True), noise),
                    # The ⚠ belongs to the chosen gap, so it marks every column that uses it.
                    stat_cell(stats(d, m, w, "config_kept"), noise=noise, flag=fail_mark),
                    stat_cell(stats(d, m, w, "config_kept", True),
                              margins(d, m, w, "config_kept", True), noise, flag=fail_mark),
                    stat_cell(stats(d, m, w, "config_rechosen"),
                              margins(d, m, w, "config_rechosen"), flag=fail_mark),
                    "—" if not cost else f"{max(cost):+.3f}".replace("-", "−")])
    return table(["draw", "selection", "net", "gap chosen, folds 1 to 4", "as run",
                  f"as run, refits under {LOW_F1:g} F1 set aside", "gap tuned",
                  f"gap tuned, refits under {LOW_F1:g} F1 set aside",
                  "gap and configuration re-chosen",
                  "worst crowded cost of the chosen gap, mean F1"], rows,
                 f"Table 1, every net in {both(docs)}")


# ---- the prose, all of it computed ----------------------------------------------------------------

def lede(docs, noise, gained, aside_gained, ahead, n_folds, refusals, costs, drop):
    claim(all(v > 0 for v in gained.values()), "tuning the gap helps every chorus net in every draw")
    claim(refusals == 1.0, "every choice had a wider setting refused by the crowded check")
    lo, hi = min(gained.values()), max(gained.values())
    alo, ahi = min(aside_gained.values()), max(aside_gained.values())
    return (
        "A detector's <b>merge gap</b> is how close two of its calls may be before they are combined "
        "into one. The coded detectors' searches tuned theirs and the nets ran at a fixed 2 s; this "
        "page tunes the nets' by the same rules, on their training folds, without retraining. "
        f"<b>It is worth about one noise unit, and the check that bounds it refused a wider gap every "
        f"time.</b> Each chorus net gains {lo:.3f} to {hi:.3f} F1 against CoactDetect counting every "
        f"refit, and {alo:.3f} to {ahi:.3f} F1 with the refits under {LOW_F1:g} F1 set aside on both "
        f"sides, against a between-draw scale of {noise:.3f} F1; <code>tube</code> gains a fifth of "
        f"that. In all {len(costs)} choices of {both(docs)} the training folds preferred a still wider "
        f"gap and the crowded-recording check refused it. Under the budget CoactDetect remains ahead "
        f"of every net on average in {both(docs)} and in {n_folds - len(ahead)} of {n_folds} "
        f"net-folds. Two things the reader should carry into the rest: on F1 alone the <b>sign</b> of "
        "the margin depends on whether the refits that failed are set aside, and every gap on this "
        f"page is decided by a {drop:g} F1 allowance the project lead has not signed.")


def question_text(docs, n_fits):
    return (
        "A detector's calls closer together than its <b>merge gap</b> are merged into one (the "
        "report's Figure 3, merging calls). In the fair comparison the coded detectors' searches "
        "tuned that gap and CoactDetect took 8 s in every fold, while the nets decoded at the fixed "
        "2 s their threshold picker returns — the one setting the two sides did not share. What "
        "turns on it: if that fixed 2 s were the nets' handicap, tuning it should close the "
        "shortfall against CoactDetect, and the report's ranking rests on it not being. The report's "
        "own matched-gap re-scoring (its section 7) bounded what the gap could be worth without "
        "letting either side re-choose; the project lead asked for the measurement (2026-09-19).")


def crowded_text(docs, costs, refusals, inner_spread, fails, drop, sce, head, margin, nonmono, n_rows):
    n = len(costs)
    over = [c for c in costs if c > drop]
    claim(refusals == 1.0, "a wider setting was refused in every choice")
    lo_h = min(v for _, v in head)
    hi_h = max(v for _, v in head)
    return (
        f"In every one of the {n} choices the inner fits preferred at least one setting the check "
        "refused, and in every one at least one of those was a wider gap. The bench barely charges "
        "for merging: its planted events are a floor of 120 s apart, so a wider merge there mostly "
        "deletes duplicate calls — held-out F1 is largest at the widest gap in every one of the "
        f"{n_rows} fold-rows, though it dips somewhere along the way in {nonmono} of them, which a "
        "pure duplicate-deletion account does not predict. The crowded recordings are what charges "
        "for fusing two real events. " + sce + " What the check does not do is make the accepted "
        f"settings free: re-measured on the five outer refits, the chosen gaps lose a median "
        f"{np.median(costs):.3f} F1 there, up to {max(costs):.3f}, against a held-out gain of about "
        f"0.010 F1 — the same size, and {sum(1 for c in costs if c < 0)} of {n} choices lose nothing "
        f"at all. {len(over)} of {n} lose more than the {drop:g} the check allows: " + and_join(fails)
        + ". <b>That cost is each net against its own 2 s, not against CoactDetect</b>, and the two "
        "comparisons point different ways: on the same crowded recordings the tuned chorus nets "
        f"score {lo_h:+.3f} to {hi_h:+.3f} F1 against CoactDetect (Figure 5, what the chosen gaps "
        f"cost on the crowded recordings), while <code>tube</code> loses {margin:.3f}. And the check "
        f"is applied at margins near its own instability: a choice's crowded cost moves by a median "
        f"{inner_spread[0]:.3f} F1 and as much as {inner_spread[1]:.3f} between the inner fits it is "
        f"enforced on and the outer refits that produce the reported number, against a {drop:g} "
        "limit, and the finest refusal on the page turned on 0.0009 F1.")


def budget_text(docs, gained, ahead, n_folds, noise, thr_same, thr_n, over_budget, over_n,
                over_budget_asrun):
    claim(all(s["mean"] < 0 for k in docs for m in NETS for s in [stats(docs[k], m, "gated", "config_kept")]),
          "every net trails CoactDetect on average under the budget, in every draw")
    inside = [f"<code>{m}</code> in {name_of(k)}" for k in docs for m in NETS
              for s in [stats(docs[k], m, "gated", "config_kept", True)]
              if s is not None and abs(s["mean"]) < noise]
    return (
        "Held to the shared cap on false alarms, every net gains from the wider gap and every net "
        f"still trails CoactDetect on average, in {both(docs)}, whether or not the low refits are set "
        f"aside. Fold by fold, {ahead_phrase(ahead, n_folds)}. The mechanism is not the one to reach "
        f"for: every one of the {thr_n} gated choices widened its gap, but the chosen threshold is "
        f"unchanged in {thr_same} of them, so the gain comes from merging at the same threshold "
        "rather than from buying a lower one. Two things the comparison does not hold level, and "
        "both cut the same way. The budget never bound CoactDetect — its F1 under the budget equals "
        "its F1 alone in every fold of both draws — while for the nets it binds at selection, on the "
        f"inner fits, and not at scoring: {over_budget} of the {over_n} budget-chosen refits are over "
        f"budget on the fold they were scored on, against {over_budget_asrun} as run, so tuning the "
        "gap left slightly more of them outside it. Read the heading as selected under the budget "
        "rather than scored under it. And with the low refits set aside "
        + (f"{and_join(inside)} sits inside the noise band rather than clearly behind"
           if inside else "no net's margin sits inside the noise band") + ".")


def alone_text(docs, noise, gained, aside_gained, carriers, systematic):
    here = {k: v for k, v in aside_gained.items() if k[2] == "ungated"}
    # Who crosses zero and who was already above it, computed: the first draft asserted that the nets
    # which end ahead were already ahead, and one of them crosses.
    crossed, already = [], []
    for k in docs:
        for m in CHORUS:
            a = stats(docs[k], m, "ungated", "as_run", True)["mean"]
            c = stats(docs[k], m, "ungated", "config_kept", True)["mean"]
            if c > 0 >= a:
                crossed.append(f"<code>{m}</code> in {name_of(k)} ({signed(a)} → {signed(c)} F1)")
            elif c > 0 and a > 0:
                already.append(f"<code>{m}</code> in {name_of(k)}")
    crossings = ((("The gap carries " + and_join(crossed) + " across zero; ") if crossed else "")
                 + (and_join(already) + (" ended ahead having started there, inside the noise band "
                    "either way." if already else "")
                    if already else "no other net ends above zero."))
    parts = []
    for k, _, name in draws(docs):
        for m in CHORUS:
            a = stats(docs[k], m, "ungated", "as_run", True)
            c = stats(docs[k], m, "ungated", "config_kept", True)
            parts.append(f"in {name} <code>{m}</code> goes {signed(a['mean'])} → {signed(c['mean'])} "
                         f"F1 ({c['folds_ahead']} of {c['folds']} folds ahead)")
    return (
        "On F1 alone the sign of the margin depends on two choices a reader must see separately: "
        "whether the refits that scored under " + f"{LOW_F1:g} F1 are set aside, and whether the "
        "baseline is scored the same way. Set aside on both sides, " + "; ".join(parts) + ". So on "
        f"this selection the gap itself is worth {min(here.values()):.3f} to {max(here.values()):.3f} "
        f"F1, about the {noise:.3f} F1 between-draw scale. " + crossings + " The set-aside is not "
        "even-handed and cannot be: CoactDetect has one value per fold and no refits, so dropping low "
        "refits can only move a net's margin upward — every set-aside column in Table 1 is at or "
        "above the column beside it. The parent report's position is the stricter one, that a user of "
        "these models gets the failures too; this page reports the set-aside as the sensitivity, not "
        "as an equal accounting. " + carriers + " " + systematic)


def ahead_phrase(ahead, n_folds):
    if not ahead:
        return f"CoactDetect is ahead of every net in all {n_folds} folds"
    return (f"CoactDetect is ahead in {n_folds - len(ahead)} of {n_folds} folds; a net leads only "
            + and_join(f"<code>{m}</code> in {name_of(k)}, {fold_label(i)}, by {signed(v)} F1"
                       for k, m, i, v in ahead))


def carrier_text(docs):
    """Which fold carries a set-aside sign change: the leverage the reader must be able to see."""
    out = []
    for k in docs:
        for m in CHORUS:
            a = margins(docs[k], m, "ungated", "config_kept")
            b = margins(docs[k], m, "ungated", "config_kept", True)
            moved = [(i, b[i] - a[i]) for i in range(len(a))
                     if a[i] is not None and b[i] is not None and abs(b[i] - a[i]) > 1e-9]
            if moved and max(abs(x) for _, x in moved) > 0.05:
                i, dv = max(moved, key=lambda t: abs(t[1]))
                out.append(f"{fold_label(i)} ({signed(dv)} F1) for <code>{m}</code> in {name_of(k)}")
    return ("The set-aside is concentrated, not spread: in each case one fold carries it — "
            + and_join(out) + " — while that row's other folds do not move at all."
            if out else "No fold's set-aside moves its row by more than 0.05 F1.")


# ---- the page -------------------------------------------------------------------------------------

def body(docs, report_href: str) -> str:
    noise = first(docs)["noise_f1"]
    drop = first(docs)["max_crowded_drop"]
    for doc in docs.values():
        rep = doc["reproduction"]
        claim(rep["own_threshold_at_2s"] == rep["rows_at_2s"] == rep["empty_recordings_at_2s"]
              == rep["fits"] and rep["rows_without_score_file"] == 0, "every fit reproduces at 2 s")
    claim(max(r["reproduces_run"][f] for doc in docs.values() for m in NETS for w in SEL
              for r in rows_of(doc, m, w) for f in ("inner_f1", "heldout_f1")) < 1e-12,
          "both selections' inner and held-out F1 reproduce the run at 2 s")
    n_fits = sum(doc["reproduction"]["fits"] for doc in docs.values())

    gained = {(k, m, w): stats(docs[k], m, w, "config_kept")["mean"] - stats(docs[k], m, w, "as_run")["mean"]
              for k in docs for m in CHORUS for w in SEL}
    aside_gained = {(k, m, w): (stats(docs[k], m, w, "config_kept", True)["mean"]
                                - stats(docs[k], m, w, "as_run", True)["mean"])
                    for k in docs for m in CHORUS for w in SEL
                    if stats(docs[k], m, w, "config_kept", True) is not None
                    and stats(docs[k], m, w, "as_run", True) is not None}
    ahead = [(k, m, i, v) for k in docs for m in NETS
             for i, v in enumerate(margins(docs[k], m, "gated", "config_kept")) if v and v > 0]
    n_gated_folds = sum(len(margins(docs[k], m, "gated", "config_kept")) for k in docs for m in NETS)
    costs = all_costs(docs)

    # How often a refusal happened at all, and how often the chosen threshold moved with the gap.
    choices = [(k, m, w, r) for k in docs for m in NETS for w in SEL for r in rows_of(docs[k], m, w)]
    refusals = sum(bool(r["config_kept"]["refused_by_crowded"]) for *_, r in choices) / len(choices)
    thr_pairs = [(r["as_run"]["threshold"], r["config_kept"]["threshold"])
                 for k, m, w, r in choices if w == "gated"]
    thr_same = sum(1 for a, b in thr_pairs if a == b)
    over_budget = sum(r["config_kept"]["heldout"]["seeds_over_budget"]
                      for k, m, w, r in choices if w == "gated" and r["config_kept"]["heldout"])
    over_n = sum(r["config_kept"]["heldout"]["n_seeds"]
                 for k, m, w, r in choices if w == "gated" and r["config_kept"]["heldout"])
    over_budget_asrun = sum(r["as_run"]["heldout"]["seeds_over_budget"]
                            for k, m, w, r in choices if w == "gated" and r["as_run"]["heldout"])
    # The crowded check's own spread: inner fits against outer refits, on the same choice.
    spread = [abs((r["config_kept"]["reference_crowded_f1"] - r["config_kept"]["crowded_f1"])
                  - (r["config_kept"]["outer_crowded_f1_as_run"] - r["config_kept"]["outer_crowded_f1"]))
              for *_, r in choices if r["config_kept"].get("outer_crowded_f1") is not None]
    fails = [f"<code>{m}</code> on {SEL_NAME[w]} in {name_of(k)}, {fold_label(r['outer_fold'])}, by "
             f"{r['config_kept']['outer_crowded_f1_as_run'] - r['config_kept']['outer_crowded_f1']:.3f} F1"
             for k, m, w, r in choices if r["config_kept"].get("outer_crowded_f1") is not None
             and r["config_kept"]["outer_crowded_f1_as_run"] - r["config_kept"]["outer_crowded_f1"] > drop]
    maxgap = {max(r["config_kept"]["heldout_f1_by_gap"],
                  key=lambda g: r["config_kept"]["heldout_f1_by_gap"][g])
              for k, m, w, r in choices if r["config_kept"].get("heldout_f1_by_gap")}
    claim(maxgap == {f"{first(docs)['gaps_sec'][-1]:g}"},
          "held-out F1 is largest at the top of the grid in every fold")
    sce = ("This is the check that decided the report's own headline: binned SCE's first place on F1 "
           "alone did not stand because its 30 s gap failed the same check in 7 of its 8 choices (the "
           "report's section 9, the coded detectors' choices), and CoactDetect's grid stops at 8 s "
           "because goal 1's crowded check refused its 16 s. The nets meet the check — and they meet "
           "it by being stopped at the same place.")
    systematic = ("One more reason not to read the replicate's lead as corroboration: the source of "
                  f"the {noise:.3f} F1 scale also measures a systematic shift of about +0.015 F1 in "
                  "the nets' favour in that second draw, which is the size of the lead itself.")
    n_edge = sum(1 for k, m, w, r in choices if r["config_kept"]["heldout"]
                 for x in r["config_kept"]["heldout"]["per_seed"] if x.get("threshold_at_grid_edge"))
    # The crowded recordings, net against CoactDetect: the comparison the per-net cost is not.
    coact_crowded = {}
    cc = first(docs).get("coact_crowded") or {}
    for key, val in cc.items():
        f, w = key.split(" ")
        coact_crowded[(int(f), w)] = val
    head_pairs, tube_margin = [], 0.0
    for m in NETS:
        vals = [r["config_kept"]["outer_crowded_f1"] - coact_crowded[(r["outer_fold"], w)]
                for k in docs for w in SEL for r in rows_of(docs[k], m, w)
                if r["config_kept"].get("outer_crowded_f1") is not None
                and (r["outer_fold"], w) in coact_crowded]
        if not vals:
            continue
        if m in CHORUS:
            head_pairs.append((m, float(np.mean(vals))))
        elif m == "tube":
            tube_margin = abs(float(np.mean(vals)))
    nonmono = sum(1 for k, m, w, r in choices
                  if (c := r["config_kept"].get("heldout_f1_by_gap"))
                  and any(c[f"{g2:g}"] < c[f"{g1:g}"] - 1e-12
                          for g1, g2 in zip(first(docs)["gaps_sec"], first(docs)["gaps_sec"][1:])))
    n_rows = sum(1 for k, m, w, r in choices if r["config_kept"].get("heldout_f1_by_gap"))
    hosts = {doc["provenance"]["host"] for doc in docs.values()}
    claim(len(hosts) == 1, "both draws were re-decoded on one machine")
    host = hosts.pop()
    # The refits under LOW_F1, counted as refits rather than as decodings: each is scored once as run
    # and once at the tuned gap, and counting the decodings doubles the population silently.
    low_seen: dict = {}
    for k in docs:
        for m in NETS:
            for w in SEL:
                for r in rows_of(docs[k], m, w):
                    for v in ("as_run", "config_kept"):
                        h = r[v].get("heldout")
                        for x in (h or {}).get("per_seed", []):
                            if x["f1"] < LOW_F1:
                                low_seen.setdefault((k, m, w, r["outer_fold"], x["seed"]),
                                                    bool(x.get("failed_training_signature")))
    n_collapsed = sum(1 for v in low_seen.values() if v)
    n_nocall = len(low_seen) - n_collapsed
    lowest_kept = min(x["f1"] for k in docs for m in NETS for w in SEL
                      for r in rows_of(docs[k], m, w)
                      for v in ("as_run", "config_kept", "config_rechosen")
                      for x in (r[v].get("heldout") or {}).get("per_seed", []) if x["f1"] >= LOW_F1)

    P = [f"""
<h1>The nets' merge gap, tuned</h1>
<p class=dim>An addendum to <a href="{report_href}">the fair comparison's report</a>, which it assumes
you have read: goal 2's weekend run of 2026-09-18 and its replicate on a second draw of recordings.
Simulated recordings, baseline periods, the fast stream.</p>
<p class=lede>{lede(docs, noise, gained, aside_gained, ahead, n_gated_folds, refusals, costs, drop)}</p>

<h2 id="question">1. The question</h2>
<p>{question_text(docs, n_fits)}</p>
<p>No net was retrained. A merge gap is applied when a net's per-frame output is turned into calls,
after the network has run, so each of the {n_fits:,} saved fits of {both(docs)} was run once more on
its recordings and decoded at every gap in the grid, and the gap was then chosen on the training
folds by the rules section 5 sets out.</p>

<h2 id="crowded">2. What the search ran into: the crowded-recording check</h2>
<p>Every fold's training fits wanted a wider gap than the fold was allowed to take, and held-out F1 is
largest at the top of the grid in every one of them — so what the nets chose is a boundary the check
imposed, not an optimum they found (Figure 1, held-out F1 against the merge gap; Figure 2, the gap
each fold chose and the settings refused).</p>
{figure(1, "Held-out F1 against the merge gap, choices on F1 alone", fig_curve(docs, "ungated"),
        "Each line is one chorus net's held-out F1, the mean over its five refits and then over the "
        "four outer folds, decoded at each gap in the grid; dots mark the gaps some fold chose. The "
        "x axis is the eight grid values evenly spaced, not a time axis, so equal steps are not "
        f"equal seconds. F1 is largest at the widest gap in every fold of {both(docs)}, which is what "
        "the crowded-recording check exists to stop — though the climb is not monotone: it dips "
        f"somewhere in {nonmono} of the {n_rows} fold-rows, so a wider merge does more here than "
        "delete duplicate calls. These are held-out scores and no choice was made on them.")}
{figure(2, "The gap each fold chose, and the settings refused", fig_gaps(docs),
        "Configuration kept, all four nets. A dot is a gap chosen by one or more of the four folds, "
        "with the count where more than one chose it; ×n counts the folds in which a setting at that "
        "gap beat the chosen one on the inner fits and was refused for losing more than "
        f"{drop:g} mean F1 on the crowded recordings. The shaded column is CoactDetect's 8 s: the top "
        "of its own grid, which stops there because goal 1's crowded check refused its 16 s.")}
{figure(5, "What the chosen gaps cost on the crowded recordings", fig_crowded(docs, coact_crowded),
        "Each mark is one outer fold of one draw, at the gap that fold chose, measured on the five "
        "outer refits. <b>A</b>: what the chosen gap costs the same net against its own 2 s, with the "
        f"{drop:g} limit the check allows; two folds are past it. <b>B</b>: the same net against "
        "CoactDetect on those recordings, which is the comparison the cost in A is not. The chorus "
        "nets sit right of zero there and <code>tube</code> far left of it.")}
<p>{crowded_text(docs, costs, refusals, (float(np.median(spread)), float(max(spread))), fails, drop,
               sce, head_pairs, tube_margin, nonmono, n_rows)}</p>

<h2 id="budget">3. Under the budget, the answer holds</h2>
<p>Every net gains from a wider gap and every net stays behind CoactDetect.</p>
{figure(3, "The chorus nets minus CoactDetect, choices under the budget", fig_margins(docs, "gated"),
        "Each dot is one outer fold's held-out F1, the net's mean over its five refits minus "
        "CoactDetect's; the bar is the mean of four folds. Grey rows are the net at its as-run 2 s, "
        f"blue rows the gap chosen on the inner fits; each appears twice, once counting every refit "
        f"and once with the refits under {LOW_F1:g} F1 set aside, so the baseline and the tuned "
        "choice are scored the same way. The shaded band is the between-draw scale. Right of the "
        "dashed zero line the net is ahead.")}
<p>{budget_text(docs, gained, ahead, n_gated_folds, noise, thr_same, len(thr_pairs), over_budget,
                over_n, over_budget_asrun)}</p>

<h2 id="alone">4. On F1 alone, the sign depends on how the failed refits are counted</h2>
<p>Scored the same way on both sides, the gap moves each chorus net by about one noise unit (Figure 4,
the chorus nets minus CoactDetect on F1 alone).</p>
{figure(4, "The chorus nets minus CoactDetect, choices on F1 alone", fig_margins(docs, "ungated"),
        "The rows, marks and key of Figure 3, for the choices made on F1 alone. Note the x "
        "axis: it is scaled to the folds whose refits all trained, and a fold beyond its left end is "
        "written in the gutter with its value, so one collapsed fold cannot flatten every other "
        "margin.")}
<p>{alone_text(docs, noise, gained, aside_gained, carrier_text(docs), systematic)}</p>
<p>Counted as refits rather than as decodings — each is scored once as run and once at the tuned gap —
{len(low_seen)} refit scorings of {both(docs)} fall under {LOW_F1:g} F1: {n_collapsed} carry the run's
failed-training signature, one call per recording, and {n_nocall} made no calls at all at the
threshold their selection chose, which the report counts as a different failure. The set-aside covers
both, and the cut sits in an empty band: no refit of either draw scores between {LOW_F1:g} and
{lowest_kept:.3f}.</p>

<h2 id="how">5. How the gap was chosen</h2>
<ul>
<li><b>On the training folds only</b>, from the inner fits, as the run chose each net's configuration
(the report's section 4.1 and its Figure 4, the nested cross-validation layout): for each outer fold,
the pooled F1 of the nine inner fits — three training seeds by three inner folds — that never saw
it.</li>
<li><b>The grid</b>: {", ".join(f"{x:g}" for x in first(docs)["gaps_sec"])} s. It holds every value of
CoactDetect's own grid and reaches the top of binned SCE's — the synchronous-calcium-event detector —
so it spans the full range any coded detector was allowed. It is coarser than the union of their
grids, which also holds 0.1, 0.5, 4, 10 and 20 s, and the coarseness probably understates the nets:
10 s was refused nowhere because it was never offered, while 15 s was refused nearly everywhere.</li>
<li><b>On F1 alone</b> the gap is a configuration setting and each fit still picks its own threshold
by its own rule, at that gap, on its two threshold recordings (pooled as four draws, as the run's own
picker does). <b>Under the budget</b> threshold and gap are chosen together, and a pair is allowed
only if the pooled inner rates are within the fold's budget.</li>
<li><b>Goal 1's move rule.</b> The search starts at the run's 2 s and moves only for a gain of at
least {first(docs)["min_gain"]:g} inner F1 — the coded searches' step, a fifth of the noise scale, so
it binds rarely.</li>
<li><b>The crowded-recording check</b>, inside the search: a move may lose no more than {drop:g} mean
F1 on 24 three-hour crowded recordings (seeds 1 to 12 at both backgrounds, built by the bench's
tail-recording generator) against the choice it replaces, on the same inner fits. ⚠ That allowance is
a judgement the project lead has not signed, and it decides every gap on this page.</li>
<li><b>Two variants</b>: the run's configuration kept, so only the gap and — under the budget — the
threshold move; and the configuration re-chosen too. The re-chosen variant is mostly unscored: where
it prefers a configuration the run never refitted, that fold has no held-out number, and nothing here
retrains.</li>
<li><b>Held out</b>, as in the run: the chosen configuration's five outer refits on the held-out fold,
at the chosen gap, each at the threshold its own rule picks there, or at the chosen threshold under
the budget.</li>
</ul>
<p>At 2 s the re-decoding reproduces both runs exactly: every fit's picked threshold, every recording's
counts and every empty recording's call count match the run's own files, for all {n_fits:,} fits, and
so do both selections' inner and held-out F1. Both draws were re-decoded on one machine, {host}, on a
GPU — the machine that trained this draw's fits, and not the one that trained the replicate's, whose
rows matched exactly all the same. That is why the match here is bit-for-bit where the report's CPU
re-scoring, in its Figure 11, what the merge gap is worth on each side, matched only to 0.0015 F1 per
refit.</p>

<h2 id="table">6. Every net, {both(docs)}</h2>
<p class=tcap><b>Table 1.</b> Held-out F1, net minus CoactDetect, mean of four outer folds, with the
folds the net leads and the paired <i>t</i> over folds (3 degrees of freedom, two-sided 5% critical
value 3.18), plain and with the Nadeau–Bengio correction for the overlap between folds' training sets
(2003, Machine Learning 52:239–281, doi:10.1023/A:1024068626366; factor
{first(docs)["nb_factor"]:.3f} = √(3/7), derived and bounded in the report's section 4.1). The five
value columns are the same quantity under different rules: as run; as run with the low refits set
aside; the gap tuned; the gap tuned with them set aside; and the gap with the configuration re-chosen
too, which is scored only where the run happened to refit that configuration. A † marks a mean inside
the ±{noise:.3f} F1 between-draw scale; a ⚠ marks a value at a chosen gap that fails the crowded check
when it is re-measured on the outer refits. Folds are numbered 1 to 4, as in the report; the JSON
counts them from 0. No correction is made for the many comparisons in this table.</p>
{results_table(docs)}

<h2 id="limits">7. Limits</h2>
<ul class=resid>
<li><b>The report's limits hold except the two this page changes</b> (its section 11): the merge gap
is no longer tuned for one side only, and the nets are now scored on crowded recordings. The rest
stand, including simulated recordings, baseline periods and the fast stream only, and a bench fitted
to an export folder with a known, uncleared contamination of about 0.03% of firings.</li>
<li><b>The crowded check bound the two sides at different times, not only one of them.</b> For the
nets it runs inside this selection, comparing a wider gap against their as-run 2 s. For CoactDetect it
had already run in goal 1, which tried 16 s and refused it — which is why its grid stops at 8 s (the
report's section 11). Inside this run its declared reference already carries that 8 s, so the
after-the-fact check had nothing left to refuse, and reading it as a pass would credit a test that
could not fail.</li>
<li><b>Every chosen gap is a boundary.</b> Held-out F1 is largest at the widest gap in the grid in
every fold of {both(docs)} (Figure 1, held-out F1 against the merge gap), so the nets stopped where
the check stopped them, and CoactDetect stopped where its grid ended. Neither is an optimum, and the
two landing near each other is not agreement.</li>
<li><b>The allowance that decides it is unsigned</b>, and no sensitivity is reported: every number
here moves with {drop:g}.</li>
<li><b>The two sides' gaps match by name, not by operation.</b> A net merges runs of frames above its
threshold; CoactDetect merges significant sliding windows two seconds wide. The same nominal gap
starts fusing real events at different separations.</li>
<li><b>The noise scale is one number standing for two sources.</b> {NOISE_SOURCE[0].upper() + NOISE_SOURCE[1:]}.
Refit-to-refit spread within a fold is comparable: the standard error of a fold's five-refit mean
exceeds {noise:.3f} F1 in more than half the chorus-net folds.</li>
<li><b>Four folds.</b> Every <i>t</i> here has 3 degrees of freedom, and "4 of 4 folds" cannot reach
significance on a sign test. The scale, not the <i>t</i>, is what separates a margin from a
result.</li>
<li><b>The scorer's match tolerance is 2.5 s</b> and interacts with a merge gap of 0 to 30 s; the
nets' tolerance curve has never been measured.</li>
<li><b>Nothing was retrained</b>, and {n_edge} of the held-out refit decodings run at an end of the
threshold grid, where the picker's own documentation says the value is not an operating point.</li>
</ul>

<h2 id="where">8. Where everything is</h2>
<ul>
<li><code>tools/tune_net_merge_gap.py</code>: the re-decoding and the selections; its docstring states
the selection and move rules, and the grid is its <code>GAPS_SEC</code>. Its output is
<code>net_merge_gap.json</code> and <code>replicate_net_merge_gap.json</code> beside this page, each
recording the machine, the torch version and the commit of both trees it ran from.</li>
<li>The nets and the tuning tool whose rules this reuses are on branch
<code>tune-bench-comparison</code>, not on <code>main</code>: the tool needs that worktree's
<code>src</code> and <code>tools</code> on <code>PYTHONPATH</code>.</li>
<li><code>tools/build_net_merge_gap_page.py</code>: this page.
<code>tests/test_tune_net_merge_gap.py</code>: the reproduction, the move rule, the crowded refusals
and the statistics, checked against the committed output.</li>
<li>The between-draw scale and the replicate's own numbers are in
<code>docs/learned/tuned_vs_coact/replicate1/report.html</code>, section 9.</li>
<li>The re-decoded arrays are not committed; <code>score</code> and <code>crowded</code> regenerate
them from the saved fits. On the workstation that produced them the two draws took about six and
seven hours of wall clock, overlapping.</li>
</ul>
"""]
    return "".join(P)


EXTRA_CSS = ("code{overflow-wrap:anywhere}td code,th code{overflow-wrap:normal;white-space:nowrap}"
             ".tcap{margin:18px 0 4px;font-size:15px}")


def build(run: Path, report_href: str) -> str:
    docs = load(run)
    ver = provenance.code_version() or "unknown"
    dirty = provenance.git_dirty()
    note = ("" if dirty is False else " <b>The tree had uncommitted changes when this was built.</b>"
            if dirty else " Whether the tree was clean could not be checked.")
    prov = (f'<h2 id="provenance">Provenance</h2><p class=dim>Built {time.strftime("%Y-%m-%d %H:%M %z")} '
            f"by <code>tools/build_net_merge_gap_page.py</code> at <code>{esc(ver)}</code>.{note} The "
            "review record for this page is <code>docs/reviews/net_merge_gap_2026-09-19.md</code>.</p>")
    meta = ('<meta name="description" content="The fair comparison\'s nets with their merge gap tuned '
            f'like any other setting, against CoactDetect, in {both(docs)} of recordings.">\n'
            f'<meta name="generator" content="tools/build_net_merge_gap_page.py {esc(ver)}">\n'
            '<meta name="author" content="the bugarach project">\n'
            f'<meta name="date" content="{time.strftime("%Y-%m-%d")}">\n')
    html = page("The nets' merge gap, tuned", body(docs, report_href) + prov)
    html = html.replace("</style>", EXTRA_CSS + "</style>", 1)
    html = html.replace('<meta name="viewport"', meta + '<meta name="viewport"', 1)
    return html.replace("<!doctype html>", '<!doctype html><html lang="en">', 1)


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--run", type=Path, default=DEFAULT_RUN)
    ap.add_argument("--out", type=Path, default=None,
                    help=f"destination folder (default: the darkroom's {DARKROOM_FOLDER}/report/)")
    ap.add_argument("--also", type=Path, default=None, help="a second copy, e.g. the run's repo folder")
    a = ap.parse_args(argv)
    out = a.out
    if out is None:
        from bugarach import paths
        root = paths.darkroom(create=True)
        if root is None:
            print(paths.unresolved_message(), file=sys.stderr)
            return 2
        out = root / DARKROOM_FOLDER / "report"
    for folder, name, href in [(Path(out), "merge-gap.html", "index.html")] + (
            [(Path(a.also), "net_merge_gap.html", "report.html")] if a.also else []):
        folder.mkdir(parents=True, exist_ok=True)
        (folder / name).write_text(build(a.run, href), encoding="utf-8")
        print(folder / name)
    return 0


if __name__ == "__main__":
    sys.exit(main())
