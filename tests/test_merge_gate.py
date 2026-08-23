"""The merge gate proves it can fire, in CI, like sapper does.

`gh pr merge --auto` only waits when a required status check exists. With no
branch protection nothing is required, so it merges instantly and the PR gates
nothing — which is what happened here for a whole session (every PR merged ~90 s
before its own CI finished). `tools/merge_when_green.sh` does the waiting and
verifying client-side instead.

The property worth testing is the counter-intuitive one: **no checks found must
be treated as failure.** An absent gate looks exactly like a passed one, so
"empty means fine" is the bug, not the fallback.

THE REAPER half of these tests is a different kind of nervous. On a green merge
the gate now removes the worktree it just merged, and a tool that deletes a
directory has to prove each of its refusals rather than assert them: standing in
the primary checkout, a detached HEAD, somebody else's PR, a branch that never
landed, an uncommitted file. `--selftest` fires all of those through the pure
`reap_verdict`; the tests below run the real `reap_worktree` against a real
scratch repo, where a real directory does and does not get deleted.

The refusal that matters most is **other-branch**. A session that merges a
colleague's PR from inside its own worktree has a worktree which is merged,
clean and idle by every fact git can see — and is not finished. Identity is
therefore checked before state, and `test_identity_is_checked_before_state` pins
that ordering, because reversing it is how this becomes the sweep's bug again.
"""

import shutil
import subprocess
from pathlib import Path

import pytest

REPO = Path(__file__).parent.parent
GATE = REPO / "tools" / "merge_when_green.sh"

pytestmark = pytest.mark.skipif(
    shutil.which("bash") is None, reason="bash unavailable (gate is a shell script)"
)


def test_gate_exists_and_is_executable():
    assert GATE.is_file(), f"{GATE} missing"


def test_decision_logic_can_fire_in_every_direction():
    """--selftest feeds the pure verdict() the JSON shapes gh actually returns:
    all-success, a failure, in-progress, queued, empty, garbage, skipped,
    cancelled, and the legacy `state` form."""
    r = subprocess.run(["bash", str(GATE), "--selftest"],
                       capture_output=True, text=True, cwd=REPO)
    assert r.returncode == 0, r.stdout + r.stderr
    assert "all checks pass" in r.stdout


def test_syntax_is_valid():
    r = subprocess.run(["bash", "-n", str(GATE)], capture_output=True, text=True)
    assert r.returncode == 0, r.stderr


def test_refuses_a_non_numeric_pr_argument():
    """Usage errors exit 2, never 0 — a gate that no-ops on bad input is the
    same failure class it exists to prevent."""
    r = subprocess.run(["bash", str(GATE), "not-a-pr"],
                       capture_output=True, text=True, cwd=REPO)
    assert r.returncode == 2, r.stdout + r.stderr


def test_grace_period_is_documented_and_parsed():
    """"No checks yet" and "no checks ever" are indistinguishable right after a
    PR opens. Refusing instantly makes the gate cry wolf in the normal case —
    and a gate that cries wolf gets bypassed. The grace window is the fix, so
    pin that it exists rather than trusting the comment."""
    src = GATE.read_text(encoding="utf-8")
    assert "--grace" in src
    assert "GRACE=" in src
    r = subprocess.run(["bash", str(GATE), "--help"], capture_output=True, text=True)
    assert "--grace" in r.stdout


def test_absence_is_still_failure_after_the_grace_window():
    """The grace period must not have turned "no checks" into a pass."""
    src = GATE.read_text(encoding="utf-8")
    none_branch = src.split("NONE)", 1)[1].split(";;", 1)[0]
    assert "exit 1" in none_branch, "no-checks must still refuse, not merge"
    assert "gh pr merge" not in none_branch


# ------------------------------------------------------------------ the reaper


def git(*args: str, cwd: Path) -> str:
    return subprocess.run(
        ["git", *args], cwd=cwd, check=True, capture_output=True, text=True
    ).stdout


def reap(cwd: Path, head: str) -> subprocess.CompletedProcess:
    """Drive the real reaper with no gh and no network: source the gate as a
    library, then call it in `cwd` as if a merge had just landed."""
    return subprocess.run(
        ["bash", "-c", f'export MERGE_WHEN_GREEN_LIB=1; . "{GATE}"; reap_worktree "{head}"'],
        cwd=cwd, capture_output=True, text=True,
    )


@pytest.fixture
def tree(tmp_path: Path):
    """An origin, a primary checkout, and a worktree on `feat` that has landed."""
    origin = tmp_path / "origin.git"
    subprocess.run(["git", "init", "-q", "--bare", "-b", "main", str(origin)], check=True)

    primary = tmp_path / "primary"
    subprocess.run(["git", "clone", "-q", str(origin), str(primary)], check=True)
    git("config", "user.email", "t@example.com", cwd=primary)
    git("config", "user.name", "t", cwd=primary)
    (primary / "seed.txt").write_text("seed\n")
    git("add", "-A", cwd=primary)
    git("commit", "-qm", "seed", cwd=primary)
    git("push", "-q", "origin", "main", cwd=primary)

    work = tmp_path / "wt-feat"
    git("worktree", "add", "-q", "-b", "feat", str(work), "main", cwd=primary)
    return primary, work


def test_the_reaper_removes_the_worktree_whose_pr_just_merged(tree):
    """The whole point: merged, clean, yours, and you are standing in it."""
    primary, work = tree
    r = reap(work, "feat")
    assert r.returncode == 0, r.stdout + r.stderr
    assert not work.exists(), r.stdout + r.stderr
    assert "reaped wt-feat" in r.stdout, r.stdout
    assert "feat" not in git("branch", "--format=%(refname:short)", cwd=primary).split()


def test_the_reaper_tells_you_your_shell_is_now_nowhere(tree):
    """It deleted the directory the caller is standing in. Saying so is the
    difference between a tidy tool and a confusing one."""
    _, work = tree
    out = reap(work, "feat").stdout
    assert "DELETED DIRECTORY" in out, out
    assert "cd " in out, out


def test_the_reaper_refuses_an_uncommitted_file(tree):
    _, work = tree
    (work / "scratch.txt").write_text("in progress\n")
    r = reap(work, "feat")
    assert work.exists()
    assert "worktree kept" in r.stdout and "uncommitted" in r.stdout, r.stdout


def test_the_reaper_refuses_somebody_elses_pr(tree):
    """You merged a colleague's PR from your own worktree. Yours is merged,
    clean and idle by every fact git has, and it is not finished."""
    _, work = tree
    r = reap(work, "their-branch")
    assert work.exists()
    assert "you are on 'feat'" in r.stdout, r.stdout


def test_identity_is_checked_before_state(tree):
    """Dirty AND somebody else's: it must say whose branch it is, not merely
    that the tree is dirty. Reporting only the state is how the worktree sweep
    let a live directory read as an abandoned one."""
    _, work = tree
    (work / "scratch.txt").write_text("in progress\n")
    r = reap(work, "their-branch")
    assert "you are on 'feat'" in r.stdout, r.stdout


def test_the_reaper_refuses_a_branch_that_never_landed(tree):
    """`git merge-base --is-ancestor` is the only proof the merge reached here.
    A gh call that said "merged" is not one — this is the same repo where an
    unverified green light merged 90 s before CI finished."""
    primary, work = tree
    (work / "new.txt").write_text("x\n")
    git("add", "-A", cwd=work)
    git("commit", "-qm", "ahead", cwd=work)
    r = reap(work, "feat")
    assert work.exists()
    assert "not on origin/main" in r.stdout, r.stdout


def test_the_reaper_never_removes_the_primary_checkout(tree):
    """And says nothing while declining — a line on every merge from the primary
    is noise, and noise is what gets tools muted."""
    primary, _ = tree
    r = reap(primary, "main")
    assert primary.exists()
    assert r.returncode == 0
    assert r.stdout.strip() == "", r.stdout


def test_a_refusal_is_never_a_failure(tree):
    """The script's promise is the merge. A worktree it declined to remove must
    not look like a merge that did not happen."""
    _, work = tree
    (work / "scratch.txt").write_text("x\n")
    assert reap(work, "feat").returncode == 0


def test_the_reaper_counts_the_ignored_files_it_destroys(tree):
    """`git worktree remove` deletes ignored files and `git status --porcelain`
    cannot see them, so no dirty-check could have caught them. Here that is the
    built `site/` — regenerable, but reported rather than discovered.

    The build cache alongside it is counted, not named: the first live run listed
    eight `__pycache__/` entries in full, which made the one line whose job is
    "did that just delete something you wanted?" the one nobody finishes."""
    primary, work = tree
    (work / ".gitignore").write_text("/site/\n__pycache__/\n")
    git("add", "-A", cwd=work)
    git("commit", "-qm", "ignore site", cwd=work)
    git("push", "-q", "origin", "feat:main", cwd=work)
    (work / "site").mkdir()
    (work / "site" / "bundle.js").write_text("// built\n")
    (work / "__pycache__").mkdir()
    (work / "__pycache__" / "x.pyc").write_text("")
    r = reap(work, "feat")
    assert not work.exists(), r.stdout + r.stderr
    assert "2 ignored path(s) went with it: site/, 1 cache dir" in r.stdout, r.stdout


def test_every_refusal_the_reaper_can_make_is_fired_by_selftest():
    r = subprocess.run(["bash", str(GATE), "--selftest"],
                       capture_output=True, text=True, cwd=REPO)
    assert r.returncode == 0, r.stdout + r.stderr
    for case in ("mine, merged, clean", "the primary is never reaped",
                 "detached HEAD", "PR head unknown", "somebody else's PR",
                 "merge did not land here", "uncommitted work"):
        assert case in r.stdout, f"{case} not fired\n{r.stdout}"


def test_the_opt_out_is_documented_in_help():
    """A flag that does not appear in --help is an absent gate by another route,
    which is the bug this whole script exists to prevent. The header outgrew a
    hardcoded `sed 2,30p` once already."""
    out = subprocess.run(["bash", str(GATE), "--help"],
                         capture_output=True, text=True).stdout
    assert "--no-reap" in out, out
    assert "--grace" in out, out
