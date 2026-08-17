---
status: open
filed: 2026-08-17
for: a session doing nothing but literature
---

# Literature deep dive — establish whose feet we are standing on

The report at `docs/learned/coordination_report.html` claims, in section 3, that no
prior work trains a network to emit coordinated population events scored against
planted ground truth. **That claim is four web searches deep and no paper was read in
full.** It is stated honestly on the page, and it is not good enough to build a
manuscript, a grant paragraph or a priority claim on.

This handoff exists so the next session can close that gap without repeating the
shallow pass. Read the report's section 3 first; it is the current state, and its
reference list is the starting bibliography rather than the answer.

## The question, stated so it can be answered

Not *"has anyone used deep learning on calcium imaging"* — many have, and the report
says so. The question is positional:

> **Has anyone trained a model whose OUTPUT is the coordinated population event
> itself — a time interval, scored against known events — rather than a per-cell
> spike train, a latent trajectory, or the parameters of a classical detector?**

Four sub-questions, each independently answerable:

1. **Output type.** Does the method emit discrete population events with times?
2. **Supervision.** Is it trained, and on what ground truth — electrophysiology,
   human labels, or simulation?
3. **The corpus.** Is the training data parameterised from the lab's own recordings,
   or is it a generic benchmark?
4. **The comparison.** Is it scored against hand-written coordination detectors on
   the same data?

A hit on all four is prior art. A hit on 1 and 2 alone is close enough that we must
cite it and position against it.

## What the shallow pass found, and what it did not check

| claim from the shallow pass | how it was established | what a deep dive must do |
|---|---|---|
| Per-cell spike inference is thoroughly learned (CASCADE, DeepCINAC, spikefinder entrants) | abstracts + publisher metadata | confirm none of them emits a population-level event; check DeepCINAC's companion tooling, which is closest to our problem because the Cossart lab does SCE and assembly work downstream of it |
| Population-level learning targets dynamics, not events (RADICaL) | abstract | read it; confirm no discrete-event output and no event-level scoring |
| Assembly/synchrony detection is unsupervised everywhere found | **abstract and method list only — this is the load-bearing gap** | read Mölter/Avitan/Goodhill's benchmark in full; enumerate every algorithm it compares and confirm none is trained. Then follow its citations forward |
| autoMEA learns the knob, not the detection | search summary | read it; confirm the network's output is MaxInterval parameters and not burst calls |

## Where to look that the shallow pass did not

- **Forward citations** of Mölter, Avitan & Goodhill 2018 (*BMC Biology* 16:143) and
  of Russo & Durstewitz 2017 (*eLife* 6:e19428). Anyone who built a learned assembly
  detector almost certainly cites one of them.
- **The MEA / electrophysiology side**, which is where "network burst" is the same
  problem under a different word. autoMEA came from there; there may be more.
- **Adjacent fields with the identical shape**: seizure and interictal-spike
  detection from EEG, and sleep-spindle detection — both are "find a coordinated
  transient in a multichannel record", both have heavy supervised-learning
  literatures, and a method there may be transferable enough to count as prior art
  in spirit even if the substrate differs.
- **Preprints.** bioRxiv is where this would land first, and a 2025–2026 preprint
  would not be in a citation graph yet.
- **Software rather than papers.** A learned detector may exist as a package with no
  paper (CaImAn / Suite2p ecosystems, lab-specific GitHub). Search code, not only
  literature.

## What would make the novelty claim real, and it is not more searching

Two things, in order of value:

1. **Run a literature method on our corpus.** The report's comparison is against six
   detectors ported *here* plus our own networks. Tony's reading — "competes with
   state-of-the-art models from the literature" — **is not currently supported**,
   because no literature model has been run. CICADA is the one published method in
   the field of play, and beating a port of it on our own simulated corpus is a
   weaker claim than it sounds. Pick two or three from Mölter's benchmark set (ICA
   and a graph or item-set method are the obvious picks; several have reference
   implementations) and put them through `tools/fair_bakeoff.py` under the same
   fit-and-score procedure. **That converts an absence-of-evidence claim into a
   measured one**, and it is the single highest-value item on this page.
2. **Then** decide whether the remaining novelty is the architecture, the
   per-lab-corpus loop, or only the combination. The report's own verdict is that no
   individual component is novel — centre−surround is a difference-of-Gaussians,
   dilated convolutions are standard, training-on-simulation is what CASCADE does one
   level down. If the deep dive holds, what is new is putting them at this level of
   the analysis, and that is a narrower and more defensible claim than "a new
   detector".

## Traps

- **`fetch_paper.py` is deliberately not vendored here** — it carries a personal
  library path that SAP004 blocks and this repo is public. See
  `docs/todo/2026-08-12-vendored-lit-tool-carries-personal-paths.md`. Fetch by hand.
- **PMC and Springer are behind a bot check** in this environment; that is what
  stopped the shallow pass. Publisher pages, bioRxiv PDFs and HAL/institutional
  mirrors did work. Try those first rather than re-discovering the wall.
- **Do not verify a claim against a half-remembered paper.** The shallow pass caught
  itself inventing an author list for autoMEA — the murderboard's role 2 found it.
  Get the text or flag the paper.
- **Terminology fragments across fields.** The same object is called a synchronous
  calcium event (SCE), a cell assembly, a network burst, a population event, a
  coactivation, and a coordinated event. A search that uses one term finds one field.

## Deliverable

Update the report's section 3 in place — it is built from
`docs/learned/coordination_report.src.html`, so edit the source and rebuild with
`tools/build_learned_report.py docs/learned/coordination_report.src.html`. Replace the
positional table with what the full texts say, keep the ⚠ on anything still unread,
and either strengthen the verdict or retract it. Then re-run the murderboard on the
rebuilt page: role 2 is the one that matters here and its standard is zero tolerance
for a citation nobody opened.
