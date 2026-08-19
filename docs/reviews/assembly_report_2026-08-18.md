# Murderboard run — the assembly report

## The problem this run found

A report was drafted saying the four experimental groups differ in whether their
coordinated events recruit recurring sets of cells — DI 9 of 10 animals down to ORX 1 of
6, p = 0.017. It was internally consistent, every number reproduced from the run files,
and it was wrong.

**Planting the same six-ROI assembly into each group's median coordinated-event count
reproduces the entire gradient:**

| planted at | simulated hit rate | observed |
|---|---|---|
| DI-like, 38 events | 0.74 | 0.71 |
| MALE-like, 27 events | 0.68 | 0.64 |
| OVX-like, 32 events | 0.64 | 0.45 |
| ORX-like, 10 events | 0.21 | 0.17 |

The groups never reached the test on equal terms. DI contributed 17 of 17 recordings and
ORX 6 of 25, and among the survivors ORX held a median of 10 coordinated events against
DI's 38. What the report had measured was how much coordination each group has, not
whether that coordination has recurring membership.

The claim is withdrawn. Three independent checks agree: permuting group within
event-count strata gives p = 0.16, scoring per recording rather than per animal gives
p = 0.11, and the "any recording counts the animal" rule gave the groups unequal exposure
because ORX animals contribute one testable recording each and DI animals up to three.

**The ORX result was the inverse of what it was read as.** Constructing the failure the
claim denies — a compact assembly in *every* ORX animal at one event in ten — predicts
1.7 of 6 animals flagged. One was observed. For three of the six, detection power is
0.03–0.07, indistinguishable from the false-positive rate. The number could not have
moved, so "close to absent" was unsupported in the direction it was read.

## Where this fits

This was the first full murderboard on this line of work, run with eleven subagents
rather than a single pass. The single-pass run earlier the same day, on the figure alone,
found real defects — a missing legend, a pooled number FOUNDATIONS §9 does not admit —
and found none of the above.

The difference is not diligence. It is that four roles reached the confound down four
different paths and none of them had the others' findings: the claim verifier recomputing
denominators, the consistency auditor noticing the table's denominators were *testable*
animals, the adversarial reviewer constructing the failure the claim denied, and the
methods reviewer simulating the confound directly. A single reviewer holding all eleven
checklists has one chance to see it.

## What would validate this, and what generalises

**Inside this project.** Match on coordinated-event count before comparing groups —
subsample every membership table to a common number of events, or model the count. Until
then group and detectability are not separable in this corpus. The spatial-adjacency
check is the cheapest way to remove the most likely alternative explanation for the
corpus-level result that survives.

**Beyond it.** Two things transfer. The first is a warning about a specific practice: an
"any unit counts the group" aggregation rule silently weights groups by their exposure,
and here that manufactured roughly 16 points of gradient before any biology. The second
is about this process — the report already carried both halves of a can-it-fail control,
generated negatives and saturated positives, and still shipped a claim whose alarm could
not ring. **Building both controls is necessary and was not sufficient**; what caught it
was constructing the specific failure the specific claim denied, and walking that one
instance through the metric as computed.

Three changes went upstream to the murderboard from this run
([syncytium2/murderboard#19](https://github.com/syncytium2/murderboard/pull/19)): check
the sources a deliverable did *not* consult; treat "the breakdown is unavailable" as a
claim to be verified; and recognise that a verification step the deliverable performed
can itself be incapable of failing.

---

## Appendix — run record

- upstream:  syncytium2/murderboard @ 57445b4
- vendored:  57445b4
- freshness: current (gate exit 0)
- artifact:  `docs/learned/assembly_report.html` (`02b4c68` → rebuilt)
- figures:   `<darkroom>/bugarach/assembly_membership.png`, `assembly_answer.png`
- roles:     11 of 11 run, as parallel subagents
- rounds:    1 blind verify round on the rebuilt page

### Role ledger

| # | Role | Findings | Note |
|---|---|---|---|
| 1 | Claim & data verifier — "Prove It." | 17 | claim ledger of 36 rows; found the corpus-size error, the membership-figure denominator artifact, and the K-sweep failure |
| 2 | Citation & reference validator — "DOI or Die." | 11 | implemented PCA/Marchenko–Pastur and disproved the "they score nothing" claim; supplied the reference list the report now carries |
| 3 | Consistency auditor — "Cross-Examiner." | 23 | pinned the canonical counting basis; found the denominators were testable animals and that testability ran with the outcome |
| 4 | Adversarial reviewer — "Reviewer 2." | 20 | constructed the ORX failure case; found the two-null apparatus contributes nothing on this corpus |
| 5 | Line editor — "Kill Your Darlings." | 46 | found `--store` contradicting "no store", the dangling antecedents, and the bolded least-supported number |
| 6 | Methods / domain expert — "RTFM." | 11 | the decisive confound simulation; verified curveball against Strona 2014 and Carstens 2015, measured chain mixing, ruled out onset double-counting |
| 7 | Reuse auditor — "Reinventing the Wheel." | 11 | found the report builder forked `md_to_page.py` and dropped the page wrapper; four constants duplicated across files |
| 8 | Naive-reader accessibility — "You Lost Me." | 21 | eight sections blocking; no preparation described, group codes and streams unexplained |
| 9 | Density & figure-first — "Show, Don't Tell." | 7 | measured the baked-in figure text at 31% and 40% of image height; specified the null-model schematic |
| 10 | Build & craft gate — "Ship It." | 13 | three exact colour collisions, four key words below WCAG AA, clipped axis label, figure predating its generator |
| 11 | Argument order — "Start With the Problem." | 4 | the power section arrived after the results it licenses |

### What was fixed

**Withdrawn or restated:** the group difference; ORX as evidence of absence; "survives at
every K" (the group test is significant at K=3 only: 0.017 → 0.262 → 0.120 → 0.788); the
membership figure's cross-panel comparison; "they score nothing"; the blind spot as a
general methods result; every power-exclusion number.

**Corrected:** corpus size 85 → 84, dates 48 → 42 animals 44; the χ² replaced by an exact
test; the pooled figure quoted on the same basis as the table; "every testable recording";
the Jeffreys interval named; the control false-positive rate given as a measured
2.5% [1.1–5.1%] rather than "none of 40", which was a property of one seed.

**Craft:** page wrapper restored so the text has a measure; figure captions moved out of
the rasters into live document type; colour keys added as live text; two disjoint colour
families so no hex means two things; contrast raised to AA; device-pixel-ratio 2; clipped
label fixed; code block no longer scrolls the page sideways on a phone.

**Added:** the preparation described in the first sentence; group codes expanded; the two
streams named; the decision threshold, statistics and surrogate count stated in the text;
optical crosstalk added as the first failure mode; a reference list.

### Residual ⚠

- **The fast/slow kinetic boundary is undefined** in this project's glossary and in the
  group-level foundations. The report says so rather than inventing one. Worth its own
  todo.
- **Spatial adjacency is unchecked.** Optical crosstalk between neighbouring ROIs would
  produce co-participation beyond rate, and the fixed-margin null cannot remove it. This
  is the most likely alternative explanation for the surviving corpus-level result.
- **Colwell & Winkler (1984)** is cited at one remove via Ulrich et al. (2017); the
  chapter itself was not read.
- **Kallio (2016) reports fixed-margin nulls becoming *liberal* under limited
  randomizability**, where this work measures power falling to chance. Both may hold in
  different corners; the disagreement is unresolved and is flagged in the report.
- **The controls are generated at one geometry.** Thin recordings are not represented,
  though a separate check at four clusters put the false-positive rate at 0.02.
