# Where the six detectors came from, and what a different field already knows

*Written 2026-08-22 from two interface2 reports, the bugarach tree, and the
darkroom literature shelf.*

> **Revised 2026-08-29: the author said where each one came from, and interface2
> is frozen on the topic.** Every lineage row in this document was assembled from
> interface2's reports and this tree. Tony supplied the missing half — who wrote
> what — and it separates the six three ways, which nothing here had recorded:
>
> - **`rate_detect`, `coact_detect`, `loco_detect` are his**, designed for this
>   preparation. *"They blindly reconstructed elements of CFAR, I was totally
>   unaware when I designed them."* §4's map is therefore a convergence, not a
>   derivation — the stronger reading, and the one §2 could only hedge toward.
>   ⚠ It rests on the author's recollection; there is no contemporaneous record
>   either way, and four literatures that could host prior art for it have never
>   been searched (§7).
> - **SPIKE-synch is his detector on someone else's measure.** The measure is
>   Kreuz's; the detector on it was written here. ⚠ *Tony described it as "peak
>   detection on the synchrony plot", and the shipped code is a **dual-threshold
>   hysteresis** scan — `detection_mode` defaults to `"threshold"`, and every
>   bake-off number came from that branch. A `"peak"` mode exists and has never
>   shipped. Design intent and shipped behaviour, not a contradiction to resolve by
>   picking one.* Not novel either: Kreuz's own lab has published the same two-knob
>   detector on this profile (personal communication, April 2026; Kreuz et al. 2022, J Neurosci Methods 381:109703).
> - **locust and binned SCE both pass through CICADA, by different routes — and one
>   of them lands on something older.** locust is the port, *"modified at port to
>   MATLAB to use our pipeline event detection data rather than feed it raw calcium —
>   our calcium events differ from the CICADA team's."* binned SCE is **not** a port:
>   *"based on ideas in CICADA before we did the port"* — 18 days before it, by
>   interface2's own git — and its published root (Cossart 2003, from **Yuste's** lab)
>   predates CICADA.
>
> **And interface2 development is frozen on this topic**, so the audit that several
> sections here defer to will not move again: what it says is final as it stands.
> §6.3 and the README's citations block were rebuilt on that basis the same day.

> **Revised 2026-08-22: the radar primaries have been retrieved, and they were
> worth retrieving.** This document first shipped with every attribution in §4
> flagged unverified. Two of the four are now **read in full** and shelved at
> `<darkroom>/bugarach/lit/radar/`; the other two are confirmed from Rohling's
> printed reference list but **not read**, and §7.2 says what they would settle
> and how to get them.
>
> The retrieval strengthened the argument rather than qualifying it. **Finn &
> Johnson's 1968 abstract already names the failure this project spent two weeks
> debugging** — *"the introduction of a second target in one of the threshold
> control cells introduces a masking effect"* — and the multiplicative threshold
> that §5.2 says rate+context is missing is stated outright in both primaries. It
> also corrected one claim of mine, in §5.1: guard cells are documented as routine
> by 1983, not by 1968.

> **Revised 2026-08-24: §2 has been overtaken, and §5 was right all along.** An
> interface2 audit closed every lineage row in §2, including the three filed below
> under *"Tier 3 — our constructions on common ideas"*. The SCE rule's root is
> **Cossart, Aronov & Yuste 2003, *Nature* 423:283–288**, whose Methods state the
> whole algorithm — not Malvache 2016, not the Cossart lab, and crediting Mao 2001,
> which nobody has reached. `rate_detect` is cell-averaging CFAR, **which §5.2 of
> this document already names** while §2 still files the detector as ours; where the
> two halves disagree, §5 wins. `loco_detect`'s `maxlt` is GO-CFAR (Hansen 1973) and
> its percentile-of-pool is kin to OS-CFAR — so §4's argument that three of these
> are re-derivations of CFAR has stopped being a reading of the design space and
> become the attribution. Separately, Kreuz's own lab has published detection layers
> on the synchronization profile, which weakens the Tier 2 framing.
>
> **None of this is a problem, and Tony has ruled on that** — *"most researchers
> would be kind of thrilled with the link … it's a tool and it's useful."* Priority
> is closed: acknowledge the origins, say we arrived independently, and take the
> engineering the radar literature is offering. **This document's own thesis is what
> survives** — §5 lists five things radar knows that this project does not, and
> being right about the lineage is the reason to trust that list.
>
> The corrections, what they change in the app, and what is still second-hand:
> [the methods are not ours](todo/2026-08-24-the-methods-are-not-ours-and-the-app-says-otherwise.md)
> and [what Kreuz answered in April](todo/2026-08-24-kreuz-answered-the-spike-synch-questions-in-april.md).

---

## The finding, first

Six detectors were built here over two years, by two teams, in two languages.
Three of them place a threshold by measuring the background **around** the moment
they are testing. **None of the three excludes that moment from its own
measurement**, so a coordinated event contributes to the estimate of the
background it is judged against, and raises the bar it has to clear.

The radar community named this decades ago, fixed it with **guard cells**, and has
not shipped a detector without them since. This project derived the same failure
from scratch, in a two-week debugging session, and wrote it into the README as its
most expensive mistake:

> Detector settings tuned on a dense benchmark — a coordinated event every 14 s —
> collapsed when the same settings met sparse data, because **four planted events
> sat inside every 60 s context window and contaminated the null the detectors
> depend on.** Binned SCE's precision fell from 74% to 10%, and finding out cost
> two weeks.

![Panel A, the six hand-written detectors plotted as F1 against firings inside a block containing no planted events, on a log axis, coloured by where each one's threshold comes from: the two rate-local detectors sit at 1 and 2 firings, the two stationary-threshold ones at 59 and 215. Panel B, three horizontal lanes showing each rolling detector's reference window centred on a red bar marking the moment under test, with the bar inside every window](learned/cfar_map.png)

**Panel A is the evidence for everything that follows.** The block contains no
planted events, so every firing inside it is a false alarm by construction. The
six separate by **where the threshold comes from**, not by what statistic they
compute: one bar per region gives 59 and 215 firings; a bar that follows local
density gives 1 and 2. That is a hundredfold separation along the axis CFAR is
organised around, measured on this project's own recordings, and it is the reason to
take the rest of this seriously. (The two learned models are omitted — the panel
is about where a *hand-placed* threshold comes from.)

**Panel B is the defect.** Each lane draws one detector's reference window at its
shipped default, with the moment under test in red. In all three the red bar is
*inside* the window. Read off the source:

- `loco.py` builds the trailing half as `[max(a - half_ctx, rs), a]` and the
  leading half as `[a, min(a + half_ctx, re)]` — both abutting the anchor.
- `coact.py` builds the context as `c_lo = ctr[b] - C/2`, `c_hi = ctr[b] + C/2`,
  so the bin under test sits dead centre of the window that judges it, and the
  circular shift runs *within* that window, preserving the bin's own events in
  the null pool.
- `rate.py` computes rate and context as **centred** sliding-window counts, so
  the 1 s test window is inside its own 60 s reference.

A guard interval is one parameter in three files. `tools/regime_shift.py` already
turned the incident into a failing assertion, which was the right response to a
mystery; it is the wrong response to a known one.

Everything below is the history that explains how six detectors arrived here, and
what to do about each of them.

---

## 1. The two reports, and the one place they disagree

interface2 holds two documents that account for the detectors' origins. They were
written a day apart, for different readers, and neither supersedes the other.

**`docs/coordination_detectors_methods.md`** (2026-07-14) is the engineering
account: one section per detector, statistic and threshold spelled out, and — for
the two detectors that carry outside DNA — a block headed *"Provenance
(important)"* saying exactly what was taken and what was changed.

**`docs/manuscript_coordination_full.md`** (2026-07-15) is the reviewer-facing
account: the same detectors arranged into a **two-axis taxonomy** and pointed at a
claim. §2.3 gives the lineages, §2.5 gives the new detector, §4.2 pre-argues the
critiques. It makes an argument the methods document deliberately does not.

They disagree about **how many detectors there are**, and the disagreement is
substantive. The methods document treats CoactDetect and LoCo as one detector —
*"detector #5"* — noting only that *"two teams built it independently and
converged on the same mechanism."* The manuscript splits them into **variant A
(CoactDetect** — per-bin z / Gaussian-tail p ≤ α**)** and **variant B (LoCo** — a
high percentile of the pooled local null**)**, then resolves the split by
benchmark: the per-bin-α form has a multiplicity problem — thousands of bins in a
dense block, so ~1% fire by chance — that the pooled-percentile form avoids.
Measured, it was 4 false alarms against 0, at identical recall.

**The manuscript decided against CoactDetect. bugarach ships both, and
CoactDetect now leads the hand-written detectors in the bake-off.** Nothing in
either repository records that the decision was revisited. §6.5 returns to it.

---

## 2. The lineage of each of the six

Three tiers, and the tier matters more than the name.

### Tier 1 — a published method, partially ported and modified

**locust.** Derived from the Cossart lab's CICADA, `gitlab.com/cossartlab/cicada`,
MIT, upstream copyright carried in the module. This entry used to call it *"the only
one of the six whose idea has a settled external owner"* — the 2026-08-24 audit found
published prior art for all six, so that sentence is withdrawn; §6.3 has what
replaced it, and the tier membership below is superseded by the three-way split in
this document's 2026-08-29 header. It is also **not a drop-in**, and both reports say
so: we feed our own
upstream-detected events instead of running CICADA's transient detection, and we
feed it a per-event duration instead of letting it measure one. The original
paints each cell active for the transient *duration* it detected itself, which
over-detects catastrophically on SLOW transients here (median ~4.6 s of
duration-overlap swamps onset-synchrony), so the brief rise interval (~2 s) is
sent instead — **by the exporter, on export; not by this code, which paints what
it is given and since 2026-08-29 refuses to compute a duration at all** (ADR-0002
addendum, FOUNDATIONS §7, sapper SAP012). A regional-scope option was added; the
original thresholds over the whole recording.

### Tier 2 — a published *measure*, with our detector on top

**SPIKE-synch.** The SPIKE-synchronization profile is Kreuz and colleagues'
(cSPIKE/SPIKY, BSD). It is a self-normalising, parameter-free **characterization**
of moment-to-moment coincidence and was never intended to emit discrete events.
The methods report is unambiguous: *"The detection layer here is ours."* Threshold
`C(t)`, extend at a lower level, require a minimum number of trains, merge. The
τ-cap that keeps it from inflating at high density is also ours — and necessarily
so, since bugarach computes its own τ rather than PySpike's: `max_tau` is **inert
upstream**, a library defect this project verified, filed, and pinned with a
regression test (`test_pyspike_max_tau_is_still_inert`).

Worth knowing before anyone writes this up: dual-threshold hysteresis detection is
ordinary signal-processing practice. This is ours as an *implementation* without
being a novel method — no claim to defend, and none to make.

### Tier 3 — our constructions on common ideas

**binned SCE.** Distinct-ROI coactivity per bin against a circular-shift surrogate
percentile. The rule was carried here as *"onsets within 250 ms exceeding 3 SD over
1000 shuffles, minimum 5 cells"*, attributed to Malvache, Cossart et al. — and it
had reached this project **through a secondary description**, which the literature
shelf flagged with an instruction: *"Get the primary before quoting it."*

**The primary was retrieved on 2026-08-22, and two of those four constants do not
survive it.** Malvache et al. 2016, *Science* **353**(6305):1280–1283, now on the
shelf as `malvache_2016_awake_reactivations.pdf`:

- **The window is 200 ms, not 250.** Fig. 1A: *"summed activity of cells (over a
  200-ms window)"*.
- **"Five cells" is an example, not a constant.** Same caption: *"significance
  threshold for synchronous activity detection (**five cells in this example**)"* —
  the threshold is derived per recording, and five was its value in that one figure.
  Carrying it as a fixed floor is a misread caption.
- **The 3 SD and the 1000 shuffles are still unverified.** The Report gives
  detection as *"(P < 0.01, supplementary methods)"*, and the supplement is a
  separate download. Plausible, unread, not to be quoted yet.

**On priority, the retrieval cuts against the premise rather than settling it.** The
Report does not present SCE detection as a contribution — it is a methods step,
deferred to the supplement in a single parenthesis. A paper introducing a canonical
rule does not usually bury it, which weakens the idea that this is where the rule
*originates* rather than where this project happened to meet it. That the same
construction turns up inside Mölter's assembly benchmark as a *precondition* rather
than a result points the same way.

So the position is unchanged in shape and much better grounded: **cite this paper
for the SCE phenomenon, which is what it establishes and what it is known for; do
not attribute the constants to it.** interface2 can say what interface2 did.

> **The root was found on 2026-08-24, and this paragraph's suspicion was
> justified.** *"A paper introducing a canonical rule does not usually bury it"* —
> and Malvache 2016 was not introducing it. **Cossart, Aronov & Yuste 2003** was,
> in its Methods, in full: coactive cells per frame, a rate-preserving per-cell
> surrogate, 1,000 iterations, pooled histogram, percentile cut. The rule is a
> **Yuste-lab** method that travelled to Marseille with its first author and
> eventually became CICADA, and the 1,000 shuffles this document lists as unverified
> are in the 2003 Methods — matched here by coincidence, since the default was
> carried from MATLAB that cited nothing. One divergence to know: 2003 resamples by
> **interval reshuffling**, where CICADA, Bocchio 2020, Dard 2022 and `sce_detect`
> all circular-shift.
> [The full correction](todo/2026-08-24-the-methods-are-not-ours-and-the-app-says-otherwise.md).

**rate+context (RateDetect).** Pooled population rate in a 1 s window minus a 60 s
rolling context; fire where the excess clears a fixed level. Authorship is not
contested. Priority has never been examined, and *"threshold the pooled population
rate against a rolling local context"* is a common construction. The cheapest
check in this document is already on the shelf and half-read:
`cotterill_2016_burst_detector_comparison.pdf` is a comparison of burst detectors,
which is precisely where a rate-threshold method would appear.

**CoactDetect and LoCo.** The distinct-ROI statistic against a rate-local, rolling
null. Authorship is not in doubt. Circular-shift surrogates over distinct-ROI
coactivity are standard — this project's own detector-free assessor uses them.
What would be distinctive is the **rate-local rolling null**. Nothing in either
tree examines whether that construction is published.

**§4 is the answer to that question, and it is not the answer the manuscript
assumes.**

---

## 3. The wider history: four traditions, and we have cited three

**Cell assemblies (neuroscience, 1949–).** Hebb's assembly, made measurable when
population recording arrived. The synchronous-calcium-event rule is this
tradition's calcium-imaging expression; CICADA and the assembly benchmarks
(Mölter, Russo, Romano's PROMAX toolbox — all on the shelf) are its current tools.
**Cited here.**

**Spike-train synchrony measures (1990s–).** A parallel effort to measure
coincidence *continuously* rather than declare events: SPIKE-distance,
SPIKE-synchronization, the Kreuz-lab family. Deliberately not detectors, which is
why bugarach had to build a detection layer on top of one. **Cited here.**

**Learned event detectors (2018–).** Networks whose output is the event itself —
DOSED on sleep EEG, cnn-ripple on hippocampal LFP, SEED on spindles. The shelf
makes the correction bluntly: this is *an established genre with a standard
architecture family*, single-shot object detectors transplanted from vision to 1D,
and **any claim that the idea is new is wrong.** DOSED's δ-swept IoU scoring is
also, in the shelf's words, *"bugarach's open question, answered."* **Cited here,
and the shelf was built specifically to stop a novelty claim that four web
searches had failed to check.**

**Adaptive-threshold detection in radar.** A target return must be declared
against a background whose power is unknown, non-stationary, and rises sharply at
**clutter edges** — coastlines, weather fronts, the boundary of a rain cell. A
fixed threshold fails there for the reason a fixed coactivity threshold fails: the
false-alarm rate tracks the background instead of staying put. The field's answer
is **CFAR — constant false alarm rate** — detectors that estimate the background
from neighbouring **reference cells** and set the threshold from that estimate, so
the probability of false alarm stays put as the background moves. The cell being
tested is the **cell under test**; the reference cells are the ones around it; the
excluded ones in between are the **guard cells**.

**This tradition is not cited anywhere in either repository.** `radar`, `CFAR`,
`clutter` and `guard cell` return nothing across interface2 and bugarach. It is
the tradition whose design space these six detectors have been re-deriving.

---

## 4. The 2×2 is a corner of the CFAR design space

The manuscript's contribution rests on a taxonomy: *statistic* (pooled rate vs
distinct-ROI coactivity) × *null locality* (stationary vs rate-local rolling). The
fourth cell — distinct-ROI × rate-local — *"was empty and motivated detector #5."*

The **statistic** axis is this project's own and has no CFAR analogue worth
claiming. The **locality** axis is CFAR's founding axis, and its variants are
named for exactly the choices bugarach made by benchmark.

| bugarach | mechanism | CFAR analogue | attribution | held? |
| --- | --- | --- | --- | --- |
| rate+context | test window vs the mean of a surrounding window | cell-averaging (CA-CFAR) | Finn & Johnson, *RCA Review* **29**(3), Sept 1968, 414–464 | **read in full** |
| CoactDetect | bin vs a null built from a window **centred on that bin** | cell-averaging, per-cell test | — | — |
| LoCo, `maxlt` | **max** of a trailing and a leading half-window | greatest-of (CAGO-CFAR) | Hansen & Sawyers, *IEEE T-AES* **AES-16**(1), Jan 1980, 115–118 | **read in full** |
| LoCo, `symmetric` | one window spanning both sides | cell-averaging again | — | — |
| LoCo's 99.9th percentile of the pooled null | a high order statistic, not a mean | kin to ordered-statistic (OS-CFAR) | Rohling, *IEEE T-AES* **AES-19**(4), July 1983, 608–621 | **read in full** |
| censoring the largest reference cells | discard the interferers before estimating | trimmed-mean / censored CFAR | Weiss 1982 and Rickard & Dillard, *per Rohling*; Gandhi & Kassam, *IEEE T-AES* **24**(4), 1988, 427–445 | **read in full** |
| `min_rois` floor on top of the significance test | a second, absolute threshold | second-threshold / binary integration | — | — |
| binned SCE, locust | one bar per region | pre-CFAR fixed threshold | — | — |

**All four primaries are now held and read**, on the shelf at
`<darkroom>/bugarach/lit/radar/` with a read-status entry each — Tony supplied the
two IEEE papers on 2026-08-22, closing the last of §7.2. Every radar quotation in
this document is matched mechanically against a PDF on that shelf.

One correction the retrieval forced: an earlier draft said the censoring fix was
Gandhi & Kassam's. Rohling, writing in 1983, already credits Weiss and Rickard &
Dillard with *"eliminating the maximum amplitude(s) from the reference window"*,
so Gandhi & Kassam is the standard **analysis**, not the origin.

**`maxlt` is greatest-of selection.** Precisely: LoCo matches greatest-of CFAR in
its **combination rule** — take the larger of the two half-window estimates —
while its **estimator** is a percentile of a circular-shift surrogate pool rather
than a mean of reference cells. The rule is the same; the thing being combined is
not. And the reasoning recorded for it in the methods report is the reasoning
greatest-of selection exists for: taking the greater half means a background
transition straddling the test point cannot *lower* the bar, so a clutter edge — a
drug-onset ramp — stops manufacturing false alarms. interface2 validated it the
same way, on a synthetic ramp: symmetric context gave 3 boundary false alarms,
`maxlt` gave 0.

This is a **convergent rediscovery, and a good one.** It is not a warning about
the work; it is a warning about one sentence in the manuscript. The empty cell was
empty *in the calcium-imaging literature*. In detection theory it has been
occupied for a long time, and a methods reviewer from a signal-processing
background will know that.

---

## 5. Five things radar knows that this project does not

### 5.1 Guard cells — the finding at the top of this document

CFAR detectors exclude the cells immediately around the one under test — the
**guard cells**. The reason is one sentence: if the target's own energy leaks into
the estimate of the background it is tested against, the target raises its own
threshold and masks itself. Weinberg's survey states the purpose plainly — the
reference cells *"are separated from the CUT by a number of guard cells, whose
purpose is to limit the effects of a range spread target"* — and by 1983 the
practice is so settled that Rohling's Fig. 3(b) specifies a reference window
*"with two guard cells directly adjacent to the test cell"* as a setup detail, with
no argument for it.

*(Correction, from retrieving the primary: an earlier version of this document said
guard cells were standard "since the first CA-CFAR papers". Finn & Johnson 1968
excludes the cell under test from its own estimate — the delay-line **centre tap**
is the test cell and the surrounding taps form the estimate — but no guard band
around it appears in the text. **Standard by 1983** is the claim the sources
support.)*

bugarach's three rolling detectors have no exclusion at all (panel B) — not even
the 1968 baseline, since CoactDetect's context is centred on the bin under test and
the shift runs inside it, so the test bin's own events sit in the null pool that
judges them. Both named consequences are live here: **self-masking** (an event
raises the bar it must clear) and **mutual masking** (a *second* event inside the
reference window raises it further, which is worse in dense data than sparse).

**Mutual masking is in the founding paper's abstract, quantified.** Finn & Johnson,
1968: *"The introduction of a second target in one of the threshold control cells
introduces a masking effect equivalent to a 1-dB loss in detection efficiency for a
worst-case analysis where 100 resolution cells are employed in the threshold-control
system."* The regime-shift incident — four planted events inside every 60 s context
window, binned SCE's precision from 74% to 10% — is that effect, at a magnitude the
radar case never had to consider, derived here the hard way fifty-eight years later.

**It is not free, and the cost runs the other way in sparse data.** A guard
interval removes reference cells, so the background estimate is built from less
data and its variance rises — radar calls the resulting sensitivity penalty *CFAR
loss*. On a sparse recording the reference window is already thin. There is a
second subtlety specific to this implementation: the null is a circular shift
*within* the window, so excising a middle chunk changes the wrap length and each
ROI's rate inside the reference. The shift has to be defined on the retained
reference span, not on a window with a hole in it.

**Cost to try: one parameter, `guard_sec`, in three detectors, defaulting to 0 so
parity with the MATLAB originals is preserved.** The bench already scores it.

### 5.2 rate+context is a cell-averaging detector whose CFAR property was removed

Cell-averaging CFAR sets the threshold **multiplicatively**: `θ = α · μ̂`, where
`μ̂` is the reference-window estimate and `α` comes from the design false-alarm
probability and the window size. The multiplication is the whole point — it is what
holds the false-alarm rate constant as the background moves.

This is the one claim here that rests on the primaries rather than on structure,
and both state it outright. Finn & Johnson make the threshold *"proportional to the
square root of this estimate of the output variance: D₀ = K√(E{|MF|²})"*. Rohling's
general CFAR processor is two steps: *"the first step is to measure the mean clutter
power level Z. The second step is to **multiply** this estimation Z by a scaling
factor T."*

RateDetect fires where `rate − context ≥ excess_threshold_hz` (default 5 Hz). The
threshold is **additive**. The effective ratio `θ/μ̂ = 1 + 5/μ̂` is enormous when
the tissue is quiet and approaches 1 when it is busy: over-conservative in sparse
recordings, over-permissive in dense ones. It has a rolling reference window and
no constant-false-alarm property.

**The bake-off measures exactly that.** rate+context fires **34.8** times in a
block containing nothing — third most promiscuous of the six, an order of
magnitude above the two rate-local detectors — while its recall (0.700) is close
to the leaders'. That is the signature of a bar that is too low where the tissue
is busy, which is what an additive offset does.

It is also **the fastest thing in the repository at 0.005 s per fold**, roughly
three times quicker than the learned model. A detector that cheap, 0.08 of F1
below the leaders, with a one-line-fixable defect in its threshold rule, is the
best return on effort in the suite.

### 5.3 Nobody here has stated a design false-alarm probability

CFAR's organising idea is that you **choose the false-alarm probability first**
and derive the threshold multiplier from it analytically, given the reference
size. The operating point becomes a stated design decision, and the gap between
design and measured false-alarm rate becomes a diagnostic.

bugarach picks operating points by sweeping a benchmark, and the bench refuses an
optimum sitting on its grid edge — more discipline than most papers show. But
these are **tuned constants, not derived ones**, and they promise nothing about a
recording unlike the benchmark.

**This does not license grid-shopping, and the repo is right to forbid it.**
`bench`'s own docstring and the SPIKE-synch note are explicit that operating
points come from baseline recordings and measured coordination properties, *"not
from whatever makes a curve look like a curve."* A design false-alarm probability
is the opposite of that: it fixes the target **before** the sweep and makes the
sweep answerable to something outside itself.

It would also give the promiscuity probe its missing teeth. The probe's firings
are already **reported** — the `probe firings` column, and panel A — but they
[cannot fail](todo/2026-08-16-promiscuity-probe-cannot-fail.md): they leave both
the numerator and the denominator of F1, so locust's 215 firings in an empty block
cost it nothing. Measured false-alarm rate against a stated design target is a
score the probe could actually fail.

### 5.4 Greatest-of selection is edge-robust and target-blind, and LoCo inherits both halves

`maxlt` buys clutter-edge robustness, and Rohling says so in as many words: the
greatest-of variant *"makes allowance for clutter edges occurring within the
reference area"*, and its transient behaviour at an edge is *"superior to that of
the CA CFAR"*, at a small sensitivity loss in stationary clutter.

**And he says what it does not buy.** For two targets close together, *"due to
symmetry, the splitting of the reference window of the CAGO CFAR does not help in
this situation"* — the split is the whole mechanism, and against an interferer in
the reference window it contributes nothing.

Gandhi & Kassam's systematic comparison of five schemes puts both halves in one
sentence: *"Although the false alarm rate performance of the GO-CFAR processor in
regions of clutter transition is **better than that of any other mean-level CFAR
scheme**, the detection performance in the **multiple target environment is quite
poor**."*

**The price of the split is now a number, and it is small.** Hansen & Sawyers
measured exactly this: *"This additional loss is seen to be quite small; typically
it falls in the range of **0.1 to 0.3 dB**."* ⚠ That magnitude does **not** transfer
— it is a signal-to-noise loss under a radar target model, and our statistic is a
count of distinct ROIs, not a power ratio. What transfers is the shape: greatest-of
is cheap.

Translated: LoCo should be expected to **miss the second of two coordinated events
falling within one half-context** — 60 s FAST, 30 s SLOW at the shipped defaults —
and to miss it *because* of the mechanism that makes it good at drug onsets.
Nothing in either tree tests this. The bench can: plant event pairs at a swept
separation and measure recall of the second.

**Which does not mean replace it — and this is where retrieving the primaries
changed the recommendation.** An earlier draft of this document said
ordered-statistic selection "was designed to get both properties at once", citing
Rohling's abstract. Gandhi & Kassam do not sustain that: *"although the OS-CFAR
processor may resolve multiple targets quite well, it lacks effectiveness in
preventing excessive false alarms during clutter"* transitions — while their
conclusion still finds ordered-cell schemes have *"in general better overall
performance than the mean-level CFAR schemes."* Both are true, and they are
different claims: **ordered statistics win on balance; greatest-of wins
specifically at edges.**

**bugarach's dominant nonhomogeneity is the drug-onset rate transition — an edge.**
On this paper's own scoring, that is precisely where greatest-of beats every other
mean-level scheme. So `maxlt` is **well chosen for this preparation**, and swapping
it for an order statistic would trade away the property that matters most here. The
upgrade path for the multiple-target blind spot is **censoring / trimming** —
discard the largest reference cells before estimating, which is what trimmed-mean
CFAR does — not replacement.

### 5.5 The surrogate pool may be an expensive way to compute an order statistic

LoCo is the slowest classical detector in the bake-off: 0.245 s per fold, 4×
CoactDetect and 17× the 1,149-parameter learned model. The cost is structural — at
each anchor, for each half, it circular-shifts every ROI's events and pools the
resulting coactivity, then takes the 99.9th percentile of that pool.

Ordered-statistic CFAR takes its threshold as the *k*-th order statistic of the
**reference cells themselves** — one sort, no shuffling. The two are not
equivalent: the surrogate pool answers *"what coactivity would these rates give
with cross-ROI timing destroyed"*, a raw order statistic answers *"what coactivity
is normal around here."* The first is a stronger null and the difference is real.
The second is essentially free, and **whether the stronger null buys accuracy
proportional to its 17× cost is a measurement nobody has made.**

**Try it as a cheaper estimator inside the greatest-of rule, not as a replacement
for it.** §5.4's correction applies here: an order statistic is the better
*estimator* on balance, but it is weaker than greatest-of at exactly the clutter
edge this preparation is full of. The two are separable — `maxlt` is a combination
rule and the percentile-of-surrogates is an estimator — so the cheap experiment is
to keep the max-of-two-halves and swap only what each half computes. That also
makes the trimming fix of §5.4 natural: an order statistic is one sort away from a
trimmed mean.

---

## 6. Keep or modify, detector by detector

### The confound that has to be read first

interface2's MATLAB benchmark reports F1 per stream from a generic ramp benchmark,
marked **provisional** upstream, with its own warning that *"anything below ~0.6
is a weak optimum on a flat/noisy surface"* and that RateDetect's and SCE's optima
sit on the swept **grid edge**. bugarach's bake-off reports F1 over four held-out
folds of a simulated data set fitted to 85 real baseline recordings. They answer
different questions and are not averaged here.

**But the bake-off carries a confound of its own, visible in `bench.py`'s own
`source` fields.** Each detector sweeps exactly one declared knob per fold; every
*other* parameter is fixed, and where those fixed values came from differs:

| detector | fixed parameters come from | bake-off F1 |
| --- | --- | --- |
| CoactDetect | calibrated viewer point | 0.651 |
| LoCo | measured-regime F1 optimum | 0.638 |
| locust | calibrated pair, retuned 2026-08-20 | 0.541 |
| rate+context | **`rate_detect` defaults** | 0.571 |
| binned SCE | **`sce_detect` defaults** | 0.420 |
| SPIKE-synch | **viewer FAST defaults** | 0.254 |

The three calibrated detectors place 1st, 2nd and 4th; the three uncalibrated ones
place 3rd, 5th and 6th. **The bake-off's ranking tracks calibration status almost
exactly, and reading it as a ranking of detectors reads that confound as a
result.** Two of the three are worse than merely uncalibrated: SCE's own bench note
says its F1 peaked at the old grid floor of 90 and was still climbing while it
ships at 99.0, and SPIKE-synch's swept knob is demonstrably not the binding one
(§6.6).

With that stated, the verdicts.

### 6.1 rate+context — keep, and fix the threshold rule first

The cheapest thing in the repository, with a defect one flag wide (§5.2) and a
measured symptom (34.8 probe firings). Make the threshold multiplicative, add a
guard interval, sweep the multiplier, re-run. If it moves even halfway to the
leaders it becomes the default detector for large corpora on cost alone. If it
does not, that is a real result about pooled-rate statistics rather than an
artifact of a threshold rule nobody examined.

**Do not retire it for its low F1 before doing this.** Its score is partly a
measurement of a fixable bug and partly a measurement of untuned defaults.

### 6.2 binned SCE — keep, and stop scoring it as a competitor

SCE is second-to-last (0.420) and fires 59.2 times in an empty block. The
promiscuity is expected — a stationary bar is what §4 predicts fails at rate
transitions. **The low recall (0.483) is not**; that is the signature of a bar set
too high, and its own bench note says the measured optimum lies at or below the
grid floor while it ships at the 99th percentile.

**Its value is not accuracy. It is comparability.** SCE is the rule the
calcium-imaging field actually uses, so it is the row that lets an outside lab
place its numbers next to these. Tuning it to compete destroys the only thing it
is for.

Two consequences. Report it as a **reference row**, visually distinct from the
competitors, at the canonical settings rather than a tuned point. And **settle its
provenance before publishing a sentence containing the words "our SCE"** — the
canonical rule reached this project second-hand, the primary was never retrieved,
and the same construction appears inside Mölter's benchmark. Tony's own framing —
*derived from ideas in CICADA, but essentially ours* — is the honest landing
place, and it is a lineage claim, not an independence claim.

### 6.3 locust — the citability this section was built on does not exist

> **Rewritten 2026-08-29.** This section used to open *"the only detector whose
> method has a settled external owner, and the port's parity to 1e-9 is what makes
> it citable in the original's place"*, and recommended shipping a faithful mode to
> spend that asset carefully. The 2026-08-28 attribution audit
> ([review](reviews/locust_attribution_2026-08-28.md)) established that the asset
> was never there. The recommendation below is the opposite of what stood here, and
> the old text is kept in this note rather than deleted so the reversal is legible.

**The 1e-9 measures this repo against interface2, not against CICADA.**
`tools/matlab_ref/gen_ref_cicada.m` builds the parity fixture by running
interface2's own `generate_sce_cicada`, so the number says bugarach computes what
interface2 computed. **No output of either has ever been compared against CICADA's**
— that comparison does not exist anywhere, and it is what "validated against the
original" would have to mean.

What *does* exist, and this document said otherwise until 2026-08-29: interface2
checked its transliteration against upstream `master` by **reading code**, function
for function, on 2026-08-21 — `local_sce_threshold`↔`get_sce_threshold`,
`local_slide_coact`↔`sum_activity`, `local_findpeaks`↔`find_peaks`, down to
confirming the single-frame-null quirk is upstream's real behaviour
(`coordination_method_provenance.md` §5, on their unmerged `coord-attribution`
branch). That is a correspondence check on the **unmodified** transliteration. It is
not a measurement, and it does not cover either documented deviation.

```text
Cossart CICADA ── read-for-correspondence, never run against ──▶ interface2 generate_sce_cicada
                                                                            │
                                                             1e-9, on every returned number
                                                                            ▼
                                                                         locust
```

It is also **already modified** — it is handed a per-event duration where the
original measures the transient itself, for a stated and good reason, and the
duration it is handed is **the exporter's** (FOUNDATIONS §7; the port paints what it
is given). But a reader who sees "CICADA" in a figure legend assumes the published
method.

**And interface2 had parked that function before this port existed.**
`generate_sce_cicada` was shelved on 2026-07-07 for over-detecting on this
preparation's long SLOW transients — median ~4.6 s of duration-overlap swamping
onset-synchrony — and bugarach's port landed a month later, on 2026-08-10. So the
upstream end of the chain is a function its own authors had already stopped using,
for a reason that bears directly on what locust measures.

**There is no faithful mode to ship.** The port skips a whole stage by design —
`generate_sce_cicada.m`: *"we already have events, so their per-cell
transient-detection step is skipped."* A mode that restores the active-duration
model would still be missing that stage, so calling it "faithful" would put the
old claim back under a new name.

**So: take the producer's exported duration as the duration — it is not this
project's to choose (FOUNDATIONS §7, ADR-0002 addendum) — and never report locust's
numbers as CICADA's.** Its 214.8 probe firings — 86× LoCo's 2.5 and 172×
CoactDetect's 1.25 — are a property of **our variant on this benchmark** and are not
available as a finding about the published method. That is the weaker thing to have measured, and it is the true one. What
would actually license the stronger claim is running CICADA itself on these
recordings, which is
[its own open item](todo/2026-08-17-run-a-literature-method-on-our-recordings.md)
and has not been done.

### 6.4 LoCo — keep as the flagship, and change three things

LoCo is the detector the manuscript is built around and it deserves the position:
top MATLAB performer on FAST, second among the hand-written detectors in the
bake-off, and 2.5 probe firings against locust's 215.

1. **Add a guard interval** (§5.1). Highest-value change here.
2. **Test the greatest-of blind spot** (§5.4): plant event pairs at swept
   separations inside one half-context and measure recall of the second. If LoCo
   misses them, that is a documented limitation rather than a surprise in
   somebody's data.
3. **Measure whether the surrogate pool earns its 17× cost** (§5.5).

On the FAST/SLOW asymmetry — LoCo's MATLAB SLOW F1 is 0.466 against CoactDetect's
0.757 — **do not treat that as an unexplained gap.** The same handoff says
anything below ~0.6 there is a weak optimum on a flat surface, so 0.466 is
plausibly a statement about the optimisation surface rather than about LoCo. Worth
re-running on the approved folder before anyone quotes it either way.

### 6.5 CoactDetect — keep, and resolve the contradiction it is carrying

CoactDetect leads the hand-written detectors (0.651; the top three including the
learned model are a statistical tie) and fires **1.2** times in an empty block —
the cleanest of the six. It is also the variant **the manuscript decided
against**, for a stated and measured reason: a per-bin α has a multiplicity
problem that the pooled-percentile form avoids (4 false alarms against 0, at
identical recall).

Two documents say opposite things, and shipping both detectors is not a decision —
it is the absence of one. The resolution is measurable, not editorial: run the
promiscuity probe with §5.3's stated target and a false-alarm rate that enters the
score. Either the multiplicity problem appears in bugarach's recordings, and the
manuscript was right; or it does not, and §2.5 needs revising before submission.

Note that bugarach's own probe **already points the other way** — 1.2 firings for
the per-bin-α form against 2.5 for the pooled-percentile one, the reverse of the
MATLAB result, though on different recordings and at a different operating point.
That is one more reason not to submit with this open.

### 6.6 SPIKE-synch — the number measures the operating point, not the detector

SPIKE-synch scores 0.816 | 0.735 in the MATLAB benchmark and **0.254** here. That
looks like the largest unexplained discrepancy in the project. **It is not
unexplained — the tree located it four days before this was written**
(`docs/todo/2026-08-18-spike-synch-knob-may-not-be-the-knob.md`), and the cause is
in `bench.py` in plain sight:

- The swept knob is `C_threshold`, over `(0.005 … 0.12)`, while `C_min` is
  **pinned at 0.1**. Most of the grid sits below the parameter that actually gates
  an event, so the sweep *measures `C_min` while reporting `C_threshold`*.
- The synchrony profile is quantised at `k/(n−1)`, so on a 30-ROI field every
  threshold below 1/29 is the same threshold.
- The todo records the consequence directly: on a default simulation **every value
  on the grid returns the identical result** — four detections, eleven misses.

The bake-off's numbers confirm it from the other side. SPIKE-synch's precision is
**0.538** — mid-pack, better than locust or SCE — while its recall is **0.167**.
It is not firing wrongly; it is barely firing at all. That is a detector held shut
by a pinned parameter, not a broken port.

**So the verdict is narrower and more actionable than "demote an unexplained
result":**

- **The 0.254 must not be quoted as SPIKE-synch's accuracy.** It is the score of a
  detector whose sensitivity axis was degenerate. Mark it as such wherever the
  bake-off table appears — a correction to a published table, not a research task.
- **Re-run with `(C_threshold, C_min)` swept together**, on a grid scaled to the
  ROI count rather than fixed in absolute `C`, since the quantum depends on *n*.
  The todo's own warning applies: do not widen the grid until something moves —
  derive it from the quantum.
- **Keep the measure regardless.** `C(t)` is a useful per-event characterization
  channel and is what Kreuz built it for. RateDetect already carries mean
  synchrony as characterization that never enters detection; that is the right
  role.
- **The τ-cap is not the suspect.** bugarach computes its own τ, and PySpike's
  inert `max_tau` is already pinned by a regression test.

### 6.7 The meta-verdict: keep all six, and relabel what they are

Six is the right number. But presenting them as six competitors invites *which one
wins*, and the honest answer — the top three are a tie across four folds of thirty
planted events, and the ranking below them tracks calibration status — reads as an
evasion.

The suite is better described as **one modified port of a published method, one
canonical reference rule, one published measure with our detector on it, and three
points in a design space detection theory already has names for**:

- **Reference rows** — binned SCE (the field's rule), locust (a partial, modified
  port of CICADA — §6.3: it stands *near* the published method, not *for* it).
  Not tuned, not competing, present so outside numbers can be placed.
- **Characterization** — SPIKE-synch's profile. Not a detector row until §6.6 is
  done.
- **The adaptive-threshold family** — rate+context (cell-averaging, pooled
  statistic), CoactDetect (cell-averaging, distinct-ROI, per-cell test), LoCo
  (greatest-of, distinct-ROI, order statistic).

That framing is stronger than "we invented the sixth", not weaker. It says the
suite is a **factorial over a known design space, ported to a substrate where
nobody had run it, and scored against planted ground truth** — a contribution that
survives a reviewer who knows CFAR. "The fourth cell was empty" does not.

---

## 7. What to do before any of this is quoted

Ordered cheapest first. Items 1 and 3 are outstanding from the 2026-08-21
provenance note; 2, 4 and 5 follow from §4.

1. **Read the body of `cotterill_2016_burst_detector_comparison.pdf`.** On the
   shelf, abstract and methods opening already read. Settles or complicates
   rate+context's priority. An hour, no fetching.
2. ~~**Verify §4's CFAR attributions against primary sources.**~~ **Done
   2026-08-22**, and the shelf is at `<darkroom>/bugarach/lit/radar/` with a
   read-status entry per work. Finn & Johnson 1968 and Rohling 1983 are **read in
   full**; both support the claims made of them, and Finn & Johnson turned out to
   quantify the masking failure in its own abstract (§5.1). One claim was corrected
   — guard cells are routine by 1983, not 1968 — and one attribution moved: the
   censoring fix is Weiss / Rickard & Dillard's, with Gandhi & Kassam the standard
   analysis. A web search had also returned the wrong initials for Finn; the
   journal's contents page settled it.

   **The last two arrived the same day**, supplied by Tony, and between them they
   changed a recommendation rather than merely confirming one:

   - **Hansen & Sawyers 1980** put the number on greatest-of — *"typically it falls
     in the range of 0.1 to 0.3 dB"* — which argues **for** `maxlt`, not against it.
   - **Gandhi & Kassam 1988** confirmed both halves of §5.4 in one sentence, and
     **corrected §5.5**: ordered statistics are not the both-at-once answer this
     document claimed. They win overall; greatest-of wins specifically at clutter
     edges, which is the nonhomogeneity this preparation actually has.

   Net effect: **stop proposing to replace `maxlt`, start proposing to censor inside
   it.** All four primaries are read; nothing on this item is outstanding.
3. ~~**Fetch Malvache et al. 2016 by hand.**~~ **Done 2026-08-22**, from Tony's own
   copy, and it was the highest-value fetch of the three: **two of the four constants
   this project attributes to it are wrong** (§2). What remains is narrower and now
   named — the **supplementary Materials and Methods**, a separate download at
   `science.org/content/353/6305/1280/suppl/DC1`, which is where the detection rule
   proper lives and where the 3 SD and 1000 shuffles would be confirmed or struck.
   Not urgent, because the correct move meanwhile is to stop quoting the constants
   at all rather than to quote better ones.
   *(Movie S1 arrived on 2026-08-22 and is shelved beside the paper. It is a
   different supplementary file — the Materials and Methods is still outstanding.)*
4. **Soften the "empty cell" sentence in the manuscript** — §2.2 and the abstract.
   **No longer pending: (2) is done and the sentence is now the exposed one.** The
   claim that the distinct-ROI × rate-local cell "was empty" is defensible only
   about the calcium-imaging literature. Rohling 1983 is a rate-local rolling null
   with a greatest-of combination rule and an order-statistic estimator, in print,
   forty-three years earlier — and it is on the shelf downstairs. A methods
   reviewer from signal processing will not need to look it up.
5. **Search for a rate-local surrogate-null coactivity detector in the calcium /
   electrophysiology literature.** Now better targeted: the query is no longer
   *"has anyone done this"* but *"has anyone brought CFAR to population event
   detection"* — and if the answer is nobody, that is the sentence the manuscript
   should be making.

**Nothing currently published depends on the provenance questions.** The
scoreboard's rules already forbid "competes with state-of-the-art", the bake-off
reports a tie rather than a win, and no method from the literature has been run on
these recordings at all — so the positioning is argued from absence, which is safe.

**Two things are no longer future, and one of them changed today.** The manuscript
is unpublished, so its "empty cell" sentence costs nothing yet — but after the
retrieval it is no longer a *risk* that a reviewer knows the prior art. Rohling
1983 is on the shelf downstairs, and the sentence is wrong as written (§7.4). And
§6.6 stands where it did: a table in the README and on the site reports 0.254 as
SPIKE-synch's accuracy, and that number measures a degenerate sweep.

---

## Sources

- `interface2:docs/coordination_detectors_methods.md` (2026-07-14) — per-detector
  mechanics and the two "Provenance (important)" blocks.
- `interface2:docs/manuscript_coordination_full.md` (2026-07-15) — the two-axis
  taxonomy, §2.3 lineages, §2.5 the A/B variant split and its resolution.
- `interface2:docs/handoffs/coordination.md` (2026-08-05) — the calibrated
  per-stream MATLAB F1 table, its PROVISIONAL marking, and the weak-optimum and
  grid-edge caveats §6 leans on.
- `<darkroom>/bugarach/lit/coordination/README.md` (2026-08-17, updated 2026-08-22)
  — the prior-art shelf and its read-status discipline. The SCE-primary gap it
  recorded is now closed: `malvache_2016_awake_reactivations.pdf`, *Science*
  353(6305):1280–1283. Every Malvache quotation in §2 is from that PDF; the
  supplementary methods are still outstanding and the entry says so.
- `<darkroom>/bugarach/lit/radar/README.md` (2026-08-22) — the CFAR shelf built to
  close §7.2, with read status per work and the two outstanding library orders.
  Every radar quotation in this document is from a PDF on that shelf.
- `docs/todo/2026-08-21-which-detector-origins-are-actually-settled.md` — the
  settled/unsettled split §2 and §7 build on.
- `docs/todo/2026-08-18-spike-synch-knob-may-not-be-the-knob.md` and
  `docs/todo/2026-08-11-file-pyspike-max-tau-issue.md` — §6.6.
- `docs/learned/bakeoff.md`, `docs/learned/bakeoff.json` — the bake-off table and
  the probe-firings column plotted in panel A.
- `src/bugarach/bench.py` — the `source` field of every operating point, which is
  where §6's calibration confound is visible.
- `src/bugarach/detectors/{rate,coact,loco}.py` — read for §5.1 and panel B; the
  absence of a guard interval is from the source, not from the reports.
- Figure: `tools/make_cfar_figures.py`.
