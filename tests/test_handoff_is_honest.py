"""A root HANDOFF.md is a claim, and a claim nothing checks goes stale silently.

CLAUDE.md rests a whole convention on this file: *"No handoff file on `main` ==
nothing in flight"*, so the root is a signal and it has to stay honest. Until now
the only thing keeping it honest was the promise each handoff makes about itself,
written inside the file it governs.

That promise has already failed once, and `docs/handoffs/README.md` records the
cost: `HANDOFF-difficulty-axis-and-synfire.md` sat at the root from 2026-08-20 to
2026-08-24 while its own second paragraph said *"nothing is half-done"*. For four
days the in-flight check returned a false positive, and the session that wrote it
had done nothing wrong — it followed the rule as written.

These tests make the claim machine-checkable instead:

1. **Structural, always runs.** If the file exists it must name the work it says is
   in flight as a PR number, near the top. A handoff that names nothing cannot be
   checked by anything, ever, and is indistinguishable from a forgotten file.
2. **Liveness, skips without network.** Every PR it names must still be open. When
   the last one closes the handoff is spent, and this is what says so — out loud, in
   CI, instead of four days later when somebody notices.

The second test is the one that matters and the one that can be offline, so it
degrades to a skip rather than a failure. The first cannot be skipped: it is what
makes the second possible.
"""

import json
import re
import shutil
import subprocess
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent
HANDOFF = ROOT / "HANDOFF.md"

# The in-flight claim belongs in the opening section, where `session_briefing.sh`'s
# `head -14` will surface it at session start. A PR named on line 300 reaches nobody,
# which is the same failure one level down.
HEAD_LINES = 40
PR_REF = re.compile(r"(?:pull/|#)(\d{2,5})\b")


def _named_prs(text: str) -> list[int]:
    return sorted({int(m) for m in PR_REF.findall(text)})


def _states(prs: list[int]) -> dict[int, tuple[str, str]] | None:
    """{pr: (state, title)}, or None when the API cannot answer — offline,
    unauthenticated, rate-limited. None means "no evidence", never "stale"."""
    out = {}
    for pr in prs:
        proc = subprocess.run(
            ["gh", "pr", "view", str(pr), "--json", "state,title"],
            cwd=ROOT, capture_output=True, text=True, timeout=30,
        )
        if proc.returncode != 0:
            return None
        info = json.loads(proc.stdout)
        out[pr] = (info["state"], info["title"])
    return out


def test_a_root_handoff_names_the_work_it_says_is_in_flight():
    """No PR number, no check. This is the precondition for every other guard."""
    if not HANDOFF.exists():
        pytest.skip("no root HANDOFF.md — nothing is in flight, which is the normal state")
    head = "\n".join(HANDOFF.read_text().splitlines()[:HEAD_LINES])
    prs = _named_prs(head)
    assert prs, (
        f"HANDOFF.md names no PR in its first {HEAD_LINES} lines. The root handoff is the "
        f"repo's 'something is in flight' signal, and a signal that does not say WHAT is in "
        f"flight cannot be retired by anything except somebody remembering. Name the PR."
    )


def test_every_pr_the_handoff_claims_is_still_open():
    """When the last one closes, the handoff is spent and the root must be cleared.

    `docs/handoffs/README.md` gives the three options: delete it if the content is
    spent, move it to `docs/handoffs/` if any of it is still worth reading, and never
    leave it at the root claiming work that has landed.
    """
    if not HANDOFF.exists():
        pytest.skip("no root HANDOFF.md — nothing is in flight")
    if not shutil.which("gh"):
        pytest.skip("gh not available — liveness needs the API")

    head = "\n".join(HANDOFF.read_text().splitlines()[:HEAD_LINES])
    prs = _named_prs(head)
    if not prs:
        pytest.skip("covered by the structural test, which fails on this instead")

    states = _states(prs)
    if states is None:
        pytest.skip("gh could not answer — no network or no auth; absence is not evidence")

    assert _still_live(states), _spent_message(states)


def _still_live(states: dict[int, tuple[str, str]]) -> bool:
    return any(s == "OPEN" for s, _ in states.values())


def _spent_message(states: dict[int, tuple[str, str]]) -> str:
    return (
        "HANDOFF.md is at the root claiming work is in flight, and every PR it names has "
        "closed:\n"
        + "\n".join(f"  #{p} {s} — {t[:60]}" for p, (s, t) in sorted(states.items()))
        + "\n\nThe signal is spent. docs/handoffs/README.md gives three options and only two "
          "are allowed: delete the file if nothing in it is worth reading, or move it to "
          "docs/handoffs/ dated if anything is. Leaving it at the root is the four-day false "
          "positive that directory exists to prevent."
    )


def test_the_liveness_check_can_actually_fire():
    """sapper's rule, applied to a test: a guard nobody has watched fail is not a guard.

    Driven on a synthetic state map rather than by planting a HANDOFF.md at this root —
    that file's presence is a live signal other sessions read, and a test must not forge
    it even briefly.
    """
    spent = {303: ("MERGED", "take the correction"), 291: ("MERGED", "the null test")}
    assert not _still_live(spent), "an all-closed handoff must not read as live"
    assert "The signal is spent" in _spent_message(spent)
    assert "#303 MERGED" in _spent_message(spent), "the message must name what closed"

    mixed = {298: ("OPEN", "parity was the inheritance"), 303: ("MERGED", "the correction")}
    assert _still_live(mixed), "one open PR is enough — the handoff is still doing its job"
