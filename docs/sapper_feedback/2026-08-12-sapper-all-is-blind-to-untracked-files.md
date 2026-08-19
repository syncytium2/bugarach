---
rule: SAP004
status: open
filed: 2026-08-12
---

# `sapper --all` reported clear on a file it never read, and a personal path reached a public `main`

**Recurred 2026-08-18** — see *It happened again* at the foot of this file. Still open,
still the natural workflow, and this time the only thing that caught it was a gate that
is opt-in per clone.

## What happened

Installing the murderboard harness (2026-08-12) I vendored four files, then ran
`python tools/sapper.py --all` as the pre-commit check. It printed **`sapper:
clear`**. I committed, opened PR #2, and merged it to `main`.

Minutes later, on the *next* branch, the same command printed:

```
BLOCK SAP004 tools/fetch_paper.py:117:
  os.path.join(home, "<INSTITUTION> Dropbox", "<PERSON>"),
```

Nothing about the file had changed between the two runs. What changed is that it
had become **tracked**.

`_tracked_files()` is `git ls-files`. `--all` therefore scans the index, not the
working tree, and a newly vendored file that has not yet been `git add`ed is
**invisible to it**. The natural workflow — write files, run the checker, commit
— is exactly the order in which the checker cannot see them.

The result: an institution name and a person's name reached the `main` branch of
a **public** repository, which is the precise incident class SAP004 and
FOUNDATIONS §5 exist to prevent ("public-repo scrub incident 2026-08-11").

## Why it is wrong

- **`clear` overstated what was checked.** Silence is read as "nothing to fix",
  not "nothing was examined". The failure mode is a confident all-clear, which is
  worse than an error — an error gets investigated.
- **The one gate that would have caught it was off.** `--staged` reads the index
  at commit time and would have blocked. It only fires via
  `git config core.hooksPath .githooks`, which is opt-in and **was not set in
  this clone** (now set). A BLOCK rule guarding a public repo should not depend
  on a per-clone config nobody is reminded about.
- Vendoring makes this materially more likely, not less: vendored files arrive in
  bulk, from a codebase written under *different* assumptions (murderboard's own
  CLAUDE.md permits calcium-imaging back-compat branches in `fetch_paper.py`),
  and nobody reads 482 lines of a file they did not write.

## Suggested fix

Two changes, both small:

1. **Make `--all` mean all.** Scan `git ls-files` **plus** untracked,
   non-ignored files (`git ls-files --others --exclude-standard`). That is the
   set a commit could plausibly add, and it matches what the word promises. If
   the wider scope is unwanted by default, add `--worktree` and have the CI/test
   path use it — but the default should not be the narrower one, because the
   default is what people run by hand.
2. **Say what was scanned.** `sapper: clear (N files)` instead of bare `clear`.
   A count that reads `clear (0 files)` or one obviously too small is
   self-diagnosing; bare `clear` is not.

Optionally: have `--selftest` assert that a rule fires on an untracked fixture,
so this specific blindness cannot come back silently.

## Immediate remediation taken

- `tools/fetch_paper.py` **removed** from the repo (not patched — editing a
  vendored file in place creates the drift the provenance stamps exist to
  prevent, and bugarach does not need the lit tool; the deviation is documented
  in `CLAUDE.md`).
- `core.hooksPath` set to `.githooks` in this clone.
- Reported upstream-facing detail in
  [`../todo/2026-08-12-vendored-lit-tool-carries-personal-paths.md`](../todo/2026-08-12-vendored-lit-tool-carries-personal-paths.md).

**Still open and NOT decided by me:** the string is in `main`'s history and was
pushed to a public remote. Removing it from history is a rewrite, which
`CLAUDE.md` requires explicit confirmation in words to perform. Flagged for
Tony — see the todo above.


## It happened again, 2026-08-18

Writing `src/bugarach/assembly.py` (new file, not yet added), I ran
`python tools/sapper.py --all` as the check before committing. **`sapper: clear`.**
The commit then failed at the pre-commit hook:

```
BLOCK SAP002 src/bugarach/assembly.py:287: rng = np.random.default_rng(seed)
```

Confirmed deliberately afterwards: drop a file containing `np.random.default_rng(7)`
into `src/bugarach/`, leave it untracked, and `--all` still reports `clear`.

Two things this second instance adds:

- **It is not vendoring-specific.** The 2026-08-12 report reasonably framed this
  around bulk-vendored files nobody reads. This was a file I had just written
  myself, in the ordinary write → check → commit order. Any new module is exposed.
- **What caught it was the opt-in gate.** `--staged` fired only because
  `core.hooksPath` happens to be set in this worktree. The 2026-08-12 report already
  says a BLOCK rule should not depend on a per-clone config; a second incident caught
  *only* by that config is the evidence for it. There is a standing todo on the
  config itself: [`../todo/2026-08-13-hookspath-is-opt-in-per-clone.md`](../todo/2026-08-13-hookspath-is-opt-in-per-clone.md).

Suggested fix 2 from above — printing the file count — would have been enough on its
own here. `sapper: clear (0 files)` immediately after writing a new module is
self-evidently wrong; bare `clear` read as confirmation.

No violation reached `main` this time: the hook blocked the commit, the RNG was
switched to `RandomState` per FOUNDATIONS §2, and the tree is clear on both `--all`
and `--staged`.
