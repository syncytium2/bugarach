# The ROI-swap null — a surrogate made of real trains, and a test for what it leaks

> **Status: PROPOSAL. Nothing here has been run.** It is written to be attacked before it is
> executed. Every number attributed to the 2026-09-11 screen was read from that run's own files on
> 2026-09-12 and carries its source; every number attributed to the literature carries its paper.
> Where a figure is quoted from another session's reading rather than re-derived here, it says so.

**Decisions this document does not make.** It does not choose the band-statistic family size — that
is Tony's and it stays open — and it does not score the thirteen band statistics against the floor,
because doing so would make any later pre-declaration harder to defend. It does not prune any
candidate from the 2026-09-10 no-pruning ruling; where it says a candidate may become unnecessary,
that is a consequence for Tony to rule on, not a pruning.

---

## 1. The goal, and why this preparation makes it hard

The aim is a coordinated-event detector that **trains without hand labels**. The mechanism is
contrastive: build a null in which cross-ROI coordination is absent but everything else is intact,
train a discriminator to tell real recordings from null ones, and — if the null is right — the only
way for it to win is to use coordination. The detector falls out of the discriminator.

Everything rests on the null. This is not a modelling preference; it is a formal identity.
Amarasingham, Harrison, Hatsopoulos & Geman (2012) — `amarasingham_2012_jitter_method.pdf` on the
shelf — make the rule explicit: **what the resampling conditions on *is* the null hypothesis.** A
surrogate is not an implementation detail underneath a test. It is the test's statement of what
"no coordination" means. Get the surrogate wrong and the detector answers a question nobody asked.

Three properties of this preparation make the standard toolkit a poor fit.

**There are no trials.** Continuous calcium imaging of slices has no stimulus-locked repetition.
Most of the surrogate literature recombines *across trials*, because trials are the structure it
has. Here there is nothing to recombine along that axis.

**Events are rare and slow.** Baseline per-ROI rates run 0.0052–0.0190 Hz interquartile
(FOUNDATIONS §9, re-derived 2026-08-20 from the approved export folder). Most baseline windows
contain no coordinated event at all, so the legitimate training signal is thin — which matters
enormously later, because a shortcut does not have to be large to dominate a thin signal.

**Within-ROI structure is sharply bounded.** Real recordings have a hard floor on within-ROI
intervals: **0.40 s on the fast stream, 3.20 s on slow** (`reproduction/leak_table.csv`, columns
`floor_sec`, every row). Nothing in real data violates it. That floor is the trapdoor the first
design fell through.

---

## 2. What has already failed, precisely

### 2.1 The first detector died of a support violation

The 2026-09-10 murderboard stopped a self-supervised detector whose null was independent per-onset
dithering. The defect was not tuning. Dithering displaces each onset independently, so it
manufactures within-ROI intervals shorter than any real one — and a single count of sub-floor
intervals then separates real from surrogate **using no cross-ROI information whatsoever.**

The 2026-09-11 screen measured it. From `reproduction/leak_table.csv`, over 543 windows:

| stream | J | real share sub-floor | dithered share | leak AUC |
|---|---|---|---|---|
| fast | 1.6 s | **0.0** | 0.307–0.331 | 0.653–0.666 |
| fast | 2.5 s | **0.0** | 0.387–0.425 | 0.693–0.713 |
| slow | 2.5 s | **0.0** | 0.173–0.180 | 0.586–0.590 |

`real_share` is **exactly zero in all nineteen rows**. This is the sharpest possible form of leak:
not a distribution that differs, but a region of the space where real data has *no mass at all* and
the surrogate has plenty. A window containing one such interval is a certain negative. The
discriminator that learned it was a sub-floor-interval detector wearing a coordination detector's
name.

### 2.2 The obvious control could not see it

The natural control — dither-of-dither — was blind, because its own reference class already
contained the leak. A control drawn from the same broken construction cannot report the breakage.
This is why §2.1's numbers had to come from a per-statistic leak screen and not from the control.

### 2.3 Mixing does not repair a support violation, and we nearly believed it would

A natural repair is to draw each training negative from a randomly chosen generator, so the model
cannot learn "this is dither-shaped." Two sessions examined it independently on 2026-09-12 and
reached the same verdict, which corrects an earlier claim made in this thread that mixing could
rehabilitate leaky candidates.

Against a mixture, the optimal discriminator compares `p_real` with the weighted mean of the
members' densities. Wherever **any** member puts mass where real data has none, that ratio is zero
and the window is classified with certainty — no generator identification required. **Mixing
divides the leak's share; it does not close the hole.** With `m` members the shortcut still pays on
roughly `1/m` of negatives, and against a signal as thin as §1 describes, an easy fraction that size
can still dominate the gradient early in training, which is when shortcuts are learned.

The correct split, and it is the load-bearing distinction of this document:

- **Support violations must be absent per member.** They are inherited by the union.
- **Soft distributional differences** genuinely dilute under mixing.

A second, worse consequence: a mixture's implied null is a *disjunction* — "some member could have
produced this" — so the test inherits its **weakest** member's destruction. A member that barely
displaces onsets is near-real data sitting in the negative class, which is label noise aimed exactly
at the feature the model is supposed to learn. If mixing is used at all, the rule is **mix over
mechanisms, never over strengths**: every member destroys alignment finer than the same declared
scale, and only *how* varies.

### 2.4 Two reevaluations of the screen were withdrawn

Both 2026-09-12 drafts were withdrawn under eleven-role review, the same defect twice: probe numbers
used where production numbers existed. The record is
[`2026-09-12-surrogate-screen-reevaluated_2026-09-12.md`](../reviews/2026-09-12-surrogate-screen-reevaluated_2026-09-12.md)
and the plan is again the only authority for what was run. **This document does not restate their
conclusions**; where it needs a screen number it reads the run files directly.

---

## 3. What the literature already knows

**The construction is not new, and that is the point.** Recombining trains that were never
simultaneous is the *shift predictor*, standard since Perkel, Gerstein & Moore (1967): pair neuron
A's trial 1 against neuron B's trial 2, preserving each train's own structure while destroying any
physiological relationship between them. The modern population version is the **pseudopopulation** —
neurons pooled across sessions or animals — whose defining, documented consequence is that it
**eliminates noise correlations.** An entire methodological literature exists on what that
construction destroys, which is exactly the question being asked here.

**Where it is absent is informative.** Stella, Bouss, Palm & Grün (2022), read directly from
`stella_2022_comparing_surrogates.pdf` on the shelf, compare six methods — uniform dither (UD),
dither with dead time (UDD), ISI dithering (ISI-D), joint-ISI dithering (JISI-D), trial shifting
(TR-SHIFT) and window shuffling (WIN-SHUFF). **No cross-session or cross-preparation surrogate
appears in the catalogue at all.** The reason looks structural rather than principled: that
literature recombines across trials because its recordings have trials. Ours do not. Across
*preparations* is the recombination axis continuous imaging actually offers.

**The method that literature ranks best is the within-recording limit of what is proposed here.**
Stella et al. found TR-SHIFT the most robust of the six and used it for their own experimental
analysis. It shifts an entire train rigidly, so within-train structure survives untouched — the same
virtue claimed below, obtained by displacement rather than by substitution. bugarach's `rigid shift`
is that method, and it is already the only candidate in the 2026-09-11 screen surviving out to
1.6 s fast / 1.4 s slow (per the outside read filed as
[`join the leak results to the destruction results`](../todo/2026-09-12-join-the-leak-results-to-the-destruction-results.md);
the join itself has not been made and is a prerequisite below).

**And it carries a defect the substitution version does not have.** bugarach's rigid shift does not
wrap, so it loses onsets at the window edge — a *count* difference, which is Stella's diagnosed
failure mechanism for uniform dither arriving through another door
([todo](../todo/2026-09-12-rigid-shift-without-wrap-loses-onsets-at-the-window-edge.md)). A
substitution surrogate has no edge, because nothing is displaced.

---

## 4. The proposal: the ROI swap

**Construction.** Take a target recording **S** with N ROIs over duration T. Replace **k of N** ROIs
with duration-matched baseline trains drawn from *donor* recordings. Two knobs:

- **swap fraction** `k/N` — 0 is real, 1 is a full chimera. A dose axis, not a binary.
- **matching level** — the donor pool: within-session → within-mouse → within-group → global.

Each chimera is **paired to its target**: same N, same T, same frame rate, same window. Donors are
window-matched or not used; nothing is padded, resampled or stretched.

**Why it should work, stated as the property that killed everything else.** Every train in a chimera
*is a real train*. Therefore, on any within-ROI statistic, the null's support is a **subset** of the
real data's support. §2.1's failure mode is not reduced, not diluted, not controlled for — it is
**unavailable by construction**. There is no sub-floor interval to manufacture, no onset lost to a
window edge, no count changed by binarisation, because no onset is moved at all.

And destruction is **total rather than scale-limited**. Dither destroys alignment finer than J and
leaves a free parameter that has to be chosen and defended. ROIs from different preparations were
never coordinated at any scale, so the null is "these cells have no relationship," full stop. That
is a cleaner statement of *no coordination* than any dither, and by Amarasingham's rule the
statement is the hypothesis.

**Where the risk goes, and it does not vanish.** ROIs within one slice share bath temperature,
drift, photobleaching, imaging depth, health and rate scale. A chimera's ROIs do not. So a
discriminator can win by detecting **preparation identity** rather than coordination — and that
signal lives in the *cross-ROI* space, which is precisely the space the detector is supposed to use.
This is the single objection on which the design stands or falls, and §5 is built to measure it
rather than argue it.

Note the shape of the leak: because every train is individually real, the leak **cannot** be a
per-ROI statistic. It must live in the *heterogeneity across ROIs within a recording* — real slices
draw their ROIs from one preparation, chimeras from several. With a baseline per-ROI rate IQR of
0.0052–0.0190 Hz, a 3.7× spread, the global matching level is very likely to leak. That is a
prediction this plan tests first and cheaply.

**One precondition, already failing on one stream.** `real_vs_real` — real against real — is the
null of the null, and it must sit at chance or nothing here is interpretable. From
`discriminator/steps_excluded/discriminator.csv`:

| stream | accuracy | P | significant |
|---|---|---|---|
| fast | 0.5386 | 0.035 | **True** |
| slow | 0.5060 | 0.415 | False |

**Fast currently fails it**, and that same flag is the void reason stamped on 126 of 248 fast
candidates. The code that constructed `real_vs_real` is not in the repo, not in the run folder and
not in `reproduction/` — it lived in the workflow script and is now transcript-only. **Recovering
what it pairs is stage 0's first task**, because if it pairs different recordings then it is already
a measurement of this proposal's leak, and the fast answer is "detectable."

---

## 5. The plan, with expected results and a stop-or-go at every stage

Stages are ordered so that **the cheapest test that can kill the design runs first.** No stage
begins until its predecessor passes. Every stage emits its figure before its prose — the finding is
visual and this repo's rule is to render it, not describe it.

### Stage 0 — recover the precondition (no compute)

Establish what `real_vs_real` pairs, from the harness archives that hold the workflow script. Then
state whether fast's 0.5386 is a preparation-identity signal or an artefact of how pairs were drawn.

- **Expected if the design is viable:** `real_vs_real` pairs windows *within* a recording, making
  fast's flag a windowing artefact and leaving this proposal's leak unmeasured.
- **Expected if not:** it pairs across recordings, and 0.5386 with P = 0.035 is a direct measurement
  that preparation identity is detectable on fast.
- 🛑 **STOP if** it pairs across recordings *and* the effect survives stage 1's matching ladder. The
  swap is then leaking on the stream that matters most, and the design needs the matching ladder to
  rescue it before any model is trained.
- ✅ **GO otherwise** — and either way, record the answer, because 126 voided candidates depend on it.

### Stage 1 — the arithmetic leak prediction (no model, no GPU, minutes)

For each matching level, compute the **across-ROI dispersion** of per-ROI summary statistics — rate,
median ISI, event width, burstiness — within real recordings and within chimeras. No training, no
discriminator: just the distributions.

**Figure:** dispersion of per-ROI rate, real vs chimera, one panel per matching level, with the real
distribution as the reference band.

- **Expected:** dispersion rises monotonically as matching loosens. Global should separate clearly;
  within-mouse should nearly overlap the real band.
- ✅ **GO if** at least one matching level puts chimera dispersion inside the real band. That level
  is the design's operating point and everything downstream uses it.
- 🛑 **STOP if** *every* level separates, including within-session. That would mean the swap is
  detectable from ROI heterogeneity alone at any achievable matching, and no amount of training
  discipline fixes it. Report it as a negative result about the construction and stop.

This stage is the whole design's cheapest kill shot and it predicts the slope of stage 3
arithmetically. **Run it before anything else is built.**

### Stage 2 — construction validity (no training)

Run the **existing per-ROI-only discriminator** with real as one class and chimera as the other.
Because every chimeric train is a real train, a discriminator that sees one ROI at a time has, by
construction, *identical* marginal distributions in both classes.

- **Expected:** chance. Exactly chance.
- 🛑 **STOP if** it beats chance. That is not a finding about the preparation; it is a **bug in the
  chimera builder** — duration mismatch, resampling, a donor pool that is not baseline-only, or
  leakage of the target's own ROIs into its donor set. Fix and re-run.
- ✅ **GO on** chance.

This stage cannot succeed and is therefore worth running: its only possible outcome is catching our
own error before a model launders it into a result.

### Stage 3 — the coordination test (compute: the workstation)

Train `tube` to discriminate real (k=0) from chimera (k=N) at **every matching level**, and across
the dose axis `k/N ∈ {0.25, 0.5, 0.75, 1.0}`.

**The measurement is not the accuracy. It is the slope across the matching ladder.** Coordination is
destroyed equally at every level, so a tube using coordination gives a flat line; any rise from
within-mouse to global is preparation-identity leak, measured rather than asserted.

> **Intercept is signal. Slope is leak.** That decomposition is why the ladder is the design and not
> a refinement of it.

**Figure:** accuracy against matching level, one line per swap fraction, with the stage-1 dispersion
prediction overlaid.

- **Expected if the design works:** a flat, well-above-chance line — high accuracy that does not
  care where donors came from — and accuracy rising smoothly with `k/N`.
- **Expected if it leaks:** accuracy tracking the stage-1 dispersion curve, and a step up as soon as
  `k/N > 0` rather than a smooth rise, because one foreign ROI is enough to betray provenance.
- ✅ **GO if** the slope is flat within seed noise at some matching level.
- 🛑 **STOP if** slope dominates intercept everywhere. Self-supervision via ROI swap is then
  unavailable on this data — **which is a result about the preparation and worth writing up, not a
  failure.** The thread's missing exit criterion is filed as
  [a todo](../todo/2026-09-12-the-label-free-detector-thread-has-no-exit-criterion.md); this is it,
  stated before the numbers exist.

### Stage 4 — the ablation that decides what was learned

`tube`'s `bright` channel is a raw-brightness bypass the DC-free kernel never reaches — an absolute
local activity level, which is exactly where an aggregate rate difference between preparations would
enter. Re-run stage 3 with that channel removed. Dropping it is already filed as item 4 of
[the learned-detectors handoff todo](../todo/2026-08-16-learned-detectors-handoff.md).

- **Expected if the tube learned coordination:** accuracy survives, because centre-surround
  structure is what the kernel computes.
- **Expected if it learned the leak:** accuracy collapses toward the stage-1 dispersion prediction.
- ✅ **GO if** accuracy survives ablation. That is the affirmative result this whole plan exists to
  produce.
- ⚠ **Neither outcome is a stop** — this stage *interprets* stage 3 rather than gating it. But an
  unablated number must never be reported on its own after this stage exists.

Note `tube`'s own standing limitation, from its docstring: three probes on three training runs put
this channel's effect an order of magnitude apart and one was not monotonic. **Multiple seeds are
mandatory here**, not advisory.

---

## 6. The side quest: can `tube` learn group identity?

A separate question that the same construction answers, and worth asking on its own terms rather
than only as a confound.

FOUNDATIONS §9 records that treatment effects run in **opposite directions by group** — ORX up, male
unchanged, diestrus down under TTX — so groups genuinely differ. Whether that difference is visible
to a learned detector, and *where it lives*, is unknown.

`tube` is an unusually clean instrument for this because **cells are summed**: the architecture never
sees which ROI is which and runs at any cell count. So it cannot memorise ROI identity, and whatever
group signal it finds must be carried by aggregate temporal structure.

**Design.** Multiclass labels (DI / MALE / ORX / OVX), three conditions:

| condition | coordination | group identity | what it isolates |
|---|---|---|---|
| real recordings | intact | intact | is group visible at all? |
| within-group chimera | destroyed | intact | group signal *without* coordination |
| cross-group chimera | destroyed | mixed | the floor |

**The informative contrast is real vs within-group chimera.**

- **If accuracy holds on within-group chimeras:** group identity lives in **single-ROI statistics**
  aggregated over cells — rates, widths, shapes. Unsurprising, still worth knowing, and it means
  group is a nuisance variable the coordination test must match on.
- **If accuracy collapses:** group identity lives in the **coordination structure itself**. That is
  a result about the preparation rather than about the detector, and a considerably more interesting
  one — it would say groups differ in *how cells coordinate*, not in how often they fire.

Run the §5 stage-4 ablation here too: it separates "groups differ in rate" from "groups differ in
temporal structure."

🛑 **One hard constraint.** Split folds **by mouse, never by recording.** Otherwise the model
memorises individual animals and the group result is circular. This is the side quest's single
largest failure mode and it is cheap to get wrong.

⚠ **Group identity being learnable is not, by itself, bad news for §5.** It becomes a problem for the
coordination test only if it survives *within-group* matching — which is exactly what stage 3's
ladder measures. The two tests share one instrument and one construction on purpose.

---

## 7. What this plan does not settle, and what it costs

**Not settled.** Family size for the band statistics (Tony's, open). Whether the thirteen band
statistics flag on the night's existing data — deliberately not computed. Whether the intractable
joint-ISI candidates are bought; if the swap succeeds they may become *unnecessary*, which is a
consequence for Tony to rule on and **not** a pruning under the 2026-09-10 no-pruning ruling.

**A pre-registration opportunity, and it is free right now.** The family-size deadlock is a
*post-hoc* problem: choosing statistics after seeing which sit on the band floor. That trap does not
bind a run that has not happened. Declaring this experiment's statistic family **before stage 3
trains anything** is legitimate by construction, and it is unbuyable afterwards. Size it with
`surrogate_stats.correction_reach` against the splits actually intended.

**Prerequisite carried from the outside read.** The leak × destruction join has never been made
though both halves sit in the 2026-09-11 run folder
([todo](../todo/2026-09-12-join-the-leak-results-to-the-destruction-results.md)). Stage 1 should
consume it rather than re-derive it.

**An open question about power that bears on every "no leak detected" below.** The outside read
reports 1,261 of 2,630 ROIs as not estimable in a discriminator cell it opened. **This document has
not verified that figure** — the cell-level status counts in
`discriminator/*/discriminator.csv` are a different granularity (326 ok / 218 intractable on
`steps_excluded`, 106 / 99 on `cossart`). If the ROI-level figure holds, per-ROI leak power sits on
a minority of ROIs and "no leak detected" is weaker than it reads. **Settle it before stage 2's
chance result is trusted.**

**Compute.** Stages 0–2 need none worth naming and run anywhere. Stage 3 is the only real cost —
matching levels × swap fractions × seeds — and a session is live on the Windows workstation that can
take it. The darkroom is claimed for the 2026-09-11 run under board block 065; **a new run needs its
own claim before it writes anything.**
