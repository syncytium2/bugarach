GRANT 8 ok — Read, Grep, Glob

(SubagentHandback is the hand-off channel, not an editing tool. I hold no Edit, Write or NotebookEdit.)

# Role 8, "You Lost Me" (naive-reader accessibility): blind verify, round 3 of 3

**Artifact:** `%USERPROFILE%\bugarach\bugarach-worktrees\replicate-report\docs\learned\tuned_vs_coact\replicate1\report.html` (hash-object 9a99a7a4…)
**What I read:**
- Rendered slices `...\scratchpad\shots3\light_1100_00.png` through `light_1100_13.png`, top to bottom.
- Spot checks in dark mode: `dark_1100_03.png`, `dark_1100_04.png`.
- Spot checks on phone: `light_390_01.png`, `light_390_02.png`.
- Prose that fell between slices, read through Grep on the HTML: line 117 (the F1 definition), line 167 (tube), line 228 (the rehearsal), lines 284–285 (goal 1's 8 s), lines 356–358 (Tuning), and the Figure 9 and Figure 10 caption text at lines 317 and 339.

I opened no earlier review reports.

**Reader modelled:** someone who knows calcium imaging and neural networks, and has never seen this lab, its detectors, its simulator or its runs.

## Per-section verdict (one row per section or figure)

| Unit | Terms and identifiers first used here | Defined here? | Can a cold reader follow it? |
|---|---|---|---|
| Title + lede + "Why this report exists" | F1, learned / hand-written, draw, simulated recordings, event streams, rehearsal, false-alarm budget, reference detector | F1 is defined 3 lines later in the answer box. The rehearsal is defined ("on a simulator since retired"). "Draw" is only implied ("recordings the first run never saw"). "Coded" in the title is not tied to "hand-written" until section 3. "Budget" and "reference" point forward. | yes (minor) |
| "The answer, in plain words" box | F1 (defined), CoactDetect, shared cap on false alarms, **fold**, joins calls / merge, **chorus models**, **slow event stream**, "where their training worked" | Defined here: F1, the cap, and joining calls within 2 s / 8 s. **Undefined: fold, chorus models, event stream**. "Call" is inferable only from context. | **BLOCKING: 3+ undefined terms** |
| §1 + Figure 1 | raster, ROI, coordinated event, lane, planted, distractor, call, dense stretch, seed, reference settings, held-out, second draw | Defined: raster, ROI, coordinated event, lane, and every legend item. Undefined at this point: seed (ML readers know it), held-out, second draw. | yes |
| §2 | bench, baseline, fast/slow stream, quiet/busy, distractor, dense stretch, "promiscuity probe", empty recording, call, match, merge, reference, recall, precision, hit, practical ceiling | All defined. "Hits" is inferable. "Can pass that figure" is ambiguous (see findings). | yes |
| §3 coded detectors | rate+context, CoactDetect, LoCo, circular shift, binned SCE, locust, SPIKE-synch, CICADA, null, surrogates, z-score, α, guard interval, context, Goal 1 | All defined or cited. In rate+context, "a window centered on **it**" has no clear referent. | yes (minor) |
| §3 learned models + Figure 2 | net, frame (0.1 s), threshold, tube, **pool**, tuning inflation, line_length, **the field**, **vote**, chorus_norm, encoder, Deep Sets, gain, configuration, hyperparameters | "Vote" is used in the line_length bullet and defined only in the next bullet (chorus_norm). "The field" and "pool of about a second" are never defined. The name "line_length" does not match the description given. Figure 2 is the deliberate placeholder, so no net is illustrated. | line_length: **no**. tube: partly. chorus pair: yes. **major** |
| §4 + Figure 3 | nested CV, outer fold, held out, inner fit, training repeat, fold pair, refit, coordinate search, grid, admissible | Defined, and Figure 3 carries the process. Three things lose the reader: "each pair serves two outer folds", the unexplained "40–60 refits", and "two held-out folds trained on" | yes (minor) |
| §5 + Figure 4 | entry, chosen on F1 alone, chosen under the budget, ceiling, margin 1.6, binned CoactDetect, candidate, gated | Defined; Figure 4 is clear. "(CoactDetect 2–6)" has no unit. | yes |
| §6 + Figure 5 | rehearsal's four defects, WSMIP064/065, settings files, the draw option | Workstation names are internal identifiers that a cold reader does not need. | yes |
| §7 + Figure 6 + Table 1 | held-out F1 per fold, mean tick, practical-ceiling line, off-scale triangle, †, ‡, flagged | All defined in the caption and the table note. | yes |
| §8 + Figure 7 + Tables 2–4 | collapse, F1 = 0.125, admissible setting, one-step neighbor, top of grid, locust's frame unit | Defined. "Refits whose output is scaled differently" gives no mechanism. | yes (minor) |
| §9 + Figures 8–11 + Tables 5–6 | between-draw move, flagged / unflagged, paired t-test, matched merge, re-decode, as-run gap, "distractor field" | Defined. Figure 10's left-edge arrows / triangles are **not explained** in its caption. | yes (minor; one legend gap) |
| §10 + Table 7 | TTX (defined), `steps_excluded` export, "the bench's eight constants", bootstrap intervals, 4,096-frame crop | `steps_excluded` is a code / folder identifier, and "export" is never defined. The "eight constants" are never listed. | yes (minor) |
| §11 + References | darkroom, branches, file paths | This is a sources appendix, so paths are appropriate here. `<darkroom>` is defined. | yes |

## False-friend test (render open, caption covered: what does it resemble · what do the axes mean in that idiom · same here?)

- **Figure 1** looks like a spike raster with an event lane above it. In that idiom the horizontal axis is time and each row is a cell. Here the axes are time (min) and ROI. **Same.** Pass.
- **Figure 2** is a placeholder box (deliberate). Not assessable.
- **Figure 3** looks like a k-fold cross-validation diagram: folds as columns, roles by colour. **Same.** Pass.
- **Figure 4** looks like a flowchart with arrows showing derivation. **Same.** Pass.
- **Figure 5** looks like a tiled table of folds by draw, and could be taken for a Gantt / timeline. The in-tile labels ("fold 0: seeds 1000–1011") rule out a time reading. Pass.
- **Figure 6** looks like a strip / forest plot: rows are entries, horizontal is the score, ticks are means, dotted line is a reference. **Same.** Pass.
- **Figure 7** looks like a bar chart: categorical horizontal axis, value vertical. **Same.** Pass.
- **Figure 8** looks like a forest plot of differences with a zero line. **Same.** Pass.
- **Figure 9** looks like a dot strip of differences with a zero line. **Same.** Pass.
- **Figure 10** looks like a dumbbell plot: two conditions per unit, joined by a line. **Same.** Pass on idiom (legend gap below).
- **Figure 11** looks like a stacked horizontal bar chart. **Same.** Pass.

No false friends found.

## "What a cold reader sees", one sentence per panel

- **Fig 1:** A black-and-white raster of 33 cells over 45 minutes with a solid dense block at 20–25 min. Above it, green and red down-triangles mark planted events, hollow triangles mark distractors, and orange ticks with red × mark CoactDetect's calls and false alarms.
- **Fig 2:** An empty dashed box saying "to come".
- **Fig 3:** Four fold tiles with fold 0 held out, three fit/score rows below them showing which training fold scores each inner fit, and two "score on fold 0" boxes fed by refit and search.
- **Fig 4:** CoactDetect's rates in the dense stretch and on the empty recording, each multiplied by 1.6 to give three ceilings.
- **Fig 5:** Blue and orange tiles giving disjoint seed ranges per fold for the two draws.
- **Fig 6:** Three side-by-side dot strips of per-fold F1 by entry. The nets sit left of CoactDetect under the budget, and three coded detectors fall off the left edge.
- **Fig 7:** Five tall bars in panel A; in B, two short hatched bars at repeats 1 and 2; in C, zero-height × marks at the same repeats.
- **Fig 8:** One dot per entry around a zero line. Filled net dots mostly sit right of zero and coded dots mostly left; hollow dots are the outliers.
- **Fig 9:** Per-fold dots of each net minus CoactDetect, all left of zero under the budget.
- **Fig 10:** Short lines per fold running from a hollow (as-run) marker to a filled (8 s) marker. Most move right toward zero, and a few run off the left edge as arrows.
- **Fig 11:** Stacked bars of false alarms per recording. A small grey dense-stretch part sits beside a long purple outside part, and chorus_gain_norm's purple bar is the longest.

Every panel could be described in one sentence. No phantom structure: the dense block in Figure 1 is real data, and its highlight sits in the lane, not on the raster.

## Findings

Each finding gives: location · issue · severity · suggested fix · verified against a source.

1. **Location:** "The answer, in plain words" box, bullets 2–5.
   **Issue:** The summary introduces **fold** ("in every fold of both draws"), **the two chorus models**, and **the slow event stream** without defining them. "Folds where their training worked" also leans on "fold". A cold reader meets these in the box they are most likely to read alone, and section 4 (folds) and section 3 (chorus) come much later.
   **Severity:** **blocking** (3+ undefined terms in one unit, per the output contract).
   **Fix:**
   - Gloss each term inline once: "fold (a quarter of the recordings, held back and scored once)".
   - Write "the two chorus models (nets that pool a vote from every cell, section 3)".
   - Write "the slow event stream (the lab's second way of scoring events, section 2)".
   - Alternatively, rephrase so the box needs none of the three.

   **Verified:** yes (rendered `light_1100_00.png`; §3/§4 are the first definitions).

2. **Location:** §3, line_length and tube bullets.
   **Issue:**
   - line_length uses **"vote"** before it is defined (the definition is in the next bullet, chorus_norm), and **"the share of the field that is active"** leaves "field" undefined.
   - Its name suggests the signal-processing line-length feature (sum of absolute differences). The description does not say whether that is what it computes, so a neural-network reader will map the name to the wrong mechanism.
   - tube's "a pool of about a second" leaves unclear whether "pool" means a time window or a set of cells.
   - With Figure 2 a placeholder, these two nets have no picture and no usable sentence. Chorus_norm's description, by contrast, is good.

   **Severity:** major.
   **Fix:**
   - Put chorus_norm first, so "vote" is defined before it is reused.
   - Replace "field" with "the imaged cells".
   - Say in one clause what line_length computes and why it has that name.
   - Write "a sliding window of about 1 s" for tube if that is what "pool" means.

   **Verified:** yes (rendered `light_1100_02/03.png`; HTML line 167).

3. **Location:** Figure 10 caption (HTML line 339).
   **Issue:** Arrowheads and a triangle sit at the left edge (line_length and tube rows, and an orange triangle in tube under the budget). The caption does not explain them. Figure 9's caption does explain its left-edge triangles ("a fold below −0.15"); Figure 10's does not, so the reader must guess whether an arrow means off-scale, direction, or something else. In the line_length row, two long lines overlap, and without that key the reader cannot tell which end is which.
   **Severity:** minor (the mechanical legend completeness is agent 10's; flagged here because a cold reader cannot decode that row).
   **Fix:** Add "an arrow or triangle at the left edge is a value below −0.15".
   **Verified:** yes (Grep: "below −0.15" appears only on line 317, the Figure 9 caption).

4. **Location:** Figure 1 and §1, "It is hard for three reasons, all visible in Figure 1".
   **Issue:** Reason 1, "an event recruits only a few of the imaged cells", is barely visible. At 45 minutes across the plot, a 3-cell event is a faint column of dots that cannot be told apart from chance. The claim "visible" rests on the reader trusting the triangles.
   **Severity:** minor.
   **Fix:** Add a small zoom inset (a few seconds) under one green triangle and one hollow distractor, or soften to "two of them visible".
   **Verified:** yes (`light_1100_01.png`).

5. **Location:** §4, second paragraph.
   **Issue:**
   - "each pair serves two outer folds, so each fit is scored on the two folds outside its pair" is correct but needs a worked example to be followed cold.
   - "(40–60 refits per net per draw)" gives a range without saying why. It varies because the three winners can coincide.
   - The callout sentence "two held-out folds trained on the same ten recordings" reads as if held-out folds train. It means that the nets for two different held-out folds trained on the same ten recordings.

   **Severity:** minor.
   **Fix:**
   - Add "(e.g., a fit on folds 1+2 is scored on fold 3 when fold 0 is held out, and on fold 0 when fold 3 is)".
   - Add "(2 or 3 distinct winners × 5 repeats × 4 folds)".
   - Reword the callout sentence.

   **Verified:** yes (rendered `light_1100_03.png`).

6. **Location:** Lede and title.
   **Issue:**
   - "Draw" is the report's central noun (title, answer box, Figure 1) but is never defined in one sentence. A cold reader infers it only from "reruns … on recordings the first run never saw".
   - "Coded" in the title is tied to "hand-written" only in §3.

   **Severity:** minor.
   **Fix:** In the lede, write "each **draw** is one full run of the comparison on its own set of simulated recordings". Write "hand-written ('coded')" at first use.
   **Verified:** yes (rendered `light_1100_00.png`).

7. **Location:** §2 end, "so a long merge can pass that figure".
   **Issue:** "Figure" here means the number 0.83, in a sentence that also cites "Figure 1". The same clash occurs in §10: "the one real-recording figure quoted (30–36%)". In a document that numbers its figures, "figure" meaning "number" misleads.
   **Severity:** minor.
   **Fix:** Write "can score above 0.83" and "the one real-recording number quoted".
   **Verified:** yes (rendered `light_1100_02.png`, `light_1100_12.png`).

8. **Location:** §3 rate+context bullet.
   **Issue:** In "compares the population's event rate with the rate in a window centered on **it**", the relative word has no referent.
   **Severity:** minor.
   **Fix:** "…with the rate in a longer window centered on the same moment".
   **Verified:** yes.

9. **Location:** §5, "What the budget does not police": "(CoactDetect 2–6)".
   **Issue:** Bare numbers with no unit.
   **Severity:** minor.
   **Fix:** "(CoactDetect: 2–6 calls per hour)".
   **Verified:** yes.

10. **Location:** §9, "Untuned, chorus_norm was −0.012 and +0.006", and "Where the as-run gap is": "recall 0.90 and 0.85 against 0.86 and 0.84".
    **Issue:** In each paired value, what the "and" separates (first draw / second draw), and what the untuned difference is relative to (CoactDetect), are left for the reader to infer.
    **Severity:** minor.
    **Fix:** Add "(first and second draw), relative to CoactDetect".
    **Verified:** yes (Table 1: 0.736−0.748, 0.753−0.748).

11. **Location:** §6 and §10: internal identifiers in the body text.
    **Issue:**
    - Workstation names (WSMIP064 / WSMIP065) appear in §6 and in the Figure 5 row labels.
    - "the `steps_excluded` export" appears in §10; "export" is never defined as the lab's data folder.
    - "the bench's eight constants" are never listed.

    **Severity:** minor.
    **Fix:**
    - Say "two workstations" in the body and keep the names in §11.
    - Write "the lab's data folder (export) in which motion correction…".
    - Either name the constants or write "seven of the bench's eight fitted rates and shares".

    **Verified:** yes.

12. **Location:** Net names throughout (chorus_norm, chorus_gain_norm, line_length).
    **Issue:** Underscore identifiers read as code. They are used consistently as proper names and a reader copes, but the checklist asks to keep code identifiers out of audience-facing text.
    **Severity:** minor (advisory; renaming touches every table and figure).
    **Fix:** Optional display names, or a one-line note in §3 that these are the models' code names.
    **Verified:** yes.

13. **Location:** Figure 1 y-axis, "simulated · 33 ROI".
    **Issue:** The unit should be the plural "ROIs"; the text elsewhere says "33 ROIs".
    **Severity:** minor.
    **Fix:** "33 ROIs".
    **Verified:** yes.

14. **Location:** Figure 3 and Figure 4 captions (light mode).
    **Issue:** The inline legend swatches are so pale they read as empty boxes, so the three roles in Figure 3 cannot be decoded from the caption. They are fine in dark mode (`dark_1100_04.png`). The in-figure labels ("held out", "fit", "score") carry the meaning, so the reader is not lost.
    **Severity:** minor. The boundary is agent 10's (legend legibility); noted, not owned.
    **Fix:** Give the swatches a border and matching saturation.
    **Verified:** yes.

15. **Location:** §3 / Figure 2.
    **Issue:** "Illustrate, don't name-drop" is unmet for the four net mechanisms while Figure 2 is a placeholder. You have said this is deliberate, so I record it as a known gap, not a new defect. Finding 2 is the part the prose can fix now.
    **Severity:** minor (acknowledged).
    **Fix:** Fill Figure 2 as planned.
    **Verified:** yes.

## Checked and found clean

- **Every other figure is labelled by what it shows:**
  - Figure 6 panels: "untuned (nets only)", "chosen on F1 alone", "chosen under the budget".
  - Figure 7 panels: A/B/C, named the same way.
  - Figure 9 and Figure 10 row groups: "chosen on F1 alone" and "chosen under the budget".
- **Idioms (false-friend test):** every one of the nine figures that has content matches its idiom's axis conventions.
- **Other terms and symbols:** everything else is defined at first use (ROI, SCE, CV, TTX, α, frame = 0.1 s, entry, budget, ceilings, admissible, †/‡). The Figure 1 legend is a real list.
- **Tone:**
  - Headings and captions use sentence case throughout.
  - No ALL-CAPS emphasis; only acronyms and proper names.
  - Lists are real lists (§2's recording contents, §3's contestants, §10's limits).
- **No phantom structure** in any render. Nothing is drawn on the Figure 1 raster, and the lane markers point down at it.
- **Phone (390 px):** Figure 1 carries a "scroll sideways" cue and its legend stacks readably.

## Overall

One blocking row: the answer box relies on "fold", "chorus models" and "event stream" before the report defines them. It is cheap to fix with inline glosses. One major row: the line_length and tube descriptions in §3 cannot be pictured cold, and Figure 2 does not rescue them yet. Everything else is minor wording.

Throughout, the lede and §1–§11 read as a coherent argument a stranger can follow.
