"""check_quotes wired into the normal suite.

The interesting test is the last one. A check built to stop a specific incident
should be shown firing on **that incident**, not on a fixture its own author
wrote — and this one needed that: the first version was tuned against the tree as
it stands, which no longer contains the quotes, and it did not fire on the real
file at all. Fixtures agreed with it, because I wrote them to.
"""

import subprocess
import sys
from pathlib import Path

REPO = Path(__file__).parent.parent
CHECK = REPO / "tools" / "check_quotes.py"

# The commit that removed Kreuz's words from the April todo (#451). Its parent is
# the tree as it stood publicly for nine days. The repo does not rewrite history
# (CLAUDE.md, Git conduct), so this reference is stable.
REDACTION = "14650a2"
LEAKED = "docs/todo/2026-08-24-kreuz-answered-the-spike-synch-questions-in-april.md"


def _run(*args):
    return subprocess.run([sys.executable, str(CHECK), *args],
                          capture_output=True, text=True, cwd=REPO)


def test_the_check_can_fire_and_can_stay_silent():
    r = _run("--selftest")
    assert r.returncode == 0, r.stdout + r.stderr


def test_the_tracked_tree_carries_nobodys_private_words():
    r = _run("--all")
    assert r.returncode == 0, r.stdout + r.stderr


def test_it_fires_on_the_file_that_actually_leaked():
    """Replay the April todo as it was published, and require a finding.

    This is the only test here that could have prevented anything. If a future
    change to WINDOW, MARKER or the Tony exemption quietly stops catching the
    real case, this goes red — which is the failure mode that already happened
    once, silently, in the first draft of the check.
    """
    sys.path.insert(0, str(REPO / "tools"))
    import check_quotes  # noqa: E402

    blob = subprocess.run(["git", "show", f"{REDACTION}^:{LEAKED}"],
                          capture_output=True, text=True, cwd=REPO)
    assert blob.returncode == 0, (
        f"cannot read {LEAKED} at {REDACTION}^ — has history moved? " + blob.stderr)

    # Under a neutral path: the real path is in RULE_DOCS, because the file whose
    # subject is the incident has to be able to describe it.
    hits = check_quotes.findings_for("docs/todo/replayed.md", blob.stdout)
    assert hits, (
        "check_quotes did not fire on the April todo as published on 2026-08-24. "
        "That file carried four verbatim block quotes from a private letter for "
        "nine days in a public repository, and catching it is the entire reason "
        "this check exists.")
