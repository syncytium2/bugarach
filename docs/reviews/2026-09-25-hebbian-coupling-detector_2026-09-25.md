# Murderboard run — the Hebbian coupling detector proposal

## The problem this review was for

Tony proposed a detector in which each region of interest (ROI) is a unit coupled to every other,
with couplings strengthened by coincident calcium-event onsets. The draft took its learning rule
from von der Malsburg & Schneider's 1986 cocktail-party processor, as transcribed in
syncytium2/clamor. The question for the review: **if Tony approved this plan, would its stages
produce a result anyone could read, and would the rule be what the page says it is?**

## What was found

**Not yet, and the second round found the reason is structural, not editorial.**

The first round took the draft apart. Its bound was not in the code it planned to copy. At the
paper's step size, a coupling pins at the clamp after one same-frame coincidence. Its kernel was
rate-neutral only on a whole-frame span, and none of the proposed spans was one. Its busy-core
check could not flag a pure core. Its per-frame call scored the frames it had learned from, and
its central zero-integral argument was Kempter, Gerstner & van Hemmen (1999), not new. The
revision fixed all of that, added Figure 1 and reordered the page to open on the gap it fills.

The second, blind round then found two problems patching will not retire:

1. **In the step range that avoids the clamp, the rule reduces to a correlogram.** Below
   *q*₀ = 0.0048 each coupling is close to *q*₀ times a sum of kernel weights. Standardizing to *Z*
   cancels *q*₀. So *Z* is a fixed, kernel-weighted cross-correlogram (centre minus flanks, close
   to Stark & Abeles 2009) with a little saturation for busy pairs. Found by Reviewer 2
   (round 2, F6) from the definitions.
2. **The busy-core stop cannot trigger as written.** Two roles simulated a pure one-core field
   independently with the repository's own `graph.sttc_matrix` and `graph.jitter_trains`. The
   stop passed in 9 of 9 recordings (Reviewer 2) and 12 of 12 (RTFM). Varying participation from
   event to event lifts eigenvalues 2–4 above any timing-destroying null. The stop needs a null
   that holds the events fixed.

Whether a kernel correlogram with saturation is still worth building is Tony's decision, not a
fix. So the loop stopped here instead of running a third round on a design he may not want.

## What would settle it

- **Decide what the rule is for.** Either keep it as a correlogram statistic and rename the page,
  or give the nonlinearity a job: a step size where saturation shapes the ranking, with the
  latch prevented some other way.
- **Rebuild the busy-core stop on the curveball (fixed-margin) null**, with controls planted as
  trains, judged per group.
- **Decide whether to publish clamor's module.** Vendoring it into this public repository
  releases a file from a private one, with its copyright notice. Tony said on 2026-09-25 that
  clamor is his to do with as he likes; that is the decision, but the page must state it.

## What this review does not warrant

This review found and fixed many defects over two rounds and did not converge. It is not a
correctness proof, and the convergence table measures how quickly reviewers stopped finding
things, not whether anything remains. Several round-2 findings are known to be wrong in the page's
body, and the page's banner lists them rather than silently correcting unreviewed text.

---

## Appendix — run header and role ledger

- upstream:  syncytium2/murderboard @ 08f5ddb (vendored stamp; upstream HEAD not reachable)
- copy:      vendored @ 08f5ddb
- freshness: UNDETERMINED
- artifact:  docs/proposals/2026-09-25-hebbian-coupling-detector.md (2300283c99f08c85c09655824366fef144133867 -> 6f5e4df151f09c26465fa71d631248b4c2a6e409 after round 1 -> a8479dcfd54b2ba862022942297fc34efd09d7f5 with the unconverged banner)
- roles:     11 of 11 run (named agents), both rounds
- reports:   2026-09-25-hebbian-coupling-detector-round2-roles/
- rounds:    2 of the process's 3 — unconverged; stopped to escalate a structural finding to Tony

Mode: standard

Round 1's eleven reports are in `2026-09-25-hebbian-coupling-detector-round1-roles/`, round
2's in the directory named above. Every report is verbatim except for one mechanical
substitution that sapper SAP004 requires in this public repository: absolute machine paths were
rewritten repo-relative, clamor paths as `clamor:<path>`, and scratch paths as `<scratchpad>`. The
reports were extracted from each agent's hand-back as it arrived and committed at once.

**Run notes.**
- The murderboard model gate is not installed in this repository, so the model and the spend
  were confirmed with Tony before the fan-out.
- `murderboard_prose.sh` is not vendored in bugarach. The main thread ran clamor's vendored copy
  (stamp `3a6a8fb`) for role 5, whose report carries the output.
- `fetch_paper.py` is deliberately not vendored (CLAUDE.md), so roles 2 and 6 fetched by hand.
  Kempter et al. 1999 was read in full; the 1986 paper and the 1981 correlation-theory report
  were not reached.
- Between rounds the main thread added `tools/make_hebbian_kernel_figure.py` and Figure 1.
  After round 2 it corrected one wrong comment and one printed line in that tool (the 0.0048
  limit applies to a step from anywhere in the band, not from rest); the figure is
  byte-identical.
- Round-1 fix outside the page: the new INDEX row's code span named a file in the private
  repo and would have turned `tests/test_index_resolves.py` red. Fixed; the test passes (483).

**Blindness.** Round 2's eleven roles were told not to open this review's files and were given
only the repaired page and its sources. Ship It and DOI or Die listed file names in
`docs/reviews/` to check the page's dead link, without opening them.

**Findings by severity per round** (rows as graded by each role, tallied by the main thread;
approximate where a role's scale differs, e.g. "high" is counted with "major"):

| round | blocking | high or major | medium | low or minor |
|---|---|---|---|---|
| 1 | 12 | 41 | 52 | 55 |
| 2 (blind) | 9 | 34 | 52 | 70 |

**Stopping reason:** a structural finding in round 2, the rule's reduction to a correlogram and a
stop that cannot trigger, is a design decision for Tony. Blocking findings fell (12 → 9), but not
to the floor. No round 3 and no follow-up pass were run.

### Role ledger

**1 · Prove It** — GRANT 1 ok — Read, Grep, Glob, Bash
Round 1: 15 findings, 2 high. The bound needs the clamp; no proposed span was a whole number of
frames. Round 2: 16 findings, 4 high. The stated reason for the 3–6 sweep is refuted by the tool's
own numbers. "Records the sign of its first pair" is false. σ was re-measured on 2026-09-23.
clamor is private.

**2 · DOI or Die** — GRANT 2 ok — Read, Grep, Glob, Bash, WebSearch, WebFetch
Round 1: 12 findings, 2 high. The rate-neutrality argument is Kempter et al. 1999, and clamor's
own record contradicted the page on what fails. Round 2: 13 findings, none high. Every DOI
checks. ADR-0008 does not rule on the unit of replication. The Schneider thesis, Masquelier et al.
2008 and the fast-weights lineage are residual ⚠.

**3 · Cross-Examiner** — GRANT 3 ok — Read, Grep, Glob
Round 1: 29 findings, 3 high. Round 2: 24 findings, none blocking. The subliminal rule is stated
two ways; "stream", "call" and "arm" collide with the glossary; the vendoring publishes a private
module.

**4 · Reviewer 2** — GRANT 4 ok — Read, Grep, Glob, Bash
Round 1: 21 findings, 8 blocking. Round 2: 18 findings, 3 blocking. The busy-core stop passed
9 of 9 simulated pure cores. The recovery test is tuned on its own metric. *Z* is 0/0 for pairs
that never update. The standardized rule is a correlogram.

**5 · Kill Your Darlings** — GRANT 5 ok — Read, Grep, Glob
Round 1: 24 findings, 3 high. Round 2: 19 findings, 2 high: "stream" is used in the paper's
sense, and the subliminal rule is inconsistent. Rate neutrality is stated five times. No banned
constructions in either round.

**6 · RTFM** — GRANT 6 ok — Read, Grep, Glob, Bash, WebSearch, WebFetch
Round 1: 14 findings, 5 high. Round 2: 14 findings, 2 high. The busy-core stop passed 12 of 12
simulated pure cores. Flooring grid onsets without a tolerance moves 4–32 % of them. The weighted
stochastic block model is a partition model and cannot give overlapping groups.

**7 · Reinventing the Wheel** — GRANT 7 ok — Read, Grep, Glob, Bash
Round 1: 15 findings, 4 high. Planted overlapping groups and stored STTC matrices do not exist.
Round 2: 14 findings, none high. `surrogates.shipped_dither` already is the frame-snapped jitter.
The modularity driver should host the busy-core check. `ONSET_FIELD` is unnamed. The figure tool's
darkroom fallback departs from its siblings.

**8 · You Lost Me** — GRANT 8 ok — Read, Grep, Glob
Round 1: 21 findings, 3 blocking; nearly every section had three or more undefined terms.
Round 2: 21 findings, 5 blocking: "clamor" is never introduced, and four sections still use
undefined terms. Figure 1C's triangles and colours mislead.

**9 · Show, Don't Tell** — GRANT 9 ok — Read, Grep, Glob, Bash
Round 1: 8 findings, 4 major; nine prose-only pages, no figure. Round 2: 11 findings, 5 high.
Figure 1 gets 46 % of its page and its text renders at 7–9 px. Eight more candidate figures are
named.

**10 · Ship It** — GRANT 10 ok — Read, Grep, Glob, Bash
Round 1: 3 findings, 1 blocking: the INDEX row turned the index test red (fixed). Round 2:
10 findings, 1 blocking: the dead link to this record, closed by writing it. The PNG has a 22 %
blank band; panel C's marker collides with the clamp line; colours are reused across panels.

**11 · Start With the Problem** — GRANT 11 ok — Read, Grep, Glob
Round 1: 7 findings, 2 major. There was no problem statement and no "what is asked"; both were
added. Round 2: 9 findings, none above medium. The page opens on definitions, the gap's "a stop
that ends one ends both" is contradicted later, and Figure 1C's finding arrives six sections
before its explanation.

### Residual ⚠ for Tony

- The two structural findings above.
- The decision to publish clamor's `malsburg1986.py` (and its copyright notice) in a public repo.
- Has anyone written to von der Malsburg's group, or has clamor's interlibrary-loan request for
  Schneider's 1986 thesis come back? The thesis is the source most likely to settle the step
  size.
- Papers not read: the 1986 PDF (held by Tony), the 1981 report (open access, blocked here), the
  Schneider thesis. Literatures not searched: fast weights, STDP as a pattern detector
  (Masquelier et al. 2008), and oscillator synchronization.
