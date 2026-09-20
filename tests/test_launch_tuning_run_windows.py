"""The launcher lost a comma-separated list, and the run died in argparse at 23:59.

`--detectors coact,loco,sce` is one argument to a human and to argparse. It is four
to cmd, which treats a comma as an argument separator — so the old launcher, which
rebuilt the tail with SHIFT one `%1` at a time, handed the script

    --detectors coact loco sce

and argparse refused the run before a single file was written. Both workstations hit
it on 2026-09-18, on the night of goal 2's fair comparison, and both worked around it
with a machine-local wrapper that quoted the list — so the defect stayed in the repo
and the workaround stayed on two disks. `HANDOFF-workstation-tuning.md` filed it as
owed once the run's worktree could change again.

The fix is to stop rebuilding the tail: `%*` is the command line as typed, separators
intact, and the run name is removed from the front of it.

Two tests, deliberately of different kinds. The behavioural one runs the launcher and
reads what it would have executed, which is the only way to prove cmd's parsing — and
it can only run on Windows, so CI (ubuntu) skips it and the workstations do not. The
static one encodes the same requirement in a form every leg can check: the tail comes
from `%*` and is not reassembled token by token. Without the second, the leg that
actually runs this suite would be the one that never tests it.
"""

import os
import re
import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent
SCRIPT = ROOT / "tools" / "launch_tuning_run_windows.cmd"


def source() -> str:
    return SCRIPT.read_text(encoding="utf-8", errors="replace")


def test_the_launcher_exists():
    assert SCRIPT.is_file(), f"{SCRIPT} is the documented launch path for unattended runs"


# --------------------------------------------------------------------------------------
# Static: readable on every platform, including the CI legs that cannot run cmd.
# --------------------------------------------------------------------------------------


def test_the_argument_tail_is_taken_from_the_raw_command_line():
    """`%*` keeps the separators as typed; rebuilding from `%1` does not."""
    text = source()
    assert "%*" in text, (
        "the tail must come from %*, the command line as typed — a comma inside an "
        "argument survives there and does not survive being reassembled"
    )


def test_the_tail_is_not_rebuilt_token_by_token():
    """The defect itself: a SHIFT/collect loop that concatenates `%1` at a time.

    This is what split `coact,loco,sce` into three arguments. Guard the shape rather
    than the label, so renaming the loop does not reopen it.
    """
    text = source()
    concatenating = re.search(r'set\s+"?ARGS=%ARGS%\s*%[1-9~]', text, re.IGNORECASE)
    assert concatenating is None, (
        "the argument tail is being reassembled one token at a time again — this is the "
        "2026-09-18 defect, and cmd has already split the commas by the time the loop runs"
    )


def test_the_run_name_is_checked_for_a_space():
    """The tail is found by locating the name in `%*`, so a name with a space cannot work.

    It has to be refused with a message; silently mis-splitting the tail is how the
    original defect behaved, and that is the behaviour being retired.
    """
    text = source()
    assert re.search(r"findstr\s+/c:\"\s\"", text), (
        "a run name containing a space must be refused, not silently mis-split"
    )


def test_the_dry_run_is_documented_in_the_header():
    """A check before scheduling is the point: the failure fired at 23:59, unattended."""
    text = source()
    head = text[: text.index("setlocal")]
    assert "BUGARACH_LAUNCH_DRYRUN" in head, (
        "the dry run has to be discoverable from the top of the file, where someone "
        "registering a scheduled task will read it"
    )


# --------------------------------------------------------------------------------------
# Behavioural: proves cmd's actual parsing. Windows only, so CI skips it by design.
# --------------------------------------------------------------------------------------

windows_only = pytest.mark.skipif(
    sys.platform != "win32",
    reason="cmd.exe parsing can only be exercised on Windows (CI runs ubuntu; the "
    "workstations run this leg)",
)


def dry_run(*args: str) -> subprocess.CompletedProcess:
    env = dict(os.environ, BUGARACH_LAUNCH_DRYRUN="1")
    return subprocess.run(
        [os.environ.get("COMSPEC", "cmd.exe"), "/c", str(SCRIPT), *args],
        capture_output=True,
        text=True,
        env=env,
        timeout=60,
    )


@windows_only
def test_an_unquoted_comma_list_arrives_as_one_argument():
    """The exact shape that failed on 2026-09-18."""
    done = dry_run("probe-run", "--detectors", "coact,loco,sce", "--device", "cuda")
    assert done.returncode == 0, done.stderr
    assert "--detectors coact,loco,sce" in done.stdout, (
        f"the comma list did not survive cmd's argument splitting: {done.stdout!r}"
    )


@windows_only
def test_a_quoted_comma_list_also_survives():
    """The workaround both machines used must keep working.

    A value carrying a space is quoted on the way to cmd, so this exercises the
    quoted form — the shape the machine-local wrappers passed — rather than the
    bare one already covered above.
    """
    done = dry_run("probe-run", "--detectors", "coact, loco")
    assert done.returncode == 0, done.stderr
    assert '--detectors "coact, loco"' in done.stdout, done.stdout


@windows_only
def test_a_path_with_spaces_survives():
    """The darkroom path contains spaces; splitting it would be the same defect."""
    done = dry_run("probe-run", "--darkroom", "C:\\path with spaces")
    assert done.returncode == 0, done.stderr
    assert '--darkroom "C:\\path with spaces"' in done.stdout, done.stdout


@windows_only
def test_the_run_name_reaches_the_out_folder():
    done = dry_run("probe-run", "--jobs", "12")
    assert done.returncode == 0, done.stderr
    assert re.search(r'--out "[^"]*[\\/]runs[\\/]probe-run"', done.stdout), done.stdout


@windows_only
def test_no_tool_arguments_is_allowed():
    """A resume with no extra arguments is a real invocation; it must not trail junk."""
    done = dry_run("probe-run")
    assert done.returncode == 0, done.stderr
    assert done.stdout.rstrip().endswith('runs\\probe-run"'), done.stdout


@windows_only
def test_a_name_with_a_space_is_refused():
    done = dry_run("bad name", "--jobs", "1")
    assert done.returncode == 2, done.stdout
    assert "may not contain a space" in done.stdout


@windows_only
def test_no_arguments_prints_usage():
    done = dry_run()
    assert done.returncode == 2
    assert "usage:" in done.stdout


@windows_only
def test_the_dry_run_starts_nothing_and_writes_nothing():
    """It prints a command; it must not create the run folder or the log."""
    done = dry_run("probe-run-never-created", "--jobs", "1")
    assert done.returncode == 0, done.stderr
    runs = Path(os.environ["USERPROFILE"]) / "runs"
    assert not (runs / "probe-run-never-created").exists()
    assert not (runs / "probe-run-never-created.log").exists()
