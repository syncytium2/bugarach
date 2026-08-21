# There are no recurring cell assemblies here, and the absence is the finding

In these slices — mouse hypothalamic tissue imaged with a calcium indicator, where each
region of interest (ROI) stands for one cell — bursts of activity recruit a handful of
ROIs at a time. Whether those are **the same** ROIs each time decides what kind of thing
we are studying and which published methods we may fairly compare ourselves against.

**They are not.** Two instruments, pointed at the same preparation from different
directions, agree:

| what was asked | instrument | fast | slow |
|---|---|---|---|
| are there groups of cells more coupled to each other than to the rest of the field | graph **modularity** on the spike-time-tiling graph, each recording against its own jitter surrogates | **no** — 2 of 79 above null (2.5%) | **no** — 2 of 78 (2.6%) |
| is *who participates* in each event explained by how often each cell fires | curveball and uniform nulls on the event × cell membership table | departure from uniform in **46 of 48** testable, against a 5.0% false-positive rate | **34 of 38**, against 9.6% |

**Both streams, both instruments.** The test calls a recording modular when its modularity
clears the 95th percentile of its own surrogates, so **about 5% should clear it by chance** —
and 2.5% and 2.6% are below that. There is no modular structure in either stream. The
median recording is *less* modular than its own surrogates (z = −1.38 fast, −3.58 slow):
holding the graph's node count, event counts and sparsity fixed and moving only the timing
makes it score **higher**, which is the opposite of what a field of assemblies would do.

Those do not conflict, and reading them together is the whole result. Participation is
not uniform — some cells are in most events and many are in few — but that unevenness
does **not** resolve into groups. A field with co-participation above rate and no modular
partition is a **core–periphery** field: a busy core, a long tail, no membership that
repeats as a unit. That is weaker and more ordinary than a cell assembly, and it is what
the evidence supports.

**So the word "assembly" should be dropped** for this preparation, in both streams, unless the
modularity result is overturned.

This report is written to be the last word on the question for our purposes. It states
the answer, then spends most of its length on the two things that decide whether anyone
should believe it: whether the test could have failed, and whether the largest alternative
explanation has been removed.

**Every number here is read from an export folder, and that is the whole input.** The contract
(`docs/export_folder_spec.md`) states it plainly: bugarach reads one folder and nothing else —
no data store, no archive, no companion database. Which recordings are analysable and which
cells are alive are the producer's calls, **already applied to what the folder contains**.
There is no exclusion step in this analysis and there must not be one.

An earlier version of this report was computed the other way, and it is worth saying what that
cost. It read the `.mat` store directly, found it therefore held recordings the lab had
withdrawn, and re-derived the exclusions from the lab's workbook. The workbook keys them on
(date, mouse, **`slice_order`**); this project has no `slice_order`, so it matched on date and
**dropped a recording the lab had not withdrawn** — one mouse contributed two slices that day
and only the first was excluded. The producer's own export had it right. The counts below are
therefore over **84 recordings**, not the 83 the previous version reported, and they reproduce
exactly the folder-based tallies this project had before the detour. ⚠ Contract revision 6
records the incident.

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

![A · one real recording's membership table beside a generated recording at the same geometry, whose participants are drawn uniformly at random by construction. B · power under the decision rule the corpus is actually scored by, evaluated at each real recording's own geometry, one curve per planted group size; the dotted line marks the 5% size of the test, where every curve begins when nothing is planted. C · the verdict before and after optical crosstalk is removed, paired on the fast and slow recordings testable in both stores; the grey bar counts recordings that fell below the testable floor, which is lost power and not a negative.](assembly_closed)

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

**The fast test sits at its nominal size; the slow test may not.** With nothing planted it
fired on 12 of 238 simulated fast recordings — **5.0%**, 95% interval 2.9–8.6%, which is the
nominal rate almost exactly — and on 18 of 187 slow, **9.6%**, interval 6.2–14.7%, which does
**not** cover 5%.

**The slow stream's test is anti-conservative at its own geometry, and that is now settled
rather than suspected.** Three independent runs of the same design, at three slightly
different geometries, put it at 6.6%, 9.1% and **9.6%** — every one above nominal and the last
two with intervals excluding it. Treat the slow false-positive rate as roughly **twice**
nominal. It costs the slow negative precision and does not touch its direction: 34 of 38 is
89%, against a null rate of at most 15% at the top of its interval. The fast test needs no
such discount.

**The test has real power at strengths worth excluding.** Recruitment is the fraction of a
recording's coordinated events drawn from the planted group; each figure is the fraction of
this corpus's *actual* recordings in which the test fires.

| planted group | 1 in 20 · fast | 1 in 10 · fast | 1 in 4 · fast | 1 in 4 · slow |
|---|---|---|---|---|
| 4 cells | 0.21 | 0.54 | **0.85** | 0.61 |
| 6 cells | 0.29 | 0.56 | 0.79 | 0.61 |
| 8 cells | 0.19 | 0.46 | 0.60 | 0.58 |
| 12 cells | 0.08 | 0.27 | 0.62 | 0.54 |
| 16 cells — half the field | 0.07 | 0.15 | 0.41 | 0.44 |

The slow stream is uniformly less powered, because it carries fewer coordinated clusters;
its column is shown at one recruitment level so the difference is visible rather than
averaged away.

**And the verdict rule does not inherit the fixed-margin null's blind spot.** At full
saturation the two nulls stop agreeing — the fraction of recordings where *both* fire
collapses to 0.00–0.10 — but the verdict still fires on 90–100% of them, carried by the
uniform null and reported as `uniform-only`. The degeneracy shows up in *which word* the
verdict returns, not in whether it returns one. This is the concrete payoff of running two
nulls, and it is why the earlier single-null curve understated the instrument.

Read against the observed 46 of 48, the corpus is not close to the boundary of what it can
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
| fast | 26 | 26 | **21** | 5, all one direction |
| slow | 25 | 25 | **21** | 4, all one direction |

**The departure survives.** It is also genuinely attenuated: all nine discordant recordings
move the same way (fires → does not), which under a sign test is p ≈ 0.004. Those nine come
from **nine different animals** — checked against the lab record's `mouse_id`, not merely
against the recording ids — so the combined test does not count one preparation twice.
**Neither stream reaches significance on its own** (fast p = 0.063, slow p = 0.125); the
attenuation is a claim about the pair, resting on the consistency of its direction rather
than on either stream's count.

The honest reading is therefore **not** "crosstalk explains it" and **not** "crosstalk is
irrelevant". It is: **optical crosstalk inflates the effect and does not account for it.**
Four in five recordings that could still be tested departed from uniform participation after
the overlap was subtracted.

The cost in power bounds how hard this control could push, and is worth stating plainly.
Penumbra subtraction retains 65% of fast events and 58% of slow, but it removes far more
*coincidences* than events: coordinated clusters at K = 3 fall from 0.35 per minute to 0.05.
Testability was lost on 21 of 47 fast recordings and 13 of 38 slow. Those are reported as
undefined, never as negative.

## What the corpus says, in full

Of the 84 recordings the export folder contains, **48 are testable** in the fast stream at
K = 3 and 38 in the slow; the rest have fewer than four coordinated clusters, too few for any
reshuffle test, and are **undefined, never negative**. Among the testable, co-participation
beyond per-cell rate is near-universal: **46 of 48** fast and **34 of 38** slow, against the
5.0% and 9.6% false-positive rates above. The result is stable across the coactivity floor — at K = 4,
K = 6 and K = 8 the firing rate stays above 85% wherever enough recordings remain testable
to say anything.

The companion measurement is the one that makes this a negative.

![A · every recording's modularity against its own jitter surrogates, in null standard deviations; marks right of the dotted line at zero are more modular than timing alone predicts, and the highlighted marks are the ones clearing the 95th-percentile threshold the test actually uses. B · the rate of those, against the 5% that chance produces.](assembly_modularity)

Graph modularity on the spike-time-tiling graph — the standard instrument for "are there
groups here" — finds **no partition above its null in either stream**: 2 of 79 fast
recordings (2.5%, 95% interval 0.7–8.8) and 2 of 78 slow (2.6%, 0.7–8.9), against the ~5%
the threshold yields by chance. The cells that participate together are not the cells more
connected to each other than to the field.

**Those numbers are this repo's own, and that is new.** They were computed by
`bugarach.graph` and `tools/modularity_null.py`, not by the interface2 pipeline that
produced the earlier version of this section. The pipeline has no maintainer and does not
run out of the box — its dead-ROI roster path resolves into a quarantined export — and a
published negative should not rest on something nobody can execute
([the todo](todo/2026-08-19-the-connectivity-pipeline-has-no-owner.md)).

**The port is validated two ways, and the second is the interesting one.**

*On identical inputs it reproduces the reference exactly.* The coefficient was written from
Cutts & Eglen (2014) with the MATLAB `if2_sttc.m` deliberately unread, so the comparison is
a real check rather than a diff of two transcriptions: across five recordings and several
thousand pairs the worst disagreement is **2.2 × 10⁻¹⁶**, the NaN pattern matches, and
Louvain lands on the same partitions (Q agreeing to 10⁻¹⁶). `tests/fixtures/ref_sttc_matlab.json`
carries those vectors so CI re-checks it without a store or MATLAB.

*Across the corpus it agrees on the verdict while disagreeing on the window.* This repo
scores the producer's analysis window where there is one and the baseline region otherwise;
interface2 caps at 1200 s after a 120 s solution delay. On the recordings where the two
differ, bugarach's window runs **1740–1800 s** against interface2's 1200 s, so more cells
clear the "at least one event" bar — `n_active` is higher on 10 of 78 fast recordings and 8
of 77 slow, and **never lower**, which is the signature a longer window predicts. It matches
exactly on the rest.

Even so the verdicts agree on **98.7%** of recordings in both streams (77 of 78, 76 of 77),
and the median difference in z is **0.03** whether or not the window matched. Each stream's
single disagreement is a recording whose active-cell count moved.

**Dead ROIs need no handling here, and that is a finding rather than an omission.** The
producer decides which cells are alive and exports accordingly, so there is nothing for this
analysis to filter. It is *also* provably moot: the R team's rejection rule is
`rejected = base_empty AND drug_empty AND hik_empty`, so a rejected cell is **by definition**
silent in baseline, and this measurement already drops any cell with no events in the window.
Checked rather than assumed, while a roster was briefly being applied here: **all 66 rejected
ROIs had zero baseline events**, and running the corpus with and without it reproduced every
count. So FOUNDATIONS §9's point — that the *rule* is not computable inside this repo, needing
drug and high-K rows — costs this measurement nothing either way.

**That is a stronger result than exact reproduction would have been.** The answer does not
depend on which of two defensible windowing conventions is used.

**Three things about those numbers are worth stating, because none of them was true of the
figure this report previously quoted.**

*The fast stream had never been measured.* `eval_modularity_null` hardcoded the slow channel,
for a stated reason — slow is the rate-independent marker, and fast is the connectivity
project's negative control because it fails rate-, node- and Δt-matching. But that objection
is about a **between-group** contrast, and this is a **within-recording** test: each Q is
compared against surrogates of that same recording, holding node count, event counts and
sparsity fixed. Nothing crosses a group boundary, so the matching failure does not reach it.
The instrument was generalized to take a channel, its default left unchanged, and run.

*The denominator was wrong, in the direction that flatters the result.* A recording too sparse
for Louvain to score returns no modularity at all, and `above_null_Q` is computed as
`Q_obs > q_hi` — which is false for a missing value, so those recordings entered the CSV as
zeros and read as "tested, not modular". They were not tested. Excluding them — one fast
recording, four slow, all with 3 to 5 active cells — is the same **undefined is not negative**
rule this report applies to its own membership test.

*And the crosstalk control agrees, where it exists.* The connectivity project's
penumbra-subtracted modularity file — slow stream only, and still the interface2 one — puts **1 of 69** recordings above
null (1.4%) once the same undefined-is-not-negative correction is applied to it; it carries
eight recordings with no computable modularity, against four in the unsubtracted slow file,
which is the same loss of testable material penumbra subtraction costs the membership test.
So removing the optical overlap does not reveal modular structure that was hiding under it.

*The roster underneath had been quarantined.* The published slow file was built with a
dead-ROI roster the R team has since moved to `2R/QUARANTINE/` as producing "plausible wrong
answers". Re-running slow on the current roster changes **nothing at all** — the same 83
recordings, the same active-cell counts, the same verdict on every one — so the published
number stands. That is a check that could have failed and did not. ⚠ The connectivity
pipeline's default roster path still points at the quarantined vintage, which is theirs to
repoint.

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
  no test; that rule excludes 36 of the 84 fast recordings, and it excludes them unevenly
  across groups.
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
  misses — overlapping groups in particular, which modularity handles badly. This is now the
  main route by which the negative could still be wrong, and it applies to both streams. ⚠
- **The penumbra-subtracted modularity run covers slow only.** The published pensub file is a
  slow-stream file, and this work did not rebuild it for fast. So the crosstalk control is
  complete for the membership instrument in both streams, and for modularity in slow. ⚠

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

1. **Nothing, for the assembly question.** It is answered, now in both streams. Reopen it only
   if the modularity result is overturned — the likeliest route being a method that finds
   *overlapping* groups, which modularity cannot — or if a store arrives whose penumbra
   estimate is materially better.
2. **Do not plant assemblies in the generator.** An earlier version of this report
   recommended it; on this evidence the generator's uniform draw is a correct model of the
   preparation, and planting groups would make the benchmark *less* faithful.
3. **Do not port an assembly detector to score it on our corpus.** It would lose on
   membership recovery, and it would lose because the tissue has no membership to recover —
   a fact about the preparation, not a result about the method.
4. **If the core–periphery reading is to be used for anything**, fit it and test it against
   alternatives rather than inferring it from two other measurements.

## How to reproduce this

**Everything takes an export folder.** That is the input contract and the whole input — no
store, no environment variable, no companion database. The power analysis needs nothing but
the repo.

    # the membership measurement
    python tools/assess_archive.py --store <export folder> --out <dir> \
        --stream fast --assemblies

    # modularity, in this repo, no MATLAB
    python tools/modularity_null.py --folder <export folder> --stream fast \
        --out <dir>

    # power under the rule the corpus is actually scored by
    python tools/assembly_power.py \
        --geometry-from <dir>/assessment_real.json --stream fast \
        --verdict-only --out <figdir>

    # the figures, then the report
    python tools/make_assembly_closed_figure.py --power <figdir>/assembly_power.json \
        --pensub <dir>/pensub_cmp_fast_k3.json <dir>/pensub_cmp_slow_k3.json \
        --folder <export folder> --slice <id> --also docs/learned
    python tools/make_modularity_figure.py \
        --fast <dir>/modularity_null_fast.csv --slow <dir>/modularity_null_slow.csv \
        --also docs/learned
    python tools/build_assembly_report.py --src docs/assembly_report.md \
        --figures <figdir> --also docs/learned

The membership test is in `bugarach.assembly`, modularity in `bugarach.graph`, the power
analysis in `tools/assembly_power.py`; all three are exercised by the test suite, and
`tests/test_graph.py` checks the modularity port against MATLAB vectors without needing
either a store or MATLAB.

**One exception, and it is the only claim here you cannot re-derive.** The crosstalk
control was computed on **2026-08-19 against `.mat` stores, before store access was
closed**, because no penumbra-subtracted export folder exists — `exports/bugarach/` holds
three folders and none of them is pensub. Its numbers (21 of 26 fast, 21 of 25 slow, sign
test p ≈ 0.004) are not withdrawn and nothing suggests they are wrong, but **nothing in the
current inputs can reproduce them.** Closing that needs one export folder from the producer:
[`2026-08-20-the-crosstalk-control-needs-a-pensub-export.md`](todo/2026-08-20-the-crosstalk-control-needs-a-pensub-export.md). ⚠

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
