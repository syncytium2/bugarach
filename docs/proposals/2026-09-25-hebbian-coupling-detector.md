# A coupling that learns within one recording — the 1986 plasticity rule as a detector

> **Status: DRAFT for Tony. Nothing here has been built or run.** Goal:
> [unsupervised learning](../goals/unsupervised-learning.md). It needs no ruling that is still open
> to start its first stage, and it does not touch the stopped surrogate screen: the rule learns
> without training negatives, and the one null it uses is the assessor's existing circular shift,
> used as a significance test only.
>
> Tony chose on 2026-09-25 to take the rule into bugarach as a stamped copy of the two functions
> from `syncytium2/clamor`, not as a dependency and not as a move (both repositories are his;
> clamor is private, so a dependency would break CI and outside reproduction here).

Abbreviations: **ROI**, region of interest, one imaged cell; **STTC**, the spike time tiling
coefficient, the pairwise coincidence measure `bugarach.graph.sttc_matrix` computes; **Co**, the
coactivity kernel of the 1986 paper's equation 7; ***W***, the learned coupling matrix, one entry
per ROI pair; ***s*₀**, the resting coupling every entry starts at; ***D*** = *W* − *s*₀, the
learned deviation; ***w***, the coincidence width in seconds; ***q*₀**, the size of one
plasticity step.

---

## The idea

Treat each ROI as a unit coupled to every other. Walk through a baseline window in time order. Every
time two ROIs have event onsets close together, strengthen their coupling; every time they have
onsets a near-miss apart, weaken it. At the end of the window, *W* is a record of which pairs kept
coinciding more than their timing would give by chance, and a frame in which the active ROIs are
strongly coupled to one another scores high.

That is a Hebbian rule, and a plain one does not work here: coupling grows for any two busy cells,
so it learns event rates rather than coordination, and it grows without bound. The rule below
comes with both repairs already in it.

## The rule: von der Malsburg & Schneider 1986, equations 7 and 8

The source is *A Neural Cocktail-Party Processor*, Biological Cybernetics 54:29–40 (1986),
DOI [10.1007/BF00337113](https://doi.org/10.1007/BF00337113), as transcribed in
`syncytium2/clamor` (`clamor/malsburg1986.py`, `CocktailParty.coactivity` and
`CocktailParty.control`). In that model the coupling is not trained across stimuli: it changes
during a single stimulus, which is what makes it usable one recording at a time.

**Equation 7, the kernel.** Co(Δ*t*) is **+1** when two bursts coincide, **0** when they overlap
for half their duration and **−1** in antiphase. The paper states it exactly as a cosine for the
case of a burst lasting half the period, and describes other cases in words; clamor's general form
is its own interpolation, marked `INTERPOLATED` in the code.

**Equation 8, the bound.** Each step is scaled by *q*(*s*) = *q*₀ · (1 − ((*s* − *s*₀)/(*s*₀ · *s*_d))²),
largest at rest and zero at *s*₀(1 ± *s*_d), so every coupling stays within 80 % of its resting
value at the paper's *s*_d = 0.8. The paper's reason is the one that matters here: a stray episode
of false synchrony cannot move a coupling far.

**The subliminal rule** (paper, p. 33): a cell that has not burst recently changes no synapse. For
us this is automatic, below, and it is the right behaviour under FOUNDATIONS §9: an ROI with no
events in the window keeps *s*₀, is not penalised, and is not dropped.

## What changes for calcium events

The 1986 units are oscillators, and "antiphase" means half a period away. Calcium events are not
periodic, so the oscillator is left behind and only the kernel's shape is kept, over a finite
window:

- **Pairs.** On each onset of ROI *i*, every onset of every other ROI *j* within ±*w* contributes
  one update to *W*_ij and *W*_ji, of size *q*(*W*_ij) · Co(Δ*t*). Pairs further apart than *w*
  contribute nothing. An ROI with no onsets forms no pairs, which is the subliminal rule.
- **Symmetric.** Co is even, and the update is applied to both entries. clamor updates one row per
  burst and carries an open question about which (its `update_column`); the symmetric form
  sidesteps it and is a deliberate deviation from the paper.
- **The kernel, at the one point the paper states exactly.** Call clamor's `coactivity` with
  period 2*w* and burst *w*: Co is +1 at Δ*t* = 0, 0 at *w*/2 and −1 at *w*. That is the
  burst-equals-half-period case, where clamor's interpolation reduces to the paper's own cosine,
  Co = cos(π Δ*t* / *w*) — checked in clamor's `selftest()` — so the part of the transcription that
  is a judgement call is never exercised.
- **Why that point and no other: it is rate-neutral.** Over |Δ*t*| ≤ *w* that cosine integrates to
  zero. For two ROIs whose onsets are independent, Δ*t* is close to uniform over the window, so the
  expected update is zero **however busy either ROI is**: the covariance rule's subtraction of
  chance, without a rate term. (The bound *q*(*s*) varies as *W* moves, so this holds to first
  order.) Any other window length breaks it — longer than *w* and the
  negative lobe outweighs the positive, so busy pairs drift down; shorter and they drift up. This is
  derived here, not measured, and stage 1 tests it.
- **On the frame grid, the ends count half.** Onsets sit on a frame grid of about 0.1 s on this
  folder (`frame_interval_sec` in `slices.csv`; the jitter run's README, Figure 2), so Δ*t* takes
  only whole-frame lags. Summed over lags −*K* … *K* frames with *w* = *K* frames, the cosine gives
  **−1, not 0**, for every *K*, because both ends sit at −1. The integral's zero is recovered by
  weighting the two end lags by one half (the trapezoid rule), and the rule is written that way.
- **The width.** *w* is set from the ruled jitter constant (Tony, 2026-09-22; `decisions_pending.md`
  item 2): measured cross-ROI jitter of **0.106 s fast** and **0.135 s slow** — one to two frames.
  A width of one jitter would leave the kernel three lags long, all shape gone, so *w* is a
  multiple of the jitter; two, three and four jitters are the stage-1 sweep, and one value is
  frozen before stage 2 reads a real recording. The same README warns that anything putting ROIs
  into the same frame — motion, light, neuropil — sharpens the zero-lag peak; that is the positive
  lobe's centre, and another reason distance and crosstalk matter below.
- **The step.** *q*₀ is an open question in clamor itself: the paper's stated 0.01 against a step
  about twelve times smaller that its own figures imply. Stage 1 runs both and one between.

## What the detector reports

Three readouts, from least to most assumption:

1. **Per recording — is there learned structure?** A statistic of *D* (its Frobenius norm and its
   leading eigenvalue), against the same statistic after the same rule has run on the assessor's
   per-ROI circular-shift surrogates of the same window (`assess.circular_shift_trains`). This is a
   significance test, not a training contrast; the rule never sees a surrogate while it learns.
2. **Per recording — what shape?** The spectrum of *D*, and an overlap-tolerant grouping of its
   positive part (mixed-membership or link communities). This is the readout that could answer the
   assembly report's main open risk: modularity finds a partition, and cannot see cells that belong
   to more than one group ([the todo](../todo/2026-08-20-what-could-still-overturn-the-assembly-negative.md), item 1).
3. **Per frame — a call.** For the set *A*(*t*) of ROIs with an onset within *w* of frame *t*, the
   score *E*(*t*) = Σ over pairs in *A*(*t*) of *D*_ij, with *D* frozen at the end of the window and
   the threshold set on the circular-shift surrogates. This is the readout that makes it a detector
   comparable with the six coded ones.

**Baseline only**, as FOUNDATIONS §9 requires. Carrying a baseline *W* into a treatment window is
the quiet → busy transfer the goal page lists under *Waiting on Tony*, and is out of scope here.

## What could make this worthless — checked before anything is built

Two things, each cheap, each with a way to fail.

**Check A — is there anything beyond a busy core?** The assembly report describes this field as a
core with a long tail and no recurring modules. If the coupling ends up near rank one, readout 2
has nothing to find and readout 3 reduces to a weighted count of active ROIs, which is roughly
CoactDetect with per-ROI weights. On the existing STTC matrices of the baseline windows, per
stream: the share of off-diagonal variance left after the leading eigenvector, against the same
share on circular-shift surrogates. The assembly report's eigenvalue statistic was computed on the
participation matrix of detected events, not on the STTC graph, so this has not been run.
**Proposed stop:** if the residual is at null level in most recordings of a stream, readout 2 is
dropped for that stream and the proposal continues only if readout 3 can beat CoactDetect in stage 1.

**Check B — is the learned matrix just STTC?** With a rate-neutral kernel and a bound, *D* may be
a monotone function of a signed coincidence count, which is a close cousin of STTC. What the rule
adds over STTC is the negative lobe (a near-miss counts against a pair) and the bound (one burst of
coincidences cannot dominate). This check needs the rule, so it runs first thing in stage 1: rank
correlation between *D* and the STTC matrix at the same *w*, per recording. **Proposed stop:** if
it is above 0.9 in most recordings, the rule is STTC with extra steps, and that is the finding; the
detector is not built, and readouts 1 and 2 are run on STTC directly.

The stop thresholds are proposals, for Tony to set or change before any number is read.

## Stages

0. **Check A**, on the default dataset's baseline windows, both streams. No new detector code.
1. **Simulation.** The rule on synthetic recordings with known answers: independent trains at
   mismatched rates (the rate-neutrality claim: *D* should stay at *s*₀ within surrogate spread),
   planted overlapping groups at the strengths `tools/assembly_power.py` already plants (can it
   recover them where the membership test has power?), and CoactDetect on the same recordings
   (does readout 3 add anything?). **Check B** runs here. *w* and *q*₀ are chosen here and frozen.
2. **Real baseline recordings**, both streams, reported per group in the order DI, OVX, MALE, ORX —
   never as a pooled number alone, because group effects run in opposite directions (§9).
3. **Back to clamor.** What *q*₀ does on real calcium data, and whether *W* goes block-diagonal or
   collapses on the core, written as a finding in clamor. clamor has only synthetic stimuli and a
   step size it cannot pin; this is the first real data its rule will see.

A fourth stage waits on data bugarach does not have. **Distance.** The export carries no ROI
positions. If it did, the question is whether *D* falls with distance and whether that falloff
survives the penumbra-subtracted store — nearby ROIs share scattered light, so a coupling learned
between neighbours may be optical crosstalk, not coordination. Distance is a covariate to test
against, never a restriction on which pairs couple: a neighbours-only network would mostly learn
crosstalk. Under ADR-0007 the request states an outcome: *each ROI's centroid, in µm, in the export
folder; every other file unchanged* — drafted here, posted by Tony.

## How the code arrives

`coactivity()` and `control()` are copied from `syncytium2/clamor` into
`src/bugarach/detectors/` with a line-1 provenance stamp (`vendored from syncytium2/clamor @ <sha>`)
and never edited in place, the convention `docs/session_protocol.md` and the murderboard copies
already follow. Both repositories are BSD-3-Clause under the same owner; clamor's open licence item
concerns its own vendored tooling, not this model. `tools/check_vendor_freshness.sh` gains a clamor
family so the check reports when clamor's rule moves on. The copy is torch code; torch is already in
bugarach's `dev` and `dl` extras, so the suite and CI can run it.

At the kernel point chosen above, Co is one cosine, and copying sixty lines for it looks like
overkill. The copy is kept because stage 1 sweeps *w* against the window, where the interpolated
form is exercised, and because a stamp is how a later change to clamor's rule gets noticed here.

## What this does not claim

- That the preparation has assemblies. The assembly negative stands until something overturns it;
  this is one instrument that could, and a null result from it is a result.
- That rate-neutrality holds for real trains. It is derived for independent, stationary trains, and
  real trains have a refractory floor and slow drift. Stage 1 measures it.
- That the 1986 model reproduces its own paper. clamor's record says the stability test reproduces
  and the one-step amplification does not; only equations 7 and 8 are used here, and neither is
  what fails there.
