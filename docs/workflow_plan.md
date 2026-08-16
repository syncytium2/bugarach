# From viewer to workflow — the plan

## Part I — the decision

### The problem

bugarach can already run six coordination detectors and draw them, and the viewer
already opens a whole directory. What it cannot do is finish: there is no way to
tune the generator to the recordings you loaded, and **no way to get a result out
of it** — every number stays on screen. Nothing in the tree writes a data file. It
writes pictures, and a page, and one text report; it has never written a table a
statistician could open.

Most of what is missing already exists as capability, locked inside command-line
scripts in `tools/` that take flags and write images to a shared folder. **A screen
needs a function it can call and a value it gets back; a script gives it neither.**
So the bulk of this work is moving capability into the library, not writing new
machinery. The screens are thin once that is done.

### What the app takes in, and what it gives back

The app reads **one export folder and nothing else**. It never opens a data
store, never derives an analysis window, and never reaches outside the folder it
was given. Region windowing is the exporter's job — ours in MATLAB, whoever else's
for an outside lab. Event properties (amplitude, width, rise time) belong to a
different project and are not read here: the detectors need per-ROI **event onset
times** and nothing more, which is what `src/bugarach/io.py` already says.

The contract is written in full in
[`docs/export_folder_spec.md`](export_folder_spec.md). In short: four CSVs, of
which **only `events.csv` is required** — `slice_id, stream, roi, time_sec`, and
nothing else read.

Periods are carried by `regions.csv`, one row per region, ordered by a plain
`region_idx` and named by the lab's own `label`. There is no notion of a treatment
*slot*, so there is nothing to run out of: one region is a recording with no
protocol, six is a baseline and five conditions. No region is privileged, no label
is special, and windows arrive **already computed** — bugarach never derives one.

Identity in `slices.csv` is an **open column set**, passed through untouched, with
exactly one exception: `frame_interval_sec`, the acquisition sampling interval.
That one is read, because several detectors build a rate trace on a grid that must
be the acquisition interval, and it cannot be recovered from onset times. Absent, a
0.1 s fallback applies and warns every time — a deliberate noise that must not be
silenced.

Output is **universally compatible first**. One computation, two writers: a plain
long-format `detections.csv` any pipeline can read, and the **contract frames** —
the two table shapes the existing R analysis already reads. Matching them is worth
doing where it is free; where it conflicts with being readable by a stranger, the
stranger wins and the R side adapts.

### What acting buys first

The first thing to build is the **yardstick**: one function that measures how wide a
coordinated event is, applied identically to every detector, so their widths become
comparable at all. Porting it also yields a statistic this project has wanted since
the generator review.

`docs/generator.md` carries an open flag that the generator's onset-jitter constant
of 0.36 s is calibrated against a statistic that sits **below its own surrogate
null** of 0.42 s, and that does not round-trip — build a recording at 0.36 and the
estimator reads back about 0.64. `docs/reviews/generator_2026-08-14.md` names two
candidate replacements: a median event **span** and a median **width**. The port
delivers the first. It cannot deliver the second — that "width" is the stored
transient width, which the yardstick is defined to exclude and which this app does
not read at all.

⚠ **A candidate, not a cure, and only half of one.** The span the yardstick returns
is bounded by the aperture the caller collects over; its straggler-robust variant is
capped by the 0.5 s clustering gap, the same order as the 0.42 s null it is meant to
escape. Retiring the flag needs a surrogate null computed *for the new statistic*
and a round-trip test. The port delivers neither, and the second candidate belongs
to another project.

### Read this before running anything

- **A worktree's Python imports the primary checkout's `src`.** The virtual
  environment is an editable install rooted in the primary checkout, so a test run
  from a worktree can execute a different branch's code and pass. Set
  `PYTHONPATH=src`, then confirm it took — `python -c "import bugarach;
  print(bugarach.__file__)"` must print a path inside the worktree. This has
  already invalidated a reported clean test run, and it invalidates every check
  below it.
- **The primary checkout is far behind `origin/main`.** Standing in it and setting
  `PYTHONPATH=src` loads stale code deterministically rather than correctly.

### Build order

1. **1a — port the uniform yardstick** (`characterize_coord_window.m`). Pure,
   deterministic, no randomness. Parity-tested against synthetic fixtures.
2. **1b — the fitting stage.** Measure an export folder well enough to configure
   the generator.
3. **1c — the writers.** Both output shapes, plus a validator that refuses a
   non-conforming frame. Export button on the existing viewer; the quick path —
   see the data, tune each detector, run, get a file — is then complete.
4. **2 — batch.** Run the folder through all six detectors on an extracted
   dispatch.
5. **3 — comparison.** Move the generated-vs-real tools into the library.
6. **4 — generator and optimization screens.** Thin wrappers over `simulate` and
   `bench`.
7. **5 — a named deep-learning seam.** It appears in the interface and does
   nothing. Recorded for whoever fills it: training data comes from planted truth
   only, never from detector output — score against detector calls and you measure
   agreement, not truth; train on them and you get a detector emulator
   (`docs/generator.md`).

### How we will know it worked

- The full test suite, with the import path confirmed first.
- **Parity** for the port: synthetic fixtures through `tools/matlab_ref/`, compared
  at the tolerance the detectors already use, with exact equality on integer
  fields. Hand-derived adversarial vectors for the branches the MATLAB test file
  does not reach.
- **Contract**: emitted frames validated against the shipped dictionary; read back;
  `NA` spelled literally; newline-only endings; a real zero preserved as zero
  rather than becoming missing.
- **Self-containment**: a folder with only `events.csv` produces detections,
  figures and an export. Nothing reaches outside it.
- **End to end**: point the app at a folder, tune, run, export; the result opens
  in R and in pandas.

### Decisions taken here, so nothing waits on them

- **Ordering is `region_idx`; naming is `label`.** The pair the existing contract
  calls `treatment_idx` / `treatment` is **derived at write time**, never stored
  twice. Two independently-editable records of one fact is a failure this ecosystem
  has already had, with disagreeing row counts to show for it.
- **bugarach reports what it computed.** It has no notion of a run "mode". If a
  detector ran in peak-gated form, its key appears in the output; if it did not,
  the key is absent. The upstream exporter's mode switch is that exporter's
  implementation detail and is not mirrored here.
- **Peak-gated keys are emitted.** Universally compatible first: a consumer that
  cannot yet read them adapts, rather than the producer withholding a result it
  computed.
- **Figures are deferred to the deliverables, not the plan.** Two reviewers flagged
  that a plan violating "show the picture" is still a plan; the same gate will
  demand figures of the reports and captions this work produces, where the picture
  is the payload rather than the argument.

---

## Part II — execution detail

*Read the section for the milestone you are starting.*

### 1a — the uniform yardstick

The detector decides **where** a coordinated event is; this function decides **how
wide**, identically for every detector, from real onset times. That is what makes
widths comparable across detectors at all — each detector's own width is a
different quantity (a tightness for some, an episode duration for others) and is
explicitly not comparable.

It returns the full extent between first and last onset, and a straggler-robust
version over the largest single-linkage cluster. Deliberately onset-based; stored
transient widths are excluded, and that boundary must survive the port.

**Parity, and the trap in it.** The reference exports come in two grains. The
**summary** files cannot test this function — a different reducer produces them and
never calls it, provable from the column shapes alone. The **per-event** export
does call it and is a genuine oracle, so it is the machine-local end-to-end check.
Neither can be committed: both are real-derived, which FOUNDATIONS §5 keeps
machine-local, and CI must still have a gate. So build synthetic fixtures through
`tools/matlab_ref/` the way every detector's oracle was built — those travel — and
use the per-event export as the second, local check.

**Pin the production settings, not the defaults.** Three of them, and the plan
previously named one:

- the **clustering gap** is per-stream — 0.5 s fast, 2.5 s slow. A fixture at the
  default validates one stream and silently ships a wrong yardstick for the other,
  so the port must carry the per-stream broadcast rather than a scalar.
- the **collection pad** is 0 in production, and the MATLAB test file's last case is
  entirely about it.
- the **collection aperture** belongs to the caller, not to this function — one
  second either side of the event centre. It is what Part I's ⚠ is actually about,
  and it is a different parameter in a different function.

**Amplitude: port it, and know it will be empty here.** Five of the function's
outputs aggregate event amplitudes. Amplitudes are another project's and this app's
input contract has no column for them, so on real bugarach input every one of those
fields is missing. Port them anyway — parity is against the MATLAB oracle, which
computes them — but do not present them as results, and note that the
length-mismatch branch compares against the ROI's **full** onset array rather than
the in-window subset. A port that naturally writes the in-window comparison
diverges on every ROI with an event outside the window, which is most of them.

**Branches the MATLAB test file does not reach** — hand-derive vectors for each:
the cluster tie-break when two clusters hold equal counts; the strict gap boundary
(onsets exactly a gap apart stay together); that peak coactivity counts distinct
ROIs rather than onsets; non-finite onsets; the defaulted coactivity window; the
amplitude-length-mismatch fill.

**MATLAB semantics that actually apply here** — the reductions drop non-finite
values and return missing on empty, which numpy's `nan*` family does not
reproduce: it propagates infinities, returns zero for an empty sum, and warns
rather than returning. Use an explicit finite mask and an empty guard. The
median in the summary reducer propagates missing values deliberately. The
percentile, rounding and grid helpers in `_shared.py` are not reached by this
function; say so rather than leaving it open. Sort with a stable kind so the
argument does not have to be re-derived.

### 1b — the fitting stage

**Use the estimator that exists.** `tools/fit_background_shape.py` already fits
**three** shapes by maximum likelihood on a negative-binomial count model: how
unevenly activity is spread across ROIs, and how much each ROI clumps in time at
two scales. It fits **no rate level** — every window keeps its own mean by
construction. It also carries a drift gate that fails when the constants in the
source stop matching the data. **That gate lives entirely in the command-line half
and is the most valuable thing in the file — lift it with the compute.**

**Do not fit to a summary.** The dispersion curve is a *reported diagnostic*, never
the objective. The file says why in its own docstring: matching the statistics by
search reproduces them without the mechanism. Report the curve beside the fitted
shapes.

**Report both the mean and the median rate, and state the pairing.** The mean is
what the generator consumes, and it is only correct when the heterogeneity
parameter is set. Fitting and then generating with heterogeneity off walks back
into a calibration error this project already made once.

**The acquisition interval cannot be fitted.** It is a property of the microscope,
and it arrives as `frame_interval_sec` in `slices.csv` — the one field in that file
bugarach reads. Absent, the 0.1 s fallback applies and warns, and the warning stays.
Note this is the detector-side grid governed by FOUNDATIONS §6, not the generator's
onset-quantization knob; different parameters in different modules, and only the
first warns at all.

**Do not fit jitter.** It is not identifiable *by the estimator that produced the
current value* — that estimator is censored by a minimum-group-size floor, sits
below its own surrogate null, and does not round-trip. Carry the number as a named
prior with the round-trip failure beside it.

**Participation — a consistency check, not an independent one.** Estimating it
from coactivity excess over a circular-shift null uses the same machinery four of
the six detectors use, so a fitted value cannot validate a detector calibrated on
it. Two further constraints: the excess must be taken as a *distribution* over
coactivity levels, since a scalar cannot separate how many coordinated moments
there are from how many ROIs each recruits; and the shift window must be at least as
long as the structure it is meant to destroy. The shipped detectors disagree about
that window — CoactDetect shifts inside a rolling minute and LoCo inside two, while
CICADA rolls across the whole recording and SCE across the whole region — and real
burst structure runs to five minutes. Say which window the fit uses and why. Apply
the same round-trip test jitter got; if it fails, participation joins jitter as a
named prior.

### 1c — the writers

**Two shapes from one computation.** A long-format detections file for general use,
and the contract frames for the existing R analysis.

- The recruitment column — **`amp_median_total`**, how many ROIs an event recruited
  — is **present and missing-filled** for the two detectors that have no recruitment
  measure, RateDetect and SPIKE-synch. Not absent. Dropping it yields a frame one
  column short of the contract.
- The written per-event file carries one more column than its builder emits; a
  validator built to the builder's count rejects real files.
- Spell missing values literally as `NA` — the default in Python's CSV writer is an
  empty field, which the contract does not name. Emit newline-only endings; a stray
  carriage return poisons the last column under exact comparison.
- A real zero is not a missing value. Some detectors legitimately report a
  tightness of exactly zero, meaning perfectly synchronous. Preserve it.

**The validator's power, stated honestly.** A dictionary-driven check catches a
**schema** that does not conform and has **no power at all** over a conforming
schema carrying wrong values — multiply every width by a thousand and it passes.
That is the failure the contract exists to stop, so say what actually catches it:

- Asserting against the dictionary's unit and direction fields catches **schema
  drift only** — those fields describe the column, not the row, and nothing in them
  moves when a value is wrong.
- The one check with power is a **byte-diff against a known-good frame**. The real
  reference exports cannot be committed (FOUNDATIONS §5), so CI needs a
  **synthetic** known-good frame, produced by this port from a committed fixture and
  diffed on every run. The real diff is a second, machine-local gate.

Without that synthetic reference, the contract check is a spell-checker.

### 2 — batch

**Do not reuse the viewer's compute path directly.** It is a compute function shaped
for the plot: it materialises a full-length trace per detector and forces two of
them to emit signals purely so the viewer can draw them. Over a folder that
dominates runtime and peak memory, for arrays that are discarded undrawn.

**Seed the extraction from the bench's runner, not the viewer's.** A name-keyed
six-way dispatch already exists there and already absorbs both call shapes — three
detectors take a whole recording, three take one stream's trains plus the extent —
so callers work in detector names rather than signatures. It has one limitation the
viewer's does not: it is hardcoded to a single stream. Lifting that assumption is a
smaller change than extracting the dispatch out of the viewer, and it leaves the
viewer a consumer rather than a donor.

Four divergences to resolve deliberately while extracting:

- **The viewer and the bench feed CICADA different onset fields.** They coincide on
  synthetic single-stream data and diverge on real recordings, which is why this has
  gone unnoticed. This is the one that changes a detector's input.
- **The bench's runner is hardcoded to a single stream**, so it cannot be the batch
  home unchanged; that assumption is what gets lifted.
- **A third consumer already exists** — the diagnostic tool imports the viewer's
  private compute function because it needs per-stream traces. Changing that
  signature breaks it silently.
- **One surrogate seed is shared across every slice**, so nulls across a folder are
  not independent draws. A feature in a redrawing viewer; a choice that must be made
  deliberately for a batch and stated in anything aggregated.

Two smaller ones. The synchrony branch reports a threshold default duplicated from
its own signature, so a partial parameter set makes the reported value diverge from
the applied one. And the detectors disagree about clipping: RateDetect is fed trains
clipped to the recording extent, while CoactDetect and SPIKE-synch are fed the raw
onset arrays. Decide which is correct and apply it once.

**Figures do not compare across slices** as they stand: drawn detection width is
floored relative to recording length, so the same detection renders differently on
a short and a long recording; raster height saturates at both ends of its clamp;
and each trace row scales to its own data with nothing marking it. Fix before any
cross-slice figure ships.

### 3 — comparison

Move the comparison tools into the library, **but apply the outstanding fix list
first** — `docs/reviews/roi_rate_distribution_2026-08-15.md` is a do-not-ship record
whose fixes are not yet applied, and most of them are code. Lifting unchanged turns
its fourteen ranked blocking-and-major defects, plus ten smaller ones, into a
library interface.

Core returns numbers and figure objects — never a verdict, and never a file path.
The moment a function returns "match: yes/no", someone optimizes against it. The
command-line shell decides where anything lands.

Consolidate the four screenshot helpers into one. They differ in viewport, scale
and wait, and only one carries the fix for an empty-selection crash that another
still documents as a hazard. Keep the fixed clipping logic and the parameterized
scale; no single copy is canonical as it stands.

Match the library's window convention — the tools are half-open at the top, the
library closed at both ends. One event per boundary, systematically, across every
window the fitting stage measures.

### 4 and 5 — deliberately unspecified

The generator and optimization screens are thin wrappers over machinery that
already works, and the deep-learning seam does nothing. Neither has a section here,
and that is a decision rather than an omission: the generator is under active
development by another session, so writing its screen down now would specify a
moving target, and the seam has no defined output to specify at all. Whoever picks
either one starts by writing the section.

### Coordination

- Claim shared external output on `docs/SESSIONS.md` before writing it.
- The generator is under active development by another session. Call it; do not
  reach into it. Pin it by commit in the fitting stage, and make the semantic gate
  a round-trip test rather than a stable function signature — a parameter's meaning
  can change while its name does not.

### What changed from the previous revision

Region windowing, data-store reading, archive layout, the metadata sidecar, the
treated-window refusal and the quarantine hazard all left scope: the app now reads
one self-contained folder and derives no windows. Event properties left scope; only
onset times are read. The fitting method changed from moment-matching a dispersion
curve to the maximum-likelihood estimator already in the tree. The parity target
changed from the golden files to synthetic fixtures, because the goldens cannot
exercise the ported function. Four quantities that could not be traced to any source
were removed.
