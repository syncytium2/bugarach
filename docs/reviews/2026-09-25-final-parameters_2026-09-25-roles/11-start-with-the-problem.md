GRANT 11 ok — Read, Grep, Glob (also holds SubagentHandback, the hand-off channel only; no Edit, Write or NotebookEdit)

# Role 11 — Argument order ("Start With the Problem")

**Artifact reviewed:** <worktree>\docs\learned\runs\2026-09-25-final-parameters\README.md (221 lines).
**Contract checked against:** <worktree>\docs\handoffs\2026-09-25-overnight-final-parameters.md, Phase 4 (lines 124–144).

## The spine (one claim per section, in the report's order)

0. **Title + preamble (1–7):** Nothing is adopted; no bench operating point changed; the night followed the runbook, ADR-0008 and ADR-0009.
1. **Floor paragraph (9–13):** Every run used a per-window floor from each recording's own null; a planted event below it leaves recall, a call on it leaves precision.
2. **In one paragraph (15–30):** Four proposals are adoptable under the strict rule; ten more gain but are held back (five only by a hard limit, four by cap/edge, one by close-events loss); four *shipped* points are out of budget; six questions are "listed at the end".
3. **The adoption table (32–87):** A 25-line key, then 26 rows × 10 columns of per-row evidence for every detector × stream.
4. **Figures (89–131):** A gallery of four captioned figures (fresh-seed F1 shipped vs proposed; the 3 × 3 cross-stream; the elevated-rate recording; the re-measured bench floors) — descriptions, no claims.
5. **What waits on Tony (133–192):** Six rulings — Q1 hard-limit-counts-as-bracket (decides 5 proposals); Q2 four shipped points fail budgets; Q3 CoactDetect alpha runs to the cap; Q4 fast LoCo context below the grid; Q5 guard cap removes 8 s guards; Q6 much of the bench sits under the floor on fast/combined, so recall is measured only on events chance does not reach. Then two smaller items.
6. **Real data (194–198):** The 66-recording run belongs to WSMIP065 and is descriptive only — a pointer, no claim.
7. **What ran (200–220):** Provenance: phases, machines, commits, record paths.

## The arc I judged it against

Not the default analysis arc (problem → cost → method → what it gets wrong → fix → evidence → residual risk). The reader commissioned the night and must act this morning, so I used a **decision-memo arc**: *the ask (what you must decide) → the answer (what we propose) → the rulings that change the answer, each with its evidence adjacent → caveats that change how to read all the evidence → the full evidence table and figures → provenance.*

The report does not state which arc it follows. Its title ("what is adoptable, and what waits on Tony") promises the decision-memo arc; its body follows the order the night was run (definitions → results table → figures → questions → provenance).

**Cold open:** the reader first sees title → "Nothing here is adopted" → two governance links → a floor-definition paragraph. The status line is a fair opening; the definition paragraph sits between the reader and the bottom line. The one-paragraph summary (15–30) is good but ends by deferring the decisions to "the end".

**Does the order serve a reader who must decide?** Partly. The bottom line is near the top, but the rulings that determine what the table *means* sit after 55 lines of table and four figures, and the primary decision (adopt the four?) never appears as a decision at all.

## Findings

| # | Location | Issue | Severity | Suggested fix | Verified |
|---|---|---|---|---|---|
| 1 | "What waits on Tony" (133–192); pointer at 29–30 ("listed at the end") | The rulings Tony must make come after the table and all four figures. Q1 (hard-limit bracketing) decides whether 4 or 9 proposals are adoptable — i.e. it decides the table's key column — yet the table's own key says "Which rule applies is Tony's decision" (line 54) and the ruling is 80 lines later. The reader reads the entire table under one rule, then learns it may not be the rule. | High | Move "What waits on Tony" to directly after "In one paragraph", before the table. Keep table and figures as the evidence the questions cite. | yes |
| 2 | "What waits on Tony" as a whole; runbook line 144 ("What waits on Tony: only the adoptions, and anything a stop rule below raised") | The primary decision — whether to adopt the four strict-adoptable proposals (fast binned SCE; combined binned SCE, rate+context, SPIKE-synch) — has no slot in the decision section. The six questions are all stop-rule/definition items; the adoptions themselves appear only as a summary sentence and a bold "yes" in a table cell. The ask the whole page exists for is missing from the spine. | High | Make item 0 of the decision section "Adopt these four?" with each gain and interval inline, then the rulings that would add candidates (Q1 first). | yes (runbook line 144 vs report 133–192) |
| 3 | Q6 (179–185) | Q6 is a reading caveat for every row: on fast and combined the lowest planted level is entirely under the floor, and part of the middle level on busy, so recall — and therefore every F1 and gain in the table — is measured only on the surviving events. It is placed last of six, after the reader has already absorbed the table's numbers. | Medium | Put it as a caveat before the table (next to the floor paragraph, as "what the floor does to the bench"), or make it the first ruling after the adoptions, with Figure 4 adjacent. | yes |
| 4 | Figures section (89–131) | The figures are a gallery with no job in the argument. Figure 1 is cited nowhere; Figures 2 (3 × 3) and 3 (elevated-rate recording) are cited by no claim or question; only Figure 4 is cited (by Q6, 48 lines after it appears). Figure 1 is the picture of the main claim but follows a 26-row table. Each figure arrives after the claim it could support, or supports no claim. | Medium | Place each figure next to its claim: Figure 1 immediately after the summary (or item 0); Figure 3 with Q2 (slow locust probe failure); Figure 4 with Q6. For Figure 2, state what decision it informs (e.g. whether a tuned version can be reused across streams); if none, move it to an appendix beside "What ran". | yes (grep: only "Figure 4" referenced outside captions) |
| 5 | Floor paragraph (9–13) | A definition opens the page ahead of the bottom line; the reader holds a definition before knowing why it matters. | Low | Move below "In one paragraph", or fold into the table key next to the "under the floor" column that uses it. | yes |
| 6 | Order within the six questions (137–185) | Q1, Q3, Q4 and Q5 are all bracketing/grid-limit questions (why proposals are held back); Q2 (shipped points out of budget) interrupts them. Q2 is a different kind of item — the settings in use now fail budgets, arguably the motivating problem and more urgent than any search-grid technicality. | Low | Group: (a) adoptions; (b) shipped points failing budget (Q2); (c) bracketing rulings (Q1, Q3, Q4, Q5) with Q1 first; (d) bench validity (Q6), unless moved up per #3. | yes |
| 7 | "In one paragraph" (20–26) | Each held-back reason maps to a numbered question, but the summary does not name them, so the reader cannot jump from "held back because an axis is at a limit" to the ruling that would release it. | Low | Add "(Q1)", "(Q3–Q5)", "(Q2)" after each category, or anchor links once the questions move up. | yes |
| 8 | "Real data" (194–198) | A section with no claim and no result: a pointer to another session's output, placed between the decisions and provenance, and silent on whether that run finished. No job in the spine. | Low | Fold into "What ran" as one row or bullet; if the real-data run should inform a decision, say which and move it next to that decision. | yes |
| 9 | Whole page | Unstated deviation from the default arc, and no stated motivation: that the shipped points were tuned pre-floor and four of them fail budgets under it appears only as the last sentence of the summary and as Q2. Minor for this reader (who commissioned the night); not minor for anyone reading the run record later from the goal page. | Low | One sentence before the summary: why the night ran and what decision the page asks for. | yes |

## Proposed order

1. Title + status line.
2. The ask + bottom line (four adoptable; what each ruling would change), with Figure 1.
3. Decisions: adopt the four → Q2 (with Figure 3) → Q1, then Q3–Q5 → Q6 (with Figure 4), or Q6 promoted as the pre-table caveat.
4. Floor definition + table key.
5. Adoption table.
6. Figure 2, with its claim stated.
7. Smaller items.
8. What ran (with the real-data pointer folded in).

**Out of my scope and not checked:** whether the numbers are right, whether each figure is readable on its own, and the rendered figure files.
