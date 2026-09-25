---
status: waiting-on-tony
filed: 2026-09-25
---

# Land the Python 3.14 floor (#825)

waiting: After #825 merges, drop the 3.11 and 3.13 required checks.

**What:** [ADR-0011](../adr/0011-bugarach-supports-the-python-its-machines-run.md), on draft PR
#825 (branch `python-floor-3-14`). `requires-python` goes to `>=3.14`, CI tests only 3.14, and
the README says so. Tony approved it on 2026-09-25, to land after the night's prep PRs.

**Order. Each step is someone's job:**
1. **A session:** merge the waiting prep PRs, #823 and #824, first.
2. **A session:** merge main into `python-floor-3-14` (the ADR index conflicts once ADR-0010's
   row lands), mark #825 ready, and merge it. It shows as blocked because its own 3.11 and 3.13
   checks never report, so it merges only once step 3 is done or Tony merges it as an admin.
3. **Tony:** remove `test (3.11)` and `test (3.13)` from main's required checks. Only a repo admin
   can.
4. **A session:** confirm the next PR goes green on `test (3.14)` alone, then set this file's
   status to `done`.

**Why this is a todo and not only a reminder:** the change is inert until all four steps happen,
and a half-landed version blocks every PR in the repository. The briefing lists this file at the
start of every session until it is closed.
