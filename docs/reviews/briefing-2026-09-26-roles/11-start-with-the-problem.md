> Archived verbatim except machine-local paths, shown as `<darkroom>`, `<worktree>`, `<scratchpad>` and `<repo>` (SAP004).

GRANT 11 ok — Read, Grep, Glob

Role 11 (Start With the Problem), round 1. Artifact read: `<darkroom>\bugarach\2026-09-26-full-panel\briefing\index.html`, all 487 lines, including the Figure 1 SVG axis and legend. I judged the order inside Tony's stated frame: leaderboard, then examples, then rasters. That frame is a stated deviation, so the default arc is not held against the page. No recording or slice id appears below.

## Spine (one claim per section)

0. **Byline.** These are the results of the 2026-09-25 night, scored on fresh seeds, and nothing here is adopted.
1. **"How to read it" box.** Each row is a paired ΔF1 (a row's F1 minus CoactDetect's F1 at its shipped setting) with a bootstrap interval over seeds. Both benches score the same candidates. Some rows were chosen on the new bench and others predate it. It closes with seed counts and scoring timestamps for each bench.
2. **Table 1.** On the new bench most rows beat shipped CoactDetect on every stream (fast 13 of 22, slow 16 of 18, combined 12 of 20). On the old bench few do (4, 0, 1), so the reference looks strong under the old spacing and weak under the new. The top row changes with the bench.
3. **Figure 1.** For each stream and row it shows the new and old intervals overlaid, so you can see which rows moved between benches and which are over a budget.
4. **Tables 2–4.** They give the same rows per stream, with absolute F1 values and the budget and ruling-5 flags. Several top rows are over a budget or sit on a grid limit, so they cannot be adopted. Absolute F1 is much lower on the new bench for the fast stream (about 0.61 against 0.77 for the reference).
5. **§2 Examples.** For each stream, the top row that ran on real recordings and is within budget is set against CoactDetect, with three calls each: both call it, only the leader calls it, only CoactDetect calls it. The leaders are chorus_gain_norm_part (fast), LoCo (slow) and chorus_gain_norm_part (combined).
6. **§3 Rasters.** It explains how to open the viewer (folder plus detections file), then gives the group × first-treatment pages (Table 5) and a link to every recording (Table 6).
7. **Terms.** It defines F1, ΔF1, the two benches, shipped/proposal, pick, budget, ruling 5, ROI and EDT.

Arc used: Tony's frame (leaderboard → old-vs-new comparison → examples → rasters), with summary → picture → detail inside §1. At the top level the page follows it. The defects are inside the sections.

## Findings

**1. The headline is never stated; the reader has to assemble it.**
- Location: §1, between the box and Table 1.
- Issue: Tony asked to "see the new bench vs the old bench for comparison". No sentence says what that comparison shows. From Table 1 plus the absolute-F1 columns in Tables 2–4, it is: the new bench is harder, shipped CoactDetect drops from near the top to the lower third, and on slow every row reverses sign. The reader meets method first (the box), then counts (Table 1), and the absolute-F1 part is only in the per-stream tables further down.
- Severity: **High.**
- Fix: open §1 with two or three sentences of result (the direction of the reversal on each stream, and the drop in absolute F1), placed before the box. Then move the box's selection-asymmetry caveat and seed counts below Table 1, where they qualify a result the reader has already seen.
- Verified: yes, against the artifact.

**2. Table 1 names leaders that later sections disqualify, and the eligibility rule arrives only in §2.**
- Location: Table 1, "top row" column, and the §2 intro paragraph.
- Issue: Table 1's fast/new leader is over a budget on both benches, as Table 2 later shows in red. The fast leader §2 actually uses sits ninth in Table 2. The rule that decides who leads (ran on real recordings, not over a budget, CoactDetect excluded) is first stated in §2. So the reader reaches the examples without knowing who the leaders are, which is the thing Tony's order depends on. The counts in Table 1 also include over-budget and ruling-5 rows, and that qualifier only shows up later.
- Severity: **High.**
- Fix: in §1, give Table 1 an "eligible leader" column (or a sentence) using the same rule as §2, and split each count into within-budget and flagged. Then §2's leaders are names the reader already knows.
- Verified: yes.

**3. Figure 1's encoding comes after about 2,000 px of marks.**
- Location: Figure 1 (a 2,122 px tall SVG).
- Issue: the axis ticks, axis title and legend (filled = new, open = old, red = over budget) are only at the very bottom, and the caption is below that. A reader scrolling from the top reads 23 fast rows of filled, open and red marks before learning what they mean.
- Severity: Medium. This is ordering within the figure; agents 9 and 10 may raise the layout.
- Fix: put the legend and a copy of the ΔF1 axis at the top of the figure, or at the top of each stream block, or put the key line in a sentence just above the figure.
- Verified: yes (legend at y≈2073 and axis at y≈2022 of 2,122).

**4. The viewer is used in §2 before §3 explains how to open it.**
- Location: §2, the Figure 2–10 image links and caption links to the viewer; the §3 "Opening one recording" box.
- Issue: every example figure links to the viewer. The two-step first-time setup (choose the export folder, then open the detections file) is only explained in §3. A reader who follows Tony's order and clicks an example lands in an empty viewer.
- Severity: Medium.
- Fix: add a one-line pointer to the §2 intro ("first-time viewer setup: see §3" with an anchor), or move the setup box above §2.
- Verified: yes.

**5. The §2 "passed over" note answers only part of the question Tables 2–4 just raised.**
- Location: §2, fast-stream subsection, the muted note.
- Issue: it explains skipping one higher row (which, as the leaderboard already showed, is flagged ruling 5 anyway). It says nothing about other unflagged rows that rank above the chosen fast leader in Table 2. The reader leaves the tables and can't reconcile the rank order with the example choice where they meet it. This shares a root cause with Finding 2.
- Severity: Medium.
- Fix: state the leader-selection result per stream in §1 (Finding 2). Then the §2 note only needs to say which rows were skipped and why, all of them.
- Verified: yes (rank order read from Table 2). Whether the skip is justified is agent 4's question; I only checked where it arrives.

**6. Terms come last, while the first box already depends on them.**
- Location: Terms, and first uses in the §1 box and Table 1.
- Issue: "pick", "proposal", "budget" and "ruling 5 / §5" are needed to read the box, Table 1's top-row column and the Figure 1 caption, and they are only defined at the end. Having Terms last is fine for a reference section, but nothing at first use points there.
- Severity: Low.
- Fix: link the first use of each term to `#terms`, or add a one-line pointer in the box ("terms defined at the end").
- Verified: yes.

**7. The §1 order (Table 1 → Figure 1 → Tables 2–4) is sound.**
- Location: §1.
- Issue: none. Summary → picture → detail is a defensible order and each part earns its place. I record it so the absence of a finding here is not read as unexamined.
- Severity: none.
- Fix: none.
- Verified: yes.

**8. §3's internal order is sound.**
- Location: §3.
- Issue: none. Setup comes before the links, and the group pages come before the per-recording list. Groups are in the house order (DI, OVX, MALE, ORX). The only problem is that the setup is needed earlier (Finding 4).
- Severity: none.
- Fix: none.
- Verified: yes.

Outside my scope and not pursued: the fast-stream "passed over" sentence is grammatically garbled (agent 8's area), and the artifact itself shows recording ids in captions, links and Table 6. That doesn't matter for the darkroom copy, but whoever writes the public report or a repo copy should know.
