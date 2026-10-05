# HANDOFF — evaluate the revised LoCo and CoactDetect (sliding), and the settings the search found

> **Retired from the root on 2026-09-21, exactly as its successor said it would be.**
> [`HANDOFF-coded-detectors.md`](../../HANDOFF-coded-detectors.md) supersedes it and said *"when
> that branch lands, that file moves to `docs/handoffs/`"*. `full-search` has landed, so it moved.
> ⚠ **Four of its readings are corrected there**, in §2 — among them that the LoCo winner's 8 s
> merge gap is the top of its grid, and that locust's 12.8 s minimum distance is where the search's
> extension cap stopped it rather than an optimum. Read the correction before quoting a number
> from here.

**Written 2026-09-17** for a session with none of the context. Tony: *"the overnight run failed.
create a new handoff with the revised models for evaluation by a new session."*

## 0. First: which run failed?

The settings search this handoff describes **did not fail on the machine that wrote it**:
`<darkroom>/bugarach/archive/2026-09/2026-09-16-full-search/` holds `search.json` with `stage: finished`
(2026-09-16 17:02, 11 minutes), an **empty** `search.err`, a complete `search.log`, and a correct
figure (`full_search.png`). Two earlier attempts were stopped on purpose and their files set
aside (`stepped-run-stopped/`, `prototype-run-stopped/`).

So **before anything else, find out what Tony saw fail** — plausibly a different run: another
session was running a large job on LoCo/CoactDetect that evening (Tony: *"they are in use for
another big run by another session"*; branch `tune-learned-vs-coact` was active). Do not assume
the results below are invalid, and do not assume they explain the failure.

## 1. What the revised models are

**LoCo and CoactDetect now slide instead of stepping** — Tony, 2026-09-16: *"the loco and coact
should slide not step"*, a defect measured and filed on 2026-09-07
(`docs/todo/2026-09-07-detector-calls-move-with-the-grid.md`) and never fixed.

The defect had **two** causes, and sliding the window fixes only the first:

1. **Counts in fixed bins** laid from the start of the recording → now an exact step function of
   distinct ROIs in a trailing window, changing only where an event enters or leaves it.
2. **A null drawn from one random stream, consumed bin by bin** (anchor by anchor for LoCo), so one
   changed candidate re-randomised every later bin → the null is now **computed, not drawn**:
   under a uniform circular shift an ROI's chance of landing in a window of width *w* on a circle
   of length *L* is `sum(min(w, gap to its next event)) / L`, and the null count is a
   Poisson-binomial with those probabilities — exact mean and sd for CoactDetect's z-test, exact
   percentile for LoCo's bar. The Monte Carlo was estimating this very distribution.

**Where:** `src/bugarach/detectors/sliding.py`, and a `window_mode="sliding"` branch in
`coact.py` / `loco.py`. `window_mode="binned"` — the MATLAB port — stays the functions' default
and its 1e-9 parity tests pass unchanged. Recorded as `docs/forks.md` §14.

| check (reproduce with `tools/probe_sliding_vs_binned.py`) | binned | sliding |
|---|---|---|
| calls kept when three real TTX baselines are shifted 0.1–0.9 s | LoCo 64%, CoactDetect 70% (Sept probe, 1 s match) | **100% at every shift** (0.05 s match) |
| time per recording | 1× | **0.25–0.75×** |

**What changes for a caller:** `thr_step_sec` and `n_surrogates` do not apply in sliding mode; an
episode's onset is its first participating event (CoactDetect used to report a bin edge); the
guard works in both detectors; peak mode is refused. **The browser viewer's `loco.js` /
`coact.js` are still binned.**

## 2. Branches — nothing here is on `main`

| branch | holds |
|---|---|
| `sliding-loco-coact` | the detector change, `OPERATING_POINTS` switched to sliding (**values not yet retuned**), `MAX_PRECISION_DROP` moved into `bench.py`, `tests/test_sliding_window.py`, `docs/forks.md` §14 |
| `full-search` | everything above merged in, plus `tools/search_all_settings.py` (+ tests), `tools/probe_sliding_vs_binned.py`, this handoff, and the superseded one at `docs/handoffs/2026-09-16-overnight-settings-search.md` |

**Held off `main` on purpose:** another session's run uses these detectors, and merging would
change what its code runs the next time it merges `main`. Coordinate before landing.

**`sliding-loco-coact` will fail CI as it stands:** at their binned-tuned values, sliding LoCo and
CoactDetect call more and break budgets — `test_precision_survives_the_regime_shift`, and the
empty-recording limit (LoCo 4.0 calls/hour vs 3, CoactDetect 7.7 vs 7). New values are part of
the evaluation (§4).

## 3. What the search measured

`tools/search_all_settings.py` — every declared setting of all six detectors, LoCo and CoactDetect
in sliding mode. Chosen on bench recordings 1–48, **scored on 49–96**, which nothing was chosen on,
with a 95% bootstrap interval on the gain. Eligible only under all three budgets in `bench.py`.
Every held-out candidate also scored on 12 **crowded** recordings per background
(`bench.make_tail_recording`, planted events as little as 6 s apart) — a check, never a selection
input. Full output and Figures 1–4: `<darkroom>/bugarach/archive/2026-09/2026-09-16-full-search/`.

| detector | candidate | settings changed | held-out mean F1 | gain (95% interval) | crowded mean F1 (change) | false alarms/hour on the empty recording (limit) |
|---|---|---|---|---|---|---|
| LoCo | shipped, sliding | — | 0.720 | — | 0.869 | **4.0 (3) — over** |
| LoCo | pair | threshold 99.5 → 99.9, context 120 → 240 s | 0.721 | +0.000 (−0.011 to +0.012) | 0.825 (−0.044) | 1.6 |
| LoCo | full grid | threshold 99.9, context 240 s, merge gap 2 → 8 s | 0.734 | +0.013 (+0.003 to +0.025) | 0.808 (**−0.060**) | 1.6 |
| CoactDetect | shipped, sliding | — | 0.712 | — | 0.859 | **7.7 (7) — over** |
| CoactDetect | rounds | alpha 1e-4 → 1e-5, context 60 → 240 s | 0.741 | +0.028 (+0.020 to +0.039) | 0.837 (**−0.022**) | 6.3 |
| locust | rounds | percentile 99.999 → 99.99, synchronous frames 1 → 2, minimum distance 4 → 128 frames | 0.666 | **+0.119 (+0.108 to +0.132)** | 0.794 (**+0.149**) | 5.2 |
| binned SCE, rate+context, SPIKE-synch | — | nothing beat the shipped setting | 0.545 / 0.621 / 0.453 | | | 3.0 / 0.1 / 0.0 |

LoCo's every-combination grid: 750 valid, 256 admissible. Its best five on the selection
recordings, (context s, merge gap s, mean F1), all at threshold 99.9 and bin 1 s: (240, 8, 0.735),
(240, 4, 0.725), **(120, 8, 0.724)**, **(60, 8, 0.722)**, (240, 2, 0.720).

## 4. What to evaluate, in order

1. **Reproduce, don't trust.** On `full-search`: `pytest tests/test_sliding_window.py
   tests/test_loco_detect.py tests/test_coact_detect.py tests/test_search_all_settings.py`, then
   `python tools/probe_sliding_vs_binned.py`. Both should match §1.
2. **Settings for sliding LoCo and CoactDetect that do not lean on a long context.** Every 240 s
   winner *loses* on the crowded recordings — it is fitting the ordinary bench's 120 s spacing of
   planted events. Candidates to score held-out and crowded before choosing:
   - LoCo: threshold 99.9, context **120** or 60 s, merge gap 8 s (admissible in the full grid).
   - CoactDetect: alpha 1e-5 at context **60** s — not yet measured; check it clears the
     empty-recording limit.
   Whatever is chosen must pass all three budgets and not lose on the crowded recordings.
3. **Sliding vs binned on real recordings.** Not yet done: run both modes over the export's
   baseline windows (`dataset.current("steps_excluded")`) and report, per recording, calls in
   each mode and how many coincide. There is no answer key; a large disagreement is a finding to
   explain before shipping.
4. **locust's 128-frame minimum distance.** The strongest result of the search — it gains on
   held-out *and* crowded recordings, so it is not the spacing artifact. Two cautions: the
   setting is in **frames** (12.8 s at 10 Hz; different elsewhere), and it suppresses a second
   call within 12.8 s of a first, which real bursts may contain. Check on real calls before
   proposing it.
5. **Then land**, after coordinating with the other session: set the chosen values in
   `OPERATING_POINTS` on `sliding-loco-coact`, update their `source` strings, green CI, merge.
   The browser `loco.js` / `coact.js` port is still owed after that.

## 5. Traps already paid for this week

- **Budgets that live only in a test cannot stop a calibration.** Three were moved into
  `bench.py` in one day (`MAX_FALSE_POSITIVES_PER_HOUR`, `MAX_PRECISION_DROP`, after
  `MAX_PROBE_PER_MIN` in August), each found by a search proposing something it would have
  refused. Look for a fourth before trusting a new search.
- **Quote held-out gains**, never the "chosen on" column.
- **Window-shaped settings** (context, integration, bin width, minimum distance) are the ones the
  bench can flatter. The crowded column exists for them.
- `detect_folder.ONSET_FIELD` and the locust anchor question are separate and still open
  (`docs/todo/2026-09-16-locust-anchor-and-the-panel-viewer.md`).

## 6. Related, not this handoff's job

- **The detector review document** (branch `detector-review-doc`, PR #587) was to be finalized
  2026-09-17; its numbers predate the sliding change, the 2026-09-16 retune, and locust's widths.
  Another session committed there on 2026-09-16 — check the board first.
- **Decisions still Tony's:** binned SCE 98 vs 75
  (`docs/todo/2026-09-16-binned-sce-trades-false-alarms-for-f1.md`); rate+context's 4.5 Hz gain
  being quiet-background only.

**When this is spent:** delete it once §4 is done and landed, or move it to `docs/handoffs/` if
anything in §4–§6 is still open.
