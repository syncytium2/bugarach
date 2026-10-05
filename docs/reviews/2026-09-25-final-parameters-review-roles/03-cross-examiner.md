GRANT 3 ok — Read, Grep, Glob

# Role 3 — Cross-Examiner

**Artifact:** <worktree>\docs\learned\runs\2026-09-25-final-parameters\README.md

**What I checked:**
- The headline counts (4 adoptable; 10 held back, split 5 / 4 / 1; 4 shipped points out of budget; 6 items for Tony) against the table and against `adoption.json`. All agree.
- `adoption.json` numbers spot-checked against the darkroom `065/phase3/candidates.json` (slow SPIKE-synch, slow locust, combined rate+context): exact agreement.
- All four figures against the table and the prose.
- Category order across figures: fast → slow → combined for streams, and one consistent detector order. The glossary does not rule on either, so I checked only that the figures agree with each other; they do.
- Cross-links and companion docs: the goal page, the runbook, the handoffs README row, ADR-0008, ADR-0009, the GLOSSARY, and the bench-floor todo (which records the re-measure; not in your list).

**What holds:**
- Figure 2's diagonal matches the table's fresh F1 in every cell, and Figure 1's markers match the adoptable column.
- Figure 4 (right) matches item 6: 25/40, 20/40, 15/40.
- Item 1's locust gains match the table.
- The crowded losses match `adoption.json` (0.044 for fast CoactDetect, 0.0207 for slow binned SCE), as does slow chorus_norm's 1.43 calls/min.
- The 38 versions and 114 cells match `cross_stream` (54 shipped, 42 proposal and 18 chorus cells).
- Citations of ADR-0009 decisions 1, 4 and 5 are correct.
- The goal-page summary does not contradict the report.
- There is no "fire" and no "data is"; no groups appear, so group order does not apply.

## Findings (location · issue · severity · suggested fix · verified)

1. **README L55–56 vs item 6 (L179–185) and Figure 4 — one population counted on two bases.** The table's under-floor column counts 24 fresh seeds on the quiet background only (120 events per level). Item 6 and Figure 4 count 8 probe seeds on both backgrounds (40 per level). The busy shares differ: fast middle level 85/120 (71%) vs 25/40 (62.5%); combined middle level 55/120 (46%) vs 20/40 (50%); slow lowest level 50/120 (42%) vs 15/40 (38%). Item 6 never states its basis, and the fresh-seed busy counts are in `adoption.json` but not in the table, so a reader checking "25 of 40" against a table that says "120 per level" cannot reconcile them. **Medium.** Fix: pick a basis — either state in item 6 that its numbers come from the 8-seed probe (Figure 4), or quote the fresh-seed counts and add the busy background to the table column. **Verified: yes** (`adoption.json` `under_floor.baseline_busy`; Figure 4 image).

2. **Item 2 table, L157 (slow locust) — "Measured on" understates the failure.** It says "selection seeds" only, but `adoption.json` shows the shipped probe failing on all three seed sets: selection 7.24, held-out 6.85, fresh 7.23, against 4.0 calls/min. **Medium.** Fix: "selection, held-out and fresh seeds", and add 6.85 and 7.23. **Verified: yes** (adoption.json L3181–3240).

3. **Item 2 table, L158 (combined rate+context) — the fresh-seed failure is omitted.** The row gives 0.245 on selection only, but the fresh-seed precision swing also fails (0.257 against 0.15). The two fast rows list both seed sets, so this row is inconsistent with them. **Medium.** Fix: "0.245 (selection), 0.257 (fresh)" and "selection and fresh seeds". **Verified: yes** (adoption.json L4461–4520).

4. **Adoption table and Figure 3 use terms the glossary has retired.** Cells "fail: crowded" and "fail: probe", and item 2's "probe (calls per minute…)", use names the GLOSSARY renamed on 2026-09-21 (*crowded* → **close-events test**, *probe* → **elevated-rate test**). The report's own prose says "close-events recordings", so the table and the prose disagree. L45 "no-coordination (empty) recording": the glossary says in terms *Not "empty"*. **Medium.** Fix: "fail: close-events" and "fail: elevated-rate (inside the stretch)", and drop "(empty)". The labels are written by `tools/make_final_parameters_report.py`, so fix the generator. **Verified: yes** (GLOSSARY L366–372, 420–425, 431–439).

5. **GLOSSARY — new terms and a changed definition not updated in the same change.**
   - The "elevated-rate test" entry still describes a 5-minute stretch in *every bench recording* (20:00–25:00); ADR-0009 decision 1 moved it into its own "elevated-rate recording", which is the term the report uses.
   - "Floor" is a reserved word with two existing meanings (**floor, provisional floor *f*** — a within-ROI interval; **participant floor** — a recruitment level). The report uses bare "floor" throughout for a third concept, ADR-0008's per-window chance floor, which has no glossary entry.
   - Other new terms missing: "don't care", "bracketed (strict / if a limit counts)", "extension cap", "fresh seeds", "precision swing", and the proposal names "rounds" / "pair" ("the pair grid" in item 4).

   **Medium.** Fix: add the entries — at least "event floor (ADR-0008)" and the revised elevated-rate entry — in the same PR. **Verified: yes** (GLOSSARY L366–371, 451–452, 476–479).

6. **Figure 1 vs Figure 3 — the same marks mean different things.** In Figure 1 a diamond is a proposal and blue/orange mean adoptable/not adoptable. In Figure 3 a triangle is a proposal and blue/orange mean CoactDetect/rate+context. Figure 3's filled/open means quiet/busy, while Figure 1's open circle means the shipped point. Figure 3 also labels the detector "SCE" where the table and Figure 1 say "binned SCE". **Low–medium.** Fix: one proposal shape across both figures; don't reuse blue/orange with a second meaning; label "binned SCE" in Figure 3. **Verified: yes** (both images).

7. **Table column "fresh F1 as scored / without decoys" (L61 ff.) is ambiguous.** In rows with a proposal it shows "shipped → proposal / X", where X is the proposal's value only; the shipped without-decoys F1 is omitted. For fast CoactDetect this hides a drop (0.981 shipped → 0.956 proposed) while as-scored F1 rises (0.769 → 0.809). **Low–medium.** Fix: show both ("0.769 → 0.809 / 0.981 → 0.956"), or label the header "(proposal)". **Verified: yes** (adoption.json L15–18, 179–181).

8. **Figure 2 caption, L108–109 vs the figure.** The caption says "all 114 cells ran", but the figure shows 72 cells (8 detectors × 3 × 3); the 114 include shipped variants the figure does not draw, as the caption's own previous bullet explains. **Low.** Fix: "114 cells were scored (every shipped point, proposal and chorus pick); the figure shows the 72 for the chosen version". **Verified: yes** (count of `"variant"` in adoption.json = 114, of which 54 are shipped).

9. **Held-out budget claims, L19 and L147 (and goal page L48–49).** "Passes every budget on selection, held-out and fresh seeds" and "Each passes every budget" contradict the report's own statement (L50–51) that the held-out precision swing is "not recorded, never as passed". **Low.** Fix: add "(held-out precision swing not recorded)", or say "passes every recorded budget". **Verified: yes.**

10. **Goal page L167 vs report item 6.** The goal page says "most of the lowest planted level under the floor"; the report says the lowest level is *entirely* under (120/120 and 40/40 on both backgrounds), plus part of the middle level on busy. **Low.** Fix: "all of the lowest planted level, and part of the middle level on busy recordings". **Verified: yes.**

11. **Runbook `docs/handoffs/2026-09-25-overnight-final-parameters.md` L4–13, now that it has moved.** L5 still says "It is at the repo root because the work is in flight". Its links are written relative to the repo root (`docs/FOUNDATIONS.md`, `docs/adr/0008-…`, `docs/handoffs/README.md`, `docs/goals/…`), so from `docs/handoffs/` they resolve to `docs/handoffs/docs/…` and are dead. The handoffs README row says the file is "kept as written" for two named errors, and this is neither. **Low.** Fix: add a retirement header (as other retired handoffs have) noting the move, and relativize the links or note they are root-relative. **Verified: yes** (by path reasoning; the link test was not run).

12. **Item 2, L157 — slow locust busy value 3.69 calls/min.** It is not in `adoption.json`, which records one probe value per seed set (7.24, 7.24166… selection). Figure 3's fresh elevated-rate recording (seeds 66000–66011) puts the slow locust shipped busy marker at or just above the 4.0 bar. That is a different seed set, so there is no strict conflict, but a reader comparing item and figure sees "busy passes" against "busy at the limit". **Low.** Fix: cite the source of 3.69, or add the fresh-seed busy value alongside. **Verified: no** (3.69 not found in the report's inputs).

13. **Table percentages vs item 6 ROI counts.** The table labels levels by fraction (10/20/30%; 13/25/40%); item 6 and Figure 4 by participants (3/6/10; 4/8/13). The report never states that a bench recording has 32 ROIs, and never gives the mapping (it is recorded only in the todo). **Low.** Fix: label table levels "10% (3 ROIs)" etc., or state the 32-ROI bench once. **Verified: yes** (bench-floor todo L34; Figure 4 axis).

14. **Item 4, L173 — "ADR-0009 decision 5 set 120 s as the longest context and no shortest one."** Decision 5 names the grid (20, 30, 45, 60, 90, 120 s) and says only that "the shorter values let a search find a short context"; whether extending below 20 s was licensed is an interpretation the ADR does not state. **Low.** Fix: "ADR-0009 decision 5 caps context at 120 s and lists 20 s as the grid's shortest value without forbidding shorter". **Verified: yes** (ADR-0009 L71–75).

## Files
- <worktree>\docs\learned\runs\2026-09-25-final-parameters\README.md
- <worktree>\docs\learned\runs\2026-09-25-final-parameters\adoption.json
- <worktree>\docs\goals\coded-detector-optimization.md
- <worktree>\docs\handoffs\2026-09-25-overnight-final-parameters.md
- <worktree>\docs\GLOSSARY.md
- <worktree>\docs\todo\2026-09-24-the-bench-floor-and-the-elevated-rate-stretch.md
- <darkroom>\bugarach\2026-09-25-final-parameters\065\phase3\candidates.json
