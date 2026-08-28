---
status: open
filed: 2026-08-28
---

# The two readers write a different `width_def` for locust, on the same input

Found by the murderboard's fifth blind pass on export contract revision 8. **Not a
documentation defect and not introduced by that revision** — it is a live divergence
between bugarach's two implementations, in the output rather than the input, and it is
the same failure class `io.py:14-20` was written to record.

## The divergence

`detections.csv` carries a `width_def` column naming how **the detector** measured a
coordinated event's span. For locust the two readers disagree:

| reader | locust's `width_def` |
|---|---|
| Python — `emit.py:227`, `getattr(result, "width_kind", None)` | **`NA`** |
| Browser — `raster_viewer.html`, `DETECTION_FIELDS.cicada.widthDef` | **`tightness`** |

Confirmed from a real `bugarach detect` run: the row comes out `('cicada', 'NA')`. The
other five detectors agree between the readers.

**The browser's label is the right one.** `CicadaStream.width_sec` really is a tightness
span — `_peak_stats` computes `max(tmax - tmin, win_dur)` over member onsets, which is
exactly what `tightness` means for the detectors that declare it. `CicadaStream` simply
has no `width_kind` field, so the `getattr` default fires and writes `NA`.

## Why it matters more than a missing label

The contract tells producers every output column is self-describing from its header and
its unit column — *"No lookup file is required to read the output."* A `width_def` of `NA`
beside a real, meaningful `width_sec` breaks that promise for the one detector export
contract revision 8 is entirely about. A reader comparing the two implementations' outputs
sees the same span described two ways and has nothing to say which is right.

The browser's own registry comment already states the invariant this breaks:

> add one here and in `emit.DETECTOR_FIELDS`, not in one of them

## The fix, and the pin that should come with it

1. Add `width_kind: str = "tightness"` to `CicadaStream`.
2. **Pin the two registries against each other**, the way
   `tests/test_webapp_detections_download.py` already pins `strength_unit`. Nothing
   currently compares them on `width_def`: `grep widthDef tests/` returns one unrelated
   hit. The precedent landed with revision 8 —
   `tests/test_site_viewer.py::test_both_readers_agree_which_widths_reach_a_peak` does
   exactly this for `WIDTH_REACHES_PEAK`, and it is six lines.

That second step is the point. This is the third place in one review where the two
implementations of one contract were found to disagree with nothing checking, after
`WIDTH_REACHES_PEAK` (now pinned) and the viewer help panel naming one accepted spelling
of two (now fixed and pinned). A general rule is earning itself: **where both readers
declare the same thing, a test compares the declarations.**

## Also filed here, same pass, same document family

- **A partly-peaked folder is scored on the subset, silently.** `cicadaTrains` refuses
  only when *no* event carries a peak; given a mix it drops the peakless events and says
  nothing. Measured: 160 events, 77 peaked, locust scored 77. The number that would say
  so, `nWithPeak`, is computed and returned and **read nowhere in the file**. Revision 8
  now warns producers about this; surfacing `nWithPeak` as a locust `extra` — the way
  single-cell moments already are — would make the page say it too.
- **Both built pages scroll horizontally below ~1000px**, because `.doc pre` in
  `docs/learned/report.css` has no `overflow-x: auto`. The offenders are the sample
  transcripts. Pre-existing, cosmetic, and one line.
