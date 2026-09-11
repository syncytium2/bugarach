#!/usr/bin/env python3
"""Write the surrogate screen's reports: one page per folder and a cross-folder summary.

    python tools/build_surrogate_report.py                 # darkroom run folder, gate on
    python tools/build_surrogate_report.py --run DIR --no-gate

**Describes; decides nothing.** The plan
(``docs/proposals/2026-09-10-surrogate-evaluation-overnight.md``, "The report")
measures every candidate and shortlists none: the rule that turns these numbers
into a shortlist is designed afterwards, from them. So every page opens with an
executive summary of what each candidate keeps and destroys, puts the three
yardsticks side by side, and ends its argument with **the choices the verdict rule
must make, each beside the measurement that bears on it** — never with a verdict.

Reads what ``tools/build_surrogate_screen.py`` wrote under ``--run`` (default
``darkroom()/2026-09-11-surrogate-screen/``) and writes there too: aggregates from
real recordings stay in the darkroom (FOUNDATIONS §5), and nothing this writes is
meant for a git tree.

* ``report_<role>.html`` for each folder present, ``report_summary.html`` across them.
* Figures are **inline SVG only**, numbered, referred to by number and name. The first
  three are synthetic — a surrogate and its leak, what each candidate does to one
  ROI, the window anatomy — so no figure of a real recording is drawn at all. Time
  axes use :mod:`bugarach.time_axis`, the viewer's own tick rule.
* **A page with no SVG is refused**: the render gate would pass it, and a report
  whose figures failed to draw would read as a report with nothing to show.
* **The render gate** runs only from stamped copies in ``<run>/tools/`` —
  ``render_check.py`` (canonical in downLow) and ``edge_collisions.py``
  (draughtsman) — so their screenshots land in the run folder, never in a git tree.
  Missing copies are an error, not a silent pass. ⚠ ``edge_collisions.py`` checks
  only draughtsman-style edges (``ds-edge`` paths); these figures have none, so it
  can pass them without having looked at anything, and the gate record says so.
  No tool catches text crossing a shape: a person looks at the screenshots.
"""

from __future__ import annotations

import argparse
import csv
import html
import json
import math
import re
import subprocess
import sys
import time
from collections import defaultdict
from pathlib import Path

import numpy as np

from bugarach import time_axis

OUT_DIRNAME = "2026-09-11-surrogate-screen"
ALPHA = 0.05

# ---- names, in the plan's words (Table 1, Table 2, Table 3) -----------------

CANDIDATES = [
    ("uniform_dither", "uniform dither (UD)"),
    ("shipped_dither", "shipped dither"),
    ("dead_time_dither", "dither with dead time (UDD)"),
    ("circular_shift", "circular shift"),
    ("rigid_shift", "rigid shift"),
    ("trial_shift", "trial shifting (TR-SHIFT)"),
    ("joint_isi", "joint-ISI dither (JISI-D)"),
    ("isi_dither", "ISI dither (ISI-D)"),
    ("interval_jitter", "interval jitter"),
    ("window_shuffle", "window shuffling (WIN-SHUFF)"),
    ("pattern_jitter", "pattern jitter"),
    ("operational_time", "operational-time dither"),
]
CONTROLS = [
    ("do_nothing", "do-nothing"),
    ("interval_shuffle", "interval shuffle"),
    ("homogeneous_resample", "homogeneous resample"),
    ("edge_thinning", "edge thinning"),
    ("edge_piling", "edge piling"),
    ("window_circular_shift", "per-window circular shift"),
]
NAME = dict(CANDIDATES + CONTROLS)

STAT_LABEL = {
    "subfloor": "sub-floor interval rate",
    "band_f_2f": "interval density from f to 2f",
    "inside_width": "intervals inside the preceding event",
    "ks_intervals": "per-ROI interval distribution (KS distance)",
    "serial_dependence": "serial dependence of intervals",
    "fano_60s": "rate profile: Fano factor",
    "count_ac1_60s": "rate profile: count autocorrelation",
    "edge_density": "edge-band density, generation window",
    "edge_density_analysis": "edge-band density, analysis windows",
}


def stat_label(stat: str) -> str:
    base, _, at = stat.partition("@")
    lab = STAT_LABEL.get(base, base)
    return f"{lab} at f = {at} × floor" if at else lab


# ---- reading ----------------------------------------------------------------

def _rows(path: Path) -> list[dict]:
    if not path.is_file():
        return []
    with open(path, encoding="utf-8", newline="") as fh:
        return list(csv.DictReader(fh))


def _f(x) -> float:
    try:
        v = float(x)
    except (TypeError, ValueError):
        return float("nan")
    return v


def _b(x) -> bool:
    return str(x).strip().lower() in ("true", "1")


def load_role(run: Path, role: str) -> dict:
    d = run / role
    meta = json.loads((d / "meta.json").read_text(encoding="utf-8")) \
        if (d / "meta.json").is_file() else {}
    mac = d / "meta.mac-2026-09-11.json"
    return {
        "role": role, "meta": meta,
        "meta_mac": json.loads(mac.read_text(encoding="utf-8")) if mac.is_file() else None,
        "cells": _rows(d / "cells.csv"), "stats": _rows(d / "stats.csv"),
        "destruction": _rows(d / "destruction.csv"),
        "yardsticks": _rows(d / "yardsticks.csv"),
        "power": _rows(d / "control_power.csv"),
        "disc": _rows(run / "discriminator" / role / "discriminator.csv"),
    }


# ---- aggregation ------------------------------------------------------------

def streams_of(R: dict) -> list[str]:
    return sorted({c["stream"] for c in R["cells"]}, key=lambda s: ("fast", "slow",
                                                                    "events").index(s)
                  if s in ("fast", "slow", "events") else 9)


def candidate_rows(R: dict, stream: str) -> list[dict]:
    """One row per candidate: cells, movement, leak flags, destruction, discriminator, cost."""
    cells = [c for c in R["cells"] if c["stream"] == stream]
    ok_ids = {c["cell_id"] for c in cells if c["status"] == "ok"}
    stats = [s for s in R["stats"] if s["stream"] == stream and s["scope"] == "all"
             and s["cell_id"] in ok_ids]
    dest = [r for r in R["destruction"] if r["stream"] == stream
            and _b(r.get("planted_visible")) and not _b(r.get("freeze_half"))]
    disc = [r for r in R["disc"] if r["stream"] == stream]
    out = []
    for name, label in CANDIDATES + CONTROLS:
        mine = [c for c in cells if c["name"] == name]
        if not mine:
            continue
        ok = [c for c in mine if c["status"] == "ok"]
        st = [s for s in stats if s["name"] == name]

        def share(pred):
            v = [pred(s) for s in st]
            return (sum(v) / len(v)) if v else float("nan")

        # A statistic "gives a candidate away" when its raw paired P is under alpha in
        # at least half of the candidate's scored cells. Raw, because the Holm-adjusted
        # P cannot reach alpha at these settings (see yardstick_reach); half, because
        # at 65 checks a cell yields a raw flag by chance now and then.
        per_stat = defaultdict(list)
        for s in st:
            per_stat[s["stat"]].append(_f(s["paired_p"]) < ALPHA)
        flagged_paired = sorted(k for k, v in per_stat.items() if v and sum(v) / len(v) >= 0.5)
        all_stats = sorted(per_stat)
        ret = defaultdict(list)
        for r in dest:
            if r["name"] == name and r["cell_id"] in ok_ids:
                ret[r["participation"]].append(_f(r["retained"]))
        dsc = [r for r in disc if r["name"] == name and r["status"] == "ok"]
        acc = [_f(r["accuracy"]) for r in dsc]
        Js = sorted({_f(c["J"]) for c in mine if c["J"] not in ("", None)})
        out.append({
            "name": name, "label": label,
            "kind": "control" if name in dict(CONTROLS) else "candidate",
            "n_cells": len(mine), "n_ok": len(ok),
            "n_intractable": sum(c["status"] == "intractable" for c in mine),
            "J": Js, "J_unit": mine[0]["J_unit"],
            "rms_disp": _med([_f(c.get("movement_rms_disp_frames")) for c in ok]),
            "share_unchanged": _med([_f(c.get("movement_share_rois_unchanged")) for c in ok]),
            "band_q95": share(lambda s: _b(s["band_flag"])),
            "band_raw": share(lambda s: _f(s["band_p"]) < ALPHA),
            "band_holm": share(lambda s: _f(s["band_p_holm"]) < ALPHA),
            "paired_raw": share(lambda s: _f(s["paired_p"]) < ALPHA),
            # 2/(K + 1) < alpha needs K > 39: below that the raw paired P cannot flag,
            # and a candidate whose every cell stopped there reads 0% for that reason.
            "paired_reachable": any(_f(c["K"]) > 2 / ALPHA - 1 for c in ok),
            "paired_holm": share(lambda s: _f(s["paired_p_holm"]) < ALPHA),
            "n_checks": len(st),
            "flagged": flagged_paired,
            "kept": [s for s in all_stats if s not in flagged_paired],
            "retained": {p: _summ(v) for p, v in ret.items()},
            "disc_acc": _summ(acc),
            "disc_sig": (sum(_b(r["significant"]) for r in dsc) / len(dsc)) if dsc else float("nan"),
            "disc_void": (sum(_b(r["void"]) for r in dsc) / len(dsc)) if dsc else float("nan"),
            "disc_n": len(dsc),
            "cost": _med([_f(c["seconds_per_roi_per_draw"]) for c in ok]),
            "K": _med([_f(c["K"]) for c in ok]),
        })
    return out


def _med(v):
    v = [x for x in v if isinstance(x, float) and math.isfinite(x)]
    return float(np.median(v)) if v else float("nan")


def _summ(v):
    v = [x for x in v if math.isfinite(x)]
    if not v:
        return None
    return {"min": min(v), "med": float(np.median(v)), "max": max(v), "n": len(v)}


def power_rows(R: dict, stream: str) -> list[dict]:
    rows = [r for r in R["power"] if r["stream"] == stream and r["scope"] == "all"]
    return [{"control": r["control"], "cell": r["cell_id"], "stat": r["stat"],
             "paired": _b(r["moved_paired"]), "band": _b(r["band_flag"]),
             "p": _f(r["paired_p"])} for r in rows]


def yard_rows(R: dict, stream: str) -> list[dict]:
    return [{"stat": r["stat"], "hb": _f(r["neg_heldout_band"]),
             "hp": _f(r["neg_heldout_paired"]), "sb": _f(r["neg_synthetic_band"]),
             "sp": _f(r["neg_synthetic_paired"]), "n": r["n_splits"]}
            for r in R["yardsticks"] if r["stream"] == stream and r["scope"] == "all"]


def yardstick_reach(R: dict) -> dict:
    """What each yardstick COULD flag at the run's settings, beside what it did.

    The smallest P a rank test can return is fixed by its sample: the band's is
    1/(n_splits + 1), the paired histogram's 2/(K + 1). Holm multiplies the smallest
    P in a cell by the number of checks in that cell. When that product is past
    alpha, the adjusted yardstick cannot flag anything — for any candidate, the
    known-bad controls included — and a column of zeros carries no information.
    """
    fam = defaultdict(int)
    for s in R["stats"]:
        fam[(s["stream"], s["cell_id"])] += 1
    m = max(fam.values()) if fam else 0
    n_splits = _med([_f(y["n_splits"]) for y in R["yardsticks"]])
    Ks = [_f(c["K"]) for c in R["cells"] if c["status"] == "ok" and math.isfinite(_f(c["K"]))]
    kc = defaultdict(int)
    for k in Ks:
        kc[int(k)] += 1

    def mn(col):
        v = [_f(s[col]) for s in R["stats"] if math.isfinite(_f(s[col]))]
        return min(v) if v else float("nan")

    def sh(pred):
        v = [pred(s) for s in R["stats"]]
        return sum(v) / len(v) if v else float("nan")
    band_floor = 1.0 / (n_splits + 1) if math.isfinite(n_splits) else float("nan")
    k_max = max(Ks) if Ks else float("nan")
    paired_floor = 2.0 / (k_max + 1) if math.isfinite(k_max) else float("nan")
    return {
        "m": m, "n_splits": n_splits, "K_counts": dict(sorted(kc.items())),
        "band_floor": band_floor, "band_floor_holm": min(1.0, band_floor * m),
        "paired_floor": paired_floor, "paired_floor_holm": min(1.0, paired_floor * m),
        "min_band": mn("band_p"), "min_band_holm": mn("band_p_holm"),
        "min_paired": mn("paired_p"), "min_paired_holm": mn("paired_p_holm"),
        "share_band_q95": sh(lambda s: _b(s["band_flag"])),
        "share_band_raw": sh(lambda s: _f(s["band_p"]) < ALPHA),
        "share_paired_raw": sh(lambda s: _f(s["paired_p"]) < ALPHA),
        "share_holm": sh(lambda s: _f(s["band_p_holm"]) < ALPHA
                         or _f(s["paired_p_holm"]) < ALPHA),
        "splits_needed": math.ceil(m / ALPHA - 1) if m else None,
        "K_needed": math.ceil(2 * m / ALPHA - 1) if m else None,
    }


def reach_block(R: dict) -> str:
    y = yardstick_reach(R)
    if not y["m"]:
        return ""
    kc = ", ".join(f"{n} cells at {k} draws" for k, n in y["K_counts"].items())
    return (
        f'<div class="warn"><p><b>⚠ Neither yardstick, Holm-adjusted, can flag anything at '
        f"these settings — so every Holm column below is zero for every candidate, the "
        f"known-bad controls included, and says nothing about them.</b> Holm is applied per "
        f"grid cell across {y['m']} checks (every statistic in every scope). The band's "
        f"smallest possible <i>P</i> is 1/({num(y['n_splits'], 0)} + 1) = "
        f"{num(y['band_floor'], 4)}, which Holm lifts to {num(y['band_floor_holm'], 2)}; the "
        f"paired histogram's is 2/(<i>K</i> + 1) = {num(y['paired_floor'], 3)} at the "
        f"largest <i>K</i> reached, which Holm lifts to {num(y['paired_floor_holm'], 2)}. "
        f"Observed smallest after Holm: band {num(y['min_band_holm'], 3)}, paired "
        f"{num(y['min_paired_holm'], 3)}. Unadjusted, the yardsticks do discriminate: "
        f"{pct(y['share_band_q95'])} of checks fall outside the band's 95th percentile and "
        f"{pct(y['share_paired_raw'])} have a raw paired <i>P</i> under 0.05 — so the "
        f"tables report those, with the held-out and synthetic negatives beside them for "
        f"what an unadjusted rate costs. <i>K</i> reached per finished cell: {kc}; a cell "
        f"at <i>K</i> = 19 cannot reach a raw paired <i>P</i> under 0.10.</p></div>")


def intractable_reasons(R: dict) -> dict:
    out = defaultdict(int)
    for c in R["cells"]:
        if c["status"] != "intractable":
            continue
        w = c.get("why") or ""
        if w.startswith("dropped before running") or w.startswith("not run"):
            out["not run: projected cost past the Mac run's stop time"] += 1
        elif "resident" in w:
            out["killed at the memory cap"] += 1
        elif w.startswith("killed after"):
            out["killed at the hard time cap"] += 1
        elif "budget" in w:
            out["time budget spent below the minimum K"] += 1
        else:
            out["other"] += 1
    return dict(out)


def group_disagreement(R: dict, stream: str) -> dict:
    """Checks flagged (paired, Holm) in a group but not overall, and the reverse."""
    by = defaultdict(dict)
    for s in R["stats"]:
        if s["stream"] != stream:
            continue
        by[(s["cell_id"], s["stat"])][s["scope"]] = _f(s["paired_p_holm"]) < ALPHA
    groups = sorted({sc for v in by.values() for sc in v if sc != "all"})
    only_group = only_all = 0
    for v in by.values():
        if "all" not in v:
            continue
        g = any(v.get(x) for x in groups)
        only_group += bool(g and not v["all"])
        only_all += bool(v["all"] and not g)
    return {"groups": groups, "only_group": only_group, "only_all": only_all,
            "n": sum("all" in v for v in by.values())}


# ---- formatting -------------------------------------------------------------

def esc(s) -> str:
    return html.escape(str(s), quote=True)


def pct(x) -> str:
    ok = isinstance(x, (int, float)) and not isinstance(x, bool) and math.isfinite(x)
    return f"{100 * x:.0f}%" if ok else "—"


def num(x, nd=2) -> str:
    if not (isinstance(x, (int, float)) and math.isfinite(float(x))):
        return "—"
    s = f"{x:.{nd}f}"
    return s[1:] if s.startswith("-") and float(s) == 0 else s    # no "-0.00"


def rng_txt(s, nd=2) -> str:
    if not s:
        return "—"
    if s["n"] == 1:
        return num(s["med"], nd)
    return f"{num(s['med'], nd)} <span class=dim>({num(s['min'], nd)}–{num(s['max'], nd)})</span>"


def table(head: list[str], rows: list[list[str]], label: str, cls: str = "") -> str:
    th = "".join(f"<th>{h}</th>" for h in head)
    tr = "".join("<tr>" + "".join(f"<td>{c}</td>" for c in r) + "</tr>" for r in rows)
    return (f'<div class="wide" role="region" aria-label="{esc(label)}" tabindex="0">'
            f'<table class="{cls}"><thead><tr>{th}</tr></thead><tbody>{tr}</tbody>'
            f"</table></div>")


# ---- SVG kit ----------------------------------------------------------------

FONT = 13


class Svg:
    def __init__(self, w: int, h: int, label: str):
        self.w, self.h, self.label, self.parts = w, h, label, []

    def add(self, s: str) -> None:
        self.parts.append(s)

    def text(self, x, y, s, size=FONT, anchor="start", weight="normal", fill="#111"):
        self.add(f'<text x="{x:.1f}" y="{y:.1f}" font-size="{size}" '
                 f'text-anchor="{anchor}" font-weight="{weight}" fill="{fill}">'
                 f"{esc(s)}</text>")

    def line(self, x1, y1, x2, y2, stroke="#111", w=1.0, dash=None):
        d = f' stroke-dasharray="{dash}"' if dash else ""
        self.add(f'<line x1="{x1:.1f}" y1="{y1:.1f}" x2="{x2:.1f}" y2="{y2:.1f}" '
                 f'stroke="{stroke}" stroke-width="{w}"{d}/>')

    def rect(self, x, y, w, h, fill="none", stroke="none", sw=1.0):
        self.add(f'<rect x="{x:.1f}" y="{y:.1f}" width="{max(w, 0):.1f}" '
                 f'height="{max(h, 0):.1f}" fill="{fill}" stroke="{stroke}" '
                 f'stroke-width="{sw}"/>')

    def circle(self, x, y, r, fill="#111", stroke="none"):
        self.add(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="{r}" fill="{fill}" '
                 f'stroke="{stroke}" stroke-width="1.2"/>')

    def time_axis(self, x0, x1, y, t0, t1):
        """The viewer's axis: 60-base ticks, labels such as 45s, 2m, 2m30s."""
        self.line(x0, y, x1, y)
        for t in time_axis.ticks(t0, t1):
            x = x0 + (t - t0) / (t1 - t0) * (x1 - x0)
            self.line(x, y, x, y + 4)
            self.text(x, y + 18, time_axis.label(t), anchor="middle")

    def render(self) -> str:
        return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {self.w} {self.h}" '
                f'width="{self.w}" height="{self.h}" role="img" '
                f'aria-label="{esc(self.label)}" font-family="system-ui, sans-serif">'
                + "".join(self.parts) + "</svg>")


def figure(n: int, title: str, svg: Svg, caption: str) -> str:
    return (f'<figure id="fig{n}"><div class="wide" role="region" '
            f'aria-label="Figure {n}, scrollable" tabindex="0">{svg.render()}</div>'
            f"<figcaption><b>Figure {n}. {esc(title)}.</b> {caption}</figcaption></figure>")


# ---- synthetic material for the first three figures -------------------------

DT = 0.1                      # the steps_excluded fast stream's frame interval
FLOOR = 4                     # its observed floor, 0.40 s, in frames
J_DEMO = 16                   # 1.6 s, the earlier review's J


def _synthetic_trains(n_roi=14, duration=600.0, seed=20260911):
    from bugarach.simulate import simulate_coordination
    rs = np.random.RandomState(seed)
    s, _ = simulate_coordination(
        duration_sec=duration, n_roi=n_roi, bg_floor_sec=FLOOR * DT,
        bg_roi_counts=rs.poisson(40, size=n_roi), participation=(0.5,),
        n_per_level=(0,), jitter_sec=DT, grid_sec=DT, seed=seed)
    n = int(round(duration / DT))
    tr = []
    for v in s.streams["events"].locs:
        f = np.unique(np.round(np.asarray(v, float) / DT).astype(np.int64))
        tr.append(f[(f >= 0) & (f < n)])
    return tr, n


def _params(name: str) -> dict:
    J, f = float(J_DEMO), FLOOR
    if name in ("circular_shift", "do_nothing", "interval_shuffle", "homogeneous_resample"):
        return {}
    if name in ("uniform_dither", "shipped_dither", "rigid_shift", "interval_jitter",
                "window_shuffle"):
        return {"J": J}
    if name in ("dead_time_dither", "trial_shift", "pattern_jitter"):
        return {"J": J, "f": f}
    if name in ("joint_isi", "isi_dither"):
        return {"J": J, "f": f, "sigma": J / 2, "use_sqrt": False}
    if name == "operational_time":
        return {"J": J, "bandwidth": float(round(5 * 60 / DT))}
    raise KeyError(name)


def fig_leak() -> Svg:
    """A real-like raster, its uniform dither, the leak lane, one interval histogram."""
    from bugarach import surrogates
    tr, n = _synthetic_trains()
    res = surrogates.generate("uniform_dither", tr, (0, n), ("fig1", "demo", "UD", 0),
                              J=float(J_DEMO))
    sur = [np.sort(np.asarray(v, np.int64)) for v in res.trains]
    t0, t1 = 0.0, 120.0
    svg = Svg(900, 430, "Figure 1: a synthetic raster before and after uniform dither, "
                        "with the sub-floor intervals it creates marked above, and "
                        "the interval histogram beside it")
    x0, x1 = 150, 560

    def X(fr):
        return x0 + (fr * DT - t0) / (t1 - t0) * (x1 - x0)

    def raster(trains, top, label, lane):
        svg.text(x0 - 10, top - 22 if lane else top - 6, label, anchor="end", weight="bold")
        if lane:
            svg.text(x0 - 10, top - 6, "sub-floor", anchor="end", size=12, fill="#444")
            svg.line(x0, top - 10, x1, top - 10, stroke="#bbb")
        for r, v in enumerate(trains):
            y = top + r * 9
            for fr in v[(v * DT >= t0) & (v * DT <= t1)]:
                svg.line(X(fr), y, X(fr), y + 7, w=1.3)
            if lane:
                iv = np.diff(v)
                for i in np.nonzero(iv < FLOOR)[0]:
                    a = v[i + 1]
                    if t0 <= a * DT <= t1:
                        xm = X(a)
                        svg.add(f'<path d="M{xm - 4:.1f} {top - 18:.1f} L{xm + 4:.1f} '
                                f'{top - 18:.1f} L{xm:.1f} {top - 11:.1f} Z" fill="#111"/>')
    raster(tr, 40, "real", False)
    raster(sur, 225, "UD, J = 1.6 s", True)
    svg.time_axis(x0, x1, 360, t0, t1)
    svg.text((x0 + x1) / 2, 398, "time (synthetic recording)", anchor="middle", fill="#444")
    # interval histogram, all ROIs pooled, one bin per frame
    hx0, hx1, hy0, hy1 = 630, 870, 60, 330
    real_iv = np.concatenate([np.diff(v) for v in tr if len(v) > 1])
    sur_iv = np.concatenate([np.diff(v) for v in sur if len(v) > 1])
    bins = np.arange(0, 31)
    hr = np.histogram(real_iv, bins)[0] / max(1, real_iv.size)
    hs = np.histogram(sur_iv, bins)[0] / max(1, sur_iv.size)
    top = max(hr.max(), hs.max()) * 1.1 or 1.0
    bw = (hx1 - hx0) / (len(bins) - 1)
    for i in range(len(bins) - 1):
        xl = hx0 + i * bw
        svg.rect(xl + 1, hy1 - hr[i] / top * (hy1 - hy0), bw - 2,
                 hr[i] / top * (hy1 - hy0), fill="#bbb")
        y = hy1 - hs[i] / top * (hy1 - hy0)
        svg.line(xl + 1, y, xl + bw - 1, y, w=2.2)
    xf = hx0 + FLOOR * bw
    svg.line(xf, hy0 - 6, xf, hy1, dash="4 3")
    svg.text(xf + 4, hy0 + 6, "floor f", size=12)
    svg.line(hx0, hy1, hx1, hy1)
    for k in (0, 10, 20, 30):
        xk = hx0 + k * bw
        svg.line(xk, hy1, xk, hy1 + 4)
        svg.text(xk, hy1 + 18, f"{k * DT:g}s", anchor="middle")
    svg.text((hx0 + hx1) / 2, 380, "interval between onsets of one ROI", anchor="middle",
             fill="#444")
    svg.rect(hx0, 20, 12, 10, fill="#bbb")
    svg.text(hx0 + 18, 29, "real", size=12)
    svg.line(hx0 + 70, 25, hx0 + 84, 25, w=2.2)
    svg.text(hx0 + 90, 29, "after UD", size=12)
    return svg


def fig_candidates() -> Svg:
    """One ROI, and what each of the twelve candidates does to it."""
    from bugarach import surrogates
    tr, n = _synthetic_trains(n_roi=6, seed=7)
    roi = [max(tr, key=len)]
    rows = [("real", roi[0])]
    notes = {}
    for name, label in CANDIDATES:
        try:
            r = surrogates.generate(name, roi, (0, n), ("fig2", "demo", name, 0),
                                    **_params(name))
            rows.append((label, np.sort(np.asarray(r.trains[0], np.int64))))
        except Exception as e:                                  # noqa: BLE001
            rows.append((label, None))
            notes[label] = f"{type(e).__name__}"
    t0, t1 = 0.0, 180.0
    h = 40 + 26 * len(rows) + 50
    svg = Svg(900, h, "Figure 2: one synthetic ROI's onsets, and the same ROI after "
                      "each of the twelve candidates at J = 1.6 s")
    x0, x1 = 250, 880

    def X(fr):
        return x0 + (fr * DT - t0) / (t1 - t0) * (x1 - x0)
    for i, (label, v) in enumerate(rows):
        y = 30 + i * 26
        svg.text(x0 - 12, y + 13, label, anchor="end",
                 weight="bold" if i == 0 else "normal")
        svg.line(x0, y + 18, x1, y + 18, stroke="#ddd")
        if v is None:
            svg.text(x0 + 4, y + 13, f"not drawn ({notes.get(label, 'error')})", size=12,
                     fill="#444")
            continue
        for fr in v[(v * DT >= t0) & (v * DT <= t1)]:
            svg.line(X(fr), y + 2, X(fr), y + 18, w=1.4)
    svg.time_axis(x0, x1, 30 + 26 * len(rows) + 4, t0, t1)
    return svg


def fig_windows() -> Svg:
    """The generation window, its 60-second analysis windows and the 5-second edge bands."""
    from bugarach import surrogate_stats as sst
    T, aw, eb = 300.0, sst.ANALYSIS_WINDOW_SEC, sst.EDGE_BAND_SEC
    svg = Svg(900, 250, "Figure 3: a 5-minute generation window cut into 60-second "
                        "analysis windows, with the 5-second edge bands of each")
    x0, x1 = 190, 880

    def X(t):
        return x0 + t / T * (x1 - x0)
    svg.text(x0 - 12, 52, "generation window", anchor="end")
    svg.rect(X(0), 36, X(T) - X(0), 22, fill="#fff", stroke="#111")
    svg.rect(X(0), 36, X(eb) - X(0), 22, fill="#999")
    svg.rect(X(T - eb), 36, X(T) - X(T - eb), 22, fill="#999")
    svg.text(x0 - 12, 104, "analysis windows", anchor="end")
    k = 0
    while (k + 1) * aw <= T + 1e-9:
        a, b = k * aw, (k + 1) * aw
        svg.rect(X(a) + 1, 88, X(b) - X(a) - 2, 22, fill="#fff", stroke="#111")
        svg.rect(X(a) + 1, 88, X(a + eb) - X(a) - 1, 22, fill="#ccc")
        svg.rect(X(b - eb), 88, X(b) - X(b - eb) - 1, 22, fill="#ccc")
        k += 1
    tr, n = _synthetic_trains(n_roi=4, duration=T, seed=11)
    v = max(tr, key=len)
    svg.text(x0 - 12, 152, "one ROI's onsets", anchor="end")
    for fr in v:
        svg.line(X(fr * DT), 138, X(fr * DT), 158, w=1.3)
    svg.time_axis(x0, x1, 190, 0.0, T)
    svg.rect(x0, 222, 14, 10, fill="#999")
    svg.text(x0 + 20, 231, "edge band, generation window", size=12)
    svg.rect(x0 + 260, 222, 14, 10, fill="#ccc")
    svg.text(x0 + 280, 231, "edge band, analysis window", size=12)
    return svg


# ---- data figures (aggregates only) -----------------------------------------

def fig_flags(rows_by_stream: dict, role: str) -> Svg:
    """Share of checks flagged, per candidate, under the band and the paired yardstick."""
    streams = list(rows_by_stream)
    names = [lab for _, lab in CANDIDATES + CONTROLS]
    h = 60 + 24 * len(names) + 50
    colw = 260
    w = max(250 + colw * len(streams) + 20, 660)   # the legend needs 660 even for one stream
    svg = Svg(w, h, f"Figure 4 ({role}): share of checks flagged per candidate under "
                    "the mouse-split band and the paired surrogate histogram, unadjusted")
    for j, st in enumerate(streams):
        cx0 = 250 + j * colw
        cx1 = cx0 + colw - 40
        svg.text((cx0 + cx1) / 2, 24, f"{st} stream", anchor="middle", weight="bold")
        for q in (0, 0.5, 1.0):
            xq = cx0 + q * (cx1 - cx0)
            svg.line(xq, 36, xq, 40 + 24 * len(names), stroke="#ddd")
            svg.text(xq, 58 + 24 * len(names), pct(q), anchor="middle", size=12)
        by = {r["label"]: r for r in rows_by_stream[st]}
        for i, lab in enumerate(names):
            y = 48 + i * 24
            if j == 0:
                svg.text(240, y + 4, lab, anchor="end", size=12)
            r = by.get(lab)
            if not r or not math.isfinite(r["paired_raw"]):
                svg.text(cx0, y + 4, "no scored cell", size=12, fill="#444")
                continue
            xb = cx0 + r["band_q95"] * (cx1 - cx0)
            xp = cx0 + r["paired_raw"] * (cx1 - cx0)
            svg.line(min(xb, xp), y, max(xb, xp), y, stroke="#888")
            svg.circle(xb, y, 5, fill="#fff", stroke="#111")
            svg.circle(xp, y, 4.5)
    yl = h - 18
    svg.circle(260, yl - 4, 5, fill="#fff", stroke="#111")
    svg.text(270, yl, "mouse-split band", size=12)
    svg.circle(420, yl - 4, 4.5)
    svg.text(430, yl, "paired surrogate histogram", size=12)
    return svg


def fig_destruction(rows_by_stream: dict, role: str) -> Svg:
    streams = list(rows_by_stream)
    names = [lab for _, lab in CANDIDATES + CONTROLS]
    h = 60 + 24 * len(names) + 50
    colw = 260
    w = max(250 + colw * len(streams) + 20, 660)   # the legend needs 660 even for one stream
    svg = Svg(w, h, f"Figure 5 ({role}): share of planted coordination retained after "
                    "each candidate, median across its cells, at 20% and 50% participation")
    for j, st in enumerate(streams):
        cx0 = 250 + j * colw
        cx1 = cx0 + colw - 40

        def X(v):
            return cx0 + max(-0.2, min(1.2, v)) / 1.4 * (cx1 - cx0) + 0.2 / 1.4 * (cx1 - cx0)
        svg.text((cx0 + cx1) / 2, 24, f"{st} stream", anchor="middle", weight="bold")
        for q in (0.0, 0.5, 1.0):
            svg.line(X(q), 36, X(q), 40 + 24 * len(names), stroke="#ddd")
            svg.text(X(q), 58 + 24 * len(names), f"{q:g}", anchor="middle", size=12)
        by = {r["label"]: r for r in rows_by_stream[st]}
        for i, lab in enumerate(names):
            y = 48 + i * 24
            if j == 0:
                svg.text(240, y + 4, lab, anchor="end", size=12)
            r = by.get(lab)
            got = False
            for p, mark in (("0.2", "open"), ("0.5", "fill")):
                s = (r or {}).get("retained", {}).get(p)
                if not s:
                    continue
                got = True
                if mark == "open":
                    svg.circle(X(s["med"]), y, 5, fill="#fff", stroke="#111")
                else:
                    svg.circle(X(s["med"]), y, 4.5)
            if not got:
                svg.text(cx0, y + 4, "not measured", size=12, fill="#444")
    yl = h - 18
    svg.circle(260, yl - 4, 5, fill="#fff", stroke="#111")
    svg.text(270, yl, "20% participation", size=12)
    svg.circle(420, yl - 4, 4.5)
    svg.text(430, yl, "50% participation", size=12)
    return svg


# ---- page assembly ----------------------------------------------------------

CSS = """
:root{color-scheme:light}
body{margin:0;background:#fff;color:#111;font:16px/1.55 system-ui,sans-serif}
main{max-width:980px;margin:0 auto;padding:24px 16px 64px}
h1{font-size:26px;line-height:1.25;margin:8px 0 4px}
h2{font-size:20px;margin:36px 0 8px;border-bottom:1px solid #ccc;padding-bottom:4px}
h3{font-size:17px;margin:22px 0 6px}
.dim{color:#444}
.lede{font-size:17px}
.wide{overflow-x:auto;max-width:100%}
.wide:focus{outline:2px solid #06c}
table{border-collapse:collapse;font-size:14px;margin:8px 0 14px}
th,td{border-bottom:1px solid #ddd;padding:4px 8px;text-align:left;vertical-align:top}
th{background:#f2f2f2;font-weight:600}
figure{margin:18px 0 26px}
figure svg{display:block;max-width:none;height:auto}
figcaption{font-size:15px;color:#222;margin-top:6px}
.warn{border-left:4px solid #b36b00;padding:6px 12px;background:#fff6e8}
code{font-size:14px}
"""


def page(title: str, body: str) -> str:
    # The title rides on the charset line: a literal opening with <title> is what
    # sapper SAP005 refuses, since that is how a page loses its charset.
    return (f'<!doctype html><meta charset="utf-8"><title>{esc(title)}</title>\n'
            '<meta name="viewport" content="width=device-width, initial-scale=1">\n'
            f"<style>{CSS}</style>\n"
            f"<main>\n{body}\n</main>\n")


TERMS = """
<h2 id="terms">Terms, before any figure</h2>
<table><tbody>
<tr><td>ROI, onset</td><td>region of interest, one imaged cell's trace; an onset is the time one
of its events begins.</td></tr>
<tr><td>surrogate</td><td>a resampled copy of a recording that keeps each ROI's own timing and
destroys the timing between ROIs.</td></tr>
<tr><td>leak</td><td>a real-versus-surrogate difference visible without any cross-ROI
information — one ROI at a time.</td></tr>
<tr><td><i>J</i></td><td>jitter radius: how far a dither may move one onset, ± seconds (or
frames); other candidates are matched to it by root-mean-square displacement.</td></tr>
<tr><td>τ</td><td>dead time: the shortest interval between two onsets of one ROI the producer's
extractor can emit. Not known yet — it is the producer's number.</td></tr>
<tr><td><i>f</i></td><td>the provisional dead time the candidates use in its place, swept at
0.5, 0.75 and 1 × the observed floor (the shortest within-ROI interval in the folder's
baselines), in whole frames.</td></tr>
<tr><td>frame</td><td>one imaging frame; every generator and statistic works on frame indices,
the nearest whole number to <i>t</i>/d<i>t</i>.</td></tr>
<tr><td>generation / analysis window</td><td>the span a surrogate is generated over (the
baseline, or the whole recording where no regions are declared), and the 60-second cuts of it
that are scored (Figure 3).</td></tr>
<tr><td><i>K</i></td><td>surrogate draws per grid cell (never below 19). In the destruction
tables, <i>K</i> is instead the assessor's scan over the minimum number of ROIs active
together.</td></tr>
<tr><td>the three yardsticks</td><td><b>mouse-split band</b>: real against real across 100
mouse-grouped half splits — the scale of between-mouse variation. <b>Paired surrogate
histogram</b>: the statistic on the real recordings ranked among <i>K</i> draws of the same
recordings (two-sided <i>P</i>). <b>Exchangeable negative</b>: a real held-out half, and a
fresh synthetic draw, scored as if each were a candidate — how often a yardstick flags what
should pass.</td></tr>
<tr><td>Holm</td><td>the Holm–Bonferroni step-down adjustment, applied per grid cell across every
statistic in every scope, separately for each yardstick.</td></tr>
<tr><td>destruction, retained</td><td>whether a surrogate removes coordination planted in a
synthetic twin; <b>retained</b> is the planted twin's coactivity excess over the unplanted
twin's after the surrogate, as a share of the same before it: 1 keeps it all, 0 removes it.</td></tr>
<tr><td>KS</td><td>Kolmogorov–Smirnov distance between two interval distributions.</td></tr>
<tr><td>UD, UDD, JISI-D, ISI-D, WIN-SHUFF, TR-SHIFT</td><td>Stella et al. 2022's names:
uniform dithering, uniform dithering with dead time, joint-ISI dithering, ISI dithering
(ISI: inter-onset interval), window shuffling, trial shifting.</td></tr>
</tbody></table>
"""


def synthetic_figures() -> str:
    return (
        "<h2 id=\"figures\">Three synthetic figures</h2>"
        "<p>None of these three is a real recording. They show what the measurements "
        "below are measuring, on synthetic trains with a hard 0.40-second floor — the "
        "fast stream's observed floor.</p>"
        + figure(1, "A surrogate and its leak", fig_leak(),
                 "Top: fourteen synthetic ROIs, one row each, over two minutes. Bottom: the "
                 "same ROIs after uniform dither (UD) at <i>J</i> = 1.6 s; each triangle in "
                 "the lane above marks an interval shorter than the floor <i>f</i> — an "
                 "interval no real ROI has, so the surrogate can be told from the real "
                 "recording one ROI at a time. Right: the interval histogram of all ROIs "
                 "pooled, real (grey bars) against UD (black steps); the dashed line is the "
                 "floor, and UD's mass left of it is the leak.")
        + figure(2, "What each candidate does to one ROI", fig_candidates(),
                 "One synthetic ROI (top row), then the same ROI after each of the twelve "
                 "candidates at <i>J</i> = 1.6 s, with <i>f</i> = 4 frames where the "
                 "candidate takes one and a 5-minute kernel for operational-time dither. "
                 "Joint-ISI and ISI dither use Stella's setting, without Gerstein's "
                 "square root.")
        + figure(3, "The window anatomy", fig_windows(),
                 "A surrogate is generated over the whole generation window, then cut into "
                 "60-second analysis windows for scoring. The edge-band statistics count "
                 "onsets in the 5-second bands at each end: dark at the generation window's "
                 "edges, light at each analysis window's. ⚠ The 60-second analysis window is "
                 "inherited from the earlier review, not justified.")
    )


def _role_intro(R: dict) -> str:
    m, mac = R["meta"], R["meta_mac"] or {}
    role = R["role"]
    cite = ""
    if role == "cossart":
        cite = ("<p>Data: the Cossart lab's in vivo two-photon recordings of hippocampal CA1 in "
                "mouse pups, dataset <b>DANDI:000219</b> (Dard, Picardo &amp; Cossart), "
                "analysed in Dard et al. 2022, <i>eLife</i> 11:e78116. One stream; no groups; "
                "each whole recording is a generation window, an assumption, since the "
                "folder declares no regions.</p>")
    elif role == "steps_excluded":
        cite = ("<p>Data: the producer's <code>steps_excluded</code> export folder, baselines "
                "only. Two streams, fast and slow; four groups — ORX and OVX, gonadectomized "
                "males and females; DI, intact females in diestrus; MALE, intact males. "
                "FOUNDATIONS §9 admits no pooled number without the per-group numbers "
                "beside it, which is why every table carries its scope.</p>")
    runs = []
    if mac.get("started"):
        runs.append(f"started on the Mac {esc(mac.get('started'))} with {mac.get('jobs')} "
                    f"jobs")
    if m.get("started"):
        runs.append(f"resumed on the Windows workstation {esc(m.get('started'))} with "
                    f"{m.get('jobs')} jobs")
    y = yardstick_reach(R)
    kc = ", ".join(f"{n} cells at {k} draws" for k, n in y["K_counts"].items()) or "—"
    return (cite + f"<p class=dim>{m.get('n_recordings_loaded', '—')} recordings. "
            f"<i>K</i> reached: {kc} (never below "
            f"{m.get('settings', {}).get('min_K', '—')}; the <i>K</i> asked for changed "
            f"between invocations, so the one <code>meta.json</code> records is only the "
            f"last). A cell's budget "
            f"{m.get('settings', {}).get('cell_seconds', '—')} s, its hard stop "
            f"{m.get('cell_hard_seconds', '—')} s, its memory cap "
            f"{m.get('cell_mem_gb', '—')} GB. The run {'; '.join(runs) or '—'}.</p>")


def exec_summary(R: dict, by_stream: dict) -> str:
    role = R["role"]
    parts = [f"<h2 id=\"summary\">Executive summary</h2>"]
    reasons = intractable_reasons(R)
    n_cells = len(R["cells"])
    n_ok = sum(c["status"] == "ok" for c in R["cells"])
    parts.append(
        f"<p class=lede>Every candidate was measured; <b>none is shortlisted</b>, by design. "
        f"{n_ok} of {n_cells} grid cells finished; the rest are intractable — "
        + ", ".join(f"{v} {esc(k)}" for k, v in sorted(reasons.items(), key=lambda x: -x[1]))
        + ".</p>" + reach_block(R) + "<p>What each candidate keeps and destroys, per "
          "stream:</p>")
    for st, rows in by_stream.items():
        body = []
        for r in rows:
            if r["kind"] != "candidate":
                continue
            J = (f"{min(r['J']):g}–{max(r['J']):g} {'s' if r['J_unit'] == 'sec' else 'frames'}"
                 if r["J"] else "none")
            body.append([
                f"<b>{esc(r['label'])}</b>", f"{r['n_ok']} of {r['n_cells']} cells", J,
                num(r["rms_disp"], 1),
                f"{pct(r['band_q95'])} / "
                + (pct(r["paired_raw"]) if r["paired_reachable"] or not r["n_ok"]
                   else "<i>unreachable</i> <span class=dim>(<i>K</i> ≤ 39)</span>"),
                esc(", ".join(stat_label(s) for s in r["flagged"][:4])
                    + (" …" if len(r["flagged"]) > 4 else "")) or "none",
                rng_txt(r["retained"].get("0.5")),
                (f"{rng_txt(r['disc_acc'])}" + (f" <span class=dim>void {pct(r['disc_void'])}"
                                                "</span>" if r["disc_void"] and math.isfinite(
                                                    r["disc_void"]) else "")),
                num(r["cost"] * 1e3, 2) if math.isfinite(r["cost"]) else "—"])
        parts.append(f"<h3>{esc(st)} stream</h3>")
        parts.append(table(
            ["candidate", "cells run", "<i>J</i>", "RMS move (frames)",
             "checks flagged, unadjusted: band / paired", "what gives it away",
             "coordination retained at 50%", "discriminator accuracy", "ms per ROI per draw"],
            body, f"{role} {st}: per-candidate summary"))
    parts.append(
        "<p class=dim>Checks flagged, unadjusted: the share of (statistic, cell) checks "
        "over all recordings where the candidate's surrogate differs from the real "
        "recordings — outside the mouse-split band's 95th percentile, and a paired "
        "surrogate histogram <i>P</i> under α = 0.05. Not Holm-adjusted, because the "
        "adjusted rate is zero by construction (the box above). 'What gives it away' "
        "lists statistics with a raw paired <i>P</i> under 0.05 in at least half of the "
        "candidate's cells. "
        "Coordination retained: median across cells, range in brackets. Discriminator: the "
        "per-ROI-only classifier's forced-choice accuracy, where 0.5 is chance.</p>")
    return "".join(parts)


def choices(R: dict, by_stream: dict) -> str:
    """The decisions the verdict rule faces, each beside what bears on it."""
    items = []
    for st, rows in by_stream.items():
        yr = yard_rows(R, st)
        pw = power_rows(R, st)
        med = {k: _med([y[k] for y in yr]) for k in ("hb", "hp", "sb", "sp")}
        moved_b = sum(p["band"] for p in pw)
        moved_p = sum(p["paired"] for p in pw)
        dead = sorted({p["stat"] for p in pw} - {p["stat"] for p in pw
                                                  if p["band"] or p["paired"]})
        ret = [r["retained"].get("0.5") for r in rows if r["kind"] == "candidate"
               and r["retained"].get("0.5")]
        void = [r["disc_void"] for r in rows if math.isfinite(r["disc_void"])]
        gd = group_disagreement(R, st)
        items.append(f"<h3>{esc(st)} stream</h3><ol>"
                     f"<li><b>Which yardstick decides.</b> Flag rate on things that should "
                     f"pass, median over statistics: held-out real half — band "
                     f"{pct(med['hb'])}, paired {pct(med['hp'])}; fresh synthetic draw — band "
                     f"{pct(med['sb'])}, paired {pct(med['sp'])}. Of {len(pw)} "
                     f"control-and-statistic checks, the band moved {moved_b} and the paired "
                     f"histogram {moved_p}.</li>"
                     f"<li><b>What a statistic no control could move counts for.</b> "
                     f"Unmoved under both yardsticks: "
                     f"{esc(', '.join(stat_label(s) for s in dead)) or 'none'}.</li>"
                     f"<li><b>How much destruction is enough.</b> Median coordination "
                     f"retained at 50% participation, across candidates: "
                     f"{num(_med([x['med'] for x in ret]))} (lowest "
                     f"{num(min((x['min'] for x in ret), default=float('nan')))}, highest "
                     f"{num(max((x['max'] for x in ret), default=float('nan')))}).</li>"
                     f"<li><b>What an intractable cell counts as.</b> See the coverage "
                     f"section: most were never run, by projected cost.</li>"
                     f"<li><b>Whether a void discriminator result counts.</b> Void share, "
                     f"median across candidates: {pct(_med(void))}.</li>"
                     f"<li><b>Pooled or per group</b> (FOUNDATIONS §9). Of {gd['n']} checks, "
                     f"{gd['only_group']} flag in a group and not overall; {gd['only_all']} "
                     f"the reverse.</li>"
                     f"<li><b>Which <i>J</i> and which <i>f</i>.</b> Every cell is in "
                     f"<code>stats.csv</code>; the per-candidate range is in the summary "
                     f"table.</li></ol>")
    return ("<h2 id=\"choices\">The choices the verdict rule faces</h2>"
            "<p>Each is a decision for the design session, not made here. Beside each is the "
            "measurement that bears on it.</p>" + _reach_choice(R) + "".join(items))


def _reach_choice(R: dict) -> str:
    y = yardstick_reach(R)
    if not y["m"]:
        return ""
    return ("<p><b>Before any of these: whether a corrected test is possible at all.</b> "
            f"At {y['m']} checks per cell, a Holm-adjusted flag at α = 0.05 needs a band of "
            f"at least {y['splits_needed']} mouse splits (there are "
            f"{num(y['n_splits'], 0)}) and a paired histogram of at least {y['K_needed']} "
            f"draws (the most any cell reached is {max(y['K_counts'] or [0])}). The other "
            "levers are a smaller correction family — per statistic, or per scope — or no "
            "correction with the negatives' flag rates as its price. Which one is the "
            "design session's first decision; every rate below is unadjusted.</p>")


def detail_sections(R: dict, by_stream: dict) -> str:
    role = R["role"]
    out = ["<h2 id=\"power\">Where each statistic had power</h2>"
           "<p>Each known-bad control is built to move one statistic. Where it does not, "
           "that statistic cannot see the defect it was meant to catch — a measurement of "
           "its power, not a failure of the run.</p>"]
    for st in by_stream:
        rows = [[esc(NAME.get(p["control"], p["control"])), esc(stat_label(p["stat"])),
                 "yes" if p["band"] else "no", "yes" if p["paired"] else "no",
                 num(p["p"], 3)] for p in power_rows(R, st)]
        out.append(f"<h3>{esc(st)} stream</h3>")
        out.append(table(["control", "statistic it must move", "band moved", "paired moved",
                          "paired <i>P</i> (raw)"], rows, f"{role} {st}: control power"))
    out.append("<h2 id=\"yardsticks\">The three yardsticks, side by side</h2>"
               "<p>How often each yardstick flags something that should pass. A yardstick "
               "that flags a real held-out half often is too strict to rank candidates "
               "with; one that never flags a known-bad control is too blind.</p>")
    for st in by_stream:
        rows = [[esc(stat_label(y["stat"])), pct(y["hb"]), pct(y["hp"]), pct(y["sb"]),
                 pct(y["sp"])] for y in yard_rows(R, st)]
        out.append(f"<h3>{esc(st)} stream</h3>")
        out.append(table(["statistic", "held-out: band", "held-out: paired",
                          "synthetic: band", "synthetic: paired"], rows,
                         f"{role} {st}: exchangeable-negative flag rates"))
    out.append(figure(4, "Checks flagged per candidate, two yardsticks", fig_flags(
        by_stream, role), "For each candidate and control, the share of its "
        "(statistic, cell) checks over all recordings flagged without adjustment: outside "
        "the mouse-split band's 95th percentile (open), and a paired surrogate histogram "
        "<i>P</i> under 0.05 (filled). The do-nothing control must read zero under both. "
        "Holm-adjusted, every point would sit at zero by construction — see the box in "
        "the executive summary."))
    out.append("<h2 id=\"destruction\">Destruction</h2>")
    out.append(figure(5, "Planted coordination retained", fig_destruction(by_stream, role),
                      "Median across each candidate's cells of the share of planted "
                      "coordination still visible after the surrogate, at 20% (open) and 50% "
                      "(filled) participation. Do-nothing must keep it (1); the whole-window "
                      "circular shift must remove it (0)."))
    out.append("<h2 id=\"discriminator\">The per-ROI-only discriminator</h2>"
               "<p>A logistic model on per-ROI features pooled by symmetric statistics — no "
               "operation touches a second ROI until each has been reduced over time — "
               "scored as a forced choice between each real window and its own surrogate, "
               "folds grouped by mouse. Uniform dither is its positive control and real "
               "against real its negative; if either fails, the results are marked void.</p>")
    rows = []
    for r in R["disc"]:
        if r["status"] != "ok":
            continue
        rows.append([esc(r["stream"]), esc(r["cell_id"]), num(_f(r["accuracy"]), 3),
                     num(_f(r["p_value"]), 3), "yes" if _b(r["void"]) else "no",
                     esc(r.get("void_reason") or "")])
    out.append(table(["stream", "cell", "accuracy", "<i>P</i>", "void", "why void"],
                     rows[:60], f"{role}: discriminator"))
    if len(rows) > 60:
        out.append(f"<p class=dim>First 60 of {len(rows)} rows; all are in "
                   f"<code>discriminator/{esc(role)}/discriminator.csv</code>.</p>")
    out.append("<h2 id=\"coverage\">Coverage and cost</h2>")
    rows = [[esc(k), str(v)] for k, v in sorted(intractable_reasons(R).items(),
                                               key=lambda x: -x[1])]
    out.append(table(["why a cell is intractable", "cells"], rows,
                     f"{role}: intractable reasons"))
    out.append("<p>Most intractable cells were never run: on the Mac, joint-ISI and ISI "
               "dither's projected cost ran past the run's stop time, and those cells were "
               "recorded with that projection rather than run. They are a statement about "
               "that machine and that deadline, not about the candidates; a rerun with more "
               "compute is a choice, not a repair.</p>")
    return "".join(out)


def reproduction_section(run: Path) -> str:
    lt = _rows(run / "reproduction" / "leak_table.csv")
    sat = _rows(run / "reproduction" / "saturation_table.csv")
    if not lt:
        return ""
    rows = [[esc(r["stream"]), esc(r["J"]), esc(r["policy"]), esc(r["time_base"]),
             esc(r["n_windows"]), pct(_f(r["real_share"])),
             f"{pct(_f(r['dithered_share_mean']))} ± {pct(_f(r['dithered_share_sd']))}",
             num(_f(r["auc_mean"]), 3)] for r in lt]
    rows2 = [[esc(r["stream"]), esc(r["J"]), esc(r["policy"]), esc(r["time_base"]),
              pct(_f(r["real"])), pct(_f(r["one_dither"])), pct(_f(r["two_dithers"]))]
             for r in sat]
    return ("<h2 id=\"reproduction\">The reproduction</h2>"
            "<p>The earlier review's leak table, rebuilt on the senktide subset's baselines "
            "— 60-second windows — under all three edge policies. The real sub-floor rate is "
            "0% by construction: the floor is the minimum of those same windows.</p>"
            + table(["stream", "<i>J</i> (s)", "edge policy", "time base", "windows",
                     "real sub-floor", "after UD", "AUC"], rows, "reproduction: leak table")
            + "<p>The saturation table, remeasured under the leak table's conditions (its "
              "original conditions were never recorded): once-dithered against "
              "twice-dithered, which both leak, so the comparison reads flat.</p>"
            + table(["stream", "<i>J</i> (s)", "edge policy", "time base", "real",
                     "one dither", "two dithers"], rows2, "reproduction: saturation table"))


def provenance(run: Path, extra: str = "") -> str:
    sha = "unknown"
    try:
        sha = subprocess.run(["git", "rev-parse", "--short", "HEAD"], capture_output=True,
                             text=True, encoding="utf-8", timeout=10,
                             cwd=Path(__file__).resolve().parent).stdout.strip() or sha
    except Exception:                                           # noqa: BLE001
        pass
    return (f"<h2 id=\"provenance\">Provenance</h2><p class=dim>Built "
            f"{time.strftime('%Y-%m-%d %H:%M %z')} by <code>tools/build_surrogate_report.py"
            f"</code> at commit <code>{esc(sha)}</code>, from the run folder "
            f"<code>&lt;darkroom&gt;/bugarach/{esc(run.name)}/</code>. The plan: "
            f"<code>docs/proposals/2026-09-10-surrogate-evaluation-overnight.md</code>. "
            f"{extra}</p>")


def role_page(run: Path, R: dict) -> str:
    by_stream = {st: candidate_rows(R, st) for st in streams_of(R)}
    title = {"steps_excluded": "The surrogate screen — steps_excluded",
             "cossart": "The surrogate screen — the Cossart folder"}.get(
        R["role"], f"The surrogate screen — {R['role']}")
    body = (f"<h1>{esc(title)}</h1>"
            "<p class=dim>Measured, not decided. A companion to the "
            "<a href=\"report_summary.html\">cross-folder summary</a>.</p>"
            + exec_summary(R, by_stream) + _role_intro(R) + TERMS + synthetic_figures()
            + choices(R, by_stream) + detail_sections(R, by_stream)
            + (reproduction_section(run) if R["role"] == "steps_excluded" else "")
            + provenance(run))
    return page(title, body)


def summary_page(run: Path, roles: dict) -> str:
    cols = list(roles)
    rows = []
    per = {role: {st: {r["name"]: r for r in candidate_rows(R, st)}
                  for st in streams_of(R)} for role, R in roles.items()}
    heads = [f"{role} · {st}" for role in cols for st in per[role]]
    for name, label in CANDIDATES:
        row = [f"<b>{esc(label)}</b>"]
        for role in cols:
            for st in per[role]:
                r = per[role][st].get(name)
                if not r or r["n_ok"] == 0:
                    row.append("not run")
                    continue
                ret = r["retained"].get("0.5")
                row.append(f"flags {pct(r['band_q95'])} / {pct(r['paired_raw'])}<br>"
                           f"retained {rng_txt(ret) if ret else '—'}<br>"
                           f"accuracy {rng_txt(r['disc_acc'])}")
        rows.append(row)
    body = ("<h1>The surrogate screen — across folders</h1>"
            "<p class=dim>Measured, not decided.</p>"
            "<h2 id=\"summary\">Executive summary</h2>"
            "<p class=lede>Twelve candidates, measured on two folders that differ in almost "
            "everything: preparation (acute slices against in vivo pups), event extraction, "
            "frame interval and ROI count. <b>No shortlist is drawn.</b> Whether the right "
            "surrogate differs between datasets is a hypothesis this comparison tests, not a "
            "premise — and any difference below is confounded with all of those.</p>"
            + table(["candidate"] + heads, rows, "cross-folder comparison")
            + "".join(reach_block(R) for R in roles.values())
            + "<p class=dim>Each cell: checks flagged without adjustment — outside the "
              "band's 95th percentile / a raw paired <i>P</i> under 0.05 — since the "
              "Holm-adjusted rates are zero by construction (the boxes above); planted "
              "coordination retained at 50% participation; the "
              "per-ROI-only discriminator's accuracy (0.5 is chance). The Cossart data are "
              "DANDI:000219 (Dard, Picardo &amp; Cossart; Dard et al. 2022).</p>"
            + "<h2 id=\"pages\">The per-folder reports</h2><ul>"
            + "".join(f"<li><a href=\"report_{esc(r)}.html\">{esc(r)}</a></li>" for r in cols)
            + "</ul>" + TERMS + synthetic_figures() + provenance(run))
    return page("The surrogate screen — across folders", body)


# ---- the gate -----------------------------------------------------------------

def refuse_without_svg(name: str, text: str) -> None:
    if "<svg" not in text:
        raise SystemExit(f"{name}: no SVG on the page — refused. The render gate would "
                         f"pass it, and a report whose figures failed to draw would read "
                         f"as a report with nothing to show.")


def run_gate(run: Path, pages: list[Path]) -> dict:
    tools = run / "tools"
    rc_tool, ec_tool = tools / "render_check.py", tools / "edge_collisions.py"
    missing = [p.name for p in (rc_tool, ec_tool) if not p.is_file()]
    if missing:
        raise SystemExit(f"render gate: missing stamped copies in {tools}: "
                         f"{', '.join(missing)}. Copy them there (stamped) or pass "
                         f"--no-gate — the gate never passes by default.")
    record = {"pages": {}}
    svgdir = tools / "svg"
    svgdir.mkdir(parents=True, exist_ok=True)
    for pg in pages:
        shots = tools / "screens" / pg.stem
        r = subprocess.run([sys.executable, str(rc_tool), str(pg), "--out", str(shots),
                            "--json"], capture_output=True, text=True, encoding="utf-8",
                           errors="replace", timeout=900)
        try:
            rc_json = json.loads(r.stdout[r.stdout.find("{"):]) if "{" in r.stdout else None
        except ValueError:
            rc_json = None
        svgs = re.findall(r"<svg\b.*?</svg>", pg.read_text(encoding="utf-8"), re.S)
        paths = []
        for i, s in enumerate(svgs, 1):
            p = svgdir / f"{pg.stem}_fig{i}.svg"
            p.write_text(s, encoding="utf-8")
            paths.append(str(p))
        e = subprocess.run([sys.executable, str(ec_tool), *paths], capture_output=True,
                           text=True, encoding="utf-8", errors="replace", timeout=300)
        n_edges = sum(s.count('class="ds-edge') for s in svgs)
        record["pages"][pg.name] = {
            "render_check_exit": r.returncode, "render_check": rc_json,
            "render_check_tail": r.stdout[-1500:] if rc_json is None else None,
            "screenshots": str(shots),
            "edge_collisions_exit": e.returncode, "edge_collisions_out": e.stdout[-1500:],
            "edge_collisions_note": (f"{n_edges} draughtsman edges on this page: "
                                     + ("the check looked at nothing." if n_edges == 0
                                        else "checked.")),
        }
    (tools / "gate.json").write_text(json.dumps(record, indent=1), encoding="utf-8")
    return record


# ---- main ---------------------------------------------------------------------

def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--run", default=None,
                    help=f"run folder (default darkroom()/{OUT_DIRNAME}/)")
    ap.add_argument("--no-gate", action="store_true",
                    help="skip the render gate (the pages are still refused without SVG)")
    args = ap.parse_args(argv)
    if args.run:
        run = Path(args.run)
    else:
        from bugarach.paths import darkroom
        run = Path(darkroom()) / OUT_DIRNAME
    roles = {r: load_role(run, r) for r in ("steps_excluded", "cossart")
             if (run / r / "cells.csv").is_file()}
    if not roles:
        raise SystemExit(f"no folder results under {run}")
    written = []
    for role, R in roles.items():
        text = role_page(run, R)
        refuse_without_svg(f"report_{role}.html", text)
        p = run / f"report_{role}.html"
        p.write_text(text, encoding="utf-8")
        written.append(p)
    text = summary_page(run, roles)
    refuse_without_svg("report_summary.html", text)
    p = run / "report_summary.html"
    p.write_text(text, encoding="utf-8")
    written.append(p)
    for p in written:
        print(f"wrote {p}")
    if not args.no_gate:
        rec = run_gate(run, written)
        for name, r in rec["pages"].items():
            print(f"gate {name}: render_check exit {r['render_check_exit']}; "
                  f"edge_collisions exit {r['edge_collisions_exit']} — "
                  f"{r['edge_collisions_note']}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
