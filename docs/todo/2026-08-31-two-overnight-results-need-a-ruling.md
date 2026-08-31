---
status: parked
filed: 2026-08-31
---

# Promote the 24-seed bake-off, or leave it beside the 8-seed run?

> **HELD 2026-08-31 — the question is no longer live.** Tony: *"we're going to hold on the
> 24 seed run. the input data may need revision."* Two reasons not to promote anything yet:
> the input data may change underneath it, and the run came out of the same ungated
> calibration that the next piece of work repairs. **Fix the gate, then re-run, then promote
> once** — the re-run is under ten minutes, and re-quoting ten documents twice is not.
>
> Next work: [the gate fix](../handoffs/2026-08-31-the-gate-fix-the-bakeoff-calibrates-without-one.md).
>
> Nothing below is withdrawn. The measurements stand; the hold is about what to publish,
> not about whether the numbers are right.

[`docs/learned/bakeoff_24seed.md`](../learned/bakeoff_24seed.md) has the numbers.

The shipped bake-off is 8 seeds and every F1 in the performance table rests on it. At 24
the **spread across the top four collapses from 0.043 to 0.011**, every fold range narrows,
and the order inside that group rearranges — LoCo fourth to second while tube falls from
first. **locust also crosses its promiscuity ceiling**, 30.62/min against 25, where at 8
seeds it read 21.48 and passed.

Nothing was promoted, because promotion is not a file copy: `bakeoff.json` is read by 20
modules under `src/`, `tests/` and `tools/` and quoted in about ten documents plus the
public site and several figures. Three options are set out in that file.

Checked before any of it was trusted: re-running the 8-seed configuration reproduces the
shipped file exactly — twelve detectors, six of them PyTorch fits, delta 0.0000.

---

## What this file used to also ask, and why it no longer does

It carried a second question — *which K for the Cossart assessment* — and that should never
have been a question. **K=12 was already decided**, measured across all 59 of their
recordings on 2026-08-29, written into
[the transfer handoff](../handoffs/2026-08-29-the-transfer-experiment-and-two-things-i-corrected-myself-on.md)
on `main`, and indexed by keyword in `docs/INDEX.md`. The overnight transfer ran at k=3 and
k=8 regardless, which is precisely the *"do not transplant K"* that handoff forbids in
those words.

The index would have caught it. It was not on `main` because #415 was red — from the same
briefing-budget defect this session hit independently and fixed in #418. **The fix for the
failure was written, sitting one unmerged pull request away, blocked by the bug that caused
the failure's twin.**

**This file was itself the band-aid** — a pointer added to a byte-starved channel because
the index it duplicated could not be reached. Landing the index is the repair, so the
pointer shrinks to the one decision genuinely open. The structural version of the lesson is
filed separately:
[a decision in prose will be re-derived](2026-08-31-a-decision-in-prose-will-be-re-derived.md).
