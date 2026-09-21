GRANT 8 ok — Read, Grep, Glob

# Role 8, "You Lost Me" (naive-reader accessibility): round 1

**Artifact:** `%USERPROFILE%\bugarach\bugarach-worktrees\replicate-report\docs\learned\tuned_vs_coact\replicate1\report.html`

**Render read:** `...\scratchpad\shots\light_1100_00.png` through `_07.png`, all 8 slices, top to bottom. I checked the HTML source only in three places:
- the Figure 1, 4, 5, 7 and 8 captions, where text was cut between slices;
- the Figure 5 fill opacities;
- whether any text explains the Figure 1 crosses. None does.

**Reader simulated:** a scientist or engineer who knows calcium imaging and neural networks in general, and knows nothing about this lab, its bench simulator, its goals or its runs.

**Summary:**
- 25 rows below: 9 blocking, 7 "no", 9 "yes".
- One real false friend: Figure 5 reads as a heatmap strip. Two figures have a mark a stranger cannot explain: Figure 1's red crosses and thick ticks, and Figure 8's invisible zero bars. Figure 6 has a hidden-tick problem that could be read as a false data point.
- Nine vocabulary problems span the whole page (C1–C9), and they matter more than any single row. The two worst: **WSMIP064/WSMIP065 are never defined** yet name the two draws everywhere, and **"seed" has three meanings**.

---

## A. Per-section / per-figure verdicts

Column "Undefined here" lists terms a stranger meets in that unit without a definition on the spot. "(fwd)" means it is defined later in the page. Reading a forward reference still requires the stranger to jump ahead, so it counts.

| # | Unit | Terms / identifiers first used here | Defined here | Undefined here | Cold reader follows? |
|---|---|---|---|---|---|
| 0a | Title + subtitle | draws, "the fair comparison", goal-2, learned / coded detectors, WSMIP064, WSMIP065, seeds 1000–1047 / 2000–2047, replicate, fast stream, baseline | none | all ten: "draw", "the fair comparison" (relative word: fair compared with what?), goal-2, WSMIP064, WSMIP065, seeds, replicate, learned/coded (fwd §3), fast stream (never really defined), baseline (fwd §2) | **BLOCKING** |
| 0b | "The answer, first." box | false-alarm budget, CoactDetect, budgeted net, chorus_gain_norm, F1, untuned, chorus_norm, "leading net", entry ("median over 20 entries"), rehearsal run | none | budget (fwd §5), CoactDetect (fwd §3), chorus_gain_norm / chorus_norm (fwd Fig 2, and they are code identifiers), F1 (fwd §2), untuned (fwd §3), **entry (never defined)**, **rehearsal run (never defined)** | **BLOCKING**. This is the one box written for a reader who stops here, and it cannot be read cold. |
| 1 | §1 The problem | raster, ROI, coordinated event, field, detector | raster, ROI, coordinated event | "field" (field of view; tolerable) | yes |
| F1 | Figure 1 | seed 2000, quiet background, WSMIP065's run, planted, decoys, CoactDetect, calls, busy stretch, budget | busy stretch, planted/decoy triangles, green/red | seed, quiet background (fwd §2), WSMIP065, CoactDetect (fwd §3), budget (fwd §5); **red crosses and thick vs thin orange ticks in the CoactDetect row are not explained anywhere** | **BLOCKING** (5 undefined, plus a mark I cannot explain; see B) |
| 2 | §2 Why a simulation | bench, baseline, fast stream, recording seed, quiet/busy background, F1, precision, recall, fold | bench, baseline, quiet/busy, F1, precision, recall | **fast stream**: "the lab's two event streams are kept apart" names the streams without saying what they are. The only hint comes in §10, eight sections later. Also fold (fwd §4) and "recording seed" (inferable). | no |
| 3 | §3 The contestants | CoactDetect, LoCo, binned SCE, rate+context, SPIKE-synch, locust, shuffled versions, per-frame, nets, tube, configurations, untuned default | SCE, nets, tube's role, untuned default | "per-frame" (frame only gets meaning, 0.1 s, in the next paragraph). The six mechanisms are named in one semicolon run-on sentence with no illustration of the shuffle null that two of them rely on. | no |
| F2 | Figure 2 | max-pool, sigmoid vote, difference-of-Gaussian kernels, raw trace, encoder, standardise, "mean of loudest m", "share lit", "judge each share against its own background", dilated convolution, gain and offset, parameters | the NN terms are fine for this reader | **m** (never defined); "share lit" / "judge each share against its own background" (**"background" collides with the bench's quiet/busy background**); "three pooled views" (what the three are is only half-given) | **BLOCKING** (3). The diagram itself reads well. |
| 4 | §4 main text | nested CV, outer fold, inner fit, training seeds, refitted at 5 seeds, coordinate search, "the same grids goal 1 declared", "fixed in size inside a fold", 6 distinct fold pairs | nested CV, outer fold, inner fit, coordinate search | **training seed**: second meaning of "seed", in the same paragraph as recording seed. **goal 1**: never defined. "fixed in size inside a fold": meaning unclear. "432 = 24 × 3 × 6 distinct fold pairs": Figure 3 says × 3 fold pairs per outer fold, so a stranger computes 24 × 3 × 3 × 4 = 864 and stalls, because the de-duplication across outer folds is never said. | **BLOCKING** |
| 4c | §4 callout, "A defect was fixed…" | rehearsal run, "training reads a contiguous run of its recording list", fold order, "folds 3 and 4 (counting from 1)", round-robin, "a check that replays every fit's own draw", `fold_check`, declaration | none | rehearsal run, contiguous run of the recording list, "fit's own draw" (**a third meaning of "draw"**), `fold_check` (code identifier), declaration. Counting folds from 1 here contradicts Figure 3's fold 0–3 right below it. | **BLOCKING**. This is process history a stranger does not need. |
| F3 | Figure 3 | outer fold 0–3, inner selection, fit here / score here, refit, coordinate search | all | "48 seeds × 2 backgrounds" (fine); the orange "score here" colour is not named in the caption (the box text carries it) | yes |
| 5 | §5 Two selections… | chosen on F1 alone, chosen under the budget, ceiling, candidate, sliding, binned, "shuffled baseline", goal 1, significance level α, merge, guard, "table of shipped settings", "browser viewer", 1.6 | the two selections, ceiling, candidate, sliding | **entry** ("Every entry is chosen twice"; never defined); **goal 1**; **guard** ("a 1 s guard"); **"shuffled baseline"** (**"baseline" now means the null model, not the pre-drug stretch of §2**); "the table of shipped settings… held back for the browser viewer's sake" (insider, unreadable); **why 1.6** (never motivated) | **BLOCKING** |
| F4 | Figure 4 | reference, busy stretch, empty recording, ceilings, admissible | empty recording, admissible, ceilings | "the fold's 36 training seeds" vs "72 training recordings" in §4 (reconcilable, but it costs a pause); WSMIP065 | yes |
| 6 | §6 Why two runs | rehearsal run, declarations, `recording_seeds`, `replicate`, `--replicate 0`, "byte for byte", "stay resumable while this option was added" | none | rehearsal run (still undefined, third mention), declaration, `recording_seeds`, `replicate`, `--replicate 0`, resumable | **BLOCKING**. Five code or insider terms in one paragraph. |
| F5 | Figure 5 | recording seed (square), fold shading, "empty twin at seed + 100,000", "24 drawn configurations", training seeds 0–2, refit seeds 0–4 | square = recording seed | "empty twin"; **training/refit seeds printed directly under a row of "recording seed" squares** (the seed collision at its most visible) | no (false friend, see B) |
| 7 | §7 Results intro | entry, "its two columns" | none | entry; "its two columns" (which two? Table 1's F1-alone and under-budget columns, not named) | no |
| F6 | Figure 6 | learned (bold) / coded, untuned (nets only), held-out F1, vertical tick = mean, "defects… not draws" | most | "not draws": "draw" here means a random outcome, while the page uses "draw" for a *run*, so "not draws" reads as "not runs" | yes, with issues (B) |
| T1 | Table 1 | † / ‡ footnotes, refit seeds, "cell", admissible, starting point, WSMIP064/065 column heads | footnote marks | **"at least one of the cell's refit seeds"**: "cell" means a *table* cell in a document where "cell" has meant a neuron since §1. "starting point" (the goal-1 value; goal 1 undefined). Column heads are machine IDs, not "first/second draw". | no |
| F7 | Figure 7 | entry · selection rows, second − first, bold > 0.027 | all | Text above says "the 20 entries without a named defect", but the figure has 24 rows and 3 bold ones. A stranger cannot tell which 20. | yes, with issues |
| 8a | §8 "A tuned configuration that does not train reliably" | `75d4474550026cfa`, "failed to train", threshold at the bottom of its grid, "the tool", `tiny`, "every published run", inner selection | "failed to train" (partly) | config hash (code identifier), `tiny` (a net never introduced), "published run" (which?), "the tool" (which?) | **BLOCKING** |
| F8 | Figure 8 | refit seed, hatched = failed | yes | the two "failed" bars under the budget have zero height, so their hatching is invisible and they read as missing bars | yes, with issue |
| 8b | §8 "Coded detectors with no admissible setting" | refused, starting point, "quiet busy stretch", "ceiling near 17" | admissible (from Fig 4) | **"the quiet busy stretch"** reads as a contradiction: the busy stretch of the recording simulated at the quiet background. **"ceiling near 17"** has no unit (per hour; house rule is every number carries its unit). "starting point". | no |
| 8c | §8 "Settings at the edge of their grid" | merge gap, goal 1, crowded recordings, "goal 1's crowded check" | merge gap | goal 1; "crowded check" (only half-defined by "events as little as 6 s apart") | no |
| T2 | Table 2 | call-fusing setting, merge gap, minimum distance between calls, maximum gap | yes (title sentence) | four names for one concept; readable | yes |
| 9 | §9 What the pair can claim | rehearsal's +0.011, paired statistic | mostly | rehearsal run (fourth mention, never defined) | yes |
| 10 | §10 Limits | "decision of 2026-09-17", slow stream, `steps_excluded`, motion-correction defect, `HANDOFF-slow-comodulation-on-the-de-pinned-export.md`, `main`, Tony, "both workstations", "eight fitted constants", bootstrap intervals, crowded check | slow stream partly (only here) | date used as a label; `steps_excluded`; the HANDOFF path and `main`; **Tony** (who?); "workstations" (the first and only hint of what WSMIP06x are); "eight fitted constants"; crowded check | **BLOCKING** |
| 11 | §11 Where everything is | `<darkroom>`, meta.json, results.json, `bugarach detect --model`, tools/ paths, `--replicate`, branch | n/a (reference section) | `<darkroom>` (never glossed) | yes (identifiers belong in a locator section) |

---

## B. Figures: cold-reader sentence and false-friend test

For each figure I asked, with the caption covered: what does this resemble; what do the axes mean in that idiom; and do they mean the same thing here?

- **Figure 1**
  - **What a cold reader sees:** a black-and-white raster, 33 rows over 45 minutes, with a dense block at 20–25 min. Above it are two lanes. One holds green, red and hollow down-triangles; the other holds orange vertical ticks of two widths, some topped by small red crosses.
  - **False friend: none.** It is a real raster and follows the raster idiom.
  - **Defect:** I cannot explain the red crosses or the thick vs thin ticks. The caption says only "the CoactDetect row is its 20 calls". The crosses probably mark false alarms, but a stranger has to guess.
  - **Smaller issue:** the lane is labelled "planted" but also carries the hollow decoys. The caption calls these "real bursts of coincidence that are not coordinated events", yet §1 defined a coordinated event as cells co-firing more than chance would explain. "Real" relative to what? How does a decoy differ, mechanically, from a planted event? One clause would settle it: what was simulated to make a decoy.
- **Figure 2**
  - **What a cold reader sees:** four left-to-right pipelines of five boxes each, one per net. Tube's stage-2 box is shaded.
  - **False friend: none.** It reads as the ordinary block-diagram idiom.
  - **Defect:** only the undefined box vocabulary (row F2).
- **Figure 3**
  - **What a cold reader sees:** four fold boxes across the top with fold 0 green, a 3×3 grid of "fit here"/"score here" boxes under folds 1–3, and refit and coordinate-search bars pointing left to "score on fold 0".
  - **False friend: none.** It matches the standard k-fold diagram: each grid row is one inner split. Readable.
- **Figure 4**
  - **What a cold reader sees:** a flow chart from CoactDetect, through two measurement boxes and three rates, × 1.6, to three ceilings.
  - **False friend: none.** Readable.
- **Figure 5: false friend, medium severity**
  - **What a cold reader sees:** two long strips of 48 touching squares, blue on top and orange below, each labelled with four fold seed ranges.
  - **What it resembles:** a heatmap row or colour bar, where each tile's position is a category and its shade is a *value*.
  - **What the shade means here:** nothing but alternation between folds (fill opacity 0.55 / 0.70 in the source). At that contrast the fold boundaries are carried almost entirely by the text labels, and a reader primed by the idiom looks for a per-seed quantity that does not exist.
  - **The squares carry no per-seed information:** the figure's whole content is "seeds 1000–1047 vs 2000–2047, four folds of 12".
  - **Suggested fix:** don't clarify the label; redraw it.
    - Four separated blocks of uniform colour with visible gaps, each labelled "fold 0: 1000–1011" and so on.
    - Or a 2 × 4 table.
    - Also move "training seeds 0–2 and refit seeds 0–4" out of this figure, or rename them (C2). Printed under a row of "recording seed" squares, they invite the reader to look for training seeds among the squares.
- **Figure 6: dot strip plot, not a false friend**
  - **What a cold reader sees:** three abutting panels, each with ten rows. Each row has two nearly overlapping clusters of four dots, blue just above orange, mostly at F1 0.6–0.8, with a few isolated dots far to the left.
  - **Raster risk: low.** Rows of dots on a horizontal axis resemble a raster at thumbnail size, but the x label "held-out F1" and the ~8 dots per row prevent the misreading.
  - **Real problem 1, the mean ticks:** each tick is mostly hidden under its own cluster. The only ticks a reader actually sees are the ones pulled away by an outlier (chorus_norm F1-alone orange at ~0.66; binned SCE under-budget orange at ~0.71; tube under budget). Those read as an extra data mark, not a mean.
    - Fix: draw the mean as a distinct offset mark, or drop it, since Table 1 carries the means.
  - **Real problem 2, abutting panels:** the panels touch, so the axis labels read "0.2 … 0.8 0.2 … 0.8" as one continuous strip.
    - Fix: put a visible gap between panels. This is a boundary with agent 10.
  - **"not draws" in the caption:** see C3.
- **Figure 7: dumbbell chart, the idiom used correctly**
  - **What a cold reader sees:** 24 rows, each with a blue and an orange dot joined by a line, plus a right-hand column of differences, three of them bold.
  - **Defect:** where the two draws coincide (both CoactDetect rows, line_length under budget) only the orange dot is visible, so the first draw looks *missing*.
    - Fix: one caption clause ("a single dot: both draws gave the same value"), or draw the hidden dot as a ring.
- **Figure 8: grouped bar chart, the idiom used correctly**
  - **What a cold reader sees:** three groups of five orange bars by refit seed. The middle group has two short hatched bars; the right group has two bars that are simply absent.
  - **Defect:** the caption says the hatched bars include the two at 0 under the budget, but at zero height the hatching cannot be seen.
    - Fix: a hatched stub or a "0: no calls" label on those two positions.

---

## C. Cross-cutting vocabulary problems

A stranger meets these in several places. Each one should be fixed once, at first use.

| # | Location(s) | Issue | Severity | Suggested fix | Verifiable against a source? |
|---|---|---|---|---|---|
| C1 | subtitle, answer box, Fig 1/4/5/6/7/8 legends, Table 1 column heads, §6, §8 | **WSMIP064 / WSMIP065 are never defined.** They name the two draws throughout. The only hint that they are machines is "Both workstations" in §10. | high | In audience text, call them "first draw (seeds 1000–1047)" and "second draw (seeds 2000–2047)" in legends and column heads. Say once in the subtitle: "run on workstations WSMIP064 and WSMIP065". | yes (render) |
| C2 | §2, §4, Fig 3, Fig 5, Table 1, Fig 8 | **"seed" has three meanings:** recording seed (which simulated recording), training seed (network initialisation), refit seed. §4 and Figure 5 put two meanings in the same sentence or figure. | high | Keep "seed" for one meaning only. Write "recording" (or "recording 1000") for the data, and "initialisation 0–4" or "training repeat" for the net. | yes |
| C3 | title, subtitle, §3 ("drawn at random"), §4 callout ("fit's own draw"), Fig 5, Fig 6 caption ("not draws") | **"draw" is overloaded:** the two runs; a random sample of configurations; a fit's random draw of recordings; and an outcome of chance. The Figure 6 caption's "defects … not draws" becomes ambiguous because of it. | medium | Define "draw" once in the subtitle as "an independent set of simulated recordings". Use "sample" or "chance" for the other senses. | yes |
| C4 | §2 vs §5; §2 vs Fig 2 | **"baseline"** means the pre-drug stretch (§2) and the shuffled null model (§5). **"background"** means the bench's quiet/busy rate (§2) and a net's per-share reference (Fig 2, "against its own background"). | medium | In §5 write "shuffled null" or "chance level". In Figure 2 write "against that share's usual level". | yes |
| C5 | Table 1 footnote | **"cell"** means a table cell in a report where "cell" means a neuron. | medium | Write "at least one of this entry's refit seeds". | yes |
| C6 | answer box, §5, §7, Fig 7 text, §9 | **"entry"** is never defined. The "20 entries" in the answer box and §7 cannot be reconciled with the 24 rows in Figure 7. | high | Define it at first use: "an entry is one detector under one selection rule (24 in Figure 7)". State which 20 the median is over, or change the count. The arithmetic belongs to the numbers roles; its unreadability belongs here. | partly (the count needs a numbers role) |
| C7 | subtitle ("goal-2"), §4, §5, T1 ("starting point"), §8c | **goal 1 / goal 2** are never defined. | high | One sentence in §1 or §2: what goal 1 established (the tuned sliding operating points, with a crowded-recording check), and that this page is goal 2. | yes |
| C8 | answer box, §4 callout, §6, §9 | **"rehearsal run"** is never defined: when it ran, on what, how it differs. | high | One sentence in §6: "an earlier run on seeds …, before the fold fix, which ended +0.011 …". | yes |
| C9 | §4 callout, §6, §8a, §10 | **Code identifiers in audience prose:** `fold_check`, `recording_seeds`, `replicate`, `--replicate 0`, `75d4474550026cfa`, `tiny`, `steps_excluded`, `HANDOFF-…md`, `main`. The snake_case net names (chorus_gain_norm, line_length) also work as identifiers, and "line_length" does not describe what the net does ("share of the field that is lit"). | medium | Move identifiers to §11. In prose use the concept: "the check that each fold trains on its own recordings", "the two runs' configurations differ only in their recordings", "the configuration tuning chose". Consider human names for the nets, or at least introduce the snake_case names as labels in Figure 2's first mention. | yes |
| C10 | §10 | **"Tony"** and "decisions waiting on Tony": a stranger does not know who this is. | medium | "an open decision for the project lead", with the HANDOFF path moved to §11. | yes |
| C11 | §2 → §10 | **"fast stream" is not explained until §10's aside** about opposite drug effects. | medium | Add one clause in §2 saying what separates the two streams. | yes |
| C12 | §8b | "the quiet busy stretch" reads as a contradiction; "ceiling near 17" has no unit. | low | "the busy stretch of the quiet-background recording"; "near 17 calls per hour". | yes |
| C13 | §5 | **1.6** is never motivated: why that margin? | medium | One clause of justification, or "a margin chosen in goal 1". Whether it *was* chosen there is for agent 2/4 to check. | no (needs the source) |

---

## D. Illustrate, don't name-drop

- **§3 needs a picture it does not have.** CoactDetect's and LoCo's core mechanism is a count of distinct active cells compared against shuffled copies of the recording, and it is described in words only. Severity: medium. Fix: reuse the project's existing illustration if it has one (not verified: I did not search beyond the artifact), or add a small panel.
- **§5's binned vs sliding window explanation needs a picture.** The paragraph on fixed bins losing 30–36% of calls under a sub-second shift is the kind of mechanism the rule says to draw: a single two-row sketch of a bin edge splitting an event would replace most of it. Severity: low to medium.
- **Figure 2 illustrates the nets well.** That is the model for the two above.

## E. Tone

- **Sentence case:** consistent in headings, figure titles and table titles. No stray capitals or all-caps emphasis.
- **List smuggled into prose, §3 paragraph 1:** the six coded detectors are six list items joined by semicolons into one 80-word sentence. Severity: low. Fix: a six-item bulleted list, one line each.
- **Figure 5's "Different / The same" block** is already laid out as a list. Fine.

## F. Boundary notes (filed here, owned elsewhere)

- **The 20-entries count (C6):** is 20 right, and which 20 are meant? That is for the numbers/claims roles. My finding is only that a stranger cannot reconstruct it.
- **Mechanical figure items for agent 10:** Figure 1's x-axis label is a bare "t", and Figure 6's panels abut.

## G. Most important fixes, in order

1. Rename WSMIP064/065 in all audience-facing text (C1).
2. Split "seed" into two words (C2).
3. Define entry, goal 1 and rehearsal run at first use (C6, C7, C8).
4. Make the answer box and subtitle readable with nothing else on the page (rows 0a, 0b).
5. Cut or collapse the §4 callout and the flag talk in §6, moving identifiers to §11 (C9).
6. Redraw Figure 5 as separated fold blocks or a table; stop shade-coded touching squares reading as a heatmap (B).
7. Explain Figure 1's red crosses and tick widths (B).
