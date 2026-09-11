# Overnight: build a surrogate evaluation step, run it on three corpora, report by morning

> **Status: a plan for Tony's review, 2026-09-10. Nothing runs until he says go.**
> Working material for this tree, murderboarded at his request before he reviews it.

## Executive summary

**What the night delivers.** A tool that takes any export folder and reports, candidate by
candidate, whether each surrogate null leaks on *that* data — and that tool's own report, run on
our baselines and on another lab's corpus, with a one-page executive summary on top. The report a
new user would get and the report we read in the morning are the same document.

**Why a tool and not a choice.** Tony ruled on 2026-09-10 that every candidate enters the screen,
none pruned: *"you can't predict a priori which one is right."* The ruling rests on figure 10 of
Stella et al. 2022, where five surrogates run through one detector on the same real recordings
disagree epoch by epoch — and the paper's own discussion says a surrogate must be chosen *"case by
case."* If nothing predicts the right null for our recordings, nothing predicts it for someone
else's. So the evaluation belongs in the pipeline, run per dataset, the way the bake-off already
calibrates detectors on each cohort's own simulated data.

**By morning:**

- a green PR adding `bugarach.surrogates` — ten generators behind one interface — and
  `tools/surrogate_screen.py`, tested on synthetic trains only;
- three screen reports in the darkroom, each opening with an executive summary: the `senktide`
  baselines (reproducing the run record first), the `steps_excluded` baselines (the producer's
  current folder), and `cossart` (another lab's preparation, our first "new user");
- the run record's leak table and saturation table **rerun under one set of conditions**, so the
  two can finally be compared;
- a short list of morning decisions, each next to the evidence that bears on it.

**Not by morning:** the full-model tier; a value for τ (the producer's number); any number derived
from real recordings inside the git tree — FOUNDATIONS §5 keeps those in the darkroom.

**What Tony decides before launch** is at the end, under *Decisions for tonight*, each with the
default the run takes if he says nothing.

## Terms

| term | meaning |
|---|---|
| surrogate | a resampled copy of a recording that keeps some properties and destroys the one under test |
| *J* | jitter radius — how far a surrogate may move an event, ± seconds |
| τ | dead time — the shortest interval between two onsets of one ROI the producer's extractor can emit |
| ISI | inter-onset interval, here always within one ROI |
| AUC | area under the ROC curve; 0.5 is chance |
| UD / UDD | uniform dithering, without and with dead time (Stella's names) |
| JISI-D / ISI-D | joint-ISI dithering / ISI dithering (Stella's names) |
| WIN-SHUFF | window shuffling (Stella's name) |
| Elephant | the Python package that carries Stella's surrogate implementations (BSD-3) |

## What gets built

### One interface, ten generators

Each generator takes one recording's stream — a list of per-ROI onset arrays in seconds, plus the
window `[t0, t1)` — and returns the same shape. Each **declares** what it preserves and what it
does at the window's edge, because the edge policy is itself a way to leak.

| candidate | implementation | preserves | at the edge |
|---|---|---|---|
| uniform per-onset dither (UD) — **the known-bad control** | Elephant `dither_spikes` | rate | drops events pushed out (`edges=True`) |
| dither with dead time (UDD) | Elephant `dither_spikes(refractory_period=τ)` | rate and τ | drops |
| circular shift | written here — one line | the circular ISI multiset | wraps |
| rigid shift, no wrap | Elephant `dither_spike_train` | ISIs exactly, away from the edge | drops, or clamps with `edges=False` |
| joint-ISI dither (JISI-D) | Elephant `joint_isi_dithering` | the joint distribution of consecutive ISIs | — |
| interval jitter | Elephant `jitter_spikes` | counts per fixed bin | bins span the window |
| pattern jitter | **written here**, from Harrison & Geman 2009 | each event's recent history, exactly | — |
| operational-time dither | **written here**, from Louis et al. 2010 | the rate profile under drift | — |
| ISI dither (ISI-D) — *free addition* | Elephant `isi_dithering` | the ISI distribution | — |
| window shuffling (WIN-SHUFF) — *free addition* | Elephant `bin_shuffling` | counts per window | — |

The first eight are the candidates Tony ruled in. The last two are the Stella candidates our list
lacked; Elephant makes each one adapter line, and with them our set covers all of Stella's — except
trial shifting, which needs trial structure these recordings do not have, and which the rigid shift
replaces.

**Elephant enters as an optional extra**, `pip install -e ".[surrogates]"`, because it brings `neo`,
`quantities` and `tqdm` and the core dependencies are `numpy`, `scipy` and `h5py`. ⚠ **Its defaults
are millisecond-scale** — the joint-ISI smoothing defaults to 2 ms — and our events are seconds
apart. Every parameter is set explicitly per stream, and a test fails if any Elephant default is
reached.

**Pattern jitter follows the clean-room discipline** in
[`clean_room/WORKFLOW.md`](../clean_room/WORKFLOW.md): a spec written from the paper on the shelf,
an implementation from the spec alone, an independently spawned adversary implementation,
hand-derived hostile vectors, and a differential fuzzer — harness in
`docs/clean_room/harness/pattern_jitter/`, wired into `tests/test_pattern_jitter.py`. It is the
one candidate built from nothing, and a subtly wrong surrogate produces a leak that looks like a
finding.

**Operational-time dither** needs a per-ROI rate estimate, which is a parameter choice in its own
right; its bandwidth is swept, not fixed.

**Every generator gets support tests on synthetic trains** — it preserves what it declares, on data
where the answer is known. Nothing from a real recording enters the test suite (FOUNDATIONS §5).

### The screen, `tools/surrogate_screen.py`

**Input** is an export folder, named by role through `dataset.current()` — the export folder is the
input, never a store. **Baseline regions only** for our corpora (FOUNDATIONS §9: calibrate from
baseline, never from treatment); whole recordings where a folder carries no `regions.csv`, which
is the case for `cossart`. The frame interval comes from `slices.csv` (FOUNDATIONS §6).
**Zero-event ROIs stay in** (§9), and **no recording is excluded**: the four recordings carrying
motion-correction frame-floor pinning are reported per recording so they can be looked at, not
filtered, because a folder that holds something it should not is a conversation with the producer.

**Output** is an HTML report written to `darkroom()` by default (sapper SAP006). A report built
from real recordings never takes the `--also` repo copy; only synthetic demonstration runs do.

**The counting tier — no model.** For every candidate, stream, *J*, and τ where the candidate takes
one, over 60-second windows:

- **Sub-floor interval rate, at level.** The share of windows holding a within-ROI interval shorter
  than the floor. ⚠ **The floor has to be independent of the windows it is tested on.** The
  [τ todo](../todo/2026-09-10-the-dead-time-floor-is-the-producers-number.md) describes the run
  record's floor as the observed minimum of the senktide baselines; if those are the windows it
  was measured on, real data scores zero **by construction**, not by measurement. Until the
  producer declares τ, the floor is estimated on a held-out half of the recordings and the rate
  measured on the other half, so the real rate becomes a measurement.
- **Within-ROI ISI divergence**, real against surrogate, pooled across ROIs per stream.
- **Edge-band onset density and boundary pile-up** — tells the drop, clamp and wrap policies
  apart, and catches the clipping `learn/encode.py` does
  ([its own todo](../todo/2026-09-10-the-encoder-clips-onsets-onto-the-boundary-frames.md)).
- **Binning collisions** — two onsets of one ROI landing in one frame at the recording's own frame
  interval.
- **Generation time**, because a surrogate that is free in the screen can still bind in a training
  loop that draws fresh negatives every epoch.
- **Estimability.** Baselines here run about twenty minutes, and baseline's interquartile per-ROI
  rate is 0.0052–0.0190 Hz (FOUNDATIONS §9) — **roughly 5 to 23 events per ROI**. A per-ROI
  joint-ISI histogram, or a per-ROI rate profile, may not be estimable from that. A generator that
  cannot be estimated for an ROI reports so, as a share of ROIs, rather than returning a number
  that looks like an answer.
- **The level-against-increment diagnostic.** The share of windows with a sub-floor interval after
  zero, one and two applications of each candidate, at the same stream, *J* and window. This is the
  saturation table, rerun under the same conditions as the leak table.

**The positive control gates the report.** Uniform dither must be flagged by the sub-floor
statistic. If it is not, the report says the screen is broken and marks every other verdict void.

**The per-ROI-only discriminator — a stretch goal.** A classifier that structurally cannot see
across ROIs: per-ROI features pooled by a symmetric function, AUC cross-validated with folds
**grouped by recording**, so windows of one recording never sit on both sides. `learn/nets/tiny.py`
registers as a *"per-ROI filter, bounded vote, rate-quantile pooling"* and may already be that
object — whether anything mixes ROIs before its pooling is checked first, and if something does, a
numpy logistic model on pooled per-ROI features replaces it. It runs only on candidates the
counting tier did not flag. If the night runs short, the report says this tier did not run.

**The full-model tier does not run tonight.**

### The grid

- ***J* per stream**, spaced around each stream's observed floor: fast 0.1, 0.2, 0.4, 0.8, 1.6,
  2.5 s; slow 0.8, 1.6, 2.5, 3.2, 6.4, 12.8 s. The run record's own values are inside both lists,
  for the reproduction check.
- **τ for dither with dead time**: 0.5, 0.75 and 1.0 times the held-out floor, per stream, labelled
  **provisional** everywhere it appears. No fitted value becomes a constant in the code — the τ todo
  says so in terms, and it is the shape FOUNDATIONS §7 and sapper SAP012 exist to stop.
- **60-second windows**, matching the run record.
- The counting tier has no pooling operator, so its grid is candidate × stream × *J* × τ. Tony
  agreed on 2026-09-10 that the tiers **with** a pooling operator run as a grid, not as contests;
  that starts at the discriminator.

## What gets run, and on what

| corpus | role | what runs | why |
|---|---|---|---|
| senktide baselines | `senktide` | **the reproduction check, first** | recover the run record's leak and saturation tables from this code. **If they do not reproduce, the night stops and reports why** instead of building on numbers it cannot recover |
| every baseline | `steps_excluded` | the full screen, per stream and per group | the producer's newest folder, whose README says to use it for any new analysis. Per group because FOUNDATIONS §9 does not admit a pooled number on its own |
| another lab's recordings | `cossart` | the full screen | the first dataset from a different preparation — in vivo CA1 in pups, onsets as the rising edge of a binarised active run, no regions. The question it answers is Tony's: does the verdict change with the data? |

## What the report must look like

- **An executive summary first**: which candidates leak on this corpus, per stream; whether the
  uniform-dither control fired; which candidates could not be estimated; a proposed shortlist for
  the model tier, each entry with its reason.
- **Every figure numbered** and referred to by number and name. **Every abbreviation defined** at
  first use and in a table. *J* and τ defined before anything uses them.
- The repo's plot conventions — no titles above plots, identity and counts in the axis labels,
  minutes-friendly time axes.
- **Gated by armory's `render_check.py`** (`origin/downLow/tools/render_check.py`): no text
  overlaps, no ink outside a figure's own box, no rendered type below its floor. ⚠ **It does not
  catch text crossing a box edge or a line**, which is the defect in the 2026-09-10 decision brief.
  armory confirms no estate tool does; `draughtsman`'s `edge_collisions.py` carries the geometry.
  The gap is filed against render_check's canonical copy. Until that check exists, report figures
  keep text out of shapes, and a person looks at the screenshots render_check writes.

## How it runs

**Proposed as a Workflow**, which needs Tony's explicit go. Its shape:

| phase | agents | work |
|---|---|---|
| build, in parallel | 5 | Elephant adapter, circular shift and support tests · pattern-jitter spec and implementation · the clean-room adversary and fuzzer · operational-time dither · the screen and its report builder |
| verify | 1 | full suite, then the senktide reproduction check |
| run | 1 | `steps_excluded` and `cossart` screens; the discriminator if time allows |
| report | 1 | the cross-corpus executive summary |
| review | 11 | the murderboard on the summary report, one agent per role |

That is **19 agents**, above this session's medium guideline of fifteen; the murderboard's eleven
roles are the whole difference. The alternative is **8 overnight and the murderboard in the
morning**, with Tony.

**The night stops and writes a handoff instead of pushing on** when:

- the reproduction check fails;
- uniform dither is not flagged;
- the suite is not green;
- any artifact derived from a real recording is about to enter the git tree.

**Stop-on-a-dime.** Branch `surrogate-screen-overnight`; every verified step committed and pushed as
it lands; on any stop, a `wip/` branch and a root `HANDOFF.md`. The worktree is claimed on the local
board; the darkroom folder `<darkroom>/bugarach/2026-09-11-surrogate-screen/` is claimed on
`docs/SESSIONS.md` before anything is written to it.

## Decisions for tonight

| decision | default if Tony says nothing |
|---|---|
| Elephant as an optional dependency | yes, as the `surrogates` extra |
| ISI-D and WIN-SHUFF as free additions | yes |
| τ run as a provisional sweep while the producer is asked | yes, labelled provisional in every output |
| run as a Workflow — 19 agents, or 8 with the murderboard moved to morning | **no default — needs his go** |
| `cossart` as the different-data test | yes |

## Tomorrow's targets, if the night succeeds

- Read the executive summary and pick the shortlist for the model tier.
- Send the producer the τ question, already drafted in its todo.
- Decide whether Elephant stays a runtime dependency or becomes only the reference our own code is
  tested against.
- Fix the grid for the tiers with a pooling operator.
- Decide whether the surrogate evaluation becomes a stage in [`pipeline.md`](../pipeline.md) that
  every user's folder passes through, and where the viewer surfaces it.

## Risks

- **Pattern jitter is wrong in a way that looks right.** The clean-room adversary and fuzzer exist
  for exactly this.
- **An Elephant default leaks through** at millisecond scale. A test fails on any default reached.
- **Several candidates are not estimable at 5 to 23 events per ROI.** That is a result, and the
  report says so; it is also the strongest argument for the per-dataset tool.
- **The edge policy leaks.** Elephant's shift and dither drop events pushed out of the window, which
  changes counts; the edge statistics are there to see it.
- **Real-recording numbers reach the public tree.** A stop condition, not a reminder.

## Out of scope

The full-model tier. The text-against-shape checker itself — filed upstream, built there. Viewer
integration. Any change to a detector.

## Sources

- Tony's rulings, 2026-09-10, and the Stella reading behind them:
  [`todo/2026-09-10-which-surrogates-enter-the-screen.md`](../todo/2026-09-10-which-surrogates-enter-the-screen.md)
- The plan this supersedes in part:
  [`todo/2026-09-10-build-the-surrogate-screen.md`](../todo/2026-09-10-build-the-surrogate-screen.md)
- The leak and saturation tables it reruns:
  [`reviews/2026-09-10-coordination-without-labels_2026-09-10.md`](../reviews/2026-09-10-coordination-without-labels_2026-09-10.md)
- Stella et al. 2022, *eNeuro* 9(3), ENEURO.0505-21.2022 — `<darkroom>/bugarach/lit/surrogates/`;
  code at `github.com/INM-6/SPADE_surrogates`; surrogates shipped in Elephant.
- Elephant 1.2.1 `elephant/spike_train_surrogates.py`, read 2026-09-10 for the method list and
  edge semantics quoted above.
