---
status: open
filed: 2026-08-28
upstream: syncytium2/murderboard
---

# "Iterate until a blind pass produces no new findings" has no stopping rule for a fixer who introduces defects

> An upstream change to the vendored process, not a bugarach one —
> `docs/doc_review_process.md` step 4. Filed here because here is where it was found,
> and the evidence is one full run:
> [`docs/reviews/learned_detector_2026-08-27.md`](../reviews/learned_detector_2026-08-27.md).

## The rule as written

Step 4 says the deliverable is not done until a fresh pass comes back clean, and the
call-up skill repeats it: *"iterate until a blind pass produces no new findings."*

That is the right instinct and it worked — the first murderboard on this artifact found
five structural defects, and the first two verify rounds each found something real that
would otherwise have shipped.

## Why it does not terminate

**A fixer with a non-zero defect rate can keep the loop alive forever.** Every repair is
a new draft of the thing it touched, so every repair can introduce a finding, so the next
round has something to find. The criterion is met only when a round of repairs happens to
be perfect — which is not a property of the artifact, and not something the loop can
drive toward.

On the run that prompted this, over eleven rounds:

- **three** rounds found defects that were in the original artifact;
- **six** found damage introduced by the previous round's repair;
- **two** found nothing.

Each round fixed roughly as much as it broke. The loop was not converging on a clean
page — it was measuring the author's error rate, at break-even, and rounds 5 through 11
cost more than half the total effort to deliver two genuine findings against six
self-inflicted ones.

The purest specimen is a single figure label, which went

    one cell, one vote  →  — soft  →  — exact  →  — exact in amplitude  →  one cell, one vote

across four rounds, ending where it began. Each change answered a defensible finding.
None of the reviewers was wrong. The artifact still oscillated, because nobody was
holding a position: **the murderboard is advisory and was treated as authoritative**, so
every finding was applied rather than adjudicated.

## The change

**Add a stopping rule to step 4, and make it about the composition of the findings rather
than their count.** The signal is free — it is visible in the round's own output:

> **Stop the loop when consecutive rounds' blocking findings are dominated by the
> previous round's repairs.** At that point the loop has stopped measuring the artifact
> and started measuring the fixer, and further rounds trade one defect for another at
> roughly one-to-one. Hand over with the residuals listed, and say in the run record that
> the loop was **stopped rather than exhausted** — those are different facts and a record
> that renders them alike is making the claim this process exists to prevent.

Two supporting notes worth carrying with it:

- **The author is allowed to decline a finding.** The process says roles return findings
  and the synthesis step adjudicates them (*fix / flag-inline `⚠` / no-change*), but in
  practice `no-change` is never exercised, because declining feels like the defect the
  review exists to catch. Say plainly that a finding may be answered with *"correct in
  isolation, and the body already qualifies it"* — and that an artifact which oscillates
  between two defensible readings is evidence the author never used that option.
- **Verify the repair inside the round that made it, not in the next one.** Committing a
  round's fixes before anything re-reads them guarantees the pattern above: each fix stays
  unvalidated for a full round. Step 4 already asks for a re-run of the craft pass on the
  corrected render; the same should apply to every *claim* the round touched.

## What this does not argue

It does not argue for fewer rounds in general, and it is not an argument against the
murderboard. Round 1 of this run was transformative, and the guards that came out of the
loop (`tests/test_svg_labels.py`) found two live defects on a **different** published page
that nobody was reviewing. The complaint is narrow: the loop has no principled exit, and
in its absence an author with stamina will run it well past the point where it is doing
the artifact any good — and will mistake the continued output for continued rigor.
