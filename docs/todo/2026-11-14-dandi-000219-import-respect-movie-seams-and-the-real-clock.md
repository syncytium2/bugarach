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

- `import_dandi.py` splits runs at movie seams, and the export keeps the real time of each
  event alongside or instead of the spliced one. Which of those two is a contract question
  ([`export_folder_spec.md`](../export_folder_spec.md)): `time_sec` is defined as a time on
  the recording's clock.
- Detection on this corpus runs on spliced time and reports in real time.
- The size of the seam-merge effect on `assessment_cossart.json` is measured, and the
  transfer README says whether any of its numbers moved.

A seam-aware adapter (`movies()`, `runs()`, `to_real()`) has already been written outside
this repository. It repaints the published raster bit for bit on four sessions. Ask Tony for
it before writing a new one.
