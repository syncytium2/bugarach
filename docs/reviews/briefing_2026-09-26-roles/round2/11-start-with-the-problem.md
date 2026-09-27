GRANT 11 ok — Read, Grep, Glob

Role 11 (Start With the Problem), blind review. I did not open anything under docs/reviews/briefing_2026-09-26-roles/.
Artifact: <darkroom>/bugarach/2026-09-26-full-panel/briefing/index.html (the built page, 646 lines). I read the header and Figure 1a in full. For everything after that I read the headings, captions, prose and boxes but not the SVG path data.

**Arc used.** Tony's own frame, not the default analysis arc: the leaderboard from the top down, with new bench against old → examples → easy access to the zoomable rasters with detection. The page follows that three-part order and names it in its nav bar, so the top-level order is not a defect. The findings below are about order inside the sections, and about points where a claim arrives before the reader has what they need to judge it.

## Spine (one claim per unit, in page order)
0. Title and byline: these are the 2026-09-25 night's results under ADR-0010, scored on fresh simulation seeds, and nothing here is adopted.
1. Nav: the page runs Leaderboard → Examples → Rasters → Terms.
2. §1 verdict box: on the new bench many more rows beat CoactDetect's shipped setting than on the old bench (fast 13 vs 4, slow 16 vs 0, combined 12 vs 1), and CoactDetect's own F1 falls. The new-bench numbers favour the proposals and picks, because they were chosen on that bench.
3. Figures 1a–1c: for each stream, every row's paired ΔF1 against CoactDetect shipped, new and old bench side by side, with budget failures in orange.
4. Table 1 ("At a glance"): the same verdict as a table, per stream and bench, including the top unflagged row.
5. "How to read it" box: defines a row, paired ΔF1 and its interval, and "unflagged". Says the order is a reading of intervals, not a ranking. Says the old bench was retired by ADR-0010 and decides nothing. Covers decoys and F1, which budgets are checked, seed counts, and says the ORX-spacing check was run but is not shown.
6. "What is compared" box: what each detector and learned model is.
7. Tables 2–4 (collapsed): every number behind Figure 1.
8. §2 viewer-setup box: how to open any recording link in the viewer.
9. §2 leader-rule paragraph: each stream's leader is the highest row in Figure 1 that ran on the real recordings, is within every budget and off every search limit. It is compared with CoactDetect *proposal*, not the shipped setting the leaderboard uses.
10. Each stream (fast, slow, combined): the rows passed over and why (fast only), the lanes shown, a count table of agreements and disagreements by group, then examples in the order both call it → leader only → reference only (Figures 2–9).
11. §3: links to the review pages (Table 5) and to every recording, one link per stream (Table 6). Setup is by back-reference to §2's box.
12. Terms.

## Findings
(location · issue · severity · fix · verified against source)

1. **§1, units 2–5, the verdict box and Figure 1 come before the reading key.** The verdict box and Figures 1a–1c use terms defined only in "How to read it" (unit 5): "unflagged", "over a budget", "rows", paired ΔF1, "the order is not a ranking", and "the old bench decides nothing". That box sits below all three figures and Table 1, roughly 2,500 px of SVG further down. So the headline and the new-versus-old comparison reach the reader before the terms that make them checkable. The most important of these is that the old bench is retired and decides nothing: it governs how the requested comparison should be read, and it arrives last. · **Major** · Put the key bullets (row, paired ΔF1 and interval, unflagged/budget, both benches score the same rows, old bench decides nothing) directly under the §1 heading or inside the verdict box. Leave the provenance bullets (seed counts, run times, ORX check) where they are. · yes (page order read)

2. **§1, units 2–4, Table 1 comes after the figures although it says the same thing as the verdict box.** Table 1 ("At a glance") is the at-a-glance version of the box's prose claim, but it sits below three tall figures. The reader gets the verdict as a run-on paragraph of numbers first and the table form only after scrolling past all the detail. · **Moderate** · Put Table 1 directly after the verdict box, or replace the box's number list with Table 1 plus one sentence. Then Figures 1a–1c follow as the evidence behind it. · yes

3. **The handoff from §1 to §2 changes the ranking and the reference, and §1 does not warn about either.** In §1, Table 1 names LoCo · shipped as the top unflagged fast row on the new bench. In §2 the reader learns that this row "did not run on the real recordings", so the examples use a different leader. The reference also changes, from CoactDetect shipped (the leaderboard's zero line) to CoactDetect proposal, which is itself on a search limit. Both facts arrive only in §2's rule paragraph and the muted "passed over" line. A reader who took the §1 leaderboard at face value cannot check the §2 examples against it without backtracking. · **Moderate** · Mark in Figure 1 and Tables 2–4 which rows ran on the real recordings. Add one sentence at the end of §1: the examples below compare each stream's highest eligible row with CoactDetect proposal, the setting the night's detection used. · yes (Table 1 row, the §2 paragraph and the passed-over line all read)

4. **§2, unit 8, the viewer-setup box sits in the wrong section.** The box opens §2, whose content is static PNG examples. The section that exists for the viewer, §3 ("easy access to the zoomable rasters"), has only a back-link to that box. The setup interrupts the examples and is missing where Tony's third request is served. · **Minor** · Move the box to the top of §3. Give a one-line pointer from the example captions, which also link to the viewer. · yes

5. **§1, unit 6, the "What is compared" glossary comes after the figures that use its names, and it splits the page's definitions in two.** Figure 1 labels its rows by detector and model name. Their definitions follow the figures, and a second glossary ("Terms") closes the page. Tony knows most of these names, so this costs little for him. · **Minor** · Fold the box into Terms at the end, or collapse it into a details element under the §1 heading. · yes

6. **The residual risk is scattered and has no position of its own.** The caveats a reader needs before acting are spread across the byline, the end of the verdict box and bullets inside "How to read it": nothing is adopted, picks are favoured on the new bench, intervals ignore the choice among training runs and are uncorrected, and the ORX check is not shown. None of them closes an argument. The frame ("nothing here is adopted") makes this acceptable for a briefing, but there is no stated place a reader can go to learn "what could make this wrong". · **Minor** · Add a short "What this does not settle" box at the end of §1, collecting these caveats. · yes

7. **The cold open is not a problem statement.** The reader first sees a title, a byline about ADR-0010 and seeds, the nav bar, then the verdict box. The frame is Tony's own ("leaderboard first"), and the first substantive content is the new-versus-old verdict, so this is his arc and not a defect. The finding is only that it is a prose paragraph rather than the at-a-glance table; see finding 2. · **Note** · As finding 2. · yes

**Order that passes:** the three top-level sections (leaderboard → examples → rasters) match the requested order. Within each stream, the count table comes before the example figures, so the claim precedes the evidence. The examples run both call it → leader only → reference only, which is defensible. The collapsed Tables 2–4 act as an appendix inside §1, and that is appropriate.

**Outside my role (for the main thread):** the verdict box counts "13 of 22 rows" while Figure 1a's header reads "23 rows", which is probably the reference row being included. The fast passed-over line says LoCo · shipped "did not run on the real recordings", while the slow leader is LoCo · shipped; that is plausibly per stream. Agents 4 and 10 own these; I did not check either.
