# Writing an export folder — a page for the producer

**bugarach reads one folder. Write these files and you are done.**

This is the short version, addressed to whoever writes the exporter. The full
contract — every optional column, every reason — is
[`export_folder_spec.md`](export_folder_spec.md). Nothing here contradicts it.

---

## The folder

```
my_export/
  20240708_13.csv     one file per recording, named by its id
  20240708_17.csv
  ...
  slices.csv          one row per recording — the frame interval, plus identity
  regions.csv         one row per treatment period
```

Everything is CSV, UTF-8, one header row. **All times are seconds** on the
recording's own clock. Extra columns are ignored, never rejected, so one file can
serve several consumers.

The file's name is the recording's id. Nothing parses it further.

## `<slice_id>.csv` — one row per event

| column | required | what it is |
|---|---|---|
| `roi` | **yes** | which ROI. Any string, used consistently, unique within the recording. |
| `time_sec` | **yes** | when the event reached **half its rise** — or `NA`, see below |
| `stream` | no | `fast`, `slow`, whatever you call them. Omit if you have one stream. |
| `width_sec` | *asked for* | how long the event lasted |
| `width_def` | with `width_sec` | the name of **your** rule for width |
| `peak_sec`, `amp` | no | send them if you have them |

## `slices.csv`

| column | required | what it is |
|---|---|---|
| `slice_id` | **yes** | matches the recording's file name |
| `frame_interval_sec` | **yes** | seconds between imaged frames |
| `group_id` | reserved | which experimental group |
| `subject_id` | reserved | which animal — recordings sharing one are **not** independent. `mouse_id` and `animal_id` are read as this, so keep whichever you already write. |
| anything else | — | carried through to the results untouched |

Without `frame_interval_sec` the app stops and asks. There is no default, because a
default here is a guess about your microscope.

## `regions.csv`

| column | required | what it is |
|---|---|---|
| `slice_id` | **yes** | which recording |
| `region_idx` | **yes** | 1-based, chronological |
| `label` | **yes** | `baseline`, `TTX`, `senktide`, `washout` — what the period was |
| `start_sec`, `end_sec` | **yes** | when it began and ended, **raw** |
| `analysis_start_sec`, `analysis_end_sec` | optional | the part of it worth scoring |

If you have both, send both. The raw pair says what happened; the analysis pair says
what to measure, and it is the one that gets used.

---

# The four things that actually go wrong

Everything above is mechanical. These four are where a folder that loads cleanly
still produces a wrong answer, and all four have happened.

## 1. `time_sec` is the half-rise, not the peak

The moment the transient reached **half its rise** — not the peak, not the first
sample over threshold.

It has to be named because your pipeline probably has several candidates and they are
far apart: in this project's own data the peak lags the half-rise by about **0.3 s in
a fast stream and 2 s in a slow one**. Two seconds is wider than the window
coincidence is judged in, so sending peaks where onsets were meant does not shift the
answer slightly — it **changes which events are found to coincide**, and nothing
anywhere fails.

If your signal has no meaningful half-rise, send the closest thing and say so in your
own documentation.

## 2. An ROI that fired nothing still needs a row

```
roi,time_sec
7,NA
```

That says *ROI 7 was recorded and produced no events*. An empty field means the same.

One row per event means a silent ROI otherwise has **no rows at all**, and absent is
indistinguishable from never-imaged — so it drops out of the population. Every
per-ROI rate divides by that population: five ROIs recorded with two silent, counted
over three, comes out **1.67× too high**. The error is worst in the quietest
recordings, which is exactly where quiet is the result.

`rate == 0` is a measurement. Omitting silent ROIs picks the denominator on the
analyst's behalf and nothing downstream can tell.

**And it is per (roi, stream), not per roi** — which is the part that is easy to miss
and which your exporter already gets right. From `20240726_34` in the current export:

```
roi,time_sec,stream
10,NA,fast          <- ROI 10 was recorded and fired nothing in the FAST stream
10,612.35,slow         ... while firing four times in the slow one
```

ROIs 10 and 16 each have four slow events and no fast ones, and each carries an `NA`
row naming the fast stream. That is exactly right: a fast-stream analysis needs them
in its population with a rate of zero. An ROI silent in *both* streams needs a row for
each.

## 3. Export what should be analysed — the selection is yours

**Send the recordings and ROIs you consider analysable, and only those.** A recording
you have withdrawn is simply absent from the folder. A dead ROI is not exported.
There is no exclusion flag, no quality column, no `keep` field — and there will not
be one.

That judgement is yours because you have evidence the analysis does not. **When the
analysis has tried to make it instead, it got it wrong.** In August 2026 an analysis
here read the raw store, found it therefore contained recordings the lab had
withdrawn, and re-derived the exclusions from the lab's workbook. That workbook keys
them on (date, mouse, **slice order**); the analysis had no slice order, matched on
date, and **dropped a recording the lab had not withdrawn** — one mouse had two
slices that day and only the first was excluded. Your export had it right. Every
published number was then computed over one recording fewer than intended.

If a folder looks like it holds something it should not, that is a conversation with
you — not a filter on our side.

## 4. `width_def` names your rule, and we never parse it

Width is not one quantity. A fast transient and a slow one are not the same shape, so
"how long it lasted" is not the same measurement.

**We do not define width and will not infer it.** Pick the rule, apply it
consistently within a stream, and name it: `t50rise_to_peak`, `fwhm`,
`above_threshold` — whatever you actually computed. We carry the string and never
read it.

A column meaning two things without saying which yields a plausible wrong answer
rather than an error.

---

# Check it before you send it

```
bugarach check my_export/
```

Exits 0 if the folder conforms, 1 if it does not, so it drops straight into a build.
It reads the folder with **the same loader the analysis uses** — a pass means the
analysis will read what you meant, not that a second implementation agreed with the
first.

Real output, from the current export:

```
export folder: .../exports/bugarach/2026-08-17_revised_2v_v2
84 recording(s), 84 conforming

  ok   20240708_13      34 ROI (0 with no events)    4494 events  streams fast+slow  dt 0.1  windows baseline, SB222200
       · analysis windows supplied — scored as given, and this project's wash-in delay and caps are not applied
       · no ROI declared with no events. If every one of the 34 ROIs fired, this is right; if some were quiet, they are missing from the population and every per-ROI figure is too high (write them as time_sec = NA)
```

**Errors name the file and the line.** Lines beginning `·` are notes — legal, but worth
a look. The silent-ROI note above fires on any recording where every ROI fired at least
once, which is often simply true; it is asking you to confirm, not reporting a fault.
The current export passes: 84 of 84 conforming, and the ROI counts match
`n_roi_recorded` on every recording checked.

---

# A complete tiny example

`my_export/rec_1.csv`
```
roi,time_sec,stream,width_sec,width_def
1,12.40,fast,0.32,t50rise_to_peak
1,88.10,fast,0.29,t50rise_to_peak
2,12.55,fast,0.35,t50rise_to_peak
3,NA,fast,,
```

`my_export/slices.csv`
```
slice_id,frame_interval_sec,group_id,mouse_id
rec_1,0.05,control,m17
```

`my_export/regions.csv`
```
slice_id,region_idx,label,start_sec,end_sec,analysis_start_sec,analysis_end_sec
rec_1,1,baseline,0,600,60,600
rec_1,2,TTX,600,1200,660,1200
```

Three ROIs, one of which was silent and says so. One stream. Widths with the rule
named. A baseline and a drug period, each with the first minute trimmed off for
analysis but the raw bounds still recorded.

**This example is checked, not illustrative.** Written to disk exactly as above and
run through the validator:

```
1 recording(s), 1 conforming

  ok   rec_1     3 ROI (1 with no events)       3 events  streams fast  dt 0.05  windows baseline, TTX
       · analysis windows supplied — scored as given, and this project's wash-in delay and caps are not applied

CONFORMING
```

That is the whole contract.
