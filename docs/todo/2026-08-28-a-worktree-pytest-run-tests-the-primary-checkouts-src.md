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

## 2026-08-29 — it bites an INTERACTIVE check too, and there it is worse

This item is written entirely about `pytest`. The same import lands on any
`.venv/bin/python -c` run from a worktree, and that case is more dangerous for a reason
worth stating plainly: **a test run at least announces which tree it ran in; a one-liner
announces nothing.**

What happened. A resolver fix was made in a worktree and verified there with
`PYTHONPATH="$PWD/src"` — correctly. An hour later the same behaviour was spot-checked
with a bare `.venv/bin/python -c "from bugarach import dataset; dataset.resolve(...)"`,
which imported the PRIMARY checkout, where the fix does not exist because it is still in
an open PR. The call returned the pre-fix answer — the raw DANDI download instead of the
59-recording export — and for several minutes it looked as though an overnight scan had
read the wrong corpus. It had not; that scan used an explicit path. **The check was
wrong, not the run**, and separating the two took reading the scan's own output back.

Why it is worse than the pytest case. The failure **inverts**: code that IS fixed reports
as broken, so the reaction is to go hunting for a defect that does not exist. A session
low on context could plausibly "fix" something already correct, or retract a sound
result. Neither leaves a trace.

It also means **an unmerged fix is invisible to every interactive check on this machine**
— which is the normal state of a worktree. The fix lives on a branch; the interpreter
reads `main`.

Whatever remedy (1)–(3) settles on must cover `python -c` and a scratchpad script, not
only `pytest`. A `conftest.py` guard does not run here at all; a per-worktree venv covers
this case for free. That asymmetry is worth weighing when choosing between them.
