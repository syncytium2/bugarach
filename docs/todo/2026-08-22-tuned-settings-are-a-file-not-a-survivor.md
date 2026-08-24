---
status: done
filed: 2026-08-22
closed: 2026-08-23
---

# Tuned settings are a saved file, not a variable that outlives the folder

> **Done 2026-08-23.** Two buttons in the Detect step — *Save these settings* and
> *Load settings…* — and `TUNED` no longer survives `open`; the survive-the-folder
> machinery went with it, exactly as predicted below. The workflow is written
> where the buttons are, in the order it is walked.
>
> **The file is the export contract's own four columns**, `detector, stream,
> parameter, value`, so `emit.read_detector_settings` — added as the sibling of
> `read_detections` — parses it and the run's `detector_settings.csv` alike.
> Provenance rides in the same columns under a `fitted_` prefix rather than in a
> header block, because a second shape would be a second dialect of a file this
> project already has one reader for: `fitted_on`, `fitted_by`, and for a swept
> value `fitted_knob`, `fitted_f1`, `fitted_tolerance_sec`, `fitted_n_folds`,
> `fitted_n_recordings`, `fitted_held_out`.
>
> **The name says which data set**, per Tony: `bugarach_settings_<folder or
> simulated_seedN>_<stream>.csv`. A directory pick knows the folder's own name; a
> loose-file pick does not, and the `fitted_on` row says so rather than inventing
> one.
>
> The stream half landed with it. A file fitted on `fast` loaded while `slow` is
> in play is **refused with the reason**, and a value still sitting in a control
> after the door moves says on screen which stream it came from instead of
> quietly passing as chosen for the one now being analysed.

Tony, 2026-08-22:

> *"tuned settings should be saved with a file name associated with the simulated
> folder or the user folder. don't assume the tuned settings survive a folder
> change."*

**The decision.** A fitted setting is written to a named file that says what it was
fitted on. Detect takes two inputs — a folder, and settings to run on it — and
loads the second rather than inheriting it.

## What it replaces

`TUNED` is a module-level object deliberately written to survive `open()`, which
is the one place the page throws work away. `SIM_TARGET` is kept alive the same
way. A session reading the code learns this from a comment; a person using the
page learns it not at all, and the sequence that depends on it — tune on
simulated data, then reopen your own folder — is nowhere on screen.

Nothing needs to survive `open()` if the settings are a file. The
survive-the-folder-change machinery becomes unnecessary rather than load-bearing,
and the step that was implicit becomes a thing you can see, name and reuse next
week.

## What the file has to carry

One row per **detector and stream**, which is what
`emit.detector_settings_rows` already writes and what
`detector_settings.csv` already specifies in
[`docs/export_folder_spec.md`](../export_folder_spec.md). The browser's
`run.json` writes `thresholds` keyed by detector alone — that is the gap.

Beyond the values: which data set it was fitted on, at what tolerance, and the
provenance the page already tracks (`from`, `f1`, `nFolds`, `dataSetN`, `tolSec`).
The chip that currently says "chosen by the sweep" is asserting exactly this, from
memory, for as long as the tab is open.

## Naming

Named for the data set, per Tony — the simulated one it was fitted on, or the
user's folder it was fitted for. The exact convention is open; what is settled is
that the name says which, so two settings files on a disk are told apart by
reading them rather than by remembering.

## Related

- [`2026-08-22-the-stream-is-chosen-at-the-door.md`](2026-08-22-the-stream-is-chosen-at-the-door.md)
  — the per-stream half, and the three call sites that make it a defect today.
- [`2026-08-22-a-back-route-for-a-reliable-pipeline.md`](2026-08-22-a-back-route-for-a-reliable-pipeline.md)
  — the automated route, which needs a settings file to exist before it can have
  anything to feed.
