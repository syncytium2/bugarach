"""The census is the outside number, so it has to be right on a machine that has one
and quiet on a machine that does not.

Both SessionStart hooks budget themselves, and until 2026-08-25 both budgets were
guessed from two remembered incidents. The comment justifying them said the exact
threshold "is not observable from inside a session" — true, and read by everyone as
not observable. It is observable from outside one: refusing an oversized payload is
what writes it to disk. tools/hook_spill_census.sh reads that record.

CI has no such record and never will, which is the point — a test that needed one
would just be the circular test again with more steps. So the parser is proved on a
synthetic tree, and the calibration test in test_session_briefing.py skips where
there is nothing to calibrate against.
"""

import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SCRIPT = ROOT / "tools" / "hook_spill_census.sh"


def _run(*args, timeout=180):
    return subprocess.run(["bash", str(SCRIPT), *args], cwd=ROOT,
                          capture_output=True, text=True, timeout=timeout)


def test_the_selftest_passes():
    """sapper-style: every branch of the parser driven over a synthetic tree,
    including the one that made the first hand-run of these numbers wrong."""
    out = _run("--selftest")
    assert out.returncode == 0, out.stdout + out.stderr
    assert "all checks pass" in out.stdout


def test_a_spilled_payload_is_not_counted_as_a_delivery():
    """The mistake worth a regression test. A refused payload can still reach a
    transcript later — a session reads the spill file back, as one did on
    2026-08-25 — so its canary looks exactly like a delivery unless it is
    subtracted. Without the subtraction the census reports a 10,492B "delivery"
    that never happened, and the threshold it derives is inverted.

    The subtraction uses comm, which compares as STRINGS. Feeding it numerically
    sorted input is the same bug wearing a different hat, and it is what the first
    run of this tool actually did.
    """
    out = _run("--selftest")
    assert "the refused one is subtracted" in out.stdout
    assert "FAIL" not in out.stdout, out.stdout


def test_it_runs_clean_on_this_machine():
    """Whatever the record here holds, the tool must not fail on it."""
    for args in (("--values",), ()):
        out = _run(*args)
        assert out.returncode == 0, out.stderr


def test_it_prints_no_absolute_paths():
    """This repo is public and sapper SAP004 blocks personal absolute paths. The
    census reads under $HOME and must print only sizes and counts — a project
    directory name carries a person's home path into anything that quotes it."""
    out = _run()
    assert "/Users/" not in out.stdout
    assert "/home/" not in out.stdout
    assert str(Path.home()) not in out.stdout


def test_check_refuses_a_budget_at_the_observed_floor():
    """--check is what makes the number binding rather than decorative."""
    vals = dict(ln.split("=", 1) for ln in _run("--values").stdout.splitlines() if "=" in ln)
    floor = vals.get("spilled_min")
    if not floor:
        return  # nothing refused on this machine; --selftest covers the logic
    assert _run("--check", floor).returncode == 1
    assert _run("--check", "1").returncode == 0
