# bugarach

[![CI](https://github.com/syncytium2/bugarach/actions/workflows/ci.yml/badge.svg)](https://github.com/syncytium2/bugarach/actions/workflows/ci.yml)
&nbsp;·&nbsp; [bugarach.tonydefazio.com](https://bugarach.tonydefazio.com)

**Find the moments when many cells fire together — and measure how often you are
wrong.** bugarach lifts six coordinated-event detectors out of MATLAB, plants
events in simulated recordings so a detector can be scored against what was
actually there instead of against another detector's opinion, and trains a small
network on that simulation. It reads one folder of event times, so a lab that has
never heard of this project can point it at its own recordings.

Its input is a list of event times per **ROI** — one region of interest, meaning
one cell's worth of signal pulled out of a calcium-imaging movie by whatever
software you already use. Everything below works from those times and nothing
else. The quickest look costs nothing: the
[raster viewer](https://bugarach.tonydefazio.com/viewer.html) draws a folder of
them in the browser, with no upload and nothing installed.

![The bugarach viewer: two stacked panels, one per stream, each with a 30-row event raster above three detector traces sharing its time axis](docs/screenshot.png)

> **The name.** Pic de Bugarach is the mountain in the French Pyrenees that doomsday
> believers converged on for the 2012 Mayan-calendar apocalypse, convinced it alone
> would be spared. The world did not end; the village had to restrict access to the
> summit. A coordination detector is a machine for deciding whether an alignment is
> real — this repo is named for the people who decided without one.
> (Team constellation, alongside `syzygy`, `murmuration`, `fireflies`.)

## The idea: an instrument built for your recordings

**Coordination is not one phenomenon, so there is no one detector to train.**
Stars coordinate and cells coordinate, and between them the timescales run over
many orders of magnitude — along with the sampling rates, the mechanisms, and what
counts as an event at all. A network trained across every source of coordination
spends its capacity on a space in which almost nothing transfers. Worse for a
working lab: what it learns is the average case, so the preparation that departs
from the average is the one it scores as noise.

So the instrument gets built per lab, in a loop:

1. **Measure** an *untreated* recording — without using a detector, so no
   detector's opinion can leak into what follows (`bugarach.assess`).
2. **Simulate** from that measurement alone, planting events at known times with
   known participants (`bugarach.adapt` → `bugarach.simulate`).
3. **Tune and train** on that synthetic baseline: the six detectors get their
   operating points, the network gets its weights (`bugarach.bench`,
   `bugarach.learn`).
4. **Detect** — and only now is the finished instrument pointed at the whole
   dataset, treatments included.

Simulating the treatment would spend the effect you ran the experiment to
measure. Withholding it is what lets the effect come back as a result.

That loop has been run end to end exactly once, on this lab's own eighty-five
recordings — the bake-off below is its output. No outside lab has taken it round
yet, so read the last step as the shape of the thing rather than a road already
traveled.

## What is built

The MATLAB originals — `explore_sce` and the detectors, generator and scoring
suite around it — live in **interface2**, this lab's analysis repository. It is
private, so it is named here as the source of a port and never linked; nothing in
this repo needs it to build, run or be tested.

| | |
| --- | --- |
| **Six detector ports** | rate+context, CoactDetect, LoCo, binned SCE, CICADA and SPIKE-synch — each matched to its MATLAB original **to 1e-9 in every detection mode**, on committed synthetic fixtures and on a real slice locally. That is what makes them citable in the originals' place. |
| **Peak gating** | The half-prominence extent kernel the peak-gated mode needs, written **clean-room** from a spec and validated against an independently built adversary implementation. |
| **A generator with ground truth** | Coordinated events planted at known times in per-ROI background activity, so a miss and a false alarm are counted rather than argued about (`bugarach.simulate`, from interface2's `generate_synth_coord.m`). |
| **A scorer that reads intervals** | Binned detectors report a bin's left edge; matching that edge against a planted onset scored a correct detector at **0.00 recall on fourteen detections that each spanned a planted event**. Detections are matched as intervals, greedily, closest pair first (`bugarach.score`). |
| **A bench with two refusals** | It will not run a detector at whatever its signature happens to default to — CoactDetect scores F1 0.72 that way against 1.00 at its calibrated point — and it will not report an optimum sitting on the edge of the grid it searched (`bugarach.bench`). |
| **A detector-free assessment** | Measures how much coordination a recording holds against a rate-matched null, with no operating point to tune, so it can set the generator's priors without closing the circle (`bugarach.assess`). |
| **Learned detectors** | A new architecture is one class and one `@register` line; it is then trained on the same data, scored by the same scorer, and placed on the same accuracy-versus-cost curve as everything else (`bugarach.learn`). |
| **The viewer** | Panel/HoloViews: per-stream raster, one signal row per detector, x-linked, live recompute. Streams are generic — `fast`/`slow` is this project's convention, not the viewer's, and a one-stream recording is the default presentation. |
| **The way in** | One folder of CSVs, [specified in full](docs/export_folder_spec.md): the event times of each ROI, the timing of each period, the acquisition frame interval, and no fourth fact. `bugarach check` tells a producer whether their folder conforms, `bugarach assess` measures how coordinated the recordings are without any detector's opinion in the answer, and the [browser raster viewer](https://bugarach.tonydefazio.com/viewer.html) draws it without the files leaving their computer. |

**What is not built: a result you can take away.** Point the viewer at a folder,
tune the detectors, and the events stay on the screen — there is still no
`detections.csv`, one row per coordinated event, that an analyst could open in
anything else. The benchmark tools write their own JSON, but the detection path
writes nothing. That writer is the next milestone in
[`docs/workflow_plan.md`](docs/workflow_plan.md), which also carries the build
order and the one stage that is blocked.

## What six detectors do with a known answer

Every coordinated event here was planted, so a hit, a miss and a false alarm are
drawn rather than argued about. Forty-five minutes of simulated recording, and
what six detectors made of it:

![One lane per detector above a 33-row event raster and six analysis traces. Inside the shaded block, the CICADA and binned SCE lanes are packed solid with detections while the LoCo lane is empty](docs/generator/coord_diagnostic_bench_quiet_hero.png)

Top row, the answer: ▲ a planted event some detector recovered, ▽ a distractor — a
correlated burst that is real coincidence and not a coordinated event. Then one
lane per detector, each bar a call it made, ✗ a false alarm and ○ a second call on
an event another detection had already claimed. Then the raster all six were
reading, one row per ROI, **every onset drawn the same** — which of them a
detector gathered into an event is not marked, because none of them reports that:
they report a window, and that is what the lanes above draw. Below the raster,
what each detector computes from it, with its own threshold drawn on where it has
one: four of the six do.

**The shaded block is the trap.** It fires faster than the rest of the recording
and contains no planted events at all, so every bar inside it is a false alarm by
construction — it is there to catch a detector that keys on how much is happening
rather than on how much of it is together. Two take the bait plainly: CICADA fires
85 times inside it and binned SCE 28, while LoCo and CoactDetect — the two that
score best on this run — fire not once.

Read that as a promiscuity *report* and not as a penalty. Firings inside the block
leave both the numerator and the denominator of the scores below, so at present
they cannot cost a detector anything — which is
[recorded as a defect](docs/todo/2026-08-16-promiscuity-probe-cannot-fail.md)
rather than dressed up as a result.

[**The annotated version**](docs/generator/coord_diagnostic_bench_quiet.png)
carries the full legend and each detector's scores;
[the interactive one](https://bugarach.tonydefazio.com/diagnostic.html) lets you
zoom a false alarm. Both rebuild with:

```bash
python tools/make_diagnostic.py --bench baseline_quiet --seed 3 --scale 2 \
    --out docs/generator --tag bench_quiet \
    --hero docs/generator/coord_diagnostic_bench_quiet_hero.png
```

The flags are not decoration — without them it renders at a different scale and
writes to the darkroom rather than to the two files this page shows.

## The bake-off — same data, same scorer, held-out folds

Eighty-five real baseline recordings were measured without a detector; one
generator spec was derived from that measurement; every detector was then
calibrated or trained on three quarters of the resulting simulated data set and
scored on the quarter it had never seen, all four rotations. **F1** is the usual
harmonic mean of recall (what fraction of planted events were found) and precision
(what fraction of calls were real), so 1.0 is perfect and a detector can reach it
only by finding everything and inventing nothing.

![Panel A, a bar per detector showing F1 with its four individual folds drawn as dots; panel B, the same F1 plotted against seconds to detect on a log axis, with the learned models in red](docs/learned/bakeoff.png)

| detector | F1 (mean of 4 folds) | fold range | detect s | params |
| --- | --- | --- | --- | --- |
| **center−surround (learned)** | 0.668 ± 0.061 | 0.58–0.73 | 0.014 | 1,149 |
| CoactDetect | 0.651 ± 0.044 | 0.61–0.71 | 0.060 | — |
| LoCo | 0.638 ± 0.053 | 0.57–0.70 | 0.245 | — |
| rate+context | 0.571 ± 0.085 | 0.46–0.65 | 0.005 | — |
| CICADA | 0.541 ± 0.070 | 0.47–0.63 | 0.114 | — |
| binned SCE | 0.422 ± 0.083 | 0.31–0.49 | 0.011 | — |
| SPIKE-synch | 0.254 ± 0.065 | 0.21–0.34 | 0.094 | — |
| pooled trace (learned) | 0.131 ± 0.012 | 0.12–0.15 | 0.015 | 2,065 |
| per-cell bank (learned) | 0.125 ± 0.000 | 0.12–0.12 | 2.453 | 2,393 |

`detect s` is wall-clock to scan one held-out fold — two recordings, about 118
minutes of data.

**The top three are a tie, and should be read as one.** Four folds of thirty
planted events cannot separate 0.668 from 0.651; the fold ranges overlap, and the
figure draws every fold so that is visible rather than hidden behind a bar. The
claim the numbers support is that a 1,149-parameter network **reaches the level of
the best hand-written detectors here**, having been given no more information than
they were — and then detects four times faster than CoactDetect and seventeen
times faster than LoCo, from 5.6 seconds of training. It is **not** the fastest
detector here: rate+context scans the same fold in 0.005 s, roughly three times
quicker again, and sits 0.10 of F1 below.

⚠ **What this does not establish.** Eight recordings, four folds, one training run
each — the intervals above are fold ranges, not confidence intervals, and seed
variance within a fold was never measured. The two learned models at the floor land
their threshold on the low edge of the searched grid, which this project treats
elsewhere as a search that stopped too early. The data set rests on one human choice
— how many clusters the assessment was read at — and a different choice halves the
event rate and builds a different benchmark. And the recordings are simulated:
their settings were measured from real ones, but **nothing here says any detector
is right about a real slice.** Full run, with the figures and the rest of the
caveats: [`docs/learned/bakeoff.md`](docs/learned/bakeoff.md).

## Where the imitation stops being convincing

![A real recording above, the generator's imitation below](docs/generator/reality_check.png)

> ⚠ **The one figure here still using the old raster convention.** It inks the
> onsets inside a window LoCo called and mutes the rest; every other raster in
> this repo now draws each onset identically. It is also the only figure that
> cannot be rebuilt without the real archive, so it lags on purpose rather than
> by oversight.

The ROI count, the duration, the per-ROI rate, the participation and the jitter
are the same in both panels. The texture is not: a real field has a few ROIs
carrying most of the activity and many carrying almost none, and what activity
there is arrives in bursts, while the generator spreads events evenly across every
ROI and across the whole recording. Run the same detector at the same settings on
both and **LoCo finds 5 events in the real recording and 10 in the imitation** —
matching the rate, the jitter and the participation is necessary and not
sufficient. The gap is open work, written down rather than papered over.

That the gap matters is not hypothetical here. Detector settings tuned on a dense
benchmark — a coordinated event every 14 s — collapsed when the same settings met
sparse data, because four planted events sat inside every 60 s context window and
contaminated the null the detectors depend on. Binned SCE's precision fell from
74% to 10%, and finding out cost two weeks. Both benchmarks were synthetic, which
is the point: a simulator that does not match the recordings can mis-tune a
detector all by itself. `tools/regime_shift.py` is that failure turned into an
assertion that fails a test run rather than a field season.

## Where this sits, and who else is doing it

Three groups already train networks whose output is a population event with times
— [DOSED](https://github.com/Dreem-Organization/dosed) on sleep EEG,
[cnn-ripple](https://github.com/PridaLab/cnn-ripple) on hippocampal LFP, and SEED
on sleep spindles. None works on calcium imaging, and all learn from events a
human expert labeled. What differs here is the substrate and where the answers
come from: the events are planted in a simulation fitted to one lab's own
recordings, so the ground truth is exact and the benchmark is rebuilt per lab.
The classical side of the same problem is
[CICADA](https://gitlab.com/cossartlab/cicada) and the coactivity-versus-shuffle
rule it comes from — both among the six ported here.

**No method from the literature has been run on this project's recordings**, so
nothing here claims to beat one. The reading behind that paragraph — which papers
were read closely and which were deliberately not opened — is on the site as
[the landscape](https://bugarach.tonydefazio.com/landscape.html), built from
`docs/learned/landscape.src.html`.

## Install

Requires Python ≥ 3.11.

```bash
python3 -m venv .venv && source .venv/bin/activate
pip install -e ".[ui]"        # viewer;  [dev] adds pytest,  [dl] adds torch
```

## Use

**An export folder is the documented way in.** One CSV per recording, named by the
recording, plus two small tables a lab keeps like a notebook:

```
my_export/
  20240708_13.csv     roi,time_sec[,stream]      <- 7,NA means ROI 7 fired nothing
  20240708_17.csv
  slices.csv          slice_id,frame_interval_sec,+ any identity columns
  regions.csv         slice_id,region_idx,label,start_sec,end_sec
```

Only the recording files are required; each table buys one thing. Analysis windows
arrive **already computed** and are used verbatim, because how to trim a window
encodes one lab's protocol rather than a universal rule — re-deriving them would
trim twice. Nothing in the contract is specific to a lab, a preparation or a
pipeline; bugarach never decides which ROIs were healthy enough to keep, since
only whoever ran the experiment can; and extra columns are carried through rather
than rejected. Full contract:
[`docs/export_folder_spec.md`](docs/export_folder_spec.md).

```bash
bugarach check my_export/          # does this folder conform? exit 0 or 1
bugarach assess my_export/         # how coordinated is it? no detector involved
bugarach view  my_export/          # one recording per page, detectors on top
bugarach view  my_export/ --raster-only    # just the events, nothing computed
bugarach view  path/to/store.mat   # or an events CSV, or a directory of either
```

From Python there are three ways in — an export folder, one of this lab's stores,
or plain arrays of times — and all three produce the same `Slice`:

```python
from bugarach.io import load_folder, slice_from_events
from bugarach import load_slice

slices = load_folder("my_export")                     # -> a list of Slice
s = load_slice("tests/fixtures/synth_fastcal_s1.mat")  # -> one Slice
s = slice_from_events([roi0_times, roi1_times])        # -> one Slice, from arrays

# whichever way it arrived, a Slice answers the same questions:
s.streams                        # generic name -> Stream mapping
s.fast.n_rois, s.fast.n_events   # canonical-store accessors
s.fast.t50rise[0]                # ROI 0's event ONSETS (sec) — what detectors read
s.fast.locs[0]                   # the same events' PEAKS, which lag the onsets
s.regions                        # annotated time windows (optional)
```

Then run a detector:

```python
from bugarach.detectors import loco_detect

det = loco_detect(s)
fast = det.streams["fast"]
fast.onset_sec, fast.width_sec, fast.width_kind    # width_kind says what width MEANS
```

**All six answer in the same shape**, which is the point of the port rather than a
coincidence of it: a statistic trace, the events found in it as an onset and a
width, and `width_kind` saying what that width measures — in whichever of the two
detection modes you asked for, supra-threshold or peak-gated. That contract is
interface2's `detector_output_spec.md`, and it is what lets one scorer, one bench
and one viewer drive all six with no special case for any of them. Scoring the
whole set against planted truth is therefore a loop, not six branches:

```python
from bugarach.bench import run_detector
from bugarach.score import score_stream
from bugarach.simulate import simulate_coordination

sim, truth = simulate_coordination(seed=1)
for name in ("rate", "coact", "loco", "sce", "cicada", "sync"):
    det = run_detector(name, sim)                 # by name, not by signature
    print(name, round(score_stream(truth, det).f1, 2))
```

Two differences survive underneath the contract, and each has something that
absorbs it. LoCo, binned SCE and CICADA take a whole slice because they window by
region, while rate+context, CoactDetect and SPIKE-synch take one stream's trains
and an extent — `run_detector` hides that split, though only for single-stream
recordings like the generator's, so the viewer keeps its own dispatch for stores
carrying several streams. And the two earliest ports spell the event fields
`locs`/`widths` rather than `onset_sec`/`width_sec`, a scar of port order and not a
difference in meaning — `score_stream` reads either spelling, and scores a binned
detector by its spans instead of mistaking a bin edge for a miss.

⚠ **The acquisition frame interval is the caller's responsibility, and only one of
the three detectors that need it will tell you.** Event times do not carry the
interval the analysis grid is built from, so `rate_detect` takes `grid_dt` and
**warns** when it is missing instead of defaulting in silence — while `sync_detect`
(`dt`) and `cicada_detect` (`imaging_rate_hz`) assume 10 Hz without a word. A lab
imaging at 20 Hz gets one warning and two quietly wrong answers. That is why the
export folder, whose `slices.csv` carries the interval, is the preferred way in;
why the gap is [written down](docs/todo/2026-08-16-dt-does-not-travel-with-the-recording.md)
rather than left to be rediscovered; and why the warning must never be silenced.

The per-lab loop runs as four scripts, each writing what the next one reads:

```bash
python tools/assess_archive.py --store <dir> --out docs/learned   # measure, no detector
python tools/derive_spec.py --assessment ... --k 3                # measurement -> settings
python tools/fair_bakeoff.py --spec ...                           # calibrate, train, score
python tools/make_diagnostic.py                                   # draw what happened
```

## Data policy

Only **synthetic** slices and synthetic-derived references are committed. Real
recordings stay machine-local behind `BUGARACH_DATA_ROOT`; the public site
generates every figure from a seed and has no code path that opens a store. The
one real recording published here is baseline-only and carries no before/after
result, released deliberately and by name — it is an exception of one, not a
category ([FOUNDATIONS §5](docs/FOUNDATIONS.md)).

The detectors need only event times, so the input is small: this lab's
`event_store_onset_revised_2v` holds 85 recordings in about 4 MB, against a 127 GB
trace archive that nothing here opens.

## How this repo is kept honest

- **A MATLAB oracle, not a hand-checked number.** Reference outputs are generated
  by `tools/matlab_ref/` and compared at 1e-9. The MATLAB-semantics helpers in
  `detectors/_shared.py` are deliberately un-numpy-ish — two-ended colon
  construction, mid-point percentiles — and must never be "fixed" toward numpy.
- **781 tests**, all green — 778 pass and 3 skip where this machine cannot answer
  (no `.mat` store), including the clean-room harnesses, the browser-driven webapp
  checks and the sapper self-test.
- **[Sapper](tools/sapper.py)** turns incidents into checks that fire by
  themselves — a personal path in a public repo, `default_rng` in `src/`, a
  PySpike runtime import. A rule must prove it can fire before it exists;
  `--staged` gates commits and CI runs them all.
- **[Clean-room specs](docs/clean_room/WORKFLOW.md)** for anything implemented
  from a description rather than from source: two independent implementers who
  never see each other's code, hand-derived hostile vectors, and a fuzzer run
  between them.
- **The murderboard** ([`docs/doc_review_process.md`](docs/doc_review_process.md))
  reviews every document deliverable through eleven roles before it is handed
  over. It has retracted a novelty claim, caught a fabricated author list, and
  found a hundred and fifty problems in a plan that was rewritten rather than
  shipped.

## Licensing & citations

bugarach itself is **BSD-3-Clause** (see `LICENSE`). It deliberately builds only on
permissively licensed implementations — that is what lets it run as a shared web app
without asking anyone's permission. The one restricted tool in the ecosystem,
cSPIKE, is **not** used; its algorithms are taken from PySpike instead. Do not port
code from cSPIKE's MATLAB source.

| Upstream | License | Role here |
| --- | --- | --- |
| [PySpike](https://github.com/mariomulansky/PySpike) | BSD | SPIKE-synchronization semantics ported from its (BSD) source; test-suite cross-check (0.9.0 `max_tau` bug limits it to the uncapped regime) |
| [CICADA](https://gitlab.com/cossartlab/cicada) | MIT | CICADA detection method (ported; carries upstream copyright notice) |
| cSPIKE (MATLAB) | research/education only — **no code used** | reference outputs for parity tests only (research use, via interface2) |

⚠ SPIKE-synchronization is a **native port** rather than a PySpike wrapper because
**PySpike 0.9.0's `max_tau` cap is broken**: the cap is applied only as the default
for missing edge-neighbour ISIs, so spikes seconds apart "coincide" under a 0.25 s
cap (see `detectors/sync.py`). PySpike stays a test-suite cross-check in the
uncapped regime, where the two definitions agree.

**Cite in any publication that uses results from this tool:**

- **PySpike** — Mulansky M., Kreuz T., *PySpike — A Python library for analyzing
  spike train synchrony*, SoftwareX 5, 183–189 (2016).
- **CICADA** — cite per the [Cossart-lab repo](https://gitlab.com/cossartlab/cicada)'s
  guidance.
- Method papers for the remaining detectors will be added here as each is confirmed.

## Dev

```bash
pip install -e ".[dev]"
git config core.hooksPath .githooks     # once per clone — see below
pytest
```

**That middle line is not optional, and the suite will tell you so.** Git ignores
`.githooks/` until a clone is pointed at it, the setting lives in `.git/config` and
travels with nothing, and a clone without it looks exactly like a clone with it —
commits simply stop being checked. That was this clone's state from the first
commit until someone thought to look, and nothing failed in between. `pytest` now
fails on a clone whose gates are not wired, and prints that command.

The `[dev]` extra includes PySpike, used only as a cross-validation reference in the
test suite — the detectors themselves have no PySpike dependency. The suite runs on
the committed synthetic fixture; point `BUGARACH_DATA_ROOT` at an
`event_store_onset*` directory to also smoke-test a real slice, and that one test
skips when it is unset.

Working in this repo: [`CLAUDE.md`](CLAUDE.md) for the durable rules,
[`docs/FOUNDATIONS.md`](docs/FOUNDATIONS.md) for what is canonical and wins over
any conversation, [`docs/GLOSSARY.md`](docs/GLOSSARY.md) for the two-axis
vocabulary (stream axis versus detector axis), and
[`docs/git_workflow.md`](docs/git_workflow.md) for how work lands.
