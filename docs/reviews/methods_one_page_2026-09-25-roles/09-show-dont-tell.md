GRANT 9 ok — Read, Grep, Glob, Bash

## Role 9 (Density & figure-first) — methods_one_page.pdf

**What I checked.** I checked the built PDF, not only the HTML. PyMuPDF (loaded from the scratchpad) gives 2 pages, both US Letter 612×792 pt. Page 1 has no images and no figure, and uses 9.6 pt body text; the 8.0 and 8.4 pt spans are sub/superscripts and the draft note. Page 2 holds the references only. I rendered page 1 to `<scratch>/mb/r9_p1.png` and looked at it. Word counts come from the HTML paragraphs with tags stripped. Nothing in the repo was edited.

**Page fill (measured).** Text on page 1 runs from y = 44.1 to 737.8 pt. The bottom margin (0.6 in) puts the limit at 748.8 pt, so there are about 11 pt spare, which is less than one line at 9.6 pt × 1.26 leading (about 12.1 pt). **Page 1 is full.** Anything added to it, a figure or a table, has to replace text of the same height.

### Count table (unit = titled paragraph; the deliverable is one page, not slides)

| Block | Words | Figure | Figure share of page |
|---|---|---|---|
| Draft note | 18 | n | — |
| Input | 143 | n | — |
| Participation floor | 90 | n | — |
| Parameters for simulation | 170 | n | — |
| Simulated recordings | 120 | n | — |
| Scoring | 84 | n | — |
| CoactDetect | 184 | n | — |
| **Chorus (largest block)** | **205** | n | — |
| Output | 113 | n | — |
| **Page 1 total** | **1,127** | **n** | **0%** |

**Thresholds.** I did not apply the slide thresholds (40 words per slide, 60 per block, results/methods slide needs a figure, 50% figure share). They describe a slide that is seen at a glance. This is a journal-style methods page that is read, and the PI fixed its form as prose on one page. Flagged against them, every block would fail, which says nothing useful. For a manuscript I used these instead, all tunable conventions rather than researched optima:
- a paragraph over about 200 words is a candidate to split;
- numbers repeated in parallel across a category (here the three streams, fast/slow/combined) are a candidate for a table;
- a mechanism described step by step is a candidate for a schematic.

The figure-share rule does not apply because the page has no figure.

### Judgment: is prose right here?

**Yes, for this page.** The PI asked for "a one page methods section with references" and not for a figure. The page has no slack, so a pipeline schematic would push it past one page. That makes a schematic a **recommendation for a companion figure, not a defect of this page.** The house rule "Show the picture — don't describe it" covers *visual findings* such as rasters, traces and sweeps. A methods description is not one, and this page reports no results; the draft note says scores are withheld. The figure-numbering rule has nothing to apply to because there is no figure.

### Findings

1. **Location:** whole page, as a companion item. **Issue:** the procedure is a flow: onset tables → three streams → floor → CoactDetect / Chorus → calls → per-call measurement, with a separate simulation → scoring → adoption loop. A reader has to rebuild that graph from 8 paragraphs. **Severity:** minor (it is not a defect of this page). **Suggested fix:** a separate **"Figure 1. Detection and evaluation pipeline"** schematic on its own page or in the companion doc: the data path across the top, the simulation/scoring/adoption loop below it, each box labelled with the paragraph heading it expands, and "Figure 1" cited once from Input. Do **not** put it on page 1. **Verified:** yes (page is full: 11 pt of slack, measured).

2. **Location:** Parameters for simulation, Simulated recordings, Scoring, Output. **Issue:** about 30 per-stream numbers are written inline as "(fast X, slow Y, combined Z)" triples across 9 quantities: timing SD, quiet and busy rates, median gap, events per hour, events per 45 min, empty-recording call budget, aperture, and split gap. Participation is given for fast only. A reader comparing streams has to hunt through four paragraphs, which is the prose-for-a-table pattern. **Severity:** minor. **Suggested fix:** a **"Table 1. Per-stream parameters"** with rows = quantity (with units) and columns = fast / slow / combined, in the DI/OVX/MALE/ORX-free stream order already used. The prose keeps the definitions and drops the numbers. Caveat on fit: I estimate a 9-row table at about 10–11 lines against about 6–7 lines of prose removed, so it does **not** fit at 9.6 pt without a further trade. At the 11 pt house minimum it fits even less. Offer it as an option to the PI or as part of the companion material, not as a required change. If adopted, it must be numbered and cited by number and name. **Verified:** partly: the triple count is from the text; the line estimate is my arithmetic, not a render.

3. **Location:** Chorus (205 words) and CoactDetect (184 words). **Issue:** these are the two largest blocks, and each packs two topics: the method, then how it was tuned or selected. In CoactDetect, the final ~95 words (from "Its settings were optimized…" to the end) are the adoption rule, and that rule also governs Chorus's comparison. **Severity:** minor. **Suggested fix:** the prose is right here; this is not a figure candidate. If space ever allows, move the adoption rules (coordinate search, bootstrap-interval gate, bracketing, "reported as a finding, not adopted") and the final "Every detector was compared…" sentence into one short "Selection and comparison" paragraph. Relocate them; do not cut them. They are the rigor content. On the one-page constraint this costs a heading line, so it is optional. **Verified:** yes (word counts measured).

4. **Location:** Output, the per-call measurement (aperture, split at gap, largest-ROI group = core, width, amplitude = ROIs/width). **Issue:** a geometric procedure described in one 113-word paragraph. It is the one passage on the page where a small diagram would clearly beat prose: an onset raster around one call, with the aperture, the split point, the core group, and the width bracket marked in a lane above it (house rule: nothing drawn on the raster). **Severity:** minor (companion only, for the same page-fit reason as finding 1). **Suggested fix:** make it a panel of the companion Figure 1, or a separate figure, built with the existing `bugarach.ui.diagnostic` raster and lane panels. **Verified:** no (not rendered; I reviewed the design only).

**No blocking or major findings.** Given the form the PI asked for and a page with less than one line spare, the page's choice of prose is correct. Every figure or table recommendation above is companion material or optional, not a defect.

Files: `<repo>/docs/methods/one_page/methods_one_page.pdf`, `<repo>/docs/methods/one_page/methods_one_page.html`; render at `<scratch>/mb/r9_p1.png`.
