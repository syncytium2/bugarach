GRANT 9 MISMATCH — missing none; holds Edit, Write, PowerShell, Agent, Artifact, Skill, ToolSearch (NotebookEdit loadable through it), Claude Docs MCP batch/update, which are forbidden or outside the grant (granted Read, Grep, Glob, Bash are all present)

**Note on the run:** I used none of the extra tools. My only writes were a word-count script and its output in my own scratch folder, `work-r2-9/`. The record's `roles:` line should say this role ran on a fallback path with extra tools, not as the named agent.

# Role 9: Density and figure-first ("Show, Don't Tell"), chapter-1-aim0.md, blind verify round 2

Artifact checked: `docs/dissertation/chapter-1-aim0.md`. Its git hash-object matches the context (cdc8fbf6…). I read the whole file and opened all 11 figures with Read. I measured each PNG's size and ink margins with PyMuPDF and counted words per section with a script. I did not open anything under `docs/reviews/chapter-1-aim0_2026-10-29*`.

## Thresholds adapted for a dissertation chapter (conventions, not optima)

The slide thresholds do not carry over directly. A chapter page is not a slide, and markdown draws every figure at the width of the text column. I used:

- **Page = one numbered (sub)section.**
- **Words:** a double-spaced page holds about 250–300 words, so the 40-words-per-slide limit is not usable here. Instead I flag:
  - any results or methods section over about 350 words with no figure;
  - any results section with more than about 400 words per figure.
- **Largest single block:** body paragraph or bullet over **150** words; caption over **120** words.
- **Results or methods section with no figure:** flagged, unchanged from the slide rule.
- **Two or more prose-only sections in a row:** flagged for results and methods. Discussion and conclusion are exempt, with the reason given.
- **Figure share,** measured two ways:
  - **(a) Share of the page:** the figure drawn at a 6.5 in column, against a 6.5 × 9 in text block, with body text double-spaced and captions single-spaced.
  - **(b) Share of the figure frame:** how much of the rendered frame is plot area rather than legend, annotation box or blank space. I flag anything under about 50%. Plot-area shares were estimated from pixel positions in the rendered PNG.
- **Native widths** are 9.6–13.8 in, so each figure shrinks to about 50–68% of its native size in a 6.5 in column. Text size inside the figures is agent 10's check; I note it only as context.

## Count table (one row per page)

| page | total words | largest block | figure? | share of page (a) | plot area in frame (b) |
|---|---|---|---|---|---|
| 1.1 The problem | 212 | 99 | n | – | – |
| 1.1 What brute force found | 321 (caption 111) | 111 (caption) | y (Fig 1.1) | 29% | ~85% |
| 1.1 The question, and the answer | 136 | 93 | n | – | – |
| 1.1 Contributions | 250 | ~35 (list items) | n | – | – |
| 1.2.1 Data and generative model | 283 + Table 1.1 | **154** (L104) | n | – | – |
| 1.2.2 The tools | 471 (caption 205) | **205 caption** (L135) | y (1.2) | 38% | ~85% |
| 1.2.3 Prior work | 458 | **151** (L173) | n | – | – |
| 1.3 Methods | 284 | 131 | **n** | – | – |
| 1.4.1 Window sharing | 341 (caption 133) | **133 caption** | y (1.3) | 25% | ~75% |
| 1.4.2 Expected excess counts | 172 | 79 | n (equations) | – | – |
| 1.4.3 Window vs jitter | 103 | 68 | n (points to 1.3B) | – | – |
| 1.4.4 The test | 282 (caption 69) | 113 | y (1.4) | 29% | ~85% |
| 1.4.5 Hard-core vs general form | 339 | 138 | **n** | – | – |
| 1.4.6 Joint fit, correlogram | 415 + Table 1.2 | 119 | **n** | – | – |
| 1.5 Assessor threshold | 471 (caption 136) | **157** (L423); caption 136 | y (1.5) | 21% | **~42%** |
| 1.6.1 Membership | 404 (caption 102) | 102 | y (1.6) | 18% | ~85% |
| 1.6.2 Order | **1013** + Tables 1.3 and Kreuz | 155 caption (Fig 1.8); 138 (L575) | y (1.7, 1.8) | 15% | 1.7 ~65%, 1.8 ~75% |
| 1.7 Separation | 523 (captions 227) | 145 caption (Fig 1.9) | y (1.9, 1.10) | 42% | 1.9 **~48%**, 1.10 ~70% |
| 1.8 What theory replaces | 386 (caption 129) | 129 caption | y (1.11) | 25% | **~43%** |
| 1.9.1 Old vs new | 100 + table | 100 | n (table) | – | – |
| 1.9.2 Two sources | 119 | 119 | n | – | – |
| 1.9.3–1.9.5, 1.10, About | 127–209 each | ≤127 | n | – | – |

The body runs about 9,100 words with 11 figures, about 830 words per figure.

- Under the slide rule, every figure-bearing page is under 50% of the canvas. That is normal for a chapter with figures drawn inline at column width, so I do not flag page share in itself.
- What I do flag:
  - results pages with no figure at all;
  - figures whose own frame gives less than half its area to the plot.

## Findings

Columns: location · issue · severity · suggested fix (replacement figure) · verified against a source (yes/no)

1. **1.4.5 and 1.4.6, "The joint fit…" (754 words in two results sections in a row, with no figure).**
   - **Issue:** Contribution 3, the chapter's one new estimator, has no figure of its own. It appears only as the violet line in Fig 1.1 D/H. Its headline limitation is carried entirely by prose:
     - "1.06 × planted [0.39, 1.53] … 8 of 40 at the bound … only 10 of 40 within 0.8–1.25" (L392);
     - Table 1.2.
   - **Severity:** **major.**
   - **Fix:** add a figure with three parts:
     - **A:** recovered ÷ planted jitter against planted σ on a log axis. Correlogram tool and joint fit side by side, both backgrounds, interquartile range (IQR) bars, and "off the curve" or "at the bound" counts as annotations. This replaces Table 1.2; move the table to an appendix.
     - **B:** per-recording strip or violin plots at realistic values: fast and slow types, 7 and 13 cells, the general form against the hard-core form. Shade the 0.8–1.25 band so "10 of 40 within" can be seen.
     - **C:** for 1.4.5, a dot plot of predicted against measured rate and participants for each window on realistic interval trains, hard-core against general form. This shows "1.16 and 0.90 predicted vs 0.99 and 0.97 measured" at a glance.
   - **Verified:** yes (word counts and figure inventory measured on the artifact).

2. **1.4.4, "The prediction is close but not exact…" (L315, 113 words), with Fig 1.4.**
   - **Issue:** the section's key quantitative claim cannot be seen in its figure. The claims are:
     - about a 1% overprediction;
     - 17 of 48 setting-windows beyond 2 SE on the held-out record;
     - a sign test of 24 of 32.

     Fig 1.4 plots measured against predicted on 0–2.5 axes, where a 1% bias is invisible. It also shows the first experiment only, so the held-out record, called "the honest one" in 1.3, is never shown. The headline "The full prediction matches" also leans further than the text does.
   - **Severity:** **major.**
   - **Fix:** add a residual panel to Fig 1.4, or a new figure: the signed residual (measured − predicted) ÷ planted for each setting-window, ordered by σ/w.
     - Plot first experiment and held-out record in two colors.
     - Draw ±2 SE whiskers and a zero line.
     - Annotate the beyond-2SE counts and the sign test.
     - Retitle the caption to the actual claim, for example "close, with a 1% excess on held-out data".
   - **Verified:** yes (figure viewed against the text).

3. **Fig 1.5 (1.5): the legend takes about 40% of the frame's width; the plot area is about 42% of the frame.**
   - **Issue:** once shrunk to the column (about 65%), the plot is roughly 3.3 in wide, while the six-entry legend repeats the caption.
   - **Severity:** major.
   - **Fix:** a reflow, not a crop.
     - Label the three lines directly at their right ends ("0.05 Hz", "0.01 Hz", "0.0096 Hz").
     - Put the measured-point and shading keys in a one-line footer.
     - Give the axes the full width.
     - The "first K under one per hour" values move to text, or to markers on the dashed line.
   - **Verified:** yes (pixel extents of the rendered PNG).

4. **Fig 1.11 (1.8): the legend column takes about 40% of the width, about 43% plot area.**
   - **Issue:** the legend includes a six-line paragraph that duplicates the caption.
   - **Severity:** major.
   - **Fix:**
     - Move the definition of "resolved" to the caption only.
     - Keep the two-symbol key as a one-line footer and widen the axes.
     - Also put the direct-simulation result at the two realistic boxes on the figure: the fraction of 40 recordings within 0.8–1.25 (10/40, 9/40 fast; 17/40, 19/40 slow). The figure then shows the conclusion of 1.8 instead of only pointing to 1.4.6.
   - **Verified:** yes.

5. **1.3 Methods (284 words, no figure) and 1.2.3 Prior work: two prose-only pages in a row.**
   - **Issue:** the methods page has no picture of the testbed design:
     - 4 × 3 × 2 × 2 grid × 5 recordings;
     - 200 background-only recordings;
     - blind measurement → estimator → residual;
     - a held-out rerun with fresh seeds.
   - **Severity:** minor.
   - **Fix:** a one-row design schematic showing:
     - the planted grid going into the simulator;
     - blind measurement by the three tools;
     - the same estimator applied to the prediction, giving the residual;
     - the held-out branch.

     Prior work can stay prose (it is a literature review). Optionally, move the 1.9.1 table forward as a positioning matrix: method × jitter law × event train × parameters estimated × multi-window.
   - **Verified:** yes.

6. **1.1 "The problem" / 1.2.1 "The generative model" (L17, L104 at 154 words).**
   - **Issue:** the five properties of a source are introduced only in prose and Table 1.1:
     - participation;
     - jitter;
     - intervals, including the hard-core 20 s gap;
     - membership rule;
     - latency template.

     Fig 1.2 shows the data, but not the hard-core spacing, the membership rule or the template.
   - **Severity:** minor.
   - **Fix:** a generative-model schematic: event times on a line with the ≥20 s hard-core gap, k of N cells drawn per event, Gaussian jitter about each event time, and Poisson background. Add a variant inset each for fixed assemblies and a latency template. This could be a new panel A of Fig 1.2.
   - **Verified:** yes.

7. **1.6.2: Table 1.3 duplicates Fig 1.8 number for number, and the L558 paragraph restates the Fig 1.8 caption.**
   - **Issue:**
     - "At one event no test has power…" and "13 cells … three events when r ≥ 2.5, and two need five or more" each appear three times: caption, table and prose.
     - The section is 1,013 words, the densest in the chapter.
   - **Severity:** minor.
   - **Fix:**
     - Keep Fig 1.8 and move Table 1.3 to an appendix.
     - Cut the restatement in L558.
     - Relocate, don't delete: move the provenance sentence about the earlier 10- and 25-event record to the appendix next to the table.
   - **Verified:** yes.

8. **1.6.2, L575 (138 words, Copeland optimality, Coppersmith et al., Shah & Wainwright, kreuz_sort search), and the "No order" bullet (L513, 130 words; Kendall, Durbin, Skillings–Mack).**
   - **Issue:** prior-art provenance sits inside a results section and is repeated in the 1.9.1 table.
   - **Severity:** minor.
   - **Fix:** prose is the right form for this, but it belongs in 1.2.3 or 1.9.1. Leave a single sentence pointing there.
   - **Verified:** yes.

9. **1.5, L423 (157 words of predicted and measured rates at each K).**
   - **Issue:** every number here is already plotted in Fig 1.5 (lines against points). Separately, "the smallest safe threshold, 5 and 8" appears three times: legend, caption and L426–429.
   - **Severity:** minor.
   - **Fix:**
     - Move the number list to a three-row table in an appendix, or drop it to the caption footer.
     - Keep one statement of the 5 and 8 result.
     - The cost side ("a safe threshold also loses spread-out events": 0.76–0.80 at 0.5 s, 0.29–0.33 at 1 s) is a result with no picture. Make it a Fig 1.5 panel B: share of planted events reported against K for each jitter.
   - **Verified:** yes.

10. **Captions over 120 words:**
    - Fig 1.2 (205)
    - Fig 1.8 (155)
    - Fig 1.9 (145)
    - Fig 1.5 (136)
    - Fig 1.3 (133)
    - Fig 1.11 (129)

    - **Issue:** several captions carry the section's argument, not just what the figure shows. Figs 1.5 and 1.8 state their conclusions, which the text then repeats. Figs 1.8 and 1.11 also carry in-figure note boxes that repeat the caption.
    - **Severity:** minor.
    - **Fix:**
      - Cut each caption to what is shown and why it matters, and remove the in-figure paragraphs.
      - Keep the Fig 1.2 sentence "This minute was picked … exactly as simulated". It is a selection disclosure; relocate it to the end of the caption, don't cut it.
    - **Verified:** yes.

11. **Fig 1.9 (1.7): bottom half split about 45/55 between panel D and the legend; plot area about 48%.**
    - **Severity:** minor.
    - **Fix:**
      - Move the legend into a full-width two-row strip under A–C.
      - Widen D to the full width, or half width beside a compact key.
      - Mark the "0.5–2.5 s merge gap", the section's punchline, as a shaded band on A–C.
    - **Verified:** yes.

12. **Fig 1.10 (1.7): panels E–H nearly duplicate A–D (realized against planned separation).**
    - **Severity:** minor.
    - **Fix:** move E–H to an appendix and give A–D the space. Or overlay the realized-separation points on A–D as open markers, as already done.
    - **Verified:** yes.

13. **1.9.2 "Two sources" (prose-only), and 1.9.1–About (six prose-only pages in a row).**
    - **Issue:** none for the run. Prose is right for discussion, limitations, next steps and conclusion.
    - **Severity:** none.
    - **Fix:** optional. The forward claim ("two sources with the same jitter look like one blended source to pair and triple counts") would be stronger as a small worked panel: f₃/f₂ for a two-source mixture against the matching single source. That is Chapter 2's opening, so it is not required here.
    - **Verified:** yes.

14. **1.4.2–1.4.3 (derivations, no figure).**
    - **Issue:** none. Prose and equations are right here, and 1.4.3 points to Fig 1.3B for the consequence.
    - **Severity:** none.

## Boundary notes (not findings for this role)

These belong to agent 10:

- Native figure widths of 9.6–13.8 in shrink to about 50–68% in a 6.5 in column. The smallest legend and annotation text, for example in Figs 1.1, 1.4 and 1.7, may fall below a readable size.
- The Fig 1.3 caption says the points cover "5, 10 and 20 cells per event", but the note inside the figure says "10- and 20-cell events".
- Figs 1.9 and 1.10 use "fast-stream/slow-stream", while the text uses "fast/slow type".

## What would get my sign-off

I would sign off once findings 1–4 are done:

- a dedicated joint-fit figure with a realistic-values panel;
- a residual view that shows the 1% bias and the held-out record;
- Figs 1.5 and 1.11 reflowed so the plot gets the frame instead of the legend.

The rest are minor relocations. No caveat needs to be deleted; each moves to an appendix or to 1.9.1.
