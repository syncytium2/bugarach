GRANT 8 ok — Read, Grep, Glob

(SubagentHandback is the hand-off channel, not an editing tool. I hold no Edit, Write or NotebookEdit, and I edited nothing.)

# Role 8: can a cold reader follow it? Report on `replicate1/report.html`

**Artifact:** `%USERPROFILE%\bugarach\bugarach-worktrees\replicate-report\docs\learned\tuned_vs_coact\replicate1\report.html`

**Render read:** `...\scratchpad\shots\light_1100_00.png` through `light_1100_10.png`, top to bottom. I grepped the HTML at three slice boundaries and each joins onto the next, so no text is missing between slices.

**Reader I assumed:** knows calcium imaging and neural networks, but has never seen this lab, its detectors, its simulator or its runs.

## A. Verdict per section, figure and table

"Blocking" means three or more terms that are not defined at the point of use, or a panel I could not describe.

| # | Unit | Terms and identifiers first met here | Defined here? | Can a cold reader follow it? |
|---|---|---|---|---|
| 0a | Title and lede | "the **fair** comparison", draw, seed, WSMIP064, fast stream, baseline | "draw" is defined. "fair" is not: fair relative to what? fast stream and baseline are only defined in §2. WSMIP064 is glossed only as "the workstation". | **no.** Three terms are undefined, and "fair" is contradicted by §10's "the two sides were not treated alike" |
| 0b | "The answer, first" box | F1, flagged fold, learned model, hand-written detector, configurations, training repeats, false-alarm budget, CoactDetect, chorus_gain_norm, chorus_norm, outer folds, "chosen on F1 alone", untuned, **merge** ("merge their calls at a fixed 2 s"), fit, matched merge | None of them. The box says "each point is explained in the section named", but the definitions sit in §2–§8. "merge" is not defined until §8. | **BLOCKING.** About 15 undefined terms. A stranger can take away only "learned models trailed CoactDetect", and cannot tell what CoactDetect is. |
| 0c | "Why this report exists" | rehearsal, "a different simulator", "goal 2 of the program", `docs/goals/README.md` | "rehearsal" is defined inline. "the program" and "goal 2" are not. | yes, with minor gaps |
| 1 | §1 The problem | raster, ROI, coordinated event, field, busy | yes, all except "field" (meaning field of view, which a stranger can guess) | **yes.** This is the best-written section. |
| F1 | Figure 1 (raster, lane and key) | CoactDetect, "reference settings of section 5", held-out recordings, distractor, dense stretch, matching tolerance, SCE ("SCE bins at ten seconds"), "four of the six", threshold, second call, "fragmentation, not hallucination" | Distractor and dense stretch are defined in the key and caption. **CoactDetect, SCE, "the six", matching tolerance, reference settings and held-out are not**: they come in §2, §3 and §5. | **BLOCKING.** Six terms are undefined. The picture itself can be read (see section B). |
| 2 | §2 Why a simulation | bench, baseline, fast/slow stream, distractor, dense stretch, quiet/busy, F1, recall, precision, "call", fold, "the folder" | Mostly defined. "fold" only arrives in §4. "call" is never defined (the key says "detection"). "the folder the bench was last checked against" has no referent. | yes |
| 3 | §3 The contestants | coded, rate+context, CoactDetect, **LoCo** (acronym never spelled out), binned SCE, locust, SPIKE-synch, "circularly shifted", "a few frames", CICADA, nets, tube, line_length, chorus_norm, chorus_gain_norm, "pool of about a second", "lit", "pool … three ways", Deep Sets, untuned default | Most get one clause. LoCo is never expanded. Nothing explains "norm" or "gain" in the net names; "gain" has to be inferred from "steepness". "three ways" is not listed. The circular-shift null is only named, never shown. | partial |
| F2 | Figure 2 (reserved slot) | "draughtsman", `<darkroom>`, "untuned parameter counts" | No. "draughtsman" is an internal agent role. "untuned parameter counts" can be read as "parameters that were not tuned". | Readable as a placeholder. See section C. |
| 4 | §4 Nested CV, and the defect call-out | nested CV, outer fold, inner fit, training repeat, threshold, "the budget's winner", refit, coordinate search, round-robin, "contiguous run of its recording list" | Nested CV and folds are defined well. "the budget's winner" is used before §5. In the call-out, "training reads a contiguous run of its recording list" has no clear owner for "its". | Main text: yes. Call-out: **no** (the mechanism cannot be followed). |
| F3 | Figure 3 (nested CV diagram) | fold 0 (numbering starts at zero), backgrounds, score/fit, grid | yes | **yes** |
| 5 | §5 Two selections and one budget | entry, chosen on F1 alone, chosen under the budget, ceilings, "binned CoactDetect", "empty-recording limit", **empty recording** (absent from §2's list of what a recording contains), "the sliding reference" (before "sliding" is defined), `HANDOFF-workstation-tuning.md`, branch `tune-bench-comparison`, `docs/forks.md §14`, "Goal 1 of the program", counting window, context, "exact null", guard window, "the code's table of shipped settings", "browser viewer", "long merge" | "entry" and the two selections are defined well. The second paragraph brings in about 10 undefined terms or internal references. | **BLOCKING** (second paragraph) |
| F4 | Figure 4 (how the budget is set) | "the reference's calls", α, context, empty recording, "a floor of one false alarm in the measured time" | The boxes are self-explanatory. The caption's last clause is cryptic. | yes |
| 6 | §6 Why two draws | "three settings", "older budget", declarations, replicate number, "the option that sets the replicate" | No. "replicate" is a second word for "draw" and is never tied to it. | partial |
| F5 | Figure 5 (seeds by fold) | "empty twin at seed + 100,000", grids, WSMIP064/065 | "empty twin" is not defined | yes |
| 7 | §7 Results text | "Binned SCE **leads**", "the reference settings" | "leads" has no referent. It means "leads CoactDetect", which the reader has to work out from Table 1 (0.771 − 0.748). | yes, with a minor gap |
| F6 | Figure 6 (held-out F1 strips) | held-out F1, panels A/B/C | yes | yes, with a low-severity rendering note (see section B) |
| T1 | Table 1 | untuned, †, "—" in the untuned columns for coded detectors | **†** is first met here but only explained after Table 2. "—" is not explained: why do coded detectors have no untuned score, when they do start from reference settings? | partial |
| T2 | Table 2 | ‡ | explained below the table | yes |
| 8a | §8 "Training that failed" | failed (defined: output near a constant), 864 scored inner fits | "864" cannot be reconciled with §4's "432 inner fits per net across the run". Perhaps it is 432 × 2 backgrounds, but the page never says so. | partial |
| F7 | Figure 7 (chorus_norm refits) | hatched bar, training repeat | yes | yes, with a note on the stubs that stand for zero (see section B) |
| 8b | §8 "no admissible setting" | starting point, one-step neighbour, "**Those cells** carry ‡" | "cells" here means table cells, on a page where "cell" otherwise always means a neuron | yes, with an ambiguity |
| T3 | Table 3 | "**refit seeds**" (a new term; 20 = 4 folds × 5 refits, which is never stated), refits and folds mixed in one column | The caption explains the mix, but not "refit seeds" | partial |
| T4 | Table 4 | "Outer folds (**of 8**)" (4 folds × 2 draws, never stated), merge gap, "goal 1's 8 s", crowded | Section 8 defines "merge" here, 8 sections after its first use | partial |
| 9 | §9 What the pair can claim | headline gap, matched merge, "re-decoding" | Mostly defined. "Re-decoding" is jargon. | yes |
| F8 | Figure 8 (net minus CoactDetect) | — | yes | yes |
| F9 | Figure 9 (where false alarms fall) | — | Why only CoactDetect and LoCo among the coded detectors is not said. Row order differs from Figures 6, 8 and 10. | yes |
| F10 | Figure 10 (second draw minus first) | hollow = flagged | yes | yes |
| 9t | "Tuning" paragraph | "raised line_length by +0.032" | The referent (over its untuned default) is not stated | yes |
| 10 | §10 Limits | `steps_excluded` export, `HANDOFF-slow-comodulation-on-the-de-pinned-export.md`, "item 3 of the decisions", TTX, bootstrap intervals | Internal file and export names appear in prose | yes, but noisy |
| 11 | §11 Where everything is | `<darkroom>`, branches, tool paths | Paths are appropriate in a provenance section. `<darkroom>` is never explained. | yes |

## B. Each figure: what a cold reader sees, and the false-friend test

For each figure I asked, with the caption covered, what the image resembles, what that idiom's axes mean, and whether they mean the same here.

- **Figure 1.** A black-and-white spike raster (33 rows, 45 minutes, a dense block at about 20–25 minutes). Above it is a lane of green down-triangles, hollow triangles, orange hairline ticks, and red × marks on some ticks.
  - Resembles a raster, and is one: time runs along x and each row is a cell. **Pass.**
  - Readability defect: the key lists **Threshold** ("a dotted line, four of the six expose one"), **Second call** (○) and **Color is detector identity**. This figure has no trace, so there is no threshold line, and it has only one detector. A stranger goes looking for dotted lines that are not there.
  - I could not find any ○ marks at this resolution.
  - The x-axis is labeled only "t".
- **Figure 2.** An empty dashed box. See section C.
- **Figure 3.** A cross-validation grid: fold 0 held out in green, a fit/fit/score rotation over folds 1–3, then a refit and a score on fold 0. It resembles a k-fold diagram and means exactly that. **Pass.**
- **Figure 4.** A left-to-right flowchart: CoactDetect runs on the dense stretch and on an empty recording, and its call rates are multiplied by 1.6 to give three ceilings. **Pass.**
- **Figure 5.** Two rows of labeled boxes (blue = first draw, orange = second), four folds each, with seed ranges. There are no axes, so there is no idiom to misread. **Pass.**
- **Figure 6.** Three strip plots of held-out F1 per entry: blue dots above orange dots, with black mean ticks. It resembles a dot or forest plot.
  - **Low risk:** each row has two black ticks close together (one per draw), which an expert can read as the end caps of an interval.
  - **Phantom marks:** overlapping dots with white outlines render as crescents or "((" glyphs (for example rate+context in panel C, and binned SCE in panel B). These read as a third kind of mark.
- **Figure 7.** Bars for five refits in each of three panels. In B and C, refits 1 and 2 are hatched stubs.
  - **Phantom structure:** in panel C the stubs are labeled "0" but drawn about 0.06 tall against a y-axis that starts at 0.0. Someone reading the axis sees a value that is not there.
  - Otherwise a bar chart, and read as one. **Pass.**
- **Figure 8.** Per-fold dots of net minus CoactDetect, with a vertical zero line, in two panels. Read correctly. **Pass.** It shows the same overlap crescents as Figure 6.
- **Figure 9.** Stacked horizontal bars (grey, amber, red) of false alarms per recording, two bars per entry, with tiny coloured dots marking the draw. Read correctly. **Pass.**
- **Figure 10.** A dot plot of second-draw minus first-draw mean F1 per entry and selection, with hollow dots for flagged entries. Read correctly. **Pass.**

No figure is a false friend. Figure 1 is the one real raster, and it is honest.

## C. Figure 2: does the page work without it?

**The argument works. Section 3 does not.**

- Every result in §5–§10 treats the four nets as black boxes. The headline (the nets trail CoactDetect, the gap is in false alarms rather than recall, and it may come from the merge) does not need the architectures. A reader can follow the argument with the slot empty.
- The paragraph on the nets in §3 is the least readable prose on the page. It names mechanisms without showing them: "pool the cells' votes three ways (the Deep Sets construction)", "a bursting cell counts more than once", "measures the share of the field that is lit", "whether the vote's steepness is fitted". Nothing explains the names "chorus", "norm" or "gain". Until the drawing arrives, this fails "illustrate, don't name-drop".
- The reserved caption has problems of its own:
  - "the project's **draughtsman**" is an internal agent role, and a stranger will think it is a person.
  - `<darkroom>` is never explained.
  - "Untuned parameter counts" reads as "counts of the parameters that were not tuned".
  - "which are not yet in this build" tells an outside reader that the page is unfinished.
- **Fix:**
  - If the page ships before the drawing, collapse the slot to one line ("Architecture drawings: forthcoming") and move the parameter counts into §3 as "parameters in the default configuration".
  - Either way, add one plain clause for each net name.

## D. Findings

Columns: location · issue · severity · suggested fix · could I verify it against a source.

1. **"The answer, first" box**
   - Issue: about 15 terms are used before any definition: F1, fold/outer fold, flagged fold, configuration, training repeat, false-alarm budget, CoactDetect, chorus_norm, chorus_gain_norm, "chosen on F1 alone", untuned, merge, fit, matched merge.
   - Severity: **blocking**
   - Fix: rewrite the box in plain words, for example: "The best learned model found as many real events as the reference detector (CoactDetect) but raised more false alarms, in both independent sets of simulated recordings…". Put identifiers in parentheses at most, or define the few needed terms inline: F1 as the balance of hits and false alarms; the budget as a shared cap on false alarms; merge as how close two calls can be before they count as one.
   - Verified: yes (render)
2. **Figure 1 key and caption**
   - Issue: CoactDetect, SCE, "the six", matching tolerance, "reference settings of section 5" and "held-out recordings" are all used before §2, §3 and §5 define them. The key also carries entries for marks this figure does not draw (Threshold, "Color is detector identity"; I could not see any Second call ○).
   - Severity: **blocking**
   - Fix:
     - Add one gloss in the caption: "CoactDetect, the hand-written reference detector (section 3)".
     - Drop SCE, "the six" and Threshold from this figure's key.
     - Give "matching tolerance" as a value ("within 2.5 s").
     - Replace "held-out recordings" with "the other test recordings".
   - Verified: yes (render)
3. **§5, second paragraph, and the ceilings sentence in the first paragraph**
   - Issue: binned CoactDetect, empty-recording limit, "the sliding reference" (used before "sliding" is defined), Goal 1 of the program, context, exact null, guard window, "the code's table of shipped settings", "browser viewer", plus a HANDOFF file and a branch name. A cold reader is lost.
   - Severity: **blocking**
   - Fix: split history from definition. Keep one sentence: "The reference is CoactDetect counting cells in a 2 s window that slides with the data, tested against circularly shifted copies of the recording." Move the settings list, the ×1.6 provenance and the shipped-settings note into a footnote or into §11. Replace the file and branch citations in prose with "(source: §11)".
   - Verified: yes (render)
4. **"merge", everywhere from the answer box to §8**
   - Issue: the concept the headline limitation depends on ("merge at a fixed 2 s", "long merge", "matched merge") is only defined in §8: "the setting that decides how close two calls may be before they count as one".
   - Severity: high
   - Fix: define it in §2, next to "call" and "match".
   - Verified: yes (render)
5. **Title, "the fair comparison"**
   - Issue: "fair" is a relative word with no referent, and the page itself says the two sides were not treated alike.
   - Severity: medium
   - Fix: either define it at first use ("'fair' here means every choice is made without the test recordings, under one shared false-alarm cap") or retitle ("Two draws of the learned-vs-coded comparison").
   - Verified: yes (render)
6. **Net names used throughout (chorus_norm, chorus_gain_norm, line_length, tube)**
   - Issue: these are internal code identifiers with underscores. "norm" and "gain" are never explained, and nothing says why "chorus" or "tube".
   - Severity: medium
   - Fix: give display names (for example "chorus", "chorus + fitted gain", "line length", "tube (control)"), or add in §3 one clause per name saying what it refers to.
   - Verified: yes (render)
7. **§3, CoactDetect, LoCo and locust ("circularly shifted in time")**
   - Issue: the circular-shift null underlies the reference detector and the budget, but it is only named, never shown.
   - Severity: medium
   - Fix: add a small graphic (one cell's event train rotated by a random offset, with the real count compared against the shifted counts), or reuse an existing project illustration if one exists.
   - Verified: no (I did not search the darkroom for an existing illustration)
8. **§3, "LoCo"**
   - Issue: the acronym is never spelled out.
   - Severity: low
   - Fix: spell it out at first use.
   - Verified: yes (render)
9. **§4 call-out, "A defect was fixed…"**
   - Issue: "training reads a contiguous run of its recording list, so in fold order that run sat inside the first training folds" cannot be followed: whose list, and what is "fold order"?
   - Severity: medium
   - Fix: "Each fit used the first ten recordings of its training list; because the list was in fold order, two different held-out folds ended up training on the same ten recordings."
   - Verified: yes (render)
10. **§4 "432 inner fits per net" against §8 "292 of 864 … scored inner fits"**
    - Issue: a stranger cannot reconcile 432 with 864.
    - Severity: medium
    - Fix: state the arithmetic, for example "(432 fits, each scored at both backgrounds)", if that is what 864 is.
    - Verified: no (I did not check which arithmetic is right)
11. **"empty recording", first met in §5 and Figure 4**
    - Issue: it is absent from §2's inventory of what a bench recording contains, and later becomes "empty twin" (Figure 5) and "empty-recording limit".
    - Severity: medium
    - Fix: add one sentence to §2: "Each seed also has an empty twin: background activity only, nothing planted."
    - Verified: yes (render)
12. **Many names for one reference**
    - Issue: "one fixed detector", "the reference", "sliding CoactDetect", "the sliding reference" and "reference settings" all point at the same thing.
    - Severity: low–medium
    - Fix: introduce "the reference: CoactDetect at goal-1 settings" once and use only that.
    - Verified: yes (render)
13. **§8 "Those cells carry ‡"**
    - Issue: "cells" means table cells on a page where "cell" otherwise always means a neuron.
    - Severity: low
    - Fix: "Those table entries carry ‡".
    - Verified: yes (render)
14. **Table 1 †**
    - Issue: the symbol is first met in Table 1, but its key sits below Table 2.
    - Severity: low
    - Fix: put the footnote under Table 1 as well, or merge the two tables.
    - Verified: yes (render)
15. **Table 1 "—" for coded detectors in the untuned columns**
    - Issue: unexplained, and a reader wonders why coded detectors have no untuned score.
    - Severity: low
    - Fix: add a note: "coded detectors start from the reference settings; see the F1-alone column".
    - Verified: yes (render)
16. **Table 3 "refit seeds"**
    - Issue: a new term, and "20" is not derived.
    - Severity: low
    - Fix: "4 of 20 refits (4 folds × 5)".
    - Verified: yes (render)
17. **Table 4 "(of 8)", and "all 8 outer folds" in the answer box**
    - Issue: 8 = 4 folds × 2 draws is never stated.
    - Severity: low
    - Fix: "(of 8: 4 per draw)".
    - Verified: yes (render)
18. **§7 "Binned SCE leads on F1 alone"**
    - Issue: "leads" has no referent.
    - Severity: low
    - Fix: "leads CoactDetect".
    - Verified: yes (render)
19. **"Tuning" paragraph in §9**
    - Issue: "raised line_length by +0.032" does not say over what.
    - Severity: low
    - Fix: "over its untuned default".
    - Verified: yes (render)
20. **§6 "declarations", "replicate number"**
    - Issue: "replicate" is a second word for "draw", and it is never tied to it.
    - Severity: low
    - Fix: "the run's settings file differs only in the seeds and the draw number".
    - Verified: yes (render)
21. **Figure 7, panel C**
    - Issue: zero values are drawn as stubs about 0.06 tall. That is phantom height, since the y-axis starts at 0.
    - Severity: low–medium
    - Fix: draw zero as an empty outline or a marker at the baseline.
    - Verified: yes (render)
22. **Figures 6 and 8**
    - Issue: overlapping dots with white strokes render as crescent or parenthesis glyphs that read as a separate mark.
    - Severity: low
    - Fix: drop the white stroke, jitter vertically, or use transparency.
    - Verified: yes (render)
23. **Figure 6, mean ticks**
    - Issue: two black ticks per row can be read as the end caps of an interval (the forest-plot idiom).
    - Severity: low
    - Fix: colour each tick to its draw, or offset each tick onto its draw's dot row.
    - Verified: yes (render)
24. **Figure 9**
    - Issue: only CoactDetect and LoCo appear among the coded detectors, with no reason given. Row order also differs from Figures 6, 8 and 10.
    - Severity: low
    - Fix: say why in one clause in the caption, and keep one entry order across figures.
    - Verified: yes (render)
25. **Figure 2 caption**
    - Issue: "draughtsman" (an internal agent role), `<darkroom>` and "untuned parameter counts" are all opaque. The empty slot tells a stranger the page is unfinished.
    - Severity: medium
    - Fix: see section C.
    - Verified: yes (render)
26. **§3 net paragraph**
    - Issue: while Figure 2 is empty, the four architectures are only named: "pool three ways", Deep Sets, "lit", "steepness".
    - Severity: medium
    - Fix: list the three pooling ways, and add one plain clause per net.
    - Verified: yes (render)
27. **Internal references in audience prose (§4, §5, §6, §10)**
    - Issue: `docs/todo/...`, `HANDOFF-*.md`, branch names, the `steps_excluded` export, `docs/forks.md §14`, WSMIP064/065, and "the code's table of shipped settings".
    - Severity: low–medium
    - Fix: keep them in §11. In the prose, say what the source is ("the workstation tuning notes") and point to §11. Replace machine IDs with "workstation A/B", or gloss them once.
    - Verified: yes (render)
28. **Figure 4 caption**
    - Issue: "a floor of one false alarm in the measured time never binds here" is cryptic.
    - Severity: low
    - Fix: explain it in words, or cut it.
    - Verified: yes (render)
29. **Tone**
    - Checked: headings and table titles are in sentence case; there are no ALL-CAPS for emphasis; lists are formatted as lists; nothing is packed into titles with separators.
    - Severity: none. **No findings.**
    - Verified: yes (render)

## Summary for the main thread

- **Three blocking units:**
  - the "answer, first" box (row 0b)
  - Figure 1's key and caption (F1)
  - §5's second paragraph (5)
- **The fix that clears most of the page:** one change clears most of the medium findings. Define the page's working vocabulary once, in §2: call, match, **merge**, empty recording, and the reference detector. Then write the answer box in plain words that assume nothing from later sections.
- **False-friend test:** no figure fails it. The rendering problems are the zero-height stubs in Figure 7 and the overlapping-dot crescents in Figures 6 and 8.
- **Figure 2:** the page's argument works without it. §3's paragraph on the nets does not, and the reserved caption is opaque to a stranger.
