# Murderboard run — docs/handoffs/2026-08-28-the-winner-stopped-changing.md

- upstream:  syncytium2/murderboard @ f62acb3
- copy:      vendored @ f62acb3
- freshness: current
- artifact:  `docs/handoffs/2026-08-28-the-winner-stopped-changing.md` (`ea94364`, first published state)
- roles:     11 of 11 run
- rounds:    1 (stopping reason: **severity floor** — the artifact was drafted against a measurement taken for the review, so the usual round-1 findings were fixed before it was written down)

## What was at stake

An item Tony had already said he did not follow, handed over twice as *"three
tests fail and I can't tell which of two rewrites is right."* That is not a
handoff, it is a shrug with provenance. The question behind it is real — whether
the bench's background-rate axis still discriminates between detectors — and it
had never been asked as a measurement.

## What the review changed

**It refused to hand over the ambiguity.** The draft's own framing named two
readings and said the failure could not separate them. Role 4's rule is that a
null result needs a test with the power to fail, and the same discipline applies
to an undecided one: if two readings differ, ask what they differ *in*, then go
and look. They differ in whether the F1 curves flatten. That is two numbers, and
`evaluate_background_curve` already computes them.

Measured (6 seeds, `baseline_quiet`, same seeds both sides): own-range across the
axis **0.185 → 0.136**, between-detector spread **0.117 → 0.098**. Neither
collapsed, so the axis still discriminates — **reading (a)** — and the note says
so instead of listing options.

**And the measurement carried a mechanism the draft did not have.** At the
busiest rate the flat field pushes every detector into a crowded low-F1 tail
(loco 0.49, coact 0.47, cicada 0.48) where crossings are cheap; the fitted field
does not (0.62, 0.67, 0.58), because a mean increase on a Gamma-shaped field
concentrates into already-busy ROIs and leaves much of the field quiet. **The
four-place rank change was real and was happening in a regime the flat background
manufactured.** That sentence is the deliverable.

**It also caught the note nearly overclaiming its own evidence.** The failing
tests find *one* winner; this run found *two*. At six seeds the difference
between "coact wins everywhere" and "nearly everywhere" is inside noise, and a
rewrite that asserts a ranking is asserting the thing seeds move. Now a named
limitation rather than a silent one, alongside "`baseline_quiet` only" and the
fact that the mechanism is an explanation consistent with the table, not an
isolated measurement.

## What would validate it

The clean experiment is named in the note and was not run: hold the shape fixed
and move the mean, against holding the mean and moving the shape. That separates
"the background is heterogeneous" from "the background is busier" as causes,
which the current sweep confounds by construction.

## Method note

Single-pass self-review across all eleven checklists; this session cannot spawn
subagents. Role 2's separate-agent carve-out does not fire — no method is
attributed and nothing is claimed as novel. One round rather than two because the
artifact was written *after* the measurement the review demanded, so the findings
that would have been round 1 are already reflected in the text; the ledger below
records them as findings anyway, since a role that changed the artifact before it
existed is not a role with nothing to say.

## Appendix — role ledger

| # | role | findings | note |
| --- | --- | --- | --- |
| 1 | Claim & data verifier — "Prove It." | 2 | every quoted figure re-derived from the run, not scrollback; `BACKGROUND_GRID` confirmed 7 values, 0.0026→0.0400 from the module rather than the draft's memory |
| 2 | Citation & reference validator — "DOI or Die." | 0 | nothing to check: no literature, no attribution. Carve-out does not fire |
| 3 | Consistency auditor — "Cross-Examiner." | 1 | "one winner" in the test message vs "two winners" in the measurement — reconciled explicitly as a seed-count limitation rather than left as a contradiction between two tables in the same file |
| 4 | Adversarial reviewer — "Reviewer 2." | 3 | **the central one: two readings with no discriminating test is not a finding** → measured; the mechanism flagged as an explanation rather than an isolated result; "reading (a)" softened to "(a), with a caveat" because both quantities did shrink ~16–26% |
| 5 | Line editor — "Kill Your Darlings." | 1 | the answer was arriving after 400 words of setup; a pointer to it now sits in the second paragraph |
| 6 | Methods / domain expert — "RTFM." | 1 | checked that `evaluate_background_curve`'s `gen=` override really reaches the generator, so the flat arm is the old background and not a differently-seeded rerun |
| 7 | Reuse auditor — "Reinventing the Wheel." | 1 | the script duplicates what the bench already exposes; recorded as belonging in `tools/` rather than silently kept in scratch |
| 8 | Naive-reader accessibility — "You Lost Me." | 1 | "own-range" and "between-detector spread" are invented names; each is glossed in the table row that uses it |
| 9 | Density & figure-first — "Show, Don't Tell." | 1 | the tail argument was a paragraph doing a table's job → the four-row table at 0.040 Hz/ROI, which is where the whole claim lives |
| 10 | Build & craft gate — "Ship It." | 0 | Markdown, no render. Both links resolve from `docs/handoffs/`; fingerprint recorded |
| 11 | Argument order — "Start With the Problem." | 1 | opened on the test failures; now opens on the fact that it is an open decision and that the answer has since been measured |

### Residual ⚠

1. **Six seeds, one regime.** The winner count is seed-sensitive at this count;
   `baseline_busy` was not swept.
2. **The mechanism is not isolated.** It explains the table and the table is
   consistent with it; the shape-vs-mean experiment that would separate them has
   not been run.

## What this run does not warrant

Eleven roles, 12 defects, one measurement that changed the conclusion from
"undecided" to "(a)". **Not a correctness proof.** One reviewer walked all
eleven checklists, and the finding that mattered came from running a command
rather than from reading the draft — which is the third time in this estate that
has been true, and worth someone noticing.
