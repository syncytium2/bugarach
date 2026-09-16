# HANDOFF — the overnight search over every detector setting, and finishing the review tomorrow

**Written 2026-09-16, ~15:30.** Tony: *"we need to finalize the detector review document
tomorrow."* The choice he made: **ship the review with the shipped settings, and run a search over
every declared setting overnight as a measurement** — its result goes into the document, and no
operating point changes tomorrow.

## 0. Changed at 16:00 — LoCo and CoactDetect now slide

Tony, ~15:50: *"the loco and coact should slide not step"* — filed 2026-09-07
(`docs/todo/2026-09-07-detector-calls-move-with-the-grid.md`) and never done. Then: *"fix loco
and coact for tonights run. start with how much slower they are."*

- **The first run (stepped) was stopped at 15:46**, mid stage 1; its files are in
  `stepped-run-stopped/` in the darkroom folder. Its LoCo results were chasing a smaller and
  smaller threshold step — the binned detector approximating a slide.
- **Branch `sliding-loco-coact`** (pushed, **not merged**, merged into `full-search`):
  `src/bugarach/detectors/sliding.py`, a `window_mode="sliding"` branch in `coact.py` and
  `loco.py`, shipped `OPERATING_POINTS` switched to sliding, `MAX_PRECISION_DROP` moved into
  `bench.py`, `tests/test_sliding_window.py`.
  - The count is an exact step function of distinct ROIs in a trailing window; the null is
    **computed, not drawn** — each ROI's catch probability under a uniform circular shift in
    closed form, the null count an exact Poisson-binomial. No random numbers.
  - **Shift probe, same three real TTX baselines:** both keep **100% of calls at every shift
    0.1–0.9 s**, matched within 0.05 s (binned: LoCo 47% mean, CoactDetect 0% at that tolerance;
    64% / 70% at the September probe's 1 s).
  - **Cost: 2–4× binned**, 0.06–2.2 s per recording.
  - Binned stays as the MATLAB port; its parity tests pass unchanged.
- **Not landed, and why:** at their binned-tuned values, sliding LoCo and CoactDetect call more
  and fail `test_precision_survives_the_regime_shift` (LoCo precision 0.53 busy vs 0.67 quiet,
  budget 0.10). The overnight search chooses new values under that budget; **set them in
  `OPERATING_POINTS` before merging**, then CI.
- **Still binned:** the browser viewer's `loco.js` / `coact.js`, and `docs/forks.md` has no entry
  yet. Both are owed before this is finished.

## 1. What is running

- **Process:** detached (`Start-Process`, hidden), **PID 34692**, 44 workers, **started 16:06**
  with LoCo and CoactDetect sliding (the 15:25 stepped run, PID 28648, was stopped).
- **Command** (from `bugarach-worktrees/full-search`, `PYTHONPATH=src`):
  `python tools/search_all_settings.py --workers 44 --full loco --out "<darkroom>/bugarach/2026-09-16-full-search"`
- **Output**, all in `<darkroom>/bugarach/2026-09-16-full-search/`:
  - `search.log` — progress, one timestamped line per step; `search.err` — stderr.
  - `search.json` — **rewritten after every stage**; its `stage` field says how far it got
    (`rounds done` → `pairs done` → `held-out done` → `full loco done` → `finished`).
  - `full_search.html` / `full_search.png` — the figures, written after the held-out stage and
    again after LoCo's full grid.
- **Expected time:** stages 1–3 well under an hour; stage 4 (LoCo, ~3,000 combinations × 144
  recordings each) roughly 40–90 minutes more. If `stage` is not `finished` in the morning, read
  `search.log` for where it stopped — everything before it is already saved.
- **If it died:** rerun the same command; it has no resume, and all of stages 1–3 took minutes.

## 2. What it measures, and the one number to quote

The tool's docstring is the full statement. In short: coordinate rounds from the shipped point,
two-setting grids for three pairs, LoCo's every combination, all chosen on recordings 1–48 and
**re-scored on recordings 49–96**, with a 95% bootstrap interval on each candidate's gain over the
shipped point. Both false-alarm budgets gate every choice.

**Quote the held-out gain, never the "chosen on" F1.** The table shows both so the optimism of
choosing is visible. How to read it for the review:

- **Interval includes zero** for a detector → "every declared setting was searched; nothing beats
  the shipped point on recordings the search did not see." That is the result that answers Tony's
  *"it looks unfinished."*
- **Interval excludes zero** → report the finding and its size as found, not adopted. **Do not move
  `OPERATING_POINTS` tomorrow.** Window-shaped settings (context, integration, bin width) are the
  ones most exposed to the bench's structure — planted events at least 120 s apart — and need the
  crowded recordings and real calls before anyone adopts them.

What was already visible at 2 recordings in a smoke run (not evidence, just what to look for):
locust's `n_synchronous_frames` 1 → 10 with `sce_min_distance_frames` 4 → 32 scored far above the
shipped point. The real run will say whether that survives 48 held-out recordings. The first real
step moved locust's percentile 99.999 → 99.99 on the selection recordings — the same +0.010 the
retune found and rejected as inside the noise.

## 3. Where the settings stand (all merged today)

| PR | what |
|---|---|
| #593 | binned SCE calls scored over their own bins (`SceStream.extent_sec`) |
| #594 | locust holds each cell for the event's own `width_sec`; every simulated recording carries widths from the export's FAST distribution |
| #597 | retune of the one swept setting per detector: binned SCE 99 → 98, LoCo 99.9 → 99.5, rate+context 5.0 → 4.5 Hz; the empty-recording budget moved into `bench.py`; `tools/retune_operating_points.py`; Figure in `<darkroom>/bugarach/2026-09-16-best-parameters/` |

The full table Tony saw, one unit (false alarms per hour), 48 recordings:

| detector | setting | F1 quiet | F1 busy | mean F1 | empty stretch quiet [limit] | empty stretch busy | empty recording [limit] |
|---|---|---|---|---|---|---|---|
| binned SCE | 99 → 98 | 0.536 → 0.557 | 0.444 → 0.492 | 0.490 → 0.525 | 344 → 347 [540] | 337 → 340 | 1.6 → 3.4 [6] |
| LoCo | 99.9 → 99.5 | 0.710 → 0.739 | 0.628 → 0.633 | 0.669 → 0.686 | 1.8 → 9.6 [60] | 3.0 → 9.6 | 0.5 → 1.7 [3] |
| rate+context | 5.0 → 4.5 Hz | 0.602 → 0.660 | 0.610 → 0.601 | 0.606 → 0.630 | 33 → 68 [120] | 63 → 101 | 0.0 → 0.1 [1] |
| CoactDetect | 1e-4 | 0.753 | 0.648 | 0.700 | 5.4 [60] | 3.0 | 2.9 [7] |
| SPIKE-synch | 0.1 | 0.433 | 0.466 | 0.449 | 15 [60] | 35 | 0.0 [1] |
| locust | 99.999 | 0.561 | 0.521 | 0.541 | 470 [1,500] | 256 | 1.1 [6] |

⚠ **rate+context's gain is all on the quiet background**; on busy it is slightly lower with more
false alarms. Tony saw this; no ruling yet.

## 4. Tomorrow, in order

1. **Read `search.json` / the figures.** Release the darkroom claim in `docs/SESSIONS.md` (git board)
   once `stage` is `finished`, and mark `065/full-search` and `065/sliding-loco-coact` DONE on the
   local board.
2. **Land sliding LoCo and CoactDetect** (§0): take their new threshold values from the search
   (held-out, all three budgets), set them in `OPERATING_POINTS` on `sliding-loco-coact`, add the
   `docs/forks.md` entry, and merge. This one *does* change operating points — Tony asked for it.
   Then land `full-search` (tool, tests; this handoff to `docs/handoffs/` or deleted).
3. **The review document is on branch `detector-review-doc` (PR #587).** Its numbers predate all
   three merges above — locust's widths, binned SCE's scoring, the retuned points. Merge `main` into
   it and regenerate: `tools/make_detector_review.py`. ⚠ Its selection "rounds" come from
   `tools/fair_bakeoff.py` runs (`--bakeoff RUN_DIR`), the ungated path Tony called stale on
   2026-08-28; the corrected `HANDOFF-detector-optimization.md` on that branch says so. Decide
   whether the document still shows those rounds or the retune's figure instead.
   ⚠ **Another session committed to that branch today** (13:12, 13:43: *"Why not just count cells in
   a bin?"*, with a darkroom claim). Check the board and its commits before writing there.
4. **Add the search result** to the document (§2 above for how to phrase it).
5. **Murderboard** the document before it goes out (CLAUDE.md: a document deliverable with figures).

## 5. Decisions still Tony's

- **Binned SCE: 98 or 75.** 75 scores mean F1 0.665 against 0.525 at 42 false calls an hour on the
  empty recording against a limit of 6 — `docs/todo/2026-09-16-binned-sce-trades-false-alarms-for-f1.md`.
- **locust's anchor** — half-rise in Python, peak in the browser, and the width is now painted
  forward from it — `docs/todo/2026-09-16-locust-anchor-and-the-panel-viewer.md`.
- **rate+context 4.5 Hz**, given the gain is quiet-background only (§3).

Both todos are `status: open`, not `waiting-on-tony`: the session briefing has no room for another
waiting item (`docs/todo/2026-08-30-the-briefing-has-one-todo-of-headroom.md`).

## 6. When this is spent

Delete it once the search result is in the review document, or move it to `docs/handoffs/` if §5
is still open then.
