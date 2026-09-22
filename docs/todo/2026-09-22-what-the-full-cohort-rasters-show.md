---
status: open
filed: 2026-09-22
priority: medium — nothing is wrong with a number; three conventions differ and one axis is unlabelled
supersedes: 2026-09-22-coactdetect-onsets-are-bin-edges.md
---

# What the full-cohort rasters actually show: three onset conventions, and an axis with no origin

Tony, 2026-09-22, on the DI senktide raster pages in
`<darkroom>/bugarach/2026-09-21-full-cohort-default/rasters/`: the detections do not line up with
the events, and they do not line up consistently with each other. Investigated against the run's
own files. **Everything below is measured, and it replaces an earlier guess that was wrong** —
see "What this corrects".

## The run

`detect_coact_and_chorus/detector_settings.csv`: CoactDetect ran **sliding**, `int_win_sec` 2.0,
`merge_gap_sec` 8.0, `guard_sec` 1.0, `alpha` 1e-5, `onset_field` **t50rise** — goal 1's
every-knob values from `weekend_settings.csv`, not the binned points `bench.OPERATING_POINTS`
still ships. `chorus_gain_norm` is the net, decoding at `dt_sec` 0.1 with threshold 0.9716.
`raster_panel` draws `stream.t50rise`, so the raster and CoactDetect use the same field and
there is no anchor offset between the dots and that lane.

## Measurement 1 — where each detector's onset sits relative to its own member events

`onset_sec − core_first_sec` from `detect/calls_measured.csv`, senktide, four DI recordings:

| detector | stream | median | p10 → p90 | within 0.1 s of a member event |
|---|---|---|---|---|
| coact | fast | **0.00** | −1.40 → 0.00 | 48/77 |
| coact | slow | **0.00** | 0.00 → +1.30 | 108/127 |
| loco | fast | 0.00 | −0.70 → 0.00 | 90/106 |
| sync | fast | 0.00 | −0.10 → +0.70 | 67/109 |
| rate | fast | −0.60 | −0.90 → −0.10 | 9/88 |
| **cicada** (locust) | fast | **+0.50** | +0.20 → +0.80 | 8/150 |
| **cicada** (locust) | slow | **+1.10** | +0.40 → +3.00 | **2/271** |
| **sce** | fast | **−3.50** | −7.50 → −0.60 | **1/77** |
| **sce** | slow | −2.20 | −5.90 → +1.70 | 3/95 |

**CoactDetect, LoCo and SPIKE-synch sit on events.** Coact's one-sided fast tail (p10 −1.4 s) is
the sliding path's own lookback: `span_of(ev, starts[first] − int_win_sec, ends[last])` anchors on
the first onset in a window opening 2 s early, so a minority of calls anchor on a bystander event.

**Two detectors genuinely float, and neither is in the figure that prompted this.** Binned SCE is
a **bin edge** — `bin_width_sec` 10.0, and the offsets sit inside that bin. Locust is **peak
versus half-rise**: the export spec puts that gap at about 0.3 s fast and 2 s slow, and the
measurement gives +0.5 and +1.1 with a p90 of +3.0 on slow. Any page drawing those two lanes
shows marks that are genuinely beside the events, for two different and both explicable reasons.

## Measurement 2 — coact against chorus, on the page's own window

**The x-axis is minutes from senktide onset, not absolute recording time** (Tony). Re-read that
way, the drawn marks match `detections.csv` exactly — `20260130_272`'s fast lane is 7.18, 10.45,
10.80, 12.25, 13.06 screen-minutes, which is the five teal marks on the page.

| panel | stream | coact | chorus | coact calls with a chorus call within 1 s | median offset |
|---|---|---|---|---|---|
| 20250926_237 | fast | 10 | 9 | 9/10 | −0.40 s |
| 20250926_237 | slow | 14 | 17 | 13/14 | −0.15 s |
| 20260130_270 | fast | 11 | 14 | 7/11 | +0.40 s |
| 20260130_270 | slow | 12 | **19** | 10/12 | +0.30 s |
| 20260130_272 | fast | 5 | 2 | 2/5 | +1.00 s |
| 20260130_272 | slow | 10 | 8 | 8/10 | −0.15 s |

**Where both fire they agree to a few tenths of a second** — sub-pixel at that zoom, about 0.34 s
per pixel. What reads as inconsistency is **chorus firing where coact does not**: 19 calls against
12 on `20260130_270` slow. The unpaired grey ticks have no teal partner because CoactDetect did
not call those moments, which is a selection difference between a net and a coded detector, not a
drawing or timing defect.

## What this corrects

[`2026-09-22-coactdetect-onsets-are-bin-edges.md`](2026-09-22-coactdetect-onsets-are-bin-edges.md)
(#728) said CoactDetect's onsets are bin edges and that this explained the figure. **The mechanism
is real but belongs to binned SCE**; CoactDetect ran sliding in this run and its onsets sit on
events. Three further readings of the figure were wrong and are recorded here so nobody repeats
them: that the first screengrab was the whole recording (it was a zoom), that `20250926_235`
rendered empty (its calls were outside that zoom window), and that the drawn marks did not match
the file (they do, once the axis is read as senktide-relative).

## What is worth doing

1. **Label the axis origin** on these pages — "minutes from senktide onset", with a zero tick. An
   unlabelled relative axis produced three wrong readings in twenty minutes from someone reading
   carefully. Convention: every number carries its unit, and an origin is part of the unit.
2. **Draw unpaired calls differently from paired ones**, or the eye reads a missing partner as a
   misalignment.
3. **Decide whether the emitted onset should be the detector's own or the call measure's.** #698
   gave width and amplitude one definition across detectors, taken from the member events; the
   onset never got the same treatment, which is why SCE and locust land where they do. This is
   also what the fireflies contract proposal asks for, so the two are one change.
4. **Nothing here blocks a result.** No number moves; three conventions differ and a page is
   ambiguous about its own time axis.
