GRANT 9 ok — Read, Grep, Glob, Bash (I also hold SubagentHandback, which is only the hand-off channel. I hold no Edit, Write or NotebookEdit.)

Role 9: Density & figure-first ("Show, Don't Tell")
Artifact: docs/proposals/2026-09-25-hebbian-coupling-detector.md, with Figure 1 at docs/proposals/2026-09-25-hebbian-coupling-detector/hebbian_kernel.png.

**Method.** I treated each `##` section as a page, plus the preamble before the first one. I counted words after removing link targets. To render, I used cmarkgfm to make HTML with a GitHub-like 880 px text column and 16 px body font. I then opened it in headless chromium at a 1280 px window (1265 px body width). I measured every element's rendered position with getBoundingClientRect, and found the figure's ink bounds by scanning the PNG pixels.

Scratch files (no repo file touched), all under <scratchpad> p.html, m.html (the measuring copy), full.png (full-page screenshot) and idea.png (the Figure 1 page).

**Thresholds, and how I applied them.** These are project conventions, not researched optima:
- more than 40 words on a page;
- any single text block over 60 words;
- a results or methods page with no figure;
- two or more consecutive prose-only pages;
- a figure given less than about 50% of its page;
- more than 20% side margin on both sides.

This is a proposal in prose, not a deck, so every page passes 40 words. I report that count but treat the **60-word block, methods-page-without-figure and consecutive-prose flags as the ones that matter.**

## Count table

| page (## section) | total words | largest block (words) | figure? | figure share of the page |
|---|---|---|---|---|
| preamble (title, status, symbols) | 283 | 42 | n | — |
| The gap | 203 | 76 | n | — |
| The idea | 323 + figure | **189 (the Figure 1 caption)** | **y** | box 880×439 px in a section 947 px tall: **46% of the text-column area, 32% of the 1265 px canvas**. PNG ink only (rows 32–978 of 1256): **~35% of the column, ~24% of the canvas** |
| Why this rule | 195 | 69 | n (points to Figure 1A and 1C) | — |
| What the detector reports | 385 | **119** (readout 3); readout 2 ~110 | **n (methods)** | — |
| What could make this worthless | 387 | **82** | **n (methods)** | — |
| What is asked | 163 | 47 | n | — |
| Stages | 595 | **89** ("Two comparison arms") | n (one table, 880×343 px) | — |
| Method detail | **727** | **111** ("The step and the clamp") | **n (methods)** | — |
| Where the code comes from | 246 | 84 | n | — |
| What this does not claim | 147 | 76 | n | — |
| References | 131 | 34 | n | — |

Whole document: 3,770 words and one figure. **Nine consecutive prose-only pages**, from "Why this rule" through "References".

## Findings

Each finding gives location · issue · severity · suggested fix · verified against a source.

**F1 · "The idea" / Figure 1, the one figure's share of its page · HIGH · verified: yes (rendered measurement and PNG pixel scan)**
- **What is wrong:**
  - Figure 1 gets 46% of its page by bounding box, and only ~35% by ink. That is under the 50% bar.
  - About 22% of the PNG's height is blank. Ink ends at row 978 of 1256, which leaves a ~97 px white band on screen between the panels and the caption.
  - It is a 2:1 strip of three panels squeezed into an 880 px column, displayed at about 0.35 of its native pixels. Tick labels and the panel C legend come out at roughly 7–8 px, too small to read (see idea.png).
  - Meanwhile the caption below it runs full width for 146 rendered words.
  - Boundary: the blank band is a geometry/build fact for agent 10. I am judging the layout.
- **Fix (a reflow, not a crop):** Markdown caps the image at the column width, so the way to give each panel more space is to split them.
  - Put 1A ("the kernel on whole frames") next to "Whole frames, ends at half weight".
  - Put 1B ("what one update is worth") next to "The span".
  - Put 1C ("the step and the clamp") next to "The step and the clamp".
  - Each panel then gets the full 880 px, about 2.9× its current linear size. Number them Figure 1, 2 and 3 with names, per the numbering rule.
  - If the three must stay one figure, stack them vertically (3 rows × 1 column) at full column width, and move panel C's four-line legend inside the axes so C is no taller than A and B.
  - Either way, cut the caption to a two-line footer (F2).

**F2 · Figure 1 caption, 189 source words · HIGH · verified: yes**
- **What is wrong:** The caption carries the argument, not just a description of the figure. Three things in it do not belong there:
  - the conclusion "an artifact weighs about seven coordinated pairs" (0.144 vs 1);
  - a ⚠ provenance caveat about σ, which is already stated in full under Method detail, "The span";
  - the verdict "At the paper's step it lands past the clamp".
- **Fix:**
  - Keep one sentence per panel saying what it shows, for example: "Figure 1. The coincidence kernel on whole-frame lags (A), the expected update for a coordinated pair against the span (B), and the step size against the bound (C). Computed from the rule's definitions; no recording is read."
  - Move the seven-to-one sentence into Method detail, "The span", next to the same number it supports. Better still, draw it in 1B: a second y-axis or a labeled ratio at *m* = 2.
  - Delete the duplicate ⚠. The copy in Method detail stays, so nothing is lost.
  - Move the clamp verdict into "The step and the clamp", which already says it.

**F3 · "The idea", paragraph 1: a process narrated in prose · MEDIUM · verified: yes (read the text)**
- **What is wrong:** "Walk through a baseline window in time order… strengthen… weaken… at the end, the couplings record…" describes a sequence over time. Figure 1 shows the kernel, not the process.
- **Fix:** a schematic.
  - Top: two ROI onset lanes, x-linked. Tick marks only; under the house raster rule nothing is drawn on a raster.
  - Below them: the coupling *W*<sub>ij</sub> as a step trace, going up at close pairs and down at near-misses. Use the minutes-friendly time axis.
  - One picture then replaces the paragraph, and the paragraph becomes a one-line caption.

**F4 · "The idea" paragraph 2, "Why this rule" bullets 2–3, and Method detail "Rate neutrality is in the mean": a quantitative claim argued three times in prose · MEDIUM · verified: yes**
- **What is wrong:** Three places assert, in words, that a plain Hebbian rule drifts with the event rates while the zero-sum kernel does not, and that the spread of *D* still grows.
- **Fix:** one figure, computable from definitions just like Figure 1:
  - x = product of the two event counts;
  - y = mean *D* for independent pairs, plain rule against zero-sum kernel;
  - a second panel showing the SD of *D*, and *Z* flat after standardization.
  - This also previews the simulation stage's rate-neutrality test (slope within ±2 surrogate standard errors).
  - Keep one sentence at each of the three places, each pointing to the figure.

**F5 · "What the detector reports": methods page, no figure, 385 words, blocks of 119 and ~110 · HIGH · verified: yes**
- **Fix:** a pipeline schematic.
  - onsets → *W* → *D* → *Z* (per-pair surrogate standardization) → three branches, each labeled with its own null:
    - λ₁ against the ±20 s jitter null ("power check");
    - λ₂… plus overlapping groups against the curveball null on fixed coordinated events (⚠ new work);
    - *E*(*t*) against a surrogate threshold.
  - Readout 3's split-half cross-fit becomes a two-row timeline: half A learns, half B is scored, then they swap.
- **Relocate:** the method comparison (weighted SBM against link communities, signed against positive weights) goes to Method detail or an appendix. Leave only "grouping method not chosen ⚠" on the page.

**F6 · "What could make this worthless": methods page, no figure, 387 words, block of 82 · HIGH · verified: yes**
- **Fix, two pictures:**
  1. A stop-rule flowchart. Busy-core check per stream: pass, or stop the stream; stop both and the proposal ends. Then the just-STTC rank arm and recovery arm: either one says yes → run the shape readout on STTC directly.
  2. An illustrative spectrum of eigenvalues 2–4 for the two planted controls the page already names: one core plus noise, and two groups. Overlay the surrogate 95th-percentile band. That shows directly why "remaining share after the first eigenvector" is blind to a pure core. It needs no data.
- **Relocate:** the "why this statistic" and "tile choice" bullets go to Method detail once the picture carries them.

**F7 · "Stages": 595 words; a table plus five dense bullets; the largest block, 89 words, is "Two comparison arms" · MEDIUM · verified: yes**
- **What is wrong:** The page names three kernel shapes in prose:
  - cosine with half-weight ends;
  - flat covariance window minus the rate expectation;
  - same-frame-excluded, with the negative lobe rescaled.
- **Fix:**
  - Draw the three kernels overlaid against lag, as an extension of Figure 1A. A reader then sees at once what "no negative lobe" and "same-frame excluded" mean.
  - Turn the simulation bullets (rate neutrality, recovery, the call, the arms, freezing) into a table: test · compared against · pass criterion · seeds.
  - The stage table itself is fine. A stage-gate flow is optional.

**F8 · "Method detail": 727 words, the biggest page, no figure, block of 111 · MEDIUM · verified: yes**
- **What is wrong:** "Gated before the kernel" (clamor's kernel wraps lags modulo the period, so a pair 2*m* apart scores +1) is a visual fact told in prose.
- **Fix:**
  - Plot Co(*k*) over lags −2*m* to 2*m*, clamor's wrapped kernel against the gated one.
  - "The span" and "The step and the clamp" already have pictures (Figure 1B, 1C). Once F1 splits the figure, each panel sits beside its paragraph, and each paragraph can shrink to the conclusion.
- **Relocate:** the provenance paragraph ("The source", clamor at `c25c7e5`, what was not reachable) to an appendix or the review record. It is rigor, so keep it; it is not the argument.

**F9 · "Where the code comes from" (246 words) and the preamble symbol list (283 words) · LOW · verified: yes**
- Prose is right for both: a vendoring plan and a set of definitions are not pictures.
- **Relocate:** move "Where the code comes from" to an appendix after "What this does not claim". It is implementation, and it separates the argument from its limits.
- The symbol list could become a two-column table (symbol · meaning), but it works as it is.

**F10 · "The gap" (block 76), "What is asked", "What this does not claim", "References" · LOW / no change · verified: yes**
- Prose is right for all four: a request list, disclaimers, citations. Nothing here is a hidden picture.
- The one exception: "The gap" could take a small two-route diagram (the discriminator route waits on Tony's surrogate choice; this route needs a null and the simulator). That is optional.

**F11 · Whole document: nine consecutive prose-only pages · HIGH · verified: yes**
- **What is wrong:** The one figure sits on page 3, and everything after it is prose. A reader who skims the headings meets no evidence after page 3.
- **Fix:** F3–F8 would put a picture on "The idea" (the process), "Why this rule" (rate neutrality), "What the detector reports", "What could make this worthless", "Stages" and "Method detail". With F1's split, that is about six to eight numbered figures.
- Every relocation above moves caveats and provenance; none deletes them.

**Not my finding, but seen while measuring (for agent 10):** the blank band at the bottom of hebbian_kernel.png (rows 979–1256, 22% of its height) is a build-geometry fact. The side margin of the rendered page (~192 px per side, 15%) comes from the renderer's column and is under the 20% flag, so it is not a finding.
