> Archived verbatim except redactions: values of individual real calls (one example's gap in R2-2 and one
> caption's participant count and floor in R2-10) are replaced by `[t]` or `[n]` (FOUNDATIONS §5). Aggregates are
> kept.

GRANT 4 ok — Read, Grep, Glob, Bash

(I also hold SubagentHandback, which is only the report channel. I hold no Edit, Write or NotebookEdit. I kept to the blind: nothing under docs/reviews/briefing_2026-09-26-roles/ and no git history of the generator or its tests. Scratch work went only to <scratchpad>/mb3/: a text extract of the page, the two Figure 1 SVGs rendered to PNG, and recomputations run from the night's calls.csv and from the generator's own build().)

# Role 4 (Reviewer 2): findings on the full-panel night briefing

Artifact: <darkroom>/bugarach/2026-09-26-full-panel/briefing/index.html. Generator: <worktree>/tools/make_briefing.py.

Row format: location · issue · severity · fix · verified against a source (yes/no).

## Blocking / major

**R2-1** · Section 2, the Table 7 caption line ("the leader calls many events CoactDetect does not: 213 calls only its own against 5"), and the matching lines under Tables 6 and 8.
- **Issue: overreach, and an unequal comparison on real data.** The leader is a learned model and runs with no floor. CoactDetect runs at the window's own participation floor (ADR-0008). So CoactDetect cannot call below the floor at all, and the leader can.
- I recomputed from 065/review/detect/calls.csv, counting participants the page's way:
  - Slow: only **44 of the 213 leader-only calls reach their window's own floor**. The median is 7 participants, against 19 for the calls both detectors make. All 421 agreed calls reach the floor.
  - Fast: all 32 leader-only calls reach the floor. Combined: all 3 do.
- So on slow, about four in five of the "events CoactDetect does not call" are sub-floor calls. ADR-0008's floor exists to exclude exactly those.
- The page describes the floor asymmetry mechanically ("the four detectors that take the participation floor … at their own window's floor, the rest as they ran"). It never draws the consequence, and it calls them "events".
- **Fix:**
  - Say "calls", not "events".
  - Add a column to Tables 6–8: disagreement calls at or above the window's own floor.
  - Say plainly that the floored and unfloored sides are not like for like.
  - Or compare the leader after applying the same floor.
- Verified: yes (recomputed; my totals match the page's 91/32/1, 421/213/5 and 388/3/71 exactly).

**R2-2** · Figure 3 (fast, leader only) and Figure 9 (combined, leader only).
- **Issue: the examples are not representative, and the pictures undermine their own captions.** I computed the nearest-call gap for every disagreement call (aggregates only):
  - Fast leader-only: 29 of 32 are more than 10 s from any CoactDetect call. **Exactly one** is within 3.5 s, and that one is the example the median-participant rule chose. Its caption reads "2.5 s away, beyond the 2.5 s tolerance", which is self-contradictory as printed.
  - Combined leader-only: 1 of 3 is within 3.5 s, and again it is the one shown ([t]).
- **What the images show:**
  - Figure 9: the leader lane has **two** calls on one population burst. CoactDetect has one call on it, a few seconds from the leader's first. That is the leader splitting an event CoactDetect also called, not calling an event CoactDetect missed. Whether the burst is really two sub-events is ambiguous.
  - Figure 3: the marked call is a small trailing cluster a few seconds after a large burst that both detectors call. Again a boundary or split case.
- The selection rule (median participant count) is blind to the gap, so it happened to pick the least typical member of each pool.
- **Fix:**
  - Print the gap distribution per kind beside each table (for example ≤5 s / 5–10 s / >10 s). It strengthens the page: most disagreements are far apart.
  - Pick examples only from calls clearly beyond tolerance (for example gap >2× tolerance). Or show the marginal case as a labelled margin example next to a typical one.
  - Print gaps to 0.1 s so "2.5 s beyond 2.5 s" cannot appear.
- Verified: yes (recomputed from calls.csv; looked at both PNGs).

**R2-3** · Headline paragraphs of section 1, Table 1, Figure 1.
- **Issue: the headline counts measure the reference's change, not the rows.** "12 of 21 rows above zero on the new bench vs 3 of 21 on the old" reads as the rows being better.
- Figure 1a shows the actual picture: most rows move right by a near-uniform +0.03 to +0.06 between benches. That is a common-mode shift of the zero line, because CoactDetect's shipped setting degraded (fast F1 0.769→0.608; slow merges 0→51).
- Everything tuned or trained on the new bench is compared with a reference that was not. The page discloses this ("their new-bench numbers favour them"), but the fair comparison is against CoactDetect's own new-bench proposal: **0 of 20 (fast), 1 of 17 (slow), 1 of 19 (combined)**. That appears second, as a subordinate clause.
- **Fix:** Lead each stream's sentence with the proposal comparison. Present the shipped-setting counts as "how much the old reference setting loses on the new bench".
- Verified: yes (read from the page's own tables and the Figure 1a render).

**R2-4** · Section 1 leaderboard statistic (ΔF1, Figure 1, Tables 1 and 3–5) against ADR-0006.
- **Issue: the ranking statistic scores decoy calls as false alarms.** ADR-0006 decision 1 rules those calls coordination by construction: "not a false alarm, whatever label a bench gives it".
- The page's own fast explanation says CoactDetect's drop is "mainly because it calls decoys". Its F1 without decoys is 0.967, and on that basis only 4 of 21 rows beat it.
- So the headline intervals rest on penalties the house definition rejects. The decoy-free view gets no interval: "F1 without decoys above the reference's" is a comparison of point values.
- The page complies with ADR-0006's letter (both columns are shown) but not its inference. The headline claim should not be one that ADR-0006 says is measuring the wrong thing.
- **Fix:**
  - Compute paired ΔF1 without decoys, with a bootstrap interval. It can be derived from the per-seed data the scorer already holds.
  - Make it at least co-equal in Table 1 and Figure 1.
  - Say in the headline that the with-decoy ranking is the one ADR-0006 disputes.
- Verified: yes (ADR-0006 decision and consequences read; page numbers checked).

**R2-5** · Headline fast paragraph: "calls decoys 2.1 times as often (214 to 439 calls)".
- **Issue: misleading.** The per-seed decoy rate is unchanged: 214/24 seeds = 8.9 against 439/48 seeds = 9.1. The same holds for SPIKE-synch (107/24 against 219/48 in briefing.json).
- The doubling comes from doubling the seeds (ADR-0010 ruling 2), not from CoactDetect behaving differently. The sentence goes on to give the right mechanism (half the planted events per recording), but its opening clause states a behavioural change that did not happen.
- **Fix:** "calls decoys at the same rate per recording (about 9), but each recording now plants about half as many events, so decoys are twice the share of its calls."
- Verified: yes.

## Medium

**R2-6** · Section 1, ORX paragraph (ρ = 0.91 / 0.76 / 0.94, under "Does the order hold?").
- **Issue: the check barely has the power to fail at the top, where the question lives.** Rank correlation over all rows is carried by the clearly bad tail (shipped locust, rate+context, binned SCE).
- I recomputed with the generator's own build():
  - Rows within 0.02 of the top: ρ = 0.80 (fast, 4 rows), 0.66 (slow, 16 rows), **0.50 (combined, 8 rows)**.
  - Rows with ΔF1 ≥ 0: 0.71 / 0.72 / 0.89.
- The top row changes on **every** stream. That is the direct answer to "does the order hold", and it points the other way from the ρ figures. ρ is given with no n and no interval.
- **Fix:**
  - Report ρ among the level or top rows alongside the all-rows ρ, with the number of rows.
  - State that the top row changes on all three streams.
  - Soften to "the tail order holds; the top does not".
- Verified: yes (recomputed).

**R2-7** · Sections 1 and 2: "Level means within 0.01 F1, the noise unit ADR-0010 uses"; "rows the leaderboard cannot separate: 8 rows sit within 0.01".
- **Issue: an unjustified constant, inconsistent with the page's own uncertainty.** ADR-0010 defines 0.01 as the "draw-to-draw spread measured in the fair comparison": a different experiment, on the retired bench, used there for a focus rule.
- The page's own paired 95% intervals have half-widths of about 0.015–0.035. So rows 0.01–0.03 apart are equally inseparable, and "cannot separate" understates how many rows are tied.
- The Table 3–5 F1 columns and ΔF1 also disagree by up to about 0.015 (for example fast SPIKE-synch: F1 difference 0.078 against ΔF1 0.063), which is more than the "level" unit.
- **Fix:** Define "level" from the page's own data (overlapping paired intervals, or a row-vs-top paired interval). Or state why a borrowed 0.01 applies here.
- Verified: yes (ADR-0010 part 1 read; arithmetic from Tables 3–5).

**R2-8** · Budget marks, "unflagged", and the leader rule (Terms: budget; section 1 "Budgets" paragraph).
- **Issue: "within budget" is not one standard, and the page does not tell the reader so.** Limits are per-detector ceilings set just above each detector's own shipped measurement. From src/bugarach/bench*.py:
  - fast precision drop: binned SCE 0.50, CoactDetect 0.10;
  - fast probe: SPIKE-synch 9.0/min, CoactDetect 1.0/min;
  - combined probe: locust 68/min.
- Learned models are held to CoactDetect's limits.
- So "unflagged" largely means "no worse than its own shipped behaviour", which a shipped setting passes almost by design. That makes it a check with little power for shipped rows. It is also a stricter bar for learned rows than for some coded ones, and the leader choice rests on it.
- The ceilings' docstring says they were measured on seeds 1–48 at the settings each module ships. I could not confirm on which bench they were measured.
- **Fix:**
  - Say on the page that limits are self-referenced ceilings, give the spread of limits across detectors, and say which bench they were measured on.
  - Flag the asymmetry for learned models.
- Verified: partly. The limits are verified; the bench they were measured on is not.

**R2-9** · Learned rows in Tables 1 and 3–5 ("wholly above zero" counts).
- **Issue: the wrong uncertainty for learned rows.** The interval covers seeds only (the page says so), but run-to-run spread is often many times the interval: held-out F1 0.25–0.67 (fast chorus_norm_part), 0.10–0.80 (combined chorus_norm), against intervals about ±0.02.
- Counting a learned pick as "wholly above zero" treats the luckiest of five runs as the model.
- **Fix:** Count learned rows separately in Table 1. Or report how many of the five runs would clear zero. At minimum, move the caveat into the headline sentence.
- Verified: yes (read from Tables 3–5).

**R2-10** · Section 2, participant counts in the Figure 2–10 captions.
- **Issue: an undefined baseline.** "with [n] participating ROIs" gives no chance expectation. The ±1 s window around a multi-second slow span is long, and at slow background rates several onsets land in it by chance.
- The window's own floor is available (own_floor in calls.csv) and is the house measure of "more than chance".
- **Fix:** Print the call's participant count against its window's floor (for example "[n] participants; floor [n]").
- Verified: yes (the fields exist; see R2-1 for the aggregate).

## Minor

**R2-11** · Table 2 and the slow/combined headline: "merges close events (0 to 51 merged calls)".
- **Issue: a check that cannot fail.** On the old bench planted events are at least 120 s apart, so a merged call is impossible by construction. "0 merged" there is not a measurement.
- Likewise, slow and combined old-bench recall of 1.00 and decoy-free F1 of 1.000 for the reference are at ceiling. The old-bench comparison can only register decoy behaviour, which is also why all 18 slow rows sit wholly below zero there.
- **Fix:** Mark the old-bench merged column "— (impossible at ≥120 s spacing)" and note the ceiling.
- Verified: yes (by construction, from the Terms definition of the old bench).

**R2-12** · Section 2 agreement rule.
- **Issue:** Agreement is span-to-span and many-to-one. The bench (score.py) matches one-to-one, from planted time to span, closest first. The page calls it "the bench's scoring tolerance", but it is a looser relation.
- It is disclosed ("one call can agree with several", and the counts of multi-matches), but the looser relation inflates "both call it". Per-group counts are fine.
- **Fix:** Call it "the bench's tolerance value, under a looser matching rule".
- Verified: yes (score_detections read).

**R2-13** · Section 2 constants.
- **Issue:** Several constants appear with no reason given on the page: the 10 s edge exclusion, the 45 s / 120 s example half-windows, and the ±1 s participant window (said to be "the review tool's way" but not justified). The reasons for the first two exist only as code comments.
- **Fix:** One clause each.
- Verified: yes.

**R2-14** · Tables 6–8 "all groups" column and the pooled sentences beneath them.
- **Issue:** The pooled count carries no rate. The disagreement is concentrated by group (fast leader-only: DI 2.8/h and MALE 2.3/h against ORX 0.3/h), but the pooled sentence reads as uniform.
- Separately, the same learned family (chorus_gain_norm_part) is the leader on both fast and combined yet behaves in opposite directions: +32/−1 on fast, +3/−71 on combined. The page does not remark on it.
- **Fix:** Add a pooled rate. Drop the pooled sentence or make it per group. Note the opposite behaviour.
- Verified: yes.

**R2-15** · Figure 1a, row "count (binned) · starting point".
- **Issue:** The row is numerically indistinguishable from the zero line on both benches (F1 0.608 against 0.608; interval [−0.001, +0.000]). It is probably the same computation as the reference (a bin count at the floor), but the page's exact-duplicate note only fires on a match to every digit, so it is not flagged.
- **Fix:** Note that it reproduces CoactDetect's shipped setting to within 0.001.
- Verified: yes (read from Table 3).

**R2-16** · Headline: "12 of 21 … 95% interval wholly above zero".
- **Issue:** The intervals are uncorrected across many rows (disclosed in "How to read it"), but the headline counts them as though they were independent tests.
- **Fix:** Put "uncorrected" in the headline sentence, or give the expected number by chance.
- Verified: yes.

## Checked and found sound

- Totals by agreement kind, and group counts, in Tables 6–8.
- The ORX ρ values as the page computes them.
- The "4 of 21 above on F1 without decoys" count.
- The doubled fast seeds (48/24/24) against ADR-0010 ruling 2.
- The page's disclosure that the section 2 examples use CoactDetect's proposal rather than the shipped setting.
- The passed-over lists follow the stated rule.
- All nine example PNGs and the fast and combined Figure 1 panels were opened. The slow Figure 1 panel was checked via its table. Figures 4, 7 and 10 (CoactDetect only) do show a visible vertical streak the leader missed. Figure 6 (slow, leader only) sits on a sparse, dispersed cluster, consistent with R2-1.

Relevant paths: <darkroom>/bugarach/2026-09-26-full-panel/briefing/{index.html, briefing.json, example_*.png, figure1_*.svg}; <darkroom>/bugarach/2026-09-26-full-panel/065/review/detect/calls.csv; <worktree>/tools/make_briefing.py (classify, pick_one, orx_check, NOISE_UNIT, EDGE_SEC); <worktree>/src/bugarach/bench.py, bench_slow.py, bench_combined.py (budget ceilings); <worktree>/src/bugarach/score.py (TOL_SEC, score_detections); docs/adr/0006-*, 0010-*.
