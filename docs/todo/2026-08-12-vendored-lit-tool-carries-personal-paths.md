---
status: open
filed: 2026-08-12
---

# murderboard's `fetch_paper.py` carries personal paths — removed here; needs a decision + an upstream report

## What

`tools/fetch_paper.py`, vendored from `syncytium2/murderboard @ b2b2ba2`, hardcodes
a fallback library location containing an institution name and a person's name:

```python
os.path.join(home, "<INSTITUTION> Dropbox", "<PERSON>"),
os.path.join(home, "Library", "CloudStorage",
             "Dropbox-<INSTITUTION>", "<PERSON>"),
```

It is a deliberate back-compat branch upstream — murderboard's `CLAUDE.md` says
the calcium-imaging origin "lives only in the appendix of `doc_review_process.md`
and in explicit back-compat branches of `fetch_paper.py` (`IF2_LIT`/`IF2_PAPERS`,
the `01-lit` autodetect)". Reasonable for murderboard. **Not** reasonable for a
consumer that is a public repo, which bugarach is (FOUNDATIONS §5).

Caught by sapper SAP004 — but only *after* it had been committed and merged. The
blind spot that let it through is filed separately:
[`../sapper_feedback/2026-08-12-sapper-all-is-blind-to-untracked-files.md`](../sapper_feedback/2026-08-12-sapper-all-is-blind-to-untracked-files.md).

## Done

Removed `tools/fetch_paper.py` from this repo, rather than patching it in place —
editing a vendored file creates exactly the drift the provenance stamps exist to
prevent, and bugarach has little use for the lit tool (the murderboard process
references it only when a reviewer needs a paper). `check_vendor_freshness.sh`
no longer lists it. The deviation is recorded in `CLAUDE.md`.

## 1. Decision needed from Tony — history

The string reached `main` and was pushed to a **public** GitHub remote (in the
merge of PR #2, commit `2ad4ac4`). Removing the file fixes the *tip*; the blob
remains reachable in history.

**Not actioned, deliberately.** `CLAUDE.md` requires that any history rewrite be
preceded by restating what would be destroyed and getting explicit confirmation
in words — a rule that exists because of a near-miss on 2026-08-11. So this is a
question, not a plan:

- **Option A — leave it.** The exposure is a Dropbox folder name and a name that
  is already public on the repo (commits are authored by "richard defazio", and
  `CITATION.cff` names the author). Arguably it adds nothing not already there.
  The institution affiliation is the only genuinely new element.
- **Option B — rewrite.** `git filter-repo` over the two commits touching the
  file, then force-push `main`. Destroys the current `main` hashes; anyone with a
  clone must re-clone or reset. Also requires GitHub to expire the old objects,
  and forks/caches may retain them regardless.

My read: **Option A is probably right** — the marginal exposure is small, and a
force-push on a public `main` has real costs and does not reliably erase
anything. But it is explicitly Tony's call, and the honest framing is that a
rewrite buys less than it looks like it does.

## 2. Report upstream

murderboard aims to be project-neutral and vendorable; a hardcoded personal path
defeats that for any public consumer. Suggested upstream fix: keep the
`MURDERBOARD_LIT` / `IF2_LIT` env lookups, and move the `01-lit` autodetect
behind an env var too (e.g. `IF2_HOME`) instead of literal names — the autodetect
still works for whoever sets it, and nothing personal ships in the file.

Worth pairing with the freshness-gate `CLONE_CANDIDATES` bug already filed in
[`2026-08-12-report-freshness-gate-clone-bug.md`](2026-08-12-report-freshness-gate-clone-bug.md)
— both are "the project-neutral generalization was left half-finished", and one
report covering both is likelier to land than two.

## 3. Consider a sapper rule for vendoring

Vendored files arrive in bulk from a codebase written under different
assumptions, and nobody reads 482 lines they did not write. A check that scans
*newly added* files harder than existing ones — or simply the `--all` scope fix
in the sapper_feedback item — would have caught this at the right moment.
