#!/usr/bin/env python3
"""The one-function bench's report: inputs before and after, settings and F1, the sensitivity check.

    python tools/one_function_bench_report.py [--root <darkroom folder>]

Reads, under ``--root`` (default ``<darkroom>/2026-09-28-one-function-bench``), what
``tools/extract_bench_inputs.py``, ``tools/search_all_settings.py`` and
``tools/score_bench_candidates.py`` wrote for ADR-0012, and the bench's present inputs
(``bench.INTERVALS_RUN`` and each stream's ``BENCH_RECORDING``), and writes ``README.md``,
``report.json`` and two figures (``figure1_gaps.svg``, ``figure2_sensitivity.svg``) into it.
"""
from __future__ import annotations

import argparse
import html
import importlib
import json
import math
import sys
from datetime import datetime, timezone
from pathlib import Path
from zoneinfo import ZoneInfo

import numpy as np

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / "src"))

ROOT_NAME = "2026-09-28-one-function-bench"
STREAMS = ("fast", "slow", "combined")
BENCHES = {"fast": "bugarach.bench", "slow": "bugarach.bench_slow",
           "combined": "bugarach.bench_combined"}
JITTER_RECORDS = {"fast": "docs/learned/bench_measured.json",
                  "slow": "docs/learned/bench_measured_slow.json",
                  "combined": "docs/learned/bench_measured_combined.json"}
PLAIN = {"win_sec": "window", "k_offset": "k", "merge_gap_sec": "merge gap", "alpha": "alpha",
         "int_win_sec": "integration window", "context_win_sec": "context window",
         "guard_sec": "guard", "min_rois": "minimum ROIs"}
UNIT = {"win_sec": " s", "merge_gap_sec": " s", "int_win_sec": " s", "context_win_sec": " s",
        "guard_sec": " s", "k_offset": " ROIs"}


def _load(p: Path):
    return json.loads(p.read_text(encoding="utf-8")) if p.exists() else None


def _f(x, nd=2):
    return "—" if x is None or (isinstance(x, float) and not math.isfinite(x)) else f"{x:.{nd}f}"


def clock() -> str:
    t = datetime.now(timezone.utc).astimezone(ZoneInfo("America/New_York"))
    return f"{t:%Y-%m-%d} {int(t.strftime('%I'))}:{t:%M %p %Z}"


def old_inputs() -> dict:
    """The bench's inputs before ADR-0012: the committed spacing and each stream's constants."""
    from bugarach import bench

    summ = _load(bench.INTERVALS_RUN / "summary.json")
    gaps = _load(bench.INTERVALS_RUN / "gaps_for_generator.json")
    out = {}
    for s in STREAMS:
        rec = importlib.import_module(BENCHES[s]).BENCH_RECORDING
        meas = (_load(REPO / JITTER_RECORDS[s]) or {}).get("values", {})
        g = next(d for d in gaps if d["stream"] == s)
        out[s] = dict(summary=summ["summary"][s], participation=list(rec["participation"]),
                      participation_measured=(meas.get("participation") or {}).get("measured"),
                      jitter_sec=rec["jitter_sec"], gaps=g["pooled"]["gaps_sec"])
    return out


def new_inputs(folder: Path) -> dict:
    summ = _load(folder / "summary.json")
    gaps = _load(folder / "gaps_for_generator.json")
    bi = _load(folder / "bench_inputs.json")
    cal = _load(folder / "calibration.json")
    out = {}
    for s in STREAMS:
        g = next(d for d in gaps if d["stream"] == s)
        out[s] = dict(summary=summ["summary"][s], participation=bi["streams"][s]["participation"],
                      jitter_sec=bi["streams"][s].get("jitter_sec"), gaps=g["pooled"]["gaps_sec"],
                      calibration=(cal or {}).get(s))
    return out


def setting_words(params: dict | None) -> str:
    if not params:
        return "—"
    keys = [k for k in PLAIN if k in params and k != "min_rois"]
    return ", ".join(f"{PLAIN[k]} {params[k]:g}{UNIT.get(k, '')}" for k in keys)


def scored(path: Path) -> dict | None:
    """Per stream: count (sliding) and CoactDetect, shipped and as searched, fresh-seed F1 and ΔF1
    against CoactDetect shipped, with the setting."""
    c = _load(path / "candidates.json")
    if c is None:
        return None
    out = {}
    for s in STREAMS:
        res, meta = c["results"].get(s, {}), c["benches"].get(s, {})
        rows = {}
        for det in ("count_sliding", "coact"):
            m = (meta.get("detectors") or {}).get(det, {})
            prop = m.get("proposal") or {}
            for which in ("shipped", "proposal"):
                r = res.get(f"{det}:{which}")
                if r is None:
                    continue
                pf = (r.get("paired_f1_vs_coact") or {}).get("shipped") or {}
                params = m.get("shipped") if which == "shipped" else prop.get("params")
                q, b = r.get("baseline_quiet") or {}, r.get("baseline_busy") or {}
                rows[f"{det}:{which}"] = dict(
                    prec_q=q.get("precision"), prec_b=b.get("precision"),
                    rec_q=q.get("recall"), rec_b=b.get("recall"),
                    swing=abs(q["precision"] - b["precision"])
                    if q.get("precision") is not None and b.get("precision") is not None else None,
                    f1=r.get("mean_f1"), f1_wo=r.get("mean_f1_without_decoys"),
                    d_mid=pf.get("mid"), d_lo=pf.get("lo"), d_hi=pf.get("hi"),
                    params=params, bracketed=(prop.get("bracketing") or {}).get("bracketed")
                    if which == "proposal" else None)
            if f"{det}:proposal" not in res and prop.get("name") == "shipped":
                rows[f"{det}:proposal"] = dict(rows.get(f"{det}:shipped", {}), same_as_shipped=True)
        out[s] = rows
    return dict(rows=out, seeds=c.get("seeds_by_bench"), dataset=(c.get("dataset")))


# --------------------------------------------------------------------------------------------
# figures, drawn as SVG: no plotting dependency, the page's own colors in both themes
# --------------------------------------------------------------------------------------------

STYLE = ("<style>.t{fill:var(--fg,#222)} .m{fill:var(--muted,#666)} .ax{stroke:var(--line,#ccc)}"
         " .old{stroke:#888;fill:none} .new{stroke:#0072B2;fill:none} .sen{stroke:#D55E00;fill:none}"
         " .dot-old{fill:#888} .dot-new{fill:#0072B2} .dot-sen{fill:#D55E00}</style>")


def figure_gaps(old: dict, new: dict, sens: dict | None, dest: Path) -> Path:
    """Figure 1: the cumulative share of gaps up to each length, log time axis, one panel per
    stream: the present spacing, count (sliding)'s, and CoactDetect shipped's."""
    W, H, L, R, T, B = 1080, 360, 70, 20, 40, 60
    pw = (W - L - R - 2 * 40) / 3
    lo, hi = 1.0, 3000.0
    ticks = (1, 3, 10, 30, 60, 120, 300, 1200)
    tl = {1: "1s", 3: "3s", 10: "10s", 30: "30s", 60: "1m", 120: "2m", 300: "5m", 600: "10m",
          1200: "20m"}

    def X(v, k):
        return L + k * (pw + 40) + (math.log10(max(v, lo)) - math.log10(lo)) / (
            math.log10(hi) - math.log10(lo)) * pw

    def Y(q):
        return T + (1 - q) * (H - T - B)

    out = [f"<svg xmlns='http://www.w3.org/2000/svg' width='{W}' height='{H}' viewBox='0 0 {W} {H}' "
           "font-family='system-ui, sans-serif' font-size='14' role='img' aria-label='Figure 1, "
           "the gaps between planted events, before and after'>", STYLE]
    series = [("old", "present bench (no detector)", old), ("new", "count (sliding) at its defaults", new)]
    if sens:
        series.append(("sen", "CoactDetect shipped (sensitivity)", sens))
    x = L
    for cls, name, _ in series:
        out.append(f"<line class='{cls}' x1='{x}' x2='{x + 24}' y1='16' y2='16' stroke-width='3'/>"
                   f"<text class='t' x='{x + 30}' y='21'>{html.escape(name)}</text>")
        x += 40 + 8 * len(name)
    for k, s in enumerate(STREAMS):
        x0 = L + k * (pw + 40)
        for q in (0, 0.25, 0.5, 0.75, 1.0):
            out.append(f"<line class='ax' x1='{x0}' x2='{x0 + pw}' y1='{Y(q):.1f}' y2='{Y(q):.1f}' "
                       f"stroke-width='0.6'/>")
            if k == 0:
                out.append(f"<text class='m' x='{x0 - 8}' y='{Y(q) + 5:.1f}' text-anchor='end'>"
                           f"{q:.2f}</text>")
        for t in ticks:
            out.append(f"<line class='ax' x1='{X(t, k):.1f}' x2='{X(t, k):.1f}' y1='{T}' "
                       f"y2='{H - B}' stroke-width='0.6'/><text class='m' x='{X(t, k):.1f}' "
                       f"y='{H - B + 18}' text-anchor='middle'>{tl[t]}</text>")
        out.append(f"<text class='t' x='{x0 + pw / 2}' y='{H - 12}' text-anchor='middle'>{s} stream: "
                   f"gap between events</text>")
        for cls, _, src in series:
            g = np.sort(np.asarray(src[s]["gaps"], float))
            if not g.size:
                continue
            q = np.arange(1, g.size + 1) / g.size
            pts = " ".join(f"{X(a, k):.1f},{Y(b):.1f}" for a, b in zip(g, q))
            out.append(f"<polyline class='{cls}' points='{pts}' stroke-width='2'/>")
    out.append(f"<text class='t' x='16' y='{(T + H - B) / 2}' transform='rotate(-90 16 "
               f"{(T + H - B) / 2})' text-anchor='middle'>share of gaps up to this length</text>")
    out.append("</svg>")
    p = dest / "figure1_gaps.svg"
    p.write_text("\n".join(out), encoding="utf-8")
    return p


def figure_sensitivity(main: dict, sens_main: dict | None, sens_re: dict | None, dest: Path) -> Path:
    """Figure 2: fresh-seed F1 per stream: count (sliding) as chosen on the count-extracted bench,
    scored there and on the CoactDetect-extracted bench, and retuned on the latter; CoactDetect
    shipped on each bench for reference."""
    W, H, L, R, T, B = 1080, 330, 380, 30, 50, 50
    rows = []
    for s in STREAMS:
        rows.append((f"{s} · count (sliding), chosen here", "dot-new",
                     main["rows"][s].get("count_sliding:proposal", {}).get("f1")))
        if sens_main:
            rows.append((f"{s} · same setting, CoactDetect-spaced bench", "dot-sen",
                         sens_main["rows"][s].get("count_sliding:proposal", {}).get("f1")))
        if sens_re:
            rows.append((f"{s} · retuned on CoactDetect-spaced bench", "dot-sen",
                         sens_re["rows"][s].get("count_sliding:proposal", {}).get("f1")))
        rows.append((f"{s} · CoactDetect shipped, this bench", "dot-old",
                     main["rows"][s].get("coact:shipped", {}).get("f1")))
    vals = [v for _, _, v in rows if v is not None]
    lo = math.floor(min(vals) * 20) / 20 if vals else 0.5
    hi = 1.0
    H = T + 24 * len(rows) + B

    def X(v):
        return L + (v - lo) / (hi - lo) * (W - L - R)

    out = [f"<svg xmlns='http://www.w3.org/2000/svg' width='{W}' height='{H}' viewBox='0 0 {W} {H}' "
           "font-family='system-ui, sans-serif' font-size='14' role='img' aria-label='Figure 2, "
           "the sensitivity check'>", STYLE]
    t = lo
    while t <= hi + 1e-9:
        out.append(f"<line class='ax' x1='{X(t):.1f}' x2='{X(t):.1f}' y1='{T - 10}' y2='{H - B}' "
                   f"stroke-width='0.6'/><text class='m' x='{X(t):.1f}' y='{H - B + 18}' "
                   f"text-anchor='middle'>{t:.2f}</text>")
        t = round(t + 0.05, 2)
    y = T
    for name, cls, v in rows:
        out.append(f"<text class='t' x='{L - 12}' y='{y + 5}' text-anchor='end'>{html.escape(name)}</text>")
        if v is not None:
            out.append(f"<circle class='{cls}' cx='{X(v):.1f}' cy='{y}' r='6'/>"
                       f"<text class='m' x='{X(v) + 10:.1f}' y='{y + 5}'>{v:.3f}</text>")
        y += 24
    out.append(f"<text class='t' x='{(L + W - R) / 2}' y='{H - 10}' text-anchor='middle'>fresh-seed "
               f"F1 (mean over the quiet and busy backgrounds)</text></svg>")
    p = dest / "figure2_sensitivity.svg"
    p.write_text("\n".join(out), encoding="utf-8")
    return p


# --------------------------------------------------------------------------------------------
# README
# --------------------------------------------------------------------------------------------

def readme(m: dict) -> str:
    L = []
    L.append("# One function builds the bench and is the detector\n")
    L.append(f"WSMIP065, built {m['built']}. **Working material, not murderboarded.** ADR-0012 "
             "(Proposed). Dataset `" + m["dataset"]["name"] + f"` ({m['dataset']['recordings']} "
             "recordings, baseline windows only). Every number is in `report.json`.\n")
    L.append("## In plain words\n")
    L.append(m["plain"] + "\n")
    n = 1
    L.append("## 1. The inputs, before and after\n")
    L.append("*Before*: the bench as it stands (ADR-0010 part 2): spacing from runs of the 2 s "
             "co-active count at or above each window's floor, placed at each run's peak and "
             "merged under 2 s apart; participation from moments with at least 4 ROIs co-active "
             "within 1 s; timing spread from the cross-ROI onset correlogram. *After*: count "
             "(sliding) at its untuned defaults, the same on every stream (2 s window, the "
             "window's own ADR-0008 floor, k 0, merge 3 s), gives all three: gaps between "
             "neighbouring calls measured call start to call start; participation as the median "
             "of each call's peak distinct-ROI count over the window's ROIs (the outer two planted "
             "levels keep the bench's present ratios to the middle, which were chosen, not "
             "measured, capped at 0.95); and timing spread as the median within-call SD of the "
             "participating ROIs' first onsets, calibrated to the generator's `jitter_sec` by "
             "running the same extractor on bench recordings planted at known jitter "
             "(`calibration.json`).\n")
    L.append(f"**Table {n}.** Pooled over the four groups, baseline windows.\n")
    L.append("| stream | inputs | events per hour | gap p5 | p25 | median | p75 | p95 | gaps under 10 s "
             "| participation (middle level) | planted levels | jitter_sec |")
    L.append("|---|---|---|---|---|---|---|---|---|---|---|---|")
    for s in STREAMS:
        for tag, d in (("before", m["old"][s]), ("after", m["new"][s])):
            a = d["summary"]["all"]
            part = d["participation"][len(d["participation"]) // 2]
            L.append(f"| {s} | {tag} | {_f(a.get('events_per_hour'), 1)} per hour | "
                     + " | ".join(f"{_f(a.get(k), 1)} s" for k in ("p5", "p25", "p50", "p75", "p95"))
                     + f" | {_f(100 * a['share_under_10_sec'], 0) if a.get('share_under_10_sec') is not None else '—'}% "
                     f"| {_f(part)} | {' / '.join(_f(x) for x in d['participation'])} | "
                     f"{_f(d['jitter_sec'], 3)} s |")
    L.append("")
    n += 1
    L.append(f"**Table {n}.** After, by group (DI, OVX, MALE, ORX): events per hour, median gap, "
             "and median participation share.\n")
    groups = m["groups"]
    L.append("| stream | " + " | ".join(groups) + " |")
    L.append("|---|" + "---|" * len(groups))
    for s in STREAMS:
        gs = m["new"][s]["summary"]["groups"]
        L.append(f"| {s} | " + " | ".join(
            f"{_f(gs[g].get('events_per_hour'), 1)} per hour, {_f(gs[g].get('p50'), 1)} s, "
            f"{_f(gs[g].get('participation_median'))}" if g in gs else "—" for g in groups) + " |")
    L.append("")
    L.append("![Figure 1](figure1_gaps.svg)\n")
    L.append("**Figure 1. The gaps between planted events.** For each stream, the share of gaps up "
             "to each length (log time axis): the bench as it stands (gray), count (sliding) at its "
             "defaults (blue), and CoactDetect shipped as the extractor, the sensitivity check "
             "(orange). The 3 s merge means no gap under 3 s survives count (sliding)'s "
             "extraction.\n")
    n += 1
    L.append("## 2. Retuned on the rebuilt benches\n")
    L.append(f"**Table {n}.** Fresh-seed F1 (seeds neither the search nor the extraction saw; mean "
             "over the quiet and busy backgrounds) and paired ΔF1 against CoactDetect shipped "
             "with its 95% interval. \"As searched\" is the setting the search chose on that "
             "stream's rebuilt bench, the floor kept out of the search.\n")
    L.append("| stream | detector | setting | F1 | ΔF1 vs CoactDetect shipped [95%] | precision, quiet · "
             "busy (swing) | recall, quiet · busy | bracketed |")
    L.append("|---|---|---|---|---|---|---|---|")
    for s in STREAMS:
        r = m["main"]["rows"][s]
        for key, name in (("count_sliding:proposal", "count (sliding), as searched"),
                          ("count_sliding:shipped", "count (sliding), defaults"),
                          ("coact:proposal", "CoactDetect, retuned"),
                          ("coact:shipped", "CoactDetect, shipped")):
            v = r.get(key)
            if not v:
                continue
            br = v.get("bracketed")
            sw = v.get("swing")
            over = " ⚠ over the 0.10 limit" if sw is not None and sw > 0.10 else ""
            L.append(f"| {s} | {name} | {setting_words(v.get('params'))} | {_f(v.get('f1'), 3)} | "
                     f"{_f(v.get('d_mid'), 3)} [{_f(v.get('d_lo'), 3)}, {_f(v.get('d_hi'), 3)}] | "
                     f"{_f(v.get('prec_q'))} · {_f(v.get('prec_b'))} ({_f(sw, 3)}{over}) | "
                     f"{_f(v.get('rec_q'))} · {_f(v.get('rec_b'))} | "
                     f"{'—' if br is None else ('yes' if br else 'no')} |")
    L.append("")
    if m.get("diag"):
        d = m["diag"]
        L.append(f"**Why CoactDetect did not move on fast.** Its search ran one round and moved "
                 f"nothing. Rerun with every candidate logged (`diagnostics/`): "
                 f"{d['refused_better']} candidates scored above the shipped point on the search's "
                 f"selection seeds (up to F1 {d['best_refused_f1']:.3f}) and every one was refused "
                 f"for precision swing ({d['swing_lo']:.3f} to {d['swing_hi']:.3f} against a limit "
                 f"of 0.10, the same limit count (sliding) is held to); the shipped point itself "
                 f"sits at {d['shipped_swing']:.3f} there and {d['fresh_shipped_swing']:.3f} on the "
                 "fresh seeds. So on fast the comparison is decided by that budget, not by F1 "
                 "alone: count (sliding) reaches its setting with a swing near zero, and "
                 "CoactDetect cannot get there within the limit. The limit was set on the old "
                 "bench; whether it should hold on this one is a question, not an answer here.\n")
    n += 1
    L.append("## 3. Sensitivity: CoactDetect shipped builds the spacing instead\n")
    L.append("The spacing alone is rebuilt with CoactDetect at its shipped setting as the "
             "extractor (same floor, same windows); participation and jitter stay count "
             "(sliding)'s, so only the gaps differ. count (sliding) is then scored at the setting "
             "chosen in section 2, and retuned on that bench.\n")
    L.append(f"**Table {n}.** count (sliding), fresh-seed F1.\n")
    L.append("| stream | setting chosen on count's bench | F1 there | F1 on CoactDetect-spaced bench | "
             "retuned there | F1 retuned | CoactDetect shipped there |")
    L.append("|---|---|---|---|---|---|---|")
    for s in STREAMS:
        a = m["main"]["rows"][s].get("count_sliding:proposal", {})
        b = (m["sens_main"] or {"rows": {s: {}}})["rows"][s].get("count_sliding:proposal", {})
        c = (m["sens_re"] or {"rows": {s: {}}})["rows"][s].get("count_sliding:proposal", {})
        k = (m["sens_main"] or {"rows": {s: {}}})["rows"][s].get("coact:shipped", {})
        L.append(f"| {s} | {setting_words(a.get('params'))} | {_f(a.get('f1'), 3)} | "
                 f"{_f(b.get('f1'), 3)} | {setting_words(c.get('params'))} | {_f(c.get('f1'), 3)} | "
                 f"{_f(k.get('f1'), 3)} |")
    L.append("")
    L.append("![Figure 2](figure2_sensitivity.svg)\n")
    L.append("**Figure 2. The sensitivity check.** Fresh-seed F1 per stream: count (sliding) at the "
             "setting chosen on its own bench (blue), the same setting on the bench whose spacing "
             "CoactDetect shipped extracted and count (sliding) retuned there (orange), and "
             "CoactDetect shipped on count's bench (gray).\n")
    L.append("## Limits\n")
    for x in m["limits"]:
        L.append(f"- {x}")
    L.append("\n## Where everything is\n")
    L.append("- `inputs-count_sliding/`, `inputs-coact_shipped/`: the extracted inputs (the bench "
             "reads them through `BUGARACH_BENCH_INPUTS`), with `calls.csv`, `calibration.json`.\n"
             "- `main/search-<stream>/<detector>/`, `sensitivity/search-<stream>/count_sliding/`: "
             "the searches.\n- `main/fresh/`, `sensitivity/fresh-main-settings/`, "
             "`sensitivity/fresh-retuned/`: the fresh-seed scorings (`candidates.json`).\n"
             "- Tools: `tools/extract_bench_inputs.py`, `tools/search_all_settings.py`, "
             "`tools/score_bench_candidates.py`, `tools/one_function_bench_report.py`.")
    return "\n".join(L) + "\n"


def diagnostic(root: Path, main_: dict | None) -> dict | None:
    """What the logged rerun of the fast CoactDetect search says about why it did not move."""
    p = root / "diagnostics" / "coact_fast_candidates.jsonl"
    srch = _load(root / "main" / "search-fast" / "coact" / "search.json")
    if not p.exists() or srch is None:
        return None
    rows = [json.loads(x) for x in p.read_text(encoding="utf-8").splitlines() if x.strip()]
    for r in rows:
        r["swing"] = abs(r["precision_quiet"] - r["precision_busy"])
    ship_f1 = srch["selection"]["coact"]["shipped"]
    ship = min(rows, key=lambda r: abs(r["mean_f1"] - ship_f1))
    refused = [r for r in rows if not r["ok"] and r["mean_f1"] > ship_f1]
    if not refused:
        return None
    fresh = ((main_ or {}).get("rows", {}).get("fast", {}).get("coact:shipped") or {}).get("swing")
    return dict(refused_better=len(refused), best_refused_f1=max(r["mean_f1"] for r in refused),
                swing_lo=min(r["swing"] for r in refused), swing_hi=max(r["swing"] for r in refused),
                shipped_swing=ship["swing"], fresh_shipped_swing=fresh or float("nan"),
                candidates=len(rows))


def main(argv=None) -> int:
    from bugarach.groups import in_group_order
    from bugarach.paths import darkroom, unresolved_message

    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("--root", type=Path, default=None)
    a = ap.parse_args(argv)
    if a.root is None:
        r = darkroom()
        if r is None:
            print(unresolved_message(), file=sys.stderr)
            return 2
        a.root = r / ROOT_NAME
    old = old_inputs()
    new = new_inputs(a.root / "inputs-count_sliding")
    sens_in = new_inputs(a.root / "inputs-coact_shipped") if (a.root / "inputs-coact_shipped").exists() else None
    main_ = scored(a.root / "main" / "fresh")
    sm = scored(a.root / "sensitivity" / "fresh-main-settings")
    sr = scored(a.root / "sensitivity" / "fresh-retuned")
    summ = _load(a.root / "inputs-count_sliding" / "summary.json")
    groups = in_group_order(summ.get("groups") or [])
    figure_gaps(old, new, sens_in, a.root)
    if main_:
        figure_sensitivity(main_, sm, sr, a.root)
    diag = diagnostic(a.root, main_)
    plain, limits = interpret(old, new, sens_in, main_, sm, sr, diag)
    m = dict(built=clock(), dataset=summ["dataset"], old=old, new=new, sens_inputs=sens_in,
             main=main_, sens_main=sm, sens_re=sr, groups=groups, plain=plain, limits=limits,
             diag=diag)
    slim = {k: v for k, v in m.items() if k not in ("old", "new", "sens_inputs")}
    slim["inputs"] = {tag: {s: {k: v for k, v in d[s].items() if k != "gaps"} for s in STREAMS}
                      for tag, d in (("before", old), ("after", new), ("sensitivity", sens_in)) if d}
    (a.root / "report.json").write_text(json.dumps(slim, indent=1, default=str) + "\n", encoding="utf-8")
    (a.root / "README.md").write_text(readme(m), encoding="utf-8")
    print(f"wrote {a.root / 'README.md'}")
    return 0


def interpret(old, new, sens_in, main_, sm, sr, diag=None) -> tuple[str, list[str]]:
    """The plain-language paragraph and the limits, each number read from the results."""
    parts = []
    for s in STREAMS:
        o, nw = old[s]["summary"]["all"], new[s]["summary"]["all"]
        parts.append(f"{s} {_f(o['events_per_hour'], 1)} → {_f(nw['events_per_hour'], 1)} events per "
                     f"hour, participation {_f(old[s]['participation'][1])} → "
                     f"{_f(new[s]['participation'][1])}, jitter {_f(old[s]['jitter_sec'], 3)} → "
                     f"{_f(new[s]['jitter_sec'], 3)} s")
    txt = ("The bench's three real-data inputs now come from one function, count (sliding), at one "
           "setting fixed in advance and shared by every stream (2 s window, each window's own "
           "floor, k 0, merge 3 s). Against the bench as it stood: " + "; ".join(parts) + ". ")
    if main_:
        f = []
        for s in STREAMS:
            r = main_["rows"][s]
            f.append(f"{s} count (sliding) {_f(r.get('count_sliding:proposal', {}).get('f1'), 3)} "
                     f"against CoactDetect retuned {_f(r.get('coact:proposal', {}).get('f1'), 3)} "
                     f"and shipped {_f(r.get('coact:shipped', {}).get('f1'), 3)}")
        txt += "Retuned on the rebuilt benches, fresh-seed F1: " + "; ".join(f) + ". "
        same = [s for s in STREAMS
                if main_["rows"][s].get("count_sliding:proposal", {}).get("prec_q") is not None
                and all(abs((main_["rows"][s]["count_sliding:proposal"].get(k) or 0)
                            - (main_["rows"][s].get("coact:proposal", {}).get(k) or 0)) < 0.002
                        for k in ("prec_q", "prec_b", "rec_q", "rec_b"))]
        if same:
            txt += (f"On {' and '.join(same)}, count (sliding) and retuned CoactDetect end up making "
                    "the same calls: their precision and recall agree to the second decimal on "
                    "both backgrounds. ")
        if diag:
            txt += (f"On fast the gap is a budget, not a detector: CoactDetect's search found "
                    f"{diag['refused_better']} settings that score better and every one breaks the "
                    f"precision-swing limit of 0.10 ({diag['swing_lo']:.3f} to {diag['swing_hi']:.3f}), "
                    "so it stays at its shipped setting, whose swing is itself "
                    f"{diag['fresh_shipped_swing']:.3f} on the fresh seeds; count (sliding) gets "
                    "to its setting with a swing near zero. ")
    if main_ and sm and sr:
        mv = []
        for s in STREAMS:
            a = main_["rows"][s].get("count_sliding:proposal", {}).get("f1")
            b = sm["rows"][s].get("count_sliding:proposal", {}).get("f1")
            c = sr["rows"][s].get("count_sliding:proposal", {}).get("f1")
            same = (main_["rows"][s].get("count_sliding:proposal", {}).get("params") ==
                    sr["rows"][s].get("count_sliding:proposal", {}).get("params"))
            mv.append(f"{s} F1 {_f(a, 3)} → {_f(b, 3)} at the same setting, {_f(c, 3)} retuned "
                      f"({'the same setting' if same else 'a different setting'})")
        txt += ("With CoactDetect shipped building the spacing instead: " + "; ".join(mv) + ".")
    limits = [
        "The extraction's participation is higher than the old measure's by construction: a call "
        "has to reach the window's floor, where the old measure counted any moment with 4 or more "
        "ROIs co-active within 1 s. The high planted level is capped at 0.95 on slow and combined.",
        "The calibrated jitter comes from one statistic run through one generator; it disagrees "
        "with the correlogram's measure (Table 1, before) by a factor of about 2 to 3, and which "
        "one is right about real events is not settled here.",
        "No gap under the 3 s merge exists on the rebuilt bench: count (sliding) cannot see one, so "
        "the bench no longer plants one. That is the price of the extractor being the detector, "
        "said openly (ADR-0012).",
        "Fresh-seed intervals cover simulation seeds only; nothing here is a treatment-effect "
        "claim.",
    ]
    return txt, limits


if __name__ == "__main__":
    raise SystemExit(main())
