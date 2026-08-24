---
status: open
filed: 2026-08-21
---

# Notes from Tony using the app — collecting, not yet acted on

Tony, 2026-08-21, while driving the deployed page: *"hold until I say go. these
are notes while using the app … store these, then wait for my go."*

The list is open and more may arrive; the call sites are recorded so acting on it
later does not start with a hunt.

## Where each one stands, 2026-08-23

Every note has been built. What is left is not code: it is four choices that
change what a step MEANS, and each of them is Tony's. They are listed here
rather than guessed at, and each is argued under its own note below.

| | note | state |
|---|---|---|
| 1 | window legend | **done** — the swatch carries both channels, is labelled `Analysis windows`, and now draws the trim or shows there is none |
| 2 | "no detector involved" | **done** — the chip no longer claims it |
| 3 | define K in the control | **half** — the control defines K; count-versus-percent is open |
| 4 | region selector | **half** — the menu says whose periods it lists; what the menu should BE is open |
| 5 | header wastes vertical | **done** |
| 6 | nothing happens on Assess | **done** — the chip persists, and says "ran · window too short" where nothing could be measured |
| 7 · 10 · 11 | panel order | **done** — one move, `SECTIONS` and the DOM in step |
| 8 | assess the whole folder | **done** — 84 of 84 in 10.2 s with the CLI's own progress line; whether it should aim the simulator is open |
| 9 | detect "all" + settings together | **done** — including the folder run, which ignored the tick list until 2026-08-23 |
| 12 | tune selector | **done** — its own tick list, LoCo and CICADA marked costly; whether the two lists are linked is open |

**The four open choices, gathered.** Each needs a person who knows what the tool
is for; none of them is blocked on anything but that.

- **K as a count or a percent** (note 3). Measured. A straight swap clamps to the
  3-ROI floor on small fields and forks from `assess.DEFAULT_MIN_ROIS`.
- **What the assessor's region menu should be** (note 4). It serves two jobs with
  one control; naming the list is all that has been done.
- **Whether the folder assessment aims the simulator** (note 8). A data set median
  in place of one recording's numbers changes what the accept step means.
- **Whether Tune's tick list and Detect's are one preference or two** (note 12).
  Built as two, because two cannot lose data; linking them is one line.

---

## 1 · The window legend describes the bar and not the shading

> *"bar = the period · shading = the part scored" — the legend shows the bars,
> legend should show the shading and label as the accordion head (match!)
> "analysis windows"*

**Where.** [`raster_viewer.html:1411-1415`](../site/raster_viewer.html) — the
legend line built at the end of the per-window loop that fills `#wins`, and the
swatches above it at :1395-1398 (`span.sw`, filled with `ink(w.label)`).

**What is wrong.** The legend sentence names two channels — the bar and the
shading — and the swatches next to it draw only one of them. Every swatch is a
solid block of the period's colour, so the reader is told a shading exists and is
never shown what it looks like. The line reads as an explanation of a key that is
not there.

**What Tony asked for.**

- the legend's swatch shows **the shading**, not just the bar, so both channels
  the sentence names are visible in the key;
- the legend is **labelled**, and the label is **the accordion head verbatim** —
  `Analysis windows` (`raster_viewer.html:355`) — so the picture and the panel
  that controls it say the same words. "match!" is the emphasis, and it is the
  point of the note rather than a detail of it.

**Watch out for.** The second branch of that same line reads *"shading = the
same, no analysis window was sent"* — a key drawn for the first branch has to
stay honest under the second, where the shading and the bar are deliberately the
same extent. Whatever the swatch shows must not imply a distinction the folder
did not make.

### Landed 2026-08-23 — and the watch-out was the harder half

The swatch carries both channels and the legend takes the accordion head's own
words. What that left, and what this pass fixed, is the warning above: the
swatch drew a saturated rail over a pale field on **every** folder, including
the ones that never made the distinction — and this lab's export is exactly that
case, 238 regions with not one analysis window among them. So the picture
asserted a trim the folder had not sent, in the key explaining what a trim looks
like.

The shading is its own box now, so it can stop short of the rail above it, and
that gap *is* the trim. Three states rather than two, because there are three:
no analysis window sent · one sent that trims nothing · one sent that trims. The
first two draw one extent and say which of the two they are; only the third
insets. Decided per window, not per recording — one folder can trim one period
and not the next, and a single flag would draw a trim on the period that has
none.

---

## 2 · "no detector involved" is not true of the assessor

> *"under assess coordination, do not say no detector involved. the assessor is
> by definition a detector"*

**Where.** [`raster_viewer.html:404`](../site/raster_viewer.html) — the chip on
the `Assess coordination` accordion head. It is the only place the page makes
this claim; the fine print inside the panel does not repeat it.

**What is wrong.** The chip is asserting something false about what the step
does. The assessor finds coordinated clusters and returns their times, their
participants and their spread — that is detection. What it is *not* is one of the
**six named detectors**, and it does not need a threshold or an operating point,
which is presumably what the phrase was reaching for. Saying "no detector
involved" buys that distinction by making a wrong statement about the method.

**Why it matters more than a word.** The whole architecture of the page rests on
the assessor being a measurement the six are later scored against. A reader who
believes the assess step involves no detection has the relationship between
stages 3 and 6 backwards, and this is the chip that told them so.

**Not yet chosen: the replacement wording.** The chip is short by design — the
others are `no data needed`, `your own recordings`, `simulated only`, `local
only`, `draft`. Something in that register that says *no threshold to pick* or
*no operating point* rather than *no detector*. Tony's call, and it belongs with
the rest of the copy pass rather than being guessed at here.

---

## 3 · Define K in the control, and the count-versus-percent question

> *"assessor controls, define K as the min number of ROIs participating in a
> coordinated event. i wonder if this should be toggled to percent, as we have
> some with 10 rois or less maybe"*

**Where.** [`raster_viewer.html:412`](../site/raster_viewer.html) — the control is
labelled `mark clusters at K` and offers `none / 3 / 4 / 6 / 8` with no statement
of what K counts. `K_SCAN = [3, 4, 6, 8]` at :3174, tracking
`assess.DEFAULT_MIN_ROIS`. The panel's fine print calls K *"the floor for how many
ROIs make an event"* — which is the definition Tony wants, sitting two paragraphs
below the control instead of on it.

### The easy half

Label it as what it is: **the minimum number of ROIs participating in a
coordinated event.** No argument here, and it is the one place a reader meets K
before any of the prose.

### The harder half, and it is a real question — measured

Read-only over `2026-08-18_revised_2v_periods`, 84 recordings:

| | ROIs |
|---|---|
| min | **9** |
| p25 / median / p75 | 23 / 32 / 37 |
| max | **61** |

So the field size spans about **7x**, and the same K is a different question on
each end:

| K | on the smallest (9) | at the median (32) | on the largest (61) |
|---|---|---|---|
| 3 | 33% | 9% | 5% |
| 4 | 44% | 12% | 7% |
| 6 | 67% | 19% | 10% |
| 8 | **89%** | 25% | **13%** |

**Tony's instinct is right about the effect and slightly off about the cause.**
Recordings with ≤10 ROIs are **2 of 84 (2%)** — 9 and 10 ROIs, `20241004_80` and
`20260707_346`. The problem is not those two; it is that K is an absolute count
across a folder whose field size varies 7-fold, so *"coordination at K=8"* is a
claim about a quarter of the field in one recording and nearly all of it in
another. That bites at the median too.

### What blocks a straight swap to percent

**The 3-ROI floor.** `minRois` is fixed at 3 in the detectors
([:2228](../site/raster_viewer.html)) and is deliberately **not a knob** —
FOUNDATIONS §9, because raising it until false alarms disappear is the exact
error this project has already refused once. A percentage lands under it on small
fields:

| asked | smallest (9) | median (32) | largest (61) |
|---|---|---|---|
| 10% | **1 ROI** ⚠ | 3 | 6 |
| 18% | **2 ROI** ⚠ | 6 | 11 |
| 30% | 3 ROI | 10 | 18 |

So on the 9-ROI recording every sensible percentage clamps to the floor and
becomes K=3 — the count behaviour, wearing a percent label. A toggle must **show
that clamp** rather than silently honour a number it did not use.

**And it would fork from Python.** `K_SCAN` tracks `assess.DEFAULT_MIN_ROIS`,
which is a count. A browser scanning percentages is scanning different Ks than
`bugarach.assess` does, and the two stop being comparable unless Python moves
with it.

### Worth noting: the app is already inconsistent about this

The **simulate** side already speaks in percent — participation is
`30/18/10% — measured` ([:302](../site/raster_viewer.html)) — while the
**assess** side speaks in counts. The same quantity, two units, two panels. So
this is not only a convenience question; it is the one place the page contradicts
itself about how participation is expressed.

**Undecided, and Tony's call:** whether to toggle, or to show both (`K = 6 · 19%
of this field`) and keep the scan in counts. The second is cheaper, forks nothing,
and answers the comparability complaint without inventing a clamp to explain.

---

## 4 · The assessor's region selector offers every period, including the wrong ones

> *"the region selector for the assessor should be simply baseline (or first
> region if not called baseline?) or full trace. i could be convinced to allow
> the user to select one additional region, but sb222200 should not be on this
> list. why is it present and not ttx or senk?"*

**Where.** `paintRegionChoices` at
[`raster_viewer.html:3701`](../site/raster_viewer.html) — it lists **every**
region the recording declares, appending *"— not for calibration"* to any whose
label is not baseline, plus a `whole recording` entry.

### Answering the question first: it is not a bug, and TTX is not missing

The list is **per recording**, not a vocabulary for the folder. The export carries
all of these:

| label | regions |
|---|---|
| baseline | 84 |
| high K+ | 60 |
| TTX | 38 |
| senktide | 35 |
| SB222200 | 12 |
| wash | 9 |

`SB222200` appeared because the recording open at the time has one. The twelve
that carry it are, in full — and note the first four are the first files in the
folder, so this is what anyone sees on opening it:

    20240708_13     baseline, SB222200
    20240708_17     baseline, SB222200, high K+
    20240723_22     baseline, SB222200, high K+
    20240726_34     baseline, SB222200, wash, high K+
    …
    20241216_135    baseline, SB222200, senktide
    20241216_137    baseline, SB222200, senktide

`20240708_13` has **only** baseline and SB222200 — no TTX, no senktide — so on
that recording the selector is showing exactly what the folder declared.

**But the confusion is itself the finding.** If a reader cannot tell that the list
is *this recording's own periods*, an unexpected drug in it reads as a bug in the
app. It cost this exchange; it will cost the next reader too. Whatever the list
becomes, it should say whose periods it is showing.

### What Tony asked for

- **baseline**, or the **first region** when nothing is called baseline;
- **full trace**;
- possibly **one** additional region, chosen by the user;
- and `SB222200` — a treatment — off the default list.

**Every recording in the current export has a region labelled `baseline`** (84 of
84), so the "first region if not called baseline" fallback is for other labs
rather than for this folder. Worth keeping anyway: `isBaselineLabel`
([:3183](../site/raster_viewer.html)) matches on a token prefix, so a lab whose
baseline is called something else already falls through it.

### The tension to resolve before building it

Measuring a treatment **is legitimate** and the code says so in terms
([:3410](../site/raster_viewer.html)): *"Measuring TTX and comparing it to
baseline is a legitimate thing to want; feeding TTX into the simulator is not."*
FOUNDATIONS §9 forbids taking coordination **properties** from a treatment, which
is a rule about parameterising the generator, not about looking.

So the panel is serving two jobs with one menu — *pick the calibration source*
and *look at this period* — and the guard already exists on the dangerous one:
`simulateFromMeasurement` refuses a non-baseline measurement outright. The menu
just does not reflect that only one entry is for the job the panel is named
after.

Tony's "one additional region" is exactly the second job. The open choice is
whether that is a second control, or a menu that separates the two groups
visually rather than tagging each entry with a disclaimer.

### Half of it landed 2026-08-23: the list says whose periods it is

The unambiguous half — *"whatever the list becomes, it should say whose periods
it is showing"* — is built, and it is built by **naming, not filtering**. The
recording's own periods sit in an `<optgroup>` labelled `declared by
20240708_13`, and a line under the control says the same in a sentence for the
reader who never opens the dropdown: which periods this recording declares, that
another recording declares different ones, that any of them can be measured, and
that only a baseline can set the simulator.

Nothing was removed. Measuring TTX and comparing it to baseline is legitimate,
the code says so in terms, and the guard that matters — `simulateFromMeasurement`
refusing a non-baseline outright — was already there.

### Still open, and it needs Tony: what the menu should BE

The panel does two jobs with one control and this pass did not change that. Four
questions, none of them answerable from the code:

1. **Should the default list be baseline + full trace only**, as Tony first
   asked, with everything else behind a second control? That is a smaller menu
   and a second thing to find.
2. **Or one menu in two groups** — the calibration source, then "or look at one
   of these" — which is what the `<optgroup>` split above is one step away from
   and needs no second control.
3. **Is "one additional region" a limit or an example?** A limit of one needs a
   reason; the panel measures one region at a time either way.
4. **Does the "first region if not called baseline" fallback ever fire?** All 84
   recordings in this export declare a `baseline`, so it is for other labs, and
   `isBaselineLabel` already matches on a token prefix. Worth keeping — but
   whether an unnamed first region should be *offered as* the baseline, rather
   than merely measurable, is the same two-jobs question in miniature.

The reason to stop here rather than pick one: every option changes what the
panel is FOR, and the panel is named after the job it might stop doing by
default.

---

## 5 · The header wastes the vertical space the sidebar needs

> *"huge waste of white space at the top when we need max verticality on the
> left. make 'open a recording' one line and medium sized"*

**Where.** [`raster_viewer.html:259`](../site/raster_viewer.html) — `<h1>Open a
recording</h1>` at 19px ([:74](../site/raster_viewer.html)), followed by a
`div.sub` running six lines: the import-contract link, the no-network promise,
and the invitation to simulate a folder.

The header sits above **both** columns, so every line of it costs the accordion
column — which is the one that has nine panels to fit and is where the work
happens.

**What Tony asked for:** the title one line, medium sized. The `div.sub`
underneath is the larger consumer of the space and he did not mention it — worth
asking whether it should shrink, move into the empty-state panel (which already
repeats much of it), or stay as the page's one statement of the promise. The
no-network sentence is the page's central claim and it is deliberately above the
fold; that is the part not to lose while reclaiming the room.

---

## 6 · "Nothing happens when I click Assess" — it ran, and showed you nothing

> *"nothing happens when i click 'assess this recording'? need progress bar or
> assessed check box plus indicators on raster that something happened"*

**It is not broken and it is not slow.** Driven against a real recording out of
the current export — `20240708_13`, 34 ROIs, 4,494 events, two streams, 1,000
surrogates:

    open + draw   44 ms
    runAssess    185 ms      <-- the click
    errors       none
    assessOut    1,413 characters of table

So the work is done before a spinner could render. Three separate things
conspire to make that look like nothing at all:

**a. The raster is marked only if you already chose a K, and the default is
"none".** `mark clusters at K` defaults to `0`
([:414](../site/raster_viewer.html)) and `K_SCAN` is `[3, 4, 6, 8]`, so
`res.find(a => a.K === wantK)` at [:4501](../site/raster_viewer.html) never
matches, `ASSESS` is set to `null`, and the tick marks are not drawn. **By
default, assessing a recording changes the raster in no way whatsoever.** That is
the whole of Tony's "indicators on raster that something happened", and it is a
default rather than a missing feature.

**b. The result renders in the other column.** `#assessOut` is at
[:798](../site/raster_viewer.html), inside `#view` — the right-hand stage,
*below the canvas*. The button is in the left accordion. On a tall raster the
table lands below the fold, so the click is in one place and its consequence is
in another, off screen.

**c. The button's own feedback is too fast to see.** It sets
`"Assessing…"` and restores in 185 ms.

**So a progress bar is the wrong fix** — there is nothing to wait for. What is
missing is *persistence*: something that still says "this recording has been
assessed" a second later. Tony's "assessed check box" is the right shape.

Worth deciding together:
- whether marking the raster should default to **on** at some K rather than
  `none` — which collides with *"K is a scan, not a choice"* and the panel's
  refusal to pick one for you. A tick layer at every K, or a neutral "clusters
  found" mark independent of K, may thread it;
- whether the chip on the accordion head should carry the state, the way
  `cntDetect` names the current detector.

## 7 · Tune belongs between Assess and Detect

> *"tune the settings should come after assess. then detect events"*

**Where.** DOM order is Simulate, Open, Analysis windows, Assess, **Detect**,
**Tune**, Lab, Compare, Recordings; `SECTIONS` at
[:6203](../site/raster_viewer.html) repeats it and the accordion behaviour
follows that array.

Tony wants **Assess → Tune → Detect**, which is the order the workflow actually
runs in and the order the plan states: measure, simulate from the measurement,
tune against planted truth, then point the tuned instrument at everything.

**One dependency to fix in the same move.** The Tune panel's own copy says it
sweeps *"one setting of the detector chosen above"* — the chooser lives in the
Detect panel. Put Tune first and "above" is false. Either the sentence changes,
or the detector chooser moves up with it. The second is probably right: the
chooser governs both panels, and after the *use this setting* button landed it is
the Tune panel that acts on it first.

Also worth checking on the move: `showSection` opens one panel at a time, and the
apply button calls `showSection("accDetect")` — reordering must not leave that
jumping backwards past the panel the reader just used.

## 8 · Assess the whole folder

> *"assessor should have assess whole folder option?"*

**Yes, and Python already has it** — this is a port, not a design.
[`src/bugarach/assess_folder.py`](../../src/bugarach/assess_folder.py) is
`bugarach assess my_export/`: it walks the folder, measures every recording's
baseline region, and prints the scan as a table. It landed 2026-08-18 and the
browser never got it, which is why the page still assesses one recording at a
time while the CLI assesses a folder.

It also already carries the three rules the browser would otherwise have to
re-derive, and getting any of them wrong is the kind of error this repo files
todos about:

* **K is a scan, never a choice** — every K printed, none picked;
* **`jit_defined` is a state, not a NaN** — the tightness comparison can be
  undefined while a finite-looking number sits in the field;
* **baseline regions only**, and **non-baseline regions are counted and the
  count is printed**, so the skip is visible rather than silent (FOUNDATIONS §9).

That last one answers note 4 from the other direction: the folder assessor
already decided that treatments are skipped and *said how many*, which is the
behaviour the per-recording selector is being asked for.

**What it is worth beyond convenience.** The webapp's completion plan calls this
Phase 2, *"a data set, not a recording"*, and the reason is not batching: the
generator is parameterised from **one** recording's measurement today, so the
simulated data set inherits whichever recording happened to be on screen. A folder
assessment is what makes "typical of this lab" a measurable statement rather than
a choice of file.

**Cost check before building.** 185 ms per recording measured above, two streams,
1,000 surrogates — so 84 recordings is roughly **15 seconds**, single-threaded, in
the page. That is genuinely a progress-bar job, unlike note 6.

**Open:** whether the folder assessment feeds the simulator directly (a data set
median rather than one recording's numbers), which is a real change to what the
accept step means and is Tony's call, not a port detail.

### Landed 2026-08-23 — and it is faster than the arithmetic said

`Assess all 84 recordings` sits under `Assess this recording`, and it is the
Python's rule rather than the panel's: baseline regions only, the producer's
analysis window where one is stated, a recording with regions and no baseline
**skipped and named**, and the folder's whole vocabulary tallied and printed so
the skip is visible.

Driven on `2026-08-18_revised_2v_periods`, served: **10.2 s, 84 of 84 measured,
none skipped, none under the floor** — against the ~15 s the 185 ms figure
predicted. Still far too long for a button that greys out and says nothing, so
the progress line is `cli._progress`'s own, word for word:

    assessing: 17/84 · 20241120_94 (1s, ~5s left)
    assessing: 84/84 in 10s

The tally it prints is the same one this note recorded by hand — baseline 84,
high K+ 60, TTX 38, senktide 35, SB222200 12, wash 9 — which is the check that
the port reads the folder the same way the command does.

**What it reports that one recording cannot.** A per-K median across the folder,
and the field's typical background rate as the *median of each recording's
MEAN* — 9.9 mHz per ROI over 32 ROIs — because the simulator's rate box means the
mean and handing it a median of medians is the defect the single-recording path
already paid for.

**The open question is still open, deliberately.** The panel prints the folder's
number and says in as many words that the accept step still aims the simulator
from one recording, and that which of the two should aim it is not the port's
decision. A port that quietly rewired the accept step would have made the call
this note reserves.

## 9 · Detect should offer "all", and the settings should be visible together

> *"detect should have the option to select all. maybe a popup window with all of
> the settings for all of the detectors in one panel"*

### The running-all-six half is nearly free

`analyseFolder` ([:4322](../site/raster_viewer.html)) **already** runs every
detector — across every recording, stream and region — and it was written this
week. What does not exist is the same thing scoped to the recording on screen:
`runDetect` takes `whichDetector()` and draws one.

So *"detect with all six, here, now"* is a loop that already exists in another
function, and the honest version is probably to factor the per-recording body out
of `runDetect` so the two cannot drift into disagreeing about what a detection
run is.

### The settings-in-one-panel half is also cheap

Each detector's controls are already a separate block —
`dRateCtl`, `dSyncCtl`, `dLocoCtl`, `dCoactCtl`, `dSceCtl`, `dCicCtl`
([:449-495](../site/raster_viewer.html)) — and `paintDetectorChoice` does nothing
but hide five and show one. Showing all six is removing that filter.

**On "popup window":** the page has no dialog or modal anywhere today (zero
`<dialog>`, zero `showModal`). A `<dialog>` element is self-contained and needs
no network, so it costs nothing against the no-network promise — it would just be
the page's first one, and worth deciding deliberately rather than by accident.

### What is NOT free: the raster

This is the part to think about before building the easy parts.

- **There is one lane.** `LANE_H = 37`, drawn once, in one colour (`--accent`),
  labelled with the single detector's name
  ([:1155-1170](../site/raster_viewer.html)). Six detectors need six lanes or one
  lane that distinguishes them.
- **They must stay distinguishable — this is a rule, not a preference.** The
  output contract is *one row per event per detector, no consensus merging*,
  because merging discards which detector fired. A raster that stacks six
  detectors into one bar has done exactly the merge the file format forbids, in
  the picture that gets screenshotted into a slide.
- **Colour is already spent.** The eight categorical window hues are fixed and
  validated for colour-vision deficiency ([:863](../site/raster_viewer.html)),
  and they are an *identity* encoding for periods. Six detector colours would
  either collide with that vocabulary or need their own, and the raster would
  then carry two categorical scales meaning different things.

Six stacked lanes at 37px is 222px of vertical, on the page Tony just asked to
reclaim vertical space from (note 5). A thinner per-detector lane, or lanes only
for the detectors that fired, are the obvious levers.

### Worth settling at the same time

Whether "all" changes what the **save** button writes. `saveDetections` currently
writes `DETECT.rows` for the one run; with six detectors live it becomes the same
shape `analyseFolder` already emits for the folder, which would make the two
buttons the same file at different scopes — a simplification rather than a new
format.

### The half that was missed the first time, landed 2026-08-23

Running several here landed with `chosenDetectors()` and a lane each. **The
folder run did not read it.** `analyseFolder` took `Object.keys(DETECTORS)`
whatever the tick list said, so the one control on the panel governed the raster
and not the file — and the file is the artifact people keep. A minute of work
that cannot be scoped is also a minute nobody can shorten.

It reads the same accessor now, so the picture and the export cannot disagree
about what "all the ticked detectors" means. Three consequences worth knowing:

- **the default changed.** With "run several" unticked the folder run does one
  detector, where it used to do six. So the button says what it will run
  *before* it is pressed — a minute-long button whose scope is discoverable only
  afterwards is how somebody exports the wrong thing and finds out from a slide.
- **a detector that did not run gets no column.** Blank is a third answer beside
  "found nothing" and "could not run", and not one this page is entitled to give.
- **an empty tick list is refused**, in the words `bugarach detect` uses: nothing
  scored is a failed run, nothing found is a result, and a header-only file blurs
  them.

## 10 · Simulate belongs next to Tune

> *"simulate a folder and tune should be combined i think. or move simulate to
> just before tune"*

**The argument is already written in the app.** The Tune panel's own copy says
it: *"Only on a folder this page invented, and that is the reason the simulate
step exists."* The simulation is not a feature beside tuning, it is tuning's
answer key — and it sits four panels away from it, at the very top.

### Where this lands with note 7

Taking both notes together the order becomes:

    Open a folder → Analysis windows → Assess → Simulate → Tune → Detect → …

which is the workflow sentence the plan opens with: measure your recordings,
simulate from what you measured, tune against planted truth, then point the
tuned instrument at everything.

### The thing that order hides, and it is not cosmetic

**Simulating REPLACES the open folder.** `runSim` calls `open(made.files, …)`,
and `open` clears `RECORDINGS`, `REGIONS`, `META` and `TRUTH` and repopulates
them ([:1550](../site/raster_viewer.html)). So in the order above, step 4
destroys the folder loaded in step 1 — your own recordings are gone from the page
and must be re-opened before step 6 can run on them.

That is **already true today**, and it is why `SIM_TARGET` and `TUNED` were
deliberately written to survive `open`: the measurement and the operating point
cross the gap even though the recordings do not. But a linear top-to-bottom
panel order *implies a pipeline that accumulates*, and this one has a step in the
middle that throws away the input. Today's order half-hides that by putting
Simulate at the top, before anything is open.

So the reorder is right and it makes an existing sharp edge more visible, which
is an argument for doing it **with** a word about the swap rather than before
one. Nothing warns about this at present.

### Combined, or adjacent?

**Adjacent looks better than combined**, for two reasons rather than taste:

- the simulate step has a **second** consumer — note 5's stage-5 comparison
  (`Compare with the real folder`) lives on it, and that is about the generator's
  fidelity, not about tuning;
- it is also the **entry point for a visitor with no folder**, which is what the
  empty state's `Simulate a folder` button is for
  ([:782](../site/raster_viewer.html), wired at :6217). Moving the panel down
  does not hurt that visitor — the CTA jumps them straight to it — but folding it
  *into* Tune would put the no-data path inside a panel that requires data.

Ten-plus controls in one panel is also a lot next to the four Tune has.

**Open:** whether the reorder should come with a line on the Simulate panel
saying it replaces what is open, and whether re-opening the real folder afterwards
deserves a shortcut (the Open panel already remembers the directory).

## 11 · The recordings list belongs under Open a folder

> *"recordings nav should be under open folder"*

**Where.** `accList` is **last** in the DOM ([:763](../site/raster_viewer.html))
and last in `SECTIONS` ([:6203](../site/raster_viewer.html)), below the training
panel and the comparison table. It is the navigation for the folder you just
opened, sitting nine panels below the button that opened it.

Cheapest of the eleven and no argument against it.

### The order all three ordering notes add up to

Notes 7, 10 and 11 together:

    Open a folder → Recordings → Analysis windows → Assess
                  → Simulate → Tune → Detect → Train → Compare

which reads as the sentence the project describes itself with. Worth doing as
**one** move rather than three, since `SECTIONS` and the DOM have to stay in step
and each reorder re-tests the same accordion behaviour.

## 12 · Tune should let you pick which detectors to sweep

> *"tune panel should have a selector for which detectors to tune. most users
> will have a favorite or two and wont even look at the weirdos we created"*

**Today the page offers one or six and nothing between.** `runTune` sweeps
`whichDetector()` — a single detector, borrowed from the Detect panel's chooser.
`scoreAllDetectors` sweeps all six on one data set and one fold split. A subset is
not expressible.

### This is a merge, not a new feature

The two functions are the same loop at different widths, and a multi-select in
Tune subsumes both: **one selected is today's Tune, all six selected is today's
scoreboard.** Worth building it that way rather than adding a third path —
especially since the scoreboard is still gated off the public page pending its
copy review, so it is the cheapest moment to fold it in rather than the most
expensive.

### The timings argue for it harder than preference does

Measured on the scoreboard run, fit seconds per detector over the same data set:

| detector | fit | detect |
|---|---|---|
| SPIKE-synch | 0.06 s | 0.001 s |
| CoactDetect | 0.08 s | 0.001 s |
| RateDetect | 0.10 s | 0.000 s |
| SCE | 0.17 s | 0.003 s |
| **LoCo** | **2.69 s** | 0.073 s |
| **CICADA** | **7.06 s** | 0.302 s |

Two detectors are **97% of the wall clock**. Deselecting them is not a
convenience, it is the difference between a sweep that returns while you are
looking at it and one you wait out. On a bigger data set, or the folder assessment
of note 8, that gap grows with the work.

### Who actually wrote the six — corrected by Tony, 2026-08-21

An earlier draft of this note claimed four of the six came from outside. **That
was wrong**, and the mistake is instructive enough to record rather than quietly
fix — see the todo it produced,
[`the word "port" is doing two jobs`](2026-08-21-port-means-two-things-in-the-detector-docstrings.md).

The actual provenance, per Tony and confirmed against the README's licensing
table:

| detector | whose method |
|---|---|
| **CICADA** | **the only ported one** — Cossart lab, `cossartlab/cicada`, MIT, carries the upstream copyright |
| **SPIKE-synch** | the *synchrony profile* is the Kreuz-lab measure (PySpike semantics, BSD). **The detector run on that series is ours** — hysteresis detection and artifact flagging |
| **RateDetect** | ours |
| **SCE** | ours, derived from ideas in CICADA |
| **LoCo** | ours |
| **CoactDetect** | ours |

So **five of six are this project's own**, one is ported, and one of the five
builds its detector on a third-party measure. LoCo and CoactDetect — the two that
**lead the comparison** — came out of Tony working the problem directly.

That matters beyond credit. A selector labelled *"the ones we made up"* would be
wrong in the direction of underselling, and the page's honesty rules are written
against overclaiming, so nothing currently catches an understatement. A neutral
list with the two **costly** ones marked as costly does both jobs and asserts
nothing about authorship.

**Open:** whether the selector lives in Tune with the detector chooser moved up
from Detect (note 7 already moves it), and whether a detector deselected here
should also drop out of the Detect step's "all" (note 9) — one preference, or
two?

### Landed 2026-08-23, and the timings came out steeper than the estimate

Tune has its own tick list, built from the registry with LoCo and CICADA marked
`slow` — a neutral list with the costly ones named, which is what this note
argued for and what avoids a label that would understate the authorship. The
sweep runs each ticked detector in turn, prints one block per detector under a
line naming the scope, and reports elapsed at the end.

Measured on four simulated 45-minute recordings, in the served page: **the cheap
four in 0.8 s, all six in 6.2 s.** So unticking two of six is not a preference,
it is 7.5x, and the panel used to show one static "Sweeping…" over the whole of
it.

**The progress line reports position and elapsed and no ETA, deliberately.** The
folder walk of note 8 can divide elapsed by recordings done because recordings
cost about the same. Detectors do not — a remaining-time figure taken before
CICADA starts would be wrong by an order of magnitude and would be believed. The
cost markers beside the ticks are where the reader learns the shape of what is
left, and the panel names the slow ones in the sentence under the button, before
the click.

**One preference, or two? Built as two.** Unticking CICADA to get a sweep back in
a second must not silently drop it from the folder export an hour later. Fitting
an operating point and using one are different decisions, and two lists cannot
lose data where one can. The defaults are shared, so the page still has one
opinion about which detectors a reader meets first. **If Tony wants them linked,
linking them is one line** — the argument against is a comment beside the second
list rather than a thing to rediscover.

**Not folded into the scoreboard, and that is a deferral rather than a
disagreement.** This note is right that the multi-select subsumes
`scoreAllDetectors`, and the merge is easier now than it will be later. But the
scoreboard is still hidden behind its own copy review
(`2026-08-20-the-scoreboard-copy-needs-review.md`), and folding it into a live
panel would publish copy that review has not seen. `sweepDetector` is split out
of the orchestrator with that merge in mind: the scoreboard's loop is the same
one at a different width.

---

## Related, and worth doing in the same pass

`docs/todo/2026-08-20-the-scoreboard-copy-needs-review.md` is the other open copy
item. Both are wording on the published page; reviewing them together is cheaper
than twice, and the scoreboard panel cannot be un-hidden until its own review is
done anyway.
