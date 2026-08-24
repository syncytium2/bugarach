---
status: open
filed: 2026-08-24
---

# The Python can toggle the coincidence window and the browser cannot

`sync_detect(..., tau_mode="fixed")` landed 2026-08-24
([fork #11](../forks.md)). **The browser has no such switch**, because the viewer
carries its own JavaScript implementation of the profile — `adaptiveProfile` in
`docs/site/raster_viewer.html` — and that one still computes the ISI-adaptive
window and nothing else. The curve is labelled *"SPIKE-synch C (adaptive)"*, which
is the word the toggle exists to disambiguate.

**Nothing is wrong today.** Both implementations compute the same thing, the page
matches the Python at its default, and the scoring-parity guard
(`tests/test_webapp_scoring_parity.py`) still holds. The gap is only that one side
gained an option.

## Why it is not just "port the flag"

The page's profile is a **second implementation, not a copy**, and this repo has
one mechanism for that — the splice guard, which pins `scoring.js` and the page's
inlined copy together and refuses a fork. **The profile has no equivalent**, so
the two could already drift and nothing would say so; adding a mode to one side
only widens what could drift silently.

So the honest order is:

1. **A parity test for the profile itself**, page against Python, at both modes on
   the same trains. That is the thing missing, and it would have value even if the
   toggle never reaches the UI.
2. **Then the flag**, in the same commit as the test that pins it.
3. **Then the label**, which is the point of the exercise: a page that can compute
   both windows can say which one it drew, instead of saying "adaptive" and
   meaning one of two things.

## What a UI for it should not do

**Not a free knob beside `tau_max`.** The fixed window makes the measure
rate-dependent — the property SPIKE-synchronization exists not to have — so
offering it as a peer of the cap invites someone to sweep it for a better F1 and
report the winner. It belongs where a *variant* belongs: named, explained in one
sentence, and recorded in the run.

**And it must reach `detector_settings.csv`.** The Python already writes
`tau_mode` into `settings`; a browser run that could pick the other window without
writing down which it used would produce a `detections.csv` nobody can reproduce
— the same defect [RESET §1](../RESET.md) describes for K.

## Blocked on nothing

No decision is pending. It needs the profile parity test first, which nobody has
written.
