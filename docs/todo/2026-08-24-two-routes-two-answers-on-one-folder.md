---
status: open
filed: 2026-08-24
---

# Nobody has compared the browser run and `bugarach detect` on one folder

> **Revised 2026-08-24, the same day it was filed.** The first version led with a
> **52% gap** between two detection totals. That number is withdrawn from the summary,
> and the reason is in the first section: a sum of rows across detectors is not a
> quantity the two routes were ever constrained to preserve, so a difference between
> two such sums measures nothing. The comparison this file asks for is unchanged and
> is still the point of it. Anything quoting "52%" is quoting the withdrawn framing.

There are three ways to get a `detections.csv` out of bugarach — the browser page,
`bugarach detect`, and the Panel viewer's Save button. The promise underneath that
choice is that they are the same analysis wearing three interfaces. **No measurement
anywhere tests that**, and the README already names the hole in terms: *"What nothing
does is compare a browser run and a `bugarach detect` run on the same folder, row for
row."*

## Why the totals are not the measurement

Two runs over `2026-08-18_revised_2v_periods` (84 recordings, 84 of 84 conforming)
were reported on 2026-08-23, in different lanes, hours apart: the browser page over
the whole folder, fast + slow, **51,968** rows; `bugarach detect` at its default
`--stream`, fast + slow, **34,124**.

**Do not read a discrepancy off those two numbers.** A total is a sum over six
detectors of things that are not alike — one row per event per detector, no consensus
merging, by contract. It is dominated by whichever detector fires most, so one extra
detector in a roster moves it by tens of percent while every shared detector agrees
row for row; and two runs can match on the total while disagreeing everywhere
underneath. The totals are a tripwire at best, and a tripwire only fires honestly
when roster, stream and settings are pinned identical on both sides. **They were
not pinned**, which is the next section.

**Neither output file was kept.** There is no `detect/` directory under
`darkroom()/bugarach` and no `detections.csv` anywhere in it. So the two figures are
each lane's report of its own run and cannot be re-derived, re-grouped by detector,
or checked. That, and not the size of the gap, is what leaves the routes uncompared.

## What was different by default, and why nobody recorded which applied

The two routes do not ask the same question out of the box.

| | detectors | streams |
|---|---|---|
| browser page | **one** — `chosenDetectors()` returns `[whichDetector()]` unless "run several" is ticked; ticking it gives the three pre-checked, `rate`, `coact`, `loco` (`DET_DEFAULT_ON`, matching `bugarach.ui.app`'s `DEFAULT_ON`) | **one**, chosen at the door |
| `bugarach detect` | **all six** (`--detectors` default) | **every** stream (`--stream` default) |

And the browser's folder run only began honouring its tick-list on **2026-08-23**, in
`a12a11f` (PR #268) — before that it ran `Object.keys(DETECTORS)` regardless of what
was ticked. Both figures above were measured that day. **Which side of that change
each one falls on is not recorded**, so the roster behind each number is unknown.

## What is not known

**Whether the routes agree, and if not where.** Nothing scores either output against
truth either — a real recording has no answer key, which is the whole reason the
simulated benchmark exists. Candidate sources of a real divergence, none tested:

- **detector roster** — see above;
- **windowing** — `check` and `detect` settled on one resolver (#246); the browser has
  its own `analysisSegments`;
- **region tagging** — `detect` maps its `"none"` sentinel to `NA` and reported 305
  such rows, where the browser may drop or keep them differently;
- **episode merging or per-stream duplication**;
- **detector settings**, since the browser only began writing `detector_settings.csv`
  in #262.

## What would settle it

Run both routes on one folder with the **same detectors, the same stream, and the same
settings file**, keep both output files, and diff by
`(slice_id, detector, stream, onset_sec)`. The pieces exist:
`bugarach.emit.read_detections` reads either file, and #262 made the browser write a
settings file the CLI can be pointed at.

**The deliverable is a per-detector table** — agreed, browser-only, CLI-only, for each
detector and stream — **plus the first rows where they part and which side is missing
them.** A grand total is not a row in it.

⚠ Until that runs, a claim of the form *"the app produces the detections for this
folder"* is not supported. *"The app produces a detections file"* is.

## Why this is worth a file rather than a line

`detect_folder.py` and the browser deliberately share a scorer, an output contract and
now a windowing resolver, precisely so the picture and the file cannot drift. The
comparison above is the measurement that would say whether that worked. The reason it
has never been made is structural: every lane checked its own route against its own
previous run, and the boundary between them belonged to nobody.
