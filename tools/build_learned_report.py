#!/usr/bin/env python3
"""Build the learned-detector review page into a single self-contained file.

    python tools/build_learned_report.py                    # the review page
    python tools/build_learned_report.py docs/learned/x.src.html

Inlines every figure as a data URI and the architecture diagram as literal SVG,
because the page is published where external requests are blocked — and because a
report whose figures live somewhere else is a report that will one day render
without them.

**The built file is the deliverable.** `report.src.html` is the source; edits go
there and this is re-run. Reviewing the source instead of the output is how a
deck once shipped one build behind its own fix.
"""

from __future__ import annotations

import base64
import json
import re
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent.parent / "docs" / "learned"
SRC = HERE / "report.src.html"
OUT = HERE / "report.html"
ARCH = HERE / "architecture.svg"

# Any {{SVG:name}} resolves to docs/learned/<name>.svg, inlined literally. The
# original page had one diagram and named it {{ARCH_SVG}}; a second page needed
# three, and three more tokens would have been three more special cases.
SVG_TOKEN = "{{SVG:%s}}"
DATA = {
    "r": HERE / "learned_results.json",
    "s": HERE / "regime_shift.json",
    # The bake-off that superseded this page. The banner quotes it, and a
    # superseding notice carrying its own stale transcription of the newer
    # result would be the exact failure this substitution exists to stop.
    "b": HERE / "bakeoff.json",
    # The transfer test. Its numbers were typed into the prose of a first draft;
    # six of them were right and that was luck, not a process.
    "g": HERE / "regime_shift_fitted.json",
    # The fitted kernel parameters, read off a trained model by
    # make_architecture_figures.py. The page quotes them; nothing is retyped.
    "a": HERE / "architecture_fitted.json",
    # The scoring-tolerance sweep. The landscape page argues from its shape, and
    # a page arguing that a transcribed number drifts must not transcribe one.
    "t": HERE / "tolerance_sweep.json",
}


def _lookup(store: dict, path: str):
    """Walk a dotted path into the cached results.

    Some keys are themselves decimals — `by_frac` is keyed by participation
    fraction, so `by_frac.0.1` means the key ``"0.1"``, not a key ``"0"`` holding
    a key ``"1"``. When a bare part does not resolve, greedily rejoin it with the
    parts after it until something does.
    """
    parts = path.split(".")
    node, i = store, 0
    while i < len(parts):
        if isinstance(node, list):
            node = node[int(parts[i])]
            i += 1
            continue
        for j in range(len(parts), i, -1):
            key = ".".join(parts[i:j])
            if key in node:
                node, i = node[key], j
                break
        else:
            raise KeyError(parts[i])
    return node


def main(argv=None) -> int:
    argv = list(sys.argv[1:] if argv is None else argv)
    src, out = SRC, OUT
    if argv:                       # build_learned_report.py <src.html> [out.html]
        src = Path(argv[0]).resolve()
        out = Path(argv[1]).resolve() if len(argv) > 1 else src.with_name(
            src.name.replace(".src.html", ".html"))
    if not src.exists():
        print(f"missing {src}", file=sys.stderr)
        return 1
    html = src.read_text()

    missing: list[str] = []

    # --- {{N:r:six.rate.f1|.2f}} — every quoted number, resolved from the cache
    #
    # Not a convenience. A murderboard on 2026-08-16 found the page quoting one
    # regime's F1 beside another's under a footnote naming a third, `trace` at
    # 0.21 in a table and 0.15 three paragraphs later, and a training time that
    # appeared in no artifact at all. Each of those is a hand-transcribed number
    # drifting from the run that produced it — the failure
    # `docs/todo/2026-08-14-generator-doc-numbers-are-transcribed.md` already
    # describes for `generator.md`. A number typed into prose cannot be checked
    # by anything; a number resolved at build time cannot disagree with its
    # source, and a stale path fails the build instead of shipping.
    stores = {}
    for key, path in DATA.items():
        if path.exists():
            stores[key] = json.loads(path.read_text())

    bad: list[str] = []

    def num(m):
        store, path, fmt = m.group(1), m.group(2), m.group(3) or ""
        if store not in stores:
            bad.append(f"{path} (no {DATA[store].name})")
            return "?"
        try:
            v = _lookup(stores[store], path)
        except (KeyError, IndexError, TypeError, ValueError):
            bad.append(path)
            return "?"
        return format(v, fmt) if fmt else str(v)

    html = re.sub(r"\{\{N:([rsbgat]):([A-Za-z0-9_.\-]+)(?:\|([^}]+))?\}\}", num, html)
    if bad:
        print("UNRESOLVED DATA PATHS: " + ", ".join(bad), file=sys.stderr)
        return 1

    def fig(m):
        stem = m.group(1)
        png = HERE / f"{stem}.png"
        if not png.exists():
            missing.append(png.name)
            return ""
        b64 = base64.b64encode(png.read_bytes()).decode("ascii")
        return f"data:image/png;base64,{b64}"

    html = re.sub(r"\{\{FIG:([A-Za-z0-9_]+)\}\}", fig, html)

    def svg(m):
        path = HERE / f"{m.group(1)}.svg"
        if not path.exists():
            missing.append(path.name)
            return ""
        # strip the XML prolog if one appears — invalid mid-document
        return re.sub(r"^<\?xml[^>]*\?>\s*", "", path.read_text())

    html = re.sub(r"\{\{SVG:([A-Za-z0-9_]+)\}\}", svg, html)

    def css(m):
        """One stylesheet, inlined. Two pages sharing a look by copy-and-paste
        is two looks with a delay."""
        path = HERE / f"{m.group(1)}.css"
        if not path.exists():
            missing.append(path.name)
            return ""
        return path.read_text()

    html = re.sub(r"\{\{CSS:([A-Za-z0-9_]+)\}\}", css, html)

    if "{{ARCH_SVG}}" in html:
        if not ARCH.exists():
            missing.append(ARCH.name)
        else:
            svg = ARCH.read_text()
            # strip the XML prolog if one ever appears — it is invalid mid-document
            svg = re.sub(r"^<\?xml[^>]*\?>\s*", "", svg)
            html = html.replace("{{ARCH_SVG}}", svg)

    if missing:
        print("MISSING INPUTS: " + ", ".join(missing), file=sys.stderr)
        print("run tools/make_learned_figures.py first", file=sys.stderr)
        return 1

    left = re.findall(r"\{\{[^}]+\}\}", html)
    if left:
        print(f"unresolved tokens: {left}", file=sys.stderr)
        return 1

    # A real document head. Without these four lines the page shipped in quirks
    # mode with no viewport, so on a phone the browser laid it out at 980 px and
    # scaled the result down — every responsive rule the stylesheet already
    # carries (the clamped h1, the auto-fit verdict grid, the scrollable tables)
    # was written and never got to run.
    out.write_text(
        '<!doctype html>\n<html lang="en">\n<head>\n'
        '<meta charset="utf-8">\n'
        '<meta name="viewport" content="width=device-width, initial-scale=1">\n'
        f"{html}\n</html>\n")
    kb = out.stat().st_size / 1024
    print(f"wrote {out}  ({kb:.0f} KB, self-contained)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
