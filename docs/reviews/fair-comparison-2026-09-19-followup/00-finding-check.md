<!-- Verbatim role report, except that this machine's absolute paths are written as %USERPROFILE% and <darkroom> (the repository is public). The unedited original is in <darkroom>/bugarach/2026-09-18-fair-comparison-run/report/review-followup/. -->

Follow-up (finding-driven) verification of report.html at hash 805b113 (worktree HEAD 127b337). I edited nothing. I checked the page text through page_text.py and re-rendered all 14 figures and 4 tables (scratchpad\v3fig\). Every number in the lede and in sections 6 to 10 was recomputed from results.json, replicate_summary.json, merge_gap.json, breakdown.json, crowded_check.json, meta.json and selections/, plus the raw replicate results. Scripts: scratchpad\verify_r3.py, verify_r3b.py, verify_r3c.py. The darkroom index.html has the same hash (805b113).

## Role 1 (Prove It)
| # | status | evidence |
|---|---|---|
| 1 | FIXED | §6: "In the replicate, the best net counting every refit is chorus_gain_norm, behind CoactDetect by 0.029 and ahead in 1 of 4 folds. This run's best net, chorus_norm, is ahead in 3 of 4…" (recomputed −0.0290, 1 of 4) |
| 2 | FIXED | "across the five refits of one chorus-net choice … differs by up to 23 false alarms per hour" (recomputed 23, chorus_norm, fold 3, busy background) |
| 3 | FIXED | "CoactDetect's 8 to 12.5" |
| 4 | FIXED | "recall 0.79 or more" (minimum is 0.797) |
| 5 | PARTLY | Figure 1 no longer gives the SD. §2 still says "Each event's onsets have a standard deviation of 0.36 s", not "drawn with". |
| 6 | FIXED | "so it was not lost to tuning the nets; the simulator and CoactDetect's own tuning changed together" |
| 7 | FIXED | Lede: "the two chorus nets find more of the faintest events" |
| 8 | FIXED | §9: "(binned SCE, LoCo, locust, SPIKE-synch and rate+context)" |
| 9 | FIXED | "0.012 F1 below its start … inside the 0.02 allowance" (0.0116) |
| 10 | FIXED | Table 1: "48 / 44 / 46 values searchable" |

## Role 2 (DOI or Die)
| # | status | evidence |
|---|---|---|
| 1 | FIXED | SPIKE-synch row cites "Cecchini and colleagues 2021, PLoS Comput Biol 17:e1008963; Kreuz, personal communication, April 2026". It cites the correspondence and does not quote it. |
| 2 | FIXED | Amarasingham is replaced by Pipa 2008, Bocchio 2020 and Dard 2022 |
| 3 | FIXED | "and, for sliding windows, 14:81–119" |
| 4 | FIXED | "the guard is later practice in that structure (Rohling 1983 …)" |
| 5 | FIXED | "designed here, independently, and later found to match". The Table 1 caption names the four unsearched literatures. |
| 6 | FIXED | "credits the technique to Mao and colleagues 2001 (not obtained here). The circular-shift null is the Cossart lab's later practice (Bocchio…; Dard…)" |
| 7 | FIXED | "read the order in which it ranks detectors, never the decimal places of one score" |
| 8 | FIXED | "carry it to repeated k-fold cross-validation, treating k-fold as a special case of random subsampling" |
| 9 | FIXED | Window credited to Quian Quiroga, Kreuz and Grassberger 2002, Phys Rev E 66:041904 |
| 10 | FIXED | Corso and colleagues 2020 (NeurIPS 33) is cited |
| 11 | FIXED | tube and line_length rows: "its comparison with the surrounding stretch is the local-context structure credited under rate+context" |
| 12 | FIXED | "(… as used by Dard and colleagues 2022)" |
| 13 | NOT FIXED | Finn 1967 is not mentioned. The reviewer marked this optional. |
| 14 | NOT FIXED | Informational; the reviewer asked for no change |

## Role 3 (Cross-Examiner)
| # | status | evidence |
|---|---|---|
| 1 | FIXED | §2: "adds 0.06 … (about 12 times the quiet background's rate…)". The Figure 1 caption no longer carries the ratio. |
| 2 | FIXED | Figure 6: "six ROIs fire within a second" |
| 3 | FIXED | §9 now names the four detectors and five starting points |
| 4 | FIXED | The 106 figure is replaced by the chorus-net budget spread (23) |
| 5 | FIXED | Table 3 caption: shipped values match goal 1 exactly; goal 1's sliding values come from held-out crowded recordings. This agrees with the new todo 2026-09-19-goal-1s-crowded-numbers…, which is still untracked (`??`) in the worktree. |
| 6 | PARTLY | "parameter" and "configuration" are used widely now, but "setting" still carries several senses: Terms "a setting is chosen on three"; "choosing every setting"; Table 2 "the budget refused every setting". Figure 8's legend says "every setting tried" where its caption says "every configuration". |
| 7 | FIXED | Searchable counts are given |
| 8 | FIXED | §4.1: "each is shared by the two outer folds that train on that pair" |
| 9 | PARTLY | GLOSSARY.md adds call, firing, background, empty recording, refit and failed-training signature. There is still no entry for local-gap window, chorus_norm, chorus_gain_norm or tube. |
| 10 | FIXED | Figure 7 caption and the glossary now say "empty recordings at the quiet background" |
| 11 | FIXED | Figure 10 has rows at 2, 4, 8 and 16 s |
| 12 | FIXED | "the two chorus nets" |
| 13 | PARTLY | The caption says "about ten minutes", but the panel heading still reads "B. Ten minutes of it, cell by cell" |
| 14 | PARTLY | Row order (Figure 12, nets first) and the participation wording are fixed. The locust × marks are still plotted at about 0.55 against Table 2's "—", though the mean bar is gone. The contamination sentence ("the project lead asked for exactly that in the brief") is unchanged. |

## Role 4 (Reviewer 2)
| # | status | evidence |
|---|---|---|
| 1 | FIXED | §7 gives budget-row t "−2.1 to −1.5 … as weak as the reversal on F1 alone" and names the threshold-at-2 s handicap. The lede says "Margins this small are at the limit…". |
| 2 | FIXED | Lede: "each fits only 10 of the 72 training recordings". §4.2: "The 10 is inherited from the earlier comparison". |
| 3 | FIXED | §10 gives the empty-quiet-background rates (budget 10.4–11.5; nets 0.0–22.9; CoactDetect 5.9–8.2) and notes that the nets were trained on the probe |
| 4 | FIXED | Lede: "a limit set at 1.6 times CoactDetect's own rates". §11 lists the declared margin with no sensitivity run. |
| 5 | PARTLY | The busy empty-recording rates are now shown (§10). The only reason given is "the project lead's decision … (goal 2's decision 3)"; there is no rationale. |
| 6 | PARTLY | The page now argues from the 30 s comparison (0.803) and states the fold-4 admissible win. The replicate sentence it added is false (see New errors 1). |
| 7 | FIXED | §4.6 and §11: "fitted to patterns identical to planted events but labeled the opposite way" |
| 8 | FIXED | "a check made after seeing the held-out scores". Table 4 separates "no calls". The lede points to §6's two places. |
| 9 | FIXED | §5: "a difference between draws of recordings and between machines, which this comparison cannot separate" |
| 10 | FIXED | "The breakdown covers the two chorus nets and this run only"; precision 0.602 vs 0.654 (recomputed, probe calls excluded); 0.79 |
| 11 | FIXED | §10 gives the replicate's tuned-minus-untuned values and untuned +0.006 (by sentence, not in the figure) |
| 12 | FIXED | 12.5 |
| 13 | FIXED | "a distractor counting as called when any call's widened span reaches it" |
| 14 | FIXED | §11: "The hit tolerance was set for the coded detectors" |

## Role 5 (Kill Your Darlings)
| # | status | evidence |
|---|---|---|
| F1 | FIXED | Order is now Question, Answer, Terms; Terms says "CoactDetect and LoCo are two of the coded detectors (Table 1)" |
| F2 | FIXED | §2 gives it its own paragraph, tied to the margins (but see New errors 3) |
| F3 | PARTLY | The merge-gap sentence still stacks an appositive and a relative clause inside one semicolon chain: "…the same merge gap, how close two calls must be…, a setting only the coded side…; and in the second set it is ahead…" |
| F4 | FIXED | Gloss at first use; "trainings"; "two independent sets of simulated recordings" |
| F5 | FIXED | "adds … about 12 times" |
| F6 | FIXED | "local gaps between each ROI's firings"; "about 0.03% of firings" |
| F7 | PARTLY | Same as role 3 #6 |
| F8 | FIXED | Table 4 replaces the repeated glosses |
| F9 | FIXED | "as chorus_norm" |
| F10 | FIXED | §7 opens with the result; the reproduction check is in the Figure 11 caption |
| F11 | FIXED | §6 opens with the conclusion |
| F12 | FIXED | Payload first; "|t| of at least 3.18"; the Varma and Simon sentence is repaired |
| F13 | FIXED | §4.3 defines the modes first |
| F14 | FIXED | "or one under the budget that is not admissible" |
| F15 | FIXED | "It penalizes a merge gap only where the gap fuses events there…" |
| F16 | FIXED | "no fold's budget was low enough to reach it" |
| F17 | FIXED | "the planted count sits on the interval's edge and the declared 0.18 just outside it" |
| F18 | FIXED | Sentence rewritten as suggested; CPU is defined in the Figure 11 caption |
| F19 | PARTLY | Export folder and bootstrap interval are glossed and steps_excluded is dropped. The process sentence ("because the project lead asked for exactly that in the brief") stays. |
| F20 | FIXED | Same as role 1 #8 |
| F21 | FIXED | The seed explanation moved to the Table 3 caption |
| F22 | FIXED | "dropped the local-gap coincidence window that defines SPIKE-synchronization" |
| F23 | PARTLY | Cell-averaging, guard and a single shift term are fixed. "threshold picker" (§7, §10) and "a more liberal operating point" (§10) remain undefined. |
| F24 | PARTLY | (a), (c) and (e) are fixed. (b) "+0.000 at the busy one" and (d) the mix of "this page" and "this report" remain. |
| F25 | FIXED | §10 names the two changes: simulator and CoactDetect's tuning |

## Role 6 (RTFM)
| # | status | evidence |
|---|---|---|
| 1 | FIXED | "the comparison is not like for like … mixes what tuning gained with what the budget cost" |
| 2 | FIXED | "A training seed sets a net's random start and also which 10 of the training recordings it fits" |
| 3 | FIXED | Every-refit comparison leads; the set-aside is labeled post hoc; §10 says the picker's warning "also fires on healthy refits" |
| 4 | FIXED | §4.5: "applied afterwards, it can strike a choice but cannot find one that passes" |
| 5 | FIXED | §9 names the rescue rule, the first-axis order and the fold-1 moves (recomputed 0.73→0.68, 0.48→0.22, 0.64→0.43) |
| 6 | FIXED | "copies of the same stretch with each ROI's firings shifted in time" |
| 7 | FIXED | "a threshold on an approximate p-value that works as a tuning parameter" |
| 8 | FIXED | "no stated form for a learner that fits only part of its training set … not exact for them either" |
| 9 | FIXED | §11: "standardize each ROI over the whole input" |
| 10 | FIXED | §11: "measured … at their shipped configurations" |
| 11 | FIXED | 23 per hour; 12.5 |
| 12 | FIXED | "On F1 alone it costs line_length and tube … under the budget a wider merge helps all four nets" (recomputed, monotone under the budget) |
| 13 | FIXED | §11 names three merge rules; §4.5 qualifies by detector |
| 14 | NOT FIXED | §2 still says "built exactly as a planted event joined by 18% … is built" and says nothing about distractors being placed without regard to planted events |

## Role 7 (Reinventing the Wheel)
| # | status | evidence |
|---|---|---|
| F1 | FIXED | `start_over_budget` now ORs in `refused_all`; the page lists five detectors |
| F2 | NOT FIXED | `fair_comparison_evidence.py` `breakdown.tally` still hand-sums `by_frac`, `n_fa` and so on instead of calling `bench.pool_scores` |
| F3 | FIXED | `context_cut` reads `decl["hand_axes"]` and calls `bench.context_fits_the_null` at the declared `min_sep_sec` |
| F4 | NOT FIXED | `refused_all` is still `n_refused >= n_scored`, with no `within()` cross-check |
| F5 | NOT FIXED | Info only; none required |
| F6 | NOT FIXED | The veto is still re-implemented. The `_clean` docstring ("stored it as NaN") still contradicts the code, which maps None to NaN. |
| F7 | FIXED | The test now asserts against `fold_maker` and `TRAIN_SEED_BLOCK`/`VAL_SEED_BLOCK` |
| F8 | NOT FIXED | Info only; no action requested |

## Role 8 (You Lost Me)
| # | status | evidence |
|---|---|---|
| 1 | FIXED | The lede's terms are glossed in place or in the Terms paragraph |
| 2 | FIXED | CICADA ("the Cossart lab's calcium-imaging analysis toolbox"), cell-averaging, local context and guard are all glossed; encoder/decoder is gone |
| 3 | FIXED | Figure 9 no longer has connecting whiskers; set-aside folds are ringed |
| 4 | FIXED | Figure 11 has a log axis with 0 s set apart, a legend, and one ring size |
| 5 | NOT FIXED | Deliberately declined: the architecture drawings stay in the separate drawing tool, and §3 and §12 point to them |
| 6 | PARTLY | Table 1 and the prose give plain names ("pool-first net", "vote-pooling nets"); figure row labels are still code names |
| 7 | FIXED | Table 2 caption parses |
| 8 | FIXED | §2 names quiet and busy and says "they are not the probe" |
| 9 | FIXED | "'the one it replaces' is the configuration the search started from" |
| 10 | FIXED | "the last two recordings of the list"; the training seed picks the fitting set |
| 11 | FIXED | "the order in which it ranks detectors" |
| 12 | FIXED | Figures 10 and 14 ring the failed-refit folds and say so in the legend and caption |
| 13 | FIXED | Failed refits are explained in §6 |
| 14 | FIXED | Same as role 5 F22 |
| 15 | PARTLY | Both Table 3 headers still read "folds passing against it"; they differ only by the column they follow |
| 16 | PARTLY | Units, repo path and export folder are fixed. The Figure 12 caption now carries `breakdown.json`, and §12's `build_chorus_norm()` developer warning stays. |
| 17 | FIXED | "(Table 1)" in Terms; §2 gives "10 frames a second" |
| 18 | FIXED | "standing in for the stretches when the whole field becomes busier" |

## Role 9 (Show, Don't Tell)
| # | status | evidence |
|---|---|---|
| 1 | NOT FIXED | Deliberately declined: no headline figure beside the lede |
| 2 | FIXED | Figure 13 is the crowded-check dot plot; Table 3 is kept |
| 3 | PARTLY | The merge schematic moved forward (Figure 3, §2). The admissibility band appears only in Figure 13 (§9), so §4.5, §4.6 and §5 now form three consecutive prose-only sections. |
| 4 | PARTLY | Table 4 replaces the refit bullets. There is no strip plot and no false-alarm dot plot. |
| 5 | NOT FIXED | Deliberately declined: the t-correction paragraph stays in §4.1. The grid paragraph also stays in §4.1. |
| 6 | FIXED | Figure 12 shows 30%, 18% and 10% panels |
| 7 | PARTLY | Figure 11 marks "every net ran at 2 s". The values are still repeated in the prose. The reproduction check went to the Figure 11 caption, not §11. |
| 8 | PARTLY | The Figure 1 onset SD is removed, but "6 aligned ticks among the 2,595 firings" stays in the caption. The Figure 9 caption still ends with the list of right-of-zero marks. |
| 9 | PARTLY | Repeated net cells are merged ("as chorus_norm"). The citations stay in the table and there is no concept strip. |
| 10 | NOT FIXED | Deliberately declined: Terms is still one paragraph |
| 11 | FIXED | Figure 9's axis runs −0.20 to +0.05 |

## Role 10 (Ship It)
| # | status | evidence |
|---|---|---|
| F1 | FIXED | The ringed dot means failed-refit fold in Figures 9, 10 and 14; the hollow circle means crowded-check failure only (Figures 8 and 13) |
| F2 | FIXED | Figure 11 uses a legend; there are no leader lines |
| F3 | FIXED | §12: "On a narrow screen, each figure scrolls sideways inside its own frame" (page scrollWidth at 400 px = 400) |
| F4 | FIXED | One ring size, keyed "the gap chosen (CoactDetect, binned SCE)" |
| F5 | FIXED | Figures 10, 12 and 14 carry legends |
| F6 | FIXED | locust × marks spread by fold, with no mean bar |
| F7 | FIXED | "3 firings, no call" |
| F8 | PARTLY | Titles remain: Figure 1 "A. The whole recording", "B. Ten minutes of it, cell by cell"; Figure 5 "A. Before the fix: consecutive order"; Figure 6 "A. As recorded". Figure 11's title is gone. |
| F9 | FIXED | Figure 6 SVG is now 336 px tall (was 330) |
| F10 | NOT FIXED | There is no `<meta name="author">` |
| F11 | FIXED | Caption and axis both say "false alarms per hour" |

## Role 11 (Start With the Problem)
| # | status | evidence |
|---|---|---|
| 1 | FIXED | The merge-gap concept and Figure 3 are in §2 |
| 2 | FIXED | New "4.6 What was not made equal" |
| 3 | PARTLY | Terms now follow the answer, and the answer drops most numbers. Figure 1 still comes after the answer, and the answer keeps "1.6 times". |
| 4 | FIXED | §6: "The one coded detector that scores higher, binned SCE at 0.771, does so by merging calls up to 30 s apart…" |
| 5 | FIXED | Failed refits are defined in §6 |
| 6 | FIXED | "Sections 6 to 8 and 10 give the numbers" |
| 7 | FIXED | §1 only names distractors; the precision cap is in §2 |
| 8 | NOT FIXED | §4.2 and Figure 5 are unchanged in scope |
| 9 | NOT FIXED | Deliberately declined: the caveat stays in §4.1 |
| 10 | NOT FIXED | §3 still gives "0.629 against … 0.748", and the pooling distinction is not tied to a later result |
| 11 | NO LONGER APPLIES | "What passes"; no action |

## New errors

1. **§9, first bullet, "the crowded-recording check was not run there, so whether those results count is unknown".**
   - **Issue:** this is false. The replicate's crowded_check.json was written at 10:07:58, before this build at 10:40, by the same tool. The replicate's own report (10:39) cites it.
   - **What the file shows:** in the replicate, binned SCE under the budget passes the check in 4 of 4 folds (crowded 0.703, 0.703, 0.714, 0.703 against 0.714). It is within budget in folds 1, 2 and 4, and ahead of CoactDetect in exactly those folds: +0.011, +0.014, +0.017. Fold 3 is refused.
   - **Consequence:** binned SCE has admissible wins over CoactDetect under the budget in 3 of 4 replicate folds, against "an admissible win in one fold" in this run. The page hides that.
   - **Severity:** major. It does not touch the headline about nets against CoactDetect, but it is a false sentence concealing a result about which coded detector leads under the budget.
   - **Fix:** read the replicate's crowded_check.json and state the 3 admissible replicate folds ahead of CoactDetect. Guard the sentence with `claim()`.
2. **§6, second sentence, "On F1 alone the margins are small; under the budget they are not" (and the lede's contrast).**
   - **Issue:** in the replicate, counting every refit, the closest net under the budget (chorus_gain_norm, −0.025) is closer to CoactDetect than the closest on F1 alone (chorus_gain_norm, −0.029). The sentence holds only for this run (−0.007 against −0.030). The lede's contrast, "CoactDetect is ahead … on two independent sets" against "nearly tied" on F1 alone, rests in the replicate on setting failed refits aside. The page says every-refit leads.
   - **Severity:** moderate.
   - **Fix:** scope the sentence to this run, or state it as consistency: under the budget every net is behind in 4 of 4 folds in both draws, while on F1 alone the sign varies.
3. **§2, "The margins between the best net and CoactDetect in sections 6 and 7 are 0.007 to 0.010 F1".**
   - **Issue:** the range is hardcoded in the builder (lines 1329–1330). Those sections also quote +0.005 (replicate, set aside), 0.029 (replicate best net), 0.030 (budget, §6) and 0.016–0.020 (budget matched, §7).
   - **Severity:** minor.
   - **Fix:** say "on F1 alone, in this run", or compute the range.
4. **Lede, "tuning moved them by a few hundredths of F1 at most".**
   - **Issue:** the replicate's chorus_norm moved −0.063 on F1 alone, and −0.097 under the budget, which §10 does not report. The phrase is hardcoded and unscoped, while §10 correctly scopes its 0.04 bound to this run.
   - **Severity:** minor.
   - **Fix:** say "in this run", or "up to about 0.06".
5. **Lede, faint-event sentence.**
   - **Issue:** it is unscoped, but holds only for choices on F1 alone. Under the budget, chorus_gain_norm at the quiet background ties CoactDetect 2–2 (0.804 against 0.812).
   - **Severity:** minor.
   - **Fix:** add "on F1 alone".
6. **§4.4, "goal 2's decision 3".**
   - **Issue:** "goal 2" is not defined in Terms (only goal 1 is).
   - **Severity:** minor.
   - **Fix:** gloss it, or say "the run's declared decision".
7. **Figure 14 caption.**
   - **Issue:** it does not say the figure shows this run only; the replicate values are only in the prose.
   - **Severity:** minor.
   - **Fix:** add "this run".
8. **Figure 8 legend against its caption.**
   - **Issue:** the legend says "every setting tried", the caption "every configuration".
   - **Severity:** minor.
   - **Fix:** use one word.

Everything else resolves:
- **Cross-references:** every "Figure N", "Table N" and "section N" reference points to the right item under the new numbering (Figure 3 merging through Figure 14 tuning; Table 4 in §10; §4.6 exists; "section 6 names the two places" resolves). Every §12 path exists, the darkroom copy is identical, and PR #660 is still open.
- **Recomputed and matching:** all Table 2 values and t values; §6 (0.007 behind in every fold; the replicate figures −0.029 with 1 of 4, +0.003/−0.243/+0.003/+0.007, −0.057, +0.005 with 4 of 4; the 0.39 and 0.51 floors).
- §7: +0.010 (4 of 4, t 2.83 / 1.86); +0.009 (3 of 4, t 2.25 / 1.47); budget t −7.1 to −4.3 and −2.1 to −1.5; 0.016–0.020; 0.731, 0.748, 0.803; 0.741 to 0.775; reproduction within 0.0015 and 0.0003.
- §8: 0.59 against 0.35; 0.81 against 0.72; −0.014 and +0.000; precision 0.602 against 0.654; 84–100%.
- §9: 30 s in every fold; 7 of 8; 0.012; +0.030; the fold-1 moves; fixed window in 4 of 4; CoactDetect over budget in 1 of 4.
- §10: all tuned-minus-untuned values; −0.012 and +0.006; 2 of 210 and 240; 3 in the replicate; about 1%; Table 4 rows and seeds; 10.4–11.5, 0.0–22.9, 5.9–8.2, 0–17 (median 1), 8–12.5, 23, 0.0–41.2, 3.4–6.1, 22.7–32.8; overruns 4, 7, 3 and 11 of 20.
- Every figure agrees with its caption; the rings in Figure 9 sit at −0.032 and −0.125, as recomputed.

## Verdict

One major problem remains, and it was introduced by the corrections. §9 says the replicate's crowded-recording check was never run. It was, before the page was built, and it makes binned SCE admissible and ahead of CoactDetect under the budget in 3 of 4 replicate folds. That should be fixed and guarded before the page ships. It does not change the headline comparison of nets against CoactDetect. One moderate problem is also new: §6's "under the budget they are not [small]" is false for the replicate when every refit is counted, which weakens the lede's contrast between the two selections in the second draw. Of the round-3 findings, all the blocking and major ones are FIXED or were deliberately declined (the architecture drawings, the headline figure, the Terms definition list, the placement of the t-correction paragraph). What remains open is minor or moderate: "setting" wording, panel titles, the missing author meta tag, the distractor-placement caveat, and several reuse items in the evidence tool (hand-pooled breakdown, the `refused_all` inference, the `_clean` docstring). One more thing, outside the artifact: docs/todo/2026-09-19-goal-1s-crowded-numbers-compare-two-seed-sets.md is untracked in the worktree and not pushed.