> **Public copy.** Lines that concern real treatment recordings are removed (18 here), per FOUNDATIONS §5, and machine paths are shortened to `<scratchpad>`, `<worktree>`, `<darkroom>` or `<home>` (sapper SAP004). Everything else is verbatim.

GRANT 8 ok — Read, Grep, Glob

# Role 8, "You Lost Me": blind pass, round 2

**What I read:** all of `detector_review_plain.txt` in the order written. For Table 2 I used `detector_review_textview.html`, because the plain-text copy flattens the table's headers. I opened all 16 figure PNGs as images and read each one before its caption. I read twice: once as a bright 6th grader, once as a scientist from a nearby field.

**Result:** 5 blocking, 13 major, 17 minor. The document is honest and well organized, and most single-detector figures (3 to 7, 11A and 11B) read well cold. The reader gets lost in four places:
1. [line removed from the public copy: it concerns real treatment recordings (FOUNDATIONS §5); the verbatim report is in the darkroom delivery folder]
2. **"Busy" means three different things**, and some phrases put two of them next to each other.
3. **Several figures show something the caption contradicts, or leave it unexplained.**
4. **The prose is well above a 6th-grade reading level**: Sections 2, 3.6, 5 and Table 2.

## 1. Section and figure verdicts

"Undefined" means the term is used here before, or without, a plain explanation.

| Unit | Terms first used here | Defined here? | Can a cold reader follow? | What a cold reader sees in the figure |
|---|---|---|---|---|
| **In short** | F1 score, "call", five detector names (CoactDetect, LoCo, tube-guard, tube, rate+context), "sense of chance" | F1: no (defined in 6.1). Call: no. Names: no (Sections 3–4). | **blocking** (3+ undefined) | no figure |
| [line removed from the public copy: it concerns real treatment recordings (FOUNDATIONS §5); the verbatim report is in the darkroom delivery folder] |
| **§2 + Figure 2** | surrogate, shuffle, circular shift, bar, *percentile* (99.9th), log scale, decoy, *four groups of mice*, fast/slow stream | surrogate, shuffle, shift, bar, log scale: yes. Decoy: partly (see B3). Percentile: no (word list only). Four groups: no (§8). Stream: no. | **blocking** | A: three rasters; the shifted copy looks almost the same as the original, and the shuffled copy looks more scattered. B: two log-scale plots (fast, slow) where the dashed "real" line stays high while the colored lines fall. I could read that only after decoding the 10⁻³ notation. C: a count line with two bars and a shaded busy stretch where the gray bar fires constantly and the purple one never does, plus a planted ▼ near 16.4 min that no one called, which nothing explains (M4). |
| **§3 intro + Table 1** | *typical spread*, *checkpoint*, frame, SCE, "switched on", window A/B | frame, SCE: yes (table note). Typical spread, checkpoint: explained only later (3.2, 3.3). | no (major) | no figure |
| **§3.1 + Figure 3** | *time step* | no | yes | A blue rate line spikes over a dotted bar at the ▼. In the busy stretch the line jumps around under a raised bar and pokes over twice, at the two ✕ marks. |
| **§3.2 + Figure 4** | "in units of how far surrogate counts usually stray" | yes | yes, with the caption | A teal bar shoots up to 7. In B, gray dots sit near 4 and black dashes float near 10–12, well above the teal line. In A, the single black dash crossing the teal bar near 2.3 looks like part of the bar chart. |
| **§3.3 + Figure 5** | greatest-of rule (not named here) | yes | yes | A purple count and a stepped dotted bar; the count clears the bar only at the ▼. |
| **§3.4 + Figure 6** | none new | — | yes | In A a green step touches the dotted bar and the ▼ is red (missed). In B a solid row of green blocks with ✕ marks all the way across. |
| **§3.5 + Figure 7** | CICADA (expanded only in §11) | no | yes | A pink count crosses the bar at the ▼, with a small ○. In B it pokes over the flat bar about 15 times, with ✕ marks. |
| **§3.6 + Figure 8** | score from 0 to 1, "half of the shortest of four gaps", the 0.25 s cap | in words only; not drawn (M8) | **no** (M3) | Red dots near zero and an average-score line. **In B the line clearly crosses the 0.1 bar near 22m45s, yet the caption says 0 calls.** |
| **§4 + Figure 9** | neural network, training, call level, filter, *weight*, *scale* (legend), learning rate, *control* | network, training, call level, filter, learning rate: yes. Weight, scale, control: no. | no (major) | A: four panels of peaked curves at 0. The gray "surround" curves are invisible in the top two panels and appear only as two sharp spikes in the fourth. B/C: colored ticks and two long gray bars (trace, tiny) across the whole window, and a score line whose peaks at 0.95 and 0.97 cannot be told apart by eye. |
| **§5 + Figure 10** | simulator, *pipeline*, *median*, ⚠, mHz (used before its definition), bench, seed, percentile, variance | simulator, bench, seed: yes. mHz: two paragraphs later. Variance: loosely. Median, pipeline, ⚠: no. | **blocking** | A1/A2: two 45-minute rasters with ▼ and ▽ above and a dense shaded block in the middle. B: eight seconds of almost empty raster; I count about 8 faint ticks, not the stated 10. C: step histograms on a log axis, where orange (flat) is a single hump. D: three lines showing blue (fitted) above black (real) above orange (flat). |
| **§6 + Figure 11** | recall, precision, F1, round, limit, setting list, loosest/strictest | yes | yes | A: a clear diagram of hit, duplicate, false alarm and miss. B: a clear 4×24 grid of tiles. C: six small dot plots with overlapping ●, ▲, ■, green ○, purple ◇ and red ✕. **Here ✕ and ○ mean something different from Figures 3–9** (M10). |
| **§7 + Figure 12 + Table 2** | quiet/busy *level*, busy block, "floor", not meaningful | level versus block: no (M1). Floor: cryptic. | **blocking** (Figure 12C) | A: clear strip plots of F1 per detector. B: log-scale dots with red limit dashes, where SPIKE-synch's dot sits right on its limit. **C: filled gray-shaded circles for quiet, but every hollow circle is the same white, so for the busy level I cannot tell 30% from 18% from 10%**; the panel heading also says "quiet background". |
| [line removed from the public copy: it concerns real treatment recordings (FOUNDATIONS §5); the verbatim report is in the darkroom delivery folder] |
| [line removed from the public copy: it concerns real treatment recordings (FOUNDATIONS §5); the verbatim report is in the darkroom delivery folder] |
| **§10** | none new | — | yes | no figure |
| **§11** | Unitary Events, CFAR, port, transliteration, 10⁻⁹ | no, but this is a reference section | yes for a scientist; no for a 6th grader (acceptable here) | no figure |
| **§12 Word list** | — | "Stream" entry is empty of meaning; several entries only point elsewhere | see Section 3 below | — |

## 2. Findings, ranked

"Verified" means I checked the finding against the built text and the rendered PNGs myself. It is yes for every row.

### Blocking

| # | Location | Issue | Suggested fix | Verified |
|---|---|---|---|---|
| [line removed from the public copy: it concerns real treatment recordings (FOUNDATIONS §5); the verbatim report is in the darkroom delivery folder] |
| B2 | "In short", first bullet | F1 and "call" are used before they are defined, alongside five detector names nobody has introduced. The first thing an outside reader meets is a ranking in a unit they do not know, of programs they have not met. | "…scored about the same on F1, a 0-to-1 grade that is high only when a detector finds most planted events *and* most of its marks (its *calls*) are right…". Say "five of the twelve programs (described in Sections 3–4)". | yes |
| [line removed from the public copy: it concerns real treatment recordings (FOUNDATIONS §5); the verbatim report is in the darkroom delivery folder] |
| B4 | §2 and Figure 2 caption | "Percentile" (99.9th) is used here and throughout Table 1 but defined only in the word list, and it is the bar rule for four of the six hand-written detectors. "The four groups of mice" is also used here but defined only in §8. | Define percentile inline at first use: "the 99.9th percentile, the count that only 1 surrogate bin in 1,000 goes above". Add "(four groups of mice; Section 8)". | yes |
| B5 | Figure 12C, and the Figure 12 "B, C" heading | Hollow (busy) circles carry no shading, so the three event sizes cannot be told apart at the busy level. The heading says "quiet background" over a panel that also shows busy data. The text quotes busy recalls ("tube … 12%") that the reader cannot find in the figure. | Split C into quiet and busy sub-panels, each with the gray shading, or use three marker shapes for the sizes. Fix the heading. | yes |

### Major

| # | Location | Issue | Suggested fix | Verified |
|---|---|---|---|---|
| [line removed from the public copy: it concerns real treatment recordings (FOUNDATIONS §5); the verbatim report is in the darkroom delivery folder] |
| [line removed from the public copy: it concerns real treatment recordings (FOUNDATIONS §5); the verbatim report is in the darkroom delivery folder] |
| M3 | Figure 8B | The average-score line visibly crosses the 0.1 bar near 22m45s, but the caption says "0 calls". The reason (a call needs at least 3 events) is in §3.6 and is not connected to the figure. | In the caption: "one bin passes 0.1, but the stretch holds fewer than 3 events, so no call". | yes |
| M4 | Figure 2C and §2, last paragraph | The top lane shows a planted ▼ near 16.4 min that neither bar calls, while both bars call the two decoys. The text reports only "1 on a planted event and 2 on decoys". A reader asks why the real event is missed and the fake ones are found. The panel title "nothing planted in it" also reads as "nothing planted in the recording", which the ▼ marks contradict. | Give the sizes: say the missed event is a small one (10% of ROIs, if that is right) and the decoys are 18%. Retitle to "…a busy block with nothing planted inside the block". | yes |
| M5 | §5 "Decoys", and Figure 2 caption | **Why decoys exist is never said.** Figure 2 calls them "lineups we added that are not coordinated events", but §5 builds them exactly like planted events. To a cold reader that is a contradiction, and a call on a decoy being "wrong" looks unfair. | One sentence of purpose, for example: "decoys stand in for chance or unexplained lineups that a careful person would not count, so a detector cannot score well just by calling every lineup." Show the 0.71 cap as 15 ÷ (15 + 6). | yes |
| [line removed from the public copy: it concerns real treatment recordings (FOUNDATIONS §5); the verbatim report is in the darkroom delivery folder] |
| [line removed from the public copy: it concerns real treatment recordings (FOUNDATIONS §5); the verbatim report is in the darkroom delivery folder] |
| M8 | §3.6 SPIKE-synch, §3.3 LoCo, §4.1 center/surround | Non-trivial mechanisms are described only in words: the "half the shortest of four gaps" window, the two-sided "take the higher half" bar, and center-versus-surround filtering. Figure 9A shows the learned weights, not how the idea works. | A small schematic for each (one event pair with its four gaps and the window drawn; a timeline with the before and after minutes and the higher side picked), or one combined diagram panel. | yes |
| M9 | §2, "Why the shift and not the shuffle" | The chain *shuffle doubles up events → fewer distinct ROIs per bin → lineups look rarer → bar too low → more chance calls* sits inside numbers like "24.5 times per 1,000 events". It is far above 6th-grade level and easy to lose. | Lead with the four-step chain in plain words, then give the numbers as support. | yes |
| M10 | Figure 11C versus Figures 3–9 | Symbols change meaning between figures: ✕ means "false alarm" in Figures 3–9 but "breaks its busy-block limit" in Figure 11C, and ○ means "second call" there but "chosen in at least one round" here. In Figure 11C the ●, ■, green ○, ◇ and ✕ stack on the same point. | Use a different mark for "breaks limit" (for example a red outline square), and a filled green ring or tick for "chosen". Nudge overlapping markers apart. | yes |
| [line removed from the public copy: it concerns real treatment recordings (FOUNDATIONS §5); the verbatim report is in the darkroom delivery folder] |
| M12 | Figure 12B versus Table 2 | Figure 12B plots busy-block rates for trace and tiny, while Table 2 says those rates are "not meaningful". tube-ratio sits on the "floor: no calls drawn here" line, but the table gives 0.01. The reader cannot tell whether it made zero calls or 0.01 calls per minute. | Leave trace and tiny out of B, or mark them "not meaningful". Explain the floor: "a rate of 0 is drawn at 0.01 because a log scale cannot show 0". | yes |
| M13 | Whole document, against the brief | The brief asks for 6th-grade reading level. §2 (the shift-shuffle paragraph), §3.2 ("typical spreads", bell-shaped spread), §3.6, §5 and Table 2 (14 columns, two header rows) are high-school to college level. | Shorten sentences to one idea each, move numbers out of the explaining sentence, and consider splitting Table 2 into "accuracy" and "calls where nothing was planted". | yes |

### Minor

| # | Location | Issue | Suggested fix |
|---|---|---|---|
| m1 | Figure 3, 6 and 7 y-axis labels | Labels are clipped: "all ROI:", "10 s bi", "0.1 s fra". A cold reader loses the unit. | Shorten the labels or widen the margin. |
| m2 | Figures 3–9 key | The "a call" swatch is a gray square, but calls are drawn in each detector's color. | Use a neutral outline tick, or "a call (in the detector's color)". |
| m3 | Figure 9 legend | "green if any model in the lane found it": "the lane" is ambiguous. The legend swatch is dark red, but the lines are four different colors. | "The ▼ turns green if any of the four tube models found it"; per-panel color note. |
| m4 | Figure 9A | Gray surround filters are invisible in the tube and tube-guard panels, and "one line per scale" ("scale") is undefined. | Note in the caption that they are too shallow to see at this scale, or add an inset. Say "one line per center/surround pair". |
| m5 | Table 1, LoCo row | "Checkpoint" is undefined until §3.3. | Write "every 15 seconds". |
| m6 | Table 1 and §3.2 | "3.72 typical spreads" appears before the idea is explained. | Put the forward reference in Table 1 ("see 3.2"). |
| m7 | §3.1 | "For more than one time step": the step size is not given. | Give the step size in seconds. |
| m8 | §4.2 | "Controls" is undefined for a lay reader. | "Controls (deliberately simpler networks, to check that tube's design matters)". |
| m9 | §5 | "60 mHz" is used before mHz is defined two paragraphs later; "pipeline" is jargon. | Move the mHz definition up; say "the lab's event-finding program". |
| m10 | §7 SPIKE-synch paragraph | "No score between 0 and about 0.03 is possible with 33 ROIs": the arithmetic is not shown. | Add "(one other ROI out of 32 is 1/32 ≈ 0.03)". |
| [line removed from the public copy: it concerns real treatment recordings (FOUNDATIONS §5); the verbatim report is in the darkroom delivery folder] |
| m12 | §8 | "Fast-stream settings were also used on the slow stream" has no "so what". | Add "so the slow-stream calls may be mis-tuned". |
| [line removed from the public copy: it concerns real treatment recordings (FOUNDATIONS §5); the verbatim report is in the darkroom delivery folder] |
| m14 | Sentence starts | Lower-case detector names start sentences ("locust turns…", "binned SCE also…") and look like typos to a young reader. | Recast so the sentence does not open with a lower-case name. |
| m15 | §11 | "Ordinary two-level threshold", but §3.6 describes only one level (0.1). | Name both levels in §3.6, or say "one-level" here. |
| m16 | Figure 10B | Caption says 10 ROIs, but only about 8 ticks are visible and they are faint. | Thicken the ticks, or note that some overlap. |
| [line removed from the public copy: it concerns real treatment recordings (FOUNDATIONS §5); the verbatim report is in the darkroom delivery folder] |

## 3. Word list coverage

**Missing, though I needed them:**
- coordinated event
- calcium event
- F1 (has a pointer only)
- median
- variance
- log scale
- control
- filter, center, surround
- weight
- busy block, and how it differs from the busy level
- analysis window ("the part the lab marks")
- [line removed from the public copy: it concerns real treatment recordings (FOUNDATIONS §5); the verbatim report is in the darkroom delivery folder]
- SCE
- round
- learning rate
- ⚠

**Present but empty:** "Stream" (B1).

*[line removed from the public copy: it concerns real treatment recordings (FOUNDATIONS §5); the verbatim report is in the darkroom delivery folder]

## 4. False-friend check

For every figure I asked what it resembles, what the axes mean in that kind of chart, and whether they mean the same here.
- [line removed from the public copy: it concerns real treatment recordings (FOUNDATIONS §5); the verbatim report is in the darkroom delivery folder]
- **Detector lanes above rasters:** time across, one detector per row. They keep the event-plot convention and are clearly labeled. No mismatch.
- **Figure 2B, Figure 10C–D, Figure 11C, Figure 12:** conventional survival-curve, histogram and strip-plot grammar. No mismatch.
- **Figure 11B:** tiles are drawn as a clear grid, not scattered marks. No mismatch.
- **Figure 4A (one near-miss):** the lone black threshold dash crossing the teal count bar reads as a line inside a bar chart. It is listed under Figure 4 in Section 1 as a readability note, not as a false friend.

## 5. Files

Artifact read:
- `<scratchpad>\review\detector_review_plain.txt`
- `<scratchpad>\review\detector_review_textview.html` (Table 2 structure)

[line removed from the public copy: it concerns real treatment recordings (FOUNDATIONS §5); the verbatim report is in the darkroom delivery folder]
