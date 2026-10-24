# The blind theory passes (2026-10-23)

Tony asked whether an analytical prediction could replace the brute force, then asked for the pass
to be run twice more by agents that did not know the first answer. They shared the prompt, the
repository, the record, the tool definitions and the model with the first pass, so this is a
consistency check rather than independent review. Each agent got his
question and pointers to the code and the Aim 1a record, nothing else, and worked in its own
checkout of `main`. Their scripts are kept here **as they ran**: from a worktree's `_scratch/`
folder, against the first Aim 1a record, now `aim1_one_source_shared_seeds.json` (their paths
still say `aim1_one_source.json`), so **they do not run where they now sit**. They are a record,
not maintained tools; `theory.py` is. Its joint fit follows blind A's route (`invert_cr.py`),
re-specified rather than ported: residuals scaled by each order's mean size (A: Charlier
background SE plus a 5 % floor); the surrogate's 1/N and 1/N² terms included (A has neither);
closed-form unrounded window sharing (A: frame-quantized numeric); σ bounds 0.005–5 s and k ≤ N
(A: 0.01–4 s, k − 2 ≤ 60); different starting points. Each folder's
`REPORT.md` is that agent's final report, verbatim apart from personal paths.

| folder | what it holds |
|---|---|
| `blind_a/` | `theory_common.py`, `theory_cr.py` (cumulants, noise), `invert_cr.py` (joint fit of jitter, participants and rate across windows), `theory_assess.py` (chance clusters, one-event Monte Carlo), `theory_floor.py` (ADR-0008 floor), `check_shared_bg.py` and `run_fresh.py` (the seed finding, fresh seeds) |
| `blind_b/` | `theory_cumulant2.py` (cumulants with the at-most-one-event term, noise), `sim_cumulant_check.py` (its 40-seed simulation check), `theory_assess.py`, `theory_floor.py`, `theory_count_detector.py` (count detector recall and false alarms), `jitter_from_window_ratio.py`, `check_row.py` (the seed finding) |

What the three passes agree on, and what each added, is on the goal page, *Aim 0*.
