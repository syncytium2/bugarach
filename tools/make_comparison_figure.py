#!/usr/bin/env python3
"""The fair comparison's four architectures on one page, at ONE scale.

    python tools/make_comparison_figure.py            # -> <darkroom>/bugarach/<dated folder>/
    python tools/make_comparison_figure.py --out /tmp/cmp

**Why a page and not four figures.** WSMIP064 and WSMIP065 each write a report on
goal 2's fair comparison, and both briefs asked for a figure of "what the four
architectures do differently". Tony, 2026-09-19: *"They should definitely use
draughtsman otherwise they'll likely be completely incomparable."* Four figures
made separately are incomparable in exactly the way that matters: each is scaled to
its own box, so a mark in one is not the size of a mark in the next, and a row of
four boxes cannot be told from a row of two.

**What "one scale" means here.** Every panel is a committed draughtsman figure from
`docs/learned/comparison/`, drawn and checked by `make_architecture_diagram.py` and
held to the model by `tests/test_architecture_diagram_is_current.py`. This tool
never re-draws them. It nests each at its own viewBox extent, so a figure unit is
the same length in every panel, and it REFUSES a set whose specs disagree about
what a unit is worth — a different `output.width` or `min_type` — because the page
would then be one scale in its markup and several in fact. At the comparison slot
(912px, 9.5px floor) one figure unit is one CSS pixel, so the page is also true to
the slot every spec was checked against.

**How to read it.** Every figure breaks its rows at the same places (`layout.breaks`
in each spec): the first row is the stages that still hold one row per ROI, the
second starts where that axis collapses, the third is the head. So the first row's
length is the comparison, and a glyph is drawn only where the ROI axis is in the
tensor.

**The composite is also committed**, at `docs/learned/comparison/comparison.svg`
(`--commit` rewrites it), because WSMIP064's report ships in the public repo, where
a darkroom file cannot be embedded. It is a function of the four committed panels,
and `tests/test_comparison_figure.py` recomposes and byte-compares it, so a panel
that moves without it turns the suite red.

The single-panel copies written beside the page carry the same one-to-one size, for
a report that embeds them one at a time; the files in `docs/learned/comparison/`
are each stretched to the full slot, which is right for one figure alone and wrong
for two side by side.
"""

from __future__ import annotations

import argparse
import datetime as dt
import html
import json
import re
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT / "tools"))

from make_architecture_diagram import COMPARED, COMPARISON  # noqa: E402

#: The composite in the repo, for pages that cannot reach the darkroom.
COMMITTED = COMPARISON / "comparison.svg"
#: The darkroom folder this page is claimed under on docs/SESSIONS.md.
SUBFOLDER = "2026-09-19-comparison-architectures"
PAD, GAP = 16.0, 40.0
TITLE = "Four architectures, one scale"
SUBTITLE = ("The fair comparison's models, each drawn by draughtsman from the registered "
            "model. The first row of each is the stages that still hold one row per ROI.")
FONT = "system-ui, -apple-system, 'Segoe UI', Helvetica, Arial, sans-serif"

_ROOT_SVG = re.compile(r"<svg\b[^>]*>")
_VIEWBOX = re.compile(r'viewBox="0 0 ([\d.]+) ([\d.]+)"')
_SIZE = re.compile(r'\s(width|height)="[^"]*"')


class Panel:
    def __init__(self, arch: str):
        self.arch = arch
        self.svg = (COMPARISON / f"{arch}.svg").read_text(encoding="utf-8")
        spec = json.loads((COMPARISON / f"{arch}.spec.json").read_text(encoding="utf-8"))
        self.output = spec.get("output") or {}
        head = _ROOT_SVG.search(self.svg)
        box = _VIEWBOX.search(head.group(0)) if head else None
        if not box:
            raise SystemExit(f"{arch}: the committed figure has no viewBox to place")
        self.w, self.h = float(box.group(1)), float(box.group(2))

    def at(self, x: float, y: float) -> str:
        """This panel as a nested <svg> at its own extent: one unit, one unit."""
        head = _ROOT_SVG.search(self.svg).group(0)
        new = _SIZE.sub("", head).replace(
            "<svg", f'<svg x="{x:.2f}" y="{y:.2f}" width="{self.w:.2f}" '
                    f'height="{self.h:.2f}"', 1)
        body = self.svg.replace(head, new, 1)
        # One document, four panels, and each panel defines its own arrowhead as
        # `ds-arrow`: prefix every id so a panel's arrows use its own markers.
        for ident in set(re.findall(r'\sid="([^"]+)"', body)):
            body = (body.replace(f'id="{ident}"', f'id="{self.arch}-{ident}"')
                        .replace(f"url(#{ident})", f"url(#{self.arch}-{ident})")
                        .replace(f'href="#{ident}"', f'href="#{self.arch}-{ident}"'))
        return re.sub(r"<\?xml[^>]*\?>\s*", "", body)

    def alone(self) -> str:
        """The single-panel copy, sized one unit to one pixel."""
        head = _ROOT_SVG.search(self.svg).group(0)
        new = _SIZE.sub("", head).replace(
            "<svg", f'<svg width="{self.w:.2f}px" height="{self.h:.2f}px"', 1)
        return self.svg.replace(head, new, 1)


def one_scale(panels: list[Panel]) -> None:
    """Refuse a set whose specs disagree about what a figure unit is worth."""
    seen = {(p.output.get("width"), p.output.get("min_type")) for p in panels}
    if len(seen) != 1 or None in next(iter(seen)):
        raise SystemExit(
            "make_comparison_figure: the four specs do not state one output.width "
            f"and min_type between them ({sorted(map(str, seen))}). One page at one "
            "scale needs one slot; fix the specs rather than scaling the panels.")


def compose(panels: list[Panel]) -> str:
    # No outer margin: every panel carries its own, and the widest panel already
    # fills the slot its spec was checked against.
    width = max(p.w for p in panels)
    y = PAD + 22.0
    parts = [
        f'<text x="{PAD}" y="{y:.2f}" style="font: 600 17px {FONT}; fill:#1b1b19">'
        f"{html.escape(TITLE)}</text>",
        f'<text x="{PAD}" y="{y + 20:.2f}" style="font: 11.5px {FONT}; fill:#6b6b66">'
        f"{html.escape(SUBTITLE)}</text>",
    ]
    y += 20 + GAP / 2
    for i, p in enumerate(panels):
        if i:
            parts.append(f'<line x1="{PAD}" x2="{width - PAD:.2f}" y1="{y - GAP / 2:.2f}" '
                         f'y2="{y - GAP / 2:.2f}" style="stroke:#d8d8d4; stroke-width:1"/>')
        parts.append(p.at(0.0, y))
        y += p.h + GAP
    height = y - GAP + PAD
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {width:.2f} {height:.2f}" '
            f'width="{width:.2f}px" height="{height:.2f}px">\n'
            f'<rect width="100%" height="100%" style="fill:#ffffff"/>\n'
            + "\n".join(parts) + "\n</svg>\n")


PAGE = """<!doctype html>
<html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{title}</title>
<style>
  body {{ margin: 0; background: #fafaf8; color: #1b1b19;
         font: 16px/1.6 {font}; }}
  .wrap {{ max-width: 960px; margin: 0 auto; padding: 2.5rem 1.5rem 4rem; }}
  h1 {{ font-size: 1.6rem; margin: 0 0 .6rem; }}
  p {{ max-width: 70ch; margin: 0 0 1rem; }}
  figure {{ margin: 2rem 0 0; }}
  figure svg {{ display: block; max-width: 100%; height: auto; }}
  code {{ font-size: .9em; }}
  .muted {{ color: #6b6b66; font-size: .9rem; }}
</style></head>
<body><div class="wrap">
<h1>{title}</h1>
<p>The four architectures in goal 2's fair comparison, drawn by draughtsman from a
trace of each registered model and placed at one scale: a mark, a box and a line of
type are the same size in every panel.</p>
<p><b>How to read it.</b> Signal runs left to right. Every figure breaks its rows at
the same places: the first row is the stages that still hold <i>one row per ROI</i>,
the second starts where that axis collapses, the third is the head. So the length of
the first row is the comparison, and a column of marks is drawn only where the ROI
axis is still in the tensor.</p>
<figure>{svg}</figure>
<p class="muted">Specs: <code>docs/learned/comparison/</code> on bugarach branch
<code>draw-the-comparison-four</code>. Built by <code>tools/make_comparison_figure.py</code>
from the committed figures, which <code>tools/make_architecture_diagram.py</code>
checks for coverage before drawing. Written {when}.</p>
</div></body></html>
"""


def write(out: Path, panels: list[Panel]) -> list[Path]:
    out.mkdir(parents=True, exist_ok=True)
    svg = compose(panels)
    written = [out / "comparison.svg", out / "index.html"]
    written[0].write_text(svg, encoding="utf-8")
    written[1].write_text(PAGE.format(
        title=TITLE, font=FONT, svg=svg,
        when=dt.date.today().isoformat()), encoding="utf-8")
    for p in panels:
        f = out / f"{p.arch}.svg"
        f.write_text(p.alone(), encoding="utf-8")
        written.append(f)
    # PNGs for a report that cannot take SVG. Optional: rsvg-convert is a system
    # binary, and the SVGs are the deliverable.
    if shutil.which("rsvg-convert"):
        for f in [x for x in written if x.suffix == ".svg"]:
            png = f.with_suffix(".png")
            subprocess.run(["rsvg-convert", "-z", "2", "-b", "white", str(f), "-o",
                            str(png)], check=True)
            written.append(png)
    return written


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--out", type=Path, default=None,
                    help=f"destination folder (default: <darkroom>/{SUBFOLDER})")
    ap.add_argument("--also", type=Path, default=None,
                    help="write a second copy here")
    ap.add_argument("--commit", action="store_true",
                    help=f"only rewrite the committed composite, {COMMITTED.relative_to(ROOT)}")
    a = ap.parse_args(argv)
    panels = [Panel(arch) for arch in COMPARED]
    one_scale(panels)
    if a.commit:
        COMMITTED.write_text(compose(panels), encoding="utf-8")
        print(COMMITTED)
        return 0
    out = a.out
    if out is None:
        from bugarach import paths
        root = paths.darkroom(create=True)
        if root is None:
            print(paths.unresolved_message(), file=sys.stderr)
            return 2
        out = root / SUBFOLDER
    for folder in [out] + ([a.also] if a.also else []):
        for f in write(Path(folder), panels):
            print(f)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
