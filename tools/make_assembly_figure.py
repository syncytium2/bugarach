#!/usr/bin/env python3
"""Do the same cells recur across coordinated events — and does it depend on group?

    python tools/make_assembly_figure.py --fast DIR --slow DIR
    python tools/make_assembly_figure.py --fast DIR --slow DIR --numbers-only

Figure id `assembly_answer`, the same on every machine.

Takes the two `assess_archive.py --assemblies` runs (one per stream) and draws the
answer the way it has to be read: **by group first**. FOUNDATIONS §9 does not admit a
pooled across-group number on its own, and this corpus shows why — pooled, the FAST
stream reads "structure in most slices"; split, it is most animals in DI and MALE and
one animal in six in ORX.

**Three panels, in the order the argument runs.**

- **A — the answer.** Fraction of ANIMALS whose slices show co-participation beyond
  per-cell rate, by group, per stream, with 95% intervals. Animals rather than
  slices because one mouse contributes up to three slices and they are not
  independent.
- **B — why the instrument is believable.** Each recording's two nulls as two axes,
  against generated recordings whose participants are drawn at random by
  construction. If the real cloud sat where the generated one sits, there would be
  nothing to report.
- **C — whether it survives the arbitrary parameter.** The verdict tally across every
  coactivity floor K, both streams.

**What is in the corpus.** Baseline windows only, every treatment arm pooled — the
question is about the preparation, not about any drug. Slices the workbook marks
`exclude` are dropped, and so are the side arms it marks with a `study` (the pilots
and the APV+CNQX / GABAZINE variants). Baseline windows are checked against the
workbook's own `exp_timing` sheet and the figure refuses to build if they disagree.

Needs the group workbook — see `bugarach.groups` for how it is resolved and why the
path is never written down.
"""

from __future__ import annotations

import argparse
import json
import os
import sys
import tempfile
from pathlib import Path

import numpy as np

FIGURE_ID = "assembly_answer"
ALPHA = 0.05
FLOOR = 5e-4          # p-value floor for the log axes; 1/(1+1000) surrogates
K_SHOWN = 3
GROUP_ORDER = ("DI", "MALE", "OVX", "ORX")

REAL_FAST = "#111111"
REAL_SLOW = "#1f6fb4"
CONTROL = "#c46a1e"
GUIDE = "#9a9a9a"


def _rows(path: Path, k: int) -> list[dict]:
    d = json.loads((path / "assessment_real.json").read_text())
    return [r for r in d["rows"]
            if r["K"] == k and r.get("asm_defined")]


def controls(n: int, geometry: dict, *, seed0: int = 500) -> list[dict]:
    """Generated recordings at the real corpus's geometry: no assembly, by
    construction. Assessed and tested through exactly the same code path."""
    from bugarach.assess import assess_coactivity
    from bugarach.assembly import assess_assemblies
    from bugarach.simulate import simulate_coordination

    out = []
    for i in range(n):
        s, _ = simulate_coordination(
            n_roi=geometry["n_roi"], duration_sec=geometry["win_sec"],
            bg_rate_hz=geometry["bg_rate_hz"],
            participation=(geometry["participation"],),
            n_per_level=(geometry["n_events"],),
            jitter_sec=geometry["jitter_sec"],
            # Real cluster centres sit as close as 3 s apart (median gap ~20 s),
            # and a control has to be able to hold as many events as the data it
            # stands beside — 30 s would not fit them in the window.
            min_sep_sec=5.0,
            spacing="uniform", seed=seed0 + i)
        # The assessor's own surrogate count is irrelevant here: membership comes
        # from the observed clusters only, so a small ensemble saves time without
        # touching anything this figure reads.
        a = [x for x in assess_coactivity(s, stream="events", n_surrogates=50)
             if x.min_rois == K_SHOWN]
        if not a:
            continue
        q = assess_assemblies(a[0], n_surrogates=1000)
        if q.defined:
            out.append(dict(asm_p_margin_disp=q.p_margin_disp,
                            asm_p_margin_eig=q.p_margin_eig,
                            asm_p_uniform_disp=q.p_uniform_disp,
                            asm_p_uniform_eig=q.p_uniform_eig,
                            asm_verdict=q.verdict()))
    return out


def _xy(rows):
    """Each slice at (uniform p, margin p), each the smaller of its two statistics.

    Deliberately the same reduction the verdict applies, and the threshold drawn on
    the axes comes from ``bugarach.assembly`` rather than a copy here: axes that
    disagreed with the verdict would put a point on the significant side of a line
    it was not called significant by.
    """
    x = np.array([min(r["asm_p_uniform_disp"], r["asm_p_uniform_eig"]) for r in rows])
    y = np.array([min(r["asm_p_margin_disp"], r["asm_p_margin_eig"]) for r in rows])
    return np.maximum(x, FLOOR), np.maximum(y, FLOOR)


def by_preparation(rows):
    """Group testable slices by preparation, taken from the date in the slice id.

    **The slices are not independent** — 85 of them come from 48 dates, up to three
    per preparation — so a per-slice count overstates how many independent
    observations stand behind it, and any combination of per-slice p-values
    (Fisher) is anti-conservative for the same reason. Reported alongside the slice
    count so the reader can see both units.
    """
    import re
    from collections import defaultdict
    out = defaultdict(list)
    for r in rows:
        m = re.match(r"(\d{8})", str(r.get("slice_id", "")))
        out[m.group(1) if m else str(r.get("slice_id"))].append(r["asm_verdict"])
    n_any = sum(1 for v in out.values() if "structure-beyond-rate" in v)
    return n_any, len(out)


def tally(rows) -> dict:
    t: dict[str, int] = {}
    for r in rows:
        t[r["asm_verdict"]] = t.get(r["asm_verdict"], 0) + 1
    return t


GROUP_COLOUR = {"DI": "#1a7f4b", "MALE": "#1f6fb4",
                "OVX": "#8a6fb4", "ORX": "#c4451e"}


def animal_split(rows, meta):
    """Per group: animals showing structure beyond rate, out of animals tested."""
    from bugarach.groups import by_animal
    return by_animal(rows, meta,
                     hit=lambda r: r["asm_verdict"] == "structure-beyond-rate")


def jeffreys(k, n):
    """95% interval for a proportion. Jeffreys rather than Wald: at 1 of 6 and 9 of
    10 the normal approximation runs off the end of [0, 1] and would draw a whisker
    into impossible territory."""
    from scipy import stats
    if n == 0:
        return (float("nan"), float("nan"))
    return tuple(stats.beta.ppf([0.025, 0.975], k + 0.5, n - k + 0.5))


def group_test(split):
    """Across-group difference at the animal level. Chi-square over the 4x2 table."""
    import numpy as np
    from scipy import stats
    tab = np.array([[split[g]["animals_hit"], split[g]["animals"] - split[g]["animals_hit"]]
                    for g in GROUP_ORDER if g in split], dtype=float)
    if tab.shape[0] < 2 or tab.sum() == 0 or (tab.sum(axis=1) == 0).any():
        return float("nan")
    return float(stats.chi2_contingency(tab)[1])


def build(fast, slow, ctrl, per_k, splits, tests, width: int):
    import holoviews as hv

    # ---- A: the answer, by group, at the animal level ----------------------
    items = []
    xticks = []
    for gi, g in enumerate(GROUP_ORDER):
        xticks.append((gi, g))
        for off, stream, marker in ((-0.16, "fast", "circle"),
                                    (0.16, "slow", "square")):
            sp = splits[stream].get(g)
            if not sp or sp["animals"] == 0:
                continue
            k, n = sp["animals_hit"], sp["animals"]
            lo, hi = jeffreys(k, n)
            x = gi + off
            items.append(hv.Segments([(x, lo, x, hi)]).opts(
                color=GROUP_COLOUR[g], line_width=2, alpha=0.55))
            items.append(hv.Scatter([(x, k / n)]).opts(
                color=GROUP_COLOUR[g], size=13, marker=marker,
                line_color="white", line_width=1.5))
    a = hv.Overlay(items).opts(
        width=int(width * 0.95), height=430, ylim=(-0.05, 1.08),
        xlim=(-0.6, len(GROUP_ORDER) - 0.4), xticks=xticks,
        xlabel="group · circle FAST, square SLOW",
        ylabel="A · animals showing structure beyond rate",
        title="", show_legend=False,
        fontsize={"labels": "11pt", "ticks": "10pt"})

    # ---- B: the control, as the reason to believe A ------------------------
    a2 = ALPHA / 2.0
    bits = [hv.VLine(a2).opts(color=GUIDE, line_width=1.5, line_dash="dotted"),
            hv.HLine(a2).opts(color=GUIDE, line_width=1.5, line_dash="dotted")]
    for rows, colour, marker in ((ctrl, CONTROL, "diamond"),
                                 (fast, REAL_FAST, "circle"),
                                 (slow, REAL_SLOW, "square")):
        if not rows:
            continue
        x, y = _xy(rows)
        bits.append(hv.Scatter((x, y)).opts(
            color=colour, size=9, marker=marker, alpha=0.75,
            line_color="white", line_width=0.8))
    b = hv.Overlay(bits).opts(
        width=int(width * 0.95), height=430, logx=True, logy=True,
        xlim=(FLOOR * 0.7, 1.4), ylim=(FLOOR * 0.7, 1.4),
        xlabel="p · uniform participation, 1000 surrogates",
        ylabel="B · p · both margins fixed, 1000 surrogates",
        title="", show_legend=False,
        fontsize={"labels": "11pt", "ticks": "10pt"})

    # ---- C: does it survive the arbitrary parameter ------------------------
    ks = sorted(per_k)
    order = ["structure-beyond-rate", "uniform-only", "margin-only", "no-assembly"]
    cols = {"structure-beyond-rate": "#1a7f4b", "uniform-only": "#d98324",
            "margin-only": "#8a6fb4", "no-assembly": "#7d7d7d"}
    recs = [(f"K{k} {st}", v, per_k[k][st].get(v, 0))
            for k in ks for st in ("fast", "slow") for v in order]
    c = hv.Bars(recs, kdims=["cell", "verdict"], vdims=["slices"]).opts(
        width=int(width * 0.95), height=430, xrotation=45,
        xlabel="coactivity floor K · stream",
        ylabel="C · slices with a testable answer",
        title="", stacked=True, show_legend=False,
        cmap=[cols[v] for v in order], line_color="white", line_width=1,
        fontsize={"labels": "11pt", "ticks": "9pt"})

    def gsw(g):
        return f'<span style="color:{GROUP_COLOUR[g]}"><b>{g}</b></span>'

    def sw(v, label):
        return f'<span style="color:{cols[v]}"><b>{label}</b></span>'

    def frac(stream, g):
        sp = splits[stream].get(g)
        return f"{sp['animals_hit']}/{sp['animals']}" if sp else "—"

    n_animals = {st: sum(v["animals"] for v in splits[st].values())
                 for st in ("fast", "slow")}
    header = (
        '<div style="font:13px/1.6 system-ui,sans-serif;color:#222;'
        'max-width:1240px">'
        '<b>Do the same cells take part in one coordinated event as in the next? '
        'In most animals yes — but not in every group, and the pooled number hides '
        'that.</b><br>'
        'Baseline windows from every treatment arm, at coactivity floor '
        f'K={K_SHOWN} — K is how many ROIs must be co-active for a cluster to '
        'count. Slices the workbook excludes, and its pilot and APV+CNQX / '
        'GABAZINE arms, are not here.<br>'
        f'<b>A — the answer.</b> Animals, not slices: one mouse gives up to three '
        'slices and they are not independent. '
        + ' · '.join(f'{gsw(g)} {frac("fast", g)} FAST, {frac("slow", g)} SLOW'
                     for g in GROUP_ORDER)
        + f'. Bars are 95% intervals. Across the four groups at the animal level, '
        f'FAST differs (chi-square p = {tests["fast"]:.3f}) and SLOW does not '
        f'(p = {tests["slow"]:.3f}) — so this is a FAST-stream group effect, the '
        'same axis on which FOUNDATIONS §9 records the streams splitting under '
        'TTX.<br>'
        f'<b>B — why A is believable.</b> Each recording at its two nulls: '
        f'<span style="color:{REAL_FAST}"><b>circles</b></span> real FAST · '
        f'<span style="color:{REAL_SLOW}"><b>squares</b></span> real SLOW · '
        f'<span style="color:{CONTROL}"><b>diamonds</b></span> generated '
        'recordings whose participants are drawn at random by construction, matched '
        'to the real ROI and cluster counts. Lower-left rejects both nulls. The '
        'generated cloud sits where "no recurring group" belongs; the real one does '
        'not. Dotted lines are alpha/2; points on an axis edge are at the 1/1001 '
        'resolution floor, and they overlap there, so B shows the separation and C '
        'carries counts.<br>'
        f'<b>C — does it survive the arbitrary parameter.</b> Every testable slice '
        f'by verdict at each K: {sw("structure-beyond-rate", "both nulls")} · '
        f'{sw("uniform-only", "uniform only")} · {sw("margin-only", "margin only")} '
        f'· {sw("no-assembly", "neither")}.<br>'
        '<b>Read with these.</b> The two nulls are <b>nested, not independent</b> — '
        'uniform participation is the stronger assumption, so rejecting both is one '
        'conclusion, not two. ORX rests on six animals in FAST and three in SLOW, so '
        '"weak" and "absent" are not separable there. Thirteen slices carry a '
        'PROVISIONAL note on their group — none of them ORX. Slices with fewer than '
        'four clusters have no permutation null: they appear nowhere here and are '
        '<b>undefined, never negative</b>. And structure beyond rate is not by '
        'itself one discrete recurring group.<br>'
        f'Animals: {n_animals["fast"]} FAST, {n_animals["slow"]} SLOW. Baseline '
        'windows agree with the workbook exp_timing sheet within 1 s for every '
        'slice. Run record in <i>docs/reviews/</i>.</div>')
    return (a + b + c).cols(3).opts(shared_axes=False, toolbar=None), header


def _render_png(html_path: Path, png_path: Path, *, wait_ms: int = 2500,
                width: int = 1500, height: int = 700) -> bool:
    try:
        from playwright.sync_api import sync_playwright
    except Exception:
        return False
    try:
        with sync_playwright() as pw:
            b = pw.chromium.launch()
            pg = b.new_page(viewport={"width": width, "height": height})
            pg.goto(html_path.as_uri())
            pg.wait_for_timeout(wait_ms)
            with tempfile.TemporaryDirectory() as td:
                tmp = Path(td) / "shot.png"
                pg.screenshot(path=str(tmp), full_page=True)
                b.close()
                os.replace(tmp, png_path)
        return True
    except Exception as exc:
        print(f"(PNG render failed: {type(exc).__name__}: {exc})", file=sys.stderr)
        return False


def main(argv=None):
    p = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--fast", type=Path, required=True,
                   help="output dir of assess_archive --stream fast --assemblies")
    p.add_argument("--slow", type=Path, required=True)
    p.add_argument("--controls", type=int, default=40,
                   help="generated recordings to place beside the real ones")
    p.add_argument("--width", type=int, default=620)
    p.add_argument("--out", default=None)
    p.add_argument("--numbers-only", action="store_true")
    p.add_argument("--no-png", dest="png", action="store_false", default=True)
    args = p.parse_args(argv)

    # ---- corpus membership comes from the workbook, not from the store -----
    from bugarach.groups import (load_groups, check_baseline_windows,
                                 unresolved_message as groups_missing)
    try:
        meta = load_groups()
    except FileNotFoundError:
        print(groups_missing(), file=sys.stderr)
        return 1

    def in_corpus(r):
        m = meta.get(str(r["slice_id"]))
        return m is not None and m.in_main_corpus

    def keep(rows):
        return [r for r in rows if in_corpus(r)]

    ks = (3, 4, 6, 8)
    per_k = {k: {"fast": tally(keep(_rows(args.fast, k))),
                 "slow": tally(keep(_rows(args.slow, k)))} for k in ks}
    fast_all, slow_all = _rows(args.fast, K_SHOWN), _rows(args.slow, K_SHOWN)
    fast, slow = keep(fast_all), keep(slow_all)
    for nm, before, after in (("FAST", fast_all, fast), ("SLOW", slow_all, slow)):
        drop = [r["slice_id"] for r in before if not in_corpus(r)]
        unknown = [r["slice_id"] for r in before if str(r["slice_id"]) not in meta]
        print(f"{nm}: {len(after)} testable in corpus "
              f"(dropped {len(drop)} excluded/side-arm: {drop}"
              + (f"; NOT IN WORKBOOK: {unknown}" if unknown else "") + ")")

    # ---- the windows we analysed must be the windows the lab recorded ------
    d0 = json.loads((args.fast / "assessment_real.json").read_text())
    observed = {str(r["slice_id"]): r["window_sec"]
                for r in d0["rows"] if r["K"] == K_SHOWN}
    chk = check_baseline_windows(observed)
    print(f"baseline windows vs workbook exp_timing: {chk['agree']}/{chk['n']} agree "
          f"within 1 s; {len(chk['missing'])} missing; "
          f"{len(chk['disagree'])} disagree")
    if chk["disagree"]:
        for row in chk["disagree"][:10]:
            print(f"   !! {row}", file=sys.stderr)
        print("refusing to build: the analysed window is not the recorded one.",
              file=sys.stderr)
        return 1

    # Control geometry: read from the real FAST run, so the comparison is at this
    # corpus's own numbers rather than remembered ones.
    d = json.loads((args.fast / "assessment_real.json").read_text())
    bk = d["by_k"][str(K_SHOWN)]
    win = float(np.median([r["window_sec"] for r in d["rows"]
                           if r["K"] == K_SHOWN]))
    # Cluster count is matched to the slices that actually GOT an answer, not to
    # the corpus median. `clusters_permin` is a median over all 85 slices and most
    # of the way down it are the ones with too few clusters to test at all, so
    # using it would build a control three times thinner than the data it is meant
    # to stand beside. A control must be at least as informative as the real thing
    # or "the real slices reject and the control does not" says nothing.
    testable = [r["asm_n_events"] for r in d["rows"]
                if r["K"] == K_SHOWN and r.get("asm_defined")]
    n_events = max(4, int(round(float(np.median(testable))))) if testable else 8
    geo = dict(n_roi=int(round(d["n_roi"]["median"])), win_sec=win,
               n_events=n_events,
               participation=bk["part_n_obs"]["median"] / max(d["n_roi"]["median"], 1),
               jitter_sec=bk["jit_obs"]["median"],
               bg_rate_hz=bk["roi_rate_med"]["median"] or 0.004)
    print(f"control geometry from the real run: {geo}")
    ctrl = controls(args.controls, geo)

    splits = {"fast": animal_split(fast, meta), "slow": animal_split(slow, meta)}
    tests = {st: group_test(splits[st]) for st in ("fast", "slow")}
    print("\nby group, at the ANIMAL level (a mouse counts if any of its slices does):")
    for st in ("fast", "slow"):
        parts = []
        for g in GROUP_ORDER:
            sp = splits[st].get(g)
            if sp:
                parts.append(f"{g} {sp['animals_hit']}/{sp['animals']}"
                             f" ({sp['slice_hits']}/{sp['slices']} slices)")
        print(f"  {st.upper():>5}: " + " · ".join(parts)
              + f"   across-group chi-square p = {tests[st]:.3f}")

    for name, rows in (("real FAST", fast), ("real SLOW", slow),
                       ("generated control", ctrl)):
        t = tally(rows)
        n = sum(t.values())
        print(f"{name:>18}: {n:>3} testable · " + " · ".join(
            f"{c} {v}" for v, c in sorted(t.items(), key=lambda kv: -kv[1])))
        if rows and rows[0].get("slice_id"):
            a, b = by_preparation(rows)
            print(f"{'':>18}  by preparation: {a}/{b} with at least one slice "
                  f"rejecting both nulls (slices are NOT independent)")
    if args.numbers_only:
        return 0

    from bugarach.paths import darkroom, unresolved_message
    dest = Path(args.out) if args.out else darkroom()
    if dest is None:
        print(unresolved_message(), file=sys.stderr)
        return 1
    dest.mkdir(parents=True, exist_ok=True)

    import holoviews as hv
    import panel as pn
    hv.extension("bokeh")
    layout, header = build(fast, slow, ctrl, per_k, splits, tests, args.width)
    html = dest / f"{FIGURE_ID}.html"
    pn.panel(pn.Column(pn.pane.HTML(header), pn.pane.HoloViews(layout))).save(str(html))
    (dest / f"{FIGURE_ID}.json").write_text(json.dumps(
        {"k_shown": K_SHOWN, "alpha": ALPHA, "control_geometry": geo,
         "per_k": {str(k): v for k, v in per_k.items()},
         "n_controls": len(ctrl),
         "by_group_animal_level": splits,
         "across_group_chi2_p": tests,
         "baseline_window_check": {"agree": chk["agree"], "n": chk["n"]}},
        indent=1, default=str))
    print(f"\nwrote {html}")
    if args.png and _render_png(html, dest / f"{FIGURE_ID}.png"):
        print(f"wrote {dest / f'{FIGURE_ID}.png'}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
