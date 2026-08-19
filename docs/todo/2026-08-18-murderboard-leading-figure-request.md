---
status: open
filed: 2026-08-18
upstream: syncytium2/murderboard#16
---

# Filed upstream: murderboard should require a leading figure

**Do not edit the vendored murderboard to add this.** `docs/doc_review_process.md`
and `.claude/skills/murderboard/` carry a provenance stamp and are re-copied, not
patched — an edit here is lost at the next refresh and, worse, makes this repo's
copy disagree with the freshness gate that reports it current.

The request is
[syncytium2/murderboard#16](https://github.com/syncytium2/murderboard/issues/16),
filed 2026-08-18 at Tony's request.

## What was asked for

That a document making a case must **open with a figure a reader can orient from** —
one image, before the prose, answering "what am I looking at and why does it matter"
without being read.

## Why it is not already covered

- **Role 11 ("Start With the Problem")** owns the cold open, but judges **which claim
  arrives first**; its output contract is one sentence per section stating that
  section's claim. A document that opens with the problem in excellent prose passes it.
  Its founding incident was about a *picture* — "the one slide that showed what the
  problem actually LOOKS LIKE was slide 6 of 12" — and the rule that came out of it is
  about *order*.
- **Role 9 ("Show, Don't Tell")** asks what should be a picture, but per page. A
  deliverable can satisfy every per-page threshold and still put its first figure on
  page three.

No role owns the reader's first five seconds.

## Our own evidence, which is why it was filed

`docs/learned/coordination_report.html` went through all eleven roles and opened on
its **method** — the pipeline diagram — because that is what had been asked for. Role
11 caught it in the blind pass, and the fix applied was *to add a figure of the problem
before anything else*. The rule was being applied by hand, one round from shipping
without it. The proposal is to extend role 11's cold-open bullet rather than add a
twelfth role, since a new role costs every consumer a subagent forever.

## What to do here

**Nothing, until upstream decides.** When it lands, refresh the vendored copies by
re-copying and bumping the stamp — `bash tools/check_vendor_freshness.sh` with
`BUGARACH_INTERFACE2` set — and close this file. If upstream declines, close it and
record the reasoning, because the next session to notice the same gap will otherwise
file it again.
