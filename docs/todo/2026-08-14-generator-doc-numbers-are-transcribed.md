---
status: open
filed: 2026-08-14
---

# `generator.md`'s numbers are transcribed by hand, and drift silently

Two blind murderboard rounds on `docs/generator.md` found 15 and 20 findings with
little overlap. The overlap being small is the finding: it is one defect wearing
many faces.

**Roughly sixty quantities in that document are copied by hand out of
`bugarach.bench`.** The bench was recalibrated three times in two days — invented
values → measured values → baseline-only regimes — and each recalibration
invalidated a different subset of them. Prose does not fail a test, so nothing
said so.

## The clearest instance

Three review passes produced **three different counts** of how many operating
points a sweep beats: four, five, three. Each was correct for its own run. The
answer turns on ties in the third decimal (CoactDetect 0.768 against 0.776) that
reverse with the seed, so the quantity was never stable enough to state. It has
been removed from the document rather than corrected.

## The fix

Generate the numeric sections the way the figures are generated: a build step
that renders the bench tables into the document, so a recalibration either
updates the prose or breaks the build. Candidates:

- a `tools/render_generator_doc.py` that fills a template from
  `bugarach.bench` — same shape as `make_generator_figures.py`, and it can reuse
  `score_table`'s formatting;
- or a test that re-derives every quoted number and asserts it, which is cheaper
  to write and catches drift without restructuring the document.

The second is probably the right first move: it needs no template, and it turns
"the doc drifted" into a red test rather than a review finding.

## Until then

`generator.md` needs a review pass after **every** calibration change, and should
be assumed stale between them. Anyone quoting a number out of it should re-derive
it first.
