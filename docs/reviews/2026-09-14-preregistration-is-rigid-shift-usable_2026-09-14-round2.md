# Murderboard run, blind round — the amended rigid-shift pre-registration

## The problem this round was for

Tony adopted eleven amendments to the signed pre-registration and capped review at **one blind
pass** before building. The question was the same as the first round's: **if the run were built
from this page, could its result be read?** The eleven roles saw the amended page only, not the
first round's findings.

## What was found

**Not yet.** The amendments closed most of what the first round found, but the page still cannot
be executed without someone deciding things after the data exist. Severity did not fall: the
first round's structural finding (a rule that cannot be read) came back in a new form. The
process calls that a structural problem, and the round cap is reached, so this record escalates
to Tony rather than patching again.

**Four holes that stop the build, each found independently by several roles:**

1. **A cell can hold two results at once, and two gates cannot fail at all.** "Decided FAIL" is
   defined only for the leak gate. A count or destruction miss is neither FAIL nor UNDECIDED, and
   FAIL, VOID and UNDECIDED overlap with no precedence (Prove It, Cross-Examiner, Reviewer 2, Kill
   Your Darlings, You Lost Me).
2. **The outcome rules contradict themselves.**
   - **The negative control:** it both "voids the stream" and "decides nothing".
   - **PASS on one stream with UNDECIDED on the other:** it ends in UNRESOLVED with nothing read,
     which is worse than PASS with FAIL, and it can never resolve.
   - **The group rule:** its output is not an input to the table, and it fires about 15 % of the
     time on a perfect surrogate.
   - **The "fixable instrument" escape from STOPPED:** a judgement with no criterion.
3. **The saturation exclusion is inverted.** It ungates exactly the K at which the shifted event
   still sits in one bin, which is the failure the destruction gate exists to catch. At slow
   1.4 s on the 2.0 s bin every K is ungated, so that cell is VOID by construction (Prove It,
   Reviewer 2, RTFM, Cross-Examiner).
4. **The leak classifier is not coordination-blind under rigid shift.** Its edge-band features
   are pooled by median over ROIs. A shift of a few seconds moves an event's members across the
   5 s edge band independently, so the classifier sees coordination being removed.
   - **With coordination planted:** rigid shift at 5 s read 0.58–0.62 on synthetic data.
   - **Without the edge-band features, or without coordination:** it read about 0.50.
   - **Consequence:** a leak FAIL at the larger displacements can mean the surrogate worked
     (Reviewer 2).

**Also found, below the build line:**
- **The can-pass check** calls a perfect surrogate UNDECIDED about a quarter of the time, and can
  overrule a candidate that already passed (RTFM, Reviewer 2).
- **Five twins** under-cover a 98.33 % bound (5–9 % against 1.67 %).
- **The slow displacements** do not follow their stated rule.
- **Cossart's destruction measure** does register removal, contrary to the signed text.
- **`destruction`** needs four code changes the page does not list, and the salting test cannot
  see the seeds that matter (Reinventing the Wheel).
- **Readers applying the page top-down** use superseded text first: there is no supersession map,
  the build list is stale, and a live "do not run" order still stands (Start With the Problem,
  You Lost Me, Show Don't Tell).

**What held:**
- **Leak bootstrap:** the refitting mouse bootstrap is valid, and it is cheap at about 7 s.
- **Count gate:** its arithmetic and its `edge_thinning` control work (−4.2 % to −5.7 %).
- **Graded destruction control:** `freeze_half` on homogeneous resample is valid at K = 4.
- **Do-nothing control:** with a separate seed it now can fail.
- **Negative control:** its chance rates are right.

## Why patching again would repeat the loop

Each round turns prose into a rule, and eleven readers each find a different reading of it. The
rule now has three levels (cell, stream, overall), four results, seven overrides and three gates
with controls. That is a decision procedure, and prose is the wrong medium for one. **The
remaining defects are exactly the kind a test suite catches and a reader does not**: overlaps,
unreachable branches, a gate that cannot fail, an exclusion that inverts its purpose. Several
roles found them by writing synthetic walk-throughs, which is testing done by hand.

## Recommendation for Tony

**Make the rule code, not prose.**
1. **Write each gate and the outcome classifier as functions**, before any real data are read.
2. **Test them against synthetic cases that force every branch:** a leak-free surrogate must
   pass, a known leak must fail, a surrogate that leaves coordination must fail destruction, and
   every combination of cell results must land in exactly one outcome.
3. **The pre-registration becomes those functions and their tests**, hashed and committed. The
   page shrinks to the question, the data, the displacements and a pointer to the commit.

A review of that is a review of tests that either pass or fail, not of sentences.

**The fixes the code should carry**, all taken from this round's reports:
- **Precedence:** VOID before FAIL before UNDECIDED before PASS.
- **Decided FAIL for count:** the interval lies wholly outside ±2 %.
- **Decided FAIL for destruction:** the 1.67th percentile of retained is above 0.25 at a gated K.
- **The negative control voids the stream.**
- **Any PASS paired with a non-PASS is NARROWED.**
- **No saturation exclusion.** Gate every visible K.
- **Leak features:** edge-band columns out of the gating features.
- **The can-pass check** tests interval width, never overrules.
- **Twins:** 20, not 5.
- **The group rule** uses the lower bound, Bonferroni over four groups.
- **STOPPED** carries a closed list of instrument defects.

**The other option is to stop the goal here, which is also a legitimate result.** Two rounds of
eleven roles found no way to read rigid shift's usability without substantial new
infrastructure. That is informative about the cost of this route, though not about whether it
works.

## What this run does not warrant

This review found defects and did not fix them. It is not a correctness proof. The convergence
table measures how quickly reviewers stopped finding things, not whether anything remains.

---

## Appendix — run header and role ledger

- upstream:  syncytium2/murderboard @ 08f5ddb
- copy:      vendored @ 08f5ddb
- freshness: current
- artifact:  docs/proposals/2026-09-14-preregistration-is-rigid-shift-usable.md (2c9813d5c17a7c946c9c7690ae77f59c9a5fdaf6 -> unchanged)
- roles:     11 of 11 run (fallback grants: spawned by name, 7 of 11 declared MISMATCH on Grep and Glob)
- reports:   2026-09-14-preregistration-is-rigid-shift-usable-round2-roles/
- rounds:    2 of the process's 3 — unconverged; stopped at the cap Tony set (one blind pass after amendment)

Mode: standard

The role reports are verbatim except that machine-local absolute paths were replaced with
placeholders, because this repository is public and sapper SAP004 blocks personal paths. The
archive is named without an underscore because `murderboard_roster.sh` strips underscores from the
`reports:` path.

**Stopping reason:** round cap reached, and blocking severity did not fall. First round: blocking
findings in 6 of 11 roles. This round: blocking or high findings in 7 of 11 roles. Escalated to
Tony under the process's rule for severity that does not fall.

**Blindness and contamination.**
- **Blindness:** no role opened the first round's reports. Ship It saw one line from that
  archive in a sapper grep it was asked to run. The line argues for figures before data; it
  quotes no outcome.
- **Contamination:** no role read or quoted rigid_shift outcomes at declared displacements.
  - **DOI or Die** read rigid-shift and joint-ISI rows to verify numbers the page already quotes.
  - **Prove It** read uniform-dither positive-control values, which are not the candidate's.

**Findings by severity, this round** (counts of rows as graded by each role):

| role | blocking | high or major | medium | low or minor |
|---|---|---|---|---|
| 1 · Prove It | 3 | 6 | — | 6 |
| 2 · DOI or Die | 0 | 3 | — | 11 |
| 3 · Cross-Examiner | 0 | 6 (high) | 16 | 5 |
| 4 · Reviewer 2 | 2 | 4 (high) | 7 | 4 |
| 5 · Kill Your Darlings | 2 | 5 (high) | 5 | 13 |
| 6 · RTFM | 0 | 2 (high) | 5 | 6 |
| 7 · Reinventing the Wheel | 0 | 2 (high) | 11 | 6 |
| 8 · You Lost Me | 6 (incl. readability) | 7 (high) | 8 | 4 |
| 9 · Show, Don't Tell | 0 | 4 | — | 6 |
| 10 · Ship It | 0 | 0 | 1 | 9 |
| 11 · Start With the Problem | 3 (critical) | 6 | — | 4 |

### Role ledger

**1 · Prove It** — GRANT 1 MISMATCH — missing Grep, Glob; holds no forbidden tools (held: Read, Bash)
Cell outcomes cannot be computed, destruction gating is under-specified, the group rule has no table row. The saturation exclusion is inverted, the slow rationale is wrong, and the Cossart exclusion is contradicted by its own controls.

**2 · DOI or Die** — GRANT 2 MISMATCH — missing Grep, Glob; holds no forbidden tools (held: Read, Bash, WebSearch, WebFetch)
The refitting bootstrap is Jiang, Varma & Simon 2008 (uncited), and its bias pulls toward PASS. The choice and the test of *J* reuse the same data (Kriegeskorte 2009). The published dithering wraps to keep counts; this run does not (Louis 2010). The 1 s and 2 s bins are uncited conventions.

**3 · Cross-Examiner** — GRANT 3 ok — Read, Grep, Glob
Six high findings: overlapping cell results, no decided-FAIL for two gates, the negative-control contradiction, a void Cossart narrowing silently, outcomes that do not improve monotonically, and the group rule against VIABLE. The 96.67 % interval is a changed threshold, not an unchanged one.

**4 · Reviewer 2** — GRANT 4 MISMATCH — missing Grep, Glob; holds no forbidden tools (Read and Bash only; no Edit, Write or NotebookEdit)
The edge-band features see coordination under rigid shift: 0.58–0.62 against 0.50, synthetic. No decided-FAIL for count or destruction. The can-pass check overrules. PASS with UNDECIDED is a dead end, and the "fixable" escape has no criterion.

**5 · Kill Your Darlings** — GRANT 5 ok — Read, Grep, Glob
No banned construction; six blocks over 120 words (tool run by the main thread). Two blocking ambiguities: decided FAIL, and the negative control. High: the outcome rows, K units, the bin width, the STOPPED rule and the group rule.

**6 · RTFM** — GRANT 6 MISMATCH — missing Grep, Glob; holds Read, Bash, WebSearch, WebFetch and no forbidden (editing) tools
The saturation rule removes the failure cases, making slow 1.4 s VOID by construction. The can-pass check reads a perfect surrogate as UNDECIDED 24 % of the time. The refit bootstrap is valid but conservative (P(pass | perfect) ≈ 0.76). Five twins under-cover. Salting misses several seeds.

**7 · Reinventing the Wheel** — GRANT 7 MISMATCH — missing Grep, Glob; holds Read, Bash (no editing tools held)
Every named instrument exists and has tests. `destruction` needs four code changes; the refitting bootstrap needs a public scorer; there is no saturation table and no occupied-frame count; the negative-control pairings are fixed across seeds; a salted seed can crash `forced_choice`.

**8 · You Lost Me** — GRANT 8 ok — Read, Grep, Glob
The owner can follow the page; a session building from it cannot. There is no supersession map, cell results overlap, decided FAIL is missing, and the destruction bin and visibility threshold cannot be computed. "Cell" collides with the biological sense.

**9 · Show, Don't Tell** — GRANT 9 MISMATCH — missing Grep, Glob; holds no forbidden tools (held: Read, Bash)
The outcome rule has three levels over five places, and 12 of 16 stream pairs end UNRESOLVED. An outcome-decision figure, a window-layout figure and a supersession table are needed before the run.

**10 · Ship It** — GRANT 10 MISMATCH — missing Grep, Glob; holds no forbidden tools (holds Read, Bash)
GitHub renders correctly; Python-Markdown flattens two-space nested lists. Blob confirmed and pushed. Sapper and the quote check clean. One blind-exposure line came from a requested grep.

**11 · Start With the Problem** — GRANT 11 ok — Read, Grep, Glob
A top-down reader applies superseded text before reaching any override: no early pointer, a stale build list, a live "do not run" order, and overrides out of body order.

### Residual ⚠
- ⚠ The page is not buildable as amended. Tony's decision is between a code-first rule and stopping the goal.
- ⚠ Nobody has asked Grün's group about the non-wrapping variant, and no statistician has reviewed using bootstrap case cross-validation to show a classifier cannot separate the two sets.
