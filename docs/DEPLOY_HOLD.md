---
held: no
set-by: Tony
set-on: 2026-09-01
released-by: Tony
released-on: 2026-09-01
release-when: draughtsman's revised model figure is vendored and lands
released-because: the condition was met — the figure landed in #443 at 1b1297c
---

> ## Released 2026-09-01 — the condition was met, not waived
>
> Tony, 2026-09-01: *"Push."* The hold asked for draughtsman's revised model figure
> to be vendored and land; it did, in **#443** at `1b1297c`, and the page moves once
> carrying it together with #439, #440, #441, #442 and #444 — which is what the hold
> was for.
>
> **What was checked before flipping this**, because a hold released on assumption is
> worse than one nobody set:
>
> - **Vendor freshness, read from the remote rather than a cache.** The stamp on
>   `third_party/draughtsman/__init__.py` is `bcd104a`; draughtsman's upstream HEAD is
>   `bcd104a`. `check_vendor_freshness.sh` could not answer — it exits 2 on the first
>   UNKNOWN family (`session-protocol`, which needs `BUGARACH_INTERFACE2`) and never
>   reaches the draughtsman family, so this was verified by hand. **That
>   short-circuit is worth fixing**: a family the gate cannot check blocks its verdict
>   on families it can.
> - **The build came from `origin/main` and nothing else.** Built in a worktree
>   detached at `bf02001` with `git rev-parse HEAD` compared against
>   `git rev-parse origin/main` first — the hand-run version of the preflight in
>   [`todo/2026-09-01-nothing-stops-a-deploy-publishing-a-branch.md`](todo/2026-09-01-nothing-stops-a-deploy-publishing-a-branch.md).
>   This was not paranoia: the primary checkout is on another session's branch, and
>   building there would have published it with every existing guard satisfied.
> - **The pages were served and walked**, not opened from `file://` — 29 passed,
>   1 xfailed, the xfail being the known diagnostic-page overflow (#440).
> - **The figure was rendered and read in both themes** at five widths. Labels land at
>   9.00px everywhere after #444 derived the scroll floor from the viewBox.
>
> **One thing shipping imperfect, on purpose.** At a 1280px viewport the `.arch` box is
> 1203px against the figure's natural 1222px, so the last stage's right border is
> clipped by 19px and the box scrolls to reach it. All of its text is legible. Widening
> `.arch` would desynchronise it from the hero figure, which shares `min(94vw, 78rem)`
> deliberately, and the fix is not worth that or another CI cycle on the way out.
>
> The 2026-08-28 release block below stays. This file's own rule is that the next hold
> starts from a page recording how the last one ended.

---

> ## Held again 2026-09-01 — the page moves once, with the figure
>
> Tony, 2026-09-01, asked to wait for draughtsman's figure rather than publish
> twice. The front page's whole first screen is now the model, so a deploy that
> carries the phone-legibility fix but not the figure it makes legible is half a
> change, and a reader would watch the diagram move twice in a day for reasons
> neither publish explains.
>
> **What is queued, at the moment of writing:** #439 — the `.arch` narrow-screen
> rule, the `MODEL_SVG` comment, and the test that the committed SVG still matches
> the model — plus whatever `python tools/site_staleness.py` lists. It computes
> the real answer and this file deliberately does not keep a second copy.
>
> **Not a reason to sit on the figure.** The items to settle before the vendoring
> are in
> [`todo/2026-09-01-a-traced-figure-cannot-tell-a-constant-from-an-initialisation.md`](todo/2026-09-01-a-traced-figure-cannot-tell-a-constant-from-an-initialisation.md);
> the load-bearing one is that the revision's *"max-pool, width 3"* is an
> initialisation and not an architectural constant.
>
> The 2026-08-28 release below stays as written. This file's own closing line
> asks that the next hold start from a page recording how the last one ended, and
> this is the next hold.

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
