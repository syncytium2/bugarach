# Handoff: revise Chapter 1 for readability

**Use this page when** you are the session asked to make Chapter 1 of the dissertation exercise
easier to read, or you want to know what that revision may and may not change.

> Working material, not murderboarded. Written 2026-11-13 by a session that did not write the
> chapter and has not revised it. It is a brief for work that has **not started**, so it sits
> here and not at the repository root. **A linked file wins** where this page and it disagree.

## The task, in Tony's words

2026-11-13: *"revise chapter 1 for readability."* He gave no list of passages. **Ask him first
which parts lost him**, in one short question, and start on the diagnosis below while you wait.
What follows about where the trouble lies is this session's reading, not his.

## Where the chapter is

- The text: [`docs/dissertation/chapter-1-aim0.md`](../dissertation/chapter-1-aim0.md), about
  16,600 words in 1,240 lines, sections 1.1 to 1.9, 16 figures, 8 tables.
- Branch `synth/dissertation-chapter-aim0`, draft PR #919, **not on `main`**. This worktree is
  `dissertation-ch1`. Merging is Tony's; he has not approved it.
- It is an exercise with no committee: Tony set it up to test how far he and Claude can take a
  piece of research together (the chapter's own *About this chapter*).
- Figures the chapter draws itself: [`docs/dissertation/figures/`](../dissertation/figures/README.md),
  built by `ch1_new_figures.py`. Six more figures are linked from
  `docs/learned/synthetic_validation/`.
- Review history: three murderboard rounds on 2026-10-29, run record
  [`docs/reviews/chapter-1-aim0-2026-10-29.md`](../reviews/chapter-1-aim0-2026-10-29.md), role
  reports in the three `chapter-1-aim0-2026-10-29-round*-roles/` folders beside it.

## What a reader gets today

A Word copy is in the Dropbox darkroom, under `bugarach/dissertation/chapter-1/`, made on
2026-11-13 from the branch as it stands. **Nobody has opened it in Word**: figure sizes and table
widths are unchecked, and its links to repository files are relative paths that do not open.

## Diagnosis to start from (unverified against the current text)

The round-3 naive-reader report,
[`round3-roles/08-you-lost-me.md`](../reviews/chapter-1-aim0-2026-10-29-round3-roles/08-you-lost-me.md),
has a per-section table of terms used before they are defined. It marked three places as
blocking: *The question, and the answer* (five undefined terms in two sentences), *Contributions*
(eight, with "run-start factor" defined nowhere) and the rederivation paragraph of 1.3. The last
commit on the branch (`fd1ace2d`) was a follow-up pass after that round. **This session did not
check which of those findings that pass fixed.** Check each against the text before treating it
as open.

This session's own guesses, to test and not to assume:

- The introduction states results before the reader has the vocabulary for them.
- Length: 1.4 alone runs 330 lines, and 1.7.2 another 125.
- Symbols collide or arrive unglossed (the round-3 report names `g` against `g_n`, and `F_M`,
  `F₀`, `ISI` in a legend and a table).

## What the revision may not change

- **No number, claim or scope moves.** Every simulation number is printed by a script listed
  under the chapter's *Reproducing this chapter*. A readability pass that changes a value has
  introduced an error. If a sentence cannot be made clear without changing what it claims, stop
  and take that to Tony as a finding.
- **References keep their ⚠ marks** unless you open the source yourself. For a paywalled paper,
  resolve the DOI and give it to Tony; do not fetch it.
- House rules in [`docs/writing_conventions.md`](../writing_conventions.md) and `CLAUDE.md`:
  "data" are plural, calcium events do not "fire", every number carries its unit, every figure is
  numbered and referred to by number and name, every abbreviation and symbol is defined at first
  use, groups are ordered DI, OVX, MALE, ORX.
- A figure that needs changing is rebuilt by its script, not edited as an image.

## One thing to raise with Tony, not to settle

On 2026-11-13 Tony sketched the later chapters: Chapter 2 builds synthetic sets from the measured
parameters and works out how detectors are tuned and compared on them, Chapter 3 applies that to
real baseline data, Chapter 4 handles treatments that may alter coordination. The brief is
`docs/handoffs/2026-11-13-chapter-2-synthetic-sets-and-detector-scoring.md` on branch
`synth/per-group-benches` (PR #929), not on this branch. Chapter 1's *Two sources* (1.8.3) and
*Next steps* (1.8.5) were written before that outline. Whether they should now point at it is a
change of content, so ask.

## How to deliver

1. **Review before handing over.** `CLAUDE.md` requires `/murderboard` for a document
   deliverable. Do not edit the chapter while reviewers are running. For a readability pass the
   roles that matter most are 8 (naive reader), 5, 9 and 11, but every role runs.
2. **Word, to Dropbox.** Tony's rule of 2026-11-13: dissertation chapters for people are
   `.docx`, in `<darkroom>/bugarach/dissertation/chapter-1/`. Name the file with armory's
   `tools/naming/artifact_name.py build --type explainer --topic "dissertation chapter 1 ..."
   --ext docx`; a hook on darkroom writes rejects other names. Use `v2` if the name is taken
   that day.
3. **Converting.** The workstation has no pandoc and the shared virtual environment has no pip.
   What worked: `uv pip install --python <venv python> --target <scratch folder> pypandoc-binary`,
   then run the bundled `pandoc.exe chapter-1-aim0.md -f gfm -t docx --resource-path=.` from
   `docs/dissertation/`, so the figure links resolve and embed. Open the result and check the
   figures and tables before giving Tony the path.
4. **Commit and push** to this branch, with the review record. Update the goal page
   ([`docs/goals/synthetic-validation.md`](../goals/synthetic-validation.md)) only if what is
   settled changes, which a readability pass should not do.

## Small things

- `uv.lock` is untracked in this worktree. It is not part of this work; leave it.
- The local board (`../SESSIONS.md` beside the worktrees) has a block for this worktree from
  2026-10-29. Claim your own before the first edit.
