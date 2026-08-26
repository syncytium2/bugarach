"""Score all six detectors against planted truth, at declared operating points.

Stage 3 of [`docs/simulation_plan.md`](../../docs/simulation_plan.md): the
sensitivity bench, and the regime-shift guard the plan calls the single
highest-value item on that page — *the precision-collapse figure is a test that
was drawn as a picture.* Here it is an assertion.

Two things this module refuses to do, both of them traps the project already
paid for.

**It will not run a detector at whatever its signature defaults to.** Those
defaults are not all calibrated operating points, and the difference is not
small: `coact_detect` defaults to the MATLAB function's `alpha=0.01`, where it
scores **F1 0.72** on the sparse regime, while explore_sce's FAST point
(`alpha=1e-4`, `int_win_sec=2.0`) scores **1.00**. A bench that read the
signature would have published the first number as CoactDetect's performance.
So every operating point is declared here with its provenance, and
:data:`OPERATING_POINTS` is the one place that changes when a calibration does.

**It will not report an optimum that sits on the edge of the grid it searched.**
An optimum at the boundary means the search was too narrow and the real one is
outside it; upstream published such a point once. :func:`pick_operating_point`
raises instead.

The scoring rule is interval-based (see :mod:`bugarach.score`) — binned
detectors report spans, and matching their bin edge against a planted onset
scores a correct detector at zero.
"""

from __future__ import annotations

from dataclasses import dataclass, field

import numpy as np

from bugarach.detectors.cicada import cicada_detect
from bugarach.detectors.coact import coact_detect
from bugarach.detectors.loco import loco_detect
from bugarach.detectors.rate import (
    rate_detect,
    recording_extent,
    stream_trains,
)
from bugarach.detectors.sce import sce_detect
from bugarach.detectors.sync import sync_detect
from bugarach.score import score_stream
from bugarach.simulate import simulate_coordination

STREAM = "events"
"""The single-stream slice the generator emits (FOUNDATIONS §3)."""

MEASURED_PROVENANCE = (
    "constellation/coordination_timescale_summary.csv — flavour 'all-baseline', "
    "fast stream, min_rois=4 (the file's own headline_K). 84 slices. Produced by "
    "interface2 measure_coordination_timescale.m: roiRate = events/win_dur (Hz "
    "per ROI), jit_obs = median within-cluster onset SD (s), partN_obs = median "
    "participating ROIs per cluster."
)
"""Where the recording's structural values come from.

Recorded as a string rather than a comment because a bench whose settings have
no traceable origin cannot be re-derived when the measurement is revised, and
this one **is** revisable: `optim_history/README.md` marks the whole campaign
PROVISIONAL, and notes that the calibrated settings were adopted on 2026-08-05
*without* the real-data validation the deck named as the deciding step. These
numbers are measurements; the decision that rested on them was never checked.
"""

MEASURED_RATE_SHAPE = 0.275
"""Gamma shape of the per-ROI background rate in real baseline windows.

Fitted, not chosen: within a window the ROI rate is modelled as
``Gamma(shape, mean/shape)`` and the observed count as Poisson over that rate —
Negative Binomial marginally — and this is the maximum-likelihood shape over
**81 baseline windows / 2 643 ROIs**, each window keeping its own mean because
untreated slices genuinely differ several-fold. Re-derive with
``python tools/fit_background_shape.py`` (needs ``$BUGARACH_DATA_ROOT``); the
tool prints the fit and says whether the tree's value still matches the data.

The number worth looking at is not the shape but what it reproduces. Real
windows leave **35%** of ROIs with no event at all, at a median 1.7 mHz, and
reach 486 mHz. Drawing rates at this shape leaves **38%** silent at a median of
1.7. The silent ROIs are **not modelled** — there is no zero-inflation term
here. They are what a low rate drawn from the tail produces over a finite
window, which is the reason to believe the shape rather than merely accept it.
A flat field at the same mean leaves 2% silent at a median of 10.0 mHz.

⚠ The tail overshoots: the fit reaches ~847 mHz where the data reaches 486. A
Gamma is the simplest distribution that produces the silence and the skew
together; it is not the last word on the busiest ROIs.

⚠ **Not wired into the bench.** ``BENCH_RECORDING`` still runs a flat field, so
every operating point and every score in this package is still measured on the
old background. Switching it re-derives the whole bench and is not a default
change — see ``docs/todo/2026-08-14-generator-background-model-is-flat.md``.
"""


@dataclass(frozen=True)
class OperatingPoint:
    """One detector, the settings it is benched at, and where they came from.

    ``knob`` and ``grid`` define the sensitivity axis: the parameter swept to
    trace a detection curve, and the values swept over. The grid must bracket
    the operating point — if the F1-optimum lands on an end of it, the search
    was too narrow and :func:`pick_operating_point` says so rather than
    reporting the boundary as an answer.
    """

    params: dict
    source: str
    knob: str
    grid: tuple
    takes_rng: bool = True

    def with_knob(self, value) -> dict:
        return {**self.params, self.knob: value}


# Provenance matters more than the numbers: a bench whose settings have no
# recorded origin cannot be compared to constellation/'s MATLAB campaign, and
# cannot be re-derived when a calibration moves.
OPERATING_POINTS: dict[str, OperatingPoint] = {
    "loco": OperatingPoint(
        params=dict(bin_width_sec=1.0, context_win_sec=120.0, thr_step_sec=15.0,
                    merge_gap_sec=2.0, threshold_pctile=99.9, n_surrogates=100),
        source="measured-regime F1 optimum, FAST (loco_detect docstring)",
        knob="threshold_pctile", grid=(99.0, 99.5, 99.9, 99.99, 99.999, 99.9999)),
    "cicada": OperatingPoint(
        params=dict(sce_percentile=99.999, active_duration_sec=1.0, n_surrogates=100),
        source="calibrated FAST pair (cicada_detect docstring); FAST percentile "
               "retuned 99.99 -> 99.999 on 2026-08-20 with REGIMES — see cicada.py "
               "for the measurement. Kept in step with the detector default on "
               "purpose: a bench grading a configuration nobody deploys grades "
               "nothing.",
        # Extended 2026-08-20 when REGIMES moved to the approved export folder: at the
        # corrected (busier) quiet endpoint the old top, 99.99999, was still the
        # peak and the search was still climbing. A busier background needs a
        # stricter percentile, so the grid needs room above the operating point
        # rather than ending at it.
        knob="sce_percentile", grid=(90.0, 99.0, 99.9, 99.99, 99.999, 99.9999,
                                     99.99999, 99.999999, 99.9999999)),
    "sce": OperatingPoint(
        params=dict(bin_width_sec=10.0, threshold_pctile=99.0, n_surrogates=200),
        source="sce_detect defaults (generate_sce contract)",
        # Extended downward for the same reason and in the opposite direction:
        # on the approved recordings SCE's F1 peaked at the old floor of 90 and was
        # still climbing, so it wants a LOOSER threshold where cicada wants a
        # stricter one. Two detectors, one change of source recordings, opposite responses.
        knob="threshold_pctile", grid=(75.0, 80.0, 85.0, 90.0, 95.0, 98.0, 99.0,
                                       99.5, 99.9)),
    "coact": OperatingPoint(
        params=dict(int_win_sec=2.0, context_win_sec=60.0, alpha=1e-4,
                    n_surrogates=100),
        source="explore_sce viewer FAST point — NOT the coact_detect signature "
               "default of alpha=0.01, which scores F1 0.72 here",
        knob="alpha", grid=(1e-2, 1e-3, 1e-4, 1e-5, 1e-6, 1e-7)),
    "rate": OperatingPoint(
        params=dict(excess_threshold_hz=5.0, context_win=60.0, rate_win=1.0,
                    grid_dt=0.1),
        source="rate_detect defaults; grid_dt is the generator's own 0.1 s grid",
        knob="excess_threshold_hz", grid=(0.5, 1.0, 2.0, 3.0, 4.0, 5.0, 6.0, 8.0),
        takes_rng=False),
    "sync": OperatingPoint(
        params=dict(tau_max=0.25, max_gap=0.5, C_threshold=0.1, C_min=0.1),
        source="viewer FAST defaults (sync_detect docstring)",
        knob="C_threshold", grid=(0.005, 0.01, 0.02, 0.04, 0.08, 0.12),
        takes_rng=False),
}

DETECTORS = tuple(OPERATING_POINTS)


REGIMES: dict[str, dict] = {
    "baseline_quiet": dict(bg_rate_hz=0.0052),
    "baseline_busy": dict(bg_rate_hz=0.0190),
}
"""The difficulty axis, and **every value on it comes from untreated recordings.**

Both endpoints are the interquartile spread of slice-mean per-ROI rate across
baseline windows, fast stream: 0.0052 Hz at p25 and 0.0190 Hz at p75, around a
median of 0.0102. Untreated slices vary 3.7-fold among themselves, and that
variation is the axis an operating point has to survive.

**Re-derived 2026-08-20 from the export folder, which is what the lab
approved.** The previous endpoints — 0.0038 and 0.0175, a 4.6-fold span — were
fitted against the `.mat` store, which carries every recording ever processed
including the two the lab withdrew (SAP007, and
`docs/todo/2026-08-20-six-tools-still-read-stores.md`). The folder is smaller and
different, so the axis moved: both ends up, and the span narrower.

**Moving it changes no detector's score beyond seed noise, and reorders nothing.**
Measured before the change rather than assumed — every detector at its calibrated
operating point, nothing re-tuned, 12 seeds at the quiet endpoint:

===========  =========  =========  ==========  =======
detector     F1 old     F1 new     mean dF1    sd(dF1)
===========  =========  =========  ==========  =======
coact            0.743      0.688      -0.055    0.078
loco             0.731      0.649      -0.083    0.102
rate             0.601      0.625      +0.023    0.085
cicada           0.521      0.547      +0.026    0.076
sync             0.377      0.473      +0.095    0.128
sce              0.284      0.360      +0.075    0.095
===========  =========  =========  ==========  =======

**No detector moves by more than its own seed-to-seed spread**, and the ranking is
identical either way: coact > loco > rate > cicada > sync > sce. A first pass at
three seeds appeared to drop loco from first to third; that was noise, and it is
recorded because three seeds is the bench default and is not enough to support a
claim of this kind.

**No treatment appears here, as a source or as an endpoint.** Tony, 2026-08-14:
*"everything should be based on baseline recordings. do not use senk or ttx as
sources for the properties of coordination."* Two earlier versions of this module
got that wrong in opposite directions — the first ran baseline → senktide, which
made the drug response the thing operating points were checked against; the
second replaced it with a TTX-derived endpoint, which is still a treatment, and
which pooled 37 slices whose measured effects run in **opposite directions by
group** (ORX up, male unchanged, diestrus down). The global foundations doc
forbids exactly that pooling: *"a TTX result on one group does not generalise to
the arm."*

**The old justification for the quiet end is withdrawn, not restated.** It used to
read: "the correction costs nothing — baseline's own p25 (0.0038) lands within 5%
of the TTX median (0.0040)". On the approved recordings p25 is 0.0052, which is 30%
above that TTX median, so the coincidence is gone.

Losing it costs nothing, because the argument was never load-bearing and should not
have been offered as reassurance. The reason to take the quiet end from untreated
p25 is that treatments are not a source of coordination properties at all — Tony,
2026-08-14. That a drug-derived number happened to sit nearby was a curiosity, and
had the two disagreed from the start the untreated value would still have been
correct. An argument that only works when the numbers agree is not an argument.

Senktide is absent entirely rather than held out. Holding it out still requires
generating a recording at senktide's rate, which is using a treatment as a source
of a coordination property. If a senktide evaluation is wanted it is a separate,
explicit decision, not a default of this module.
"""

NULL_RECORDING = dict(bg_rate_hz=0.0052, n_per_level=(0, 0, 0),
                      hot_window=None, hot_rate_hz=0.0, ramp_sec=0.0,
                      n_distractors=0)
"""A **synthetic** recording with no planted coordination — Poisson background at
the quiet end of baseline, and nothing else.

Its only claim is about construction: this generator planted no events, so a
detector reporting one is reporting structure that was not put there. That is a
useful false-positive floor precisely because it rests on the construction and on
nothing about biology.

**It is not a TTX recording, and TTX is not a silencing control.** An earlier
version asserted that under TTX action potentials are blocked so coordination
cannot happen, and treated a detector's TTX detections as false positives by
construction. That is false and the project forbids the premise: coordination
persists under TTX, the mechanism is open work, and a detector returning little
in a TTX window is **not** thereby validated. The rate here is baseline's own
p25, not a drug's median.

⚠ **This is measured at one rate only.** Reviewer 2's finding, 2026-08-14: the
false-positive ranking is not stable across the range — re-run at a busier
background it reorders, so a detector that reports zero here is not thereby
quiet. Report it with its rate attached, and do not read it as a ranking.
"""

# Measured off baseline slices only — see MEASURED_PROVENANCE.
BENCH_RECORDING = dict(
    duration_sec=2700.0,
    n_roi=33,
    participation=(0.30, 0.18, 0.10),
    n_per_level=(5, 5, 5),
    jitter_sec=0.36,
    min_sep_sec=120.0,
    hot_window=(1200.0, 1500.0),
    hot_rate_hz=0.06,
    ramp_sec=30.0,
    n_distractors=6,
    distractor_frac=0.18,
    distractor_window=(120.0, 1100.0),
)
"""The recording every bench run is scored on.

Its structural values are **measured off real recordings**, not invented. Until
2026-08-13 they were guesses, and every one of them made coordination easier
than it is:

===================  ==========  =============================  ==============
knob                 was         measured                       effect
===================  ==========  =============================  ==============
``n_roi``            30          ~33                            (was right)
``bg_rate_hz``       0.05 Hz     0.0096 Hz/ROI                  5× too busy
``jitter_sec``       0.05 s      0.36 s                         7× too tight
``participation``    50–100%     6 of ~33 ROI = 18%             3–6× too many
===================  ==========  =============================  ==============

The consequence was not subtle. On the invented values every detector scored
F1 ≈ 0.9–1.0 and the bench could not tell them apart; on the measured ones they
range 0.20–0.75 and separate sharply, because a real coordinated event recruits
about **six ROIs with a third of a second of spread** — which sits just above
the ``min_rois`` floor the detectors ship with. That is the regime the
instruments were designed for, and it is where they differ.

``participation`` keeps a spread (30 / 18 / 10%) around the measured median
rather than collapsing to it, so recall still resolves a participant floor. The
10% level is ~3 ROIs, at the floor itself.

``hot_rate_hz`` moved with them. At 0.30 it was 6x the invented background and
**31x the measured one** — a probe that severe stops asking whether a detector
keys on rate and starts asking whether it survives an impossible surge. 0.06 is
6x measured baseline and 1.6x senktide: busier than any real condition in the
table, which is the point, without leaving the physical world.

``min_sep_sec`` is 120 s and not the generator's 15 s default on purpose. The
detectors estimate their null over context windows up to 120 s wide, so events
spaced more tightly than that put real coordination inside the null the
threshold is derived from — the **contaminated null**, the trap that made the
first upstream benchmark unusable and cost two weeks of tuning against it. One
event per context window is the condition for a background-only null.

That spacing is what sets ``duration_sec``, not the other way round: the
generator needs a mean interval above the floor, the hot window is excluded from
placement, and it refuses outright rather than quietly packing the events
closer. A 45-minute recording is the price of a null worth estimating against.

It is also long enough that the *realized* spacing stays irregular (CV ~0.8 at
these settings). At the shortest length that fits, every interval is pinned near
the floor and the schedule becomes near-metronomic — harmless for these six,
which use no timing prior, but the same configuration feeding a training set
would hand a model the clock as a shortcut (the plan's warning that regularity
is a cue). Shortening this recording is therefore not the free win it looks
like.

The hot window is dense-but-random with no planted events (a rate-fooled
detector fires there) and the distractors are correlated bursts that are real
coincidence but not coordination. Both are negatives with no recall value; they
exist so the bench can fail a detector for firing on them.
"""


def make_recording(regime: str, seed: int, **overrides):
    """One bench recording. ``regime`` selects the background rate.

    Every regime here is derived from untreated recordings; there is no
    treatment regime to accept. See :data:`REGIMES`.
    """
    if regime not in REGIMES:
        raise ValueError(f"unknown regime {regime!r} — have {sorted(REGIMES)}")
    return simulate_coordination(
        seed=seed, **{**BENCH_RECORDING, **REGIMES[regime], **overrides})


CROWDED_RECORDING = dict(BENCH_RECORDING, min_sep_sec=14.0, duration_sec=10800.0,
                         n_per_level=(40, 40, 40), hot_window=None,
                         hot_rate_hz=0.0, ramp_sec=0.0, n_distractors=0)
"""Some events sit inside one another's reference window and some do not — so the
recording is its own control.

**The bench cannot exhibit reference-window contamination, and that is why the
regime-shift incident was found by hand rather than by the suite.**
``BENCH_RECORDING`` plants events at least **120 s** apart while a rolling
detector's reference window spans **±30 s**, so a second planted event can never
land in the first one's context. The failure mode every CFAR detector uses guard
cells against — Finn & Johnson quantified it in 1968, and this project met it as
binned SCE's precision falling 74% → 10% — is *impossible by construction* on the
recording the detectors are scored on.

So it gets its own recording rather than a change to the shared one. Moving
``BENCH_RECORDING``'s spacing would re-derive every operating point and invalidate
every published number for a reason unrelated to why they were derived; this adds
a condition instead of moving the goalposts.

**14 s** is not arbitrary: it is the spacing of the dense benchmark whose settings
collapsed on sparse data, recorded in the README as the incident that cost two
weeks. The probe and distractors are off because this recording asks one question
— what happens when events crowd each other's context — and a dense-but-random
block would confound it with rate-keying.

⚠ **It carries no background rate, and that is deliberate — it takes a regime,
like every other recording here.** Until 2026-08-23 :func:`make_crowded_recording`
merged no regime at all, so ``bg_rate_hz`` fell through to
:func:`~bugarach.simulate.simulate_coordination`'s own default of **0.05 Hz** — the
pre-2026-08-13 invented value the correction table above names *"5× too busy"*,
roughly 10× :data:`REGIMES`' quiet endpoint. The recording built to isolate
crowding was running off the difficulty axis, and two thirds of the recall
collapse attributed to crowding was that instead: CoactDetect recalls **0.652**
at ``baseline_quiet`` against **0.254** as it had been shipped. The rate-keying
confound this docstring shuts the door on arrived through a keyword default.
``test_the_crowded_recording_stays_on_the_difficulty_axis`` is the door that
closes by itself.

**The count matters as much as the floor**, which is not obvious and cost a
measurement to find. ``min_sep_sec`` is a *floor* under a renewal process, not a
target: at the bench's own event count it changes almost nothing, because the
median gap stays near 70 s and only 5 of 35 gaps land inside a reference window.
**The count is what crowds.**

⚠ **It runs three hours, and the length is the design.** Tony, 2026-08-23:
*"shouldn't the two tests have the same number of events so F1 can be compared.
who cares how long the recording has to be?"* Both halves were right and the
second one is what fixed this.

The first version planted the same 120 events in 45 minutes, which put **every**
event inside a neighbour's reference window — 97 of 119 gaps under 30 s, none
over 60. So there was no uncontaminated group anywhere in it, and the only
available comparison was against ``BENCH_RECORDING``, which differs in event
count, duration and therefore false-alarm opportunity all at once. Two things
followed, both bad. F1 could not be compared across the pair at all, because
eight times the events raises precision on density alone — CoactDetect reads a
*higher* F1 crowded than on the bench while recalling a fifth less. And matching
the count by lengthening the sparse side cannot fix that, because false-alarm
opportunity scales with duration: the bench's own 15 events over 6 h hold recall
at 0.85 and drop precision from 0.633 to 0.250. **Crowding is events per unit
time, so no two recordings can differ in it and match on both count and
duration.**

Three hours dissolves the problem instead of balancing it. At the bench's own
``interval_cv`` the gap distribution spans both regimes in **one** recording:
about **38%** of events have a neighbour inside their own ±30 s reference window
and about **31%** have nothing within 60 s. Recall is per-event, so splitting it
by each event's own nearest-neighbour gap (:func:`nearest_neighbour_gaps`) holds
the count, the duration, the background *and* the false-alarm opportunity fixed
by construction — there is only one recording. See
``test_the_crowded_recording_contains_its_own_control``.

That contrast immediately paid for itself. Between recordings, a guard interval
looked like the masking fix §4a predicted. Within one, its recall gain is **flat
across the gap** — CoactDetect +0.045 at a 15–30 s gap and +0.046 at over 60 s,
where there is no neighbour to unmask — while precision falls 0.889 → 0.867. It
was lowering the bar everywhere, not relieving masking. `docs/forks.md` §4a.

Use it through :func:`make_crowded_recording`. It is a **diagnostic, not a
regime**: nothing should be calibrated on it, because a set assembled to hold
both populations in useful proportions is not one that anything resembles.
"""

TAIL_RECORDING = dict(CROWDED_RECORDING, n_per_level=(60, 60, 60),
                      min_sep_sec=6.0, interval_cv=1.0)
"""The crowded **tail** — fitted to real recordings, not invented.

:data:`CROWDED_RECORDING` plants a crowding fraction of **0.38**. Measured against the
export folder (``tools/probe_real_crowding.py``, 39 recordings with enough detections
to characterize), real recordings run **median 0.00, IQR 0.00–0.30, range 0.00–0.57**,
and **7 of 39 sit above 0.38**. So the region where reference-window contamination is
worst had no simulated counterpart at all;
``docs/reviews/guard_prior_art_2026-08-26.md`` records that as the gap this closes.

**The tail is not bursty, and that ruled out the obvious knob.** ``interval_cv`` buys
crowding by making the schedule clumpy — ``simulate_coordination`` calls ``>1`` *"long
quiet stretches broken by closely-spaced events"* — and reaching 0.5 that way needs
``interval_cv`` near 1.5, whose realized interval CV is 1.2–1.6. The seven real tail
recordings have an interval CV of **0.62–1.59, median 0.93**: Poisson-ish spacing, not
bursts. What they do have is a **small floor** — minimum gaps of **6–26 s, median 8** —
against this module's 14 s, and more events per hour.

So the tail is reached with ``interval_cv`` left at 1.0, the floor dropped onto the
real tail's own minimum gaps, and the count raised, holding the three-hour duration.
8 seeds, realized:

===============================  ========  ======  =========  =================
setting                           crowded      CV    min gap  matches real?
===============================  ========  ======  =========  =================
``CROWDED_RECORDING``                0.39    0.85       14.7  at the boundary
120 ev / 3 h / floor 6 s             0.48    0.94        6.8  **yes, mid-tail**
**TAIL_RECORDING** (180 / 3 h)       0.61    0.91        6.3  above in aggregate
===============================  ========  ======  =========  =================

**Its aggregate crowding is above anything observed, on purpose, and it is meant to be
used per-event rather than in aggregate.** This is the same trade
:data:`CROWDED_RECORDING` makes and states — *"a set assembled to hold both populations
in useful proportions is not one that anything resembles"* — for the same reason:
recall is per-event, so splitting by each event's own :func:`nearest_neighbour_gaps`
holds count, duration, background and false-alarm opportunity fixed inside one
recording. Raising the count is what populates the **tightest gap bins**, which are the
point and which :data:`CROWDED_RECORDING` barely reaches. Read the bins, not the
headline fraction.

⚠ **A diagnostic, exactly like its parent. Nothing may be calibrated on it**, and no
operating point in this module is derived from it.

One note against the parent's docstring: *"at the bench's own event count
[``min_sep_sec``] changes almost nothing"* is true, and is about
:data:`BENCH_RECORDING`'s 15 events. At the crowded count the floor moves crowding
0.39 → 0.51 by itself, which is why it is a knob here and not there.
"""


def make_tail_recording(regime: str, seed: int, **overrides):
    """A recording whose planted events reach the real crowded tail.

    Same ``(slice, ground_truth)`` pair as :func:`make_recording`, and ``regime`` is
    required for the same reason it is on :func:`make_crowded_recording`. See
    :data:`TAIL_RECORDING` for what it is fitted to and what it must not be used for.
    """
    if regime not in REGIMES:
        raise ValueError(f"unknown regime {regime!r} — have {sorted(REGIMES)}")
    return simulate_coordination(
        seed=seed, **{**TAIL_RECORDING, **REGIMES[regime], **overrides})


CROWDING_GAP_SEC = 30.0
"""Half the shipped 60 s context — a gap below this puts two planted events in
one another's reference window, which is what makes an event crowded.

Named rather than written as a literal because it is a *consequence* of
``context_win``: change the context and this moves with it.
"""


def nearest_neighbour_gaps(gt) -> "np.ndarray":
    """Seconds to each planted event's closest neighbour, in ``gt.times`` order.

    The companion to :data:`CROWDED_RECORDING`, and the reason that recording is
    three hours long. **Crowding is a property of an event, not of a recording**,
    so it is measurable within one: score as usual, then split recall by this.
    Everything a between-recording comparison cannot hold fixed — event count,
    duration, background rate, false-alarm opportunity — is fixed here because
    there is only one recording.

    A lone event gets ``inf``. Compare against :data:`CROWDING_GAP_SEC`::

        sl, gt = make_crowded_recording("baseline_quiet", 1)
        gaps = nearest_neighbour_gaps(gt)
        crowded = gaps < CROWDING_GAP_SEC        # has a neighbour in its context
        isolated = gaps >= 2 * CROWDING_GAP_SEC  # has none, and is the control

    The order is ``gt.events``' — ``gt.times`` is derived from it and
    :attr:`~bugarach.score.Score.hits` is in it — so ``gaps`` and ``score.hits``
    are column-aligned and ``score.hits[gaps < CROWDING_GAP_SEC].mean()`` is the
    crowded group's recall. Do not sort one without the other.
    """
    t = np.asarray(gt.times, dtype=float)
    order = np.argsort(t)
    gaps = np.full(t.size, np.inf)
    if t.size > 1:
        d = np.diff(t[order])
        by_time = np.full(t.size, np.inf)
        by_time[:-1] = np.minimum(by_time[:-1], d)
        by_time[1:] = np.minimum(by_time[1:], d)
        gaps[order] = by_time
    return gaps


def make_crowded_recording(regime: str, seed: int, **overrides):
    """A recording whose planted events crowd each other's reference window.

    Same signature and same ``(slice, ground_truth)`` pair as
    :func:`make_recording` — ``regime`` selects the background rate from
    :data:`REGIMES` and is **required**, because this function once defaulted it
    and the default was wrong for eight months of nobody noticing. See
    :data:`CROWDED_RECORDING` for what the recording is for, what it must not be
    used for, and what the missing regime cost.

    Crowding and the background are separate axes and both matter: at
    ``baseline_quiet`` crowding costs CoactDetect 0.181 of its recall, and moving
    the background off the axis cost another 0.398 on top.
    """
    if regime not in REGIMES:
        raise ValueError(f"unknown regime {regime!r} — have {sorted(REGIMES)}")
    return simulate_coordination(
        seed=seed, **{**CROWDED_RECORDING, **REGIMES[regime], **overrides})


def make_null_recording(seed: int, **overrides):
    """A recording with no planted coordination — background only.

    Returns the same ``(slice, ground_truth)`` pair as :func:`make_recording`,
    with ``gt.events`` empty. Nothing is scored against planted truth because
    there is none: every detection is a false positive *of this construction*.
    See :data:`NULL_RECORDING` for what that does and does not license.
    """
    return simulate_coordination(
        seed=seed, **{**BENCH_RECORDING, **NULL_RECORDING, **overrides})


def false_positives_per_hour(name: str, seeds=(1, 2, 3), **overrides) -> float:
    """How often a detector fires on a recording containing no coordination.

    Does not depend on the generator being realistic beyond its firing rate:
    there is no planted structure to get wrong, so a detector cannot be
    flattered by an easy benchmark or punished by a hard one.

    What it measures is a detector's response to Poisson background at a given
    rate. It is not a statement about any biological preparation, and it must
    not be read as one.
    """
    hours = 0.0
    total = 0
    for seed in seeds:
        s, _ = make_null_recording(seed)
        det = run_detector(name, s, **overrides)
        onsets = getattr(det, "onset_sec", None)
        onsets = det.locs if onsets is None else onsets
        onsets = np.asarray(onsets, dtype=float)
        total += int(np.isfinite(onsets).sum())
        hours += BENCH_RECORDING["duration_sec"] / 3600.0
    return total / hours if hours else float("nan")


def run_detector(name: str, s, *, rng_seed: int = 20260706, **overrides):
    """Run one detector on a slice at its declared operating point.

    Absorbs the two call shapes — three detectors take a ``Slice`` and run every
    stream, three take one stream's trains plus the extent — so callers work in
    detector names rather than signatures.
    """
    if name not in OPERATING_POINTS:
        raise ValueError(f"unknown detector {name!r} — have {sorted(OPERATING_POINTS)}")
    op = OPERATING_POINTS[name]
    params = {**op.params, **overrides}
    if op.takes_rng:
        params["rng_seed"] = rng_seed

    if name in ("loco", "cicada", "sce"):
        fn = {"loco": loco_detect, "cicada": cicada_detect, "sce": sce_detect}[name]
        return fn(s, **params).streams[STREAM]

    ext = recording_extent(s)
    trains = stream_trains(s.streams[STREAM], ext)
    fn = {"coact": coact_detect, "rate": rate_detect, "sync": sync_detect}[name]
    return fn(trains, ext, **params)


@dataclass
class BenchResult:
    """One detector on one regime, pooled over seeds.

    Pooled counts, not the mean of per-seed ratios: a seed that happens to plant
    fewer events should not carry the same weight as a fuller one, and a seed
    with no detections at all makes precision undefined rather than zero.
    """

    detector: str
    regime: str
    knob_value: float | None = None
    n_planted: int = 0
    n_detected: int = 0
    n_hit: int = 0
    n_fa: int = 0
    hot_fa: int = 0
    distractor_hits: int = 0
    by_frac: dict = field(default_factory=dict)
    seeds: tuple = ()
    tol_sec: float | None = None
    """The match tolerance every pooled score was measured at.

    It travels with the number because it is the number's units. A hit is
    counted at a 1.5 s edge gap against a median realized event 0.80 s wide
    (``docs/learned/tolerance_sweep.png``), so this F1 cannot tell landing on an
    event from landing a second away from it. The *ranking* survives that and
    any comparison drawn from it is safe; a bare F1 implying timing accuracy is
    not. ``None`` where nothing was pooled — a result assembled by hand has no
    tolerance to claim.
    """

    @property
    def n_scored(self) -> int:
        """Detections the headline numbers are computed over — everything
        outside the promiscuity probe. The probe has no planted events, so it
        contributes no hits and its firings would otherwise land entirely in the
        precision denominator."""
        return self.n_detected - self.hot_fa

    @property
    def recall(self) -> float:
        return self.n_hit / self.n_planted if self.n_planted else float("nan")

    @property
    def precision(self) -> float:
        """Precision outside the probe.

        The probe is deliberately severe — a rate six times the background, no
        coordination in it — so its firings dominate any precision it is folded
        into. Fold them in and the headline stops measuring the detector and
        starts measuring how hard the probe was set: CICADA reads F1 0.09 here,
        against 0.68 in the upstream campaign, on 599 hot-window detections out
        of 601 false alarms. That is the project's own cautionary tale — *the
        benchmark, not the detectors, was the original problem* — reached by
        turning one knob too far.

        So the probe gets its own number (:attr:`hot_fa`, gated separately) and
        stays out of this one, which is also how ``score_coord_detection.m``
        reported it upstream.
        """
        return self.n_hit / self.n_scored if self.n_scored else float("nan")

    @property
    def f1(self) -> float:
        r, p = self.recall, self.precision
        if not np.isfinite(r) or not np.isfinite(p) or (r + p) == 0:
            return float("nan")
        return 2 * r * p / (r + p)

    def recall_at(self, frac: float) -> float:
        """Recall at one participation level — the participant-floor axis."""
        n, h = self.by_frac.get(frac, (0, 0))
        return h / n if n else float("nan")

    @property
    def hot_fa_per_min(self) -> float:
        """The promiscuity probe's own number: firings per minute inside the
        dense-but-random block, where by construction there is nothing to find."""
        span = BENCH_RECORDING["hot_window"]
        minutes = (span[1] - span[0]) / 60.0 * max(1, len(self.seeds))
        return self.hot_fa / minutes if minutes else float("nan")

    def summary(self) -> str:
        knob = "" if self.knob_value is None else f" @{self.knob_value:g}"
        by = " ".join(f"{int(f * 100)}%:{self.recall_at(f):.2f}"
                      for f in sorted(self.by_frac, reverse=True))
        # The tolerance rides beside F1, not in a footnote: it is what the F1
        # was measured with, and the two are only meaningful together.
        tol = "" if self.tol_sec is None else f"@{self.tol_sec:g}s"
        return (f"{self.detector:6}/{self.regime:6}{knob}  recall {self.recall:.2f}  "
                f"precision {self.precision:.2f}  F1 {self.f1:.2f}{tol}  "
                f"FA {self.n_fa - self.hot_fa}  |  probe {self.hot_fa_per_min:5.1f}/min  "
                f"distractor {self.distractor_hits}   [{by}]")


@dataclass(frozen=True)
class FoldSplit:
    """The simulated data set, divided once, so every detector is asked the same question.

    A fold split is only worth anything if it is the *same* split for everyone
    being compared. Derive it here and hand it around; deriving it twice invites
    two detectors to be scored on different held-out sets under one heading.

    It is fully determined by ``base_seed``, ``n_folds`` and ``seeds_per_fold``:
    recording seeds run consecutively from the base and are dealt out in
    contiguous blocks. There is no shuffle, so there is no random source for two
    languages to agree about — which is what lets the browser reproduce a split
    the command line made.
    """

    seeds: tuple[int, ...]
    n_folds: int
    seeds_per_fold: int
    base_seed: int

    def fold_of(self, seed: int) -> int:
        """Which fold a recording seed belongs to."""
        i = seed - self.base_seed
        if not 0 <= i < len(self.seeds):
            last = self.base_seed + len(self.seeds) - 1
            raise KeyError(f"seed {seed} is not in this simulated data set "
                           f"({self.base_seed}..{last})")
        return i // self.seeds_per_fold

    def train(self, held: int) -> tuple[int, ...]:
        """Everything outside the held-out fold — what a knob may be fitted on."""
        self._check(held)
        return tuple(s for s in self.seeds if self.fold_of(s) != held)

    def test(self, held: int) -> tuple[int, ...]:
        """The held-out fold — what the reported number is scored on, and the
        only recordings nothing was fitted on."""
        self._check(held)
        return tuple(s for s in self.seeds if self.fold_of(s) == held)

    def _check(self, held: int) -> None:
        if not 0 <= held < self.n_folds:
            raise IndexError(f"fold {held} is outside 0..{self.n_folds - 1}")


def fold_split(*, n_folds: int = 4, seeds_per_fold: int = 3,
               base_seed: int = 1000) -> FoldSplit:
    """Deal ``n_folds * seeds_per_fold`` recording seeds into contiguous folds.

    One fold is refused rather than allowed to degenerate: with a single fold
    there is nothing left to fit on, and what comes back is a held-out score with
    no training set behind it — the exact claim this split exists to make true.
    """
    if n_folds < 2:
        raise ValueError(
            f"n_folds={n_folds} leaves no training data — fitting on three and "
            "scoring on the fourth needs at least two folds")
    if seeds_per_fold < 1:
        raise ValueError(f"seeds_per_fold={seeds_per_fold} makes an empty fold")
    seeds = tuple(base_seed + i for i in range(n_folds * seeds_per_fold))
    return FoldSplit(seeds=seeds, n_folds=n_folds,
                     seeds_per_fold=seeds_per_fold, base_seed=base_seed)


def pool_scores(scores, *, detector: str, regime: str, seeds=(),
                knob_value=None) -> BenchResult:
    """Pool per-seed :class:`~bugarach.score.Score` objects into one result.

    **Anything scored against this bench pools through here** — including
    detectors that are not in :data:`OPERATING_POINTS`: a learned model, a
    candidate, a one-off. That is the point of it being a function.

    A review on 2026-08-16 found the learned models pooled by hand in two tools
    as ``n_hit / n_detected``, while the six went through :func:`evaluate` and
    got :attr:`BenchResult.precision`, which excludes the promiscuity probe. The
    two halves of that report's central comparison sat on different
    denominators under a caption reading *"scored by the same rule"*, and the
    gap is not small — SCE reads precision 0.91 one way and 0.11 the other.
    Pooling is six lines, so it was rewritten instead of imported, and the rule
    for what counts forked in silence. Import this.

    The pooled result carries the tolerance its inputs were scored at. Scores
    measured at different tolerances are not poolable and are refused here
    rather than summed into a number whose units are a mixture — the failure
    would be invisible, since counts add whatever they were counted against.
    """
    out = BenchResult(detector=detector, regime=regime, knob_value=knob_value,
                      seeds=tuple(seeds))
    tols = {float(sc.tol_sec) for sc in scores if sc.tol_sec is not None}
    if len(tols) > 1:
        raise ValueError(
            f"cannot pool scores measured at different tolerances: "
            f"{sorted(tols)} s. A pooled count is only meaningful against one "
            "matching rule.")
    out.tol_sec = tols.pop() if tols else None
    for sc in scores:
        out.n_planted += sc.n_planted
        out.n_detected += sc.n_detected
        out.n_hit += sc.n_hit
        out.n_fa += sc.n_fa
        out.hot_fa += sc.hot_fa
        out.distractor_hits += sc.distractor_hits
        for frac, (n, h) in sc.by_frac.items():
            pn, ph = out.by_frac.get(frac, (0, 0))
            out.by_frac[frac] = (pn + n, ph + h)
    return out


def evaluate(name: str, regime: str, seeds=(1, 2, 3), *, tol_sec: float = 1.5,
             gen: dict | None = None, **overrides) -> BenchResult:
    """Run one detector over several seeds and pool the outcome.

    ``gen`` passes generator settings through to :func:`make_recording`, so a
    caller can hold the difficulty axis (``regime``) fixed while changing the
    recording it runs on — the fitted background out of
    ``docs/learned/generator_spec.json``, say, instead of the bench's flat one.
    Separate from ``**overrides``, which are the *detector's* knobs: the two used
    to be impossible to tell apart because only one of them existed.
    """
    scores = []
    for seed in seeds:
        s, gt = make_recording(regime, seed, **(gen or {}))
        det = run_detector(name, s, **overrides)
        scores.append(score_stream(gt, det, tol_sec=tol_sec))
    return pool_scores(scores, detector=name, regime=regime, seeds=seeds,
                       knob_value=overrides.get(OPERATING_POINTS[name].knob))


TOLERANCE_GRID = (0.1, 0.15, 0.25, 0.4, 0.5, 0.75, 1.0, 1.25, 1.5, 2.0, 2.5, 3.0)
"""Edge gaps to score at, spanning well under and well over the shipped 1.5 s.

**Reported as a curve rather than chosen as a constant** — the practice DOSED
uses (Chambon et al. 2019, on the coordination shelf, recorded there as
*"bugarach's open question, answered"*): report precision, recall and F1 across a
swept matching tolerance, so how much timing slack a score was granted is a
**visible axis** instead of a hidden constant.

Measured here, that costs almost nothing and settles an argument. Five of the six
detectors are flat from **0.75 s** upward and the ranking does not change between
0.4 s and 2.0 s, so the shipped 1.5 s sits deep in the plateau and no comparison
rests on it. The exception is **binned SCE**, still climbing at 1.5 s because its
10 s bins make its detections coarse and only a loose tolerance credits them —
which is exactly what a single number hides and a curve shows.

Same grid as ``docs/learned/tolerance_sweep.json``, so figures and bench runs
describe one sweep rather than two.
"""


def evaluate_curve(name: str, regime: str, seeds=(1, 2, 3), *,
                   tols=TOLERANCE_GRID, gen: dict | None = None,
                   **overrides) -> dict[float, BenchResult]:
    """One :class:`BenchResult` per matching tolerance — the curve, not a point.

    Detection runs **once per seed** and every tolerance scores those same
    detections, so the curve isolates the scoring rule. Re-detecting per
    tolerance would fold detector RNG into what is meant to be a property of the
    scorer.
    """
    per_tol: dict[float, list] = {float(t): [] for t in tols}
    for seed in seeds:
        s, gt = make_recording(regime, seed, **(gen or {}))
        det = run_detector(name, s, **overrides)
        for t in tols:
            per_tol[float(t)].append(score_stream(gt, det, tol_sec=float(t)))
    return {t: pool_scores(v, detector=name, regime=regime, seeds=seeds,
                           knob_value=overrides.get(OPERATING_POINTS[name].knob))
            for t, v in per_tol.items()}


def plateau_tol(curve: dict[float, BenchResult], *, eps: float = 1e-9):
    """The smallest tolerance whose F1 already equals the curve's best, or None.

    ``None`` means the detector was **still climbing at the widest tolerance
    scored**: its score depends on how much slack it was granted, so quoting one
    F1 for it asserts a timing accuracy it does not have. That is not a defect to
    fix by widening the grid — it is a fact about the detector, and the honest
    report names it rather than averaging it away.
    """
    tols = sorted(curve)
    best = max(curve[t].f1 for t in tols)
    if curve[tols[-1]].f1 < best - eps:
        return None                    # non-monotone: the widest is not the best
    if len(tols) > 1 and curve[tols[-1]].f1 - curve[tols[-2]].f1 > eps:
        return None                    # still rising where the grid stopped
    return next(t for t in tols if curve[t].f1 >= best - eps)


def describe_curve(curve: dict[float, BenchResult]) -> str:
    """An F1 that carries the tolerance it needed — for anything human-facing."""
    tols = sorted(curve)
    best = max(curve[t].f1 for t in tols)
    flat = plateau_tol(curve)
    if flat is None:
        return (f"F1 {curve[tols[-1]].f1:.3f} at {tols[-1]:g}s and STILL "
                "CLIMBING — this score depends on the matching tolerance")
    return f"F1 {best:.3f}, flat from {flat:g}s"


BACKGROUND_GRID = (0.0026, 0.0052, 0.0080, 0.0120, 0.0190, 0.0280, 0.0400)
"""Per-ROI background rates to score across — the SECOND hidden constant.

:data:`TOLERANCE_GRID` above dissolved the first one: how much timing slack a
score was granted became a visible axis instead of an inherited number. **The
background rate is the same defect and a larger one.** An operating point is
chosen at one point on this axis and quoted as though it held across it, and it
does not: on the same 120 events CoactDetect recalls **0.817** at the quiet
endpoint and **0.560** at the busy one — 0.26 of recall across a 3.7-fold rate
change that is only the interquartile spread of *untreated* slices
(``docs/RESET.md`` §6).

The grid brackets :data:`REGIMES` rather than reproducing it: p25 (0.0052) and
p75 (0.0190) are both on it, with a point below the quiet endpoint and two above
the busy one, because a curve that stops at the endpoints cannot show whether it
was about to fall off one. **``REGIMES`` is not changed by this** — moving the
axis is a recalibration; this reports across the axis that already exists.

**Why this matters more than the tolerance did.** Five of six detectors turned
out flat across the tolerance grid, so that constant was granting slack nobody
used and no comparison rested on it. Nothing is flat across this one. And the
treatment contrast the whole loop builds toward compares two windows at
*different* backgrounds, so a detector's sensitivity to this axis is confounded
with the effect being measured — and until now nothing reported it.
"""


def evaluate_background_curve(name: str, regime: str, seeds=(1, 2, 3), *,
                              rates=BACKGROUND_GRID, tol_sec: float = 1.5,
                              gen: dict | None = None,
                              **overrides) -> dict[float, BenchResult]:
    """One :class:`BenchResult` per background rate — the curve, not a point.

    **Unlike :func:`evaluate_curve` this re-generates the recording at every
    point, and it has to.** The tolerance curve scores one set of detections
    several ways, so it isolates the scoring rule. The background is a property
    of the *recording*, so changing it means a different recording. The planted
    events are held fixed by the seed — same count, same times, same recruitment
    — so what moves across the curve is the field they sit in and nothing else.

    ``regime`` still selects the base recording and ``gen`` still passes generator
    settings through, so a caller can put a fitted background *shape* underneath
    and sweep its level. ``bg_rate_hz`` from either is overridden per point, which
    is the whole operation.
    """
    out: dict[float, BenchResult] = {}
    for rate in rates:
        g = dict(gen or {})
        g["bg_rate_hz"] = float(rate)
        scores = []
        for seed in seeds:
            s, gt = make_recording(regime, seed, **g)
            det = run_detector(name, s, **overrides)
            scores.append(score_stream(gt, det, tol_sec=float(tol_sec)))
        out[float(rate)] = pool_scores(
            scores, detector=name, regime=regime, seeds=seeds,
            knob_value=overrides.get(OPERATING_POINTS[name].knob))
    return out


def background_spread(curve: dict[float, BenchResult]) -> float:
    """How much F1 moves across the axis — the number a bare F1 hides.

    Deliberately the full range rather than a slope or a fitted coefficient: the
    question a reader actually has is *"how wrong is this number if my slices are
    busier than the ones it was measured on"*, and the range answers it without
    assuming the curve has a shape.
    """
    f1s = [curve[r].f1 for r in sorted(curve)]
    return max(f1s) - min(f1s)


BACKGROUND_TOLERABLE_SPREAD = 0.05
"""Above this much movement across the grid, one F1 is not reportable alone.

Set at the scale of the differences the bake-off asks readers to believe: the top
two detectors there are **0.017** apart, so a score that swings several times that
with the background cannot be compared against its neighbour without naming where
on the axis both were measured.
"""


def describe_background(curve: dict[float, BenchResult]) -> str:
    """An F1 that carries the background it was measured at — human-facing.

    The counterpart of :func:`describe_curve`, refusing on the same principle:
    when the score still depends on the axis, say so rather than hand over a
    number that reads like a property of the detector.

    In practice this refuses for nearly every detector, and **that is the finding
    rather than a threshold set too tight** — the tolerance version usually
    settles, which is exactly the contrast worth seeing.
    """
    rates = sorted(curve)
    lo, hi = curve[rates[0]].f1, curve[rates[-1]].f1
    spread = background_spread(curve)
    if spread > BACKGROUND_TOLERABLE_SPREAD:
        return (f"F1 {lo:.3f} at {rates[0]*1000:g} mHz/ROI to {hi:.3f} at "
                f"{rates[-1]*1000:g} — spread {spread:.3f}, so this score "
                "depends on the background rate and is NOT one number")
    return (f"F1 {max(curve[r].f1 for r in rates):.3f}, flat across "
            f"{rates[0]*1000:g}–{rates[-1]*1000:g} mHz/ROI (spread {spread:.3f})")


def sweep(name: str, regime: str, seeds=(1, 2, 3), values=None, *,
          gen: dict | None = None) -> list[BenchResult]:
    """The sensitivity curve: one :class:`BenchResult` per knob value."""
    op = OPERATING_POINTS[name]
    values = op.grid if values is None else values
    return [evaluate(name, regime, seeds, gen=gen, **{op.knob: v})
            for v in values]


class EdgeOfRange(ValueError):
    """The best point found sits on the boundary of the grid that was searched.

    Not a warning. An optimum at the edge is not an optimum — it is the search
    telling you it stopped too early, and reporting it as a calibrated point is
    how a boundary value once got published upstream as one.
    """


MAX_PROBE_PER_MIN = {
    "coact": 1.0,      # measured: 0.0
    "loco": 1.0,       # measured: 0.1
    "sync": 1.0,       # measured: 0.2
    "rate": 2.0,       # measured: 0.6
    "sce": 9.0,        # measured: 5.6
    "cicada": 25.0,    # measured: 17.3 — still the most rate-fooled of the six
}
"""Firings per minute each detector may make inside a block containing nothing.

**Measured baselines, not aspirations** — the convention the regime-shift budgets
use. A detector that improves past its ceiling should have the ceiling tightened
in the commit that improves it.

**These lived in `tests/test_bench.py` until 2026-08-22, and that was the defect.**
The test caught a regression at the *shipped* operating point, but
:func:`pick_operating_point` — the thing that *chooses* the shipped operating
point — had no notion of an acceptable probe rate. So a sweep could select a
promiscuous setting and nothing objected: the probe could fail a detector, but it
could not fail a **calibration**, which is where operating points come from.

What is deliberately still true: the probe stays **out of F1**. Folding it in makes
the headline measure how hard the probe was set rather than how good the detector
is — CICADA reads F1 0.09 that way against 0.68 upstream, on 599 hot-window
detections out of 601 false alarms. The fix for "the alarm cannot ring" is to give
the probe a gate at selection time, not to corrupt the score.
`docs/todo/2026-08-16-promiscuity-probe-cannot-fail.md`.
"""


class TooPromiscuous(ValueError):
    """The best-scoring point on the sweep fires too often on nothing.

    Raised by :func:`pick_operating_point` when the F1-optimum exceeds that
    detector's :data:`MAX_PROBE_PER_MIN` ceiling. A third refusal for a third
    remedy: the grid is fine and the knob is binding, but the value that wins on
    F1 wins by firing into a block where nothing was planted.
    """


class DegenerateSweep(ValueError):
    """Every point on the grid scored identically — the knob did nothing.

    Distinct from :class:`EdgeOfRange` because the remedy is the opposite. There
    the grid was too narrow and the answer is to widen it; here the grid is
    irrelevant, because the parameter being swept is **not the one deciding the
    answer**, and widening it only produces more identical rows.

    The case this was written for is SPIKE-synch, recorded in
    ``docs/todo/2026-08-18-spike-synch-knob-may-not-be-the-knob.md``: the sweep
    moves ``C_threshold`` over ``(0.005 … 0.12)`` while ``C_min`` sits pinned at
    0.1 above most of that range, so the bin that *opens* an event gets cheaper
    while every bin that *sustains* one must still clear 0.1. The synchrony
    profile is also quantised at ``k/(n-1)``, so on a 30-ROI field every
    threshold below 1/29 is the same threshold. On a default simulation every
    value on the grid returned four detections and eleven misses.

    :func:`pick_operating_point` could not see it. Its plateau rule — an optimum
    is trustworthy if *some* optimal point has neighbours on both sides — is
    right for a **saturating** plateau (LoCo at F1 1.00 from 99.99 upward) and
    cannot distinguish that from a curve flat because nothing is happening: when
    every point ties, the whole grid is "optimal", interior points exist, and the
    first is returned as a calibrated setting. A boundary answer wearing a
    plateau's clothes. That is how SPIKE-synch answered 3 of 3 folds on the
    scoreboard while measuring nothing.

    **The test is a total tie, not "flat within noise"** — a stricter rule than
    first proposed, and deliberately. Partial ties are real and informative: the
    bench's own ``sweep("sync", "baseline_busy")`` moves F1 from 0.58 to 0.48
    across the upper half with the bottom three tied. Refusing "nearly flat"
    would need a noise model nobody has, and would refuse curves that carry
    information. An exact tie across every point cannot be a measurement of
    anything, so it is the case that can be refused without one.
    """


def _gate_on_probe(best: BenchResult, ceiling: float | None) -> BenchResult:
    """Refuse a winner that got there by firing where nothing was planted.

    ``-1.0`` is the sentinel for "look it up"; ``None`` disables the gate. The
    lookup is by detector name, so a curve for something not in
    :data:`MAX_PROBE_PER_MIN` passes rather than crashing — a new detector should
    not be un-calibratable until someone writes it a budget.
    """
    if ceiling is None:
        return best
    if ceiling == -1.0:
        ceiling = MAX_PROBE_PER_MIN.get(best.detector)
        if ceiling is None:
            return best
    rate = best.hot_fa_per_min
    if not np.isfinite(rate) or rate <= ceiling:
        return best
    raise TooPromiscuous(
        f"{best.detector}/{best.regime}: the best F1 on this sweep "
        f"({best.f1:.2f} at {best.knob_value:g}) fires {rate:.1f} times/min "
        f"inside a block containing no planted events, against a ceiling of "
        f"{ceiling:g}. That setting wins on F1 by keying on rate, so it is not "
        "an operating point. Tighten the detector or raise the ceiling "
        "deliberately — do not take the runner-up silently")


def pick_operating_point(curve: list[BenchResult], *,
                         max_probe_per_min: float | None = -1.0) -> BenchResult:
    """The F1-optimal point on a sweep, refusing a boundary answer.

    A *plateau* that reaches the edge is not a boundary answer. LoCo saturates
    at F1 1.00 from ``threshold_pctile`` 99.99 upward on this bench — recall and
    precision both stay at 1.00 — so the top of any grid is optimal and no
    amount of widening produces an interior peak. What makes an optimum
    trustworthy is that some optimal point has neighbours on both sides, not
    that the single argmax happens to sit inside. So the test is: if any point
    achieving the best F1 is interior, the grid bracketed the optimum and the
    first such point is returned; only when *every* optimal point is at an end
    is the search still climbing when it stopped.

    ``max_probe_per_min`` gates the choice on the **promiscuity probe**, which is
    what makes that probe able to fail a calibration rather than only a shipped
    setting. Default ``-1.0`` means *look the detector up in*
    :data:`MAX_PROBE_PER_MIN`; pass a number to override, or ``None`` to select on
    F1 alone the way this did before 2026-08-22.

    The gate is applied **after** the edge and degeneracy checks and **before**
    the answer is returned, so a sweep whose winner fires into a block containing
    nothing raises :class:`TooPromiscuous` instead of quietly becoming an
    operating point. It does not re-rank: a promiscuous winner is a refusal, not
    an invitation to take second place, because silently accepting a worse point
    is how a calibration stops being reproducible.
    """
    scored = [r for r in curve if np.isfinite(r.f1)]
    if not scored:
        raise ValueError("no point on the curve has a defined F1")
    if len(scored) == 1:
        return _gate_on_probe(scored[0], max_probe_per_min)

    best_f1 = max(r.f1 for r in scored)
    # Before asking WHERE the optimum sits, ask whether the sweep found one at
    # all. A grid whose every point ties has not measured the knob; see
    # DegenerateSweep. Checked first because such a curve also passes the
    # interior test below, which is exactly how it went unnoticed.
    if best_f1 - min(r.f1 for r in scored) <= 1e-9:
        d = scored[0]
        raise DegenerateSweep(
            f"{d.detector}/{d.regime}: every point on the "
            f"{OPERATING_POINTS[d.detector].knob} grid scores F1 {best_f1:.4f} "
            f"({len(scored)} values, {scored[0].knob_value:g}–"
            f"{scored[-1].knob_value:g}) — the swept parameter is not what is "
            "deciding the answer, so no value of it is an operating point. "
            "Widening this grid will not help; sweep the binding parameter "
            "instead, or sweep them together")
    optimal = [r for r in scored if r.f1 >= best_f1 - 1e-9]
    interior = [r for r in optimal if r is not scored[0] and r is not scored[-1]]
    if interior:
        return _gate_on_probe(interior[0], max_probe_per_min)

    end = "low" if optimal[0] is scored[0] else "high"
    best = optimal[0]
    raise EdgeOfRange(
        f"{best.detector}/{best.regime}: F1 peaks at the {end} end of the "
        f"{best.detector} {OPERATING_POINTS[best.detector].knob} grid "
        f"({best.knob_value:g}, F1 {best.f1:.2f}) — the search was still "
        "climbing when it stopped; widen the grid before calling this an "
        "operating point")


MEASURED_BURST_SHAPE = (1.547, 1.388)
"""Gamma shapes of the per-bin rate multiplier, for `MEASURED_BURST_BINS`.

The temporal partner of `MEASURED_RATE_SHAPE`, and the same estimator turned
ninety degrees. There, ROIs differed from one another. Here **one ROI is followed
across time bins**: under a constant rate its counts would be Poisson with
variance equal to mean, and a bursty ROI is over-dispersed. Fixing the ROI is
what makes the estimate clean — rate heterogeneity across ROIs is held constant
inside one of them, so the over-dispersion left over is temporal.

Maximum likelihood over the ROIs carrying at least 10 events in their baseline
window (784 of them, across 85 windows), each ROI keeping its own mean.
Re-derive with `python tools/fit_background_shape.py`.

**Two scales, because one cannot work.** A single bin width draws independent
bins, so its over-dispersion stops growing once the window exceeds the bin. Real
ROIs keep getting more over-dispersed the wider you look:

| variance/mean | 30 s | 60 s | 120 s | 300 s |
|---|---|---|---|---|
| real | 1.82 | 2.61 | 3.88 | 5.69 |
| flat background | 0.99 | 0.95 | 0.93 | 0.74 |
| these two scales | 1.87 | 2.76 | 3.04 | 4.44 |

Fine scales are reproduced; the coarse end is still short, so a busy stretch of
several minutes is shorter here than in real tissue.

⚠ The two shapes are fitted **per scale independently** and then multiplied. A
joint fit would not give these two numbers, and the agreement above is partly
that approximation being forgiving. It is an approximation on purpose — the
joint likelihood has no closed form — and it is why the coarse end is the half
that misses.

⚠ **Not wired into the bench**, exactly like `MEASURED_RATE_SHAPE`.
`BENCH_RECORDING` still runs a homogeneous background in both axes.
"""

MEASURED_BURST_BINS = (300.0, 60.0)
"""Bin widths (s) the shapes in `MEASURED_BURST_SHAPE` were fitted at."""
