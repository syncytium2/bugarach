> Archived verbatim except: in finding 14, one real call's gap and one example time are replaced by `[t]`
> (FOUNDATIONS §5), and repository paths are shown as `<repo>` (SAP004).

GRANT 3 ok — Read, Grep, Glob (I also hold SubagentHandback, which only delivers this report and cannot edit anything)

**Role 3, Cross-Examiner: blind review of the full-panel briefing.** I did not open `docs/reviews/briefing_2026-09-26-roles/` or the generator's git history.

**What I checked:**
- Every Table 1 count cell, recounted by hand from the per-row intervals in Tables 3–5 and cross-read against `briefing.json`.
- The headline box against Tables 1 and 2.
- Figure 1a/1b/1c row counts, row order, orange marks and † marks against Tables 3–5.
- The leader and runner-up choices and their passed-over lists against the stated rule.
- Tables 6–8 group sums and per-hour rates.
- The Table 9 total, and group order everywhere.
- The seed/run renumbering against 064/README.
- The held-out F1 spreads against 064/README's picks.
- The ORX-check counts against 065/RUN_C.md and 064/count/README.md.
- Budget and search-limit claims against 065/README.md.
- Timestamps against RUN_C.
- Terms against `docs/GLOSSARY.md` and ADR-0006.

**Clean:**
- All 36 Table 1 count cells reproduce from Tables 3–5 under the page's own rules, including every "top unflagged row" and "N other rows level" entry.
- Figure titles (23/19/21 rows) match Tables 3–5, and the figure order matches the table order.
- Every orange mark matches a budget mark in the tables, and every † matches a search-limit mark.
- The 11 † proposals match 065 README's "11 of the 12 proposals are unbracketed"; the combined SPIKE-synch proposal is correctly the only one without †.
- Training run N = the notes' seed N−1 for all 24 picks.
- Tables 6–8 rows sum to their "all groups" column.
- Table 9 sums to 66 recordings, and so does 065 README.
- The 24 review pages = 4 groups × 2 treatments × 3 streams.
- Group order is DI, OVX, MALE, ORX everywhere.
- "6 intervals of 59" reproduces: 59 = 21 + 18 + 20. The 6 are RUN_C's 4 shipped-basis entries plus 2 count rows from 064/count's ORX tables.
- All source timestamps convert correctly from RUN_C's UTC.
- The page says where it departs from 065 README's "only one row over budget", and it discloses that the count folder calls its starting point "shipped".
- No "fire"/"fired", no "modality", no singular "data".

## Findings (location · issue · severity · fix · verified?)

1. **Fast Figure 1a / Table 3 row 1 (SPIKE-synch · shipped, the fast leaderboard's top row) vs 064/README.md section A** · 064/README says the fast SPIKE-synch search did move: its shipped point was out of budget and was rescued to `tau_max` 0.5 s, with gain −0.018. 065/README lists "SPIKE-synch on fast" among searches that proposed nothing. The page silently follows 065: it has no fast SPIKE-synch proposal row. Its Terms entry then says "A detector whose search found the shipped setting best has no proposal row", which 064's record contradicts for this detector. The page's own Table 3 marks the shipped point over budget, which matches 064. So the top row of Figure 1a is a setting one companion says the search replaced, and the page does not mention the conflict. · **Major** · State that 064 records a rescued proposal and why no row is scored for it (for example, the scorer drops a rescue with negative gain). Otherwise score that row. Either way, fix the Terms line so it does not claim "shipped was best" here. · Verified: yes (064/README, 065/README, page).

2. **Table 1 caption and the fast old-bench row; headline "3 of 21 on the old bench"** · The caption says "a row that repeats another's scores counted once". LoCo · proposal repeats CoactDetect · proposal only on the new bench; the Table 3 note says so ("to every digit on the new bench"). On the old bench its scores differ (+0.031 vs +0.033), yet it is still dropped. Evidence: fast old reads 3 of 21, and it would be 4 of 22 with LoCo · proposal counted. Its "level" count (2) and its without-decoys count (4) also leave it out. So one duplicate rule is applied to a bench where the scores are not duplicated. · Moderate · Dedupe per bench, which makes fast old read 4 of 22. Or say in the caption that the new bench decides the dedupe for both. · Verified: yes (recounted from Table 3).

3. **Section 2 notes ("8 / 15 / 2 rows sit within 0.01 F1 of the top unflagged row") vs Table 1 and the headline ("7 / 14 / 1 other rows")** · The two passages count on different bases: Section 2 includes the top row itself, Table 1 counts only the others. A reader sees 8 against 7, 15 against 14 and 2 against 1 for the same set. · Minor · Use one basis on the whole page. For example, Section 2 could say "7 other rows sit within…". · Verified: yes.

4. **Headline box, Slow and Combined ("its recall is 0.91 against 1.00", "0.92 against 1.00")** · Table 2 gives recall as quiet · busy: 0.91 · 0.90 and 0.92 · 0.91. The headline quotes the quiet value alone and does not say so. · Minor · Write "recall 0.91 quiet, 0.90 busy, against 1.00", or say "quiet". · Verified: yes.

5. **Figure 3 caption** · "The nearest of CoactDetect's calls … is 2.5 s away, beyond the 2.5 s tolerance." At the precision shown, this contradicts itself. · Moderate (a reader will take it for an error) · Print enough decimals to show the gap, for example "2.54 s". · Verified: yes (text only; I did not open the image).

6. **ORX paragraph: "(The worker's run notes count 17, because they also count intervals against CoactDetect's proposal.)"** · The explanation is incomplete. RUN_C's 17 are 13 intervals against the proposal plus 4 against the shipped setting. The page's 6 are those 4 plus 2 count-rule intervals (slow count (binned) starting point, combined count (binned) starting point) that RUN_C never scored. So the notes and the page differ in both directions, not only by the proposal basis. · Minor · Say: "…17: 13 against CoactDetect's proposal and 4 against its shipped setting; this page adds the 2 count-rule intervals the notes did not score." · Verified: yes (RUN_C list, 064/count ORX tables).

7. **Flags on shipped rows (slow and combined LoCo · shipped, slow rate+context · shipped, slow binned SCE · shipped)** · These rows carry search-limit marks that 065/README's ruling-5 table does not list, because that table covers only the 12 proposals. The page's Terms explain the logic: when the search found shipped best, shipped is what gets flagged. But two things are unsupported by the companions:
   - The page names "merge gap none" as the limit for the combined SCE proposal, where 065/README says that proposal is "recorded as unbracketed with no axis named, and I have not looked into why".
   - The combined LoCo · shipped row reports "bin width 0.5 s, at the edge of the grid". 064/README gives LoCo's shipped bin width as 1 s (on fast), so a reader will ask whether this row is really the shipped setting.

   · Moderate · Add one line saying these marks come from the search records' bracketing on non-proposal rows, which the run notes do not cover. Say where the combined SCE axis was read from, since the notes say it is unnamed. Confirm per stream that the combined LoCo row's setting is the shipped one. · Verified: partly. The companion text is verified; the source of the page's axis name is not.

8. **Terms "training run … numbered 1 to 5 here"** · Every companion (064/README, 065/README, RUN_C, model filenames) numbers them seed 0–4. The page never gives the mapping, so a reader who cross-checks "run 5" against the notes' "seed 4" is off by one. · Minor · Add: "run 1 is the run notes' seed 0." · Verified: yes (all 24 picks map as N−1).

9. **"decoy" (headline, Budgets, Terms) vs GLOSSARY "distractor"** · The page uses a term that is not in the glossary and points at the glossary's "distractor". ADR-0006 uses "decoys", so the page is right to. The defect is in the glossary: it has no "decoy" entry, and its "distractor" entry still calls counting a decoy call an "open question", which ADR-0006 settled. The reserved-word rule requires a new term to be added to the glossary in the same change. · Minor for the page, Moderate for the glossary · Add "decoy" to `docs/GLOSSARY.md`, or update the "distractor" entry per ADR-0006, in the same PR as the page. · Verified: yes.

10. **Budgets bullet and Terms "no-coordination recording"** · The glossary term is "no-coordination test" (a recording "one per seed at each background"). The page's "recording" wording is close but not the reserved form. · Minor · Use "no-coordination test", or "the no-coordination test's recording". · Verified: yes.

11. **Budgets bullet: "The limits are per detector"** · Precision-swing limits for one detector differ by stream: rate+context has 0.100 on fast and 0.150 on combined (Tables 3 and 5), and count (sliding) has 0.1 and 0.15 in 064/count. So the limits are set per detector and stream. 064/count also says "all three budgets" where the page lists four; the page does not reconcile the two. · Minor · Say "per detector and stream", and note that 064/count's three budgets count the elevated-rate stretch as one. · Verified: yes.

12. **Bench order: Table 1 lists new then old, Table 2 old then new, Tables 3–5 new columns first** · The same categorical pair is ordered differently from table to table. · Minor · Order Table 2 new, old like the others. Or, if old → new is the narrative order, use it everywhere. · Verified: yes.

13. **Row labels: Figure 1 vs Tables 1 and 3–5 vs Section 2** · One row gets different names in different places: "pick, run 5 of 5" / "pick: training run 5 of 5"; "starting point" / "starting point (untuned)"; "no pick, run 5 of 5" / "no pick; best was training run 5 of 5". · Minor · Use one label form, or state the short form in the Figure 1a caption. · Verified: yes.

14. **Figure 4 caption, "[t] away"** · Raw seconds, where every other time on the page is written minutes-friendly (e.g. [t]). This breaks the house time convention. · Minor · Write it in minutes and seconds. · Verified: yes.

15. **Section 3 thumbnails (8 `<figure>` elements)** · These are figures with no numbers; every other figure on the page is numbered, and the house rule is to number every figure. · Minor · Caption the grid "Figure 11. …", or make it a numbered table of links. · Verified: yes.

16. **Table 3 row 17 (count (binned) · starting point, new bench ΔF1 "+0.000")** · The mean in `briefing.json` is −0.0005, and 064/count prints it as −0.000. The page's sign disagrees with the source. · Minor · Keep the sign of negative values that round to zero ("−0.000"). · Verified: yes.

17. **Headline first paragraph: "Each row … is a detector at one setting, or a learned model's picked training run"** · Slow chorus_gain_norm_part is a "no pick" comparator, so the definition does not cover every row. Figure 1b and Table 4 handle it correctly. · Minor · Add "(or, where no run met the budget, its best run, shown as a comparator)". · Verified: yes.

The run-notes contradiction behind finding 1 (064 records a fast SPIKE-synch proposal, 065 says there was none) is between the companions themselves; it matters here because the page sides with 065 without saying so. I cannot check the "four detectors that take the participation floor" in Section 2 and Terms: none of the documents names them, and the page could list them.

Files:
- `<darkroom>/bugarach/2026-09-26-full-panel/briefing/index.html`
- `<darkroom>/bugarach/2026-09-26-full-panel/briefing/briefing.json`
- `<darkroom>/bugarach/2026-09-26-full-panel/065/README.md`
- `<darkroom>/bugarach/2026-09-26-full-panel/065/RUN_C.md`
- `<darkroom>/bugarach/2026-09-26-full-panel/064/README.md`
- `<darkroom>/bugarach/2026-09-26-full-panel/064/count/README.md`
- `<repo>\docs\GLOSSARY.md`
- `<repo>\docs\adr\0006-a-false-alarm-is-coincidence-the-event-rates-explain.md`
