#!/usr/bin/env python3
# instrument: staleness
"""The detector challenge's full field, derived from the runs' own files.

    python3 tools/leaderboard.py                 # darkroom copy
    python3 tools/leaderboard.py --also docs/learned/leaderboard.html

**Every player, not a challenger against one champion.** All six coded detectors were
tuned per outer fold by the every-knob search, and all four nets were trained against
them, so the field is ten. An earlier draft of this tool ranked nets against CoactDetect
alone, which made the other five coded detectors look ignored and made CoactDetect look
like an arbitrary favourite. It is neither: it is the highest-scoring coded detector
whose chosen settings pass the crowded-recording veto in every fold, and that sentence
is what the earlier draft was missing.

**The raw leader is not the admissible leader.** Binned SCE tops mean held-out F1 under
both selections, and its chosen settings fail the veto in 3 of 4 folds under the budget
and 4 of 4 on F1 alone, because it gets there with a 30 s merge gap that fuses genuinely
separate events on crowded recordings. So the table carries a veto column, and the
standing line names both leaders.

**Nothing here is retyped.** Every score, rank and verdict is read from the committed
run files and recomputed. That is the failure being avoided: `bakeoff.md` retypes nine
rows a token could substitute and one of its claims went stale for eight days
(`docs/todo/2026-08-28-the-bakeoff-page-transcribes-what-a-token-could-substitute.md`).

**The bar** (`docs/goals/learned-model-family.md`): a learned detector earns its place
only by clearing the coded detectors **separably** — by a margin the fold-to-fold
variation cannot explain — and by being understood well enough that the margin is
attributable to its shape rather than to its tuning budget. The first clause is computed
here against the admissible leader. The second is a judgement and is not scored.

**Separability** uses the corrected *t* the runs record: the paired statistic over outer
folds times the Nadeau-Bengio factor for a train/test split reused across folds. A margin
counts as separable when the corrected two-sided 95 % interval excludes zero, which at
df = 3 means |t| > 3.182 — harsh for four folds, deliberately.
"""

from __future__ import annotations

import argparse
import html
import json
import sys
from dataclasses import dataclass
from statistics import mean
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
    ("gated", "with false alarms held to CoactDetect's level"),
    ("ungated", "on F1 alone"),
]

# Plain names for a person reading the page (docs/GLOSSARY.md, 2026-09-21). The code and
# the run files keep their own words — `gated`, `passes_veto`, `crowded_check.json`.
CLOSE_EVENTS = "close-events test"


def shown(key: str) -> str:
    """The name a person sees: ``cicada`` prints as locust, ``coact`` as CoactDetect.

    From ``bugarach.detectors.DISPLAY_NAMES``. The key on a page reads as the Cossart lab's
    CICADA, which locust is a modified partial port of (FOUNDATIONS §7). Falls back to the
    key where the package cannot be imported, so the page still builds.
    """
    try:
        from bugarach.detectors import display_name
    except Exception:                      # noqa: BLE001 — a page with keys beats no page
        return key
    return display_name(key)

# What each comparison variant means, in the source files' own vocabulary.
VARIANTS = {
    "as_run": "as the run scored it, the net's merge gap fixed at 2 s",
    "config_kept": "the net's merge gap tuned, its configuration kept",
    "config_rechosen": "the net's merge gap tuned and its configuration re-chosen",
}


@dataclass
class Player:
    """One detector's standing in one selection, coded or learned alike."""

    name: str
    kind: str  # "coded" or "net"
    selection: str
    f1: float
    folds: int
    veto_passed: int | None  # folds whose chosen settings survive the crowded veto
    veto_folds: int | None

    @property
    def admissible(self) -> bool:
        """Settings that survive the crowded-recording veto in every fold it was run on.

        A detector with no veto verdict is not called admissible, because the run
        never asked: the nets decoded at a fixed 2 s gap and the veto reached them
        only in the later merge-gap work.
        """
        return self.veto_folds is not None and self.veto_passed == self.veto_folds

    @property
    def veto_label(self) -> str:
        if self.veto_folds is None:
            return "not applied"
        return f"{self.veto_passed} of {self.veto_folds}"


def read_field(runs: Path) -> list[Player]:
    """Every player's mean held-out F1, from the run's own results, plus the veto."""
    results = runs / "results.json"
    if not results.exists():
        return []
    doc = json.loads(results.read_text())

    veto: dict[tuple[str, str], list[int]] = {}
    crowded = runs / "crowded_check.json"
    if crowded.exists():
        for choice in json.loads(crowded.read_text())["choices"]:
            cell = veto.setdefault((choice["detector"], choice["selection"]), [0, 0])
            cell[0] += 1 if choice["passes_veto"] else 0
            cell[1] += 1

    players: list[Player] = []
    for selection, _ in SELECTIONS:
        for name, records in doc.get("hand", {}).items():
            scores = [
                r[selection]["f1"]
                for r in records
                if r.get(selection) and r[selection].get("f1") is not None
            ]
            if not scores:
                continue
            passed, of = veto.get((name, selection), (None, None))
            players.append(
                Player(name, "coded", selection, mean(scores), len(scores), passed, of)
            )
        for name, records in doc.get("learned", {}).items():
            # A net's fold score is the mean over its training seeds.
            scores = [
                r[selection]["f1_mean"]
                for r in records
                if r.get(selection) and r[selection].get("f1_mean") is not None
            ]
            if not scores:
                continue
            players.append(
                Player(name, "net", selection, mean(scores), len(scores), None, None)
            )
    return players


def field_standing(players: list[Player]) -> str:
    """Who leads, who leads admissibly, and where the best net actually sits."""
    if not players:
        return "No committed results to rank."
    lines = []
    for selection, gloss in SELECTIONS:
        here = sorted(
            [p for p in players if p.selection == selection],
            key=lambda p: -p.f1,
        )
        if not here:
            continue
        top = here[0]
        admissible = [p for p in here if p.admissible]
        best_net = next((p for p in here if p.kind == "net"), None)
        # First letter only: str.capitalize() lowercases the rest ("coactdetect's", "f1").
        part = f"{gloss[:1].upper() + gloss[1:]}, {shown(top.name)} leads the field at {top.f1:.3f} F1"
        if admissible and admissible[0].name != top.name:
            part += (
                f", but its settings fail the {CLOSE_EVENTS}; the best admissible "
                f"detector is {shown(admissible[0].name)} at {admissible[0].f1:.3f}"
            )
        if best_net is not None:
            rank = here.index(best_net) + 1
            part += (
                f". The best net is {best_net.name}, {rank} of {len(here)}, "
                f"at {best_net.f1:.3f}"
            )
        lines.append(part + ".")
    return " ".join(lines)


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


def render(rows: list[Row], constants: dict, players: list[Player]) -> str:
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
    parts.append(f"<p class='standing'>{esc(field_standing(players))}</p>")

    # The full field first: every player the run tuned and scored, not a
    # challenger table against one champion.
    for selection, gloss in SELECTIONS:
        here = sorted(
            [p for p in players if p.selection == selection], key=lambda p: -p.f1
        )
        if not here:
            continue
        parts.append(f"<h2>The field, {esc(gloss)}</h2>")
        parts.append("<div class='scroll'><table><thead><tr>")
        parts.append(
            "<th>#</th><th>detector</th><th>kind</th>"
            f"<th class='n'>mean held-out F1</th><th class='n'>{CLOSE_EVENTS} "
            "(folds passing)</th>"
            "</tr></thead><tbody>"
        )
        for i, pl in enumerate(here, 1):
            kind = "learned" if pl.kind == "net" else "coded"
            veto_cls = (
                "v-clears"
                if pl.admissible
                else ("v-behind" if pl.veto_folds is None else "v-ahead")
            )
            parts.append(
                f"<tr><td class='note'>{i}</td>"
                f"<td>{esc(shown(pl.name))}</td>"
                f"<td class='note'>{kind}</td>"
                f"<td class='n'>{pl.f1:.4f}</td>"
                f"<td class='n {veto_cls}'>{esc(pl.veto_label)}</td></tr>"
            )
        parts.append("</tbody></table></div>")
    parts.append(
        "<p class='note'>All six coded detectors were tuned per outer fold by the "
        "every-knob search, and all four nets were trained against them. "
        "<strong>The raw leader is not the admissible leader</strong>: binned SCE tops "
        "both selections and its chosen settings fail the close-events test, "
        "because it gets there with a 30 s merge gap that fuses genuinely separate "
        "events when they come close together. The test was not applied to the nets in "
        "this run — they decoded at a fixed 2 s gap, and it reached them only in the "
        "later merge-gap work, where it refused a wider gap in all 64 choices. "
        "<em>locust</em> is this project's modified partial port of the Cossart lab's "
        "CICADA; its numbers are not measurements of CICADA.</p>"
    )

    parts.append("<h2>Against the admissible leader</h2>")
    parts.append(
        "<p class='note'>CoactDetect is the reference below because it is the "
        "highest-scoring coded detector whose settings pass the close-events test in "
        "every fold "
        "— not because the other five were set aside.</p>"
    )
    parts.append(f"<p>{esc(standing(rows))}</p>")
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
    players = read_field(args.runs)
    if not rows and not players:
        print(f"no run files under {args.runs}", file=sys.stderr)
        return 2

    page = render(rows, constants, players)

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

    print(field_standing(players))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
