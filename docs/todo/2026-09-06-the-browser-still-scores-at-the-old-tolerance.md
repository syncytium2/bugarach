---
status: open
filed: 2026-09-06
---

# The browser still scores at 1.5 s after the bench moved to 2.5 s

Found while landing `bench-background-is-not-flat`, and left out of that PR on purpose:
it is viewer work, the viewer is under a deploy hold, and a tolerance change there
moves every number the tune panel shows.

## What is true

`bugarach.score.TOL_SEC` is 2.5 s from the day the bench stopped running a flat
background (2026-08-28; Tony: *"expand the tolerance"*), because on the fitted field
LoCo and CoactDetect plateau at 2.5 s and RateDetect at 2.0 s where five of six had
settled below 1.5 s on the flat one. The Python bench, `diagnostic.py`'s figure, the
README and `docs/generator.md` now all say 2.5.

The browser does not. `docs/site/viewer.template.html` ships two tolerance inputs
with `value="1.5"` — `#tTol` for the tune panel and `#scTol` for scoring — and the
comment block above `SCORE_COPY` says *"the bench scores a hit at a 1.5 s edge gap"*.
The assembled `raster_viewer.html` carries the same three copies.

So the two modes the pipeline handoff says must walk one pathway — a session driving
the Python bench, a user driving the browser — score the same detection differently
at the last step before a number is shown. A user who tunes in the browser and
compares to a published F1 is comparing across tolerances, which `scoring.js`
refuses to *pool* but cannot see when the comparison is done by eye.

## What is not broken

Nothing crashes and no test fails. `test_webapp_scoring_parity.py` checks that both
languages carry the tolerance with the score and refuse to pool across two of them,
which they do. The defect is a default, not a mechanism.

## What to do

1. Change the two `value="1.5"` defaults to `2.5` and the `SCORE_COPY` comment with
   them, then `python tools/assemble_viewer.py` — `raster_viewer.html` is assembled,
   never hand-edited, and `--check` refuses a hand edit.
2. Look for a third copy: `scoring.js` has no constant (it takes `tolSec` from the
   caller), but the tune plan and the scoreboard may carry one.
3. Read the default from one place if the template can reach it — the point of
   `TOL_SEC` was that six bare `1.5`s were five too many, and the browser is a seventh.

The deploy hold (`docs/DEPLOY_HOLD.md`) means this reaches the live site with the
next publish, not before.
