---
status: open
filed: 2026-08-28
rule: SAP007
kind: dispute + rule-design question
---

# SAP007 cannot tell an importer from an analysis, and its backlog list is now two lists

## What happened

`tools/import_dandi.py` was blocked:

```
BLOCK SAP007 tools/import_dandi.py:257: files = sorted(src.glob("*.mat"))
```

The rule is right about the pattern and wrong about this file, and the reason is
a category it has no way to see.

**SAP007 exists to stop an ANALYSIS reading a `.mat` store instead of the export
folder** — the 2026-08-20 defect where two withdrawn recordings reached every
published number. That rule is correct and should not be weakened.

**`import_dandi.py` is not an analysis. It is a producer.** It reads the Cossart
lab's published DANDI:000219 — foreign source data, extracted to `.mat` by
interface2 — and *writes an export folder*. It is the same role interface2's
exporter plays for this lab's recordings, and its output is what analyses then
read. It consumes nothing of this lab's and cannot go around this lab's
exclusions, because there are none to go around: the corpus is another group's,
published under CC-BY-4.0, and its authors chose its contents.

So the pattern `*.mat` here means "someone else's source data on the way in", not
"this lab's store, read behind the contract's back."

## The narrow fix, applied

Added to SAP007's `exclude`, with a comment naming the category. That matches how
every other legitimate entry on that list is handled (`store.py` is the reader,
`matlab_ref/**` regenerates parity fixtures, `lab_excluded.py` reads the
spreadsheet on purpose).

## The design question, which is the real reason this file exists

**The exclusion list is now doing two jobs and its own comment only describes
one.** It says:

> THE EXCLUSION LIST IS THE BACKLOG. […] They are named rather than
> pattern-matched so that fixing one means DELETING A LINE HERE, and the list
> shrinking is the progress.

That is true of six entries and false of the other six. `store.py`, `cli.py`,
`ui/app.py`, `matlab_ref/**`, `lab_excluded.py` and `assess_archive.py` are not
going to be deleted — they are permanently legitimate. Mixing them with the
backlog means **the list's length no longer measures anything**: it cannot go to
zero, and a reader cannot tell which entries are progress and which are
furniture. Every importer added for another lab makes that worse.

Suggestion, for whoever owns the rule:

1. **Split `exclude` into two named tuples** — `_SAP007_LEGITIMATE` and
   `_SAP007_BACKLOG` — concatenated at the rule. The backlog's length is then a
   real metric and could even be asserted non-increasing by a test.
2. Or give the rule a **positive marker** instead: a file declaring
   `# sapper: SAP007 producer` in its header is an importer and is skipped, so a
   new importer needs no edit to `sapper.py` at all. This is the better shape if
   more outside-lab corpora are coming, because it puts the justification **in
   the file being excused** where a reviewer reading that file will see it,
   rather than in a list nobody opens.

I have not implemented either — a change to a shared gate's structure is not
mine to make from a branch about something else, and option 2 changes how every
rule could be excused, which is a bigger decision than this one file.

## What I explicitly did NOT do

- **Did not weaken the pattern.** `*.mat` still blocks everywhere else.
- **Did not use `ALLOW_UNCLAIMED_BOARD`-style override to sneak past.** The gate
  firing was correct behaviour; the fix belongs in the rule, visibly.
- **Did not restructure the importer to dodge the regex** (e.g. building the glob
  from a variable). That would pass the gate while defeating it, and a rule you
  can style your way around stops being a rule.
