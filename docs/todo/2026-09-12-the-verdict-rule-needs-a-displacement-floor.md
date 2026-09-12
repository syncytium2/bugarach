---
status: open
filed: 2026-09-12
---

# The verdict rule needs a displacement floor, or it will credit surrogates that barely move anything

The surrogate screen's verdict rule is still to be designed — two review rounds stalled on it, and the
escalation left it to a session with the numbers. This is one gate that rule needs, and the published
literature states the reason.

## The trap

A screen that rewards "did not leak" ranks highest whichever candidate moves onsets least. The plan's
own review caught that shape once already and answered it with a destruction test and a do-nothing
control. The floor is the same lesson applied to the **displacement axis** rather than the candidate
axis: a candidate credited at a displacement too small to destroy coordination is do-nothing wearing
that candidate's name.

This is not hypothetical here. Most candidates that survive the per-ROI leak detector survive at a
single frame — 0.1 s — against coordination that is a seconds-scale phenomenon. See
[the join](2026-09-12-join-the-leak-results-to-the-destruction-results.md).

## What the literature says, and it says it twice

Stella et al. 2022 set their dither parameter at 15–25 ms, a multiple of the bin, and state the
trade-off in both directions: too small, and the displacement is insufficient, so significance is
underestimated; too large, and the firing-rate profile is smoothed, which makes the null inappropriate
in a different way. Their two-sided caution is the argument for a floor **and** a ceiling on *J*.

The ceiling is partly handled already — *J* is per-stream, ruled from the measurement that at 2.5 s
half of fast within-ROI intervals sit inside 2*J* against none of the slow ones. The floor is not
handled at all.

## The proposal

No candidate may be credited at a displacement where it fails the destruction test. Mechanically: for
each candidate and stream, the viable *J* range is bounded below by destruction and above by the
rate-profile and interval evidence already gathered. A candidate with an empty range is out, however
clean its leak numbers are.

⚠ **A floor defined as "wherever the control fires" is not a floor** — the same defect the second
review round found in the control gate. It must be defined against destruction of planted
coordination, which is a property of the surrogate, not of the test's sensitivity.

## Closes when

The verdict rule states a displacement floor, derived from destruction rather than from test power,
and the report applies it before any candidate is called viable.
