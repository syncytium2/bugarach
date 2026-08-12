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

## 5. The honest blocker: nothing measures the domain gap

Two facts that have to be stated plainly:

1. **The benchmark's realism parameters were never signed off.**
   `rederive_optima_fast.m` says "PROVISIONAL — params from a measurement pending
   Tony's review". The benchmark is parameterized by the *measured coordination
   timescale*, and that measurement was not reviewed. Training on it bakes an
   unreviewed number into a model instead of into a config file.
2. **There is no labeled real data.** So "does the synthetic distribution match
   reality" is currently unanswerable, and a model can look excellent on
   held-out synthetic while failing on a real slice.

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

## 6. Staging

Each stage is independently useful — nothing here is only valuable if the DL
work happens.

| # | stage | delivers | depends on |
|---|---|---|---|
| 1 | Port Layer 1 + parity test | benchmark runs in Python; the opaque fixture is replaced by a regenerable one | MATLAB once, to emit reference JSONs |
| 2 | Port scoring (`score_coord_detection`, `score_coord_grid`) | recall-by-participation and FA-vs-density for all six ports | 1 |
| 3 | **ROC / sensitivity bench across the six** | a portfolio-grade result, and the first real answer to "which detector, when" | 2 |
| 4 | Measure real-data statistics; review the timescale | the generator's priors, and a realism check | real stores + Tony's review |
| 5 | Layer 2: superset generator + domain randomization + noise model | training-set generation at volume | 1, 4 |
| 6 | Dataset contract + label emitter + rasterizer | a stable on-disk format | 5 |
| 7 | Gold-set labeling (scope TBD) | the only honest eval number | a human decision |

**Stages 1–3 are worth doing on their own merits.** They replace an
unreproducible fixture, and they answer a question the lab actually has — how the
six detectors compare, and where each fails — without committing to any machine
learning at all. Stage 4 is the gate: everything after it depends on numbers
nobody has reviewed yet.

## 7. Open questions for Tony

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
