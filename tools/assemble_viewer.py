#!/usr/bin/env python3
"""Assemble docs/site/raster_viewer.html from the template and the detector folder.

    python tools/assemble_viewer.py            # write the page
    python tools/assemble_viewer.py --check    # fail if the page is not what this writes

**A detector is a file.** ``docs/site/detectors/<key>.js`` holds one detector's
descriptor and its algorithm; deleting the file removes the detector, its
controls and its code together. That is the whole point (ADR-0005), and it is
what "added and removed at will" has to mean if it is to mean anything.

**Why assembly happens here and not in the browser.** The page must stay one
self-contained file making zero requests: that is what lets a lab open it from
``file://`` without asking anyone, and what guarantees no recording leaves the
machine. ``build_site.py``'s ``NETWORK`` guard enforces it by refusing
``<script src``, ``import(`` and ``fetch(``. So the folder is a *source* layout
and the single file is the artifact.

**The assembled page is committed.** Rejected the tidier alternative — generate
it and gitignore it — because the page is what an outside lab actually runs, and
``git diff`` on it is how three separate sessions caught each other's mistakes in
this file on 2026-08-29 alone. Committing it keeps that review surface; ``--check``
keeps it from drifting from its sources. Same generate-commit-verify shape the
viewer's own version stamp already uses.

**The failure this invites, named so it is not a surprise:** somebody hand-edits
``raster_viewer.html`` and the next build silently discards it. ``--check`` in CI
turns that into a red build instead, and the marker region says so in the page.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SITE = ROOT / "docs" / "site"
TEMPLATE = SITE / "viewer.template.html"
PAGE = SITE / "raster_viewer.html"
DETECTORS = SITE / "detectors"

OPEN = "/* <<<ASSEMBLED DETECTORS>>> —"
CLOSE = "/* <<<END ASSEMBLED DETECTORS>>> */\n"


def detector_files() -> list[Path]:
    """Every object file, in sorted order.

    Sorted rather than declared-order on purpose: the page must be reproducible
    from the folder alone, so the order cannot live anywhere else. A detector's
    position in the picker is the picker's business, not the filesystem's.
    """
    return sorted(p for p in DETECTORS.glob("*.js") if not p.name.startswith("_"))


def assemble() -> str:
    template = TEMPLATE.read_text(encoding="utf-8")
    start = template.index(OPEN)
    end = template.index(CLOSE, start) + len(CLOSE)
    head, tail = template[:start], template[end:]

    parts = [template[start:template.index("*/\n", start) + len("*/\n")]]
    for p in detector_files():
        parts.append("\n" + p.read_text(encoding="utf-8").rstrip("\n") + "\n")
    parts.append(CLOSE)
    return head + "".join(parts) + tail


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--check", action="store_true",
                    help="exit 1 if raster_viewer.html differs from the assembly")
    a = ap.parse_args(argv)

    built = assemble()
    if a.check:
        current = PAGE.read_text(encoding="utf-8")
        if current == built:
            print("assemble_viewer: raster_viewer.html matches its sources")
            return 0
        print("assemble_viewer: raster_viewer.html is NOT what the sources assemble to.\n"
              "  Either a detector file changed and the page was not rebuilt, or the\n"
              "  page was hand-edited between the markers. Edit docs/site/detectors/*.js\n"
              "  or docs/site/viewer.template.html, then run:\n"
              "      python tools/assemble_viewer.py",
              file=sys.stderr)
        return 1

    PAGE.write_text(built, encoding="utf-8")
    names = ", ".join(p.stem for p in detector_files())
    print(f"assemble_viewer: wrote {PAGE.relative_to(ROOT)} "
          f"({len(built.splitlines())} lines) with [{names}]")
    return 0


if __name__ == "__main__":       # pragma: no cover
    raise SystemExit(main())
