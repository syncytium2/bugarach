---
status: open
filed: 2026-08-28
---

# The export sends `peak_sec`, locust anchors on the peak, and nothing connects them

Found while importing another lab's corpus, by asking what a folder without a
peak would do. The answer turned out to be a question about the folders that
*have* one.

## What is true

`cicada_detect(..., onset_field="locs")` is the default, and its own docstring
says what that means:

> onset_field anchors the raster, and the default is "locs" — **the PEAK, not the
> onset**. […] a single-cell event runs 10-60+ s from half-rise to peak, so
> **scoring coincidence on onsets alone would call nearly any two events
> coordinated**.

That is correct for a **store**, where `locs` *is* the peak. For an **export
folder** it is not. `bugarach.store.Stream` says so plainly — a folder's `locs`
is the half-rise, "the only time `docs/export_folder_spec.md` guarantees", and a
peak the producer sent goes to `Stream.peak` because it "has nowhere else to go."

Verified on `dataset.current()`, recording `20240708_13`, fast stream:

```
locs[0:3]  [ 513.2  893.9 1516. ]
t50rise    [ 513.2  893.9 1516. ]     <- identical to locs
peak[0:3]  [ 513.6  894.2 1516.5]     <- loaded, and never read
has_peak   True
```

So on folder input:

1. **`onset_field="locs"` and `onset_field="t50rise"` select the same array.** The
   parameter that chooses CICADA's own parity convention over explore_sce's
   collapses to one behaviour, with no error. The viewer passes `"t50rise"`
   deliberately (`ui/app.py`); `bench.py` passes nothing and takes the default.
   **Both get half-rises.**
2. **`peak_sec` is loaded and never consumed.** No caller passes
   `onset_field="peak"`. `getattr(stream, "peak")` would work — the capability
   exists, the data exists, nothing joins them.

The producer knows CICADA needs it. `<data>/bugarach/README.md` says: *"It
matters most to **CICADA**, which anchors on the peak of each transient rather
than its half-rise and recovers that peak from `peak_sec`, or from `time_sec +
width_sec` where `width_def` says the width reaches the peak."* interface2 sends
the column for this reason.

## What is NOT established, and must not be assumed

**The size of the consequence is unmeasured.** On fast the peak lags the
half-rise by ~0.3–0.4 s (0.4 s in the sample above); the contract puts it at
~0.3 s fast and ~2 s slow. Whether that changes a detection is an experiment
nobody has run, and this file does not claim it does.

It is **tempting** to read this as the explanation for locust's promiscuity — 85
firings (35 after retune) on the decoy block where LoCo and CoactDetect fire
zero, which is the exact symptom the docstring predicts for onset-anchoring.
**That is a hypothesis with a matching symptom, not a finding.** The honest test
is to run the bench at `onset_field="peak"` and compare; until then the
resemblance proves nothing.

Note also that `OPERATING_POINTS["cicada"]` was calibrated on
`simulate_coordination` output, which is not a folder — so the calibrated point
and the deployed input may not agree about what `locs` means. That is worth
checking before any re-fit.

## Why this was invisible

Nothing is wrong on either side alone. The store path is right, the folder path
is documented, the viewer's override is deliberate, and the parity tests run on a
store fixture where `locs` genuinely is the peak. **The defect lives in the joint
— one parameter name meaning two quantities depending on where the slice came
from** — and no test loads a folder and asks a detector what it anchored on.

## What would settle it

1. Run the bench at `onset_field="peak"` on `dataset.current()`, fast only, and
   compare F1 and decoy firings against the deployed default.
2. Decide whether `onset_field` should **refuse** `"locs"` on a folder stream that
   has a peak, the way `--store` is refused on a folder-only analysis — a
   parameter that silently means two things is the shape sapper rules exist for.
3. Whichever way it goes, `cicada_detect`'s docstring needs to say what `locs`
   means per input kind. It currently asserts "the PEAK" without qualification.

Not fixed here: this was found from a branch whose claim excludes
`src/bugarach/detectors/**` on purpose, and retuning a detector to chase a
hypothesis is how the original error would repeat.
