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
           "current", "current_name", "declared_exports",
           "DataError", "ENV_VAR", "POINTER"]

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


# ---------------------------------------------------------------------------
# WHICH folder — as against `resolve()`, which answers WHERE a named one lives.
#
# These two questions kept getting confused, and only one of them had an answer.
# `resolve("2026-08-18_revised_2v_periods")` has always worked; what no session
# could do was find out that this was the name to pass. See `current_export.toml`
# for the four disagreeing places the answer used to be scattered across, and for
# Tony's instruction that produced this: "claude.md is unreliable. help me fix
# this permanently." Prose in CLAUDE.md is not a mechanism. A function is.
# ---------------------------------------------------------------------------

POINTER = "current_export.toml"
"""The single declaration of which export folder is the input. Repo root."""


def _pointer_path() -> Path:
    """The pointer file, found from this module rather than the working directory.

    Walking up from ``__file__`` and not from ``cwd``: a tool run from a worktree
    subdirectory, or from the darkroom, still gets its own repo's answer. An
    installed (non-editable) copy has no repo above it, which is why the caller
    gets ``DataError`` naming the file rather than a stack trace.
    """
    for parent in Path(__file__).resolve().parents:
        cand = parent / POINTER
        if cand.is_file():
            return cand
    raise DataError(
        f"{POINTER} not found above {__file__}. It declares which export folder is "
        f"the input and lives at the repo root; without it there is no default and "
        f"a caller must name a folder explicitly.")


def declared_exports() -> dict[str, dict]:
    """Every export folder the repo declares, by role. Reads no recording.

    Roles are the table names in ``current_export.toml`` — ``default`` and ``pensub``
    today. Each maps to that table, so a caller can report ``recordings`` and ``note``
    alongside the name it used.
    """
    import tomllib

    path = _pointer_path()
    try:
        with path.open("rb") as fh:
            doc = tomllib.load(fh)
    except tomllib.TOMLDecodeError as exc:      # a typo here breaks every analysis
        raise DataError(f"{path} is not valid TOML: {exc}") from exc

    roles = {k: v for k, v in doc.items() if isinstance(v, dict) and "name" in v}
    if not roles:
        raise DataError(
            f"{path} declares no export folder. It needs at least a [default] table "
            f"with a `name` key naming a folder under <data root>/exports/bugarach/.")
    return roles


def current_name(role: str = "default") -> str:
    """The NAME of the current export folder. Does not touch the filesystem.

    Separate from ``current()`` on purpose: an error message, a log line or a hook
    can say which folder is meant on a machine where the data is not mounted at all.
    """
    roles = declared_exports()
    try:
        return str(roles[role]["name"])
    except KeyError:
        raise DataError(
            f"no export role {role!r} in {_pointer_path()}; declared: "
            f"{', '.join(sorted(roles))}") from None


def current(role: str = "default") -> Path:
    """The current export folder, resolved on this machine.

    The one call an analysis should make when it has no reason to read anything
    else::

        folder = dataset.current()            # the standard export
        folder = dataset.current("pensub")    # the crosstalk control's pair

    Raises ``DataError`` — never returns a store, never guesses a folder — if the
    declared name is not under the data root on this machine.
    """
    name = current_name(role)
    try:
        path = resolve(name)
    except DataError as exc:
        raise DataError(
            f"{_pointer_path().name} declares the {role} export as {name!r}, but it "
            f"is not on this machine: {exc}") from None

    k = kind(path)
    if not k.is_export_folder:
        # The pointer naming something that is not a folder is a repo-level mistake,
        # not a caller's. Say which file to fix rather than what shape was found.
        raise DataError(
            f"{_pointer_path()} declares the {role} export as {name!r}, but "
            f"{path} is a {k.name.replace('_', ' ')} ({k.detail}). The pointer names "
            f"export folders only; stores are not inputs.")
    return path


#: The stream a HEADLESS analysis uses when neither a caller nor a person named one.
#:
#: **This does not privilege a stream in the sense FOUNDATIONS §3 refuses to.**
#: §3 is right that streams are generic, that ``Slice.streams`` takes any count
#: and any names, and that most outside labs have one. This is the **tie-break
#: for the case §3 leaves open** — a recording carrying more than one, where a
#: script has to pick and something has to be written down. Tony, 2026-08-27:
#: *"fast and slow are two utterly different data streams. both are interesting,
#: but fast is closer to classical calcium events. for now, stick with fast."*
#: And on why there was no default at all: *"this is intended as a general
#: project. we might be the only ones with two streams. its fine to default to
#: fast."*
#:
#: **The viewer does not use this as an answer, it uses it as an opening
#: position.** Where there is a person, the person picks: ``ui/app.py`` shows a
#: stream control, and this only decides which entry it opens on.
DEFAULT_STREAM = "fast"


def preferred_stream(names) -> str:
    """Which stream to analyse, given the names a recording actually carries.

    The rule, in order:

    1. **One stream — use it**, whatever it is named. The common case outside
       this lab (FOUNDATIONS §3); no convention of ours should touch it.
    2. **:data:`DEFAULT_STREAM` present — use it.** The tie-break above.
    3. **Otherwise the first**, which is what the tree already did.

    It lives *here*, beside :func:`current`, because it is the same kind of
    question — *which data* — and because nothing declared it, so consumers had
    drifted: ``assess_folder`` silently took ``names[0]`` while ``detect_folder``
    ran every stream. A question with no answer in the tree gets a different
    answer from each caller. That is what ``current_export.toml`` fixed for
    *which folder*, and it is fixed the same way here: **a function that returns
    the answer, not a paragraph that describes it.**

    Deliberately **not** in ``store.py``. Stream choice is an analysis
    convention, not a property of the store reader, and putting it there made
    every caller import the module the folder-is-the-input hook watches — which
    is how a helper about *convention* starts tripping a gate about *provenance*.
    That happened once while this was being written.

    Raises ``ValueError`` on an empty list rather than returning ``None``: a
    recording with no streams is a defect the caller must report, and handing
    back a name that indexes nothing moves the failure somewhere less legible.
    """
    names = list(names)
    if not names:
        raise ValueError("no streams to choose from")
    if len(names) == 1:
        return names[0]
    return DEFAULT_STREAM if DEFAULT_STREAM in names else names[0]


def main() -> int:
    """Print what resolved, so a machine can be checked in one command.

    The counterpart to ``python -m bugarach.paths``, and it exists for the same
    reason: the session briefing names this command when the declared export does
    not resolve, and a pointer to a probe that does not exist is worse than none.

    Every declared role is printed, not just ``default`` — the failure this answers
    is "which folder, and is it here?", and a session running it has usually just
    been told that one of them is missing.
    """
    try:
        roles = declared_exports()
    except DataError as exc:
        print(exc)
        return 1

    root = data_root()
    print(f"data root: {root if root else f'not found (${ENV_VAR} unset, no Dropbox)'}")
    print(f"declared in {POINTER}:")

    bad = 0
    for role in sorted(roles):
        name = roles[role]["name"]
        try:
            path = current(role)
        except DataError as exc:
            bad = 1
            print(f"  {role:8} {name}\n           !! {exc}")
            continue
        print(f"  {role:8} {name}\n           -> {path}  ({describe(path)})")
    return bad


if __name__ == "__main__":
    raise SystemExit(main())
