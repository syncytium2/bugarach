# The ROI-swap null — a surrogate made of real trains

> **Status: NOT RECOMMENDED — review did not converge. Nothing here has been run.**
>
> Three review rounds. The first two found errors in a plan that looked sound. **The third found that
> the plan cannot be built on this cohort and that its two "free" stages cannot fail** — which means
> approving them would produce a record of passed gates that validates nothing. The hostile reviewer's
> summary is that this proposal *"has argued itself out of its experiment without saying so"*, and
> after checking the load-bearing numbers, that verdict stands. **Do not approve any stage below as
> written.** What survives, and what should replace it, is in
> [the verdict](#verdict-after-three-rounds) immediately after this banner.
>
> The document is kept, unconverged and marked, because the path to that verdict is worth more than a
> tidy withdrawal — the same reason the two earlier withdrawn reevaluations were kept. The reports are
> [roles 1-4](../reviews/2026-09-12-the-roi-swap-null-roles-1-4.md) and
> [roles 5-11](../reviews/2026-09-12-the-roi-swap-null-roles-5-11.md), and the run record is
> [here](../reviews/2026-09-12-the-roi-swap-null_2026-09-12.md). **What that review changed is
> listed in the revision note at the end** — read it before treating any claim here as new.
>
> Every screen number was read from the run's own files in
> `<darkroom>/bugarach/2026-09-11-surrogate-screen/` on 2026-09-12. Literature claims carry their
> paper, or are marked not-held.

---

## Verdict after three rounds

**The swap grid cannot be built on this cohort.** The construction requires each swapped ROI from a
different donor recording, with donors confined to the target's own mouse fold. The median recording
has 31.5 ROIs and most mice contributed two recordings. The round-3 hostile reviewer simulated five
mouse folds over fifty seeds and reports this many of the 84 targets as buildable. ⚠ **That simulation
has not been reproduced by this session** — it is the first thing the replacement table below should
recompute, since the verdict leans on it. The `rigid_shift` accuracies further down were re-checked
against the run files and hold.

| swap fraction k/N | global donor pool | within-group donor pool |
|---|---|---|
| 0.25 | 82.8 | 9.3 |
| 0.5 | 39.1 | 0.9 |
| 0.75 | 14.3 | 0.2 |
| 1.0 | 3.7 | 0.0 |

The within-group chimera — the group side quest's informative arm — **cannot be built at all**, and the
recordings buildable at high k/N are the small ones, so dose is confounded with recording size.
Within-mouse and within-session matching allow at most two swapped ROIs.

**The two stages offered for free approval cannot kill the design.** The dispersion stage cannot reach
its STOP, because the tight matching levels it would need to separate can swap only one or two ROIs and
so cannot separate; its GO therefore carries no information. The construction-validity stage's only
STOP is a builder assertion, and its own predicted outcome — the discriminator above chance — was given
no consequence. Both would pass. **A gate that cannot fail is not a gate**, and a record of two passed
gates would read as justification for the compute stage.

**The alternative that was never measured may already do the job.** `rigid_shift` — whole-train
shifting *within* a recording — keeps slice, day, silent-ROI composition and rate scale, which is
exactly what the swap loses on its largest objection. On `steps_excluded` fast its per-ROI
discriminator accuracy is **0.495-0.524 across all six J values**. The case made against it here was a
count-difference argument that was never checked against those numbers. **The swap's only advantage is
avoiding the splice and edge leaks of within-recording shifting**, and this document never showed that
advantage outweighs losing preparation identity.

**What survives.** The support-violation argument is sound: a chimera made of real trains cannot
manufacture an interval real data never produces. So does the untouchable-floor finding and the
correction of the seed-0 voiding (section 5), which stands independently of this proposal and is the
most useful thing the review produced.

**What should replace this.** Not revision 4 of the same plan. A **single leak-versus-destruction
table** putting the within-recording nulls (`rigid_shift`, `circular_shift`, `trial_shift`) and the ROI
swap side by side on the same cohort, with a **donor-feasibility table** computed before anything is
proposed, and gates that are **paired** (each target against its own chimera) with margins declared in
the document. Only if the swap beats the within-recording nulls on that table is there a case for it.

⚠ **The group side quest's verdict is right for a different reason than section 8 gives.** Group
nested in imaging day is, on this cohort, group nested in mouse — true of any between-animal design,
and mouse-held-out folds handle random day effects. What folds cannot fix is **group aligned with
calendar era**: several imaging months are single-group (DI-only in 2024-09, 2025-07, 2026-03 and
2026-06). And the within-group chimera cannot be built anyway. A *negative* group result — group not
learnable — would still be interpretable despite the confound.

---

## The ask (as written for revision 3 — superseded by the verdict above)

**Approve the two arithmetic stages. They cost no compute, and either can kill the design before
anything is trained.** If both pass, the training stage is a separate decision with a number
attached. Tony said on 2026-09-12 that a session is live on the Windows workstation and can take the
compute.

**Do not approve the group-identity side quest on this cohort.** Group is perfectly confounded with
imaging day in the approved export — 42 dates, none carrying more than one group — so a positive
result could not be told apart from a day effect. Section 8 says what a future cohort would need.

⚠ **This does not reopen the surrogate screen.** Tony stopped that thread on 2026-09-12 — his
recorded answers were that the family-size question needed discussion before deciding, and to stop
there for now. Nothing here runs the screen or changes its verdict rule.

Why it is worth asking at all: **every train in a chimera is a real train**, so the failure that
killed the first label-free detector — a surrogate manufacturing within-ROI intervals real data
never produces — is not reduced here, it is *unavailable*. That is the one property no amount of
tuning gave the dither family.

Why now: **pre-registering this experiment's statistic family is legitimate today and impossible
later.** Once a single run exists, no declaration can be distinguished from a choice made with the
numbers in view.

**Two things this document does not decide.** The band-statistic family size is Tony's and stays
open, and the thirteen band statistics are deliberately not scored against their floor. Where the
plan says an intractable candidate may become *unnecessary*, that is a consequence for Tony to rule
on and not a pruning under the 2026-09-10 no-pruning ruling.

---

## 1. What failed, and what it looks like

The first label-free detector was stopped by its own murderboard on 2026-09-10. Its null was
independent per-onset dithering, which displaces each onset separately and therefore manufactures
within-ROI intervals shorter than any real one. A single count of sub-floor intervals then separates
real from surrogate **using no cross-ROI information at all.**

The 2026-09-11 screen measured it on the **senktide cohort** — 543 windows from 29 recordings and 18
mice, not the `steps_excluded` folder the rest of this document uses. Each row below is the range
over all six policy-by-time-base rows for that stream and J, so the table summarises all eighteen
(`reproduction/leak_table.csv`, `reproduction/reproduction.json`):

| stream | J (dither half-width, s) | real share sub-floor | dithered share | leak AUC |
|---|---|---|---|---|
| fast | 1.6 | **0.0** | 0.306–0.331 | 0.653–0.666 |
| fast | 2.5 | **0.0** | 0.387–0.425 | 0.693–0.713 |
| slow | 2.5 | **0.0** | 0.173–0.180 | 0.586–0.590 |

`real_share` is exactly zero in **all eighteen** rows. The leak is a **support violation**: not a
distribution that differs, but a region of the space where real data has no mass and the surrogate
has plenty.

⚠ **Two honest qualifications on that table, both from the review.** The floor is *defined* as the
shortest within-ROI interval present in the screen's own analysis windows, so `real_share = 0` cannot
take another value — it is a definitional zero, and the support argument rests on the extraction
physics rather than on that row. And the AUC column carries no information the share column does not:
`AUC = 0.5 x (1 + share)` exactly, per the run's own report. One measurement, shown twice.

⚠ **Where the floor comes from is an open question for the producer, not a finding.** The floors are
0.39999999999997726 s and 3.1999999999999886 s, identical in every row. Revision 2 read their
alignment to a 0.1 s grid as the signature of a pipeline constant, but **all 84 `steps_excluded`
recordings have `frame_interval_sec` = 0.1**, so every interval is a multiple of 0.1 s and the
alignment is no evidence at all. The run's own report says the extractor's shortest emittable
interval "is the producer's number and is not known". That matters here because it decides whether a
chimera inherits the floor automatically, and the answer is a conversation with the producer.

**The obvious control could not see it.** Dither-of-dither was blind because its own reference class
already contained the leak — which is why these numbers had to come from a per-statistic leak screen.

### Mixing does not repair a support violation

A natural remedy is to draw each negative from a randomly chosen generator, so the model cannot learn
one generator's shape. It was examined on 2026-09-12 and does not work, for the following reason.

Against a mixture the optimal discriminator compares `p_real` with the weighted mean of the members'
densities — the noise-contrastive estimation result of **Gutmann & Hyvärinen (2012)**, JMLR 13:307-361,
on the shelf at `ml/gutmann_hyvarinen_2012_nce.pdf`. Wherever **any** member puts mass where real
data has none, that ratio is zero and the window is classified with certainty, with no generator
identification required. **Mixing divides the leak's share; it does not close the hole.**

The distinction this turns on:

- **Support violations must be absent per member.** They are inherited by the union.
- **Soft distributional differences** dilute — but only when members deviate in *different
  directions*. Every member of the dither family shifts the ISI distribution the same way, so for the
  screen's actual candidates the soft part does not dilute either.

A mixture's implied null is also a **disjunction** — "some member could have produced this" — so the
test inherits its weakest member's destruction. If mixing is used at all, the rule is **mix over
mechanisms, never over strengths**.

### A floor no surrogate can move, and the swap inherits it

Filed as
[an empty baseline is a group feature](../todo/2026-09-12-an-empty-baseline-is-a-group-feature-and-39-percent-of-every-surrogate-is-the-data.md),
and re-derived for this revision:

**There is a floor on how many ROIs any surrogate can change, and it is about 38-39%** — fast 0.379,
slow 0.390 on `steps_excluded`. Generators that need a per-ROI estimate leave more untouched: the
ISI-dither and joint-ISI families 48-58%, pattern jitter about 55%. **The floor is not flat in J on
fast** — trial shift runs from about 0.46 at J = 0.1 s down to 0.38 at J = 2.5 s — but its minimum is
stable.

**That floor is the share of ROIs with no event in the baseline window, to three decimals** (0.379
fast, 0.390 slow, recomputed from the export folder), so the untouched ROIs are empty baselines: a
surrogate cannot move an onset that does not exist. On `cossart` the dither family and controls sit
at 0.039-0.073, but the full candidate range there runs up to 1.000.

Tony's ruling of 2026-09-12 is that an empty baseline is a **feature of some groups** and matters as
much as an active ROI.

⚠ **This is a share of ROIs, not of training examples, and revision 2 conflated the two.** The
discriminator's unit is a pooled window pair, and a pair is identical only when *every* ROI in that
window is unchanged. Windows with no event in any ROI are **8.7% on fast and 12.4% on slow** — an
upper bound on identical pairs. So the effect is not that 39% of negatives are coin flips; it is that
empty ROIs **dilute every pooled feature**. And the question revision 2 left open is settled:
`surrogate_discriminator.py` never refers to `unchanged`, so **there is no exclusion** of them.

**The ROI swap inherits this exactly** — swapping an empty ROI for another empty ROI changes nothing.
It is not a surrogate defect, no candidate choice fixes it, and it does not belong in a verdict rule
that ranks candidates. It belongs in what the objective does with those ROIs, and the three options
are accept, weight, or drop, with drop the one FOUNDATIONS §9 rules out by default because it
conditions on having fired.

---

## 2. Why this preparation makes surrogates hard

Everything rests on the null, and not as a modelling preference. **Amarasingham, Harrison,
Hatsopoulos & Geman (2012)**, *J Neurophysiol* 107(2):517-531, doi:10.1152/jn.00633.2011
(`surrogates/amarasingham_2012_jitter_method.pdf`) make the rule explicit: what the resampling
conditions on *is* the null hypothesis. Get the surrogate wrong and the detector answers a question
nobody asked.

Three properties of continuous slice imaging rule out the standard toolkit.

**There are no trials.** Most of the surrogate literature recombines across trials because trials are
the structure it has. There is nothing to recombine along that axis here.

**Events are rare and slow.** Baseline per-ROI rates run 0.0052-0.0190 Hz interquartile (FOUNDATIONS
§9, re-derived 2026-08-20 from the approved export folder), so the legitimate training signal is
thin — which matters enormously later, because a shortcut does not have to be large to dominate a
thin signal.
⚠ **That range does not reproduce, and the reading this proposal needs has a lower quartile of
zero.** An open finding
([the FOUNDATIONS rate range does not reproduce](../todo/2026-09-10-the-foundations-rate-range-does-not-reproduce.md))
records that GLOSSARY calls the same two numbers a quartile across *recordings* where §9 calls them
per-*ROI*. Recomputed from the export folder for this revision, none of the readings gives
0.0052-0.0190:

| reading | fast (Hz) | slow (Hz) |
|---|---|---|
| per-ROI, zeros kept (the §9 rule) | p25 **0**, p75 0.0100 | p25 **0**, p75 0.0100 |
| per-ROI, events only | 0.0017-0.0184 | 0.0025-0.0200 |
| per-recording mean | 0.0036-0.0186 | 0.0024-0.0109 |

The leak prediction needs the first row, whose p25 is zero because roughly 38-39% of ROIs are empty.
So **a "3.7x spread" is not the right way to state the heterogeneity** — the distribution is
zero-inflated, and the across-ROI dispersion in a chimera is dominated by how many empty ROIs it
draws, which is the same untouchable floor as above.

**Within-ROI structure is sharply bounded** — the floor above, which is the trapdoor the first design
fell through.

---

## 3. The proposal: the ROI swap

**The incumbent alternative, first.** `rigid_shift` — whole-train shifting — is already the only
candidate in the 2026-09-11 screen surviving contiguously out to 1.6 s on fast. A reader should ask
why not simply use it. Two reasons: bugarach's implementation does not wrap, so it loses onsets at
the window edge, which is a *count* difference and therefore the same failure mechanism by another
route; and its slow-stream survival is not a survival at all but a single isolated non-significant
point at P = 0.08, failing at 0.7 s below it and at 2.5 s above.
⚠ `circular_shift` and `window_circular_shift` also exist and *do* wrap, so the edge gap is narrower
than it looks — but wrapping splices the record's end to its beginning, manufacturing one arbitrary
and possibly sub-floor interval per ROI per window. That is a real comparison to make, and it belongs
on the ladder below rather than in a paragraph.

**Construction.** Take a target recording with N ROIs over duration T. Replace **k of N** ROIs with
duration-matched baseline trains, **each drawn from a different donor recording**, so no two swapped
ROIs were ever simultaneous with each other or with the target. Two knobs: the **swap fraction**
`k/N`, from 0 (real) to 1 (full chimera); and the **matching level**, the donor pool.

Each chimera is paired to its target: same N, same T, same frame rate, same window. Donors must
supply a baseline stretch of at least the target's duration **at the target's `frame_interval_sec`**,
and are otherwise not used. Nothing is padded, resampled or stretched.

**What is won.** On any within-ROI statistic the null's support is a **subset** of the real data's
support, so a support violation is unavailable. No sub-floor interval can be manufactured, no onset
lost to a window edge.

**What is not won, and revision 1 got this wrong.** Subset-of-support rules out a support violation;
it does **not** rule out a per-ROI *density* difference, and several are available using nothing but
untouched real trains:

- **Window position within the donor's own recording.** Rate drifts across a baseline window —
  measured here, **upward**: the median recording has more events in the second half, by 4.3% of its
  total on fast (58% of recordings) and 14.7% on slow (71%). Donors not matched on within-window
  position therefore carry systematically different rates. (Revision 2 asserted the drift ran down,
  without a source; the data say otherwise.)
- **Donor sampling weight.** Sampling uniformly over ROIs lets large-N recordings dominate the pool;
  uniformly over recordings does not. The two give different chimera marginals and only one matches
  the real class.
- **Duration eligibility.** Long-T targets can only draw from long-baseline recordings. **Small on
  this folder:** 75 of 84 baseline windows are exactly 1200 s, 8 are 1140 s and one is 1020 s.
- **The encoder.** `encode()` truncates rather than rounds, and **clips** out-of-range onsets onto
  frames 0 and n-1 rather than dropping them, so a one-frame duration mismatch manufactures a
  boundary pile-up. And truncation bites even at *equal* frame intervals, because floors are stored
  just under the grid: `int(3.1999999999999886 / 0.1)` is **31**, not 32. On `steps_excluded` every
  recording shares `frame_interval_sec` = 0.1, so a grid mismatch cannot arise there — but **`cossart`
  varies across nine values from 0.0926 s to 0.1190 s**, and a donor re-quantised onto a different
  target grid can land an interval **below the floor**, the exact violation this design claims to make
  unavailable. Hence the frame-rate clause in the construction, and the builder assertion below.

So the honest claim is: **the chimera cannot commit a support violation; it can still differ in
per-ROI density, and that is a testable property of the builder rather than a guarantee.**

**Where the risk goes.** ROIs within one slice share bath temperature, drift, photobleaching,
imaging depth, health and rate scale; a chimera's do not. A discriminator can therefore win by
detecting **slice identity**, which lives in the cross-ROI space the detector is supposed to use.
This is the largest of the three objections the plan must survive.

**And the null is compound.** The same Amarasingham paper discusses the nearest relative of this
construction. Jitter is its worked example; trial shuffling is, in its own words, "another, familiar,
example" of conditional inference, and of it the paper says (emphasis added):

> "an excess of synchronies in the original pairing, relative to the trial-shuffled pairings,
> **rejects the hypothesis that all pairings are equally likely**, not a hypothesized lack of
> precision of spike timing."

⚠ Trial shuffling recombines trials *within* a session; the ROI swap recombines *across*
preparations. The paper's caution transfers by analogy, not by direct treatment.

The ROI swap's null is "these ROIs are independent **and** exchangeable across slices". A rejection
does not isolate coordination, and the plan's ladder exists to separate the conjuncts rather than to
pretend they are one. **That paper also recommends jitter over trial shuffling** when the goal is
fine-temporal correlation, because shuffle-correction flags "because of slow, common rate fluctuations
alone". Shared slow fluctuation across ROIs in a slice is plausible — common bath, drift and bleaching
— though this document has not measured it. Citing the paper as authority for this construction while
omitting that recommendation would be selective, so it is stated here and the plan is built against it.

⚠ **One more cost of totality.** A null that destroys everything identifies nothing: the negative
class now differs from the positive on many axes and gradient descent takes the cheapest. This is
Elsayed & Cunningham's objection (`surrogates/elsayed_cunningham_2017_byproduct.pdf`), and
Amarasingham, Geman & Harrison 2015 on nonidentifiability is the same point
(`surrogates/amarasingham_2015_ambiguity_nonidentifiability.pdf`). It also breaks a condition of noise-contrastive
estimation. Gutmann & Hyvärinen's Theorem 1 guarantees the objective has **no other extrema** only if
the *noise* density is nonzero wherever the data density is — a condition for **uniqueness**, not for
the maximum to exist — and this design deliberately does the opposite. The practical consequence: the
learned logit need not be a density ratio where real data is coordinated and the null is not, so
**accuracy near 1 carries no effect-size information** and must be reported alongside a calibrated
measure.

---

## 4. Precedent

Recombining trains that were never simultaneous is the **shift predictor**, whose construction goes
back to Perkel, Gerstein & Moore (1967), *Biophys J* 7(4):419-440, **"II. Simultaneous spike
trains"**, doi:10.1016/S0006-3495(67)86597-4. ⚠ **Not held** — an open ask in
[`lit_needed.md`](../lit_needed.md), and the *name* is later usage: Amarasingham et al. call it the
shuffle predictor and Pipa et al. credit König (1994).

The modern population version is the **pseudopopulation**, whose defining consequence is that it
eliminates noise correlations. ⚠ **Uncited and therefore not yet admissible.** The obvious shelf
candidate does not support it — `elsayed_cunningham_2017_byproduct.pdf` contains no occurrence of
"pseudopopulation" and one of "noise correlation", in a reference title. Cunningham & Yu (2014),
*Nat Neurosci* 17:1500-1509, doi:10.1038/nn.3776 is a candidate source, now an open ask in
`lit_needed.md`; **nobody here has read it**, so this paragraph claims nothing until someone has.

**Where it is absent.** Stella, Bouss, Palm & Grün (2022), *eNeuro* 9(3), ENEURO.0505-21.2022
(`surrogates/stella_2022_comparing_surrogates.pdf`) compare six methods — uniform dither, dither with
dead time, ISI dithering, joint-ISI dithering, trial shifting and window shuffling. **No
cross-session or cross-preparation surrogate appears.** Verified by full-text search.

⚠ **That absence is weaker evidence than revision 1 claimed.** A reviewer reports that cross-subject
recombination is a routine null in hyperscanning inter-brain synchrony, where "pseudo-pairs" of
participants who never interacted serve as the control. ⚠ **Not held and not cited** — that report came
from search results, not from reading a paper, so it is a lead rather than a finding. Either way,
absence from one catalogue in one field is not absence. Three fields remain unsearched: contrastive
learning on neural time series, fMRI surrogate construction, and ecology/genomics null models.

**Trial shifting is `trial_shift`, not `rigid_shift`.** bugarach ships both as separate candidates.
Stella shifts real experimental trials, which this data does not have, so `trial_shift` **adapts** the
method to pseudo-trials cut at silences longer than 2J + f, where `f` is the pseudo-trial parameter.
It descends from
Pipa et al. (2008), whose own antecedent is the multiple-shift method of **Grün et al. (1999)**,
*J Neurosci Methods* 94:67-79 (⚠ not held, now an open ask).

⚠ **Stella's ranking is not citable here.** `docs/INDEX.md` row 125 carries a standing prohibition —
their discussion says the surrogates agree and their figure 10 says they do not, with the recommended
method the one that misses a pattern the other four find (uniform dither having been set aside). Their *measurements* are citable and are
what this document uses. The 2026-09-10 ruling records that the recommendation was a tiebreak on ease
of explanation, not a performance claim.

**The design mechanism is not ours either.** Training a classifier to separate two samples and reading
its held-out accuracy is a **classifier two-sample test**, Lopez-Paz & Oquab (2017), ICLR
(`ml/lopezpaz_oquab_2017_c2st.pdf`), which also supplies the null the plan below uses.

⚠ **Nobody has asked the people who would know.** No one has written to the Grün group asking whether
a cross-session surrogate has been tried. That is the cheapest outstanding check on this whole
section. Per CLAUDE.md, cite any reply, never quote it.

---

## 5. The precondition, and a finding that outlives this proposal

`real_vs_real` — real against real — is the null of the null. Revision 1 said it was failing on the
fast stream and that the code building it was lost. **Both were wrong**, and the correction matters
more than the proposal.

The code is `negative_control_pairs` in `surrogate_discriminator.py` on the screen branch. Its
docstring answers the question outright: each real window is paired with **another real window of its
own recording**, orientation drawn at random. It pairs *within* a recording, so it measures machinery
— folds, scaling, the null — and can measure no slice-identity leak at all. The arithmetic agrees:
candidates run at 1669 pairs, `real_vs_real` at 830.

And it is not failing. `controls/negative_seeds.json` holds **20 seeds at flag_rate 0.05** with mean
accuracy 0.4948, below chance. The 0.5386 / P = 0.035 that revision 1 quoted is **seed 0**, the single
flagged draw of twenty — a negative control flagging at exactly its nominal rate.

> ⚠ **126 of 248 fast candidates were voided on that seed-0 coin flip, while the 20-seed flag rate
> sat in the same run folder.** Among fast candidates that returned a number at all it is 126 of 126.
> That is a defect in how the voiding rule read the control, not a fact about the preparation, and it
> is worth its own todo regardless of what happens to this proposal.

Revision 1 committed the same probe-for-production substitution that withdrew both 2026-09-12
reevaluations, in a document that cited those withdrawals. **Third occurrence in this thread.**

---

## 6. The plan

Two stages cost nothing and either can end the design. The third costs real compute and is a separate
decision. Every gate names a statistic, a threshold and a unit; revision 1's gates were qualitative
and, by the review's judgement, could not have been adjudicated by two readers to the same answer.

**Units of analysis, stated once because they differ by stage:** the dispersion stage's unit is the
recording (84, clustered in 44 mice); the discriminator stage's is the window pair (1669), clustered
in recording then mouse; the training stage's is the **recording**, because slice identity is a
per-recording property; the group side quest's is the **mouse** (44 total, 10-12 per group, from
`slices.csv`).

**Folds are grouped by mouse throughout, and donors are drawn only from the target's own fold.** A
chimera has k+1 contributing mice, so a donor whose mouse sits in the test fold would otherwise put
test data in training. `mouse_folds` exists and takes one mouse label per unit, so this needs a
wrapper, not a new fold maker.

**Which folder.** `steps_excluded` first, because the whole-field-step contaminant was removed there
and every recording shares one frame interval; `cossart` second, because the *proposed* exit
criterion asks for both folders (that criterion is still an open todo, and its narrowed branch
proceeds on one) and because the untouchable floor differs roughly tenfold between them.

### Stage one — the arithmetic leak prediction (no model, minutes)

For each matching level, compute the **across-ROI dispersion** of per-ROI summary statistics within
real recordings and within chimeras. Use the definitions the project already has, in their own units:
rate as `events/win_dur` Hz (`bench.py`), burstiness as the Fano factor of 60 s bins
(`count_dispersion.fano`), median ISI, event width in frames where `has_width`.

**Figure `dispersion_ladder`:** rows are statistics, one shared x axis of matching level on the bottom
row only, one point per chimera with jitter, reference band = 5th-95th percentile of the same
statistic over real recordings. Matching level and donor count go in each row's y-axis label.

- **Expected:** dispersion rises monotonically as matching loosens; within-mouse close to the real
  band, global clearly outside it.
- **GO if** the chimera dispersion at some matching level lies inside the reference band on all four
  statistics, by a **TOST equivalence test** with the margin declared before the run. The **loosest**
  qualifying level is the chosen matching level.
- **STOP if** every level separates, including within-session. The swap is then detectable from ROI
  heterogeneity alone at any achievable matching, and no training discipline fixes it. That is a
  negative result about the construction and it gets written up.

⚠ **This stage predicts less than revision 1 claimed.** It measures dispersion of first-order
summaries, and the confounds that matter most — whole-field brightness steps, shared rundown, common
motion — are cross-ROI and *temporal*, and move none of these four numbers. Two further statistics
are therefore required, not optional: the **population-sum Fano factor** and the **pairwise
frame-coincidence count**, real against chimera, per recording.

### Stage two — construction validity (no training)

Assert what the builder claims, directly, rather than inferring it from a classifier:
`set(chimera onsets) == set(donor onsets)` after encoding, equal `n_frame` per pair, and the
encoder's boundary clip never firing. These are free and they catch the encoder defects named above.

Then run the existing per-ROI discriminator, real against chimera.

⚠ **Revision 1 expected "exactly chance" here and would have stopped on a correct build.**
`pool_symmetric` pools per-ROI columns with `("mean", "sd", "min", "median", "max")`, so `sd_count`
**is** the across-ROI dispersion stage one measures — and on seed 0 of the fast `real_vs_real` control
it is the top-weighted feature. (Per-seed feature weights are not stored, so this rests on the one
flagged seed — the same single-seed reliance section 5 warns against; it is suggestive, not
established.) This stage is therefore the powered version of stage one, not an
independent check, and a result above chance is the design's predicted leak rather than a builder
bug. The builder assertions above are what catch builder bugs.

**Figure `chimera_marginals`:** four panels, real and chimera densities overlaid, so that when they
separate, *which* panel separates names the cause — width says resampling, rate says the donor pool is
not baseline-only, count says duration mismatch.

- **GO if** the assertions hold and the discriminator's accuracy is within the declared equivalence
  margin of chance, tested against the binomial null at the **mouse** level, not the pair level.
  ⚠ At 44 mice the exact minimum detectable accuracy is about **0.684**, so this gate can only rule
  out a large leak. A GO here is weak evidence, and the margin must be declared knowing that.
- **STOP if** an assertion fails. Fix the builder and re-run.

### Stage three — the coordination test (compute: the workstation)

Train `tube` — the project's 1,149-parameter center-surround detector, which averages over cells and
so never sees which ROI is which — to discriminate real recordings from chimeras, across matching levels
and swap fractions `k/N` in {0.25, 0.5, 0.75, 1.0}, multiple seeds per cell.

⚠ **Two things this requires that do not exist.** `learn/train.py` is a supervised per-frame trainer
on *generated* recordings; there is no window-level real-versus-surrogate path, and turning tube's
per-frame score into a window logit is a weak-label pooling choice that has to be declared because it
determines what "the detector falls out of the discriminator" means. And the ablation below needs a
new registered architecture, because the `bright` bypass is hardcoded and ADR-0005 makes one file one
architecture. **Budget this stage as new code plus compute.**

**Revision 1's decomposition — "intercept is signal, slope is leak" — is withdrawn.** It assumed every
nuisance destroyed by the swap is monotone in matching looseness. The two largest documented
confounds in this tree are not: whole-field brightness steps make **74% of fast and 82% of slow
cells** appear to fire at once, and motion-correction pinning drives 12 ROIs in four recordings to a
common value. Both are real-only, both are destroyed equally at every rung, and both therefore land
in the *intercept* and would be scored as coordination. The ladder is a leak detector for static
compositional heterogeneity and is silent on every temporal leak.

What replaces it:

- **A metric x axis.** Regress accuracy on the *measured* donor-target dispersion distance from stage
  one, not on the ordinal rung, and report the **intercept at distance zero with a confidence
  interval** over mice.
- **A zero-leak anchor.** Add a **within-recording, across-time** rung: replace an ROI with the same
  recording's other ROIs re-origined from a disjoint segment. Bath, drift, depth and rate scale are
  then identical by construction, so the anchor is measured rather than extrapolated. This is the
  large-lag limit of `circular_shift` and is nearly free.
- **A planted-artifact control.** Insert a synthetic whole-field step into held-out real windows and
  show accuracy does not move. Without it, "the tube learned to recognise acquisition artifacts"
  remains the strongest alternative explanation for any positive result.

**Figures:** `accuracy_vs_dispersion` (metric x, the stage-one prediction as a reference line) and
`accuracy_vs_dose` (x = k/N, where the "step at k/N > 0" prediction actually lives). Each seed drawn
as a thin line with the mean heavy — never a mean with an error bar, because tube's own docstring
puts three probes on one channel an order of magnitude apart with one non-monotonic.

- **GO if** the intercept at zero dispersion distance is above chance by more than the declared
  margin, the planted-artifact control does not move accuracy, and the result survives the ablation
  below.
- **STOP if** accuracy tracks the dispersion regression with an intercept indistinguishable from
  chance. Self-supervision via ROI swap is then unavailable on this data — **a result about the
  preparation, worth writing up.** The thread's proposed exit criterion is written for the screen
  rather than for this construction, so this is an additional criterion, not a discharge of that one.

**The ablation.** Re-run without tube's raw-brightness bypass, which carries absolute local activity
straight past the DC-free kernel.
⚠ It does not separate what revision 1 said it did. The bypass is a *level*; a composition leak
expressed as the **variance** of the summed trace survives its removal, because the kernel cancels DC
and not variance — and for a sum of per-ROI processes at matched mean rate, greater rate dispersion
*lowers* that variance. The ablation therefore needs a **rate-matched-donor arm** to be interpretable:
donors selected to match the replaced ROI's rate within a tolerance, compared against unmatched.

---

## 7. Residual risk, and what is not settled

**Open, and not this document's to close.** The band-statistic family size, and which of the
thirteen statistics sit on the floor — deliberately not looked at, and still not looked at here. One
thing about that family *is* already settled and is not a per-statistic result: the screen's own gate
returns `correction_reach(m=13, n_splits=100, K=99)` = `band_reaches: False`, so **a family of all
thirteen cannot flag on the night's 100 splits**. That is arithmetic about the family's size and says
nothing about any statistic. Whether the intractable joint-ISI candidates are bought is also open; if
the swap succeeds they may become unnecessary, which is a consequence to rule on and not a pruning.

**Prerequisite.** The leak-by-destruction join has never been made though both halves sit in the
2026-09-11 run folder ([todo](../todo/2026-09-12-join-the-leak-results-to-the-destruction-results.md)).
Stage one consumes it rather than re-deriving it.

**Power, and it is not reassuring.** At 830 pairs the exact minimum detectable accuracy is about
**0.544**, and the 0.5386 that `real_vs_real` was voided on sits **below** it — power at 0.5386 is only
about 0.70. So the negative control is less powered than the tests it gated. Those figures treat pairs
as independent; the gates in this plan are declared at the **mouse** level, where at 44 mice the
floor is about 0.684. At 1669 independent pairs the critical accuracy is 0.521 and power against a
true 0.52 is about 0.49 — a coin flip — so a small chimera leak is unlikely to be caught by the
construction-validity stage while remaining fully available to tube. The screen's own machinery
already reports `powered: False` for **seven** of twelve positive controls — fast J 0.8, 1.6, 2.5 and
slow J 2.5, 2.8, 5.6, 11.2 — with `required_mice` up to 104 against 44.

**The unchanged-ROI question is settled, and it changes the power picture.** `surrogate_stats` masks
not-estimable ROIs when scoring preservation, and `surrogate_discriminator.py` **never refers to
`unchanged` at all** — there is no exclusion. Because the discriminator pools whole windows, empty ROIs
do not make pairs into coin flips; they dilute every pooled feature, which lowers the discriminator's
sensitivity most on the folder with the most empty baselines. Every "no leak detected" on
`steps_excluded` should be read with that in mind.

**Cost.** Stages one and two need no compute worth naming and run anywhere. Stage three is
matching levels x swap fractions x seeds, doubled by the ablation, and the seed count must be declared
before the first run because the gate is a function of it. The compute can go to the Windows
workstation session Tony named on 2026-09-12. `<darkroom>/bugarach/2026-09-11-surrogate-screen/` is
claimed under board block 065; **a new run claims its own folder before writing.**

---

## 8. Second use of the same construction: group identity

Optional, priced separately, and decided separately. It shares the instrument and one of its arms
bears on the leak above, which is why it is here rather than elsewhere.

> **As designed, this cannot run on this cohort, and the reason is in `slices.csv`.** The approved
> export holds 84 recordings on **42 imaging dates, and not one date carries more than one group.** No
> mouse was imaged on more than one date. At day resolution, **group and imaging day are perfectly
> confounded**: anything that varies by day — laser power, bath temperature, bleaching, the day's
> slice health — is indistinguishable from group. A classifier that learns group from these recordings
> cannot be told apart from one that learns the day, and no fold rule over this cohort fixes that.
>
> ⚠ **Revision 3 argued the next part wrongly, and gave wrong numbers for it.** It said 9 of 22 months
> contain more than one group; the correct count is **10 of 14 imaging months**. The error was in this
> session's own check, which sliced an eight-character date at seven characters and so split each
> month by the tens digit of the day. And the day-versus-month framing was the wrong frame: see
> [the verdict](#verdict-after-three-rounds) — the confound that folds cannot fix is group aligned with
> **calendar era**, not day-scale noise. The rest of this section is kept because it specifies the
> design a future cohort with groups interleaved across time would need.

⚠ **The motivating premise is also weaker than revision 1 stated.** FOUNDATIONS §9 records a group ×
*treatment* interaction — ORX up, male unchanged, diestrus down **under TTX** — and this design trains
on **baseline** trains. Groups can have identical baseline statistics and opposite TTX responses, so
whether groups differ *at baseline* is an **open question**, not a consequence of §9.

`tube` is a clean instrument for it because cells are pooled, so the model cannot memorise which ROI
is which and any group signal must be carried by aggregate structure. (The code takes a mean, not a
sum; permutation invariance holds either way, but the mean makes that channel a per-ROI activity
level — which is the quantity most likely to carry group.)

| condition | coordination | group identity | what it isolates |
|---|---|---|---|
| real recordings | intact | intact | is group visible at all? |
| within-group chimera | destroyed | intact | group signal without coordination |
| cross-group chimera | destroyed | mixed | the floor |

**The informative contrast is real against within-group chimera.** If accuracy holds, group lives in
single-ROI statistics aggregated over cells. If it collapses, group lives in the coordination
structure — the more interesting outcome, and the one with the most ways to be wrong:

- **Train and test within condition**, never train-on-real/test-on-chimera, or a collapse is fully
  explained by distribution shift.
- **Fold by mouse nested in acquisition batch, with batch defined before the run.** Mouse folds alone
  do not break a batch confound, and the within-group chimera *preserves* the batch signature — so
  "group lives in coordination" and "group lives in a day signature that co-varies with group" are not
  separated by the fold rule alone. On this cohort that crosstab has been produced and it is the reason
  for the box above.
- **Sex is confounded with group** — MALE and ORX are male, DI and OVX female — so report the 4x4
  confusion matrix, which shows it immediately.
- **Chance is not 0.25** with unequal classes; use balanced accuracy against a mouse-level label
  permutation. At 44 mice the exact significance threshold is 17 of 44 (about **0.386**), and about
  **129 mice** would be needed for 80% power against a true 0.35. **This is powered only for a large
  effect**, which compounds the confound: a cohort big enough to power it would also need groups spread
  across days.

**Figure `group_confusion`:** three 4x4 matrices, shared colour scale — because which pair of groups
stops being separable is the result, and no accuracy number says it.

⚠ Group identity being learnable is **not by itself bad news** for the coordination test. It bites
only if it survives within-group matching, which is what the ladder measures.

---

## Revision note — what three rounds of review changed

**Round 3, two blind passes on revision 3 — it did not converge.** See
[the verdict](#verdict-after-three-rounds). Beyond the design-level findings there, round 3 caught two
integrity errors that revision 3 introduced and that would have stood otherwise: words attributed to
Tony in quotation marks that were a handoff author's instruction, not his; and a month count
("9 of 22") that this session had presented as independently verified and that came from its own
slicing bug. Both corrected above. Also found and **not** applied, because the plan they would repair
is not recommended: the ISI families leave 55-60% of ROIs untouched (48% is operational-time dither);
the swap's untouched share depends on the swap fraction as `(1 - k/N) + (k/N) x p_both`, about 0.14
for a full chimera, not the 0.38 floor; the 8.7% "upper bound" on identical pairs is not a bound,
because pooled features collapse shifted trains to the same vector; `trial_shift`'s `f` is the dead
time, not a pseudo-trial parameter; the empty-baseline share is 0.367/0.371 in the approved periods
folder and 0.379/0.390 only after field-step removal; 129 mice is the first power crossing and the
repo's own rule gives 141; and "Pipa credits König" should read "cites König for the procedure".

**Round 2, the blind pass on revision 2 — the ones that mattered.** The group-identity side quest
**cannot run cleanly on this cohort**: group is perfectly nested in imaging day (verified independently
of the reviewer, from `slices.csv`). The 39% untouchable floor is a share of **ROIs**, not of training
examples — windows with no event in any ROI are 8.7% fast and 12.4% slow — and the question revision 2
left open is closed: the discriminator has **no** exclusion of unchanged ROIs. Revision 2 claimed four
papers had been added to `lit_needed.md` when they had not; **they are added now.** And "every
generator leaves 39%" was wrong — that is a floor; the ISI families leave 48-58%.

Also corrected in round 2: power figures (MDA 0.544 sits *above* 0.5386, not below; seven of twelve
positive controls unpowered, not six; exact binomial 0.386 and 129 mice); baseline rate drifts
**up**, not down; the leak table is the senktide cohort and summarises all eighteen rows; floor-grid
alignment is no evidence when every recording is at 0.1 s, so the floor's origin is a question for the
producer; there is no 0.05 s grid on `steps_excluded`, and the frame-interval hazard is real on
`cossart`; the per-ROI rate IQR has a lower quartile of zero; Stella's figure 10 is "the other four";
`trial_shift` adapts rather than is Stella's method; Amarasingham treats trial shuffling as "another,
familiar" example rather than the worked one; NCE's condition is for uniqueness, not existence; the
workstation claim is attributed to Tony, and the stopped screen thread is named; `correction_reach`
for a thirteen-statistic family is recorded as already computed.

**Round 1, the eleven-role review on revision 1.**

**Withdrawn:** that the fast precondition was failing (it is nominal at 20 seeds); that the code
building it was lost (it is `negative_control_pairs`); that the leak cannot be per-ROI (four density
channels are available); that "intercept is signal, slope is leak" (field steps and motion pinning
land in the intercept); that the construction-validity stage should expect exact chance (its own
features include the dispersion statistic); that the ablation separates coordination from leak (it
separates level, not composition); that Stella's ranking supports this design (a standing prohibition
forbids citing it); that mixing could rehabilitate leaky candidates (true only for non-aligned soft
differences).

**Added:** the untouchable-ROI floor and its inheritance; the compound-null statement and
Amarasingham's recommendation against trial shuffling; NCE's support condition and what breaking it
costs; the noise-contrastive and two-sample-test citations that were the document's own uncited
premises; the within-recording zero-leak anchor; the planted-artifact control; the rate-matched arm;
units, folds, donor-fold confinement, equivalence margins and power; the group-by-date crosstab and
the sex confound.

**Corrected:** eighteen rows not nineteen; 0.306 not 0.307; `rigid_shift` and `trial_shift` are
different functions; the dead review link; the definitional zero;
AUC as a restatement of share; the pseudopopulation claim demoted to unadmissible pending a reading.

**Still open against this document:** it has no figures, and three of the ones specified above are
renderable from data already on disk. That is the repo's own show-the-picture rule and this revision
does not satisfy it.

## Sources

On the shelf at `<darkroom>/bugarach/lit/`: `surrogates/amarasingham_2012_jitter_method.pdf` ·
`surrogates/amarasingham_2015_ambiguity_nonidentifiability.pdf` ·
`surrogates/elsayed_cunningham_2017_byproduct.pdf` · `surrogates/stella_2022_comparing_surrogates.pdf` ·
`surrogates/pipa_2008_neuroxidence.pdf` · `ml/gutmann_hyvarinen_2012_nce.pdf` ·
`ml/lopezpaz_oquab_2017_c2st.pdf`.

Not held, open asks in [`lit_needed.md`](../lit_needed.md): Perkel, Gerstein & Moore 1967 (II) ·
Grün et al. 1999 · Stella et al. 2019 3d-SPADE and the INM-6 harnesses · Cunningham & Yu 2014.
