---
status: open
filed: 2026-08-15
---

# A zero-event ROI is not a dead ROI, and the verdict is not bugarach's to compute

**If you are about to filter, drop, or characterise ROIs that produce no events,
stop and read this.** Two sessions reached this question on 2026-08-15 and one of
them got it wrong twice in a row before finding the answer, which already existed.

## The lab has a normative spec, and it is not "silent in baseline"

`fireflies` [`decisions/0002-dead-roi-rejection-spec-for-matlab-port.md`][adr2]
(@ `691ae62`, 2026-07-16, status ACTIVE). The criterion, §4.3:

```
rejected = base_empty AND drug_empty AND (hik_present ? hik_empty : TRUE)
```

An ROI is dead only if it is silent at baseline **and** at drug **and** — where a
high-K⁺ depolarisation test exists for its slice — silent under that too. High K⁺
is the positive control that proves the ROI *can* fire. Baseline silence is one
of three conjuncts.

The spec is unusually trustworthy: §0 records that it was re-implemented from its
own prose with deliberately different mechanics and diffed against the
authoritative R, **identical on every row and column**.

## The numbers are an order of magnitude apart

| quantity | value |
|---|---|
| ROIs **rejected as dead**, `ROI_revised_2v` (ADR 0002 §7.1) | **66 of 2185 = 3.0%** |
| ROIs with **no events in a baseline window**, measured here | **~35%** |

These answer different questions and must never be swapped. ⚠ Whether bugarach's
`processed_archive/event_store_onset_revised_2v` is the same corpus as fireflies'
`ROI_revised_2v` is **not verified** — the `revised_2v` vintage matches, the
extraction path may not. Do not quote the 3.0% as bugarach's number without
checking that first.

## Three traps, all of them already documented upstream

1. **Do not recompute a verdict per stream.** ADR 0002 §2: the verdict is computed
   **once** on the custard stream (≈ fast + slow) and applied to every other
   stream by key. *"Recomputing per stream would give FAST an impoverished signal
   and reject ROIs that are alive in SLOW"* (ADR 0001). A session here compared
   fast-silence against slow-silence as if they were independent verdicts; that
   comparison is the error the spec exists to prevent.
2. **Do not drop zero-event ROIs to "clean up" a distribution.** `freq == 0` is a
   **valid value**, not a missing one — ADR 0002 §3.5 makes EMPTY a first-class
   row state with its own integrity invariant, and fireflies keeps empty ROIs in
   frequency models for exactly that reason. Dropping them conditions the result
   on the ROI having fired, and fireflies flags that conditioning as carrying a
   **group-dependent** skew. ⚠ That skew is explicitly labelled by fireflies as *a
   hypothesis they asked others not to build on* — so treat it as a live risk, not
   an established effect. Either way FOUNDATIONS §9 already forbids a pooled
   number that hides a group-dependent sign change.
3. **Selection is not the analysis layer's decision.** Tony to fireflies,
   2026-08-10: *"the CSVs do not carry enough information for fireflies to do the
   filtering"* — selection belongs upstream, with the exporter. bugarach inventing
   an activity threshold would repeat, one repo over, the thing fireflies is
   being told to stop doing.

## What bugarach should do instead

**Keep every ROI the exporter delivers, and say what was actually measured:**
*"ROIs with no events in this baseline window"* — a property of the window, not of
the cell. Never "silent ROIs", never "dead", never a viability claim.

The dead-ROI verdict is **not computable here at all**: it needs drug and high-K⁺
rows, and FOUNDATIONS §9 restricts this repo to baseline windows. So there is
nothing to port and no threshold to pick.

**This costs the generator critique nothing**, which is worth knowing before
anyone tries to rescue it. The six detectors count *distinct coactive ROIs out of
the population the exporter hands them*, and that population contains ROIs
contributing nothing. Whether those are dead cells or quiet cells is irrelevant
to a benchmark — what matters is that the detector's effective population is
smaller than its ROI count while the generator's is not. See
[`2026-08-14-generator-background-model-is-flat.md`](2026-08-14-generator-background-model-is-flat.md).

[adr2]: https://github.com/syncytium2/fireflies — `decisions/0002-dead-roi-rejection-spec-for-matlab-port.md`; a local clone is the reliable route (`fireflies` @ `691ae62`).
