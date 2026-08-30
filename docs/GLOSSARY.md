# Glossary — bugarach

Purpose: disambiguate terms that share words but mean different things. When
a term below is used in conversation, code, or specs, it means the referent
defined here. Inherits interface2's two-axis rule, generalized for bugarach's
generic streams.

## Vocabulary — two axes

Two independent axes. Each gets ONE word; the words do not overlap.

**AXIS 1 — STREAM (the signal):** a named per-ROI event stream on a slice.
Canonical stores carry exactly `fast` and `slow`; foreign data may carry one
stream or several under any names (`Slice.streams` is the iteration
surface). Use "stream", "per-stream". **RETIRED:** "modality"/"multimodal" —
they collide with the detector axis (inherited ban).

**AXIS 2 — DETECTOR (the algorithm):** which coordination detection method,
always by proper name:
  - **rate+context** (RateDetect port) — population-rate excess vs a slow
    context rate.
  - **CoactDetect** — distinct-ROI coincidence vs a rolling rate-local
    circular-shift null, per-bin z/p.
  - **LoCo** — distinct-ROI coactivity vs a rolling null-pool percentile
    threshold envelope.
  - **binned SCE** — surrogate-thresholded coactivity per trimmed region
    window (generate_sce port).
  - **locust** — sliding-window coactivity with per-cell roll null. Derived
    from the Cossart lab's **CICADA** (Denis et al. 2020) and **modified**, in
    both cases by changing what it is *fed* rather than what it computes: it gets
    the events already in the folder rather than running CICADA's own transient
    detection, and it gets each event's duration from the producer rather than
    measuring the whole transient the way the original does. **Duration is never
    derived here** — it arrives in `width_sec` under its `width_def` and the port
    paints what it is given (ADR-0002 addendum). **RENAMED 2026-08-24** — a
    modified port does not carry the original's name in a public UI (Tony's
    call, on interface2's ADR-0016: *"we can't say we used it if we turned off
    half of it"*).
  - **SPIKE-synch** — tau-capped **ISI-adaptive** SPIKE-synchronization profile
    (Kreuz lab) with hysteresis detection. The window is switchable:
    `tau_mode="isi_adaptive"` (default) or `"fixed"`. See **"adaptive" — never
    on its own** below.

A sentence must pick its axis: "all six detectors, both streams" — never
"multimodal".

## "adaptive" — never on its own

**RETIRED: bare "adaptive".** Tony, 2026-08-24: *"lots of things can be adaptive,
so include a word before or after for clarity."* In this project it has named at
least four unrelated things — a coincidence window, a time-scale floor, a rolling
detector threshold, and a plot's tick spacing — so a sentence using it alone
cannot be checked. `tau_mode="adaptive"` is **refused by the code**, with a
message naming the two candidates.

- **ISI-adaptive** — the coincidence window in SPIKE-synch. τ for a spike pair is
  the minimum of the four surrounding half-ISIs, capped at `tau_max`, so a dense
  stretch **tightens its own window** and the measure does not reward firing
  faster. This is core SPIKE-synchronization (Kreuz 2015), not an option on it,
  and it is what `adaptive_profile` computes by default. Its opposite here is
  `tau_mode="fixed"` — the cap for every spike, ordinary fixed-window coincidence
  detection, which makes the measure rate-dependent again.
- **MRTS — minimum relevant time scale** (Satuvuori et al. 2017). A **floor**
  under that adaptive window: time differences below it are not treated as
  resolvable, so the window cannot shrink past the scale you declare meaningful.
  It is cSPIKE's `threshold` argument to `AdaptiveSPIKESynchroProfile` — **which
  is where the word "adaptive" in that function name comes from**, and
  interface2's wrapper passed it as **0**, i.e. off. **Never on in this lineage
  and not implemented here**; `tau_mode="mrts"` says so rather than failing as a
  typo. ⚠ *Read from cSPIKE's API and interface2's wrapper, not from the
  Satuvuori paper — nobody here has read it.*
  **Why it is worth knowing rather than trivia:** with no floor, a burst of
  fast events drives τ below the frame interval, and the measure starts
  resolving differences the camera never recorded. An MRTS at the frame interval
  is the standard remedy. Nobody has checked whether our recordings do this —
  [filed](todo/2026-08-24-does-the-isi-window-go-below-the-frame-interval.md).
- **Adaptive threshold** (radar sense) — CFAR, an entirely separate axis with its
  own vocabulary further down this file. Nothing to do with either of the above.
- **`AdaptiveTicker`** — Bokeh's axis tick spacing in `ui/app.py`. Named here only
  so a grep for "adaptive" does not leave anyone wondering.

**locust versus CICADA, and it is one word apart.** *CICADA* in this repo means
the **upstream tool** — the Cossart lab's software, the thing we cite. *locust*
means **the detector here**: a **partial** port, because CICADA's per-cell
transient-detection stage is skipped entirely, and a **modified** one, because the
durations it paints come from the producer's export rather than from measuring the
transient itself. **The 1e-9 parity reaches interface2's `generate_sce_cicada`, not
the Cossart source**, so locust's numbers are never measurements of CICADA
([`detector_history.md`](detector_history.md) §6.3). The **code key is still
`cicada`** everywhere it is
an identifier: the module, `cicada_detect`, the fixtures, and the `detector`
column value in `detections.csv`, which is output contract and not this repo's
alone to change ([the identifier
todo](todo/2026-08-24-the-identifier-still-says-cicada.md)). So `which ==
"cicada"` in a file and *locust* on a screen are the same detector, deliberately.

## Parameter vocabulary — four things, four owners

Four groups of numbers in this project get called "settings" in conversation, and
they are four different things belonging to four different parts of it. Each
already has a specific name in the code; the vagueness was only ever in the prose
around it (Tony, 2026-08-22: *"settings can mean a ton of things even in this
app… let's start trying to be specific"*).

- **detector settings** — the parameter set one detector runs with. Keyed by
  **(detector, stream)**, because a detector may run differently on fast and slow
  and a record that could not say so makes one of the two unreproducible:
  `emit.detector_settings_rows`, `detector_settings.csv` in the export contract,
  `cfg` in the viewer. This is a **record of what a run used**, written as output
  so a result reproduces from the folder alone.
- **operating point** — a detector setting that was **chosen**, carrying the
  provenance of the choice: what it was fitted or benched on, at what tolerance,
  and what it scored. `bench.OPERATING_POINTS` declares the benched ones; the
  viewer's sweep fits new ones. An operating point *becomes* detector settings the
  moment a run uses it — the difference is that an operating point can say where
  it came from, and detector settings only say what was used.
- **generator spec** — the simulator's inputs: recording count, duration, ROI
  count, background rate and its shape, coordinated-event count, participation,
  jitter, windows, seed. `SIM_SPEC`, `run.json`'s `generator_spec`,
  `docs/learned/generator_spec.json`. Never "simulation settings".
- **training spec** — the trainer's inputs, on the lab server. `labSpec()`. It
  configures a fit; it is neither a detector's parameters nor a generator's.

Two more that are decisions rather than parameters, and should not be called
settings at all:

- **K** — the minimum number of participating ROIs an assessment reports at. A
  **scan, not a setting**: the assessor reports every K that clears the floor and
  refuses to pick one, because picking it is the analyst's call. It is the
  clearest case of why the instrument is [MAHDCE](#the-instrument-that-finds-coordination)
  rather than the machine alone — K moves the headline by an order of magnitude
  across the range the assessor scans, and no arithmetic chooses it.
- **tolerance** — the match window scoring uses to pair a detection with a planted
  event. One word; it needs no qualifier and should not acquire one.

**RETIRED: bare "settings".** It spans all four of the above and resolves to none
of them, so a sentence using it cannot be checked. Name which. The word is fine
inside a phrase that has already said which — "the detector settings above" — and
useless on its own.

**RETIRED: "corpus"** (Tony, 2026-08-22). The replacement depends on which one is
meant, and that ambiguity is half the reason it goes: a set of generated
recordings is a **simulated data set**; the real recordings the lab approved are
**the export folder**, which is what the input contract already calls them.

## The instrument that finds coordination

> **MAHDCE is this project's own coinage** — Tony, 2026-08-24, and he said in the
> same breath that he had just made it up. It is **not** a term of art, not a
> published method, and not something a reader will find in the literature. It is
> written down here because the thing it names is real and had no name, and
> because an acronym loose in a public repo without this paragraph beside it reads
> like a citation. **Anything outward-facing spells it out on first use and says
> whose word it is** — the same rule the detector attributions live under.

- **MAHDCE** — *machine-assisted human detection of coordinated events.* The
  instrument, and it is a **person and a program together**. The machine proposes
  candidate coordinated events and the statistics behind them; a person judges
  them; **neither half is the instrument on its own.** This is the reset's §1
  reversal given a name: there is no autonomous assessor, and a coordination
  number produced without anybody having looked at the recording is not a weaker
  result of the same kind — it is not a result.
- **the assessor** — the **machine half** of MAHDCE: `bugarach assess`,
  `assess_coactivity`, the browser's ported copy. It proposes; it does not
  conclude. Never *"the assessment says"* — an assessment is a record containing
  a judgement, and the judgement and the **view it was made in** travel with it
  (`annotations.csv`, `bugarach.annotate`).
- **the verdict** — a person's call on one candidate, carrying the recording, the
  rendering (`view_t0`/`view_t1`, ROI ordering, stream) and the observer. A row
  missing the view is **refused at write time**, because a judgement is a property
  of (recording × rendering × observer) rather than of the recording.

**The code keeps its names on purpose.** `assess.py` and `bugarach assess` are the
machine half and are correctly named for it; renaming them MAHDCE would give one
half the name of the pair and undo the distinction the term exists to draw.

## Data objects

- **slice** — one recording: N named streams + optional regions
  (`bugarach.store.Slice`).
- **store** — interface2's on-disk `event_store_onset*` `.mat` format
  (v7/v7.3), always fast+slow.
- **per-ROI events / trains** — the already-detected upstream event times
  the detectors consume. Never "detection" (that's the detector axis).
- **onset field** — which per-event time anchors analysis: `t50rise`
  (transient onset; explore_sce's choice) or `locs` (peak). Foreign data has
  only one time, stored as both.
- **extent** — `[t_lo, t_hi]`, union span of regions + every stream's
  `locs`; also the circular-shift wrap length.
- **region window** — a region's RAW bounds vs its TRIMMED stats window
  (aCa5z rule: backward-capped baseline, wash-in-delayed treatments, HiK
  exempt from the floor). "in stats window" = inside the trimmed window.
- **grid_dt** — the rate-trace grid; must be the acquisition sampling
  interval (see FOUNDATIONS §6).

## Detection vocabulary

- **episode** — threshold-mode detection unit (supra-threshold bins merged
  by a gap rule). **peak mode** — half-prominence peak-gated alternative
  (shared kernel in `detectors/peaks.py`).
- **width_kind** — what `width_sec` means, self-describing per mode:
  `tightness` / `episode_span` (event-time spread) vs `half_prominence`.
- **coactivity** — distinct active ROIs per bin/window (one count per ROI),
  never a spike count.
- **saddle** — the extent bound in the peak kernel: minimum-valued run
  between a peak and its nearest equal-or-taller peak (spec rev 2).
- **hilite** — signal-contract field: time spans where the raw criterion is
  met pre-merge (rate+context).

## Adaptive-threshold vocabulary (borrowed from radar)

Introduced by [`detector_history.md`](detector_history.md), which argues that
three of the six detectors are re-derivations of this design space. Listed here
so the words mean one thing.

**That argument is no longer a reading — it is the attribution.** This paragraph
used to say the attributions were "flagged unverified and nothing below depends
on them", which was true when it was written and stopped being true twice: two of
the radar primaries were retrieved and read on 2026-08-22, and an interface2 audit
on 2026-08-24 closed every lineage row — `rate_detect` is cell-averaging CFAR
(Finn & Johnson 1968), `loco_detect`'s `maxlt` is GO-CFAR (Hansen 1973), and its
percentile-of-pool is kin to OS-CFAR (Rohling 1983). **The words below name what
these detectors are, not what they resemble.** None of it is a problem — priority
is closed (Tony, 2026-08-24) and the reason to care is the engineering the radar
literature is offering, which
[the attribution note](todo/2026-08-24-the-methods-are-not-ours-and-the-app-says-otherwise.md)
sets out.

- **CFAR** — constant false alarm rate: set the threshold from an estimate of
  the local background so the false-alarm probability stays put as the
  background moves. A family name, not one algorithm.
- **cell under test** — the moment/bin whose statistic is being compared to the
  threshold. bugarach's names for it: LoCo's *anchor*, CoactDetect's *bin*,
  rate+context's *primary window*.
- **reference cells** — the neighbouring data the background estimate is built
  from. bugarach's *context window* is a reference window.
- **guard cells / guard interval** — reference cells immediately around the cell
  under test, **excluded** so the event cannot inflate the threshold it must
  clear. This entry read *"bugarach has none; that absence is the finding"* until
  2026-08-28, and was true for one day: guard cells landed on the two surrogate
  detectors the morning after it was written (`a15f5e3`). **Three of the six now
  take a `guard_sec`** — CoactDetect, LoCo and rate+context — and it defaults to
  `0.0` on all three, with no operating point in `bench.OPERATING_POINTS` setting
  it. So the capability exists and **nothing ships with it on**, which is a
  different statement from either "has none" or "has them"; say which one you
  mean. Where it lands and what it costs:
  [`docs/reviews/guard_prior_art_2026-08-26.md`](reviews/guard_prior_art_2026-08-26.md).
  **Not to be confused with a `clamp`**, which bounds a *fitted parameter* to a
  range in `learn/nets.py`. A guard excludes data from a background estimate; a
  clamp bounds a number during fitting. Different objects, different stage.
- **self-masking / mutual masking** — an event raising its own bar; a second
  event inside the reference window raising it further.
- **greatest-of / ordered-statistic selection** — combination rules for the
  reference estimate. LoCo's `maxlt` is greatest-of; its percentile-of-pool is
  kin to an ordered statistic.

## Validation vocabulary

- **oracle** — MATLAB reference output (generated by `tools/matlab_ref/`)
  that parity tests compare against; "MATLAB-exact" means bit-matching it.
- **parity** — agreement with the oracle to 1e-9 on committed synthetic
  fixtures (and locally on real slices).
- **clean-room primary / adversary** — the two independent implementers in
  `docs/clean_room/WORKFLOW.md`; they never see each other's code.
- **sapper** — the mechanized rule gate (`tools/sapper.py`); a rule must
  prove it can fire (self-test fixtures) to exist.

## Bench and simulation

Terms used by `bugarach.bench`, `bugarach.simulate` and
[`generator.md`](generator.md). Added 2026-08-14, when a review found six
load-bearing terms with no glossary entry.

- **regime** — a named background-activity level the bench runs at. Both are
  derived from untreated recordings: `baseline_quiet` (0.0052 Hz/ROI, the p25 of
  baseline slices) and `baseline_busy` (0.0190, the p75). Treatments are never
  regimes. Re-derived 2026-08-20 from the export folder — the recordings the lab
  approved — having been fitted against the `.mat` store, which carries the two
  recordings the lab withdrew.
- **operating point** — the parameter set a detector is benched at, declared with
  its provenance in `bench.OPERATING_POINTS`. Not the same as its signature
  defaults, which are not all calibrated. The general sense — a *chosen* detector
  setting that carries where the choice came from, benched or freshly fitted — is
  under **Parameter vocabulary** above, with the three terms it is confused with.
- **promiscuity probe** — a stretch of the synthetic recording with elevated
  background and *no* planted events, used to see whether a detector keys on
  rate rather than on coordination. Its firings are reported separately and kept
  out of headline precision.
- **distractor** — a planted correlated burst: real cross-ROI coincidence that is
  not a coordinated event. A negative that is meant to be confusable.
- **contaminated null** — a surrogate null estimated over a context window that
  contains real coordinated events, which inflates the threshold. Avoided by
  spacing events wider than the widest context window.
- **participant floor** — the recruitment level below which a detector stops
  finding events. Reported as recall broken down by participation fraction.
