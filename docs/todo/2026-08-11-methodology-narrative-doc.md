---
status: open
filed: 2026-08-11
---

# Methodology narrative doc (portfolio surface)

External-facing account of how this repo was built, in the style of
interface2's `docs/sapper_description.md` — durable, reusable text for
bios, grant facilities sections, talks, and hiring reviewers. Written for
an outside audience; presentation, not process (the process docs stay
authoritative).

## Should cover

- **Parity methodology**: six detectors ported from MATLAB, each gated by
  reference fixtures generated from the originals and matched to 1e-9 in
  every mode, on synthetic AND real data — including exact reproduction of
  MATLAB's RNG streams (`rng(seed)` == `RandomState(seed)`,
  `randi(k)` == `floor(rand*k)+1`) and floating-point semantics
  (two-ended colon, mid-point prctile, NaN-ignoring max/min).
- **Clean-room reimplementation**: the peak-extent kernel rewritten from a
  behavioral spec by an implementer with no access to the original, gated
  by adversarial differential validation (independent adversary impl,
  hand-derived hostile vectors, mutant-checked fuzzer) —
  `docs/clean_room/WORKFLOW.md`.
- **Upstream bug found**: PySpike's `max_tau` cap, inert since 0.8.0,
  discovered because bit-exact cSPIKE parity made a quantitative
  inflation visible that normal use cannot detect (see the PySpike-issue
  todo).
- **Engineering hygiene**: sapper (incident-derived self-testing rules in
  CI), CI matrix, one-human/many-AI-sessions operating model with the
  repo as the only durable channel.

## Notes

- Verify all counts/claims against the tree at writing time (test counts
  drift; say "matched to 1e-9", not stale numbers).
- Home: `docs/methodology.md`, linked from the README.
