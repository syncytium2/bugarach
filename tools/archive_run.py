#!/usr/bin/env python3
"""Put a finished run in Dropbox and in the repo, and record that it was done.

    python3 tools/archive_run.py ~/runs/<run> --name 2026-09-18-my-run              # Dropbox
    python3 tools/archive_run.py ~/runs/<run> --name 2026-09-18-my-run --to-repo    # and the repo
    python3 tools/archive_run.py --pending                   # finished runs not yet archived
    python3 tools/archive_run.py --selftest

WHY THIS EXISTS. The weekend of 2026-09-18 ran two nested-tuning runs, about 14 hours each,
into ``~/runs/`` on two workstations. That is the right place to *run* (FOUNDATIONS §8, and
``docs/windows_workstation_setup.md`` §8: not the repo, not Dropbox, not a scratchpad). But
nothing moved the results anywhere afterwards. Their fits and scores reached Dropbox because
a session zipped them by hand; the repo got one run's results and neither run's chosen
models. On 2026-09-21 the models were needed to run a net on real data and were found on one
disk. Tony: *"hours of compute is not backed up? ... ensure that future runs go straight to
repo and dropbox. crazy."*

TWO HALVES, BECAUSE ONLY ONE CAN HAPPEN UNATTENDED.

- **Dropbox needs no session.** The darkroom is mounted and writable at 03:00.
  ``tools/mirror_run_status.py --archive-as <name>``, which a scheduled task already runs
  every five minutes beside every long run, calls :func:`to_darkroom` once ``results.json``
  appears. So a run reaches Dropbox within minutes of finishing, with nobody present.
- **The repo needs a session.** A commit passes hooks, a board guard and a PR, so a run
  cannot commit itself (the reasoning ``mirror_run_status.py`` records). Instead the session
  briefing lists every finished run under ``~/runs`` that is not in the repo yet, with the
  command that puts it there. The next session to start on that machine is told.

WHAT GOES WHERE. Everything goes to Dropbox, under ``<darkroom>/bugarach/runs/<name>/``. The
bulk folders (``fits``, ``scores`` by default) go as ``.tar.gz`` and everything else as
files. The repo gets everything **except** the bulk folders, under
``docs/learned/runs/<name>/``. The weekend's bulk was 146 MB and 1.1 GB unpacked per run, and
this repo is public and does not use Git LFS. ``docs/learned/tuned_vs_coact/README.md`` is
the worked example.

VERIFIED, NOT ASSUMED. Every copied file is compared by SHA-256 with its source, and every
archive is reopened and its member count checked against the folder it came from. What was
done is written to ``ARCHIVED.json`` in the run folder, one entry per destination, so
"archived?" is a file anyone can read rather than something a session remembers.

STANDARD LIBRARY ONLY, loading ``paths.py`` by file, for the reason ``mirror_run_status.py``
gives: a scheduled task that needs the venv fails at the one moment it exists for.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import shutil
import socket
import sys
import tarfile
import tempfile
from datetime import datetime, timezone
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
MARKER = "ARCHIVED.json"
FINISHED = "results.json"
BULK = ("fits", "scores")
RUNS_ROOT = Path.home() / "runs"


def _load_paths():
    import importlib.util

    src = REPO / "src" / "bugarach" / "paths.py"
    spec = importlib.util.spec_from_file_location("_bugarach_paths", src)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def _now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def _sha(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as fh:
        for block in iter(lambda: fh.read(1 << 20), b""):
            h.update(block)
    return h.hexdigest()


def _plain_name(name: str) -> str:
    """A run name is one folder name: no anchor, no separator, no climb."""
    from pathlib import PurePosixPath, PureWindowsPath

    for flavour in (PurePosixPath, PureWindowsPath):
        p = flavour(name)
        if p.anchor or len(p.parts) != 1 or name in (".", ".."):
            raise ValueError(f"--name must be a single folder name, not {name!r}")
    return name


def read_marker(run_dir: Path) -> dict:
    try:
        return json.loads((run_dir / MARKER).read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return {}


def _write_marker(run_dir: Path, key: str, entry: dict) -> dict:
    m = read_marker(run_dir)
    m[key] = entry
    tmp = run_dir / (MARKER + ".tmp")
    tmp.write_text(json.dumps(m, indent=2), encoding="utf-8")
    os.replace(tmp, run_dir / MARKER)
    return m


def _files(root: Path) -> list[Path]:
    return sorted(p for p in root.rglob("*") if p.is_file())


def _copy_verified(src_root: Path, dest_root: Path, skip: tuple[str, ...]) -> int:
    """Copy every file under src_root except the top-level ``skip`` folders and the marker;
    compare each copy with its source by SHA-256. Returns the number of files."""
    n = 0
    for src in _files(src_root):
        rel = src.relative_to(src_root)
        if rel.parts[0] in skip or rel.as_posix() in (MARKER, MARKER + ".tmp"):
            continue
        dst = dest_root / rel
        dst.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(src, dst)
        if _sha(src) != _sha(dst):
            raise OSError(f"copy of {rel} does not match its source")
        n += 1
    return n


def _tar_verified(folder: Path, dest: Path) -> int:
    """``folder`` as ``dest`` (.tar.gz), written beside it and moved into place, then
    reopened and its file count checked. Returns the number of files."""
    want = len(_files(folder))
    fd, tmp = tempfile.mkstemp(dir=str(dest.parent), prefix=".archive-", suffix=".tar.gz")
    os.close(fd)
    try:
        with tarfile.open(tmp, "w:gz") as t:
            t.add(folder, arcname=folder.name)
        with tarfile.open(tmp, "r:gz") as t:
            got = sum(1 for m in t.getmembers() if m.isfile())
        if got != want:
            raise OSError(f"{dest.name}: {got} files in the archive, {want} in {folder}")
        os.replace(tmp, dest)
    except BaseException:
        Path(tmp).unlink(missing_ok=True)
        raise
    return want


def to_darkroom(run_dir: Path, name: str, *, bulk: tuple[str, ...] = BULK,
                root: Path | None = None) -> dict:
    """Everything in ``run_dir`` into ``<darkroom>/bugarach/runs/<name>/``, bulk folders packed.

    ``root`` replaces the darkroom (tests). Records the result in ``ARCHIVED.json``.
    """
    name = _plain_name(name)
    if root is None:
        paths = _load_paths()
        root = paths.darkroom("runs")
        if root is None:
            raise OSError(paths.unresolved_message("--name"))
    dest = Path(root) / name
    dest.mkdir(parents=True, exist_ok=True)
    # A scheduled task killed mid-pack (its time limit, a sign-out) leaves a temp archive
    # behind; the next attempt starts clean rather than letting them pile up in Dropbox.
    for stale in dest.glob(".archive-*.tar.gz"):
        stale.unlink(missing_ok=True)
    present = tuple(b for b in bulk if (run_dir / b).is_dir())
    n = _copy_verified(run_dir, dest, present)
    packed = {b: _tar_verified(run_dir / b, dest / f"{b}.tar.gz") for b in present}
    entry = {"path": str(dest), "at": _now(), "host": socket.gethostname(),
             "files": n, "packed": packed}
    _write_marker(run_dir, "darkroom", entry)
    return entry


def to_repo(run_dir: Path, name: str, *, bulk: tuple[str, ...] = BULK,
            dest: Path | None = None) -> dict:
    """Everything except the bulk folders into ``docs/learned/runs/<name>/`` in this repo.

    Copies only; committing is the session's, through the usual branch and PR.
    """
    name = _plain_name(name)
    dest = dest or (REPO / "docs" / "learned" / "runs" / name)
    n = _copy_verified(run_dir, dest, bulk)
    entry = {"path": str(dest), "at": _now(), "host": socket.gethostname(), "files": n,
             "left_out": [b for b in bulk if (run_dir / b).is_dir()]}
    _write_marker(run_dir, "repo", entry)
    return entry


def pending(runs_root: Path = RUNS_ROOT) -> list[tuple[Path, list[str]]]:
    """Finished runs (a ``results.json``) under ``runs_root`` missing a destination."""
    out = []
    if not runs_root.is_dir():
        return out
    for run in sorted(p for p in runs_root.iterdir() if p.is_dir()):
        if not (run / FINISHED).is_file():
            continue
        m = read_marker(run)
        missing = [k for k in ("darkroom", "repo") if k not in m]
        if missing:
            out.append((run, missing))
    return out


def _selftest() -> int:
    tmp = Path(tempfile.mkdtemp(prefix="archive-selftest-"))
    try:
        run = tmp / "runs" / "r1"
        (run / "fits" / "a").mkdir(parents=True)
        (run / "scores").mkdir()
        (run / "chosen").mkdir()
        (run / "fits" / "a" / "f1.json").write_text("{}")
        (run / "fits" / "f2.json").write_text("{}")
        (run / "scores" / "s.npz").write_bytes(b"\x00" * 64)
        (run / "chosen" / "seed0.json").write_text('{"w": 1}')
        (run / "meta.json").write_text("{}")
        assert pending(tmp / "runs") == [], "unfinished runs are not pending"
        (run / FINISHED).write_text("{}")
        assert pending(tmp / "runs") == [(run, ["darkroom", "repo"])]
        d = to_darkroom(run, "r1", root=tmp / "dark")
        assert d["packed"] == {"fits": 2, "scores": 1} and d["files"] == 3, d
        assert (tmp / "dark" / "r1" / "chosen" / "seed0.json").is_file()
        assert not (tmp / "dark" / "r1" / "fits").exists()
        assert pending(tmp / "runs") == [(run, ["repo"])]
        r = to_repo(run, "r1", dest=tmp / "repo" / "r1")
        assert r["files"] == 3 and r["left_out"] == ["fits", "scores"], r
        assert not (tmp / "repo" / "r1" / "scores").exists()
        assert pending(tmp / "runs") == []
        for bad in ("../x", "a/b", "C:\\x", "/x"):
            try:
                _plain_name(bad)
            except ValueError:
                continue
            raise AssertionError(f"{bad!r} should be refused")
        print("selftest: all checks pass")
        return 0
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("run_dir", nargs="?", type=Path)
    ap.add_argument("--name", help="the run's folder name in Dropbox and the repo, "
                                   "dated: 2026-09-18-fair-comparison")
    ap.add_argument("--to-repo", action="store_true",
                    help="also copy everything but the bulk folders into docs/learned/runs/<name>/")
    ap.add_argument("--bulk", nargs="*", default=list(BULK),
                    help="top-level folders packed for Dropbox and left out of the repo")
    ap.add_argument("--pending", action="store_true",
                    help="list finished runs under ~/runs not yet in Dropbox or the repo")
    ap.add_argument("--brief", action="store_true", help="with --pending: one line, or nothing")
    ap.add_argument("--selftest", action="store_true")
    a = ap.parse_args(argv)

    if a.selftest:
        return _selftest()
    if a.pending:
        found = pending()
        if a.brief:
            if found:
                print(f"!! {len(found)} finished run(s) in ~/runs not archived: "
                      f"python3 tools/archive_run.py --pending")
            return 0
        for run, missing in found:
            print(f"{run}  missing: {', '.join(missing)}")
        if found:
            print("archive: python3 tools/archive_run.py <run> --name <dated-name> --to-repo")
        return 0
    if a.run_dir is None or a.name is None:
        ap.error("run_dir and --name are required (or --pending / --selftest)")
    if not (a.run_dir / FINISHED).is_file():
        print(f"{a.run_dir} has no {FINISHED}: not finished, or not a run. Archiving anyway "
              f"would copy a half-written run.", file=sys.stderr)
        return 1
    bulk = tuple(a.bulk)
    d = to_darkroom(a.run_dir, a.name, bulk=bulk)
    print(f"Dropbox: {d['files']} files and {len(d['packed'])} archive(s) -> {d['path']}")
    if a.to_repo:
        r = to_repo(a.run_dir, a.name, bulk=bulk)
        print(f"repo: {r['files']} files -> {r['path']} (not committed: branch, commit, PR)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
