"""The session board has to reach a session, and for a while it did not.

On 2026-08-20 the vendored session-start hook emitted 60,235 bytes across 868
lines — 835 of them the machine-local board, `cat`-ed whole. The harness will not
inject a hook that size: it wrote the output to a file and gave the session a 2KB
preview instead. `--- session board:` is at line 32. The preview ends at line 26.

So the board reached nobody, and it also evicted the worktree list, the MATLAB
report and the unpushed-work alarm that share the stream. A board of 52 blocks of
which 8 were live cost the whole briefing and delivered none of itself.

These are the sapper-style proofs that the trim can fire: that the live blocks
survive, that the dead ones do not, that `Touches:` — the field that would have
caught all three of that day's collisions, none of which shared a branch name —
travels with them, and that a filter which cannot find its markers says so loudly
instead of passing an empty briefing off as a trimmed one.
"""

import json
import re
import shutil
import subprocess
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent
DIGEST = ROOT / "tools" / "board_digest.sh"
WRAPPER = ROOT / "tools" / "session_start_trimmed.sh"
VENDORED = ROOT / ".claude" / "hooks" / "session-start.sh"
SETTINGS = ROOT / ".claude" / "settings.json"

pytestmark = pytest.mark.skipif(
    shutil.which("bash") is None, reason="bash unavailable (these are shell tools)"
)

BOARD = """# board

### Mac/live — a live task
- **Status:** ACTIVE
- **Worktree:** live-wt   **branch:** live
- **Touches:** src/alpha.py, tools/beta.sh
- **Holds:** the venv
- **Notes:** a long note that belongs in the file, not in every briefing

### Mac/done — a finished task
- **Status:** DONE 2026-08-20 — merged as PR #1
- **Touches:** src/gamma.py
- **Notes:** history worth keeping, and worth keeping out of the way
"""


def sh(script, *args):
    return subprocess.run(["bash", str(script), *args],
                          capture_output=True, text=True, cwd=ROOT, timeout=60)


@pytest.mark.parametrize("script", [DIGEST, WRAPPER], ids=["digest", "wrapper"])
def test_syntax_is_valid(script):
    assert subprocess.run(["bash", "-n", str(script)],
                          capture_output=True, text=True).returncode == 0


@pytest.mark.parametrize("script", [DIGEST, WRAPPER], ids=["digest", "wrapper"])
def test_every_branch_can_fire(script):
    r = sh(script, "--selftest")
    assert r.returncode == 0, r.stdout + r.stderr
    assert "all checks pass" in r.stdout


def test_the_live_block_travels_and_the_dead_one_does_not(tmp_path):
    b = tmp_path / "SESSIONS.md"
    b.write_text(BOARD, encoding="utf-8")
    out = sh(DIGEST, str(b)).stdout
    assert "Mac/live" in out
    assert "Mac/done" not in out, "a finished block is a record, not a briefing"
    assert "belongs in the file" not in out, "Notes must not travel"


def test_touches_travels_because_paths_are_what_collided(tmp_path):
    """Branch names would have caught none of 2026-08-20's three duplications.
    Paths would have caught all three, so the digest must carry them."""
    b = tmp_path / "SESSIONS.md"
    b.write_text(BOARD, encoding="utf-8")
    out = sh(DIGEST, str(b)).stdout
    assert "src/alpha.py" in out and "tools/beta.sh" in out


def test_it_says_how_many_are_live_out_of_how_many(tmp_path):
    b = tmp_path / "SESSIONS.md"
    b.write_text(BOARD, encoding="utf-8")
    assert "1 ACTIVE of 2" in sh(DIGEST, str(b)).stdout


def test_a_missing_board_is_reported_not_fatal(tmp_path):
    r = sh(DIGEST, str(tmp_path / "absent.md"))
    assert r.returncode == 0
    assert "no board yet" in r.stdout


def test_the_trim_is_large_enough_to_matter(tmp_path):
    """The property, on a board big enough to have it. 60 blocks of which 5 are
    live is roughly the shape that broke: the digest must cost a small fraction
    of the file, not a slightly smaller version of it.

    Stated against a synthetic board rather than the machine's own, because CI
    checks out a bare clone with no `-worktrees/` beside it — and a first draft
    of this test asserted the ratio there, where there is no board to trim and
    the trimmed output is *larger* by the size-canary line. The trim is only
    meaningful where a board exists; asserting it elsewhere tested nothing and
    failed honestly."""
    blocks = []
    for i in range(60):
        live = i % 12 == 0
        blocks.append(
            f"### Mac/task-{i} — a task\n"
            f"- **Status:** {'ACTIVE' if live else 'DONE 2026-08-19 — merged'}\n"
            f"- **Worktree:** wt-{i}\n"
            f"- **Touches:** src/mod_{i}.py\n"
            f"- **Notes:** " + ("history. " * 40) + "\n"
        )
    b = tmp_path / "SESSIONS.md"
    b.write_text("# board\n\n" + "\n".join(blocks), encoding="utf-8")

    digest = sh(DIGEST, str(b)).stdout
    assert "5 ACTIVE of 60" in digest
    assert len(digest) < len(b.read_text(encoding="utf-8")) / 8, (
        f"digest {len(digest)}B of a {b.stat().st_size}B board — not enough of a trim"
    )


def test_the_trim_fires_on_this_machines_own_board():
    """The same property end to end, where a real board exists. Skipped rather
    than asserted where it does not — see the note above."""
    full = sh(VENDORED).stdout
    m = re.search(r"^--- session board: (.*) ---$", full, re.M)
    if not m:
        pytest.skip("vendored hook printed no board marker")
    board = Path(m.group(1))
    if not board.is_file() or board.stat().st_size < 4000:
        pytest.skip(f"no substantial machine-local board here ({board})")
    trimmed = sh(WRAPPER).stdout
    assert len(trimmed) < len(full) / 2, (
        f"trimmed {len(trimmed)}B vs full {len(full)}B — the trim is not doing its job"
    )


def test_the_trimmed_briefing_keeps_everything_else():
    """The board dump is the only thing that goes. If the filter ate the tail,
    a session would lose the RULES line and the timing canary and never know."""
    trimmed = sh(WRAPPER).stdout
    if "SESSION START" not in trimmed:
        pytest.skip("not a git repo / hook unavailable")
    assert "RULES:" in trimmed
    assert "briefing took" in trimmed, "the vendored time canary must survive"
    assert "briefing delivered:" in trimmed, "the size canary must be printed"


def test_it_degrades_loudly_when_the_markers_move(tmp_path):
    """The vendored hook is upstream's. If it reformats, this filter must print
    the original and say so — a silent empty trim is the bug it exists to fix."""
    r = sh(WRAPPER, "--selftest")
    assert "no board marker refuses (3), never silent" in r.stdout
    assert "marker but no tail refuses (4)" in r.stdout


def test_the_hook_is_actually_wired_to_the_wrapper():
    """A trim nothing calls is decoration. The settings entry must name the
    wrapper, not the vendored hook it wraps."""
    cfg = json.loads(SETTINGS.read_text(encoding="utf-8"))
    entries = [h["command"]
               for m in cfg["hooks"]["SessionStart"]
               for h in m["hooks"]]
    assert any("session_start_trimmed.sh" in c for c in entries)
    assert not any(c.strip().endswith(".claude/hooks/session-start.sh") for c in entries), (
        "the vendored hook must be reached through the wrapper, not alongside it"
    )


def test_the_vendored_hook_is_still_vendored():
    """The whole reason this is a wrapper. If someone edits the core instead,
    the stamp goes and the file stops being re-copyable — say so here, loudly."""
    first = VENDORED.read_text(encoding="utf-8").splitlines()[1]
    assert "vendored from interface2" in first and "do NOT edit here" in first


def test_the_block_template_offers_a_touches_line():
    """The gate hands you the stanza to paste. If Touches is not in it, nobody
    writes one, and the digest has nothing to show."""
    r = subprocess.run(["bash", str(ROOT / "tools" / "guard_local_board.sh"),
                        "--board", "/definitely/absent.md", "--name", "w"],
                       capture_output=True, text=True, cwd=ROOT)
    assert "**Touches:**" in r.stderr
    assert "too late" in r.stderr.lower(), "the gate should admit when it fires"
