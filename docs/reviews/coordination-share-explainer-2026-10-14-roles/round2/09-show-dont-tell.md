GRANT 9 ok — Read, Grep, Glob, Bash

# Role 9: Density and figure-first review

**Artifact:** `c:\Users\defazio\bugarach\bugarach-worktrees\coordination-share-explainer\docs\learned\coordination_share_explainer\README.md` (3,269 words) and its six PNG figures.

**Thresholds I used.** These are conventions, not researched optima:
- Any single text block over 60 words is flagged.
- The 40-words-per-slide rule does not fit a scrolling page, so I applied it per figure caption, not per section.
- A figure under about 50% of its canvas is flagged, as is more than 20% empty margin on both sides.
- Two or more prose-only sections in a row would normally be flagged. ADR-0014 points 1–4 require explainers to put all text after the figures, so every text section here is prose-only by rule. I do not flag the layout itself. I judge whether each text block is doing work a figure should do. Because of that layout, a reader of "What else it counts" is about five screens below Figure 5, so every number the text has to recite is a scroll back up.

## Table 1: per caption and per section

| Unit | Words | Largest block | Figure? | Figure share of its canvas |
|---|---|---|---|---|
| Fig 1 caption + PNG (1471×1401) | 83 | 83 | y | 95% of the image is ink, 1% margin each side |
| Fig 2 caption + PNG (1369×724) | 61 | 61 | y | 92%, 1% / 1% |
| Fig 3 caption + PNG (1352×734) | 57 | 57 | y | 92%, 1% / 1% |
| Fig 4 caption + PNG (1394×745) | 63 | 63 | y | 93%, 1% / 1% |
| Fig 5 caption + PNG (1445×728) | 69 | 69 | y | 92%, 1% / 2% |
| Fig 6 caption + PNG (1397×655) | 42 | 42 | y | 91%, 1% / 2% (but see F8: the plot area is about 40% empty) |
| The question | 166 | 97 (L31) | n | — |
| Terms | 154 | 32 | n | — |
| §1 Count onsets in windows | 180 | 75 (L73) | n (refers to Figs 1C, 2A, 2B) | — |
| §2 Chance is measured | 159 | 109 (L81) | n (refers to Figs 1D, 2B) | — |
| §3 From two numbers to three answers | 114 | 68 (L95) | n (refers to Figs 2B, 6) | — |
| The check, and the two models | 392 | 129 (L128) | n (refers to Fig 3) | — |
| Window size, and moments close together | 366 | 105 (L151) | n (refers to Fig 4) | — |
| What else it counts | 364 | 144 (L175) | n (refers to Fig 5) | — |
| How far one recording strays | 211 | 52 | n (refers to Fig 6) | — |
| The simulated recordings | 248 | 110 (L218) | n | — |
| Where the method comes from | 194 | 119 (L239) | n | — |
| What waits | 129 | 109 (L256) | n | — |
| For developers | 110 | 46 | n | — |

**How I measured the canvas.** I took the ink bounding box (pixels darker than 245) on each PNG. Every PNG is wider than a GitHub README column (about 880–1,012 px), so GitHub scales each one down to the full column width. No figure is under-sized and none has empty side margins; there is no reflow finding at page level. I did not render the page in a browser, so the column-width part is inferred from GitHub's behaviour, not observed.

## Findings

Each finding gives: location · issue · severity · fix (with the replacement figure) · whether I could verify it against a source.

**F1 · "What else it counts", first bullet (L175, 144 words, the longest block on the page) · major**
- **Issue:** The page's central mechanism is told in prose: the shifted copies slide each cell by at most about 30 s, so a long busy stretch lines up with itself and only its edges survive ("how fast the rate changes matters, not how long"). Figure 5A shows only the result, a share against stretch length, never why.
- **Fix:** Add a schematic panel to Figure 5 (a new 5A, or a Figure 5 inset) with two stacked rate traces against time:
  - the recording's whole-field rate with a sharp-edged step;
  - the summed rate over shifted copies, whose cells' steps are staggered by up to ±30 s, so its edges are smeared;
  - the difference shaded, which sits only at the two edges.
- If the "rate of change, not duration" claim is meant literally, a second small panel would show it directly: the same length with sharp edges against 30 s ramps. Today it is inferred across 5A (sharp edges) and 5B (ramps).
- **Relocate:** "0.1334 onsets per second … 27 times the quiet background, so 28 times in all" goes to the Simulated recordings section or Table 2 (F6).
- **Verify:** yes (README L175–182; Fig 5 PNG).

**F2 · "The check, and the two models" bullets (L118–126) and "Why the fixed model reads low" (L128, 129 words) · major**
- **Issue 1:** The three bullets recite medians (18% / 8%, 5% / 17%, 16% / 2%) that Figure 3 does not draw. Fig 3 shows the points but no median marker, so the reader cannot see the headline numbers in the figure.
- **Fix 1:** Add a median tick per model per panel to Figure 3, labelled with its value (for example "−18%" and "−8%" in 3A). The bullets then shrink to one sentence: "all three medians pass".
- **Issue 2:** The 129-word paragraph explains two mechanisms in prose: (a) mixed moment sizes pull the triples-to-pairs ratio towards the biggest moments; (b) a moment straddling a window edge loses pairs and triples.
- **Fix 2:** A two-part schematic (new Figure 3D, or a small figure of its own):
  - (a) bars of pairs and triples contributed by 10-, 6- and 3-cell moments, showing the triples dominated by the 10s, so *k* reads high and λ reads low;
  - (b) one 10-cell moment split 6 + 4 across a window edge: 90 ordered pairs fall to 30 + 12 = 42.
- Panel (b) turns the edge-splitting argument into arithmetic the reader can see.
- **Relocate:** "That is a reason about matching the bench, not about accuracy" is a caveat that must be kept, not cut. It stays as one sentence of text.
- **Verify:** yes (README; Fig 3 PNG; `numbers.json` holds the medians).

**F3 · §3 "From two numbers to three answers" (L95–98) · major**
- **Issue:** The heading promises three answers, but the worked example stops at *k* ≈ 8.1. λ and the share for busy recording 3 are never computed, either in the text or in Figure 2B, so the chain from *f*₂ and *f*₃ to the share is described but never shown.
- **Fix:** Extend the inline formula box in Figure 2B, or add a Figure 2C, into a three-step flow with this example's numbers:
  - *f*₃ ÷ *f*₂ + 2 → *k*;
  - *f*₂ → λ (moments per minute);
  - λ*k*/*N* ÷ event rate → share.
- **Verify:** yes (README L95–98; Fig 2 PNG shows only the *k* step).

**F4 · "How far one recording strays" bullets (L201–210) and Figure 6 · moderate**
- **Issue:** The prose quotes "middle 80% … 0.78 to 0.86" and similar ranges for every group. Figure 6 draws only the medians, so the ranges exist only in the text.
- **Fix:** Add a 10th–90th percentile whisker per column in Figure 6. The bullets then reduce to their assertions ("fewer moments, more spread"; "pooling steadies the median, not the single recording"; "a lower rate does not add spread, a busier background does"), with the figure carrying the numbers.
- **Verify:** yes.

**F5 · "Window size, and moments close together", first bullet (L151, 105 words) and the pass-band paragraph (L165, 65 words) · moderate**
- **Issue 1:** L151 reads Figure 4A aloud point by point (14% to 19%, 21% against 14%, 22% to 23%).
- **Fix 1:** Label the endpoint values on the Figure 4 lines, or simply let the figure carry them. Keep only the assertion ("the share hardly moves, except for moments closer than a window") and the one-line mechanism (a 2 s pair falls in one 4 s window about half the time).
- **Issue 2:** L165 quotes binomial-model shares (3% to 17% low) that appear in no figure.
- **Fix 2:** Either add the binomial model as open markers to Figure 4A, matching Figure 3's open/filled code, or move that sentence to a notes or appendix line.
- **Issue 3:** L144 (93 words) describes the five interval designs in prose.
- **Fix 3:** A timeline strip (F6) shows these designs.
- **Verify:** yes.

**F6 · "The simulated recordings" (L218, 110 words; L226, 106 words) and the L144 design description · moderate**
- **Issue:** The parameter sets (cells, duration, background rates, moments per recording, sizes 10/6/3, jitter 0.106 s, decoys on or off, recordings per set) are buried in two long paragraphs. The five interval designs are described three times: L144, L226 and the Figure 4 legend.
- **Fix:** Two replacements:
  - **Table 2:** one row per set (mixed, 120 s only, medium pairs, close pairs, very close pairs, one size, bench's own, nothing planted), with columns for moments, pair kind, background, recordings and decoys.
  - **A timeline schematic:** one 45-minute strip per interval set, with ▼ marks where moments are planted (colours as in Figure 4).
- Prose keeps only the provenance sentences (the bench generator, "the bench itself is not changed", the todo link).
- **Verify:** yes.

**F7 · Figure captions 1, 2, 4, 5 (83, 61, 63, 69 words) · minor**
- **Issue:** Each caption repeats an in-figure legend. Fig 1's ▼ key, Fig 3's and Fig 4's symbol keys, and Fig 5C's open/filled key are all printed on the PNGs already. Captions also carry explanation that ADR-0014 point 2 sends to the text: Fig 1, "The measure never sees this lane"; Fig 2B, "and the participants per moment that the two excesses give".
- **Fix:** Cut each caption to its figure number and name, panel letters with what each panel plots, and whatever key is not on the PNG. Move the explanatory clauses to the text section that discusses the figure (relocate, not delete). Fig 1 could drop to about 40 words.
- **Boundary:** whether this breaks the ADR is the line editor's or ADR checker's call. I flag it on density.
- **Verify:** yes (PNGs viewed).

**F8 · Figure 6, y-axis 0 to 1.25 · minor**
- **Issue:** All data sit between 0.53 and 1.24, so about 40% of the plot area (0 to 0.5) is empty ink. Figure 3, which plots the same quantity (recovered ÷ planted), uses 0.4 to 1.6, so the two figures cannot be compared by eye.
- **Fix:** Give Figure 6 Figure 3's axis (0.4 to 1.6) and add the ±25% pass band behind it. That reflows the space to the data and links the two figures.
- **Boundary:** if agent 10 reports this as an axis or geometry fault, this finding is the layout-policy side of it.
- **Verify:** yes.

## Prose is right here (checked, not flagged)

- **"The question" (L31, 97 words):** the page's thesis and its implicit definition of coordination. That is an argument, not data.
- **"Where the method comes from" (119 and 75 words):** citations and attribution. Prose is correct.
- **"What waits" (109 words):** the contamination stop and provenance. This is a caveat that must stay in full, and it has no figure form.
- **Terms and For developers:** both are under 60 words per block, and both are reference material.
- **§1 L73 (75 words):** the "90 ordered pairs, 720 ordered triples" arithmetic is short and concrete. It is fine as text.
- **§2 L81 (109 words):** this one is borderline. Figures 1B and 1D already show the effect of the shift. An optional three-cell slide-and-wrap mini-schematic beside 1D would carry "slid by its own amount, wrapping round, at least two windows apart". Low priority.

## A judgment for the main thread, not a finding

At 3,269 words, with roughly 2,900 of them after the figures, this page reads like a report as much as an explainer. ADR-0014 point 5 (lead with the main figure, keep the others where the text discusses them) would put Figure 5 beside "What else it counts" and Figure 3 beside "The check". The ADR names explainers under points 1–4, so the current layout complies. F1–F6 are the way to make figures-first work: move the numbers into the figures so the text is optional reading. If those fixes are not taken, the main thread or Tony should decide whether point 5 is the better fit.
