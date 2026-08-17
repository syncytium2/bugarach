# Putting the learned-detector loop into the web app — what exists, what it costs, what will bite

**For the session that builds this into the app.** You are not starting from a
prototype; the loop runs end to end today as four command-line stages, and its
numbers are published. Your job is to put a UI in front of it, not to rebuild it.
Read this, then [`docs/workflow_plan.md`](../workflow_plan.md) — that plan is the
app's overall shape and it went through the murderboard; this file is only the
learned-detector part of it.

There is already a viewer: `bugarach.ui.app.build_viewer`, a Panel/HoloViews app with
detector lanes over an ROI raster. The loop below is what has to grow around it.

## The loop, as it actually runs

Each stage is a script, each output is a file on disk, and every one of them can be
run and inspected on its own. That property is worth preserving in the app: it is why
the current results are checkable.

| stage | script | in | out | wall clock |
|---|---|---|---|---|
| 1 · assess | `tools/assess_archive.py` | a store of real recordings | `assessment_real.json` | ~2 min for 85 slices at 1,000 surrogates |
| 2 · derive | `tools/derive_spec.py` | that assessment **+ a human choosing K** | `generator_spec.json` | seconds |
| 3 · generate + fit + score | `tools/fair_bakeoff.py` | the spec | `bakeoff.json` | minutes; the per-cell model dominates at ~236 s per fold |
| 4 · draw | `tools/make_bakeoff_figures.py`, `make_regime_figure.py`, `make_architecture_figures.py` | those JSONs | PNG + interactive HTML | seconds, except the architecture figure which trains a model first (~6 s) |

**Costs you can promise a user**, measured on one laptop, one process, no warm-up
control — order-of-magnitude, not benchmarks: the centre−surround model **trains in
~5.6 s** and **scans two hour-long recordings in ~0.014 s**, at 1,149 parameters. That
is what makes an in-app fit-and-run plausible. The per-cell model costs 236 s to train
and 2.45 s to detect for a fifth of the F1 — do not put it in a default path.

## Where a human is required, and it is not the modelling

**Stage 2 needs a person to choose K**, the cluster size the assessment runs at. K=3
was chosen for the published corpus; **K=4 halves the resulting event rate** and builds
a materially different benchmark. `derive_spec.py` refuses to choose and ships the whole
scan beside the choice, deliberately.

For the app this is the one screen that cannot be a spinner. It needs to show the scan
and take a decision, and the decision needs to be recorded with the corpus it produced
— otherwise two labs get different benchmarks and nothing says why. There is an open
item on exactly this: `docs/todo/2026-08-16-assessment-needs-a-human-in-the-loop.md`.

## What to reuse rather than rewrite

- **`bugarach.bench.pool_scores`** is the single scoring path. `evaluate` is built on
  it. Do not compute F1 in the UI layer — an earlier version of the regime-shift tool
  did its own arithmetic and put the two halves of a comparison on different metrics.
- **`bugarach.learn.nets.ARCHITECTURES`** is a registry. A new model is one class plus
  one `@register` line and it then appears in every sweep, figure and table with
  nothing else edited. If the app offers a model picker, drive it off this registry
  rather than a hardcoded list.
- **`bugarach.learn.train.train(name, make_recording, ...)`** returns a `Trained` with
  `.predict(slice_)`, `.threshold`, `.n_params`, `.train_seconds`. That is the whole
  API the app needs for fitting.
- **`bugarach.paths.darkroom()`** for any figure export. It resolves
  `$BUGARACH_DARKROOM` or finds the Dropbox mount, and returns `None` when it cannot
  — treat `None` as "skip the export", never as an error to work around.
- **`_time_axis_hook`** in `ui/app.py` for any time axis: 60-base ticks labelled
  `45s` / `2m30s`, never raw seconds. Plot conventions are in `CLAUDE.md` and the app
  must not invent its own.

## Traps that will cost you a day each

1. **Frames, not seconds, inside a model.** Nothing in a network knows what a second
   is; every width is in samples and `dt` is the loader's business (FOUNDATIONS §6).
   If the app shows a user "event width: 0.4 s" it is displaying a *conversion* of a
   fitted sample count, and it must not feed a seconds value back into a model. The
   same rule is why `grid_dt` must be the acquisition frame interval and why omitting
   it warns rather than defaulting silently.
2. **One cell, one vote.** Coactivity is distinct active cells, never an onset count.
   Any aggregation the app adds — a summary number, a sparkline, a "how coordinated is
   this slice" badge — must preserve that, or one busy cell reads as a crowd.
3. **A zero-event ROI is not a dead ROI**, and the app must never imply otherwise.
   Report "no events in this window". Never "silent", "dead", or any viability claim;
   that verdict belongs to `fireflies` and needs drug and high-K⁺ rows this repo does
   not have. See FOUNDATIONS §9.
4. **TTX does not silence the field.** If the app ever runs on treatment windows, a
   detector returning little under TTX is not thereby validated, and coordination
   persisting under TTX is a finding about the preparation rather than a false-alarm
   floor to tune away. FOUNDATIONS §9, and a session has already made this mistake.
5. **Calibrate from baseline only.** Do not let the app derive coordination properties
   from senktide or TTX windows, however convenient the data is.
6. **Fit busy, deploy quiet.** The measured transfer asymmetry
   (`docs/learned/regime_shift_fitted.json`): fitted on a quiet background and run on a
   busy one, the learned model loses 0.24 of F1 and `rate+context` loses 0.45; the
   other direction holds or improves. **If the app fits a model for a user, it should
   fit on their busier recordings.** This is the cheapest correctness win available to
   the UI and it costs nothing to implement.
7. **The threshold must not be re-picked at deployment.** It is chosen on held-out
   training-regime data on purpose. A "re-tune on this recording" button would hide
   exactly the failure section 5 of the report measures.
8. **The promiscuity probe cannot fail** — firings inside it leave both numerator and
   denominator, so it reports promiscuity rather than penalising it. Do not surface it
   as a pass/fail badge. `docs/todo/2026-08-16-promiscuity-probe-cannot-fail.md`.
9. **Every learned number is one training run per fold.** No seed error bars exist. If
   the app shows a model's score, it must not imply a precision it does not have.
10. **The corpus is simulated.** Nothing measured here says any detector is right about
    a real slice, and app copy must not blur that.

## What is honestly not ready

- **The per-cell architecture does not train** on this corpus and its threshold lands
  on the edge of the searched grid. Its number is not an operating point. Why it fails
  is unresolved — it also trains at a tenth the learning rate of the model that works,
  so the architecture comparison is uncontrolled.
- **The four-scale kernel bank collapsed to one scale** in the fit (4.0–6.6 samples
  from initialisations a doubling apart). The multi-scale design may not be earning its
  parameters; one scale has not been tried.
- **A fitted surround ratio sits within 10% of its clamp.** Widen and re-fit before
  quoting surround widths.
- **No literature method has been run on this corpus**, so "competes with
  state-of-the-art" is not a supported claim and must not appear in app copy. See
  `docs/todo/2026-08-17-literature-deep-dive-handoff.md`.

## What the literature survey changed for you — read before writing copy

Added 2026-08-17, after twelve papers went onto the shelf at
`<darkroom>/bugarach/lit/coordination/`. Four things bear on the app.

1. **"A new kind of detector" is not available, and neither is "the first".** Three
   groups already train networks that emit population events with times — DOSED
   (sleep EEG), cnn-ripple (hippocampal LFP), SEED (sleep spindles) — all descended
   from single-shot object detectors. The honest positioning, and it is still a good
   one, is **the level of the analysis and where the truth comes from**: nobody does
   this from per-cell calcium activity against events planted in a simulation fitted
   to the lab's own recordings. `docs/learned/landscape.svg` is that claim as one
   picture and the app is welcome to it.
2. **Link to the competitors, do not just name them.** Whatever page positions this
   work should link out to `PridaLab/cnn-ripple`, `Dreem-Organization/dosed` and
   `gitlab.com/cossartlab/cicada`. A positioning claim with no route to the thing it
   positions against reads as marketing.
3. **A displayed F1 is more permissive than a reader will assume.** The bench scores
   a hit at a 1.5 s edge gap, and the median realized event is 0.80 s wide — so the
   score cannot distinguish landing on an event from landing a second away.
   Measured: `docs/learned/tolerance_sweep.png`. The ranking is stable, so any
   *comparison* the app shows is safe; a bare number implying timing accuracy is not.
   If the app ever shows "how well did this detector do", say what tolerance it
   means. `docs/todo/2026-08-17-scoring-cannot-see-localization.md`.
4. **Two open upgrades would change the fit path**, so do not harden it yet:
   non-maximum suppression on the learned model's probability trace
   (`2026-08-17-no-suppression-of-overlapping-detections.md`), and pretraining on the
   six hand-written detectors' output over unlabelled real recordings before
   fine-tuning on the simulation
   (`2026-08-17-pretrain-on-the-six-then-fine-tune.md`). The second one is a route to
   a per-lab model that has actually seen that lab's real backgrounds, which is close
   to the app's whole selling point — but it is unmeasured, and its control
   experiment has not been run.

**What you do not need to do:** nothing here blocks the first slice of work below.
None of these change `train()`'s signature, the registry, or the scoring path.

## Suggested first slice of work

Do not start with the whole loop. Start with **stage 3 on a spec that already exists**:
load `docs/learned/generator_spec.json`, generate a corpus, train `tube`, and show its
detections on the viewer's existing lanes beside two of the six. That exercises
training, thresholding, scoring and display in one screen, on a path where every number
already has a published value to check against — so if the app disagrees with
`bakeoff.json`, the app is wrong, and you will know on day one rather than after the
UI is built.

## The published result, for checking against

`<darkroom>/bugarach/2026-08-17-coordination-report/coordination_report.html` — the
whole pipeline, both architectures drawn from their fitted parameters, the comparison
against the six, and the transfer test. Its review record is beside it. Read section 6
("what this does not establish") before writing any user-facing copy.
