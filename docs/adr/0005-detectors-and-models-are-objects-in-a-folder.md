# ADR-0005 — Detectors and models are objects in a folder

- **Status:** accepted 2026-08-29
- **Decider:** Tony
- **Supersedes nothing.** Extends [ADR-0001](0001-the-lab-server.md) (the lab server)
  and the requirement in [`../webapp_spec.md`](../webapp_spec.md).

## What is built, and what is only decided — 2026-08-30

This ADR was written before the work and describes six decisions. Three are built
and three are not, and an ADR that does not say which is a plan pretending to be a
record.

| # | decision | state |
|---|---|---|
| 1 | page assembled from a folder, assembled file committed | **built** — `tools/assemble_viewer.py`, `--check` in the suite |
| 2 | knobs as data, controls rendered not written | **NOT built.** All six objects carry their descriptor and algorithm, but `read()` still names input ids by string and the control divs are still hand-written HTML. This is the decision that finishes the job, and it is the one still open |
| 3 | Python is source of truth for the descriptor | **partly** — `test_registries_do_not_drift` compares the two lists by name; the full parameter comparison is not written |
| 4 | browser trainer is a SECOND trainer | decided, nothing built |
| 5 | user files load Worker-sandboxed | decided, nothing built |
| 6 | Chromium is the super-user target | decided, nothing built |

**Also built, and not in the original six:** the architectures moved the same way
— `learn/nets.py` became `learn/nets/`, one file per architecture, auto-imported
so a dropped-in file registers with nothing else edited and no list of names
exists anywhere.

### Two things learned by doing it

**Detector order was incidental and is load-bearing.** `rate` was first only
because it was first in the literal. Moving it into a file put it last, which
moves `detections.csv` row order, raster lane order, and *the sequence detectors
draw from the shared RNG* (`cicada_detect`: "declaration order, one RNG"). A test
with a different subject caught it, which was luck. `DETECTOR_ORDER` in the
template declares it now; a detector not named there loads at the end, so adding
one still needs no central edit.

**The collision predicted below arrived on the first merge.** `main` edited
`raster_viewer.html` in three places while this branch made that file generated.
Git auto-merged it — meaningless for a build artifact — and each change had to be
rehomed by hand, two to the template and one to `cicada.js`. The generated page is
committed precisely so that shows up in a diff rather than in a browser, and it
did. Every session that edits that file needs telling.

## The ask

Tony, 2026-08-29: *"the structure was always intended to be flexible. detectors and dl
models added removed at will."* And the target flow, in his words:

> a super user now has a folder of detectors that includes algorithms like rate, loco,
> coact etc and a folder containing models tube variations both downloaded from the
> site. now the user runs the app, the app sees the folders populates the detectors
> from the user, reads simulated or user data, simulates training data, optimizes the
> detectors, saves the settings in another folder (with training source info to enable
> the cross data set test), user trains models and weights are stored, bench is run,
> models compared, selections made, final run on users full data set

## Why the current shape blocks it

Adding a detector today means editing three coupled places, and **the coupling is in
the HTML**:

| where | what | why it blocks *removal* |
|---|---|---|
| `<div class="ctl" id="dLocoCtl">` | hand-written control block with hand-picked input ids (`dThr`, `dRate`, `dCtx`) | the ids are referenced by string from JS; deleting the detector orphans them |
| `const DETECTORS.loco` | `read()` pulls those ids **by name**, plus `run()`, `settings()`, `knob` | the id coupling lives here |
| `locoDetect()` | the algorithm | genuinely must be JS |

Plus `OPERATING_POINTS`, `emit.DetectionField` and `diagnostic.SHORT`/`COLORS` on the
Python side. **Nothing compared the page's list to the library's** until
`tests/test_registries_do_not_drift.py` (2026-08-29), so "add a detector" was a change
with a silent second half.

**The model half is already right and is the template.** `/api/capabilities` returns one
row per `@register`ed architecture with its note and its parameter count *built rather
than quoted*, and the picker populates from it. The page's own comment: *"adding a model
is one line in `nets.py` and it appears in this picker with nothing else edited."* Its
only gaps are the serverless fallback (`<option value="tube">` hardcoded) and
`fair_bakeoff`'s `LEARNED` tuple.

## What the viewer actually is

Not a viewer. `docs/site/raster_viewer.html` is **10,612 lines and a second
implementation of the pipeline** — all six detectors, the assessment
(`assessCoactivity`, `assessWindow`), the generator (`simulateFromMeasurement`,
`simulateRecording`, `simulateFolder`), the scorer, the sweep and `run.json`. Steps 1–4
of the per-lab loop exist twice in this repo, in two languages, and the browser copy is
the one an outside lab runs.

So a detector object is a **pair** — `loco.py` and `loco.js` — bound by a parity test.
`sync` is the standing proof of what happens without one: it is `unavailable` in the
page because the Python gained a fixed-window mode the JS did not, and nothing pinned
the profile, so the two could have drifted with no test saying so.

## Decisions

### 1. The page is assembled from a folder, and the assembled file is committed

```
docs/site/
  viewer.template.html          the shell: layout, chrome, the generic control renderer
  detectors/
    _contract.md                what an object must declare
    rate.js  coact.js  loco.js  sce.js  cicada.js  sync.js
  raster_viewer.html            ASSEMBLED — committed, reviewed in diff, never hand-edited
```

**Committed, not generated-and-ignored.** A test regenerates and asserts byte equality,
so the assembled file cannot drift from its sources. Rejected alternative: generate at
build time and leave it out of git — it is tidier and it loses `git diff` review of the
artifact an outside lab runs, which is how three sessions caught each other's mistakes
in this file on 2026-08-29 alone. The repo already uses generate-commit-verify for the
viewer's version stamp; this is the same trick one level up.

**The page must stay one file making zero requests.** `build_site.py`'s `NETWORK` guard
blocks `<script src`, `import(`, `fetch(` and the rest so the page works from `file://`
and no recording can leave the machine. Assembly is therefore at build time, not load
time.

### 2. A detector object declares its knobs as data; controls are rendered, not written

```js
registerDetector({
  key: "loco", label: "LoCo", blurb: "how local",
  strengthUnit: "local_coincidence_coactivity", takesRng: true,
  knobs: [{ id: "thresholdPctile", label: "threshold percentile",
            min: 90, max: 99.9999, default: 99.0, unit: "" }, ...],
  sweep: { knob: "thresholdPctile", grid: [99.0, 99.5, 99.9, 99.99] },
  run: (trains, range, cfg) => locoDetect(trains, range, cfg),
  settings: cfg => `threshold ${cfg.thresholdPctile}th percentile`,
  unavailable: null,
});
function locoDetect(...) { ... }
```

**This is the decision that actually unblocks removal.** With knobs as data there is no
`dLocoCtl` div and no `read()` naming ids by string, so deleting the file deletes the
detector *and its controls*. Everything else here is bookkeeping by comparison.

`unavailable` keeps the `sync` pattern: not in this build, drawn anyway, reason given —
because a picker that silently drops a detector reads as a detector that never existed.

### 3. Python is the source of truth for the descriptor; a test enforces it

`OPERATING_POINTS` grows the display fields it lacks. A test regenerates the descriptor
set from Python and asserts the page's objects match — the extension of
`test_registries_do_not_drift.py` from names to full parameters. The page cannot import
Python, so the copy is structural; what is not structural is it drifting unnoticed.

### 4. The browser trainer, when it exists, is a SECOND trainer

Every published number came from torch. The models are 1,149–2,393 parameters, so a JS
trainer is feasible without a framework — but it produces different weights. Making it
the reference means rerunning and rewriting the whole bake-off and everything citing it.

So: the browser trains, its weights are stamped browser-trained in the `provenance`
block, and **the bench refuses to compare across trainers without saying so.** Revisit
only if a deliberate decision is taken to re-baseline the published numbers.

### 5. User-supplied detector files load Worker-sandboxed, behind an explicit action

There is **no CSP** anywhere in this project, so nothing platform-level prevents
`import(blob:)` of a file the user picked. This is our call, not the browser's.

The page's promise is *no data leaves your machine*. A detector object runs in a Worker
with no network handle, so that promise survives a hostile or broken file. Loading
happens only on an explicit user action, never on page load.

This requires editing `build_site.py`'s `NETWORK` guard to permit a blob import while
still blocking egress. **That is a deliberate change to a safety guard and gets its own
commit and its own reasoning** — a guard quietly loosened is worse than one that was
never there.

### 6. Chromium is the supported super-user target

`showDirectoryPicker({mode:"readwrite"})` + `createWritable` gives real folder output
for settings and weights. Firefox and Safari have neither and fall back to downloads.
The page **says which it is doing** rather than silently offering less.

## The spine: every artifact names the input it came from

Tony's parenthetical — *"with training source info to enable the cross data set test"* —
is the architecture, not a detail.

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

Once that holds, the cross-dataset test is not a feature to add — it is a question the
artifacts already answer, and **the bench can refuse an invalid comparison** rather than
silently produce one.

That failure is live today:
[`../todo/2026-08-28-the-refit-still-picks-thresholds-on-its-fitting-data.md`](../todo/2026-08-28-the-refit-still-picks-thresholds-on-its-fitting-data.md)
— settings chosen on the data they were then scored on. Two pieces already exist and
were built for other reasons: `bugarach.provenance` (2026-08-29) records *which code*,
and `fair_bakeoff --score-spec` (PR #398) records *which corpus was fitted on versus
scored on*. Neither alone is enough; together they are the chain.

## Consequences

- Adding a detector becomes: one `.js` in the folder, one entry in `OPERATING_POINTS`,
  one parity test. The gate refuses a Python side with no JS side, or either with no
  parity test.
- `docs/site/raster_viewer.html` stops being hand-edited. **Every session that edits it
  today must be told**, or the first hand-edit after this lands is silently overwritten
  by the next build — the loudest foreseeable failure of this change.
- The six existing detectors must be converted before the template can drop the
  hand-written control divs. Until then both paths exist, which is the risky interval.

## Rejected

- **Runtime fetch of a detector folder.** Breaks the no-request guarantee and the
  `file://` route, which is the whole reason a lab will try this without asking IT.
- **Descriptors duplicated by hand in JS with no Python source.** That is today's state
  and it is what produced a viewer nothing compared to the library.
- **Deleting `sync` rather than marking it `unavailable`.** Removing the row takes the
  parity harness, the ability to read back an older `detections.csv`, and the reason
  with it — leaving a page silently missing a detector nobody can ask about.
