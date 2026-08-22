---
status: open
filed: 2026-08-22
---

# Quotation checking is a report, not a gate — and the naive version is dangerous

`tools/verify_quotes.py` exists and is deliberately **not** wired into CI. It reports
which quotations in a document can be found in a PDF on the darkroom lit shelf. On
the 1980s IEEE scans it currently traces **11 of 30** quotations in
[`detector_history.md`](../detector_history.md), while hand-checking every one
against `pdftotext -layout` confirmed **all sixteen paper quotations were genuine**
(the other fourteen quote repo docs, interface2 and the author's own phrasing, and
can never match a PDF).

So its miss rate is mostly false, and a gate whose alarms are mostly false is a gate
people learn to ignore. **A MISS means "check by hand", never "this is wrong."**

## The part that is already worth knowing

The obvious implementation — extract the PDF text, collapse all whitespace, grep —
is unsound on a two-column scan **in both directions**, and the second one is
dangerous:

- **False negatives.** A sentence broken across a line keeps its hyphen
  (`mean-\nlevel`), so the phrase never appears contiguous.
- **False positives — it can manufacture a quotation that appears nowhere on the
  page.** `pdftotext` without `-layout` interleaves the columns line by line. Collapse
  the whitespace and you have spliced the left column onto the right. This is not
  hypothetical: while checking Rohling 1983, the naive extraction produced

  > "…for both CFAR procedures. Due to **filter), or whenever defined image structures
  > are to be de**symmetry, the splitting of the reference window of the CAGO CFAR
  > does not help in this situation."

  The real sentence — *"Due to symmetry, the splitting of the reference window of the
  CAGO CFAR does not help in this situation"* — is genuine and sits in the left
  column. But a reader (or a reviewer, or a language model) skimming the naive
  extraction can lift a phrase that spans the splice and quote text that was never
  written. **A checker that can invent a match is worse than no checker.**

## Why it still does not work

`columns()` extracts with `-layout`, splits each line on runs of 3+ spaces, clusters
the cell offsets into column origins, and joins each column separately. That is the
right shape and it fixed the splicing. What it does not yet handle:

- **OCR word-breaks without hyphens.** Rohling's scan renders *measure* as `mea-`/
  `sure` (hyphenated, handled) but also *superior* as `supe`/`rior` with a stray
  character (not handled). De-hyphenation only catches the explicit case.
- **Dropped and mangled characters.** `a r e` for *are*, `Thl` for *TM*, `clearl>`
  for *clearly*. Letters-and-digits normalisation absorbs some of this and not all.
- **Column origins that drift across pages.** Clustering is per-document, and a
  paper whose layout changes between the abstract page and the body gets its columns
  mixed.

## What would finish it

Fuzzy matching rather than substring: normalise both sides, then accept a match
above a similarity threshold on the best-aligned window (`difflib`, or a rolling
Levenshtein bounded by the quotation length). That tolerates OCR damage without
tolerating splices, because a spliced candidate differs by whole clauses rather than
by characters.

Worth doing when the shelf is bigger. Until then the honest workflow is: run it, take
the hits as verified, and hand-check the misses against `pdftotext -layout`.
