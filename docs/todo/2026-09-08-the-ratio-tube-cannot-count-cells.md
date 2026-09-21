---
status: open
filed: 2026-09-08
---

# The ratio arm of the tube 2×2 does not measure participation, and the bake-off cannot see it

> **Not murderboarded** — working material for sessions in this tree, same standing as
> [`docs/run_records.md`](../run_records.md). **If any of it reaches an outside reader,
> murderboard that artifact first.** No number derived from a real recording is in this
> file; the figures and the tallies are in the darkroom.

**Tony, 2026-09-08**, looking at the pilot APV+CNQX+GZ run's learned detections: *"the
learned detectors fire on a single event in a single roi"*.

He is right about two of the six, and it is not a threshold that needs nudging. **The two
log-ratio variants — `tube_ratio` and `tube_ratio_guard` — have lost participation as a
variable.** The two subtract variants, `tube` and `tube_guard`, are fine.

## What was measured

Two independent lines, in `tools/probe_participation.py`. Both figures are at
`<darkroom>/bugarach/participation_probe/`.

**The ladder.** Refit the four tube variants on the pilot's own
`generator_spec.json` exactly the way `tools/run_learned_on_folder.py` fits them — same
seeds, same steps, same learning rates — so all four thresholds come out equal to that
run's `learned_settings.csv` and the probe is talking about the run's own models. Then
plant *k* cells in one frame, no jitter, against a stated background, and read the peak
score.

| | k=1 | what it takes to cross its own threshold |
|---|---|---|
| `tube` | flat at zero | **2 cells**, at every background |
| `tube_guard` | flat at zero | **2 cells**, at every background |
| `tube_ratio` | **0.89 in a silent field** | 1 cell if the neighbourhood is quiet, 4 if it is at the spec's background |
| `tube_ratio_guard` | 0.77 silent, **~0.98 at the spec's background** | its curve is **flat across every k including k=0** — it sits on its threshold whether eight cells fire, one fires, or none does |

`tube_ratio_guard`'s flat line is the whole finding in one panel: at the spec's own
background it scores the same at k=0, where the planted frame was deliberately emptied,
as at k=8. It is not answering *"did many cells fire together"* at all.

**The tally.** Count, for every call in the run's `07_learned/detections.csv`, how many
ROIs in the real recording have an onset within ±0.25 s of the call's own span. A
bursting cell counts once, because the question is how many cells.

> ⚠ **Revised 2026-09-08, same day, and the revision matters.** The first version of
> this section gave the percentages alone. **A raw lone percentage is not comparable
> across detectors** — it is set by the width each detector declares — so every call
> is now matched against windows of its own width thrown at random times in its own
> recording. On this cohort that chance rate is **90–97 %** for every detector with
> short calls, which is what makes a low observed fraction worth anything. The
> uncorrected reading put a red flag on locust, whose 12 % is against a chance of 98 %.

| | calls | on one ROI or none | thrown at random | ratio |
|---|---|---|---|---|
| `tube` | 354 | 1 — 0.3 % | 95 % | **0.00** |
| `tube_guard` | 369 | 3 — 0.8 % | 96 % | **0.01** |
| `tube_ratio` | 298 | 17 — 5.7 % | 96 % | **0.06** |
| `tube_ratio_guard` | 247 | 16 — 6.5 % | 96 % | **0.07** |

**Read this as a comparison, not as an indictment.** Both ratio variants are still
15× better than dart-throwing; what they are is **ten times worse than the two
subtract variants**, which differ from them by one kernel operation and nothing else.
That differential is the finding here, and the ladder is what makes it a mechanism
rather than a coincidence — the tally on its own could not carry the claim.

The lone calls cluster where the ladder predicts: the median count of events within
±30 s of one is 7–9, against 20 around the same detector's multi-ROI calls. **They are
in the quiet stretches**, which under a ratio is where contrast is largest.

## Why — and it is the mechanism, not the fit

`_build_tube_variant`'s ratio mode replaces centre-minus-surround with
`log(centre) − log(surround)`. A log difference is **scale-free by construction**: it
reports contrast and discards magnitude. One onset against a near-empty surround has the
same contrast as five onsets against a surround five times larger. That is the property
the variant was added to have — CFAR divides where the shipped tube subtracts — and
participation is exactly the magnitude it throws away.

`build_tube`'s bypass channel is supposed to carry the magnitude back: `bright` reaches
the head on its own channel beside the zero-integral responses. On this fit it does not
do enough of that. Whether more training seeds, more steps, or a corpus with a quiet-field
negative would fix it is unmeasured.

## The bake-off's rate-robustness column reads the wrong end of the fraction

On the pilot's bake-off `tube_ratio` and `tube_ratio_guard` score **`hot_fa` 0.0 and 0.2**
— the cleanest promiscuity-probe numbers in the whole table, better than every hand-written
detector and better than `tube`'s 7.5. That looks like the ratio winning the argument the
2×2 was built to settle.

It is not evidence of anything. **The probe is a HOT window** — a stretch of raised
background with nothing coordinated planted — and a model that divides by its surround
cannot fire there, because the denominator is large. The failure it trades into is the
other end of the same fraction, a *small* denominator, and **the simulated corpus contains
no quiet-field negative at all**. So `hot_fa` 0 on a ratio model is a restatement of the
arithmetic, not a measurement of its robustness.

That is a gap in `bench`, not only in this variant: any future divide-shaped detector will
pass the same probe the same way.

## What is open, and it is Tony's

1. **Does the ratio arm stay in the 2×2?** It is a mechanism screen, so a variant that
   fails on the axis the screen is about is a *result*, not a defect to patch out. The
   honest outcome may be to keep it and report it.
2. **A quiet-field negative in the bench.** The cheap version is a low-rate stretch with
   nothing planted, scored like the hot window, so `hot_fa` gains a twin. Until it exists
   no detector's rate robustness has been measured, only half of it.
3. **`n_roi` is `NA` on every learned call.** `run_learned_on_folder.py` writes
   `n_roi=None`, so this could not have been seen in the file — only by rendering the
   raster and looking, which is how it *was* seen. The six write a participation count;
   the learned models should too, and then a lone call is visible in `detections.csv`.
4. **One training seed.** Everything above is seed 0. The standing limitation of every
   learned number in this project, and a comparison between architectures is where it
   bites hardest.

## What this does NOT say

The pilot run's `for_fireflies/` note already warns that two of the six learned files are
degenerate (`trace` and `tiny`, threshold on the edge of the grid, one span per window).
**That warning does not cover the ratio variants** — their thresholds are interior and
their calls look like ordinary detections. Anything drawn from `tube_ratio` or
`tube_ratio_guard` in that folder carries this finding instead, and the before/after
figure's panels Q, R, S and T are those two detectors.

Reproduce:

```
python tools/probe_participation.py \
  --spec  <run>/02_spec/generator_spec.json \
  --detections <run>/07_learned/detections.csv \
  --folder <run>/data/<export folder>
```
