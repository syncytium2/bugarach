# Run records — what this conversation added to ADR-0005, and what it contradicts

> **Status: three proposals and one tension, against an accepted ADR.** Not a design
> of its own. [ADR-0005](adr/0005-detectors-and-models-are-objects-in-a-folder.md),
> accepted 2026-08-29, already decided the run-record architecture; this file exists
> because a design conversation on 2026-08-31 re-derived much of it, added three
> things it does not cover, and produced one proposal that **cuts against it**.
>
> **Not murderboarded** — working material for sessions in this tree. If any of it
> reaches an outside reader, murderboard that artifact first.

## Read this first: it was mostly already decided

Tony, 2026-08-31, looking at the tables this conversation produced: *"reinventing the
wheel. cfar all over again."*

He was right, and the wheel was **two days old and his own**. ADR-0005's closing
section — *"The spine: every artifact names the input it came from"* — already
specifies the layout:

```
workspace/
  detectors/     the objects
  models/        weights + arch descriptor
  data/          export folder(s)
  runs/<id>/
    settings.json   operating points + provenance{ fitted_on, detector versions }
    weights/        + provenance{ trained_on, trainer }
    bench.json      + provenance{ fitted_on, scored_on }
    detections.csv  run.json
```

Four questions this conversation spent time treating as open are answered there:

| question re-opened on 2026-08-31 | ADR-0005's answer |
|---|---|
| per-run subfolder, or an id column on shared files? | **subfolder** — `runs/<id>/` |
| what identifies the dataset a thing was fitted on? | **`fitted_on` / `trained_on` / `scored_on`**, one per artifact |
| what identifies a detector version? | **`detector versions`**, in `settings.json`'s provenance block |
| non-Chromium browsers? | **§6** — Chromium is the supported target; Firefox and Safari fall back to downloads, and the page **says which it is doing** |

And the payoff is already stated there: once every artifact names its input, *"the
cross-dataset test is not a feature to add — it is a question the artifacts already
answer, and the bench can refuse an invalid comparison rather than silently produce
one."*

**The lesson is not that the conversation was wasted.** It is that a decision
recorded in an ADR did not reach a session reasoning about the same problem two days
later, which is the failure mode this repo keeps paying for. The prior-art suspicion
was correct; the prior art was local.

⚠ **The literature question is still open, and separately.** Experiment tracking,
run provenance and settings-versioning are a developed field, and `rate_detect`,
`coact_detect` and `loco_detect` converging on CFAR unknowingly
([`detector_history.md`](detector_history.md) §4) is this project's own proof that
arriving somewhere by reasoning is no evidence nobody is there. A pass over the
experiment-tracking tools, the provenance vocabularies and the neuroscience data
standards has **not** been run. Adopting an existing vocabulary would be the better
outcome — a name someone else has already defended is worth more than one we argued
ourselves into.

---

## 1 · New: `detector` absorbs the nets — and this contradicts ADR-0005

Tony, 2026-08-31: *"maybe expand detector to include the coded detectors (loco etc)
and the nets (tube etc)."*

The term already supports it. A detector is defined by what it **emits**, not by how
it is built — the site's own line is *"detectors flag the moments when many ROIs fire
together"* — so a trained network emitting coordinated-event calls satisfies the
definition and always did. The output contract costs nothing: `detections.csv`'s
`detector` column means "which detector called it", so the domain grows and the
meaning does not, and consumers read that column as an opaque string. One wrinkle:
the column carries the **key**, not the display name — `cicada` in the file, *locust*
on the screen ([ADR-0002](adr/0002-the-sixth-detector-is-called-locust.md)) — so the
union is a namespace of keys.

**Where it collides.** ADR-0005's workspace has `detectors/` and `models/` as two
top-level folders, and its §4 keeps them apart deliberately — the browser trainer is
a *second* trainer, weights are stamped browser-trained, and the bench refuses to
compare across trainers. That separation is about **provenance of weights**, which a
knob sweep does not have. So the union is a naming decision at the *emitting*
boundary, and it must not be read as permission to merge the two folders or to let a
net's weights and a detector's knob share one provenance shape.

**Proposed resolution:** one namespace, two homes. The folders stay (different
dependencies, different fit paths, different provenance blocks); the `detector` term
and the key namespace span both.

**The gap this opens, which nothing catches today.** Nothing stops someone
registering a net called `rate`. `test_registries_do_not_drift.py` checks that the
browser offers every detector the library has, and that the bake-off selection is a
subset of what is registered — neither catches a collision *across* the two
registries. Under one namespace that collision is silent and lands in the `detector`
column and in every run id keyed on it. The check is cheap and belongs in that file.

## 2 · New: a genus for fitting, and two species that already exist

| term | means | covers | status |
|---|---|---|---|
| **fit** | genus — settings chosen from data rather than by a person | both halves | **proposed**; `opt` is the alternative |
| **calibrate** | species — sweep one declared knob | the coded six | already in the tree |
| **train** | species — gradient descent on weights | the nets | already in the tree |
| **detect** | apply fitted settings to a recording and emit calls | both | already in the tree |

The genus is needed *because* of §1. If detectors were nets alone, `train` would be
exact; once one term spans a knob sweep and a gradient descent, the run that produced
the settings needs a word one level up. `fair_bakeoff.py` already uses it that way —
its shared corpus is `fit_cache`, whose docstring reads *"The FITTING corpus.
Calibration, training and threshold-picking only."*

**`train` and `opt` are not interchangeable.** `train` is a species and `opt` would be
a genus. `fair_bakeoff.py`'s first line keeps them apart — *"Calibrate the six and
train the learned models"* — and no code here says "train" about `loco`.

**Both halves pick an operating point**, which is what makes one genus honest:

| | the coded six | the nets |
|---|---|---|
| fit parameters | sweep one declared knob | gradient descent on 1,149 weights |
| pick an operating point | ✓ | ✓ |

**Costs on each side.** `fit` may read to a statistician as though the six were fitted
*models* — `detector_settings.csv` answers that on sight, one parameter and one value
per row, but it is the objection. `opt` imports a word with a narrower existing
meaning upstream: `optimize_detectors.m` in the MATLAB producer suite and
`tools/make_optimization_figure.py` here. Against that, *optimize* is the word in
Tony's original webapp request (*"train and optimize"*).

## 3 · New: one run id is not enough, and ADR-0005 has one

This is the substantive gap. ADR-0005's `runs/<id>/` bundles `settings.json`,
`weights/`, `bench.json` and `detections.csv` under a single id — which is right for
one workspace running the whole loop in order, and wrong the first time someone
**detects today using settings fitted last month**.

The two have different scopes:

- a **fit run** is per (detector, dataset) and produces settings;
- a **detect run** is per (folder, set of detectors) and produces calls.

So one detection pass over six detectors consumes **six** fit runs. In
`detections.csv` that means `detect_run_id` is constant down the file while
`fit_run_id` varies with the `detector` column — they cannot be one column, and a row
carrying only one of them breaks the chain:

> *these detections came from **detect run X**, over this folder, using settings from
> **fit run Y**, which was fitted on **`fitted_on` Z** at **detector version V**.*

ADR-0005 names the last two already. This adds the first two, and it is compatible
with its layout rather than a replacement for it: `runs/<id>/` stays, and a detect run
records the fit run ids it consumed rather than assuming its own directory produced
them.

**Naming, open:** `fit_run_id` / `detect_run_id`, or `opt_run_id` / `detect_run_id`.
`opt`/`detect` is asymmetric — one abbreviates, one does not — and both names land in
an output contract that interface2 and fireflies read, so it is an announced revision
and expensive to reverse. Same lesson as `cicada` staying `cicada` forever.

---

## Already settled, restated only so it is not re-litigated

| | | source |
|---|---|---|
| runs live on the **user's** machine, beside their output; we store nothing | Tony, 2026-08-31 | this conversation |
| the **page** writes, not the server — it holds the directory handle; the server opens one module constant and no request may name a path | | [ADR-0001](adr/0001-the-lab-server.md) |
| Chromium is the super-user target; elsewhere, downloads, and the page says so | | ADR-0005 §6 |
| user-supplied detector files load Worker-sandboxed, on an explicit action | | ADR-0005 §5 |
| the browser trainer is a **second** trainer; weights stamped, comparisons refused across trainers | | ADR-0005 §4 |
| our own runs are synthetic-only, in the repo and the darkroom | | FOUNDATIONS §5 |

**Two run stores, different owners, and only one is ours.** A visitor's runs are their
data on their machine and never come back — though the same page that wrote them can
read them back from the granted folder and draw their history locally. Ours are
synthetic-only and published, and are what a detector's history page shows. The
consequence worth stating in public: **bugarach can never aggregate across labs, and
should not want to.**

## What preserving the originals requires

Tony, 2026-08-31: *"these are now research tools in their own right with an origin
story. the original versions should be saved for historical review and comparisons."*

[`forks.md`](forks.md) §1 has mechanism changes landing as keyword flags whose default
reproduces the MATLAB original. That was right while parity was the contract;
[ADR-0003](adr/0003-parity-was-the-inheritance-not-the-contract.md) loosened it to
modify-at-will with an enumerated fork entry. Edit-at-will goes past both: flags
accumulate combinatorially on one function, and **no flag combination is addressable
as *the thing that scored 0.62 in March***.

ADR-0005's `detector versions` field is the record; what is not decided is whether a
version is also **addressable in the registry** — `rate@v1` runnable beside `rate@v4`
— which is what turns an original into a row in a table rather than an excavation. It
would also put the parity fixtures where FOUNDATIONS §2 already says they belong: *"the
before in every 'I improved this' claim."* A v0 row, not a gate.

## What this does to the site

`docs/detector_history.md` is already the origin story — the three-way authorship
split, the CFAR convergence, SPIKE-synch's design-intent-versus-shipped-behaviour note.
Under these conventions a detector's page becomes where it came from, what it was when
inherited, every version since with what changed and why, and its run history across
datasets. **Not a rank.**

Two consequences. *"Six coordinated-event detectors ported from MATLAB"* stops being
true as an identity claim — six is a snapshot and porting is an origin, not a
description. And *"no single satisfying metric"* stops being a stance the prose must
keep asserting: if runs are keyed by dataset, one detector has many numbers by
construction, and there is nowhere on the page a ranked table could go.

## Decisions this needs

1. **Does `detector` absorb the nets at the emitting boundary**, keeping ADR-0005's two
   folders and two provenance shapes?
2. **`fit` or `opt` as the genus** — and therefore `fit_run_id` or `opt_run_id`.
3. **Two run ids, against ADR-0005's one** — accepted as an amendment to it, or rejected?
4. **Is a detector version addressable in the registry**, or only recorded in provenance?
5. **Prior art**, before any of the above is built. Nothing has been checked.

An accepted ADR is amended by another ADR, not by this file. If 1–4 land, they land as
ADR-0006.
