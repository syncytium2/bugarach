# Murderboard run — docs/learned/coordination_report.html (section 3 rewrite)
- upstream:  syncytium2/murderboard @ 783501e
- vendored:  783501e (freshness gate exit 0, same session as the landscape run)
- freshness: current
- artifact:  `docs/learned/coordination_report.html` — section 3 replaced at source and rebuilt
- roles:     11 of 11 run
- rounds:    1 blind verify round to clean

**Scope, stated so the coverage claim is honest.** The report as a whole was
murderboarded on 2026-08-16 (`docs/reviews/coordination_report_2026-08-17.md`, 11/11,
2 rounds). This run covers **the replaced section 3 and its effect on the rest of the
page** — it is the process's small-deliverable mode: every role walked in turn against
the changed section, role 10's table produced against the rebuilt render. Sections 0–2
and 4–6 were not re-reviewed except where section 3 could have contradicted them
(role 3). Same subagent deviation as the landscape run, and recorded there.

## Role ledger

| # | role | findings |
|---|---|---|
| 1 | Claim & data verifier — "Prove It." | none — every claim in the new section is a subset of the landscape page's, verified in that run |
| 2 | Citation & reference validator — "DOI or Die." | none — DOSED, cnn-ripple, SEED, CASCADE, Mölter, Russo & Durstewitz all traced to full texts on the shelf; SpikeNet, the one unretrieved paper, is **not** cited in this section |
| 3 | Consistency auditor — "Cross-Examiner." | **1** — S1 |
| 4 | Adversarial reviewer — "Reviewer 2." | none — the section withdraws a claim rather than making one; the replacement claim is the narrow positional one, and its ⚠ tail states what is still unestablished |
| 5 | Line editor — "Kill Your Darlings." | none — the section is a withdrawal, a pointer and a replacement claim, each doing one job |
| 6 | Methods / domain expert — "RTFM." | none — no new analysis code underlies this section; the coactivity-gate description was checked word by word against Mölter's methods in the landscape run |
| 7 | Reuse auditor — "Reinventing the Wheel." | none — no code changed; the section reuses the page's existing `.note` and `.verdict-line` components rather than introducing new styling |
| 8 | Naive-reader accessibility — "You Lost Me." | none — the terms it introduces (DOSED, cnn-ripple, SEED, coactivity gate) are each given their substrate and what they emit at first use |
| 9 | Density & figure-first — "Show, Don't Tell." | **1** — S2 |
| 10 | Build & craft gate — "Ship It." | **1** — S3, plus the table below |
| 11 | Argument order — "Start With the Problem." | none — see below |

### Role 11 — no findings, and here is what I checked
Section 3's position in the report's spine. It sits after the two models are described
and before the comparison against the six, which is where a novelty question belongs:
the reader has seen what the thing *is* and has not yet been given its score, so the
"is it new" question arrives somewhere it can be judged and does not pre-empt the
evidence. Within the section the order is withdrawal → pointer → the two further
corrections → the surviving claim → the ⚠ tail. The retraction leads, which is correct:
a reader who stops after one paragraph leaves with the correction rather than the claim.

## Findings and adjudications

**S1 · Cross-Examiner · major · FIXED (in the landscape run).** Section 3 and the
landscape page state the same permutation-null rule, the same CASCADE precedent and the
same "membership, never event timing" claim. Checked they agree word for word on the
percentile (95th, SVD 99th), the iteration count (a thousand), and the count of
algorithms benchmarked (eight). They do. The one number that could have drifted — the
read-status count — is quoted only on the landscape page, so it cannot disagree here.

**S2 · Show, Don't Tell · minor · NO CHANGE, deliberate.** The section is prose-only in
a report where every other section carries a figure. The picture that belongs here is
the landscape map, and duplicating it would put the same figure on two pages that ship
together. The section links to it instead. Recorded rather than fixed so the choice is
visible.

**S3 · Ship It · major · FLAGGED ⚠.** The section links to the companion page as a
**relative** href (`landscape.html`). Both pages are self-contained single files, so the
link works only where the two sit in the same directory. In `docs/learned/` they do. If
the report is copied to the darkroom or the site **without** the landscape page beside
it, the link dead-ends — and the report's central retraction points at it. Not fixable
inside the page; it is a publication constraint, carried to the delivery message and to
the residual list below.

## Role 10 — build & craft table

Checked against the rebuilt `coordination_report.html` (1541 KB), section 3 scrolled
into view at 1000 px width.

| element | build current | overlap / off-page | every mark identified | verdict |
|---|---|---|---|---|
| section 3 heading + lead | html rebuilt after the source edit | none | n/a | pass |
| `.note` withdrawal block | same build | none; block sits clear of the heading above and the prose below | the three withdrawn-against methods each carry author, year and substrate | pass |
| companion-page link | same build | none | link text names the page rather than saying "here" | pass, but see S3 |
| `.verdict-line` surviving claim | same build | none; green rule renders at full block height | n/a | pass |
| ⚠ tail | same build | none | the warning glyph renders and is not the only carrier — the text says "still not established" | pass |
| rest of page | unresolved-token scan clean; no `{{...}}` survived | not re-inspected (out of scope, see Scope) | — | n/a |

## Residual ⚠ — for the human

1. **⚠ S3 — the two pages must publish together.** `coordination_report.html` links to
   `landscape.html` relatively. Wherever the report goes, the landscape page goes with
   it, or the retraction points at nothing.
2. **⚠ Inherited from the report's own review**, unchanged by this edit and still live:
   the corpus is simulated, every learned number is one training run per fold, and no
   seed error bars exist. Section 6 states these.
