# The merge-gap addendum, murderboarded — and stopped unconverged

**The artifact:** `docs/learned/tuned_vs_coact/fair_comparison_2026_09_18/net_merge_gap.html`, the
fair comparison's addendum. The nets decoded at a fixed 2 s merge gap while the coded detectors tuned
theirs; this page tunes the nets' by the same rules, without retraining, and asks whether the verdict
moves.

**This run is delivered unconverged, and that is the headline.** Two blind rounds of the review team
produced **11 blocking findings in round 1 and 10 in round 2**. The process says what a flat blocking
count means: *"it means the artifact has a structural problem that patching will not retire"*, and it
says to stop and escalate rather than run a third round. So the fixes from both rounds are applied
and the page ships with the residual list below, for the project lead to rule on.

## What the review changed about the result, not the prose

Each of these is a claim the first draft made that its own data do not support. They are the reason
this record exists, and they are all now in the page.

1. **The set-aside was applied to one side only.** The page compared "tuned, failed refits set aside"
   against a baseline that still counted them. Scored the same way on both sides, the replicate's
   `chorus_norm` is already +0.005 F1 ahead at its as-run 2 s, and tuning adds +0.010 — one noise
   unit, not a sign flip.
2. **Every chosen gap is a boundary, not an optimum.** Held-out F1 is largest at the widest gap in the
   grid in all 64 fold-rows. The nets stopped where the crowded-recording check stopped them, and
   CoactDetect's 8 s is the top of its own grid — which stops there because goal 1's crowded check
   refused its 16 s. The two sides landing together is not agreement, and the first draft read it as
   convergence.
3. **The crowded cost was charged against the wrong reference.** What the page reported is each net
   against its own 2 s. On the same recordings, head to head, the tuned chorus nets *beat* CoactDetect
   by 0.016 to 0.056 F1 while `tube` loses 0.142. Both are now drawn (Figure 5).
4. **The noise scale was named for something its source does not measure.** The 0.010 F1 is a median
   absolute move between two draws that differ in recordings *and* in the machine that trained them,
   and the same source measures a systematic **+0.015 F1 shift in the nets' favour in the replicate's
   draw** — the size of the lead being read as corroboration there.
5. **The mechanism under the budget was wrong.** "A wider gap lets a net fit the budget at a lower
   threshold" is refuted by the run: the chosen threshold is unchanged in 26 of the 32 gated choices.
6. **The budget bound one side only.** CoactDetect's F1 under the budget equals its F1 alone in every
   fold of both draws, while 44 of the nets' 160 budget-chosen refits are over budget on the fold they
   were scored on (41 as run).
7. **"A wider merge can only delete duplicate calls" is too strong.** Held-out F1 dips somewhere in 18
   of the 64 fold-rows; merging chains, and the project's glossary already recorded that.

## What would validate this, and what generalises

The single cheapest check that would move the result is the one nobody has run: **CoactDetect on the
crowded recordings with no merging at all**, which would say whether its 8 s gap is bought on the same
terms the nets' is. The page now says that comparison is missing rather than asserting its outcome.
Beyond this artifact, two habits generalise. A post hoc exclusion must be applied to the baseline as
well as the treatment, or the treatment inherits the exclusion's effect — that defect survived a first
round of eleven roles here and was caught only when a reviewer recomputed the baseline itself. And a
selection that is bounded by a check must report where the boundary is: reporting the chosen value
alone made a censored choice look like an optimum on this page for two rounds.

## Residual ⚠ — open, and not fixed

- ⚠ **Unconverged.** Blocking findings did not fall between rounds (11 → 10). The recurring shape is
  scope: a multi-factor result (two draws × two selections × four nets × two treatments × two
  variants) restated in prose, where each repair adds surface for the next round. A third round was
  not run, per the process's own escalation rule.
- ⚠ **The 0.02 F1 crowded allowance is unsigned** and decides every gap on this page. One refusal
  turned on 0.0009 F1, against a quantity that moves as much as 0.045 F1 between the fits the check is
  enforced on and the refits that produce the number. No sensitivity at other allowances was run.
- ⚠ **Two accepted choices fail the crowded check** when re-measured on the outer refits, by 0.063 and
  0.024 F1 against the 0.02 limit. They stay inside the reported means, marked in Table 1.
- ⚠ **The re-chosen-configuration column is missing non-randomly**, in 6 of 16 rows, precisely where
  the search preferred a configuration the run never refitted. Nothing here retrains.
- ⚠ **The reproduction check covers 2 s only** — the gap that was already run. Every number the result
  rests on is at 3 to 30 s and has no independent check.
- ⚠ **The set-aside cannot be even-handed.** CoactDetect has one value per fold and no refits, so
  dropping low refits can only move a net's margin upward. The page says so and reports both.

---

## Appendix

- upstream:  syncytium2/murderboard @ 08f5ddb
- copy:      vendored @ 08f5ddb
- freshness: current
- artifact:  docs/learned/tuned_vs_coact/fair_comparison_2026_09_18/net_merge_gap.html (c52fe2b -> rebuilt clean at each round; the shipped build is the one committed with this record)
- roles:     11 of 11 run (named agents) in round 1; 5 of 11 re-run blind in round 2
- reports:   net-merge-gap-2026-09-19-roles/
- round 2 reports: net-merge-gap-2026-09-19-round2-roles/ (roles 1, 3, 4, 8, 10)
- rounds:    2 blind rounds, stopped unconverged

Mode: standard

Findings by severity, per round, counted from the archived reports:

| round | blocking | notes |
|---|---|---|
| 1 (all 11 roles, blind to each other) | 11 | roles 4 (3), 8 (3), 10 (2), 5, 6, 11 (1 each) |
| 2 (roles 1, 3, 4, 8, 10, blind) | 10 | roles 8 (5), 4 (4), 10 (1) |

**Stopping reason: severity did not fall.** The process's rule is to escalate rather than run a third
round, which is what this record does. It is not a clean run and must not be read as one.

### Role ledger

Round 1, every role, with the grant each declared:

| role | grant declared | outcome |
|---|---|---|
| 1 Prove It | GRANT 1 ok — Read, Grep, Glob, Bash | 12 findings; every statistic in Table 1 and every figure coordinate recomputed and matching; found the refuted budget mechanism |
| 2 DOI or Die | GRANT 2 ok — Read, Grep, Glob, Bash, WebSearch, WebFetch | 12 findings; Nadeau–Bengio verified to its DOI and its factor; found that the noise scale's source contradicts the use made of it |
| 3 Cross-Examiner | GRANT 3 ok — Read, Grep, Glob | 16 findings; decoded every SVG mark against the JSON; found the stale fold number in the goal page |
| 4 Reviewer 2 | GRANT 4 ok — Read, Grep, Glob, Bash | 3 blocking, 9 major; the one-sided set-aside, the powerless coded check, the censored boundary |
| 5 Kill Your Darlings | GRANT 5 ok — Read, Grep, Glob | 23 findings; the lede's headline attributed two nets' results to one |
| 6 RTFM | GRANT 6 ok — Read, Grep, Glob, Bash, WebSearch, WebFetch | 15 findings; confirmed no leak, the threshold rule and the pooling; found the unreported crowded cost of accepted settings |
| 7 Reinventing the Wheel | GRANT 7 ok — Read, Grep, Glob, Bash | 11 findings; confirmed the rules are imported not copied; found the hand-carried noise constant and the unrecorded tool provenance |
| 8 You Lost Me | GRANT 8 ok — Read, Grep, Glob | 25 findings, 3 blocking; the seconds-labelled axis at equal spacing |
| 9 Show, Don't Tell | GRANT 9 ok — Read, Grep, Glob, Bash | 14 findings; measured the page at 80% prose by area; asked for the F1-versus-gap figure, now Figure 1 |
| 10 Ship It | GRANT 10 ok — Read, Grep, Glob, Bash | 2 blocking, 9 major; the clipped key, the merged crosses, the overlaps, the sub-floor type |
| 11 Start With the Problem | GRANT 11 ok — Read, Grep, Glob | 11 findings; the crowded-check finding was section 5 and absent from the lede |

Round 2, blind, against the rebuilt page:

| role | grant declared | outcome |
|---|---|---|
| 1 Prove It | GRANT 1 ok — Read, Grep, Glob, Bash | 15 findings; all 16 table rows and all four figures recompute exactly; found the 0.388 band bound and the rate detector's 0.1 s gap |
| 3 Cross-Examiner | GRANT 3 ok — Read, Grep, Glob | 16 findings; found the same-GPU claim false for the replicate's 1,943 fits |
| 4 Reviewer 2 | GRANT 4 ok — Read, Grep, Glob, Bash | 4 blocking, 14 major; the crowded head-to-head, the unmeasured no-merge comparison |
| 8 You Lost Me | GRANT 8 ok — Read, Grep, Glob | 34 findings, 5 blocking; the inverted sign convention in the table's cost column |
| 10 Ship It | GRANT 10 ok — Read, Grep, Glob, Bash | 1 blocking, 5 major; the shipped page was built before the panel-width fix |

Roles 2, 5, 6, 7, 9 and 11 were **not** re-run in round 2. Their round-1 findings were applied and
are listed above; they have no second-round verdict, and this record does not claim one.

### What a clean run would and would not warrant

This review found and fixed a large number of defects, several of which changed what the page is
allowed to claim. **It is not a correctness proof.** The convergence table measures how quickly
reviewers stopped finding things — and here they did not stop, which is the one thing this record is
most confident about.
