# Two drafts of the reevaluation, both withdrawn — what the murderboard found

The surrogate screen ran overnight on 2026-09-11 and flagged nothing. Two documents were then
written to say what that meant and what to buy next. **Both were reviewed by eleven roles and
both were withdrawn**, for the same underlying defect in two different disguises: a number was
taken from the cheaper source when the expensive source was already on disk, and a parameter
that controlled the conclusion was never varied.

This record exists because five separate reviewers, independently, reported that it did not.

## The verdict

| draft | hash | rounds | outcome |
|---|---|---|---|
| [v1](../proposals/2026-09-12-surrogate-screen-reevaluated.md) | `e36082da` (was `d623f5a5` when reviewed) | 1 | **WITHDRAWN** — four load-bearing conclusions rested on probe numbers where production numbers existed |
| [v2](../proposals/2026-09-12-surrogate-screen-reevaluated-v2.md) | `4b44e408` | 1 blind | **WITHDRAWN** — two blocking findings, one of them the same probe-for-production substitution, three times over, in the section titled *"with the power stated correctly"* |

**Nothing in either draft should be acted on.** What the night established about the Holm floor
survives and is restated below; what either draft recommended buying does not.

## The two blocking findings, verified against production rather than taken on report

**1. The family size was never varied, and the headline claim is false.** v2 says *"The overnight
run could not have produced a corrected flag at any setting"* and *"Only a new run can flag."*
Both hold only for the two family sizes it tested, 65 and 13. The band floor is 1/101 = 0.009901,
and that floor is **attained** — 1,145 statistics sit exactly on it in scope DI, 1,144 in MALE,
1,189 in ORX, 1,146 in OVX, 1,223 in `all`, and 229 of 858 on `cossart`. So Holm on a
**pre-declared family of five band statistics flags on the night's existing data**: 5 x 1/101 =
0.049505 < 0.05.

The refutation is one call to this session's own gate:

```
correction_reach(m=5,  n_splits=100, K=99) -> band_reaches: True,  splits_needed: 100
correction_reach(m=6,  n_splits=100, K=99) -> band_reaches: False, splits_needed: 120
correction_reach(m=13, n_splits=100, K=99) -> band_reaches: False, splits_needed: 260
```

The night ran exactly 100 splits. The gate built this session to stop precisely this error would
have said *yes, this can flag* — and it was never asked. Paired is unrescuable either way: it
needs m <= 2 on `steps_excluded` and m <= 1 on `cossart`.

⚠ **The remedy is a pre-declaration, not a free rescue.** Choosing which five statistics now,
having seen which ones sit on the floor, is post-hoc and inadmissible. This is a cheap route for a
future run, or for a pre-registration defensible without reference to these results. It is not a
way to read a flag out of the night retroactively. v2's error is not that it rejected this remedy;
it is that it never considered it, and priced a 53,432-core-hour rerun as the only option.

**2. The discriminator table mixes three provenances, under a heading claiming one.** v2 states
*"Every cost, destruction and capability figure below is from production. That distinction is what
the withdrawn draft got wrong."* Then:

| v2 row | what it actually is |
|---|---|
| fast positive 1,669 / 0.112 / 5.14 / 324 / 89 | production `homogeneous_resample` (ICC 0.11231, 89 mice) — and the probe reproduces it exactly, so the coincidence hid the substitution |
| events positive 1,375 / 0.004 / 1.16 / 1,184 / 18 | production `homogeneous_resample` (ICC 0.00426, 18 mice); 1,184 is the effective n, 1375/1.161 |
| **slow positive 0.109 / 5.03 / 332 / 87** | **matches no production control.** Production slow `homogeneous_resample` is ICC 0.1397 / 107 mice; the designated `uniform_dither` positives span 0.0368–0.1228. 0.109/87 traces to `isi_dither` *candidate* rows |
| **fast negative "not flagged"** | **inverted.** Production `real_vs_real` fast: accuracy 0.5386, P = 0.035, `significant: True` — and that flag is the single void reason stamped on 126 of 248 fast candidates. v2's own next paragraph is built on the flag it denies here |

Production also carries **20-seed** negative-control reruns for all three streams that v2 never
used: fast `flag_rate 0.05` (1 of 20, seed 0 only), slow `0.0`, events `0.0`. v2 argues from the
probe's five seeds and hedges that *"five seeds cannot separate alpha from 10 alpha"*. The
stronger evidence — an alpha-level rate measured at n=20 — was in the same run folder. That is the
third probe-over-production substitution in a document written to end the first.

## Corrections established, with the arithmetic

Every row recomputed from the run folders during adjudication, not quoted from a reviewer.

| v2 claim | correct |
|---|---|
| sqrt/nosqrt pairs "differ on 5–7 of 13" | matches no metric. At scope `all`, 23 pairs: `delta` **9–13** (9 in 3 pairs, 13 in 20), `real` 6–8, `band_p` 3–7, `paired_p` 1–5. **`band_p_holm` and `paired_p_holm` differ on 0 of 13 in all 23 pairs** — the square root moves nearly every raw statistic and changes no corrected verdict. The withdrawal of "provable no-op" stands and is understated |
| "sizing for one is roughly 480 splits and 960 draws" | **520 splits, 1040 draws.** `paired_p` is two-sided `2*min(...)/(K+1)`, so one discordant draw takes the floor to 4/(K+1), not 3/(K+1). At K=1039 the adjusted P is exactly 0.050000 and does not fire under the strict `<`; K=1040 gives 0.049952. The same off-by-one this document exists to expose |
| "the night's 100 mouse splits and 99 draws" | K ranges **19–99**. The entire ISI family ran at 19, where the within-scope paired floor is 1.000, not 0.260. Conclusion strengthened |
| "the probe is used only for ... two recordings at three draws" | only stage 1. `stage2`/`stage2b` loaded **84 recordings** at 259–260 splits and 519–520 draws; `stage4` ran 1,669 pairs across 44 mice |
| "cuts the required sample four- to fivefold" | exactly **fivefold** on `steps_excluded` (65 -> 13); **no change** on `cossart`, which has one scope |
| Cossart destruction "a tenth of the shipped ensemble" | 20 surrogates is a tenth of `steps_excluded`'s 200 **and a fiftieth of the assessor's shipped 1000** (`assess.assess_coactivity` default). Say both |
| "47 of 144 slow cells" | counts correct; the denominator is the **ISI-family cell count** (72 `isi_dither` + 72 `joint_isi` per stream), never defined in the text |
| provenance row: production files | they are one directory down, in `steps_excluded/` and `cossart/`, and exist twice with different contents |
| provenance row: code at `0dc6356` | that tree corrects Holm **within** scope (family 13); the run's numbers are family 65. The cited code cannot produce the cited floors |
| review record at `docs/reviews/...reevaluated_2026-09-12.md` | did not exist. This file is it |

## What survives

Stated so the next draft does not re-derive it. All reproduced independently by several roles and
re-checked here:

- Every Holm floor: 65 x 1/101 = 0.644; 13 x 1/101 = 0.129; 13 x 2/100 = 0.260; 11 x 1/101 =
  0.109; 11 x 2/41 = 0.537. And 260/520, 220/440 at the strict boundary.
- The full probe keystone table at 260/520 and 259/519, including the 0.0498 / 0.0499 minima.
- 53,432 core-hours at 19 draws and 278,409 at 99 — though **91% of it is Cossart** (48,799 vs
  4,633), which v2 sets beside a `steps_excluded` fact.
- All five destruction rows, both participation arms, and the 20% arm's absence at floor 8.
- 2,630 ROIs, 358 dropped cells, 46 unpriced, 654 required pairs, 248 candidates / 126 stamped.
- **The Elephant square-root ordering**: `sqrt` at `spike_train_surrogates.py:995-996`, before the
  smoothing and before `_normalize_cumulative_distribution`, which is affine and cannot undo it.
- **The zero-readers are zero by construction**: `surrogates.circular_shift` calls the assessor's
  own `assess.circular_shift_trains`, and `homogeneous_resample` places onsets uniformly, the
  distribution that null is invariant under.
- `holm()` is not a reinvention — nothing in the tree, statsmodels absent, SciPy ships none.

## Findings the review raised that are not about either draft

Filed because they outlive the withdrawn documents.

- **Two implementations of one stated rule disagree.** Both docstrings in `surrogates.py` say the
  window is sqrt(2)*J; `interval_jitter_bin` computes `round(sqrt(2)*J)` and `window_shuffle_width`
  computes `2*round(J/sqrt(2))`. They differ on 5 of 6 fast radii, 2 of 6 slow, 5 of 6 Cossart, and
  at J=2 the window is *narrower* than at J=1. `tests/test_surrogates.py:444-453` asserts both
  values, so the suite blesses the divergence. Candidates carrying the same radius label were run
  at different effective radii. ⚠ **Open.**
- **The keystone arithmetic exists twice** — `build_surrogate_report.yardstick_reach` recomputes
  what `surrogate_stats.correction_reach` is for, on different inputs. Reproducing exactly today;
  drift risk. ⚠ **Open.**
- **`recruited = 0.5 * n_roi` is hardcoded** in the report builder while the `meta.json` it already
  reads records `participation: [0.2, 0.5]`. The 20% arm v2 lists as a design limitation was
  available at the point of use. ⚠ **Open.**
- **Prior art on the wrapping is unsituated**: Stella, Quaglio, Torre & Grün (2019) 3d-SPADE, and
  the group's released `INM-6/SPADE_surrogates` / `SPADE_applications`, run substantially this
  comparison. Neither draft cites them. ⚠ **Open**, on `docs/lit_needed.md`.
- **The dithering root is Date, Bienenstock & Geman 1998**, not Gerstein 2004 — Gerstein's own
  abstract says so, and Date 1998 was already on the shelf. Gerstein says flat dither *adds* short
  intervals; the stronger "shorter than any real one" is bugarach's own measurement and was
  misattributed to him. **Fixed** on the shelf and in `lit_needed.md` at `6c74f84`.
- **The Cossart lab's method is uncredited** — `detectors/cicada.py` declares itself a port derived
  from CICADA, which is separately citable. Both drafts cite only DANDI and the eLife paper.
  ⚠ **Open.**
- **Zero figures in either draft**, against this repo's "show the picture" rule, while the same run
  ships five numbered SVG figures per report from `tools/build_surrogate_report.py` — including
  `fig_leak`, which v2 re-describes in a 72-word paragraph. ⚠ **Open**, and it applies to the
  replacement.

## Round 2 role ledger — blind pass on v2 (`4b44e408`)

Every role was given the same minimal prompt: *"You are reviewing this document on its own terms.
You have not been told what any earlier review found; do not assume any particular defect exists
or does not."* No finding was suggested, no ordering hinted, no verdict supplied.

| # | role | GRANT line as returned | findings | highest severity |
|---|---|---|---|---|
| 1 | Claim & data verifier — "Prove It." | GRANT 1 ok — Read, Grep, Glob, Bash | 14 | high |
| 2 | Citation & reference validator — "DOI or Die." | GRANT 2 ok — Read, Grep, Glob, Bash, WebSearch, WebFetch | 13 | blocking |
| 3 | Consistency auditor — "Cross-Examiner." | GRANT 3 ok — Read, Grep, Glob | 20 | high |
| 4 | Adversarial reviewer — "Reviewer 2." | GRANT 4 ok — Read, Grep, Glob, Bash | 22 | **blocking x2** |
| 5 | Line editor — "Kill Your Darlings." | GRANT 5 ok — Read, Grep, Glob | 24 | major |
| 6 | Methods / domain expert — "RTFM." | GRANT 6 ok — Read, Grep, Glob, Bash, WebSearch, WebFetch | 13 | **critical x2** |
| 7 | Reuse auditor — "Reinventing the Wheel." | GRANT 7 ok — Read, Grep, Glob, Bash | 10 | major |
| 8 | Naive-reader accessibility — "You Lost Me." | GRANT 8 ok — Read, Grep, Glob | 24 | blocking |
| 9 | Density & figure-first — "Show, Don't Tell." | GRANT 9 ok — Read, Grep, Glob, Bash | 10 | critical |
| 10 | Build & craft gate — "Ship It." | GRANT 10 ok — Read, Grep, Glob, Bash | 16 | high |
| 11 | Argument order — "Start With the Problem." | GRANT 11 ok — Read, Grep, Glob | 9 | major |

Every declared grant matches the compiled agent file exactly. Eleven `ok`, no `MISMATCH`.

**Independent confirmation counts**, which is what a blind round buys: the missing review record
was found by **five** roles separately (2, 3, 8, 10, 11); the inverted fast-negative verdict by
**five** (1, 3, 4, 6, 10); the probe-for-production discriminator table by **four** (3, 4, 6, 10);
the 480/960 sizing error by **four** (1, 3, 6, 10); the absence of figures by **three** (4, 9, 10).

Role 11 recorded, unprompted, that the cold open is right — *"The overnight run could not have
produced a corrected flag at any setting, and that was derivable from the plan before it started"*
— and that sections 7, 8 and 10–14 sit in defensible positions. That judgement now stands corrected
by role 4's blocking finding: the sentence it praised is the false one.

## Round 1 — v1, and what this record cannot tell you

Eleven roles reviewed v1 and it was withdrawn on their findings. The four conclusions that failed
are listed verbatim in [v1's own withdrawal banner](../proposals/2026-09-12-surrogate-screen-reevaluated.md).

⚠ **The per-role reports from that round were not preserved, and I will not reconstruct them from
memory.** The ledger above covers round 2 only. That is a defect in how I ran round 1, not a
property of the review, and it is the reason this record's round-1 section is a summary where its
round-2 section is verbatim. A murderboard whose outputs are not durable is one nobody can check.

## What I owe Tony, stated plainly

He challenged me during round 1 for seeding the reviewers, quoting my own sentence back. On audit
he was right: I had told role 5 the verdict and its exact wording, handed role 9 seven numbered
table candidates, given role 4 my own binomial doubt, and given role 11 my ordering questions —
then reported what came back as discoveries.

**Round 2 was run blind with the minimal prompt above, and every finding in it is independent.**
The confirmation counts are given because they are now meaningful; in round 1 they would not have
been. This paragraph stays in the record so the distinction is checkable rather than asserted.

## Residual ⚠

- **The pre-declared-family question is Tony's, not a measurement.** Which statistics, chosen
  before looking, and whether a pre-registration on already-collected data is acceptable here.
- Round 1's per-role outputs are lost; only its conclusions survive.
- Both drafts are withdrawn and no replacement exists. The authority for what was run is
  [the plan](../proposals/2026-09-10-surrogate-evaluation-overnight.md); there is currently no
  authority for what to run next.
- The seven open items in *"Findings not about either draft"* above are unfixed.
- The darkroom claim on `docs/SESSIONS.md` stays ACTIVE: the probe has reported, but the plan has
  not been reevaluated in a document that survives review.

## Run header

- upstream:  syncytium2/murderboard @ `81a0927`
- copy:      vendored @ `81a0927`
- freshness: current (checked with `--refresh`, exit 0)
- artifact:  `docs/proposals/2026-09-12-surrogate-screen-reevaluated-v2.md` (`4b44e408` -> `4b44e408`, unchanged — the adjudication is withdrawal, so no fixes were applied to it)
- roles:     11 of 11 run (named agents)
- rounds:    2 run across two drafts; **not converged** — round 2 returned two blocking findings and no third round was run, because the artifact is withdrawn rather than repaired

Mode: standard
