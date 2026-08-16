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

## The rule exists and has NOT been applied to the data bugarach reads

Tony, 2026-08-16, asked directly:

> *"the exporter (the data to be read by the webapp and detectors) should remove
> DEAD rois. We have a rule for that, but it has not been applied to the data you
> have access to."*

Two things follow, and they point in opposite directions — which is why this
section exists rather than a one-line note.

**The direction of travel is settled.** Dead-ROI removal belongs to the
**exporter**, not to bugarach, and the rule to apply is ADR 0002's, not an
activity threshold invented here. Nothing in the section below changes; this is
that principle being exercised by the person who owns it, not overturned.

**But the corpus in hand still carries them.** So every measurement this repo has
taken off `processed_archive/event_store_onset_revised_2v` was taken over a
population that includes ~3% of rows which are zero **by construction rather than
by biology**. That includes `bench.MEASURED_RATE_SHAPE` and
`bench.MEASURED_BURST_SHAPE`. The ⚠ above about corpus correspondence is now
*more* load-bearing, not less: if that archive is the `ROI_revised_2v` corpus,
3.0% is the contamination; if it is not, the rate is unknown.

### How much does that bend the fitted shape? Measured: almost none.

The obvious worry is that structural zeros inflate the low tail, and a Gamma
shape MLE is most sensitive exactly there. That worry was raised here and then
**tested, and it does not survive the test.**

Method: draw Gamma-Poisson count matrices at a known shape, 81 windows × 33 ROI
to match the real fit's geometry, contaminate 3.0% of rows with structural zeros,
and refit with `tools/fit_background_shape.py`'s own estimator (reused, not
re-derived). 20 replicates per cell.

| true shape | fit, clean | fit, +3% dead | bias |
|---|---|---|---|
| 0.275 | 0.286 ± 0.008 | 0.272 ± 0.008 | −0.014 |
| 0.450 | 0.466 ± 0.013 | 0.431 ± 0.016 | −0.036 |
| 0.800 | 0.825 ± 0.029 | 0.756 ± 0.018 | −0.069 |

Reproduce with `python tools/fit_background_shape.py --dead-roi-sensitivity`,
which needs **no data root** — the question is settleable on any machine,
including one that cannot open a store.

Contamination biases the shape **down** (toward more apparent skew) and the bias
grows with the true shape — but at the value actually in the tree it is small,
and it nearly cancels the estimator's own upward small-sample bias. Inverting:
an observed 0.275 on contaminated data implies a live-population shape of
**≈ 0.277**. Under 1%.

**So applying the dead-ROI rule should not move `MEASURED_RATE_SHAPE`
meaningfully, and no bench number computed against it is stranded by this.**
Recorded because the opposite was assumed out loud before it was checked, and
the assumption was more alarming than the truth.

⚠ Two limits on that result. It assumes dead ROIs are **missing-at-random with
respect to rate**, which is what a structural zero means — if dead ROIs are
preferentially segmented from dim or marginal fields, the contamination is not
random and this simulation does not cover it. And it assumes ~3.0%; the corpus
question above has to close before that rate can be relied on.

### A separate finding, free from the same run

The estimator carries an **upward small-sample bias of roughly 5%** at this
geometry (fitted 0.288 against a true 0.275; 0.836 against 0.800). That is larger
than the dead-ROI effect at the operating point and is nobody's fault — it is what
an 81 × 33 sample buys. Worth knowing before `--tol 0.05` is read as a drift
alarm: the estimator's own noise floor is about that size.

### Open, and with the people who can close it

**Tony is confirming the export function with the MATLAB team (2026-08-16).**
Until that lands, two things stay unknown and neither should be guessed here:
whether `processed_archive/event_store_onset_revised_2v` is the `ROI_revised_2v`
corpus, and whether the exporter that produced it will apply ADR 0002. When the
answer arrives, the actions are: re-run `tools/fit_background_shape.py` against
the filtered export and check the drift gate, and strike the ⚠ above.

Nothing in bugarach should change before then. The measurement above exists
precisely so that the wait is cheap — the expected correction is under 1%.

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
