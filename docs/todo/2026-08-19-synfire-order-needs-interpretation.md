---
status: open
filed: 2026-08-19
kind: measurement done, interpretation open — needs a person
---

# SPIKE-order is measured; what it means is not settled

> **This was `HANDOFF.md` at the repo root until 2026-08-20**, moved here without a word
> changed below it. A handoff file on `main` means *work is in flight and a session
> stopped mid-task* — the signal CLAUDE.md asks the next session to read. This file says
> the opposite in its own second line: everything landed, nothing uncommitted, no branch
> waiting. It was a finished measurement waiting on a judgement, which is what
> `docs/todo/` is for. Left at the root it made the in-flight signal permanently true and
> therefore worthless, and opened a public repository's file list with the word "Handoff".

> The modularity port that shared this file is **done** — landed, validated, and its
> section removed. Only synfire is still open.

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
