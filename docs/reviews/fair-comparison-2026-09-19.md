# Murderboard run — the fair comparison's report

## The problem the review was for

The weekend run tuned both sides of goal 2's comparison (four learned detectors, six coded ones) on
the current simulator, with nested cross-validation, a shared false-alarm budget, and a second draw of
recordings on another workstation. The project lead asked for a report a newcomer could read, with
figures that explain what was done and why, and for it to be reviewed before it went out. The
question for the review: **does the page say what the run shows, no more, in words a newcomer can
follow?**

## What the review found

The review changed the answer twice. The first draft said no net was ahead of the tuned CoactDetect
and that binned SCE's first place did not stand.

- **Round 1** found that the two sides had not shared one setting. The coded searches tuned their
  merge gap (how close two calls must be before they merge); the nets' was fixed at 2 s. Re-scored
  with only that setting changed, the best net moves ahead on F1 alone. The page then said the run
  does not settle which side is better.
- **Round 2** found that reversal holds on F1 alone only: under the budget CoactDetect stays ahead at
  every matched gap. It also found that the replicate's "agreement" came from two refits that failed to
  train; set aside, the replicate's best net leads fold by fold. And it asked where the two sides
  actually differ: the faintest events, joined by 10% of the ROIs, go to the chorus nets against a busy
  background and to CoactDetect against a quiet one (the report's Figure 12).
- **Round 3** found no wrong number in the tables and a page still saying more than its evidence.
  Setting failed refits aside is a check made after seeing the held-out scores, so the page now leads
  with every refit counted: CoactDetect ahead on average in both draws and both selections, the net
  ahead only at a matched gap or fold by fold in the replicate. The under-budget lead at matched gaps
  is as weak as the F1-alone reversal. The nets' data handicap (10 of 72 training recordings), the
  budget's shape (CoactDetect's own rates times a declared 1.6), and what the nets were trained on
  (the same probe and distractors, labeled negative) now sit in the answer and the limits. The earlier
  +0.103 lead was not lost to tuning the nets: untuned, the best net is already within 0.02 F1 of the
  tuned CoactDetect.

Every sentence the page states about the run's results is printed only while it holds: the builder's
`claim()` stops the build otherwise. It fired twice while round 3's fixes were applied, once on a
sentence a reviewer had endorsed (chorus_norm does not beat CoactDetect on faint busy-background events
in every fold under the budget; only chorus_gain_norm does).

The review also found a problem outside this report: goal 1's published crowded numbers for its sliding
CoactDetect and LoCo compare two seed sets. Filed as
`docs/todo/2026-09-19-goal-1s-crowded-numbers-compare-two-seed-sets.md`; the goal pages were not edited,
per the brief.

## What would validate it, and what it does not settle

- A rerun that tunes the nets' merge gap like any other parameter (re-scoring only, no retraining).
- The crowded-recording check run on the nets, in both draws.
- A sensitivity sweep of the budget's 1.6 margin.
- Nets fitted on all 72 training recordings rather than 10.

Until those, the page's answer is: under the budget, CoactDetect ahead of every net in every fold of both draws, with binned SCE the one coded detector that admissibly beats it in some folds; on F1 alone, a
near tie whose sign depends on the merge gap and on the draw.

## Appendix

- upstream:  syncytium2/murderboard @ 08f5ddb
- copy:      vendored @ 08f5ddb
- freshness: current
- artifact:  docs/learned/tuned_vs_coact/fair_comparison_2026_09_18/report.html (76c3270 -> 3c94e2e)
- roles:     11 of 11 run (named agents), in each of three blind rounds
- reports:   fair-comparison-2026-09-19-round3-roles/
- rounds 1 and 2 reports: fair-comparison-2026-09-19-roles/ and fair-comparison-2026-09-19-round2-roles/
- rounds:    3 blind rounds (the cap); round 3 of 3 still had blocking and major findings, which were
  fixed and then checked by a finding-driven pass and a fresh role 10 run on the final build (below)
- Stopping reason: round 3 of 3, the process's cap on blind rounds.

Mode: standard

Unedited originals of every role report, with this machine's paths, are in
`<darkroom>/bugarach/2026-09-18-fair-comparison-run/report/review-roles/`, `review-roles-round2/` and
`review-roles-round3/`; the repository copies differ only in those paths. Round 3's originals were
extracted from the agents' own transcripts after the repository copies had been scrubbed, and match
them byte for byte apart from the paths and a trailing newline.

### Findings by round (highest severity each role gave)

| role | round 1 (76c3270) | round 2 (16ac704) | round 3 (5c0ccbb) |
|---|---|---|---|
| 1 · Prove It | blocking | major | moderate |
| 2 · DOI or Die | major | major | major |
| 3 · Cross-Examiner | major | medium | medium |
| 4 · Reviewer 2 | blocking | blocking | major |
| 5 · Kill Your Darlings | major | high | high |
| 6 · RTFM | major | high | medium |
| 7 · Reinventing the Wheel | major | medium | medium |
| 8 · You Lost Me | blocking | blocking | blocking |
| 9 · Show, Don't Tell | high | major | major |
| 10 · Ship It | major | moderate | medium |
| 11 · Start With the Problem | high | high | high |

### Role ledger

Round 1, on 76c3270:

**1 · Prove It** — GRANT 1 ok — Read, Grep, Glob, Bash
A limits sentence the record did not back; coded candidates wrongly said to go through the inner
rotation; a false Figure 8 caption ("no dot is to the right of it").

**2 · DOI or Die** — GRANT 2 ok — Read, Grep, Glob, Bash, WebSearch, WebFetch
No reference list; "ports of established methods" wrong; binned SCE uncredited and SPIKE-synch's
window misdescribed.

**3 · Cross-Examiner** — GRANT 3 ok — Read, Grep, Glob
Thirty-one consistency findings, the recording count on two bases among them; Table 2 and the job
counts recomputed clean.

**4 · Reviewer 2** — GRANT 4 ok — Read, Grep, Glob, Bash
The merge gap was tuned for the coded side only; the headline changed on it.

**5 · Kill Your Darlings** — GRANT 5 ok — Read, Grep, Glob
Thirty-three line edits and a passage test of every long block.

**6 · RTFM** — GRANT 6 ok — Read, Grep, Glob, Bash, WebSearch, WebFetch
The coded side's search misdescribed; the false Figure 8 caption; the earlier-lead causal claim
confounded; the probe rate wrong.

**7 · Reinventing the Wheel** — GRANT 7 ok — Read, Grep, Glob, Bash
The architecture figure drawn by hand instead of through the project's tool; the raster copied
without its rules; a copied paired statistic that matched exactly.

**8 · You Lost Me** — GRANT 8 ok — Read, Grep, Glob
Undefined terms from the header on; "distractor" defined circularly; the nets known only by code
names.

**9 · Show, Don't Tell** — GRANT 9 ok — Read, Grep, Glob, Bash
Thirteen findings on sections carried in prose that figures should carry.

**10 · Ship It** — GRANT 10 ok — Read, Grep, Glob, Bash
A stale build, an overplotted results figure, a false caption, unnumbered tables.

**11 · Start With the Problem** — GRANT 11 ok — Read, Grep, Glob
The crowded veto arrived after the results it changed.

Round 2, on 16ac704:

**1 · Prove It** — GRANT 1 ok — Read, Grep, Glob, Bash
The tube refit's mechanism wrong; "loses nothing" contradicted by two nets; a dangling reference.

**2 · DOI or Die** — GRANT 2 ok — Read, Grep, Glob, Bash, WebSearch, WebFetch
The nets are the Deep Sets shape; binned SCE is not the 2003 rule; CICADA needs its DOI.

**3 · Cross-Examiner** — GRANT 3 ok — Read, Grep, Glob
Nineteen findings; "admissible" used two ways; the crowded reference against goal 1's record.

**4 · Reviewer 2** — GRANT 4 ok — Read, Grep, Glob, Bash
The reversal holds on F1 alone only; the replicate's agreement is failed training; pooled F1 hides
where the sides differ.

**5 · Kill Your Darlings** — GRANT 5 ok — Read, Grep, Glob
Twenty-four findings; the dangling context-window rule; payloads buried.

**6 · RTFM** — GRANT 6 ok — Read, Grep, Glob, Bash, WebSearch, WebFetch
The same two scope findings as role 4, independently; one-to-one matching; "matched" is nominal.

**7 · Reinventing the Wheel** — GRANT 7 ok — Read, Grep, Glob, Bash
Nineteen reuse findings, none changing a number.

**8 · You Lost Me** — GRANT 8 ok — Read, Grep, Glob
The lede's undefined terms; the hit rule contradicted a figure.

**9 · Show, Don't Tell** — GRANT 9 ok — Read, Grep, Glob, Bash
The headline, the bench and the counting modes had no picture.

**10 · Ship It** — GRANT 10 ok — Read, Grep, Glob, Bash
Figure 5's curves unidentifiable; Figure 8's diamonds hid dots.

**11 · Start With the Problem** — GRANT 11 ok — Read, Grep, Glob
The merge gap filed as a fairness device ahead of the results.

Round 3, on 5c0ccbb:

**1 · Prove It** — GRANT 1 ok — Read, Grep, Glob, Bash
Every table number recomputes; the replicate's "best net" used two rules; a spread figure from the
wrong selection.

**2 · DOI or Die** — GRANT 2 ok — Read, Grep, Glob, Bash, WebSearch, WebFetch
CoactDetect's null credited to jitter instead of whole-train shifts; Cecchini 2021 and the Kreuz
correspondence uncited; the scorer misparaphrased.

**3 · Cross-Examiner** — GRANT 3 ok — Read, Grep, Glob
Fourteen findings; five starting points over the budget, not four; the crowded-seed explanation.

**4 · Reviewer 2** — GRANT 4 ok — Read, Grep, Glob, Bash
The headline's confidence overreached: the under-budget matched lead is weak, the data handicap and
the budget's shape were out of the answer, binned SCE's verdict rested on a handicapped comparison.

**5 · Kill Your Darlings** — GRANT 5 ok — Read, Grep, Glob
Twenty-five findings; the scorer's warning buried against the margins it undercuts.

**6 · RTFM** — GRANT 6 ok — Read, Grep, Glob, Bash, WebSearch, WebFetch
The set-aside is post hoc; the training seed picks the recordings; the rescue rule's axis order.

**7 · Reinventing the Wheel** — GRANT 7 ok — Read, Grep, Glob, Bash
Eight findings; the start-over-budget helper missed locust; the breakdown pools by hand.

**8 · You Lost Me** — GRANT 8 ok — Read, Grep, Glob
The lede and Table 1 still carried undefined terms; Figure 8 read as a forest plot.

**9 · Show, Don't Tell** — GRANT 9 ok — Read, Grep, Glob, Bash
The crowded check and the failed refits as prose; Figure 11 showed half its contrast.

**10 · Ship It** — GRANT 10 ok — Read, Grep, Glob, Bash
One glyph meaning two things across four figures; crossing leaders; phone width undisclosed.

**11 · Start With the Problem** — GRANT 11 ok — Read, Grep, Glob
The merge-gap concept arrived after five forward references to it.

### Adjudications

**Round 1** (applied at 2ca264e): the merge-gap finding changed the headline; binned SCE's lead is its
30 s merge; the probe rate, backgrounds, hit rule, tube description, distractor construction and
origins corrected; the contamination limit cites its record; tables numbered; the hand-drawn
architecture figure removed on the project lead's ruling.

**Round 2** (applied at 69480a7).

Fixed, with the evidence each needed:

- **The reversal is on F1 alone only** (roles 4 B1, 6 #1). Under the budget CoactDetect stays ahead of
  both chorus nets at every matched gap. The lede, section 7 and Figure 10 now say so; the builder
  refuses to print the lede's budget sentence unless it holds in both draws and at every gap.
- **The replicate's "agreement" was failed training** (roles 3 #7, 4 B2, 6 #2, 11 #3). One rule,
  refits under 0.2 F1 set aside, now applied to both draws from one function
  (`fair_comparison_evidence._refit_health`); Figure 8 draws every affected fold twice; section 6
  says the two draws disagree on F1 alone and agree under the budget; section 10 lists the
  replicate's low refits beside this run's.
- **Where the two sides differ** (role 4 M1): new `breakdown` evidence and Figure 11; section 8.
- **Crowded-check reference** (roles 1 m7, 4 M10, 6 #13, 7 #1): the tool now scores goal 1's shipped
  reference too; "changes no verdict" is computed from `crowded_check.json`. The 0.826 against goal 1's
  0.818 (role 3 #6) is a seed-set difference (goal 1 publishes its held-out crowded seeds 49–60; the
  check uses 1–12, as goal 1's search does), stated on the page and in the tool.
- **One-to-one matching** (roles 6 #5, 8 F2, 5 F17): section 2 corrected; new Figure 2 draws the rule.
- **Dangling context-window reference** (roles 1 M4, 5 F3, 6 #11, 8 F3): the rule is stated in 4.1,
  with the values it removed computed from `bench.FULL_GRIDS`.
- **"A wide merge gap loses nothing"** (roles 1 M2, 3 #1, 6 #4): now true only where true; the nets it
  costs are named, and merging's chaining is stated.
- **The tube refit's mechanism** (roles 1 M1, 6 #6): its threshold came from the inner fits, not two
  recordings; the text now depends on the selection.
- **Argument order** (role 11): terms first; rules before numbers (4.5 is now the crowded check,
  method only); the merge gap its own section after the results; the t discussion moved to 4.1.
- **Attributions** (role 2): the nets as the Deep Sets shape; binned SCE not the 2003 rule; CICADA by
  DOI; SPIKE-synch's root; CoactDetect's nearest published null; t citations in full; draughtsman
  identified; nested cross-validation cited.
- **Figures** (roles 9, 10): whole-recording lane (Figure 1A), scoring (2), binned against sliding
  (5), both draws per fold (8), matched gaps both selections (10), breakdown (11), tuning (12);
  Figure 6 of round 2 (two seed strips) dropped; Figure 9B labels tied to their curves by leaders,
  axis stated as not to scale, rings de-collided; panel letters punctuated; threshold colour no longer
  shared with the replicate.
- **Wording and numbers**: corrected *t* factor 0.655 (√(3/7)); reproduction bounds as measured
  (0.0015 per refit); lowest other refit 0.51 printed from data; "tuned CoactDetect"; "empty
  recordings"; only the quiet empty recordings gate the budget; budget counts calls after merging;
  the 3-hour crowded recordings; "indicate" for "bound"; participation item paraphrased; hostnames
  moved to section 12; minus signs; "an F1"; 10⁻⁵.
- **Reuse** (role 7): `mmss` → `time_axis.label`; `NAME` from `TITLES`; stable raster sort; `n_part` from
  the ground truth; gap grid from `merge_gap.json`; the test's draw rule gains `seed*1000`; docstring
  corrected about the provenance line.

Not changed, and why:

- Role 7 #9 ("the `cmp` fallback is unreachable"): it is reached, by every coded row of Table 2; kept,
  now through the shared `stats` helper.
- Role 7 #2, #3, #4, #7, #8, #10, #16, #19: copies that agree on these data today (each verified by
  role 7 itself); left as they are, with the test covering the draw rule. Moving the Nadeau–Bengio
  factor into `src/` is outside this report.
- Role 7 #6 (rate+context not in the merge-gap ablation): stated on the page rather than re-run.
- Role 7 #18 (the test's own path check): filed upstream as
  `docs/sapper_feedback/2026-09-19-sap004-cannot-see-a-backslash.md`.
- Role 4 M2 (F1 with distractor calls left out) and M8 (sensitivity to the 1.6 margin): not run; the
  precision ceiling and "no sensitivity was run" are stated.
- Role 4 M6 (real candidate cloud for Figure 6): the schematic stays, as the concept figure the brief
  asks for; held-out false-alarm rates are now given in section 10.
- Role 6 #14 (probe overlap under wide merges): not verified; recorded here as open.
- Role 9 #8 (Table 3 as a chart): Table 3 kept, now with both references.
- Role 8 F4 (architecture drawings): the drawings are draughtsman's by the project lead's ruling
  (2026-09-19); section 12 points to them on pull request #660.
- The contamination stated as a limit (roles 1 u1, 4 m17, 11 round 1): the project lead's brief for
  this report asked for exactly that; the page says so and says listing it is not evidence the effect
  is small.
- `docs/goals/` not edited, per the brief.

**Round 3** (applied at 1a0a260). Fixed:

- **Every refit counted first** (roles 1 #1, 4 #8, 6 #3): the lede and section 6 lead with the
  all-refit comparison; the set-aside is labeled a check made after seeing held-out scores, and
  section 6 names the two places the page looks at them. Section 10 says no rule fixed in advance picks
  out the failed refits (the picker's warning also fires on healthy ones).
- **The headline held to its own uncertainty** (role 4 #1, #2, #4, #9; role 1 #6, #7): the under-budget
  matched-gap *t* values are given beside the F1-alone ones; the lede names the budget's shape, the nets'
  data handicap, and the draw-and-machine confound; the earlier lead's loss is narrowed to the simulator
  and CoactDetect's tuning (untuned, the best net is within 0.02 F1 of the tuned CoactDetect in both
  draws); "the chorus nets", not "the nets".
- **What was not made equal** gets section 4.6 (role 11 #2); the merge-gap concept moves to section 2
  with its own figure (role 11 #1, role 9 #3); the terms follow the answer (roles 5 F1, 8 #1, 11 #3).
- **Figures** (roles 8, 9, 10): the margins figure drops the connecting lines that read as intervals
  and rings the affected folds, and every per-fold figure rings them the same way; the gap curves get a
  logarithmic axis with 0 s set apart and a key instead of crossing leaders; the participation
  breakdown shows all three levels; the crowded check becomes a figure; keys on every per-fold figure;
  units on the counting schematic; the refused locust row loses its mean bar.
- **Numbers and wording** (roles 1, 3, 5, 6): five starting points over the budget, not four; the
  spread figure scoped to the budgeted chorus nets (23 per hour); 8 to 12.5; "0.79 or more"; the probe's
  added rate; "within a second"; the training seed picks the recordings; inner fits shared between outer
  folds; alpha as a tuning parameter; the rescue rule's grid order; the three merge rules; the post hoc
  check cannot find a passing configuration; the crowded-seed explanation corrected (the shipped values
  match goal 1's; its published sliding values come from held-out seeds) and moved to Table 3's caption;
  the tolerance measured at shipped settings; normalization over the whole recording; the nets trained
  on the probe and distractors as negatives; binned SCE compared at a matched 30 s, its admissible
  fold-4 win acknowledged, the replicate's SCE results left open.
- **Attributions** (role 2): CoactDetect's null to whole-train and per-cell shifts (Pipa 2008, Bocchio
  2020, Dard 2022), Grün part II, the guard to Rohling 1983; SPIKE-synch's window to Quian Quiroga and
  colleagues 2002 and its detection step to Cecchini and colleagues 2021, with the Kreuz correspondence
  cited as personal communication, not quoted; "designed here" read as "not found elsewhere yet"; the
  2003 SCE root credited as reached, with Mao 2001 not obtained; CICADA with Dard 2022; Corso 2020 for
  multi-statistic pooling.
- **Reuse** (role 7): the context-rule values from the run's declared grids through
  `bench.context_fits_the_null`; the start-over-budget helper counts refused starts.
- **Glossary**: call, firing, background, empty recording, refit, failed-training signature; the merge
  gap and budget entries corrected.

Not changed, and why:

- The architecture drawings (roles 8 #5, 9 #9): the project lead ruled on 2026-09-19 that they belong
  to draughtsman, not this page; section 12 now points at the drawings, which exist in the darkroom and
  on pull request #660.
- A headline figure beside the lede (role 9 #1): the lede is now plain words, and Figure 9 carries both
  draws per fold one section later.
- Moving the *t*-correction paragraph out of section 4.1 (roles 9 #5, 11 #9): round 2's role 11 asked
  for the opposite move; it stays in 4.1, now leading with its conclusion.
- Terms as a definition list (role 9 #10), captions cut to 60 words (role 9 #8), panel headings as short
  tags (role 10 F8): left as they are.
- Role 7 #2 (`breakdown` pools by hand), #4, #5, #6: agree exactly with the canonical code on these
  data, as role 7 verified; not refactored in this report.
- Role 4 #5 (justify leaving the busy empty recordings out of the budget): the page cites the project
  lead's pre-run decision and now reports those rates; the justification is the lead's to give.
- Role 6 #1 (tuned minus untuned under the budget is not like for like): relabeled rather than
  recomputed at a budgeted untuned threshold.
- Role 2's unsearched literatures and the questions it could not ask (the CICADA authors on citation;
  Grün's or Amarasingham's groups on the null): carried to the residual list.

### Follow-up on the final build

Round 3 was the last blind round the process allows, and it still had blocking and major findings, so
its fixes were checked on the rebuilt page (805b113) two ways, both archived in
`fair-comparison-2026-09-19-followup/`:

- **A finding-driven pass** (`00-finding-check.md`, a general agent, not one of the eleven roles)
  graded every round-3 finding against the page and recomputed every number in the lede and sections
  6 to 10. Every blocking and major finding was fixed or deliberately declined. It found one new major
  error the fixes had introduced: section 9 said the crowded-recording check was never run on the
  replicate, when it had been. Read from the replicate's own `crowded_check.json` and `selections/`,
  binned SCE under the budget is admissible and ahead of CoactDetect in 3 of 4 replicate folds. The
  page and the lede now say so, behind a `claim()` guard. It also found one moderate overreach (the
  budget contrast stated as margin size, which the replicate contradicts; now stated as consistency,
  every net behind in every fold of both draws, guarded) and six minor ones, all fixed at a07fd9d.
- **Role 10 re-run in full** on the new render (`10-ship-it.md`), with the same grant as its rounds
  above. No high-severity finding; four medium ones (stale figure numbers in the SVG labels, the
  axis-break bridge style in Figure 11, Figure 8's no-result marks, the ringed dot's two meanings),
  all fixed at a07fd9d. Left as judged: tick-label spacing (`2 s` against the viewer's `8s`) and the
  red and green verdict text in Figures 5 and 6, whose words carry the meaning.

The page shipped (hash in the appendix header) is the build after those fixes. It was not reviewed
again blind; the residual list below is what a fourth round would start from.

### Residual ⚠

For the project lead to resolve:

- ⚠ **The page's answer rests on choices the lead has not signed**: the budget's 1.6 margin (no
  sensitivity run), the crowded check's 0.02, and leaving the busy empty recordings out of the budget.
- ⚠ **The contamination is stated as a limit, not treated as a stop.** CLAUDE.md says a known
  contamination stops the work; the brief for this report asked for it to be stated plainly as a
  limit, and the page does that. The bench does not read the contaminated folder at run time, but its
  fitted values were measured on it. Whether that is enough is the lead's call.
- ⚠ **The merge-gap asymmetry is unresolved.** The rerun that tunes the nets' merge gap (re-scoring
  only) has not been run, so the F1-alone comparison is not settled.
- ⚠ **The replicate's nets were not checked on crowded recordings**, and neither were this run's.
- ⚠ **The architecture drawings are pointed to, not shown** (pull request #660, unmerged). Once it
  lands, the lead may want them embedded; three rounds of role 8 and role 9 asked for a picture of
  how the nets work.
- ⚠ **Nobody has asked** the CICADA authors how they want the software cited, or Grün's or
  Amarasingham's groups whether CoactDetect's time-shift null is published; the Kreuz correspondence
  is cited, not quoted.
- ⚠ **Literatures not searched** for the "designed here" detectors: genomics peak calling,
  seismological event triggers, adaptive image thresholding, changepoint detection.
- ⚠ **Goal 1's crowded numbers** compare two seed sets (the todo above); the goal pages were left
  alone.

Minor items left open by the final pass: "setting" still carries more than one meaning in a few
places; short panel tags remain above some panels; the evidence tool pools the breakdown by hand
(agrees exactly with `bench.pool_scores` on these data) and infers "refused every configuration" from
the search's counts (agrees with the run's `within()` on all 24 selections); section 4.2 and the
statistical paragraph stay where they are.
