---
status: open
filed: 2026-09-02
---

# You can tune a detector in the browser and the CLI will not run what you tuned

The detector registry and the sidecar files both landed, and they work. What did not
land is the join between them: **`detector_settings.csv` is write-only across the
front-end boundary.** Three writers produce it, nothing reads one back to configure a
run, and so the last step of the flow ADR-0005 was written for silently does something
other than what the user asked.

Tony's own words for that flow, quoted in
[`adr/0005-detectors-and-models-are-objects-in-a-folder.md`](../adr/0005-detectors-and-models-are-objects-in-a-folder.md):

> *"…optimizes the detectors, saves the settings in another folder (with training source
> info to enable the cross data set test), user trains models and weights are stored,
> bench is run, models compared, selections made, **final run on users full data set**"*

The final run is the step that does not work. Everything before it does.

Filed from a review Tony asked for on 2026-09-01/02. Every claim below was re-verified
against `origin/main` at `a55ca27`; §*Re-verifying* has the commands.

---

## 1 · The headline: the settings file has no reader

Three writers, one reader, zero callers.

| | |
|---|---|
| the browser page | writes it, with provenance — `fitted_on`, `fitted_by` (`sweep` / `hand`), `fitted_f1`, `fitted_tolerance_sec` |
| `bugarach detect` | writes it, bare — parameters and values, no provenance |
| the Panel viewer's Save | writes it, bare, via the same `emit` helpers |
| `emit.read_detector_settings` | exists, is in `__all__`, and **has no caller in `src/` or `tools/`** — only tests |

And nothing downstream could use it if it did:

- `detect_folder()` takes `detectors`, `stream`, `frame_interval_sec`, `limit`,
  `progress` — **no settings argument**
  ([`detect_folder.py:414`](../../src/bugarach/detect_folder.py#L414)). Its parameters
  come from `OPERATING_POINTS` and nowhere else (`:300`).
- `bugarach detect` takes `--out`, `--stream`, `--detectors`, `--frame-interval`,
  `--limit` — **no `--settings`** ([`cli.py:148-170`](../../src/bugarach/cli.py#L148-L170)).

**So the failure is silent.** Point the CLI at your full dataset after an afternoon of
tuning and it runs stock operating points, writes a `detector_settings.csv` saying so,
and reports success. Nothing warns, because nothing was asked.

**The browser's file is the richer one, and that asymmetry is the second half of the
defect.** Its provenance rows ride in the same four columns under a `fitted_` prefix,
deliberately — the test says *"so one reader parses both files"*
([`test_webapp_settings_file.py:339`](../../tests/test_webapp_settings_file.py#L339)).
The reader was built for that and never wired up. Meanwhile Python's writer emits none
of those rows, so a Python-written file cannot be checked by the page's own refusal
test the way a page-written one can.

### What to build

1. `detect_folder(..., settings=None)`, consuming `emit.read_detector_settings` — which
   already parses the page's format, including the `fitted_` rows.
2. `--settings` on `bugarach detect`.
3. Python's writers emit the `fitted_*` rows too, so a file is self-describing whichever
   side made it.
4. A round-trip test: page writes → CLI reads → the detector demonstrably runs at the
   tuned value and not the stock one. **Assert the value that reached the detector**, not
   that the file parsed — a test that only round-trips the CSV would pass today.

⚠ **A detector that is `unavailable` in the page still has a row in a CLI-written
file.** Decide what the reader does with a settings row for a detector the writing side
could not run; `sync` is the live case.

## 2 · The drift test guards the far copies and leaves the near ones open

[`test_registries_do_not_drift.py`](../../tests/test_registries_do_not_drift.py) compares
the browser's detector list to the library's, and the bake-off's `LEARNED` tuple to the
architecture registry. It does **not** compare the four hand-typed Python copies to
`OPERATING_POINTS`:

- `detect_folder.DETECTORS` and `detect_folder.ONSET_FIELD`
- `emit.DETECTOR_FIELDS`
- `ui/app.py`'s `COLORS` / `TITLES` / `SHORT` / `_SPECS` / `DT_DERIVED` (`:125-186`)

**All four agree with the library today** — checked, not assumed. So this is a free
ratchet: four asserts that pass on the day they are written, guarding the copies a
person adding a detector in Python edits *first*. The test file's own docstring argues
for exactly this and then only does the browser.

**Add the cross-registry collision check in the same commit.** Nothing stops registering
a net named `rate`; the two key sets are disjoint today and no test says they must stay
that way. [`run_records.md`](../run_records.md) §1 predicts it and calls the check cheap.
Under the one-namespace proposal that collision lands silently in the `detector` column
of every `detections.csv`.

## 3 · Knobs are still not data, so a detector file cannot be deleted

ADR-0005 decision 2 — *"the decision that actually unblocks removal"* — is unbuilt, and
its own status table says so. Re-verified: **`knobs:` appears zero times across all six**
objects in [`docs/site/detectors/`](../site/detectors/). Every one still carries
`ctl: "dRateCtl"` and a `read()` naming inputs by string, and
`viewer.template.html` still holds **21** hand-written `class="ctl"` divs.

So deleting `rate.js` today removes the algorithm and the descriptor and orphans the
controls. The folder is built; the promise on the tin is not yet redeemed.

**What is finished, and should stop being described as in progress:** `const DETECTORS`
is now an **empty literal** (`viewer.template.html:7208`) — all six arrive through
`registerDetector`. The drift test's docstring still describes a "mid-migration" state
with two sources, which the tree has left. Fix that docstring when you touch the file
for §2.

## 4 · The defect that motivated the registry is not a defect

[`what_the_webapp_was_for.md`](../what_the_webapp_was_for.md) says the five dispatch
sites disagree — `bench.run_detector` feeds `coact` and `sync` through `stream_trains`
while `detect_folder._run_flat` and `ui/app._compute` hand them raw `t50rise` — and
concludes *"the bench and the folder path are not running the same thing."*

**Traced, and they are running the same thing.** `coact_detect` calls `clip_sorted` at
[`coact.py:104`](../../src/bugarach/detectors/coact.py#L104); `sync_detect` at
[`sync.py:313`](../../src/bugarach/detectors/sync.py#L313), and `adaptive_profile` clips
again at `:175`. `clip_sorted` ([`_shared.py:78`](../../src/bugarach/detectors/_shared.py#L78))
drops non-finite values and clips to the range — everything `stream_trains` does, plus
sorting. The call at the bench site is **redundant, not divergent**.

**The real gap is smaller and worth closing anyway.** `rate_detect` does *not* clip
internally — `rate.py` contains no `clip_sorted` at all, and its docstring says a caller
holding bare trains must state it, *"no fallback and no warning"*. So one of the three
flat detectors depends on caller preparation and two do not, **and nothing declares
which**. The JS side has vocabulary for this (`peaks: true` declares an input
requirement); the Python side has none, and no test pins the equivalence.

Proposal: a `prepares_own_trains` field on `OperatingPoint`, asserted against the three.
It converts a latent trap into a fact the registry states, and it is the third assert in
§2's commit.

⚠ **Do not "simplify" by deleting the internal `clip_sorted` calls.** They are what makes
`coact` and `sync` caller-independent. Removing them would make finding 4 true.

## 5 · Two things this review got wrong, recorded because the corrections are the content

**A claim that the sidecar spine "appears nowhere".** It does not appear in `src/` or
`tools/` — which is what was grepped — but `fitted_on` is live in the browser and pinned
by three tests. The correct statement is that data provenance is **asymmetric, not
absent**, and that flips the advice: not *build the spine*, but *Python is the side that
is behind, and the page is the reference implementation for what a row looks like*. It
also narrows the naming decision still open in `run_records.md` §3 — `fitted_on` is
already shipping in files users can save, so that name is settled by deployment. What is
open is the two run ids.

**Repeating the "five dispatch sites disagree" claim before tracing it.** §4. The source
document is murderboarded and correct about the *shape*; the behavioural conclusion
drawn from it is wrong, and this todo is the only place that currently says so.

## What not to do

Two limits are deliberate and predate this file. Interchangeable **artifacts**, not
interchangeable **provenance claims**:

- **ADR-0005 §4** — the browser trainer is a *second* trainer, weights are stamped
  browser-trained, and the bench refuses to compare across trainers. Making weights load
  both ways without the stamp silently re-baselines every published number.
- **ADR-0001** — the page holds the directory handle; the lab server binds `127.0.0.1`
  and reads no path. Sharing goes through the user's own folder, never a daemon that can
  name one. A shared cache would trade away the property that lets a lab try this without
  asking IT.

Model weights being one-way (torch `.pt`, the browser cannot load one, `bugarach lab`
bridges it) and a user-supplied detector being a `.js` the Python side cannot run are
**real gaps and ADR territory** — not bugs to fix in passing.

## Re-verifying

From a worktree, with `PYTHONPATH=$PWD/src` so the import is this tree's and not the
primary checkout's
([`2026-08-28-a-worktree-pytest-run-tests-the-primary-checkouts-src.md`](2026-08-28-a-worktree-pytest-run-tests-the-primary-checkouts-src.md)):

```sh
grep -rn read_detector_settings src/ tools/          # §1 — no caller
grep -n  "def detect_folder" -A 4 src/bugarach/detect_folder.py
grep -n  "det.add_argument"  src/bugarach/cli.py     # §1 — no --settings
grep -c  "knobs:" docs/site/detectors/*.js           # §3 — all zero
grep -c  'class="ctl"' docs/site/viewer.template.html
grep -n  clip_sorted src/bugarach/detectors/*.py     # §4 — rate.py absent
pytest tests/test_registries_do_not_drift.py tests/test_provenance.py \
       tests/test_assembled_viewer.py tests/test_detectors_survive_assembly.py \
       tests/test_architectures_are_files.py
python tools/assemble_viewer.py --check
```

All green at `a55ca27`; nothing here is a failing test, which is the point — every one of
these is a gap **no test can currently see**.

## Order

§2 first — it is asserts-only, passes on arrival, and cannot turn `main` red. Then §1,
which is the one a user notices. §3 is the largest and unblocks user-supplied detector
files (ADR-0005 §5), which cannot work while a dropped-in `.js` has no way to bring its
own controls.
