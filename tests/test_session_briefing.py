"""The session briefing must actually carry the facts that bind.

CLAUDE.md's first line says to read docs/FOUNDATIONS.md at session start. A
session on 2026-08-13 did not, and spent a day building on the assumption that
TTX silences the field — which this project's data refutes and FOUNDATIONS
forbids. Tony: *"claude.md is the first thing you ignore. we have built tools
for this purpose."*

So the fix is not another sentence in a file that has to be read to work. The
briefing injects the binding facts into every session's context whether anyone
opens the file or not — and these tests are the sapper-style proof that it can
fire, because a channel nobody verifies is the same as no channel.
"""

import json
import os
import shutil
import subprocess
import tempfile
import time
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent
SCRIPT = ROOT / "tools" / "session_briefing.sh"


@pytest.fixture(scope="module")
def briefing():
    t0 = time.monotonic()
    out = subprocess.run(["bash", str(SCRIPT)], cwd=ROOT,
                         capture_output=True, text=True, timeout=30)
    return out, time.monotonic() - t0


def test_it_runs_and_succeeds(briefing):
    out, _ = briefing
    assert out.returncode == 0, out.stderr


def test_it_is_fast_enough_to_be_unconditional(briefing):
    """It runs on the blocking session-start path, ahead of the generic hook.
    interface2 lost half a day to a SessionStart hook that took the whole
    session down at 60 s; this one is local-only and must stay trivial.

    This docstring used to go on: "the moment it needs a budget it becomes
    droppable — and a channel dropped for budget is the failure it exists to
    prevent." That reasoning conflated two budgets. A RUNTIME budget would make
    the hook droppable; a SIZE budget is what keeps it deliverable, and refusing
    one is what made the whole channel silent on 2026-08-25 instead of shorter.
    """
    _, elapsed = briefing
    assert elapsed < 3.0, f"briefing took {elapsed:.1f}s on the blocking path"


# ---------------------------------------------------------------------------------
# DELIVERY. Everything below this line asserts about what a session RECEIVES.
#
# The fifteen tests in this file on 2026-08-25 all asserted what the script PRINTS,
# and every one of them passed while the hook emitted 17,568B — which the harness
# spilled to a file, injecting a 2KB preview instead. 88% of a green-tested channel
# reached nobody: the waiting-on-tony alarm, the commit-gate report, the handover
# gates, the darkroom line, and the HANDOFF-in-flight alarm, which nothing else in
# the tree prints.
#
# `test_waiting_items_come_before_the_fifty_open_ones` is the sharpest example. It
# asserts an ORDERING, and passed — with both sides of the comparison past the cut.
# ---------------------------------------------------------------------------------


def _budget() -> int:
    """The script's own default, read from the script — never a second copy of the
    number here, or the test and the thing it guards drift apart."""
    for line in SCRIPT.read_text().splitlines():
        if line.startswith("briefing_budget()"):
            return int(line.split(":-")[1].split("}")[0])
    raise AssertionError("briefing_budget() is gone — the size guard has no number")


def test_the_briefing_fits_in_one_injection(briefing):
    """THE TEST THIS FILE DID NOT HAVE.

    An oversized SessionStart hook is not truncated in place — it is spilled to a
    file and replaced by a ~2KB preview, so going over is not "slightly less gets
    through", it is "almost nothing does". Two payloads are known to have been
    spilled (60,235B and 13,414B); 6,809B is known to have arrived whole.

    A content assertion cannot catch this, because the content is all still there
    in the script's stdout. Only the total can.
    """
    out, _ = briefing
    size = len(out.stdout.encode())
    assert size <= _budget(), (
        f"the briefing is {size}B against a {_budget()}B budget. It will be spilled "
        f"to a file and delivered as a 2KB preview — i.e. it will not arrive. Trim a "
        f"section or move it behind the budget ladder in deliver()."
    )


def test_it_prints_its_own_size(briefing):
    """The canary. The 2026-08-20 note on the sibling hook ends "Watch that number";
    this one had no number to watch, which is how it crossed the line unobserved."""
    out, _ = briefing
    assert "briefing delivered:" in out.stdout
    assert f"budget {_budget()}B" in out.stdout


def test_the_alarms_come_before_the_bulk(briefing):
    """Ordering as a survival property, not a courtesy.

    If the budget machinery ever fails, what survives is whatever fits in 2KB. The
    alarms are bounded and small; FOUNDATIONS §9 is 5.7KB. So the alarms lead —
    which is the reverse of the order that made them invisible.
    """
    out, _ = briefing
    facts = out.stdout.index("Facts about the preparation")
    for alarm in ("commit gates:", "darkroom:", "gates, before you hand anything over"):
        assert alarm in out.stdout, f"alarm missing entirely: {alarm}"
        assert out.stdout.index(alarm) < facts, (
            f"{alarm!r} sits after the 5.7KB FOUNDATIONS extract. That is the "
            f"position it was in when it stopped arriving."
        )


def test_the_open_thread_list_is_a_count_not_a_dump(briefing):
    """9,658B of the 17,568 that got this hook spilled was a list of every open todo
    — the largest thing in the briefing and, by its own handoff's account, "a record,
    not a queue". It evicted the six alarms behind it. The count and the query stay;
    the list is a file you open."""
    out, _ = briefing
    assert "open threads:" in out.stdout
    names = [p.name for p in sorted((ROOT / "docs" / "todo").glob("*.md"))
             if "status: open" in p.read_text()]
    listed = [n for n in names if n in out.stdout]
    assert not listed, f"the open-todo dump is back ({len(listed)} filenames): {listed[:3]}"


def test_a_root_handoff_is_the_first_thing_a_session_sees():
    """This script is the ONLY thing in the tree that reads HANDOFF.md, and CLAUDE.md
    rests "no handoff file == nothing in flight" on it. On 2026-08-25 the alarm sat at
    byte 17,569 of a stream cut at 2,000, so a root handoff could not have reached any
    session at all.

    Driven in a throwaway repo rather than by creating HANDOFF.md at this root: the
    file's presence is a live signal other sessions read, and a test must not forge it
    even for a second.
    """
    with tempfile.TemporaryDirectory() as tmp:
        repo = Path(tmp)
        subprocess.run(["git", "init", "-q"], cwd=repo, check=True)
        (repo / "tools").mkdir()
        (repo / "docs" / "todo").mkdir(parents=True)
        shutil.copy(SCRIPT, repo / "tools" / SCRIPT.name)
        shutil.copy(ROOT / "tools" / "guard_local_board.sh", repo / "tools")
        shutil.copy(ROOT / "docs" / "FOUNDATIONS.md", repo / "docs")
        (repo / "HANDOFF.md").write_text(
            "# Handoff — the one thing in flight\n\nPR #1 is open and main depends on it.\n"
        )
        out = subprocess.run(["bash", "tools/" + SCRIPT.name], cwd=repo,
                             capture_output=True, text=True, timeout=30)

    assert "HANDOFF.md present" in out.stdout, "the in-flight alarm did not fire"
    head = "\n".join(out.stdout.splitlines()[:6])
    assert "HANDOFF.md present" in head, (
        "the in-flight alarm is not in the first six lines. It was last, and last is "
        "where it stopped arriving:\n" + head
    )
    assert "the one thing in flight" in out.stdout, "the alarm must carry the file's own words"


def test_over_budget_it_degrades_loudly_and_keeps_the_alarms():
    """Degrade loudly, the rule the sibling hook sets for its own budget cuts. A
    silent trim looks like a working briefing while delivering less than it says."""
    env = {**os.environ, "BUGARACH_BRIEFING_BUDGET_BYTES": "1"}
    out = subprocess.run(["bash", str(SCRIPT)], cwd=ROOT, env=env,
                         capture_output=True, text=True, timeout=30)
    assert "TTX IS NOT A SILENCING CONTROL" in out.stdout, "the claim must survive any cut"
    assert "min_rois" not in out.stdout, "the reasoning is what the cut drops"
    assert "THE CLAIMS ONLY" in out.stdout, "and it must say that it cut"
    assert "(TERSE" in out.stdout, "the canary names the degraded mode"
    assert "commit gates:" in out.stdout, "alarms are never budgeted"
    assert "over the 1B budget" in out.stderr, "and it is loud where a human looks"


def test_the_selftest_passes():
    """sapper-style: the script proves its own ladder can fire in every direction,
    and the suite runs that proof rather than trusting it."""
    out = subprocess.run(["bash", str(SCRIPT), "--selftest"], cwd=ROOT,
                         capture_output=True, text=True, timeout=60)
    assert out.returncode == 0, out.stdout + out.stderr
    assert "all checks pass" in out.stdout


def test_it_carries_the_ttx_fact(briefing):
    """The specific thing a session got wrong, and the reason this file exists."""
    out, _ = briefing
    assert "TTX IS NOT A SILENCING CONTROL" in out.stdout
    assert "min_rois" in out.stdout, "the consequence must travel with the fact"


def test_it_carries_the_held_out_treatment(briefing):
    out, _ = briefing
    assert "Senktide is not one effect" in out.stdout


def test_the_facts_are_read_from_foundations_not_restated():
    """If the briefing restated them, the two would drift and the canonical file
    would quietly stop being canonical."""
    text = SCRIPT.read_text()
    assert "docs/FOUNDATIONS.md" in text
    assert "TTX IS NOT" not in text, "the fact is extracted, never hardcoded here"


def test_foundations_still_has_the_section_the_briefing_extracts():
    """The other half of the same guard: renaming or deleting section 9 would
    make the briefing silently print nothing."""
    foundations = (ROOT / "docs" / "FOUNDATIONS.md").read_text()
    assert "## 9. Facts about the preparation" in foundations
    assert "## 10." in foundations, "the extractor needs a terminating heading"


def test_it_names_the_gates_that_get_skipped(briefing):
    out, _ = briefing
    for gate in ("murderboard", "never commit on main", "render the figure"):
        assert gate in out.stdout, f"gate not surfaced: {gate}"


def test_it_reports_whether_the_commit_gates_are_installed(briefing):
    """core.hooksPath is per clone and travels with nothing, so a fresh clone
    silently has no branch guard and no sapper."""
    out, _ = briefing
    assert "commit gates:" in out.stdout


def test_it_reports_where_figure_output_goes(briefing):
    """A session must not have to ask, or infer it from a silent skip.

    On 2026-08-17 one reported the darkroom unavailable and skipped its export
    while Dropbox sat mounted and visible in Finder — BUGARACH_DARKROOM was
    exported from a ~/.zshrc, which zsh reads for interactive shells only. The
    briefing prints what resolved, so the next session sees the answer instead of
    the absence of one.
    """
    out, _ = briefing
    assert "darkroom:" in out.stdout


@pytest.mark.parametrize(
    "value, expected",
    [
        ("__set_to_a_real_dir__", "$BUGARACH_DARKROOM ->"),
        ("/definitely/not/here", "does not exist"),
    ],
)
def test_it_distinguishes_a_set_variable_from_a_usable_one(tmp_path, value, expected):
    """Set-but-wrong is the failure a bare "is it set?" check reads as healthy."""
    env = {"PATH": "/usr/bin:/bin:/usr/sbin:/sbin", "HOME": str(tmp_path)}
    env["BUGARACH_DARKROOM"] = str(tmp_path) if value.startswith("__") else value
    out = subprocess.run(["bash", str(SCRIPT)], cwd=ROOT, env=env,
                         capture_output=True, text=True, timeout=30)
    assert expected in out.stdout, out.stdout


def test_with_no_variable_and_no_dropbox_it_says_exports_are_skipped(tmp_path):
    """The honest end state: nowhere to write, and nothing pretending otherwise.

    HOME points at an empty directory, so the resolver finds no info.json and
    discovery declines — which is what a fresh machine with no Dropbox looks like.
    """
    env = {"PATH": "/usr/bin:/bin:/usr/sbin:/sbin", "HOME": str(tmp_path)}
    out = subprocess.run(["bash", str(SCRIPT)], cwd=ROOT, env=env,
                         capture_output=True, text=True, timeout=30)
    assert "darkroom: not found" in out.stdout
    assert "SKIPPED" in out.stdout
    assert "python -m bugarach.paths" in out.stdout, "say how to look into it"


def test_it_surfaces_work_that_is_finished_and_waiting_on_a_person(briefing):
    """`open` cannot say "done, awaiting a human" -- so that kind drowned.

    The PySpike report was finished, verified and correct for twelve days while
    nothing in the repo said it was ready to go out. `waiting-on-tony` is the
    status for work no session can advance, and this asserts it reaches the top
    of the briefing with its one action attached, rather than sitting at line 31
    of fifty open threads.
    """
    out, _ = briefing
    waiting = [p for p in sorted((ROOT / "docs" / "todo").glob("*.md"))
               if p.name != "README.md" and "status: waiting-on-tony" in p.read_text()]
    assert waiting, "no waiting-on-tony items -- if that is real, delete this test"
    assert "waiting on Tony" in out.stdout
    # README documents the format, so it carries the frontmatter as an example and
    # reported itself as a waiting item on the first run. It must not come back.
    assert "docs/todo/README.md" not in out.stdout
    for item in waiting:
        assert item.name in out.stdout, f"{item.name} never reached the briefing"
        action = [ln for ln in item.read_text().splitlines()
                  if ln.startswith("waiting: ")]
        assert action, f"{item.name} has no `waiting:` line saying what to do"
        assert action[0][len("waiting: "):][:40] in out.stdout, \
            f"{item.name}'s action line never printed"


def test_waiting_items_come_before_the_fifty_open_ones(briefing):
    """Position is the whole point: a loud line after fifty quiet ones is quiet."""
    out, _ = briefing
    if "waiting on Tony" not in out.stdout:
        pytest.skip("no waiting-on-tony items right now")
    assert out.stdout.index("waiting on Tony") < out.stdout.index("open threads:")


def test_it_is_wired_into_both_session_start_matchers():
    """Wired as its own entry so the vendored generic hook stays byte-identical
    and re-copyable, and placed FIRST so the binding facts land even if the
    later git briefing truncates."""
    cfg = json.loads((ROOT / ".claude" / "settings.json").read_text())
    blocks = cfg["hooks"]["SessionStart"]
    assert {b["matcher"] for b in blocks} == {"startup", "resume"}
    for block in blocks:
        assert block["hooks"][0]["command"] == "bash tools/session_briefing.sh"


# ---------------------------------------------------------------------------------
# THE CANARY HAS TO BE THE PART THAT SURVIVES, and the number on it has to be true.
#
# #306 added a size canary and printed it as the LAST line — the one position a
# spilled payload cannot deliver, since a spill keeps the opening ~2KB and discards
# the rest. So it reported only in the case where nothing was wrong.
# ---------------------------------------------------------------------------------

CENSUS = ROOT / "tools" / "hook_spill_census.sh"


def test_the_canary_is_the_first_line(briefing):
    out, _ = briefing
    first = out.stdout.splitlines()[0]
    assert first.startswith("briefing delivered:"), (
        "the canary is not line 1. A spilled payload keeps its opening bytes and "
        f"drops the rest, so anywhere else it reports only on success. Got: {first!r}"
    )


def test_the_canary_number_is_the_real_payload_size(briefing):
    """A canary that is merely present was what this file already had. The number
    describes the whole payload including the canary line itself — which is why
    canary_line() settles a fixed point rather than measuring the body alone."""
    out, _ = briefing
    claimed = int(out.stdout.split("lines, ")[1].split("B")[0])
    assert claimed == len(out.stdout.encode()), (
        f"the canary says {claimed}B and the payload is {len(out.stdout.encode())}B"
    )


def test_the_alarms_with_a_deadline_are_inside_the_preview(briefing):
    """Stated as an OFFSET, not as a total, and the difference is the whole finding.

    A first cut of this asserted the alarm block came in under 2,000B. It passed on
    a configured machine — where "commit gates: ACTIVE" and "darkroom: -> ..." are
    one line each — and failed on CI, where the clone is fresh, every standing alarm
    fires at full length and the block runs past 2.3KB whatever else happens. The
    tempting repair was to squeeze the waiting-on-Tony list to make room, which is
    backwards twice: it truncates the one list with a person waiting at the end of
    it, to protect standing context that has no deadline.

    So what ordering actually buys is asserted directly. The alarms that cannot wait
    — a live handoff, work finished and waiting on a person, whether the commit
    gates are installed — are rendered first and land inside the first 2,000 bytes
    however misconfigured the machine is. `head -14 HANDOFF.md` bounds lines rather
    than bytes, and fourteen 300-character lines would undo exactly that.
    """
    out, _ = briefing
    preview = out.stdout.encode()[:2000].decode("utf-8", "ignore")
    assert "commit gates:" in preview, (
        "the commit-gate alarm is past the ~2KB a spilled payload keeps. Everything "
        "ordered after it is past it too."
    )
    if "waiting on Tony" in out.stdout:
        assert "waiting on Tony" in preview


def test_the_ladder_has_a_floor():
    """A terse render that is still over budget used to ship labelled '(TERSE',
    which reads as a degrade that worked. There is no rung below it, so the only
    honest move is to say so."""
    env = {**os.environ, "BUGARACH_BRIEFING_BUDGET_BYTES": "1"}
    out = subprocess.run(["bash", str(SCRIPT)], cwd=ROOT, env=env,
                         capture_output=True, text=True, timeout=30)
    assert "STILL OVER" in out.stdout.splitlines()[0], "the canary must name the floor"
    assert "STILL over" in out.stderr, "and it must be loud where a human looks"


def test_each_hook_reads_its_own_budget_variable():
    """One name meant two numbers: BUGARACH_BRIEFING_BUDGET_BYTES defaulted to 9,000
    in session_briefing.sh and 8,000 in session_start_trimmed.sh, so setting it to
    drive either hook silently retuned the other — including this file's own
    over-budget tests, which set it to 1."""
    sibling = (ROOT / "tools" / "session_start_trimmed.sh").read_text()
    live = [ln for ln in sibling.splitlines()
            if "BUGARACH_" in ln and "BUDGET_BYTES" in ln
            and not ln.lstrip().startswith("#")]
    assert live, "the sibling hook reads no budget variable at all"
    for line in live:
        assert "BUGARACH_BRIEFING_BUDGET_BYTES" not in line, (
            f"the sibling still reads this script's variable: {line.strip()}"
        )
        assert "BUGARACH_SESSION_START_BUDGET_BYTES" in line


def test_the_budget_is_under_what_the_harness_has_actually_refused():
    """THE CIRCULARITY, BROKEN. test_the_briefing_fits_in_one_injection reads the
    budget out of the script and asserts the output is under it — so raising the
    budget to 50,000 keeps that test green while the channel dies.

    tools/hook_spill_census.sh supplies the outside number: every payload the
    harness ever refused is still on disk, because refusing it is what wrote it
    there. Skipped where there is no such record (CI, a fresh clone) — the number
    comes from outside this repo, so it cannot always be here.
    """
    census = subprocess.run(["bash", str(CENSUS), "--values"], cwd=ROOT,
                            capture_output=True, text=True, timeout=180)
    assert census.returncode == 0, census.stderr
    vals = dict(ln.split("=", 1) for ln in census.stdout.strip().splitlines() if "=" in ln)
    if not vals.get("spilled_min"):
        pytest.skip("no spill on record on this machine — nothing to calibrate against")

    check = subprocess.run(["bash", str(CENSUS), "--check", str(_budget())], cwd=ROOT,
                           capture_output=True, text=True, timeout=180)
    assert check.returncode == 0, check.stdout + check.stderr


def test_the_budget_is_also_above_the_ordinary_briefing(briefing):
    """The other side of it, and why the budget was NOT lowered to the sibling's
    8,000 when the census came back tighter than the header had claimed: a budget
    under the ordinary payload degrades §9 to its claims on every run and reports
    that as normal."""
    out, _ = briefing
    assert "(TERSE" not in out.stdout, (
        "the ordinary briefing is already degrading. The ladder is a backstop, not "
        "the normal path — trim a section rather than living in the degraded form."
    )
