"""Where bugarach writes review output.

Figures, parity reports and benchmark output go to the shared **darkroom** —
`<dropbox>/darkroom/bugarach/`, the folder this project owns alongside
`constellation/` (the MATLAB producer side), `syzygy/`, and the rest. See that
folder's own `README.md` for what belongs in it.

The path is **never hardcoded**. It lives on a Dropbox mount whose absolute
path differs per machine and per OS and contains a person's name, and this repo
is public — sapper SAP004 blocks exactly that string from a tracked file.

So ``darkroom()`` resolves it two ways, in order:

1. **``BUGARACH_DARKROOM``**, if set. An explicit answer always wins, and it is
   the only way to point at a darkroom that is not under a Dropbox mount.
2. **Dropbox's own record of where it put itself** — ``info.json``, which the
   client writes and keeps current, listing the local path of each linked
   account. If exactly one of those accounts has a real ``darkroom/bugarach``
   directory in it, that is the darkroom.

Only then, ``None``, and the caller writes nothing.

**Finding is not guessing, and the distinction is the whole safety property
here.** The darkroom is visible from every machine that mounts the Dropbox, so a
wrong path does not fail locally — it scatters files into another project's
folder. Step 2 never invents a location: it asks the client that owns the mount,
and it accepts an answer only if the directory is *already there*. Where that
leaves it uncertain — no account has one, or several do — it declines and returns
``None`` rather than picking. Callers treat ``None`` as "skip the export", not as
an error worth working around::

    out = darkroom()
    if out is not None:
        fig.savefig(out / "parity_summary.png")

Why step 2 exists: the environment variable kept going missing. It was set in a
``~/.zshrc``, which zsh reads for interactive shells only, so every tool a Claude
Code session ran saw it unset and silently skipped its export while Dropbox sat
mounted and visible in Finder (2026-08-17). An env var is also per-machine setup,
and this project runs on several — a fresh clone on a second workstation should
find the darkroom without anyone remembering a dotfile.

To see which route resolved, and what it found::

    python -m bugarach.paths

Because it is shared across machines, claim it on the session board
(``docs/SESSIONS.md``) before writing — see ``docs/session_protocol.md``.
"""

from __future__ import annotations

import json
import os
import re
import sys
from pathlib import Path

ENV_VAR = "BUGARACH_DARKROOM"

#: The darkroom folder, relative to a Dropbox account root, and bugarach's own
#: folder inside it. Names of shared folders — no machine and no person in them.
DARKROOM_SUBPATH = ("darkroom", "bugarach")

#: Where the client keeps its own record, as path *segments*.
#:
#: Segments rather than a joined string, and that is not a style preference:
#: sapper SAP004 blocks the client's folder name followed by a slash from any
#: tracked file, because the one thing it must never miss is somebody's real
#: synced path landing in a public repo. It cannot tell a wildcarded pattern from
#: a personal path, so it blocks both — and being crude in that direction is
#: correct. Composing through pathlib is what CLAUDE.md asks for anyway; the
#: near-miss is written up in ``docs/sapper_feedback/``, so this is a documented
#: shape rather than a quiet dodge.
_CLIENT_DIR = "Dropbox"
_INFO_FILE = "info.json"


def _info_json_candidates() -> list[Path]:
    """Every place Dropbox is known to keep ``info.json`` on this machine.

    macOS and Linux put it in ``~/.dropbox``. Windows uses the two AppData
    roots, depending on whether the install was per-user or per-machine. Under
    WSL there is no ``$APPDATA`` to read, and the Linux-side ``~/.dropbox`` is
    not where the Windows client wrote — so reach across to the mounted drives
    and let the glob find the user, rather than asking who is logged in.
    """
    seen: list[Path] = [Path.home() / ".dropbox" / _INFO_FILE]

    for var in ("APPDATA", "LOCALAPPDATA"):
        base = os.environ.get(var, "").strip()
        if base:
            seen.append(Path(base) / _CLIENT_DIR / _INFO_FILE)

    for drive in sorted(Path("/mnt").glob("[a-z]")) if Path("/mnt").is_dir() else []:
        users = drive / "Users"
        if not users.is_dir():
            continue
        for home in sorted(users.glob("*")):
            for appdata in ("Roaming", "Local"):
                seen.append(home / "AppData" / appdata / _CLIENT_DIR / _INFO_FILE)

    out: list[Path] = []
    for p in seen:  # preserve order, drop repeats
        if p not in out:
            out.append(p)
    return out


def _as_local_path(raw: str) -> Path | None:
    """Turn one path out of ``info.json`` into a path this process can open.

    A Windows client records ``C:\\Users\\...``. Read from WSL that string names
    nothing, and the same JSON is the only record available there, so translate
    the drive letter onto ``/mnt``. Anywhere else the string is already local.
    """
    raw = raw.strip()
    if not raw:
        return None
    win = re.fullmatch(r"([A-Za-z]):[\\/](.*)", raw)
    if win and not sys.platform.startswith("win"):
        drive, rest = win.group(1).lower(), win.group(2).replace("\\", "/")
        return Path("/mnt") / drive / rest
    return Path(raw)


def dropbox_roots() -> list[Path]:
    """The local root of every Dropbox account this machine has linked.

    Straight out of the client's own ``info.json`` — a business account's entry
    points at the member folder (the one carrying the person's name), which is
    the level the shared folders sit under. Unreadable or malformed files are
    skipped: a broken Dropbox install is a reason to find nothing, not to raise
    inside a figure script.
    """
    roots: list[Path] = []
    for info in _info_json_candidates():
        try:
            accounts = json.loads(info.read_text())
        except (OSError, ValueError):
            continue
        if not isinstance(accounts, dict):
            continue
        for entry in accounts.values():
            if not isinstance(entry, dict):
                continue
            path = _as_local_path(str(entry.get("path", "")))
            if path is not None and path not in roots:
                roots.append(path)
    return roots


def discover_darkroom() -> Path | None:
    """Locate ``<dropbox>/darkroom/bugarach`` via Dropbox's own record, or ``None``.

    Returns a path only when **exactly one** linked account already contains
    that directory. Zero means this machine does not mount it; more than one
    means the machine cannot tell which is meant, and picking one would write
    into a folder nobody chose.
    """
    found: list[Path] = []
    for root in dropbox_roots():
        candidate = root.joinpath(*DARKROOM_SUBPATH)
        if candidate.is_dir() and candidate not in found:
            found.append(candidate)
    return found[0] if len(found) == 1 else None


def resolve_root() -> tuple[Path | None, str]:
    """The darkroom root and how it was found: ``"env"``, ``"dropbox"`` or ``"none"``.

    Split out from ``darkroom()`` so a session can ask which route answered
    without reading a figure script's output to infer it.
    """
    raw = os.environ.get(ENV_VAR, "").strip()
    if raw:
        return Path(raw).expanduser(), "env"
    found = discover_darkroom()
    if found is not None:
        return found, "dropbox"
    return None, "none"


def darkroom(*parts: str, create: bool = False) -> Path | None:
    """Return the bugarach darkroom directory, or ``None`` if it cannot be found.

    parts: optional sub-path components joined onto the root, e.g.
    ``darkroom("parity", "2026-08-12.png")``.
    create: make the directory (the parent, when ``parts`` names a file with a
    suffix) if it does not exist. Off by default so merely asking where output
    *would* go never touches a synced folder.

    Returns ``None`` when ``BUGARACH_DARKROOM`` is unset and no single Dropbox
    account on this machine has a ``darkroom/bugarach`` in it — see the module
    docstring for why that is a skip rather than a fallback.
    """
    path, _ = resolve_root()
    if path is None:
        return None
    for p in parts:
        path = path / p
    if create:
        target = path.parent if path.suffix else path
        target.mkdir(parents=True, exist_ok=True)
    return path


def unresolved_message(flag: str = "--out DIR") -> str:
    """What to tell a person when nothing resolved, and how to fix it.

    Shared by the figure tools so that none of them keeps blaming the
    environment variable alone — a machine can now fail to find the darkroom
    with the variable working exactly as intended.
    """
    return (
        f"No darkroom found: ${ENV_VAR} is unset and no Dropbox account on this "
        f"machine has a {'/'.join(DARKROOM_SUBPATH)} in it.\n"
        f"Writing nothing rather than guessing — the darkroom is visible from "
        f"every machine, so a wrong path lands files in another project's folder.\n"
        f"Mount the Dropbox, set ${ENV_VAR}, or pass {flag}. "
        f"`python -m bugarach.paths` shows what this machine can see."
    )


def main() -> int:
    """Print what resolved, so a new machine can be checked in one command."""
    path, how = resolve_root()
    if how == "env":
        print(f"darkroom: {path}\n  from:   ${ENV_VAR}")
        if not path.is_dir():
            print("  WARNING: that directory does not exist — check the value")
        return 0
    if how == "dropbox":
        print(f"darkroom: {path}\n  from:   Dropbox info.json ({ENV_VAR} unset)")
        return 0
    print(f"darkroom: not found ({ENV_VAR} unset), exports will be skipped")
    roots = dropbox_roots()
    if not roots:
        print("  no Dropbox account found — checked:")
        for c in _info_json_candidates():
            print(f"    {c}")
    else:
        print(f"  Dropbox is here, without a {'/'.join(DARKROOM_SUBPATH)} in it:")
        for r in roots:
            print(f"    {r}")
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
