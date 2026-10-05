#!/usr/bin/env python3
"""Build the report on goal 2's fair comparison as TWO independent draws, for a reader new to it.

    python tools/make_replicate_report.py --rehearsal <shakedown results.json>
    python tools/make_replicate_report.py --rehearsal ... --also docs/learned/tuned_vs_coact/replicate1/report.html

WSMIP064 ran the fair comparison of the learned detectors against the coded ones on bench recording
seeds 1000-1047 (the first draw); WSMIP065 ran the same declared comparison on seeds 2000-2047
(`--replicate 1`, the second draw). This page explains what was done and why, conceptually first,
then what the PAIR of runs can claim that either alone cannot. It is WSMIP065's report; WSMIP064
writes its own for its run.

**Where the page's numbers come from.** Every RESULT — each score, gap, count, rate, flag and
parameter count — is computed here from the two runs' own files in their darkroom `results/`
folders (`results.json`, `meta.json`, `selections/`, `configs/`, and the fit and score archives),
from the rehearsal's own `results.json` (`--rehearsal`), and from `bugarach.bench` and
`bugarach.score`. The build asserts every headline sentence against those numbers, so a claim that
stops being true stops the build instead of shipping. The HISTORY and CONTEXT the page gives — why a
choice was made, what an earlier measurement found — is written by hand and cites the file it
comes from. The first draft said "nothing is typed by hand"; its murderboard showed that was false,
and a hand-typed number from a third run was the result.

**Output goes to the darkroom by default** (CLAUDE.md, SAP006); `--also` writes the repo copy. The
page is one self-contained HTML file: figures are inline SVG, and the one raster is a PNG data URI
rendered through `tools/make_diagnostic.py`'s own Playwright path.

**The matched merge.** Each draw's held-out output was re-decoded with the nets and CoactDetect at
the same merge gap by `tools/fair_comparison_evidence.py merge-gap` (WSMIP064's tool, branch
`nets/fair-comparison-report`), run unchanged on each draw; `--merge-gap-mine` and
`--merge-gap-theirs` name the two files, and `matched_gaps` refuses one that does not reproduce its
run.

**The architecture figure is not drawn here.** Both workstations' reports must carry the SAME
drawing of the four nets, which the project's drafting tooling produces; Figure 2 is a marked slot
for it.
"""

from __future__ import annotations

import argparse
import base64
import html
import io
import json
import math
import re
import statistics as st
import sys
import tarfile
import tempfile
import zipfile
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / "src"))
sys.path.insert(0, str(REPO / "tools"))

MINE_FOLDER = "2026-09-18-replicate-run-status"
THEIRS_FOLDER = "2026-09-18-fair-comparison-run"
THEIRS_MERGE_GAP = "docs/learned/tuned_vs_coact/fair_comparison_2026_09_18/merge_gap.json"
THEIRS_CROWDED = "docs/learned/tuned_vs_coact/fair_comparison_2026_09_18/crowded_check.json"
ARCH_SVG = "docs/learned/comparison/comparison.svg"

# The two draws, in the order the page always shows them. Color follows the draw, never its rank
# (slots 1 and 2 of the reference categorical palette, validated for color-vision deficiency).
DRAWS = (
    dict(key="a", name="first draw", machine="WSMIP064", folder=THEIRS_FOLDER),
    dict(key="b", name="second draw", machine="WSMIP065", folder=MINE_FOLDER),
)

NETS = ("chorus_norm", "chorus_gain_norm", "line_length", "tube")
# The glossary's canonical order for the coded detectors (docs/GLOSSARY.md).
CODED = ("rate", "coact", "loco", "sce", "cicada", "sync")
NAMES = {"coact": "CoactDetect", "loco": "LoCo", "rate": "rate+context", "sce": "binned SCE",
         "sync": "SPIKE-synch", "cicada": "locust", "chorus_norm": "chorus_norm",
         "chorus_gain_norm": "chorus_gain_norm", "line_length": "line_length", "tube": "tube"}
SEL_WORDS = {"untuned": "untuned", "ungated": "on F1 alone", "gated": "under the budget"}
# Each coded detector's setting for how close two calls may be before they count as one.
FUSE = {"coact": "merge_gap_sec", "loco": "merge_gap_sec", "sce": "merge_gap_sec",
        "rate": "merge_gap_s", "sync": "max_gap", "cicada": "sce_min_distance_frames"}
FUSE_WORDS = {"merge_gap_sec": "merge gap", "merge_gap_s": "merge gap", "max_gap": "maximum gap",
              "sce_min_distance_frames": "minimum distance between calls"}


# ---- reading the runs --------------------------------------------------------------------------

class Archive:
    """The fit or score archive of one run: a .zip (WSMIP065) or a .tar.gz (WSMIP064)."""

    def __init__(self, folder: Path, stem: str):
        z, t = folder / f"{stem}.zip", folder / f"{stem}.tar.gz"
        self.path = z if z.is_file() else t
        if not self.path.is_file():
            raise SystemExit(f"{folder}: neither {stem}.zip nor {stem}.tar.gz")

    def items(self, want):
        """(name, bytes) for every member whose normalised name satisfies ``want``."""
        if self.path.suffix == ".zip":
            with zipfile.ZipFile(self.path) as z:
                for n in z.namelist():
                    nn = n.replace("\\", "/").lstrip("./")
                    if want(nn):
                        yield nn, z.read(n)
        else:
            with tarfile.open(self.path, "r:gz") as t:
                for m in t:
                    if not m.isfile():
                        continue
                    nn = m.name.replace("\\", "/").lstrip("./")
                    if want(nn):
                        yield nn, t.extractfile(m).read()


def load_run(folder: Path) -> dict:
    res = json.loads((folder / "results.json").read_text(encoding="utf-8"))
    meta = json.loads((folder / "meta.json").read_text(encoding="utf-8"))
    return dict(results=res, meta=meta, decl=meta["declaration"], folder=folder)


def fold_f1(entry: dict) -> float:
    """One outer fold's held-out F1, as the run wrote it: a net's `f1_mean` over its refit seeds
    (0.0 where the run recorded no admissible configuration — the tuner's own rule), a coded
    detector's `f1`."""
    if "f1_mean" in entry:
        return float(entry["f1_mean"] or 0.0)
    return float(entry.get("f1") or 0.0)


def table(run: dict) -> dict:
    """{(name, selection): [held-out F1 per outer fold]} for every net and coded detector."""
    out = {}
    for m, folds in run["results"]["learned"].items():
        for w in ("untuned", "ungated", "gated"):
            out[(m, w)] = [fold_f1(f[w]) for f in folds]
    for d, folds in run["results"]["hand"].items():
        for w in ("ungated", "gated"):
            out[(d, w)] = [fold_f1(f[w]) for f in folds]
    return out


def declaration_difference(a: dict, b: dict) -> list[str]:
    keys = set(a["decl"]) | set(b["decl"])
    return sorted(k for k in keys if a["decl"].get(k) != b["decl"].get(k))


def seed_flags(run: dict, net: str, sel: str) -> list[dict]:
    """Refit seeds that failed to train (the run's `failed_training_signature`) or called nothing
    on the held-out fold (`f1_was_nan`)."""
    out = []
    for f in run["results"]["learned"][net]:
        for s in f[sel].get("per_seed", []):
            if s.get("failed_training_signature") or s.get("f1_was_nan"):
                out.append(dict(fold=f["outer_fold"], seed=s["seed"], f1=s["f1"],
                                failed=bool(s.get("failed_training_signature")),
                                nothing=bool(s.get("f1_was_nan")), config=f[sel]["config_key"]))
    return out


def refused_everything(run: dict) -> dict:
    """{(detector, fold): (n_refused, n_scored)} for budgeted coded searches that found NO
    admissible candidate among the settings they reached; they then return their starting point."""
    out = {}
    for d in run["results"]["hand"]:
        for h in range(run["decl"]["folds"]):
            p = run["folder"] / "selections" / "gated" / f"outer{h}" / f"{d}.json"
            if p.exists():
                s = json.loads(p.read_text(encoding="utf-8"))
                if s["n_scored"] and s["n_refused"] == s["n_scored"]:
                    out[(d, h)] = (s["n_refused"], s["n_scored"])
    return out


def selection(run: dict, sel: str, h: int, det: str) -> dict:
    return json.loads((run["folder"] / "selections" / sel / f"outer{h}" / f"{det}.json")
                      .read_text(encoding="utf-8"))


def crowded_refused(crowded: dict | None) -> set:
    """{(detector, selection, fold)} whose choice fails goal 1's crowded-recording veto, from
    WSMIP064's `crowded_check_fair_comparison.py` output for that draw (`passes_veto`)."""
    if not crowded:
        return set()
    return {(c["detector"], c["selection"], c["outer_fold"]) for c in crowded["choices"]
            if not c["passes_veto"]}


def flagged(run: dict, entry) -> bool:
    """An entry is flagged in a draw when any fold carries a † (a refit seed failed or called
    nothing), a ‡ (the budgeted search reached no admissible setting) or a § (the choice fails goal
    1's crowded-recording veto). The same rule marks Table 1 and decides which entries the
    between-draw spread leaves out, so the two cannot disagree."""
    name, sel = entry
    if name in NETS:
        return bool(seed_flags(run, name, sel))
    if any((name, sel, h) in run.get("crowded", set()) for h in range(4)):
        return True
    return sel == "gated" and any((name, h) in refused_everything(run) for h in range(4))


def held_out_compliance(run: dict) -> dict:
    """What the run itself wrote about the held-out folds against each fold's ceilings:
    nets → refit seeds over budget (of all refit seeds); coded → folds over budget."""
    out = {}
    for m, folds in run["results"]["learned"].items():
        n = sum(f["gated"]["n_seeds"] for f in folds)
        over = sum(f["gated"].get("seeds_over_budget") or 0 for f in folds)
        out[m] = (over, n, "refit seeds")
    for d, folds in run["results"]["hand"].items():
        over = sum(1 for f in folds if f["gated"].get("over_budget"))
        out[d] = (over, len(folds), "folds")
    return out


def archive_facts(run: dict) -> dict:
    """What the fit and score archives say, in one pass each: how many recordings a net fit
    trains on and picks its threshold on, how many refits each net made, how often inner fits
    collapsed to one call per recording, and the held-out false alarms split three ways for every
    entry chosen under the budget and on F1 alone."""
    decl, res = run["decl"], run["results"]
    fits = {}                          # (net, cfg, seed, recs) -> run record
    for name, raw in Archive(run["folder"], "fits").items(lambda n: n.endswith(".run.json")):
        parts = name.split("/")
        net, cfg, stem = parts[-3], parts[-2], parts[-1][: -len(".run.json")]
        m = re.match(r"seed(\d+)__recs-([0-9a-f]+)$", stem)
        rec = json.loads(raw)
        fits[(net, cfg, int(m.group(1)), m.group(2))] = rec
    n_train = sorted({len(r["fitted_recordings"]) for r in fits.values()})
    n_thresh = sorted({len(r["threshold_recordings"]) for r in fits.values()})
    refits = {net: sum(1 for (n, *_), r in fits.items() if n == net and r["role"] != "inner")
              for net in NETS}

    # which held-out rows to read: (net, fold, cfg, seed) -> threshold index, per selection
    want = {}
    for sel in ("ungated", "gated"):
        for net in NETS:
            for f in res["learned"][net]:
                h, cfg = f["outer_fold"], f[sel]["config_key"]
                for s in f[sel].get("per_seed", []):
                    want.setdefault((net, h, cfg, s["seed"]), {})[sel] = s["threshold_index"]
    folds_all = set(range(decl["folds"]))
    outer_recs = {}
    for (net, cfg, seed, recs), r in fits.items():
        if r["role"] != "inner":
            h = next(iter(folds_all - set(r["train_folds"])))
            outer_recs[(net, h, cfg, seed)] = recs

    one_call = {}                      # (net, inner fit) -> [scorings with one call, scorings]
    rows_by = {}                       # (name, sel) and (name, sel, background) -> score rows
    def add(key, row, background):
        for k in (key, key + (background,)):
            rows_by.setdefault(k, []).append(row)

    for name, raw in Archive(run["folder"], "scores").items(lambda n: n.startswith("scores/")):
        parts = name.split("/")
        if len(parts) == 4:            # a net: scores/<net>/<cfg>/seed<s>__recs-<h>__fold<j>.json
            net, cfg = parts[1], parts[2]
            m = re.match(r"seed(\d+)__recs-([0-9a-f]+)__fold(\d+)\.json$", parts[3])
            seed, recs, j = int(m.group(1)), m.group(2), int(m.group(3))
            role = fits.get((net, cfg, seed, recs), {}).get("role")
            d = json.loads(raw)
            if role == "inner":
                oi = d["own_index"]
                pair = tuple(sorted(fits[(net, cfg, seed, recs)]["train_folds"]))
                c = one_call.setdefault((net, cfg, seed, pair), [0, 0])
                c[1] += 1
                c[0] += all(rows[oi]["n_detected"] == 1 for rows in d["rows"].values())
            elif outer_recs.get((net, j, cfg, seed)) == recs and (net, j, cfg, seed) in want:
                for sel, ti in want[(net, j, cfg, seed)].items():
                    for rec_name, rows in d["rows"].items():
                        add((net, sel), rows[ti], rec_name.split(":")[0])
        elif len(parts) == 3 and "__" in parts[2]:   # a coded detector: scores/<det>/outer<h>__<sel>.json
            d = json.loads(raw)
            for rec_name, row in d["rows"].items():
                add((parts[1], d["selection"]), row, rec_name.split(":")[0])
    # An inner fit collapsed when it made exactly one call on every recording of EVERY fold it was
    # scored on; each inner fit is scored on the two folds outside its training pair.
    collapsed = {net: [sum(1 for (n, *_), (k, s) in one_call.items() if n == net and k == s),
                       sum(1 for (n, *_), (k, s) in one_call.items() if n == net and 0 < k < s),
                       sum(1 for (n, *_) in one_call if n == net)] for net in NETS}
    # the fits themselves, keyed by what the two draws share (configuration, training seed and fold
    # pair), so the draws can be compared fit by fit
    collapsed_keys = {k for k, (c, s) in one_call.items() if c == s}
    split = {k: pooled(v) for k, v in rows_by.items()}
    return dict(n_train=n_train, n_thresh=n_thresh, refits=refits, collapsed=collapsed,
                collapsed_keys=collapsed_keys, split=split)


def pooled(rows: list) -> dict:
    """Stored score rows pooled through `bench.pool_scores`, the project's one pooling rule (it
    refuses rows scored at mixed tolerances), with the counts the page reads beside the result."""
    from types import SimpleNamespace

    from bugarach.bench import pool_scores
    res = pool_scores([SimpleNamespace(**{**r, "by_frac": {float(f): (n, h) for f, (n, h)
                                                           in r["by_frac"].items()}})
                       for r in rows], detector="report", regime="held-out")
    return dict(n=len(rows), hit=res.n_hit, planted=res.n_planted, detected=res.n_detected,
                fa=res.n_fa, dense=res.hot_fa, by_frac=dict(res.by_frac), res=res)


def prf(t: dict) -> tuple[float, float, float]:
    """Recall, precision and F1 of pooled score rows, from the bench's own `BenchResult`: precision
    leaves out calls overlapping the dense stretch (`BenchResult.n_scored`)."""
    r = t["res"]
    return r.recall, r.precision, r.f1


# ---- formatting --------------------------------------------------------------------------------

def f3(x) -> str:
    return "—" if x is None or (isinstance(x, float) and math.isnan(x)) else f"{x:.3f}"


def sgn(x: float) -> str:
    s = f"{x:+.3f}"
    return "0.000" if s in ("+0.000", "-0.000") else s.replace("-", "−")


def sci(x: float) -> str:
    """1e-05 as 10⁻⁵, which is how a reader writes it."""
    e = int(round(math.log10(x)))
    if abs(x - 10 ** e) < 1e-12 * max(1, abs(x)):
        return "10" + str(e).translate(str.maketrans("-0123456789", "⁻⁰¹²³⁴⁵⁶⁷⁸⁹"))
    return f"{x:g}"


def esc(s) -> str:
    return html.escape(str(s), quote=True)


# ---- SVG: every figure is built here, in page tokens, so dark mode is the same drawing -----------

_SVG_N = [0]

# An SVG element's tooltip tag. Named through a constant because sapper SAP005 reads any string that
# opens with that tag as an HTML document missing its charset; an SVG has no head to hold one (the
# same false positive sapper.py records for draughtsman's SVGs). The page's own head declares it.
SVG_TITLE = "title"


class Svg:
    """A minimal SVG writer. Colors are CSS custom properties, so the page's light and dark themes
    restyle one drawing. Each drawing gets its own id prefix, so markers and patterns never collide
    between the page's inline SVGs."""

    def __init__(self, w: int, h: int, label: str):
        _SVG_N[0] += 1
        self.id = f"s{_SVG_N[0]}"
        self.w, self.h, self.parts, self.label = w, h, [], label

    def add(self, s: str):
        self.parts.append(s)

    def text(self, x, y, s, *, size=13, anchor="start", weight="normal", fill="var(--ink)",
             italic=False):
        style = "font-style:italic;" if italic else ""
        self.add(f'<text x="{x:.1f}" y="{y:.1f}" font-size="{size}" text-anchor="{anchor}" '
                 f'font-weight="{weight}" fill="{fill}" style="{style}">{esc(s)}</text>')

    def line(self, x1, y1, x2, y2, *, stroke="var(--rule)", width=1, dash=None):
        d = f' stroke-dasharray="{dash}"' if dash else ""
        self.add(f'<line x1="{x1:.1f}" y1="{y1:.1f}" x2="{x2:.1f}" y2="{y2:.1f}" '
                 f'stroke="{stroke}" stroke-width="{width}"{d}/>')

    def rect(self, x, y, w, h, *, fill="none", stroke="none", width=1, rx=0, title=None, dash=None):
        t = f"<{SVG_TITLE}>{esc(title)}</{SVG_TITLE}>" if title else ""
        d = f' stroke-dasharray="{dash}"' if dash else ""
        fill = fill.replace("url(#hatch)", f"url(#{self.id}-hatch)")
        self.add(f'<rect x="{x:.1f}" y="{y:.1f}" width="{w:.1f}" height="{h:.1f}" rx="{rx}" '
                 f'fill="{fill}" stroke="{stroke}" stroke-width="{width}"{d}>{t}</rect>')

    def circle(self, x, y, r, *, fill, stroke="var(--surface)", width=1, title=None, hollow=False,
               opacity=1.0):
        t = f"<{SVG_TITLE}>{esc(title)}</{SVG_TITLE}>" if title else ""
        if hollow:
            self.add(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="{r}" fill="var(--surface)" '
                     f'stroke="{fill}" stroke-width="2">{t}</circle>')
        else:
            self.add(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="{r}" fill="{fill}" stroke="{stroke}" '
                     f'stroke-width="{width}" fill-opacity="{opacity}">{t}</circle>')

    def edge(self, x, y, pointing, *, fill, title=None):
        """A value beyond the axis, drawn AT the edge as a triangle pointing off it, so it cannot
        be read as a value at the edge."""
        t = f"<{SVG_TITLE}>{esc(title)}</{SVG_TITLE}>" if title else ""
        d = 6 if pointing == "right" else -6
        self.add(f'<path d="M{x + d:.1f},{y:.1f} L{x - d:.1f},{y - 5:.1f} L{x - d:.1f},{y + 5:.1f} z" '
                 f'fill="{fill}">{t}</path>')

    def dot(self, x, y, lo_x, hi_x, r, *, fill, title=None, hollow=False, opacity=0.8):
        """A dot at x, or an edge triangle when x lies outside [lo_x, hi_x]."""
        if x < lo_x:
            self.edge(lo_x, y, "left", fill=fill, title=title)
        elif x > hi_x:
            self.edge(hi_x, y, "right", fill=fill, title=title)
        else:
            self.circle(x, y, r, fill=fill, stroke="none", width=0, title=title, hollow=hollow,
                        opacity=opacity)

    def arrow(self, x1, y1, x2, y2):
        self.add(f'<path d="M{x1:.1f},{y1:.1f} L{x2:.1f},{y2:.1f}" stroke="var(--ink-2)" '
                 f'stroke-width="1.4" fill="none" marker-end="url(#{self.id}-arrow)"/>')

    def render(self) -> str:
        i = self.id
        defs = (f'<defs><marker id="{i}-arrow" viewBox="0 0 10 10" refX="9" refY="5" '
                'markerWidth="7" markerHeight="7" orient="auto-start-reverse">'
                '<path d="M0,0 L10,5 L0,10 z" fill="var(--ink-2)"/></marker>'
                f'<pattern id="{i}-hatch" width="6" height="6" patternUnits="userSpaceOnUse" '
                'patternTransform="rotate(45)"><line x1="0" y1="0" x2="0" y2="6" '
                'stroke="var(--ink-3)" stroke-width="1.5"/></pattern></defs>')
        return (f'<div class="figscroll"><svg viewBox="0 0 {self.w} {self.h}" width="100%" '
                f'role="img" aria-label="{esc(self.label)}" xmlns="http://www.w3.org/2000/svg" '
                f'style="max-width:{self.w}px;min-width:{min(self.w, 820)}px;font-family:inherit">'
                f'{defs}{"".join(self.parts)}</svg></div>')


def x_axis(svg: Svg, x0, x1, y, lo, hi, ticks, label, fmt="{:.1f}"):
    """The axis, and the UNCLAMPED scale: callers draw off-axis values with `Svg.dot`."""
    sx = lambda v: x0 + (v - lo) / (hi - lo) * (x1 - x0)
    svg.line(x0, y, x1, y, stroke="var(--ink-3)")
    for t in ticks:
        svg.line(sx(t), y, sx(t), y + 4, stroke="var(--ink-3)")
        s = fmt.format(t)
        s = s.lstrip("+") if float(s) == 0 else s
        svg.text(sx(t), y + 17, s.replace("-", "−"), size=12, anchor="middle", fill="var(--ink-2)")
    svg.text((x0 + x1) / 2, y + 34, label, size=12, anchor="middle", fill="var(--ink-2)")
    return sx


def box(svg, x, y, w, h, lines, *, fill="var(--box)", stroke="var(--ink-3)", size=12, bold0=False):
    svg.rect(x, y, w, h, fill=fill, stroke=stroke, width=1.2, rx=6)
    n = len(lines)
    for i, s in enumerate(lines):
        svg.text(x + w / 2, y + h / 2 + (i - (n - 1) / 2) * (size + 3) + size / 3, s, size=size,
                 anchor="middle", weight="bold" if (bold0 and i == 0) else "normal")


# ---- the one raster: a real bench recording from this draw -------------------------------------

def raster_png(regime: str, seed: int, coact_params: dict) -> tuple[bytes, dict]:
    """One bench recording rendered with `bugarach.ui.diagnostic`.

    Nothing is drawn on the raster (CLAUDE.md): planted events, distractors, the dense stretch and
    CoactDetect's calls sit in the lane above. `raster_panel` gets ``gt=None`` because, given the
    ground truth, it shades the dense stretch across the marks (filed: docs/todo/
    2026-09-19-raster-panel-shades-the-probe-band-on-the-raster.md). CoactDetect runs through
    `bench.run_detector` — the path that scored the runs — at the budget's reference settings, read
    from the run's declaration, and is scored through `score_stream`, as the runs were.

    The key is NOT `diagnostic.legend_html` rendered into the picture: that key is shared by every
    diagnostic and lists marks this figure does not draw (a threshold line, a second detector, the
    duplicate ring), and inside a PNG it shrinks below body text on a phone. The page writes its own
    key from the facts returned here, so it lists exactly the marks that are drawn.
    """
    import holoviews as hv
    import numpy as np
    import panel as pn

    hv.extension("bokeh")
    import make_diagnostic as md
    from bugarach.bench import make_recording, run_detector
    from bugarach.detectors.rate import recording_extent
    from bugarach.score import _gap, _spans, score_stream
    from bugarach.ui.diagnostic import SEPARABLE_PX, lane_panel, raster_panel

    slice_, gt = make_recording(regime, seed)
    ext = recording_extent(slice_)
    r = run_detector("coact", slice_, **dict(coact_params))
    events = (r.onset_sec, r.width_sec)
    width = 1000
    top = lane_panel({"coact": events}, ext=ext, gt=gt, width=width)
    bottom = raster_panel(slice_.streams["events"], ext=ext, gt=None, name="simulated",
                          height=220).opts(xlabel="time")
    fig = (top + bottom).cols(1).opts(shared_axes=True, merge_tools=True, toolbar=None)
    page = pn.Column(pn.pane.HoloViews(fig))
    with tempfile.TemporaryDirectory() as td:
        out = Path(td) / "raster.html"
        page.save(str(out), embed=True)
        png = Path(td) / "raster.png"
        if not md._render_png(out, png):
            raise SystemExit("the raster did not render (Playwright chromium): "
                             "python -m playwright install chromium")
        data = _crop_to_ink(png.read_bytes())
    sc = score_stream(gt, r)
    # Which calls sit on a distractor, by score.py's own gap rule. `Score.distractor_hits` is not
    # this: it counts distractors touched by ANY call, matched calls included.
    lo, hi = _spans(events[0], events[1])
    dt = np.asarray(gt.distractor_times, dtype=float)
    on_d = lambda a, b: bool(dt.size) and bool(np.any(_gap(dt, a, b) <= sc.tol_sec))
    used = np.zeros(lo.size, dtype=bool)
    for m in sc.matched[np.isfinite(sc.matched)]:
        used |= lo == m
    fa_on = sum(on_d(a, b) for a, b in zip(lo[~used], hi[~used]))
    # distractors that only a MATCHED call covers: a merge long enough to join a distractor to a
    # nearby planted event hides the distractor inside a hit
    hidden = sum(1 for t in dt
                 if np.any(_gap(t, lo[used], hi[used]) <= sc.tol_sec)
                 and not np.any(_gap(t, lo[~used], hi[~used]) <= sc.tol_sec))
    # the same split lane_panel draws: ✕ for a false alarm, ○ for one it cannot separate from a hit
    dup = set(np.round(sc.dup_times, 6).tolist())
    spurious = np.array([t for t in sc.fa_times if round(float(t), 6) not in dup])
    won = sc.matched[np.isfinite(sc.matched)]
    near = float(ext[1] - ext[0]) / width * SEPARABLE_PX
    ring = len(dup) + (int(sum(np.min(np.abs(won - t)) <= near for t in spurious))
                       if spurious.size and won.size else 0)
    p = gt.params
    facts = dict(n_roi=int(p["n_roi"]), duration_sec=float(p["duration_sec"]),
                 hot_window=tuple(float(x) for x in p["hot_window"]),
                 participation=tuple(float(x) for x in p["participation"]),
                 n_per_level=tuple(int(x) for x in p["n_per_level"]),
                 jitter_sec=float(p["jitter_sec"]), min_sep_sec=float(p["min_sep_sec"]),
                 n_distractors=int(p["n_distractors"]),
                 distractor_frac=float(p["distractor_frac"]),
                 dt=float(slice_.dt), n_part=[int(e.n_part) for e in gt.events],
                 n_dist_part=[int(d.n_part) for d in gt.distractors],
                 n_planted=int(len(gt.times)), n_calls=int(len(r.onset_sec)),
                 n_hit=int(sc.n_hit), n_fa=int(sc.n_fa), hot_fa=int(sc.hot_fa),
                 fa_on_distractor=int(fa_on), distractors_in_hits=int(hidden),
                 n_ring=int(ring), n_missed=int(sc.n_miss))
    return data, facts


def _crop_to_ink(png: bytes, pad: int = 24) -> bytes:
    """Trim the rendered page's empty margin so the lane and raster fill the column: the render
    leaves about a sixth of its width blank on the right, which also shrinks every label in it."""
    from PIL import Image, ImageChops

    im = Image.open(io.BytesIO(png)).convert("RGB")
    box = ImageChops.difference(im, Image.new("RGB", im.size, (255, 255, 255))).getbbox()
    if box is None:
        return png
    x0, y0, x1, y1 = box
    im = im.crop((max(0, x0 - pad), max(0, y0 - pad), min(im.width, x1 + pad),
                  min(im.height, y1 + pad)))
    out = io.BytesIO()
    im.save(out, format="PNG", optimize=True)
    return out.getvalue()


def figure1_key(rf: dict) -> str:
    """Figure 1's key: only the marks the figure draws, symbol first, in page text."""
    from bugarach.ui.diagnostic import (COLORS, FALSE_ALARM, FOUND, MISSED, PROBE_BAND,
                                        RASTER_INK, _key)
    rows = [(_key("inverted", FOUND), "planted event that CoactDetect's calls matched")]
    if rf["n_missed"]:
        rows.append((_key("inverted", MISSED), "planted event no call matched"))
    rows += [(_key("inverted_open", "#5a5a5a"), "distractor: a burst built like a planted event "
                                                "placed at random; a call on one is a false alarm"),
             (_key("bar", COLORS.get("coact", "#555")), "one CoactDetect call, spanning its "
                                                        "onset to its end"),
             (_key("x", FALSE_ALARM), "a call that matched no planted event (a false alarm)")]
    if rf["n_ring"]:
        rows.append((_key("circle", FALSE_ALARM), "a false alarm too close to a matched call for "
                                                  "this figure to separate"))
    rows += [(_key("band", PROBE_BAND), "the dense stretch: faster firing, nothing planted"),
             (_key("tick", RASTER_INK), "one calcium event of one ROI (the raster)")]
    cells = "".join(f'<div class="k1"><span>{k}</span><span>{t}</span></div>' for k, t in rows)
    return f'<div class="key1">{cells}</div>'


# ---- figures -----------------------------------------------------------------------------------

def fig_nested_cv(label: str, n_folds: int, per_fold: int, n_configs: int, n_tune: int,
                  n_refit: int, n_train: int, n_thresh: int, n_coded: int, min_gain: float) -> str:
    """One run's nested cross-validation, drawn for held-out fold 0."""
    w, h = 980, 440
    svg = Svg(w, h, label)
    x0, fw, fh, y0 = 150, 180, 44, 30
    svg.text(x0 - 12, y0 + fh / 2 + 4, f"{n_folds * per_fold} recording seeds", anchor="end",
             size=12, weight="bold")
    svg.text(x0 - 12, y0 + fh / 2 + 19, "× 2 backgrounds", anchor="end", size=12,
             fill="var(--ink-2)")
    for f in range(n_folds):
        box(svg, x0 + f * (fw + 12), y0, fw, fh,
            [f"outer fold {f}", f"{per_fold} seeds · {2 * per_fold} recordings"],
            fill="var(--held)" if f == 0 else "var(--box)", bold0=True)
    svg.text(x0 + fw / 2, y0 + fh + 16, "held out: scored once, at the end", size=12,
             anchor="middle", fill="var(--ink-2)")
    svg.text(x0 + fw + 12 + (3 * fw + 24) / 2, y0 + fh + 16,
             "training folds: everything is chosen here", size=12, anchor="middle",
             fill="var(--ink-2)")
    yi = 120
    svg.text(24, yi + 4, "learned model", size=13, weight="bold")
    svg.text(24, yi + 20, "inner selection", size=12, fill="var(--ink-2)")
    for k, (a, b) in enumerate([(1, 2), (1, 3), (2, 3)]):
        yy = yi + k * 40
        for f in range(1, n_folds):
            fit = f in (a, b)
            svg.rect(x0 + f * (fw + 12), yy, fw, 30, rx=5,
                     fill="var(--box)" if fit else "var(--score)", stroke="var(--ink-3)")
            svg.text(x0 + f * (fw + 12) + fw / 2, yy + 20, "fit" if fit else "score",
                     size=12, anchor="middle")
    for i, s in enumerate([f"{n_configs} configurations", f"× {n_tune} training repeats",
                           "× 3 fold pairs"]):
        svg.text(x0 + fw / 2, yi + 30 + 16 * i, s, size=12, anchor="middle")
    svg.text(x0 + fw / 2, yi + 84, "best inner F1 wins", size=12, anchor="middle", weight="bold")
    yr = 250
    box(svg, x0 + fw + 12, yr, 3 * fw + 24, 40,
        [f"refit the winner at {n_refit} training repeats, each on {n_train} recordings "
         f"drawn from these folds"], fill="var(--box)")
    svg.arrow(x0 + fw + 10, yr + 20, x0 + fw - 2, yr + 20)
    box(svg, x0, yr, fw - 8, 40, ["score on fold 0"], fill="var(--held)")
    yc = 320
    svg.text(24, yc + 24, "coded detector", size=13, weight="bold")
    svg.text(24, yc + 40, "coordinate search", size=12, fill="var(--ink-2)")
    box(svg, x0 + fw + 12, yc, 3 * fw + 24, 62,
        [f"walk each setting's grid in turn, scoring on all {n_coded} training recordings;",
         f"keep a move only if F1 rises by more than {min_gain:g} (under the budget: among",
         "admissible settings, and an over-budget start first moves toward the ceilings)"],
        fill="var(--box)")
    svg.arrow(x0 + fw + 10, yc + 31, x0 + fw - 2, yc + 31)
    box(svg, x0, yc + 11, fw - 8, 40, ["score on fold 0"], fill="var(--held)")
    svg.text(w / 2, 420, f"Repeated with each of the {n_folds} folds held out. Nothing about a "
                         "held-out fold is chosen with that fold's recordings.",
             size=12, anchor="middle", fill="var(--ink-2)")
    return svg.render()


def fig_budget(label: str, b: dict, margin: float, alpha: float, busy_sec: float,
               bg_quiet: float, context: float) -> str:
    """How the shared false-alarm budget is set, with one fold's real numbers."""
    w, h = 980, 260
    svg = Svg(w, h, label)
    y = 76
    box(svg, 20, y, 210, 76, ["CoactDetect", f"sliding, α = {sci(alpha)},", f"context {context:g} s"],
        fill="var(--ref)", bold0=True)
    box(svg, 290, y - 30, 250, 56, [f"dense stretch, {busy_sec:g} s per recording,",
                                    "nothing planted"])
    box(svg, 290, y + 50, 250, 56, ["empty recording: bench background",
                                    f"at {bg_quiet:g} events/s per ROI, nothing planted"])
    svg.arrow(232, y + 30, 288, y)
    svg.arrow(232, y + 46, 288, y + 76)
    rp, rq = b["reference_probe_per_hour"], b["reference_quiet_per_hour"]
    pp, qq = b["probe_per_hour"], b["quiet_per_hour"]
    box(svg, 600, y - 30, 170, 56, [f"quiet: {rp['quiet']:.1f} calls/hour",
                                    f"busy: {rp['busy']:.1f} calls/hour"])
    box(svg, 600, y + 50, 170, 56, [f"{rq:.2f} calls/hour"])
    svg.arrow(542, y, 598, y)
    svg.arrow(542, y + 76, 598, y + 76)
    box(svg, 820, y - 30, 150, 56, [f"quiet: ≤ {pp['quiet']:.1f} calls/hour",
                                    f"busy: ≤ {pp['busy']:.1f} calls/hour"], fill="var(--ceiling)")
    box(svg, 820, y + 50, 150, 56, [f"≤ {qq:.2f} calls/hour"], fill="var(--ceiling)")
    svg.arrow(772, y, 818, y)
    svg.arrow(772, y + 76, 818, y + 76)
    svg.text(795, y - 6, f"× {margin:g}", size=12, anchor="middle", weight="bold")
    svg.text(795, y + 70, f"× {margin:g}", size=12, anchor="middle", weight="bold")
    svg.text(685, y - 42, "the reference's calls", size=12, anchor="middle", fill="var(--ink-2)")
    svg.text(895, y - 42, "the three ceilings", size=12, anchor="middle", fill="var(--ink-2)")
    svg.text(20, 222, "Measured on the fold's training recordings only. A candidate is admissible "
                      "only if it stays under all three ceilings on those recordings.", size=12)
    return svg.render()


def fig_two_draws(label: str, runs: dict) -> str:
    """The two draws' recording seeds, as separated fold blocks: nothing varies within a block."""
    w, h = 980, 200
    svg = Svg(w, h, label)
    x0, x1, gap = 190, 960, 14
    for k, dr in enumerate(DRAWS):
        run = runs[dr["key"]]
        y = 30 + k * 80
        svg.text(x0 - 14, y + 18, dr["name"], anchor="end", size=13, weight="bold")
        svg.text(x0 - 14, y + 34, dr["machine"], anchor="end", size=12, fill="var(--ink-2)")
        nf = run["decl"]["folds"]
        bw = (x1 - x0 - gap * (nf - 1)) / nf
        for f in range(nf):
            held = sorted(set(run["decl"]["recording_seeds"])
                          - set(run["meta"]["budgets"][str(f)]["recording_seeds"]))
            xx = x0 + f * (bw + gap)
            svg.rect(xx, y, bw, 40, fill=f"var(--draw-{dr['key']})", rx=4,
                     title=f"{dr['name']}: outer fold {f}, recording seeds {held[0]}–{held[-1]}")
            svg.text(xx + bw / 2, y + 25, f"fold {f}: seeds {held[0]}–{held[-1]}", size=12,
                     anchor="middle", fill="#ffffff", weight="bold")
    svg.text(x0, 190, "Each seed is simulated at both backgrounds, and its empty twin at seed + "
                      "100,000, so the two draws share no recording.", size=12, fill="var(--ink-2)")
    return svg.render()


FOLD_LO, FOLD_HI = 0.55, 0.85


def fig_per_fold(tabs: dict, runs: dict, label: str, ceiling: float) -> str:
    """Every entry's held-out F1 in every outer fold, both draws; panels A–C by selection.

    The axis spans FOLD_LO–FOLD_HI, where the entries that matter differ; a fold below it is drawn
    as a triangle at the edge pointing off the axis. The dotted line is the practical ceiling of
    section 2."""
    rows = list(NETS) + list(CODED)
    sels = (("untuned", "A · untuned (nets only)"), ("ungated", "B · chosen on F1 alone"),
            ("gated", "C · chosen under the budget"))
    left, pw, gap, top, rh = 150, 244, 44, 34, 34
    w = left + 3 * pw + 2 * gap + 16
    h = top + rh * len(rows) + 58
    svg = Svg(w, h, label)
    lo, hi = FOLD_LO, FOLD_HI
    for i, name in enumerate(rows):
        y = top + i * rh + rh / 2
        svg.text(left - 10, y + 4, NAMES[name], anchor="end", size=13,
                 weight="bold" if name in NETS else "normal")
        if i == len(NETS):
            svg.line(8, top + i * rh, w - 8, top + i * rh, stroke="var(--ink-3)", dash="4 3")
    svg.text(8, top - 14, "nets (bold), then coded detectors", size=12, fill="var(--ink-2)")
    for j, (sel, title) in enumerate(sels):
        x0 = left + j * (pw + gap)
        x1 = x0 + pw
        svg.text((x0 + x1) / 2, h - 6, title, anchor="middle", size=12, weight="bold")
        for i in range(len(rows)):
            svg.rect(x0, top + i * rh + 3, pw, rh - 6, fill="var(--band)" if i % 2 else "none")
        sx = x_axis(svg, x0, x1, top + rh * len(rows) + 4, lo, hi, (0.6, 0.7, 0.8),
                    "held-out F1")
        svg.line(sx(ceiling), top, sx(ceiling), top + rh * len(rows), stroke="var(--ink-3)",
                 dash="2 3")
        for i, name in enumerate(rows):
            for k, dr in enumerate(DRAWS):
                vals = tabs[dr["key"]].get((name, sel))
                if vals is None:
                    continue
                y = top + i * rh + rh / 2 + (-6 if k == 0 else 6)
                colour = f"var(--draw-{dr['key']})"
                off = [(fi, v) for fi, v in enumerate(vals) if v < lo]
                for fi, v in enumerate(vals):
                    if v >= lo:
                        svg.dot(sx(v), y, x0, x1, 4, fill=colour,
                                title=f"{NAMES[name]}, {SEL_WORDS[sel]}, {dr['name']}, outer fold "
                                      f"{fi}: held-out F1 {v:.3f}")
                if off:
                    # every fold off the axis shares ONE triangle, drawn clear of the edge so it
                    # cannot hide a dot sitting there, with the count beside it
                    tip = "; ".join(f"fold {fi}: {v:.3f}" for fi, v in off)
                    svg.edge(x0 - 8, y, "left", fill=colour,
                             title=f"{NAMES[name]}, {SEL_WORDS[sel]}, {dr['name']}: {tip}")
                    if len(off) > 1:
                        svg.text(x0 - 16, y + 4, f"×{len(off)}", size=11, anchor="end",
                                 fill="var(--ink-2)")
                m = st.mean(vals)
                if lo <= m <= hi:
                    svg.line(sx(m), y - 6, sx(m), y + 6, stroke=colour, width=2.5)
    return svg.render()


def fig_collapse(run: dict, model: str, fold: int, label: str) -> str:
    """One outer fold's refit seeds, untuned against the configurations tuning chose."""
    f = run["results"]["learned"][model][fold]
    sels = (("untuned", "A · untuned"), ("ungated", "B · chosen on F1 alone"),
            ("gated", "C · chosen under the budget"))
    left, top, bw, gap, ph = 70, 22, 34, 10, 180
    gw = 5 * (bw + gap)
    w = left + len(sels) * (gw + 60) + 20
    h = top + ph + 70
    svg = Svg(w, h, label)
    sy = lambda v: top + ph - v / 0.8 * ph
    for t in (0.0, 0.2, 0.4, 0.6, 0.8):
        svg.line(left - 4, sy(t), w - 10, sy(t), stroke="var(--rule)")
        svg.text(left - 8, sy(t) + 4, f"{t:.1f}", anchor="end", size=12, fill="var(--ink-2)")
    svg.add(f'<text x="0" y="0" font-size="12" text-anchor="middle" fill="var(--ink-2)" '
            f'transform="translate(18,{top + ph / 2:.1f}) rotate(-90)">held-out F1</text>')
    for gi, (k, title) in enumerate(sels):
        gx = left + 14 + gi * (gw + 60)
        for si, s in enumerate(f[k]["per_seed"]):
            x = gx + si * (bw + gap)
            v = max(0.0, s["f1"])
            bad = bool(s.get("failed_training_signature")) or s["f1_was_nan"]
            tip = (f"{title}, training repeat {s['seed']}: F1 {s['f1']:.3f}"
                   + (" — one call per recording" if s.get("failed_training_signature") else "")
                   + (" — called nothing" if s["f1_was_nan"] else ""))
            if v < 0.005:
                # zero has no height: a ring on the baseline, not a stub that reads as a value (and
                # not a ×, which Figure 1 spends on "false alarm")
                svg.circle(x + bw / 2, sy(0) - 7, 6, fill="var(--draw-b)", hollow=True, title=tip)
                svg.text(x + bw / 2, sy(0) - 18, "0", size=12, anchor="middle")
            else:
                hgt = max(sy(0) - sy(v), 1.5)
                svg.rect(x, sy(0) - hgt, bw, hgt, rx=2,
                         fill="url(#hatch)" if bad else "var(--draw-b)", stroke="var(--draw-b)",
                         width=1.5, title=tip)
            svg.text(x + bw / 2, sy(0) + 15, str(s["seed"]), size=12, anchor="middle",
                     fill="var(--ink-2)")
        svg.text(gx + gw / 2 - gap / 2, sy(0) + 34, title, size=12, anchor="middle", weight="bold")
    svg.text(left + 14 + (len(sels) * (gw + 60) - 60) / 2, sy(0) + 56,
             "training repeat (one bar each)", size=12, anchor="middle", fill="var(--ink-2)")
    return svg.render()


def fig_gaps(runs: dict, label: str) -> str:
    """Every net minus CoactDetect, in every outer fold of both draws: panel A chosen on F1 alone,
    panel B under the budget. Each row reads the run's own paired per-fold differences
    (`comparisons`). Same axis as `fig_matched`, which plots the same quantity."""
    rows = [(n, s) for s in ("ungated", "gated") for n in NETS]
    left, top, rh, pw = 250, 26, 26, 560
    w, h = left + pw + 30, top + rh * (len(rows) + 1) + 60
    svg = Svg(w, h, label)
    lo, hi = GAP_LO, GAP_HI
    sx = x_axis(svg, left, left + pw, top + rh * (len(rows) + 1) + 4, lo, hi, GAP_TICKS,
                "net minus CoactDetect, held-out F1", fmt="{:+.2f}")
    svg.line(sx(0), top - 6, sx(0), top + rh * (len(rows) + 1), stroke="var(--ink-3)", width=1.2)
    for i, (n, s) in enumerate(rows):
        y = top + i * rh + rh / 2 + (rh if s == "gated" else 0)
        if i in (0, 4):
            svg.text(8, y - rh / 2 + 2 - 4, "A · chosen on F1 alone" if s == "ungated"
                     else "B · chosen under the budget", size=12, weight="bold")
        svg.text(left - 10, y + 8, NAMES[n], anchor="end", size=12)
        for k, dr in enumerate(DRAWS):
            comp = runs[dr["key"]]["results"]["comparisons"][s][f"{n} - coact"]
            yy = y + 4 + (-4 if k == 0 else 4)
            for fi, v in enumerate(comp["per_fold"]):
                svg.dot(sx(v), yy, left, left + pw, 3.6, fill=f"var(--draw-{dr['key']})",
                        title=f"{NAMES[n]} {SEL_WORDS[s]}, {dr['name']}, fold {fi}: {sgn(v)}")
    return svg.render()


GAP_LO, GAP_HI, GAP_TICKS = -0.15, 0.05, (-0.15, -0.10, -0.05, 0.0, 0.05)


def fig_split(facts: dict, label: str, entries) -> str:
    """Held-out false alarms per recording under the budget, split into those in the dense stretch
    and those outside it. Both parts are counts of false-alarm CALLS from the score rows (`n_fa`
    and `hot_fa`), so they partition.

    The first two drafts split "outside" further into "on a distractor" and "anywhere else" using
    `Score.distractor_hits`. That field counts distractors touched by ANY call, matched calls
    included, so it is not a count of false-alarm calls; the subtraction went negative for LoCo and
    understated every "anywhere else" bar. The score rows carry nothing that separates the two."""
    left, top, rh, pw = 190, 30, 22, 520
    rows = [(e, dr) for e in entries for dr in DRAWS]
    vmax = max(facts[dr["key"]]["split"][e]["fa"] / facts[dr["key"]]["split"][e]["n"]
               for e, dr in rows)
    hi = int(math.ceil(vmax))
    w, h = left + pw + 30, top + rh * len(rows) + 84
    svg = Svg(w, h, label)
    sx = x_axis(svg, left, left + pw, top + rh * len(rows) + 4, 0, hi, list(range(0, hi + 1)),
                "false alarms per held-out recording", fmt="{:.0f}")
    for i, ((name, sel), dr) in enumerate(rows):
        y = top + i * rh
        t = facts[dr["key"]]["split"][(name, sel)]
        dense, outside = t["dense"] / t["n"], outside_fa(t)
        if dr["key"] == "a":
            svg.text(left - 16, y + rh - 4, NAMES[name], anchor="end", size=12,
                     weight="bold" if name in NETS else "normal")
        svg.rect(left, y + 3, sx(dense) - left, rh - 8, fill="var(--c-dense)",
                 title=f"{NAMES[name]} {SEL_WORDS[sel]}, {dr['name']}: {dense:.2f} per recording "
                       f"in the dense stretch")
        svg.rect(sx(dense) + 2, y + 3, sx(dense + outside) - sx(dense) - 2, rh - 8,
                 fill="var(--c-other)",
                 title=f"{NAMES[name]} {SEL_WORDS[sel]}, {dr['name']}: {outside:.2f} per recording "
                       f"outside the dense stretch")
        svg.circle(left - 7, y + rh / 2 - 1, 3.5, fill=f"var(--draw-{dr['key']})", stroke="none")
    ly = top + rh * len(rows) + 66
    for x, colour, words in ((left, "var(--c-dense)", "in the dense stretch"),
                             (left + 200, "var(--c-other)", "outside the dense stretch")):
        svg.rect(x, ly - 9, 12, 12, fill=colour)
        svg.text(x + 18, ly + 1, words, size=12)
    return svg.render()


def outside_fa(t: dict) -> float:
    """False alarms per recording outside the dense stretch."""
    return (t["fa"] - t["dense"]) / t["n"]


MATCHED = (2, 4, 8, 16)


def matched_gaps(mg: dict, run: dict) -> dict:
    """Net minus CoactDetect per outer fold with ONLY the merge gap changed, both sides set to the
    same gap, from `tools/fair_comparison_evidence.py merge-gap` (WSMIP064's tool, run on each
    draw). Nothing is re-chosen: every threshold and setting is the one the run chose.

    {(net, sel): {"run": [...], 2: [...], 4: [...], 8: [...], 16: [...]}, "worst": ...}. Each
    re-decode at the run's own gap must reproduce the run's F1 (the file's `reproduces_run`, the
    absolute difference) to within 0.002 (re-running a model is not bit-exact at thresholds near the
    top of the grid; the page reports the worst case), and the as-run gap must equal the run's own paired
    comparison, or this is not the same comparison. CoactDetect must sit at 8 s in every fold,
    which the page states."""
    assert mg["net_gap_as_run_sec"] == 2.0
    coact = {(e["outer_fold"], e["selection"]): e for e in mg["coded"]["coact"]}
    assert all(e["reproduces_run"] == 0 for e in coact.values())
    assert all(e["chosen_gap"] == 8.0 for e in coact.values())
    out = {"worst": 0.0, "inexact": set()}
    for net in NETS:
        for e in mg["nets"][net]:
            h, sel = e["outer_fold"], e["selection"]
            worst = max(s["reproduces_run"] for s in e["per_seed"])
            assert worst < 2e-3, (net, h, sel, worst)
            out["worst"] = max(out["worst"], worst)
            out["inexact"] |= {(net, h, sel, s["seed"]) for s in e["per_seed"]
                               if s["reproduces_run"] > 0}
            c = coact[(h, sel)]
            row = out.setdefault((net, sel), {"run": [None] * 4, **{g: [None] * 4 for g in MATCHED}})
            row["run"][h] = e["run_f1_mean"] - c["run_f1"]
            for g in MATCHED:
                row[g][h] = e["f1_mean_by_gap"][f"{g}"] - c["f1_by_gap"][f"{g}"]
    for key, row in out.items():
        if key in ("worst", "inexact"):
            continue
        net, sel = key
        per_fold = run["results"]["comparisons"][sel][f"{net} - coact"]["per_fold"]
        assert all(abs(a - b) < 1e-9 for a, b in zip(row["run"], per_fold)), (net, sel)
    return out


def flagged_folds(run: dict, net: str, sel: str) -> set:
    return {s["fold"] for s in seed_flags(run, net, sel)}


def fig_matched(mgap: dict, runs: dict, label: str) -> str:
    """Per outer fold, the net-minus-CoactDetect gap as run (hollow: the nets at 2 s, CoactDetect
    at its chosen 8 s) and with both sides at 8 s (filled), joined by a line. A fold whose refits
    failed or called nothing is left out and counted in the row label."""
    rows = [(n, s) for s in ("ungated", "gated") for n in NETS]
    left, top, sub, pw = 250, 30, 5, 560
    rh = sub * 8 + 12
    w, h = left + pw + 30, top + rh * len(rows) + 30 + 70
    svg = Svg(w, h, label)
    lo, hi = GAP_LO, GAP_HI
    base = top + rh * len(rows) + 30
    sx = x_axis(svg, left, left + pw, base, lo, hi, GAP_TICKS,
                "net minus CoactDetect, held-out F1", fmt="{:+.2f}")
    svg.line(sx(0), top - 6, sx(0), base, stroke="var(--ink-3)", width=1.2)
    for i, (n, s) in enumerate(rows):
        y0 = top + i * rh + (30 if s == "gated" else 0)
        if i in (0, len(NETS)):
            svg.text(8, y0 - 8, "A · chosen on F1 alone" if s == "ungated"
                     else "B · chosen under the budget", size=12, weight="bold")
        left_out = sum(len(flagged_folds(runs[dr["key"]], n, s)) for dr in DRAWS)
        svg.text(left - 10, y0 + rh / 2 + 2, NAMES[n] + (f" ({left_out} left out)" if left_out
                                                          else ""), anchor="end", size=12)
        if i % 2:
            svg.rect(left, y0 + 2, pw, rh - 4, fill="var(--band)")
        for k, dr in enumerate(DRAWS):
            skip = flagged_folds(runs[dr["key"]], n, s)
            g = mgap[dr["key"]][(n, s)]
            for f in range(4):
                if f in skip:
                    continue
                y = y0 + 8 + (k * 4 + f) * sub
                a, b = g["run"][f], g[8][f]
                colour = f"var(--draw-{dr['key']})"
                xa, xb = min(max(sx(a), left), left + pw), min(max(sx(b), left), left + pw)
                svg.line(xa, y, xb, y, stroke=colour, width=1.6)
                svg.dot(sx(a), y, left, left + pw, 3, fill=colour, hollow=True,
                        title=f"{NAMES[n]} {SEL_WORDS[s]}, {dr['name']}, fold {f}, as run: {sgn(a)}")
                svg.dot(sx(b), y, left, left + pw, 3.2, fill=colour, opacity=1,
                        title=f"{NAMES[n]} {SEL_WORDS[s]}, {dr['name']}, fold {f}, both at 8 s: "
                              f"{sgn(b)}")
    ly = h - 16
    svg.circle(left + 6, ly - 4, 4, fill="var(--ink-2)", hollow=True)
    svg.text(left + 16, ly, "as run: nets at 2 s, CoactDetect at 8 s", size=12)
    svg.circle(left + 316, ly - 4, 4, fill="var(--ink-2)", stroke="none")
    svg.text(left + 326, ly, "both at 8 s", size=12)
    return svg.render()


def fig_moves(tabs: dict, runs: dict, label: str) -> str:
    """How far each entry's mean held-out F1 moved between the draws, second minus first. Hollow
    marks are entries flagged in either draw (the same † and ‡ rule as Table 1)."""
    entries = [(n, s) for n in NETS for s in ("untuned", "ungated", "gated")] + \
              [(d, s) for d in CODED for s in ("ungated", "gated")]
    left, top, rh, pw = 250, 20, 20, 520
    w, h = left + pw + 30, top + rh * len(entries) + 56
    svg = Svg(w, h, label)
    lo, hi = -0.07, 0.04
    sx = x_axis(svg, left, left + pw, top + rh * len(entries) + 4, lo, hi,
                (-0.06, -0.04, -0.02, 0.0, 0.02, 0.04), "second draw minus first, mean held-out F1",
                fmt="{:+.2f}")
    svg.line(sx(0), top - 4, sx(0), top + rh * len(entries), stroke="var(--ink-3)", width=1.2)
    for i, (n, s) in enumerate(entries):
        y = top + i * rh + rh / 2
        if i and entries[i - 1][0] != n:
            svg.line(8, y - rh / 2, w - 8, y - rh / 2, stroke="var(--rule)")
        svg.text(left - 10, y + 4, f"{NAMES[n]} · {SEL_WORDS[s]}", anchor="end", size=12,
                 weight="bold" if n in NETS else "normal")
        d = st.mean(tabs["b"][(n, s)]) - st.mean(tabs["a"][(n, s)])
        bad = flagged(runs["a"], (n, s)) or flagged(runs["b"], (n, s))
        svg.circle(sx(max(lo, min(hi, d))), y, 4.5, fill="var(--ink)", hollow=bad,
                   title=f"{NAMES[n]} {SEL_WORDS[s]}: {sgn(d)}" + (" (flagged)" if bad else ""))
    return svg.render()


ARCH_SLOT = ('<div style="border:2px dashed var(--ink-3);border-radius:8px;padding:16px 20px;'
             'text-align:center;color:var(--ink-2)">Architecture drawings: to come.</div>')


# ---- the page ----------------------------------------------------------------------------------

CSS = """
:root{--surface:#fcfcfb;--ink:#0b0b0b;--ink-2:#52514e;--ink-3:#8a8984;--rule:#e4e3df;--band:#f4f3f0;
--box:#eef3fb;--score:#fdf1e8;--held:#dff2e8;--ref:#f3e9fb;--ceiling:#fbf0c4;--draw-a:#2a78d6;
--draw-b:#eb6834;--c-dense:#d9a441;--c-other:#4a3aa7;--link:#1c5cab}
@media (prefers-color-scheme: dark){:root:not([data-theme="light"]){--surface:#1a1a19;--ink:#fff;
--ink-2:#c3c2b7;--ink-3:#8f8e87;--rule:#34342f;--band:#232321;--box:#20314a;--score:#4a2f1c;
--held:#1c4a33;--ref:#3b2a4a;--ceiling:#4d4520;--draw-a:#3987e5;--draw-b:#d95926;--c-dense:#b98a2e;
--c-other:#9085e9;--link:#86b6ef}}
:root[data-theme="dark"]{--surface:#1a1a19;--ink:#fff;--ink-2:#c3c2b7;--ink-3:#8f8e87;--rule:#34342f;
--band:#232321;--box:#20314a;--score:#4a2f1c;--held:#1c4a33;--ref:#3b2a4a;--ceiling:#4d4520;
--draw-a:#3987e5;--draw-b:#d95926;--c-dense:#b98a2e;--c-other:#9085e9;--link:#86b6ef}
html{background:var(--surface)}
body{background:var(--surface);color:var(--ink);font:16px/1.6 system-ui,-apple-system,"Segoe UI",sans-serif;
max-width:1000px;margin:0 auto;padding:24px 16px 80px}
h1{font-size:28px;line-height:1.25;margin:8px 0 4px}h2{font-size:21px;margin:40px 0 8px;
border-top:1px solid var(--rule);padding-top:20px}h3{font-size:17px;margin:24px 0 6px}
p,li{max-width:74ch}.sub{color:var(--ink-2);margin:0 0 18px}a{color:var(--link)}
figure{margin:22px 0 28px}figcaption{color:var(--ink-2);font-size:14px;max-width:86ch;margin-top:8px}
figcaption b{color:var(--ink)}img.raster{width:100%;max-width:100%;box-sizing:border-box;
border:1px solid var(--rule);background:#fff;display:block}
.key1{display:grid;grid-template-columns:repeat(auto-fill,minmax(290px,1fr));gap:4px 18px;
margin:10px 0 0;font-size:14px;color:var(--ink-2)}.k1{display:flex;gap:8px;align-items:flex-start}
.k1 span:first-child{flex:0 0 18px;padding-top:2px;background:#fff;border-radius:3px}
.sw{display:inline-block;width:11px;height:11px;border:1px solid var(--ink-3);vertical-align:-1px;
margin:0 4px 0 2px}.tnote{font-size:14px;color:var(--ink-2);max-width:86ch}
tr.tsep td{text-align:left;font-weight:600;color:var(--ink-2);padding-top:10px}
thead th[colspan]{text-align:center}
ul.refs li{font-size:14px;margin:4px 0}
.archbox{max-height:880px;overflow:auto;border:1px solid var(--rule);background:#fff}
img.arch{display:block;width:100%;max-width:893px;margin:0 auto}
.figscroll{overflow-x:auto}.scrollhint{display:none;font-size:13px;color:var(--ink-2)}
@media (max-width:700px){.scrollhint{display:block}img.raster{min-width:680px;max-width:none}}
table{border-collapse:collapse;font-size:14px;margin:12px 0 6px;font-variant-numeric:tabular-nums}
th,td{padding:4px 10px;border-bottom:1px solid var(--rule);text-align:right}
th:first-child,td:first-child{text-align:left}thead th{color:var(--ink-2);font-weight:600;white-space:nowrap}
.key{display:inline-block;width:11px;height:11px;border-radius:6px;vertical-align:-1px;margin:0 4px 0 2px}
.box{background:var(--band);border-radius:8px;padding:12px 16px;margin:16px 0}
.note{border-left:3px solid var(--ink-3);padding-left:12px}code{font-size:14px;overflow-wrap:anywhere}
.tablewrap{overflow-x:auto}
"""


def build(mine: Path, theirs: Path, rehearsal: Path | None, raster_seed: int, raster_regime: str,
          mg_mine: Path, mg_theirs: Path, cr_mine: Path, cr_theirs: Path,
          arch_svg: Path | None = None) -> str:
    from scipy import stats

    from bugarach.score import TOL_SEC

    a, b = load_run(theirs), load_run(mine)
    runs = {"a": a, "b": b}
    cr_raw = {"a": json.loads(Path(cr_theirs).read_text(encoding="utf-8")),
              "b": json.loads(Path(cr_mine).read_text(encoding="utf-8"))}
    for k, r in runs.items():
        r["crowded"] = crowded_refused(cr_raw[k])
        # the check must be of THIS run's choices: every (detector, selection, fold) it scored
        assert {(c["detector"], c["selection"], c["outer_fold"]) for c in cr_raw[k]["choices"]} \
            == {(d, s, f["outer_fold"]) for d, fs in r["results"]["hand"].items()
                for f in fs for s in ("ungated", "gated")}
    differ = declaration_difference(a, b)
    assert differ == ["recording_seeds", "replicate"], (
        f"the two declarations differ in {differ}, not only in their recordings; this page compares "
        "draws of data and would be comparing something else")
    da, db = a["decl"], b["decl"]
    seeds = {k: r["decl"]["recording_seeds"] for k, r in runs.items()}
    assert not set(seeds["a"]) & set(seeds["b"])
    tabs = {k: table(r) for k, r in runs.items()}
    mean = {k: {e: st.mean(v) for e, v in t.items()} for k, t in tabs.items()}
    facts = {k: archive_facts(r) for k, r in runs.items()}
    refused = {k: refused_everything(r) for k, r in runs.items()}
    comp = {k: r["results"]["comparisons"] for k, r in runs.items()}
    compliance = {k: held_out_compliance(r) for k, r in runs.items()}
    mg_raw = {"a": json.loads(Path(mg_theirs).read_text(encoding="utf-8")),
              "b": json.loads(Path(mg_mine).read_text(encoding="utf-8"))}
    mgap = {k: matched_gaps(mg_raw[k], runs[k]) for k in runs}

    n_folds, per_fold = db["folds"], db["seeds_per_fold"]
    n_configs = len(next(iter(db["configurations"].values())))
    n_tune, n_refit = len(db["tune_seeds"]), len(db["refit_seeds"])
    margin = db["budget_margin"]
    budget0 = b["meta"]["budgets"]["0"]
    n_coded_train = len(budget0["recordings"])
    min_gain = db["hand_search"]["min_gain"]
    ref = da["reference"]["params"]
    assert ref == db["reference"]["params"]
    busy_sec = float(db["busy_window_sec"])
    bg = {k: db["backgrounds"][k]["bg_rate_hz"] for k in ("quiet", "busy")}
    n_train = facts["b"]["n_train"]
    n_thresh = facts["b"]["n_thresh"]
    assert len(n_train) == 1 and len(n_thresh) == 1 and facts["a"]["n_train"] == n_train
    n_train, n_thresh = n_train[0], n_thresh[0]
    inner_fits = n_configs * n_tune * math.comb(n_folds, 2)
    refit_counts = [v for k in runs for v in facts[k]["refits"].values()]
    net_merge = mg_raw["b"]["net_gap_as_run_sec"]
    assert net_merge == mg_raw["a"]["net_gap_as_run_sec"]

    # --- the between-draw spread, on one rule (the Table 1 flags), nets and coded kept apart -----
    entries = [e for e in mean["a"]]
    moves = {e: mean["b"][e] - mean["a"][e] for e in entries}
    clean = [e for e in entries if not (flagged(a, e) or flagged(b, e))]
    # CoactDetect's two selections are one fact when they chose the same configuration everywhere
    same_coact = all(f["gated"]["config_key"] == f["ungated"]["config_key"]
                     for r in runs.values() for f in r["results"]["hand"]["coact"])
    if same_coact and ("coact", "gated") in clean:
        clean.remove(("coact", "gated"))
    net_clean = [e for e in clean if e[0] in NETS]
    coded_clean = [e for e in clean if e[0] in CODED]
    net_moves = [abs(moves[e]) for e in net_clean]
    coded_moves = [abs(moves[e]) for e in coded_clean]
    med_net, med_coded = st.median(net_moves), st.median(coded_moves)
    net_up = sum(moves[e] > 0 for e in net_clean)
    coded_not_up = sum(moves[e] <= 0 for e in coded_clean)
    assert net_up >= 0.75 * len(net_clean) and coded_not_up >= 0.6 * len(coded_clean), \
        "section 9: the nets rose between the draws and the coded detectors did not"
    drift = st.mean(moves[e] for e in net_clean) - st.mean(moves[e] for e in coded_clean)

    # --- the headline gap as run ---------------------------------------------------------------
    def best(k, sel, pool):
        vals = {n: mean[k][(n, sel)] for n in pool}
        return max(vals, key=vals.get)
    bg_net = {k: best(k, "gated", NETS) for k in runs}
    assert bg_net["a"] == bg_net["b"], f"best budgeted net differs between draws: {bg_net}"
    gnet = bg_net["a"]
    assert not any(flagged(runs[k], (gnet, "gated")) for k in runs)
    gap_g = {k: comp[k]["gated"][f"{gnet} - coact"] for k in runs}

    def paired_t(v):
        """A paired t over folds, computed here only where the run wrote none (matched merges)."""
        t = st.mean(v) / (st.stdev(v) / math.sqrt(len(v)))
        return t, 2 * stats.t.sf(abs(t), len(v) - 1)
    # the as-run test is the run's own (`_paired` in the tuner); only p is computed here
    tt = {k: (gap_g[k]["t"], 2 * stats.t.sf(abs(gap_g[k]["t"]), gap_g[k]["df"])) for k in runs}
    tdf = {gap_g[k]["df"] for k in runs}
    assert len(tdf) == 1
    tdf = tdf.pop()
    tfmt = {k: f"{tt[k][0]:.1f}".replace("-", "−") for k in runs}
    folds_neg = sum(v < 0 for k in runs for v in gap_g[k]["per_fold"])
    gap_move = gap_g["b"]["mean"] - gap_g["a"]["mean"]
    all_nets_trail = all(mean[k][(n, "gated")] < mean[k][("coact", "gated")] for k in runs
                         for n in NETS)
    assert all_nets_trail, "every net trails CoactDetect under the budget, as run"
    assert all(v < 0 for k in runs for n in NETS
               for v in comp[k]["gated"][f"{n} - coact"]["per_fold"]), \
        "under the budget every net sits below zero in every fold of both draws"
    assert folds_neg == 2 * n_folds, "the budgeted gap is negative in every fold of both draws"
    assert abs(gap_move) < med_net, "the gap moved less than the typical between-draw move"

    # --- on F1 alone: the chorus models, where training did not fail -----------------------------
    chorus = ("chorus_norm", "chorus_gain_norm")
    bu_net = {k: best(k, "ungated", NETS) for k in runs}
    gap_u = {k: comp[k]["ungated"][f"{bu_net[k]} - coact"]["mean"] for k in runs}
    unflag_u = [v for k in runs for n in chorus
                for f, v in enumerate(comp[k]["ungated"][f"{n} - coact"]["per_fold"])
                if f not in flagged_folds(runs[k], n, "ungated")]
    near_u = max(abs(v) for v in unflag_u)
    assert near_u < 0.03, "on F1 alone the chorus models are within 0.03 of CoactDetect as run"
    n_flag_u = sum(len(flagged_folds(runs[k], n, "ungated")) for k in runs for n in chorus)
    unt = {k: mean[k][("chorus_norm", "untuned")] - mean[k][("coact", "ungated")] for k in runs}
    assert (unt["a"] > 0) != (unt["b"] > 0), "the untuned margin changes sign"

    # --- at a matched merge -----------------------------------------------------------------------
    def mmean(k, n, s, g):
        fl = flagged_folds(runs[k], n, s)
        return st.mean(v for f, v in enumerate(mgap[k][(n, s)][g]) if f not in fl)
    g_asrun = {k: mmean(k, gnet, "gated", "run") for k in runs}
    g_matched = {k: [mmean(k, gnet, "gated", g) for g in MATCHED] for k in runs}
    assert all(g_asrun[k] < v < 0 for k in runs for v in g_matched[k]), \
        "at every matched merge the budgeted gap is smaller than as run and still negative"
    closed = [1 - v / g_asrun[k] for k in runs for v in g_matched[k]]
    assert 0.25 <= min(closed) and max(closed) <= 0.6, \
        "a matched merge closes a quarter to a half of the budgeted gap"
    assert all(2 <= abs(gap_g[k]["mean"]) / med_net <= 3.2 for k in runs), \
        "the as-run gap is two to three times the typical between-draw move"
    g8_neg = sum(v < 0 for k in runs for v in mgap[k][(gnet, "gated")][8])
    assert g8_neg == 2 * n_folds
    ch_m = [mmean(k, n, "ungated", g) for k in runs for n in chorus for g in MATCHED]
    assert min(ch_m) > 0, "on F1 alone both chorus models lead at every matched merge"
    ch8 = [(v > 0) for k in runs for n in chorus
           for f, v in enumerate(mgap[k][(n, "ungated")][8])
           if f not in flagged_folds(runs[k], n, "ungated")]
    assert sum(ch8) >= 0.75 * len(ch8), "the chorus models lead in most folds where they trained"
    # ...but is that lead more than the luck of the recordings? The same paired test the as-run
    # gap gets, per net and draw at 8 s over the folds where the net trained, and the mean at 8 s
    # with the failed folds counted, since a user of the model gets those too.
    ch_t = {(k, n): paired_t([v for f, v in enumerate(mgap[k][(n, "ungated")][8])
                              if f not in flagged_folds(runs[k], n, "ungated")])
            for k in runs for n in chorus}
    ch_sig = sum(p < 0.05 for _, p in ch_t.values())
    ch_all8 = {(k, n): st.mean(mgap[k][(n, "ungated")][8]) for k in runs for n in chorus}
    ch_all_neg = sum(v < 0 for v in ch_all8.values())
    assert ch_sig < len(ch_t), "the page says the F1-alone lead is not established"
    remain = [1 - c for c in closed]
    # re-decoding at a longer merge with a threshold chosen for 2 s can hurt a net
    ll_hurt = min(v8 - vr for k in runs
                  for vr, v8 in zip(mgap[k][("line_length", "ungated")]["run"],
                                    mgap[k][("line_length", "ungated")][8]))
    assert ll_hurt < -0.05
    coll_share = {n: [facts[k]["collapsed"][n][0] / facts[k]["collapsed"][n][2] for k in runs]
                  for n in chorus}
    assert all(0.28 <= v <= 0.38 for v in coll_share["chorus_norm"]), "about a third"
    assert all(0.14 <= v <= 0.2 for v in coll_share["chorus_gain_norm"]), "about a sixth"
    # the draws share their configurations and training seeds, so the same fits can fail in both
    coll_both = {n: sum(1 for key in facts["a"]["collapsed_keys"] & facts["b"]["collapsed_keys"]
                        if key[0] == n) for n in NETS}
    assert coll_both["chorus_norm"] > 0.5 * min(facts[k]["collapsed"]["chorus_norm"][0]
                                                 for k in runs), "most failures recur"
    trail_always = all(v < 0 for k in runs for n in ("line_length", "tube")
                       for s in ("ungated", "gated") for g in MATCHED
                       for f, v in enumerate(mgap[k][(n, s)][g])
                       if f not in flagged_folds(runs[k], n, s))
    assert trail_always, "line_length and tube trail at every matched merge"
    coact_by = {k: {g: st.mean(e["f1_by_gap"][g] for e in mg_raw[k]["coded"]["coact"]
                               if e["selection"] == "ungated") for g in ("2", "8", "30")}
                for k in runs}
    assert all(coact_by[k]["2"] < coact_by[k]["8"] < coact_by[k]["30"] for k in runs)
    inexact = {k: mgap[k]["inexact"] for k in runs}
    worst = max(mgap[k]["worst"] for k in runs)

    # --- where the as-run gap is ------------------------------------------------------------------
    pb = {k: {(e, g): prf(facts[k]["split"][(e, "gated", g)]) for e in (gnet, "coact")
              for g in ("quiet", "busy")} for k in runs}
    assert all(pb[k][(gnet, g)][1] < pb[k][("coact", g)][1] for k in runs
               for g in ("quiet", "busy")), "the best net's precision is lower at both backgrounds"
    assert all(pb[k][(gnet, "quiet")][0] < pb[k][("coact", "quiet")][0]
               and pb[k][(gnet, "busy")][0] > pb[k][("coact", "busy")][0] for k in runs), \
        "the best net finds fewer events at the quiet background and more at the busy one"
    rec = {k: {e: prf(facts[k]["split"][(e, "gated")])[0] for e in (gnet, "coact")} for k in runs}
    assert all(rec[k][gnet] >= rec[k]["coact"] for k in runs), "pooled, recall is not lower"
    per_rec = lambda k, e, part: (facts[k]["split"][(e, "gated")][part]
                                  / facts[k]["split"][(e, "gated")]["n"])
    for k in runs:
        assert per_rec(k, gnet, "dense") < per_rec(k, "coact", "dense")
        assert outside_fa(facts[k]["split"][(gnet, "gated")]) > \
            outside_fa(facts[k]["split"][("coact", "gated")])
    pattern = [n for n in NETS if all(
        per_rec(k, n, "dense") < per_rec(k, "coact", "dense")
        and outside_fa(facts[k]["split"][(n, "gated")])
        > outside_fa(facts[k]["split"][("coact", "gated")]) for k in runs)]
    tube_dense = all(per_rec(k, "tube", "dense") > per_rec(k, "coact", "dense") for k in runs)
    assert "tube" not in pattern and tube_dense
    first_only = [n for n in NETS if n not in pattern and n != "tube" and (
        per_rec("a", n, "dense") < per_rec("a", "coact", "dense")
        and outside_fa(facts["a"]["split"][(n, "gated")])
        > outside_fa(facts["a"]["split"][("coact", "gated")]))]
    # recall by event size: where the difference between the two sides actually lives
    fracs = sorted({f for k in runs for f in facts[k]["split"][(gnet, "gated", "quiet")]["by_frac"]},
                   reverse=True)
    by_size = {k: {(e, g, f): (lambda n, h: h / n)(*facts[k]["split"][(e, "gated", g)]["by_frac"][f])
                   for e in (gnet, "coact") for g in ("quiet", "busy") for f in fracs}
               for k in runs}
    big = [by_size[k][(e, g, f)] for k in runs for e in (gnet, "coact") for g in ("quiet", "busy")
           for f in fracs[:2]]
    assert min(big) >= 0.9, "recall on the two larger event sizes is near its ceiling"
    small = fracs[-1]
    assert all(by_size[k][(gnet, "busy", small)] > by_size[k][("coact", "busy", small)]
               for k in runs), "at the busy background the net finds more of the smallest events"
    # the crowded-recording veto, after the fact, both draws
    cr_refused = {k: {(d, s) for d, s, _ in runs[k]["crowded"]} for k in runs}
    cr_all = {k: {(d, s) for (d, s) in cr_refused[k]
                  if sum(1 for dd, ss, _ in runs[k]["crowded"] if (dd, ss) == (d, s)) == n_folds}
              for k in runs}
    assert not any(d == "coact" for k in runs for d, _ in cr_refused[k]), \
        "CoactDetect passes the crowded veto in every fold of both draws"
    assert ("sce", "ungated") in cr_all["a"] and ("sce", "ungated") in cr_all["b"]

    # --- the rehearsal, read from its own file --------------------------------------------------
    reh = None
    if rehearsal is not None:
        rr = json.loads(Path(rehearsal).read_text(encoding="utf-8"))["comparisons"]["gated"]
        reh = {n: rr[f"{n} - coact"]["mean"] for n in chorus}
        assert max(reh.values()) < 2 * med_net, "the rehearsal's lead is the size of rerun noise"

    png, rf = raster_png(raster_regime, raster_seed, ref)
    raster_uri = "data:image/png;base64," + base64.b64encode(png).decode()
    counts = untuned_param_counts(b)
    hw = rf["hot_window"]
    part = rf["participation"]
    part_rois = sorted(set(rf["n_part"]), reverse=True)
    n_dist_rois = sorted(set(rf["n_dist_part"]))
    assert len(part_rois) == 3 and len(n_dist_rois) == 1
    n_dist_rois = n_dist_rois[0]
    ceil_p = rf["n_planted"] / (rf["n_planted"] + rf["n_distractors"])
    ceil_f1 = 2 * ceil_p / (1 + ceil_p)
    coll = {k: facts[k]["collapsed"] for k in runs}
    cn_flags = seed_flags(b, "chorus_norm", "ungated")
    cn_fold = cn_flags[0]["fold"] if cn_flags else None
    cn_bad = [s for s in cn_flags if s["fold"] == cn_fold]
    nothing = {}
    for k in runs:
        for n in NETS:
            for s in seed_flags(runs[k], n, "gated"):
                if s["nothing"]:
                    nothing[(k, n, s["fold"])] = nothing.get((k, n, s["fold"]), 0) + 1
    cgn_failed = [(k, s) for k in runs for s in seed_flags(runs[k], "chorus_gain_norm", "ungated")]
    cic_probe = [f["gated"]["probe_per_hour"]["quiet"] for k in runs
                 for f in runs[k]["results"]["hand"]["cicada"]]
    ceil_q = [runs[k]["meta"]["budgets"][str(h)]["probe_per_hour"]["quiet"] for k in runs
              for h in range(n_folds)]
    sce_ref = [(k, h, v) for k in runs for (d, h), v in refused[k].items() if d == "sce"]
    sce_busy_null = [f["gated"]["quiet_per_hour"]["null_busy"] for k in runs
                     for f in runs[k]["results"]["hand"]["sce"]
                     if ("sce", f["outer_fold"]) not in refused[k]]
    coact_busy_null = [f["gated"]["quiet_per_hour"]["null_busy"] for k in runs
                       for f in runs[k]["results"]["hand"]["coact"]]
    coact_moves = {k: sum(1 for h in range(n_folds)
                          if selection(runs[k], "ungated", h, "coact")["moves"]) for k in runs}
    coact_over = {k: [f["outer_fold"] for f in runs[k]["results"]["hand"]["coact"]
                      if f["gated"].get("over_budget")] for k in runs}
    tops = {}
    for d in CODED:
        vals = {max(selection(runs[k], "ungated", h, d)["grids"][FUSE[d]])
                for k in runs for h in range(n_folds)}
        assert len(vals) == 1
        tops[d] = vals.pop()
    top_sec = {d: tops[d] * (rf["dt"] if FUSE[d].endswith("frames") else 1.0) for d in CODED}
    long_merge = [d for d in CODED if top_sec[d] > net_merge]
    short_merge = [d for d in CODED if top_sec[d] <= net_merge]
    edge_rows = []
    for d in CODED:
        started = moved = 0
        for k in runs:
            for h in range(n_folds):
                s = selection(runs[k], "ungated", h, d)
                if (s.get("edge_flags") or {}).get(FUSE[d]) == "high":
                    if any(mv["setting"] == FUSE[d] for mv in s["moves"]):
                        moved += 1
                    else:
                        started += 1
        edge_rows.append((d, started, moved))
    sce_lead = {k: mean[k][("sce", "ungated")] - mean[k][("coact", "ungated")] for k in runs}
    ll = {k: comp[k]["ungated"]["line_length tuned - untuned"]["mean"] for k in runs}
    cn_t = {k: comp[k]["ungated"]["chorus_norm tuned - untuned"]["mean"] for k in runs}
    ll_t = {k: paired_t(comp[k]["ungated"]["line_length tuned - untuned"]["per_fold"])
            for k in runs}
    assert all(v > 0 for v in ll.values()), "line_length's tuning gain has one sign in both draws"
    tube_t = {k: mean[k][("tube", "ungated")] - mean[k][("tube", "untuned")] for k in runs}
    assert all(abs(v) < med_net for v in tube_t.values()), "tuning barely moved tube"
    crop = {json.loads((b["folder"] / "configs" / n / f"{key}.json").read_text())["training"]
            ["crop_frames"] for n in chorus for key in db["configurations"][n]}
    assert len(crop) == 1
    crop = crop.pop()
    assert all(r.tol_sec == TOL_SEC for k in runs for r in
               [facts[k]["split"][(gnet, "gated")]["res"]]), "the rows were scored at TOL_SEC"
    same_coact_f1 = f3(mean["a"][("coact", "ungated")]) == f3(mean["b"][("coact", "ungated")])

    F = {}
    for i, n in enumerate(("raster", "arch", "cv", "budget", "draws", "folds", "collapse", "moves",
                           "gaps", "matched", "split"), 1):
        F[n] = i

    def ref_(name, words):
        return f'<a href="#fig-{name}">Figure {F[name]}, {words}</a>'

    hint_html = '<div class="scrollhint">Scroll sideways to see the whole {}.</div>'

    def fig(name, body, caption, hint=True):
        h_ = hint_html.format("figure") if hint else ""
        return (f'<figure id="fig-{name}">{h_}{body}<figcaption><b>Figure {F[name]}.</b> '
                f'{caption}</figcaption></figure>')

    def tab(n, caption, body, note="", wide=True):
        h_ = hint_html.format("table") if wide else ""
        return (f'<p id="tab-{n}"><b>Table {n}.</b> {caption}</p>{h_}'
                f"<div class='tablewrap'><table>{body}</table></div>"
                + (f'<p class="tnote">{note}</p>' if note else ""))

    key = lambda k: f'<span class="key" style="background:var(--draw-{k})"></span>'
    sw = lambda v: f'<span class="sw" style="background:var(--{v})"></span>'
    nm = lambda n: f"<b>{NAMES[n]}</b>" if n in NETS else NAMES[n]
    A, B = DRAWS[0]["name"], DRAWS[1]["name"]
    ra = f"{min(seeds['a'])}–{max(seeds['a'])}"
    rb = f"{min(seeds['b'])}–{max(seeds['b'])}"
    cb = da["coded_base"]["values"]["coact"]
    lo_cl, hi_cl = min(closed), max(closed)

    # ---- Table 1: every entry's mean, both draws ---------------------------------------------
    def mark(k, n, s):
        m_ = "†" if n in NETS and seed_flags(runs[k], n, s) else ""
        if s == "gated" and any((n, h) in refused[k] for h in range(n_folds)):
            m_ += "‡"
        if any((n, s, h) in runs[k]["crowded"] for h in range(n_folds)):
            m_ += "§"
        return m_
    t1_rows = []
    for n in list(NETS) + list(CODED):
        cells = [f"<td>{nm(n)}</td>"]
        for s in ("untuned", "ungated", "gated"):
            for k in ("a", "b"):
                cells.append(f"<td>{f3(mean[k][(n, s)])}{mark(k, n, s)}</td>"
                             if (n, s) in mean[k] else "<td>—</td>")
        t1_rows.append("<tr>" + "".join(cells) + "</tr>")
    sub = "".join(f"<th>{key('a')}first</th><th>{key('b')}second</th>" for _ in range(3))
    table1 = tab(1, "Mean held-out F1 over the 4 outer folds of each draw.",
                 "<thead><tr><th rowspan='2'>entry</th><th colspan='2'>untuned</th>"
                 "<th colspan='2'>on F1 alone</th><th colspan='2'>under the budget</th></tr>"
                 f"<tr>{sub}</tr></thead><tbody>{''.join(t1_rows)}</tbody>",
                 "Nets in bold. † at least one refit in some fold made one call per recording or "
                 "called nothing on the held-out fold (section 8). ‡ in at least one fold the "
                 "budgeted search found no admissible setting and returned its starting point, "
                 "which is over the budget. § in at least one fold the choice fails goal 1's "
                 "crowded-recording check (section 8). Means are over all four folds, flagged ones "
                 "included. A coded detector has no untuned entry: its search starts from fixed "
                 "starting values (goal 1's for CoactDetect and LoCo, the bench's stored operating "
                 "points for the other four). Differences quoted in the text are computed before "
                 "rounding, so they can differ from these rounded values by 0.001.")

    # ---- Table 2: collapsed inner fits ---------------------------------------------------------
    t2 = "".join(f"<tr><td><b>{NAMES[n]}</b></td>"
                 + "".join(f"<td>{coll[k][n][0]} of {coll[k][n][2]} fits</td>" for k in ("a", "b"))
                 + f"<td>{coll_both[n]} fits</td></tr>" for n in NETS)
    one_fold = [(k, n, coll[k][n][1]) for k in runs for n in NETS if coll[k][n][1]]
    table2 = tab(2, "Inner fits that made exactly one call on every recording of both folds they "
                    "were scored on.",
                 f"<thead><tr><th>net</th><th>{key('a')}first draw</th><th>{key('b')}second draw"
                 f"</th><th>the same fit in both</th></tr></thead><tbody>{t2}</tbody>",
                 f"Each net has {inner_fits} inner fits per draw, each scored on the two folds "
                 "outside its training pair. The two draws share their configurations and training "
                 "seeds, so a fit is \"the same\" when its configuration, training seed and pair of "
                 "folds match; only its recordings differ."
                 + "".join(f" One more {NAMES[n]} fit in the {DRAWS[0 if k == 'a' else 1]['name']} "
                           "did so on one of its two folds only." for k, n, c in one_fold
                           if c == 1), wide=False)
    assert all(c == 1 for *_, c in one_fold)

    # ---- Table 3: held-out compliance ----------------------------------------------------------
    t3 = "".join(
        f"<tr><td>{nm(n)}</td>"
        + "".join(f"<td>{compliance[k][n][0]} of {compliance[k][n][1]} "
                  f"{'refits' if n in NETS else 'folds'}</td>" for k in ("a", "b")) + "</tr>"
        for n in list(NETS) + list(CODED))
    table3 = tab(3, "Choices made under the budget that broke their fold's ceilings on the held-out "
                    "recordings.",
                 f"<thead><tr><th>entry</th><th>{key('a')}first draw</th><th>{key('b')}second draw"
                 f"</th></tr></thead><tbody>{t3}</tbody>",
                 f"For a net, refits ({n_folds} folds × {n_refit} refits); for a coded detector, "
                 "folds.", wide=False)

    # ---- Table 4: merge settings at the top of their grid -------------------------------------
    t4 = "".join(f"<tr><td>{NAMES[d]}</td><td style='text-align:left'>{FUSE_WORDS[FUSE[d]]}, top "
                 f"{top_sec[d]:g} s</td><td>{s} of {2 * n_folds} folds</td>"
                 f"<td>{m} of {2 * n_folds} folds</td>"
                 "</tr>" for d, s, m in edge_rows)
    table4 = tab(4, "Outer folds in which a coded detector's merge setting, chosen on F1 alone, sat "
                    "at the top of its grid.",
                 "<thead><tr><th>detector</th><th style='text-align:left'>setting</th>"
                 f"<th>started there</th><th>moved there</th></tr></thead><tbody>{t4}</tbody>",
                 f"Of {2 * n_folds} folds: {n_folds} in each draw, pooled. locust's setting is in "
                 f"frames of {rf['dt']:g} s ({tops['cicada']:g} frames).")

    # ---- Table 5: gaps at a matched merge ------------------------------------------------------
    def t5_rows(s):
        out_ = []
        for n in NETS:
            for k in ("a", "b"):
                fl = flagged_folds(runs[k], n, s)
                out_.append(f"<tr><td>{'<b>' + NAMES[n] + '</b>' if k == 'a' else ''}</td>"
                            f"<td style='text-align:left'>{key(k)}"
                            f"{'first' if k == 'a' else 'second'}"
                            f"{f' ({len(fl)} left out)' if fl else ''}</td>"
                            + "".join(f"<td>{sgn(mmean(k, n, s, g))}</td>"
                                      for g in ("run",) + MATCHED) + "</tr>")
        return "".join(out_)
    t5_body = ("<thead><tr><th>net</th><th style='text-align:left'>draw</th><th>as run</th>"
               + "".join(f"<th>both {g} s</th>" for g in MATCHED) + "</tr></thead><tbody>"
               "<tr class='tsep'><td colspan='7'>chosen on F1 alone</td></tr>" + t5_rows("ungated")
               + "<tr class='tsep'><td colspan='7'>chosen under the budget</td></tr>"
               + t5_rows("gated") + "</tbody>")
    table5 = tab(5, "Net minus CoactDetect, mean held-out F1 over the folds, as run and with both "
                    "sides' merge set to the same gap.", t5_body,
                 "Nothing is re-chosen at the new gap: every threshold and setting is the one the "
                 "run chose. Folds whose refits made one call per recording or called nothing "
                 "are left out.")

    # ---- Table 6: recall and precision by background ------------------------------------------
    n_cells = {f: c for f, c in zip(fracs, part_rois)}
    t6 = "".join(f"<tr><td>{nm(e)}</td><td style='text-align:left'>{g}</td>"
                 + "".join("".join(f"<td>{by_size[k][(e, g, f)]:.2f}</td>" for f in fracs)
                           + f"<td>{pb[k][(e, g)][1]:.2f}</td>" for k in ("a", "b")) + "</tr>"
                 for g in ("quiet", "busy") for e in (gnet, "coact"))
    size_heads = "".join(f"<th>{n_cells[f]} cells</th>" for f in fracs) + "<th>precision</th>"
    table6 = tab(6, f"Recall by event size, and precision, under the budget: {gnet} against "
                    "CoactDetect, by background.",
                 f"<thead><tr><th rowspan='2'>entry</th><th rowspan='2' style='text-align:left'>"
                 f"background</th><th colspan='{len(fracs) + 1}'>{key('a')}first draw</th>"
                 f"<th colspan='{len(fracs) + 1}'>{key('b')}second draw</th></tr>"
                 f"<tr>{size_heads}{size_heads}</tr></thead><tbody>{t6}</tbody>",
                 "Recall is the share of planted events of that size found, pooled over each draw's "
                 "held-out recordings at that background (and, for the net, over its refits); "
                 "precision leaves out calls in the dense stretch.")

    # ---- Table 7: the asymmetries --------------------------------------------------------------
    def and_list(xs):
        xs = list(xs)
        return xs[0] if len(xs) == 1 else ", ".join(xs[:-1]) + " and " + xs[-1]
    merges = "; ".join(
        f"{and_list(NAMES[d] for d in CODED if top_sec[d] == v)} {v:g} s"
        for v in sorted({top_sec[d] for d in CODED}, reverse=True))
    asym = [("merge", f"fixed at {net_merge:g} s by the training code, not tuned",
             f"tuned on a grid; grid tops {merges} (locust drops the lower of two nearby calls "
             "rather than joining them)"),
            ("recordings behind a choice", f"each fit trains on {n_train} and picks its threshold on "
             f"{n_thresh}", f"all {n_coded_train} training recordings"),
            ("across refits", f"under the budget, one threshold chosen on the inner fits, carried "
             f"onto {n_refit} refits trained afresh; untuned and on F1 alone, each refit picks its "
             f"own threshold on its {n_thresh} threshold recordings",
             "one setting; the detector is deterministic"),
            ("tuning before this comparison", f"none beyond the {n_configs} configurations",
             "CoactDetect and LoCo start from goal 1's values, chosen on bench seeds 1–48 and "
             "checked on 49–96; the other four from the bench's stored operating points"),
            ("the budget", "measured against another detector", "anchored to CoactDetect's own "
             "rates, so its reference settings are admissible by construction"),
            ("scaling each cell", "the chorus nets standardize each cell's encoder output over the "
             f"stretch they see: a {crop:,}-frame crop in training, the whole recording (dense "
             "stretch included) when scored", "—")]
    table7 = tab(7, "Where the two sides were not treated alike.",
                 "<thead><tr><th>what</th><th style='text-align:left'>learned models</th>"
                 "<th style='text-align:left'>coded detectors</th></tr></thead><tbody>"
                 + "".join(f"<tr><td>{w_}</td><td style='text-align:left'>{x}</td>"
                           f"<td style='text-align:left'>{y}</td></tr>" for w_, x, y in asym)
                 + "</tbody>")

    split_entries = [(n, "gated") for n in NETS] + [("coact", "gated"), ("loco", "gated")]
    dens = lambda k, e: per_rec(k, e, "dense")
    dname = lambda k: DRAWS[0 if k == "a" else 1]["name"]
    rem_lo, rem_hi = min(remain), max(remain)
    # which folds fall off Figure 9's axis, and whether each is a flagged (failed-training) fold
    off_axis = [(k, n, s, f) for k in runs for s in ("ungated", "gated") for n in NETS
                for f, v in enumerate(comp[k][s][f"{n} - coact"]["per_fold"]) if v < -0.15]
    off_unflagged = [(k, n, s, f) for k, n, s, f in off_axis if f not in flagged_folds(runs[k], n, s)]
    cr_both = sorted(cr_all["a"] & cr_all["b"], key=lambda e: (CODED.index(e[0]), e[1]))
    cr_other = sorted({(d, s, k) for k in runs for d, s in cr_refused[k]
                       if (d, s) not in cr_both}, key=lambda e: (CODED.index(e[0]), e[1], e[2]))
    cr_n = {(d, s, k): sum(1 for dd, ss, _ in runs[k]["crowded"] if (dd, ss) == (d, s))
            for d, s, k in cr_other}
    max_drop = cr_raw["b"]["max_crowded_drop"]
    assert cr_raw["a"]["max_crowded_drop"] == max_drop
    inexact_thr = [s["threshold"] for k in runs for net in NETS for e in mg_raw[k]["nets"][net]
                   for s in e["per_seed"] if s["reproduces_run"] > 0]
    assert min(inexact_thr) >= 0.9, "every inexact re-decode sits near the top of the grid"
    if arch_svg is not None and Path(arch_svg).is_file():
        svg_text = Path(arch_svg).read_text(encoding="utf-8")
        assert "<script" not in svg_text.lower()
        arch_body = ('<div class="archbox"><img class="arch" alt="The four learned architectures, '
                     'each drawn stage by stage at one common scale" src="data:image/svg+xml;base64,'
                     + base64.b64encode(svg_text.encode("utf-8")).decode() + '"></div>')
        arch_caption = ("<b>The four learned architectures, drawn at one scale.</b> Each is traced "
                        "stage by stage from the registered model the runs trained, with every size "
                        "read off the trace (the drawings are the project's, from branch "
                        "<code>draw-the-comparison-four</code>). Scroll inside the frame to see all "
                        "four.")
        arch_ref = ref_("arch", "the four architectures")
    else:
        arch_body = ARCH_SLOT
        arch_caption = ("<b>The four learned architectures.</b> The drawings were not available to "
                        "this build.")
        arch_ref = ref_("arch", "the four architectures")

    body = []
    body.append(f"""
<h1>Two draws of the learned-versus-coded comparison</h1>
<p class="sub">Can a lead of about a hundredth of F1 (a detection score from 0 to 1) between a learned
detector and a hand-written one be told apart from the luck of which simulated recordings were drawn?
This report reruns the project's comparison of four learned detectors with six hand-written ones on
recordings the first run never saw. Each run is a <b>draw</b>: one full run of the comparison on its
own set of simulated recordings. Simulated recordings only, untreated activity only, one of the lab's
two event streams (section 10).</p>

<p><b>Why this report exists.</b> A rehearsal of this comparison put two learned models slightly ahead
of the reference hand-written detector under its false-alarm budget. Whether a lead that small is real
depends on how far a result moves when nothing but the recordings changes, and one run cannot measure
that, so the comparison was run a second time. It feeds the project's decision about which detectors to
keep, which the project says is not yet final. Sections 1–5 explain the comparison itself, so that the
rest can be read cold; section 6 onward is what the second draw adds.</p>

<div class="box"><b>The answer, in plain words.</b>
<ul>
<li><b>Changing only the recordings moves a score by about a hundredth.</b> F1 balances events found
against false alarms. On new recordings, with the models' settings and training seeds held fixed, the
learned models' scores moved by a median of {med_net:.3f} and the hand-written detectors' by
{med_coded:.3f} (section 9); a rerun that also changed those would likely move them further. The
rehearsal's lead was about that size, so it could not have been told from luck.</li>
<li><b>As the comparison was run, every learned model trailed the reference detector, CoactDetect, in
every held-out quarter of the recordings in both draws</b>, when all were held to one shared cap on
false alarms (the budget, section 5). The closest, chorus_gain_norm, trailed on average by two to three
times the typical move (section 9).</li>
<li><b>Part of that shortfall is one setting.</b> Every detector joins calls that fall close together
into one call. The learned models joined calls within {net_merge:g} s, CoactDetect within
{cb['merge_gap_sec']:g} s. With both sides joining at the same gap, chorus_gain_norm still trailed under
the cap, by {rem_lo:.0%}–{rem_hi:.0%} of its as-run gap. Judged on F1 alone, the two chorus models
(learned models that pool a vote from every imaged cell, section 3) came out at or slightly above
CoactDetect where their training worked, by less than the typical move and without a test that
separates it from luck (section 9).</li>
<li><b>Training often failed for the two chorus models</b>, and the failures pull their averages down
(section 8).</li>
<li><b>What this does not show.</b> Anything about drugs, the lab's second event stream, or real
recordings. The simulator was fitted to a data folder with a known defect, and whether to refit it is
the project lead's open decision (section 10).</li>
</ul></div>
""")
    body.append(f"""
<h2>1. The problem: finding coordinated events</h2>
<p>A calcium-imaging recording of a brain slice is turned into a <b>raster</b>: one row per imaged
cell, called a <b>region of interest (ROI)</b>, and one mark per calcium event, at the moment the
event rose. A <b>coordinated event</b> is several ROIs' events rising together, within a fraction of
a second, more often than their own firing rates would explain. Finding them is the job of every
detector here.</p>
<p>It is hard for three reasons, and {ref_('raster', 'a simulated recording')}, shows two of them
plainly. The cells fire on their own too, at rates that differ from cell to cell and drift over
minutes, so chance coincidences are common. Some stretches are dense — many cells active, none of it
coordinated — which a detector that watches the overall rate will mistake for events. And an event
recruits only a few of the imaged cells, as few as {part_rois[-1]} here, which at this scale is a thin
column of marks that the answer key has to point to.</p>
""")
    body.append(fig("raster", f'<div class="figscroll"><img class="raster" src="{raster_uri}" '
        f'alt="A simulated bench recording, {rf["n_roi"]} ROIs over '
        f'{rf["duration_sec"] / 60:.0f} minutes, with planted events and CoactDetect\'s calls in a '
        f'lane above the raster"></div>' + figure1_key(rf),
        f"<b>One simulated recording from the second draw: seed {raster_seed}, quiet "
        f"background.</b> The top strip holds the answer key and CoactDetect's calls; below it, the "
        f"raster: {rf['n_roi']} ROIs over {rf['duration_sec'] / 60:.0f} minutes, one mark per "
        f"calcium event. CoactDetect, the hand-written detector used as the reference (section 3), "
        f"made {rf['n_calls']} calls at its reference settings; {rf['n_hit']} matched one of the "
        f"{rf['n_planted']} planted events and {rf['n_fa']} matched none, {rf['fa_on_distractor']} "
        f"of them on distractors. Another {rf['distractors_in_hits']} distractors lie inside calls "
        f"that matched a planted event: CoactDetect joins calls within "
        f"{cb['merge_gap_sec']:g} s, which joined each distractor to a nearby event, so they cost it "
        f"nothing. This recording draws no call in the dense stretch; across the second draw's "
        f"held-out recordings CoactDetect averages {dens('b', 'coact'):.2f} calls per recording "
        f"there."))
    assert rf["hot_fa"] == 0 and rf["distractors_in_hits"] >= 1
    body.append(f"""
<h2>2. Why a simulation, and what it simulates</h2>
<p>On a real recording nobody knows which coordinated events happened, so a detector can only be
compared with another detector, which measures agreement, not truth. A simulation plants the events
and keeps the answer key. Every recording here comes from the project's <b>bench</b>, a simulator
whose background activity was fitted to the untreated stretch of real recordings, before any drug —
the <b>baseline</b>. The lab's data come as two event streams, a fast and a slow one, for which the
export records an event's duration by different rules, and which respond to drugs differently; this
work uses only the fast stream.</p>
<p><b>What one bench recording holds.</b></p>
<ul>
<li>{rf['n_roi']} ROIs over {rf['duration_sec']:.0f} s ({rf['duration_sec'] / 60:.0f} minutes), at a
<b>quiet</b> or a <b>busy</b> background: {bg['quiet']:g} or {bg['busy']:g} events per second per
ROI, the 25th and 75th percentiles of real baseline rates.</li>
<li>{rf['n_planted']} planted coordinated events, at least {rf['min_sep_sec']:.0f} s apart:
{rf['n_per_level'][0]} at each of three sizes, recruiting {part[0]:.0%}, {part[1]:.0%} and
{part[2]:.0%} of the ROIs ({part_rois[0]}, {part_rois[1]} and {part_rois[2]} cells), each cell's
onset scattered by {rf['jitter_sec']:.2f} s (standard deviation).</li>
<li>{rf['n_distractors']} <b>distractors</b>: bursts built exactly like a planted {part[1]:.0%} event
({n_dist_rois} cells, the same scatter), placed without regard to the planted events; a call on one
counts as a false alarm.</li>
<li>A <b>dense stretch</b> of {hw[1] - hw[0]:.0f} s, from minute {hw[0] / 60:.0f} to minute
{hw[1] / 60:.0f}, in which every cell fires faster and nothing is planted (the project's glossary
calls it the promiscuity probe).</li>
<li>For every recording seed, an <b>empty recording</b>: the same background with nothing planted, at
seed + 100,000.</li>
</ul>
<p><b>Words used from here on.</b> A detector's <b>call</b> is one claimed event, with an onset and an
end. A call <b>matches</b> a planted event when the event lies within {TOL_SEC:g} s of the call, one
call to one event (the project's standard tolerance, <code>score.py</code>). Every detector keeps calls
at least some gap apart, usually by joining calls closer than that gap into a single call (locust
instead drops the lower of two nearby calls); that gap is its <b>merge</b>. The <b>reference</b> is
CoactDetect at the settings of section 3; it anchors the false-alarm budget of section 5.</p>
<p>A detector's score is its <b>F1</b>, the harmonic mean of <b>recall</b> (the share of planted
events it matched) and <b>precision</b> (the share of its calls that matched one). Calls in the dense
stretch are left out of precision and policed separately, by the budget. Hits and calls are summed over
the recordings scored together at each background, and the two backgrounds' F1 scores are averaged.
Because distractors look exactly like {n_dist_rois}-cell events, a detector that finds every planted
event and calls every distractor separately scores precision
{rf['n_planted']}/{rf['n_planted'] + rf['n_distractors']} and F1 {ceil_f1:.2f}. A merge long enough to
join a distractor to a nearby planted event hides that distractor inside a hit, as in
{ref_('raster', 'the simulated recording')}, so a long merge can score above {ceil_f1:.2f}; it is a
practical ceiling, not a hard one.</p>
""")
    body.append(f"""
<h2>3. The contestants</h2>
<p><b>Six hand-written ("coded") detectors</b>, each a rule with its own settings:</p>
<ul>
<li><b>rate+context</b> compares the population's event rate with the rate in a longer window around
the same moment.</li>
<li><b>CoactDetect</b> and <b>LoCo</b> (Local Coincidence) count how many distinct cells are active in
a short window, and compare that count with a <b>null</b>: the same count when each cell's events are
circularly shifted in time — moved by the cell's own offset within a context window around the test
window, wrapping at its ends — which keeps every cell's rate and pattern and breaks only the timing
between cells. The sliding versions used here compute that null exactly rather than sampling shifted
copies.</li>
<li><b>binned SCE</b> (synchronous calcium events) makes the same count in fixed time bins.</li>
<li><b>locust</b> counts cells co-active across a few frames against one cell-count threshold built
from circularly shifted copies.</li>
<li><b>SPIKE-synch</b> measures how tightly event times align across cells and calls where that
alignment is high.</li>
</ul>
<p>Three of the six descend from published methods and three were designed here; the origins are
recorded in <code>docs/detector_history.md</code>. Binned SCE descends from Cossart, Aronov and Yuste
(2003), from Rafael Yuste's laboratory, who tested counts of coactive cells against surrogates with each
cell's intervals reshuffled; the circular-shift null is the form the Cossart lab later adopted in its
own laboratory (Dard and colleagues, 2022), in its CICADA software, through which it reached this
project. locust is a modified port of CICADA. SPIKE-synch applies a threshold to the
SPIKE-synchronization measure of Kreuz, Mulansky and Bozanic (2015); the Kreuz lab introduced threshold
detection on that measure itself (Kreuz and colleagues, 2017; applied by Cecchini and colleagues, 2021),
so this is an implementation, not a new method. rate+context, CoactDetect and LoCo were designed here;
by the author's account they resemble radar constant-false-alarm-rate detection (Finn and Johnson, 1968)
without having been derived from it.</p>
<p><b>The reference, sliding CoactDetect.</b> CoactDetect counts distinct cells in a
{cb['int_win_sec']:g} s window that slides with the data and calls an event where the count is
improbably high: a z-score using the null's exact mean and standard deviation over a
{cb['context_win_sec']:g} s context, at a nominal significance level α = {sci(cb['alpha'])} (the tail
is treated as Gaussian, so the true rate of chance calls is higher). A {cb['guard_sec']:g} s band at the
center of the counting window is left out of the context, so the core of an event does not raise its
own threshold (its edges can). Calls within {cb['merge_gap_sec']:g} s are joined. Goal 1 of the
project, which tuned the coded detectors, chose these values on bench seeds 1–48 and checked them on
seeds 49–96, none of which is used here. LoCo and CoactDetect were first written with fixed time bins;
on three real baseline recordings, shifting a recording by a fraction of a second lost 30–36% of their
calls, so both now slide (sources in section 11).</p>
<p><b>Four learned models</b> ("nets"): small neural networks trained on bench recordings to give a
probability of a coordinated event at every {rf['dt']:g} s frame ({arch_ref}). Where that probability
crosses a threshold chosen in training, the net calls an event, and its calls are joined within a
fixed {net_merge:g} s; each coded detector instead tunes its own merge.</p>
<ul>
<li><b>chorus_norm</b> passes every cell through one shared encoder, standardizes each cell's encoder
output over time ("norm"), turns it into a bounded vote, and pools the votes of the whole "chorus" of
cells into three statistics: their mean, their spread, and the mean of the loudest few. The shape — one
encoder shared by every element, then a pool that ignores their order — is the construction formalized
as Deep Sets (Zaheer and colleagues, 2017) and reached independently by PointNet (Qi and colleagues,
2017); the three statistics are this project's choice. ({counts['chorus_norm']:,} parameters in its
default configuration.)</li>
<li><b>chorus_gain_norm</b> is chorus_norm with a fitted steepness ("gain") and midpoint on each vote.
({counts['chorus_gain_norm']:,} parameters.)</li>
<li><b>line_length</b> measures, at each moment, the share of imaged cells lit — the project's
"relative length" of the field, not the signal-processing line-length feature; each cell's vote is
bounded in height, though a cell that bursts holds it for longer. ({counts['line_length']:,}
parameters.)</li>
<li><b>tube</b> widens each cell's onsets to about a second, averages them over cells, and compares that
against its own surround in time with a center-minus-surround filter. It does not count distinct cells:
two bursting cells can score like four distinct ones. It is the project's control for tuning inflation:
untuned, it tied CoactDetect in an earlier comparison on the retired simulator, so if tuning lifts it
clear too, the gains are about the amount of tuning, not the architecture.
({counts['tube']:,} parameters.)</li>
</ul>
<p>Each net has {n_configs} configurations: {n_configs - 1} drawn at random from its hyperparameters
(learning rate, training length and its own shape parameters) plus the untuned default, the same
{n_configs} in both draws.</p>
<p class="note"><b>These are the models their names claim.</b> Built through the project's model
registry, as the trainer builds them, chorus_norm and chorus_gain_norm carry their registered settings.
Built by calling their bare builder functions, as a figure script or a notebook might, both silently
build plain chorus, and nothing complains. The runs went through the registry: both declarations give
chorus_gain_norm a search over its vote's steepness and chorus_norm none, and the fitted checkpoints
differ by the {counts['chorus_gain_norm'] - counts['chorus_norm']} parameters that steepness and midpoint
add. The same trap caught the project's own drawing check, which passed on the wrong model: a check
that runs correctly on the wrong subject is a different failure from a check that cannot fire.</p>
""")
    assert counts["chorus_gain_norm"] - counts["chorus_norm"] == 8
    assert all(any(ax[0] == "vote_gain" for ax in runs[k]["decl"]["learned_axes"]["chorus_gain_norm"])
               and not any(ax[0] == "vote_gain"
                           for ax in runs[k]["decl"]["learned_axes"]["chorus_norm"]) for k in runs)
    body.append(fig("arch", arch_body, arch_caption, hint=False))
    body.append(f"""
<h2>4. One run: nested cross-validation</h2>
<p>A score is honest only if nothing about the recordings it is measured on was used to choose what
is being measured. Each run therefore uses <b>nested cross-validation (CV)</b>
({ref_('cv', 'the nested cross-validation')}). Its {n_folds * per_fold} recording seeds are split into
{n_folds} <b>outer folds</b> of {per_fold} ({2 * per_fold} recordings: each seed at both backgrounds).
Each fold in turn is <b>held out</b>; everything — a net's configuration and threshold, a coded
detector's settings, the false-alarm budget — is chosen on the other three, then scored once on the
held-out fold. Folds are numbered 0–3, as in the runs' files (WSMIP064's own report numbers them
1–4).</p>
<p>A net's configurations are compared by <b>inner fits</b>. Each inner fit trains on two folds and is
scored on the other two; for any one held-out fold that leaves three pairs of training folds
({ref_('cv', 'the nested cross-validation')}), and across the draw there are
{math.comb(n_folds, 2)}, so a net has {inner_fits} inner fits per draw ({n_configs} configurations ×
{n_tune} training repeats × {math.comb(n_folds, 2)} pairs). The best pooled inner F1 wins. The winner,
the winner under the false-alarm budget (section 5) and the untuned configuration are each
<b>refitted</b> at {n_refit} training repeats and scored on the held-out fold
({min(refit_counts)}–{max(refit_counts)} refits per net per draw; fewer when two of the three pick the
same configuration). A net's score in a fold is the mean of its refits' F1. Every net fit trains on
{n_train} recordings drawn from its training folds and picks its threshold on {n_thresh} more. A coded
detector is tuned by a coordinate search on all {n_coded_train} training recordings.</p>
<p class="note"><b>A defect was fixed before either run started.</b> In the rehearsal, the nets for two
different held-out folds trained on the same ten recordings
(<code>docs/todo/2026-09-17-two-bake-off-folds-train-the-same-model.md</code>). Recordings are now dealt
round-robin across the training folds, and a check refuses to start a run unless every outer fold trains
its own models on its own recordings. Both runs passed it.</p>
""")
    body.append(fig("cv", fig_nested_cv("nested cross-validation", n_folds, per_fold, n_configs,
                                        n_tune, n_refit, n_train, n_thresh, n_coded_train, min_gain),
        f"<b>One run's nested cross-validation, drawn for held-out fold 0.</b> {sw('held')}the "
        f"held-out fold; {sw('box')}where fitting and choosing happen; {sw('score')}the fold an inner "
        "fit is scored on."))
    body.append(f"""
<h2>5. Two selections and one shared budget</h2>
<p>Each detector and net is chosen two ways, and each detector–selection pair is an <b>entry</b> (the
nets also have an untuned entry). <b>Chosen on F1 alone</b> takes the best score on the training
folds. But F1 leaves the dense stretch out of precision, and a detector that fires there, or on an empty
recording, is not usable. So each is also <b>chosen under the budget</b>: the best F1 among candidates
whose calls per hour stay under three ceilings shared by every entry
({ref_('budget', 'the shared budget')}). The three ceilings are calls per hour in the dense stretch at
each background, and on the quiet empty recording. Each is the reference's own rate on the fold's
training recordings times {margin:g}, a margin carried over from the bench's calibration of the binned
CoactDetect (source in section 11). The budget is therefore anchored to CoactDetect, and its reference
settings are admissible by construction. A net's candidate is a configuration <i>and</i> a threshold,
and under the budget the threshold chosen on the inner fits is carried onto all {n_refit} refits.</p>
<p><b>What the budget does not police.</b> Only the quiet empty recording is gated; the busy one is only
reported. Binned SCE fires {min(sce_busy_null):.0f}–{max(sce_busy_null):.0f} times per hour on the busy
empty recording (CoactDetect {min(coact_busy_null):.0f}–{max(coact_busy_null):.0f} calls per hour) and
passes. And the dense-stretch ceiling counts calls, not time spent calling: a detector whose long merge
joins a whole dense stretch into one call is charged once.</p>
""")
    body.append(fig("budget", fig_budget("the shared false-alarm budget", budget0, margin,
                                         ref["alpha"], busy_sec, bg["quiet"], ref["context_win_sec"]),
        f"<b>How the shared budget is set, with the second draw's outer fold 0.</b> "
        f"{sw('ref')}CoactDetect is run on the fold's training recordings; its calls per hour in "
        f"the dense stretch at each background, and on the empty recording, are each multiplied by "
        f"{margin:g} to give {sw('ceiling')}three ceilings. Every fold gets its own ceilings the "
        f"same way."))
    body.append(f"""
<h2>6. Why two draws</h2>
<p>The two runs' settings files differ in exactly two fields, the recording seeds and the draw number,
and by the branch history their code differs only in the option that sets the draw
({ref_('draws', 'the two draws')}): WSMIP064 ran the first draw and WSMIP065 the second. The rehearsal
before them differed in five ways: a simulator since retired, the coded side tuned on only three of its
settings, an older budget, the fold defect of section 4, and no limit on CoactDetect's context window,
which reached 240 s in some folds — wider than the planted spacing, so its null contained the events it
was testing. Its notes say not to quote it as a comparison (source in section 11). It is quoted here
only for the size of the margin that prompted this rerun:{f" under its budget chorus_norm led CoactDetect by {sgn(reh['chorus_norm'])} F1 and chorus_gain_norm by {sgn(reh['chorus_gain_norm'])}." if reh else ""}</p>
""")
    body.append(fig("draws", fig_two_draws("the two draws", runs),
        f"<b>The two draws' recording seeds, by outer fold.</b> {key('a')}The {A} and "
        f"{key('b')}the {B} use disjoint seeds; everything else — configurations, training repeats, "
        f"grids, the budget rule and the scoring — is the same."))
    body.append(f"""
<h2>7. Results of each draw</h2>
<p>Under the budget every net's mean sits below CoactDetect's in both draws (panel C of
{ref_('folds', 'every held-out fold')}; means in Table 1). CoactDetect scores
{f"{f3(mean['a'][('coact', 'ungated')])} in both draws" if same_coact_f1 else f"{f3(mean['a'][('coact', 'ungated')])} and {f3(mean['b'][('coact', 'ungated')])}"},
the same whichever way it is chosen: its choice on F1 alone already met the budget on its training
recordings in every fold. In the second draw its search never left the reference settings; in the first
it moved in {coact_moves['a']} of {n_folds} folds. Binned SCE leads CoactDetect on F1 alone in the first
draw ({sgn(sce_lead['a'])}) and ties it in the second ({sgn(sce_lead['b'])}), with settings that fail
goal 1's crowded-recording check in every fold of both draws (section 8).</p>
""")
    body.append(fig("folds", fig_per_fold(tabs, runs, "held-out F1 per fold", ceil_f1),
        f"<b>Held-out F1 in every outer fold: under the budget no net reaches CoactDetect.</b> Each dot "
        f"is one fold; {key('a')}first draw above {key('b')}second in each row, with a tick of the same "
        f"color at each draw's mean. A triangle at the left edge stands for every fold of that row "
        f"below {FOLD_LO:g}, with their number beside it when there is more than one; a row whose mean "
        f"is off the axis has no tick. The dotted line is the practical ceiling of section 2 "
        f"({ceil_f1:.2f}). The isolated low folds are the flagged ones of section 8."))
    body.append(table1)
    body.append(f"""
<h2>8. What the runs carry besides the models' skill</h2>
<h3>Training that failed</h3>
<p>Inner selection scores each configuration at {n_tune} training repeats, so a configuration that
fails at some of them can still win. In the second draw's fold {cn_fold}, chorus_norm's winner on F1
alone made one call per recording at {len(cn_bad)} of its {n_refit} refits
({ref_('collapse', 'the collapse')}): at a low threshold the whole recording became one call, which
matches one of the {rf['n_planted']} planted events, so F1 is exactly 0.125. That is consistent with an
output that barely varies with the input; the output itself is not examined here. Under the budget the
threshold sits above everything those refits output, so they call nothing. The fold's mean fell to
{f3(tabs['b'][('chorus_norm', 'ungated')][cn_fold])}, against
{f3(tabs['b'][('chorus_norm', 'untuned')][cn_fold])} untuned. It is not rare in this search (Table 2):
about a third of chorus_norm's inner fits did it and a sixth of chorus_gain_norm's. Across the two
draws, {len(cgn_failed)} refits of chorus_gain_norm did the same, and under the budget
{sum(nothing.values())} refits called nothing at all
({'; '.join(f"{c} of {NAMES[n]}'s in the {dname(k)}, fold {h}" for (k, n, h), c in nothing.items())}).
The two draws share their configurations and training seeds, so the same fits largely fail in both
({coll_both['chorus_norm']} of chorus_norm's are the same fit): Table 2 shows where training fails in
this search, not two independent measurements of how often.</p>
{table2}
""")
    body.append(fig("collapse", fig_collapse(b, "chorus_norm", cn_fold, "the collapse"),
        f"<b>chorus_norm in the second draw's outer fold {cn_fold}: the same two refits fail under "
        f"both selections.</b> One bar per refit, in {key('b')}the second draw's color. Panel A: the "
        f"untuned configuration trains normally at all {n_refit} refits. Panels B and C: the "
        f"configuration tuning chose, the same in both. Hatched: F1 0.125, one call per recording. "
        f"A ring on the baseline: no call at all, F1 0."))
    body.append(f"""
<h3>Searches that found no admissible setting</h3>
<p>Under the budget, locust's search found no admissible setting among those it reached, in any fold of
either draw: its starting point fires {min(cic_probe):.0f}–{max(cic_probe):.0f} times per hour in the
dense stretch at the quiet background, against ceilings of {min(ceil_q):.0f}–{max(ceil_q):.0f} per
hour, and every setting reachable by changing one setting across its whole grid was also over. Binned
SCE did the same in {len(sce_ref)} fold
({', '.join(f'the {dname(k)}, fold {h}' for k, h, _ in sce_ref)}). Those table entries carry ‡ and are
not results.</p>
<h3>Whether the held-out folds kept to the budget</h3>
<p>The budget is enforced on the training recordings. On the held-out recordings the run checked each
choice again (Table 3). Every net had refits go over — tube most, in
{compliance['a']['tube'][0]} of {compliance['a']['tube'][1]} refits in the first draw — against
CoactDetect's 1 of {2 * n_folds} folds
({', '.join(f'the {dname(k)}, fold ' + ', '.join(map(str, v)) for k, v in coact_over.items() if v) or 'none'}),
and the ‡ entries went over as their starting points do. For the nets two causes are possible and
neither was measured: a threshold chosen on inner fits and carried onto refits whose output is scaled
differently, and chance, since a held-out fold holds only an hour of dense stretch per background; for
CoactDetect, only chance. A choice over its ceiling was not held to the budget on those recordings; how
that moved its F1 was not measured.</p>
{table3}
<h3>Settings at the top of their grid, and the crowded-recording check</h3>
<p>A longer merge scores better on this bench: CoactDetect's own F1 rises from
{coact_by['b']['2']:.3f} at 2 s to {coact_by['b']['8']:.3f} at 8 s and {coact_by['b']['30']:.3f} at 30 s
in the second draw, partly because a long merge hides distractors inside hits (section 2). Inside a fold
the grids are fixed, so a setting that wanted to go further stops at the top, and the merge sat at the
top of its grid in every fold for all six coded detectors (Table 4). CoactDetect and LoCo started there,
at goal 1's {cb['merge_gap_sec']:g} s; the others moved there.</p>
<p>Goal 1 guards against exactly this with a fourth check this search did not apply: a setting may not
lose more than {max_drop:g} F1, on goal 1's crowded recordings (events as little as 6 s apart), against
the setting it replaces. WSMIP064's tool applied it afterwards to every coded choice of the first draw,
and the same tool, unchanged, to the second. It refuses
{and_list(f"{NAMES[d]} {SEL_WORDS[s]}" for d, s in cr_both)} in every fold of both draws{"; and " + and_list(f"{NAMES[d]} {SEL_WORDS[s]} in {cr_n[(d, s, k)]} of {n_folds} folds of the {dname(k)}" for d, s, k in cr_other) if cr_other else ""}.
CoactDetect passes in every fold of both draws, so the comparison of the nets with it is untouched; the
nets' merge is fixed, so the check does not apply to them. Those entries carry § and are left out of the
between-draw spread of section 9. Binned SCE's first-draw lead on F1 alone is one of them.</p>
{table4}
""")
    body.append(f"""
<h2>9. What the pair of draws can claim</h2>
<h3>How far results move between draws</h3>
<p>{ref_('moves', 'the between-draw moves')} shows each entry's second-draw mean minus its first. Among
entries with no flagged fold, the nets moved a median of {med_net:.3f} F1 in absolute value (at most
{max(net_moves):.3f}) and the coded detectors {med_coded:.3f} (at most {max(coded_moves):.3f});
CoactDetect's two selections count once. That is the scale any lead has to beat. It was measured with
the {n_configs} configurations and the training seeds held fixed, so it is the move from changing the
recordings alone, and probably understates how far a full rerun can move a result.</p>
<p>The rehearsal's leads ({', '.join(sgn(v) for v in reh.values()) if reh else 'about 0.01'}) are about
that size. The rehearsal ran six seeds per fold where these runs ran {per_fold}, so its own luck was, if
anything, larger: a single run could not have told its lead from the luck of the recordings. With five
things changed at once (section 6), the two draws cannot say which of them turned that lead around.</p>
<p>The moves are not independent noise either: {net_up} of {len(net_clean)} unflagged net entries rose
and {coded_not_up} of {len(coded_clean)} unflagged coded entries did not. The nets' mean signed move
minus the coded detectors' is {sgn(drift)}: the second draw favors the nets by about that much.</p>
""")
    body.append(fig("moves", fig_moves(tabs, runs, "between-draw moves"),
        "<b>Second draw minus first, mean held-out F1, for every entry: most move by about a "
        "hundredth.</b> Filled dots: entries with no flagged fold in either draw. Hollow dots: entries "
        "with a †, ‡ or § in either draw, which move for reasons other than the recordings."))
    body.append(f"""
<h3>The headline gap, as run</h3>
<p>{ref_('gaps', 'every net against CoactDetect')} shows each net minus CoactDetect in every outer fold
of both draws. Under the budget (panel B) every net sits below zero in every fold. {gnet}, the closest
on its mean over all four folds, trails by {abs(gap_g['a']['mean']):.3f} F1 in the first draw (standard
deviation over folds {gap_g['a']['sd']:.3f}) and {abs(gap_g['b']['mean']):.3f} in the second
({gap_g['b']['sd']:.3f}): on average two to three times the typical between-draw move, though single
folds trail by less. A paired t-test over the four folds, which the run computed, gives t = {tfmt['a']}
(p = {tt['a'][1]:.3f}) in the first draw and t = {tfmt['b']} (p = {tt['b'][1]:.2f}) in the second, on
{tdf} degrees of freedom; the folds share training data, so both p-values are optimistic (Dietterich,
1998; Bengio and Grandvalet, 2004). The gap itself moved {abs(gap_move):.3f} between draws, less than the
typical move, which is what agreement should look like but not proof of it.</p>
<p>Chosen on F1 alone (panel A), the best net's mean also trailed ({sgn(gap_u['a'])} for {bu_net['a']}
in the first draw, {sgn(gap_u['b'])} for {bu_net['b']} in the second), but those means carry the failed
refits of section 8. In the folds where their training worked, chorus_norm and chorus_gain_norm were
within {near_u:.3f} of CoactDetect, on either side, as run. Untuned, chorus_norm was {sgn(unt['a'])}
against CoactDetect in the first draw and {sgn(unt['b'])} in the second.</p>
""")
    off_words = "; ".join(f"{NAMES[n]} {SEL_WORDS[s]}, {dname(k)}, fold {f}"
                          for k, n, s, f in off_unflagged)
    body.append(fig("gaps", fig_gaps(runs, "net minus CoactDetect"),
        f"<b>Every net minus CoactDetect, one dot per outer fold, as run: under the budget no fold of "
        f"any net reaches zero.</b> {key('a')}First and {key('b')}second draw; zero is CoactDetect. A "
        f"triangle at the left edge is a fold below −0.15: {len(off_axis) - len(off_unflagged)} of "
        f"the {len(off_axis)} are folds where a net's training failed (section 8)"
        + (f", and the other is a low fold with no failed refit ({off_words})" if off_unflagged else "")
        + "."))
    assert len(off_unflagged) <= 1
    body.append(f"""
<h3>At a matched merge</h3>
<p>The nets joined their calls within {net_merge:g} s and CoactDetect within {cb['merge_gap_sec']:g} s,
and a longer merge scores better on this bench (section 8). So every net's held-out output and
CoactDetect's were decoded again with both sides at the same merge — 2, 4, 8 and 16 s, the grid of
WSMIP064's tool — changing nothing else ({ref_('matched', 'the matched merge')}, Table 5). No threshold
or setting was re-chosen. A longer merge can only lower a detector's call counts, so the nets' budgeted
choices at 4–16 s and CoactDetect's at 16 s stay within their ceilings; at 2 and 4 s CoactDetect's merge
is shorter than the 8 s it was chosen at, so it calls more there, and its budget was not rechecked at
those merges. Each re-decode at the run's own merge reproduced the run's F1: exactly, except
{sum(len(v) for v in inexact.values())} refits, off by at most {worst:.4f}, all at thresholds near the
top of the grid (probably the precision of re-running the model; not investigated).</p>
<p><b>Under the budget, part of {gnet}'s gap is the merge, and the rest survives.</b> With both sides at
the same merge it trails by {', '.join(f'{abs(v):.3f}' for v in g_matched['a'])} in the first draw and
{', '.join(f'{abs(v):.3f}' for v in g_matched['b'])} in the second (at 2, 4, 8 and 16 s), against
{abs(g_asrun['a']):.3f} and {abs(g_asrun['b']):.3f} as run: {rem_lo:.0%}–{rem_hi:.0%} of the gap
remains, and at 8 s it is still below zero in all {g8_neg} folds.</p>
<p><b>On F1 alone, the two chorus models come out at or slightly above CoactDetect.</b> Over the folds
where they trained, their mean is above CoactDetect's at every matched merge, by
{min(ch_m):.3f}–{max(ch_m):.3f}, and at 8 s they are ahead in {sum(ch8)} of those {len(ch8)} folds. That
is within the typical move, and it is not established: the same paired test at 8 s passes p &lt; 0.05 in
{ch_sig} of the {len(ch_t)} model-by-draw cases, and with their failed folds counted — a user of these
models gets the failures too — the mean at 8 s is below CoactDetect's in {ch_all_neg} of the
{len(ch_all8)}. line_length and tube trail at every merge in every fold.</p>
<p>The matched merge is not the better comparison, only the other one: at 8 s CoactDetect runs at
settings tuned for 8 s and the nets at thresholds chosen for 2 s, and at 2 s the reverse. The first
cost is visible: re-decoded at 8 s, one line_length fold on F1 alone lost {abs(ll_hurt):.3f} F1
(the line running off the left of {ref_('matched', 'the matched merge')}).</p>
""")
    body.append(fig("matched", fig_matched(mgap, runs, "the matched merge"),
        f"<b>A matched merge closes part of the budgeted gap, not all of it.</b> Net minus CoactDetect "
        f"per outer fold, as run and with both sides' merge at 8 s; zero is CoactDetect. Each line is "
        f"one fold: {key('a')}first draw, {key('b')}second; hollow at the as-run gap, filled at the "
        f"matched one. A triangle at the left edge is a value below −0.15, and a line running off the "
        f"left edge ends below it. Folds whose refits made one call per recording or called nothing "
        f"are left out and counted beside the net's name. Table 5 gives the means at 2, 4, 8 and 16 s."))
    body.append(table5)
    body.append(f"""
<h3>Where the as-run gap is</h3>
<p>It is in precision, and in the smallest events. Pooled, {gnet} found at least as many planted events
as CoactDetect under the budget (recall {rec['a'][gnet]:.2f} against {rec['a']['coact']:.2f} in the
first draw, {rec['b'][gnet]:.2f} against {rec['b']['coact']:.2f} in the second), but that hides where
(Table 6). On the two larger event sizes both find nearly every event. On {part_rois[-1]}-cell events
at the busy background CoactDetect finds only {by_size['a'][('coact', 'busy', small)]:.2f} and
{by_size['b'][('coact', 'busy', small)]:.2f} of them (first and second draw), {gnet}
{by_size['a'][(gnet, 'busy', small)]:.2f} and {by_size['b'][(gnet, 'busy', small)]:.2f}; at the quiet
background the two are closer, and {gnet} finds fewer. Its precision is lower at both backgrounds.</p>
<p>In {ref_('split', 'where the false alarms fall')}, {gnet} makes fewer
than CoactDetect in the dense stretch and more outside it
({outside_fa(facts['a']['split'][(gnet, 'gated')]):.1f} against
{outside_fa(facts['a']['split'][('coact', 'gated')]):.1f} per recording in the first draw,
{outside_fa(facts['b']['split'][(gnet, 'gated')]):.1f} against
{outside_fa(facts['b']['split'][('coact', 'gated')]):.1f} in the second).
{and_list([n for n in pattern if n != gnet])} {"shows" if len([n for n in pattern if n != gnet]) == 1 else "show"} the same pattern in both draws{"" if not first_only else ", " + and_list(first_only) + " in the first only"};
tube instead calls more than CoactDetect in the dense stretch. The score files do not record which of the
false alarms outside the dense stretch fell on distractors.</p>
{table6}
""")
    assert [n for n in pattern if n != gnet]
    body.append(fig("split", fig_split(facts, "held-out false alarms by where they fall",
                                       split_entries),
        f"<b>The nets' extra false alarms fall outside the dense stretch.</b> False alarms per held-out "
        f"recording, for entries chosen under the budget. Two bars per entry: {key('a')}first draw, "
        f"then {key('b')}second. {sw('c-dense')}In the dense stretch (not counted in precision); "
        f"{sw('c-other')}outside it. The four nets, then CoactDetect and LoCo, the two coded detectors "
        f"that, like the nets, count across cells in a short window."))
    body.append(f"""
<h3>Tuning</h3>
<p>Tuning on F1 alone raised line_length over its untuned default by {abs(ll['a']):.3f} and
{abs(ll['b']):.3f} F1, the same direction in both draws (paired tests over the folds, p =
{ll_t['a'][1]:.2f} and {ll_t['b'][1]:.2f}); consistent, small, and not firmly established. tube, the
control for tuning inflation, moved by {sgn(tube_t['a'])} and {sgn(tube_t['b'])}, less than the typical
move: tuning did not lift it. For chorus_norm the change was {sgn(cn_t['a'])} and {sgn(cn_t['b'])}; the
second is the failed training of section 8, so tuning's effect on chorus_norm cannot be separated from
it.</p>
<h2>10. Limits a reader must be told</h2>
<ul>
<li><b>Baseline only, fast stream only.</b> By the project's decision (<code>docs/goals/README.md</code>),
these runs use only the untreated part of the recordings and only the fast stream. Nothing here says
how any detector behaves under a drug, or on the slow stream, whose event rate under tetrodotoxin (TTX,
a sodium channel blocker applied to the slice) rises while the fast stream's falls
(<code>docs/FOUNDATIONS.md</code> §9).</li>
<li><b>The simulator was fitted to a folder with a known defect.</b> The bench's constants were measured
on the <code>steps_excluded</code> export (the lab's data folder), in which motion correction pinned 12
ROIs in 4 recordings to the frame's floor value, about 0.03% of the folder's events. Measured again on
the corrected export, on both workstations, seven of the bench's eight fitted rates and shares were
unchanged to four decimals or moved far inside their bootstrap intervals; the share of ROIs a 6-cell
event recruits sits just outside its interval on both exports, because the bench stores 0.18 (6 of 33)
where the data say 0.19. Whether that settles it, and whether to point the bench at the corrected
export, is the project lead's open decision; these results are conditional on it (sources in section
11).</li>
<li><b>The two sides were not treated alike</b> (Table 7). The merge is the difference measured above;
the others were not varied.</li>
<li><b>Settings fixed before the runs and never varied:</b> the budget's margin of {margin:g}, the
{TOL_SEC:g} s tolerance, {n_train} training and {n_thresh} threshold recordings per fit, {n_tune} and
{n_refit} training repeats, and the coordinate search's minimum gain of {min_gain:g}. How the headline
depends on any of them is untested.</li>
<li><b>What the budget does not police</b> (section 5): the busy empty recording, and time spent
calling in the dense stretch.</li>
<li><b>The crowded-recording check came after the run</b> (section 8). The search could choose settings
the check refuses, and did; the § entries are reported, not results.</li>
<li><b>Recall by event size is shown only for the headline pair</b> (Table 6); every other number pools
the three sizes.</li>
<li><b>Simulation only.</b> Every result is on simulated recordings; the one real-recording number quoted
(30–36%, section 3) comes from another document.</li>
</ul>
{table7}
<h2>11. Where everything is</h2>
<p><code>&lt;darkroom&gt;</code> is the project's shared figure folder, the same on every
workstation.</p>
<ul>
<li>The second draw, all of it: <code>&lt;darkroom&gt;/bugarach/{MINE_FOLDER}/results/</code> — the
declaration (<code>meta.json</code>), <code>results.json</code>, every fold's selection, the chosen
refits, the fits and score tables as two archives ({b['results']['n_fits']:,} fits;
{b['results']['cpu_hours_training']:.1f} hours of training on one graphics processor),
<code>merge_gap.json</code> (the matched-merge re-decode) and <code>crowded_check.json</code> (the
crowded-recording check). The chorus models are not on <code>main</code>; they load from branch
<code>replicate-run</code>.</li>
<li>The first draw: <code>&lt;darkroom&gt;/bugarach/{THEIRS_FOLDER}/results/</code>
({a['results']['n_fits']:,} fits; {a['results']['cpu_hours_training']:.1f} hours); its matched-merge
re-decode and crowded check are <code>merge_gap.json</code> and <code>crowded_check.json</code> in
<code>docs/learned/tuned_vs_coact/fair_comparison_2026_09_18/</code> (branch
<code>nets/fair-comparison-report</code>). WSMIP064 writes its own report on it.</li>
<li>Both checks are WSMIP064's tools on that branch, run unchanged on each draw:
<code>tools/fair_comparison_evidence.py merge-gap</code> and
<code>tools/crowded_check_fair_comparison.py</code>.</li>
<li>The draw option is <code>--replicate</code> in <code>tools/tune_learned_vs_coact.py</code> on branch
<code>replicate-run</code>; <code>--replicate 0</code> declares exactly what the first draw declared.</li>
<li>Sources for the history. The {margin:g} margin, the bench's constants on the corrected export, and
tube's tie with CoactDetect on the retired simulator: <code>HANDOFF-workstation-tuning.md</code> (branch
<code>tune-bench-comparison</code>). The 30–36% of calls lost to binning:
<code>docs/todo/2026-09-07-detector-calls-move-with-the-grid.md</code> (<code>main</code>), measured on
the same <code>steps_excluded</code> export, and summarized in <code>docs/forks.md</code> §14 (branch
<code>tune-bench-comparison</code>). The rehearsal and why not to quote it:
<code>docs/learned/tuned_vs_coact/shakedown_home_spec/README.md</code> (same branch). The open decision
on the bench: item 3 of the decisions in
<code>HANDOFF-slow-comodulation-on-the-de-pinned-export.md</code> (<code>main</code>). That the choice of
detectors is not final: <code>docs/goals/README.md</code> and
<code>docs/goals/learned-model-family.md</code> (<code>main</code>). Goal 1's values, its seeds and its
crowded check: <code>docs/goals/coded-detector-optimization.md</code> and
<code>HANDOFF-coded-detectors.md</code> (branch <code>opt-every-knob-run</code>).</li>
<li>This page is built by <code>tools/make_replicate_report.py</code>. Its results — every score, gap,
count, rate, flag, grid top and parameter count — are computed from the two runs' folders, the
matched-merge and crowded-check files and the rehearsal's <code>results.json</code>, and the build
asserts the page's result claims against those files. The history and the detector descriptions in
sections 2–6, 8 and 10 are written by hand and cite their sources.</li>
</ul>
<h2>References</h2>
<ul class="refs">
<li>Bengio Y, Grandvalet Y (2004). No unbiased estimator of the variance of K-fold cross-validation.
<i>Journal of Machine Learning Research</i> 5:1089–1105.
https://www.jmlr.org/papers/v5/grandvalet04a.html</li>
<li>Cecchini G, Scaglione A, Allegra Mascaro AL, Checcucci C, Conti E, Adam I, Fanelli D, Livi R,
Pavone FS, Kreuz T (2021). Cortical propagation tracks functional recovery after stroke. <i>PLoS
Computational Biology</i> 17(5):e1008963. doi:10.1371/journal.pcbi.1008963</li>
<li>Cossart R, Aronov D, Yuste R (2003). Attractor dynamics of network UP states in the neocortex.
<i>Nature</i> 423:283–288. doi:10.1038/nature01614</li>
<li>Dard R and colleagues, with Cossart R and Picardo M (2022). <i>eLife</i> 11:e78116.
doi:10.7554/eLife.78116</li>
<li>Denis J, Dard R, Quiroli E, Cossart R, Picardo M (2020). CICADA: Calcium Imaging Complete
Automated Data Analysis, version 1.0.3 (software). Zenodo. doi:10.5281/zenodo.10041434</li>
<li>Dietterich TG (1998). Approximate statistical tests for comparing supervised classification
learning algorithms. <i>Neural Computation</i> 10(7):1895–1923. doi:10.1162/089976698300017197</li>
<li>Finn HM, Johnson RS (1968). Adaptive detection mode with threshold control as a function of
spatially sampled clutter-level estimates. <i>RCA Review</i> 29(3):414–464.</li>
<li>Kreuz T, Mulansky M, Bozanic N (2015). SPIKY: a graphical user interface for monitoring spike train
synchrony. <i>Journal of Neurophysiology</i> 113(9):3432–3445. doi:10.1152/jn.00848.2014</li>
<li>Kreuz T, Satuvuori E, Pofahl M, Mulansky M (2017). Leaders and followers: quantifying consistency
in spatio-temporal propagation patterns. <i>New Journal of Physics</i> 19(4):043028.
doi:10.1088/1367-2630/aa68c3</li>
<li>Qi CR, Su H, Mo K, Guibas LJ (2017). PointNet: deep learning on point sets for 3D classification
and segmentation. <i>CVPR 2017</i>. arXiv:1612.00593</li>
<li>Zaheer M, Kottur S, Ravanbakhsh S, Póczos B, Salakhutdinov R, Smola AJ (2017). Deep Sets.
<i>Advances in Neural Information Processing Systems</i> 30. arXiv:1703.06114</li>
</ul>
""")
    return ("<!doctype html><html lang='en'><head>"
            "<meta name='viewport' content='width=device-width,initial-scale=1'>"
            "<meta name='date' content='2026-09-19'><meta name='author' content='bugarach, WSMIP065'>"
            "<meta charset='utf-8'><title>Two draws of the comparison</title><style>" + CSS
            + "</style></head><body>"
            + "".join(body) + "</body></html>")


def untuned_param_counts(run: dict) -> dict:
    """Each net's parameter count at its untuned configuration, read from one of the run's own
    fitted checkpoints, with the checkpoint format checked as `learn.checkpoint.peek` does. The
    chorus models are registered only on the tuning branch, and building one from its bare entry
    point silently builds a different model, so the run's own files are the authority."""
    from bugarach.learn.checkpoint import FORMAT as fmt

    out = {}
    keys = {m: run["decl"]["configurations"][m][-1] for m in NETS}
    for m, key in keys.items():
        assert json.loads((run["folder"] / "configs" / m / f"{key}.json").read_text())["is_untuned"]
    want = {m: f"fits/{m}/{k}/" for m, k in keys.items()}
    for name, raw in Archive(run["folder"], "fits").items(
            lambda n: n.endswith(".json") and not n.endswith(".run.json")
            and any(n.startswith(p) for p in want.values())):
        m = name.split("/")[1]
        if m in out:
            continue
        c = json.loads(raw)
        assert c.get("format") == fmt, f"{name}: checkpoint format {c.get('format')}"
        out[m] = int(c["n_params"])
    assert set(out) == set(NETS)
    return out


def main(argv=None) -> int:
    from bugarach.paths import darkroom, unresolved_message

    p = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    p.add_argument("--mine", type=Path, default=None,
                   help=f"this machine's results folder (default <darkroom>/{MINE_FOLDER}/results)")
    p.add_argument("--theirs", type=Path, default=None,
                   help=f"the other draw's results folder (default <darkroom>/{THEIRS_FOLDER}/results)")
    p.add_argument("--rehearsal", type=Path, default=None,
                   help="the rehearsal's results.json (docs/learned/tuned_vs_coact/"
                        "shakedown_home_spec/results.json on branch tune-bench-comparison)")
    p.add_argument("--out", type=Path, default=None,
                   help=f"default <darkroom>/{MINE_FOLDER}/report/report.html")
    p.add_argument("--also", type=Path, default=None, help="a second copy, e.g. the repo's")
    p.add_argument("--merge-gap-mine", type=Path, default=None,
                   help="this draw's matched-merge re-decode (default <mine>/merge_gap.json)")
    p.add_argument("--merge-gap-theirs", type=Path, default=REPO / THEIRS_MERGE_GAP,
                   help=f"the other draw's (default {THEIRS_MERGE_GAP}, which lands with "
                        "WSMIP064's report)")
    p.add_argument("--crowded-mine", type=Path, default=None,
                   help="this draw's crowded-recording check (default <mine>/crowded_check.json)")
    p.add_argument("--crowded-theirs", type=Path, default=REPO / THEIRS_CROWDED,
                   help=f"the other draw's (default {THEIRS_CROWDED}, which lands with WSMIP064's "
                        "report)")
    p.add_argument("--arch-svg", type=Path, default=REPO / ARCH_SVG,
                   help=f"the four architectures drawn at one scale (default {ARCH_SVG}); the "
                        "figure falls back to a marked slot when it is absent")
    p.add_argument("--raster-seed", type=int, default=2000)
    p.add_argument("--raster-regime", default="baseline_quiet")
    a = p.parse_args(argv)
    mine = a.mine or darkroom(MINE_FOLDER, "results")
    theirs = a.theirs or darkroom(THEIRS_FOLDER, "results")
    out = a.out or darkroom(MINE_FOLDER, "report", "report.html")
    if mine is None or theirs is None or out is None:
        print(unresolved_message("--mine/--theirs/--out"), file=sys.stderr)
        return 2
    page = build(Path(mine), Path(theirs), a.rehearsal, a.raster_seed, a.raster_regime,
                 a.merge_gap_mine or Path(mine) / "merge_gap.json", a.merge_gap_theirs,
                 a.crowded_mine or Path(mine) / "crowded_check.json", a.crowded_theirs, a.arch_svg)
    for dest in [Path(out)] + ([a.also] if a.also else []):
        dest.parent.mkdir(parents=True, exist_ok=True)
        tmp = dest.with_suffix(".tmp")
        tmp.write_text(page, encoding="utf-8")
        tmp.replace(dest)
        print(f"wrote {dest}  ({len(page) / 1e6:.2f} MB)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
