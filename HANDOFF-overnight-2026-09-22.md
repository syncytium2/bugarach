# Overnight 2026-09-22 → 23: adopt the measured jitter, measure the rest, rerun

> **In flight.** Driven by the cloud orchestrator session (title *"bugarach orchestrator"*), with
> one live session on each workstation. Each workstation session reads **its own section** and
> nothing else is assigned to it. Delete this file, or move it to `docs/handoffs/`, when every
> section below is marked done.
>
> **Not murderboarded** — working material. Tony, 2026-09-22: no time.

## Tony's rulings, 2026-09-22 evening

1. **Jitter: adopt the measured values** in both benches — fast **0.106 s**, slow **0.135 s**
   (`docs/learned/runs/2026-09-22-jitter-correlogram/`), and rerun. Ruling-queue item 2.
2. **Participation 0.18 → 0.19**, approved by the morning meeting, in the same pass
   (`docs/todo/2026-09-21-bench-participation-to-0-19-after-the-meeting.md`).
3. **New measurements go into the bench tonight unless there is a reason to hold** — Tony will
   check in later tonight. The orchestrator has flagged one reason, below.
4. **Run fast, slow and combined.**

### What is adopted tonight, and what is only reported

| value | tonight | why |
|---|---|---|
| jitter, both streams | **adopt** | ruled |
| participation middle level 0.19 | **adopt** | ruled |
| quiet / busy background rate | **adopt** if the tool's calibration passes | replaces like with like: total rate minus the coordinated share |
| probe (elevated-rate stretch) level | **adopt** if calibration passes | replaces a chosen multiple of the median with a measured high percentile of untreated 5-minute stretches |
| event frequency, participation from cumulants | **report only** | the bench plants a fixed participant count at three levels with ≥120 s spacing (a design floor that keeps each detector's null clean). The cumulant measure is a per-cell join probability over all shared moments, including ones joined by one or two cells. Adopting it means restructuring how events are planted, which is a decision, not a substitution |
| anything **combined** | **report only** | no combined-stream bench exists; whether a slow onset and a fast onset are one event is goal 4's open question |

**Operating points are not changed overnight.** The reruns produce searches and proposed settings;
adopting a detector's shipped settings stays Tony's, as it was for the slow reference.

---

## WSMIP065 — the bench constants, then the searches

Start from `main`, pull first, claim both boards. Tony confirms the dataset default in your session.

1. **Make the jitter measurable by the re-measure.** `tools/remeasure_bench.py` still takes
   `jitter_sec` from `assess_coactivity`'s within-cluster spread (`jit_obs`), the instrument the
   correlogram showed tracks bin ÷ √12. Change it to take jitter from
   `tools/measure_jitter_correlogram.py` (calibrated half-width), with its bootstrap interval, so
   `docs/learned/bench_measured.json`'s `jitter_sec` row is the correlogram's. Same for the slow
   stream's `tools/measure_slow_bench.py` → `bench_measured_slow.json`. Keep `jit_obs` in the
   record under another name as provenance, not as the checked value.
2. **Move the constants.** `bench.BENCH_RECORDING`: `jitter_sec=0.106`,
   `participation=(0.30, 0.19, 0.10)` (outer levels unchanged — they bracket the median).
   `bench_slow`: `jitter_sec=0.135`. Update the docstrings' tables and provenance. Remove
   `participation` from `MEASURED_OUTSIDE_INTERVAL`.
3. **Move `bench.MEASURED_ROLE` to the default dataset** (0.19 todo, step 3), re-measure both
   benches, and move `tests/test_bench_is_measured_on_the_declared_folder.py` and the bench's
   `ROLE_LITERAL_ALLOWED` entries with it.
4. **Full suite green**, then one PR: *"The bench adopts the measured jitter and 0.19"*. Remove
   ruling-queue item 2 from `docs/decisions_pending.md` and close the 0.19 todo in the same PR.
   Set it to auto-merge.
5. **Rerun the every-knob search** on the new bench, fast then slow
   (`tools/search_all_settings.py --bench fast|slow`, about 11 min each), archive each with
   `--archive-as`, commit the run records under `docs/learned/runs/2026-09-23-…`. Report the
   proposed operating points against the current ones in the run README; do **not** edit
   `OPERATING_POINTS`.
6. When done, write one line at the bottom of this section: what merged, where the runs are.

## WSMIP064 — the sweep's findings, then the new measurements

Start from `main`, pull first, claim both boards. Tony confirms the dataset default in your session.

1. **The crowded-allowance sweep** you finished: push its output and a findings note to
   `nets/crowded-allowance-sweep` ([#682](https://github.com/syncytium2/bugarach/pull/682)), do the
   4-row top-up if it is under an hour, and set #682 to auto-merge.
2. **When `tools/measure_coordination_rates.py` is on `main`** (the orchestrator is writing it now;
   it will say so), run it on the default dataset's baseline windows for **fast, slow and
   combined**, with its calibration. Commit the run record under
   `docs/learned/runs/2026-09-23-coordination-rates/`. If the calibration passes, open a PR that
   adopts quiet/busy and the probe level per the table above, rebased on WSMIP065's constants PR.
3. When done, write one line at the bottom of this section.

## Orchestrator (cloud)

Writes `tools/measure_coordination_rates.py`, tests it on simulations with known answers, merges
it; checks each workstation about every 45 minutes; merges green PRs; writes the morning status.
