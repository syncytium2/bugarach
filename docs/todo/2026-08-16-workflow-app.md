---
status: open
filed: 2026-08-16
---

# Grow bugarach from a viewer into the full workflow

Tony, 2026-08-16: the app should cover the whole arc — a folder of recordings in,
measure them well enough to configure the generator, check the generated data
against the real, generate simulated data for detector optimization, run all six
detectors, and hand off publishable figures plus a statistics export.

This is the plan as reviewed by four sessions (interface2, the generator session,
the generator-doc session, and fireflies as the R consumer) and revised on their
findings. **A murderboard run against this revision was commissioned and its record
belongs at `docs/reviews/jazzy-watching-pixel_2026-08-16.md`** — if that file is
absent, the review did not land and this plan has had peer review but not the gate.

## What Tony settled

- **No upload, no server.** Data is processed on the user's own machine. He
  corrected an early misreading in terms: *"the whole idea of the app is to allow a
  user to process data on their computer without upload. i misspoke."*
- **One route, CSVs.** Reading them is already built — `load_events_csv` in
  [`io.py`](../../src/bugarach/io.py) takes long-format `time_sec`/`roi`
  (+ optional `stream`), [`ui/app.py`](../../src/bugarach/ui/app.py)'s `load_any`
  routes `.csv`, and the CLI globs a whole directory.
- **The unit of work is a folder of slices**, not one recording. A statistics
  handoff over a single recording is a figure, not a handoff.
- **Quickstart** — see the data, adjust each detector's parameters, then run. This
  is essentially the existing viewer; what it lacks is a way to write the run out.
- **Not every user has the R side.** *"whatever we do should be flexible enough for
  general use."* Lab-specific things are optional and degrade to something useful —
  joining regions (§4) and streams (§3), which are already optional.
- **The generator exists and is upgraded concurrently.** Call it; never reach in.
- **The deep-learning module is an idea at best, outputs undefined.** A named empty
  seam. Train only on planted `gt.events` — never on detector calls, which yields a
  detector emulator rather than truth.

## The structural finding

Most capability exists, but as `tools/*.py` argparse scripts writing PNGs to the
darkroom. **An app can call a function, not a script.** So the bulk of the work is
lifting capability into `src/bugarach/`; the screens are then thin.

**Lift the refusals with the compute, not the CLI.** `make_reality_check.py` refuses
any slice whose regions are not exactly `{baseline}`;
`make_roi_rate_distribution.py` refuses when the data root is unset rather than
guessing. Those guards are what make the scripts safe to run. Leave them in argparse
and you ship a library function that will happily fit a treated window.

Consolidate `_render_png` while passing — four copies exist with different
viewports, scales and waits, and two carry a clip-to-ink fix the other two lack.

## The export contract — port, don't design

It already exists and was **not** ported when the detectors were. The detectors
carry the in-memory half of the contract; nothing in this tree writes results in any
format.

**Authority chain.** The contract's `PROTOCOL.md` makes the dictionary a *mirror* of
the canonical ADR, with the ADR winning on conflict — but interface2's review queue
flags ADR 0005 stale on stream-by-filename. So **the golden fixtures arbitrate**.

**Golden fixtures are the parity target**: nine real exporter CSVs with checksums
and a check script, in the `team_major_coincidence` contract folder (a personal
Dropbox path — resolve it locally, it is deliberately not recorded here). 480 rows
each, 84 slices, 18 columns, zero failures. Its README flags that **`sce` has 3
tightness zeros and `loco` has 5 — real zeros, not missing**, which is the
NA-vs-zero test case handed over rather than invented.

`metric_dictionary.csv` (tracked in fireflies) is **v1.1**: 37 data rows, 15
columns, versioned **per row** — key the validator on the row's own version, not a
document version. A stale third copy exists elsewhere and must not be picked up.

### What to port, in order

1. **`characterize_coord_window.m`** — the uniform yardstick, and the reason the six
   detectors are comparable at all. Pure and deterministic: no I/O, no RNG. Returns
   `span_sec` (last − first onset) and `core_span_sec` (largest gap-clustered core,
   single-linkage). **`coact_sec` defaults to `gap_sec` — a defaulted option is a
   parity variable, so pin it.** An assertion test exists upstream: a free oracle.
2. **The per-event writer** that consumes it. Porting the yardstick without this
   leaves it with no downstream.
3. **The region-summary reducer** — one row per slice × region × stream. Zero-event
   regions still emit a row, so a consumer never has to distinguish "found nothing"
   from "slice missing". Membership by window bounds, never by region label.
4. **`detector_settings.csv`** — long/tidy `detector, stream, param, value`. A
   scalar is written for *both* streams deliberately: the file records what each
   stream was run with, not the struct's shape.

**The width distinction is per-grain and must not be collapsed:**

| grain | width column | comparable across detectors? |
|---|---|---|
| summary | the detector's own width kind | **no** — tightness vs episode duration |
| per-event | `span_sec` / `core_span_sec` | **yes** — one yardstick |

### Corrections that change the build

- **Source keys are mode-gated.** The three peak variants are emitted in REAL mode
  only — nine keys real, six surrogate. **Open decision: which mode does a generated
  run report as?** Getting it wrong silently omits or fabricates three source keys.
- **One generic reducer plus a small shim.** Three detectors speak the native
  contract; rate, sync and coact are adapted through a shim. **Recruitment is NaN
  for rate and sync** — they have no such measure, which is why the dictionary has
  no `amp_total` rows for them. The reducer must tolerate its absence rather than
  emit the column.
- **"Unknown column is a hard ingest error" is stated but NOT enforced** downstream:
  fireflies' validator checks only that value columns are present and the source key
  resolves; a missing dictionary falls back to legacy behavior. **Our validator would
  be the only place that rule ever fires — build it, but do not assume R catches what
  we let through. Today it silently mislabels instead.**
- **RateDetect emits rolling context, not excess over a scalar.** The spec is stale
  and the code is right. This does not reach any CSV, but it does bear on the port.

### Emission rules

- **`source_key` is never NA**, even when all identity is. It is a data column
  precisely so nobody recovers meaning by parsing filenames. Parser rule: strip only
  a trailing `_(fast|slow)` — *not* "detector keys have no underscore", which the
  peak variants already violate.
- **Spell missing as literal `NA`, and emit LF.** pandas writes empty by default; a
  trailing `\r` poisons the last column under exact comparison.
- **Ship the dictionary with the batch.** The contract requires it and the MATLAB
  producer does it — and it is the answer to "works with no R side": the lab gets
  the dictionary in the folder rather than from someone's Dropbox.
- **Identity is optional; the treatment *index* is load-bearing.** fireflies' ingest
  ignores identity entirely, so an all-NA frame ingests clean and renders as a raw
  viewer — exactly the general-use case. But analysis needs group and treatment as
  model factors and the **index** to order epochs: the before/after contrast is
  defined as index 1 against index 2. A sidecar carrying only a label is not enough.
- **ROI membership as a separate sidecar**, keyed `(slice_id, source_key,
  event_idx)`. It cannot be a column on the contract frames. fireflies explicitly
  wants it — for relating coordinated events back to the per-ROI stream, for
  participation analysis, and for QC.

## The fitting stage

### The contradiction to avoid

An earlier draft required the degradation check to succeed on bare CSVs with no
region annotation *and* the fitting stage to refuse treated windows. **These
conflict.** §4 gives an un-annotated recording one implicit whole-recording window,
so a user with treated recordings and no annotations gets the whole treated
recording fitted as baseline, silently, and the refusal never fires because there
was nothing to refuse — Tony's rule defeated through the door marked "general use".

**Fitting requires a positive assertion that the windows are untreated.** Absence of
annotation means *cannot fit*, not *fit everything*. Degradation still applies to
the viewer and export paths, which is where general use actually matters.

### What to estimate, and what not to

- **Temporal clumping is a curve, not a scalar.** Real ROIs grow steadily more
  over-dispersed as the window widens while independent bins stop growing past the
  bin — one scale provably cannot reproduce real data, which is why the generator's
  burst knob takes a sequence. Return dispersion at each of several bin widths,
  with the widths.
- **Return median as well as mean rate, and state which the generator eats.** The
  mean is only correct when heterogeneity is on. A user who fits and then generates
  with it off reproduces the original calibration bug — the mean of a heavily
  right-skewed distribution applied to every ROI — from numbers that look
  authoritative.
- **The imaging grid cannot be fitted; ask for it, with no default.** §6: it is the
  acquisition sampling interval, the stores do not carry it, and the fallback raises
  its warning on purpose. For a stranger's folder that fallback is a guess about
  their microscope.
- **Do not fit jitter.** It is not identifiable from this data at all, independent
  of any circularity: the value in use was measured against a statistic whose own
  circular-shift null is larger than the measurement, and it does not round-trip.
  Carry it as a **named prior** with the round-trip failure cited beside it.
- **Participation can be fitted honestly** — estimate the coactivity distribution's
  excess over a circular-shift null and read recruitment off the excess in
  aggregate. That never labels an individual moment, so it needs no detection
  threshold and is not circular. A circular shift preserves each ROI's own
  burstiness while destroying cross-ROI alignment, which is the right null now that
  both real fields and the generator are bursty — provided real data is shifted
  rather than compared against a flat synthetic. **Report the minimum group size
  beside the value** (it is left-censored by that floor), and never present it as
  independent validation of a detector calibrated on it.

### Immediate scientific payoff

[`generator.md`](../generator.md) carries an open flag that the jitter constant is
calibrated against a near-null statistic, and names span/width medians as the
replacement candidates — **exactly what the yardstick returns**. The first port in
this plan therefore produces the measurement that could retire it.

## Batch and figures

- **Do not reuse `_compute` directly.** It is a drawing function that also detects:
  every branch returns full-length signal traces, and it asks two detectors for
  traces solely so they can be rendered. Over a folder that is the dominant cost and
  memory, for arrays never drawn. Extract the detector dispatch and let the viewer
  and the batch each take what they need — `bench.run_detector` already solves the
  same two-call-shape problem, so the dispatch is currently written twice.
- **The surrogate seed is a module constant**, so every slice in a folder draws the
  identical null. That is a feature in a redrawing viewer and a misstatement in a
  batch; choose it deliberately and say which was used in anything aggregated.
- **Two inconsistencies to fix while extracting**: the sync branch reports a
  threshold default duplicated from the signature, so a partial parameter dict makes
  the reported threshold differ from the one used; and coact reads onsets directly
  while rate goes through the shared helper, so a slice with one field empty and the
  other populated feeds two detectors different data in the same row.
- **Stream keys vary per slice**, and `stream` is an export column, so heterogeneous
  naming across a folder surfaces immediately.
- **The figure layer breaks cross-slice comparability three ways**: drawn width is
  floored relative to the recording extent, so the same detection renders differently
  on a short and a long recording; raster height saturates above roughly seventy
  ROIs; and each trace row takes its y-limits from its own data, so scales differ
  between figures with nothing marking it. The scoreboard also requires planted
  truth, so real slices get none.

## Build order

**1a.** Port the yardstick, parity-tested against its upstream assertion test and
the goldens. **1b.** The fitting stage — it consumes the yardstick and can retire
the jitter flag. **1c.** The reducers, the per-event writer, the settings file, and
the dictionary-driven validator; then an export button on the existing viewer, which
completes quickstart. **2.** Batch, on the extracted dispatch. **3.** Lift the
comparison tools — core returns numbers and figure objects, the CLI decides where
anything lands, and **the core returns numbers, never a verdict**: the moment a
function returns "match: yes/no", someone optimizes against it. **4.** Generator and
optimization screens, thin. **5.** The DL seam, named and inert.

## Traps

- **A worktree's Python imports the primary checkout's `src`** — the venv is an
  editable install rooted there. Use `PYTHONPATH=src` and verify with
  `python -c "import bugarach; print(bugarach.__file__)"`. This silently invalidated
  a reported "344 passed". **Listed first because it invalidates every other check.**
- **`bench.make_recording()` is not the background model** — it carries planted
  events and a probe far above background, so most of its realized rate is not
  background. Use `make_null_recording` with the regime's own parameters.
- **Pooled dispersion cannot isolate temporal clumping** — ROI-rate spread and
  within-ROI clumping both move it, and the first is already fixed.
- **Interval distributions are unavailable** — the median ROI has under one event per
  baseline window. Binned counts only.
- **A zero-event ROI is not a dead ROI.** fireflies owns that verdict; it needs drug
  and high-K rows and is not computable baseline-only.
- **Some archived batches sit in a quarantine folder** — do not reach for them as
  reference data without asking Tony.

## Verification

- `pytest`, with the worktree-import trap checked first.
- **Parity** for the yardstick against its upstream assertion test and the golden
  CSVs, on the detectors' existing oracle chain.
- **Contract check**: emitted frames validated against the dictionary's per-row
  version; round-trip read-back; `NA` spelling and LF endings asserted; the
  tightness **zeros** confirmed as zeros rather than NA.
- **Degradation**: bare CSVs, no sidecar, no regions → the viewer and export produce
  usable output while the **fitting stage refuses, loudly, with a reason**.
- The handoff schema doc and any figure caption are document deliverables — run the
  murderboard, then the roster check.
