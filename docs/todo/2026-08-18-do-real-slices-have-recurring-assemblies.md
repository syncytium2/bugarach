---
status: done
filed: 2026-08-18
revised: 2026-08-19
closed: 2026-08-19
---

# Do the real recordings have recurring assemblies, or random participation?

> ## CLOSED 2026-08-19. The absence is the result, and every step it needed is done.
>
> Tony: *"the lack of assembly is a result, just like the lack of 'connectivity'."*
>
> **There are no recurring cell assemblies in this preparation, in either stream.**
>
> | | instrument | fast | slow |
> |---|---|---|---|
> | discrete recurring groups | **modularity** on the STTC graph, each recording against its own jitter surrogates | **2 of 78** above null (2.6%) | **1 of 77** (1.3%) |
> | who participates, beyond rate | curveball + uniform nulls on membership (`bugarach.assembly`) | departure from uniform in **45 of 47** testable | **36 of 38** |
>
> Against the ~5% the modularity threshold gives by chance, and a measured false-positive
> rate of 6.0% (fast) / 9.1% (slow) for the membership test at this folder's own geometry.
> The median recording is *less* modular than its own surrogates. Co-participation above
> rate with **no modular partition** is a **core–periphery** field — a busy core, a long
> tail, no membership repeating as a unit. **Drop the word "assembly"** unless the
> modularity result is overturned; the likeliest route is a method that finds *overlapping*
> groups, which modularity cannot see.
>
> **All three closing steps are done** (PRs #135, #139):
>
> 1. **Power under the real decision rule**, at each recording's own geometry — the earlier
>    curve scored a looser test than the one that produced the answer.
> 2. **The penumbra-subtracted store**, paired on recordings testable in both: the departure
>    survives in 21 of 26 fast and 21 of 25 slow. Crosstalk inflates it without accounting
>    for it.
> 3. **Modularity on the fast stream**, which had never been run — the instrument hardcoded
>    `slow`, and this report had been asserting an absence on a stream nobody had measured.
>
> **And a fourth thing that was not on the list.** The instrument itself moved into this repo
> (PR #151). The modularity numbers above are now `bugarach.graph`'s, not interface2's: the
> pipeline that produced the originals has no maintainer and does not run out of the box. The
> port reproduces it to 2.2e-16 on identical inputs and agrees on 98.7% of folder verdicts
> under a different window rule. **The interface2 figures — 3 of 78 and 2 of 77 — are the
> cross-check, not the result**, which is why the row above changed.
>
> **Numbers in the body below this box predate all of that and are superseded.** In
> particular the earlier "3% ROI / 1% pensub" modularity figures counted recordings too
> sparse to score as negatives, and the earlier membership tallies included two recordings
> the lab had marked `exclude=1` — see
> [`2026-08-19-lab-exclusions-were-never-consulted.md`](2026-08-19-lab-exclusions-were-never-consulted.md).
> The current statement of record is `docs/assembly_report.md`, with its run record at
> `docs/reviews/assembly_summary_2026-08-19.md`.

**A question about the preparation, small enough to answer in a day, and it gates a
whole family of comparisons.**

> **Revision 2 — the power question is now measured, not argued.**
> `tools/assembly_power.py` plants assemblies of known strength at this folder's own
> geometry and reports how often the test finds them. Two results change what follows.
> **The event-conditioned null cannot be run alone**: it goes blind exactly where the
> signal is purest. And **the folder is well powered after all** — the arithmetic in
> revision 1 that made it look hopeless was the wrong intuition. Read
> *What the folder can actually see* before writing any measurement code.
>
> *Revision 1 replaced the original method, which tested co-participation against the
> assessor's circular-shift null and called the work free. Both were wrong, and the first
> would have returned a confident yes that meant nothing.*

## Why it came up

Tony pushed back on a claim that no literature detector was in our comparison — rightly:
CICADA is the Cossart lab's, ported here, and SpikyDetect runs on cSPIKE/PySpike's
synchrony profile. The question that followed — *which detector would you add* — has a
prerequisite nobody had noticed.

**Our generator draws every planted event's participants at random**
(`simulate.py`: `rois = rng.choice(nR, size=np_, replace=False)`). So the folder has
coordinated *events* and no cell *assemblies* — no group that recurs. The entire
assembly-detection literature (ICA/PCA, CAD, graph methods, item-set mining) finds
recurring co-activation patterns, so on this folder it finds nothing, and the zero would
be a fact about our generator rather than about those methods.

## The question

**Across the 85 baseline recordings, do the same cells tend to participate together
across events — and by how much more than chance?**

The measurement is on the real recordings throughout. The generator appears twice below,
once as the thing the answer would change and once as a name for the hypothesis being
tested. Neither is a reason to run this on simulated data.

## The null has to condition on the events

The assessor's circular shift moves each ROI's train independently, so it destroys every
trace of cross-ROI timing. Under it, co-participation sits at chance — and these
recordings are coordinated, which is the one thing about them we already know and which
survives even TTX (FOUNDATIONS §9). So every pair that appears together in a coordinated
event clears that null, on essentially every slice. The test returns a resounding yes,
the yes means *"these recordings are coordinated"*, and read as *"assemblies recur"* it
walks directly into the trap the last section of this file warns about.

**Condition on the events instead.** Hold the observed cluster times and each cluster's
participant count fixed, and redraw *which* ROIs took part — preserving each ROI's own
total participation count, so the busiest cells cannot manufacture an assembly. A
margin-preserving shuffle of the event x ROI membership matrix (curveball / swap
randomization) does this directly; the eigenvalue-against-Marchenko-Pastur route from the
Lopes-dos-Santos and Peyrache line answers the same question with a different instrument
and is worth running as a cross-check rather than a replacement.

That null is exactly the assumption `rng.choice` makes. So the test on real membership
reduces to *"do these recordings depart from uniform participation"* — which is the
decision the answer feeds, stated as a hypothesis.

## What it actually costs

Small, but not free, and the first draft's "no new instrument, no new null" was wrong on
both counts.

- **Membership is not recorded anywhere.** `_clusters` in `src/bugarach/assess.py`
  returns onset SD, participant *count*, peak coactivity and span. It gathers each
  participating ROI's nearest onset and then keeps only the times — the ROI index is
  discarded inside the loop. There is nothing yet to count co-participation over.
- **That function is on the parity path**, running against a 1e-9 MATLAB reference and
  called once per surrogate per K. Add membership additively — an optional return, or a
  sibling function that shares the clustering — and do not reshape what is pinned.
- **The corrected null reuses none of the assessor's surrogate machinery.** It is a new
  randomization over a new matrix. The clustering is what gets reused, not the null.
- **Done.** `bugarach.assembly` holds both nulls, both statistics and the two-null
  verdict; `tools/assembly_power.py` imports them rather than keeping a copy, so the
  instrument the power curve validated is the one the folder is measured with. The
  assessor records `Assessment.members` (observed clusters only) at unchanged 1e-9 MATLAB
  parity, and `tools/assess_archive.py --assemblies` runs the question over a store.
- **One thing the build caught that the design had not.** The verdict takes the smaller
  of two p-values per null, and a minimum of two tests is a third test with a larger size:
  uncorrected it called 2 of 8 uniformly generated recordings an assembly. Bonferroni over
  the two statistics fixed it — 22 of 24 now read `no-assembly`, and a test pins that rate,
  because the negative result is the thing this exercise exists to be able to publish.

## What the folder can actually see

**Measured, not estimated** — `tools/assembly_power.py`, figure `assembly_power` in the
darkroom. It plants an assembly of known size and known strength at the median slice
geometry the derived spec already records (`docs/learned/generator_spec.json`, medians
over all 85 baseline slices: **32 ROIs**, **21 clusters** at K=3 over a 59-minute window,
**4.5 participants** each) and counts how often the test rejects. Membership is simulated
directly — no onsets, no detector, no operating point — so it runs on a bare clone with no
`BUGARACH_DATA_ROOT`.

### The folder is well powered, and revision 1's arithmetic was misleading

496 pairs share about 165 co-participation observations, a third of an observation per
pair, and revision 1 read that as fatal. It is not. **An assembly concentrates counts
rather than spreading them**, and concentration is what the statistic measures. At the
median geometry, against the uniform null:

Recruitment is the fraction of a slice's 21 clusters drawn from the assembly; the power
in brackets is against the uniform null at alpha 0.05, over 400 simulated slices and 200
surrogates each.

| assembly | one slice alone | group of 20 slices |
|---|---|---|
| 4 cells | 1 event in 7 (0.66) | **1 event in 10 (1.00)** |
| 6 cells | 1 event in 7 (0.55) | **1 event in 10 (1.00)** |
| 8 cells | 1 event in 4 (0.73) | **1 event in 7 (1.00)** |
| 12 cells | 1 event in 2 (0.93) | **1 event in 4 (1.00)** |
| 16 cells — half the field | 1 event in 2 (0.82) | 1 event in 4 (0.90) |

So a negative result from this folder would be worth publishing. Stated the way it would
have to be written up: **a group of twenty slices excludes a recurring group of four to
six cells that takes part in more than a tenth of coordinated events**, and a compact
assembly is excluded well below the level a single slice could reach. A diffuse group
spanning half the field needs to recruit a quarter of events before the same claim holds.
Both nulls sit at their nominal 0.05 when nothing is planted.

### The event-conditioned null goes blind at full strength

The null revision 1 argued for — hold event times and sizes fixed, preserve each ROI's own
participation total — **loses all power exactly where the assembly is purest**. At full
strength the non-members never participate at all: 24 of 32 ROIs have a column sum of
zero, the entire signal has moved into the margins the null conditions on, and the
observed statistic lands on the null mean. Power rises to 1.00 and then falls back to
chance, so it is not monotonic in the quantity being measured — the shape a positive
control exists to catch, and the failure mode
[`2026-08-16-promiscuity-probe-cannot-fail.md`](2026-08-16-promiscuity-probe-cannot-fail.md)
records in another guise.

**So run both nulls.** The companion fixes event sizes only and redraws participants
uniformly, which is exactly what `simulate.py` does; it is monotonic and passes the
full-strength control, but it also fires on plain rate heterogeneity. Neither is
sufficient alone and the pair is interpretable:

- **both fire** — structure beyond what per-cell participation rates explain;
- **uniform only** — read the participation counts before claiming an assembly; it may be
  a few busy cells, or an assembly so sharp the conservative null cannot see it;
- **neither fires** — no assembly above the strengths tabled above.

### What is still worth counting on the real store

The spec's medians are enough to size the test, not to run it. When the store is mounted:
the per-slice *distribution* of ROI count and cluster count, since a slice well below the
median may be individually unpowered and should be reported as such rather than as a
negative. `assess_assemblies` already refuses rather than guesses — under four clusters it
returns `defined=False` and the verdict `undefined`, so "we could not look" can never be
read as "we looked and found nothing".

## All that is left is the store

    python tools/assess_archive.py --store <archive> --out <dir> --assemblies

Everything above this line runs on a bare clone and is tested. This command needs
`BUGARACH_DATA_ROOT` and the machine that holds it. It prints the verdict tally and a
pooled combination per K — **pooled, and labelled as such**, because the group of each
slice is not carried through the assessor yet and FOUNDATIONS §9 forbids quoting an
across-group number on its own. Splitting by group is the last piece, and it is a
plumbing job rather than a measurement one.

## Why the answer matters either way

- **If assemblies recur:** the generator should plant them, our benchmark is currently
  unable to reward membership structure, and PCA/ICA assembly detection becomes the
  obvious first literature port — a genuinely different principle from our six, which
  are all variations on "more coincidence than the local background explains".
- **If participation is random event-by-event:** the assembly family is simply not the
  right comparison for this preparation, the generator is right as it stands, and that
  is a publishable statement about the biology rather than a gap in our benchmark.

## What must not happen

Do not port an assembly detector first and report its score. On today's folder it will
lose, we will have "beaten" a respected method by testing it on data built to contain
nothing it looks for, and the first reviewer to notice will be right.

## Constraints

Baseline recordings only, as always — participation properties must not be taken from
senktide or TTX windows. And group-dependence applies: if assembly structure differs by
group, a pooled statistic hides it (FOUNDATIONS §9). With 85 slices split across groups,
the per-group n is around twenty, which is another reason the per-slice scalar is the
unit and not the pair.

Two more that bite this measurement specifically:

- **The dead-ROI store is cleaned asymmetrically** — 67 of 85 slices carry a verdict and
  the other 18 keep every ROI (FOUNDATIONS §9). A membership statistic is directly
  sensitive to which cells are in the matrix, so record per slice whether it was judged.
  Pooling the two silently would put the answer at the mercy of the exporter's coverage.
- **This needs the real store mounted** — `BUGARACH_DATA_ROOT`. Nothing here runs on a
  bare clone.

## What this does and does not block

It gates the assembly family only. The nearest neighbouring item — clean-rooming the
Molter coactivity frame gate, recommended in
[`2026-08-17-run-a-literature-method-on-our-recordings.md`](2026-08-17-run-a-literature-method-on-our-recordings.md)
— detects population *events*, not assemblies, so it is unaffected by how this falls and
remains the better move if a published-method comparison is wanted sooner.
