---
status: open
filed: 2026-08-28
---

# A worktree's `pytest` run tests the PRIMARY checkout's `src`, and reports success

Found by accident, and it had already corrupted a number I reported.

## What happens

The venv holds one editable install, made from the primary checkout:

```
$ .venv/bin/python -c "import bugarach; print(bugarach.__file__)"
/Users/…/Developer/bugarach/src/bugarach/__init__.py      # the PRIMARY checkout
```

Run `pytest` from a worktree and you get **that worktree's `tests/` against the primary
checkout's `src/`.** The two are almost never at the same commit — this project keeps a
dozen worktrees and the primary drifts on its own — so a green run means "your tests pass
against somebody else's code."

Demonstrated 2026-08-28, primary at `7ee0a3a` and the worktree at `7a0c221`:

| run | result |
|---|---|
| `pytest tests/` from the worktree | **collection error** — `cannot import name 'VAL_SEED_BLOCK'` |
| `PYTHONPATH=$PWD/src pytest tests/` | **1498 passed, 3 skipped, 1 xfailed** |

The error was the giveaway. **The silent case is the dangerous one**, and it had already
happened: two PRs the same day reported *"1454 passed, 16 skipped"* as evidence, measured
against the primary checkout's older tree. The true figure for those branches was
different, and nothing said so. A count quoted from the wrong tree is exactly the class of
claim this project files incidents about.

## Why it is worse than it looks

- **It fails toward green.** A worktree editing `src/` gets tests that never see the edit.
  A change can pass its own suite without being executed once.
- **It is invisible in the output.** pytest prints the rootdir, not the import origin.
- **CI does not have it.** CI checks out one tree and installs it, so the failure mode
  exists only on this machine — which is where every session runs.
- **The reported number moves.** 1454/16 against 1498/3 is not a rounding difference; the
  older `src` skipped tests the newer one enables, so the *shape* of the result changed
  too.

## Fixes, cheapest first

1. **`PYTHONPATH=$PWD/src`** in front of every worktree pytest invocation. Works today,
   depends on being remembered, which this project's own rule says is not a gate.
2. **A `conftest.py` that inserts the repo's own `src` at position 0.** `tests/conftest.py`
   already exists. Three lines, fixes every invocation including a bare `pytest`, and
   needs nothing from the runner. Check it does not break the CI path, where the installed
   package and the tree are the same thing.
3. **A sapper-style guard**: a test that asserts `bugarach.__file__` resolves under the
   repo root of the tests being run, and fails loudly otherwise. This is the version that
   cannot be forgotten, and it makes the failure legible instead of silent.

(2) plus (3) is probably right — (2) fixes it, (3) proves it stayed fixed.

## What this does not explain

`.venv` is machine-local by design (CLAUDE.md's inventory), so one shared editable install
is the natural consequence of the worktree workflow rather than a mistake anyone made. The
question is not why it happens but why nothing says so when it does.
