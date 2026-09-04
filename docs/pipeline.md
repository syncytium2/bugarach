# The pipeline — the loop bugarach runs

> **Working material, not murderboarded.** Same standing as `run_records.md` and the
> handoff: for sessions in this tree. Nothing here is written for an outside reader; if
> any of it becomes one, murderboard that artifact first.

**Dictated by Tony on 2026-09-04, one step at a time, each row corrected before the next
was taken.** [`RESET.md`](RESET.md) §2 holds his 2026-08-24 statement of the same loop and
stays as the record of what was said then. This page is the walked version: the steps
named, what each one owns, and what is actually built behind it.

**No counts here.** `pytest -q`, `python3 tools/sapper.py --all`, `git rev-parse --short
origin/main`. A number written into a page nothing recomputes is a promise nobody is
keeping, and this repo has watched that go wrong twice in three days.

---

## Two modes, one pathway

There are two ways to run this loop and **they must walk the same steps**:

- **Orchestrator mode** — Tony says what he wants and a Claude Code session walks it.
- **Webapp mode** — Tony or a new user walks it unattended in the browser.

The code underneath differs in places — the browser carries its own ported detectors and
its own scan — and that is accepted. **The pathway does not differ.** Where the two have
drifted, that is a defect and is listed under the step it belongs to.

**They converge on the webapp for MAHICE.** There is exactly one surface on which a person
judges coordinated events, and it is the browser. Orchestrator mode drives up to that step,
hands off, and resumes from `annotations.csv` and `mahice.json`. **No rendering-to-judge in
a chat window, ever** — if judging needs a better picture, the fix goes into the webapp.

---

## Open a folder

**The user's recordings, and nothing else.** One file per slice holding the times of events
for each ROI. The user may also give duration and amplitude per event.

A **sidecar carries the treatment timings**. When there is none, the recordings are taken
as baseline throughout — and **the folder is made to say so**, as a `baseline` region
spanning each recording. Today a folder without timings simply has no regions, which is not
the same claim and leaves the baseline-only restriction below with nothing to select on.

The sidecar may also carry **analysis windows** — which parts of the data are to be
analysed. Where the producer sent none, the user defines them from three deltas relative to
the treatment timing: a baseline measured backward from its end, and a treatment that skips
a wash-in delay and then runs for a stated length.

Two choices are the **user's**, made here and recorded:

- **Restrict optimisation and training to baseline only.** Default on. Treatments are what
  the instruments are pointed at, and taking coordination properties from them assumes the
  answer (FOUNDATIONS §9).
- **Detection scope** — run detection over the whole trace and cut the output to the
  analysis windows, or run it within each baseline and treatment separately.

**The user decides what is appropriate for their data.** Both choices apply to every
detector. We warn where a choice has a consequence; we never refuse.

**Built.** Conformance checking in both modes. Optional per-event duration and amplitude.
Optional sidecars — a folder of nothing but event files is a valid input. The three-delta
window interface, **in the browser**, including the rule that a window the folder sent is
never overwritten.

**Owed.**

- The baseline default, written as a region rather than left as an absence.
- The three deltas in Python. The browser has them; the library does not. **This is the
  first place the two modes diverge.**
- The scope choice. Today it is decided per detector, not by the user: `loco`, `sce` and
  `cicada` scan the whole recording and tag each event with the period it fell in; `rate`,
  `coact` and `sync` run once per declared window so their rolling context stays inside one
  condition. Both behaviours exist; neither is offered. Giving `rate`, `coact` and `sync` a
  whole-trace path lets their context span a treatment boundary, and that is the warning
  the user gets — not a veto.
- Both choices into the run record.

---

## MAHICE — propose, judge, set K

**Assessment must include the user.** *Machine-assisted human identification of coordinated
events.* The machine proposes candidate coordinated events and the statistics behind them;
a person judges them; **neither half is the instrument on its own.** No detector is
involved — this is the stream axis only.

The person sets **K as a percentage** of each recording's ROI population, once per review,
never a different one per slice. The absolute count then follows each field size on its own,
which is what makes one setting fair across recordings running 10 to 51 ROIs.

A coordination number produced with nobody having looked is not a weaker result of the same
kind. **It is not a result.**

What is recorded: the verdicts, **the view they were made in**, the percentage, who set it,
and the ROI counts it resolved against.

**Built.** The machine half in both modes, pinned by a parity test. The human half in the
browser — judge, then set K as a percentage — since #469, 2026-09-04. Python reads back
what the browser writes.

**Owed.**

- **Nobody has run this on the approved export folder.** No K is set for it. That is expert
  attention, not compute.
- The browser proposes candidates at K≥3, so **its own labels can never validate a smaller
  K** — the cross-check reports that honestly rather than returning the floor as an answer.
  Closing it means the scan reaching down to 2 on both sides at once.

---

## Derive the spec

**Establish the parameters for the simulator from MAHICE and from properties of the user's
own data.** Nothing inherited from this laboratory.

The generator is set from four quantities — **rate, cluster, participation, jitter**.

- **From the data, baseline only:** baseline event frequency, per-ROI rate heterogeneity,
  and **burstiness** — fitted at several time scales, because burstiness is scale-dependent
  and one scale cannot carry it.
- **From MAHICE:** K becomes participation; the confirmed events give the coordinated-event
  rate, span and tightness.

The spec records how K got its value, so a consumer can tell *a person set 10% while
looking at the recordings* from *3 is where the labels happen to separate*.

**Built.** Rate derived from the assessment. Participation, span, tightness and jitter from
the confirmed events. The K provenance field.

**Owed.**

- **Burstiness is an inherited constant.** The tool says so in its own note — *"Still
  inherited — the assessment does not yet fit this one per folder."* Per-ROI rate
  heterogeneity is inherited too when the folder has too little baseline to fit one, and
  its note calls it *"a constant standing in for a measurement."*
- Fit both from the user's own baseline, and fall back only when the folder cannot support
  a fit — saying in the spec which happened. On a stranger's preparation an inherited
  burstiness is not conservative, it is wrong.

---

## Simulate and validate

**Simulate a data set, and confirm interactively that it resembles the user's data.** The
machine reports both sides; the person decides. **This may become recursive** — the user
modifies the extracted parameters to improve the fit, re-simulates, and compares again.

**The division from detection is deliberate.** The user does not see detection output until
the simulation parameters are settled, so the simulation cannot be tuned toward a detection
result somebody liked. Going back afterwards is allowed and is **a conscious decision** —
therefore it is recorded, not silent.

**Built.** Simulation writes a conforming folder. The comparison reports rate, cluster,
participation and jitter with a measured value from each side, and **delivers no verdict**.
A simulated data set aimed at a real measurement and never checked **says so on the rail,
every time it paints, until somebody looks** — it does not block, because the check has no
verdict to enforce.

**Owed.**

- **Gate the detection steps on the simulation being validated.** Today `Detect` and the
  scoreboard are reachable the moment a folder is open, which is exactly what the division
  exists to prevent.
- **Per-parameter provenance.** K carries its source; no other knob does. The moment a user
  hand-modifies rate or burstiness, nothing records that it was hand-set, and every
  downstream number then inherits a generator shaped partly by preference while the spec
  still reads like a measurement. Each knob needs: derived, inherited, or hand-set, and by
  whom.
- A spec revised **after** detections were seen carries that fact.

---

## Tune

**Two branches — the coded detectors and the tube variants — both tuned here, both selected
by the user.** Modular on each side: a new architecture, a user's own model, or three
variants run in parallel, without editing the pipeline around them.

**Built.** The learned branch is a real registry: one file per architecture, auto-imported,
*"a dropped-in file registers with nothing else edited and no list of names exists
anywhere"* (ADR-0005). The browser's model picker is multi-select and comes from that
registry, and selecting every architecture trains every architecture — **variants in
parallel already works on this side.** The bench scores detectors that are not in the
calibrated set, so the learned branch reaches the same scoreboard. Per-detector ticks, with
the costly ones marked.

**Owed.**

- **Nothing persists a trained model.** No checkpoint is saved anywhere. A user cannot bring
  a trained model, and a variant trained here cannot survive to be tested or to detect.
  **This blocks three later steps and is the single most upstream item on this page.**
- The coded branch is one dictionary plus hand-maintained tables in a second module, not a
  drop-in folder. Either give it the same shape or state that the six are fixed.
- ADR-0005's open decisions belong here: **knobs as data, controls rendered rather than
  written** — which is what makes a user-supplied detector's controls appear at all — and
  **user files loaded Worker-sandboxed**, which is bring-your-own-model.

---

## Test on a fresh batch, compare

**Take the tuned detectors and compare their performance on held-out data.** The user
specifies how many simulated slices are used for tuning and how many for testing, with
smart defaults.

**Built.** The fairness rule is load-bearing and came from a real defect: the six once
reported an at-home, in-sample number while the learned models were scored on held-out
seeds, so one side of the comparison was an optimum and the other was not. Now the
operating point is chosen on a calibration fold and scored on a held-out fold, and
**nothing is tuned on one distribution and scored on another**. Every number is reported
across folds **with its spread — intervals, not rankings**. Fold and seed counts are already
parameters, and a genuinely separate test set is available by drawing the held-out fold from
a second generator spec.

**Owed.**

- The browser exposes the fold count; **seeds-per-fold and the training count are not
  exposed** in either mode's interface.
- **The defaults are fixed constants and nothing about them is smart** — and this is not a
  cost knob. Measured here: across twelve seeds one detector won every grid point by
  0.0011; across the next twelve, a different one took the busy half. **The ordering flips
  with the seed block.** A three-seed setting was called noise-dominated by its own author.
  So a default has to come from a stability criterion, and the page has to be able to say
  *these are not separated* instead of printing an order.

---

## Detect on the real folder

**Run the user-selected detectors on the user's data folder.**

**Built.** Works in both modes and writes the detections, the per-detector settings, and the
run record. Detector selection exists in both. Every row carries the producer's own region,
and the run summary says how many detections landed in no declared period.

**Owed.**

- **Tuning does not reach detection in orchestrator mode.** The library's detect path takes
  its parameters from the calibrated operating points and has no argument for a settings
  file. The browser can apply a tuned setting to the user's folder; the command line cannot.
  **This is the second place the two modes diverge, and it is the one that matters most** —
  it makes the whole Tune step unreachable from one of the two paths.
- **The tube variants cannot run on the user's data at all.** The detect path knows the six
  and has no route to the architecture registry. With nothing persisting a trained model, a
  tuned variant has no way back to the folder it was tuned for. The two branches settled at
  Tune merge back into one here.
- The scope choice and the validation gate, both settled earlier, land here unbuilt.

---

## Output — figures and the coordinated-event table

**Our job is detection.** We provide well-formatted, easy-to-evaluate output that lets the
user judge the success or failure of each detector quickly, for each slice, group and
treatment. The statistics on top of it are the user's.

**Figures.** One detector row each, per slice / group / treatment. Publication quality
eventually; for now the summary page — rows are recordings, `FAST` beside `SLOW`, every
recording re-zeroed at the end of its own baseline so the treatment onset is one vertical,
treatment regions in a lane above each raster, per-region counts in the margin.

⚠ **There is no ground truth on the user's folder.** Success and failure there are a
person's judgement from looking, not a computed score — the quantitative comparison already
happened, on simulation. A mark on a real raster is a claim, not a verdict: no ✕, no
scoreboard, no F1.

**The table.** One row per **coordinated event**:

| column | what it is |
|---|---|
| `slice_id`, `group_id` | identity, so the figure's grouping is reproducible from the table |
| `stream` | fast and slow are different measurements and must never be merged |
| `detector` | one row per event per detector |
| `onset_sec` | time |
| `width_sec` | the detector's own width |
| `strength` + `strength_unit` | the detector's own amplitude, in its own unit |
| **universal amplitude** | **peak coactivity in #ROIs** |
| **universal width** | **participant onset span, in seconds** |
| `n_roi` | participants, explicitly missing for the one detector that reports none |
| `region_idx`, `region_label` | the producer's own index and name, carried unchanged |
| K, detection scope | the same folder gives different numbers under a different scope |

**The universal amplitude is what makes the detector rows comparable.** Each detector's own
`strength` is in its own unit — a rate in Hz, a z-score, a coefficient, and two different
ROI counts — so those values cannot be read across rows. Peak coactivity in #ROIs and
participant onset span in seconds belong to the recording rather than to any detector, which
is why they are the axes a reader can compare on.

**ROI events are not re-exported.** The user gave us those. Tagging each ROI event with the
coordinated event it belongs to is a **v2 stretch goal**.

**Owed.**

- Compute the universal amplitude and width **for a given detector's detections**. Both
  quantities exist and are already computed for the assessment's own clusters and for
  MAHICE-confirmed events; nothing yet applies them to an arbitrary detector's output. The
  coactivity trace is detector-free and already there, so this is a function, not a research
  question.
- The summary page in the shape above.
- For v2 tagging, note that **the assessor already knows the membership** — which ROIs made
  up each observed cluster — while **none of the six detectors reports it**. Five report only
  how many took part; three build the participating set internally and hand back its size.
  Those are different facts and the difference is where v2 starts.

---

## What blocks what

Two items sit upstream of most of the rest:

1. **Model persistence.** Nothing saves a trained model, so the learned branch cannot be
   tested on a fresh batch, cannot detect on the user's folder, and cannot accept a model
   the user brings.
2. **A settings file the library's detect path will read.** Without it, tuning reaches the
   browser and not the command line, and the two modes stop being one pathway at the last
   step before output.

Everything else on this page is additive to a loop that already runs.
