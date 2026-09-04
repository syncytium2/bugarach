# Proposal — one parameter object, carried end to end

**Status: proposal, for review. Nothing built.** Written 2026-08-16, revised
the same day against PR #46 (merged) and PR #48 (open), because
several sessions are building against `simulate_coordination` *now*, and the
window in which its surface can change cheaply closes as they do.

## The problem, stated as a number

`simulate_coordination` takes **25 keyword parameters**. Four describe the
background: `bg_rate_hz`, `bg_rate_shape`, `bg_burst_shape`, `bg_burst_bin_sec`.
Three of those four landed within the last two days — `bg_rate_shape` on
2026-08-15, the two burst fields on 2026-08-16 — as the background model learned
two things about real recordings it had not known.

That rate of change is not a defect — it is the project working. The defect is
that it arrives through the **call site of every consumer**. A slow on/off
modulation, which the data is already asking for (see "what is still missing"),
adds two more. Each addition is a breaking change for anyone who named the
parameters individually, and the sessions building the workflow app have said
they intend to call the generator by keyword.

The parameters are internal modelling choices. They are in the public signature.

## What changes

Pass **one object** instead of N parameters, and let the same object be what the
fitting stage produces:

```python
spec = fit_recording_spec(folder)          # measured from the user's data
sim, gt = simulate_coordination(spec, seed=1)
```

Adding a third background axis then changes no call site. A caller who passed a
fitted spec gets the improvement; a caller who passed nothing keeps the flat
default they already had.

⚠ **Be honest about who that protects.** A caller who *receives* a spec and hands
it on is insulated, and that is every stage of the workflow app — fit, generate,
optimise, train, export. A caller who **constructs** a `BackgroundModel` by naming
its fields is as coupled to the model as it is today; it has just moved which
file the coupling lives in. The claim is not that the model stops changing. It is
that the places which do not care stop being made to care, and the places which
do care become countable — a grep for `BackgroundModel(` instead of a grep for
four keyword names that will be six.

### The objects

```python
@dataclass(frozen=True)
class BackgroundModel:
    """How background events are distributed. Every field is fittable."""
    rate_hz: float                              # MEAN per-ROI rate
    rate_shape: float | None = None             # Gamma across ROIs
    burst_shape: tuple[float, ...] = ()         # Gamma per time scale
    burst_bin_sec: tuple[float, ...] = ()       # the scales, coarsest first

@dataclass(frozen=True)
class CoordinationModel:
    """The planted events. Fittable in principle; see the caveats."""
    participation: tuple[float, ...]
    n_per_level: tuple[int, ...]
    jitter_sec: float
    min_sep_sec: float
    interval_cv: float = 1.0
    spacing: str = "renewal"

@dataclass(frozen=True)
class RecordingSpec:
    """What one recording looks like. This is the thing a dataset is fitted to."""
    n_roi: int
    duration_sec: float
    grid_sec: float                             # acquisition interval; see §6
    background: BackgroundModel
    coordination: CoordinationModel
```

### What deliberately stays out

The **promiscuity probe** and the **distractors** are not in `RecordingSpec`.
They are not properties of a real recording and cannot be fitted from one — they
are test constructs, deliberately planted to catch a detector that keys on rate
or on coincidence. They belong to the bench, which is a different thing:

> **The generator makes data. The bench is a standard** — a pinned recipe, pinned
> detector settings, and a scoring rule — and it *calls* the generator. It is
> the yardstick; the generator marks the ruler.

Keeping the probe out of the spec is what makes that boundary hold in code rather
than in prose. It also answers a confusion this project has already had out loud:
`bench.make_recording()` is not a background model. Measured here against
`make_null_recording` over three seeds, **31–67% of its realized rate is not
background** (67.2% in the quiet regime, 30.6% in the busy one) — the planted
events and the probe are most of the quiet regime's activity.

## Migration, since everyone is mid-flight

Three commitments, in order of how much they cost the people already building:

1. **The keyword form keeps working for one release.** `simulate_coordination`
   accepts either a spec or the current keywords, never both; passing keywords
   emits a `DeprecationWarning` naming the replacement field. Nobody's branch
   breaks on merge.
2. **A mechanical translation exists both ways** — `BackgroundModel.from_kwargs()`
   and `spec.as_kwargs()` — so a caller can move one call site at a time and a
   test can prove the two paths produce identical output for a given seed. That
   equality is the migration's acceptance test, not a promise in a document.
3. **A sapper rule refuses NEW `bg_*` keyword call sites in `src/`** once the
   deprecation lands, because a rule that depends on being remembered is not a
   gate. Prose in this file is the weakest form of the same instruction.

The keyword form is removed when the last call site is gone, not on a date.

## What this unlocks in each stage

| stage | what the spec does for it |
|---|---|
| **user data in** | the fitting stage's *output type* is `RecordingSpec` — no parameter plumbing between measuring and generating, and no caller needs to know the model to name its fields |
| **generator** | new background axes stop being breaking changes |
| **detector optimization** | a sweep records the spec it swept against, so two operating points are comparable only when their specs match — the check becomes possible instead of assumed |
| **DL training** | a trained model carries the spec it was trained on, and since PR #46 the labels carry the onsets each participant actually got rather than a parametric restatement of the request — so "targeted to this dataset" becomes a checkable claim about a describable training set rather than a story |
| **graphics / export** | every figure and every exported row can name the spec behind it |

That last column is the one worth arguing about, because the project has already
been bitten by its absence: **every F1 in this repo was measured on a background
that is flat in both axes, and no artifact says so.** The numbers are not wrong;
they are unlabelled. A spec recorded on the artifact makes "which world was this
measured in" answerable without reading the commit that produced it.

## Fitting — what the estimator must return

Not a scalar per axis. The temporal term is a **curve**: dispersion at several
bin widths, with the widths, because the generator takes a sequence of scales and
because the *growth* of that curve is what says how many scales the data needs.
Real windows run variance/mean 1.81 / 2.60 / 3.87 / 5.68 at 30 / 60 / 120 / 300 s;
a single scale cannot reproduce that at any shape.

Three constraints on the fitting stage that are not negotiable:

- **Baseline windows only** (FOUNDATIONS §9). Treatments are what the instruments
  are pointed at; fitting from them assumes the answer, and *"if we simulate
  treatment for a training set, we lose the consequence of the treatment"*.
- **Absence of a region annotation means "cannot fit", not "fit everything".**
  FOUNDATIONS §4 gives an un-annotated recording one implicit whole-recording
  window, so a folder of unlabelled treated recordings would otherwise be fitted
  silently and entirely as baseline. Refusing a *labelled* treatment window does
  not protect against this; only requiring a positive assertion does.
- **`grid_sec` cannot be fitted and must be supplied.** It is the acquisition
  sampling interval and the onset stores do not carry it, so the 0.1 s fallback
  is a guess about someone's microscope. It belongs in the spec with no default.

  FOUNDATIONS §6 currently makes it the caller's responsibility *at detection
  time*, with a warning on the fallback. **PR #48 reverses that** — Tony:
  *"we cannot allow data loading without the user specifying a dt"* — moving the
  check to a refusal at the load boundary, because a warning fires after the
  trace is computed and 0.1 s being genuinely this lab's rate is what teaches a
  team to filter it out. That reversal strengthens this bullet rather than
  changing it: if a dt is guaranteed at load, the spec has a real value to carry
  instead of a default to apologise for.

  ⚠ The generator's `grid_sec` and a detector's `grid_dt` mean the same physical
  quantity and are **not** the same knob. `grid_sec` quantizes planted onsets
  through `matlab_round` at construction, so it decides which bin an event lands
  in before any detector sees it. One spec field, two consumers, and the fitting
  stage must not assume setting one sets the other.

## What is still missing from the model, and why it belongs here

The generator reproduces the fine-scale structure of a real field and not the
coarse. Real ROIs go quiet for minutes at a time; the two-scale model makes an
ROI busy in patches rather than busy and then silent. Measured on one slice: the
real busiest ROI puts **57%** of its events into three minutes and the generated
one **27%**, while holding a comparable share of the recording (28% against 26%).
The totals are not matched — 178 events against 214 — which is the point: the
concentration across ROIs is right and its distribution in time is not.

Fixing that is a third axis — slow on/off epochs — and under the current design
it is two more keyword parameters and a fourth breaking change. Under this
proposal it is a field on `BackgroundModel` and nobody's call site moves. **That
is the argument for doing this now rather than after.**

## Staging

1. The objects, `from_kwargs` / `as_kwargs`, and the equality test. No behaviour
   change, no call site touched.
2. `simulate_coordination(spec=...)` accepted alongside keywords; deprecation
   warning; `bench` moved to the spec form as the first consumer.
3. The fitting stage returns a `RecordingSpec`.
4. Sapper rule against new `bg_*` call sites.
5. The slow-epoch axis, as the first change that costs nobody anything.

## Open questions for Tony

- **Do `n_roi` / `duration_sec` / `grid_sec` belong in the same object as the
  models?** They describe the recording rather than the process. One spec is
  simpler to hand around; two is honest about what is fitted versus what is
  configured.
- **Is the deprecation window worth its cost?** Cutting the keywords immediately
  is a smaller surface and a worse afternoon for three sessions.
- **Should the bench move onto a fitted background as part of this, or after?**
  Moving it re-derives every operating point and every score in the package. Doing
  it inside this change conflates an API migration with a recalibration; doing it
  after means the spec ships while the standard still describes a world nothing
  was recorded in.
