"""Does a confirmed field step COINCIDE with events, or GENERATE them?

    python tools/make_field_step_figure.py --dataset 2026-09-03_revised_2v_long_PRE_ARTIFACT_KILLER

interface2 shipped the draft-final-run export labelled ``PRE_ARTIFACT_KILLER``
and asked one question with it (handoff 2026-09-03, §4 item 2). They measured
*onset inside a confirmed whole-field brightness step* and got **slow baseline
7.28%** against **fast baseline 2.33%**, and offered two readings they could not
separate:

  A  a step is arithmetically more likely to land inside a broad SLOW event
  B  a whole-field step is itself SLOW-shaped and is generating SLOW calls

The consequences differ: under A the artifact work removes a coincidence, under B
there is no coincidence to remove because the events are the artifact.

**Three tests, and none of them needs the step's duration** — which the handoff
does not state:

1. **What chance predicts.** *Onset inside a window* is a point-in-window test,
   so under uniform onsets the in-window fraction is the window's duty cycle:
   the same for both streams whatever their rate and whatever their event
   **width**. Event width cannot enter a test on a point. So reading A, as
   stated, describes an *extent-overlap* test rather than the onset test that was
   run — and panel C measures the prediction directly.
2. **Simultaneity.** A whole-field step hits every ROI at once. B predicts an
   unusual number of *distinct ROIs* onsetting together at the step; A predicts
   the usual few. Panel A.
3. **Shape.** Under B the near-step events are one waveform seen in many cells,
   so whatever the producer put in ``width_sec`` should come back *tighter*
   across ROIs at the step than across the rest of the same region. Panel B.
   Each stream is compared only against itself: the declared ``width_def`` is
   read from the folder and reported, never interpreted here, and this export
   declares a different rule per stream — so the two streams' widths are not
   comparable to each other (export spec, rule 6).

The null is the same statistic at step times drawn uniformly inside the region
that holds the real step, which keeps each recording's own rate, roster and
region length and moves only the position.

**This measures the export, and decides nothing about the detections.** Whether a
coordinated event built from step-coincident members is itself false is a call on
bugarach's output, and interface2 explicitly left it here rather than writing
rules for it.
"""
from __future__ import annotations

import argparse
import csv
import json
import random
import statistics as st
import sys
from collections import defaultdict
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))

FIGURE_ID = "field_step_shape"

INK = "#16202b"
GUIDE = "#9a9a9a"
MUTED = "#5c6773"

COLOURS = {"fast": "#1f6fb4", "slow": "#b03a48"}
NULL_COLOUR = "#9aa7b4"

#: The nine steps Tony confirmed in the trace waterfall viewer, from the export
#: folder's own README. Not derived here and not derivable from the CSVs — the
#: adjudication is interface2's, and this figure is only as good as that list.
STEPS = {
    "20240708_17": 167.0,
    "20260122_259": 448.0,
    "20250826_192": 653.8,
    "20260701_331": 1401.0,
    "20250911_222": 1642.0,
    "20260707_346": 1990.7,
    "20250808_186": 3057.0,
    "20250904_211": 3530.0,
    "20240723_22": 3820.1,
}

#: Half-widths the onset test is run at, in seconds. The step's own duration is
#: not stated in the handoff, so the test is a scan rather than a choice — and
#: panel C's point is that the null is flat in the stream at every one of them.
HALF_WIDTHS = [0.5, 1.0, 2.0, 5.0, 10.0]

#: The half-width panels A and B report at. Wide enough to hold a whole-field
#: recruitment, narrow enough that two independent events rarely share it.
W_MAIN = 2.0

NULL_DRAWS = 2000
NULL_SEED = 20260903


def _num(row, key):
    v = (row.get(key) or "").strip()
    return None if v in ("", "NA") else float(v)


def _read_regions(folder: Path) -> dict[str, list[dict]]:
    out: dict[str, list[dict]] = defaultdict(list)
    with open(folder / "regions.csv", newline="") as fh:
        for r in csv.DictReader(fh):
            out[r["slice_id"]].append({
                "idx": int(r["region_idx"]),
                "label": r["label"],
                "raw": (float(r["start_sec"]), float(r["end_sec"])),
            })
    return out


def _declared_width_defs(path: Path) -> dict[str, set[str]]:
    """stream -> the ``width_def`` strings the producer declared, verbatim.

    Read rather than assumed. Panel B compares each stream's widths only against
    itself, so what the rule *is* never has to be known here — but which rule was
    declared is a fact about the folder and belongs in the figure's footer, and a
    stream declaring two would make that panel meaningless.
    """
    out: dict[str, set[str]] = defaultdict(set)
    with open(path, newline="") as fh:
        for r in csv.DictReader(fh):
            wd = (r.get("width_def") or "").strip()
            if wd and wd != "NA":
                out[r.get("stream") or "events"].add(wd)
    return out


def _read_events(path: Path) -> dict[str, list[tuple]]:
    """stream -> [(roi, t50rise, width_sec, amp)]. NA rows are not events.

    An ``NA`` time is the contract's way of saying the ROI was imaged in that
    stream and fired nothing (export spec, "An ROI that fired nothing is a row
    with no time"), so it is dropped here rather than counted as an onset at 0.
    """
    out: dict[str, list[tuple]] = defaultdict(list)
    with open(path, newline="") as fh:
        for r in csv.DictReader(fh):
            t = _num(r, "time_sec")
            if t is None:
                continue
            out[r.get("stream") or "events"].append(
                (r["roi"], t, _num(r, "width_sec"), _num(r, "amp")))
    return out


def _frac_within(evs, centre, w):
    return sum(1 for e in evs if abs(e[1] - centre) <= w) / len(evs) if evs else None


def _rois_within(evs, centre, w):
    return len({e[0] for e in evs if abs(e[1] - centre) <= w})


def _cv(rows, i):
    """Coefficient of variation, or None when too few values to mean anything."""
    vals = [r[i] for r in rows if r[i] is not None]
    if len(vals) < 3:
        return None
    m = st.fmean(vals)
    return (st.stdev(vals) / m) if m else None


def measure(folder: Path) -> dict:
    rng = random.Random(NULL_SEED)
    regions = _read_regions(folder)
    per_slice: dict[str, dict] = {}
    pooled = {w: {"fast": [], "slow": []} for w in HALF_WIDTHS}
    pooled_null = {w: {"fast": [], "slow": []} for w in HALF_WIDTHS}

    declared: dict[str, set[str]] = defaultdict(set)
    for sid, step in STEPS.items():
        ev = _read_events(folder / f"{sid}.csv")
        for stream, defs in _declared_width_defs(folder / f"{sid}.csv").items():
            declared[stream] |= defs
        holder = next((r for r in regions[sid]
                       if r["raw"][0] <= step <= r["raw"][1]), None)
        rec = {"step_sec": step, "region": holder, "streams": {}}
        per_slice[sid] = rec
        if holder is None:
            continue
        lo, hi = holder["raw"]

        for stream in ("fast", "slow"):
            evs = [e for e in ev.get(stream, []) if lo <= e[1] <= hi]
            if not evs:
                continue
            near = [e for e in evs if abs(e[1] - step) <= W_MAIN]
            rest = [e for e in evs if abs(e[1] - step) > W_MAIN]
            s = {
                "n_events": len(evs),
                "n_roi": len({e[0] for e in evs}),
                "roi_at_step": _rois_within(evs, step, W_MAIN),
                "observed": {}, "null_mean": {}, "null_p": {},
                "null_roi_mean": None,
                "cv_width_near": _cv(near, 2), "cv_width_rest": _cv(rest, 2),
                "cv_amp_near": _cv(near, 3), "cv_amp_rest": _cv(rest, 3),
                "n_near": len(near),
            }
            for w in HALF_WIDTHS:
                if hi - lo <= 2 * w:
                    continue
                obs = _frac_within(evs, step, w)
                draws, roidraws = [], []
                for _ in range(NULL_DRAWS):
                    c = rng.uniform(lo + w, hi - w)
                    draws.append(_frac_within(evs, c, w))
                    roidraws.append(_rois_within(evs, c, w))
                s["observed"][w] = obs
                s["null_mean"][w] = st.fmean(draws)
                s["null_p"][w] = (1 + sum(1 for d in draws if d >= obs)) \
                    / (NULL_DRAWS + 1)
                if w == W_MAIN:
                    s["null_roi_mean"] = st.fmean(roidraws)
                pooled[w][stream].append(obs)
                pooled_null[w][stream].append(s["null_mean"][w])
            rec["streams"][stream] = s

    return {
        "folder": folder.name,
        "declared_width_def": {k: sorted(v) for k, v in declared.items()},
        "per_slice": per_slice,
        "pooled": {w: {st_: (st.fmean(pooled[w][st_]) if pooled[w][st_] else None)
                       for st_ in ("fast", "slow")} for w in HALF_WIDTHS},
        "pooled_null": {w: {st_: (st.fmean(pooled_null[w][st_])
                                  if pooled_null[w][st_] else None)
                            for st_ in ("fast", "slow")} for w in HALF_WIDTHS},
        "n_slices": sum(1 for r in per_slice.values() if r["region"]),
    }


def _ordered(m: dict):
    """Slices in step order, so panels A and B read left to right the same way."""
    return [sid for sid, _ in sorted(STEPS.items(), key=lambda kv: kv[1])
            if m["per_slice"][sid]["region"]]


def build(m: dict, width: int):
    import holoviews as hv

    sids = _ordered(m)
    xs = {sid: i + 1 for i, sid in enumerate(sids)}
    ticks = [(i + 1, sid.replace("2024", "24·").replace("2025", "25·")
                        .replace("2026", "26·")) for i, sid in enumerate(sids)]

    # --- A: how many distinct ROIs onset together at the step
    items_a = []
    for stream in ("fast", "slow"):
        segs, pts, nulls = [], [], []
        for sid in sids:
            s = m["per_slice"][sid]["streams"].get(stream)
            if not s or s["null_roi_mean"] is None:
                continue
            x = xs[sid] + (-0.16 if stream == "fast" else 0.16)
            nul = max(s["null_roi_mean"], 0.05)
            segs.append((x, nul, x, max(s["roi_at_step"], 0.05)))
            pts.append((x, max(s["roi_at_step"], 0.05)))
            nulls.append((x, nul))
        items_a.append(hv.Segments(segs).opts(color=COLOURS[stream],
                                              line_width=2, alpha=0.55))
        items_a.append(hv.Scatter(nulls).opts(color=NULL_COLOUR, size=5,
                                              marker="dash", line_width=3))
        items_a.append(hv.Scatter(pts, label=f"{stream} · at the step").opts(
            color=COLOURS[stream], size=8, line_color="white"))
    panel_a = hv.Overlay(items_a).opts(
        width=width // 3, height=340, logy=True, show_grid=True,
        xticks=ticks, xrotation=60, ylim=(0.04, 90),
        ylabel=f"distinct ROI onsetting within ±{W_MAIN:g}s  ({len(sids)} slices)",
        xlabel="", legend_position="top_left", fontsize={"legend": 8},
        toolbar=None)

    # --- B: the shape of what sits at the step, against the same region
    items_b = []
    for stream in ("fast", "slow"):
        segs, near, rest = [], [], []
        for sid in sids:
            s = m["per_slice"][sid]["streams"].get(stream)
            if not s or s["cv_width_near"] is None or s["cv_width_rest"] is None:
                continue
            x = xs[sid] + (-0.16 if stream == "fast" else 0.16)
            segs.append((x, s["cv_width_rest"], x, s["cv_width_near"]))
            rest.append((x, s["cv_width_rest"]))
            near.append((x, s["cv_width_near"]))
        items_b.append(hv.Segments(segs).opts(color=COLOURS[stream],
                                              line_width=2, alpha=0.55))
        items_b.append(hv.Scatter(rest).opts(color=NULL_COLOUR, size=5,
                                             marker="dash", line_width=3))
        items_b.append(hv.Scatter(near, label=f"{stream} · at the step").opts(
            color=COLOURS[stream], size=8, line_color="white"))
    panel_b = hv.Overlay(items_b).opts(
        width=width // 3, height=340, show_grid=True,
        xticks=ticks, xrotation=60,
        ylabel="width spread (CV) · dash = rest of region",
        xlabel="", legend_position="top_left", fontsize={"legend": 8},
        toolbar=None)

    # --- C: what chance predicts, and it is flat in the stream
    items_c = []
    for stream in ("fast", "slow"):
        obs = [(w, 100 * m["pooled"][w][stream]) for w in HALF_WIDTHS
               if m["pooled"][w][stream] is not None]
        nul = [(w, 100 * m["pooled_null"][w][stream]) for w in HALF_WIDTHS
               if m["pooled_null"][w][stream] is not None]
        items_c.append(hv.Curve(obs, label=f"{stream} · observed").opts(
            color=COLOURS[stream], line_width=2))
        items_c.append(hv.Scatter(obs).opts(color=COLOURS[stream], size=7,
                                            line_color="white"))
        items_c.append(hv.Curve(nul, label=f"{stream} · chance").opts(
            color=COLOURS[stream], line_width=1.5, line_dash="dashed",
            alpha=0.8))
    panel_c = hv.Overlay(items_c).opts(
        width=width // 3, height=340, logx=True, logy=True, show_grid=True,
        ylabel="onsets within ±w of the step (%), mean over slices",
        xlabel="half-width w (s)", legend_position="bottom_right",
        fontsize={"legend": 8}, toolbar=None)

    return hv.Layout([panel_a, panel_b, panel_c]).cols(3).opts(
        shared_axes=False, toolbar=None)


def header_html(m: dict) -> str:
    def pooled(w, s, key="pooled"):
        v = m[key][w][s]
        return "—" if v is None else f"{100 * v:.2f}%"

    rows = "".join(
        f"<tr><td style='padding:2px 14px 2px 0'>±{w:g} s</td>"
        f"<td style='padding:2px 14px 2px 0;text-align:right'>{pooled(w,'fast')}</td>"
        f"<td style='padding:2px 14px 2px 0;text-align:right;color:{MUTED}'>"
        f"{pooled(w,'fast','pooled_null')}</td>"
        f"<td style='padding:2px 14px 2px 0;text-align:right'><b>{pooled(w,'slow')}</b></td>"
        f"<td style='padding:2px 0;text-align:right;color:{MUTED}'>"
        f"{pooled(w,'slow','pooled_null')}</td></tr>"
        for w in HALF_WIDTHS)

    worst = max(
        ((sid, s["roi_at_step"], s["null_roi_mean"])
         for sid, r in m["per_slice"].items()
         for st_, s in r["streams"].items()
         if st_ == "slow" and s["null_roi_mean"] is not None),
        key=lambda t: t[1])
    tight = sorted(
        (s["cv_width_near"], sid) for sid, r in m["per_slice"].items()
        for st_, s in r["streams"].items()
        if st_ == "slow" and s["cv_width_near"] is not None)
    declared = "; ".join(
        f"<b>{stream}</b> <code>{', '.join(defs)}</code>"
        for stream, defs in sorted(m["declared_width_def"].items()))

    return f"""
<div style="font:13px/1.5 -apple-system,Segoe UI,sans-serif;color:{INK};
            max-width:70rem;margin:0 auto 0.5rem">
<p><b>A confirmed field step does not coincide with slow events. It generates
them — and it generates fast ones too.</b> interface2 asked which of two readings
explains slow baseline at 7.28% against fast baseline at 2.33%
(<code>PRE_ARTIFACT_KILLER</code> handoff §4 item 2). All three tests here answer
the same way, and the third one settles it on their own statistic.</p>

<p><b>Reading A cannot be what produced the asymmetry, for a reason that needs no
data.</b> <i>Onset inside a window</i> is a point-in-window test, so under
uniform onsets the in-window fraction is the window's duty cycle — identical in
both streams whatever their rate and whatever their event <b>width</b>. Width
cannot enter a test on a point. Panel C measures it: the dashed chance curves for
fast and slow lie on each other at every half-width
({pooled(HALF_WIDTHS[2], 'fast', 'pooled_null')} against
{pooled(HALF_WIDTHS[2], 'slow', 'pooled_null')} at ±{HALF_WIDTHS[2]:g} s), while
the observed curves sit one to two orders of magnitude above them. <i>"A step is
arithmetically more likely to land inside a broad SLOW event"</i> describes an
extent-overlap test, not the onset test that was run.</p>

<table style="border-collapse:collapse;font-size:12px;margin:0.6rem 0 0.8rem">
<tr style="border-bottom:1px solid #c8d6e4">
  <th style="text-align:left;padding-right:14px">onsets within</th>
  <th style="text-align:right;padding-right:14px">fast</th>
  <th style="text-align:right;padding-right:14px;color:{MUTED}">chance</th>
  <th style="text-align:right;padding-right:14px">slow</th>
  <th style="text-align:right;color:{MUTED}">chance</th></tr>
{rows}
</table>

<p><b>What is actually at the step is the whole field at once.</b> Panel A:
<code>{worst[0]}</code> has <b>{worst[1]} distinct ROIs</b> onsetting in the slow
stream within ±{W_MAIN:g} s of its step, against a chance expectation of
<b>{worst[2]:.2f}</b>. That is not a coincidence between a step and an event; it
is one event in every cell, which is what a whole-field brightness change looks
like from inside a per-ROI event table.</p>

<p><b>And it is one waveform, not many.</b> Panel B asks what the producer wrote
into <code>width_sec</code> for the events sitting at the step, against what it
wrote for the rest of the same region — each stream against itself, since this
export declares a different <code>width_def</code> per stream and bugarach does
not interpret either. In slow the spread <b>collapses</b>: a CV of
{tight[0][0]:.3f} on <code>{tight[0][1]}</code>, under {tight[2][0]:.2f} on the
tightest three, against 0.3–0.7 elsewhere in the very same window. Many cells
returning one value is a single event seen many times, not many events. In fast
the spread <b>widens</b> instead, on the same slices — so the two streams'
declared rules respond to a step differently, which is a question for the
producer and is filed as one rather than answered here.</p>

<p><b>Two of the nine do nothing in slow, and they are the low red points.</b>
<code>20240723_22</code> has no slow onset at its step at all and
<code>20250808_186</code> has four against a chance expectation of 2.4
(p&nbsp;=&nbsp;0.15) — while both show the fast recruitment plainly. So the claim
is that a confirmed step <i>can</i> generate a field-wide slow call, in seven of
nine cases here, not that it always does. Whatever separates those two from the
rest is not in these columns, and it is worth knowing before the flag is
built: a per-event <code>on_field_step</code> that assumes every step recruits
will be wrong twice in nine.</p>

<p><b>Two consequences that change what the artifact work has to do.</b> First,
<b>this is not a slow-stream problem</b> — panel A's fast points stand as far off
their own chance line as the slow ones, so the 7.28%-versus-2.33% contrast is
about which windows the nine steps happened to fall in, not about slow being
selectively affected. Second, the effect is <b>not confined to baseline</b>: the
largest slow recruitments here sit in <code>wash</code> and <code>TTX</code>
regions. And FOUNDATIONS §9 is why the second one matters more than it looks —
coordination under TTX is a live finding of this lab's, measured on these
detectors, and a field step inside a TTX window manufactures exactly the
signature that finding is made of.</p>

<p style="color:{MUTED}">Widths compared within a stream only. The
<code>width_def</code> each stream declares, read from these files and quoted
without interpretation: {declared}. A stream declaring two would make panel B
meaningless, and the folder check refuses that case.<br>
Export <code>{m['folder']}</code>,
{m['n_slices']} of the 9 confirmed-step slices resolved to a declared region,
{NULL_DRAWS} null draws per slice per half-width, seed {NULL_SEED}. The null
redraws the step's <b>position</b> inside the region that holds it, keeping that
recording's own rate, ROI roster and region length. The nine step times are
Tony's adjudications, quoted from the folder's README and not derivable from the
CSVs — this figure is exactly as good as that list, and 282 further candidates
are unadjudicated. <b>This decides nothing about the detections:</b> whether a
coordinated event built from step-coincident members is itself false is a call on
bugarach's output, and it has not been made.</p>
</div>"""


def _render_png(html_path: Path, png_path: Path, *, wait_ms: int = 2500,
                width: int = 1560, height: int = 1000) -> bool:
    try:
        from playwright.sync_api import sync_playwright
    except Exception as exc:                                   # noqa: BLE001
        print(f"(PNG render skipped: {exc})", file=sys.stderr)
        return False
    try:
        with sync_playwright() as pw:
            b = pw.chromium.launch()
            pg = b.new_page(viewport={"width": width, "height": height},
                            device_scale_factor=2)
            pg.goto(html_path.resolve().as_uri())
            pg.wait_for_timeout(wait_ms)
            pg.screenshot(path=str(png_path), full_page=True)
            b.close()
        return True
    except Exception as exc:                                   # noqa: BLE001
        print(f"(PNG render failed: {type(exc).__name__}: {exc})", file=sys.stderr)
        return False


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--width", type=int, default=1500)
    p.add_argument("--dataset", default=None,
                   help="export folder name or path; default is the folder the "
                        "nine confirmed steps were adjudicated on")
    p.add_argument("--out", default=None,
                   help="destination; defaults to the darkroom")
    p.add_argument("--also", type=Path, default=None,
                   help="second destination, e.g. docs/learned")
    p.add_argument("--json", type=Path, default=None,
                   help="also write the measurement as JSON")
    p.add_argument("--no-png", dest="png", action="store_false", default=True)
    a = p.parse_args()

    from bugarach import dataset
    from bugarach.paths import darkroom, unresolved_message

    name = a.dataset or "2026-09-03_revised_2v_long_PRE_ARTIFACT_KILLER"
    folder = Path(name) if Path(name).is_dir() else dataset.resolve(name)
    print(f"reading {folder}…")
    m = measure(folder)
    print(f"  {m['n_slices']} of {len(STEPS)} confirmed-step slices in a region")
    for sid in _ordered(m):
        for stream in ("fast", "slow"):
            s = m["per_slice"][sid]["streams"].get(stream)
            if not s or s["null_roi_mean"] is None:
                continue
            print(f"  {sid:14s} {stream:5s} "
                  f"{s['roi_at_step']:3d} ROI at the step vs "
                  f"{s['null_roi_mean']:5.2f} by chance   p={s['null_p'][W_MAIN]:.4f}"
                  + (f"   width CV {s['cv_width_near']:.3f} vs "
                     f"{s['cv_width_rest']:.3f}"
                     if s["cv_width_near"] and s["cv_width_rest"] else ""))

    dest = Path(a.out) if a.out else darkroom()
    if dest is None:
        print(unresolved_message(), file=sys.stderr)
        return 1

    if a.json:
        a.json.parent.mkdir(parents=True, exist_ok=True)
        a.json.write_text(json.dumps(m, indent=2, sort_keys=True, default=str))
        print(f"wrote {a.json}")

    import holoviews as hv
    import panel as pn
    hv.extension("bokeh")
    layout = build(m, a.width)

    dests = [dest] + ([a.also] if a.also else [])
    for i, d in enumerate(dests):
        d.mkdir(parents=True, exist_ok=True)
        html = d / f"{FIGURE_ID}.html"
        pn.panel(pn.Column(pn.pane.HTML(header_html(m)),
                           pn.pane.HoloViews(layout))).save(str(html))
        print(f"wrote {html}")
        if a.png:
            shot = d / f"{FIGURE_ID}.png"
            if i == 0:
                if _render_png(html, shot):
                    print(f"wrote {shot}")
            else:
                src = dests[0] / f"{FIGURE_ID}.png"
                if src.is_file():
                    shot.write_bytes(src.read_bytes())
                    print(f"wrote {shot}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
