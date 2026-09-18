# The GPU shakedown on the home spec — a rehearsal, not a result

**Kept so that the numbers quoted in `HANDOFF-workstation-tuning.md` can be traced to their files.**
Run on WSMIP064 from 12:42 on 2026-09-17 to 02:35 on 2026-09-18: 2,089 jobs, 0 errors, 13 hours
53 minutes, 27.3 GPU-hours of training, unattended from Task Scheduler.

**Why it is not a result.** It ran on the retired home spec (`docs/learned/generator_spec.json`),
with the coded detectors on three knobs, the budget of the 2026-09-16 design, and no rule against a
context window wider than the planted spacing — so some of its CoactDetect choices sit at 240 s,
which contaminates their own null. No readout is planned from it, and nothing should quote it as a
comparison. Its purpose was to prove the launch path before the run that matters.

**What is here:** `meta.json` (the declaration, the machine and the budgets; the output folder in
its command line is written as `%USERPROFILE%` rather than a personal path), `results.json` (held-out
numbers per selection), `progress.json`, `selections/` (every choice, by configuration key) and
`configs/` (what each key means). **Not here:** `fits/`, `scores/` and `chosen/`, about 0.4 GB of
per-fit files, which stayed on WSMIP064's local disk.
