#!/usr/bin/env python3
"""One page that briefs a night's run from the top down: leaderboard, examples, rasters.

    python tools/make_briefing.py [--night <darkroom night folder>] [--out <folder>] \
        [--also docs/learned/runs/<name>] [--no-examples]

Tony, 2026-09-26: *"I need an html I can click on and get a full briefing. Top down performance
leader board first then examples. In this case I need to see the new bench vs the old bench for
comparison. Then I need easy access to the zoomable rasters with detection."*

**What it reads**, all under ``--night`` (default ``<darkroom>/2026-09-26-full-panel``), exactly as
the worker sessions wrote it:

* ``065/fresh-realistic/candidates.json`` — the fresh-seed scoring on the **new bench** (ADR-0010's
  realistic spacing), and ``065/fresh-bench/candidates.json`` — the same candidates on the **old
  bench** (the spacing before ADR-0010). Either may be missing; its column then says so.
* ``064/count/**/candidates.json`` — any later run in the scorer's schema (the bin-and-count rule
  WSMIP064 is building). Rows it holds that are not one of the six coded detectors or a learned
  pick are added to the leaderboard under their own name, on the bench their ``spacing`` names.
  Rerunning this tool is the whole of adding them.
* ``065/review/detect/calls.csv`` and ``windows.csv`` — ``tools/detect_with_floors.py``'s calls on
  the real recordings, for the examples and the raster links.
* ``065/review/pages/*.html`` — the group × treatment × stream raster pages, linked as they are.

**The examples read the default dataset** (``dataset.default()``), so they need the person's
confirmation for the session like every other analysis; ``--no-examples`` builds the rest without.

**What it decides: nothing.** The leaderboard orders rows by the paired F1 difference against
CoactDetect's shipped setting on the new bench, and marks what the run's own records mark: a row
over a budget, a proposal on a grid limit (ADR-0010 ruling 5), a training run with no pick. The
order is a reading of intervals, not a ranking the intervals support (``docs/performance_table.md``).

**What it writes:** ``index.html``, ``briefing.json`` (every number on the page), ``figure1_*.png``,
``example_*.png``, and ``viewer.html`` (a copy of the site's viewer, so the raster links open
locally). It defaults to the darkroom. ``--also`` copies **only the simulation half** —
Figure 1 and ``leaderboard.json`` — because the page, the examples and the raster links name real
recordings, and nothing derived from real recordings goes into the repo (FOUNDATIONS §5).
"""
from __future__ import annotations

import argparse
import csv
import html
import json
import os
import shutil
import sys
import tempfile
import warnings
from collections import defaultdict
from datetime import datetime, timedelta, timezone
from pathlib import Path
from urllib.parse import quote

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / "tools"))
sys.path.insert(0, str(REPO / "src"))

from bugarach.groups import group_key  # noqa: E402

NIGHT_NAME = "2026-09-26-full-panel"
STREAMS = ("fast", "slow", "combined")
CODED = ("coact", "loco", "sce", "rate", "sync", "cicada")
NAME = {"coact": "CoactDetect", "loco": "LoCo", "sce": "binned SCE", "rate": "rate+context",
        "sync": "SPIKE-synch", "cicada": "locust",    # the sixth detector's name, ADR-0002
        "count": "count (binned)", "count_sliding": "count (sliding)"}   # the simple rule, #841
#: The two benches the page sets side by side, and the scorer's ``spacing`` value for each.
BENCH_COLS = (("new", "realistic", "065/fresh-realistic/candidates.json"),
              ("old", "bench", "065/fresh-bench/candidates.json"))
BENCH_TITLE = {"new": "new bench (realistic spacing, ADR-0010)",
               "old": "old bench (spacing before ADR-0010)"}
#: Later runs in the scorer's schema. Each adds the rows of detectors the night's own files do not
#: hold, on the bench its ``spacing`` names: WSMIP064's count rule on the new bench (and ORX, which
#: this page does not show), and the same candidates on the old bench, scored here.
EXTRA_GLOBS = ("064/count/**/candidates.json", "065/fresh-bench-count/candidates.json")
CALLS = "065/review/detect/calls.csv"
WINDOWS = "065/review/detect/windows.csv"
PAGES = "065/review/pages"
EDT = timezone(timedelta(hours=-4), "EDT")
#: The half-width of an example's window, in seconds, per stream: slow and combined events last
#: seconds, fast ones a fraction of one.
EXAMPLE_HALF_SEC = {"fast": 45.0, "slow": 120.0, "combined": 120.0}
#: How close two calls must come to count as the same event in the examples, in seconds: the
#: bench's scoring tolerance, so "agree" here means what a hit means there.
AGREE_TOL_SEC = 2.5


# --------------------------------------------------------------------------------------------
# the model: every number on the page, read from files
# --------------------------------------------------------------------------------------------

def _load(p: Path) -> dict | None:
    return json.loads(p.read_text(encoding="utf-8")) if p.exists() else None


def when_edt(p: Path) -> str | None:
    """A file's modification time in EDT, the house clock for Tony."""
    if not p.exists():
        return None
    t = datetime.fromtimestamp(p.stat().st_mtime, tz=timezone.utc).astimezone(EDT)
    return t.strftime("%Y-%m-%d %-I:%M %p EDT") if os.name != "nt" else \
        t.strftime("%Y-%m-%d %#I:%M %p EDT")


#: What each budget is called on the page, and its unit.
BUDGET_WORDS = {"null": ("calls on the recording with nothing planted", "calls/h"),
                "probe": ("calls in the dense block with nothing planted (the probe)", "calls/min"),
                "elevated_out_quiet": ("calls outside the elevated-rate window", "calls/h"),
                "precision_swing": ("precision change between quiet and busy backgrounds", "")}


def budgets_of(bench_mod, det: str, row: dict) -> list[dict]:
    """The budgets a fresh-seed row fails, with value and limit — every budget the search's
    admissibility rule holds (``search_all_settings.make_admissible``; ADR-0010: "within every
    budget"), computed by the final-parameters report's own function so the two reports cannot
    disagree about what a failure is. A detector the bench holds budgets for is held to its own;
    a learned model is held to CoactDetect's.

    The worker's README counts only the first of these, the one the training pick uses; the page
    names each failure so the difference is visible rather than a contradiction."""
    from make_final_parameters_report import fresh_budgets

    own = det in getattr(bench_mod, "MAX_FALSE_POSITIVES_PER_HOUR", {})
    b = fresh_budgets(bench_mod, det, row, det if own else "coact")
    return [dict(name=k, value=v["value"], limit=v["limit"]) for k, v in b.items()
            if v["ok"] is False]


def budget_words(f: dict) -> str:
    what, unit = BUDGET_WORDS.get(f["name"], (f["name"], ""))
    u = f" {unit}" if unit else ""
    return f"{what}: {f['value']:.2f}{u} against a limit of {f['limit']:g}{u}"


def _unbracketed(meta: dict) -> list[str]:
    """A proposal's axes on a grid limit, in words: ADR-0010 ruling 5's stop."""
    prop = meta.get("proposal") or {}
    br = prop.get("bracketing") or {}
    if not prop.get("unbracketed"):
        return []
    out = []
    for axis, v in (br.get("unbracketed_axes") or {}).items():
        out.append(f"{axis} at its {v.get('reason', 'limit').replace('_', ' ')} ({v.get('value')})")
    return out or ["unbracketed, no axis named"]


def _family(pick: str, stream: str) -> str:
    return pick.split(f"_{stream}_seed")[0]


def bench_rows(cand: dict, stream: str, bench_mod) -> dict:
    """``{row id: row}`` for one stream of one candidates.json: every coded setting, every learned
    pick (or the best seed of a run with none, as a comparator), and every other row as-is."""
    res, meta = cand["results"][stream], cand["benches"][stream]
    rows = {}

    def put(rid, key, label, setting, family, flags):
        r = res[key]
        pf = (r.get("paired_f1_vs_coact") or {}).get("shipped") or {}
        rows[rid] = dict(label=label, setting=setting, family=family, key=key,
                         mid=pf.get("mid"), lo=pf.get("lo"), hi=pf.get("hi"),
                         n_seeds=pf.get("n_seeds"), mean_f1=r.get("mean_f1"),
                         null_per_hour=r.get("null_calls_per_hour"),
                         budget_fails=budgets_of(bench_mod, family, r), flags=list(flags))

    dets = list(CODED) + [d for d in meta.get("detectors", {}) if d not in CODED]
    for det in dets:
        if f"{det}:shipped" in res:
            put(f"{det}:shipped", f"{det}:shipped", NAME.get(det, det), "shipped", det, [])
        if f"{det}:proposal" in res:
            put(f"{det}:proposal", f"{det}:proposal", NAME.get(det, det), "proposal", det,
                [f"ruling 5: {x}" for x in _unbracketed(meta["detectors"].get(det, {}))])
    for fam, c in (meta.get("chorus") or {}).items():
        pick = c.get("picked")
        if pick and f"chorus:{pick}" in res:
            put(f"learned:{fam}", f"chorus:{pick}", fam, pick.replace(".json", ""), fam, [])
        elif c.get("out_of_budget"):
            best = c["out_of_budget"]["best"]
            if f"chorus:{best}" in res:
                put(f"learned:{fam}", f"chorus:{best}", fam, best.replace(".json", ""), fam,
                    ["no pick: no seed within the empty-recording budget; a comparator only"])
    for key in res:
        kind = key.split(":", 1)[0]
        if kind not in dets and kind != "chorus":
            put(key, key, NAME.get(kind, kind), key.split(":", 1)[-1], kind, [])
    return rows


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
        sources[col] = dict(path=rel, present=c is not None, written=when_edt(p),
                            # seeds_by_bench holds each stream's [first, last] seed, inclusive
                        seeds={s: (lambda r: r[1] - r[0] + 1 if len(r) == 2 else None)(
                                   (c or {}).get("seeds_by_bench", {}).get(s, []))
                               for s in STREAMS} if c else None)
        benches[col] = {s: bench_rows(c, s, mods[s]) for s in STREAMS
                        if c and s in c["results"]} if c else {}
    # Later runs in the scorer's schema add rows on the bench their spacing names, for detectors
    # the night's own files do not hold (a later file's CoactDetect rows repeat the night's).
    own = {col: {r["family"] for st in benches.get(col, {}).values() for r in st.values()}
           for col, _, _ in BENCH_COLS}
    count_files = sorted({p for g in EXTRA_GLOBS for p in night.glob(g)})
    extra = []
    for p in count_files:
        c = _load(p)
        col = next((b for b, sp, _ in BENCH_COLS if sp == c.get("spacing", "bench")), None)
        if col is None:
            continue
        for s in STREAMS:
            if s in c.get("results", {}):
                for rid, row in bench_rows(c, s, mods[s]).items():
                    if row["family"] not in own[col] and not rid.startswith("learned:"):
                        benches.setdefault(col, {}).setdefault(s, {})[rid] = row
                        extra.append(rid)
        sources.setdefault("extra", []).append(str(p.relative_to(night)))
    board = {}
    for s in STREAMS:
        ids = list(dict.fromkeys(rid for col, _, _ in BENCH_COLS
                                 for rid in benches.get(col, {}).get(s, {})))
        entries = []
        for rid in ids:
            per = {col: benches.get(col, {}).get(s, {}).get(rid) for col, _, _ in BENCH_COLS}
            first = next(v for v in per.values() if v)
            entries.append(dict(id=rid, label=first["label"], setting=first["setting"],
                                family=first["family"], per=per))
        def order(e):
            mid = (e["per"]["new"] or {}).get("mid")
            return (0, -mid) if mid is not None else (1, 0.0)
        entries.sort(key=order)
        board[s] = entries
    return dict(night=str(night), sources=sources, board=board,
                count_present=bool(extra), count_files=[str(p) for p in count_files],
                budgets={s: {d: float(mods[s].MAX_FALSE_POSITIVES_PER_HOUR[d]) for d in CODED}
                         for s in STREAMS})


def ran_on_real(entry: dict) -> str | None:
    """The ``calls.csv`` detector name for a leaderboard row, if the real-data run used exactly
    that setting: a coded detector at its proposal where the search made one (otherwise shipped),
    and each learned family at its pick. ``None`` for anything the real run did not use."""
    fam, setting = entry["family"], entry["setting"]
    if fam in CODED:
        has_prop = any(e["family"] == fam and e["setting"] == "proposal"
                       for e in entry.get("_siblings", ()))
        return fam if (setting == "proposal") == has_prop else None
    if entry["id"].startswith("learned:") and not any(
            f.startswith("no pick") for v in entry["per"].values() if v for f in v["flags"]):
        return fam
    return None


# --------------------------------------------------------------------------------------------
# the real-data side: calls, windows, examples
# --------------------------------------------------------------------------------------------

def read_calls(p: Path) -> list[dict]:
    with p.open(newline="", encoding="utf-8") as fh:
        return [r for r in csv.DictReader(fh)
                if r.get("variant") in ("own_floor", "unfloored")]


def recordings(windows_csv: Path) -> list[dict]:
    """One row per recording: its group and its first treatment (the first treatment window by
    region index), in the house group order."""
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


def pick_examples(calls: list[dict], stream: str, leader: str, ref: str,
                  used: set) -> list[dict]:
    """Three baseline-window calls on one stream: the leader and the reference agree, the leader
    calls and the reference does not, the reference calls and the leader does not. Each is the
    median-participant call of its kind, preferring a recording not used yet, so the choice is
    reproducible and not the most striking one."""
    by = defaultdict(lambda: defaultdict(list))
    for r in calls:
        if r["stream"] == stream and r["window_kind"] == "baseline":
            by[r["slice_id"]][r["detector"]].append(r)
    kinds = {"agree": [], "leader_only": [], "ref_only": []}
    for sid, per in by.items():
        L, R = per.get(leader, []), per.get(ref, [])
        for c in L:
            kinds["agree" if _overlaps(c, R, AGREE_TOL_SEC) else "leader_only"].append(c)
        for c in R:
            if not _overlaps(c, L, AGREE_TOL_SEC):
                kinds["ref_only"].append(c)
    out = []
    for kind, pool in kinds.items():
        if not pool:
            out.append(dict(kind=kind, call=None))
            continue
        fresh = [c for c in pool if c["slice_id"] not in used] or pool
        fresh.sort(key=lambda c: (int(float(c["participants"] or 0)), c["slice_id"],
                                  float(c["onset_sec"])))
        c = fresh[len(fresh) // 2]
        used.add(c["slice_id"])
        out.append(dict(kind=kind, call=c))
    return out


def render_example(sl, stream: str, call: dict, lanes_for: dict, dest: Path,
                   stem: str) -> Path | None:
    """One example: the detectors' lanes above the recording's raster, a window around the call.
    Drawn through ``ui.diagnostic`` like every other raster figure; nothing on the raster."""
    import holoviews as hv
    import panel as pn

    from bugarach.ui.diagnostic import lane_panel, raster_panel
    from make_diagnostic import _render_png
    from make_group_raster_summary import LANE_NAMES, lane_color

    hv.extension("bokeh")
    t = float(call["onset_sec"])
    half = EXAMPLE_HALF_SEC[stream]
    ext = (max(0.0, t - half), t + half)
    st = sl.streams[stream]
    lanes = {}
    for det, rows in lanes_for.items():
        on = [float(r["onset_sec"]) for r in rows]
        wd = [float(r["width_sec"] or 0) for r in rows]
        info = [f"{int(float(r['participants'] or 0))} participants · own floor "
                f"{r['own_floor']} co-active ROIs" for r in rows]
        lanes[det] = (on, wd, info)
    big = {"yticks": "11pt", "ylabel": "11pt", "xticks": "11pt", "xlabel": "11pt"}
    lp = lane_panel(lanes, ext=ext, width=1000, row_px=30, names=LANE_NAMES,
                    colors={d: lane_color(d) for d in lanes}).opts(
        height=30 * len(lanes) + 30, fontsize=big, toolbar=None)
    # A window of a minute or four, not an hour, so the marks can be drawn thicker than the
    # group pages draw them; minimal ticks as there (the ROI count is in the label).
    rp = raster_panel(st, ext=ext, width=1000, height=max(160, min(360, 5 * st.n_rois)),
                      name=stream, mark_px=4.0, ticks="minimal").opts(fontsize=big, toolbar=None)
    with tempfile.TemporaryDirectory() as td:
        tmp = Path(td) / "ex.html"
        pn.Column(pn.pane.HoloViews(lp, linked_axes=True, margin=0),
                  pn.pane.HoloViews(rp, linked_axes=True, margin=0), margin=0).save(str(tmp))
        png = dest / f"{stem}.png"
        return png if _render_png(tmp, png, scale=2) else None


def examples(model: dict, night: Path, dest: Path) -> list[dict]:
    """Per stream: the leader and CoactDetect on real baseline windows, three calls each."""
    from bugarach import dataset
    from bugarach.io import load_folder

    folder = dataset.default()
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        slices = {sl.slice_id: sl for sl in load_folder(folder)}
    calls = read_calls(night / CALLS)
    out, used = [], set()
    for s in STREAMS:
        entries = model["board"][s]
        for e in entries:
            e["_siblings"] = entries
        real = [(e, ran_on_real(e)) for e in entries]
        real = [(e, d) for e, d in real if d and d != "coact"
                and not any((e["per"][c] or {}).get("budget_fails") for c in ("new",))]
        if not real:
            continue
        # THE LEADER FOR THE EXAMPLES DISAGREES WITH COACTDETECT AT LEAST ONCE EACH WAY. A row
        # whose baseline calls all coincide with CoactDetect's has no disagreement to show, and
        # showing "no such call" three times over is less use than the next row down. Every row
        # passed over is named with its reason on the page.
        skipped, choice = [], None
        for i, (e, d) in enumerate(real):
            picks = pick_examples(calls, s, d, "coact", set(used))
            if all(p["call"] is not None for p in picks):
                choice = i
                break
            n = sum(1 for r in calls if r["stream"] == s and r["window_kind"] == "baseline"
                    and r["detector"] == d)
            skipped.append(dict(label=f"{e['label']} · {setting_words(e)}", calls=n,
                                missing=[p["kind"] for p in picks if p["call"] is None]))
        if choice is None:
            choice = 0
        (lead, ldet) = real[choice]
        runner = next((d for j, (_, d) in enumerate(real) if j != choice), None)
        for pick in pick_examples(calls, s, ldet, "coact", used):
            ex = dict(stream=s, leader=ldet, leader_label=lead["label"], runner=runner,
                      kind=pick["kind"], call=pick["call"], png=None, skipped=skipped)
            c = pick["call"]
            if c is not None and c["slice_id"] in slices:
                sl = slices[c["slice_id"]]
                if s == "combined":
                    from bugarach.combined import COMBINED, has_sources, stream_of
                    if has_sources(sl) and COMBINED not in sl.streams:
                        sl.streams[COMBINED] = stream_of(sl, COMBINED)
                if s in sl.streams:
                    half = EXAMPLE_HALF_SEC[s]
                    t = float(c["onset_sec"])
                    show = [d for d in (ldet, runner, "coact") if d]
                    lanes_for = {d: [r for r in calls if r["slice_id"] == c["slice_id"]
                                     and r["stream"] == s and r["detector"] == d
                                     and abs(float(r["onset_sec"]) - t) <= half + 60]
                                 for d in show}
                    png = render_example(sl, s, c, lanes_for, dest,
                                         f"example_{s}_{pick['kind']}")
                    ex["png"] = png.name if png else None
                    ex["lanes"] = show
            out.append(ex)
    for s in STREAMS:
        for e in model["board"][s]:
            e.pop("_siblings", None)
    return out


# --------------------------------------------------------------------------------------------
# rendering
# --------------------------------------------------------------------------------------------

def _f(x, nd=3, sign=True):
    if x is None:
        return "—"
    return f"{x:+.{nd}f}" if sign else f"{x:.{nd}f}"


def figure1(model: dict, dest: Path) -> Path:
    """Figure 1: every row's paired F1 difference against CoactDetect's shipped setting, new bench
    (filled) beside old bench (open), 95% intervals, one block per stream.

    Drawn as SVG by hand: no plotting dependency (matplotlib is not one of this project's), exact
    type sizes (15 px, over the house floor of 11 pt), and the page's own colours in both themes.
    Fixed at 1000 px wide and scrolled rather than shrunk on a narrow screen, so the type never
    drops under the floor."""
    W, LEFT, RIGHT, ROW, HEAD, AXIS = 1000, 330, 30, 30, 34, 60
    vals = [x for s in STREAMS for e in model["board"][s] for v in e["per"].values() if v
            for x in (v["lo"], v["hi"]) if x is not None] + [0.0]
    lo, hi = min(vals), max(vals)
    pad = 0.06 * (hi - lo or 0.1)
    lo, hi = lo - pad, hi + pad
    # Steps whose ticks print exactly at two decimals, so a label never rounds away from its line.
    step = next(st for st in (0.01, 0.02, 0.05, 0.1, 0.2) if (hi - lo) / st <= 10)

    def X(v):
        return LEFT + (v - lo) / (hi - lo) * (W - LEFT - RIGHT)

    n = sum(len(model["board"][s]) for s in STREAMS)
    H = HEAD * len(STREAMS) + ROW * n + AXIS + 70
    out = [f"<svg xmlns='http://www.w3.org/2000/svg' width='{W}' height='{H}' "
           f"viewBox='0 0 {W} {H}' font-family='system-ui, sans-serif' font-size='15' "
           f"role='img' aria-label='Figure 1, the leaderboard'>",
           "<style>.ax{stroke:var(--line,#ccc)} .zero{stroke:var(--fg,#222)} "
           ".t{fill:var(--fg,#222)} .m{fill:var(--muted,#666)} "
           ".new{stroke:var(--accent,#0072B2);fill:var(--accent,#0072B2)} "
           ".old{stroke:var(--accent,#0072B2);fill:var(--bg,#fff)} "
           ".badn{stroke:var(--bad,#b03a2e);fill:var(--bad,#b03a2e)} "
           ".bado{stroke:var(--bad,#b03a2e);fill:var(--bg,#fff)}</style>"]
    y = 10
    ticks = []
    k = int(lo / step) - 1
    while k * step <= hi:
        if k * step >= lo:
            ticks.append(round(k * step, 6))
        k += 1
    top = y
    for s in STREAMS:
        rows = model["board"][s]
        out.append(f"<text class='t' x='8' y='{y + 22}' font-weight='650'>{s} stream · "
                   f"{len(rows)} rows</text>")
        y += HEAD
        for e in rows:
            cy = y + ROW / 2
            flag = " §5" if any(f.startswith("ruling 5") for v in e["per"].values() if v
                               for f in v["flags"]) else ""
            name = f"{e['label']} · {setting_words(e)}{flag}"
            out.append(f"<text class='t' x='{LEFT - 10}' y='{cy + 5}' text-anchor='end'>"
                       f"{html.escape(name)}</text>")
            out.append(f"<line class='ax' x1='{LEFT}' x2='{W - RIGHT}' y1='{y + ROW}' "
                       f"y2='{y + ROW}' stroke-width='0.5'/>")
            for col, dy in (("new", -6), ("old", 6)):
                v = e["per"][col]
                if not v or v["mid"] is None:
                    continue
                bad = bool(v["budget_fails"]) or any(f.startswith("no pick") for f in v["flags"])
                cls = ("bad" if bad else "") + ("n" if col == "new" else "o")
                cls = {"n": "new", "o": "old"}.get(cls, cls)
                out.append(f"<line class='{cls}' x1='{X(v['lo']):.1f}' x2='{X(v['hi']):.1f}' "
                           f"y1='{cy + dy}' y2='{cy + dy}' stroke-width='2'/>")
                out.append(f"<circle class='{cls}' cx='{X(v['mid']):.1f}' cy='{cy + dy}' r='5' "
                           f"stroke-width='2'/>")
            y += ROW
    bottom = y
    for t in ticks:
        out.append(f"<line class='{'zero' if t == 0 else 'ax'}' x1='{X(t):.1f}' x2='{X(t):.1f}' "
                   f"y1='{top}' y2='{bottom}' stroke-width='{1.2 if t == 0 else 0.6}'/>")
        out.append(f"<text class='m' x='{X(t):.1f}' y='{bottom + 20}' text-anchor='middle'>"
                   f"{'0' if abs(t) < 1e-9 else f'{t:+.2f}'}</text>")
    out.append(f"<text class='t' x='{(LEFT + W - RIGHT) / 2}' y='{bottom + 44}' "
               f"text-anchor='middle'>ΔF1 against CoactDetect at its shipped setting (95% "
               f"interval)</text>")
    ly = bottom + 76
    for i, (cls, label) in enumerate((("new", "new bench"), ("old", "old bench"),
                                      ("badn", "over a budget, or no pick"))):
        lx = 8 + i * 110 if i < 2 else 8 + 2 * 110
        out.append(f"<circle class='{cls}' cx='{lx + 6}' cy='{ly - 5}' r='5' stroke-width='2'/>"
                   f"<text class='t' x='{lx + 16}' y='{ly}'>{label}</text>")
    out.append("</svg>")
    p = dest / "figure1_leaderboard.svg"
    p.write_text("\n".join(out), encoding="utf-8")
    return p


CSS = """
:root { --bg:#fbfaf7; --fg:#1b1b1b; --muted:#5b5b5b; --line:#dcd8cf; --accent:#0072B2;
        --bad:#b03a2e; --warn:#8a5a00; --card:#ffffff; --mono: ui-monospace, Consolas, monospace; }
@media (prefers-color-scheme: dark) { :root:not([data-theme="light"]) {
  --bg:#141414; --fg:#e8e6e1; --muted:#a8a49c; --line:#3a3833; --accent:#6cb4e4;
  --bad:#ef8a7e; --warn:#e3b35a; --card:#1d1d1d; } }
:root[data-theme="dark"] { --bg:#141414; --fg:#e8e6e1; --muted:#a8a49c; --line:#3a3833;
  --accent:#6cb4e4; --bad:#ef8a7e; --warn:#e3b35a; --card:#1d1d1d; }
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
th, td { border-bottom: 1px solid var(--line); padding: .35rem .5rem; text-align: left;
         vertical-align: top; }
th { font-weight: 650; }
td.n { font-family: var(--mono); white-space: nowrap; text-align: right; }
.bad { color: var(--bad); font-weight: 600; } .warn { color: var(--warn); }
td.marks { padding-top: 0; }
figure { margin: 1.2rem 0 1.8rem; } figure img { width: 100%; height: auto; background: #fff;
         border: 1px solid var(--line); }
figcaption { color: var(--muted); margin-top: .4rem; }
.pill { display: inline-block; border: 1px solid var(--line); border-radius: 4px;
        padding: 0 .35rem; margin: 0 .2rem .2rem 0; font-size: .95rem; }
code { font-family: var(--mono); font-size: .95em; }
.box { border: 1px solid var(--line); background: var(--card); padding: .8rem 1rem;
       border-radius: 6px; margin: 1rem 0; }
"""


def _marks_html(per: dict) -> str:
    """A row's marks: each bench's budget failures, labelled by bench, then the flags the search
    or the training pick carries (the same on both benches, so said once)."""
    out = []
    for col in ("new", "old"):
        v = per.get(col)
        for f in (v or {}).get("budget_fails", []):
            out.append(f"<span class='bad'>{col} bench over budget, "
                       f"{html.escape(budget_words(f))}</span>")
    first = next((v for v in per.values() if v), None)
    for f in (first or {}).get("flags", []):
        cls = "bad" if f.startswith("no pick") else "warn"
        out.append(f"<span class='{cls}'>{html.escape(f)}</span>")
    return "<br>".join(out)


def setting_words(e: dict) -> str:
    """A row's setting as the table says it: shipped or proposal for a detector, and for a learned
    model the seed its training run picked (the checkpoint's full name is in briefing.json)."""
    if not e["id"].startswith("learned:"):
        return e["setting"]
    seed = e["setting"].rsplit("_seed", 1)[-1]
    nopick = any(f.startswith("no pick") for v in e["per"].values() if v for f in v["flags"])
    return f"{'best seed' if nopick else 'pick'}, seed {seed}"


def leaderboard_table(model: dict, s: str, tno: int) -> str:
    rows = model["board"][s]
    head = ("<tr><th>#</th><th>detector or model</th><th>setting</th>"
            "<th>new bench ΔF1 [95%]</th><th>new mean F1</th>"
            "<th>old bench ΔF1 [95%]</th><th>old mean F1</th></tr>")
    body = []
    for i, e in enumerate(rows, 1):
        cells = []
        for col in ("new", "old"):
            v = e["per"][col]
            if not v:
                cells += ["<td class='n muted'>not scored</td>", "<td class='n'>—</td>"]
            else:
                cells += [f"<td class='n'>{_f(v['mid'])} [{_f(v['lo'])}, {_f(v['hi'])}]</td>",
                          f"<td class='n'>{_f(v['mean_f1'], sign=False)}</td>"]
        marks = _marks_html(e["per"])
        # THE MARKS GO ON A LINE OF THEIR OWN under the row: as a column they pushed the table
        # past the page and made every flagged row several lines tall.
        edge = " style='border-bottom:none'" if marks else ""
        body.append(f"<tr><td class='n'{edge}>{i}</td><td{edge}>{html.escape(e['label'])}</td>"
                    f"<td{edge}>{html.escape(setting_words(e))}</td>"
                    + "".join(c.replace("<td", f"<td{edge}", 1) for c in cells) + "</tr>")
        if marks:
            body.append(f"<tr><td></td><td colspan='6' class='marks'>{marks}</td></tr>")
    if not model["count_present"]:
        body.append("<tr><td class='n'>—</td><td>count (bin-and-count rule)</td><td>—</td>"
                    "<td class='n muted' colspan='4'>not scored yet: WSMIP064 is building it, and "
                    "its results land in <code>064/count/</code>. Rerunning the builder adds "
                    "this row.</td></tr>")
    return (f"<div class='tablewrap'><table><caption style='text-align:left'><b>Table {tno}.</b> "
            f"The {s} stream, {len(rows)} rows, ordered by the new bench's paired F1 difference "
            f"(ΔF1) against CoactDetect at its shipped setting.</caption>{head}{''.join(body)}"
            f"</table></div>")


def glance(model: dict) -> dict:
    """Per stream and bench: how many rows' intervals sit wholly above, include zero, or sit wholly
    below CoactDetect's shipped setting, and the top row. Counted from the rows on the page, so the
    summary cannot say what the table does not (CoactDetect's own shipped row is left out)."""
    out = {}
    for s in STREAMS:
        out[s] = {}
        for col in ("new", "old"):
            rows = [(e, e["per"][col]) for e in model["board"][s]
                    if e["per"][col] and e["id"] != "coact:shipped"]
            if not rows:
                continue
            above = sum(v["lo"] > 0 for _, v in rows)
            below = sum(v["hi"] < 0 for _, v in rows)
            top_e, top_v = max(rows, key=lambda ev: ev[1]["mid"])
            out[s][col] = dict(n=len(rows), above=above, below=below,
                               straddle=len(rows) - above - below,
                               top=f"{top_e['label']} · {setting_words(top_e)}",
                               top_mid=top_v["mid"])
    return out


def glance_html(g: dict) -> str:
    head = ("<tr><th>stream</th><th>bench</th><th>rows above</th><th>interval includes zero</th>"
            "<th>rows below</th><th>top row (ΔF1)</th></tr>")
    body = []
    for s in STREAMS:
        for col in ("new", "old"):
            v = g[s].get(col)
            if not v:
                body.append(f"<tr><td>{s}</td><td>{col}</td><td colspan='4' class='muted'>not "
                            f"scored</td></tr>")
                continue
            body.append(f"<tr><td>{s}</td><td>{col}</td><td class='n'>{v['above']} rows</td>"
                        f"<td class='n'>{v['straddle']} rows</td><td class='n'>{v['below']} rows"
                        f"</td><td>{html.escape(v['top'])} ({_f(v['top_mid'])})</td></tr>")
    return (f"<div class='tablewrap'><table><caption style='text-align:left'><b>Table 1.</b> At a "
            f"glance: of the rows on each stream (CoactDetect's shipped row left out), how many "
            f"have a 95% interval wholly above CoactDetect's shipped setting, including zero, or "
            f"wholly below it, on each bench.</caption>{head}{''.join(body)}</table></div>")


def viewer_href(slice_id: str, stream: str, t: float | None = None) -> str:
    frag = f"slice={quote(slice_id)}&stream={quote(stream)}"
    if t is not None:
        frag += f"&t={t:.1f}"
    return f"viewer.html#{frag}"


EX_TEXT = {"agree": "{L} and CoactDetect both call it",
           "leader_only": "{L} calls it; CoactDetect does not",
           "ref_only": "CoactDetect calls it; {L} does not"}


def render(model: dict, exs: list[dict] | None, recs: list[dict], pages: list[str],
           *, dataset_name: str | None, results_path: str | None) -> str:
    src = model["sources"]
    fig_no = 1
    parts = []
    parts.append(f"<h1>Full-panel night briefing</h1><p class='byline'>The night of 2026-09-25 "
                 f"(ADR-0010), scored on fresh seeds. Built {html.escape(model['built'])}. "
                 f"Every number is read from the run's own files; nothing here is adopted.</p>")
    parts.append("<nav><a href='#leaderboard'>1. Leaderboard</a><a href='#examples'>2. Examples"
                 "</a><a href='#rasters'>3. Rasters</a><a href='#terms'>Terms</a></nav>")
    # 1. leaderboard ---------------------------------------------------------------------------
    parts.append("<h2 id='leaderboard'>1. Leaderboard: every detector and learned pick against "
                 "CoactDetect</h2>")
    seeds = []
    for col in ("new", "old"):
        s_ = src[col]
        if s_["present"]:
            seeds.append(f"{BENCH_TITLE[col]}: scored {html.escape(s_['written'] or '')}, "
                         + ", ".join(f"{k} {v} seeds per background" for k, v in
                                     s_["seeds"].items()))
        else:
            seeds.append(f"{BENCH_TITLE[col]}: <span class='bad'>not scored yet</span> "
                         f"(<code>{html.escape(s_['path'])}</code> is missing)")
    parts.append("<div class='box'><b>How to read it.</b> Each row is scored on the same simulated "
                 "recordings as CoactDetect at its shipped setting, so the difference is paired: "
                 "the mean over seeds of (row F1 − CoactDetect F1), with a 95% bootstrap interval "
                 "over seeds (2,000 draws). An interval clear of zero is a difference the seeds "
                 "resolve; one that straddles zero is not. The new and old benches score the "
                 "<i>same</i> candidates. The proposals and the learned picks were chosen on the "
                 "new bench, while the shipped settings, the reference among them, date from "
                 "before ADR-0010, when the old bench was the only one: each column is partly a "
                 "field some rows were chosen on and others were not.<br>"
                 + "<br>".join(seeds) + "</div>")
    parts.append(glance_html(glance(model)))
    svg = model.get("_figure1_svg", "")
    parts.append(f"<figure><div class='tablewrap'>{svg}</div>"
                 f"<figcaption><b>Figure {fig_no}, the leaderboard.</b> Paired F1 difference "
                 f"against CoactDetect at its shipped setting; filled marks are the new bench, "
                 f"open marks the old, bars the 95% interval. Red: over a budget on that bench, or "
                 f"a training run with no pick. §5: a proposal on a grid limit (ADR-0010 ruling "
                 f"5), not adoptable on the search's own rule.</figcaption></figure>")
    fig_no += 1
    for i, s in enumerate(STREAMS, 2):       # Table 1 is the at-a-glance table
        parts.append(f"<h3>{s.capitalize()} stream</h3>" + leaderboard_table(model, s, i))
    # 2. examples ------------------------------------------------------------------------------
    parts.append("<h2 id='examples'>2. Examples on real recordings</h2>")
    if exs is None:
        parts.append("<p class='bad'>Not built: the examples read the default dataset, and this "
                     "build ran without it (<code>--no-examples</code>, or the dataset was not "
                     "confirmed for the session).</p>")
    else:
        parts.append(f"<p>Per stream, the top row that ran on the real recordings "
                     f"(<code>{html.escape(CALLS)}</code>; CoactDetect excluded, and no row over "
                     f"a budget) set against CoactDetect as it ran there, on baseline windows "
                     f"only. Three calls each: both call it, only the leader does, only "
                     f"CoactDetect does. Each is the call with the median participant count of "
                     f"its kind, so the choice is reproducible and not the most striking one. "
                     f"Lanes sit above the raster; nothing is drawn on it. Two calls agree when "
                     f"their spans come within {AGREE_TOL_SEC:g} s, the bench's scoring "
                     f"tolerance.</p>")
        for s in STREAMS:
            mine = [e for e in exs if e["stream"] == s]
            if not mine:
                continue
            parts.append(f"<h3>{s.capitalize()} stream: {html.escape(mine[0]['leader_label'])} "
                         f"against CoactDetect</h3>")
            for sk in mine[0].get("skipped") or []:
                parts.append(f"<p class='muted'>Passed over: {html.escape(sk['label'])}, higher on "
                             f"the leaderboard. Of its {sk['calls']} calls on baseline windows, "
                             f"none gives an example of: "
                             + "; ".join(EX_TEXT[k].format(L=html.escape(sk['label']))
                                         for k in sk["missing"])
                             + ". It has no disagreement with CoactDetect to show here.</p>")
            for e in mine:
                L = mine[0]["leader_label"]
                what = EX_TEXT[e["kind"]].format(L=html.escape(L))
                c = e["call"]
                if c is None:
                    parts.append(f"<p class='muted'>{what}: no such call on any baseline window."
                                 f"</p>")
                    continue
                t = float(c["onset_sec"])
                link = viewer_href(c["slice_id"], s, t)
                cap = (f"<b>Figure {fig_no}.</b> {what}. Recording "
                       f"<a href='{link}'>{html.escape(c['slice_id'])}</a> "
                       f"({html.escape(c['group'])}), {s} stream, the call at "
                       f"{t / 60:.0f}m{t % 60:02.0f}s with {int(float(c['participants'] or 0))} "
                       f"participating ROIs; {EXAMPLE_HALF_SEC[s]:g} s either side. Lanes: "
                       + ", ".join(html.escape(NAME.get(d, d)) for d in e.get("lanes", []))
                       + ". Hover a call in the viewer for its participants and floors.")
                if e["png"]:
                    parts.append(f"<figure><a href='{link}'><img src='{e['png']}' "
                                 f"alt='Figure {fig_no}'></a><figcaption>{cap}</figcaption>"
                                 f"</figure>")
                else:
                    parts.append(f"<p class='bad'>Figure {fig_no} did not render (no "
                                 f"Playwright chromium?).</p><p>{cap}</p>")
                fig_no += 1
    # 3. rasters -------------------------------------------------------------------------------
    parts.append("<h2 id='rasters'>3. Rasters with detection</h2>")
    parts.append(
        "<div class='box'><b>Opening one recording.</b> Each link opens the site's viewer, copied "
        "beside this page, at that recording and stream, with the night's calls in lanes above the "
        "raster (▼ at each onset, one lane per detector and floor variant; hover a ▼ for its "
        "participants and floors). The viewer reads only files you open; nothing leaves the "
        "machine. The first time: <b>1.</b> click <i>Choose folder…</i> and pick the export folder "
        f"<code>{html.escape(dataset_name or 'the default dataset')}</code>; <b>2.</b> click "
        "<i>Open results (detections.csv)…</i> and pick "
        f"<code>{html.escape(results_path or 'detections.csv')}</code>. After that, a link needs "
        "one click on <i>Reopen</i> and the browser's permission prompt; the results file is "
        "picked again each visit unless it is copied into the export folder.</div>")
    if pages:
        by = defaultdict(dict)
        for p in pages:
            g, t, s = Path(p).stem.split("_", 2)
            by[(g, t)][s] = p
        rows = []
        for (g, t) in sorted(by, key=lambda k: (group_key(k[0]), k[1])):
            links = " · ".join(f"<a href='{html.escape(by[(g, t)][s])}'>{s}</a>"
                               for s in STREAMS if s in by[(g, t)])
            rows.append(f"<tr><td>{g}</td><td>{html.escape(t)}</td><td>{links}</td></tr>")
        parts.append(f"<p>Every recording in a group whose first treatment was the same, stacked "
                     f"and aligned at the end of its own baseline — the night's review pages, "
                     f"{len(pages)} pages:</p><div class='tablewrap'><table><caption "
                     f"style='text-align:left'><b>Table 5.</b> Group × first-treatment pages, "
                     f"one per stream.</caption><tr><th>group</th><th>first treatment</th>"
                     f"<th>pages</th></tr>{''.join(rows)}</table></div>")
    rows = []
    for r in recs:
        links = " · ".join(f"<a href='{viewer_href(r['slice_id'], s)}'>{s}</a>"
                           for s in r["streams"])
        rows.append(f"<tr><td>{html.escape(r['group'])}</td><td>{html.escape(r['first'] or '—')}"
                    f"</td><td><code>{html.escape(r['slice_id'])}</code></td><td>{links}</td></tr>")
    parts.append(f"<p>One recording at a time, in the viewer ({len(recs)} recordings):</p>"
                 f"<div class='tablewrap'><table><caption style='text-align:left'><b>Table 6.</b>"
                 f" Every recording the night's detection ran on, by group and first treatment."
                 f"</caption><tr><th>group</th><th>first treatment</th><th>recording</th>"
                 f"<th>open in the viewer</th></tr>{''.join(rows)}</table></div>")
    # terms ------------------------------------------------------------------------------------
    parts.append("""<h2 id='terms'>Terms</h2><table>
<tr><th>F1</th><td>The harmonic mean of precision (the share of calls on a planted coordinated
event) and recall (the share of planted events called), on simulated recordings with known
events.</td></tr>
<tr><th>ΔF1</th><td>A row's F1 minus CoactDetect's at its shipped setting, on the same seeds,
averaged over seeds.</td></tr>
<tr><th>new bench / old bench</th><td>The simulator that plants coordinated events at the spacing
measured in real recordings (ADR-0010) / at least 120 s apart, as before it.</td></tr>
<tr><th>shipped / proposal</th><td>The setting a coded detector ships with / the setting the
night's search proposed. A detector whose search proposed nothing has no proposal row.</td></tr>
<tr><th>pick</th><td>The one of a learned model's five training seeds with the best held-out F1
among those within CoactDetect's budget on the recording with nothing planted.</td></tr>
<tr><th>budget</th><td>A limit on false calls, per detector: calls per hour on a recording with
nothing planted, calls per minute in a dense block with nothing planted (the promiscuity probe),
calls per hour outside an elevated-rate window, and how far precision moves between the quiet and
busy backgrounds.</td></tr>
<tr><th>ruling 5 (§5)</th><td>ADR-0010: a setting that lands on a grid limit or an off-limit
value is a finding, not a tuned value, so the proposal is not adoptable on the search's own
rule.</td></tr>
<tr><th>ROI</th><td>Region of interest: one cell's trace.</td></tr>
<tr><th>EDT</th><td>Eastern daylight time, UTC − 4 h.</td></tr></table>""")
    return ("<!doctype html>\n<html lang='en'>\n<head>\n"
            "<meta charset='utf-8'><title>Full-panel briefing</title>\n"
            "<meta name='viewport' content='width=device-width, initial-scale=1'>\n"
            "<style>" + CSS + "</style>\n</head>\n<body>"
            "<div class='wrap'>" + "\n".join(parts) + "</div></body></html>\n")


def main(argv=None) -> int:
    from bugarach.paths import darkroom, unresolved_message

    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("--night", type=Path, default=None,
                    help=f"the night's darkroom folder (default <darkroom>/{NIGHT_NAME})")
    ap.add_argument("--out", type=Path, default=None, help="default: <night>/briefing")
    ap.add_argument("--also", type=Path, default=None, help="a second copy, e.g. the repo folder")
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
    model["built"] = datetime.now(timezone.utc).astimezone(EDT).strftime("%Y-%m-%d %H:%M EDT")
    written = [figure1(model, a.out)]
    model["_figure1_svg"] = written[0].read_text(encoding="utf-8")
    exs, dataset_name = None, None
    try:
        from bugarach import dataset
        dataset_name = dataset.current_name("default")
    except Exception:          # the name is a courtesy on the page; a missing toml is not fatal
        pass
    if not a.no_examples and (a.night / CALLS).exists():
        exs = examples(model, a.night, a.out)
        written += [a.out / e["png"] for e in exs if e.get("png")]
    recs = recordings(a.night / WINDOWS) if (a.night / WINDOWS).exists() else []
    pages = sorted(os.path.relpath(p, a.out).replace(os.sep, "/")
                   for p in (a.night / PAGES).glob("*.html")) if (a.night / PAGES).exists() else []
    # The results file the viewer opens: the night's calls in the output contract, which
    # `detect_with_floors.py --detections-from <run>` writes beside this page.
    results_path = str(a.out / "detections.csv") if (a.out / "detections.csv").exists() else None
    page = render(model, exs, recs, pages, dataset_name=dataset_name, results_path=results_path)
    tmp = a.out / "index.html.tmp"
    tmp.write_text(page, encoding="utf-8")
    os.replace(tmp, a.out / "index.html")       # write-then-replace: the darkroom is Dropbox
    model["examples"] = exs
    model.pop("_figure1_svg", None)
    (a.out / "briefing.json").write_text(json.dumps(model, indent=1, default=str) + "\n",
                                         encoding="utf-8")
    written += [a.out / "index.html", a.out / "briefing.json"]
    if a.viewer.exists():
        shutil.copy2(a.viewer, a.out / "viewer.html")
        written.append(a.out / "viewer.html")
    else:
        print(f"no viewer at {a.viewer}: the raster links will not open", file=sys.stderr)
    if a.also:
        # THE SIMULATION HALF ONLY. The page, its examples and its raster links name real
        # recordings, and nothing derived from real recordings goes into this public repo
        # (FOUNDATIONS §5); the leaderboard is scored on simulated recordings and may.
        a.also.mkdir(parents=True, exist_ok=True)
        shutil.copy2(written[0], a.also / written[0].name)
        (a.also / "leaderboard.json").write_text(json.dumps(
            {k: model[k] for k in ("sources", "board", "count_present", "budgets", "built")},
            indent=1, default=str) + "\n", encoding="utf-8")
        print(f"wrote the leaderboard (simulated data only) to {a.also}")
    for p in written:
        print(f"wrote {p}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
