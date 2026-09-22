# Role 9 — Show, Don't Tell (round 1, verbatim as returned)

GRANT 9 ok — Read, Grep, Glob, Bash

# Role 9: Density and figure-first. Methods section, round 1

I reviewed the source (docs\methods\coordination_pipeline_methods.md) and all six rendered pages (…\scratchpad\methods_build_r0\coordination_pipeline_methods_page01..06.png). Each page was one unit. No files were modified.

## Thresholds used
These are project conventions, adapted for the genre. They are not researched optima.
- **Slide threshold (40 words per slide) not applied.** It has no meaning on a manuscript methods page, and every page here carries 300 to 525 words by design.
- **Text block over 60 words** is logged. It becomes a finding only if the block is a list of parameters or a spatial or temporal layout that a table or schematic would carry better. Long prose that explains reasoning is not flagged.
- **Missing figure** is not flagged just because a page has none. Methods text is prose by genre, and the PI asked for it "as brief as possible". I flag content only where a figure or table would replace more words than it costs, or would make a relation visible that prose makes the reader rebuild in their head.
- **Figure share of canvas** is not applicable: the document has no figures. I recommend a budget of one main-text figure and one supplementary figure.

## Count table (one row per rendered page)
The renders overlap by a few lines (for example, page 2 repeats the quiet/busy bullets from page 1). I counted overlapping lines once, so the counts are approximate. Whether the overlap is a render defect is agent 10's question.

| page | prose words | largest block (words, where) | table | figure | figure share |
|---|---|---|---|---|---|
| 1 | ~416 | 96 (opening "Analyses start from…") | group table | n | 0% |
| 2 | ~525 | 72 (close-events test bullet); also Coordinated events 71, Background 70 | none | n | 0% |
| 3 | ~345 | 62 (Scoring, call matching); locust bullet 59 | Table 2 | n | 0% |
| 4 | ~309 | 66 (Learned detectors, Input) | Table 1 | n | 0% |
| 5 | ~468 | 66 (Separability) | none | n | 0% |
| 6 | ~446 | 62 (Analysis of recorded data, opening) | none | n | 0% |

Blocks over 60 words: lines 8, 16, 47, 61, 80, 100, 108, 196, 250 and 258 of the source.

All six pages are prose-only. That run is acceptable for the genre, with one exception: pages 1–2 (see finding 1).

## Findings

Each row gives location, issue, severity, suggested fix, and whether I could verify it against a source.

**1. Synthetic recordings (source lines 42–92, pages 1–2, ~450 words). Severity: major.**
- **Issue:** The benchmark recording is a layout in time, but it is described only in prose spread over seven paragraphs and bullets:
  - 15 planted events at three participation levels, interleaved, at 120 s plus gamma intervals;
  - six distractors placed uniformly between 120 s and 1,100 s;
  - an elevated-rate block from 1,200 s to 1,500 s with a 30 s ramp;
  - no planted event within 120 s of that block;
  - a total length of 2,700 s.
- The reader has to assemble a timeline from numbers scattered over two pages, and nothing on the page shows that the distractor, block and exclusion intervals fit together.
- **Fix:**
  - **Figure 1: an annotated timeline.** A 0–2,700 s time axis with:
    - a lane of down-pointing marks for the planted events, coloured by participation level (30% / 18% / 10%);
    - a distractor lane, with the 120–1,100 s span hatched;
    - the elevated-rate block, with its ramp drawn as a hatch or ramp shape;
    - the 120 s exclusion margins.
  - Put a real synthetic raster of 33 cells below the timeline, in black and white, with nothing drawn on it. That follows the house raster rule, and `bugarach.ui.diagnostic` with `lane_panel` above `raster_panel` already draws this.
  - The prose can then shrink to one sentence per element that points at the figure.
- **Verifiable:** yes, the layout values are in the source text. I did not check them against the generator.

**2. Generator parameters (lines 47–59 and 80–89). Severity: minor-major.**
- **Issue:** About 12 numeric parameters are embedded in running prose and bullets:
  - gamma shape 0.275;
  - modulation shapes 1.547 and 1.388 on 300 s and 60 s bins;
  - quiet and busy rates;
  - jitter SD 0.36 s;
  - participation;
  - width median and IQR;
  - 33 cells.
- Each is "measured on the recorded data with 200 bootstrap resamples", and only participation falls outside its interval.
- **Fix:** Add a **table of generator parameters**, one row per parameter, with columns parameter · value · measured value (95% interval). The participation row then shows its own discrepancy (0.18 used against 0.190 measured, 0.182–0.232) without the two-bullet explanation.
- **Relocate, don't delete:** "measured before floor-pinned windows were removed … agreed to four decimal places" (lines 91–92) is provenance. Move it to a table footnote or the supplement.
- **Verifiable:** yes, against the source text.

**3. Test recordings (lines 94–104, page 2, largest bullet 72 words). Severity: minor.**
- **Issue:** Three test types are defined in prose, and their limits sit separately in Table 2 on page 3. The reader has to join them across a page break.
- **Fix:** Either add a column to Table 2 (test · construction · what a call there means · limit per detector), or add a three-row test table directly above Table 2.
- **Relocate:** the crowding justification ("7 of 39 recordings whose crowding exceeded 0.38 … 6–26 s") is rationale. It can go to a table footnote.
- **Verifiable:** yes.

**4. Coded detector descriptions and Table 1 (lines 137–176, pages 3–4). Severity: major.**
- **Issue 1:** Table 1's caption and line 139 say "Table 1 summarises each detector", but the table holds only settings. The description of each detector is six prose bullets (54–59 words at the longest). Four of the six detectors share one structure: count distinct active cells, compare with a circular-shift or circular-roll null, threshold at a percentile or p-value. The bullets hide that family resemblance.
- **Fix 1:** Restructure Table 1 with columns detector · statistic · null · threshold rule · settings, for example:
  - rate+context: population rate over 1 s · none (60 s moving average) · excess over 4.5 events s⁻¹;
  - CoactDetect: distinct cells in 2 s · circular shift within 120 s, exact mean and variance · Gaussian p ≤ 10⁻⁵;
  - and so on for the other four.
- Keep in prose only what does not fit a table cell: the CICADA attribution and disclaimer, SPIKE-synch's adaptive window, and verification to 10⁻⁹.
- **Issue 2:** The settings cells pair names and values by position. A cell reads "bin · context · null percentile · merge gap · null context · minimum cells · mode" and the next cell reads "1 s · 120 s · 99.9 · 8 s · symmetric · 3 · sliding". To match a value to its name the reader counts to the fifth item. That is a list that failed to become a table. (I checked: every row pairs up 1:1.)
- **Fix 2:** Write "name = value" inside the cell, or use long form with one row per parameter. The first is shorter on the page.
- **Verifiable:** yes, I checked the pairing counts in the source.

**5. Table 2, last row (line 132, page 3). Severity: minor.**
- **Issue:** The close-events row is 0.02 in all six columns. Its four-line wrapped label ("close-events test, largest F1 loss vs. the setting it replaces") makes it the tallest row in the table while it carries no per-detector information.
- **Fix:** Drop the row. Say it once in the caption ("…and a close-events F1 loss of at most 0.02 for every detector").
- **Ordering note (boundary with roles 10 and 11):** Table 2 appears on page 3, before Table 1 on page 4.
- **Verifiable:** yes.

**6. Group table (page 1) and "Recordings analysed" bullets (page 6, lines 274–278). Severity: minor.**
- **Issue:** The same group breakdown appears twice, five pages apart: animals and recordings per group on page 1, then TTX and senktide counts per group as inline parentheticals on page 6. The reader cannot see that 38 + 29 = 67 of the 84 recordings, or how many per group were not analysed (for example, MALE 14 of 22).
- **Fix:** Merge into one table on page 1: group · animals · recordings · first treatment TTX · first treatment senktide. Page 6 then needs one sentence.
- **Verifiable:** yes. Group sums checked: DI 17, MALE 14 of 22, ORX 19 of 25, OVX 17 of 20.

**7. Nested cross-validation (lines 221–254, page 5, ~350 words). Severity: minor. Figure goes in the supplement, not the main text.**
- **Issue:** The nested structure has to be rebuilt from prose. It has these parts:
  - 48 seeds × 2 backgrounds;
  - 4 outer folds of 12 seeds;
  - tuning on 3 folds (72 recordings);
  - inner cross-validation over those 3 folds, with 24 configurations × 3 training seeds;
  - refits with 5 seeds, each trained on 10 recordings;
  - two selection rules;
  - replication on a second draw.
- The "20 refits" quoted on page 6 (line 261) is derivable only by the reader: 4 folds × 5 seeds, from one draw.
- **Fix:** Add a **supplementary schematic**. Draw the outer folds as a 4-column block with the held-out fold shaded. Show inner cross-validation as a nested 3-block inside it, and branch it into coded (coordinate search, grids not extended) and learned (24 configurations → 5-seed refit). Mark the replication as "×2 draws". A diagram makes the 72, 10 and 20 counts checkable at a glance.
- **Keep in prose:** the Nadeau–Bengio correction.
- **Verifiable:** partly. The counts are internally consistent in the text, but whether the 20 refits come from one draw could not be checked without the run.

**8. Call width and amplitude measurement (lines 287–305, page 6). Severity: nit.**
- **Prose is right here.** The three numbered steps are short and exact. A schematic adds little per unit of space.
- **Optional:** a small panel could go in the Figure 1 supplement. It would show one call with its ±1 s window, the events split into groups at gaps over 0.5 s, the chosen group, and its width.
- **Where a figure would pay:** the dense-senktide chaining caveat (for example, the 26.3 s call with 53 cells). But that is a result or caveat, not method.
- **Verifiable:** n/a.

**9. Scoring, learned architectures, training and decoding (pages 3 and 5). No finding.**
- **Prose is right.** Call matching is one rule, the F1 formulas are already set out as a list, and the architectures are standard, small and described in one line each.
- An architecture diagram for chorus_norm would be supplementary at most, and is not warranted under the brevity mandate.
- **Verifiable:** n/a.

**10. Draft-status annotations (lines 19–20, 88–89, 135, 281, 302–305). Severity: minor for brevity; rigor content must be kept.**
- **Issue:** The ⚠ notes are review and project status, not method. They are:
  - "slow stream awaits a benchmark";
  - "move to 0.19 is scheduled";
  - "not yet been approved";
  - "an earlier rule required 15 min";
  - "a revision … is under review".
- They make up about 110 words of the manuscript face.
- **Fix: relocate, do not delete.** Move them to a cover memo or reviewer-notes companion that goes with the draft to the PI, where every word survives. Remove them from the manuscript text only once each is resolved. The chaining caveat about the width measure is a real limitation. It belongs in the Discussion or the supplement in the final version, not deleted.
- **Verifiable:** yes.

## Summary
The document is dense, and correctly so for a methods section. Most of it should stay prose.

Three things would carry content better than prose, and each saves more words than it costs:
1. A **timeline figure of the synthetic benchmark** (finding 1). This is the only main-text figure I recommend.
2. A **restructured Table 1** that holds the detectors' statistic, null and threshold, with settings written as name = value (finding 4).
3. **Merged tables:** the group table with the analysed-recordings counts, and the test definitions with Table 2's limits (findings 3 and 6). Plus a generator-parameter table (finding 2).

The nested cross-validation schematic belongs in the supplement.

---
*Transcription note: personal absolute paths were replaced with placeholders (sapper SAP004); nothing else was altered.*
