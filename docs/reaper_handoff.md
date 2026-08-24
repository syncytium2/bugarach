# The worktree reaper — a rule interface2 can implement, not a script it can run

Worktrees pile up because **nothing collects them at the moment they stop being
useful**, and that moment is not when a session ends. This is the rule bugarach used to
stop the growth, the decision function that implements it, and the two constraints
interface2's own history imposes on anything that deletes a worktree.

**It is not a vendoring drop.** bugarach's implementation is a `gh` wrapper on GitHub
pull requests; interface2 is on GitLab and shows no pull-request merge in the subjects of
its last 300 commits. Copying the file would give you a script that cannot run.

**From:** `syncytium2/bugarach` @ `7813613` (2026-08-23). The implementation landed as
PRs #240 and #241. bugarach's package version string was `0.0.1` when this was written (0.1.0 was cut the same day), so
the sha is the only provenance worth quoting.

---

## 1. The finding

Measured in bugarach on 2026-08-23, across the 27 non-primary worktrees on one machine.
**Time from a worktree's creation to the last time anything wrote in it**, in minutes:

```
under 20 min  13  #############
20–60 min      1  #
1–4 h          2  ##
4–24 h         7  #######
over a day     4  ####

n = 27   median 37 min   p25 5 min   p75 750 min   mean 825 min
```

The raw per-worktree pairs and the script that reduces them are committed at
`docs/reviews/reaper_handoff_2026-08-23_worktree_lifetimes.csv` — every number above is
re-derivable, though the population itself is gone.

The shape matters more than any single number, which is why the buckets are here and
not just a median. **Half the worktrees on the machine were used for under twenty
minutes** — created for one task, one branch, never written to again; the shortest
three were finished inside the minute they were made. The rest are session-scale, hours
to days. Almost nothing lives in between.

Note the mean, 825 minutes, against the median of 37. A summary statistic quoted alone
would have described no worktree that actually existed.

Two more counts from the same day:

- 28 worktrees at 16:34, of which **17 were merged, clean and idle** — removable by
  every fact git can produce.
- Between 09:45 and 16:34 the worktree count went **21 → 28**, while ACTIVE claims on
  the session board went **8 → 3**.

That last pair is the diagnosis. Same sessions, same load, opposite directions. Board
claims are gated — a pre-commit hook refuses a commit from a worktree with no block —
and they were maintained. Worktree removal was gated by nothing, documented as step 5 of
a workflow document, and it leaked. **The tree is a record of which rules were mechanized
and which were written down.**

And cleanup-at-session-end cannot work even for the long mode. A session is unbounded;
half these worktrees were done inside twenty minutes. Anything deferred to "session end"
is deferred past the end of the thing that knew about it.

### The same leak in interface2, measured

From a read-only survey of `~/Developer/interface2` on 2026-08-23, at `c711e737`:

- **35 worktrees**, of which **19** (excluding the primary checkout) have branches that
  are already ancestors of `origin/main` **and** clean working trees.
- No merge gate, no sweep, no reaper — neither of bugarach's tools exists there.

Those 19 are the same object as bugarach's 17. It is a snapshot; **re-run the count
before acting on it**, with the command in §7.

---

## 2. The rule

> **The process that observes the landing removes the worktree.**

Not a session at its end, not a sweep the next morning. Whatever step makes your branch
an ancestor of `origin/main` is awake at the exact moment the worktree becomes
disposable, and it knows which worktree that is without asking anyone.

In bugarach that step is `tools/merge_when_green.sh`, which blocks polling CI until the
pull request merges; the reaper hangs off its exit-0 path.

**Where that step is in interface2 is for you to confirm.** What was observed from
outside: no commit subject in the last 300 on `main` is a pull-request merge; 22 of the
last 100 commits *are* merge commits, and their subjects are `origin/main` merged **into
a branch**, not a branch merged into `main`; and your `CLAUDE.md` says never to commit on
`main` directly. Read together, that says a branch catches up and then reaches `main` by
fast-forward, locally, in a step a session performs. If so, the moment is sharper than
bugarach's: no CI wait, and the session is standing in the worktree when it happens.
**This is inference from the shape of the history — nobody watched a branch land — and
you are far better placed to check it than we were.**

---

## 3. Why a sweep is not the answer, and why this is different

bugarach has a sweep — `tools/worktree_sweep.sh` — and it is currently **the tool nobody
may run.** It decides removability from git state alone: merged, clean, untouched for
some hours. Every fact it checks is correct. It reads neither session board, so a
worktree that is merged, clean and idle may belong to a session that landed one branch
and is about to open the next from the same directory. A dry run on the morning of
2026-08-23 offered **27** worktrees for deletion, at least three of which held ACTIVE
claims at that moment. (That was before the session in question removed its own by name;
by 16:34 the same command offered 17 out of 28. The population moves all day — take
neither figure as standing.) It is filed at
`docs/todo/2026-08-23-the-worktree-sweep-does-not-read-the-board.md` and the honest
workflow meanwhile is to remove your own by name.

The reaper does not inherit that problem, and the reason is worth stating precisely:

> **It removes exactly one thing — the worktree you are standing in, on the branch that
> just landed. It never scans. It never judges a directory it did not create.**

Intent is the thing a sweep cannot see. The reaper never needs to see it, because the
only intent in play is the caller's own, and the caller just landed the branch.

**This does not replace a sweep.** It stops the growth; it collects nothing that leaked
before it existed and nothing a crashed session leaves behind. Both repos still need a
collector for the backlog, and that collector still has to read the board. Build one
collector, not two — the reaper and the sweep share their notion of "clean", "primary"
and "merged", and the two implementations drifting apart is a defect waiting to happen.

---

## 4. The decision function

Six facts in, one word out. Pure: no network, no forge API, no filesystem, no board.
This is the part that vendors verbatim, and it is reproduced here byte-for-byte from
`tools/merge_when_green.sh`:

```bash
# $1 self  $2 primary  $3 branch  $4 pr-head-branch  $5 merged  $6 dirty-count
reap_verdict() {
  local self="$1" primary="$2" branch="$3" head="$4" merged="$5" dirty="$6"
  if [ -z "$self" ];                              then echo "SKIP:not-a-worktree"; return; fi
  if [ "$self" = "$primary" ];                    then echo "SKIP:primary";        return; fi
  if [ -z "$branch" ] || [ "$branch" = DETACHED ]; then echo "SKIP:detached";       return; fi
  if [ -z "$head" ];                              then echo "SKIP:unknown-head";   return; fi
  if [ "$branch" != "$head" ];                    then echo "SKIP:other-branch";   return; fi
  if [ "$merged" != yes ];                        then echo "SKIP:not-merged";     return; fi
  if [ "$dirty" != 0 ];                           then echo "SKIP:dirty";          return; fi
  echo REAP
}
```

**The ordering is the design, not tidiness.** Identity questions — *is this even mine?*
— come before state questions — *is it finished?*. A session that lands a colleague's
branch from inside its own worktree has a worktree that is merged, clean and idle by
every fact git can produce, and is **not finished**. Check state first and you have
rebuilt the sweep's bug inside the safe tool. bugarach pins the ordering with a test
named for it.

Three of the seven refusals exist because a *check* can fail rather than a worktree:

- `SKIP:not-a-worktree` — `rev-parse` gave nothing.
- `SKIP:unknown-head` — the landing step could not name the branch it landed. Refusing
  to guess is the point: an unanswerable question must not resolve to "delete".
- `SKIP:not-merged` — the ancestry check said no, whatever anything else claimed.

That last one matters more than it looks. A green light from your forge is a report; an
`is-ancestor` against the ref you just pushed is a proof. bugarach has already been
bitten by trusting the report — for one entire session every pull request merged about
ninety seconds *before* its own CI finished, and they all happened to pass, so nothing
looked wrong.

### Facts to feed it

| argument | how bugarach gets it |
|---|---|
| `self` | `git rev-parse --show-toplevel` |
| `primary` | first row of `git worktree list --porcelain` — **not** `--show-toplevel`, which answers "the worktree I am standing in"; that mistake once made the sweep offer to delete the primary checkout |
| `branch` | `git symbolic-ref --quiet --short HEAD`, else `DETACHED` |
| `head` | the branch the landing step actually landed |
| `merged` | `git fetch -q origin` then `git merge-base --is-ancestor "$branch" "$TRUNK"` |
| `dirty` | `git -C "$self" status --porcelain \| wc -l` |

Throughout, **the primary checkout is the first row of `git worktree list`** — the
working tree you happen to be standing in is a different question, and confusing the two
is how a collector offers to delete the main checkout.

**`TRUNK` must be a parameter, not the literal `origin/main`.** bugarach hardcodes it and
gets away with it. In this family of repos `fireflies` reports a default branch of
`origin/precomputed-rejection` and `coding-project` uses `origin/master`. Resolve it, or
take it as an argument, and fail closed when you cannot.

---

## 5. What interface2 must add that bugarach does not have

### 5.1 A restore ledger — required by your own standard

Your `CLAUDE.md` closed the DO-NOT-PRUNE freeze on 2026-08-04 with a condition attached:

> verify a tip is an ancestor of `origin/main` in the **SAME LOOP** that removes it, and
> **leave a restore ledger in git**.

bugarach's reaper satisfies the first half exactly — the `is-ancestor` check is three
lines above the removal, in the same function, on the same facts. It satisfies **none**
of the second. It deletes and prints; nothing is written down.

So a faithful interface2 implementation is bugarach's plus a ledger: branch name, tip
sha and date, appended to a tracked file and committed. Cheap, and it converts an
irreversible act into a recoverable one — the tip is already on `main`, so the ledger is
what lets a person find *which* commit a directory corresponded to without archaeology.

### 5.2 Do not pitch this as briefing speed

Your `CLAUDE.md` measured it: pruning worktrees is worth about **2 s of a ~56 s**
briefing, and the only lever that ever worked was architectural. **SAP032 fires if the
claim is written again.** This proposal is not a performance argument and must not be
filed as one.

The case is legibility, and it is your own sentence: *a live worktree and an abandoned
one look identical.* A session reading the worktree list to find out who else is working
cannot tell last week's landed branch from a colleague mid-edit, so it either stomps or
freezes. In bugarach both happened in a single day — one session read a worktree that was
actively being written to as "unpushed and at risk", another concluded nobody was working
on CI while somebody was. The list is only worth reading if presence *means* something.
After this, presence means **not yet landed**.

### 5.3 Ignored files are destroyed and no dirty-check can see them

`git worktree remove` deletes ignored files, and `git status --porcelain` does not report
them, so the clean check above is blind to exactly what is about to be lost. Verified
directly in a scratch repository: a worktree whose only content was an ignored build
directory reported clean and was removed without complaint.

In bugarach that is a built `site/` and `__pycache__` — regenerable, so the reaper counts
them in its output rather than leaving them to be discovered. **Check what it is for you
before enabling anything.** A repo whose worktrees hold ignored artifacts that are
expensive or irreproducible needs that to be a refusal, not a footnote.

---

## 6. Failure directions, stated plainly

Every judgement call points the same way:

| the question | if it cannot be answered | why |
|---|---|---|
| which branch landed? | KEEP | an unanswerable question must not resolve to "delete" |
| is it an ancestor of trunk? | KEEP | absence of proof is not proof |
| is the tree clean? | KEEP | uncommitted work is unrecoverable |
| is this my branch? | KEEP | somebody else's landing says nothing about my worktree |
| can I reach the primary checkout? | KEEP | nowhere safe to remove from |
| did `git worktree remove` fail? | KEEP, and say so | git had a reason |

And: **a refusal is never a failure.** The landing already happened; the exit status
belongs to the landing. A worktree that was kept is not a branch that did not land, and
conflating them will get the whole thing switched off.

---

## 7. Evaluating it before you build it

Count what a reaper would have collected, without changing anything. **The first row of
`git worktree list` is the primary checkout and must be skipped** — an earlier draft of
this snippet counted it, which is the same bug §4 warns about:

```bash
cd ~/Developer/interface2
git fetch -q origin
primary=$(git worktree list --porcelain | awk '/^worktree /{print $2; exit}')
git worktree list --porcelain |
  awk '/^worktree /{w=$2} /^branch /{sub("refs/heads/","",$2); print w"\t"$2}' |
while IFS=$'\t' read -r w b; do
  [ "$w" = "$primary" ] && continue
  if git merge-base --is-ancestor "$b" origin/main 2>/dev/null; then
    printf '%s\tdirty=%s\n' "$(basename "$w")" "$(git -C "$w" status --porcelain | wc -l | tr -d ' ')"
  fi
done
```

Every row with `dirty=0` is one this would have removed at its landing. That number
against your worktree total is the whole business case; if it is small, do not build
this.

Then decide **where your landing step is** — the one place a branch becomes an ancestor
of `main`. If there is more than one such place, or if it is a bare `git push`, the honest
options are to give landing a single entry point first, or to attach the reaper to a
`post-merge`/`pre-push`-style hook and accept that it fires on more paths than
bugarach's does. bugarach had the entry point already, which is most of why this was
cheap there: PR #240 was 140 lines of tool and 165 of tests, 340 insertions in all.

---

## 8. What bugarach proved, and what it did not

**Proved.** Both pull requests that introduced the reaper were landed **by the reaper**,
run from inside the worktree it then deleted. It merged, verified ancestry, verified
clean, removed the directory, deleted the branch, and reported what it destroyed. Since
then no worktree from that session has been left behind. Nine decisions fire in a
`--selftest` with no git tree and no network; the test suite sources the script as a
library and drives the real removal against a scratch repository, where a directory
genuinely does and does not get deleted.

**Not proved.** It has existed for hours, not weeks. Nobody has hit the `other-branch`
case in anger — it is covered by a test and by argument, not by an incident. Nothing is
known about how it behaves when two sessions land branches in the same minute, or on
Windows/WSL, where bugarach does not run it. The population behind §1 is one machine,
one repo, one operator's working style, measured once; the worktrees it describes have
since been collected, so that exact measurement cannot be repeated.

**And the first version of this document got its own headline number wrong** — it
reported a ten-minute median, which was the median of the short mode, not of the
distribution. The bucket table in §1 is there because the single number was not
recoverable from the claim. Treat every figure here as bugarach's, and **measure your
own**; §7 is how.

---

## 9. If you implement it, tell us

bugarach would take the restore ledger back — it is the better design and the reason is
your incident, not ours. The channel that already exists runs the other way (bugarach
vendors `session_protocol.md` and the session-start hook *from* interface2), so the
natural home for the rule in §2 is that protocol document, where it reaches every repo
that vendors it without anyone exporting a shell script.
