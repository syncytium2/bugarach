"""What produced a run — one answer, in one place, for every artifact here.

**Why this module exists.** On 2026-08-29 Tony asked what generated
``docs/learned/bakeoff.json`` and the honest answer was "the file cannot say".
The prose in ``docs/learned/bakeoff.md`` says it well — which store, which
stream, which K, which four tools in which order — but the artifact carried
``platform`` and ``python`` and nothing else, so a reader holding only the JSON
could not tell whether it came from the current library or one from three weeks
ago. A number whose origin lives only in a document beside it is one rename away
from being unattributable.

**And there were three different answers to "what version" already.**
``detect_folder`` had a ``_code_version()`` returning a **git sha**;
``ui/app.py`` had a ``_code_version()`` — same name, same package — returning an
**installed package version**; the browser page wrote a hardcoded ``null``; and
``fair_bakeoff`` wrote no version at all. Four call sites, four meanings, one
name. This module is the single answer, and the two local copies are gone.

**The distinction that matters, and why both fields exist.** A package version
says *which release*; a commit says *which tree*. They answer different questions
and neither substitutes for the other: this project is normally run from a git
checkout at a version that has not been bumped in weeks, so the package version
alone would report the same string for every run in that period. ``dirty`` is the
third field and the load-bearing one — a commit sha with uncommitted changes on
top of it names a tree that does not exist anywhere, which a reader must be told
rather than left to assume.

Everything is optional and every field can be ``None``. An installed wheel has no
git; a source tree may have no package metadata; a browser has neither. Reporting
``None`` is the honest answer and is not an error — what this module refuses to do
is guess.
"""

from __future__ import annotations

import platform
import subprocess
from pathlib import Path

__all__ = ["code_version", "git_commit", "git_dirty", "package_version", "stamp"]

_REPO = Path(__file__).resolve().parent


def package_version() -> str | None:
    """The installed distribution version, or ``None`` in an uninstalled tree."""
    from importlib.metadata import PackageNotFoundError, version

    try:
        return version("bugarach")
    except PackageNotFoundError:      # pragma: no cover - depends on install mode
        return None


def _git(*args: str) -> str | None:
    """Run a git command in this package's directory; ``None`` if git cannot answer.

    Every failure mode collapses to ``None`` on purpose — no git binary, not a
    checkout, a timeout, a repository owned by another user. A provenance helper
    that raises would take down the run whose provenance it was describing, which
    is exactly backwards.
    """
    try:
        out = subprocess.run(["git", *args], cwd=_REPO,
                             capture_output=True, text=True, timeout=5)
    except (OSError, subprocess.SubprocessError):      # pragma: no cover - env
        return None
    if out.returncode != 0:
        return None
    return out.stdout.strip() or None


def git_commit() -> str | None:
    """The commit this tree is at, or ``None`` outside a checkout."""
    return _git("rev-parse", "HEAD")


def git_dirty() -> bool | None:
    """Are there uncommitted changes? ``None`` when git cannot say.

    ``None`` and ``False`` are different answers and must not be collapsed:
    ``False`` means *checked, and the tree is clean*; ``None`` means *nobody
    could check*. Only the first licenses trusting the commit above.
    """
    out = _git("status", "--porcelain")
    if out is None:
        return None
    return bool(out)


def code_version() -> str | None:
    """One human-readable string naming the code, for ``run.json``'s scalar field.

    Shaped so the interesting part is never silently absent: ``0.1.0+g4e19ac0``,
    ``0.1.0+g4e19ac0.dirty``, ``g4e19ac0`` with no package metadata, ``0.1.0``
    outside a checkout, or ``None`` when neither is available.

    This is the value that goes in ``run.json``'s **existing** ``code_version``
    key, which is output contract read by other teams — so it stays a string.
    The structured form is :func:`stamp`, which lands beside it under a new key.
    """
    pkg, commit, dirty = package_version(), git_commit(), git_dirty()
    short = commit[:7] if commit else None
    if pkg and short:
        return f"{pkg}+g{short}" + (".dirty" if dirty else "")
    if short:
        return f"g{short}" + (".dirty" if dirty else "")
    return pkg


def stamp(**extra: object) -> dict:
    """The full provenance block: what code, on what machine, plus what a caller adds.

    ``extra`` is where a caller puts the identity of the thing it just ran — the
    operating points a bench swept, the architectures a training pass registered,
    the spec a generator was built from. Those are the caller's to know; this
    function will not go looking for them, because a helper that guessed at a
    bench's parameters would be inventing provenance rather than recording it.
    """
    doc: dict = {
        "bugarach_version": package_version(),
        "git_commit": git_commit(),
        "git_dirty": git_dirty(),
        "code_version": code_version(),
        "python": platform.python_version(),
        "platform": platform.platform(),
    }
    doc.update(extra)
    return doc
