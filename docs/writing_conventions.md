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

## A finding about an environment names the environment

"CI has no chromium" was repeated across sessions for days without ever saying
*which machine*. One session read it the only way it could be read from where it
sat — as this laptop — and installed the browser locally. Another read the same
sentence and changed the workflow. Both then reported "chromium is in", truthfully,
about different machines, and the duplicated work was invisible to both.

A laptop, a linked worktree, a Dropbox mount and a GitHub runner are four different
places. A sentence that omits which one it means gets resolved by whoever reads it
next, in favour of wherever they happen to be standing.

> ✗ "chromium is installed now"
>
> ✓ "chromium is installed on the GitHub runner, as a workflow step; this laptop
> still has none"

This is the same failure the two session boards exist to prevent — one for what
another *machine* can see, one for what this *machine* shares — and it is the half
no board catches, because it lives in the wording rather than the filing.

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
| **a table in a chat reply** | **nothing, and it is where the units rule broke** |

The last row is not a gap waiting for a tool. A chat reply reaches one reader
immediately and is never reviewed, which makes it the surface where a convention
has to be held by whoever is writing rather than caught downstream. It is listed
so that "the conventions are for documents" cannot be read into the table.

A sapper rule was considered for bare commit shas in prose and **not** written:
the repo's own vendoring stamps (`vendored from interface2 @ 9df9a16`) are
legitimate bare shas, as are the provenance lines in this file's neighbours, so
the rule would have fired mostly on correct text. Filed as a thought rather than
a rule — see `docs/sapper_feedback/` if that changes.

## American English

`center`, not `centre`; `labeled`, `traveled`, `modeling`, `analyze`. Tony's
call, 2026-08-18, made after a README table shipped the model's name as
"centre−surround" while the code that defines it — `learn/nets.py`'s own
`@register("tube", note="center-surround …")` — had spelled it the American way
all along.

This bites hardest in **figure labels**, because a figure is regenerated from a
script and a README is edited by hand, so the two drift apart silently and the
mismatch is only visible to someone looking at the picture and the table at the
same time. When a name changes, change it in the generator and re-render, rather
than in the prose alone.

Known drift, not yet swept: several figure generators under `tools/` and their
committed renders still spell it `centre−surround` (the learned-detector report
figures, the architecture and regime figures). They need a re-render to fix, and
some of those re-renders retrain a model, which is why this is recorded here
instead of being done in the same change.

## Bold in a results table asserts a claim

Bolding a cell says *this is the best one*, and a reader takes it from the table
without reading the paragraph under it. The bake-off table bolded the learned
model's detect time at 0.014 s while `rate+context` scanned the same fold in
0.005 s, and bolded its F1 while the surrounding prose argued — correctly — that
the top three are a tie. Both were caught by Tony reading the table, which is
exactly the reader the bold was talking to.

Emphasize the row a passage is *about* if you like. Do not emphasize a number
unless it is the extreme of its column, and not even then when the document's own
argument is that the differences are not separable.

## Every table column carries its units, and *dimensionless* is a unit

A bare number in a table is a number in whatever unit the reader last saw. This
repo puts seconds, hertz, millihertz per ROI, bytes, counts, ratios and
dimensionless scores in front of the same reader, often on the same page, so
there is no default to fall back on.

Tony had to ask what the units were on a table of F1 gaps — *"minutes?"* — and
the honest answer is that nothing in the table said, while the paragraph beside
it discussed a guard in **seconds** and an α that is a **dimensionless
probability**. Three kinds of quantity, one of them a duration, no column marked.
The reading he took is the one the table supported.

- **Put the unit in the header**, not in a caption underneath: `gap (ΔF1)`,
  `seed sd (F1)`, `guard (s)`, `rate (mHz/ROI)`, `size (B)`.
- **Say dimensionless when it is dimensionless.** F1, α, precision, a ratio of
  two F1s — these carry no unit, and *writing that down* is what stops a reader
  supplying one. `gap/sd (ratio)` costs eight characters and closes the question.
- **A ratio names what it is a ratio of, in the prose once.** `gap/SEM` is F1 over
  F1; what the reader needs is that it means *how many standard errors wide*.
- **Percentages say what of.** `+2.03%` of a bar sitting near 2.9 is not
  comparable to `+8.78%` of a bar near 0.5 — `probe_guard_where_it_lands.py` got
  this right and said so in its own table. The point is that it had to.

This applies to any table a person reads: a PR body or a chat reply as much as a
document under `docs/`. The chat reply is where it went wrong.
