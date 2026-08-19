# Do the same cells fire together, again and again?

In these slices — mouse hypothalamic tissue imaged with a calcium indicator, where each
region of interest (ROI) stands for one cell — bursts of activity recruit a handful of
ROIs at a time. Whether those are **the same** ROIs each time, or a fresh draw, decides
what kind of thing we are studying and which published methods we may fairly compare
ourselves against. Nobody here had measured it.

This reports what 84 baseline recordings say, what the measurement cannot support, and
what would have to change before any of it is worth publishing. A first draft of this
report claimed a difference between experimental groups; an adversarial review showed
that claim was an artifact of detection power, and it has been withdrawn. What that
looked like is in the [run record](reviews/assembly_report_2026-08-18.md).

Two event streams are analysed separately throughout and never mixed. The upstream
pipeline separates each ROI's calcium events into a **fast** and a **slow** stream; this
report treats them as two measurements of the same recording and does not define the
kinetic boundary between them, because no document in this project does. ⚠

## The problem is that you cannot settle it by looking

![Which ROIs took part in each coordinated event, in three recordings. One row per event, one mark per participating ROI, ROIs ordered by how often they took part. A and B are real; C is generated with participants drawn uniformly at random, at A's geometry.](assembly_membership)

If the same group kept firing together, the left-hand columns would be dense. The first
panel leans left. The second and third are hard to separate by eye.

A summary number does separate them — but only when each recording is compared against
its own expectation. The share of all participation carried by the five busiest ROIs is
**45%** in the first panel against **30%** for a generated recording at that panel's
geometry, and **25%** in the second against **29%** at *its* geometry. The second
recording sits on its own no-structure expectation; the first sits well above.

The trap is that those shares cannot be compared *across* panels: the second recording
has 33 ROIs and the third has 24, so a top-five share means different things in each. An
earlier version of this figure compared them directly and appeared to show the statistic
ranking a structureless recording above a real one. It does not. It was a denominator.

That is the difficulty. ROIs differ in how often they fire for reasons unrelated to
recurring groups, and recordings differ in size, so any measure of "the same ROIs keep
appearing" is driven partly by rate and partly by geometry. The question needs a null
model — a reshuffle of the same data that destroys group structure while holding each
ROI's own participation fixed — and asks whether *which* ROIs co-occur is still
improbable under it.

## Why it matters beyond curiosity

Our event generator draws every planted event's participants uniformly at random, so no
group recurs. The benchmark corpus therefore contains coordinated **events** and no cell
**assemblies** — groups whose membership repeats.

That matters for what we may claim against the assembly-detection literature. Cell
assemblies there are defined as *subsets of neurons with significant co-activation*
(Lopes-dos-Santos et al. 2013), with membership read off the recovered patterns
afterwards — recurrence is an interpretation step, not part of the definition. So the
methods do **not** simply fail on our corpus. Run at our geometry, PCA with a
Marchenko–Pastur eigenvalue threshold (Peyrache et al. 2010) flags essentially every
simulated recording, because the coordinated events themselves violate its
independent-neurons null.

What our corpus cannot reward is **membership recovery**: the patterns those methods
return are not reproducible, because there is no stable membership to recover. That is
the reason not to port one yet — narrower than "they would score nothing", and the one
that actually holds.

## The instrument

A recording becomes an events × ROI table: one row per coordinated cluster the assessor
found, one mark per participating ROI. Two null models reshuffle it.

**Fixed margins.** Hold each event's size *and* each ROI's own total participation
fixed — these row and column totals are the margins — and move only who co-occurs, by
repeatedly swapping pairs of participations that leave both totals unchanged. This is
the curveball algorithm (Strona et al. 2014; uniform sampling proved by Carstens 2015).
It can respond only to *which* ROIs co-occur, never to how busy they are.

**Uniform participation.** Hold event sizes and redraw participants uniformly — the same
assumption our generator makes. It responds to any departure from uniformity, including
plain rate differences between ROIs.

The two are **nested, not independent**: every table the first null can reach, the second
can too. Rejecting both is one conclusion, not two agreeing ones. A recording is scored
by the smaller of two statistics — the variance of pairwise co-participation counts, and
the leading eigenvalue of the ROI correlation matrix — against each null, at α/2 = 0.025
after correcting for using two statistics, over 1000 reshuffles.

**On this corpus the pair collapses to one.** No recording was rejected by the fixed-margin
null alone, and 41 of 48 fast recordings sit at the resolution floor under the uniform
null, which is saturated. So "rejects both" is decided by the fixed-margin null. The
second null earns its place as a guard, not as corroboration.

**One known blind spot, narrower than it first appeared.** When a group recurs *perfectly*
— every event drawn from it, non-members never firing — the whole signal moves into the
margins the first null holds fixed and there is nothing left to swap. Measured: power is
0.85 at 90% saturation and 0.00 at 100%. It is a knife-edge at literal saturation, not a
general softness, and no recording with background activity reaches it. This degeneracy
is known in the ecological null-model literature as the Narcissus effect (Colwell &
Winkler 1984) and as limited randomizability (Kallio 2016), which reports fixed-margin
nulls becoming *liberal* in that regime rather than blind — a disagreement with what we
measure that is not yet resolved. ⚠

## What the corpus says

![Whether a recording is called structured against how many coordinated events it contains, coloured by experimental group (A); every testable recording plotted at its two nulls beside generated controls (B); and the verdict tally across the coactivity floor K (C).](assembly_answer)

<p class="note">Groups in panel A:
<b style="color:#20506b">DI</b> ·
<b style="color:#7a5c2e">MALE</b> ·
<b style="color:#5c5470">OVX</b> ·
<b style="color:#8c3b3b">ORX</b>.
Panel B: <b style="color:#111111">circles</b> real fast ·
<b style="color:#1f6fb4">squares</b> real slow ·
<b style="color:#a9540f">diamonds</b> generated controls; dotted lines mark the
&alpha;/2 threshold, and points against an axis edge are at the resolution floor
that 1000 reshuffles can reach, not identical values.
Panel C verdicts: <b style="color:#1a7f4b">both nulls</b> ·
<b style="color:#a35f10">uniform only</b> ·
<b style="color:#6f52a0">fixed margins only</b> ·
<b style="color:#6a6a6a">neither</b>.</p>

Of 84 baseline recordings, **48 are testable** in the fast stream and 38 in the slow —
the rest have fewer than four coordinated clusters, which is too few for any reshuffle
test, and are reported as **undefined, never negative**.

Among those, co-participation beyond per-ROI rate is common: **27 of 48** fast recordings
and **27 of 38** slow. Against generated recordings with no recurring group by
construction, the same pipeline returns a false-positive rate of **2.5%** (6 of 240,
95% interval 1.1–5.1%). Fifty-six percent against 2.5% is the finding.

**What detection tracks is how much there was to see.** Recordings called structured hold
a median of 45 coordinated events; the rest hold 17 (p = 0.002). That is panel A, and it
is the reason the next section exists.

## The group difference this report previously claimed, and why it is withdrawn

The four experimental groups — DI (diestrus females), MALE (intact males), OVX
(ovariectomised females) and ORX (orchidectomised males) — differ in the rate at which
this test fires. At the animal level in the fast stream: DI 9 of 10, MALE 7 of 9, OVX 4
of 8, ORX 1 of 6, exact test p = 0.017.

**That gradient is reproduced by identical assemblies.** Planting the *same* six-ROI
assembly at each group's median coordinated-event count and running the same scoring
gives 0.74, 0.68, 0.64 and 0.21 — against observed 0.71, 0.64, 0.45 and 0.17. The groups
do not reach the test on equal terms: DI contributes 17 of 17 recordings, ORX **6 of 25**,
and among those that survive, ORX holds a median of 10 coordinated events against DI's
38.

Three further checks agree. Permuting group within event-count strata gives p = 0.16.
The same data scored per recording rather than per animal gives p = 0.11. And the
"an animal counts if any of its recordings does" rule gives the groups unequal exposure,
because ORX animals contribute one testable recording each and DI animals up to three.

**So the claim is withdrawn.** What differs between these groups, on this evidence, is how
much coordination they have — DI 1.90 clusters per minute against ORX 0.05 — not whether
that coordination has recurring membership. Those may both be true; this corpus cannot
separate them.

The ORX result in particular must not be read as absence. Constructing the failure it
would have to deny — a compact assembly in *every* ORX animal at one event in ten —
predicts 1.7 of 6 animals flagged. One was observed. For three of the six, detection
power is 0.03–0.07, indistinguishable from the false-positive rate. The number could not
have moved.

## What would have to be true for this to be wrong

- **Optical crosstalk.** Neighbouring or overlapping ROIs share neuropil signal and will
  co-participate above rate for reasons that have nothing to do with assemblies. The
  fixed-margin null cannot remove this, because it conditions on totals and not on
  geometry. Nothing here checks whether co-participation concentrates in spatially
  adjacent ROI pairs, and that is the first check a reviewer will ask for. ⚠
- **The clusters are the assessor's, not ground truth.** Every table is built from
  coordinated clusters this project's own assessor found. A different clustering gives a
  different table.
- **The verdict rests on one arbitrary threshold that decides almost half the corpus.**
  Fewer than four clusters means no test; that rule excludes 36 of 84 fast recordings, and
  it excludes them unevenly across groups.
- **The controls are generated at a single geometry**, matched to the median testable
  recording. Thin recordings — the ones the withdrawn group claim turned on — are not
  represented in the control set, though a separate check at four clusters put the
  false-positive rate at 0.02.
- **Structure is not the same as a discrete assembly.** What is measured is
  co-participation beyond rate. Showing that these are specific recurring groups needs
  clustering the membership table and demonstrating the groups are stable, which nothing
  here has done.

## What travels beyond this lab

Less than the first draft of this report claimed, and it is worth being precise about
what is left.

The blind spot above is **not** a new result: fixed-margin degeneracy is documented in
ecology under two names. What this work adds is a **measured power curve for it on an
assembly-membership statistic at a realistic neural geometry, with a saturation positive
control** — and the observation that the collapse is a knife-edge rather than a gradual
softening.

The transferable practice is smaller and firmer: **a null result needs a test demonstrated
able to fail in both directions.** Both halves were built here — generated recordings
with no assemblies return negative, and saturated assemblies return positive under the
null that can see them — and the review still found a claim whose alarm could not ring.
Building both controls is necessary and was not sufficient.

## What should happen next

1. **Match on coordinated-event count before comparing anything across groups** —
   subsample every membership table to a common number of events, or model the count
   explicitly. Until then group and detectability are not separable in this corpus.
2. **Plant assemblies in the generator** at the strengths this instrument can resolve.
   Until it does, the benchmark cannot reward membership recovery, and every detector
   score to date was earned on a corpus easier than reality in exactly this way.
3. **Then port an assembly detector** and score it on membership recovery, not on event
   detection — which it will pass regardless.
4. **Check spatial adjacency**, which is the cheapest way to remove the most likely
   alternative explanation for everything above.

## How to reproduce this

Every number reads one export folder — no event store, no environment variable, no
companion spreadsheet. The `--store` flag takes the export folder.

    python tools/assess_archive.py --store <folder> --out <dir> \
        --stream fast --assemblies
    python tools/assess_archive.py --store <folder> --out <dir> \
        --stream slow --assemblies
    python tools/make_assembly_figure.py --fast <dir> --slow <dir> --out <figdir>
    python tools/make_membership_example.py --folder <folder> --runs <dir> \
        --out <figdir>

Group and animal come from the folder's `slices.csv` as reserved columns; the window
scored is the producer's own analysis window; recordings the producer excluded are
already absent. The measurement is in `bugarach.assembly`, the power analysis in
`tools/assembly_power.py`, and both are exercised by the test suite.

## References

- Strona G. et al. (2014) A fast and unbiased procedure to randomize ecological binary
  matrices with fixed row and column totals. *Nat Commun* 5:4114.
  doi:10.1038/ncomms5114 — the curveball algorithm.
- Carstens C.J. (2015) Proof of uniform sampling of binary matrices with fixed row sums
  and column sums for the fast curveball algorithm. *Phys Rev E* 91:042812.
- Colwell R.K. & Winkler D.W. (1984) A null model for null models in biogeography, in
  *Ecological Communities: Conceptual Issues and the Evidence*, Princeton UP, 344–359 —
  the Narcissus effect. ⚠ cited at one remove; not read in full.
- Kallio A. (2016) Properties of fixed-fixed models and alternatives in presence-absence
  data analysis. *PLOS ONE* 11(11):e0165456.
- Lopes-dos-Santos V., Ribeiro S. & Tort A.B.L. (2013) Detecting cell assemblies in large
  neuronal populations. *J Neurosci Methods* 220:149–166.
- Peyrache A. et al. (2010) Principal component analysis of ensemble recordings reveals
  cell assemblies at high temporal resolution. *J Comput Neurosci* 29:309–325.
- Russo E. & Durstewitz D. (2017) Cell assemblies at multiple time scales with arbitrary
  lag constellations. *eLife* 6:e19428 — cell assembly detection (CAD).
- Phipson B. & Smyth G.K. (2010) Permutation p-values should never be zero. *Stat Appl
  Genet Mol Biol* 9(1):39.
