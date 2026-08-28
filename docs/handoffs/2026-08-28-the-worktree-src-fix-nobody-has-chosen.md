# A worktree's tests run against another branch's code — three fixes, pick one

**Short on purpose.** Tony, 2026-08-28, on the root handoff: *"might as well be page
666 of the bible at this point"* — meaning **antiquity**, not length. A handoff nobody
finishes is one nobody acts on, so this is one screen and one decision.

## The defect

The venv holds **one** editable install, made from the primary checkout:

```
$ .venv/bin/python -c "import bugarach; print(bugarach.__file__)"
/…/Developer/bugarach/src/bugarach/__init__.py      # the PRIMARY checkout
```

Run `pytest` from a worktree and you get **that worktree's `tests/` against the primary
checkout's `src/`.** With a dozen worktrees the two are almost never at the same commit.

Demonstrated with primary at `7ee0a3a`, worktree at `7a0c221`:

| run | result |
|---|---|
| `pytest tests/` | collection error — `cannot import name 'VAL_SEED_BLOCK'` |
| `PYTHONPATH=$PWD/src pytest tests/` | 1498 passed, 3 skipped, 1 xfailed |

**It fails toward green.** The error above was the lucky case. The dangerous one is a
worktree editing `src/` whose tests never execute the edit — and that is silent. It has
already put *"1454 passed, 16 skipped"* into two PR messages on 2026-08-28, measured
against a tree that was not the branch's.

CI does not have this: it checks out one tree and installs it. The hazard exists only on
the machine where every session runs.

## The three fixes

1. **`PYTHONPATH=$PWD/src` by hand.** Works today. Depends on being remembered, which
   this project's own rule says is not a gate.
2. **`tests/conftest.py` inserts the repo's own `src` at position 0.** Three lines; fixes
   every invocation including a bare `pytest`; needs nothing from the runner. **Check it
   does not break CI**, where the installed package and the tree are the same thing.
3. **A guard test** asserting `bugarach.__file__` resolves under the repo root of the
   tests being run, failing loudly otherwise. Cannot be forgotten; makes the failure
   legible instead of silent.

**Recommendation: 2 + 3.** (2) fixes it, (3) proves it stayed fixed. (1) is what to type
until one of them lands.

## Why it is not already done

Tony was asked and said *"no clue, write the handoff"* — so this is unchosen, not
blocked. **A `conftest.py` change touches every test run in every worktree**, which is
why the session that found it did not slip it into an unrelated PR.

## What to watch when doing it

- Run the suite from **both** a worktree and the primary checkout afterwards; the fix must
  not make the primary import something unexpected.
- Confirm CI still passes on all three Python legs — that is the case where the installed
  package and the tree coincide, and a `sys.path` insert is a no-op if it is right and a
  shadow if it is not.
- The full todo, with the reasoning behind each option, is
  [`docs/todo/2026-08-28-a-worktree-pytest-run-tests-the-primary-checkouts-src.md`](../todo/2026-08-28-a-worktree-pytest-run-tests-the-primary-checkouts-src.md).

## Provenance

Found 2026-08-28 by accident, while a collection error exposed it during unrelated work.
Written at Tony's request. **Review scope: a single-pass claim check** against the two
commits, the two suite runs and the venv's own resolution — not an eleven-role
murderboard, stated because a handoff claiming more review than it had is the defect this
repo files incidents about.
