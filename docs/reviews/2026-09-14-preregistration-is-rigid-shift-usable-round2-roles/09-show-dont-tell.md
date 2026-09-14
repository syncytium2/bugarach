GRANT 9 MISMATCH — missing Grep, Glob; holds no forbidden tools (held: Read, Bash)

That is a finding about the run, not about the page. I did the search work with `grep` inside Bash, so nothing in this review was skipped.

**Artifact:** `docs/proposals/2026-09-14-preregistration-is-rigid-shift-usable.md`. Blob 2c9813d is confirmed, last touched in 4f20d3b. It has 355 lines and about 3,070 words.

I opened no file under `docs/reviews/`. I read three source files to check whether the figures I propose would expose real questions: `src/bugarach/surrogates.py`, `src/bugarach/surrogate_discriminator.py` and `tools/build_surrogate_screen.py`.

## Thresholds used

- **Slide rules, as written:** more than 40 words on a page; any single text block over 60 words; a methods or results section with no figure; two or more prose-only sections in a row; a figure under 50% of the canvas.
- **Tuned for a pre-registration:** the text of a pre-registration is the contract, so its word count is not a defect in itself. A figure goes beside the rule and never replaces it. I only flag a section when its content has a shape: a sequence, a set of branches, a timeline or a grid. Those are the sections where prose hides the structure.
- **Figure share:** the source has no image, `<img>` or embed tags and no "Figure" references anywhere. The rendered figure share is therefore 0% on every section by construction, so I had no bounding boxes to measure. The repo rule to number every figure is only met because there are no figures.

## Count table (each heading is one page)

| section | words | largest block | figure | share | table |
|---|---|---|---|---|---|
| title / preamble | 141 | 70 (why this page exists) | n | 0% | – |
| The question | 84 | 42 | n | 0% | – |
| Why rigid shift, and why only rigid shift | 126 | **93** | n | 0% | – |
| What this run cannot claim | 65 | **65** | n | 0% | – |
| Data | 80 | 29 | n | 0% | – |
| The displacements — accepted | 80 | 52 (table) | n | 0% | y |
| The gates | 16 | 16 | n | 0% | – |
| Leak (signed) | 165 | 55 | n | 0% | – |
| Count preservation (signed) | 91 | 32 | n | 0% | – |
| Destruction (signed) | 257 | **66** | n | 0% | – |
| The outcome, per stream and overall (signed) | 178 | 55 (table) | n | 0% | y |
| Not in this run | 37 | 23 | n | 0% | – |
| What has to be built, and its cost | 106 | 46 | n | 0% | – |
| Review, once | 25 | 25 | n | 0% | – |
| Sign-off | 62 | 47 (one table cell) | n | 0% | y |
| Amendments | 146 | **96** | n | 0% | – |
| Adopted amendments — 2026-09-14 | 141 | **94** | n | 0% | – |
| The outcome, completed | 279 | 58 (table) | n | 0% | y |
| The leak gate | 203 | 48 | n | 0% | – |
| The count gate | 128 | 37 | n | 0% | – |
| The destruction gate | 271 | 36 | n | 0% | – |
| Randomness | 49 | 49 | n | 0% | – |
| What was known before signing | 93 | 33 | n | 0% | – |
| What a PASS may claim | 84 | 30 | n | 0% | – |
| What STOPPED means | 106 | 50 | n | 0% | – |
| Groups | 54 | 31 | n | 0% | – |

**What the slide rules flag:**
- **More than 40 words:** 23 of the 26 sections.
- **Blocks over 60 words:** five. They are "why this page exists" (70), the "why rigid shift" paragraph (93), the "cannot claim" caveat (65), the "review ran" paragraph (96) and the adoption paragraph (94). The destruction Instrument paragraph (66) is a sixth.
- **Methods sections with no figure:** all six gate sections, the signed ones and the amended ones.
- **Longest prose-only runs:**
  - The signed leak, count and destruction sections: three in a row, 513 words.
  - The amended leak gate through Groups: eight in a row, 988 words. This is where the rule the run will actually use lives.

## Which figures must exist before the run

A figure belongs before the run if it defines or decides something. Two do:
- the outcome decision flow;
- the window layout, drawn to scale.

Everything else reports a result and belongs in the write-up. Neither of the two pre-run figures can go above the sign-off line. Each has to arrive as a dated note that says so explicitly: **"illustrative; where it and the text disagree, the text wins"**. If it is instead adopted by Tony as the rule, that must also be written down. A drawing of the rule is a second copy of the rule.

Drawing either figure raises rule questions (listed in the findings below). Those go to Tony as amendments. They must not be settled quietly by how the picture is drawn.

## Findings

Each finding gives: **location · issue · severity · suggested fix · verified against a source**.

1. **"The outcome, completed", together with "What STOPPED means" and "Groups".**
   - **Issue:** The outcome rule has three levels (cell → stream → overall) and is spread over five places:
     - the per-cell results;
     - the per-stream rule;
     - the overall table, whose last row is "any other combination";
     - the STOPPED scope ("intrinsic" failure only);
     - the group override (any group's leak point estimate at or above 0.55 makes the outcome NARROWED).
     
     No single place shows the whole path from a result to an outcome. Prose also hides the shape of the rule. Of the 16 possible pairs of fast and slow results, only 4 are named. The other **12 end in UNRESOLVED**, including PASS paired with UNDECIDED and PASS paired with VOID. So one stream passing cleanly while the other is undecided yields "nothing is read about the candidate". Seen as a grid, a reader questions that at once; buried in "any other combination", nobody does.
     
     The drawing also forces two questions the text leaves open:
     - In what order do the group override and the Cossart column apply?
     - Does the STOPPED scope rule ("no cell passes both leak and destruction") replace or narrow the FAIL/FAIL row? That rule leaves out the count gate, which the FAIL/FAIL row includes.
   - **Severity:** major. The rule decides the result, and this is the repo's own rule to show the picture.
   - **Fix:** In a dated note, add **Figure 1, the outcome decision**:
     - **Left panel:** a flow from cell to stream. Each cell is PASS, FAIL (decided), UNDECIDED or VOID, and each stream combines its three *J* cells.
     - **Centre panel:** a **4×4 matrix of fast × slow results**. All 16 squares are filled and coloured by outcome, with the Cossart split drawn inside the PASS/PASS square.
     - **Right panel:** the order in which the later rules apply: the group override, then the STOPPED scope, then the rerun branch (a VOID stream may be rerun; an UNDECIDED stream is not).
     
     Put the two open questions to Tony before building.
   - **Verified:** yes, against the page text. The count of 12 comes from the rules on the page.

2. **"The leak gate" and "The count gate": which windows count.**
   - **Issue:** "Interior window" is defined in one sentence ("neither the first nor the last window of its recording"). Four kinds of edge are then described in prose in four different places:
     - where rigid shift drops onsets, at the edges of the generation window;
     - the 60 s analysis windows;
     - the discriminator's edge-band features;
     - `edge_thinning`'s fixed 5 s zone at *every* analysis-window edge.
     
     A timeline drawn to scale raises two things the sentence hides:
     - **The trailing tile can be short.** `surrogates._tiles` makes "the last, shorter one its own window". If that tile is shorter than *J* (up to 5.6 s on slow), rigid shift's drop zone reaches back into the second-to-last window, which the definition counts as interior. The interior-only rule then no longer "removes the generation-edge loss" as the amendment claims.
     - **"Its recording" may not be one generation window.** The definition says "its recording", but losses happen at generation-window edges. If a recording contributes more than one baseline segment, the two are not the same thing.
     
     The runner's "pair count from the window layout" is a table the reader cannot picture without this figure.
   - **Severity:** major. It decides which data gate two of the three tests.
   - **Fix:** In a dated note, add **Figure 2, the window layout**. One baseline recording on a minutes axis (`1m`, `2m`, …) at the largest slow *J*, showing:
     - the generation window, and 60 s tiles including the short trailing tile;
     - the first and last windows hatched as edge windows, interior windows shaded;
     - rigid shift's ±*J* drop zones at the generation edges;
     - edge bands, and the 5 s thinning zones at every tile edge.
     
     Beside it, a small table of pair counts: interior and edge windows per stream, including recordings with zero interior windows.
   - **Verified:**
     - The short trailing tile and the per-tile thinning: yes, from `src/bugarach/surrogates.py` (`_tiles`, `_edge_dither`).
     - Whether the discriminator uses the same tiling, and whether recordings have more than one baseline segment: no.

3. **"The leak gate": the bounds.**
   - **Issue:** PASS, decided FAIL, UNDECIDED, a valid positive control and the can-pass check are five conditions on percentiles against one number, 0.55. They are spread over the signed leak section and two amended sections. This is a number line told as prose.
   - **Severity:** minor. It could be folded into the outcome decision figure.
   - **Fix:** Add a panel to Figure 1, or a small figure of its own: an accuracy axis with a line at 0.55 and three example intervals (1.67th to 98.33rd percentile) labelled PASS, UNDECIDED and FAIL. Draw the positive control's interval (must sit wholly above the line) and the can-pass interval (must end below it) beside them.
   - **Verified:** yes, against the page text.

4. **The signed sections that the amendments override: Leak, Count preservation, Destruction and "The outcome, per stream and overall", plus "Joint-ISI was never measured" in "Why rigid shift".**
   - **Issue:** A reader meets the superseded rule first, including an outcome table with no VOID, UNDECIDED or UNRESOLVED rows. The only way to reconcile the two versions is the sentence "where an amendment and the text above disagree, the amendment wins". That tells the reader there is a mapping instead of showing it. Above the line nothing can be marked, because it is frozen.
   - **Severity:** major for a pre-registration, because it invites reading the result against the wrong table.
   - **Fix:** In a dated note directly under "Adopted amendments", add a **concordance table** with columns *signed section · overridden by · what changed, in one line*:
     - Leak → The leak gate
     - Count preservation → The count gate
     - Destruction → The destruction gate
     - Outcome → The outcome, completed + What STOPPED means + Groups
     - Why rigid shift (the Joint-ISI sentence) → What STOPPED means
     
     This is a table, not a figure, and a table is the right form here.
   - **Verified:** yes, against the page text.

5. **"Amendments": the paragraph beginning "the review ran; eleven amendments are proposed and none is adopted yet" (96 words).**
   - **Issue:** It is a status paragraph that the next section supersedes, yet it ends "**Do not run until Tony has ruled on each**". It is also the longest block on the page. Its home is the run record, which it already links to.
   - **Severity:** minor. The fix is a pointer; nothing is deleted.
   - **Fix:** You cannot edit it in place. Let the concordance note from the previous finding open with one line: "that status is superseded by the adoption below". Everything else stays where it is.
   - **Verified:** yes.

6. **"Why rigid shift, and why only rigid shift" (93-word paragraph).**
   - **Issue:** It is a table told as prose, a comparison of candidates: rigid shift, the one-frame survivors, uniform dither and joint-ISI. One of its cells ("Joint-ISI was never measured") is corrected four sections later.
   - **Severity:** minor. It is frozen and was used in the exploratory run.
   - **Fix:** For the result write-up, not this page: a **candidate table** with columns *candidate · largest displacement with no leak detected · removes seconds-scale coordination? · why it is out*. The joint-ISI row should carry the corrected fact ("measured where tractable, leaked at every cell it reached").
   - **Verified:** yes, against the page text.

7. **"The destruction gate": gated K and saturation.**
   - **Issue:** "Visible", "not saturated" and "P(largest bin ≥ K) ≥ 0.95" define which K values count. The saturation table is committed before any score exists, so it is a pre-run artifact. A table of probabilities across K × *J* × bin width cannot be read at a glance.
   - **Severity:** minor.
   - **Fix:** The runner's first step commits the saturation table *and* a **heatmap**: P(largest bin ≥ K) with K on x and *J* on y, one panel per stream and bin width (fast 1.0 s; slow 1.0 s and 2.0 s), and a contour at 0.95 marking which K values are gated. Number it at that point.
   - **Verified:** no. This is a proposal for an artifact that does not exist yet.

8. **Result write-up (gates, groups, outcome).**
   - **Issue:** Nothing on the page commits to the figures the result will be read from. The risk is that the result comes out as prose too, which the repo rule forbids.
   - **Severity:** minor for this page; major at write-up time.
   - **Fix:** Add a dated note naming the result figures ahead of time, numbered and each with its name:
     - **Leak forest plot:** for each stream and *J*, the point with its 1.67–98.33 percentile interval, a line at 0.55, and the uniform-dither and can-pass intervals beside each.
     - **Count equivalence plot:** each cell's interval against a ±2% band, with interior and edge windows separate and the `edge_thinning` control beside.
     - **Destruction:** retained share against K, in panels for participation (0.2, 0.5) × bin width, with a line at 0.25, gated K shaded and the three controls overlaid.
     - **Groups:** a dot plot per group for leak accuracy, count difference and zero-event share beside the pooled value.
     - **Filled outcome grid:** the stream × *J* cells from Figure 1, coloured by result.
   - **Verified:** no. This is a proposal.

9. **Prose that is right where it is.**
   - **Sections that stay prose:**
     - "What this run cannot claim" (65 words), "What was known before signing" and "What a PASS may claim" are caveats and statements of scope. They must stay on the face of the page, and there is no picture of them.
     - "Randomness" is a list of keys.
     - "Not in this run", "What has to be built" and "Review, once" are short and have no structure to draw.
   - **Tables already right:** the displacement table and the sign-off table (its 47-word cell is a record of consent and belongs where it is).
   - **Severity:** none.
   - **Fix:** none. Keep them.
   - **Verified:** yes.

10. **Preamble, "why this page exists" (70 words).**
   - **Issue:** This is history of how the goal came to a stop, not the rule. It is frozen.
   - **Severity:** minor.
   - **Fix:** None here. For future pre-registrations, put the history in the goal file and leave one link in the preamble.
   - **Verified:** yes.

**Boundary notes:**
- **Whether the rule is correct:** the questions that Figures 1 and 2 would force, the order of the later outcome rules and the trailing-tile definition, are rigor questions. I found them by drawing the structure and report them so they reach Tony. Whether each is a defect in the rule belongs to the rigor and statistics reviewers.
- **Mechanical checks:** confirming the rendered Markdown and that the tables with blank cells display correctly is the mechanical reviewer's job. I did not render the page.
