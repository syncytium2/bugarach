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

from bugarach import provenance  # noqa: E402

DEFAULT_RUN = REPO / "docs" / "learned" / "tuned_vs_coact" / "fair_comparison_2026_09_18"
DRAWS = (("this", "net_merge_gap.json", "this run's draw"),
         ("replicate", "replicate_net_merge_gap.json", "the replicate's draw"))
NETS = ("chorus_norm", "chorus_gain_norm", "line_length", "tube")
CHORUS = ("chorus_norm", "chorus_gain_norm")
SEL = ("ungated", "gated")
VARIANTS = (("as_run", "as run, 2 s"), ("config_kept", "gap tuned"),
            ("config_rechosen", "gap and configuration re-chosen"))
NOISE_INK = "#ececec"


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


def heldout(entry):
    h = entry.get("heldout") if isinstance(entry, dict) else None
    return None if h is None else h["f1_mean"]


def margins(doc, m, w, variant):
    """Net minus CoactDetect per fold, held-out F1; None where the choice has no refits."""
    coact = doc["coact"]["f1"][w]
    return [None if heldout(r[variant]) is None else heldout(r[variant]) - coact[r["outer_fold"]]
            for r in doc["nets"][m][w]]


def comp(doc, m, w, variant):
    return doc["comparisons"][w].get(f"{m} {variant} - coact")


def gaps(doc, m, w, variant="config_kept"):
    return [r[variant]["gap_sec"] for r in doc["nets"][m][w]]


def fmt_gaps(gs):
    return ", ".join(f"{g:g}" for g in gs) + " s"


# ---- figures ------------------------------------------------------------------------------------

def fig_margins(docs, w) -> Svg:
    """Per fold, net minus CoactDetect, for the two chorus nets as run, with the gap tuned, and with
    the configuration re-chosen too; one panel per draw; the noise scale shaded around zero."""
    rows = [(m, v, lab) for m in CHORUS for v, lab in VARIANTS]
    top, rh = 50, 30
    yb = top + len(rows) * rh
    svg = Svg(900, yb + 110, f"The two chorus nets minus CoactDetect per outer fold, {SEL_NAME[w]}, "
                             "as run, with the merge gap tuned, and with the configuration re-chosen "
                             "too, for each draw of recordings")
    vals = [v for d in docs.values() for m, var, _ in rows for v in margins(d, m, w, var)
            if v is not None]
    step = 0.02 if max(vals) - min(vals) <= 0.1 else 0.04    # labels 11 px wide need the room
    lo = min(-step, math.floor(min(vals) / step) * step)
    hi = max(step, math.ceil(max(vals) / step) * step)
    ticks = [round(v, 2) for v in np.arange(lo, hi + 1e-9, step)]
    noise = first(docs)["noise_f1"]
    panels = ([((330, 590), draws(docs)[0], "A")] if len(docs) == 1 else
              [((330, 590), draws(docs)[0], "A"), ((630, 880), draws(docs)[1], "B")])
    for (x0, x1), (k, _, name), letter in panels:
        X = lambda v, a=x0, b=x1: a + (v - lo) / (hi - lo) * (b - a)   # noqa: E731
        svg.text((x0 + x1) / 2, 24, f"{letter}.  {name[0].upper() + name[1:]}", anchor="middle",
                 size=13, weight="bold")
        svg.rect(X(-noise), top - 6, X(noise) - X(-noise), yb - top + 6, fill=NOISE_INK)
        x_axis(svg, X, x0, x1, yb, ticks, fmt_diff, "net minus CoactDetect, held-out F1",
               zero_rule=True, top=top - 6)
        for i, (m, var, _) in enumerate(rows):
            yc = top + i * rh + rh / 2
            d = margins(docs[k], m, w, var)
            ink = GREY if var == "as_run" else NET_INK
            for j, v in enumerate(d):
                if v is not None:
                    svg.circle(X(v), yc + (j - 1.5) * 3.2, 3.4, fill=ink)
            got = [v for v in d if v is not None]
            if len(got) == len(d):
                svg.line(X(float(np.mean(got))), yc - 11, X(float(np.mean(got))), yc + 11,
                         stroke=ink, w=2.4)
            else:
                # No mean: a fold is missing. Said at the row's top left, clear of the dots.
                svg.text(x0 + 2, yc - 7, f"{len(got)} of {len(d)} folds refitted, so no mean",
                         size=10, fill=GREY)
    for i, (m, var, lab) in enumerate(rows):
        yc = top + i * rh + rh / 2
        svg.text(320, yc + 4, f"{m}, {lab}", anchor="end", size=12)
        if i and i % len(VARIANTS) == 0:
            svg.line(20, top + i * rh, 890, top + i * rh, stroke="#bbb", dash="3 3")
    y = yb + 74
    svg.circle(30, y, 3.4, fill=GREY)
    svg.text(40, y + 4, "one outer fold, as run", size=12)
    svg.circle(210, y, 3.4, fill=NET_INK)
    svg.text(220, y + 4, "one outer fold, re-selected", size=12)
    svg.line(410, y - 8, 410, y + 8, stroke=NET_INK, w=2.4)
    svg.text(418, y + 4, "mean of 4 folds", size=12)
    svg.rect(540, y - 8, 22, 16, fill=NOISE_INK)
    svg.text(570, y + 4, f"within ±{noise:.3f} F1, the noise scale", size=12)
    return svg


def fig_gaps(docs) -> Svg:
    """Which gap each fold chose, and which higher-scoring gaps the crowded check refused."""
    grid = first(docs)["gaps_sec"]
    rows = [(k, m, w) for k, _, _ in draws(docs) for m in CHORUS for w in SEL]
    top, rh = 64, 30
    yb = top + len(rows) * rh
    svg = Svg(900, yb + 100, "The merge gap each outer fold chose for the two chorus nets, and the "
                             "settings refused by the crowded-recording check, for each selection "
                             "and each draw of recordings")
    x0, x1 = 390, 870
    X = lambda i: x0 + (i + 0.5) * (x1 - x0) / len(grid)   # noqa: E731
    coact_gap = sorted({g for d in docs.values() for w in SEL for g in d["coact"]["merge_gap_sec"][w]})
    claim(coact_gap == [8.0], "CoactDetect chose 8 s in every fold, selection and draw")
    ci = grid.index(8.0)
    svg.rect(X(ci) - (x1 - x0) / len(grid) / 2, top - 6, (x1 - x0) / len(grid), yb - top + 6,
             fill=NOISE_INK)
    svg.text(X(ci), top - 14, "CoactDetect: 8 s everywhere", anchor="middle", size=11)
    svg.text(X(grid.index(2.0)), top - 14, "the nets, as run", anchor="middle", size=11)
    svg.line(x0, yb, x1, yb)
    for i, g in enumerate(grid):
        svg.line(X(i), yb, X(i), yb + 4)
        svg.text(X(i), yb + 18, f"{g:g} s", anchor="middle", size=11)
    svg.text((x0 + x1) / 2, yb + 36, "merge gap", anchor="middle", size=12)
    names = {k: n for k, _, n in DRAWS}
    for r, (k, m, w) in enumerate(rows):
        yc = top + r * rh + rh / 2
        svg.text(380, yc + 4, f"{names[k]}, {m}, {SEL_NAME[w]}", anchor="end", size=12)
        if r and r % (len(CHORUS) * len(SEL)) == 0:
            svg.line(20, top + r * rh, 890, top + r * rh, stroke="#bbb", dash="3 3")
        for j, row in enumerate(docs[k]["nets"][m][w]):
            c = row["config_kept"]
            dy = (j - 1.5) * 5.0
            for g in sorted({x["gap_sec"] for x in c["refused_by_crowded"]}):
                gi = grid.index(g)
                svg.text(X(gi), yc + dy + 4, "×", anchor="middle", size=13, fill=REPL_INK)
            svg.circle(X(grid.index(c["gap_sec"])), yc + dy, 3.4, fill=NET_INK)
    y = yb + 72
    svg.circle(30, y, 3.4, fill=NET_INK)
    svg.text(40, y + 4, "one outer fold's chosen gap", size=12)
    svg.text(250, y + 5, "×", anchor="middle", size=13, fill=REPL_INK)
    svg.text(260, y + 4, "a setting at that gap that scored higher on the inner fits and was refused: "
                         "it lost more than 0.02 F1 on the crowded recordings", size=12)
    return svg


# ---- tables -------------------------------------------------------------------------------------

def stat_cell(c, per_fold=None):
    if c is None:
        got = sum(v is not None for v in per_fold or [])
        return (f"no mean: {got} of {len(per_fold)} folds refitted" if per_fold else "not measured")
    return (f"{signed(c['mean'])} ({c['folds_ahead']} of {c['folds']}; <i>t</i> {tnum(c['t'])}, "
            f"corrected {tnum(c['t_corrected'])})")


def both(docs):
    return "both draws" if len(docs) > 1 else "this draw"


def results_table(docs) -> str:
    rows = []
    for k, _, name in draws(docs):
        d = docs[k]
        for w in SEL:
            for m in NETS:
                rows.append([name, SEL_NAME[w], f"<code>{m}</code>", fmt_gaps(gaps(d, m, w)),
                             stat_cell(comp(d, m, w, "as_run")),
                             stat_cell(comp(d, m, w, "config_kept")),
                             stat_cell(comp(d, m, w, "config_rechosen"),
                                       margins(d, m, w, "config_rechosen"))])
    return table(["draw", "selection", "net", "gap chosen, folds 1 to 4",
                  "as run: net minus CoactDetect, F1 (folds ahead; <i>t</i>)",
                  "gap tuned", "gap and configuration re-chosen"], rows,
                 f"Table 1, every net in {both(docs)}")


# ---- the page -----------------------------------------------------------------------------------

def body(docs, report_href: str) -> str:
    d = first(docs)
    noise = d["noise_f1"]
    for doc in docs.values():
        rep = doc["reproduction"]
        claim(rep["own_threshold_at_2s"] == rep["rows_at_2s"] == rep["empty_recordings_at_2s"]
              == rep["fits"] and rep["rows_without_score_file"] == 0, "every fit reproduces at 2 s")
    n_fits = sum(doc["reproduction"]["fits"] for doc in docs.values())
    claim(all(doc["coact"]["passes_crowded_check"] and all(doc["coact"]["passes_crowded_check"].values())
              for doc in docs.values()),
          "CoactDetect's choices pass the crowded check after the fact, in both draws")

    # F1 alone
    u = {k: {m: comp(docs[k], m, "ungated", "config_kept") for m in CHORUS} for k in docs}
    u0 = {k: {m: comp(docs[k], m, "ungated", "as_run") for m in CHORUS} for k in docs}
    # Under the budget
    g = {k: {m: comp(docs[k], m, "gated", "config_kept") for m in NETS} for k in docs}
    g0 = {k: {m: comp(docs[k], m, "gated", "as_run") for m in NETS} for k in docs}
    closed = {k: {m: 1 - g[k][m]["mean"] / g0[k][m]["mean"] for m in CHORUS} for k in docs}
    gated_ahead_folds = [(k, m, i, v) for k in docs for m in NETS
                         for i, v in enumerate(margins(docs[k], m, "gated", "config_kept")) if v > 0]
    n_gated_folds = sum(len(margins(docs[k], m, "gated", "config_kept")) for k in docs for m in NETS)
    lead_u = {k: max(CHORUS, key=lambda m: u[k][m]["mean"]) for k in docs}
    ungated_under_noise = all(abs(u[k][lead_u[k]]["mean"]) < noise for k in docs)

    all_gaps = [gg for k in docs for m in NETS for w in SEL for gg in gaps(docs[k], m, w)]
    n_moved = sum(gg != 2.0 for gg in all_gaps)
    n_refusing = sum(bool(row["config_kept"]["refused_by_crowded"]) for k in docs for m in NETS
                     for w in SEL for row in docs[k]["nets"][m][w])
    changed = [(k, m, w, row["outer_fold"], row["config_rechosen"]) for k in docs for m in NETS
               for w in SEL for row in docs[k]["nets"][m][w] if row["config_rechosen"]["config_changed"]]
    unmeasured = [c for c in changed if c[4]["heldout"] is None]

    P = []
    P.append(f"""
<p class=dim>An addendum to <a href="{report_href}">the fair comparison's report</a> (goal 2, the
weekend run of 2026-09-18, and WSMIP065's replicate), which it assumes. Simulated recordings,
baseline periods, the fast stream.</p>
<h1>The nets' merge gap, tuned</h1>
<p class=lede><b>{lede(docs, u, closed, noise, lead_u, ungated_under_noise, gated_ahead_folds,
                        n_gated_folds)}</b></p>

<h2 id="question">1. The question</h2>
<p>A detector's calls closer together than its <b>merge gap</b> are merged into one (the report's
Figure 3). In the fair comparison the coded detectors' searches tuned that gap, and CoactDetect chose
8 s in every fold, while the nets decoded at a fixed 2 s (20 frames), their threshold picker's default.
The report's section 7 re-scored both sides at matched gaps with nothing else re-chosen, which bounds
what the gap could do without measuring it. The project lead asked for the measurement (2026-09-19):
tune the nets' merge gap like any other setting.</p>
<p>No net was retrained. A merge gap is applied when a net's per-frame output is turned into calls,
after the network has run, so each of the {n_fits:,} saved fits of the two draws (inner fits and outer
refits, as the run and the replicate wrote them) was run once more on its recordings and decoded at
every gap in the grid.</p>

<h2 id="how">2. How the gap was chosen</h2>
<ul>
<li><b>On the training folds only</b>, from the inner fits, exactly as the run chose each net's
configuration (the report's Figure 4): for each outer fold, the pooled F1 of the nine inner fits
(three training seeds, three inner folds) that never saw it.</li>
<li><b>The grid</b>: {", ".join(f"{x:g}" for x in d["gaps_sec"])} s. It holds every gap CoactDetect's
own grid offers (0 to 8 s) and runs to binned SCE's top, 30 s, so a net can reach any gap a coded
detector was allowed.</li>
<li><b>On F1 alone</b>, the gap is a configuration setting and each fit still picks its own threshold
by its own rule, on its two threshold recordings, <b>at that gap</b>. <b>Under the budget</b>,
threshold and gap are chosen together, and a pair is admissible only if its pooled false-alarm rates
on the inner fits are within the fold's budget, as the run chose the threshold alone.</li>
<li><b>Goal 1's move rule.</b> The search starts from the run's own choice at 2 s and leaves it only
for a gain of at least {d["min_gain"]:g} inner F1 (the coded searches' step) that also passes goal
1's <b>crowded-recording check</b>: the new choice may lose no more than {d["max_crowded_drop"]:g} mean
F1 on the crowded recordings (24 three-hour recordings, seeds 1 to 12 at both backgrounds, built
by <code>bench.make_tail_recording</code>) against the choice it replaces, measured on the same inner
fits. Goal 1 applies that check inside its search. The coded side of the fair comparison did not,
and CoactDetect's 8 s choices pass it after the fact (the report's section 9).</li>
<li><b>Two variants</b>: the run's configuration <b>kept</b>, so only the gap (and, under the budget,
the threshold) moves; and the configuration <b>re-chosen</b> too, over every configuration's inner
fits. A re-chosen configuration that the run never refitted has no held-out number, because nothing
here retrains.</li>
<li><b>Held out</b>, as in the run: the chosen configuration's five outer refits on the held-out
fold, at the chosen gap, each at the threshold its own rule picks there (F1 alone) or at the chosen
threshold (under the budget).</li>
</ul>
<p>At 2 s the re-decoding reproduces the run exactly, not approximately: every fit's picked threshold,
every recording's counts and every empty recording's call count equal the run's own files, for all
{n_fits:,} fits, and so do both selections' inner and held-out F1.</p>

<h2 id="alone">3. On F1 alone: a tie, still</h2>
<p>{alone_text(docs, u, u0, lead_u, noise)}</p>
{figure(1, "The chorus nets minus CoactDetect, choices on F1 alone", fig_margins(docs, "ungated"),
        "Each dot is one outer fold's held-out F1, the net's mean over its five refits minus "
        "CoactDetect's; the bar is the mean of the four folds. Grey: the net at its 2 s, as run. Blue: "
        "the gap chosen on the inner fits, with the configuration kept, then re-chosen too. The shaded "
        f"band is ±{noise:.3f} F1, the median change in F1 from changing the recordings alone "
        "(WSMIP065's replicate); a mean inside it is not a result. Right of the dashed zero line, the "
        "net is ahead.")}

<h2 id="budget">4. Under the budget: closer, and behind</h2>
<p>{budget_text(docs, g, g0, closed, gated_ahead_folds, n_gated_folds, noise)}</p>
{figure(2, "The chorus nets minus CoactDetect, choices under the budget", fig_margins(docs, "gated"),
        "As Figure 1, for the choices held to the shared false-alarm budget; threshold and gap were "
        "chosen together on the inner fits.")}

<h2 id="crowded">5. What the crowded check refused</h2>
<p>{crowded_text(docs, n_moved, len(all_gaps), n_refusing)}</p>
{figure(3, "The gap each outer fold chose, and the settings refused", fig_gaps(docs),
        "Configuration kept. Each dot is one outer fold's chosen gap (four folds per row, offset "
        "vertically so they do not cover each other); a cross marks a gap at which a setting beat the "
        "chosen one on the inner fits and was refused because it lost more than 0.02 mean F1 on the "
        "crowded recordings against the as-run choice. Under the budget a setting is a gap and a "
        "threshold together, so a cross can share a column with the chosen gap at another threshold. "
        "The shaded column is CoactDetect's choice.")}

<h2 id="table">6. Every net, {both(docs)}</h2>
<p class=tcap><b>Table 1.</b> Held-out F1, net minus CoactDetect, mean of four outer folds, with the
number of folds the net is ahead and the paired <i>t</i> over folds (3 degrees of freedom), plain and
with the Nadeau–Bengio correction for overlapping training sets (factor {d["nb_factor"]:.3f}).</p>
{results_table(docs)}
<p>{rechosen_text(changed, unmeasured, len(all_gaps))}</p>

<h2 id="limits">7. Limits</h2>
<ul class=resid>
<li><b>The report's limits hold here unchanged</b> (its section 11): simulated recordings, baseline
periods and the fast stream only, and a bench fitted to an export folder with a known, uncleared
contamination of about 0.03% of firings.</li>
<li><b>The nets' side is now tuned inside the crowded check and the coded side is not.</b> CoactDetect's
choices pass that check after the fact, so for CoactDetect the difference is none; for the other coded
detectors the report lists which of their choices it would have refused.</li>
<li><b>The move rule is goal 1's, and it favors the as-run choice.</b> A gap is taken only for at least
{d["min_gain"]:g} inner F1; a smaller gain is treated as no gain.</li>
<li><b>Nothing was retrained.</b> A configuration the re-chosen variant prefers but the run never
refitted is reported and not scored, and a net trained with its gap known might train differently.</li>
<li><b>Four folds.</b> Every <i>t</i> here has 3 degrees of freedom; the noise scale, not the
<i>t</i>, is what separates a margin from a result.</li>
</ul>

<h2 id="where">8. Where everything is</h2>
<ul>
<li><code>tools/tune_net_merge_gap.py</code>: the re-decoding and the selections; its docstring states
every rule above. <code>docs/learned/tuned_vs_coact/fair_comparison_2026_09_18/net_merge_gap.json</code>
and <code>replicate_net_merge_gap.json</code>: its output, one per draw.</li>
<li><code>tools/build_net_merge_gap_page.py</code>: this page. <code>tests/test_tune_net_merge_gap.py</code>:
the reproduction, the move rule and the statistics, checked against the committed output.</li>
<li>The re-decoded arrays are not committed; <code>tune_net_merge_gap.py score</code> and
<code>crowded</code> regenerate them from the saved fits in about two hours on a workstation with a
GPU.</li>
</ul>
""")
    return "".join(P)


def ahead_phrase(ahead, n_folds):
    names = {k: n for k, _, n in DRAWS}
    if not ahead:
        return f"CoactDetect is ahead of every net in all {n_folds} folds"
    return (f"CoactDetect is ahead in {n_folds - len(ahead)} of {n_folds} folds; the net leads only "
            + ", ".join(f"<code>{m}</code> in {names[k]}, {fold_label(i)}, by {signed(v)}"
                        for k, m, i, v in ahead))


def lede(docs, u, closed, noise, lead_u, under_noise, ahead, n_folds):
    claim(under_noise, "on F1 alone the leading chorus net's margin is inside the noise scale in both draws")
    claim(all(v < noise for *_, v in ahead), "under the budget no net leads a fold by the noise scale")
    claim(all(closed[k][m] > 0 for k in docs for m in CHORUS), "tuning the gap helps each chorus net "
          "under the budget")
    lo = min(closed[k][m] for k in docs for m in CHORUS)
    hi = max(closed[k][m] for k in docs for m in CHORUS)
    return (f"Tuned like any other setting, the nets' merge gap moves each chorus net toward "
            f"CoactDetect, and past it by no more than the noise. On F1 alone the better chorus net "
            + and_join([f"ends {signed(u[k][lead_u[k]]['mean'])} F1 from CoactDetect in {name}"
                        for k, _, name in draws(docs)])
            + f", inside ±{noise:.3f}: still a tie. Under the budget, tuning the gap closes "
            f"{lo:.0%} to {hi:.0%} "
            f"of the chorus nets' shortfall, and {ahead_phrase(ahead, n_folds)}.")


def alone_text(docs, u, u0, lead_u, noise):
    parts = []
    for k, _, name in draws(docs):
        m = lead_u[k]
        c, c0 = u[k][m], u0[k][m]
        parts.append(f"In {name}, <code>{m}</code> goes from {signed(c0['mean'])} as run to "
                     f"{signed(c['mean'])} with its gap tuned ({c['folds_ahead']} of 4 folds ahead; "
                     f"<i>t</i> {tnum(c['t'])}, corrected {tnum(c['t_corrected'])}), choosing "
                     f"{fmt_gaps(gaps(docs[k], m, 'ungated'))}.")
    return (" ".join(parts) + f" {'Both margins are' if len(parts) > 1 else 'That margin is'} under "
            f"{noise:.3f} F1, the change that swapping the recordings alone produces, so on F1 alone "
            "the two stay tied (Figure 1).")


def budget_text(docs, g, g0, closed, ahead, n_folds, noise):
    parts = []
    for k, _, name in draws(docs):
        for m in CHORUS:
            parts.append(f"<code>{m}</code> in {name}: {signed(g0[k][m]['mean'])} as run, "
                         f"{signed(g[k][m]['mean'])} tuned ({closed[k][m]:.0%} of the shortfall "
                         f"closed; <i>t</i> {tnum(g[k][m]['t'])}, corrected "
                         f"{tnum(g[k][m]['t_corrected'])})")
    claim(all(v < noise for *_, v in ahead), "no fold led by the noise scale under the budget")
    return ("Held to the shared false-alarm budget, a wider gap lets a net call less and so fit the "
            "budget at a lower threshold, and every chorus net gains: " + "; ".join(parts) + ". "
            f"Across the four nets and {both(docs)}, {ahead_phrase(ahead, n_folds)}"
            + (f", inside ±{noise:.3f}" if ahead else "") + " (Figure 2).")


def count(n, of):
    return f"all {of}" if n == of else f"{n} of the {of}"


def crowded_text(docs, n_moved, n_all, n_refusing):
    names = {k: n for k, _, n in DRAWS}
    moved = sorted({gg for k in docs for m in NETS for w in SEL for gg in gaps(docs[k], m, w)
                    if gg != 2.0})
    rows = [(k, m, w, row) for k in docs for m in NETS for w in SEL for row in docs[k]["nets"][m][w]]
    wider = sum(any(x["gap_sec"] > row["config_kept"]["gap_sec"]
                    for x in row["config_kept"]["refused_by_crowded"]) for *_, row in rows)
    drop = first(docs)["max_crowded_drop"]
    outer = [(k, m, w, row["outer_fold"],
              row["config_kept"]["outer_crowded_f1_as_run"] - row["config_kept"]["outer_crowded_f1"])
             for k, m, w, row in rows if row["config_kept"].get("outer_crowded_f1") is not None]
    fails = [o for o in outer if o[4] > drop]
    worst_pass = max(o[4] for o in outer if o[4] <= drop)
    fail_txt = ("On every one of them the chosen gap also passes when checked afterwards on the five "
                "outer refits instead of the inner fits" if not fails else
                "Checked afterwards on the five outer refits instead of the inner fits, "
                + and_join([f"<code>{m}</code>'s choice on {SEL_NAME[w]} in {names[k]}, "
                            f"{fold_label(h)}, loses {v:.3f}" for k, m, w, h, v in fails])
                + f" on the crowded recordings, more than the {drop:g} the check allows, and every "
                f"other choice loses at most {worst_pass:.3f}")
    return (f"Of {n_all} choices (four nets, two selections, four folds, two draws), {n_moved} moved "
            f"off 2 s, to {and_join([f'{g:g}' for g in moved])} s. In {count(n_refusing, n_all)} the "
            "inner fits preferred at least one setting that the crowded check then refused, and in "
            f"{count(wider, n_all)} that setting had a wider gap than the one chosen. A wide merge "
            "fuses events a few seconds apart, which the bench's recordings, "
            "with planted events at least 120 s apart, cannot penalize, and the crowded recordings can "
            f"(Figure 3). {fail_txt}.")


def rechosen_text(changed, unmeasured, n_all):
    if not changed:
        return ("Re-choosing the configuration together with the gap picked the run's configuration "
                "in every case.")
    worse = [c for c in changed if c[4]["heldout"] is not None]
    return (f"Re-choosing the configuration together with the gap changed it in {len(changed)} of "
            f"{n_all} choices. In {len(unmeasured)} of those the new configuration was never refitted "
            "by the run, so that fold has no held-out number and its row no mean (Table 1, last "
            f"column). The other {len(worse)} have held-out numbers: in that column, and for the "
            "chorus nets in Figures 1 and 2.")


EXTRA_CSS = "<style>code{overflow-wrap:anywhere}.tcap{margin:18px 0 4px;font-size:15px}</style>"


def build(run: Path, report_href: str) -> str:
    docs = load(run)
    ver = provenance.code_version() or "unknown"
    dirty = provenance.git_dirty()
    note = ("" if dirty is False else " <b>The tree had uncommitted changes when this was built.</b>"
            if dirty else " Whether the tree was clean could not be checked.")
    prov = (f'<h2 id="provenance">Provenance</h2><p class=dim>Built {time.strftime("%Y-%m-%d %H:%M %z")} '
            f"by <code>tools/build_net_merge_gap_page.py</code> at <code>{esc(ver)}</code>.{note}</p>")
    meta = ('<meta name="description" content="The fair comparison\'s nets with their merge gap tuned '
            f'like any other setting, against CoactDetect, in {both(docs)} of recordings.">\n'
            f'<meta name="generator" content="tools/build_net_merge_gap_page.py {esc(ver)}">\n'
            '<meta name="author" content="the bugarach project">\n'
            f'<meta name="date" content="{time.strftime("%Y-%m-%d")}">\n')
    html = page("The nets' merge gap, tuned", EXTRA_CSS + body(docs, report_href) + prov)
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
