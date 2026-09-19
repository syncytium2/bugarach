# Murderboard run: why a third of chorus_norm's tuning fits do not train

## What was at stake

In both draws of goal 2's comparison, about a third of chorus_norm's inner (tuning) fits made a
single call covering the whole recording. The diagnosis page,
[`docs/learned/chorus_collapse/index.html`](../learned/chorus_collapse/index.html), says why. Its
Figure 1 shows the failure on a recording held out from both fits:
- a working fit's output rises at each planted event and makes 25 calls;
- a collapsed fit of the same configuration, trained on the same folds, gives a flat output far
  above its own threshold and makes one call.

The page is written for Tony, who asked for the mechanism rather than a hurried fix, and for outside
readers of a public repository. Its claims are about how a neural net fails to train, so an error in
it would misdirect goal 2's repair.

## What was found, and what changed because of it

**Round 1** found no wrong number. Every count recomputed from the raw archives. It found wrong
inferences:
- **The "dead layer" rule was a sign test.** GELU's negative dip carries signal, so the rule counted
  layers that still transmit.
- **The overlap between draws was read wrongly.** 111 fits collapsed in both draws, which is what the
  configurations' rates predict by chance, not evidence about particular fits.
- **One warm-up run was counted twice.**
- **The refit counts mixed in the untuned default's refits.**
- **The learning-rate story was applied to chorus_gain_norm too.** That net follows its encoder's
  shape at least as much.
- **The problem was never shown.** Role 11 rated this blocking.

**The repaired page then went to a blind round (round 2)**, and that round found problems in the
analysis itself:
- **The #596 test could not fail.** The page's test for "this is not the failure PR #596 fixed" was a
  scale-free separation measure. An untrained plain chorus, the net #596 showed was deaf, passes it
  (role 4).
- **Zero padding fooled the silent-layer measure.** The convolutions pad with zeros, so a constant
  layer still "varied" near the ends of a recording. Measured on the interior, every collapsed fit
  has a silent head layer and no working fit does (role 6).
- **Figure 1's two fits were not a matched pair.** They differed in fold pair as well as in seed
  (roles 1, 3, 4 and 6). In this runner the seed also picks the training recordings.

What changed:
- **Figure 1** now shows a pair that differs only in seed.
- **The census** runs on a fresh recording, with every variation measure taken on the interior.
- **#596's own test replaces the separation measure.** That test asks how far one onset moves a vote,
  and its controls show it can fail. It finds that most collapsed chorus_norm fits' votes still
  respond, while 4 of 153 are as deaf as plain chorus, and 19 of chorus_gain_norm's 75.
- **The replays were rerun with interior measures.** They show that every fit's head starts mostly
  silent, and that what separates the fits is whether training wakes it. That reverses round 1's
  claim that silence "follows the stall", and the page now says so.
- **What tuning chose** is now split by selection rule. For chorus_gain_norm, lr 0.03 was picked
  only on F1 alone.
- **The replicate report's reading of the 111-fit overlap** is corrected on this page, and its own
  fix is filed in the todo.

The per-round table is below. It shows blocking findings going **3 → 4**. **Severity did not fall,
so the process says stop and escalate rather than run another round.** The round-2 repairs are
applied and rebuilt, but no reviewer has seen them.

This review found and fixed many defects. It is not a correctness proof. The convergence table
measures how quickly reviewers stopped finding things, not whether anything remains.

## Convergence

| round | artifact reviewed | blocking | major | minor | outcome |
|---|---|---|---|---|---|
| 1 (first pass) | 5cafecea | 3 | 52 | 111 | repaired and rebuilt (56e5c49) |
| 2 (blind, round 1 of 3) | fe8db88a | 4 | 55 | 110 | repaired and rebuilt; **not blind-verified** |

Stopping reason: **severity not falling.** Blocking went from 3 to 4 across two rounds, so the run
is escalated to Tony instead of running blind round 2 of 3. Most of round 2's blocking findings were
not regressions. They were deeper faults in the analysis that round 1's repairs made reviewable (the
#596 test, the padding artifact, the matched pair). That is the pattern the process calls a
structural problem. Counts are per role, as each report states them, and are not deduplicated
across roles.

## Residual ⚠ for Tony

- ⚠ **The round-2 repairs are unreviewed.** These include a rebuilt Figure 1, a new Figure 4 (#596's
  test), a merged Figure 5, the interior census and replays, the selection split, and rewritten
  §§1–6. Run a blind round on the new page, or accept it with this flag.
- ⚠ **The replicate report still reads the 111-fit overlap as the same fits failing twice**, and its
  builder asserts it. This page corrects that reading, and the fix to the report itself is filed in
  [`todo/2026-09-19-chorus-norm-does-not-train-at-lr-0.03.md`](../todo/2026-09-19-chorus-norm-does-not-train-at-lr-0.03.md).
- ⚠ **The counterfactual replays are judged by training loss, not by calls on held-out
  recordings.** Role 4 asked for held-out scoring before the page says "prevents"; it now says
  "trains".
- ⚠ **"Silent" uses an absolute threshold** (standard deviation 0.001). At the starting weights some
  of the silence may be scale rather than a layer that passes nothing. The page says so in its
  Limits.
- ⚠ **Declined refactors (role 7, minor).** These are routing `replay` through `train()` with hooks,
  sharing the collapse rule with the replicate report's builder, and moving the palette tokens into
  the shared CSS. The copies are proved equal by the byte-for-byte checkpoint match and the identical
  collapse counts, but nothing guards them against drift.
- ⚠ **Literature not searched (role 2):** transformer training instability, and signal propagation
  at initialization beyond Hanin & Rolnick.

## Appendix: the run

Mode: standard
- upstream:  syncytium2/murderboard @ 08f5ddb
- copy:      vendored @ 08f5ddb
- freshness: current
- artifact:  docs/learned/chorus_collapse/index.html (5cafecea0898379c4f05434dde6e7a2d5695120c -> e477f6f2170ef1d634366304bae519fe776e5360)
- roles:     11 of 11 run (named agents)
- reports:   chorus-collapse-2026-09-19-roles/
- rounds:    1 blind round after the first pass; severity not falling (blocking 3 -> 4); escalated; round-2 repairs not blind-verified

The round-2 reports are at the archive's top level, and the round-1 reports are in `round1/`. Both
were written to disk verbatim as each arrived. Paths inside them are written as `<worktrees>`,
`<darkroom>` and `<scratch>`.

### Role ledger (round 2, blind)

| # | role | grant, as the reviewer declared it | findings | heaviest |
|---|---|---|---|---|
| 1 | Prove It | GRANT 1 ok — Read, Grep, Glob, Bash | 14, plus a 47-row claim ledger; the collapse table rebuilt from raw archives with 0 differences; both replays reproduced through `train.train` itself | major: Figure 1 fits differ in fold pair; the seed effect put on starting weights; float32 artifact in the output separation; chorus_gain_norm's lr 0.03 picked on F1 alone only; the replicate report's reading |
| 2 | DOI or Die | GRANT 2 ok — Read, Grep, Glob, Bash, WebSearch, WebFetch | 8; all 8 references exist | major: Sokar's definition misstated; warm-up credited as the known cure for this failure; the fair-comparison link dead on the branch |
| 3 | Cross-Examiner | GRANT 3 ok — Read, Grep, Glob | 21 | blocking: Figure 1's fits "differ only in seed" is false |
| 4 | Reviewer 2 | GRANT 4 ok — Read, Grep, Glob, Bash | 20 | blocking: the #596 test cannot fail (untrained plain chorus passes it) |
| 5 | Kill Your Darlings | GRANT 5 ok — Read, Grep, Glob | 28 (tool not vendored; searched by hand) | major: "run" in three senses; the round-1 history paragraph; "goal 2" as a name |
| 6 | RTFM | GRANT 6 ok — Read, Grep, Glob, Bash, WebSearch, WebFetch | 12 | blocking: zero padding fakes variation at the ends; every collapsed fit is silent on the interior |
| 7 | Reinventing the Wheel | GRANT 7 ok — Read, Grep, Glob, Bash | 10 | major: the separation measure is not #596's measure |
| 8 | You Lost Me | GRANT 8 ok — Read, Grep, Glob | 18, plus a per-section table and the false-friend check on every figure | blocking: seven undefined terms in the answer box |
| 9 | Show, Don't Tell | GRANT 9 ok — Read, Grep, Glob, Bash | 14, plus a density table | major: first figure 1,292 px down; Figures 5 and 6 should merge; Table 2 should be the loss curves |
| 10 | Ship It | GRANT 10 ok — Read, Grep, Glob, Bash | 13, one row per figure and table; build current and byte-reproducible | major: Figure 1's panels unlettered |
| 11 | Start With the Problem | GRANT 11 ok — Read, Grep, Glob | 11 | major: Figure 1 after the box; the cost to goal 2 arrives late; §3 reads causal before §4 takes it back |

Role 11's report is archived verbatim; its grant line puts a colon where the others put a dash,
and names the same three tools.

### Adjudication of round 2

Fixed:
- **Figure 1.** Now a matched pair (seed 0 against seed 2 on the same fold pair), with panels
  lettered A to C and the threshold's value outside the plot.
- **What the seed sets.** The seed sets weights, crop order and training recordings. The seed test is
  now reported per draw, with a cross-draw test, and the effect is no longer put on starting weights.
- **The #596 test.** The separation measure is replaced by #596's own test, with untrained controls.
- **Interior measures.** The census and replays measure on the interior, and the census runs on a
  fresh recording.
- **Onset of silence.** The claim is corrected: every head starts mostly silent, and the collapsed
  fit's is never woken.
- **Selection.** Split by rule, with selections counted instead of refits.
- **Counting fixes.**
  - The number of warm-up configurations is corrected.
  - The null is relabelled: doing nothing trains none.
  - The fold structure and the definition of a configuration (including the vote gain) are rewritten.
  - The threshold floor is explained as a tie-break and asserted against the declared grid.
  - The CPU re-scoring is asserted to match the run's own call counts.
- **Citations.** Sokar and the warm-up literature are cited for what they say; Gulcehre's venue is
  added.
- **Order.**
  - Figure 1 now comes before the box, and the terms before the box.
  - The cost is its own section after §2.
  - The replicate report's reading is corrected on the page.
  - The house time axis is reused.
  - Figure 2 shows encoder shape by mark.
  - Figures 5 and 6 are merged into Figure 5.
  - Figure 7 and the warm-up axes have headroom.
  - The dim green is replaced by dashed ink.

Declined, with reasons:
- **Table 2 as a chart (role 9).** It is six small counts, and its one finding is a zero that a table
  shows plainly.
- **A build stamp (role 10).** It would break the byte-for-byte rebuild test unless it came from the
  data.
- **Role 7's refactors.** Listed in the residuals above.
- **A new replay of every collapsed fit (role 4, M4).** The claim is narrowed to the one fit replayed
  and to the step-count twins instead.

### Checks

- `bash tools/murderboard_roster.sh check --require-reports docs/reviews/chorus-collapse_2026-09-19.md`
- `python tools/murderboard_agents.py --process docs/doc_review_process.md verify docs/reviews/chorus-collapse_2026-09-19.md`
