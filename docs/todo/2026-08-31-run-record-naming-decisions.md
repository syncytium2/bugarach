---
status: waiting-on-tony
filed: 2026-08-31
---

# Run-record naming: four decisions, and a prior-art pass nobody ran

waiting: Rule the four items in `docs/run_records.md` — they amend ADR-0005 and land in a contract two other teams read.

**Read [`docs/run_records.md`](../run_records.md).** This file is the queue entry; that
one is the content.

## Why it is waiting rather than open

The names land in `detections.csv`, which interface2 and fireflies both read. Changing
one afterwards is an announced spec revision across three repos — the same position
`cicada` is in, where the key can never move because two consumers parse it.

## The short version

A design conversation on 2026-08-31 converged on a shape for run records. Most of it
was **already decided** by [ADR-0005](../adr/0005-detectors-and-models-are-objects-in-a-folder.md)
on 2026-08-29 — the `runs/<id>/` layout, `fitted_on` / `trained_on` / `scored_on`,
`detector versions`, and Chromium as the super-user target. Tony spotted it in the
moment: *"reinventing the wheel. cfar all over again."* He was right and the wheel was
his own, two days old.

What the conversation added, and what needs ruling:

1. **`detector` absorbs the nets** at the emitting boundary — Tony's proposal, and it
   cuts against ADR-0005's two-folder split, which exists for a reason (weights have a
   trainer provenance a knob sweep does not).
2. **A genus word for fitting** — `fit` or `opt`, with `calibrate` and `train` as the
   species that already exist in the tree.
3. **Two run ids, where ADR-0005 has one.** A detect run consumes many fit runs, so one
   id cannot express *detecting today with settings fitted last month*. This is the
   substantive gap.
4. **Whether a detector version is addressable in the registry** (`rate@v1` runnable
   beside `rate@v4`) or only recorded in provenance.

## The item that is not Tony's to rule, and has not been done

**No prior-art pass has been run.** Experiment tracking, run provenance and
settings-versioning are a developed field, and this project has already discovered
once that reasoning its way somewhere is no evidence nobody is there — `rate_detect`,
`coact_detect` and `loco_detect` reconstructed CFAR unknowingly
([`detector_history.md`](../detector_history.md) §4). Three groups to cover: the
experiment-tracking tools, the provenance vocabularies, and the neuroscience-specific
data standards — the last because that is where this lab's collaborators may already
be reading files.

Adopting someone else's vocabulary would be the better outcome and would make decisions
1–4 mostly moot. **Do this before building, not after.**

## What happens when it is ruled

An accepted ADR is amended by another ADR. If 1–4 land they land as ADR-0006, and
`docs/run_records.md` retires into it.

## What must not happen meanwhile

**Nothing gets built against these names.** They are provisional in both directions —
Tony has not ruled, and the prior-art pass could replace the whole vocabulary.
