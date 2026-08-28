---
held: no
set-by: Tony
set-on: 2026-08-28
released-by: Tony
released-on: 2026-08-28
release-when: the next iteration of the pipeline plumbing lands
released-because: lifted early — the live page was misattributing a result to another lab
---

> ## Released 2026-08-28, early and deliberately
>
> **The hold did not expire; it was lifted.** Tony, 2026-08-28: *"fine. fucking
> deploy."* The queued changes went out without waiting for the pipeline plumbing.
>
> **Why early.** The live page told readers `locust` **is** CICADA's method — an
> unvalidated claim about another laboratory, beside this project's own benchmark
> numbers — and, four sentences later in the same paragraph, that no method from
> the literature had been run here. Both bold, and they cannot both hold. That is
> the case the "how to release it" section below names in terms: *a wrong number
> on a public page, anything actively misleading a reader.* `ed5e02e` fixes it.
> See [`handoffs/2026-08-28-deploy-notes-2.md`](handoffs/2026-08-28-deploy-notes-2.md).
>
> **⚠ What the published page now predates.** The bench changed on branch
> `bench-background-is-not-flat`, which is **not merged**: the background is no
> longer flat and the scoring tolerance moved 1.5 s → 2.5 s. **Every F1 on the
> published page, and `hero.png` and `diagnostic.png`, were computed under
> neither.** Those figures are rendered from `src/bugarach`, so when that branch
> lands the front page's picture moves and the commit list will not obviously say
> why. Recorded here at that branch's own request — see
> [`handoffs/2026-08-28-the-bench-moved-under-the-deploy.md`](handoffs/2026-08-28-the-bench-moved-under-the-deploy.md).
>
> **This file stays** rather than being deleted, because the next hold should
> start from a page that records how the last one ended.

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
