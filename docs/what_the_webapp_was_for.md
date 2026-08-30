# Nobody chose the six, and the in-app comparison runs in one front end

> **Tony, 2026-08-29, and it is the right reading:** *"the webapp was supposed to
> have detectors and deep learning modules and compare performance. never once was
> it dictated that the six were special or that tube was THE ONE."*

**Short answer: nobody dictated either, and the two halves are in different
states.** The learned half has a registry and the browser page reads it — six
architectures, one `@register` line each, and the model picker is built from that
registry at runtime. The hand-written half has no registry at all: six detector
names dispatched by hand across five sites in `src/`. And the Panel viewer, one of
the two front ends, cannot reach a learned model at all. The offline comparison
does run over both halves (`tools/fair_bakeoff.py`); it is the *interactive* one
that exists in a single front end.

**The ask:** give the Python side the record the browser already has, and pin the
two. Roughly a day — an estimate, not a measurement — and §*What would fix it*
says what it must not do.

*This is bugarach — a folder of detected calcium events goes in, coordination
detectors run over it, and their performance is compared against planted truth. A
"detector" here emits coordinated-event calls; F1, recall and precision are scored
against those plants.*

---

## What was supposed to happen

`docs/workflow_plan.md` is the app's approved shape (review record:
`docs/reviews/workflow_plan_2026-08-16.md`), and the learned half has its own
brief, `docs/learned/README_for_the_webapp.md`, which says the loop already runs
and *"Your job is to put a UI in front of it, not to rebuild it."*

The intent is one sentence in `src/bugarach/learn/nets.py`:

> A new architecture is one class plus one `@register` line.

That is a platform statement: the set of methods is open, adding one is cheap, and
nothing downstream needs their names in advance.

## Nobody designated tube — but three things did

The learned half kept the promise, and I got this wrong on the first draft in a way
worth recording. The page's architecture `<select>` carries a hardcoded
`<option value="tube">`, and it is **not** the model list — `wireLab`
(`docs/site/raster_viewer.html:9991`, populating at `:10017`) clears it and
rebuilds it from
`/api/capabilities`, one row per registered architecture, offering unavailable ones
disabled-with-a-reason rather than hidden. `src/bugarach/lab.py:617` anticipates
the mistake: *"A hardcoded `<option>` list in the page would be that second edit,
and it would be the one nobody remembers."* The hardcoded option is the
static-build fallback, and the HTML comment directly above it says so. That landed
2026-08-28, the day before this was written.

So "tube is THE ONE" is not markup. What is real is narrower and more interesting:

1. **It is the default selection** — one line, `raster_viewer.html:10029`:
   `else if (a.name === "tube") o.selected = true;`
2. **It is the only learned architecture with an operating point.** Of the three
   ever benchmarked, two pick a threshold at the search floor and are not operating
   points (`docs/todo/2026-08-28-two-architectures-have-no-operating-point.md`).
3. **Three of the six registered architectures have never been benchmarked at
   all** — `tube_guard`, `tube_ratio`, `tube_ratio_guard` are in the registry and
   absent from the bake-off.

**And the Panel viewer has no learned models whatever.** Neither `tube` nor `learn`
appears in `src/bugarach/ui/app.py`. Two front ends; the learned-versus-hand-written
comparison exists in one.

## Nobody chose the six either

There is **no detector registry in `src/`**. `bench.OPERATING_POINTS` and
`emit.DETECTOR_FIELDS` are two partial records with no shared key list, and each
detector's name is a string literal appearing **14–19 times across 4–5 modules**,
maintained by hand:

| kind | where |
|---|---|
| tables | `bench.OPERATING_POINTS`, `detect_folder.DETECTORS` / `NESTED` / `ONSET_FIELD`, `emit.DETECTOR_FIELDS`, `ui/app` `COLORS` / `TITLES` / `SHORT` / `_SPECS` / `DT_DERIVED` |
| dispatch on the name | `bench.run_detector`, `detect_folder.detector_params`, `detect_folder._run_flat`, `detect_folder._run_nested`, `ui/app._compute` |

Five dispatch sites, and they do not agree with each other. `bench.run_detector`
feeds `coact` and `sync` through `stream_trains` (which clips to the extent and
drops non-finite values); `detect_folder._run_flat` and `ui/app._compute` hand them
raw `st.t50rise`, which does neither. The bench and the folder path are not running
the same thing.

**The browser, by contrast, already has the record.** Its `DETECTORS` object
carries per detector: `label`, `run` (call shape), `read`, `settings`, `params`,
`knob` + `grid`, `unavailable` (availability) and `peaks: true` (a required input) —
and `tests/test_webapp_settings_file.py` derives its checks from it. That is most
of what a registry needs, already built and load-bearing in one reader and absent
from the other.

In fairness to the Python side, its *data* is deliberately factored:
`emit.DETECTOR_FIELDS` reconciles six output shapes in one table and says *"A
seventh detector is one entry here"*; `OPERATING_POINTS` is guarded at import so a
viewer default cannot drift from the bench. What was never factored is the wiring.

## What the comparison says

![Panel A, nine methods' F1 with each of four folds drawn on the bar: the top
three — center−surround (learned) 0.681, CoactDetect 0.651 and LoCo 0.638 — have
overlapping fold ranges, while the two other learned architectures sit at 0.125 and
0.118, far below every hand-written detector. Panel B, detection time against
accuracy on a log axis, marker area by parameter count.](learned/bakeoff.png)

Full table and provenance: [`learned/bakeoff.md`](learned/bakeoff.md). ⚠ Per
[RESET §5](RESET.md), everything in `docs/learned/` was computed before the
difficulty axis was corrected; these numbers are quoted as they stand. The
2026-08-28 re-run fixed three unrelated defects and kept the store-derived
generator spec, so the axis correction has still not reached them.

The bake-off's own summary is that **three** detectors are tied at the top, not
that one leads: fold ranges 0.63–0.74, 0.61–0.71 and 0.57–0.70 overlap. Behaviour
separates them more than F1 does — tube recall 0.917 / precision 0.543 against
CoactDetect's 0.767 / 0.572: the learned model buys recall and pays in precision.

One thing the figure shows cuts *against* a tidy story and belongs here: tube beats
the other two learned architectures by roughly 0.56 F1 on the mean, and by at least
0.50 at every fold. It was not crowned by markup — among the models actually
measured, it won. ⚠ But that comparison is **uncontrolled**, and the same todo
cited above says so: `trace` trained at a tenth of tube's learning rate, so *"the
pooled baseline is worse" is not separable from "the pooled baseline was trained
differently."*

## What the calcification has already cost — and where it does not reach

locust is the only one of the six that consumes a per-event duration, and this is
where the two halves of the diagnosis have to be kept apart, because I ran them
together on the first draft.

**The platform does express the requirement.** `peaks: true` declares locust's
peak-anchor need in the browser registry and `cicadaTrains` refuses in words when a
folder cannot supply one; `perEventDuration` is a live two-valued control. That is
a declaration, in the reader that has a registry.

**What cannot express it is the generator.** `simulate.py` plants no per-event
durations, so `Stream.width_def` is `None`, `has_width` is `False`, and locust in
per-event mode would raise. **The bench can exercise only one of locust's two
duration modes, and the other has never been scored** — not because it lost, but
because there is nothing planted for it to read. That is a `simulate.py` gap, not
an architecture gap, and no registry fixes it.

What the missing Python record *did* cost is prose. Ten surfaces named a duration
rule paired with the wrong stream — and naming any producer rule here is what
FOUNDATIONS §7 forbids, precisely because it goes stale and readers mistake the
producer's decision for ours. It survived a session whose subject was this exact
area; Tony caught it, not the test suite. Sapper now blocks the code half outright
(SAP012) and the one phrase that recurred ten times (SAP013) — narrower than it
sounds: reviewing *this* document turned up a live instance inside SAP013's own
scope that its pattern does not match, a user-facing settings string naming a
producer's rule, fixed in the same change. The general form is already filed —
[`docs/todo/2026-08-28-there-is-no-root-element-to-assert-a-claim-into.md`](todo/2026-08-28-there-is-no-root-element-to-assert-a-claim-into.md).

## Three things that read as findings and are not

1. **"The six" were not chosen as a set** — they are the six that existed when the
   dispatch sites were written. But they have since been *considered* as one and
   endorsed (`detector_history.md` §6.7, *"Six is the right number"*), and the
   boundary was ruled on separately. What was never designed is the wiring.
2. **"tube is the best model"** is a three-way tie at the top, plus a default
   selection, plus two rivals that were never given an operating point.
3. **"locust underperforms"** is a detector scored in the only mode its benchmark
   can generate data for.

## What would fix it, what it costs, and what not to touch

**Port the browser's record into Python and pin the two** — this is convergence on
a design that already ships, not an invention. A method declares in one place: the
fields it requires, its call shape, its calibrated operating point, its display
name, its cost class, its availability. The five dispatch sites read the record.
A cross-reader test compares the two declarations, which is the rule the tree is
already deriving from repeated incidents
([`2026-08-28-the-two-readers-write-different-width-def-for-locust.md`](todo/2026-08-28-the-two-readers-write-different-width-def-for-locust.md)).

**One hard constraint.** The record may carry the call shape but **never the stream
set**. `detect_folder._run_nested` runs every stream even when one was asked for,
because the three nested detectors draw surrogates from one RNG stream in
declaration order and dropping a stream changes the numbers of the ones that
remain. The filter belongs on the output, never the input. A day of porting that
silently reorders one RNG draw is a day that costs the parity claim.

**Cost: roughly a day — an estimate, not a measurement.** Most of it is porting the
existing six onto the record to prove it covers them.

**What this does not buy.** [`2026-08-25-cfar-variants-are-a-knob-axis-not-new-detectors.md`](todo/2026-08-25-cfar-variants-are-a-knob-axis-not-new-detectors.md)
— Tony-ruled — argues the wiring is not what makes a new detector expensive: the
binding costs are the tuned constants and a scorer two tools compute differently.
The registry removes the wiring cost only. That is worth having and it is not the
whole bill.

**Do not rename the `cicada` key.** It is the `detections.csv` contract value
(ADR-0002); the revision rule is in
[`2026-08-24-the-identifier-still-says-cicada.md`](todo/2026-08-24-the-identifier-still-says-cicada.md)
— it moves everywhere at once as an announced spec revision, or not at all.

**Do not delete locust.** Suppression already keeps it out of the release, and the
port with its 1e-9 parity is worth keeping. ⚠ Note what that parity is and is not:
it measures this repo against interface2's MATLAB, **not** against CICADA —
`detector_history.md` §6.3 retracted the citability claim on 2026-08-29, and no
literature method has been run on these recordings
([`2026-08-17-run-a-literature-method-on-our-recordings.md`](todo/2026-08-17-run-a-literature-method-on-our-recordings.md)).

## The CLI has no seam to suppress through

`bugarach detect` still runs and emits locust while both viewers report it off in
this build. That is scoped deliberately — `ui/app.py`'s own docstring records the
2026-08-29 call as *"the port stands… and `bugarach detect` still runs it"* — so
this is not an incoherence to fix behind Tony's back. What the CLI lacks is the
*mechanism*: `detect_folder.DETECTORS` is also the allowlist, so removing a name
makes `--detectors cicada` a hard error rather than a default change. The
symmetric seam is a `SUPPRESSED` set beside the tuple, mirroring
`ui/app.SUPPRESSED_IN_VIEWER`, which keeps the detector reachable on request and
its calibration guarded.

## Open, and Tony's to decide

Whether the registry work happens before or after the locust decision. The argument
for *after* is that it is a day and the release does not need it. The argument for
*before* is that porting locust onto the record is what proves the record covers a
method whose inputs differ — and locust is the only such method the project has.

---

*Written 2026-08-29 at Tony's request. First draft's headline finding — that the
app hardcoded tube as the only reachable model — was false, and the murderboard
killed it: the quote was cropped one line above the comment that refuted it. The
run record is `docs/reviews/what_the_webapp_was_for_2026-08-29.md`.*
