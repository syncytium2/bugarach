---
status: open
filed: 2026-08-16
---

# Handoff — learned detectors: where this got to, and the next four things

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
- **The export team is applying the dead-ROI rule** (PR #51). Until it lands the
  corpus carries ~3% structural zeros; measured effect on the fitted background is
  under 1%.
- **The regime-shift guard does not reproduce the failure it exists to catch.**
  The six show no precision collapse across this axis. A clean pass is weaker
  evidence than it looks, and the axis probably needs widening.

## Where the outputs are

- Report: `docs/learned/report.html`, published, and copied to
  `<darkroom>/bugarach/2026-08-16-learned-detectors/`
- Board claim on `docs/SESSIONS.md` — **mark it DONE when you pick this up**
- Six other PRs are open and none should be merged without Tony: #45 (peer
  session), #46, #48, #50, #51, #52
