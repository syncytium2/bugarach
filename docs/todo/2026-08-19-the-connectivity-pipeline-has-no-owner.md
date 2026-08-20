---
status: open
filed: 2026-08-19
---

# bugarach's assembly negative rests on a pipeline nobody maintains

The connectivity team disbanded weeks ago believing there was little more to do. On the
strength of their headline that was right; on everything holding it up it was not, and
**bugarach acquired a dependency on it today** — the modularity half of the assembly
negative (PR #139) is computed by `eval_modularity_null` in interface2, not by anything here.

## What was checked, and what it says

**Their load-bearing result is safe.** Reproduced from
`murmuration/archive_sttc_slow_with_group.csv`: intact (DI+MALE) n=39, median `meanSTTC`
0.365 against GDX (OVX+ORX) — matching their published figure exactly. Dropping the
lab-excluded recording gives n=38, median 0.373, rank-sum p = 1.6e-10. **The intact-vs-GDX
finding does not move**, and nothing below should be read as casting doubt on it.

**Four things around it are broken.**

- **The `include` column is inert.** All 240 rows in both stream files carry `include=1`. The
  mechanism for honouring exclusions exists and was never wired to a source of record, so
  `20250731_151` — which the lab marks `exclude=1` — sits in the headline dataset.
- **Their modularity denominator counted untested recordings as negatives.** `above_null_Q` is
  `Q_obs > q_hi`, false for a missing value, so a graph too sparse for Louvain entered the CSV
  as a `0`. The published "3% on ROI, 1% on pensub" is **2 of 77** and **1 of 69**.
- **The pipeline cannot be re-run.** `if2_dead_roi_keep` hardcodes `2R/2026-07-13/`, which the
  R team moved to `2R/QUARANTINE/` as producing "plausible wrong answers". Restoring it runs
  on a known-bad roster; not restoring it errors.
- **Modularity had never been run on the fast stream.** Now done (3 of 78 above null, 3.8%).

## What is waiting, and on whom

- **interface2 branch `bct-modularity-fast`** (GitLab, pushed 2026-08-19) — makes the channel
  an argument with the default unmoved, and adds the `IF2_DROI_CSV` override the pipeline now
  needs. **Nobody is left to open the MR or to decide whether to repoint the default.**
- **Whether murmuration's other conclusions carry the same two defects** — coverage,
  distance-decay, the treatment analyses. Not checked. The undefined-as-negative pattern and
  the inert `include` column are both the kind that survive a review of the numbers a document
  *names*.

## The decision this actually forces

Either bugarach **takes the instrument** — clean-rooming the Louvain-against-jitter-surrogates
test into this repo, so the assembly negative stops depending on an unmaintained MATLAB
pipeline that does not run out of the box — or it **keeps the dependency and documents it**,
in which case this file is the documentation and the assembly report should say so where it
quotes the modularity numbers.

Doing neither is the option that fails silently: the next person to re-run the assembly work
will hit the quarantined-roster error and have nobody to ask.
