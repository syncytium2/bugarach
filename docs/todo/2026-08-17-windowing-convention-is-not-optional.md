---
status: open
filed: 2026-08-17
---

# This project's windowing convention is applied to everybody's data, and cannot be turned off

> **Settled for detection, 2026-08-23.** The default is fixed where it was doing
> the damage. `bugarach detect <folder>` settles a recording's windows before any
> detector sees it: the producer's `analysis_*` where the folder states them, and
> **the raw period bounds verbatim where it does not** — no wash-in delay, no cap,
> no backward-measured baseline, no `"hi"` substring, and no HALT on a baseline
> beginning at 500 s or a gap after it. That is option 2 below, resolved the way
> FOUNDATIONS §4 always said it should be: the store path derives, the folder path
> does not, and the folder no longer falls *through* into the store path.
> `region_windows` is unchanged and still halts on the data it was written for;
> `tests/test_detect_folder.py` asserts both halves on the same folder, because
> either one alone is the bug.
>
> **Two fall-throughs remain, and they are why this stays open.** `bugarach check`
> runs `effective_region_windows` on every recording (`conform.py:163`), so a legal
> foreign folder with no analysis windows still **fails at the door** even though
> detection would now score it happily. And `assess_coactivity`'s `window=None`
> path still derives (`assess.py:267`) — right for the `.mat` store it is
> parity-tested against, wrong for a folder. Nothing is wrong today, because
> `assess_folder` passes explicit windows and never takes that path; the trap is
> live for the next caller. Both belong to a lane that owns `conform.py`.

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

## Partly answered 2026-08-17: the contract now carries analysis windows

Tony's call: `regions.csv` gains optional `analysis_start_sec` / `analysis_end_sec`, so
a region states **what happened** and **what to score**, and a producer with its own
windowing policy is honoured rather than re-windowed. Verified behaviour-preserving on
interface2's 84-recording export — supplying the windows bugarach would have derived
reproduces all 240 of them exactly, so nothing already measured moves.

That resolves option 3 below for anyone who *has* a policy to state. **What remains
open is the default**, which is what this todo was filed about: a folder with no
analysis windows still gets this project's delay, caps and `"hi"`-substring exemption,
and a lab that dosed instantly still loses two minutes of every treatment without being
asked. An analysis-window editor in the app is **version 2** (Tony, 2026-08-17) — the
contract carries them now, nothing edits them yet.

## Why the default is still filed rather than fixed

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
