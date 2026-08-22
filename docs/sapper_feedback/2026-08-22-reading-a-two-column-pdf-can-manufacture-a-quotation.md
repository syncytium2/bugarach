---
rule: none-yet
status: open
filed: 2026-08-22
---

# Reading a two-column PDF the obvious way can manufacture a quotation that is not in it

## What happened

Retrieving the CFAR primaries onto the lit shelf (2026-08-22) meant checking that
every quotation in `docs/detector_history.md` was actually in a source. The obvious
check is one line:

```bash
pdftotext paper.pdf - | tr -s ' \n' ' ' | grep -i "the phrase"
```

On a **two-column** scan that is not a check. `pdftotext` without `-layout` emits
the page line by line **across both columns**, so collapsing whitespace splices the
left column onto the right. Working on Rohling 1983 it produced this:

> "…for both CFAR procedures. **Due to** *filter), or whenever defined image
> structures are to be de*
> **symmetry, the splitting of the reference window of the CAGO CFAR does not help
> in this situation.**"

The real sentence — *"Due to symmetry, the splitting of the reference window of the
CAGO CFAR does not help in this situation"* — is genuine and sits in the left
column. But the extraction interleaves ~50 characters of unrelated right-column
text into the middle of it, and a reader skimming for the phrase lifts it across
the splice without noticing.

It fails the other way too. `"mean-\nlevel"` keeps its hyphen and `"supe\nrior"`
breaks without one, so real quotations come back **not found** — two from Gandhi &
Kassam 1988 did.

## Why it is worth a rule or a gotcha

**This repository's entire lit-shelf discipline exists to stop a fabricated
quotation**, and the shelf README says so: an earlier draft carried a fabricated
author list, caught in review. The failure mode above is worse than fabrication
from memory, because it produces text that *looks* verified — it came out of the
actual PDF — and a session that runs the one-liner will report it as checked.

Concretely, in this session: an earlier commit stated "seven quotations, seven
hits, each to a named file" as evidence. That check used the unsound method. Every
quotation turned out to be genuine when re-checked with `-layout` column by column,
so nothing wrong shipped — but the evidence offered for it was worthless, and that
is exactly the shape of defect sapper exists to catch before it matters.

## What a rule could fire on

Honestly assessed, this is **probably a gotcha rather than a SAP rule**, and it is
filed here so the sapper owner decides rather than me.

**Against a rule:** the hazard lives in *how a session reads a PDF at the terminal*,
not in committed code. `grep -rn pdftotext --include='*.py' --include='*.sh'` over
`tools/`, `src/` and `.claude/` returns **nothing** today — there is no tracked
caller to lint.

**For a rule, if one is wanted:** a narrow, checkable form exists — flag any tracked
file that invokes `pdftotext` **without** `-layout`. It would have zero current
findings, which by this project's own standard ("a rule must prove it can fire")
means it needs a self-test fixture rather than a real hit. That is cheap: a fixture
script containing the bare invocation.

**The stronger placement may be neither.** The durable artifact is the *procedure*:
when quoting from a PDF on the shelf, extract with `-layout` and confirm the phrase
is contiguous **within one column**. That belongs wherever this repo keeps
verification gotchas — interface2 has `docs/verification_gotchas.md`; bugarach does
not have an equivalent, and the lit shelf's own README is the other candidate home.

## What was done meanwhile

- Every quotation in `docs/detector_history.md` re-checked by hand against
  `pdftotext -layout`, column by column. All sixteen paper quotations are genuine.
- `tools/verify_quotes.py` mechanises the sound version — extract with `-layout`,
  cluster cell offsets into column origins, join each column separately, match only
  within a column. It ships as a **report, not a gate**, and is deliberately not in
  CI: OCR word-breaks without hyphens still make it under-report (11 of 30 traced),
  and a gate whose alarms are mostly false is one people learn to ignore.
- `docs/todo/2026-08-22-quote-verification-is-not-a-gate-yet.md` records what would
  finish it — fuzzy matching over exact substring, which tolerates OCR damage
  without tolerating splices.
