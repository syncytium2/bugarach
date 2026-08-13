---
status: open
filed: 2026-08-13
---

# The commit gates are opt-in per clone, so a fresh clone has none

`.githooks/pre-commit` runs the branch guard and sapper, and its own header says
the point is that "both run without anyone remembering them". They don't. Git
ignores `.githooks/` until someone runs

```
git config core.hooksPath .githooks
```

which is **per clone**, stored in `.git/config`, and therefore travels with
nothing. Found 2026-08-13: this Mac clone had never had it set, so every commit
made here for the life of the clone bypassed both gates. The gates were working
perfectly and were simply not installed.

## Why this is the sapper lesson, again

The repo's own rule is to prefer a mechanized check over prose (CLAUDE.md), and
the simulation plan names the failure mode outright: **a gate written as a
sentence gets skipped.** The enabling step is currently a sentence — in
CLAUDE.md, in `docs/git_workflow.md`, and in the hook's own comment. Three
places, all prose, none of them executable.

The consequence is quiet rather than loud, which is worse: nothing fails, and a
commit that a gate would have blocked simply lands. `main` is protected and CI
runs sapper, so the blast radius is a branch rather than production — but the
branch guard's whole job is to catch a commit *before* it is authored on `main`,
and that one has no CI backstop at all.

## Options

1. **A `SessionStart` check.** The hook that prints the briefing already runs on
   every session; have it verify `core.hooksPath` and say so loudly when unset.
   Cheap, and it fires on the machine where the problem is — but it warns rather
   than fixes, and only for sessions started through Claude Code.
2. **Self-install from the test suite.** `tests/test_sapper.py` already proves
   the gates can fire; add a test that asserts `core.hooksPath` is configured.
   Runs on every developer's first `pytest`, fails loudly with the one command
   to run. Would need to skip in CI, where the setting is irrelevant.
3. **Set it in the bootstrap path.** Whatever a new clone runs first
   (`pip install -e ".[dev]"` has no hook; a `make setup` or `tools/setup.sh`
   would) configures it. The honest fix, and it needs a bootstrap step to exist.

Options 1 and 2 are complementary and neither is much work: 2 catches it on any
machine running the suite, 1 catches it before the first commit. Do not fix this
by adding a fourth sentence to a document.

## Check it on a given clone

```
git config core.hooksPath        # want: .githooks — no output means the gates are off
```

Worth running on the workstation, which has never been checked.
