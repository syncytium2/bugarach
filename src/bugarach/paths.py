"""Where bugarach writes review output.

Figures, parity reports and benchmark output go to the shared **darkroom** —
`<dropbox>/darkroom/bugarach/`, the folder this project owns alongside
`constellation/` (the MATLAB producer side), `syzygy/`, and the rest. See that
folder's own `README.md` for what belongs in it.

The path is **never hardcoded**. It lives on a Dropbox mount whose absolute
path differs per machine and per OS and contains a person's name, and this repo
is public — sapper SAP004 blocks exactly that string from a tracked file. So the
location comes from the ``BUGARACH_DARKROOM`` environment variable, and when
that is unset ``darkroom()`` returns ``None`` and the caller writes nothing.

Guessing would be worse than not writing: the darkroom is visible from every
machine that mounts the Dropbox, so a wrong guess does not fail locally — it
scatters files into another project's folder. Callers should treat ``None`` as
"skip the export", not as an error worth working around::

    out = darkroom()
    if out is not None:
        fig.savefig(out / "parity_summary.png")

Because it is shared across machines, claim it on the session board
(``docs/SESSIONS.md``) before writing — see ``docs/session_protocol.md``.
"""

from __future__ import annotations

import os
from pathlib import Path

ENV_VAR = "BUGARACH_DARKROOM"


def darkroom(*parts: str, create: bool = False) -> Path | None:
    """Return the bugarach darkroom directory, or ``None`` if it is not set.

    parts: optional sub-path components joined onto the root, e.g.
    ``darkroom("parity", "2026-08-12.png")``.
    create: make the directory (the parent, when ``parts`` names a file with a
    suffix) if it does not exist. Off by default so merely asking where output
    *would* go never touches a synced folder.

    Returns ``None`` when ``BUGARACH_DARKROOM`` is unset or empty — see the
    module docstring for why that is a skip rather than a fallback.
    """
    root = os.environ.get(ENV_VAR, "").strip()
    if not root:
        return None
    path = Path(root).expanduser()
    for p in parts:
        path = path / p
    if create:
        target = path.parent if path.suffix else path
        target.mkdir(parents=True, exist_ok=True)
    return path
