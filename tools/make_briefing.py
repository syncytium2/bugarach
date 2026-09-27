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
  bench its ``spacing`` names, so its CoactDetect rows never replace the night's. Rerunning this
  tool is the whole of adding them.
* ``065/fresh-orx/candidates.json`` — ADR-0010 ruling 1's check at slow-ORX spacing, summarised in
  one line (how many intervals change side), not shown as a column.
* ``065/review/detect/calls.csv``, ``windows.csv`` and ``results.json`` —
  ``tools/detect_with_floors.py``'s calls on the real recordings, for the examples and the links.
* ``065/review/pages/*.html`` — the group × first treatment × stream raster pages, linked as they
  are.

**The examples read the default dataset** (``dataset.default()``), so they need the person's
confirmation for the session like every other analysis, and they refuse a detection run scored on
a different folder; ``--no-examples`` builds the rest without.

**What it decides: nothing.** The leaderboard orders rows by the paired F1 difference against
CoactDetect's shipped setting on the new bench, and marks what the run's own records mark: a row
over a budget, a proposal on a search limit, a training run with no pick. The order is a reading
of intervals, not a ranking the intervals support (``docs/performance_table.md``).

**What it writes:** ``index.html``, ``briefing.json`` (every number on the page),
``figure1_<stream>.svg``, ``example_*.png``, and ``viewer.html`` (a copy of the site's viewer, so
the recording links open locally). It defaults to the darkroom. ``--also`` copies **only the
simulation half** — Figure 1 and ``leaderboard.json`` — because the page, the examples and the
recording links name real recordings, and nothing derived from real recordings goes into the repo
(FOUNDATIONS §5).
"""
from __future__ import annotations

import argparse
import csv
import html
import json
import math
import os
import shutil
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
from bugarach.groups import GROUP_ORDER, group_key  # noqa: E402
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
ORX = "065/fresh-orx/candidates.json"
CALLS = "065/review/detect/calls.csv"
WINDOWS = "065/review/detect/windows.csv"
RESULTS = "065/review/detect/results.json"
PAGES = "065/review/pages"
HOUSE_TZ = ZoneInfo("America/New_York")      # the house clock for Tony
#: The half-width of an example's window, in seconds, per stream: slow and combined calls last
#: seconds, fast ones a fraction of one. The window is cut at the baseline window's edges.
EXAMPLE_HALF_SEC = {"fast": 45.0, "slow": 120.0, "combined": 120.0}
#: An example call is taken at least this far inside its baseline window, in seconds, so the
#: figure shows the call and not an edge of the analysed time (every call is still counted).
EDGE_SEC = 10.0
#: What each detector is, in a line, for the page's "What is compared" box. The coded lines follow
#: docs/GLOSSARY.md (axis 2); the learned lines follow each model's registry note.
WHAT = {
    "coact": "counts distinct cells with an onset in a short bin and tests the count against a "
             "rolling circular-shift null (coded)",
    "loco": "counts distinct co-active cells and compares them with a rolling percentile "
            "threshold (coded)",
    "sce": "binned SCE: counts co-active cells per bin against a surrogate threshold (coded)",
    "rate": "rate+context: a population-rate excess over a slower context rate (coded)",
    "sync": "SPIKE-synch: the SPIKE-synchronization profile with hysteresis detection (coded)",
    "cicada": "locust: sliding-window coactivity against a per-cell roll null, modified from "
              "CICADA (ADR-0002; coded)",
    "count": "the simple rule, binned: bins onsets and calls a bin whose count of co-active cells "
             "reaches the recording's floor plus an offset k (coded)",
    "count_sliding": "the simple rule, sliding: the same count over sliding windows (coded)",
    "chorus_norm": "a network that encodes each cell's trace, standardised over time, then pools "
                   "across cells (learned)",
    "chorus_gain_norm": "chorus_norm with a learnable vote gain and bias (learned)",
    "line": "a network with two sensors, how much of the field is lit and how tightly, then a "
            "centre-surround in time (learned)",
    "tube": "a network running a centre-surround kernel on the brightness trace, with a "
            "raw-brightness bypass (learned)",
}
PART_NOTE = ("A name ending in <i>_part</i> is the same network with participation added "
             "(ADR-0010 part 5): a bounded vote per cell summed into a count, the recording's "
             "floor as an input, and a membership term in the training loss.")
#: Plain words and units for the search parameters a limit mark names.
PARAM = {"guard_sec": ("guard", "s"), "context_win_sec": ("context window", "s"),
         "context_win": ("context window", "s"), "threshold_pctile": ("threshold", "percentile"),
         "n_synchronous_frames": ("synchronous-frame run", "frames"), "C_min": ("C_min", ""),
         "dt": ("SPIKE-synch bin dt", "s"), "k_offset": ("count offset k", "cells"),
         "merge_gap_sec": ("merge gap", "s"), "bin_width_sec": ("bin width", "s"),
         "bin_sec": ("bin width", "s"), "alpha": ("alpha", ""),
         "int_win_sec": ("integration window", "s")}
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
    if x is None:
        return "—"
    if sign and abs(x) < 0.5 * 10 ** -nd:
        x = 0.0                                   # no "-0.000"
    return f"{x:+.{nd}f}" if sign else f"{x:.{nd}f}"


def _param_value(name: str, v) -> str:
    word, unit = PARAM.get(name, (name, ""))
    if v is None or (isinstance(v, float) and math.isnan(v)):
        return f"{word}: none"
    val = f"{v:g}"
    if unit == "percentile":
        return f"{word} at the {val}th percentile"
    return f"{word} {val}{(' ' + unit) if unit else ''}"


# --------------------------------------------------------------------------------------------
# budgets and limit marks
# --------------------------------------------------------------------------------------------

def budgets_of(bench_mod, det: str, row: dict) -> list[dict]:
    """The budgets a fresh-seed row fails, with value and limit — every budget the search's
    admissibility rule holds (``search_all_settings.make_admissible``; ADR-0010: "within every
    budget"), computed by the final-parameters report's own function so the two reports cannot
    disagree about what a failure is. A detector the bench holds budgets for is held to its own;
    a learned model is held to CoactDetect's. A value that was not measured is kept, as
    ``None``, rather than read as a pass.

    The worker's README counts only the no-coordination budget, the one the training pick uses;
    the page says so, so the difference is visible rather than a contradiction."""
    from make_final_parameters_report import failed, fresh_budgets

    own = det in getattr(bench_mod, "MAX_FALSE_POSITIVES_PER_HOUR", {})
    b = fresh_budgets(bench_mod, det, row, det if own else "coact")
    return [dict(name=k, value=b[k]["value"], limit=b[k]["limit"]) for k in failed(b)]


def budget_words(f: dict) -> str:
    """One failed budget in words, with enough digits that the value visibly passes the limit."""
    from make_final_parameters_report import BUDGET_NAME

    what = BUDGET_NAME.get(f["name"], f["name"])
    unit = BUDGET_UNIT.get(f["name"], "")
    u = f" {unit}" if unit else ""
    if f["value"] is None:
        return f"{what}: not measured (limit {f['limit']:g}{u})"
    return f"{what}: {f['value']:.3f}{u} against a limit of {f['limit']:.3f}{u}"


def limit_marks(meta: dict) -> list[str]:
    """What the search's bracketing record says about a proposal, in words, each with the rule
    that governs it. ADR-0010 ruling 5 covers only a value that switches a setting off; a setting
    stopped at a grid edge or an extension cap is not bracketed, which part 1 requires of a final
    setting. Both make the proposal not adoptable as tuned, and they are said apart."""
    prop = meta.get("proposal") or {}
    br = prop.get("bracketing") or {}
    if prop.get("name") in (None, "shipped"):
        return []
    out, seen = [], set()
    for f in br.get("findings") or []:
        name, kind = f.get("setting"), f.get("kind")
        seen.add(name)
        if kind == "off_limit":
            out.append(f"{_param_value(name, f.get('value'))}, a value that switches it off "
                       f"(ADR-0010 ruling 5: a finding, not a tuned value)")
        elif kind == "cap":
            out.append(f"{_param_value(name, f.get('value'))}, at the search's extension cap, "
                       f"so not bracketed (ADR-0010 part 1)")
    for name, v in (br.get("unbracketed_axes") or {}).items():
        if name in seen:
            continue
        side = "lower" if v.get("side") == "low" else "upper"
        why = {"grid_floor": f"at the grid's {side} edge", "grid_ceiling": f"at the grid's {side} edge",
               "edge": f"at the grid's {side} edge", "cap": "at the search's extension cap",
               "limit": f"at its {side} limit by design"}.get(v.get("reason"), "at a limit")
        note = ""
        if name in ("context_win", "context_win_sec") and v.get("value") == 20.0:
            note = ", the shortest context ruling 7 allows"
        out.append(f"{_param_value(name, v.get('value'))}, {why}{note}, so not bracketed "
                   f"(ADR-0010 part 1)")
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
        pf = (r.get("paired_f1_vs_coact") or {}).get("shipped") or {}
        merged = sum((r.get(reg) or {}).get("merged_calls") or 0
                     for reg in ("baseline_quiet", "baseline_busy"))
        rows[rid] = dict(label=label, setting=setting, family=family, key=key,
                         mid=pf.get("mid"), lo=pf.get("lo"), hi=pf.get("hi"),
                         n_seeds=pf.get("n_seeds"), mean_f1=r.get("mean_f1"),
                         mean_f1_without_decoys=r.get("mean_f1_without_decoys"),
                         merged_calls=merged, null_per_hour=r.get("null_calls_per_hour"),
                         budget_fails=budgets_of(bench_mod, family, r), flags=list(flags),
                         spread=spread)

    dets = list(CODED) + [d for d in meta.get("detectors", {}) if d not in CODED]
    for det in dets:
        if f"{det}:shipped" in res:
            put(f"{det}:shipped", f"{det}:shipped", display_name(det),
                _setting(det, "shipped", bench_mod), det, [])
        if f"{det}:proposal" in res:
            put(f"{det}:proposal", f"{det}:proposal", display_name(det), "proposal", det,
                limit_marks(meta["detectors"].get(det, {})))
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


def _side(v: dict | None) -> str | None:
    if not v or v.get("lo") is None:
        return None
    return "above" if v["lo"] > 0 else "below" if v["hi"] < 0 else "includes zero"


def build(night: Path) -> dict:
    import importlib

    from score_bench_candidates import BENCHES

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
    own = {col: {r["family"] for st in benches.get(col, {}).values() for r in st.values()}
           for col, _, _ in BENCH_COLS}
    extra_files = sorted({p for g in EXTRA_GLOBS for p in night.glob(g)})
    extra = []
    for p in extra_files:
        c = _load(p)
        col = next((b for b, sp, _ in BENCH_COLS if sp == c.get("spacing", "bench")), None)
        if col is None:
            continue
        added = set()
        for s in STREAMS:
            if s in c.get("results", {}):
                for rid, row in bench_rows(c, s, mods[s]).items():
                    if row["family"] not in own[col] and not rid.startswith("learned:"):
                        benches.setdefault(col, {}).setdefault(s, {})[rid] = row
                        extra.append(rid)
                        added.add(row["label"])
        if added:
            sources[col]["extra"].append(dict(path=str(p.relative_to(night)).replace(os.sep, "/"),
                                              written=when(p), rows=sorted(added)))
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
                                same_as=None))

        def order(e):
            mid = (e["per"]["new"] or {}).get("mid")
            return (0, -mid) if mid is not None else (1, 0.0)
        entries.sort(key=order)
        # TWO ROWS WITH THE SAME SCORES TO EVERY DIGIT are one result shown twice (fast LoCo's and
        # CoactDetect's proposals on the 2026-09-25 night). Said beside the row, not left to look
        # like corroboration.
        for i, e in enumerate(entries):
            v = e["per"]["new"]
            for f in entries[:i]:
                w = f["per"]["new"]
                if v and w and e["id"] != "coact:shipped" and f["id"] != "coact:shipped" and all(
                        v[k] == w[k] for k in ("mid", "lo", "hi", "mean_f1")):
                    e["same_as"] = f"{f['label']} · {f['setting']}"
                    break
        board[s] = entries
    model = dict(night=str(night), sources=sources, board=board, count_present=bool(extra),
                 extra_files=[str(p) for p in extra_files])
    model["orx"] = orx_check(night, board, mods)
    return model


def orx_check(night: Path, board: dict, mods: dict) -> dict | None:
    """ADR-0010 ruling 1's check at slow-ORX spacing: how many rows' intervals change side
    against the new bench, and how many cross from one side of zero to the other."""
    c = _load(night / ORX)
    if c is None:
        return None
    changed = crossed = total = 0
    for s in STREAMS:
        if s not in c.get("results", {}):
            continue
        orx = bench_rows(c, s, mods[s])
        for e in board[s]:
            o = orx.get(e["id"])
            a, b = _side(e["per"]["new"]), _side(o)
            if e["id"] == "coact:shipped" or a is None or b is None:
                continue
            total += 1
            if a != b:
                changed += 1
                crossed += {a, b} == {"above", "below"}
    return dict(path=ORX, rows=total, changed=changed, crossed=crossed)


def flagged(e: dict, col: str = "new") -> bool:
    """A row the page would not put forward: over a budget, on a search limit, or no pick."""
    v = e["per"].get(col)
    return bool(v and (v["budget_fails"] or v["flags"]))


def glance(model: dict) -> dict:
    """Per stream and bench: the reference's own F1, how many rows' intervals sit wholly above,
    include zero, or sit wholly below CoactDetect's shipped setting, how many of those above are
    also unflagged, and the top unflagged row. Counted from the rows on the page (CoactDetect's
    shipped row left out), so the summary cannot say what the table does not."""
    out = {}
    for s in STREAMS:
        out[s] = {}
        ref = next((e for e in model["board"][s] if e["id"] == "coact:shipped"), None)
        for col in ("new", "old"):
            rows = [e for e in model["board"][s] if e["per"][col] and e["id"] != "coact:shipped"]
            if not rows:
                continue
            sides = [_side(e["per"][col]) for e in rows]
            clean = [e for e in rows if not flagged(e, col)]
            top = max(clean, key=lambda e: e["per"][col]["mid"]) if clean else None
            others = sorted(e["per"][col]["mean_f1"] for e in rows)
            out[s][col] = dict(
                n=len(rows), above=sides.count("above"), below=sides.count("below"),
                straddle=sides.count("includes zero"),
                above_clean=sum(1 for e, sd in zip(rows, sides) if sd == "above"
                                and not flagged(e, col)),
                top=f"{top['label']} · {setting_words(top)}" if top else None,
                top_mid=top["per"][col]["mid"] if top else None,
                ref_f1=(ref["per"][col] or {}).get("mean_f1") if ref else None,
                others_median_f1=others[len(others) // 2])
    return out


def setting_words(e: dict) -> str:
    """A row's setting as the page says it: shipped, proposal or starting point for a coded
    detector; for a learned model, which of its five training runs was picked."""
    if not e["id"].startswith("learned:"):
        return e["setting"]
    run = e["setting"].rsplit("_seed", 1)[-1]
    nopick = any(f.startswith("no pick") for v in e["per"].values() if v for f in v["flags"])
    n = (e.get("spread") or {}).get("n") or 5
    return f"{'no pick, best' if nopick else 'pick,'} training run {run} of {n}"


def ran_on_real(entry: dict, board: list[dict]) -> str | None:
    """The ``calls.csv`` detector name for a leaderboard row, if the real-data run used exactly
    that setting: one of the six coded detectors at its proposal where the search made one
    (otherwise shipped), and each learned family at its pick (``065/README.md`` step D). ``None``
    for anything the real run did not use, the count rule included."""
    fam, setting = entry["family"], entry["setting"]
    if fam in CODED:
        has_prop = any(e["family"] == fam and e["setting"] == "proposal" for e in board)
        return fam if (setting == "proposal") == has_prop else None
    if entry["id"].startswith("learned:") and not any(
            f.startswith("no pick") for v in entry["per"].values() if v for f in v["flags"]):
        return fam
    return None


# --------------------------------------------------------------------------------------------
# the real-data side: calls, windows, examples
# --------------------------------------------------------------------------------------------

def read_calls(p: Path) -> list[dict]:
    """The night's calls, one variant per detector: ``own_floor`` for the four that take the floor
    as their participation minimum, ``unfloored`` for the rest — the default of
    ``make_group_raster_summary.call_lanes``, which draws the review pages."""
    with p.open(newline="", encoding="utf-8") as fh:
        return [r for r in csv.DictReader(fh) if r.get("variant") in ("own_floor", "unfloored")]


def read_windows(p: Path) -> tuple[dict, dict]:
    """(bounds, hours): each baseline window's (start, end) in seconds by (slice, stream, region),
    and baseline hours per (stream, group), each window counted once."""
    bounds, hours, seen = {}, defaultdict(float), set()
    with p.open(newline="", encoding="utf-8") as fh:
        for r in csv.DictReader(fh):
            if r["window_kind"] != "baseline":
                continue
            key = (r["slice_id"], r["stream"], r["region_idx"])
            bounds[key] = (float(r["win_start"]), float(r["win_end"]))
            if key not in seen:
                seen.add(key)
                hours[(r["stream"], r["group"])] += float(r["hours"])
    return bounds, dict(hours)


def recordings(windows_csv: Path) -> list[dict]:
    """One row per recording: its group and its first treatment (the first treatment window by
    region index, the rule ``detect_with_floors.py`` wrote the windows by), in the house group
    order."""
    rec: dict = {}
    with windows_csv.open(newline="", encoding="utf-8") as fh:
        for r in csv.DictReader(fh):
            d = rec.setdefault(r["slice_id"], dict(slice_id=r["slice_id"], group=r["group"],
                                                   first=None, idx=None, streams=set()))
            d["streams"].add(r["stream"])
            if r["window_kind"] == "treatment":
                i = int(r["region_idx"])
                if d["idx"] is None or i < d["idx"]:
                    d["idx"], d["first"] = i, r["label"]
    out = sorted(rec.values(), key=lambda d: (group_key(d["group"]), d["first"] or "~",
                                               d["slice_id"]))
    for d in out:
        d["streams"] = [s for s in STREAMS if s in d["streams"]]
    return out


def _overlaps(a: dict, others: list[dict], tol: float) -> bool:
    a0, a1 = float(a["onset_sec"]), float(a["onset_sec"]) + float(a["width_sec"] or 0)
    return any(float(b["onset_sec"]) - tol <= a1 and
               float(b["onset_sec"]) + float(b["width_sec"] or 0) + tol >= a0 for b in others)


def classify(calls: list[dict], stream: str, leader: str, ref: str) -> dict:
    """Every baseline-window call of the leader and the reference on one stream, by kind: both
    call it, only the leader does, only the reference does. Two calls agree when their spans come
    within the bench's scoring tolerance of each other (span to span, and one call may agree with
    several), which is looser than the bench's one-to-one match from a planted onset."""
    by = defaultdict(lambda: defaultdict(list))
    for r in calls:
        if r["stream"] == stream and r["window_kind"] == "baseline":
            by[r["slice_id"]][r["detector"]].append(r)
    kinds = {"agree": [], "leader_only": [], "ref_only": []}
    for sid, per in by.items():
        L, R = per.get(leader, []), per.get(ref, [])
        for c in L:
            kinds["agree" if _overlaps(c, R, TOL_SEC) else "leader_only"].append(c)
        for c in R:
            if not _overlaps(c, L, TOL_SEC):
                kinds["ref_only"].append(c)
    return kinds


def _inside(c: dict, bounds: dict) -> bool:
    b = bounds.get((c["slice_id"], c["stream"], c["region_idx"]))
    if b is None:
        return False
    t0, t1 = float(c["onset_sec"]), float(c["onset_sec"]) + float(c["width_sec"] or 0)
    return t0 >= b[0] + EDGE_SEC and t1 <= b[1] - EDGE_SEC


def pick_one(pool: list[dict], bounds: dict, used: set) -> dict | None:
    """The call with the median participant count among the calls at least :data:`EDGE_SEC`
    inside their baseline window, preferring a recording no earlier figure has shown. The page
    says both conditions and prints the pool's size beside the figure."""
    inner = [c for c in pool if _inside(c, bounds)]
    fresh = [c for c in inner if c["slice_id"] not in used] or inner
    if not fresh:
        return None
    fresh.sort(key=lambda c: (int(float(c["participants"] or 0)), c["slice_id"],
                              float(c["onset_sec"])))
    c = fresh[len(fresh) // 2]
    used.add(c["slice_id"])
    return c


def render_example(sl, stream: str, call: dict, lanes_for: dict, names: dict, colors: dict,
                   ext: tuple, dest: Path, stem: str) -> Path | None:
    """One example: a lane marking the call (▼, pointing down), the detectors' lanes, then the
    recording's raster over the window. Drawn through ``ui.diagnostic`` like every other raster
    figure; nothing on the raster."""
    import holoviews as hv
    import panel as pn

    from bugarach.ui.diagnostic import lane_panel, raster_panel
    from make_diagnostic import _render_png

    hv.extension("bokeh")
    W = 1160                                      # fills _render_png's 1180 px page
    big = {"yticks": "13pt", "ylabel": "13pt", "xticks": "13pt", "xlabel": "13pt"}
    st = sl.streams[stream]
    lanes = {d: ([float(r["onset_sec"]) for r in rows], [float(r["width_sec"] or 0) for r in rows])
             for d, rows in lanes_for.items()}
    mark = hv.Scatter(([float(call["onset_sec"])], [0.0]), kdims=["t"], vdims=["mark"]).opts(
        marker="inverted_triangle", size=16, color="#111111", xlim=ext, ylim=(-0.8, 0.8),
        yticks=[(0, "this call")], xaxis=None, width=W, height=46, toolbar=None,
        ylabel="", fontsize=big, show_grid=False)
    lp = lane_panel(lanes, ext=ext, width=W, row_px=34, names=names, colors=colors).opts(
        height=34 * len(lanes) + 30, fontsize=big, toolbar=None)
    rp = raster_panel(st, ext=ext, width=W, height=max(220, min(380, 6 * st.n_rois)),
                      name=stream, mark_px=4.0, ticks="minimal").opts(
        fontsize=big, toolbar=None, xlabel="time in recording")
    with tempfile.TemporaryDirectory() as td:
        tmp = Path(td) / "ex.html"
        pn.Column(*(pn.pane.HoloViews(p, linked_axes=True, margin=0) for p in (mark, lp, rp)),
                  margin=0).save(str(tmp))
        png = dest / f"{stem}.png"
        return png if _render_png(tmp, png, scale=3) else None


#: Okabe–Ito reddish purple and orange: apart from each other and from CoactDetect's lane colour.
LEADER_COLOR, RUNNER_COLOR = "#CC79A7", "#E69F00"


def examples(model: dict, night: Path, dest: Path) -> dict:
    """Per stream: the leader and CoactDetect (at the setting the review run used) on real
    baseline windows — every call counted by kind and group, and one figure per kind."""
    from bugarach import dataset
    from bugarach.io import load_folder
    from make_group_raster_summary import lane_color

    res = _load(night / RESULTS) or {}
    scored = (res.get("dataset") or {}).get("name")
    if scored and scored != dataset.current_name("default"):
        raise SystemExit(f"the night's detection ran on {scored!r}, but the default dataset is "
                         f"{dataset.current_name('default')!r}: refusing to draw one over the other")
    folder = dataset.default()
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        slices = {sl.slice_id: sl for sl in load_folder(folder)}
    calls = read_calls(night / CALLS)
    bounds, hours = read_windows(night / WINDOWS)
    chosen = res.get("chosen") or {}
    out, used = dict(dataset=dataset.stamp(), streams={}), set()
    for s in STREAMS:
        board = model["board"][s]
        ref_which = ((chosen.get(s) or {}).get("detectors", {}).get("coact") or {}).get("which")
        ref_label = f"CoactDetect · {ref_which or 'as run'}"
        top_new = next((e["per"]["new"]["mid"] for e in board if e["per"]["new"]), None)
        passed, leader, runner = [], None, None
        for e in board:
            det = ran_on_real(e, board)
            why = None
            if e["family"] == "coact":
                why = "CoactDetect is the reference"
            elif det is None:
                why = "did not run on the real recordings"
            elif e["per"]["new"] and e["per"]["new"]["budget_fails"]:
                why = "over a budget on the new bench"
            elif e["per"]["new"] and e["per"]["new"]["flags"]:
                why = "its setting sits on a search limit, so it is not adoptable as tuned"
            else:
                k = classify(calls, s, det, "coact")
                if not all(k.values()):
                    why = (f"no disagreement with {ref_label} to show "
                           f"({n_of(len(k['agree']), 'call')} agree, "
                           f"{len(k['leader_only'])} only its own, "
                           f"{len(k['ref_only'])} only CoactDetect's)")
            if why is None:
                if leader is None:
                    leader = (e, det)
                    continue
                runner = (e, det)
                break
            if leader is None:
                passed.append(dict(label=f"{e['label']} · {setting_words(e)}", why=why))
        if leader is None:
            out["streams"][s] = dict(passed=passed, leader=None)
            continue
        (le, ldet) = leader
        kinds = classify(calls, s, ldet, "coact")
        groups = [g for g in GROUP_ORDER if (s, g) in hours]
        table = {k: {g: sum(1 for c in pool if c["group"] == g) for g in groups}
                 for k, pool in kinds.items()}
        show = [(ldet, f"{le['label']} · {setting_words(le)}", LEADER_COLOR)]
        if runner:
            show.append((runner[1], f"{runner[0]['label']} · {setting_words(runner[0])}",
                         RUNNER_COLOR))
        show.append(("coact", ref_label, lane_color("coact")))
        figs = []
        for kind, pool in kinds.items():
            c = pick_one(pool, bounds, used)
            fig = dict(kind=kind, pool=len(pool),
                       inner=sum(1 for x in pool if _inside(x, bounds)), call=c, png=None)
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
                                     and float(r["onset_sec"]) + float(r["width_sec"] or 0)
                                     >= ext[0] and float(r["onset_sec"]) <= ext[1]]
                                 for d, _, _ in show}
                    png = render_example(sl, s, c, lanes_for, {d: n for d, n, _ in show},
                                         {d: col for d, _, col in show}, ext, dest,
                                         f"example_{s}_{kind}")
                    fig.update(png=png.name if png else None, ext=list(ext),
                               cut=(ext[0] > t - half, ext[1] < t + half))
            figs.append(fig)
        out["streams"][s] = dict(
            passed=passed, leader=f"{le['label']} · {setting_words(le)}", leader_det=ldet,
            leader_mid=le["per"]["new"]["mid"], top_mid=top_new, ref=ref_label,
            runner=show[1][1] if runner else None, lanes=[n for _, n, _ in show],
            counts=table, totals={k: len(v) for k, v in kinds.items()},
            hours={g: hours[(s, g)] for g in groups}, figures=figs)
    return out


# --------------------------------------------------------------------------------------------
# rendering
# --------------------------------------------------------------------------------------------

def figure1(model: dict, dest: Path) -> list[Path]:
    """Figure 1, one SVG per stream: every row's paired F1 difference against CoactDetect's
    shipped setting, new bench (filled) above old bench (open), 95% intervals, a grey line joining
    the two centres so the move between benches reads as a line.

    Drawn as SVG by hand: no plotting dependency (matplotlib is not one of this project's), exact
    type sizes (15 px, over the house floor of 11 pt), and the page's own colours in both themes.
    Each stream carries its own axis and legend at the top as well as the bottom, so no row is
    read two thousand pixels from its key. All three share one x-range, so they compare."""
    W, LEFT, RIGHT, ROW = 1000, 330, 30, 30
    vals = [x for s in STREAMS for e in model["board"][s] for v in e["per"].values() if v
            for x in (v["lo"], v["hi"]) if x is not None] + [0.0]
    lo, hi = min(vals), max(vals)
    pad = 0.06 * (hi - lo or 0.1)
    lo, hi = lo - pad, hi + pad
    # Steps whose ticks print exactly at two decimals, so a label never rounds away from its line.
    step = next(st for st in (0.01, 0.02, 0.05, 0.1, 0.2) if (hi - lo) / st <= 10)
    ticks, k = [], int(lo / step) - 1
    while k * step <= hi:
        if k * step >= lo:
            ticks.append(round(k * step, 6))
        k += 1

    def X(v):
        return LEFT + (v - lo) / (hi - lo) * (W - LEFT - RIGHT)

    style = ("<style>.ax{stroke:var(--line,#ccc)} .zero{stroke:var(--fg,#222)} "
             ".t{fill:var(--fg,#222)} .m{fill:var(--muted,#666)} .j{stroke:var(--muted,#999)} "
             ".new{stroke:var(--accent,#0072B2);fill:var(--accent,#0072B2)} "
             ".old{stroke:var(--accent,#0072B2);fill:var(--bg,#fff)} "
             ".badn{stroke:var(--warn,#b35c00);fill:var(--warn,#b35c00)} "
             ".bado{stroke:var(--warn,#b35c00);fill:var(--bg,#fff)}</style>")

    def axis(y, out, labels_below=True):
        for t in ticks:
            out.append(f"<text class='m' x='{X(t):.1f}' y='{y + (20 if labels_below else -8)}' "
                       f"text-anchor='middle'>{'0' if abs(t) < 1e-9 else f'{t:+.2f}'}</text>")

    def legend(y, out):
        items = (("new", "new bench"), ("old", "old bench"),
                 ("badn", "new bench, over a budget"), ("bado", "old bench, over a budget"))
        x = 8
        for cls, text in items:
            out.append(f"<circle class='{cls}' cx='{x + 6}' cy='{y - 5}' r='5' stroke-width='2'/>"
                       f"<text class='t' x='{x + 16}' y='{y}'>{text}</text>")
            x += 16 + 9 * len(text) + 22
        out.append(f"<text class='m' x='8' y='{y + 24}'>† a proposal on a search limit, not "
                   f"adoptable as tuned · the vertical line at 0 is CoactDetect at its shipped "
                   f"setting</text>")

    paths = []
    for s in STREAMS:
        rows = model["board"][s]
        top = 108                     # title, legend, legend note, then the top tick labels
        H = top + ROW * len(rows) + 70
        out = [f"<svg xmlns='http://www.w3.org/2000/svg' width='{W}' height='{H}' "
               f"viewBox='0 0 {W} {H}' font-family='system-ui, sans-serif' font-size='15' "
               f"role='img' aria-label='Figure 1, the {s} stream'>", style]
        out.append(f"<text class='t' x='8' y='16' font-weight='650'>{s} stream · "
                   f"{n_of(len(rows), 'row')}</text>")
        legend(42, out)
        axis(top - 4, out, labels_below=False)
        y = top
        for e in rows:
            cy = y + ROW / 2
            dagger = " †" if any(not f.startswith("no pick") for v in e["per"].values() if v
                                 for f in v["flags"]) else ""
            name = f"{e['label']} · {setting_words(e)}{dagger}"
            out.append(f"<text class='t' x='{LEFT - 10}' y='{cy + 5}' text-anchor='end'>"
                       f"{html.escape(name)}</text>")
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
        out.append(f"<text class='t' x='{(LEFT + W - RIGHT) / 2}' y='{y + 46}' "
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
td.marks { padding-top: 0; }
.bad { color: var(--bad); font-weight: 600; } .warn { color: var(--warn); }
figure { margin: 1.2rem 0 1.8rem; }
figure img.ex { width: 1080px; max-width: none; height: auto; background: #fff;
                border: 1px solid var(--line); box-sizing: border-box; display: block; }
figcaption { color: var(--muted); margin-top: .4rem; }
code { font-family: var(--mono); font-size: .95em; overflow-wrap: anywhere; }
.box { border: 1px solid var(--line); background: var(--card); padding: .8rem 1rem;
       border-radius: 6px; margin: 1rem 0; }
.box ul, .notes { margin: .3rem 0; padding-left: 1.2rem; }
details > summary { cursor: pointer; font-weight: 650; margin: 1rem 0 .4rem; }
.chips a { white-space: nowrap; }
"""


def _marks_html(e: dict) -> str:
    """A row's marks: each bench's budget failures (said once when both benches fail alike), then
    the flags the search or the training pick carries, then an identical-scores note."""
    out = []
    n, o = e["per"].get("new"), e["per"].get("old")
    nf, of = (n or {}).get("budget_fails", []), (o or {}).get("budget_fails", [])
    same = nf and nf == of
    for col, fails in (("both benches", nf if same else []), ("new bench", [] if same else nf),
                       ("old bench", [] if same else of)):
        for f in fails:
            out.append(f"<span class='bad'>Over budget on the {col}: "
                       f"{html.escape(budget_words(f))}</span>")
    first = n or o
    for f in (first or {}).get("flags", []):
        cls = "bad" if f.startswith("no pick") else "warn"
        out.append(f"<span class='{cls}'>{html.escape(f[0].upper() + f[1:])}</span>")
    if e.get("same_as"):
        out.append(f"<span class='muted'>Same scores as {html.escape(e['same_as'])} to every "
                   f"digit on the new bench: one result, shown twice.</span>")
    return "<br>".join(out)


def _setting_cell(e: dict) -> str:
    s = html.escape(setting_words(e))
    sp = e.get("spread")
    if e["id"].startswith("learned:") and sp:
        s += (f"<br><span class='muted'>held-out F1 of the {n_of(sp['n'], 'run')}: "
              f"{sp['lo']:.2f}–{sp['hi']:.2f}</span>")
    return s


def leaderboard_table(model: dict, s: str, tno: int) -> str:
    rows = model["board"][s]
    head = ("<tr><th>#</th><th>detector or model</th><th>setting</th>"
            "<th>new bench ΔF1 [95%]</th><th>new F1 · without decoys</th>"
            "<th>old bench ΔF1 [95%]</th><th>old F1 · without decoys</th>"
            "<th>merged calls, new bench</th></tr>")
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
        mc = (e["per"]["new"] or {}).get("merged_calls")
        cells.append(f"<td class='n'>{n_of(mc, 'call') if mc is not None else '—'}</td>")
        marks = _marks_html(e)
        edge = " style='border-bottom:none'" if marks else ""
        body.append(f"<tr><td class='n'{edge}>{i}</td><td{edge}>{html.escape(e['label'])}</td>"
                    f"<td{edge}>{_setting_cell(e)}</td>"
                    + "".join(c.replace("<td", f"<td{edge}", 1) for c in cells) + "</tr>")
        if marks:
            body.append(f"<tr><td></td><td colspan='7' class='marks'>{marks}</td></tr>")
    if not model["count_present"]:
        body.append("<tr><td class='n'>—</td><td>count (the simple rule)</td><td>—</td>"
                    "<td class='muted' colspan='5'>not scored yet: its results land in "
                    "WSMIP064's count folder, and rerunning this page's builder adds the row."
                    "</td></tr>")
    return (f"<div class='tablewrap'><table><caption><b>Table {tno}.</b> The {s} stream, "
            f"{n_of(len(rows), 'row')}, in Figure 1's order. F1 is the mean over the quiet and "
            f"busy backgrounds; ΔF1 is the mean over simulation seeds of per-seed differences, so "
            f"the F1 columns do not subtract to it exactly.</caption>{head}{''.join(body)}"
            f"</table></div>")


def glance_html(g: dict) -> str:
    head = ("<tr><th>stream</th><th>bench</th><th>CoactDetect shipped, F1</th>"
            "<th>median F1 of the other rows</th><th>interval above zero</th>"
            "<th>… of those, unflagged</th><th>includes zero</th><th>below zero</th>"
            "<th>top unflagged row (ΔF1)</th></tr>")
    body = []
    for s in STREAMS:
        for col in ("new", "old"):
            v = g[s].get(col)
            if not v:
                body.append(f"<tr><td>{s}</td><td>{col}</td><td colspan='7' class='muted'>not "
                            f"scored</td></tr>")
                continue
            top = (f"{html.escape(v['top'])} ({_f(v['top_mid'])})" if v["top"] else "none")
            body.append(f"<tr><td>{s}</td><td>{col}</td><td class='n'>{_f(v['ref_f1'], sign=False)}"
                        f"</td><td class='n'>{_f(v['others_median_f1'], sign=False)}</td>"
                        f"<td class='n'>{n_of(v['above'], 'row')}</td>"
                        f"<td class='n'>{n_of(v['above_clean'], 'row')}</td>"
                        f"<td class='n'>{n_of(v['straddle'], 'row')}</td>"
                        f"<td class='n'>{n_of(v['below'], 'row')}</td><td>{top}</td></tr>")
    return (f"<div class='tablewrap'><table><caption><b>Table 1.</b> At a glance. For each stream "
            f"and bench: CoactDetect's shipped F1, the median F1 of every other row, and how many "
            f"rows have a 95% interval of ΔF1 wholly above zero, one that includes zero, or one "
            f"wholly below zero. \"Unflagged\" means within every budget and not on a search "
            f"limit.</caption>{head}{''.join(body)}</table></div>")


def headline(g: dict) -> str:
    """Two or three sentences of result, each number computed from Table 1's rows."""
    parts = []
    for s in STREAMS:
        n, o = g[s].get("new"), g[s].get("old")
        if not n:
            continue
        txt = (f"<b>{s.capitalize()}:</b> on the new bench {n['above']} of {n_of(n['n'], 'row')} "
               f"sit above CoactDetect's shipped setting ({n['above_clean']} of them unflagged)")
        if o:
            dr = n["ref_f1"] - o["ref_f1"]
            dm = n["others_median_f1"] - o["others_median_f1"]
            txt += (f"; on the old bench, {o['above']} of {o['n']}. From old bench to new, "
                    f"CoactDetect's shipped F1 moves {_f(dr)} ({_f(o['ref_f1'], sign=False)} to "
                    f"{_f(n['ref_f1'], sign=False)}) and the other rows' median F1 moves "
                    f"{_f(dm)} ({_f(o['others_median_f1'], sign=False)} to "
                    f"{_f(n['others_median_f1'], sign=False)})")
        parts.append(txt + ".")
    return ("<div class='box'><p><b>What the new bench against the old bench shows.</b> "
            + " ".join(parts) + " The search's proposals and the learned picks were chosen on "
            "the new bench, so their new-bench numbers favour them; the shipped settings predate "
            "it.</p></div>")


def viewer_href(slice_id: str, stream: str) -> str:
    return f"viewer.html#slice={quote(slice_id)}&stream={quote(stream)}"


EX_TEXT = {"agree": "{L} and {R} both call it",
           "leader_only": "{L} calls it; {R} does not",
           "ref_only": "{R} calls it; {L} does not"}
EX_HEAD = {"agree": "both call it", "leader_only": "only the leader", "ref_only": "only CoactDetect"}


def viewer_box(dataset_name: str | None, has_results: bool) -> str:
    return (
        "<div class='box' id='viewer-setup'><b>Opening a recording in the viewer.</b> Every "
        "recording link on this page opens the site's viewer, copied beside this page, at that "
        "recording and stream, with the night's calls in lanes above the raster (one lane per "
        "detector and variant; hover a call for its participants and floors). The viewer reads "
        "only files you open, and nothing leaves the machine. The first time:<ul>"
        f"<li>click <i>Choose folder…</i> and pick the export folder "
        f"<code>{html.escape(dataset_name or 'of the default dataset')}</code> "
        f"(<code>python -m bugarach.dataset</code> prints where it is on this machine);</li>"
        "<li>click <i>Open results (detections.csv)…</i> and pick "
        f"{'the <code>detections.csv</code> beside this page' if has_results else 'the night’s detections.csv'}."
        "</li></ul>After that, a link needs one click on <i>Reopen</i> and the browser's "
        "permission prompt, and you pick the results file again each visit. The link opens the "
        "recording at its start; the caption gives the time of the call.</div>")


def render(model: dict, exs: dict | None, recs: list[dict], pages: list[str], *,
           dataset_name: str | None, has_results: bool) -> str:
    src = model["sources"]
    g = glance(model)
    parts = []
    parts.append(
        "<h1>Full-panel night briefing</h1><p class='byline'>The night of 2026-09-25, run under "
        "ADR-0010, the record that moved the bench to event spacing measured in real recordings. "
        "Scored on fresh simulation seeds, ones neither the search nor the training saw. Built "
        f"{html.escape(model['built'])}. Every number is read from the night's files; nothing "
        "here is adopted.</p>")
    parts.append("<nav><a href='#leaderboard'>1. Leaderboard</a><a href='#examples'>2. Examples"
                 "</a><a href='#rasters'>3. Rasters</a><a href='#terms'>Terms</a></nav>")
    # 1. leaderboard -------------------------------------------------------------------------
    parts.append("<h2 id='leaderboard'>1. Leaderboard: every detector and learned pick against "
                 "CoactDetect</h2>")
    parts.append(headline(g))
    for s, svg in zip(STREAMS, model.get("_figure1_svgs", [])):
        cap = (f"<b>Figure 1{'abc'[STREAMS.index(s)]}, the {s} stream.</b> Each row's paired F1 "
               f"difference (ΔF1) against CoactDetect at its shipped setting, the vertical line "
               f"at 0. Filled marks are the new bench, open marks the old, bars the 95% "
               f"interval, and the grey line joins the two. Orange: over a budget on that bench. "
               f"All three panels share one x-range.") if s == STREAMS[0] else (
               f"<b>Figure 1{'abc'[STREAMS.index(s)]}, the {s} stream.</b> As Figure 1a.")
        parts.append(f"<figure><div class='tablewrap'>{svg}</div><figcaption>{cap}"
                     f"</figcaption></figure>")
    parts.append(glance_html(g))
    seeds = []
    for col in ("new", "old"):
        s_ = src[col]
        name = "new bench" if col == "new" else "old bench"
        if s_["present"]:
            ex = "".join(f"; the {', '.join(x['rows'])} rows were scored in a later run "
                         f"(<code>{html.escape(x['path'])}</code>, {html.escape(x['written'] or '')})"
                         for x in s_["extra"])
            seeds.append(f"<li>The {name} was scored {html.escape(s_['written'] or '')}, on "
                         + ", ".join(f"{v} {k}" for k, v in s_["seeds"].items())
                         + f" simulation seeds, each one recording per background{ex}.</li>")
        else:
            seeds.append(f"<li class='bad'>The {name} is not scored yet "
                         f"(<code>{html.escape(s_['path'])}</code> is missing).</li>")
    orx = model.get("orx")
    orx_li = (f"<li>ADR-0010 ruling 1's check, the same rows on a bench spaced like the slow ORX "
              f"recordings, was scored too (<code>{orx['path']}</code>): against the new bench, "
              f"{n_of(orx['changed'], 'interval')} of {orx['rows']} change side, and "
              f"{orx['crossed']} cross from above zero to below or back. It is not shown here."
              f"</li>") if orx else ""
    parts.append(
        "<div class='box'><b>How to read it.</b><ul>"
        "<li>A <b>row</b> is one detector at one setting, or one learned model's picked training "
        "run. Each is scored on the same simulated recordings as CoactDetect at its shipped "
        "setting, so ΔF1 is paired: the mean over simulation seeds of (row F1 − CoactDetect F1), "
        "with a 95% percentile-bootstrap interval over seeds (2,000 draws). The interval covers "
        "simulation seeds only, not the choice among a learned model's five training runs, and "
        "each interval stands alone, uncorrected for the many rows.</li>"
        "<li><b>The order is a reading of intervals, not a ranking.</b> ADR-0010 counts 0.01 F1 "
        "as one noise unit, the draw-to-draw spread; rows closer than that are level.</li>"
        "<li><b>The two benches score the same rows.</b> The new bench plants coordinated events "
        "at the spacing measured in real recordings; the old bench plants them at least 120 s "
        "apart, as before ADR-0010. Proposals and learned picks were chosen on the new bench; "
        "the six detectors' shipped settings date from before it, and the count rule's starting "
        "point was set on 2026-09-26 and is untuned. ADR-0010 ruling 2 retired the old bench as "
        "a reference: it is scored here because Tony asked to see new against old on "
        "2026-09-26, and it decides nothing.</li>"
        "<li><b>F1 counts calls on decoys as false alarms.</b> ADR-0006 rules that a call on a "
        "decoy is coordination by construction, so the tables give F1 without decoy calls "
        "beside it. On slow, where most rows score about 0.99 without decoys, the spread is "
        "mostly how each row handles decoys.</li>"
        "<li><b>Budgets.</b> A row is marked over budget if it fails any budget the search's "
        "admissibility rule holds: the no-coordination recording, the elevated-rate test inside "
        "and outside its stretch, and the precision swing between backgrounds. The close-events "
        "test is not run on fresh seeds. The worker's README counts only the no-coordination "
        "budget, the one the training pick uses, which is why it names one row where this page "
        "marks more.</li>"
        + "".join(seeds) + orx_li + "</ul></div>")
    fams = []
    for s in STREAMS:
        fams += [e["family"] for e in model["board"][s]]
    fams = list(dict.fromkeys(f.removesuffix("_part") for f in fams))
    parts.append("<div class='box'><b>What is compared.</b><ul>"
                 + "".join(f"<li><b>{html.escape(display_name(f))}</b>: {WHAT[f]}.</li>"
                           for f in fams if f in WHAT)
                 + f"</ul>{PART_NOTE}</div>")
    parts.append("<details><summary>Tables 2–4: every number behind Figure 1, with each row's "
                 "budget and limit marks</summary>")
    for i, s in enumerate(STREAMS, 2):
        parts.append(f"<h3>{s.capitalize()} stream</h3>" + leaderboard_table(model, s, i))
    parts.append("</details>")
    # 2. examples ----------------------------------------------------------------------------
    parts.append("<h2 id='examples'>2. Examples on real recordings</h2>")
    parts.append(viewer_box(dataset_name, has_results))
    fig_no = 2
    if exs is None:
        parts.append("<p class='bad'>Not built: the examples read the default dataset, and this "
                     "build ran without it (<code>--no-examples</code>, or the dataset was not "
                     "confirmed for the session).</p>")
    else:
        parts.append(
            "<p>For each stream, the <b>leader</b> is the highest row in Figure 1 that ran on the "
            "real recordings, is within every budget, is not on a search limit, and disagrees with "
            "CoactDetect at least once each way. Every row passed over is named with its reason. "
            "It is set against CoactDetect <i>at the setting the night's detection ran</i>, its "
            "proposal, which is not the leaderboard's reference and is itself on a search limit. "
            f"Only baseline windows are used. Two calls agree when their spans come within "
            f"{TOL_SEC:g} s of each other (the bench's scoring tolerance, here applied span to "
            f"span, so one call can agree with several). Each figure shows one call: the one with "
            f"the median participant count of its kind among calls at least {EDGE_SEC:g} s inside "
            f"their window, preferring a recording no earlier figure shows. Participants are "
            f"counted the review tool's way, not the detector's: "
            f"{html.escape(_participants_rule())}.</p>")
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
            if ex["passed"]:
                parts.append("<p class='muted'>Passed over, from the top of Figure 1: "
                             + "; ".join(f"{html.escape(p['label'])} ({html.escape(p['why'])})"
                                         for p in ex["passed"]) + ".</p>")
            lanes = ", ".join(html.escape(x) for x in ex["lanes"])
            parts.append(f"<p class='muted'>Lanes in every figure below: {lanes}"
                         + (" (the runner-up, the next row meeting the rule)" if ex["runner"]
                            else "") + ".</p>")
            groups = list(ex["hours"])
            head = ("<tr><th>kind</th><th>all groups</th>"
                    + "".join(f"<th>{g_}</th>" for g_ in groups) + "</tr>")
            rows = []
            for kind in ("agree", "leader_only", "ref_only"):
                cells = "".join(
                    f"<td class='n'>{n_of(ex['counts'][kind][g_], 'call')}<br>"
                    f"<span class='muted'>{ex['counts'][kind][g_] / ex['hours'][g_]:.1f}/h</span>"
                    f"</td>" for g_ in groups)
                rows.append(f"<tr><td>{EX_HEAD[kind]}</td><td class='n'>"
                            f"{n_of(ex['totals'][kind], 'call')}</td>{cells}</tr>")
            hrs = ", ".join(f"{g_} {ex['hours'][g_]:.1f} h" for g_ in groups)
            parts.append(f"<div class='tablewrap'><table><caption>Calls on baseline windows by "
                         f"kind and group, with the rate per baseline hour ({hrs} of baseline)."
                         f"</caption>{head}{''.join(rows)}</table></div>")
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
                link = viewer_href(c["slice_id"], s)
                one_off = " A one-off: read it as one call, not a pattern." if f["pool"] <= 3 else ""
                shown = (f"shown from {time_label(round(f['ext'][0]))} to "
                         f"{time_label(round(f['ext'][1]))}"
                         + (" (cut at the baseline window's edge)" if any(f.get("cut", ())) else "")
                         if f.get("ext") else "")
                cap = (f"<b>Figure {fig_no}.</b> {what}. Recording "
                       f"<a href='{link}'>{html.escape(c['slice_id'])}</a> "
                       f"({html.escape(c['group'])}), {s} stream: the call marked ▼, at "
                       f"{time_label(round(t))}, with {n_of(int(float(c['participants'] or 0)), 'participating ROI')}; "
                       f"one of {n_of(f['pool'], 'call')} of its kind ({f['inner']} away from "
                       f"window edges); {shown}.{one_off}")
                if f["png"]:
                    parts.append(f"<figure><div class='tablewrap'><a href='{link}'><img class='ex' "
                                 f"src='{f['png']}' alt='Figure {fig_no}: {what}'></a></div>"
                                 f"<figcaption>{cap}</figcaption></figure>")
                else:
                    parts.append(f"<p class='bad'>Figure {fig_no} did not render (no Playwright "
                                 f"chromium?).</p><p>{cap}</p>")
                fig_no += 1
    # 3. rasters -----------------------------------------------------------------------------
    parts.append("<h2 id='rasters'>3. Rasters with detection</h2>")
    parts.append("<p>The recording links below open the viewer as described in "
                 "<a href='#viewer-setup'>the box at the top of section 2</a>.</p>")
    if pages:
        by = defaultdict(dict)
        for p in pages:
            stem = Path(p).stem
            g_, rest = stem.split("_", 1)
            t_, s_ = rest.rsplit("_", 1)
            by[(g_, t_)][s_] = p
        rows = []
        for (g_, t_) in sorted(by, key=lambda k: (group_key(k[0]), k[1])):
            links = " · ".join(f"<a href='{html.escape(by[(g_, t_)][s_])}'>{s_}</a>"
                               for s_ in STREAMS if s_ in by[(g_, t_)])
            rows.append(f"<tr><td>{g_}</td><td>{html.escape(t_)}</td><td>{links}</td></tr>")
        parts.append(f"<p>Table 5 links the night's {n_of(len(pages), 'review page')}, one per "
                     f"group, first treatment and stream. Each stacks its recordings, every one "
                     f"aligned at the end of its own baseline, with every call in lanes above.</p>"
                     f"<div class='tablewrap'><table><caption><b>Table 5.</b> Review pages by "
                     f"group and first treatment.</caption><tr><th>group</th>"
                     f"<th>first treatment</th><th>pages</th></tr>{''.join(rows)}</table></div>")
    grouped = defaultdict(list)
    for r in recs:
        grouped[(r["group"], r["first"] or "—")].append(r)
    rows = []
    for (g_, t_), members in sorted(grouped.items(), key=lambda kv: (group_key(kv[0][0]),
                                                                        kv[0][1])):
        chips = " · ".join(
            f"<span class='chips'><code>{html.escape(r['slice_id'])}</code> "
            + " ".join(f"<a href='{viewer_href(r['slice_id'], s_)}'>{s_}</a>"
                       for s_ in r["streams"]) + "</span>" for r in members)
        rows.append(f"<tr><td>{g_}</td><td>{html.escape(t_)}</td><td class='n'>"
                    f"{n_of(len(members), 'recording')}</td><td>{chips}</td></tr>")
    parts.append(f"<div class='tablewrap'><table><caption><b>Table 6.</b> Every recording the "
                 f"night's detection ran on ({n_of(len(recs), 'recording')}), by group and first "
                 f"treatment, each with a link per stream.</caption><tr><th>group</th>"
                 f"<th>first treatment</th><th>count</th><th>recordings</th></tr>{''.join(rows)}"
                 f"</table></div>")
    # terms ----------------------------------------------------------------------------------
    parts.append(TERMS)
    return ("<!doctype html>\n<html lang='en'>\n<head>\n"
            "<meta charset='utf-8'><title>Full-panel night briefing</title>\n"
            "<meta name='viewport' content='width=device-width, initial-scale=1'>\n"
            "<style>" + CSS + "</style>\n</head>\n<body>"
            "<div class='wrap'>" + "\n".join(parts) + "</div></body></html>\n")


def _participants_rule() -> str:
    try:
        from detect_with_floors import PARTICIPANTS_RULE
        return PARTICIPANTS_RULE
    except Exception:            # the rule is a courtesy line; the page stands without it
        return "ROIs with an onset near the call"


TERMS = """<h2 id='terms'>Terms</h2><table>
<tr><th>ADR</th><td>Architecture decision record, <code>docs/adr/</code>. ADR-0010 is the one
this night ran under; ADR-0006 rules on decoys.</td></tr>
<tr><th>stream</th><td>Which events a detector reads: <i>fast</i>, <i>slow</i>, or
<i>combined</i> (both).</td></tr>
<tr><th>bench</th><td>The simulator that plants coordinated events at known times into
recordings with a steady random background, so a call can be scored against the truth.</td></tr>
<tr><th>new bench</th><td>Planted events spaced as measured in real recordings (ADR-0010).</td></tr>
<tr><th>old bench</th><td>Planted events at least 120 s apart, the spacing used before
ADR-0010.</td></tr>
<tr><th>background</th><td>The steady random event rate of a bench recording: <i>quiet</i> or
<i>busy</i>, the 25th and 75th percentiles of real baseline rates.</td></tr>
<tr><th>simulation seed</th><td>One draw of the bench: one quiet and one busy recording.
Distinct from a training run.</td></tr>
<tr><th>training run</th><td>One of the five fits of a learned model, each from its own starting
seed.</td></tr>
<tr><th>F1</th><td>The harmonic mean of precision (the share of calls on a planted event) and
recall (the share of planted events called).</td></tr>
<tr><th>decoy</th><td>A planted look-alike the bench counts as a false alarm when called;
ADR-0006 rules it coordination by construction, hence F1 without decoys.</td></tr>
<tr><th>ΔF1</th><td>A row's F1 minus CoactDetect's at its shipped setting, on the same seeds,
averaged over seeds.</td></tr>
<tr><th>shipped</th><td>The setting a coded detector ships with.</td></tr>
<tr><th>proposal</th><td>The setting the night's search proposed. A detector whose search
proposed nothing has no proposal row.</td></tr>
<tr><th>starting point (untuned)</th><td>The count rule's first setting, set on 2026-09-26;
it ships nowhere.</td></tr>
<tr><th>pick</th><td>The one of a learned model's five training runs with the best held-out F1
among those within CoactDetect's no-coordination budget.</td></tr>
<tr><th>no pick, best training run</th><td>A family with no run inside that budget: its best run
is shown as a comparator only.</td></tr>
<tr><th>budget</th><td>A limit a row must stay within to count: calls per hour on the
no-coordination recording (nothing planted), calls per minute inside the elevated-rate test's
stretch and per hour outside it, and the precision swing between backgrounds. The coded
detectors have their own limits (<code>src/bugarach/bench*.py</code>); learned models are held to
CoactDetect's.</td></tr>
<tr><th>search limit (†)</th><td>A proposal whose setting is a value that switches the setting
off (ADR-0010 ruling 5), or that stopped at a grid edge or extension cap and so is not bracketed
(ADR-0010 part 1). Either way it is not adoptable as tuned.</td></tr>
<tr><th>merged calls</th><td>Calls whose span covers two or more planted events, summed over the
seeds and both backgrounds (ADR-0010 part 3).</td></tr>
<tr><th>baseline window</th><td>The scored part of a recording's pre-treatment period.</td></tr>
<tr><th>floor</th><td>A recording window's own participation floor (ADR-0008): the smallest
co-active cell count that is not chance there.</td></tr>
<tr><th>participants</th><td>The cells with an onset around a call, counted the same way for every
detector.</td></tr>
<tr><th>ROI</th><td>Region of interest: one cell's trace.</td></tr>
<tr><th>EDT</th><td>Eastern daylight time, UTC − 4 h.</td></tr></table>"""


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
