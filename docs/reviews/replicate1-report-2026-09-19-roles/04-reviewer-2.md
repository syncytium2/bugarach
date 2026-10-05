GRANT 4 ok — Read, Grep, Glob, Bash
(I also hold SubagentHandback, which only returns this report. I hold no Edit, Write or NotebookEdit.)

# Reviewer 2 (adversarial), blind verify round 3 of 3

**Artifact reviewed:** `%USERPROFILE%\bugarach\bugarach-worktrees\replicate-report\docs\learned\tuned_vs_coact\replicate1\report.html`. I confirmed its hash is 9a99a7a4209b11b7bb285c260a43ea31aabda1d3. I read the text in full, and read the rendered slices `shots3\light_1100_00`, `_01`, `_05` through `_11`.

**Generator:** `%USERPROFILE%\bugarach\bugarach-worktrees\replicate-report\tools\make_replicate_report.py`, specifically `build()`, `archive_facts()` and section 9.

**Re-decode tool:** `%USERPROFILE%\bugarach\bugarach-worktrees\merge-gap-second-draw\tools\fair_comparison_evidence.py`.

I did not open any earlier review report, and I wrote nothing into any repository. My scratch outputs are in the session scratchpad (`r2_round3_text.txt`, `r2_coact_budget_fold0.txt`).

## Findings

Each finding gives: location · issue · severity · suggested fix · verified against a source.

### 1. The claim that merging keeps every budgeted choice within its ceilings
- **Location:** §9 "At a matched merge": *"merging can only lower a detector's call counts, so every budgeted choice stays within its ceilings."*
- **Issue:** The stated reason is false for one side of the comparison.
  - At both 2 s and 4 s, CoactDetect's merge is *shorter* than the 8 s it was chosen at. So its call counts go **up**, not down. `fair_comparison_evidence.py` says as much in its own docstring: "a coded choice made at 8 s is kept at 2 s". It records no call rates, and nothing checks the budget.
  - I re-ran CoactDetect on the second draw's fold-0 training recordings (seeds 2012–2047). My 8 s run reproduced the run's reference rates exactly: 10.33, 8.0 and 5.41 per hour.
  - At 2 s the rates rose to 12.0 per hour in the dense stretch at the quiet background, 8.67 per hour at the busy background, and 5.44 per hour on the empty recording. The ceilings are 16.5, 12.8 and 8.65 per hour.
  - So the conclusion holds in that one fold, but for the wrong reason. It is unverified in the other 15 fold × gap cases where CoactDetect's merge shrank.
- **Severity:** major.
- **Fix:** Rewrite the sentence along these lines: "a longer merge can only lower call counts, so the nets' choices at 4–16 s and CoactDetect's at 16 s stay within their ceilings. CoactDetect at 2 and 4 s calls more, and its rates were rechecked: …". Add that recheck to the re-decode, and assert it in the generator.
- **Verified against a source:** yes (tool source, meta.json budgets, my re-run).

### 2. "On F1 alone, the two chorus models lead" is asserted but never tested
- **Location:** §9 (in bold) and the plain-words bullet 3: *"came out ahead of CoactDetect in most folds where their training worked"*.
- **Issue:** The report's own yardstick says a lead of about 0.01 cannot be told from luck, yet it calls a +0.005–0.022 matched-merge lead a "lead" and gives no test.
  - I ran the same paired t-test the report uses for the as-run gap, per net and draw at 8 s over the folds kept:

    | net | draw | folds kept | t | p |
    |---|---|---|---|---|
    | chorus_norm | first | 4 | 2.25 | 0.11 |
    | chorus_norm | second | 3 | 12.0 | 0.007 |
    | chorus_gain_norm | first | 3 | 0.46 | 0.69 |
    | chorus_gain_norm | second | 3 | 2.04 | 0.18 |

  - Only 1 of these 4 cases clears p < 0.05.
  - The lead exists only after the net's own failed folds are removed. With those folds included, the 8 s means are:

    | net | draw | mean at 8 s, failed folds included |
    |---|---|---|
    | chorus_gain_norm | first | −0.031 |
    | chorus_norm | second | −0.046 |
    | chorus_gain_norm | second | −0.018 |
    | chorus_norm | first | +0.009 |

  - So in 3 of 4 cases the "lead" flips sign when failed folds are counted. The failures belong to the method, and a user of chorus_norm gets them.
- **Severity:** major.
- **Fix:** Soften "lead" to "at or slightly above CoactDetect, within the between-draw move, and not tested". Or report the paired test per net and draw. Add a Table 5 row, or a note, giving the means with failed folds included. Drop the bold.
- **Verified against a source:** yes (computed from both matched-merge files; my values reproduce Table 5).

### 3. The comparison is pooled over event size, and all the recall structure is in one size
- **Location:** §9 "Where the as-run gap is" and Table 6; §10 "Not broken down by event size".
- **Issue:** The report pools a factor the study manipulates, and says the breakdown "exists in the score files and is not shown". I computed it (chosen under the budget, held-out recordings).
  - For 30% and 18% events, every entry is saturated: recall is 0.95–1.00 for chorus_gain_norm and 0.97–1.00 for CoactDetect.
  - **All** of the recall difference lies in the 3-cell (10%) events. At the busy background, CoactDetect finds 0.35 of them in the first draw and 0.28 in the second; chorus_gain_norm finds 0.64 and 0.52. At the quiet background the figures are 0.81 and 0.80 against 0.80 and 0.63.
  - So the sentence "found fewer at the quiet one and more at the busy one" is entirely a statement about 3-cell events. The reference detector misses about two thirds of small events on a busy background, which bears directly on which detector to keep, and the page hides it.
- **Severity:** major.
- **Fix:** Break Table 6 down by recruitment level, or add a panel showing recall by event size × background for the budgeted entries. Say in the text that recall on the two larger sizes is at ceiling, so only the 3-cell events separate the detectors.
- **Verified against a source:** yes (both draws' score and fit archives, using the generator's own selection logic).

### 4. The two draws' training failures are largely the same fits failing twice
- **Location:** §8 Table 2 and "Training that failed"; §9 "How far results move"; plain-words bullet 2 ("two to three times the typical move").
- **Issue:** The two draws are independent only in their recordings. The 24 configurations *and* the training seeds were held fixed; I confirmed this in the code diff e8764aa..7a95e8a, which says "Everything else is held fixed — the 24 configurations (DRAW_SEED), the training seeds".
  - **Failures:** Of chorus_norm's collapsed inner fits, 111 collapsed in **both** draws (146 in the first, 153 in the second). By configuration and seed, 34 pairs collapsed in both, against 37 and 36 per draw. chorus_gain_norm's 75/75 match is 38 shared fits.
  - So Table 2's two columns are not two measurements of a failure rate. Failure is mostly fixed by configuration × seed, and the pair agrees partly by construction.
  - **The yardstick:** The same fact means the "typical move" excludes the variation from which configurations were sampled and from training seeds. The as-run gap's "two to three times" ratio inherits that underestimate. The §9 hedge "probably understate" does not reach the headline.
- **Severity:** major.
- **Fix:**
  - In §8, say the draws share configurations and training seeds, and give the overlap: the same fits collapsed in both draws, so Table 2 does not replicate a rate.
  - In the headline, add that the move measures changing the recordings only, with configurations and training seeds held fixed, and so understates how far a rerun can move.
- **Verified against a source:** yes (both fit and score archives; git diff of the run code).

### 5. The headline's "in every fold" can be read as a per-fold claim that is false
- **Location:** Plain-words bullet 2: *"the closest by two to three times the typical move, in every fold of both draws"*.
- **Issue:** Read per fold, this is false. chorus_gain_norm's second-draw per-fold gaps are −0.051, −0.010, −0.019 and −0.020, so fold 1 trails by about 1× the typical move (0.010). Only the means are 2–3×. The paired t-test in the second draw gives p = 0.07.
- **Severity:** major (it is the headline).
- **Fix:** Rewrite as "the closest by two to three times the typical move on average (p = 0.001 and 0.07), and below zero in every fold of both draws".
- **Verified against a source:** yes (results.json comparisons).

### 6. "Half to three-quarters as much" is loose, and "the closest" is ambiguous
- **Location:** Plain-words bullet 3 ("the closest learned model still trailed … by half to three-quarters as much") and §9.
- **Issue:**
  - The retained share is 43%–72% (the report itself says 28–57% closes). At 2 s in the second draw only 44% remains (0.011 of 0.025), which is less than half.
  - At a matched merge the closest net in the second draw is chorus_norm (−0.004 at 2 s), not chorus_gain_norm, although chorus_norm has a fold left out.
- **Severity:** minor.
- **Fix:** Write "by roughly half to three-quarters (43–72%)" and name chorus_gain_norm in the bullet.
- **Verified against a source:** yes.

### 7. Figure 10 shows structure the text never mentions
- **Location:** Figure 10, the "chosen on F1 alone" rows for line_length and tube (read from the picture).
- **Issue:** One first-draw line_length fold and one tube fold run off the left edge when the merge is widened to 8 s. Widening the merge on a threshold chosen at 2 s *wrecked* a net: line_length's mean goes from −0.043 as run to −0.088 at 8 s. The text says only that line_length and tube "trail at every merge". This is direct evidence for "the matched merge is not the better comparison", and the prose leaves it unused.
- **Severity:** minor.
- **Fix:** Add one sentence: re-decoding at a longer merge can hurt a net whose threshold was set for 2 s, as in this line_length fold and this tube fold.
- **Verified against a source:** yes (picture plus Table 5).

### 8. Figure 9's caption blames failed training for a fold the † flag does not cover
- **Location:** Figure 9 caption: *"a fold below −0.15, where a net's training failed"*.
- **Issue:** tube's second-draw budgeted fold 0 (−0.164) is drawn with a triangle but is unflagged (Table 1 shows 0.616 with no †). Its drop comes from one refit at F1 0.388: a partial failure the † definition (exactly one call, or no call at all) does not catch. Other partial failures are also unflagged and count as "clean" in the between-draw yardstick: refit F1s of 0.51, 0.508, 0.568 and 0.622.
- **Severity:** minor.
- **Fix:** Change the caption to "a fold below −0.15", and say that the flag catches only the two extreme failure modes.
- **Verified against a source:** yes (per_seed F1 values in results.json).

### 9. The tuning effect is called "probably real" on reasoning that does not support it
- **Location:** §9 "Tuning": *"about as much as the largest between-draw move, so it is probably real but small"*.
- **Issue:** An effect equal to the largest noise observed is not evidence that it is real. The per-fold paired t is 1.97 in the first draw (one fold at −0.016, p ≈ 0.14) and 3.44 in the second (p ≈ 0.04).
- **Severity:** minor.
- **Fix:** Rest the claim on the fact that it recurs in both draws, and quote the paired test. Or soften it to "consistent in direction in both draws, untested".
- **Verified against a source:** yes (results.json, "line_length tuned - untuned").

### 10. Two quantities are never defined
- **Location:** §9 "How far results move".
- **Issue:**
  - The "typical move" is the median of *absolute* moves, and the text never says "absolute".
  - "Favors the nets by about 0.018 relative to the coded side" is the mean signed move of the nets minus that of the coded detectors (generator line 1028). The text never defines it.
- **Severity:** minor.
- **Fix:** Define both in one clause each.
- **Verified against a source:** yes (generator).

### 11. The footer claims more checking than the generator does
- **Location:** §11 footer: *"the build stops if a sentence above stops being true"*.
- **Issue:** Several result sentences have no assert:
  - "Under the budget every net sits below zero in every fold": only the closest net's folds are asserted. The sentence is true; I checked all four nets.
  - The sentence in finding 1 about merging and ceilings.
  - Figure 9's caption claim, "no fold of any net reaches zero".
- **Severity:** minor.
- **Fix:** Assert these sentences, or narrow the footer's claim.
- **Verified against a source:** yes.

### 12. The re-decode's six inexact reproductions are not explained
- **Location:** §9: *"exactly, except 6 refits, off by at most 0.0015"*.
- **Issue:** No reason is given. Five of the six are in the first draw. All six are at thresholds between 0.90 and 0.997, which suggests floating-point or device precision near the top of the threshold grid.
- **Severity:** minor.
- **Fix:** Give the probable cause, or say "unexplained".
- **Verified against a source:** yes (both matched-merge files).

### 13. The held-out budget breaches are understated
- **Location:** §8 "Whether the held-out folds kept to the budget" and Table 3.
- **Issue:**
  - "Some refits of every net went over" understates tube, which went over in 11 of 20 refits in the first draw.
  - No base rate is given, although the reference detector itself went over in 1 of 8 folds.
  - The direction of the bias is not stated. Out-of-budget net output can only flatter the nets' budgeted F1, so the as-run gap is, if anything, conservative.
- **Severity:** minor.
- **Fix:** Quote the rates against CoactDetect's 1 of 8, and state the direction.
- **Verified against a source:** yes (the table itself).

### 14. The rehearsal is judged against noise measured on a different setup
- **Location:** Plain-words bullet 1 and §9: the rehearsal's lead "could not have been told from luck".
- **Issue:** The noise scale was measured on the current bench with 12 seeds per fold, and it is applied to a rehearsal run on a retired simulator with 6 seeds per fold (per the run code's own comment, "Twelve seeds per fold, not six"). The conclusion probably holds more strongly, since fewer recordings mean more noise, but the text should say it is an extrapolation.
- **Severity:** minor.
- **Fix:** Add a clause saying so.
- **Verified against a source:** yes (the comment in `tune_learned_vs_coact.py`).

### 15. Three figure titles name the quantity rather than the point
- **Location:** The bold titles of Figures 6, 10 and 11.
- **Issue:** They name the quantity plotted, not why it matters. Figure 8's caption does state its purpose.
- **Severity:** minor.
- **Fix:** Examples: "Figure 10. A matched merge closes part of the budgeted gap, not all of it". "Figure 11. The best net's extra false alarms fall outside the dense stretch".
- **Verified against a source:** yes (rendered slices).

### 16. Some fixed values are given without a reason
- **Location:** §2 (the 2.5 s matching tolerance) and §9 (the matched-merge grid of 2, 4, 8 and 16 s).
- **Issue:** Nowhere does the report explain why 2.5 s, or why the nets stop at 16 s while CoactDetect was re-decoded up to 30 s. Section 10 lists 2.5 s as fixed and untested, but gives no reason for its value.
- **Severity:** minor.
- **Fix:** Add one clause of justification for each, or say the value was inherited and where from.
- **Verified against a source:** yes (the tool's `NET_GAPS` and `CODED_GAPS`).

## Checked and found clean
- **Paired t-tests:** t = −13.0 with p = 0.001, and t = −2.8 with p = 0.07, both on 3 degrees of freedom, recomputed from results.json.
- **CoactDetect's 0.748 in both draws:** the per-fold values average 0.7480 in the first draw and 0.7478 in the second. This is a genuine coincidence. The first draw moved settings in 3 of 4 folds (alpha in folds 0 and 2, guard in fold 1), as stated.
- **The two runs' code:** the diff contains only the `--replicate` option, as claimed.
- **Arithmetic:** F1 of exactly 0.125 for one call per recording, and the 0.83 practical ceiling, both check out.
- **Budget ceilings:** each equals the reference rate × 1.6 (meta.json).
- **Table 2 and Table 5:** Table 2's counts reproduce, and so do Table 5's gaps at 2 and 8 s and its left-out folds.
- **Other statements:** "11 of those 13 folds" and "every net below zero in every budgeted fold" are both correct.
- **Re-decode reproduction:** this check has real power to fail, because it re-loads checkpoints and thresholds, and it is not circular.
- **Enrichment claims:** there are none. No rate-versus-count issue arises.
- **Figures 1, 5, 6 and 8:** the images support their captions. The low isolated folds in Figure 6 are the flagged ones.
