# Murderboard run, round 4: the rigid-shift report

## What was at stake

`docs/learned/tube_self_supervised/README.md` reports whether a coordinated-event detector can be
trained against rigid shift with no labels, and ends on four decisions for Tony. Its third blind
round found that the trained models' checks could not fail against slow shared modulation. Tony
chose to add controls that can fail, rerun, restructure the page, and review it a fourth time past
the three-round cap. This is that fourth round: eleven roles, blind, given the rewritten page at
`f2278da` and its sources and nothing from rounds 1–3.

## What was found

**The rerun's central numbers held.** Three roles recomputed them independently (Prove It from the raw
stage outputs, Cross-Examiner against `summary.json`, RTFM and Reinventing the Wheel by re-running
code). All five figures rebuild byte-identical, and `summary.json` reproduces on every key except its
provenance. Every reference exists and its metadata check out.

**Two measurements are wrong, and one of them was a headline.**

- **Events called on a rigid shift were scored against the unshifted recording** (Reviewer 2, blocking).
  `tools/tube_ssl_real_compare.py` `measure` reads the real trains for every detector, including the
  "on its rigid shift" rows, so their share of events with onsets in at least three ROIs
  (0.046–0.070 supervised, 0.073 `count_excess`) says only that shift events fall at random times in
  the real recording. Rebuilt and scored against the shifted trains, supervised models' shift events
  hold three or more ROIs in 0.43–0.54 of cases and `count_excess` in 0.67. The page's claim that these
  detectors "lose" their co-activity on a rigid shift is not what the data show. That shift is also one
  of the three the threshold was set on, so its low event rate is guaranteed.
- **The supervised fits for the third and fourth held-out folds are the same model** (Prove It,
  confirmed in the main thread). `bugarach.learn.train.fold_maker` fits on the first two of the three
  training folds and validates on the last, so held-out folds 2 and 3 both fit on recordings 1000–1003
  with the same seed: 9 distinct bake-off fits per model, not 12, and 3 distinct fitted models in the
  aggregate test, not 4. The "third fold carries every margin" finding is that shared model scored on
  different held-out recordings, and the Nadeau–Bengio correction assumes distinct training sets.
  **This is a property of the project's bake-off harness, not only of this report.**

**Three claims are wrong as written.**

- The supervised and count-baseline label-free thresholds on real recordings used rigid shifts at
  **J = 10 s**, not 20 s (four roles). The caveat about bench and real operating points built on 20 s
  is false.
- "No more co-activity than chance" for the models trained against rigid shift compares a range with a
  range. Each condition against its own activity-weighted chance: 6–7 of 10 sit above it, by up to
  0.09 (four roles). Reviewer 2 measured further: 46–61 % of their events cover a span with no onset
  in any ROI while the surrounding 10 s runs at 1.4–1.5× mean activity, and 0.67–0.81 lie within 3 s of
  a frame with three or more ROIs lit, against 0.44–0.50 by chance. **They fire in gaps beside
  co-activity: imprecise localization, not chance.**
- "Supervised models, never shown modulation": the simulator's five-minute dense stretch is shared
  modulation (Reviewer 2).

**The twin check is weaker than the page says** (Reviewer 2, RTFM). The 1.6 s shared-modulation cell
cannot detect modulation (`slow_modulation` reads 0.550 there against its own null of 0.546); the
events twin carries 0.1 s of jitter and sits at the 1.000 ceiling for most scorers; each scorer gets
about 120 correlated crop pairs with no interval, and a null reads as low as 0.383; one supervised fit
per architecture; and `count_excess`, which cannot follow a 40 s cycle, still responds to the
shared-modulation twin through coincidences that rise with rate. "The trained models respond to planted
events as strongly as supervised ones and to shared modulation less" is described, not tested.

**Attribution** (DOI or Die, RTFM): the Kreuz group's thresholding of the SPIKE-synchronization profile
to isolate events originates in Kreuz, Satuvuori, Pofahl & Mulansky 2017 (*New J Phys* 19:043028),
on hippocampal-slice calcium imaging, not Cecchini et al. 2021; `SPIKE-synch` is ported from cSPIKE,
not PySpike; the objective is a contrastive ranking loss with one negative (van den Oord et al. 2018),
related to but not noise-contrastive estimation; the nearest self-supervised precedents, Hyvärinen &
Morioka 2017 and Chau et al. 2025, are on the project's own shelf and uncited; roots are missing for
the classifier two-sample test (Friedman 2003), NCE (Gutmann & Hyvärinen 2010) and Neyman–Pearson
learning (Cannon et al. 2002).

**Data and policy** (Prove It, Reviewer 2): the export folder flags ROIs stuck at the frame floor in
four of the 84 recordings and removed events around field steps in three, and the page mentions
neither; results pool four groups the export folder labels. **FOUNDATIONS §5 keeps anything derived
from real data machine-local with no slice ids, and `real_compare/events.json` (per-recording event
times keyed by recording id) and checkpoints trained on real recordings are committed, and the events
file has been on `main` since the earlier PR.** That is Tony's to rule on.

**Presentation** (You Lost Me, Show Don't Tell, Kill Your Darlings, Start With the Problem, Ship It):
terms used before definition in the summary and the problem section (twin, crop, head, fold,
`count_share` never defined); Figure 3 panel B reads as a forest plot whose filled diamond is the one
outlier fold; the twin check, which the page calls decisive, has no figure; tables repeat panels, so
each figure gets a third of its section; one paragraph appears twice; glyph and colour reuse across
figures; the answer to the title question is fourth of seven bullets.

## Convergence, and what would validate the page

| round | date | finding rows | blocking | stopping state |
|---|---|---|---|---|
| 1 | 2026-09-15/16 | 11 | not recorded | repaired |
| 2 (blind) | 2026-09-16 | 51 | 2 (inverted decision lines) | repaired |
| 3 (blind) | 2026-09-17 | about 200 | 1 (controls cannot fail) | cap reached; escalated; Tony chose rework and a fourth round |
| 4 (blind) | 2026-09-17 | about 190 | 2 from Reviewer 2 (a scoring bug; the chance claim), 4 section-level blocks from You Lost Me, and a harness defect (shared bake-off fits) | **not converged; past the cap; escalated to Tony** |

Severity is not falling: each round has found a measurement defect the previous one could not see,
because each rework adds measurements. The page cannot be validated by another review of its prose; it
needs the two measurement defects fixed and rerun, and the twin check either hardened (harder twins,
intervals over twins, several supervised seeds, and a direct localization test on twins with known
event times) or reported as described rather than tested.

How it generalises: a check added in answer to a review is new code, and it gets the least scrutiny of
anything in the run. Here the fix for round 3 (score detectors on their own rigid shift) carried the
bug round 4 found, and the harness defect was older than every round and invisible to all of them until
a role counted distinct fits instead of rows.

This review found a large number of defects. **It is not a correctness proof**: the convergence table
measures how quickly reviewers stopped finding things, not whether anything remains.

## Adjudication

Pending Tony's ruling on scope (below). Proposed, per cluster:

- **Fix and rerun** (tool defects): score shift events against the shifted trains, on a fresh shift the
  threshold never saw; add the localization measures Reviewer 2 used; correct `J`, the chance
  comparison, parameter counts, slow-stream displacements, twin counts, the `slow_modulation` zero, the
  per-ROI test's exposure to the ends, and every other number the roles flagged.
- **Soften or harden** the twin check, per Tony.
- **File, not fix here**: the bake-off harness's shared folds (`fold_maker`) and the encoder's
  truncating frame mapping (`bugarach.learn.encode`, Reinventing the Wheel) are project-wide and change
  every learned number on `main`; each needs its own todo and review.
- **Tony**: the FOUNDATIONS §5 question about committed real-derived event times and checkpoints.
- **Apply** all attribution and presentation findings.
- **Not accepted as written**: none so far.

## Residual ⚠ for Tony

- Whether to fix, rerun and deliver unconverged, run a fifth round, or park the report.
- FOUNDATIONS §5 and `real_compare/events.json` and the checkpoints, including what is already on `main`.
- The bake-off harness's shared folds, which touch every published bake-off number.
- Human-only questions from DOI or Die: the exact date of Kreuz's reply and which paper he pointed to;
  whether anyone has asked Pipa or Grün where whole-train shifting began; whether Dard or the Cossart
  lab have trained detectors against circular-shift surrogates.
- Papers not reached: Pipa, Riehle & Grün 2007; Pipa & Grün 2003; Mao et al. 2001; Finn 1966; Friedman
  2003; Gutmann & Hyvärinen 2010; Cannon et al. 2002.

## Appendix: the run

Mode: standard
- upstream:  syncytium2/murderboard @ 08f5ddb
- copy:      vendored @ 08f5ddb
- freshness: current
- artifact:  docs/learned/tube_self_supervised/README.md (d39dd8bc6b2dd3d934682874821f90b45e511525 -> not yet repaired)
- roles:     11 of 11 run (inline fallback: spawned through the compiled agent files by agent type, but 7 of 11 declared GRANT MISMATCH because Grep and Glob were not delivered)
- reports:   tube-self-supervised-2026-09-17-round4-roles/
- rounds:    4 blind rounds; past the cap of 3, not converged; escalated to Tony

The role reports were written verbatim as each arrived. Personal absolute paths were replaced with
`<worktree>`, `<scratchpad>` and `<darkroom>`, and one retired acronym spelling that the Cross-Examiner
quoted as absent was redacted so sapper SAP014 passes; nothing else was changed. No reviewer opened the
off-limits folders, except that RTFM ran `git log --oneline -3` on one tool and disclosed it (it relied
on none of the three subject lines).

### Role ledger

| # | role | grant declared | findings | most severe |
|---|---|---|---|---|
| 1 | Prove It | GRANT 1 MISMATCH — missing Grep, Glob; holds no forbidden tools (Read, Bash only; no Edit, Write or NotebookEdit) | 17, plus a full claim ledger | high: J is 10 s; the chance comparison; medium: supervised folds 2 and 3 are one model |
| 2 | DOI or Die | GRANT 2 MISMATCH — missing Grep, Glob; holds no forbidden tools (held: Read, Bash, WebSearch, WebFetch) | 10; all 29 references exist | high: the Kreuz group's event detection originates in Kreuz et al. 2017 |
| 3 | Cross-Examiner | GRANT 3 ok — Read, Grep, Glob | 22 | high: J is 10 s; "no more co-activity than chance" |
| 4 | Reviewer 2 | GRANT 4 MISMATCH — missing Grep, Glob; holds none | 18 | blocking: shift events scored against the unshifted recording; localization is imprecise, not chance |
| 5 | Kill Your Darlings | GRANT 5 ok — Read, Grep, Glob | 37, by hand (`murderboard_prose.sh` not vendored; no Bash) | high: a paragraph appears twice |
| 6 | RTFM | GRANT 6 MISMATCH — missing Grep, Glob; holds no forbidden tools (I hold Read, Bash, WebSearch, WebFetch) | 14 | high: J is 10 s; the chance comparison |
| 7 | Reinventing the Wheel | GRANT 7 MISMATCH — missing Grep, Glob; holds none (I have Read and Bash, and no editing tools) | 9 | high: J is 10 s; medium: real rasters round frames while the encoder truncates |
| 8 | You Lost Me | GRANT 8 ok — Read, Grep, Glob | 18, plus a per-section and per-figure table | blocking: undefined terms in the summary, the problem section, Figures 3 and 4 |
| 9 | Show, Don't Tell | GRANT 9 MISMATCH — missing Grep, Glob; holds no forbidden tools (holds Read, Bash) | 12 | high: the twin check has no figure |
| 10 | Ship It | GRANT 10 MISMATCH — missing Grep, Glob; holds no forbidden tools (holds Read, Bash) | 17 rows; figures and summary rebuild byte-identical | medium: hidden and unidentified marks, glyph reuse across figures |
| 11 | Start With the Problem | GRANT 11 ok — Read, Grep, Glob | 14 | medium: the answer to the title question is buried; the bake-off splits the modulation thread |
