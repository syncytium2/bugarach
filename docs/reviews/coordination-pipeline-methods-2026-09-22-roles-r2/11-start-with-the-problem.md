# Role 11 — Start With the Problem (round 2, blind pass, verbatim as returned)

GRANT 11 ok — Read, Grep, Glob (plus SubagentHandback, the report channel; no editing tools held)

Role 11, Start With the Problem (argument order). Blind pass, round 2. Artifact: docs\methods\coordination_pipeline_methods.md (commit 464d995). I read the whole file and used Grep to confirm first-use positions for mode, sliding, fitting pool, minimum cells, synchronous frames, TTX, senktide and crowding.

**Arc used.** Dependency order, which fits a methods section better than problem-first: input → constructed test material → instruments → yardstick → tuning → learned models → comparison → application → downstream measure.

**Cold open.** Lines 7–10 define coordinated event, detector, call, and coded vs learned detectors. Then §1 opens on the detected event data. That is what the PI asked for first. For a methods section, opening on the input is the right cold open, and the four definitions it front-loads are all used before §3. No finding.

## Spine (one claim per section)
0. Preamble: a coordinated event is cells firing within about 1 s more often than chance. Detectors report such events as calls; coded detectors are hand-written rules and learned detectors are trained networks.
1. Detected calcium events: the input is the imaging pipeline's per-event export (84 recordings, 2,630 ROIs, 168,755 fast events, 44 mice). The producer applied the exclusions; the analysis adds none. Each period has one analysis window.
2. Synthetic recordings: detectors are tuned on synthetic recordings with known planted events. The constants come from earlier lab data and hold on re-measurement (Table 2). Three test recordings target specific failures.
3. Coded detectors: six rule-based detectors, each with its mechanism and origin, validated against MATLAB or cSPIKE.
4. Scoring: calls match planted events within 2.5 s. The objective is the mean F1 over two backgrounds, and a setting must be admissible under Table 3.
5. Optimization: a coordinate search plus two-parameter grids was run on seeds 1–48 and held out on 49–96. Only CoactDetect and LoCo changed (Table 4).
6. Learned detectors: four small architectures read a binary raster and output a per-frame probability. They are trained on 10 benchmark recordings and decoded by a threshold.
7. Comparison: coded and learned detectors are compared under nested 4-fold cross-validation with two selection rules, a replication, and a descriptive separability bar.
8. Analysis of recorded data: the Table 4 coded settings plus one learned detector run on 67 recordings (baseline vs first treatment). Rates are in calls per minute.
9. Width and amplitude: one rule for all detectors takes width and amplitude from the recorded events inside each call.

Overall the order is sound. Every section depends only on the sections above it, apart from the items below. None of them calls for moving a whole section; they are misplaced paragraphs and forward references.

## Findings (location · issue · severity · suggested fix · verified)

1. **§1, Table 1 caption and columns (l.28–37), and the "analysed" wording at l.48.** The analysed population (67 recordings whose first treatment was TTX or senktide) is used here but defined only in §8, "Recordings analysed" (l.353–357). TTX and senktide are used at l.29/31 but spelled out only at l.354–355. That is a backward dependency, an abbreviation used before it is defined, and an explicit forward pointer ("see *Analysis of recorded data*"). · **Moderate** · Move the "Recordings analysed" paragraph and the window-length sentence (l.356–357) into §1, next to Table 1 and "Periods and analysis windows". Define TTX and senktide there. §8 then needs only a one-line back-reference. It is a description of the data, and the PI's item 1 is where he expects it. · yes

2. **§2 Distractors (l.87–88).** "precision 15/21 and F1 0.83" uses precision and F1 two sections before §4 defines them (l.199–201). · Minor · Move the cap sentence into §4 after the F1 definition ("Distractors cap the attainable score: …"), leaving §2 to say only that distractors are labelled negatives and cannot be told apart from 18% events. · yes

3. **§2 Close-events test (l.133–135).** It uses CoactDetect (introduced at l.149) and "merges calls over long gaps" (merge gap, introduced at l.140) before either exists. In the same paragraph, "crowding above 0.38" appears before crowding is defined in the next sentence. · Minor · Define crowding before it is used. Either turn "CoactDetect" into "one of the coded detectors described below", or accept the forward reference and say it ("CoactDetect, below"). The spacing's provenance could also sit beside Table 3, where the close-events limit is used. · yes

4. **§3, mode never defined (first use l.180–182; then l.212, 223, 240–243, Table 4, l.302).** "Binned mode" vs "sliding mode" for CoactDetect and LoCo is never explained. The detector bullets (l.149–157) describe one window each and never say a detector has two modes. Yet §5's headline result is defined relative to "sliding mode at the default values", and the Table 3 close-events limit is defined relative to "the default in binned mode". A reader cannot evaluate either. · **Major** (the section that relies on it most is where the only adopted changes are) · In the CoactDetect and LoCo bullets, add one sentence each on what binned and sliding mean (non-overlapping bins vs a window stepped every frame, or whatever it actually is) and which is the default. · yes

5. **PI item 7, "the knobs for each detector", has no home (§3 and Table 4).** Knobs appear piecemeal. Several reach the reader only as Table 4 values, with no statement of what they do: minimum cells, rate window, synchronous frames, surrogates, mode. The searched grids are never given, although §5 relies on them ("varied over its grid", "extended"). The learned-detector knobs (learning rate, training length, architecture size) appear only inside §7 (l.303). This is the one PI item the dependency order dissolved rather than moved. · **Major** (an item the PI asked for by name is only partly answered, and not in one place) · Close §3 with a table of knobs: detector · parameter · what it controls · default · grid searched. Put it before Scoring/Optimization so §5 can refer to it; Table 4 stays the chosen values. Add the learned-detector search space to §6 (it is currently in §7). · yes

6. **§6 Training (l.284): "fitting pool".** This is undefined. What it is appears only in §7 (the three tuning folds; "a learned refit fitted on 10", l.333). A reader of §6 cannot tell where the 10 recordings or the "two further recordings" come from. · Moderate · In §6, say that fits draw from the tuning folds defined in §7 (forward reference stated). Alternatively, define the pool in §6 as "the tuning recordings of a cross-validation fold (below)". · yes

7. **§6 Decoding (l.292) and Architectures (l.268).** "except under the false-alarm rule below" and "configurations searched" both point into §7. Stated forward references are acceptable, but they show that §6 is incomplete on its own. The learned models' selection lives entirely inside the comparison, and the §8 model comes from §7's replication. · Minor · Keep §6 → §7, but add one opening sentence to §6: "Configuration, threshold and merge gap were selected inside the cross-validation of the next section." That turns an unstated deviation into a stated one. · yes

8. **§4, "default setting" (l.205–206).** This is defined in Scoring although it belongs to the detectors. It is needed there for Table 3's limits, so the position is defensible. The only issue is placement: a reader looking for "what are the defaults" in §3 will not find them. · Minor · If finding 5's knob table is added, it carries the defaults and §4 can point to it. · yes

9. **§8 window-length sentence (l.356–357).** "Baseline windows are 17–20 min; first-treatment at least 12 min." This describes the analysis windows defined in §1 (l.53–57) and arrives six sections later. · Minor · Move it to §1 "Periods and analysis windows" (goes with finding 1). · yes

10. **§7 Comparison is not on the PI's list.** It is an addition. It is justified: it is how the learned models were configured and selected, and the one learned detector in §8 depends on it. But the PI did not ask for it. · Minor (disclosure) · State it in the delivery note to the PI, not in the manuscript. · yes

## Is departing from the PI's list justified?
Yes. The PI's order puts "optimize coded detectors" (item 3) before the benchmark (5), scoring (6) and knobs (7). But optimization cannot be followed without the objective, the admissibility limits, the benchmark seeds and the parameters it moves. His item 4 (training) likewise needs the benchmark and the scoring rule. Dependency order is the only order in which each section can be judged where it arrives.

The departure is stated in the brief to reviewers but not to the PI. Say it in the cover note: "reordered so each step's inputs precede it; your nine items map as follows". It does not belong in the methods text itself.

## PI's nine items: answered, and where
| # | PI item | Where | Answered? |
|---|---|---|---|
| 1 | detected calcium event data | §1 | yes (but the analysed population is stranded in §8; finding 1) |
| 2 | synthetic data sets | §2 | yes |
| 3 | coded detector optimization | §5 | yes (depends on the undefined mode; finding 4) |
| 4 | model training | §6, completed in §7 | yes, split across two sections (findings 6, 7) |
| 5 | the benchmark and how it was determined | §2 (benchmark recording, "Origin of the constants", Table 2) | yes |
| 6 | scoring parameters | §4 | yes |
| 7 | knobs for each detector | scattered across §3, Table 4 and §7 | **partly**: no per-detector list of knobs, meanings or grids (finding 5) |
| 8 | real data assessment | §8 | yes |
| 9 | universal amplitude and width | §9 | yes ("one rule for every detector") |

## Section table (job · earliest intelligible position · verdict)
| section | job in the argument | earliest intelligible position | verdict |
|---|---|---|---|
| Preamble | define the four terms everything uses | 0 | stays |
| §1 Detected events | the input and its provenance | 1 | stays; should absorb the analysed-population and window-length paragraphs from §8 (findings 1, 9) |
| §2 Synthetic recordings | ground-truth test material, shown to match the data | after §1 (it uses baseline windows and rates) | stays; move the F1-cap sentence to §4 and fix the close-events forward references (findings 2, 3) |
| §3 Coded detectors | the instruments | after §2 (validation cites the benchmark) | stays; needs the mode definition and a knob table (findings 4, 5) |
| §4 Scoring | the yardstick and admissibility | after §3 (interval rules are per detector) and §2 (test recordings) | stays |
| §5 Optimization | tune the instruments against the yardstick | after §4 | stays |
| §6 Learned detectors | the second family of instruments | after §4 (thresholds maximize F1) | stays; state that selection happens in §7 (findings 6, 7) |
| §7 Comparison | coded vs learned under cross-validation; picks the learned model used downstream | after §5 and §6 | stays; disclose it to the PI as an addition (finding 10) |
| §8 Recorded data | apply the chosen detectors | after §5 and §7 | stays, minus the population paragraph (move it to §1) |
| §9 Width and amplitude | downstream measure per call | after §8 | stays, last |

No section needs to move. Two paragraphs do (findings 1, 9), and one sentence does (finding 2). The two major findings are about content that is missing from where it should be: the mode definition and the per-detector knobs. Nothing is simply in the wrong order.

---
*Transcription note: personal absolute paths were replaced with placeholders (sapper SAP004); nothing else was altered.*
