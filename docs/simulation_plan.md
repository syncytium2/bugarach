# Rebuilding the coordination simulator, with training sets in view

**Status:** plan, not built. Supersedes the "port it" framing in
[`todo/2026-08-12-port-coordination-benchmark.md`](todo/2026-08-12-port-coordination-benchmark.md)
— that todo stays the inventory of what exists upstream; this is the design.

## The one-paragraph version

Port interface2's generator faithfully **first**, held to the same 1e-9 MATLAB
parity bar as the six detectors, because that is cheap, gives us the benchmark,
and replaces an unreproducible committed fixture. Then build the training
generator as a **strict superset** whose defaults reproduce the port exactly, so
the parity test doubles as a regression test forever. The hard part is neither
of those: it is that the current generator is homogeneous Poisson and we have
**no labeled real data**, so nothing yet measures the domain gap. Plan for that
explicitly instead of discovering it after training a model.

---

## 1. Why simulate at all — the argument that actually holds

The tempting shortcut is to train on detector output over real recordings. That
produces a **detector emulator**, not a detector: it inherits every bias of
whichever detector labeled it, and cannot exceed its teacher.

Worse, there is no single teacher to copy. The six disagree on what an event
*is* — `episode` vs peak mode, `width_kind` of `tightness` / `episode_span` /
`half_prominence` (GLOSSARY). Ask them to label the same recording and you get
six different label sets. There is no consensus target.

Planted ground truth sidesteps this entirely: the label is **what was planted**,
not what a detector said. That is the whole case for simulation here, and it is
a strong one.

## 2. What already exists (verified, not assumed)

`generate_synth_coord.m` (193 lines) and `generate_coord_benchmark.m` (158)
already emit ground truth in a usable shape:

```
gt.events(k) .time .n_part .frac .jitter .rois     <- .rois is the participant list
gt.times / .n_part / .frac / .jitter               <- column vectors
gt.part_levels / .tight_levels                     <- grid axes
gt.distractors                                     <- correlated bursts; NOT recall targets
gt.bg_rate_at = @(t)                               <- local background rate, for FA-vs-density
gt.params                                          <- provenance
```

Two design choices upstream got right and we must keep:

- **`hot_window`** — a dense-but-random block with a linear wash-in ramp and *no*
  planted events, replicating a drug onset. A rate-fooled detector fires there.
  The ramp exists because a sharp step edge produced a boundary false alarm.
- **`gt.distractors`** — correlated population bursts: genuine cross-ROI
  coincidence that is *not* a coordinated event, scattered in the dense half.

These are the hard negatives. For a parameter sweep they were false-alarm
counters; **for a training set they are labeled negative classes**, and they are
the single most important ingredient for learning rate-invariance. A network
trained without them will learn "lots of spikes at once = event" and fail
exactly where the detectors already fail.

**Fixture provenance, resolved.** `generate_synth_coord` documents `es.fast/.slow`
as *identical* streams with `locs == t50rise`. The committed
`tests/fixtures/synth_fastcal_s1.mat` has exactly that signature (probed:
byte-identical streams, `t50rise == locs`, 30 ROIs, 32 bins with ≥5/30 coactive).
It almost certainly came from this generator family, even though the string
"fastcal" appears nowhere in interface2. It still has no generator in *this*
repo and no stored labels — which is why porting replaces it.

## 3. The two-layer architecture

This is the central decision.

```
Layer 1  simulate/_matlab_port.py     faithful port; bit-parity with MATLAB
                                      params: the MATLAB defaults, one RNG stream
                                      TEST: 1e-9 vs committed reference JSONs
           ^ special case of v
Layer 2  simulate/generator.py        the training generator; a strict superset
                                      params: distributions, not scalars
                                      TEST: layer-1 defaults reproduce layer 1
```

Why this shape and not "just write the good one":

- **Parity is affordable here.** `RandomState(seed) ≡ rng(seed)` is already
  verified (FOUNDATIONS §2), and the generator's RNG use is simple (`poissrnd`
  then `rand`). A port can be held to the detectors' own 1e-9 bar rather than
  "looks about right", which is the standard this repo is built on.
- **It buys a permanent regression test.** Once Layer 2 can reproduce Layer 1
  exactly at default settings, any future change to Layer 2 that breaks that
  equality is caught by a test that already exists. Without it, a training
  generator silently drifts and nobody notices for months.
- **It keeps the benchmark honest.** Detector calibration must run on the *same*
  generator the MATLAB numbers came from, or the F1 values are not comparable to
  `constellation/`'s.

`default_rng` is banned in `src/` (sapper SAP002) — both layers use
`RandomState`. That is also what parity requires, so there is no tension.

## 4. What changes when the consumer is a network

| | calibration sweep (today) | training set (needed) |
|---|---|---|
| **volume** | 2 seeds | 10³–10⁴ recordings |
| **labels** | event time list + tolerance match | dense per-(ROI, frame) participation mask **and** per-event records |
| **negatives** | counted as false alarms | first-class labeled classes |
| **params** | fixed scalars per run | sampled from priors per recording (domain randomization) |
| **output** | `.mat` + figures | a stable on-disk dataset contract |

### 4.1 Labels

`gt.events(k).rois` already carries participation, so the information exists; it
needs emitting in a trainable form. Minimum viable label set per recording:

- **per-event**: `t_center`, `t_start`, `t_end`, `participants` (ROI indices),
  `n_part`, `frac`, `jitter_sigma`, `class ∈ {coordinated, distractor}`
- **per-(ROI, frame)**: boolean participation mask on the imaging grid
- **per-frame**: event/no-event, plus `n_participants` as a regression target
- **per-recording**: the generating parameters (provenance and stratification)

Emit the sparse form as the source of truth and rasterize on demand — a dense
`(ROI × frame)` mask for a 30-ROI, 4520 s, 10 Hz recording is 1.4 M cells, and
storing 10⁴ of those is wasteful when the events are sparse.

### 4.2 Domain randomization

Sample per recording rather than fixing: `n_roi`, duration, background rate
(and its time profile), participation, tightness, distractor count and
`distractor_frac`, imaging rate, `hot_window` presence and depth. A network
trained at one operating point learns that operating point. This is also the
cheapest defense against the measurement problem in §5.

### 4.3 Realism gaps in the current generator

Today's background is **homogeneous Poisson** per ROI (`poissrnd(rate*T)`, then
uniform placement). Real trains are not. In rough order of likely impact:

1. **No refractory period.** Poisson allows arbitrarily close events; calcium
   events cannot overlap. Easy fix, changes short-timescale statistics a lot.
2. **No per-ROI rate heterogeneity.** Every ROI fires at the same rate. Real ROIs
   vary by an order of magnitude, and a detector's `min_rois` behaviour depends
   on that distribution.
3. **No bursting / ISI structure.** The committed fixture's own ISI CV is 1.13
   with a 0.0 s minimum — not Poisson-like.
4. **No upstream detection noise.** bugarach consumes *already-detected* events
   (GLOSSARY: "per-ROI events / trains"). Real inputs carry missed and spurious
   onsets from the event-extraction stage. Training on perfect inputs and
   deploying on noisy ones is a classic, avoidable domain gap. Model it as
   per-event drop probability and a spurious-event rate.
5. **Identical streams.** `es.fast/.slow` being byte-identical means the stream
   axis carries no information. Fine for single-stream labs (most of them,
   FOUNDATIONS §3), wrong for the canonical two-stream stores.
6. No drift, no region/treatment effects, no amplitude/width covariates.

Do **not** fix all six before shipping anything. (1), (2) and (4) are the ones
that plausibly change what a network learns; the rest can wait for evidence.

## 5. The traps this project already paid for — read before writing any generator

Everything in this section is documented in
`<darkroom>/constellation/optim_history/` (the `optim_history.pptx` deck, its
README, and the figures it embeds). It is not hypothetical: this exact project
has already paid for each of these once.

### The contaminated null — the benchmark's event spacing collided with the detectors' context window

The **dense benchmark** — the first one — planted **a coordinated event every 14 s**. The detectors
estimate their null over a **60 s context window**. So **four coordinated events
sat inside every context window**: the circular-shift "null" was built from data
containing real coordination, and the threshold inflated. The **calibrated benchmark** that eventually replaced it spaces events
150 s (FAST) / 300 s (SLOW) — one per window, a clean background-only null.

The cost, measured (`deploy_cost.png`, dense-tuned settings run on sparse data —
**both synthetic**):

| | RateDetect | SCE | CICADA | spike-sync | CoactDetect | LoCo |
|---|---|---|---|---|---|---|
| precision where tuned | 90 | 74 | 58 | 75 | 90 | 89 |
| precision when sparse | **45** | **10** | **10** | **30** | **16** | **21** |

The deck's own conclusion: *"The benchmark, not the detectors, was the original
problem."*

**Why a network does not escape this.** It has no circular-shift null, so this
looks like somebody else's problem. It is not. Event spacing sets the **class
base rate**: train where events are ten times too frequent, and the model learns
that events are ten times more likely than they are, then over-fires on sparse
real data. *Same observable failure — precision collapse on
deployment — reached by a different mechanism.* Any generator knob that changes
how often events occur is a knob on the label distribution, not a cosmetic
realism detail.

### Realism is not one property — and randomizing is not centering

The benchmark was rebuilt twice. The **dense** original had both the wrong
spacing and made-up timescales. The **sparse rebuild** fixed the spacing — and
stopped there, keeping the made-up timescales and covering only the FAST stream.
Only the third version, the **calibrated** one, replaced those timescales with
onset jitter and per-ROI rates measured off real recordings.

The middle version is the cautionary one: it fixed the thing everyone was looking
at, looked repaired, and was still wrong.

This tempers the domain-randomization section above: **domain randomization widens a distribution, it does
not center one.** Sampling event spacing over [10, 60] s when reality is 150 s
covers reality zero percent of the time — and produces a confident-looking
training set. Randomize *around measured values*, never instead of measuring them.

### The skipped gate — the step named as deciding is the one that got skipped

The deck listed four next steps. The first was *"validate the calibrated settings
on real data in the viewer"* — and the deck says plainly that the decision rested
on it. Two weeks later it had **not been done, and not been attempted.** The
fourth step was *"revisit the benchmark decision, then touch production."* That
one happened backwards: production changed first. The calibrated settings became
the shipped defaults without the validation, and the change is not subtle — on
one real recording it takes LoCo from **81 detected events down to 28**.

It did not happen because it was hard to reach. A viewer crash had blocked it,
but a fix was sitting on a pushed branch the whole time. The record's own words:
*"not prioritised, not impossible."*

**And the caveat was not missing.** Nearly every slide carries "Not validated on
real data" in its footer. The warning was present, prominent, repeated — and
overridden anyway. That is the strongest possible argument for this repo's own
rule: *prefer a firing check over prose* (FOUNDATIONS §9). A gate that is a
sentence is not a gate. The checks section below makes it a script.

### Structural flaws don't tune away — and a network hides its own

CICADA's F1 sat at 0.68 through **all three generations** — 83% recall, 57%
precision, ~19 false alarms per recording. Root cause: it has no
minimum-active-cell floor, so it fires on sparse low-count coincidences that
SCE / CoactDetect / LoCo reject (they require ≥3 co-active ROIs). Raising a
percentile cannot add a floor the algorithm does not have. The adoption raised
CICADA's SLOW percentile anyway — `generate_sce_cicada.m` still
has no `min_rois` gate, and the flaw is still open.

For a network this is *worse*, not better. CICADA's flaw was visible by reading
the algorithm. A model's equivalent — no notion of a participant floor, or a
learned dependence on local rate — cannot be read off the weights. **Behavioural
probes are the only instrument**, which promotes `hot_window` and
`gt.distractors` from diagnostics to required, thresholded tests — see the
checks section.

### Scope mismatch — tuned whole-recording, deployed per-region

SCE and CICADA were tuned under **global** scope on single-region, whole-trace
synthetic data. The real-data viewer runs **per-region** scope. Generate in the
scope the thing actually deploys in.

### Stranded validation — the numbers were checked against a benchmark that then changed

Leave-one-recording-out cross-validation was run against the **sparse rebuild**.
When the calibrated benchmark replaced it, that validation was not redone — the
shipped operating points are **not cross-validated**, and *the detector ranking differs between the two
generations*. Any change to the generator invalidates every validation number
computed before it — silently, unless something enforces the link.

### An optimum at the edge of the search isn't an optimum

Several optima sit at the extreme of the swept range (SCE/CICADA percentiles;
CoactDetect alpha 1e-6; CICADA 99.9999 SLOW). An optimum at the boundary means
the true optimum may lie outside it — the search reports a number either way.

### Artifacts outlive the settings that made them

An export produced by the **old** settings sat on disk for weeks after they were
replaced, indistinguishable at a glance from current output. Nothing about the
file said which settings made it.

## 6. The honest blocker: nothing measures the domain gap

Two facts that have to be stated plainly:

1. **The realism measurement exists and is used, but was never reviewed.**
   (An earlier draft of this file implied the measurement had not been made. It
   has.) The calibrated benchmark is built from onset-jitter and per-ROI rate measured off
   the real baseline, and those files —
   `fast_coordination_measured.mat`, `slow_coordination_measured.mat`,
   `coordination_timescale_*`, `rate_measured.*`, `width_measured.*` — live in
   `<darkroom>/constellation/` (deliberately *not* moved into `optim_history/`,
   because other work reads them too). What is missing is the **review**:
   `rederive_optima_fast.m` still says "PROVISIONAL — params from a measurement
   pending Tony's review". So the number is real, in use, shipped as production
   defaults — and unsigned. Training on it bakes an unreviewed constant into a
   model instead of into a config file.
2. **There is no labeled real data.** So "does the synthetic distribution match
   reality" is currently unanswerable, and a model can look excellent on
   held-out synthetic while failing on a real slice. This is not a hypothetical:
   the calibrated settings were adopted into production **without** the
   real-data validation step, so right now nobody knows whether the calibrated
   benchmark improved real detection or only synthetic scores.

### What to do about it

- **Step 0 is measurement, not code.** Extract from the real stores (machine-local,
  `BUGARACH_DATA_ROOT`): per-ROI rate distribution, ISI distribution and CV,
  refractory floor, coactivity distribution, and the coordination timescale. Get
  the timescale reviewed. These become the generator's priors, and the same
  script becomes the realism check — a two-sample comparison of synthetic vs real
  summary statistics that runs in CI-adjacent form and fails loudly when the
  generator drifts from the data.
- **A small gold set is worth more than a lot of realism work.** A few hundred
  hand-labeled real events — even just "these windows are events, these are not,
  these are ambiguous" — would give the only honest evaluation number in the
  project. Worth asking whether that is affordable *before* building the
  generator, because it changes what the generator has to be good at.
- Absent a gold set, fall back to weaker but real signals: regime-shift tests
  (train sparse → test dense), the `hot_window` probe as a standing test, and
  agreement with the six detectors on real slices (not truth, but a large
  disagreement is a finding).

## 7. Staging

Each stage is independently useful — nothing here is only valuable if the DL
work happens.

| # | stage | delivers | depends on |
|---|---|---|---|
| 1 | Port Layer 1 + parity test | benchmark runs in Python; the opaque fixture is replaced by a regenerable one | MATLAB once, to emit reference JSONs |
| 2 | Port scoring (`score_coord_detection`, `score_coord_grid`) | recall-by-participation and FA-vs-density for all six ports | 1 |
| 3 | **ROC / sensitivity bench across the six** — plus the regime-shift test | a portfolio-grade result, and a standing guard against the contaminated null | 2 |
| 4 | Measure real-data statistics; review the timescale | the generator's priors, and a realism check | real stores + Tony's review |
| 5 | Layer 2: superset generator + domain randomization + noise model | training-set generation at volume | 1, 4 |
| 6 | Dataset contract + label emitter + rasterizer | a stable on-disk format | 5 |
| 7 | Gold-set labeling (scope TBD) | the only honest eval number | a human decision |

**Stages 1–3 are worth doing on their own merits.** They replace an
unreproducible fixture and turn `deploy_cost.png` from a figure into a test.

One correction to an earlier draft: the bench is **not** the first comparison of
the six — that exists, pooled over 6 seeds (deck slide 14: LoCo FAST F1 0.86 at
99% precision; SCE and CoactDetect 0.83; spike-sync 0.82; CICADA 0.68;
RateDetect 0.44). Its value here is different and larger: a Python bench can be
run by anyone without MATLAB, wired into CI, and — unlike the MATLAB campaign —
made to **fail** when a regime shift or a participant-floor probe regresses.

The measurement stage is the gate — and the checks below are what stop "the gate"
from meaning what it meant last time.

## 8. Making the gate mechanical — the actual anti-trap work

The load-bearing lesson is the skipped gate: **a gate written as a sentence gets
skipped.** The deck named its deciding step, footered every slide with "not
validated on real data", and production shipped without it anyway. So the following are not
recommendations in this document — they are things to build, and each one is a
specific trap turned into a check that fails closed.

| check | what it stops | shape |
|---|---|---|
| **Provenance stamp on every dataset** — which generator built it, which measured-parameter files it drew on, whether those were reviewed, and which scope it used. Model artifacts record the dataset they came from. | stranded validation; stale artifacts | metadata written at generation; nothing to remember |
| **Promotion gate** — refuse to mark a dataset or model "production" while its measurements are unreviewed, or when the generator has moved on since it was built. | the skipped gate; stranded validation | `tools/check_training_provenance.py`, exit 1 |
| **Regime-shift test** — train or tune in one regime, evaluate in the other, and fail if precision drops more than a set amount. | the contaminated null | a test, not a figure |
| **Negative-class probes, with thresholds** — false-alarm rate inside the dense-but-random block; fire rate on the correlated-burst distractors. | the contaminated null; hidden structural flaws | required test cases |
| **Participant-floor probe** — plant events with too few participants and assert the model stays quiet. | hidden structural flaws | a behavioural test for a structural property |
| **Edge-of-range guard** — if the chosen operating point lands on the boundary of the range that was searched, fail instead of reporting it. | optima at the edge of the search | an assertion in the sweep |
| **Measured-vs-synthetic statistics check** — compare per-ROI rate, interval distribution, coactivity and event spacing against real recordings. | mistaking one fixed axis for realism | the realism check above |

The regime-shift test deserves emphasis: **the precision-collapse figure is a
test that was drawn as a picture.** Had it been an assertion from the start, the
dense benchmark would have failed on day one instead of after two weeks of tuning
against it. Turning that one figure into a standing test is probably the single
highest-value item on this page.

The stamp and the promotion gate are what make the measurement step an actual
gate rather than an intention. Written only as prose, it is the same sentence the
deck wrote — and that sentence lost to a shipping deadline.

## 9. Open questions for Tony

1. **Is a hand-labeled real gold set affordable?** Even ~200 events. It changes
   the plan more than any technical choice here.
2. **Has the coordination-timescale measurement been reviewed** since
   `rederive_optima_fast.m` was written, or is it still pending?
3. **Single-stream or two-stream targets?** Most outside labs have one stream
   (FOUNDATIONS §3), and the current generator's streams are identical. Is
   cross-stream coordination a thing we want the generator — and eventually a
   model — to represent?
4. **What is the actual downstream goal:** a better detector, a faster one, or a
   *calibration-free* one? They imply different training targets, and only the
   third is clearly worth the trouble given six working detectors already exist.
   The optim_history campaign sharpens this: the expensive, repeated failure was
   **calibration against a mis-specified benchmark**, not detection itself. A
   model whose selling point is "no operating point to mis-tune" would attack the
   thing that actually cost two weeks — twice.
5. **Should the real-data validation (deck item 1) be run before any of this?**
   It has been outstanding since 2026-07-23, the viewer crash that blocked it was
   fixed on 2026-08-04, and current production defaults rest on it. Porting a
   Everything downstream would rest on a number nobody has checked — which is
   the same mistake as last time, one level up: skipping the check because
   there was something more interesting to build.
