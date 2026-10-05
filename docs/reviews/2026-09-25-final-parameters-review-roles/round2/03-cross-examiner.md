GRANT 3 ok — Read, Grep, Glob

# Role 3 — Cross-Examiner: docs/learned/runs/2026-09-25-final-parameters/README.md

**Artifact:** README + four figures, `adoption.json`, `adoption_table.md` (all in `docs/learned/runs/2026-09-25-final-parameters/`).
**Companions:** `docs/goals/coded-detector-optimization.md`, `docs/handoffs/2026-09-25-overnight-final-parameters.md`, `docs/handoffs/README.md`, ADR-0008, ADR-0009, `docs/GLOSSARY.md`, CLAUDE.md house conventions.
**Source records:** `<darkroom>/bugarach/2026-09-25-final-parameters/` — `064/phase3/candidates.json`, `065/phase3/candidates.json`, `064/phase3-3x3/cross_stream.json`, `064/phase3-3x3/selection_budgets.json`.

**Counting basis:** each count was checked on the basis the page declares for it. Tables 1–3, Figure 1 and Figure 2 are fresh seeds (24 recordings per background; 120 planted events per level). Held-out gains are seeds 49–96. Decision 3's "selection" column is `selection_budgets.json`.

## Findings (location · issue · severity · suggested fix · verified against a source)

1. **Decision 1, third bullet ("Combined rate+context's barely touch").** The intervals do not touch: shipped [0.642, 0.726] vs proposal [0.748, 0.793], a gap of 0.022, which is wider than fast binned SCE's (0.765 vs 0.769, 0.004) — and the same bullet calls fast binned SCE's "do not overlap". The page understates the independent check for one of the four proposals Tony is asked to adopt, and ranks the two backwards. · **major** · "fast binned SCE's and combined rate+context's intervals do not overlap; combined binned SCE's and combined SPIKE-synch's overlap." · verified yes (Table 1; `adoption.json` fresh intervals).

2. **Table 2 held-out column vs Decision 3's table.** For fast rate+context, fast SPIKE-synch and combined rate+context (shipped), Table 2 prints held-out **"pass"**. Decision 3 says the same precision-swing value is "not recorded" on held-out, and `adoption.json` has `precision_swing: {value: null, ok: null, note: "not recorded in the search's held-out rows"}`. Table 2's own caption says "Not checked" marks a missing check, so the table contradicts itself: every held-out "pass" silently omits the precision swing. · **major** · In the generator (`tools/make_final_parameters_report.py`), render a null check as "pass (precision swing not recorded)" or "not checked", not "pass", in every held-out cell. · verified yes.

3. **Decision 7, the bullet under the table ("25 of 40, 20 of 40 and 15 of 40 for the last three rows").** That table's last three rows are combined quiet, combined busy and slow busy. Figure 4's values belong to fast busy (middle, 25/40), combined busy (middle, 20/40) and slow busy (lowest, 15/40), i.e. rows 2, 4 and 5. · **major** · Name the rows: "fast busy middle 25 of 40, combined busy middle 20 of 40, slow busy lowest 15 of 40". · verified yes (Figure 4 right panel).

4. **Decision 7's table — stream order.** Rows run fast, fast, combined, combined, slow, and slow quiet is omitted. Table 3, Figures 1–2 and every other table use fast → slow → combined. Two tables of the same quantity in different orders cannot be lined up, and the mismatch is part of what caused finding 3. · minor · Order the rows fast, slow, combined, and either include slow quiet (0/120 at every level) or say it is omitted because nothing is under the floor there. · verified yes.

5. **Decision 7, last bullet ("each planted recording's floor sits about one ROI above the no-coordination recording's floor").** Figure 4 contradicts this on slow: the no-coordination bar is ~3–4 ROIs and the planted quiet bar 6–7, so about 3 ROIs higher. Fast (4–5 vs 5–6) and combined (5–6 vs 6–7) are ~1 ROI. Figure 4's legend also shows the no-coordination recording on the quiet background only, so "on the same background" holds only for quiet. · **major** (it supports the "event set partly defines itself" reading) · "about one ROI above on fast and combined, about three on slow (quiet background; the no-coordination recording was probed on quiet only)". · verified yes (read off Figure 4).

6. **Decision 7 ("as ADR-0009 anticipated").** ADR-0009's Consequences put the share of fast and combined events leaving scoring at "a third to a half". Table 3 gives fast busy 205/360 (57%), combined busy 175/360 (49%) and quiet 120/360 (33%), so fast busy is outside what the ADR anticipated. · minor · "as ADR-0009 anticipated, and more on fast busy (57%)". · verified yes.

7. **Decision 1, second bullet ("1.28 calls per hour … on the held-out seeds … Figure 3 shows the same point above its bar").** 1.28 is the held-out search-row value (`065/phase3/candidates.json` `elevated_out_busy_per_hour` 1.28125), while Figure 3 plots the fresh elevated-rate seeds 66000–66011, where the same proposal reads 1.375/h. The figure does not show "the same point": both the number and the seed set differ. · minor · "1.28 calls per hour on the held-out seeds and 1.38 on the fresh ones (Figure 3)". · verified yes.

8. **Decision 3's table, slow locust row ("quiet background").** The inside-stretch budget gates both backgrounds (Figure 3 caption, README L352), and slow locust shipped also fails on busy (fresh 4.35 calls/min vs the 4.0 limit, `065/phase3/candidates.json`). Labelling the row "quiet background" implies busy passed. · minor · Add the busy value, or "(quiet; busy 4.35 fresh also over)". · verified yes.

9. **Decision 2, second bullet ("On fast, the proposal did not move `n_synchronous_frames` …").** Slow is the same case: the slow locust proposal has `n_synchronous_frames` = 1 (`adoption.json`) and Table 1 lists no change to it, so slow's shipped point also sits at 1. As written, the reader infers slow's shipped point differs. · minor · "On fast and slow …". · verified yes (`adoption.json` locust params).

10. **Decision 8's table.** It is a selection, but the lead sentence reads as a complete list. It omits the largest case on fast: the combined-tuned rate+context proposal scores 0.736 [0.714, 0.759] on the fast bench against fast's own shipped 0.703 [0.678, 0.727] (`cross_stream.json`). The three listed values were verified exactly (0.820 [0.806, 0.838]; 0.865 [0.855, 0.874]; 0.827). · minor · Add the row, or say "for example". · verified yes.

11. **What ran, "The 3 × 3" bullet ("for all 38 versions") vs Figure 2.** Figure 2 shows 24 versions (8 detectors × 3 streams). The 38 in `cross_stream.json` `diagonal_check` counts 18 coded shipped + 14 proposals + 6 chorus fits (matching Table 2's 38 rows). Two different "version" counts sit on one page with no stated basis. · minor · "all 38 (every shipped point, proposal and picked chorus fit; Figure 2 shows the 24 chosen ones)". · verified yes.

12. **Table 1 vs Decision 1's table; CLAUDE.md "every number carries its unit".** Decision 1 writes `bin_width_sec` 10 → 2 s and `excess_threshold_hz` 4.5 → 6 Hz, while Table 1 drops the units on the same values, and gives none for `dt` 0.1 → 0.00625, `max_gap` 4 → 8, `tau_max` 0.5 → 1, `merge_gap_s` 3 → 5, `int_win_sec` 2 → 3 or `context_win_sec`. · minor · Have the generator append units (s, Hz, frames, bins). · verified yes.

13. **Figure 3's x-axis tick labels ("SCE").** Tables 1–2, Figures 1–2 and the prose all say "binned SCE"; Figure 3 says "SCE". · minor · Relabel "binned SCE". · verified yes.

14. **Definitions, "Decoy", vs the glossary.** The glossary has no "decoy"; its term for this object is **distractor** ("a planted correlated burst … differs only in its label"). "Decoy" comes from ADR-0006 (which notes `distractor` in code), so the page uses an unglossaried synonym for a glossary term. · minor · Add "decoy" to the glossary as the reader-facing name for *distractor* in the same PR, or use "distractor" here. · verified yes.

15. **Definitions, second bullet ("SCE …, ROI …, **stream**. The event trace analysed …").** Three terms are fused into one bullet, so "The event trace analysed" reads as though it defines ROI. · minor · Split into separate bullets. · verified yes.

16. **"How to read them" (held-out "400-resample interval") vs the fresh intervals.** The resample count is stated for the held-out gain only; the fresh and 3 × 3 intervals come from `n_boot` 2000 (`cross_stream.json`), which the page never says, so two bases for a "95% interval" sit side by side. · minor · State "2,000 resamples over recordings" for the fresh and Figure 2 intervals. · verified yes (from the 3 × 3 file's 2,000).

17. **Decision 4 ("the loss is 0.0165, inside the 0.02 allowance") and What ran ("re-derived independently in review").** Neither `adoption.json` nor any record checked holds the 0.0165 re-run (`adoption.json` carries only −0.0441), so a number that overturns Table 2's verdict has no record a reader can open. · minor · Name where the re-run lives, or add it to `adoption.json`. · verified no (absent from every record checked).

18. **Decision 4 ("combined's sits at a context of 120 s … which the bracketing record does not flag") vs Table 1's slow LoCo row.** The bracketing record flags slow LoCo's `context_win_sec` 120 s as "edge" but does not flag the same 120 s cap on combined CoactDetect. The page acknowledges the gap for Coact but not the inconsistency, so Table 1's "bracketed" column applies two rules to one condition. · minor (no verdict changes; combined Coact is already unbracketed on alpha) · Note in "How to read" that 120 s is flagged "edge" for LoCo and not for CoactDetect, or fix the record. · verified yes (`adoption.json` combined Coact at 120 s; Table 1 slow LoCo edge).

19. **Real data, "What it found" (OVX +17, ORX +20) vs the goal page.** The goal page's 2026-09-24 entry gives fast medians 6 → 24 (OVX) and 4 → 26 (ORX), i.e. +18 and +22. Floors do not depend on detector settings, so the two runs should agree unless the bases differ (median of paired differences vs difference of medians, or v3 vs the earlier run). · minor · State the basis ("median of each recording's own − baseline"). · verified no (`065/phase3-real-v3` not opened).

20. **Goal page, "Waiting on Tony" table, link text "[report, *What waits on Tony*]".** The report has no such section; the rulings are under "The rulings the adoption depends on" plus Decision 1. · minor (companion) · Change the anchor text to match. · verified yes.

21. **Glossary, elevated-rate test entry ("Since ADR-0009 (2026-09-25)").** ADR-0009 was accepted 2026-09-24. · minor (companion) · Change the date to 2026-09-24. · verified yes.

22. **Runbook "Verify each run record … intervals are paired" vs Decision 1's note that the fresh paired gain "was not computed".** The runbook's check was not met for the fresh seeds. The page discloses this but does not tie it to the runbook requirement. · minor · One clause: "(the runbook asked for paired intervals; the fresh ones are not)". · verified yes.

## Checked clean (verified against the sources)
- **Decision 1:** the four proposals' settings, gains and fresh intervals match Table 1.
- **Decision 2:** the five limit rows and gains match Table 1. "Nine if a limit counts" = 4 adoptable + 5 limit-only (fast locust, slow rate, slow SPIKE-synch, slow locust, combined locust). Slow binned SCE is bracketed but fails close-events, which is consistent. All 14 proposals are accounted for: 4 adoptable, 5 limit-only, 4 unbracketed, 1 close-events failure.
- **Decision 3:** 0.181 / 0.181 / 7.24 / 0.245 match `selection_budgets.json`; 0.148 / 0.175 / 7.23 / 0.257 match the fresh precisions and elevated-rate calls in `candidates.json`; the limits 0.10 / 0.10 / 4.0 / 0.15 match.
- **Table 3:** every count and floor range matches the fresh `under_floor` records (85, 55, 50; the 120-per-level basis).
- **Figures:** Figure 1 markers match Table 1; Figure 2 diagonals match Table 1 to rounding. Figure 3 points were checked against `candidates.json` (fast locust 30.35/25.4, slow locust 7.23/4.35, combined rate+context outside 10.125 and 1.375, fast rate+context 3.25), and its budget bars against the selection limits.
- **Counts:** "Four shipped points out of budget" matches Table 2 and the goal page; "seven rulings" matches Decisions 2–8; seed ranges agree across README, glossary, runbook and `candidates.json`; 128 × 3 × 8 = 3,072.
- **House rules:** no "fire" and no "data is" in the artifact; the one group mention (OVX, ORX) is in canonical order; figures are numbered and named.
