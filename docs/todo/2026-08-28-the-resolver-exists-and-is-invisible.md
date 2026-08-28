---
status: open
filed: 2026-08-28
---

# The data resolver exists, works, and a session still ran `find` over the home directory

**Do not build a resolver. There is one, and it is correct.** This item is about
why it did not get used, one day after it shipped.

## What happened

On **2026-08-27** a session lost track of where the data lived and began
re-deriving it from a `.mat` store. The permanent fix Tony asked for —
*"claude.md is unreliable. help me fix this permanently."* — was built the same
day, and it is good work:

- `current_export.toml` at the repo root **declares** which export folder is the
  input, by name, with recording counts and a note per role. It replaced an answer
  that previously had to be triangulated from four disagreeing places.
- `bugarach.dataset.current()` resolves that name on whatever machine it is run on.
- `.claude/hooks/the-folder-is-the-input.sh` is a wired `PreToolUse(Bash)` gate that
  intercepts a session reaching for a store and answers with the folder instead.
- Sapper SAP007 blocks store reads in `src/**` and `tools/**`, exclusion list empty.

On **2026-08-28**, one day later, a session (this one) needed the real recording to
rebuild `docs/generator/reality_check.png`, did not know where it was, and ran:

```
find <home> -maxdepth 6 -type d -name "exports"     # the literal home path, redacted per SAP004
```

It then passed the discovered absolute path to `--folder` by hand, and did so
**four separate times** over the session. Every one of those runs read the correct
folder — by luck and by reading the directory listing, not because anything told
it which folder was current.

Verified on this machine today, and this is the point:

```
$ python -c "from bugarach import dataset as ds; print(ds.current())"
<data root>/exports/bugarach/2026-08-18_revised_2v_periods    # exactly right
```

`BUGARACH_DATA_ROOT` is **unset** here and it did not matter — `data_root()` found
the Dropbox mount by itself. The call would have worked the first time, instantly,
with no search and no guessing.

## The actual defect

**The mechanism is invisible at the moment of need.** Every part of it addresses a
session that has already decided to read a store. None of it reaches a session that
simply does not know where the data is and reaches for the filesystem.

- The **hook** fires on store access. `find` is not store access, so it stayed
  silent — correctly, by its own design.
- **SAP007** greps what a commit adds. An interactive `--folder /Users/...` never
  gets committed, so it never sees it — its own header says so.
- The **session briefing** prints where output goes (`darkroom: $BUGARACH_DARKROOM
  -> ...`) and says nothing about where input comes from. That asymmetry is the
  whole bug: the write path is announced unprompted, the read path is not.
- **CLAUDE.md** mentions "the export folders under `<data>/exports/bugarach/`" in a
  machine-local inventory — descriptive prose, in a document Tony has already
  ruled unreliable for exactly this, and it does not name `dataset.current()`.

So: a session is told where to put things and left to find where to get them.

## The fix

Symmetry with the darkroom, which already works this way and does not have this
problem:

1. **A briefing line.** One line, next to the darkroom line, in
   `tools/session_briefing.sh` — the folder `dataset.current_name()` declares, and
   whether `dataset.current()` resolves it on this machine. `current_name()` reads
   no filesystem, so it prints on a machine with the data unmounted and says so
   rather than going quiet. Note the briefing has a **byte budget** and a canary;
   this line is small, but read `briefing_budget()` before adding it, and add it to
   the *bounded alarms* block rather than the budgeted one.
2. **A fixed alarm when it does not resolve.** Mounted-but-wrong is the dangerous
   state, and it is exactly where a session starts inventing.
3. **Consider a second `PreToolUse` pattern** on `find`/`ls`/`glob` aimed at the
   home directory or `exports`, answering the same way the store hook answers. This
   is the one design question in this item: it may be too noisy, and it is Tony's
   call whether the false-positive rate is worth it. The store hook's own argument —
   *see the attempt, not the wreckage* — applies unchanged.
4. **A test** that the briefing names the declared folder, in
   `tests/test_session_briefing.sh` or its pytest wrapper, so the line cannot be
   dropped in a future budget squeeze the way the whole board was in August.

## What NOT to do

- **Do not add a paragraph to CLAUDE.md.** That was already offered, rejected in
  words, and the rejection is quoted in two files that shipped because of it.
- **Do not put a path in the repo.** `current_export.toml` names folders, never
  paths, and sapper **SAP004** blocks any absolute home directory — it would fail
  the commit, correctly. The per-machine half is not a repo fact.
- **Do not add `--store` anywhere**, or widen `_dataset_arg`'s aliases on a
  folder-only tool. `tools/_dataset_arg.py` explains why in its own docstring.
- **Do not touch `_quarantine/`** or `processed_archive/`. `current_export.toml`
  names both as non-inputs precisely so "it was not in the list" can never be the
  reason someone goes looking in the store.

## Where everything is

| what | where |
| --- | --- |
| declares the current folder | `current_export.toml` (repo root) |
| resolves it | `bugarach.dataset` — `current()`, `current_name()`, `data_root()`, `resolve()` |
| the shared CLI flag | `tools/_dataset_arg.py` — `add()` / `get()`, one `--dataset` for every analysis |
| the store gate | `.claude/hooks/the-folder-is-the-input.sh`, wired in `.claude/settings.json` |
| the briefing to edit | `tools/session_briefing.sh` — darkroom block is the template to copy |
| the contract | `docs/export_folder_spec.md` (revision 6) |
| tests already guarding this | `tests/test_current_export.py`, and SAP004/SAP007 in `tools/sapper.py` |

## Why this is a todo and not a root `HANDOFF.md`

`tests/test_handoff_is_honest.py` requires a root handoff to name an **open PR**
near the top, and checks in CI that the PR is still open. Nothing is in flight for
this — no branch, no PR, no half-done work. A root handoff here would be the exact
false positive that guard exists to catch, and that `docs/handoffs/README.md`
records four days of.
