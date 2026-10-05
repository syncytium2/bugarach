GRANT 1 ok — Read, Grep, Glob, Bash

(SubagentHandback is the hand-off channel, not an editing tool. I have no Edit, Write or NotebookEdit.)

# Role 1, Prove It: blind round 3 on `<worktree>/docs/learned/runs/2026-09-25-final-parameters/README.md` (run/final-parameters @ 0638de5)

Almost every number in the report recomputes exactly from the darkroom records. The main problems are two explanatory claims in Decision 1 that the report's own tables contradict (F1 is the harmonic mean of recall and precision; a decoy is a planted burst labelled as not an event).

## Findings

**F1: the claim that the gain is mostly fewer calls on decoys is refuted by the report's own numbers (major)**
- **Location:** Decision 1, the "What the gain is made of" bullets.
- **Issue:** Two claims fail:
  - "F1 without decoy calls is near 1 … for the shipped points too" is false. Combined rate+context shipped scores 0.855 (Table 1 and `cross_stream.json`).
  - "So the gain comes from rejecting decoys" is also false. If that were true, the gain in F1 without decoys would be about zero. It is not:

| proposal | F1 gain without decoys | F1 gain as scored |
|---|---|---|
| fast binned SCE | +0.028 | +0.038 |
| combined binned SCE | +0.010 | +0.017 |
| combined rate+context | +0.123 | +0.090 |
| combined SPIKE-synch | +0.029 | +0.021 |

  - Decoy calls (quiet + busy) barely move: combined rate+context 125+126 → 115+114, SPIKE-synch 121+98 → 118+94, combined binned SCE 131+106 → 131+89.
  - What moves is precision without decoys on the busy background: rate+context 0.551 → 0.916, SPIKE-synch 0.830 → 0.967, combined binned SCE 0.886 → 0.956, fast binned SCE 0.877 → 1.000. So the proposals mostly cut false alarms on non-decoy background, not decoy calls.
- **Fix:** Rewrite the bullet from these numbers. The gain is fewer false alarms on the busy background, outside the decoys.
- **Verified against a source:** yes. `064/phase3/candidates.json` and `065/phase3/candidates.json` results (`precision_without_decoys`, `decoy_calls`), and `064/phase3-3x3/cross_stream.json`.

**F2: the claim that the floor blocks nearly every binned SCE call in the stretch is refuted (major)**
- **Location:** Decision 1, "Some budget checks cannot fail here".
- **Issue:** The report says that for binned SCE and SPIKE-synch the floor "blocks nearly every call in the stretch by construction", so a pass there "is no evidence for those two". That holds for combined SPIKE-synch (0.2 calls/min) but not for binned SCE:
  - Combined binned SCE, shipped and proposal, makes 5.70 calls/min in the stretch on every seed set: selection 5.696/5.742, held-out 343.25/h = 5.72, fresh 5.700/5.750. Its limit is 10.
  - Fast binned SCE shipped makes 5.6 calls/min. Slow binned SCE makes 1–4.5.
  - Figure 3's top row shows the same.
  - `bench.py`'s own note on the SCE operating point says "about 5.7 firings/min at every threshold".
  - Only the fast binned SCE proposal (about 0.017/min) behaves as described.
  - The claim traces to the `ELEVATED_RATE_RECORDING` docstring ("calls little there by construction"), which these data refute for SCE.
- **Fix:** Limit the claim to SPIKE-synch. Say instead that combined binned SCE is genuinely tested there and passes at 5.7 against 10 calls/min.
- **Verified against a source:** yes. `selection_budgets.json`, candidates `search_row.probe_*_per_hour`, fresh `probe_calls_per_min`.

**F3: the floor-stability sentence is unsourced, and "seeds 1–96 were not checked" is inaccurate (minor)**
- **Location:** The full tables, "Methods caveats", floor stability.
- **Issue:** Two problems:
  - "On the 144 fresh-seed recordings … match the full floor on 142. The two exceptions are on slow, off by 1 ROI." I found no record holding this. Nothing under `064/phase3`, `065/phase3`, `report-inputs`, or the generator and review-check tools carries per-recording half-draw floors for fresh seeds. I could not verify it.
  - `065/bench-floor/bench_floor.json`, the record behind Figure 4, did check stability on seeds 1–8: 114 of 120 floors stable. All 48 planted-recording floors were stable. The 6 unstable ones are 4 elevated-rate and 2 no-coordination floors, and 4 of the 6 are on fast or combined, not slow.
- **Fix:** Cite the source of the 142/144 figure or drop it. Report the seeds 1–8 check as it stands.
- **Verified against a source:** partly. The 114/120 figure is verified; the 142/144 figure is not verifiable.

**F4: the slow locust old-layout rates have no source (minor)**
- **Location:** Decision 3, Reason 2: "Shipped slow locust made 1.83 calls per minute in the old layout (seeds 1–8, quiet) and 5.00 in the new one."
- **Issue:** Neither number appears in any named record (bench_floor.json, the candidates files, selection_budgets.json, the RUN files), in ADR-0008/0009, or in `bench*.py`. The only hit for "1.83" is the report itself. This is the key evidence that the layout, not the floor, causes the failure.
- **Fix:** Name the run and record that measured both, or mark the figures as unverified.
- **Verified against a source:** no (unverifiable).

**F5: rounding mismatch in a paired fresh-seed interval (minor)**
- **Location:** Decision 1 table, combined SPIKE-synch paired fresh-seed gain upper bound.
- **Issue:** The report prints +0.041. `review_checks.json` holds 0.040499, which rounds to +0.040.
- **Fix:** Print +0.040.
- **Verified against a source:** yes.

**F6: the LoCo context values are in the wrong order (minor)**
- **Location:** Decision 8: "The search did go below on fast and combined LoCo, to 10 s and 5 s."
- **Issue:** It is the other way round. Fast LoCo moved to 5 s in round 1, and its grid reached 2.5 s. Combined LoCo's pair best is 10 s.
- **Fix:** Write "to 5 s (fast) and 10 s (combined)".
- **Verified against a source:** yes. Both LoCo `search.json` histories and grids.

**F7: the "cap" label is spurious for slow LoCo too, but only fast is explained (minor)**
- **Location:** Table 1, slow LoCo, "threshold_pctile (cap)".
- **Issue:** Decision 8 explains that fast LoCo's "cap" is an artefact. `bracketing()` counts extensions per axis, not per side, so six downward extensions label the untouched upper end "cap". Slow LoCo has exactly the same pattern: six downward extensions to the 1st percentile, sitting at the top value 99.995, labelled "cap". The report doesn't mention it.
- **Fix:** Apply the same caveat to slow LoCo.
- **Verified against a source:** yes. `search_all_settings.py` `bracketing()` and slow LoCo `search.json`.

**F8: "the proposals call far fewer" overstates the middle level (minor)**
- **Location:** Decision 1, the under-floor bullet.
- **Issue:** On the busy background's middle level, rate+context goes 55 → 54 and SPIKE-synch 42 → 41. That is essentially unchanged. "Far fewer" holds only at the lowest level.
- **Fix:** Qualify the sentence by level.
- **Verified against a source:** yes. `under_floor.calls_on_under_floor`.

**F9: the shipped-point-at-a-limit note is incomplete (minor)**
- **Location:** Decision 5: "On fast and slow, locust's shipped point already sits at 1 frame."
- **Issue:** Slow SPIKE-synch's shipped point already sits at `C_min` = 0.0 (`bench_slow.py`, adopted 2026-09-21 on that plateau). Slow rate+context's shipped guard is also 0. So the same "shipped would fail the same test" point applies to them too.
- **Fix:** Extend the sentence to cover them.
- **Verified against a source:** yes.

## Claim ledger (all match unless noted)
- **Decision 1 table:**
  - Held-out gains (search_row `gain_vs_shipped`) match for all 4.
  - Paired fresh-seed gains match, except F5.
  - Fresh F1 shipped → proposal matches for all 4.
  - The 2,000 paired resamples and seeds 6000–6023 match.
- **Under-floor call table:** all 12 cells match (22→5, 23→6, 60→49/85, 36→24, 19→12, 39→33/55, 34→2, 41→11, 55→54, 6→5, 41→20, 42→41).
- **Other Decision 1 figures:**
  - Combined SPIKE-synch makes 0.2 calls/min in the stretch on selection, held-out and fresh seeds, shipped and proposal.
  - Combined rate+context outside the stretch on busy: 1.28 calls/h held-out and 1.38 fresh, against a limit of 1.
  - Combined binned SCE's runner-up led on the selection seeds by 0.0003 (0.75193 vs 0.75162).
  - The proposal rule matches `score_bench_candidates.proposal()` (interval lower bound > 0, best held-out F1).
- **Decision 2:** recomputed from `cross_stream.json`:
  - 14 of 48 off-diagonal cells score higher, and 13 of those have overlapping intervals.
  - Rate+context on slow: 0.865 [0.855, 0.874] vs 0.834 [0.825, 0.843].
  - Binned SCE on combined: 0.788 [0.774, 0.802] vs 0.764 [0.748, 0.781].
  - 38 versions reproduce exactly, and the chosen chorus seeds match.
- **Decision 3 table:**
  - Swings: 0.181/0.148, 0.181/0.175, 0.245/0.257.
  - Slow locust in the stretch: 7.24 · 6.85 (411.25/h) · 7.23, and 4.35 busy. Limits 0.10, 0.10, 0.15 and 4.0.
  - Fast SPIKE-synch decoy calls 84/23, precision without decoys 1.000/1.000.
  - Fast rate+context precision without decoys 0.992/0.764.
  - Decoys at 6 participants (0.18 × 32 ROIs).
  - Floors 5–6 quiet and 6–8 busy.
- **Figure 3 text:**
  - A 2700 s (45 min) recording with the stretch at 1200–1500 s. Not noted in the report: the stretch has 30 s ramps.
  - Rates 0.1334, 0.0321 and 0.1529 Hz.
  - Seeds 66000–66011.
- **Decision 4 and Table 3:**
  - All floor ranges and under-floor counts match.
  - Fast busy loses 205/360 = 56.9%.
  - ADR-0009's "a third to a half" matches.
  - Figure 4's 25/40, 20/40 and 15/40 match.
  - Elevated-rate floors are 16–18 on fast and 18–20 on combined, which supports "16–20".
  - The planted-minus-null floor offset is about 1.1 on fast and combined and 2.5 on slow.
- **Decision 5:** the five held-out gains and the `C_min` plateau from 0 to 0.03 on seeds 1–48 (`bench_slow.py`) match.
- **Decision 6:**
  - Close-events loss 0.0207 held-out and 0.0198 on the selection seeds.
  - 12 recordings per background.
  - The "unsigned" wording is in `bench_slow.py`.
- **Decision 7:**
  - `alpha` alone gains +0.031 on fast and +0.013 on combined.
  - The z-cutoffs are 3.72 and 5.95. The report's "about 5.9" is fine; 5.95 rounds to 6.0.
  - The p-value is a one-sided normal tail (`coact.py`).
  - Held-out gains match. The 240 s context was in combined's grid.
  - The loss against binned shipped is 0.0165 on seeds 49–60.
  - The search's verdict is −0.044.
- **Decisions 8 and 9:**
  - ADR-0009 decision 5's context grid matches.
  - Every LoCo grid was extended down to the 1st percentile.
  - Combined LoCo's held-out gain is exactly 0.
  - Fast LoCo moved to a 5 s context in round 1, and its guard grid is 0.5–4 s.
  - Slow and combined LoCo held the context at 120 s in their rounds.
- **Table 1:** all 24 fresh F1 values with intervals, F1 without decoys, settings changes and bracketing reasons match. Fast ships CoactDetect and LoCo binned (`bench.py`), and slow and combined ship them sliding.
- **Tables 1–3 against `adoption_table.md`:** the generated blocks in the README match `adoption_table.md`. Figures 3–4 are byte-identical to `065/report-inputs`, and the darkroom `report/README.md` is identical to the repo copy.
- **Real data:**
  - 66 recordings, 128 treatment windows, 3,072 combinations, 2,696 with different floors and 498 flips.
  - Senktide medians on fast: +1, +17, +1, +20.
  - `879be03` is #814's head, merged as 3153b9b with an identical tree. The 4 locust-only differences from v2 match.
- **Definitions and What ran:**
  - Matching tolerance 2.5 s (`score.TOL_SEC`).
  - Floor null: J = 20 s, 1000 draws, 2 s window, minimum 3, 1 false alarm per hour.
  - Held-out interval: 400 resamples, bootstrap median.
  - Commits b6e40f0, a70b185, 7af68c9 and 723f1e6 match the RUN files.
  - The DIAGNOSIS file exists and supports "nothing it was allowed to move to".

## Record of design and unit membership
- I located the record: `<worktree>/current_export.toml` [senktide_ttx]. It lists 66 recordings, notes that withdrawn and contaminated recordings (steps and pins) were removed by the producer, and carries no open contamination note.
- The real-data run is stamped with this dataset and 66 recordings. The count reconciles and there are no withdrawn units.
- Group medians are descriptive and computed over windows. No inference treats windows from the same recording as independent.
- The bench sections are simulated, so no membership question applies.

## What I did not check
- Visual properties of Figures 1, 2 and 4 (role 10's job).
- That combined LoCo made identical calls, since only the zero gain and equal F1 are recorded.
- The claim that `alpha` "gained F1 at each step": the history records only one jump to the capped value.
