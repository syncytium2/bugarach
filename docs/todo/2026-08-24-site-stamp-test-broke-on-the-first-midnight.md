---
status: done
filed: 2026-08-24
---

# The viewer's date-stamp test failed on the first commit after midnight

**Closed the same day, in the commit that found it.** Recorded because the shape
of the bug is worth keeping, not because anything is left to do.

## What happened

`tests/test_site_dates.py::test_the_stamp_prefix_is_the_one_the_viewer_page_writes_by_hand`
compared the **hand-written** stamp in `docs/site/raster_viewer.html` against
`bs._stamp_dates(HEAD)`, whose version date is the committer date of the commit
being built. The page said `this version 2026-08-23`, which was true — that is
the day the page last changed. `HEAD` then moved to 2026-08-24, and the test
failed on a branch that touched nothing to do with the site:

```
assert 'First published 2026-08-13 · this version 2026-08-24' in '<!doctype html>...'
```

It went red on all three Python versions in CI at once, and it was not the
branch's fault. **Every** open branch would have hit it on its next commit, and
`main` on its next merge. The window between landing and firing was about five
hours: PR #269 merged at 23:29 Eastern on 2026-08-23, and the first commit after
midnight tripped it.

## Why it is the interesting kind of bug

The test was not wrong about what it wanted. Its own docstring says the two
sides "must phrase it identically" and to "change both together or neither" —
that is a **phrasing** contract, and the prefix is the part that matters. But it
enforced that contract by comparing to a date that moves on its own, every day,
with no edit to either file. The assertion was satisfiable only on the calendar
day the page was last touched, so it read as a strict test while actually being a
timer.

A generated page takes its version date from HEAD because build_site stamps it at
build time; the viewer page is copied byte-for-byte and cannot be injected into,
so its date is the day that file last changed. Those are two different dates by
design, and they coincide only on the day of the edit.

## The fix

Compare the page's stamp against the last-commit date **of that file** —
`git log -1 --format=%cs -- docs/site/raster_viewer.html` — while still asserting
the shared prefix wording against `build_site`. The contract is preserved and the
clock is out of it: editing the page still forces its stamp to be updated in the
same commit, and a quiet day no longer breaks the build.

## What to watch for elsewhere

Any assertion that pins committed content to `HEAD`'s date has this shape. It
passes on the day it is written and fails later for no reason a reader can see in
the diff, which is the most expensive kind of red — the next session spends its
first hour proving its own change is innocent.
