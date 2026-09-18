---
status: open
filed: 2026-09-18
---

# Finish leaving GitLab

> **Filed** when [`docs/handoffs/2026-09-18-interface2-mirror.md`](../handoffs/2026-09-18-interface2-mirror.md)
> left the root. Tony, 2026-09-18: *"i want to remove all dependencies on gitlab."* Most of it is
> done — see `docs/SESSIONS.md`, block `065/interface2-mirror`, for what and how it was verified.

## Done on WSMIP065, 2026-09-18

- **interface2** — full mirror in private `syncytium2/interface2`, parity verified ref for ref
  immediately before this machine's checkout was re-pointed. GitHub is its only remote. GitLab's
  last commit is a banner telling any machine that has not re-pointed to do so.
- **coding-project, interfaceDFoF0, ICCetcStatistics, ggplot-tuner** — each mirrored into a private
  repo of the same name, verified, and its checkout re-pointed.
- **R** — already gone from GitLab. The 21 commits fireflies lacked are `archive/R-*` tags in
  fireflies; the dead remote was removed from all three checkouts.
- **CASCADE** — found while going through the GitLab UI. Its four GitLab projects (`cascade-local`,
  `cascade`, `tdcascade`, `cascadeTD`) each held one commit, a README with a title and nothing else;
  **Tony deleted them.** The real work was in `Documents\cascade stuff\Cascade`, a checkout of the
  Helmchen lab's CASCADE with **no remote holding any of it**: 3 unpushed commits (TD ground truth,
  `cascade2p` edits) and 168 untracked files — the CASCADE models trained on TD data (`TD_5min`,
  `TD_thing64`, `TD_thing65`, `TD_three`), KNDy ground truth (DS96/97/98) and 2024 traces with their
  predictions. Now private **`syncytium2/cascade-td`**: `master`, `defazio`, and
  `archive/untracked-2026-09-18` (the 168 files, committed without touching the working tree), each
  identical by SHA; 162 files byte-identical on the archive branch and six `config.yaml` identical
  after `core.autocrlf`'s CRLF→LF. The checkout's `origin` is now that repo; the Helmchen lab's is
  `upstream`.

No checkout on WSMIP065 has a gitlab.com remote. Check it again with:

```
find ~ -maxdepth 4 -name .git -type d -not -path '*/AppData/*' | while read g; do
  git -C "$(dirname "$g")" remote -v | grep -qi gitlab && dirname "$g"; done
```

## Open, in order

1. ~~**Re-point the Mac's interface2 checkout**, and run the sweep above there too.~~ **Done
   2026-09-18** (Tony). Checked from WSMIP065 afterwards: GitLab's `main` still at the cutover
   commit `94912afc`, and no ref on GitLab that GitHub lacks — nothing was pushed there after it.
2. **Look through the GitLab web UI before access ends** (Tony; the date is unknown and no later
   than 2027-03-31): projects never cloned on either machine, and the discussion on interface2's
   4 merge requests, any issues and any wiki. None of it is git, so none of it is in a mirror.
3. **Archive the GitLab projects** (Tony, web UI: Settings → General → Advanced → Archive). This is
   what makes a stray push fail loudly instead of splitting the history. **interface2: archived
   2026-09-18** (Tony). The rest: open.
   `Documents\cascade stuff\TDCascade` (286 MB, not a git repo — a copy of the CASCADE tree plus a
   clone of the empty `tdcascade` project) is still on disk, unchecked against `cascade-td`.
4. **interface2's branch list on GitHub** — the triage in its `docs/migration_selection.tsv`,
   applied on GitHub only, **after** step 3: create each `archive/<branch>` tag, verify it SHA
   against SHA, then delete the branch. Decided on interface2's board, block
   `065/reply-branch-list`: before cutover a GitLab catch-up would have undone it, and after the
   tags exist the deletions depend on nothing at GitLab.
5. **Text that still names GitLab as live** — foundations' `GLOSSARY.md` line 1 provenance stamp
   (`interface2 (GitLab) … @ 62c856c`) and its `README.md` line 81 and ADRs 0001/0004 (the ADRs are
   dated records: add a note, do not rewrite). In interface2, its own docs beyond the banner and
   runbook. bugarach's `gitlab.com/cossartlab/cicada` links **stay** — they cite another lab's
   project, not a dependency.
6. **WSMIP065's MATLAB path** — `pathdef.m` still lists 128 worktree folders that no longer exist
   (interface2's `docs/worktree_prune_ledger_2026-09-18_WSMIP065.md` has the detail). Separately,
   Tony asked about moving the interface2 checkout out of `Documents\MATLAB`: 25 `.m` files on its
   `main` hard-code that location and would need `if2_paths` first.
