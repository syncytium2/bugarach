---
status: open
filed: 2026-10-23
---

# Handoff: finish the reply to the reviewer of the plain detector document

**This is a handoff to a new session** (Tony, 2026-10-23: *"write a handoff for a separate session
to handle the detector explainer edits"*). It is filed as a todo, not a root `HANDOFF-*.md`, because
nothing is half-done: a draft exists and is waiting on edits.

Goal page: [`detector-review-document.md`](../goals/detector-review-document.md). Read it first,
including the 2026-10-20 and 2026-10-22 blocks under *Where it stands*.

## The task

A lab reviewer returned the plain-language detector document (*"Finding neurons that act
together"*, built 2026-09-17) as a Word file with tracked edits and **98 comments**, dated 18 to 22
September 2026. A session on 2026-10-20 drafted replies. Since then Tony has ruled on most of the
open questions. **Your job is to bring the draft in line with those rulings, so Tony can review it
and send it back.**

You do not send anything to the reviewer, and you do not run the murderboard. **The murderboard runs
on Tony's command only** (2026-10-22).

## Where everything is

| what | where |
|---|---|
| The reviewer's copy, read-only | `<darkroom>/bugarach/detector_review_plain-22Sep2026.docx` |
| The draft reply: her edits accepted, ours tracked under the author "Claude (draft for Tony)", a reply threaded under every comment | `<darkroom>/bugarach/2026-10-20-detector-review-response/explainer_detector-review-reply-draft_20261020.docx` |
| The ledger: every comment beside its reply, sorted into *Tony decides*, *figure rebuild*, *text changed* and *answer only* | same folder, `explainer_detector-review-reply-ledger_20261020.html` |
| The document's builder, template and figure tools | branch `detector-review-doc`, [PR #587](https://github.com/syncytium2/bugarach/pull/587), **not on `main`** |
| The built pages | `<darkroom>/bugarach/archive/2026-09/2026-09-15-detector-review-plain/` |

Resolve `<darkroom>` with `python -m bugarach.paths`. Use the `anthropic-skills:docx` skill to edit the
Word file, so tracked changes and comment threads survive.

## Rules that bind this work

- **The comments are private correspondence and this repository is public.** No comment text, no
  quotation from her, and no real-recording figure goes into the tree. Work in the darkroom; the repo
  gets only status lines on the goal page. Real-recording figures are darkroom-only under FOUNDATIONS
  §5, and the builder keeps their prose in `real_prose.json`, outside the tree.
- **The document is a record of September 2026, and it does not rank the detectors** (Tony,
  2026-10-20). Take out "best", "highest", "performed better" and the like. Describe a later change as
  "since then", never as a correction.
- **Take over the darkroom claim.** `docs/SESSIONS.md` holds
  `bugarach/2026-10-20-detector-review-response/` under `WSMIP065/sue-review-response`, a session that
  has ended (its worktree was reaped). Rewrite that block as yours before you write in the folder. New
  versions take a new date in the name; do not overwrite the 20 October draft.
- **File names** follow the estate scheme. Build and check them with `artifact_name.py`. On WSMIP065 it
  lives at `~/.claude/armory-naming/tools/naming/`, and a hook checks every write to the darkroom.

## What changed since the draft, and what each change means for it

| ruling | date | what to change in the draft |
|---|---|---|
| **The deep learning models are on hold.** Chorus is one of them | 2026-10-22 | The reviewer's edits put CoactDetect and chorus in the main text, with the other five in an appendix. Chorus does not get the planned main-text figure and paragraph. Reply that the learned models are on hold, and that CoactDetect stands alone in the main text for now. Which version of chorus to show is moot until the hold lifts |
| **The decoys are retired** (ADR-0019, `docs/adr/0019-the-decoys-are-retired-negatives-are-rate-matched.md`) | 2026-10-23 | She could not see how an algorithm could tell a decoy, and she was right. Rewrite the decoy section to say so, and say that decoys were dropped since then and that negatives are now rate-matched and carry no coordination. Scores from September stay as they were, as a record. ⚠ ADR-0019 is on [PR #902](https://github.com/syncytium2/bugarach/pull/902), not yet merged; read it there if `main` lacks it |
| **Which events go in the combined list** | 2026-10-23 | The draft presents the 2 s rule as our method. It is not ours. The exporter (interface2) assigns events to fast and slow, and the 2 s rule is our working assumption about how it does that, not yet confirmed by the producer ([`combined-stream-coordination.md`](../goals/combined-stream-coordination.md)). bugarach builds combined as every fast and every slow event together, labelled, with nothing dropped (`bugarach.combined.combine`). Say that |
| **Hand-marked events: the rater sheet** | 2026-10-23 | The ledger asks whether to have her, or someone in the lab, mark stripes by hand. Tony has since had a sheet built for exactly that, `tools/rater_sheet/` ([PR #903](https://github.com/syncytium2/bugarach/pull/903)). A reply can invite her to take it once real rows are released. Ask Tony before promising anything |
| **The floor** (ADR-0008) | 2026-09-24 | Already in the draft: each window's minimum is the larger of 3 neurons and the count chance reaches at most once an hour. Check that the draft also says the floor's redesign (ADR-0012/0013, PR #856) is still open |

## Still Tony's to decide; ask, do not settle

1. **C333.** She asked whether "fewer than 1% of copies reach 4" means a >99% chance the event is
   real, and Tony's reply on 22 September was "exactly". It doesn't mean that: chance alone would give
   that count less than once in 100 tries. The draft corrects this gently. Tony edits the wording.
2. **C374/375.** Tony said "shuffled" should be "shifted". The draft keeps "shuffled" for Cossart,
   Aronov and Yuste (2003), who did reorder each neuron's gaps, and says binned SCE (the
   synchronous-calcium-event detector) uses shifts. Confirm with him.
3. **Structure:** move the shifted-copy explanation (Section 5) ahead of Figure 6, which uses it
   (C320).
4. **The 12 figure fixes** listed under *figure rebuild* in the ledger. They need the builder, so they
   wait for #587 (below).

## The builder, and merging PR #587

Tony asked on 2026-10-22 for #587 to be merged, then paused it while decoys were searched. That search
is closed (ADR-0019), so the merge can resume. **Confirm with Tony before you start.** The branch is
about 690 commits behind `main`. A trial merge on 2026-10-22 conflicted in five files:

- `HANDOFF-detector-review.md`
- `docs/GLOSSARY.md`
- `docs/SESSIONS.md`
- `docs/todo/2026-09-17-detector-windowing-does-not-match-intent.md`
- `tools/sapper.py`

It was aborted, and the branch is unchanged (`3379a823`). Merge `main` into `detector-review-doc` in its
worktree (`bugarach-worktrees/detector-review-doc`). Resolve the conflicts, run the suite, and push. Then
ask Tony to merge the PR: `tools/merge_when_green.sh` is the house tool, but this session's
permissions did not allow it to merge, and that is Tony's call.

The document's numbers predate three merges (locust's per-event widths, binned SCE's scoring, and the
retune of all six operating points). Under the September-record rule, the numbers do not change in this
reply. Regenerating the figures for the 12 fixes changes their numbers unless the builder pins the
September inputs. **Ask Tony which he wants before rebuilding.**

## Done means

- A new dated draft in the claimed darkroom folder, with every *text changed* and *answer only* reply
  checked against the rulings above, and an updated ledger showing what changed since 20 October.
- The four items under *Still Tony's to decide* put to Tony, with his answers applied.
- The goal page updated in a PR: a dated line under *Where it stands*, and *Waiting on Tony* trimmed to
  what is left.
- Not done here: the figure rebuild, unless #587 has landed and Tony has said how to pin the numbers;
  the murderboard; sending anything to the reviewer.
