#!/usr/bin/env python3
"""Build the learned-detector review page into a single self-contained file.

    python tools/build_learned_report.py

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
import re
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent.parent / "docs" / "learned"
SRC = HERE / "report.src.html"
OUT = HERE / "report.html"
ARCH = HERE / "architecture.svg"


def main() -> int:
    if not SRC.exists():
        print(f"missing {SRC}", file=sys.stderr)
        return 1
    html = SRC.read_text()

    missing: list[str] = []

    def fig(m):
        stem = m.group(1)
        png = HERE / f"{stem}.png"
        if not png.exists():
            missing.append(png.name)
            return ""
        b64 = base64.b64encode(png.read_bytes()).decode("ascii")
        return f"data:image/png;base64,{b64}"

    html = re.sub(r"\{\{FIG:([A-Za-z0-9_]+)\}\}", fig, html)

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

    OUT.write_text(html)
    kb = len(html.encode()) / 1024
    print(f"wrote {OUT}  ({kb:.0f} KB, self-contained)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
