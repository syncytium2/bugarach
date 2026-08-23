---
status: open
filed: 2026-08-23
---

# LoCo's null comes from the analysis window, not the period the window was cut from

Rescued from `2026-08-20-webapp-session-status.md` when that page was closed. The
port is faithful; the question is about how it is called, and no test asks it.

## What differs

LoCo clamps its rolling context to the **raw region**, so the null it compares a
moment against is estimated from the whole period the moment belongs to rather than
from whatever slice of that period is being analysed. That is deliberate in the
Python: a threshold fitted inside a narrow analysis window is fitted on less
background than the period actually offers, and on background that has been selected
for.

The browser page hands `locoDetect` **one analysis segment per call**, which makes
the clamp a no-op — there is no wider region for it to reach back into. So the two
implementations agree on every recording where the analysis window is the period,
and diverge exactly where it is not.

`bugarach detect` resolves windows onto the recording before any detector runs, and
the three region-aware ports read them through the supplied-windows path, so it is
worth checking whether the headless route has quietly acquired the same shape as the
browser rather than the shape the Python was written with.

## Why it has not bitten

**It only bites where an analysis window is narrower than its region**, and the two
real export folders mostly state windows that are the periods. That makes it a
sleeper rather than a non-issue: the first producer who sends a genuinely trimmed
window gets a different threshold from the two routes and nothing will say so.

## What settling it looks like

Not "make them match" — decide **which null is correct**, say so, and then make the
callers agree with the decision. Either:

- the period is the right background and the browser should be given it, which means
  passing the region alongside the segment; or
- the analysis window is the right background, because the producer trimmed it for a
  reason and reaching outside it re-imports data they excluded — in which case the
  Python's clamp is the thing to revisit, and FOUNDATIONS §4's rule that folder input
  is used verbatim is the argument for it.

The second reading is the one the export contract points at, which is why this is a
decision rather than a bug report. `region_windows` is a 1e-9 parity port and is not
what would change either way.

## Check that it can fire

Whichever way it goes, the test is a recording whose analysis window is materially
narrower than its period, run through both routes, asserting the same threshold. That
case does not exist in the fixtures today, so it has to be built — and built first,
so the fix is checkable rather than assumed.
