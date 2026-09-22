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
3. ~~**Archive the GitLab projects.**~~ **Done 2026-09-18** (Tony) — interface2 first, then the rest.
   `Documents\cascade stuff\TDCascade` (286 MB, not a git repo — a copy of the CASCADE tree plus a
   clone of the empty `tdcascade` project) was **checked and deleted 2026-09-18** (Tony: go). Every
   file was hashed against all of `cascade-td`'s objects: 681 of 694 already there. Of the 13 not,
   one mattered — `cascade2p/utils.py` of 2024-09-04, an unfinished fix for the ground-truth path —
   and it is branch `archive/tdcascade-utils-2024-09-04` in `cascade-td`, byte-identical. The rest
   were `__pycache__`, Jupyter checkpoints and the one-line README.
4. ~~**interface2's branch list on GitHub.**~~ **Done 2026-09-18** (Tony: *"clean up interface2 on
   github"*), from a fresh clone of GitHub, restore ledger landed on interface2's `main` **before**
   anything was deleted (`docs/github_branch_triage_ledger_2026-09-18.md`). 39 `tag` rows became
   `archive/<branch>` tags, all verified SHA against SHA on GitHub first; then one atomic push, each
   deletion leased at its recorded SHA, removed those 39, 112 branches whose tips are in `main`, and
   GitLab's 8 `refs/merge-requests/*` (each `head` in `main`; each `merge` a preview merge whose
   parents are both in `main`). No `tag` row had been committed to since the triage. **GitHub now:
   27 branches** (the 21 `branch` rows still unmerged, `main`, and 5 unlisted ones kept by default),
   39 `archive/*` + 16 `rescue/*` tags. WSMIP065's checkout still has 25 local branches whose remote
   is gone — every commit on them is on GitHub; delete them locally whenever.
5. ~~**Text that still names GitLab as live.**~~ **Done 2026-09-18** (Tony: *"clean up the last of
   the gitlab remnants"*), after a sweep of every repo on WSMIP065. Rule applied: fix what claims
   GitLab is live or tells a reader to use it; leave dated records as written, adding a dated note
   to an ADR rather than editing it; leave citations of another lab's GitLab (CICADA) alone.
   - **interface2** (`e603b00d` on `main`) — the real dependency was **Great Lakes**: both cluster
     clones fetch from GitLab with a token in the remote URL, and `greatlakes/ACCESS.md` plus four
     READMEs taught that. The clone section now uses a **read-only GitHub deploy key**, with
     github.com's host-key fingerprints confirmed from GitHub's API and a live keyscan (identical;
     not yet from a login node). The scrubber already redacted GitHub tokens; its self-test now
     plants a `github_pat_` in the `git remote -v` shape that leaked on 2026-09-04, and passes.
     Also: the MIGRATED banner replaces the planned-migration one, ROADMAP goal 3 is done,
     `docs/gitlab_auth.md` is marked superseded, two handoffs and a todo corrected.
   - **foundations** #7, **fireflies** #8, **downLow** #2, **no_peak** #3 — the GLOSSARY stamp and
     README, notes on ADRs 0001/0004; fireflies' one-remote rule (the `archive/R-*` tags named),
     `NEXT_SESSION.md`, two workflow comments; the `coding-project` source line gains its GitHub
     home. Merged 2026-09-22 — item 10.
   - **bugarach** — this todo, `bct-modularity-fast`'s pointer (now `archive/bct-modularity-fast`),
     and `docs/reaper_handoff.md`'s "interface2 is on GitLab".
   - **Left, deliberately:** ledgers, board blocks, reviews, changelogs, archived notes, the
     runbook body, short-course's dated case studies and its generic "your institution may run
     GitLab" advice, and armory's `tri_paths.py`, whose GitLab URLs are a guard and its test data.
   - **This machine's stored GitLab credentials** (two Git Credential Manager OAuth entries for
     gitlab.com) were deleted. That removes the local copy only; see item 9.
6. **WSMIP065's MATLAB path** — `pathdef.m` still lists 128 worktree folders that no longer exist
   (interface2's `docs/worktree_prune_ledger_2026-09-18_WSMIP065.md` has the detail). Separately,
   Tony asked about moving the interface2 checkout out of `Documents\MATLAB`: 25 `.m` files on its
   `main` hard-code that location and would need `if2_paths` first.
7. **Re-point both Great Lakes clones** (`~/if2-bakeoff`, `~/interface2`) — needs a login (Okta).
   Steps: interface2's `greatlakes/ACCESS.md` § "Cloning comes from GITHUB": generate a key on the
   cluster, register it as a read-only deploy key on `syncytium2/interface2`, `set-url`, fetch.
   Until then a fetch there reads a frozen GitLab copy and reports success.
   **Owned in interface2 since 2026-09-22** (Tony: *"make sure the next greatlakes session fires a
   big flare"*): `docs/todo/2026-09-22-compute_infra-great-lakes-clones-still-fetch-from-gitlab-re-po.md`
   there, on its pipeline map, with a `🔴 GREAT LAKES` notice its session briefing prints first, a
   red line on its `CLAUDE.md` banner and a box atop `greatlakes/ACCESS.md` (`700df29d`). Close this
   item when that one resolves.
8. **Confirm 064.** interface2's ROADMAP planned the cutover "with 064 + Mac"; the Mac is confirmed.
   **064: in progress, 2026-09-22** (Tony). Done when every checkout there passes the sweep above
   (`git remote -v | grep -i gitlab` finds nothing) — and that includes a `git pull` of its interface2
   checkout, or item 11's flare never reaches sessions on 064.
9. **Revoke GitLab credentials while access lasts** (Tony, GitLab web UI): personal/project access
   tokens and deploy tokens (Settings → Access tokens), deploy keys on the archived projects, and the
   Git Credential Manager OAuth grant (User settings → Applications → Authorized applications). The
   cluster's token-in-URL is among them.
10. ~~**Merge foundations #7, fireflies #8, downLow #2, no_peak #3.**~~ **Done 2026-09-22** (Tony:
    *"merge the four prs"*), each squash-merged pinned to the head commit that was reviewed:
    foundations `0733068e`, fireflies `7328dd71`, downLow `9833eeb3`, no_peak `c103d2be`.
11. **Pull interface2 on the Mac (and 064), or the Great Lakes flare does not reach them.** The
    session briefing reads the board from the checkout **on disk**, never from GitHub, and does not
    pull. A checkout behind `700df29d` shows no `🔴 GREAT LAKES` notice and no red `CLAUDE.md` line.
    On each machine: `git -C <interface2 checkout> pull --ff-only`. **WSMIP065's is done**: its
    primary checkout (`Documents\MATLAB\interface2`, the one MATLAB runs from) was fast-forwarded
    `7242a2fc` → `700df29d` on 2026-09-22 with no MATLAB running — undo with
    `git reset --hard 7242a2fc` if that code change is unwanted.
12. **Small, any time:** WSMIP065's MATLAB checkout still has 25 local branches whose remotes are gone
    (item 4) — every commit on them is on GitHub, so `git branch -D` on each is safe; and interface2's
    `tools/check_doc_links.py` comments still name `origin/db4-sqlite-pipeline`, deleted 2026-09-11,
    whose commits are in `db4-pilot-verify`.
