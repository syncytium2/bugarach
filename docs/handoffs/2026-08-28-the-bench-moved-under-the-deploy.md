# The bench moved under the deploy — every published number and two published figures

> **Updated 2026-08-28, after the deploy.** The hold was lifted early and the site
> published at `3a0b63b` (PR #386) — *"the live page was misattributing a result to
> another lab."* The two conditional sections at the end are no longer both live:
> **the deploy went first**, and the session that ran it carried this note's caveat
> into [`DEPLOY_HOLD.md`](../DEPLOY_HOLD.md) rather than leaving it here. What
> remains open is the other branch — what happens when `bench-background-is-not-flat`
> lands on a site that has already published.

**The published page predates the bench.** When the hold was set, the queue was
three viewer commits and a prose fix. Then the bench itself changed: the
background is no longer flat and the scoring tolerance moved 1.5 s → 2.5 s.
**Every F1 now on the site was computed under neither of those**, and `hero.png`
and `diagnostic.png` are *rendered from* `src/bugarach`, so they will move when
that branch lands.

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

Two readings wanted opposite rewrites, and the failure alone could not separate
them. **It has since been measured**, and the answer has its own handoff:
[the winner stopped changing](2026-08-28-the-winner-stopped-changing.md). Short
version — the axis **still discriminates** (own-range 0.185 → 0.136,
between-detector spread 0.117 → 0.098, neither collapsed), and the four-place
reordering was living in a crowded low-F1 tail that the *flat* field manufactured
at the busy end.

So these three are still red, but no longer undecided: what they should assert is
the spread rather than the ordering, and that note lists three options in the
order worth trying. **Tony has not ruled on the rewrite** — that is the open item
on this branch.

`test_the_server_reproduces_the_published_bakeoff` also fails, and it is a
consequence rather than a decision: it compares against `docs/learned/bakeoff.json`,
computed at 1.5 s on a flat field. Regenerating that file puts new numbers into
something people read, so it waits for the same ruling.

## The deploy went first — done, 2026-08-28

The hold was lifted early and the site published at `3a0b63b` (PR #386), because
the live page was misattributing a result to another laboratory. This note asked
for one thing in that case — *say in the deploy record that the published bench
numbers predate the background change* — and the session that ran it did, in
[`DEPLOY_HOLD.md`](../DEPLOY_HOLD.md) rather than only in a PR body, which is the
better place: the next hold starts from a page that records how the last one
ended.

Nothing here blocked that deploy and nothing here was published by it. **The
site's F1 numbers and both rendered figures are the pre-change ones.**

## When this branch lands — still open

**Rebuild and *look at* `hero.png` before uploading**, not just the four pages'
links. It is rendered from the detectors at the bench's settings, and both the
background and the tolerance moved, so it will not be the picture now on the
site. `docs/deploy.md`'s *"drive the built site before you upload it"* is the step
that catches this, and it is exactly the step a prose-only change trains people
to skip — the deploy that just happened was a prose-only change.

The before/after render comparison **has still not been run** (residual ⚠ below);
the claim rests on reading the build's imports. Running it is now cheap and
meaningful, because there is a published `hero.png` to compare against.

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
