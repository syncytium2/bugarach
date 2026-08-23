---
status: open
filed: 2026-08-23
---

# A vendored file was edited in place, and the freshness gate cannot see it

Re-vendoring the murderboard from `f26414a` to `fae0eca` turned up an edit nobody
recorded. `docs/doc_review_process.md` line 241 read:

> a **folder-level** result was reviewed by eleven roles

where upstream says:

> a **corpus** result was reviewed by eleven roles

One word, inside an incident note, in a file whose first line says *do NOT edit here*.
Re-copying discarded it, which is the correct outcome — but it was discarded silently,
and that is the part worth fixing.

## Why the gate missed it

`tools/murderboard_freshness.sh` compares the **stamped sha** against upstream's HEAD.
It answers "is this copy from a current commit?" and never "is this copy *that commit's
content*?". So an in-place edit to a vendored file is invisible to it forever: the stamp
still names a real upstream sha, and the gate keeps reporting current.

Worse, the two failure modes cancel. A stale stamp gets loudly reported; an edited body
does not — and an edited body is the one that changes what the process actually says.

## What to do

1. **Add a content check to the freshness family**: for each vendored file, compare the
   body (everything but the stamp line) against the upstream blob at the stamped sha,
   and fail on divergence. bugarach can do this locally today — the check is the same
   `diff <(sed '1d' vendored) <upstream file>` used to find this — but it belongs
   upstream, because every consumer has the same hole.
2. **Decide what the edit wanted.** "Corpus" may have been changed deliberately: this
   repo's export-folder contract makes *folder* the unit of analysis, and a session may
   have been aligning vocabulary. If the distinction matters to the process document,
   the change belongs upstream as a PR, not as a local edit — that is what "update
   upstream and re-copy" means.

## Related

- `docs/todo/2026-08-12-vendored-lit-tool-carries-personal-paths.md` — the other
  deliberate divergence from this upstream, which is *recorded* and therefore fine.
  The difference between that one and this one is the record, not the edit.
