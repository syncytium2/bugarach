# Overnight 2026-09-22 → 23: adopt the measured jitter, measure the rest, rerun

> **Done, 2026-09-23 04:41 EDT. Nothing is in flight.** Every section below landed: #748, #750,
> #752–#759. Moved here from the root because the decisions it lists are still Tony's. The
> morning status page carries them, numbered, with the SPIKE-synch question first (robust to the
> background, or keyed on rate?). Kept as the night's record: rulings 1–7, what was adopted and
> what was only reported, and each workstation's own notes.
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
5. **(later, 2026-09-22 ~21:00 EDT) The probe moves to the measured 99th percentile** of 5-minute
   baseline stretches, so the methods statement's "99th percentile of the baseline frequency" is
   true of the bench. Adopted **before** the searches run, so one rerun covers every change tonight.
   *As first relayed, this named fast's raw value (0.128) and slow's background one (−9%) — two
   quantities; see 5a.*
5a. **(~21:45 EDT) The basis is background, end to end** —
   [#748](https://github.com/syncytium2/bugarach/pull/748). Quiet, busy and both probes are all
   raw minus the coordinated share, on the bench's `shape_usable` set, fixed model, 1 s window:
   probe fast 0.060 → **≈0.127 Hz**, slow 0.032 → **≈0.029 Hz**; quiet/busy 13–22% below today's.
6. **(same time) SPIKE-synch flat across the background axis is a result, not a reason to change
   the axis.** Tony: *why change something because SPIKE-synch fails to improve? It's middle of the
   pack.* The axis is measured from baseline recordings and stays; the MILESTONES row that says no
   detector is flat is corrected; the searches run.
7. **(~22:00 EDT) Combined is a third stream, the same pipeline as fast and slow.** Tony: the
   pipeline fed both streams' onsets as one stream, labels kept for plotting, the same correlogram
   and characterisation, a third parameter set from the detector search, two-colour rasters with
   detection, and the fireflies export prepared, *"just like fast and slow"*. The code is
   [#752](https://github.com/syncytium2/bugarach/pull/752); the run is the **Combined** section below.

**Order from here:** ~~#738 (constants)~~ merged → WSMIP064 marks #748 ruled and merges it, then
its adoption PR (background values throughout: quiet, busy, both probes), merged → WSMIP065 runs the
fast and slow searches on the finished bench. The 21:04 fast search was stopped and deleted (#749).

### What is adopted tonight, and what is only reported

| value | tonight | why |
|---|---|---|
| jitter, both streams | **adopt** | ruled |
| participation middle level 0.19 | **adopt** | ruled |
| quiet / busy background rate | **adopt** if the tool's calibration passes | replaces like with like: total rate minus the coordinated share |
| probe (elevated-rate stretch) level | **adopt** if calibration passes | replaces a chosen multiple of the median with a measured high percentile of untreated 5-minute stretches |
| event frequency, participation from cumulants | **report only** | the bench plants a fixed participant count at three levels with ≥120 s spacing (a design floor that keeps each detector's null clean). The cumulant measure is a per-cell join probability over all shared moments, including ones joined by one or two cells. Adopting it means restructuring how events are planted, which is a decision, not a substitution |
| anything **combined** | ~~report only~~ **a third stream, run end to end** (ruling 7) | #752 builds the combined bench and gives every stage a `combined` value; the membership question stays open because nothing is deduplicated |

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

- **2026-09-22 ~20:40 (WSMIP065): steps 1–3 are written and pushed; steps 3 (the re-measure),
  4 and 5 are BLOCKED on one thing, and it is Tony's.** Branch `opt/bench-measured-jitter`,
  **[#738](https://github.com/syncytium2/bugarach/pull/738), left a DRAFT on purpose and not
  set to auto-merge** — it cannot be green as it stands. Both benches carry the measured
  jitter (fast 0.106 s, slow 0.135 s) and participation 0.19; `MEASURED_OUTSIDE_INTERVAL` and
  `ROLE_LITERAL_ALLOWED` are both empty; `MEASURED_ROLE` is `"default"`; and both re-measure
  tools now read `jitter_sec` from the correlogram record rather than deriving it, refusing a
  record measured on a different folder. **What blocks it:**
  `test_bench_is_measured_on_the_declared_folder` fails by design — *"a constant changed
  without re-measuring"* — and the re-measure needs `dataset.default()`, which refuses until
  Tony runs `python -m bugarach.dataset confirm` in a session on this machine. A session does
  not run that on his behalf. **After the confirm this is two commands** —
  `python tools/remeasure_bench.py --jobs 12` and `python tools/measure_slow_bench.py --jobs 12`
  — then step 4's doc changes and step 5's searches, which had no chance to start.
  **Two things whoever picks this up needs.** First, **a worktree on this machine imports the
  primary checkout's `src/bugarach`**, because the editable install points there: 87 tests
  "passed" against unmodified code before this was noticed. Export
  `PYTHONPATH=<worktree>/src` before `pytest`, or the suite is not testing your branch.
  Second, **`main` is red on Windows** for reasons that predate tonight — `read_text()` with no
  encoding, walking repo source that carries em-dashes — fixed for two files in #738 and filed
  more widely, with sapper's own crash, in
  [`docs/todo/2026-09-22-sapper-crashes-instead-of-reporting-on-windows.md`](docs/todo/2026-09-22-sapper-crashes-instead-of-reporting-on-windows.md).
  No darkroom folder was written; the git-board claim for step 5 is live and unwritten.
- **2026-09-22 ~20:30 (WSMIP065): Tony confirmed the folder, steps 3 and 4 are DONE, and step 5
  is HELD on a finding — not on a blocker.** Both benches re-measured on
  `2026-09-17_revised_2v_long_STEPS_AND_PINS_EXCLUDED` (84 recordings, 0 skipped) and **every
  constant landed inside its interval**; `MEASURED_OUTSIDE_INTERVAL` is empty. Ruling-queue item 2
  is a stub and the 0.19 todo is closed. [#738](https://github.com/syncytium2/bugarach/pull/738)
  carries all of it and is **still a draft, still not on auto-merge**, because the suite is not
  green and should not be made green by editing a test.
  **The finding, and it is the reason to stop:** on the corrected jitter **SPIKE-synch goes flat
  across the background difficulty axis** — F1 0.657, spread 0.026 against a 0.05 tolerance, at
  12 seeds per grid point. The MILESTONES row *"nothing is flat across it"* (`measured`,
  `current`, `c7786f2`) is no longer true of this bench. Figure 1 is
  `<darkroom>/bugarach/2026-09-22-jitter-background-curve/background_curve.png`; the full write-up,
  with what is and is not Tony's, is
  [`docs/todo/2026-09-22-the-corrected-jitter-flattens-spike-synch-across-the-axis.md`](docs/todo/2026-09-22-the-corrected-jitter-flattens-spike-synch-across-the-axis.md).
  One of the three readings is closed rather than left open: the flattening is **not** a
  quantisation artefact of planting 0.106 s on a 0.1 s grid — the correlogram's own calibration
  resolves 0.05 s from 0.10 s from 0.15 s cleanly.
  **WSMIP064 should know two things.** `tools/build_fair_comparison_report.py` now refuses to
  rebuild the 2026-09-18 fair comparison, correctly — that run declared `jitter_sec` 0.36, so the
  weekend result, the merge-gap addendum and the leaderboard all belong to the old bench. And any
  slow-stream work inherits this: SPIKE-synch was adopted on slow at `max_gap` 4 s on old-jitter
  evidence.

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

**Step 1 DONE 2026-09-22 22:10 UTC — #682, #740, #741 merged.** The sweep is complete (11
allowances × 2 draws, every cell measured) and the 4-row top-up is **closed, not skipped**: it was
cheap once run strict-end-first — the replicate's 0.000 took 6 rounds, then 0.005 and 0.010 took
one each off the cache it had filled. **The verdict only flips where the search is pinned at the
30 s gap-grid edge**: 0 of 32 selections sit there below an allowance of 0.10, all 32 at 0.25 and
looser, and at the strict end both draws put CoactDetect ahead in 31 of 32 cells. Record and
Figure 1 in `docs/learned/runs/2026-09-21-crowded-allowance-sweep/`; bulk in the darkroom, claim
released. **Adjudicates nothing** — no operating point moved, `MAX_CROWDED_DROP` still 0.02.
*Found and fixed on the way:* `sapper.py --staged`, the pre-commit gate, crashed on native Windows
(cp1252) printing any staged line containing `→`, `⚠` or an em dash, and `check_quotes.py` had the
same defect and runs first in the hook. CI is UTF-8, so only this workstation ever saw it —
`test_tracked_tree_is_clear` included, which asserts `--all` exits 0 and could not pass here. Both
forced to UTF-8, two regression tests that force cp1252 (#682).

**Step 2 MEASURED 2026-09-22 — #743 merged (`f9bde16`). The adoption PR is deliberately NOT
opened.** Tony confirmed the default dataset in his own words and told this session to run
`dataset.default()`'s confirm; it was run on that instruction, not on the relayed one. Record and
Figure 1: `docs/learned/runs/2026-09-23-coordination-rates/`, darkroom claim released.

*What it found.* **A defect in the tool, first**: quiet and busy were measured over all 84
recordings while `remeasure_bench.py` — which *set* `bench.REGIMES` — uses only recordings
clearing `fit_background_shape`'s floors. Two recording sets, reported as a measurement; the tell
was quiet off 30% while busy agreed to 2%, because the floors cut the quiet tail. **On the bench's
own set the raw rates reproduce `bench.REGIMES` to within 3%** (80 of 84 recordings on fast, 75 on
slow). Found by the orchestrator, verified here against both tools before acting, fixed with two
tests, and the all-recordings pair kept beside it as `*_all_recordings`.

*So the real proposal is smaller than the first run claimed:* **the whole quiet/busy change is the
coordination subtraction, 13% to 22% on both streams.** The probes split — fast's correction at
the probe is −0.6%, so its **+112%** is purely a change of definition (99th percentile of 300 s
stretches vs a chosen multiple of the median); slow's is −35.9%, and its small net −9% is two
large opposite moves cancelling. ⚠ Calibration is **not uniform**: slow clears every window, fast
clears **only 1 s** (+0.46 at 2 s, +1.00 at 4 s), and the `passed` flag never inspects the two
terms where slow is worst (moment rate −22.8%).

*Baseline only, confirmed with the count as Tony asked:* a recording with no declared baseline
region returns `window=None` and is **dropped, not measured over its whole span**. All 84
contributed; no treatment window enters any number.

**ADOPTION DONE 2026-09-22 — [#756](https://github.com/syncytium2/bugarach/pull/756) merged
(`2c19003`), green on all three legs. 065's fast and slow searches are unblocked.** Tony ruled
**background, end to end** (#748): `bench.REGIMES` 0.0042/0.0165, `bench_slow.REGIMES`
0.0024/0.0089, probes 0.1271 and 0.0291, each with its provenance in its own docstring.

⚠ **FOR TONY — adopting the constants reversed four things this tree had pinned as findings.**
Every one was **re-measured and restated**, never re-baselined: no tolerance loosened, no test
skipped, and each restated test asserts the *mechanism* so it cannot pass for an unrelated reason.

1. **No detector is a steady leader across the whole background axis any more.** Three win
   somewhere — CoactDetect quiet, LoCo middle, SPIKE-synch busy. The leader still holds between
   the two named `REGIMES` endpoints, which is where we report.
2. **The fitted-versus-flat contrast `tests/test_background_curve.py` is named for is gone.** Both
   fields now show the same flat set, the same three winners, the same rank change of four. Only
   magnitude separates them: mean own-range 0.126 fitted against 0.171 flat.
3. **Three probe ceilings rose because the PROBE rose, not because a detector got worse** — and
   the harder probe exposed what the gentle one could not. Calls per minute into a block with
   nothing in it: **CoactDetect 0.08 and LoCo 0.21 — they do not key on rate at all** — against
   rate 4.14 (3.8x), cicada 29.66 (1.7x) and **SPIKE-synch 5.54, a 28x jump** from 0.2. Sync was
   passing a 1.0 ceiling only because the probe was too gentle to ask.
4. **The shipped bake-off stopped failing its gate.** rate+context fires 3.47/min: it failed a
   ceiling of 2.0 and passes one of 4.5. *Nothing about the shipped file changed* — it still picks
   knobs by raw argmax with no probe gate; that choice is simply not over the line now.

**1, 2 and 3 are one detector.** SPIKE-synch's flatness reads as **robustness** on the background
axis and as **rate-keying** on the probe. That is one observation, not two, and **which it is is
deliberately decided nowhere in this change** — it is a judgement about the detector, not about
the constants. It is the thing to look at first.

**One number worth its own line:** at this probe, rate+context's shipped setting sits within about
**10%** of the setting its own gate exists to refuse (3.83 against 4.98/min). There is no longer
room for the 1.6x headroom rule, so that one ceiling is hand-set at 4.5 from the separation window,
checked to separate on seeds 1–48 *and* on the test's own seed. Every other ceiling came from the
unchanged rule.

Unchanged by the adoption: **slow is the stream to be slowest about** — this run, the per-group
correlogram (#744, slow borderline at p = 0.054) and ruling item 3 all point the same way. And the
calibration now excludes the probe stretch, which admits that a real baseline window containing a
busy stretch may be **slightly over-subtracted**: bounded small on fast (0.6% of the rate at the
probe), not obviously small on slow (35.9%).

## Combined — the third stream, end to end (WSMIP064, after its adoption PR)

Needs [#752](https://github.com/syncytium2/bugarach/pull/752) on `main`. Every step is the fast/slow
step with `combined` passed, in the order `src/bugarach/bench_combined.py`'s docstring gives.
`PYTHONPATH=<worktree>/src` throughout; claim `<darkroom>/bugarach/2026-09-23-full-cohort-combined/`
on `docs/SESSIONS.md` before step 7.

1. **Jitter:** `python tools/measure_jitter_correlogram.py --jobs 12 --streams combined --out
   docs/learned/runs/2026-09-23-jitter-correlogram-combined`.
2. **Bench values:** `python tools/measure_slow_bench.py --stream combined --jobs 12 --jitter-record
   docs/learned/runs/2026-09-23-jitter-correlogram-combined/jitter_correlogram.json` →
   `docs/learned/bench_measured_combined.json`. Also report `bugarach.combined.near_coincident` at
   one frame (0.1 s): how many slow onsets sit within a frame of a fast one on the same ROI. That
   is the count goal 4's membership question turns on, and the union keeps both.
3. **Background and probe:** `python tools/measure_coordination_rates.py --jobs 12 --out
   docs/learned/runs/2026-09-23-coordination-rates-combined`. It reads the combined bench, so it
   takes the calibration change you are making to `_sim` for fast.
4. **Transcribe** into `bench_combined.py`, like slow's: jitter; `n_roi`; participation middle =
   measured, outer levels at slow's ratio around it; rate and 300 s burst shapes; width table;
   `REGIMES` = background quiet/busy; `hot_rate_hz` = background 99th percentile (ruling 5a);
   `distractor_frac` = the middle participation. Clear `PROVISIONAL`. Then
   `python tools/measure_slow_budgets.py --bench combined --jobs 12` and put its ceilings into
   the three `MAX_*` tables. One PR, *"The combined bench is measured"*, with auto-merge.
5. **Search:** `python tools/search_all_settings.py --bench combined --sliding --jobs 12`,
   archived like fast's and slow's; the run record goes under
   `docs/learned/runs/2026-09-23-full-search-combined/`.
6. **The third parameter set:** write the search's held-out picks into
   `bench_combined.OPERATING_POINTS`, each with a `source` saying it is the search's pick and
   Tony asked for it on 2026-09-22 (awaiting his review, as slow's were). This is the combined
   stream's own set. It is **not** `bench.OPERATING_POINTS`, and fast and slow are untouched.
7. **Detect, rasters, export:** in the claimed folder,
   - `python tools/settings_from_bench.py --bench combined --out <claimed>/combined_settings.csv`
   - `bugarach detect <default folder> --stream combined --settings <claimed>/combined_settings.csv --out <claimed>/detect`
   - `python tools/measure_calls.py --detections <claimed>/detect/detections.csv` (slow's aperture)
   - `python tools/make_group_raster_summary.py --steps-excluded --streams combined --detections
     <claimed>/detect/detections.csv --out <claimed>/rasters`. Fast onsets are black and slow ones
     vermillion. Use the same flags as the slow set in `2026-09-22-full-cohort-slow/`.

   `detections.csv` and `detector_settings.csv` carry `stream=combined` rows: that is the
   fireflies export, **prepared, not sent**. A third stream value is a contract change for their
   adapter (`docs/decisions_pending.md` item 4), so it goes with that conversation.
8. Write one line here: what merged, where the runs and rasters are. **Show one raster page**
   (`tools/show.py <png> --project bugarach`).

## Orchestrator (cloud)

Writes `tools/measure_coordination_rates.py`, tests it on simulations with known answers, merges
it; checks each workstation about every 45 minutes; merges green PRs; writes the morning status.
