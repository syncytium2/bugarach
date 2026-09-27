GRANT 4 ok — Read, Grep, Glob, Bash

Role 4 (Reviewer 2), BLIND pass. I did not open docs/reviews/briefing_2026-09-26-roles/ and did not read the git history of the generator or its tests. I edited nothing. My scratch files are in <scratchpad>/mb2/: r4_text.txt, which is the page's text, and r4_fig1_*.png, which are Figure 1 rendered from the shipped SVGs.

**What I checked:**
- The built page's text.
- All three Figure 1 panels.
- Four example PNGs: fast agree, fast leader-only, combined ref-only, slow ref-only.
- The generator <worktree>/tools/make_briefing.py, all 1348 lines.
- ADR-0006 and ADR-0010.
- The budget tables in src/bugarach/bench*.py, and TOL_SEC in score.py.
- Every candidates.json. I read per-background recall, decoy calls and planted counts myself, and checked that the count runs are paired with the night's runs.
- Rank agreement between the new bench and the slow-ORX-spaced bench, computed from the files.

**Findings.** Format: location · issue · severity · fix · verified against source.

1. **Headline box; Table 1; Figure 1a (fast) · The fast result mostly measures decoys, not realistic spacing.** Severity: BLOCKING.
   - **The ratio of decoys to scored events doubled.** ADR-0010 ruling 2 doubled fast's seeds (24 → 48) to hold the number of planted events constant. Decoys stay at 6 per recording, so they doubled.
     - New fast bench, quiet background: 240 planted events and about 288 decoys.
     - Old bench: 240 planted and about 144 decoys.
   - **CoactDetect shipped barely changed in anything but decoys.** Its recall moved only from 0.97 to 0.93. Its precision without decoys stayed at 1.00. Its precision as scored fell from 0.64 to 0.46, and that fall is entirely the extra decoy calls (130 → 265 on quiet).
   - **So the drop is mostly a change in the denominator.** The headline "CoactDetect's shipped F1 moves −0.160" and "13 of 22 vs 4 of 22" read as findings about the new spacing. Mostly they are not.
   - **Slow and combined are not affected.** Both kept 24 seeds, and their ratio of planted events to decoys is about the same or better.
   - Fix: say this in the headline. Give the planted and decoy counts per bench. Either lead the fast comparison with F1 without decoys, or state that the comparison between benches is confounded by the decoy ratio.
   - Verified: yes. I read n_planted, decoy_calls, recall and precision per background from 065/fresh-realistic and 065/fresh-bench.

2. **Figure 1a order; Table 2 rows 2, 3, 4 and 10; Table 1's "13 rows above" · The fast leaderboard ranks detectors that miss most events above one that finds 93%.** Severity: BLOCKING.
   - **The top of the list is low recall.** These rows are all ranked above CoactDetect shipped (recall 0.93/0.95):

     | row | recall, quiet / busy background |
     |---|---|
     | count (sliding) · proposal | 0.43 / 0.67 |
     | rate+context · proposal | 0.40 / 0.67 |
     | tube pick | 0.42 / 0.66 |
     | line pick | 0.40 / 0.67 |
     | chorus_norm pick | 0.64 / 0.64 |

   - **Why they rank high.** When decoys outnumber planted events, calling less raises precision as scored. This is exactly the failure ADR-0006 describes.
   - **On ADR-0006's own measure the count collapses.** Only 5 of 22 fast rows beat the reference on F1 without decoys, against 13 "above" on F1.
   - **The page's decoy caveat covers slow only**, the stream where it matters least for the reference. It says nothing on fast, where decoy handling reverses the order.
   - Fix:
     - Add a recall column, or recall on the quiet and busy backgrounds.
     - Extend the decoy caveat to fast, stating that the top four fast rows recall about 40% of events on the quiet background.
     - Count "above" on F1 without decoys beside F1.
   - Verified: yes. I computed this from the candidates.json files and briefing.json.

3. **Headline; "How to read it" ("the spread is mostly how each row handles decoys"); Table 1 slow row · On slow, the gap is CoactDetect's own recall and merges, and the rows are level.** Severity: MAJOR.
   - **The reference's slow gap is not decoys.** CoactDetect shipped has recall 0.91/0.90 on the new slow bench and 51 merged calls. The other rows sit at about 1.00 recall. So "16 of 18 above" means "CoactDetect shipped merges close events". That is a real result under ADR-0010 part 3, but the page attributes the slow spread to decoys.
   - **The picture shows one cluster, not an order.** Figure 1b shows about 15 rows between +0.031 and +0.038, with bars that overlap almost entirely.
   - **The page contradicts its own rule.** It says rows within 0.01 are level. It still names "top unflagged row LoCo · shipped (+0.038)" and uses LoCo shipped as the slow leader. Among level rows, choosing a leader is arbitrary.
   - Fix:
     - State that the slow gap is the reference's merges and recall.
     - Show the slow top as a tie group, not a top row.
     - Say the slow leader was chosen within noise.
   - Verified: yes (candidates.json, Figure 1b).

4. **"How to read it", the ORX sentence ("4 intervals of 51 change side … 0 cross") · The check cannot detect what ruling 1 asked it to.** Severity: MAJOR. This is a check without power.
   - **What ruling 1 asked.** ADR-0010 ruling 1 asks whether "the rankings hold" at slow-ORX spacing.
   - **What the page's metric counts.** It only counts whether a row's interval changes side of zero against CoactDetect.
   - **Why that metric cannot respond.** On slow, rows sit about 0.03 above zero and within 0.01 of each other. Their order could scramble completely and the count would not move.
   - **What rank agreement shows.** I computed Spearman rank correlation between new-bench and ORX-bench ΔF1:
     - fast 0.87, slow 0.70, combined 0.96;
     - the top row changes on slow (LoCo shipped → SPIKE-synch proposal; LoCo's ΔF1 falls from 0.038 to 0.021);
     - the top row changes on combined (chorus_gain_norm_part → tube_part).
   - **Two rows it examines lose their top place.** The slow and combined leaders used for the examples are not top at ORX spacing. The sentence reassures without showing anything ("It is not shown here").
   - **It also silently leaves out 9 count rows,** although 064/count/fresh-orx/candidates.json exists (51 = 60 − 9).
   - Fix:
     - Report rank agreement and whether the leader or top row is the same.
     - Say count rows were excluded, or include them.
     - Or show the ORX column.
   - Verified: yes (computed from 065/fresh-orx and briefing.json).

5. **Table 1 "unflagged"; headline "(n of them unflagged)"; Terms "budget" · "Unflagged" is not one common bar.**
   - Severity: MAJOR.
   - **Detectors are measured against very different limits.**
     - Each coded detector is held to its own limits. The comments in bench*.py say most were set by measuring that detector on the old bench and allowing margin. For example, the elevated-rate limit is SPIKE-synch 9.0 calls/min against CoactDetect 1.0 calls/min on fast, and locust 68 calls/min on combined.
     - Learned models are held to CoactDetect's strict limits.
     - The precision swing limit is 0.100 for most rows but 0.150 for rate+context on combined, with no reason on the page.
   - **The check is partly calibrated on the shipped setting it judges.** For a shipped setting, "within its own budget" is close to guaranteed. So "unflagged" counts compare rows against differently set bars.
   - **"Every budget" overstates.** Table 1 defines unflagged as "within every budget", but the close-events test "is not run". ADR-0010 part 4 retired it, and the page's wording implies it was skipped.
   - Fix:
     - Say that the budgets are per detector and derived from each detector's own measurement.
     - Give the reason for the 0.150 limit.
     - Say "every budget in force (close-events retired by ADR-0010 part 4)".
   - Verified: yes (bench.py, bench_slow.py, bench_combined.py).

6. **Section 2 ("both call it 91 calls" and so on) · The unit of the agreement counts is undefined and lopsided.**
   - Severity: MAJOR.
   - **The counts are in different units.** In `classify()`, "both call it" and "only the leader" count the leader's calls, and "only CoactDetect" counts the reference's calls.
   - **The match is many-to-one.** Spans within 2.5 s of each other agree, so one long merged call can absorb several of the other detector's calls, which then vanish from the disagreement counts.
   - **Consequence.** The three numbers are not in one unit, and a merge (the very behaviour ADR-0010 is about) lowers disagreement instead of showing up as it.
   - Fix:
     - Say whose calls each row counts.
     - Report agreement one-to-one, or report the matching cardinality: how many calls matched more than one.
   - Verified: yes (make_briefing.py lines 516–539).

7. **Combined examples; Figure 9 image · The picture undercuts the combined bench leader, and the page does not say so.** Severity: MAJOR ("read the picture").
   - **What the image shows.** In the example_combined_ref_only image, the leader's lane (chorus_gain_norm_part) is empty on three visually clear stripes in a 4-minute window where CoactDetect calls, the marked one included.
   - **What the table shows.** On real baseline windows the leader misses 71 of CoactDetect's calls (8.5 per hour in DI), against 3 calls only it makes.
   - **The tension goes unstated.** The page presents the combined leader as the bench's top row (+0.057), while its real-data behaviour on these recordings is mostly under-calling relative to the reference. The page decides nothing, but it should not leave this tension to the reader.
   - Fix: add one sentence beside the combined table: on real recordings the leader calls far fewer events than CoactDetect (71 against 3), and the figure shows missed stripes.
   - Verified: yes (PNG viewed; counts on the page).

8. **Slow examples; Figure 6 image · The "one-off" is not isolated, and it shows a pattern.** Severity: MINOR.
   - In the slow ref-only image, LoCo shipped misses two of CoactDetect's three "ref-only" slow calls inside the same 30 s window. Its lane is nearly empty while the other two detectors call the stripes.
   - The caption's "A one-off: read it as one call" is wrong on both counts: the rule fires at pool ≤ 3, and two of the three sit together here.
   - Fix: reword the rule to "one of only N calls". Say when the pool's calls concentrate in one recording.
   - Verified: yes (PNG, and the code's `pool <= 3`).

9. **Section 2, the leader rule and its reference · The examples are compared against a different reference than the leaderboard.**
   - Severity: MINOR, because the page discloses it.
   - The examples compare against CoactDetect proposal, which is on a search limit. The leader rule meanwhile disqualifies other rows for sitting on a search limit (LoCo proposal).
   - It also passes over LoCo shipped and the count rows because they "did not run on the real recordings". So on fast, the ninth row is shown as the leader.
   - Fix: say plainly that the real-data examples cannot test the leaderboard's top rows, and give the reason (the review run used the proposal settings).
   - Verified: yes (code, lines 452–464 and 603–700).

10. **Headline and Table 1 counts · Duplicate and near-duplicate rows inflate the "above" counts and the medians.** Severity: MINOR.
    - Fast CoactDetect proposal and LoCo proposal are "one result, shown twice", yet both are counted among the 13 above.
    - Fast count (binned) starting point matches CoactDetect shipped (0.608 · 0.967; ΔF1 +0.000). That near-identity is not remarked on.
    - "Median F1 of the other rows" takes the upper middle value for an even number of rows. Fast new is printed as 0.641; the true median is 0.639.
    - Fix: count distinct results. Use a true median, or say "upper median".
    - Verified: yes (computed).

11. **"How to read it" · The seed counts differ between benches, and the interval is uncorrected, but conclusions are drawn from counting intervals.**
    - Severity: MINOR.
    - Fast new has 48 seeds and fast old has 24, so the intervals have different widths. "Rows with the interval above zero" is not comparable across the two benches: the new bench has more power.
    - The page states that intervals are uncorrected, but then counts them in the headline.
    - The page never explains why fast has 48 seeds (ADR-0010 ruling 2).
    - Fix: give the reason for 48 seeds and warn that counts of intervals differ in power between benches.
    - Verified: yes (seeds_by_bench).

12. **Pooling across the design · The leaderboard pools the two backgrounds and the groups.** Severity: MINOR.
    - F1 is averaged over the quiet and busy backgrounds, and there is no per-background view.
    - Findings 1 and 2 are strongest on the quiet background (recall about 0.40 against 0.67 on busy).
    - The bench's backgrounds and spacing pool all four groups, as ruled in ADR-0010 ruling 1, and only the ORX check probes that.
    - Fix: offer a per-background ΔF1, or at least recall per background, in Tables 2–4.
    - Verified: yes (candidates.json).

13. **Briefing folder · Stale artifacts sit beside the shipped page.** Severity: MINOR.
    - figure1_leaderboard.svg and example_slow_leader_only.png come from an earlier build, 20:29 against 20:58–20:59 for the rest. The page references neither.
    - The stale slow leader-only PNG is a figure for a kind the page says has no example ("no call of this kind lies at least 10 s inside").
    - Fix: have the builder clear its own old outputs, or list what it wrote.
    - Verified: yes (`ls`, and grep of index.html).

**Checked and found sound:**
- The count rows added from later runs are properly paired. The later files reproduce CoactDetect shipped's F1 exactly on the same seed ranges.
- The examples' per-group hourly rates use the right per-group denominators, for example 46/5.7 h = 8.1 per hour.
- The page correctly discloses that the intervals exclude the choice among training runs, that proposals and picks were chosen on the new bench, and that the old bench decides nothing.
- Example selection by median participant count is a reasonable choice for representativeness.

**Paths:**
- Generator: <worktree>/tools/make_briefing.py
- Artifact: <darkroom>/bugarach/2026-09-26-full-panel/briefing/index.html
- Sources used: <darkroom>/bugarach/2026-09-26-full-panel/065/{fresh-realistic,fresh-bench,fresh-orx,fresh-bench-count}/candidates.json and 064/count/fresh-realistic/candidates.json
- Budget tables: <worktree>/src/bugarach/bench.py, bench_slow.py, bench_combined.py
- Scratch: <scratchpad>/mb2/r4_*
