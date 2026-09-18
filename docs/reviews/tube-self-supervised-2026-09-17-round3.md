# Murderboard run, round 3: the rigid-shift report

## What was at stake

`docs/learned/tube_self_supervised/README.md` is the only document carrying the label-free detector
thread's last three days to a reader, and it ends on four decisions for Tony. Its second blind
round (2026-09-16) returned fifty-one findings, including two inverted decision lines. The
residuals that round left were fixed, every stage was rerun on 2026-09-16 and 2026-09-17, and the
page was rewritten from one computed `summary.json`. This third round reviewed that rewrite blind:
eleven roles, given the page and its sources and nothing from rounds 1 or 2.

**The numbers held.** Three roles recomputed them independently from the raw stage outputs (Prove
It, Cross-Examiner, and parts of RTFM and Reinventing the Wheel), and the only numerical
mismatch on the page is one boundary (a coverage of 0.928 written as "0.93 or more").

**The controls did not.** Reviewer 2 built a probe that has no events at all, only a slow rate
modulation shared across ROIs, and ran it through the exact paired checks of Figure 3, panel C:

| paired check (probe: shared 40 s rate modulation, no events; score = top 1 % of a 10 s population count) | share of crops where "real" scores higher |
|---|---|
| real vs rigid shift | 1.000 |
| real vs a fifth of onsets removed (the "positive control") | 1.000 |
| real vs shared offset, same crop | 0.494 |
| real vs shared offset, independent crop | 0.512 |
| unplanted twin vs its rigid shift | 0.512 |

Every check "passes" for a scorer that has learned no coordination. So the checks cannot tell a
model that learned coordinated events from one that learned slow shared modulation, which is the
question the page hands to Tony. Two further control findings sit beside it: the unplanted-twin
control is a stationary process with independent ROIs, which rigid shift leaves invariant, so it
cannot fail for any leak; and per-onset dither, the positive control in Figure 1, tests a failure
rigid shift cannot produce, because rigid shift preserves every same-ROI interval exactly. (The
probe is Reviewer 2's; the main thread has not rerun it. Its logic is checkable from
`tools/tube_self_supervised.py`'s `paired_checks`.)

## What would validate the page, and what was decided

This is round 3 of a process capped at three blind rounds, with blocking findings still arriving
(round 2: two inverted decision lines; round 3: one blocking control finding plus nineteen other
high-severity findings, most of them fixable text). The process says a run that is not converging
goes to the human. **Tony was asked on 2026-09-17 and chose to add controls that can fail, rerun,
restructure the page, and run a fourth blind round past the cap.**

The controls that answer the blocking finding, each with the failure it can register:

- **Rigid shift at a small displacement (about 1.6 s) beside 10–20 s**, in the paired checks and
  the aggregate test. Slow shared modulation survives a 1.6 s shift; sub-second alignment does not.
  A model that learned modulation reads chance against the small shift; one that learned
  coordination does not.
- **A shared-modulation twin with no events**, and a **per-ROI-modulated twin**, replacing the
  stationary twin. The first must separate from its rigid shift for any modulation learner; the
  second must read chance.
- **The probe itself, as a test**: a no-event modulation scorer and a sub-second coincidence scorer
  run through the paired checks, so the checks are shown to separate the two.
- **A zero-parameter count baseline** under the same label-free rule, so "training buys something"
  is measured against a detector that fires, not only against untrained networks.
- **A positive control that keeps intervals and moves window counts** (per-ROI circular shift) in
  the per-ROI test, and the caption corrected: the classifier cannot see alignment finer than its
  60 s window, and does see co-modulation at that scale.

How it generalises: a null check on a surrogate contrast is only as strong as the alternative it
was built to reject. Every control in this run was built to reject a per-ROI leak, and the
plausible alternative was a population-level one. The pipeline page
(`docs/pipelines/learned-model-evaluation.md`, stage 3) should require naming the alternative a
control rejects, and constructing its opposite.

## Round-by-round convergence

| round | date | findings | blocking or high | stopping state |
|---|---|---|---|---|
| 1 | 2026-09-15/16 | 11 | not recorded by severity | repaired |
| 2 (blind) | 2026-09-16 | 51 | 2 inverted decision lines among them | repaired; residuals left for this round |
| 3 (blind) | 2026-09-17 | about 200 rows across eleven reports, many duplicates | 1 blocking (controls), about 20 high | **round cap reached, not converged; escalated; Tony chose rework and a fourth round** |

This review found and will fix a large number of defects. **It is not a correctness proof**: the
convergence table measures how quickly reviewers stopped finding things, not whether anything
remains.

## Adjudication of the other clusters

Every cluster below is accepted and will be applied with the rework unless marked otherwise. The
role reports carry each finding's location and wording.

- **Citations** (DOI or Die, Prove It, RTFM): the SPIKE-synch detection layer is Cecchini et al.
  2021, not Kreuz et al. 2022; Louis, Borgelt & Grün 2010 is quoted backwards (their start-and-end-rate
  condition licenses *rolling*); the origin trace omits Pipa, Riehle & Grün 2007, which the glossary
  already cites; whole-train shifting as published is per trial, and this run uses one trial per
  recording; CFAR predates Finn & Johnson 1968 (Finn 1967); "differentiable Neyman–Pearson layers"
  is uncited and misnamed; noise-contrastive estimation and classifier two-sample tests are missing
  from the lineage; CICADA's framework paper is from Dard's group at EPFL; Dard 2022's construction
  descends from Cossart, Aronov & Yuste 2003. **The same Kreuz 2022 miscitation sits in
  `docs/detector_history.md`**, which is fixed in the same change.
- **One tool defect**: `tools/tube_ssl_real_compare.py` computes the reference-to-model agreement
  against seed 0 only, while the page says every row pools its seeds. Fixed in the tool and rerun.
- **Statistics** (Reviewer 2, RTFM): paired *t* over folds with overlapping training sets needs the
  Nadeau–Bengio correction and an interval; eight comparisons need a multiplicity note; "changes
  nothing measurable" becomes an interval; per-fit positive-control failures are reported; the
  final-step loss is replaced by a mean over the last logged steps.
- **Rendering** (Ship It, Show Don't Tell, You Lost Me): Figure 3 names the wrong figure for its F1
  scale; its shading marks the wrong columns; Figure 1 panel C's fold bars are hidden and its glyphs
  mean different things than in Figures 2 and 3; figures are unreadable at page width; the page's
  main claims (the rate-dependent trained-versus-untrained result, the one-fold bake-off margins,
  the coverage caveat, the real-recording findings) are tables or prose and will be drawn.
- **Order and terms** (Start With the Problem, You Lost Me, Kill Your Darlings, Cross-Examiner): the
  page opens on results before the problem; the changelog sits between the questions and their
  answers; "cell" carries three meanings; "corpus" is retired; "truth-reading threshold" and
  "concentration channels" differ from the glossary; several terms are undefined.
- **Companion documents** (Cross-Examiner): `docs/MILESTONES.md` section C, the goal page, the
  pipeline page, the glossary's `line` entry and three tool docstrings still carry the superseded
  run. Updated in the same change.
- **Not accepted as written**: Kill Your Darlings asks for American spelling throughout. The page
  is edited toward it where touched, but this round does not respell the tree.
- **Out of scope, recorded**: Reinventing the Wheel's findings that four tools copy the bake-off's
  fit loop and that the new figure tools do not default to the darkroom are real and filed, not
  fixed here.

## Residual ⚠ for Tony

- The blocking control finding is open until the rework's controls have run.
- `line_bound` differs from `line` twice (the time bound and the vote-floor subtraction), so the
  ablation is confounded; the page will name both changes, and no floor-only variant is being
  added without a ruling.
- Unsearched literatures remain: Neyman–Pearson classification beyond one hit, contrastive learning
  beyond the shelf's own README, time-shift surrogates in nonlinear time-series analysis, and the
  fields the page already lists.
- Nobody has asked Pipa or Grün where whole-train shifting begins, or the CICADA authors about the
  `locust` port.

## Appendix: the run

Mode: standard
- upstream:  syncytium2/murderboard @ 08f5ddb
- copy:      vendored @ 08f5ddb
- freshness: current
- artifact:  docs/learned/tube_self_supervised/README.md (8317932de780f180ae27ccf394ad945e4891659c -> not yet repaired)
- roles:     11 of 11 run (inline fallback: spawned through the compiled agent files by agent type, but 7 of 11 declared GRANT MISMATCH because Grep and Glob were not delivered)
- reports:   tube-self-supervised-2026-09-17-round3-roles/
- rounds:    3 blind rounds; cap reached, not converged; a fourth authorised by Tony on 2026-09-17

The role reports were written as each arrived. Personal absolute paths in them were replaced with
`<worktree>`, `<scratchpad>`, `<darkroom>` and `<primary checkout>` before committing (sapper
SAP004); nothing else was changed.

### Role ledger

| # | role | grant declared | findings | most severe |
|---|---|---|---|---|
| 1 | Prove It | GRANT 1 MISMATCH — missing Grep, Glob; holds Read, Bash (no forbidden editing tools) | 14, plus a full claim ledger (one numerical mismatch) | medium: agreement column is seed 0 only; mixed quantities; Louis inverted; "every number is in summary.json" too broad |
| 2 | DOI or Die | GRANT 2 MISMATCH — missing Grep, Glob; holds no forbidden tools (held: Read, Bash, WebSearch, WebFetch) | 13 | high: Kreuz 2022 miscited (Cecchini 2021); origin trace omits Pipa, Riehle & Grün 2007 |
| 3 | Cross-Examiner | GRANT 3 ok — Read, Grep, Glob | 32; every number traced and consistent | high: MILESTONES section C rows superseded (two) |
| 4 | Reviewer 2 | GRANT 4 MISMATCH — missing Grep, Glob; holds no forbidden tools (Read, Bash only) | 15 | **blocking**: paired checks pass for a no-event shared-modulation scorer |
| 5 | Kill Your Darlings | GRANT 5 ok — Read, Grep, Glob | 46, by hand (`murderboard_prose.sh` is not vendored; no Bash) | high: the Figure 1 and paired-check scores are never named; "two more names" followed by three; mixed quantities |
| 6 | RTFM | GRANT 6 MISMATCH — missing Grep, Glob; holds no forbidden tools (Read, Bash, WebSearch, WebFetch; I searched files with `grep` through Bash instead) | 14 | medium: whole-train shifting is per trial; Louis inverted; features see window-scale co-modulation; edge enrichment appears on surrogates too (measured) |
| 7 | Reinventing the Wheel | GRANT 7 MISMATCH — missing Grep, Glob; holds none of the forbidden editing tools (I hold Read and Bash only) | 9 (one a confirmed match) | medium: Figure 3 recomputes coverage differently from summary.json; the initial bank re-derives tube's kernels |
| 8 | You Lost Me | GRANT 8 ok — Read, Grep, Glob | 22, plus a per-decision table | blocking (for a cold reader): terms undefined before use; "cell" has three meanings; Figure 3's shading contradicts the text |
| 9 | Show, Don't Tell | GRANT 9 MISMATCH — missing Grep, Glob; holds none of the forbidden editing tools (my tools are Read and Bash only) | 12 | high: the page's main claims are drawn nowhere; figures are unreadable at page width; the real-recordings section has no figure |
| 10 | Ship It | GRANT 10 MISMATCH — missing Grep, Glob; holds no forbidden tools (holds Read, Bash) | 14 checks; all four PNGs rebuild pixel-identical | high: Figure 3 names the wrong figure for its F1 scale |
| 11 | Start With the Problem | GRANT 11 ok — Read, Grep, Glob | 12 | high: the page opens on results before the problem; the changelog splits the questions from their answers |
