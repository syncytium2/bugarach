# Handoff — porting modularity into bugarach, 2026-08-19

**Paused for CI upgrades (chromium install), mid-task and deliberately unfinished.**
Nothing here is validated. Do not quote a number out of `src/bugarach/graph.py` yet.

## Where this sits

Branch `wip/modularity-port`. The only new file is **`src/bugarach/graph.py`** — it
imports and runs, and that is *all* that is known about it. It has **no tests, no
differential validation, and is not wired into any tool or report.**

`main` is clean and complete without it: the assembly answer landed in PRs #135, #139,
#140, #141, and the connectivity findings in #143 (open at pause — the audit commit
`d85ef2b` is pushed on `connectivity-is-unowned`).

## Why it was being built

Tony, 2026-08-19: *"the connectivity team disbanded weeks ago believing there was little
more to do."* PR #139 had just put the modularity half of the assembly negative on
interface2's `eval_modularity_null`, which now has no maintainer **and does not run out of
the box** — its dead-ROI roster path resolves into `2R/QUARANTINE/`. A published negative
should not rest on a pipeline nobody can execute. Tony chose: port it, and audit the rest.

The audit is **done** and is in
[`docs/todo/2026-08-19-the-connectivity-pipeline-has-no-owner.md`](docs/todo/2026-08-19-the-connectivity-pipeline-has-no-owner.md).
Short version: the undefined-as-negative defect is in **13 verdict columns across 8 files**,
no claim flips, but it **flatters every negative** in that project. Their headline is safe —
verified.

## What `graph.py` contains, and what is honest about it

- `sttc()` — Cutts & Eglen (2014), written **from the paper**. `if2_sttc.m` was
  deliberately not read, so this part is genuinely independent and is the part
  differential validation can actually certify.
- `sttc_matrix()`, `modularity()`, `louvain()` (best-of-N restarts), `jitter_trains()`,
  `modularity_vs_null()` -> `ModularityResult`.
- **This is a PORT, not a clean-room, and the module says so.** The MATLAB driver was read
  while chasing the quarantined roster, so the *procedure* — window, surrogate scheme,
  best-of-N — is not independently derived. Only the coefficient is.

## The three steps that finish it, in order

1. **Differentially validate against the reference CSVs.** They are already in the repo:
   `docs/learned/eval_modularity_null_{fast,slow}.csv`, 78 + 77 scored recordings with
   per-slice `n_active`, `meanSTTC`, `Q_obs`, `Q_null_mu`, `z_Q`, `above_null_Q`.
   - `n_active` and `meanSTTC` are **deterministic** — these must match tightly, and that
     is what certifies the STTC, the windowing and the active-cell rule.
   - `Q_obs` and `z_Q` are **stochastic** (best-of-5 Louvain on random restarts, 200 random
     surrogates) — compare distributionally, and compare the **verdict** per recording.
   - Read the window rule off the reference driver rather than guessing: baseline region,
     the producer's analysis window where present, `dt=2.0`, `jitter=20`, `pctl=95`,
     `n_surrogates=200`, `n_restarts=5`, and the dead-ROI roster applied first.
     **The roster matters** — use `IF2_DROI_CSV`-equivalent selection from
     `2R/2026-08-15/long_window_20_strict_ROI/`, not the quarantined 2026-07-13 vintage.
2. **Wire it into a tool** — `tools/modularity_null.py --store <store> --stream <fast|slow>`,
   writing the same columns so `tools/make_modularity_figure.py` reads it unchanged, and
   honouring `--exclude-file docs/learned/lab_excluded_slices.txt`.
3. **Repoint the report.** `docs/assembly_report.md` currently attributes modularity to the
   interface2 pipeline. Once the port is validated, the report should cite the in-repo
   instrument and keep the MATLAB numbers as the cross-check. **Then murderboard it** — the
   documents are already at round 4 in
   `docs/reviews/assembly_summary_2026-08-19.md`; append round 5.

## One bug already caught, before it could look like a porting mismatch

Sapper **SAP001** blocked the first commit: `np.percentile` matches no MATLAB `prctile`
mode, and the surrogate threshold `q_hi` is a MATLAB `prctile(qs, 95)` in the reference.
Now uses `matlab_prctile` from `detectors/_shared`. Left un-caught it would have shifted
every `above_null` verdict slightly and read as a porting error in step 1.

## Two traps waiting in step 1

- **Louvain is stochastic and best-of-N is upward biased.** Observed and null must use the
  same N or the comparison is rigged toward finding structure. `louvain()`'s docstring says
  so; a validation that changes N on one side only will look like a porting bug and is not.
- **The reference's `above_null_Q` counts untested recordings as 0** — that is the defect
  found today. The port returns `defined=False` instead. So a straight column-to-column diff
  will disagree on exactly those 5 recordings (1 fast, 4 slow, all 3–5 active cells), and
  **the port is right there**. Expect it; do not "fix" it.

## Not blocked on anything but CI

No shared resource is held. MATLAB has exited. The darkroom claim is released
(`docs/SESSIONS.md`, `Mac/modularity-on-fast` DONE). interface2 branch
`bct-modularity-fast` is pushed to GitLab, unmerged, and now has nobody to merge it —
its `IF2_DROI_CSV` override is what makes that pipeline runnable at all.

**Delete this file when the port lands.**
