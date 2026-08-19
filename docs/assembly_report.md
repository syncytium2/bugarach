# There are no recurring cell assemblies here, and the absence is the finding

In these slices — mouse hypothalamic tissue imaged with a calcium indicator, where each
region of interest (ROI) stands for one cell — bursts of activity recruit a handful of
ROIs at a time. Whether those are **the same** ROIs each time decides what kind of thing
we are studying and which published methods we may fairly compare ourselves against.

**They are not.** Two instruments, pointed at the same preparation from different
directions, agree:

| what was asked | instrument | verdict |
|---|---|---|
| are there groups of cells more coupled to each other than to the rest of the field | graph **modularity** on the spike-time-tiling graph | **no partition above its null** — 3% of ROI recordings, 1% with the penumbra subtracted |
| is *who participates* in each event explained by how often each cell fires | curveball and uniform nulls on the event × cell membership table | departure from uniform in **47 of 49** testable fast recordings and **38 of 40** slow, against a **5.3%** false-positive rate measured at this corpus's own geometry |

Those do not conflict, and reading them together is the whole result. Participation is
not uniform — some cells are in most events and many are in few — but that unevenness
does **not** resolve into groups. A field with co-participation above rate and no modular
partition is a **core–periphery** field: a busy core, a long tail, no membership that
repeats as a unit. That is weaker and more ordinary than a cell assembly, and it is what
the evidence supports.

**So the word "assembly" should be dropped** for this preparation unless the modularity
result is overturned.

This report is written to be the last word on the question for our purposes. It states
the answer, then spends most of its length on the two things that decide whether anyone
should believe it: whether the test could have failed, and whether the largest alternative
explanation has been removed.

Two event streams are analysed separately throughout and never mixed. The upstream
pipeline separates each ROI's calcium events into a **fast** and a **slow** stream; this
report treats them as two measurements of the same recording and does not define the
kinetic boundary between them, because no document in this project does. ⚠

## Why an absence is worth reporting at all

A negative is only a result if a positive was reachable. Three things follow from this
one, and each costs real work if the answer is wrong:

- **Our event generator is right as it stands.** It draws every planted event's
  participants uniformly at random (`simulate.py`, `rng.choice`), so the benchmark corpus
  contains coordinated *events* and no cell *assemblies*. If membership recurred in the
  tissue, the generator would be missing a feature of the preparation, and every detector
  score earned on it would have been earned on a corpus easier than reality.
- **The assembly-detection literature is not the right comparison for this preparation.**
  Not because those methods would score zero — they would not, see below — but because our
  corpus cannot reward the thing they exist to do.
- **A family of downstream comparisons is closed rather than merely unattempted**, which is
  a different and more defensible position to write up.

## The problem is that you cannot settle it by looking

![A · one real recording's membership table beside a generated recording at the same geometry, whose participants are drawn uniformly at random by construction. B · power under the decision rule the corpus is actually scored by, evaluated at each real recording's own geometry. C · the verdict on every testable recording before and after optical crosstalk is removed.](assembly_closed)

Panel A is the data before any statistic touches it: one row per coordinated event, one
column per cell, a mark where that cell took part, cells ordered by how often they
participated. A recording in which the same cells recur would show vertical stripes on the
left. The real panel and the uniform-random panel beside it are hard to separate by eye,
and that is the honest starting point — the generated one has **no** recurring group, by
construction.

Summary numbers do not rescue it, because they cannot be compared across recordings. The
share of participation carried by the five busiest cells means different things in a
14-cell recording and a 55-cell one; an earlier version of this figure compared such panels
directly and appeared to show the statistic ranking a structureless recording above a real
one. It was a denominator, not a finding.

So the question needs each recording compared against **its own** expectation: a reshuffle
of that recording's own table that destroys group structure while holding fixed everything
that is not group structure.

## The instrument: two nulls, because neither is sufficient alone

A recording becomes an events × cell table, and two null models reshuffle it.

**Fixed margins.** Hold each event's size *and* each cell's own total participation fixed —
these row and column totals are the margins — and move only who co-occurs, by repeatedly
swapping pairs of participations that leave both totals unchanged. This is the curveball
algorithm (Strona et al. 2014; uniform sampling proved by Carstens 2015). It can respond
only to *which* cells co-occur, never to how busy they are.

**Uniform participation.** Hold event sizes and redraw participants uniformly — exactly the
assumption our generator makes. It responds to any departure from uniformity, including
plain rate differences between cells.

The two are **nested, not independent**: every table the first null can reach, the second
can too. Rejecting both is one conclusion, not two agreeing ones.

Each null is tested with two statistics — the variance of pairwise co-participation counts,
and the leading eigenvalue of the cell correlation matrix — and a recording is scored at
**α/2 = 0.025** within each null, correcting for the use of two statistics, over 1000
reshuffles. That correction is not decoration: uncorrected, taking the smaller of two
p-values is itself a test with a larger size, and it called 2 of 8 uniformly generated
recordings an assembly.

**Why both are needed** is a measured property, not an argument. The fixed-margin null
loses all power exactly where an assembly is purest: when every event is drawn from the
group, non-members never participate, the entire signal has moved into the margins the null
conditions on, and the observed statistic lands on the null mean. Power rises and then
falls back to chance — not monotonic in the quantity being measured, which is the shape a
positive control exists to catch. The uniform null is monotonic and survives saturation but
fires on plain rate heterogeneity. Neither is sufficient; the pair is interpretable.

## Could this test have failed? Yes — measured, under the rule that produced the answer

This is the question a negative result lives or dies on, and answering it properly required
redoing the earlier power analysis.

**The earlier curve measured a different instrument than the one that produced the answer.**
It reported power for *one statistic* under *one null* at α, combining twenty recordings by
Fisher. No recording was ever scored that way. Recordings are scored by
`AssemblyResult.verdict()`, which Bonferroni-corrects across the two statistics *within*
each null and then reads both nulls together — a strictly more conservative rule, α/2 twice
over, and one decision per recording.

It was also computed at a **median slice**. The corpus is not median: across the 49 testable
fast recordings the cell count runs 14 to 55 and the coordinated-event count runs **4 to
235**. A recording near the bottom of that range may be individually unpowered, and pooling
it with the rest would let "we could not look" pass as "we looked and found nothing".

So the curve was recomputed under `verdict()`, planting assemblies at **each real
recording's own geometry**. Two things come out of it.

**The test sits at its nominal size.** With nothing planted it fired on 13 of 244 simulated
fast recordings — **5.3%**, 95% interval 3.1–8.9% — and 13 of 197 slow, **6.6%**, interval
3.9–11.0%, against a nominal 5%. A `no-assembly` verdict from this corpus means what it
says.

**The test has real power at strengths worth excluding.** Recruitment is the fraction of a
recording's coordinated events drawn from the planted group; each figure is the fraction of
this corpus's *actual* recordings in which the test fires.

| planted group | 1 in 20 · fast | 1 in 10 · fast | 1 in 4 · fast | 1 in 4 · slow |
|---|---|---|---|---|
| 4 cells | 0.31 | 0.59 | **0.90** | 0.55 |
| 6 cells | 0.24 | 0.61 | 0.73 | 0.68 |
| 8 cells | 0.29 | 0.43 | 0.84 | 0.62 |
| 12 cells | 0.10 | 0.24 | 0.59 | 0.56 |
| 16 cells — half the field | 0.12 | 0.29 | 0.50 | 0.53 |

The slow stream is uniformly less powered, because it carries fewer coordinated clusters;
its column is shown at one recruitment level so the difference is visible rather than
averaged away.

**And the verdict rule does not inherit the fixed-margin null's blind spot.** At full
saturation the two nulls stop agreeing — the fraction of recordings where *both* fire
collapses to 0.00–0.10 — but the verdict still fires on 90–100% of them, carried by the
uniform null and reported as `uniform-only`. The degeneracy shows up in *which word* the
verdict returns, not in whether it returns one. This is the concrete payoff of running two
nulls, and it is why the earlier single-null curve understated the instrument.

Read against the observed 47 of 49, the corpus is not close to the boundary of what it can
see.

## The alternative the nulls cannot remove, and what happened when it was removed

Both nulls reshuffle a membership table that has **already been built**. If two ROIs overlap
optically — neighbouring cells, shared neuropil — one cell's calcium transient lands in both
traces, and that pair co-participates for a reason that has nothing to do with the tissue's
coordination. **No reshuffle can undo this, because the artifact is in the table being
reshuffled.** The previous version of this report named this as the first check a reviewer
would ask for, and did not perform it.

It has now been performed, by rebuilding the tables from the **penumbra-subtracted** store —
the same recordings with the estimated optical contribution of neighbouring ROIs removed —
and re-measuring. The comparison is **paired**, on the recordings testable in *both* stores,
because penumbra subtraction removes events, removing events removes coactive clusters, and
a recording that falls below the floor returns `undefined` rather than a negative. Comparing
49-of-85 against 28-of-85 would read a loss of *power* as a loss of *signal*, which is the
single most likely way to get this question wrong.

At the standard coactivity floor K = 3:

| stream | testable in both stores | fires, original | fires, penumbra-subtracted | discordant |
|---|---|---|---|---|
| fast | 28 | 28 | **22** | 6, all one direction |
| slow | 26 | 26 | **22** | 4, all one direction |

**The departure survives.** It is also genuinely attenuated: all ten discordant recordings
move the same way (fires → does not), which under a sign test is p ≈ 0.002. Per stream the
fast shift alone reaches p = 0.031 and the slow does not (p = 0.125). At K = 4 the same
pattern is weaker still — 13 of 16 fast and 18 of 19 slow continue to fire.

The honest reading is therefore **not** "crosstalk explains it" and **not** "crosstalk is
irrelevant". It is: **optical crosstalk inflates the effect and does not account for it.**
Four in five recordings that could still be tested departed from uniform participation after
the overlap was subtracted.

The cost in power bounds how hard this control could push, and is worth stating plainly.
Penumbra subtraction retains 65% of fast events and 58% of slow, but it removes far more
*coincidences* than events: coordinated clusters at K = 3 fall from 0.35 per minute to 0.05.
Testability was lost on 21 of 49 fast recordings and 14 of 40 slow. Those are reported as
undefined, never as negative.

## What the corpus says, in full

Of 85 baseline recordings, **49 are testable** in the fast stream at K = 3 and 40 in the
slow; the rest have fewer than four coordinated clusters, too few for any reshuffle test,
and are **undefined, never negative**. Among the testable, co-participation beyond per-cell
rate is near-universal: **47 of 49** fast and **38 of 40** slow, against the 5.3% and 6.6%
false-positive rates above. The result is stable across the coactivity floor — at K = 4,
K = 6 and K = 8 the firing rate stays above 85% wherever enough recordings remain testable
to say anything.

The companion measurement is the one that makes this a negative. Graph modularity on the
spike-time-tiling graph — the standard instrument for "are there groups here" — finds **no
partition above its null**: 3% of ROI recordings, 1% with the penumbra subtracted. The cells
that participate together are not the cells more connected to each other than to the field.

## What this report previously claimed and no longer does

**A difference between experimental groups is withdrawn.** The four groups — DI, MALE, OVX,
ORX — differ in the rate at which this test fires, and that gradient is reproduced by
planting the *same* six-cell assembly at each group's median coordinated-event count:
simulated 0.74 / 0.68 / 0.64 / 0.21 against observed 0.71 / 0.64 / 0.45 / 0.17. It was
detection power, not biology. The groups do not reach the test on equal terms — DI
contributes 17 of 17 testable recordings, ORX 6 of 25 — and permuting group within
event-count strata gives p = 0.16.

The ORX result in particular must not be read as absence: a compact assembly present in
*every* ORX animal at one event in ten predicts 1.7 of 6 animals flagged, and one was
observed. The number could not have moved.

**"PCA/ICA would score nothing on our corpus" is also withdrawn**, as simply false. Cell
assemblies in that literature are defined as subsets of neurons with significant
co-activation (Lopes-dos-Santos et al. 2013), with membership read off the recovered patterns
afterwards — recurrence is an interpretation step, not part of the definition. Run at our
geometry, PCA against a Marchenko–Pastur bound flags essentially every simulated recording,
because the coordinated events themselves violate its independent-neurons null. The real
reason not to port one is narrower, and it holds: our corpus cannot reward **membership
recovery**, because there is no stable membership to recover.

## What would still have to be true for this to be wrong

- **The clusters are the assessor's, not ground truth.** Every table is built from
  coordinated clusters this project's own assessor found. A different clustering gives a
  different table, and nothing here validates the clustering against an external standard.
- **One arbitrary threshold decides which recordings are in.** Fewer than four clusters means
  no test; that rule excludes 36 of 85 fast recordings, and it excludes them unevenly across
  groups.
- **The dead-ROI store is cleaned asymmetrically** — 67 of 85 recordings carry a verdict and
  18 keep every ROI. A membership statistic is directly sensitive to which cells are in the
  matrix. ⚠
- **Penumbra subtraction is itself a model.** It removes an *estimate* of optical overlap. A
  residual after subtraction is evidence the estimate was incomplete as much as evidence the
  coordination is real, and this report cannot separate those.
- **Core–periphery is an interpretation, not a fitted model.** Nothing here fits a
  core–periphery structure and tests it against alternatives; it is the reading that
  reconciles two measurements. ⚠
- **Modularity is one instrument.** A field can carry assemblies a partition-based method
  misses — overlapping groups in particular, which modularity handles badly.

## What travels beyond this lab

The transferable practice is smaller and firmer than the finding: **a null result needs a
test demonstrated able to fail, scored under the rule that actually produced the result.**
Both halves were built here and the second was initially wrong — the power curve licensing
this negative was measuring a looser test than the one the recordings were scored by, and
nobody noticed until the question was asked directly.

The measured fixed-margin degeneracy is a genuine if narrow contribution: the collapse at
saturation is a **knife-edge rather than a gradual softening**, and it is invisible unless a
saturation positive control is run. It is known in the ecological null-model literature as
the Narcissus effect (Colwell & Winkler 1984) and as limited randomizability (Kallio 2016),
which reports fixed-margin nulls becoming *liberal* in that regime rather than blind — a
disagreement with what we measure that is not resolved. ⚠

## What should happen next

1. **Nothing, for the assembly question.** It is answered. Reopen it only if the modularity
   result is overturned, or if a store arrives whose penumbra estimate is materially better.
2. **Do not plant assemblies in the generator.** An earlier version of this report
   recommended it; on this evidence the generator's uniform draw is a correct model of the
   preparation, and planting groups would make the benchmark *less* faithful.
3. **Do not port an assembly detector to score it on our corpus.** It would lose on
   membership recovery, and it would lose because the tissue has no membership to recover —
   a fact about the preparation, not a result about the method.
4. **If the core–periphery reading is to be used for anything**, fit it and test it against
   alternatives rather than inferring it from two other measurements.

## How to reproduce this

The assembly measurement and the crosstalk control both need the real recordings behind
`BUGARACH_DATA_ROOT`; the power analysis needs nothing but the repo.

    # the measurement, on each store
    python tools/assess_archive.py --store <store> --out <dir> \
        --stream fast --assemblies

    # the crosstalk control: paired, on recordings testable in both
    python tools/assembly_pensub_compare.py --main <dir>/assessment_real.json \
        --pensub <pendir>/assessment_real.json --k 3 --stream fast \
        --json-out <dir>/pensub_cmp_fast_k3.json

    # power under the rule the corpus is actually scored by
    python tools/assembly_power.py \
        --geometry-from <dir>/assessment_real.json --stream fast \
        --verdict-only --out <figdir>

    # the figure, then the report
    python tools/make_assembly_closed_figure.py --power <figdir>/assembly_power.json \
        --pensub <dir>/pensub_cmp_fast_k3.json <dir>/pensub_cmp_slow_k3.json \
        --store <store> --slice <id> --also docs/learned
    python tools/build_assembly_report.py --src docs/assembly_report.md \
        --figures <figdir> --also docs/learned

The measurement is in `bugarach.assembly`, the power analysis in `tools/assembly_power.py`,
and both are exercised by the test suite.

**One caveat on the numbers above.** The crosstalk comparison reads `.mat` stores on both
sides, because no export folder exists for the penumbra-subtracted recordings. A `.mat`
store carries no producer analysis window, so those runs score the raw baseline period. The
export-folder tallies quoted in the previous version of this report — 48 testable fast, 38
slow — differ slightly from the `.mat` tallies here (49 and 40) for that reason and no
other. The comparison is `.mat`-against-`.mat` throughout, so the crosstalk contrast is
unaffected. ⚠

## References

- Strona G. et al. (2014) A fast and unbiased procedure to randomize ecological binary
  matrices with fixed row and column totals. *Nat Commun* 5:4114. doi:10.1038/ncomms5114 —
  the curveball algorithm.
- Carstens C.J. (2015) Proof of uniform sampling of binary matrices with fixed row sums and
  column sums for the fast curveball algorithm. *Phys Rev E* 91:042812.
- Colwell R.K. & Winkler D.W. (1984) A null model for null models in biogeography, in
  *Ecological Communities: Conceptual Issues and the Evidence*, Princeton UP, 344–359 — the
  Narcissus effect. ⚠ cited at one remove; not read in full.
- Kallio A. (2016) Properties of fixed-fixed models and alternatives in presence-absence data
  analysis. *PLOS ONE* 11(11):e0165456.
- Lopes-dos-Santos V., Ribeiro S. & Tort A.B.L. (2013) Detecting cell assemblies in large
  neuronal populations. *J Neurosci Methods* 220:149–166.
- Peyrache A. et al. (2010) Principal component analysis of ensemble recordings reveals cell
  assemblies at high temporal resolution. *J Comput Neurosci* 29:309–325.
- Russo E. & Durstewitz D. (2017) Cell assemblies at multiple time scales with arbitrary lag
  constellations. *eLife* 6:e19428 — cell assembly detection (CAD).
- Phipson B. & Smyth G.K. (2010) Permutation p-values should never be zero. *Stat Appl Genet
  Mol Biol* 9(1):39.
