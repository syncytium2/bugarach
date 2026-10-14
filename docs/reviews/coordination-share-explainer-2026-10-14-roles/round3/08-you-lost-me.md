GRANT 8 ok — Read, Grep, Glob

(I also hold SubagentHandback, which is only the hand-off channel. I hold no editing tool and edited nothing.)

## Summary

The page mostly works as an explainer once you reach its text. It does not work for its stated reader, who arrives at six dense figure legends before any definition. The legend for each of Figures 1 to 6 introduces three or more terms that are defined only after Figure 6 (in *Terms*), so every one of the six is a **blocking** row under my output contract.

The cause is structural. Under ADR-0014 the page puts the figures first and allows only a key in each figure's heading line. The ADR's point 5 names "explainers" as figures-first pages, so the layout applies the rule correctly. For this reader I think the rule defeats the page. ADR-0014's reasons are a reader who opens a page again and again to work a figure, and controls that need to stay near it. This page has no controls and its reader reads it once, top to bottom.

Two figure-level defects are independent of the layout:
- **Figure 5C** uses an axis that is linear near zero and logarithmic beyond it (a symlog axis). It splits each row into what look like two clusters, and the "98% removed" result cannot be read off it.
- **Figure 3** puts its median bars on the data axis, where they read as data points.

## Per-figure verdicts (legend plus image, read before the Terms section, as the layout forces)

| Figure | Terms/identifiers first used here | Defined here | Cold reader follows? |
|---|---|---|---|
| 1. The count | shared moment, planted, "a lane the measure never sees", the measure, onset, tick, window, *X*, shifted copy, close/medium pair, single moment | the pair spacings, single-moment spacing (image legend), *X* = onsets per 1 s window | **BLOCKING**: shared moment, onset, the measure, shifted copy are undefined |
| 2. Same mean, wider spread | busy background, shifted copy, *f*₂, *f*₃, "beyond chance", excess, "the excess the measure keeps", *k*, "+2" in the in-panel formula | *f*₂/*f*₃ glossed as pairs/triples beyond chance; *k* given as a formula | **BLOCKING**: busy background, shifted copy, chance/"beyond chance", the reason for "+2" are undefined |
| 3. Recovered against planted | fixed model, binomial model, adopted, the bench, the tool's built-in check, recovered, planted share, "the mixed set of Figure 4" (a forward reference) | pass band (±25%, median must fall inside) | **BLOCKING**: fixed model, binomial model, the bench, the tool's check are undefined |
| 4. Window size and intervals | fixed model, mixed, "120 s only", *k*, λ, median error, pass band | pair spacings in the legend; *k*/λ glossed in the axis labels | **BLOCKING**: fixed model, mixed, "120 s only" are opaque names |
| 5. What else it counts | nothing planted, "worked out as one recording in a run with 24 recordings that do hold planted moments" (pooling), stretch, sharp edges, ramp, quiet, "13× quiet", shifted copies, *f*₂, "linear below 0.001" | percentile band, median, zero line | **BLOCKING**: pooling/run, quiet, shifted copies, the symlog axis are undefined |
| 6. How far one recording strays | "worked out on its own", "pooled *f*₃/*f*₂", quiet, busy, "¼ quiet", fixed model, planted share | median, 10th–90th percentile | **BLOCKING**: pooling, quiet/busy/¼ quiet, fixed model are undefined |

## Per-section verdicts (text)

| Section | Undefined at first use | Follows? |
|---|---|---|
| The question | senktide, `fireflies`, ADR-0017; "the tool" is never named; "bugarach" for a public reader | **BLOCKING** by count (3 or more). The fix is cheap (see F9). |
| Terms | "fast stream" is circular ("two named streams, fast and slow" never says what they are) | yes |
| Step 1 | "ordered pairs/triples" (why 90 and 720) | yes, until the last sentence |
| Step 2 | none | yes. This is the clearest part of the page. |
| Step 3 | none undefined, but "*k* − 2" and "λ*k*/*N*" lose a non-math reader | no (math, not terms) |
| The check, and the two models | `CAL_NO_PROBE` (code identifier); "elevated-rate stretch" (defined two sections later) | mostly |
| Window size | none ("mixed" and "120 s only" are defined here, too late for Figure 4) | yes, though dense with percentages |
| What else it counts | none | yes |
| How far one recording strays | none | yes |
| The simulated recordings | `simulate_coordination` (code identifier), "the correlogram's measured fast-stream jitter", standard deviation | no |
| Where the method comes from | cumulants, compound Poisson, multiple-interaction process, factorial cumulants, Poisson, shifting surrogate | **BLOCKING** by count. It is a citations section, so one plain gloss line is enough (F12). |
| What waits | none (pinning and DI are explained) | yes |
| For developers | identifiers are fine for this audience | exempt |

## What a cold reader sees, one sentence per panel

- **1A**: Colored down-triangles in a strip labeled "planted": two orange near the start, one green in the middle, and two blue stacked near the end, tagged "2 s pair".
- **1B**: A black-and-white raster, 32 rows of short ticks over 5 minutes, with visible vertical columns of ticks at about 30m25s, 32m32s and 34m45s under the triangles.
- **1C**: A bar trace of counts per second with tall spikes (10, 6, 4) under the same columns and mostly 0–1 elsewhere.
- **1D**: A second raster that looks like the first with the columns gone. However, rows 25 and 31 look almost identical to Figure 1B, so the reader may think those cells were not shifted (F4).
- **2A**: Paired gray and black bars on a log-count axis, nearly equal for 0–3 per window, with only black bars from 6 to 11.
- **2B**: Two clusters of gray dots near zero (f₂, f₃), a black diamond slightly above for f₂ and far above for f₃, arrows marking "excess 0.20" and "excess 1.21", and a formula box in the middle.
- **3A–C**: Clouds of filled and open dots of a ratio against the planted share, inside a gray band from 0.75 to 1.25, with short black bars and percentage labels parked at about 32% on the x-axis (F5).
- **4A**: Five colored lines across 1, 2 and 4 s, all between −14% and −23%, inside a gray band.
- **4B**: The same five lines, all 25–70% above zero, with the yellow line highest and blue/black rising steeply at 4 s.
- **4C**: The same five lines, all 35–55% below zero.
- **5A**: A hump-shaped median line with a gray band, peaking near 8% at 30s–1m and falling to about 1% at 15m, above a flat dotted line near zero.
- **5B**: A rising line from about 0% at 2× to 2.8% at 28×.
- **5C**: Four rows of dots. In each row the reader sees **two separate clusters**, one left of zero near −0.01 and one right of zero, on an axis whose ticks jump from 0.01 straight to 1. I cannot say from the panel how much was removed. This is the panel I could not explain.
- **6**: Five groups of open and filled dots with median ticks and vertical whiskers. Spread is narrow for "15 moments" and very wide for "6" and "3 moments", and every median sits near 0.8, below the 1.0 line.

## "What does it resemble" check

- **Figure 1B/D**: Resembles a spike raster (time across, cells as rows) and *is* one. Pass. **Figure 1C**: resembles a population histogram over time and is one. Pass. **Figure 1A**: an event lane above the raster with down-pointing markers, following house convention. Pass.
- **Figure 2A**: Resembles a histogram and is one. Pass. The y ticks are written as powers of ten (10⁰, 10¹), which a non-math reader does not parse (F7). **Figure 2B**: a dot plot with annotation. Pass.
- **Figure 3**: Resembles a scatter of recovered against true value (a Bland–Altman-like plot), and the axes match that idiom. However, the median bars sit on the continuous x-axis at about 32% planted share, a place where data could be, so they read as data points. **Partial false friend.**
- **Figure 4**: Resembles a dose-response line plot (a parameter on x, outcome on y) and is one. Pass.
- **Figure 5A/B**: Line plus band against a parameter. Pass. **Figure 5C**: resembles a forest plot (rows of conditions, effect on x, line of no effect at 0). The meaning matches, but forest plots are read as linear, and this axis is not. The symlog axis makes each row look bimodal and hides the size of the subtraction. **Fail (phantom structure).**
- **Figure 6**: Resembles a strip plot with median and range, and is one. The whisker glyph in the legend is horizontal while the whiskers on the plot are vertical (minor; the mechanical glyph check is agent 10's).

## Does the ADR-0014 rule defeat this reader? Yes, plainly.

- Under point 5 this page is an "explainer", so it falls under points 1 to 4: figures first, and only the key in each heading line.
- As a result the question the page answers, and every definition it needs, arrive after six figures and about 40 undefined uses.
- The ADR's reasons do not apply here:
  - a repeat reader scrolling past text they have already read;
  - controls drifting away from the figure they drive.

  This is a static README with no controls, read once by a stranger.
- Ways to fix it within the rule:
  - (a) Write every legend in plain words that need no Terms section: "▼ times when the simulation made several cells start an event together", not "shared moments".
  - (b) Use the page title, which is allowed above the figures, to carry the question.
- Outside the rule: (c) ask Tony whether a static, controlless explainer counts as a "report" under point 5. If it does, the page would lead with one main figure and place the others where the text discusses them. That decision is not mine, but the page as built shows the cost.

## Finding list (location · issue · severity · suggested fix · verifiable against a source)

**F1 · Figures 1–6 legends · the layout**
- **Issue:** Every legend relies on terms defined only in *Terms*, after Figure 6. All six figures are blocking rows.
- **Severity:** blocking.
- **Fix:** Rewrite each legend's panel descriptions in plain words ("onset = the moment a cell's calcium event starts"; "shifted copy = the same recording with each cell's events slid by its own amount"), or escalate the ADR-0014 point 5 question to Tony.
- **Verifiable:** yes (README lines 3–23 vs 52–73; ADR-0014 points 1–5).

**F2 · Figure 5C**
- **Issue:** The symlog x-axis (ticks −0.01, 0, 0.01, 1, "linear below 0.001") makes each row look like two clusters on either side of zero, and the claimed 98–99% removal cannot be read from the panel. Open points are also largely hidden under filled ones in the "quiet" rows.
- **Severity:** major.
- **Fix:**
  - Plot before and after as paired values per recording on a linear axis, one panel per background, or show the removal directly as a percentage.
  - If a log axis is kept, label it in words ("each step right is 100 times larger").
- **Verifiable:** yes (render).

**F3 · Figure 5C row labels**
- **Issue:** The label "rising 3× over 45 min, 13× quiet" runs into Figure 5B's plot area.
- **Severity:** minor.
- **Fix:** none from me. This is the boundary with agent 10, which owns the mechanical check; noted only because a stranger reads it as part of 5B.
- **Verifiable:** yes.

**F4 · Figure 1D / step 2**
- **Issue:** The shift is a non-trivial mechanism, and it is shown only as its result, never as the slide itself. Rows 25 and 31 look almost unchanged from Figure 1B, which suggests the shift skipped some cells.
- **Severity:** major.
- **Fix:** Add a small schematic of 3–4 rows sliding by different amounts with wrap-around, or print each row's slide in seconds at the right edge of 1D.
- **Verifiable:** yes (render).

**F5 · Figure 3 median bars**
- **Issue:** The median bars sit at about 32% on the planted-share axis and read as data. Their labels are in percent error (−18%) while the axis is a ratio (0.82). Figure 4 uses "recovered ÷ planted − 1" in percent, and Figures 3 and 6 use the plain ratio, so a stranger learns two scales for one quantity.
- **Severity:** major.
- **Fix:** Move the medians into a separate strip outside the data axis, and pick one scale for all three figures. The cross-figure rule is agent 3's; flagged here for readability.
- **Verifiable:** yes.

**F6 · Figure 2B in-panel formula and step 3**
- **Issue:** "*k* = excess *f*₃ ÷ excess *f*₂ + 2" and "λ*k*/*N*" have no plain-language route. "Ordered pairs/triples" is unexplained.
- **Severity:** minor.
- **Fix:** Say it in words once: "10 cells give 8 times as many triples as pairs, so the size is the ratio plus 2". Explain "ordered" as "counting A-then-B and B-then-A separately".
- **Verifiable:** yes.

**F7 · Figure 2A y-ticks**
- **Issue:** The ticks are written as powers of ten (10⁰, 10¹, 10², 10³), which non-math readers do not parse.
- **Severity:** minor.
- **Fix:** Label them 1, 10, 100, 1,000.
- **Verifiable:** yes.

**F8 · Figures 4 and 6 category names**
- **Issue:** "mixed", "120 s only" and "¼ quiet" are names a stranger cannot decode at the figure.
- **Severity:** minor (it feeds F1).
- **Fix:** Use "moments ≥120 s apart", "a quarter of the quiet rate", and "mixed: 2 close + 2 medium pairs".
- **Verifiable:** yes.

**F9 · *The question*, lines 39–46**
- **Issue:**
  - senktide is undefined (name it as a drug and give its effect in a few words).
  - "ADR-0017" is a lookup key, not content.
  - `fireflies` is a code name.
  - "the tool" is never named anywhere outside *For developers*.
- **Severity:** blocking by the 3-term rule; the fix is cheap.
- **Fix:** Gloss senktide; replace "ADR-0017" with the decision it records; describe `fireflies` once as "the lab's separate group-comparison analysis"; introduce "the tool" once, for example as "bugarach's coordination measure".
- **Verifiable:** yes.

**F10 · Line 136 `CAL_NO_PROBE`, line 257 `simulate_coordination`**
- **Issue:** Internal code identifiers appear in audience-facing text.
- **Severity:** minor.
- **Fix:** Use plain words ("the tool's own note"; "the bench's generator"). Keep the identifiers in *For developers*.
- **Verifiable:** yes.

**F11 · Lines 260–261**
- **Issue:** "standard deviation of 0.106 s (the correlogram's measured fast-stream jitter)" leaves a non-math reader with two undefined terms.
- **Severity:** minor.
- **Fix:** "each cell's onset lands within about a tenth of a second of the moment, the spread measured in real recordings".
- **Verifiable:** yes.

**F12 · *Where the method comes from***
- **Issue:** Six specialist terms with no gloss (Poisson, compound Poisson, cumulants, factorial cumulants, multiple-interaction process, shifting surrogate).
- **Severity:** minor (it is a citations section, but blocking by count).
- **Fix:** One opening line saying the section is for readers who know the statistics literature, plus "Poisson (events at random times at a steady rate)" where it is used.
- **Verifiable:** yes.

**F13 · Terms, "fast stream" (lines 69–71)**
- **Issue:** The definition is circular: it never says what distinguishes fast events from slow ones.
- **Severity:** minor.
- **Fix:** Add one clause on what makes an event "fast".
- **Verifiable:** no. I do not know the definition without opening other docs.

**F14 · Terms, "onset", and the illustrate rule**
- **Issue:** "Reaches half its rise" is a mechanism described only in text, and the page never shows a calcium trace.
- **Severity:** minor.
- **Fix:** Add a small inset trace with the onset marked, reusing `tools/make_diagnostic.py` traces if they fit.
- **Verifiable:** yes.

**F15 · Legends of Figures 3, 4 and 5 (tone rule)**
- **Issue:** The keys are lists strung together with semicolons and commas, and they repeat the legend inside each image.
- **Severity:** minor.
- **Fix:** Because the image legends already carry the key, cut the heading line to a one-line plain description per panel (allowed under ADR-0014 point 2 as "the key"), or format the key as a list.
- **Verifiable:** yes.

**Tone check:** sentence case is consistent and there are no ALL-CAPS. Bold is heavy but used for emphasis only. Lists are formatted as lists in the text. Nothing further.

## What I checked

- The README in full: `c:\Users\defazio\bugarach\bugarach-worktrees\coordination-share-explainer\docs\learned\coordination_share_explainer\README.md`.
- All six PNGs in the same folder (`explainer_coordinated-share-fig1…fig6_20261014.png`), opened as renders.
- The ADR, `c:\Users\defazio\bugarach\bugarach-worktrees\coordination-share-explainer\docs\adr\0014-a-figure-page-is-figures-then-controls-then-text.md`, to judge the layout rule.

I did not open the generator (`explain_coordination_share.py`), `numbers.json`, or the tool, as instructed. I did not check any numbers; that belongs to other roles.
