# Murderboard run — the rigid-shift report

## What was at stake

The report is the only artifact carrying a night's computation to a reader, and it ends on four
decisions. Two of them turned on numbers that were wrong in the direction that flattered the work.

The first round of eleven roles found eleven defects and they were repaired. **The blind second
round found that the repair had not reached the substance**: three reviewers who had never seen
round one independently recomputed the same set of inverted claims. The two that matter most were
both on the decision lines Tony was being asked to rule on.

- *"On real recordings the architecture that leads the bake-off is **last** of the four supervised
  models."* It is **third**. The sentence quoted the two models that made "last" readable and named
  neither of the two that refute it. `line` catches 0.774/0.758 of the two references' events;
  `line_length` catches 0.745/0.688 and is last.
- *"Fitting is eight times slower"*, offered as the argument **against** keeping the second sensor
  on. The eightfold cost is `line` against `tube` — a different architecture. Against its own
  ablation the second sensor costs **1.4 %** of fit time and 72 parameters. The decision brief was
  off by a factor of about 560.

A third finding changed a headline's meaning rather than its number. The report told the reader
that *"most of what these models learned needs no cross-ROI structure at all"*, citing a classifier
that reads only the pooled trace. But the pooled trace **is the share of the field that is lit** —
the very quantity the counting architecture computes. The test excludes pairwise and ROI-identity
structure, not co-activity; and its confidence interval reaches the models' own scores, so the gap
the word "most" quantifies is not resolved at all.

## What the blind round found

Fifty-one findings across eleven roles. Grouped by what they cost:

**Numbers that were wrong** (11 roles found these independently; all recomputed and fixed): two
unsourced probe-firing cells (2.75 and 1.00, both actually 0.00); the truth-reading range quoted as
0.40–0.49 where the report's own table shows 0.338; a probe ratio printed as 1.02 where the shipped
value is 0.99, flipping the sign of the only sub-unity entry; chance-loss counts of 0–4 and 1–4
where the file says 0–3 and 1–5; edge-enrichment ranges wrong at both ends and in both windows; the
detectors' ROI floor stated as 4 where both run at their default of 3; and — the one that inverts a
reading — the ±1 second random-chance row **copied into the ±2 frame column**, inflating the strict
column's baseline two- to threefold and making a rigid-shift row look at chance when it sits above
it.

**Claims the evidence does not support.** The untrained arm was dismissed as "no working baseline",
quoting two of four models; untrained `line_length` scores 0.272 at the label-free threshold —
beating nine of the sixteen trained cells — and untrained `tube` at 0.507 beats **every** trained
truth-reading cell. The shared-offset control was presented as excluding a per-ROI leak; on the
stream the whole experiment ran on it never rises above chance for rigid shift *either*, 26–42 % of
its comparisons are ties, and it cannot detect the one leak the run found. And the comparison that
decides whether the learned family earns its place — against the existing hand-written CoactDetect
— was never made: `line` leads it by +0.063 at t(3) = 1.31, and the ablation by +0.005 at
t(3) = 0.34.

**Provenance that credited the wrong party.** The report said Elephant "generates every surrogate";
Elephant generates none of them in this run — every stage draws through a numpy reimplementation,
as the tool's own docstring says. And `locust` was cited as "a port of CICADA (Denis et al. 2020)",
which is wrong twice: Denis et al. 2020 is DeepCINAC, a different tool, and this repo had
**deliberately checked for and avoided that exact conflation on 2026-08-28**. The same bad citation
was sitting in `docs/GLOSSARY.md` and is fixed in the same change.

**Method the citations do not cover.** Whole-train shifting is ranked most robust at a dither of
**25 ms**, trial by trial. This run shifts a whole recording by **10–20 seconds** — three orders of
magnitude away, and the page's own measurement of slow-modulation removal is the explanation of why
that ranking does not transfer. Separately, the architecture's defining claim ("one ROI, one vote")
does not hold as stated: onsets are summed *before* the sigmoid, so the cap bounds the vote's
height and not its time integral, and the stage downstream reads the integral. A four-onset burst
delivers 1.7–2.7× the integrated vote of a single onset.

**Render defects.** Both figures failed their build gate. Figure 2 had been narrowed in the round-one
repair while its legend grew, which collided the arm labels into "supervisedintrained" and drove the
legend through panel B's axis label. Figure 1's panel letter was drawn underneath its own legend,
which also covered the largest data point in the panel. And `fuzz` — measured for every model, named
in the caption, and the thing the tool is named after — **was drawn nowhere**, because the constant
listing the plants was never read.

All of the above are fixed. The figures were rebuilt and re-read; the report was rewritten around
tables that, as role 1 established, reproduce cell-for-cell. **Every defect was in the hand-typed
prose around them.**

## What would validate this

The report now carries what it cannot settle, and three items are cheap enough to close:

- **The seed axis has not been run.** One training seed per fold decides nothing at four folds; three
  seeds would settle whether the second sensor's 0.058 is real.
- **No test covers the numpy rigid shift that produced every surrogate here.** The Elephant-backed
  version *is* tested and is not the path that ran.
- **The untrained-arm widths and coverage are in no shipped file.** They are read off a diagnostic
  that was not kept, so a reader cannot reproduce the one paragraph that disqualifies the baseline.

The deeper residual is that this run cannot distinguish "the objective is wrong" from "the contrast
contains little beyond co-activity". Resolving it needs an objective that pays for the *number* of
ROIs in a window rather than for any separation of real from shifted — which is the third decision
the report puts to Tony.

## Appendix — run header

- upstream:  syncytium2/murderboard @ 08f5ddb
- copy:      vendored @ 08f5ddb
- freshness: current
- artifact:  `docs/learned/tube_self_supervised/README.md` (63b0d08 -> rewritten this round)
- roles:     11 of 11 run (spawned by role name; role 2 reported a grant MISMATCH — see the ledger)
- reports:   `tube-self-supervised-2026-09-16-round2-roles/`
- rounds:    1 blind round after the round-one repair; **not yet clean**

Mode: retrospective

⚠ **Stopped at round 2 of 3, and the loop did not finish.** The blind round returned fifty-one
findings, the repair that followed was substantial — a near-total rewrite of the prose and a rebuild
of both figures — and **the repaired artifact has not been re-reviewed**. The process requires
iterating until a blind pass returns nothing new. This record is filed in the state the night ended
in, not in a clean one, and it is declared retrospective so that nothing downstream reads it as a
completed review.

⚠ **This record is filed after one blind round, not after a clean one.** The process requires
iterating until a blind pass returns no new findings. The second round returned fifty-one, the
repair was substantial, and the repaired artifact has **not** been re-reviewed. A third blind round
is owed before any number here is quoted outward.

## Appendix — role ledger

Round one is archived at `tube-self-supervised-2026-09-16-roles/`; the counts below are round two.

Each row opens with the role's own grant declaration, verbatim.

| # | role | findings |
|---|---|---|
| 1 | Prove It — GRANT 1 ok — Read, Grep, Glob, Bash | 22 findings + a 50-row claim ledger; every machine-generated table reproduces, every defect in the prose |
| 2 | DOI or Die — GRANT 2 MISMATCH — missing Grep, Glob; holds Read, Bash, WebSearch, WebFetch (no forbidden editing tools) | 14; the CICADA misattribution and the Elephant provenance claim |
| 3 | Cross-Examiner — GRANT 3 ok — Read, Grep, Glob | 30 across five groups; found the ±2-frame chance-row duplication |
| 4 | Reviewer 2 — GRANT 4 ok — Read, Grep, Glob, Bash | 20, 6 blocking; found the untrained arm working and the pooled-trace conflation |
| 5 | Kill Your Darlings — GRANT 5 ok — Read, Grep, Glob | 66; also reported that the prose tool is **not vendored here** and its grant excludes Bash, so the tool half of the role could not be run |
| 6 | RTFM — GRANT 6 ok — Read, Grep, Glob, Bash, WebSearch, WebFetch | 30; measured that the vote cap does not bind, and the 25 ms/10 s regime gap |
| 7 | Reinventing the Wheel — GRANT 7 ok — Read, Grep, Glob, Bash | 14; the aggregate-leak bank is built at initialisation, not fitted, values |
| 8 | You Lost Me — GRANT 8 ok — Read, Grep, Glob | 25; the forest-plot false friend and the undefined two sensors |
| 9 | Show, Don't Tell — GRANT 9 ok — Read, Grep, Glob, Bash | 13; figure share measured at 11.5 % of rendered canvas |
| 10 | Ship It — GRANT 10 ok — Read, Grep, Glob, Bash | 19; both figures failed, `fuzz` drawn nowhere, this record's own link dead |
| 11 | Start With the Problem — GRANT 11 ok — Read, Grep, Glob | 15; the verdict was scattered across six screens with no result on the first |

**Grant note.** Every role was spawned by its compiled agent name. Role 2 nonetheless declared
`MISMATCH`, reporting that it reached the pattern work through Bash rather than Grep and Glob — so
no check was skipped, but the header does not claim the clean "named agents" mode on its behalf.

## Appendix — residual ⚠ carried, not fixed

- A third blind round is owed on the rewritten artifact.
- `murderboard_prose.sh` is not vendored into this repo, and the process file grants role 5 no Bash,
  so that role's mechanical half cannot run here as written. Worth an upstream note.
- The aggregate-leak classifier's filter bank is built from `tube`'s **initial** parameters, not
  fitted ones; the fitted widen is ±2 frames against the bank's ±1, and two of its eight scales lie
  outside the model's own clamp. The Stage 1 gate that licensed the whole run rests on it.
- `oracle_threshold` re-derives `pick_threshold` without its edge-of-grid guard, which is what a
  threshold pinned to the grid floor looks like — the untrained arm's coverage is the symptom.
- The probe measures on a **flat** Poisson background, the one the generator spec deliberately does
  not use.
- Figure 3 was not built. Role 9 showed that `tools/make_real_detection_figure.py` already draws
  detections in lanes above a real raster, and that the report's most consequential negative — calls
  landing where no ROI has an onset — is carried by prose where a picture exists. The saved events
  would feed it directly.
- `docs/goals/unsupervised-learning.md` still does not mention the controls, the aggregate-channel
  test, this training run, or `line`.
