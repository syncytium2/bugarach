---
status: open
filed: 2026-08-27
upstream: syncytium2/murderboard
---

# The citation role returned "0 findings" on a page that cited nobody, and it was right by its own reading

> An upstream change, not a bugarach one — `docs/doc_review_process.md` and
> `.claude/skills/murderboard/` are **vendored**, so this must be fixed in
> `syncytium2/murderboard` and re-copied. Filed here because here is where it was found
> and here is the evidence.

## The two runs

An earlier murderboard on the learned-detector page's ancestor recorded role 2 as:

> **0 findings** — the page cites no papers, DOIs or external attributions. Nothing to
> verify against a bibliography.

The 2026-08-27 murderboard ran the same role on the same lineage as a **separate
agent**, with an instruction to enumerate the methods the document names *before*
checking any citation that is present. It returned the largest finding in the review:

> The page contains zero citations. It names six other people's published methods in a
> comparison table and puts this project's network on top of them.

Both describe the same page. The first treats an empty bibliography as an empty
worklist. The second treats it as the finding.

## Why the checklist permits the first reading

Role 2's checklist is written in terms of citations that **exist**: confirm the work
exists, check it is the origin, check the lab, name the literatures searched. Every
instruction takes a reference as its subject. A document with no references satisfies
all of them vacuously, and "nothing to verify" is a defensible summary of the role as
written.

The role's own later bullets almost close it — *"When a deliverable claims something is
novel, unattributed, or 'ours', the reportable finding is never 'looks fine'"* — but
that fires on an explicit novelty claim. A page that simply lists other people's methods
under its own project's name makes no such claim out loud, which is exactly the case
that slipped.

## The change

Make enumeration the role's **first step and its output contract**, so an empty
bibliography produces a table rather than a sentence:

> **Before checking any citation that is present, list every method, tool, measure,
> data set and named result the document mentions.** One row each: *what is named ·
> is it this project's own work · is it cited here · where should it be cited from*.
> **A named method with no citation is a finding.** A document with no bibliography
> makes this table longer, not shorter.

Two supporting notes worth carrying with it:

- **This is the same defect the role already guards against, one level up.** The role's
  existing rule is that verifying everything *present* while never asking what is
  *absent* is how a reference list can be entirely correct and credit the wrong paper.
  The failure here is the same sentence with the list empty.
- **It also explains why the size rule exempts role 2.** The process already says role 2
  may not be collapsed into a single-pass self-review, because *"a single pass inherits
  the drafter's search history, so it stops in the same place for the same reason."*
  The 0-findings run **was** a single-pass self-review. The rule was correct, was
  written down, and was skipped — so this change is worth having even where the
  separate-agent rule is honored, because it makes the omission visible in the output
  rather than depending on the reviewer's instinct.

## Related, same review

The run record is [`docs/reviews/learned_detector_2026-08-27.md`](../reviews/learned_detector_2026-08-27.md).
Its "Findings about the repo, not the page" section carries this item and five others.
