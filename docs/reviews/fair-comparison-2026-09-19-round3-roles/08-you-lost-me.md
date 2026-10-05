<!-- Verbatim role report, except that this machine's absolute paths are written as %USERPROFILE% and <darkroom> (the repository is public). The unedited original is in <darkroom>/bugarach/2026-09-18-fair-comparison-run/report/review-roles-round3/. -->

GRANT 8 ok — Read, Grep, Glob (plus SubagentHandback, the hand-back channel; I hold no editing tool)

Role 8 (You Lost Me, naive reader), round 3, BLIND. Artifact: %USERPROFILE%\bugarach\bugarach-worktrees\fair-comparison-report\docs\learned\tuned_vs_coact\fair_comparison_2026_09_18\report.html (hash 5c0ccbb, as given to me). I read all the prose lines of the HTML and took the figure captions from the HTML and from tools\build_fair_comparison_report.py. I opened all 12 figure renders and Tables 2 and 3 in ...\scratchpad\mb\renders_round3\. I did not open the review record or the run record. I read as a neuroscientist who knows calcium imaging and basic statistics and has never seen this project.

## Overall verdict

A cold reader can follow most sections. The report defines most of its terms where it uses them, and figures 1–6 do the conceptual work the brief asked for. Two rows are blocking by the three-or-more rule:
- the "The answer" paragraph
- Table 1

Beyond those, I found:
- one false-friend figure (Figure 8 reads as a forest plot)
- one partial false friend (Figure 9B)
- one missing illustration: nothing shows how the nets or CoactDetect work, and those are half the comparison

## Per-section / per-figure verdict

| unit | terms and identifiers first used here | defined here? | can a cold reader follow? |
|---|---|---|---|
| Title + subtitle | simulated recordings, baseline periods, fast stream | deferred to the Terms box directly below | yes |
| Terms box | ROI, firing, coordinated event, call, F1, recall, precision, outer folds, held-out, fast/slow stream, baseline periods, goal 1, project lead; also **CoactDetect, LoCo** | all yes except CoactDetect and LoCo, which are named but not defined (LoCo waits until Table 1) | yes |
| The question | coded, nets, untuned setting, since-retired simulator; a repo path in the lede | yes (repo path aside) | yes |
| **The answer** | "shared limit on false alarms", "both draws of recordings", "given its merge gap" (used before the gloss later in the paragraph), "refits that failed to train", "set aside", "faintest events", "busy / quiet background" | **no**: draws, refit, failed-to-train, faintest, and busy/quiet are all undefined at this point. Merge gap is glossed only after its first use. | **BLOCKING**: 5 or more undefined terms, in the paragraph read most. The closing "sections below explain every term" is honest, but it does not make the paragraph readable on its own. |
| §1 | distractor, probe, "labeled a negative" | yes | yes. The probe is not explicitly tied back to "the whole field becomes busier" two sentences earlier. |
| Fig 1 | recording seed, busy background, ramp | busy/quiet never named as such (see §2) | yes |
| §2 | bench, recording seed, two backgrounds, hit, tolerance, one-to-one matching, false alarms per hour, empty recordings | mostly yes. "the scorer's own documentation says to read the order of **its rows**": rows of what? | yes, with one lost referent |
| Fig 2 | none new | – | yes |
| §3 | net names chorus_norm, chorus_gain_norm, line_length, tube (code identifiers, and the text says so); "bounded vote", "pool" | the names are opaque by design, and the mechanism is prose only | partly. The nets' mechanism is name-dropped and not illustrated. |
| **Table 1** | Deep Sets shape, encoder/decoder, standardizes, gain and offset, share of ROIs lit, circularly shifted, rolled in time, coincidence window, **cell-averaging structure**, **CICADA**, **local context and guard**, frame, decoding, threshold, merge gap | Deep Sets is glossed. Cell-averaging structure, CICADA and local context are never defined. Guard is defined only in §4.3. Frame length only in §7. | **BLOCKING** by rule: 3 or more undefined, though they sit mainly in the "where it comes from" column |
| §4.1 | nested cross-validation, inner loop, training seed, refit, learning rate, training steps, context window, degrees of freedom, corrected *t* | yes | yes (the Nadeau–Bengio paragraph is dense, but its takeaway sentence is clear) |
| Fig 3 | none new | – | yes |
| §4.2 | fitting set, threshold recordings, "at some training seeds the run of 10 fell…" | why a *training* seed decides *which recordings* are fitted is never said | partly |
| Fig 4 | "at the first training seed", "picks the threshold" | partly | partly (see findings) |
| §4.3 | binned/sliding mode, alpha, guard, percentile, shipped operating point | yes | yes (but three reference points are in play: current defaults, shipped, goal 1's values) |
| Fig 5 | none new | – | yes |
| §4.4 | shared false-alarm budget, reference CoactDetect, "the quiet background" (first used as a proper name here) | budget yes; which background is "quiet" is not said | yes |
| Fig 6 | none new | – | yes |
| §4.5 | crowded-recording check, crowded recordings, admissible, "the setting it replaces" | "replaces" has no referent until §9; "the check sees gaps wider than about 6 s" is opaque | partly |
| §5 | replicate, draw, GPU | yes | yes |
| §6 + Table 2 + Figs 7–8 | corrected *t*, admissible, "refits that failed to train" | failed refits are explained only in §10, with no pointer | yes, except that the Table 2 caption is garbled (see findings) |
| §7 + Figs 9–10 | frames of 0.1 s, threshold picker, re-decoded, processors | yes | yes, apart from figure issues |
| §8 + Fig 11 | faintest events (= 10% participation) | yes, here | yes |
| §9 + Table 3 | shipped setting, "the window **its credit** is for", crowded_check.json | "its credit" is obscure; the file name is a code identifier | partly |
| §10 + Fig 12 | failed-training signature, threshold grid, "no operating point" | mostly | yes |
| §11 | export folder, `steps_excluded`, `min_rois`, bootstrap interval | export folder is undefined; the two code identifiers each have a plain gloss | yes |
| §12 | ARCHITECTURES[name].make(), build_chorus_norm(), WSMIP064/065 | developer text | not meant for a cold reader. Acceptable as a pointer section; the rebuild warning is developer guidance inside an audience document. |

## What a cold reader sees, per panel (render open, caption covered first)

- **Fig 1A**: a timeline of blue down-triangles in three shades, hollow triangles, a hatched stretch and a gray band. Readable.
- **Fig 1B**: a true raster: ROI rows, time across, one tick per firing. One vertical column of ticks at ~16.5 min, two more at ~17.3 and ~18.3 min, and a much denser block from 20 min. The idiom and its axes agree. Readable, and it makes the "events and distractors look alike" point well.
- **Fig 2**: four labeled rows (hit, false alarm, one call over two events, a call in the probe): black bars with gray brackets. Readable.
- **Fig 3**: a standard cross-validation grid, which is the right idiom. Readable.
- **Fig 4**: strips of cells, blue for fitted and black for held out, with a single purple cell. Readable in outline, but see the findings on "the last two" and "first training seed".
- **Fig 5**: tick marks over boxed counts, 3 and 3 against 6. Readable, and it is one of the best conceptual panels.
- **Fig 6**: a schematic scatter of F1 against false alarms per hour, the right side shaded "outside the budget", with two circled points. Readable.
- **Fig 7A/B**: dot strips per contestant: blue nets above, black coded below, hollow for failing, × for refused. Readable.
- **Fig 8**: rows of dots and diamonds around a dashed zero, with **long thin horizontal lines ending in a hollow marker**. I first read those lines as confidence intervals and only corrected that from the legend. **False friend** (finding 3).
- **Fig 9A**: bursts of short dashes above gray merged bars: far apart, two hits; close, one hit. Readable.
- **Fig 9B**: a line chart of F1 against merge gap. The x axis looks continuous but is ordinal (0, 2, 4, 8, 16, 30 s evenly spaced). Two rings overlap near 8 s. Partly readable (finding 4).
- **Fig 10A/B**: dot rows of net minus CoactDetect by matched gap. Readable, but one chorus_gain_norm dot at about −0.15 in every row of panel A is unexplained.
- **Fig 11A/B**: recall of 10% events by detector × background. Readable.
- **Fig 12**: dots of tuned minus untuned. Readable. Two outliers at about −0.13 are unexplained.
- **Table 2**: readable, but the caption does not parse (finding 7).
- **Table 3**: readable, but it has two identical "folds passing" headers.

## Findings

Each finding gives location · issue · severity · suggested fix · verified.

1. **"The answer" paragraph** · It introduces at least 5 undefined terms: draws of recordings, refits, refits that failed to train, faintest events, busy/quiet background. It also uses "its merge gap" before glossing it. This is the paragraph a new reader reads and may stop at. · **blocking** · Either add refit, draw/replicate, merge gap, budget, and quiet/busy background to the Terms box, or rewrite the answer in plain words (e.g. "on a second, independent set of simulated recordings"; "when the few net trainings that failed outright are excluded"; "events joined by only 10% of cells"; "at the higher of two background firing rates"). · verified yes

2. **Table 1, "where it comes from" column, and CoactDetect "what it does"** · "cell-averaging structure", "CICADA", and "local context and guard" are undefined (guard waits until §4.3). "encoder/decoder" is ML jargon for this audience. · **blocking** by rule (3 or more undefined in one unit) · Give each a one-clause gloss: "a moving average of the surrounding activity as the local baseline"; "CICADA, a calcium-imaging analysis toolbox"; "local context = the stretch around a moment used to estimate chance; guard = the part of it next to the candidate that is left out". · verified yes

3. **Figure 8** · False friend. Rows of point estimates around a dashed zero, with long horizontal whiskers, is the forest-plot idiom. There a horizontal line is a confidence interval. Here it joins "failed refit counted" to "set aside". The whiskers are the most salient marks on the page (e.g. −0.24 to 0 for chorus_norm in the replicate), so a fluent reader will see a huge interval crossing zero. The legend does not save it: the idiom is recognized before the legend is read. · **major** · Redraw so it cannot be read as an interval. Draw an arrow from hollow to filled, or show the failed-refit fold as a separate labeled marker in its own sub-row with no connecting line, or drop the with-failure value and state it in text. · verified yes (render)

4. **Figure 9B** · The x axis is labeled in seconds (0, 2, 4, 8, 16, 30 s) but spaced evenly, with connected lines. Readers read slope as F1 per second, so the rise from 16 to 30 s looks as steep as the rise from 2 to 4 s. The caveat "evenly spaced, not to scale" is text trying to fix what the chart shape says. Also, the CoactDetect and LoCo rings overlap at 8 s with the chorus_norm line passing through, so a reader cannot tell whose ring is whose. · moderate · Use a log-2 spaced axis with the 0 s point shown as a broken-axis stub, or drop the connecting lines, since these are categories. Offset or label the two rings at 8 s. · verified yes (render)

5. **§3 / Table 1: the nets' mechanism is not illustrated** · The brief asks for "figures to explain conceptually what was done". The report says the key difference between nets is "where each stops treating ROIs separately… a bounded vote, then pool the votes". The drawings are only "listed in section 12" and live on an unmerged PR. No figure shows what a net or CoactDetect actually computes. The nets are half the comparison, and the time-shifted null that CoactDetect and LoCo rest on is also only named. · major · Embed the existing draughtsman comparison drawing, or add a simple schematic: per-ROI trace → bounded vote → pooled votes → per-frame probability → threshold → calls, next to "pool first" for tube. Add a small panel for "count coincident ROIs, compare with a time-shifted copy". · verified yes (the report points to a drawing it does not include)

6. **Net names are code identifiers** (chorus_norm, chorus_gain_norm, line_length, tube), used in the prose, figures and tables throughout · The report admits it ("known by their names in the code"), but the names carry no meaning to a stranger, and "line_length" misleads: it sounds like a line-length feature, not a net. · moderate · Give each a plain-language label on first use and in figure row labels (e.g. "vote-pooling net (chorus_norm)"). At least gloss each on its first use outside Table 1. · verified yes

7. **Table 2 caption** · "a coded choice that fails the crowded-recording check, or under the budget is not admissible (section 4.5), gets its difference and no *t*" does not parse. · moderate · Rewrite, e.g. "A coded choice that fails the crowded-recording check (F1 alone), or that is not admissible (under the budget), gets its difference but no *t*." · verified yes

8. **"Quiet" / "busy" background never named** · §2 gives two rates (0.0052 and 0.019 firings per second per ROI) without calling them quiet and busy. The names first appear in the lede, the Fig 1 caption and §4.4. "Busy" also collides with §1's "the whole field sometimes becomes busier", which is the probe. So "nets find more faint events against a busy background" can be read as "during the busy stretches". · moderate · In §2, write "the **quiet** background, 0.0052…, and the **busy** background, 0.019…", and add one clause saying the busy background is a steady higher rate and is not the probe. · verified yes

9. **§4.5, "the setting it replaces"** · The relative phrase has no referent until §9 (the search's starting setting, or the shipped setting). "So the check sees gaps wider than about 6 s" is also opaque. · moderate · Name the referent in §4.5. Rephrase the second sentence, e.g. "so only merge gaps wider than about 6 s can be penalized by it". · verified yes

10. **§4.2 and Figure 4** · (a) "picks its threshold on the last two" reads as the last two of the run of 10. Figure 4 shows the last seed *of the whole list* (1047), far from the fitted cells. (b) Nothing says why a *training* seed (defined in §4.1 as "the random start of a net's training") decides *which recordings* are fitted. · moderate · (a) Write "the last two recordings of the list". (b) Add a clause: "the training seed also picks where in the list the run of 10 starts". · verified yes

11. **§2, "read the order of its rows, not their third decimal place"** · The referent "its rows" is undefined. The warning also sits awkwardly beside headline margins of 0.007–0.010 F1. · minor · Say what the rows are (e.g. "its ranking of detectors"). Consider pointing forward to where the report relies on third-decimal differences. · verified yes

12. **Figures 10 and 12: unexplained outliers** · One chorus_gain_norm fold sits at about −0.15 in every row of Fig 10A, and two dots sit at about −0.13 in Fig 12. They are the failed refits of §10, but neither caption says so. · minor · Add a caption clause: "the far-left dot is fold 3, which holds a refit that failed to train (section 10)". · verified yes (render; the identity is inferred from §10's list)

13. **§6 bullets: "refits that failed to train"** · Used with no pointer to §10, where the failure signature is explained. · minor · Add "(section 10)". · verified yes

14. **§9, "switched off the window its credit is for"** · "Credit" (meaning the literature attribution in Table 1) is obscure. · minor · Rewrite as "switched off the local-gap window that is SPIKE-synchronization's defining feature (Table 1)". · verified yes

15. **Table 3 headers** · Two columns are both headed "folds passing". · minor · Head them "passing vs starting" and "passing vs shipped". · verified yes (render)

16. **Units and code identifiers in prose** · §10: "differs by up to 106 per hour" has no noun (106 false alarms per hour). The lede carries a repo path (`docs/goals/learned-model-family.md`). §11 uses "export folder" undefined. §9 mentions `crowded_check.json`. §12's ARCHITECTURES/build_chorus_norm() warning is developer text. · minor · Add the unit. Move the repo path to §12. Gloss "export folder" ("the lab's exported event lists"). Keep code identifiers in §12 only. · verified yes

17. **Terms box** · CoactDetect and LoCo are named before they are introduced. The "frame" length (0.1 s) first appears only in §7, though Table 1's caption uses "frame". · minor · Add "(two of the coded detectors, Table 1)" and state the 10 frames-per-second rate in §2. · verified yes

18. **§1, the probe** · The probe is not tied to the problem it models ("the whole field sometimes becomes busier for minutes"). · minor · Add "the probe stands in for those busy stretches". · verified yes

## Checked with no finding

- **Tone:** headings are in sentence case, with no stray capitals or all-caps emphasis. Lists are formatted as lists, and no list is packed into a title or legend.
- **Numbering:** all 12 figures and 3 tables are numbered, and prose references carry both number and name.
- **Figure idioms:** Fig 1B is a true raster with conventional axes. Figs 3 and 4 use the cross-validation grid idiom correctly. Figs 5 and 6 are clearly marked schematics. Figs 7, 10, 11 and 12 are dot strips whose axes mean what they appear to mean.
