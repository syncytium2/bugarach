#!/usr/bin/env python3
"""Build the field-size proposal page: inline the figures, write it where it is read.

    python tools/build_net_design_page.py [--out DIR] [--also DIR]

The prose lives in `docs/proposals/2026-09-16-nine-cells-to-a-thousand.src.html` so it is
reviewable in a diff. The figures are **inlined, not linked** — the page has to survive
being opened from a folder, mailed, or published as a standalone artifact, and a linked
SVG survives none of those. The two data figures are regenerated from
`docs/learned/field_size.json` on every build, so a number cannot go stale in the page
while the probe says something else.

Destination defaults to the darkroom and takes `--also` for the repo copy (sapper SAP006):
the repo copy is what review and git history need, the darkroom copy is what a person opens.
"""
from __future__ import annotations

import argparse
import subprocess
import sys
import tempfile
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
SRC = REPO / "docs/proposals/2026-09-16-nine-cells-to-a-thousand.src.html"
PAGE = "2026-09-16-nine-cells-to-a-thousand.html"

FIGS = {"FIG1": "field_size_fig1.svg",
        "FIG2": "field_size_fig2.svg",
        "FIG3": "net_fig3_tube.svg",
        "FIG4": "net_fig4_chorus.svg",
        "FIG5": "net_fig5_gauge.svg",
        "FIG6": "net_fig6_quorum.svg",
        "FIG7": "net_fig7_axes.svg"}


def build() -> str:
    """Regenerate every figure into a scratch directory, then substitute."""
    with tempfile.TemporaryDirectory() as tmp:
        for tool in ("make_field_size_figures.py", "make_net_diagrams.py"):
            subprocess.run([sys.executable, str(REPO / "tools" / tool), "--out", tmp],
                           check=True, stdout=subprocess.DEVNULL)
        html = SRC.read_text()
        for token, name in FIGS.items():
            marker = f"<!--{token}-->"
            if marker not in html:
                raise SystemExit(f"{SRC.name}: no placeholder for {token}")
            html = html.replace(marker, (Path(tmp) / name).read_text().strip())
    return html


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--out", default=None, help="where the page goes (default: darkroom)")
    ap.add_argument("--also", default=None, help="a second copy, usually the repo")
    ap.add_argument("--check", action="store_true",
                    help="rebuild and compare against the repo copy; a stale page is a "
                         "build failure, not a warning")
    args = ap.parse_args()

    html = build()
    repo_copy = REPO / "docs/proposals" / PAGE
    if args.check:
        if not repo_copy.exists():
            print(f"{repo_copy} does not exist", file=sys.stderr)
            return 1
        if repo_copy.read_text() != html:
            print(f"{repo_copy} is stale — rebuild it", file=sys.stderr)
            return 1
        print(f"{repo_copy} is current")
        return 0

    out_dir = args.out
    if out_dir is None:
        try:
            from bugarach.paths import darkroom
            out_dir = str(darkroom())
        except Exception:                                   # pragma: no cover
            out_dir = str(REPO / "docs" / "proposals")
    for d in [out_dir] + ([args.also] if args.also else []):
        Path(d).mkdir(parents=True, exist_ok=True)
        target = Path(d) / PAGE
        target.write_text(html)
        print(target)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
