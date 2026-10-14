# ADR-0018: The dataset an analysis reads is reported, not confirmed per session

## Status

Accepted, 2026-10-14, by Tony: *"it is probably time to simply report the data set you are
using. we were scared the stale dataset would sneak in unnoticed. i think we are past that
now."* Backfills the 2026-09-21 rule it changes, which never had a record of its own, and
supersedes that rule's confirmation half.

## Context

**On 2026-09-21 the repository went to one default dataset.** Tony: *"there should be one
default data folder that the user confirms at the start of every session."* The top-level
`default` in `current_export.toml` became the one line that names the input, and
`dataset.default()` the one call that reads it. Other folders were declared `eval` (read by
name on purpose) or `archive` (refused unless `BUGARACH_REPRODUCE` names the run). Behind it
was a stale folder being read without anyone noticing, and analyses scored on different
exports turning up side by side.

**The confirmation was the second half.** Inside a Claude session, `dataset.default()`
refused until `python -m bugarach.dataset confirm` had recorded the person's yes for that
session, and a session was told never to run it for them. That made every session's first
analysis wait on Tony. On 2026-10-14 it also failed in the way such a gate can: the
confirmation Tony typed ran a Python without bugarach installed, recorded nothing, and the
gate held a run he had already agreed to.

**The danger the gate guarded against is now held by mechanisms that do not need a person.**
One pointer names the default. Archive folders are refused, and so is any folder with a
declared contamination. Every result records `dataset.stamp()`, and
`tools/check_scored_dataset.py` flags at startup any result scored on anything else.

## Decision

1. **The per-session confirmation is retired.** `confirm`, `confirmed`, `require_confirmed`
   and `UnconfirmedDefault` are removed from `bugarach.dataset`.
   `python -m bugarach.dataset confirm` prints that it is retired, rather than failing for
   someone typing it from habit.
2. **Every analysis names the folder it reads.** `dataset.report` prints one line on stderr,
   once per folder per process, with the folder, its role and what is in it. It fires for
   every declared folder opened through `current()`, and for one reached by name or path.
3. **Anything reported to Tony names the dataset it was run on.** The briefing prints the
   default without asking for anything.
4. **Unchanged:** one default named in one line, the archive refusal, the contamination stop,
   `stamp()` in every result, and the startup check on scored results.

## Consequences

- A session can run an analysis on the default without waiting, and the folder is in the
  run's log and in what the session tells Tony.
- If a stale folder becomes the default by mistake, nothing stops the run. It is caught by
  the line naming the folder, by the stamp, and by the startup check. That is the trade Tony
  made.
- Old folders can move out of the way. Tony asked in the same message for the stale exports
  to go to a deprecated folder. That is a move of shared data and is done separately, against
  a list he approves.
