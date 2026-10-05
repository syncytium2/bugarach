GRANT 6 ok — Read, Grep, Glob, Bash, WebSearch, WebFetch

**Role 6 (methods / RTFM), blind round 3: `<worktree>/docs/learned/runs/2026-09-25-final-parameters/README.md` @ 0638de5**

I found 2 major problems that change what Tony would decide, 2 more major ones about how a result is described, and 4 minor ones. I edited nothing.

**What I did before reviewing:**
- Read the code the page rests on:
  - `src/bugarach/detectors/coact.py` (both the binned and the sliding path)
  - `src/bugarach/detectors/sync.py`
  - `src/bugarach/event_floor.py` and `src/bugarach/score.py`
  - the floor and gate code in `bench.py`, and the operating points in `bench_combined.py` and `bench_slow.py`
  - the held-out stage and bootstrap of `tools/search_all_settings.py`, and `proposal()` in `tools/score_bench_candidates.py`
  - `tools/final_parameters_review_checks.py`, and the Figure 2 code in `tools/make_final_parameters_report.py`
- Checked that PySpike's SPIKE-synchronization takes a `max_tau` cap: its source says "Maximum coincidence window size". I did not re-read the Kreuz 2015 paper itself, so the "core SPIKE-synch" wording is checked against the code and PySpike, not the paper.
- Re-ran parts of the analysis at the shipped settings on the page's own seeds. Every baseline I re-ran matched the page's numbers (0.761, 0.782, 0.788, 0.764, 0.845), so the reruns use the same scoring as the page.

## Findings

**1. Decision 1, the combined SPIKE-synch row and the "may it still be called SPIKE-synch?" question. MAJOR. Verified: yes (rerun).**
- **Issue:** the change to a fixed coincidence window adds nothing. The whole gain comes from `C_threshold` 0.08 → 0.1. I scored the combined bench with each change on its own (mean F1 over quiet and busy):

  | seeds | shipped | `C_threshold` 0.1 only | the proposal (0.1 + fixed window) |
  |---|---|---|---|
  | fresh, 6000–6023 | 0.7606 | **0.7860** | 0.7818 |
  | selection, 1–48 | 0.7607 | 0.7873 | 0.7898 |
  | held-out, 49–96 | 0.7542 | 0.7826 | 0.7834 |

  - On the fresh seeds the fixed window costs 0.004. On the other two sets it adds +0.0025 and +0.0008, which is noise.
  - The reason: at tau_max = 0.25 s and bench event rates, the cap binds almost everywhere. With the shipped ISI-adaptive window, only 39 of 5,479 coincidence values (0.7%) on quiet differ from the fixed-window values, and 1,163 of 19,380 (6%) on busy.
- **Fix:** tell Tony the ruling can be avoided. `C_threshold` 0.1 with the ISI-adaptive window keeps the whole gain and keeps the name and the methods citation. Offer that variant after its own paired fresh-seed interval and a bracketing check. Neither was run; I only have point estimates.

**2. Decision 1, "Combined SPIKE-synch's proposal changes what the detector is … it depends on event rate again". MAJOR (only a framing problem). Verified: yes (code plus the counts in finding 1).**
- **Issue:** the sentence implies the shipped window is free of event rate. It is not, at these rates. The shipped ISI-adaptive window is already capped at tau_max. On the bench it equals the fixed ±0.25 s window for more than 99% of onsets on quiet and 94% on busy, so the shipped detector is itself almost fixed-window coincidence counting.
- **Fix:** add one sentence: "At tau_max 0.25 s and these event rates the cap binds for over 94% of onsets, so the two modes differ only in dense stretches."

**3. Decision 1, "What the gain is made of: mostly fewer calls on decoys … the gain comes from rejecting decoys". MAJOR. Verified: yes (Table 1's own numbers).**
- **Issue:** for two of the four proposals, the table contradicts the claim. If fewer decoy calls made the gain, F1 without decoy calls would gain less than F1 as scored. It gains more:
  - combined rate+context: +0.123 without decoy calls (0.855 → 0.978), against +0.090 as scored;
  - combined SPIKE-synch: +0.029 (0.949 → 0.978), against +0.021 as scored.
- The same line says F1 without decoy calls is "near 1 … for the shipped points too", but shipped combined rate+context is 0.855.
- **Fix:** split the claim by proposal. Rate+context's and SPIKE-synch's gains come mostly from calls that are not on decoys. Only the two binned SCE rows are partly explained by decoys.

**4. Decision 2 (and Figure 2's star), "In 13 of those the intervals overlap … One does not overlap". MAJOR. Verified: yes (rerun).**
- **Issue:** comparing two versions scored on the same recordings needs a paired test. Whether two separate intervals overlap is the wrong test, and it is far too lenient. The figure code stars a cell only when `ci[i,j,0] > ci[j,j,1]` (`tools/make_final_parameters_report.py`, lines 347–350).
- I re-ran the one comparison that bears on Decision 1, fast's binned SCE proposal against combined's own proposal on the combined bench, fresh seeds, with 2,000 paired resamples. The paired difference is **+0.024 [+0.005, +0.044]**, which excludes zero. So "at least as good" understates it: fast's version is better on combined under the right test. Some of the other 12 "overlapping" cells may also turn out to differ.
- **Fix:** replace the overlap criterion with a paired interval on the difference, in the text and for the star. Keep the note that some wins among 48 comparisons are expected by chance.

**5. Decision 5 and Table 1, slow SPIKE-synch `dt` 0.1 → 0.00625 s. MINOR. Verified: yes (rerun).**
- **Issue:** the bench's onsets sit on a 0.1 s frame grid. Any `dt` of 0.05 s or less puts each frame's onsets in a separate bin. Fresh-seed mean F1 is identical, 0.8447, at `dt` 0.05, 0.025, 0.0125 and 0.00625; it is 0.815 at 0.1.
  - So the three extensions below 0.05 walked a flat stretch, and 0.00625 is an arbitrary point on it.
  - The detector's own docstring (`PROFILE_BIN_SEC` in `sync.py`) warns that a bin finer than the frame interval buys nothing real.
  - What changes the result is dropping below the frame interval. That ends the bin-overwrite quirk, so the floor-set `min_n` then counts every onset.
- **Fix:** state the change as "`dt` ≤ half the frame interval (0.05 s); the same from 0.05 down". Report that it moves what `min_n` counts, and do not present 0.00625 as a tuned value.

**6. Decision 7, alpha read as a z-cutoff. MINOR. Verified: yes.**
- The claims are correct:
  - the p-value is one-sided, `0.5*erfc(z/√2)`, on both paths in `coact.py`;
  - 1e-4 → z = 3.72 and 1.4e-9 → z = 5.94;
  - the exact binomial tail is far larger than the nominal one. For example, at the busy combined rate with a 3 s window, 1.4e-9 nominal is 7.6e-7 exact; on quiet, 1.4e-9 nominal is 5e-5 exact.
- **Suggested addition:** give the cutoff in ROIs as well. At 1.4e-9 with a 3 s window it means at least 6 ROIs on quiet and 13 on busy. The quiet figure sits at or below the combined quiet floor (6–7 ROIs), so on quiet the floor, not alpha, is what binds. That makes "stop at a stated z-cutoff" something Tony can decide on concretely.

**7. Definitions, "F1" and Figure 1 "F1 is the mean over the quiet and busy backgrounds". MINOR. Verified: yes (code).**
- **Issue 1:** F1 is pooled over the 24 recordings within each background, then averaged across the two backgrounds. It is not a mean of per-recording F1s. The text does not say so.
- **Issue 2:** matching is one-to-one, closest pair first, so a second call on the same event counts as a false alarm. This matters for reading the gains: two of the four proposals lengthen a merge gap (fast binned SCE 10 s, rate+context 16 s), and part of what they gain may be fewer split calls.
- **Fix:** add "pooled over recordings" and "one call per planted event; extra calls on the same event count as false alarms".

**8. "The full tables", Held-out gain. MINOR. Verified: yes (code).**
- **Issue:** the held-out interval is paired: `search_all_settings.held_out` uses the same resample index for shipped and candidate. Its resampling is not split by background, while the fresh check's is. Both are valid. But the page presents "paired" as what sets the fresh check apart, which suggests the held-out interval is not paired.
- **Fix:** say "paired, 400 resamples" in "How to read them".

## Checked and correct (no finding)
- **Event floor** (definition and methods caveat): max(3, the smallest count whose null calls come to at most 1 per hour); per-ROI rigid shift uniform in ±20 s; 1,000 draws; 2 s sliding window; the null is read on the window trimmed by *J* at each end; the stability check compares the two halves with the full-draw chance floor. The direction of the window-width caveat is right: chance co-activity is higher for wider windows and lower for LoCo's.
- **Which settings the floor sets:** `FLOORED_SETTING` covers CoactDetect, LoCo, binned SCE and SPIKE-synch (`min_n`). Rate+context and locust have none, as the page says.
- **Under-floor events:** they are "don't care", and a call matched to one leaves precision. A call on a decoy still counts as a false alarm. Fast decoys have 6 participants (round(0.18 × 32 ROIs) = 6).
- **The precision-swing gate** takes the absolute swing (`search_all_settings.py`, line 413), as the page says.
- **The held-out gain is biased upward:** confirmed. `proposal()` takes the highest held-out F1 among candidates whose lower bound is above zero.
- **The paired fresh-seed gain:** same resample index for both versions, split by background, 2,000 resamples.
- **`C_min` = 0 as a hard limit:** confirmed. The test is a strict `>` on values that are never negative.
- **The 2.5 s match to the call's span:** `TOL_SEC = 2.5`, gap measured to the span.

## Files
- `<worktree>/docs/learned/runs/2026-09-25-final-parameters/README.md`
- `<worktree>/src/bugarach/detectors/sync.py` (lines 176–215: in "fixed" mode tau is the cap for every onset)
- `<worktree>/src/bugarach/detectors/coact.py` (lines 13, 158, 363)
- `<worktree>/tools/make_final_parameters_report.py` (lines 347–350: the overlap star)
- `<worktree>/tools/search_all_settings.py` (lines 413 and 696–760)
- `<worktree>/tools/final_parameters_review_checks.py`
- `<worktree>/src/bugarach/bench_combined.py` (line 223) and `<worktree>/src/bugarach/bench_slow.py` (line 275): the shipped SPIKE-synch points

The reruns were one-off `python -c` commands; no scripts or outputs were saved.
