GRANT 11 ok — Read, Grep, Glob

Role 11 (Start With the Problem), blind pass. I read only the built artifact at `<darkroom>/bugarach/2026-09-26-full-panel/briefing/index.html` (all 693 lines) and opened nothing under `docs/reviews/briefing_2026-09-26-roles/`.

**The arc I judged against:** the order Tony set: (1) a top-down performance leaderboard, new bench against old; (2) examples; (3) easy access to the zoomable rasters with detections. Inside each part I used a claim → evidence → caveat order, with procedure placed where it is first needed. The page follows Tony's order at the top level (nav, then sections 1, 2, 3, then Terms). Every finding below is about order inside a section.

## Spine (one claim per unit, in page order)

0. **Byline:** last night every coded detector was searched and every learned model trained on the new bench, then scored on held-out simulation seeds. Nothing here is adopted.
1. **Section 1 heading:** every row is measured against CoactDetect at its shipped setting.
   - **1a, the summary box:** on the new bench most rows beat CoactDetect-shipped (fast 12 of 21, slow 16 of 18, combined 12 of 20), against few on the old bench. Measured against CoactDetect's own new-bench proposal, almost none do (0, 1 and 1). The reference fell mainly because each planted event now comes with twice the decoys. The top unflagged row is level with many others. The old bench decides nothing.
   - **1b, Table 1:** those counts, per stream and bench, plus the top unflagged row and how many rows are level with it.
   - **1c, Table 2:** what changes under the reference (CoactDetect-shipped) between benches: decoy calls, merged calls, recall.
   - **1d, details "What each row is":** what each detector and model is.
   - **1e, Figures 1a–1c:** each row's ΔF1 on the new bench next to the old, ranked by new-bench ΔF1. This is the leaderboard itself.
   - **1f, details "How to read it":** how the interval, sort, decoys and budgets work, and where the numbers come from. It also carries a result: whether the order holds on the ORX-spaced bench (ρ 0.91 / 0.76 / 0.94; 6 of 59 intervals move).
   - **1g, details Tables 3–5:** every number behind Figure 1.
2. **Section 2, examples on real recordings:**
   - **2a, viewer-setup box:** how to open the viewer and load the folder and detections.
   - **2b, "Read this first" box:** the examples use CoactDetect-proposal, not the leaderboard's zero line. The leaderboard's top rows mostly did not run on real recordings, so the examples cannot test them.
   - **2c:** the rule for choosing the leader and runner-up, and how agreement and participants are counted.
   - **2d, fast:** the leader calls far more than CoactDetect (32 calls only its own, against 1).
   - **2e, slow:** the same (213 against 5).
   - **2f, combined:** the reverse: the leader misses what CoactDetect calls (3 against 71).
   - **Within each stream the order is:** search-limit note, passed-over lists, "cannot separate" note, lane legend, table, then the one-sentence claim, then three figures.
3. **Section 3, rasters:** 24 review pages (one per group × first treatment × stream), with 8 fast-stream thumbnails, plus a collapsed table of every recording and its viewer links.
4. **Terms.**

**The cold open:** the reader first meets the title, a history-style byline and a dense prose box of counts. The leaderboard Tony asked to see first (Figure 1a) comes fifth in section 1, after the box, two tables and a details block. On a wide screen that is well below the first screen.

## Findings (location · issue · severity · fix · verified)

1. **Section 1: box, Table 1, Table 2, details, then Figure 1a.**
   - **Issue:** Tony asked for the leaderboard first, but section 1 opens with a summary box and Table 1. Table 1 counts rows in a leaderboard the reader has not seen yet: "12 of 21 wholly above zero", "top unflagged row … 7 rows level". It is a digest of Figure 1 placed ahead of Figure 1, so its claims cannot be checked where they stand.
   - **Severity:** High. It inverts the ordering instruction Tony gave in his own words.
   - **Fix:** Put Figures 1a–1c directly after a trimmed box of two or three sentences. Move Table 1 below the figures, as their tally, or into a details block.
   - **Verified:** yes (lines 61–66).
2. **Section 1: Table 1 comes before Table 2.**
   - **Issue:** Every ΔF1 on the page is measured against CoactDetect-shipped, and Table 2 shows that this reference itself moved between benches (decoy calls 214 → 439 on fast). The new-vs-old comparison Tony asked for can only be judged once the reader knows the zero line moved. Table 2 is the prerequisite, yet it comes after the counts that depend on it. The box has the same problem: it leads with "12 of 21 beat it", and only afterwards says the reference fell and that 0 of 20 beat CoactDetect's proposal. Good-looking news arrives first and is retracted two clauses later.
   - **Severity:** Medium-high.
   - **Fix:** Order the box as: (a) the reference fell, and why (decoys); (b) so most rows now clear it; (c) against CoactDetect's own proposal almost none do. Put Table 2's content, or a one-line version of it, ahead of the leaderboard figures.
   - **Verified:** yes (lines 62–64).
3. **Figures 1a–1c: the top-down order puts flagged rows first.**
   - **Issue:** Rows are sorted by new-bench ΔF1. In Figure 1a the first four rows are all orange (over a budget on the new bench). The first row that could actually be adopted is fifth, and it is itself marked † as sitting on a search limit. A reader reading "top down" meets rows that cannot win before rows that can. The only explanation is in the collapsed "How to read it" details ("Rows are sorted by ΔF1 on the new bench") and the figure legend.
   - **Severity:** Medium.
   - **Fix:** Either group unflagged rows first, with flagged rows below a divider, or state the sort in one line directly above Figure 1a ("sorted by ΔF1; the leader is the first unflagged row, marked X"). The deviation from what a reader expects of a leaderboard would then be stated rather than silent.
   - **Verified:** yes (lines 79–113, 582).
4. **Details "How to read it" (after Figures 1a–1c).**
   - **Issue:** Two problems. First, the reading rules the figures need (the interval is per seed and uncorrected, the sort key, the budget definitions) come after all three figures. Second, the block hides a result: whether the leaderboard order holds on the ORX-spaced bench (ADR-0010 ruling 1). That result is evidence about how robust the ranking is, the residual-risk step, and it is filed under reading instructions in a collapsed block where a reader judging the leaderboard will not look.
   - **Severity:** Medium.
   - **Fix:** Move the interval and sort notes into or above Figure 1a's caption. Lift the ORX-spaced result into a visible one-to-two-line paragraph after Figure 1c ("the order mostly holds: ρ …; 6 of 59 intervals move").
   - **Verified:** yes (line 582).
5. **The caveat that bridges the leaderboard and the examples.**
   - **Issue:** The fact that most of the leaderboard's top rows never ran on the real recordings, so the examples cannot illustrate them, first appears at the start of section 2. Tony reads the leaderboard expecting the examples to show its winners. He learns otherwise only after the leaderboard is behind him, and the example leaders turn out to be rows far down the ranking.
   - **Severity:** Medium.
   - **Fix:** Add one sentence to the section 1 box (or at the end of section 1) saying which top rows ran on real recordings. Keep the section 2 box as the reminder.
   - **Verified:** yes (lines 590, 594, 605).
6. **Section 2 opening: the viewer-setup box comes before the "Read this first" box.**
   - **Issue:** A box titled "Read this first" is the second box in its section, after procedural viewer instructions. The setup also serves section 3, which only links back to it, so the procedure sits away from the part (the rasters) that Tony named "easy access". A reader who jumps from the nav to section 3 has to scroll back up into section 2 to learn how to use the links.
   - **Severity:** Medium-low.
   - **Fix:** Put the "Read this first" box first in section 2. Move the viewer setup either to the top of section 3 (with section 2's figure links pointing forward to it) or into a compact box just under the nav, so both sections can reach it.
   - **Verified:** yes (lines 589–590, 624).
7. **Each stream subsection in section 2 (fast, slow, combined).**
   - **Issue:** The subsection's claim ("the leader calls many events CoactDetect does not: 32 against 1", or for combined "the leader misses … 3 against 71") comes after four or five muted bookkeeping notes (search-limit status, the passed-over lists, the "cannot separate" note, the lane legend) and after the count table. Evidence and bookkeeping lead; the claim follows. The combined stream's result runs the opposite way to fast and slow, and it is the most important of the three sentences, yet it is the easiest to miss.
   - **Severity:** Medium.
   - **Fix:** Start each subsection with its claim sentence, then the table, then Figures 2–10. Collapse the passed-over lists and the "cannot separate" note into a per-stream details block below the figures. Keep the lane legend immediately above the figures.
   - **Verified:** yes (lines 592–622).
8. **Setting labels in Figure 1's row names.**
   - **Issue:** The labels "shipped", "proposal", "pick, run N of 5" and "starting point" are needed to parse every row of Figure 1. They are defined only in Terms at the end of the page. The box does link to Terms, and Table 1's caption defines "unflagged" and "level", so the deviation is partly stated. The "What each row is" block, which sits just before the figures, defines the detectors but not their settings.
   - **Severity:** Low.
   - **Fix:** Add one line on the four setting kinds to the "What each row is" details.
   - **Verified:** yes (lines 65, 655–663).

## Checked and clean

- The top-level order matches Tony's frame: nav, then leaderboard, examples, rasters.
- The old bench is explicitly demoted ("decides nothing") before the reader relies on it.
- The detector glossary precedes the figures that use its names.
- The leader-selection rule precedes its application in each stream.
- Section 3 is self-contained apart from the viewer-setup back-reference (finding 6).
- Terms at the end is a stated and linked deviation.

No recording ids are quoted in this report, and paths are given as `<darkroom>`.
