---
status: open
filed: 2026-08-15
---

# The session briefing takes 15.8 s on Windows against a 3 s budget

`tests/test_session_briefing.py::test_it_is_fast_enough_to_be_unconditional`
asserts the briefing completes in under 3 s. On the Windows box (WSMIP) it takes
**15.8 s**, so the test fails there while CI stays green.

```
E  AssertionError: briefing took 15.8s on the blocking path
E  assert 15.811999999918044 < 3.0
```

## Why this is a finding and not a flaky test

The budget is not arbitrary. The briefing runs on the **blocking** SessionStart
path, and the test's own docstring gives the reason: interface2 lost half a day
to a SessionStart hook that took whole sessions down at 60 s. The rule that came
out of that incident is that a blocking hook must stay trivial, "because the
moment it needs a budget it becomes droppable — and a channel dropped for budget
is the failure it exists to prevent."

15.8 s is a fifth of the way to the SDK's abort, on a machine that is in the
rotation. The guard is doing its job; the platform is where the assumption
breaks.

This is consistent with an independent measurement: the vendored
`.claude/hooks/session-start.sh` was timed at **16 s** on this same box on
2026-08-12, against its own 20 s budget. Two different scripts, both ~16 s, both
dominated by git. Windows git in this environment is slow enough that "trivial"
does not survive the port.

## Do NOT fix it by raising the budget

The number encodes an incident. Raising it to 20 s makes the test pass and
removes the only thing that would warn before a session-killing hook ships.

Options that keep the guarantee:

1. **Make the briefing cheap on Windows.** Find what dominates — almost certainly
   git subprocesses; each one pays process-creation cost that is far higher on
   Windows than on Linux/macOS. Batch them, or drop the expensive sections on
   the blocking path and defer them.
2. **Move it off the blocking path**, the way the murderboard freshness gate
   does with `--hook`: serve a cached answer instantly, refresh detached. The
   pattern is already vendored in this repo and solves exactly this.
3. **Platform-aware budget with a loud floor**: assert < 3 s on POSIX and, say,
   < 20 s on Windows, and make the Windows branch *print* its timing so the drift
   is visible rather than silently allowed. Weakest of the three — it documents
   the problem instead of fixing it.

Option 2 is the one with precedent in this repo.

## How to reproduce

```bash
python -m pytest tests/test_session_briefing.py -q     # on Windows: fails
bash tools/session_briefing.sh                          # time it directly
```

CI (ubuntu) passes, so `main` is genuinely green — this is a cross-OS gap, not a
regression.

---

## Update 2026-08-17 — the gap is wider than one timing assertion

Re-checked at session close. CI on `main` is green (Linux); on native Windows
**11 tests fail across two files**, five distinct cases:

```
tests/test_session_briefing.py::test_it_is_fast_enough_to_be_unconditional
tests/test_session_briefing.py::test_with_no_variable_and_no_dropbox_it_says_exports_are_skipped
tests/test_session_briefing.py::test_it_distinguishes_a_set_variable_from_a_usable_one[...]  (x2)
tests/test_session_briefing.py::test_foundations_still_has_the_section_the_briefing_extracts
tests/test_paths.py::test_windows_path_is_translated_for_wsl
```

So this is no longer "one performance budget does not survive the port". The
briefing's *behaviour* tests fail on Windows too, and a **WSL path-translation
test fails on native Windows** — plausibly because it assumes a WSL environment
that a plain Windows shell is not.

Worth noting what this means about the guard: every one of these passes in CI, so
nothing warns before a Windows session hits them. The repo is worked from a
Windows box in the rotation (FOUNDATIONS §8), so "green" currently means "green
on Linux".

**The cheapest thing that would have caught it:** add Windows to the CI matrix,
even as a non-blocking job to start. `.github/workflows/ci.yml` runs
`ubuntu-latest` across three Pythons — three Linuxes and no other OS. A single
`windows-latest` entry converts this whole class of finding from "somebody
notices while doing something else" into a build signal.
