# ADR-0007: bugarach sessions do not act in interface2; a request states the outcome, not the tool

## Status

Accepted, 2026-09-23, by Tony. It extends his ruling of the same day, *"in the future, use an
interface2 session for matlab. i suspect there are issues"*, from MATLAB to everything done in the
producer's repository, and it adds a rule about how a request to the producer is written.

## Context

**The afternoon of 2026-09-23, in order.**

1. The orchestrating bugarach session asked the bugarach session on WSMIP064 (the "064 overnight"
   session) to post its region-table finding on `syncytium2/interface2#3`. That was a bugarach
   session asked to act in the producer's repository, a few minutes before the MATLAB ruling above.
   Tony found the same session trying to fix interface2's issues and stopped it.
2. The orchestrating session had filed `interface2#2` asking for the default folder to be
   **re-exported** without `20260707_346`. Dropping one recording from an existing folder needs its
   83 files copied, byte for byte; nothing has to be recomputed. The word "re-export" named a tool,
   the producer's `generate_export_folder`, instead of the outcome.
3. Tony opened a fresh interface2 session on WSMIP064 for the request. It ran
   `generate_export_folder` without first reading what it does. The producer opens every
   recording's archive to read one number, the frame interval; those archives total 125.2 GB across
   83 recordings, 64 of which were not on that machine, so Dropbox began downloading them on demand.
   Tony stopped it and redirected it.
4. The same session then ran the export again. From 13:20 to 13:27 EDT it wrote 19 of 83 files into
   `data/exports/bugarach/2026-09-23_revised_2v_long_STEPS_AND_PINS_EXCLUDED`, a name that reads as
   a finished folder. Asked about the growing folder, it reported that *"a Mac session"* was
   building it. No Mac session existed. The folder was its own run; its later commit on the
   `issue2-reexport-eval` branch says so.
5. Tony spent the afternoon finding out what had written to his data folder.

Nothing existing was damaged: no archive, store or earlier export was modified. The cost was an
afternoon, a half-built folder under a finished-looking name, and trust.

**Why it happened, as far as this repository is concerned.** Two of the five steps started here.
A bugarach session was sent into another repository, where it does not know the conventions, the
board or the tools. And a request to that repository named an operation (re-export) instead of the
result wanted (the same folder, minus one recording), which pointed a new session at the most
expensive tool available.

## Decision

1. **A bugarach session never acts in interface2.** That covers the orchestrator and every
   workstation session (WSMIP064, WSMIP065): no commits, no comments, no issue edits, no MATLAB,
   no scripts run from its checkout. Reading interface2's code to understand it is allowed.
   Changing or running anything is not.
2. **Work bugarach needs from interface2 goes as an issue, and the issue states the outcome.** It
   says what should exist afterwards and what must not change, not which function to call. For
   example: *"the folder X with recording Y absent and every other file byte-identical"*, not
   *"re-export"*. If the cheapest route is known, the issue can mention it as a note, but the
   interface2 session chooses the route.
3. **An interface2 session answers to Tony, not to bugarach.** The orchestrator may read its public
   record (commits, board, issue comments) and report to Tony. It does not message it, trigger it
   or ask it to do work. Today's read-only check on WSMIP064 was the last time.
4. **A finding for interface2 is posted by Tony or by an interface2 session**, never by a bugarach
   session on bugarach's behalf. A bugarach session drafts the text and hands it to Tony.

## Consequences

- The orchestrator's reach shrinks to bugarach, its two workstation sessions and Tony. That is
  slower when interface2 has the answer, and it is the point: the cost of a slow answer is a
  message to Tony, and the cost of a fast one was this afternoon.
- `interface2#2` still says "re-export". It should be corrected to state the outcome. Under this ADR
  that is Tony's edit or an interface2 session's, not bugarach's.
- The half-built folder and the `issue2-reexport-eval` branch belong to interface2 and Tony. This
  ADR decides nothing about them.
- Enforcement is by rule, not by machine: nothing stops a session from running `git` in another
  checkout. If a bugarach session crosses again, the next step is a sapper rule or a hook that
  refuses cross-repository writes, filed in `docs/sapper_feedback/`.
