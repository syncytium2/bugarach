GRANT 4 ok — Read, Grep, Glob, Bash

# Role 4, Reviewer 2 (adversarial): Round 1 findings

**Artifact:** `%USERPROFILE%\bugarach\bugarach-worktrees\replicate-report\docs\learned\tuned_vs_coact\replicate1\report.html`

**What I checked:**
- All 8 screenshots, plus the embedded Figure 1 PNG, extracted and enlarged.
- The extracted text of the report.
- `results.json`, `meta.json`, the per-fold selections and the per-recording score archives of both runs.
- `tune_learned_vs_coact.py`, `train.py`, `score.py`, `bench.py` and `simulate.py` in the weekend-runs worktree.
- The generator `make_replicate_report.py` (the defect-exclusion logic and the prose asserts).
- The HANDOFF-workstation-tuning spec on `origin/tune-bench-comparison`.
- The git diff between the two runs' commits (e8764aa for WSMIP064, 7a95e8a for WSMIP065).

My scratch outputs are in `...\scratchpad\mb\role04\` (`report.txt`, `learned.txt`, `raster_top.png`).

**Format:** location · issue · severity · suggested fix · verified against a source (yes/no)

---

## Blocking

**B1. Summary bullet 2, and §9 "On F1 alone, the question is open"**
- **Issue:** The contrast between the two selections is created by switching columns. "On F1 alone, the leading net" is really the *untuned* chorus_norm (Table 1's untuned column), set against CoactDetect's *chosen-on-F1-alone* entry. In the report's own "chosen on F1 alone" column, no net reaches CoactDetect in either draw:
  - WSMIP064: best net chorus_norm 0.741 vs 0.748
  - WSMIP065: best net chorus_gain_norm 0.719 vs 0.748
  - So under both selections the tuned nets trail in both draws. The only net that ever beats CoactDetect is the untuned chorus_norm in one draw (+0.006).
  - Choosing the untuned column after its tuned twin collapsed is a selection on the outcome. Picking the best of about 8 net cells against one reference also carries a winner's-curse bias.
- **Fix:** State the like-for-like numbers per column: F1-alone gap −0.007 / −0.029; budget gap −0.030 / −0.025. Then report the untuned result separately, as "the untuned default ties CoactDetect". Do not label it "On F1 alone".
- **Verified:** yes (Table 1; `results.json` means).

**B2. Summary bullet 3; §7 around Figure 7; §9 "How big a real difference has to be" (the noise yardstick)**
- **Issue:** The "median 0.008, at most 0.027" yardstick is not a sound noise measure for a net-minus-CoactDetect gap, for five reasons:
  - **(a) It mixes two populations.** Split by type, the 20 entries give:

    | entries | count | median between-draw move |
    |---|---|---|
    | coded detectors (deterministic, no training noise) | 10 | 0.005 |
    | nets | 10 | 0.015 |

    Two of the coded entries are CoactDetect's two identical 0.000 rows, counted twice. The gaps under study are net minus coded, so the relevant move is the net's, about 0.015. Against that, 0.030 / 0.025 is about 2×, not "about 3 times".
  - **(b) The moves are not independent.** 9 of the 10 clean net entries moved upward in WSMIP065 (untuned +0.018, +0.027, +0.006, +0.022), while the coded entries mostly moved down. That is a draw-level shift shared across nets, not 20 independent draws.
  - **(c) The exclusion is hand-coded by entry name.** `make_replicate_report.py` line 653 sets `defective = {("chorus_norm","ungated"),("chorus_norm","gated")}`. It is also inconsistent with Table 1's own † marks: chorus_gain_norm-F1-alone † and tube-budget † stay *in* the yardstick. Including every entry gives median 0.0105 and max 0.060. With max 0.060, the generator's own assert `min(ll) > noise_max` (line 677) fails, so the line_length sentence would not survive.
  - **(d) The Figure 7 bolding is circular.** The threshold is the maximum over the non-excluded rows, so only excluded rows *can* exceed it. "Those bold rows are the defects of section 8" is true by construction, not a finding.
  - **(e) "At most 0.027" is the maximum of 20 values**, so it grows with the number of entries. It is not a bound.
- **Fix:**
  - Report the between-draw move separately for nets and coded detectors.
  - Use the change in the *gap* between draws (e.g. chorus_gain_norm budget gap: −0.030 → −0.025, a move of 0.005; untuned chorus_norm: +0.018) as the yardstick for gap claims.
  - Define the exclusion from the † / ‡ flags, not by name.
  - Drop the max-based threshold, or label it descriptive.
- **Verified:** yes (computed from Figure 7's values and generator lines 650–683).

**B3. §9 "Within a run the four folds share training data…" (the strongest evidence is withheld)**
- **Issue:** The report dismisses the per-fold paired statistic, yet it is the best support for the headline and it is already in `results.json` → `comparisons.gated`. The chorus_gain_norm − CoactDetect budget gap is negative in all 8 outer folds:
  - WSMIP064: −0.029, −0.033, −0.035, −0.024
  - WSMIP065: −0.051, −0.010, −0.019, −0.020
  - Paired t per run: −13.0 and −2.8 on 3 degrees of freedom.

  Held-out folds share no scored recordings; the dependence runs only through training overlap. What the report offers instead ("same sign twice") is a sign test on 2 observations (p = 0.25).
- **Fix:** Show the per-fold gaps for both draws (8 dots) with the training-overlap caveat. Present the pair as the replication check on top of that, not as the only evidence.
- **Verified:** yes.

**B4. §4–§5, summary bullet 1 (undisclosed asymmetries that could produce the gap)**
- **Issue:** The budget gap is a precision gap, not a recall gap:
  - Mean recall under the budget: chorus_gain_norm 0.86–0.93 vs CoactDetect 0.83–0.89. The net finds *more* events.
  - Per-recording decomposition of held-out false alarms (my computation from the score archives):
    - Busy-stretch false alarms: CoactDetect 0.88 / 0.75, chorus_gain_norm 0.09 / 0.14. The net is far cleaner there.
    - Decoy hits: about 5.8 vs 5.5, roughly equal.
    - False alarms that are neither busy-stretch nor on a decoy: CoactDetect 0.57 / 0.24, chorus_gain_norm 3.51 / 2.10.

    Those extra "other" false alarms are the whole deficit.
  - Three undisclosed design differences point straight at this:
    - **(a) Merge gap.** Nets decode with a fixed `merge_gap_frames=20` (2 s; `train.py` `pick_threshold` returns it untouched, and there is no merge axis in `LEARNED_AXES`). Every coded detector tunes its merge gap and sits at the grid top in 8/8 folds (CoactDetect 8 s, SCE 30 s). Duplicate calls on one event count as false alarms (`score.py`: dups stay in `fa_times`).
    - **(b) Training data.** Each net fit trains on `N_TRAIN=10` of ~70 training recordings, and its ungated threshold is picked on 2 recordings (`fold_maker` n_val=2, read twice). Coded detectors search on all 72.
    - **(c) Carried threshold.** Under the budget, one threshold is carried onto all 5 refit seeds. The handoff required saying so; the report doesn't. This is why some refits "called nothing".
  - "Refitted on all three training folds" reads as "trained on all 72 recordings". The truth is a 10-recording draw spanning the three folds.
- **Fix:**
  - Disclose (a)–(c) in §4/§5 and in §10 Limits.
  - Before claiming "no learned model reached CoactDetect", re-decode the nets' held-out probabilities at CoactDetect's 8 s merge gap. This is cheap: no retraining.
  - Report the false-alarm decomposition (busy stretch / decoys / other) per entry.
- **Verified:** yes for (a), (b), (c) and the decomposition. No for duplicates being the mechanism: the score rows carry no dup count.

**B5. §5, Table 1 "chosen under the budget" (held-out budget compliance never reported)**
- **Issue:** Budgets are checked on training recordings only. `results.json` has `seeds_over_budget` for nets and `over_budget` for coded detectors, but the report never shows either, although the handoff required "how often the held-out rates exceed the budget". Refit seeds (of 20) over budget on held-out:

  | entry | WSMIP064 | WSMIP065 |
  |---|---|---|
  | chorus_gain_norm | 7 | 5 |
  | tube | 11 | 7 |
  | chorus_norm | 4 | 3 |
  | line_length | 3 | 1 |

  CoactDetect itself was over budget on held-out in WSMIP064 fold 2 (alpha 3e-5). "Under one shared false-alarm budget" is therefore only true on training data.
- **Fix:** Add a held-out compliance column or table, or add it to Figure 6. Rephrase the claim as "budget met on training recordings; held-out exceedances: …".
- **Verified:** yes.

---

## Major

**M1. Summary bullet 3; §6; §9 (the rehearsal's +0.011)**
- **Issue:** "The +0.011 lead of the rehearsal run … sits inside it [the noise]" treats the rehearsal as a draw of the same comparison. It was not. Commit e8764aa ("Fix the fold defect, search the coded side sliding, and double the recordings") shows the rehearsal differed in three ways: the fold defect, a binned coded search, and 6 seeds per fold.
  - By the report's own yardstick, the swing from +0.011 to −0.030 / −0.025 (about 0.04) *exceeds* the 0.027 maximum. So the design changes, not the draw, moved it.
  - The +0.011 is also typed by hand (generator lines 778, 914, 1006), although §11 says "nothing on it is typed by hand".
- **Fix:** Say the rehearsal ran against a different (binned-search) coded side and a defective fold split, so its margin is not comparable. Source the number from a file.
- **Verified:** yes.

**M2. §5, Figure 4 (what the budget can and cannot catch)**
- **Issue:**
  - **(a) The busy empty recording is not gated.** The gate uses only the quiet empty recording (`gate_empty_recording: null_quiet`; `null_busy` is "reported only"). Binned SCE fires 22–34 per hour on the busy empty recording (CoactDetect 2–5) and passes. That is how SCE "under the budget" scores 0.770 in WSMIP064, above CoactDetect. §5's "a detector that fires … on a recording with nothing in it is not usable" implies more coverage than the gate has.
  - **(b) The busy-stretch probe counts calls, not time spent firing.** SCE's held-out probe is exactly 12.0 per hour in every fold, at both backgrounds. That is one call per 300 s busy stretch in every recording: its 30 s merge gap collapses sustained firing into one call. The ceiling (about 12.3–12.8 per hour at the busy background) allows roughly one call per busy stretch, so "fires on the busy stretch" is not what it rejects.
  - **(c) The 1.6 is unjustified on the page.** The handoff says it was carried over from binned CoactDetect's ratio (7.0 against 4.4) and must be declared.
- **Fix:**
  - State that the busy empty recording is ungated, and show each entry's rate on it.
  - Restate the busy-stretch ceiling as "about one call per busy stretch".
  - Give the origin of 1.6 and say it was carried over.
- **Verified:** yes.

**M3. Figure 1 and caption; §2 (reading the picture, and the decoys)**
- **Issue:**
  - The enlarged lane shows 4 of the 6 hollow decoy triangles with a red × directly beneath. Per the score file, CoactDetect hit all 6 decoys in this recording (the other two sit inside thick ticks next to planted events). Decoys are about 80% of CoactDetect's false alarms overall (5.8 of 7.3 per recording).
  - The red × is never defined in the caption.
  - The decoys are generated exactly like a planted 6-cell event (`distractor_frac` 0.18 and the same 0.36 s jitter, per `simulate.py`), differing only in label. No detector can separate them in principle. This caps precision near 15/21 = 0.71 and F1 near 0.83 for a detector that finds every event of 6 or more cells. None of this is said; "not coordinated events" is undefined.
  - The example shows CoactDetect with zero calls in the busy stretch, but it averages 0.75–0.88 there per recording. The figure flatters the reference on exactly the axis the budget polices.
- **Fix:**
  - Define the ×.
  - Say decoys are generatively identical to 6-cell events, and give the F1 ceiling this implies.
  - Say the example's clean busy stretch is atypical, and give the average.
- **Verified:** yes.

**M4. §7 "CoactDetect is the steadiest … its two columns are identical … the budget is built around its own settings"; §9 "among the steadiest"**
- **Issue:**
  - In WSMIP065 the coordinate search never moved off the reference (`moves: []`; min_gain 0.002). In WSMIP064 it moved in 3 of 4 folds (alpha 3e-5, guard 0), and fold 2 was over budget on held-out. So the "0.748 and 0.748" compares a tuned setting with an untuned one, and the 0.000 is a coincidence of means.
  - "Steadiest" for either entry rests on one between-draw difference each. That cannot estimate an entry's variance.
- **Fix:** Say what CoactDetect's search did in each draw. Drop the steadiness argument, or ground it in per-fold spread.
- **Verified:** yes.

**M5. §8, Table 2; §10 "No crowded check" (the missing crowded-recording veto)**
- **Issue:** The report confines the crowded caveat to SCE. But the bench's 120 s minimum spacing rewards long merges for *every* coded detector: all six hit the top of their merge-type grid in 8/8 folds. Meanwhile the nets are pinned at 2 s (B4a).
  - `score.py` also matches any detection whose span contains a planted event, at any tolerance. Wide merged spans therefore match more easily.
  - The comparison as a whole, not only SCE's lead, is shaped by a bench spacing that no crowded check tests.
- **Fix:** Widen the §10 limit accordingly. Note that the matching rule favours wide spans.
- **Verified:** yes for the grids and scoring rule. No for the magnitude.

**M6. The results are not broken down by the design variables**
- **Issue:** Every headline pools the two backgrounds and the three recruitment sizes (30 / 18 / 10%). The data exist (`f1_by_background`; `by_frac` in the score rows).
  - The budget gap differs by background, e.g. chorus_gain_norm busy −0.035 in WSMIP064 vs −0.014 in WSMIP065.
  - Recall by event size is not shown anywhere.
- **Fix:** Add a per-background × per-event-size panel for the headline entries.
- **Verified:** yes (the background split was computed; the event-size split was not).

**M7. Figure 6 caption "The lone low dots are defects named in section 8, not draws"**
- **Issue:**
  - tube's WSMIP064 budget dot at 0.505 (fold 0, refit seed 4 at F1 0.000) is a visible lone low dot that §8 never names.
  - "Not draws" is an assertion. A configuration that collapses at some seeds is part of the pipeline's between-draw variability, not something outside it.
  - The failed-training flag (`failed_training_signature`) fires only when F1 is within 0.01 of 0.125 and the threshold sits at the bottom of its grid. Partial collapses (e.g. tube WSMIP065 fold 0 seed 3 at 0.388) and zero-call refits are not flagged.
- **Fix:** Name tube's collapse in §8. Replace "not draws" with the flag's actual definition and its blind spots.
- **Verified:** yes.

---

## Minor

**m1. §6 "nothing else differs — the two declarations differ in exactly 2 entries"**
- **Issue:** Verified true of the declarations. But a declaration diff cannot see code: the runs used different commits (e8764aa, 7a95e8a) on different machines. I checked the diff: it is replicate plumbing, a test and handoff text only, so benign.
- **Fix:** Say the commits differ and that the diff is plumbing only.
- **Verified:** yes.

**m2. Summary bullet 1 "The best budgeted net in both"**
- **Issue:** In WSMIP064 chorus_gain_norm beats chorus_norm under the budget by 0.002 (0.718 vs 0.716). "Best" is fragile, and the generator asserts it (line 670).
- **Fix:** Say "all four nets trail", with the numbers.
- **Verified:** yes.

**m3. §9 "Tuning helped one net … more than any entry moved between draws"**
- **Issue:** True only with the exclusions; the moves go up to 0.060 including defective entries. In WSMIP064 fold 2 the tuning gain was also negative (−0.016).
- **Fix:** Add "…than any entry without a defect", and give the per-fold count (7 of 8 folds positive).
- **Verified:** yes.

**m4. Summary "Neither run alone could show that"; §6 "one run cannot measure that"**
- **Issue:** Overclaim. A recording bootstrap within one run measures the recording-sampling part. What a single run cannot measure is data-draw variability of training and selection.
- **Fix:** Narrow the wording.
- **Verified:** no (reasoning).

**m5. Table 1 ‡ cells**
- **Issue:** Means average inadmissible folds (e.g. SCE's 0.557) together with admissible ones. The handoff's rule was to count "no admissible configuration" as 0.
- **Fix:** Give the admissible-fold mean and count, or follow the declared rule.
- **Verified:** yes.

---

## Checked, no finding
- The fold check can fail. `tests/test_tune_learned_vs_coact.py::test_the_fold_check_fires_on_the_old_contiguous_order` exists at both run commits, and both `meta.json` files record `fold_check.distinct: true`.
- The declarations differ in exactly `recording_seeds` and `replicate`.
- The seed ranges are disjoint, including the empty-recording twins.
- The 449–527 per hour figure for locust matches the data.

## Summary
The budgeted headline (nets trail CoactDetect) survives, and more strongly than the report argues: 8 of 8 folds are negative. But the report:
- argues it with a diluted, circular yardstick;
- creates its F1-alone contrast by switching columns;
- never reports held-out budget compliance;
- omits the asymmetries that plausibly produce the gap. The net's deficit is off-decoy, off-busy false alarms, alongside a fixed 2 s merge gap, 10-recording training and a threshold picked on 2 recordings.

The next step I would ask for is to re-decode the nets at an 8 s merge gap before the headline ships.
