# From viewer to workflow — the plan

## Part I — the decision

### The problem

bugarach can already run six coordination detectors and draw them. It cannot be
*used* end to end: there is no way to point it at a set of recordings, no way to
tune the generator to those recordings, and **no way to get results out of it at
all** — nothing in the tree writes a result file in any format.

Most of what is missing already exists as capability. It is locked inside
command-line scripts in `tools/` that take flags and write pictures to Dropbox.
**An app can call a function; it cannot call a script.** So the bulk of this work
is moving capability into the library, not writing new machinery. The screens are
thin once that is done.

### What the app takes in, and what it gives back

The app reads **one export folder and nothing else**. It never opens a data
store, never derives an analysis window, and never reaches outside the folder it
was given. Region windowing is the exporter's job — ours in MATLAB, whoever else's
for an outside lab. Event properties (amplitude, width, rise time) belong to a
different project and are not read here: the detectors need per-ROI **event onset
times** and nothing more, which is what `src/bugarach/io.py` already says.

| file in the folder | one row per | carries |
|---|---|---|
| `events.csv` | one detected event in one ROI | `slice_id, stream, roi, time_sec` |
| `regions.csv` | slice × region | `slice_id, region, treatment, treatment_idx, start_sec, end_sec` — **already windowed** |
| `slices.csv` | slice | identity: `slice_id, group_id, mouse_id, …`; optional, absent means NA |
| `metric_dictionary.csv` | metric | the column contract, shipped with the batch |

Output is **universally compatible first**. One computation, two writers: a plain
long-format `detections.csv` any pipeline can read, and the contract frames that
stack against the existing R analysis. Matching that contract is worth doing where
it is free; where it conflicts with being readable by a stranger, the stranger
wins and the R side adapts.

### What acting buys first

The first thing to build — porting the uniform width/amplitude yardstick — also
produces a measurement this project has wanted for two days. `docs/generator.md`
carries an open flag that the generator's onset-jitter constant is calibrated
against a statistic barely above its own noise floor, and that it does not
round-trip. `docs/reviews/generator_2026-08-14.md` names the median event span and
median width as the candidate replacements. Those are medians of what the yardstick
returns per event, so milestone 1a produces the input to that decision.

⚠ **That is a candidate, not a cure.** The yardstick's own outputs are bounded by
measurement parameters — the span by the collection aperture, the core span by the
clustering gap, which at 0.5 s sits inside the 0.42 s noise band of the statistic
being replaced. Retiring the flag needs a surrogate null computed *for the new
statistics* and a round-trip test. Porting alone delivers neither.

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

### Open decisions — yours

1. **Does the exporter emit `treatment_idx`?** It is what the R side uses to order
   baseline against first treatment. If the exporter derives it from region order,
   the whole identity chain works with no sidecar. If not, output cannot be stacked
   against existing files without a join.
2. **Which mode does a generated run report as?** The MATLAB exporter emits nine
   detector keys in real mode and six in surrogate mode, and the per-event file is
   written only in real mode. Choosing wrong either omits three keys or claims
   three that were never computed — and can delete milestone 1a's only consumer.
3. **Should we ask the R side to accept the peak-mode keys**, or hold them back?

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

**Parity, and the trap in it.** The golden CSVs cannot test this function — they
are the summary grain, produced by a different reducer that never calls it.
Provable from the shapes alone. Build synthetic fixtures through
`tools/matlab_ref/` the way every detector's oracle was built, and keep the
goldens as a machine-local end-to-end check of the *export*.

**Pin the production settings, not the defaults.** The clustering gap is
per-stream — 0.5 s for the fast stream, 2.5 s for the slow one — and the
coactivity window defaults to whichever gap applies. A fixture built at the
default validates one stream and silently ships a wrong yardstick for the other.
The port must carry the per-stream broadcast, not a scalar.

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
both background parameters by maximum likelihood on a negative-binomial count
model, with a drift gate that fails when the constants in the source stop matching
the data. **That gate lives entirely in the command-line half and is the most
valuable thing in the file — lift it with the compute.**

**Do not fit to a summary.** The dispersion curve is a *reported diagnostic*, never
the objective. The file says why in its own docstring: matching the statistics by
search reproduces them without the mechanism. Report the curve beside the fitted
shapes.

**Report both the mean and the median rate, and state the pairing.** The mean is
what the generator consumes, and it is only correct when the heterogeneity
parameter is set. Fitting and then generating with heterogeneity off walks back
into a calibration error this project already made once.

**The acquisition interval cannot be fitted — take it from the folder or ask.**
It is a property of the microscope. Note that the parameter governed by
FOUNDATIONS §6 is the detector-side grid, not the generator's quantization knob;
they are different parameters in different modules and only the first raises a
warning.

**Do not fit jitter.** It is not identifiable *by the estimator that produced the
current value* — that estimator is censored by a minimum-group-size floor, sits
below its own surrogate null, and does not round-trip. Carry the number as a named
prior with the round-trip failure beside it.

**Participation — a consistency check, not an independent one.** Estimating it
from coactivity excess over a circular-shift null uses the same machinery four of
the six detectors use, so a fitted value cannot validate a detector calibrated on
it. Two further constraints: the excess must be taken as a *distribution* over
coactivity levels, since a scalar cannot separate how many coordinated moments
there are from how many ROIs each recruits; and the shift window must be at least
as long as the structure it is meant to destroy — the shipped detectors shift
inside a rolling context of one to two minutes, while real burst structure runs to
five. Apply the same round-trip test jitter got. If it fails, participation joins
jitter as a named prior.

### 1c — the writers

**Two shapes from one computation.** A long-format detections file for general use,
and the contract frames for the existing R analysis.

- The recruitment field is **present and missing-filled** for the detectors that
  have no recruitment measure — not absent. Dropping the column yields a frame one
  column short of the contract.
- The written per-event file carries one more column than its builder emits; a
  validator built to the builder's count rejects real files.
- Spell missing values literally as `NA` — the default in Python's CSV writer is an
  empty field, which the contract does not name. Emit newline-only endings; a stray
  carriage return poisons the last column under exact comparison.
- A real zero is not a missing value. Some detectors legitimately report a
  tightness of exactly zero, meaning perfectly synchronous. Preserve it.
- **The validator detects a non-conforming schema and has no power over a
  conforming schema carrying wrong values** — which is the failure the contract
  exists to stop. Assert against the dictionary's unit and direction fields too,
  and diff values against a known-good file.

### 2 — batch

**Do not reuse the viewer's compute path directly.** It is a drawing function that
also detects: it builds full-length traces and asks two detectors for signals
purely so they can be rendered. Over a folder that dominates runtime and memory
for arrays nobody draws. Extract the six-way dispatch; let the viewer and the batch
each take what they need.

Four divergences to resolve deliberately while extracting:

- **The viewer and the bench feed CICADA different onset fields.** They coincide on
  synthetic single-stream data and diverge on real recordings, which is why this has
  gone unnoticed. This is the one that changes a detector's input.
- **The bench's runner is hardcoded to a single stream**, so it cannot be the batch
  home unchanged; it becomes a convenience wrapper over the extracted dispatch.
- **A third consumer already exists** — the diagnostic tool imports the viewer's
  private compute function because it needs per-stream traces. Changing that
  signature breaks it silently.
- **One surrogate seed is shared across every slice**, so nulls across a folder are
  not independent draws. A feature in a redrawing viewer; a choice that must be made
  deliberately for a batch and stated in anything aggregated.

Two smaller ones: the synchrony branch reports a threshold default duplicated from
its own signature, so a partial parameter set makes the reported value diverge from
the applied one; and two detectors are fed different arrays for the same stream.

**Figures do not compare across slices** as they stand: drawn detection width is
floored relative to recording length, so the same detection renders differently on
a short and a long recording; raster height saturates at both ends of its clamp;
and each trace row scales to its own data with nothing marking it. Fix before any
cross-slice figure ships.

### 3 — comparison

Move the comparison tools into the library, **but apply the outstanding fix list
first** — `docs/reviews/roi_rate_distribution_2026-08-15.md` is a do-not-ship record
whose fixes are not yet applied, and most of them are code. Lifting unchanged turns
fourteen known script defects into a library interface.

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
