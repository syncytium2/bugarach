# Writing conventions — docs, commit messages, PR bodies, replies

Tony, 2026-08-12: *"the numbers and dates don't mean much to a human."*

This is a **document-quality** rule, so its real enforcement is the murderboard
([`doc_review_process.md`](doc_review_process.md)) — the line-editor and
naive-reader roles are where these get caught. Nothing here is mechanized; that
is a known gap, recorded rather than glossed.

## Name things; don't index them

If a document defines a set of traps, stages, or findings, refer to them by a
short descriptive name — never `T3`, `stage 4`, `§6bis`.

> ✗ "Building stage 5 on stage 4's unreviewed number is T3 again, one level up."
>
> ✓ "Everything downstream would rest on a number nobody has checked — the same
> mistake as last time: skipping the check because there was something more
> interesting to build."

The first asks the reader to hold two private taxonomies in their head and
cross-reference them, and carries no meaning on its own. This is the same
instinct as the plot conventions: identity lives in the label, and no title
restates what the axes already say.

Give each item a name **at the point it is defined**, and the cross-references
write themselves: *the contaminated null*, *the skipped gate*, *stranded
validation*.

## Shas and dates are lookup keys, not content

`b94062e` and `2026-07-23` tell a reader nothing on their own.

> ✗ "b94062e adopted the measured-regime optima on 2026-08-05."
>
> ✓ "The calibrated settings became the shipped defaults — on one real recording
> that takes LoCo from 81 detected events down to 28."

Include a sha only where someone would genuinely go look it up, and then in
parentheses after the meaning. Keep a duration when the duration is the point
("two weeks later it still had not been attempted"); drop the calendar date that
merely encodes it.

Frontmatter dates, provenance stamps, and session-board entries are exempt —
there the date *is* the content.

## Prefer the consequence to the label

> ✗ "the adoption had a large effect"  ✓ "81 events become 28 on a real recording"
>
> ✗ "precision degraded"  ✓ "precision fell from 74% to 10%"

## Where this is enforced

| surface | enforcement |
|---|---|
| document deliverables | the murderboard, line-editor and naive-reader roles |
| commit messages, PR bodies | nothing — reviewer judgement |
| docs under `docs/` | nothing automated |

A sapper rule was considered for bare commit shas in prose and **not** written:
the repo's own vendoring stamps (`vendored from interface2 @ 9df9a16`) are
legitimate bare shas, as are the provenance lines in this file's neighbours, so
the rule would have fired mostly on correct text. Filed as a thought rather than
a rule — see `docs/sapper_feedback/` if that changes.
