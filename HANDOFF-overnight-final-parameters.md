# Runbook: the night that takes the detectors to final parameters

**For a fresh orchestrator session.** Written 2026-09-24 by the orchestrator, at Tony's request:
*"R1-R5 as recommended, write the runbook for a fresh orchestrator session"*. It is at the repo root
because the work is in flight. Phase 0 finishes
[#793](https://github.com/syncytium2/bugarach/pull/793). When the morning report lands, move it to
[`docs/handoffs/`](docs/handoffs/README.md).

**Read first, in this order:** `CLAUDE.md`, [`docs/FOUNDATIONS.md`](docs/FOUNDATIONS.md),
[ADR-0008](docs/adr/0008-the-event-floor-is-set-per-window-from-its-own-null.md) (the floor),
[ADR-0009](docs/adr/0009-the-bench-keeps-its-elevated-rate-test-in-a-recording-of-its-own.md) (how the
bench meets it; tonight's rulings R1–R5), and the goal page
[`docs/goals/coded-detector-optimization.md`](docs/goals/coded-detector-optimization.md).

## What "final" means

A setting is final when all four hold:

1. **It was tuned under the definitions it is scored under:** ADR-0008's floor, on the bench as
   ADR-0009 builds it.
2. **It is an interior optimum:** bracketed on both sides, not stopped at a grid edge or at the
   search's extension cap.
3. **It is confirmed** on held-out seeds and on fresh seeds, inside every budget.
4. **Tony adopted it** into `bench*.py` in the morning. Nothing is adopted overnight.

Last night's proposals (2026-09-24) fail 1, because they are pre-ADR-0008. Some also fail 2: fast
SPIKE-synch's `dt` and `C_min` stopped at the search's cap.

## Who does what

- **Tony** sets up a new session on each of WSMIP064 and WSMIP065. In each, he confirms the default
  dataset himself (`python -m bugarach.dataset confirm`). `dataset.default()` refuses until he does,
  and no session runs that on his behalf.
- **The orchestrator (you)** briefs both sessions, checks every output against this page, merges only
  what is green, and writes to Tony. You do not run the searches or edit their tools yourself.
- **Reaching a session:** find it with `list_sessions`. To send a message, create a one-shot trigger
  bound to that session, run it once and delete it. Running an old trigger a second time has
  spawned new sessions twice; never do it.
- **Every change** is a PR against `main`, set to auto-merge when green. Never force-push, never
  rebase a pushed branch, never commit on `main`, and never merge a PR into another PR's branch. No
  MATLAB and nothing in interface2 (ADR-0007).

## Phase 0, evening: build (one session, suggested WSMIP065)

**Nothing in phase 2 starts until this has merged to `main`.** Finish #793 on its own branch,
`floor-adr-0008`, by merging `main` into it (no rebase):

1. **Wire the floor in:**
   - inject each recording's ADR-0008 floor as `min_rois` in `run_detector`;
   - make the scorer honour it;
   - score treatment windows under both floors in the detection path.
2. **ADR-0009 decision 1, the bench:**
   - drop `hot_window` from `BENCH_RECORDING` and from every recording built from it (crowded, tail),
     on the fast, slow and combined benches;
   - add an elevated-rate recording (the stretch, no planted events), scored for calls per minute
     inside the stretch against `MAX_PROBE_PER_MIN`, and calls per hour outside it against
     `MAX_FALSE_POSITIVES_PER_HOUR`;
   - keep the recordings' length and event spacing unchanged.
3. **Decision 2, "don't care":** a planted event under its recording's floor leaves recall, and a
   call matched to one leaves precision. Report the count by participation level with every score.
4. **Decision 3:** take `min_rois` and SPIKE-synch's `min_n` out of `FULL_GRIDS` (both are set by the
   floor).
5. **Decision 5, context grids:** 20, 30, 45, 60, 90 and 120 s for CoactDetect, LoCo and
   rate+context. Cap any guard at a quarter of the context.
6. **Bracketing:**
   - raise `MAX_EXTENSIONS` in `tools/search_all_settings.py` enough for last night's edges to
     bracket;
   - any proposal still at a grid edge or at the cap is marked **unbracketed** in `candidates.json`
     and is not adoptable.
7. **Re-measure the bench floors** with `tools/probe_bench_floor.py` on the new generator, 8 seeds ×
   2 backgrounds × 3 benches. Report, by participation level, the share of planted events under the
   floor.
   - ADR-0009 expects 5–10 co-active ROIs on fast and combined, and 6–8 on slow.
   - **If the new numbers differ materially, stop and tell Tony before phase 2.** "Materially" means
     outside those ranges, or the middle planted level mostly under the floor on quiet recordings.
8. **Tests** for each of 1–6, then the suite green, sapper and `check_quotes` clear.

## Phase 1, evening, in parallel: pilot (the other session, suggested WSMIP064)

On phase 0's branch, before it merges:
- one detector per bench on 4 seeds;
- one chorus fit per stream.

The purpose is to measure wall-clock time per search and per fit, and to catch breakage. Report the
projected time for phase 2 per machine. If it does not fit the night, tell the orchestrator which
part to drop. Drop the learned models before any coded detector.

## Phase 2, overnight: search and train (both sessions, after phase 0 merges)

Split by stream so that no search is on two machines:

| Machine | Work |
|---|---|
| The one with the GPU (last night that was WSMIP064, `--device cuda`) | **fast**: every coded detector searched. **Chorus:** chorus_norm and chorus_gain_norm retrained on all three revised benches, 5 seeds per stream. |
| The other | **slow** and **combined**: every coded detector searched |

- **Coded detectors:**
  `tools/search_all_settings.py --bench <b> --sliding --workers <n> --out <run>/search-<b>`.
  Chosen on seeds 1–48 and held out on seeds 49–96, as the tool does.
- **Chorus:** `tools/train_learned_on_bench.py --bench <b> --model <m> --seeds 0 1 2 3 4 --device cuda
  --out <run>/models-<b>`. Each training run's own rule picks the checkpoint.
- **Label the floor** in every run record as "ADR-0008 per-window floor, bench per ADR-0009". No run
  tonight may be labelled pre-ADR-0008.

## Phase 3, overnight: confirm

After phase 2, on whichever machine is free:

1. **Fresh-seed scoring:** `tools/score_bench_candidates.py`, run on every shipped point and every
   proposal.
   - Seeds 6000–6023 per background, the no-coordination recording on 56000–56011, and the new
     elevated-rate recording on its own seed range (state it).
   - F1 as scored and without decoys (ADR-0006), every budget, and the under-floor counts.
2. **The 3 × 3:** `tools/score_cross_stream.py` on the new versions.
3. **Real data:** `tools/detect_with_floors.py` on the 66 recordings with the proposals. Every window
   is scored under both floors, the result is stamped with `dataset.stamp()`, and it is descriptive
   only (FOUNDATIONS §9).

## Phase 4, morning: one report for Tony

One page in `docs/learned/runs/<date>-final-parameters/`, copied to the darkroom, figures numbered,
every number with its unit, groups in DI, OVX, MALE, ORX order:

- **An adoption table, one row per detector × stream.** Each row gives:
  - the shipped point and the proposal;
  - the held-out gain with its 95% interval;
  - fresh-seed F1 both ways;
  - every budget, marked pass or fail;
  - bracketed, yes or no;
  - the under-floor counts.

  **Adoptable** means the gain interval is above zero, every budget passes, and the proposal is
  bracketed. Everything else is listed with its reason.
- **Figures:**
  - F1 for shipped against proposed;
  - the 3 × 3;
  - the elevated-rate recording (calls in and outside the stretch);
  - the bench floors re-measured.
- **What waits on Tony:** only the adoptions, and anything a stop rule below raised.

## Stop rules

Each of these goes to Tony that morning, or at once if he is awake. None of them is decided by a
session.

- **A known contamination** (`dataset.refuse_if_contaminated()`) stops the work.
- **Phase 0's floors differ materially** from ADR-0009's expectation (phase 0, step 7).
- **A search ends unbracketed.** Rerun it bracketed if time allows. Never pick the edge.
- **A proposal fails a budget.** It is reported, not adopted, and no limit is loosened (ADR-0009,
  decision 4).
- **Anything this page did not foresee that would need a new definition.** Stop that line of work,
  finish the others, and ask.

## The orchestrator's night

- **Claim** the work on both boards before any session writes. Check the darkroom claims in
  `docs/SESSIONS.md`.
- **Brief** each session with its phase, pointing it at this page and at ADR-0009.
- **Check in** with `send_later` about hourly. At each check, go through open PRs, CI, what each
  session last pushed, and any stop rule. Re-arm the next check.
- **Verify each run record** before it merges:
  - the floor label and the dataset stamp are present;
  - intervals are paired;
  - the under-floor counts are reported;
  - unbracketed results are flagged;
  - nothing is drawn on a raster.
- **In the morning:** tell Tony where the report is, with its paths. Move this file to
  `docs/handoffs/`. Update the goal page in the same PR as the report.
