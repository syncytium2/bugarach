# The export folder — bugarach's input contract

**This is the whole input.** bugarach reads one folder and nothing else: no data
store, no archive, no environment variable, no network, no companion database. If
a fact is not in the folder, bugarach does not know it and does not guess it.

Everything is CSV, UTF-8, newline-only endings, one header row. Times are
**seconds** on the recording's own clock. Any producer can write these files —
this project's MATLAB exporter, another lab's Python, a spreadsheet exported by
hand.

## Files

Only `events.csv` is required.

### `events.csv` — required

One row per detected event, in one ROI.

| column | type | meaning |
|---|---|---|
| `slice_id` | text | which recording. Any string; it is an identifier, not a format. |
| `stream` | text | which signal the event came from. Any name. A single-stream lab may omit the column entirely — every event is then one unnamed stream. |
| `roi` | text | which cell. Any string, unique within a slice. |
| `time_sec` | number | when the event began, in seconds. |

Nothing else is read. **Event properties — amplitude, width, rise time — belong to
a different project and are not consumed here.** The six detectors need onset times
and nothing more. Extra columns are ignored rather than rejected, so a producer may
ship one file that serves several consumers.

### `regions.csv` — optional

One row per region of a recording. **This is how a recording says it has periods.**

| column | type | meaning |
|---|---|---|
| `slice_id` | text | which recording |
| `region_idx` | integer | **1-based, chronological.** This is the ordering, and the only ordering. |
| `label` | text | **the treatment name** — `baseline`, `TTX`, `senktide`, `washout`, `pre-drug`, whatever the period actually was. |
| `start_sec` | number | window start |
| `end_sec` | number | window end |

**`label` is required whenever this file is present, and it must be the real
treatment name.** It is not decoration. Every figure axis, every legend, and every
row of the results is named by it — a region with no name yields a plot nobody can
read and a table nobody can group. Two things a producer must not do: send a
positional placeholder (`region 2`, `treatment 1`), and overwrite the first region's
real name with `baseline`. This project's own MATLAB exporter currently does the
second, discarding whatever the lab actually called that period.

**Five columns, and none of them derived.** A producer may want to send its
judgement that a window is long enough to analyse. It should not: that judgement is
`end_sec - start_sec` compared against a threshold, the duration is already in the
row, and the threshold is **policy, not fact** — one lab's floor is not another's.
Sending it would put two records of one quantity in the same file, which is exactly
what this contract avoids elsewhere by deriving the treatment index at write time
instead of storing it. Send the bounds; let whoever is deciding decide.

**Windows arrive already computed.** Whatever produced this folder decided where
each period begins and ends — trimming, caps, wash-in delays, exclusions. bugarach
uses the bounds as given and never adjusts them. That rule exists because the
windowing rule in this ecosystem has been reimplemented five times and has drifted
every time; there will not be a sixth implementation here.

**How this handles any number of treatments.** It carries no notion of a treatment
*slot*, so there is nothing to run out of. One region is a recording with no
protocol. Two is a before and an after. Six is a baseline and five conditions.
Ordering is `region_idx`; naming is `label`; neither is a controlled vocabulary and
neither is capped. A lab that runs a wash-in, three doses and a washout writes six
rows and changes nothing else.

**No region is privileged.** bugarach does not assume region 1 is a baseline, does
not treat any label as special, and does not decide which pair of regions is a
comparison. It reports every region separately and the contrast is chosen
downstream, by the person who knows the experiment.

**⚠ A label may be load-bearing upstream, even though it is inert here.** bugarach
interprets no label — but the producer that wrote the bounds may have. This
project's own MATLAB exporter decides a region's treatment by **substring match on
the label**: a name containing `hi` is taken to be a high-potassium condition and
is given raw, untrimmed bounds, while every other treatment gets a two-minute
wash-in delay and a twenty-minute cap. So `high K` and `elevated potassium`
describe the same experiment and produce different windows, and any label
containing those two letters — `chelerythrine`, `histamine`, `washin` — trips the
same rule.

The consequence for a producer: **renaming a region can silently change its
bounds.** The consequence for a reader: the label tells you what a period was
called, not that the bounds were computed the way a similar name elsewhere implies.
That is a reason to receive windows rather than derive them, not a reason to
re-derive them here.

**A label of `baseline` is not evidence of a baseline.** This project's exporter
overwrites the first region's real name with the literal string `baseline` on every
run, so a period the lab called `pre-drug`, `control` or `aCSF` arrives labelled
`baseline` and its original name is lost. Read such a label as *"whatever region 1
was called"*. A producer conforming to this spec should send the real name.

**When the file is absent**, the recording has one region spanning its own extent,
with `region_idx = 1` and **no label**. It is emitted as missing, never as
`baseline` — an unlabelled recording is one nobody has told us about, and calling
it a baseline manufactures a claim about a possibly-treated preparation.

### `slices.csv` — the sidecar

One row per recording. Identity, carried through — plus the one field bugarach
cannot work without.

| column | type | meaning |
|---|---|---|
| `slice_id` | text | the join key; must match `events.csv` |
| `frame_interval_sec` | number | the acquisition sampling interval, the mean time between imaged frames |
| *anything else* | text or number | **an open set** — `group_id`, `mouse_id`, `sex`, `age`, `cohort`, whatever the lab records |

**The interval comes from the sidecar. If it is not there, the app asks for it at
load, and will not proceed until it has one.** Three of the six detectors build
their analysis grid from it, so a wrong or guessed value silently changes what they
count. It is a property of the microscope, it cannot be recovered from onset times,
and it can only be told to us.

Asking is deliberate, and it replaces both a warning and a bare refusal. A warning
fires *after* the number exists — by then the trace is computed, the figure may be
drawn and the file may be on disk, and anyone whose rig genuinely runs at the
default learns to filter the warning away. A bare refusal is honest but useless: it
turns a lab away at the door over a number they know perfectly well. Asking is the
version that is both a gate and a way through. **There is no default**, because a
default here is a guess about somebody else's microscope.

A caller with no interface — a script, a batch run — supplies the value the same way
the prompt would, and gets the same refusal if it does not.

Everything else in this file bugarach **passes through to its output unchanged and
interprets not at all.** It does not know what a mouse is. Every column present
becomes a column in the results, so a statistician gets their own vocabulary back
rather than ours; absent columns are reported as missing, and a lab with no metadata
beyond the interval still gets a usable file.

### `metric_dictionary.csv` — optional

The column contract for the results, shipped alongside the batch so the folder
stays self-describing. When present, bugarach validates its output against it and
refuses to write a frame that does not conform. When absent, it writes the same
frame and says the check was skipped.

## What bugarach emits back

Into the same folder or one the user picks, from **one computation**. **One output
shape, carrying nothing specific to any lab** — including ours. Our own analysis
adapts to read this; it does not get a private dialect.

### `detections.csv` — one row per detected coordinated event

| column | meaning |
|---|---|
| `slice_id` · `stream` | which recording, which signal — the strings you sent |
| `detector` | which detector called it, by its plain name |
| `mode` | `threshold` or `peak` — how it was called, as a value rather than folded into the detector name |
| `region_idx` · `region_label` | which period it fell in — **your** index and **your** name, unchanged |
| `onset_sec` · `width_sec` | when it started and how long it lasted |
| `n_roi` | how many cells took part |
| `strength` · `strength_unit` | how strong, and **in what units** — because the six detectors do not measure strength in the same thing, the unit travels in the row rather than in a lookup table |
| *identity columns* | every column from `slices.csv`, carried through unchanged |

### `detector_settings.csv` — one row per parameter

`detector, stream, parameter, value`. Every setting each detector ran with, so a
result can be reproduced from the folder alone.

### What this deliberately does not do

- **No column means different things in different rows.** A single column holding a
  count for one detector and a dimensionless index for another cannot be read
  without a decoder, and a reader who lacks the decoder gets a plausible wrong
  answer rather than an error. Where the meaning varies, the unit is in the row.
- **No name has to be parsed.** Detector, stream and mode are their own columns.
  Nothing is packed into an identifier for a consumer to split apart later.
- **No privileged region, and no protocol vocabulary.** There is no "treatment
  index" and no reserved `baseline`; there is the index you sent and the name you
  gave it. A consumer that needs a baseline-versus-drug contrast picks the two rows
  it wants — it knows which they are and we do not.
- **No lookup file is required to read the output.** Every column is self-describing
  from its header and its unit column.

## The rules that make it universal

1. **One folder in, one folder out.** No path outside it is ever read.
2. **Only `events.csv` is required.** Every other file adds fidelity; none is a
   precondition. A folder holding one CSV of onset times is a valid input.
3. **No controlled vocabularies.** Stream names, region labels, ROI ids and slice
   ids are the lab's own strings. bugarach matches them, counts them, and hands
   them back.
4. **Nothing is inferred that was not given.** No window is derived, no region is
   assumed to be a baseline, no viability verdict is computed, no missing metadata
   is invented.
5. **Extra columns are ignored, not rejected**, so one file can serve several
   consumers.
6. **Missing is written as missing** — literally `NA`, never an empty field and
   never a plausible substitute.
