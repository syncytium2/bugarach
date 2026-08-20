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

## The audit: was "little more to do" right?

**On the conclusions, essentially yes. On the reporting, no — there is a systematic bias, and
for the negative claims it points the wrong way.**

Every `above_null`-style verdict column in `murmuration/` was checked for the pattern: a
recording whose statistic could not be computed enters the file as a **0**, because
`obs > threshold` is false for a missing value. It is in **13 verdict columns across 8
files** — not confined to modularity.

| file | verdict | fires / scored | fires / all rows | untested read as 0 |
|---|---|---|---|---|
| `archive_sttc_slow_with_group` | `above_null` | 202/234 = **86.3%** | 202/240 = 84.2% | 6 |
| `archive_sttc_fast_with_group` | `above_null` | 189/236 = **80.1%** | 189/240 = 78.8% | 4 |
| `eval_modularity_null_slow` | `above_null_Q` | 2/79 = **2.5%** | 2/83 = 2.4% | 4 |
| `eval_centrality_slow` | `above_null_3` | 33/78 = **42.3%** | 33/83 = 39.8% | 5 |
| `eval_centrality_slow` | `above_null_4` | 5/72 = **6.9%** | 5/83 = 6.0% | 11 |
| `eval_bct_treatment_null_slow` | `above_null_b` | 3/70 = **4.3%** | 3/74 = 4.1% | 4 |

Corrections are one to three points and **no claim flips**. But the direction is not neutral:

- Where the claim is a **positive** ("coordination is above null in most slices"), the bias
  **understates** it — the real rate is higher.
- Where the claim is a **negative** ("no modular structure", "no centrality structure"), the
  bias **flatters** it. Counting a recording nobody could test as one that was tested and
  found nothing makes an absence look better established than it is. That is
  anti-conservative in exactly the place a negative result can least afford it.

So the finding is not "their results are wrong". It is that **every negative in this project
is quoted over a denominator that includes recordings it could not test**, and any of them
that gets written up should be recounted first. The recount is arithmetic, not re-analysis.

**The `include` column, separately, is inert** — `1` on all 240 rows of both stream files, so
the mechanism for honouring the lab's exclusions was never wired to a source of record.
`20250731_151`, which the lab marks `exclude=1`, is in the headline dataset. Dropping it moves
the headline from n=39 / median 0.365 to n=38 / 0.373, p = 1.6e-10. **It does not matter for
that result**, and it was not checked for any other.

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
