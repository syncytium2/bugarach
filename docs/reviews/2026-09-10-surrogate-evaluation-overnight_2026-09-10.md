# Murderboard run — the overnight surrogate-screen plan

Mode: standard

> **Round 1 rewrote the plan; round 2 (blind) is recorded below.** Tony asked for a plan for an
> overnight run — build a surrogate-evaluation tool, run it on our data, report — murderboarded
> before he reviewed it. The first draft would have launched a screen that could not do its job.

## What was at stake

A surrogate is a resampled copy of a recording that keeps each ROI's own timing and destroys the
timing between ROIs; a self-supervised detector learns coordination by telling real from surrogate.
The day's earlier review had killed one surrogate for **leaking** — being distinguishable without any
cross-ROI information. The plan under review was to screen every replacement overnight and let the
screen's report pick a shortlist.

The first draft's screen measured only whether a candidate **kept** what real data has. It never
asked whether a candidate **destroyed** coordination. So a surrogate that changed nothing would have
passed every statistic, and a shortlist built on "did not leak" would have ranked highest whichever
candidate moved onsets least. That is the same shape as the defect the earlier review found — a check
that cannot fail — one level up: then it was a control that saturated, here it was a screen with no
test of the thing surrogates exist to do.

## What was found

Round 1: **20 blocking, 89 major, 93 minor** across eleven roles. By kind:

- **The mechanism.** No destruction test and no do-nothing control. The uniform-dither control
  genuinely cannot fire at the grid's smallest jitter radii, so the gate as written would have
  stopped the night or voided every verdict. The verdict rule and the shortlist rule were undefined —
  an agent would have written them overnight, after seeing the numbers. The counting statistics could
  not see serial-order or drift leaks, so the screen could not separate the candidates that exist to
  differ on exactly those. The discriminator the draft named, `tiny`, sums per-ROI votes frame by
  frame — a coactivity trace, the one thing a sound surrogate removes. *Found by Reviewer 2, RTFM,
  Prove It and Reinventing the Wheel, independently.*
- **A library that fails silently at our timescale.** Two roles installed Elephant in a scratch
  environment and ran it rather than reading it. Joint-ISI dither returns trains with fewer than
  three onsets unchanged, and falls back to plain uniform dither whenever its bins or truncation do
  not fit; dead-time dither caps the dead time at each train's own minimum interval and never drops
  onsets; interval jitter crashes or misplaces onsets in any window not starting at zero — every
  baseline; window shuffling drops edge onsets; nothing takes a seed. A reviewer reading only the
  documentation would have passed all of it.
- **The data.** About half the ROIs in a baseline have fewer than two onsets, so a within-ROI
  statistic reaches half the population at best. Real onsets sit exactly on the 0.1-second frame
  grid, so any continuous-time surrogate leaks off-grid intervals of its own. The earlier review's
  "real data scores 0%" is confirmed as by construction — its floor is the minimum of the same
  windows. Its leak table's 543 windows were reconstructed exactly; its saturation table's
  conditions were never recorded and cannot be. Splits by recording leak animal identity: 35 of the
  44 mice contribute more than one recording.
- **Operations.** Writing a stop handoff to the root `HANDOFF.md` would have overwritten another
  thread's. The render gate crashes when pointed outside its own repository and, by default, writes
  screenshots of the report into that repository's git tree — real-data images in a second public
  repo. It also measures only inline SVG, so a page of canvas figures passes with zero flags. One
  agent writing both the pattern-jitter spec and its implementation would have broken the clean-room
  rule.
- **Words.** "Corpus", a retired term, six times. τ already means SPIKE-synch's coincidence window in
  the glossary. "Leak", "floor", the tiers, the streams and the folder roles were all undefined, in a
  plan whose reader had asked that evening for every abbreviation to be defined.
- **The canonical documents.** FOUNDATIONS §9's interquartile per-ROI rate does not reproduce from
  any current folder, and GLOSSARY describes the same two numbers as a quartile across *recordings*
  where FOUNDATIONS calls it a quartile of the *per-ROI* rate. Filed as its own todo; FOUNDATIONS is
  not edited here.

Round 1 was applied as a **rewrite**, not a patch, because the blocking findings were structural:
the screen gained a destruction test with a do-nothing control, a known-bad control for every
statistic, a verdict rule fixed before the run, mouse-grouped splits, frame-grid quantization,
explicit handling of every Elephant failure, and the problem and Tony's decisions at the top.

## What generalises

- **A screen that only tests preservation rewards inaction.** Any surrogate screen needs a test that
  the surrogate removes what it is meant to remove, and a do-nothing control that must fail it.
- **Every statistic needs its own known-bad control**, or its silence is not evidence. One control
  gating the whole screen exercises one statistic.
- **Run a library before planning around it.** The roles that read Elephant confirmed its method
  list; the roles that ran it found the failures.
- **A number quoted from a canonical document is still a claim.** The FOUNDATIONS rate range survived
  into the plan because it was quoted from the source of truth.

## What would validate the corrected plan

The night's own gates, if Tony launches it: the controls flagged where the plan says they must be,
the do-nothing control failing destruction, the pattern-jitter differential fuzz agreeing, and the
reproduction written up either way.

This review found and fixed many defects. **It is not a correctness proof.** The convergence table
measures how quickly reviewers stopped finding things, not whether anything remains.

## Round 2 — blind

*(pending)*

---

## Appendix — run header, convergence, role ledger

- upstream:  syncytium2/murderboard @ 81a0927
- copy:      vendored @ 81a0927
- freshness: current
- artifact:  docs/proposals/2026-09-10-surrogate-evaluation-overnight.md (50d04b07df79 -> ab65c2926eaf -> pending)
- roles:     11 of 11 run (role agents on fallback grants — the seven Bash-holding roles arrived without Grep and Glob)
- rounds:    pending

**Convergence, by severity per round.**

| round | blocking | major | minor | applied as |
|---|---|---|---|---|
| 1 (first draft) | 20 | 89 | 93 | rewrite |
| 2 (blind) | pending | pending | pending | pending |

**Role ledger — round 1.** GRANT lines are quoted as each reviewer wrote them.

| role | grant declared | findings (B/M/m) | what it carried |
|---|---|---|---|
| 1 Prove It | GRANT 1 MISMATCH — missing Grep, Glob; holds no forbidden tools (held: Read, Bash) | 0 / 8 / 14 | ran Elephant; measured event counts, floors and fold structure; reconstructed the 543 windows; the render gate's crash and git-tree leak |
| 2 DOI or Die | GRANT 2 MISMATCH — missing Grep, Glob; holds none | 1 / 7 / 10 | origins: joint-ISI dither to Gerstein 2004, interval jitter to Date, Bienenstock & Geman 1998, uniform dither's defect to Gerstein 2004; trial shifting runnable on pseudo-trials; nobody has written to Grün's group |
| 3 Cross-Examiner | GRANT 3 ok — Read, Grep, Glob | 0 / 14 / 15 | retired "corpus"; three reports promised from two screens; clean-room violation; root handoff collision; τ's two meanings |
| 4 Reviewer 2 | GRANT 4 MISMATCH — missing Grep, Glob; holds no forbidden tools (held: Read, Bash) | 5 / 12 / 4 | no destruction test; control unfireable at small *J*; undefined verdict rule; serial and drift leaks invisible; per-dataset claim is a hypothesis |
| 5 Kill Your Darlings | GRANT 5 ok — Read, Grep, Glob | 0 / 10 / 19 | the decision buried at the end; "run record" ambiguity; edge column dashes. ⚠ `murderboard_prose.sh` exists in neither tree, so the count was by hand |
| 6 RTFM | GRANT 6 MISMATCH — missing Grep, Glob; holds no forbidden tools (held: Read, Bash, WebSearch, WebFetch) | 3 / 13 / 4 | ran Elephant; joint-ISI intractable at small *J*; pattern jitter's parameters; frame grid; two-sample-test design; no seeding |
| 7 Reinventing the Wheel | GRANT 7 MISMATCH — missing Grep, Glob; holds no forbidden tools (held: Read, Bash) | 1 / 6 / 6 | the reproduction target's code is in no tree; the shipped dither omitted; baseline-window rule already exists; render gate passes canvas pages |
| 8 You Lost Me | GRANT 8 ok — Read, Grep, Glob | 9 / 13 / 5 | "leak" never defined; eight sections blocking on undefined terms |
| 9 Show, Don't Tell | GRANT 9 MISMATCH — missing Grep, Glob; holds none | 1 / 4 / 8 | no figure at all in a plan that demands numbered figures of its report |
| 10 Ship It | GRANT 10 MISMATCH — missing Grep, Glob; holds none of the forbidden tools (I have Read and Bash only) | 0 / 0 / 4 | rendered via GitHub's API, pandoc and python-markdown; links, symbols, sapper, quotes clean; module paths short of `src/bugarach/` |
| 11 Start With the Problem | GRANT 11 ok — Read, Grep, Glob | 0 / 2 / 4 | opens on its solution; the problem appears only in Sources; decisions at the end |

**The grant mismatches are one pattern, not seven accidents.** Every role granted `Bash` arrived
without `Grep` and `Glob`; every role granted only `Read`, `Grep` and `Glob` arrived as granted. It
looks like a property of this harness, which routes searching through the shell when a shell is held.
No role held an editing tool, and each searched with `grep` through Bash, so no check was skipped.

**Adjudication, round 1.** Fixed: every blocking and major finding above, in the rewrite. No change,
with reason: the optional preserved-property check-matrix (the table already carries the content);
Perkel 1967 as a possible earlier root for the rigid shift (unverified, not cited); the SpiSeMe
library as a second surrogate source (out of scope tonight); `tools/md_to_page.py` as a report-shape
template (the report builder will choose). Residual ⚠, carried in the plan: the FOUNDATIONS rate
range; the inherited 60-second window; the saturation table's lost conditions; joint-ISI
intractability and operational-time degeneracy; the render gate's text-against-shape gap; nobody has
written to Grün's group.
