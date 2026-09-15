> **Public copy.** Lines that concern real treatment recordings are removed (17 here), per FOUNDATIONS §5, and machine paths are shortened to `<scratchpad>`, `<worktree>`, `<darkroom>` or `<home>` (sapper SAP004). Everything else is verbatim.

GRANT 8 ok — Read, Grep, Glob

# Role 8, "You Lost Me": naive-reader review of `detector_review.html`

I read the text through `detector_review_textview.html` and opened all 16 figure PNGs in `...\review\_work\`. The bar I held it to is the stated one: an outside reviewer with no project context, who must be able to follow at a US 6th-grade level.

**Headline:** 10 of the 34 units are **blocking** (the rows marked so in the table). Two defects cost the reader the most:
1. **Figure 11C's x-axes are raw code parameter names**, and one of them is attached to the wrong detector.
2. **The comparison of now against nearby times that the learned detectors rely on (Figure 9A) can't be seen in its own picture.**

## Per-unit verdict table

"Undefined here" means not defined in that unit, or defined only somewhere a reader of that unit would not have seen. Blocking means three or more undefined terms, or a panel a stranger cannot read.

| Unit | Terms and identifiers first used here | Undefined here | Can a cold reader follow? |
|---|---|---|---|
| Title and "In short" box | detectors, coordinated events, simulated recordings, planted, false alarms, "written by hand" | "written by hand" (a 6th grader reads it as pen and paper); "simulated" | yes |
| §1 The problem | KNDy neurons, slices, dye, calcium event, raster, coordinated event | "KNDy" is never spelled out; "reproductive hormones" | yes |
| [line removed from the public copy: it concerns real treatment recordings (FOUNDATIONS §5); the verbatim report is in the darkroom delivery folder] |
| [line removed from the public copy: it concerns real treatment recordings (FOUNDATIONS §5); the verbatim report is in the darkroom delivery folder] |
| §3 Surrogates | shuffle, circular shift, rhythm, bursts | none in the prose | yes |
| Figure 2 | K, log scale, 10⁻⁴-style axis ticks, busy block, "bar from nearby 60 s" | log scale; exponent notation; Panel C swaps the colour code used everywhere else (see findings) | no |
| §4 intro | Window A/B, "the settings they ship with", lane symbols | "ship"; windows are given in seconds (400–580 s) but the figure axes are in minutes | yes |
| Table in §4 (no number) | the six detector names, SCE, frame, "switched on", 99.999th percentile | SCE (spelled out only in §4.4); "frame" (explained only in §4.5); nothing explains the names (LoCo? Coact?) | no |
| §4.1 rate+context | "surrounding minute", "joined" | none | yes |
| Figure 3 | "pooled event rate" | "pooled" | yes |
| §4.2 CoactDetect | "units of how much the surrogate counts vary", "candidate bin" | "how much counts vary" is a standard deviation or z-score in disguise, and the jump from that to "once in 10,000 bins" is not explained; "candidate" | no |
| Figure 4 | grey dots, black dashes, "rebuilt the bar from its own numbers" | "its own numbers"; a bar of 2.3 ROIs (a fraction of a cell); 6 cells planted but the count shows 7 | no |
| §4.3 LoCo | "higher side" | why taking the higher side helps is stated, not reasoned | yes |
| Figure 5 | bar that steps every 15 s | none | yes |
| §4.4 binned SCE | SCE (spelled out) | none | yes |
| Figure 6 | green call blocks | green also means "found" on the ▼ marker (see findings) | yes |
| §4.5 locust | switched on, frame, Cossart lab, CICADA toolbox, "data file", "event's length" | "toolbox"; where event lengths come from, given §1 says detectors get only start times | yes |
| Figure 7 | axis says "ROIs **active**", text says "switched on" | the two words mismatch | yes |
| §4.6 SPIKE-synch | "close", "the smaller half-gap", 0.25 s cap, 0.5 s gap rule | "half-gap"; the gap-based window is explained in one sentence with no picture; "synch" | **blocking** |
| Figure 8 | "synchrony per event", "mean synchrony" | synchrony; mean (the text says "score" and "average") | no |
| §5 intro | neural network, output level, adjustable numbers, tube models | "tube models" appears before tube is introduced; "18 simulated recordings (Section 6)", but §6 never mentions 18 | no |
| §5.1 tube and three variations | time filter, filter width, center, surround, brightness, `tube_guard`, `tube_ratio`, `tube_ratio_guard` | **filter** (the key idea, never defined); three code-style names with underscores | **blocking** |
| §5.2 trace and tiny | controls, "plain network", "filters each cell's row" | filter again | no |
| Figure 9 | weight, time filter, center, surround, "widened", call level 0.972, `tube_*` names | weight; filter; widened; drawing a *divided* surround below zero makes no sense | **blocking** |
| §6 Simulator | layers, busy block, decoys, bench, quiet/busy, 25th/75th percentile | "pipeline" | yes |
| Figure 10 | log₁₀ Hz, variance, burstiness, flat, fitted, `t` | log₁₀ Hz (the glossary unit is mHz); variance; burstiness; `t` | **blocking** |
| §7.1 Grading a call | claimed, closest-first | none | yes |
| §7.2 Choosing a setting | rounds, groups, "different random numbers" | why training starts from random numbers; says each learned detector was trained **three times**, but Figure 9's weaknesses box says **"Each was trained once"** | no |
| §7.3 Limit | limit, "past measured behavior" | where the limit comes from (a limit set from past behaviour sounds circular) | yes |
| Figure 11 | `excess_threshold_hz`, `alpha`, `threshold_pctile` (twice), `sce_percentile`, `C_threshold`, 1e-05-style ticks, "score" | 5 code identifiers; scientific notation; "score" never says F1; no legend inside the plot for the dashed lines | **blocking** |
| §8 Results | mean, training runs, "real time", "0.005" | "mean"; what SPIKE-synch's 0.005 is a value *of*; "the other two rules in Section 4.6", but §4.6 lists three | no |
| Figure 12 | held-out, training seed, log scale, "event size" | held-out; seed; exponent notation | **blocking** |
| Table 1 | lowest–highest round, confidence interval, speed | "confidence interval" is brought up only to say it doesn't apply, and never defined | yes |
| [line removed from the public copy: it concerns real treatment recordings (FOUNDATIONS §5); the verbatim report is in the darkroom delivery folder] |
| [line removed from the public copy: it concerns real treatment recordings (FOUNDATIONS §5); the verbatim report is in the darkroom delivery folder] |
| [line removed from the public copy: it concerns real treatment recordings (FOUNDATIONS §5); the verbatim report is in the darkroom delivery folder] |
| [line removed from the public copy: it concerns real treatment recordings (FOUNDATIONS §5); the verbatim report is in the darkroom delivery folder] |
| [line removed from the public copy: it concerns real treatment recordings (FOUNDATIONS §5); the verbatim report is in the darkroom delivery folder] |
| §10 table (no number) | "jumpy" | none | yes |
| §11 Not covered | none | none | yes |
| §12 Credits | cell-averaging detector, clutter, greatest-of rule, Unitary Events, jitter method | radar jargon; "cell" here means a radar cell, not a brain cell | no (low stakes) |

## Per figure: what a cold reader sees, and can they read it?

- **Figure 1:** A: a mostly empty 32-row grid with a few busy rows of tiny ticks at the top. B: a nearly empty grid with a column of about 6 dots under a black triangle. *Readable, but the "vertical stripe" the text promises is 6 specks. There is no visible stripe in A, and the one in B is hard to see.*
- **Figure 2:** A: three stacked tick grids; the bottom one looks clumpier. B: two log-scale plots of three falling lines, with the dashed line staying high. C: a shaded strip of orange triangles over a raster with a dense block, and a spiky grey line under a smooth blue line and an orange dashed line. *Readable only with the caption. Panel C reverses the colour code used in Figures 3–8 (there, colour is what the detector measures and grey is chance; here grey is the measure and colour is the bar). Panel B asks a 6th grader to compare lines on a 10⁻⁶ log axis.*
- **Figure 3:** A blue spiky line that pokes over a dotted line once in A and twice in B, with blue bars and red ✕ marks above. *Readable.*
- **Figure 4:** A teal staircase with floating black dashes and grey dots; in B the dashes hover far above the staircase. *Readable with the caption. The dashes look like a separate thing rather than "the bar", and a bar of 2.3 cells in A will puzzle a stranger.*
- **Figure 5:** A purple staircase under a dotted step line; it pokes over once in A and never in B. *Readable.*
- **Figure 6:** Wide green steps. In A, one step touches a flat dotted line under a red ▼; in B a row of green blocks, each with a ✕. *Readable. Green call blocks sit next to "green = found", so the false alarms look like successes at a glance.*
- **Figure 7:** A pink spiky count under a flat dotted line: one spike over it in A, many in B. *Readable.*
- **Figure 8:** Orange dots lying almost flat at zero, then a nearly empty bottom plot with a dotted line at 0.1. *Readable with the caption, but there is almost nothing to see. The row labels "synchrony" and "mean synchrony" use words the text never uses.*
- **Figure 9:** A: four plots of coloured bell-shaped peaks at zero, plus grey lines that hug zero. One plot has two sharp grey downward spikes at about ±0.9 s. B/C: seven lanes, a raster, a dark-red "% active, widened" line and a score line. **Panel A: not readable.** Surround widths of 2.6–16.3 s on a ±8 s axis draw as nearly flat lines, so the center-minus-surround comparison is invisible. The most striking marks (the ±0.9 s spikes in `tube_ratio_guard`) are explained nowhere. Nothing shows what a filter *does* to the brightness line.
- **Figure 10:** A1/A2: two long rasters with triangle lanes and a dense block. B: a few scattered ticks under a ▼. C: three overlapping staircase outlines on an x-axis of negative numbers. D: three dot-lines rising at different rates. *A and B are readable. C and D are not readable at this audience level (log₁₀ Hz, "variance ÷ mean"). D's x-axis (30, 60, 120, 300) is evenly spaced, so it looks like a straight number line when it is not.*
- **Figure 11:** A: green bands, triangles and blue blocks labelled hit, duplicate, false alarm, miss. B: a 4×24 grid of blue and grey tiles. C: six small line plots with rings, squares and ✕ marks over code-name x-axes. *A and B are readable. **C is not readable**:*
  - The x-axes are code identifiers.
  - The locust panel is labelled `sce_percentile`, so a stranger thinks it belongs to binned SCE.
  - Tick labels such as "99.9999999" and "1e-07" are unreadable at this level.
  - The x positions are evenly spaced list slots drawn as a continuous line: a line chart that implies a number line it doesn't have (a **false friend**).
  - "Stricter" runs right in some panels and effectively reverses in `alpha`, and nothing says which.
  - There is no blue square on SPIKE-synch, so the shipped value can't be found.
  - The red ✕ here means "breaks the limit", but in Figures 3–9 it means "false alarm".
- **Figure 12:** A: two dot-strip plots of F1 by detector with black dashes. B: blue and dark-red dots against red dashes on a log axis whose label is cut off ("…was plant"). C: grey-shaded dots per detector. *A and B are readable apart from the jargon.* **C: the caption says "one line per detector", but there are no lines.** The alt text says "against the percent of ROIs taking part", but the x-axis is detector names. Three grey shades are hard to tell apart, and the legend covers LoCo's 10% dot.
- [line removed from the public copy: it concerns real treatment recordings (FOUNDATIONS §5); the verbatim report is in the darkroom delivery folder]

*[line removed from the public copy: it concerns real treatment recordings (FOUNDATIONS §5); the verbatim report is in the darkroom delivery folder]

## Findings

Every row could be checked against a source: the PNG, or the text at the line cited.

| # | Location | Issue | Severity | Suggested fix |
|---|---|---|---|---|
| 1 | Figure 11C x-axis labels | Code identifiers `excess_threshold_hz`, `alpha`, `threshold_pctile` (twice), `sce_percentile`, `C_threshold` in figure labels. The locust panel reads `sce_percentile`, which points a stranger at the wrong detector. | blocking | Plain-language labels: "extra events per second above the average", "chance allowed (1 in N bins)", "bar percentile", "score level". Mark which direction makes the bar stricter. |
| 2 | Figure 11C ticks and y-axis | "1e-05", "99.9999999"; y-axis says "score" but means F1; no legend for the dashed lines inside the plot; list positions drawn as a continuous line; red ✕ reused with a new meaning; SPIKE-synch's shipped value is missing. | blocking | Write "1 in 100,000"; label the y-axis "F1 score"; add a legend; use markers without connecting lines, or say "values tried, in order"; use a different limit-break symbol; mark the shipped value (0.1) or say why it isn't on the list. |
| 3 | §4.6 and Figure 8 | SPIKE-synch's gap-based "close" window ("the smaller half-gap") is a mechanism named but not illustrated, and it can't be followed from one sentence. Figure labels say "synchrony"; the text says "score". §8's "the other two rules in Section 4.6", but §4.6 lists three. | blocking | Add a small drawing: two rows of events, the gaps, half of each gap shaded, the smaller one chosen. Rename the axis "score per event". Name the rules §8 means. |
| 4 | §5.1 and Figure 9A | "Filter" / "time filter" is never defined, yet it is the whole mechanism. Panel A's grey surround curves are nearly invisible (2.6–16.3 s widths on a ±8 s axis). The `tube_ratio_guard` ±0.9 s spikes are unexplained. "Weight" is undefined. A divided surround is drawn "below zero". | blocking | Define a filter as "a weighted average over nearby moments". Show one worked example: brightness line, center average, surround average, difference. Widen the axis or zoom the surround. Explain the spikes. Drop "or divided" from the below-zero sentence. |
| [line removed from the public copy: it concerns real treatment recordings (FOUNDATIONS §5); the verbatim report is in the darkroom delivery folder] |
| [line removed from the public copy: it concerns real treatment recordings (FOUNDATIONS §5); the verbatim report is in the darkroom delivery folder] |
| [line removed from the public copy: it concerns real treatment recordings (FOUNDATIONS §5); the verbatim report is in the darkroom delivery folder] |
| [line removed from the public copy: it concerns real treatment recordings (FOUNDATIONS §5); the verbatim report is in the darkroom delivery folder] |
| 9 | Figure 10C and D | x-axis "log₁₀ Hz" (the glossary unit is mHz and no log is explained); y-axis "burstiness (variance ÷ mean of counts)"; D's uneven widths are evenly spaced. | blocking | Label rates in mHz (1, 10, 100) or explain "each step is ×10". Say "how bunched (1 = not bunched)". Note the uneven spacing. |
| 10 | Figure 12 | "held-out", "training seed", exponent tick labels; the B y-axis label is cut off; the C caption says "one line per detector" but the plot has dots grouped by detector, and the alt text describes a different x-axis; the legend covers a data point. | blocking | "Recordings it was not tuned on"; "training run"; "0.01, 0.1, 1, 10, 100 calls per minute"; fix the clipping; fix the caption and alt text; move the legend. |
| 11 | Figure 9 weaknesses box vs §7.2 | "Each was trained once" contradicts "We trained each learned detector three times". The reader can't tell which is true. | high | Make the two agree. The Figure 12 dots suggest three runs. |
| 12 | §5 intro | "trained … on 18 simulated recordings (Section 6)", but §6 never mentions 18; the 18 = 3 groups of 6 split is in §7.2. | medium | Point to §7.2, or say "18 of the 24 test recordings". |
| 13 | Figure 2C vs Figures 3–8 | Colour code reversed: grey is the measure and colour the bar in 2C; colour is the measure and grey/black the chance estimate and bar in 3–8. | medium | Redraw 2C's count in a colour and its bars in black/grey dashes. |
| 14 | §2 Stream | "Fast" and "slow" are named but never explained: "fast" relative to what? The first use is in Figure 1. | high | One sentence on what makes the two streams differ, in plain terms. |
| 15 | §4.2 and Figure 4 | "Measured in units of how much the surrogate counts vary" and "rebuilt the bar from its own numbers" are opaque. A bar of 2.3 ROIs and a count of 7 for a 6-cell planted event go unexplained. | medium | Explain the bar as "average plus N times the typical wobble". Say the bar can fall between whole numbers. Note that one background cell joined the bin. |
| 16 | §4 intro | Windows given as "400–580 s" and "1290–1470 s" while the figure axes read 6m40s–9m40s and 21m30s–24m30s. | medium | Give windows in minutes and seconds to match the axes. |
| 17 | §4 table and §10 table | Neither is numbered or captioned (only Table 1 is). SCE and "frame" are used in the §4 table before they are defined. | medium | Number them (e.g. Table 1 in §4, Table 3 in §10) and add captions. Spell out SCE and define frame in the table or glossary. |
| 18 | Figure 6 (and all lanes) | Green call blocks sit beside the green "found" ▼, so false alarms look like successes. | low | Take green out of binned SCE's call colour. |
| 19 | Figure 7 | y-axis says "ROIs active"; the text defines "switched on". | low | "ROIs switched on in each 0.1 s frame". |
| [line removed from the public copy: it concerns real treatment recordings (FOUNDATIONS §5); the verbatim report is in the darkroom delivery folder] |
| [line removed from the public copy: it concerns real treatment recordings (FOUNDATIONS §5); the verbatim report is in the darkroom delivery folder] |
| [line removed from the public copy: it concerns real treatment recordings (FOUNDATIONS §5); the verbatim report is in the darkroom delivery folder] |
| 23 | §8 | "Mean" is undefined (the glossary uses "average"); "the lowest value, 0.005" doesn't say what quantity it is. | low | Say "average". Name the setting: "its score level". |
| 24 | Table 1 caption | "Not a confidence interval" brings up undefined jargon only to deny it. | low | Delete the phrase. |
| 25 | §12 | Radar jargon ("cell-averaging", "clutter", "greatest-of"). "Cell" means a radar cell here and collides with brain cells. | low | Add a short gloss, or "averaging detector used in radar". |
| [line removed from the public copy: it concerns real treatment recordings (FOUNDATIONS §5); the verbatim report is in the darkroom delivery folder] |
| 27 | "In short" box, §4 | "Written by hand" and "settings they ship with" are jargon or literal traps for a 6th grader. | low | "Programmed step by step by a person"; "their standard settings". |

**Outside my role, noticed and not adjudicated** (for agents 1 and 10): Figure 5's alt text says the planted event "reaches 6", but the image peaks at 5. Figure 12B's y-axis label is clipped.
