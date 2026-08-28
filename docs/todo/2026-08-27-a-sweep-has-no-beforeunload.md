---
status: open
filed: 2026-08-27
---

# Backgrounding a tab mid-sweep costs nothing; closing it loses everything, silently

> Tony, 2026-08-27: *"can you change tabs while the sweep is running and not lose
> anything?"* Asked of the page deployed as `acac81b2`. Half-answered before the
> session stopped; both halves are below, and which is which is the point.

## Measured

A 40-setting SCE sweep over two simulated recordings, run twice in one chromium
context — once with its tab in front, once with the tab sent to the background a
second in:

| | rows | settings | errors |
|---|---|---|---|
| in front | 40 | — | none |
| backgrounded | 40 | identical | none |

**Nothing is lost.** The sweep keeps its place, the table comes back whole, the
settings are the same values, and no error is thrown. That is the direct answer
to the question as asked.

## NOT measured, and it is the number that matters

Both runs finished in well under a second, so the tab was **already done** by the
time it was hidden — the test proved the results survive a tab switch and proved
nothing about what happens to a sweep that is *still running* while hidden.

The mechanism to expect: the page yields with
`await new Promise(r => setTimeout(r, 0))` in **17 places**, and `sweepDetector`
hits one once per grid setting and once per fold. Chrome clamps background-tab
timers to **≥1 s**, then to **once per minute** after roughly five minutes
hidden. Neither is data loss; both are the sweep crawling. A 12-setting LoCo
sweep has ~15 yields, so the arithmetic to check is whether a two-minute sweep
becomes a fifteen-second penalty or a fifteen-minute one.

**To finish it:** LoCo or locust (~1.3–7 s a fit, so the sweep outlives the tab
switch), a wide grid, two tabs in one headed context — headless `bring_to_front`
does not change `document.visibilityState`, which is what made the first attempt
measure nothing. Hide it four seconds in, hold it for forty, and compare elapsed
against the same sweep in front.

If the penalty turns out to be large, the fix is not a warning but a different
yield: `MessageChannel` tasks are not subject to the timer clamp, and swapping
the yield primitive is a one-line change in `sweepDetector`.

## The finding that was not asked for, and is probably worse

**There is no `beforeunload` handler on this page. There is no `visibilitychange`
handler either.** Grep the file: neither string appears.

So backgrounding a tab is safe, and **closing it, reloading it, or navigating
away mid-sweep discards the run with no prompt**. A locust sweep is minutes of
work — the panel says so beside the tick list — and the browser's own "leave
site?" dialog exists for exactly this. The page declines it by omission rather
than by decision.

It costs more than the sweep. `TUNED`, `VERIFY` and the simulated folder itself
live only in the page, and the settings file is the deliberate way to carry a
fitted value across a reload. A reader who has swept, not yet saved, and hits
⌘R loses the fit and the folder it was fitted on.

**What a fix has to not become:** a page that nags on every close. The handler
should arm only while `TUNE_RUNNING` — or, more usefully, while there is unsaved
provenance in `TUNED` — and disarm the moment there is not. A blanket
`beforeunload` on a page people open to look at a raster would be worse than the
gap it closes.

## Where

- `sweepDetector` and `runTune` in `docs/site/raster_viewer.html` — the yields
  and the `TUNE_RUNNING` flag.
- `TUNED` / `paintTunedChip` / `paintSaveSettings` in the same file — what is
  actually at risk on a reload, and what already knows whether it has been saved.
