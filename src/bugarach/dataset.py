"""Point an analysis at a directory and have it say what it found.

**Why this exists.** Every analysis in `tools/` takes a directory, and until now each
one named it differently and meant something different by it: `assess_archive.py
--store` accepted either an export folder or a `.mat` store, `modularity_null.py
--folder` accepted only an export folder, and `synfire_scan.py --store` accepted only
an export folder while its flag said otherwise. Running the three analyses over the
same recordings meant remembering which word each tool wanted.

Worse than the naming was the failure. Handing `synfire_scan.py --store` an actual
`.mat` store — which is exactly what the flag invites — did not say "that is a store,
not an export folder". It walked in, treated `detector_settings.csv` as a table of
events, and died with::

    ValueError: detector_settings.csv must have columns 'time_sec' and 'roi'
                (found ['detector', 'stream', 'param', 'value'])

naming an internal file the caller never mentioned and a column contract they were not
thinking about. `kind()` below exists so that becomes "this is a .mat store and this
tool reads export folders", said before anything is read.

**What a dataset can be.** Two shapes, and the distinction is the producer's, not a
detail:

- an **export folder** — one CSV per recording, the contract in
  `docs/export_folder_spec.md`. Carries regions, and possibly analysis windows.
- a **`.mat` store** — the archive form, one `.mat` per recording.

Nothing here reads a dataset; it identifies one and resolves where it lives.
"""
from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path

__all__ = ["Kind", "kind", "describe", "data_root", "resolve", "require",
           "DataError", "ENV_VAR"]

ENV_VAR = "BUGARACH_DATA_ROOT"
"""Optional. Where the stores live, so a dataset can be named rather than pathed."""

#: Files an export folder may hold that are not recordings. Kept in step with
#: ``io.RESERVED``; a name here is *not* evidence of an export folder, which is the
#: mistake that produced the detector_settings.csv error above.
_NOT_A_RECORDING = {"slices.csv", "regions.csv", "detector_settings.csv",
                    "PROVENANCE.md", "README.md"}


class DataError(Exception):
    """The dataset is missing, or is not the shape the caller needs."""


@dataclass(frozen=True)
class Kind:
    name: str          # "export_folder" | "mat_store" | "empty" | "missing"
    n_recordings: int
    detail: str

    @property
    def is_export_folder(self) -> bool:
        return self.name == "export_folder"

    @property
    def is_mat_store(self) -> bool:
        return self.name == "mat_store"


def kind(path) -> Kind:
    """What sort of dataset is this directory, if any? Reads no recording.

    Counts rather than guesses: a directory holding `.mat` files is a store, one
    holding non-reserved `.csv` files is an export folder. A directory holding both is
    reported as whichever has more, with the other named in ``detail`` — that case is
    real (a store directory that also carries a settings CSV) and silently picking one
    is how the confusing error above happened.
    """
    p = Path(path)
    if not p.exists():
        return Kind("missing", 0, f"{p} does not exist")
    if not p.is_dir():
        return Kind("missing", 0, f"{p} is a file, not a dataset directory")

    # Asked of the store reader rather than globbed here: SAP007 keeps `.mat` access
    # inside `store.py`, and refusing a store is that rule's purpose rather than an
    # exception to it. See `store.store_recordings`.
    from .store import store_recordings

    mats = store_recordings(p)
    csvs = [c for c in sorted(p.glob("*.csv")) if c.name not in _NOT_A_RECORDING]

    if mats and csvs:
        if len(mats) >= len(csvs):
            return Kind("mat_store", len(mats),
                        f"{len(mats)} .mat recordings (also {len(csvs)} loose .csv)")
        return Kind("export_folder", len(csvs),
                    f"{len(csvs)} recording CSVs (also {len(mats)} .mat)")
    if mats:
        return Kind("mat_store", len(mats), f"{len(mats)} .mat recordings")
    if csvs:
        return Kind("export_folder", len(csvs), f"{len(csvs)} recording CSVs")

    reserved = [f.name for f in p.iterdir() if f.name in _NOT_A_RECORDING]
    if reserved:
        return Kind("empty", 0,
                    f"holds {', '.join(sorted(reserved))} but no recordings — an "
                    f"export folder is one CSV per recording besides those")
    return Kind("empty", 0, f"{p} holds no .mat or .csv recordings")


def describe(path) -> str:
    """One line naming what was resolved, for a tool to print before it works.

    Tools print this so a run that read the wrong data is visible in its own log
    rather than inferred afterwards from the numbers.
    """
    k = kind(path)
    return f"{Path(path).name}: {k.name.replace('_', ' ')} — {k.detail}"


def data_root() -> Path | None:
    """Where stores live: ``$BUGARACH_DATA_ROOT``, else found beside the darkroom.

    The darkroom already finds its own mount (`paths.discover_darkroom`), and the
    stores sit under the same Dropbox. Sessions have had to hunt for this by hand with
    the variable unset, which is a per-machine fact no repo document can carry.
    Returns None rather than guessing wrong.
    """
    raw = os.environ.get(ENV_VAR, "").strip()
    if raw:
        p = Path(raw).expanduser()
        return p if p.is_dir() else None

    # `dropbox_roots()` already returns the OWNER directory (…/Dropbox-<org>/<person>),
    # the same level `discover_darkroom` appends `darkroom/bugarach` to — not the mount.
    # Checking one level further down as well costs nothing and covers a layout where
    # the data sits beside a differently-named owner folder.
    from .paths import dropbox_roots

    def _looks_like_root(c: Path) -> bool:
        return (c / "processed_archive").is_dir() or (c / "exports").is_dir()

    for root in dropbox_roots():
        cand = root / "data"
        if _looks_like_root(cand):
            return cand
    for root in dropbox_roots():
        for owner in sorted(root.glob("*/data")):
            if _looks_like_root(owner):
                return owner
    return None


def resolve(spec) -> Path:
    """A path, or a name to look for under the data root. Never reads it.

    ``resolve("event_store_onset_revised_2v")`` finds it under
    ``<data root>/processed_archive/``; ``resolve("2026-08-17_revised_2v_v2")`` finds
    it under ``<data root>/exports/bugarach/``. An existing path is returned as given.
    """
    p = Path(spec).expanduser()
    if p.exists():
        return p
    if p.is_absolute() or len(p.parts) > 1:
        raise DataError(f"{p} does not exist")

    root = data_root()
    if root is None:
        raise DataError(
            f"{spec!r} is not a path, and there is nowhere to look it up: set "
            f"{ENV_VAR} to the directory holding processed_archive/ and exports/, "
            f"or pass a full path")

    for sub in ("processed_archive", "exports/bugarach", "exports", ""):
        cand = root / sub / spec if sub else root / spec
        if cand.is_dir():
            return cand

    available = []
    for sub in ("processed_archive", "exports/bugarach"):
        d = root / sub
        if d.is_dir():
            available += [f"{sub}/{c.name}" for c in sorted(d.iterdir())
                          if c.is_dir()][:8]
    hint = ("\n  available: " + ", ".join(available)) if available else ""
    raise DataError(f"no dataset named {spec!r} under {root}{hint}")


def require(spec, *, want: str, flag: str = "--dataset") -> Path:
    """Resolve, then insist it is the shape this analysis reads. Reads no recording.

    ``want`` is ``"export_folder"``, ``"mat_store"``, or ``"any"``. The error names
    what was found and what the tool needs, which is the whole point — see the module
    docstring for what the alternative looked like.
    """
    path = resolve(spec)
    k = kind(path)

    if k.name in ("missing", "empty"):
        raise DataError(f"{flag} {path}: {k.detail}")
    if want == "any" or k.name == want:
        return path

    reads = {"export_folder": "an export folder (one CSV per recording)",
             "mat_store": "a .mat store (one .mat per recording)"}
    raise DataError(
        f"{flag} {path} is a {k.name.replace('_', ' ')} ({k.detail}), but this "
        f"analysis reads {reads[want]}.")
