GRANT 8 ok — Read, Grep, Glob

Role 8, You Lost Me. Artifact: `<worktrees>/chorus-collapse/docs/learned/chorus_collapse/index.html`, the built page.

**I did not see the page rendered.** I have no Bash, so I could not run `<scratch>/shoot.py`. Everything below comes from the page text, the inline SVG markup (`<text>`, `<title>`, polyline coordinates) and the captions. The "what a cold reader sees" sentences describe what the markup draws, so they carry `verified: no` on the rendered view. Agent 10's render should confirm them.

## Per-section and per-figure verdicts

| # | Place | Terms first used here | Defined here | Can a cold reader follow? |
|---|---|---|---|---|
| 1 | Title and subtitle | chorus_norm, fits, fair comparison, coded detectors, learned nets, goal 2, runs, training runs replayed, starting points | goal 2 (in parentheses); chorus_norm in the next paragraph | yes (minor: "coded detectors") |
| 2 | Intro paragraph | chorus_norm, chorus_gain_norm, coordinated events, ROI, frame, score, logit, threshold, call, F1, planted events | all of these except **what makes chorus_gain_norm different** | yes, with F2 |
| 3 | "The answer" box | inner fits, configurations, refits, encoder, encoder's shape, head, flat start, "second run", plain chorus, PR #596, held-out scores, out of contention | collapsed, learning rate (lr), head, warm-up | **BLOCKING.** Seven or more undefined: inner fits, configuration, refit, encoder / encoder's shape, "second run" (the body calls it a draw), plain chorus, PR #596 |
| 4 | §1 The problem | configuration, encoder width and depth, top m, nested cross-validation, outer fold, inner folds, inner fits, refit, draws, training seed | all except encoder (§3); the fold structure is ambiguous (F7) | no (major, F7) |
| 5 | Figure 1 | planted events, calls, output logit, 1-second bin envelope, threshold as a logit | yes | yes |
| 6 | §2 and Table 1 | encoder shape "4 × 6", grid, shuffle test, p, risky configuration, step-count twins | yes; the Table 1 header gives "units wide × layers deep" | yes |
| 7 | Figure 2 | share of 36 inner fits, learning-rate rows | yes | yes (hover text is hashes, F8) |
| 8 | §3 Where the signal stops | shared encoder, standardize, **vote per ROI**, pooled statistics, head, GELU, Adam, β1/β2, census, silent, **threshold grid (0.0001)**, d, **"Round 1 of this page's review"**, **dead**, **sign test** | encoder, head, GELU, census, silent, d | **BLOCKING.** Undefined or misleading: vote, threshold grid (and which unit it is in), review round / "dead", "sign test" (F3, F4, F5) |
| 9 | Figure 3 | smallest share of varying units, output SD (log scale), hollow floor | mostly; "silent" is not on the figure | yes (minor, F10) |
| 10 | Figure 4 | event separation d at the input and at the output, identity line | d defined; "input channels" is not tied to §3 | yes (minor, F11) |
| 11 | §4 When it happens | replayed exactly, checkpoint, sibling, as run, batch, stalled, chosen by hand, `e86433df`, shorter twin, dormant, 2/(1 − β2) | most; checkpoint is standard ML | yes (minor: a hash in the prose, F8) |
| 12 | Figure 5 | silent head layers (of 8), training step, "as run" | yes | yes |
| 13 | Figure 6 | training loss, mean of 5 logged steps, warm-up (solid vs dashed) | yes | yes (minor, F12: no reference level) |
| 14 | Figure 7 | trains / does not train, loss 0.5 | yes | yes |
| 15 | Table 2 | top m, collapse share, final loss, configuration (the values are hashes) | the note defines final loss and "trains" | yes (minor, F8) |
| 16 | §5 and Table 3 | inner selection, † flag, grid floor, trainer, untuned default configuration | yes | yes (minor, F15, F20) |
| 17 | §6 Limits | distinct collapsed runs | — | yes (minor, F16) |
| 18 | §7 Where everything is | paths, branch, `--code`, `replay` | n/a: a locations section, where identifiers belong | yes |
| 19 | References | — | — | yes |

## What a cold reader sees, caption covered

These are inferred from the markup, not from a render.

- **Figure 1.** Three thin lanes across the top. The first has downward triangles for the planted events. The second has short spans for the working fit's 23 calls. The third has one bar across the whole width for the collapsed fit's single call. Below the lanes are two stacked traces against a 0–45-minute axis. The upper trace is jagged and spikes above a dashed line at each triangle. The lower one is perfectly flat near the top of its panel (y coordinate constant at 240.4 in the markup), with its dashed line at the very bottom. This is readable, and the full-width bar tells the story at a glance. Chart-type check: the lanes and trace follow the lane-above-trace convention, and the axes mean time and logit, as that idiom expects. **Passes.** One thing for the render to check: if the min-to-max envelope is a *filled* polygon, it could read as a confidence band.
- **Figure 2.** Two panels, A chorus_norm and B chorus_gain_norm. Each has three rows (learning rate 0.003, 0.01, 0.03) of dots along a 0–1 axis labelled "share … that collapsed", with "n of N fits" at the right of each row. In A the two lower rates sit at 0 and the 0.03 row sits at about 0.4–0.9. In B the 0.03 row spreads from 0 to about 0.9. Readable. Chart type: a dot or strip plot, used as that idiom expects. **Passes.**
- **Figure 3.** Two scatter panels. The x-axis runs 0–1 in columns at eighths, slightly jittered. The y-axis is output SD on a log scale. Orange dots pile into the x = 0 column, and many sit hollow on a floor line. Blue dots sit high and spread from about 0.25 to 1. Readable, but the page's key word, *silent*, appears nowhere on the figure (F10). Chart type: a scatter. **Passes.**
- **Figure 4.** Two scatter panels with "event separation (d)" from 0 to 12 on both axes and a dashed diagonal. Blue dots sit around or above the diagonal. Orange dots lie along the bottom at x ≈ 1–3. Readable. Chart type: a scatter with an identity line. **Passes.**
- **Figure 5.** One plot of "silent head layers (of 8)" against training steps 0–1,600. A blue line stays at 0 throughout. An orange line sits at 0 and then, from about step 230, flickers between 1 and 2. Readable. **Passes.**
- **Figure 6.** Six loss curves against training step, some solid and some dashed. Several fall from about 1.5 to about 0.1 within a few hundred steps, and some stay flat near 1.5. Readable only by comparison between curves: nothing marks what "not training" looks like (F12). **Passes** the chart-type check.
- **Figure 7.** Eight loss curves over 0–3,000 steps with a dashed line at 0.5. Seven fall well below it and one stays near 1.7. Readable. **Passes.**

**Chart-type (false-friend) check:** none of the seven figures borrows an idiom while giving its axes a different meaning.

## Findings

Format: location · issue · severity · suggested fix · verified

- **F1** · "The answer" box · **Blocking.** A stranger starts here and meets seven or more undefined terms in five bullets: inner fits ("146 and 153 of chorus_norm's 432 inner fits"), configuration, refit, encoder / encoder's shape, "second run" (the body says "second draw"), plain chorus, PR #596. The definitions arrive in §1–§3, after the reader has already been lost. · Define in place with a short gloss or pointer, e.g. "inner fits (the trainings used to choose settings, §1)", "refits (the final trainings scored on held-out recordings)". Or put a three-line terms strip above the box. Say "draw", not "run". Replace "PR #596" with "an earlier diagnosis of the plain chorus net (§7)". · verified: yes (page text)
- **F2** · whole page: intro, box, §2, §3 · **Major.** The page keeps contrasting chorus_norm with chorus_gain_norm ("chorus_gain_norm is different: its encoder's shape matters…") and with "plain chorus". It never says what separates the three nets. §3 describes chorus_norm's architecture only. A stranger cannot guess why the two nets behave differently, or what "norm" and "gain" mean. · Add one sentence in the intro saying what chorus_gain_norm adds to chorus_norm and what plain chorus lacks. · verified: no (I cannot check the architecture against source)
- **F3** · §3 ("lowest value on the threshold grid (0.0001)") against Figure 1 ("threshold, −9.2") · **Major.** The intro says thresholds apply to logit scores. §3 then gives the collapsed threshold as 0.0001, while Figure 1 labels the same threshold −9.2. The page never says the grid is in probability, and never defines "threshold grid". A reader sees two numbers for one threshold. · Write "the lowest threshold training could choose, probability 0.0001 (logit −9.2)". Define the grid once, in the intro sentence about thresholds. · verified: yes (logit(0.0001) = −9.21; page text)
- **F4** · §3, the paragraph beginning "Round 1 of this page's review counted a layer as dead…" · **Major.** This is review-process history inside the argument. It points to a review the reader never sees, brings in a retired term ("dead") beside "silent" and, later, "dormant", and calls a check for positive outputs a "sign test". To a statistician that is a false friend: it is the name of a specific nonparametric test. · Cut the paragraph, or move it to §6 as "an earlier criterion (a unit that never exceeds 0.001) counted 152 collapsed and 1 working; it misreads GELU's negative dip". Drop "sign test". · verified: yes
- **F5** · §3, "turns it into a vote per ROI" · minor · "Vote" is never defined: what quantity is it, and at what time resolution? · Say what the vote is, e.g. "one score per ROI per frame". · verified: no
- **F6** · "run" used for three different things: subtitle, box, §1, §4, §6 · **Major.** "Two runs of goal 2" means draws. "14 training runs were replayed" and "6 of 7 distinct runs train" mean single trainings. "Goal 2 was run twice". The box says "In the second run" where the body says "second draw". The page's own reconciliation ("calls the two runs draws") comes after the box has already used "run". · Use "draw" for the two goal-2 repetitions everywhere, subtitle and box included. Use "fit" or "training run" for single trainings. · verified: yes
- **F7** · §1, fold structure · **Major.** The text reads "Inside each outer fold, every configuration is trained at 3 training seeds on each of the 6 pairs of 4 inner folds … 432 per net per run." But 24 × 3 × 6 = 432 already, with no outer-fold factor, and Figure 2's "36 = 3 × 6 × 2 draws" agrees with that. A reader who takes "each outer fold" to mean several outer folds cannot rebuild the headline denominator. Table 3's note ("in every fold", 40 default refits) adds to the doubt. "6 pairs of 4 inner folds" also reads as six groups of four. · State how many outer folds there are, and whether the 432 are per outer fold or once per draw. Rephrase as "on each of the 6 ways to pick 2 of the 4 inner folds, scored on the other 2". · verified: yes against the page's own arithmetic; no against the run
- **F8** · internal identifiers in text the audience reads · minor · Prose in §4 has "(e86433df)". Table 2's "configuration" column holds hashes ("2736f584, training seed 1"). Hover titles in Figures 2, 3, 4 and 7 are hashes, and Figures 3 and 4 add an undefined abbreviation, "recs 3a17721a7a". · In prose, name the configuration by its settings ("the 8 × 6, top-2, 3,600-step configuration, seed 2"). Rename the Table 2 column "configuration ID". In hover text, replace "recs <hash>" with "fold pair k of 6". · verified: yes
- **F9** · snake_case net names (chorus_norm, chorus_gain_norm) in the title and throughout · minor (judgment call) · These are registered code names doing the work of model names. · Keep them, but say once that they are the nets' names in the code, or render them as "chorus-norm". · verified: yes
- **F10** · Figure 3 · minor · The headline term "silent head layer" is not on the figure. The reader has to work out that x = 0 means a silent layer. · Label the x = 0 column "a silent layer", or add "(0 = at least one silent layer)" to the axis label. · verified: yes (markup)
- **F11** · Figure 4 and §3 · minor · d is "the largest standardized difference … over its input channels". "Channels" is not connected to the three pooled statistics §3 describes, and the page does not say what the difference is standardized by. · Write "over the head's three input statistics; d = difference of means ÷ pooled SD", or whichever SD is actually used. · verified: no
- **F12** · Figure 6 · minor · There is no reference level. The reader learns what a constant output's loss is (≈1.4) only from Table 2's note, after Figure 7. · Draw the 0.5 line as Figure 7 does, or a "constant output ≈ 1.4" line, and say so in the caption. · verified: yes
- **F13** · §1 prose on Figure 1 · minor · "Sits far above the fit's threshold" does not say why the collapsed threshold is so low (−9.2). That is explained two sections later. · Add a half-sentence pointer: "(its threshold is the lowest training allowed; §3)". · verified: yes
- **F14** · §4 against §6 · minor · §4 says "6 of 7 distinct runs train" and §6 says "8 distinct collapsed runs". The reader sees 7 and 8 with no bridge. · Write "8 (the Figure 1 fit and 7 others)". · verified: yes (page text)
- **F15** · §5, list of refits that collapsed · minor · "chorus_norm, second draw, lr 0.01; chorus_norm, second draw, lr 0.01" looks like a duplicated typo. · Write "two chorus_norm refits, second draw, both at lr 0.01". · verified: yes
- **F16** · §3, "lr 0.03 is 30 times the step size that paper suggests" · minor · The reader has to back out 0.001 themselves. · State "(0.001)". · verified: yes
- **F17** · subtitle · minor · "Coded detectors" is undefined. · Write "hand-written detection algorithms", or whatever is accurate. · verified: yes
- **F18** · §5, "The census holds the second draw's 3" · minor · "Holds" is unclear. · Write "The census includes the second draw's 3 collapsed refits". · verified: yes

## Tone and sentence case

**Passes.** Headings, bold lead-ins, legends, axis labels and table headers are all in sentence case. There is no all-caps or scattered-capitals emphasis. List content is formatted as lists. The "·" separators ("working fit · logit", "A · chorus_norm") follow the house identity · unit style; they are not list items hidden in a label.

## Outside my role, noted only

- §4 cites Figure 6 before Figure 5 (reading order): agents 3 and 11.
- Figure 1's collapsed-call hover reads "from 0, 2693.8 s long" in raw seconds instead of the 44m54s house style: agent 10.
- Figure 1's working-panel y-ticks are only −20 and 13: agent 10.
