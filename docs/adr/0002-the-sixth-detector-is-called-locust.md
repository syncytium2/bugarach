# ADR-0002: The sixth detector is called locust, not CICADA

## Status

Accepted, 2026-08-24, by Tony. Changes **the name a person sees** and nothing a
file contains — the `cicada` key survives everywhere it is an identifier,
including the `detector` column of `detections.csv`, which is output contract.
The split and its cost are in
[`docs/todo/2026-08-24-the-identifier-still-says-cicada.md`](../todo/2026-08-24-the-identifier-still-says-cicada.md).

## Context

An attribution audit from interface2 arrived on 2026-08-24 and closed the
lineage of all six detectors. Tony ruled on the general question the same day:

> *"I don't think anyone is going to jump on us for a technique used in radar
> analysis from 1968. In fact I feel most researchers would be kind of thrilled
> with the link. We acknowledge its origins, don't worry about finding the lit
> after we built it, it's a tool and it's useful."*

**That ruling closes priority, and it does not reach this one.** The other five
detectors are cases of *arriving somewhere the literature already was* — a good
story, a citation, and no further obligation. The sixth is different in kind:

- It is a **port of a specific, living lab's named software** — the Cossart lab's
  CICADA, MIT-licensed, whose copyright notice this repo already carries.
- It is a **modified** port, in two ways that change what it detects — and both
  are changes to what it is **fed**, not to what it computes. It is fed the events
  the folder already contains rather than running CICADA's own transient
  detection, and it is fed a per-event duration rather than measuring the whole
  transient the way the original does: on slow transients a median ~4.6 s of
  duration-overlap swamps onset synchrony, so the exporter sends the **rise
  interval** instead. *(That the truncation is the exporter's, and not this
  code's, is the 2026-08-28 addendum below — this bullet was read the other way
  twice before it said so. Since 2026-08-29 the code cannot do it either:
  `rise_durations()` refuses and sapper SAP012 blocks the arithmetic.)*
- The name was **on a public website**, in a lane label, a scoreboard column, a
  help panel and every figure legend.

interface2 states the principle as its ADR-0016 — *"we can't say we used it if we
turned off half of it"* — and asked for `"CICADA-derived (modified)"`.

## Decision

**The detector is called `locust`.**

Tony chose it over `CICADA-derived (modified)`, which keeps the original's name
as the root of ours and which readers compress back to "CICADA" in speech, and
over `cicada-like`, for the same reason. A distinct name cannot be misread as a
claim to be the other lab's tool, and the citation goes where a citation belongs
— in the help panel, the README and the methods text, all of which now carry
Denis et al. 2020 with the two deviations stated.

It also fits: syncytium2's projects are already named this way (fireflies,
glowworm, murmuration, muster), and it retires `"CIC"`, the short row label Tony
noted on 2026-08-15 *"is not CICADA to anyone who has met the other CIC"*.

## What this is not

- **Not a claim that the method is ours.** The opposite: the rename exists so the
  citation can be unambiguous instead of implied by a borrowed label.
- **Not a code change.** No detector behaviour moves, no parity fixture changes,
  no operating point is touched. `cicada_detect` still computes what
  `generate_sce_cicada.m` computes, to 1e-9.
- **Not a contract change.** `detections.csv` still says `cicada`. A file written
  before this ADR and a file written after it are byte-identical.

## Consequences

- **The glossary carries the mapping**, because the split is the part that will
  confuse someone: *CICADA* means the upstream tool, *locust* means the detector
  here, and `cicada` is the key.
- **Every committed figure still draws the old label** until the regeneration
  pass in [RESET §5](../RESET.md) runs. The README says so under the hero figure
  rather than letting page and picture disagree silently.
- **interface2 asked to be told which way this went** so their docs and ours cite
  identically. That reply is owed and has not been sent.
- **`docs/FOUNDATIONS.md` names CICADA in §2 and §9** and was not edited — a
  session does not edit FOUNDATIONS (CLAUDE.md). Folding the rename in is Tony's.

## Addendum, 2026-08-28 — why the port needs a duration at all, and whose duration it is

Added at Tony's direction, in his account. The decision above names the rise interval as one
of the two modifications. That is true of the pipeline, and it has since been read as a claim
about the algorithm — twice in one day, on a public page and in a handoff. The constraint
behind it was never written down, so every reader reconstructed it and some reconstructed it
wrong.

**This project detects its own calcium events, and that is not a preference.** Calcium imaging
in KNDy neurons reveals **action-potential-independent** calcium events. External
event-detection algorithms cannot be relied on for them. The effort to establish whether any
can is under way in interface2, and is pending.

**What was taken from CICADA is the coordinated-event stage, and nothing else.** Its
calcium-event detection pipeline is not usable here without major effort, and this work is
under severe time constraints. So the coordinated-event detection was ported, and fed the
events this project had already detected.

**That stage requires an event duration, and this preparation's slow events break it.** The
slow events here are not described in the literature, and at full duration they destroy CICADA
fundamentally. The attempt to make it work truncates a slow event's duration to
`peak − t50rise` — and **that truncation is done on export, by the MATLAB team.** It is not a
step inside `cicada_detect`.

**So there is no duration decision for this project to make.** The imported duration is the
duration. In Tony's words: *"it is none of our business what the user decides to put in the
duration column of the import."* A `width_sec` arrives with the `width_def` that names the rule
which produced it (`../export_folder_spec.md`), the port paints each cell active for what it is
given, and **no webapp behaviour and no dev-team judgement depends on which rule that was.**

**What this changes about the decision above: nothing.** The rename stands, both deviations
stand, and the reasoning is untouched — a port fed another project's events, painting durations
another team defined, is a modified port. What the addendum settles is *where a reader locates
the second deviation*: upstream, in the export, not in the algorithm.

## Addendum, 2026-08-29 — the 1e-9 does not reach CICADA

This ADR's "What this is not" says `cicada_detect` still computes what
`generate_sce_cicada.m` computes, to 1e-9. That remains true and it is **not** a
validation against CICADA: the parity fixture is generated by running
`generate_sce_cicada` itself, so the number compares this repo to interface2 and to
nothing upstream of it. No output of either has ever been compared against CICADA's.

Two facts this ADR did not record, both of which strengthen the rename:

- **interface2 parked `generate_sce_cicada`** on 2026-07-07 for over-detecting on
  this preparation's long SLOW transients — a month before bugarach's port landed.
- interface2 *did* check its transliteration against upstream by reading code,
  function for function, on 2026-08-21 and found it matched. That is a
  correspondence check on the **unmodified** transliteration: not a measurement, and
  not a check of either deviation this ADR names.

**What this changes about the decision above: nothing** — it removes the last reason
anyone might have had to argue against it. The rename was defended on two
deviations; the parity number that was supposed to offset them never reached the
original. Chain and evidence: [`../detector_history.md`](../detector_history.md)
§6.3 and [the 2026-08-28 review](../reviews/locust_attribution_2026-08-28.md).

⚠ **FOUNDATIONS §2's "the ports are citable in place of the originals" now has a
per-detector exception**, for the same reason. A session does not edit FOUNDATIONS;
folding this in is Tony's.
