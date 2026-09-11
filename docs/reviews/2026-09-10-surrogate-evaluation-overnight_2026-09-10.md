# Murderboard run — the overnight surrogate-screen plan

Mode: standard

> **Stopped at round 2 and escalated, as the process requires; delivered unconverged.** Blocking
> findings went 20 → 19 across two rounds. Those on the screen's mechanism roughly halved, but every
> round found new holes in the same place — the rule that turns measurements into a shortlist — and
> that rule needs numbers nobody had. Tony chose the narrower night: **measure every candidate
> tonight, shortlist nothing, design the verdict rule tomorrow from the measurements.** The plan was
> rewritten to that scope and approved for launch; the review itself ran past the night's deadline, so the run is staged.

## What was at stake

A surrogate is a resampled copy of a recording that keeps each ROI's own timing and destroys the
timing between ROIs; a self-supervised detector learns coordination by telling real from surrogate.
The day's earlier review had killed one surrogate for **leaking** — being distinguishable without any
cross-ROI information. The plan under review was to screen every replacement overnight and let the
screen's report pick a shortlist.

The first draft's screen measured only whether a candidate **kept** what real data has. It never
asked whether a candidate **destroyed** coordination. So a surrogate that changed nothing would have
passed every statistic, and a shortlist built on "did not leak" would have ranked highest whichever
candidate moved onsets least — the same shape as the defect the earlier review found, a check that
cannot fail, one level up.

## What was found

**Round 1: 20 blocking, 89 major, 93 minor.** By kind:

- **The mechanism.** No destruction test and no do-nothing control. The uniform-dither control
  genuinely cannot fire at the grid's smallest jitter radii. The verdict and shortlist rules were
  undefined — an agent would have written them overnight, after seeing the numbers. The counting
  statistics could not see serial-order or drift leaks. The discriminator the draft named, `tiny`,
  sums per-ROI votes frame by frame — a coactivity trace, the one thing a sound surrogate removes.
- **A library that fails silently at our timescale.** Two roles installed Elephant in a scratch
  environment and ran it: joint-ISI dither returns sparse trains unchanged and falls back silently to
  uniform dither; dead-time dither caps the dead time at each train's own minimum; interval jitter
  crashes or misplaces onsets in any window not starting at zero; nothing takes a seed.
- **The data.** About half the ROIs in a baseline have fewer than two onsets. Real onsets sit exactly
  on the 0.1-second frame grid, so continuous surrogates leak off-grid intervals of their own. The
  earlier review's "real data scores 0%" is by construction. Splits by recording leak animal identity.
- **Operations.** A stop handoff would have overwritten another thread's; the render gate would have
  written screenshots of real data into another repository's git tree; one agent would have written
  both the pattern-jitter spec and its implementation.
- **Words, and the canonical documents.** "Corpus", a retired term; τ already taken in the glossary;
  "leak" never defined. FOUNDATIONS §9's rate range does not reproduce, and GLOSSARY and FOUNDATIONS
  disagree about what it is a quartile of — filed as its own todo.

Round 1 was applied as a **rewrite**: a destruction test with a do-nothing control, a known-bad
control per statistic, a verdict rule fixed before the run, mouse-grouped splits, frame-grid
quantization, explicit handling of every Elephant failure, and the problem and Tony's decisions first.

**Round 2, blind: 19 blocking, 78 major, 112 minor.** Thirteen of the blocking were the cold reader's
term-order rows. The six on the mechanism were all in the verdict rule:

- **The control gate could not fail**: the powered region was *defined* as wherever the control fires.
- **A cell where no statistic had power passed the shortlist**, so the known-bad control could be
  shortlisted.
- **The yardstick was the wrong null**: an unpaired between-mouse band, against paired
  real-to-surrogate differences. Measured on real data, a full interval shuffle stays inside the band
  in three of the four groups.
- **The destruction test cited a generator that does not exist**, and the edge-band control could not
  move the edge-band statistic.

Round 2 also found more of Elephant (trial shifting duplicates onsets on pseudo-trial boundaries;
window shuffling misplaces on-grid onsets in floating point; joint-ISI's smoothing width, not *J*,
decides whether it moves anything), that the encoder truncates frame positions, and that Gerstein's
joint-ISI recipe takes a square root Elephant's default and Stella's own runs both skip.

## The decision the escalation produced

The process says a flat blocking count after two rounds means a structural problem patching will not
retire. Here the structure was the verdict rule, and its open questions are empirical. So the
rewritten plan **measures the three candidate yardsticks side by side** — the mouse-split band, a
paired surrogate histogram, and an exchangeable negative's flag rate — and leaves the choice among
them, and the shortlist, to a design session with the numbers. Every round-2 finding about *how to
measure* is applied; the findings about *how to decide* become that session's agenda.

## What generalises

- **A screen that only tests preservation rewards inaction.** Any surrogate screen needs a test that
  the surrogate removes what it is meant to remove, and a do-nothing control that must fail it.
- **Every statistic needs its own known-bad control, named in advance** — and a gate defined as
  "wherever the control fires" is not a gate.
- **Compare like with like.** A paired leak is invisible against an unpaired between-subject band.
- **Run a library before planning around it.** The roles that read Elephant confirmed its method list;
  the roles that ran it found the failures — in both rounds.
- **When review keeps finding holes in one rule, the rule may need data, not wording.**

This review found and fixed many defects. **It is not a correctness proof.** The convergence table
measures how quickly reviewers stopped finding things, not whether anything remains — and this run did
not converge.

---

## Appendix — run header, convergence, role ledger

- upstream:  syncytium2/murderboard @ 81a0927
- copy:      vendored @ 81a0927
- freshness: current
- artifact:  docs/proposals/2026-09-10-surrogate-evaluation-overnight.md (50d04b07df79 -> ab65c2926eaf -> e4049bfdd84c)
- roles:     11 of 11 run (role agents on fallback grants in both rounds — the seven Bash-holding roles arrived without Grep and Glob)
- rounds:    2 blind rounds; stopped by escalation, unconverged

**Convergence, by severity per round.**

| round | blocking | major | minor | applied as |
|---|---|---|---|---|
| 1 (first draft) | 20 | 89 | 93 | rewrite |
| 2 (blind) | 19 | 78 | 112 | escalated; rewritten to the measurement scope Tony chose |

**Stopping reason:** blocking count flat across two rounds (20 → 19), concentrated in one rule; escalated
to the human, who narrowed the deliverable. Not a severity floor, not the round cap.

**Role ledger.** GRANT lines are quoted as each reviewer wrote them. Findings as blocking / major / minor.

| role | round 1 grant | round 1 | round 2 grant | round 2 | what it carried |
|---|---|---|---|---|---|
| 1 Prove It | GRANT 1 MISMATCH — missing Grep, Glob; holds no forbidden tools (held: Read, Bash) | 0 / 8 / 14 | GRANT 1 MISMATCH — missing Grep, Glob; holds none of the forbidden tools (holds Read, Bash) | 0 / 6 / 12 | ran Elephant both rounds; measured floors, counts, fold structure; trial shifting's boundary duplication; the render gate refuses nothing without SVG |
| 2 DOI or Die | GRANT 2 MISMATCH — missing Grep, Glob; holds none | 1 / 7 / 10 | GRANT 2 MISMATCH — missing Grep, Glob; holds no forbidden tools (held: Read, Bash, WebSearch, WebFetch) | 0 / 5 / 8 | origins (Gerstein, Date, Pipa, Harrison & Geman); circular shift is standard, not ours; Gerstein's square root; Grün's group's prior work on choosing surrogates |
| 3 Cross-Examiner | GRANT 3 ok — Read, Grep, Glob | 0 / 14 / 15 | GRANT 3 ok — Read, Grep, Glob | 0 / 10 / 16 | counts (controls counted twice); the floor on three populations; two meanings of "analysis window"; the contaminated-recordings view is a consumer filter |
| 4 Reviewer 2 | GRANT 4 MISMATCH — missing Grep, Glob; holds no forbidden tools (held: Read, Bash) | 5 / 12 / 4 | GRANT 4 MISMATCH — missing Grep, Glob; holds Read, Bash | 4 / 9 / 4 | round 1: no destruction test; round 2: the verdict rule's four holes, measured on real data |
| 5 Kill Your Darlings | GRANT 5 ok — Read, Grep, Glob | 0 / 10 / 19 | GRANT 5 ok — Read, Grep, Glob | 0 / 8 / 30 | the decision's action unnamed; British spellings; the destruction band undefined. ⚠ `murderboard_prose.sh` exists in neither tree, so both counts were by hand |
| 6 RTFM | GRANT 6 MISMATCH — missing Grep, Glob; holds no forbidden tools (held: Read, Bash, WebSearch, WebFetch) | 3 / 13 / 4 | GRANT 6 MISMATCH — missing Grep, Glob; holds no forbidden tools (held: Read, Bash, WebSearch, WebFetch) | 2 / 10 / 5 | ran Elephant; the paired surrogate histogram as the right null; joint-ISI's smoothing width; the edge-band control that cannot move its statistic |
| 7 Reinventing the Wheel | GRANT 7 MISMATCH — missing Grep, Glob; holds no forbidden tools (held: Read, Bash) | 1 / 6 / 6 | GRANT 7 MISMATCH — missing Grep, Glob; holds none (I have Read and Bash only; no editing tool) | 0 / 7 / 2 | the encoder's truncation; the shipped dither's production 20 s; five copies of the baseline-window rule; seeding under SAP002 |
| 8 You Lost Me | GRANT 8 ok — Read, Grep, Glob | 9 / 13 / 5 | GRANT 8 ok — Read, Grep, Glob | 13 / 12 / 13 | "leak" undefined; then thirty terms used before the Terms table; group codes and senktide never expanded |
| 9 Show, Don't Tell | GRANT 9 MISMATCH — missing Grep, Glob; holds none | 1 / 4 / 8 | GRANT 9 MISMATCH: missing Grep, Glob; holds no forbidden tools (I have Read and Bash only) | 0 / 6 / 10 | no figure at all; then ten figure-free sections. The synthetic per-ROI figures move to the report |
| 10 Ship It | GRANT 10 MISMATCH — missing Grep, Glob; holds none of the forbidden tools (I have Read and Bash only) | 0 / 0 / 4 | GRANT 10 MISMATCH — missing Grep, Glob; holds no forbidden tools (Read, Bash only) | 0 / 1 / 6 | rendered through GitHub's API, pandoc, python-markdown and mermaid-cli; Mermaid labels wrapping mid-phrase |
| 11 Start With the Problem | GRANT 11 ok — Read, Grep, Glob | 0 / 2 / 4 | GRANT 11 ok — Read, Grep, Glob | 0 / 4 / 6 | round 1: opened on its solution; round 2: decision rows leaning on later sections |

**The grant mismatches are one pattern, not seven accidents.** In both rounds every role granted
`Bash` arrived without `Grep` and `Glob`, and every role granted only `Read`, `Grep` and `Glob` arrived
as granted — a property of this harness, which routes searching through the shell when a shell is
held. No role held an editing tool, and each searched with `grep` through Bash.

**Findings about the run itself.**

- The render command in the round-2 brief (`gh api … -f text=@file`) sends the literal path, not the
  file; GitHub returns an empty page with exit code 0. The build reviewer caught it and used `--input`.
- One reviewer, checking the claimed workflow-size setting, read `~/.claude.json` (read-only; the
  setting was not there). Relayed to Tony.
- The repo's heredoc hook blocked reviewers from writing scratch scripts; they ran probes as
  `python -c` instead. Nothing was written inside the repo.

**Adjudication.** Round 1: every blocking and major finding fixed in the rewrite. Round 2: every
finding about how to measure is applied in the measurement-scope rewrite; the verdict-rule findings —
gates, shortlist, yardsticks, family-wise control, negative controls — are carried as the design
session's agenda, not fixed. No change, with reason: the drawn per-ROI figures (moved to the report,
where they are cheap once the generators exist); the five drifted copies of the baseline-window rule
beyond the one factored out (left for their own change); Perkel 1967 as an earlier root for the rigid
shift (unverified); the SpiSeMe library (out of scope). Residual ⚠, carried in the plan: the
FOUNDATIONS rate range; the inherited 60-second window; the saturation table's lost conditions;
joint-ISI intractability and operational-time degeneracy; no tool catches text crossing a shape; the
circular shift's root and the physics surrogate literature unsearched; nobody has asked Grün's group or
the Cossart lab.
