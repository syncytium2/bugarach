# Handoff — the loop closes; both of pipeline.md's blockers are gone

**In flight: [#508](https://github.com/syncytium2/bugarach/pull/508)** (the checkpoint, the
`--model` flag and the lab's model exchange, merging on green) and
**[#466](https://github.com/syncytium2/bugarach/pull/466)** (the field-step figure, still held
because it is a figure with a caption and was never murderboarded).
[#507](https://github.com/syncytium2/bugarach/pull/507) landed overnight; everything else this
session opened is merged. The predecessor is
[`docs/handoffs/2026-09-08-mahice-is-usable-nobody-has-run-one.md`](docs/handoffs/2026-09-08-mahice-is-usable-nobody-has-run-one.md)
— its MAHICE section, its K-floor note and its trap list are NOT superseded by this file.

> **Not murderboarded** — working material for sessions in this tree, same standing as
> `docs/run_records.md` and `docs/pipeline.md`. Nothing here is for an outside reader.

**No counts in this file.** Derive them: `git rev-parse --short origin/main` · `pytest -q` ·
`python3 tools/sapper.py --all` · `python3 tools/site_staleness.py`.

---

## Do not break this

**Tony judges out of `../bugarach-worktrees/mahice`, which is DETACHED on purpose.**
`merge_when_green.sh` reaps a worktree when its branch lands, and on 2026-09-05 that deleted
his viewer mid-session. To move it when `main` advances:

```
git -C ../bugarach-worktrees/mahice checkout --detach origin/main
```

**Do not delete and recreate it. Do not reap it.** His verdicts live in `localStorage`, keyed
per channel, and do not leave the browser until *Download annotations.csv*.

## What changed overnight, and why

> Tony, on being told the six ran the pilot folder at *shipped* operating points while the
> bake-off had calibrated them on simulated data derived from that same cohort:
> **"that is the whole point of the pipeline"**.

**`docs/pipeline.md`'s blocker list is now empty.** Both items that sat upstream of everything
else on that page are closed:

| was blocked | now |
|---|---|
| a settings file the library's detect path will read | `bugarach detect --settings`, plus `tools/settings_from_bakeoff.py` to write one from a bake-off |
| model persistence | `bugarach.learn.checkpoint`, `run_learned_on_folder.py --save-models`, `bugarach detect --model`, and `/api/export_model` + `/api/import_model` on the lab server |

Both directions work for both artifacts: a calibration or a model fitted at the command line
runs in the browser, and one fitted in the browser runs at the command line.

## Two things to know before touching any of it

**The settings format was already shared and nobody had called it.**
`emit.read_detector_settings` had parsed the browser's file and the library's since the day it
was written — its own docstring says why, in terms. The whole gap was that nothing invoked it
on the way **in**. Before building a format here, check whether the reader already exists.

**A checkpoint is JSON, not `torch.save`, and that is not a style choice.** These nets are
1,149–2,393 parameters, so the file can be one `JSON.parse` loads — which is what lets a model
cross to the browser at all. And ADR-0005's target flow is a user downloading models from the
site: pickle would mean opening a stranger's model runs their code.

## Measured, not asserted

- At the calibration derived from the pilot cohort's own simulated data: `rate+context`
  **+90 %** calls against its shipped point, `locust` **+105 %**, `LoCo` **+10 %**. That gap
  was the distance between the instrument the bench scored and the instrument that ran.
- Train two models with `--save-models`, then `bugarach detect --model` in a **separate
  process**: identical, call for call (101/253 tube, 112/257 tube_guard). 31 KB per file.

## Three refusals that are findings

`settings_from_bakeoff.py` will not emit a calibration for three of the six on that cohort.
**CoactDetect** and **binned SCE** because their folds disagreed — a mean over a knob grid is
not a knob anyone ran. **SPIKE-synch** because every fold landed on the *end* of its grid,
which `bench.pick_operating_point` already treats as a search that stopped too early. Each is
named and left out, because a file carrying shipped values for the uncalibrated detectors
would read as a calibration of all six.

⚠ **So SPIKE-synch's bake-off F1 was measured at a bound rather than an operating point.**
Nobody has acted on that.

## Still open, in the order I would take it

1. **MAHICE has never been run on the approved folder.** The ground truth everything above
   rests on is the assessor's clusters at a K nobody judged. Expert attention, not compute,
   and the only remaining step a person must do. The viewer for it went live this session —
   what had been published was the version whose judging step could not be opened at all.
2. **`docs/performance_table.md` §1 has a header saying its evidence is superseded and no
   argument in its place.** The replacement is available — the background axis narrowed
   rather than died, mean own-range 0.136 against a 0.017 headline gap — but whether *"no
   ranking"* survives on spread alone is Tony's call about his own result.
3. **`docs/learned/background_curve.png` is the flat field's**, and its Panel B draws a rank
   crossing that no longer reproduces. Regenerate or delete it.
4. **The ratio arm of the tube 2×2** does not gate on participation, measured two ways, and
   the failure was pre-registered in the variants' own scoping doc. Whether the arm stays is
   a decision about a mechanism result, not a defect to patch.
5. **binned SCE sits at 0.64× its own chance rate** on real recordings, beside the two
   degenerate learned baselines. It ran at the shipped percentile while every fold calibrated
   twenty points away — now testable in one command, which it was not yesterday.

All five have todos under `docs/todo/` dated 2026-09-08.

## Traps this session hit, so the next one does not

- **The board gate matches on the WORKTREE NAME**, not on your block's title. A block called
  `Mac/close-the-loop-overnight` does not clear a worktree called
  `detect-reads-a-settings-file`. Two refused commits.
- **`tests/test_architectures_are_files.py` fails from any worktree** using the primary
  checkout's `.venv`: those tests write a probe file into their own tree and import from the
  editable install, which is a different tree. Run with `PYTHONPATH=$PWD/src`. INDEX row added.
- **A settings file this module writes must load back into it.** The round-trip test caught
  `grid_dt` and `imaging_rate_hz` on its first run — `detect` writes them and no detector
  takes them.
- **The site deploy needs the claim landed, and CI is ~13 minutes.** The claim PR was pushed
  and open but not merged when `npm run deploy` ran; `docs/SESSIONS.md` records the gap
  honestly. And `main` moved under the preflight — the `HEAD == origin/main` check caught it.
