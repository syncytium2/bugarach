---
status: open
filed: 2026-08-17
---

# This project's windowing convention is applied to everybody's data, and cannot be turned off

The import contract asks any lab for raw region bounds, and then
`region_windows` ([`src/bugarach/detectors/loco.py`](../../src/bugarach/detectors/loco.py))
applies **aCa5z's** convention to them with no way to decline:

| what it does | value | where it comes from |
|---|---|---|
| baseline measured **backward** from its end | cap 1200 s | `if2_region_windows` |
| every non-hi-K treatment starts late | `solution_delay_sec` 120 s | drug wash-in on this rig |
| every non-hi-K treatment is capped | `treatment_window_sec` 1200 s | this lab's protocol |
| hi-K is exempt from both | decided by `"hi" in name.lower()` | substring match on the label |

For this project that is right, and it is what its own analysis does — parity with
`explore_sce` is the reason the port exists. For a lab that dosed instantly, or ran
five-minute treatments, or recorded a forty-minute drug application it wants scored in
full, it silently deletes the first two minutes of every treatment window and the last
eighteen of a long one.

**The label substring is the sharper edge.** `is_hik = "hi" in name.lower()` exempts
any period whose name contains those two letters from both the delay and the cap. A
lab with a condition called `histamine`, `chelerythrine`, `high-frequency stim` or
`hi-Mg` gets untrimmed windows for it and no warning. Rename the same period to
`elevated potassium` and it gets trimmed. The spec already documents this as a trap for
producers; it should not survive as behaviour.

## Why it is filed rather than fixed

The fix is not "add a parameter" — it is deciding **who owns the windowing** for a
foreign folder, and that is a scientific call:

1. **Keep applying it, name it in the output.** Every result already carries
   `detector_settings.csv`; the window convention could ride there, so a reader can at
   least see what was applied. Cheapest, and leaves the wrong default in place.
2. **Apply it only to this project's own data**, and pass foreign bounds through
   untouched. Needs a way to tell the two apart — a field in `slices.csv`, or the
   absence of one — and means two windowing paths to keep honest.
3. **Make it explicit and required.** The folder states its own convention (delay,
   cap, which labels are exempt) or gets none applied. Most honest, most work, and it
   puts a decision in front of every new lab before they can run anything.

Related, and the reason this is not hypothetical: the contract's own text promised for
its whole life that bugarach "uses the bounds as given and never adjusts them", which
is how interface2 came to ship pre-trimmed windows that halted 83 of 85 recordings
(2026-08-17). The prose has been corrected; the behaviour it was describing has not
been decided.

**Do not "fix" this by relaxing the guards in `region_windows`.** They halt on a
baseline that does not start at 0 and on gaps between regions, and for these stores
either really is a data defect — that is why the halt caught a bad export rather than
quietly scoring it. Whatever is decided above, the guards should still fire on the data
they were written for.
