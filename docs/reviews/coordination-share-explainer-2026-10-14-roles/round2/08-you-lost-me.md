GRANT 8 ok — Read, Grep, Glob

Role 8, the naive-reader review ("You Lost Me"). Edits made: none.

**What I read:** README.md in `c:\Users\defazio\bugarach\bugarach-worktrees\coordination-share-explainer\docs\learned\coordination_share_explainer\`, all six PNGs beside it, and `docs/adr/0014-a-figure-page-is-figures-then-controls-then-text.md` in the same worktree. I did not open the generator, the tool or numbers.json. I wrote each figure verdict with the render open and with only the README text that comes before that figure in mind, which on this layout means the legends of the earlier figures.

## Verdict on the layout rule (ADR-0014)

The page follows the rule. ADR-0014 point 5 lists "explainers" under points 1 to 4, so it is right that all six figures come before the text.

**For this audience, though, the rule defeats a cold reader from Figure 3 onward.** The six legends use about 15 terms before the Terms section defines any of them: fixed model, binomial model, pass band, the bench, quiet and busy background, mixed, ramps, pooled, and others. Figures 1 and 2 survive a cold reading. Figures 3 to 6 cannot be read until the reader has scrolled past all of them into the text.

The fix this role would normally ask for is a short definition in each legend. ADR-0014 point 2 forbids exactly that ("key to its colours, line styles and symbols. Nothing else"). So this is a conflict between the rule and the audience, and it is not mine to resolve silently. It needs Tony's ruling. Options:
- (a) Treat this page as a "written report" under point 5: lead with Figure 1 and put Figures 2 to 6 where the text discusses them.
- (b) Allow a legend to carry a few words defining a term on first use.
- (c) Accept that the page is read text-first, and say so under the title. Point 1 forbids that sentence.

## Per-figure and per-section table

| Unit | Terms and identifiers first used here | Defined here | Cold reader follows? |
|---|---|---|---|
| Title | coordinated, calcium events | yes, by framing | yes |
| Fig 1 | onset, "the measure", shared moment, planted, lane, close / medium pair, single moment, X, 1 s window, shifted copy | X, shifted copy, pair spacings, planted | **yes**. Only "onset" and "the measure" are undefined. |
| Fig 2 | busy background, f₂, f₃, "beyond chance", excess, k, cells per moment | f₂ and f₃ by axis words; k by the formula on the plot | **no**. "Busy" has no referent, "chance" means two things (finding 2.1), and "+2" is unexplained. |
| Fig 3 | fixed model, adopted, binomial model, pass band, right answer, the bench, the tool's built-in check, planted share | pass band (±25%), right answer | **BLOCKING**. Fixed, binomial, the bench, and the tool and its check are all undefined. |
| Fig 4 | median error, mixed, 120 s only, close / medium / very close pairs, participants per moment (k), moments per minute (λ), window length (w) | pair spacings; k and λ by axis words | **no**. "Mixed" is undefined, and "planted k" has no referent when sizes vary. |
| Fig 5 | stretch, busier, +0.1334 onsets/s/cell, sharp edges, the bench's 30 s ramps, ÷ background, quiet, 13× quiet, steady, rising 3× over 45 min, before / after subtracting | "busier" (relative to the background) | **BLOCKING**. Quiet (relative to what?), ramps, "13× quiet", "steady" and the 45 min recording length are undefined. |
| Fig 6 | ¼ quiet, pooled f₃/f₂, "15 / 6 / 3 moments" (per what length?), "on its own" | pooled over the 24 | **BLOCKING**, at the threshold. ¼ quiet, what f₃/f₂ estimates, and "per 45 minutes" are not given. |
| §The question | `fireflies`, baseline windows, treatment windows | none | **BLOCKING** for a public reader. `fireflies` is an internal repo name, and the two window terms are undefined. |
| §Terms | cell, onset, shared moment, window, X, N, k, λ, share | all of them | yes. It omits bench, stream, quiet / busy, fixed / binomial and pass band. |
| §How the measure works | f₂, f₃, excess, chance | yes | yes. Small gap: "+2" (finding 2.2). |
| §Does it get the right answer? | the bench, fast stream, 2026-10-07 bench intervals | fixed and binomial (here, after the figures) | **no**. "Bench" and "stream" are never defined anywhere on the page. |
| §What else it counts | elevated-rate level, "27 times … so 28 times in all" | partly | no (findings 5.2, 5.3) |
| §How far one recording strays | — | — | yes |
| §The simulated recordings | quiet (0.0049/s), busy (0.0169/s), decoys, mixed set, "Tony" | yes, but last | yes. It is the place where terms the figures needed are finally defined. |
| §Where the method comes from | cumulants, factorial cumulants, MIP, rigid shift | no | mostly. Names terms without explaining them (finding 7.1). |
| §What waits | export, default export, `senktide_ttx`, contamination stop, producer, stream, pinned, DI | DI only | **BLOCKING**. Five or more undefined project terms, including an internal identifier. |
| §For developers | code identifiers | n/a | Exempt: the audience is developers. |

## What a cold reader sees, one sentence per panel

- **1A:** A row of coloured down-triangles above the raster: two orange on the left, one green in the middle, a tight blue pair labelled "2 s pair" at the right.
- **1B:** A spike-raster-like grid of black ticks, 32 cells against time. Three vertical columns of ticks line up under the triangles, and one cell near the bottom (row 31) is bursty.
- **1C:** A bar trace of onset counts per 1 s window, mostly 0 to 2. Tall bars reach 6, 10 and 6 under the three columns.
- **1D:** A second raster that looks similar overall but has no vertical columns.
- **2A:** Paired green and black histogram bars on a log scale that match up to about 3. Beyond 5, only black bars remain (6 to 11).
- **2B:** Two clusters of green dots near zero, labelled f₂ and f₃, and a black diamond above each, with arrows labelled "excess 0.20" and "excess 1.21". A formula gives k ≈ 8.1 cells per moment.
- **3A–C:** Three scatters of filled and open circles around a horizontal line at 1.0, inside a grey band from 0.75 to 1.25. In A and C the filled circles sit mostly below the line. In B the open circles sit above it and some leave the band.
- **4A:** Five coloured lines across window lengths of 1, 2 and 4 s, all between −14% and −23%, inside a grey band.
- **4B:** The same five lines, all 25% to 70% above zero. The gold line is highest, and the blue line jumps at 4 s.
- **4C:** The same five lines, all 35% to 55% below zero. Gold is lowest, and blue drops at 4 s.
- **5A:** A hump-shaped median line with a grey band, peaking near 8% at 30 s to 1 min stretches and falling to about 1% at 15 min. The dotted "no stretch" line is almost on the zero axis.
- **5B:** A rising line from about 0.1% at 2× to 2.8% at 28×, with a grey band.
- **5C:** Four labelled rows of points. In the top two rows all points sit at zero. In the bottom two, open circles spread to the right (up to about 3) and filled circles stay at zero.
- **6:** Five pairs of beeswarm columns (open, filled) with orange median bars at about 0.8 and a line at 1.0. The 6- and 3-moment columns are visibly the widest.

Every panel can be described, so none fails as unreadable. Phantom structure: the 5A dotted line nearly merges with the zero axis, and in 5C the quiet rows hide the open circles (findings 5.4, 5.5).

## "What does this resemble" check, per figure

- **Fig 1:** B and D look like spike rasters (time on x, one row per cell), and they are rasters of onsets. C looks like a population histogram of counts against time, which is what it is. **Same meaning, no false friend.** The planted cues sit in a lane above the raster, as the house rule requires.
- **Fig 2:** A is a grouped count histogram with a log y-axis, and B is a categorical dot plot with annotations. Both match.
- **Fig 3:** The name "Planted against recovered" sets up a recovered-versus-planted scatter with an identity diagonal. The y-axis is actually the ratio recovered ÷ planted, with a horizontal line at 1. **Mild false friend from the name**: the axis label and the flat line correct it within seconds. Low severity.
- **Fig 4:** A line plot against a categorical, log-spaced window length. It matches.
- **Fig 5:** A and B are a median with a percentile band, which matches. C is a horizontal strip plot, which matches.
- **Fig 6:** A beeswarm with median bars, which matches.

## Findings (location · issue · severity · suggested fix · could I verify it against a source)

**1.1** · Page layout under ADR-0014 · The six legends come before every definition, so Figures 3 to 6 cannot be read cold. Point 2 of the rule forbids putting definitions in legends. · **High (the rule against the audience)** · Escalate to Tony: treat the page as a report under point 5, or allow first-use definitions in legends. Do not quietly break the rule. · yes (ADR text)

**3.1** · Fig 3 legend · Blocking: "fixed model (adopted)", "binomial model", "the bench" and "the tool's built-in check" are undefined at first use. · **Blocking** · Define them in a few words, e.g. "fixed: every moment the same size; binomial: sizes vary". This depends on 1.1. · yes

**3.2** · Fig 3 · The text says "All three medians pass", but no median is drawn, so a reader cannot check the claim from the figure. The band also invites the reading "every point must be inside". · Medium · Draw the median for each model in each panel, and put "the median must fall inside" in the band's key. · yes (render)

**3.3** · Fig 3 name · "Planted against recovered" promises a scatter with an identity line, but the y-axis is a ratio. · Low · Rename it, e.g. "Recovered ÷ planted, by planted share". · yes

**5.1** · Fig 5 legend and axes · Blocking: "quiet" and "13× quiet" have no referent (0.0049 onsets/s/cell is defined only in §The simulated recordings). "The bench's 30 s ramps" is undefined, and the legend does not say that A uses sharp edges while B uses ramps. "Rising 3× over 45 min" relies on a recording length no legend gives. · **Blocking** · Give the referents ("quiet background, 0.0049 onsets/s per cell"), define "ramp", and state the 45 min length. · yes

**5.2** · Fig 5C row labels against §What else it counts · "steady" means a constant rate in the row labels, but the prose says "a slow, steady change is removed" about the rising rows. One word has two opposite meanings. · Medium · Use "constant" in the row labels, or "gradual" in the prose. · yes

**5.3** · Fig 5A against its text · The prose says a stretch "is counted most when it is short", but the curve rises from 10 s (3.7%) to its peak at 30 s to 1 min. A cold reader sees a hump the text does not explain. · Medium · Add one clause explaining the 10 s point (e.g. it holds few onsets), or say "peaks for stretches of 30 s to 1 min". · yes (render)

**5.4** · Fig 5C, quiet rows · The open circles are hidden under the filled ones, so the reader sees no "before" data and may think it is missing. · Low · Add to the key: "in the quiet rows both sit at zero". · yes

**5.5** · Fig 5A dotted "no stretch" line, and the 5C bottom row label · The dotted line is nearly indistinguishable from the zero axis, and the label "45 min, 13× quiet" runs into panel B's area. · Low · Hand the mechanics to agent 10. Noted here because they hurt a cold reading. · yes

**5.6** · §What else it counts, line 177 · "About 27 times the quiet background, so 28 times in all" makes the reader do arithmetic to get the one number the figure uses. · Low · Say "28 times the quiet background (an added 0.1334 onsets/s per cell)". · yes

**6.1** · Fig 6 legend and axis · Blocking at the threshold: "¼ quiet" (a quarter of what?), what "f₃/f₂ pooled" estimates (k), and "15 / 6 / 3 moments" with no recording length. · **Blocking** · Write "15 moments in 45 min · quiet background ÷ 4" and "the size estimate f₃/f₂, pooled over the 24". · yes

**2.1** · Fig 2B and §How the measure works, step 1 against step 2 · "Pairs beyond chance" defines chance as independent, steady cells, yet the green dots *are* the measured chance and sit above zero at 0.03. A cold reader cannot tell which "chance" the axis means. · Medium · Label the axis "pairs beyond independent-steady expectation", or say in step 2 that the copies measure what the formula's "chance" leaves in. · yes

**2.2** · Fig 2B annotation and step 3 · "k = f₃ ÷ f₂ + 2" appears without connecting it to the 90-pairs / 720-triples example the text already gives. The formula also uses f₃ ÷ f₂ while the numbers plugged in are the excesses. · Low-Med · Add "720 ÷ 90 = 8 = 10 − 2", and write the annotation as "excess f₃ ÷ excess f₂ + 2". · yes

**2.3** · Fig 2 legend · "busy background" is a relative word with no referent. · Low · "busy background (0.0169 onsets/s per cell)". · yes

**4.1** · Fig 4 legend · "mixed" is undefined; it is defined only at line 226. · Medium · "mixed (2 close + 2 medium pairs + 7 singles)". · yes

**4.2** · Fig 4B axis · "Planted k" has no single value in the mixed and three-size sets. · Low · Name the referent, e.g. "the average planted size". · yes

**4.3** · Fig 4C axis against §Terms · λ is "per second" in Terms but "moments per minute (λ)" on the axis. The ratio cancels the unit, but the mismatch makes a reader stop. · Low · Use one unit in both places. · yes

**4.4** · §Window size, lines 144 to 149 and 151 to 153 · "measured after merging any two events less than 2 s apart. So the closest moments real recordings hold are the ones the bench never plants" does not follow for a cold reader. Lines 151 to 153 pack a list of conditions into one sentence. · Medium · Spell out the chain of reasoning in two sentences, and turn the conditions into a list. · yes

**0.1** · §The question, line 38 · `fireflies` is an internal repo name in audience-facing text, and "baseline windows" and "treatment windows" are undefined. · Medium (blocking row for a public reader) · "the lab's group-comparison analysis (`fireflies`)", and define baseline and treatment. · yes

**0.2** · Whole page · "The bench" and "stream" / "fast stream" are never defined anywhere, yet they are used in Figs 3 and 5 and in three sections. · **High** · Add both to §Terms: the bench is the simulated benchmark of planted coordinated events used to check the detectors, and "stream" needs the GLOSSARY's stream-axis meaning in one line. · yes

**8.1** · §What waits · Undefined project terms: export, default export, `senktide_ttx` (an internal identifier), contamination stop, producer, stream. · Medium (blocking row) · Rephrase: "the current data release from the lab's processing pipeline is on hold because…". Drop `senktide_ttx` or move it to §For developers. · yes

**8.2** · Lines 226 and 232 · "Tony" means nothing to a public reader. · Low · "the PI (Tony DeFazio)", or leave the name out. · yes

**7.1** · §Where the method comes from · "Factorial cumulants" is never connected to f₂ and f₃. "See the rigid shift entry…, which this tool's shift is not" points a cold reader at something irrelevant. · Low · "f₂ and f₃ are what statisticians call factorial cumulants"; give the rigid-shift contrast in half a sentence, or cut it. · yes

**1.2** · §2, line 86 · "Every cell has the same number of ticks" holds over the whole recording, not visibly in the 5-minute view. A reader who counts rows at the window edges may disagree. · Low · Add "over the whole 45 minutes". · partially (eye count of row 1 roughly agrees)

**9.1** · Legends of Figs 1, 4 and 5 · The keys are lists strung together with semicolons, which the tone rule discourages. ADR-0014 requires the key inline in the heading line, so this is a rule tension, not an author error. · Low · No change unless the ADR allows a list-form legend. · yes

**Tone:** sentence case throughout, no ALL-CAPS, and bold used for emphasis. No issue.

**Summary:** Figures 1 and 2 work cold, and Figure 1 is the right figure to lead with. Blocking: Figs 3, 5 and 6, §The question and §What waits. The one page-wide gap is that "bench" and "stream" are never defined (0.2). Finding 1.1, whether ADR-0014 suits a static explainer written for a cold audience, needs Tony's decision.
