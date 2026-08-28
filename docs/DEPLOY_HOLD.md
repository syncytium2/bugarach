---
held: yes
set-by: Tony
set-on: 2026-08-28
release-when: the next iteration of the pipeline plumbing lands
---

# The site deploy is held

**Do not publish `bugarach.tonydefazio.com` while this file says `held: yes`.**
Tony, 2026-08-28: *"queue these updates to land with the next iteration of the
pipeline plumbing."* Pending page changes ride along with that work instead of
going out one at a time.

`tools/site_staleness.py` reads this file, so the tool that otherwise prints
*"Publish it"* prints the hold instead — in the full report, in the daily CI
summary, and in the one-line session briefing. That is deliberate: a hold written
only in prose loses to a nag that fires every morning.

## What is queued right now

Whatever `python tools/site_staleness.py` lists as changing what the site serves.
It is not a fixed list and this file does not keep one — a second copy of "what is
pending" is a thing that goes stale, and the tool already computes it correctly.

As this was written, that was one commit: `53b1d62`, the sweep-range fix on the
viewer. The 2026-08-27 status banners and the CICADA attribution are **already
live** — they went out at `0ed939d` before the hold existed.

## How to release it

Set `held: no` — or delete this file — in the same PR as the pipeline-plumbing
change, then deploy per [`docs/deploy.md`](deploy.md) and record it on
`docs/SESSIONS.md` like any other deploy. The point is that the page moves once,
with that work, and a reader sees one coherent change rather than three days of
half-states.

**If a deploy genuinely cannot wait** — a wrong number on a public page, a broken
link, anything actively misleading a reader — that is not a hold to route around
silently, it is a reason to say so and lift the hold deliberately. Publishing over
a live hold without a word is the failure this file exists to make visible.

## Why this is a file and not a rule in someone's head

Three things in this repo tell a session to deploy: the staleness report's
copy-paste command, `.github/workflows/site-staleness.yml` running daily, and the
`site:` line in the session briefing. All three fire without being asked. A queue
that lives in prose is outvoted by them every morning, and the session that gives
in will be right by every signal it can see.
