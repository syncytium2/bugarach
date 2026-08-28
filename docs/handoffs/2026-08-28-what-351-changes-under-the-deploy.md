# What #351 changes under the deploy, for whoever lifts the hold

**`53b1d62` is not a content change.** It changes **how every long loop on the
page schedules itself**, adds a **browser prompt the page never had**, and stamps
autofill-refusing attributes on **all fifty inputs**. A reader looking at a raster
sees nothing new. A reader who runs a sweep, tries to close the tab, or has a
password manager installed sees all three.

The riskiest part is the one with the least to show for it: the scheduling swap
touches **seventeen call sites, only four of them in the sweep**.

> Tony, 2026-08-28: *"there are a lot of moving pieces. i don't think we should
> deploy at this time. prepare a coordination handoff so the session that handles
> deployment is aware of your work."*

This does **not** lift, amend or duplicate [`docs/DEPLOY_HOLD.md`](../DEPLOY_HOLD.md).
That file owns the hold, and it deliberately keeps no list of what is queued
because `tools/site_staleness.py` computes it. This answers a different question:
**when the page does move, what did `53b1d62` change about how it behaves, and
what should the pre-flight look at.**

---

## What is queued, and what is already live

Three viewer commits were pending when this was written (`1b82160`), and one is
mine. **Re-run `python tools/site_staleness.py` rather than trusting this table** —
`main` moved twice while this was being reviewed, and it is the tool's job to
know, not this file's.

| commit | what it is | whose |
| --- | --- | --- |
| `53b1d62` | autofill attributes, the unload guard, the scheduling swap | this handoff |
| `173accd` | the learned rows join the scoreboard table | another session |
| `f7c0edb` | the panel says why it is quiet with no trainer | another session |

**The sweep range control is already live.** It went out at `0ed939d` on
2026-08-27, before the hold existed, along with the status banners and the CICADA
attribution fix. So if someone reports the range boxes behaving oddly on the live
page today, that is `0ed939d`'s behaviour and not something waiting in the queue —
worth knowing before debugging the wrong version.

## The three things `53b1d62` does

### 1. A `beforeunload` prompt, which the page never had

The page now asks the browser's own "leave site?" question in exactly two states:
a sweep is **running**, or a setting the sweep chose has **not been saved to a
settings file**. Nothing else — not an open folder, not a hand-typed threshold,
not a drawn detection. ("Armed" below means one of those two states holds.)

**This is the change most likely to be noticed, and the one to watch after
publishing.** The failure that matters is not the prompt failing to appear; it is
the prompt appearing when it should not. A viewer that asks on every close trains
the one reader it is for to click straight through it, and then it protects
nobody. `tests/test_webapp_leaving_the_page.py` spends most of its cases on
staying quiet, including one that fires a real `beforeunload` and asserts the
event comes back **uncancelled**.

**Walking it by hand after publishing:** run a sweep, apply the setting, try to
close the tab — you should get the prompt. Save the settings file, try again — it
should let you go. That is the whole feature, in two clicks.

### 2. Every long loop yields differently

All seventeen `await new Promise(r => setTimeout(r, 0))` sites became
`await yieldToUI()`, built on a `MessageChannel`. **Four are in the sweep** — two
in `sweepDetector`, two in `runTune`. The other thirteen are in the folder walk,
the detection runs, the assessment and the annotation loop, so this commit touches
the scheduling of nearly every long-running thing the page does. That is more
surface than its description suggests, and it is why this is the part to be
careful about.

Why it was worth doing. Chrome clamps background-tab timers to ≥1 s, and to
≥1/min after about five minutes hidden (Chrome's documented behaviour — **not
re-verified against Chrome's docs in this session ⚠**). The yields are per grid
setting, so the clamp multiplies by sweep size rather than costing a flat delay:

| sweep | timer yields | in front | at the 1 s clamp | after ~5 min hidden |
| --- | --- | --- | --- | --- |
| LoCo, 20 settings | 25 | 10.1 s | ~25 s | **~25 min** |
| locust, 6 settings | 8 | 4.2 s | ~8 s | ~8 min |
| RateDetect, 8 settings | 13 | 0.1 s | ~13 s | ~13 min |

Three simulated recordings of 30 min, 40 ROI. (*locust* is this project's port of
the CICADA detector; it and LoCo are the two slow ones, together about 97% of a
six-detector sweep's wall clock.) Measured after the change:
instrumented **timer** yields for the LoCo case went **25 → 0**, and the
foreground got slightly faster (10.1 s → 9.7 s), with every other detector inside
noise.

**⚠ What this does NOT establish.** The swap removes the **timer** clamp — that
much is measured, because the timer-yield count is zero. Whether Chrome throttles
`MessageChannel` tasks in a hidden tab by some other mechanism **was not
measured**, so "backgrounding now costs nothing" is not a claim this file makes.
Chromium under automation refuses to throttle three different ways: Playwright
launches it with `--disable-background-timer-throttling` and two friends, dropping
those flags still will not hide a tab via `bring_to_front`, and CDP's `frozen`
lifecycle state was ignored (the sweep ran to completion through it).

**This deploy is the cheapest chance to settle it.** On the live page, in an
ordinary browser: start a locust sweep, switch tabs for a minute, come back. If it
is roughly as far along as it would have been, the swap did what it was meant to.

### 3. Fifty inputs stamped against autofill

Five attributes on every `<input>` in the markup, plus a `noAutofill()` helper for
the four built at runtime. This is the bulk of the diff and the least of the risk:
the attributes are inert to everything except a password manager.

It is a superset on purpose. LastPass was reported filling the sweep's *from* box;
the page had no autofill hint anywhere, so "only the new boxes are broken" and
"they always were and nobody looked" were both live readings, and only a real
browser with a manager installed could separate them. No input on this page is a
credential, so covering all fifty costs nothing and settles it.

**This is the one thing no headless pre-flight can verify.** The tests prove the
attributes are present; whether LastPass now leaves the box alone needs a browser
with LastPass in it. If you have one, that is a ten-second check on the live page,
and it is the actual bug report.

## What the pre-flight should do differently

Nothing — and that was checked rather than assumed:

- **No tool or test in this repo registers a dialog handler.** Grepped `tools/`
  and `tests/` for `on("dialog"`, `once("dialog"`, `expect_event("dialog"`,
  `.dismiss(` and `.accept(`: zero hits. The same grep finds two hits in the
  scratch script that *does* register one, so its silence means something.
- **`tools/audit_deployed_page.py` never arms the guard.** It loads the page once
  and never sweeps or applies a fit, so no prompt can fire at it.
- The full suite passes with all of this in place — **1,485 passed, 16 skipped, 1
  xfailed** at `1b82160`, run with `PYTHONPATH=$PWD/src` (see the worktree trap
  below), including every existing browser test.

**One trap, if you write your own driver.** A driver that registers its own dialog
handler and calls `dismiss()` on a `beforeunload` is saying *stay on this page*,
and its next navigation aborts with `net::ERR_ABORTED`. I hit exactly that while
testing and briefly misread it as the guard blocking navigation — it is not.
Playwright's default handling (no handler at all) navigates fine, and so does
`accept()`.

## Two things that will bite the deploy session regardless of #351

Neither is mine; both cost me time on 2026-08-27, and both are already filed:

- **`npm install` every deploy.** `merge_when_green.sh` reaps the deploy worktree
  when it lands the deploy-record PR from inside it, and `node_modules` goes with
  it. Three deploys, three installs, recorded in the `deploy-0827` block on
  `docs/SESSIONS.md`; a fourth confirmed it.
- **A worktree that edits the viewer fails a test about a file it did not touch.**
  The editable install resolves `bugarach.lab.VIEWER` to the *primary checkout*,
  so `test_lab_server.py::test_the_server_hands_out_the_page_with_the_shim` fails
  in any worktree with viewer edits. `PYTHONPATH=$PWD/src` passes all 20. Filed:
  [worktree tests read the primary checkout's viewer](../todo/2026-08-27-worktree-tests-read-the-primary-checkouts-viewer.md).

## A correction this handoff owes

**PR #351's body and commit message both say the suite was "1,442". That number is
wrong.** The run behind it reported *1 failed, 1421 passed, 15 skipped* — the one
failure being the worktree trap above. Nothing downstream depends on it and the
history is not being rewritten to fix it, but the figure is in a merged commit
message where a later reader would take it at face value, so it is corrected here.
The verified count today is the 1,485 quoted above.

## Still open, and not blocking the deploy

[One knob per detector is the next wall](../todo/2026-08-27-one-knob-per-detector-is-the-next-wall.md) —
the sweep varies exactly one setting per detector, and the page's own
degenerate-sweep message already tells the reader to *"sweep the parameter that is
binding, or sweep them together"*, which nothing on the page can do. The smaller
fix is probably letting the reader choose **which** knob rather than only its
range. Unowned.

## Provenance

| | |
| --- | --- |
| merged | PR #351, `53b1d62`, 2026-08-27 |
| tree when written | `1b82160` |
| live | `0ed939d`, worker version `acac81b2` |
| tests added | `tests/test_webapp_no_autofill.py`, `tests/test_webapp_leaving_the_page.py` |
| todos closed | the [autofill](../todo/2026-08-27-lastpass-autofills-the-sweep-range-boxes.md) and [unload](../todo/2026-08-27-a-sweep-has-no-beforeunload.md) items, both `status: done` |
| residual ⚠ | Chrome's clamp figures are quoted from documented behaviour, not re-verified here; and `MessageChannel` throttling in a hidden tab is unmeasured — see §2 |
