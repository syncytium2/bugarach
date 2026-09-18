---
status: open
filed: 2026-09-17
---

# Tools that recognise the lab folder by its role NAME, and go quiet when the name changes

> Found the day the role name changed. Two of the three instances crashed; the third
> turned a guard off without saying anything.

## What happened

The producer shipped `2026-09-17_revised_2v_long_STEPS_AND_PINS_EXCLUDED`, and the role
reading it became `steps_and_pins_excluded` rather than `steps_excluded`. Several tools
were testing the role name as a proxy for *"this is the lab's two-stream folder with
declared treatment regions"*:

- `tools/look_rigid_shift.py`, `look_rigid_shift_controls.py` (fixed 2026-09-17 by the
  session running them: they now ask the folder, `is_lab_folder()`). Two of those
  comparisons sent the loader after the Dard et al. single `events` stream and it loaded
  **0 of 84 recordings** — a loud failure.
- **The third was a guard**: the rule refusing any window that is not the producer's
  declared baseline. Under the new name it simply stopped applying. Nothing failed, and a
  baseline-only analysis would have quietly included treatment windows.
- `tools/measure_slow_comodulation.py` had the same shape and was fixed the same day: it
  now asks whether the folder declares regions, and applies the baseline guard whenever it
  does. Verified equal to the old name rule on all three roles before the change landed.

## Still open

**`tools/build_surrogate_report.py:1991`** tests the recorded role against the literal
`"steps_excluded"` and drops its reproduction section for any other value. It is not wrong
today, it is just silent tomorrow: a report built from the de-pinned folder loses the
section that says how to rebuild it, with no error.

## The rule worth generalising

**Recognise a folder by what it has, not by what it is called.** A role name is a pointer
into `current_export.toml` and it moves whenever the producer ships; a property — does this
folder declare regions, does it carry two streams — moves with the data. Where a name
comparison is unavoidable, it must fail loudly rather than degrade: a guard keyed on a name
is the worst case, because the failure mode is silence.

## Closes when

`build_surrogate_report.py` asks the run for a property (or fails loudly on an unknown
role), and a grep for role-name comparisons across `tools/` comes back clean or annotated.
