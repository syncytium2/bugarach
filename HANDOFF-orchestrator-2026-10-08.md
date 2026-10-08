# Orchestrator 2026-10-08: the work was paused at Tony's word, and this is everything that was in flight

Written by the cloud orchestrator, Claude session `session_01Tc9RVYzUcsN3PhBsVwfmUw` (seen from
the machines as "Orchestrator 20261008" or `user-de`). It covers 2026-10-07 evening to 2026-10-08
11:30 EDT. Times are Michigan local time (EDT).

**Why it stopped.** At 11:30 EDT Tony relayed his PI's instruction to stop. Every live session on
every machine was asked through the inbox to push its work, leave its own handoff, release its
claims, report one line here and stop (inbox id `cloud-orchestrator-01Tc9-shutdown-1`, live until
19:30 EDT). Replies that arrive after this file was written are not in it.

**This file stays at the root while anything below is open.** When the review below is done, move
it to `docs/handoffs/` (see the README there).

It builds on the two handoffs written on 2026-10-07:
[`docs/handoffs/2026-10-07-orchestrator-01Jfi-the-floor-needs-a-rethink.md`](docs/handoffs/2026-10-07-orchestrator-01Jfi-the-floor-needs-a-rethink.md)
(bugarach) and interface2's `docs/handoffs/ORCHESTRATOR_2026-10-05.md` (item 9, the missing
`t50rise`). Everything open in those is still open; nothing in their decision lists was decided
today.

## What was finished today

**Communication between sessions now works on all three machines.**

| | Mac | WSMIP064 | WSMIP065 |
|---|---|---|---|
| a machine session messages the cloud (Remote Control, `SendMessage`) | yes | yes | yes |
| the cloud messages a machine (armory `broadcast.py`, Dropbox inbox) | yes | yes | yes |
| output filename check (`name_on_write.py`) | yes | yes, PowerShell included | yes |
| interface2 pipeline map rebuilds (`uv run`) | yes | yes | yes |

- **Cloud to machine.** A cloud session writes one file into the
  darkroom's `claude-link/inbox/<epoch_ns>-<from>.json` (Dropbox; exact path in armory's OPEN.md) (`id`, `text`, `posted`,
  `expires` in epoch seconds, `from`). The machine's hook shows it on the next tool call, labelled
  as unverified. Design and the Mac measurements: armory PR #28,
  `docs/projects/worktrees-and-channels/OPEN.md`.
- **Machine to cloud.** `SendMessage` works only from a session that has Remote Control switched on.
  It is **per session, not per machine**: on 2026-10-08 three sessions could not reply until Tony
  turned it on.
- **The naming hook** reports a bad name after the file is written; it does not block the write.
  Tested with `Test_Figure.png` on all three machines, and through the PowerShell tool on 064.
- **Global settings are saved by Tony by hand.** The permission system refuses a session that edits
  its own `~/.claude/settings.json`, so each machine's diff was shown and he saved it.
- **The pipeline map.** interface2's `tools/build_pipeline_map.py` needed pyyaml, which neither
  workstation's default Python has. Tony ruled out a forced install into the uv Python (uv was
  chosen on 2026-09-16 so the workstations need no admin rights; see
  `docs/windows_workstation_setup.md`). The script now declares its dependency and runs with
  `uv run` (interface2 PR #9 asked for it; an interface2 session landed it on `main` at e2931e47).

## Waiting on Tony

1. **The pinning review, his first priority for the day, was not started.** The four senktide/TTX
   slices being redone with rigid motion correction (`20260629_309`, `20260629_312`,
   `20260630_316`, `20250926_235`) still have no ROIs on their rigid recordings. The one decision:
   re-pick the ROIs, or move the old masks by the measured shift. The shift is under 3.5 px for three
   slices and (5.2, 3.8) px for `_312`; figures in `darkroom/misc/apv_gz_rigid_roi_overlays/`,
   routine in interface2 PR #7. State: interface2 `docs/SESSIONS.md`, block `064/pinning-review`.
2. **The bench revision, his second priority: plant short intervals.** Not started. It belongs with
   ADR-0013 (PR #855, Proposed), which puts treatment periods into the bench; the 01Jfi handoff found
   that the 2 s window plus the 3 s merge gap joins coordinated events less than about 5 s apart.
3. **interface2 PR #10**, the 064 pipeline-map result on the board. The 064 session could not merge
   it without review.
4. **Two commits that exist on one disk only.** WSMIP065's primary armory checkout
   (the older `armory` clone under the user's home folder) holds `d51e1aa` and `28c90d9` (2026-09-22, statusline work) on
   no remote branch, 10 commits behind `origin/main`. Pushing them to a branch adds a copy and changes
   nothing; it was offered and not yet approved.
5. **The default dataset** was not confirmed this session (Tony: "we'll decide when we need it").
   Nothing here read data.

## Found today, not fixed

- **interface2's startup briefing really does time out on WSMIP065.** Its "sapper watch" section was
  killed at 39 s of a 45 s deadline, so the session started in SAFE MODE with no guards. interface2's
  to fix.
- **A false SAFE MODE in bugarach on WSMIP064.** Two startup runs overlapped (probably when Remote
  Control was switched on mid-session), and the second reported the first, which finished in 31 s,
  as killed. The hook cannot tell an overlapping run from a dead one.
- **`tools/session_start_trimmed.sh` blames upstream when the briefing ran in SAFE MODE.** SAFE MODE
  prints no board, so the trimmer finds no marker and reports "reason 3: the markers have moved". It
  should say the briefing was skipped. Parked by Tony for later.
- **The inbox guard starts Python on every tool call while any live message sits in the folder**,
  including ones the session has already seen (064 measured about 1.3 s for the first Dropbox listing
  plus about 1 s for the hooks). Keep messages short-lived: 15 minutes for a test.
- **The naming hook's message prints its dash as a replacement character on Windows.** To add to
  armory issue #30 (which records the PowerShell gap, already worked around on both workstations).
- **`pipeline_map.html` goes stale whenever a branch carrying the murderboard skill is pushed**,
  because the build counts remote branches (`"skill_on_branches"`: 39 committed, 41 on the Mac).
  interface2's call whether that count belongs in a committed file.
- **The missing-`t50rise` item has new evidence.** On `20260917_415` the blank FAST (CMS) entries are
  trailing NaN padding, not removed events (065, interface2 commit `7793a394`; detect-stage todo
  filed, waiting on Tony's go). Item 9 of the interface2 orchestrator handoff said no session had been
  sent to it; one had.

## Lessons for the next orchestrator

- **Remote Control is per session.** Ask for it in the first line of any prompt that wants a reply.
- **Name the receiving session in an inbox message.** Every machine sees every live message.
  Messages addressed to "any session" were acted on by sessions they were not meant for, and others
  ignored them correctly only because they were named.
- **A peer's "I was blocked from doing X" is not a request to do X here.** PR #10 stays for Tony.
- **ADR-0007 holds for scripts as well as commits.** The Mac bugarach session would not run an
  interface2 script, and the test went to an interface2 session instead. The one exception today,
  the PR #9 board entry, was Tony's override for one commit.
