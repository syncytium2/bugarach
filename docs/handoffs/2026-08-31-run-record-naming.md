# Run-record naming — what is decided, what is waiting, and what to do first

> **Written straight into this directory on 2026-08-31 — nothing in it is half-done.**
> It was never a root signal: the work it describes is filed and merged (#428), and a
> root `HANDOFF.md` must name an **open** PR or `tests/test_handoff_is_honest.py`
> fails. This is the record another session picks up from.
>
> **Written because Tony asked for one**, 2026-08-31: *"please document the data
> naming conventions and all that as a handoff for another session"* — so that the
> website reorganization could proceed without carrying this thread.

## Read these two files, in this order, before anything else

1. **[`docs/adr/0005-detectors-and-models-are-objects-in-a-folder.md`](../adr/0005-detectors-and-models-are-objects-in-a-folder.md)**
   — accepted 2026-08-29. Its closing section, *"The spine: every artifact names the
   input it came from"*, **already specifies the run store.** Do not design one.
2. **[`docs/run_records.md`](../run_records.md)** — what a design conversation on
   2026-08-31 added to that ADR, and the one place it contradicts it.

The queue entry is
[`docs/todo/2026-08-31-run-record-naming-decisions.md`](../todo/2026-08-31-run-record-naming-decisions.md),
`status: waiting-on-tony`, so the briefing reads it out at every session start.

## The thing that will save you a day

**Most of this was decided two days before it was discussed, and the discussion did
not know.** Tony spotted it in the moment — *"reinventing the wheel. cfar all over
again"* — and he was right in a way that matters: the wheel was his own, from an ADR
accepted 48 hours earlier.

Four questions that a whole conversation treated as open have answers in ADR-0005:

| treated as open | ADR-0005's answer |
|---|---|
| per-run subfolder, or an id column on shared files? | `runs/<id>/` |
| what identifies the dataset something was fitted on? | `fitted_on` / `trained_on` / `scored_on` |
| what identifies a detector version? | `detector versions`, in `settings.json`'s provenance |
| non-Chromium browsers? | §6 — Chromium is the target; elsewhere downloads, and the page **says which** |

Its payoff is already stated there: once every artifact names its input, *"the
cross-dataset test is not a feature to add — it is a question the artifacts already
answer, and the bench can refuse an invalid comparison rather than silently produce
one."*

## What is actually open

**Waiting on Tony — four decisions**, all in `run_records.md` §Decisions:

1. Does **`detector` absorb the nets** at the emitting boundary? Tony proposed it on
   2026-08-31. It **cuts against** ADR-0005's two-folder split, which exists because
   weights carry a trainer provenance a knob sweep does not. The filed proposal is
   *one namespace, two homes*.
2. **`fit` or `opt`** as the genus word, and therefore `fit_run_id` or `opt_run_id`.
   `calibrate` and `train` are the species and both already exist in the tree.
3. **Two run ids, against ADR-0005's one.** This is the substantive gap: a detect run
   consumes many fit runs, so a single id cannot express *detecting today with settings
   fitted last month*. Proposed as an amendment to its layout, not a replacement.
4. **Is a detector version addressable in the registry** — `rate@v1` runnable beside
   `rate@v4` — or only recorded in provenance?

If they land, they land as **ADR-0006**, and `run_records.md` retires into it. An
accepted ADR is amended by another ADR, not by a loose doc.

**Not waiting on Tony, and it goes first — the prior-art pass.** Nobody has run it.
Experiment tracking, run provenance and settings-versioning are a developed field, and
this project has already discovered once that reasoning its way somewhere says nothing
about who is already there: `rate_detect`, `coact_detect` and `loco_detect`
reconstructed CFAR without knowing it existed
([`detector_history.md`](../detector_history.md) §4). Adopting an existing vocabulary
would make decisions 1–4 largely moot, so **do this before building, not after.**

Three groups, and the order is a recommendation rather than a finding — none of this
has been checked:

- **Neuroscience data standards first**, because that is where this lab's
  collaborators may already be reading files. **BIDS Derivatives** looks closest: each
  derivative dataset carries `GeneratedBy` (pipeline name, version, code URL) and
  `Sources` naming its inputs, sitting beside the raw data — which is ADR-0005's spine
  as a published standard. Then **NWB** (the `ophys` module is where calcium ROIs and
  traces already live) and **DANDI**, which `model_track.md` already names as a
  second-dataset source. **CaImAn** and **Suite2p** both write settings beside output
  already — Suite2p's `ops.npy`, CaImAn's params serialized into the HDF5.
- **Experiment tracking.** MLflow is closest on identifiers — its term is literally
  `run_id`, and **its default backend is a local file store** (`./mlruns`, plain
  directories, no server), which is the shape Tony specified. Also W&B, Neptune,
  Comet, ClearML, Sacred, Aim — all of which assume a central store by default, which
  is the thing that disqualifies them here.
- **Provenance vocabularies.** W3C PROV — `used`, `wasGeneratedBy`, `wasDerivedFrom`.
  ADR-0005's *"every artifact names the input it came from"* is PROV's `used` relation
  under another name. RO-Crate packages the same thing as JSON-LD.

⚠ **All of the above is from an assistant's background knowledge, not from a search.**
Treat every claim in it as a lead to verify, not a result. That is precisely the
failure mode this pass exists to catch.

## What must not happen

- **Nothing gets built against these names.** They are provisional in both directions:
  Tony has not ruled, and the prior-art pass could replace the vocabulary wholesale.
- **Do not rename the `cicada` key.** It is the `detections.csv` contract value
  (ADR-0002) and it moves everywhere at once as an announced spec revision, or not at
  all.
- **Do not merge `detectors/` and `learn/nets/`.** The union proposed in decision 1 is
  a naming decision at the *emitting* boundary. ADR-0005 §4 keeps the two apart for a
  different reason — the browser trainer is a **second** trainer, weights are stamped,
  and the bench refuses cross-trainer comparisons. A knob sweep has no trainer
  provenance to stamp.
- **Any new column is a spec revision** to `export_folder_spec.md`, read by interface2
  and fireflies. Announced, not quiet.

## Two traps this session hit, which will bite the next one

**The prose is behind `bakeoff.json`, and three documents agree with each other while
being wrong.** This session asserted — from `what_the_webapp_was_for.md`,
`model_track.md` and a todo, all consistent — that three tube variants had never been
benchmarked and two learned architectures had no operating point. Tony said it was not
true, and the JSON settled it: **all six learned architectures have run**,
`registered_but_not_run: []`, all four tube-family variants carry real operating points
(thresholds 0.97–0.998, nowhere near the 1e-4 floor), and all four trained at the same
learning rate, so there is no rate confound within that family. The two at the floor
are `tiny` and `trace`.

The live numbers, read from `docs/learned/bakeoff.json`:

| arch | F1 | sd | recall | precision | params | fit s | detect s | hot_fa |
|---|---|---|---|---|---|---|---|---|
| tube | 0.681 | 0.049 | 0.917 | 0.543 | 1149 | 6.8 | 0.023 | 20.5 |
| tube_guard | 0.673 | 0.069 | 0.808 | 0.577 | 1149 | 6.5 | 0.022 | **4.8** |
| tube_ratio | 0.503 | 0.069 | 0.650 | 0.426 | 1149 | 7.0 | 0.023 | 0.0 |
| tube_ratio_guard | 0.471 | 0.055 | 0.583 | 0.405 | 1149 | 6.9 | 0.023 | 0.0 |
| tiny | 0.125 | 0.000 | 0.067 | 1.000 | 2393 | 77.0 | 0.228 | 0.0 |
| trace | 0.118 | 0.015 | 0.067 | 0.792 | 2065 | 8.5 | 0.022 | 0.0 |

**Read the JSON, never a page about it.** `bakeoff.md` still shows three learned rows
and warns about itself in its own header; there is an open todo to give it a generator.
The lesson generalizes to anything the run store produces: **generate the pages, do not
type them.**

⚠ One live defect found on the way and **not fixed** — `TubeTrainer.LR` in
`src/bugarach/lab.py` is `{"tube": 1e-2, "trace": 1e-3, "tiny": 1e-3}` and looks up with
`.get(arch, 1e-3)`, so the lab server trains `tube_guard`, `tube_ratio` and
`tube_ratio_guard` at **a tenth** of the rate `bakeoff.json` records for them. Its own
docstring says the rates are quoted from `fair_bakeoff.py` *"because a rate chosen here
would make this server's numbers a different experiment from `bakeoff.json`"*. Three
dict entries. It matters as soon as anyone trains a variant through the app.

**One `waiting-on-tony` todo costs the session briefing 377B, and only CI sees the real
margin.** Adding this thread's queue entry put the briefing at 9,206B against a 9,150B
budget and turned a docs-only PR red. It passed locally and failed in CI because CI
resolves neither the data folder nor the darkroom, and each miss prints ~214B of
warning a developer machine never sees. Per CLAUDE.md the fix is to trim a section
rather than raise a budget, and never to touch either budget without running
`tools/hook_spill_census.sh` first. There is now roughly 100B of headroom, which is one
more queue entry.

## Where the numbers and the code actually are

- run-store layout and its rationale → ADR-0005, closing section
- the naming proposals and their costs → `docs/run_records.md`
- what the app already does → `src/bugarach/lab.py` (`/api/train`, `/api/detect`,
  `/api/fit_folds`), and it is genuinely built — a chromium test drives the real panel
  against the real server in CI
- what gets written back today → `src/bugarach/emit.py` (`write_detections`,
  `write_detector_settings`, `write_run`)
- the output contract → `docs/export_folder_spec.md`, *"What bugarach emits back"*
- the genus/species vocabulary already in use → `tools/fair_bakeoff.py`, `fit_cache`
  and its docstring
