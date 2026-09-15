GRANT 8 ok — Read, Grep, Glob

# Role 8, "You Lost Me": round 1 review of the rigid-shift look README

**Artifact:** `<worktree>/docs/learned/rigid_shift_look/README.md`, plus all six PNGs in that folder and its `larger-displacements/` and `cossart/` subfolders. I opened every one.

**What I checked:** I read every section and every figure as a stranger. I opened each render before reading its caption. For each section and figure I noted:
- terms used there for the first time, and whether they are defined there;
- which chart type the image resembles;
- one sentence on what a stranger sees.

I checked terms against `docs/GLOSSARY.md`. For two terms the glossary lacks I used `docs/proposals/2026-09-10-surrogate-evaluation-overnight.md` (the group names) and `docs/proposals/2026-09-14-preregistration-is-rigid-shift-usable.md` (the count and threshold definitions).

## Main finding

The README never says why anyone wants a shift that "hides" and "removes". The word "surrogate" first appears in the very last line, and "negatives" and "negative class" first appear in the final two sections. A cold reader goes through five sections and six figures without knowing what the shifted copy is for.

The mechanism that explains every destruction curve is explained only once, in words, near the end of the Cossart section. That mechanism is: a shift spreads one event over 2*J*, so fewer ROIs share any one bin, and removal depends on whether that count falls below K. It is never drawn.

## Verdict per section and figure

Where a row says "blocking (by count)", the section introduces three or more undefined terms, which the checklist makes blocking.

| Section / figure | Terms and identifiers first used here | Defined here? | Can a cold reader follow it? |
|---|---|---|---|
| Header blockquote | pre-registration machinery; the thresholds 0.55, ±2 % and 0.25, with no quantity attached to each; "murderboarded"; `<darkroom>`; "lab folder" | none | **no, blocking (by count)** for an outside reader. It also says "Baseline windows of the lab folder only", but the Cossart section reads whole recordings. |
| The answer, short | rigid shift; fast and slow stream; displacement; planted coordination; "large event"; "2 s bin"; "the window"; DI; "the recording-identity run"; why hiding matters | only "hides", by paraphrase | **blocking (by count)** |
| What was measured: Leak | ROI (abbreviation); train; onset statistics; edge-band features; "the second review"; why uniform dither leaks; what "leak" means | rigid shift yes; dither partly | **blocking (by count)** |
| What was measured: Destruction | synthetic twins; "level"; coordination excess; the assessor; circular-shift null; homogeneous resample | K and retained share yes | **blocking (by count)** |
| What was measured: Count | occupied frames; edge-thinning control; why that control "must show a change" | none | **blocking (by count)** |
| Figure 1, leak and count at the planned displacements | forced-choice accuracy; why a 1.67–98.33 % range; meaning of the 0.55 line; meaning of the ±2 % band; why slow uses 1.4, 2.8 and 5.6 s while fast uses 1.6, 2.5 and 5 s | 0.55 and ±2 % are named, not explained | **blocking (by count)** |
| Figure 2, destruction at the planned displacements | the 0.25 dashed line (not mentioned in the caption at all); "95 %" of what; "large events"; why lines fall with K | none | **blocking (by count)** |
| Larger-displacements intro | "no leak rising with displacement" (awkwardly phrased) | — | yes, minor |
| Figure 3, leak and count at larger displacements | DI, MALE, ORX, OVX; "lower bounds" of which interval; the per-group numbers, which no figure shows | none | **blocking (by count)** |
| Figure 4, destruction at larger displacements | no new terms | — | yes for terms, but the 10 s and 40 s lines cannot be told apart |
| Cossart intro | "Cossart dataset" (no citation); "field"; the scaling rule behind K = 55, 73, 110, 146 | field is guessable | **no** (major) |
| Figure 5, Cossart leak and count | "events" as a stream name; "59 slices" where the text says 59 recordings; "upper bound" | none | **no** (major) |
| Figure 6, Cossart destruction | "events" stream label | the empty K = 146 point is explained | yes, minor |
| Reading | "the only candidate" (for what?); "upper bound" | — | mostly, minor |
| The K scaling makes removal easy | 283 ROIs (where it comes from is unstated); "the screen's review"; "at its settings" (bare "settings" is retired in the glossary) | the mechanism, in words | **no** (major). This paragraph is the key to Figures 2, 4 and 6, and it comes last. |
| What this cannot say | "an interface2 commit"; "a trained model" (the linear classifier is also trained); "the earlier screen"; "negatives" | none | **blocking (by count)** |
| The decision this sets up | negative class; surrogate (first appearance); DI nonstationarity | none | **blocking (by count)** |

## What a cold reader sees in each figure, and what the chart resembles

**Figure 1** (`fig1_leak_count.png`):
- **Left panels:** red dots with bars sit high, near 0.63–0.77. Blue dots with bars sit on a dotted line near 0.5, under a dashed line with no label. Each dot has a thick and a thin bar side by side.
  - It resembles a dodged dot-and-whisker plot. In that idiom, bars placed side by side are different groups.
  - Here they are the same estimate resampled two ways. The legend saves it, but only just (minor).
- **Right panels:** blue dots sit at zero inside a grey band. One grey dot sits at −5, at a fourth tick labelled "edge thinning 5 s (control)" on an axis titled "displacement J".
  - This is a mild false friend. The control reads as a fourth, larger displacement where the method fails.

**Figure 2** (`fig2_destruction.png`): six line plots. Each has a flat light-grey line at 1, a flat dark-grey line at 0, three blue lines falling as K rises, and a dashed line at 0.25 with no explanation.
- It resembles a dose-response panel, and the axes mean what that idiom expects, so it is not a false friend.
- The dashed 2.5 s curve and the dashed 0.25 line share a style.
- The legend is repeated three times.

**Figure 3** (`larger-displacements/fig1_leak_count.png`): the same layout as Figure 1. The blue slow-stream dots climb to and past the dashed line at 22.4 and 44.8 s. The DI breakdown that the caption and "The answer, short" rely on appears nowhere in it.

**Figure 4** (`larger-displacements/fig2_destruction.png`): the same layout as Figure 2. Most lines collapse onto zero. Four displacements share one colour and differ only by dash pattern, and the 10 s and 40 s patterns look nearly the same in the legend.

**Figure 5** (`cossart/fig1_leak_count.png`):
- **Left panel:** red dots are pinned at 0.99. Blue dots climb from 0.49 across the dashed line.
- **Axis labels:** the y-axis reads "events · forced-choice accuracy", which parses as a measurement ("events"), not as the name of the Cossart folder's single stream.
- **Right panel:** the same as Figure 1, labelled "59 slices".

**Figure 6** (`cossart/fig2_destruction.png`): one visible blue line in the right panel, falling steeply from 73 to 110. Everything else overlaps at 0. The legend lists five displacements, but only 1.6 s can be seen. The y-label "events · 1 s bin" reads like "events per 1 s bin".

No panel is unreadable. The problems are undefined meaning and one mild false friend, not panels I could not describe.

## Findings

*Verified against a source?* means I could check the fix against a repo file, not only reason about it.

| # | Location | Issue | Severity | Suggested fix | Verified against a source? |
|---|---|---|---|---|---|
| 1 | Whole README, especially "The answer, short" and "The decision this sets up" | The purpose is never stated. "Surrogate" first appears in the last line, and "negatives" and "negative class" only in the final two sections. A reader cannot tell why "hides" is good and "removes" is good. | blocking | Open with two sentences: rigid shift is a candidate *surrogate*, a copy that keeps each ROI's own timing and destroys cross-ROI timing. A self-supervised detector would train against it as negatives, so it must be indistinguishable per ROI ("hides") and must remove coordination ("removes"). | yes (GLOSSARY "surrogate", "leak", "destruction test") |
| 2 | "What was measured" | Rigid shift and uniform dither are named, not illustrated. They are the core mechanism, and the difference is visual: the whole train moves as one versus each onset moving on its own. | major | Add a small schematic at the top: a few ROI rows of ticks shown three ways (original, rigid shift, uniform dither), marking that within-ROI intervals survive the rigid shift. Per house rules, draw nothing on top of the rows. | no |
| 3 | "The K scaling makes removal easy", placed after Figure 6 | The only explanation of why retained share falls with K and with *J* comes after all four destruction figures that need it. | major | Move the worked example (an event spread over 2*J*, so about N/2*J* ROIs per 1 s bin, compared with K) into the Destruction bullet, before Figure 2. Keep the Cossart-specific conclusion where it is. | no |
| 4 | "The answer, short"; Figure 3 caption; Decision | DI, MALE, ORX and OVX are never defined anywhere in the README. "The recording-identity run" is unlinked. | blocking | Define them at first use: "DI, intact females in diestrus; MALE, intact males; ORX and OVX, gonadectomized males and females". Link the recording-identity result. | yes (`docs/proposals/2026-09-10-surrogate-evaluation-overnight.md:88`) |
| 5 | Figure 3 caption and "The answer, short" | The DI finding is the stated explanation for the slow-stream leak, and no figure shows it. | major | Add a per-group leak panel for the slow stream, or a small per-group table beside Figure 3. | no |
| 6 | Figures 1, 3 and 5, and their captions | The 0.55 line is labelled "dashed line 0.55" with no rule attached. The Reading then says "its upper bound crosses 0.55", so the reader must already know the upper end of the mouse range is what gets compared. The ±2 % band is likewise unexplained. | major | State in the Figure 1 caption: "dashed line: the signed leak threshold, compared against the top of the range over mice; grey band: the signed ±2 % count-equivalence band". | yes (preregistration proposal lines 259–262, 278–280) |
| 7 | Figures 2, 4 and 6 captions | The dashed 0.25 line is never mentioned in any destruction caption. It is explained only by a passing number in the header blockquote. | major | Add "dashed line: 0.25, the signed ceiling on retained share" to the Figure 2 caption. | no |
| 8 | Figure 1 and "The answer, short" | The slow stream's displacements (1.4, 2.8, 5.6 s) differ from the fast stream's (1.6, 2.5, 5 s) with no reason given. "About 11 s" and "22 s" in the text are 11.2 s and 22.4 s on the axes. | major | One sentence: slow displacements are matched to fast by root-mean-square displacement (or whatever the actual rule is). Quote axis values exactly. | partly (GLOSSARY *J* says other surrogates are matched by root-mean-square displacement; I did not confirm that rule produced these values) |
| 9 | "What was measured: Count", and the Figure 1 and 3 titles | "Occupied frames" is undefined. The titles say "onset count" while the axis says "occupied-frame change", and a reader cannot tell whether these are one quantity. The edge-thinning control is not described, nor why it must move. | blocking | "Occupied frames: frames holding at least one onset, so two onsets in one frame count once. Edge-thinning control: a surrogate known to lose about 4 % of onsets near window edges, included to prove the count measure can see a loss." Use one name in titles and axis. | yes (preregistration proposal lines 275, 284) |
| 10 | "What was measured: Leak" | "Edge-band features" and "the second review" are undefined and unlinked. "Onset statistics" is vague. "ROI" is never spelled out. | blocking (by count) | "Features: per-ROI onset count and interval quantiles, pooled over ROIs. Left out: counts in the 5 s bands at window edges, which [link to review] showed can see coordination under a shift." Spell out "region of interest (ROI)". | yes (surrogate-evaluation proposal lines 196, 233) |
| 11 | "What was measured: Destruction" | "The assessor", "circular-shift null" and "homogeneous resample" are project jargon, undefined here. "Level" means participation level, and that is unstated. | blocking (by count) | Gloss each in a clause. Replace "the assessor" with "the coactivity count". Write "per participation level". | yes (GLOSSARY "the assessor", "CoactDetect") |
| 12 | "The answer, short" | "Large event" is never tied to 50 % participation. "Removes 84–99 %" and "keep 29 %" do not say at which K, so the reader cannot find them in a figure. Bare numbers (0.52, 0.55–0.56, 0.62–0.68) do not name the quantity. | major | "…an event in 50 % of ROIs keeps 29 % at K = 3"; "leak accuracy 0.55–0.56". | no |
| 13 | "The answer, short", slow stream | "The window is narrow" collides with the 60 s analysis windows used throughout. It also hides that the "window" is a single tested displacement, 11.2 s. | major | "Only one tested displacement, 11.2 s, both hides and removes enough." | no |
| 14 | Cossart intro | The rule behind K = 55, 73, 110, 146 is unstated. They are the lab's 3, 4, 6, 8 of 31 ROIs expressed as fractions (about 10, 13, 19, 26 %) of 566. The figure axis still says "(absolute)". The glossary defines K as a percentage, so a reader who knows the glossary sees an absolute K and a contradiction. | major | "K was set to the same fractions of the field as the lab's 3–8 of 31 (about 10–26 %)". Relabel the axis to show both the count and the percentage. | yes (GLOSSARY K entry, lines 195–203; the arithmetic is mine) |
| 15 | Cossart intro and the K-scaling paragraph | "Cossart dataset" has no citation or pointer for an outside reader. "283 ROIs" is unexplained (it is 50 % of 566). | minor | Cite the source dataset once. Write "an event in 283 ROIs (50 % of 566)". | no |
| 16 | Figures 5 and 6, y-axis labels | "events" is the Cossart stream's name but reads as a quantity ("events · 1 s bin"). The Figure 5 caption says "one stream" without naming it. | major | Label it "stream: events · forced-choice accuracy", or name the stream in the caption: "the folder's single stream, called *events*". | no |
| 17 | Figures 1, 3 and 5, right panels | This is a mild false friend. The edge-thinning control is a fourth tick on the "displacement J" axis, so it reads as a larger displacement where rigid shift fails at −5 %. | minor | Separate the control with a gap and a vertical divider, or move it to its own narrow panel. | no |
| 18 | Figures 1, 3 and 5, left panels | The thick and thin bars sit side by side, a layout that normally means two groups. The 1.67–98.33 % range is an unusual number with no reason given. | minor | Say "96.67 % interval (0.05/3 two-sided, one per signed test)" in the caption. Consider overlaying the two bars rather than dodging them. | yes (preregistration proposal line 278) |
| 19 | Figure 4 (and Figure 6's legend) | Four displacements share one colour. The 10 s and 40 s dash patterns are nearly identical, and near zero the lines are indistinguishable. | major | Use a sequential colour ramp across displacements, as well as or instead of dash patterns. Keep dashes out of the style of the 0.25 threshold line. | no |
| 20 | Figure 2 caption against the figure | The caption says "20 % and 50 %" while the axis says "participation 0.2 / 0.5". "Bars are 95 %" does not say 95 % of what, and differs from Figure 1's interval without a reason. | minor | Pick one form (percent). Write "95 % bootstrap interval over the 20 twin pairs". | no |
| 21 | Header blockquote | For an outside reader, "murderboarded", `<darkroom>` and "lab folder" are undefined. "Baseline windows of the lab folder only" is contradicted by the Cossart section. "One figure he reads himself" sits above six figures. | minor for Tony, blocking by count for an outside reader | Rewrite the scope line: "Lab folder baseline windows; a Cossart run on whole recordings follows." Gloss or drop the internal-process words. | no |
| 22 | "What this cannot say" | "An interface2 commit" is unlinked and unexplained. "A trained model is a stronger learner" (stronger than what, when the classifier is also trained?). "The earlier screen" is unlinked. "Negatives" is used before it is defined. | blocking (by count) | Link the commit and name interface2 as the lab's MATLAB predecessor. Write "a nonlinear model trained on the same features". Link the screen proposal. Define negatives, or rely on the fix in finding 1. | partly (the screen proposal exists at `docs/proposals/2026-09-10-surrogate-evaluation-overnight.md`) |
| 23 | K-scaling paragraph | "At its settings": bare "settings" is retired in the glossary. | minor | "At its K of 3–8 ROIs", or whichever parameter set is meant. | yes (GLOSSARY lines 150–153) |
| 24 | Figures 1, 3 and 5 against the text | The figures say "84 slices" and "59 slices" while the text says recordings. An outside reader may not know a slice is a recording. The lab frame interval is never given, yet "one frame of jitter" relies on it. | minor | Use one word, or gloss "slice (one recording)". Give the lab frame interval once. | yes (GLOSSARY "slice") |
| 25 | Figure 3 caption; "MALE" | ALL-CAPS group code inside prose. | minor | Keep the code as data, but define it (see finding 4) so it does not read as emphasis. | no |

## Boundary notes

- I did not check whether the quoted numbers match the renders; that belongs to other roles. I did notice that the Figure 1 caption says the fast control reads −4.6 %, while the fast right panel shows about −4.8 %. The role that checks numbers should look at it.
- "Not murderboarded" in the header will be stale once this review finishes. That is a factual staleness issue for another role, not a readability finding.
