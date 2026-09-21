#!/usr/bin/env python3
"""Write the surrogate screen's reports: one page per folder and a cross-folder summary.

    python tools/build_surrogate_report.py                 # darkroom run folder, gate on
    python tools/build_surrogate_report.py --run DIR --no-gate

**Describes; decides nothing.** The plan
(``docs/proposals/2026-09-10-surrogate-evaluation-overnight.md``, "The report")
measures every candidate and shortlists none: the rule that turns these numbers
into a shortlist is designed afterwards, from them. So each page opens with the
problem and a picture of it, then what each candidate keeps and destroys, and ends
with **the choices the verdict rule must make, each beside the measurement that
bears on it** — never with a verdict.

Reads what ``tools/build_surrogate_screen.py`` wrote under ``--run`` (default
``darkroom()/2026-09-11-surrogate-screen/``) and writes there too: aggregates from
real recordings stay in the darkroom (FOUNDATIONS §5).

**What the 2026-09-11 murderboard changed here**, because each was a number that
read as a result and was not one:

* the discriminator column pooled the discriminator's own control rows with the
  candidate's cells — 12 rows where 6 cells existed — so the control validating a
  candidate was reported as evidence about it. Rows are now filtered by ``kind``.
* a candidate whose cells all stopped below *K* = 40 was shown as "0% flagged"
  where the paired yardstick cannot reach α at all; the cross-folder page dropped
  even that caveat. Unreachable cells are excluded from the denominator, counted,
  and named on both pages.
* the FOUNDATIONS §9 reconciliation was computed on the Holm-adjusted P the page
  itself says can never flag, so it read 0/0 by construction. It is computed on the
  unadjusted P the tables report, and the per-group shares are shown.
* "the comparison reads flat" was asserted against a table where twice-dithered
  exceeds once-dithered in every row.
* the graded freeze-half control and the 20% participation arm were measured and
  filtered out of every page; the freeze-half cell was also counted as a circular
  shift candidate cell.
* destruction on a 566-ROI twin cannot register removal at a scan that stops at 8
  ROIs: the page now computes what the metric could see before it reports what it
  saw.

Figures are **inline SVG only**, numbered, referred to by number and name; a page
with no SVG is refused. The **render gate** runs only from stamped copies in
``<run>/tools/`` and never passes by default. ⚠ ``edge_collisions.py`` checks only
draughtsman-style edges, which these figures do not have, so it passes without
looking; the gate record says so.
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

from bugarach import provenance, time_axis
from bugarach.surrogate_stats import smallest_n

OUT_DIRNAME = "2026-09-11-surrogate-screen"
ALPHA = 0.05
K_PAIRED_MIN = 2 / ALPHA - 1        # 39: below this a two-sided rank P cannot reach alpha

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
FREEZE = ("freeze_half", "freeze-half (graded destruction control)")
NAME = dict(CANDIDATES + CONTROLS + [FREEZE])

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
    """Plain name for a statistic; an f suffix reads as a multiple or as frames."""
    base, _, at = stat.partition("@")
    lab = STAT_LABEL.get(base, base)
    if not at:
        return lab
    if at.endswith("fr"):                       # absolute, as the Cossart folder sweeps it
        n = at[:-2]
        return f"{lab} at f = {n} frame" + ("" if n == "1" else "s")
    return f"{lab} at f = {at.rstrip('x')} × floor"


def cells_n(n: int) -> str:
    return f"{n} cell" if n == 1 else f"{n} cells"


def draws_n(n) -> str:
    return f"{int(n)} draw" if int(n) == 1 else f"{int(n)} draws"


# ---- reading ----------------------------------------------------------------

def _rows(path: Path) -> list[dict]:
    if not path.is_file():
        return []
    with open(path, encoding="utf-8", newline="") as fh:
        return list(csv.DictReader(fh))


def _json(path: Path):
    return json.loads(path.read_text(encoding="utf-8")) if path.is_file() else None


def _f(x) -> float:
    try:
        v = float(x)
    except (TypeError, ValueError):
        return float("nan")
    return v


def _b(x) -> bool:
    return str(x).strip().lower() in ("true", "1")


def _tri(x):
    """True / False / None — a blank field is *unknown*, never False (murderboard F3)."""
    s = str(x).strip().lower()
    return True if s in ("true", "1") else (False if s in ("false", "0") else None)


def load_role(run: Path, role: str) -> dict:
    d = run / role
    return {
        "role": role,
        "meta": _json(d / "meta.json") or {},
        "run_notes": _json(run / "run_notes.json") or {},
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


def _med(v):
    v = [x for x in v if isinstance(x, float) and math.isfinite(x)]
    return float(np.median(v)) if v else float("nan")


def _summ(v):
    v = [x for x in v if math.isfinite(x)]
    if not v:
        return None
    return {"min": min(v), "med": float(np.median(v)), "max": max(v), "n": len(v)}


def candidate_rows(R: dict, stream: str) -> list[dict]:
    """One row per candidate and control: cells, movement, flags, destruction, cost.

    Destruction-only cells (freeze-half) are NOT candidate cells and are returned as
    their own row; the discriminator's control rows are not the candidate's results.
    """
    cells = [c for c in R["cells"] if c["stream"] == stream
             and c["cell_id"] != FREEZE[0]]
    ok = {c["cell_id"]: c for c in cells if c["status"] == "ok"}
    # A cell whose generator returned its input measures nothing about the generator.
    noop = {cid for cid, c in ok.items()
            if _f(c.get("movement_share_moved")) == 0.0
            and _f(c.get("movement_share_rois_unchanged")) == 1.0}
    # 2/(K+1) <= alpha needs K > 39. Checks from a cell below that cannot flag.
    reach = {cid for cid, c in ok.items() if _f(c["K"]) > K_PAIRED_MIN}
    stats = [s for s in R["stats"] if s["stream"] == stream and s["scope"] == "all"
             and s["cell_id"] in ok]
    dest = [r for r in R["destruction"] if r["stream"] == stream
            and _b(r.get("planted_visible"))]
    disc = [r for r in R["disc"] if r["stream"] == stream and r.get("kind") == "candidate"]
    out = []
    for name, label in CANDIDATES + CONTROLS + [FREEZE]:
        if name == FREEZE[0]:
            mine, ok_mine = [], []
        else:
            mine = [c for c in cells if c["name"] == name]
            if not mine:
                continue
            ok_mine = [c for c in mine if c["status"] == "ok"]
        ids = {c["cell_id"] for c in ok_mine}
        st = [s for s in stats if s["cell_id"] in ids]
        st_scored = [s for s in st if s["cell_id"] not in noop]
        st_paired = [s for s in st_scored if s["cell_id"] in reach]

        def share(rows, pred):
            v = [pred(s) for s in rows]
            return (sum(v) / len(v)) if v else float("nan")

        per_stat = defaultdict(list)
        for s in st_paired:
            per_stat[s["stat"]].append(_f(s["paired_p"]) < ALPHA)
        flagged = sorted(k for k, v in per_stat.items() if v and sum(v) / len(v) >= 0.5)
        # Retained at 50% participation per K (the assessor's minimum ROIs together) and
        # per J; and the 20% arm, which the plan asked for and the first build dropped.
        jof = {c["cell_id"]: (_f(c["J"]) if c["J"] not in ("", None) else None)
               for c in (mine or [])}
        rjk = defaultdict(lambda: defaultdict(list))
        ret20 = defaultdict(list)
        for r in dest:
            is_mine = (_b(r.get("freeze_half")) if name == FREEZE[0]
                       else r["name"] == name and not _b(r.get("freeze_half"))
                       and r["cell_id"] in ids)
            if not is_mine:
                continue
            K = int(float(r["K"]))
            if r["participation"] == "0.5":
                rjk[K][jof.get(r["cell_id"])].append(_f(r["retained"]))
            elif r["participation"] == "0.2":
                ret20[K].append(_f(r["retained"]))
        dsc = [r for r in disc if r["name"] == name and r["status"] == "ok"
               and r["cell_id"] in ids]
        Ks = sorted({_f(c["K"]) for c in ok_mine if math.isfinite(_f(c["K"]))})
        out.append({
            "name": name, "label": label,
            "kind": ("control" if name in dict(CONTROLS) else
                     "destruction-control" if name == FREEZE[0] else "candidate"),
            "n_cells": len(mine), "n_ok": len(ok_mine),
            "n_noop": len(ids & noop), "n_unreachable": len(ids - reach),
            "J": sorted({_f(c["J"]) for c in mine if c["J"] not in ("", None)}),
            "J_unit": mine[0]["J_unit"] if mine else "",
            "K_lo": Ks[0] if Ks else float("nan"), "K_hi": Ks[-1] if Ks else float("nan"),
            "rms_disp": _med([_f(c.get("movement_rms_disp_frames")) for c in ok_mine]),
            "band_q95": share(st_scored, lambda s: _b(s["band_flag"])),
            "band_raw": share(st_scored, lambda s: _f(s["band_p"]) < ALPHA),
            "band_holm": share(st_scored, lambda s: _f(s["band_p_holm"]) < ALPHA),
            "paired_raw": share(st_paired, lambda s: _f(s["paired_p"]) < ALPHA),
            "paired_holm": share(st_paired, lambda s: _f(s["paired_p_holm"]) < ALPHA),
            "n_checks": len(st_paired),
            "flagged": flagged,
            "ret_JK": {K: {J: _med(v) for J, v in d.items()} for K, d in rjk.items()},
            "ret20": {K: _med(v) for K, v in ret20.items()},
            "disc_acc": _summ([_f(r["accuracy"]) for r in dsc]),
            "disc_void": ([_tri(r["void"]) for r in dsc].count(True) / len(dsc)
                          if dsc else float("nan")),
            "disc_powered": ([_tri(r.get("powered")) for r in dsc].count(True) / len(dsc)
                             if dsc else float("nan")),
            "disc_needs": max([_f(r.get("required_mice")) for r in dsc], default=float("nan")),
            "disc_mice": max([_f(r.get("n_mice")) for r in dsc], default=float("nan")),
            "disc_n": len(dsc),
            "cost": _med([_f(c["seconds_per_roi_per_draw"]) for c in ok_mine]),
        })
    return [r for r in out if r["n_ok"] or r["ret_JK"] or r["n_cells"]]


def ret_span(r: dict, sat: dict | None = None) -> str:
    """Coordination retained at 50% participation, smallest J -> largest J, largest K.

    A J at which the measure is saturated is marked, not printed as a result: the
    smallest radii are exactly where retention cannot fall, so an unmarked 0.96 there
    reads as a candidate keeping coordination when it is the twin's ROI count talking
    (blind role 4, 2026-09-11).
    """
    if not r.get("ret_JK"):
        return "—"
    d = r["ret_JK"][max(r["ret_JK"])]
    Js = sorted(j for j in d if j is not None)
    bad = (sat or {}).get("saturated") or {}

    def one(J):
        return num(d[J]) + ("<sup>†</sup>" if bad.get(J) else "")
    if not Js:
        return num(d.get(None))
    if len(Js) == 1:
        return one(Js[0])
    return f"{one(Js[0])} → {one(Js[-1])}"


SAT_FOOTNOTE = ("<p class=dim>† at this <i>J</i> the destruction measure is saturated — more "
                "co-active ROIs stay inside the assessor's coincidence bin than its scan "
                "reaches, so retention cannot fall there whatever the candidate does. The "
                "number describes the twin, not the candidate.</p>")


def power_rows(R: dict, stream: str) -> list[dict]:
    """Control power, with the reachability of the paired yardstick per cell.

    A control cell that ran at K <= 39 cannot produce a paired flag whatever it did to
    the statistic; recording that as "no" reports the cap as a property of the statistic.
    """
    K = {c["cell_id"]: _f(c["K"]) for c in R["cells"] if c["stream"] == stream}
    out = []
    for r in R["power"]:
        if r["stream"] != stream or r["scope"] != "all":
            continue
        k = K.get(r["cell_id"], float("nan"))
        out.append({"control": r["control"], "cell": r["cell_id"], "stat": r["stat"],
                    "paired": _b(r["moved_paired"]), "band": _b(r["band_flag"]),
                    "p": _f(r["paired_p"]), "K": k,
                    "reachable": math.isfinite(k) and k > K_PAIRED_MIN})
    return out


def yard_rows(R: dict, stream: str, scope: str = "all") -> list[dict]:
    return [{"stat": r["stat"], "hb": _f(r["neg_heldout_band"]),
             "hp": _f(r["neg_heldout_paired"]), "sb": _f(r["neg_synthetic_band"]),
             "sp": _f(r["neg_synthetic_paired"]), "n": r["n_splits"]}
            for r in R["yardsticks"] if r["stream"] == stream and r["scope"] == scope]


def high_neg_stats(R: dict, stream: str) -> set:
    """Statistics whose SYNTHETIC negative rate is above alpha in at least one scope.

    The page promises "a statistic whose negative rate is above alpha is marked where it
    is cited as evidence". The first build made the promise and marked nothing, while
    the fast interval-density statistic ran negative rates of 0.55-1.00 and was cited
    for nine of twelve candidates (blind role 4, 2026-09-11).
    """
    out = set()
    for y in R["yardsticks"]:
        if y["stream"] != stream:
            continue
        for col in ("neg_synthetic_band", "neg_synthetic_paired"):
            v = _f(y.get(col))
            if math.isfinite(v) and v > ALPHA:
                out.add(y["stat"])
    return out


NEG_FOOTNOTE = ("<p class=dim>‡ this statistic flags a fresh synthetic draw that should pass "
                "more often than α in at least one scope — so its appearance in <i>what gives "
                "it away</i> is weaker evidence than the others, and in the worst case none.</p>")


def zero_width_band_stats(R: dict) -> set:
    """(stream, statistic) whose mouse-split band has zero width.

    Where the real value is identically 0 by construction — the sub-floor rate, whose
    floor IS the observed minimum — the band's 2.5th and 97.5th percentiles coincide and
    "outside the 95% band" degenerates into "not exactly equal to zero". That is a
    presence test, not a percentile comparison, and it carried a third of the band rate
    (blind role 4, 2026-09-11).
    """
    out = set()
    for y in R["yardsticks"]:
        lo, hi = _f(y.get("band_q025")), _f(y.get("band_q975"))
        if math.isfinite(lo) and math.isfinite(hi) and lo == hi:
            out.add((y["stream"], y["stat"]))
    return out


def yardstick_reach(R: dict) -> dict:
    """What each yardstick COULD flag at the run's settings, beside what it did.

    The smallest P a rank test can return is fixed by its sample: the band's is
    1/(n_splits + 1), the paired histogram's 2/(K + 1). Holm multiplies the smallest P
    in a cell by the number of checks in it; past alpha, the adjusted yardstick cannot
    flag anything, for any candidate, the known-bad controls included. Unadjusted, the
    price is a family-wise false-flag rate per cell, which this reports rather than
    leaving to the reader.
    """
    # The Holm family is whatever the RUN used, not whatever this build would choose.
    # Runs before 2026-09-12 corrected across every scope, so the family is the checks per
    # cell; runs after it correct within scope and record the family in meta.json. Reading
    # the recorded value keeps a page describing the run that produced it rather than the
    # rule in force when the page was built.
    recorded = [((R["meta"].get("streams") or {}).get(st) or {}).get("correction_reach")
                for st in ((R["meta"].get("streams") or {}))]
    recorded = [int(c["m"]) for c in recorded if isinstance(c, dict) and c.get("m")]
    if recorded:
        m = max(recorded)
    else:
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

    # The two rates below sit beside the per-candidate tables and must count the same
    # things those tables count, or one page carries one label over two populations:
    # pooled scope only, no-op cells out, and — for the paired rate — cells that cannot
    # reach alpha out, exactly as candidate_rows() filters them. Computed over every
    # stream, since this box speaks for the folder. (Blind role 1, 2026-09-11: the old
    # version counted all five group scopes and scored unreachable cells as non-flags,
    # landing 14-16 points below the tables in the same breath as the sentence saying
    # those cells were excluded.)
    okc = {c["cell_id"]: c for c in R["cells"]
           if c["status"] == "ok" and c["cell_id"] != FREEZE[0]}
    noop = {cid for cid, c in okc.items()
            if _f(c.get("movement_share_moved")) == 0.0
            and _f(c.get("movement_share_rois_unchanged")) == 1.0}
    reach = {cid for cid, c in okc.items() if _f(c["K"]) > K_PAIRED_MIN}
    scored = [s for s in R["stats"] if s["scope"] == "all"
              and s["cell_id"] in okc and s["cell_id"] not in noop]
    paired = [s for s in scored if s["cell_id"] in reach]
    zw = zero_width_band_stats(R)
    on_zw = [s for s in scored if (s["stream"], s["stat"]) in zw]
    keep_zw = [s for s in scored if (s["stream"], s["stat"]) not in zw]

    def sh(rows, pred):
        v = [pred(s) for s in rows]
        return sum(v) / len(v) if v else float("nan")
    band_floor = 1.0 / (n_splits + 1) if math.isfinite(n_splits) else float("nan")
    k_max = max(Ks) if Ks else float("nan")
    paired_floor = 2.0 / (k_max + 1) if math.isfinite(k_max) else float("nan")
    unreach = sum(n for k, n in kc.items() if k <= K_PAIRED_MIN)
    return {
        "m": m, "n_splits": n_splits, "K_counts": dict(sorted(kc.items())),
        "band_floor": band_floor, "band_floor_holm": min(1.0, band_floor * m),
        "paired_floor": paired_floor, "paired_floor_holm": min(1.0, paired_floor * m),
        "min_band_holm": mn("band_p_holm"), "min_paired_holm": mn("paired_p_holm"),
        "share_band_q95": sh(scored, lambda s: _b(s["band_flag"])),
        "share_paired_raw": sh(paired, lambda s: _f(s["paired_p"]) < ALPHA),
        "n_scored": len(scored), "n_paired": len(paired),
        "n_zero_width": len(on_zw), "n_zw_stats": len(zw),
        "share_band_nozw": sh(keep_zw, lambda s: _b(s["band_flag"])),
        # Strictly, because a check fires on P < alpha and an adjusted P of exactly alpha
        # fires nothing. `ceil(m/alpha - 1)` named the sample that REACHES alpha, one
        # short of the sample that can flag: 1299 where 1300 is needed. The helper is
        # imported from surrogate_stats rather than restated here, because this formula
        # existing separately in two modules is how it came to be wrong in both.
        "splits_needed": smallest_n(m, ALPHA) if m else None,
        "K_needed": smallest_n(2 * m, ALPHA) if m else None,
        "fwer": 1 - (1 - ALPHA) ** m if m else float("nan"),
        "cells_unreachable": unreach, "cells_ok": len(Ks),
    }


def destruction_status_note(R: dict) -> str:
    """Which (participation, floor) arms were measured, and why one was not.

    The run records this per stream in meta.json's summary; the first build printed it
    nowhere, so a whole arm was missing from the table with nothing to say it had been
    tried (blind role 1, 2026-09-11).
    """
    st = ((R["meta"].get("summary") or {}).get("destruction_status") or {})
    skipped = sorted({v for d in st.values() for v in d.values() if not str(v).startswith("ok")})
    if not skipped:
        return ""
    where = sorted({f"{k.replace('p', '').replace('_K', ' participation, floor ')}"
                    for d in st.values() for k, v in d.items() if not str(v).startswith("ok")})
    return (f"<p class=dim><b>Not every arm was measured.</b> "
            f"{esc(', '.join(where))}: {esc('; '.join(skipped))}. The rest are recorded "
            f"<code>ok</code> in <code>meta.json</code>.</p>")


def reach_block(R: dict, named: bool = False) -> str:
    """The box that says what the yardsticks could detect at all. Named on a page
    that carries more than one folder, where two unlabelled boxes read as a duplicate."""
    y = yardstick_reach(R)
    if not y["m"]:
        return ""
    who = f"<b>{esc(R['role'])}:</b> " if named else ""
    return (
        f'<div class="warn"><p>{who}<b>⚠ Neither yardstick, Holm-adjusted, can flag anything '
        f"at these settings — so no Holm-adjusted rate is reported anywhere in this report, "
        f"and one would have read zero for every candidate, the known-bad controls "
        f"included.</b> Holm is applied per grid cell across {y['m']} checks (every statistic "
        f"in every scope). The band's smallest possible <i>P</i> is "
        f"1/({num(y['n_splits'], 0)} + 1) = {num(y['band_floor'], 4)}, which Holm lifts to "
        f"{num(y['band_floor_holm'], 2)}; the paired histogram's is 2/(<i>K</i> + 1) = "
        f"{num(y['paired_floor'], 3)} at the largest draw count reached, which Holm lifts to "
        f"{num(y['paired_floor_holm'], 2)}. A corrected test would need at least "
        f"{y['splits_needed']} mouse splits and {draws_n(y['K_needed'])}. Unadjusted, the "
        f"yardsticks do discriminate — {pct(y['share_band_q95'])} of the {y['n_scored']} "
        f"pooled checks fall outside the band's 95th percentile, and "
        f"{pct(y['share_paired_raw'])} of the {y['n_paired']} that a paired test can reach "
        f"have a raw paired <i>P</i> under 0.05 — and this report uses the unadjusted rates "
        f"throughout. These are the same two populations the per-candidate tables use. "
        f"<b>What that "
        f"costs:</b> at {y['m']} checks per cell and α = 0.05, the chance of at least one "
        f"false flag somewhere in a cell is {pct(y['fwer'])}; the held-out and synthetic "
        f"negatives below are the measured price per check. {cells_n(y['cells_unreachable'])} "
        f"of {y['cells_ok']} finished cells ran at 39 draws or fewer, where a raw paired "
        f"<i>P</i> under 0.05 is unreachable; their checks are excluded from every paired rate "
        f"and counted in the tables.</p>"
        + (f"<p><b>⚠ And the band rate is not one test.</b> {y['n_zw_stats']} of the "
           f"statistics have a mouse-split band of <b>zero width</b> — the sub-floor family, "
           f"whose real value is identically 0 because the floor is the observed minimum — so "
           f"for them \"outside the 95% band\" is an exact-inequality test, not a percentile "
           f"comparison. That is {y['n_zero_width']} of {y['n_scored']} pooled checks. With "
           f"them removed the band rate is {pct(y['share_band_nozw'])} rather than "
           f"{pct(y['share_band_q95'])}; both are reported here because the difference is the "
           f"measure changing, not the candidates.</p>" if y.get("n_zero_width") else "")
        + "</div>")


def intractable_reasons(R: dict) -> dict:
    """Why cells did not finish — projection and measurement kept apart."""
    out = defaultdict(int)
    for c in R["cells"]:
        if c["status"] != "intractable":
            continue
        w = c.get("why") or ""
        if w.startswith("dropped before running"):
            out["never run: cost projected past the run's stop time"] += 1
        elif w.startswith("not run"):
            out["never run: measured cost past the run's stop time"] += 1
        elif "resident" in w:
            out["killed at the memory cap"] += 1
        elif w.startswith("killed after"):
            out["killed at the hard time cap"] += 1
        elif "budget" in w:
            out["time budget spent below the minimum K"] += 1
        else:
            out["other"] += 1
    return dict(out)


def group_flags(R: dict, stream: str) -> dict:
    """Per-group flag shares and the pooled/per-group disagreement, on the RAW P.

    Computed on the unadjusted P the tables report. On the Holm-adjusted P both
    counters are zero by construction, which is what the first build reported and
    what FOUNDATIONS §9 was then said to be satisfied by.
    """
    by = defaultdict(dict)
    for s in R["stats"]:
        if s["stream"] != stream:
            continue
        by[(s["cell_id"], s["stat"])][s["scope"]] = _f(s["paired_p"]) < ALPHA
    groups = sorted({sc for v in by.values() for sc in v if sc != "all"})
    only_group = only_all = 0
    per = {g: [0, 0] for g in groups + ["all"]}
    for v in by.values():
        for sc, flag in v.items():
            if sc in per:
                per[sc][0] += bool(flag)
                per[sc][1] += 1
        if "all" not in v:
            continue
        g = any(v.get(x) for x in groups)
        only_group += bool(g and not v["all"])
        only_all += bool(v["all"] and not g)
    return {"groups": groups, "only_group": only_group, "only_all": only_all,
            "n": sum("all" in v for v in by.values()),
            # Each scope carries its own denominator: a group is only scored on the
            # checks that had it, so the pooled count is not the per-group count.
            "n_scope": {k: b for k, (_a, b) in per.items()},
            "share": {k: (a / b if b else float("nan")) for k, (a, b) in per.items()}}


def saturation_by_J(R: dict, stream: str) -> dict:
    """The saturation test at EVERY J in the sweep, not only the largest.

    ``expected = recruited x bin / (2J + 1)`` FALLS as J grows, so the largest J is the
    least saturated one in the sweep. Testing there and generalising declared a whole
    sweep measurable when its small-J end was not — and the small-J end is where every
    headline span starts (blind role 4, 2026-09-11).
    """
    tw = ((R["meta"].get("streams") or {}).get(stream) or {}).get("destruction_twins") or {}
    n_roi, dt = tw.get("n_roi"), _f(tw.get("dt"))
    bin_fr = 2 * int(tw.get("coincidence_half_window_frames", 2)) + 1
    ud = next((r for r in candidate_rows(R, stream)
               if r["name"] == "uniform_dither" and r.get("ret_JK")), None)
    if not ud or not n_roi:
        return {}
    Ks = sorted(ud["ret_JK"])
    Js = sorted(j for j in ud["ret_JK"][Ks[-1]] if j is not None)
    in_sec = ud["J_unit"] == "sec" and math.isfinite(dt) and dt
    recruited = 0.5 * n_roi
    per = {J: recruited * min(1.0, bin_fr / (2 * (J / dt if in_sec else J) + 1))
           for J in Js}
    return {"n_roi": n_roi, "recruited": recruited, "bin": bin_fr, "K_hi": Ks[-1],
            "per_J": per, "saturated": {J: e > Ks[-1] for J, e in per.items()},
            "unit": "s" if in_sec else "frames"}


def sat_Js(R: dict, stream: str) -> list:
    """The J values at which the measure cannot register removal, smallest first."""
    sj = saturation_by_J(R, stream)
    return [J for J, bad in (sj.get("saturated") or {}).items() if bad]


def destruction_reach(R: dict, stream: str) -> dict:
    """Could the destruction measure register removal on this twin at all?

    A planted event recruits ``participation × n_roi`` ROIs. A dither of radius J
    spreads each onset over 2J+1 frames, so the expected number still inside the
    assessor's coincidence bin is ``recruited × bin / (2J+1)``. When that stays above
    the largest K the assessor scans, every planted event trips the threshold however
    far the surrogate smears it, and "retained" cannot fall — the measure is saturated.
    """
    tw = ((R["meta"].get("streams") or {}).get(stream) or {}).get("destruction_twins") or {}
    n_roi, dt = tw.get("n_roi"), _f(tw.get("dt"))
    bin_fr = 2 * int(tw.get("coincidence_half_window_frames", 2)) + 1
    rows = candidate_rows(R, stream)
    ud = next((r for r in rows if r["name"] == "uniform_dither" and r.get("ret_JK")), None)
    if not (n_roi and ud):
        return {}
    Ks = sorted(ud["ret_JK"])
    Js = sorted(j for j in ud["ret_JK"][Ks[-1]] if j is not None)
    if not Js:
        return {}
    J_top = Js[-1]
    J_frames = J_top / dt if (ud["J_unit"] == "sec" and math.isfinite(dt) and dt) else J_top
    recruited = 0.5 * n_roi
    # Capped at what was recruited: bin/(2J+1) is a PROBABILITY of staying in the bin, so
    # it cannot exceed 1. Uncapped, a dither radius below the bin's half-width reported
    # more co-active ROIs than the event planted — 25.8 from a twin that recruits 15.5,
    # 471.7 from one that recruits 283 (caught 2026-09-11 while computing this per J).
    expected = recruited * min(1.0, bin_fr / (2 * J_frames + 1))
    return {"n_roi": n_roi, "recruited": recruited, "bin": bin_fr, "J_top": J_top,
            "J_frames": J_frames, "K_hi": Ks[-1], "K_lo": Ks[0], "expected": expected,
            "saturated": expected > Ks[-1], "unit": "s" if ud["J_unit"] == "sec" else "frames",
            "ret_hi": ud["ret_JK"][Ks[-1]].get(J_top), "ret_lo": ud["ret_JK"][Ks[0]].get(J_top)}


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


def table(head: list[str], rows: list[list[str]], label: str) -> str:
    th = "".join(f"<th>{h}</th>" for h in head)
    tr = "".join("<tr>" + "".join(f"<td>{c}</td>" for c in r) + "</tr>" for r in rows)
    return (f'<div class="wide" role="region" aria-label="{esc(label)}" tabindex="0">'
            f"<table><thead><tr>{th}</tr></thead><tbody>{tr}</tbody></table></div>")


# ---- SVG kit ----------------------------------------------------------------

FONT = 13


class Svg:
    def __init__(self, w: int, h: int, label: str):
        self.w, self.h, self.label, self.parts = w, h, label, []
        # An explicit ground: the page is light-only, and a transparent figure would
        # borrow whatever the viewer paints behind it.
        self.rect(0, 0, w, h, fill="#fff")

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

    def tri(self, x, y, s=4.5, fill="#111"):
        """A down-triangle: the one glyph this report uses to mark a value on an axis,
        never a vertical rule, which on a histogram reads as data."""
        self.add(f'<path d="M{x - s:.1f} {y:.1f} L{x + s:.1f} {y:.1f} '
                 f'L{x:.1f} {y + s * 1.6:.1f} Z" fill="{fill}"/>')

    def panel(self, x, y, letter):
        self.text(x, y, letter, size=14, weight="bold")

    def time_axis(self, x0, x1, y, t0, t1, name="time"):
        """The viewer's axis: 60-base ticks, labels such as 45s, 2m, 2m30s."""
        self.line(x0, y, x1, y)
        for t in time_axis.ticks(t0, t1):
            x = x0 + (t - t0) / (t1 - t0) * (x1 - x0)
            self.line(x, y, x, y + 4)
            self.text(x, y + 18, time_axis.label(t), anchor="middle")
        self.text((x0 + x1) / 2, y + 38, name, anchor="middle", fill="#444")

    def render(self) -> str:
        return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {self.w} {self.h}" '
                f'style="--w:{self.w}px" role="img" aria-label="{esc(self.label)}" '
                f'font-family="system-ui, sans-serif">' + "".join(self.parts) + "</svg>")


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
    """A real-like raster, its uniform dither, the leak lane, the interval histogram."""
    from bugarach import surrogates
    tr, n = _synthetic_trains()
    res = surrogates.generate("uniform_dither", tr, (0, n), ("fig1", "demo", "UD", 0),
                              J=float(J_DEMO))
    sur = [np.sort(np.asarray(v, np.int64)) for v in res.trains]
    t0, t1 = 0.0, 120.0
    svg = Svg(900, 452, "Figure 1: panel A, a synthetic raster; panel B, the same ROIs after "
                        "uniform dither with the intervals shorter than the floor marked "
                        "above; panel C, the pooled interval histogram of both")
    x0, x1 = 150, 560

    def X(fr):
        return x0 + (fr * DT - t0) / (t1 - t0) * (x1 - x0)

    def raster(trains, top, label, lane):
        svg.text(x0 - 10, top - 22 if lane else top - 6, label, anchor="end", weight="bold")
        if lane:
            svg.text(x0 - 10, top - 6, "shorter than f", anchor="end", size=12, fill="#444")
            svg.line(x0, top - 10, x1, top - 10, stroke="#bbb")
        n_sub = 0
        for r, v in enumerate(trains):
            y = top + r * 9
            for fr in v[(v * DT >= t0) & (v * DT <= t1)]:
                svg.line(X(fr), y, X(fr), y + 7, w=1.3)
            if lane:
                iv = np.diff(v)
                for i in np.nonzero(iv < FLOOR)[0]:
                    a = v[i + 1]
                    if t0 <= a * DT <= t1:
                        n_sub += 1
                        svg.tri(X(a), top - 21, 4)
        return n_sub
    svg.panel(24, 34, "A")
    raster(tr, 40, "real", False)
    svg.panel(24, 219, "B")
    raster(sur, 225, "UD, J = 1.6 s", True)
    svg.time_axis(x0, x1, 360, t0, t1, "time (synthetic recording)")
    # Panel C: the interval histogram, all ROIs pooled, one bin per frame.
    hx0, hx1, hy0, hy1 = 640, 870, 60, 330
    svg.panel(600, 34, "C")
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
        if i:                                   # join the steps so they read as one series
            svg.line(xl + 1, prev, xl + 1, y, w=1.0, stroke="#111")
        prev = y
    # y axis: a share of intervals, with ticks — not an unlabelled box.
    svg.line(hx0, hy0, hx0, hy1)
    for q in (0.0, 0.5, 1.0):
        yq = hy1 - q * (hy1 - hy0)
        svg.line(hx0 - 4, yq, hx0, yq)
        svg.text(hx0 - 7, yq + 4, pct(q * top), anchor="end", size=11)
    svg.add(f'<text x="{hx0 - 40}" y="{(hy0 + hy1) / 2:.1f}" font-size="12" fill="#444" '
            f'text-anchor="middle" transform="rotate(-90 {hx0 - 40} '
            f'{(hy0 + hy1) / 2:.1f})">share of intervals</text>')
    svg.line(hx0, hy1, hx1, hy1)
    for k in (0, 10, 20, 30):
        xk = hx0 + k * bw
        svg.line(xk, hy1, xk, hy1 + 4)
        svg.text(xk, hy1 + 18, f"{k * DT:g}s", anchor="middle")
    # The floor is marked on the axis and named in the legend. A floating label here
    # collided with the tick row, and moving it down collided with the axis title
    # (both measured, 2026-09-11) — the legend is the one place nothing drifts into.
    svg.tri(hx0 + FLOOR * bw, hy1 + 4, 5)
    svg.text((hx0 + hx1) / 2, 380, "interval between one ROI's successive onsets",
             anchor="middle", fill="#444")
    svg.text((hx0 + hx1) / 2, 398, "(every ROI pooled)", anchor="middle", size=11, fill="#444")
    svg.rect(hx0, 20, 12, 10, fill="#bbb")
    svg.text(hx0 + 18, 29, "real", size=12)
    svg.line(hx0 + 62, 25, hx0 + 76, 25, w=2.2)
    svg.text(hx0 + 82, 29, "after UD", size=12)
    svg.tri(hx0 + 152, 21, 5)
    svg.text(hx0 + 162, 29, "floor f", size=12)
    return svg


def fig_candidates() -> Svg:
    """One ROI, and what each of the twelve candidates does to it."""
    from bugarach import surrogates
    tr, n = _synthetic_trains(n_roi=6, seed=7)
    roi = [max(tr, key=len)]
    rows = [("the real ROI", roi[0])]
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
    h = 46 + 26 * len(rows) + 56
    svg = Svg(900, h, "Figure 2: one synthetic ROI's onsets on the top row, and the same "
                      "single ROI after each of the twelve candidates at J = 1.6 s — every "
                      "row is one ROI, not one cell of a population")
    x0, x1 = 268, 880

    def X(fr):
        return x0 + (fr * DT - t0) / (t1 - t0) * (x1 - x0)
    svg.text(x0 - 12, 24, "one ROI, before and after each candidate", anchor="end", size=12,
             fill="#444")
    # NOT A RASTER, and drawn so it cannot be read as one: banded rows with explicit
    # borders, round marks rather than spike bars, and a bracket saying every row is the
    # same ROI. A caption saying "this is not a raster" was the previous answer, and a
    # label cannot undo an idiom the reader recognises before reading it.
    for i, (label, v) in enumerate(rows):
        y = 36 + i * 26
        svg.rect(x0, y, x1 - x0, 22, fill="#f4f6f5" if i % 2 else "#fff", stroke="#e2e7e5",
                 sw=0.8)
        svg.text(x0 - 12, y + 15, label, anchor="end",
                 weight="bold" if i == 0 else "normal")
        if v is None:
            svg.text(x0 + 4, y + 15, f"not drawn ({notes.get(label, 'error')})", size=12,
                     fill="#444")
            continue
        for fr in v[(v * DT >= t0) & (v * DT <= t1)]:
            svg.circle(X(fr), y + 11, 2.6)
    # The bracket sits at the far left, clear of the row labels: at x0 - 176 it clipped
    # "window shuffling (WIN-SHUFF)", the longest of them (measured, 2026-09-11).
    bx = 30
    svg.line(bx, 36 + 26, bx, 36 + 26 * len(rows) + 22, w=1.2)
    svg.line(bx, 36 + 26, bx + 6, 36 + 26, w=1.2)
    svg.line(bx, 36 + 26 * len(rows) + 22, bx + 6, 36 + 26 * len(rows) + 22, w=1.2)
    svg.add(f'<text x="{bx - 6}" y="{36 + 13 * len(rows) + 22:.1f}" font-size="12" '
            f'fill="#444" text-anchor="middle" transform="rotate(-90 {bx - 6} '
            f'{36 + 13 * len(rows) + 22:.1f})">the same ROI, twelve times</text>')
    svg.time_axis(x0, x1, 40 + 26 * len(rows), t0, t1, "time (synthetic recording)")
    return svg


def fig_windows() -> Svg:
    """The generation window, its 60-second analysis windows and the 5-second edge bands."""
    from bugarach import surrogate_stats as sst
    T, aw, eb = 300.0, sst.ANALYSIS_WINDOW_SEC, sst.EDGE_BAND_SEC
    svg = Svg(900, 268, "Figure 3: a 5-minute generation window cut into 60-second "
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
    svg.time_axis(x0, x1, 190, 0.0, T, "time (synthetic recording)")
    svg.rect(x0, 240, 14, 10, fill="#999")
    svg.text(x0 + 20, 249, "edge band, generation window", size=12)
    svg.rect(x0 + 260, 240, 14, 10, fill="#ccc")
    svg.text(x0 + 280, 249, "edge band, analysis window", size=12)
    return svg


# ---- data figures (aggregates only) -----------------------------------------

def fig_flags(rows_by_stream: dict, role: str, neg: dict) -> Svg:
    """Share of checks flagged per candidate, under each yardstick, with the negatives.

    Two marks, no connector: the marks are two different yardsticks, and a line between
    them reads as a change in one quantity (murderboard, role 8).
    """
    streams = list(rows_by_stream)
    names = [lab for _, lab in CANDIDATES + CONTROLS]
    h = 76 + 24 * len(names) + 58
    colw = 260
    w = max(250 + colw * len(streams) + 20, 780)   # the two legend entries need 780
    svg = Svg(w, h, f"Figure 4 ({role}): share of checks flagged per candidate under the "
                    "mouse-split band and the paired surrogate histogram, unadjusted, with "
                    "the exchangeable negatives' flag rates as reference lines")
    for j, st in enumerate(streams):
        cx0 = 250 + j * colw
        cx1 = cx0 + colw - 40
        svg.text((cx0 + cx1) / 2, 24, f"{st} stream", anchor="middle", weight="bold")
        for q in (0, 0.5, 1.0):
            xq = cx0 + q * (cx1 - cx0)
            svg.line(xq, 52, xq, 56 + 24 * len(names), stroke="#ddd")
            svg.text(xq, 74 + 24 * len(names), pct(q), anchor="middle", size=12)
        svg.text((cx0 + cx1) / 2, 92 + 24 * len(names), "checks flagged (%)", anchor="middle",
                 size=12, fill="#444")
        # the negatives: what each yardstick flags on something that should pass
        # Two reference lines. At equal rates they sit at the same x, so they get ONE
        # label: two staggered strings there still overlapped when measured.
        vals = {k: (neg.get(st) or {}).get(k) for k in ("band", "paired")}
        vals = {k: v for k, v in vals.items() if v is not None and math.isfinite(v)}
        same = len(vals) == 2 and abs(vals["band"] - vals["paired"]) < 1e-9
        for row, (key, dash) in enumerate((("band", "3 3"), ("paired", "1 3"))):
            if key not in vals:
                continue
            xv = cx0 + vals[key] * (cx1 - cx0)
            svg.line(xv, 50, xv, 56 + 24 * len(names), stroke="#b36b00", dash=dash)
            if same and row:
                continue
            lab = (f"band / paired negative {pct(vals[key])}" if same
                   else f"{key} negative {pct(vals[key])}")
            svg.text(xv, 34 + row * 16, lab, anchor="middle", size=11, fill="#b36b00")
        by = {r["label"]: r for r in rows_by_stream[st]}
        for i, lab in enumerate(names):
            y = 64 + i * 24
            if j == 0:
                svg.text(240, y + 4, lab, anchor="end", size=12)
            r = by.get(lab)
            if not r or not r["n_ok"]:
                svg.text(cx0, y + 4, "not measured", size=12, fill="#444")
                continue
            if math.isfinite(r["band_q95"]):
                svg.circle(cx0 + r["band_q95"] * (cx1 - cx0), y - 4, 5, fill="#fff",
                           stroke="#111")
            if math.isfinite(r["paired_raw"]):
                svg.circle(cx0 + r["paired_raw"] * (cx1 - cx0), y + 5, 4.5)
            else:
                svg.text(cx0, y + 9, "paired unreachable (≤ 39 draws)", size=11, fill="#444")
    yl = h - 16
    svg.circle(250, yl - 4, 5, fill="#fff", stroke="#111")
    svg.text(260, yl, "band (upper mark)", size=12)
    svg.circle(420, yl - 4, 4.5)
    svg.text(430, yl, "paired histogram (lower mark)", size=12)
    return svg


def _shade(v: float) -> tuple[str, str]:
    """Retained 1 -> dark ink (kept), 0 -> white (removed); returns (fill, text colour)."""
    v = max(0.0, min(1.0, v))
    lo, hi = (255, 255, 255), (27, 42, 38)
    rgb = tuple(round(a + (b - a) * v) for a, b in zip(lo, hi))
    return "#%02x%02x%02x" % rgb, ("#fff" if v > 0.55 else "#111")


def fig_destruction(rows_by_stream: dict, role: str) -> Svg:
    """Retained at 50% participation, every candidate × J, at both ends of the K scan.

    One grid per (stream, K), stacked rather than side by side so eight J columns fit
    the page at every width the report is rendered at.
    """
    lab_w, cw, rh = 230, 46, 22
    names = [(n, lab) for n, lab in CANDIDATES + CONTROLS + [FREEZE]]
    blocks = []
    for st, rows in rows_by_stream.items():
        by = {r["name"]: r for r in rows}
        Ks = sorted({K for r in rows for K in (r.get("ret_JK") or {})})
        Js = sorted({J for r in rows for d in (r.get("ret_JK") or {}).values() for J in d
                     if J is not None})
        unit = next((r["J_unit"] for r in rows if r.get("J_unit")), "sec")
        for K in ([Ks[0], Ks[-1]] if len(Ks) > 1 else Ks):
            blocks.append((st, K, by, Js, unit))
    ncol = max((len(Js) for *_, Js, _ in blocks), default=0) + 1
    w = max(lab_w + ncol * cw + 30, 660)     # the legend needs 660 whatever the grid is
    block_h = 56 + len(names) * rh + 22
    h = block_h * len(blocks) + 34
    svg = Svg(w, h, f"Figure 5 ({role}): share of planted coordination retained after each "
                    "candidate at 50% participation, for every J, at the smallest and the "
                    "largest number of ROIs the assessor requires active together")
    y0 = 0
    for st, K, by, Js, unit in blocks:
        cols = [None] + Js
        svg.text(0, y0 + 20, f"{st} stream · {K} co-active ROIs required", weight="bold",
                 size=13)
        svg.text(lab_w - 10, y0 + 42, f"J ({'s' if unit == 'sec' else 'frames'})",
                 anchor="end", size=12, fill="#444")
        for c, J in enumerate(cols):
            svg.text(lab_w + c * cw + cw / 2, y0 + 42, "no J" if J is None else f"{J:g}",
                     anchor="middle", size=12)
        for i, (n, lab) in enumerate(names):
            y = y0 + 50 + i * rh
            svg.text(lab_w - 10, y + 15, lab, anchor="end", size=12)
            d = ((by.get(n) or {}).get("ret_JK") or {}).get(K)
            if not d:
                svg.text(lab_w + 4, y + 15, "not measured", size=12, fill="#444")
                continue
            for c, J in enumerate(cols):
                v = d.get(J)
                if v is None or not math.isfinite(v):
                    continue
                fill, ink = _shade(v)
                svg.rect(lab_w + c * cw + 1, y + 1, cw - 2, rh - 2, fill=fill,
                         stroke="#c9d1ce", sw=0.6)
                svg.text(lab_w + c * cw + cw / 2, y + 15, num(v), anchor="middle", size=12,
                         fill=ink)
        y0 += block_h
    fill_k, _ = _shade(1.0)
    svg.rect(0, h - 26, 14, 12, fill=fill_k)
    svg.text(20, h - 16, "1 = kept", size=12)
    svg.rect(110, h - 26, 14, 12, fill="#fff", stroke="#c9d1ce")
    svg.text(130, h - 16, "0 = removed", size=12)
    svg.text(230, h - 16, "above 1 = draw noise", size=12)
    svg.text(400, h - 16, "blank = that J not run", size=12, fill="#444")
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
/* Intrinsic width, and the container scrolls. Letting a figure scale into the column
   was tried and measured: at 900px and 430px the 12-13px labels rendered at 8.1px,
   under the 11px floor, on every page. Legibility wins and the sideways scroll on a
   narrow window stays a known cost, recorded in the report's residual flags. */
figure svg{display:block;width:var(--w);max-width:none;height:auto}
figcaption{font-size:15px;color:#222;margin-top:6px}
.warn{border-left:4px solid #b36b00;padding:6px 12px;background:#fff6e8}
.resid li{margin-bottom:6px}
code{font-size:14px}
"""


def page(title: str, body: str) -> str:
    # The title rides on the charset line: a literal opening with <title> is what
    # sapper SAP005 refuses, since that is how a page loses its charset.
    return (f'<!doctype html><meta charset="utf-8"><title>{esc(title)}</title>\n'
            '<meta name="viewport" content="width=device-width, initial-scale=1">\n'
            f"<style>{CSS}</style>\n"
            f"<main>\n{body}\n</main>\n")


PROBLEM = """
<h2 id="problem">The problem</h2>
<p class=lede>A coordinated-event detector with no labels can be trained one way here: teach a
model to tell a real recording from a <b>surrogate</b> of itself — a resampled copy that keeps
each ROI's own timing and destroys the timing <i>between</i> ROIs. Whatever the model learns to
spot is then coordination. That holds only while the surrogate differs from real data in
cross-ROI timing and nothing else.</p>
<p>When something else gives the surrogate away, it <b>leaks</b>, and the model learns the
giveaway instead. On 2026-09-10 a review killed the surrogate a self-supervised detector was to
be built on for exactly that: uniform dither manufactures within-ROI intervals shorter than any
real one, so a single ROI is enough to tell the copy from the original (Figure 1) — a defect
Gerstein described in 2004. <b>Two nulls this project already ships are among the candidates
here</b>: the dither behind the modularity result, and the per-ROI circular shift the assessor
uses, which is also the standard null in the Cossart lab's own published analysis of the other
folder in this screen.</p>
<p>Two symbols carry the measurements below. <b><i>J</i></b> is the jitter radius: how far a
dither may move one onset, ± seconds or frames, with the other candidates matched to it by
root-mean-square displacement. <b><i>f</i></b> is the provisional dead time — the shortest
interval the extractor can emit is the producer's number and is not known, so the candidates
use <i>f</i> in its place. Both are defined again, with everything else, under <i>Terms</i>.</p>
<p>So this report measures what each candidate keeps and what it destroys. It shortlists
nothing: the rule that turns these measurements into a choice is designed afterwards, from
them. The earlier review's own safeguard — comparing a once-dithered recording against a
twice-dithered one — could not separate them; <i>The reproduction</i> measures by how much.</p>
"""


SUMMARY_TERMS = """
<h2 id="terms">Terms this page uses</h2>
<table><tbody>
<tr><td>ROI, grid cell</td><td>an ROI is one imaged cell's trace. A <b>grid cell</b> is one
combination of candidate, stream, <i>J</i> and any other swept parameter — the unit of this
screen, and what "cell" means on these pages.</td></tr>
<tr><td><i>J</i>, <i>f</i></td><td>the jitter radius, and the provisional dead time the
candidates use in place of the producer's unknown one.</td></tr>
<tr><td><i>K</i></td><td><b>two different things.</b> In the flag rates, the number of surrogate
draws per grid cell — that sets the smallest <i>P</i> a paired test can return, 2/(<i>K</i> + 1).
In the retained column, the assessor's scan over the minimum number of ROIs active
together.</td></tr>
<tr><td>band / paired</td><td>the two yardsticks: real against real across 100 mouse-grouped half
splits, and the statistic ranked among that cell's own surrogate draws. Two views of one
statistic, not independent methods.</td></tr>
<tr><td>unreachable</td><td>that candidate's cells all ran at 39 draws or fewer, where a raw paired
<i>P</i> under 0.05 cannot be reached at all — so no rate is reported rather than a zero.</td></tr>
<tr><td>retained, saturated</td><td>planted coordination still visible after the surrogate: 1
keeps it all, 0 removes it. <b>Saturated</b> means the measure could not have registered removal
on that folder's twin, so its numbers are not evidence about the candidate.</td></tr>
<tr><td>void</td><td>the discriminator's own positive or negative control failed, so its
accuracy supports no claim.</td></tr>
</tbody></table>
"""


def terms_table(role: str, f_sweep: str) -> str:
    return f"""
<h2 id="terms">Terms</h2>
<table><tbody>
<tr><td>⚠</td><td>marks a caveat, an assumption, or something this report could not
verify.</td></tr>
<tr><td>ROI, onset</td><td>region of interest, one imaged cell's trace; an onset is the time one
of its events begins.</td></tr>
<tr><td>the producer</td><td>the lab stage upstream of this analysis: the MATLAB pipeline that
extracts events and writes the export folder this screen reads. Its extractor's shortest
emittable interval is "the producer's number".</td></tr>
<tr><td>the assessor</td><td>this project's existing coordinated-event detector. Its null is the
per-ROI circular shift, and its scan over how many ROIs must be active together is what the
destruction measure is scored against.</td></tr>
<tr><td>stream</td><td>an export folder carries one or more separately extracted event sets per
recording — here <b>fast</b> and <b>slow</b> for the producer's folder, and a single
<b>events</b> stream for the Cossart folder.</td></tr>
<tr><td>frame interval (d<i>t</i>)</td><td>the seconds between imaging frames; it is fixed at
0.1 s in the producer's folder and varies by session in the Cossart folder.</td></tr>
<tr><td>the six known-bad controls</td><td>each is built to fail one statistic, so a statistic
it does not move is blind there. <b>do-nothing</b> returns its input; <b>interval shuffle</b>
permutes one ROI's intervals; <b>homogeneous resample</b> redraws its onsets at a constant rate;
<b>edge thinning</b> and <b>edge piling</b> move onsets away from and toward a window's edges;
<b>per-window circular shift</b> shifts each analysis window separately. <b>freeze-half</b> is
the graded destruction control: half the ROIs are put back unchanged, so it should land between
do-nothing and the circular shift.</td></tr>
<tr><td>grid cell</td><td>one combination of candidate, stream, <i>J</i> and any other swept
parameter — the unit of this screen. "Cell" alone in this report always means a grid cell; an
imaged cell is an ROI.</td></tr>
<tr><td>surrogate</td><td>a resampled copy of a recording that keeps each ROI's own timing and
destroys the timing between ROIs.</td></tr>
<tr><td>leak</td><td>a real-versus-surrogate difference visible without any cross-ROI
information — one ROI at a time.</td></tr>
<tr><td><i>J</i></td><td>jitter radius: how far a dither may move one onset, ± seconds (or
frames); other candidates are matched to it by root-mean-square displacement.</td></tr>
<tr><td><i>f</i>, dead time</td><td>the shortest interval between two onsets of one ROI the
producer's extractor can emit is not known — it is the producer's number. In its place the
candidates use a provisional dead time <i>f</i>, {f_sweep}.</td></tr>
<tr><td>frame</td><td>one imaging frame; every generator and statistic works on frame indices,
the nearest whole number to <i>t</i>/d<i>t</i>.</td></tr>
<tr><td>generation / analysis window</td><td>the span a surrogate is generated over (the
baseline, or the whole recording where no regions are declared), and the 60-second cuts of it
that are scored (Figure 3).</td></tr>
<tr><td>draws</td><td>surrogate draws per grid cell (never below 19). The count fixes the
smallest <i>P</i> a paired test can return: 2/(draws + 1). ⚠ The plan writes this <i>K</i>, and
so do the run's CSV columns, but this project's glossary reserves <i>K</i> for the assessor's
coactivity floor — so these pages write "draws" and "co-active ROIs" and leave <i>K</i>
alone.</td></tr>
<tr><td>co-active ROIs</td><td>the assessor's threshold — how many ROIs must be active together
for an event to count. The destruction measure is read at the smallest and largest value the
assessor scans.</td></tr>
<tr><td>the floor</td><td>the shortest within-ROI interval actually present in a folder's
baselines (0.40 s in the producer's fast stream, 2 frames in the Cossart folder). It is what
Figure 1 marks; <i>f</i> above is the dead time swept in units of it.</td></tr>
<tr><td>the three yardsticks</td><td><b>mouse-split band</b>: real against real across 100
mouse-grouped half splits — the scale of between-mouse variation. <b>Paired surrogate
histogram</b>: the statistic on the real recordings ranked among <i>K</i> draws of the same
recordings; the one-sided rank <i>P</i> is Amarasingham et al. 2012's, and doubling it for two
sides is this screen's convention, with a floor of 2/(<i>K</i> + 1). <b>Exchangeable
negative</b>: a real held-out half, and a fresh synthetic draw, scored as if each were a
candidate — how often a yardstick flags what should pass. The first two are two views of one
statistic on one set of recordings, not two independent methods.</td></tr>
<tr><td>Holm</td><td>Holm's step-down adjustment (Holm 1979), applied per grid cell across every
statistic in every scope, separately for each yardstick.</td></tr>
<tr><td>destruction, retained</td><td>whether a surrogate removes coordination planted in a
synthetic twin; <b>retained</b> is the planted twin's coactivity excess over the unplanted
twin's after the surrogate, as a share of the same before it: 1 keeps it all, 0 removes it.
Above 1 is draw noise, not more coordination than was planted.</td></tr>
<tr><td>void, powered</td><td>the discriminator marks a result <b>void</b> when its own positive
or negative control failed, and <b>not powered</b> when the fold count is below the mice its
effect size needs.</td></tr>
<tr><td>no-op cell</td><td>a grid cell whose generator returned its input unchanged — at the
smallest <i>J</i> some bins round to a single frame. It measures nothing about the candidate and
is excluded from that candidate's rates.</td></tr>
<tr><td>KS</td><td>Kolmogorov–Smirnov distance between two interval distributions.</td></tr>
<tr><td>AUC</td><td>area under the receiver-operating curve: how well the sub-floor rate alone
separates real windows from dithered ones; 0.5 is chance. ⚠ Because the real sub-floor rate is
0 in every window <b>by construction</b>, this reduces exactly to 0.5 × (1 + the dithered
share) — it is the column beside it rescaled, not a second piece of evidence.</td></tr>
<tr><td>UD, UDD, JISI-D, ISI-D, WIN-SHUFF, TR-SHIFT</td><td>the names used by Stella et al. 2022,
who introduce UDD and WIN-SHUFF and take the others from earlier work: joint-ISI and ISI
dithering from Gerstein 2004, trial shifting from Pipa et al. 2008 and Harrison &amp; Geman
2009.</td></tr>
</tbody></table>
"""


def synthetic_figures(R: dict | None, which: tuple) -> str:
    """Figures 2 and 3 (apparatus); Figure 1 is placed with the problem."""
    out = []
    if 2 in which:
        out.append(figure(2, "What each candidate does to one ROI", fig_candidates(),
                          "The top row is one synthetic ROI's onsets; every row below is "
                          "<b>that same ROI</b> after one candidate at <i>J</i> = 1.6 s, with "
                          "<i>f</i> = 4 frames where the candidate takes one and a 5-minute "
                          "kernel for operational-time dither. Each band is one method's "
                          "output for that one ROI; onsets are round marks, not spikes. "
                          "Joint-ISI and ISI dither run here "
                          "without Gerstein's square root, at this screen's smoothing and "
                          "dead-time settings rather than Stella et al.'s."))
    if 3 in which:
        out.append(figure(3, "The window anatomy", fig_windows(),
                          "A surrogate is generated over the whole generation window, then cut "
                          "into 60-second analysis windows for scoring. The edge-band "
                          "statistics count onsets in the 5-second bands at each end: dark at "
                          "the generation window's edges, light at each analysis window's. ⚠ "
                          "The 60-second analysis window is inherited from the earlier review, "
                          "not justified; the 5-second band is declared, not justified."))
    return "".join(out)


def fig1_block(R: dict | None) -> str:
    note = ""
    if R is not None and R["role"] == "cossart":
        tw = ((R["meta"].get("streams") or {}).get("events") or {}).get("destruction_twins") or {}
        dt = _f(tw.get("dt"))
        note = (" ⚠ This figure is drawn at the <code>steps_excluded</code> fast stream's "
                f"scale — d<i>t</i> = {DT} s, floor {FLOOR} frames — not this folder's "
                f"(d<i>t</i> ≈ {num(dt, 3)} s, floor 2 frames). It illustrates what a leak "
                "is; it is not this folder's data.")
    return figure(
        1, "A surrogate and its leak", fig_leak(),
        "The leak is the interval mass a surrogate puts below the floor — intervals no real "
        "ROI has, so the copy can be told from the original one ROI at a time. <b>A</b>: "
        "fourteen synthetic ROIs, one row each, over two minutes. <b>B</b>: the same ROIs "
        "after uniform dither (UD) at <i>J</i> = 1.6 s; each triangle above marks an interval "
        "shorter than the floor <i>f</i>. <b>C</b>: the pooled interval histogram, real (grey "
        "bars) against UD (black steps), with the floor marked on the axis; UD's mass left of "
        "it is the leak." + note)


def _cossart_J_note(m: dict) -> str:
    """J is a frame count on this folder, and a frame is not one duration here.

    The frame interval varies by session, so a single grid cell pools jitter radii that
    differ in seconds by the same spread (blind role 4, 2026-09-11).
    """
    dts = [_f(x) for x in
           (((m.get("streams") or {}).get("events") or {}).get("dt_values") or [])]
    dts = sorted(x for x in dts if math.isfinite(x) and x > 0)
    if len(dts) < 2 or dts[0] == dts[-1]:
        return ""
    lo, hi = dts[0], dts[-1]
    return (f"<div class=\"warn\"><p><b>⚠ <i>J</i> is swept in frames here, and a frame is not "
            f"one duration on this folder.</b> The frame interval ranges {lo:.4f}–{hi:.4f} s "
            f"across sessions, a {100 * (hi - lo) / lo:.0f}% spread, so one grid cell pools "
            f"radii that differ in real time by that much: <i>J</i> = 32 frames is "
            f"{32 * lo:.2f} s in the fastest session and {32 * hi:.2f} s in the slowest. Every "
            f"<i>J</i> table and Figure 5 on this page inherit that spread, and the "
            f"RMS-movement column is the only place it shows.</p></div>")


def _role_intro(R: dict) -> str:
    m = R["meta"]
    notes = R.get("run_notes") or {}
    first, resumed = notes.get("first_agent") or {}, notes.get("resumed_run") or {}
    role = R["role"]
    if role == "cossart":
        cite = ("<p>Data: in vivo two-photon recordings of hippocampal CA1 in mouse pups from "
                "Cossart and Picardo's group at INMED U1249, dataset <b>DANDI:000219</b> "
                "(Dard, Picardo &amp; Cossart), analyzed in Dard et al. 2022. One stream; no "
                "groups; each whole recording is a generation window, an assumption, since the "
                "folder declares no regions. ⚠ The dandiset <b>version</b> is not recorded in "
                "this export's provenance, so the citation below cannot name the one "
                "downloaded; the data are CC-BY-4.0.</p>" + _cossart_J_note(m))
    else:
        cite = ("<p>Data: the producer's <code>steps_excluded</code> export folder, baselines "
                "only. Two streams, fast and slow; four groups — ORX and OVX, gonadectomized "
                "males and females; DI, intact females in diestrus; MALE, intact males. "
                "<b>Every number in the tables below is pooled across those groups</b>; the "
                "per-group shares are in <i>Per group</i>, as FOUNDATIONS §9 requires. ⚠ Four "
                "recordings carry a known motion-correction contaminant — 12 ROIs pinned to "
                "the frame floor, flagged in no column — and are included here unflagged per "
                "recording; the producer's caveat and the open question are in "
                "<code>docs/todo/2026-09-10-four-recordings-carry-an-unflagged-contaminant.md"
                "</code>.</p>")
    y = yardstick_reach(R)
    kc = ", ".join(f"{cells_n(n)} at {draws_n(k)}" for k, n in y["K_counts"].items()) or "—"
    hist = []
    if first.get("run_folder"):
        hist.append("started on the Mac on the morning of 2026-09-11 (its own notes record the "
                    "claim checked at 07:25 EDT, a restart at about 07:37 with a larger budget, "
                    "and a resume at 08:12 after the first agent's network dropped)")
    if resumed:
        fin = (m.get("finished") or "")[11:16]
        hist.append("finished on the Windows workstation later that day"
                    + (f", its last cell at {fin} EDT" if fin else ""))
    # The draw target was set per class of generator, and the classes are this folder's
    # own — the earlier build printed steps_excluded's budgets on the Cossart page, where
    # no joint-ISI cell ever ran (blind role 1, 2026-09-11).
    mine = {k[len(role):].strip(" ,"): v for k, v in (first.get("K_by_class") or {}).items()
            if k.startswith(role)}
    plan = "; ".join(
        f"{esc(k or 'every generator')} at {draws_n(int(mo.group(1)))}"
        for k, v in mine.items() if (mo := re.search(r"K = (\d+)", str(v))))
    budget = (f"Draws were targeted per class of generator, not once for the run — {plan} — "
              f"each cell stopping early once its generation budget was spent, so the draw "
              f"count each cell actually reached is the histogram above, not the target. "
              f"<code>meta.json</code>'s single budget is the last invocation's. ⚠ "
              f"<code>run_notes.json</code>, which carries the per-class plan, was written at "
              f"13:28 EDT and stops there: it does not cover the Windows phase that produced "
              f"this folder's finished cells, whose record is <code>_logs/065-*.log</code> and "
              f"each cell's own row in <code>cells.csv</code>." if plan else "")
    return (cite + f"<p class=dim>{m.get('n_recordings_loaded', '—')} recordings. "
            f"Draws reached: {kc}. {budget} The run {'; '.join(hist) or '—'}.</p>")


def how_to_read() -> str:
    return ("<p class=dim><b>How to read a row.</b> <i>cells run</i>: grid cells that finished, "
            "of those the grid holds. <i>checks flagged</i>: the share of (statistic, grid "
            "cell) checks over all recordings where the surrogate differs from the real "
            "recordings — outside the mouse-split band's 95th percentile, and a raw paired "
            "<i>P</i> under α = 0.05 — unadjusted, with no-op cells and cells that cannot "
            "reach α excluded. <i>what gives it away</i>: statistics flagged in at least half "
            "of the candidate's scored cells. <i>retained</i>: planted coordination still "
            "visible after the surrogate, at the smallest and largest <i>J</i>, at the largest "
            "<i>K</i> the assessor scans (Figure 5 has every <i>J</i>). <i>discriminator</i>: "
            "the per-ROI-only classifier's forced-choice accuracy, median and range over the "
            "candidate's cells, where 0.5 is chance.</p>")


def exec_summary(R: dict, by_stream: dict) -> str:
    role = R["role"]
    reasons = intractable_reasons(R)
    cells = [c for c in R["cells"] if c["cell_id"] != FREEZE[0]]
    n_cells, n_ok = len(cells), sum(c["status"] == "ok" for c in cells)
    measured = {r["name"] for st in by_stream for r in by_stream[st]
                if r["kind"] == "candidate" and r["n_ok"]}
    parts = ['<h2 id="summary">Executive summary</h2>',
             f"<p class=lede>{len(measured)} of {len(CANDIDATES)} candidates were measured on "
             f"this folder and <b>none is shortlisted</b>, by design. {n_ok} of "
             f"{cells_n(n_cells)} in the grid finished. The rest did not run: "
             + "; ".join(f"{cells_n(v)} {esc(k)}" for k, v in
                         sorted(reasons.items(), key=lambda x: -x[1])) + ".</p>",
             reach_block(R)]
    # The two facts that change how every table below reads, beside the tables rather
    # than eight sections later: a saturated destruction measure, and a tier that
    # returned nothing because its own controls failed.
    for st in by_stream:
        dr, bad = destruction_reach(R, st), sat_Js(R, st)
        sj = saturation_by_J(R, st)
        if bad:
            allJ = list((sj.get("per_J") or {}))
            whole = len(bad) == len(allJ)
            parts.append(
                f'<div class="warn"><p><b>⚠ {esc(st)}: the destruction measure is saturated at '
                + (f"every <i>J</i> in the sweep" if whole else
                   f"the {len(bad)} smallest of {len(allJ)} jitter radii "
                   f"({esc(', '.join(f'{J:g}' for J in bad))} {esc(sj['unit'])})")
                + f" on this folder's twin ({sj['n_roi']} ROIs).</b> There, more co-active ROIs "
                f"stay inside the assessor's coincidence bin than its scan reaches, so retention "
                f"cannot fall whatever a candidate does and the value describes the twin rather "
                f"than the candidate; those entries are marked †. This is a limit of the "
                f"measure, not a result: it is <b>not</b> evidence that the measure works "
                f"elsewhere, and the one control that reads zero by construction — the circular "
                f"shift, which is the assessor's own null — cannot demonstrate that either. "
                f"<i>Destruction</i> has the arithmetic.</p></div>")
        v = [r["disc_void"] for r in by_stream[st]
             if r["kind"] == "candidate" and math.isfinite(r["disc_void"])]
        if v and min(v) >= 0.99:
            parts.append(
                f'<div class="warn"><p><b>⚠ {esc(st)}: every discriminator result is void.</b> '
                f"The plan calls this tier required; its own negative control — real against "
                f"real — flagged, so the accuracies below support no claim about a "
                f"candidate.</p></div>")
        g = group_flags(R, st)
        if g["groups"]:
            parts.append(
                f"<p class=dim>Pooled across groups, as every table here is: of {g['n']} checks "
                f"on the {esc(st)} stream, {g['only_group']} flag in at least one group and not "
                f"overall, and {g['only_all']} the reverse — the per-group rates are in "
                f"<i>Per group</i> (FOUNDATIONS §9).</p>")
    y = yardstick_reach(R)
    parts.append(
        f"<p><b>The first choice this leaves the verdict rule</b> is whether a corrected test "
        f"is possible at all: at {y['m']} checks per grid cell it needs at least "
        f"{y['splits_needed']} mouse splits and {draws_n(y['K_needed'])}. That and seven more "
        f"are in <i>The choices the verdict rule faces</i>, each beside its measurement.</p>")
    parts.append(how_to_read())
    for st, rows in by_stream.items():
        body = []
        for r in rows:
            if r["kind"] != "candidate":
                continue
            J = (f"{min(r['J']):g}–{max(r['J']):g} {'s' if r['J_unit'] == 'sec' else 'frames'}"
                 if r["J"] else "none")
            marks = []
            if r["n_noop"]:
                marks.append(f"{cells_n(r['n_noop'])} no-op")
            if r["n_unreachable"]:
                marks.append(f"{cells_n(r['n_unreachable'])} at ≤ 39 draws")
            cells_txt = f"{r['n_ok']} of {cells_n(r['n_cells'])}"
            if r["n_unreachable"]:
                marks[-1] = f"{cells_n(r['n_unreachable'])} at ≤ 39 draws"
            if marks:
                cells_txt += f" <span class=dim>({', '.join(marks)})</span>"
            if not r["n_ok"]:
                gives = "not measured"
            else:
                shown = r["flagged"][:4]
                hi_neg = high_neg_stats(R, st)
                gives = ", ".join(esc(stat_label(s))
                                  + ("<sup>‡</sup>" if s in hi_neg else "")
                                  for s in shown) or "nothing in half its cells"
                if len(r["flagged"]) > len(shown):
                    gives += (f" <span class=dim>({len(shown)} of "
                              f"{len(r['flagged'])} shown)</span>")
            paired = (pct(r["paired_raw"]) if math.isfinite(r["paired_raw"])
                      else ("<i>unreachable</i> <span class=dim>(≤ 39 draws)</span>"
                            if r["n_ok"] else "—"))
            disc = rng_txt(r["disc_acc"])
            flags = []
            if r["disc_n"] and r["disc_void"]:
                flags.append(f"void {pct(r['disc_void'])}")
            if r["disc_n"] and math.isfinite(r["disc_powered"]) and r["disc_powered"] < 1:
                flags.append(f"underpowered {pct(1 - r['disc_powered'])}")
            if flags:
                disc += f" <span class=dim>{', '.join(flags)}</span>"
            # Marked per J, not per row: saturation is a property of the jitter radius,
            # and the sweep's small end can be unmeasurable while its large end is fine.
            ret = ret_span(r, saturation_by_J(R, st))
            body.append([f"<b>{esc(r['label'])}</b>", cells_txt, J, num(r["rms_disp"], 1),
                         f"{pct(r['band_q95'])} / {paired}", gives, ret, disc,
                         num(r["cost"] * 1e3, 2) if math.isfinite(r["cost"]) else "—"])
        parts.append(f"<h3>{esc(st)} stream</h3>")
        parts.append(table(
            ["candidate", "grid cells run", "<i>J</i>", "RMS move (frames)",
             "checks flagged, unadjusted: band % / paired %", "what gives it away",
             "coordination retained, smallest → largest <i>J</i>", "discriminator accuracy",
             "ms per ROI per draw"], body, f"{role} {st}: per-candidate summary"))
        if sat_Js(R, st):
            parts.append(SAT_FOOTNOTE)
        if high_neg_stats(R, st):
            parts.append(NEG_FOOTNOTE)
    return "".join(parts)


def per_group(R: dict, by_stream: dict) -> str:
    """FOUNDATIONS §9: the per-group numbers beside the pooled one."""
    if not any(group_flags(R, st)["groups"] for st in by_stream):
        return ""
    out = ['<h2 id="groups">Per group</h2>',
           "<p>FOUNDATIONS §9 admits no pooled number without the per-group numbers beside it. "
           "This is the paired flag rate computed per group, on the same unadjusted paired "
           "<i>P</i> as the pooled tables.</p>",
           "<div class=\"warn\"><p><b>⚠ §9 is met for the flag rate and for nothing else on "
           "this page.</b> The screen recorded a per-group breakdown only for the paired and "
           "band checks. Retained coordination, the discriminator, cost and RMS movement were "
           "computed pooled and have no per-group counterpart in the run's output — so for "
           "those the pooled number stands alone, which §9 does not admit. Producing them per "
           "group is a rerun, not a rebuild.</p></div>"]
    for st in by_stream:
        g = group_flags(R, st)
        if not g["groups"]:
            continue
        # The project's own order for these groups, not the alphabetical one the data
        # arrives in: the prose introduces them as ORX, OVX, DI, MALE.
        canon = [k for k in ("ORX", "OVX", "DI", "MALE") if k in g["groups"]]
        canon += [k for k in g["groups"] if k not in canon]
        head = ["scope", "share of checks flagged (paired, raw)", "checks"]
        rows = [[esc(k if k != "all" else "all (pooled)"), pct(g["share"].get(k)),
                 str(g["n_scope"].get(k, 0))] for k in ["all"] + canon]
        out.append(f"<h3>{esc(st)} stream</h3>")
        out.append(table(head, rows, f"{R['role']} {st}: per-group flag shares"))
        out.append(f"<p class=dim>Of {g['n']} checks, {g['only_group']} flag in at least one "
                   f"group and not overall, and {g['only_all']} flag overall and in no group. "
                   f"Computed on the raw paired <i>P</i>: on the Holm-adjusted <i>P</i> both "
                   f"counts are zero for the reason in the box above, which is what an earlier "
                   f"build of this page reported as agreement.</p>")
    return "".join(out)


def choices(R: dict, by_stream: dict) -> str:
    """The decisions the verdict rule faces, each beside what bears on it."""
    y = yardstick_reach(R)
    items = [("<p><b>Before any of these: whether a corrected test is possible at all.</b> At "
              f"{y['m']} checks per grid cell, a Holm-adjusted flag at α = 0.05 needs a band of "
              f"at least {y['splits_needed']} mouse splits (there are {num(y['n_splits'], 0)}) "
              f"and a paired histogram of at least {draws_n(y['K_needed'])} (the most any cell "
              f"reached is {max(y['K_counts'] or [0])}). The levers are more splits and draws, a "
              "smaller correction family — per statistic, or per scope — or no correction with "
              f"the negatives' flag rates and a {pct(y['fwer'])} per-cell false-flag rate as its "
              "price. Every rate in this report is unadjusted.</p>")]
    for st, rows in by_stream.items():
        yr = yard_rows(R, st)
        pw = power_rows(R, st)
        med = {k: _med([v[k] for v in yr]) for k in ("hb", "hp", "sb", "sp")}
        reach_pw = [p for p in pw if p["reachable"]]
        dead = sorted({p["stat"] for p in pw}
                      - {p["stat"] for p in pw if p["band"] or (p["reachable"] and p["paired"])})
        at_top = []
        for r in rows:
            if r["kind"] != "candidate" or not r.get("ret_JK"):
                continue
            d = r["ret_JK"][max(r["ret_JK"])]
            Js = sorted(j for j in d if j is not None)
            at_top.append(d[Js[-1]] if Js else d.get(None))
        at_top = [v for v in at_top if v is not None and math.isfinite(v)]
        dr = destruction_reach(R, st)
        sj, badJ = saturation_by_J(R, st), sat_Js(R, st)
        void = [r["disc_void"] for r in rows if math.isfinite(r["disc_void"])]
        g = group_flags(R, st)
        sat = ""
        if sj:
            allJ = sorted(sj["per_J"])
            sat = (f"<li><b>Whether the destruction measure can see removal on this twin, and "
                   f"at which <i>J</i>.</b> Its twin has {sj['n_roi']} ROIs, so a 50% event "
                   f"recruits about {sj['recruited']:.0f}. A dither of radius <i>J</i> leaves "
                   f"about recruited × {sj['bin']}/(2<i>J</i> + 1) of them inside the "
                   f"assessor's {sj['bin']}-frame coincidence bin, against a scan that stops at "
                   f"{sj['K_hi']} co-active ROIs — so saturation is a property of <i>J</i>, not "
                   f"of the folder. "
                   + (f"<b>Saturated at {len(badJ)} of {len(allJ)} radii "
                      f"({esc(', '.join(f'{J:g}' for J in badJ))} {esc(sj['unit'])}), where "
                      f"retention cannot fall whatever the candidate does.</b> Those entries "
                      f"are marked †. Whether the scan must grow with the ROI count is the "
                      f"rule's first decision here; so is whether a sweep may report radii it "
                      f"cannot measure."
                      if badJ else
                      "The expected count falls below the scan's top at every <i>J</i> in the "
                      "sweep, so the measure can "
                      "register removal on this twin.") + "</li>")
        items.append(
            f"<h3>{esc(st)} stream</h3><ol>"
            f"<li><b>Which yardstick decides.</b> Flag rate on things that should pass, median "
            f"over statistics: held-out real half — band {pct(med['hb'])}, paired "
            f"{pct(med['hp'])}; fresh synthetic draw — band {pct(med['sb'])}, paired "
            f"{pct(med['sp'])}. Of {len(pw)} control-and-statistic checks the band moved "
            f"{sum(p['band'] for p in pw)}; of the {len(reach_pw)} whose cell could reach α at "
            f"all, the paired histogram moved {sum(p['paired'] for p in reach_pw)}. The two are "
            f"views of one statistic, not independent methods.</li>"
            f"<li><b>What a statistic no control could move counts for.</b> Unmoved under both "
            f"yardsticks: {esc(', '.join(stat_label(s) for s in dead)) or 'none'}.</li>"
            f"<li><b>How much destruction is enough, and at which <i>J</i>.</b> At each "
            f"candidate's largest <i>J</i> and the largest <i>K</i>, coordination retained "
            f"across candidates: median {num(_med(at_top))}, lowest "
            f"{num(min(at_top, default=float('nan')))}, highest "
            f"{num(max(at_top, default=float('nan')))}. At small <i>J</i> almost every "
            f"candidate keeps it (Figure 5).</li>" + sat +
            f"<li><b>What a cell that never ran counts as.</b> See <i>Coverage and cost</i>: "
            f"most were dropped on a projection, not a measurement.</li>"
            f"<li><b>Whether a void or underpowered discriminator result counts.</b> Void "
            f"share, median across candidates: {pct(_med(void))}.</li>"
            + (f"<li><b>Pooled or per group</b> (FOUNDATIONS §9). Of {g['n']} checks, "
               f"{g['only_group']} flag in a group and not overall; {g['only_all']} the "
               f"reverse — see <i>Per group</i>.</li>" if g["groups"] else
               "<li><b>Pooled or per group</b> (FOUNDATIONS §9). This folder declares no "
               "groups, so there is nothing to reconcile here and no per-group section.</li>")
            +
            f"<li><b>Which <i>J</i> and which <i>f</i>.</b> Every grid cell is in "
            f"<code>stats.csv</code>; the per-candidate range is in the summary table.</li>"
            "</ol>")
    return ('<h2 id="choices">The choices the verdict rule faces</h2>'
            "<p>Each is a decision for the design session, not made here. Beside each is the "
            "measurement that bears on it.</p>" + "".join(items))


def detail_sections(R: dict, by_stream: dict) -> str:
    role = R["role"]
    out = ['<h2 id="power">Where each statistic had power</h2>',
           "<p>Each known-bad control is built to move one statistic. Where it does not, that "
           "statistic cannot see the defect it was meant to catch — a measurement of its power, "
           "not a failure of the run. A control cell that ran at 39 draws or fewer cannot "
           "produce a paired flag at all, so it reads <i>unreachable</i> rather than no.</p>"]
    for st in by_stream:
        rows = [[esc(NAME.get(p["control"], p["control"])), esc(stat_label(p["stat"])),
                 "yes" if p["band"] else "no",
                 ("yes" if p["paired"] else "no") if p["reachable"]
                 else f"<i>unreachable</i> <span class=dim>({draws_n(p['K'])})</span>",
                 num(p["p"], 3)] for p in power_rows(R, st)]
        out.append(f"<h3>{esc(st)} stream</h3>")
        out.append(table(["control", "statistic it must move", "band detected it",
                          "paired detected it", "paired <i>P</i> (raw)"], rows,
                         f"{role} {st}: control power"))
    out.append('<h2 id="yardsticks">The three yardsticks, side by side</h2>'
               "<p>How often each yardstick flags something that should pass. A yardstick that "
               "flags a real held-out half often is too strict to rank candidates with; one "
               "that never flags a known-bad control is too blind. A statistic whose negative "
               "rate is above α is marked where it is cited as evidence.</p>")
    for st in by_stream:
        rows = [[esc(stat_label(y["stat"])), pct(y["hb"]), pct(y["hp"]), pct(y["sb"]),
                 pct(y["sp"])] for y in yard_rows(R, st)]
        out.append(f"<h3>{esc(st)} stream</h3>")
        out.append(table(["statistic", "held-out: band", "held-out: paired",
                          "synthetic: band", "synthetic: paired"], rows,
                         f"{role} {st}: exchangeable-negative flag rates"))
    neg = {st: {"band": _med([y["sb"] for y in yard_rows(R, st)]),
                "paired": _med([y["sp"] for y in yard_rows(R, st)])} for st in by_stream}
    out.append(figure(4, "Checks flagged per candidate, two yardsticks",
                      fig_flags(by_stream, role, neg),
                      "For each candidate and control, the share of its (statistic, grid cell) "
                      "checks flagged without adjustment: outside the mouse-split band's 95th "
                      "percentile (upper, open) and a raw paired <i>P</i> under 0.05 (lower, "
                      "filled). The dashed lines are what each yardstick flags on a fresh "
                      "synthetic draw that should pass. The do-nothing control must read zero "
                      "under both — it is bit-identical to its input, so it tests the plumbing, "
                      "not the yardsticks."))
    out.append('<h2 id="destruction">Destruction</h2>')
    dr_lines = []
    for st in by_stream:
        sj = saturation_by_J(R, st)
        if not sj:
            continue
        per = sj["per_J"]
        rows_sat = [[f"{J:g} {esc(sj['unit'])}", f"{per[J]:.1f}",
                     "yes — not measurable" if sj["saturated"][J] else "no"]
                    for J in sorted(per)]
        if any(sj["saturated"].values()):
            dr_lines.append(
                f"<div class=\"warn\"><p><b>⚠ {esc(st)}: the measure is saturated at the "
                f"smaller jitter radii.</b> The twin has {sj['n_roi']} ROIs, so a 50% event "
                f"recruits about {sj['recruited']:.0f}. A dither of radius <i>J</i> spreads each "
                f"onset over 2<i>J</i> + 1 frames, leaving about "
                f"recruited × {sj['bin']}/(2<i>J</i> + 1) inside the assessor's "
                f"{sj['bin']}-frame coincidence bin — and the assessor's scan stops at "
                f"{sj['K_hi']} co-active ROIs. Wherever the first exceeds the second, every "
                f"planted event trips the threshold regardless of the candidate.</p></div>")
        dr_lines.append(table([f"<i>J</i>", "co-active ROIs expected still in the bin",
                               "saturated?"], rows_sat, f"{role} {st}: saturation by J"))
    out.append("".join(dr_lines))
    out.append("<p>Destruction climbs with <i>J</i> and with <i>K</i> wherever the measure can "
               "register removal at all; each panel below should be read against its own "
               "numbers rather than the caption's.</p>")
    sat_bits = []
    for st in by_stream:
        sj, bad = saturation_by_J(R, st), sat_Js(R, st)
        if bad:
            sat_bits.append(f"{esc(st)} at {esc(', '.join(f'{J:g}' for J in bad))} "
                            f"{esc(sj['unit'])}")
    sat_note = (" ⚠ Not every <i>J</i> drawn here is measurable: at the smallest radii more "
                "co-active ROIs stay inside the coincidence bin than the assessor's scan "
                "reaches, so those columns report the twin's ROI count rather than the "
                "candidate (" + "; ".join(sat_bits) + "). Read them as unmeasured."
                if sat_bits else "")
    out.append(figure(5, "Planted coordination retained, by J and K",
                      fig_destruction(by_stream, role),
                      "The share of coordination planted in a synthetic twin (50% "
                      "participation) still visible after each candidate, for every jitter "
                      "radius <i>J</i>, at the smallest and the largest <i>K</i> — here the "
                      "number of ROIs the assessor requires active together, not the draw "
                      "count. Each square is the median over that candidate's grid cells at "
                      "that <i>J</i>. Do-nothing must keep it (1) and freeze-half is the graded "
                      "control, which should land between the ends. ⚠ The whole-window circular "
                      "shift reads 0 <b>by construction, not as a test</b>: it is the assessor's "
                      "own null (<code>assess.circular_shift_trains</code>, the same function "
                      "the scorer draws its surrogates from), so it would read 0 whether or not "
                      "the measure worked. Homogeneous resample, which is not the null, also "
                      "reads 0 and is the honest zero-reader here." + sat_note)
               + (SAT_FOOTNOTE if sat_note else ""))
    rows20 = []
    for st in by_stream:
        for r in by_stream[st]:
            if not r["ret20"]:
                continue
            Ks = sorted(r["ret20"])
            rows20.append([esc(st), esc(r["label"]),
                           f"{num(r['ret20'][Ks[0]])} <span class=dim>({Ks[0]})</span>",
                           f"{num(r['ret20'][Ks[-1]])} <span class=dim>({Ks[-1]})</span>"])
    if rows20:
        # The top of this arm is NOT the top of the 50% arm wherever the assessor found
        # no excess to keep at the higher floor, and the two pages differ: naming the
        # floor in each cell is the only way the columns can be compared (blind role 1).
        out.append("<p>The 20% participation arm, which the plan asked for beside the 50% one: "
                   "median retained across each candidate's grid cells, with the coactivity "
                   "floor it was measured at in brackets.</p>")
        out.append(table(["stream", "candidate",
                          "retained at the lowest floor (co-active ROIs)",
                          "at the highest floor it could be measured at"], rows20,
                         f"{role}: 20% participation"))
        out.append(destruction_status_note(R))
    out.append('<h2 id="discriminator">The per-ROI-only discriminator</h2>')
    voidshare = _med([r["disc_void"] for st in by_stream for r in by_stream[st]
                      if math.isfinite(r["disc_void"])])
    lead = ""
    if math.isfinite(voidshare) and voidshare >= 0.99:
        lead = ("<div class=\"warn\"><p><b>⚠ Every discriminator result on this folder is "
                "void:</b> its negative control — real against real — flagged, so the "
                "accuracies below are shown for completeness and support no claim about a "
                "candidate.</p></div>")
    out.append(lead + "<p>A logistic model on per-ROI features pooled by symmetric statistics — "
               "no operation touches a second ROI until each has been reduced over time — "
               "scored as a forced choice between each real window and its own surrogate, folds "
               "grouped by mouse. It is a classifier two-sample test (Friedman 2003; Lopez-Paz "
               "&amp; Oquab 2017). Uniform dither is its positive control and real against real "
               "its negative; if either fails, the results are void. ⚠ It ran earlier in the "
               "day than the final grid, so a row can exist for a grid cell the screen finally "
               "recorded as never run.</p>")
    rows = []
    for r in R["disc"]:
        if r["status"] != "ok" or r.get("kind") != "candidate":
            continue
        rows.append([esc(r["stream"]), esc(cell_label(r["cell_id"])),
                     num(_f(r["accuracy"]), 3), num(_f(r["p_value"]), 3),
                     "yes" if _tri(r["void"]) else "no",
                     "yes" if _tri(r.get("powered")) else "no"])
    out.append(table(["stream", "grid cell", "accuracy", "<i>P</i>", "void", "powered"],
                     rows[:40], f"{role}: discriminator"))
    if len(rows) > 40:
        out.append(f"<p class=dim>First 40 of {len(rows)} rows; all are in "
                   f"<code>discriminator/{esc(role)}/discriminator.csv</code>, with the void "
                   f"reason and the mice each cell would need.</p>")
    out.append('<h2 id="coverage">Coverage and cost</h2>')
    rows = [[esc(k), cells_n(v)] for k, v in sorted(intractable_reasons(R).items(),
                                                    key=lambda x: -x[1])]
    out.append(table(["why a grid cell did not finish", "grid cells"], rows,
                     f"{role}: coverage"))
    err = [c for c in R["cells"] if c["status"] == "error"]
    if R["role"] == "cossart":
        out.append("<p class=dim>Two cells — shipped dither and trial shift, both at "
                   "<i>J</i> = 32 frames — failed on a Dropbox file-replacement error rather "
                   "than on anything about the surrogate, were set aside in "
                   "<code>_superseded_error_065/</code>, and were rerun to 40 draws; they are "
                   "among the finished cells above. No cell is left in an error state"
                   + (f" (<code>cells.csv</code> holds {cells_n(len(err))} errored)." if err
                      else ".") + "</p>")
    out.append("<p>Most cells that did not finish were never run: joint-ISI and ISI dither's "
               "cost was projected past the run's stop time and the cells were recorded with "
               "that projection. They are a statement about that machine and that deadline, "
               "not about the candidates; rerunning them is a choice, not a repair.</p>")
    return "".join(out)


def cell_label(cell_id: str) -> str:
    """A grid cell's id in words: `dead_time_dither__J16fr__f2` reads as a sentence."""
    parts = cell_id.split("__")
    out = [NAME.get(parts[0], parts[0].replace("_", " "))]
    for p in parts[1:]:
        m = re.fullmatch(r"J([\d.]+)(s|fr)", p)
        if m:
            out.append(f"<i>J</i> = {m.group(1)} {'s' if m.group(2) == 's' else 'frames'}")
            continue
        m = re.fullmatch(r"f(\d+)", p)
        if m:
            out.append(f"<i>f</i> = {m.group(1)} frames")
            continue
        m = re.fullmatch(r"sig([\d.]+)J", p)
        if m:
            out.append(f"σ = {m.group(1)}<i>J</i>")
            continue
        m = re.fullmatch(r"bw([\d.]+)min", p)
        if m:
            out.append(f"kernel {m.group(1)} min")
            continue
        out.append({"sqrt": "with the square root", "nosqrt": "no square root"}.get(p, p))
    return " · ".join(out)


def reproduction_section(run: Path) -> str:
    lt = _rows(run / "reproduction" / "leak_table.csv")
    sat = _rows(run / "reproduction" / "saturation_table.csv")
    rep = _json(run / "reproduction" / "reproduction.json") or {}
    if not lt:
        return ""
    rows = [[esc(r["stream"]), esc(r["J"]), esc(r["policy"]), esc(r["time_base"]),
             esc(r["n_windows"]), pct(_f(r["real_share"])),
             f"{pct(_f(r['dithered_share_mean']))} ± {pct(_f(r['dithered_share_sd']))}",
             num(_f(r["auc_mean"]), 3)] for r in lt]
    rows2 = [[esc(r["stream"]), esc(r["J"]), esc(r["policy"]), esc(r["time_base"]),
              pct(_f(r["real"])), pct(_f(r["one_dither"])), pct(_f(r["two_dithers"]))]
             for r in sat]
    gaps = [_f(r["two_dithers"]) - _f(r["one_dither"]) for r in sat]
    gaps = [g for g in gaps if math.isfinite(g)]
    above = sum(g > 0 for g in gaps)
    verdict = (f"twice-dithered is higher than once-dithered in {above} of {len(gaps)} rows, by "
               f"{100 * min(gaps):.1f} to {100 * max(gaps):.1f} percentage points"
               if gaps else "—")
    return ('<h2 id="reproduction">The reproduction</h2>'
            f"<p>The earlier review's leak table, rebuilt on the <b>baselines</b> — the "
            f"untreated stretch the producer declares in each recording — of the "
            f"{rep.get('n_recordings', '—')} recordings whose first treatment was "
            f"<b>senktide</b>, a neurokinin-3 agonist, which is the subset that review used. "
            f"{rep.get('rows', [{}])[0].get('n_windows', '—')} windows of 60 seconds, under "
            f"all three <b>edge policies</b> — what a dither does with an onset pushed past a "
            f"window's end: <b>wrap</b> it round to the start, <b>drop</b> it, or <b>clamp</b> "
            f"it to the edge. The <b>sub-floor rate</b> is the share of intervals shorter than "
            f"the floor — the leak itself; it is 0% for the real recordings by construction, "
            f"since the floor is the minimum of those same windows. ± is the standard "
            f"deviation over draws. <b>The AUC column is not independent of the one beside "
            f"it</b>: with the real rate identically 0, AUC = 0.5 × (1 + the dithered share) "
            f"exactly — it is kept because the earlier review reported it, and it is reported "
            f"here as the same number in other units.</p>"
            + table(["stream", "<i>J</i> (s)", "edge policy", "time base", "windows",
                     "real sub-floor", "after UD", "AUC"], rows, "reproduction: leak table")
            + f"<p>The saturation table, remeasured under the leak table's conditions (its "
              f"original conditions were never recorded). The earlier review's safeguard "
              f"compared a once-dithered recording against a twice-dithered one and read the "
              f"comparison as flat; measured here, {verdict} — small beside the gap from real "
              f"(0%) to once-dithered, which is why the safeguard could not separate them, but "
              f"not flat.</p>"
            + table(["stream", "<i>J</i> (s)", "edge policy", "time base", "real",
                     "one dither", "two dithers"], rows2, "reproduction: saturation table"))


SOURCES = """
<h2 id="sources">Sources</h2>
<ul>
<li><b>Circular shift</b> (the assessor's null, and a candidate here) — Cossart, Aronov &amp;
Yuste 2003, <i>Nature</i> 423:283–288, doi:10.1038/nature01614, from Yuste's laboratory at
Columbia, which credits Mao, Hamzei-Sichani, Aronov, Froemke &amp; Yuste 2001, <i>Neuron</i>
32:883–898 ⚠ (not obtained here). Modern per-ROI form: Dard et al. 2022.</li>
<li><b>Uniform dither and its lineage</b> — Gerstein 2004, <i>Acta Neurobiologiae
Experimentalis</i> 64:203–207 (joint-ISI dithering and its square root); Date, Bienenstock &amp;
Geman 1998; Abeles &amp; Gat 2001.</li>
<li><b>UDD, WIN-SHUFF and the comparison this screen follows</b> — Stella, Bouss, Palm &amp; Grün
2022, <i>eNeuro</i> 9(3):ENEURO.0505-21.2022, doi:10.1523/ENEURO.0505-21.2022.</li>
<li><b>Trial shifting</b> — Pipa, Wheeler, Singer &amp; Nikolić 2008, <i>Journal of
Computational Neuroscience</i> 25:64–88; Harrison &amp; Geman 2009, <i>Neural Computation</i>
21:1244–1258 (pattern jitter).</li>
<li><b>Operational-time dither</b> — Louis, Gerstein, Grün &amp; Diesmann 2010, <i>Frontiers in
Computational Neuroscience</i> 4:127.</li>
<li><b>Choosing a surrogate by what it keeps and destroys</b> — Louis, Borgelt &amp; Grün 2010,
in Grün &amp; Rotter (eds), <i>Analysis of Parallel Spike Trains</i>, 359–382,
doi:10.1007/978-1-4419-5675-0_17 ⚠ paywalled, not read here.</li>
<li><b>The paired rank <i>P</i></b> — Amarasingham, Harrison, Hatsopoulos &amp; Geman 2012,
<i>Journal of Neurophysiology</i> 107:517–531, doi:10.1152/jn.00518.2011; the Monte-Carlo rank
test's root is Dwass 1957 and Barnard 1963.</li>
<li><b>Holm's adjustment</b> — Holm 1979, <i>Scandinavian Journal of Statistics</i>
6(2):65–70.</li>
<li><b>The discriminator</b> — Friedman 2003; Lopez-Paz &amp; Oquab 2017, <i>ICLR</i>
(classifier two-sample tests).</li>
<li><b>Seven of the twelve generators</b> come from Elephant 1.2.1, pinned (RRID:SCR_003833);
Denker, Yegenoglu &amp; Grün 2018, <i>Neuroinformatics</i>. The adapter corrects six defects
found by running it; they are listed in
<code>docs/todo/2026-09-11-elephant-surrogate-defects-are-not-filed-upstream.md</code>.</li>
<li><b>The Cossart folder</b> — DANDI:000219 (Dard, Picardo &amp; Cossart), CC-BY-4.0, ⚠ version
not recorded in this export; Dard, Chen, Picardo et al. 2022, <i>eLife</i> 11:e78116,
doi:10.7554/eLife.78116. The same group's protocol paper on these recordings, Ratsifandrihamanana
et al. 2023, <i>STAR Protocols</i> 4:102760, was not consulted.</li>
</ul>
"""


def residuals(R: dict | None) -> str:
    """What this report does not establish — the flags a reader must carry out of it."""
    return """
<h2 id="residual">What this report does not establish</h2>
<p>The measurements above were reviewed by this project's eleven-role murderboard on
2026-09-11. These are the flags that review left open; none is resolved by anything on this
page.</p>
<ul class="resid">
<li><b>Joint-ISI and ISI dither did not run as the published method.</b> The joint-ISI
histogram was binned at half the jitter radius, so the dithered interval can take only five
values and displacements are multiples of <i>J</i>/2; Stella et al. use a bin 25 times finer.
Their cells are a lattice variant, not JISI-D as published.</li>
<li><b>Half the joint-ISI cells are duplicates.</b> Gerstein's square root cannot bind at these
onset counts — every occupied histogram cell holds exactly one — so the on/off sweep produced
bit-identical output, at the most expensive cells in the grid.</li>
<li><b>"Stella's setting" is not Stella's</b> in three of four parameters: this screen smooths,
cuts off and applies a dead time where their runs do none of the three.</li>
<li><b>The destruction measure's coincidence window, planted jitter, participation levels and
ROI-count scan are declared, not justified</b>, and the scan is the constant that decides the
headline destruction result on a large-ROI twin.</li>
<li><b>Four <code>steps_excluded</code> recordings carry a motion-correction contaminant</b> —
12 ROIs pinned to the frame floor, flagged in no column — and are included unflagged per
recording.</li>
<li><b>The literature was searched in three fields and not in two</b>: the physics and
nonlinear-time-series surrogate literature, and the selection-bias literature behind the
assessor's selection-corrected excess, were not searched. Nobody has asked the Cossart lab or
Grün's group anything; correspondence would be the cheapest check available.</li>
<li><b>Gerstein 2004 was read through a later restatement</b> for part of this report's
description of his recipe; the PDF did not parse.</li>
<li><b>The renders were checked in one theme.</b> The page is light-only, so the render gate's
three theme passes are one image three times.</li>
</ul>
<p class=dim>This review found and fixed defects in this report. It is not a correctness proof:
a review measures how quickly its reviewers stopped finding things, not whether anything
remains.</p>
"""


def provenance_block(run: Path) -> str:
    ver = provenance.code_version() or "unknown"
    dirty = provenance.git_dirty()
    note = ("" if dirty is False else
            " <b>The tree had uncommitted changes when this was built</b>, so the commit above "
            "names a tree that exists nowhere else." if dirty else
            " Whether the tree was clean could not be checked.")
    return (f'<h2 id="provenance">Provenance</h2><p class=dim>Built '
            f"{time.strftime('%Y-%m-%d %H:%M %z')} by <code>tools/build_surrogate_report.py"
            f"</code> at <code>{esc(ver)}</code>.{note} Source data: the run folder "
            f"<code>&lt;darkroom&gt;/bugarach/{esc(run.name)}/</code>. Planned in "
            f"<code>docs/proposals/2026-09-10-surrogate-evaluation-overnight.md</code>; "
            f"reviewed by <code>docs/doc_review_process.md</code>'s eleven roles.</p>")


def role_page(run: Path, R: dict) -> str:
    by_stream = {st: candidate_rows(R, st) for st in streams_of(R)}
    title = {"steps_excluded": "The surrogate screen — steps_excluded",
             "cossart": "The surrogate screen — the Cossart folder"}.get(
        R["role"], f"The surrogate screen — {R['role']}")
    f_sweep = ("swept at 1 and 2 frames on this folder, whose floor is 2 frames"
               if R["role"] == "cossart" else
               "swept at 0.5, 0.75 and 1 × the observed floor — the shortest within-ROI "
               "interval in the folder's baselines — in whole frames")
    body = (f"<h1>{esc(title)}</h1>"
            "<p class=dim>Measured, not decided. A companion to the "
            "<a href=\"report_summary.html\">cross-folder summary</a>.</p>"
            + PROBLEM + fig1_block(R)
            + terms_table(R["role"], f_sweep)
            + exec_summary(R, by_stream) + _role_intro(R) + synthetic_figures(R, (2, 3))
            + detail_sections(R, by_stream) + per_group(R, by_stream)
            + (reproduction_section(run) if R["role"] == "steps_excluded" else "")
            + choices(R, by_stream) + residuals(R) + SOURCES + provenance_block(run))
    return page(title, body)


def summary_page(run: Path, roles: dict) -> str:
    cols = list(roles)
    per = {role: {st: {r["name"]: r for r in candidate_rows(R, st)}
                  for st in streams_of(R)} for role, R in roles.items()}
    heads = [f"{role} · {st}" for role in cols for st in per[role]]
    sat = {(role, st): saturation_by_J(R, st) for role, R in roles.items()
           for st in streams_of(R)}
    rows = []
    for name, label in CANDIDATES:
        row = [f"<b>{esc(label)}</b>"]
        for role in cols:
            for st in per[role]:
                r = per[role][st].get(name)
                if not r or not r["n_ok"]:
                    row.append("not measured")
                    continue
                paired = (pct(r["paired_raw"]) if math.isfinite(r["paired_raw"])
                          else "<i>unreachable</i>")
                ret = ret_span(r, sat.get((role, st)))
                acc = rng_txt(r["disc_acc"])
                # A void column has no estimate to compare: the tier's own negative
                # control flagged, so printing the number invites a comparison the
                # discriminator cannot support (blind role 4, 2026-09-11).
                if r["disc_n"] and math.isfinite(r["disc_void"]) and r["disc_void"] >= 0.99:
                    acc = "<i>void</i>"
                elif r["disc_n"] and r["disc_void"]:
                    acc += f" <span class=dim>void {pct(r['disc_void'])}</span>"
                row.append(f"flags {pct(r['band_q95'])} / {paired}<br>retained {ret}<br>"
                           f"accuracy {acc}")
        rows.append(row)
    # "Measured on two folders" is true of the screen, not of every candidate: three of
    # them finished no cell on Cossart (blind role 1, 2026-09-11).
    # The cross-folder table marks saturated radii the same way the folder pages do, so
    # this page has to carry the legend and say which folders it applies to — otherwise
    # the dagger is unexplained here and the saturation caveat exists only elsewhere.
    sat_where = [f"{esc(role)} · {esc(st)} at "
                 + esc(", ".join(f"{J:g}" for J, bad in
                                 ((sat[(role, st)].get("saturated") or {}).items()) if bad))
                 + f" {esc(sat[(role, st)].get('unit', ''))}"
                 for (role, st) in sat
                 if any((sat[(role, st)].get("saturated") or {}).values())]
    named = dict(CANDIDATES)
    meas = [{n for st in per[role] for n, r in per[role][st].items()
             if n in named and r["n_ok"]} for role in cols]
    n_both = len(set.intersection(*meas)) if meas else 0
    folders = []
    for role, R in roles.items():
        m = R["meta"]
        st0 = streams_of(R)[0]
        tw = ((m.get("streams") or {}).get(st0) or {}).get("destruction_twins") or {}
        n_stat = len([c for c in R["cells"] if c["cell_id"] != FREEZE[0]])
        folders.append([esc(role), f"{cells_n(n_stat)} carrying statistics",
                        f"{m.get('n_recordings_loaded', '—')} recordings",
                        ", ".join(streams_of(R)),
                        f"{tw.get('n_roi', '—')} ROIs in the destruction twin",
                        f"{m.get('settings', {}).get('destruction_draws', '—')} destruction "
                        f"draws, {m.get('settings', {}).get('destruction_assess_surrogates', '—')}"
                        f" assessor surrogates"])
    body = ("<h1>The surrogate screen — across folders</h1>"
            "<p class=dim>Measured, not decided. <b>Start here</b>: the two per-folder pages "
            "carry the detail, the power of each measurement, and the choices each folder "
            "leaves open.</p>" + PROBLEM + fig1_block(None) + SUMMARY_TERMS
            + '<h2 id="folders">The two folders</h2>'
            + "<p>They differ in almost everything: preparation (acute slices against in vivo "
              "pups), event extraction, frame interval, ROI count — and in how much compute "
              "each measurement got. Any difference in the table below is confounded with all "
              "of that.</p>"
            + table(["folder", "grid", "recordings", "streams", "destruction twin",
                     "destruction settings"], folders, "the two folders")
            + "<p class=dim>⚠ The destruction settings are read from <code>meta.json</code>'s "
              "settings block, which each folder page warns is the last invocation's rather "
              "than what most cells ran under. <code>run_notes.json</code> independently "
              "records the same two destruction settings, which is why they are quoted here; "
              "the draw counts in that same block are not, and are not reproduced.</p>"
            + '<h2 id="summary">Executive summary</h2>'
            + f"<p class=lede>{len(CANDIDATES)} candidates, measured on two folders — "
              f"{n_both} of them on both. <b>No shortlist is drawn.</b> Whether the right "
              f"surrogate differs between datasets is a hypothesis this comparison <b>bears on "
              f"but cannot settle</b>: the two folders differ in preparation, extraction, frame "
              f"interval, ROI count and in how much compute each measurement got, so no "
              f"difference below is attributable to the dataset alone.</p>"
            + "".join(reach_block(R, named=True) for R in roles.values())
            + table(["candidate"] + heads, rows, "cross-folder comparison")
            + "<p class=dim><b>The circular shift's retained 0.00 is not a result.</b> It is "
              "the assessor's own null — the scorer draws every one of its surrogates from "
              "<code>assess.circular_shift_trains</code> — so that row reads 0 whether or not "
              "the measure works, on both folders. Homogeneous resample reads 0 without being "
              "the null, and is the comparison worth making.</p>"
            + (f"<div class=\"warn\"><p><b>⚠ Where the destruction measure is saturated, "
               f"retention cannot fall and the number describes the twin, not the "
               f"candidate.</b> That is the case for {esc('; '.join(sat_where))} — those "
               f"entries are marked †, and the retained column is not comparable across "
               f"folders there.</p></div>" + SAT_FOOTNOTE if sat_where else "")
            + "<p class=dim>Each cell: checks flagged without adjustment — outside the band's "
              "95th percentile / a raw paired <i>P</i> under 0.05, with cells that cannot reach "
              "α excluded and marked <i>unreachable</i>; planted coordination retained at 50% "
              "participation, smallest → largest <i>J</i>, at the largest <i>K</i> the assessor "
              "scans, marked <i>saturated</i> where the measure cannot register removal on that "
              "folder's twin; the per-ROI-only discriminator's accuracy (0.5 is chance) with "
              "its void share. Destruction was measured at different draw counts on the two "
              "folders — see the table above — so the retained columns are not measured "
              "alike.</p>"
            + '<h2 id="pages">The per-folder reports</h2><ul>'
            + "".join(f'<li><a href="report_{esc(r)}.html">{esc(r)}</a> — the measurements, '
                      f"their power, the per-group numbers where the folder has groups, and "
                      f"the choices that folder leaves the verdict rule</li>" for r in cols)
            + "</ul>"
            + residuals(None) + SOURCES + provenance_block(run))
    return page("The surrogate screen — across folders", body)


# ---- the gate -----------------------------------------------------------------

def refuse_without_svg(name: str, text: str) -> None:
    if "<svg" not in text:
        raise SystemExit(f"{name}: no SVG on the page — refused. The render gate would "
                         f"pass it, and a report whose figures failed to draw would read "
                         f"as a report with nothing to show.")


# The rendered-type floor the gate enforces. Matches render_check.py's own
# MIN_RENDERED_PX (11.0) — kept here because the caller, not the tool, is what fails.
GATE_MIN_PX = 11.0


def run_gate(run: Path, pages: list[Path]) -> dict:
    tools = run / "tools"
    rc_tool, ec_tool = tools / "render_check.py", tools / "edge_collisions.py"
    missing = [p.name for p in (rc_tool, ec_tool) if not p.is_file()]
    if missing:
        raise SystemExit(f"render gate: missing stamped copies in {tools}: "
                         f"{', '.join(missing)}. Copy them there (stamped) or pass "
                         f"--no-gate — the gate never passes by default.")
    record = {"pages": {}, "min_rendered_px": GATE_MIN_PX}
    svgdir = tools / "svg"
    svgdir.mkdir(parents=True, exist_ok=True)
    # Derived artifacts from an earlier build are evidence for a page that no longer
    # exists: a reviewer read a three-build-old screenshot as current and reported its
    # numbers against the live page (blind role 10 / role 4, 2026-09-11).
    for old in svgdir.glob("*.svg"):
        old.unlink()
    failures = []
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
        # render_check --json returns 0 before it counts anything, so its exit code is
        # not a verdict: on the 18:45 build it exited 0 while its own JSON held 104
        # sub-11px labels, 5 overlaps and 2 viewBox escapes (blind role 10, 2026-09-11).
        # The caller counts, and the caller fails.
        views = (rc_json or {}).get("views") or []
        counts = {
            "small": sum(1 for v in views for t in (v.get("texts") or [])
                         if _f(t.get("renderedPx")) < GATE_MIN_PX),
            "overlaps": sum(len(v.get("overlaps") or []) for v in views),
            "escapes": sum(len(v.get("escapes") or []) for v in views),
        }
        if rc_json is None:
            failures.append(f"{pg.name}: render_check produced no JSON to check")
        elif any(counts.values()):
            failures.append(f"{pg.name}: " + ", ".join(f"{v} {k}" for k, v in counts.items()
                                                       if v))
        record["pages"][pg.name] = {
            "counts": counts, "views_measured": len(views),
            "exit_code_note": ("render_check --json always exits 0; the verdict here is the "
                               "counts above, computed by the caller"),
            "render_check_exit": r.returncode, "render_check": rc_json,
            "render_check_tail": r.stdout[-1500:] if rc_json is None else None,
            "screenshots": str(shots),
            "edge_collisions_exit": e.returncode, "edge_collisions_out": e.stdout[-1500:],
            "edge_collisions_note": (
                f"{n_edges} draughtsman edges on this page: "
                + ("the check parsed no edges and no boxes, so its pass means nothing here."
                   if n_edges == 0 else "checked.")),
            "themes_note": ("the page is light-only, so render_check's three theme passes "
                            "produce one image three times"),
        }
    record["failures"] = failures
    (tools / "gate.json").write_text(json.dumps(record, indent=1), encoding="utf-8")
    if failures:
        raise SystemExit("render gate FAILED — " + "; ".join(failures)
                         + f"\n(floor {GATE_MIN_PX:g}px; details in {tools / 'gate.json'})")
    return record


def shoot_figures(run: Path, pages: list[Path]) -> list[Path]:
    """One PNG per figure, from the page as just built.

    The murderboard found the previous set of these ten minutes older than the build and
    materially different — and reviewed them as evidence. Rendering them with the build
    is what stops that.
    """
    try:
        from playwright.sync_api import sync_playwright
    except ImportError:
        return []
    out_dir = run / "tools" / "screens" / "figures"
    out_dir.mkdir(parents=True, exist_ok=True)
    for old in out_dir.glob("*.png"):        # never leave a previous build's evidence
        old.unlink()
    written = []
    with sync_playwright() as p:
        try:
            browser = p.chromium.launch()
        except Exception:                                        # noqa: BLE001
            return []
        pg = browser.new_page(viewport={"width": 1100, "height": 900})
        for path in pages:
            pg.goto(path.resolve().as_uri())
            for i, fig in enumerate(pg.query_selector_all("figure"), 1):
                target = out_dir / f"{path.stem}_figure{i}.png"
                fig.screenshot(path=str(target))
                written.append(target)
        browser.close()
    return written


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
        from bugarach.paths import darkroom, unresolved_message
        root = darkroom()
        if root is None:
            print(unresolved_message("--run DIR"), file=sys.stderr)
            return 1
        run = Path(root) / OUT_DIRNAME
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
    shots = shoot_figures(run, written)
    if shots:
        print(f"re-rendered {len(shots)} figure screenshots beside the build")
    if not args.no_gate:
        rec = run_gate(run, written)
        for name, r in rec["pages"].items():
            print(f"gate {name}: render_check exit {r['render_check_exit']}; "
                  f"edge_collisions exit {r['edge_collisions_exit']} — "
                  f"{r['edge_collisions_note']}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
