# Handoff — two things in flight, 2026-08-19

**Two sessions are mid-task and this file carries both.** They are unrelated: one measured
synfire order and is undecided about its interpretation; the other is porting the modularity
instrument into this repo and stopped for a CI upgrade. Each section says who owns it and
what "finished" would mean. **Delete only your own section.**

---

# A · synfire order — measured, interpretation open

**Everything is landed on `main`. Nothing uncommitted, no branch waiting.** This exists
because one measurement is finished and its interpretation is not.

> **The assembly question is closed and is not mine to summarise.** Another session ran the
> three closing steps and superseded my numbers. The statement of record is
> `docs/assembly_report.md` with its run record at
> `docs/reviews/assembly_summary_2026-08-19.md`. Do not read the older assembly figures in
> commit messages before `dc10189`.

---

## What was measured

**SPIKE-order** (Kreuz, Satuvuori, Pofahl & Mulansky 2017, *New J. Phys.* 19:043028) over
the 84-recording baseline corpus, both streams, via PySpike's implementation by the same
authors. Tool: `tools/synfire_scan.py`. Results:
`<darkroom>/bugarach/synfire_{fast,slow}_relabel.json`.

This asks a **different question from assemblies**: not *which* cells take part, but
*which follows which* — whether the same units repeatedly fire from leader to follower.

| | above its own null (p<0.05) | median indicator |
|---|---|---|
| fast | **23 of 80** (29%) | 0.036 |
| slow | **44 of 82** (54%) | 0.099 |
| generated control, no order planted | **3 of 40** (8%) | 0.101 |

**There is leader–follower order in these recordings, above chance.** The control row is
what makes that a claim: `simulate.py` places each event's onsets as independent jitter
around a common time, so there is no order to find, and the test does not find it.

## The lesson that cost the most

The first run used this project's standing surrogate — per-ROI circular shift. **On the
order-free control it called 60% of recordings significant, higher than the real data.** A
circular shift destroys the coordinated events themselves, so any recording that *has*
events beats it regardless of order. It was answering "is there coordination", already
settled.

The replacement keeps every spike time and permutes **which ROI owns each spike** —
pooled event structure and per-ROI counts held fixed, cell-to-latency assignment destroyed.
False-positive rate 8%.

**This is the second measure in two days to need that fix**, the assembly work being the
first, with the same null answering the same wrong question. **Assume any new measure on
this corpus needs an event-preserving null until shown otherwise**, and run the order-free
generated control *before* believing any number.

**A second instance of the same class, found by the session that closed the assembly
half:** the modularity instrument was hardcoded to the `slow` stream, and a report had been
asserting a fast-stream absence that nobody had ever measured. Different mechanism, same
shape — the number was not measuring what the sentence above it claimed. Before quoting an
absence, check which stream, which recordings and which parameter the instrument actually
ran on. Both failures this week were invisible in the output and visible only in the
control or the call site.

## The group question — open, and the honest status is "not established"

- **fast:** does **not** survive the corrected null. chi-square p = 0.40.
- **slow:** survives, DI 16/17 · MALE 16/22 · OVX 6/18 · ORX 6/25, and — unlike the
  assembly claim — **survives permuting group within spike-count strata, p = 0.0004**.

Three reasons it is still not quotable:

1. **The magnitude shows no group gradient.** Median indicator DI 0.087, MALE 0.137,
   OVX 0.083, ORX 0.093. What differs by group is whether a recording beats *its own* null,
   not how ordered it is.
2. **Coarse strata, small cells.** Top spike tercile is DI 12/12, MALE 9/9, OVX 2/5,
   **ORX 2/2** — ORX at n=2 cuts against the intact-versus-gonadectomized reading.
3. **The indicator is strongly anti-correlated with spike count** (fast rho −0.75, slow
   −0.40), so raw values are not comparable across recordings of different richness. Only
   the per-recording verdict is.

**It converges with the connectivity effort**, which also finds its group effect in slow
and treats fast as a negative control. Two independent measures agreeing on which stream
carries group structure is worth something; neither is evidence about the other's mechanism.

## What closes it

1. **Rate-matching and node-matching**, not coarse terciles — `darkroom/murmuration/
   connectivity_handoff.md` documents how that work did both for its own result. This is
   the step between "survives stratification" and quotable.
2. **Re-run on the penumbra-subtracted store.** Optical crosstalk between neighbouring ROIs
   produces apparent latency structure, and the relabel null cannot remove it. The assembly
   work found crosstalk inflates its own measure without accounting for it, so expect the
   same here.
3. ⚠ **Check the exclusion question against this run.** Another session found the lab's
   `exclude=1` recordings were reaching analyses that believed they were filtered
   (`docs/todo/2026-08-19-lab-exclusions-were-never-consulted.md`). The synfire scan reads
   the same export folder and inherits whatever that folder does. **I have not verified
   which recordings it included.** Do that before quoting any count above.

## Two PySpike traps, both hit here

- **`optimal_spike_train_sorting` returns an unnormalized value and calls it the synfire
  indicator.** It builds the directionality matrix with `normalize=False`; on the first
  recording tried it returned 324 where the indicator is 0.021. The indicator is
  `spike_train_order` on the *sorted* trains. Both are in the JSON, the raw one only so a
  cSPIKE cross-check has something to match.
- **The sort is simulated annealing with no seed.** interface2 hit the MATLAB equivalent
  (`SYNCHRO_PROGRESS.md`). The tool takes the best of `--restarts` optimisations and seeds
  numpy per recording so a rerun reproduces.

## Related, filed

- `docs/todo/2026-08-19-synfire-measured-and-what-it-cost.md` — this result in full.
- `docs/todo/2026-08-18-synfire-order-is-not-the-assembly-question.md` — why the question is
  distinct, with the Kreuz papers now in `01-lit/` and cSPIKE v1.3 confirmed to ship
  SPIKE-order if a MATLAB cross-check is wanted.
- **syncytium2/murderboard #19 and #21** — two process changes still open and waiting on a
  person; that repo has no CI, so merging is a manual act.

---

# B · porting modularity into bugarach — PAUSED, unvalidated

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
