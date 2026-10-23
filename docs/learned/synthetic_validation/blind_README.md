# The blind theory passes (2026-10-23)

Tony asked whether an analytical prediction could replace the brute force, then asked for the pass
to be run twice more by independent agents that did not know the first answer. Each agent got his
question and pointers to the code and the Aim 1a record, nothing else, and worked in its own
checkout of `main`. Their scripts are kept here **as they ran**: from a worktree's `_scratch/`
folder, against the first Aim 1a record, now `aim1_one_source_shared_seeds.json` (their paths
still say `aim1_one_source.json`). They are a record, not maintained tools; `theory.py` is.

| folder | what it holds |
|---|---|
| `blind_a/` | `theory_common.py`, `theory_cr.py` (cumulants, noise), `invert_cr.py` (joint fit of jitter, participants and rate across windows), `theory_assess.py` (chance clusters, one-event Monte Carlo), `theory_floor.py` (ADR-0008 floor), `check_shared_bg.py` and `run_fresh.py` (the seed finding, fresh seeds) |
| `blind_b/` | `theory_cumulant2.py` (cumulants with the at-most-one-event term, noise), `theory_assess.py`, `theory_floor.py`, `theory_count_detector.py` (count detector recall and false alarms), `jitter_from_window_ratio.py`, `check_row.py` (the seed finding) |

What the three passes agree on, and what each added, is on the goal page, *Aim 0*.
