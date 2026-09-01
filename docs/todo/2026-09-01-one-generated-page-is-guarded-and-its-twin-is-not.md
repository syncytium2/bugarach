---
status: open
filed: 2026-09-01
owner: unassigned
---

# One generated page is guarded against going stale; its twin is not, and the twin is a whole run behind

`build_site.py` carries a good guard. `_is_current()` rebuilds a generated page
from its `.src.html` into a temp file and **compares the bytes**, refusing the
build when they differ — with a comment explaining exactly why an `exists()`
check is not enough:

```
build_site: docs/learned/learned_detector.html is STALE — rebuilding it from
learned_detector.src.html produces different bytes, so the page is quoting an
older run of its own data.
```

**The guard is general and the call site is not.** `_is_current()` takes the page
as an argument and would work on any of them. It is only ever called for
`learned_detector.html`.

`docs/learned/coordination_report.html` is the same kind of artifact — generated
by the same `build_learned_report.py` from `coordination_report.src.html`,
tracked in git, embedding the same `{{SVG:architecture}}` and `{{SVG:pipeline}}`
tokens and the same `{{N:…}}` numeric tokens. Nothing checks it, and it is stale.

Found by `draughtsman` on 2026-09-01 while vendoring the model figure, after the
same class of miss had already cost a deploy-time build refusal that day.

## How stale, measured

A fresh rebuild differs from the committed page by **32,254 bytes**, and the
difference is not cosmetic. Every quoted number moves:

| quantity | committed page | fresh rebuild |
|---|---|---|
| tube F1 | 0.668 ± 0.061 | **0.681 ± 0.049** |
| fold range | 0.58–0.73 | **0.63–0.74** |
| a floor detector's F1 | 0.131 ± 0.012 | **0.118 ± 0.015** |
| its range | 0.12–0.15 | **0.10–0.12** |
| scan time, held-out fold | 0.014 s | **0.023 s** |
| train from scratch | 5.6 s | **6.8 s** |
| the slow variant's training | 236 s | **77 s** |

It also still carries a **retracted claim about ground truth**. The page says the
dashed line *"reaches the SCORER and nothing else. No detector, learned or
hand-written, ever sees it."* `docs/learned/pipeline.svg` was corrected on
**2026-08-28** in `a16b787` — *"The pooled trace does both things, and my
distinction between them was false"* — and now reads *"it fits every detector on
the 3 training folds … No detector ever sees the truth of the fold it is scored
on."* That correction is **on `main`** and has been for four days; the report has
simply never been rebuilt since, because nothing makes it.

## Do not just regenerate it

The one-command fix is real (`python tools/build_learned_report.py
docs/learned/coordination_report.src.html`) and it is **not** the right first
move, for a reason bigger than the one that first suggested itself.

The initial reading was *"regenerating would sweep in someone else's in-flight
`pipeline.svg` correction."* That is wrong on the facts: `a16b787` landed on
`main` four days ago, so nobody is going to land it again and there is nothing
in flight to disturb.

The actual reason is heavier. **This is a report, and every number in it moves.**
Regenerating republishes a different set of results under a commit that would
look like a figure refresh. `CLAUDE.md` requires `/murderboard` for a document
deliverable, and a page whose headline F1 changes from 0.668 to 0.681 is a
document deliverable however mechanical the command that produces it. The numbers
themselves also want a look before they ship: a training time falling **236 s →
77 s** is either a real result or an artifact of a changed cache, and the diff
alone cannot say which.

So: regenerate it deliberately, with the murderboard, as its own piece of work —
not as a side effect of whatever touched a figure.

## What to do

- [ ] **Call `_is_current()` on every generated page, not one.** This is the
      durable half and it is nearly free — the function already takes the page as
      an argument. Anything with a `.src.html` beside it should be checked.
      Without it this finding recurs the next time any embedded token changes.
- [ ] Decide what `coordination_report.html` is *for*. It is **not** in
      `build_site.PAGES`, so it is not published — which is why this blocked
      nothing and why nobody noticed for four days. If it is a live artifact it
      should be guarded and rebuilt; if it is a historical record it should say so
      at the top, and the guard should skip it on purpose rather than by
      omission. Compare
      [`2026-08-30-landscape-is-withheld-until-it-catches-up.md`](2026-08-30-landscape-is-withheld-until-it-catches-up.md),
      which is the same question answered explicitly for a different page.
- [ ] Regenerate it through `/murderboard` once that is decided, so the numbers
      and the ground-truth sentence land together and reviewed.

## Related

- `tools/build_site.py` — `_is_current()` and its one call site.
- [`2026-09-01-the-diagnostic-page-scrolls-sideways-and-takes-the-nav-with-it.md`](2026-09-01-the-diagnostic-page-scrolls-sideways-and-takes-the-nav-with-it.md)
  — the other thing the same afternoon's page-by-page check turned up.
- `tests/test_site_pages_render.py` — builds the real site, so a *refused* build
  is now a red suite rather than a deploy-time surprise. It does not cover this
  page, because nothing builds it.
