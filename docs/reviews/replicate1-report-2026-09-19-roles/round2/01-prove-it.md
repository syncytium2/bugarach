GRANT 1 ok — Read, Grep, Glob, Bash

# Role 1 (Prove It): claim and data verification of `replicate1/report.html`

**Result:** 2 high, 7 medium and 10 low findings. The core results tables and the headline numbers recompute exactly. The errors sit in two places: Figure 1's caption, and the "where the gap is" argument (section 9 and Figure 9). Both rest on a score field (`distractor_hits`) that does not measure what the page says it measures.

**Method.** I recomputed every number from the two runs' own files, independently of the generator:
- `results.json`, `meta.json` and `selections/` for both draws.
- Every `.run.json` in the fits archives: 1,938 in the first draw, 1,943 in the second.
- Every score file: 3,720 in the second draw, plus the first draw's.

I also re-ran CoactDetect on the Figure 1 recording. The generator's worktree has the same `bench.py`, `simulate.py`, `score.py` and detector code as `weekend-runs` (checked with `diff`). I held no Write tool, so all recomputation ran as inline `python -c`; no file was edited. Intermediate files are in `...\scratchpad\mb2\role01\` (`stripped.html`, `text.txt`, `handoff_ws.md`, `handoff_slow.md`, `goal1.md`, `goals.md`).

## Findings
Columns: location · issue · severity · suggested fix · verified against a source

1. **Figure 1 caption: "6 of its 6 unmatched calls fell on distractors."**
   - **Issue:** Recomputed as **4 of 6**. I re-ran `run_detector("coact", …)` at the reference settings on `baseline_quiet` seed 2000: 20 calls, 14 hits, 6 false alarms. The false alarms at 206, 340.6, 479.5 and 975.3 s overlap a distractor. The ones at 1090.5 s and 2213.6 s are 115 s and 1238 s from the nearest distractor.
   - **Why the page got it wrong:** it read `distractor_hits = 6`. In `score.py` (lines 104–105 and 267–271) that field counts *distractors touched by any call*, including calls that matched a planted event. It does not count unmatched calls.
   - **Severity:** high.
   - **Fix:** "4 of its 6 unmatched calls fell on distractors", computed from `fa_times`/`fa_ends` rather than `distractor_hits`.
   - **Verified:** yes.

2. **Figure 9 and section 9 ("Where the gap is"): the three-way split of false alarms.**
   - **Issue:** "Anywhere else" is computed as `n_fa − hot_fa − distractor_hits`. Because `distractor_hits` counts distractors touched (at most 6 per recording, hit calls included), this is not a partition, and it goes negative:

     | entry | "anywhere else", first draw | second draw |
     |---|---|---|
     | LoCo, under the budget | −0.70 | −0.67 |
     | binned SCE, under the budget | — | −0.83 |
     | rate+context, under the budget | −0.20 | −0.14 |
     | SPIKE-synch, under the budget | −0.09 | −0.06 |

     `fig_split` draws `max(0, wv)`, so LoCo's negative segment is silently dropped and its bar is longer than its real false-alarm count. CoactDetect's red segment (0.57 and 0.24) comes from the same subtraction.
   - **"About as often on distractors"** compares a saturated count: 5.0–5.8 against CoactDetect's 5.8, out of a maximum of 6.
   - **What survives:** the best net has more false alarms outside the dense stretch than CoactDetect.
     - Draw 1: 9.10 against 6.41 per recording.
     - Draw 2: 7.56 against 6.03.
     - But "on a distractor" versus "anywhere else" cannot be separated with the fields in the score files.
   - **Severity:** high.
   - **Fix:** either re-score per unmatched call (whether each `fa_times` span lies within tolerance of a distractor), or show two categories (dense stretch / outside it) and drop the distractor clause. The build's asserts at `make_replicate_report.py` lines 836–843 use the same flawed `other()`.
   - **Verified:** yes.

3. **Section 9: "the nets call less in the dense stretch and about as often on distractors, but far more often anywhere else."**
   - **Issue:** False for tube on all three parts. Per recording, first draw / second draw:

     | | dense stretch | on distractors | anywhere else |
     |---|---|---|---|
     | tube | 1.70 / 1.34 | 3.84 / 3.70 | 0.57 / 0.43 |
     | CoactDetect | 0.88 / 0.75 | 5.84 / 5.79 | 0.57 / 0.24 |

     The build asserts this only for chorus_gain_norm.
   - **Severity:** medium.
   - **Fix:** "the best net (chorus_gain_norm) …", or name tube as the exception.
   - **Verified:** yes.

4. **Section 10: "the coded detectors tune their merge (up to 8–30 s)".**
   - **Issue:** Wrong for two of six detectors. The grid tops in `selections/*/rate|sync|cicada.json` are:
     - locust `sce_min_distance_frames`: 16 frames, which is 1.6 s at the bench's 0.1 s frame.
     - SPIKE-synch `max_gap`: 2.0 s.

     For those two, the coded "merge" is at or below the nets' fixed 2 s (all 1,943 checkpoints have `merge_gap_frames = 20`). The asymmetry in summary bullet 4 ("each hand-written detector tuned its own merge") is correct, but the implied "longer merge" holds for only four detectors.
   - **Severity:** medium.
   - **Fix:** "up to 1.6–30 s (8–30 s for rate+context, CoactDetect, LoCo and binned SCE)".
   - **Verified:** yes.

5. **Summary bullet 1 and section 9: "the same learned model moved …" and "It is a lower bound, since the configurations … were held fixed".**
   - **Issue:** Only the candidate set is fixed. Every tuned net entry chose different configurations in the two draws. Example: tube under the budget chose `60fb765e…` in all four first-draw folds, and `38b0e61e…`, `5b53b48b…` and `725a6956…` in the second. So 5 of the 8 unflagged net entries are not "the same model". A median of |moves| over 8 entries is an estimate, not a bound.
   - **Severity:** medium.
   - **Fix:** "the same entry (net and selection rule)"; say "probably an underestimate" instead of "lower bound"; or restrict the statistic to untuned entries.
   - **Verified:** yes.

6. **Section 9: "The nets moved more, and mostly in the same direction, which is a shift of the whole draw rather than independent noise."**
   - **Issue:** The page's own numbers contradict "shift of the whole draw". The unflagged nets moved up in 7 of 8 entries. The unflagged coded detectors moved **down** in 7 of 9 (for example SCE −0.023, SPIKE-synch −0.011 and −0.013, rate+context −0.010). A whole-draw shift would move both sides the same way; this is the nets gaining relative to the coded side.
   - **Severity:** medium.
   - **Fix:** rephrase, for example "the nets rose and the coded detectors fell, so the draws differ in a way that favours the nets slightly".
   - **Verified:** yes.

7. **Summary bullet 3: "Chosen on F1 alone, the best learned model also trailed in both (−0.007 and −0.029)."**
   - **Issue:** The −0.029 comes from a † entry. chorus_gain_norm's second-draw mean includes a collapsed refit (fold 3: −0.114 against CoactDetect). chorus_norm tuned on F1 alone beat CoactDetect in 3 of 4 second-draw folds (+0.003, +0.003, +0.007); its mean (0.690) is pulled down by the fold-1 collapse. The bullet does not show the flag.
   - **Severity:** medium.
   - **Fix:** mark it "(both flagged †, section 8)" and give the best unflagged comparison (line_length, −0.039).
   - **Verified:** yes.

8. **Section 3: "line_length votes once per cell".**
   - **Issue:** This repeats a claim the code has withdrawn. `learn/nets/line.py`, which `line_length.py` builds, says: "That bounds the vote's height, not its time integral, and this docstring used to say it bounded both". A reviewer measured a four-onset burst delivering 1.7–2.7x the integrated vote. The page's contrast with tube ("where a bursting cell counts more than once") therefore does not hold.
   - **Severity:** medium.
   - **Fix:** "line_length's vote is bounded in height per cell, though a burst still counts for longer".
   - **Verified:** yes.

9. **Section 6 and "Why this report exists": the rehearsal margins +0.011 and +0.016.**
   - **Issue:** The numbers match the rehearsal's `results.json` (identical to the `--rehearsal` file). But the cited README says "nothing should quote it as a comparison". It also says the rehearsal's CoactDetect choices sat at a 240 s context, which contaminates its own null. The page cites the README and then quotes the numbers anyway. (The goals page also quotes +0.011.)
   - **Severity:** medium.
   - **Fix:** drop the numbers, or state that the README forbids quoting them and why the page does anyway.
   - **Verified:** yes.

10. **Section 4: "(50–55 refits per net)".**
    - **Issue:** True for the second draw only. The first draw has chorus_norm 40, chorus_gain_norm 60, and line_length and tube 55, so 40–60.
    - **Severity:** low.
    - **Fix:** "50–55 in the second draw, 40–60 in the first".
    - **Verified:** yes.

11. **Figure 2 caption: the drawings are said to be in `<darkroom>/bugarach/2026-09-19-comparison-architectures/`.**
    - **Issue:** That folder does not exist at review time.
    - **Severity:** low.
    - **Fix:** say "will be in", or point at the branch doing the drawing (a branch `origin/draw-the-comparison-four` exists; I did not check its contents).
    - **Verified:** yes.

12. **Section 11: "The chorus models load only from branch replicate-run or tune-bench-comparison".**
    - **Issue:** `chorus_gain_norm.py` is also on `origin/draw-the-comparison-four`, `eval-field-size-candidates`, `tune-learned-vs-coact` and `tune-wider-reference-grid`.
    - **Severity:** low.
    - **Fix:** "not on main; for example …".
    - **Verified:** yes.

13. **Section 3: "Kreuz and colleagues' SPIKE-synchronization measure (2015)" and "designed here and independently resemble radar CFAR".**
    - **Issue:** The cited `docs/detector_history.md` does not contain 2015. It cites Cecchini 2021, and Kreuz 2022 was withdrawn as a citation. The year is likely right from outside sources, but it does not come from the cited file. The same file says the claim of independent design "rests on the author's recollection".
    - **Severity:** low.
    - **Fix:** cite the 2015 paper directly, and soften "independently".
    - **Verified:** partly.

14. **Section 3: "chorus_norm and chorus_gain_norm … differ only in whether the vote's steepness is fitted".**
    - **Issue:** chorus_gain_norm also fits the vote's bias (midpoint). The 8 extra parameters (1,905 − 1,897) are 4 gains plus 4 biases (`chorus.py` lines 93–110). `vote_gain` is also a tuned axis.
    - **Severity:** low.
    - **Fix:** "steepness and midpoint".
    - **Verified:** yes.

15. **Section 3: "locust … against a per-cell circular-shift threshold".**
    - **Issue:** `cicada.py` step 3 builds one absolute cell-count threshold from a null in which each cell is shifted separately. It is not a per-cell threshold.
    - **Severity:** low.
    - **Fix:** "against a cell-count threshold from circularly shifted copies".
    - **Verified:** yes.

16. **Section 5: "Binned SCE fires 4–33 times per hour on the busy empty recording … and passes".**
    - **Issue:** The low end (3.9) is second-draw fold 2, the ‡ fold where the budgeted search found nothing admissible. The folds that passed run 21–33.
    - **Severity:** low.
    - **Fix:** use "21–33".
    - **Verified:** yes.

17. **Section 6: "their code differs only in the option that sets the replicate".**
    - **Issue:** The only tool change between the fold-fix commit `e8764aa` and the replicate commit `7a95e8a` is the replicate option (plus tests and a handoff), which is consistent. But neither `meta.json` nor `run.log` records the commit WSMIP064 ran.
    - **Severity:** low.
    - **Fix:** name both commits, or say "by the branch history".
    - **Verified:** no (not from the runs' own files).

18. **Section 10: "It does not make the results wrong".**
    - **Issue:** This is backed by `HANDOFF-workstation-tuning.md` ("Consequences for goal 2: none"; the constants are unchanged to four decimals). But `HANDOFF-slow-comodulation…` item 3 records that "'small' is the argument we agreed not to accept alone", and the bench pointer is still undecided.
    - **Severity:** low.
    - **Fix:** state the measurement ("the eight constants re-measured on the corrected export are unchanged to four decimals") rather than the conclusion.
    - **Verified:** yes.

19. **Section 8 and Figure 7: "failed to train" and "The net's output sat near a constant".**
    - **Issue:** "Failed to train" is inferred from F1 ≈ 0.125 (`tune_learned_vs_coact.py` line 1581), not from a training diagnostic, and "near a constant" is not measured. The score file does show what the page describes: one call per recording at threshold index 0, and none at index 30.
    - **Severity:** low.
    - **Fix:** "made one call per recording", which is what was measured.
    - **Verified:** partly.

## Claim ledger (quoted · source · recomputed · verdict)
"a" is the first draw (WSMIP064, seeds 1000–1047); "b" is the second (WSMIP065, seeds 2000–2047).

**Tables 1–4**
- **Tables 1–2** (all 50 cells): `results.json` `f1_mean`/`f1`, averaged over 4 folds. Every cell matches to 3 decimals.
- **† and ‡ placement:** per-seed `failed_training_signature`/`f1_was_nan`, and `n_refused == n_scored` in the selections. All match: chorus_norm b F1-alone and budgeted; chorus_gain_norm a and b F1-alone; tube a budgeted; locust ‡ in all 8 folds; SCE ‡ in b fold 2.
- **Table 3** (held-out over budget): `seeds_over_budget` and `over_budget`. All 20 cells match (4, 7, 3, 11 / 3, 5, 1, 7 of 20; CoactDetect a 1; SCE b 1; locust 4 and 4).
- **Table 4** (merge at top of grid): `edge_flags` and `moves`. All match (0/8, 8/0, 8/0, 0/8, 0/8, 0/8).

**Summary box**
| quoted | recomputed | verdict |
|---|---|---|
| median move, nets 0.010 | 0.01047 | match |
| median move, coded 0.006 | 0.00646 | match |
| largest move, nets 0.027 / coded 0.023 | 0.0268 / 0.0231 | match |
| best budgeted net's gap 0.030 / 0.025 | 0.0303 / 0.0250 | match |
| budgeted gap below zero in all 8 folds | 8 of 8 | match |
| gap moved 0.005 | 0.00528 | match |
| best on F1 alone −0.007 / −0.029 | −0.0069 / −0.0290 | numbers match (see finding 7) |
| untuned chorus_norm −0.012 / +0.006 | −0.0122 / +0.0055 | match |
| nets train on 10 recordings; coded on 72 | 10 in all fits; 72 pooled in every selection | match |
| nets' merge 2 s | `merge_gap_frames` 20 × 0.1 s | match |
| gap is in precision, not recall | see recall row in section 9 below | match |

**Figure 1**
| quoted | recomputed | verdict |
|---|---|---|
| 33 ROIs, 45 min | 33, 2700 s | match |
| 15 planted, 6 distractors | 15, 6 | match |
| dense stretch 20–25 min | 1200–1500 s | match |
| 20 calls, 14 of 15 matched | 20, 14 | match (also matches the run's own score file, `quiet:2000`, fold 0) |
| 6 of 6 unmatched on distractors | 4 of 6 | **mismatch** (finding 1) |
| no call in the dense stretch | `hot_fa` 0 | match |
| CoactDetect averages 0.75 in the dense stretch | 0.75 over 96 held-out recordings | match |

**Section 2** (from the declaration's `bench_recording`, `simulate.py` and `bench.REGIMES`):
- 120 s spacing, 5 events per level, 30/18/10% → 10, 6 and 3 cells (`max(1, matlab_round(f·n))`), 0.36 s scatter, distractors 6 cells with the same scatter, 300 s dense stretch in which every cell gains 0.06 Hz: all match.
- Quiet 0.0052 Hz (25th percentile) and busy 0.019 Hz (75th): match.
- 2.5 s tolerance (`TOL_SEC`), a call matching anywhere inside its span, and dense-stretch calls excluded from precision (`BenchResult.precision`): all match.
- Pooled per background, then averaged (`objective`): match.
- Ceiling precision 15/21 and F1 0.83 (0.833): match.

**Sections 3 and 4**
- **Nets and hyperparameters:** 24 configurations, 23 drawn plus the default, the same in both draws (the declarations differ only in `recording_seeds` and `replicate`); axes are lr, steps and shape parameters: match.
- **Parameter counts:** 1,897 / 1,905 / 1,233 / 1,149, from the untuned checkpoints: match.
- **Frame:** 0.1 s (`sl.dt`): match. Deep Sets / Zaheer 2017 (`chorus.py`): match.
- **Folds:** 48 seeds in 4 folds of 12 (24 recordings each), from `budgets` and Figure 5: match.
- **Inner fits:** 432 per net, counted in both archives: match. 5 refits; the threshold is picked on 2 recordings: match.
- **Fold fix:** matches the todo, and `fold_check.distinct = true`.
- **Figure 3:** 0.002 minimum gain: match.
- **Refit counts:** "50–55" is a partial match (finding 10).

**Section 5**
- **Ceilings:** 1.6 = 7.0 / 4.4 (workstation handoff): match. Every fold's ceiling is exactly 1.6 × the reference in both draws, so the floor never binds: match.
- **Figure 4** (second draw, fold 0): 10.3 / 8.0 / 5.41 → 16.5 / 12.8 / 8.65: match.
- **30–36% of calls lost** (forks.md §14: 64% and 70% kept): match.
- **Sliding values:** 2 s window, 120 s context, α = 1e-5, 8 s merge, 1 s guard (`coded_base` and the `OPERATING_POINTS` source): match.
- **Shipped table still binned, and why** (`OPERATING_POINTS` "NOT YET SWITCHED"; goal-1 page line 78): match.
- **Only the quiet empty recording is gated; the busy one is reported only** (declaration): match.
- **Empty-recording rates:** SCE 4–33 per hour and CoactDetect 2–6: match (3.9–32.8 and 2.3–6.1), see finding 16.

**Sections 6 and 7**
- **Rehearsal +0.011 / +0.016:** numbers match (finding 9).
- **Declarations differ in exactly two entries:** match.
- **Figure 5 seed ranges; empty twins at seed + 100,000:** match.
- **CoactDetect 0.748 / 0.748:** match. Same configuration under both selections in all 8 folds: match. Search moved in 3 of 4 first-draw folds and never in the second: match.
- **SCE lead +0.023 / 0.000:** match.

**Section 8**
- **Collapse:** chorus_norm, second draw, fold 1, 2 of 5 refits, F1 0.125; fold mean 0.501 against 0.745 untuned: match.
- **One-call inner fits:** 292 and 306 of 864 (chorus_norm), 150 and 150 (chorus_gain_norm), 16 and 22 (line_length), 15 and 12 (tube): all match.
- **Other flags:** 2 chorus_gain_norm refits failed; 1 tube budgeted refit called nothing: match.
- **Figure 7:** same configuration under both selections; refits 1 and 2 call nothing under the budget: match.
- **locust:** 449–527 per hour against ceilings of 15–18 per hour (14.9–18.1): match.
- **SCE's grid top 30 s; goal-1 context of 8 s merge and 6 s crowding** (goal-1 page lines 79 and 86): match.

**Section 9**
- **Standard deviation over folds** 0.005 / 0.018: match.
- **Recall** 0.90 / 0.85 against 0.86 / 0.84: match.
- **Tuning gains:** line_length +0.032 / +0.029 and chorus_norm +0.005 / −0.063: match.
- **Score files do not count duplicate calls:** match (the rows have no `n_duplicate`, although `score.py` computes it).

**Section 10**
- **Baseline and fast stream only; FOUNDATIONS §9** (goals README decisions 2 and 4): match.
- **12 ROIs, 4 recordings, about 0.03%** (83 of 264,075 events): match. Item 3 of the decisions: match.
- **Eight constants inside their intervals, participation outside in both folders** (workstation handoff, lines 847–856): match.

**Section 11**
- **Fit counts:** 1,943 and 1,938: match.
- **Training hours:** 13.2 and 12.7 (sum of `train_sec` 13.21 and 12.69; `device.learned` is `cuda`): match.
- **`--replicate 0` declares exactly what the first draw declared** (the tool writes the key only when R > 0): match.
- **WSMIP064 writes its own report:** unverifiable.

## Unit membership and the design record
The project's design record for this work is the declaration, not a lab record.
- **Counts reconcile:**
  - 48 seeds, and each fold's 36 training seeds plus 12 held-out seeds make 48.
  - Coded entries are scored on 96 held-out recordings; nets on 480 (96 × 5 refits).
  - The two draws share no seed and no empty twin.
- **Twins are independent:** a seed's quiet and busy recordings have different planted times, cells and distractors (checked on seed 2000), so counting them as separate recordings does not overstate independence.
- **Withdrawn recordings:** not applicable, since the runs read no real data.
- **The one real-data dependency** is the bench's fitted constants from the `steps_excluded` folder. The page discloses it, and the handoff shows the constants unchanged on the corrected export.

## Other observations
- **Earlier build:** I compared the page with the round-1 build (`scratchpad\mb\role09\stripped.html`). The data are the same; the medians changed from 0.008 / 0.027 to 0.010 / 0.006 because the rule for excluding flagged entries changed, which is intended.
- **Delivery (outside my role):** `<darkroom>/bugarach/2026-09-18-replicate-run-status/report/` contains only the `review-roles` folders and no `report.html`. This build went to the scratchpad and the repo, not to the generator's darkroom default.

## Key files
- `%USERPROFILE%\bugarach\bugarach-worktrees\replicate-report\docs\learned\tuned_vs_coact\replicate1\report.html` (the artifact)
- `%USERPROFILE%\bugarach\bugarach-worktrees\replicate-report\tools\make_replicate_report.py` (`fig_split` and `other()`, the Figure 1 caption from `rf['distractor_hits']`, and the asserts at lines 836–843)
- `%USERPROFILE%\bugarach\bugarach-worktrees\weekend-runs\src\bugarach\score.py` (lines 104–105 and 267–271: what `distractor_hits` counts)
- `%USERPROFILE%\bugarach\bugarach-worktrees\weekend-runs\src\bugarach\learn\nets\line.py` (the withdrawn "bounded both" claim)
