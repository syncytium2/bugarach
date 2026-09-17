"""Where a matplotlib figure tool writes: the darkroom by default, and a repo copy with ``--also``.

The house rule (CLAUDE.md, *Figure/report output goes to the Dropbox darkroom*): a tool that renders
something for a person to read defaults its destination to ``bugarach.paths.darkroom()`` and takes
``--also`` for the copy that review and git history need. The rigid-shift report's four figure tools
share this so the rule lives in one place.

    from figure_destination import add_arguments, save
    add_arguments(ap)                                  # --out, --also
    save(fig, "name_fig.png", a, subfolder="tube_self_supervised")
"""

from __future__ import annotations

import sys
from pathlib import Path


def add_arguments(ap) -> None:
    ap.add_argument("--out", type=Path, default=None,
                    help="destination folder (default: the darkroom)")
    ap.add_argument("--also", type=Path, default=None,
                    help="write a second copy here, e.g. the run folder in the repo")


def save(fig, name: str, args, subfolder: str, dpi: int = 150) -> list[Path]:
    """Write ``fig`` to ``--out`` (default: the darkroom's ``subfolder``) and ``--also``."""
    out = args.out
    if out is None:
        from bugarach import paths
        root = paths.darkroom(create=True)
        if root is None:
            print(paths.unresolved_message(), file=sys.stderr)
            raise SystemExit(2)
        out = root / subfolder
    written = []
    for folder in [out] + ([args.also] if args.also else []):
        folder = Path(folder)
        folder.mkdir(parents=True, exist_ok=True)
        p = folder / name
        fig.savefig(p, dpi=dpi)
        print(p)
        written.append(p)
    return written
