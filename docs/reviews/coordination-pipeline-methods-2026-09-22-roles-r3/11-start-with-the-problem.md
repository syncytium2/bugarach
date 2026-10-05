# Role 11 — Start With the Problem (round 3, blind pass, verbatim as returned)

GRANT 11 ok — Read, Grep, Glob

(I also hold SubagentHandback, the report channel. I hold no editing tool.)

# Role 11: argument order review of the methods section

**Artifact:** docs\methods\coordination_pipeline_methods.md (ee7bd62). I also read §5 of docs\methods\coordination_pipeline_methods_cover_memo.md.

**Arc used:** dependency order for a methods section: input → constructed test material → instruments → yardstick → tuning → learned models → comparison → application → downstream measure. The document follows this arc. The one departure from the PI's list, putting scoring before optimization, is explained in memo §5. That is the right place for it, because a manuscript should not narrate the PI's list.

**Overall:** the order holds. Every section comes after the material it needs, with one exception: *Learned detectors* uses the cross-validation design, the configuration search and the false-alarm rule, and all three are only introduced in the next section. The remaining issues are minor forward references, most of them signposted.

## Spine (one claim per section)

0. **Preamble.** A coordinated event is a set of cells whose events fall within about 1 s of one another more often than chance would produce. Detectors report calls. Coded detectors are hand-written rules; learned detectors are trained networks.
1. **Detected calcium events.** The input is the pipeline's exported fast-stream event tables: 84 recordings from 44 mice, 67 of them with a TTX or senktide first treatment. The pipeline had already applied the exclusions, and it supplies one analysis window per period.
2. **Synthetic recordings.** Benchmark recordings plant known coordinated events at three participation levels on a background matched to the data. Distractors and an elevated-rate block are added. The constants are consistent with a re-measurement on the recorded data (Table 2). Three test recordings target specific failures.
3. **Coded detectors.** Six coded detectors are described: their rules, their nulls, where each comes from, and how the ports were validated.
4. **Scoring.** Calls are matched one-to-one to planted events within 2.5 s. The objective is F1 averaged over the two backgrounds, and distractors cap it at 0.83. A setting is admissible when it meets the Table 3 limits, which are set against the default setting.
5. **Optimization of coded detectors.** A coordinate search with two-parameter grids used seeds 1–48 for selection and seeds 49–96 as a held-out set. Only the CoactDetect and LoCo changes were adopted. Table 4 gives every parameter.
6. **Learned detectors.** Four small architectures label frames. They are trained with weighted cross-entropy on crops, and their calls are decoded by a threshold plus a 2 s merge gap.
7. **Comparison of coded and learned detectors.** Nested four-fold cross-validation on seeds 1000–1047, under two selection rules, replicated on seeds 2000–2047. The close-events test is re-selected or reported, and "separable" is defined by a corrected paired t.
8. **Analysis of recorded data.** The six coded detectors run at their Table 4 settings, plus one learned refit. Calls are counted by onset inside each analysis window, as calls per minute. The statistics are out of scope.
9. **Width and amplitude.** One rule for every detector: the width and cells-per-second of the core event group inside each call. The rule has not been checked against planted events.
10. **Limitations.** Everything was tuned at 33 cells on baseline-rate backgrounds. The comparison uses a single generator, and several constants were set by judgement.

## Cold open

The reader first sees a four-sentence definitions paragraph, then *Detected calcium events*. The PI asked to "start with the detected calcium event data". The first heading does that, and the definitions are the minimum needed to read what follows. In a methods section the "problem" is the input, and the input comes first. Verdict: acceptable.

## Findings (location · issue · severity · suggested fix · verified)

1. *Learned detectors*, lines 348 and 376–380, and *Decoding* line 385 · **Backward dependency on the next section.** The section opens by deferring to "the cross-validation described in the next section". *Training* then uses "the tuning recordings of its cross-validation fold". It also refers to "the configurations searched", but the search itself (24 configurations, 23 random plus the default) is only described at line 396. *Decoding* uses "the false-alarm rule below", which is defined at line 404. A reader of *Training* cannot tell which seeds the fits used (1000–1047, not the 1–48 of the section just before) or how many recordings the "tuning recordings" are (72). · **major** · Put a three-sentence design paragraph at the head of *Learned detectors*: seeds 1000–1047 at both backgrounds, four outer folds of 12 seeds, 72 tuning recordings per fold, and a one-line pointer to the two selection rules. Alternatively, move the first paragraph of *Comparison* (the nested CV design) ahead of *Learned detectors* and keep the rules and separability after it. · verified yes

2. *Comparison* → *Analysis of recorded data*, lines 401–442 · **The comparison's link to the recorded-data run is never stated.** Memo §5 justifies the *Comparison* section as "how the learned detector used on recorded data was chosen". The manuscript never says so. Line 437 names the detector (cell-set network with channel gain, replication draw, false-alarm rule) but not why it was chosen over the other three architectures, the first draw, or the F1-only rule. Separability, the section's final construct, is never used again. As written, *Comparison* has no job in the spine beyond describing itself. · **moderate** · Add one sentence either at the end of *Comparison* or at line 437 giving the criterion that picked this detector, with a reference back to separability or the rule. If no criterion was applied, say the choice was by judgement and add it to *Limitations*. · verified yes (lines 437–442 give no reason)

3. *Coded detectors*, line 163; *Scoring*, line 245 · "Their defaults are binned" uses *default*, which is only defined two sections later as the "default setting". · minor · Either define the default setting at its first use in *Coded detectors* ("the setting stored with each implementation"), or write "their stored settings are binned". · verified yes

4. *Coded detectors*, line 163; Table 4 placement · The PI's "knobs for each detector" are answered by Table 4. *Coded detectors* points to it, but the table appears only at the end of *Optimization*, two sections later. Memo §5 lists "coded detectors (the knobs, all in Table 4)", which implies the table sits there. It combines knobs, grids and outcomes, so its current position is defensible. · minor · Keep the table where it is and correct memo §5 to say Table 4 sits in *Optimization*, because its "value" column is that section's result. Or split it: parameters and grids in *Coded detectors*, values in *Optimization*. · verified yes

5. *Learned detectors*, lines 357, 396, 440 · "Default configuration" of a learned detector is used three times and never defined. The size parameter ("the architecture's size") is not specified. This is the learned-detector half of the PI's "knobs for each detector", and it has no table. · minor · Give the default configuration and the ranges searched: learning rate, steps, size. A short table, or a row group added to Table 4. · verified yes

6. *Detected calcium events*, lines 18, 50, 55 vs 21 and 57 · "Fast stream" (line 18) is used before it is defined (line 21). "Baseline" and "treatment periods" (lines 50 and 55, in the exclusions) come before the *Periods and analysis windows* paragraph (line 57). · minor · Move the stream sentence ahead of the "87 rows" sentence, and move the *Periods* paragraph ahead of the exclusion list. · verified yes

7. *Synthetic recordings*, line 104 · "1.6 times the senktide rate": the senktide rate is never given. "6 times the measured baseline rate" is also not tied to the quiet or busy rates given at line 85. · minor · Give the senktide rate, in events s⁻¹ per cell, and the baseline rate being compared. · verified yes

8. *Test recordings*, lines 147–153 · Forward references to "the settings search", "the comparison of coded and learned detectors" and "CoactDetect (below)". All are signposted and all are needed, because the test material is described once, where it is built. · advisory · No change needed. Optionally, name the sections they point to. · verified yes

9. *Learned detectors*, line 365 vs 374–375 · "The crop in training" (in *Architectures*) comes before crops are defined in *Training*. · minor · Write "(a 409.6 s training crop, see *Training*)", or move *Training* ahead of *Architectures*. · verified yes

10. *Comparison*, lines 394–395 · "Under the false-alarm rule below, its budget replaced them": a forward reference within the section, one paragraph ahead. · advisory · Move the *Two selection rules* paragraph before the coded/learned tuning bullets. · verified yes

11. *Comparison*, lines 413–414 · Learned detectors' merge gaps are re-selected "subject to the close-events limit". Table 3 defines that limit as a fall in F1 relative to a detector's *default setting*, and learned detectors have no Table 3 row or default setting. The reference point is not stated anywhere earlier. · minor · State the reference for learned detectors, for example "relative to the 2 s gap it was trained with". · verified yes

12. *Analysis of recorded data*, lines 452–453 · The PI's item 8, "how are the real data assessed", is answered only up to rates. The statistical assessment is explicitly left out. The document discloses this, so it is not an order defect, but the item is only partly answered. · minor (brief coverage) · Leave it as it is, but make sure the PI knows. Memo §2 raises it as "No statistics plan"; memo §5's "every item on your list is answered" overstates this item. · verified yes

13. Memo §5, "The benchmark" · The memo reads the PI's "benchmark" as the synthetic benchmark recording and its derivation. That reading is answered by *Origin of the constants* and Table 2. A second reading also fits: the performance yardstick, or CoactDetect's false-alarm level as the reference. The memo states its reading, which is correct practice, but only the PI can confirm it. · advisory · Leave it, and ask the PI to confirm the reading. · verified yes (reading) / no (PI's intent)

## Section table (job · earliest intelligible position · verdict)

| § | job in the argument | earliest intelligible position | verdict |
|---|---|---|---|
| 0 Preamble | defines coordinated event, call, coded and learned | 1st | holds |
| 1 Detected calcium events | the input and the populations (84 recordings, 67 analysed) | 1st after preamble | holds; tidy the internal order (#6) |
| 2 Synthetic recordings (+ tests) | constructed test material with known answers, and why its constants are credible | after §1, because the rates and widths come from §1 | holds |
| 3 Coded detectors | the instruments | after §1; needs events and windows only | holds (#3, #4) |
| 4 Scoring | the yardstick and admissibility | after §2 and §3, because it needs planted events, distractors, tests and call intervals | holds; correctly placed ahead of the PI's order |
| 5 Optimization | tuning the instruments against the yardstick; gives Table 4 | after §4 | holds |
| 6 Learned detectors | the learned instruments and their training | after §4, and **after the CV design in §7** | **misplaced in part (#1)**: needs the fold and rule definitions first |
| 7 Comparison | coded vs learned under nested CV, and choosing the learned detector for recorded data | after §5 and §6 | holds, but its link to §8 is never stated (#2) |
| 8 Analysis of recorded data | applies the chosen detectors and defines rates | after §5 and §7 | holds |
| 9 Width and amplitude | downstream measure, one rule for all detectors | after §8, because it needs calls on recorded data | holds |
| 10 Limitations | residual risk | last | holds |

## The PI's nine items

| # | PI item | answered where | status |
|---|---|---|---|
| 1 | detected calcium event data | §1 *Detected calcium events* (first) | answered, in the PI's position |
| 2 | how synthetic data sets are constructed | §2 *Synthetic recordings*: Background, Planted events, Distractors, Elevated-rate block, Event widths, Test recordings | answered |
| 3 | how coded detectors are optimized | §5 *Optimization of coded detectors* | answered; moved after scoring, and memo §5 explains why |
| 4 | how the models are trained | §6 *Training* and *Decoding*; configuration selection in §7 | answered, but only intelligible once §7's design is known (#1) |
| 5 | what the benchmark is and how it was determined | §2 *Origin of the constants*, Table 2, Figure 1 | answered under the memo's reading (#13) |
| 6 | parameters used to score the detectors | §4 *Scoring*: 2.5 s tolerance, F1, objective, Table 3 | answered |
| 7 | knobs for each detector | Table 4, in §5, for the coded detectors; §6 for the learned ones, partly | answered for coded; incomplete for learned (#4, #5) |
| 8 | how the real data are assessed | §8 *Analysis of recorded data* | partly: rates defined, statistics deferred (#12) |
| 9 | universal amplitude and width assessment | §9 *Width and amplitude* ("one rule for every detector") | answered |

**Deviation from the PI's order:** stated in memo §5, and justified by what each section needs from the ones before it. The added *Comparison* section is justified in the memo but not in the manuscript (#2). No section is out of place except the part of §6 that depends on §7.
