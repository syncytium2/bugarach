---
status: open
filed: 2026-09-03
---

# `show.py` scatters files into a darkroom folder per worktree, not per project

Found by using the tool on the day it was vendored, which is the only way this
surfaces: every check in its own `--selftest` passes.

## What happens

`tools/show.py` derives the darkroom project folder from the **checkout directory
basename**. Run from a worktree, that is the worktree's name:

```
$ cd bugarach-worktrees/vendor-send-goes-nowhere-fresh
$ python3 tools/show.py --no-open docs/learned/three_scoring_rules.png
<darkroom>/vendor-send-goes-nowhere-fresh/three_scoring_rules.png
```

The file was meant for `<darkroom>/bugarach/`. `--project bugarach` places it
correctly, and the selftest even has a case for *"an explicit --project wins"* —
so the override exists because derivation was known to be fallible. What is wrong
is the default.

## Why it matters more here than upstream

**This repo's normal working state is many worktrees at once** — 21 on this machine
today, and `CLAUDE.md` tells every session to make its own rather than share a HEAD.
So the derivation is wrong in the *common* case here, not the edge case. Left as it
is, a week of sessions delivering figures produces a darkroom full of folders named
after branches, each holding one file, and none of them where anybody looks. That is
the same failure the tool exists to end, one level along: the file goes somewhere,
the tool truthfully prints where, and the human still does not find it.

It also silently defeats `bugarach.paths.darkroom()`, which every figure tool in
this repo already routes through, so two delivery paths in one repo would disagree
about where bugarach's darkroom is.

## Do not patch it here

`tools/show.py` is **vendored from armory** (stamp on line 3). The rule in
`CLAUDE.md` is explicit for exactly this case — *"never edit a vendored file in
place"*, and the murderboard-selftest item is the precedent: *"It is a vendored
file: send it back, do not patch it."* Reported to armory rather than fixed locally.

## The fix worth proposing upstream

Derive from the **repository**, not the directory. `git rev-parse --git-common-dir`
answers this correctly from any worktree — it points at the primary checkout's
`.git`, so its parent is the project root whether you are in the primary checkout or
in a worktree of it. `--show-toplevel` does **not** work: in a worktree it returns
the worktree.

Until it lands, a bugarach session using `show.py` should pass `--project bugarach`
explicitly. Worth a line in `CLAUDE.md` only if the upstream fix stalls; a workaround
in a durable doc that outlives the bug is its own defect, and this repo has paid for
that one twice.

## It stalled, and the scattering is what this page predicted

**2026-09-17, found by Tony:** *"you are bugarach why are you posting to the root of
dropbox?"* — two weeks on, `show.py` is unchanged upstream, and the darkroom root held
**five** folders named after worktrees, three of them empty. This page had described
the outcome in the future tense (*"a week of sessions delivering figures produces a
darkroom full of folders named after branches"*); it had happened.

| folder at the root | written | held |
|---|---|---|
| `unsup-rigid-shift-report-residuals` | 2026-09-17 | one PNG, a duplicate of the copy inside the run's claimed folder |
| `unsup-rule-as-code` | 2026-09-16 | three PNGs, one of them a **real-recording lanes figure** (FOUNDATIONS §5 material sitting a level above bugarach's own folder) |
| `turbo-takes-the-width` | 2026-09-12 | two PNGs |
| `ci-covers-the-send-gate`, `ci-covers-the-vendored-two` | 2026-09-02 | empty; another repo's worktrees, same defect |
| `proj` | 2026-09-11 | empty — `show.py --selftest` creates `<review root>/proj` in the **real** darkroom, which is a third defect worth sending upstream with the other two |

Cleaned up the same day: the duplicate was deleted, and `unsup-rule-as-code` and
`turbo-takes-the-width` were moved to `<darkroom>/bugarach/archive/2026-09/strays-from-the-darkroom-root/`,
keeping their folder names so whoever wrote them can still find their files. The empty
folders belonging to other repositories were left alone.

**So the `CLAUDE.md` line is now warranted, and it is mechanized rather than
remembered.** Sapper **SAP016** blocks `python3 tools/show.py <file>` on any line that
does not name `--project`, and `CLAUDE.md`'s darkroom paragraph — which taught the bare
form, and is where this session learned it — now carries the flag and the reason. This
page is excluded from the rule, because it is where the wrong form is shown as wrong.

The prose caution above still holds for the *next* workaround: when upstream lands the
`--git-common-dir` fix, SAP016 and the `CLAUDE.md` sentence come out together.

## Reported upstream, 2026-09-17: syncytium2/armory issue #15

Tony's instruction — report it to armory so the fix is redistributed rather than patched
per consumer. Filed with both defects, the `proj` trace, the estate-wide evidence (five
folders at the darkroom root, one of them from armory's **own** worktree), the consumer
list (12 repositories vendor this file) and the fix in code form. armory is private but
its issues are reachable from this account, which is how the report exists.

**A correction was posted to that issue an hour later, and it is the part worth reading
here.** The report claimed the vendored header misroutes consumer findings, because it
says *"there is nowhere to send a patch"*. armory's own board records that wording as a
**deliberate trade**: it is accurate for the four **public** consumers, of which bugarach
is one — the file cannot point a public reader at a private tracker — and one wording
across all ten consumers is intentional, because a stamp that differs per consumer is a
stamp nobody can verify. So the wording is not the defect. What remains is only the
observable: this page existed for two weeks and did not reach upstream.

**Redistribution is upstream's to sequence, not ours.** `show.py` is pinned across ten
consumers at three shas, and the stamp is what makes a pin checkable, so a fix in armory
reaches bugarach only when someone re-vendors on purpose. Our copy is stamped `e8ffaa3`;
armory's trunk was `548f734` when this was filed, so this repo is already behind by
commits that have nothing to do with this bug. Re-vendoring is a separate decision —
`bash tools/check_vendor_freshness.sh` is the check, and `CLAUDE.md` says never to edit a
vendored file in place.

**What closes this page:** upstream fixes `project_name()` (and, ideally, the copy guard),
bugarach re-vendors, `tests/test_sapper.py` loses SAP016, and the `CLAUDE.md` sentence
about `--project bugarach` comes out with it. Until then the local check is what holds.

---

# Second defect: `show.py` dies on a file that is already in the darkroom

Found 2026-09-03 by the session doing the annotation-and-K work (`derive_k`,
`assess --for-annotation`, K as a percentage), which used the tool because this one
had just told it the tool existed. **Reproduced here in both forms before recording
it.**

```
shutil.SameFileError: '…/darkroom/bugarach/archive/2026-09/three_scoring_rules.png' and
                      '…/darkroom/bugarach/archive/2026-09/three_scoring_rules.png' are the same file
```

`main()` calls `shutil.copy2(src, dest)` unconditionally. When `src` already IS the
file at `dest`, `copyfile` raises rather than treating it as a no-op — an uncaught
traceback, not a message.

## Why this is the common case here, not an edge case

**Every `make_*_figure.py` in this repo defaults its output to the darkroom** — that
is sapper SAP006's whole point. So the natural gesture, *render a figure and then
show it to Tony*, hands `show.py` a path that is already inside the darkroom. The
tool is most likely to crash exactly when it is used for its stated purpose.

Passing the `--also` repo copy works, and is the workaround until this lands.

## The symlink form is the one that will waste somebody's afternoon

The two paths do not have to look alike. `~/Dropbox-<org>` is a **symlink** to
`~/Library/CloudStorage/Dropbox-<org>` — the pair `CLAUDE.md` already warns about
under *"Two paths, one directory"*. Hand `show.py` the symlinked spelling of a file
whose resolved spelling is the destination, and it still raises, with a message
naming two paths that read as different:

```
'/Users/…/Dropbox-<org>/…/bugarach/archive/2026-09/three_scoring_rules.png' and
'/Users/…/Library/CloudStorage/Dropbox-<org>/…/bugarach/archive/2026-09/three_scoring_rules.png'
are the same file
```

`shutil` is right and the message is accurate; it just does not look accurate.

## Read this next to the `--project` defect above

They present identically — a `show.py` invocation that produces no file — so a person
who has read the first half of this page will reasonably assume they got `--project`
wrong. They are unrelated: one puts the file in the wrong folder, the other refuses
to write at all. They were asked to sit together for exactly that reason.

## The fix worth proposing upstream

`os.path.samefile(src, dest)` before the copy, and on a match print the destination
and exit 0 — the file **is** where the tool exists to put it, so the postcondition
already holds and the honest report is the path, not a traceback.

**Guard it by existence, not by exception, and the difference is not cosmetic.**
Write it as:

```python
if dest.exists() and os.path.samefile(src, dest):
    print(dest); return 0
```

**Not** as a `try: … except FileNotFoundError:` around the comparison. `samefile`
calls `os.stat` on both operands and raises `FileNotFoundError` for **either** one
missing — verified, and the two cases are indistinguishable from the exception:

| `samefile(src, dest)` | result |
|---|---|
| dest missing | raises `FileNotFoundError` |
| **src** missing | raises `FileNotFoundError` |
| both present, same file | `True` |

So the try/except form silently treats *"the file you asked me to show does not
exist"* as *"not the same file, carry on"*. That is a worse bug than the one being
fixed: the crash at least stops. The existence check asks the question that is
actually being asked — *is there already a file at the destination* — and leaves a
missing source to fail as a missing source.

This was caught by the workflow-readiness session reviewing the first version of
this page, which proposed the guard without saying which form. Recorded explicitly
because the natural implementation is the wrong one and it looks fine.

Still **not** to be patched here: `tools/show.py` is vendored from armory, stamped on
line 3, and the rule is to send it back. Both defects on this page belong in one
upstream report — and **that report should lead with the symlink form**, not with the
identical-path one. The identical-path case reads as an obvious oversight and invites
a one-line patch; the symlink case is what makes it worth a maintainer's attention,
because the traceback names two absolute paths sharing no visible prefix, so the
reader's first hypothesis is that the tool wrote to the wrong place — which is the
*other* defect on this page. Leading with the cheap half buries the expensive one.
