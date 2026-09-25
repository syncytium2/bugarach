GRANT 11 ok — Read, Grep, Glob

Role 11 — Start With the Problem (argument order). Artifact: `docs/learned/runs/2026-09-25-final-parameters/README.md` (floor-and-grids worktree). Contract checked against the Phase 4 section of `docs/handoffs/2026-09-25-overnight-final-parameters.md` (L126–146). No file edited.

## Spine (one claim per section, in page order)

0. **Opening (L1–13):** Nothing is adopted. Every shipped setting predates the event floor, and four now fail a budget. Tony is asked for one adoption decision and seven rulings.
1. **Decision 1 (L15–63):** Four proposals pass the strict rule and are up for adoption. Three caveats: held-out seeds also chose, so only fresh seeds are independent; the budget checks have gaps (combined rate+context makes 1.28/h on busy against a limit of 1); combined's own budgets carry an open warning. Then the Decide line, then Figure 1.
2. **Preamble (L65–68):** Decisions 2 and 3 come first among the rulings because they change the number of proposals or what the shipped points are worth.
3. **Decision 2 (L70–88):** Five more proposals are held back only by a hard limit; if a limit counts, 9 are adoptable instead of 4.
4. **Decision 3 (L90–117):** Four shipped points are out of budget, and the precision-swing failures may come from the floor itself, since the floor varies by background and sets aside planted events (cites Table 3).
5. **Decision 4 (L119–139):** CoactDetect's alpha ran to the extension cap (~1e-9); should the grid stop at a stated floor?
6. **Decision 5 (L141–153):** Can a context be shorter than 20 s?
7. **Decision 6 (L155–165):** Keep the quarter-of-context guard cap? (A bug in it was fixed; no result changes.)
8. **Decision 7 (L167–190):** Much of the planted bench sits under the floor, so recall on fast and combined counts only events above it; change the bench levels?
9. **Decision 8 (L192–207):** Combined-tuned versions beat some streams' own versions; does per-stream tuning hold?
10. **Smaller items (L209–218):** Slow binned SCE misses the close-events allowance by noise ("the call is Tony's"); slow chorus_norm is over CoactDetect's limit.
11. **Full tables (L220–366):** Reading key, three methods caveats, Tables 1–3, Figures 2–4.
12. **Real data (L368–384):** The own and baseline floors disagree in 2,696 of 3,072 cells, and 498 calls flip; descriptive only, run on unmerged PR #814.
13. **Definitions (L386–416).**
14. **What ran (L418–443):** Provenance.

## Arc used

The default analysis arc (problem → cost → method → what it gets wrong → fix → evidence → residual risk) does not fit a morning decision page, so I judged it as a **decision memo**: problem and ask → the rulings that change the decision set → the decisions → evidence adjacent to each → residual risks bearing on the decisions → appendix (tables, definitions, provenance).

The page mostly follows this. The deviation is that the adoption decision comes before the rulings that scope it. The page half-admits this: the heading "The rulings the adoption depends on" is there, but it never says Decision 1 is conditional on them.

## Cold open

The reader first sees "Nothing here is adopted", then the problem in sentences 2–3 (the shipped settings predate the floor; four fail a budget). That is the problem, so it passes. One weakness: the problem is given only by reference ("(decision 3)"), and its cause — the floor — is not explained until Decisions 3 and 7.

## Findings

| # | location | issue | severity | suggested fix | verified |
|---|---|---|---|---|---|
| 1 | Decision 1 (L15–52) vs L67–68 | Tony is asked to "adopt all four, some, or none" before the rulings that the page itself says change the count (Decision 2: four becomes nine) and the worth of the baselines (Decision 3). The page asks for a decision whose scope is settled below it. | major | Either move Decisions 2 and 3 ahead of Decision 1, or keep adoption first but reword its Decide line as "under the strict rule" and add one line naming which later rulings would change the set (Decision 2 changes the count; Decisions 3 and 7 change what the baselines and F1 mean). | yes |
| 2 | Decision 7 (L167–190), Decision 3 (L107–112) | The root mechanism — the floor removes planted events, and does so differently per background — is presented eighth. Decision 3's argument already relies on it (it cites Table 3), and it changes what every F1 in Decision 1 measures, so Decision 3 depends on material far below it. | major | Put Decision 7 directly before Decision 3 (or before Decision 1), or merge them into one "the floor changes the bench" section. | yes |
| 3 | "Smaller items", slow binned SCE bullet (L211–216) | A real adoption decision is filed under "smaller": the proposal misses the 0.02 allowance by 0.0007 and "the call is Tony's", yet the opening count ("one adoption decision and seven rulings") omits it. | major | Move it next to Decision 2 as another proposal "held back only by…", and include it in the opening count. | yes |
| 4 | Figures 2, 3, 4 (L336–366) | Each is the evidence for a decision higher up (Figure 2 → Decision 8; Figure 3 → Decision 1's busy-background caveat; Figure 4 → Decision 7), but they sit in the appendix 100–200 lines below the question they support, so Tony cannot judge those decisions where they are asked. | major | Move each figure into the section of the decision it supports; leave only Tables 1–3 in "The full tables". | yes |
| 5 | Reading key, "Three methods caveats" (L235–243) | These are residual risks for adoptable proposals (e.g. the floor is counted in a 2 s window while binned SCE uses 2–10 s bins, and fast binned SCE's proposal changes its bin width 10 → 2 s), but they are buried in the table key, after every Decide line. | major | Move them into Decision 1's "Read these three things", or a short residual-risk section before the tables. | yes |
| 6 | Decision 1, Figure 1 placement (L52 vs L54–63) | The Decide line comes before Figure 1, the section's main evidence; the ask should close the section. | minor | Put Figure 1 directly after the adoption table and end the section with the Decide line. | yes |
| 7 | Heading "The rulings the adoption depends on" (L65) | Decisions 4, 5 and 6 are grid rules for future searches (Decision 6 even says no result changes). They do not fit the heading, and nothing marks them as a separate, lower-stakes group. | minor | Split into "changes today's adoption set" (Decisions 2, 3, 7, 8, the slow binned SCE item) and "search rules for next time" (Decisions 4, 5, 6). | yes |
| 8 | Decision 1 second caveat (L45–47) | One of the four adoptable proposals goes over a limit on busy (1.28/h against 1) — effectively a ruling — but it appears as a caveat bullet with no Decide line. (Whether it is supported is role 4's; my point is placement: a decision is sitting where no decision is asked.) | minor | Give it an explicit sub-question: should calls outside the stretch be gated on busy too? | yes |
| 9 | Real data section (L368–384) | No job in the spine: it asks nothing and sits after the appendix. Yet a floor choice that flips 498 calls bears on ADR-0008 (the per-window floor), and could be the "would need a new definition" stop rule at runbook L158. | minor (major if it implies a ruling) | Either say it asks nothing and move it into the appendix block, or state the ruling it implies and place it with the other rulings. | yes (placement); no (whether it triggers the stop rule is Tony's) |
| 10 | Definitions at the end (L386–416) | Terms used from Decision 1 onward are defined only at the bottom. This is a declared deviation (L12–13 says so) and defensible for this reader. | minor | Optional: a four-line key to the budgets near the top; otherwise leave it. | yes |

## Verdict on order

The problem-first opening works, and so does one Decide line per section. But the page follows the order the night produced things, not the order of dependency: the adoption question comes before the rulings that scope it, the root mechanism (Decision 7) comes eighth, and the evidence for three decisions sits in the appendix. A reader deciding top to bottom would answer Decision 1 before learning what might change it. Findings 1–5 are the reorder, and none of them changes content.

Files:
- `docs/learned/runs/2026-09-25-final-parameters/README.md` (reviewed artifact)
- `docs/handoffs/2026-09-25-overnight-final-parameters.md` (Phase 4, L126–146)
