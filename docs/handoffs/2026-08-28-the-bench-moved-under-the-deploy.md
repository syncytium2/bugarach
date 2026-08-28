# The bench moved under the deploy — every published number and two published figures

**The deploy hold is protecting more than it was set up to protect.** When it was
set, the queue was three viewer commits and a prose fix. Since then the bench
itself changed: the background is no longer flat and the scoring tolerance moved
1.5 s → 2.5 s. **Every F1 on the site was computed under neither of those**, and
`hero.png` and `diagnostic.png` are *rendered from* `src/bugarach`, so they move
too.

None of it is merged. Branch `bench-background-is-not-flat`, **red on purpose —
four tests**: three that encode a finding and one stale published artifact, both
described below. Suite otherwise **1,492 passing**. This note exists so the deploy
session finds that out here rather than from a figure that changed without
explanation.

> Tony, 2026-08-28: *"all the benchmarks have changed because the bench is
> changed. cut the gordian knot."* — and, on the four decisions it surfaced,
> *"matlab is irrelevant… expand the regime. expand the tolerance."*

**Companion to** [`what #351 changes under the deploy`](2026-08-28-what-351-changes-under-the-deploy.md)
(the viewer page) and [`deploy notes 2`](2026-08-28-deploy-notes-2.md) (the front
page's attribution prose). Those two cover commits already queued. This covers a
change **not yet queued** that would land on the same page.

This does not lift, amend or duplicate [`docs/DEPLOY_HOLD.md`](../DEPLOY_HOLD.md).

---

## The one thing to check before publishing

`tools/site_staleness.py` warns, in its own output, that **`hero.png` is rendered
from `src/bugarach`, so a detector change can move the published picture without
appearing in the commit list.** That caveat is now live rather than hypothetical:

| build input | reads | so it moves when |
| --- | --- | --- |
| `hero.png`, `diagnostic.png`, `diagnostic.html/.txt` | `tools/make_diagnostic.py` → `BENCH_RECORDING`, `OPERATING_POINTS` | the background or an operating point changes |
| the same figures' hit/miss marks | `ui/diagnostic.py` → `score.TOL_SEC` | the tolerance changes |
| `docs/learned/bakeoff.json` → the served comparison | a stored artifact, **not** rebuilt by the site build | never — it is stale and stays stale until regenerated |

**If this branch lands before a deploy, the front page's figure changes and the
commit list will not obviously say why.** That is the sentence worth carrying.

## What actually changed, and what it cost

**The background.** `bg_rate_shape` and `bg_burst_shape` — fitted weeks ago from
81 baseline windows / 2 643 ROIs, and left `None` because that kept the RNG
stream identical — are wired into `BENCH_RECORDING`.

Paired over 12 seeds, F1 deltas run −0.069 to +0.076. **Quiet keeps its ranking**
(coact > loco > rate > cicada > sync > sce); busy reorders three detectors that
sat within 0.02 of each other, which is a coin landing differently. *Use 12
seeds:* the first 3-seed run showed swings to 0.12 that were noise, and quoting
them would have been wrong.

**The tolerance**, 1.5 → 2.5 s, now `score.TOL_SEC` with one home instead of six
bare literals. On the fitted field LoCo and CoactDetect plateau at 2.5 s and
RateDetect at 2.0 s, where five of six had settled below 1.5 s on the flat one. A
tolerance under the plateau does not make the bench stricter — it makes every F1
understate its detector.

**Coact's grid** gains `1e-1` and `3e-2`; its optimum had walked off the loose end
once the background stopped being flat. It brackets again at 0.001 / 0.0001.

**The regime budget was not touched, and that is the result.** Rate's precision
swing across the regime shift was 0.103 against a 0.10 budget *at the old
tolerance*; at 2.5 s it is **0.003**. All six measure 0.017 / 0.128 / 0.193 /
0.002 / 0.003 / 0.011, every one inside the budget it already had. The guard was
reporting the tolerance, not the operating point. Expanding the budget — which is
what was asked for — would have hidden a number that fixed itself.

## The bug this note found

Moving `TOL_SEC` caught five call sites and **missed four in `ui/diagnostic.py`**,
the module that renders the published figure. The bench would have scored at
2.5 s while the picture on the front page scored at 1.5 s, and nothing would have
said so — the two simply stop being the same measurement.

Fixed on the branch. **No test compares the figure's tolerance to the bench's**,
which is why it could sit there, and that gap is still open. Two `tools/probe_guard_*`
scripts still pass `tol_sec=1.5` explicitly; two of their siblings already use
`TOL_SEC`, so those two look unmigrated rather than deliberate. They publish
nothing, so they are recorded, not changed.

## What is still red, and why it was left

Three `test_background_curve` tests. On the flat field the *winner changed* as
background rate swept, and one detector moved four places — the tests assert
exactly that, because it proves you cannot quote "detector X is best" without
naming a background. With the fitted field **coact wins at every rate** and the
largest rank change is two.

Two readings, opposite rewrites, and the failure cannot separate them:

1. the instability was largely an artifact of the flat field, and the honest new
   claim is "coact wins across the range"; or
2. the fitted heterogeneity now dominates the rate axis, so the axis has stopped
   discriminating and these tests should sweep something else.

Re-baselining them to the new numbers would delete the finding either way. One of
them says so in its own failure message: *"the reordering this test was written
for has gone, which is good news worth looking at."* **Tony has not ruled on
this one** — it is the open item on this branch.

`test_the_server_reproduces_the_published_bakeoff` also fails, and it is a
consequence rather than a decision: it compares against `docs/learned/bakeoff.json`,
computed at 1.5 s on a flat field. Regenerating that file puts new numbers into
something people read, so it waits for the same ruling.

## If you deploy before this lands

Nothing here blocks you. The site serves what is on `main`, this is not on
`main`, and the two companion notes cover what is. **Say in the deploy record
that the bench numbers on the published page predate the background change** —
otherwise the next deploy moves the figure and the diff will not explain it.

## If this lands first

Rebuild and *look at* `hero.png` before uploading — not just the four pages'
links. It is rendered from the detectors at the bench's settings, and both of
those moved. `docs/deploy.md`'s "drive the built site before you upload it" is
the step that catches this, and it is the step a prose-only change lets people
skip.

## Reproduce

```bash
PYTHONPATH=$PWD/src python -m pytest tests/ -q     # 1,492 pass, 4 red, named above
PYTHONPATH=$PWD/src python -c "from bugarach.score import TOL_SEC; print(TOL_SEC)"
```

⚠ **Check `git config --get core.hooksPath` in whatever worktree you use.** It
came back empty here after a rebase, and `tests/test_hooks_installed.py` was the
only thing that noticed — two commits on this branch went in with the branch
guard, sapper and the board guard all silently absent. `git config
core.hooksPath .githooks` restores it; sapper was re-run by hand over the whole
tree afterwards and is clean. Whether a rebase can really clear it, or another
session rewrote the shared `.git/config`, is not established.

`PYTHONPATH=$PWD/src` is not optional in a worktree —
[why](../todo/2026-08-28-a-worktree-pytest-run-tests-the-primary-checkouts-src.md).
The paired-delta and heterogeneity tables come from two scratch scripts that are
not in the tree; if they are wanted permanently they belong in `tools/` beside
`probe_vs_heterogeneity.py`, which does the same job for PR #50.
