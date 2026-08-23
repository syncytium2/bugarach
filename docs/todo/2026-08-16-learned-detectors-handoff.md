---
status: open
filed: 2026-08-16
---

# Handoff — learned detectors: where this got to, and the next four things

> ## Revision, 2026-08-17 — read this before the body
>
> **PR #52 is merged.** Everything described below is on `main`, and so is a later
> bake-off that changed the result: `docs/learned/bakeoff.md`. The body is left in
> the words of the session that wrote it, with three corrections.
>
> **Retracted.** *"The regime-shift guard does not reproduce the failure it exists
> to catch"* — the murderboard on the report took this away. Do not build on it.
>
> **Superseded numbers.** Everything below is scoped to the earlier bench: three
> simulated recordings, flat-background generator, each detector at a declared
> operating point. `F1 0.68 / recall 0.91` belongs to that bench. On the data set
> measured from 85 real recordings, with every detector fitted on three folds and
> scored on a held-out fourth, `tube` scores **0.668 ± 0.061 at recall 0.775** and
> **ties** CoactDetect's 0.651 ± 0.044 rather than leading anything. Its case is
> cost: 0.014 s to scan a held-out fold, 1,149 parameters, 5.6 s to train.
>
> **Still open, carried here from the root `HANDOFF.md` before it was deleted**
> — the bake-off's own "what this does not establish" list has the full version:
>
> 1. **Multi-seed within a fold.** Still one training run per fold, so fold spread
>    confounds data variation with training variation. Cheapest thing that could
>    change a conclusion — this is item 1 below, unmoved by the bake-off.
> 2. **K=3 was chosen by a human and moves the data set.** The scan ships in
>    `docs/learned/generator_spec.json`; K=4 cuts the cluster rate to roughly a quarter
>    (0.095 against 0.350 per minute) — an earlier draft said "halves" and nobody had
>    divided the two numbers. Review surface:
>    `2026-08-16-assessment-needs-a-human-in-the-loop.md`.
> 3. **The architecture conclusion is not controlled.** `tube` trains at 10× the
>    learning rate of the two it is contrasted with, and the project's own
>    diagnostic ranks `pos_weight`/batch size as the leading *untested* cause of
>    their failure to descend. "Building the invariant in beats hoping for it" is
>    the reading, not yet the finding.
> 4. **Drop the raw brightness channel and re-run.** One line. It would settle
>    whether the transfer asymmetry is the variance story below or simply the one
>    channel that never had its background subtracted.
> 5. **The probe cannot fail** — `2026-08-16-promiscuity-probe-cannot-fail.md`.
>    Firings leave both numerator and denominator, so no "does not fire on dense
>    random activity" claim is supported yet.
> 6. **interface2 has an unanswered message to us** —
>    `docs/teams/inbox/2026-08-16-bugarach-vendoring-ownership-and-two-bad-stamps.md`.
>    Two of three files a session proposed re-vendoring are wrong, and
>    `docs/writing_conventions.md` has no upstream there at all while a freshness
>    gate reports it current. That last one is our bug and it is live.
>
> The darkroom copy is no longer the withdrawn report, and the board claim is
> released — both closed 2026-08-17.

Branch `learned-detectors-framework`, PR #52. Everything below is pushed. This
supersedes `2026-08-16-learned-detector-does-not-converge.md`, which described a
model that has since been replaced — **read this file, not that one**, and delete
that one once you have.

## The one-paragraph version

Tony asked for lightweight learned detectors, adaptable to a lab's own data. The
measurement half is built and at parity. Three architectures were tried; the
first two never learned, and the third — **Tony's**, a centre-surround "tube" —
reaches **F1 0.68 at recall 0.91** in 1,149 parameters and six seconds of
training. A transfer test then falsified half the explanation for why it works.
Nothing rests on real data.

## What exists

| | |
|---|---|
| `bugarach.assess` | the assessor, ported from `measure_coordination_timescale.m`, **1e-9 parity** on four cases. Coordination measured without a detector. |
| `bugarach.adapt` | assessment → generator parameters, with a measured round-trip fidelity table (K=4 default; participation +18%, jitter +9%, frequency −7%) |
| `bugarach.learn.encode` | frames-not-seconds, rate-sorted rows, labels from `observed_span`, decode to the six ports' contract |
| `bugarach.learn.nets` | `ARCHITECTURES` registry — a new model is one class plus one `@register` line |
| `bugarach.learn.train` | training, threshold selection with an edge-of-range guard |
| `tools/make_learned_figures.py`, `make_tube_figure.py`, `regime_shift.py` | every number in the report, regenerable |
| `docs/learned/report.html` | the review page. Built from `report.src.html` — **edit the source and rebuild**, never the output |
| `docs/reviews/learned_detector_review_2026-08-16.md` | murderboard, 3 rounds, 11/11 roles |

## The progression, and what each model settled

1. **`trace`** (2,065 params) — pool cells away, then filter. F1 0.21. Never
   learned, which ruled out the cell axis as the problem.
2. **`tiny`** (2,393 params, 234 s) — keep cells, filter each, soft cap, pool by
   rate band, 2,000-sample receptive field left to *discover* rate invariance.
   F1 0.12. It did not discover it.
3. **`tube`** (1,149 params, 6 s) — centre minus surround on the brightness trace.
   **F1 0.68 / recall 0.91** on the quiet regime, 0.56 on busy. Half the size,
   forty times faster, and its loss actually descends.

The lesson is not capacity. It is that **building the invariant in beats hoping a
receptive field discovers it.**

## The four things I would do next, in order

1. **Multi-seed everything.** Every number is one training run at one seed; six
   runs total. The 0.68-vs-0.12 gap is far outside plausible seed variance, but
   0.68-vs-0.56 between `tube`'s two regimes is not obviously so, and no error bar
   exists. This is the cheapest thing that could change a conclusion.
2. **Sweep the mass axis** — `n_rate_quantiles`, the question the exercise was
   built to answer, blocked until now because every model scored 0.12. `tube`
   currently pools all cells into one band; splitting them is the knob. Add
   ROI-band pooling to `tube` rather than reviving `tiny`.
3. **Vary the sampling rate across training recordings.** Every bench recording
   shares one imaging rate, so nothing here can fail if the model has learned our
   microscope — and per the mechanism below, sampling rate is the axis most likely
   to break it. The learned centre widths make this testable: train at one rate,
   evaluate at another, see whether they track.
4. **Attack precision.** The model finds events and also fires on things that are
   not events. The generator already plants the negatives that would teach the
   difference — correlated bursts, and a dense block containing nothing — and they
   are labelled but never emphasised in training.

## Things that are settled — do not relitigate

- **Frames, not seconds, inside a model.** dt is the loader's problem
  (FOUNDATIONS §6, PR #48).
- **The event width is learned, not supplied.** Scales start at one sample and
  grow. No fixed scale bank, ever.
- **An event is defined by what was planted** — `observed_span` (PR #46). A
  tolerance band may be used for a training loss; it must never reach
  `frame_targets` or the scorer, and must be stated if added.
- **Rows sorted by firing rate**, ties broken by the cell's own onsets, tested.
- **One cell, one vote** — exact in `tube` (cap inside the centre window).
- **A new architecture is one file plus one registry line.**

## Two mechanistic facts worth carrying

**Centre-surround cancels the mean, not the variance.** A uniform background rise
subtracts out in expectation; the fluctuations around it grow with rate and make
chance alignments no surround removes. Hence: **train on the busier regime and
deploy downward.**

**The fitted centre widths are not a pure measurement of the event.** Retrained on
a quieter background with identical events they moved 40%. They land in the right
range and should not be quoted as recovering the timescale.

## ⚠ Open, and not mine to close

- **The generator revision is in flight** and moves the distribution this whole
  loop is fitted to. Every number here would need re-running. Tony has not said
  whether it lands first.
- **Who picks K?** It changes the derived event frequency roughly tenfold across
  its scan, a lab has to choose one, and there is no review surface —
  `2026-08-16-assessment-needs-a-human-in-the-loop.md`.
- **The dead-ROI rule has landed** — the exporter ships
  `event_store[_onset]_revised_2v_alive` (2026-08-16), the verdict made in MATLAB
  where the full record of each ROI is. It reaches 67 of 85 slices; the other 18
  are not eligible and keep every ROI, so the recordings are cleaned unevenly rather
  than cleaned. The ~3% structural zeros moved the fitted background under 1%, so
  nothing fitted before this needs redoing.
- **The regime-shift guard does not reproduce the failure it exists to catch.**
  The six show no precision collapse across this axis. A clean pass is weaker
  evidence than it looks, and the axis probably needs widening.

## Where the outputs are

- Report: `docs/learned/report.html`, published, and copied to
  `<darkroom>/bugarach/2026-08-16-learned-detectors/`
- Board claim on `docs/SESSIONS.md` — **mark it DONE when you pick this up**
- Six other PRs are open and none should be merged without Tony: #45 (peer
  session), #46, #48, #50, #51, #52
