# Handoff — the assembly question, 2026-08-19

**Everything below is landed on `main`. Nothing is uncommitted, no branch is waiting.**
This file exists because the *question* is not finished, not because code is in flight.

> ⚠ This handoff has **not** been through a murderboard. Every number in it was verified
> during the session it summarises, but the document itself got a single-pass self-check,
> not the eleven roles. Do not treat it as reviewed.

---

## The answer

**There are no discrete recurring cell assemblies in this preparation, and the absence is
the result.** Two instruments, independently:

| what was asked | instrument | verdict |
|---|---|---|
| are there groups of cells more coupled to each other than to the rest | BCT **modularity** on the STTC graph (`darkroom/murmuration`, 2026-07) | **no structure above null** — 3% ROI, 1% penumbra-subtracted |
| is *who participates* explained by how often each cell fires | curveball + uniform nulls on membership (`bugarach.assembly`) | departure from uniform in **27 of 48** fast recordings, **27 of 38** slow, against **2.5%** on matched synthetic controls |

They do not conflict. Co-participation variance above rate, with **no modular partition**,
is a **core–periphery** field: a few cells in most events, a long tail in few. That is
weaker and more ordinary than "assemblies", and it is what the evidence supports. **Drop
the word "assembly"** unless the modularity result is overturned.

## What is settled — do not re-derive

- **The group difference is withdrawn.** Planting the *same* six-ROI assembly at each
  group's median event count reproduces the whole gradient: simulated 0.74 / 0.68 / 0.64 /
  0.21 against observed 0.71 / 0.64 / 0.45 / 0.17. It was detection power. It was also a
  **fast-stream** claim, and the connectivity work independently treats fast as a negative
  control (it fails rate-, node- and Δt-matching). The real group effect is **slow** and
  belongs to that project.
- **Do not run BCT graph metrics.** `decisions/0011` records them as redundant with
  `meanSTTC` (strength ρ 0.995); modularity, the one metric carrying independent
  information, fails node-matching at p=0.098. Tested, not argued.
- **"PCA/ICA would score nothing on our corpus" is false.** Run at our geometry, PCA
  against a Marchenko–Pastur bound flags essentially every simulated recording — the
  coordinated events violate its independent-neurons null. The real reason not to port one
  is that the corpus cannot reward **membership recovery**.

## What closes it — three bounded steps, in order

1. **Re-run `tools/assembly_power.py` with `AssemblyResult.verdict()` as the decision
   rule**, per recording, at this corpus's own cluster counts. Today's power figures were
   computed at α=0.05, one statistic, one null, 20 slices combined by Fisher — while
   recordings are scored at α/2 across two statistics under both nulls, per recording. A
   negative is only a result if the test could have failed, and that is the missing proof.
2. **Re-run the measurement on the penumbra-subtracted store.** Optical crosstalk between
   neighbouring ROIs is the largest unchecked alternative and the null cannot remove it.
   The store exists — `darkroom/murmuration/pensub/`, 85/85 slices — behind three
   environment variables (`IF2_ONSET_STORE`, `IF2_DROI_SOURCE`, `IF2_OUT_SUB`). If the
   departure collapses there, the answer is crosstalk and the negative is complete.
3. **Reframe the report to lead with the negative.** It currently opens on the positive
   fragment and files the absences as caveats and withdrawals. Tony, 2026-08-19: *"the lack
   of assembly is a result, just like the lack of 'connectivity'."* He also found the
   present framing unclear on first read, which is independent reason to redo it.

## Where things are

- **Report** — `<darkroom>/bugarach/assembly_report.html`, self-contained, both figures
  embedded. Repo copy at `docs/learned/assembly_report.html`.
- **Figures** — `assembly_membership.png` (membership matrices), `assembly_answer.png`
  (verdict vs event count, the two-null control, the K sweep), `assembly_power.png`.
- **Run record** — `docs/reviews/assembly_report_2026-08-18.md`, eleven roles, roster gate
  passing. Read it before trusting any claim in the report; it lists what was withdrawn.
- **The question** — `docs/todo/2026-08-18-do-real-slices-have-recurring-assemblies.md`
  carries the answer at the top.
- **Sister effort** — `darkroom/murmuration/connectivity_handoff.md`. Its "START HERE" box
  supersedes the body; several passages below it are retracted and marked.

## Open, waiting on a person

- **syncytium2/murderboard #19 and #21** — two process changes from this session's review
  (check the sources a deliverable did *not* consult; name the chart type an image
  resembles). Both `CLEAN`. That repo has **no CI**, so `merge_when_green.sh` will refuse
  them by design — merging is a manual decision. Two other PRs (#18, #20) are someone
  else's and touch the same file; whoever merges last needs a rebase and a re-run of
  `murderboard_roster.sh count`.
- **Papers to fetch** — `docs/todo/2026-08-18-synfire-order-is-not-the-assembly-question.md`.
  Synfire order is a *different* question from assemblies and a cheaper port than PCA/ICA,
  since this repo already ships a cSPIKE-validated measure. The Kreuz/cSPIKE/PySpike PDFs
  are not in the Dropbox library; the todo asserts no bibliographic detail nobody verified.

## Two cautions for whoever picks this up

- **The event/onset contract moved twice after this work landed** (PRs #126, #127). The
  membership tables are built on onset times, so if the definition of where an event *is*
  changed, they inherit it. Diff those before quoting the report's numbers again.
- **A figure that borrows a familiar chart's grammar gets read through it.** The leading
  figure was drawn as scattered marks and read as a spike raster — wrong axes, confidently
  — and eleven review roles passed it. It is a tile matrix now. The general form is
  murderboard #21.
