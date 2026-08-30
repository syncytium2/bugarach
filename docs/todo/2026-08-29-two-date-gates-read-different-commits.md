---
status: open
filed: 2026-08-29
---

# Two gates guard the viewer's date stamp, and a merge commit makes them disagree

Both are right about their own question. Together they are unsatisfiable for as long
as the page's most recent change lives in a merge commit, and the failure reads as a
wrong date rather than as a disagreement — so the reaction is to edit the stamp, which
fixes one gate and breaks the other.

## What each one asks

| gate | compares the stamp against |
|---|---|
| `tests/test_site_dates.py::test_the_stamp_prefix_is_the_one_the_viewer_page_writes_by_hand` | `build_site._stamp_dates(HEAD)` — i.e. `git log -1 --format=%cs HEAD` |
| `tests/test_site_viewer.py::test_the_version_date_is_the_date_this_page_last_changed` | `git log -1 --no-merges --format=%cs -- docs/site/raster_viewer.html`, or `date.today()` while the file is uncommitted |

Three different commits, then: **HEAD**, the page's last **non-merge** commit, and — for
as long as the change is unstaged — **no commit at all**.

## How it fires

Merge a branch that touches `raster_viewer.html`. The page's newest change is now in a
merge commit, which the second gate skips by design (`--no-merges` is there so a
`pull_request` build does not compare against a merge ref GitHub created at test time —
`test_site_viewer.py`'s own docstring has the incident). So it attributes the page to
whatever non-merge commit came before, while the first gate reads the merge itself.

Measured on 2026-08-29 landing `learned-detector-page`:

```
HEAD %cs                             2026-08-29     <- test_site_dates wants this
page's last non-merge %cs            2026-08-30     <- test_site_viewer wants this
page's last commit of any kind %cs   2026-08-29
```

**Neither date is wrong.** The 2026-08-30 came from a commit made at 22:54 local the
evening before, recorded with an offset that renders as the next day — the timezone trap
`test_site_viewer.py` already documents from PR #262, arriving through a different door.

## The workaround, which is not the fix

Put the stamp in an **ordinary commit** rather than in the merge. Both gates then read
the same commit and agree. That is what was done here, and it is a thing somebody has to
know — which is the definition this project uses for "not a gate".

## What a fix would have to decide

1. **Which commit is "when this page last changed"?** A merge that brings in a change to
   the page did change the page. `--no-merges` exists for a real reason and should not
   simply be dropped; the question is whether a merge that *touches the file* should
   count where a merge ref that touches nothing should not — `git log -1 --no-merges` and
   `git log -1 -m --first-parent` answer that differently.
2. **Should the two gates share one accessor?** They ask overlapping questions from two
   files with two implementations. One function, imported by both, cannot disagree with
   itself — the same argument `build_site.NETWORK` already won for the network scan.
3. **Whose clock?** `%cs` renders in the commit's recorded offset, `date.today()` in the
   runner's. Every evening in New York they differ. Pinning both to one — probably the
   commit's, since the stamp is about the page and not about who is looking — removes a
   whole class of this.

## Not urgent, and worth doing before the next merge that touches the page

It costs one confusing failure and one wrong-looking edit each time. It has now cost
that twice: once on PR #262, once here.
