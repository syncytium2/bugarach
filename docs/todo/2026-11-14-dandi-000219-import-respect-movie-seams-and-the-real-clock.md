---
status: open
filed: 2026-11-14
---

# DANDI:000219 import: respect movie seams and the real clock

**Scope: the Cossart corpus only, which is foreign data.** None of this lab's recordings is
affected. It is filed because bugarach is expected to carry all future work on the Cossart
corpus (Tony, 2026-11-14), and the import should not leave a trap for that work.

## What is wrong

Each DANDI:000219 session is **five movies of 2,500 frames each**, recorded back to back
with **gaps of about 17–18 s** between them in the frame timestamps. Two rigs were used,
at 10.79 Hz and at 8.44–8.48 Hz.

[`tools/import_dandi.py`](../../tools/import_dandi.py) `runs(raster, dt, t0)` ignores both
facts:

- **Times come from `t0 + frame × dt`, never from the timestamps.** The importer reads only
  `t[0]` and the median frame interval from each extracted session. The gaps therefore
  vanish, and every event after the first movie lands earlier than it happened: by about
  17 s in the second movie and up to about 70 s in the fifth.
- **Runs are found over the whole raster.** A cell active in the last frame of one movie and
  the first frame of the next becomes **one event** spanning a seam that was never recorded
  as continuous.

## What it costs

1. **The seam merges are unmeasured.** They feed the transfer statistics in
   [`assessment_cossart.json`](../learned/assessment_cossart.json): event rates, coactivity
   excess by *K*, and from there the generator specs in
   [`cossart_transfer/`](../learned/cossart_transfer/README.md). The effect is probably
   small, since at most four seams fall in each session, but nobody has counted it.
2. **The clock is wrong.** Anything aligned to the sessions' own behavior epochs (movement
   start and stop) would be off by up to about 70 s. Nothing does that today.

What it does **not** cost: the spliced time base is the right one for detection. Taking the
real timestamps (gaps included) would be the worse error, and the next section says why.

## The rule for any foreign recording with gaps

1. **Splice the segments for detection.** Time = frame index × that session's own frame
   interval, with the movies back to back. The nulls in `sce.py` and `cicada.py` build their
   grid over the extent from the first event to the last
   (`detectors.rate.recording_extent`) and know nothing about gaps. Fed real timestamps,
   they count each gap as recording time in which the data hold no events but the circular
   shifts place some. That dilutes the null and lowers the threshold. With splicing, a wrap
   crosses only movie seams, as any circular shift does.
2. **Find runs inside each segment**, so that no event spans a seam.
3. **Map calls back to the real timestamps** before anything is aligned to an external clock
   or reported in time.

The frame interval is per session. Pass each session's own, never a corpus-wide one, because
the two rigs differ by about 28%.

## Done when

- ✅ **2026-11-14.** `import_dandi.py` splits runs at movie seams and writes real
  timestamps, and `imaging.csv` declares the movies. The contract question was settled by
  [ADR 2026-11-14-7a3a](../adr/2026-11-14-7a3a-a-recording-imaged-in-stretches-says-so-in-imaging-csv-detec.md)
  and revision 11 of [`export_folder_spec.md`](../export_folder_spec.md): `time_sec` stays
  real, and the stretches go in a new optional table. Tony asked for the import to be
  fixed in this repository, so `movies()`, `runs()` and `bugarach.imaging` were written
  here rather than taken from the outside adapter.
- ✅ **Re-imported 2026-11-14, with the four reserved sessions left out** (Tony's call).
  The input was `dandi-cache slice --preset cossart-raster`, which streams only the raster,
  its timestamps and the ROI ids. The 58 sessions total 69 GB as NWB files and were not
  downloaded. They were read through an explicit manifest (`import_dandi.py --manifest`).
  The result is 54 recordings: 863,353 events, 1,255 zero-event ROIs, five movies each, and
  every recording loads and validates against its `imaging.csv`. It sits in a local folder on
  the Mac mini (`~/data/exports/external/dandi_000219_20261114`), not under a data root,
  because that machine has none. **Six recordings carry `analysis_hold` in `slices.csv`**:
  they share an animal with a reserved session, and nothing analyses them until the hold is
  cleared.
  **Four sessions could not be imported as they stand.** `sub-190921-190927-1_ses-190927-a000`
  has 11,873 raster frames against 12,500 timestamps, and nothing says which frames the
  times belong to. `sub-200108-200117-1_ses-200117-a001`, `sub-210226-210307-1_ses-210307-a000`
  and `sub-210226-210308-1_ses-210308-a000` have no raster under
  `processing/ophys/fluorescence_all_cells`. DANDI lists 62 sessions; the first import had
  59, which probably means it skipped the same three.
- ⬜ **The reserved four go in once their hold ends**, and the folder replaces the old one
  on the machine that holds the data root. Nothing has run on the new folder; the transfer
  re-measure waits for Tony.
- ⬜ **Detection on this corpus runs on spliced time and reports in real time.** The helper
  exists (`imaging.splice`, with a pad stated per detector, and `to_real`). The route from a
  folder to calls ([ADR-0020](../adr/0020-one-route-from-a-folder-to-calls-per-stream.md)) does not call it yet; wire it there, then check that every
  detector's pad is at least its window.
- ⬜ The size of the seam-merge effect on `assessment_cossart.json` is measured after the
  re-import, and the transfer README says whether any of its numbers moved.
- ⬜ locust's painter floors frame-aligned onsets one frame early
  ([todo](2026-11-14-locust-repaint-floors-frame-aligned-onsets-one-early.md)). Fix that
  before comparing locust with CICADA on this corpus.
