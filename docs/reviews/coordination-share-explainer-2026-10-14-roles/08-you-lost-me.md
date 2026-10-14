GRANT 8 ok — Read, Grep, Glob

Role 8, naive-reader accessibility ("You Lost Me"), round 1.

**Artifact reviewed:** `c:\Users\defazio\bugarach\bugarach-worktrees\coordination-share-explainer\docs\learned\coordination_share_explainer\README.md` and the five PNGs beside it. All five renders were opened. As instructed, I did not open the generator, the tool or `numbers.json`.

**Headline:** a cold reader is lost from Figure 1 onward, and this is a layout problem more than a figure problem.
- All five figures sit above the "Terms" section and above the sentence saying everything is simulated. So every caption uses words (planted, shared moment, *f*₂/*f*₃, fixed and binomial model, schedule, pass band) that the page defines only further down.
- Figure 1 is read as real data until line 32.
- The prose also carries 9 code identifiers and roughly 10 internal-process terms.
- The rendered figures themselves are mostly readable. None is a false friend of the "looks like a raster but isn't" kind.

## Per-figure / per-section verdicts

| Location | Terms and identifiers first used here | Defined here | Cold reader follows? |
|---|---|---|---|
| Title (l.1) | coordinated, "an event" | none. "Without defining an event" reads as "without defining a calcium event", which the page *does* define (onset). The objection is about a *coordinated* event. | no |
| Fig 1 caption + render | planted, shared moment, close pair, medium pair, single, onset, window, *X*; simulated (implicit, never stated) | close, medium and single (by gap); *X* | **BLOCKING**: 3+ undefined (planted, shared moment, onset), and not told the data are simulated |
| Fig 2 caption + render | *f*₂, *f*₃, factorial cumulant, rigidly shifted copy, "the excess that is kept", 20 copies, chance | "pairs/triples beyond chance" (axis gloss only) | **BLOCKING**: shifted copy, *f*₂/*f*₃, excess, "kept" |
| Fig 3 caption + render | simulated recording, fixed model, binomial model, adopted, planted vs recovered share, pass band, median error | pass band (±25%) | **BLOCKING**: fixed, binomial, adopted, planted share |
| Fig 4 caption + render | median error, mixed schedule, 120 s only, participants per moment (*k*), moments per minute (λ), *w*, "recovered ÷ planted − 1" | none on the figure (close/medium pairs come from the Fig 1 caption) | **BLOCKING**: mixed, *k*, λ, schedule, ratio-minus-one notation |
| Fig 5 caption + render | nothing planted, "share reported coordinated", *f*₃/*f*₂ pooled, "as the tool does", "the tool", answer ÷ planted share | none | **BLOCKING**: pooled, the tool, answer |
| Preamble (l.25–33) | `numbers.json`, "the producer's corrected export", treatment | none | no (the producer and the export are unexplained) |
| The objection (l.35–40) | onset, shared moment | partly | yes |
| Terms (l.42–57) | ROI, *N*, *w*, *X*, *k*, λ, factorial cumulant, `coordinated_share_of_rate` | yes, except the identifier | yes, but it arrives after every figure |
| Simulated recordings (l.59–78) | fast stream, bench, `bugarach.bench`, background rate, jitter, "Tony", seed 10, seed 3, todo | jitter (a number is given) | **BLOCKING**: fast stream, bench, Tony, seed |
| §1 (l.82–101) | mean, spread, E[·], factorial cumulant formulas | E[·] not defined | no for the non-math reader the page is written for (E[ ] undefined) |
| §2 (l.103–113) | slid/wrapping, `shifted`, "two windows apart" | slide is described in words | mostly yes. The mechanism is not drawn (see finding 7). |
| §3 (l.115–127) | ordered pairs/triples, `solve`, "the run", pooling | none | no ("ordered" and "run" undefined; identifier) |
| §4 (l.129–150) | `ADOPTED_MODEL`, "the bench's background subtraction" | none | no (the reason for adopting the fixed model is opaque) |
| §5 (l.152–170) | gap schedule, `numbers.json` | yes | yes |
| What it cannot see (l.172–206) | elevated-rate level, `CAL_NO_PROBE`, slow stream, docstring, todo, `solve` declines, `shape_usable`, background fit, "quiet and busy rates it reports" | partial | no |
| How we know (l.208–214) | `CAL_TOL`, `numbers.json` | ±25% | mostly yes |
| What waits (l.216–228) | `senktide_ttx`, export, contamination stop, motion-correction pinning census, DI, producer, murderboarded | none | **BLOCKING**: 5+ undefined |

## What a cold reader sees (one sentence per panel)

- **Fig 1, top lane:** blue double-triangles at about 35m22s and 37m55s and two orange triangles near 40m30s and 40m40s, under a three-entry legend whose third entry (green "single moment") has no mark anywhere in the figure.
- **Fig 1, raster:** a sparse black-and-white tick raster of 32 cells over 6 minutes, with clear vertical columns of ticks under each triangle.
- **Fig 1, bottom:** a bar trace of onsets per 1-s window with spikes of 6, 10 and 11 under the columns and 0 to 2 elsewhere.
- **Fig 2A:** paired green and black bars on a log axis that match at 0 to 4 onsets, with black-only bars at 5 to 11.
- **Fig 2B:** two clusters of green dots at zero and two black diamonds above them. The *f*₃ diamond (1.37) sits far higher than the *f*₂ diamond (0.21), each with an arrow from zero labelled "excess".
- **Fig 3:** filled and open dots along a diagonal, all below the identity line and inside a grey wedge, with the open dots closer to the line.
- **Fig 4A:** four coloured lines flat at about −15% to −21%, inside a grey band.
- **Fig 4B:** lines at about +30%, above the grey band, with black and blue rising to about +55% at 4 s.
- **Fig 4C:** lines at about −35%, below the band, with black and blue dropping to about −47% at 4 s.
- **Fig 5A:** three labelled rows. The middle row is a scatter between 2% and 6% ("median 3.7%"). The top and bottom rows carry only the text "no coordination reported in any of 24 recordings".
- **Fig 5B:** three dot columns for 15, 6 and 3 moments that widen as the moments fall, each with an open diamond at about 0.81 to 0.83 and a reference line at 1.0.

Every panel can be described, so none is unreadable. The places a stranger misreads are listed in the findings.

## "What does this resemble?" check

- **Fig 1, top/middle:** resembles a spike raster plus a population PSTH (peri-stimulus time histogram). In that idiom x is time and rows are cells, and that is exactly what it is here. The bottom row is a population count per bin, which matches a PSTH. **No false friend.**
- **Fig 2A:** resembles a paired histogram, and it is one. The log y-axis is not said in words; to a non-math eye 10³ against 10⁰ looks like a modest height difference.
- **Fig 2B:** resembles a strip/dot plot with a category axis, and it is one. **Partial false friend:** *f*₂ and *f*₃ share one y-axis, so the reader compares heights and sees "more triples beyond chance than pairs", which reads as impossible to someone who has not been told why.
- **Fig 3:** resembles a calibration scatter (measured against true, identity line, tolerance wedge), and it is one. **No false friend.**
- **Fig 4:** resembles a three-panel line chart over a continuous x. The x is categorical and log-spaced (1, 2, 4 s); that is harmless. **Two real misreads:**
  - Each x-axis label is "window w · <quantity>", so the reader reads the x-axis as "share of events coordinated" or "participants per moment", when that is the y quantity.
  - The ±25% pass band is drawn in B and C as well. In the idiom that grey band means pass/fail, so B and C read as failures. The text never says whether *k* and λ have a criterion.
- **Fig 5A:** resembles a categorical strip plot, and it is one. The top and bottom rows look identical ("no coordination reported"), while the text says the top row gives *no answer at all* and the bottom row gives zero.
- **Fig 5B:** resembles a strip plot against a 1.0 reference, and it is one. **No false friend.**

## Findings

Each row: location · issue · severity · suggested fix · could I verify it against a source.

1. **README l.3–21 (layout)** · All five figures are stacked before the simulation statement and the Terms section, so every caption is unreadable cold. This conflicts with the house rule in CLAUDE.md for written reports: lead with the main figure, keep the others where the text discusses them. · **blocking** · Keep Fig 1 at the top. Move Figs 2 to 5 into §1/§2, §4, §5 and "What it cannot see". Put "every figure is simulated" and a one-line definition of a shared moment into the Fig 1 caption. · yes (the README, plus the CLAUDE.md plot-conventions bullet)
2. **Fig 1 caption** · "Planted", "shared moment" and "onset" are undefined there, and the reader is not told the data are simulated. · **blocking** · Example: "Simulated recording. Shared moment: several cells with an onset within a tenth of a second; 'planted' means put in by the simulation, so the answer is known." · yes
3. **Fig 1 render, legend** · The green "single moment" entry has no mark in the 6 minutes shown, so the reader hunts for it. · minor · Drop the entry, or mark it "(none in this stretch)". · yes
4. **Captions for Figs 1, 2, 4 and 5 (colour names)** · The captions say "aqua", but the render is a green/teal. · minor · Say "green", or use the legend's own words. · yes (renders)
5. **Fig 2 caption** · "Rigidly shifted copy", "*f*₂/*f*₃" and "the excess that is kept" are undefined, and "kept" has no referent (kept by what, for what?). · **blocking** · Define the shifted copy in a clause. Write "the excess over the copies, which the measure uses". · yes
6. **Fig 2B and §1/§3** · *f*₃ > *f*₂ reads as "more triples than pairs", which looks paradoxical. "Ordered" pairs and triples (l.118) are never explained. · major · Add one sentence: a 10-cell moment holds 90 ordered pairs but 720 ordered triples, so triples always outnumber pairs. · yes
7. **§2, the shift/null model** · The key non-trivial mechanism (sliding each cell's train with wrap-around) is described only in words. Fig 2 shows its result, not the mechanism. · major · Add a small schematic: 3 to 4 cells' trains before and after sliding by different amounts, with wrap-around, showing a shared column breaking apart. · yes
8. **§1, l.97–98** · E[·] is never defined, and the page is for non-math readers. · major · "E[·] means the average over all windows". Or move the formulas to a footnote and keep the word gloss in the main text. · yes
9. **Fig 3 caption** · "Fixed model", "binomial model" and "adopted" are undefined at the figure. · **blocking** (with finding 1) · Add one clause each ("fixed: every moment has the same number of cells; binomial: the number varies"). · yes
10. **Fig 4, x-axis labels** · "window w · share of events coordinated" puts the panel's y quantity on the x-axis label. · major · The x-label should be just "window length". Name the quantity as the panel title or y-label ("A. Share of events coordinated"). · yes (render)
11. **Fig 4B/4C, grey band** · The ±25% pass band drawn on *k* and λ implies those fail. The text (l.161–163) quotes +28% and −30% without saying whether that matters. · major · Draw the band only in A, or say in the caption that the band applies to the share only. Say plainly in §5 that *k* and λ are biased by design (§4) and are not pass/fail. · yes
12. **Fig 4 y-axis "recovered ÷ planted − 1"** · This is maths notation for "error". The same quantity appears as "median error −21%" in Fig 3, as "answer ÷ planted share" (a ratio of about 0.8) in Fig 5B, and as "78% to 84%" in the text. · major · Use one form throughout: "error (%)" or "recovered as % of planted". (Cross-figure consistency is role 3's; flagged here as a reader-is-lost issue.) · yes
13. **Fig 5A, top row against the text** · The figure says "no coordination reported" for both the top and bottom rows. The text (l.190–191) says the top row gives "no answer at all, not a small one". · major · Label the top row "no answer given (measure declines) in any of 24 recordings" and the bottom row "zero reported". · yes (render against prose)
14. **Fig 5A, middle row** · "0.127 onsets per second per cell" has no reference point. · minor · Add "(about 26 times the quiet background)". · yes (l.65 gives 0.0049)
15. **Fig 5B legend** · "*f*₃/*f*₂ pooled over the 24 recordings, as the tool does (median)": pooled, the tool and the "(median)" are all opaque on the figure. · major · Example: "the answer when the 24 recordings share one estimate of moment size (median over recordings)". · yes
16. **Title, l.1** · "Without defining an event" contradicts the page, which defines calcium events (onsets). The objection is about *coordinated* events. · major · "…counted without defining a coordinated event". · yes
17. **Code identifiers in prose** · `coordinated_share_of_rate` (l.57), `bugarach.bench` (l.61), `shifted` (l.108), `solve` (l.125, 191), `ADOPTED_MODEL` (l.144), `CAL_NO_PROBE` (l.181), `shape_usable` (l.203, 219), `CAL_TOL` (l.211), `numbers.json` (l.30, 158, 213), `senktide_ttx` (l.218). · major · Replace each with the plain concept: "the setting that picks the model", "the tool's fitness check", "the pass threshold", and so on. If traceability matters, move the identifiers into one "for developers" line at the foot. · yes
18. **l.158 and l.213, "in `numbers.json`"** · Binomial-model claims are backed only by a JSON file a reader cannot be expected to open. · major · State the numbers in the text, or plot the binomial model in Fig 4 (open markers). · yes
19. **Simulated recordings section** · "Fast stream", "bench", "seed 10/3", "(Tony, 2026-10-14)", "todo": a stranger does not know what a stream or bench is, who Tony is, or what a seed is. · **blocking** · Example: "the project's standard simulation (its 'bench') of the fast imaging stream"; "simulated recording no. 10"; "the lab's PI decided…"; drop the todo reference or footnote it. · yes
20. **§4, l.144–147** · The reason for adopting the fixed model ("matches what the bench's background subtraction removes") is opaque. "Background subtraction" is used nowhere else. · major · Rewrite in plain terms, or say "for consistency with the project's simulation; it is not the more accurate of the two". · yes
21. **§4, l.133–134** · "A moment joined by one cell looks exactly like background" is a jump that a stranger cannot connect to "pairs and triples can't tell the models apart". · minor · Add a bridging sentence. · yes
22. **§3, l.126** · "Every recording in the run": "run" is undefined. · minor · "every recording analysed together". · yes
23. **"What it cannot see", l.181–189** · "elevated-rate level", "slow stream", "the todo that commissioned this page", "docstring". · major · Cut the internal process remark. Define the slow stream, or drop it. · yes
24. **l.187, "two windows per cell, about a minute for 32 cells at 1 s"** · The arithmetic (32 × 2 × 1 s ≈ 64 s) is not shown. · minor · Show it inline. · yes
25. **l.203–205** · "Background fit" and "quiet and busy rates it reports" introduce outputs the page never described. · minor · Define them, or cut to "the tool skips recordings shorter than 5 minutes, with fewer than 20 onsets or fewer than 5 cells". · yes
26. **"What waits", l.218–224** · `senktide_ttx`, "export", "contamination stop", "motion-correction pinning census", "DI" and "producer" are all undefined. · **blocking** for that section · Example: "The real-data numbers are held back until a known artefact in the source data (image registration making several cells appear to have events together) is corrected upstream." · yes
27. **l.228, "Not murderboarded as of the first draft"** · Internal process jargon in audience-facing text. · minor · "Under internal review", or remove. · yes
28. **Fig 2A** · The log y-axis is not stated in words, and the legend's "mean 0.47 onsets" has no "per window". · minor · Use "(log scale)" in the axis label and "mean 0.47 onsets per window". · yes
29. **Tone** · Sentence case is consistent and there is no ALL-CAPS. Captions for Figs 1, 4 and 5 pack semicolon-separated legend lists into prose, which is acceptable because the renders carry real legends. · no finding · — · yes

No false friend of the raster kind was found. Fig 1 is a genuine raster with matching conventions. The nearest misreads are findings 10 and 11 (Fig 4 axes and band) and finding 13 (Fig 5A rows that look the same but mean different things).
