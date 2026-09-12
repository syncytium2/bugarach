# Murderboard run — the surrogate screen's three reports

- upstream:  syncytium2/murderboard @ 81a0927
- copy:      vendored @ 81a0927
- freshness: current
- artifact:  `<darkroom>/bugarach/2026-09-11-surrogate-screen/report_steps_excluded.html`
  (`f39e4979` -> `566a2c20`), with its companions `report_cossart.html`
  (`05db65b3` -> `dfcd9ba6`) and `report_summary.html` (`ea7127e0` -> `18edde2c`)
  — rebuilt twice after the review, for the two defects at the end of this record
- roles:     11 of 11 run (each spawned as its own compiled per-role agent, not an inline
  prompt; role 4's round-2 instance declared MISMATCH, holding an editing capability over
  the artifact's location beyond its grant — its own words are in the ledger)
- rounds:    2 — and the second was **not clean**. See the residuals.

## The problem this review was for

The screen measured 728 grid cells in order to decide nothing. It shortlists no
surrogate, by design: its entire value is that a later design session can trust the
numbers it reports. So the only defect that matters here is a number that reads as a
result and is not one.

The first build already carried the two findings that make the screen worth reading —
that no Holm-adjusted yardstick can flag anything at these settings, and that on the
Cossart twin the destruction measure cannot register removal at all. Both survived
review intact. What did not survive was a ring of numbers standing next to them,
each of which looked like a measurement of a candidate and was a measurement of
something else: the scoring apparatus, the twin's ROI count, or the population the
number happened to be averaged over.

Five of those are worth stating plainly, because each was invisible in the page and
each changes what a reader would conclude.

**The control that proved the destruction measure works could not fail.** Every page
presented the whole-window circular shift as the must-pass control: it reads 0.00, so
the measure can see removal. But `assess.circular_shift_trains` is documented in this
repo as *"the assessor's null"*, and `assess_coactivity` draws all 200 (or 20)
surrogates from that same function. A circular shift is therefore a sample from the
distribution the excess is measured against. It reads 0.00 by construction, and would
read 0.00 if the measure were broken. Homogeneous resample also reads 0.00 without
being the null, and is now named as the honest zero-reader.

**Saturation was tested at one jitter radius and generalised to six.** The expected
number of co-active ROIs still inside the assessor's coincidence bin is
`recruited x bin / (2J + 1)` — it *falls* as *J* grows, so the largest radius is the
least saturated one in the sweep. The build tested there, found the fast stream
unsaturated, and printed "the measure can register removal on this twin." Recomputed
at every radius, 3 of 6 fast radii are saturated: at *J* = 0.1, 0.2 and 0.4 s about
15.5, 15.5 and 8.6 ROIs stay in the bin against a scan stopping at 8. (Those first two
counts read 25.8 and 15.5 in the build this review shipped, because the formula multiplied
the recruitment by `bin/(2J+1)` without capping it at 1 — a probability cannot exceed 1, so
the count cannot exceed what the event planted. Corrected 2026-09-12; the saturation
verdicts are unchanged, the printed counts were not.) Every headline
span — "retained 0.96 → 0.00" — began at a radius where retention *cannot* fall.
Those entries are now marked † and the report computes saturation per radius.

**The headline flag rates were computed on a different population than the tables
beside them.** The ⚠ box said "32% of checks fall outside the band's 95th percentile
and 38% have a raw paired *P* under 0.05", then ended by saying that cells which
cannot reach α are excluded from every paired rate. They were not excluded from those
two numbers, which also counted all five group scopes on one folder and one on the
other. On the population the tables actually use, the paired figure is 14–16 points
higher. Both rates are now computed exactly as the tables compute them.

**A third of the band rate was not a percentile comparison.** For the sub-floor family
of statistics the real value is identically 0 — the floor *is* the observed minimum —
so the mouse-split band has zero width and "outside the 95% band" degenerates into
"not exactly equal to zero". That covers 7,225 of 18,785 pooled checks on
`steps_excluded` and 312 of 858 on Cossart. Excluding them, the band rate is **9.9%**
rather than 31.6% (**7.7%** rather than 26.9%). Both are now reported, because the
difference is the measure changing, not the candidates.

**One column was another column rescaled.** With the real sub-floor rate 0 in every
window by construction, AUC reduces exactly to `0.5 x (1 + dithered share)` — verified
equal on all 18 rows to 2.2e-16. Two columns implied two pieces of evidence where
there was one.

## What each round cost

| round | who ran | findings | blocking | outcome |
|---|---|---|---|---|
| 1 | all 11 roles, named agents, against the first build | ~170 | 14 | builder rewritten; nearly all applied |
| 2 | blind, 6 roles (1, 3, 4, 8, 10, 11) against the rebuilt pages | 89 | 4 | 2 new blocking from role 4 alone; all applied |

Round 2 was a blind pass — the reviewers were given the rebuilt artifact, not the
round-1 finding list. It produced new blocking findings, which is the point of running
it and also the reason this review is not finished: see residuals.

## Role ledger

One declaration per role, as that role reached it. Role 4 ran twice and its two
instances did not reach the same verdict; the MISMATCH is the one recorded, because it
is the stronger claim and the one a reader must weigh.

**1 · Claim & data verifier — "Prove It."**
GRANT 1 ok — Read, Grep, Glob, Bash
Round 1: 19 findings, 5 blocking — recomputed every quoted number against the CSVs.
Round 2 (blind): 11 findings, 2 blocking; 43 of 52 claims reproduced exactly.

**2 · Citation & reference validator — "DOI or Die."**
GRANT 2 ok — Read, Grep, Glob, Bash, WebSearch, WebFetch
Round 1: 14 findings, 2 blocking — four of six "Stella's names" are not Stella's;
Elephant supplies seven of twelve candidates and was never named; no reference list.
Not re-run in round 2.

**3 · Consistency auditor — "Cross-Examiner."**
GRANT 3 ok — Read, Grep, Glob
Round 1: 15 findings, 3 blocking — freeze-half absent from every page; per-draw tallies
summing to 289 beside a stated 291.
Round 2 (blind): 18 findings, 2 blocking — the *K* reserved-word collision, and the grid
counted 530/198 against the folder pages' 528/197.

**4 · Adversarial reviewer — "Reviewer 2."**
GRANT 4 MISMATCH — missing none (holds Read, Grep, Glob, Bash as granted); holds additionally a claude.ai Dropbox MCP server whose surface includes create/upload/move/copy/delete over the Dropbox tree in which the artifact under review lives. No Edit/Write/NotebookEdit. I used none of the Dropbox write tools and edited nothing; declaring it because it is an editing capability over the reviewed artifact's location, which is the thing the no-edit rule exists to prevent.
Round 1: 13 findings, 2 blocking — the §9 reconciliation was a check that could not fail.
Round 2 (blind): 13 findings, 2 blocking — the circular-shift circularity and per-*J*
saturation, both narrated above. This instance's declaration is the MISMATCH quoted
here; the round-1 instance held exactly its granted tools.

**5 · Line editor — "Kill Your Darlings."**
GRANT 5 ok — Read, Grep, Glob
Round 1: 46 rows checked; zero AI-register hits. Number/noun disagreement ("1 cells"),
two multiplier notations, ISO timestamps to the second in body prose.
Not re-run in round 2.

**6 · Methods / domain expert — "RTFM."**
GRANT 6 ok — Read, Grep, Glob, Bash, WebSearch, WebFetch
Round 1: 12 findings — three of them unfixable by rebuilding; see residual 3.
Not re-run in round 2.

**7 · Reuse auditor — "Reinventing the Wheel."**
GRANT 7 ok — Read, Grep, Glob, Bash
Round 1: 11 findings — `_round_half_up` duplicates `matlab_round`; a CSV writer missing
`lineterminator`; the bespoke SVG kit judged justified by the plan's inline-SVG rule.
Not re-run in round 2.

**8 · Naive-reader accessibility — "You Lost Me."**
GRANT 8 ok — Read, Grep, Glob
Round 1: 22 findings, 10 blocking — "the assessor", "stream" and "the producer" carry
real load and were never defined.
Round 2 (blind): 18 findings — the *f* symbol collision, code identifiers in
audience-facing prose, and "what gives it away" lists truncated with no count.

**9 · Density & figure-first — "Show, Don't Tell."**
GRANT 9 ok — Read, Grep, Glob, Bash
Round 1: 11 findings, 5 major — figure-free sections of 800–965 words carrying
2,000-pixel tables.
Not re-run in round 2.

**10 · Build & craft gate — "Ship It."**
GRANT 10 ok — Read, Grep, Glob, Bash
Round 1: 17 findings — stale figure PNGs reviewed as current; summary renders absent.
Round 2 (blind): 16 findings, 2 high — the render gate could not fail, and contrast is
never evaluated.

**11 · Argument order — "Start With the Problem."**
GRANT 11 ok — Read, Grep, Glob
Round 1: 10 findings, 2 blocking — the reader never meets the problem; Figure 1, the one
picture of what a leak is, was section 3 of 11.
Round 2 (blind): 12 findings — no Terms section on the entry page; a dangling
"see *Per group*" pointing at a section that does not exist on that folder's page.

## What was applied

Beyond the five findings narrated above:

- **A defect this review did not catch, found the next day and fixed.** The saturation
  arithmetic read `recruited x bin/(2J+1)` with no cap, so it reported 25.8 expected
  co-active ROIs from a twin that recruits 15.5, and 471.7 from one that recruits 283 —
  impossible counts, in the build eleven roles had just signed off. It surfaced only when
  the same formula was run across every radius to plan the follow-up. Capped at the
  recruitment, with a test asserting the expected count never exceeds it.
- **A second defect this review did not catch, and the probe did.** The report told the
  reader a corrected test would need "at least 1299 mouse splits and 2599 draws". Those
  are the samples at which the Holm-adjusted floor *equals* α — and a check fires on
  `P < α`, so equality fires nothing. The correct minimums are **1300 and 2600**. It came
  to light on 2026-09-12 by running the screen at the boundary the same formula blessed:
  at 13 statistics with 259 splits and 519 draws, uniform dither — the known-bad control
  — was flagged 7 of 13 (band) and 11 of 13 (paired) raw, and **0 of 13 under Holm**,
  smallest adjusted *P* exactly 0.0500. The formula existed in two modules and was wrong
  in both; there is now one implementation (`surrogate_stats.smallest_n`) and a test that
  brute-forces the boundary. The pages are rebuilt and say 1300 and 2600.
- **The gate that could not fail now fails.** `render_check.py --json` returns 0 before
  it counts anything; on one build it exited 0 while its own JSON held 104 sub-11px
  labels, 5 overlaps and 2 viewBox escapes. The vendored copy is stamped "do NOT edit,
  re-copy", so the fix went where it belongs — the caller. `run_gate` now counts small
  type, overlaps and escapes itself, records them in `gate.json`, and raises. The final
  build reports 0/0/0 across 7,569 measured text nodes in 9 views per page, floor 11.0px.
- **Stale evidence is deleted on rebuild.** Two reviewers read three-build-old
  screenshots as current, one quoting "291 of 530" against a page saying 289 of 528.
  Figure PNGs and extracted SVGs are now cleared before each build.
- ***K* was a reserved word.** `docs/GLOSSARY.md` defines *K* as the coactivity floor;
  the report also spent it on draw counts. The pages now say "draws" and "co-active
  ROIs" and leave *K* alone.
- **One grid, one count.** The summary said 530/198 cells where the folder pages said
  528/197 — the freeze-half destruction control. Both now say "carrying statistics".
- **The Cossart page was quoting the other folder's budgets**, including a 400-second
  joint-ISI budget on a folder where no joint-ISI cell ever ran. Budgets are now derived
  per folder, and the pages state that `run_notes.json` stops at 13:28 EDT and does not
  cover the Windows phase that produced the finished cells.
- **The 20% participation arm** was measured at a floor of 6 co-active ROIs on one page
  and 8 on the other, under a header reading "at the largest *K*", and the run's own
  `destruction_status` ("not run: the planted events carry no excess at this K") was
  printed nowhere. Both are now on the page.
- **Two Cossart cells that errored** on a Dropbox file-replacement failure and were
  rerun to 40 draws are now disclosed; the word "error" had appeared in no report.
- ***J* is a frame count on Cossart**, where the frame interval varies 0.0926–0.1190 s
  across sessions — a 28% spread, so *J* = 32 frames is 2.96 s in one session and 3.81 s
  in another, pooled into one grid cell. Now stated.
- **A statistic that flags its own negatives is marked ‡** where it is cited as
  evidence. The page had promised this and marked nothing, while the fast interval-
  density statistic ran synthetic negative rates of 0.55–1.00 and was cited for nine of
  twelve candidates.
- **Void discriminator columns print "void"** instead of an accuracy, and the
  cross-folder claim "measured on two folders" now says how many candidates were
  measured on both (three were measured on only one).
- **"A hypothesis this comparison tests"** became "bears on but cannot settle", beside
  the confounds the same page lists.

Nineteen tests pin this behaviour, including the per-*J* saturation asymmetry, the
zero-width band disclosure, the ‡ mark, and a fake render-check that exits 0 while
reporting an 8.1px label — which the gate must now reject.

## Residual ⚠ — what is still wrong

1. **A third blind round has not been run.** The process says iterate until a blind
   pass produces no new findings. Round 2 produced four blocking findings; the fixes
   for them have not themselves been reviewed blind.
2. **Only 6 of 11 roles ran in round 2.** Roles 2, 5, 6, 7 and 9 have not seen the
   rebuilt artifact.
3. **Three methods findings cannot be fixed by rebuilding** (role 6, round 1). The
   joint-ISI histogram is binned at *J*/2, giving a 5-point lattice; Gerstein's square
   root is a provable no-op for JISI-D on this data, so half those grid cells are
   duplicates of the other half; and "Stella's setting" is wrong in 3 of its 4
   parameters. These are properties of the **run**, not the report. They are flagged on
   the pages; correcting them is a rerun.
4. **FOUNDATIONS §9 is satisfied for the flag rate only.** Retained coordination, the
   discriminator, cost and RMS movement were computed pooled and have no per-group
   counterpart in the run's output. The page now says so rather than implying coverage.
5. **Two vendored gate tools do less than they appear to.** `render_check.py` defines
   contrast helpers and never calls them, and its probe's selectors match nothing on
   these pages; `edge_collisions.py` reports "clean" while parsing zero edges and zero
   boxes. Neither was edited here (both are stamped vendored copies); the gate record
   states what each did not check.
6. **Figure craft findings from role 10's blind pass are not applied**: panels in
   Figures 4 and 5 are unlettered, Figure 5 has no colourbar, Figure 1 uses one glyph
   for two meanings, and annotations in Figure 4 cross reference lines. No gate leg
   detects text crossing a shape; a person has to look.
7. **The screenshots are viewport-only at 900 and 430 px** while the pages are
   10,600–51,400 px tall, so the narrow renders show only the top of each page.
8. **Three generators score a fraction of their ROIs and no page says so** (found
   2026-09-12, by the probe rather than by this review). On the fast stream every cell
   holds the same 2,630 ROIs, and `not_estimable_rois` is **0 for fifteen generators**
   but a median **1,676 for joint-ISI dither, 1,664 for ISI dither and 1,302 for
   operational-time dither** — so those three are scored on 803–1,328 ROIs while the rest
   are scored on all 2,630. That column is in `cells.csv` and on no page. Worse, the one
   quantity a reader would reach for reads the wrong way: per-statistic `coverage` is
   **1.000** for exactly those three and **0.505** for everything else, because the
   excluded ROIs leave the denominator with the numerator. Of joint-ISI's 1,676, 1,452 are
   ROIs with fewer than three onsets (`surrogates.JISI_MIN_ONSETS`) — a property of this
   corpus — and the rest were excluded by the method itself, chiefly
   `jisi_moved_nothing`. Two consequences, both for the verdict rule: the joint-ISI family
   is not merely expensive on this data but largely inapplicable to it, which bears
   directly on whether its dropped cells are worth rerunning; and any rule that reads
   `coverage` as completeness will prefer whichever generator discarded the most data. The
   docstring that claimed the drop "is reported as coverage" is corrected; surfacing
   `not_estimable_rois` on the page, and adding a scored-share column that keeps the full
   ROI population in its denominator, are not done.

## Reproduction

```bash
bash tools/murderboard_roster.sh check docs/reviews/report_steps_excluded_2026-09-11.md
python3 tools/murderboard_agents.py --process docs/doc_review_process.md \
        verify docs/reviews/report_steps_excluded_2026-09-11.md
"$VENV/python" -m pytest tests/test_build_surrogate_report.py -q
"$VENV/python" tools/build_surrogate_report.py     # rebuilds and re-runs the render gate
```
