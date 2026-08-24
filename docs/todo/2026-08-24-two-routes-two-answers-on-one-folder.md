---
status: open
filed: 2026-08-24
---

# Two routes, two answers, one folder — and a 52% gap between them

There are three ways to get a `detections.csv` out of bugarach. On the same export
folder, two of them disagree by half.

| route | streams | detections | source |
|---|---|---|---|
| browser page, whole folder | fast + slow | **51,968** | the folder run behind `analyseFolder` |
| `bugarach detect` (default `--stream`) | fast + slow | **34,124** | `src/bugarach/detect_folder.py` |

Folder: `2026-08-18_revised_2v_periods`, 84 recordings, 84 of 84 conforming. Both
figures were measured on 2026-08-23, in different lanes, hours apart.

## Why nobody saw it

Each lane measured its own route and reported honestly. The numbers were never put
next to each other, and one comparison that *was* made looked like agreement:

- browser, **fast only** — 33,689 rows
- `bugarach detect`, **both streams** — 34,124 detections

1.3% apart. Read quickly, that is two routes corroborating each other. It is two
different quantities. `bugarach detect --stream` defaults to **every** stream; the
browser analyzes one at a time and needs a second run for the other. Comparing the
like-for-like totals is what opens the gap to 52%.

The README already names this hole in terms: *"What nothing does is compare a
browser run and a `bugarach detect` run on the same folder, row for row."*

## What is not yet known

**Which one is right, or whether either is.** Nothing here scores either output
against truth — a real recording has no answer key, which is the whole reason the
simulated benchmark exists. The gap could be any of:

- **a detector roster difference** — the browser's folder run honors its tick-list
  as of #268, so a run with fewer detectors selected produces fewer rows, and the
  default changed from six to one in that same PR;
- **a windowing difference** — the two settled on one resolver for `check` and
  `detect` (#246), and the browser has its own `analysisSegments`;
- **a region-tagging difference** — `detect` maps its `"none"` sentinel to `NA` and
  reported 305 such rows, where the browser may drop or keep them differently;
- **an episode-merging or per-stream duplication difference**;
- **or simply two different detector settings**, since the browser only began
  writing `detector_settings.csv` in #262.

Each is cheap to test and none has been tested.

## What would settle it

Run both routes on one folder with the **same six detectors, the same streams, and
the same settings file**, and diff the two `detections.csv` files by
`(slice_id, detector, stream, onset_sec)`. The pieces all exist now:
`bugarach.emit.read_detections` reads either file, and #262 made the browser write
a settings file the CLI can be pointed at. The output worth having is not "the
totals match" but **the first ten rows where they do not**, and which side is
missing them.

⚠ Until that runs, a claim of the form *"the app produces the detections for this
folder"* is not supported. *"The app produces a detections file"* is.

## Why this is worth a file rather than a line

The three routes exist so a lab can choose between clicking, scripting, and a local
viewer — and the promise underneath that choice is that they are the same analysis
wearing three interfaces. `detect_folder.py` and the browser deliberately share a
scorer, an output contract and now a windowing resolver, precisely so the picture
and the file cannot drift. This is the measurement that would have caught it if it
had ever been made, and the reason it was not is structural: every lane checked its
own route against its own previous run, and the boundary between them belonged to
nobody.
