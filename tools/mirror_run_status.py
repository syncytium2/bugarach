#!/usr/bin/env python3
# instrument: retrieval
"""Copy an unattended run's status file into the darkroom, so it is readable from
somewhere other than the machine it runs on.

WHY THIS EXISTS. On 2026-09-16 a nested-tuning run was launched detached on a
workstation, estimated to finish a day and a half later. It wrote `progress.json`
into `~/runs/`, rewritten atomically after every fit — durable, and durable on
exactly one machine. The session that launched it was archived at 01:56, and the
next morning nobody could say whether the run was alive: the answer existed, on a
disk no one present could reach, and the person asking was on a phone.

The design that put it there was not careless. It rejected `/tmp` (cleared when the
distribution restarts) and session scratchpads (they belong to the session that made
one), each with its reason. It never asked *durable and legible from where*.

TWO CHANNELS EXISTED AND NEITHER WAS USED, and the choice between them is not taste.
**git cannot do this job**: the run commits nothing, because commits pass hooks and a
board guard and those need a session, and at 02:00 there is no session. **The darkroom
can**: it is mounted on every machine, it syncs, and it was already configured on that
workstation so the run's *figures* could reach Tony. The channel for the pictures was
set up and the channel for "is it still running" was not.

WHAT MAKES THIS ANSWER THE QUESTION rather than merely move a file. A copied
`progress.json` cannot tell a finished run from a stalled one — a run that died at
03:00 leaves a file that reads perfectly well. So each copy is stamped: when it was
taken, how old the source already was, and which host it came from. `STATUS.txt` puts
the same thing in one line, because the reader is on a phone.

RUN IT FROM A SCHEDULER, NOT AS A DAEMON. One-shot is the default and the recommended
form: a scheduled task has no process to lose, and the failure this tool exists to fix
was itself a lost process. `--watch` is for starting it beside a run by hand.

    python3 tools/mirror_run_status.py ~/runs/my-run --into 2026-09-18-my-run
    python3 tools/mirror_run_status.py ~/runs/my-run --into 2026-09-18-my-run --watch 60
    python3 tools/mirror_run_status.py --selftest

A GENERAL COPY LIVES IN ARMORY (`tools/mirror_run_status.py`, syncytium2/armory#18),
resolving the darkroom through that repo's estate-wide resolver and taking the status
file's name as an argument. Neither vendors from the other yet, so **a fix here does not
reach that one** — say which you changed.

ON WINDOWS, AS PROVEN ON WSMIP065 (2026-09-18). A Task Scheduler task, one-shot every
5 minutes, headless, logging beside the run; the exact PowerShell is in
`docs/windows_workstation_setup.md`, section 8. What that proof settled:

* **Run it from a checkout.** This file loads `src/bugarach/paths.py` relative to
  itself, so a copy standing alone finds no resolver. It needs no venv.
* **Name the interpreter by absolute path** (WSMIP065 used uv's managed Python). The
  `python3` on PATH may be the Windows Store alias, which is not what a task should
  depend on.
* **`BUGARACH_DARKROOM` was not needed.** It is unset for the user and the machine, and
  the task still resolved the darkroom through Dropbox's `info.json`. Where no Dropbox is
  found, set it durably — `[Environment]::SetEnvironmentVariable('BUGARACH_DARKROOM',
  <path>, 'User')` — never `$env:` in a shell, which a task does not inherit; the tool
  then exits 2.
* **Prove a tick by its output, not by `Get-ScheduledTaskInfo`.** Its `LastRunTime`
  trailed a manual run by about three minutes; the log line and `STATUS.txt`'s own
  stamp were immediate.
* **The task's logon is interactive**, like the tuning launcher's: signed out, both stop.
  `STATUS.txt`'s stamp then goes old, which is itself the signal.

The destination is always inside bugarach's own darkroom folder — `darkroom(*parts)`
joins onto it — and a subfolder that tries to climb out is refused. bugarach owns
`<darkroom>/bugarach/` and nothing above it.
"""
from __future__ import annotations

import argparse
import json
import os
import socket
import sys
import tempfile
import time
from datetime import datetime, timezone
from pathlib import Path

# LOADED BY PATH, NOT BY `import bugarach.paths`, AND THAT IS THE POINT.
# `paths.py` is pure stdlib, but `bugarach/__init__.py` eagerly imports the store,
# which imports scipy — so the package form makes this tool need the venv. A status
# mirror that needs the venv is one that fails at 03:00 on a scheduled task, which is
# the single moment it exists for. This keeps one source of truth for where the
# darkroom is, and no dependency beyond the standard library.
def _load_paths():
    import importlib.util

    src = Path(__file__).resolve().parents[1] / "src" / "bugarach" / "paths.py"
    spec = importlib.util.spec_from_file_location("_bugarach_paths", src)
    if spec is None or spec.loader is None:  # pragma: no cover
        raise ImportError(f"cannot load {src}")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


_paths = _load_paths()
darkroom, unresolved_message = _paths.darkroom, _paths.unresolved_message

STATUS_NAME = "progress.json"
MIRROR_NAME = "mirror.json"
HUMAN_NAME = "STATUS.txt"


def _subfolder(name: str) -> str:
    """Refuse anything that is not a plain folder name under the darkroom.

    Judged under BOTH path flavours, not the local one. On Windows ``/tmp/x`` is
    not ``is_absolute()`` — it has a root but no drive — yet joining it onto the
    darkroom discards the darkroom and lands on ``C:\\tmp\\x``. The first version
    asked the local ``Path`` and let exactly that through on WSMIP065 (2026-09-18);
    its own selftest caught it. Anything with an anchor (drive or root) in either
    flavour, or a ``..`` in either, is refused.
    """
    from pathlib import PurePosixPath, PureWindowsPath

    for flavour in (PurePosixPath, PureWindowsPath):
        p = flavour(name)
        if p.anchor or ".." in p.parts:
            raise ValueError(
                f"--into must be a folder inside the darkroom, not {name!r}. "
                "bugarach owns <darkroom>/bugarach/ and nothing above it."
            )
    return name


def _atomic_write(dest: Path, data: bytes) -> None:
    """Write through a temp file in the same directory, so a reader mid-sync
    never sees half a file."""
    dest.parent.mkdir(parents=True, exist_ok=True)
    fd, tmp = tempfile.mkstemp(dir=str(dest.parent), prefix=".mirror-")
    try:
        with os.fdopen(fd, "wb") as fh:
            fh.write(data)
        os.replace(tmp, dest)
    except BaseException:
        Path(tmp).unlink(missing_ok=True)
        raise


def mirror_once(run_dir: Path, dest_dir: Path, extra: list[str] | None = None) -> dict:
    """Copy the status file (and any --also files) into dest_dir, stamped.

    Returns the mirror record. A missing source is reported, never fatal: a run
    that has not started yet has not failed.
    """
    now = datetime.now(timezone.utc)
    src = run_dir / STATUS_NAME
    record: dict = {
        "copied_at": now.isoformat(timespec="seconds"),
        "host": socket.gethostname(),
        "run_dir": str(run_dir),
        "source_present": src.is_file(),
    }

    if src.is_file():
        raw = src.read_bytes()
        mtime = src.stat().st_mtime
        record["source_mtime"] = datetime.fromtimestamp(
            mtime, timezone.utc
        ).isoformat(timespec="seconds")
        record["source_age_sec"] = round(now.timestamp() - mtime, 1)
        _atomic_write(dest_dir / STATUS_NAME, raw)
    else:
        record["source_age_sec"] = None

    copied = []
    for name in extra or []:
        f = run_dir / name
        if f.is_file():
            _atomic_write(dest_dir / f.name, f.read_bytes())
            copied.append(f.name)
    record["also_copied"] = copied

    _atomic_write(dest_dir / MIRROR_NAME, json.dumps(record, indent=2).encode())
    _atomic_write(dest_dir / HUMAN_NAME, _human_line(record).encode())
    return record


def _human_line(record: dict) -> str:
    """One line, for a reader on a phone. Age is the point: a status file alone
    cannot tell a finished run from a stalled one."""
    when = record["copied_at"]
    host = record["host"]
    if not record["source_present"]:
        return (
            f"{when}  {host}\n"
            f"NO {STATUS_NAME} in {record['run_dir']} — the run has not written one yet,\n"
            f"or it never started. This mirror is working; the run may not be.\n"
        )
    age = record["source_age_sec"]
    stale = "  ⚠ STALE — the run may have stopped" if age is not None and age > 900 else ""
    return (
        f"{when}  {host}\n"
        f"{STATUS_NAME} was {age} seconds old when copied.{stale}\n"
        f"Source: {record['run_dir']}\n"
    )


def _selftest() -> int:
    """Prove each branch, against real files in a temp directory.

    It asserts behaviour rather than the presence of a string: a run directory is
    built, mirrored, mutated and mirrored again, and the copied bytes and the
    recorded age are checked each time.
    """
    import shutil

    tmp = Path(tempfile.mkdtemp(prefix="mirror-selftest-"))
    try:
        run, dest = tmp / "run", tmp / "dark" / "sub"
        run.mkdir(parents=True)

        # 1. No status file yet: reported, not fatal, and the human line says so.
        rec = mirror_once(run, dest)
        assert rec["source_present"] is False, rec
        assert not (dest / STATUS_NAME).exists()
        assert "has not written one yet" in (dest / HUMAN_NAME).read_text()

        # 2. With a status file: bytes copied verbatim, age recorded.
        (run / STATUS_NAME).write_text('{"stage": "rounds done", "done": 7}')
        rec = mirror_once(run, dest)
        assert rec["source_present"] is True, rec
        assert (dest / STATUS_NAME).read_text() == '{"stage": "rounds done", "done": 7}'
        assert rec["source_age_sec"] is not None and rec["source_age_sec"] >= 0, rec

        # 3. A later write is picked up; the mirror record follows it.
        (run / STATUS_NAME).write_text('{"stage": "finished", "done": 42}')
        rec = mirror_once(run, dest)
        assert json.loads((dest / STATUS_NAME).read_text())["done"] == 42
        assert json.loads((dest / MIRROR_NAME).read_text())["copied_at"] == rec["copied_at"]

        # 4. --also copies named neighbours and records which.
        (run / "run.log").write_text("line\n")
        rec = mirror_once(run, dest, extra=["run.log", "absent.log"])
        assert rec["also_copied"] == ["run.log"], rec
        assert (dest / "run.log").read_text() == "line\n"

        # 5. An old source is called stale in the human line.
        old = time.time() - 3600
        os.utime(run / STATUS_NAME, (old, old))
        mirror_once(run, dest)
        assert "STALE" in (dest / HUMAN_NAME).read_text()

        # 6. A subfolder that climbs out of the darkroom is refused — including the
        #    Windows shapes, on every OS: rooted without a drive, drive-relative,
        #    drive-absolute, and a backslash climb.
        for bad in ("../elsewhere", "/tmp/elsewhere", "\\elsewhere", "C:elsewhere",
                    "C:\\elsewhere", "..\\elsewhere", "run/../../elsewhere"):
            try:
                _subfolder(bad)
            except ValueError:
                pass
            else:  # pragma: no cover - the assert is the test
                raise AssertionError(f"{bad!r} should have been refused")
        for good in ("2026-09-18-my-run", "2026-09-18-my-run/sub"):
            assert _subfolder(good) == good, good

        print("selftest: 6 checks, 0 failures")
        return 0
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


def _archive_if_finished(run_dir: Path, name: str, ar=None) -> None:
    """Hand a finished run to ``tools/archive_run.py``, loaded by path (standard library
    only, like this tool). Once: ``ARCHIVED.json`` records it, and a recorded Dropbox
    archive is not redone every five minutes. ``ar`` replaces the module (tests)."""
    if ar is None:
        import importlib.util

        src = Path(__file__).resolve().parent / "archive_run.py"
        spec = importlib.util.spec_from_file_location("_archive_run", src)
        ar = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(ar)
    if not (run_dir / ar.FINISHED).is_file() or "darkroom" in ar.read_marker(run_dir):
        return
    entry = ar.to_darkroom(run_dir, name)
    print(f"archived to Dropbox: {entry['path']}")


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("run_dir", nargs="?", type=Path, help="the run's output directory")
    ap.add_argument("--into", help="folder name inside the darkroom to write into")
    ap.add_argument("--also", nargs="*", default=[],
                    help="further files in run_dir to copy, e.g. run.log")
    ap.add_argument("--watch", type=int, metavar="SECONDS",
                    help="loop instead of copying once; prefer a scheduled task")
    ap.add_argument("--archive-as", metavar="NAME",
                    help="once the run writes results.json, archive the whole run to "
                         "<darkroom>/bugarach/runs/NAME/ (tools/archive_run.py), once. "
                         "Tony, 2026-09-21: finished runs go straight to Dropbox")
    ap.add_argument("--selftest", action="store_true")
    args = ap.parse_args(argv)

    if args.selftest:
        return _selftest()
    if args.run_dir is None or args.into is None:
        ap.error("run_dir and --into are required (or use --selftest)")

    dest_root = darkroom(_subfolder(args.into))
    if dest_root is None:
        print(unresolved_message("--into"), file=sys.stderr)
        return 2

    while True:
        try:
            rec = mirror_once(args.run_dir, dest_root, extra=args.also)
            age = rec["source_age_sec"]
            print(f"mirrored to {dest_root}  source age: "
                  f"{'absent' if age is None else str(age) + ' s'}")
            if args.archive_as:
                _archive_if_finished(args.run_dir, args.archive_as)
        except OSError as exc:
            # The mount can go away while Dropbox restarts. A watcher that dies
            # then is worse than one that says so and tries again.
            print(f"mirror failed, will retry: {exc}", file=sys.stderr)
            if not args.watch:
                return 1
        if not args.watch:
            return 0
        time.sleep(args.watch)


if __name__ == "__main__":
    raise SystemExit(main())
