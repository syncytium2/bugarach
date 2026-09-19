# Handoff — the rigid-shift report's last two steps: fix what changes its conclusions, then review it blind

> **Written 2026-09-16, at the end of the session that ran the work.** Filed here and **not** at
> the repo root on purpose: a root `HANDOFF-*.md` means work is in flight, and nothing is. Every
> commit is on `main`, no branch is waiting and nothing is half-done. What remains is queued work,
> and its open items live in
> [the todo](../todo/2026-09-16-land-pr-588-and-finish-the-rigid-shift-report.md), which is the
> list to tick. This page is the briefing a session needs before starting on it.
>
> **Tony, 2026-09-16:** *"write a hand off for 3 and 4. prepare to end session"*

## Where it stands

- **Landed.** [PR #588](https://github.com/syncytium2/bugarach/pull/588) merged as `b4f09ab`: the
  rigid-shift controls, the aggregate-channel test, label-free training of `tube`, `tube_guard`,
  `line` and `line_length`, the report, and the pipelines index.
  [PR #592](https://github.com/syncytium2/bugarach/pull/592) (`967dfd4`) added the milestone rows.
  CI was green on both.
- **Held.** `docs/MILESTONES.md` section C carries three rows for this work. Two are `held` and one
  is ⚠ `evidence` / `open`. The *Open* table names the third blind review as the thing standing
  between those numbers and being quoted.
- **The report**: [`docs/learned/tube_self_supervised/README.md`](../learned/tube_self_supervised/README.md).
  **The review so far**: [run record](../reviews/tube-self-supervised-2026-09-16.md), filed
  `Mode: retrospective`, with every round-2 role report kept verbatim in
  `docs/reviews/tube-self-supervised-2026-09-16-round2-roles/`.
- **Round 2's lesson, for both steps.** The machine-generated tables reproduced cell for cell.
  **Every one of the fifty-one findings was in the hand-typed prose around them**, and two of them
  inverted the decisions the report was asking Tony to make.

## Recommended order: step 4, then step 3

The todo lists the blind review (step 3) before the residuals (step 4). **Do them the other way
round.** Several residuals change numbers the report quotes. Reviewing first means reviewing text
that is about to change, and a blind round is eleven agents. Fix, re-render, rewrite, then review
the result once. If Tony prefers the todo's order, it still works; it just costs an extra round.

## Step 4 — the residuals, in the order they matter

Each entry says where the problem is, why it matters, and what a fix looks like. The full wording is
in the round-2 role reports named in brackets. **Any fix that moves a number means re-rendering the
figures and rewriting the prose around them**, using the commands in
[`docs/pipelines/learned-model-evaluation.md`](../pipelines/learned-model-evaluation.md). It also
means updating the section-C rows, which pin `75f7e5a` and `8efda4a`: a changed result is a new row
that supersedes the old one, never an edit to the old row.

**1. The gate that licensed the whole run was built at initialisation values** (role 7).
`tools/tube_aggregate_leak.py:54-56` fixes `CENTRES = (1…128)`, `SURROUND_RATIO = 8.0` and
`WIDEN = 1`. A supervised `tube` fitted the way the bake-off fits it has onsets widened by ±2 frames,
surround ratios of 9.7–21.1 and centre widths of 2.3–5.3 frames. The `128`-frame scale lies outside
the model's own clamp of [0.5, 64]. The report's "the pooled trace separates real from rigid-shifted
at 0.66–0.67" comes from this bank. **Fix:** build the channel from a fitted model's `_kernels`
(`src/bugarach/learn/nets/tube.py`), then re-run the aggregate-leak stage. That number may move, and
the report's reading of it with it.

**2. The truth-reading threshold has no edge-of-grid guard** (role 7; role 6, C2 and C3).
`oracle_threshold` (`tools/tube_self_supervised.py:305`) re-derives `pick_threshold`
(`src/bugarach/learn/train.py:228`) and drops its warning for an optimum on a grid end. The grid
(`quantile_grid`, line 232) bottoms out at the median score, so half of all frames fire, which is
what the untrained arm's near-total coverage looks like. The same function returns `None` where
`pick_threshold` returns 0.5, and `score_held_out` then skips it silently. It asks for 4 validation
seeds that map to 2 recordings. And the `ssl_sim` arm's threshold is picked on recordings it was
trained on. **Fix:** give `pick_threshold` a `grid=` argument and call it, then re-run training.
Every truth-reading column may move.

**3. The shared-offset control has never been shown able to fail on the stream that matters**
(role 4 #14; role 6 C1). On lab fast the same classifier reads chance for rigid shift *as well*,
at every *J*. 26–42 % of the paired comparisons are ties (`paired_summary`, line 375; the
`tie_share` is recorded but was never reported until the rewrite). It also preserves the cross-ROI
rate covariance, so it cannot see the one leak the run did find. **Fix:** a positive control that
must move the number, such as a planted per-ROI rate change, or a control that draws the real and
surrogate crops at independent indices.

**4. `line`'s defining claim does not hold as written** (role 6, B1 and B2). The docstring
(`src/bugarach/learn/nets/line.py:47`) says one ROI casts at most one vote. But onsets are summed
before the sigmoid (`forward`, line 141), so the cap bounds the vote's *height* and not its time
integral. The area-normalised difference-of-Gaussians stage downstream reads the integral, and a
four-onset burst delivers 1.7–2.7× the integrated vote of a single onset. The concentration
channel's empty-field baseline is also 0.635, 1.30 and 0.494 rather than 1. **Either** bind the vote
over time and subtract the floor, which is an architecture change and means retraining everything
with `line` in it, **or** rewrite the docstring and the report's rationale to say the cap is on
amplitude only. That is Tony-adjacent: decision 1 in the report is whether the second sensor stays on.

**5. Numbers the report quotes that no file stores** (role 1, F14 and F16). The untrained arm's
detection widths and coverage ("tens of seconds wide… almost the whole recording") exist in no
shipped file, because `results.jsonl` records only `n_detected`. Neither do the fitted smear widths
in the ablation caveat. **Fix:** record widths, coverage and fitted parameters in the result rows,
then quote them from there. This project's gate is "if a number is in the prose, it is in a file".

**6. The seed axis.** One training seed per fold decides nothing at four folds. `tools/fair_bakeoff.py`
already takes `--train-seed` (line 353). Three seeds would settle the second sensor's +0.058 F1 and
`line`'s +0.063 over CoactDetect. This is the cheapest item on the list that feeds a decision.

**7. No test covers the rigid shift that produced every surrogate here** (role 6, C9).
`rigid_frames` (`tools/tube_self_supervised.py:97`) is a numpy reimplementation. The tested,
Elephant-backed `rigid_shift` (`src/bugarach/surrogates.py:368`) is not the path that ran. **Fix:** a
test that the two agree in distribution.

**Lower, and worth doing only if nearby:** the plant probe measures on a flat Poisson background the
generator spec deliberately avoids (role 7). Its ratio statistic is not scale-free through a
six-layer head (role 6, C6). The wave's duration grows with plant size by construction (role 6, C4).
The real-recording "agreement" is a many-to-one overlap share under a `TOL_SEC` name that shadows the
scorer's (role 7). Checkpoints are stamped with an encoding contract the run did not use (role 7).
And five tools hand-copy the model list with no registry check (role 7).

## Step 3 — the third blind round

Run it on the report as it stands **after** step 4.

- **Use `/murderboard`.** Its freshness gate, agent compilation and roster derivation are not
  optional. All eleven roles run as named agents.
- **Blind means blind.** Role prompts name the artifact and its sources and say nothing about what
  rounds 1 or 2 found. Give round 2's archive to nobody until the blind reports are in.
- **Write each report to disk the moment it arrives**, into
  `docs/reviews/tube-self-supervised-<date>-round3-roles/`, as `NN-role-name.md`. Round 2 lost one
  report between arrival and filing; `murderboard_roster.sh check --require-reports` caught it, which
  is why that flag is not optional.
- **Scrub personal absolute paths** from the saved reports before committing. Agents quote full
  paths and sapper's SAP004 blocks them.
- **Role 10 re-runs in full** against the re-rendered figures, including the darkroom copies. The
  real-recording lanes figure lives only in the darkroom (FOUNDATIONS §5 releases one real raster by
  name, *"a list of one, not a category"*), so role 10 has to be pointed there explicitly.
- **Two process gaps that will recur.** Role 5's instructions say to run `murderboard_prose.sh`,
  which is not vendored here, and role 5's grant has no Bash anyway, so it will hand-count again.
  Round 2's role 2 declared `GRANT 2 MISMATCH`. If any role does, the run record's `roles:` line must
  not claim "named agents", or `murderboard_agents.py verify` fails, correctly.
- **Loop.** If the round finds anything, fix it and run another blind round. Only a round that comes
  back empty lets the record declare `Mode: standard` and the section-C rows move off `held`.
- **Gate the record without pipes** (see the first trap below):
  `bash tools/murderboard_roster.sh check --require-reports --require-mode <record>` and
  `python3 tools/murderboard_agents.py --process docs/doc_review_process.md verify <record>`.

## Traps this session walked into, so the next one does not

1. **A pipe swallows the exit code.** `python3 tools/check_milestones.py | tail -1 && git commit`
   committed a failing tree (`92efed4`), because `&&` saw `tail`'s zero. Run gates bare, or
   `set -o pipefail` first.
2. **The session briefing has a byte budget, and CI renders it bigger than a Mac does.** The budget
   is 9,150 B. On a fresh clone the briefing carries extra alarm lines (commit gates OFF, darkroom
   not found), and `data in:` must stay inside the first 2,000 B. A one-line addition failed four
   CI tests (`d0453de` has the story). Measure any briefing change under an empty `HOME` with
   `core.hooksPath` unset.
3. **The primary `.venv` imports the primary checkout's `src/`, not a worktree's.** Set
   `PYTHONPATH=src` when running tests from a worktree. That `.venv` also predates the Elephant pin;
   the Elephant environment is `bugarach-worktrees/surrogate-screen-overnight-venv`.
   `test_a_worker_past_its_cap_is_killed_and_recorded` fails on a fast Mac and passes on CI.
4. **`.claude/hooks/no-heredoc-source.sh` blocks writing source through a heredoc.** Write Python
   with the Write tool, even a throwaway script.
5. **Tools named `tube_*` sweep the whole registry**, and `--checkpoints` on
   `tube_ssl_real_compare.py` *writes* the fits while `probe_line_vs_fuzz.py` reads them.
6. **`tools/merge_when_green.sh` removes the worktree after a merge** unless given `--no-reap`. It
   does true merges, so a branch's own commits can be pinned in milestone rows afterwards.
7. **`bugarach.paths.darkroom()` already ends in `bugarach`.** Appending it again doubled a path
   once this thread.
8. **`check_milestones.py` reads every code span in a row as a path.** Write `tools/x.py`, not `x.py`.
9. **`SendUserFile` may report success and deliver nothing in VS Code.** Put images in front of
   Tony with `tools/show.py` and give the path it prints.

## Waiting on Tony, not on a session

Four decisions, each with its evidence, are in the report under
[What waits on Tony](../learned/tube_self_supervised/README.md#what-waits-on-tony): whether the
concentration sensor stays on by default; whether 10–45 s shared modulation counts as coordination;
whether the label-free objective gets another attempt; and which firing rate the label-free threshold
targets. Step 4's item 4 feeds the first, and item 3 bears on the second.
