# Handoff — goal 2's two readouts are on `main`; the tool that produced them is not

> **Its own thread.** The root `HANDOFF.md` and the other root handoffs are different threads;
> none supersedes another. When this one is finished, delete this file — or move it to
> [`docs/handoffs/`](docs/handoffs/README.md) if anything in it is still worth reading.

> **Working material, not murderboarded.** Same standing as `docs/run_records.md`. Nothing here is
> written for an outside reader; the two pages named below are.

**Start at the goal page**, not here:
[`docs/goals/learned-model-family.md`](docs/goals/learned-model-family.md). This file only records
what a session on 2026-09-19/20 left in an odd state, and the one question that is Tony's.

**No counts in this file.** Derive them: `git rev-parse --short origin/main` · `pytest -q` ·
`python3 tools/sapper.py --all`.

---

## What landed, and where to read it

Goal 2's fair comparison — the tuned learned detectors against the every-knob coded detectors,
under nested cross-validation, on two independent seed draws — now has both of its readouts on
`main`:

- **The report for a new reader** — [PR #665](https://github.com/syncytium2/bugarach/pull/665).
  Repo copy `docs/learned/tuned_vs_coact/fair_comparison_2026_09_18/index.html`; built copy
  `<darkroom>/bugarach/2026-09-18-fair-comparison-run/report/index.html`. Run record
  `docs/reviews/fair-comparison-2026-09-19.md`.
- **The merge-gap addendum** — [PR #671](https://github.com/syncytium2/bugarach/pull/671). The
  nets' merge gap selected by the same rules the run used for everything else, on both draws, with
  no retraining, because a merge gap is applied when a net's per-frame output is decoded. Repo copy
  `…/net_merge_gap.html`; built copy `…/report/merge-gap.html`. Run record
  `docs/reviews/net-merge-gap-2026-09-19.md`, **delivered unconverged** — see below.

Both are murderboarded, both carry their role archives verbatim, and the darkroom folder holding
them is **released** on `docs/SESSIONS.md`: it is finished and nothing more is written to it.

## ⚠ The one thing that is Tony's

**The crowded-recording allowance is unsigned, and it decides every gap on the addendum's page.**
Goal 1's move rule refuses a wider merge gap when it costs more than `bench.MAX_CROWDED_DROP` =
0.02 F1 on crowded recordings. Nobody has ever signed off on that 0.02 F1. It is not a rounding
detail here: held-out F1 rises all the way to the widest gap in the grid in every fold-row of both
draws, so **every chosen gap is the boundary that allowance drew**, on both sides — CoactDetect's
own 8 s is the top of its grid because the same check refused its 16 s. One of the refusals turned
on 0.0009 F1. Move the allowance and the settings move with it.

Until that is answered, the addendum's numbers are a faithful report of a rule, not of an optimum,
and the page says so.

## Why that record ships unconverged, and what it means for the next session

The murderboard ran eleven roles blind, then five blind again against the rebuilt page: **11
blocking findings, then 10**. The process's own rule is that a flat blocking count means a
structural problem patching will not retire, and to escalate rather than run a third round — so
both rounds' fixes are applied and the record names its residuals instead of claiming a clean bill.
The residual ⚠ are listed at the end of `docs/reviews/net-merge-gap-2026-09-19.md`; the largest
after the allowance are two accepted choices that fail the crowded check on the outer refits, and a
reproduction check that covers 2 s only.

**Do not read the escalation as "the page is wrong."** The rounds overturned real things and they
are fixed. It means the page ships with named debts, and the next person to touch it inherits them
rather than discovering them.

## The odd state: the readouts are on `main`, the code is not

`tools/tune_net_merge_gap.py` and `tools/build_net_merge_gap_page.py` are on `main`. The tuning
tool they build on, `tools/tune_learned_vs_coact.py`, and the nets themselves are **not** — they
live on branch `tune-bench-comparison` ([PR #642](https://github.com/syncytium2/bugarach/pull/642),
still a draft), which is itself based on
[PR #596](https://github.com/syncytium2/bugarach/pull/596), open and deliberately **not** set to
auto-merge because merging it puts chorus and gauge in the lab server's capabilities and in the
browser's model picker, and those have been run on simulation only.

So:

- **Rerunning either tool needs that branch's `src` and `tools` on `PYTHONPATH`**, plus the saved
  fits of both runs. From `main` alone it will not import.
- **The suite on `main` is nevertheless honest.** `tests/test_tune_net_merge_gap.py` does not run
  the tool against fits it cannot see; it checks every rule a reader relies on against what the
  tool committed and against the run's own `results.json` and selections beside it. Its docstring
  says which, and why.
- **That debt is already on the goal page**, in *Where the work lives* — every ⚠ "not on `main`"
  marker comes off in the same PR as the branch that lands it.

**#642's CI is green on all three Python legs** as of its current head. It stays a draft because
#596 beneath it is Tony's call, not because anything on it is failing.

## Two small things owed, neither urgent

- **`tools/launch_tuning_run_windows.cmd` splits a comma-separated argument** — `cmd` treats commas
  as separators, so `--detectors coact,loco,…` reaches argparse as six arguments. Both workstations
  hit it on 2026-09-18 and both launched through a machine-local wrapper that quotes the list. It
  was deferred while the run held the worktree; the worktree is free now. On `tune-bench-comparison`.
- **The murderboard roster gate cannot see an archive whose name contains an underscore** — it
  strips `_` as markdown emphasis and then reports a complete archive as missing. Filed with the
  reasoning and the upstream fix in
  [`docs/sapper_feedback/2026-09-19-the-roster-gate-eats-underscores.md`](docs/sapper_feedback/2026-09-19-the-roster-gate-eats-underscores.md).
  `tools/murderboard_roster.sh` is vendored, so this repo renamed its archives to hyphens rather
  than editing it. **Name new review archives with hyphens** until upstream fixes it.

## The workstation, WSMIP064

- **Nothing is held.** No run, no scheduled task, the GPU idle. All four of goal 2's blocks on
  `../bugarach-worktrees/SESSIONS.md` are DONE.
- **Three worktrees remain, all clean and all pushed**: `tune-bench-comparison` (#642),
  `fair-comparison-report` (#665, merged — removable), `matched-merge-gaps` (#671, merged —
  removable).
- **Safe to delete, and large**: `%USERPROFILE%\runs\fair-comparison-2026-09-18-gaps\`,
  `%USERPROFILE%\runs\replicate-2026-09-18\` and its `-gaps` scratch — about 30 GB of re-decoded
  arrays `tools/tune_net_merge_gap.py` regenerates. The runs' own outputs are in the darkroom and
  are not these.
- **Two GPU pools at once thrash the 16 GB card.** Run one.
