GRANT 8 ok — Read, Grep, Glob

# Naive-reader review: `docs/learned/slow_comodulation/README.md` and its six figures

**What I checked:** I read the whole page in order, as a stranger. I opened all six PNGs and checked every panel. For Figure 3, the drawing of the three surrogates, I measured the tick positions in pixels to see whether the drawing does what its labels say. I also grepped the page for jargon (`hot`, `dense block`, `arm`, `producer`, `review role`, `folds`, `OPERATING_POINTS`, `baseline`) and confirmed the figure conventions in the worktree's `CLAUDE.md`.

## Per-location verdict

| location | terms, identifiers, symbols and units first used here | defined here? | can a cold reader follow? |
|---|---|---|---|
| Title | co-modulation, rigid shift | neither | no |
| "Why this page exists" box | rigid shift, "paid for", label-free detector thread, "item 2 of *What waits on Tony*", baseline windows, milestone, **Measured** / **argued**, 95 % interval from resampling mice, ⚠ | only measured/argued; the rest are not | no (a reader gets the gist, but "rigid shift" is the subject and is never explained) |
| **"What the page finds" and Figure 1** | ROI, onset, population onset count, circular shift, rigid shift, *J*, block control, CoactDetect, episodes, lab fast stream / slow stream, benchmark generator, Dard et al. dataset, onset pairs, paired difference, "arm" (inside the figure), dense block, "producer" | Only "population onset count", and the ratio as "1 means no shared structure". The caption sends the rest "below" | **BLOCKING**: about 15 terms are used before they are defined, and the page's headline result sits here |
| "Two ways ROIs are active together" | ROI, onset, stream (fast/slow), lit, coordinated event, shared modulation, drift, label-free detector, surrogate, rigid shift, *J* | all yes, except "the producer" (never said who that is) | yes |
| "Telling them apart: the cross-correlogram" | *τ*, excess coincidence, independence level, onset pairs, pooling weight, *T* | all yes | yes. The correlogram is named, not drawn, which is acceptable for this audience |
| Figure 2 caption | planted-event world, 20 s world, 5-minute world, `generator_spec.json`, dense block, distractors, log-normal multiplier | Worlds yes. "Distractors" no. "Dense block" is defined on line 47 but the figure calls it **"hot window"** | yes, apart from the name mismatch below |
| Brody paragraph after Figure 2 | "paid back", zero by construction | yes | yes |
| Figure 3 caption | circular shift, "the null", block control, "drawn from fixed numbers" | yes | yes |
| Figure 4 caption and bullets | **arm**, trimmed window, "whole spec", `hot_window` (a code field name) | trim yes. "Arm" no, `hot_window` no, "whole spec" no | yes, with friction |
| **Figure 5 caption** | field steps, approved export, declared baseline, CoactDetect (first definition, four sections after first use), episode, rolling context window, **α**, `bench.OPERATING_POINTS`, `coact_detect`'s docstring, retuned slow point | CoactDetect and episode yes. α, declared baseline, approved export, operating point / retuned slow point and both code identifiers: no | **BLOCKING**: five or more undefined terms, symbols and identifiers |
| Figure 5 bullets ("Lab fast", "Lab slow", "Dard et al. dataset") | real-against-shifted contrast, "+0.01 per pair" | no, no | yes, but see the bad pointer to Figure 4 panel A |
| "Why the slow stream dips" | extractor dead time, "review role", "the source" | dead time yes; "review role" and "the source" no | mostly |
| "Numbers behind Figures 1 and 5" (collapsed) | arm, paired differences, quartiles | paired yes; arm no | yes |
| **"What this changes for the label-free thread"** | 10 s scorer, **0.669 / 0.522 (no metric, no unit)**, `tools/check_small_j_mixes_events.py`, shas, branch name, `count_excess`, no-training baseline, simulated folds | none | **BLOCKING**: scorer, the unnamed metric, `count_excess` and folds are all undefined in the two last bullets |
| "The decision this sets up" | FOUNDATIONS §9, `syncytium2/foundations` §15, producer | no | mostly; an outside reader cannot follow the § references |
| "What this does not settle" | full bins, whole-window means, field-step gap | yes | yes |
| Figure 6 caption and text | DI, MALE, ORX, OVX, pooled vs equal-weight, heaviest mouse | yes (with a ⚠ on the expansions) | yes |
| Published lineage / Reproduce | dithering, interval jitter, `--resummarise` | enough for this audience | yes |

## What a cold reader sees in each panel, and the false-friend check

A false friend is a plot that looks like a familiar chart type but whose axes mean something different.

**Figure 1, the count-swing bars**
- **A–D:** groups of coloured bars climbing a log axis from an unlabeled floor near 0.55, with a dashed line at 1.
  - **Looks like:** a grouped bar chart, where bar length means value measured from zero.
  - **Here:** length means log(value ÷ an arbitrary floor).
  - **Verdict: false friend.** The 0.59 green bar in panel B reads as a short positive bar, not as the dip below 1 that it is. Bar heights are not proportional to the ratios.
- **Hatching** on the green bars is unexplained.

**Figure 2, the three synthetic worlds**
- **A–C:** jagged step lines of "share of ROIs lit".
  - **A:** tall one-bin spikes.
  - **B:** broader bumps.
  - **C:** looks like noise; by eye the 5-minute drift cannot be told apart from B or from background.
  - **Looks like:** a population-rate trace or PSTH (peri-stimulus time histogram), and the axes do mean the same. Not a false friend.
  - A–C carry no world names; the coloured names sit above D–F.
  - A spans 58 minutes and B and C span 20 minutes at the same width, so A looks spikier partly because it is compressed.
- **D–F:** rasters of 32 rows over 1 minute.
  - **D:** a thin column of ticks near 33 s, plus a very salient **horizontal row of about 14 ticks in one ROI**. The caption does not explain that row, and it says distractors are off.
  - **E:** loose clustering around 35–47 s.
  - **F:** scattered ticks with nothing to see (by design, but unexplained).
  - **Looks like:** a raster, and the axes mean the same. Not a false friend.
- **G:** four curves against a log lag axis. Pink and brown shoulders, an orange peak that drops by 1 s, and a dotted line at zero.
  - **Looks like:** a cross-correlogram.
  - **Normally:** a symmetric, linear lag axis with zero lag in the centre.
  - **Here:** one-sided and logarithmic, with zero lag never drawn. The leftmost point (about 0.2 s) holds lag zero, but nothing says so.
  - **Verdict: partial false friend.** H is the prescribed fix, but only here.
- **H:** the same curves on a linear axis. The orange peak collapses to a sliver at 0 s; brown stays up past 2 minutes. Reads correctly.

**Figure 3, the three surrogates drawn**
- **A:** four ROI rows with ticks; all four line up at 1m40s. A raster, and it reads as one.
- **B:** the same ticks moved by small amounts; the alignment at 1m40s is broken. I measured offsets of +9, −12, +4 and +15 s.
  - **Nothing leaves the window**, so the "dropped" in the panel label is named, not shown.
  - *J* is not given.
- **C:** four new-looking trains.
  - I checked the wrap: the lags are +70, +150, +30 and +200 s and every tick is consistent.
  - But no tick can be traced back to panel A, so the reader has to trust the label.
- **D:** as C, with a purple dashed line at 2m.
  - **ROI 4's tick sits exactly on the dashed block edge** and is hidden by it; which block it belongs to is ambiguous.
  - The per-block counts check out.
- All four panels are rasters, so no false friend. But the headings above the plots break the "no titles above plots" convention (a boundary item for agent 10).

**Figure 4, each world against every surrogate**
- **A:** a black peak that is gone by 1 s; a light-blue plateau to about 2 s; everything else at zero.
  - The prose says rigid shift's plateau reaches "about 2*J*". That is visible only for *J* = 1.6 s; the 10 s and 20 s plateaus are about 0.01 high and cannot be seen.
- **B:** stepped plateaus below the black curve, ordered by *J*, with purple lowest.
- **C:** all rigid-shift curves lie on black; purple sits slightly lower.
- **D:** a black curve on a 0–1.75 y-scale (unlike A–C) with a shoulder near 1.0.
- All four use the log-lag correlogram and share its partial false friend. **No linear view is given.**

**Figure 5, the recordings**
- **A–C:** tall black peaks with grey bands, collapsing to near zero.
- **D:** zoomed. Many crossing lines. **Where the grey and green bands overlap they make a dark olive third shade** from about 3 s to 5 minutes, and that shade is not in the legend. This is phantom structure.
- **E:** zoomed. A deep black dip to −0.56 near 3–5 s, with blue rigid-shift curves above it.
- **F:** zoomed. A small dip near 5 s and a flat purple line.
- The bottom row's y-labels **drop the dataset name** ("excess coincidence, zoomed / 84 recordings, 44 mice"), so D and E cannot be told apart without looking up to the top row.
- The log-lag partial false friend applies, and the caption does not repeat the warning from Figure 2.

**Figure 6, by group**
- **A:** coloured solid and dashed curves falling from off-scale peaks. **The brown dashed curve (ORX) shoots up to +0.6 at the last lag bin**, which is unexplained.
- **B:** a deep common dip near 3 s, then noisy curves.
- **C:** flat low curves near 0.05–0.2, with the brown dashed line spiking up again at 5 minutes.
- **D:** flat low curves; a yellow dashed line (MALE, equal-weight) stands clearly above the rest.
- In C and D the −0.8 to 0.8 y-range leaves most of each panel empty.
- The log-lag partial false friend applies again.

## Findings

| # | location | issue | severity | suggested fix | verified |
|---|---|---|---|---|---|
| 1 | "What the page finds" and Figure 1 | The headline figure and its four bullets use about 15 terms defined later: rigid shift, *J*, circular shift, block control, CoactDetect, episodes, ROI, onset, fast/slow stream, benchmark generator, onset pairs, paired difference, arm, dense block, producer. "Each defined below" does not help someone reading the result first. (Where the section sits in the page is agent 11's call; the missing definitions here are this role's finding.) | **blocking** | Put a five-line glossary box before Figure 1 (ROI, onset, stream, rigid shift with *J*, circular shift, block control, CoactDetect episode), each with a one-clause meaning. Or move Figure 1 and its bullets after "What the surrogates remove" and keep a two-sentence plain-language summary at the top. | yes |
| 2 | Figure 5 caption | α, "declared baseline", "approved export", "operating point / retuned slow point", `bench.OPERATING_POINTS` and `coact_detect`'s docstring are all undefined or are code identifiers. CoactDetect is first defined here, four sections after it is first used. | **blocking** | Say "α, the significance level of CoactDetect's test". Say "the baseline, the stretch recorded before any treatment". Replace both code identifiers with "the settings the repository's benchmark uses" (keep the identifiers in the Reproduce section). Define CoactDetect in the glossary from finding 1. | yes |
| 3 | "What this changes for the label-free thread", last two bullets | "tells … at 0.669 … at 0.522" gives no metric and no unit (probably AUC, the area under the ROC curve, but the page never says). "10 s scorer", `count_excess`, "no-training baseline" and "simulated folds" are all undefined. This also breaks the rule that every number carries its unit. | **blocking** | Name the metric and its chance level ("AUC 0.669, where 0.5 is chance"). Replace `count_excess` with "a baseline that counts lit ROIs and subtracts their 30 s moving mean". Replace "folds" with "held-out simulated recordings". Move shas and branch names into a provenance parenthesis. | yes |
| 4 | Figure 1, all panels | Bars on a log axis are a false friend: bar length reads as value from zero, but it is measured from an arbitrary unlabeled floor (about 0.55). Ratios below 1 (lab slow after removal: 0.59, 0.79, 0.86) draw as short upward bars rather than deficits. Relabeling will not fix this. | major | Redraw as dot-and-whisker on the log axis, or as bars that start at the dashed line at 1 and go up or down. Explain or drop the hatching. | yes |
| 5 | Figures 4, 5 and 6 | Every correlogram here uses a one-sided log lag axis. A correlogram reader expects a symmetric linear axis with zero lag in the centre, and on a log axis a sub-second peak and a minute-wide shoulder look equally wide. Figure 2 panel H corrects this, but nothing repeats it later, where the claims about the recordings are made. The leftmost point contains zero lag and nothing says so. | major | Repeat the one-sentence warning in the Figure 5 and 6 captions, and say "leftmost point: lags 0–0.3 s". Better: add a small linear-lag inset, or a linear version of Figure 5 panel D, which carries the main lab-fast claim. | yes |
| 6 | Figure 2 panel D title, panel G legend, Figure 4 panel A y-label ("no hot window"); Figure 4 bullet (`hot_window`) | The prose calls it the "dense block"; the figures call it "hot window" and the text uses the code field name `hot_window`. A stranger sees two undefined names for one thing, and one is an internal identifier. | major | Use "dense block" in every figure label and legend. Drop `hot_window` from the prose, or keep it only in the Reproduce section. | yes |
| 7 | Figure 5 bullet "Lab fast" → "(Figure 4, panel A)" | The text says the block control "makes a flat excess from events alone" and points to Figure 4 panel A. There the purple block-control curve sits at or just below zero; no excess is visible. A reader who follows the pointer finds the opposite. | major | Point to a panel where it can be seen (Figure 4 panel D), or give the number, or mark the sentence as argued. The factual side is for the evidence roles to adjudicate. | yes (by eye) |
| 8 | Figure 5 panel D | Where the grey band (as recorded) and the green band (episodes removed) overlap they make a dark olive third shade from about 3 s to 5 minutes. It reads as a third category that is not in the legend. | major | Draw one interval as outline or hatch instead of fill, or show only the as-recorded band in the zoomed panels. | yes |
| 9 | Figure 5 panels D–F | The zoomed y-labels drop the dataset name, so the panels are not labeled by what they show; the slow-stream dip panel reads the same as the fast-stream panel. | minor | "lab, fast stream, zoomed · 84 recordings, 44 mice", and so on. | yes |
| 10 | Figure 2 panels A–C | The world names appear only above D–F, so A–C are unlabeled. Panel C's 5-minute drift cannot be seen by eye, and the panel meant to show drift shows noise. Panel A (58 minutes) is squeezed into the same width as B and C (20 minutes). | major | Put the world name in each A–C y-label. Show a smoothed share, or the planted shared multiplier as a second line (these are not rasters, so the no-drawing rule does not apply), or use a longer bin for C. Show the first 20 minutes of A, or say it is compressed. | yes |
| 11 | Figure 2 panel D | The most salient thing in the panel is a horizontal row of about 14 ticks from one ROI in 1 minute. At the stated background rate of 0.0097 onsets per ROI per second (about 0.6 per minute) that is far too many, and the caption says distractors are off. A cold reader will ask what it is, and nothing answers. | minor | Explain it in the caption (for example, a high-rate ROI the generator keeps), or pick a zoom without it. | yes (by eye; cause not checked) |
| 12 | Figure 3 panel B | The label says "what leaves the window is dropped", but no tick leaves the window in the drawing (offsets +9, −12, +4, +15 s). *J* is not stated. | minor | Put one tick close enough to an edge that it drops out, and give *J* in the label ("*J* = 20 s"). | yes (pixel-measured) |
| 13 | Figure 3 panels B–D | No tick can be traced back to panel A, so the reader cannot watch the aligned event at 1m40s scatter. The mechanism is drawn, but its effect is not shown. | minor | Keep one ink and put each ROI's offset in its row label ("ROI 1 (+70 s)"), which fits the convention that identity goes in axis labels. | yes |
| 14 | Figure 3 panel D | ROI 4's tick lands exactly on the dashed 2-minute block edge; it is hidden and its block is ambiguous. | minor | Move that onset off the edge in the fixed schematic numbers. | yes |
| 15 | Figure 4 panel A vs the bullet "a low plateau reaching to about 2*J*" | Only the *J* = 1.6 s plateau can be seen; the 10 s and 20 s plateaus are about 0.01 high. | minor | Say "visible here for *J* = 1.6 s", or add an inset zoomed to ±0.05. | yes |
| 16 | Figure 6 panels A and C | The ORX equal-weight dashed curve jumps to +0.6 and +0.4 in the last lag bin. It is a salient feature with no explanation beyond "wander". | minor | Say in the caption that the last bin holds few pairs, or clip or mark it. | yes (by eye) |
| 17 | Figure 1 legend and panels C, D; Figure 4 caption; tables; "What this does not settle" | "Arm" (one condition: as recorded or one surrogate) is never defined. | minor | Define it at first use or replace it with "condition". | yes |
| 18 | "producer": lines 51, 62, 213, 289, 297 | Never says who the producer is (the lab's event-extraction pipeline). "Producer to explain" is one of the three options in the page's central decision. | major | At first use: "the lab's event-extraction pipeline that produces the export (the producer)". | yes |
| 19 | "Why the slow stream dips", first bullet | "measured by a review role" and "the source attributes it" use internal process jargon; "the source" has no referent. | minor | "measured in an earlier review of the rigid-shift report and not re-run here"; name the source. | yes |
| 20 | "Why this page exists" box; "The decision this sets up" | "item 2 of *What waits on Tony*", "FOUNDATIONS §9" and "§15" are bare enumerated labels (a `CLAUDE.md` violation), and outside readers cannot resolve the § references. | minor | Name the item ("the question of whether shared slow modulation counts as coordination"). Replace the § numbers with their topics ("the rule that facts about the preparation come from the lab's shared foundations document"). | yes |
| 21 | Prose references to figures throughout ("read off Figure 1", "Figure 4, panel A", "of Figure 1") | They carry the number but not the name the convention asks for ("Figure 3, the candidate field"). This is a boundary item for agent 10. | minor | "Figure 1, the count-swing bars", "Figure 4, the synthetic worlds against each surrogate", and so on. | yes |
| 22 | Figure 2 panels D–F headings; Figure 3 panel headings | Titles above plots break the "no titles above plots" convention. The Figure 3 headings do the needed work of saying what each panel shows, so they should be moved rather than deleted. This is also a boundary item for agent 10. | minor | Move world names and surrogate descriptions into the y-labels (Figure 2) or a text header outside the plot (Figure 3). | yes |
| 23 | "Dard et al. dataset" bullet: "+0.01 per pair" | The excess is a pooled normalised ratio, so "per pair" suggests a per-ROI-pair quantity the page never computes. | minor | "an excess of about +0.01, small, but summed over about 160,000 ROI pairs per recording …" | yes |
| 24 | First mention of the Dard et al. dataset ("What the page finds") | The fact that it is in vivo in mouse pups, which matters for reading its 15× swing, first appears four sections later. | minor | "(in vivo, in mouse pups)" at first mention. | yes |
| 25 | Prose group labels ("except MALE's equal-weight curve") | An ALL-CAPS export label sits in running text. | minor | "the intact males' (MALE) equal-weight curve", or put the label in code format. | yes |

**Mechanisms (illustrated or only named?):**
- **Illustrated:** rigid shift, circular shift and block control (Figure 3); the three kinds of activity (Figure 2).
- **Named only:**
  - How the correlogram is built (counting lagged pairs against the independence level). Acceptable for a neuroscientist.
  - CoactDetect episode removal.
  - "Dropped at the window edge" (finding 12).

**Tone:** headings are consistently sentence case, and nothing is in ALL-CAPS for emphasis. Bold is heavy but used consistently. Lists are formatted as lists.
