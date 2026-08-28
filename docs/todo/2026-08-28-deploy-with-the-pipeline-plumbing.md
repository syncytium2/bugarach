---
status: open
filed: 2026-08-28
---

# The queued site updates go out with the next pipeline-plumbing iteration

Tony, 2026-08-28:

> *"queue these updates to land with the next iteration of the pipeline
> plumbing."*

**This is the work item the hold points at.** `docs/DEPLOY_HOLD.md` stops the
deploy; this file is where the release lives, so that lifting the hold is a task
somebody picks up rather than a thing that happens when the nagging gets loud
enough.

## What is actually queued

`python tools/site_staleness.py` computes it, and this file deliberately does not
keep a second copy — a hand-maintained list of pending commits goes stale, and the
tool already gets it right.

At filing time that was one commit: `53b1d62`, the sweep-range fix on the viewer.
The status banners and the CICADA attribution from 2026-08-27 are **already live**
— another session published them at `0ed939d` on 2026-08-27, before the hold
existed. If you came here expecting those to be pending, they are not.

## Done when

1. The pipeline-plumbing change lands on `main`.
2. `held: no` in `docs/DEPLOY_HOLD.md` — or the file is deleted — **in that same
   PR**, so the release is reviewed with the work that earns it rather than as a
   separate act of judgement afterwards.
3. `npm run deploy`, `tools/audit_deployed_page.py`, and a block on
   `docs/SESSIONS.md` like any other deploy.

## Why a hold and not just "remember not to deploy"

Three things in this repo tell a session to publish, and none of them waits to be
asked: the staleness report's copy-paste command, the daily
`.github/workflows/site-staleness.yml` summary, and the `site:` line in every
session briefing. A queue held in prose loses to all three, and the session that
gives in is *right by every signal available to it*. So the hold lives where those
signals are computed — `tools/site_staleness.py` reads `DEPLOY_HOLD.md` and prints
the hold in all three surfaces instead of the publish command.

The measurement is untouched: a held site still reports how far behind it is, and
still exits 1. Holding a deploy is not the same as calling the page current, and a
hold that turned the verdict green would hide the drift it was supposed to be
managing.

## The open question this does not settle

**Nothing releases the hold by itself.** If the pipeline-plumbing iteration slips,
the page keeps drifting and the only thing standing between it and a reader is a
file saying "not yet". That is the right trade for a queue measured in days; it is
the wrong one for a queue measured in months, and there is no mechanism here that
notices the difference. The staleness report still prints the distance every day,
which is the tripwire — a number that keeps climbing while a hold sits still is
the signal that the queue has stopped being a queue.
