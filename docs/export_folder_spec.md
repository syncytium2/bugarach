# The export folder — bugarach's input contract

**bugarach needs three facts:** the event times of each ROI, the timing of each
treatment period, and the acquisition frame interval. Nothing here is specific to a
lab, a preparation, a drug or a pipeline. A producer that can state those three is a
conforming producer.

**A fourth is asked for and not required:** how big each event was. A producer that
can state it should; one that cannot is still conforming, and every detector still
runs. What it buys is in revision 5 below.

**This is the whole input.** bugarach reads one folder and nothing else: no data
store, no archive, no environment variable, no network, no companion database. If
a fact is not in the folder, bugarach does not know it and does not guess it.

**And the folder is the corpus.** Every recording in it is to be analysed; a
recording that should not be analysed is not in it. Deciding which is the
producer's, made before the folder is written, from records bugarach has never
seen and must never look for. See revision 6.

Everything is CSV, UTF-8, newline-only endings, one header row. Times are
**seconds** on the recording's own clock. Any producer can write these files —
this project's MATLAB exporter, another lab's Python, a spreadsheet exported by
hand.

> **Revision 6** (2026-08-20). **Selection is the producer's, and the consumer may
> not second-guess it.**
>
> "bugarach reads one folder and nothing else" was stated from revision 1 and was
> read as a *convenience* — the folder is enough — rather than as the *rule* it is.
> It is the rule. **Which recordings are analysable, and which ROIs are alive, are
> expressed by what the folder contains.** A recording the producer withdrew is
> absent. A dead ROI is not exported. There is nothing for the consumer to filter,
> and filtering anyway is a defect rather than a precaution.
>
> **The incident.** An analysis in this repo read the `.mat` store directly, noticed
> it therefore contained recordings the lab had withdrawn, and "fixed" that by
> reading the lab's workbook to re-derive the exclusions. The workbook keys them on
> (date, mouse, **`slice_order`**). bugarach has no `slice_order`, so it matched on
> date and dropped **a recording the lab had not withdrawn** — one mouse had two
> slices that day and only the first was excluded. The producer's export had it
> right. Every number in a published report was then computed over a corpus one
> recording smaller than the producer intended, by machinery built to be careful.
>
> **The generalisation.** A consumer re-deriving a producer's decision is working
> from strictly less information than the producer had. It will sometimes agree, and
> when it disagrees it will be wrong. If a folder looks like it contains something it
> should not, that is a **conversation with the producer**, not a filter in the
> consumer. `bugarach.assembly` carries the same note where the deleted code was.

> **Revision 5** (2026-08-18). **An event is located at its half-rise, and the
> contract now asks how big it was.**
>
> `time_sec` is the **`t50rise`** — the time the transient reached half its rise.
> Rev 1–4 said only "when the event began", which is the same thing said loosely, and
> loosely was not enough: a store can hold both an onset and a peak, and they are not
> close together — in **this project's own** stores the gap is roughly 0.3 s in a fast
> stream and 2 s in a slow one. Another producer's gap will differ; that it exists at
> all is the point. A producer reading "when it began" had no way to know which was
> wanted. One rule, named, for every stream and every producer.
>
> `width_sec` is **new, optional, and requested.** With it, `amp` and `peak_sec` may
> also be sent. **`width` is not one quantity** — it is defined differently for a
> fast event than for a slow one, and defining it is the **producer's**
> responsibility, not bugarach's. For this project's own exporter that is
> interface2's call to make and to document; for anyone else it is theirs. So width
> travels with a `width_def` naming the rule that produced it, exactly as `strength`
> travels with `strength_unit` in the output — for the same reason, which is that a
> column meaning two things without saying so yields a plausible wrong answer rather
> than an error.
>
> **Why ask at all.** A coordinated event is currently described by how many cells
> took part and how long the coordination lasted. Nothing says how big the events
> *making it up* were — whether a coordinated event is many small transients or a few
> large ones, and whether that changes under a treatment. That question cannot be
> asked of onset times alone, and it is the reason this revision exists.
>
> ⚠ **Nothing in bugarach reads `width_sec` today** — not the loader, not the folder
> check, not any detector. It is not validated, not carried through, and no result
> changes by supplying it; it is an extra column like any other until code is written
> for it. This is a
> contract to build against, stated ahead of the code on purpose so producers can
> begin emitting it — the same posture FOUNDATIONS §4 takes for the folder reader,
> and it is written down here so nobody mistakes the column for a feature.
>
> **Revision 4** (2026-08-18). **Group and subject are named, not merely allowed.**
> `slices.csv` reserves `group_id` (which experimental group this recording belongs
> to) and `subject_id` (which animal it came from). Both were already legal as
> free-form identity columns; naming them is what lets an analysis *split by group*
> and *stop counting two slices from one animal as two independent observations*.
> A producer already writing `mouse_id` or `animal_id` is conforming and need change
> nothing — those spellings are read as `subject_id`. Both columns stay optional.
>
> This revision also narrows one sentence that was too broad. Rev 1–3 said bugarach
> "interprets not at all" and "does not know what a mouse is". That is right about
> **values** and was wrong about **roles**: an app that may not know which column
> says two recordings share an animal cannot produce a group-split result, which
> FOUNDATIONS §9 requires before a corpus number is admissible. bugarach still never
> interprets a *value* — `DI`, `ORX`, `wildtype`, `cohort-B` mean nothing to it — but
> it now knows which column plays which *role*. Written after an analysis went to a
> spreadsheet outside the folder for group membership that `slices.csv` was already
> carrying.
>
> **Revision 3** (2026-08-17). `regions.csv` gains optional
> `analysis_start_sec` / `analysis_end_sec`: a region now states what happened AND
> what to score, so a producer with its own windowing policy is honoured instead of
> re-windowed. Rev 2's instruction to send raw bounds still holds — that is what
> `start_sec` / `end_sec` are — and the paragraph below records why sending analysis
> windows in their place halted 83 of 85 recordings.
>
> **Revision 2** (2026-08-17). **One file per recording**, rather than one table
> holding every recording. A lab's pipeline runs per recording and writes per
> recording, so a batch table made them concatenate before they could start.
> `slices.csv` and `regions.csv` stay, as the two small tables a lab keeps like a
> notebook: one row per recording, one row per window. And an ROI that was imaged
> and fired nothing is now expressible — one row with no time — which rev 1 could
> not say at all.

## The folder

```
my_export/
  20240708_13.csv     one recording — its ROIs and their event times
  20240708_17.csv
  20240723_22.csv
  ...
  slices.csv          one row per recording: the frame interval, plus identity
  regions.csv         one row per treatment window
```

**Every `.csv` is a recording except three reserved names**: `slices.csv` and
`regions.csv`, the two input tables shown above, and `metric_dictionary.csv` — not
shown, because it belongs to the *output* contract further down. It is reserved
anyway, so that shipping it alongside the input does not read as a recording called
"metric_dictionary".

The file's name is the recording's id — no column declares it and nothing parses
the name further. A folder of recording files and nothing else is a valid input;
each input table buys exactly one thing.

**A table that names a recording the folder does not hold is fine** — one batch
table may cover more recordings than any given folder. **The reverse is reported:**
if a table is present and has no row for a recording that *is* in the folder, that
recording silently gets nothing from it, which is almost always one typo in a
`slice_id`. bugarach warns and names the recordings it could not match.

### `<slice_id>.csv` — one per recording, at least one required

One row per detected event, in one ROI.

| column | type | required | meaning |
|---|---|---|---|
| `roi` | text | yes | which ROI. Any string; the same string on every row of that ROI, and used by no other ROI in the recording. |
| `time_sec` | number | yes | **when the event reached half its rise** (`t50rise`), in seconds — **or `NA`**, see below. |
| `stream` | text | no | which signal the event came from. Any name. A single-stream lab may omit the column entirely — every event is then one unnamed stream. |
| `width_sec` | number | **asked for** | how long the event lasted. See below — this is not one quantity. |
| `width_def` | text | with `width_sec` | the name of the rule that produced `width_sec`. Constant within a stream. |
| `peak_sec` | number | no | when the transient peaked, if the producer has it |
| `amp` | number | no | how large the transient was, in the producer's own units |

#### An event is located at its half-rise, and that is not a matter of taste

`time_sec` is the **`t50rise`**: the moment the transient reached half its rise.
Not the peak, not the first sample above threshold, not the midpoint.

It has to be named rather than described because a producer may have several
candidates and they are far apart. In this project's own stores the peak lags the
half-rise by roughly **0.3 s in a fast stream and 2 s in a slow one**. Two seconds is
wider than the tolerance a detection is scored at, so a producer that sent peaks
where onsets were meant would not merely shift the answer — it would change which
events were found to coincide, with nothing anywhere failing.

A producer whose signal has no meaningful half-rise sends the closest thing it has
and says so in its own documentation. One rule, applied consistently, beats each
producer choosing the field whose name it liked.

#### Width is not one quantity, and the producer defines it

A fast transient and a slow one are not the same shape, so "how long it lasted" is
not the same measurement. **bugarach does not define width and will not infer it.**
The producer chooses the rule, applies it consistently within a stream, and names it
in `width_def` — `t50rise_to_peak`, `fwhm`, `above_threshold`, whatever it actually
computed. The string is the producer's; bugarach carries it and never parses it.

This mirrors `strength_unit` in the output, and for the same reason: **a column that
means two things without saying which yields a plausible wrong answer rather than an
error.** A consumer comparing widths across streams must read `width_def` first, and
where the definitions differ the comparison is not available — which is a fact about
the measurement, not a gap in the file.

For this project's own exporter, defining fast and slow width is **interface2's**
responsibility and belongs in their documentation, not here.

#### Sending more than is asked for

Extra columns are ignored rather than rejected, so a producer may ship one file that
serves several consumers. A producer that already computes the full per-event set is
encouraged to send it — `amp`, `peak_sec`, `t50rise` (as `time_sec`) and `width_sec`
— because the questions those support are the ones nobody can ask today, and a folder
is cheaper to write once than to regenerate.

#### An ROI that fired nothing is a row with no time

`roi = 7`, `time_sec = NA` says *ROI 7 was recorded here and produced no event*. An
empty field means the same thing, because that is what a spreadsheet writes.

This is the only way to say it, and it has to be said. One row per event means a
silent ROI otherwise has no rows at all — and *absent* is indistinguishable from
*never imaged*, so the ROI drops out of the population. Every per-ROI quantity
divides by that population: five ROIs recorded with two quiet, counted over three,
comes out **1.67× too high**. The error is largest in the quietest recordings,
which is exactly where quiet is the result.

So `rate == 0` is a measurement, not a gap. bugarach reports the ROIs it was given
and never infers the ones it wasn't — a producer that omits its silent ROIs has
chosen the denominator on the analyst's behalf, and nothing downstream can tell.

**No verdict, no viability, no quality flag.** These files say which ROIs were
recorded and nothing about whether any of them was worth keeping. That judgement
belongs to the producer, who has evidence bugarach does not, and it is applied
before the folder is written. What arrives is simply the population the producer
chose.

### `regions.csv` — optional

One row per region of a recording. **This is how a recording says it has periods.**

| column | type | meaning |
|---|---|---|
| `slice_id` | text | which recording |
| `region_idx` | integer | **1-based, chronological.** This is the ordering, and the only ordering. |
| `label` | text | **the treatment name** — `baseline`, `TTX`, `senktide`, `washout`, `pre-drug`, whatever the period actually was. |
| `start_sec` | number | when the period **began** — raw, untrimmed |
| `end_sec` | number | when the period **ended** — raw, untrimmed |
| `analysis_start_sec` | number | *optional* — the part of it to **score** |
| `analysis_end_sec` | number | *optional* — as above |

### Two windows, because they answer different questions

`start_sec`/`end_sec` are **what happened**: the drug was on from here to here.
`analysis_start_sec`/`analysis_end_sec` are **what to score**, and they exist because
those are rarely the same thing — a wash-in delay before the drug reaches the tissue,
a cap so a long application does not outweigh a short one, a stretch dropped for a
reason only the producer knows.

**Send both when you have a windowing policy.** They are used exactly as given: no
delay, no cap, and no guard on where the baseline starts, because none of that is
bugarach's to apply to your protocol. The raw period travels alongside, so how much
was trimmed stays visible in the output rather than being absorbed into the number.

**Both bounds or neither, and all regions of a recording or none.** Half an analysis
window is a producer bug rather than a partial answer, and a recording scored half on
your windows and half on ours is two policies inside one number — both are refused
rather than guessed at.

**Used as given is not the same as unchecked.** Four things are refused, and they are
the ones that are wrong under anybody's protocol: a period that ends before it begins,
an analysis window that ends before it begins, an analysis start that is not a finite
time, and an analysis window falling outside the period it claims to be part of. That
last one means the two pairs contradict each other, and the file cannot say which of
them is right.

Nothing else about your bounds is judged. In particular a period beginning somewhere
other than 0 and a gap between two periods are both legal here, whatever this project's
own stores would make of them — a lab that started recording before it started
treating, or left the tissue alone between conditions, is describing its experiment
rather than making a mistake.

This paragraph is new because that path had no checks at all. Supplying these columns
routes a folder past the guards on the raw bounds, so the producer who states their
policy — the thing this contract asks for — was the one producer nothing validated. A
recording whose baseline began at 500 s with an 8,899 s gap after it and an analysis
window running `99999` to `-500` passed `bugarach check` and handed the detectors a
window of **−100,499 seconds**, which every detector downstream would have reported as
an absence of coordination. Found by interface2 on 2026-08-18, running our own gates
against a folder they broke on purpose.

**When they are absent, bugarach derives the analysis window itself**, applying this
project's convention: the baseline measured backward from its end with a 20-minute
cap, every non-high-K treatment starting 2 minutes late and capped at 20 minutes,
high K⁺ exempt from both. For this project that is correct and matches its own
analysis. For anybody else it is an assumption you did not make, which is the reason
these two columns exist —
[`docs/todo/2026-08-17-windowing-convention-is-not-optional.md`](todo/2026-08-17-windowing-convention-is-not-optional.md).

**This is not a derived column of the kind the section above refuses.** A duration
judgement is recomputable from the row and so does not belong in it; an analysis
window is not — it encodes a decision about the preparation that nothing in the file
implies. Send the bounds and the policy; keep the verdicts out.

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

**⚠ Send the RAW bounds, not analysis windows.** `start_sec` and `end_sec` are when
the period *began and ended* on the recording's clock: **region 1 starts at 0, and
each region starts where the previous one ended.** No trimming, no caps, no wash-in
delay, no gaps.

**This paragraph said the opposite until 2026-08-17, and it cost a whole export.** It
promised bugarach "uses the bounds as given and never adjusts them". It does not:
`region_windows` in `src/bugarach/detectors/loco.py` re-applies this project's
windowing convention — a backward cap on the baseline, a two-minute wash-in delay and
a cap on each treatment — and it **halts** on a baseline that does not begin at 0 or a
gap between regions, because in these stores either means a data defect.

So a producer who did the trimming, exactly as this text asked, shipped a folder that
loaded cleanly and then halted **83 of 85** recordings. That happened: interface2 read
this paragraph, sent pre-trimmed windows, and every detector refused them. `bugarach
check` now runs `region_windows` over every recording, so a folder that cannot be
analysed fails at the door rather than at the first detector.

The case for raw bounds is the one the old text made, pointing the other way: this
windowing rule has been reimplemented five times in this ecosystem and drifted every
time, so it is applied **once**, here, to bounds nobody has already adjusted. Two
consumers handed the same raw folder compute the same windows; two consumers handed
pre-trimmed folders get whatever each producer decided.

**⚠ If your lab has no wash-in and no cap, that convention is applied anyway**, and it
is not currently optional: a treatment window will start two minutes after your
`start_sec` and end twenty minutes later. For this project that is correct and matches
its own analysis. For anyone else it is an inherited assumption, and making it a
parameter is open work —
[`docs/todo/2026-08-17-windowing-convention-is-not-optional.md`](todo/2026-08-17-windowing-convention-is-not-optional.md).

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
| `slice_id` | text | the join key; must match a recording file's name |
| `frame_interval_sec` | number | the acquisition sampling interval, the mean time between imaged frames |
| `group_id` | text | **optional, reserved** — which experimental group this recording belongs to. The values are yours; bugarach only needs to know which column names the grouping |
| `subject_id` | text or number | **optional, reserved** — which animal this recording came from. Two recordings sharing one are siblings, never independent observations. `mouse_id` and `animal_id` are read as this |
| *anything else* | text or number | **an open set** — `sex`, `age`, `cohort`, `slice_loc`, whatever the lab records |

**Why those two are named when the rest are not.** Both are optional and neither is
interpreted, but each answers a question an analysis cannot answer for itself.
`group_id` says which comparison the study is about, so a result can be reported per
group instead of pooled across groups that may run in opposite directions.
`subject_id` says which recordings are siblings, so twenty slices from eight animals
are not counted as twenty independent observations. Without them a corpus number is
still computable and is quietly weaker than it looks — so when they are absent
bugarach says which claims it cannot support, rather than refusing the folder or
pretending it can.

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
interprets not at all.** Every column present becomes a column in the results, so a
statistician gets their own vocabulary back rather than ours; absent columns are
reported as missing, and a lab with no metadata beyond the interval still gets a
usable file.

**The line between a column's role and its values.** bugarach reads the *role* of
`group_id` and `subject_id` — which column groups, which column identifies the
animal — and never their *values*. It does not know what `ORX` means, what a mouse
is, or which group is a control. It knows only that rows sharing a `subject_id` came
from one animal and that rows differing in `group_id` belong to different groups.
Every other column, including the values in these two, is carried and not read.

### `metric_dictionary.csv` — optional

The column contract for the results, shipped alongside the batch so the folder
stays self-describing. When present, bugarach validates its output against it and
refuses to write a frame that does not conform. When absent, it writes the same
frame and says the check was skipped.

### What the producer says about the folder — optional, and expected

A folder can carry a prose statement about how it was made. Nothing reads it and
nothing validates it; it is written for the person deciding whether a number
computed from this folder means what they think it means. This project's exporter
writes `PROVENANCE.md`; the name is not part of the contract and any file that
says these things serves.

**What is worth stating, and why each earns its place:**

- **Which recordings were left out, and under what rule.** This is the one that
  makes a corpus checkable. "84 recordings" is unverifiable on its own — it cannot
  distinguish a complete export from one that lost twelve. Naming the rule and the
  count makes the same number auditable, and naming the recordings makes it
  reproducible.
- **What `width_sec` means in each stream**, where the producer sends it. The
  column travels with `width_def` per row, but a reader deciding whether two
  streams are comparable wants it in one place.
- **Known contamination.** A recording can be in the corpus and still have a
  defect the producer knows about and the consumer cannot see — motion artefacts
  pinning a trace, a period whose end is a clamp rather than a measurement. A
  consumer that cannot be told will discover it as a result.
- **What the identifiers mean.** Whether `roi` is a fresh numbering or the source
  store's index decides whether a gap in the ids is missing data or a removed cell.

**It is not a substitute for the CSVs.** Anything a detector needs is a column, in
the contract, validated. This is the part a machine cannot use and a person cannot
do without.

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

## Check it yourself

```
bugarach check my_export/
```

Exits 0 when the folder conforms and 1 when it does not, so it drops into a build.
It reads the folder with **the same loader the analysis uses**, so a pass means the
analysis will read what you meant — not that a second implementation agreed with
the first.

```
export folder: my_export
2 recording(s), 2 conforming

  ok   20240708_13     3 ROI (1 with no events)     3 events  streams fast+slow  dt 0.05  windows baseline, TTX
  ok   20240708_17     2 ROI (1 with no events)     1 events  streams events     dt 0.1   windows —
       · no treatment windows — analysed as one whole-recording window
```

Two kinds of line, and the difference between them is the point:

- **`!` is an error.** The folder cannot be read as written, and the message names
  the file and the line — a label in the `region_idx` column, a time that is not a
  time, a frame interval given as a frame *rate*.
- **`·` is a note.** It read fine and may not be what you meant. Notes never fail
  the check, because none of them is decidable from the folder alone. The one worth
  reading every time is **"no ROI declared with no events"**: if every ROI in that
  recording really did fire, ignore it — but if some were quiet, they are missing
  from the population, every per-ROI figure computed from it is too high, and
  nothing downstream can tell those two cases apart.

## Measure it, once it reads

```
bugarach assess my_export/
```

`check` answers *can this be read*. `assess` answers the next question: **how
coordinated are these recordings** — measured with a rate-matched null and **no
detector involved**, so the answer is not one instrument's opinion. Per recording it
reports coactivity excess, coordinated-event rate, participants per event and onset
spread.

Three things it will not do, and each is a rule rather than a limitation:

- **It does not choose `K`** — the floor for how many ROIs make an event. `K` moves
  the headline by an order of magnitude, so every value in the scan is printed and
  none is marked as the answer. Quoting one of these numbers means naming its `K`.
- **It does not measure treatments.** Coordination properties come from untreated
  recordings only; a region whose name is not a baseline is counted and skipped, and
  the count is printed. A folder with no `regions.csv` at all is assessed over its
  whole extent, and the report says that is what happened.
- **It does not turn a measurement into a setting.** That step needs a person who
  has looked at the recording.

A recording whose baseline is shorter than the assessment's floor comes back with no
numbers at all rather than with undefined ones, and the same is true of the tightness
comparison when no cluster forms — it prints as *undefined*, never as a value.

## The rules that make it universal

1. **One folder in, one folder out.** No path outside it is ever read.
2. **Only the recording files are required.** The two tables add fidelity; neither
   is a precondition. A folder holding one CSV of onset times is a valid input —
   bugarach then asks for the frame interval and analyses the recording as one
   unlabelled window. Add `slices.csv` and it stops asking; add `regions.csv` and
   the results split by treatment.
3. **No controlled vocabularies.** Stream names, region labels, ROI ids and slice
   ids are the lab's own strings. bugarach matches them, counts them, and hands
   them back.
4. **Nothing is inferred that was not given.** No window is derived, no region is
   assumed to be a baseline, no viability verdict is computed, no missing metadata
   is invented.
5. **Extra columns are ignored, not rejected**, so one file can serve several
   consumers.
6. **A quantity different producers define differently travels with its definition**
   — `width_sec` with `width_def`, `strength` with `strength_unit` — and is never
   pooled across definitions. The label is the producer's own string, to be matched
   and carried, never parsed.
7. **Missing is written as missing** — literally `NA`, never an empty field and
   never a plausible substitute.
