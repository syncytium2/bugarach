GRANT 5 ok — Read, Grep, Glob (also holds SubagentHandback, the report channel, not an editing tool; no Edit, Write or NotebookEdit)

**Role 5 — Line editor ("Kill Your Darlings")**
Artifact: `docs/learned/runs/2026-09-25-final-parameters/README.md` (floor-and-grids worktree, 444 lines).

**Tool receipt: `murderboard_prose.sh` is not vendored in this repo, so there is no tool receipt.** Record this as "tool not run", not as a clean result. The construction search was done by Grep plus a full read.

**List run:** the house list from the role-5 checklist — not just X but Y · it's not about A, it's about B · it's worth noting · delve / leverage / robust / seamless / crucial / landscape / tapestry · a three-item list built for rhythm · an em-dash pivot into an uplifting close · an "In today's ___" opener. Repo conventions added: "data" singular; fire/firing; British spellings; "modality"; undefined labels (PR A/B, WSMIP06x, OVX/ORX, senktide).

**Construction search results (line · construction · kind):**
- House list: no hits. No banned words, no em-dash pivots. Two three-item lists — "Read these three things" (28) and "Three methods caveats" (235) — are real triples, not rhythm.
- 136 · "labelled" · British spelling (→ "labeled")
- 391 · "analysed" · British spelling (→ "analyzed")
- 408 · "labelled" · British spelling
- 45 · "PR A's choice" · label used before definition; first explained only in the What ran table (423), and there as a label, not a name
- 347, 359 · "supplied by WSMIP065" · machine label used as a name, never defined
- 382–383 · OVX, ORX, senktide · undefined abbreviations
- 411 · *pair* · defined but not used in the body, which says "two-setting grid" (147)
- No hits for "data" grammar, "fire" or "modality".

Block word counts below are by-eye estimates, not tool output.

## Findings (location · issue · severity · suggested fix · verified)

1. **Lines 37–39 · "Combined rate+context's [intervals] barely touch."** The table contradicts this: shipped [0.642, 0.726] and proposal [0.748, 0.793] are separated by a 0.022 gap. Fast binned SCE — presented as the clean case — has a smaller gap (0.765 vs 0.769, 0.004). The sentence ranks the two backwards. · **blocking** (this is the decision-1 evidence) · "On fresh seeds, the shipped and proposal intervals do not overlap for fast binned SCE or combined rate+context; they overlap for combined binned SCE and combined SPIKE-synch." · verified yes (table L23–26).

2. **Lines 30–41 · payload buried.** The sentence that should drive decision 1 — only the fresh seeds are an independent check, and on them two of the four proposals separate — comes fourth; the bullet opens with how selection worked. · major · Lead with the fresh-seed result, then one sentence: "The held-out seeds chose among candidates, so the held-out gain is biased upward." Keep the 0.0003 example as evidence. · verified yes.

3. **Lines 42–47 · payload buried.** One of the four adoptable proposals goes over a limit (combined rate+context, 1.28/h outside the stretch on busy against 1), and this comes last, after three sentences about what was not checked. · major (it bears on adopting that row) · Open the bullet with that sentence, and replace "(PR A's choice)" with what PR A is, e.g. "the bench PR, #809". · verified yes.

4. **Lines 48–50 · a bullet that asks nothing.** It ends "no verdict here depends on that", under "Read these before deciding", giving nothing to act on. · minor · Cut it, or shrink it to a clause inside the budgets bullet. · verified yes.

5. **Line 6 · "seven rulings" undercounts.** Smaller items (216) also asks for a decision ("the call is Tony's"), which makes eight. Also, "(decision 3)" is lowercase while every heading says "Decision 3". · minor · Say "seven rulings and one smaller call", or make slow binned SCE Decision 9; capitalize "Decision 3". · verified yes.

6. **Line 216 · "the call is Tony's".** In this document "call" means a detector's output, so the word is ambiguous here. · minor · "the decision is Tony's". · verified yes.

7. **Line 90 heading · "Four shipped points are out of budget, and the floor may be why".** The floor explanation (107–112) covers only the three precision-swing failures; slow locust's elevated-rate failure is never explained. The heading asserts more than the section does. · major · "…and for three of them the floor may be why", plus one line on slow locust (or "unexplained"). · verified yes.

8. **Lines 114–117 · option 1 restates a measurement.** "Are these four shipped points out of budget?" — they measurably are. · minor · "Treat these four as failing, or re-measure the precision-swing budget under the floor (a new ruling, not a loosened limit)?" · verified yes.

9. **Lines 169–187 · the Decision 7 table duplicates Table 3.** Same counts and floors, typed a second time: Table 3 is generator-written, this one hand-written, so one number now lives in two places. · major (drift risk) · Keep the two-line lead-in, point to "Table 3, planted events under the floor", and delete the hand table. · verified yes (L175–179 match L328–333).

10. **Lines 182–183 · the Figure 4 numbers cannot be placed.** "25 of 40, 20 of 40 and 15 of 40 for the last three rows" is positional. The last three rows are combined quiet, combined busy and slow busy, and combined quiet has no nonzero middle level, so the reader cannot map each number to a cell. · major · Name each one, e.g. "combined busy, middle level: 20 of 40". · verified yes (the mismatch is visible in the text; the figure was not checked).

11. **Line 184 · "So recall … counts only events above the floor".** True by definition, so it does not follow from the table. What does follow is that the lowest planted level no longer contributes to recall on fast and combined. · minor · "So on fast and combined, the lowest level contributes nothing to recall, as ADR-0009 anticipated." · verified yes.

12. **Lines 203–204 · the reading instruction contradicts the table.** "Compare down a column, not across a row" is copied from the Figure 2 caption, but in the Decision 8 table the comparison is across a row (score vs the stream's own version's score). · major · Delete the bullet here; keep it only in the Figure 2 caption. · verified yes.

13. **Line 201 · the lead-in promises intervals a row lacks.** It says "fresh seeds, 95% intervals", but the CoactDetect row has none. · minor · Add intervals from `adoption.json` `cross_stream`, or mark the row "(point only)". · verified yes.

14. **Lines 149–151 · a bullet in the wrong decision, with no consequence stated.** The fast-LoCo `threshold_pctile` "cap" point is about bracketing (Decision 2), not context length. "(94 to 1)" does not say whether these are percentiles or counts. The consequence is never stated: the proposal sits at an unextended upper end, so "cap" hides an unextended edge. Lines 231–233 repeat the point. · major · Move it once, to Decision 2 or the table notes, and write: "all six extensions lowered the bottom of the grid, from 94 down to 1 percentile; the proposal sits at the top, 99.99, which was never extended, so its 'cap' label hides an unextended edge". · verified yes (Table 1 L251).

15. **Lines 131–136 · ~70 words to correct Table 2 for a proposal that stays blocked anyway (`alpha` cap).** · minor · Move it to a single note under Table 2; keep one clause in Decision 4. · verified yes.

16. **Lines 225–230 · two table-note bullets repeat one fact** (fast CoactDetect/LoCo shipped is sliding on selection and held-out, binned on fresh). · minor · Merge them into one bullet. · verified yes.

17. **Lines 235–236 · throat-clearing, and misplaced.** "…stated here because they affect how far the numbers transfer" is preamble, and the three caveats are about methods, not about reading tables. · minor · Cut the "stated here because" clause; consider moving the three caveats under Definitions → Event floor. · verified yes.

18. **Lines 67, 28 · preview sentences.** "Each item ends with the decision it asks for" is a preview; the bold **Decide:** already shows it. "Read these three things before deciding:" is borderline and can stay. · minor · Cut the first sentence at L67; keep the ordering reason. · verified yes.

19. **Line 157 · "(not an ADR)" is cryptic.** · minor · "a runbook rule that no ADR records, so it is yours to keep or drop". · verified yes.

20. **Lines 44, 352–353 · "gated" is undefined jargon.** · minor · "held to a limit" / "checked against the limit". · verified yes.

21. **Lines 347, 359, 424–431 · WSMIP064/065 are machine labels used as names and never defined** (CLAUDE.md: "Name things; don't index them"). · minor · Define once in Definitions ("WSMIP064/065 — the two lab workstations that ran the night"), or drop them from captions. · verified yes.

22. **Lines 380–384 · the Real data section omits three things:**
    - OVX, ORX and senktide are undefined.
    - It does not say why only OVX and ORX are reported; a reader will ask about DI and MALE.
    - It has no ask and no one-line takeaway. Its payload would be: the floor choice flips the call in 498 of 3,072 cells (~16%).

    · major (FOUNDATIONS §8 means outside readers) · Define the abbreviations; either say why only those two groups are shown, or list all four in house order DI, OVX, MALE, ORX; lead with the 498 figure. · verified yes (arithmetic checks: 128 × 3 × 8 = 3,072).

23. **Lines 390–391 · the Definitions entry's punctuation breaks it.** "…**ROI** (…), **stream**. The event trace analysed…" reads as if the second sentence defines all three terms. · minor · One bullet each for SCE, ROI and stream; "analysed" → "analyzed". · verified yes.

24. **Lines 399–401 · a sentence with too many "and"s.** "Fresh seeds 6000–6023, and 56000–56011 and 66000–66011 for the no-coordination and elevated-rate recordings, are what nothing chose on." · minor · "Nothing chose on the fresh seeds: 6000–6023 for the bench, 56000–56011 for the no-coordination recording, 66000–66011 for the elevated-rate recording." · verified yes.

25. **Line 411 · a term defined but not used.** *pair* is defined, but the body says "two-setting grid", and *rounds* appears only as "first-round". · minor · Pick one term and use it in both places. · verified yes.

26. **Line 56 · "the chorus fit each training run picked" is ambiguous** (one diamond per run, or the single fit the training rule picked? Table 1 means the latter). · minor · "the fit chorus's training rule picked". · verified yes.

## Passage tests (block · ~words · the sentence it exists to deliver · what the rest buys)

- **Intro L3–13 (~110):** "Nothing is adopted; the night re-tuned every detector under the new floor, and this page asks for one adoption and seven rulings." Payload first: yes. The links are needed evidence; keep them.
- **Decision 1 lead L17–19 (~45):** "Four proposals meet the strict rule." Keep. It slightly overstates, which L30–47 correct (F2, F3).
- **Decision 1 caveats L30–50 (~290):** "On the fresh seeds, which nothing chose on, fast binned SCE and combined rate+context separate from their shipped points, the other two overlap, and combined rate+context breaks the outside-stretch limit on busy." Split, and partly wrong (F1). The bias explanation is sceptic-demanded evidence and stays, shorter. The "open warning" bullet buys nothing and can go. Promoting the payload is the main fix.
- **Decision 2 L72–86 (~120 incl. table):** "Five more proposals would be adoptable if a hard limit counted as a bracket, making nine." At the end; promote it to the lead line. The fast-locust note is real evidence.
- **Decision 3 L92–117 (~200):** "Three of the four out-of-budget shipped points fail the precision swing, which the per-recording floor may cause by treating the backgrounds differently." In the middle. The darkroom-diagnosis sub-bullet buys provenance. Fold "No limit was loosened" into the Decide.
- **Decision 4 L121–139 (~170):** "The search lowered `alpha` to the extension cap, ~1e-9, still gaining F1, so neither proposal is bracketed." Payload first: yes. The close-events correction (~70 words) belongs with Table 2 (F15).
- **Decision 5 L143–153 (~130):** "ADR-0009 does not say whether a context may go below 20 s, and the search went to 5 s." Payload first: yes. The LoCo "cap" bullet is off-topic here (F14).
- **Decision 6 L157–165 (~90):** "The quarter-of-context guard cap never reached LoCo until this PR; no proposal is affected." Clean.
- **Decision 7 L169–190 (~200 incl. table):** "On fast and combined the lowest planted level is entirely under the floor, so it no longer counts toward recall." Payload first: yes. The table duplicates Table 3 (F9). The self-defining-null sentence earns its place and flags itself as read off the figure.
- **Decision 8 L194–207 (~110):** "A combined-tuned version beats the stream's own version on fast and on slow." Payload first: yes. The column-reading bullet is wrong for this table (F12).
- **Smaller items L211–218 (~110):** "Slow binned SCE sits at the close-events allowance within noise; the decision is Tony's." The noise evidence is sceptic-demanded; keep it. The chorus bullet needs an ask, or a "for information" label.
- **How to read L222–243 (~300):** No payload; reference material. It carries two repeats (F14, F16) and a misplaced caveat block (F17), and could lose about a third.
- **Figure captions 1–4:** Fine as bullets. Figure 2's caption is where "compare down a column" belongs.
- **Real data L370–384 (~150):** "On real data, the floor choice flips the call in 498 of 3,072 cells; descriptive only." Second to last; promote it (F22).
- **What ran L420–443:** A provenance table; it is evidence, so no cuts. It is the only place PR A and PR B are labeled.

**Totals:** 1 blocking (F1), 9 major, 16 minor. Every finding was verified by reading the artifact and its own tables; no figures, darkroom files or ADRs were opened.
