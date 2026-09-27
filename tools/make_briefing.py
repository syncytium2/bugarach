#!/usr/bin/env python3
"""One page that briefs a night's run from the top down: leaderboard, examples, rasters.

    python tools/make_briefing.py [--night <darkroom night folder>] [--out <folder>] \
        [--also docs/learned/runs/<name>] [--viewer <viewer.html>] [--no-examples]

Tony, 2026-09-26: *"I need an html I can click on and get a full briefing. Top down performance
leader board first then examples. In this case I need to see the new bench vs the old bench for
comparison. Then I need easy access to the zoomable rasters with detection."*

**What it reads**, all under ``--night`` (default ``<darkroom>/2026-09-26-full-panel``), exactly as
the worker sessions wrote it:

* ``065/fresh-realistic/candidates.json`` — the fresh-seed scoring on the **new bench** (ADR-0010's
  realistic spacing), and ``065/fresh-bench/candidates.json`` — the same candidates on the **old
  bench** (the spacing before ADR-0010). Either may be missing; its column then says so.
* the files in :data:`EXTRA_GLOBS` — later runs in the scorer's schema (the count rule WSMIP064
  built, on each bench). A later file adds only the detectors the night's own files lack, on the
  bench its ``spacing`` names, so its CoactDetect rows never replace the night's.
* the ORX-spaced scorings (ADR-0010 ruling 1), night's and later runs' alike, for a rank-agreement
  line.
* ``065/review/detect/calls.csv``, ``windows.csv`` and ``results.json`` —
  ``tools/detect_with_floors.py``'s calls on the real recordings, the settings it ran
  (``chosen``), its participant rule and its dataset stamp.
* ``065/review/pages/*.html`` and their PNGs — the group × first treatment × stream raster pages.

**The examples read the default dataset** (``dataset.default()``), so they need the person's
confirmation for the session like every other analysis, and they refuse a detection run whose
stamp is missing or names another folder; ``--no-examples`` builds the rest without.

**What it decides: nothing.** The leaderboard orders rows by the paired F1 difference against
CoactDetect's shipped setting on the new bench, and marks what the run's own records mark. The
order is a reading of intervals, not a ranking the intervals support (``docs/performance_table.md``).

**What it writes:** ``index.html``, ``briefing.json`` (every number on the page),
``figure1_<stream>.svg``, ``example_*.png``, and ``viewer.html`` (a copy of the site's viewer, so
the recording links open locally). Its own earlier outputs in ``--out`` are removed first, so no
figure from a previous build sits beside the page. It defaults to the darkroom. ``--also`` copies
**only the simulation half** — Figure 1 and ``leaderboard.json`` — because the page names real
recordings, and nothing derived from real recordings goes into the repo (FOUNDATIONS §5).
"""
from __future__ import annotations

import argparse
import csv
import html
import json
import math
import os
import shutil
import statistics
import sys
import tempfile
import warnings
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import quote
from zoneinfo import ZoneInfo

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / "tools"))
sys.path.insert(0, str(REPO / "src"))

from bugarach.detectors import display_name  # noqa: E402
from bugarach.groups import group_key, in_group_order  # noqa: E402
from bugarach.score import TOL_SEC  # noqa: E402
from bugarach.time_axis import label as time_label  # noqa: E402

NIGHT_NAME = "2026-09-26-full-panel"
STREAMS = ("fast", "slow", "combined")
#: The six coded detectors in the glossary's order. The count rule is coded too, but it did not
#: run on the real recordings, so it is found through the scorer's own detector list instead.
CODED = ("coact", "loco", "sce", "rate", "sync", "cicada")
#: The two benches the page sets side by side, and the scorer's ``spacing`` value for each.
BENCH_COLS = (("new", "realistic", "065/fresh-realistic/candidates.json"),
              ("old", "bench", "065/fresh-bench/candidates.json"))
EXTRA_GLOBS = ("064/count/**/candidates.json", "065/fresh-bench-count/candidates.json")
ORX_FILES = ("065/fresh-orx/candidates.json", "064/count/fresh-orx/candidates.json")
CALLS = "065/review/detect/calls.csv"
WINDOWS = "065/review/detect/windows.csv"
RESULTS = "065/review/detect/results.json"
PAGES = "065/review/pages"
VIEWER_TAB = "bugarach-viewer"
#: The streams the viewer can open. It builds its streams from the export folder's own, and the
#: combined stream is derived in Python (``bugarach.combined``), never stored, so a combined link
#: would land on the viewer's "no such stream" error. Combined calls are on the review pages.
VIEWER_STREAMS = ("fast", "slow")
HOUSE_TZ = ZoneInfo("America/New_York")      # the house clock for Tony
#: The half-width of an example's window, in seconds, per stream: slow and combined calls last
#: seconds, fast ones a fraction of one. The window is cut at the baseline window's edges.
EXAMPLE_HALF_SEC = {"fast": 45.0, "slow": 120.0, "combined": 120.0}
#: An example call is taken at least this far inside its baseline window, in seconds, so the
#: figure shows the call and not an edge of the analysed time (every call is still counted).
EDGE_SEC = 10.0
#: Two spans "within the tolerance" compare with this much slack, in seconds: the scorer's test is
#: inclusive (``score.py``, ``<= tol_sec``), and a gap of exactly 2.5 s otherwise lands on either
#: side by floating-point error (murderboard 2026-09-26 round 3, roles 1, 4 and 6).
EPS_SEC = 1e-6
#: A disagreement example is drawn from calls at least this many tolerances from the other
#: detector's nearest call, so the figure shows a call the other did not make, not a timing split.
CLEAR_TOLS = 2.0
#: The noise unit ADR-0010 part 1 uses for its focus rule (the draw-to-draw spread measured in the
#: fair comparison). This page borrows it to say which rows it treats as level.
NOISE_UNIT = 0.01
#: What each detector is, in a line (the name is printed before it). The coded lines follow
#: docs/GLOSSARY.md (axis 2); the learned lines follow each model's registry note. Bases come
#: before the variants built on them.
WHAT_ORDER = ("coact", "loco", "sce", "rate", "sync", "cicada", "count", "count_sliding",
              "chorus_norm", "line", "chorus_gain_norm", "tube")
WHAT = {
    "coact": "counts distinct cells with an onset in a short bin and tests the count against a "
             "rolling null made by circularly shifting each cell's events in time (coded)",
    "loco": "counts distinct co-active cells and compares the count with a rolling percentile "
            "threshold (coded)",
    "sce": "binned SCE (synchronous calcium events): counts co-active cells per bin against a "
           "threshold from shuffled surrogates; the Yuste-lab rule of Cossart, Aronov & Yuste "
           "2003, ported from interface2's MATLAB (coded)",
    "rate": "a population-rate excess over a slower context rate (coded)",
    "sync": "the SPIKE-synchronization profile of the Kreuz lab, adaptive to each cell's "
            "inter-event intervals, with a cap on its coincidence window and a two-threshold "
            "(hysteresis) detection of our own (coded)",
    "cicada": "sliding-window coactivity against a null made by rolling each cell's events in "
              "time: the method of CICADA, the Cossart lab's software, changed only in its input "
              "(ADR-0002; coded)",
    "count": "bins the onsets and calls a bin whose count of co-active cells reaches the "
             "window's event floor plus an offset k (coded)",
    "count_sliding": "the same count over sliding windows (coded)",
    "chorus_norm": "a network that encodes each cell's trace, standardizes the encoding over time, "
                   "then pools across cells (learned)",
    "line": "a network with two sensors, how much of the field is active at once (relative "
            "length) and how concentrated in time that activity is, then a center-surround "
            "filter over that count in time (learned)",
    "chorus_gain_norm": "chorus_norm plus line's vote, with a learnable gain on that vote "
                        "(started at 8) and a learnable bias (learned)",
    "tube": "a network running a center-surround kernel on the brightness trace, with a "
            "raw-brightness bypass (learned)",
}
SETTING_NOTE = ("Each row also names its setting: <i>shipped</i> (the setting in the detector's "
                "code before this night), <i>proposal</i> (the setting the night's search found "
                "best on the new bench), <i>starting point</i> (the count rule's first, untuned "
                "setting, set on 2026-09-26), or, for a learned model, <i>pick</i> (the training "
                "run chosen by held-out F1 within CoactDetect's no-coordination budget) or "
                "<i>no pick</i> (no run met that budget; the best is shown as a comparator).")
PART_NOTE = ("A name ending in <i>_part</i> is the same network with participation added "
             "(ADR-0010 part 5 asks it of every learned model; the plain variants were trained "
             "beside them as comparators). For the chorus and line networks that is a bounded vote per cell "
             "summed into a count, the recording's event floor as an input, and a "
             "membership term in the training loss. <i>tube_part</i> has no per-cell stage, so it "
             "takes a count of cells with an onset in a 20-frame window and the floor as inputs, "
             "with no membership term.")
#: Settings not in the final-parameters report's tables, in its format.
EXTRA_PLAIN = {"k_offset": "count offset k", "bin_sec": "bin width"}
EXTRA_UNIT = {"k_offset": "cells", "bin_sec": "s"}
#: Units for the budgets (their names are the final-parameters report's, which are the glossary's).
BUDGET_UNIT = {"probe": "calls/min", "elevated_out_quiet": "calls/h", "null": "calls/h",
               "precision_swing": ""}


# --------------------------------------------------------------------------------------------
# small helpers
# --------------------------------------------------------------------------------------------

def _load(p: Path) -> dict | None:
    return json.loads(p.read_text(encoding="utf-8")) if p.exists() else None


def house_time(t: datetime) -> str:
    """A time on the house clock, one format everywhere: ``2026-09-26 8:03 PM EDT``."""
    t = t.astimezone(HOUSE_TZ)
    return f"{t:%Y-%m-%d} {int(t.strftime('%I'))}:{t:%M %p %Z}"


def when(p: Path) -> str | None:
    """A file's modification time on the house clock."""
    if not p.exists():
        return None
    return house_time(datetime.fromtimestamp(p.stat().st_mtime, tz=timezone.utc))


def n_of(n: int, one: str, many: str | None = None) -> str:
    """``1 row``, ``2 rows``: every count carries its unit, in the right number."""
    return f"{n} {one if n == 1 else (many or one + 's')}"


def _f(x, nd=3, sign=True):
    """A number to ``nd`` places. A negative value that rounds to zero keeps its sign
    ("-0.000"), so the sign agrees with the source."""
    if x is None:
        return "—"
    return f"{x:+.{nd}f}" if sign else f"{x:.{nd}f}"


def gap_words(sec: float) -> str:
    """A gap between calls: tenths of a second under a minute, minutes and seconds above."""
    return f"{sec:.1f} s" if sec < 60 else time_label(round(sec))


def _setting_value(name: str, v) -> str:
    """A setting and its value in the final-parameters report's words and units, so the two
    reports built from one night name a setting the same way. A float is shown to 6 significant
    digits (a percentile of 99.9921875 reads 99.9922)."""
    from make_final_parameters_report import PLAIN, UNIT, _vu

    if isinstance(v, float) and math.isfinite(v):
        v = float(f"{v:.6g}")
    word = PLAIN.get(name) or EXTRA_PLAIN.get(name) or name
    if name in EXTRA_UNIT and name not in UNIT:
        unit = EXTRA_UNIT[name]
        return f"{word} {v:g} {'cell' if unit == 'cells' and v == 1 else unit}"
    return f"{word} {_vu(name, v)}"


# --------------------------------------------------------------------------------------------
# budgets and limit marks
# --------------------------------------------------------------------------------------------

def budgets_of(bench_mod, det: str, row: dict) -> list[dict]:
    """The budgets a fresh-seed row fails, with value and limit — every budget in force under the
    search's admissibility rule (``search_all_settings.make_admissible``; ADR-0010 part 4 retired
    the close-events test), computed by the final-parameters report's own function so the two
    reports cannot disagree about what a failure is. A detector the bench holds budgets for is
    held to its own; a learned model is held to CoactDetect's. A value that was not measured is
    kept, as ``None``, rather than read as a pass."""
    from make_final_parameters_report import failed, fresh_budgets

    own = det in getattr(bench_mod, "MAX_FALSE_POSITIVES_PER_HOUR", {})
    b = fresh_budgets(bench_mod, det, row, det if own else "coact")
    return [dict(name=k, value=b[k]["value"], limit=b[k]["limit"]) for k in failed(b)]


def budget_words(f: dict) -> str:
    """One failed budget in words, with enough digits that the value visibly passes the limit."""
    from make_final_parameters_report import BUDGET_NAME

    what = BUDGET_NAME.get(f["name"], f["name"])
    if f["name"] == "elevated_out_quiet":
        what += " (quiet background, as the search gates it)"
    unit = BUDGET_UNIT.get(f["name"], "")
    u = f" {unit}" if unit else ""
    if f["value"] is None:
        return f"{what}: not measured (limit {f['limit']:g}{u})"
    return f"{what}: {f['value']:.3f}{u} against a limit of {f['limit']:.3f}{u}"


def limit_marks(meta: dict) -> list[str]:
    """What the search's bracketing record says about the setting it found best, in words, each
    with the rule that governs it — read whatever the best is called, because a search that
    proposes nothing still found its best at the shipped setting, and that setting can sit on a
    limit too.

    The search's own rule decides what is flagged, not this page: any unbracketed axis makes a
    candidate not adoptable (``search_all_settings.bracketing``: cap, limit or edge alike), and
    ADR-0010 part 1 requires a final setting to be bracketed. ADR-0010 ruling 5 covers a value
    that switches a setting off. Each mark says, in a clause, why the search stopped there — read
    from the ``reason`` the search recorded, never re-guessed from the value."""
    prop = meta.get("proposal") or {}
    br = prop.get("bracketing") or {}
    out, seen = [], set()
    for f in br.get("findings") or []:
        name, kind = f.get("setting"), f.get("kind")
        seen.add(name)
        if kind == "off_limit":
            out.append(f"{_setting_value(name, f.get('value'))}, a value that turns the setting "
                       f"off: the search preferring \"off\" is reported as a finding, not a tuned "
                       f"value (ADR-0010 ruling 5)")
        elif kind == "cap":
            out.append(f"{_setting_value(name, f.get('value'))}, at the search's extension cap, "
                       f"so the best value may lie beyond it (not bracketed, ADR-0010 part 1)")
    for name, v in (br.get("unbracketed_axes") or {}).items():
        if name in seen:
            continue
        side = "lower" if v.get("side") == "low" else "upper"
        val = _setting_value(name, v.get("value"))
        why = {
            "cap": "at the search's extension cap, so the best value may lie beyond it",
            "limit": f"at the {side} limit the setting can take, so the search could not test "
                     f"past it",
            "grid_floor": "the shortest context allowed (ADR-0010 ruling 7), so the search could "
                          "not test shorter",
            "grid_ceiling": "the longest context allowed (the 120 s ceiling of ADR-0009 decision "
                            "5), so the search could not test longer",
        }.get(v.get("reason"), "at the edge of the search's grid, so the best value may lie "
                               "beyond it")
        out.append(f"{val}, {why} (not bracketed, ADR-0010 part 1)")
    if prop.get("unbracketed") and not out:
        out.append("not bracketed, and the search record names no setting")
    return out


# --------------------------------------------------------------------------------------------
# the model: every number on the page, read from files
# --------------------------------------------------------------------------------------------

def _setting(det: str, which: str, bench_mod) -> str:
    """shipped / proposal, or the count rule's untuned starting point, which ships nowhere."""
    if which == "shipped":
        op = getattr(bench_mod, "OPERATING_POINTS", {}).get(det)
        if op is not None and str(getattr(op, "source", "")).startswith("not tuned"):
            return "starting point (untuned)"
    return which


def bench_rows(cand: dict, stream: str, bench_mod) -> dict:
    """``{row id: row}`` for one stream of one candidates.json: every coded setting, every learned
    pick (or the best training run of a family with none, as a comparator), and any other row."""
    res, meta = cand["results"][stream], cand["benches"][stream]
    rows = {}

    def put(rid, key, label, setting, family, flags, spread=None):
        r = res[key]
        pf = (r.get("paired_f1_vs_coact") or {})
        sh, pr = pf.get("shipped") or {}, pf.get("proposal") or {}
        q, b = r.get("baseline_quiet") or {}, r.get("baseline_busy") or {}
        rows[rid] = dict(label=label, setting=setting, family=family, key=key,
                         mid=sh.get("mid"), lo=sh.get("lo"), hi=sh.get("hi"),
                         n_seeds=sh.get("n_seeds"), n_dropped=sh.get("n_dropped"),
                         vp_mid=pr.get("mid"), vp_lo=pr.get("lo"), vp_hi=pr.get("hi"),
                         mean_f1=r.get("mean_f1"),
                         mean_f1_without_decoys=r.get("mean_f1_without_decoys"),
                         recall_quiet=q.get("recall"), recall_busy=b.get("recall"),
                         precision_quiet=q.get("precision"), precision_busy=b.get("precision"),
                         planted=(q.get("n_planted") or 0) + (b.get("n_planted") or 0),
                         decoy_calls=(q.get("decoy_calls") or 0) + (b.get("decoy_calls") or 0),
                         merged_calls=(q.get("merged_calls") or 0) + (b.get("merged_calls") or 0),
                         null_per_hour=r.get("null_calls_per_hour"),
                         budget_fails=budgets_of(bench_mod, family, r), flags=list(flags),
                         spread=spread)

    dets = list(CODED) + [d for d in meta.get("detectors", {}) if d not in CODED]
    for det in dets:
        m = meta.get("detectors", {}).get(det, {})
        best_is_shipped = (m.get("proposal") or {}).get("name") == "shipped"
        if f"{det}:shipped" in res:
            put(f"{det}:shipped", f"{det}:shipped", display_name(det),
                _setting(det, "shipped", bench_mod), det,
                limit_marks(m) if best_is_shipped else [])
        if f"{det}:proposal" in res:
            put(f"{det}:proposal", f"{det}:proposal", display_name(det), "proposal", det,
                limit_marks(m))
    for fam, c in (meta.get("chorus") or {}).items():
        means = [t.get("mean") for t in c.get("train_rows") or [] if t.get("mean") is not None]
        spread = dict(n=len(means), lo=min(means), hi=max(means)) if means else None
        pick = c.get("picked")
        if pick and f"chorus:{pick}" in res:
            put(f"learned:{fam}", f"chorus:{pick}", fam, pick.replace(".json", ""), fam, [],
                spread)
        elif c.get("out_of_budget"):
            best = c["out_of_budget"]["best"]
            if f"chorus:{best}" in res:
                put(f"learned:{fam}", f"chorus:{best}", fam, best.replace(".json", ""), fam,
                    ["no pick: no training run met the no-coordination budget; shown as a "
                     "comparator only"], spread)
    for key in res:
        kind = key.split(":", 1)[0]
        if kind not in dets and kind != "chorus":
            put(key, key, display_name(kind), key.split(":", 1)[-1], kind, [])
    return rows


def _side(v: dict | None, lo="lo", hi="hi") -> str | None:
    if not v or v.get(lo) is None:
        return None
    return "above" if v[lo] > 0 else "below" if v[hi] < 0 else "includes zero"


def _merge_extra(night: Path, col_by_spacing: dict, benches: dict, sources: dict, mods: dict,
                 files) -> list[str]:
    """Add later runs' rows to ``benches`` (keyed by bench column) for detectors the night's own
    files lack. Returns the row ids added."""
    own = {col: {r["family"] for st in benches.get(col, {}).values() for r in st.values()}
           for col in benches}
    extra = []
    for p in files:
        c = _load(p)
        if c is None:
            continue
        col = col_by_spacing.get(c.get("spacing", "bench"))
        if col is None:
            continue
        added = set()
        for s in STREAMS:
            if s in c.get("results", {}):
                for rid, row in bench_rows(c, s, mods[s]).items():
                    if row["family"] not in own.get(col, set()) and not rid.startswith("learned:"):
                        benches.setdefault(col, {}).setdefault(s, {})[rid] = row
                        extra.append(rid)
                        added.add(row["label"])
        if added and col in sources:
            sources[col]["extra"].append(dict(
                path=str(p.relative_to(night)).replace(os.sep, "/"), written=when(p),
                rows=sorted(added)))
    return extra


def build(night: Path) -> dict:
    import importlib

    from score_bench_candidates import BENCHES, BOOTSTRAP

    mods = {s: importlib.import_module(BENCHES[s]) for s in STREAMS}
    benches, sources = {}, {}
    for col, spacing, rel in BENCH_COLS:
        p = night / rel
        c = _load(p)
        if c is not None and c.get("spacing", "bench") != spacing:
            raise SystemExit(f"{p} was scored at spacing {c.get('spacing')!r}, not {spacing!r}")
        sources[col] = dict(path=rel, present=c is not None, written=when(p),
                            # seeds_by_bench holds each stream's [first, last] seed, inclusive
                            seeds={s: (lambda r: r[1] - r[0] + 1 if len(r) == 2 else None)(
                                       (c or {}).get("seeds_by_bench", {}).get(s, []))
                                   for s in STREAMS} if c else None, extra=[])
        benches[col] = {s: bench_rows(c, s, mods[s]) for s in STREAMS
                        if c and s in c["results"]} if c else {}
    extra_files = sorted({p for g in EXTRA_GLOBS for p in night.glob(g)})
    extra = _merge_extra(night, {sp: col for col, sp, _ in BENCH_COLS}, benches, sources, mods,
                         extra_files)
    board = {}
    for s in STREAMS:
        ids = list(dict.fromkeys(rid for col, _, _ in BENCH_COLS
                                 for rid in benches.get(col, {}).get(s, {})))
        entries = []
        for rid in ids:
            per = {col: benches.get(col, {}).get(s, {}).get(rid) for col, _, _ in BENCH_COLS}
            first = next(v for v in per.values() if v)
            entries.append(dict(id=rid, label=first["label"], setting=first["setting"],
                                family=first["family"], spread=first.get("spread"), per=per,
                                same_as={}))

        def order(e):
            mid = (e["per"]["new"] or {}).get("mid")
            return (0, -mid) if mid is not None else (1, 0.0)
        entries.sort(key=order)
        # TWO ROWS WITH THE SAME SCORES TO EVERY DIGIT are one result shown twice (fast LoCo's and
        # CoactDetect's proposals on the new bench, 2026-09-25 night). Said beside the row and
        # counted once — per bench, because the same two rows can differ on the other bench, and
        # there they are two results (murderboard 2026-09-26 round 3, roles 1, 3 and 6).
        for col, _, _ in BENCH_COLS:
            for i, e in enumerate(entries):
                v = e["per"][col]
                for f in entries[:i]:
                    w = f["per"][col]
                    if v and w and e["id"] != "coact:shipped" and f["id"] != "coact:shipped" and all(
                            v[k] == w[k] for k in ("mid", "lo", "hi", "mean_f1")):
                        e["same_as"][col] = f"{f['label']} · {f['setting']}"
                        break
        board[s] = entries
    model = dict(sources=sources, board=board, count_present=bool(extra), bootstrap=BOOTSTRAP,
                 extra_files=[str(p.relative_to(night)).replace(os.sep, "/") for p in extra_files])
    model["orx"] = orx_check(night, board, mods)
    return model


def spearman(a: list[float], b: list[float]) -> float | None:
    """Spearman's rank correlation (scipy's), or ``None`` for fewer than 3 pairs or a constant
    input, where it says nothing."""
    from scipy.stats import spearmanr

    if len(a) < 3:
        return None
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        r = float(spearmanr(a, b).statistic)
    return r if math.isfinite(r) else None


def orx_check(night: Path, board: dict, mods: dict) -> dict | None:
    """ADR-0010 ruling 1 asks whether the rankings hold on a bench spaced like the ORX recordings
    (on each stream). Per stream: the rank correlation of ΔF1 between the new bench and the ORX
    bench, whether the top row is the same, and how many intervals change side of zero — all
    against CoactDetect's shipped setting, on every row the page shows (later runs included)."""
    files = [night / f for f in ORX_FILES if (night / f).exists()]
    if not files:
        return None
    orx = {}
    first = _load(files[0])
    for s in STREAMS:
        if s in first.get("results", {}):
            orx[s] = bench_rows(first, s, mods[s])
    wrap = {"orx": orx}
    _merge_extra(night, {"orx": "orx"}, wrap, {}, mods, files[1:])
    out = dict(paths=[str(p.relative_to(night)).replace(os.sep, "/") for p in files], streams={})
    tot = dict(rows=0, changed_above=0, changed_below=0, crossed=0, top_moved=0)
    for s in STREAMS:
        pairs = [(e, wrap["orx"].get(s, {}).get(e["id"])) for e in board[s]
                 if e["id"] != "coact:shipped" and e["per"]["new"]
                 and not e["same_as"].get("new")]
        pairs = [(e, o) for e, o in pairs if o and o.get("mid") is not None]
        if not pairs:
            continue
        a = [e["per"]["new"]["mid"] for e, _ in pairs]
        b = [o["mid"] for _, o in pairs]
        upper = [(x, y) for x, y in zip(a, b) if x >= 0]
        top_new = max(pairs, key=lambda p: p[0]["per"]["new"]["mid"])[0]
        top_orx = max(pairs, key=lambda p: p[1]["mid"])[0]
        sides = [{_side(e["per"]["new"]), _side(o)} for e, o in pairs]
        changed_above = sum(1 for sd in sides if sd == {"above", "includes zero"})
        changed_below = sum(1 for sd in sides if sd == {"below", "includes zero"})
        crossed = sum(1 for sd in sides if sd == {"above", "below"})
        out["streams"][s] = dict(
            rows=len(pairs), rho=spearman(a, b), upper_rows=len(upper),
            rho_upper=spearman([x for x, _ in upper], [y for _, y in upper]),
            changed_above=changed_above, changed_below=changed_below, crossed=crossed,
            top_new=f"{top_new['label']} · {setting_words(top_new)}",
            top_orx=f"{top_orx['label']} · {setting_words(top_orx)}")
        tot["rows"] += len(pairs)
        tot["changed_above"] += changed_above
        tot["changed_below"] += changed_below
        tot["crossed"] += crossed
        tot["top_moved"] += top_new["id"] != top_orx["id"]
    out.update(tot)
    return out


def flagged(e: dict, col: str = "new") -> bool:
    """A row the page would not put forward: over a budget, on a search limit, or no pick."""
    v = e["per"].get(col)
    return bool(v and (v["budget_fails"] or v["flags"]))


def glance(model: dict) -> dict:
    """Per stream and bench, counted from the rows on the page — CoactDetect's shipped row left
    out, and a row with the same scores as another counted once: how many rows' intervals sit
    wholly above zero, include it, or sit wholly below, against CoactDetect's shipped setting and
    against its proposal; how many rows beat the reference's F1 without decoys; the top unflagged
    row and how many rows are level with it; and the reference's own numbers."""
    out = {}
    for s in STREAMS:
        out[s] = {}
        ref = next((e for e in model["board"][s] if e["id"] == "coact:shipped"), None)
        for col in ("new", "old"):
            rows = [e for e in model["board"][s] if e["per"][col] and e["id"] != "coact:shipped"
                    and not e["same_as"].get(col)]
            if not rows:
                continue
            sides = [_side(e["per"][col]) for e in rows]
            vp = [e for e in rows if not e["id"].startswith("coact:")]
            vp_sides = [_side(e["per"][col], "vp_lo", "vp_hi") for e in vp]
            clean = [e for e in rows if not flagged(e, col)]
            top = max(clean, key=lambda e: e["per"][col]["mid"]) if clean else None
            level = [e for e in rows if top and abs(e["per"][col]["mid"] - top["per"][col]["mid"])
                     <= NOISE_UNIT]
            rv = (ref["per"][col] or {}) if ref else {}
            out[s][col] = dict(
                n=len(rows), above=sides.count("above"), below=sides.count("below"),
                straddle=sides.count("includes zero"),
                above_clean=sum(1 for e, sd in zip(rows, sides) if sd == "above"
                                and not flagged(e, col)),
                above_learned=sum(1 for e, sd in zip(rows, sides) if sd == "above"
                                  and e["id"].startswith("learned:")),
                vp_n=len(vp), vp_above=vp_sides.count("above"),
                above_wo=sum(1 for e in rows if (e["per"][col]["mean_f1_without_decoys"] or 0)
                             > (rv.get("mean_f1_without_decoys") or 0)),
                top=f"{top['label']} · {setting_words(top)}" if top else None,
                top_mid=top["per"][col]["mid"] if top else None, level=len(level),
                ref_f1=rv.get("mean_f1"), ref_f1_wo=rv.get("mean_f1_without_decoys"),
                ref_recall=(rv.get("recall_quiet"), rv.get("recall_busy")),
                ref_decoys=rv.get("decoy_calls"), ref_planted=rv.get("planted"),
                ref_merged=rv.get("merged_calls"),
                seeds=((model["sources"].get(col) or {}).get("seeds") or {}).get(s),
                others_median_f1=statistics.median(e["per"][col]["mean_f1"] for e in rows))
    return out


def setting_words(e: dict, short: bool = False) -> str:
    """A row's setting as the page says it: shipped, proposal or starting point for a coded
    detector; for a learned model, which of its training runs was picked, counted from one.
    ``short`` is Figure 1's row label, which has to fit its column."""
    if not e["id"].startswith("learned:"):
        return ("starting point" if short and e["setting"].startswith("starting point")
                else e["setting"])
    run = int(e["setting"].rsplit("_seed", 1)[-1]) + 1
    nopick = any(f.startswith("no pick") for v in e["per"].values() if v for f in v["flags"])
    n = (e.get("spread") or {}).get("n") or 5
    if short:
        return f"{'no pick' if nopick else 'pick'}, run {run} of {n}"
    return f"{'no pick; best was' if nopick else 'pick:'} training run {run} of {n}"


def ran_on_real(entry: dict, chosen: dict) -> str | None:
    """The ``calls.csv`` detector name for a leaderboard row, if the night's detection ran exactly
    that setting — read from ``results.json``'s ``chosen`` record, not inferred: a coded detector
    whose recorded ``which`` is this row's setting, a learned family whose recorded file is this
    row's pick. ``None`` for anything the real run did not use, the count rule included."""
    fam = entry["family"]
    det = (chosen.get("detectors") or {}).get(fam)
    if det is not None:
        which = det.get("which")
        setting = "shipped" if entry["setting"].startswith("starting point") else entry["setting"]
        return fam if which == setting else None
    if entry["id"].startswith("learned:"):
        f = (chosen.get("chorus") or {}).get(fam)
        return fam if f and str(f).replace(".json", "") == entry["setting"] else None
    return None


# --------------------------------------------------------------------------------------------
# the real-data side: calls, windows, examples
# --------------------------------------------------------------------------------------------

def _num(x) -> float:
    try:
        v = float(x)
    except (TypeError, ValueError):
        return 0.0
    return v if math.isfinite(v) and v > 0 else 0.0


def read_calls(p: Path) -> list[dict]:
    """The night's calls, one variant per detector: ``own_floor`` for the four that take the floor
    as their participation minimum, ``unfloored`` for the rest — the default of
    ``make_group_raster_summary.call_lanes``, which draws the review pages, and with its stream
    normalisation."""
    with p.open(newline="", encoding="utf-8") as fh:
        rows = [r for r in csv.DictReader(fh) if r.get("variant") in ("own_floor", "unfloored")]
    for r in rows:
        r["stream"] = str(r["stream"]).strip().lower()
    return rows


def read_windows(p: Path) -> tuple[dict, dict]:
    """(bounds, hours): each baseline window's (start, end) in seconds by (slice, stream, region),
    and baseline hours per (stream, group), each window counted once."""
    bounds, hours, seen = {}, defaultdict(float), set()
    with p.open(newline="", encoding="utf-8") as fh:
        for r in csv.DictReader(fh):
            if r["window_kind"] != "baseline":
                continue
            key = (r["slice_id"], str(r["stream"]).strip().lower(), r["region_idx"])
            bounds[key] = (float(r["win_start"]), float(r["win_end"]))
            if key not in seen:
                seen.add(key)
                hours[(key[1], r["group"])] += float(r["hours"])
    return bounds, dict(hours)


def recordings(windows_csv: Path) -> list[dict]:
    """One row per recording: its group and its first treatment (the treatment window that starts
    earliest; on the 2026-09-25 night this agrees with the review pages' ``treatment_one`` on all
    66 recordings, but it is a separate copy of that rule), in the house group order."""
    rec: dict = {}
    with windows_csv.open(newline="", encoding="utf-8") as fh:
        for r in csv.DictReader(fh):
            d = rec.setdefault(r["slice_id"], dict(slice_id=r["slice_id"], group=r["group"],
                                                   first=None, t0=None, streams=set()))
            d["streams"].add(str(r["stream"]).strip().lower())
            if r["window_kind"] == "treatment":
                t0 = float(r["win_start"])
                if d["t0"] is None or t0 < d["t0"]:
                    d["t0"], d["first"] = t0, r["label"]
    out = sorted(rec.values(), key=lambda d: (group_key(d["group"]), d["first"] or "~",
                                               d["slice_id"]))
    for d in out:
        d["streams"] = [s for s in STREAMS if s in d["streams"]]
    return out


def _span(c: dict) -> tuple[float, float]:
    t0 = float(c["onset_sec"])
    return t0, t0 + _num(c.get("width_sec"))


def _gap(a: dict, b: dict) -> float:
    """Seconds between two calls' spans, 0 when they overlap (``score.py``'s gap)."""
    a0, a1 = _span(a)
    b0, b1 = _span(b)
    return max(0.0, b0 - a1, a0 - b1)


def _near(a: dict, others: list[dict], tol: float) -> list[dict]:
    return [b for b in others if _gap(a, b) <= tol + EPS_SEC]


def classify(calls: list[dict], stream: str, leader: str, ref: str) -> dict:
    """Every baseline-window call of the leader and the reference on one stream, by kind. "Both
    call it" and "only the leader" count the leader's calls; "only CoactDetect" counts the
    reference's. Two calls agree when their spans come within the bench's scoring tolerance of
    each other (span to span), so one call can agree with several: ``many`` counts the calls of
    either side that agree with two or more of the other's, which is where a merge hides."""
    by = defaultdict(lambda: defaultdict(list))
    for r in calls:
        if r["stream"] == stream and r["window_kind"] == "baseline":
            by[r["slice_id"]][r["detector"]].append(r)
    kinds = {"agree": [], "leader_only": [], "ref_only": []}
    many = dict(leader=0, ref=0)
    for sid, per in by.items():
        L, R = per.get(leader, []), per.get(ref, [])
        for c in L:
            hits = _near(c, R, TOL_SEC)
            kinds["agree" if hits else "leader_only"].append(c)
            many["leader"] += len(hits) >= 2
        for c in R:
            hits = _near(c, L, TOL_SEC)
            if not hits:
                kinds["ref_only"].append(c)
            many["ref"] += len(hits) >= 2
    kinds["_many"] = many
    return kinds


def _inside(c: dict, bounds: dict) -> bool:
    b = bounds.get((c["slice_id"], c["stream"], c["region_idx"]))
    if b is None:
        return False
    t0, t1 = _span(c)
    return t0 >= b[0] + EDGE_SEC and t1 <= b[1] - EDGE_SEC


def pick_one(pool: list[dict], bounds: dict, used: set,
             others: list[dict] | None = None) -> dict | None:
    """The call with the median participant count among the calls at least :data:`EDGE_SEC`
    inside their baseline window, preferring a recording no earlier figure has shown. For a
    disagreement (``others`` given: the other detector's calls), only calls at least
    :data:`CLEAR_TOLS` tolerances from the other's nearest call qualify when any do, so the figure
    shows a call the other did not make rather than a timing split. The page says every
    condition and prints the pool's size and gap distribution beside the figure."""
    inner = [c for c in pool if _inside(c, bounds)]
    if others is not None:
        clear = [c for c in inner if (nearest_gap(c, others) or math.inf) > CLEAR_TOLS * TOL_SEC]
        inner = clear or inner
    fresh = [c for c in inner if c["slice_id"] not in used] or inner
    if not fresh:
        return None
    fresh.sort(key=lambda c: (int(float(c["participants"] or 0)), c["slice_id"],
                              float(c["onset_sec"])))
    c = fresh[len(fresh) // 2]
    used.add(c["slice_id"])
    return c


def nearest_gap(c: dict, others: list[dict]) -> float | None:
    """Seconds between a call's span and the nearest span of another detector's calls on the same
    recording and stream (0 when they overlap)."""
    gaps = [_gap(c, b) for b in others
            if b["slice_id"] == c["slice_id"] and b["stream"] == c["stream"]]
    return min(gaps) if gaps else None


def gap_bins(pool: list[dict], others: list[dict]) -> dict:
    """How far a disagreement pool's calls sit from the other detector's nearest call: within 2
    tolerances, 2 to 4, beyond 4, or no call of the other's on that recording and stream."""
    out = dict(near=0, mid=0, far=0, none=0)
    for c in pool:
        g = nearest_gap(c, others)
        key = ("none" if g is None else "near" if g <= 2 * TOL_SEC
               else "mid" if g <= 4 * TOL_SEC else "far")
        out[key] += 1
    return out


def at_floor(c: dict) -> bool:
    """Whether a call's participants reach its window's own event floor (ADR-0008): as the
    detection run recorded it for an unfloored call, and by comparing the two counts where the
    column is blank (a floored run's calls, which reach it by construction)."""
    rec = str(c.get("reaches_own_floor", "")).strip().lower()
    if rec:
        return rec in ("true", "1", "yes")
    try:
        return float(c["participants"]) >= float(c["own_floor"])
    except (KeyError, TypeError, ValueError):
        return False


def render_example(sl, stream: str, call: dict, lanes_for: dict, names: dict, colors: dict,
                   ext: tuple, dest: Path, stem: str, mark_label: str = "this call") -> Path | None:
    """One example: a lane marking the call (▼, pointing down), the detectors' lanes, then the
    recording's raster over the window, rows sorted by event count in the window, busiest at the
    top. Drawn through ``ui.diagnostic`` like every other raster figure; nothing on the raster."""
    import holoviews as hv
    import panel as pn

    from bugarach.ui.diagnostic import lane_panel, raster_panel
    from make_diagnostic import _render_png

    hv.extension("bokeh")
    W = 1160                                      # fills _render_png's 1180 px page
    big = {"yticks": "14pt", "ylabel": "14pt", "xticks": "14pt", "xlabel": "14pt"}
    st = sl.streams[stream]
    lanes = {d: ([float(r["onset_sec"]) for r in rows], [_num(r.get("width_sec")) for r in rows])
             for d, rows in lanes_for.items()}
    mark = hv.Scatter(([float(call["onset_sec"])], [0.0]), kdims=["t"], vdims=["mark"]).opts(
        marker="inverted_triangle", size=16, color="#111111", xlim=ext, ylim=(-0.8, 0.8),
        yticks=[(0, mark_label)], xaxis=None, width=W, height=48, toolbar=None,
        ylabel="", fontsize=big, show_grid=False)
    lp = lane_panel(lanes, ext=ext, width=W, row_px=36, names=names, colors=colors).opts(
        height=36 * len(lanes) + 30, fontsize=big, toolbar=None)
    rp = raster_panel(st, ext=ext, width=W, height=max(240, min(400, 6 * st.n_rois)),
                      name=stream, mark_px=4.0, ticks="minimal").opts(
        fontsize=big, toolbar=None, xlabel="time in recording (min:s)",
        backend_opts={"plot.min_border_left": 90})
    with tempfile.TemporaryDirectory() as td:
        tmp = Path(td) / "ex.html"
        pn.Column(*(pn.pane.HoloViews(p, linked_axes=True, margin=0) for p in (mark, lp, rp)),
                  margin=0).save(str(tmp))
        png = dest / f"{stem}.png"
        return png if _render_png(tmp, png, scale=3) else None


#: Okabe–Ito reddish purple and blue: apart from each other and from CoactDetect's lane colour,
#: which is the review pages' own, and clear of the orange and red the leaderboard uses for its
#: marks. A leader and runner-up of the same learned family would share one colour on the review
#: pages, so the examples give them fixed ones and say so.
LEADER_COLOR, RUNNER_COLOR = "#CC79A7", "#0072B2"


def _check_stamp(res: dict | None) -> None:
    """Refuse to draw the night's calls over the default dataset unless the detection run's own
    stamp says it scored that folder (``check_scored_dataset.scored_on``, which fails closed)."""
    from bugarach import dataset
    from check_scored_dataset import scored_on

    if res is None:
        raise SystemExit(f"{RESULTS} is missing: the calls cannot be checked against the dataset")
    kind, name = scored_on(res)
    want = dataset.current_name("default")
    if kind != "dataset" or name != want:
        raise SystemExit(f"the night's detection is stamped {kind}={name!r}, not the default "
                         f"dataset {want!r}: refusing to draw one over the other")


def examples(model: dict, night: Path, dest: Path) -> dict:
    """Per stream: the leader and CoactDetect (at the setting the review run used) on real
    baseline windows — every call counted by kind and group, and one figure per kind."""
    from bugarach import dataset
    from bugarach.io import load_folder
    from make_group_raster_summary import lane_color

    res = _load(night / RESULTS)
    _check_stamp(res)
    folder = dataset.default()
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        slices = {sl.slice_id: sl for sl in load_folder(folder)}
    calls = read_calls(night / CALLS)
    bounds, hours = read_windows(night / WINDOWS)
    chosen = res.get("chosen") or {}
    out = dict(dataset=dataset.stamp(), participants_rule=res.get("participants_rule"),
               streams={})
    used = set()
    for s in STREAMS:
        board = model["board"][s]
        ch = chosen.get(s) or {}
        ref_which = ((ch.get("detectors") or {}).get("coact") or {}).get("which")
        ref_row = next((e for e in board if e["id"] == f"coact:{ref_which}"), None)
        ref_label = f"CoactDetect · {ref_which or 'as run'}"
        ref_marks = list(((ref_row or {}).get("per", {}).get("new") or {}).get("flags", []))
        passed, leader, runner = [], None, None
        for e in board:
            det = ran_on_real(e, ch)
            why = None
            if e["family"] == "coact":
                why = "CoactDetect is what the leader is compared with"
            elif det is None:
                why = "did not run on the real recordings"
            elif e["per"]["new"] and e["per"]["new"]["budget_fails"]:
                why = "over a budget on the new bench"
            elif e["per"]["new"] and e["per"]["new"]["flags"]:
                why = "its setting sits on a search limit, so it is not adoptable as tuned"
            else:
                k = classify(calls, s, det, "coact")
                a_, l_, r_ = (len(k[x]) for x in ("agree", "leader_only", "ref_only"))
                if not (a_ and l_ and r_):
                    lack = ("never shares a call with CoactDetect" if not a_ else
                            "makes no call CoactDetect lacks" if not l_ else
                            "never lacks a call CoactDetect makes")
                    why = (f"{lack}, so there is no disagreement both ways to show: "
                           f"{n_of(a_, 'call')} shared, {n_of(l_, 'call')} only its own, "
                           f"{n_of(r_, 'call')} only CoactDetect's")
            if why is None:
                if leader is None:
                    leader = (e, det)
                    continue
                runner = (e, det)
                break
            passed.append(dict(label=f"{e['label']} · {setting_words(e)}", why=why,
                               before_leader=leader is None))
        if leader is None:
            out["streams"][s] = dict(passed=passed, leader=None)
            continue
        (le, ldet) = leader
        kinds = classify(calls, s, ldet, "coact")
        many = kinds.pop("_many")
        groups = in_group_order(g for (st, g) in hours if st == s)
        table = {k: {g: sum(1 for c in pool if group_key(c["group"]) == group_key(g))
                     for g in groups} for k, pool in kinds.items()}
        floor_n = {k: sum(1 for c in pool if at_floor(c)) for k, pool in kinds.items()}
        # Lanes carry their role; the full names are printed once above the figures.
        show = [(ldet, "leader", LEADER_COLOR,
                 f"{le['label']} · {setting_words(le)}")]
        if runner:
            show.append((runner[1], "runner-up", RUNNER_COLOR,
                         f"{runner[0]['label']} · {setting_words(runner[0])}"))
        show.append(("coact", "CoactDetect", lane_color("coact"), ref_label))
        L_calls = [c for c in calls if c["stream"] == s and c["detector"] == ldet]
        R_calls = [c for c in calls if c["stream"] == s and c["detector"] == "coact"]
        other_of = {"agree": None, "leader_only": R_calls, "ref_only": L_calls}
        gaps = {k: gap_bins(kinds[k], other_of[k]) for k in ("leader_only", "ref_only")}
        figs = []
        for kind, pool in kinds.items():
            c = pick_one(pool, bounds, used, other_of[kind])
            fig = dict(kind=kind, pool=len(pool),
                       inner=sum(1 for x in pool if _inside(x, bounds)), call=c, png=None,
                       recordings=len({x["slice_id"] for x in pool}))
            if c is not None:
                if other_of[kind] is not None:
                    fig["gap"] = nearest_gap(c, other_of[kind])
                fig["floor"] = c.get("own_floor")
            if c is not None and c["slice_id"] in slices:
                sl = slices[c["slice_id"]]
                if s == "combined":
                    from bugarach.combined import COMBINED, has_sources, stream_of
                    if has_sources(sl) and COMBINED not in sl.streams:
                        sl.streams[COMBINED] = stream_of(sl, COMBINED)
                if s in sl.streams:
                    t = float(c["onset_sec"])
                    b0, b1 = bounds[(c["slice_id"], s, c["region_idx"])]
                    half = EXAMPLE_HALF_SEC[s]
                    ext = (max(b0, t - half), min(b1, t + half))
                    lanes_for = {d: [r for r in calls if r["slice_id"] == c["slice_id"]
                                     and r["stream"] == s and r["detector"] == d
                                     and _span(r)[1] >= ext[0] and _span(r)[0] <= ext[1]]
                                 for d, _, _, _ in show}
                    whose = "CoactDetect's" if kind == "ref_only" else "leader's"
                    png = render_example(sl, s, c, lanes_for, {d: n for d, n, _, _ in show},
                                         {d: col for d, _, col, _ in show}, ext, dest,
                                         f"example_{s}_{kind}", f"this call ({whose})")
                    fig.update(png=png.name if png else None, ext=list(ext),
                               cut=(ext[0] > t - half, ext[1] < t + half))
            figs.append(fig)
        lvl = glance(model)[s]["new"]["level"] if model["board"][s] else 0
        out["streams"][s] = dict(
            passed=passed, leader=f"{le['label']} · {setting_words(le)}", leader_det=ldet,
            leader_mid=le["per"]["new"]["mid"], ref=ref_label, ref_marks=ref_marks,
            runner=show[1][3] if runner else None,
            lanes=[(role, full) for _, role, _, full in show],
            counts=table, totals={k: len(v) for k, v in kinds.items()}, many=many,
            at_floor=floor_n, gaps=gaps,
            hours={g: hours[(s, g)] for g in groups}, figures=figs, level=lvl)
    return out


# --------------------------------------------------------------------------------------------
# rendering
# --------------------------------------------------------------------------------------------

def figure1(model: dict, dest: Path) -> list[Path]:
    """Figure 1, one SVG per stream: every row's paired F1 difference against CoactDetect's
    shipped setting, new bench (filled) above old bench (open), 95% intervals, a gray line joining
    the two centers so the move between benches reads as a line.

    Drawn as SVG by hand: no plotting dependency (matplotlib is not one of this project's), exact
    type sizes (15 px, over the house floor of 11 pt), and the page's own colours in both themes.
    Each stream carries its own axis and legend at the top as well as the bottom. The label column
    is sized from the longest label, so no row name is cut. All three share one x-range."""
    ROW, RIGHT, PLOT_W, CH = 30, 30, 640, 8.3
    labels = {e["id"] + s: f"{e['label']} · {setting_words(e, short=True)}"
              + (" †" if any(not f.startswith("no pick")
                             for v in e["per"].values() if v for f in v["flags"]) else "")
              for s in STREAMS for e in model["board"][s]}
    LEFT = max(330, int(max(len(x) for x in labels.values()) * CH) + 24)
    W = LEFT + PLOT_W + RIGHT
    vals = [x for s in STREAMS for e in model["board"][s] for v in e["per"].values() if v
            for x in (v["lo"], v["hi"]) if x is not None] + [0.0]
    lo, hi = min(vals), max(vals)
    pad = 0.06 * (hi - lo or 0.1)
    lo, hi = lo - pad, hi + pad
    step = next(st for st in (0.01, 0.02, 0.05, 0.1, 0.2) if (hi - lo) / st <= 10)
    ticks, k = [], int(lo / step) - 1
    while k * step <= hi:
        if k * step >= lo:
            ticks.append(round(k * step, 6))
        k += 1

    def X(v):
        return LEFT + (v - lo) / (hi - lo) * PLOT_W

    style = ("<style>.ax{stroke:var(--line,#ccc)} .zero{stroke:var(--fg,#222)} "
             ".t{fill:var(--fg,#222)} .m{fill:var(--muted,#666)} .j{stroke:var(--muted,#999)} "
             ".new{stroke:var(--accent,#0072B2);fill:var(--accent,#0072B2)} "
             ".old{stroke:var(--accent,#0072B2);fill:var(--bg,#fff)} "
             ".badn{stroke:var(--bad,#b03a2e);fill:var(--bad,#b03a2e)} "
             ".bado{stroke:var(--bad,#b03a2e);fill:var(--bg,#fff)}</style>")

    def axis(y, out, below=True):
        for t in ticks:
            out.append(f"<text class='m' x='{X(t):.1f}' y='{y + (20 if below else -8)}' "
                       f"text-anchor='middle'>{'0' if abs(t) < 1e-9 else f'{t:+.2f}'}</text>")

    def legend(y, out):
        items = (("new", "new bench"), ("old", "old bench"),
                 ("badn", "new bench, over a budget or no pick"),
                 ("bado", "old bench, over a budget or no pick"))
        x = 8
        for cls, text in items:
            out.append(f"<circle class='{cls}' cx='{x + 6}' cy='{y - 5}' r='5' stroke-width='2'/>"
                       f"<text class='t' x='{x + 16}' y='{y}'>{text}</text>")
            x += 16 + int(8.4 * len(text)) + 22
        out.append(f"<text class='m' x='8' y='{y + 24}'>† the setting sits on a search limit, not "
                   f"adoptable as tuned · the vertical line at 0 is CoactDetect at its shipped "
                   f"setting</text>")

    paths = []
    for s in STREAMS:
        rows = model["board"][s]
        top = 108
        H = top + ROW * len(rows) + 70
        out = [f"<svg xmlns='http://www.w3.org/2000/svg' width='{W}' height='{H}' "
               f"viewBox='0 0 {W} {H}' font-family='system-ui, sans-serif' font-size='15' "
               f"role='img' aria-label='Figure 1{'abc'[STREAMS.index(s)]}, the {s} stream'>",
               style]
        out.append(f"<text class='t' x='8' y='16' font-weight='650'>{s} stream · "
                   f"{n_of(len(rows), 'row')}, CoactDetect's shipped row among them</text>")
        legend(42, out)
        axis(top - 4, out, below=False)
        y = top
        for e in rows:
            cy = y + ROW / 2
            out.append(f"<text class='t' x='{LEFT - 10}' y='{cy + 5}' text-anchor='end'>"
                       f"{html.escape(labels[e['id'] + s])}</text>")
            out.append(f"<line class='ax' x1='{LEFT}' x2='{W - RIGHT}' y1='{y + ROW}' "
                       f"y2='{y + ROW}' stroke-width='0.5'/>")
            n, o = e["per"]["new"], e["per"]["old"]
            if n and o and n["mid"] is not None and o["mid"] is not None:
                out.append(f"<line class='j' x1='{X(n['mid']):.1f}' y1='{cy - 6}' "
                           f"x2='{X(o['mid']):.1f}' y2='{cy + 6}' stroke-width='1.2'/>")
            for col, dy in (("new", -6), ("old", 6)):
                v = e["per"][col]
                if not v or v["mid"] is None:
                    continue
                bad = bool(v["budget_fails"]) or any(f.startswith("no pick") for f in v["flags"])
                cls = {("new", False): "new", ("old", False): "old",
                       ("new", True): "badn", ("old", True): "bado"}[(col, bad)]
                out.append(f"<line class='{cls}' x1='{X(v['lo']):.1f}' x2='{X(v['hi']):.1f}' "
                           f"y1='{cy + dy}' y2='{cy + dy}' stroke-width='2'/>")
                out.append(f"<circle class='{cls}' cx='{X(v['mid']):.1f}' cy='{cy + dy}' r='5' "
                           f"stroke-width='2'/>")
            y += ROW
        for t in ticks:
            out.append(f"<line class='{'zero' if t == 0 else 'ax'}' x1='{X(t):.1f}' "
                       f"x2='{X(t):.1f}' y1='{top}' y2='{y}' "
                       f"stroke-width='{1.2 if t == 0 else 0.6}'/>")
        axis(y, out)
        out.append(f"<text class='t' x='{LEFT + PLOT_W / 2}' y='{y + 46}' "
                   f"text-anchor='middle'>ΔF1 against CoactDetect at its shipped setting, 95% "
                   f"interval</text>")
        out.append("</svg>")
        p = dest / f"figure1_{s}.svg"
        p.write_text("\n".join(out), encoding="utf-8")
        paths.append(p)
    return paths


CSS = """
:root { --bg:#fbfaf7; --fg:#1b1b1b; --muted:#5b5b5b; --line:#dcd8cf; --accent:#0072B2;
        --bad:#b03a2e; --warn:#b35c00; --card:#ffffff; --mono: ui-monospace, Consolas, monospace; }
@media (prefers-color-scheme: dark) { :root:not([data-theme="light"]) {
  --bg:#141414; --fg:#e8e6e1; --muted:#a8a49c; --line:#3a3833; --accent:#6cb4e4;
  --bad:#ef8a7e; --warn:#e3a35a; --card:#1d1d1d; } }
:root[data-theme="dark"] { --bg:#141414; --fg:#e8e6e1; --muted:#a8a49c; --line:#3a3833;
  --accent:#6cb4e4; --bad:#ef8a7e; --warn:#e3a35a; --card:#1d1d1d; }
html { font-size: 17px; }
body { background: var(--bg); color: var(--fg); margin: 0;
       font: 1rem/1.55 system-ui, -apple-system, "Segoe UI", sans-serif; }
.wrap { max-width: 1080px; margin: 0 auto; padding: 24px 16px 80px; }
h1 { font-size: 1.9rem; margin: 0 0 .3rem; } h2 { font-size: 1.4rem; margin: 2.4rem 0 .6rem; }
h3 { font-size: 1.1rem; margin: 1.8rem 0 .4rem; }
.byline, .muted { color: var(--muted); }
nav a { margin-right: 1.1rem; }
a { color: var(--accent); }
.tablewrap { overflow-x: auto; }
table { border-collapse: collapse; width: 100%; margin: .6rem 0 1rem; font-size: 1rem; }
caption { text-align: left; }
th, td { border-bottom: 1px solid var(--line); padding: .35rem .5rem; text-align: left;
         vertical-align: top; }
th { font-weight: 650; }
td.n { font-family: var(--mono); white-space: nowrap; text-align: right; }
td.setting { min-width: 12rem; }
td.wrapn { font-family: var(--mono); text-align: right; }
td.marks { padding-top: 0; }
.bad { color: var(--bad); font-weight: 600; } .warn { color: var(--warn); }
figure { margin: 1.2rem 0 1.8rem; }
figure img.ex { width: 1080px; max-width: none; height: auto; background: #fff;
                border: 1px solid var(--line); box-sizing: border-box; display: block; }
.scrollcue { display: none; color: var(--muted); font-size: .95rem; }
@media (max-width: 1100px) { .scrollcue { display: block; } }
p.cap { margin: 1rem 0 .2rem; }
.tcue { color: var(--muted); font-size: .95rem; margin: 0; }
@media (min-width: 1500px) { .tcue.wideonly { display: none; } }
@media (min-width: 700px) { .tcue.narrow { display: none; } }
@media (min-width: 1400px) {
  figure.wide, div.widetable { width: min(94vw, 1700px);
                               margin-left: calc((100% - min(94vw, 1700px)) / 2); }
  figure.wide img.ex { width: 100%; }
  figure.wide svg { width: 100%; height: auto; }
}
dl.terms { display: grid; grid-template-columns: minmax(9rem, max-content) 1fr; gap: .35rem 1rem; }
dl.terms dt { font-weight: 650; } dl.terms dd { margin: 0; }
@media (max-width: 700px) { dl.terms { grid-template-columns: 1fr; } dl.terms dd { margin-bottom: .5rem; } }
figcaption { color: var(--muted); margin-top: .4rem; }
code { font-family: var(--mono); font-size: .95em; overflow-wrap: anywhere; }
.box { border: 1px solid var(--line); background: var(--card); padding: .8rem 1rem;
       border-radius: 6px; margin: 1rem 0; }
.box ul, .notes { margin: .3rem 0; padding-left: 1.2rem; }
details > summary { cursor: pointer; font-weight: 650; margin: 1rem 0 .4rem; }
.chips a { white-space: nowrap; }
th.num { text-align: right; }
"""


def tbl(caption: str, inner: str, *, wide: bool = False, cue: bool = False) -> str:
    """A numbered table with its caption above the scroller, not inside it, so the caption never
    scrolls out of view. ``wide`` breaks out of the text column on a wide screen; ``cue`` says the
    table scrolls sideways where it does (always on a phone, below 1500 px for a wide one)."""
    cues = ("<p class='tcue wideonly'>Scroll the table sideways for every column →</p>"
            if wide else "") + ("<p class='tcue narrow'>Scroll the table sideways →</p>"
                                if cue or wide else "")
    body = f"<div class='tablewrap'><table>{inner}</table></div>"
    return (f"<p class='cap'>{caption}</p>{cues}"
            + (f"<div class='widetable'>{body}</div>" if wide else body))


def _marks_html(e: dict) -> str:
    """A row's marks: each bench's budget failures (said once when both benches fail alike), then
    the flags the search or the training pick carries, then the notes, then an identical-scores
    note."""
    out = []
    n, o = e["per"].get("new"), e["per"].get("old")
    nf, of = (n or {}).get("budget_fails", []), (o or {}).get("budget_fails", [])
    same = nf and nf == of
    for where, fails in (("both benches", nf if same else []),
                         ("the new bench", [] if same else nf),
                         ("the old bench", [] if same else of)):
        for f in fails:
            out.append(f"<span class='bad'>Over budget on {where}: "
                       f"{html.escape(budget_words(f))}</span>")
    first = n or o
    for f in (first or {}).get("flags", []):
        cls = "bad" if f.startswith("no pick") else "warn"
        out.append(f"<span class='{cls}'>{html.escape(f[0].upper() + f[1:])}</span>")
    for col, name in (("new", "new"), ("old", "old")):
        if e["same_as"].get(col):
            out.append(f"<span class='muted'>Same scores as {html.escape(e['same_as'][col])} to "
                       f"every digit on the {name} bench: there one result, shown twice, and "
                       f"counted once.</span>")
    if (n and e["id"] != "coact:shipped" and n["lo"] is not None
            and max(abs(n["lo"]), abs(n["hi"])) < 0.002):
        out.append("<span class='muted'>Reproduces CoactDetect's shipped setting to within 0.002 "
                   "F1 on the new bench.</span>")
    return "<br>".join(out)


def _spread_words(sp: dict) -> str:
    if abs(sp["hi"] - sp["lo"]) < 0.005:
        return f"held-out F1 {sp['lo']:.2f} in all {n_of(sp['n'], 'run')}"
    return f"held-out F1 of the {n_of(sp['n'], 'run')}: {sp['lo']:.2f}–{sp['hi']:.2f}"


def _setting_cell(e: dict) -> str:
    s = html.escape(setting_words(e))
    sp = e.get("spread")
    if e["id"].startswith("learned:") and sp:
        s += f"<br><span class='muted'>{_spread_words(sp)}</span>"
    return s


def leaderboard_table(model: dict, s: str, tno: int) -> str:
    rows = model["board"][s]
    head = ("<tr><th>#</th><th>detector or model</th><th>setting</th>"
            "<th>new bench ΔF1 [95%]</th><th>new F1 · without decoys</th>"
            "<th>new recall, quiet · busy</th>"
            "<th>old bench ΔF1 [95%]</th><th>old F1 · without decoys</th>"
            "<th>merged calls, new</th></tr>")
    body = []
    for i, e in enumerate(rows, 1):
        cells = []
        for col in ("new", "old"):
            v = e["per"][col]
            if not v:
                cells += ["<td class='n muted'>not scored</td>", "<td class='n'>—</td>"]
            else:
                cells += [f"<td class='n'>{_f(v['mid'])} [{_f(v['lo'])}, {_f(v['hi'])}]</td>",
                          f"<td class='n'>{_f(v['mean_f1'], sign=False)} · "
                          f"{_f(v['mean_f1_without_decoys'], sign=False)}</td>"]
            if col == "new":
                cells.append(f"<td class='n'>{_f((v or {}).get('recall_quiet'), 2, False)} · "
                             f"{_f((v or {}).get('recall_busy'), 2, False)}</td>")
        mc = (e["per"]["new"] or {}).get("merged_calls")
        cells.append(f"<td class='n'>{n_of(mc, 'call') if mc is not None else '—'}</td>")
        marks = _marks_html(e)
        edge = " style='border-bottom:none'" if marks else ""
        body.append(f"<tr><td class='n'{edge}>{i}</td><td{edge}>{html.escape(e['label'])}</td>"
                    f"<td class='setting'{edge}>{_setting_cell(e)}</td>"
                    + "".join(c.replace("<td", f"<td{edge}", 1) for c in cells) + "</tr>")
        if marks:
            body.append(f"<tr><td></td><td colspan='8' class='marks'>{marks}</td></tr>")
    if not model["count_present"]:
        body.append("<tr><td class='n'>—</td><td>count (the simple rule)</td><td>—</td>"
                    "<td class='muted' colspan='6'>not scored yet: its results land in "
                    "WSMIP064's count folder, and rerunning this page's builder adds the row."
                    "</td></tr>")
    return tbl(f"<b>Table {tno}.</b> The {s} stream, {n_of(len(rows), 'row')}, in Figure 1's "
               f"order. F1 is the mean over the quiet and busy backgrounds; ΔF1 is, per "
               f"simulation seed, F1 pooled over that seed's quiet and busy recordings, "
               f"differenced against CoactDetect and averaged over seeds, so the F1 columns do "
               f"not subtract to it exactly. Red: over a budget, or no pick. Orange: a search "
               f"limit (†).", head + "".join(body), wide=True)


def glance_html(g: dict) -> str:
    head = ("<tr><th>stream</th><th>bench</th><th>above CoactDetect's proposal</th>"
            "<th>interval wholly above zero</th>"
            "<th>… of those, unflagged</th><th>includes zero</th><th>wholly below</th>"
            "<th>F1 without decoys above the reference's"
            "</th><th>top unflagged row (ΔF1), and rows level with it</th></tr>")
    body = []
    for s in STREAMS:
        for col in ("new", "old"):
            v = g[s].get(col)
            if not v:
                body.append(f"<tr><td>{s}</td><td>{col}</td><td colspan='7' class='muted'>not "
                            f"scored</td></tr>")
                continue
            top = (f"{html.escape(v['top'])} ({_f(v['top_mid'])}); "
                   f"{n_of(v['level'] - 1, 'other row')} within {NOISE_UNIT:g} of it"
                   ) if v["top"] else "none"
            learned = (f" ({v['above_learned']} learned)" if v["above_learned"] else "")
            body.append(f"<tr><td>{s}</td><td>{col}</td>"
                        f"<td class='n'>{v['vp_above']} of {n_of(v['vp_n'], 'row')}</td>"
                        f"<td class='n'>{v['above']} of {n_of(v['n'], 'row')}{learned}</td>"
                        f"<td class='n'>{n_of(v['above_clean'], 'row')}</td>"
                        f"<td class='n'>{n_of(v['straddle'], 'row')}</td>"
                        f"<td class='n'>{n_of(v['below'], 'row')}</td>"
                        f"<td class='n'>{v['above_wo']} of {n_of(v['n'], 'row')}</td>"
                        f"<td>{top}</td></tr>")
    return tbl(
        "<b>Table 2.</b> Figure 1 tallied, per stream and bench, over the rows besides "
        "CoactDetect's shipped setting (a row that repeats another's scores on that bench "
        "counted once). The first column reads each row's 95% interval of ΔF1 against "
        "CoactDetect's own proposal on that bench, every row but CoactDetect's; the next four "
        "read it against CoactDetect's shipped setting, the zero line of Figure 1. \"Learned\" "
        "rows' intervals cover simulation seeds only, not the spread across training runs. Each "
        "interval stands alone, uncorrected for the many rows. The next column compares point "
        "values of F1 without decoy calls. \"Unflagged\" and \"level\" are defined in "
        "<a href='#terms'>Terms</a>.", head + "".join(body), cue=True)


def reference_table(g: dict) -> str:
    """The reference's own numbers on each bench: what moves between them."""
    head = ("<tr><th>stream</th><th>bench</th><th>F1 · without decoys</th>"
            "<th>recall, quiet · busy</th><th>planted events scored</th><th>calls on decoys</th>"
            "<th>merged calls</th></tr>")
    body = []
    for s in STREAMS:
        for col in ("new", "old"):
            v = g[s].get(col)
            if not v:
                continue
            rq, rb = v["ref_recall"]
            per = (f"<br><span class='muted'>{v['ref_decoys'] / v['seeds']:.1f} per seed</span>"
                   if v.get("seeds") and v["ref_decoys"] is not None else "")
            merged = (n_of(v["ref_merged"] or 0, "call") if col == "new" else
                      "— <span class='muted'>(none possible: events at least 120 s apart)</span>")
            body.append(f"<tr><td>{s}</td><td>{col}</td><td class='n'>"
                        f"{_f(v['ref_f1'], sign=False)} · {_f(v['ref_f1_wo'], sign=False)}</td>"
                        f"<td class='n'>{_f(rq, 2, False)} · {_f(rb, 2, False)}</td>"
                        f"<td class='n'>{n_of(v['ref_planted'] or 0, 'event')}</td>"
                        f"<td class='wrapn'>{n_of(v['ref_decoys'] or 0, 'call')}{per}</td>"
                        f"<td class='wrapn'>{merged}</td></tr>")
    ceil = [s for s in STREAMS if g[s].get("old") and min(
        x or 0 for x in (*g[s]["old"]["ref_recall"], g[s]["old"]["ref_f1_wo"])) >= 0.995]
    ceil_txt = (f" On the old bench, {' and '.join(ceil)} recall and F1 without decoys sit at "
                f"1.00, so there that bench can register little but calls on decoys." if ceil
                else "")
    return tbl("<b>Table 1.</b> CoactDetect at its shipped setting, Figure 1's zero line, on each "
               "bench: what moves under it. Counts are summed over every simulation seed and both "
               f"backgrounds.{ceil_txt}", head + "".join(body), cue=True)


def headline(g: dict, seeds: dict | None) -> str:
    """The result first, each number computed from Tables 1 and 2, then the one reading that
    governs all of them."""
    parts, tot_vp, tot_sh = [], 0, 0
    for s in STREAMS:
        n, o = g[s].get("new"), g[s].get("old")
        if not n:
            continue
        tot_vp += n["vp_above"]
        tot_sh += n["above"]
        txt = (f"<li><b>{s.capitalize()}:</b> against CoactDetect's own new-bench proposal, "
               f"{n['vp_above']} of {n_of(n['vp_n'], 'row')} "
               f"{'has' if n['vp_above'] == 1 else 'have'} a 95% interval of ΔF1 wholly above "
               f"zero. Against its shipped setting, {n['above']} of {n['n']} "
               f"{'does' if n['above'] == 1 else 'do'}")
        txt += f" (old bench: {o['above']} of {o['n']})" if o else ""
        if o:
            verb = "falls" if (n["ref_f1"] or 0) < (o["ref_f1"] or 0) else "rises"
            f1 = (f"its F1 {verb} from {_f(o['ref_f1'], sign=False)} to "
                  f"{_f(n['ref_f1'], sign=False)}")
            dec_ratio = (n["ref_decoys"] or 0) / max(o["ref_decoys"] or 1, 1)
            rq_n, rq_o = n["ref_recall"], o["ref_recall"]
            seed_ratio = (n["seeds"] or 1) / max(o["seeds"] or 1, 1)
            if dec_ratio >= 1.5 and abs((rq_n[0] or 0) - (rq_o[0] or 0)) < 0.1 \
                    and seed_ratio >= 1.5 and n["seeds"] and o["seeds"]:
                txt += (f", mostly because the shipped setting itself loses on the new bench: "
                        f"{f1} while its recall barely moves. It calls decoys at the same rate "
                        f"({o['ref_decoys'] / o['seeds']:.1f} against "
                        f"{n['ref_decoys'] / n['seeds']:.1f} calls per seed), but each recording "
                        f"now plants about {o['ref_planted'] / o['seeds']:.0f} → "
                        f"{n['ref_planted'] / n['seeds']:.0f} scored events per seed, so decoys "
                        f"are a larger share of its calls (ADR-0010 ruling 2 doubles the seeds to "
                        f"keep the event count). On F1 without decoys, {n['above_wo']} of "
                        f"{n['n']} rows beat it.")
            elif (n["ref_merged"] or 0) > (o["ref_merged"] or 0) + 5:
                txt += (f", mostly because the shipped setting itself loses on the new bench: "
                        f"{f1}. Its recall is {_f(rq_n[0], 2, False)} quiet · "
                        f"{_f(rq_n[1], 2, False)} busy against {_f(rq_o[0], 2, False)} · "
                        f"{_f(rq_o[1], 2, False)}, and it merges close events "
                        f"({n_of(n['ref_merged'], 'merged call')}; none are possible on the old "
                        f"bench). F1 without decoys, which shows that loss directly, goes from "
                        f"{_f(o['ref_f1_wo'], sign=False)} to {_f(n['ref_f1_wo'], sign=False)}")
                if abs((n["ref_f1"] or 0) - (o["ref_f1"] or 0)) < 0.02:
                    txt += (f"; F1 itself barely moves because planted events rose "
                            f"({o['ref_planted']} to {n['ref_planted']}) while calls on decoys "
                            f"held ({o['ref_decoys']} to {n['ref_decoys']})")
                txt += "."
            else:
                txt += "."
        else:
            txt += "."
        if n["level"] > 1 and n["top"]:
            txt += (f" The top unflagged row has {n_of(n['level'] - 1, 'other row')} within "
                    f"{NOISE_UNIT:g} F1 of it, so the leaderboard does not separate them.")
        parts.append(txt + "</li>")
    title = ("What the new bench shows: it mostly exposes CoactDetect's shipped setting, not "
             "better detectors." if tot_sh and tot_vp * 3 < tot_sh else
             "What the new bench against the old bench shows.")
    return ("<div class='box'><p><b>" + title + "</b> Each row of Figure 1 below is a detector "
            "at one setting, or a learned model's picked training run (or, where no run met the "
            "budget, its best run, shown as a comparator), scored on simulated recordings with "
            "known coordinated events. ΔF1 is a row's F1 minus CoactDetect's on the same "
            "recordings. CoactDetect's <i>shipped</i> setting is the one in its code before this "
            "night, and Figure 1's zero line; its <i>proposal</i> is the setting the night's search "
            "found best on the new bench. <i>Decoys</i> are planted look-alike events. A row is "
            "<i>unflagged</i> when it is within every budget and not on a search limit.</p><ul>"
            + "".join(parts) + "</ul><p>The proposals and the learned picks were chosen on the "
            "new bench, so their new-bench numbers favor them; the shipped settings predate it. "
            "The old bench is shown because you asked to see new against old; ADR-0010 ruling 2 "
            "retired it as a reference, so it decides nothing. Each interval stands alone, "
            "uncorrected for the many rows. Section 2 says which of the top rows ran on the real "
            "recordings. Terms are defined <a href='#terms'>at the end</a>.</p></div>")


def orx_paragraph(orx: dict | None) -> str:
    """ADR-0010 ruling 1's check, answered first, visible under Figure 1: it is evidence about how
    far the order holds, not a reading instruction."""
    if not orx or not orx["streams"]:
        return ""
    per = "; ".join(
        f"{s} ρ = {v['rho']:.2f} over {n_of(v['rows'], 'row')}"
        + (f", {v['rho_upper']:.2f} among the {v['upper_rows']} at or above zero"
           if v.get("rho_upper") is not None else "")
        for s, v in orx["streams"].items() if v["rho"] is not None)
    tops = "; ".join(f"{s}: {html.escape(v['top_new'])} on the new bench, "
                     f"{html.escape(v['top_orx'])} on the ORX-spaced one"
                     for s, v in orx["streams"].items() if v["top_new"] != v["top_orx"])
    n_str = len(orx["streams"])
    head = ("The tail of the order holds; the top does not." if orx["top_moved"] == n_str
            else "The order mostly holds.")
    return (f"<p><b>Does the order hold on a bench spaced like the ORX recordings?</b> "
            f"(ADR-0010 ruling 1; the same rows were scored there, the count rule included.) "
            f"{head} Spearman rank correlation (ρ) of ΔF1 with the new bench: {per}. The top row, "
            f"flagged or not, changes on {orx['top_moved']} of {n_of(n_str, 'stream')}"
            + (f" ({tops})" if tops else "") + ". Against CoactDetect's shipped setting, "
            f"{n_of(orx['changed_above'], 'interval')} of {orx['rows']} move between wholly above "
            f"zero and including it, {orx['changed_below']} between including zero and wholly "
            f"below, and {orx['crossed']} cross from one side to the other. (The 065 worker's run "
            f"notes count differently: they also count intervals against CoactDetect's proposal, "
            f"and they predate the count rule, whose rows this count includes.)</p>")


def viewer_href(slice_id: str, stream: str) -> str:
    return f"viewer.html#slice={quote(slice_id)}&stream={quote(stream)}"


def vlink(slice_id: str, stream: str, text: str) -> str:
    """A link into the viewer tab. Every link names the same tab, so after the first one the
    browser changes only the address's fragment: the viewer jumps to the recording without
    reloading, and the folder it already has open stays open. A stream the viewer cannot open
    (see :data:`VIEWER_STREAMS`) gets the text alone, not a link that lands on an error."""
    if stream not in VIEWER_STREAMS:
        return html.escape(text)
    return (f"<a href='{viewer_href(slice_id, stream)}' target='{VIEWER_TAB}'>"
            f"{html.escape(text)}</a>")


EX_TEXT = {"agree": "{L} and {R} both call it",
           "leader_only": "{L} calls it; {R} does not",
           "ref_only": "{R} calls it; {L} does not"}
EX_HEAD = {"agree": "both call it (leader's calls)",
           "leader_only": "only the leader (leader's calls)",
           "ref_only": "only CoactDetect (CoactDetect's calls)"}


def viewer_box(dataset_name: str | None, has_results: bool) -> str:
    return (
        "<div class='box' id='viewer-setup'><b>Opening a recording in the viewer.</b> Every "
        "recording link on this page opens a copy of the bugarach viewer, saved beside this page, "
        "at that recording and stream, with the night's calls in lanes above the raster, one lane "
        "per detector and floor variant. All links open in one viewer tab. The viewer reads only "
        "files you open, and nothing leaves the machine. In that tab, the first time:<ul>"
        "<li>expand <i>Open a folder</i> in the left rail and click <i>Choose folder…</i>; pick "
        f"the export folder <code>{html.escape(dataset_name or 'of the default dataset')}</code>, "
        "in the bugarach exports folder under this machine's data root (opened from a file, "
        "Chrome shows its own file dialog, which may say \"upload\": nothing is uploaded);</li>"
        "<li>click <i>Open results (detections.csv)…</i> and pick "
        f"{'the <code>detections.csv</code> beside this page' if has_results else 'the night’s detections.csv'}"
        " (written from the night's calls by the detection run's export step; this page's "
        "builder only links it).</li></ul>Leave that tab open: every later link jumps within it, "
        "keeping the folder and the results. A link opens the recording at its start; the "
        "caption gives the time of the call. The viewer names lanes by short id: <i>coact</i> is "
        "CoactDetect, <i>sync</i> SPIKE-synch, <i>rate</i> rate+context, <i>sixth</i> locust, "
        "and a learned model by its name; <i>own_floor</i> is the run at the window's own event "
        "floor, which the examples use. <b>The viewer has no combined stream</b> (it is derived, "
        "never stored in the export folder), so combined recordings carry no viewer link; their "
        "calls are on the combined review pages in <a href='#rasters'>section 3</a>.</div>")


def render(model: dict, exs: dict | None, recs: list[dict], pages: list[str], *,
           dataset_name: str | None, has_results: bool) -> str:
    src = model["sources"]
    g = glance(model)
    parts = []
    parts.append(
        "<h1>Full-panel night briefing</h1><p class='byline'>On the night of 2026-09-25 every "
        "coded detector's settings were searched, and the four learned families ADR-0010 names "
        "were trained, each with and without participation (8 models), on the new bench: "
        "planted events spaced as measured in real recordings (ADR-0010). Everything was then "
        "scored on fresh simulation seeds that neither the search nor the training saw; the "
        "last scoring finished on the evening of 2026-09-26. "
        f"Built {html.escape(model['built'])}. Every number is read from the night's files. "
        "Nothing here is adopted.</p>")
    parts.append("<nav><a href='#leaderboard'>1. Leaderboard</a><a href='#examples'>2. Examples"
                 "</a><a href='#rasters'>3. Rasters</a><a href='#terms'>Terms</a></nav>")
    # 1. leaderboard -------------------------------------------------------------------------
    parts.append("<h2 id='leaderboard'>1. Leaderboard: every detector and learned pick against "
                 "CoactDetect</h2>")
    parts.append(headline(g, src))
    fams = list(dict.fromkeys(e["family"].removesuffix("_part")
                              for s in STREAMS for e in model["board"][s]))
    fams = [f for f in WHAT_ORDER if f in fams] + [f for f in fams if f not in WHAT_ORDER]
    parts.append("<details><summary>What each row is: the detectors and models compared "
                 "(coded = a hand-written rule with settings; learned = a trained network)"
                 "</summary><ul>"
                 + "".join(f"<li><b>{html.escape(display_name(f))}</b>: {WHAT[f]}.</li>"
                           for f in fams if f in WHAT)
                 + f"</ul><p>{PART_NOTE}</p><p>{SETTING_NOTE}</p></details>")
    parts.append("<p>Figure 1 is sorted by ΔF1 on the new bench, top down. Red rows are over a "
                 "budget and † rows sit on a search limit, so the first row that could be adopted "
                 "is the first with neither; Table 2 names it per stream.</p>")
    for s, svg in zip(STREAMS, model.get("_figure1_svgs", [])):
        letter = "abc"[STREAMS.index(s)]
        cap = (f"<b>Figure 1{letter}, the {s} stream.</b> Each row's paired F1 difference (ΔF1) "
               f"against CoactDetect at its shipped setting, the vertical line at 0. Filled marks "
               f"are the new bench, open marks the old, bars the 95% interval over simulation "
               f"seeds, and the gray line joins the two. Red: over a budget on that bench, or a "
               f"training run with no pick. Row labels are short: \"pick, run 5 of 5\" is the "
               f"picked training run 5 of 5; \"starting point\" is the count rule's untuned "
               f"one. All three panels share one x-range.") if letter == "a" else (
               f"<b>Figure 1{letter}, the {s} stream.</b> As Figure 1a.")
        parts.append(f"<figure class='wide'><p class='scrollcue'>Scroll the figure sideways for "
                     f"the marks →</p><div class='tablewrap'>{svg}</div><figcaption>{cap}"
                     f"</figcaption></figure>")
    parts.append(orx_paragraph(model.get("orx")))
    parts.append(reference_table(g))
    parts.append(glance_html(g))
    seeds = []
    for col in ("new", "old"):
        s_ = src[col]
        name = "new bench" if col == "new" else "old bench"
        if s_["present"]:
            ex = "".join(f"; the {' and '.join(x['rows'])} rows come from a follow-up run "
                         f"scored {html.escape(x['written'] or '')}" for x in s_["extra"])
            seeds.append(f"<li>The {name} was scored {html.escape(s_['written'] or '')}, on "
                         + ", ".join(f"{v} {k}" for k, v in s_["seeds"].items())
                         + f" simulation seeds, each one quiet and one busy recording{ex}.</li>")
        else:
            seeds.append(f"<li class='bad'>The {name} is not scored yet "
                         f"(<code>{html.escape(s_['path'])}</code> is missing).</li>")
    parts.append(
        "<details><summary>How to read it, and where the numbers come from</summary><ul>"
        f"<li><b>The interval.</b> ΔF1 is paired: the mean over simulation seeds of (row F1 − "
        f"CoactDetect F1), with a 95% percentile-bootstrap interval over seeds "
        f"({model['bootstrap']:,} draws). It covers simulation seeds only, not the choice among a "
        f"learned model's training runs, whose held-out F1 can spread far wider (Tables 3–5 give "
        f"each spread), and each interval stands alone, uncorrected for the many rows. Fast has "
        f"twice the seeds on the new bench (ADR-0010 ruling 2), so its new-bench intervals are "
        f"narrower than its old-bench ones and count differently.</li>"
        f"<li><b>Level.</b> This page treats rows within {NOISE_UNIT:g} F1 of each other as level, "
        f"borrowing the draw-to-draw spread ADR-0010 part 1 measured in an earlier comparison. "
        f"The paired intervals here are wider than that, about ±0.015 to ±0.035, so rows further "
        f"apart can be tied too; \"level\" is the least the page cannot separate, not the "
        f"most.</li>"
        "<li><b>Decoys.</b> The bench plants look-alike events (decoys) and scores a call on one "
        "as a false alarm. Decoys are coordination by construction, so ADR-0006 rules that a "
        "call on one is not a false alarm; the bench keeps scoring it as one until a later "
        "decision changes its objective (ADR-0006, consequences). Hence F1 without decoy calls "
        "beside F1, and recall on each background. The ranking itself still uses F1 with decoys, "
        "the reading ADR-0006 disputes, and F1 without decoys has no interval here: the scored "
        "files keep no per-seed values to draw one from.</li>"
        "<li><b>Budgets.</b> A row is marked over budget if it fails any budget in force under "
        "the search's own admissibility rule. The budgets are: calls per hour on the "
        "no-coordination test (a recording with nothing planted); calls inside and outside the "
        "elevated-rate test's stretch (a stretch where the background rate is raised with "
        "nothing planted), outside it only on the quiet background, as the search checks it; "
        "and the precision swing, the change in precision between the quiet and busy "
        "backgrounds. The limits are set per detector and stream, most just above each "
        "detector's own shipped measurement, so a shipped setting passes its own almost by "
        "construction; learned models are held to CoactDetect's, a stricter bar than some coded "
        "detectors' own. The limits are read from <code>src/bugarach/bench*.py</code> as of this "
        "build; the run records only the no-coordination limits, and those match. ADR-0010 part "
        "4 retired the close-events test. The 065 worker's README counts only the "
        "no-coordination budget, the one the training pick uses, so it names one row over budget "
        "where this page marks more.</li>"
        "<li><b>Rows the scored files do not carry.</b> A detector with no proposal row had none "
        "in the scored file. 064's README records a rescued fast SPIKE-synch setting (maximum "
        "τ 0.25 → 0.5 s, because the shipped point is over budget; held-out gain −0.018) that "
        "065's README and the scoring do not carry; this page follows the scored file.</li>"
        + "".join(seeds) + "</ul></details>")
    parts.append("<details><summary>Tables 3–5: every number behind Figure 1, with each row's "
                 "recall and its budget and limit marks</summary>")
    for i, s in enumerate(STREAMS, 3):
        parts.append(f"<h3>{s.capitalize()} stream</h3>" + leaderboard_table(model, s, i))
    parts.append("</details>")
    # 2. examples ----------------------------------------------------------------------------
    parts.append("<h2 id='examples'>2. Examples on real recordings</h2>")
    fig_no, tno = 2, 6
    if exs is None:
        parts.append(viewer_box(dataset_name, has_results))
        parts.append("<p class='bad'>Not built: the examples read the default dataset, and this "
                     "build ran without it (<code>--no-examples</code>, or the dataset was not "
                     "confirmed for the session).</p>")
    else:
        rule = exs.get("participants_rule") or _participants_rule()
        which = []
        for s in STREAMS:
            ex = exs["streams"].get(s) or {}
            above = [p for p in ex.get("passed", []) if p.get("before_leader", True)
                     and not p["why"].startswith("CoactDetect")]
            nr = sum(1 for p in above if p["why"].startswith("did not run"))
            if ex.get("leader") is None:
                which.append(f"on {s}, no row meets the rule")
            elif not above:
                which.append(f"on {s}, the leader is the top row of Figure 1"
                             f"{'abc'[STREAMS.index(s)]} besides CoactDetect's")
            else:
                rest = len(above) - nr
                which.append(f"on {s}, {nr} of the {n_of(len(above), 'row')} above the leader "
                             f"did not run on the real recordings and {rest} "
                             f"{'was' if rest == 1 else 'were'} passed over for a budget or a "
                             f"search limit")
        parts.append(
            "<div class='box'><b>Read this first.</b> The night's detection on the real "
            "recordings ran each coded detector at its proposal where the search made one, so "
            "here CoactDetect is at its proposal, not the shipped setting that is the "
            "leaderboard's zero line. The examples can test only rows that ran there and are "
            "unflagged: " + "; ".join(which) + ". And the comparison is not like for like: "
            "CoactDetect runs at each window's event floor (ADR-0008) and cannot call below it, "
            "while a learned leader runs without one, so a learned leader's calls that CoactDetect "
            "lacks can fall below the floor. Each table below counts, per kind, the calls that "
            "reach it. With no ground "
            "truth on real recordings, a call only one detector makes is a disagreement, not a "
            "missed event.</div>")
        parts.append(viewer_box(dataset_name, has_results))
        parts.append(
            "<p>For each stream, the <b>leader</b> is the first row in Figure 1's order (1a, 1b or "
            "1c) that ran on the real recordings, is within every budget and not on a search "
            "limit, shares at least one call with CoactDetect, and has at least one call "
            "CoactDetect lacks while lacking at least one of CoactDetect's. The <b>runner-up</b> "
            "is the next row meeting the same rule. Every row passed over is named with its "
            "reason, below each stream's figures. Only baseline windows are used. For the four "
            "detectors that ran and take the event floor as their minimum (CoactDetect, LoCo, "
            "binned SCE and SPIKE-synch), the calls are from the run at each window's own floor, "
            "as the review pages draw them; the others' calls are as they ran.</p>"
            f"<p>Two calls agree when their spans come within {TOL_SEC:g} s of each other, "
            f"inclusive. That is the bench's tolerance value under a looser matching rule than "
            f"the bench's one-to-one matching: span to span, so one call can agree with several. "
            f"Each disagreement figure shows a call more than {CLEAR_TOLS * TOL_SEC:g} s from the "
            f"other detector's nearest call where one exists, so it shows a call the other did "
            f"not make rather than a timing split. Within that, the figure shows the call with "
            f"the median participant count of its kind among calls at least {EDGE_SEC:g} s inside "
            f"their window, so the window's edge is not in the picture, preferring a recording "
            f"no earlier figure shows. Participants are counted the review tool's way: "
            f"{html.escape(rule)}. Each window shows "
            f"{EXAMPLE_HALF_SEC['fast']:g} s either side of a fast call and "
            f"{EXAMPLE_HALF_SEC['slow']:g} s either side of a slow or combined one, enough for "
            f"several events of context. In each raster the rows are cells sorted by their event "
            f"count in the window shown, busiest at the top; cells with no event in the window "
            f"sit at the bottom.</p>")
        for s in STREAMS:
            ex = exs["streams"].get(s)
            if not ex:
                continue
            if ex["leader"] is None:
                parts.append(f"<h3>{s.capitalize()} stream</h3><p class='muted'>No row meets the "
                             f"leader rule.</p>")
                continue
            parts.append(f"<h3>{s.capitalize()} stream: {html.escape(ex['leader'])} against "
                         f"{html.escape(ex['ref'])}</h3>")
            lo_, ro_ = ex["totals"]["leader_only"], ex["totals"]["ref_only"]
            fl = ex.get("at_floor", {})
            claim = (f"On these recordings the leader makes {n_of(lo_, 'call')} CoactDetect does "
                     f"not, and CoactDetect makes {n_of(ro_, 'call')} the leader does not; "
                     f"{n_of(ex['totals']['agree'], 'call')} of the leader's are shared.")
            if lo_ and fl.get("leader_only", lo_) < lo_:
                claim += (f" Only {fl['leader_only']} of the leader's {n_of(lo_, 'call')} "
                          f"reach their window's event floor, the minimum CoactDetect runs at.")
            parts.append(f"<p>{claim}</p>")
            groups = list(ex["hours"])
            tot_h = sum(ex["hours"].values())
            head = ("<tr><th>kind (whose calls)</th><th class='num'>all groups</th>"
                    "<th class='num'>reach the event floor</th>"
                    + "".join(f"<th class='num'>{g_}</th>" for g_ in groups) + "</tr>")
            rows = []
            for kind in ("agree", "leader_only", "ref_only"):
                cells = "".join(
                    f"<td class='wrapn'>{n_of(ex['counts'][kind][g_], 'call')}<br>"
                    f"<span class='muted'>{ex['counts'][kind][g_] / ex['hours'][g_]:.1f} calls "
                    f"per baseline hour</span></td>" for g_ in groups)
                rows.append(f"<tr><td>{EX_HEAD[kind]}</td><td class='wrapn'>"
                            f"{n_of(ex['totals'][kind], 'call')}<br><span class='muted'>"
                            f"{ex['totals'][kind] / tot_h:.1f} calls per baseline hour</span>"
                            f"</td><td class='n'>{n_of(fl.get(kind, 0), 'call')}</td>{cells}</tr>")
            hrs = ", ".join(f"{g_} {ex['hours'][g_]:.1f} h" for g_ in groups)
            m = ex["many"]
            gp = ex.get("gaps", {})
            gap_txt = " ".join(
                f"Of {who} {n_of(sum(b.values()), 'call')} the other lacks, {b['near']} "
                f"{'lies' if b['near'] == 1 else 'lie'} within {2 * TOL_SEC:g} s of the other's "
                f"nearest call, {b['mid']} within {2 * TOL_SEC:g} to {4 * TOL_SEC:g} s, and "
                f"{b['far'] + b['none']} further or on a recording where the other made no call."
                for who, b in (("the leader's", gp.get("leader_only")),
                               ("CoactDetect's", gp.get("ref_only"))) if b and sum(b.values()))
            parts.append(tbl(
                f"<b>Table {tno}.</b> The {s} stream: calls on baseline windows by kind and group "
                f"({hrs} of baseline). \"Reach the event floor\" counts the calls whose "
                f"participants reach their window's own floor (ADR-0008). "
                f"{n_of(m['leader'], 'call')} of the leader's and {n_of(m['ref'], 'call')} of "
                f"CoactDetect's overlap two or more of the other's calls, so a merge of two "
                f"events into one could be hiding there. {gap_txt}", head + "".join(rows),
                cue=True))
            tno += 1
            lane = [f"<i>leader</i>: {html.escape(ex['lanes'][0][1])}"]
            if ex["runner"]:
                lane.append(f"<i>runner-up</i>: {html.escape(ex['lanes'][1][1])}")
            lane.append(f"<i>CoactDetect</i>: {html.escape(ex['lanes'][-1][1])}")
            parts.append(f"<p class='muted'>Lanes in every figure below, top down under the ▼ "
                         f"lane: {'; '.join(lane)}.</p>")
            for f in ex["figures"]:
                what = EX_TEXT[f["kind"]].format(L=html.escape(ex["leader"]),
                                                 R=html.escape(ex["ref"]))
                c = f["call"]
                if c is None:
                    parts.append(f"<p class='muted'>{what}: no call of this kind lies at least "
                                 f"{EDGE_SEC:g} s inside a baseline window "
                                 f"({n_of(f['pool'], 'call')} in all).</p>")
                    continue
                t = float(c["onset_sec"])
                if f["pool"] == 1:
                    pool = "the only call of its kind"
                else:
                    pool = (f"one of {'only ' if f['pool'] <= 3 else ''}"
                            f"{n_of(f['pool'], 'call')} of its kind, from "
                            f"{n_of(f['recordings'], 'recording')} "
                            f"({n_of(f['inner'], 'call')} away from window edges)")
                gap = ""
                if f["kind"] != "agree":
                    other = "CoactDetect's" if f["kind"] == "leader_only" else "the leader's"
                    nobody = "CoactDetect" if f["kind"] == "leader_only" else "The leader"
                    gap = (f" The nearest of {other} calls on this recording is "
                           f"{gap_words(f['gap'])} away." if f.get("gap") is not None else
                           f" {nobody} made no call on this recording and stream.")
                shown = (f"shown from {time_label(round(f['ext'][0]))} to "
                         f"{time_label(round(f['ext'][1]))}"
                         + (" (cut at the baseline window's edge)" if any(f.get("cut", ())) else "")
                         if f.get("ext") else "")
                fl_txt = (f" (its window's event floor is {n_of(int(float(f['floor'])), 'ROI')})"
                          if f.get("floor") not in (None, "") else "")
                where = ("" if s in VIEWER_STREAMS else
                         "; no viewer link, as the viewer has no combined stream")
                near = ""
                if f["kind"] != "agree" and f.get("gap") is not None \
                        and f["gap"] <= CLEAR_TOLS * TOL_SEC:
                    near = (f" This is a near-miss, not a clear disagreement: no call of its kind "
                            f"lies both more than {CLEAR_TOLS * TOL_SEC:g} s from the other's "
                            f"nearest call and away from the window edges.")
                cap = (f"<b>Figure {fig_no}.</b> {what}. Recording "
                       f"{vlink(c['slice_id'], s, c['slice_id'])} "
                       f"({html.escape(c['group'])}{where}), {s} stream: the call marked ▼, at "
                       f"{time_label(round(t))}, with "
                       f"{n_of(int(float(c['participants'] or 0)), 'participating ROI')}"
                       f"{fl_txt}; {pool}; {shown}.{gap}{near}")
                if f["png"]:
                    img = f"<img class='ex' src='{f['png']}' alt='Figure {fig_no}: {what}'>"
                    if s in VIEWER_STREAMS:
                        img = (f"<a href='{viewer_href(c['slice_id'], s)}' "
                               f"target='{VIEWER_TAB}'>{img}</a>")
                    parts.append(f"<figure class='wide'><p class='scrollcue'>Scroll the figure "
                                 f"sideways →</p><div class='tablewrap'>{img}</div>"
                                 f"<figcaption>{cap}</figcaption></figure>")
                else:
                    parts.append(f"<p class='bad'>Figure {fig_no} did not render (no Playwright "
                                 f"chromium?).</p><p>{cap}</p>")
                fig_no += 1
            notes = []
            if ex["ref_marks"]:
                notes.append(f"{html.escape(ex['ref'])} is itself on a search limit: "
                             + "; ".join(html.escape(m) for m in ex["ref_marks"]) + ".")
            for before, head_ in ((True, f"Passed over for the leader, from the top of Figure 1"
                                         f"{'abc'[STREAMS.index(s)]}"),
                                  (False, "Passed over for the runner-up")):
                ps = [p for p in ex["passed"] if p.get("before_leader", True) == before]
                if ps:
                    notes.append(f"{head_}: " + "; ".join(
                        f"{html.escape(p['label'])} — {html.escape(p['why'])}" for p in ps) + ".")
            if ex.get("level", 0) > 1:
                k_ = ex["level"] - 1
                notes.append(f"The leader was chosen by the rule among rows the leaderboard "
                             f"cannot separate: {n_of(k_, 'other row')} "
                             f"{'sits' if k_ == 1 else 'sit'} within {NOISE_UNIT:g} F1 of the top "
                             f"unflagged row on this stream.")
            if notes:
                parts.append(f"<details><summary>How the {s} leader was chosen</summary>"
                             + "".join(f"<p class='muted'>{x}</p>" for x in notes)
                             + "</details>")
    # 3. rasters -----------------------------------------------------------------------------
    parts.append("<h2 id='rasters'>3. Rasters with detection</h2>")
    parts.append("<p>The recording links below open the viewer as described in "
                 "<a href='#viewer-setup'>the box in section 2</a>; the review pages open "
                 "directly and carry every stream, combined included.</p>")
    if pages:
        by = defaultdict(dict)
        for p in pages:
            stem = Path(p).stem
            g_, rest = stem.split("_", 1)
            t_, s_ = rest.rsplit("_", 1)
            by[(g_, t_)][s_] = p
        treatments = sorted({t_ for _, t_ in by})
        head = ("<tr><th>group</th>" + "".join(f"<th>first treatment {html.escape(t_)}</th>"
                                               for t_ in treatments) + "</tr>")
        rows = []
        for g_ in in_group_order({g_ for g_, _ in by}):
            cells = "".join(
                "<td>" + (" · ".join(f"<a href='{html.escape(by[(g_, t_)][s_])}'>{s_}</a>"
                                     for s_ in STREAMS if s_ in by.get((g_, t_), {})) or "—")
                + "</td>" for t_ in treatments)
            rows.append(f"<tr><td>{g_}</td>{cells}</tr>")
        parts.append(tbl(
            f"<b>Table {tno}.</b> The night's {n_of(len(pages), 'review page')}, one per group, "
            f"first treatment and stream. Each stacks its recordings, every one aligned at the "
            f"end of its own baseline, with every detector's calls in lanes above the raster.",
            head + "".join(rows), cue=True))
        tno += 1
    grouped = defaultdict(list)
    for r in recs:
        grouped[(r["group"], r["first"] or "—")].append(r)
    rows = []
    for (g_, t_), members in sorted(grouped.items(), key=lambda kv: (group_key(kv[0][0]),
                                                                        kv[0][1])):
        chips = " · ".join(
            f"<span class='chips'><code>{html.escape(r['slice_id'])}</code> "
            + " ".join(vlink(r["slice_id"], s_, s_) for s_ in r["streams"]) + "</span>"
            for r in members)
        rows.append(f"<tr><td>{g_}</td><td>{html.escape(t_)}</td><td class='n'>"
                    f"{n_of(len(members), 'recording')}</td><td>{chips}</td></tr>")
    parts.append(f"<details><summary>Every recording, one viewer link per stream the viewer "
                 f"opens ({n_of(len(recs), 'recording')})</summary>" + tbl(
                     f"<b>Table {tno}.</b> Every recording the night's detection ran on, by group "
                     f"and first treatment. Combined is named without a link: the viewer has no "
                     f"combined stream.", "<tr><th>group</th><th>first treatment</th>"
                     f"<th>count</th><th>recordings</th></tr>{''.join(rows)}", cue=True)
                 + "</details>")
    # terms ----------------------------------------------------------------------------------
    parts.append(TERMS)
    return ("<!doctype html>\n<html lang='en'>\n<head>\n"
            "<meta charset='utf-8'><title>Full-panel night briefing</title>\n"
            "<meta name='viewport' content='width=device-width, initial-scale=1'>\n"
            "<style>" + CSS + "</style>\n</head>\n<body>"
            "<div class='wrap'>" + "\n".join(parts) + "</div></body></html>\n")


def _participants_rule() -> str:
    from detect_with_floors import PARTICIPANTS_RULE
    return PARTICIPANTS_RULE


TERMS = """<h2 id='terms'>Terms</h2><dl class='terms'>
<dt>ADR</dt><dd>Architecture decision record, <code>docs/adr/</code>. ADR-0010 is the one this
night ran under; ADR-0006 rules on decoys; ADR-0008 sets the event floor.</dd>
<dt>full panel</dt><dd>Every coded detector, searched, and the four learned families ADR-0010
names (chorus_norm, chorus_gain_norm, line and tube), each with and without participation, trained
on one night: 8 learned models.</dd>
<dt>stream</dt><dd>Which events a detector reads: <i>fast</i>, <i>slow</i>, or <i>combined</i>
(both).</dd>
<dt>bench</dt><dd>The simulator that plants coordinated events at known times into recordings
with a steady random background, so a call can be scored against the truth.</dd>
<dt>new bench</dt><dd>Planted events spaced as measured in real recordings (ADR-0010).</dd>
<dt>old bench</dt><dd>Planted events at least 120 s apart, the spacing used before ADR-0010.</dd>
<dt>ORX-spaced bench</dt><dd>The new bench with each stream's event spacing taken from the ORX
recordings alone (ADR-0010 ruling 1).</dd>
<dt>background</dt><dd>The steady random event rate of a bench recording: <i>quiet</i> or
<i>busy</i>, the 25th and 75th percentiles over real recordings of the per-cell baseline
background rate, with the coordinated share subtracted.</dd>
<dt>simulation seed</dt><dd>One draw of the bench: one quiet and one busy recording. Distinct from
a training run.</dd>
<dt>training run</dt><dd>One of a learned model's five fits, each from its own starting seed,
numbered 1 to 5 here; run 1 is the run notes' seed 0.</dd>
<dt>held-out F1</dt><dd>A training run's F1 on bench recordings it was not trained on, the number
the pick is made by.</dd>
<dt>F1</dt><dd>The harmonic mean of precision (the share of calls on a planted event) and recall
(the share of planted events called).</dd>
<dt>decoy</dt><dd>A planted look-alike event (<code>docs/GLOSSARY.md</code> calls it a
distractor). A decoy is coordination by construction, so ADR-0006 rules that a call on one is not
a false alarm; the bench still scores it as one until its objective is changed, hence F1 without
decoys beside F1.</dd>
<dt>ΔF1</dt><dd>A row's F1 minus CoactDetect's at its shipped setting, on the same seeds,
averaged over seeds.</dd>
<dt>the search</dt><dd>The night's automatic search over each coded detector's settings.</dd>
<dt>shipped</dt><dd>The setting in a coded detector's code before this night.</dd>
<dt>proposal</dt><dd>The setting the night's search found best, when it was not the shipped one.
A detector with no proposal row had none in the scored file.</dd>
<dt>starting point (untuned)</dt><dd>The count rule's first setting, set on 2026-09-26; it ships
nowhere, though the count run's own files call it "shipped".</dd>
<dt>pick</dt><dd>The one of a learned model's training runs with the best held-out F1 among those
within CoactDetect's no-coordination budget.</dd>
<dt>no pick</dt><dd>A model with no training run inside that budget: its best run is shown as a
comparator only.</dd>
<dt>budget</dt><dd>A limit a row must stay within to count: calls per hour on the no-coordination
test (a recording with nothing planted), calls per minute inside the elevated-rate test's stretch
and per hour outside it, and the precision swing between backgrounds. Coded detectors have their
own limits per stream; learned models are held to CoactDetect's.</dd>
<dt>search limit (†)</dt><dd>The search found its best at a value that turns the setting off
(reported as a finding, ADR-0010 ruling 5), or stopped at the end of what it could test: its
grid's edge, its extension cap, the setting's own limit (the count offset k cannot go below 0,
the floor itself), or a ruled context limit. Such a setting is not bracketed, which ADR-0010 part
1 requires of a final setting, and the search's own rule marks it not adoptable.</dd>
<dt>guard</dt><dd>A detector setting: the time just around the moment under test that is left
out of the background estimate, so an event cannot raise the threshold it has to clear. A guard of
0 s turns it off.</dd>
<dt>merge gap</dt><dd>Calls closer than this are merged into one; "none" means no merging.</dd>
<dt>context window</dt><dd>The stretch of time a detector compares a moment with; ADR-0010 ruling
7 sets 20 s as the shortest and ADR-0009 decision 5 caps it at 120 s.</dd>
<dt>extension cap</dt><dd>The search widens a setting's grid when the best value is at its end,
up to a fixed number of times; the cap is that number.</dd>
<dt>unflagged</dt><dd>Within every budget in force and not on a search limit.</dd>
<dt>level</dt><dd>Within 0.01 F1 of each other: a unit borrowed from ADR-0010 part 1, narrower
than this page's paired intervals.</dd>
<dt>merged calls</dt><dd>Calls whose span covers two or more scored planted events (a planted
event under the floor is not scored), summed over the seeds and both backgrounds (ADR-0010 part
3).</dd>
<dt>leader, runner-up</dt><dd>In section 2, the first and second rows in Figure 1's order that
meet the examples' rule.</dd>
<dt>baseline window</dt><dd>The scored part of a recording's pre-treatment period.</dd>
<dt>review pages</dt><dd>The night's raster pages, one per group, first treatment and stream,
linked in section 3.</dd>
<dt>event floor</dt><dd>ADR-0008: for each recording window, the larger of 3 ROIs and the
smallest co-active count the window's own rigid-shift null (every cell's events shifted together
in time) reaches at most once an hour.</dd>
<dt>floor variant</dt><dd>For the four detectors that ran on the real recordings and take the
floor as their minimum (ADR-0010 part 6), the run at the window's own floor or at the baseline's;
the examples use the window's own. The count rule takes the floor too, but did not run there.</dd>
<dt>participants</dt><dd>The cells with an onset around a call, counted the same way for every
detector.</dd>
<dt>span</dt><dd>A call's extent in time, from its onset to its onset plus its width.</dd>
<dt>ROI</dt><dd>Region of interest: one cell; a raster row shows its events.</dd>
<dt>SCE</dt><dd>Synchronous calcium event.</dd>
<dt>EDT</dt><dd>Eastern daylight time, the clock every time on this page is given in.</dd></dl>"""


def _clean(out: Path) -> None:
    """Remove this builder's own earlier outputs, and only those, so no figure from a previous
    build sits beside the page."""
    for pat in ("example_*.png", "figure1_*.svg"):
        for p in out.glob(pat):
            p.unlink()


def main(argv=None) -> int:
    from bugarach.paths import darkroom, unresolved_message

    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("--night", type=Path, default=None,
                    help=f"the night's darkroom folder (default <darkroom>/{NIGHT_NAME})")
    ap.add_argument("--out", type=Path, default=None, help="default: <night>/briefing")
    ap.add_argument("--also", type=Path, default=None,
                    help="a second copy of the simulated half only (Figure 1, leaderboard.json)")
    ap.add_argument("--viewer", type=Path, default=REPO / "docs" / "site" / "raster_viewer.html",
                    help="the viewer to copy beside the page (default the site's)")
    ap.add_argument("--no-examples", action="store_true",
                    help="skip the examples, which read the default dataset")
    a = ap.parse_args(argv)
    if a.night is None or a.out is None:
        root = darkroom(create=True)
        if root is None:
            print(unresolved_message(), file=sys.stderr)
            return 2
        a.night = a.night or root / NIGHT_NAME
        a.out = a.out or a.night / "briefing"
    a.out.mkdir(parents=True, exist_ok=True)
    _clean(a.out)
    model = build(a.night)
    model["built"] = house_time(datetime.now(timezone.utc))
    svgs = figure1(model, a.out)
    model["_figure1_svgs"] = [p.read_text(encoding="utf-8") for p in svgs]
    written = list(svgs)
    exs, dataset_name = None, None
    try:
        from bugarach import dataset
        dataset_name = dataset.current_name("default")
    except Exception:          # the name is a courtesy on the page; a missing toml is not fatal
        pass
    if not a.no_examples and (a.night / CALLS).exists():
        exs = examples(model, a.night, a.out)
        written += [a.out / f["png"] for ex in exs["streams"].values()
                    for f in ex.get("figures", []) if f.get("png")]
    recs = recordings(a.night / WINDOWS) if (a.night / WINDOWS).exists() else []
    pages = sorted(os.path.relpath(p, a.out).replace(os.sep, "/")
                   for p in (a.night / PAGES).glob("*.html")) if (a.night / PAGES).exists() else []
    page = render(model, exs, recs, pages, dataset_name=dataset_name,
                  has_results=(a.out / "detections.csv").exists())
    tmp = a.out / "index.html.tmp"
    tmp.write_text(page, encoding="utf-8")
    os.replace(tmp, a.out / "index.html")       # write-then-replace: the darkroom is Dropbox
    model.pop("_figure1_svgs", None)
    model["examples"] = exs
    (a.out / "briefing.json").write_text(json.dumps(model, indent=1, default=str) + "\n",
                                         encoding="utf-8")
    written += [a.out / "index.html", a.out / "briefing.json"]
    if a.viewer.exists():
        shutil.copy2(a.viewer, a.out / "viewer.html")
        written.append(a.out / "viewer.html")
    else:
        print(f"no viewer at {a.viewer}: the recording links will not open", file=sys.stderr)
    if a.also:
        # THE SIMULATION HALF ONLY. The page, its examples and its recording links name real
        # recordings, and nothing derived from real recordings goes into this public repo
        # (FOUNDATIONS §5); the leaderboard is scored on simulated recordings and may.
        a.also.mkdir(parents=True, exist_ok=True)
        for p in svgs:
            shutil.copy2(p, a.also / p.name)
        (a.also / "leaderboard.json").write_text(json.dumps(
            {k: model[k] for k in ("sources", "board", "count_present", "orx", "built")},
            indent=1, default=str) + "\n", encoding="utf-8")
        print(f"wrote the leaderboard (simulated recordings only) to {a.also}")
    for p in written:
        print(f"wrote {p}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
