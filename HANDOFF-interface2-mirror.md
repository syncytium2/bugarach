# Handoff — mirror interface2 to GitHub, private, before anything is curated

> **For a Claude Code session on WSMIP065.** Written 2026-09-18 by the cloud session
> `Orchestration goals tracking`, on Tony's instruction. **Working material, not murderboarded** —
> same standing as the other root handoffs. Every fact below either links the file that owns it or
> says how to derive it; the linked file wins.
>
> When this work lands, this file leaves the root: delete it if spent, or move it to
> [`docs/handoffs/`](docs/handoffs/README.md) if anything in it is still worth reading.

## The decision this implements

Tony, 2026-09-18, asked whether to transfer the whole GitLab repository now and pick it apart for
the sub-goals later. **Yes, and the order is the point.**

A mirror is **additive and reversible** — if it is wrong, delete the repository and push again.
Curation is **subtractive and lossy**, and doing it without a preserved source is a one-way door.
So the copy comes first and every selection decision comes after, against a source that is already
safe.

It also retires the risk that prompted the goal — losing GitLab access — **today**, rather than at
the end of a curation project.

## Scope

**In scope:** one complete, private copy of interface2 on GitHub, verified complete, attached to the
estate so sessions can read it.

**Out of scope, deliberately:** choosing what a paper shows, rewriting history, scrubbing anything,
making anything public, and retiring the GitLab remote. Those are the later sub-goals and each one
needs the mirror to exist first.

## Before you start

1. **Claim it.** This creates a repository under Tony's account — a shared, world-adjacent output.
   Put a block on [`docs/SESSIONS.md`](docs/SESSIONS.md) before the first push, not after, and one
   on the machine-local board (`tools/guard_local_board.sh --path` prints where). `Holds:` names the
   new GitHub repository until this is done.
2. **Take a worktree.** armory's isolation rule: worktree per session, branch per worktree, pushed on
   creation; never `checkout -b` in a shared checkout, and **never `git add -A`** — the session
   writing this handoff staged an unresolved merge that way the same morning and pushed conflict
   markers.
3. **Derive the remote; do not transcribe it.** From the interface2 checkout:

   ```
   git remote get-url origin
   ```

   The URL carries a personal namespace and this repository is public, so it is read at run time and
   not written down here.
4. **Check the room.** `CNMF_E` is in that tree, so the clone is not small. Confirm free disk before
   starting, and confirm whether Git LFS is in use — `git lfs env` in the checkout, and look for
   `.gitattributes` lines naming `filter=lfs`.

## The procedure

**Step 1 — a complete local copy.** A working clone is not enough; `--mirror` is what carries every
ref.

```
git clone --mirror "$(git -C <interface2 checkout> remote get-url origin)" interface2.git
```

If LFS is in use, the objects are not in that clone:

```
cd interface2.git && git lfs fetch --all
```

**Step 2 — the empty private repository.** `syncytium2/interface2` is free — checked 2026-09-17, it
resolves to nothing. **Private.** Create it empty: no README, no licence, no `.gitignore`. Anything
GitHub adds is a commit the mirror push will have to reconcile.

**Step 3 — push.**

```
git push --mirror https://github.com/syncytium2/interface2.git
```

⚠ **`push --mirror` makes the target match the source exactly, including deleting refs the source
does not have.** Against the empty repository from step 2 that is safe and is why step 2 says empty.
Never aim it at a repository that already holds anything.

## Verification — what "complete" means, and it is checkable

Do not report this done on the push exiting zero. Compare both sides:

```
# counts, source then target
git -C interface2.git rev-list --all --count
git -C interface2.git for-each-ref --format='%(refname)' | wc -l

git ls-remote --heads https://github.com/syncytium2/interface2.git | wc -l
git ls-remote --tags  https://github.com/syncytium2/interface2.git | wc -l
```

Branch and tag counts must match the mirror clone. Then one content check that matters for this
estate specifically:

**The stranded tools must be present.** armory's scan found **35 of the estate's 44 stranded tools —
committed on a branch, never merged — live in interface2**, and they are the part a non-mirror
transfer silently loses. Derive the list from armory and confirm each path resolves on some branch of
the new remote:

```
python3 -c "import json;m=json.load(open('MANIFEST.json'));\
rows=m if isinstance(m,list) else m.get('tools') or m.get('entries') or [];\
print('\n'.join(r.get('origin_path') or r.get('path','') for r in rows \
if isinstance(r,dict) and r.get('repo')=='interface2' and r.get('status')=='stranded'))"
```

Record the three numbers and the stranded check in the board block. A mirror nobody counted is a
backup nobody tested.

## The gate — do not make it public, and that is a separate decision

**Private on creation, private after verification, and "make it public" is its own ruling with its own
review.** Three things are known to be in that history:

- **Its commit prose reads as a second laboratory.** Messages say *"the other team's detector #5"* and
  *"for the CoactDetect team's integration"*. From outside this estate that says another laboratory
  wrote LoCo. It does not — Tony, 2026-08-30: *"i am the only human in these repos. my teams are
  sessions."* Recorded in [PR #414](https://github.com/syncytium2/bugarach/pull/414), and anyone
  quoting interface2 commit prose in a public artifact has to decode it first.
- **Personal paths, including the shape the guard cannot see.** SAP004 matches a forward-slash home
  path; a Windows or WSL path written for a Windows reader uses backslashes and slips past it. Filed
  as armory finding 23.
- **A paper is under review**, and its venue may have anonymity or prior-disclosure rules that a
  public repository breaks.

And publishing here is not undoable: GitHub keeps edit history, a superseded commit stays fetchable by
hash, and every clone and fork keeps both. A private mirror made public later cannot be made private
again in any way that matters.

## What a mirror does not carry

Name these in the board block as owed, or they will be discovered missing later:

| not carried | why | what it needs |
|---|---|---|
| issues and merge requests | platform data, not git | a separate export, if any of the paper's record lives there |
| the wiki | a separate git repository on GitLab | its own `--mirror` push |
| releases and CI semantics | tags travel; release notes and pipeline meaning do not | a decision, once the working remote is settled |
| LFS objects | not in a plain `--mirror` clone | `git lfs fetch --all`, above |

## Waiting on Tony

**Which remote is authoritative once the mirror exists.** Two writable copies drift, and drift between
copies is the failure armory was built to name. The recommendation is **GitHub becomes the working
remote and GitLab goes read-only**; otherwise an access problem has been traded for a sync problem.
Nothing in this handoff makes that change — it copies and stops.

## What this unblocks

Two goals currently live where no session but interface2's own can read them, and the mirror ends that
for both:

- **The `varyburstwindow` idea and how it applies to coordination**, which bears on goal 1's window
  knobs and on the simulator planting one event width.
- **The migration goal itself** — the per-paper curated repository and the citable release are
  selections from this copy, and cannot start before it exists.

Neither is actionable from the mirror alone. Both still want the ending session's own account, and
[`docs/exports/`](docs/exports/) is where interface2's conclusions have reached this repository before.

## When this is spent

Delete this file once the mirror is verified, the board block is released and the authority question
above is answered. Move it to [`docs/handoffs/`](docs/handoffs/README.md) instead if the authority
question is still open then — the verification numbers are worth keeping beside whatever decides it.
