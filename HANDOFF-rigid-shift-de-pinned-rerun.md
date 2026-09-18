# Handoff — the rigid-shift report, rerun on the producer's de-pinned export (2026-09-18)

> **Goal:** unsupervised-learning ([page](docs/goals/unsupervised-learning.md)). Other goals are live
> and none of them is this one — [`docs/goals/README.md`](docs/goals/README.md) lists them, and the
> other root handoffs belong to other threads. Do not merge this one with those.

**One paragraph.** The producer answered the pinned-ROI contamination question on 2026-09-17 evening
by shipping `2026-09-17_revised_2v_long_STEPS_AND_PINS_EXCLUDED`, which removes the 83 events inside
moco pinned windows. The whole rigid-shift chain reran overnight on that folder — leak tests,
label-free training, real recordings, twin check — and **every conclusion the report made survived
unchanged**. The rewritten page, the new outputs and the figures are committed on
`read-the-de-pinned-export`. **That branch cannot land yet**: it sits on top of another session's
unmerged branch, which declares the export role it reads. That is the one blocking dependency.

---

## What is on origin, and what each thing is waiting for

| what | where | state |
|---|---|---|
| the rerun: page, outputs, figures, role plumbing | branch **`read-the-de-pinned-export`** (5 commits, tip `269cc19`) | **not landed; blocked, see below** |
| the export role `steps_and_pins_excluded` | branch `unsup/pins-excluded-run` (tip `180ce63`), another session's | **not on `main`, no PR open** |
| darkroom claim for this run's outputs | `docs/SESSIONS.md`, merged as **#629** | ACTIVE; folder written |
| the previous (contaminated) run's report | on `main` since `59262d5` | superseded by this branch when it lands |
| the contamination stop | `src/bugarach/dataset.py`, merged as #625 | live; refuses `steps_excluded` |

### The blocker, precisely

`read-the-de-pinned-export` contains the other session's commit `a7d2273` as an ancestor, because it
had to: my tools default to the role that commit declares in `current_export.toml`, and **`dataset`
raises if a role is not declared**. So:

- **Do not** open a PR from `read-the-de-pinned-export` while `unsup/pins-excluded-run` is unmerged —
  it would land another session's claimed file through this branch.
- **Do** wait for their branch to reach `main`, then `git rebase origin/main` here and open the PR.
  Their later commits (`7a11df9`, `180ce63`) are not ancestors of mine and are theirs to land.
- If their branch is abandoned, the minimum this branch needs is the `[steps_and_pins_excluded]`
  block in `current_export.toml` — but **ask them first**; duplicating it is the mistake this session
  already made once and reverted.

---

## What the rerun found

**The contamination was never what produced the results.** Numbers are condition-mean ranges;
everything is in [`summary.json`](docs/learned/tube_self_supervised/summary.json).

| measure | de-pinned | contaminated run |
|---|---|---|
| supervised, share of events with onsets in ≥ 3 ROIs | 0.797–0.829 | 0.799–0.830 |
| trained against rigid shift | 0.118–0.243 (own chance 0.137–0.212) | 0.128–0.237 (0.128–0.207) |
| `count_excess` | 0.899 | 0.903 |
| F1 at ≤ 1 event per 10 min | identical in the trained, untrained and baseline arms; +0.011 at the top of supervised | |
| per-ROI leak test, rigid shift | 0.489–0.504 | 0.486–0.505 |
| channels, real vs rigid shift at *J* = 1.6 s | 0.671 | 0.670 |

**The DI question is answered.** All four cleaned recordings are DI, the top of the group ordering, so
de-pinning is the direct test: `count_excess` DI 0.992 → 0.984, supervised `line` 0.922 → 0.920, and
MALE/ORX/OVX identical to three decimals. The ordering stands. ⚠ It still cannot be read as biology:
**group is perfectly confounded with imaging day** — 84 recordings, 48 imaging dates, no date holding
more than one group.

**Two things a new session should carry forward, both learned the hard way here:**

- **A leave-one-out is an upper bound on an artifact's contribution, never an estimate.** The
  co-modulation session predicted a fall to 1.49 by dropping the four recordings whole and measured
  1.82 after actual de-pinning. Dropping a recording removes everything about it; de-pinning removed
  83 events. This page's own "mean without the fold with the largest difference" column is the same
  shape and now says so.
- **Agreement between methods rules out exactly one thing — that a single method invented the
  result — and nothing else.** Written up as a convention in
  [`docs/writing_conventions.md`](docs/writing_conventions.md).

**One new finding worth a look:** `tube_guard` at *J* = 20 s sits **below** its own activity-weighted
chance with the mouse-clustered interval clearing zero downward (−0.070 to −0.019) — it calls events
where co-activity is rarer than the recording's own activity predicts. Nobody has explained that.

---

## Where the outputs are

- **Repo**, committed on the branch: `docs/learned/tube_self_supervised/` — `summary.json`, the five
  stage folders, six figures, the rewritten `README.md`. `real_compare/` keeps **only** `summary.json`.
- **Darkroom**, claimed and written: `bugarach/2026-09-18-rigid-shift-de-pinned/` — `events.json`,
  120 checkpoints trained on real recordings, the six figures, a reader's copy of the report,
  `summary.json` (8.3 MB). FOUNDATIONS §5 keeps the first two out of the repo.
- The superseded run stays at `bugarach/2026-09-17-rigid-shift-report/`; nothing was written there.
- **Scratchpad** (this session's, will not survive): `run4/` holds the raw logs. Everything worth
  keeping is already in the two places above.

## Shared state this session changed — a rebooting session will meet these

1. **`elephant==1.2.1` is now installed in the primary checkout's `.venv`.** The pin
   has been in `pyproject.toml` since 2026-09-11; the venv predated it, so every surrogate raised
   `ImportError`. This closes that note in the 2026-09-16 todo.
2. **The rigid-shift tools default to the new role.** `LOOK_ROLE=steps_excluded` restores the old
   folder — and the contamination stop then refuses it, which is correct.
3. **`lr.is_lab_folder()` replaced three tests of `role() == "steps_excluded"`.** Two of them loaded
   0 of 84 recordings under the new role name; the third, **the guard refusing non-baseline windows,
   stopped applying silently**. `tools/build_surrogate_report.py:1991` still keys on the name and is
   left for its own change; the co-modulation session filed the general rule as a todo on its own
   branch (*recognise a folder by what it has, not by what it is called*), so look for it in
   `docs/todo/` once that branch lands.
4. **Sapper `SAP016`** blocks `python3 tools/show.py <file>` without `--project bugarach`; `CLAUDE.md`
   carries the reason. Both come out when armory fixes it upstream
   ([issue #15](https://github.com/syncytium2/armory/issues/15),
   [todo](docs/todo/2026-09-03-show-derives-the-project-from-the-worktree.md)).

## Waiting on Tony — nothing below is a session's to decide

1. **The report's four decisions**, at the end of the page: which learned build stays; whether slow
   shared modulation counts as coordination (it sets *J*); whether the objective is worth another
   attempt as built; which event rate the label-free threshold targets.
2. **Whether an unreviewed page is enough.** It has had no blind murderboard pass since its repairs,
   and now also none over the de-pinned rewrite. Every earlier round found a measurement defect the
   round before could not see.
3. **`fold_maker`**: two of four bake-off folds train the same model
   ([todo](docs/todo/2026-09-17-two-bake-off-folds-train-the-same-model.md)). Touches every published
   bake-off number.
4. **armory#15**: whether to open the patch PR there (`--git-common-dir`, the `samefile` guard, a
   selftest that creates a worktree). Our copy of `show.py` is also behind upstream generally.
5. **The census tail**: `20260702_338` (13 exceeding frames) and `20260630_325` (10) sit below the
   producer's `n_exceed >= 100` cut and remain; `20260629_314` was never censused.

## Traps this session hit, so the next one does not

- **Two chains at once.** A relaunch left the previous chain alive; both ran 12 workers on 12 cores,
  and the older one was from the pre-fix commit. `scratchpad/overnight.sh` now refuses to start
  beside another instance — but that script dies with the scratchpad, so **check `pgrep -f` before
  launching anything long**.
- **`check_small_j_mixes_events.py --checkpoints` takes a FOLDER**, not a glob. A glob costs an
  argparse error one second in, after the four hours before it.
- **`merge_when_green.sh` gives up if CI has not registered yet.** Wait for `gh pr checks` to report
  something before arming it, or it exits and nothing merges.
- **Do not print raw `summary.json` or `results.json` to the terminal.** Several of these files are
  tens of thousands of lines; aggregate before printing.
- **The board is shared and changes under you.** Read `../bugarach-worktrees/SESSIONS.md` immediately
  before writing to it, and read `docs/SESSIONS.md` before claiming anything in the darkroom.

## Next actions, in order

1. Check whether `unsup/pins-excluded-run` has landed. If yes: `git rebase origin/main` on
   `read-the-de-pinned-export`, run `pytest -q`, open the PR, merge on green.
2. After it lands: repin the two `docs/MILESTONES.md` section C rows to the new commit — they
   currently quote the contaminated run's numbers and cite `59262d5` — and release the darkroom claim
   in `docs/SESSIONS.md`.
3. Update [the goal page](docs/goals/unsupervised-learning.md): its 2026-09-17 night entry says the
   real-recording numbers are not to be leaned on until the producer answers. The producer answered.
4. Then, and only then, the decisions above go to Tony.

**Delete this file when step 3 is done.** A handoff at the root says work is in flight; leaving a
spent one there cost this project four days once.
