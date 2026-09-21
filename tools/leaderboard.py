#!/usr/bin/env python3
# instrument: staleness
"""The detector challenge's standing, derived from the runs' own files.

    python3 tools/leaderboard.py                 # darkroom copy
    python3 tools/leaderboard.py --also docs/learned/leaderboard.html

**Nothing here is retyped.** Every margin, interval and verdict is read from the
committed comparison files and recomputed on the spot. That is the whole point:
`bakeoff.md` retypes nine rows a token could substitute, and one of its claims went
stale for eight days
(`docs/todo/2026-08-28-the-bakeoff-page-transcribes-what-a-token-could-substitute.md`),
which is the failure a fourth hand-maintained table would inherit.

**Why this is not a ranking.** Sorted by F1 alone this page would have shown a net on
top on the morning of 2026-09-20, and by that evening the review had established that
the two selections disagree, that the margins sit at about one draw-to-draw noise unit,
and that the two sides of the comparison are not the same kind of object — CoactDetect
is one deterministic value per outer fold, each net is five refits, some of which fail
to train. So the columns carry the qualification the rank would hide, and the verdict
line is computed from the bar the goal page states rather than from who is highest.

**The bar** (`docs/goals/learned-model-family.md`): a learned detector earns its place
only by clearing the coded detectors **separably** — by a margin the fold-to-fold
variation cannot explain — and by being understood well enough that the margin is
attributable to its shape rather than to its tuning budget. The first clause is what
this page computes. The second is a judgement and is reported as an open question, not
scored.

**Separability** uses the corrected *t* the runs already record: the paired statistic
over outer folds times the Nadeau-Bengio factor for a train/test split reused across
folds. A margin is called separable when the corrected two-sided interval excludes zero
at 95 %, which at df = 3 means |t_corrected| > 3.182. That threshold is deliberately
harsh for four folds and it is meant to be.

**Attempts are counted and shown.** Every model-by-selection-by-variant comparison in
the source files is one shot at the bar. At margins this size the count is not a
footnote: the more configurations compared, the more likely one clears by chance.
"""

from __future__ import annotations

import argparse
import html
import json
import sys
from dataclasses import dataclass
from datetime import date
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
RUNS = REPO / "docs" / "learned" / "tuned_vs_coact" / "fair_comparison_2026_09_18"

# Two-sided 95 % critical value of Student's t at df = 3, the four outer folds.
T_CRIT_DF3 = 3.182

DRAWS = [
    ("first draw", "net_merge_gap.json"),
    ("replicate", "replicate_net_merge_gap.json"),
]

SELECTIONS = [
    ("gated", "under the shared false-alarm budget"),
    ("ungated", "on F1 alone"),
]

# What each comparison variant means, in the source files' own vocabulary.
VARIANTS = {
    "as_run": "as the run scored it, the net's merge gap fixed at 2 s",
    "config_kept": "the net's merge gap tuned, its configuration kept",
    "config_rechosen": "the net's merge gap tuned and its configuration re-chosen",
}


@dataclass
class Row:
    draw: str
    selection: str
    model: str
    variant: str
    mean: float
    t_corrected: float
    folds_ahead: int
    folds: int
    within_noise: bool

    @property
    def separable(self) -> bool:
        """Does the corrected interval exclude zero, in the net's favour?"""
        return self.mean > 0 and abs(self.t_corrected) > T_CRIT_DF3

    @property
    def verdict(self) -> str:
        if self.separable:
            return "clears"
        if self.mean > 0:
            return "ahead, not separably"
        return "behind"


def read_rows(runs: Path) -> tuple[list[Row], dict]:
    """Every comparison in every committed draw, plus the shared constants."""
    rows: list[Row] = []
    constants: dict = {}
    for draw, filename in DRAWS:
        path = runs / filename
        if not path.exists():
            continue
        doc = json.loads(path.read_text())
        constants.setdefault("noise_f1", doc.get("noise_f1"))
        constants.setdefault("nb_factor", doc.get("nb_factor"))
        constants.setdefault("as_run_gap_sec", doc.get("as_run_gap_sec"))
        constants.setdefault("max_crowded_drop", doc.get("max_crowded_drop"))
        for selection, _ in SELECTIONS:
            for key, cmp in doc.get("comparisons", {}).get(selection, {}).items():
                # keys read "<model> <variant> - coact"
                head = key.rsplit(" - ", 1)[0]
                model, _, variant = head.rpartition(" ")
                rows.append(
                    Row(
                        draw=draw,
                        selection=selection,
                        model=model,
                        variant=variant,
                        mean=cmp["mean"],
                        t_corrected=cmp["t_corrected"],
                        folds_ahead=cmp["folds_ahead"],
                        folds=cmp["folds"],
                        within_noise=cmp["within_noise"],
                    )
                )
    return rows, constants


def standing(rows: list[Row]) -> str:
    """The one sentence the page exists to print, computed rather than written."""
    cleared = [r for r in rows if r.separable]
    if not cleared:
        ahead = [r for r in rows if r.mean > 0]
        return (
            f"No learned detector has cleared the bar. "
            f"Of {len(rows)} comparisons, {len(ahead)} put a net ahead of CoactDetect at all, "
            f"and none of those margins is separable from fold-to-fold variation."
        )
    names = sorted({r.model for r in cleared})
    return (
        f"{len(cleared)} of {len(rows)} comparisons clear the bar separably: "
        f"{', '.join(names)}. Read the attempt count beside this."
    )


# The one qualification the table cannot carry in a column, and the page would
# mislead without it — in the other direction from a naive ranking.
ACCOUNTING = (
    "These rows count <strong>every refit</strong>. A second accounting sets aside the "
    "refits that failed to train — those scoring under 0.2 F1 — and under it both chorus "
    "nets lead on F1 alone in the replicate. Neither accounting is neutral, which is the "
    "point: CoactDetect is one deterministic value per outer fold while each net is five "
    "refits, some of which collapse, so a rule that drops the collapses is not the same "
    "test applied to both sides. The goal page reports both and so should any reading of "
    "this table."
)


def esc(text: object) -> str:
    return html.escape(str(text))


def render(rows: list[Row], constants: dict) -> str:
    noise = constants.get("noise_f1")
    nb = constants.get("nb_factor")
    draws = sorted({r.draw for r in rows}, key=lambda d: [n for n, _ in DRAWS].index(d))
    models = sorted({r.model for r in rows})

    # The charset opens the head, before anything that could carry an en-dash.
    # Without it a page opened from disk is read as Latin-1 and every — in it
    # becomes mojibake; sapper SAP005 enforces the ordering on this line.
    head = (
        # Charset and title share a line on purpose: sapper SAP005 matches per
        # line, so a title opening its own string reads as a head with no charset.
        '<meta charset="utf-8"><title>Detector challenge, standing</title>'
        '<meta name="viewport" content="width=device-width,initial-scale=1">'
        "<style>"
        ":root{--ink:#16191d;--ground:#faf9f7;--rule:#dfdcd6;--muted:#6b7178;"
        "--clears:#1f6353;--near:#8f5514;--behind:#6b7178}"
        "body{margin:0;background:var(--ground);color:var(--ink);"
        "font:15px/1.6 ui-sans-serif,system-ui,-apple-system,sans-serif}"
        ".wrap{max-width:60rem;margin:0 auto;padding-inline:20px;padding-block:2.5rem 4rem}"
        "h1{font-size:1.8rem;line-height:1.2;margin:0 0 .4rem}"
        "h2{font-size:1.15rem;margin:2.4rem 0 .5rem}"
        ".standing{font-size:1.1rem;line-height:1.5;padding:1rem 1.1rem;"
        "background:#fff;border-left:3px solid var(--ink);margin:1.2rem 0}"
        ".note{color:var(--muted);font-size:.92rem}"
        "table{width:100%;border-collapse:collapse;font-size:.9rem;"
        "font-variant-numeric:tabular-nums}"
        "th,td{text-align:left;padding:.45rem .6rem .45rem 0;"
        "border-bottom:1px solid var(--rule);vertical-align:top}"
        "th{font-size:.7rem;letter-spacing:.07em;text-transform:uppercase;"
        "color:var(--muted);font-weight:600}"
        "td.n{text-align:right;padding-right:1.1rem;font-variant-numeric:tabular-nums}"
        ".v-clears{color:var(--clears);font-weight:600}"
        ".v-ahead{color:var(--near)}"
        ".v-behind{color:var(--behind)}"
        ".scroll{overflow-x:auto}"
        "code{font:.88em ui-monospace,monospace}"
        "</style>"
    )
    parts: list[str] = []
    parts.append(f"<!doctype html>\n<html lang=\"en\">\n<head>{head}</head>\n")
    parts.append("<body><div class='wrap'>")
    parts.append("<h1>Detector challenge — standing</h1>")
    parts.append(
        f"<p class='note'>Derived from the runs' own comparison files on "
        f"{esc(date.today().isoformat())}. Nothing on this page is retyped.</p>"
    )
    parts.append(f"<p class='standing'>{esc(standing(rows))}</p>")
    parts.append(f"<p class='note'>{ACCOUNTING}</p>")

    parts.append("<h2>The bar</h2>")
    parts.append(
        "<p>A learned detector earns its place only by clearing the coded detectors "
        "<strong>separably</strong> — by a margin the fold-to-fold variation cannot "
        "explain — and by being understood well enough that the margin is attributable "
        "to its shape rather than to its tuning budget.</p>"
        "<p class='note'>The first clause is computed here: a margin counts as separable "
        f"when the Nadeau-Bengio corrected |<em>t</em>| over 4 outer folds exceeds "
        f"{T_CRIT_DF3} (two-sided 95 %, df = 3)"
        + (f", the correction factor being {nb:.4f}" if nb else "")
        + ". The second clause is a judgement and is not scored.</p>"
    )
    if noise:
        parts.append(
            f"<p class='note'>Scale: changing only which recordings were drawn moves a net "
            f"by a median of {noise} F1. Most margins below are that size.</p>"
        )

    for selection, gloss in SELECTIONS:
        sel_rows = [r for r in rows if r.selection == selection]
        if not sel_rows:
            continue
        parts.append(f"<h2>Selected {esc(gloss)}</h2>")
        parts.append("<div class='scroll'><table><thead><tr>")
        parts.append(
            "<th>model</th><th>comparison</th><th>draw</th>"
            "<th class='n'>margin F1</th><th class='n'>corrected t</th>"
            "<th class='n'>folds ahead</th><th>verdict</th></tr></thead><tbody>"
        )
        for model in models:
            for variant in VARIANTS:
                for draw in draws:
                    match = [
                        r
                        for r in sel_rows
                        if r.model == model and r.variant == variant and r.draw == draw
                    ]
                    if not match:
                        continue
                    r = match[0]
                    cls = (
                        "v-clears"
                        if r.separable
                        else ("v-ahead" if r.mean > 0 else "v-behind")
                    )
                    parts.append(
                        f"<tr><td><code>{esc(r.model)}</code></td>"
                        f"<td class='note'>{esc(VARIANTS[variant])}</td>"
                        f"<td class='note'>{esc(r.draw)}</td>"
                        f"<td class='n'>{r.mean:+.4f}</td>"
                        f"<td class='n'>{r.t_corrected:+.2f}</td>"
                        f"<td class='n'>{r.folds_ahead} of {r.folds}</td>"
                        f"<td class='{cls}'>{esc(r.verdict)}</td></tr>"
                    )
        parts.append("</tbody></table></div>")

    parts.append("<h2>Attempts</h2>")
    parts.append(
        f"<p>{len(rows)} comparisons across "
        f"{len(models)} models, {len(SELECTIONS)} selection rules, "
        f"{len(draws)} draws and {len(VARIANTS)} merge-gap treatments. "
        "Every one is a shot at the bar, and at these margins the count is not a "
        "footnote: the more configurations compared, the more likely one clears by "
        "chance. A final run should be read against this number.</p>"
    )

    parts.append("<h2>What is not frozen</h2>")
    parts.append(
        "<p>A stopping rule was deliberately not set on 2026-09-21, because three "
        "things that move these numbers are still in motion. Until they land, this "
        "page reports a standing rather than a result.</p><ul>"
        "<li>The <strong>crowded-recording allowance</strong> is unsigned. Every chosen "
        "merge gap is the boundary it imposes rather than an optimum, so every margin "
        "here is a function of it.</li>"
        "<li>The <strong>training-collapse mechanism</strong> is unresolved: the stored "
        "census cannot separate a signal that died inside a net's head from one that "
        "never reached it.</li>"
        "<li>The <strong>merge-gap page's verdict</strong> is being demoted to a "
        "measurement, because the two sides of the comparison are not the same kind of "
        "object and no accounting between them is neutral.</li></ul>"
    )
    parts.append("</div></body></html>")
    return "".join(parts)


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument(
        "--out",
        type=Path,
        default=None,
        help="where to write; defaults to the darkroom, per FOUNDATIONS §5",
    )
    ap.add_argument(
        "--also",
        type=Path,
        default=None,
        help="a second copy, normally the repo one review and git history need",
    )
    ap.add_argument("--runs", type=Path, default=RUNS, help="the run's summary folder")
    args = ap.parse_args(argv)

    rows, constants = read_rows(args.runs)
    if not rows:
        print(f"no comparison files under {args.runs}", file=sys.stderr)
        return 2

    page = render(rows, constants)

    out = args.out
    if out is None:
        from bugarach.paths import darkroom

        out = darkroom() / "leaderboard.html"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(page)
    print(f"wrote {out}")

    if args.also:
        args.also.parent.mkdir(parents=True, exist_ok=True)
        args.also.write_text(page)
        print(f"wrote {args.also}")

    print(standing(rows))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
