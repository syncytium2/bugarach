---
status: open
filed: 2026-08-15
---

# A worktree's tests import `main`'s library, and nothing says so

The `.venv` lives in the primary checkout and was created with `pip install -e`,
so `bugarach` resolves to `/…/bugarach/src` — **the primary checkout, whatever
branch it happens to be on** — no matter which worktree the interpreter is
invoked from. Every other worktree therefore runs *its own tests* against
*`main`'s source*.

It fails silently and in the most convincing possible way: the suite passes, the
figures render, and the numbers look right. It was caught only because a rendered
figure disagreed with the branch's code — the lane labels showed `CIC` and
`coact` where `diagnostic.py` on that branch clearly asked for `TITLES`, which
maps to `CICADA` and `CoactDetect`.

## What it cost, concretely

Landing `rewrite-generator-doc`, a session reported "344 passed, sapper clear" as
evidence the branch was green. That run had imported `main`'s library and proved
nothing about the branch. Re-run correctly it was *also* 344 passed — so the
claim happened to be true and was entirely unearned, which is the worst outcome,
because nothing would have contradicted it.

The same session then rebuilt the site's hero figure from that worktree and got
`main`'s render, and nearly rewrote the caption to match a figure the branch does
not produce.

**It cost again on 2026-08-24, on the same map, in both directions.** Renaming the
sixth detector's label (`TITLES["cicada"]`, CICADA → locust, ADR-0002) was checked
with a full local suite that came back green — and could not have come back
anything else, because `bugarach.ui.app` resolved to the primary checkout, where
the label still said `CICADA`. So `test_make_diagnostic_refuses.py` asserted
CICADA against a report built from `main`'s `TITLES`, agreed with itself, and
passed. **CI, running one checkout, failed both of its label assertions**, and the
branch went red after a session had said it was green.

Then the mirror image: after fixing the tests to expect `locust`, they **fail
locally** — the report still says CICADA — and are correct. So in this worktree
the label tests are green when wrong and red when right, and neither result means
anything. Any branch that touches a display string is in this position and cannot
tell from a local run.

Worth noting what caught it in 2026-08-15 and what caught it now: the first time,
lane labels showing `CIC` where `TITLES` said `CICADA`. The second time, the same
dictionary. **This trap has now fired twice on the same three lines of code.**

## The workaround that works today

```bash
PYTHONPATH=src python -m pytest -q          # from the worktree root
PYTHONPATH=src python tools/build_site.py   # env is inherited by subprocesses
```

Verify it took, rather than trusting it:

```bash
PYTHONPATH=src python -c "import bugarach; print(bugarach.__file__)"
```

## What to actually do

Options, roughly in order of preference:

1. **A `.venv` per worktree.** Correct and boring; costs disk and a rebuild per
   worktree (`python3 -m venv .venv && pip install -e ".[dev]"`).
2. **A `conftest.py` guard** that fails the run when `bugarach.__file__` is not
   under the rootdir. Cheap, catches it everywhere pytest runs, and turns a
   silent wrong answer into a red test — the shape this repo already prefers.
3. **A sapper rule** — poor fit: sapper reads files, and this is a property of
   the interpreter's import state, not of any file's contents.

Option 2 is the one that fires by itself, which is the test this repo applies to
every other gate. It also generalizes: the same guard catches a stale editable
install pointing at a deleted path.

## It is worse than "a worktree imports the wrong `src`": the answer depends on test order

Measured 2026-09-01, in `bugarach-worktrees/walk-the-built-pages`, same commit:

```
pytest tests/test_architectures_are_files.py                  ->  2 failed, 2 passed
pytest tests/test_architecture_diagram_is_current.py \
       tests/test_architectures_are_files.py                  ->  6 passed
```

**Same tests, same worktree, opposite verdicts.** Whichever file imports
`bugarach` first decides which `src` the whole session resolves; after that it is
in `sys.modules` and no later `sys.path` change can move it.
`tools/make_architecture_diagram.py` does `sys.path.insert(0, ROOT / "src")` at
import, so a test that imports it early pins the **worktree's** copy and every
later test agrees — while a run that reaches `bugarach` by another route first
pins the **primary checkout's**.

That upgrades the defect. A consistently wrong answer is a hazard people learn
once. An order-dependent one is a flake: two sessions run the same suite in the
same worktree, get different results, and each has grounds to think the other
misread something. It cuts both ways — `draughtsman` hit the mirror image the same
day, its branch green when the arch test ran first and red when it ran alone, and
correctly reported that as an order dependency rather than as a fix.

**This argues for option 2's urgency, not for a new option.** A `conftest.py`
guard asserting `bugarach.__file__` lives under the rootdir fires at collection,
before ordering can matter, and turns both directions into one loud failure
instead of two quiet disagreements.

Until then, the working rule: **a green suite in a worktree is not evidence unless
it also ran in the primary checkout**, and a red `test_architectures_are_files.py`
in a worktree is this, not your branch.

## Related

The session protocol already says to work in your own worktree
([`session_protocol.md`](../session_protocol.md)), and the SessionStart hook
prints that advice on every start. Following that advice is what exposes you to
this. Worth a line in the briefing until it is fixed.
