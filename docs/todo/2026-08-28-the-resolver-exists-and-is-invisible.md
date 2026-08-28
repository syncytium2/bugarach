---
status: done
filed: 2026-08-28
---

# The data resolver exists, works, and a session still ran `find` over the home directory

> **Done, 2026-08-28.** All four fixes shipped. The briefing names the declared export
> and whether it resolves; the unresolved case is an alarm; the search gate went in at
> the **narrow** scope, which is Tony's call recorded below; and the tests were each
> watched failing before they were trusted. What the work changed about the *proposal*
> is at the bottom, under **What shipped, and where it differed**.

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

## What shipped, and where it differed

**1. The briefing line — `tools/session_briefing.sh` §5a, above the darkroom block.**

```
data in: 2026-08-18_revised_2v_periods — dataset.current() resolves it here
```

The name comes from `sed` and only *resolution* pays for a python spawn (~0.2s,
stdlib-only, so it works in a worktree with no venv). That split is the sibling hook's
scar: a message this file exists to deliver must not depend on an interpreter being on a
hook's login PATH.

**It does not print the path, and that is deliberate.** The failure was hand-pathing —
`--folder /Users/…`, four times. `dataset.current()` and `--dataset <name>` both take the
NAME, so printing the path would make copying it the easy road again.
`test_the_input_line_does_not_hand_over_a_path` holds it to that.

**2. The alarm, and it had to shrink.** The unresolved branch was three lines and also
said *"do not hunt with find(1); do not fall back to a .mat store"*. Measured in a fresh
clone with no data and no darkroom — which is what CI is — that put the briefing at
**9,013B against a 9,000B budget**, and 13B over degrades the *whole* payload to TERSE and
takes FOUNDATIONS §9 with it. `a194188` had made the identical cut for §9's own signpost
hours earlier, off the same laptop-versus-CI gap.

So the alarm is one line, and **the corrective moved into the gate**, which fires on the
`find` itself and has no byte budget at all. That is the better home on its merits, and it
generalises: the briefing's job is to make the search unnecessary; the gate's job is to
catch the session that searched anyway. Filed in
[the budget ratchet](2026-08-27-the-briefing-budget-ratchets-the-digest-oscillates.md).
Fresh clone now: **8,878B, 122B of headroom.**

**3. The search gate — narrow, and the false-positive rate is measured, not argued.**
This item called it "the one design question … Tony's call whether the false-positive rate
is worth it." It was put to him with a number instead of a guess. Every Bash command in the
54 bugarach transcripts on this machine — **12,009** — was scored through the real
`grep -E` the hook runs:

| trigger | fires | false positives |
| --- | --- | --- |
| **shipped:** a line-leading `find`/`ls`/`tree` naming `exports/`, `processed_archive` or `/data` | **30 (0.25%)** | **0**, all 30 read by hand |
| same, but allowing the verb after `;` or `&&` | 140 (1.17%) | many, incl. a heredoc writing a todo |
| any `find` rooted at the home directory | 46 | 23 — about 50% |

All 30 are sessions locating the data root, listing export folders, or counting a store's
slices. Not one is unrelated work. **Tony chose the narrow scope.**

Two things the measurement changed. It **must sit above** the read-only-verb opt-out that
exempts `find`/`ls` — that exemption is right for the store branch and is exactly what hid
this one, so `test_the_search_gate_outranks_the_read_only_verb_exemption` asserts the
order, because getting it wrong leaves every other test passing and the gate silent. And
the block offers **`data_root()` as well as `current()`**: six of the thirty were hunting
the raw `2R` acquisition folders or the lab workbook, which the export folder is not the
answer to. Opt-out: `BUGARACH_DATA_OK=1`.

**4. Tests — and each was watched failing first.** Five regressions were driven through a
copy of the tree before the guards were trusted: the line dropped; the path printed instead
of the name; the alarm going quiet with the data unmounted; the `find(1)` corrective
creeping back into the budgeted payload; the search check sinking below the exemption.
`tests/test_session_briefing.py` and `tests/test_where_the_data_are.py`, plus 11 new probes
in the gate's own `--selftest`.

**SAP004 caught this work's own test fixtures.** The gate probes were first written with a
home-directory-shaped root, because that is the shape of the command being caught; sapper
blocked the commit and they became `/mnt/lab/…`. The rule earned its keep on the very
change written to respect it — and then blocked this paragraph's first draft too, for
quoting the offending path.

**What was NOT done, per this item's own instructions:** nothing added to CLAUDE.md, no
path in the repo, no `--store` alias widened, `_quarantine/` and `processed_archive/`
untouched.

## Why this is a todo and not a root `HANDOFF.md`

`tests/test_handoff_is_honest.py` requires a root handoff to name an **open PR**
near the top, and checks in CI that the PR is still open. Nothing is in flight for
this — no branch, no PR, no half-done work. A root handoff here would be the exact
false positive that guard exists to catch, and that `docs/handoffs/README.md`
records four days of.
