---
status: open
filed: 2026-08-18
---

# Synfire order is a different question from assemblies, and it is the cheaper port

The assembly measurement asks **who** takes part in each coordinated event. cSPIKE's
SPIKE-order work asks **in what order** they fire — whether the same units lead and the
same units follow, event after event, summarised as a synfire indicator. These are not
the same property and a recording can have either without the other.

Three questions about the same coordinated events, and this project answers one and a
half of them:

| question | measure | here? |
|---|---|---|
| how much co-firing | SPIKE-synchronization | **yes** — `detectors/sync.py`, ported from cSPIKE and cross-validated to 1e-9 against MATLAB *and* PySpike |
| which cells, repeatedly | assembly membership | **yes** — `bugarach.assembly`, 2026-08-18 |
| in what order, repeatably | SPIKE-order / synfire | **no** |

## Why it is worth doing, and why it is cheap

**The assembly measurement is order-blind by construction.** It collapses each
coordinated cluster to a set of participating ROIs and discards the onsets — even though
`assess._clusters` already gathers each participant's onset and computes their spread.
Any leader/follower structure in this corpus is untouched and has never been looked for.

**We already ported the sibling measure.** `detectors/sync.py` is a cSPIKE port validated
to 1e-9. SPIKE-order is the same lab, the same suite, and the same input representation
this project already produces — plausibly the cheapest published-method comparison
available, and cheaper than the PCA/ICA port
([`2026-08-17-run-a-literature-method-on-our-corpus.md`](2026-08-17-run-a-literature-method-on-our-corpus.md))
that has been the assumed candidate.

**And the benchmark cannot reward it either.** The generator plants each event's onsets
as jitter around a common time with no systematic order, so a synfire measure scores
nothing on our corpus — the same structural gap the assembly work found, on a second
axis. Whatever is decided about planting assemblies in the generator should decide about
planting order at the same time, or the second port hits the same wall as the first.

## What must not happen

The same mistake the assembly work nearly shipped: reporting a synfire score against a
corpus built to contain no order, and reading the zero as a fact about the method. See
[`2026-08-18-do-real-slices-have-recurring-assemblies.md`](2026-08-18-do-real-slices-have-recurring-assemblies.md).

## Papers needed — Tony has them or can fetch them at work

Searched the Dropbox on 2026-08-18: **no cSPIKE, PySpike, Kreuz or synfire PDFs**
anywhere under `01-lit/`, `01-lit/_autofetch/` or the darkroom. `01-lit/_NEEDED.md` does
not list them either. Nothing in this repo should characterise the method until someone
reads them — the assembly report shipped a claim about PCA/ICA that a reviewer disproved
by actually implementing it, and the lesson generalises.

- [ ] **Kreuz et al., SPIKE-order / spike train order and the synfire indicator**
  ("leaders and followers", quantifying consistency in spatio-temporal propagation
  patterns). This is the one that defines the measure.
- [ ] **cSPIKE documentation / manual** — the MATLAB suite's own description of the
  SPIKE-order API, which is what a port would be written against.
- [ ] **PySpike paper** (Mulansky & Kreuz) — already the reference for the ported
  synchronization measure and cited in `detectors/sync.py`, but the PDF is not in the
  library.

⚠ The bibliographic details above are from memory and are deliberately incomplete: no
year, journal or DOI is asserted here because none was verified this session. Fill them
in from the PDFs rather than from a search result.
