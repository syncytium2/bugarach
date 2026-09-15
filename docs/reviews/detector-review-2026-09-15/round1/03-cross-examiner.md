> **Public copy.** Lines that concern real treatment recordings are removed (14 here), per FOUNDATIONS §5, and machine paths are shortened to `<scratchpad>`, `<worktree>`, `<darkroom>` or `<home>` (sapper SAP004). Everything else is verbatim.

GRANT 3 ok — Read, Grep, Glob

*[line removed from the public copy: it concerns real treatment recordings (FOUNDATIONS §5); the verbatim report is in the darkroom delivery folder]

## Findings

### High

| # | Location | Issue | Fix | Verified? |
|---|---|---|---|---|
| [line removed from the public copy: it concerns real treatment recordings (FOUNDATIONS §5); the verbatim report is in the darkroom delivery folder] |
| 2 | §5 Strengths "The fastest detectors here once trained" vs Table 1, §8 | Table 1 contradicts it. tube is about 18,000× faster than real time, and tube_ratio (9,786×) is the slowest of all twelve, which §8 itself says. rate+context is 536,163×, binned SCE 166,570×, trace 148,799×. | Delete the claim, or replace it with the measured speeds. | yes |
| 3 | §8 third tuning flaw ("nothing stopped rate+context…") vs Fig 11C, `numbers.json` | Two other detectors also chose settings that break their limits, and the red ✕ marks in Fig 11C show both. SPIKE-synch picked 0.04 in all 4 rounds, and 0.04 is over its limit. locust picked 99.9 in 2 of 4 rounds, also over. That is why SPIKE-synch ends up over its limit (1.05 per minute). Naming only rate+context contradicts the figure beside it. | Name all three, or say "rate+context, SPIKE-synch and (in two rounds) locust". | yes |
| [line removed from the public copy: it concerns real treatment recordings (FOUNDATIONS §5); the verbatim report is in the darkroom delivery folder] |
| [line removed from the public copy: it concerns real treatment recordings (FOUNDATIONS §5); the verbatim report is in the darkroom delivery folder] |
| 6 | §6 "Planted events are at least 120 seconds apart, so that no detector's chance estimate contains a second planted event" vs §4.4, §4.5 | binned SCE and locust build their surrogates from the whole recording, which holds all 15 planted events. The statement is false for 2 of the 6. | "…so that no rolling detector's nearby window contains a second planted event." | yes (`bench.py` 378–383, 425–430) |
| 7 | §5 "We trained each one on 18 simulated recordings… chose the output level… using simulated recordings the network had not trained on" | Read literally, the only untrained recordings are the 6 scored ones, which would make §8's "not tuned or trained on" false. In the code, 2 of the 18 are held back to choose the call level (`fold_maker`, `n_val=2`) and training uses at most 10 of the other 16. | "trained on 16 of the 18 and chose the call level on the other 2." | yes (`learn/train.py` 67–97; generator 139–146) |

### Medium

| # | Location | Issue | Fix | Verified? |
|---|---|---|---|---|
| 8 | Fig 10 A1/B vs Fig 1B, Figs 3–9; §6 "the bench" | Two different simulated recordings are both called "the bench recording". Figs 1B and 3–9 use seed 3, with a planted event at 491.9 s. Fig 10A1 has an event at 513 s (`gen_zoom_event`) and none at about 492 s. Planted events are at least 120 s apart, so these cannot be the same recording. §6 also defines the bench as one recording, yet 24 are scored. | Call the bench a recipe. Say which recording (seed) each figure shows. | yes |
| 9 | Fig 10 caption "The fitted simulator is closer to real than the flat one" | At 30 s it is not. Real is 1.39, fitted 1.86 (0.47 off), flat 0.97 (0.42 off). Fitted is only closer at 60 s and above. | "closer at 60 s and above; at 30 s both are about equally far off." | yes |
| 10 | §7.1 "a detector may not exceed its own limit (Section 7.3)" vs §7.2, §8 | The page states a rule that is never applied: rounds choose by F1 alone, and rate+context and SPIKE-synch exceed their limits. The companion doc does the opposite: `bench.pick_operating_point` does check the limit (`bench.py` 1119–1124). | "we report whether a detector exceeds its limit; the rounds do not enforce it." Say the bake-off differs from `bench.pick_operating_point`. | yes |
| 11 | §12 "All six hand-written detectors were first written in MATLAB in the same lab… matched… one part in a billion" | This contradicts §12's own credits: locust comes from the Cossart lab's CICADA, SPIKE-synch from Kreuz/PySpike. The glossary says locust's 1e-9 parity reaches interface2's `generate_sce_cicada`, not the Cossart source. | "Python ports of the lab's MATLAB versions, which matched those…". Do not say "first written". | yes (GLOSSARY lines 82–89) |
| [line removed from the public copy: it concerns real treatment recordings (FOUNDATIONS §5); the verbatim report is in the darkroom delivery folder] |
| [line removed from the public copy: it concerns real treatment recordings (FOUNDATIONS §5); the verbatim report is in the darkroom delivery folder] |
| [line removed from the public copy: it concerns real treatment recordings (FOUNDATIONS §5); the verbatim report is in the darkroom delivery folder] |
| 15 | Table 1 "calls per minute in the busy block" and "speed" columns | Unlike the recall and precision columns, neither says which background. Values exist for both: SPIKE-synch is 1.05 quiet but 1.59 busy, rate+context 5.3 quiet but 1.08 busy. | Add "quiet" to both headers. | yes |
| 16 | §8 prose vs Table 1 vs Fig 12B: busy-block rates | The same quantity is shown at different precision, and the table disagrees with the prose and figure. Prose gives CoactDetect 0.17, LoCo 0.31, SPIKE-synch 1.05, tube_guard 1.01, ratio models 0.01 and 0.02. The table shows 0.2, 0.3, 1.1, 1.0, 0.0 and 0.0. trace shows 0.0 in the table but about 0.04 in Fig 12B, above both ratio models. tube_ratio (0.008) is drawn at the floor, like tiny (0), so it looks like "no calls". | Use two decimals in the table, or quote the table's values in the prose. | yes |
| 17 | §8 "binned SCE is the one exception: its score rose" | trace also rose, from 0.23 to 0.25. In the same paragraph, "best mean scores at busy… tube 0.64" leaves out tube_guard's equal 0.64. | Say "the one hand-written exception", or name trace too. Add tube_guard. | yes |
| 18 | Section 10 table, binned SCE row vs LoCo row | LoCo's row says "best setting may lie past the end of the list". binned SCE's row does not, although §8 says binned SCE's curve is "still rising" there and LoCo's is flat. The detector more likely to be affected gets no warning. | Add the same caveat to binned SCE. | yes |
| 19 | Fig 9 lanes vs `numbers.json` | trace and tiny each have 1 call in window A and 1 in window B, yet their lanes in Fig 9B and 9C are empty. `tiny_bench_seed_score` has only 1 call in total, so it would have to span both windows and would appear as a long bar. The Fig 9C caption also leaves out their calls in the busy block. | Draw the calls, or fix the counting and say what those numbers mean. | yes for the mismatch, no for its cause |
| [line removed from the public copy: it concerns real treatment recordings (FOUNDATIONS §5); the verbatim report is in the darkroom delivery folder] |
| 21 | Fig 11C x-axis labels | The axes show code names the page never defines (`excess_threshold_hz`, `alpha`, `threshold_pctile`, `sce_percentile`, `C_threshold`). locust's panel reads `sce_percentile`, which suggests binned SCE, and the code name leaks through contrary to the locust/CICADA naming rule. | Label in the page's words, for example "bar percentile". | yes |
| 22 | New terms not in the glossary | "decoy" (glossary: distractor), "busy block" (promiscuity probe), "limit" (ceiling in `MAX_PROBE_PER_MIN`), "background level" (regime), "round" (fold), "call level" (threshold). The rule is that new terms go into the glossary in the same change. | Add a mapping to `docs/GLOSSARY.md`, or use the glossary words. | yes |

### Low

| # | Location | Issue | Fix | Verified? |
|---|---|---|---|---|
| 23 | Fig 6 caption "19 bins in this window pass it" | The lane shows 18 bars with ✕. The 19th is probably a partial bin at the left edge (count 11 visible at 21m30s). | Count whole bins, or explain the edge bin. | partly (by eye) |
| 24 | Fig 11C caption "Blue square: the value the detector ships with" | SPIKE-synch ships at 0.1, which is not on its list (0.005–0.12), so its panel has no square. | Note this in the caption, or add 0.1 to the list. | yes |
| 25 | Fig 12C caption "one line per detector" | The panel shows dots grouped by size, not lines. The legend also covers LoCo's 10% dot (about 0.48). | Fix the caption; move the legend. | yes |
| 26 | Fig 12A title "(learned: one round per training seed)" vs caption "three dots per round, one per training run" | Two different descriptions of the same dots. | Use one wording. | yes |
| 27 | §8 "Scores… differ from round to round by more than these five differ" vs §11 "by about as much as" | The two sections give different strengths for the same comparison. | Use one. | yes |
| 28 | §8 "For LoCo the curve is nearly flat there; for binned SCE it is still rising" | In Fig 11C binned SCE is also nearly flat at the low end (0.452 at 75, 0.445 at 80 and 85). It is only "rising" when read from 99.9. | "binned SCE rises steadily toward the low end" or "both are nearly flat". | yes (figure) |
| 29 | Fig 10C x-axis "log₁₀ Hz" vs §2, §6, Fig 10 A labels in mHz | The same quantity is given in two units with no conversion, against the plot rule. | Label in mHz, or give the conversion. | yes |
| [line removed from the public copy: it concerns real treatment recordings (FOUNDATIONS §5); the verbatim report is in the darkroom delivery folder] |
| [line removed from the public copy: it concerns real treatment recordings (FOUNDATIONS §5); the verbatim report is in the darkroom delivery folder] |
| [line removed from the public copy: it concerns real treatment recordings (FOUNDATIONS §5); the verbatim report is in the darkroom delivery folder] |
| 33 | ▼ meaning | ▼ means "planted event" in Figs 1B, 3–11 but "bins that pass each bar" in Fig 2C. In Figs 3–8, the green used for "found" is also binned SCE's call and trace color, and red ("missed") is SPIKE-synch's. | Use another mark in Fig 2C, or say so in its caption. | yes |
| [line removed from the public copy: it concerns real treatment recordings (FOUNDATIONS §5); the verbatim report is in the darkroom delivery folder] |
| 35 | §4 layout paragraph | Does not explain the tan shading of the busy block in the lanes of Figs 3–9 (Fig 2C and 10 captions do). | Add "shaded: the busy block". | yes |
| 36 | §2 "Bar: The count a detector's measure must pass" | SPIKE-synch's bar is a score (0.1) and rate+context's is in events per second, so not counts. | "The value…". | yes |
| 37 | Tables | Only Table 1 is numbered. The Section 4 summary table and the Section 10 table are not. | Number all three. | yes |
| [line removed from the public copy: it concerns real treatment recordings (FOUNDATIONS §5); the verbatim report is in the darkroom delivery folder] |
| 39 | Fig 10B "10 ROIs (30%) take part" | I can make out about 8 separate ticks; some may merge vertically. | Check the render. | no |
| 40 | Fig 12B y-axis label | Clipped: "…where nothing was plant". | Shorten or widen. | yes |

## What I checked

- **Figures:** all 16 PNGs, against their captions and the prose. Figure numbering runs 1–16 in order of first mention.
- **Numbers:** every number in the prose and in Table 1, against `numbers.json` and `table_performance.html`.
- **Cross-references:** every Section and Figure reference resolves.
- [line removed from the public copy: it concerns real treatment recordings (FOUNDATIONS §5); the verbatim report is in the darkroom delivery folder]
- **Glossary terms:** modality, corpus and bare "adaptive" are absent (the only "Adaptive" is a paper title); locust and CICADA are used correctly. Bare "settings", K and "analysis window" are misused.
- **Companion constants:** limits, operating points, regimes and bench layout checked against `src/bugarach/bench.py`; also `detect_folder.py`, `cicada.py`, `learn/train.py`, and the generator's training and selection code.

Files:
- <scratchpad>\review\detector_review_plain.txt
- <scratchpad>\review\_work\numbers.json
- <worktree>\tools\make_detector_review.py
- <worktree>\src\bugarach\bench.py
- <worktree>\src\bugarach\learn\train.py
- <worktree>\src\bugarach\detectors\cicada.py
- <worktree>\docs\GLOSSARY.md
