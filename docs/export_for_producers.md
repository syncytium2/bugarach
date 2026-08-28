# Writing an export folder — a page for the producer

**bugarach reads one folder. Write these files and you are done.**

This is the short version, addressed to whoever writes the exporter. The full
contract — every optional column, every reason — is
[`export_folder_spec.html`](export_folder_spec.html), rendered beside this page so the
link works wherever you are reading it. Nothing here contradicts it.

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
| `peak_sec` | **strongly asked for** | when the transient peaked. Not required — but the browser viewer's locust cannot run without it, or without a `width_sec` whose rule reaches it. See §4. |
| `amp` | no | how large it was, in your units. Send it if you have it. |

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
| `analysis_start_sec`, `analysis_end_sec` | optional — **usually leave them out** | the part of it worth scoring |

**Send the raw periods. Leave the analysis pair out unless you specifically mean it** —
and if you leave it out, omit the columns rather than writing `NA` or `NaN` in them. A
non-finite bound is refused with a named error rather than scored, but the refusal comes
from the detector rather than the loader, so you see it at `bugarach check` or at run
time and not at import.

An earlier version of this page said "if you have both, send both". interface2 pushed
back and was right. Two reasons, and the second is the one that bites:

- **An analysis window is a named paradigm, not a rule.** Two columns express exactly one
  at a time and cannot say which, so a folder that pins one has quietly chosen the
  analysis on the consumer's behalf. Raw periods keep every paradigm reachable from a
  single export.
- **Supplying it switches a check off.** The raw bounds are validated — baseline starting
  at zero, regions contiguous — and supplying `analysis_*` short-circuits that validation.
  The same corrupted folder passes clean *with* the columns and is caught *without* them.
  So sending an analysis window costs you the structural gate on the raw one.

If you do have a window worth stating, send it **and** keep the raw bounds correct — the
check you give up is exactly the one that would have caught them being wrong.

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

## 4. `width_sec` is kept, and the rule you pick decides what it does

> ⚠ **This section said the opposite until 2026-08-28. If you read it before then, read
> it again.** It told you the `width_sec` you send was "read from the file and discarded".
> That stopped being true on 2026-08-23 and the page did not catch up. If it persuaded
> you to stop sending the column, or not to start, that was our error — the column is
> worth sending, and one of the checks below can now reject a folder that used to load.

Width is not one quantity. A fast transient and a slow one are not the same shape, so
"how long it lasted" is not the same measurement, and **we do not define it for you.** Pick
a rule, apply it consistently within a stream, and name it in `width_def`.

**Two things can now reject a file that used to load.** A `width_sec` with no `width_def`
on the same row is an error naming the file and line. Two different `width_def` values
inside one stream are an error naming the recording. Either one stops the whole folder
loading in `bugarach check` and `bugarach detect` — the browser viewer is more permissive
and will load the file anyway, so **run the folder check, not the viewer, to find these**.
If you have been sending width without the rule beside it, add the rule before your next
export.

**Two spellings, and only two, let your width stand in for a `peak_sec` you did not
send** — `t50rise_to_peak` and `rise_interval_peak_minus_t50rise`. We match the exact
string, case and all (we do trim surrounding whitespace); we do not work out what your
rule means. A width that genuinely runs from the
half-rise to the peak under any other name derives nothing and warns about nothing. If
you send `peak_sec`, none of this applies and your peak is the one we keep. **If your
spelling differs, tell us and we will add it** — that is a conversation, not a rename on
your side.

**What you get for sending it.** Your width becomes the *active duration* in locust, our
coincidence detector (it appears as `cicada` in the `detector` column of our output) —
how long each event keeps its cell counted as active, and so how far apart two cells'
events can be and still land in the same window. What that is worth depends on which of
our two readers opens your folder, and the honest answer is different for each:

- **The browser viewer runs per-event by default, and its locust will not run at all on
  a recording with no peak.** A `peak_sec`, or a `width_sec` whose `width_def` is one of
  the two names above, are the only two ways to give it one. For that reader your width
  is the difference between a detector that runs and one that declines — it says so in
  its own refusal message. **Send `peak_sec` but no `width_sec` and that default turns
  every event into a one-frame active duration**, which floods the page with single-cell
  "events" and explains itself nowhere. Sending the width is the fix.
- **Our Python commands use a fixed duration.** `bugarach detect` and `bugarach view`
  do not run per-event, so sending width changes no number they currently produce.

We are spelling out both because an earlier draft of this correction said only the second
and would have told you your width did nothing.

`bugarach check` will name the width rules your folder carries, and say which streams
carry none — or, if none of them do, that none of them do.

**Because it becomes a coincidence unit, some rules break at that scale.** On this
project's own slow stream, `fwhm` *would* have run to a median of **4.7 s** and a maximum
of **186.9 s** — which is why the rule actually shipped there is
`rise_interval_peak_minus_t50rise`, whose maximum is 5.5 s. A 187-second "event duration"
is not a coincidence unit; it makes one cell overlap essentially everything. Rules that
behave: `t50rise_to_peak`, `above_threshold`, anything bounded by the event's rise rather
than its decay. `fwhm` is reasonable on a fast stream and wrong on a slow one, which is
exactly why the definition is per stream.

If the natural output of your pipeline is a decay-dominated width, send it and say so in
`width_def` — the string is what lets a consumer notice the scale before using it rather
than after.

---

# Check it before you send it

```
bugarach check my_export/
```

Exits 0 if the folder conforms, 1 if it does not, so it drops straight into a build.
It reads the folder with **the same loader the analysis uses** — a pass means the
analysis will read what you meant, not that a second implementation agreed with the
first.

Real output, from the current export (`2026-08-18_revised_2v_periods`):

```
84 recording(s), 84 conforming

  ok   20240708_13      34 ROI (0 with no events)    4494 events  streams fast+slow  dt 0.1  windows baseline, SB222200
       · no ROI declared with no events. If every one of the 34 ROIs fired, this is right; if some were quiet, they are missing from the population and every per-ROI figure is too high (write them as time_sec = NA)

CONFORMING
Lines marked · read fine and may still not be what you meant.
```

**Errors name the file and the line.** Lines beginning `·` are notes — legal, but worth a
look.

**The silent-ROI note is noisier than it should be**, and it is worth saying so rather
than letting you learn to skip it: it fires on **59 of the 84** recordings in the current
export, because in most of them every ROI really did fire at least once across the whole
recording. A note that fires on 70% of a folder trains the reader to ignore it, which is
the opposite of its purpose. It is asking you to confirm, not reporting a fault, and
sharpening it is on our side rather than yours.

The current export passes: 84 of 84 conforming, ROI counts matching `n_roi_recorded` on
**all 84**.

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
