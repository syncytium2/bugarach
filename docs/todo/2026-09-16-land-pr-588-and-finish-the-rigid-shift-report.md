---
status: open
filed: 2026-09-16
---

# Land PR #588, and finish what the rigid-shift report still owes

> **Tony, 2026-09-16:** *"we need to close up shop. write the status in milestones and a todo"*

> **Progress, 2026-09-17.** Steps 3 and 4 were done on branch `unsup/rigid-shift-report-residuals`
> (draft PR #603): the residuals were fixed and rerun, and a third blind round ran
> ([record](../reviews/tube-self-supervised-2026-09-17-round3.md)). It reached the three-round cap
> with a blocking finding, that the trained models' checks could not fail against slow shared
> modulation. **Tony chose to add controls that can fail, rerun, restructure the report and run a
> fourth blind round.** The controls, the rerun, a direct check of what the models respond to, and
> the rewritten report are on the branch. **Remaining:** the fourth blind round and its fixes; land
> the branch; then supersede the section C rows in `docs/MILESTONES.md`, pinned to its commits once
> they are on `main`; then the four decisions go to Tony.

> **Progress, 2026-09-16 (Tony: *"do 1 and 2"*).** Steps 1 and 2 are **done**.
> [PR #588](https://github.com/syncytium2/bugarach/pull/588) merged as `b4f09ab` with CI green on
> Python 3.11, 3.13 and 3.14 — after its first CI run caught a regression of this session's own:
> the pipelines line added to the session briefing put it 2 B over budget on a fresh clone, and
> `merge_when_green.sh` refused the merge. Fixed in `d0453de`. The milestone rows are in
> `docs/MILESTONES.md` section C (three) and section H (one). **Steps 3 and 4 remain**, and so does
> everything under *Waiting on Tony*.
>
> **Before starting 3 or 4, read the handoff:**
> [`docs/handoffs/2026-09-16-rigid-shift-report-steps-3-and-4.md`](../handoffs/2026-09-16-rigid-shift-report-steps-3-and-4.md)
> — file and line for every residual, the blind-round procedure, and the traps this session hit.
> It recommends doing **step 4 before step 3**, since several residuals change numbers the report
> quotes, and reviewing text that is about to change wastes a blind round.

Everything from the 2026-09-15/16 sessions was on branch `unsup/rigid-shift-controls`,
[PR #588](https://github.com/syncytium2/bugarach/pull/588), and is now on `main`. Before it landed,
none of it could be a milestone — `tools/check_milestones.py` refuses a row whose commit is not an
ancestor of `origin/main`, correctly.

## What is on the branch

- **The rigid-shift controls**: shared-offset control, graded control, Cossart destruction at real
  participation — [`docs/learned/rigid_shift_look/controls/`](../learned/rigid_shift_look/controls/).
- **The aggregate-channel test** and **label-free training of four architectures** (`tube`,
  `tube_guard`, `line`, `line_length`), the bake-off, the real-recording comparison and the plant
  probe — [`docs/learned/tube_self_supervised/`](../learned/tube_self_supervised/README.md).
- **`line`**, the counting architecture, and its registered ablation `line_length` —
  `src/bugarach/learn/nets/line.py`, `line_length.py`.
- **The report**, rewritten after a blind eleven-role murderboard that returned fifty-one findings —
  [run record](../reviews/tube-self-supervised-2026-09-16.md), filed `Mode: retrospective`.
- **The pipelines index** — [`docs/pipelines.md`](../pipelines.md), its first route
  [`learned-model-evaluation`](../pipelines/learned-model-evaluation.md), and
  `tools/check_pipelines.py`, now in the SessionStart briefing and the pre-commit hook.

## Do, in this order

1. **Resolve the merge conflict.** The PR is a draft and reads `CONFLICTING`; the only conflicted
   file is `docs/SESSIONS.md` (`git merge-tree` against `origin/main`, 2026-09-16). Merge
   `origin/main` into the branch and keep every other session's blocks. ⚠ The PR shows **no
   checks**, and `tools/merge_when_green.sh` refuses a PR with none — mark it ready for review so CI
   runs, then merge on green.
2. **Write the milestone rows, pinned to the merge commit**, and delete the *Open* row that points
   here. Candidates, with the strength each can honestly carry:
   - rigid shift at 10–20 s hides on all three folders and removes shared modulation slower than
     an event on lab slow and Cossart — ⚠ `evidence`, because whether that modulation counts as
     coordination is Tony's open decision;
   - training against rigid shift alone did not beat random initialisation — `measured`;
   - `line` leads the supervised bake-off and is **not separable** from CoactDetect (+0.063,
     t(3) = 1.31) — `measured`, `held`, since MILESTONES reserves bake-off promotion to Tony;
   - the pipelines index is checked in both directions — `built`.
3. **Run a third blind murderboard round** on
   `docs/learned/tube_self_supervised/README.md`. The second round found fifty-one defects, the
   repair was a near-total rewrite, and **the rewrite has not been reviewed**. No number from that
   folder is quotable until a blind pass comes back clean.
4. **Work the residuals the run record carries**, which are the ones that change conclusions:
   - the aggregate-channel classifier's filter bank is built from `tube`'s **initial** parameters,
     not fitted ones — and it is the gate that licensed the whole run;
   - `oracle_threshold` re-derives `pick_threshold` without its edge-of-grid guard;
   - `line`'s "one ROI, one vote" does not hold as written: the sigmoid caps the vote's height, not
     its time integral, and the stage downstream reads the integral;
   - the shared-offset control has never been shown able to fail on the lab fast stream;
   - the untrained arm's widths and coverage are quoted in the report and stored in no file;
   - the seed axis has not been run, and no test covers the numpy rigid shift that produced every
     surrogate.

## Two things in the environment, not the branch

Both fail identically on a clean checkout of `origin/main` (`0a98e2b`), so neither is caused by
this work. The full suite on the branch: 3,108 passed, 3 failed.

- **Elephant is on `main`; it is not installed on this Mac.** `pyproject.toml` has pinned
  `elephant==1.2.1` in both the `surrogates` and `dev` extras since `47e278e` (2026-09-11). The
  `.venv` in the primary checkout predates that pin and was never rebuilt, and the `.venv` is
  machine-local by design (CLAUDE.md, *Machine-local inventory*). So
  `test_holm_corrects_within_each_scope_and_not_across_them` fails there with
  `No module named 'elephant'`, and passes in the separate Elephant venv. Fix: claim the venv on
  the machine-local board, then `.venv/bin/pip install -e ".[dev]"` in the primary checkout.
- **`test_a_worker_past_its_cap_is_killed_and_recorded` fails on a fast machine**, both
  parametrisations, with or without Elephant. It sets a cap (1 MB, or 0.5 s) and expects the
  worker to be stopped; the fixture's job finishes in 0.004 s using about 21 KB, so it never
  reaches either cap and records `ok` where the test wants `intractable`. The test asserts on the
  machine's speed. It needs a workload guaranteed to exceed the cap, not a smaller cap.

A related trap, for anyone running tests from a worktree: the primary `.venv` resolves `bugarach`
to the **primary checkout's** `src/`, not the worktree's. Code that exists only on the branch —
`bugarach.confirm` did — fails to import unless `PYTHONPATH=src` is set.

## Waiting on Tony

The report ends on four decisions; they are written out there with their evidence
([What waits on Tony](../learned/tube_self_supervised/README.md#what-waits-on-tony)):

- does the concentration sensor stay on by default in `line`;
- does shared modulation on timescales of 10–45 s count as coordination;
- is the label-free objective worth another attempt, and if so with one that pays for the number
  of ROIs in a window;
- which firing rate the label-free threshold should target.
